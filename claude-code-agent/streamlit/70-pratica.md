# 70 · Prática — 14 laboratórios progressivos

> **Nível:** iniciante a avançado · **Escrito em:** 02/09/2026 · Streamlit 1.63.0

Cada laboratório tem: **objetivo**, **passos**, **critério de aceite** (como você
sabe que terminou) e **armadilha esperada**. Faça na ordem. Não pule para o 10.

Ambiente pronto conforme [03-instalacao.md](03-instalacao.md).

---

## Lab 1 · Provar o rerun (20 min)

**Objetivo:** ver com os próprios olhos que o script roda inteiro a cada
interação.

**Passos**
1. Crie `lab1.py` com um `st.slider` e um `st.caption` mostrando
   `datetime.now()` com microssegundos.
2. Rode e arraste o controle. Observe o horário.
3. Acrescente `print("rodou", datetime.now())` e olhe o **terminal**.
4. Acrescente `time.sleep(2)` no topo. Arraste rápido. O que acontece?

**Critério de aceite:** você consegue explicar, em voz alta, por que o horário
muda e o que aconteceu com o run interrompido no passo 4.

**Armadilha esperada:** achar que o `print` do passo 3 aparece na página. Não
aparece — vai para o terminal. `st.write` é o `print` da tela.

---

## Lab 2 · O contador que não conta (20 min)

**Objetivo:** sentir a necessidade do `session_state`.

**Passos**
1. Escreva o contador **errado** (variável comum). Confirme que nunca passa de 1.
2. Corrija com `st.session_state`.
3. Acrescente um botão "zerar" — usando `on_click`, não `if st.button`.
4. Abra a app em **duas abas**. Os contadores são independentes?
5. Aperte F5 numa delas. O que acontece com o contador?

**Critério de aceite:** contador funciona; zerar funciona; você explica por que as
abas são independentes e por que o F5 zera.

**Armadilha esperada:** tentar `st.session_state.contador = 0` dentro de um
`if st.button("Zerar")` **depois** de o valor já ter sido lido no rerun — funciona
por acidente em alguns casos e confunde. Use `on_click`.

---

## Lab 3 · Painel de um CSV (45 min)

**Objetivo:** o primeiro painel de verdade.

**Passos**
1. Pegue qualquer CSV (ou gere um com `numpy`).
2. `layout="wide"`, título, três `st.metric` com `border=True`.
3. Filtros na barra lateral: um `date_input` de intervalo e um `multiselect`.
4. Um gráfico de linha e uma tabela.
5. **Trate o estado vazio.**

**Critério de aceite:** com filtros que não devolvem nada, a app mostra uma
mensagem útil — e não estoura.

**Armadilha esperada:** `df["valor"].mean()` de um DataFrame vazio devolve `NaN`,
e o cartão mostra "nan". E `date_input` com intervalo devolve **tupla de 1
elemento** enquanto o usuário escolheu só a primeira data.

---

## Lab 4 · Medir e cachear (30 min)

**Objetivo:** sentir a diferença que o cache faz.

**Passos**
1. Ponha `time.sleep(3)` na função de carga. Meça o tempo de trocar um filtro.
2. Acrescente `@st.cache_data`. Meça de novo.
3. Ponha `ttl=20` e observe: a cada 20 s, uma interação volta a demorar.
4. Ponha `show_time=True` e veja a duração na tela.
5. Acrescente um botão "Atualizar" que chama `funcao.clear()`.

**Critério de aceite:** você mediu os dois tempos e sabe dizer quantas vezes mais
rápido ficou.

**Armadilha esperada:** cachear uma função que chama `st.*` por dentro. O
Streamlit avisa (`CachedStFunctionWarning`) — funções cacheadas devolvem **dado**,
não desenham.

---

## Lab 5 · Do banco, não do CSV (60 min)

**Objetivo:** trocar arquivo por banco e aprender a filtrar do lado certo.

**Passos**
1. Carregue o CSV para um SQLite (`df.to_sql`).
2. Versão A: `SELECT *` e filtro em pandas. Meça.
3. Versão B: `WHERE` no SQL, com parâmetros ligados. Meça.
4. Crie um índice na coluna de data. Meça de novo.
5. Tente injetar `'; DROP TABLE ...; --` num filtro de texto das duas versões.

**Critério de aceite:** você tem três números de tempo e explica a diferença. A
injeção não funciona em nenhuma das versões (porque as duas usam parâmetros).

**Armadilha esperada:** `sqlite3.connect` sem `check_same_thread=False` quebra
quando o Streamlit atende de outra thread. E `PRAGMA foreign_keys` vem **desligado**
por padrão.

---

## Lab 6 · Layout profissional (45 min)

**Objetivo:** aplicar o [16-layout-e-design.md](16-layout-e-design.md).

**Passos**
1. Reorganize o painel do Lab 3 na ordem canônica: KPIs → tendência → composição
   → detalhe.
2. `st.container(border=True)` em cada bloco.
3. Título de cada bloco = uma pergunta respondida.
4. `help=` com a definição em cada KPI.
5. `delta` em todos os KPIs, comparando com o período anterior — e `None` quando
   não há base.
6. Detalhe dentro de um `expander`, com botão de download.

**Critério de aceite:** mostre a tela a alguém por 5 segundos e pergunte "como
estamos?". Se a pessoa responder, passou.

**Armadilha esperada:** mostrar `+100%` quando o período anterior é zero.

---

## Lab 7 · Formulário e validação (45 min)

**Objetivo:** entrada de dados com validação de verdade.

**Passos**
1. `st.form` com cinco campos, incluindo e-mail e data.
2. Uma função `validar(dados) -> dict[str, str]`, **fora** do arquivo da tela.
3. Uma mensagem por campo com problema.
4. `clear_on_submit=True`.
5. Escreva três testes `pytest` para `validar`, sem Streamlit.

**Critério de aceite:** `pytest` passa; a tela mostra erro por campo.

**Armadilha esperada:** tentar pôr `st.button` dentro do form (só
`form_submit_button` é permitido); e confiar no `validate=` do widget como
validação de verdade.

---

## Lab 8 · CRUD completo (90 min)

**Objetivo:** o "site com backend".

**Passos**
1. Tabela com `on_select="rerun"`.
2. Criar num `st.dialog`; editar num formulário abaixo da tabela; excluir com
   confirmação.
3. Toda escrita em transação.
4. **Invalide o cache** depois de cada escrita.
5. Grave auditoria (quem, o quê, quando).
6. Mensagem "flash" que aparece uma vez e some.

**Critério de aceite:** criar um registro e vê-lo aparecer na lista **sem**
recarregar a página, e sem chamar `st.cache_data.clear()` global.

**Armadilha esperada:** esquecer a invalidação — o registro está no banco e a tela
não muda. É o bug mais comum de CRUD em Streamlit.

---

## Lab 9 · Papéis e permissões (60 min)

**Objetivo:** autorização de verdade.

**Passos**
1. Três papéis: admin, editor, leitor.
2. `st.navigation` que registra páginas conforme o papel.
3. Guarda `exigir(("admin",))` no topo da página restrita.
4. A verificação de permissão **dentro** da função que grava, não perto do botão.
5. Um teste `AppTest` por papel × página.

**Critério de aceite:** um leitor que force a URL da página de admin não vê a
página; e um teste automatizado prova isso.

**Armadilha esperada:** achar que esconder o botão é segurança.

---

## Lab 10 · Cache correto num app multiusuário (45 min)

**Objetivo:** entender isolamento.

**Passos**
1. Cacheie uma consulta com `@st.cache_data` **sem** o usuário na chave.
2. Abra duas abas com usuários diferentes. O que acontece?
3. Corrija com o usuário na chave.
4. Corrija com `scope="session"`. Compare as duas correções.
5. Ponha um dicionário mutável em `@st.cache_resource` e altere-o numa aba.
   Observe a outra.

**Critério de aceite:** você reproduziu o vazamento **e** as duas correções, e
sabe dizer quando usar cada uma.

**Armadilha esperada:** o prefixo `_` num parâmetro tira o argumento da chave —
`_usuario` é exatamente como o vazamento acontece na vida real.

---

## Lab 11 · Fragmentos e tempo real (45 min)

**Objetivo:** reexecução parcial.

**Passos**
1. Uma página com uma consulta cara e um bloco de gráfico com controles próprios.
2. Meça: mexer no controle reexecuta a consulta?
3. Envolva o bloco em `@st.fragment`. Meça de novo.
4. Acrescente um segundo fragmento com `run_every="3s"`.
5. **Faça a conta:** quantas consultas por hora com 10 usuários?
6. Ponha `ttl=3` no cache da consulta e refaça a conta.

**Critério de aceite:** você tem os dois números (com e sem fragmento) e a conta
de consultas por hora, antes e depois do TTL.

**Armadilha esperada:** ler, dentro do fragmento, uma variável definida fora —
ela fica congelada no valor da última execução completa.

---

## Lab 12 · Testes (60 min)

**Objetivo:** cobrir a app.

**Passos**
1. Extraia toda regra de negócio para um módulo que **não importa** `streamlit`.
2. `pytest` para as regras, com fixture de banco temporário e semente fixa.
3. `AppTest` para: cada página carrega; estado vazio; cada papel.
4. Rode `pytest -q` e conte os testes.
5. Aumente `default_timeout` até parar de falhar por tempo.

**Critério de aceite:** `pytest -q` passa; a suíte roda em menos de 60 s; há ao
menos um teste que prova o comportamento do estado vazio.

**Armadilha esperada:** `AppTest.from_function` não enxerga os imports do módulo
de teste — todo import precisa estar dentro da função.

---

## Lab 13 · Contêiner e proxy (90 min)

**Objetivo:** colocar no ar como se fosse produção.

**Passos**
1. `Dockerfile` com usuário sem privilégio e `HEALTHCHECK`.
2. `docker compose up`, com volume para os dados.
3. nginx na frente, com repasse de WebSocket e `proxy_read_timeout 3600s`.
4. **Teste o erro de propósito:** tire as duas linhas de `Upgrade`/`Connection` e
   veja o "Connecting..." acontecer.
5. Reinicie o contêiner e confirme que os dados sobreviveram.
6. Rode uma tarefa de 2 minutos com `proxy_read_timeout 60s` e veja o que quebra.

**Critério de aceite:** você **reproduziu** as duas falhas clássicas (WebSocket e
timeout) e as corrigiu.

**Armadilha esperada:** esquecer `--server.address=0.0.0.0` e passar meia hora
achando que o problema é a rede do Docker.

---

## Lab 14 · Projeto final (4 a 8 horas)

**Objetivo:** juntar tudo.

Escolha **um** e faça inteiro:

- **A.** Painel de finanças pessoais: importa extrato CSV, categoriza,
  gráficos, metas, exportação.
- **B.** Ferramenta de suporte: consulta pedidos, edita status, registra
  observação, tudo com auditoria.
- **C.** Painel de monitoramento: lê métricas, mostra ao vivo com fragmentos,
  alerta visual, histórico.
- **D.** Chat sobre documentos: envia PDF, indexa, responde com streaming.

**Requisitos obrigatórios, para qualquer opção:**

- [ ] `nucleo/` sem importar `streamlit`.
- [ ] Login com papéis (OIDC ou o padrão do projeto-modelo).
- [ ] Banco com migração versionada.
- [ ] Cache com TTL, invalidado depois de cada escrita.
- [ ] Os quatro estados de tela tratados.
- [ ] Tema próprio, com paleta validada.
- [ ] ≥ 15 testes, incluindo `AppTest`.
- [ ] `Dockerfile` que sobe.
- [ ] `README.md` com os comandos exatos.

**Critério de aceite:** outra pessoa clona, roda os comandos do README e a app
funciona — sem te perguntar nada.

---

## Como saber que você aprendeu

| Nível | Você consegue... |
|---|---|
| **Iniciante** | fazer um painel com filtro e gráfico, e explicar o rerun |
| **Intermediário** | escolher entre `cache_data` e `cache_resource` sem pensar; tratar os quatro estados; separar `nucleo/` de `paginas/` |
| **Avançado** | diagnosticar lentidão medindo, não chutando; implementar autorização em duas camadas; colocar em produção atrás de proxy |
| **Pesquisa** | explicar o modelo de execução, o cálculo de identidade de widget e por que a memorização automática é indecidível |

---

## Autoteste

1. No Lab 1, o que acontece com o run quando você arrasta o controle rápido?
2. Por que o contador do Lab 2 precisa de `on_click` para zerar?
3. Que dois problemas de estado vazio o Lab 3 revela?
4. No Lab 5, quais são os três tempos que você mediu, e o que explica cada
   diferença?
5. Qual é o bug mais comum de CRUD, e como o Lab 8 o expõe?
6. No Lab 10, como o prefixo `_` causa vazamento entre usuários?
7. No Lab 13, quais são as duas falhas clássicas que você reproduziu de propósito?
