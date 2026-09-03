# 02 · Pré-requisitos

**Nível:** iniciante · Atualizado em 13/08/2026

---

## Conhecimento

### Indispensável

| O que | Por que | Onde aprender |
|---|---|---|
| **Terminal básico** — `cd`, `ls`, `pwd`, editar um arquivo, ler uma mensagem de erro | O Claude Code *é* um programa de terminal. Se `cd` te trava, tudo trava. | [The Missing Semester (MIT), aula 1](https://missing.csail.mit.edu/2020/course-shell/) — 1 h, legendas em PT |
| **Git no essencial** — `status`, `diff`, `add`, `commit`, `branch` | O agente edita seus arquivos. Sem `git diff` você não revisa; sem commit você não tem rede de proteção. | [Pro Git, capítulos 1–3](https://git-scm.com/book/pt-br/v2) — grátis, em português |
| **Ler código em pelo menos uma linguagem** | Você é o revisor. Aprovar código que você não entende é assinar em branco. | qualquer linguagem serve |
| **O que é uma API e uma chave de API** | Custo, limite e segurança dependem disso. | [04](04-como-comecar.md) explica o mínimo |

### Ajuda muito

| O que | Por que |
|---|---|
| **JSON** | Todo o material de configuração (`settings.json`, `.mcp.json`) e o protocolo MCP são JSON. |
| **Python ou TypeScript** | Para construir o seu próprio agente ([19](19-agent-sdk-e-agentes-proprios.md)) e para o projeto-modelo. |
| **Testes automatizados** | O laço agêntico funciona porque o agente pode verificar. Sem suíte de testes, o agente fica cego. Ver o assunto [`testes-automatizados`](../testes-automatizados/00-MAPA.md) desta pasta. |
| **Docker** | Sandbox é a forma séria de dar autonomia sem risco. Ver [`docker`](../docker/00-MAPA.md). |
| **Noção de como um LLM funciona** (tokens, contexto, alucinação) | Explica por que o agente "esquece" e por que ele às vezes inventa. Ver [`bert`](../bert/00-MAPA.md) para a base de transformers. |

### O que **não** é pré-requisito

- Matemática de aprendizado de máquina. Você vai *usar* o modelo, não treiná-lo.
- Saber inglês fluente. Ajuda para ler documentação (a oficial não tem
  tradução completa), mas você pode conversar com o agente em português.
- Placa de vídeo. Nada roda localmente.

---

## Rota de resgate (se faltar um pré-requisito)

| Falta | O que fazer agora |
|---|---|
| Terminal | Faça a aula 1 do Missing Semester (1 h). Depois volte. É o único item realmente bloqueante. |
| Git | Comece assim mesmo, mas **crie um commit antes de cada sessão** com o agente. Aprenda `git diff` na semana seguinte. |
| Linguagem de programação | Use o Claude Code em modo `plan` (`Shift+Tab` duas vezes): ele explica e propõe, sem editar. Você aprende lendo os planos. |
| Testes | Peça ao agente para escrever o teste **antes** da correção. Você ganha a rede de proteção e aprende o assunto de graça. |
| Não sabe programar de jeito nenhum | Use o Claude na web (claude.ai) por algumas semanas. Volte quando `cd` e `git commit` forem automáticos. |

---

## Ambiente

### Sistema operacional

| SO | Versão mínima | Observação |
|---|---|---|
| macOS | 13.0 | Intel e Apple Silicon |
| Windows | 10 (build 1809) ou Server 2019 | nativo **ou** WSL 2 — ver [03](03-instalacao.md) |
| Ubuntu | 20.04 | |
| Debian | 10 | |
| Alpine | 3.19 | exige pacotes extras, ver [03](03-instalacao.md) |

### Hardware

- **RAM:** 4 GB mínimo. Na prática, 8 GB é o piso confortável — o Claude Code
  é um processo Node/nativo que fica residente, e você vai ter editor,
  navegador e testes rodando junto.
- **Processador:** x64 ou ARM64.
- **Disco:** ~1,5 GB para o binário e as versões guardadas, mais o que os
  transcritos das sessões ocuparem em `~/.claude/` (cresce devagar; some
  algumas centenas de MB por mês de uso pesado).
- **Placa de vídeo:** irrelevante.

### Rede

Conexão obrigatória e constante — cada turno é uma chamada de API. Em rede
corporativa com proxy ou certificado interno, veja a seção correspondente em
[03-instalacao.md](03-instalacao.md#rede-corporativa) **antes** de instalar.

### Conta

O Claude Code exige uma destas:

| Conta | Serve? |
|---|---|
| Claude.ai **gratuito** | ⚠️ fontes divergem — ver [80](80-custos-e-licencas.md#1-assinaturas). Insuficiente para uso real de qualquer forma |
| Claude Pro | ✅ |
| Claude Max (5× ou 20×) | ✅ |
| Team / Enterprise | ✅ |
| Anthropic Console (chave de API, pago por uso) | ✅ |
| Amazon Bedrock / Google Cloud / Microsoft Foundry | ✅ (configuração adicional) |

Preços, limites e o que cabe em cada plano: [80-custos-e-licencas.md](80-custos-e-licencas.md).

> **Cartão de crédito:** a assinatura Pro/Max exige cartão. A conta de API do
> Console também. Não existe camada gratuita permanente do Claude Code. Se
> isso for impeditivo, [80](80-custos-e-licencas.md) lista as alternativas
> abertas (OpenHands, Aider, Cline com modelos locais).

---

## Tempo realista até cada nível

Estimativas para alguém que já programa, estudando **fora** do horário de
trabalho. Se você puder usar no trabalho, divida por dois — a prática diária
domina qualquer curso.

| Nível | O que você consegue fazer | Tempo |
|---|---|---|
| **Instalado e produtivo** | corrigir bugs pequenos, escrever testes, entender um repositório novo | **1 a 2 dias** (~6 h) |
| **Confortável** | `CLAUDE.md` decente, permissões ajustadas, plan mode como hábito, sabe quando o agente vai falhar | **2 a 3 semanas** (~15 h) |
| **Avançado no uso** | MCP próprio, hooks, skills, subagentes, sessões paralelas com worktrees | **1 a 2 meses** (~40 h) |
| **Constrói o próprio agente** | laço com o Agent SDK ou com a Claude API, ferramentas próprias, avaliação | **+1 mês** (~40 h) — exige o assunto [`apis`](../apis/00-MAPA.md) |
| **Nível de pesquisa** | lê e critica papers, projeta avaliação honesta, conhece os limites teóricos | **6 meses a 1 ano**, contínuo |

**Sendo honesto sobre a curva:** o dia 1 é surpreendentemente fácil e o mês 1
é surpreendentemente frustrante. A razão é sempre a mesma: no dia 1 você faz
tarefas pequenas e verificáveis; no mês 1 você tenta tarefas grandes e o
agente perde o fio. Aprender a **fatiar a tarefa** é 80% da habilidade, e não
se aprende lendo — só apanhando. [75-armadilhas.md](75-armadilhas.md) encurta
esse caminho.

---

## Checklist antes de seguir para o `03`

```bash
# 1. Terminal funciona e você sabe onde está
pwd
# esperado: um caminho, ex.: /home/voce

# 2. Git instalado
git --version
# esperado: git version 2.x.y  (se "command not found", instale antes)

# 3. Você está numa pasta que é um repositório git (recomendado, não obrigatório)
git status
# esperado: "On branch main" ou similar

# 4. Tem curl (necessário para o instalador)
curl --version | head -1
# esperado: curl 7.x ou 8.x

# 5. Rede alcança a Anthropic
curl -sS -o /dev/null -w '%{http_code}\n' https://api.anthropic.com/
# esperado: um código HTTP (401 ou 404 servem — significa que chegou lá).
#           Se travar ou der 000, você está atrás de proxy: leia o 03 antes.
```

Cinco linhas verdes? Siga para [03-instalacao.md](03-instalacao.md).

---

## Autoteste

1. Qual é o **único** pré-requisito realmente bloqueante, e por quê?
2. Você não sabe Git. Qual é a rota de resgate, e qual risco concreto ela
   mitiga?
3. Por que testes automatizados aparecem em "ajuda muito" e não em
   "indispensável", se o laço agêntico depende de verificação?
4. Um colega quer usar o Claude Code com a conta gratuita do Claude.ai. O que
   você responde?
5. Por que o mês 1 tende a ser mais frustrante que o dia 1?
6. O comando `curl https://api.anthropic.com/` devolveu `401`. Isso é problema?
7. Quanto tempo, realisticamente, até conseguir escrever um servidor MCP
   próprio — e de que assunto adjacente isso depende?
