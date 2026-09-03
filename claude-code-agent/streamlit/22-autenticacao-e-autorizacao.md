# 22 · Autenticação e autorização

> **Nível:** avançado · **Escrito em:** 02/09/2026 · Streamlit 1.63.0
> Assunto de segurança. Onde eu não tenho certeza, está escrito que não tenho.

Duas palavras diferentes, e confundi-las é a origem de metade dos furos:

- **Autenticação** — *quem é você?*
- **Autorização** — *o que você pode fazer?*

O `st.login()` resolve a primeira. A segunda é **sempre** sua.

---

## 1. As quatro estratégias, com recomendação

| Estratégia | Segurança | Esforço | Quando usar |
|---|---|---|---|
| **1. Proxy de autenticação na frente** (oauth2-proxy, Cloudflare Access, Authelia, ALB+Cognito) | **alta** | médio (infra) | **a melhor opção** quando você controla a infraestrutura |
| **2. `st.login()` / OIDC** | alta | **baixo** | quando a empresa tem Google Workspace, Entra ID, Okta, Keycloak, Auth0 |
| **3. Community Cloud com app privado** | média | nenhum | protótipo interno, poucos usuários |
| **4. Login caseiro** (tabela de usuários) | **você é o responsável** | alto (para fazer certo) | último recurso |

**Minha recomendação, e é opinião fundamentada:** comece pela **1** se você tem
infraestrutura; pela **2** se não tem. A **4** só se você tem um requisito que as
outras não atendem — e, nesse caso, leia a seção 6 inteira antes.

---

## 2. `st.login()` — OIDC nativo

Disponível desde a 1.42. Exige o extra de autenticação:

```bash
pip install "streamlit[auth]"      # traz Authlib >= 1.3.2 e httpx
```

`.streamlit/secrets.toml`:

```toml
[auth]
redirect_uri = "https://painel.empresa.com/oauth2callback"
cookie_secret = "<32+ bytes aleatórios; gere com: python -c 'import secrets;print(secrets.token_hex(32))'>"

[auth.google]
client_id = "....apps.googleusercontent.com"
client_secret = "..."
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

[auth.entra]
client_id = "..."
client_secret = "..."
server_metadata_url = "https://login.microsoftonline.com/<TENANT>/v2.0/.well-known/openid-configuration"
```

```python
import streamlit as st

if not st.user.is_logged_in:
    st.title("Painel Comercial")
    st.write("Entre com a sua conta corporativa.")
    a, b = st.columns(2)
    a.button("Entrar com Google", on_click=st.login, args=("google",),
             type="primary", icon=":material/login:", width="stretch")
    b.button("Entrar com Microsoft", on_click=st.login, args=("entra",),
             width="stretch")
    st.stop()

st.sidebar.write(f"**{st.user.name}**")
st.sidebar.caption(st.user.email)
st.sidebar.button("Sair", on_click=st.logout)
```

O que `st.user` traz depende do que o provedor devolve no *token* de identidade;
`email`, `name`, `sub` e `picture` são os usuais. `st.user.is_logged_in` está
sempre presente. Desde a 1.53 há `st.user.tokens`.

### Os três erros de configuração que custam a tarde

1. **`redirect_uri` diferente do cadastrado no provedor.** Tem de bater **byte a
   byte**: esquema, host, porta, caminho. `http://localhost:8501/oauth2callback`
   e `http://127.0.0.1:8501/oauth2callback` são endereços **diferentes** para o
   provedor.
2. **`cookie_secret` fraco ou compartilhado entre ambientes.** Ele assina o cookie
   de sessão. Fraco = falsificável. Igual em dev e prod = um cookie de dev vale em
   produção.
3. **Atrás de proxy sem repasse de cabeçalho.** O Streamlit monta a URL de retorno
   e precisa saber que está atrás de HTTPS. Configure `X-Forwarded-Proto` e
   `X-Forwarded-Host` no proxy — ver [28](28-deploy-e-operacao.md).

### O que `st.login()` **não** faz

- **Não autoriza.** Ele diz quem é a pessoa. Se ela pode ver a página de admin,
  quem decide é você.
- **Não restringe o domínio.** Com o provedor Google configurado em modo público,
  qualquer conta Google entra. Restrinja no provedor **e** no código:

```python
DOMINIOS = {"empresa.com.br"}
if st.user.email.split("@")[-1].lower() not in DOMINIOS:
    st.error("Esta aplicação é restrita a contas @empresa.com.br.")
    st.logout()
    st.stop()
```

---

## 3. Autorização: papéis, e onde eles moram

O `sub`/`email` do provedor identifica; os **papéis** são seus.

Três lugares para guardá-los, em ordem de robustez:

| Onde | Prós | Contras |
|---|---|---|
| **tabela no banco** | fonte única, auditável, muda sem deploy | você mantém |
| **grupos do provedor** (claim `groups`) | já existe no diretório da empresa | exige configurar o provedor para incluir o claim |
| **lista no `secrets.toml`** | zero infra | muda com deploy; não escala |

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Usuario:
    email: str
    nome: str
    papel: str            # "admin" | "analista" | "leitor"

@st.cache_data(ttl=300, scope="session")
def carregar_usuario(email: str) -> Usuario | None:
    linha = repositorio.buscar_usuario(email)
    return Usuario(email, linha["nome"], linha["papel"]) if linha else None

u = carregar_usuario(st.user.email)
if u is None:
    st.error("Sua conta não tem acesso a esta aplicação. Peça liberação a X.")
    st.stop()
```

### A guarda de página

```python
def exigir(papeis: tuple[str, ...]) -> Usuario:
    u = st.session_state.get("usuario")
    if u is None:
        st.error("Sessão expirada. Recarregue a página.")
        st.stop()
    if u.papel not in papeis:
        st.error(f"Acesso negado. Exige: {', '.join(papeis)}.")
        st.stop()
    return u
```

**Chame no topo da página.** `st.stop()` é o que garante que **nada** abaixo
executa — inclusive as consultas ao banco.

### As duas camadas, de novo

1. **Não registre a página** no `st.navigation` para quem não pode.
2. **Guarde a página** com `exigir(...)` no topo.

Verificado na 1.63.0: forçar a URL de uma página não registrada faz o Streamlit
cair na página padrão — a camada 1 funciona. A camada 2 existe porque um dia
alguém vai registrar a página para todo mundo por engano.

### O erro conceitual mais comum

> "Escondi o botão de excluir para quem é leitor."

Esconder o botão é **usabilidade**, não segurança. A regra é:

> **Toda verificação de permissão acontece no ponto de execução da ação, no
> servidor** — dentro da função que grava, não perto do botão.

```python
def excluir_pedido(usuario: Usuario, pedido_id: int) -> None:
    if not usuario.pode_editar():
        raise PermissionError("sem permissão para excluir")   # aqui
    repositorio.excluir(pedido_id)
```

---

## 4. Sessões: o limite honesto do `session_state`

`st.session_state` é memória do servidor associada à conexão WebSocket. Isso
significa:

**O que é bom:** o cliente não consegue forjá-lo. Não há cookie que o usuário
edite para virar admin.

**O que é ruim, e precisa ser dito:**

| Situação | O que acontece |
|---|---|
| usuário aperta F5 | **sessão nova**: `session_state` zerado, e ele precisa logar de novo |
| servidor reinicia (deploy) | **todo mundo cai** |
| várias réplicas sem sessão fixa | cada requisição pode ir para um processo diferente, sem o estado |

Por isso `st.login()` (que usa um **cookie assinado**) é melhor que login caseiro
guardado em `session_state`: o cookie sobrevive ao F5 e ao reinício.

**Se você precisa de sessão persistente sem OIDC:** a saída é um proxy de
autenticação (estratégia 1) ou um cookie assinado próprio — que exige componente
customizado para ler/escrever cookie no navegador, porque o Streamlit não expõe
uma API de escrita de cookie. `st.context.cookies` é **somente leitura**.

---

## 5. Segredos

```toml
# .streamlit/secrets.toml  — NUNCA no Git
[banco]
url = "postgresql+psycopg://..."
```

```python
st.secrets["banco"]["url"]
```

**Em produção, prefira variável de ambiente ao arquivo.** Um arquivo pode ser
lido por engano, entrar num backup, ou aparecer num `docker cp`. Variável de
ambiente é o que os orquestradores (Kubernetes, ECS, Cloud Run) sabem injetar a
partir de um cofre.

```bash
export PAINEL_BANCO_URL="postgresql+psycopg://..."
```

O `.gitignore` do seu projeto **precisa** ter:

```
.streamlit/secrets.toml
```

Se um segredo vazou para o Git: **rotacione o segredo**. Reescrever o histórico
não basta — quem clonou já tem. Ver
[`variaveis-de-ambiente-e-segredos`](../variaveis-de-ambiente-e-segredos/00-MAPA.md).

---

## 6. Login caseiro: o que é obrigatório

Se você **precisa** mesmo fazer, este é o mínimo — e cada item abaixo é um item
porque é onde eu já vi errarem:

1. **Hash lento e com sal:** PBKDF2-HMAC-SHA256 (≥ 200 mil iterações), bcrypt,
   scrypt ou **Argon2id** (o preferido hoje). **Nunca** SHA-256 puro, nunca MD5.
2. **Sal por usuário**, aleatório, guardado junto.
3. **Comparação em tempo constante** (`hmac.compare_digest`).
4. **Mesma mensagem** para "usuário não existe" e "senha errada" — e o mesmo
   tempo de resposta, senão você vaza a lista de e-mails cadastrados pelo relógio.
5. **Limite de tentativas** por conta e por IP, com atraso progressivo.
6. **Redefinição de senha** por token de uso único, com prazo curto.
7. **Registro de auditoria** de login, falha de login e logout.
8. **Segundo fator**, se houver qualquer dado sensível.
9. **HTTPS obrigatório** — senha em HTTP é senha pública.

O [`nucleo/auth.py`](07-projeto-modelo/nucleo/auth.py) do projeto-modelo
implementa 1 a 4 e 7, e **diz no próprio docstring** que 5, 6 e 8 faltam e por
quê. Ele existe para o projeto rodar offline e para ensinar o mecanismo — não
para ser copiado para produção.

> **Sobre bibliotecas de terceiros** (`streamlit-authenticator` e afins): existem,
> economizam trabalho, e você passa a confiar a autenticação da sua app a um
> pacote mantido por poucas pessoas. Se for usar, leia o código, confira quando
> foi a última atualização e como as senhas são guardadas. Isso não é paranoia —
> é o mínimo para qualquer dependência que fica no caminho da credencial.

---

## 7. Autorização em nível de dado

Permissão de página não basta quando o dado é segmentado (cada vendedor vê a
carteira dele).

**A regra:** o filtro por permissão vai **no SQL**, no servidor. Nunca em Python,
depois de trazer tudo.

```python
# ERRADO — os dados dos outros já vieram para a memória do servidor
df = todos_os_pedidos()
df = df[df.vendedor == usuario.email]

# CERTO
df = pedidos_do_vendedor(usuario.email)     # WHERE vendedor = ?
```

O jeito errado tem dois problemas: desempenho, e o fato de que um erro qualquer
depois desse ponto (um `st.dataframe(df_original)` esquecido) expõe tudo.

**Cache e isolamento:** se a consulta é cacheada com `scope="global"` e o
`usuario` é argumento, o isolamento depende da chave estar certa. Um `_` mal
colocado no parâmetro do usuário e um vê o dado do outro. Em app com dado
segmentado, use `scope="session"`.

---

## 8. Checklist

- [ ] HTTPS obrigatório, com redirecionamento de HTTP.
- [ ] Autenticação por OIDC (`st.login`) ou por proxy — não caseira.
- [ ] Domínio de e-mail restrito, no provedor **e** no código.
- [ ] Papéis num lugar auditável.
- [ ] Guarda no topo de toda página restrita (`st.stop()`).
- [ ] Verificação de permissão **dentro** da função que executa a ação.
- [ ] Filtro por permissão no SQL, não em Python.
- [ ] `cookie_secret` forte e diferente por ambiente.
- [ ] `secrets.toml` no `.gitignore`.
- [ ] Login, falha e logout registrados em auditoria.
- [ ] `showErrorDetails = "none"` em produção.

---

## Autoteste

1. Autenticação × autorização: qual o `st.login()` resolve?
2. Quais são as quatro estratégias, e qual você usaria numa empresa com Google
   Workspace e um cluster Kubernetes próprio?
3. Cite os três erros de configuração de OIDC que mais custam tempo.
4. Por que restringir o domínio de e-mail no código, se já restringi no provedor?
5. Onde a verificação de permissão **tem** de acontecer, e por que esconder o
   botão não conta?
6. Quais são as três limitações do `session_state` como mecanismo de sessão?
7. Nove requisitos de um login caseiro. Quais deles o projeto-modelo **não**
   implementa, e por quê?
8. Por que filtrar por permissão em Python, depois da consulta, é perigoso mesmo
   funcionando?
9. Que cuidado de cache é obrigatório em app com dado segmentado por usuário?
