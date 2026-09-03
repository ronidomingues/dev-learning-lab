# 12 · Anatomia do pacote ARP — byte a byte

> **Nível:** intermediário → avançado
> **Data:** 14/08/2026
> Pré-requisito: hexadecimal básico ([02](02-pre-requisitos.md) §3). Ao fim deste arquivo você
> decodifica um pacote ARP à mão, sem consultar tabela.

---

## 1. Onde o ARP fica dentro do quadro Ethernet

Um pacote ARP não viaja sozinho: vai **dentro de um quadro Ethernet**. O quadro é:

```
┌───────────────┬───────────────┬───────────┬──────────────────────┬─────────┐
│ MAC destino   │ MAC origem    │ EtherType │ payload              │  FCS    │
│   6 bytes     │   6 bytes     │  2 bytes  │  (o pacote ARP: 28)  │ 4 bytes │
└───────────────┴───────────────┴───────────┴──────────────────────┴─────────┘
```

- **MAC destino**: no request, `ff:ff:ff:ff:ff:ff` (broadcast). No reply, o MAC de quem perguntou.
- **EtherType**: `0x0806` identifica "o que vem dentro é ARP". (IPv4 seria `0x0800`.)
- **payload**: os 28 bytes do ARP para o caso IPv4/Ethernet.
- Como o mínimo de um quadro Ethernet é 46 bytes de payload e o ARP tem só 28, ele é
  **preenchido** (*padding*) com zeros até 46 — por isso o `tcpdump` mostra `length 46`.

---

## 2. Os 28 bytes do ARP (IPv4 sobre Ethernet)

```
 offset  tam  campo                          valor típico (request p/ IPv4/Ethernet)
 ──────  ───  ────────────────────────────   ─────────────────────────────────────
   0      2   Hardware Type (HTYPE)           0x0001   (Ethernet)
   2      2   Protocol Type (PTYPE)           0x0800   (IPv4 — mesmo nº do EtherType de IP)
   4      1   Hardware Addr Length (HLEN)     0x06     (MAC tem 6 bytes)
   5      1   Protocol Addr Length (PLEN)     0x04     (IPv4 tem 4 bytes)
   6      2   Operation (OPER / opcode)       0x0001 request | 0x0002 reply
   8      6   Sender Hardware Addr (SHA)      MAC de quem envia
  14      4   Sender Protocol Addr (SPA)      IP de quem envia
  18      6   Target Hardware Addr (THA)      MAC do alvo (00:00:00:00:00:00 no request!)
  24      4   Target Protocol Addr (TPA)      IP do alvo (o que se quer resolver)
```

Pontos que sempre pegam o iniciante:

- **HTYPE/PTYPE/HLEN/PLEN** existem porque o ARP é genérico ([11](11-historia.md) §2). Eles
  dizem "os endereços aqui dentro são MAC de 6 bytes e IP de 4 bytes". Em 99,99% dos casos são
  os mesmos quatro valores acima.
- **PTYPE = 0x0800**, o mesmo número do EtherType de IPv4. Não é coincidência: Plummer reusou o
  espaço de EtherTypes para o "tipo de protocolo" do ARP.
- **THA no request é tudo zero.** É óbvio quando você pensa: você está perguntando *qual é* o MAC
  do alvo — se soubesse, não perguntaria. O campo existe (formato fixo) mas vai zerado.
- **Há dois pares (Sender, Target).** O request preenche Sender (você) e o TPA (o IP que quer),
  deixando o THA zerado. O reply preenche **os quatro**: agora o "Sender" é o antigo alvo, e o
  THA/TPA apontam de volta para quem perguntou.

---

## 3. Um request de verdade, decodificado à mão

Bytes capturados (hipotéticos mas válidos), sua máquina `10.209.2.168`
(`d0:94:66:99:99:99`) perguntando por `10.209.0.1`:

```
Ethernet:
  ff ff ff ff ff ff              MAC destino = broadcast
  d0 94 66 99 99 99              MAC origem  = eu
  08 06                          EtherType   = ARP
ARP:
  00 01                          HTYPE = 1  (Ethernet)
  08 00                          PTYPE = 0x0800 (IPv4)
  06                             HLEN  = 6
  04                             PLEN  = 4
  00 01                          OPER  = 1 (request)
  d0 94 66 99 99 99              SHA   = meu MAC
  0a d1 02 a8                    SPA   = 10.209.2.168   (0a=10, d1=209, 02=2, a8=168)
  00 00 00 00 00 00              THA   = desconhecido (zerado)
  0a d1 00 01                    TPA   = 10.209.0.1     (alvo)
```

Confira o SPA: `0a`=10, `d1`=209, `02`=2, `a8`=168 → **10.209.2.168**. ✔

O reply que volta, de `10.209.0.1` (`6c:31:0e:44:44:04`):

```
Ethernet:
  d0 94 66 99 99 99              destino = eu (unicast agora!)
  6c 31 0e 44 44 04              origem  = o gateway
  08 06                          ARP
ARP:
  00 01 08 00 06 04              HTYPE/PTYPE/HLEN/PLEN iguais
  00 02                          OPER = 2 (reply)
  6c 31 0e 44 44 04              SHA = MAC do gateway   ← a resposta que eu queria
  0a d1 00 01                    SPA = 10.209.0.1
  d0 94 66 99 99 99              THA = meu MAC
  0a d1 02 a8                    TPA = 10.209.2.168
```

O que sua máquina extrai e guarda no cache: **SPA (10.209.0.1) → SHA (6c:31:0e:44:44:04)**.

---

## 4. Ver isso na ferramenta

No `tcpdump` (`sudo tcpdump -i enp2s0 -e -n arp`), os mesmos dois pacotes:

```
d0:94:66:99:99:99 > ff:ff:ff:ff:ff:ff, ARP, Request who-has 10.209.0.1 tell 10.209.2.168, length 46
6c:31:0e:44:44:04 > d0:94:66:99:99:99, ARP, Reply 10.209.0.1 is-at 6c:31:0e:44:44:04, length 46
```

Mapeamento texto ↔ campos:
- `who-has 10.209.0.1` = TPA;
- `tell 10.209.2.168` = SPA;
- `is-at 6c:31:0e:44:44:04` = SHA do reply;
- destino `ff:ff:...` no request, unicast no reply = a assimetria broadcast/unicast.

No Wireshark, filtro de exibição `arp`, a árvore mostra cada campo nomeado. Vale abrir uma vez.

---

## 5. Construir e ler com Scapy (prática)

```python
from scapy.all import ARP, Ether

# montar um request
pkt = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(op=1, psrc="10.209.2.168",
                                          hwsrc="d0:94:66:99:99:99", pdst="10.209.0.1")
pkt.show()          # imprime todos os campos com nome
bytes(pkt).hex()    # os bytes crus — confronte com a seção 3

# ler os campos de um reply recebido (resp[0][1] no exemplo 11 do cap. 06)
# reply.op == 2 ; reply.psrc == IP resolvido ; reply.hwsrc == MAC procurado
```
`op` = OPER, `psrc/pdst` = SPA/TPA, `hwsrc/hwdst` = SHA/THA. Scapy usa nomes curtos; o mapa
acima liga cada um ao byte.

---

## 6. Casos especiais no formato

- **Gratuitous ARP**: um ARP (request **ou** reply) em que **SPA == TPA** — você anuncia o seu
  próprio IP. No request gratuito, você "pergunta pelo seu próprio IP" (para detectar conflito);
  no reply gratuito, "responde sem ninguém ter perguntado" (para atualizar caches). Ver
  [15](15-variacoes-do-protocolo.md) §2.
- **ARP Probe** (RFC 5227): um request com **SPA = 0.0.0.0** e TPA = o IP que você *pretende*
  usar — "isto é de alguém?" sem ainda reivindicá-lo. O SPA zerado evita poluir o cache alheio.
- **RARP** (EtherType `0x8035`, opcodes 3/4): mesmo layout, pergunta invertida. Morto.
- **InARP** (opcodes 8/9): "sei o MAC, quero o IP" — usado em Frame Relay/ATM, raríssimo hoje.

---

## 7. Por que exatamente 28 bytes, e por que padding

`2+2+1+1+2 + (6+4)×2 = 8 + 20 = 28`. Fixo para IPv4/Ethernet. Como o quadro Ethernet exige
payload mínimo de **46 bytes** (herança da detecção de colisão do coaxial original — o quadro
tinha de durar tempo suficiente no fio), os 18 bytes que faltam são **padding** de zeros. Por
isso todo ARP aparece com `length 46`. É uma cicatriz física de 1980 visível até hoje —
**parada legítima: lei da física do CSMA/CD** (o quadro mínimo garantia que uma colisão fosse
detectada antes de a transmissão acabar).

---

## Autoteste

1. Qual campo do ARP request vai zerado, e por que isso é logicamente inevitável?
2. Decodifique o SPA `0a d1 05 07` para decimal pontuado.
3. Por que o request tem MAC destino `ff:ff:...` e o reply não?
4. O que sua máquina extrai de um reply para guardar no cache — quais dois campos?
5. Como você reconhece um *gratuitous ARP* olhando só os campos SPA e TPA?
6. Por que todo pacote ARP aparece com `length 46` no tcpdump, se o ARP tem 28 bytes?
7. Para que servem HTYPE, PTYPE, HLEN e PLEN se são quase sempre os mesmos quatro valores?

*(Respostas: 1 → THA, seção 2; 2 → 10.209.5.7; 3 → seção 4/assimetria; 4 → SPA→SHA, seção 3;
5 → SPA==TPA, seção 6; 6 → padding p/ 46, seção 7; 7 → generalidade histórica, seções 2 e
[11](11-historia.md).)*

---

**Fontes:** RFC 826 (formato), RFC 5227 (probe/ACD), RFC 5494 (campos); saída de `tcpdump`
4.99.1 e documentação do Scapy. Consultado em 14/08/2026.

**Próximo:** [13-o-ciclo-de-resolucao.md](13-o-ciclo-de-resolucao.md)
