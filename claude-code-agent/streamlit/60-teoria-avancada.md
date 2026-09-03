# 60 · Teoria avançada — o Streamlit por dentro

> **Nível:** pesquisa · **Escrito em:** 02/09/2026 · Streamlit 1.63.0
> Os detalhes de implementação foram lidos no **código-fonte do pacote
> instalado**, com o caminho de cada arquivo indicado. Onde eu extrapolo, está
> marcado como interpretação.

Este arquivo é para quem quer entender *por que* o Streamlit funciona assim, no
nível em que se pode discordar com fundamento.

---

## 1. O modelo formal: `tela = f(estado)`

O Streamlit implementa um modelo de interface que se escreve assim:

```
V : S → T
```

onde `S` é o estado (valores de widget + `session_state` + dados externos), `T` é
a árvore de elementos, e `V` é o seu script. A cada mudança de `S`, o sistema
recalcula `V(S)` **inteiro** e reconcilia o resultado com o que está na tela.

Isso é a mesma família do **React** (`UI = f(state)`) e do **Elm** (a *Elm
Architecture*: `Model → View`). A diferença está em três eixos:

| | React | Elm | Streamlit |
|---|---|---|---|
| Onde `V` executa | navegador | navegador | **servidor** |
| Granularidade do recálculo | componente (via `memo`/hooks) | árvore virtual inteira, com diff | **script inteiro** |
| Onde vive o estado | cliente | cliente | **servidor** |
| Reconciliação | *virtual DOM* | *virtual DOM* | **deltas por caminho** |

**A consequência teórica de `V` rodar no servidor:** o estado nunca precisa
atravessar a rede em direção ao cliente para ser confiável. É por isso que
`st.session_state` não é falsificável pelo navegador — diferente de um estado em
React, que o usuário edita com o console aberto. Isso é uma **propriedade de
segurança** que o modelo ganha de graça, e é subestimada.

**A consequência de custo:** cada interação é uma ida e volta na rede mais uma
execução completa. Latência mínima ≈ RTT + tempo do script. Em rede local, ~30 ms;
via internet transatlântica, ~200 ms + script.

---

## 2. Reconciliação: deltas em vez de DOM virtual

O React compara duas árvores virtuais e calcula a diferença. O Streamlit não
compara nada: ele **numera as posições**.

Cada elemento tem um `delta_path` — uma lista de índices que descreve o caminho na
árvore de contêineres. Uma mensagem `Delta` carrega o caminho e o conteúdo; o
navegador aplica na posição.

**Por que isso é mais barato que um DOM virtual:** não há comparação; o servidor
sabe, por construção, que "o terceiro elemento do segundo contêiner" mudou.

**Por que isso é mais frágil:** a identidade é **posicional**. Se o número de
elementos muda entre reruns (um `if` que às vezes escreve), a numeração desloca, e
o navegador remonta a partir dali. É a causa técnica do "pisca".

**Interpretação minha:** essa é a escolha de projeto mais consequente depois do
rerun. Identidade posicional é barata e funciona quando a estrutura é estável — e
a estrutura é estável porque o script é linear. Os dois se sustentam mutuamente.

---

## 3. Identidade de elemento: o hash e a mudança de 2026

Em `streamlit/elements/lib/utils.py`, a função `_compute_element_id` produz:

```
<PREFIXO>-<hash>-<chave do usuário>
```

O hash é construído com `util.create_fast_hasher()` — que é **BLAKE2b com digest
de 16 bytes**, com queda para **MD5** em builds FIPS que rejeitam `digest_size`
customizado (o comentário no código diz exatamente isso). Entram no hash:

- o tipo do elemento;
- a chave do usuário, se houver;
- os argumentos do comando — **exceto** quando há chave e o elemento declara
  `key_as_main_identity`;
- o `active_script_hash` (para o mesmo widget em páginas diferentes ter IDs
  diferentes);
- o `form_id` e o contêiner-raiz — **exceto** no mesmo caso acima.

```python
ignore_command_kwargs = user_key is not None and (
    (key_as_main_identity is True) or isinstance(key_as_main_identity, set)
)
```

**A leitura teórica dessa mudança (1.54):** o sistema passou de *identidade
estrutural* (o elemento é definido pelo que ele é) para *identidade nominal
opcional* (o elemento é definido pelo nome que você deu). Identidade estrutural é
elegante e não exige disciplina do programador; identidade nominal é robusta a
mudanças de aparência. O React resolveu isso com o mesmo mecanismo: a `key` das
listas.

A consequência prática — "use `key=` em todo widget de app real" — é uma
**disciplina** que o modelo agora recompensa. Antes da 1.54, `key` era opcional e
mudar um rótulo apagava a seleção do usuário.

---

## 4. O protocolo

Duas direções, ambas em Protocol Buffers, sobre um WebSocket em
`/_stcore/stream` (verificado: responde 101 Switching Protocols).

**ForwardMsg** (servidor → cliente). Os campos declarados no `.proto` do pacote
1.63.0 incluem:

```
delta · new_session · page_config_changed · page_info_changed · script_finished
navigation · page_not_found · session_status_changed · session_event
auto_rerun · stop_auto_rerun · logo · auth_redirect · file_urls_response
dataframe_chunk · deferred_file · parent_message · git_info_changed
page_profile · backend_operation_response · error_msg · heartbeat_ack
install_skills · dismiss_skills_nudge
```

Dois merecem comentário:

- **`dataframe_chunk`** é a mecânica do `st.dataframe(lazy=True)` (1.61): a tabela
  deixou de ser uma mensagem única e passou a ser um fluxo de pedaços sob demanda.
  É a admissão de que o modelo "mande a tela inteira" não escala para tabelas
  grandes;
- **`auto_rerun` / `stop_auto_rerun`** é como o `run_every` do fragmento é
  implementado: o servidor instrui o cliente a pedir reexecução periódica. Ou
  seja, o temporizador vive no **cliente**, não no servidor — o que explica por
  que fechar a aba interrompe o ciclo.

**Cache de mensagens.** Há um `ForwardMsgCache` (`runtime/forward_msg_cache.py`) e
as opções `global.minCachedMessageSize` e `global.maxCachedMessageAge`: mensagens
grandes são enviadas uma vez e depois referenciadas por hash (`ref_hash`). Duas
sessões vendo o mesmo DataFrame não pagam a serialização duas vezes.

**Dados tabulares em Apache Arrow.** É por isso que `pyarrow` é dependência
obrigatória. Arrow é colunar, binário e de cópia zero — um DataFrame de 100 mil
linhas em JSON seria dezenas de megabytes de texto para o navegador analisar.

---

## 5. O ScriptRunner e a máquina de estados

`runtime/scriptrunner/script_runner.py` define os eventos:

```
SCRIPT_STARTED
SCRIPT_STOPPED_WITH_COMPILE_ERROR
SCRIPT_STOPPED_WITH_SUCCESS
SCRIPT_STOPPED_FOR_RERUN
FRAGMENT_STOPPED_WITH_SUCCESS
ENQUEUE_FORWARD_MSG
SHUTDOWN
```

E a nota sobre threads, no próprio código:

> "There are two kinds of threads in Streamlit, the main thread and script
> threads. The main thread is started by invoking the Streamlit CLI, and
> bootstraps the framework and runs the Uvicorn webserver."

(Repare no "Uvicorn": é a migração para ASGI da 1.57 aparecendo no comentário.)

E, sobre threads do usuário:

> "It is possible for the user script to spawn its own threads, which could call
> Streamlit functions. We restrict the ScriptRunner's execution control to the
> script thread. Calling Streamlit functions from other threads is unlikely to
> work correctly due to lack of ScriptRunContext."

**`SCRIPT_STOPPED_FOR_RERUN` é o mecanismo de preempção:** quando chega estado
novo enquanto um run acontece, o atual é interrompido. Implementado por exceções
de controle (`RerunException`, `StopException`) que atravessam o seu código.

**A implicação teórica, e é séria:** o seu script **não tem garantia de
terminar**. Qualquer efeito colateral não transacional pode ficar pela metade.
Isso reclassifica "usar transação" de boa prática para **requisito do modelo de
execução**.

---

## 6. Teoria do cache: por que o hash é o problema difícil

O cache do Streamlit é memorização: `f(x) = f(x)` se `x` for o mesmo. O difícil é
decidir o que "o mesmo" significa para um objeto Python arbitrário.

`runtime/caching/hashing.py` trata explicitamente, entre outros:
`pandas.Series`/`DataFrame`, `polars.Series`/`DataFrame`, `numpy.ndarray`,
`PIL.Image`, `re.Pattern`, `io.StringIO`/`BytesIO`, `functools.partial`,
`UploadedFile`, modelos Pydantic, `Mock`. Fora dessa lista, `UnhashableTypeError`.

**Por que não dá para fazer melhor.** Determinar se duas invocações de uma função
Python arbitrária produzem o mesmo resultado é, no caso geral, **indecidível** —
redutível ao problema da parada. Uma função pode:

- ler um arquivo que mudou (dependência invisível);
- consultar a hora, ou um gerador aleatório;
- captar variáveis livres mutáveis do escopo externo;
- ter efeito colateral que importa.

Nenhum sistema de memorização automática resolve isso sem análise de efeitos
(o que Haskell tem pelo sistema de tipos, e Python não tem).

**A saída de engenharia do Streamlit é pedir a anotação humana**, e em duas
dimensões:

1. **onde** memorizar — o decorador;
2. **o quê** o valor é — dado (copiável, serializável) ou recurso (compartilhado,
   único).

A segunda dimensão é a contribuição interessante, e não é óbvia. O `@st.cache`
original tentava **inferir** isso e errava; a separação em `cache_data` e
`cache_resource` (2023) eliminou uma classe inteira de bugs simplesmente
transferindo a decisão para quem sabe.

**Trade-off explícito:** `cache_data` copia (custo O(n) por chamada, isolamento
garantido); `cache_resource` compartilha (custo O(1), isolamento nenhum). Não há
opção que dê os dois — é o mesmo trade-off de valores imutáveis versus memória
compartilhada, que é anterior ao Streamlit em umas cinco décadas.

---

## 7. Fragmentos: reatividade parcial num sistema não reativo

Um sistema reativo de verdade mantém um **grafo de dependências**: mudou `x`,
recalcula só o que depende de `x`. React o constrói pela árvore de componentes;
Elm, pelo tipo `Msg`; Shiny (R), por observação de leitura em tempo de execução —
literalmente detectando quais reativos foram lidos durante o cálculo.

O Streamlit **não constrói grafo nenhum**. `@st.fragment` é uma aproximação:
o programador declara manualmente uma fronteira e diz "o que está aqui dentro
depende só do que está aqui dentro".

**A consequência é uma obrigação não verificada.** Se o fragmento lê uma variável
de fora, ele fica com o valor da última execução completa — e nada avisa. É a
mesma classe de problema das dependências de `useEffect` no React: uma lista que
o programador mantém à mão e que ninguém verifica.

**Poderia ser diferente?** Sim, em princípio: dá para instrumentar leituras de
`session_state` e construir o grafo em tempo de execução, que é o que o Shiny faz.
O custo é uma camada de indireção em toda leitura de estado — e, provavelmente,
o fim do "é só Python normal", que é o argumento de venda do Streamlit.

**Interpretação minha:** essa recusa a construir o grafo é coerente com a filosofia
do projeto, e é também o teto do que ele pode ser. Um Streamlit com grafo de
dependências seria um Dash com sintaxe melhor.

Sobre `parallel=True` (1.58): fragmentos independentes rodam num pool de threads.
Como o GIL só é liberado em I/O e em código C, o ganho é limitado a esses casos —
o que é uma limitação do CPython, não do Streamlit. (O PEP 703, do CPython sem
GIL, muda esse cálculo a partir do momento em que o ecossistema de dados o
suportar; hoje, não muda.)

---

## 8. O custo do modelo, formalizado

Para um rerun:

```
T = T_rede + T_script + T_serialização + T_render

T_script = Σ (custo de cada linha)
         = T_io  +  T_computação  +  T_construção_da_árvore
```

O cache ataca `T_io` (que domina, e é o mais variável). O fragmento reduz o
conjunto de linhas somadas em `T_script`. O `lazy=True` e a agregação atacam
`T_serialização`. Nada ataca `T_rede` — é o piso.

**Consequência prática:** existe um piso de latência igual ao RTT. Um painel usado
do outro lado do oceano nunca vai parecer instantâneo, por melhor que esteja o
código. É argumento para hospedar perto do usuário — e argumento a favor de
frameworks que rodam no cliente, quando a latência é requisito.

---

## 9. Concorrência e o GIL

Um processo; uma thread por sessão; um GIL.

| Trabalho | Libera o GIL? | Duas sessões competem? |
|---|---|---|
| laço Python puro | não | **sim, muito** |
| numpy/pandas vetorizado | sim (no código C) | pouco |
| I/O de banco/rede/disco | sim | não |
| serialização Arrow | parcialmente | pouco |

Escalar é rodar mais processos com sessão fixa — que é escalar horizontalmente com
estado no servidor, um problema conhecido e chato: o balanceador precisa de
afinidade, e o deploy derruba todas as sessões.

**Comparação teórica:** um app React + API sem estado escala melhor porque o
estado da tela vive no cliente. O Streamlit troca essa escalabilidade pela
simplicidade de não ter cliente. É a mesma troca que aplicações web faziam nos
anos 1990 com sessão no servidor, e que a indústria abandonou por escala — e que
o Streamlit reintroduziu deliberadamente, porque para painel interno a escala não
é o problema.

---

## 10. Segurança do modelo, formalizada

**Propriedade forte:** todo o estado autoritativo vive no servidor. O cliente
envia valores de widget, e o servidor decide o que fazer com eles. Não há
"esconder o botão e confiar".

**Propriedade fraca:** o valor de widget que chega é **entrada não confiável**. O
`selectbox` restringe o que aparece na tela; nada impede um cliente adulterado de
mandar outra coisa pelo WebSocket. Formalmente: a interface é uma **sugestão** de
domínio, não uma restrição.

**Consequência formal:** toda validação e toda autorização precisam ser
verificadas no servidor, no ponto de execução da ação. É o mesmo teorema de
qualquer aplicação cliente-servidor, e a fluidez do Streamlit faz muita gente
esquecê-lo — porque parece que o widget e a ação estão "no mesmo lugar".

---

## 11. Limites teóricos, em resumo

1. **Memorização automática é indecidível** → o cache precisa de anotação humana.
2. **Reatividade sem grafo é aproximação** → o fragmento é uma obrigação não
   verificada.
3. **Estado no servidor limita a escala horizontal** → sessão fixa é obrigatória.
4. **Latência tem piso igual ao RTT** → não existe interação instantânea.
5. **Identidade posicional é frágil sob estrutura variável** → daí a `key`.
6. **O script pode ser preemptado** → efeito colateral tem de ser transacional.
7. **O GIL serializa CPU Python** → paralelismo só em I/O e em código C.

Cada limitação prática do Streamlit é consequência direta de um destes sete. E
cada um deles é um trade-off consciente, não um descuido — o que é a diferença
entre uma ferramenta com limites e uma ferramenta malfeita.

---

## 12. Para ler o código-fonte

Ordem que eu recomendo, para quem quer entender de verdade:

| Arquivo | Por quê |
|---|---|
| `runtime/scriptrunner/script_runner.py` | o laço principal e a máquina de estados |
| `runtime/app_session.py` | o ciclo de vida da sessão |
| `delta_generator.py` | como um `st.*` vira uma mensagem |
| `elements/lib/utils.py` | o cálculo de identidade de elemento |
| `runtime/state/session_state.py` | o estado, e as regras de escrita |
| `runtime/caching/hashing.py` | o *hasher*, e os tipos que ele conhece |
| `runtime/fragment.py` | como o fragmento é implementado |
| `proto/ForwardMsg.proto` | o protocolo inteiro, em uma página |

Repositório: <https://github.com/streamlit/streamlit>.

---

## Autoteste

1. Escreva `V : S → T` e explique cada símbolo. Quais são os três eixos de
   diferença para o React?
2. Que propriedade de segurança o Streamlit ganha por `V` rodar no servidor?
3. Como funciona a reconciliação por deltas? Por que ela é mais barata e mais
   frágil que um DOM virtual?
4. Que função de hash é usada na identidade de elemento, e o que entra nela?
5. O que mudou conceitualmente na identidade de widget em 2026?
6. Por que `SCRIPT_STOPPED_FOR_RERUN` reclassifica "usar transação" de boa prática
   para requisito?
7. Por que memorização automática é indecidível? A que problema clássico isso se
   reduz?
8. Qual é a contribuição conceitual da separação `cache_data`/`cache_resource`?
9. Por que `@st.fragment` é uma aproximação de reatividade, e o que custaria fazer
   de verdade?
10. Escreva a decomposição de `T` num rerun e diga o que cada otimização ataca.
11. Enuncie os sete limites teóricos e dê um sintoma prático de cada um.
