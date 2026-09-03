# 75 · Armadilhas, mitos e más práticas

> **Nível:** todos
> **Data:** 14/08/2026
> Erros clássicos, mitos que persistem e por que persistem. Se você leu o curso, vai reconhecer
> cada um — este arquivo é a lista para revisar antes de operar.

---

## Parte 1 — Armadilhas conceituais

**A1. Achar que o ARP resolve o IP do destino remoto.**
Ele resolve o **próximo salto**. Para destino fora da sub-rede, resolve o **gateway**. Procurar
o ARP de `8.8.8.8` na sua tabela é procurar o que nunca vai estar lá. ([13](13-o-ciclo-de-resolucao.md))

**A2. Confundir tabela ARP (host) com tabela MAC (switch).**
IP→MAC num host; MAC→porta num switch. Perguntas diferentes, equipamentos diferentes. Erro nº 1
em entrevista e em diagnóstico. ([17](17-arp-em-redes-reais.md) §1)

**A3. "`STALE` é ruim / causa lentidão."**
`STALE` é normal e **usável**: o pacote sai na hora. Nunca é causa de lentidão. ([14](14-a-tabela-por-dentro.md) §2)

**A4. "ARP `REACHABLE` significa que o serviço funciona."**
Significa só que a **placa** respondeu — camada 2. O SO, o serviço ou o firewall do outro lado
podem estar mortos. ARP bom é o primeiro degrau, não o último. ([19](19-diagnostico.md) §4)

**A5. Comparar "tempo de cache" entre sistemas ingenuamente.**
"Linux esquece em 30 s, Cisco em 4 h" compara coisas diferentes: `REACHABLE→STALE` (Linux) vs.
remoção total (Cisco). Não são o mesmo relógio. ([16](16-arp-em-cada-sistema.md) §5)

**A6. Achar que MAC é imutável e identifica o fabricante sempre.**
MAC é reconfigurável por software; dispositivos modernos usam MAC aleatório por privacidade (bit
`0x02`). Um MAC `02:...`/`06:...`/`0a:...`/`0e:...` não tem fabricante. ([16](16-arp-em-cada-sistema.md) §2)

---

## Parte 2 — Armadilhas operacionais

**O1. Configurar um IP estático sem checar se está em uso.**
Derruba quem já usava. Rode `arping -D` antes, sempre. ([06](06-exemplos.md) exemplo 5)

**O2. Deixar entradas `PERMANENT` de teste na tabela.**
Se o MAC real mudar, sua máquina insiste no MAC velho e "perde" o host, sem erro visível.
Documente e reveja toda entrada estática. ([04](04-como-comecar.md) §8)

**O3. Só aumentar `gc_thresh3` diante de `neighbor table overflow`.**
Trata o sintoma; a causa é domínio de broadcast grande demais. Aumente **e** planeje
resegmentar. ([14](14-a-tabela-por-dentro.md) §7, [60](60-teoria-avancada.md) §3)

**O4. Timers de ARP e MAC descasados.**
ARP (roteador) durar mais que a tabela MAC (switch) causa *unicast flooding* — lentidão e
vazamento. Case os timers. ([17](17-arp-em-redes-reais.md) §4)

**O5. "ARP flux" em servidor multi-homed.**
Com o default do Linux, um host com várias placas responde ARP por todos os IPs em todas elas e
confunde a rede. `arp_ignore=1` + `arp_announce=2`. ([16](16-arp-em-cada-sistema.md) §1)

**O6. Rodar `arp-scan`/`nmap` na rede corporativa sem avisar.**
Dispara IDS e, sem autorização, é o art. 154-A. Combine antes ou use o lab.
([03](03-instalacao.md) §10)

**O7. Rodar Wireshark como `root`.**
Superfície de ataque enorme (dissecadores têm CVEs às dúzias — a própria 4.6.8 corrige 31). Use
o grupo `wireshark`/`cap_net_raw`. ([03](03-instalacao.md) §7.2)

**O8. Estudar ARP em Wi-Fi de convidado com isolamento de cliente.**
A tabela fica com uma entrada só (o gateway). Não é bug; é o isolamento. Use outra rede ou o lab.
([17](17-arp-em-redes-reais.md) §3)

---

## Parte 3 — Mitos

**M1. "O ARP é seguro porque é local."**
Local é exatamente onde o spoofing acontece. "Local" ≠ "confiável" — pode haver um atacante no
mesmo segmento. ([18](18-seguranca.md))

**M2. "IPv6 resolveu a insegurança do ARP."**
O NDP tem SEND, mas quase ninguém o usa; NDP spoofing e rogue RA são reais. A defesa migrou para
o switch, igual ao IPv4. ([20](20-ipv6-e-ndp.md) §5)

**M3. "Basta uma entrada estática do gateway para estar protegido contra spoofing."**
Protege **um** host e **um** sentido. O atacante ainda envenena o gateway→você. Defesa completa
é DAI no switch e/ou cifra fim-a-fim. ([18](18-seguranca.md) §5)

**M4. "Dois IPs com o mesmo MAC é sempre ataque."**
Normal para roteador, proxy ARP, ou uma máquina com vários IPs. O **perigoso é o inverso**: um
IP com dois MACs. ([07-projeto-modelo](07-projeto-modelo/))

**M5. "O ARP vai ser substituído em breve."**
Previsto há 25 anos (IPv6). Enquanto o IPv4 dominar LANs, o ARP fica. Ele será suprimido em
redes grandes, não substituído nos hosts. ([65](65-estado-da-arte.md))

**M6. "`arp -a` mostra tudo."**
Só IPv4. `ip neigh` mostra IPv4 **e** IPv6. Endereços que "somem" entre um e outro costumam ser
IPv6. ([04](04-como-comecar.md) §7)

**M7. "Cache ARP vazio = ARP quebrado."**
ARP é sob demanda. Vazio só significa que a máquina ainda não falou com ninguém. ([04](04-como-comecar.md) §7)

**M8. "Precisa de root para tudo em ARP."**
**Ler** não precisa. Só **alterar**, **capturar** e **enviar** precisam. 60% do curso roda sem
`sudo`. ([03](03-instalacao.md) §7.2)

---

## Parte 4 — Por que os mitos persistem

- **O ARP "simplesmente funciona"**, então quase ninguém precisa entendê-lo — até o dia do
  incidente. A ignorância sobrevive porque raramente é testada.
- **A confusão ARP/MAC-table** é reforçada por documentação descuidada que usa "ARP" para
  qualquer coisa de camada 2.
- **A falsa sensação de segurança do "local"** vem de uma época em que a LAN era fisicamente
  confiável — premissa morta em redes com Wi-Fi, visitantes e dispositivos comprometidos.
- **"IPv6 conserta"** é otimismo de quem não viu a adoção real de SEND (perto de zero).

---

## Autoteste

1. Por que procurar o ARP de um IP remoto na sua tabela é um erro conceitual?
2. Um colega diz "está lento porque a entrada está STALE". Corrija-o.
3. Por que aumentar `gc_thresh3` não é a solução definitiva do overflow?
4. Desminta "uma entrada estática do gateway me protege totalmente de spoofing".
5. Dois IPs com o mesmo MAC: quando é normal e quando o padrão inverso é perigoso?
6. Por que "o ARP é seguro porque é local" é um mito, e de onde ele vem?
7. Quais operações de ARP **não** precisam de root?

---

**Fontes:** síntese dos capítulos deste curso; execuções e observações em 14/08/2026.

**Próximo:** [80-custos-e-licencas.md](80-custos-e-licencas.md)
