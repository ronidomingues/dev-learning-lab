# 65 · Estado da arte — agosto de 2026

**Nível:** avançado · **Escrito em:** 20/08/2026
**Este arquivo envelhece rápido.** Reavalie a cada 3 meses.

---

## 1 · Capacidade: onde estamos

### Horizonte temporal (METR, dados v1.1, consultados em 20/08/2026)

| Modelo | Lançamento | Horizonte 50% |
|---|---|---|
| Claude Opus 4.6 | 05/02/2026 | ~12 h |
| Gemini 3.1 Pro | 19/02/2026 | ~6 h 24 min |
| GPT-5.4 | 05/03/2026 | ~5 h 42 min |
| GPT-5.3 Codex | 05/02/2026 | ~5 h 50 min |
| Claude Opus 4.5 | 24/11/2025 | ~4 h 53 min |

Taxa de crescimento: dobra a cada **~130,8 dias (4,3 meses)** desde 2023; antes
disso, ~7 meses.

> **Como ler:** "50%" significa metade das tarefas daquela duração. O modelo que
> completa metade das tarefas de 12 horas **falha na outra metade**, e você não
> sabe qual sem verificar.

### Benchmarks de código: cuidado redobrado

**Aviso importante, e é uma lição do próprio curso:** ao pesquisar para este
arquivo, encontrei múltiplos sites agregadores publicando tabelas de SWE-bench
com números e nomes de modelo que **não batem entre si nem com as fontes
primárias**. Boa parte desse conteúdo é gerada por IA e não verificada.

**Não cite número de benchmark de agregador.** Consulte:

- SWE-bench: https://www.swebench.com/ (Verified, Pro, Multilingual, Multimodal)
- Terminal-Bench: https://www.tbench.ai/
- METR: https://metr.org/time-horizons/

E, mais importante: **o benchmark que vale é o seu**. Um conjunto de 20 tarefas
representativas do seu repositório, rodado a cada troca de modelo, informa mais
que qualquer leaderboard. Método em [70-pratica](70-pratica.md).

### Contexto e preço

- Janelas de **1 milhão de tokens** são padrão nos modelos de ponta.
- Cache de prompt reduz entrada repetida a **10%** do preço.
- Preços por milhão de tokens caíram consistentemente a capacidade constante.
- **Novidade que confunde métrica:** modelos Claude 4.7+ usam tokenizador que
  gera ~30% mais tokens para o mesmo texto. Comparação de custo entre gerações
  exige recalibrar a linha de base.

---

## 2 · O contramovimento: SDD consolidado

*Spec-driven development* deixou de ser tendência e virou categoria de produto.

| Ferramenta | Origem | Nota |
|---|---|---|
| **GitHub Spec Kit** | GitHub, aberto | CLI + templates; ~29 integrações |
| **AWS Kiro** | AWS (internacional em 07/05/2026) | IDE com espec como objeto de primeira classe; notação EARS |
| **OpenSpec, BMAD, Tessl** | comunidade / *startups* | Variações |
| Claude Code, Cursor, Antigravity | fornecedores de agente | Cada um com seu sabor de fluxo espec→plano→tarefas |

**A pergunta em aberto**, e é a mesma que matou o MDA nos anos 90: *o que
acontece com a especificação quando alguém edita o código gerado?* Ninguém
resolveu. Ver [11-historia](11-historia.md) e [16](16-especificacao-e-plano.md).

---

## 3 · Padrões que se consolidaram em 2026

| Padrão | Situação |
|---|---|
| **`AGENTS.md`** | Padrão de fato. Agentic AI Foundation (Linux Foundation) desde dez/2025; 60.000+ projetos, 24 ferramentas |
| **MCP** | Padrão de fato para conectar agentes a sistemas. Superfície de ataque em amadurecimento ([22](22-seguranca.md)) |
| **Agentes assíncronos na nuvem** | Copilot Coding Agent, Jules, Codex, Devin. Consolidados e com o problema de fila documentado |
| **Subagentes** | Presentes em todas as ferramentas maduras |
| ***Sandbox* com lista de domínios** | Virou requisito, não diferencial |
| **Revisão automática de PR** | CodeRabbit, Bugbot, Copilot review, Graphite. Todos como assistente, não decisor |

---

## 4 · O que virou consenso

1. **A revisão é o gargalo.** LinearB (8,1 M de PRs), CircleCI, Sonar e o
   discurso de fornecedores convergiram. Não há mais quem defenda o contrário.
2. **Especificação importa mais que prompt.** A indústria inteira migrou para
   SDD em algum grau.
3. **Verificação automática é pré-requisito de autonomia.** Ninguém sério defende
   agente autônomo sem portão.
4. **`AGENTS.md` é o formato.** Guerra de formatos encerrada.
5. **Adoção não é a questão.** DORA: 90%. Stack Overflow: 84%. A questão é
   **como**.
6. **Confiança caiu enquanto o uso subiu.** 29% de confiança, −11 pontos.

---

## 5 · O que ainda está em disputa

| Debate | Lado A | Lado B | Minha leitura |
|---|---|---|---|
| **A produtividade aumentou de fato?** | DORA: vazão maior | METR: seniores mais lentos; LinearB: ~10% líquido | Depende do contexto; é a pergunta errada. Pergunte "no meu time, medido como?" |
| **A qualidade está piorando?** | GitClear: +81% duplicação | "duplicação nem sempre é ruim" | A tendência é real e ninguém mede. Preocupante |
| **Autonomia total é viável?** | Devin e afins | Ninguém confia sem portão | Viável **com** portão e raio de explosão finito |
| **Modelo local vale a pena?** | Privacidade, custo fixo | Muito atrás em trabalho agêntico | Só quando a privacidade é requisito absoluto |
| **SDD resolve a deriva?** | Adotantes reportam ganho | MDA prometia o mesmo | A prática vale; a ferramenta é aposta |
| **Júnior está sendo prejudicado?** | Contração na contratação | Confundido com macroeconomia | A barra subiu; a causa é múltipla |
| **Devemos marcar código gerado?** | Rastreabilidade | Estigma e burocracia | A favor, pelo valor de investigação |

---

## 6 · O que mudou desde 2025 e você talvez não tenha notado

Cinco mudanças silenciosas com consequência prática:

1. **Prompt elaborado virou desnecessário.** Persona, "pense passo a passo",
   apelo emocional — tudo obsoleto nos modelos com raciocínio embutido. Quem
   ainda coleciona técnicas de prompt está otimizando o que deixou de importar.
2. **Colar arquivo no contexto virou ruim.** Com janela de 1 M e busca embutida,
   dar a **estratégia de busca** rende mais que despejar conteúdo.
3. **O portão virou o produto.** Ferramentas competem em qualidade de
   verificação, não só de geração.
4. **Custo migrou de por-assinatura para híbrido.** GitHub Copilot passou a
   cobrança baseada em uso a partir de 01/06/2026 (créditos de IA, 1 crédito =
   US$ 0,01). Cursor documenta que usuários diários de agente ficam mais perto de
   US$ 60–100/mês que dos US$ 20 do plano base. **Orçamento por assinatura
   deixou de prever o gasto.**
5. **Segurança de agente virou disciplina própria.** CVEs com CVSS acima de 9,
   pesquisa de RCE em frameworks de agente, injeção indireta com casos
   confirmados em todos os agentes principais.

---

## 7 · Fronteiras de pesquisa

| Frente | Pergunta em aberto |
|---|---|
| **Defesa contra injeção de prompt** | Existe separação arquitetural entre instrução e dado? Propostas de canais separados e de arquiteturas dual-LLM ainda não são padrão |
| **Verificação formal assistida** | Modelos gerando prova (Lean, Dafny, F*) junto com código. Promissor e restrito a domínios pequenos |
| **Memória entre sessões** | Como acumular conhecimento sem inchar contexto |
| **Avaliação de trabalho real** | Benchmarks saturam e não medem o que importa. E, como a METR mostrou, o experimento randomizado está ficando inviável |
| **Erros correlacionados** | Se todos usam modelos parecidos, os bugs ficam parecidos. Monocultura de software |
| **Manutenção de código gerado em escala** | O que acontece com uma base de 5 anos majoritariamente gerada? Ninguém tem dado ainda |

> **A última linha é a que eu mais gostaria de ver respondida.** Estamos no
> quinto ano de código gerado em produção e o primeiro grande ciclo de
> manutenção ainda não chegou. O sinal de alerta do GitClear sugere que a conta
> virá — mas ninguém sabe o tamanho.

---

## 8 · Previsões — marcadas como especulação

Assino, com prazo, para poder ser cobrado depois:

| Até | Previsão | Confiança |
|---|---|---|
| 2027 | "AI-assisted" some do título de vaga; vira o padrão | alta |
| 2027 | Verificação automática de PR (não geração) vira o campo de batalha comercial | média-alta |
| 2028 | Um incidente público relevante causado por dependência alucinada | média |
| 2028 | Métrica de "cobertura do diff" mais comum que "cobertura total" | média |
| 2029 | Primeiro grande relato de manutenção de base majoritariamente gerada — e não será elogioso | média |
| — | **Especificar e verificar continuam sendo trabalho humano** | alta |

---

## Fontes consultadas

Todas em **20/08/2026**:

- METR — horizontes: https://metr.org/time-horizons/ e o conjunto
  `benchmark_results_1_1.yaml`
- METR — mudança de desenho experimental: https://metr.org/blog/2026-02-24-uplift-update/
- DORA 2025: https://dora.dev/dora-report-2025/ · ROI 2026 (InfoQ):
  https://www.infoq.com/news/2026/05/dora-roi-ai-assisted-dev-report/
- LinearB 2026 Benchmarks: https://linearb.io/resources/software-engineering-benchmarks-report
- GitClear — *The Maintainability Gap*: https://www.gitclear.com/the_ai_code_quality_maintainability_gap
- Stack Overflow — *Closing the developer AI trust gap*: https://stackoverflow.blog/2026/02/18/closing-the-developer-ai-trust-gap/
- AGENTS.md: https://agents.md/
- GitHub Spec Kit: https://github.com/github/spec-kit
- Microsoft Security — RCE em frameworks de agente:
  https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks/
- Preços: https://claude.com/pricing · https://github.com/features/copilot/plans ·
  https://cursor.com/pricing · https://platform.claude.com/docs/en/about-claude/pricing

---

## Autoteste

1. Qual é o horizonte temporal de 50% do modelo líder e como se lê esse número?
2. Por que não se deve citar número de benchmark de site agregador? Qual é a
   alternativa mais útil?
3. Qual pergunta o SDD ainda não respondeu, e que precedente histórico ela ecoa?
4. Cite quatro pontos que viraram consenso em 2026.
5. Cite três debates ainda em disputa e a leitura de cada lado.
6. Cite as cinco mudanças silenciosas desde 2025 e a consequência prática de cada.
7. Por que o modelo de custo mudou e o que isso significa para o seu orçamento?
8. Qual é a fronteira de pesquisa que este curso considera mais importante e por
   quê?
9. Qual novidade de tokenização confunde a comparação de custo entre gerações?
10. Escolha duas previsões do §8 e argumente contra elas.

---

**Anterior:** [60-teoria-avancada](60-teoria-avancada.md) ·
**Próximo:** [70-pratica](70-pratica.md)
