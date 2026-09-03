# 18 · Tabelas, edição e o `column_config`

> **Nível:** intermediário · **Escrito em:** 02/09/2026 · Streamlit 1.63.0

Tabela é o componente mais usado e o menos cuidado. A diferença entre "despejo de
DataFrame" e "relatório" cabe num dicionário.

---

## 1. Os três comandos

| Comando | Interativo? | Editável? | Use para |
|---|---|---|---|
| `st.table` | não | não | tabela curta e fixa (≤ 20 linhas), tipo legenda |
| `st.dataframe` | sim | não | leitura, consulta, seleção |
| `st.data_editor` | sim | **sim** | correção pontual, entrada de dados |

---

## 2. `st.dataframe`: de despejo a relatório

```python
st.dataframe(df)          # despejo: nomes de coluna do banco, datas ISO, floats crus
```

```python
st.dataframe(                                    # relatório
    df,
    hide_index=True,
    height=420,
    column_order=["id", "data", "cliente", "valor", "status"],
    column_config={
        "id":      st.column_config.NumberColumn("Nº", format="%d",
                                                 pinned=True, width="small"),
        "data":    st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
        "cliente": st.column_config.TextColumn("Cliente", width="medium"),
        "valor":   st.column_config.NumberColumn("Valor", format="R$ %.2f"),
        "status":  st.column_config.TextColumn("Situação", width="small"),
    },
)
```

Cinco decisões nessas 12 linhas:

1. **`hide_index=True`** — o índice do pandas quase nunca significa algo para o
   usuário.
2. **`column_order`** — escolhe **e ordena** as colunas de uma vez. Você raramente
   quer mostrar tudo que veio do banco.
3. **`pinned=True`** na coluna-chave — ela fica fixa ao rolar para o lado. Em
   tabela larga, é o que salva a leitura.
4. **Rótulos em português**, sem `vlr_liq_ctv`.
5. **Formatos** de data e moeda no padrão do país.

---

## 3. O catálogo de colunas

Verificado por `dir(st.column_config)` na 1.63.0:

| Tipo | Para |
|---|---|
| `TextColumn` | texto, com `max_chars`, `validate` |
| `NumberColumn` | número, com `format`, `min_value`, `max_value`, `step` |
| `CheckboxColumn` | booleano |
| `SelectboxColumn` | escolha entre opções fixas |
| `MultiselectColumn` | várias opções por célula |
| `DateColumn` / `DatetimeColumn` / `TimeColumn` | data e hora, com `format` |
| `ListColumn` | lista numa célula |
| `JsonColumn` | objeto JSON navegável |
| `LinkColumn` | URL clicável, com `display_text` |
| `MarkdownColumn` | Markdown na célula |
| `ImageColumn` / `AudioColumn` / `VideoColumn` | mídia |
| `ProgressColumn` | barra de progresso na célula |
| `LineChartColumn` / `BarChartColumn` / `AreaChartColumn` | minigráfico por linha |
| `ButtonColumn` | **botão por linha** (1.59+) |

### Os três que mais impressionam e menos custam

```python
st.dataframe(df, column_config={
    # minigráfico por linha: 12 meses de histórico dentro da célula
    "historico": st.column_config.LineChartColumn("12 meses", y_min=0, width="medium"),

    # barra de progresso: atingimento de meta
    "meta": st.column_config.ProgressColumn("Meta", min_value=0, max_value=1,
                                            format="%.0f%%"),

    # link com texto fixo, em vez da URL crua
    "url": st.column_config.LinkColumn("Ficha", display_text="abrir"),
})
```

`LineChartColumn` espera uma coluna cujas **células são listas de números**:

```python
df["historico"] = df["id"].map(lambda i: serie_de_12_meses(i))   # list[float]
```

### `ButtonColumn` (1.59+): ação por linha

```python
def aprovar():
    linha = st.session_state["tabela"]["clicked_row"]   # veja a nota abaixo
    ...

st.dataframe(df, key="tabela", column_config={
    "acao": st.column_config.ButtonColumn("Aprovar", type="primary",
                                          on_click=aprovar, key="btn_aprovar"),
})
```

> **Nota honesta:** `ButtonColumn` é recente e a forma de descobrir *qual* linha
> foi clicada mudou entre versões. Confira o comportamento na sua versão com
> `st.write(st.session_state["tabela"])` antes de confiar. Para código que precisa
> durar, o par `on_select="rerun"` + `st.dialog` (seção 5) é mais estável.

---

## 4. Tabela como widget: seleção

```python
evento = st.dataframe(
    df, key="tab", on_select="rerun",
    selection_mode="single-row",     # "multi-row" | "single-column" | "multi-column"
)

linhas = evento.selection.rows       # índices POSICIONAIS (0, 1, 2...)
if linhas:
    registro = df.iloc[linhas[0]]
```

**Atenção ao índice posicional.** `evento.selection.rows` devolve a posição na
tabela **como ela está exibida**, não o índice do DataFrame nem a chave primária.
Se você ordenou, filtrou ou reindexou, `df.iloc[pos]` continua certo, mas
`df.loc[pos]` está errado. Regra: use sempre `.iloc`, e tire o ID de verdade da
linha (`registro["id"]`).

---

## 5. Padrão CRUD com tabela

O fluxo que funciona, e que está implementado em
[`paginas/pedidos.py`](07-projeto-modelo/paginas/pedidos.py):

```
tabela com on_select  →  usuário marca a linha
                      →  formulário de edição aparece abaixo
                      →  gravar: valida, grava em transação, invalida cache, rerun
                      →  excluir: st.dialog de confirmação
```

```python
evento = st.dataframe(df, key="tab", on_select="rerun", selection_mode="single-row")
sel = evento.selection.rows
if not sel:
    st.info("Selecione uma linha para editar.", icon=":material/ads_click:")
    st.stop()

linha = df.iloc[sel[0]]
with st.form("editar"):
    qtd = st.number_input("Quantidade", 1, 999, int(linha["quantidade"]))
    gravar = st.form_submit_button("Gravar", type="primary")

if gravar:
    erros = validar({...})                 # 1. validação, no serviço
    if erros: ...
    else:
        repositorio.atualizar(int(linha["id"]), {...})   # 2. transação
        registrar_auditoria(...)                         # 3. auditoria
        consulta_em_cache.clear()                        # 4. invalidação
        st.session_state["_flash"] = "Atualizado."       # 5. mensagem
        st.rerun()
```

Os cinco passos numerados são obrigatórios. Faltar o 4 produz o bug clássico
"salvei e não apareceu".

---

## 6. `st.data_editor`: a planilha

```python
editado = st.data_editor(
    df,
    key="editor",
    num_rows="dynamic",              # "fixed" | "dynamic" | "add" | "delete"
    disabled=["id", "criado_em"],    # colunas somente leitura
    column_config={
        "uf": st.column_config.SelectboxColumn("UF", options=UFS, required=True),
        "obs": st.column_config.TextColumn("Observação", max_chars=200),
    },
)
```

### O que mudou está no estado, não no DataFrame

```python
mudancas = st.session_state["editor"]
# {"edited_rows": {2: {"uf": "RJ"}}, "added_rows": [{...}], "deleted_rows": [5]}
```

**Use isso, não a comparação de DataFrames.** Comparar `df` com `editado` linha a
linha é caro, e erra quando o índice muda ou quando há valores `NaN` (que não são
iguais a si mesmos).

```python
for pos, campos in mudancas["edited_rows"].items():
    registro_id = int(df.iloc[int(pos)]["id"])
    atualizar(registro_id, campos)      # só as colunas que mudaram
```

**Filtre por lista branca antes de gravar.** O dicionário vem do navegador; nunca
o repasse direto para um `UPDATE`:

```python
PERMITIDAS = {"nome", "uf", "observacao"}
campos = {k: v for k, v in campos.items() if k in PERMITIDAS}
```

### Onde `data_editor` para de servir

| Situação | `data_editor` serve? |
|---|---|
| corrigir 5 linhas de 200 | **sim**, é para isto |
| revisar 2.000 linhas | no limite |
| editar 50.000 linhas | **não** — tudo vai para o navegador |
| entrada de dados com validação cruzada entre campos | **não** — use formulário |
| edição concorrente (duas pessoas na mesma linha) | **não** — o último grava por cima |

Sobre a última: o `data_editor` não tem controle de concorrência. Se duas pessoas
editam a mesma linha, a última gravação vence, silenciosamente. A solução é
*optimistic locking* — guardar a versão da linha e recusar a gravação se ela
mudou. Este repositório tem um assunto inteiro sobre isso:
[`optimistic-locking`](../optimistic-locking/00-MAPA.md).

---

## 7. Tabelas grandes

```python
st.dataframe(df, lazy=True, height=500)      # 1.61+: linhas sob demanda
```

Antes disso, a tabela inteira ia para o navegador de uma vez, e 200 mil linhas o
congelavam. Com `lazy=True`, o Streamlit envia por pedaços (é o
`dataframe_chunk` do protocolo).

Ainda assim, hierarquia de soluções, da melhor para a pior:

1. **Não mostre 200 mil linhas.** Agregue, ou pagine (`st.pagination`).
2. **`lazy=True`** para o caso em que o usuário precisa rolar mesmo.
3. **Exporte um arquivo** — se o usuário quer *todos* os dados, ele quer um
   arquivo, não uma tela.

```python
pagina = st.pagination(num_pages=math.ceil(len(df) / 100), key="pg")
st.dataframe(df.iloc[(pagina - 1) * 100 : pagina * 100], hide_index=True)
```

---

## 8. Exportar

```python
csv = df.to_csv(index=False, sep=";", decimal=",",
                date_format="%d/%m/%Y").encode("utf-8-sig")
st.download_button("Baixar CSV", csv, "relatorio.csv", "text/csv",
                   on_click="ignore")
```

Os quatro detalhes: `sep=";"`, `decimal=","`, `utf-8-sig` (o BOM, sem o qual o
Excel estraga acentos) e `on_click="ignore"` (que evita um rerun inútil).

Para tirar o botão nativo de exportação da tabela (requisito comum em ambiente
regulado):

```toml
[client]
disableDataExport = true        # 1.60+
```

---

## 9. Armadilhas

| Armadilha | Sintoma | Correção |
|---|---|---|
| `ArrowInvalid` / `ArrowTypeError` | coluna `object` com tipos misturados | `df["c"] = df["c"].astype(str)` |
| datas viram texto | dtype `object` | `pd.to_datetime` antes |
| índice esquisito na tela | índice do pandas exposto | `hide_index=True` |
| `df.loc[posição]` errado | seleção devolve posição, não rótulo | use `.iloc` |
| edição some ao filtrar | `data_editor` recebeu um DataFrame novo | grave antes de refiltrar |
| tabela lenta | linhas demais no navegador | `lazy=True`, agregue, pagine |
| `NaN` na tela | valor ausente | `df.fillna("—")` na camada de exibição |
| coluna de dinheiro em `float` | erro de centavo ao somar | guarde em centavos `int`, exiba dividido por 100 |

---

## Autoteste

1. Quando `st.table`, quando `st.dataframe`, quando `st.data_editor`?
2. Cite cinco ajustes que transformam um despejo de DataFrame num relatório.
3. Para que serve `pinned=True`, e em que caso ele salva a leitura?
4. O que `evento.selection.rows` devolve exatamente? Que erro isso costuma causar?
5. Onde ficam as alterações do `data_editor`? Por que não comparar DataFrames?
6. Por que filtrar as colunas por lista branca antes de gravar o que veio do
   editor?
7. Em que três situações o `data_editor` deixa de ser a ferramenta certa?
8. O que `lazy=True` mudou, e por que ainda assim não é a primeira solução?
9. Quais são os quatro detalhes de um CSV que o Excel brasileiro abre certo?
