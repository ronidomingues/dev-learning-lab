# 17 · Gráficos — escolher a forma, validar a cor, ajustar a marca

> **Nível:** intermediário · **Escrito em:** 02/09/2026 · Streamlit 1.63.0,
> Plotly 7.0.0, Altair 5.x
> Os números de validação de paleta deste arquivo foram **medidos**, não
> estimados — o método está na seção 4.

Gráfico ruim quase nunca é falta de biblioteca. É forma errada, cor escolhida por
gosto, e ruído que ninguém apagou. Este arquivo trata das três coisas, nessa
ordem — e **cor vem por último**, de propósito.

---

## 1. Qual biblioteca usar

| Biblioteca | Já vem instalada? | Use quando |
|---|---|---|
| **nativos** (`st.line_chart`, `st.bar_chart`, `st.area_chart`, `st.scatter_chart`) | sim | rascunho, exploração, protótipo |
| **Plotly** | não (`pip install plotly`) | painel entregue: hover rico, seleção, controle fino |
| **Altair / Vega-Lite** | **sim** (dependência do Streamlit) | gramática declarativa, gráficos ligados entre si |
| **matplotlib** | não | figura estática, artigo, relatório em PDF |
| **pydeck** | sim | mapa 3D, grande volume geoespacial |
| **graphviz / `st.mermaid_chart`** | mermaid é nativo (1.59+) | diagrama, fluxo, hierarquia |

**Recomendação prática:** comece nos nativos, mude para **Plotly** quando o painel
for para alguém. E **escolha uma só** — painel com três bibliotecas tem três
estilos de tooltip, três fontes e três paletas, e parece remendado. Isso é
visível para o usuário mesmo quando ele não sabe nomear o que incomoda.

---

## 2. Escolher a forma: o trabalho manda no tipo

Pergunte **qual é o trabalho do dado**, não "que gráfico é bonito".

| O trabalho do dado | Forma | Nunca |
|---|---|---|
| um número que resume tudo | **nenhum gráfico** — `st.metric` | um gráfico de um ponto só |
| mudança ao longo do tempo | linha (ou área, se for acumulado) | barras para série longa |
| comparar magnitudes entre categorias | **barra**, horizontal se os rótulos forem longos | pizza |
| parte do todo, 2 ou 3 fatias | barra empilhada 100% | pizza com 9 fatias |
| relação entre duas medidas | dispersão | linha ligando pontos sem ordem |
| distribuição | histograma, ou caixa (*boxplot*) | média sozinha |
| duas dimensões categóricas × um valor | mapa de calor | 3D |
| fluxo entre estágios | funil, ou barras ordenadas | qualquer coisa animada |

### As três regras que mais se quebram

**1. Nunca dois eixos Y.** É o erro nº 1 em painel corporativo. Duas escalas
diferentes no mesmo desenho permitem "provar" qualquer correlação, dependendo de
onde você corta os eixos. Se são duas medidas de grandezas diferentes: **dois
gráficos empilhados**, ou indexe as duas a uma base comum (`= 100` no primeiro
período).

**2. Nunca pizza com mais de três fatias.** O olho compara comprimento bem e
ângulo mal. Com 4+ categorias, a barra ordenada é estritamente melhor. Pizza só
se justifica em "dois pedaços, e o ponto é que um é quase tudo".

**3. Barra sempre começa no zero.** Cortar o eixo Y de um gráfico de barras
multiplica visualmente a diferença. Em gráfico de **linha**, cortar é legítimo
(o que interessa é a variação) — em barra, não, porque a barra codifica magnitude
pelo comprimento.

---

## 3. Ruído: o que apagar

Configuração padrão de qualquer biblioteca desenha coisas que não informam. A
diferença entre gráfico de tutorial e gráfico de produto está aqui.

**Apague:**
- grade vertical (quase sempre inútil);
- moldura em volta do desenho;
- fundo colorido;
- legenda quando só há uma série (o título já a nomeia);
- rótulo de eixo que repete o título ("Data" embaixo de um eixo de datas);
- casas decimais que ninguém usa;
- número em cima de **todo** ponto.

**Mantenha:**
- grade horizontal fraca (ajuda a ler valores);
- eixo X com uma linha discreta;
- **hover** com o valor exato — o gráfico dá a forma, o hover dá o número;
- rótulo direto nas 1 ou 2 séries que importam.

Um único lugar decide isso para o painel inteiro:

```python
def layout_padrao(fig, altura=320):
    fig.update_layout(
        height=altura,
        margin=dict(l=8, r=8, t=28, b=8),
        showlegend=False,
        hovermode="x unified",
        xaxis_title=None, yaxis_title=None,
        separators=",.",                      # ← decimal vírgula, milhar ponto
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False, showline=True,
                     linecolor="rgba(128,128,128,.25)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,.15)",
                     zeroline=False)
    return fig
```

`separators=",."` é o parâmetro que mais falta em painel brasileiro feito com
Plotly. Sem ele o gráfico mostra `1,234.56` e o cartão ao lado mostra `1.234,56`.

E o hover, que é onde o valor exato mora:

```python
fig.update_traces(
    hovertemplate="%{x|%d/%m/%Y}<br><b>R$ %{y:,.2f}</b><extra></extra>")
```

O `<extra></extra>` remove a caixinha lateral com o nome do traço, que o Plotly
desenha por padrão e quase nunca ajuda.

---

## 4. Cor: computável, portanto compute

Aqui está a parte que quase todo material sobre "dashboards bonitos" erra: trata
paleta como gosto. **Não é.** As propriedades que fazem uma paleta funcionar são
mensuráveis, e existe validação automática.

### As quatro funções da cor

| Função | Quando | Regra |
|---|---|---|
| **categórica** (identidade) | séries distintas: produtos, canais | matizes fixos, **em ordem fixa**, nunca reciclados |
| **sequencial** (magnitude) | mapa de calor, mapa coroplético | **um** matiz, claro → escuro |
| **divergente** (polaridade) | variação, desvio da meta | **dois** matizes + cinza neutro no meio |
| **estado** (bom/alerta/grave/crítico) | semáforo, alarme | reservada; nunca reusada como "série 4"; sempre com ícone e texto |

**Nunca arco-íris para magnitude.** A ordem das cores do arco-íris não corresponde
à ordem dos números, e o olho inventa fronteiras onde os dados são contínuos.

### O que se mede numa paleta categórica

1. **faixa de luminosidade** — todas as cores numa faixa parecida, para nenhuma
   sumir no fundo nem gritar;
2. **piso de croma** — nada tão dessaturado que vire cinza;
3. **separação sob daltonismo** — as cores continuam distinguíveis em
   deuteranopia, protanopia e tritanopia (ΔE OKLab ≥ 8);
4. **separação para visão normal** — pares adjacentes com ΔE ≥ 15;
5. **contraste com o fundo** — pelo menos 3:1.

### Um caso real, deste curso

A primeira versão do [projeto-modelo](07-projeto-modelo/) usava esta paleta,
escolhida por gosto:

```python
["#2563eb", "#0891b2", "#7c3aed", "#c2410c", "#15803d", "#be123c", "#a16207"]
```

Validada, ela **reprova**:

```
[FAIL] separação sob daltonismo:
       #be123c (vermelho) ↔ #15803d (verde) — ΔE 1,4 em deuteranopia
```

Traduzindo: para cerca de 8% dos homens, **as duas séries têm a mesma cor**. O
gráfico ficava ilegível, e ninguém perceberia sem medir — inclusive eu não
percebi, e por isso o exemplo está aqui.

A paleta corrigida, que passa em todos os cinco testes na ordem em que está:

```python
PALETA_CLARA = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
                "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
PALETA_ESCURA = ["#3987e5", "#d95926", "#199e70", "#c98500",
                 "#d55181", "#008300", "#9085e9", "#e66767"]
```

Medições (pares adjacentes, OKLab ×100): pior ΔE sob daltonismo **9,1** no claro
e **8,4** no escuro; pior ΔE para visão normal **19,6** e **19,3**.

**Dois detalhes que parecem picuinha e não são:**

- **A ordem faz parte da garantia.** As cores foram ordenadas para que os pares
  **vizinhos** se separem. Reordenar por gosto quebra a validação.
- **A versão escura não é a clara invertida.** São os mesmos oito matizes,
  reescalonados para o fundo escuro. Clarear tudo automaticamente produz cores
  que estouram.

### O limite honesto: dispersão precisa de mais que cor

Numa linha ou barra empilhada, o olho compara **vizinhos**. Numa dispersão, todas
as séries aparecem juntas e todos os pares importam. Aí a conta muda: **três**
cores desta paleta separam todos os pares; a partir da quarta, não separam.

A resposta não é procurar uma paleta mágica — é acrescentar um **segundo canal**:

```python
# Dispersão com 5 categorias: cor + FORMA do marcador
fig = px.scatter(df, x="pedidos", y="receita",
                 color="segmento", symbol="segmento",     # ← o segundo canal
                 color_discrete_sequence=PALETA_CLARA)
fig.update_traces(marker=dict(size=8,
                              line=dict(width=1, color="rgba(255,255,255,.6)")))
```

Ou reduza: as 3 maiores categorias e "Outros". Painel com 9 séries coloridas não
é lido por ninguém — nem por quem enxerga todas as cores.

### Onde declarar a paleta no Streamlit

Desde a 1.54, no **tema** — assim os gráficos nativos e qualquer figura com
`theme="streamlit"` herdam sem repetição:

```toml
# .streamlit/config.toml
[theme]
chartCategoricalColors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
                          "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
chartSequentialColors  = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5",
                          "#256abf", "#184f95", "#0d366b"]

[theme.dark]
chartCategoricalColors = ["#3987e5", "#d95926", "#199e70", "#c98500",
                          "#d55181", "#008300", "#9085e9", "#e66767"]
```

E, para saber em qual tema o usuário está (para escolher a paleta em código
Plotly):

```python
escuro = st.context.theme.type == "dark"
```

---

## 5. Marcas: os detalhes de desenho

- **linha**: 2 px. Mais fino some; mais grosso esconde o dado.
- **marcador**: ≥ 8 px, senão não dá para acertar com o mouse.
- **barra**: cantos levemente arredondados na ponta do dado, quadrados na base.
- **fatias adjacentes**: 2 px de respiro entre elas, na cor do fundo — é o que
  separa uma pilha legível de uma faixa contínua.
- **marcas sobrepostas**: um anel de 2 px na cor do fundo em volta do marcador,
  para o de cima não se fundir com o de baixo (é o `line=` do exemplo acima).
- **rótulo direto**: nas 1 ou 2 séries que importam, no fim da linha. Não em todas,
  e nunca em todos os pontos.

---

## 6. Interatividade: seleção que vira filtro

```python
evento = st.plotly_chart(fig, key="g", on_select="rerun",
                         selection_mode=("points", "box", "lasso"))
pontos = evento.selection["points"]
```

Funciona igual em `st.altair_chart`, `st.dataframe` e `st.pydeck_chart`.

**A pegadinha do Plotly**, que custa uma tarde a quem descobre sozinho: o índice
que volta (`pointIndex`) é **dentro do traço** — cada cor é um traço separado — e
não dentro do seu DataFrame. Duas saídas:

```python
# 1. carregue o ID real em customdata (robusto)
fig = px.scatter(df, x="a", y="b", color="seg", custom_data=["id"])
ids = [p["customdata"][0] for p in evento.selection["points"]]

# 2. reconstrua por x/y e faça merge (simples, falha com duplicatas)
```

Prefira a 1.

---

## 7. Gráficos nativos: o que dá e o que não dá

```python
st.line_chart(df, x="data", y="valor", color="regiao", height=300)
st.bar_chart(df, x="cat", y="valor", horizontal=True, stack="normalize")
st.area_chart(df, x="data", y=["a", "b"], stack=True)
st.scatter_chart(df, x="a", y="b", size="c", color="d")
```

**Dão:** velocidade, tema herdado, zero configuração.
**Não dão:** formato de número personalizado, hover customizado, anotação,
segundo eixo (o que é bom), controle de margem.

Use-os para explorar. Quando o painel tiver dono, migre para Plotly ou Altair.

---

## 8. Mapas

```python
st.map(df, latitude="lat", longitude="lon", size="peso", color="#2a78d6",
       zoom=4)
```

Simples e suficiente para pontos. Para escolha de cor por valor, camadas,
coroplético ou 3D, use `st.pydeck_chart`. Para mapa de calor geográfico, lembre
a regra: **um matiz, claro → escuro**.

Nota prática: `st.map` usa Mapbox, e há a opção `mapbox.token` no `config.toml`
para usar a sua própria conta se o volume crescer.

---

## 9. Anti-padrões: verifique cada gráfico contra esta lista

| Anti-padrão | Por que é errado | Faça |
|---|---|---|
| dois eixos Y | permite "provar" qualquer correlação | dois gráficos, ou indexe à base 100 |
| pizza com 4+ fatias | o olho compara ângulo mal | barra ordenada |
| barra com eixo cortado | exagera a diferença | comece no zero |
| arco-íris para magnitude | a ordem das cores não é a ordem dos números | um matiz, claro → escuro |
| cor como único diferenciador | exclui ~8% dos homens | + forma, texto ou textura |
| 9 séries coloridas | ninguém acompanha | top 3 + "Outros", ou pequenos múltiplos |
| número em todo ponto | vira ruído | rótulo direto seletivo + hover |
| 3D em dado 2D | a perspectiva distorce comprimento | 2D, sempre |
| cor recalculada quando o filtro muda | a mesma série troca de cor e confunde | cor ligada à **entidade**, não à posição |
| 500 mil pontos numa dispersão | mancha, e o navegador trava | amostre ou agregue |
| legenda para uma série só | o título já a nomeia | apague |
| `1,234.56` num painel brasileiro | formato errado | `separators=",."` |

---

## 10. Modelo pronto: um módulo de gráficos do painel

O arquivo [`ui/componentes.py`](07-projeto-modelo/ui/componentes.py) do
projeto-modelo é este modelo, funcionando: uma função `layout_padrao` que decide
como **todo** gráfico se parece, uma paleta validada com variante escura, e uma
função por tipo de gráfico. Centralizar isso é o que impede o painel de virar
uma colcha de retalhos quando cinco pessoas mexem nele.

---

## Autoteste

1. Como se escolhe o tipo de gráfico? Qual é a pergunta que vem antes?
2. Por que dois eixos Y é o erro nº 1, e quais são as duas saídas corretas?
3. Quando cortar o eixo Y é legítimo e quando não é? Por quê?
4. Liste cinco elementos que devem ser apagados de um gráfico padrão.
5. Quais são as quatro funções da cor, e qual é a regra de cada uma?
6. Que cinco propriedades se **medem** numa paleta categórica?
7. O que aconteceu com a paleta original deste curso, e como isso foi descoberto?
8. Por que uma paleta que serve para barras pode não servir para dispersão? O que
   fazer?
9. Por que a versão escura de uma paleta não é a clara invertida?
10. Qual é a pegadinha do índice de seleção no Plotly, e qual é a solução robusta?
11. Que parâmetro faz o Plotly usar vírgula decimal?
