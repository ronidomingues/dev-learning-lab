# 26 · Arquivos: upload, download e conteúdo estático

> **Nível:** intermediário · **Escrito em:** 02/09/2026 · Streamlit 1.63.0

---

## 1. Upload

```python
arquivo = st.file_uploader(
    "Planilha", type=["csv", "xlsx"],
    accept_multiple_files=False,      # ou True, "multiple", "directory"
    max_upload_size=20,               # MB, por widget (1.6x)
    key="up",
)
if arquivo is not None:
    st.write(arquivo.name, arquivo.type, f"{arquivo.size/1024:.0f} KB")
```

**O que ele devolve:** um `UploadedFile`, que é um objeto tipo-arquivo **em
memória** — não um caminho no disco do servidor. Não existe "o arquivo que o
usuário enviou" num diretório, a menos que você o grave.

```python
import io
import pandas as pd

df = pd.read_csv(arquivo)                       # pandas aceita objeto tipo-arquivo
bytes_ = arquivo.getvalue()                     # os bytes crus
df2 = pd.read_excel(io.BytesIO(bytes_))         # quando a lib exige BytesIO
arquivo.seek(0)                                 # se for ler duas vezes
```

O `seek(0)` é a pegadinha: depois de uma leitura, o ponteiro está no fim, e a
segunda leitura devolve vazio sem erro nenhum.

### Persistência do upload entre reruns

O arquivo enviado **permanece** enquanto o widget estiver na tela; o Streamlit o
mantém no gerenciador de arquivos da sessão. Ele some quando: o usuário remove o
arquivo, o widget deixa de ser renderizado, ou a sessão acaba.

Para trabalhar com ele depois, guarde o **conteúdo processado**, não o objeto:

```python
if arquivo is not None and "dados_importados" not in st.session_state:
    st.session_state.dados_importados = pd.read_csv(arquivo)
```

### Limites e configuração

```toml
[server]
maxUploadSize = 200      # MB, global (padrão: 200)
maxMessageSize = 200     # MB — precisa acompanhar o de upload
```

E, no proxy reverso, `client_max_body_size` no nginx precisa ser **maior** que o
`maxUploadSize` — senão o nginx recusa com **413** antes de o Streamlit ver algo.

---

## 2. Validar o que chega — obrigatório

Todo arquivo enviado por usuário é entrada não confiável. O mínimo:

```python
LIMITE = 20 * 1024 * 1024          # 20 MB
EXTENSOES = {".csv", ".xlsx"}

if arquivo is not None:
    # 1. tamanho (o `type=` do widget é conveniência do navegador, não garantia)
    if arquivo.size > LIMITE:
        st.error(f"Arquivo de {arquivo.size/1e6:.1f} MB — o limite é 20 MB.")
        st.stop()

    # 2. extensão, com o nome SANEADO
    nome = Path(arquivo.name).name          # remove qualquer caminho embutido
    if Path(nome).suffix.lower() not in EXTENSOES:
        st.error("Formato não aceito.")
        st.stop()

    # 3. conteúdo: tentar interpretar e falhar com mensagem clara
    try:
        df = pd.read_csv(arquivo)
    except Exception as e:
        st.error(f"Não consegui ler o CSV: {e}")
        st.stop()

    # 4. esquema
    faltando = [c for c in OBRIGATORIAS if c not in df.columns]
    if faltando:
        st.error(f"Faltam as colunas: {', '.join(faltando)}")
        st.stop()
```

**Nunca use `arquivo.name` para montar um caminho de gravação.** O nome vem do
cliente e pode conter `../../etc/`. Use `Path(arquivo.name).name` e, de
preferência, gere um nome novo:

```python
from uuid import uuid4
chave = f"anexos/{uuid4().hex}{Path(arquivo.name).suffix.lower()}"
```

---

## 3. Onde guardar

| Destino | Quando | Cuidado |
|---|---|---|
| **memória** (processar e descartar) | o padrão; a maioria dos casos | nada a fazer |
| **volume persistente** | um servidor só, volume montado | o disco do contêiner é **efêmero**: sem volume, some no deploy |
| **S3 / GCS / Azure Blob** | qualquer coisa séria | é a resposta certa com mais de uma réplica |
| **banco (`BLOB`)** | poucos arquivos, pequenos (< 1 MB) | infla backup e memória |

```python
import boto3
from uuid import uuid4

@st.cache_resource
def s3():
    return boto3.client("s3")

chave = f"anexos/{uuid4().hex}.pdf"
s3().put_object(Bucket=st.secrets["s3"]["bucket"], Key=chave,
                Body=arquivo.getvalue(), ContentType=arquivo.type)
repositorio.registrar_anexo(pedido_id, chave)
```

Para exibir depois, gere uma URL assinada com prazo curto — nunca torne o bucket
público:

```python
url = s3().generate_presigned_url(
    "get_object",
    Params={"Bucket": bucket, "Key": chave},
    ExpiresIn=300,      # 5 minutos
)
st.link_button("Abrir anexo", url)
```

---

## 4. Download

```python
st.download_button(
    "Baixar", data=conteudo,           # bytes, str, ou objeto tipo-arquivo
    file_name="relatorio.csv",
    mime="text/csv",
    on_click="ignore",                 # não reexecuta o script
    icon=":material/download:",
)
```

**`on_click="ignore"` importa mais do que parece.** Sem ele, cada download dispara
um rerun completo — o que, num painel pesado, faz o usuário esperar depois de já
ter o arquivo.

### Gerar sob demanda, sem gastar à toa

O problema: `data=` é avaliado **a cada rerun**, mesmo que ninguém clique. Gerar
um XLSX de 50 MB a cada movimento de filtro é desperdício puro.

Duas soluções:

```python
# 1. cachear a geração, com os filtros na chave
@st.cache_data(ttl=600)
def gerar_xlsx(inicio, fim, segmentos) -> bytes:
    ...

st.download_button("Baixar XLSX", gerar_xlsx(i, f, segs), "rel.xlsx", ...)
```

```python
# 2. gerar só depois de um clique explícito
if st.button("Preparar arquivo"):
    st.session_state.arquivo = gerar_xlsx(i, f, segs)
if "arquivo" in st.session_state:
    st.download_button("Baixar", st.session_state.arquivo, "rel.xlsx", ...)
```

### Os formatos, e o detalhe de cada um

```python
# CSV que o Excel brasileiro abre certo
csv = df.to_csv(index=False, sep=";", decimal=",",
                date_format="%d/%m/%Y").encode("utf-8-sig")

# XLSX (requer openpyxl)
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as w:
    df.to_excel(w, index=False, sheet_name="Dados")
xlsx = buffer.getvalue()

# JSON
js = df.to_json(orient="records", force_ascii=False, date_format="iso").encode()

# Parquet (para quem vai reprocessar: menor e com tipos preservados)
buffer = io.BytesIO(); df.to_parquet(buffer, index=False)
```

O `utf-8-sig` (BOM) é o que impede "Ação" de virar "AÃ§Ã£o" no Excel. O `;` é o
que impede tudo de cair numa coluna só.

---

## 5. Conteúdo estático

```toml
[server]
enableStaticServing = true
```

Uma pasta `static/` ao lado do script principal passa a ser servida em
`/app/static/...`:

```
projeto/
├── app.py
└── static/
    ├── logo.png
    └── Inter-Regular.woff2
```

```python
st.image("app/static/logo.png", width=180)
st.logo("app/static/logo.png")
```

Serve para logotipo, fonte própria ([ver 20](20-tema-e-identidade-visual.md)) e
arquivos pequenos e públicos.

> **Aviso:** é **público**, sem autenticação. Nada de dados aí dentro.

---

## 6. Câmera, áudio e PDF

```python
foto = st.camera_input("Tire uma foto", resolution="1080p")
if foto:
    st.image(foto)

audio = st.audio_input("Grave um áudio", sample_rate=16000)
if audio:
    st.audio(audio)
    # transcrever, enviar para uma API, etc.

st.pdf(bytes_do_pdf, height=600)          # requer streamlit[pdf]
```

Câmera e microfone exigem **HTTPS** (ou `localhost`) — é uma exigência do
navegador, não do Streamlit. Em rede interna com IP e HTTP puro, os widgets
simplesmente não pedem permissão e não funcionam.

---

## 7. Armadilhas

| Armadilha | Sintoma | Correção |
|---|---|---|
| tratar `arquivo` como caminho | `TypeError` / arquivo não encontrado | é objeto em memória |
| ler duas vezes sem `seek(0)` | segunda leitura vazia, sem erro | `arquivo.seek(0)` |
| gravar no disco do contêiner | some no próximo deploy | volume ou S3 |
| usar `arquivo.name` no caminho | travessia de diretório | `Path(name).name` + nome gerado |
| `maxUploadSize` sem ajustar o proxy | **413 Request Entity Too Large** | `client_max_body_size` no nginx |
| `data=` gerado a cada rerun | app lento sem motivo aparente | cache ou geração sob clique |
| CSV sem BOM | acentos quebrados no Excel | `utf-8-sig` |
| upload grande somando na memória | app estoura | limite o tamanho e processe em pedaços |
| `static/` com dado sensível | vazamento | não é autenticado |

---

## Autoteste

1. O que `st.file_uploader` devolve, exatamente? Por que não é um caminho?
2. Por que `seek(0)`?
3. Quatro validações obrigatórias de um arquivo enviado por usuário.
4. Por que nunca usar `arquivo.name` para montar o caminho de gravação?
5. Onde guardar anexos numa app com três réplicas? Por quê?
6. Que problema `on_click="ignore"` resolve no `download_button`?
7. Por que gerar o arquivo dentro de `data=` pode deixar o app lento, e quais são
   as duas soluções?
8. Quais são os quatro ajustes de um CSV para o Excel brasileiro?
9. Que exigência do navegador `st.camera_input` tem, e qual é o sintoma de não
   cumpri-la?
