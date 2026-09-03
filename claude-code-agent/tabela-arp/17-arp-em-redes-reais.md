# 17 · ARP em redes reais — VLAN, Wi-Fi, VRRP, Docker, Kubernetes, nuvem

> **Nível:** avançado
> **Data:** 14/08/2026
> Onde o ARP encontra a infraestrutura de verdade — e onde ele vira a causa-raiz de bugs que
> parecem bruxaria.

---

## 1. A confusão que precede tudo: ARP ≠ tabela MAC

Repetindo, porque é o erro nº 1:

| | Tabela ARP | Tabela MAC (CAM) |
|---|---|---|
| Onde vive | num **host/roteador** (camada 3) | num **switch** (camada 2) |
| Responde | "IP → qual MAC?" | "MAC → qual porta física?" |
| Preenchida por | ARP (pergunta-resposta) | *learning*: o switch observa o MAC **origem** de cada quadro |
| Comando | `ip neigh` / `show ip arp` | `show mac address-table` |
| Timeout típico | segundos (host) / horas (roteador) | ~5 min (300 s) |

Elas **cooperam**: o ARP descobre *qual MAC*; a tabela MAC do switch descobre *por qual porta*
entregar àquele MAC. Um pacote precisa das duas para chegar. Confundi-las é falhar entrevista e
diagnosticar errado.

---

## 2. VLAN — um domínio de broadcast por VLAN

Uma **VLAN** (802.1Q) divide um switch físico em vários **domínios de broadcast lógicos**. Como
o ARP é broadcast e o broadcast não cruza VLAN, **cada VLAN tem seu próprio "universo" de ARP**.

Consequências:

- dois hosts em VLANs diferentes **não** se resolvem por ARP, mesmo no mesmo switch — precisam de
  um roteador entre elas (inter-VLAN routing);
- segmentar em VLANs é a principal ferramenta para **encolher domínios de broadcast** e assim
  aliviar o custo de ARP em redes grandes ([60](60-teoria-avancada.md) §3);
- o quadro ganha 4 bytes de *tag* 802.1Q (EtherType `0x8100`), mas o pacote ARP dentro é idêntico.

Regra de projeto: **VLAN grande demais = broadcast demais.** A prática comum limita uma VLAN a
uma `/24` ou `/23` justamente para manter o broadcast (e a tabela de vizinhos) sob controle.

---

## 3. Wi-Fi — ARP sobre um meio que não é Ethernet

O Wi-Fi (802.11) **finge** ser Ethernet para as camadas de cima, mas por baixo:

- broadcast em Wi-Fi é **caro e frágil**: vai na taxa mais baixa (para todos ouvirem), não é
  confirmado (sem ACK de camada 2 para broadcast) e compete com todo o tráfego. Muito ARP =
  desperdício de espectro;
- por isso Access Points corporativos fazem **ARP/ND proxy e "broadcast suppression"**:
  interceptam o ARP request e respondem em nome do cliente (que aprenderam via DHCP snooping),
  evitando espalhar o broadcast por todo o BSS. É a mesma ideia do EVPN ([65](65-estado-da-arte.md));
- **isolamento de cliente** (*client isolation*, comum em Wi-Fi de visitante): o AP bloqueia
  tráfego station-a-station, então um cliente só resolve o **gateway** por ARP e nada mais — a
  tabela ARP fica com uma entrada só. É por isso que o [02](02-pre-requisitos.md) §4.3 avisa que
  Wi-Fi de convidado é ruim para estudar ARP.

---

## 4. O bug clássico: timers descasados e *unicast flooding*

*(caso real de produção)* Uma rede onde tudo "funciona, mas está lento e o switch está com CPU
alta". Causa: **o timeout de ARP do roteador (4 h) é maior que o timeout da tabela MAC do switch
(5 min).**

Sequência:
1. host silencioso por >5 min → o switch **esquece** por qual porta o MAC dele está;
2. o roteador ainda tem o ARP válido (4 h) → continua mandando quadros unicast para aquele MAC;
3. o switch, sem saber a porta, **inunda** o quadro por **todas** as portas da VLAN (*unicast
   flooding*);
4. tráfego que deveria ir por uma porta vai por todas → desperdício, e vazamento de dados para
   segmentos que não deviam vê-los.

Correção: **casar os timers** — deixar o timeout de ARP ≤ timeout da tabela MAC (ex.: ARP para
~4 min se o MAC é 5 min), de modo que o roteador reverifique (e o switch reaprenda) antes de
esquecer. É uma das afinações de rede mais citadas em certificações de nível associate/professional.

---

## 5. VRRP / alta disponibilidade — o MAC virtual

**VRRP** (e o HSRP da Cisco) dá aos hosts um gateway que nunca cai: dois roteadores compartilham
um **IP virtual** e um **MAC virtual** (`00:00:5e:00:01:XX` para VRRP). Os hosts resolvem o IP
virtual por ARP e recebem o MAC virtual; qual roteador físico o "veste" é invisível para eles.

No **failover**, o roteador que assume dispara **gratuitous ARP** (e atualiza a tabela MAC do
switch anunciando o MAC virtual pela sua porta) para que o tráfego vire na hora
([15](15-variacoes-do-protocolo.md) §2). Sem esse gratuitous ARP, os hosts continuariam mandando
para o MAC velho até o cache envelhecer — minutos de queda em vez de milissegundos.

Isso explica por que, na tabela de um host, o MAC do gateway pode ser `00:00:5e:00:01:...`
(virtual) em vez do MAC de fábrica de um roteador específico.

---

## 6. Docker — ARP na bridge virtual

Uma rede Docker `bridge` é um switch virtual (`docker0` ou uma bridge dedicada) num único host:

- containers na mesma bridge se resolvem por **ARP normal** entre si — é um domínio de broadcast
  de camada 2 emulado em software;
- você viu no [03](03-instalacao.md) §9.2: `ping h2` de dentro de `h1` gera ARP e preenche a
  tabela do container;
- **alterar** a tabela dentro do container exige `--cap-add=NET_ADMIN` (containers têm
  *capabilities* reduzidas por padrão — inclusive não podem abrir sockets raw sem isso);
- redes Docker `overlay` (multi-host, Swarm) e a maioria dos CNIs de Kubernetes **não** usam ARP
  entre nós: encapsulam (VXLAN) ou roteiam (L3), justamente para não depender de broadcast entre
  máquinas físicas.

---

## 7. Kubernetes e nuvem — onde o ARP é suprimido

- **Kubernetes**: cada nó pode ter **centenas a milhares** de IPs de pods. Se tudo fosse um
  domínio de broadcast de camada 2, a tabela de vizinhos estouraria (`gc_thresh3` — o bug do
  [06](06-exemplos.md) exemplo 14 e [14](14-a-tabela-por-dentro.md) §7). Por isso CNIs sérios
  (Calico, Cilium) preferem **roteamento L3** ou encapsulamento, e o ARP fica restrito ao
  enlace nó↔gateway. **Ajustar `gc_thresh1/2/3` nos nós é operação padrão** em clusters densos.
- **AWS VPC / Azure / GCP**: a "rede" é definida por software (SDN). O ARP que a sua VM vê é uma
  **ilusão** mantida pelo hipervisor: você manda um ARP request, e a plataforma responde com o
  MAC que ela quer (frequentemente o mesmo MAC para o gateway em todas as VMs). Não há broadcast
  físico de verdade cruzando o data center — seria insustentável. O gateway `.1` da sua subnet
  responde ARP, mas por trás é um sistema distribuído, não uma caixa.
- **IP flutuante / Elastic IP**: mover um IP entre VMs na nuvem dispara, nos bastidores, o
  equivalente a um gratuitous ARP (a plataforma reprograma suas tabelas), mesmo que você não veja
  o pacote.

---

## 8. O fio condutor

Em toda infraestrutura moderna, o padrão é o mesmo:

> **Quanto maior a rede, mais o broadcast do ARP é suprimido, interceptado ou substituído por
> uma camada de controle central** — AP fazendo proxy no Wi-Fi, switch fazendo DAI, EVPN fazendo
> ARP suppression, hipervisor respondendo no lugar da rede física.

É a decisão de projeto de 1982 (broadcast grátis, sem infraestrutura) sendo revertida onde o
broadcast deixou de ser grátis. O círculo que a [11](11-historia.md) §7 previu: o "servidor
central" que Plummer evitou volta, disfarçado de plano de controle. Detalhado em
[65-estado-da-arte](65-estado-da-arte.md).

---

## Autoteste

1. Distinga tabela ARP de tabela MAC: onde cada uma vive, o que responde, como é preenchida.
2. Por que dois hosts em VLANs diferentes não se resolvem por ARP mesmo no mesmo switch?
3. Explique o *unicast flooding* por timers descasados e como casá-los corrige.
4. Por que o MAC do seu gateway pode ser `00:00:5e:00:01:0a`? O que isso indica?
5. Por que broadcast (e portanto ARP) é especialmente caro em Wi-Fi?
6. Por que clusters Kubernetes densos precisam ajustar `gc_thresh`, e por que aumentar não é a
   cura definitiva?
7. Quando sua VM na AWS resolve o gateway por ARP, o que realmente responde?

---

**Fontes:** IEEE 802.1Q, 802.11; RFC 5798 (VRRPv3); documentação Docker networking, Calico/Cilium;
docs de rede AWS VPC/Azure; experiência de campo. Consultado em 14/08/2026.

**Próximo:** [18-seguranca.md](18-seguranca.md)
