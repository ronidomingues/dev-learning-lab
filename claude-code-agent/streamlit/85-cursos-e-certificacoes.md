# 85 · Cursos gratuitos e certificações

> **Nível:** todos · **Pesquisado na web em 02/09/2026.**
> Links podem expirar. O ano de publicação de cada recurso está indicado —
> material de Streamlit envelhece rápido, e a seção 6 explica como detectar isso.

---

## Aviso de método, antes de tudo

Duas coisas que quase nenhum "melhores cursos de Streamlit" diz:

1. **A documentação oficial é melhor que 90% dos cursos**, e é gratuita. Ela é
   versionada, tem exemplos executáveis e uma referência de API completa. Comece
   por ela.
2. **Curso de Streamlit envelhece em meses.** Um vídeo de 2022 ensina
   `@st.cache` (removido), `st.experimental_rerun` (removido) e a pasta mágica
   `pages/` (superada). Ele não está "um pouco velho": ele ensina API que não
   existe mais.

---

## 1. Português (Brasil e Portugal)

### 1.1 Gratuitos de verdade

| Curso | Autor / instituição | Plataforma | Duração | Nível | Ano | Vale? |
|---|---|---|---|---|---|---|
| [Curso de Streamlit (playlist)](https://www.youtube.com/playlist?list=PLpdAy0tYrnKyEqDC6ymS4MQaAOnDXCUY0) | Hashtag Programação | YouTube | ~4 h | iniciante | 2024 | **Sim.** Progressivo e em português claro; chega a um dashboard de corretora de ações. Confira a API contra o [05](05-manual-de-uso.md) antes de copiar. |
| [Construção de Dashboards em Python com Streamlit](https://www.youtube.com/watch?v=RNi1kQxNw5E) | canal independente | YouTube | ~3 h (aulas) | iniciante | 2023 | **Com ressalva.** Bom para a intuição; a API mudou bastante desde então. |
| [Streamlit em menos de 10 minutos](https://www.youtube.com/watch?v=zxA97KcUm1Q) | Asimov Academy | YouTube | 10 min | iniciante | 2024 | **Sim, como aperitivo.** Serve para decidir se você quer seguir. |
| [Curso gratuito de Python para iniciantes](https://wp.asimov.academy/curso-gratuito-python/) | Asimov Academy | próprio | ~20 h | zero absoluto | 2025 | **Sim, se falta Python.** Termina construindo um app de vendas com Streamlit e pandas. Gratuito com cadastro; emite certificado de conclusão. |
| [Curso Completo de Streamlit (texto)](https://medium.com/@habbema/curso-completo-de-streamlit-parte-1-e7fed18d010b) | Hugo Habbema | Medium | leitura | iniciante/intermediário | atualizado em fev/2026 | **Sim.** É dos materiais em português mais atualizados que encontrei. Formato texto, fácil de conferir contra a documentação. |

### 1.2 "Gratuito para assistir, pago para o resto"

| Curso | Plataforma | O que é grátis | O que é pago |
|---|---|---|---|
| [Curso de Streamlit](https://www.hashtagtreinamentos.com/streamlit-python) | Hashtag Treinamentos | as aulas em vídeo, em quatro etapas | trilhas completas e suporte |
| [Trilha Dashboards Interativos com Python](https://www.asimov.academy/trilhas/dashboards-interativos-com-python/) | Asimov Academy | parte introdutória | a trilha completa (Pandas, Plotly, Dash, Streamlit) e o certificado |
| Diversos cursos de Streamlit | Udemy | prévia de algumas aulas | o curso (frequente promoção; **nunca pague o preço cheio**, ele cai para ~R$ 30–60 com regularidade) |

### 1.3 A verdade sobre o material em português

Sendo direto: **o material em português é fraco em profundidade.** Ele cobre bem
"faça seu primeiro dashboard" e para aí. Não encontrei, em 02/09/2026, nenhum
curso em português que trate a sério de: modelo de execução, isolamento de cache
entre usuários, autenticação OIDC, testes com `AppTest`, ou deploy atrás de proxy.

**Consequência prática:** use o português para a porta de entrada e passe para o
inglês (ou para este curso) para o resto. Foi uma das razões de escrever este
material.

---

## 2. Inglês

### 2.1 A documentação oficial — comece aqui

| Recurso | Link | Por que |
|---|---|---|
| **Documentação** | <https://docs.streamlit.io> | referência de API completa, versionada, com exemplos executáveis |
| **Tutoriais oficiais** | <https://docs.streamlit.io/develop/tutorials> | autenticação, conexão com banco, gráficos, recursos avançados — passo a passo |
| **Conceitos de arquitetura** | <https://docs.streamlit.io/develop/concepts/architecture> | rerun, session state, fragmentos, cache — a parte que os cursos pulam |
| **Notas de versão** | <https://docs.streamlit.io/develop/quick-reference/release-notes> | o que mudou e quando; leia antes de atualizar |
| **App testing** | <https://docs.streamlit.io/develop/concepts/app-testing> | `AppTest`, do zero |
| **Galeria** | <https://streamlit.io/gallery> | apps reais, com código |
| **Fórum** | <https://discuss.streamlit.io> | onde os mantenedores respondem |

**Recomendação:** leia inteira a seção *Concepts → Architecture*. São poucas
páginas e resolvem mais dúvidas que dez horas de vídeo.

### 2.2 Vídeo gratuito

| Curso | Autor | Plataforma | Duração | Nível | Ano | Vale? |
|---|---|---|---|---|---|---|
| [Build 12 Data Science Apps with Python and Streamlit](https://www.freecodecamp.org/news/build-12-data-science-apps-with-python-and-streamlit) | Chanin Nantasenamat (Data Professor) / freeCodeCamp | YouTube | ~3,5 h | iniciante | 2021 | **Sim, com ressalva grande.** É o curso gratuito mais completo que existe, e o mais citado. **Mas é de 2021**: usa `@st.cache` (removido) e ensina deploy no Heroku (que acabou com a camada gratuita). Assista pela estrutura, escreva o código conferindo a API atual. |
| [Streamlit — Web Application in Python (playlist)](https://www.classcentral.com/course/youtube-streamlit-web-application-in-python-97505) | Data Professor | YouTube | ~6 h | iniciante/intermediário | 2020–2023 | **Parcialmente.** Muitos episódios, qualidade desigual, partes desatualizadas. Bom como consulta por tema. |
| [Streamlit Dashboards / Web Apps Tutorials](https://www.youtube.com/playlist?list=PLAX4txYnwreL9FUh1MODUykorMNjM-QVD) | vários | YouTube | variável | intermediário | 2022–2025 | **Sim, por tema.** Não assista em ordem; procure o assunto. |
| [8 days of Streamlit](https://www.youtube.com/playlist?list=PLpdmBGJ6ELUKVcOnN3PrIlCc50MZ7qor6) | comunidade Streamlit | YouTube | ~2 h | iniciante | 2022 | Formato de desafio diário. Bom para manter ritmo. |

### 2.3 Texto e plataformas

| Recurso | Plataforma | Grátis? | Observação |
|---|---|---|---|
| [Python Tutorial: Streamlit](https://www.datacamp.com/tutorial/streamlit) | DataCamp | **tutorial sim**, curso não | atualizado em 31/03/2026 — dos textos mais recentes em inglês |
| [What is Streamlit?](https://www.codecademy.com/article/what-is-streamlit-) | Codecademy | sim | artigo introdutório, bom panorama |
| [Introduction to Streamlit](https://www.mygreatlearning.com/academy/learn-for-free/courses/introduction-to-streamlit) | Great Learning | sim, **com certificado gratuito** | curto e superficial; o certificado é simbólico (ver seção 4) |
| [Streamlit no Class Central](https://www.classcentral.com/subject/streamlit) | Class Central | agregador | 200+ cursos catalogados, com filtro de gratuidade. Útil para procurar por tema |

---

## 3. Francês

O material em francês é **escasso** — bem menos que em português. O que existe,
verificado em 02/09/2026:

| Recurso | Plataforma | Duração | Nível | Ano | Vale? |
|---|---|---|---|---|---|
| [Tutoriel Streamlit Python : Dashboard Complet](https://tech-insider.org/fr/tutoriel-streamlit-python-dashboard-2026/) | tech-insider.org | leitura | iniciante | 2026 | **Sim.** Cobre widgets, cache, chatbot LLM e deploy no Community Cloud. Escrito para versão recente. |
| [Tutoriel Streamlit Python : Tableau de Bord en 12 Étapes](https://tech-insider.org/fr/tutoriel-streamlit-python-tableau-de-bord-2026/) | tech-insider.org | leitura | iniciante | 2026 | **Sim.** Dashboard analítico com pandas e Plotly, com Docker no fim. |
| [Déployer un dashboard interactif avec Streamlit](https://flowt.fr/blog/deployer-dashboard-interactif-streamlit-tutoriel/) | flowt.fr | leitura | iniciante | 2024–2025 | Foco em deploy. Curto. |
| [Cours Streamlit](https://www.udemy.com/fr/topic/streamlit/) | Udemy França | variável | variável | vários | pago; qualidade desigual |

**Conclusão honesta:** se você lê francês mas também lê inglês, vá para o inglês.
O material francês de Streamlit é raso e há pouca coisa além de tutorial
introdutório.

---

## 4. Certificações — a verdade sobre elas

### Existe certificação oficial de Streamlit?

**Não.** Verificado em 02/09/2026: a Streamlit/Snowflake **não emite certificação
de Streamlit**. Quem disser o contrário está vendendo alguma coisa.

O que existe:

| Certificado | Emissor | Grátis? | Vale no mercado? |
|---|---|---|---|
| Conclusão de curso | Great Learning, Asimov, Udemy, Coursera | varia | **Simbólico.** Ninguém contrata por causa dele |
| **SnowPro Core / Advanced** | Snowflake | **pago** (~US$ 175 a 375) | **Sim, para quem trabalha com Snowflake.** Não é de Streamlit, mas cobre SiS |
| Certificados de Python | vários | varia | pouco |

### O que substitui certificado, e funciona

Sendo franco, porque isto importa mais que a tabela acima: **em vaga de dados e
engenharia, ninguém pede certificado de Streamlit. Pedem um link.**

O que efetivamente conta, em ordem de peso:

1. **Uma app publicada e funcionando**, com link (Community Cloud é gratuito).
2. **O repositório**, com README, testes e um `Dockerfile` que sobe.
3. **A arquitetura**: `nucleo/` separado, testes que rodam, tratamento de erro.
   É o que diferencia "fez um tutorial" de "sabe construir software".
4. Um artigo curto explicando uma decisão técnica que você tomou e por quê.

**Sugestão prática:** faça o [Lab 14](70-pratica.md) deste curso, publique no
Community Cloud, ponha o link no currículo. Isso vale mais que qualquer
certificado gratuito de duas horas.

---

## 5. Trilha recomendada, por ponto de partida

### Não sei Python
1. [Curso gratuito de Python](https://wp.asimov.academy/curso-gratuito-python/) (Asimov) ou
   [Curso em Vídeo — Python 3](https://www.youtube.com/playlist?list=PLHz_AreHm4dlKP6QQCekuIPky1CiwmdI6) (Guanabara)
2. Este curso, do [01](01-introducao-leigo.md) ao [07](07-projeto-modelo/)

### Sei Python, nunca fiz interface
1. [Streamlit em menos de 10 minutos](https://www.youtube.com/watch?v=zxA97KcUm1Q) — decidir se quer
2. Este curso, Bloco A ([01](01-introducao-leigo.md) a [07](07-projeto-modelo/))
3. [Concepts → Architecture](https://docs.streamlit.io/develop/concepts/architecture) na documentação oficial
4. Labs 1 a 6 de [70-pratica.md](70-pratica.md)

### Já faço painéis, quero fazer bem
1. [12](12-modelo-de-execucao-e-rerun.md), [13](13-session-state-e-widgets.md), [14](14-cache-e-dados.md) — o modelo
2. [16](16-layout-e-design.md), [17](17-graficos-e-visualizacao.md) — o painel profissional
3. [75-armadilhas.md](75-armadilhas.md) inteiro
4. Labs 6 a 11

### Quero pôr em produção
1. [21](21-backend-dados-e-conexoes.md), [22](22-autenticacao-e-autorizacao.md), [23](23-arquitetura-de-app-real.md)
2. [28](28-deploy-e-operacao.md), [29](29-seguranca.md), [30](30-testes.md)
3. [Tutoriais oficiais](https://docs.streamlit.io/develop/tutorials) de autenticação e conexão
4. Labs 12 a 14

---

## 6. Como avaliar um curso de Streamlit em 30 segundos

Abra e procure por estes sinais. **Cada um é motivo para desconfiar:**

| Sinal | O que significa |
|---|---|
| `@st.cache` | pré-2023. Removido. |
| `st.experimental_rerun`, `st.experimental_memo` | pré-2023 |
| pasta `pages/` sem mencionar `st.navigation` | pré-junho de 2024 |
| deploy no **Heroku** | pré-2022 (acabou a camada gratuita) |
| `use_container_width=True` | pré-2025; hoje é `width="stretch"` |
| não menciona `session_state` | não trata o problema central |
| não menciona cache | vai ensinar a fazer app lento |

**Sinais de que o curso é atual e sério:**

- fala de `st.fragment`, `st.navigation`, `st.dialog`;
- menciona `st.login()` ou autenticação de verdade;
- mostra `AppTest` ou qualquer forma de teste;
- diz **quando não usar** Streamlit;
- trata do estado vazio e do tratamento de erro.

---

## 7. Onde acompanhar o que muda

| Fonte | Para quê |
|---|---|
| [Notas de versão](https://docs.streamlit.io/develop/quick-reference/release-notes) | o que mudou, a cada 2–4 semanas |
| [Fórum oficial](https://discuss.streamlit.io) | anúncios e dúvidas respondidas por mantenedores |
| [GitHub — releases](https://github.com/streamlit/streamlit/releases) | o detalhe técnico |
| [GitHub — issues](https://github.com/streamlit/streamlit/issues) | saber se o seu bug é conhecido |
| [Blog do Streamlit](https://blog.streamlit.io) | tutoriais oficiais e casos |
| `streamlit docs` (no terminal) | abre a documentação da sua versão |

---

## Autoteste

1. Existe certificação oficial de Streamlit? O que existe no lugar?
2. Qual é o recurso de aprendizado mais subestimado, e por quê?
3. Por que o curso mais completo em inglês (freeCodeCamp) precisa de ressalva?
4. Cite quatro sinais de que um curso de Streamlit está desatualizado.
5. Qual é a limitação honesta do material em português? O que fazer a respeito?
6. O que vale mais que certificado numa vaga, em ordem de peso?
7. Monte a sua trilha a partir do seu ponto de partida atual.

---

## Fontes consultadas (02/09/2026)

Todas verificadas na web em 02/09/2026:

- Documentação oficial — <https://docs.streamlit.io>, <https://docs.streamlit.io/develop/tutorials>
- freeCodeCamp — <https://www.freecodecamp.org/news/build-12-data-science-apps-with-python-and-streamlit>
- Class Central, catálogo de Streamlit — <https://www.classcentral.com/subject/streamlit>
- DataCamp, tutorial atualizado em 31/03/2026 — <https://www.datacamp.com/tutorial/streamlit>
- Great Learning — <https://www.mygreatlearning.com/academy/learn-for-free/courses/introduction-to-streamlit>
- Hashtag Treinamentos — <https://www.hashtagtreinamentos.com/streamlit-python>
- Asimov Academy — <https://www.asimov.academy/trilhas/dashboards-interativos-com-python/>, <https://wp.asimov.academy/curso-gratuito-python/>
- Medium, curso em português atualizado em fev/2026 — <https://medium.com/@habbema/curso-completo-de-streamlit-parte-1-e7fed18d010b>
- tech-insider.org (francês, 2026) — <https://tech-insider.org/fr/tutoriel-streamlit-python-dashboard-2026/>
- flowt.fr (francês) — <https://flowt.fr/blog/deployer-dashboard-interactif-streamlit-tutoriel/>
- Udemy França — <https://www.udemy.com/fr/topic/streamlit/>
