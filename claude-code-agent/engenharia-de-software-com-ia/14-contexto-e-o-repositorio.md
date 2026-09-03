# 14 · Contexto e o repositório — o repositório é o prompt

**Nível:** intermediário · **Escrito em:** 20/08/2026

---

## A ideia central

> **O prompt que mais importa não é o que você digita. É o repositório.**

Um agente monta o entendimento dele a partir do que encontra: nomes de arquivo,
estrutura de pastas, testes, tipos, README, mensagens de commit, `AGENTS.md`.
Tudo isso é entrada.

Consequência direta e um pouco desconfortável: **melhorar o repositório é
melhorar o prompt permanentemente, para todas as sessões futuras, de todas as
pessoas.** Melhorar o prompt melhora uma sessão.

Isso reordena prioridades. Meia hora arrumando os nomes dos módulos rende mais,
ao longo de um trimestre, do que qualquer técnica de prompt.

---

## 1 · A hierarquia do contexto

Da mais permanente para a mais volátil:

| Camada | Onde vive | Vida útil | Custo de manter |
|---|---|---|---|
| **Estrutura do código** | nomes, pastas, tipos, testes | anos | alto, paga sempre |
| **Instruções do repositório** | `AGENTS.md`, `CLAUDE.md` | meses | baixo |
| **Decisões registradas** | ADRs, comentários de *porquê* | anos | baixo |
| **Especificação da tarefa** | `ESPEC.md`, *issue* | dias | baixo |
| **Instrução da sessão** | o que você digita | minutos | zero |

**Regra:** ao repetir uma instrução pela terceira vez, ela subiu de camada.
Escreva-a no arquivo.

---

## 2 · `AGENTS.md` — o formato que venceu

Nasceu em agosto de 2025 de uma colaboração entre OpenAI, Google, Cursor,
Factory e Sourcegraph. Em dezembro de 2025 foi doado à **Agentic AI Foundation**,
sob a Linux Foundation. Mais de **60.000 projetos** o adotam e **24 ferramentas**
o leem — Codex, Jules, Factory, Aider, goose, opencode, Zed, Warp, VS Code,
Devin, Junie, Amp, Cursor, RooCode, Gemini CLI, Kilo Code, Semgrep, Copilot
Coding Agent, Windsurf, Augment Code, entre outras.

É Markdown comum na raiz do repositório. Sem esquema, sem validação.

### O que colocar

| Seção | Conteúdo | Exemplo |
|---|---|---|
| **Comandos** | Como instalar, testar, buildar, rodar migração | `npm ci` · `npm test` · `npm run lint` |
| **Estrutura** | O que é cada pasta, em uma linha | `src/domain/` = regra de negócio, sem I/O |
| **Convenções não óbvias** | O que o código não conta sozinho | "erros de domínio herdam de `DomainError`" |
| **Proibições** | O que nunca deve acontecer | "não edite `schema.sql` à mão" |
| **Armadilhas** | Onde alguém já se queimou | "`user` está morta; use `user_v2`" |

### O que **não** colocar

- Explicação de conceitos gerais ("um teste unitário é...").
- Informação já óbvia no código.
- Documentação de API pública (isso é `README.md`).
- Regras que ninguém segue. Instrução ignorada é ruído, e ruído consome
  contexto que faltaria ao código.

### Tamanho

**Uma tela.** 50 a 150 linhas. A pesquisa acadêmica sobre *configuration smells*
em `AGENTS.md` (arXiv 2606.15828, 2026) identifica arquivos inchados e
instruções contraditórias como os defeitos mais comuns — e ambos degradam a
aderência.

Teste caseiro honesto: **se um humano novo não seguiria aquilo, o agente também
não vai.**

### Hierarquia

```
repositorio/
├── AGENTS.md                 regras gerais
├── frontend/
│   └── AGENTS.md             regras do frontend
└── servicos/pagamento/
    └── AGENTS.md             regras de pagamento (mais específicas)
```

O arquivo mais próximo do que está sendo editado costuma ter precedência. É a
mesma lógica de `.gitignore` ou `.editorconfig`, e pelo mesmo motivo: contexto
local é mais relevante e mais barato.

### `AGENTS.md` vs. `CLAUDE.md` vs. `.cursorrules`

| Arquivo | Situação em 08/2026 |
|---|---|
| `AGENTS.md` | **O padrão.** Use este |
| `CLAUDE.md` | Específico do Claude Code, que também lê `AGENTS.md` |
| `.cursorrules` | Legado. Ainda lido por compatibilidade; não crie novos |
| `.github/copilot-instructions.md` | Específico do Copilot |

**Recomendação:** um `AGENTS.md` com todo o conteúdo. Se precisar de algo
específico de uma ferramenta, um arquivo curto que aponte para ele.

---

## 3 · Registrar decisões: ADR

Um **ADR** (*Architecture Decision Record*) é um arquivo curto que registra uma
decisão e, principalmente, **por que** ela foi tomada. Formato criado por
Michael Nygard em 2011.

```markdown
# ADR-014 — Não migrar `billing.js` antes do fim do contrato com o adquirente

Data: 2026-03-11 · Status: aceita

## Contexto
`src/legacy/billing.js` tem 2.800 linhas, zero testes, e implementa a
integração com o adquirente atual. O contrato vence em 2027-06.

## Decisão
Congelar o arquivo. Nenhuma refatoração até a migração de adquirente.

## Consequências
- O linter fica desabilitado nesse arquivo.
- Correção de bug ali exige teste manual documentado.
- Quem tocar sem necessidade cria risco sem contrapartida.
```

### Por que ADR importa muito mais na era dos agentes

Sem o ADR-014, **todo agente que passar por ali vai propor refatorar** — e a
proposta será tecnicamente correta e estrategicamente errada. Você vai gastar o
mesmo argumento toda semana.

Com o ADR e uma linha no `AGENTS.md` apontando para ele, a decisão está no
contexto. O agente para de sugerir, e — mais importante — **o humano novo que
entrar na equipe também entende**.

> Este é o exemplo mais limpo de um princípio geral: **as práticas que fazem um
> repositório ser bom para agentes são as mesmas que o fazem bom para humanos.**
> A IA não trouxe práticas novas; ela tornou caro continuar ignorando as antigas.

---

## 4 · O que o agente lê sem você mandar

Vale saber, porque muda o que você escreve:

| Sinal | O que ele extrai |
|---|---|
| Nome de arquivo e pasta | Onde as coisas ficam, o que é o quê |
| Assinaturas e tipos | Contratos, sem precisar ler corpo |
| Testes | **A especificação executável.** Frequentemente o sinal mais forte |
| `package.json` / `pyproject.toml` | Stack, versões, scripts disponíveis |
| Mensagens de commit recentes | O que está sendo feito agora |
| `README.md` | Propósito e como rodar |
| Código vizinho | O padrão a seguir |

### Consequência prática, e é forte

**Teste bem escrito vale mais que documentação bem escrita**, porque ele é
verificável e nunca fica desatualizado sem alguém notar.

Um agente que lê `test_calcula_juros_compostos_com_carencia` entende mais que
lendo um parágrafo dizendo "calcula juros". E se o comportamento mudar, o teste
quebra; o parágrafo, não.

---

## 5 · Gestão de contexto na sessão

### Uma tarefa, uma sessão

Motivos, em ordem de importância:

1. **Qualidade.** Contexto poluído com tentativas anteriores erradas condiciona o
   modelo a repetir a linha de raciocínio ruim.
2. **Custo.** Você paga a entrada inteira a cada passo. Contexto grande é caro
   por passo e o passo se repete dezenas de vezes.
3. **Atenção.** Efeito de "perdido no meio" (ver [12](12-o-modelo-por-dentro.md)).

### O que fazer quando a tarefa é grande demais

Não estique a sessão. **Materialize o estado num arquivo** e recomece:

```
Antes de eu limpar o contexto: escreva em ESTADO.md
1. o que já foi feito e onde
2. o que falta, em ordem
3. as decisões tomadas e por quê
4. o que você tentou e não funcionou

Seja específico com caminhos de arquivo.
```

Depois `/clear`, e na sessão nova: *"Leia `ESTADO.md` e continue do item 2."*

Isso é o equivalente de um *checkpoint*, e é a técnica que mais separa quem
trabalha bem em tarefas longas de quem não trabalha.

### Compactação automática

Ferramentas modernas resumem o histórico quando a janela enche. Funciona, e
**perde informação** — inevitavelmente, porque resumo é compressão com perda.

Sinal de que aconteceu: o agente repete algo já feito, ou esquece uma restrição
que você deu no começo. **Quando notar isso, prefira `/clear` + `ESTADO.md` a
continuar.** Compactar duas vezes é copiar uma cópia.

---

## 6 · Repositório legível por agente — o checklist

Cada item é uma melhoria permanente, ordenada por retorno sobre esforço.

| # | Prática | Por que ajuda o agente |
|---|---|---|
| 1 | Um comando roda todos os testes | Dá a ele um sensor de "está bom?" |
| 2 | Testes rodam em < 5 min | Ele consegue iterar; acima disso, ele "chuta e reza" |
| 3 | `AGENTS.md` de uma tela | Instruções permanentes no contexto |
| 4 | Tipos ou anotações | Contrato explícito; menos leitura, menos invenção |
| 5 | Nomes que dizem a verdade | Ele confia no nome. Nome que mente causa erro sistemático |
| 6 | Erro com mensagem específica | Ele lê a mensagem e se corrige. `Exception: erro` não ajuda |
| 7 | Fronteiras de módulo claras | Limita o raio da mudança |
| 8 | `README` com "como rodar" | Ele consegue começar sozinho |
| 9 | Commits pequenos e atômicos | Ele aprende o padrão do projeto; e `bisect` funciona |
| 10 | ADRs para decisões contraintuitivas | Ele para de propor o que já foi decidido |
| 11 | Lockfile commitado | Ambiente reprodutível |
| 12 | Portão automático antes da `main` | O que este curso inteiro defende |

> **Repare:** nenhum item desta lista menciona IA. **É engenharia de software
> comum.** A diferença é que antes o custo de ignorar era difuso e distante;
> agora é imediato e mensurável, porque o agente falha visivelmente onde o
> repositório é ruim.

---

## Autoteste

1. Por que "o repositório é o prompt"? Qual é a consequência prática disso?
2. Cite as cinco camadas de contexto. Quando uma instrução deve subir de camada?
3. Quem mantém o `AGENTS.md` hoje e qual é a adoção medida?
4. Qual é o tamanho recomendado e o teste caseiro para saber se está bom?
5. O que é um ADR e por que ele ficou mais importante na era dos agentes?
6. Por que teste bem escrito vale mais que documentação bem escrita para um
   agente?
7. Cite os três motivos de "uma tarefa, uma sessão", em ordem de importância.
8. Como se preserva estado entre sessões, e por que isso é melhor que esticar a
   sessão?
9. Quais são os dois sinais de que a compactação automática aconteceu, e o que
   fazer?
10. Por que nenhum item do checklist do §6 menciona IA?

---

**Anterior:** [13-os-quatro-modos-de-uso](13-os-quatro-modos-de-uso.md) ·
**Próximo:** [15-o-loop-do-agente](15-o-loop-do-agente.md)
