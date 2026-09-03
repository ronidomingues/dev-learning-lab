"""Administração: importação de CSV, auditoria e diagnóstico.

Três coisas que todo sistema real tem e todo tutorial omite.

A importação é o exemplo de **tarefa longa**: usa `st.status` para mostrar o
progresso, valida linha a linha, e — o ponto importante — **não grava nada se
qualquer linha for inválida**, porque importação parcial é pior que importação
falha (você não sabe onde parou).
"""

from __future__ import annotations

import io
import time
from datetime import date

import pandas as pd
import streamlit as st

from nucleo import config, repositorio, servicos
from nucleo.db import transacao, versao_atual, conexao
from paginas._comum import exigir, invalidar_cache_de_pedidos
from ui import componentes as c

CFG = st.session_state.get("_cfg") or config.carregar()
st.session_state["_cfg"] = CFG

u = exigir(("admin",))     # guarda de permissão: para a página se não for admin

c.cabecalho("Administração", f"Conectado como {u.email}", icone=":material/settings:")

aba_import, aba_audit, aba_diag = st.tabs(["Importar pedidos", "Auditoria", "Diagnóstico"])

# ---------------------------------------------------------------------------
COLUNAS_ESPERADAS = ["cliente_id", "produto_id", "quantidade", "valor", "status", "canal", "data"]

with aba_import:
    st.markdown("Envie um CSV com as colunas: `" + "`, `".join(COLUNAS_ESPERADAS) + "`.")

    exemplo = pd.DataFrame([
        {"cliente_id": 1, "produto_id": 2, "quantidade": 3, "valor": 1497.00,
         "status": "confirmado", "canal": "site", "data": date.today().isoformat()},
    ])
    st.download_button("Baixar modelo CSV",
                       exemplo.to_csv(index=False).encode("utf-8"),
                       "modelo_pedidos.csv", "text/csv", icon=":material/download:")

    arquivo = st.file_uploader("Arquivo CSV", type=["csv"], key="up_pedidos")

    if arquivo is not None:
        # O uploader devolve um objeto tipo-arquivo em memória (BytesIO), não um
        # caminho. Não existe "arquivo no disco do servidor" para ler.
        try:
            bruto = pd.read_csv(io.BytesIO(arquivo.getvalue()))
        except Exception as e:
            st.error(f"Não consegui ler o CSV: {e}", icon=":material/error:")
            st.stop()

        faltando = [c_ for c_ in COLUNAS_ESPERADAS if c_ not in bruto.columns]
        if faltando:
            st.error(f"Faltam colunas: {', '.join(faltando)}", icon=":material/error:")
            st.stop()

        st.caption(f"Prévia — {len(bruto)} linha(s):")
        st.dataframe(bruto.head(20), hide_index=True, width="stretch")

        if st.button("Validar e importar", type="primary", icon=":material/upload:"):
            with st.status("Importando...", expanded=True) as status:
                st.write("Validando linhas...")
                problemas: list[str] = []
                registros = []
                for i, linha in bruto.iterrows():
                    reg = {
                        "cliente_id": int(linha["cliente_id"]),
                        "produto_id": int(linha["produto_id"]),
                        "quantidade": int(linha["quantidade"]),
                        "valor_centavos": int(round(float(linha["valor"]) * 100)),
                        "status": str(linha["status"]).strip(),
                        "canal": str(linha["canal"]).strip(),
                        "data": str(linha["data"]).strip(),
                    }
                    erros = servicos.validar_pedido(reg)
                    if erros:
                        problemas.append(f"linha {i + 2}: " + "; ".join(erros))
                    registros.append(reg)

                if problemas:
                    status.update(label="Importação recusada", state="error")
                    st.error(f"{len(problemas)} problema(s). Nada foi gravado.",
                             icon=":material/error:")
                    st.code("\n".join(problemas[:50]))
                    st.stop()

                st.write(f"{len(registros)} linhas válidas. Gravando em uma transação...")
                inicio = time.perf_counter()
                # Tudo em UMA transação: ou entram as N linhas, ou nenhuma.
                with transacao(CFG.caminho_banco) as con:
                    con.executemany(
                        """INSERT INTO pedidos
                           (cliente_id, produto_id, quantidade, valor_centavos, status, canal, data)
                           VALUES (:cliente_id,:produto_id,:quantidade,:valor_centavos,:status,:canal,:data)""",
                        registros,
                    )
                decorrido = time.perf_counter() - inicio

                repositorio.registrar_auditoria(CFG.caminho_banco, ator=u.email,
                                                acao="pedido.importar",
                                                detalhe=f"{len(registros)} linhas")
                invalidar_cache_de_pedidos()
                status.update(label=f"{len(registros)} pedidos importados em "
                                    f"{decorrido:.2f}s", state="complete")
            st.balloons()

with aba_audit:
    st.caption("Últimas 200 ações registradas. Quem, o quê, quando.")
    registros = repositorio.listar_auditoria(CFG.caminho_banco, 200)
    if registros:
        st.dataframe(pd.DataFrame(registros), hide_index=True, height=460, width="stretch",
                     column_config={
                         "quando": st.column_config.TextColumn("Quando (UTC)", width="medium"),
                         "ator": st.column_config.TextColumn("Quem", width="medium"),
                         "acao": st.column_config.TextColumn("Ação", width="medium"),
                         "detalhe": st.column_config.TextColumn("Detalhe", width="large"),
                     })
    else:
        st.info("Nenhuma ação registrada ainda.")

with aba_diag:
    con = conexao(CFG.caminho_banco)
    a, b, d = st.columns(3)
    a.metric("Versão do esquema", versao_atual(con), border=True)
    a.metric("Streamlit", st.__version__, border=True)
    b.metric("Pedidos", f"{con.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0]:,}".replace(",", "."), border=True)
    b.metric("Clientes", con.execute("SELECT COUNT(*) FROM clientes").fetchone()[0], border=True)
    tamanho = CFG.caminho_banco.stat().st_size / 1_048_576 if CFG.caminho_banco.exists() else 0
    d.metric("Banco (MB)", f"{tamanho:.1f}".replace(".", ","), border=True)
    d.metric("Ambiente", CFG.ambiente, border=True)

    st.divider()
    st.markdown("**Contexto da requisição** (`st.context`) — útil para depurar proxy e tema:")
    st.json({
        "url": st.context.url,
        "ip": st.context.ip_address,
        "locale": st.context.locale,
        "timezone": st.context.timezone,
        "tema": st.context.theme.type if st.context.theme else None,
        "embutido": st.context.is_embedded,
    })

    st.divider()
    if st.button("Limpar todos os caches", icon=":material/mop:"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.toast("Caches limpos.", icon=":material/check:")
