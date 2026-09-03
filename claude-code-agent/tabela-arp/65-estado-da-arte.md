# 65 · Estado da arte — o ARP em agosto de 2026

> **Nível:** pesquisa
> **Data:** 14/08/2026 · **este arquivo envelhece** — reavaliar a cada 6 meses.
> O protocolo não muda desde 1982. O que muda é tudo em volta.

---

## 1. O consenso de 2026: o ARP está sendo *suprimido*, não substituído

A tendência dominante nos últimos ~10 anos, consolidada em 2026, é **eliminar o broadcast do
ARP** em redes grandes por meio de um **plano de controle** que já conhece todos os pares
IP↔MAC — sem tocar no protocolo que os hosts falam. Os hosts continuam emitindo ARP de 1982; a
rede o intercepta e responde localmente.

Onde isso acontece:

- **Data centers — EVPN/VXLAN com ARP suppression.** O padrão de fato para data centers
  modernos (Cisco, Arista, Juniper, Dell, NVIDIA/Cumulus). O switch de folha (*leaf*) aprende
  todos os pares IP↔MAC via **BGP EVPN** (a camada de controle) e responde ao ARP request do
  host **localmente**, sem inundar o *fabric*. Requisito: gateway distribuído (*distributed
  anycast gateway*). Efeito: broadcast de ARP some do backbone, e a rede escala para dezenas de
  milhares de hosts sem a carga Θ(N²) do [60](60-teoria-avancada.md) §2.
- **Wi-Fi corporativo — proxy ARP/ND e broadcast suppression** no controlador/AP
  ([17](17-arp-em-redes-reais.md) §3).
- **Nuvem — SDN.** AWS/Azure/GCP nunca fizeram broadcast físico; o ARP é uma ilusão local
  respondida pelo hipervisor ([17](17-arp-em-redes-reais.md) §7).
- **Kubernetes — L3 puro.** Cilium (baseado em eBPF) e Calico evitam camada 2 entre nós; o ARP
  fica restrito ao enlace nó↔gateway.

É a volta do "servidor central" que Plummer evitou em 1982, agora como plano de controle
distribuído (BGP) — o círculo que a [11](11-historia.md) §7 previu.

---

## 2. eBPF e o plano de dados programável

A fronteira técnica mais quente em torno da resolução de vizinhos é o **eBPF** (o mecanismo de
programação do kernel Linux). Projetos como **Cilium** implementam a lógica de rede — incluindo
tratamento de ARP/vizinhança — em programas eBPF anexados ao caminho de dados (XDP/tc), em vez de
depender só da pilha tradicional. Consequências para o tema:

- respostas ARP podem ser geradas por um programa eBPF sem envolver a tabela de vizinhos clássica;
- o *overhead* da tabela de vizinhos (`gc_thresh`, [14](14-a-tabela-por-dentro.md) §7) pode ser
  contornado com estruturas eBPF próprias em escala de pod;
- observabilidade: dá para instrumentar cada resolução sem `tcpdump`.

Isto não muda o ARP no fio, mas muda **quem** responde e **como** o cache é mantido — a
implementação sob o protocolo.

---

## 3. Segurança: o que mudou (pouco) e o que preocupa (mais)

- **ARP spoofing continua funcionando** na maioria das redes internas em 2026, exatamente como
  em 2005. A defesa (DAI + DHCP snooping) existe e é madura, mas depende de switches gerenciados
  bem configurados — ausentes em boa parte das redes de escritório, escola e varejo.
- **IPv6/NDP spoofing e rogue RA** ganham relevância à medida que o IPv6 cresce; **RA Guard** e
  **ND Inspection** são a resposta, com adoção desigual ([20](20-ipv6-e-ndp.md) §5).
- **Automação ofensiva com IA**: ferramentas de pentest cada vez mais orquestram ataques de
  camada 2 (spoofing + DNS + downgrade) automaticamente. Não é uma técnica nova de ARP — é
  automação da conhecida. A defesa não muda; a velocidade do ataque, sim. (Ver
  [ethical-hacking](../ethical-hacking/00-MAPA.md) para o estado da IA ofensiva.)

Não houve, e não se espera, um "ARP seguro" universal — pelo trilema do [60](60-teoria-avancada.md)
§4 e pela imposição de compatibilidade.

---

## 4. Ferramentas — versões de referência em ago/2026

| Ferramenta | Versão atual (ago/2026) | Nota |
|---|---|---|
| **iproute2** (`ip neigh`) | **7.1.0** (jun/2026 em Debian testing); Ubuntu 22.04 traz 5.15.0 | comando de referência para ARP no Linux |
| **net-tools** (`arp`) | 1.60 (último release 2021) | **congelado/obsoleto**; ainda presente |
| **Wireshark** | **4.6.8** (ago/2026, 31 correções de segurança); Ubuntu 22.04 traz 3.6.2 | dissecção de ARP |
| **nmap** | **7.991** (05/08/2026) | descoberta por ARP (`-PR`) |
| **arp-scan** | 1.10.x upstream; 1.9.7 no Ubuntu 22.04 | varredura ARP |
| **Scapy** | 2.6.x upstream; 2.4.4 no Ubuntu 22.04 | ARP programável |

A estabilidade do próprio protocolo se reflete nas ferramentas: elas ganham correções de
segurança e formatos de saída (JSON), não novas semânticas de ARP.

---

## 5. Debates e fronteiras abertas

- **Camada 2 grande vs. roteamento até a folha.** O debate de arquitetura de data center:
  esticar VLANs/EVPN (mobilidade de VM fácil, mas broadcast a controlar) versus rotear até o
  host (L3 puro, sem ARP entre racks, mas mobilidade mais complexa). Cilium/Calico empurram para
  L3; EVPN mantém L2 estendida viável. Sem vencedor único em 2026.
- **A migração SHA-... não é aqui** — mas vale notar que, ao contrário de assinaturas
  (commits, TLS), **não há urgência pós-quântica no ARP**: ele não usa criptografia alguma. A
  segurança dele é um problema de arquitetura, não de algoritmo.
- **Fim do IPv4?** Enquanto o IPv4 dominar (e ele domina em LANs corporativas em 2026), o ARP
  fica. A previsão realista: o ARP sobreviverá a esta década tranquilamente.

---

## 6. O que esperar

Opinião fundamentada do autor (não é consenso):

1. **O ARP no fio não vai mudar** — compatibilidade é destino.
2. **A supressão de broadcast vira padrão** também em redes de campus médias, não só data
   centers, à medida que switches com EVPN/controle central barateiam.
3. **eBPF absorve a resolução de vizinhos** em ambientes de contêiner, tornando `gc_thresh` uma
   preocupação de legado.
4. **A insegurança de camada 2 persiste** onde não há switch gerenciado — ou seja, na maioria
   das redes pequenas. Cifra fim-a-fim continua sendo a única defesa universal e é onde investir.

---

## Autoteste

1. O que significa "o ARP está sendo suprimido, não substituído"? Dê o mecanismo em data centers.
2. Como o EVPN elimina o broadcast de ARP, e qual requisito de gateway ele impõe?
3. Que papel o eBPF/Cilium tem na resolução de vizinhos, e o que ele contorna?
4. Por que não há urgência pós-quântica no ARP, ao contrário de assinaturas digitais?
5. Por que o ARP spoofing ainda funciona em 2026 apesar de a defesa existir há ~20 anos?
6. Qual a versão de referência do `ip neigh` (iproute2) e do Wireshark em ago/2026?
7. Qual é, na sua leitura do capítulo, a única defesa de camada 2 verdadeiramente universal?

---

**Fontes (pesquisadas na web em 14/08/2026):** documentação de ARP suppression EVPN/VXLAN
(Cisco, Arista, Dell, Aruba); Debian package tracker (iproute2 7.1.0); notas do Wireshark 4.6.8;
changelog do nmap 7.991 (05/08/2026); documentação Cilium/eBPF; docs Cisco DAI. Ver
[95-referencias](95-referencias.md).

**Próximo:** [70-pratica.md](70-pratica.md)
