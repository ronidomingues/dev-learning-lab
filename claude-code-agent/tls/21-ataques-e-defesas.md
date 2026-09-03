# 21 · Ataques e defesas

**Nível:** avançado · **Data:** 31/08/2026

Catálogo dos ataques que moldaram o TLS. Para cada um: **o que explorava**, **como
funcionava**, **o que sobrou hoje** e **a lição de projeto** que ficou.

Isto não é lista de curiosidades. É a engenharia reversa das recomendações: quando você
souber por que `ssl_protocols TLSv1.2 TLSv1.3;` está lá, nunca mais vai copiá-la sem entender.

---

## 1. Classificação

```
┌── contra o PROTOCOLO ──────────────────────────────────────────────┐
│  downgrade · renegociação · truncamento · confusão de estado       │
├── contra a CRIPTOGRAFIA ───────────────────────────────────────────┤
│  padding oracle · canal lateral de tempo · viés de cifra · nonce   │
├── contra a IMPLEMENTAÇÃO ──────────────────────────────────────────┤
│  Heartbleed · goto fail · CCS injection · parsers de ASN.1         │
├── contra a PKI ─────────────────────────────────────────────────────┤
│  CA comprometida · certificado forjado · MITM autorizado           │
├── contra a APLICAÇÃO ───────────────────────────────────────────────┤
│  SSL stripping · conteúdo misto · verificação desligada · BREACH    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 2. Contra o protocolo

### 2.1 Downgrade / POODLE (2014)

**Explorava:** o *fallback* voluntário dos navegadores. Se o handshake TLS falhasse,
o navegador tentava de novo com uma versão mais antiga — até SSL 3.0. Um atacante
provocava a falha e forçava o rebaixamento; então explorava o preenchimento CBC do
SSL 3.0 (que não é verificável) para decifrar um byte por vez com ~256 tentativas.

**Sobrou hoje:** nada, se o SSL 3.0 estiver desligado (está, em tudo).

**Defesas:** `TLS_FALLBACK_SCSV` (RFC 7507) no TLS 1.2; no TLS 1.3, a sentinela
`DOWNGRD` no `ServerHello.random` ([12 §3.1](12-handshake.md)). Fim do fallback nos navegadores.

**Lição:** *tentar de novo mais fraco anula toda a negociação.* Vale para qualquer
protocolo que você projetar.

### 2.2 Renegociação insegura (CVE-2009-3555)

**Explorava:** o TLS permitia refazer o handshake numa conexão viva, e não havia
vínculo criptográfico entre o handshake antigo e o novo. Um atacante abria uma conexão,
enviava um prefixo (`GET /transferir?para=atacante HTTP/1.1\r\nX-Ignorar: `) e então
"entregava" a conexão à vítima via renegociação. O servidor concatenava o prefixo do
atacante com a requisição autenticada da vítima.

**Sobrou:** nada. Corrigido pela RFC 5746 (renegociação segura, que amarra os
handshakes) e **removida por completo no TLS 1.3**.

**Lição:** *estado de segurança precisa estar amarrado ao contexto em que foi
estabelecido.* É o mesmo princípio do `CertificateVerify` cobrir o transcript inteiro.

### 2.3 Truncamento

**Explorava:** encerrar a conexão TCP sem o `close_notify` do TLS, cortando a resposta.
Se a aplicação processasse a parte recebida (por exemplo, um `logout` que nunca chega),
o atacante manipulava o resultado.

**Defesa:** exigir `close_notify`; a aplicação deve distinguir "fim limpo" de "conexão cortada".

**Lição:** *o fim de uma mensagem também precisa ser autenticado.*

---

## 3. Contra a criptografia

### 3.1 BEAST (2011)

**Explorava:** o IV previsível do CBC no TLS 1.0 — o IV de um registro era o último
bloco cifrado do anterior, e portanto conhecido. Com controle parcial do texto claro
(via JavaScript no navegador), o atacante testava palpites bloco a bloco.

**Sobrou:** nada. TLS 1.1 (2006!) já usava IV explícito. O ataque veio **cinco anos
depois da correção estar disponível** — porque ninguém migrou.

**Lição:** *a correção existir não é a correção acontecer.* Migre cedo. Vale hoje
para o pós-quântico.

### 3.2 CRIME e BREACH (2012, 2013)

**Explorava:** compressão. Se o atacante consegue injetar texto na mesma mensagem que
contém um segredo (um cookie), e observar o **tamanho** do resultado comprimido, ele
descobre o segredo byte a byte: quando o palpite bate, a compressão fica mais eficiente
e a mensagem encolhe.

**CRIME** atacava a compressão do **TLS** — removida do protocolo.
**BREACH** ataca a compressão do **HTTP** (`Content-Encoding: gzip`) — **e continua
tecnicamente viável hoje**.

**Defesas contra BREACH:** não colocar segredos em resposta comprimida junto com
entrada refletida do usuário; token CSRF mascarado por requisição; preenchimento
aleatório na resposta; limitar taxa.

**Lição:** *comprimir dados secretos junto com dados controlados pelo atacante vaza
os secretos.* Isto é geral, e vale para qualquer sistema, não só para TLS.

### 3.3 Lucky13 (2013)

**Explorava:** diferença de **tempo** na verificação do preenchimento CBC — poucos
microssegundos, mas mensuráveis com muitas amostras.

**Defesa:** verificação em tempo constante (difícil de acertar) e, definitivamente,
**AEAD**, que não tem preenchimento a verificar. O TLS 1.3 eliminou CBC.

**Lição:** *tempo é um canal de saída.* Todo código que toca segredo precisa ser de
tempo constante.

### 3.4 FREAK e Logjam (2015)

**Explorava:** as cifras de exportação de 512 bits, herança das leis de exportação
dos EUA nos anos 1990. **FREAK** forçava o servidor a usar RSA-EXPORT; **Logjam**
forçava DH de 512 bits. Fatorar/quebrar 512 bits custava algumas centenas de dólares
em nuvem.

O agravante do Logjam: alguns poucos grupos DH de 1024 bits eram compartilhados por
milhões de servidores. O pré-cálculo contra **um único grupo** — estimado como viável
para um Estado — quebraria todos eles.

**Defesa:** remover as suites EXPORT; grupos DH **nomeados** e ≥2048 bits; no TLS 1.3,
só grupos da lista.

**Lição:** *enfraquecimento deliberado por decreto é dívida técnica de 20 anos.*
É o argumento técnico central contra propostas de "acesso excepcional".

### 3.5 DROWN (2016) e Sweet32 (2016)

**DROWN:** um servidor que ainda aceitasse **SSLv2** — mesmo em outro serviço com a
**mesma chave** (por exemplo, o servidor de e-mail) — permitia decifrar sessões TLS
modernas. **Lição:** *uma chave reutilizada num protocolo fraco compromete todos os
lugares onde ela é usada.*

**Sweet32:** cifras de bloco de **64 bits** (3DES, Blowfish) sofrem colisão de blocos
após ~32 GB no mesmo fluxo, vazando texto claro. Viável em conexões longas.
**Lição:** *o tamanho do bloco importa tanto quanto o tamanho da chave.*

### 3.6 Bleichenbacher e ROBOT (1998, 2017)

**Explorava:** o preenchimento PKCS#1 v1.5 do RSA. O servidor responde de forma
distinguível para "preenchimento válido" e "inválido", virando um **oráculo** que
permite decifrar uma mensagem com ~1 milhão de consultas adaptativas.

**O detalhe que dói:** foi publicado em **1998**. As contramedidas eram conhecidas.
Em **2017**, o ROBOT encontrou a mesma falha em produtos da F5, Citrix, Cisco e
outros — e em servidores do Facebook e do PayPal.

**Defesa:** TLS 1.3 removeu o RSA-transporte; RSA-PSS para assinatura.

**Lição:** *falhas conhecidas ressurgem porque cada implementação nova repete o erro.*
Por isso a solução certa foi **remover a primitiva do protocolo**, não documentar melhor.

### 3.7 Raccoon (2020)

**Explorava:** um canal lateral de tempo na derivação do segredo DH no TLS 1.2, quando
o segredo tinha zeros à esquerda (o TLS 1.2 removia os zeros antes de aplicar o hash,
mudando o tempo de execução).

**Defesa:** TLS 1.3, que fixa o tamanho do segredo. Difícil de explorar na prática.

**Lição:** *normalizar tamanhos evita vazamento por tempo.*

---

## 4. Contra a implementação

### 4.1 Heartbleed (2014, CVE-2014-0160)

Detalhado em [11 §5](11-historia.md). Em uma frase: o OpenSSL confiava no tamanho
declarado pelo cliente e copiava até 64 KB de memória do processo — chaves privadas
inclusive — sem verificar se aquele dado existia.

**A lição menos citada e a mais importante:** o bug foi possível porque o OpenSSL
usava um alocador próprio que reaproveitava memória, contornando as proteções do
sistema. E o projeto era mantido por essencialmente uma pessoa e meia, com ~US$ 2.000
por ano em doações, sustentando a criptografia de metade da internet.
*Infraestrutura crítica sem financiamento é risco sistêmico* — e a resposta (Core
Infrastructure Initiative, LibreSSL, BoringSSL) foi econômica antes de ser técnica.

### 4.2 "goto fail" da Apple (2014, CVE-2014-1266)

```c
    if ((err = SSLHashSHA1.update(&hashCtx, &signedParams)) != 0)
        goto fail;
        goto fail;              // ← linha duplicada, SEM chaves no if
    if ((err = SSLHashSHA1.final(&hashCtx, &hashOut)) != 0)
        goto fail;
```

A segunda `goto fail` executava **sempre**, pulando a verificação da assinatura.
Resultado: iOS e macOS aceitavam **qualquer** assinatura no `ServerKeyExchange` — MITM
trivial contra todos os dispositivos Apple.

**Lição:** *sempre use chaves em blocos condicionais; ligue o aviso do compilador para
código inalcançável; e tenha um teste que verifique que uma assinatura inválida é
REJEITADA.* Um único teste negativo teria pego isso. É por isso que metade dos testes
do [projeto-modelo](07-projeto-modelo/README.md) são ataques.

### 4.3 CCS Injection (2014, CVE-2014-0224) e outros

O OpenSSL aceitava `ChangeCipherSpec` cedo demais no handshake, permitindo forçar
chaves de sessão fracas e previsíveis. Junto com uma longa lista de CVEs em parsers de
ASN.1 (corrupção de memória ao processar certificados malformados).

**Lição:** *máquinas de estado de protocolo precisam ser explícitas e testadas para
transições inválidas.* Trabalhos acadêmicos (`FlexTLS`, `frankencert`) encontraram
dezenas de bugs assim justamente fazendo *fuzzing* de máquinas de estado.

---

## 5. Contra a PKI

Coberto em [13 §5](13-certificados-e-pki.md): DigiNotar (2011), TÜRKTRUST (2013),
Symantec (2017–18), WoSign (2016), TrustCor (2022), Flame (2012).

**O padrão:** o ataque não foi contra a matemática, foi contra o **processo**. E a
defesa que funcionou não foi criptográfica: foi **auditabilidade pública**
(Certificate Transparency).

**Caso especial — o MITM autorizado.** Proxies corporativos de inspeção instalam uma
CA na sua máquina e reassinam todo o tráfego. Tecnicamente é um ataque de intermediário
consentido. Riscos reais e documentados:

- pesquisas encontraram appliances de inspeção que **degradavam** a segurança da conexão
  (aceitando certificados inválidos do lado de fora, oferecendo cifras fracas) — a
  "proteção" deixava a conexão pior do que sem ela;
- o Superfish (2015) veio **pré-instalado** em notebooks Lenovo, com a **mesma chave
  privada de CA em todas as máquinas** — extraída em horas, permitindo a qualquer
  atacante forjar certificados para qualquer usuário.

Verifique se você está sendo inspecionado:

```bash
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null \
  | openssl x509 -noout -issuer
# se o emissor for o nome da sua empresa ou de um fabricante de appliance, você está.
```

---

## 6. Contra a aplicação — onde os incidentes de verdade acontecem

### 6.1 SSL stripping (Moxie Marlinspike, 2009)

O atacante intercepta a **primeira** requisição, que é em HTTP, e serve uma versão da
página com todos os links reescritos para `http://`. O usuário nunca chega ao HTTPS.
Não há aviso de certificado, porque não há TLS.

**Defesa:** **HSTS** ([17 §9](17-configuracao-de-servidores.md)) e, para a primeira
visita, a **lista de preload** embutida nos navegadores.

### 6.2 Verificação desligada — o campeão absoluto

```python
requests.get(url, verify=False)                  # ❌
ssl._create_default_https_context = ssl._create_unverified_context  # ❌❌
```
```javascript
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';  // ❌
```
```go
&tls.Config{InsecureSkipVerify: true}            // ❌
```
```bash
curl -k ...                                      # ❌ como hábito
```

Um estudo clássico (Georgiev et al., *"The Most Dangerous Code in the World"*, CCS 2012)
examinou aplicações e bibliotecas não-navegador e encontrou validação de certificado
quebrada em uma quantidade alarmante delas — em SDKs de pagamento, carrinhos de compra,
clientes de nuvem. A causa raiz apontada: APIs confusas, em que a opção insegura era
mais fácil de escrever que a segura.

**Sempre aparece do mesmo jeito:** alguém encontra um erro de certificado, procura na
internet, acha a resposta "desligue a verificação", o erro some, o commit entra.
E aí você tem criptografia sem autenticação — um canal privado com um desconhecido.

**Como pegar isso no seu código:**

```bash
grep -rn "verify=False\|InsecureSkipVerify\|NODE_TLS_REJECT_UNAUTHORIZED\|rejectUnauthorized: *false\|CERT_NONE\|check_hostname *= *False" . \
  --include=*.py --include=*.js --include=*.ts --include=*.go --include=*.java
```

Coloque esse `grep` no CI. Custa nada e pega a classe inteira.

### 6.3 Conteúdo misto (*mixed content*)

Página HTTPS carregando script por HTTP: o atacante substitui o script e executa código
na sua origem segura. Os navegadores hoje bloqueiam scripts ativos misturados e tentam
promover o resto para HTTPS automaticamente.

```
Content-Security-Policy: upgrade-insecure-requests
```

### 6.4 Cookies sem `Secure`

Um cookie de sessão sem a flag `Secure` é enviado também em requisições HTTP — inclusive
numa requisição que o atacante provoque. TLS não ajuda se o cookie sai por fora.

```
Set-Cookie: sessao=...; Secure; HttpOnly; SameSite=Lax; Path=/
```

---

## 7. Tabela-resumo

| Ataque | Ano | Alvo | Ainda relevante? | O que o mata |
|---|---|---|---|---|
| Renegociação insegura | 2009 | protocolo | não | RFC 5746; removida no 1.3 |
| SSL stripping | 2009 | aplicação | **sim** | HSTS + preload |
| BEAST | 2011 | CBC/TLS 1.0 | não | TLS 1.2+ |
| CRIME | 2012 | compressão TLS | não | compressão removida |
| Lucky13 | 2013 | CBC | não | AEAD |
| BREACH | 2013 | compressão HTTP | **sim** | mascarar segredos, não comprimir com entrada refletida |
| Heartbleed | 2014 | OpenSSL | não | atualizar (mas atualize!) |
| goto fail | 2014 | Apple | não | atualizar |
| POODLE | 2014 | SSL 3.0 | não | desligar SSL 3.0 |
| FREAK / Logjam | 2015 | cifras EXPORT | não | remover EXPORT; grupos nomeados |
| DROWN | 2016 | SSLv2 residual | não | desligar SSLv2 em toda parte |
| Sweet32 | 2016 | 3DES | marginal | AES |
| ROBOT | 2017 | RSA PKCS#1 | não no 1.3 | TLS 1.3 |
| Raccoon | 2020 | DH no TLS 1.2 | marginal | TLS 1.3 |
| **verificação desligada** | sempre | aplicação | **SIM — o nº 1** | revisão de código + CI |
| **CA comprometida** | sempre | PKI | **sim** | CT + CAA + monitoramento |
| **certificado vencido** | sempre | operação | **SIM — o mais frequente** | ACME + monitoramento |

> **Leia a coluna "ainda relevante".** Quase todos os ataques criptográficos famosos
> estão mortos. **Os que continuam derrubando sistemas em 2026 são operacionais e de
> aplicação:** certificado vencido, verificação desligada, cadeia incompleta, HSTS
> ausente, cookie sem `Secure`. É onde vale investir o seu tempo.

---

## 8. O que fazer com tudo isso

**Configuração** (30 minutos, uma vez):
- TLS 1.2 + 1.3, nada abaixo; perfil Intermediate da Mozilla
- HSTS, começando com `max-age` curto ([17 §9](17-configuracao-de-servidores.md))
- CAA no DNS; monitoramento de CT
- cookies com `Secure`, `HttpOnly`, `SameSite`
- CSP com `upgrade-insecure-requests`

**Código** (contínuo):
- `grep` do §6.2 no CI
- teste que **exige falha** com certificado inválido
- nenhuma exceção de "confiar em tudo" fora de um teste explicitamente marcado

**Operação** (contínuo):
- ACME automatizado + monitoramento de validade
- `apt list --upgradable | grep -i ssl` no ciclo de patch
- `testssl.sh` mensal, comparado com o mês anterior
- procedimento de chave comprometida escrito ([20 §9](20-desempenho-e-operacao.md))

---

## Autoteste

1. Qual é a lição de projeto do POODLE sobre *fallback*?
2. Por que a renegociação foi removida do TLS 1.3?
3. Explique CRIME e BREACH. Por que um morreu e o outro não?
4. Por que o BEAST aconteceu cinco anos depois de a correção existir? Que lição isso dá hoje?
5. O que o FREAK/Logjam prova sobre criptografia enfraquecida por lei?
6. Por que o Bleichenbacher ressurgiu como ROBOT 19 anos depois, e qual foi a solução definitiva?
7. Descreva o bug "goto fail". Que tipo de teste o teria pego?
8. Qual foi a lição **econômica** do Heartbleed?
9. Por que um proxy de inspeção corporativo pode deixar sua conexão **pior**?
10. Qual é o ataque nº 1 contra TLS em 2026, e por que ele nem é um ataque criptográfico?
11. Cite três ataques da tabela que **ainda** são relevantes e a defesa de cada um.
12. Escreva o comando de `grep` que pega verificação desligada no seu código.

*Respostas: §2.1, §2.2, §3.2, §3.1, §3.4, §3.6, §4.2, §4.1, §5, §6.2/§7, §7, §6.2.*

---

**Próximo:** [60-teoria-avancada.md](60-teoria-avancada.md) — as provas.
