# 75 · Armadilhas, mitos e más práticas

> **Nível:** todos · **Escrito em:** 02/09/2026 · Streamlit 1.63.0
> As armadilhas 24 e 25 foram **encontradas e isoladas na produção deste curso**,
> em 02/09/2026, e não estão em nenhuma documentação.

---

# Parte I — 28 armadilhas

## Modelo de execução

### 1. Achar que o script roda uma vez
**Sintoma:** conexão aberta a cada interação; contador que não conta; arquivo lido
mil vezes.
**Causa:** não entendeu o rerun.
**Correção:** [12-modelo-de-execucao-e-rerun.md](12-modelo-de-execucao-e-rerun.md).

### 2. `if st.button(...)` que "não funciona na segunda vez"
```python
if st.button("Mostrar"):
    st.write("apareceu")          # some ao clicar em qualquer outra coisa
```
**Causa:** `st.button` é `True` **só** no rerun causado pelo próprio clique.
**Correção:** guarde no estado.
```python
if st.button("Mostrar"):
    st.session_state.mostrar = True
if st.session_state.get("mostrar"):
    st.write("apareceu")
```

### 3. `st.rerun()` incondicional
Laço infinito, 100% de CPU. **Sempre** condicione a um evento.

### 4. Escrita no banco disparada por `slider`
Cada movimento grava; e o run pode ser abandonado no meio.
**Correção:** escrita só por botão ou `form_submit_button`, sempre em transação.

### 5. `while True` + `time.sleep`
Trava a sessão para sempre. **Correção:** `@st.fragment(run_every=...)`.

### 6. Variável global do módulo guardando dado de usuário
Ela é **compartilhada por todas as sessões**. Vazamento de dados garantido.
**Correção:** `st.session_state`.

## Estado

### 7. Inicializar sem `if`
```python
st.session_state.carrinho = []       # zera a cada rerun
```
**Correção:** `st.session_state.setdefault("carrinho", [])`.

### 8. Escrever na chave de um widget depois de ele existir
`StreamlitAPIException`. **Correção:** escreva antes, ou dentro de `on_change`.

### 9. Widget dentro de `if` perde o valor
Ao sair da tela, a chave é limpa.
**Correção:** `persist_state="session"`, ou copie para outra chave.

### 10. Widget sem `key`
Mudar o rótulo ou as opções pode fazer o usuário perder a seleção (pior antes da
1.54; ainda assim, sem `key` você não acessa o valor pelo estado).
**Correção:** `key=` em todo widget de app real.

### 11. Comparar com o "valor anterior" no corpo do script
Sempre um rerun atrasado. **Correção:** `on_change`.

## Cache

### 12. `cache_resource` num DataFrame
Todos recebem **o mesmo objeto**; quem alterar, alterou para todos.
**Correção:** `cache_data`.

### 13. `cache_data` numa conexão
Tenta serializar. **Correção:** `cache_resource`.

### 14. Cache sem TTL em painel operacional
O número está velho, e ninguém desconfia. É pior que estar errado.

### 15. Esquecer de invalidar depois de escrever
"Salvei e não apareceu." **Correção:** `funcao.clear()` depois de gravar.

### 16. Prefixo `_` num parâmetro que muda o resultado
```python
@st.cache_data
def dados(_usuario):        # o usuário SAIU da chave
    return consultar(_usuario)   # o primeiro define o resultado de todos
```
Vazamento entre usuários. **Correção:** usuário na chave, ou `scope="session"`.

### 17. Conexão cacheada que morre por inatividade
"Funciona de manhã, quebra à tarde."
**Correção:** `@st.cache_resource(validate=...)` ou `pool_pre_ping=True`.

## Dados e desempenho

### 18. `SELECT *` e filtro em pandas
Traz milhões de linhas para a memória do servidor, por sessão.
**Correção:** filtre no banco.

### 19. Mandar 500 mil pontos para o gráfico
O navegador congela. **Correção:** agregue (`resample`) antes de desenhar.

### 20. Lista que só cresce no `session_state`
Histórico de chat, série de monitoramento. Estoura a memória.
**Correção:** `historico[-N:]`.

### 21. `run_every` sem cache
10 usuários × 1 s = 36 mil consultas por hora. E a aba esquecida no fim de semana.
**Correção:** `ttl` ≈ `run_every`, e intervalos maiores.

## Interface

### 22. Não tratar o estado vazio
`mean()` de série vazia devolve `NaN`; `iloc[0]` estoura.
**Correção:** trate os quatro estados ([16](16-layout-e-design.md)).

### 23. `date_input` de intervalo devolvendo 1 elemento
Enquanto o usuário escolheu só a primeira data, a tupla tem tamanho 1.
```python
if isinstance(intervalo, (tuple, list)) and len(intervalo) == 2:
    inicio, fim = intervalo
else:
    inicio, fim = padrao_inicio, hoje
```

### 24. **`AppTest.date_input().set_value()` não funciona (1.63.0)** ⚠
**Encontrado e isolado na produção deste curso, em 02/09/2026.** O estado do
widget é gerado corretamente, mas o script continua lendo o valor anterior.
Reproduzido com e sem `key`, com e sem `value=`, em intervalo e em data única.
`text_input`, `number_input`, `slider`, `time_input`, `multiselect`, `selectbox`
e `segmented_control` funcionam normalmente, testados no mesmo script.
**Contorno:** conduza o teste por outro widget.
**Lição geral:** confirme que o harness aplicou o que você pediu —
`assert at.session_state["chave"] == valor_esperado`.

### 25. **`AppTest.from_function` não enxerga os imports do módulo de teste** ⚠
Ele reexecuta o **código-fonte** da função num script novo. Todo import precisa
estar **dentro** da função. Verificado na 1.63.0.

### 26. Dois widgets iguais sem `key`
`StreamlitDuplicateElementKey`. **Correção:** `key` distinta.

### 27. CSS mirando classe interna do Streamlit
`.st-emotion-cache-...` muda entre versões, sem aviso.
**Correção:** `st.container(key="x")` → classe estável `st-key-x`.

### 28. `st.set_page_config` fora do lugar
`StreamlitSetPageConfigMustBeFirstCommandError`. Primeiro comando `st.*`, e só no
script principal.

---

# Parte II — 14 mitos

### Mito 1 · "Streamlit não escala"
**Meia-verdade.** Um processo atende bem dezenas de sessões pouco ativas; com
réplicas e sessão fixa, centenas. O que não escala é *milhares de simultâneos*.
A maioria das apps que "não escalaram" tinha `SELECT *` sem cache.

### Mito 2 · "Streamlit é só para protótipo"
**Falso desde 2023.** `AppTest`, `st.connection`, OIDC, tema, `allowedHosts`,
`disableDataExport` são recursos de produção. O que não é de produção é um
`app.py` de 2.000 linhas sem teste — e isso não é culpa da ferramenta.

### Mito 3 · "Precisa saber front-end"
**Falso.** Nem HTML, nem CSS, nem JavaScript — exceto para escrever componente
customizado.

### Mito 4 · "O rerun torna tudo lento"
**Falso.** O rerun em si custa milissegundos. O que custa é I/O e volume de dados.
Meça antes de acusar o modelo.

### Mito 5 · "Cache resolve tudo"
**Falso.** Cache esconde I/O lento; não conserta consulta ruim, nem volume demais
na tela — e introduz o problema novo de dado velho.

### Mito 6 · "`session_state` é um banco de dados"
**Falso e perigoso.** Some no F5, no fechar da aba, no reinício do servidor. Se o
usuário não pode perder, vai para o banco.

### Mito 7 · "Não dá para testar"
**Falso desde outubro de 2023.** `AppTest` roda sem navegador, em CI, em segundos.
Ver [30-testes.md](30-testes.md).

### Mito 8 · "Não dá para autenticar"
**Falso desde a 1.42.** `st.login()` com OIDC. E proxy de autenticação sempre foi
possível.

### Mito 9 · "É só um wrapper de Flask"
**Falso.** Foi Tornado até a 1.56; desde a 1.57 é Starlette + Uvicorn. E o modelo
de execução não tem nada a ver com um framework de rotas.

### Mito 10 · "Como a Snowflake comprou, vai fechar o código"
**Sem evidência.** Continua Apache 2.0, com lançamentos a cada 2–4 semanas e as
melhorias de 2026 beneficiando todo mundo. O risco real não é fechar o código: é
o roteiro priorizar o que serve ao produto pago. Acompanhe; não se alarme.

### Mito 11 · "Precisa de Snowflake"
**Falso.** Roda em qualquer lugar que rode Python.

### Mito 12 · "`st.experimental_*` é instável, evite"
**Desatualizado.** Esses nomes foram promovidos e removidos. Se um tutorial os
usa, o tutorial é velho — ver a tabela de obsoletos em
[05-manual-de-uso.md](05-manual-de-uso.md).

### Mito 13 · "Streamlit não serve para escrever no banco"
**Falso.** Serve, com transação, validação e invalidação de cache. É o que o
[projeto-modelo](07-projeto-modelo/) demonstra, com testes.

### Mito 14 · "Se ficar lento, é só usar fragment"
**Falso, e é a otimização na ordem errada.** Fragment é o quarto passo. Antes:
medir, filtrar no banco, cachear, agregar. Ver
[15-fragments-e-performance.md](15-fragments-e-performance.md).

---

# Parte III — más práticas que persistem, e por quê

**1. Tudo num arquivo só.**
*Por que persiste:* todo tutorial mostra assim, e funciona nos primeiros dois
meses. O custo aparece no mês seis, quando já é caro.

**2. `st.cache_data.clear()` global depois de qualquer escrita.**
*Por que persiste:* funciona. E joga fora o cache de todo mundo, inclusive de
consultas caras que não mudaram.

**3. Injetar CSS para tudo.**
*Por que persiste:* há centenas de posts ensinando, escritos antes de o sistema de
tema existir. Hoje, quase tudo se resolve no `config.toml`.

**4. Desligar `enableXsrfProtection` para "consertar" o upload.**
*Por que persiste:* é a primeira sugestão que aparece nos fóruns, e resolve o
sintoma. O problema é o proxy.

**5. `try/except Exception: pass`.**
*Por que persiste:* o traceback na tela assusta. E aí o painel mostra zero como se
fosse um número real.

**6. Copiar e colar o bloco de KPI em cinco páginas.**
*Por que persiste:* é mais rápido hoje. Amanhã você muda em quatro e esquece uma.

**7. Guardar senha com SHA-256 puro.**
*Por que persiste:* "é hash, está seguro". SHA-256 é **rápido** de propósito — é
exatamente a propriedade que você **não** quer numa senha. Use PBKDF2, bcrypt,
scrypt ou Argon2id.

**8. Não fixar versões.**
*Por que persiste:* `pip install streamlit` é mais curto. Até o dia em que o app
quebra sozinho, sem ninguém ter mexido.

**9. Usar `@st.fragment(run_every="1h")` como agendador.**
*Por que persiste:* parece um cron e não exige infraestrutura. Se ninguém abre a
aba, não roda; se dez abrem, roda dez vezes.

**10. Confiar no `selectbox` como validação.**
*Por que persiste:* a tela mostra só as opções válidas. Mas o valor chega pelo
WebSocket e pode ser qualquer coisa.

**11. Mostrar oito KPIs.**
*Por que persiste:* o solicitante pediu oito números. Ninguém compara oito. Quatro
no topo, o resto em gráfico ou tabela.

**12. Paleta escolhida por gosto.**
*Por que persiste:* parece bonita para quem escolheu. Vermelho e verde vizinhos
são a **mesma cor** para ~8% dos homens — e este curso cometeu esse erro na
primeira versão. Ver [17-graficos-e-visualizacao.md](17-graficos-e-visualizacao.md).

---

## Autoteste

1. Por que `if st.button(...)` "não funciona na segunda vez"? Correção.
2. Três formas de um usuário ver o dado de outro.
3. Por que cache sem TTL em painel operacional é pior que um número errado?
4. Qual é a armadilha do `date_input` de intervalo?
5. Que defeito da 1.63.0 este curso encontrou, e qual é a lição geral dele?
6. Desmonte o mito "Streamlit não escala" com precisão.
7. Por que SHA-256 puro é inadequado para senha — usando a palavra "rápido"?
8. Por que desligar a proteção XSRF é a resposta errada para o 403 no upload?
9. Por que `@st.fragment(run_every="1h")` é um péssimo agendador?
10. Qual é a ordem correta de otimização, e qual mito a inverte?
