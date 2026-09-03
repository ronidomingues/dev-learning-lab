# 13 · Estado da sessão e widgets

> **Nível:** intermediário · **Escrito em:** 02/09/2026 · Streamlit 1.63.0

O segundo maior gerador de bugs, depois do rerun. E, diferente do rerun, este
tem regras exatas que dá para decorar.

---

## 1. O que é `st.session_state`

Um dicionário por **sessão** (aba do navegador), que sobrevive aos reruns.

```python
st.session_state["chave"] = 1
st.session_state.chave = 1        # idêntico
"chave" in st.session_state
st.session_state.get("chave", 0)  # ⚠ funciona no app; NÃO funciona no AppTest
del st.session_state["chave"]
st.session_state.pop("chave", None)
list(st.session_state.keys())
```

Escopo, em uma frase: **uma aba, um estado.** Duas abas do mesmo usuário são dois
estados. Recarregar a página cria uma sessão nova e zera tudo.

---

## 2. Inicialização — o padrão certo

```python
# CERTO
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

# equivalente e mais curto
st.session_state.setdefault("carrinho", [])

# ERRADO — zera o carrinho a cada rerun
st.session_state.carrinho = []
```

Em app com muitas chaves, centralize:

```python
PADROES = {"carrinho": [], "pagina": 1, "filtros": {}, "usuario": None}

for chave, valor in PADROES.items():
    st.session_state.setdefault(chave, valor)
```

Isso também documenta, num lugar só, **todo** o estado que a app mantém — o que
é ouro quando o app cresce.

---

## 3. A relação entre widget e estado

Quando um widget recebe `key="x"`:

1. `st.session_state["x"]` passa a conter o valor atual do widget;
2. o widget lê dali no início do rerun;
3. **a chave pertence ao widget** enquanto ele existir na tela.

```python
valor = st.slider("Nota", 0, 10, key="nota")
# valor == st.session_state["nota"]  — sempre
```

### As três regras de escrita

**Regra 1 — antes do widget existir, você pode escrever.**

```python
if "nota" not in st.session_state:
    st.session_state.nota = 7        # ok: define o valor inicial
st.slider("Nota", 0, 10, key="nota")
```

**Regra 2 — depois do widget existir no script, você não pode.**

```python
st.slider("Nota", 0, 10, key="nota")
st.session_state.nota = 5            # StreamlitAPIException
```

A mensagem é explícita: *"st.session_state.nota cannot be modified after the
widget with key nota is instantiated"*.

**Regra 3 — dentro de um callback, sempre pode**, porque os callbacks rodam antes
do corpo do script.

```python
def zerar():
    st.session_state.nota = 0        # ok

st.slider("Nota", 0, 10, key="nota")
st.button("Zerar", on_click=zerar)
```

Esse é **o** padrão para "botão que limpa o formulário". Sem callback, não tem
como.

---

## 4. Widget que sai da tela perde o valor

Comportamento que surpreende todo mundo:

```python
if st.checkbox("Mostrar filtro avançado"):
    uf = st.selectbox("UF", ["SP", "RJ"], key="uf")
# desmarcar o checkbox → a chave "uf" some do session_state
```

**Por quê:** o Streamlit limpa o estado de widgets que não foram renderizados,
para não vazar memória em apps com muitos widgets condicionais.

**Três soluções, em ordem de preferência:**

```python
# 1. (1.6x) o parâmetro dedicado
st.selectbox("UF", ["SP", "RJ"], key="uf", persist_state="session")

# 2. copiar para uma chave que não é de widget
if "uf" in st.session_state:
    st.session_state["uf_guardado"] = st.session_state["uf"]

# 3. reafirmar o valor a cada rerun (funciona, é feio)
st.session_state.uf = st.session_state.get("uf", "SP")
```

`persist_state="page"` guarda enquanto o usuário estiver na mesma página;
`"session"` guarda pela sessão inteira, mesmo trocando de página.

---

## 5. Identidade do widget — o que mudou em 2026

Este é o ponto que mais mudou recentemente e que mais economiza tempo saber.

**Como era até a 1.53:** o ID do widget era o hash de tipo + **todos os
argumentos**. Trocar o `label` ou as `options` gerava um ID novo, e o widget
"nascia de novo", perdendo o que o usuário tinha escolhido.

**Como é a partir da 1.54:** quando você passa uma `key`, ela é a **identidade
principal**; os demais argumentos deixam de entrar no cálculo do ID (é o
`key_as_main_identity` no código de `_compute_element_id`).

O ID continua incluindo o hash do script ativo (para páginas diferentes) e, na
ausência de `key`, o `form_id` e o contêiner-raiz.

**Consequência, e é uma regra dura:**

> Em app real, **todo widget leva `key=`**. Sem exceção.

Vantagens: identidade estável, acesso pelo `session_state`, mensagem de erro
legível em duplicata, e o valor sobrevive a mudanças de rótulo e de opções.

```python
# sem key: trocar as opções apaga a escolha do usuário
st.selectbox("Cliente", carregar_clientes())

# com key: a escolha sobrevive
st.selectbox("Cliente", carregar_clientes(), key="filtro_cliente")
```

---

## 6. Callbacks: `on_change`, `on_click`

```python
def ao_mudar(prefixo: str):
    st.session_state.log = f"{prefixo}: {st.session_state.uf}"

st.selectbox("UF", ["SP", "RJ"], key="uf", on_change=ao_mudar, args=("mudou",))
```

Ordem garantida em cada rerun:

```
1. callbacks dos widgets que mudaram
2. corpo do script
```

**Quando usar callback:**

- limpar ou preencher outro widget (única forma legal de escrever na chave dele);
- registrar auditoria da mudança;
- evitar "estado atrasado por um rerun".

**Quando NÃO usar:** para a lógica principal da tela. O corpo do script é o lugar
da lógica; callback é para efeito colateral pontual. Apps com dez callbacks
costumam ser apps que estão tentando ser React sem ser React.

### O bug do "um rerun atrasado"

```python
# ERRADO
uf = st.selectbox("UF", ["SP", "RJ"], key="uf")
st.write(st.session_state.get("uf_anterior"))   # sempre um passo atrás
st.session_state.uf_anterior = uf
```

Se você precisa reagir à **mudança**, use `on_change`. Comparar com o valor
anterior no corpo do script sempre produz defasagem de um rerun.

---

## 7. `st.form` — agrupar interações

```python
with st.form("filtros", clear_on_submit=False, enter_to_submit=True, border=True):
    inicio = st.date_input("De", key="f_inicio")
    fim = st.date_input("Até", key="f_fim")
    ufs = st.multiselect("UF", ["SP", "RJ"], key="f_uf")
    aplicar = st.form_submit_button("Aplicar", type="primary")

if aplicar or "resultado" not in st.session_state:
    st.session_state.resultado = consultar(inicio, fim, tuple(ufs))

st.dataframe(st.session_state.resultado)
```

**O que o form faz:** os widgets internos não disparam rerun ao mudar; o estado
deles só vai para o servidor no envio.

**O que o form custa:** você não consegue reagir *durante* o preenchimento —
adeus filtro em cascata, adeus preço calculado ao vivo.

**Regras:**

- `st.button` comum **não** pode ficar dentro de um form (só `form_submit_button`);
- pode haver mais de um `form_submit_button` no mesmo form (cada um devolve `True`
  quando é o clicado);
- `clear_on_submit=True` reseta os widgets aos valores iniciais depois do envio —
  perfeito para "cadastrar mais um".

**Quando usar form:** formulário de cadastro; filtro com consulta cara; qualquer
coisa em que reagir a cada tecla seja desperdício.
**Quando não usar:** filtros de painel que devem responder na hora.

---

## 8. Estado na URL

```python
st.query_params["uf"] = "SP"
uf = st.query_params.get("uf", "SP")
st.query_params.from_dict({"uf": "SP", "de": "2026-01-01"})
todos = st.query_params.get_all("uf")     # ?uf=SP&uf=RJ
st.query_params.clear()
```

Desde a 1.55 há o atalho declarativo, que é o que você quase sempre quer:

```python
st.multiselect("UF", ufs, key="f_uf", bind="query-params")
```

**Por que isso importa mais do que parece.** Painel sem estado na URL não é
compartilhável: a pessoa manda o link e o colega vê outra coisa. Com a ligação, o
link **é** o relatório. É o recurso que mais aproxima um painel de Streamlit de
uma ferramenta de BI comercial.

**Cuidados:**

- a URL é visível e vai para o histórico do navegador e para os logs do proxy.
  **Nunca** ligue um widget que contenha dado sensível;
- há limite de tamanho de query string (o Streamlit 1.60 passou a impô-lo
  explicitamente). Não ligue um multiselect com 500 opções selecionáveis.

---

## 9. Padrões prontos

### Máquina de estados (assistente de várias etapas)

```python
st.session_state.setdefault("etapa", 1)

if st.session_state.etapa == 1:
    nome = st.text_input("Nome", key="w_nome")
    if st.button("Avançar", disabled=not nome):
        st.session_state.etapa = 2
        st.rerun()

elif st.session_state.etapa == 2:
    st.write(f"Olá, {st.session_state.w_nome}")
    a, b = st.columns(2)
    if a.button("Voltar"):
        st.session_state.etapa = 1
        st.rerun()
    if b.button("Concluir", type="primary"):
        st.session_state.etapa = 3
        st.rerun()

else:
    st.success("Concluído!")
    if st.button("Recomeçar"):
        st.session_state.etapa = 1
        st.rerun()
```

### Mensagem que sobrevive a um rerun ("flash")

```python
# ao gravar:
st.session_state["_flash"] = "Pedido 42 criado."
st.rerun()

# no topo da página:
if msg := st.session_state.pop("_flash", None):
    st.success(msg, icon=":material/check_circle:")
```

O `pop` é o detalhe: a mensagem aparece **uma vez** e some.

### Botão que "gruda"

```python
st.session_state.setdefault("mostrar", False)
if st.button("Mostrar detalhes"):
    st.session_state.mostrar = not st.session_state.mostrar
if st.session_state.mostrar:
    st.dataframe(detalhe)
```

### Limpar todos os filtros

```python
def limpar():
    for k in [k for k in st.session_state if k.startswith("f_")]:
        del st.session_state[k]

st.sidebar.button("Limpar filtros", on_click=limpar)
```

Prefixar as chaves de filtro (`f_`) é uma convenção barata que habilita isso.

---

## 10. Armadilhas específicas

| Armadilha | Sintoma | Correção |
|---|---|---|
| `st.session_state.x = []` sem `if` | o valor zera a cada rerun | `setdefault` |
| escrever na chave do widget depois dele | `StreamlitAPIException` | escreva antes, ou em callback |
| widget condicional | valor some ao esconder | `persist_state="session"` |
| widget sem `key` | valor perdido ao mudar rótulo/opções | sempre use `key` |
| objeto mutável no `cache_resource` | um usuário altera para todos | guarde imutável, ou proteja com `Lock` |
| classe redefinida com o app rodando | `isinstance` falha misteriosamente | reinicie o servidor |
| `enforceSerializableSessionState` ligado | erro ao guardar objeto não serializável | é proposital; guarde só o que serializa (obrigatório em backends de sessão distribuídos) |
| comparar valor atual com "anterior" no corpo | defasagem de um rerun | use `on_change` |

---

## Autoteste

1. Qual é o escopo exato do `st.session_state`? O que acontece com F5?
2. Escreva as três regras de escrita na chave de um widget, e explique **por que**
   a regra do callback é diferente.
3. Por que um widget dentro de um `if` perde o valor quando some da tela? Duas
   formas de evitar.
4. O que mudou na identidade de widget a partir da 1.54, e qual regra prática
   isso gera?
5. Quando usar `st.form` e o que você perde ao usá-lo?
6. Implemente "limpar todos os filtros" e explique por que precisa ser callback.
7. Por que comparar com o valor anterior no corpo do script dá resultado atrasado?
8. Que cuidado de segurança `bind="query-params"` exige?
9. Explique o padrão "flash" e por que ele usa `pop` em vez de `get`.
