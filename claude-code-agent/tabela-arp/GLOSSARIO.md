# Glossário — tabela ARP

> **Data:** 14/08/2026 · Todo termo técnico usado no curso, definido. Termo em inglês mantido
> quando é assim que o campo o usa, com a tradução na primeira ocorrência.

---

**ACD** (*Address Conflict Detection*) — detecção de conflito de IP, padronizada na RFC 5227.
Usa ARP para descobrir se um IP já está em uso antes de assumi-lo. É o `arping -D`.

**Aging (envelhecimento)** — política de expirar entradas de cache velhas, porque mapeamentos
IP↔MAC mudam com o tempo.

**Anycast gateway (distribuído)** — configuração em que o mesmo IP/MAC de gateway existe em
vários switches simultaneamente; requisito para ARP suppression em EVPN.

**ARP** (*Address Resolution Protocol*) — protocolo de resolução de endereços (RFC 826, 1982)
que descobre o MAC correspondente a um IP no mesmo segmento. O tema deste curso.

**ARP cache** — ver *tabela ARP*.

**ARP flux** — comportamento do Linux em que um host multi-homed responde ARP por todos os seus
IPs em todas as interfaces, confundindo a rede. Corrige-se com `arp_ignore`/`arp_announce`.

**ARP probe** — request com SPA = 0.0.0.0 e TPA = IP pretendido; pergunta "isto é de alguém?"
sem reivindicar o IP (RFC 5227).

**ARP spoofing / poisoning** — ataque em que o atacante forja respostas ARP para se colocar no
meio da comunicação (*man-in-the-middle*). Ver [18](18-seguranca.md).

**ARP suppression** — técnica (EVPN/Wi-Fi) em que a rede responde ao ARP localmente, via plano
de controle, eliminando o broadcast. Ver [65](65-estado-da-arte.md).

**arpwatch** — ferramenta que monitora pares IP↔MAC e alerta quando um muda (detecção de
spoofing).

**Broadcast** — envio a **todos** no segmento; MAC de destino `ff:ff:ff:ff:ff:ff`. O ARP request
é broadcast.

**CAM (tabela)** — ver *tabela MAC*. *Content-Addressable Memory*, a memória onde o switch guarda
MAC→porta.

**CIDR** — notação de máscara (`/20`) que define quantos bits são de rede. Determina o tamanho do
domínio de broadcast e o alcance do ARP.

**DAI** (*Dynamic ARP Inspection*) — defesa no switch que descarta ARP que não bate com a base de
DHCP snooping. Ver [18](18-seguranca.md).

**DELAY** — estado NUD: a entrada foi usada e está no período de graça antes de sondar.

**DHCP snooping** — o switch observa o DHCP para saber quais pares IP↔MAC↔porta são legítimos;
base do DAI.

**Domínio de broadcast** — conjunto de dispositivos que recebem os broadcasts uns dos outros.
Delimitado por roteador ou VLAN, não por switch. É a fronteira do ARP.

**eBPF** — mecanismo de programação do kernel Linux; usado por Cilium para tratar rede (incl.
ARP) no caminho de dados. Ver [65](65-estado-da-arte.md).

**EtherType** — campo do quadro Ethernet que diz qual protocolo vem dentro: `0x0806` = ARP,
`0x0800` = IPv4, `0x8035` = RARP, `0x8100` = VLAN.

**EVPN** (*Ethernet VPN*) — camada de controle baseada em BGP para data centers; habilita ARP
suppression em VXLAN. Ver [65](65-estado-da-arte.md).

**FAILED** — estado NUD: as tentativas de resolver falharam; o fracasso é guardado para evitar
nova tempestade de broadcast.

**Gateway (default)** — o roteador para onde vai o tráfego destinado a fora da sub-rede. O ARP
resolve o MAC **dele** para destinos remotos.

**gc_thresh1/2/3** — limiares do coletor de lixo da tabela de vizinhos no Linux. `gc_thresh3` é o
teto rígido; acima dele, entradas novas são recusadas. Ver [14](14-a-tabela-por-dentro.md) §7.

**Gratuitous ARP (ARP gratuito)** — ARP em que SPA == TPA; anuncia o próprio IP↔MAC sem ser
perguntado. Usado em failover e detecção de conflito; abusado em spoofing.

**HLEN / PLEN** — campos do pacote ARP: comprimento do endereço de hardware (6) e de protocolo
(4). Ver [12](12-anatomia-do-pacote.md).

**HTYPE / PTYPE** — tipo de hardware (1 = Ethernet) e de protocolo (`0x0800` = IPv4) no pacote
ARP.

**INCOMPLETE** — estado NUD: request enviado em broadcast, aguardando o primeiro reply.

**InARP** (*Inverse ARP*) — "sei o circuito, quero o IP"; usado em Frame Relay/ATM. Extinto.

**IP (endereço)** — identificador de camada 3, hierárquico e roteável.

**lladdr** (*link-layer address*) — o endereço de camada de enlace (o MAC), como o `ip neigh` o
chama.

**MAC (endereço)** — *Media Access Control*; identificador de camada 2, plano, 48 bits, gravado
de fábrica (mas reconfigurável). Os 3 primeiros bytes são o OUI.

**MAC localmente administrado** — MAC com o bit `0x02` no 1º octeto ligado; não vem de fábrica
(aleatório por privacidade, ou virtual, ou forjado). Sem fabricante associado.

**Multicast** — envio a um grupo; MAC `01:00:5e:...` (IPv4) ou `33:33:...` (IPv6). Não usa ARP:
o MAC é calculado do IP.

**NDP** (*Neighbor Discovery Protocol*) — o "ARP do IPv6" (RFC 4861), sobre ICMPv6, usando
multicast. Ver [20](20-ipv6-e-ndp.md).

**Next hop (próximo salto)** — o dispositivo imediatamente seguinte no caminho. O ARP sempre
resolve o next hop, nunca o destino final remoto.

**NOARP** — estado de entradas que não precisam de resolução (broadcast, multicast) — o MAC é
calculado, não perguntado.

**NS / NA** — *Neighbor Solicitation / Advertisement*; o request/reply do NDP (IPv6).

**NUD** (*Neighbor Unreachability Detection*) — a máquina de estados (REACHABLE/STALE/…) que
decide quando confiar, reverificar e desistir de uma entrada. Veio do IPv6, retroaplicada ao
IPv4 pelo Linux. Ver [14](14-a-tabela-por-dentro.md).

**OpCode (OPER)** — campo do ARP: 1 = request, 2 = reply, 3/4 = RARP, 8/9 = InARP.

**OUI** (*Organizationally Unique Identifier*) — os 3 primeiros bytes do MAC; identificam o
fabricante (registro do IEEE).

**PERMANENT** — entrada estática, criada à mão, que não envelhece e ignora ARP recebido. Base de
defesa anti-spoofing de host.

**PROBE** — estado NUD: sondando ativamente o vizinho em unicast.

**Proxy ARP** — um roteador responde ARP por IPs que não são dele, para "colar" sub-redes.
Malvisto hoje; nichado em VPN/nuvem. Ver [15](15-variacoes-do-protocolo.md) §3.

**RA / RS** — *Router Advertisement / Solicitation*; mensagens NDP para descobrir roteador e
prefixo (IPv6). Base do SLAAC.

**RA Guard** — defesa de switch contra *rogue RA* (RA falso) no IPv6.

**RARP** (*Reverse ARP*) — "sei meu MAC, qual meu IP?" (RFC 903). Morto; substituído por
BOOTP/DHCP.

**REACHABLE** — estado NUD: mapeamento confirmado nos últimos ~15–45 s (tempo aleatorizado).

**SEND** (*SEcure Neighbor Discovery*) — extensão de segurança do NDP (RFC 3971); quase não
implementada.

**SHA / SPA / THA / TPA** — campos do pacote ARP: *Sender/Target Hardware/Protocol Address* —
MAC e IP de origem e alvo. Ver [12](12-anatomia-do-pacote.md).

**SLAAC** — *Stateless Address Autoconfiguration*; o host IPv6 monta o próprio endereço a partir
do RA. Sem equivalente no ARP.

**STALE** — estado NUD: entrada válida mas não confirmada recentemente. **É usável** — o pacote
sai na hora.

**Sub-rede** — faixa de IPs definida por IP+máscara. Coincide com o domínio de broadcast e o
alcance do ARP.

**Tabela ARP (cache de vizinhos)** — estrutura num host/roteador que mapeia IP→MAC aprendido, com
estado. O objeto central deste curso. No Linux, `ip neigh` (IPv4+IPv6).

**Tabela MAC (tabela CAM)** — estrutura num **switch** que mapeia MAC→porta física. **Diferente**
da tabela ARP. Ver [17](17-arp-em-redes-reais.md) §1.

**Unicast** — envio a **um** destinatário. O ARP reply é unicast.

**Unicast flooding** — switch inunda um quadro unicast por todas as portas por ter esquecido a
porta do MAC (tabela MAC expirou antes do ARP). Ver [17](17-arp-em-redes-reais.md) §4.

**VLAN** (802.1Q) — segmentação lógica de um switch em vários domínios de broadcast. Cada VLAN
tem seu próprio "universo" de ARP.

**VRRP** — protocolo de redundância de gateway; usa IP/MAC virtual e gratuitous ARP no failover.
Ver [17](17-arp-em-redes-reais.md) §5.

**VXLAN** — encapsulamento que estende camada 2 sobre camada 3 em data centers; combinado com
EVPN e ARP suppression.

---

**Próximo:** volte ao [00-MAPA.md](00-MAPA.md).
