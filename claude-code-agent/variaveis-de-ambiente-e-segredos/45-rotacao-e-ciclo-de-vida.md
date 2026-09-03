# 45 · Rotação e ciclo de vida de um segredo

`Nível: avançado` · `Atualizado em: 14/08/2026`

Todo segredo tem um ciclo de vida. Quase todo time só pensa nos dois primeiros passos
— gerar e usar — e descobre os outros durante um incidente.

```
   gerar → distribuir → usar → MONITORAR → ROTACIONAR → REVOGAR → destruir
                                    ▲                        │
                                    └────────────────────────┘
                                      o ciclo que não acontece
```

---

## 1. Gerar

### Entropia: quanto é suficiente

| Uso | Mínimo | Comando |
|---|---|---|
| Segredo de sessão / assinatura | 256 bits | `openssl rand -base64 32` |
| Chave de API interna | 128 bits | `openssl rand -hex 16` |
| Senha de banco | 128 bits | `openssl rand -base64 24` |
| Senha memorizável por humano | 4–6 palavras | Diceware |

```bash
openssl rand -base64 32
# ex.: 8xK2mNp5qR7sT9vW1yZ3aB5cD7eF9gH1iJ3kL5mN7oP=
```

```bash
# alfabeto seguro: sem $ ` " ' \ # @ / + = — evita a classe inteira de bug de parsing
openssl rand -base64 48 | tr -dc 'A-Za-z0-9_-' | head -c 32; echo
```

**Por que fugir de `$`, `#`, `@`, `/` e `+`:**

| Caractere | Onde quebra |
|---|---|
| `#` | vira comentário no `.env` do Node (medido em [12](12-formato-dotenv.md)) |
| `$` | expandido por `source`, por `python-dotenv`, pelo shell |
| `@` e `/` | quebram o parsing de `postgres://user:senha@host` |
| `"` `'` `\` | escape inconsistente entre carregadores |
| `+` `=` | precisam de codificação percentual em URL |

Você perde ~1 bit de entropia por caractere e evita uma noite de depuração.
É o melhor negócio deste curso.

### O que **nunca** usar como fonte

```javascript
Math.random()                       // ❌ não é criptográfico. Previsível.
Date.now()                          // ❌
crypto.randomBytes(32)              // ✅ Node
secrets.token_urlsafe(32)           // ✅ Python (não `random`!)
random_bytes(32)                    // ✅ PHP
```

Em Python, `random` é um Mersenne Twister: observando ~624 saídas, um atacante prevê
todas as seguintes. Use `secrets`, não `random`.

---

## 2. Distribuir — e o antipadrão universal

```
❌ WhatsApp, Slack, Telegram, e-mail, Jira, Notion, Google Docs
```

Motivo: o segredo passa a existir em servidores de terceiros, com backup, indexação
e retenção que você não controla, **para sempre**. Apagar a mensagem não apaga o
backup nem a cópia no celular de quem recebeu.

**O que fazer, em ordem de preferência:**

1. **Nunca transportar.** O melhor segredo é o que não viaja:
   - **gere no destino** (como o `SESSION_SECRET` do
     [instalador do projeto-modelo](07-projeto-modelo/deploy/install.sh));
   - peça ao **cliente** que crie a credencial no painel dele e a coloque
     direto no sistema, sem passar por você;
   - use identidade de máquina (IAM role, ServiceAccount) — não há segredo a transportar.
2. **Link de uso único e autodestrutivo**: `onetimesecret.com`, ou o `pwpush`
   auto-hospedado. O segredo some após a primeira leitura.
3. **Canais separados**: o link por e-mail, a senha de abertura por telefone.
   Um invasor precisa comprometer dois canais.
4. **Cofre compartilhado** (1Password, Bitwarden, Vault) com acesso concedido —
   e revogável, e auditado.

E, sempre: **um segredo que passou por um canal inadequado é um segredo comprometido**.
Rotacione. Não negocie com você mesmo sobre isso.

---

## 3. Monitorar — o passo que não existe na maioria dos times

Você só pode rotacionar com segurança se souber **quem ainda usa** a credencial antiga.

| O que monitorar | Como |
|---|---|
| Último uso de uma chave de API | painel do provedor (Stripe, SendGrid, AWS) |
| Conexões por usuário de banco | `SELECT usename, count(*) FROM pg_stat_activity GROUP BY 1` |
| Chaves de acesso AWS não usadas | IAM Credential Report (`aws iam generate-credential-report`) |
| Quem leu o segredo | log de auditoria do cofre — só um cofre dá isso |
| Idade das credenciais | inventário com data de criação |

Sem o item 5, "quem viu esse segredo?" não tem resposta. É o argumento mais forte a
favor de um cofre, e o menos citado.

---

## 4. Rotacionar sem derrubar: a técnica da sobreposição

**O problema:** entre trocar a senha e todas as instâncias reiniciarem com a nova, as
antigas usam a velha e falham. Isso é indisponibilidade.

**A solução: duas credenciais válidas ao mesmo tempo.**

```
Tempo →
        t0            t1              t2                t3
────────────────────────────────────────────────────────────────
Sistema │ aceita A    aceita A e B    aceita A e B      aceita B
App     │ usa A       usa A           reinicia → usa B  usa B
Ação    │             cria B          faz deploy        REVOGA A
                                                        ↑
                                       só depois de CONFIRMAR
                                       que ninguém usa A
```

### Senha de banco

```sql
-- t1: cria um SEGUNDO usuário. Não troca a senha do que está em uso!
CREATE USER app_v2 WITH PASSWORD 'nova-senha-forte';
GRANT ALL PRIVILEGES ON DATABASE loja TO app_v2;
GRANT ALL ON ALL TABLES IN SCHEMA public TO app_v2;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO app_v2;
```

```sql
-- t2 → t3: confirme que ninguém usa mais o antigo
SELECT usename, count(*), max(backend_start)
FROM pg_stat_activity WHERE usename LIKE 'app%' GROUP BY 1;
```

```sql
-- t3: só agora
REASSIGN OWNED BY app_v1 TO app_v2;
DROP OWNED BY app_v1;
DROP USER app_v1;
```

⚠️ O `ALTER DEFAULT PRIVILEGES` é o passo esquecido: sem ele, tabelas criadas
**depois** da rotação não são acessíveis pelo `app_v2`, e o erro aparece semanas
depois, numa migração.

### Chave de API

A maioria dos provedores sérios (Stripe, AWS, SendGrid, Twilio) permite **múltiplas
chaves ativas**. O procedimento:

1. crie a nova chave;
2. faça o deploy;
3. **olhe o painel de uso** e confirme que a antiga zerou;
4. só então revogue.

O passo 3 é o que as pessoas pulam, e é o que evita o incidente — porque quase sempre
existe um lugar esquecido usando a chave antiga: um cron, um script de backup, um
webhook, um Postman de alguém, o ambiente de homologação.

### Segredo de assinatura de sessão (o caso especial)

Trocar o `SESSION_SECRET` **desconecta todos os usuários**, porque as sessões
existentes foram assinadas com o valor antigo. A solução é aceitar **duas** chaves
para verificar, e assinar só com a nova:

```javascript
// verifica com qualquer uma das chaves; assina sempre com a primeira
const chaves = [config.sessionSecretAtual, config.sessionSecretAnterior].filter(Boolean);

function verificar(valor, assinatura) {
  return chaves.some((k) => iguaisSeguro(assinar(valor, k), assinatura));
}
function assinar(valor) {
  return hmac(valor, chaves[0]);   // sempre a nova
}
```

Depois de um período maior que a validade da sessão (digamos, 30 dias), remova a
chave antiga. Esse padrão — **lista de chaves, a primeira assina, todas verificam** —
é o mesmo usado em JWKS, em rotação de chave JWT e em webhooks assinados.

---

## 5. Com que frequência rotacionar?

Aqui há um debate real, e é justo apresentar os dois lados.

**A posição tradicional (PCI-DSS, muitas auditorias):** rotação periódica obrigatória,
tipicamente a cada 90 dias.

**A posição moderna (NIST SP 800-63B, para senhas de usuário):** rotação periódica
forçada é **contraproducente** — leva a senhas mais fracas e previsíveis
(`Senha2026!` → `Senha2027!`), e a rotação deve ser **por evento** (suspeita de
comprometimento).

**Minha leitura, e é opinião:** a recomendação do NIST é sobre **senhas escolhidas
por humanos**, e ela está certa nesse contexto. Para **credenciais de máquina**
geradas aleatoriamente, o raciocínio é outro: o risco não é o humano criar uma
credencial fraca, é o acúmulo silencioso de cópias ao longo do tempo — em backups,
em laptops de ex-funcionários, em logs, em ambientes de teste. A rotação periódica
combate isso, e mais: **ela testa o procedimento**. Um time que nunca rotacionou não
sabe rotacionar, e vai descobrir isso durante um incidente, sob pressão.

Sugestão pragmática:

| Tipo | Frequência | Gatilho adicional |
|---|---|---|
| Credencial dinâmica | 1 h (automática) | — |
| Token de CI (OIDC) | por execução | — |
| Chave de API de terceiro | 6–12 meses | saída de pessoa, suspeita |
| Senha de banco | 6–12 meses | idem |
| `SESSION_SECRET` | 12 meses | comprometimento |
| Chave privada TLS | conforme validade do certificado | — |
| Chave-mestra (KMS) | 1–3 anos | — |
| **Qualquer uma** | **imediatamente** | **saída de quem tinha acesso; vazamento; canal inadequado** |

**A meta real não é rotacionar com frequência — é chegar a um ponto em que a rotação
seja automática e você não precise pensar nela.** Um sistema que rotaciona sozinho a
cada hora é mais seguro que um que rotaciona a cada 90 dias com um chamado no Jira.

---

## 6. Revogar e destruir

**Revogar não é apagar.** Revogar significa que o **sistema que valida** para de
aceitar aquele valor.

```bash
aws iam delete-access-key --access-key-id AKIA...
bao lease revoke -prefix database/creds/app
```

E, depois de revogar, **verifique**:

```bash
AWS_ACCESS_KEY_ID=AKIA... AWS_SECRET_ACCESS_KEY=... aws sts get-caller-identity
# esperado: InvalidClientTokenId
```

Um segredo "revogado" que ainda funciona é pior que um segredo ativo, porque você
parou de vigiá-lo.

Destruir as cópias:

```bash
shred -u /etc/minha-app/env.bak       # sobrescreve antes de apagar
```

⚠️ **`shred` não funciona de forma confiável em SSD, em sistemas com journaling
(ext4, XFS), em cópia-na-escrita (btrfs, ZFS) nem em armazenamento virtualizado.**
O bloco físico pode continuar lá, remapeado pelo controlador. A única garantia real
é criptografia de disco desde o início, e descartar a chave.

E o que quase sempre sobra:

- backups (o segredo antigo está em todos os do último ano);
- snapshots de VM;
- imagens Docker publicadas;
- histórico do Git;
- logs com retenção de 90 dias;
- o Slack;
- a máquina de quem já saiu.

**Por isso a resposta a um vazamento é rotacionar, nunca "apagar".**
Ver [50-vazamentos-e-resposta.md](50-vazamentos-e-resposta.md).

---

## 7. Inventário — o pré-requisito de tudo

Você não consegue rotacionar o que não sabe que existe.

```markdown
| Segredo | Onde é usado | Onde é guardado | Quem tem acesso | Criado em | Rotacionar até | Como rotacionar |
|---|---|---|---|---|---|---|
| DATABASE_URL prod | api, worker, cron de backup | /etc/minha-app/env em 3 servidores | ops (2 pessoas) | 03/2025 | 03/2026 | runbook RB-07 |
| STRIPE_SECRET | api | painel Vercel | 4 devs | 11/2024 | **VENCIDO** | runbook RB-03 |
| SESSION_SECRET | api | /etc/minha-app/env | ops | 03/2025 | 03/2026 | RB-09 (lista de 2 chaves) |
```

As colunas que fazem a diferença: **"onde é usado"** (é a lista do que quebra se você
errar) e **"como rotacionar"** (um link para um procedimento escrito e **ensaiado**).

**Ensaiar é a parte que ninguém faz.** Rotacione um segredo de homologação de
propósito, cronometre, anote o que deu errado. Fazer isso uma vez por semestre custa
uma hora e vale mais que qualquer ferramenta.

---

## Autoteste

1. Por que gerar segredos sem `$`, `#`, `@` e `/` evita bugs, e quanto isso custa em entropia?
2. Por que `random` do Python não serve para gerar segredo, mas `secrets` serve?
3. Cite três formas corretas de entregar um segredo a outra pessoa, em ordem de preferência.
4. Descreva a técnica de sobreposição com os quatro instantes.
5. O que é `ALTER DEFAULT PRIVILEGES` e por que esquecê-lo causa erro semanas depois?
6. Por que trocar `SESSION_SECRET` desconecta todos, e qual padrão resolve isso?
7. Qual é o argumento do NIST contra rotação periódica, e por que ele não se aplica igual a credencial de máquina?
8. Por que "rotação periódica testa o procedimento" é um argumento a favor dela?
9. Por que `shred` não garante destruição em SSD?
10. Quais são as duas colunas mais importantes de um inventário de segredos, e por quê?

---

**Fontes consultadas em 14/08/2026:** NIST SP 800-63B (Digital Identity Guidelines) ·
PCI-DSS v4.0 · postgresql.org/docs (GRANT, ALTER DEFAULT PRIVILEGES) ·
developer.hashicorp.com/vault/docs/concepts/lease.

**Próximo:** [50-vazamentos-e-resposta.md](50-vazamentos-e-resposta.md) · Voltar ao [mapa](00-MAPA.md)
