# 95 · Referências — specs, RFCs, código-fonte, docs

> **Nível:** todos
> **Data:** 14/08/2026
> Fontes primárias e verificáveis. Nada inventado.

---

## 1. RFCs (fontes primárias)

| RFC | Título | Ano | Relevância |
|---|---|---|---|
| **826** | An Ethernet Address Resolution Protocol | 1982 | **O ARP.** STD 37. Autor: David C. Plummer. [rfc-editor.org/info/rfc826](https://www.rfc-editor.org/info/rfc826) |
| 903 | A Reverse Address Resolution Protocol | 1984 | RARP ([15](15-variacoes-do-protocolo.md) §4) |
| 1027 | Using ARP to Implement Transparent Subnet Gateways | 1987 | Proxy ARP ([15](15-variacoes-do-protocolo.md) §3) |
| 1112 | Host Extensions for IP Multicasting | 1989 | mapeamento IP multicast → MAC ([15](15-variacoes-do-protocolo.md) §5) |
| 1122 | Requirements for Internet Hosts | 1989 | comportamento de cache/host |
| 2390 | Inverse Address Resolution Protocol | 1998 | InARP |
| **5227** | IPv4 Address Conflict Detection (ACD) | 2008 | gratuitous ARP / probe / `arping -D` |
| 5494 | IANA Allocation Guidelines for ARP | 2009 | organização dos campos |
| **4861** | Neighbor Discovery for IPv6 (NDP) | 2007 | o sucessor; NUD ([20](20-ipv6-e-ndp.md)) |
| 4862 | IPv6 Stateless Address Autoconfiguration (SLAAC) | 2007 | RS/RA, autoconfig |
| 3971 | SEcure Neighbor Discovery (SEND) | 2005 | segurança do NDP ([20](20-ipv6-e-ndp.md) §5) |
| 4443 | ICMPv6 | 2006 | transporte do NDP |
| 5798 | VRRPv3 | 2010 | MAC virtual, failover ([17](17-arp-em-redes-reais.md) §5) |

Todas grátis em [rfc-editor.org](https://www.rfc-editor.org/).

---

## 2. Padrões IEEE

| Padrão | Assunto | Relevância |
|---|---|---|
| IEEE 802.3 | Ethernet | quadro, MAC de 48 bits, EtherType |
| IEEE 802.1Q | VLAN tagging | domínios de broadcast por VLAN ([17](17-arp-em-redes-reais.md) §2) |
| IEEE 802.11 | Wi-Fi | ARP sobre meio sem fio ([17](17-arp-em-redes-reais.md) §3) |
| IEEE OUI / MA-L registry | atribuição de prefixos MAC | base de fabricante ([01](01-introducao-leigo.md) §4). Consulta: [standards-oui.ieee.org](https://standards-oui.ieee.org/) |

---

## 3. Código-fonte (Linux)

O subsistema de vizinhos, onde ARP e NDP realmente vivem:

| Arquivo (kernel Linux) | O que contém |
|---|---|
| `net/core/neighbour.c` | a máquina de estados NUD genérica, o GC, os `gc_thresh` ([14](14-a-tabela-por-dentro.md)) |
| `net/ipv4/arp.c` | o resolvedor ARP (IPv4) |
| `net/ipv6/ndisc.c` | o resolvedor NDP (IPv6) |
| `Documentation/networking/` | descrição dos sysctls (`arp_ignore`, `arp_announce`, etc.) |

Navegável em [elixir.bootlin.com](https://elixir.bootlin.com/linux/latest/source/net/core/neighbour.c).

**iproute2** (o `ip neigh`): [git.kernel.org/pub/scm/network/iproute2](https://git.kernel.org/pub/scm/network/iproute2/iproute2.git/)
· versão de referência 7.1.0 (2026).

---

## 4. Documentação oficial e de fornecedor

- **man pages:** `ip-neighbour(8)`, `arp(8)`, `arping(8)`, `arp-scan(1)`, `tcpdump(8)`, `arp(7)`.
- **Microsoft Learn:** `Get-NetNeighbor`, `New-NetNeighbor`, `Set-NetIPInterface`
  (learn.microsoft.com).
- **Cisco:** `show ip arp`, Dynamic ARP Inspection, DHCP Snooping (cisco.com/docs).
- **Arista / Juniper / Dell / NVIDIA-Cumulus:** ARP suppression / EVPN ([65](65-estado-da-arte.md)).
- **Wireshark:** [wiki.wireshark.org/AddressResolutionProtocol](https://wiki.wireshark.org/AddressResolutionProtocol).
- **Scapy:** [scapy.readthedocs.io](https://scapy.readthedocs.io/).

---

## 5. Ferramentas (projetos)

| Ferramenta | Repositório / site |
|---|---|
| iproute2 | git.kernel.org (network/iproute2) |
| net-tools | sourceforge.net/projects/net-tools |
| tcpdump / libpcap | [tcpdump.org](https://www.tcpdump.org/) |
| Wireshark | [wireshark.org](https://www.wireshark.org/) |
| nmap / arp-scan | [nmap.org](https://nmap.org/) · github.com/royhills/arp-scan |
| arpwatch | ee.lbl.gov / pacotes de distro |
| Scapy | [github.com/secdev/scapy](https://github.com/secdev/scapy) |

---

## 6. Pessoas (para seguir a fonte)

- **David C. Plummer** — autor da RFC 826 (1982).
- **Robert Metcalfe & David Boggs** — Ethernet (Xerox PARC).
- **W. Richard Stevens** (1951–1999) — *TCP/IP Illustrated*; a forma canônica de explicar
  protocolos com capturas reais.
- **Van Jacobson** — trabalho sobre congestionamento/sincronização, base conceitual da
  aleatorização de timers ([14](14-a-tabela-por-dentro.md) §3, [60](60-teoria-avancada.md) §5).

---

## 7. O que foi executado neste curso (rastreabilidade)

Para honestidade, o que gerou as saídas reais mostradas no material:

- **Máquina:** Ubuntu 22.04.5 LTS, kernel 6.8.0-136, iproute2 5.15.0, net-tools 1.60,
  tcpdump 4.99.1, arp-scan 1.9.7, nmap local, Python 3.10.12.
- **Executado e mostrado:** `ip neigh show` (todas as variações), transições de estado
  (`STALE→DELAY→REACHABLE→STALE` e `INCOMPLETE→FAILED`) medidas segundo a segundo, `ip -s -d
  neigh`, `ip -j neigh`, filtros `nud`, `ip neigh get`, `ip ntable show`, sysctls de
  `neigh`/`conf`, o erro real de `ip neigh flush` sem root, o erro real de captura sem
  privilégio, e o [07-projeto-modelo](07-projeto-modelo/) (`arpinspect` + **19 testes, todos
  passando**, contra a tabela real e o arquivo de spoofing).
- **Não executado nesta máquina (declarado):** comandos macOS/Windows/Cisco (da documentação);
  captura com `tcpdump`/Wireshark e `arp-scan`/`arping` (exigem root/privilégio ausente aqui);
  labs de ataque (exigem lab isolado); MAC dos 3 últimos octetos foram mascarados por privacidade.
- **Pesquisado na web em 14/08/2026:** versões (iproute2 7.1.0, Wireshark 4.6.8, nmap 7.991),
  EVPN ARP suppression, DAI, cursos PT/EN/FR, RFC 826.

---

## Autoteste

1. Qual RFC define o ARP, de que ano, e qual é o número do padrão (STD)?
2. Onde, no código do kernel Linux, vive a máquina de estados NUD?
3. Qual RFC define o sucessor do ARP no IPv6?
4. Onde consultar oficialmente a que fabricante pertence um prefixo MAC?
5. Qual RFC padroniza a detecção de conflito de IP (o `arping -D`)?
6. Cite a obra e a pessoa que popularizaram "explicar protocolo com captura real".
7. Que saídas deste curso foram medidas de verdade, e o que foi declarado como não executado?

---

**Fontes:** as próprias referências listadas, todas verificáveis online, consultadas em
14/08/2026.

**Próximo:** [GLOSSARIO.md](GLOSSARIO.md)
