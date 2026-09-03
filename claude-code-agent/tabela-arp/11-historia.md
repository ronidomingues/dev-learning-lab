# 11 · História — por que o ARP existe, e por que quase não mudou

> **Nível:** intermediário
> **Data:** 14/08/2026

---

## 1. O problema, antes da solução (1973–1982)

A Ethernet nasceu no Xerox PARC entre 1973 e 1976 (Robert Metcalfe e David Boggs). Era um
**cabo coaxial compartilhado**: todas as estações ouviam tudo, e cada quadro trazia um endereço
de hardware de 48 bits para que cada placa filtrasse o que era seu. Endereço de hardware plano,
gravado de fábrica — o MAC.

Em paralelo, o TCP/IP amadurecia (o IPv4 como o conhecemos foi fixado na RFC 791, 1981). O IP
trazia endereços **lógicos, hierárquicos**, atribuídos por configuração.

Quando puseram IP para rodar sobre Ethernet, apareceu a lacuna: **uma máquina tinha o IP do
destino, mas o hardware só entendia MAC.** Faltava a tradução. Havia três saídas concebíveis:

1. **Tabela estática** em cada máquina, mapeando todo IP a todo MAC, mantida à mão. Não escala,
   não sobrevive a mudança de hardware.
2. **Codificar o MAC dentro do IP** (como fez o IPX da Novell, que embutia o MAC de 48 bits no
   endereço de nó). Amarra a camada 3 à 2 e desperdiça espaço de endereço.
3. **Resolver dinamicamente, por pergunta e resposta.** Foi a escolhida.

---

## 2. RFC 826 — David Plummer, novembro de 1982

O [RFC 826](https://www.rfc-editor.org/info/rfc826), "An Ethernet Address Resolution Protocol",
de **David C. Plummer**, tem ~10 páginas e definiu o ARP essencialmente como usamos hoje. Virou
**STD 37** (Padrão da Internet), status que pouquíssimos protocolos alcançam.

As decisões de projeto de Plummer, e por que ele as tomou:

- **Genérico, não amarrado a IP nem a Ethernet.** O pacote ARP tem campos para "tipo de
  hardware" e "tipo de protocolo" justamente para resolver *qualquer* endereço lógico sobre
  *qualquer* meio. Em 1982 isso era essencial — havia IP, CHAOS, DECnet. Hoje 99,99% do ARP é
  IPv4-sobre-Ethernet, mas a generalidade sobrou no formato (ver [12](12-anatomia-do-pacote.md)).
- **Sem servidor, sem estado global.** Cada host responde por si. Sem ponto único de falha, sem
  problema de bootstrap.
- **Aprender de graça.** Uma inovação sutil e poderosa da RFC 826: ao **receber** um request,
  você já pode anotar o par IP↔MAC de quem perguntou, mesmo que a pergunta não seja para você.
  A rede "se ensina" passivamente. (É também a origem de uma classe de ataques — [18](18-seguranca.md).)
- **Cache com envelhecimento.** A RFC já previa expirar entradas, embora deixasse os tempos em
  aberto.
- **Zero autenticação.** No contexto — um cabo num laboratório entre colegas — verificar
  identidade seria custo sem benefício. Essa ausência é a dívida técnica mais longeva da
  Internet: ainda pagamos por ela em 2026 (ARP spoofing).

---

## 3. Os primos que vieram junto

- **RARP** (RFC 903, 1984): o ARP ao contrário — "eu sei meu MAC, qual é meu IP?". Usado por
  estações sem disco para descobrir o próprio IP no boot. Morto: substituído por BOOTP e depois
  DHCP, que fazem muito mais. Ver [15](15-variacoes-do-protocolo.md) §4.
- **Proxy ARP** (RFC 1027, 1987): um roteador responde ARP por IPs que não são dele, para
  "colar" duas sub-redes como se fossem uma. Útil e perigoso; ver [15](15-variacoes-do-protocolo.md) §3.
- **Gratuitous ARP**: formalizado aos poucos (RFC 2002 no contexto de Mobile IP, depois RFC 5227).
  Anunciar-se sem ser perguntado. Base de detecção de IP duplicado e de failover de IP virtual.

---

## 4. As correções de segurança que chegaram tarde

O ARP funcionou tão bem que ficou 20 anos sem revisão. Quando a rede saiu do laboratório para o
mundo hostil, os remendos vieram — mas **por fora**, sem tocar no protocolo:

- **RFC 5227 (2008), *IPv4 Address Conflict Detection* (ACD)**: padronizou como usar ARP para
  detectar conflito de IP de forma robusta (o `arping -D`).
- **RFC 5494 (2009)**: organizou a alocação dos campos do ARP (limpeza de IANA).
- **Dynamic ARP Inspection (DAI)** e **DHCP Snooping**: defesas implementadas **no switch**, não
  no protocolo, porque mudar o ARP em todos os hosts do mundo é impossível. Ver
  [18-seguranca](18-seguranca.md).

Ponto que vale internalizar: **o ARP nunca foi consertado; foi cercado.** Toda defesa contra
ARP spoofing é uma camada externa (switch inteligente, monitor, entrada estática), porque o
protocolo em si é imutável por razões de compatibilidade — há bilhões de dispositivos que só
falam o ARP de 1982.

---

## 5. Por que o IPv6 abandonou o ARP

O IPv6 (RFC 8200 e antecessores, anos 1990–2000) **não tem ARP**. No lugar, usa **NDP**
(*Neighbor Discovery Protocol*, RFC 4861), que roda sobre ICMPv6 e usa **multicast** em vez de
broadcast. Motivos:

1. **Broadcast é caro**; multicast direcionado incomoda só quem interessa.
2. NDP integra numa coisa só o que no IPv4 estava espalhado por ARP + ICMP Router Discovery +
   configuração — descoberta de vizinho, de roteador, de prefixo, autoconfiguração (SLAAC).
3. NDP nasceu com ganchos de segurança (SEND, RFC 3971) — pouco usados na prática, mas presentes.

O NDP herdou do IPv4 a máquina de estados NUD (que o Linux depois **retroimportou** para o
IPv4 — por isso você vê `REACHABLE`/`STALE` no ARP hoje). Detalhes em
[20-ipv6-e-ndp](20-ipv6-e-ndp.md).

---

## 6. Linha do tempo

```
1973–76  Ethernet no Xerox PARC — endereço de hardware de 48 bits (MAC)
1981     RFC 791 — IPv4
1982     RFC 826 — ARP (Plummer). Vira STD 37. Praticamente inalterado desde então.
1984     RFC 903 — RARP (hoje morto)
1987     RFC 1027 — Proxy ARP
1998     Ethernet vira comutada (switches) por padrão — broadcast deixa de ser "grátis"
2002+    Mobile IP formaliza gratuitous ARP
2005     ferramentas de ARP spoofing populares (ettercap, dsniff) já maduras
2008     RFC 5227 — detecção de conflito de IP (ACD)
2007+    Dynamic ARP Inspection difundido em switches corporativos
2011     net-tools (arp/ifconfig) considerado obsoleto no Linux; iproute2 assume
2015+    EVPN/VXLAN traz "ARP suppression" — o controle central volta, em círculo
2021     último release do net-tools
2026     ARP segue idêntico ao de 1982 no fio; o ecossistema em volta é que mudou
```

---

## 7. A lição histórica

O ARP é um estudo de caso de **como decisões de projeto envelhecem**:

- o que era virtude em 1982 (broadcast grátis, sem infraestrutura, sem autenticação) virou
  passivo em 2026 (broadcast caro em redes grandes, e um vetor de ataque);
- mas a **compatibilidade** é uma força tão poderosa que o protocolo não pode ser trocado —
  só cercado. O IPv6 tentou substituí-lo há 25 anos e o ARP ainda domina, porque o IPv4 ainda
  domina;
- a inovação real acontece **em volta** do protocolo (switch inteligente, EVPN, nuvem), não
  nele. Esse é o padrão de quase toda infraestrutura madura da Internet.

> **Opinião do autor (não é consenso):** o ARP vai sobreviver ao IPv4, não o contrário — no
> sentido de que a *ideia* (resolver enlace por pergunta-resposta cacheada) é tão boa que o NDP
> a reimplementou em vez de abandoná-la. O que morre é o broadcast, não o cache de vizinhos.

---

## Autoteste

1. Que três saídas existiam para o problema "tenho o IP, preciso do MAC", e por que a
   pergunta-resposta venceu?
2. Por que o pacote ARP tem campos "tipo de hardware" e "tipo de protocolo" se hoje é quase
   sempre IPv4-sobre-Ethernet?
3. O que significa dizer que o ARP "nunca foi consertado, foi cercado"? Dê dois exemplos de
   cerca.
4. Por que a ausência de autenticação foi uma decisão razoável em 1982 e um problema em 2026?
5. Por que o IPv6 trocou broadcast por multicast no NDP?
6. Que evento de ~1998 mudou a economia do broadcast e por quê?
7. Por que é praticamente impossível "atualizar o ARP" para uma versão segura?

---

**Fontes:** RFC 826, 903, 1027, 5227, 5494, 4861; história da Ethernet (Metcalfe & Boggs, CACM
1976); ver [90-bibliografia](90-bibliografia.md) e [95-referencias](95-referencias.md).

**Próximo:** [12-anatomia-do-pacote.md](12-anatomia-do-pacote.md)
