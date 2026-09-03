# 10 · Fundamentos

**Nível:** iniciante → intermediário · **Data:** 31/08/2026

O vocabulário inteiro do assunto, as garantias que o TLS oferece, o modelo de ameaça
que ele assume, e — principalmente — **o que ele não promete**. Depois deste arquivo
você lê qualquer RFC de TLS sem tropeçar em terminologia.

---

## 1. Onde o TLS mora

```
┌──────────────────────────────────────────┐
│  APLICAÇÃO   HTTP · SMTP · IMAP · MQTT   │  "o que é dito"
├──────────────────────────────────────────┤
│  ► TLS ◄     cifra, autentica, verifica  │  ← nós estamos aqui
├──────────────────────────────────────────┤
│  TRANSPORTE  TCP (entrega ordenada)      │  "chega inteiro e na ordem"
├──────────────────────────────────────────┤
│  REDE        IP (encontra o destino)     │  "chega ao endereço"
├──────────────────────────────────────────┤
│  ENLACE      Ethernet, Wi-Fi             │  "atravessa o cabo/ar"
└──────────────────────────────────────────┘
```

TLS é uma camada **opcional e transparente**: quem está acima (o HTTP) não muda uma
vírgula, e quem está abaixo (o TCP) não sabe que existe. Você troca `socket.send()`
por `tls_socket.send()` e pronto.

Essa transparência é a razão do sucesso — e a origem de duas confusões:

1. **TLS não é "camada 4" nem "camada 5" do modelo OSI**, e discutir isso é perda de
   tempo. O modelo OSI é de 1984 e não previu isso. Na prática, TLS fica entre o
   transporte e a aplicação. Alguns dizem "camada 6". Ninguém que trabalha com o
   protocolo se importa.
2. **Existem TLS que não rodam sobre TCP.** O **DTLS** (*Datagram TLS*) roda sobre UDP,
   para voz, vídeo e VPN. E o **QUIC** (base do HTTP/3) não usa TLS como camada:
   ele **incorpora** o handshake do TLS 1.3 dentro do próprio protocolo de transporte.
   Ver [19-tls-alem-do-https.md](19-tls-alem-do-https.md).

---

## 2. As quatro garantias

| Garantia | Pergunta que responde | Como o TLS consegue |
|---|---|---|
| **Confidencialidade** | "alguém no caminho lê?" | cifra simétrica (AES-GCM, ChaCha20-Poly1305) com uma chave que só os dois lados têm |
| **Integridade** | "alguém alterou?" | tag de autenticação (AEAD) calculada sobre cada registro |
| **Autenticidade da origem** | "é mesmo o servidor?" | certificado X.509 + assinatura de uma chave privada que só ele tem |
| **Proteção contra repetição e reordenação** | "é a mensagem de agora, na ordem certa?" | número de sequência implícito, incluído no cálculo da tag |

E uma quinta, que não é obrigatória mas é essencial na prática:

| **Sigilo futuro** (*forward secrecy*) | "se a chave do servidor vazar amanhã, o que gravei hoje será lido?" | a chave da sessão vem de um par **efêmero** (ECDHE) que é apagado ao fim da conexão |

> ### Por que o sigilo futuro merece um parágrafo
> Antes de 2013 era comum usar RSA para transportar a chave de sessão: o cliente
> sorteava a chave, cifrava com a chave pública do servidor e mandava. Simples,
> rápido — e catastrófico: quem gravasse o tráfego por dez anos e um dia obtivesse a
> chave privada do servidor decifraria **tudo**, retroativamente. Depois das
> revelações de Edward Snowden (junho de 2013), que documentaram gravação de tráfego
> em massa, a indústria migrou para ECDHE em poucos anos. O **TLS 1.3 removeu o
> transporte de chave por RSA do protocolo** — não é mais uma opção que se possa
> configurar errado. Este é um exemplo raro e limpo de o campo aprender uma lição e
> tornar o erro impossível, em vez de só desaconselhá-lo.

---

## 3. As duas metades do protocolo

TLS tem dois subprotocolos, e confundi-los atrapalha:

### 3.1 O **Handshake Protocol** — a negociação

Roda uma vez, no começo. Faz quatro coisas: acorda a versão e os algoritmos, troca
as chaves, autentica o servidor (e opcionalmente o cliente), e verifica que ninguém
mexeu na negociação. Custa uma ida e volta (1-RTT) no TLS 1.3, duas no TLS 1.2.
Dissecado em [12-handshake.md](12-handshake.md).

### 3.2 O **Record Protocol** — o transporte

Depois do handshake, todo byte da aplicação é fatiado em **registros** (*records*) de
até 16 KB, cada um cifrado e autenticado. É o trabalho contínuo, e é onde está o
custo de CPU do TLS em regime.

```
Dado da aplicação:  [ GET /saldo HTTP/1.1\r\nHost: banco... ]
                                   │
                    fatia em registros de ≤ 16.384 bytes
                                   ▼
Registro TLS 1.3:   ┌──────┬─────┬──────┬───────────────────────┬─────┐
                    │ tipo │ ver │ tam  │  conteúdo CIFRADO     │ tag │
                    │ 0x17 │0303 │ 2 B  │  (dado + tipo real)   │16 B │
                    └──────┴─────┴──────┴───────────────────────┴─────┘
                      ↑      ↑                                     ↑
              sempre "application_data"                  autentica cabeçalho
              (o tipo real vai cifrado dentro:            E conteúdo (AEAD)
               é o "content type masking" do 1.3)
```

Três detalhes que só quem leu a RFC sabe:

- O campo `ver` (versão) no registro do TLS 1.3 mente: diz `0x0303` (TLS 1.2) por
  **compatibilidade com equipamentos de rede** que descartavam pacotes com versão
  desconhecida. A versão real vai numa extensão do `ClientHello`. Chama-se
  *middlebox compatibility mode*, e é um dos melhores exemplos de **ossificação**
  da internet: o protocolo teve de mentir porque equipamentos intermediários
  quebravam com a verdade.
- O **tamanho do registro é visível** mesmo com tudo cifrado. Daí os ataques de
  análise de tráfego: dá para inferir qual página você abriu pelo padrão de tamanhos.
  O TLS 1.3 permite preenchimento (*padding*) para mitigar; quase ninguém usa.
- **16.384 bytes é o máximo por registro.** Registros grandes economizam overhead;
  registros pequenos reduzem latência de primeiro byte (o receptor só decifra o
  registro completo). Servidores otimizados começam com registros pequenos e crescem.

---

## 4. Vocabulário completo

Termos em inglês são mantidos onde é assim que o campo os usa. Todos estão também
no [GLOSSARIO.md](GLOSSARIO.md).

### 4.1 Criptografia

| Termo | Definição | Exemplo concreto |
|---|---|---|
| **cifra simétrica** | mesma chave cifra e decifra; rápida | AES-256, ChaCha20 |
| **cifra assimétrica** | par de chaves: pública e privada | RSA, ECDSA, Ed25519 |
| **AEAD** | *Authenticated Encryption with Associated Data*: cifra **e** autentica numa operação só | AES-256-GCM, ChaCha20-Poly1305 |
| **KEM** | *Key Encapsulation Mechanism*: mecanismo para combinar uma chave secreta | ML-KEM (pós-quântico) |
| **(EC)DHE** | Diffie–Hellman efêmero (em curva elíptica): os dois lados calculam o mesmo segredo sem transmiti-lo | X25519, P-256 |
| **KDF / HKDF** | função que deriva várias chaves de um segredo só | HKDF-SHA256 |
| **MAC** | código de autenticação de mensagem: prova que quem tem a chave escreveu aquilo | HMAC-SHA256 |
| **hash** | função de mão única, saída de tamanho fixo | SHA-256, SHA-384 |
| **nonce** | *number used once*: valor que nunca se repete com a mesma chave | contador de 96 bits no GCM |
| **entropia** | aleatoriedade genuína; sem ela toda a criptografia cai | `/dev/urandom` |

> **Reutilizar um nonce com a mesma chave em AES-GCM destrói a segurança por completo** —
> não enfraquece, destrói: dá para recuperar a chave de autenticação e forjar mensagens.
> É por isso que o TLS 1.3 fixou a construção do nonce em vez de deixá-la à escolha
> da implementação. Detalhes em [14-criptografia-do-tls.md](14-criptografia-do-tls.md).

### 4.2 Protocolo

| Termo | Definição |
|---|---|
| **handshake** | a negociação inicial |
| **cipher suite** | o conjunto de algoritmos negociado. No TLS 1.3, só cifra+hash (ex.: `TLS_AES_128_GCM_SHA256`); no 1.2, também a troca de chaves e a autenticação (`ECDHE-RSA-AES128-GCM-SHA256`) |
| **extensão** | campo opcional do `ClientHello`/`ServerHello`. TLS 1.3 vive delas |
| **SNI** | *Server Name Indication*: qual site o cliente quer, dito **em claro** no `ClientHello` |
| **ECH** | *Encrypted Client Hello*: cifra o `ClientHello` (incluindo o SNI). RFC 9849, março de 2026 |
| **ALPN** | *Application-Layer Protocol Negotiation*: acorda no handshake se vai ser `http/1.1`, `h2` ou `h3` |
| **alert** | mensagem de erro do TLS (`handshake_failure`, `bad_certificate`, `unknown_ca`…) |
| **session resumption** | retomar uma sessão anterior sem refazer o handshake completo |
| **0-RTT / early data** | enviar dados **junto** com o `ClientHello`, na retomada. Rápido e **sujeito a repetição** |
| **renegociação** | refazer o handshake numa conexão viva. **Removida no TLS 1.3** (era fonte de ataques) |
| **downgrade** | atacante força versão/cifra mais fraca. TLS 1.3 tem defesa embutida no `ServerHello.random` |
| **MITM** | *man-in-the-middle*, intermediário: quem se põe no caminho e se passa pelos dois lados |

### 4.3 PKI

| Termo | Definição |
|---|---|
| **certificado X.509** | documento assinado que liga uma chave pública a um nome |
| **CA** | *Certificate Authority*: quem assina certificados |
| **CSR** | pedido de assinatura: chave pública + nomes + prova de posse da privada |
| **cadeia** | folha → intermediário(s) → raiz |
| **raiz / trust anchor** | certificado autoassinado em que o cliente confia por decisão prévia |
| **root store** | a lista de raízes do sistema/navegador |
| **SAN** | *Subject Alternative Name*: os nomes que o certificado realmente cobre |
| **CN** | *Common Name*: campo legado; **ignorado pelos navegadores desde 2017** |
| **DV / OV / EV** | níveis de validação: domínio / organização / estendida |
| **CRL** | lista de revogados, publicada pela CA |
| **OCSP** | consulta on-line de revogação, um certificado por vez |
| **OCSP stapling** | o servidor anexa a resposta OCSP no handshake, evitando que o cliente consulte a CA |
| **CT** | *Certificate Transparency*: logs públicos e append-only de tudo que foi emitido |
| **mTLS** | ambos os lados se autenticam por certificado |
| **pinning** | fixar uma chave/CA específica, ignorando o root store |

---

## 5. O modelo de ameaça

Não dá para avaliar um mecanismo de segurança sem dizer **contra quem**.

### 5.1 O que o TLS assume sobre o atacante — o modelo Dolev–Yao

TLS é projetado contra um adversário que **controla a rede por completo**:

- **lê** tudo que passa;
- **altera** qualquer byte;
- **descarta** o que quiser;
- **repete** mensagens antigas;
- **injeta** mensagens próprias;
- **se passa** por qualquer endereço IP ou nome.

É o modelo mais pessimista razoável, formalizado por Danny Dolev e Andrew Yao em 1983.
Ele **não** assume que o atacante quebra a matemática — a criptografia é tratada como
caixa-preta perfeita. Contra esse atacante, TLS 1.3 tem prova de segurança
([60-teoria-avancada.md](60-teoria-avancada.md)).

### 5.2 O que o TLS **não** protege

Esta é a lista que separa quem entende de quem repete slogan:

| Fora do escopo | Por quê | O que usar |
|---|---|---|
| **dados no servidor** | TLS termina lá; os dados são decifrados | criptografia em repouso, controle de acesso |
| **dados no cliente** | idem | segurança do dispositivo |
| **quem você acessa** | IP de destino é visível; SNI também, salvo com ECH | Tor, VPN, ECH + DNS cifrado |
| **quanto e quando você acessa** | tamanho e tempo dos registros são visíveis | preenchimento, tráfego de cobertura — caro e raro |
| **um servidor comprometido** | ele tem a chave; TLS funciona perfeitamente para o invasor | defesa em profundidade |
| **uma CA comprometida ou coagida** | qualquer uma das ~150 raízes pode emitir para qualquer domínio | CT, CAA, pinning em app próprio |
| **o usuário clicando em "prosseguir mesmo assim"** | o elo humano | HSTS, que remove o botão |
| **um root store adulterado** | proxy corporativo, malware, coação | pinning, atestação de dispositivo |
| **bugs de implementação** | Heartbleed foi um erro de C, não do protocolo | atualizar, linguagens seguras em memória |
| **quantum futuro** | um computador quântico grande quebraria a troca de chaves clássica | ML-KEM híbrido, já em uso ([65](65-estado-da-arte.md)) |

> ### O elo mais fraco, dito sem rodeios
> **Qualquer uma das autoridades certificadoras do seu root store pode emitir um
> certificado válido para o seu banco.** São ~150 organizações, em dezenas de
> jurisdições, sujeitas a leis e pressões diferentes. Isso já aconteceu: a
> **DigiNotar** (Holanda, 2011) foi invadida e emitiu certificado para `*.google.com`,
> usado para espionar cerca de 300 mil usuários iranianos — a empresa faliu em semanas.
> A **TrustCor** foi removida dos navegadores em 2022 por ligações com uma empresa de
> vigilância. A **Symantec**, uma das maiores CAs do mundo, foi progressivamente
> desconfiada pelo Google entre 2017 e 2018 por emissões irregulares, e vendeu a
> operação. O TLS não resolve isso; **Certificate Transparency**
> ([15](15-validacao-revogacao-transparencia.md)) transforma o problema de
> "impossível de detectar" em "detectável em horas", que é uma melhora enorme e
> ainda assim não é uma solução.

---

## 6. Os cinco porquês, aplicados a "por que o TLS precisa de certificados?"

Este é o exercício central do curso. Vamos até o fim.

**1. Por que preciso de certificado?**
Porque a troca de chaves Diffie–Hellman, sozinha, dá um canal privado com **alguém** —
sem dizer com quem. Um atacante no meio faz DH com você e outro DH com o servidor,
e lê tudo. É o *man-in-the-middle*.

**2. Por que o certificado resolve isso?**
Porque ele obriga o outro lado a **assinar** o handshake com uma chave privada cujo
correspondente público está num documento assinado por alguém que você já confia.
O intermediário não tem essa chave privada, então não consegue produzir a assinatura.

**3. Por que confiar em uma CA, e não simplesmente na chave do site?**
Porque não escala. Você não tem como conhecer a chave de cada um dos ~200 milhões de
sites antes de visitá-los. A CA é uma **indireção de confiança**: você confia em ~150
entidades, e elas atestam por bilhões de sites. É o mesmo raciocínio de um passaporte:
o hotel não te conhece, mas confia no seu país.

**4. Por que ~150 CAs e não uma só, o que seria mais seguro?**
Três motivos, e nenhum é técnico:
(a) **antitruste e geopolítica** — nenhum governo aceitaria que uma única empresa
estrangeira controlasse a identidade de toda a internet;
(b) **história** — o modelo nasceu comercial: a Netscape embutiu a VeriSign em 1994
porque precisava de um parceiro que já fazia autenticação, e a lista cresceu por
pressão de mercado e de governos, cada um querendo sua CA nacional;
(c) **disponibilidade** — uma CA única seria um ponto único de falha para a economia mundial.
O custo dessa escolha é exatamente a fragilidade do §5.2: **a segurança do sistema é
a da CA mais fraca**, não a da mais forte.

**5. Por que ninguém consertou isso em 30 anos?**
Houve tentativas sérias: **DANE** (âncora de confiança no DNSSEC, RFC 6698, 2012),
**Convergence**, **Sovereign Keys**, **HPKP**. Todas fracassaram na adoção. Motivos
combinados: DANE depende do DNSSEC, cuja adoção estagnou (~5% dos domínios) e cuja
raiz de confiança é... a hierarquia do DNS, controlada por governos e pela ICANN —
troca-se um problema de centralização por outro; o HPKP permitia que um erro do
administrador tornasse o site inacessível por meses; e nenhuma proposta resolvia a
inércia de compatibilidade com bilhões de clientes.

**Onde a corrente para:** numa **decisão histórica documentada** (a Netscape, em 1994,
escolheu um modelo comercial de terceiros confiáveis porque era o que existia e o que
dava para vender) reforçada por um **trade-off econômico e político** (nenhum ator
aceita que outro controle a raiz). Não é uma limitação matemática. É a resposta
honesta, e ela explica por que Certificate Transparency — que **aceita** o modelo e
apenas o torna auditável — foi a única mitigação que pegou.

---

## 7. Como ler uma cipher suite

**TLS 1.2** — quatro informações no nome:

```
ECDHE - RSA - AES128GCM - SHA256
  │      │       │          │
  │      │       │          └── hash usado na PRF/HMAC
  │      │       └───────────── cifra simétrica e modo (AEAD)
  │      └───────────────────── como o SERVIDOR se autentica (assinatura)
  └──────────────────────────── como as chaves são trocadas (E = efêmero)
```

**TLS 1.3** — só duas, porque o resto deixou de ser negociável:

```
TLS_AES_128_GCM_SHA256
      │          │
      │          └── hash para o HKDF
      └───────────── cifra AEAD
```

**Por que encolheu:** no TLS 1.3 a troca de chaves é **sempre** (EC)DHE, e o método de
assinatura vai numa extensão separada (`signature_algorithms`). Eliminou-se a
explosão combinatória: o TLS 1.2 tem **centenas** de suites registradas, muitas
inseguras, e escolher errado era trivial. O TLS 1.3 tem **cinco**, todas seguras:

| Suite | Quando |
|---|---|
| `TLS_AES_128_GCM_SHA256` | padrão; mais rápida em CPU com AES-NI |
| `TLS_AES_256_GCM_SHA384` | quando se exige "256 bits" por política |
| `TLS_CHACHA20_POLY1305_SHA256` | celulares e CPUs sem aceleração de AES |
| `TLS_AES_128_CCM_SHA256` | dispositivos restritos (IoT) |
| `TLS_AES_128_CCM_8_SHA256` | idem, com tag de 8 bytes |

Reduzir o espaço de configuração para eliminar erro é um **princípio de projeto**, não
um detalhe. Vale para tudo que você constrói.

---

## 8. Um mapa mental para guardar

```
                  ┌──────────── TLS ────────────┐
                  │                             │
          HANDSHAKE (uma vez)          RECORD (sempre)
                  │                             │
   ┌──────────────┼──────────────┐              │
   ▼              ▼              ▼              ▼
NEGOCIAR      TROCAR         AUTENTICAR     CIFRAR+AUTENTICAR
versão        CHAVES         servidor       cada registro
cifras        (ECDHE)        (certificado)  (AEAD + seq)
extensões        │               │              │
   │             │               │              │
   │        sigilo futuro    depende da    confidencialidade
   │                            PKI         + integridade
   └── proteção contra downgrade            + anti-repetição
```

---

## Autoteste

1. Quais são as quatro garantias do TLS, e qual é a quinta que não é obrigatória?
2. Por que o campo de versão do registro TLS 1.3 diz "TLS 1.2"?
3. O que o TLS **não** protege? Cite cinco itens.
4. Explique sigilo futuro e por que o TLS 1.3 removeu o transporte de chave por RSA.
5. Por que uma cipher suite do TLS 1.3 tem menos informação que uma do TLS 1.2?
6. O que é o modelo Dolev–Yao e o que ele **não** assume?
7. Percorra os cinco porquês de "por que preciso de certificado" e diga onde a corrente para.
8. Por que o tamanho dos registros ainda vaza informação?
9. Qual é a diferença entre handshake protocol e record protocol?
10. O que o caso DigiNotar demonstra sobre o modelo de confiança?

*Respostas: §2, §3.2, §5.2, §2, §7, §5.1, §6, §3.2, §3, §5.2.*

---

**Próximo:** [11-historia.md](11-historia.md) — como chegamos até aqui, e o que cada acidente ensinou.
