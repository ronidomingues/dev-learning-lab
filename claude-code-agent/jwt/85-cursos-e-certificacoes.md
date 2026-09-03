# 85 · Cursos gratuitos e certificações

> Nível: todos · **Pesquisado na web em 14/08/2026**
> Links podem expirar. O ano de publicação está indicado quando conhecido.

**Aviso honesto que orienta este arquivo inteiro:** não existe curso longo, gratuito
e bom **dedicado só a JWT** — porque o assunto não dá um curso longo. Ele dá:

- **20 minutos** de "o que é";
- **3 horas** dentro de um curso de autenticação ou de API;
- **um mês** de aprofundamento em segurança, quando você já usa.

Desconfie de "Curso completo de JWT — 40 horas". Ou é um curso de outra coisa com JWT
no título, ou está enchendo linguiça. Este material é, sem falsa modéstia, mais
completo que a maioria do que se encontra por aí — porque foi escrito para atravessar
as doze camadas de profundidade, e quase nenhum curso faz isso.

---

## Parte I · Português 🇧🇷 🇵🇹

### Vídeos gratuitos — para entender o conceito

| Título | Canal | Duração | Nível | Vale? |
|---|---|---|---|---|
| [O que é JWT? Aprenda tudo sobre JSON Web Token](https://www.youtube.com/watch?v=sHyoMWnnLGU) | Hora de Codar | ~20 min | iniciante | ✅ boa introdução; direto ao ponto |
| [JWT (JSON Web Token — Autenticação e Segurança)](https://www.youtube.com/watch?v=Gyq-yeot8qM) | Dicionário do Programador (Filipe Deschamps) | ~15 min | iniciante | ✅ **o melhor para começar**: explica o *porquê*, não só o *como* |
| [Autenticação JWT — tudo o que você precisa saber](https://www.youtube.com/watch?v=dglEyFdOUKM) | — | ~30 min | iniciante/intermediário | ✅ cobre o fluxo completo |
| [Fluxo de autenticação (JWT) completo](https://www.youtube.com/watch?v=-G7Dzbpd1B4) | — | ~40 min | intermediário | ✅ implementação prática |
| [Estratégias de autenticação entre front-end e back-end com JWT (cookies storage)](https://www.youtube.com/watch?v=YcH2kxqK3nc) | Rocketseat | ~1 h | intermediário | ✅ **o mais útil da lista**: trata de onde guardar o token, que é a parte que todo mundo erra |
| [Estratégias de autenticação, JWT, OAuth, qual usar? — Podcast FalaDev #21](https://www.youtube.com/watch?v=mZrt5R9eZzM) | Rocketseat | ~1 h | intermediário | ✅ discussão de **decisão**, não de sintaxe — raro e valioso |

**Recomendação de trilha em vídeo (≈ 3 h):**
Dicionário do Programador → Hora de Codar → Rocketseat (cookies) → FalaDev #21.

### Cursos e minicursos gratuitos

| Recurso | Onde | Nível | Nota |
|---|---|---|---|
| **Minicurso Java com Spring Boot** (API completa com autenticação JWT e deploy) | [Rocketseat](https://www.rocketseat.com.br/) | intermediário | gratuito; JWT é um módulo dentro dele |
| [Curso de JSON Web Tokens: primeiros passos](https://www.devmedia.com.br/curso/o-que-e-jwt/2169) | DevMedia | iniciante | 🟡 **gratuito para assistir, pago para certificar** |
| [Web Services RESTful com JWT em Java](https://www.devmedia.com.br/curso/jwt-web-services-seguros-em-java/2152) | DevMedia | intermediário | 🟡 mesma ressalva |
| [JWT — JSON Web Token (Fundamentos de IdentityServer)](https://desenvolvedor.io/curso/fundamentos-de-identity-server/identityserver4/jwt-json-web-token) | desenvolvedor.io | intermediário | 🇧🇷 trilha .NET; conteúdo sólido |
| [Materiais gratuitos da Rocketseat (lista curada)](https://github.com/nicolas-justin/rocketseat-awesome) | GitHub | vários | agregador útil |

> ⚠️ **"Gratuito para assistir, pago para certificar"** é o modelo da DevMedia e de
> várias plataformas brasileiras. O conteúdo é acessível; o certificado exige
> assinatura. Não há problema nisso — só saiba antes.

### Em português de Portugal

O material específico é escasso. Universidades portuguesas (Universidade Aberta, IST)
publicam material de segurança informática que cobre tokens; procure por
"autenticação baseada em *tokens*" nos repositórios abertos.

---

## Parte II · Inglês 🇬🇧 🇺🇸

### O melhor recurso gratuito de todos

| Recurso | Onde | Por que é o melhor |
|---|---|---|
| **[PortSwigger Web Security Academy — JWT attacks](https://portswigger.net/web-security/jwt)** | PortSwigger | **Laboratórios interativos gratuitos** com aplicações vulneráveis de verdade. Você **executa** `alg: none`, confusão de algoritmo, injeção por `kid`, `jku` e `jwk`. Não é vídeo: é mão na massa, com ambiente pronto. Gratuito, sem cadastro pago. **Se você fizer só uma coisa desta página, faça esta.** |

Tempo: 4 a 8 horas para os laboratórios de JWT. Nível: intermediário. Requer Burp
Suite Community (gratuito).

### Documentação que funciona como curso

| Recurso | Onde | Nota |
|---|---|---|
| [Auth0 — JWT Handbook](https://auth0.com/resources/ebooks/jwt-handbook) | Auth0 | **e-book gratuito** (pede e-mail), ~90 páginas, escrito por Sebastián Peyrott. Excelente sobre a criptografia por baixo. |
| [jwt.io — introdução](https://jwt.io/introduction) | Auth0/Okta | a referência canônica curta |
| [Okta Developer — blog de identidade](https://developer.okta.com/blog/) | Okta | artigos técnicos consistentemente bons |
| [OAuth 2.0 Simplified](https://www.oauth.com/) | Aaron Parecki | **livro gratuito online**, do coeditor do OAuth 2.1. Melhor material de OAuth que existe de graça |
| [`jose` — documentação](https://github.com/panva/jose) | Filip Skokan | a documentação é, ela mesma, um curso de JOSE |
| [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/) | OWASP | referência de segurança, curta e densa |

### Vídeos

| Título | Autor | Duração | Nota |
|---|---|---|---|
| [Everything You Ever Wanted to Know About OAuth and OIDC](https://www.classcentral.com/course/youtube-everything-you-ever-wanted-to-know-about-oauth-and-oidc-198250) | Aaron Parecki (Okta) | ~33 min | ✅ **excelente**; do coeditor do OAuth 2.1 |
| Conteúdo de JWT no [freeCodeCamp](https://www.freecodecamp.org/) | vários | varia | ✅ projetos práticos com Node, Django, Laravel |
| [Class Central — JWT (agregador)](https://classcentral.com/subject/jwt) | agregador | — | 500+ cursos listados; filtre por "free" |
| [Class Central — OAuth 2.0](https://www.classcentral.com/subject/oauth-2-0) | agregador | — | 100+ cursos |

### Especificações como material de estudo

Ler a RFC é subestimado. As do JOSE são curtas e legíveis:

| RFC | Páginas | Vale ler inteira? |
|---|---|---|
| [RFC 7519 — JWT](https://www.rfc-editor.org/rfc/rfc7519) | ~30 | ✅ **sim**, em uma tarde |
| [RFC 8725 — JWT BCP](https://www.rfc-editor.org/rfc/rfc8725) | ~15 | ✅ **sim**, é a mais útil de todas |
| [RFC 7515 — JWS](https://www.rfc-editor.org/rfc/rfc7515) | ~60 | 🟡 as seções 1–5; os apêndices são vetores de teste |
| [RFC 9068 — access token JWT](https://www.rfc-editor.org/rfc/rfc9068) | ~15 | ✅ sim |

---

## Parte III · Francês 🇫🇷

| Recurso | Autor/Plataforma | Duração | Nível | Nota |
|---|---|---|---|---|
| [Découverte du JWT](https://grafikart.fr/tutoriels/json-web-token-presentation-958) | **Grafikart** | ~20 min | iniciante | ✅ **o melhor em francês**. Grafikart é referência estabelecida; explicação clara do problema de centralização que o JWT resolve |
| [Introduction au JWT : principe de fonctionnement](https://www.youtube.com/watch?v=V27fNfRNHkg) | YouTube | ~25 min | iniciante | ✅ boa introdução conceitual |
| [Sécuriser avec JSON Web Token (JWT)](https://fr.linkedin.com/learning/securiser-avec-json-web-token-jwt) | LinkedIn Learning (Denis Voituron) | ~1 h 30 | intermediário | 🟡 **pago** (assinatura), com período de avaliação. Foco .NET/Visual Studio. Bom se você já tem LinkedIn Premium |
| [OpenClassrooms](https://openclassrooms.com/fr/) | — | varia | vários | 🟡 leitura gratuita, certificado pago. Cursos de API e Node cobrem JWT |

O ecossistema francês de conteúdo técnico gratuito é menor que o inglês, mas o
Grafikart é de qualidade real — não é tradução requentada.

---

## Parte IV · Certificações

### A resposta curta

> **Não existe certificação de JWT.** E não deveria existir — o assunto é um
> componente, não uma profissão.

Quem promete "certificação em JWT" está vendendo um PDF sem valor de mercado. Seja
franco consigo mesmo sobre isso.

### O que existe e tem valor

| Certificação | Emissor | Custo | Valor de mercado |
|---|---|---|---|
| **OSCP** | OffSec | ~US$ 1.749 (2026) | 🟢 **alto** em segurança ofensiva. Cobre ataques a autenticação web, JWT incluído |
| **Burp Suite Certified Practitioner (BSCP)** | PortSwigger | ~US$ 99 | 🟢 **bom custo-benefício**; exige os laboratórios da Academy, JWT incluso |
| **CISSP** | ISC² | ~US$ 749 | 🟢 alto em gestão; exige 5 anos de experiência. Não é técnico |
| **eWPT / eWPTX** | INE/eLearnSecurity | ~US$ 400+ | 🟡 reconhecimento médio |
| **AWS Security Specialty** | AWS | US$ 300 | 🟢 bom se você é de nuvem; cobre Cognito |
| **Okta Certified Developer** | Okta | ~US$ 150 | 🟡 valor **restrito ao ecossistema Okta** |
| **Auth0/Okta — trilhas de aprendizado** | Okta | gratuito | conteúdo bom; certificado sem peso fora do ecossistema |

### Certificadores gratuitos — a verdade sem rodeios

| Emissor | O que é | Vale? |
|---|---|---|
| Cursos gratuitos com certificado (Udemy free, Great Learning, Simplilearn) | certificado de conclusão | ❌ **valor de mercado próximo de zero**. Ninguém contrata por isso |
| freeCodeCamp | certificações gratuitas de trilha | 🟡 simbólico; o **portfólio de projetos** é o que vale |
| Class Central (agregador) | lista cursos com certificado gratuito | 🟡 depende do curso |
| **Certificação OpenID** | conformidade de **implementação**, não de pessoa | 🟢 **valiosa — mas para software, não para você** |

### A certificação OpenID, que é diferente de tudo acima

A [OpenID Foundation](https://openid.net/developers/certified-openid-connect-implementations/)
certifica **implementações** — não pessoas. Uma biblioteca ou produto passa numa
suíte de testes de conformidade e entra na lista pública.

Novidade de 2026: a Fundação anunciou o lançamento, em **26 de fevereiro de 2026**,
da autocertificação para OpenID4VP 1.0, OpenID4VCI 1.0 e HAIP 1.0 — ligada a
carteiras e credenciais verificáveis, e disponível para organizações em 38
jurisdições. **As ferramentas de teste de conformidade são gratuitas e de código
aberto**, e podem ser rodadas localmente ou contra servidores da Fundação.

**Por que isso importa para você mesmo sem certificar nada:** rodar a suíte de
conformidade contra a sua implementação é um exercício de aprendizado excelente e
gratuito, e é a forma mais objetiva de descobrir o que você entendeu errado.

---

## Parte V · Como eu estudaria hoje, do zero

Uma trilha concreta, toda gratuita, com tempo estimado:

### Semana 1 — entender (≈ 6 h)

1. Vídeo do Dicionário do Programador (15 min)
2. [01-introducao-leigo.md](01-introducao-leigo.md) e [04-como-comecar.md](04-como-comecar.md) deste material (1 h)
3. **Fabrique um JWT à mão no terminal** ([laboratório 1](70-pratica.md)) (30 min)
4. RFC 7519, inteira (2 h)
5. [10-fundamentos.md](10-fundamentos.md) e [12-anatomia-do-token.md](12-anatomia-do-token.md) (2 h)

### Semana 2 — usar (≈ 10 h)

6. Rode o [projeto-modelo](07-projeto-modelo/) e leia `src/jwt.js` inteiro (3 h)
7. [06-exemplos.md](06-exemplos.md), reproduzindo os exemplos na sua linguagem (4 h)
8. Vídeo da Rocketseat sobre onde guardar o token (1 h)
9. [18-onde-guardar-no-cliente.md](18-onde-guardar-no-cliente.md) (2 h)

### Semana 3 — quebrar (≈ 10 h)

10. **Laboratórios de JWT da PortSwigger Academy** (6 h) ← *o mais importante*
11. [20-ataques-e-defesas.md](20-ataques-e-defesas.md) (2 h)
12. RFC 8725 (1 h)
13. [Laboratório 3](70-pratica.md) — quebre a defesa do projeto-modelo de propósito (1 h)

### Semana 4 — decidir (≈ 8 h)

14. [21-quando-nao-usar.md](21-quando-nao-usar.md) e [17-ciclo-de-vida-sessao.md](17-ciclo-de-vida-sessao.md) (3 h)
15. *OAuth 2.0 Simplified*, de Aaron Parecki (3 h)
16. [Laboratório 12](70-pratica.md) — escreva as sete decisões de arquitetura (2 h)

**Total: cerca de 34 horas, custo R$ 0,00.** Ao final você está acima da média de
mercado no assunto — e não porque assistiu a vídeos, mas porque quebrou coisas de
propósito e escreveu decisões com argumento.

**O que colocar no currículo:** não "certificado em JWT". Coloque o que você
construiu e o que sabe defender numa entrevista: *"implementei autenticação com
rotação de refresh e detecção de reuso; sei explicar por que escolhi ES256 e quando
eu escolheria uma sessão comum"*. Isso vale mais que qualquer PDF.

---

## Autoteste

1. Por que não existe (e não deveria existir) uma certificação de JWT?
2. Qual é o melhor recurso gratuito em inglês, e por que ele bate qualquer vídeo?
3. O que significa "gratuito para assistir, pago para certificar"? Cite uma
   plataforma brasileira que usa esse modelo.
4. Qual é o melhor recurso em francês, e o que ele explica bem?
5. O que a certificação OpenID certifica — e por que ela é útil para você mesmo sem
   certificar nada?
6. Quais duas certificações pagas têm valor de mercado real e cobrem ataques a JWT?
7. Quantas horas leva a trilha completa sugerida, e quanto custa?
8. Por que a semana 3 (quebrar) é a mais importante da trilha?

---

### Fontes consultadas

Pesquisado na web em **14/08/2026**:

- [Class Central — JWT](https://classcentral.com/subject/jwt) e [OAuth 2.0](https://www.classcentral.com/subject/oauth-2-0)
- [PortSwigger Web Security Academy — JWT attacks](https://portswigger.net/web-security/jwt)
- [DevMedia — cursos de JWT](https://www.devmedia.com.br/curso/o-que-e-jwt/2169)
- [Grafikart — Découverte du JWT](https://grafikart.fr/tutoriels/json-web-token-presentation-958)
- [LinkedIn Learning FR — Sécuriser avec JWT](https://fr.linkedin.com/learning/securiser-avec-json-web-token-jwt)
- [Rocketseat — materiais gratuitos](https://github.com/nicolas-justin/rocketseat-awesome)
- [OpenID Foundation — autocertificação a partir de fev/2026](https://openid.net/openid-for-verifiable-credential-self-certification-to-launch-feb-2026/)
- [OpenID Foundation — implementações certificadas](https://openid.net/developers/certified-openid-connect-implementations/)
- Vídeos em português citados, com links diretos na tabela da Parte I

Os preços de certificação são aproximados e mudam. Confirme na fonte oficial.
