# 19 · TLS além do HTTPS

**Nível:** avançado · **Data:** 31/08/2026

TLS protege muito mais que a web. E cada protocolo que o adotou trouxe uma
complicação própria — algumas delas mudam o que "seguro" significa.

---

## 1. E-mail: o caso mais mal resolvido da internet

### 1.1 Dois papéis, duas portas

| Papel | Porta | Como o TLS entra |
|---|---|---|
| **Submissão** (seu cliente → seu servidor) | 587 (STARTTLS) ou **465 (TLS implícito)** | obrigatório na prática; há autenticação |
| **Entrega** (servidor → servidor) | 25 (STARTTLS) | **oportunista** — e aí está o problema |

### 1.2 STARTTLS × TLS implícito

```
TLS implícito (465, 993, 995):     TCP → TLS imediato → protocolo
STARTTLS      (587, 143, 110, 25): TCP → protocolo EM CLARO → comando STARTTLS → TLS
```

STARTTLS começa em claro e **pede** para virar cifrado. Isso cria o ataque de
**STARTTLS stripping**: o atacante no meio remove o anúncio `250-STARTTLS` da resposta
do servidor. O cliente, não vendo a oferta, envia tudo em claro — sem erro nenhum.

> **A RFC 8314 (2018) recomenda TLS implícito** (portas 465/993/995) em vez de
> STARTTLS para submissão e acesso. **Opinião profissional:** para portas de cliente,
> use 465 e 993, e configure o cliente como "SSL/TLS", não "STARTTLS". A distinção
> "465 é obsoleta" que circulou nos anos 2000 foi revertida pela própria IETF.

### 1.3 A entrega entre servidores é oportunista — e por quê

Quando o servidor A entrega uma mensagem para o servidor B na porta 25, ele:
tenta STARTTLS; se falhar, **entrega em claro assim mesmo**. Não valida o certificado
na configuração padrão. Aceita autoassinado. Aceita nome errado.

Percorrendo os porquês: *(1)* Por que tão frouxo? Porque a alternativa seria **não
entregar o e-mail**. *(2)* Por que isso não é opção? Porque e-mail perdido é
inaceitável comercialmente, e o remetente não controla o servidor do destinatário.
*(3)* Por que não exigir certificado válido? Porque em 2010 uma fração enorme dos
servidores de e-mail do mundo tinha certificado autoassinado ou vencido. *(4)* Por que
ninguém corrigiu? Porque o SMTP é de 1982, tem centenas de milhares de operadores
independentes, e não existe autoridade que possa obrigar ninguém. *(5)* **Parada:**
trade-off econômico e de coordenação em escala planetária — entregar sempre venceu
entregar seguro.

**As correções vieram por cima, e são opcionais:**

| Mecanismo | O que faz |
|---|---|
| **MTA-STS** (RFC 8461) | o domínio publica, por HTTPS, uma política dizendo "exija TLS válido para me entregar" |
| **DANE para SMTP** (RFC 7672) | publica no DNSSEC o hash do certificado esperado; exige DNSSEC |
| **TLS-RPT** (RFC 8460) | relatórios diários de falhas de TLS na entrega para o seu domínio |

```
# _mta-sts.exemplo.com.br  TXT
v=STSv1; id=20260831T000000;

# https://mta-sts.exemplo.com.br/.well-known/mta-sts.txt
version: STSv1
mode: enforce
mx: mail.exemplo.com.br
max_age: 604800
```

> **E o mais importante:** mesmo com tudo isso, **TLS no e-mail é salto a salto**
> (*hop-by-hop*), não ponta a ponta. A mensagem é decifrada em cada servidor do caminho.
> Para sigilo de verdade, é preciso **PGP ou S/MIME**, que cifram o conteúdo. TLS
> protege o transporte; não protege a mensagem.

---

## 2. DNS cifrado: DoT, DoH e DoQ

O DNS tradicional é UDP em claro na porta 53. Qualquer um vê **todos** os domínios que
você consulta — o que muitas vezes é mais revelador que o conteúdo.

| Protocolo | Porta | Como | Notas |
|---|---|---|---|
| **DoT** (DNS over TLS, RFC 7858) | **853** | DNS dentro de TLS | fácil de bloquear (porta dedicada); preferido por administradores de rede |
| **DoH** (DNS over HTTPS, RFC 8484) | **443** | DNS dentro de HTTPS | indistinguível de tráfego web; padrão em navegadores |
| **DoQ** (DNS over QUIC, RFC 9250) | 853/UDP | DNS sobre QUIC | menor latência; adoção crescente |

```bash
kdig +tls @1.1.1.1 exemplo.com.br            # DoT
curl -s -H 'accept: application/dns-json' \
  'https://cloudflare-dns.com/dns-query?name=exemplo.com.br&type=A' | head -c 300   # DoH
```

**A controvérsia, com os dois lados:**

*A favor do DoH:* impede que o provedor de internet leia e altere suas consultas —
prática documentada de injeção de publicidade e de censura por DNS. Como usa a 443,
é difícil de bloquear sem bloquear a web.

*Contra o DoH:* centraliza. Se o navegador manda tudo para um punhado de resolvedores
públicos, esses passam a ver o histórico de navegação de milhões de pessoas — troca-se
o provedor local por uma empresa global. Além disso, quebra a filtragem legítima de
redes corporativas e escolares, e complica o *split-horizon* DNS.

**Opinião profissional:** DoT ou DoH apontando para um resolvedor que **você** escolhe
(o da sua empresa, ou um resolvedor local como Unbound) é o melhor dos dois mundos.
O padrão de fábrica do navegador é uma decisão razoável para o usuário médio e uma
decisão ruim para uma rede administrada.

**Ligação com o TLS:** o ECH ([65](65-estado-da-arte.md)) **depende** de DNS cifrado.
Cifrar o SNI não adianta se a consulta de DNS que precedeu a conexão foi feita em claro
e já revelou o domínio. As duas peças só funcionam juntas.

---

## 3. QUIC e HTTP/3: TLS incorporado ao transporte

QUIC (RFC 9000, 2021) roda sobre **UDP** e **incorpora** o TLS 1.3 — não roda "sobre" ele.

```
Pilha clássica:            QUIC:
┌──────────┐               ┌─────────────────────┐
│  HTTP/2  │               │      HTTP/3         │
├──────────┤               ├─────────────────────┤
│   TLS    │               │  QUIC (inclui o     │
├──────────┤               │  handshake TLS 1.3, │
│   TCP    │               │  streams, controle  │
├──────────┤               │  de congestão)      │
│    IP    │               ├─────────────────────┤
└──────────┘               │        UDP / IP     │
                           └─────────────────────┘
```

**O que isso resolve:**

| Problema | Solução no QUIC |
|---|---|
| 2 handshakes (TCP + TLS) = 2–3 RTTs | **1 RTT** total; 0-RTT na retomada |
| *head-of-line blocking* do TCP: um pacote perdido trava **todos** os fluxos do HTTP/2 | streams independentes; a perda só afeta o próprio stream |
| conexão morre ao trocar de rede (Wi-Fi → 4G) | **connection ID**: a conexão migra sem refazer o handshake |
| *middleboxes* enrijecem o protocolo | quase todo o cabeçalho é **cifrado e autenticado** — nada de fora pode depender do formato |

**O último ponto é uma decisão de projeto explícita**, tomada por causa da lição de
ossificação do TLS 1.3 ([12 §2.1](12-handshake.md)): se intermediários não conseguem
ler o protocolo, não conseguem impedir sua evolução.

**Os custos reais, ditos sem entusiasmo:**

- **UDP é bloqueado ou limitado** em muitas redes corporativas; toda implementação
  precisa cair para HTTP/2 sobre TCP.
- **Mais CPU**: o processamento fica em espaço de usuário, sem as otimizações de
  décadas do TCP no núcleo do sistema. Medições mostram consumo maior por byte
  (a diferença vem caindo com `GSO`/`GRO` e offload, mas ainda existe).
- **Observabilidade menor**: as ferramentas de rede não enxergam quase nada. O que é
  o objetivo — e também um problema operacional real.

```bash
curl --http3 -sI https://cloudflare.com | head -1
tshark -i any -f "udp port 443" -Y quic
```

---

## 4. VPN

| Tecnologia | Base | Notas |
|---|---|---|
| **OpenVPN** | TLS (com DTLS ou TCP) | maduro, flexível, lento em comparação; usa PKI X.509 clássica |
| **WireGuard** | **não usa TLS** | Noise Protocol Framework, ~4.000 linhas de código, chaves fixas trocadas fora de banda; muito mais rápido e simples |
| **IPsec/IKEv2** | não usa TLS | padrão de infraestrutura; complexo |
| **DTLS** (RFC 9147) | TLS sobre UDP | base de várias VPNs e do WebRTC |

> **WireGuard merece nota justamente por não usar TLS.** Ele descarta a negociação de
> algoritmos: as primitivas são **fixas** (ChaCha20-Poly1305, Curve25519, BLAKE2s).
> Não há downgrade possível, não há cipher suite para configurar errado, e a superfície
> auditável é minúscula. O preço: para trocar um algoritmo, troca-se a **versão do
> protocolo** — nada de negociação. É a tese do §7 de [10](10-fundamentos.md) levada ao
> extremo, e o resultado prático lhe dá razão.

---

## 5. IoT e dispositivos restritos

Um microcontrolador com 64 KB de RAM não roda a mesma pilha TLS de um servidor.

| Restrição | Consequência | Mitigação |
|---|---|---|
| pouca memória | uma cadeia de certificados grande não cabe | certificado único, sem cadeia; **PSK** (chave pré-compartilhada) em vez de certificado |
| pouca CPU | RSA é caro demais | ECC obrigatório; ChaCha20 em vez de AES sem aceleração |
| sem relógio confiável | validade não pode ser verificada | relógio via NTP seguro, ou aceitar a limitação conscientemente |
| sem atualização de firmware | as raízes embutidas vencem **e o aparelho morre** | mecanismo de atualização de raízes desde o primeiro dia |
| rede com perda | handshake TCP+TLS é caro | **DTLS sobre UDP**, CoAP |

**O modo PSK do TLS** (`TLS_PSK_*`, sem certificado) é comum em IoT: os dois lados
compartilham um segredo provisionado de fábrica. Simples e barato — e sem sigilo
futuro nem revogação, a menos que combinado com DHE (`TLS_DHE_PSK_*`).

> **O problema real do IoT não é criptográfico, é de ciclo de vida.** Um medidor
> instalado em 2026 com raízes embutidas que vencem em 2035 vira lixo eletrônico em
> 2035, a não ser que alguém tenha planejado a atualização. Isso já aconteceu em massa
> quando a raiz **DST Root CA X3** do Let's Encrypt expirou em 30/09/2021: dispositivos
> Android antigos, TVs e leitores de e-book pararam de acessar sites perfeitamente
> normais. Este é um problema de **produto**, não de protocolo.

---

## 6. Bancos de dados e filas

Quase todo banco moderno fala TLS — e quase toda instalação padrão **não verifica nada**.

| Sistema | Como ligar | Armadilha |
|---|---|---|
| **PostgreSQL** | `sslmode=verify-full` | o padrão `prefer` cifra **sem verificar identidade** — inútil contra MITM |
| **MySQL/MariaDB** | `--ssl-mode=VERIFY_IDENTITY` | `REQUIRED` cifra sem verificar |
| **MongoDB** | `tls=true&tlsCAFile=...` | `tlsAllowInvalidCertificates` aparece em toda thread de fórum |
| **Redis** | TLS a partir do 6.0 | muitos ainda expõem sem TLS "porque é rede interna" |
| **Kafka** | `security.protocol=SSL` | mTLS é o padrão recomendado |
| **RabbitMQ / MQTT** | porta 8883 (MQTT sobre TLS) | dispositivos IoT frequentemente com verificação desligada |

**A regra:** `sslmode=require` **não é seguro**. Ele cifra e não verifica com quem —
o cenário do §Passo 4 de [04](04-como-comecar.md). Use sempre o modo que valida
a identidade (`verify-full`, `VERIFY_IDENTITY`).

```bash
psql "host=db.exemplo.com.br dbname=app sslmode=verify-full sslrootcert=/etc/pki/ca.crt"
```

---

## 7. Tabela de portas

| Protocolo | Porta em claro | Porta com TLS | Modo |
|---|---|---|---|
| HTTP | 80 | **443** | implícito |
| SMTP (entrega) | 25 | 25 | STARTTLS oportunista |
| SMTP (submissão) | 587 | **465** | STARTTLS / implícito |
| IMAP | 143 | **993** | STARTTLS / implícito |
| POP3 | 110 | **995** | STARTTLS / implícito |
| DNS | 53 | **853** (DoT) / 443 (DoH) | implícito |
| LDAP | 389 | **636** | STARTTLS / implícito |
| FTP | 21 | 990 (FTPS) | — |
| MQTT | 1883 | **8883** | implícito |
| PostgreSQL | 5432 | 5432 | negociado no protocolo |
| MySQL | 3306 | 3306 | negociado no protocolo |
| Syslog | 514 | 6514 | implícito |

Mais sobre portas em [portas-de-rede](../portas-de-rede/00-MAPA.md).

---

## Autoteste

1. Qual é a diferença entre STARTTLS e TLS implícito, e qual o ataque específico do primeiro?
2. Por que a entrega de e-mail entre servidores é oportunista? Percorra os porquês.
3. O que MTA-STS resolve, e o que continua sem solução no TLS do e-mail?
4. Compare DoT e DoH, com um argumento a favor e um contra cada.
5. Por que o ECH depende de DNS cifrado?
6. Cite quatro problemas que o QUIC resolve e três custos reais que ele traz.
7. Por que o QUIC cifra quase todo o cabeçalho? Qual lição histórica motivou isso?
8. Por que o WireGuard **não** negocia algoritmos, e qual é o trade-off?
9. Qual é o problema real do TLS em IoT, e o que aconteceu em 30/09/2021?
10. Por que `sslmode=require` no PostgreSQL não é seguro?

*Respostas: §1.2, §1.3, §1.3, §2, §2, §3, §3, §4, §5, §6.*

---

**Próximo:** [20-desempenho-e-operacao.md](20-desempenho-e-operacao.md) — o que o TLS custa e como operá-lo.
