# 80 · Custos e licenças

**Nível:** todos
**Data da consulta de preços: 31/08/2026.** Preço sem data é desinformação — se você
está lendo isto muito depois, **confirme tudo**.
**Câmbio usado:** US$ 1,00 ≈ **R$ 5,17** (faixa de agosto/2026: R$ 5,05–5,25).
Valores em BRL são **ordem de grandeza**, não cotação.

---

## 1. A primeira linha, que muda tudo

> **Para a esmagadora maioria dos casos, o custo direto do TLS é ZERO.**
> O protocolo é um padrão aberto e livre de royalties. As implementações principais
> (OpenSSL, BoringSSL, GnuTLS, rustls) são open source. E o certificado — que era o
> único item pago — é gratuito desde 2015, via Let's Encrypt.

O que **não** é zero: o tempo de engenharia, a automação, o monitoramento, e o custo
de um incidente. É lá que está a conta real.

---

## 2. Certificados públicos

| Opção | Preço/ano | ≈ BRL/ano | Validação | Notas |
|---|---|---|---|---|
| **Let's Encrypt** | **US$ 0** | **R$ 0** | DV | 90 dias (ou 6 dias no perfil `shortlived`); ACME; sem cartão |
| **ZeroSSL** | US$ 0 (3 certs) / a partir de ~US$ 50 | R$ 0 / ~R$ 260 | DV | ACME; plano gratuito limitado |
| **Google Trust Services** | US$ 0 (via Google Cloud) | R$ 0 | DV | ACME; para clientes GCP |
| **BuyPass Go** | US$ 0 | R$ 0 | DV | ACME; alternativa europeia |
| **Cloudflare Universal SSL** | US$ 0 (inclusive no plano grátis) | R$ 0 | DV | só funciona com o DNS na Cloudflare |
| **Sectigo OV** | a partir de ~US$ 69 | ~R$ 360 | OV | — |
| **DigiCert Basic OV** | ~US$ 218 | ~R$ 1.130 | OV | |
| **DigiCert Secure Site OV** | ~US$ 399 | ~R$ 2.060 | OV | |
| **DigiCert Basic EV** | ~US$ 344 | ~R$ 1.780 | EV | |
| **DigiCert Secure Site EV** | ~US$ 995 | ~R$ 5.140 | EV | |
| **DigiCert Basic OV curinga** | ~US$ 800 | ~R$ 4.140 | OV | por domínio |

> ⚠️ **Detalhe de 2026 que muda a conta:** com a validade máxima em **200 dias** desde
> 15/03/2026, um "certificado anual" pago significa **duas emissões por ano**. Confirme
> com o fornecedor se o preço anual cobre as reemissões — a maioria cobre, mas o
> processo manual dobra.

### 2.1 Quando pagar faz sentido

| Situação | Vale pagar? |
|---|---|
| site comum, blog, e-commerce, API pública | **não** — Let's Encrypt resolve |
| norma setorial ou contrato exige OV/EV | sim, é requisito, não escolha |
| você precisa de garantia financeira contratual | talvez — leia a apólice, os limites são estreitos |
| suporte 24×7 com SLA para emissão | sim, se o seu processo depende disso |
| certificado para intranet sem internet | não — use CA interna |
| você quer "mais segurança" | **não.** É criptograficamente idêntico ([13 §6](13-certificados-e-pki.md)) |

### 2.2 Quem paga a conta do Let's Encrypt

O Let's Encrypt é operado pela **ISRG** (*Internet Security Research Group*), uma
organização sem fins lucrativos americana. A receita vem de patrocínio corporativo
(Mozilla, Google Chrome, Cisco, AWS, Meta, Shopify e dezenas de outros) e de doações.
O orçamento anual é da ordem de poucos milhões de dólares para emitir **centenas de
milhões** de certificados.

**Por que uma empresa patrocina isso?** Porque HTTPS universal é do interesse direto
de quem vende navegador, nuvem e publicidade: reduz fraude, viabiliza recursos que
exigem contexto seguro, e — no caso dos navegadores — evita que eles tenham de escolher
entre segurança e quebrar metade da web. É filantropia com retorno estratégico claro,
e isso é bom saber: **o modelo é sustentável enquanto esses interesses se mantiverem
alinhados**. Um cenário em que o Let's Encrypt perdesse financiamento seria um problema
sistêmico para a internet — mais um argumento para ter um plano B de CA
([65 §7.1](65-estado-da-arte.md)).

---

## 3. PKI privada gerenciada — onde o dinheiro aparece de verdade

| Serviço | Preço | ≈ BRL/mês | Observação |
|---|---|---|---|
| **AWS Private CA** — modo geral | **US$ 400 por CA/mês** | ~R$ 2.070 | + US$ 0,75/certificado (1–1.000/mês) |
| **AWS Private CA** — modo vida curta | **US$ 50 por CA/mês** | ~R$ 260 | para certificados de curta duração |
| AWS Private CA — OCSP | US$ 0,06/cert/mês | — | se habilitar OCSP |
| **Google CAS** — DevOps | **US$ 20 por CA/mês** | ~R$ 103 | + US$ 0,30/cert (até 50 mil) |
| **Google CAS** — Enterprise | **US$ 200 por CA/mês** | ~R$ 1.034 | + US$ 0,50/cert (até 50 mil) |
| **step-ca** (Smallstep) | **US$ 0** | R$ 0 | open source, Apache 2.0; você opera |
| **HashiCorp Vault PKI** | US$ 0 (community) | R$ 0 | ⚠️ licença **BUSL** desde 2023; leia antes de uso comercial |
| **OpenBao** | US$ 0 | R$ 0 | fork do Vault sob MPL 2.0, na Linux Foundation |
| **cert-manager** | US$ 0 | R$ 0 | Apache 2.0, CNCF |
| **SPIRE** | US$ 0 | R$ 0 | Apache 2.0, CNCF |

> **A conta que surpreende:** três ambientes (prod/hml/dev) no AWS Private CA em modo
> geral custam **US$ 1.200/mês ≈ R$ 6.200/mês ≈ R$ 74.000/ano** — só pelas CAs, antes
> de emitir um único certificado. Um `step-ca` numa VM de US$ 10/mês faz o mesmo
> trabalho técnico. A diferença que você compra é **operação gerenciada, auditoria e
> conformidade**, e para muitas empresas isso vale; para muitas outras, é gasto por
> inércia. Rode a conta antes.

---

## 4. Licenças das implementações

| Software | Licença | O que permite comercialmente | Pegadinha |
|---|---|---|---|
| **OpenSSL** | **Apache 2.0** (desde a 3.0) | uso livre, inclusive fechado | antes da 3.0 era a dupla OpenSSL/SSLeay, **incompatível com GPLv2** — dor de cabeça histórica |
| **LibreSSL** | ISC + Apache 2.0 | livre | — |
| **BoringSSL** | mista (ISC/OpenSSL) | livre, **mas** o Google não garante estabilidade de API/ABI | não é para uso externo; use por sua conta |
| **GnuTLS** | **LGPLv2.1+** | uso livre; ligação dinâmica em software fechado é OK | ligação **estática** em software fechado exige atenção jurídica |
| **wolfSSL** | **GPLv2 ou comercial** | GPL exige abrir o seu código | **licença dupla**: uso embarcado fechado exige comprar |
| **mbedTLS** | Apache 2.0 | livre | popular em IoT |
| **rustls** | Apache 2.0 / MIT / ISC | livre | seguro em memória; adoção crescente |
| **NSS** (Mozilla) | MPL 2.0 | livre | usado por Firefox e Red Hat |
| **s2n-tls** (AWS) | Apache 2.0 | livre | implementação enxuta |
| **Caddy** | Apache 2.0 | livre | ⚠️ o binário oficial reporta telemetria; desligável |
| **nginx** | BSD 2-cláusulas | livre | módulos comerciais no nginx Plus |
| **certbot** | Apache 2.0 | livre | — |
| **HashiCorp Vault** | **BUSL 1.1** (desde ago/2023) | ⚠️ **proíbe** oferecer como serviço concorrente | migre para OpenBao se isso te afeta |

> **A única armadilha de licença que realmente pega gente:** **wolfSSL é GPLv2 ou
> comercial**. Empresas de dispositivos embarcados a escolhem pelo tamanho, embarcam em
> produto fechado, e descobrem tarde que precisam comprar licença ou abrir o firmware.
> Se o seu produto é fechado e embarcado, **mbedTLS (Apache 2.0)** evita a conversa.

**Sobre patentes:** TLS, AES, SHA-2, ECDSA sobre curvas NIST, X25519 e ChaCha20 estão
livres de royalties conhecidos. ML-KEM e ML-DSA foram padronizados pelo NIST com
compromissos de licenciamento livre — o caso do Kyber envolveu acordos de patente que
o NIST negociou antes da padronização, justamente para evitar o que aconteceu com
outras primitivas nos anos 1990.

---

## 5. Custos ocultos — a parte que o orçamento esquece

| Custo | Ordem de grandeza | Comentário |
|---|---|---|
| **Tempo de engenharia inicial** | 4 a 40 h | de "certbot num site" a "PKI interna com mTLS em 50 serviços" |
| **Manutenção** | 1 a 4 h/mês | renovações que falham, clientes antigos, CVEs |
| **Um incidente de certificado vencido** | **horas de indisponibilidade** | costuma ser o maior custo real de todos |
| **CPU** | <5% em regime | ver [20 §1](20-desempenho-e-operacao.md) |
| **Latência** | 50–200 ms no primeiro acesso | mitigável com retomada e CDN |
| **HSM** | US$ 1.000 a US$ 40.000, ou ~US$ 1,50–5,00/h em nuvem | só para raiz de CA séria |
| **Auditoria WebTrust** (para ser uma CA pública) | dezenas de milhares de USD/ano | é por isso que existem poucas CAs |
| **Migração de CA** | 20 a 200 h | e cresce com o tamanho do parque |
| **Aprisionamento em CDN** | difícil de medir | quem termina o TLS controla o tráfego |
| **Egress do CDN** | US$ 0,01–0,15/GB | não é custo do TLS, mas vem junto na decisão |

### 5.1 A conta de um incidente

Um site que fatura R$ 100.000/dia e fica 4 horas fora por certificado vencido perde
~**R$ 16.700** de receita direta, mais o custo da equipe, mais o dano de reputação.
A automação que teria evitado isso custa **4 horas de trabalho, uma vez**.

Este é o argumento econômico central do assunto, e ele é simples: **automatizar
certificado é o investimento com melhor retorno em toda a infraestrutura de TLS**.

---

## 6. Alternativas gratuitas equivalentes

| Em vez de… | Use | O que se perde |
|---|---|---|
| certificado DV pago | **Let's Encrypt** | nada |
| certificado OV/EV | Let's Encrypt DV | o selo (que ninguém vê) e a validação organizacional |
| AWS Private CA | **step-ca** ou **cert-manager** | operação gerenciada, SLA, relatório de conformidade |
| Vault (BUSL) | **OpenBao** (MPL 2.0) | suporte comercial da HashiCorp |
| CDN pago | **Cloudflare grátis** | recursos avançados, WAF completo, suporte |
| SSL Labs / scanner pago | **testssl.sh** | interface e relatório executivo |
| wolfSSL comercial | **mbedTLS** | alguns recursos e o suporte |
| certificado local pago | **mkcert** | nada, para desenvolvimento |

---

## 7. Três orçamentos realistas

**(a) Site pequeno / autônomo — R$ 0/mês**
Let's Encrypt + Caddy numa VPS que você já paga. Custo de TLS: zero. Tempo: 1 hora,
uma vez.

**(b) Startup com 15 serviços e mTLS interno — ~R$ 60/mês + 3 h/mês**
Let's Encrypt para o que é público (R$ 0), `step-ca` ou `cert-manager` numa instância
pequena (~US$ 12/mês ≈ R$ 62) para o interno, monitoramento no que você já tem.

**(c) Empresa com conformidade e três ambientes — R$ 8.000 a R$ 15.000/mês**
AWS Private CA ou Google CAS gerenciado (R$ 3.000–6.200/mês), certificados OV para
sistemas que exigem por norma (~R$ 500/mês amortizado), meio período de uma pessoa
dedicada a PKI (o item mais caro), auditoria e ferramenta de inventário.
**A maior parte desse custo é pessoa, não licença.**

---

## Fontes consultadas (31/08/2026)

- Let's Encrypt — <https://letsencrypt.org/> e <https://letsencrypt.org/2026/01/15/6day-and-ip-general-availability>
- AWS Private CA — preços: <https://aws.amazon.com/private-ca/pricing/>
- Google Cloud CAS — preços: <https://cloud.google.com/certificate-authority-service/pricing>
- Preços de CAs comerciais (DigiCert, Sectigo) — compilados de páginas de fornecedores e revendedores em 31/08/2026; **variam muito por revendedor e por promoção**
- Câmbio USD/BRL — faixa de agosto/2026 (R$ 5,05–5,25); usado R$ 5,17
- Licenças: OpenSSL (Apache 2.0 desde a 3.0), GnuTLS (LGPL), wolfSSL (GPLv2/comercial), HashiCorp BUSL 1.1 (ago/2023), OpenBao (MPL 2.0)

> Preços de CAs comerciais são especialmente voláteis e dependem de revendedor,
> volume e negociação. Trate os números da §2 como **ordem de grandeza**, e cote antes
> de decidir.

---

## Autoteste

1. Qual é o custo direto do TLS para a maioria dos casos, e onde está o custo real?
2. Quem financia o Let's Encrypt, e por que faz sentido para essas empresas?
3. Quanto custam três CAs no AWS Private CA (modo geral) por ano, e qual é a alternativa gratuita?
4. Qual é a única armadilha de licença que realmente pega empresas, e como evitá-la?
5. Por que a licença do OpenSSL mudou na versão 3.0, e qual problema histórico isso resolveu?
6. O que muda no custo de um certificado pago por causa da regra de 200 dias?
7. Faça a conta: 4 horas fora do ar por certificado vencido, num site de R$ 100 mil/dia.
8. Em que casos pagar por OV/EV se justifica?
9. Qual é o item mais caro do orçamento (c), e o que isso diz sobre o assunto?

*Respostas: §1, §2.2, §3, §4, §4, §2, §5.1, §2.1, §7.*

---

**Próximo:** [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md).
