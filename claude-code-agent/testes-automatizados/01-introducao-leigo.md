# 01 · O que são testes automatizados — para quem nunca programou um

`Nível: iniciante` · `Zero jargão` · `Última atualização: 12/08/2026`

---

## 1. A pergunta antes da pergunta

Você escreveu um programa. Ele funciona? Como você sabe?

A resposta honesta da maioria das pessoas é: *"eu rodei e vi na tela"*. Isso se chama
**teste manual**, e é o que todo mundo faz desde o primeiro dia. Não é errado. O problema é
que ele não escala — e é exatamente por isso que os testes automatizados existem.

## 2. A analogia: a fábrica de torneiras

Imagine uma fábrica de torneiras. Ao final da linha de montagem, uma pessoa pega cada
torneira, abre a água, vê se vaza, fecha, e libera.

Enquanto a fábrica faz 20 torneiras por dia, funciona bem. A pessoa conhece as torneiras,
percebe qualquer coisa estranha, e ainda tem tempo de tomar café.

Agora a fábrica cresce:

- **200 torneiras por dia** → a pessoa começa a testar por amostragem. Alguma vaza no cliente.
- **um modelo novo por semana** → ela precisa lembrar o que verificar em cada modelo.
- **uma peça mudou no modelo antigo** → alguém precisa testar **todos** os modelos de novo,
  porque a peça é compartilhada. Ninguém faz isso. Passa vazando.

O que a fábrica faz na vida real? Instala uma **bancada de teste**: um dispositivo que
prende a torneira, aplica pressão de água, mede o vazamento e acende uma luz verde ou
vermelha. Em três segundos. Para toda torneira, todo dia, sem cansar, sem esquecer, sem
tomar café.

**Um teste automatizado é a bancada de teste do software.** É um programa que usa o seu
programa e verifica se a resposta é a esperada.

## 3. Concretamente: como isso se parece

Suponha que seu programa tenha uma função que calcula desconto:

```
preço 100 reais, desconto de 10%  →  deve dar 90 reais
```

O teste manual é: abrir o programa, digitar 100, digitar 10, olhar a tela, ver "90".

O teste automatizado é um pedacinho de código que faz isso sozinho:

```python
def test_desconto_de_dez_por_cento():
    resultado = aplicar_desconto(100, 10)
    assert resultado == 90
```

Leia em voz alta: *"o teste do desconto de dez por cento: o resultado de aplicar desconto de
10 em 100 — afirmo que é igual a 90."*

Essa palavra `assert` significa **afirmo que**. Se for verdade, o teste passa em silêncio.
Se for mentira, o programa de teste grita.

E é só isso. Um teste automatizado é: **prepare uma situação, execute uma ação, afirme o
resultado**. Todo teste do mundo, do mais simples ao mais sofisticado, é esse trio.

## 4. O que você ganha, em ordem de importância

### 4.1 Você para de ter medo de mexer no código

Este é o benefício real, e quase nunca é o primeiro que citam. Todo programa que dá certo
precisa mudar: a lei mudou, o cliente pediu, a tela ficou feia. Mexer em código que funciona
é assustador — você pode quebrar alguma coisa longe dali e só descobrir com o cliente
ligando.

Com uma boa suíte de testes, você muda, aperta um botão, e em cinco segundos sabe se
quebrou alguma coisa. **Medo vira rotina.** Programadores chamam isso de "rede de
segurança", e a palavra é bem escolhida: o trapezista não usa rede para não cair; usa para
poder arriscar.

### 4.2 Você encontra o erro no minuto em que o comete, não no mês seguinte

Existe uma regra empírica bem estabelecida na engenharia de software: **quanto mais tarde
um defeito é descoberto, mais caro é consertá-lo.** Você acabou de escrever o código —
está tudo fresco na cabeça, conserta em dois minutos. Três meses depois, você não lembra
nada, o código mudou, e conserta em dois dias.

*(A magnitude exata dessa diferença é debatida — números como "100× mais caro em produção"
circulam há décadas com base empírica frágil. Que é **muito** mais caro, ninguém contesta.
Detalhes em [11-historia.md](11-historia.md).)*

### 4.3 O teste é a única documentação que não mente

Comentário no código envelhece: alguém muda a função e esquece o comentário. Documento no
Confluence envelhece pior ainda.

Um teste **não pode** envelhecer sem que alguém perceba: se a função mudar de comportamento,
o teste fica vermelho. Isso o torna a única descrição do sistema que é verificada
automaticamente todo dia. Quando você quer saber o que uma função faz, ler os testes dela é
frequentemente melhor do que ler a função.

### 4.4 Você entrega mais rápido, depois de entregar mais devagar

Escrever teste custa tempo. É verdade, e não adianta fingir que não. Nas primeiras semanas
você produz menos.

O que se ganha depois: você para de gastar tempo abrindo o programa, clicando em cinco
telas e digitando dados de teste **toda vez** que muda uma linha. Esse gasto é invisível
porque está diluído, mas em projeto de tamanho médio ele é maior que o custo de escrever os
testes.

**Opinião profissional, declarada como opinião:** o ponto de equilíbrio costuma chegar em
semanas, não em meses — mas só se os testes forem rápidos. Suíte lenta ninguém roda, e
suíte que ninguém roda tem valor zero.

## 5. O que você **não** ganha

Preciso ser honesto aqui, porque a literatura de testes é cheia de promessa exagerada.

- **Testes não provam que o programa está certo.** Provam que ele passa nos casos que você
  imaginou. Se você não pensou no caso do ano bissexto, o teste não pensa por você. Isso não
  é uma limitação da sua ferramenta; é um resultado teórico, e voltamos a ele em
  [60-teoria-avancada.md](60-teoria-avancada.md).
- **Testes não substituem pensar.** Um teste ruim dá falsa segurança, que é pior que
  nenhuma segurança.
- **Testes não deixam o código bom sozinhos.** Mas eles **denunciam** código ruim: se testar
  uma função é insuportavelmente difícil, quase sempre a função é que está mal desenhada.
  Esse sinal é um dos benefícios mais subestimados do assunto todo.
- **100% de cobertura não significa nada.** Voltamos a isso em
  [19-cobertura-e-metricas.md](19-cobertura-e-metricas.md) — é um dos mitos mais caros do
  campo.

## 6. "Testes automatizados" e "testes unitários" são a mesma coisa?

Não. Essa é provavelmente a confusão mais comum de quem está começando.

- **Teste automatizado** é o gênero: qualquer verificação que um programa faz sozinho.
- **Teste unitário** é uma espécie dentro desse gênero: aquele que verifica **um pedacinho
  isolado** do programa.

Uma analogia com carro:

| Tipo de teste | Na fábrica de carros | No software |
|---|---|---|
| **Unitário** | testar o parafuso: ele aguenta 200 kg? | testar uma função: `desconto(100, 10)` dá 90? |
| **Integração** | testar o motor montado: as peças conversam? | testar se o código grava mesmo no banco de dados |
| **Ponta a ponta** | dar uma volta no quarteirão | abrir o site, clicar, comprar, ver se chegou o e-mail |

Todos os três são automatizados. O unitário é o mais rápido, mais barato e mais numeroso —
por isso ele domina a conversa. Mas ele sozinho não garante que o carro anda: o parafuso
pode estar perfeito e o motor mal montado.

O desdobramento completo está em [12-tipos-e-piramide.md](12-tipos-e-piramide.md).

## 7. Por que isso existe: o problema que fez os testes aparecerem

Nos anos 1950 e 1960, testar era uma **fase**. Programava-se por meses, e no fim uma equipe
separada (às vezes literalmente em outro prédio) testava tudo e mandava a lista de erros de
volta. O ciclo levava semanas.

Duas coisas quebraram esse modelo:

1. **O custo do erro tardio.** Descobrir em novembro um erro cometido em março significava
   refazer tudo que foi construído em cima dele.
2. **A entrega contínua.** A partir dos anos 1990, virou normal atualizar o software toda
   semana, depois todo dia, depois várias vezes por dia. Com uma fase de teste manual de
   duas semanas, isso é aritmeticamente impossível.

A solução foi mover o teste para **dentro** do trabalho de programar e para dentro da
máquina. É daí que vem tudo o que este curso trata. A história completa, com nomes, datas e
o que deu errado no caminho, está em [11-historia.md](11-historia.md).

## 8. Um exemplo que dói: o caso do centavo

Uma empresa cobra R$ 19,99 por mês. Dá 10% de desconto para quem paga anual.

`19,99 − 10%` dá `17,991`. O sistema precisa cobrar R$ 17,99 ou R$ 18,00?

Parece bobagem. Não é:

- se você arredondar para baixo, a empresa perde 1 centavo por cliente por mês;
- se arredondar para cima, o cliente paga 1 centavo a mais;
- com 2 milhões de clientes, isso é R$ 240 mil por ano indo para um lado ou para o outro;
- e há uma segunda armadilha: em quase toda linguagem de programação, `0.1 + 0.2` **não é
  igual a 0.3**. É `0.30000000000000004`. Dinheiro guardado como número decimal comum
  acumula erro.

Um teste automatizado transforma essa decisão de negócio em uma linha executável que
ninguém pode mudar por acidente:

```python
def test_desconto_favorece_o_cliente_no_meio_centavo():
    assert Dinheiro.de_reais("19,99").aplicar_desconto(10).centavos == 1799
```

Se daqui a dois anos alguém "simplificar" o código e mudar o arredondamento, esse teste
fica vermelho e a pessoa é obrigada a decidir conscientemente. Sem o teste, ninguém percebe
até a auditoria.

Esse caso exato está implementado, com as duas linguagens, em
[07-projeto-modelo/](07-projeto-modelo/README.md).

## 9. Quem escreve os testes?

Historicamente havia uma separação: programadores programam, testadores testam. Hoje, na
prática dominante do mercado:

| Quem | O que escreve |
|---|---|
| **Quem programa** | testes unitários e de integração do próprio código, junto com o código |
| **Especialista em qualidade (QA)** | testes de ponta a ponta, exploratórios, de carga, e estratégia |
| **Ninguém, e é um problema** | testes do código antigo que ninguém entende |

A ideia de "jogar o código por cima do muro para o time de testes" é considerada obsoleta
desde os anos 2000, e o motivo é econômico, não ideológico: o retrabalho de ida e volta
custa mais que escrever o teste na hora.

## 10. Como se parece na prática, no dia a dia

O ciclo de quem trabalha com testes automatizados:

```
 ┌─────────────────────────────────────────────────┐
 │                                                 │
 │   1. escreve/muda um pedaço de código           │
 │                    ↓                            │
 │   2. escreve/roda o teste  →  🔴 vermelho       │
 │                    ↓                            │
 │   3. arruma                                     │
 │                    ↓                            │
 │   4. roda de novo          →  🟢 verde          │
 │                    ↓                            │
 │   5. limpa o código, roda de novo → 🟢          │
 │                    ↓                            │
 │   6. envia. Um robô roda tudo de novo. 🟢       │
 │                                                 │
 └─────────────────────────────────────────────────┘
```

Os passos 2 a 5 levam **segundos**, não minutos. É por isso que a velocidade da suíte é
tratada neste curso como requisito, não como detalhe.

O passo 6 se chama **integração contínua** (CI) e está em
[21-ci-e-automacao.md](21-ci-e-automacao.md).

## 11. O vocabulário mínimo para seguir adiante

Sete palavras. Todas voltam com definição formal depois; aqui vai o suficiente para
continuar lendo.

| Palavra | O que quer dizer | Em inglês |
|---|---|---|
| **asserção** | a afirmação que o teste faz ("afirmo que é 90") | *assertion* |
| **suíte** | o conjunto de todos os testes de um projeto | *test suite* |
| **passar / falhar** | verde / vermelho | *pass / fail* |
| **cobertura** | quanto do seu código foi executado pelos testes | *coverage* |
| **dublê** | objeto falso que substitui algo caro ou externo no teste | *test double* |
| **fixture** | o cenário preparado antes do teste rodar | *fixture* |
| **flaky** | teste que às vezes passa e às vezes falha sem motivo | *flaky test* |

Todas as demais estão no [GLOSSARIO.md](GLOSSARIO.md).

## 12. O que vem agora

Se você quer **entender**, siga para [10-fundamentos.md](10-fundamentos.md).

Se você quer **fazer**, siga para [02-pre-requisitos.md](02-pre-requisitos.md) e depois
[03-instalacao.md](03-instalacao.md). Em cerca de 40 minutos você terá o primeiro teste
rodando, em Python ou em JavaScript, à sua escolha.

Se você tem pressa e já programa, pule direto para
[04-como-comecar.md](04-como-comecar.md) — ele leva do zero à primeira luz verde.

---

## Autoteste

1. Explique, sem usar a palavra "teste", o que uma bancada de teste de torneiras tem a ver com software.
2. Quais são as três partes de qualquer teste automatizado?
3. Qual a diferença entre "teste automatizado" e "teste unitário"?
4. Cite dois benefícios de testes automatizados que **não** são "encontrar erros".
5. Por que um teste é considerado melhor documentação que um comentário no código?
6. O que um teste automatizado **não** consegue provar?
7. No caso do centavo, o teste resolve a questão do arredondamento? Ou faz outra coisa?
8. Por que a **velocidade** da suíte de testes é tratada como requisito, e não como detalhe?
