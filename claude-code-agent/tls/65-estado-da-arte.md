# 65 · Estado da arte

**Nível:** pesquisa · **Data desta revisão:** 31/08/2026
**Este arquivo envelhece rápido.** Tudo aqui tem data. Confirme antes de decidir.

Onde o TLS está em agosto de 2026, o que mudou nos últimos 24 meses, e o que está
em disputa. As fontes estão no rodapé, com a data de consulta.

---

## 1. O que mudou desde 2024 — resumo executivo

| Mudança | Quando | Impacto |
|---|---|---|
| ML-KEM híbrido padrão nos navegadores | 2024–2025 | **já é maioria do tráfego**; a troca de chaves está resolvida |
| **RFC 9849** — ECH publicado | 03/03/2026 | o SNI finalmente pode ser cifrado |
| **RFC 9848** — ECH via SVCB/HTTPS no DNS | 2026 | como o cliente descobre a chave do ECH |
| Certificados de **6 dias** e para **IP** no Let's Encrypt | 15/01/2026 | vida curta vira produto de prateleira |
| Validade máxima cai para **200 dias** | 15/03/2026 | renovação manual deixa de ser viável |
| **Merkle Tree Certificates**: WG PLANTS na IETF | 2026 | a resposta ao tamanho das assinaturas PQ |
| Let's Encrypt anuncia MTC como caminho PQ | 03/06/2026 | staging no fim de 2026, produção em 2027 |
| Desativação progressiva do **OCSP** | 2025–2026 | CRL + vida curta assumem o lugar |

---

## 2. Troca de chaves pós-quântica: praticamente resolvida

**Situação em agosto de 2026:** o híbrido **X25519MLKEM768** é o padrão de facto.

| Marco | Data |
|---|---|
| NIST padroniza ML-KEM (FIPS 203) | agosto de 2024 |
| Chrome liga X25519MLKEM768 por padrão | 2024 |
| Firefox liga por padrão | novembro de 2024 |
| Apple (iOS/macOS) liga por padrão | outubro de 2025 |
| Akamai torna padrão em toda a rede | janeiro–março de 2026 |
| **>2/3 do tráfego TLS humano à Cloudflare usa ML-KEM híbrido** | abril de 2026 |

**Por que híbrido e não ML-KEM puro:** o segredo final combina X25519 **e** ML-KEM.
Se o ML-KEM tiver uma falha ainda desconhecida — é criptografia com poucos anos de
escrutínio —, o X25519 sustenta a segurança clássica. Se um computador quântico
surgir, o ML-KEM sustenta. Cinto e suspensório, pelo tempo da transição.

**Testar (exige OpenSSL 3.5+):**

```bash
docker run --rm -it alpine:3.22 sh -c \
  "apk add --no-cache openssl && \
   openssl s_client -connect cloudflare.com:443 -servername cloudflare.com \
     -groups X25519MLKEM768 -brief </dev/null 2>&1 | grep 'Temp Key'"
# esperado em servidor moderno: Server Temp Key: X25519MLKEM768
```

**O que ainda incomoda:** o `ClientHello` cresce de ~300 para ~1.200–1.700 bytes,
podendo passar de um pacote. Isso expôs *middleboxes* que não lidam com `ClientHello`
fragmentado — mais um capítulo da ossificação ([12 §2.1](12-handshake.md)).

---

## 3. Assinaturas pós-quânticas: **o problema em aberto**, e a solução que emergiu

### 3.1 O problema, em números

| Esquema | Assinatura | Chave pública |
|---|---|---|
| ECDSA P-256 | **64 B** | 64 B |
| RSA-2048 | 256 B | 256 B |
| **ML-DSA-44** (Dilithium) | **~2.420 B** | ~1.312 B |
| SLH-DSA (SPHINCS+) | 8.000–30.000 B | 32 B |

Um handshake típico carrega **várias** assinaturas: a do certificado folha, a do
intermediário, os SCTs de Certificate Transparency, e o `CertificateVerify`. Trocando
tudo por ML-DSA ingenuamente, os dados de autenticação vão de **~3 KB para ~14,7 KB**.

Por que 14,7 KB dói: a **janela inicial de congestionamento** do TCP é de ~10 pacotes
(~14 KB). Estourá-la custa um RTT extra antes de o handshake terminar — perceptível em
rede móvel, e multiplicado por bilhões de conexões.

### 3.2 A resposta: Merkle Tree Certificates (MTC)

Anunciada pelo Google em **fevereiro de 2026**, desenvolvida com a Cloudflare, e sendo
padronizada no **novo grupo de trabalho PLANTS** da IETF (*PKI, Logs, And Tree Signatures*).

**A ideia:** em vez de cada certificado carregar a própria assinatura pós-quântica
enorme, a CA assina **uma única raiz de árvore de Merkle** que representa milhões de
certificados de uma vez. O que viaja no handshake é uma **prova de inclusão** — uma
cadeia de hashes de tamanho logarítmico.

```
Modelo atual:                        Merkle Tree Certificates:
cada certificado                     a CA assina UMA raiz por lote
carrega uma assinatura               ┌──────── raiz assinada ────────┐
grande e própria                     │        (1 assinatura)         │
                                     └───┬───────────────┬───────────┘
                                       hash            hash
                                      ┌─┴─┐           ┌─┴─┐
   ≈ 14,7 KB por handshake            c1  c2   ...    cN     ≈ 736 bytes por handshake
```

**Redução relatada: de ~14.700 bytes para até ~736 bytes** — ou seja, a autenticação
pós-quântica ficaria **menor que a cadeia clássica de hoje**.

**Dois efeitos colaterais notáveis:**

1. **Certificate Transparency deixa de ser um apêndice.** Hoje a CT é "aparafusada" por
   cima: o certificado é emitido e depois publicado. Com MTC, o certificado **só existe
   dentro da árvore** — a transparência é estrutural, não opcional.
2. **Exige um novo repositório de raízes.** A proposta prevê um root store específico
   (o Chrome fala em um *Quantum-resistant Root Store*) que só aceita MTCs. Ou seja:
   é uma mudança de arquitetura da Web PKI, não um ajuste de parâmetro.

**Cronograma anunciado:**

| Marco | Data |
|---|---|
| Google anuncia MTC | fevereiro de 2026 |
| Let's Encrypt adota MTC como caminho PQ | 03/06/2026 |
| Ambiente de **staging** do Let's Encrypt emitindo MTC | fim de 2026 |
| Ambiente de **produção** | 2027 |
| Experimentos com tráfego real (Cloudflare + Chrome) | em curso |

**O que isso significa para você, hoje:** nada de operacional ainda. Mas é a mudança
mais estrutural da Web PKI desde o Certificate Transparency, e vale acompanhar.
Note também que **KEMTLS** ([60 §6.1](60-teoria-avancada.md)), a alternativa acadêmica
mais discutida entre 2020 e 2024, **não** foi o caminho escolhido pela indústria.

---

## 4. ECH — publicado, mas longe de universal

**RFC 9849** (03/03/2026) e **RFC 9848** (bootstrap via SVCB/HTTPS no DNS).

**Como funciona:** o cliente descobre, por um registro `HTTPS` no DNS, a chave pública
ECH do servidor. Cifra o `ClientHello` real (com o SNI verdadeiro) e o envolve num
`ClientHello` externo que aponta para um nome público comum (por exemplo,
`cloudflare-ech.com`). Quem observa a rede vê apenas o nome público.

```
sem ECH:  ClientHello { server_name: "site-sensivel.org" }     ← em claro
com ECH:  ClientHello { server_name: "cloudflare-ech.com",
                        encrypted_client_hello: <cifrado> }     ← o real vai dentro
```

**Estado da adoção (agosto de 2026):**

| Dimensão | Situação |
|---|---|
| Navegadores | Chrome, Edge, Firefox e Safari suportam; ~59% dos navegadores em uso |
| CDNs | **Cloudflare** ligado por padrão (inclusive no plano gratuito, onde não pode ser desligado); Fastly e Akamai com suporte parcial; AWS CloudFront e outros, lentos |
| Sites | poucos por cento do topo da web |
| Servidores próprios | nginx começou a ganhar suporte; ainda incipiente |

**Os obstáculos, e eles não são técnicos:**

1. **Depende de DNS cifrado.** Se a consulta DNS foi em claro, o domínio já vazou —
   cifrar o SNI não adianta ([19 §2](19-tls-alem-do-https.md)).
2. **Quebra a inspeção de rede.** Firewalls corporativos filtram por SNI. Com ECH, não
   conseguem — e a resposta de vários fabricantes é **bloquear conexões com ECH**.
3. **Geopolítica.** Filtragem estatal por SNI é comum. A Rússia bloqueou o ECH.
   O padrão ameaça diretamente um mecanismo de censura em larga escala, e isso torna
   a adoção uma questão política, não de engenharia.
4. **Concentração.** Um `ClientHello` externo que aponta para `cloudflare-ech.com`
   esconde qual site você acessa — **desde que muitos sites estejam atrás da mesma
   Cloudflare**. O anonimato depende do tamanho do rebanho, o que reforça a
   centralização em poucos CDNs. É um trade-off desconfortável e pouco discutido.

**Opinião profissional:** ECH é tecnicamente sólido e resolve um vazamento real de
privacidade. Mas eu não esperaria adoção majoritária antes de 2028: os obstáculos são
de política de rede e de geopolítica, e esses não se resolvem com uma RFC.

---

## 5. Vida curta: o novo normal

| Data | Validade máxima pública |
|---|---|
| set/2020 | 398 dias |
| **15/03/2026** | **200 dias** ✅ em vigor |
| 15/03/2027 | 100 dias |
| 15/03/2029 | **47 dias** |

Aprovado pelo **Ballot SC-081v3** do CA/B Forum (abril de 2025), **29 a favor, 0 contra**.

Em paralelo, o Let's Encrypt disponibilizou em **15/01/2026** o perfil `shortlived`
(**160 horas**, ~6 dias) e certificados para **endereço IP** — estes só na modalidade de
6 dias, porque o controle de um IP muda de mãos com muito mais frequência que o de um domínio.

E, fechando o raciocínio: o ecossistema começou a **desligar o OCSP**, tratando a
consulta on-line de revogação como um custo sem benefício proporcional. A tese está
consolidada: **vida curta substitui revogação** ([15](15-validacao-revogacao-transparencia.md)).

---

## 6. Números de adoção (agosto de 2026)

| Métrica | Valor | Fonte/observação |
|---|---|---|
| Páginas carregadas por HTTPS (Firefox/Chrome) | >90% na maioria dos países | telemetria dos navegadores |
| TLS 1.3 entre os sites do topo | ~75% (medição de meados de 2025) | tendência de alta |
| Tráfego humano à Cloudflare com ML-KEM híbrido | **>2/3** (abril de 2026) | Cloudflare |
| Navegadores com suporte a ECH | ~59% | mas o tráfego que **usa** ECH é bem menor |
| Sites do top 1M com suporte a ECH | poucos por cento | Cloudflare domina esse número |
| Certificados ativos do Let's Encrypt | centenas de milhões | maior CA do mundo em volume |

> Números de adoção variam bastante conforme a metodologia (top 1M × tráfego real,
> por site × por conexão). Trate-os como **ordem de grandeza**, não como precisão.

---

## 7. Debates em aberto

### 7.1 Vida curta *versus* capacidade operacional

**A favor:** elimina a dependência de revogação, que nunca funcionou; reduz a janela de
uma chave comprometida; força automação, que é boa por si só.

**Contra:** empurra toda a internet para dependência de automação e de CAs sempre
disponíveis. Uma falha de várias horas no Let's Encrypt, com certificados de 6 dias,
teria consequências muito maiores do que teria com 90 dias. E há setores (industrial,
médico, embarcado) onde renovar de 6 em 6 dias é operacionalmente impossível.

**Minha leitura:** o rumo está certo e é irreversível, mas o ecossistema subestima o
risco de concentração. Uma internet em que 47 dias é o teto **exige** múltiplas CAs
com ACME e capacidade de troca rápida entre elas. Poucas organizações têm isso hoje —
e testar a troca de CA deveria estar no plano de continuidade de quem opera algo sério.

### 7.2 ECH e o direito de inspecionar a rede

Não há solução técnica que satisfaça os dois lados: ou o intermediário vê o nome do
site, ou não vê. Empresas argumentam necessidade legítima (conformidade, prevenção de
vazamento); defensores de privacidade apontam que o mesmo mecanismo serve à censura
estatal. **Provavelmente vai se resolver por fragmentação:** ECH na internet aberta,
e dispositivos gerenciados com CA corporativa instalada, onde a organização já tem
controle explícito e declarado.

### 7.3 Centralização

Uma fração enorme do TLS do mundo passa por três ou quatro CDNs, e a maioria dos
certificados vem de uma CA sem fins lucrativos sustentada por doações. Isso deu
uniformidade, velocidade de correção e HTTPS universal. E criou pontos únicos de falha
de escala planetária. **Não há proposta séria em cima da mesa para reverter isso** —
inclusive porque as propostas descentralizadas (DANE, blockchain, web of trust) todas
falharam em adoção. É um fato do campo, não um problema com solução conhecida.

### 7.4 Vale a pena migrar assinaturas para PQ agora?

**Não.** Uma assinatura só precisa resistir **no momento** em que é verificada; não há
"colher agora, verificar depois". Um computador quântico futuro não permite forjar
retroativamente uma assinatura que já foi aceita. Por isso é racional migrar as
**trocas de chaves** com urgência (o dano seria retroativo) e as **assinaturas** com
calma, esperando por MTC. Este é consenso confortável no campo.

---

## 8. O que fazer hoje, em ordem de prioridade

1. **Automatize a renovação.** Não é opinião: 100 dias em março de 2027 torna o resto inviável.
2. **Garanta TLS 1.3.** Um RTT a menos e melhor privacidade, sem custo.
3. **Monitore Certificate Transparency.** Cinco minutos de configuração; é a defesa que funciona.
4. **Publique CAA.** Dois minutos.
5. **Tenha um plano B de CA.** Saiba trocar de CA em horas, não em semanas.
6. **Confirme que você já está em ML-KEM híbrido.** Se você está atrás de um CDN
   grande, provavelmente sim, sem ter feito nada. Se termina TLS você mesmo, precisa de
   OpenSSL 3.5+ ou equivalente.
7. **Não migre assinaturas para PQ ainda.** Espere o MTC.
8. **Considere ECH se privacidade é requisito** — sabendo que hoje isso implica,
   na prática, estar atrás da Cloudflare.

---

## Fontes consultadas (31/08/2026)

- Let's Encrypt — *6-day and IP Address Certificates are Generally Available* (15/01/2026): <https://letsencrypt.org/2026/01/15/6day-and-ip-general-availability>
- Let's Encrypt — *A Post-Quantum Future for Let's Encrypt* (03/06/2026): <https://letsencrypt.org/2026/06/03/pq-certs>
- Google Security Blog — *Cultivating a robust and efficient quantum-safe HTTPS* (fev/2026): <https://security.googleblog.com/2026/02/cultivating-robust-and-efficient.html>
- IETF — *Merkle Tree Certificates* (WG PLANTS): <https://datatracker.ietf.org/doc/html/draft-ietf-plants-merkle-tree-certs-03>
- CA/Browser Forum — *Ballot SC-081v3* (abril/2025): <https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/>
- RFC 9849 (ECH) e RFC 9848 (bootstrap via DNS), publicadas em 2026
- Cloudflare Blog — transparência sobre uso de PQ: <https://blog.cloudflare.com/radar-origin-pq-key-transparency-aspa/>
- SANS ISC — *Encrypted Client Hello: Ready for Prime Time?*: <https://isc.sans.edu/diary/32778>
- NGINX — *Encrypted Client Hello Comes to NGINX*: <https://blog.nginx.org/blog/encrypted-client-hello-comes-to-nginx>

> Percentuais de adoção citados vêm de fontes secundárias e de metodologias diferentes.
> Trate-os como ordem de grandeza. Para números primários, consulte
> <https://radar.cloudflare.com/> e a telemetria pública da Mozilla.

---

## Autoteste

1. Qual é o estado da troca de chaves pós-quântica em agosto de 2026, e por que é híbrida?
2. Por que as assinaturas PQ são um problema maior que a troca de chaves? Dê os números.
3. O que são Merkle Tree Certificates e como reduzem 14,7 KB para ~736 bytes?
4. Que dois efeitos colaterais estruturais o MTC traz?
5. Qual é o cronograma do Let's Encrypt para MTC?
6. Como o ECH funciona, e por que ele depende de DNS cifrado?
7. Cite os quatro obstáculos à adoção do ECH — e note que só um deles é técnico.
8. Por que o anonimato do ECH depende do tamanho do "rebanho"?
9. Qual é o cronograma de redução da validade e o que ele exige de você?
10. Por que **não** é urgente migrar assinaturas para pós-quântico?
11. Quais são os oito passos recomendados para hoje?

*Respostas: §2, §3.1, §3.2, §3.2, §3.2, §4, §4, §4, §5, §7.4, §8.*

---

**Próximo:** [70-pratica.md](70-pratica.md) — laboratórios.
