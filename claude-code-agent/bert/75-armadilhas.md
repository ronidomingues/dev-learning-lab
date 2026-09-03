# 75 · Armadilhas, mitos e más práticas

`Nível: todos` · `Última atualização: 12/08/2026`

Leia este arquivo **antes** de entregar qualquer coisa, mesmo com pressa. Cada item aqui
custou tempo, dinheiro ou credibilidade a alguém.

---

## Parte 1 · Mitos

### Mito 1 — "BERT é um LLM pequeno, dá para usar como ChatGPT"

Não. Ele não gera texto, e isso não é limitação de tamanho — é de arquitetura. Não existe
prompt, não existe instrução, não existe conversa. Ver
[01-introducao-leigo.md](01-introducao-leigo.md).

### Mito 2 — "BERT está obsoleto, use LLM para tudo"

Falso, e caro. Para classificação fechada em volume, encoders afinados batem LLMs em custo e
latência por **uma a duas ordens de grandeza**, com qualidade igual ou superior — medido em
literatura de 2026 ([65-estado-da-arte.md](65-estado-da-arte.md)). Quem manda 10 milhões de
classificações por dia para uma API de LLM está queimando dinheiro.

### Mito 3 — "Mais épocas = melhor modelo"

Não. Duas a quatro épocas é a receita padrão. Mais que isso costuma causar *overfitting* e,
paradoxalmente, deixa o modelo **mais confiante e não mais correto** — medido no
[projeto-modelo](07-projeto-modelo/README.md#experimentos-reais-deste-projeto-e-a-lição-que-vale-mais-que-o-código).

### Mito 4 — "Modelo maior é sempre melhor"

BERT-large custa 3× mais que o base e rende ~3%. ModernBERT-base ganha do BERT-large em
inglês, sendo menor. Escala não é o único eixo, e raramente é o mais eficiente.

### Mito 5 — "O modelo aprende sozinho com o uso"

Não aprende. Os pesos são congelados após o treino. Melhorar exige retreinar. Essa confusão
vem de sistemas que coletam feedback e retreinam periodicamente — o que é um **processo**, não
uma propriedade do modelo.

### Mito 6 — "Preciso de GPU para trabalhar com BERT"

Não para aprender, nem para inferência, nem para afinar conjuntos pequenos. O
[projeto-modelo](07-projeto-modelo/README.md) inteiro treina em 60 segundos numa CPU comum.

### Mito 7 — "Basta usar embeddings do BERT para busca semântica"

O BERT cru é ruim nisso — problema geométrico documentado (anisotropia). Use um modelo
treinado para similaridade. Ver [16](16-embeddings-e-busca-semantica.md).

### Mito 8 — "Meu modelo tem 95% de acurácia, está pronto"

95% em quê? Com quantos exemplos de teste? Que intervalo de confiança? Qual a distribuição das
classes? O que diz a matriz de confusão? Um número solto não é evidência de nada.

---

## Parte 2 · Erros de dados (os mais caros)

### Vazamento por duplicata

O mesmo texto em treino e teste. O modelo "acerta" porque decorou. Comum em bases reais, onde
chamados são copiados e e-mails são reencaminhados.

**Correção:** `drop_duplicates` antes de dividir, e um teste automatizado que falha se houver
duplicata ([testes/test_projeto.py](07-projeto-modelo/testes/test_projeto.py)).

### Vazamento temporal

Divisão aleatória em dado que tem tempo. O modelo treina com o futuro e é testado no passado.
Funciona lindamente no teste e falha em produção.

**Correção:** divida por data. Treine no passado, avalie no futuro.

### Vazamento de grupo

Vários textos do mesmo cliente, documento ou autor espalhados entre treino e teste. O modelo
aprende o estilo do autor, não a tarefa.

**Correção:** `GroupShuffleSplit` do scikit-learn, agrupando pelo identificador.

### Rótulos inconsistentes

Dois anotadores discordam em 30% dos casos. Nenhum modelo passa muito do teto de concordância
humana, e você vai perseguir décimos que são ruído.

**Correção:** meça a concordância (Cohen's kappa), refine o guia de anotação até ela subir, e
só então treine. Isso parece burocrático e é o passo com maior retorno em projetos reais.

### Desbalanceamento ignorado

95% de uma classe, acurácia de 95%, modelo que responde sempre a mesma coisa.

**Correção:** F1 macro, pesos na perda, e limiar ajustado.

### Dado de teste usado para decidir

Você olha o teste, ajusta hiperparâmetros, olha de novo. O teste virou validação e o número
final é otimista.

**Correção:** o teste é aberto uma vez. Se você abriu, ele queimou — arrume outro.

---

## Parte 3 · Erros de modelagem

### Escolher a classe errada

`SequenceClassification` para NER não funciona: você precisa de um rótulo por token.
Ver a tabela em [05-manual-de-uso.md](05-manual-de-uso.md#1--escolher-a-classe-certa).

### Não alinhar rótulos com subtokens em NER

O bug nº 1 de quem treina NER. A perda cai, o modelo treina, e as previsões saem deslocadas.
Ver [06, exemplo 9](06-exemplos.md#9--ner-próprio-com-rótulos-alinhados-a-subtokens).

### Esquecer `model.eval()`

Dropout ativo na inferência: a mesma frase devolve respostas diferentes. Sintoma reportado
como "o modelo está instável".

### Esquecer a `attention_mask`

O modelo presta atenção nos tokens de padding. Não dá erro; só piora a qualidade em silêncio.

### Tokenizador de um modelo com pesos de outro

Os ids não significam nada no outro vocabulário. Resultado: lixo com aparência de
funcionamento. **Sempre carregue os dois do mesmo repositório.**

### Truncar sem perceber

`max_length=128` num texto de 800 tokens joga fora 85% do conteúdo — silenciosamente.
Verifique a distribuição de comprimentos antes de escolher.

### Confiar no `[CLS]` sem afinar

O vetor do `[CLS]` de um modelo não afinado não é um bom resumo da frase.

---

## Parte 4 · Erros de avaliação e comunicação

### Reportar a melhor semente

Rodar 5 vezes e reportar o melhor resultado é seleção de ruído. Reporte média ± desvio.

### Trocar a métrica depois de ver o resultado

Auto-engano que quase ninguém percebe estar cometendo. Defina a métrica antes.

### Ignorar a matriz de confusão

O agregado esconde exatamente a informação acionável.

### Comparar com baseline mal ajustado

"Meu BERT bate o TF-IDF" — com o TF-IDF em configuração padrão e o BERT ajustado por três
dias. Esse é o pecado que o RoBERTa expôs no próprio campo
([11-historia.md](11-historia.md)).

### Não ter baseline nenhum

Sem TF-IDF + regressão logística medido, você não sabe se o BERT está agregando valor ou
complexidade.

### Prometer explicabilidade com mapa de atenção

Atenção não é explicação — há literatura formal sobre isso
([20](20-interpretabilidade-e-bertologia.md)). Prometer isso a um auditor é um problema seu
daqui a alguns meses.

---

## Parte 5 · Erros de produção

### Carregar o modelo dentro da requisição

Latência de segundos em vez de milissegundos. O erro mais comum de todos em produção.

### Não ter limiar de confiança

O modelo sempre responde algo, com confiança alta, inclusive para entrada fora do domínio.
Sem limiar, não existe a rota "não sei" e o erro vira decisão automática.

### Confiar que a confiança é probabilidade

Redes neurais modernas são sistematicamente mais confiantes do que acertam. 90% de confiança
não significa 90% de acerto. Calibre ([18](18-avaliacao-e-benchmarks.md)).

### Baixar o modelo do Hub em runtime

Falha de rede ou mudança no repositório derruba a produção. Empacote o modelo na imagem e use
`HF_HUB_OFFLINE=1`.

### Não fixar a revisão do modelo

O autor pode atualizar os pesos no Hub sem aviso. Seu serviço muda de comportamento sozinho.
Use `revision="<commit sha>"`.

### Não monitorar deriva

O modelo não quebra: degrada. Sem monitoramento, você descobre pelo cliente.

### Sem plano de rollback

Modelo novo ruim em produção e nenhum caminho de volta rápido. Versione modelos como código.

### `trust_remote_code=True` sem pensar

Isso executa código Python do repositório na sua máquina. Só para fonte confiável.

---

## Parte 6 · Erros de projeto e negócio

### Usar BERT onde regex resolve

Extrair CPF, CNPJ, data e valor é trabalho de expressão regular. Um transformer para isso é
100× mais caro e menos confiável.

### Usar BERT onde faltam dados

Com 20 exemplos por classe, use zero-shot ou LLM. Afinar exige dado.

### Não estimar o custo antes de começar

Rotulagem, GPU, engenharia de produção, manutenção, retreino. O treino é a parte barata.
Ver [80-custos-e-licencas.md](80-custos-e-licencas.md).

### Ignorar LGPD

Texto de chamado contém dado pessoal. Enviar para API de terceiro, guardar sem base legal ou
treinar sem consentimento são riscos jurídicos reais. Encoder local é, aliás, uma das
**vantagens** aqui — use-a como argumento.

### Prometer 99%

Se a concordância entre humanos é 85%, prometer 99% é prometer o impossível. Estabeleça a
expectativa medindo o teto humano primeiro.

### Não planejar o retreino

Todo modelo em produção precisa de dono, de cadência de revisão e de orçamento de retreino.
Sem isso, ele apodrece.

---

## Parte 7 · Sinais de alerta

Se você vir isto, pare e investigue:

| Sinal | Suspeita |
|---|---|
| Acurácia > 98% em tarefa difícil | vazamento |
| Treino perfeito, teste ruim | overfitting ou vazamento invertido |
| Resultado muda muito entre sementes | dados insuficientes |
| Perda não cai | taxa de aprendizado alta demais, ou rótulos embaralhados |
| Perda cai, métrica não sobe | métrica errada, ou classe dominante |
| Modelo prevê sempre a mesma classe | desbalanceamento sem tratamento |
| Confiança sempre acima de 99% | overfitting ou calibração ruim |
| Funciona em teste, falha em produção | vazamento temporal ou deriva |
| Ninguém sabe dizer o que o modelo faz | falta model card |

---

## Autoteste

1. Por que "mais épocas" não melhora o modelo, e o que aumenta?
2. Cite três tipos de vazamento e como detectar cada um.
3. Por que a concordância entre anotadores limita o desempenho do modelo?
4. Qual é o efeito de esquecer `model.eval()`? E a `attention_mask`?
5. Por que reportar a melhor de cinco sementes é desonesto, mesmo sem má-fé?
6. Por que mapa de atenção não serve como explicação para um auditor?
7. Cite três erros de produção e a correção de cada um.
8. Quando **não** usar BERT? Dê três casos.
9. Você vê 99% de acurácia numa tarefa difícil. Qual sua primeira hipótese?

---

*Anterior: [70-pratica.md](70-pratica.md) · Próximo: [80-custos-e-licencas.md](80-custos-e-licencas.md)*
