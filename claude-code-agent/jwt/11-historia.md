# 11 · História — de onde o JWT veio e que problema resolveu

> Nível: intermediário · Atualizado em 14/08/2026
> Datas de RFCs conferidas contra o RFC Editor. Onde há incerteza, está dito.

A história explica quase toda decisão estranha do padrão. Ler isto economiza muitas
horas de "mas por que diabos eles fizeram assim?".

---

## Linha do tempo

| Ano | Evento | Consequência |
|---|---|---|
| 1994 | Netscape inventa o **cookie** | nasce a sessão por referência; é o padrão por 20 anos |
| 2001–2005 | **SAML** 1.0 → 2.0 (OASIS) | *single sign-on* corporativo, em XML |
| 2002 | **XML Signature** (W3C) | assinatura de documento XML, com canonicalização |
| 2005–2012 | ataques de **XML Signature Wrapping** | prova de que canonicalização é um buraco |
| 2006–2007 | OpenID 1.0/2.0 | identidade descentralizada; fracassa na usabilidade |
| 2009 | **Simple Web Token (SWT)** — Microsoft, Google, Yahoo | token compacto, mas só HMAC e formato `chave=valor` |
| 2009–2010 | **Magic Signatures** (protocolo Salmon, Google) | primeira assinatura sobre JSON com codificação base64url |
| dez/2010 | primeiro rascunho `draft-jones-json-web-token-00` | Mike Jones, John Bradley, Nat Sakimura |
| 2011 | IETF cria o grupo de trabalho **JOSE** | o padrão sai do domínio de uma empresa |
| out/2012 | **RFC 6749** (OAuth 2.0) e **RFC 6750** (Bearer Token) | define `Authorization: Bearer`, mas **não** o formato do token |
| fev/2014 | **OpenID Connect 1.0** final | usa JWT como `id_token` — antes de o JWT ser RFC |
| mar/2015 | **Tim McLean** publica "Critical vulnerabilities in JWT libraries" | `alg: none` e confusão de algoritmo entram no vocabulário |
| **mai/2015** | **RFC 7515–7519** publicadas | JWS, JWE, JWK, JWA, **JWT** viram padrão |
| set/2015 | **RFC 7638** — JWK Thumbprint | `kid` derivável da própria chave |
| jan/2017 | **RFC 8037** — curvas CFRG (Ed25519) no JOSE | chega o `EdDSA` |
| fev/2020 | **RFC 8725** — *JWT Best Current Practices* | o IETF admite por escrito o que deu errado |
| fev/2020 | **RFC 8705** — OAuth com mTLS | primeiro token amarrado ao portador |
| out/2021 | **RFC 9068** — perfil JWT para access token do OAuth | padroniza `typ: at+jwt`, `scope`, `client_id` |
| set/2023 | **RFC 9449** — **DPoP** | prova de posse sem certificado de cliente |
| jan/2025 | **RFC 9700** — *OAuth 2.0 Security BCP* | mata o fluxo *implicit*; exige PKCE e rotação de refresh |
| **nov/2025** | **RFC 9901** — **SD-JWT** (divulgação seletiva) | base técnica das carteiras de identidade digital |
| **mai/2026** | **RFC 9964** — **ML-DSA** para JOSE e COSE | assinatura pós-quântica entra no padrão |

---

## Ato 1 · O mundo XML e por que ele cansou (2001–2010)

O problema do *single sign-on* — entrar uma vez e acessar vários sistemas — foi
resolvido primeiro no mundo corporativo, com **SAML**. E SAML funciona: é maduro,
completo, e ainda hoje é o que sustenta o login de milhares de empresas.

O problema não era o SAML fazer pouco. Era fazer demais, em XML.

Uma asserção SAML típica tem **4 a 8 KB**. Ela precisa de canonicalização XML
(*Exclusive C14N*) antes de assinar, de resolução de espaços de nomes, de validação
de esquema. Nada disso cabe num cabeçalho HTTP, e nada disso é razoável dentro de um
aplicativo de celular em 2010, com processador fraco e rede 3G.

E havia um problema pior que o tamanho: **XML Signature Wrapping**. Uma família de
ataques, documentada academicamente entre 2005 e 2012, em que o atacante reorganiza o
documento XML de modo que o verificador assine/valide um elemento e o processador leia
outro. Os ataques não quebravam a criptografia — quebravam a **distância entre o que
foi verificado e o que foi usado**. A lição ficou, e você vai reconhecê-la no projeto
do JOSE.

Ao mesmo tempo, o mundo dos desenvolvedores migrava de XML para JSON em tudo. Um
token XML numa API JSON era um corpo estranho.

---

## Ato 2 · As tentativas fracassadas (2009–2010)

**Simple Web Token (SWT)**, 2009, proposto conjuntamente por Microsoft, Google e
Yahoo. Compacto: pares `chave=valor` separados por `&`, como uma query string.
Assinado com HMAC-SHA256.

Por que não pegou: **só HMAC**. Sem algoritmo assimétrico não há como um emissor
assinar e mil serviços verificarem sem que todos possam forjar. Para federação de
identidade — o caso de uso principal — isso é fatal. E o formato `chave=valor` não
suporta estrutura aninhada.

**Magic Signatures**, 2009–2010, de John Panzer no Google, parte do protocolo Salmon
(comentários federados em blogs). Aqui aparecem, já reconhecíveis, duas ideias que
sobreviveram: assinar **JSON** e usar **base64url** para transportar sem escapar
nada.

Nenhum dos dois virou padrão. Mas em dezembro de 2010, Mike Jones (Microsoft), John
Bradley (Ping Identity) e Nat Sakimura (NRI) publicaram
`draft-jones-json-web-token-00`, que pegava o compacto do SWT, o JSON do Magic
Signatures e acrescentava o que faltava: algoritmos assimétricos, e um catálogo
extensível de algoritmos.

---

## Ato 3 · A decisão de projeto que define o assunto (2011–2015)

O grupo JOSE do IETF tinha a experiência do XML Signature diante dos olhos. A decisão
central:

> **Não canonicalizar nada. Assinar exatamente os bytes que trafegam.**

Daí vem o formato de três segmentos, o base64url e o fato — que confunde todo
iniciante — de a assinatura cobrir `base64url(header) + "." + base64url(payload)` e
não o JSON.

O preço: o token fica ~33% maior que os dados brutos. Foi pago de olhos abertos, e é
o melhor negócio do padrão. A classe inteira de ataques de *wrapping* simplesmente
não existe no JOSE.

**A decisão de que se arrependeram:** tornar `alg` um campo do próprio token. Parecia
óbvio — como o verificador saberia o algoritmo? — e é o pecado original do formato.
Voltaremos a ele.

Uma coisa que ajuda a entender o padrão: JWS, JWE, JWK, JWA e JWT foram publicadas
**no mesmo dia**, 19 de maio de 2015, como um bloco. Não é uma especificação com
extensões; é um sistema projetado junto.

---

## Ato 4 · Março de 2015: o padrão nasce quebrado

Dois meses **antes** da publicação das RFCs, Tim McLean publicou uma análise que
mudou o assunto. Ele mostrou que a maioria das bibliotecas de JWT existentes tinha
duas falhas críticas, ambas decorrentes da mesma decisão de projeto:

### 4.1 · `alg: none`

A especificação define `none` como algoritmo válido — "JWS não seguro". A intenção
era legítima: usar quando o JWT já está protegido por fora (dentro de um JWE, por
exemplo).

Só que a API típica das bibliotecas era `verify(token, chave)`. Com `alg: none`, a
biblioteca via "sem assinatura", pulava a verificação e **retornava sucesso**. O
atacante montava qualquer payload, punha `{"alg":"none"}` no cabeçalho, deixava o
terceiro segmento vazio, e virava administrador.

### 4.2 · Confusão de algoritmo (RS256 → HS256)

Mais sutil, e mais bonito como ataque. Um serviço verifica com RS256, usando a chave
**pública** do emissor — que é pública por definição.

O atacante pega essa chave pública, monta um token com `{"alg":"HS256"}` e calcula o
HMAC **usando o texto da chave pública como segredo**. Ao receber, a biblioteca lê
`alg: HS256`, vai buscar "a chave" configurada — que é a chave pública RSA —, e a usa
como segredo de HMAC. **Confere.** O atacante forjou um token usando apenas
informação pública.

### 4.3 · A causa raiz, e por que ela é permanente

As duas falhas têm a mesma origem:

> **O token diz como deve ser verificado, e quem manda o token é quem ataca.**

É como um envelope trazer, escrito nele, as instruções para conferir se ele é
autêntico.

Poderiam ter tirado o `alg` do token? Não sem perder a rotação de algoritmo e a
interoperabilidade. A solução real foi transferir a responsabilidade para quem
implementa: **o verificador declara os algoritmos aceitos, e o `alg` do token é
apenas conferido contra essa lista.**

E é por isso que, em 2026 — onze anos depois —, ainda saem CVEs disso:

- **CVE-2026-34950** (`fast-jwt`, CVSS 9,1, publicada em 06/04/2026): um espaço em
  branco no início da chave derrotava a expressão regular que separava chave pública
  de segredo. A confusão de algoritmo, reaberta.
- **CVE-2026-48526** (PyJWT, anterior à 2.13.0): confusão de algoritmo em aplicações
  que validam com JWK cru e suportam famílias mistas de algoritmo.
- Variações de caixa (`nOnE`, `NONE`) que passam por comparações de string sem
  normalização.

Um defeito de projeto de 2015 continua produzindo vulnerabilidades em 2026. Isso é o
que significa "pecado original" em engenharia de software.

Detalhes técnicos e defesas: [20-ataques-e-defesas.md](20-ataques-e-defesas.md).

---

## Ato 5 · Por que o JWT venceu mesmo assim (2015–2020)

Três forças, nenhuma delas técnica em sentido estrito:

**1. O OpenID Connect chegou primeiro.** O OIDC foi finalizado em fevereiro de 2014,
mais de um ano **antes** de o JWT virar RFC, e definiu o `id_token` como um JWT.
Quando Google, Microsoft e Facebook implementaram OIDC, o JWT virou obrigatório para
qualquer um que quisesse "entrar com...". O padrão foi puxado pelo caso de uso.

**2. Microsserviços.** Entre 2014 e 2018 a arquitetura de microsserviços virou
dominante. Nela, a sessão centralizada é um gargalo e um ponto único de falha: 40
serviços consultando o mesmo Redis de sessão. O JWT resolvia isso de forma
convincente — cada serviço verifica localmente.

**3. Aplicativos móveis e SPAs.** Cookies são desconfortáveis fora do navegador. Um
token que cabe num cabeçalho e não depende de política de domínio caiu bem.

**A honestidade que faltou nessa fase:** o JWT foi vendido como "sessão sem estado" e
adotado em milhares de sistemas que teriam sido melhor servidos por um cookie de
sessão comum. A conta chegou entre 2018 e 2022, quando essas equipes descobriram que
precisavam deslogar pessoas. Ver [21-quando-nao-usar.md](21-quando-nao-usar.md).

---

## Ato 6 · A fase adulta (2020–2026)

O padrão amadureceu justamente admitindo os próprios erros.

**RFC 8725 (fev/2020), *JWT Best Current Practices*.** Um documento inteiro dizendo
"não faça o que a RFC 7519 permite". As recomendações principais: exija algoritmos
específicos na validação; valide todas as claims; use `typ` para separar tipos de
token; não use `none`; use chaves fortes.

**RFC 9068 (out/2021).** Até então, o formato do access token do OAuth era
deliberadamente indefinido — cada provedor fazia o seu. A RFC padronizou:
`typ: at+jwt`, `scope`, `client_id`, `auth_time`, e a exigência de validar `aud`.

**RFC 8705 (mTLS) e RFC 9449 (DPoP).** Atacam a limitação mais séria: o *bearer
token*. Quem tem, é. Ambas amarram o token a uma chave que o cliente possui, de modo
que um token roubado seja inútil sem a chave. Ver
[65-estado-da-arte.md](65-estado-da-arte.md).

**RFC 9700 (jan/2025), *OAuth 2.0 Security Best Current Practice*.** Aposenta
formalmente o fluxo *implicit* (token na barra de endereços — vai para o histórico e
para o `Referer`), exige PKCE, exige rotação de refresh token com detecção de reuso.

**RFC 9901 (19/11/2025), SD-JWT.** A mudança conceitual mais interessante em dez
anos: o portador do token pode revelar **apenas parte** das claims, e o verificador
ainda consegue conferir a assinatura do emissor. É a base técnica das carteiras de
identidade digital — provar que se tem mais de 18 anos sem revelar a data de
nascimento.

**RFC 9964 (mai/2026), ML-DSA para JOSE e COSE.** Assinatura pós-quântica
(FIPS 204) com identificadores registrados na IANA. O padrão começa a se preparar
para um computador quântico que ainda não existe.

---

## O que a história ensina

**1. Formato compacto venceu formato completo.** SAML faz mais e é mais seguro por
projeto. O JWT venceu por caber num cabeçalho HTTP. Restrição prática bate elegância
teórica, sempre.

**2. Flexibilidade em campo controlado pelo atacante é dívida permanente.** O `alg`
no token parecia bom projeto em 2011. Produziu CVEs em 2015, 2018, 2022 e 2026.
Quando um formato deixa o remetente escolher como será verificado, essa escolha vai
ser abusada — para sempre.

**3. Um padrão adotado antes de existir carrega os erros de quem o adotou.** O OIDC
usou JWT antes da RFC; o mercado seguiu o OIDC; correções posteriores tiveram de ser
compatíveis com o que já existia.

**4. "Best Current Practice" é um atestado de arrependimento.** Quando o IETF publica
uma BCP para um padrão seu, está dizendo: a especificação permite coisas que não
deveria permitir, e não podemos mais mudá-la.

**5. Opinião profissional, declarada como opinião:** o JWT é um formato bom
implantado errado em milhares de lugares. A tecnologia não é o problema — a narrativa
de "sessão sem estado" que a acompanhou é. A maioria das aplicações web que hoje usa
JWT teria menos código, menos bug e mais segurança com um cookie de sessão comum.

---

## Autoteste

1. Qual problema concreto do XML Signature o JOSE decidiu eliminar, e como?
2. Por que o Simple Web Token não pegou, apesar de compacto e simples?
3. O que Tim McLean publicou em março de 2015, e por que a data importa?
4. Explique a confusão RS256→HS256 em três frases. Qual informação o atacante
   precisa ter?
5. Por que ainda saem CVEs de confusão de algoritmo em 2026? Cite uma.
6. Cite as três forças não técnicas que fizeram o JWT vencer.
7. O que a publicação da RFC 8725 admite implicitamente sobre a RFC 7519?
8. O que a RFC 9901 (SD-JWT) permite que nenhuma versão anterior permitia?
9. Que lição geral de engenharia se tira do campo `alg`?
