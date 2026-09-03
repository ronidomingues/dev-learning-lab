# 2 · Pré-requisitos

> Nível: iniciante · Atualizado em 14/08/2026

Este arquivo existe para você **não descobrir no meio do caminho** que faltava uma
base. Leia a tabela, marque o que falta, siga a rota de resgate.

---

## Conhecimento indispensável

Sem isto, o material dos blocos A e B vai parecer arbitrário.

| O que | Por que é indispensável aqui | Onde aprender |
|---|---|---|
| **HTTP: requisição, resposta, cabeçalho, código de status** | O JWT vive dentro de um cabeçalho HTTP. Sem saber o que é `Authorization:` ou o que significa 401, nada faz sentido. | [apis/12-http-por-dentro.md](../apis/12-http-por-dentro.md) · [MDN HTTP](https://developer.mozilla.org/pt-BR/docs/Web/HTTP) |
| **JSON** | O payload de um JWT *é* um objeto JSON. | [JSON.org (PT)](https://www.json.org/json-pt.html) — 20 minutos |
| **Linha de comando básica** | Todo exemplo aqui é `curl`, `openssl`, `node`. | [docker/02-pre-requisitos.md](../docker/02-pre-requisitos.md) tem a base |
| **Alguma linguagem de programação** | Os exemplos são em JavaScript, mas os conceitos são idênticos em Python, Java, Go, C#. Se você lê pseudocódigo, se vira. | qualquer uma |
| **A diferença entre autenticação e autorização** | Autenticação = *quem você é*. Autorização = *o que você pode*. JWT participa das duas, de formas diferentes. Confundir as duas é a origem de metade dos erros de projeto. | [10-fundamentos.md](10-fundamentos.md) define ambas |

## Conhecimento que ajuda muito

Você consegue seguir sem, mas o Bloco B vai render bem mais com:

| O que | Onde entra | Onde aprender |
|---|---|---|
| **Noção de hash criptográfico** (SHA-256) | assinatura, `kid`, armazenamento de token | [commits-assinados/10-fundamentos.md](../commits-assinados/10-fundamentos.md) |
| **Chave pública vs. chave privada** | a diferença entre HS256 e ES256, que é a decisão de arquitetura mais importante do assunto | [commits-assinados/13-gpg-a-fundo.md](../commits-assinados/13-gpg-a-fundo.md) |
| **Cookies, `SameSite`, XSS, CSRF** | onde guardar o token no navegador — [arquivo 18](18-onde-guardar-no-cliente.md) | [OWASP: XSS](https://owasp.org/www-community/attacks/xss/) |
| **Base64** | os dois primeiros segmentos do token | [12-anatomia-do-token.md](12-anatomia-do-token.md) explica do zero |
| **OAuth 2.0 / OpenID Connect** | onde o JWT mais aparece na vida real | [19-jwt-no-oauth-e-oidc.md](19-jwt-no-oauth-e-oidc.md) |
| **Matemática de curvas elípticas** | só para o [arquivo 60](60-teoria-avancada.md) | Katz & Lindell, cap. 12 — ver [90-bibliografia.md](90-bibliografia.md) |

**Não é pré-requisito:** saber criptografia. Este material ensina o que você precisa
saber de assinatura digital do zero, em [14-assinatura-jws.md](14-assinatura-jws.md).

---

## Ambiente

| Item | Mínimo | Recomendado | Por quê |
|---|---|---|---|
| Sistema operacional | Linux, macOS ou Windows 10+ | Linux ou WSL2 | os exemplos usam `openssl` e utilitários POSIX |
| Node.js | 18 | **24 LTS** | `node --test`, `fetch` nativo, `crypto` moderno |
| Python (opcional) | 3.9 | 3.12+ | só para os exemplos em PyJWT |
| Memória | 1 GB livre | 2 GB | nada aqui é pesado |
| Disco | ~200 MB | 500 MB | Node + material |
| Conexão | necessária para instalar | — | o projeto-modelo roda offline depois de instalado |
| Conta em serviço | **nenhuma** | — | não é preciso conta em Auth0, Okta ou similar |
| Cartão de crédito | **nenhum** | — | tudo neste material é gratuito |

Detalhes por sistema operacional: [03-instalacao.md](03-instalacao.md).

---

## Tempo realista de estudo

Honesto, não otimista. Assume que você tem os pré-requisitos indispensáveis.

| Nível | O que você consegue fazer | Tempo | Arquivos |
|---|---|---|---|
| **Sobreviver** | ler um token, entender um erro 401, saber que ele não é criptografado | **2 h** | 01, 04, e o [jwt.io](https://jwt.io) |
| **Usar com competência** | proteger uma API, escolher tempo de vida, decidir onde guardar no cliente | **1 a 2 dias** | 01–07, 10, 13, 17, 18, 75 |
| **Projetar** | escolher entre sessão e JWT com argumento, desenhar rotação de chave, revogação, multi-serviço | **1 a 2 semanas** | + 12, 14, 16, 19, 20, 21, 22, 70 |
| **Dominar** | auditar uma implementação, ler a RFC e discordar dela com razão, avaliar SD-JWT e DPoP | **2 a 3 meses** | tudo, + as RFCs de [95-referencias.md](95-referencias.md) |
| **Fronteira** | contribuir com a discussão de padrão, publicar pesquisa | **1 a 2 anos** | + papers de [60](60-teoria-avancada.md) e [65](65-estado-da-arte.md) |

O salto que trava a maioria das pessoas é entre "usar" e "projetar", e ele não é de
sintaxe — é de **modelo de ameaça**. Escrever `jwt.sign(...)` leva 5 minutos.
Responder "o que acontece se este token vazar, e em quanto tempo eu percebo?" leva
semanas de leitura. Esse é o assunto real.

---

## Rota de resgate — o que fazer se faltar um pré-requisito

**Não sei HTTP direito.**
Faça só isto, em 90 minutos: rode `curl -v https://exemplo.com` e leia linha por
linha o que subiu e o que desceu. Depois leia
[apis/12-http-por-dentro.md](../apis/12-http-por-dentro.md). É suficiente para
continuar.

**Não sei JSON.**
30 minutos em [json.org](https://www.json.org/json-pt.html). Você já sabe 80% se já
programou.

**Não sei o que é hash.**
Rode `echo -n "oi" | sha256sum`, depois `echo -n "Oi" | sha256sum`. Repare que a
saída muda inteira com uma letra maiúscula, e que ela tem sempre o mesmo tamanho.
Pronto — para começar, é o que basta. O resto vem em
[14-assinatura-jws.md](14-assinatura-jws.md).

**Não sei a diferença entre chave pública e privada.**
Este é o único que vale parar para estudar antes, porque a escolha entre HS256 e
ES256 depende dele e é irreversível na prática. Uma frase para levar: *a chave
privada assina e não sai de casa; a chave pública verifica e pode ser publicada num
outdoor*. Se isso já fez sentido, pode seguir.

**Não sei JavaScript.**
Siga assim mesmo. O código dos exemplos é comentado linha a linha, e
[06-exemplos.md](06-exemplos.md) traz as mesmas receitas em Python, Java, Go e C#.

**Não tenho como instalar nada na máquina.**
[03-instalacao.md](03-instalacao.md) abre com três caminhos que não exigem instalar
coisa alguma.

---

## Autoteste

1. Qual a diferença entre autenticação e autorização? Dê um exemplo de cada num
   sistema que você conhece.
2. Por que "saber criptografia" **não** é pré-requisito deste material, mas "saber a
   diferença entre chave pública e privada" ajuda muito?
3. Quanto tempo, de forma realista, até você conseguir proteger uma API com JWT sem
   copiar de tutorial?
4. Qual é o salto que trava a maioria — e por que ele não é de sintaxe?
5. Você precisa de conta paga em algum serviço para estudar este assunto? E de cartão
   de crédito?
6. Faltando a base de HTTP, qual é o exercício de 90 minutos que resolve?
