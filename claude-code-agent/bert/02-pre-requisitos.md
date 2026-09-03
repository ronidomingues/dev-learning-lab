# 02 · Pré-requisitos

`Nível: iniciante` · `Última atualização: 11/08/2026`

---

Este arquivo responde: **o que preciso saber, ter e quanto tempo vai levar** — com números
honestos, não otimistas. E o que fazer se faltar algo (a *rota de resgate*, no final).

---

## Parte 1 · Conhecimento

### Indispensável

Sem isto, você vai travar na primeira hora. Não dá para pular.

| Pré-requisito | O que exatamente | Onde aprender |
|---|---|---|
| **Python básico** | variáveis, `if`/`for`, funções, listas, dicionários, importar módulo, ler arquivo | [Curso em Vídeo — Python 3 (Gustavo Guanabara, PT, grátis)](https://www.cursoemvideo.com/curso/python-3-mundo-1/) · [Python for Everybody (EN, grátis)](https://www.py4e.com/) |
| **Terminal / linha de comando** | `cd`, `ls`, rodar um comando, ativar um ambiente virtual, ler mensagem de erro | [MIT Missing Semester (EN, grátis, 2h)](https://missing.csail.mit.edu/) |
| **Ler inglês técnico** | ler mensagem de erro, documentação e model card. Não precisa falar nem escrever | tradutor + prática. Não há atalho: 95% do material vive em inglês |

Note o que **não** está nesta lista: matemática, machine learning, redes neurais, álgebra
linear, estatística. Para *usar* BERT — instalar, afinar, colocar em produção — nada disso é
necessário. Isso surpreende quem chega, e é verdade: as bibliotecas escondem a matemática
por trás de umas 15 linhas de código.

Se você só quer usar, pare de ler os pré-requisitos aqui e vá para
[03-instalacao.md](03-instalacao.md).

### Ajuda muito (mas dá para começar sem)

| Pré-requisito | Por que ajuda | Onde aprender |
|---|---|---|
| **pandas / NumPy** | seus dados vão chegar em CSV/Excel; toda preparação passa por aí | [pandas — 10 minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html) |
| **Noção de ML supervisionado** | entender treino/validação/teste, *overfitting*, acurácia vs. F1 — sem isso você vai treinar algo que parece ótimo e falha em produção | [Google ML Crash Course (tem PT-BR, grátis)](https://developers.google.com/machine-learning/crash-course?hl=pt-br) |
| **Git** | baixar projetos, versionar experimentos | [Git — Pro Git em português (grátis)](https://git-scm.com/book/pt-br/v2) |
| **Docker** | reprodutibilidade e deploy. Há um curso completo nesta pasta | [`../docker/00-MAPA.md`](../docker/00-MAPA.md) |

### Necessário só para os arquivos de teoria profunda (Bloco B avançado, 60)

| Pré-requisito | Onde ele aparece |
|---|---|
| **Álgebra linear** — vetor, matriz, produto escalar, multiplicação de matrizes | [13-arquitetura-encoder.md](13-arquitetura-encoder.md), [60-teoria-avancada.md](60-teoria-avancada.md) |
| **Cálculo** — derivada parcial, regra da cadeia, gradiente | [60-teoria-avancada.md](60-teoria-avancada.md) |
| **Probabilidade** — distribuição, verossimilhança, entropia cruzada | [14-pre-treino-mlm-nsp.md](14-pre-treino-mlm-nsp.md), [60-teoria-avancada.md](60-teoria-avancada.md) |

Onde aprender, de graça e em ordem:
[3Blue1Brown — Essence of Linear Algebra](https://www.3blue1brown.com/topics/linear-algebra)
(legendas em PT) → [Khan Academy Brasil — Cálculo](https://pt.khanacademy.org/math/calculus-1) →
capítulos 2–5 de [*Dive into Deep Learning*](https://pt.d2l.ai/) (versão em português, grátis).

Estes arquivos avisam no topo quando exigem matemática. Você pode ler todo o resto do curso
sem eles e voltar depois.

---

## Parte 2 · Ambiente e hardware

### Software mínimo

| Item | Versão mínima | Versão recomendada (ago/2026) | Observação |
|---|---|---|---|
| Sistema operacional | Linux, macOS 12+, Windows 10+ | Ubuntu 24.04 LTS, macOS 15, Windows 11 + WSL2 | Windows nativo funciona; WSL2 é melhor |
| Python | 3.10 | **3.12** | 3.9 é rejeitado por `transformers` 5.x. 3.13/3.14 funcionam, mas alguma dependência ainda pode atrasar |
| PyTorch | 2.4 | **2.13** | é o único backend suportado desde `transformers` 5.0 |
| transformers | 5.0 | **5.15** | v4.x ainda funciona, mas a API mudou; ver [03-instalacao.md](03-instalacao.md) |
| Espaço em disco | 10 GB | **25 GB** | PyTorch com CUDA sozinho passa de 3 GB; modelos e cache crescem rápido |
| Memória RAM | 8 GB | **16 GB** | com 8 GB dá para *usar* BERT-base; treinar fica apertado |

### Hardware: preciso de GPU?

A pergunta mais frequente, e a resposta é "depende do que você vai fazer":

| Tarefa | CPU comum | GPU |
|---|---|---|
| Rodar (inferência) BERT-base em 1 frase | 5–30 ms — **tranquilo** | 1–3 ms |
| Classificar 100 mil textos | ~1 a 3 horas — aceitável | 2–5 minutos |
| **Afinar** BERT-base, 5 mil exemplos, 3 épocas | 40 min a 3 h — **desconfortável, mas viável** | 2–5 minutos |
| Afinar BERT-large ou 100 mil exemplos | 10+ horas — inviável na prática | 20–60 minutos |
| Pré-treinar do zero | impossível | também caro: milhares de dólares |

**Conclusão prática:** você **não precisa comprar GPU** para aprender. As duas saídas
gratuitas, nesta ordem:

1. **Google Colab** (gratuito) — GPU T4 grátis com limite diário, no navegador, sem instalar
   nada. É onde a maioria das pessoas aprende. Detalhes em
   [03-instalacao.md](03-instalacao.md#alternativa-sem-instalar-nada).
2. **Kaggle Notebooks** (gratuito) — cota mais generosa: ~30 h/semana de GPU. Exige
   verificação por telefone.

Se for comprar: qualquer NVIDIA com 8 GB de VRAM (RTX 3060 12 GB é o melhor custo-benefício
usado, em agosto de 2026) resolve tudo neste curso. AMD funciona via ROCm no Linux com
atrito real; Apple Silicon funciona via MPS e é surpreendentemente decente para BERT-base
(um M2/M3 afina em minutos), mas parte do ecossistema assume CUDA.

### Contas em serviços

| Serviço | Obrigatório? | Custo | Precisa cartão? |
|---|---|---|---|
| **Hugging Face** | Não para modelos públicos; **sim** para publicar modelos, usar modelos "gated" e evitar limite de download anônimo | Grátis | Não |
| **Google (Colab)** | Só se usar Colab | Grátis (com limites) | Não |
| **Kaggle** | Só se usar Kaggle | Grátis | Não (mas exige telefone) |
| **Weights & Biases** | Não. Opcional, para acompanhar treinos | Grátis para uso pessoal | Não |

Nada neste curso exige cartão de crédito. Ver [80-custos-e-licencas.md](80-custos-e-licencas.md).

---

## Parte 3 · Tempo realista

Estimativas para alguém que já tem os pré-requisitos indispensáveis e estuda com regularidade.
São honestas, não motivacionais — a maioria dos cursos promete metade disso.

| Nível | O que você consegue fazer | Tempo | Arquivos |
|---|---|---|---|
| **Curioso** | explicar o que é BERT, rodar um exemplo pronto, classificar sentimento | **2 a 4 horas** | `01`, `03`, `04` |
| **Usuário** | afinar um modelo nos seus dados, avaliar, saber se está bom | **15 a 25 horas** (2 a 3 semanas de noites) | + `05`, `06`, `07`, `15`, `18` |
| **Praticante** | escolher o modelo certo, tratar dados sujos, tokenização, colocar em produção com latência controlada | **60 a 100 horas** (2 a 3 meses) | + `10`–`19`, `70`, `75` |
| **Avançado** | ler a arquitetura por dentro, otimizar, quantizar, destilar, adaptar a domínio, pré-treinar de forma contínua | **200 a 300 horas** (6 a 9 meses) | + `20`, `60`, `65` |
| **Pesquisa** | ler e criticar papers, propor variações, reproduzir resultados | **1 a 2 anos** de prática contínua | tudo + `90`, `95` |

Três observações que ninguém dá:

- **A maior parte do tempo não é o modelo — são os dados.** Numa tarefa real, 70% a 85% do
  esforço é conseguir, limpar e rotular exemplos. O treino em si são 20 linhas e 5 minutos.
  Se o seu planejamento não reserva a maior fatia para dados, ele está errado.
- **A curva não é suave.** Existe um platô cruel entre "rodei o tutorial" e "funciona nos meus
  dados". Quase todo mundo trava ali, e o motivo quase nunca é o BERT — é desbalanceamento de
  classes, vazamento entre treino e teste, ou rótulos inconsistentes. O arquivo
  [75-armadilhas.md](75-armadilhas.md) existe por causa desse platô.
- **Estudar teoria antes de rodar não funciona bem aqui.** Rode primeiro, entenda depois.
  A intuição de por que a atenção importa vem muito mais rápido depois de você ter visto o
  modelo errar.

---

## Parte 4 · Rota de resgate

O que fazer se você percebeu que falta um pré-requisito.

### "Não sei Python"

Não tente aprender Python *e* BERT ao mesmo tempo — a taxa de desistência é alta. Faça 15 a
25 horas de Python primeiro (os cursos da tabela acima cobrem). Você precisa de menos do que
imagina: sintaxe básica e conforto com erros. Não precisa de programação orientada a objetos,
decoradores, async nem type hints.

**Atalho legítimo:** se você tem pressa e prazo, o Google Colab com um LLM ao lado te leva
longe copiando e adaptando código. Você vai conseguir resultado — e vai travar feio na
primeira coisa que der errado, porque não vai saber ler o erro. Aceite o atalho conscientemente,
e volte para aprender Python quando travar.

### "Não tenho computador bom"

Use Colab ou Kaggle. Sério: um Chromebook ou um notebook de 2016 com navegador basta para
fazer tudo neste curso até o arquivo `19`. Você só sente falta de máquina própria quando vai
colocar algo em produção — e aí a máquina é do servidor, não sua.

### "Não sei nada de machine learning"

Não bloqueia o início. Mas antes de confiar em qualquer número que seu modelo produzir,
faça as 3 primeiras seções do [Google ML Crash Course](https://developers.google.com/machine-learning/crash-course?hl=pt-br)
(~4 h) e leia [18-avaliacao-e-benchmarks.md](18-avaliacao-e-benchmarks.md) deste curso.
Sem isso você vai anunciar "95% de acurácia" num conjunto em que 95% dos exemplos são de uma
classe só — o erro mais clássico e mais constrangedor do campo.

### "Não sei a matemática"

Leia todo o curso pulando os blocos marcados com `matemática à frente`. Você vai chegar
tranquilo até o arquivo `19` e conseguir trabalhar profissionalmente com isso. A matemática
é o que separa "usar bem" de "criar coisa nova" — e a maioria das pessoas pagas para trabalhar
com isso está no primeiro grupo.

### "Meu problema é urgente e é para ontem"

Ordem mínima, ~3 horas: [03-instalacao.md § Colab](03-instalacao.md#alternativa-sem-instalar-nada)
→ [04-como-comecar.md](04-como-comecar.md) → o exemplo de fine-tuning em
[06-exemplos.md](06-exemplos.md) → [75-armadilhas.md](75-armadilhas.md) (leia este, mesmo com
pressa — ele te poupa de entregar um modelo quebrado).

---

## Checklist antes de seguir

- [ ] Consigo abrir um terminal e rodar `python --version` sem erro
- [ ] Sei o que é uma pasta, um caminho e como navegar até uma no terminal
- [ ] Consigo ler uma mensagem de erro em inglês e identificar a última linha
- [ ] Tenho 25 GB livres em disco **ou** decidi usar Colab/Kaggle
- [ ] Decidi meu caminho: máquina local ou nuvem gratuita
- [ ] (Opcional, recomendado) Criei uma conta gratuita no Hugging Face

Com isso marcado, siga para [03-instalacao.md](03-instalacao.md).

---

## Autoteste

1. Para *usar* BERT, você precisa saber álgebra linear? E para entender o arquivo `60`?
2. Qual é a versão mínima de Python aceita por `transformers` 5.x, e por quê?
3. Você tem um notebook sem GPU e quer afinar um BERT-base com 5 mil exemplos. Quais são suas três opções, e qual você escolheria?
4. Qual fatia do tempo de um projeto real vai para os dados, e não para o modelo?
5. Onde a maioria das pessoas trava, e qual costuma ser a causa real?
6. Você precisa de cartão de crédito para completar este curso?
7. Qual é a rota de resgate se você não sabe Python mas tem prazo curto — e qual o preço desse atalho?

---

*Anterior: [01-introducao-leigo.md](01-introducao-leigo.md) · Próximo: [03-instalacao.md](03-instalacao.md)*
