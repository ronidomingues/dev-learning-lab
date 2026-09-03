# 18 · Segurança web — o OWASP Top 10:2025 explicado por causa-raiz

`Nível: intermediário → avançado` · `Última atualização: 12/08/2026`

A web é a porta de entrada mais comum da carreira, das vagas e do dinheiro em bug bounty. Este
arquivo destrincha o **OWASP Top 10:2025** — não decorando a lista, mas entendendo a
causa-raiz de cada categoria e como testá-la. Laboratório: PortSwigger Web Security Academy
(gratuita), DVWA, Juice Shop ([`03`](03-instalacao.md) §6).

> A lista **OWASP Top 10:2025** foi anunciada em nov/2025 (Global AppSec, Washington) e
> finalizada em jan/2026. Base: 175.000+ CVEs, 248 CWEs mapeados. Duas categorias novas.

---

## 1. Como a web funciona (o mínimo para atacar)

Uma requisição HTTP tem: **método** (GET, POST…), **caminho**, **cabeçalhos** (incluindo
cookies e `Authorization`) e **corpo**. O servidor responde com **status** (200, 302, 403,
500), cabeçalhos e corpo. Tudo isso é texto que o atacante controla e edita — via Burp ([`05`](05-manual-de-uso.md) §4).

O princípio-mestre (de [`10`](10-fundamentos.md)): **nada que venha do cliente é confiável.**
Cookie, parâmetro, cabeçalho, corpo — todos podem ter sido forjados. Validação de segurança só
vale no **servidor**. Guarde isto; ele explica quase todo o Top 10.

## 2. OWASP Top 10:2025 — a lista

| # | Categoria | Mudança vs. 2021 |
|---|---|---|
| **A01** | Broken Access Control | permanece nº 1; **absorveu SSRF** |
| **A02** | Security Misconfiguration | subiu |
| **A03** | Software Supply Chain Failures | **NOVA** (era "Vulnerable Components", agora ampliada) |
| **A04** | Cryptographic Failures | — |
| **A05** | Injection | desceu (inclui SQLi, XSS, cmd injection) |
| **A06** | Insecure Design | — |
| **A07** | Authentication Failures | renomeada |
| **A08** | Software or Data Integrity Failures | — |
| **A09** | Logging & Alerting Failures | renomeada |
| **A10** | Mishandling of Exceptional Conditions | **NOVA** |

> ⚠️ Numeração/nomes podem ser ajustados na consolidação final da OWASP — confira em
> [owasp.org/Top10](https://owasp.org/Top10/) antes de citar num relatório. As **classes de
> falha** abaixo são estáveis independentemente da posição exata.

---

## 3. A01 · Broken Access Control (nº 1)

A aplicação não verifica **se você pode** acessar o recurso/ação. Autentica, mas não autoriza
por objeto.

**Sub-tipos e como testar:**
- **IDOR:** trocar um id (`/api/fatura/1043` → `1044`) devolve dado de outro. Ver [`06`](06-exemplos.md) ex. 9.
- **Escalação vertical:** usuário comum acessa função de admin (`/admin`) sem ser admin.
- **Escalação horizontal:** usuário A age como usuário B.
- **Path traversal:** `../` para ler arquivos fora da pasta. Ver projeto-modelo F-02.
- **SSRF** (agora aqui): forçar o servidor a fazer requisições que você escolhe — clássico para
  alcançar o *metadata service* da nuvem (`169.254.169.254`) e roubar credenciais. Ver [`21`](21-nuvem-e-containers.md).

**Causa-raiz:** confiar no identificador/rota que o cliente controla, sem checar dono/papel no
servidor. **Defesa:** negar por padrão; verificar autorização por objeto, em cada requisição,
no servidor; derivar identidade da sessão, não do parâmetro.

## 4. A05 · Injection (SQLi, XSS, comando)

Entrada do usuário vira parte de uma linguagem interpretada.

### SQL Injection
Entrada concatenada numa query. Detecção e exploração manual em [`06`](06-exemplos.md) ex. 3.
Tipos: *in-band* (UNION, error-based), *blind* (boolean/time-based), *out-of-band*. Automação:
`sqlmap` ([`05`](05-manual-de-uso.md) §5). **Defesa:** *prepared statements* (queries
parametrizadas) — a entrada vira **dado**, nunca **código**. É a defesa definitiva; sanitização
manual é frágil.

### XSS (Cross-Site Scripting)
Entrada vira HTML/JS no navegador de **outro** usuário. Refletido, armazenado, DOM-based — ver
[`06`](06-exemplos.md) ex. 4. **Defesa:** escapar na saída conforme o contexto (HTML, atributo,
JS, URL); Content-Security-Policy; cookies `HttpOnly`.

### Command Injection
Entrada vira comando do SO. Ver [`16`](16-vulnerabilidades-e-exploracao.md) §4.

**Causa comum:** misturar dados de controle (código) com dados do usuário. **Defesa geral:**
separar dado de código — parametrizar, escapar por contexto, allowlist.

## 5. A07 · Authentication Failures

Falhas em provar identidade:
- Senhas fracas aceitas, sem rate limit → força bruta (projeto-modelo F-04).
- Enumeração de usuário (mensagem "usuário não existe" ≠ "senha errada").
- Gestão de sessão fraca: token previsível, sem expiração, sem invalidar no logout.
- Recuperação de senha insegura, ausência de MFA.

**Testar:** tentar credenciais padrão, medir resposta a força bruta, analisar o token de
sessão (aleatório? expira?), testar o fluxo de "esqueci a senha". **Defesa:** MFA, rate
limit/bloqueio, hash forte de senha (argon2/bcrypt), tokens aleatórios com expiração,
mensagens de erro genéricas.

## 6. A04 · Cryptographic Failures

Dados sensíveis mal protegidos: senha em texto (projeto-modelo F-04), HTTP sem TLS, hash fraco
(MD5/SHA1 para senha), chave hardcoded, criptografia caseira. **Testar:** procurar dado
sensível em trânsito (sem HTTPS) e em repouso (como as senhas são guardadas). **Defesa:** TLS
em tudo, argon2/bcrypt para senha, algoritmos padrão bem configurados, gestão de chaves.

## 7. A02 · Security Misconfiguration & A10 · Mishandling of Exceptional Conditions

- **A02:** padrões inseguros, portas/serviços desnecessários, permissões largas, cabeçalhos de
  segurança ausentes, painéis de admin expostos, verbosidade demais.
- **A10 (nova):** o programa reage mal a condições excepcionais — vaza *stack trace* e segredos
  em erro (projeto-modelo F-05), falha "aberto" (fail-open) em vez de "fechado", trata mal
  timeouts e entradas inesperadas. **Causa-raiz:** o "caminho de erro" não recebeu o mesmo
  cuidado do "caminho feliz". **Defesa:** erros genéricos ao cliente + detalhe só no log;
  fail-closed; testar entradas malformadas deliberadamente.

## 8. A03 · Software Supply Chain Failures (nova, ampliada)

Você não é atacado diretamente — é atacada uma **dependência** sua ou o **processo** que a
entrega. Engloba componentes com CVE (o antigo "Vulnerable and Outdated Components"), pacotes
maliciosos (typosquatting no npm/PyPI), build comprometido (SolarWinds), e o próprio pipeline
de CI/CD. **Log4Shell** (CVE-2021-44228) e SolarWinds são os casos que forçaram esta categoria.
**Testar:** inventariar dependências (SBOM), checar versões contra CVEs, ver se o pipeline é
seguro. **Defesa:** SBOM, fixar versões, verificar integridade (assinatura/hash), scanning de
dependência, princípio de menor confiança no build.

## 9. A06 · Insecure Design & A08 · Integrity Failures & A09 · Logging Failures

- **A06 Insecure Design:** a falha está no **projeto**, não na implementação — faltou pensar no
  abuso. Ex.: fluxo de compra que permite desconto de 200% por lógica; recuperação de senha
  por pergunta secreta adivinhável. Não se corrige com patch; corrige-se com *threat modeling*.
- **A08 Integrity Failures:** aceitar código/atualização/dado sem verificar integridade
  (deserialização insegura, update sem assinatura). Parente da A03.
- **A09 Logging & Alerting Failures:** não registrar/alertar o suficiente para detectar e
  responder. Do lado ofensivo: se o alvo não loga, você age impune — e o relatório aponta isso.

## 10. Fluxo de um teste web (juntando tudo)

```
1. Mapear:    ffuf/feroxbuster + Burp Site map → todas as rotas e parâmetros
2. Fingerprint: whatweb, cabeçalhos, cookies → tecnologia
3. Por entrada, perguntar (WSTG como checklist):
   - vai para um banco?      → testar Injection (A05)
   - controla um recurso?    → testar Access Control (A01, IDOR)
   - reflete na página?      → testar XSS (A05)
   - é upload/arquivo?       → testar path traversal / RCE (A01/A05)
   - é login/sessão?         → testar Auth (A07)
   - força o servidor a pedir algo? → SSRF (A01)
4. Erros: provocar exceções → A10, A02 (vazamento)
5. Dependências/headers: A02, A03
6. Lógica de negócio: A06 (o que scanner não acha — onde está o ouro)
```

**Referência de cobertura:** OWASP **WSTG** ([`13`](13-metodologias-e-frameworks.md)) e **ASVS**
como critério de "passou/não passou".

## 11. Os cinco porquês: por que Broken Access Control é sempre o nº 1?

**Por quê 1** — Por que falha de controle de acesso lidera a lista há anos?
Porque autorização é *específica de cada objeto e cada regra de negócio* — há milhares de
pontos onde checar, e basta esquecer um.

**Por quê 2** — Por que se esquece de checar em algum ponto?
Porque autorização não é uma feature visível; é uma checagem invisível que precisa estar em
**todo** endpoint. O "caminho feliz" funciona sem ela — o bug não aparece em teste funcional.

**Por quê 3** — Por que o teste funcional não pega?
Porque o desenvolvedor testa como usuário legítimo, que **tem** direito ao recurso. O bug só
aparece quando alguém pede o recurso de **outro** — o que ninguém testa por acidente.

**Por quê 4** — Por que ferramenta automática não pega?
Porque a ferramenta não sabe **quem deveria** acessar o quê — isso é a lógica de negócio, que
é única de cada app. Scanner acha SQLi (padrão universal), não IDOR (regra específica).

**Por quê 5** — Qual é a parada?
Uma **propriedade estrutural**: autorização correta exige aplicar uma regra contextual em cada
um de milhares de pontos, verificável só por quem conhece a regra, invisível ao teste funcional
e ao scanner. Enquanto software for construído assim, controle de acesso vai liderar — e é por
isso que testá-lo (na mão, entendendo o negócio) é a habilidade web mais valiosa que você pode
ter.

---

## Autoteste

1. Qual princípio único explica quase todo o OWASP Top 10?
2. Por que *prepared statements* é a defesa definitiva contra SQLi, e sanitização manual não?
3. Diferencie escalação vertical e horizontal em Broken Access Control.
4. O que é SSRF e por que ele é perigoso especialmente em ambiente de nuvem?
5. Quais duas categorias são novas em 2025, e que incidentes as motivaram?
6. No projeto-modelo, a qual categoria do Top 10 corresponde cada uma das 5 falhas?
7. Por que um scanner automático acha SQLi mas não IDOR?
8. Por que Broken Access Control é sempre o nº 1? Leve o porquê até o fim.
