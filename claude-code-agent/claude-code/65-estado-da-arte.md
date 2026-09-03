# 65 · Estado da arte — agosto de 2026

> **Nível:** avançado · **Escrito em:** 13/08/2026 · **Base:** Claude Code 2.1.231
> ⚠️ **Este arquivo é o que envelhece mais rápido do curso, junto com o [`05`](05-manual-de-uso.md).**
> Números de terceiros estão marcados com a fonte; onde há opinião, está dito.
> **Reavalie em dezembro de 2026.**

---

## 1. Onde o campo está

Três frases que resumem agosto de 2026:

1. **A questão deixou de ser "o modelo consegue escrever este código?"** — nas tarefas com
   oráculo claro, consegue. Passou a ser **"como verificar em escala o que ele produz?"**.
2. **A superfície virou plataforma.** Hooks, skills, subagentes, plugins, MCP, headless,
   nuvem, times de agentes. O produto de 2025 era um chat no terminal; o de 2026 é um
   ambiente programável.
3. **A adoção corporativa saiu do piloto** e entrou nos problemas chatos: custo por assento,
   política gerenciada, auditoria, atribuição de responsabilidade.

---

## 2. O panorama competitivo

**[dados de agregadores de terceiros, consultados em 13/08/2026 — não são fontes primárias
e devem ser tratados com ceticismo; leaderboards de código são notoriamente instáveis]**

| Ferramenta | Aposta principal |
|---|---|
| **Claude Code** (Anthropic) | Profundidade de plataforma: contexto de 1 M, hooks, subagentes, SDK |
| **Codex CLI** (OpenAI) | Execução em sandbox na nuvem |
| **Antigravity CLI** (Google) | Anunciado em 19/05/2026, substituindo o Gemini CLI. Orquestração multiagente, subagentes dinâmicos, tarefas agendadas |
| **Cursor** | Experiência de uso dentro do editor |
| **Windsurf** | Agentes em paralelo |
| **opencode** e outros de código aberto | Independência de fornecedor; troca de modelo |

Números de *benchmark* que circulavam em 13/08/2026, **todos de agregadores**:
SWE-bench Verified com líderes na faixa de 88–95%; Terminal-Bench 2.1 com os dois primeiros
colocados praticamente empatados em ~89%.

**Como ler isso, que é a parte útil:**

1. **A dispersão entre os primeiros colocados é menor que a dispersão entre repositórios.**
   O mesmo agente resolve 90% num projeto com testes rápidos e 40% num sem testes. A
   escolha da ferramenta importa menos que o estado do seu repositório. **[opinião, coerente
   com o Pilar 1 do [`25`](25-o-oficio-do-profissional.md)]**
2. **SWE-bench mede tarefas com oráculo.** São issues do GitHub com testes que decidem se
   passou. Ou seja: mede exatamente a categoria em que agentes são fortes, e não mede a que
   é difícil — trabalho sem critério objetivo.
3. **Contaminação é problema reconhecido.** Repositórios públicos entram em conjuntos de
   treino. Trabalhos como o UTBoost investigam justamente a rigidez dessas avaliações.
4. **Eficiência de token virou eixo de comparação**, e não só qualidade — o que confirma que
   o custo do laço, e não a capacidade, é o limitante prático.

---

## 3. O que mudou na prática em 2026

| Mudança | Por que importa |
|---|---|
| **Janela de 1 milhão de tokens** | Cabe um projeto inteiro — e ficou claro que **caber não é entender** ([`60`](60-teoria-avancada.md)) |
| **Modo `auto`** com classificador separado | Menos prompts sem abrir a mão de tudo. **A partir de 14/08/2026 vira o padrão** em Pro, Max e Team |
| **Skills substituindo comandos** | Reconhecimento de que `CLAUDE.md` não escala como contêiner de procedimento |
| **Times de agentes** (experimental) | Orquestração de várias sessões — a **~7× o custo de tokens** |
| **Sessões em nuvem, background, Remote Control** | O agente deixou de estar preso ao seu terminal |
| **Saída estruturada (`--json-schema`)** | O que torna o agente utilizável **dentro** de software |
| **Inteligência de código (LSP) por plugin** | Navegação exata em vez de busca textual: menos contexto, menos erro |
| **Configuração gerenciada e analytics** | O aparato corporativo que faltava |

---

## 4. Debates em aberto

### 4.1 Autonomia × supervisão

Um polo empurra para mais autonomia (modo auto, sessões em background, times de agentes);
o outro observa que a revisão humana já é o gargalo e que mais autonomia agrava a fila.

**[opinião]** Ambos estão certos sobre metade do problema. Autonomia rende **onde há
oráculo forte** e vira dívida onde não há. A pergunta certa não é "quanto de autonomia?",
e sim "qual a força do meu oráculo nesta tarefa?".

### 4.2 MCP × CLI

MCP padronizou integração — e criou um custo de contexto recorrente que a CLI não tem. A
mitigação por carregamento adiado ajudou, mas não eliminou.

**[opinião]** MCP ganha onde não há CLI, onde a autenticação é interativa, ou onde o
servidor **empurra** eventos. Nos demais casos, `gh`, `kubectl` e `psql` continuam vencendo
— e a própria documentação oficial recomenda a CLI quando ela existe.

### 4.3 Contexto grande × contexto curado

Janelas cresceram muito mais rápido do que a capacidade de usá-las bem. *Lost in the middle*
continua valendo em 2026.

**[consenso emergente]** Curadoria vence tamanho. É o que sustenta subagentes, filtragem por
hook e regras com `paths:`.

### 4.4 Quem responde pelo código gerado

Sem resposta técnica, jurídica ou organizacional consolidada. Na prática vigente: **quem
fez merge é o responsável** — e é o único arranjo que funciona hoje. **[opinião]**

### 4.5 O efeito sobre quem está começando

Uma pessoa iniciante que delega tudo não constrói o julgamento necessário para avaliar o
que foi delegado. **[opinião, sem dado conclusivo]** Minha leitura: o agente é excelente
para aprender **com** ele (peça explicação, faça você, compare) e péssimo para aprender
**por meio** dele (peça pronto, aceite, siga). A diferença é quem exerce o raciocínio.

---

## 5. O que ainda não funciona bem

Sendo específico, porque listas otimistas não ajudam ninguém:

| Área | Estado real |
|---|---|
| **Mudança arquitetural grande** | O agente segue a arquitetura existente; questionar a estrutura ainda é trabalho humano |
| **Código sem teste, sem tipo e sem convenção** | Resultado ruim e caro. Não é falha do modelo: não há oráculo |
| **Verificar o que não tem oráculo** | O problema central em aberto |
| **Memória entre sessões** | `CLAUDE.md` e memória automática são aproximações grosseiras |
| **Coordenação de vários agentes** | Custo alto, ganho inconsistente, sem ferramentas de consistência |
| **Estimar esforço** | O agente é otimista de forma sistemática ao prever o que vai conseguir |
| **Dizer "não sei"** | Melhorou, ainda insuficiente. A confiança continua desacoplada da correção |

---

## 6. Para onde parece ir

**[especulação fundamentada — trate como hipótese, não previsão]**

1. **Verificação vira o produto.** Ferramentas cujo valor é *checar* trabalho de agente:
   geração de teste com garantia, verificação diferencial, prova assistida em escopos
   restritos. É onde está o gargalo, logo é onde deve ir o investimento.
2. **Arquiteturas híbridas de contexto.** Atenção completa nos blocos que precisam +
   recorrência barata no resto. Muda a economia do laço mais do que qualquer prompt.
3. **Padronização da configuração de agente.** `AGENTS.md`, Agent Skills, MCP: convergência
   parcial já em curso, ainda longe de portabilidade real.
4. **Consolidação do papel humano.** O trabalho migra para especificar, verificar e decidir
   arquitetura. Não é "o programador desaparece"; é o mesmo movimento de abstração que
   ocorreu com o compilador — só que mais rápido, e mais desconfortável por isso.
5. **Regulação e auditoria.** Setores regulados vão exigir rastreabilidade do que foi gerado
   por agente. Quem já mantém atribuição nos commits vai agradecer.

---

## 7. O que **não** mudou, e provavelmente não vai

Vale fechar por aqui, porque é o que dá estabilidade ao resto do curso:

- **Teoria da computação.** Rice, parada, indecidibilidade: nenhum modelo derruba teorema.
- **"Testes mostram presença, não ausência de bugs"** (Dijkstra, 1970) — mais relevante hoje
  do que quando foi escrito.
- **A atenção é quadrática.** Constantes melhoraram muito; a ordem, não.
- **Contexto é orçamento.** Janela maior mudou os números, não o princípio.
- **Você é responsável pelo que faz merge.**

---

## Fontes consultadas

- Documentação oficial do Claude Code (code.claude.com/docs), 13/08/2026 — recursos, modo
  auto e a data de 14/08/2026 para a mudança de padrão, custo de times de agentes.
- Buscas na web em 13/08/2026 sobre panorama competitivo e leaderboards. As fontes
  encontradas são **agregadores de terceiros**, entre eles morphllm.com, deployhq.com,
  irenictech.com e lushbinary.com, além de páginas de leaderboard como llm-stats.com.
  Os números citados na seção 2 vêm delas e **não** foram verificados contra fonte primária.
- Trabalhos de avaliação citados: *SWE-bench Verified* (OpenAI), *UTBoost* (arXiv 2506.09289),
  *Holistic Agent Leaderboard* (arXiv 2510.11977).

---

## Autoteste

1. Quais são as três frases que resumem agosto de 2026?
2. Por que a dispersão entre os primeiros colocados importa menos que a dispersão entre repositórios?
3. Que categoria de tarefa o SWE-bench mede — e qual ele **não** mede?
4. Enuncie os dois lados do debate autonomia × supervisão e a pergunta que os reconcilia.
5. Em que casos MCP ganha da CLI, segundo este arquivo e a documentação oficial?
6. Cite três coisas que ainda não funcionam bem, e diga se a causa é o modelo ou o repositório.
7. Cite três coisas que não mudaram e provavelmente não vão mudar. Por quê?
8. Qual a diferença entre aprender **com** o agente e aprender **por meio** dele?
