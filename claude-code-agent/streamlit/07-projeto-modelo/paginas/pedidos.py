"""Pedidos: o CRUD. É aqui que o "site com backend" aparece.

Um painel só lê. Uma aplicação **escreve** — e escrever traz problemas que
ler não tem:

- **validação** antes de gravar (e a validação mora no serviço, não no formulário);
- **transação** (grava tudo ou nada);
- **invalidação de cache** (depois do INSERT, o cache mente);
- **permissão** (leitor não escreve);
- **auditoria** (quem mudou o quê, quando);
- **confirmação** para o que é destrutivo.

Os seis pontos estão implementados abaixo, cada um marcado com um comentário.
"""

from __future__ import annotations

from datetime import date

import streamlit as st

from nucleo import config, repositorio, servicos
from nucleo.modelos import CANAIS, STATUS
from paginas._comum import (
    Filtros, barra_de_filtros, clientes_em_cache, invalidar_cache_de_pedidos,
    pedidos_em_cache, produtos_em_cache, usuario_atual,
)
from ui import componentes as c
from ui.formatos import brl

CFG = st.session_state.get("_cfg") or config.carregar()
st.session_state["_cfg"] = CFG
u = usuario_atual()
f: Filtros = barra_de_filtros(CFG.caminho_banco)

c.cabecalho("Pedidos", "Consultar, criar, alterar e excluir.", icone=":material/receipt_long:")

clientes = clientes_em_cache(CFG.caminho_banco)
produtos = produtos_em_cache(CFG.caminho_banco)
nome_cliente = dict(clientes)
info_produto = {pid: (nome, preco) for pid, nome, preco in produtos}


# ---------------------------------------------------------------------------
# Criar — em um diálogo modal (st.dialog), para não empurrar a lista para baixo.
# ---------------------------------------------------------------------------
@st.dialog("Novo pedido", width="medium")
def dialogo_novo() -> None:
    with st.form("novo_pedido", border=False):
        cid = st.selectbox("Cliente", [c_[0] for c_ in clientes],
                           format_func=lambda i: nome_cliente[i])
        pid = st.selectbox("Produto", [p[0] for p in produtos],
                           format_func=lambda i: f"{info_produto[i][0]} — {brl(info_produto[i][1])}")
        a, b = st.columns(2)
        qtd = a.number_input("Quantidade", min_value=1, max_value=999, value=1, step=1)
        desconto = b.number_input("Desconto (%)", min_value=0.0, max_value=50.0,
                                  value=0.0, step=0.5)
        d, e = st.columns(2)
        status = d.selectbox("Status", STATUS, index=STATUS.index("confirmado"))
        canal = e.selectbox("Canal", CANAIS)
        quando = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")

        preco = info_produto[pid][1]
        # Conta em inteiro, do começo ao fim. `round` explícito na única
        # multiplicação que produz fração.
        valor = int(round(preco * qtd * (1 - desconto / 100)))
        st.metric("Valor do pedido", brl(valor), border=True)

        salvar = st.form_submit_button("Salvar", type="primary", icon=":material/save:")

    if salvar:
        novo = dict(cliente_id=cid, produto_id=pid, quantidade=int(qtd),
                    valor_centavos=valor, status=status, canal=canal,
                    data=quando.isoformat())

        # (1) VALIDAÇÃO — no serviço, para valer também na importação de CSV.
        erros = servicos.validar_pedido(novo)
        if erros:
            for msg in erros:
                st.error(msg, icon=":material/error:")
            return

        # (2) TRANSAÇÃO — dentro de repositorio.inserir_pedido.
        pedido_id = repositorio.inserir_pedido(CFG.caminho_banco, novo)

        # (5) AUDITORIA
        repositorio.registrar_auditoria(
            CFG.caminho_banco, ator=u.email, acao="pedido.criar",
            detalhe=f"id={pedido_id} valor={valor} status={status}",
        )

        # (3) INVALIDAÇÃO DE CACHE — sem isto, a lista continua sem o pedido novo.
        invalidar_cache_de_pedidos()

        st.session_state["_flash"] = f"Pedido nº {pedido_id} criado ({brl(valor)})."
        st.rerun()


@st.dialog("Excluir pedido")
def dialogo_excluir(pedido_id: int, descricao: str) -> None:
    # (6) CONFIRMAÇÃO — ação destrutiva nunca acontece em um clique só.
    st.warning(f"Excluir o pedido **nº {pedido_id}**?\n\n{descricao}", icon=":material/warning:")
    st.caption("Não há desfazer.")
    a, b = st.columns(2)
    if a.button("Cancelar", width="stretch"):
        st.rerun()
    if b.button("Excluir", type="primary", width="stretch", icon=":material/delete:"):
        repositorio.excluir_pedido(CFG.caminho_banco, pedido_id)
        repositorio.registrar_auditoria(CFG.caminho_banco, ator=u.email,
                                        acao="pedido.excluir", detalhe=f"id={pedido_id}")
        invalidar_cache_de_pedidos()
        st.session_state["_flash"] = f"Pedido nº {pedido_id} excluído."
        st.rerun()


# --- mensagem de resultado da última ação ("flash") -------------------------
if msg := st.session_state.pop("_flash", None):
    st.success(msg, icon=":material/check_circle:")

# (4) PERMISSÃO
acoes, _ = st.columns([1, 3])
with acoes:
    if u.pode_editar():
        if st.button("Novo pedido", type="primary", icon=":material/add:", width="stretch"):
            dialogo_novo()
    else:
        st.button("Novo pedido", disabled=True, width="stretch",
                  help="Seu papel é 'leitor': acesso somente leitura.")

df = pedidos_em_cache(CFG.caminho_banco, f.inicio, f.fim, f.status, f.canais, f.segmentos)
if df.empty:
    st.info("Nenhum pedido com esses filtros.", icon=":material/filter_alt_off:")
    st.stop()

st.caption(f"{len(df)} pedidos · seleção de linha habilita as ações.")

# `on_select="rerun"` transforma a tabela num widget: clicar numa linha
# reexecuta o script com a seleção disponível no retorno.
evento = st.dataframe(
    df[["id", "data", "cliente", "produto", "quantidade", "valor", "status", "canal"]],
    hide_index=True, height=420, key="tabela_pedidos",
    on_select="rerun", selection_mode="single-row",
    column_config={
        "id": st.column_config.NumberColumn("Nº", format="%d", pinned=True, width="small"),
        "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY", width="small"),
        "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
        "quantidade": st.column_config.NumberColumn("Qtd.", format="%d", width="small"),
    },
)

selecionadas = evento.selection.rows if evento and hasattr(evento, "selection") else []
if not selecionadas:
    st.info("Selecione uma linha para editar ou excluir.", icon=":material/ads_click:")
    st.stop()

linha = df.iloc[selecionadas[0]]
st.divider()
st.markdown(f"#### Pedido nº {int(linha['id'])}")

if not u.pode_editar():
    c.aviso_sem_permissao("editar pedidos")
    st.stop()

with st.form("editar_pedido"):
    a, b, d = st.columns(3)
    nova_qtd = a.number_input("Quantidade", min_value=1, max_value=999,
                              value=int(linha["quantidade"]))
    novo_status = b.selectbox("Status", STATUS, index=STATUS.index(linha["status"]))
    novo_canal = d.selectbox("Canal", CANAIS, index=CANAIS.index(linha["canal"]))
    novo_valor = st.number_input("Valor (R$)", min_value=0.0,
                                 value=float(linha["valor"]), step=10.0, format="%.2f")

    g, h = st.columns(2)
    gravar = g.form_submit_button("Gravar alterações", type="primary", icon=":material/save:")
    apagar = h.form_submit_button("Excluir", icon=":material/delete:")

if gravar:
    campos = {"quantidade": int(nova_qtd), "status": novo_status,
              "canal": novo_canal, "valor_centavos": int(round(novo_valor * 100))}
    erros = servicos.validar_pedido({**campos, "cliente_id": int(linha["cliente_id"]),
                                     "produto_id": int(linha["produto_id"]),
                                     "data": str(linha["data"])})
    if erros:
        for m in erros:
            st.error(m, icon=":material/error:")
    else:
        repositorio.atualizar_pedido(CFG.caminho_banco, int(linha["id"]), campos)
        repositorio.registrar_auditoria(CFG.caminho_banco, ator=u.email,
                                        acao="pedido.editar",
                                        detalhe=f"id={int(linha['id'])} {campos}")
        invalidar_cache_de_pedidos()
        st.session_state["_flash"] = f"Pedido nº {int(linha['id'])} atualizado."
        st.rerun()

if apagar:
    dialogo_excluir(int(linha["id"]), f"{linha['cliente']} · {linha['produto']} · {brl(linha['valor_centavos'])}")
