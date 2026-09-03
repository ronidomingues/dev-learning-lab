# 16 · Layout e design — o que faz um painel parecer profissional

> **Nível:** intermediário · **Escrito em:** 02/09/2026 · Streamlit 1.63.0
> Este arquivo responde diretamente à pergunta **"como faço um dashboard
> profissional?"**. Complementos: [17-graficos](17-graficos-e-visualizacao.md),
> [18-tabelas](18-tabelas-e-edicao.md), [20-tema](20-tema-e-identidade-visual.md).

Painel amador e painel profissional raramente diferem em tecnologia. Diferem em
**decisões**. Este arquivo lista as decisões, na ordem em que se tomam.

---

## 1. Antes de escrever uma linha: as três perguntas

Nenhuma quantidade de CSS conserta um painel que erra estas três.

**1. Quem abre isto, e quantas vezes por semana?**
Um diretor que abre segunda de manhã quer **quatro números e uma tendência**. Um
analista que fica o dia todo quer **filtro fino e exportação**. São painéis
diferentes. Fazer um só que sirva aos dois produz um que não serve a nenhum.

**2. Que decisão esta tela apoia?**
Se a resposta for "nenhuma, é só para acompanhar", o painel vai morrer em três
meses — e tudo bem saber disso antes. Se for "decidir se aumentamos o estoque",
então **estoque × demanda** é o gráfico principal, e o resto é contexto.

**3. Qual é a pergunta de cada bloco?**
Todo bloco responde a **uma** pergunta, escrita no título. "Receita por dia" é uma
pergunta respondida. "Análise temporal" não é nada.

> **Teste dos cinco segundos.** Mostre a tela a alguém por cinco segundos e
> pergunte: como estamos? Se a pessoa não souber, a hierarquia está errada — não
> a paleta.

---

## 2. A anatomia de um painel que funciona

```
┌──────────┬────────────────────────────────────────────────────────┐
│          │  Título · período · última atualização                 │
│          ├────────────┬────────────┬────────────┬─────────────────┤
│ FILTROS  │  KPI 1     │  KPI 2     │  KPI 3     │  KPI 4          │
│          │  + Δ       │  + Δ       │  + Δ       │  + Δ            │
│ período  ├────────────┴────────────┴──┬─────────┴─────────────────┤
│ segmento │                            │                           │
│ canal    │  Evolução no tempo         │  Composição               │
│ status   │  (o gráfico principal)     │  (o contexto)             │
│          ├────────────────────────────┼───────────────────────────┤
│ [limpar] │  Ranking A                 │  Ranking B                │
│          ├────────────────────────────┴───────────────────────────┤
│          │  ▸ Detalhe (recolhido) — tabela + exportar             │
└──────────┴────────────────────────────────────────────────────────┘
```

**A regra de ouro do layout:** *números → tendência → composição → detalhe*.
Nessa ordem, de cima para baixo. Quem manda para no primeiro nível; quem executa
desce.

Traduzido para código:

```python
st.set_page_config(layout="wide")     # painel precisa de largura

f = barra_de_filtros()                 # 1. filtros na lateral

cabecalho(f)                           # 2. contexto: o quê, quando, comparado a quê
linha_de_kpis(kpis)                    # 3. os números

esq, dir_ = st.columns([2, 1], gap="medium")
with esq:  grafico_serie(...)          # 4. a tendência (o maior)
with dir_: grafico_composicao(...)     # 5. o contexto

a, b = st.columns(2, gap="medium")     # 6. rankings
with st.expander("Ver os N registros"):
    tabela(...)                        # 7. detalhe, recolhido
```

É exatamente a estrutura de
[`07-projeto-modelo/paginas/painel.py`](07-projeto-modelo/paginas/painel.py).

---

## 3. Filtros: onde ficam e como se comportam

**Regra:** filtro que vale para a página inteira vai para a **barra lateral**.
Filtro que vale só para um bloco fica **dentro do bloco**. Misturar os dois
lugares é o que faz o usuário perder de vista o que está vendo.

```python
with st.sidebar:
    st.markdown("#### Filtros")
    st.segmented_control("Período", ["7 dias", "30 dias", "90 dias", "12 meses"],
                         default="90 dias", key="f_atalho", bind="query-params",
                         label_visibility="collapsed", width="stretch")
    st.date_input("Intervalo", key="f_intervalo", format="DD/MM/YYYY")
    st.multiselect("Segmento", segmentos, key="f_segmento", bind="query-params")
    st.divider()
    st.caption(f"Período: {ini:%d/%m/%Y} a {fim:%d/%m/%Y}")
```

Cinco decisões escondidas aí, todas deliberadas:

1. **Atalhos de período antes do seletor de datas.** 90% das vezes o usuário quer
   "últimos 30 dias", não escolher duas datas.
2. **`bind="query-params"`** — o link carrega os filtros. Isto transforma o painel
   em algo compartilhável.
3. **`label_visibility="collapsed"`** onde o rótulo é redundante — economiza altura.
4. **O período escolhido escrito por extenso, embaixo.** Confirma o recorte sem o
   usuário reconferir os campos.
5. **Chaves prefixadas (`f_`)** — habilita "limpar todos os filtros" em três linhas.

### Quantos filtros?

- **até 4:** barra lateral aberta;
- **5 a 8:** barra lateral, com os menos usados dentro de um `expander`;
- **mais de 8:** o problema não é layout — é que você está tentando servir a
  públicos diferentes na mesma tela. Separe em duas páginas.

---

## 4. KPIs: o bloco mais copiado e o mais malfeito

Um cartão de indicador precisa de **quatro** coisas. Faltando qualquer uma, ele
informa menos do que parece:

| Elemento | Sem ele... |
|---|---|
| **rótulo** claro | ninguém sabe o que é |
| **valor** formatado no padrão do país | "1234567.89" não se lê |
| **comparação** (Δ contra o quê) | número sem base não diz se é bom ou ruim |
| **definição** (`help=`) | duas pessoas calculam diferente e brigam na reunião |

```python
st.metric(
    "Receita", brl_compacto(k.receita),
    delta=percentual(k.var_receita),
    delta_description="vs. período anterior",
    border=True,
    icon=":material/payments:",
    chart_data=serie_30_dias, chart_type="area",
    help="Soma dos pedidos, excluindo cancelados. Fonte: tabela `pedidos`.",
)
```

**Cinco erros de KPI, em ordem de frequência:**

1. **Sem comparação.** "Receita: R$ 1,2 mi" não informa nada. Contra o mês
   anterior? Contra a meta? Contra o mesmo mês do ano passado? Escolha e diga.
2. **`+100%` contra zero.** Se a base é zero, a variação é indefinida — mostre
   `—`, não um número inventado. (É o que `percentual(None)` faz no projeto-modelo.)
3. **Verde/vermelho errado.** Para custo, churn, tempo de resposta,
   **subir é ruim**: `delta_color="inverse"`. Errar isso faz o painel mentir.
4. **Precisão falsa.** "R$ 1.234.567,89" num cartão executivo. Use
   "R$ 1,2 mi" no cartão e o valor exato no `help=` ou no rodapé.
5. **Oito KPIs.** Ninguém compara oito números. **Quatro** é o teto; seis é
   exceção. O que não couber vira gráfico.

---

## 5. Grade, espaço e alinhamento

```python
esq, dir_ = st.columns([2, 1], gap="medium", vertical_alignment="top")
```

**Proporções que funcionam:** `[2,1]`, `[3,1]`, `[1,1]`, `[1,1,1]`, `[1,1,1,1]`.
Proporções esquisitas (`[7,3,2]`) parecem acidente — porque geralmente são.

**Bordas: use.** `st.container(border=True)` e `st.metric(border=True)` agrupam
visualmente e custam nada. Um painel sem bordas parece uma lista de coisas; com
bordas, parece um painel.

```python
with st.container(border=True):
    st.markdown("**Receita por dia**")
    st.plotly_chart(fig, width="stretch")
```

**Espaço vertical é conteúdo.** `st.space("small"|"medium"|"large")` e
`st.divider()` separam seções. Painel apertado cansa; painel espaçado respira.

**Alinhamento.** `vertical_alignment="center"` em colunas com alturas diferentes
evita o efeito "escada". Para uma linha de botões, `st.container(horizontal=True)`
é mais limpo que `st.columns`.

---

## 6. Os quatro estados de toda tela

Isto é o que separa protótipo de produto. **Toda** tela tem quatro estados, e a
maioria dos painéis só implementa um.

| Estado | O que mostrar | Comando |
|---|---|---|
| **carregando** | esqueleto ou spinner com o que está sendo feito | `st.spinner`, `st.skeleton`, `st.status` |
| **vazio** | por que está vazio **e o que fazer** | `st.info` + sugestão |
| **erro** | o que falhou, em português, e o próximo passo | `st.error(title=..., icon=...)` |
| **cheio** | o painel | — |

```python
if erro:
    st.error("Não consegui falar com o banco.",
             title="Dados indisponíveis", icon=":material/cloud_off:")
    st.caption("Tente de novo em alguns minutos. Se persistir, avise a equipe de dados.")
    st.stop()

if df.empty:
    st.info("Nenhum pedido bate com esses filtros. "
            "Tente ampliar o período ou limpar o filtro de canal.",
            icon=":material/filter_alt_off:")
    st.stop()
```

**Estado vazio útil diz o que fazer.** "Sem dados" é inútil; "sem dados — amplie o
período ou limpe o filtro de canal" é ajuda.

---

## 7. Densidade: quanto cabe

| Público | Densidade | Como |
|---|---|---|
| executivo | **baixa** | 4 KPIs, 2 gráficos, nada mais na primeira tela |
| gerencial | média | 4 KPIs, 4 gráficos, tabela recolhida |
| operacional | **alta** | tabela grande, filtros, ações em massa |

**A dobra importa.** O que exige rolagem é lido por metade das pessoas. Na
primeira tela: título, período, KPIs e **um** gráfico. O resto pode descer.

**Abas versus rolagem.** Use `st.tabs` quando os blocos são **alternativas**
("por produto" × "por região"); use rolagem quando são **sequência** (resumo →
detalhe). Aba escondendo informação que deveria ser comparada é erro.

---

## 8. Texto: o que escrever e o que apagar

- **Título do bloco = a pergunta respondida.** "Quanto entrou por dia", não
  "Série temporal".
- **`st.caption` para unidade, fonte e recorte.** "Valores em R$, sem impostos.
  Fonte: ERP, atualizado às 06h."
- **Apague o jargão do banco.** `qtd_ped_liq` na tela é um erro de respeito com o
  usuário. Renomeie na camada de apresentação.
- **Datas em `DD/MM/AAAA`.** `2026-09-02` num painel brasileiro é preguiça.
- **Números no padrão do país.** `R$ 1.234,56`, não `R$ 1,234.56`. E não use
  `locale.setlocale` — ele é global, não é seguro entre threads (e o Streamlit
  usa threads), e o locale pode não existir no contêiner. Formate à mão; ver
  [`ui/formatos.py`](07-projeto-modelo/ui/formatos.py).

---

## 9. Acessibilidade — o mínimo que não é negociável

Não é enfeite: é a diferença entre um painel que 100% da empresa lê e um que 92%
lê.

1. **Nunca só a cor.** Cerca de 8% dos homens têm alguma deficiência de visão de
   cores. Onde a cor informa, tem de haver **também** texto, ícone ou forma.
   (No projeto-modelo, a dispersão usa `symbol=` além de `color=` exatamente por
   isso.)
2. **Contraste.** Texto sobre fundo precisa de pelo menos 4,5:1; marca de gráfico,
   3:1. Não confie no olho — meça.
3. **Não desative o zoom** e não fixe fonte em pixels minúsculos.
4. **Rótulo em todo widget.** Se você usa `label_visibility="collapsed"`, o rótulo
   ainda existe para o leitor de tela — mantenha um texto real, não `""`.
5. **Tabela como alternativa ao gráfico.** Quem usa leitor de tela não "vê" o
   gráfico. Um `st.expander("Ver os dados")` com a tabela resolve.

---

## 10. Cinco toques baratos que mudam a percepção

Em ordem de retorno sobre esforço:

1. **Barra lateral com fundo próprio** (`[theme.sidebar]`). Separa "controles" de
   "conteúdo". Cinco linhas de configuração, e o painel deixa de parecer protótipo.
2. **`st.logo()`** com a marca da empresa no topo da lateral.
3. **`border=True`** em KPIs e contêineres.
4. **Ícones do Material** (`:material/monitoring:`) em vez de emoji. Emoji tem
   estilo diferente em cada sistema operacional; ícone é consistente.
5. **`toolbarMode = "minimal"`** no `config.toml` — some o menu de desenvolvedor
   da tela de quem só consome o painel.

E um que **não** vale: injetar CSS com `st.markdown(..., unsafe_allow_html=True)`
para mexer em classes internas do Streamlit. Elas mudam entre versões, sem aviso,
e o seu painel quebra numa atualização de rotina. Se precisar mesmo, use
`st.container(key="x")` — que gera a classe estável `st-key-x` — e estilize a
partir dela. Ver [20-tema-e-identidade-visual.md](20-tema-e-identidade-visual.md).

---

## 11. Celular

Streamlit é responsivo por padrão: as colunas empilham em tela estreita. O que
quebra:

- **tabela larga** — vira rolagem horizontal. Use `column_order` para mostrar
  menos colunas, e `pinned=True` na coluna-chave;
- **8 KPIs** — viram 8 linhas empilhadas;
- **barra lateral** — no celular ela começa fechada; se o painel só faz sentido
  filtrado, ponha um resumo do filtro no corpo.

Se celular for um caso de uso real, faça uma **página específica** com 2 KPIs e um
gráfico. Tentar servir desktop e celular na mesma tela produz uma tela ruim nos
dois.

---

## 12. Checklist do painel profissional

**Conteúdo**
- [ ] Sei quem abre isto e que decisão apoia.
- [ ] Todo bloco tem um título que é uma pergunta respondida.
- [ ] Todo KPI tem comparação e definição (`help=`).
- [ ] Nenhum KPI mostra `+100%` contra base zero.
- [ ] Indicadores em que "subir é ruim" usam `delta_color="inverse"`.

**Layout**
- [ ] `layout="wide"`.
- [ ] Filtros globais na lateral; filtros locais dentro do bloco.
- [ ] Primeira tela: título, período, KPIs e um gráfico.
- [ ] Detalhe em `expander` ou aba.
- [ ] Bordas agrupando os blocos.

**Estados**
- [ ] Carregando tratado.
- [ ] Vazio tratado, **com sugestão do que fazer**.
- [ ] Erro tratado, em português, sem traceback na tela do usuário.

**Forma**
- [ ] Datas em DD/MM/AAAA; números com ponto de milhar e vírgula decimal.
- [ ] Nenhum nome de coluna do banco visível.
- [ ] Paleta validada; a cor nunca é o único diferenciador.
- [ ] Tema com barra lateral distinta; `toolbarMode = "minimal"`.

**Compartilhamento**
- [ ] Filtros ligados à URL (`bind="query-params"`).
- [ ] Botão de exportar o recorte.
- [ ] Rodapé com fonte do dado e horário da última atualização.

---

## Autoteste

1. Quais são as três perguntas antes de escrever a primeira linha?
2. Descreva a ordem canônica dos blocos de um painel e por que ela é essa.
3. Quatro elementos de um KPI bem-feito. O que falta em "Receita: R$ 1,2 mi"?
4. Quando `delta_color="inverse"`? Dê dois indicadores.
5. Quais são os quatro estados de uma tela? O que um estado vazio útil precisa ter
   além da frase "sem dados"?
6. Onde ficam os filtros globais e onde ficam os locais? Por quê?
7. Por que não usar `locale.setlocale` para formatar moeda numa app Streamlit?
8. Por que injetar CSS mirando classes internas do Streamlit é má ideia, e qual é
   a alternativa oficial?
9. Cite três coisas que quebram no celular e o que fazer.
