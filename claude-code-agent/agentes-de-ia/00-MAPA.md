# Agentes de IA — mapa do curso

**Do zero absoluto ao nível de pesquisa, em português.**
Escrito em 13/08/2026 · Base: Claude Code **2.1.231**

---

## O que é este material

Um curso completo sobre **agentes de IA** — o que são, como funcionam por
dentro, e como usar e construir um. O caso concreto que atravessa tudo é o
**Claude Code**, porque é o agente mais maduro disponível hoje e porque é a
melhor forma de estudar o assunto com as mãos.

Metade do que está aqui é independente de fornecedor: o laço agêntico, projeto
de ferramentas, gestão de contexto, avaliação e os limites teóricos valem para
qualquer agente que você venha a usar ou escrever.

## O que você saberá ao final

- Explicar o que é um agente e distingui-lo de um workflow — e escolher o
  certo.
- Instalar, configurar e usar o Claude Code com competência: comandos,
  permissões, contexto, plan mode.
- Estender: MCP, skills, hooks, subagentes, plugins.
- Escrever o laço agêntico à mão e construir o seu próprio agente.
- Avaliar um agente sem se enganar, e ler um benchmark com ceticismo
  fundamentado.
- Saber onde estão os limites teóricos e por que não adianta correr contra
  eles.

## Se você tem pouco tempo

| Tempo | Leia |
|---|---|
| **20 minutos** | [01](01-introducao-leigo.md) |
| **1 hora** | [01](01-introducao-leigo.md) + [10](10-fundamentos.md) |
| **1 dia** | Bloco A inteiro ([01](01-introducao-leigo.md)–[07](07-projeto-modelo/README.md)) |
| **1 semana** | Blocos A e B até o [16](16-subagentes-e-orquestracao.md) |
| **1 mês** | tudo, com os laboratórios do [70](70-pratica.md) |

**Se você quer só a resposta para "quais comandos?":**
[05-manual-de-uso.md](05-manual-de-uso.md).

---

## Roteiro

### Bloco A · Porta de entrada

| # | Arquivo | O que é | Nível |
|---|---|---|---|
| 01 | [introducao-leigo](01-introducao-leigo.md) | o que é um agente, sem jargão nenhum | leigo |
| 02 | [pre-requisitos](02-pre-requisitos.md) | o que saber e ter antes; tempo realista; rota de resgate | iniciante |
| 03 | [instalacao](03-instalacao.md) | manual de campo: 3 SOs, todas as tecnologias, PATH, permissões, proxy, desinstalação, tabela de erros | iniciante |
| 04 | [como-comecar](04-como-comecar.md) | do ambiente pronto ao primeiro resultado; ciclo diário; cinco erros | iniciante |
| 05 | [manual-de-uso](05-manual-de-uso.md) | **referência de comandos, flags e atalhos**, por tarefa | iniciante → interm. |
| 06 | [exemplos](06-exemplos.md) | 12 receitas, do trivial a dois casos de produção | todos |
| 07 | [projeto-modelo/](07-projeto-modelo/README.md) | aplicação completa e **executável**: servidor MCP + testes + laço à mão + skill + hook + subagente | intermediário |

### Bloco B · Núcleo

| # | Arquivo | O que é | Nível |
|---|---|---|---|
| 10 | [fundamentos](10-fundamentos.md) | definição, vocabulário, o laço, agente × workflow | intermediário |
| 11 | [historia](11-historia.md) | de SHRDLU (1968) ao Claude Code; o que sobreviveu e o que morreu | intermediário |
| 12 | [anatomia-do-loop-agentico](12-anatomia-do-loop-agentico.md) | **o capítulo central.** Blocos, `stop_reason`, pensamento, paralelismo, erro, travas | interm. → avançado |
| 13 | [ferramentas-e-tool-use](13-ferramentas-e-tool-use.md) | ACI, descrições, bash × dedicada, as ferramentas do Claude Code | intermediário |
| 14 | [contexto-memoria-compactacao](14-contexto-memoria-compactacao.md) | janela, compactação, `CLAUDE.md`, camadas de memória, cache | intermediário |
| 15 | [mcp-model-context-protocol](15-mcp-model-context-protocol.md) | o protocolo por dentro, escrever servidor, custo e segurança | intermediário |
| 16 | [subagentes-e-orquestracao](16-subagentes-e-orquestracao.md) | as 4 formas de paralelizar, worktrees, workflows, quando não vale | avançado |
| 17 | [hooks-permissoes-seguranca](17-hooks-permissoes-seguranca.md) | permissões, hooks, sandbox, **injeção de prompt**, dados | avançado |
| 18 | [skills-plugins-extensibilidade](18-skills-plugins-extensibilidade.md) | os 5 mecanismos de extensão e como escolher | interm. → avançado |
| 19 | [agent-sdk-e-agentes-proprios](19-agent-sdk-e-agentes-proprios.md) | os 4 caminhos para construir o seu; 7 decisões de projeto | avançado |
| 20 | [avaliacao-e-benchmarks](20-avaliacao-e-benchmarks.md) | SWE-bench e suas reservas; montar a **sua** avaliação | avançado |
| 60 | [teoria-avancada](60-teoria-avancada.md) | POMDP, composição de erro, Rice, injeção como problema fundamental, limites | pesquisa |
| 65 | [estado-da-arte](65-estado-da-arte.md) | instantâneo de ago/2026: modelos, números, debates, fronteiras | pesquisa |

### Bloco C · Prática e erros

| # | Arquivo | O que é |
|---|---|---|
| 70 | [pratica](70-pratica.md) | 14 laboratórios progressivos, com critério de conclusão |
| 75 | [armadilhas](75-armadilhas.md) | 30 armadilhas, 9 mitos, e os 5 erros que mais custam |

### Bloco D · Economia e ecossistema

| # | Arquivo | O que é |
|---|---|---|
| 80 | [custos-e-licencas](80-custos-e-licencas.md) | preços com data, custos ocultos, licenças, dados, alternativas abertas |
| 85 | [cursos-e-certificacoes](85-cursos-e-certificacoes.md) | cursos gratuitos em PT/EN/FR, pesquisados na web; a verdade sobre certificações |

### Bloco E · Fontes

| # | Arquivo | O que é |
|---|---|---|
| 90 | [bibliografia](90-bibliografia.md) | livros comentados, com o que é legalmente gratuito |
| 95 | [referencias](95-referencias.md) | documentação, ~18 papers, código-fonte para ler, benchmarks |
| — | [GLOSSARIO](GLOSSARIO.md) | ~60 termos, todos com link para o capítulo |

---

## As doze camadas de profundidade

| Camada | Onde |
|---|---|
| 1. Intuição para leigo | [01](01-introducao-leigo.md) |
| 2. Definição informal | [01](01-introducao-leigo.md), [10](10-fundamentos.md) |
| 3. Por que existe | [11](11-historia.md) |
| 4. Ambiente e primeiro uso | [02](02-pre-requisitos.md), [03](03-instalacao.md), [04](04-como-comecar.md) |
| 5. Fundamentos formais | [10](10-fundamentos.md), [60](60-teoria-avancada.md) |
| 6. Mecânica interna | [12](12-anatomia-do-loop-agentico.md), [13](13-ferramentas-e-tool-use.md), [14](14-contexto-memoria-compactacao.md), [15](15-mcp-model-context-protocol.md) |
| 7. Implementação prática | [06](06-exemplos.md), [07](07-projeto-modelo/README.md), [19](19-agent-sdk-e-agentes-proprios.md) |
| 8. Casos de uso reais | [06](06-exemplos.md) §11–12, [70](70-pratica.md) |
| 9. Trade-offs e alternativas | [10](10-fundamentos.md), [16](16-subagentes-e-orquestracao.md), [80](80-custos-e-licencas.md) |
| 10. Economia | [80](80-custos-e-licencas.md) |
| 11. Profundidade de pesquisa | [60](60-teoria-avancada.md) |
| 12. Estado da arte e fronteira | [65](65-estado-da-arte.md) |

---

## O que foi executado e verificado

**Verificado em 13/08/2026, em Ubuntu 22.04 / Python 3.10.12 / Node v24.18.0 /
Claude Code 2.1.231:**

- **Projeto-modelo:** `python3 teste_mcp.py` — **19 verificações, todas
  passando.** A saída no [README](07-projeto-modelo/README.md) é a saída real.
- Diálogo JSON-RPC manual com o servidor MCP (`initialize` + `tools/list`).
- Versões de `claude`, `node`, `python3` na máquina de escrita.
- `claude --help` da versão 2.1.231 (usado no [05](05-manual-de-uso.md)).

**Pesquisado na web em 13/08/2026:** instalação e versões
([03](03-instalacao.md)), preços ([80](80-custos-e-licencas.md)), cursos em
PT/EN/FR ([85](85-cursos-e-certificacoes.md)), estado da arte e números de
benchmark ([65](65-estado-da-arte.md)), documentação oficial completa do
Claude Code.

**Declarado como não executado:**

- `agente_minimo.py` do projeto-modelo (exige chave de API e consome créditos).
- A sessão do Claude Code com MCP, skill, hook e subagente (exige assinatura
  ativa). As configurações seguem os esquemas da documentação oficial
  consultada, mas o comportamento em tela não foi verificado aqui.
- Os 14 laboratórios do [70](70-pratica.md) — são roteiros para você executar.
- Instalação em macOS e Windows (documentada a partir das fontes oficiais).
- Os números de benchmark do [65](65-estado-da-arte.md) vêm de compilações
  públicas, não de execução própria.

---

## Status por bloco

| Bloco | Status | Conteúdo |
|---|---|---|
| **A · Porta de entrada** | ✅ | 7 documentos + projeto-modelo executável |
| **B · Núcleo** | ✅ | 13 documentos, do fundamento ao estado da arte |
| **C · Prática e erros** | ✅ | 14 laboratórios, 30 armadilhas, 9 mitos |
| **D · Economia e ecossistema** | ✅ | preços com data, cursos em 3 idiomas |
| **E · Fontes** | ✅ | ~18 papers, documentação, código-fonte, glossário |

**Pendências declaradas** (candidatas a uma próxima rodada):

- Um capítulo dedicado a **agentes fora de código** (atendimento, dados,
  operações) — hoje o assunto aparece só de passagem.
- Um capítulo sobre **frameworks** (LangGraph, CrewAI, AutoGen, smolagents)
  comparados lado a lado.
- Um segundo projeto-modelo em **TypeScript**, para quem não usa Python.
- Uso de computador (agentes que operam interface gráfica) — hoje só citado
  no [65](65-estado-da-arte.md).

---

## Convenções deste material

- **Nível** e **data** no topo de cada arquivo.
- **Autoteste** ao final de cada arquivo (5 a 10 perguntas).
- Opinião do autor marcada explicitamente como opinião.
- Datas absolutas, sempre. Nunca "recentemente".
- Comandos copiáveis, um por bloco, com a saída esperada.
- Termos técnicos em inglês quando é assim que o campo os usa, com tradução na
  primeira ocorrência.

---

Voltar ao [INDICE.md](../INDICE.md) da pasta.
