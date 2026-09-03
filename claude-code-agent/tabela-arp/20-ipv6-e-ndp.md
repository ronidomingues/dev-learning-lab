# 20 · O sucessor — NDP, o "ARP" do IPv6

> **Nível:** avançado
> **Data:** 14/08/2026
> O IPv6 não tem ARP. Tem **NDP**. Entender o que mudou (e o que não mudou) fecha o assunto e
> mostra para onde a resolução de vizinhos evoluiu.

---

## 1. Por que o IPv6 abandonou o ARP

O NDP (*Neighbor Discovery Protocol*, [RFC 4861](https://www.rfc-editor.org/info/rfc4861)) roda
sobre **ICMPv6** e substitui o ARP por três motivos ([11](11-historia.md) §5):

1. **Multicast em vez de broadcast.** Em vez de incomodar todo o segmento, o NDP pergunta a um
   grupo multicast pequeno, derivado do endereço-alvo — só quem pode ser o dono processa.
2. **Integração.** O ARP resolvia só IP→MAC; o resto (achar roteador, achar prefixo,
   autoconfigurar endereço) estava espalhado por ICMP e DHCP. O NDP unifica tudo.
3. **Ganchos de segurança de fábrica** (SEND, RFC 3971) — mesmo que pouco usados.

---

## 2. As cinco mensagens do NDP

| Mensagem ICMPv6 | Tipo | Equivalente ARP | Para quê |
|---|---|---|---|
| **Neighbor Solicitation (NS)** | 135 | ARP request | "quem tem o IPv6 X?" (multicast) |
| **Neighbor Advertisement (NA)** | 136 | ARP reply | "X está no MAC Y" |
| **Router Solicitation (RS)** | 133 | — (novo) | "há roteadores aqui?" |
| **Router Advertisement (RA)** | 134 | — (novo) | roteador anuncia prefixo, MTU, gateway |
| **Redirect** | 137 | ICMP redirect | "use outro roteador para esse destino" |

O par **NS/NA** faz o trabalho do ARP. RS/RA fazem o que no IPv4 era DHCP + descoberta de
roteador — base da **autoconfiguração SLAAC** (o host monta o próprio endereço a partir do
prefixo do RA + seu identificador de interface).

---

## 3. O truque do multicast de nó solicitado

Em vez de broadcast, o NS vai para o **endereço multicast de nó solicitado** (*solicited-node
multicast*): `ff02::1:ffXX:XXXX`, onde `XX:XXXX` são os **24 bits baixos** do endereço-alvo.

Efeito: só hosts cujo endereço termina naqueles 24 bits estão inscritos nesse grupo e processam
a mensagem. Estatisticamente, quase sempre **um** host — em vez dos milhares que um broadcast
acordaria. É a correção direta do custo de broadcast do ARP.

Você viu essas entradas na tabela desta máquina ([14](14-a-tabela-por-dentro.md) §6):
```
ff02::1:ff14:7684 dev enp2s0 lladdr 33:33:ff:14:76:84 NOARP
```
`33:33:...` é o prefixo de MAC multicast do IPv6, e os últimos bytes vêm dos 24 bits baixos do
endereço — cálculo, sem resolução, por isso `NOARP`.

---

## 4. O que **não** mudou: a máquina de estados

O NDP definiu a máquina de estados NUD (`REACHABLE`/`STALE`/`DELAY`/`PROBE`/`INCOMPLETE`) —
e foi **essa** que o Linux retroimportou para o IPv4 ([14](14-a-tabela-por-dentro.md) §1). Ou
seja: o cache de vizinhos do IPv4 moderno é, na verdade, **o modelo do IPv6 aplicado ao ARP**.
Por isso `ip neigh` trata os dois com os mesmos estados e os mesmos comandos — **é uma tabela
só**, com dois resolvedores (`arp.c` e `ndisc.c`) plugados no mesmo `neighbour.c`.

```bash
ip -6 neigh show          # a "tabela ARP" do IPv6
ip neigh show             # as duas juntas
ndp -a                    # equivalente no macOS/BSD
```

---

## 5. Segurança: melhor no papel, igual na prática

- **SEND** (*SEcure Neighbor Discovery*, RFC 3971) adiciona endereços gerados
  criptograficamente (CGA) e assinaturas — em tese, mata o "NDP spoofing" (o equivalente do ARP
  spoofing). Na prática, **quase ninguém implementa**; a maioria das pilhas nem oferece.
- Resultado: o **NDP spoofing existe** e funciona de forma análoga ao ARP spoofing. A defesa
  também migra para o switch: **RA Guard** e **ND Inspection** (o análogo do DAI para IPv6).
- Um vetor novo do IPv6: **RA falso** (*rogue RA*) — um atacante anuncia um prefixo/gateway
  forjado e sequestra a configuração dos hosts. RA Guard no switch é a defesa.

Moral: o IPv6 teve a chance de nascer seguro na resolução de vizinhos, projetou a solução (SEND),
mas a adoção não veio — e a segurança de camada 2 continua sendo feita **em volta**, no switch,
igual ao IPv4. O padrão da [17](17-arp-em-redes-reais.md) §8 se repete.

---

## 6. Tabela comparativa ARP × NDP

| Aspecto | ARP (IPv4) | NDP (IPv6) |
|---|---|---|
| Transporte | quadro Ethernet próprio (`0x0806`) | ICMPv6 (dentro de IPv6) |
| Descoberta | **broadcast** | **multicast** de nó solicitado |
| Resolver vizinho | request/reply | NS/NA |
| Achar roteador | fora do ARP (ICMP RD, config) | **RS/RA** (integrado) |
| Autoconfig de endereço | não (precisa DHCP) | **SLAAC** (integrado) |
| Máquina de estados | NUD (importada do IPv6) | **NUD (nativa)** |
| Segurança nativa | nenhuma | SEND/CGA (quase não usado) |
| Defesa prática | DAI + DHCP snooping | ND Inspection + RA Guard |
| Comando Linux | `ip neigh` / `ip -4 neigh` | `ip -6 neigh` |

---

## 7. Vale aprender NDP hoje?

Sim, e cada vez mais: o IPv6 já é maioria do tráfego em várias operadoras móveis e cresce em data
centers. Mas o IPv4 (e o ARP) não vão embora tão cedo — convivência de décadas. A boa notícia:
**quem entendeu o ARP e a máquina de estados NUD já entendeu 80% do NDP** — o que resta é
"multicast em vez de broadcast" e as mensagens de roteador (RS/RA). Este capítulo é essa ponte.

---

## Autoteste

1. Cite três razões pelas quais o IPv6 trocou ARP por NDP.
2. Qual par de mensagens NDP faz o trabalho do ARP request/reply?
3. O que o NDP usa no lugar do broadcast, e por que isso reduz o incômodo na rede?
4. Que parte do NDP o IPv4 do Linux "pegou emprestado", e como isso aparece no `ip neigh`?
5. O NDP é imune a spoofing? Explique SEND e por que ele não resolveu na prática.
6. O que é um *rogue RA* e qual a defesa?
7. Por que "quem entendeu ARP já entendeu 80% do NDP"?

---

**Fontes:** RFC 4861 (NDP), 4862 (SLAAC), 3971 (SEND), 4443 (ICMPv6); entradas IPv6 reais desta
máquina (`ff02::...` `NOARP`); documentação RA Guard/ND Inspection. Consultado em 14/08/2026.

**Próximo:** [60-teoria-avancada.md](60-teoria-avancada.md)
