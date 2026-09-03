# 14 · UDP, ICMP, SCTP, DCCP e QUIC — os outros transportes

**Nível:** intermediário a avançado · **Última atualização:** 14/08/2026
Os experimentos com UDP deste arquivo foram **executados** em Ubuntu 22.04.5 em 14/08/2026.

---

## Por que UDP merece um arquivo próprio

Porque quase tudo o que você aprendeu sobre portas no [`13`](13-tcp-por-dentro.md) **não se
aplica**. Não há estado, não há `LISTEN`, não há handshake, não há confirmação. E, em
consequência, **varrer portas UDP é um problema fundamentalmente diferente e muito pior**.

E porque o serviço mais importante da internet — DNS — e o transporte que está engolindo a
web — QUIC — são ambos UDP.

---

## 1. UDP em uma tela

```
┌──────────────────────────────────────────┐
│ CABEÇALHO UDP — 8 bytes. É isso.         │
│ porta origem (2B) │ porta destino (2B)   │
│ comprimento  (2B) │ checksum      (2B)   │
└──────────────────────────────────────────┘
```

Oito bytes, contra 20 do TCP. Sem número de sequência, sem ACK, sem flags, sem janela.
O RFC 768 (agosto de 1980) tem **três páginas**. O RFC 793 (TCP) tem 85.

| | TCP | UDP |
|---|---|---|
| Conexão | Sim (handshake) | Não |
| Entrega garantida | Sim | Não |
| Ordem garantida | Sim | Não |
| Controle de congestionamento | Sim | **Não** — é problema da aplicação |
| Estado no kernel | Muito | Quase nenhum |
| Cabeçalho | 20+ bytes | 8 bytes |
| Estado observável | 12 estados | **`UNCONN`, e só** |

### O que "não tem conexão" significa na prática

```bash
ss -ulpn
```
```
udp   UNCONN 0  0  0.0.0.0:5353   0.0.0.0:*
udp   UNCONN 0  0  127.0.0.53:53  0.0.0.0:*
```

`UNCONN` — *unconnected*. **Não existe `LISTEN` em UDP.** Um socket UDP com `bind()` recebe
datagramas; não há nada para "escutar", porque não há conexão para aceitar.

E há uma consequência boa: **um socket UDP não guarda estado por cliente**. Um servidor DNS
atende milhões de consultas com um socket só. Não há `accept()`, não há descritor por
cliente, não há `TIME_WAIT`. É por isso que UDP escala tão bem para pedido-resposta curto.

E uma consequência ruim: **o servidor precisa implementar sozinho** tudo o que o TCP daria
de graça — retransmissão, ordem, controle de congestionamento. O QUIC é, essencialmente,
"o TCP reimplementado em espaço de usuário sobre UDP".

---

## 2. Como se sabe que uma porta UDP está fechada

Aqui está o nó do problema. Em TCP, uma porta fechada responde RST. **Em UDP, o próprio
protocolo não responde nada.**

Quem responde é o **ICMP**:

> **ICMP tipo 3, código 3** — *Destination Unreachable: Port Unreachable*

### O experimento

```python
u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
u.connect(("127.0.0.1", 54321))     # porta sem ninguém
u.send(b"ping")
u.settimeout(2)
print(u.recv(100))
```

**Saída real:**

```
UDP para porta fechada -> ConnectionRefusedError 111 [Errno 111] Connection refused
```

Um `ConnectionRefusedError` **num socket UDP**, que supostamente não tem conexão. O que
aconteceu: o kernel local recebeu o ICMP "port unreachable" e, como o socket estava
`connect()`ado (o que em UDP significa apenas "fixe o destino"), ele conseguiu associar o
erro àquele socket e o entregou na chamada seguinte.

**Se o socket não estivesse `connect()`ado, o erro seria perdido em silêncio.** Esse é o
comportamento padrão do UDP: erros somem.

### Por que isso torna a varredura UDP ruim

| Você manda datagrama | Volta | Conclusão possível |
|---|---|---|
| → | resposta da aplicação | **aberta** — a única certeza |
| → | ICMP tipo 3 código 3 | **fechada** |
| → | ICMP tipo 3 código 1/2/9/10/13 | **filtrada** |
| → | **nada** | **`open|filtered`** — não dá para saber |

O último caso é o comum, e é a razão de o `nmap` ter uma classe própria para ele:
`open|filtered`. Três coisas produzem "nada":

1. A porta está aberta e o serviço não responde a lixo (comportamento normal!).
2. Um firewall descartou seu datagrama.
3. O ICMP de resposta foi descartado no caminho.

**E há o agravante decisivo:** o RFC 1812 recomenda **limitar a taxa de ICMP**, e o Linux
faz isso por padrão:

```bash
sysctl net.ipv4.icmp_ratelimit          # tipicamente 1000 (ms entre mensagens)
sysctl net.ipv4.icmp_msgs_per_sec       # tipicamente 1000
```

Logo, se você sondar 1 000 portas UDP, o alvo não vai mandar 1 000 ICMPs. Vai mandar
uns poucos por segundo. **O `nmap -sU` precisa esperar e retransmitir cada porta**, e é por
isso que uma varredura UDP completa pode levar **horas** onde a TCP leva segundos.

```bash
sudo nmap -sU --top-ports 20 alvo        # 20 portas. Já é o que dá para fazer.
sudo nmap -sU -sV -p 53,123,161,500,1900 alvo   # com sondas específicas: bem melhor
```

**A estratégia profissional para UDP:** não varra às cegas. Sonde as portas UDP que
importam, com **sondas específicas do protocolo** (`-sV` faz isso: manda uma consulta DNS
de verdade na 53, uma consulta SNMP na 161). Uma resposta positiva é conclusiva; a ausência
dela nunca é.

---

## 3. As portas UDP que importam

| Porta | Serviço | Por que importa |
|---|---|---|
| **53** | DNS | A porta mais importante da internet |
| **67/68** | DHCP | Sem ela sua máquina não tem IP |
| **123** | NTP | Relógio. Amplificação DDoS clássica |
| **161/162** | SNMP | Monitoração. v1/v2c: senha em texto claro |
| **500 / 4500** | IKE / IPsec NAT-T | VPN |
| **514** | Syslog | Log remoto, sem autenticação |
| **1194** | OpenVPN | |
| **1900** | SSDP/UPnP | Amplificação DDoS |
| **4789** | VXLAN | Rede de containers/nuvem |
| **5353** | mDNS | Descoberta local (Bonjour/Avahi) |
| **11211** | memcached | Amplificação recorde de 2018 |
| **51820** | WireGuard | VPN moderna |
| **443** | **QUIC / HTTP/3** | A porta UDP que passou a importar |

### Amplificação — por que UDP é a arma preferida de DDoS

O ataque tem três ingredientes, e **os três só existem em UDP**:

1. **Não há handshake**, logo o endereço de origem pode ser forjado sem consequência.
2. **A resposta é muito maior que o pedido.**
3. **Existem milhões de servidores mal configurados** respondendo a qualquer um.

O atacante manda um pedido pequeno com o **IP da vítima** como origem. O servidor responde
— para a vítima. Multiplique por milhões.

| Serviço | Fator de amplificação típico |
|---|---|
| memcached (11211) | até ~51 000× |
| NTP `monlist` (123) | ~550× |
| DNS ANY (53) | ~50× |
| SSDP (1900) | ~30× |
| CLDAP (389) | ~55× |

O ataque de 1,35 Tbit/s contra o GitHub em fevereiro de 2018 usou memcached. Depois dele, o
projeto **desabilitou o UDP por padrão** — uma correção de configuração padrão, não de código.

**A defesa que funciona e quase ninguém aplica:** BCP 38 (RFC 2827) — filtragem de entrada
na borda, de modo que um provedor não deixe sair pacote com IP de origem que não é dele.
É conhecida desde 2000. A adoção segue parcial, porque o custo é de quem implementa e o
benefício é de terceiros — um problema clássico de incentivo, não de tecnologia.

---

## 4. ICMP — o protocolo sem porta que todo mundo tenta filtrar por porta

**ICMP não tem portas.** Ele tem **tipo** e **código**.

| Tipo | Código | Nome | Onde aparece |
|---|---|---|---|
| 0 | 0 | Echo Reply | resposta do `ping` |
| 3 | 0 | Net Unreachable | |
| 3 | 1 | Host Unreachable | |
| **3** | **3** | **Port Unreachable** | **como se descobre porta UDP fechada** |
| 3 | 4 | Fragmentation Needed | **essencial para o PMTU** |
| 3 | 13 | Communication Administratively Prohibited | firewall educado |
| 8 | 0 | Echo Request | o `ping` |
| 11 | 0 | Time Exceeded | é assim que o `traceroute` funciona |

### ⚠️ Bloquear ICMP inteiro quebra a internet

É uma prática difundida e **errada**. O motivo é o tipo 3 código 4.

Quando um pacote grande demais encontra um enlace com MTU menor e tem o bit *don't fragment*
ligado, o roteador devolve "Fragmentation Needed" **informando o MTU correto**. O emissor
reduz o tamanho e segue.

Se você bloqueia ICMP, essa mensagem não chega. O emissor continua mandando pacotes grandes
demais, que somem. O sintoma é característico e enlouquecedor:

> A conexão abre. Requisições pequenas funcionam. Requisições grandes travam para sempre.

Chama-se **PMTU black hole**. Diagnostica-se com:

```bash
ping -M do -s 1472 destino        # 1472 + 28 = 1500. Reduza até passar.
tracepath destino                  # mostra onde o MTU cai
```

**A regra correta:** bloqueie *echo request* se quiser (perde pouco, ganha pouco), mas
**nunca bloqueie ICMP tipo 3 nem tipo 11**.

---

## 5. SCTP e DCCP — os transportes que quase ninguém usa

| | SCTP (RFC 9260) | DCCP (RFC 4340) |
|---|---|---|
| Tem porta? | Sim, 16 bits | Sim, 16 bits |
| Diferencial | Multi-stream, multi-homing | Datagramas com controle de congestionamento |
| Onde é usado | **Telecomunicações**: SS7 sobre IP, Diameter, interfaces 4G/5G | Praticamente nada |
| Suporte | Linux tem; muitos NATs não | Marginal |

**SCTP é relevante se você trabalha com telecomunicações e irrelevante fora disso.**
Ele resolve, entre outras coisas, o *head-of-line blocking* — o problema de um pacote perdido
travar todos os fluxos que compartilham a conexão. Foi projetado em 2000 e nunca decolou
fora das telecoms.

**Por que não decolou?** Porque NATs e firewalls domésticos só entendem TCP e UDP. Um
protocolo de transporte novo simplesmente não atravessa a internet real. Esta é a lição
central que o QUIC aprendeu — e a razão de ele ter sido construído **sobre UDP** em vez de
ser um protocolo IP novo.

É a mesma lição do "flag day" de 1983, dita de outro jeito: **depois de 1983, só passa o que
se disfarça de algo já permitido.**

```bash
nmap -sY alvo        # varredura SCTP INIT (exige root)
ss --sctp            # sockets SCTP locais
```

---

## 6. QUIC — o transporte que virou a exceção mais importante

**O que é:** um transporte confiável, com controle de congestionamento e criptografia
obrigatória, implementado **em espaço de usuário sobre UDP**.

- **RFC 9000** (maio/2021) — QUIC
- **RFC 9114** (junho/2022) — HTTP/3

### Por que sobre UDP

Não por elegância. Por **sobrevivência**. Um transporte novo no nível do IP não atravessaria
os NATs, firewalls e middleboxes da internet real — foi exatamente o que matou o SCTP.
UDP passa em todo lugar (quase).

E há um segundo motivo, mais profundo: implementar em espaço de usuário permite **evoluir**.
Uma mudança no TCP exige atualizar kernels do mundo inteiro — o que leva uma década. Uma
mudança no QUIC exige atualizar o navegador, o que leva seis semanas.

### O que isso faz com o nosso assunto

**1. `443/UDP` é um serviço de verdade agora.**

```bash
ss -ulpn | grep :443
sudo nmap -sU -p 443 alvo
curl --http3 https://alvo/          # se seu curl tiver suporte
```

Um firewall que libera "porta 443" pensando em TCP **bloqueia HTTP/3 sem perceber**. É
apontado nas fontes de 2026 como o principal obstáculo à adoção. Rede corporativa que
bloqueia UDP na 443 força os navegadores a cair de volta para TCP — o que funciona (por
projeto) e passa despercebido, exceto pela perda de desempenho.

**2. Não há handshake TCP para observar.** Não existe SYN-ACK. Um scanner precisa falar
QUIC de verdade para descobrir qualquer coisa. `nmap -sU -p 443` sozinho é quase inútil.

**3. A visibilidade do operador de rede caiu.** Em TCP+TLS, quem observa vê números de
sequência, flags e (sem ECH) o SNI. Em QUIC, quase tudo é cifrado desde o primeiro pacote —
sobra o *connection ID*, os IPs, e as portas.

**4. Migração de conexão.** O QUIC identifica a conexão por um *connection ID*, não pela
quádrupla. Você troca de Wi-Fi para 5G, seu IP e sua porta mudam, e **a conexão sobrevive**.

Essa é a ruptura conceitual mais importante do arquivo: **em QUIC, a quádrupla deixa de
identificar a conexão.** Todo o modelo do [`10-fundamentos.md`](10-fundamentos.md) — que
vale para TCP desde 1981 — deixa de valer aqui. Ferramentas de rastreamento de fluxo
construídas sobre a quádrupla precisam ser repensadas.

### Adoção, agosto de 2026

| Fonte | Métrica | Valor |
|---|---|---|
| W3Techs | Sites que **suportam** HTTP/3 | ~39 % |
| Cloudflare | Tráfego na borda | ~35 % |
| TechnologyChecker | **Carregamentos de página** por HTTP/3 | ~21 % |

*(Pesquisado na web em 14/08/2026. As fontes divergem porque medem denominadores diferentes —
suportar não é ser usado.)*

---

## 7. Tabela final: quem tem porta, quem não tem

| Protocolo | Nº IP | Porta? | Estado observável |
|---|---|---|---|
| TCP | 6 | Sim | 12 estados |
| UDP | 17 | Sim | só `UNCONN` |
| SCTP | 132 | Sim | tem estados |
| DCCP | 33 | Sim | tem estados |
| **ICMP** | 1 | **Não** | tipo/código |
| **ICMPv6** | 58 | **Não** | idem, e é essencial ao IPv6 (ND) |
| **GRE** | 47 | **Não** | — |
| **ESP** (IPsec) | 50 | **Não** | — |
| **AH** (IPsec) | 51 | **Não** | — |
| **QUIC** | (dentro do UDP) | **Herda a do UDP** | invisível de fora |

⚠️ **ICMPv6 não pode ser bloqueado, ponto final.** O IPv6 usa ICMPv6 para *Neighbor
Discovery* — o equivalente ao ARP. Bloquear ICMPv6 no IPv6 é como bloquear ARP no IPv4:
a rede simplesmente para de funcionar. Ver RFC 4890, que lista quais tipos podem ser
filtrados com segurança.

---

## Autoteste

1. Por que não existe estado `LISTEN` em UDP? O que aparece no lugar?
2. Como um socket UDP consegue devolver `ConnectionRefusedError` se UDP não tem conexão?
   E o que precisa ser verdade para que ele consiga?
3. Explique, em três frases, por que `nmap -sU` é ordens de grandeza mais lento que
   `nmap -sS`.
4. O que significa `open|filtered` numa saída de varredura UDP, e por que essa categoria
   precisa existir?
5. Quais três condições tornam a amplificação por UDP possível? Qual delas o BCP 38
   ataca, e por que ele não é adotado universalmente?
6. Por que bloquear ICMP inteiro quebra transferências grandes mas deixa as pequenas
   funcionando? Como se chama esse sintoma e como diagnosticá-lo?
7. Por que o SCTP não decolou, e o que o QUIC fez de diferente por causa disso?
8. Em QUIC, o que identifica uma conexão — e por que isso invalida um modelo mental que
   vale para TCP desde 1981?
9. Seu firewall libera "a porta 443". Ele libera HTTP/3? Justifique.

---

*Próximo: [`15-sockets-e-o-kernel.md`](15-sockets-e-o-kernel.md) — o que o `ss` faz por dentro.*
