# Glossário — engenharia de prompt

Todo termo técnico usado no curso. Termos em inglês aparecem como o campo os
usa, com a tradução ao lado. Ordem alfabética.

---

**Ablação** — remover uma parte do prompt e medir o efeito. Serve para
descobrir o que é peso morto. Ver [12 §12.10](12-anatomia-de-um-prompt.md).

**Agente** — sistema em que o modelo decide, em laço, quais ferramentas chamar
até concluir uma tarefa. Distingue-se do *workflow*, em que os passos são
fixos. Ver [25](25-ferramentas-e-agentes.md).

**Alucinação** — saída factualmente errada apresentada com confiança. Não é
defeito acidental: é o funcionamento normal aplicado a um caso sem base. Ver
[10 §10.8](10-fundamentos.md).

**Amostragem** (*sampling*) — como se escolhe o próximo token a partir da
distribuição de probabilidade. Gulosa, temperatura, top-p, top-k.

**Aprendizado em contexto** (*in-context learning*) — a capacidade de executar
uma tarefa a partir de exemplos no prompt, **sem** atualizar pesos.

**Arnês** (*harness*) — o sistema em volta do modelo: ferramentas, políticas,
validadores, avaliadores, limites. O objeto de trabalho de 2026.

**Atenção** (*attention*) — mecanismo pelo qual cada token gerado pondera todos
os anteriores. Base do Transformer.

**Autoconsistência** (*self-consistency*) — gerar N respostas e votar na mais
frequente. Cara; ver [13 §13.4](13-tecnicas-nucleo.md).

**Autocrítica** — pedir ao modelo que critique e corrija a própria saída. Útil
com critério objetivo; enganosa sem ele.

**Avaliação** (*eval*) — o conjunto rotulado mais o programa que mede o
desempenho sobre ele. O ativo central da profissão. Ver
[20](20-avaliacao-e-evals.md).

**BM25** — algoritmo clássico de busca por palavras (léxica). Bom em termo
exato; ruim em paráfrase.

**Cabeça de indução** (*induction head*) — circuito observado em transformers
que implementa "vi `A B` antes; depois de `A`, preveja `B`". Evidência
mecanicista do aprendizado em contexto.

**Cache de prompt** — reaproveitamento do processamento de um **prefixo**
idêntico entre chamadas. Reduz custo e latência. Ver
[30 §30.3](30-custo-latencia-caching.md).

**Cadeia de pensamento** (*chain-of-thought*, CoT) — gerar passos intermediários
antes da resposta. Aumenta a computação disponível por resposta. Ver
[60 §60.2](60-teoria-avancada.md).

**Calibração** — grau em que a confiança declarada corresponde ao acerto real.
Confiança verbalizada é mal calibrada.

**Cascata** (de modelos) — modelo barato resolve o fácil e escala o duvidoso
para o caro. Ver [06, exemplo 11](06-exemplos.md).

**Compactação** (*compaction*) — resumir o histórico antigo para caber na
janela. Destrói o cache; perde detalhe.

**Conjunto de desenvolvimento / de validação** — o primeiro você olha centenas
de vezes; o segundo, raramente. Separá-los evita medir o quanto você decorou.

**Contexto** — tudo que entra na chamada: instrução, histórico, documentos,
ferramentas.

**Decodificação restrita** (*constrained decoding*) — impedir, no nível da
geração, tokens que violariam um esquema. É o que dá **garantia** de formato.

**Delimitação** — separar dado de instrução com marcadores nomeados
(`<documento>…</documento>`).

**Deriva** (*drift*) — mudança da distribuição real das entradas com o tempo,
que faz o conjunto de avaliação envelhecer.

**DSPy** — framework que trata prompt como programa compilável, com
otimizadores. Versão 3.3.0 em 19/08/2026.

**Embedding** — vetor numérico que representa o sentido de um texto. Base da
busca densa.

**Encadeamento** (*prompt chaining*) — dividir a tarefa em várias chamadas
sequenciais, cada uma com um objetivo.

**Engenharia de contexto** — a disciplina de decidir **o que entra na janela**.
Deslocou a redação como problema central em 2025.

**Escalonamento** (*escalation*) — devolver o caso a um humano. Métrica
operacional valiosa.

**Esforço** (*effort*) — parâmetro que controla profundidade de raciocínio e
gasto de tokens (`low` … `max`).

**Esquema** (*schema*) — descrição formal da estrutura de saída (JSON Schema).
As descrições dos campos **são prompt**.

**Exfiltração** — fazer o sistema enviar dado privado para fora. Ver
[35](35-seguranca-e-injecao.md).

**Few-shot** — prompt com exemplos. **Zero-shot**: sem exemplos.

**Ferramenta** (*tool*) — função que você descreve ao modelo; ele pede a
chamada, **você** executa.

**Fidelidade** (*faithfulness*) — grau em que a resposta se apoia nos trechos
fornecidos, e não em conhecimento externo.

**Fronteira de Pareto** — conjunto de soluções em que não se melhora um
objetivo (acerto) sem piorar outro (custo). Entregável mais útil da otimização.

**GEPA** — otimizador de prompt por evolução reflexiva com fronteira de Pareto.
arXiv:2507.19457; ICLR 2026 (oral).

**Injeção de prompt** — instrução maliciosa inserida no que o modelo lê.
**Direta**: pelo usuário. **Indireta**: por conteúdo que o sistema lê. Não tem
solução por prompt.

**Instrução de sistema** (*system prompt*) — canal do operador: papel, regras,
formato. Não guarde segredo nele.

**Jailbreak** — contornar as políticas de segurança do modelo.

**Janela de contexto** — total de tokens que cabem numa chamada.

**JSON Schema** — linguagem para descrever a estrutura de um JSON. Ver
[14](14-saida-estruturada.md).

**Juiz** (*LLM-as-a-judge*) — usar um modelo para avaliar saídas. Precisa de
rubrica e de **calibração contra humano**.

**Latência** — tempo de resposta. **TTFT**: até o primeiro token. **Total**: até
o fim.

**Lote** (*batch*) — processamento assíncrono com desconto (~50%).

**Menor privilégio** — dar à ferramenta só a permissão indispensável. Defesa
que funciona mesmo com o modelo enganado.

**Metaprompting** — usar um modelo para escrever ou melhorar o prompt de outro.

**MIPROv2** — otimizador do DSPy que escolhe exemplos e reescreve instruções.

**Modelo de linguagem** (LLM) — sistema que prevê o próximo token de uma
sequência. Todo o resto é emergente disso.

**p95** — o valor abaixo do qual estão 95% das observações. Em custo e latência
de agente, é a cauda que quebra o orçamento.

**Papel** (*role*) — declaração de quem o modelo é na tarefa. Funcional ajuda;
inflacionário, não.

**Perdido no meio** (*lost in the middle*) — informação no miolo de um contexto
longo é recuperada com menos confiabilidade.

**Pensamento estendido** (*extended thinking*) — raciocínio interno do modelo
antes da resposta, nativo nos modelos de 2025–2026.

**Prefill** — iniciar a resposta do assistente para forçar formato. **Removido**
nos modelos Claude 4.6+ (erro 400).

**Prefixo** — o começo da requisição. O cache casa por prefixo **exato**.

**Preâmbulo** — "Claro! Aqui está…". Suprimir é instrução explícita.

**Priming de formato** — terminar o prompt com o início da estrutura esperada
(`saida:`). Diferente de prefill; continua válido.

**Prompt** — tudo que entra no modelo antes da resposta.

**promptfoo** — ferramenta aberta (MIT) de avaliação declarativa e red teaming.
Adquirida pela OpenAI em 09/03/2026.

**RAG** (*Retrieval-Augmented Generation*) — recuperar trechos relevantes e
colocá-los no contexto, em vez de despejar a base inteira.

**Recall@k** — proporção de perguntas cujo trecho correto está entre os k
recuperados. Teto do desempenho de um RAG.

**Recência** — o que está perto do fim do prompt pesa mais.

**Red team** — testar o próprio sistema como adversário.

**Reranking** (reordenação) — um segundo modelo reordena os candidatos
recuperados, aumentando a precisão.

**RLHF** — ajuste por preferência humana. Origem da obediência a instrução — e
dos vieses de prolixidade, cordialidade e bajulação.

**Rubrica** — escala curta com âncoras textuais por ponto. Reduz a variância do
juiz.

**Saída estruturada** — recurso de API que garante conformidade da saída a um
esquema.

**Sintaxe × semântica** — a saída estruturada garante a primeira, nunca a
segunda. Valide sempre.

**Superajuste** (*overfitting*) — o prompt resolve o **seu conjunto**, não o
problema.

**Temperatura** — parâmetro de aleatoriedade da amostragem. Removido nos
modelos Claude mais novos. `0` **não** dá determinismo.

**Token** — unidade que o modelo enxerga; pedaço de texto de tamanho
variável. Português custa mais tokens que inglês.

**Tokenizador** — algoritmo que converte texto em tokens.

**Trinca letal** — dado privado + conteúdo não confiável + comunicação externa.
Com os três juntos, há risco de exfiltração. Ver
[35 §35.3](35-seguranca-e-injecao.md).

**Truncamento** — saída cortada por `max_tokens` insuficiente. Causa nº 1 de
JSON quebrado.

**Transformer** — arquitetura de rede neural baseada em atenção (2017).

**Validação** — verificar programaticamente a saída: parse, esquema, semântica
de negócio, referências.

**Workflow** — sequência **fixa** de chamadas, definida por código. Frequentemente
melhor que agente.

**Zero-shot** — prompt sem exemplos.
