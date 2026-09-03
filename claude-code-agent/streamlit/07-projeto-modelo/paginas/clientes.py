"""Clientes: cadastro com edição em lote (`st.data_editor`).

`st.data_editor` é a planilha do Streamlit. É excelente para corrigir dez linhas
e péssimo para editar dez mil — ele traz TUDO para o navegador. A regra que uso:
até ~2.000 linhas, data_editor; acima disso, tela de busca + formulário.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from nucleo import config, repositorio
from paginas._comum import clientes_em_cache, usuario_atual
from ui import componentes as c

CFG = st.session_state.get("_cfg") or config.carregar()
st.session_state["_cfg"] = CFG
u = usuario_atual()

c.cabecalho("Clientes", "Cadastro e observações.", icone=":material/group:")

if msg := st.session_state.pop("_flash_cli", None):
    st.success(msg, icon=":material/check_circle:")

clientes = repositorio.listar_clientes(CFG.caminho_banco)
df = pd.DataFrame([vars(x) for x in clientes])

busca = st.text_input("Buscar", type="search", placeholder="nome do cliente...",
                      icon=":material/search:", key="cli_busca", bind="query-params")
if busca:
    df = df[df["nome"].str.contains(busca, case=False, na=False)]

st.caption(f"{len(df)} clientes.")

if not u.pode_editar():
    st.dataframe(df, hide_index=True, height=440, width="stretch")
    c.aviso_sem_permissao("editar clientes")
    st.stop()

editado = st.data_editor(
    df, hide_index=True, height=440, width="stretch", key="editor_clientes",
    num_rows="fixed",                       # criar cliente tem formulário próprio
    disabled=["id"],                        # chave primária não se edita
    column_config={
        "id": st.column_config.NumberColumn("Nº", format="%d", pinned=True, width="small"),
        "nome": st.column_config.TextColumn("Nome", required=True, max_chars=80),
        "segmento": st.column_config.SelectboxColumn(
            "Segmento", options=["Varejo", "Indústria", "Serviços", "Governo", "Educação"],
            required=True),
        "uf": st.column_config.SelectboxColumn(
            "UF", options=["SP", "RJ", "MG", "RS", "PR", "BA", "PE", "SC", "GO", "CE"],
            width="small", required=True),
        "observacao": st.column_config.TextColumn("Observação", width="large"),
    },
)

# `st.session_state["editor_clientes"]` guarda SÓ o que mudou:
# {"edited_rows": {2: {"uf": "RJ"}}, "added_rows": [...], "deleted_rows": [...]}
# Comparar DataFrames inteiros para descobrir a diferença é desperdício — e erra
# quando o índice muda.
alteracoes = st.session_state.get("editor_clientes", {}).get("edited_rows", {})

col_a, col_b = st.columns([1, 3])
with col_a:
    if st.button("Gravar alterações", type="primary", icon=":material/save:",
                 disabled=not alteracoes, width="stretch"):
        from nucleo.db import transacao

        permitidas = {"nome", "segmento", "uf", "observacao"}
        with transacao(CFG.caminho_banco) as con:
            for pos, campos in alteracoes.items():
                cliente_id = int(df.iloc[int(pos)]["id"])
                campos = {k: v for k, v in campos.items() if k in permitidas}
                if not campos:
                    continue
                atrib = ", ".join(f"{k} = :{k}" for k in campos)
                con.execute(f"UPDATE clientes SET {atrib} WHERE id = :id",
                            {**campos, "id": cliente_id})
        repositorio.registrar_auditoria(CFG.caminho_banco, ator=u.email,
                                        acao="cliente.editar_lote",
                                        detalhe=f"{len(alteracoes)} linha(s)")
        clientes_em_cache.clear()
        st.session_state["_flash_cli"] = f"{len(alteracoes)} cliente(s) atualizado(s)."
        st.rerun()
with col_b:
    if alteracoes:
        st.caption(f"{len(alteracoes)} linha(s) pendente(s) de gravação.")
    else:
        st.caption("Edite uma célula para habilitar a gravação.")

with st.expander("Cadastrar novo cliente", icon=":material/person_add:"):
    with st.form("novo_cliente", clear_on_submit=True):
        nome = st.text_input("Nome", max_chars=80)
        a, b = st.columns(2)
        seg = a.selectbox("Segmento", ["Varejo", "Indústria", "Serviços", "Governo", "Educação"])
        uf = b.selectbox("UF", ["SP", "RJ", "MG", "RS", "PR", "BA", "PE", "SC", "GO", "CE"])
        obs = st.text_area("Observação", height=80)
        if st.form_submit_button("Cadastrar", type="primary", icon=":material/add:"):
            if not nome.strip():
                st.error("O nome é obrigatório.", icon=":material/error:")
            else:
                novo_id = repositorio.inserir_cliente(CFG.caminho_banco, {
                    "nome": nome.strip(), "segmento": seg, "uf": uf, "observacao": obs,
                    "criado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                })
                repositorio.registrar_auditoria(CFG.caminho_banco, ator=u.email,
                                                acao="cliente.criar", detalhe=f"id={novo_id}")
                clientes_em_cache.clear()
                st.session_state["_flash_cli"] = f"Cliente '{nome}' cadastrado (nº {novo_id})."
                st.rerun()
