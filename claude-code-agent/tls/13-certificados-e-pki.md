# 13 · Certificados X.509 e a PKI

**Nível:** intermediário → avançado · **Data:** 31/08/2026

O certificado campo a campo, a cadeia de confiança, quem decide em quem você confia —
e por que este é o pedaço mais frágil e mais político do TLS.

O certificado dissecado abaixo é **real**: foi emitido pela CA do
[projeto-modelo](07-projeto-modelo/README.md) nesta máquina, em 31/08/2026.

---

## 1. O que um certificado é, em uma frase

> Um certificado é uma **declaração assinada** de que uma determinada **chave pública**
> pertence a um determinado **nome**, válida por um determinado **prazo**.

Nada mais. Não é uma senha, não é um segredo, não prova competência nem idoneidade.
É público — pode ser publicado num outdoor. O que é secreto é a **chave privada**
correspondente, e a única coisa que o certificado faz é dizer quem é o dono dela.

---

## 2. Anatomia, campo a campo

```
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:
            15:d0:68:18:70:2d:58:9d:fe:56:4d:9e:34:df:07:92:f3:17:47:04
        Signature Algorithm: ecdsa-with-SHA256
        Issuer: O = Cofre TLS, CN = Cofre TLS Root CA
        Validity
            Not Before: Aug 31 19:43:08 2026 GMT
            Not After : Nov 29 19:43:08 2026 GMT
        Subject: O = Cofre TLS, CN = cofre.interno
        Subject Public Key Info:
            Public Key Algorithm: id-ecPublicKey
                Public-Key: (256 bit)
                pub: 04:09:f6:f2:69:8f:09:47:90:d1:70:98:5f:ca:f5:...
                ASN1 OID: prime256v1
                NIST CURVE: P-256
        X509v3 extensions:
            X509v3 Basic Constraints: critical
                CA:FALSE
            X509v3 Key Usage: critical
                Digital Signature, Key Encipherment
            X509v3 Extended Key Usage:
                TLS Web Server Authentication
            X509v3 Subject Key Identifier:
                7F:80:2F:0D:61:06:CC:08:FA:B8:56:F8:B0:9F:BE:BA:99:39:04:60
            X509v3 Authority Key Identifier:
                07:D1:E7:55:9F:2F:2E:26:83:A7:EF:B9:EB:6E:77:2D:B8:B8:59:49
            X509v3 CRL Distribution Points:
                URI:http://localhost:8080/ca.crl
            X509v3 Subject Alternative Name:
                DNS:localhost, DNS:cofre.interno, IP Address:127.0.0.1
    Signature Algorithm: ecdsa-with-SHA256
    Signature Value: 30:44:02:20:...
```

| Campo | O que é | O que dá errado |
|---|---|---|
| **Version: 3** | X.509v3, de 1996. É o que existe. v1 não tem extensões e é inútil hoje | um certificado v1 não tem SAN → rejeitado |
| **Serial Number** | identificador único **dentro daquela CA**. Deve ter ≥64 bits de entropia | seriais previsíveis viabilizaram ataques de colisão contra MD5 (Flame, 2012) |
| **Signature Algorithm** | como a CA assinou | SHA-1 aqui = rejeitado desde 2017 |
| **Issuer** | o *Subject* de quem assinou. É o elo da cadeia | `Issuer == Subject` → autoassinado |
| **Validity** | `notBefore`/`notAfter`, em UTC | relógio errado no cliente derruba conexões válidas |
| **Subject** | a quem pertence. O `CN` aqui é **decorativo** desde 2017 | confiar no CN em vez do SAN |
| **Subject Public Key Info** | **o conteúdo útil**: o algoritmo e a chave pública | chave fraca (RSA 1024) → rejeitada |
| **Extensões** | quase toda a semântica moderna | ver §3 |
| **Signature Value** | a assinatura da CA sobre tudo acima | — |

### 2.1 O detalhe do `critical`

Uma extensão marcada como `critical` significa: **quem não entender esta extensão deve
recusar o certificado**. Não entendeu, não usa. Uma extensão não crítica que o cliente
não conhece pode ser ignorada.

É por isso que `basicConstraints` e `keyUsage` são sempre críticos: se um cliente
antigo ignorasse `CA:FALSE`, um certificado de folha poderia ser usado para assinar
outros certificados. E foi exatamente isso que aconteceu na prática — ver §5.

---

## 3. As extensões que importam

| Extensão | Para quê | Consequência de errar |
|---|---|---|
| **subjectAltName (SAN)** | **os nomes que o certificado cobre.** DNS, IP, e-mail, URI | sem SAN → não funciona em navegador nenhum desde 2017 |
| **basicConstraints** | `CA:TRUE/FALSE` e `pathlen` | `CA:TRUE` indevido = quem tem esse certificado emite qualquer coisa |
| **keyUsage** | o que a chave pode fazer: assinar, cifrar, assinar certificados, assinar CRL | chave de servidor com `keyCertSign` é uma CA disfarçada |
| **extendedKeyUsage** | `serverAuth`, `clientAuth`, `emailProtection`, `codeSigning`… | sem separação, o certificado de um cliente serve para se passar por servidor |
| **authorityKeyIdentifier** | identifica **qual** chave da CA assinou | necessário quando a CA tem várias chaves (rotação) |
| **subjectKeyIdentifier** | identifica a chave deste certificado | usado para montar a cadeia rapidamente |
| **crlDistributionPoints** | onde baixar a CRL | sem isto, revogação por CRL é impossível |
| **authorityInfoAccess (AIA)** | URL do respondedor OCSP e do certificado do emissor | navegadores usam para buscar intermediário faltante |
| **certificatePolicies** | qual política de validação (DV/OV/EV) | — |
| **SCT** (*Signed Certificate Timestamps*) | provas de que foi publicado em logs de CT | sem SCTs, o Chrome recusa certificados públicos desde 2018 |
| **nameConstraints** | limita uma CA a certos domínios | usada para conter CAs corporativas; pouco adotada |

### 3.1 Curingas (*wildcards*), com as regras exatas

`*.exemplo.com.br` cobre:

| Nome | Coberto? |
|---|---|
| `www.exemplo.com.br` | ✅ |
| `api.exemplo.com.br` | ✅ |
| `exemplo.com.br` (o apex, sem subdomínio) | ❌ — precisa estar no SAN separadamente |
| `a.b.exemplo.com.br` | ❌ — o curinga cobre **um** nível só |
| `*.com.br` | ❌ — proibido: não se emite curinga sobre sufixo público |

O `*` só pode aparecer no rótulo mais à esquerda. `www.*.exemplo.com` é inválido.

**Custo escondido do curinga:** uma única chave privada passa a valer para todos os
subdomínios. Se ela vazar num servidor secundário mal cuidado, o atacante se passa por
todos os outros. Com ACME automatizado, emitir um certificado por nome costuma ser
melhor que um curinga — a comodidade do curinga era resposta a um problema (emissão
cara e manual) que deixou de existir.

---

## 4. A cadeia de confiança

```
   ┌─────────────────────────────────────────┐
   │  RAIZ (self-signed)                     │  guardada OFFLINE, validade 10-25 anos
   │  Subject: CN=ISRG Root X1               │  está no SEU sistema, veio de fábrica
   │  Issuer:  CN=ISRG Root X1   ← igual!    │
   └───────────────┬─────────────────────────┘
                   │ assina
   ┌───────────────▼─────────────────────────┐
   │  INTERMEDIÁRIO                          │  em uso diário, validade ~5 anos
   │  Subject: CN=R11                        │  o servidor DEVE enviá-lo
   │  Issuer:  CN=ISRG Root X1               │
   └───────────────┬─────────────────────────┘
                   │ assina
   ┌───────────────▼─────────────────────────┐
   │  FOLHA (o seu site)                     │  validade curta (≤200 dias desde 03/2026)
   │  Subject: CN=exemplo.com.br             │
   │  Issuer:  CN=R11                        │
   │  SAN: exemplo.com.br, www.exemplo...    │
   └─────────────────────────────────────────┘
```

**Por que existe um intermediário, em vez de a raiz assinar direto?**

Percorrendo os porquês:
*(1)* Porque a chave da raiz precisa ficar **offline**, num cofre, em HSM, sem
conexão de rede. *(2)* Por quê? Porque se ela vazar, todos os certificados que ela
já emitiu ficam suspeitos, e ela não pode ser revogada — ela **é** a âncora.
*(3)* E por que não pode ser revogada? Porque revogar exige alguém acima, e não há
ninguém acima da raiz; a única saída é remover a raiz dos root stores do mundo
inteiro, o que leva **anos** para chegar a todos os dispositivos. *(4)* Por que anos?
Porque root stores viajam com atualizações de sistema operacional, e há bilhões de
aparelhos que não atualizam — TVs, caixas eletrônicos, carros, celulares antigos.
*(5)* **Parada:** é um trade-off econômico e logístico da distribuição de software em
escala planetária. A resposta é: separa-se em duas camadas para que a chave que assina
todo dia (o intermediário) possa ser revogada e substituída sem tocar na âncora.

**Consequência prática que você vai encontrar:** o servidor precisa enviar
folha + intermediário(s), **sem a raiz**. Enviar a raiz é desperdício (o cliente já a
tem); não enviar o intermediário é o erro nº 1 do mundo real
([04 §Erro 1](04-como-comecar.md), [06 Exemplo 8](06-exemplos.md)).

### 4.1 Como o cliente valida — o algoritmo, passo a passo

1. **Monta o caminho** da folha até uma raiz do seu root store, usando `Issuer` e
   `authorityKeyIdentifier`. (Pode haver vários caminhos válidos — *path building* é
   um problema surpreendentemente difícil, e implementações divergem.)
2. Para cada elo: **verifica a assinatura** com a chave pública do elo de cima.
3. Verifica **validade temporal** de cada certificado do caminho.
4. Verifica **`basicConstraints`**: todo elo intermediário tem de ter `CA:TRUE` e
   `pathlen` compatível com a profundidade.
5. Verifica **`keyUsage`** de cada CA: tem de incluir `keyCertSign`.
6. Verifica **revogação** (CRL/OCSP/stapling) — [15](15-validacao-revogacao-transparencia.md).
7. Verifica **`extendedKeyUsage`**: a folha precisa de `serverAuth`.
8. Verifica **SCTs** de Certificate Transparency (obrigatório no Chrome para certificados públicos).
9. **Verifica o nome**: o host solicitado tem de casar com o SAN. *Esta etapa é
   separada e independente das anteriores* — e é a que mais falta em código escrito à mão.
10. Verifica **algoritmos e tamanhos de chave** contra a política mínima.

> ### O erro que quase todo cliente feito à mão comete
> Validar a cadeia **e esquecer o passo 9**. O código conecta, o OpenSSL diz que a
> cadeia é válida, e tudo parece certo — mas o atacante apresentou um certificado
> perfeitamente válido, emitido para **o domínio dele**. Você está falando com um
> estranho, com cadeado. Em Python, `ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)` já liga
> `check_hostname`; `SSLContext(ssl.PROTOCOL_TLS)` **não**. Essa diferença de uma
> constante é a fronteira entre seguro e inútil.

---

## 5. Quem decide em quem você confia

### 5.1 Os quatro root stores que importam

| Root store | Quem administra | Usado por |
|---|---|---|
| **Mozilla CA Program** | Mozilla, público e transparente | Firefox, e — na prática — a maior parte do Linux, curl, Python, Java |
| **Microsoft Trusted Root** | Microsoft | Windows, Edge, .NET |
| **Apple Root Program** | Apple | macOS, iOS, Safari |
| **Chrome Root Store** | Google (desde 2022, próprio) | Chrome em todas as plataformas |

Antes de 2022 o Chrome usava o root store do sistema operacional. Passar a ter o
próprio deu ao Google controle direto sobre a confiança de ~65% dos navegadores do
mundo — e tornou as decisões mais rápidas e mais unilaterais.

**As regras comuns** vêm do **CA/Browser Forum**, um consórcio de CAs e fabricantes de
navegadores que publica os *Baseline Requirements*. Não é um órgão governamental nem
um padrão da IETF: é um acordo privado entre empresas. Suas decisões — como a redução
da validade para 47 dias — valem porque quem não cumpre é removido dos navegadores,
o que equivale a deixar de existir comercialmente.

### 5.2 O que já deu errado — casos documentados

| Caso | Ano | O que houve | Resultado |
|---|---|---|---|
| **DigiNotar** | 2011 | invadida; emitiu `*.google.com` fraudulento, usado para espionar ~300 mil usuários iranianos | removida dos navegadores; a empresa faliu em semanas |
| **TÜRKTRUST** | 2013 | emitiu por engano dois certificados **intermediários** em vez de folhas; um deles foi usado para gerar `*.google.com` | sanções; motivou o *pinning* no Chrome |
| **Symantec** | 2017–18 | milhares de certificados emitidos sem validação adequada; auditorias falhas | Google desconfiou progressivamente; a operação foi vendida à DigiCert |
| **WoSign/StartCom** | 2016 | emissões retroativas, controle de propriedade ocultado | removidas |
| **TrustCor** | 2022 | ligações societárias com uma empresa de vigilância que produzia spyware | removida do Mozilla e do Chrome |
| **Flame** (malware) | 2012 | forjou certificado da Microsoft explorando colisão MD5 e serial previsível | fim definitivo do MD5; seriais aleatórios obrigatórios |
| **e-Tugra** | 2023 | pesquisador achou credenciais expostas e falhas graves na infraestrutura | desconfiada |

**O padrão em todos eles:** o problema nunca foi a matemática. Foi processo,
governança, incentivo e, em alguns casos, coação estatal.

### 5.3 O que sobrou como defesa

| Defesa | O que faz | Limite |
|---|---|---|
| **Certificate Transparency** | toda emissão pública vai para logs append-only auditáveis | detecta **depois** da emissão, não impede |
| **CAA** (registro DNS) | você declara quais CAs podem emitir para o seu domínio | a CA é quem checa; não impede uma CA maliciosa |
| **pinning** (em app próprio) | ignora o root store, exige sua chave | derruba o app se você errar; inviável na web aberta |
| **nameConstraints** | limita uma CA a certos domínios | pouco usado; suporte irregular |
| **monitoramento de CT** | alerta quando alguém emite para o seu domínio | reativo, mas custa uma chamada HTTP por dia |

Configure o CAA hoje, leva dois minutos:

```
exemplo.com.br.  IN  CAA  0 issue "letsencrypt.org"
exemplo.com.br.  IN  CAA  0 issuewild ";"
exemplo.com.br.  IN  CAA  0 iodef "mailto:seguranca@exemplo.com.br"
```

```bash
dig +short CAA exemplo.com.br
```

A primeira linha diz "só o Let's Encrypt pode emitir"; a segunda proíbe curingas; a
terceira pede que violações sejam reportadas para esse e-mail. Desde 2017 a
verificação do CAA é **obrigatória** para todas as CAs públicas.

---

## 6. Os níveis de validação: DV, OV, EV

| Nível | O que a CA verifica | Tempo | Preço típico |
|---|---|---|---|
| **DV** (*Domain Validated*) | só que você controla o domínio (via HTTP, DNS ou e-mail) | segundos | **R$ 0** (Let's Encrypt) |
| **OV** (*Organization Validated*) | além disso, que a organização existe legalmente | dias | R$ 300–1.500/ano |
| **EV** (*Extended Validation*) | verificação documental reforçada, segundo um roteiro do CA/B Forum | 1–3 semanas | R$ 800–5.000/ano |

> ### Opinião profissional, marcada como opinião
> **Para a esmagadora maioria dos casos, OV e EV não valem o dinheiro.**
> O argumento de venda do EV era a **barra verde com o nome da empresa** no navegador.
> Chrome e Firefox **removeram esse indicador em 2019**, depois de pesquisas mostrarem
> que praticamente nenhum usuário reparava nele — e depois que pesquisadores
> demonstraram registrar empresas com nomes ambíguos para obter EVs enganosos.
> Hoje, um EV e um DV aparecem **idênticos** para o usuário. Criptograficamente,
> **são idênticos**: mesma cifra, mesma força, mesma proteção.
>
> O que resta de real: alguns setores regulados exigem OV/EV por contrato ou norma,
> e alguns clientes corporativos pedem por política. Se é um requisito, cumpra. Se é
> uma escolha técnica sua, escolha DV automatizado e gaste o orçamento em
> monitoramento e resposta a incidente, que reduzem risco de verdade.
> Isto é opinião fundamentada, não consenso universal — há profissionais sérios que
> defendem OV por rastreabilidade jurídica em caso de fraude.

---

## 7. Nomes, codificação e o inferno do ASN.1

Certificados são codificados em **DER**, uma serialização binária de **ASN.1** —
uma notação de descrição de dados dos anos 1980, do mundo das telecomunicações.

Isso tem consequências práticas:

- **É complexo de analisar**, e parsers de ASN.1 são fonte histórica de
  vulnerabilidades de corrupção de memória (várias CVEs no OpenSSL e no GnuTLS).
- **Há mais de uma forma de codificar a mesma coisa** (`PrintableString`, `UTF8String`,
  `IA5String`, `BMPString`). Duas implementações podem discordar sobre se dois nomes
  são "iguais" — e é daí que vieram os ataques de byte nulo (`banco.com\0.mau.com`),
  onde a CA lia o nome inteiro e o cliente parava no byte nulo.
- **Nomes internacionalizados** viram Punycode (`xn--...`), abrindo espaço para
  homógrafos: `аpple.com` com "а" cirílico é um domínio diferente de `apple.com`, e
  o certificado dele é perfeitamente válido. Os navegadores mitigam mostrando o
  Punycode quando o domínio mistura alfabetos.

**Por que ASN.1/DER e não JSON?** Resposta histórica: o X.509 nasceu em 1988 como parte
do X.500, o diretório de assinantes da ITU-T, num mundo em que cada byte de linha
telefônica custava caro e JSON não existiria por mais uma década. Ficou por
compatibilidade — bilhões de dispositivos falam esse formato. É uma **convenção
arbitrária congelada por inércia**, e essa é a resposta honesta.

---

## 8. Ver tudo isso com as mãos

```bash
# 1. Suas âncoras de confiança: quantas são?
awk '/BEGIN CERT/{n++} END{print n" raízes confiáveis"}' /etc/ssl/certs/ca-certificates.crt

# 2. Quem são elas
awk -v cmd='openssl x509 -noout -subject' '/BEGIN/{close(cmd)};{print | cmd}' \
  /etc/ssl/certs/ca-certificates.crt | sed 's/.*CN *= *//' | sort | head -20

# 3. Quando a mais antiga vence
awk -v cmd='openssl x509 -noout -enddate' '/BEGIN/{close(cmd)};{print | cmd}' \
  /etc/ssl/certs/ca-certificates.crt | sort -t= -k2 | head -3

# 4. Todo certificado já emitido para um domínio (Certificate Transparency)
curl -s "https://crt.sh/?q=exemplo.com.br&output=json" | \
  python3 -c "import sys,json;[print(r['issuer_name'][:60],r['not_before'][:10]) for r in json.load(sys.stdin)[:15]]"

# 5. O CAA do domínio
dig +short CAA exemplo.com.br
```

---

## Autoteste

1. O que exatamente um certificado declara? O que ele **não** prova?
2. Por que o `CN` não deve ser usado para verificar o nome do host, e desde quando?
3. O que significa uma extensão marcada como `critical`?
4. Por que existe um intermediário entre a raiz e a folha? Percorra os porquês.
5. `*.exemplo.com.br` cobre `exemplo.com.br`? E `a.b.exemplo.com.br`?
6. Liste os dez passos da validação de cadeia. Qual deles é o mais esquecido?
7. Quem administra os quatro root stores relevantes, e quem escreve as regras comuns?
8. O que o caso DigiNotar e o caso Symantec têm em comum?
9. Qual é a diferença criptográfica entre um certificado DV e um EV?
10. Como o registro CAA ajuda, e qual é o limite dele?
11. Por que certificados usam ASN.1/DER e não um formato moderno?
12. Qual é o custo escondido de um certificado curinga?

*Respostas: §1, §2/§3, §2.1, §4, §3.1, §4.1, §5.1, §5.2, §6 (nenhuma), §5.3, §7, §3.1.*

---

**Próximo:** [14-criptografia-do-tls.md](14-criptografia-do-tls.md) — as primitivas por dentro.
