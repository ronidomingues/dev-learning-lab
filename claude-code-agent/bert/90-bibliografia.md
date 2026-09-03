# 90 · Bibliografia comentada

`Nível: todos` · `**Edições e disponibilidade verificadas em 12/08/2026**`

Livros, com autor, editora, edição e ano — e, para cada um, o que ele faz melhor que os
outros, para que nível serve, e se envelheceu. **Nada aqui foi inventado**; onde não
confirmei o ISBN ou a edição, digo isso explicitamente.

Legenda: 🆓 legalmente gratuito · 🇧🇷 tem edição em português · ⭐ recomendação principal

---

## 1 · O livro para começar

### ⭐ 🇧🇷 *Natural Language Processing with Transformers* (Revised Edition)
**Lewis Tunstall, Leandro von Werra, Thomas Wolf** · O'Reilly Media, edição revisada, 2022
ISBN-13: 978-1-098-13679-6 (a primeira edição é 978-1-098-10324-8)

Escrito por três engenheiros do **Hugging Face** — os autores da biblioteca que este curso
usa. Cobre classificação, NER, QA, sumarização, destilação, quantização e treino de
modelos, sempre com código.

- **Nível:** iniciante a intermediário.
- **O que faz melhor:** é o único livro que ensina *a biblioteca* e *os conceitos* juntos,
  sem desconexão. A explicação da atenção no capítulo 3 é excelente.
- **Envelheceu?** **Parcialmente, e você precisa saber onde.** Foi escrito para o
  `transformers` 4.x. Boa parte do código não roda literalmente na v5 usada aqui — veja a
  [tabela de tradução v4 → v5](03-instalacao.md#o-que-mudou-do-transformers-4-para-o-5).
  Os **conceitos** continuam corretos e valiosos; trate o código como pseudocódigo a ser
  adaptado.
- **Em português:** existe tradução — *Processamento de linguagem natural com
  transformadores, edição revisada*, publicada pela O'Reilly
  ([página do livro](https://www.oreilly.com/library/view/processamento-de-linguagem/9798341641341/)).
  Não avaliei a qualidade da tradução; a terminologia técnica de PLN traduzida costuma
  atrapalhar quem depois lê documentação em inglês.

---

## 2 · A referência da área

### ⭐ 🆓 *Speech and Language Processing* (3rd edition, rascunho)
**Dan Jurafsky, James H. Martin** · rascunho aberto, atualização mais recente de **janeiro de 2026**
[web.stanford.edu/~jurafsky/slp3](https://web.stanford.edu/~jurafsky/slp3/)

**O livro-texto canônico de PLN**, usado em cursos de graduação e pós no mundo inteiro. A
terceira edição foi reescrita para a era dos Transformers e modelos de linguagem, e o
rascunho é **legalmente gratuito** — os autores liberam os capítulos e os slides.

- **Nível:** intermediário a avançado. Exige matemática.
- **O que faz melhor:** rigor e amplitude. Trata linguística, não só engenharia — a única
  fonte desta lista que explica *por que* a língua é difícil, não só como o modelo lida com ela.
- **Envelheceu?** Não: está em atualização ativa, e a versão de janeiro de 2026 é a mais recente.
- **Como usar neste curso:** os capítulos de embeddings, atenção e Transformers são a
  fundamentação teórica ideal para [13](13-arquitetura-encoder.md) e [60](60-teoria-avancada.md).
- **Em português:** a 2ª edição teve tradução; a **3ª não** (é rascunho aberto em inglês).

---

## 3 · Fundamentos de aprendizado profundo

### 🆓 🇧🇷 *Dive into Deep Learning* (D2L)
**Aston Zhang, Zachary Lipton, Mu Li, Alexander Smola** · Cambridge University Press, 2023
[d2l.ai](https://d2l.ai/) (inglês) · [pt.d2l.ai](https://pt.d2l.ai/) (tradução para português)

Livro interativo: cada conceito vem com código executável em PyTorch. Tem capítulos
próprios sobre atenção, Transformers e BERT — inclusive **pré-treino de BERT do zero**.

- **Nível:** iniciante a avançado (cresce com você).
- **O que faz melhor:** a integração texto ↔ código. É o melhor lugar para *implementar*
  os conceitos, não só ler sobre eles.
- **Gratuito:** sim, versão web completa. Também existe edição impressa paga.
- **Em português:** tradução comunitária, **incompleta e com qualidade irregular**. Útil,
  mas confira contra o original quando algo parecer estranho.

### *Deep Learning*
**Ian Goodfellow, Yoshua Bengio, Aaron Courville** · MIT Press, 2016 · 🆓 em
[deeplearningbook.org](https://www.deeplearningbook.org/)

- **Nível:** avançado, matemático.
- **Envelheceu?** **Sim, em parte relevante para este curso:** é de 2016 e **não cobre
  Transformers**. Continua sendo a melhor referência de fundamentos (otimização,
  regularização, teoria da generalização) — leia por isso, não por BERT.
- **Em português:** a Bookman publicou uma tradução (*Deep Learning*). Não verifiquei a
  edição e não avaliei a tradução.

### 🇧🇷 *Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow* (3ª edição)
**Aurélien Géron** · O'Reilly, 3ª edição, 2022

- **Nível:** iniciante a intermediário. O melhor livro prático de ML em geral.
- **Ressalva importante para este curso:** usa **TensorFlow/Keras**, não PyTorch. Os
  capítulos de fundamentos de ML (avaliação, validação cruzada, overfitting) valem muito;
  os de PLN são secundários e menos atuais que os do Tunstall.
- **Em português:** há edição pela Alta Books (*Mãos à Obra: Aprendizado de Máquina...*).
  A tradução para PT-BR de livros técnicos da Alta Books tem qualidade variável — folheie
  antes de comprar.

---

## 4 · Para entender por dentro

### *Build a Large Language Model (From Scratch)*
**Sebastian Raschka** · Manning, 2024

Constrói um modelo de linguagem completo do zero, em PyTorch, linha por linha — incluindo
tokenizador, atenção e treino.

- **Nível:** intermediário. Exige PyTorch básico.
- **O que faz melhor:** é o antídoto para caixa-preta. Depois dele, nenhuma parte de um
  Transformer parece mágica.
- **Ressalva:** o foco é **decoder** (estilo GPT), não encoder. A mecânica da atenção,
  porém, é a mesma — e é o que importa aqui.
- **Gratuito?** O livro é pago; o **código é aberto** em
  [github.com/rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch), e vale
  por si só.

### *Transformers for Natural Language Processing and Computer Vision* (3ª edição)
**Denis Rothman** · Packt, 3ª edição, 2024

- **Nível:** intermediário.
- **Opinião honesta:** cobre muita coisa, incluindo material recente, mas é irregular em
  profundidade e edição. Prefira o Tunstall como primeiro livro; use este como
  complemento se quiser mais amplitude de modelos.

---

## 5 · Contexto e crítica

### *Atlas of AI*
**Kate Crawford** · Yale University Press, 2021

Sobre o custo material, ambiental e humano da IA — mineração, trabalho de anotação,
extração de dados. Nenhuma linha de código.

- **Por que está numa bibliografia técnica:** porque [80-custos-e-licencas.md](80-custos-e-licencas.md)
  e [20-interpretabilidade-e-bertologia.md](20-interpretabilidade-e-bertologia.md) tocam em
  questões que este livro trata a sério. Rotular dados é trabalho humano, e vale saber de
  quem é.
- **Em português:** existe tradução no Brasil; não verifiquei a editora e a edição.

---

## 6 · O que **não** recomendar

Honestidade sobre o que evitar:

| Categoria | Por quê |
|---|---|
| Livros de PLN anteriores a 2019 | pré-Transformer. A área virou; o material é história, não prática |
| Livros de "BERT" de editoras de nicho, 2019–2021 | costumam ser tutoriais reciclados da documentação, já desatualizados |
| Qualquer livro cujo código dependa de `transformers` 3.x ou 4.x sem aviso | vai falhar na v5 e você vai perder tempo depurando o livro |
| Cursos-livro gerados por IA em plataformas de autopublicação | proliferaram desde 2023; conteúdo genérico, referências às vezes inventadas |

**Regra prática:** em uma área com ciclo de 12 a 18 meses, livro é para **conceito**, não
para API. Para API, a fonte é a documentação oficial —
[95-referencias.md](95-referencias.md).

---

## 7 · Ordem de leitura sugerida

**Praticante:**
```
Tunstall (caps. 1–4)  →  este curso  →  D2L (atenção e Transformers)  →  Raschka
```

**Acadêmico / pesquisa:**
```
Jurafsky & Martin (embeddings → Transformers)  →  papers de 95-referencias.md
   →  Goodfellow (fundamentos)  →  D2L (implementação)
```

**Com orçamento zero:**
```
Jurafsky & Martin 🆓  →  D2L 🆓  →  código do Raschka 🆓  →  Goodfellow 🆓
```
Os quatro juntos cobrem do zero ao nível de pesquisa **sem custo nenhum e legalmente**.

---

## Autoteste

1. Qual livro é escrito pelos autores da própria biblioteca `transformers`, e qual é sua principal limitação hoje?
2. Qual é o livro-texto canônico de PLN, e por que ele é gratuito?
3. Por que o *Deep Learning* de Goodfellow não serve para aprender BERT?
4. Qual livro é o melhor antídoto contra tratar o Transformer como caixa-preta?
5. Quais quatro livros formam uma trilha completa e legalmente gratuita?
6. Por que livros de PLN anteriores a 2019 são de valor histórico apenas?
7. Qual é a regra prática sobre livro versus documentação nesta área?

---

## Nota de verificação

Confirmei em 12/08/2026: os ISBNs de Tunstall (ambas as edições), a atualização de janeiro
de 2026 do Jurafsky & Martin, e a existência da tradução do Tunstall para português pela
O'Reilly. **Não verifiquei** editoras, edições e ISBNs das traduções brasileiras de
Goodfellow, Géron e Crawford — por isso estão citadas sem ISBN, apenas por autor e título.
Confira antes de comprar.

---

*Anterior: [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) · Próximo: [95-referencias.md](95-referencias.md)*
