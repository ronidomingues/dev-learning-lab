# 70 · Prática — 12 laboratórios progressivos

`Nível: iniciante → avançado` · `Última atualização: 12/08/2026`

Exercícios com objetivo, critério de sucesso e dica. **Faça na ordem** — cada um depende do
anterior. Todos rodam em CPU, exceto onde indicado.

Como usar: tente sozinho primeiro. A solução de referência está sempre indicada por link,
mas ler a solução antes de tentar é o jeito mais eficiente de não aprender nada.

---

## Nível 1 · Primeiros passos

### Lab 1 — Sondando o que o modelo sabe
**Tempo:** 30 min · **Pré-requisito:** [04](04-como-comecar.md)

Use `fill-mask` para investigar o conhecimento do BERTimbau. Monte 20 frases que testem:
5 de conhecimento factual (capitais, datas, empresas), 5 de gramática (concordância de gênero
e número), 5 de desambiguação por contexto, 5 de viés social (profissões, gênero, região).

**Critério de sucesso:** você consegue apontar uma frase em que ele acerta com >90% de
confiança e uma em que erra com confiança alta, e explicar por quê.

**Dica:** teste "A [MASK] operou o paciente" e "O [MASK] cuidou das crianças". Anote as
respostas — elas voltam no Lab 11.

---

### Lab 2 — Autópsia do tokenizador
**Tempo:** 30 min · **Pré-requisito:** [12](12-tokenizacao-wordpiece.md)

Compare quatro tokenizadores (BERTimbau, DistilBERT multilíngue, XLM-R, ModernBERT) sobre 30
termos do **seu** domínio profissional. Calcule a fertilidade (tokens por palavra) de cada um.

**Critério de sucesso:** uma tabela ordenada por fertilidade e uma conclusão sobre qual modelo
lida melhor com o seu vocabulário.

**Dica:** inclua siglas, nomes próprios e termos com hífen — é onde as diferenças aparecem.

---

### Lab 3 — Medindo a distância entre significados
**Tempo:** 45 min · **Pré-requisito:** [04](04-como-comecar.md), [16](16-embeddings-e-busca-semantica.md)

Monte 10 pares de frases: 5 pares de paráfrases e 5 pares sem relação. Calcule a similaridade
com três métodos: `[CLS]` cru, mean pooling, e um modelo `sentence-transformers`.

**Critério de sucesso:** uma tabela mostrando a **separação média** (média dos pares
similares menos média dos dissimilares) de cada método, e a conclusão de qual usar.

**Dica:** a separação importa, não o valor absoluto. Ver
[16, seção 2](16-embeddings-e-busca-semantica.md#2--do-bert-cru-ao-sentence-bert).

---

## Nível 2 · Treinando

### Lab 4 — Seu primeiro classificador, com dados seus
**Tempo:** 2 h · **Pré-requisito:** [15](15-fine-tuning.md), [07-projeto-modelo](07-projeto-modelo/README.md)

Colete 200 exemplos rotulados de algo do seu trabalho (e-mails por assunto, produtos por
categoria, comentários por sentimento) e afine um BERTimbau. Use a estrutura do projeto-modelo.

**Critério de sucesso:** F1 macro no teste **acima do baseline TF-IDF + regressão logística**,
com matriz de confusão inspecionada.

**Dica:** se não bater o baseline, o problema quase certamente são os dados — rótulos
inconsistentes ou classes mal definidas.

---

### Lab 5 — A curva de dados
**Tempo:** 1,5 h · **Pré-requisito:** Lab 4

Treine o mesmo modelo com 25, 50, 100, 200 e todos os exemplos por classe. Trace a curva
F1 × quantidade de dados. Rode **3 sementes** por ponto e plote média ± desvio.

**Critério de sucesso:** um gráfico com barras de erro e uma resposta quantitativa a
"quantos exemplos a mais eu preciso para ganhar 5 pontos?".

**Dica:** este é o laboratório que mais muda a forma de trabalhar. Ele te ensina a estimar se
vale a pena rotular mais — a decisão de projeto mais frequente da área.

---

### Lab 6 — Caçando o vazamento
**Tempo:** 1 h · **Pré-requisito:** [18](18-avaliacao-e-benchmarks.md)

Introduza de propósito três vazamentos no Lab 4: (a) duplique 20% dos exemplos de treino no
teste; (b) inclua no texto uma palavra que correlacione perfeitamente com o rótulo;
(c) divida sem estratificar, com classes desbalanceadas.

Meça a acurácia em cada caso e depois corrija.

**Critério de sucesso:** você consegue dizer quanto cada vazamento inflou o resultado, e
escrever um teste automatizado que detecta cada um.

---

### Lab 7 — Limiar e custo do erro
**Tempo:** 1 h · **Pré-requisito:** Lab 4, [18](18-avaliacao-e-benchmarks.md)

Defina um custo em reais para falso positivo e para falso negativo no seu caso (ex.: FP =
R$ 5 de revisão humana; FN = R$ 200 de cliente perdido). Trace o custo total em função do
limiar e escolha o ótimo.

**Critério de sucesso:** um gráfico custo × limiar, o limiar ótimo, e a diferença de custo
anual entre ele e o limiar padrão de 0,5.

**Dica:** o resultado costuma ser bem longe de 0,5, e a economia costuma surpreender.

---

## Nível 3 · Aplicações

### Lab 8 — Busca híbrida completa
**Tempo:** 3 h · **Pré-requisito:** [16](16-embeddings-e-busca-semantica.md)

Monte um buscador sobre 200 documentos seus (FAQ, artigos, manuais) com BM25 + bi-encoder +
reranker. Crie 30 consultas de teste e marque à mão o documento correto de cada uma.

Meça **Recall@1, Recall@5 e MRR** para: só BM25, só vetorial, híbrido, e híbrido + reranker.

**Critério de sucesso:** a tabela com as quatro configurações e uma decisão fundamentada sobre
qual usar, considerando latência.

**Dica:** o código de referência está em
[16, seção 5](16-embeddings-e-busca-semantica.md#5--código-completo-do-pipeline). O interessante
é o seu resultado, que provavelmente vai contrariar sua expectativa em pelo menos um ponto.

---

### Lab 9 — NER no seu domínio
**Tempo:** 3 h · **Pré-requisito:** [06, exemplo 9](06-exemplos.md#9--ner-próprio-com-rótulos-alinhados-a-subtokens)

Anote 100 frases com 3 tipos de entidade do seu domínio (produtos, códigos internos, órgãos).
Treine um `TokenClassification` com alinhamento correto de subtokens.

**Critério de sucesso:** F1 por entidade usando `seqeval` (métrica de span, não de token —
essa distinção importa) e uma análise dos erros de fronteira.

**Dica:** use a ferramenta de anotação `doccano` ou `Label Studio` — anotar NER em CSV à mão
é sofrimento desnecessário.

---

### Lab 10 — Otimização para produção
**Tempo:** 2 h · **Pré-requisito:** [19](19-producao-e-otimizacao.md)

Pegue seu modelo do Lab 4 e meça a latência p50/p95 em quatro configurações: PyTorch um a um;
PyTorch em lote 32; ONNX; ONNX int8. Meça também a F1 de cada uma.

**Critério de sucesso:** uma tabela latência × qualidade e uma recomendação com justificativa.
Verifique se a quantização degradou alguma classe específica.

**Dica:** meça com 200 requisições, descartando as 20 primeiras (aquecimento). Uma medição
única não vale nada.

---

## Nível 4 · Avançado

### Lab 11 — Auditoria de viés
**Tempo:** 2 h · **Pré-requisito:** [20](20-interpretabilidade-e-bertologia.md)

Construa um teste de invariância: pegue 50 frases do seu conjunto e crie variantes trocando
apenas nome (masculino/feminino), origem regional e marcadores socioeconômicos. A predição
deveria ser idêntica.

**Critério de sucesso:** a taxa de mudança de predição por tipo de troca, e um parágrafo de
model card descrevendo honestamente o que você encontrou.

**Dica:** encontre pelo menos um caso em que a predição muda. Se não encontrar, seu teste
provavelmente está fraco demais.

---

### Lab 12 — Destilação
**Tempo:** 4 h · **Pré-requisito:** [19](19-producao-e-otimizacao.md), GPU recomendada

Use seu modelo do Lab 4 como professor para treinar um aluno menor (`distilbert` ou um BERT de
4 camadas) sobre texto **não rotulado** do seu domínio, com a perda de destilação.

**Critério de sucesso:** aluno com pelo menos 2× menos latência e perda menor que 3 pontos de
F1. Compare com treinar o aluno diretamente nos rótulos originais — a destilação deve ganhar.

**Dica:** quanto mais texto não rotulado você tiver, menor a perda. Com pouco texto, a
destilação não mostra sua vantagem.

---

## Projeto final sugerido

Escolha **um** problema real do seu trabalho e leve do início ao fim:

1. Definir a tarefa e o custo do erro
2. Coletar e rotular dados (o mais demorado — reserve 60% do tempo)
3. Baseline burro
4. Afinar 2 ou 3 modelos candidatos
5. Avaliar com intervalo de confiança e matriz de confusão
6. Otimizar para o alvo de latência
7. Servir com API e health check
8. Escrever o model card
9. Instrumentar monitoramento de deriva

**Critério de sucesso:** outra pessoa consegue rodar seu projeto do zero seguindo o README, e
o model card responde honestamente "para que isto não serve".

---

## Autoteste

1. No Lab 5, por que rodar 3 sementes por ponto em vez de uma?
2. No Lab 6, qual dos três vazamentos infla mais o resultado, e por quê?
3. No Lab 7, por que o limiar ótimo raramente é 0,5?
4. No Lab 8, em que tipo de consulta o BM25 ganha do vetorial?
5. No Lab 9, qual a diferença entre F1 por token e F1 por span, e por que a segunda é a correta?
6. No Lab 10, por que descartar as primeiras medições?
7. No Lab 12, por que a destilação bate treinar o aluno direto nos rótulos?

---

*Anterior: [65-estado-da-arte.md](65-estado-da-arte.md) · Próximo: [75-armadilhas.md](75-armadilhas.md)*
