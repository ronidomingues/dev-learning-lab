# 55 · Entrega ao cliente — quando o sistema roda numa máquina que não é sua

`Nível: avançado` · `Atualizado em: 14/08/2026`

A pergunta que originou este curso dizia: *"quando vai para o cliente, quando
finalmente vai ser usado o sistema"*. Este arquivo trata exatamente desse caso —
o menos coberto na literatura, e o mais comum no mercado brasileiro de software sob
encomenda.

---

## 1. Primeiro, decida o modelo de entrega

As respostas mudam completamente conforme o modelo. Identifique o seu:

| Modelo | Quem controla o servidor | Quem detém os segredos |
|---|---|---|
| **SaaS** (você hospeda, muitos clientes) | você | você |
| **SaaS dedicado** (você hospeda, uma instância por cliente) | você | você |
| **On-premise** (roda no servidor do cliente) | **o cliente** | **o cliente** |
| **Nuvem do cliente** (você opera a conta dele) | compartilhado | ⚠️ ambíguo — resolva por contrato |
| **Software distribuído** (o cliente instala sozinho) | o cliente | o cliente |

**A linha ambígua é a que dá processo judicial.** Se você opera a nuvem do cliente,
defina por escrito: quem tem acesso às credenciais, quem responde por um vazamento,
o que acontece ao encerrar o contrato, e como o acesso é revogado.

---

## 2. A questão central: **de quem é o segredo?**

```
   Segredo do CLIENTE                    Segredo SEU
   ─────────────────                     ───────────
   • senha do banco dele                 • chave da SUA API
   • credencial do ERP dele              • licença do seu software
   • conta de e-mail dele                • chave de assinatura das suas atualizações
   • certificado digital dele
                    │                              │
                    ▼                              ▼
   NUNCA deve chegar às suas mãos.       NUNCA deve ficar legível na máquina dele.
   Faça o cliente inseri-lo              Se ficar, considere-o público —
   diretamente no sistema.               ele tem root na máquina.
```

**As duas regras derivadas, e elas resolvem 90% das dúvidas práticas:**

> **Regra 1 — o que é dele, ele digita.** Você nunca deve receber a senha do banco do
> cliente por e-mail. Um instalador que **pergunta** elimina o transporte e elimina a
> sua responsabilidade sobre aquele segredo.

> **Regra 2 — o que é seu, na máquina dele, está comprometido.** O cliente tem root.
> Ele pode ler `/proc/PID/environ`, despejar a memória do processo, interceptar o
> tráfego. Qualquer segredo seu embutido no produto **é público** — trate-o assim ao
> projetar. Isso é o mesmo raciocínio de [20-frontend-e-build-time.md](20-frontend-e-build-time.md),
> aplicado a servidor.

### A consequência da Regra 2, que muda arquitetura

Se a sua aplicação on-premise precisa chamar **a sua** API na nuvem, **não** embuta a
sua chave-mestra nela. Faça assim:

```
1. Na instalação, o cliente informa uma LICENÇA (identificador dele, não é segredo grave).
2. A instância chama a sua API: POST /ativar { licenca, impressao_da_maquina }
3. Você emite uma credencial ESPECÍFICA daquela instalação, com escopo mínimo.
4. Essa credencial é revogável individualmente, e você sabe qual cliente a usa.
```

Se vazar, você revoga **aquele** cliente, e os outros seguem funcionando. Compare com
a alternativa: uma chave-mestra embutida em todas as instalações, que ao vazar
obriga a atualizar **todos** os clientes ao mesmo tempo.

---

## 3. O instalador — o mecanismo concreto

O código completo está em
[07-projeto-modelo/deploy/install.sh](07-projeto-modelo/deploy/install.sh).
Aqui, o raciocínio de cada decisão.

### 3.1 Pergunte, não transporte

```bash
read -rsp "  Senha do banco de dados: " valor </dev/tty; echo
```

`-s` não ecoa na tela (ninguém lê por cima do ombro, e não fica no compartilhamento
de tela). E, por não ser digitado num comando, **não entra no histórico do shell**.

### 3.2 Gere o que puder ser gerado

```bash
printf 'SESSION_SECRET=%s\n' "$(openssl rand -base64 48 | tr -d '\n')" >> "$TMP"
```

**Segredo que não viaja não vaza.** E cada instalação fica com um valor **diferente**:
o comprometimento de um cliente não atinge os demais. Se você usasse o mesmo
`SESSION_SECRET` em todas as instalações, uma cópia vazada permitiria forjar sessões
**em todos os clientes**.

### 3.3 Valide antes de gravar

```bash
if ! ( set -a; . "$TMP"; set +a; node "$DIR_APP/src/check-config.mjs" ); then
  echo "❌ Configuração inválida. NADA foi gravado."
  rm -f "$TMP"; exit 1
fi
mv "$TMP" "$ARQ_ENV"
```

O `mv` é atômico: ou o arquivo final existe completo, ou não existe. Um Ctrl+C no
meio nunca deixa configuração pela metade — que é o pior estado possível, porque o
serviço sobe e falha de forma esquisita.

### 3.4 Permissões e `umask`

```bash
umask 077              # tudo que nascer daqui em diante é 600
# ...
chown root:cofre "$ARQ_ENV"
chmod 640 "$ARQ_ENV"
```

O `umask 077` na primeira linha fecha uma janela real: sem ele, o arquivo temporário
nasce `644` e fica legível por todos os usuários do servidor durante os segundos até
o `chmod`.

### 3.5 Idempotência

```bash
if [[ -f "$ARQ_ENV" ]]; then
  echo "• configuração já existe — mantida"
  echo "  Para reconfigurar: sudo mv $ARQ_ENV $ARQ_ENV.bak && sudo $0"
  exit 0
fi
```

O cliente vai rodar duas vezes. **Sempre roda.** Um instalador que sobrescreve a
configuração na segunda execução destrói o `SESSION_SECRET` gerado e desconecta todos.

### 3.6 Diga ao cliente o que ele precisa saber

```
⚠️  IMPORTANTE:
   1. Faça backup de /etc/cofre-de-recados/env. O SESSION_SECRET foi gerado
      agora e não existe em nenhum outro lugar.
   2. NÃO copie esse arquivo por e-mail ou WhatsApp.
   3. NÃO adicione essas variáveis ao ~/.bashrc de ninguém.
   4. Para trocar a chave de API: sudo mv ... && sudo ./install.sh
```

Sem isso, em seis meses alguém do TI do cliente vai copiar o `.env` para o Drive da
empresa "para não perder", e você não vai nem saber.

---

## 4. Como a **sua** credencial chega ao cliente

O caso em que o transporte é inevitável (uma chave de API que você emitiu para ele).

**Em ordem de preferência:**

| # | Método | Por quê |
|---|---|---|
| 1 | **O cliente gera no seu painel** | o segredo nunca trafega; você só confirma que foi criado |
| 2 | **Link de uso único** (`onetimesecret.com`, `pwpush`) | some após a primeira leitura; expira sozinho |
| 3 | **Canais separados** | link por e-mail, senha de abertura por telefone |
| 4 | **Cofre compartilhado** (1Password, Bitwarden) | acesso concedido e revogável, com auditoria |
| 5 | ~~E-mail, WhatsApp, Slack, Jira, Notion~~ | ❌ fica para sempre em servidor de terceiro |

E o combinado que evita discussão depois: **toda credencial que passou pelo método 5
é considerada comprometida e será rotacionada.** Coloque isso no seu procedimento de
implantação, por escrito.

---

## 5. Atualizações e migração de configuração

O problema que só aparece na versão 2.0: você adicionou `SMTP_URL` como obrigatória,
e as 40 instalações existentes não têm essa variável. Todas quebram na atualização.

**Padrão de migração:**

```javascript
// config.mjs — introduza como OPCIONAL, com aviso
smtpUrl: opcional('SMTP_URL', null, v.url(['smtp', 'smtps'])),
```

```javascript
if (!config.smtpUrl) {
  log.warn('SMTP_URL não configurada — o envio de e-mail está desativado. ' +
           'A partir da versão 3.0 esta variável será obrigatória.');
}
```

Depois de dois ou três ciclos de atualização, promova a obrigatória.

E dê ao cliente uma ferramenta para descobrir o que falta **antes** de atualizar:

```bash
./bin/check-config --versao-alvo 3.0
# ❌ A versão 3.0 exige SMTP_URL, que não está configurada.
#    Rode ./install.sh --reconfigurar antes de atualizar.
```

**Regra de compatibilidade:** uma atualização **nunca** deve exigir configuração nova
sem aviso na versão anterior. Se exigir, seu cliente vai descobrir com o sistema fora
do ar, num domingo.

---

## 6. Suporte remoto sem pedir o segredo

Situação recorrente: o cliente diz "não conecta no banco", e você precisa diagnosticar
sem pedir a senha dele por WhatsApp.

**A ferramenta certa é o comando de diagnóstico mascarado**
([07-projeto-modelo/src/check-config.mjs](07-projeto-modelo/src/check-config.mjs)):

```bash
sudo -u cofre node /opt/cofre-de-recados/src/check-config.mjs
```
```
✅ Configuração válida.

   ambiente         production
   porta            8080
   databaseUrl      postgres://app:***@db.interno:5432/loja
   sessionSecret    QH1…bC (64 chars)
   apiKey           sk_…1d (32 chars)
```

**Essa saída pode ser colada num chamado com segurança**, e ainda assim responde às
perguntas do suporte: o host está certo? a porta está certa? o segredo tem o tamanho
esperado (32 caracteres, e não 31 por causa de um espaço)? o ambiente é `production`?

**Nunca peça:**
- ❌ "me manda o `.env`";
- ❌ "roda `printenv` e cola aqui";
- ❌ "cola a saída completa do log em modo debug".

**Peça sempre a saída mascarada.** Construir essa ferramenta é meio dia de trabalho e
evita que a sua caixa de entrada vire um repositório de senhas de clientes — o que,
sob a LGPD, é uma responsabilidade que você não quer.

---

## 7. Multi-inquilino: o segredo por cliente

Se você é SaaS e guarda credenciais **dos clientes** (para integrar com o ERP deles,
por exemplo), o problema muda de natureza: você agora é **custodiante de segredo de
terceiro**, com as obrigações legais que isso traz.

**O mínimo aceitável:**

```
┌─────────────────────────────────────────────────────────────┐
│ chave-mestra (KMS / HSM / cofre) — a aplicação NUNCA a vê    │
└────────────────────────┬────────────────────────────────────┘
                         │ deriva ou decifra
    ┌────────────────────┼────────────────────┐
    ▼                    ▼                    ▼
 chave do            chave do             chave do
 cliente A           cliente B            cliente C
    │                    │                    │
 credenciais         credenciais          credenciais
 do cliente A        do cliente B         do cliente C
```

Requisitos, e cada um evita um desastre específico:

1. **Chave distinta por inquilino.** O comprometimento de um não expõe os outros.
2. **Criptografia de envelope** com KMS ([60 §3](60-teoria-avancada.md)): a
   aplicação nunca segura a chave-mestra em memória.
3. **Auditoria de acesso**: registre toda leitura de credencial de cliente, com
   usuário, motivo e horário. É o que você vai precisar apresentar numa investigação.
4. **Sem acesso humano por padrão.** Ver credencial de cliente deve exigir
   aprovação e gerar alerta — não ser um `SELECT` que qualquer dev roda.
5. **Rotação e exclusão a pedido.** O cliente encerrou o contrato? As credenciais
   dele devem ser destruídas, e você precisa **conseguir comprovar** isso.

O motor **Transit** do Vault/OpenBao ([40 §6](40-cofres-de-segredos.md)) é feito
exatamente para isso: sua aplicação manda o texto e recebe o cifrado, sem nunca ver
a chave.

---

## 8. Checklist de entrega on-premise

```
Antes da primeira instalação
[ ] .env.example completo, com COMO OBTER cada valor, não só o nome
[ ] install.sh idempotente, com umask 077, validação antes de gravar
[ ] Segredos gerados no destino sempre que possível (não transportados)
[ ] Comando de diagnóstico mascarado, para o suporte
[ ] Documento "o que o TI do cliente precisa saber" (backup, o que não fazer)
[ ] Permissões definidas: 640 root:app, fora do diretório da aplicação
[ ] Contrato: quem detém o quê, quem responde por vazamento, o que ocorre no encerramento

A cada versão
[ ] Nova variável entra como OPCIONAL com aviso, por 2–3 ciclos
[ ] check-config informa o que falta ANTES da atualização
[ ] CHANGELOG lista mudanças de configuração em destaque

Sempre
[ ] Nenhuma credencial de cliente na sua caixa de entrada
[ ] Credencial sua na máquina do cliente = específica daquela instalação, revogável
[ ] Inventário: qual cliente tem qual credencial, emitida quando
```

---

## Autoteste

1. Quais são as duas regras sobre "de quem é o segredo", e o que decorre de cada uma?
2. Por que uma chave-mestra embutida em todas as instalações é uma decisão arquitetural ruim?
3. Por que o instalador **gera** o `SESSION_SECRET` em vez de perguntar? Cite dois motivos.
4. O que `umask 077` na primeira linha do instalador evita, concretamente?
5. Por que o instalador precisa ser idempotente?
6. Como você entrega uma chave de API a um cliente sem que ela fique em servidor de terceiro?
7. Descreva o padrão de migração para tornar uma variável obrigatória sem quebrar instalações existentes.
8. O que você pede ao cliente em vez de "me manda o `.env`"?
9. Num SaaS que guarda credenciais dos clientes, por que a chave precisa ser distinta por inquilino?
10. Por que "quem detém os segredos" precisa estar no contrato quando você opera a nuvem do cliente?

---

**Próximo:** [60-teoria-avancada.md](60-teoria-avancada.md) · Voltar ao [mapa](00-MAPA.md)
