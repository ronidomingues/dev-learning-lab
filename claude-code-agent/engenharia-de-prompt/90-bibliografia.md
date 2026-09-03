# 90 · Bibliografia comentada

**Nível:** todos
**Edições e disponibilidade conferidas na web em 19/08/2026.**
Regra deste arquivo: **nada inventado.** Onde não conferi o ISBN, ele não
aparece — cito autor, título e ano, e você confere na livraria.

---

## 90.1 · Se você for ler um livro só

**Chip Huyen, *AI Engineering: Building Applications with Foundation Models*,
O'Reilly, 2025.** ISBN 978-1098166304 (impresso).

Cobre o ofício inteiro: avaliação, projeto de prompt, RAG, agentes, custo,
implantação. O enquadramento é de engenharia, não de pesquisa — que é
exatamente o que falta na maioria dos livros da categoria. A seção de avaliação
sozinha justifica o preço.

**Nível:** intermediário. **Envelheceu?** Não; foi escrito já com a virada de
2024–2025. As partes sobre modelos específicos envelhecem; o método, não.
**Português:** não localizei tradução em 19/08/2026.

---

## 90.2 · Sobre prompt, especificamente

**John Berryman e Albert Ziegler, *Prompt Engineering for LLMs: The Art and
Science of Building Large Language Model-Based Applications*, O'Reilly,
novembro de 2024.** ISBN 978-1098156152.

O único livro sério dedicado ao assunto. Escrito por gente que construiu o
GitHub Copilot — e isso aparece: o foco é montar o contexto de um sistema real,
não colecionar frases. Melhor no que é "montagem de prompt em produção".

**Nível:** intermediário. **Envelheceu?** Parcialmente. Escrito antes da
geração de modelos com raciocínio nativo, então a parte de cadeia de pensamento
está datada. A parte de arquitetura de contexto continua excelente.

---

## 90.3 · Para entender o modelo por dentro

**Jay Alammar e Maarten Grootendorst, *Hands-On Large Language Models:
Language Understanding and Generation*, O'Reilly, outubro de 2024.**
ISBN 978-1098150969.

Alammar é o autor do *The Illustrated Transformer*, e o livro tem a mesma
qualidade visual. É o caminho mais rápido de "não faço ideia de como funciona"
até "consigo raciocinar sobre tokens, embeddings e atenção". Código no
[repositório oficial](https://github.com/handsOnLLM/Hands-On-Large-Language-Models).

**Nível:** iniciante → intermediário. **Envelheceu?** A parte conceitual, não.

**Sebastian Raschka, *Build a Large Language Model (From Scratch)*, Manning,
2024.** ISBN 978-1633437166.

Você implementa um LLM em PyTorch, do tokenizador ao ajuste fino. É o antídoto
definitivo contra tratar o modelo como magia. **Não é necessário** para
engenharia de prompt — é para quem quer a compreensão profunda. Código em
[github.com/rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch).

**Nível:** avançado; exige Python e PyTorch.

---

## 90.4 · Clássicos e referência

**Dan Jurafsky e James H. Martin, *Speech and Language Processing*, 3ª edição
(rascunho).** 🆓 **Legalmente gratuito**, licença Creative Commons, em
<https://web.stanford.edu/~jurafsky/slp3/>. Rascunho da 3ª edição publicado em
24/08/2025.

A referência canônica de processamento de linguagem natural. Você não lê de
capa a capa; consulta o capítulo de que precisa. Os capítulos sobre modelos de
linguagem e transformers dão a base formal que falta em todo material prático.

**Nível:** intermediário → avançado. **Envelheceu?** É atualizado
continuamente. **Português:** há tradução da 2ª edição, que está muito datada
para este uso — prefira o rascunho gratuito em inglês.

---

## 90.5 · Adjacentes que valem o tempo

| Livro | Por que ler | Nível |
|---|---|---|
| **Tunstall, von Werra e Wolf, *Natural Language Processing with Transformers*, O'Reilly** (rev. 2022) | a mecânica de transformers com código; datado quanto a APIs, sólido quanto a conceitos | intermediário |
| **Kahneman, *Rápido e Devagar*** (Objetiva, ed. brasileira) | vieses cognitivos — os seus, ao avaliar saída de modelo, e os do humano que rotula | todos |
| **Kohavi, Tang e Xu, *Trustworthy Online Controlled Experiments*, Cambridge, 2020** | como não se enganar com experimento e métrica; aplica-se diretamente a avaliação de prompt | intermediário |
| **Huyen, *Designing Machine Learning Systems*, O'Reilly, 2022** | deriva de dados, monitoramento, ciclo de vida — tudo reaproveitável | intermediário |

---

## 90.6 · O que **não** recomendo

Sem citar títulos, porque o problema é de categoria:

- **"1000 prompts para X"**, em qualquer formato. Prompt fora do seu contexto,
  dos seus dados e da sua métrica não transfere. E envelhece em meses.
- **Livros de "domine a IA em 7 dias"** publicados em 2023. Metade do conteúdo
  são técnicas hoje inúteis ([11-historia](11-historia.md)).
- **Livros gerados por IA** vendidos em plataformas de autopublicação. Há
  muitos, com capa profissional e conteúdo genérico. Sinais: autor sem
  histórico, sem código, sem número, sem editora conhecida.

---

## 90.7 · Como ler, na ordem

| Momento | Leia |
|---|---|
| antes de tudo | este curso, [01](01-introducao-leigo.md) a [07](07-projeto-modelo/README.md) |
| quando quiser entender o "porquê" | Alammar & Grootendorst |
| quando for para produção | **Huyen, *AI Engineering*** |
| quando montar contexto de sistema real | Berryman & Ziegler |
| quando avaliação virar seu trabalho | Kohavi et al. + [20](20-avaliacao-e-evals.md) |
| quando quiser a base formal | Jurafsky & Martin (gratuito) |
| quando quiser tirar toda a magia | Raschka |

---

## Autoteste

1. Se você só puder ler um livro para trabalhar com isso, qual e por quê?
2. Qual parte do livro de Berryman & Ziegler envelheceu, e qual continua valendo?
3. Qual referência da lista é legalmente gratuita, e sob qual licença?
4. Por que um livro sobre experimentos controlados entra numa bibliografia de
   engenharia de prompt?
5. Como identificar um livro gerado por IA numa livraria online?

---

### Fontes consultadas (19/08/2026)

- O'Reilly, *AI Engineering* — <https://www.oreilly.com/library/view/ai-engineering/9781098166298/>
- O'Reilly / Amazon, *Prompt Engineering for LLMs* (ISBN 9781098156152) — <https://www.amazon.com/Prompt-Engineering-LLMs-Model-Based-Applications/dp/1098156153>
- O'Reilly, *Hands-On Large Language Models* (ISBN 9781098150969) — <https://www.oreilly.com/library/view/hands-on-large-language/9781098150952/>
- Manning, *Build a Large Language Model (From Scratch)* (ISBN 9781633437166) — <https://www.manning.com/books/build-a-large-language-model-from-scratch>
- Stanford, *Speech and Language Processing*, 3ª ed. (rascunho, CC) — <https://web.stanford.edu/~jurafsky/slp3/>
