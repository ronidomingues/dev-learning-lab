# Relatório de Teste de Invasão — Aplicação LojaExemplo

**Cliente:** LojaExemplo Ltda. (fictício) · **Executante:** [seu nome] ·
**Período:** 12–19/08/2026 · **Classificação:** Confidencial

> Este é o **entregável** do projeto-modelo — o produto que o cliente compra. Um teste sem
> relatório é um hobby. Estrutura completa e boas práticas em
> [`../../24-relatorio-e-comunicacao.md`](../../24-relatorio-e-comunicacao.md).

---

## 1. Sumário executivo

*(Uma página, para quem decide. Sem jargão. Responde: quão ruim, e o que fazer.)*

Foi realizado um teste de invasão na aplicação web da LojaExemplo (`http://127.0.0.1:3000`),
no escopo e período autorizados. Foram identificadas **5 vulnerabilidades**, sendo **2 de
severidade crítica** e **2 alta**. Em conjunto, elas permitem que **qualquer usuário
autenticado acesse dados de todos os clientes** (nome, CPF, saldo) e que **um atacante leia
arquivos internos do servidor**, incluindo senhas e a chave de assinatura de sessão — o que
equivale a comprometimento total da aplicação.

**Risco de negócio:** exposição de dados pessoais (violação de LGPD, art. 46), fraude
financeira e sequestro de contas. Recomenda-se correção **imediata** dos itens críticos antes
de qualquer novo ciclo de produção.

| Severidade | Qtd. | Corrigir em |
|---|---|---|
| 🔴 Crítica | 2 | 24–48 h |
| 🟠 Alta | 2 | 1 semana |
| 🟡 Média | 1 | 1 mês |

## 2. Escopo e metodologia

- **Escopo:** aplicação em `http://127.0.0.1:3000` e seu arquivo de dados. Nada mais.
- **Abordagem:** *grey box* — sem código-fonte, com uma conta de cliente de teste.
- **Metodologia:** PTES + OWASP WSTG. Mapeamento das classes do OWASP Top 10:2025.
- **Limitações:** sem DoS, sem engenharia social, sem alteração de dados (ver RoE).

## 3. Achados técnicos

Cada achado tem: descrição, severidade (CVSS 3.1), reprodução, evidência, impacto e correção.

---

### F-01 · IDOR — acesso a contas de outros usuários 🔴 Crítica

- **CVSS:** 8.1 (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N) · **OWASP:** A01 Broken Access Control
- **Onde:** `GET /api/conta?id=`
- **Descrição:** a rota valida o token de sessão (autenticação) mas devolve a conta do `id`
  informado na URL sem verificar se ele pertence ao usuário logado (falha de autorização).
- **Reprodução:**
  1. Autenticar como `bruno` (cliente comum) e obter o token.
  2. `GET /api/conta?id=1` com esse token → retorna a conta da `ana` (outro cliente).
- **Evidência:** resposta HTTP 200 com `login:"ana"`, `cpf:"111.111.111-11"`, `saldo:1240.55`.
- **Impacto:** qualquer cliente enumera `id=1..N` e coleta PII de toda a base. Violação de LGPD.
- **Correção:** derivar o alvo da **sessão**, não do parâmetro; para acesso a outras contas,
  checar `papel === 'admin'` explicitamente. (Ver `app-corrigida/app.js`, FIX #1.)

### F-02 · Path Traversal — leitura de arquivos internos 🔴 Crítica

- **CVSS:** 9.1 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H) · **OWASP:** A01 / A05
- **Onde:** `GET /download?arquivo=`
- **Descrição:** o nome do arquivo é concatenado ao caminho sem normalização nem verificação
  de prefixo, permitindo `../` para sair da pasta.
- **Reprodução:** `GET /download?arquivo=../../app-vulneravel/usuarios.db.json`
- **Evidência:** retorno do arquivo de dados com senhas em texto e `segredo_jwt`.
- **Impacto:** leitura de qualquer arquivo legível pelo processo (`/etc/passwd`, configs,
  chaves). Com o `segredo_jwt`, forja-se sessão de qualquer usuário → comprometimento total.
- **Correção:** resolver o caminho (`path.resolve`) e exigir que continue dentro da pasta base;
  idealmente, *allowlist* de nomes. (FIX #3.)

### F-03 · Bypass de autenticação por injeção 🟠 Alta

- **CVSS:** 8.1 · **OWASP:** A03 Injection
- **Onde:** `POST /api/login`
- **Descrição:** as credenciais são inseridas numa expressão avaliada dinamicamente (`eval`
  de uma string montada com a entrada). Um valor de senha com aspas e operadores lógicos
  altera a lógica e autentica sem senha válida.
- **Reprodução:** `POST /api/login` com `{"login":"admin","senha":"\" || u.papel===\"admin"}`
  → resposta com `papel:"admin"`.
- **Impacto:** login como qualquer usuário, inclusive admin, sem conhecer a senha.
- **Correção:** nunca avaliar entrada como código; comparar dados diretamente. Em SQL, o
  equivalente é usar *prepared statements*. (FIX #2.)

### F-04 · Ausência de limitação de tentativas + senha em texto 🟠 Alta

- **CVSS:** 7.5 · **OWASP:** A07 Auth Failures / A02 Cryptographic Failures
- **Onde:** `POST /api/login` e `usuarios.db.json`
- **Descrição:** não há *rate limit* nem bloqueio após falhas, viabilizando força bruta; e as
  senhas são armazenadas em **texto puro**.
- **Reprodução:** 10 requisições de login erradas seguidas — todas processadas (nenhum 429).
- **Impacto:** quebra de senhas por força bruta; e qualquer leitura do banco (ver F-02) expõe
  todas as senhas imediatamente, sem esforço de quebra.
- **Correção:** *rate limit*/bloqueio progressivo, MFA, e armazenamento com **bcrypt/argon2**
  (hash lento + sal). (FIX #4.)

### F-05 · Vazamento de informação em mensagens de erro 🟡 Média

- **CVSS:** 5.3 · **OWASP:** A05 Misconfiguration / A10
- **Onde:** tratador de erro global
- **Descrição:** respostas de erro 500 incluem *stack trace* e o objeto de configuração, com
  o `segredo_jwt`.
- **Reprodução:** enviar login com aspas desbalanceadas → 500 com detalhes internos.
- **Impacto:** entrega caminhos internos, versões e segredo de assinatura ao atacante.
- **Correção:** erro genérico ao cliente; detalhe apenas no log do servidor. (FIX #5.)

## 4. Recomendações priorizadas

| Prioridade | Ação | Achados que fecha |
|---|---|---|
| 1 (24–48 h) | Verificação de autorização por objeto + validar caminho de arquivo | F-01, F-02 |
| 2 (1 semana) | Remover `eval`/concatenação; rate limit + hash de senha (argon2) | F-03, F-04 |
| 3 (1 mês) | Erros genéricos ao cliente; rotacionar o `segredo_jwt` vazado | F-05 |
| Contínuo | Revisão de código focada em autorização; testes de segurança no CI | todos |

## 5. Retest

Após aplicar as correções (ver `app-corrigida/app.js`), a mesma bateria de testes foi
reexecutada:

```
$ ALVO=http://127.0.0.1:3001 node testar-vulnerabilidades.js
0/5 vulnerabilidades confirmadas
```

**Todos os cinco achados foram corrigidos e verificados.**

## 6. Anexos

- Comandos de reprodução: [`../pentest/roteiro.md`](../pentest/roteiro.md)
- Evidências automatizadas: saída de `testar-vulnerabilidades.js`
- Escopo e autorização: [`../escopo-e-roe.md`](../escopo-e-roe.md)

---

*Relatório gerado como material didático. Números CVSS são ilustrativos e devem ser
recalculados por achado em um trabalho real (calculadora oficial em first.org/cvss).*
