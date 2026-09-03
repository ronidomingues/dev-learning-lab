# Glossário

**Escrito em:** 20/08/2026

Todo termo técnico usado no curso, definido. Termos em inglês aparecem com a
tradução ou explicação quando é assim que o campo os usa.

---

## A

**ADR** (*Architecture Decision Record*) — Arquivo curto que registra uma decisão
de arquitetura e, principalmente, **por que** ela foi tomada. Formato proposto por
Michael Nygard em 2011. Ver [14](14-contexto-e-o-repositorio.md).

**Agente** — Modelo de linguagem preso num laço: pensa → usa uma ferramenta → lê
o resultado → repete, até concluir. Ver [15](15-o-loop-do-agente.md).

**`AGENTS.md`** — Formato aberto de instruções para agentes, na raiz do
repositório. Criado em agosto de 2025 (OpenAI, Google, Cursor, Factory,
Sourcegraph); doado à Agentic AI Foundation (Linux Foundation) em dezembro de
2025. 60.000+ projetos, 24 ferramentas.

**Alucinação** (*hallucination*) — Saída plausível e falsa. Não é bug: é o
comportamento normal de um preditor estatístico quando o mais provável diverge do
verdadeiro. Ver [12](12-o-modelo-por-dentro.md) e [60](60-teoria-avancada.md).

**Amostragem** (*sampling*) — Processo de escolher o próximo token a partir da
distribuição de probabilidade. Controlado por `temperature`, `top_p`, `top_k`.

**Amplificador** — Modelo mental da IA como algo que magnifica forças e
disfunções existentes na organização. Conclusão central do DORA 2025.

---

## B

**Batch API** — Processamento assíncrono de requisições, com desconto (50% na
Claude API). Ver [80](80-custos-e-licencas.md).

**Benchmark** — Conjunto padronizado de tarefas para comparar modelos.
SWE-bench, Terminal-Bench. **Advertência:** saturam, contaminam-se e não
representam o seu código.

---

## C

**Cache de prompt** — Reaproveitamento do estado interno de um prefixo já
processado. Um acerto custa 10% do preço de entrada. Casa por **prefixo exato**.

**Calibração** — Saber, antes de delegar, se a tarefa vai voltar boa. Constrói-se
por acumulação de casos, não por leitura. É o que separa L2 de L3.

**Codemod** — Transformação automatizada e determinística de código em massa.
Ferramentas: `sed`, `comby`, `ast-grep`, `jscodeshift`.

**Complexidade acidental** — A que vem das ferramentas e do ferramental. A IA
ataca esta. (Brooks, 1986.)

**Complexidade essencial** — A inerente ao problema: decidir o que o sistema deve
fazer. A IA não a toca. (Brooks, 1986.)

**Contexto** — O que está na janela do modelo naquele instante: instruções,
arquivos, histórico, resultados de ferramenta.

**Cobertura do diff** (*diff coverage*) — Fração das linhas **adicionadas por
esta mudança** que são exercidas por algum teste. Métrica muito melhor que
cobertura total. Ver [17](17-verificacao-e-testes.md).

**Cobertura de linha** — Fração das linhas executadas pelos testes. Mede
**execução**, não **verificação**. Não confunda com detecção.

---

## D

**Deriva de intenção** (*intent drift*) — Fenômeno em que o código produzido se
afasta progressivamente do que foi pedido. Motivação central do SDD.

**Diff** — Representação das diferenças entre duas versões de arquivos. A
**unidade de decisão** da revisão.

**Disjuntor** (*circuit breaker*) — Limite que interrompe um laço automatizado:
número de passos, tempo, falhas seguidas. Todo laço automatizado precisa de um.

**Duplicação de bloco** — Trecho repetido em mais de um lugar. Subiu 81% entre
2023 e 2026 (GitClear). O defeito estrutural característico da era dos agentes.

---

## E

**EARS** (*Easy Approach to Requirements Syntax*) — Cinco moldes de frase para
escrever requisitos sem ambiguidade (ubíquo, evento, estado, indesejado,
opcional). Origem em requisitos aeroespaciais. Ver [16](16-especificacao-e-plano.md).

**Entropia de Shannon** — Medida de aleatoriedade de uma sequência, em bits por
caractere. Usada para detectar segredo sem formato conhecido.

**Envenenamento de contexto** — Informação errada que entra cedo no contexto e
contamina todas as conclusões seguintes. Não há mecanismo de retratação.

**Especificação** — Descrição do que deve ser construído. Boa quando duas pessoas
competentes produzem implementações equivalentes e conseguem decidir se uma dada
implementação a satisfaz.

**Explosão de escopo** — O agente altera muito mais do que foi pedido.

---

## F

**Fadiga de alerta** (*alert fatigue*) — Quando há tantos avisos que as pessoas
param de ler. Modo de falha nº 1 de toda ferramenta de verificação automática.

**Ferramenta** (*tool*) — Função que o agente pode chamar: ler arquivo, escrever,
executar comando, buscar. **O programa executa, não o modelo.**

---

## G

**Goodhart, lei de** — "Quando uma medida vira alvo, ela deixa de ser boa
medida." (1975.) Operacionalmente crítica com agentes, que otimizam exatamente o
que foi medido, sem o bom senso de não desabilitar o teste.

**Golden test** — Ver *teste de caracterização*.

---

## H

**Headless** — Modo não interativo: o agente roda dentro de script ou CI, sem
humano presente.

**Horizonte temporal** (*time horizon*) — Duração de tarefa que um modelo
completa com dada taxa de sucesso (tipicamente 50%). Métrica da METR. Dobrou a
cada ~4,3 meses desde 2023.

---

## I

**Injeção de prompt** (*prompt injection*) — Fazer o modelo obedecer instruções
vindas do conteúdo processado, e não do usuário. **Direta:** o usuário injeta.
**Indireta:** o conteúdo lido injeta. Não tem solução no prompt.

**Isolamento** (*sandboxing*) — Restringir o que o agente pode alcançar:
container, *worktree*, permissões, rede.

---

## J

**Janela de contexto** — Número máximo de tokens que o modelo processa de uma
vez. 1 milhão nos modelos de ponta em 2026. **Fora da janela não existe.**

---

## L

**L0–L5** — Escala de níveis deste curso: recusa · autocompleta · conversa ·
delega com verificação · projeta o ambiente · opera em escala. Ver
[25](25-niveis-do-dev-com-ia.md).

**Laço agêntico** — O ciclo pensa → ferramenta → resultado → repete.

**Localidade de comportamento** — Quanto é preciso ler além de um trecho para
entender o que ele faz. Alta localidade = a mudança cabe no contexto.

**Lockfile** — Arquivo que trava versões exatas de dependências
(`package-lock.json`, `uv.lock`). Primeira defesa contra dependência alucinada.

**LLM** (*large language model*) — Modelo que prediz o próximo token dado o texto
anterior.

**Lost in the middle** — Efeito em que informação no meio de um contexto longo é
recuperada com menos confiabilidade que a do começo e a do fim. (Liu et al.,
2023.)

---

## M

**MCP** (*Model Context Protocol*) — Padrão aberto para conectar agentes a
sistemas externos. Cada servidor MCP é código de terceiro rodando com o seu
contexto — superfície de ataque.

**Modo 1–5** — Completar · conversar · editar · agir · assíncrono na nuvem. Ver
[13](13-os-quatro-modos-de-uso.md).

**MTok** — Milhão de tokens. Unidade de cobrança da API.

---

## P

**Portão** (*gate*) — Verificação determinística que decide se uma mudança entra.
Precisa ser rápido, determinístico, com mensagem acionável, com duas severidades
e **sem IA dentro**. Ver [17](17-verificacao-e-testes.md) e
[projeto-modelo](07-projeto-modelo/README.md).

**Prompt** — Tudo que entra no modelo antes de ele responder.

---

## R

**Raio de explosão** (*blast radius*) — Extensão do dano possível se algo der
errado. Autonomia total é aceitável quando o raio é finito.

**Rice, teorema de** (1953) — Toda propriedade não trivial e semântica de
programas é indecidível. Consequência: não existe verificador universal. Ver
[60](60-teoria-avancada.md).

**Round-trip engineering** — Manter modelo e código sincronizados nos dois
sentidos. Nunca foi resolvido; matou o MDA e é a pergunta em aberto do SDD.

---

## S

**SAST** (*Static Application Security Testing*) — Análise estática em busca de
vulnerabilidade. Semgrep, CodeQL, Bandit, gosec.

**SDD** (*Spec-Driven Development*) — Método em que a especificação é o artefato
primário e o código é saída regenerável. GitHub Spec Kit, AWS Kiro, OpenSpec.

**Severidade** — Classificação de um achado: **bloqueia** (reprova) ou **avisa**
(aparece e passa). A calibração é a decisão de projeto mais importante de um
portão.

**Slopsquatting** — Ataque que registra nomes de pacote que os modelos alucinam.
Termo cunhado por Seth Larson. ~20% das amostras geradas citam pacote
inexistente; 58% dos nomes se repetem.

**Subagente** — Agente delegado pelo agente principal, com contexto próprio.
Delegue **busca e verificação**, nunca decisão.

---

## T

**Teste de caracterização** (*characterization test*) — Teste que trava o
comportamento **atual**, sem julgar se está certo. Indispensável em migração.
(Michael Feathers, 2004.)

**Teste de contrato** — Verifica que produtor e consumidor de uma API concordam.

**Teste de mutação** — Sabota o código de propósito e verifica se a suíte
percebe. Mede **detecção**, não execução. A verificação da verificação.

**Teste de propriedade** (*property-based testing*) — Declara-se uma invariante
e a ferramenta gera centenas de entradas tentando quebrá-la. Combina
especialmente bem com código de IA, porque cobre o ponto cego dele: casos de
borda.

**Teste tautológico** — Teste que reproduz a fórmula do código. Passa sempre,
inclusive quando o código está errado. O padrão mais perigoso de teste gerado
por IA, porque parece completo.

**Token** — Pedaço de texto do vocabulário do modelo (~4 caracteres em inglês,
menos em português). Unidade de cobrança e de limite.

**Tokenizador** — O que converte texto em tokens. Modelos Claude 4.7+ usam um
tokenizador que gera ~30% mais tokens para o mesmo texto.

**Trinca letal** (*lethal trifecta*) — Conteúdo não confiável + acesso a dado
sensível + capacidade de comunicar para fora. As três juntas permitem
exfiltração; remova uma. Ver [22](22-seguranca.md).

---

## U

**Unified diff** — Formato textual padrão de diferença entre arquivos, produzido
por `git diff`.

---

## V

**Verificação** — Conjunto de mecanismos que decidem se algo está certo, do
compilador ao julgamento humano. **O gargalo do ofício em 2026.**

**Vibe coding** — Programar por conversa, aceitando tudo, sem ler o código.
Termo cunhado por Andrej Karpathy em fevereiro de 2025; palavra do ano do
dicionário Collins em novembro de 2025. Legítimo para código descartável;
irresponsável para código que alguém vai manter.

---

## W

**Worktree** — Segunda cópia de trabalho do mesmo repositório Git, em outra
pasta e outro branch, compartilhando o mesmo `.git`. A técnica mais
subestimada para trabalhar com agentes.

---

**Volta para:** [00-MAPA](00-MAPA.md)
