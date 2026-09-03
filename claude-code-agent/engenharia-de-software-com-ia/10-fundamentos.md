# 10 · Fundamentos — o que exatamente mudou no ofício

**Nível:** intermediário · **Escrito em:** 20/08/2026

---

## A tese, enunciada de uma vez

> **A geração de código deixou de ser o gargalo. A verificação passou a ser.**
> E verificação humana não escala — só verificação automática escala.
> Portanto: **um dev que sabe usar IA é aquele que converte julgamento humano
> em verificação automática mais rápido do que a máquina produz trabalho.**

Tudo neste curso é consequência disso. Vale destrinchar cada parte.

---

## 1 · Por que a geração deixou de ser o gargalo

Não é opinião: é o que a curva de capacidade mostra.

A METR (Model Evaluation & Threat Research) mede uma grandeza chamada
**horizonte temporal**: a duração da tarefa que um modelo completa com 50% de
sucesso, medida em quanto tempo um engenheiro competente levaria.

Dados do próprio conjunto publicado pela METR (arquivo
`benchmark_results_1_1.yaml`, versão 1.1, consultado em 20/08/2026), em minutos:

| Modelo | Lançamento | Horizonte 50% |
|---|---|---|
| GPT-4 | 14/03/2023 | ~4 min |
| GPT-4o | 13/05/2024 | ~7 min |
| Claude 3.5 Sonnet (out/2024) | 22/10/2024 | ~21 min |
| o1 | 05/12/2024 | ~39 min |
| Claude 3.7 Sonnet | 24/02/2025 | ~60 min |
| o3 | 16/04/2025 | ~2 h |
| Claude Opus 4 / 4.1 | 05/2025 · 08/2025 | ~1 h 40 min |
| GPT-5 | 07/08/2025 | ~3 h 23 min |
| Claude Opus 4.5 | 24/11/2025 | ~4 h 53 min |
| Gemini 3 Pro | 18/11/2025 | ~3 h 44 min |
| GPT-5.2 | 11/12/2025 | ~5 h 52 min |
| Claude Opus 4.6 | 05/02/2026 | ~12 h |
| Gemini 3.1 Pro | 19/02/2026 | ~6 h 24 min |
| GPT-5.4 | 05/03/2026 | ~5 h 42 min |

A METR estima que, de 2019 a 2023, esse horizonte **dobrava a cada ~7 meses**;
depois de 2023, o intervalo comprimiu para **~130,8 dias (4,3 meses)**.

### O que esse número quer dizer, e o que não quer

**Quer dizer:** a fatia de tarefa que a máquina consegue levar até o fim sozinha
cresce exponencialmente. Em 2023, ela mal terminava um exercício de 5 minutos.
Em 2026, ela termina metade das tarefas de um dia de trabalho.

**Não quer dizer** que ela substituiu ninguém. Repare no "50%". Um sistema que
acerta metade das tarefas de meio dia é um sistema que **erra metade das tarefas
de meio dia** — e você não sabe qual metade sem verificar.

**É exatamente isso que empurra o trabalho para a verificação.** Quanto maior o
lote que a máquina produz e quanto mais confiável ela *parece*, mais caro fica
descobrir qual metade está errada.

> **Isenção necessária:** o horizonte é medido numa suíte específica de tarefas
> de software com critério automático de sucesso. Ele **não** mede trabalho com
> requisito ambíguo, com stakeholder humano, ou em código sem teste — que é a
> maior parte do trabalho real. Trate como indicador de tendência, não como
> previsão de emprego. A dissecação está em
> [24-produtividade](24-produtividade-o-que-diz-a-evidencia.md).

---

## 2 · Por que verificação humana não escala

Aritmética simples e implacável.

Suponha que você revise código a **200 linhas por hora** com atenção real —
número generoso; a literatura de revisão de código sugere que a taxa de detecção
de defeito despenca acima de ~300 linhas/hora.

| Cenário | Linhas produzidas/dia | Horas de revisão necessárias |
|---|---|---|
| Você sozinho, sem IA | ~150 | 0,75 h |
| Você com IA, delegando | ~1.200 | **6 h** |
| Você com 3 agentes | ~3.600 | **18 h** |

O dia continua tendo 8 horas. **A partir de um certo ponto, a única saída é
deixar de revisar** — e é exatamente isso que acontece, silenciosamente, em
milhares de equipes.

Os números de campo confirmam:

- PRs assistidos por IA são **2,6× maiores** no percentil 75 (408 vs. 157 linhas).
- PRs de agente esperam **5,3× mais** para alguém começar a revisar
  (1.055 vs. 201 minutos).
- Apenas **32,7%** do código de IA passa na revisão sem modificação, contra
  84,4% do código humano.
- O tempo de revisão subiu **91%** em equipes com adoção intensa.

*(LinearB, 2026 Software Engineering Benchmarks Report — 8,1 milhões de PRs,
4.800 organizações, 42 países.)*

### O que escala

| Mecanismo | Escala? | Custo marginal |
|---|---|---|
| Você lendo o diff | Não | Seu tempo, linearmente |
| Outro humano revisando | Não | O tempo dele, linearmente |
| Outra IA revisando | Parcialmente | Barato, mas correlacionado — erra parecido |
| **Teste automatizado** | **Sim** | ~zero |
| **Tipo estático** | **Sim** | ~zero |
| **Linter e análise estática** | **Sim** | ~zero |
| **Portão determinístico** | **Sim** | ~zero |

A linha "outra IA revisando" merece atenção: uma segunda IA **não** é
independente da primeira. Elas foram treinadas nos mesmos dados e erram de forma
correlacionada. Isso é útil como filtro barato de primeira passada — e é
perigoso como substituto de verificação, porque produz a sensação de duas
opiniões quando há uma e meia.

---

## 3 · O que é "converter julgamento em verificação"

É a habilidade central. Vale exemplificar em concreto.

| Julgamento (na sua cabeça) | Verificação (executável) |
|---|---|
| "esse valor nunca pode ser negativo" | `assert` / tipo `PositiveInt` / `CHECK (valor > 0)` no banco |
| "a resposta tem que sair em menos de 300 ms" | teste de desempenho no CI |
| "essa função não pode fazer I/O" | teste que roda com a rede desligada |
| "não pode entrar dependência nova sem eu ver" | regra `pacotes` do [projeto-modelo](07-projeto-modelo/README.md) |
| "esse módulo não pode importar aquele" | teste de arquitetura (`import-linter`, ArchUnit) |
| "o comportamento não pode mudar nesta migração" | teste de caracterização ([exemplo 10](06-exemplos.md)) |
| "isso não pode vazar dado de outro cliente" | teste com dois inquilinos e asserção cruzada |

Cada linha da esquerda é conhecimento que hoje mora só na sua cabeça, e que
**morre quando você sai de férias**. Cada linha da direita é o mesmo
conhecimento numa forma que a máquina consegue aplicar 1.000 vezes por dia, de
graça, inclusive contra um agente.

> **Reformulação da tese, e talvez a frase mais útil deste curso:**
> escrever verificação não é burocracia — é **externalizar o seu julgamento**.
> Antes da IA, isso era higiene. Depois da IA, é a condição para ter alavancagem.

---

## 4 · Vocabulário — defina antes de usar

Termos que aparecem no resto do material. O glossário completo está em
[GLOSSARIO](GLOSSARIO.md).

| Termo | Definição |
|---|---|
| **LLM** (*large language model*) | Modelo estatístico que prediz o próximo *token* dado o texto anterior. É o motor de tudo aqui |
| **Token** | Pedaço de texto (~4 caracteres em inglês, menos em português). A unidade de cobrança e de limite |
| **Janela de contexto** | Quantidade máxima de tokens que o modelo enxerga de uma vez. Tudo fora dela simplesmente não existe para ele |
| **Prompt** | Tudo que entra no modelo antes de ele responder |
| **Alucinação** | Saída plausível e falsa. Não é bug; é o comportamento normal de um preditor quando o provável diverge do verdadeiro |
| **Agente** | LLM num laço: pensa → usa ferramenta → lê resultado → repete |
| **Ferramenta** (*tool*) | Função que o agente pode chamar: ler arquivo, rodar comando, buscar na web |
| **Laço agêntico** | O ciclo acima. Dissecado no [15](15-o-loop-do-agente.md) |
| **Contexto** | O que está na janela naquele instante: instruções, arquivos, histórico, resultados de ferramenta |
| **Vibe coding** | Programar por conversa, sem ler o código gerado. Karpathy, fev/2025; palavra do ano do Collins em 2025 |
| **Spec-driven development (SDD)** | Método em que a especificação é o artefato primário e o código é saída regenerável |
| **Slopsquatting** | Ataque que registra nomes de pacote que os modelos alucinam |
| **Injeção de prompt** | Fazer o modelo obedecer instrução vinda do conteúdo que ele processa, e não de você |
| **Portão** (*gate*) | Verificação determinística que decide se uma mudança entra |
| **Horizonte temporal** | Duração de tarefa que o modelo completa com dada taxa de sucesso |

---

## 5 · Os quatro modelos mentais que funcionam

Modelo mental é ferramenta de previsão: serve para você antecipar o
comportamento sem ter que testar tudo. Estes quatro cobrem a maior parte dos
casos.

### Modelo 1 — O estagiário genial e amnésico

Sabe tudo que já foi escrito, esquece tudo entre tarefas, nunca diz "não sei",
nunca pergunta, faz exatamente o que você escreveu.

**Prevê bem:** por que instrução precisa ser explícita; por que ele não pergunta
quando devia; por que a mesma explicação precisa ser repetida a cada sessão.

**Prevê mal:** ele não "aprende" com a correção de ontem. Não há relação de
aprendizado; há um arquivo que você mantém.

### Modelo 2 — Interpolador estatístico

Ele interpola entre padrões que viu. Onde há muito exemplo, o resultado é
excelente. Onde há pouco, ele **extrapola** — e extrapolação de interpolador é
invenção.

**Prevê bem:** por que ele acerta um CRUD em Express e erra a sua regra de
negócio; por que ele acerta mais em Python e JavaScript que em COBOL ou no seu
DSL interno; por que ele inventa nome de pacote (o nome *parece* certo pelo
padrão dos nomes que existem).

**Prevê bem também:** por que ele às vezes sugere API que não existe — ela
*deveria* existir, pela regularidade das APIs que ele viu.

### Modelo 3 — O amplificador

Ele multiplica o que já existe na organização. Equipe com testes bons, deploy
confiável e arquitetura limpa fica muito mais rápida. Equipe com código
emaranhado, sem teste e com deploy manual fica **mais rápida em produzir
problema**.

Este não é meu palpite: é a conclusão central do relatório DORA de 2025 sobre
desenvolvimento assistido por IA (≈5.000 profissionais, 100+ horas de dados
qualitativos): a IA é **amplificadora** — magnifica as forças de organizações
saudáveis e as disfunções das doentes. O relatório de ROI de 2026 do mesmo grupo
reforça: o retorno vem do **sistema organizacional** (qualidade da plataforma
interna, clareza dos fluxos, alinhamento dos times), não da ferramenta.

**Prevê bem:** por que a mesma ferramenta produz relatos opostos em empresas
diferentes; por que "adotamos IA e piorou" é um diagnóstico sobre a empresa.

### Modelo 4 — A serraria (do [01](01-introducao-leigo.md))

Máquina rápida, gargalo migra para especificar, conferir e integrar.

**Prevê bem:** onde o seu tempo vai parar; por que automatizar só a geração
rende pouco.

---

## 6 · A regra de ouro, e por que ela é enunciada no negativo

> **Nunca delegue à IA aquilo que você não conseguiria avaliar.**

Formulada assim de propósito. A versão positiva ("delegue o que você sabe
avaliar") soa permissiva e não gera decisão. A negativa dá um teste imediato:
*se voltasse errado, eu perceberia?*

Corolários:

1. **Você pode delegar o que não sabe fazer**, desde que saiba julgar. Eu não
   escreveria uma expressão regular complexa de cabeça, mas sei escrever 20 casos
   de teste que a prendem. Delegar é seguro.
2. **Você não deve delegar o que não sabe julgar**, mesmo sabendo fazer devagar.
   Criptografia é o exemplo canônico: o código gerado *parece* certo, roda, passa
   nos testes — e é inseguro de um jeito que só quem é da área enxerga.
3. **Delegar pode ser a forma de aprender a julgar** — se você fizer as
   perguntas certas. "Por que assim e não assado?" ensina. "Escreve pra mim" não.

### A pergunta operacional

Antes de mandar qualquer coisa:

> **"Se isso voltar sutilmente errado, eu percebo? Como?"**

Três respostas possíveis:

| Resposta | O que fazer |
|---|---|
| "Percebo, porque o teste X pega" | Delegue à vontade |
| "Percebo lendo, se o diff for pequeno" | Delegue com escopo estreito |
| "Não percebo" | **Não delegue** — ou construa a verificação primeiro |

A terceira linha é onde mora o trabalho de verdade. "Construa a verificação
primeiro" é o curso inteiro em quatro palavras.

---

## 7 · O que **não** mudou

Lista curta e importante, porque o barulho do mercado sugere que tudo mudou.

- **Sistemas continuam sendo difíceis pelas mesmas razões.** Estado
  compartilhado, concorrência, acoplamento, requisito ambíguo, coordenação
  humana. Nenhuma dessas é um problema de digitação.
- **Continua sendo mais barato não construir.** A funcionalidade que não existe
  não tem bug, não precisa de manutenção e não confunde o usuário. A IA baratear
  a construção **aumenta** a tentação de construir demais — e o desperdício é
  agora mais barato de produzir e igualmente caro de manter.
- **Responsabilidade continua sendo humana.** Nenhum contrato, nenhum regulador
  e nenhum cliente aceita "o agente escreveu". Você assina o commit.
- **Entender continua sendo o trabalho.** Se ninguém entende o sistema, não
  importa quão rápido ele foi escrito.
- **O custo total é dominado pela manutenção.** Estimativas clássicas de
  engenharia de software colocam 60–80% do custo de vida de um sistema depois da
  primeira entrega. Acelerar a fatia de 20–40% e piorar a de 60–80% é um mau
  negócio — e a duplicação de blocos subindo 81% desde 2023 (GitClear) sugere
  que é isso que está acontecendo em média.

---

## 8 · Os cinco porquês, aplicados à tese

**Por que a verificação virou o gargalo?**
Porque a geração ficou barata e rápida.

**Por que a geração ficou barata?**
Porque modelos treinados em praticamente todo o código aberto do mundo
interpolam bem entre padrões conhecidos, e a maior parte do código escrito
diariamente é padrão conhecido.

**Por que a maior parte do código é padrão conhecido?**
Porque software é feito de camadas repetidas: rota HTTP, validação, acesso a
banco, serialização, teste. A parte genuinamente nova de qualquer sistema é
pequena — a regra de negócio. O resto é a mesma coisa em roupas diferentes.

**Por que a parte nova é pequena e mesmo assim tudo é difícil?**
Porque a dificuldade não está no volume de código, está na **interação** entre
as partes. Fred Brooks separou isso em 1986 (*No Silver Bullet*) como
**complexidade essencial** (inerente ao problema) e **acidental** (do
ferramental). A IA ataca a acidental com força; a essencial ela não toca,
porque a complexidade essencial *é* a especificação — e especificar continua
sendo o trabalho humano.

**Por que a complexidade essencial não pode ser automatizada?**
Porque ela consiste em decidir **o que o sistema deve fazer**, e isso depende de
objetivos, restrições e trade-offs que existem fora do sistema — no negócio, na
lei, nas pessoas. Uma máquina pode ajudar a explorar o espaço de opções, mas
escolher requer alguém que **responda pela escolha**. Essa é a parada legítima:
não é limitação técnica, é a natureza da decisão sob responsabilidade.

---

## Autoteste

1. Enuncie a tese central do curso em uma frase.
2. O horizonte temporal de 50% da METR estava em ~4 minutos em 2023 e em ~12
   horas em fev/2026. O que isso significa e o que **não** significa?
3. Faça a conta: a 200 linhas/hora de revisão atenta, quantas horas custa revisar
   a produção de três agentes? Qual é a conclusão prática?
4. Por que uma segunda IA revisando não é verificação independente?
5. Dê três exemplos de "converter julgamento em verificação" que não estejam na
   tabela do texto.
6. Explique os quatro modelos mentais e diga o que cada um prevê bem.
7. Por que a regra de ouro é enunciada no negativo?
8. Você sabe escrever criptografia, mas devagar. Deve delegar? Por quê?
9. Qual é a pergunta operacional antes de delegar, e o que fazer em cada uma das
   três respostas possíveis?
10. Segundo Brooks, qual é a diferença entre complexidade essencial e acidental?
    Qual delas a IA ataca, e por que a outra não é automatizável?

---

**Anterior:** [07-projeto-modelo](07-projeto-modelo/README.md) ·
**Próximo:** [11-historia](11-historia.md)
