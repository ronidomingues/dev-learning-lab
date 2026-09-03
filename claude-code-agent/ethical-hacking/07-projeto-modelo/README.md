# Projeto-modelo — Pentest completo de uma aplicação web

`Nível: intermediário` · `Última atualização: 12/08/2026`

Este não é um trecho de código: é um **ciclo de pentest inteiro**, do escopo ao relatório,
numa aplicação real que roda na sua máquina. Você recebe:

1. **`app-vulneravel/`** — uma aplicação web deliberadamente insegura (Node.js, sem
   dependências externas). Roda com um comando.
2. **`escopo-e-roe.md`** — o documento de autorização e regras de engajamento, como num
   trabalho real. **Leia primeiro.**
3. **`pentest/`** — o roteiro de teste guiado e um script de reconhecimento reproduzível.
4. **`relatorio/relatorio-exemplo.md`** — o relatório final, o produto que o cliente compra.
5. **`app-corrigida/`** — a mesma aplicação, com as cinco falhas corrigidas, para você
   comparar o antes e o depois e rodar o *retest*.

O que este projeto ensina que tutoriais omitem: que o teste começa por um **documento**, não
por um `nmap`; que o **relatório** é o entregável; e que **corrigir** é parte do ciclo.

---

## Por que sem dependências externas?

A app usa só o módulo `http` nativo do Node. Motivo pedagógico: você consegue **ler o
servidor inteiro** (um arquivo, ~200 linhas) e ver a causa de cada vulnerabilidade no código,
não numa biblioteca opaca. As falhas são as mesmas de apps reais; a moldura é mínima de
propósito.

> ⚠️ **A app é vulnerável de propósito.** Rode apenas em `localhost`, na sua máquina de
> laboratório. Nunca a exponha à internet nem à sua rede. Ela guarda senhas em texto,
> aceita SQL-like injection e serve arquivos arbitrários — por design didático.

---

## Pré-requisitos

- **Node.js 18+** (testado em Node v24.18.0). Verifique: `node --version`.
- Um terminal e um navegador.
- Opcional: `curl` (quase sempre já instalado) e o Burp Suite para a parte manual.

Sem Node? No Kali: `sudo apt install -y nodejs`. Ou use o container:
`docker run --rm -it -v "$PWD":/app -w /app -p 3000:3000 node:24 node app-vulneravel/app.js`.

---

## Como rodar

```bash
# 1. Suba a aplicação vulnerável
cd app-vulneravel
node app.js
# esperado: "App vulneravel ouvindo em http://127.0.0.1:3000  (SOMENTE laboratorio)"
```
```bash
# 2. Em outro terminal, confirme que responde
curl -s http://127.0.0.1:3000/ | head -5
```
```bash
# 3. Rode a bateria de testes automatizada (prova que as 5 falhas existem)
cd pentest
node testar-vulnerabilidades.js
# esperado: "5/5 vulnerabilidades confirmadas"
```

Depois, para ver as correções:
```bash
# 4. Suba a versão corrigida (porta 3001) e rode a MESMA bateria contra ela
node app-corrigida/app.js         # em um terminal
cd pentest && ALVO=http://127.0.0.1:3001 node testar-vulnerabilidades.js
# esperado: "0/5 vulnerabilidades confirmadas" — o retest passou
```

---

## Estrutura de pastas

```
07-projeto-modelo/
├── README.md                         ← este arquivo
├── escopo-e-roe.md                   ← autorização + regras de engajamento (LEIA 1º)
├── app-vulneravel/
│   ├── app.js                        ← servidor com 5 vulnerabilidades comentadas
│   └── usuarios.db.json              ← "banco" em arquivo (senhas em texto, de propósito)
├── app-corrigida/
│   └── app.js                        ← as 5 falhas corrigidas, com comentário do porquê
├── pentest/
│   ├── roteiro.md                    ← passo a passo manual das 5 fases
│   └── testar-vulnerabilidades.js    ← prova automatizada (serve de retest também)
└── relatorio/
    └── relatorio-exemplo.md          ← o entregável final, formatado como o de verdade
```

## O que cada decisão de projeto ensina

| Decisão | O que ensina |
|---|---|
| Começar por `escopo-e-roe.md` | Que autorização e limites vêm **antes** da primeira ferramenta. |
| App legível de 1 arquivo | A ver a **causa-raiz** no código, não só o sintoma. |
| Teste automatizado que vira retest | Que "corrigido" precisa ser **provado**, com o mesmo teste. |
| Versão corrigida lado a lado | O que muda no código para a falha sumir — a defesa concreta. |
| Relatório como arquivo final | Que o produto é o documento, não o acesso. |

## As cinco vulnerabilidades plantadas

Mapeadas ao OWASP Top 10:2025 (ver [`18-seguranca-web.md`](../18-seguranca-web.md)):

| # | Falha | Categoria OWASP 2025 | Onde no código |
|---|---|---|---|
| 1 | IDOR — ver conta de outro usuário | A01 Broken Access Control | rota `/api/conta` |
| 2 | Injeção (query montada por concatenação) | A03 Injection | rota `/api/login` |
| 3 | Path traversal — ler arquivos do servidor | A01 / A05 | rota `/download` |
| 4 | Senha em texto puro + sem rate limit | A07 Auth Failures / A02 Crypto | `usuarios.db.json`, `/api/login` |
| 5 | Segredo/*stack trace* vazando em erro | A05 Misconfiguration / A10 | tratamento de erro global |

Depois de rodar o projeto, você vai ter feito, num ciclo só, o que o curso inteiro descreve.
Próximo passo: [`70-pratica.md`](../70-pratica.md).
