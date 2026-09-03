# 90 · Bibliografia comentada

> **Nível:** todos · **Pesquisado e conferido na web em 02/09/2026.**
> Onde não tenho certeza de uma edição ou ISBN, **está dito no texto**.
> Nada aqui foi inventado.

---

## Aviso, antes da lista

**Livro de Streamlit envelhece muito rápido.** A biblioteca muda a cada duas ou
três semanas, e livro leva de doze a dezoito meses entre escrita e publicação.
Nenhum livro de Streamlit publicado até hoje cobre `st.navigation` (jun/2024),
`st.fragment` estável (jul/2024), `st.login` (2025) ou qualquer coisa de 2026.

**Consequência prática:** leia livro de Streamlit pelos **conceitos e pela
estrutura de projeto**, e a API pela documentação oficial. O contrário produz
código que não roda.

Por isso esta bibliografia é dividida em três: os livros de Streamlit (poucos, e
datados), os livros que **não** envelhecem (design, dados, arquitetura) e os
fundamentos.

---

## 1. Livros de Streamlit

### 1.1 Streamlit for Data Science — 2ª edição

- **Autor:** Tyler Richards (cientista de dados sênior na Snowflake/Streamlit)
- **Editora:** Packt · **2ª edição, setembro de 2023**
- **ISBN-13:** 978-1-80324-822-6
- **Nível:** iniciante a intermediário
- **Gratuito?** Não. Código de exemplo aberto no GitHub da Packt.

**O que faz melhor que os outros:** é escrito por alguém de dentro do projeto, e
se nota — as explicações sobre *por que* a API é assim são melhores que a média.
Cobre bem o fluxo completo: da primeira tela ao deploy, incluindo conexão com
Snowflake, Hugging Face e OpenAI.

**Envelheceu?** **Sim, na API.** É de setembro de 2023: anterior a
`st.navigation`, `st.fragment` estável, `st.dialog`, `st.login`, ao sistema de
tema de 2025–2026 e à troca para Starlette. Já traz `cache_data`/`cache_resource`
(que é o divisor de águas), então não é código antigo demais.

**Recomendo?** Sim, se você quer um livro só. Leia sabendo que a parte de
multipágina e de estado avançado está superada.

### 1.2 Getting Started with Streamlit for Data Science — 1ª edição

- **Autor:** Tyler Richards · **Editora:** Packt · **agosto de 2021**
- **ISBN-13:** 978-1-80056-550-0

É a **primeira edição** do livro acima. **Não compre**: é anterior a
`st.session_state` maduro e usa `@st.cache`, removido. Mencionado aqui só para
você não comprar por engano ao procurar pelo título.

### 1.3 Web App Development Made Simple with Streamlit

- **Autor:** Rosario Moscato · **Editora:** Packt · **fevereiro de 2024**
- **ISBN-13:** 978-1-83508-631-5 · ~350 páginas
- **Nível:** iniciante

**O que faz melhor:** ênfase em **aplicação** e não em ciência de dados — trata de
banco, hashes, sessões e multipágina, que é justamente o que falta na maioria do
material. Se a sua pergunta é "como faço um site com backend", este é o livro de
Streamlit mais próximo do assunto.

**Envelheceu?** Fevereiro de 2024: anterior a `st.navigation` (jun/2024) e a tudo
de 2025–2026. A parte conceitual continua válida.

### 1.4 Web Application Development with Streamlit

- **Autores:** Mohammad Khorasani, Mohamed Abdou, Javier Hernández Fernández
- **Editora:** Apress · **2022**
- **Nível:** intermediário

Foco em desenvolvimento e implantação segura e escalável. **Confira a edição
antes de comprar** — é de 2022, e a parte de API está bastante datada.

### 1.5 O veredito sobre livros de Streamlit

**Opinião, e é minha:** nenhum livro de Streamlit vale o preço hoje se você tem a
documentação oficial e este curso. Livro de Streamlit vale por **um** motivo:
estrutura de aprendizado do começo ao fim, num só volume. Se você aprende melhor
assim, pegue o de Tyler Richards (1.1) ou o de Moscato (1.3) se o seu foco é app
com backend — e confira toda API contra a documentação.

---

## 2. Livros que **não** envelhecem — e valem mais

Estes são os que realmente melhoram o que você produz. Nenhum é sobre Streamlit.

### 2.1 Visualização e painéis

**Storytelling with Data** — Cole Nussbaumer Knaflic
- Wiley, 1ª edição **2015**, ISBN 978-1-119-00225-3
- **Edição de 10º aniversário, 2025**, ISBN 978-1-394-38809-7 (capa dura, visuais
  refeitos, conteúdo ampliado)
- **Nível:** iniciante · **O melhor livro para começar.**
- **O que faz melhor:** ensina a escolher a forma e a **apagar o supérfluo**, com
  antes-e-depois. Metade do [16](16-layout-e-design.md) e do
  [17](17-graficos-e-visualizacao.md) deste curso vem daqui.
- **Envelheceu?** Não. Trata de percepção humana, não de ferramenta.
- **Em português:** há edição brasileira ("Storytelling com Dados", HSM/Alta
  Books). A tradução é razoável; os exemplos foram mantidos.

**Information Dashboard Design** — Stephen Few
- 1ª ed.: O'Reilly, 2006, ISBN 0-596-10016-7
- **2ª ed.: Analytics Press, 2013, ISBN 978-1-938377-00-6** — *Displaying Data for
  At-a-Glance Monitoring*
- **Nível:** intermediário · **O livro sobre painéis.**
- **O que faz melhor:** é implacável com o excesso — medidores, 3D, cores
  decorativas. A regra "números antes de gráficos" e o teste dos cinco segundos
  vêm dessa tradição.
- **Envelheceu?** Os exemplos, sim (as capturas são de ferramentas dos anos 2000).
  Os princípios, não. Leia pelos princípios.

**The Visual Display of Quantitative Information** — Edward Tufte
- Graphics Press, 2ª edição, 2001, ISBN 978-0-9613921-4-7
- **Nível:** intermediário · **O clássico dos clássicos.**
- Origem de "razão dado-tinta" e da crítica ao ornamento. É um livro bonito, mais
  ensaio que manual. Não espere receita.

**Fundamentals of Data Visualization** — Claus O. Wilke
- O'Reilly, 2019, ISBN 978-1-4920-3108-6
- **LEGALMENTE GRATUITO** em <https://clauswilke.com/dataviz/> (o autor liberou)
- **Nível:** intermediário
- **O que faz melhor:** é o mais **técnico e prático** da lista. Capítulos
  específicos sobre daltonismo, escalas de cor e distorção de eixo — exatamente o
  conteúdo do [17](17-graficos-e-visualizacao.md). Se você só for ler um, e for
  ler de graça, leia este.

### 2.2 Dados em Python

**Python for Data Analysis** — Wes McKinney (o criador do pandas)
- O'Reilly, **3ª edição, 2022**, ISBN 978-1-09-810403-0
- **LEGALMENTE GRATUITO** em <https://wesmckinney.com/book/> (versão aberta)
- **Nível:** iniciante a intermediário
- 95% de um painel é pandas. Este é **o** livro de pandas, pelo autor da
  biblioteca. A 3ª edição cobre pandas 2.x.
- **Em português:** há edição da Novatec de edições anteriores; a 3ª aberta em
  inglês é melhor e é grátis.

**Effective Pandas** — Matt Harrison
- publicação independente, 2021 (e edições posteriores)
- **Nível:** intermediário
- Sobre **estilo**: encadeamento de operações, tipos corretos, evitar
  `SettingWithCopyWarning`. Melhora código de painel de forma imediata.
- Confira a edição atual antes de comprar; o autor republica com frequência.

### 2.3 Arquitetura e ofício

**Architecture Patterns with Python** — Harry Percival, Bob Gregory
- O'Reilly, 2020, ISBN 978-1-4920-5220-3
- **LEGALMENTE GRATUITO** em <https://www.cosmicpython.com/>
- **Nível:** avançado
- **O que faz melhor:** é a fundamentação teórica do
  [23-arquitetura-de-app-real.md](23-arquitetura-de-app-real.md). Repositório,
  serviço, unidade de trabalho, e **por que** separar a regra de negócio da
  infraestrutura. Se você leu o arquivo 23 e quer o porquê completo, é aqui.

**A Philosophy of Software Design** — John Ousterhout
- Yaknyam Press, 2ª edição, 2021, ISBN 978-1-73210-221-0
- **Nível:** intermediário · Curto (~190 páginas) e denso.
- Sobre profundidade de módulo e complexidade acumulada. Explica, melhor que
  qualquer outro, por que o `app.py` de 2.000 linhas acontece.

**The Pragmatic Programmer** — Hunt & Thomas
- Addison-Wesley, **edição de 20º aniversário, 2019**, ISBN 978-0-13-595705-9
- **Nível:** todos · Clássico que continua valendo. Há tradução brasileira
  (Bookman), decente.

### 2.4 Segurança

**Web Application Security** — Andrew Hoffman
- O'Reilly, 2020 (2ª edição anunciada; **confira antes de comprar**)
- **Nível:** intermediário
- Contexto para o [29-seguranca.md](29-seguranca.md): por que injeção funciona,
  por que XSS importa, por que autorização no cliente não é autorização.

**OWASP Top 10** — não é livro, é documento, e é **gratuito**
- <https://owasp.org/www-project-top-ten/>
- Leia. São dez itens, e oito deles se aplicam a uma app de Streamlit.

---

## 3. O que é legalmente gratuito, em resumo

Se o orçamento é zero, esta é a estante inteira:

| Livro | Onde |
|---|---|
| **Fundamentals of Data Visualization** (Wilke) | <https://clauswilke.com/dataviz/> |
| **Python for Data Analysis, 3ª ed.** (McKinney) | <https://wesmckinney.com/book/> |
| **Architecture Patterns with Python** (Percival & Gregory) | <https://www.cosmicpython.com/> |
| **Documentação do Streamlit** | <https://docs.streamlit.io> |
| **OWASP Top 10** | <https://owasp.org/www-project-top-ten/> |
| **Documentação do pandas** | <https://pandas.pydata.org/docs/> |
| **The Visual Display of Quantitative Information** | não é gratuito; há cópias em bibliotecas universitárias |

Os quatro primeiros, lidos nesta ordem — Wilke, McKinney, este curso, Percival —
cobrem mais do que qualquer combinação paga da mesma faixa de preço.

---

## 4. A trilha de leitura que eu recomendo

**Se você tem 10 horas:** documentação oficial (seção *Concepts*) + Wilke,
capítulos 4 (cor), 19 (eixos) e 29 (excesso de tinta).

**Se você tem um mês:**
1. este curso, Blocos A e B;
2. Wilke inteiro;
3. McKinney, capítulos 5 a 10.

**Se você quer profissionalizar:**
1. Percival & Gregory (Cosmic Python) inteiro;
2. Ousterhout;
3. Knaflic;
4. OWASP Top 10.

**Se você quer um livro de Streamlit mesmo assim:** Tyler Richards, 2ª edição —
com a documentação aberta ao lado.

---

## Autoteste

1. Por que livro de Streamlit envelhece tão rápido, e como isso muda a forma de
   lê-lo?
2. Qual livro de Streamlit é o mais próximo de "site com backend", e de quando é?
3. Cite três livros da lista que são **legalmente gratuitos** e onde encontrá-los.
4. Qual livro fundamenta teoricamente o arquivo [23](23-arquitetura-de-app-real.md)?
5. Qual é o melhor livro de visualização para quem vai fazer painel, e por quê?
6. Por que "Information Dashboard Design" continua valendo mesmo com exemplos dos
   anos 2000?

---

## Fontes consultadas (02/09/2026)

- Packt Publishing — catálogo de Streamlit: <https://www.packtpub.com/en-us/programming/tool/streamlit>
- Packt, *Streamlit for Data Science, 2nd Ed.* — <https://www.packtpub.com/en-us/product/streamlit-for-data-science-9781803248226>
- Packt, *Web App Development Made Simple with Streamlit* — <https://www.packtpub.com/en-us/product/web-app-development-made-simple-with-streamlit-9781835086315>
- Wiley, *Storytelling with Data* (ed. original e 10º aniversário) — <https://www.wiley.com>
- Sites dos autores para as versões abertas: clauswilke.com/dataviz, wesmckinney.com/book, cosmicpython.com
- Registros de ISBN conferidos nas páginas das editoras e da Amazon
