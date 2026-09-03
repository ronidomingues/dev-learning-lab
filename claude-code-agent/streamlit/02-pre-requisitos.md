# 02 · Pré-requisitos

> **Nível:** iniciante · **Escrito em:** 02/09/2026

Streamlit tem fama de "não precisa saber nada". É meia verdade: para fazer a
primeira tela, não precisa mesmo. Para fazer um painel que alguém use todo dia,
ou um site com backend, precisa de bastante coisa — e a maior parte dela **não é
Streamlit**, é Python, dados e web.

Este arquivo separa os dois casos com honestidade.

---

## 1. Conhecimento

### Indispensável

| O quê | Quanto | Por que | Onde aprender |
|---|---|---|---|
| **Python básico** | variáveis, `if`, `for`, funções, listas e dicionários, `import` | O script é Python. Não tem como escapar. | [Curso em Vídeo — Python 3 (Guanabara)](https://www.youtube.com/playlist?list=PLHz_AreHm4dlKP6QQCekuIPky1CiwmdI6), gratuito, PT |
| **Ler mensagem de erro** | achar o arquivo, a linha, e o nome da exceção | O Streamlit mostra o traceback na tela. Quem lê, resolve em 1 min; quem não lê, perde a tarde. | qualquer curso de Python; treine de propósito |
| **Terminal** | `cd`, `ls`/`dir`, rodar um comando, variável de ambiente | Instalar e rodar são comandos. | [`variaveis-de-ambiente-e-segredos`](../variaveis-de-ambiente-e-segredos/00-MAPA.md) |

Isso é o suficiente para o [04-como-comecar.md](04-como-comecar.md) e para o
[06-exemplos.md](06-exemplos.md).

### Ajuda muito (e é o que separa "funciona" de "é bom")

| O quê | Por que | Onde aprender |
|---|---|---|
| **pandas** | 95% de um painel é agrupar, filtrar e somar um DataFrame. Se você briga com `groupby`, vai brigar com o Streamlit por engano. | [`estatistica-descritiva`](../estatistica-descritiva/00-MAPA.md); docs do pandas |
| **SQL** | Filtrar no banco e não em Python é a diferença entre 0,2 s e 40 s. | [`sql`](../sql/00-MAPA.md) |
| **Git** | Deploy no Streamlit Community Cloud é *literalmente* um repositório no GitHub. Sem Git, não tem deploy grátis. | [`commits-assinados`](../commits-assinados/00-MAPA.md) |
| **Ambiente virtual** (`venv`, `uv`) | Instalar tudo no Python do sistema é a origem de metade dos problemas de instalação. | [`uv-python`](../uv-python/00-MAPA.md) |
| **Noções de HTTP e navegador** | Entender o que é porta, WebSocket, proxy reverso — vira obrigatório no dia do deploy. | [`portas-de-rede`](../portas-de-rede/00-MAPA.md), [`hospedagem-de-aplicacoes-web`](../hospedagem-de-aplicacoes-web/00-MAPA.md) |
| **Docker** | O jeito mais previsível de colocar em produção. | [`curso-docker`](../curso-docker/00-indice.md) |
| **Uma biblioteca de gráficos** (Plotly ou Altair) | Os gráficos nativos do Streamlit resolvem o rascunho; painel bom precisa de controle fino. | [17-graficos-e-visualizacao.md](17-graficos-e-visualizacao.md) |

### Explicitamente **não** necessário

Isto derruba muita gente antes de começar, então vale dizer:

- **HTML, CSS e JavaScript não são necessários.** Ajudam para ajustes finos e
  são obrigatórios para escrever um componente customizado — só isso.
- **React não é necessário** (salvo componente customizado).
- **Nenhum framework web** (Flask, Django, FastAPI). O Streamlit já é o servidor.
- **Frontend/backend como disciplina** não é pré-requisito — mas o
  [23-arquitetura-de-app-real.md](23-arquitetura-de-app-real.md) vai te ensinar a
  separar as duas coisas mesmo assim, porque é o que salva o projeto no mês 3.

---

## 2. Ambiente

### Mínimo real

| Item | Mínimo | Recomendado | Observação |
|---|---|---|---|
| **Python** | 3.10 | 3.12 ou 3.13 | Streamlit 1.63.0 declara `Requires-Python: >=3.10`. 3.9 **não** roda mais. |
| **Memória** | 2 GB livres | 8 GB | O que come memória é o seu DataFrame, não o Streamlit. |
| **Disco** | ~700 MB | 2 GB | Streamlit + pandas + pyarrow + numpy passa de meio giga. |
| **Sistema** | Linux, macOS 12+, Windows 10+ | qualquer um dos três | Windows nativo funciona; WSL2 funciona melhor. |
| **Navegador** | Chrome/Edge/Firefox/Safari atuais | — | Internet Explorer, obviamente, não. |
| **Internet** | para instalar | — | Depois de instalado, roda offline. |

### Contas em serviço

Nenhuma é obrigatória para aprender:

| Serviço | Precisa? | Custo | Cartão? |
|---|---|---|---|
| GitHub | só para publicar no Community Cloud | grátis | não |
| Streamlit Community Cloud | só para publicar de graça | grátis | não |
| Snowflake | só para *Streamlit in Snowflake* | pago, por crédito | sim |
| Provedor OIDC (Google/Entra/Auth0) | só para `st.login()` | tem camada grátis | varia |

Detalhes e preços com data em
[80-custos-e-licencas.md](80-custos-e-licencas.md).

---

## 3. Tempo realista até cada nível

Números da minha experiência ensinando e revisando código alheio, supondo
**Python básico já sabido**. Se você é otimista, some 40%.

| Nível | O que você consegue fazer | Tempo dedicado |
|---|---|---|
| **Primeira tela** | um script com título, filtro e gráfico | **1 a 2 horas** |
| **Painel que funciona** | KPIs, filtros, três gráficos, dados de um CSV | **1 a 2 dias** |
| **Painel que alguém usa todo dia** | cache correto, estado vazio tratado, tema, layout que cabe na tela, dados de um banco | **1 a 2 semanas** |
| **Site com backend** | login, papéis, CRUD, migração, transação, testes, deploy em contêiner | **3 a 6 semanas** |
| **Produção com muitos usuários** | observabilidade, réplicas, proxy reverso, gestão de memória, orçamento de custo | **2 a 4 meses** |
| **Entender por dentro** | modelo de execução, protocolo, hashing do cache, escrever componente customizado | **3 a 6 meses** |

Onde as pessoas travam, em ordem de frequência:

1. **"Meu app está lento."** Não entenderam o rerun nem o cache. → [14](14-cache-e-dados.md), [15](15-fragments-e-performance.md)
2. **"O botão não funciona / o valor some."** Não entenderam o `session_state`. → [13](13-session-state-e-widgets.md)
3. **"Funciona na minha máquina."** Não fixaram versão nem usaram contêiner. → [03](03-instalacao.md), [28](28-deploy-e-operacao.md)
4. **"Ficou feio."** Não é falta de CSS; é falta de decisão de layout. → [16](16-layout-e-design.md)

---

## 4. Rota de resgate — o que fazer se faltar um pré-requisito

**Se falta Python:** não comece por Streamlit. Sério. Duas semanas de Python
básico economizam dois meses de frustração, porque quase todo erro que você vai
ver é erro de Python aparecendo dentro do Streamlit. Faça o mínimo: tipos,
funções, listas, dicionários, `for`, `if`, `import`, ler traceback.

**Se falta pandas:** comece assim mesmo, com dados pequenos e um CSV. Aprenda
`read_csv`, `groupby`, `merge`, `sort_values` e filtro booleano — nessa ordem.
Cinco funções cobrem quase tudo de painel.

**Se falta terminal:** aprenda só quatro comandos (`cd`, `ls`, `python -m venv`,
`pip install`) e siga. O resto vem por osmose.

**Se falta permissão de administrador na máquina** (empresa, laboratório): você
**não precisa** dela. Instale no diretório do usuário (`pip install --user`) ou,
melhor ainda, comece pelo GitHub Codespaces, que não instala nada localmente.
O [03-instalacao.md](03-instalacao.md) tem a seção inteira sobre isso.

**Se falta máquina decente:** use um ambiente na nuvem. Codespaces dá 60 h/mês
grátis; o Community Cloud roda o app publicado. Streamlit é leve no cliente — o
peso está no servidor.

**Se falta tempo:** o roteiro de 1 hora está no
[00-MAPA.md](00-MAPA.md). Ele leva do zero a um painel funcionando e para por aí,
sem culpa.

---

## 5. Checklist antes de ir para a instalação

```bash
python3 --version     # precisa dizer 3.10 ou mais
```

- [ ] Sei o que é uma função em Python e sei chamar uma.
- [ ] Sei abrir um terminal e navegar até uma pasta.
- [ ] Tenho ≥ 2 GB de disco livres.
- [ ] Sei o que vou querer mostrar na tela (nem que seja um CSV bobo).

Faltando algum, volte à rota de resgate. Todos marcados, vá para
[03-instalacao.md](03-instalacao.md).

---

## Autoteste

1. Qual é a versão mínima de Python para o Streamlit 1.63.0, e onde essa
   informação está escrita de forma verificável?
2. Cite duas coisas que **não** são pré-requisito e que muita gente acha que são.
3. Por que saber SQL muda o desempenho de um painel, se o Streamlit é Python?
4. Você não tem permissão de administrador na máquina do trabalho. Quais são as
   suas duas opções?
5. Quanto tempo, honestamente, até um painel que alguém usa todo dia? E até um
   site com login e CRUD?
6. Quais são os quatro pontos onde as pessoas mais travam, e qual arquivo trata
   de cada um?
