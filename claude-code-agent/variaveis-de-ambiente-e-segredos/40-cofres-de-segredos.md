# 40 · Cofres de segredos — o que são, quando valem, qual escolher

`Nível: avançado` · `Atualizado em: 14/08/2026`

---

## 1. O que um cofre resolve que um arquivo não resolve

Um arquivo `640` num servidor resolve **confidencialidade básica** e nada mais.
Um cofre acrescenta cinco coisas:

| Capacidade | O que significa | Por que importa |
|---|---|---|
| **Auditoria de acesso** | quem leu, quando, de qual IP | sem isso, "o segredo vazou" não tem investigação possível |
| **Controle de acesso fino** | a aplicação A lê só os segredos dela | limita o estrago de um comprometimento |
| **Versionamento** | histórico e rollback do valor | rotação errada volta em segundos |
| **Rotação automatizada** | o cofre troca a senha no banco sozinho | tarefa que ninguém faz passa a acontecer |
| **Credencial dinâmica** | usuário criado na hora, válido por 1 h | ⭐ muda a economia do vazamento |

A quinta linha é a única que **muda de categoria** — o resto é gerência melhor do
mesmo problema. Se você adotar um cofre e não usar credencial dinâmica, ganhou
auditoria e um sistema novo para operar. É um negócio razoável, mas menor do que
costumam vender.

---

## 2. Credencial dinâmica — a ideia que justifica tudo

```
   ── Modelo estático ──────────────────────────────────
   senha do banco = "S3nh4F1x4"
   • a mesma para todas as instâncias, desde 2019
   • ninguém sabe quantas cópias existem
   • está no laptop de um ex-funcionário
   • rotacionar = projeto, com janela de indisponibilidade

   ── Modelo dinâmico ──────────────────────────────────
   app pede credencial ao cofre
        ↓
   cofre CRIA no banco:  usuario "v-app-a1b2c3" / senha aleatória
        ↓
   entrega à app, com validade de 1 hora
        ↓
   passada 1 h, o cofre EXECUTA `DROP USER v-app-a1b2c3`
```

Consequências, cada uma com valor real:

- **vazou? expira sozinha.** A janela de exploração cai de anos para minutos;
- **rastreabilidade:** cada instância tem um usuário distinto, então o log do banco
  diz **qual** delas fez a consulta problemática;
- **revogação instantânea:** `vault lease revoke -prefix database/creds/app` derruba
  todas as credenciais emitidas, agora;
- **rotação deixa de ser projeto** — é o funcionamento normal.

Configuração (Vault/OpenBao):

```bash
bao secrets enable database

bao write database/config/postgres \
  plugin_name=postgresql-database-plugin \
  allowed_roles="app-leitura,app-escrita" \
  connection_url="postgresql://{{username}}:{{password}}@db.interno:5432/loja" \
  username="vault_admin" password="senha-do-admin"

bao write database/roles/app-escrita \
  db_name=postgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
                       GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" max_ttl="24h"
```

```bash
bao read database/creds/app-escrita
# Key                Value
# lease_id           database/creds/app-escrita/xyz...
# lease_duration     1h
# password           A1b2C3d4-e5F6...
# username           v-token-app-escr-a1b2c3d4
```

**O preço, que ninguém menciona no material de marketing:**

- o cofre precisa de credencial **administrativa** no banco — se o cofre cair, você
  tem um problema muito maior que antes;
- a aplicação precisa **renovar a concessão** ou reconectar quando ela expira; um
  *pool* de conexões que não sabe disso quebra de hora em hora, e o sintoma é
  intermitente e horrível de diagnosticar;
- nem todo sistema suporta: bancos sim, muitas APIs de terceiros não.

---

## 3. O panorama em agosto de 2026

### Autogerenciados

| Ferramenta | Licença | Situação |
|---|---|---|
| **HashiCorp Vault** | **BUSL 1.1** desde ago/2023 | produto **IBM** desde o início de 2025; versão paga = IBM Vault Enterprise |
| **OpenBao** | **MPL 2.0** | fork do Vault 1.14 (última versão MPL), sob a **Linux Foundation**; 2.0 em set/2024; adotantes de peso, incluindo a Nvidia |
| **Infisical** | open source + planos pagos | interface moderna; plano gratuito para até 5 identidades; Pro por identidade/mês (humanos **e** máquinas contam) |
| **SOPS** | MPL 2.0, **sandbox da CNCF** | não é servidor: criptografa arquivos. Linha 3.13.x |
| **Sealed Secrets** | Apache 2.0 | específico de Kubernetes; permite versionar o segredo cifrado |

**Sobre a licença do Vault, o que você precisa saber para decidir:** a BUSL 1.1
permite usar e modificar, e **proíbe oferecer o produto como serviço concorrente**;
cada versão vira MPL 2.0 quatro anos depois de lançada. Para uso interno de empresa,
**não muda nada na prática**. O motivo real para preferir o OpenBao é governança
(Linux Foundation, sem dono comercial único) e evitar risco futuro de licença, não
uma restrição que te atinja hoje.

### Gerenciados na nuvem

| Serviço | Preço (consultado em 14/08/2026) |
|---|---|
| **AWS Secrets Manager** | US$ 0,40 por segredo/mês + US$ 0,05 por 10.000 chamadas |
| **Google Secret Manager** | US$ 0,06 por versão ativa/mês + US$ 0,03 por 10.000 acessos; camada gratuita de 6 versões e 10.000 acessos/mês |
| **Azure Key Vault (Standard)** | US$ 0,03 por 10.000 operações de segredo |
| **AWS Parameter Store (Standard)** | **gratuito** até 10.000 parâmetros — a opção mais subestimada da AWS |
| **Doppler** | gratuito até 3 usuários; ~US$ 8/usuário/mês (Developer); ~US$ 21/usuário/mês (Team) |
| **Infisical Cloud** | gratuito até 5 identidades; ~US$ 18/identidade/mês (Pro) |

Detalhamento, moeda, custos ocultos e conversão para BRL em
[80-custos-e-licencas.md](80-custos-e-licencas.md).

> 💡 **A dica que economiza dinheiro:** o **AWS Systems Manager Parameter Store** com
> `SecureString` é **gratuito** até 10.000 parâmetros, criptografa com KMS, integra
> com IAM e com o ECS/Lambda igualzinho ao Secrets Manager. O que ele **não** faz:
> rotação automática gerenciada e credencial dinâmica. Para a maioria dos casos que
> só precisa "guardar em segurança e controlar acesso", ele resolve a US$ 0.

---

## 4. Qual escolher — recomendação honesta

```
Você já está numa nuvem só?
├── SIM → use o cofre dela. O IAM já está integrado, não há servidor a operar,
│         e o menor atrito ganha de qualquer vantagem técnica marginal.
│         (E considere o Parameter Store antes do Secrets Manager, na AWS.)
└── NÃO ou multi-nuvem ou on-premise
    ├── precisa de credencial DINÂMICA?
    │   └── SIM → OpenBao (ou Vault, se já paga)
    ├── quer interface amigável e time pequeno?
    │   └── Infisical ou Doppler
    └── só precisa versionar segredo criptografado no Git?
        └── ⭐ SOPS + age. Simples, sem servidor, sem custo.
```

**E a pergunta anterior a todas:** *você precisa mesmo de um cofre?*

| Situação | Precisa? |
|---|---|
| 1–3 servidores, equipe de 1–5, sem conformidade | **não**. `LoadCredential` + rotação anual anotada no calendário |
| Vários serviços compartilhando credenciais | começa a valer |
| Exigência de auditoria (SOC 2, PCI-DSS, ISO 27001) | **sim** — a auditoria é o entregável |
| Rotação frequente obrigatória | **sim** |
| Muitos ambientes efêmeros | **sim** |
| "Porque é a boa prática" | ❌ **não**. Esse é o motivo errado |

Um cofre é **mais um sistema crítico** para operar: alta disponibilidade, backup,
destravamento (*unseal*) após reinício, atualização, e a possibilidade de ele ser o
motivo da sua próxima indisponibilidade. Ver [75-armadilhas.md](75-armadilhas.md).

---

## 5. SOPS — o meio-termo que resolve muita gente

Não é servidor. Criptografa **valores** dentro de arquivos YAML/JSON/ENV/INI,
deixando as chaves legíveis — então `git diff` continua útil e o arquivo pode ser
versionado.

Instalação em [03-instalacao.md §8](03-instalacao.md). Fluxo completo:

```yaml
# .sops.yaml — na raiz do repositório
creation_rules:
  - path_regex: secrets/producao/.*\.yaml$
    age: age1abc...,age1def...       # chaves públicas de quem pode decifrar
  - path_regex: secrets/dev/.*\.yaml$
    age: age1abc...,age1def...,age1estagiario...
```

```bash
sops secrets/producao/app.yaml        # abre no editor, decifra, recifra ao salvar
sops --decrypt secrets/producao/app.yaml
sops exec-env secrets/producao/app.yaml './app'   # ⭐ sem escrever nada em disco
```

Antes e depois, para ver o que ele faz:

```yaml
# antes
DATABASE_URL: postgres://app:senha@db/loja
API_KEY: sk_live_xxx

# depois — a CHAVE continua legível, o VALOR não
DATABASE_URL: ENC[AES256_GCM,data:8sK2...,iv:...,tag:...,type:str]
API_KEY: ENC[AES256_GCM,data:9dL3...,iv:...,tag:...,type:str]
sops:
    age:
        - recipient: age1abc...
          enc: |
            -----BEGIN AGE ENCRYPTED FILE-----
```

**Como funciona por dentro** (criptografia de envelope, ver
[60-teoria-avancada.md §3](60-teoria-avancada.md)): o SOPS gera uma chave de dados
aleatória, cifra cada valor com AES-256-GCM, e cifra **a chave de dados** para cada
destinatário. Adicionar alguém não recifra os valores — só acrescenta uma cópia da
chave de dados.

Backends de chave suportados: **age** (recomendado), AWS KMS, GCP KMS, Azure Key
Vault, HashiCorp Vault, PGP.

### Quando SOPS é a escolha certa

- ✅ entrega **on-premise**: o cliente recebe o repositório com os segredos dentro,
  cifrados para a chave dele;
- ✅ GitOps: o `SealedSecret`/`SopsSecret` fica no Git e o operador decifra no cluster;
- ✅ times pequenos que querem versionamento e revisão de mudanças de segredo;
- ✅ multi-nuvem sem servidor a operar.

### As três limitações que você precisa aceitar

1. **Sem auditoria de leitura.** Quem clonou o repositório e tem a chave lê quando
   quiser, sem registro nenhum.
2. **Revogar é ilusório.** Removeu a chave de um ex-colega com `sops updatekeys`?
   Ele tem o repositório clonado, com o arquivo antigo no histórico, e a chave dele.
   **A única resposta correta é rotacionar os segredos em si.** Este é o erro de
   raciocínio mais comum com criptografia de repositório — vale para `git-crypt` também.
3. **O problema do segredo zero permanece**, e apenas se concentra: a chave `age`
   precisa chegar ao servidor de algum jeito.

---

## 6. Vault / OpenBao — o mínimo operacional

```bash
# desenvolvimento — em memória, destravado. Ótimo para aprender, CRIMINOSO em produção.
docker run --rm -d --name bao -p 8200:8200 \
  -e BAO_DEV_ROOT_TOKEN_ID=raiz openbao/openbao:latest \
  server -dev -dev-listen-address=0.0.0.0:8200
```

```bash
export BAO_ADDR=http://127.0.0.1:8200 BAO_TOKEN=raiz
bao kv put secret/minha-app API_KEY=sk_live_xxx DATABASE_URL=postgres://...
bao kv get -field=API_KEY secret/minha-app
```

### Os conceitos que você precisa dominar

| Conceito | O que é |
|---|---|
| **Selo (seal)** | ao iniciar, o Vault está **selado** e não responde. Precisa ser destravado |
| **Auto-unseal** | destravar automaticamente usando KMS da nuvem ou TPM — **obrigatório em produção** |
| **Método de auth** | como a aplicação prova quem é: AppRole, Kubernetes, JWT/OIDC, IAM da nuvem |
| **Política** | o que aquela identidade pode ler/escrever |
| **Concessão (lease)** | validade do segredo entregue; renovável e revogável |
| **Motor de segredos** | KV (estático), database (dinâmico), PKI (certificados), Transit (cifra sem guardar) |

🚨 **Sem auto-unseal, todo reinício do Vault exige que humanos com as chaves de
Shamir se reúnam para destravá-lo.** Às 3h da manhã. É a razão nº 1 de arrependimento
com Vault autogerenciado.

### Autenticação de aplicação, sem segredo zero

```bash
# em Kubernetes: a app prova quem é com o token da ServiceAccount
bao auth enable kubernetes
bao write auth/kubernetes/role/minha-app \
  bound_service_account_names=minha-app \
  bound_service_account_namespaces=producao \
  policies=minha-app-leitura ttl=1h
```

Aqui **não há segredo zero**: a identidade vem do orquestrador, que a atesta.
É o modelo ideal, e o assunto de [60-teoria-avancada.md §5](60-teoria-avancada.md).

### O motor Transit — cifrar sem guardar

```bash
bao write transit/encrypt/dados-clientes plaintext=$(base64 <<< "CPF: 000.000.000-00")
# devolve: vault:v1:8SDd3WHDOjf7mq69...
```

Sua aplicação **nunca vê a chave de criptografia**. Ela manda o texto e recebe o
cifrado. Rotacionar a chave não exige reescrever os dados (o prefixo `v1` diz qual
versão cifrou). É "criptografia como serviço", e resolve elegantemente o problema de
cifrar dados sensíveis em banco.

---

## 7. Integrar sem acoplar

**A regra de projeto que evita arrependimento:** o cofre é mais uma **fonte** que
preenche o ambiente. O código de negócio continua lendo `process.env`.

```javascript
// boot.mjs
if (process.env.SECRETS_ID) {
  await carregarDoCofre(process.env.SECRETS_ID);   // só preenche o que falta
}
const { config } = await import('./config.mjs');   // o resto do sistema não sabe de nada
```

Isso preserva três coisas: o desenvolvimento local com `.env`, os testes sem cofre, e
a liberdade de trocar de cofre depois sem tocar no código de negócio.

**Três cuidados operacionais:**

1. **Cache com TTL.** Buscar por requisição estoura custo e limite de vazão
   (ver [30 §8](30-entrega-em-producao.md)).
2. **Falha na inicialização.** Cofre fora do ar = aplicação não sobe. É o
   comportamento certo, mas precisa constar do seu plano de indisponibilidade.
3. **Renovação de concessão.** Com credencial dinâmica, alguém precisa renovar
   antes de expirar — normalmente um agente (Vault Agent, OpenBao Agent) que faz
   isso e escreve o valor num arquivo, que a aplicação relê. O padrão `_FILE` de novo.

---

## Autoteste

1. Cite as cinco capacidades que um cofre acrescenta a um arquivo `640`. Qual delas muda de categoria?
2. Explique credencial dinâmica e as três consequências práticas dela.
3. Cite dois preços a pagar por credencial dinâmica que o marketing não menciona.
4. O que mudou na licença do Vault em 2023, e por que isso pode não afetar você?
5. Por que o AWS Parameter Store merece ser considerado antes do Secrets Manager?
6. Como o SOPS funciona por dentro? O que acontece ao adicionar um destinatário?
7. Um colega saiu. Você rodou `sops updatekeys`. Ele ainda lê os segredos? Justifique.
8. O que é o selo (seal) do Vault e por que auto-unseal é obrigatório em produção?
9. Por que a autenticação Kubernetes do Vault elimina o problema do segredo zero?
10. O que o motor Transit resolve, e por que a aplicação nunca ver a chave é importante?
11. Para 3 servidores e uma equipe de 2, você recomendaria um cofre? Justifique.

---

**Fontes consultadas em 14/08/2026:** openbao.org · developer.hashicorp.com/vault ·
getsops.io/docs · aws.amazon.com/secrets-manager/pricing ·
cloud.google.com/secret-manager/pricing · azure.microsoft.com/pricing/details/key-vault ·
infisical.com · doppler.com · external-secrets.io.

**Próximo:** [45-rotacao-e-ciclo-de-vida.md](45-rotacao-e-ciclo-de-vida.md) · Voltar ao [mapa](00-MAPA.md)
