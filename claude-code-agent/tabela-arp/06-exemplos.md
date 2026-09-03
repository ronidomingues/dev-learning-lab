# 06 · Exemplos — do trivial ao de produção

> **Nível:** iniciante → avançado
> **Data:** 14/08/2026
> Cada exemplo: **problema → solução → explicação**. Onde marcado *(executado)*, a saída é real
> desta máquina (Ubuntu 22.04.5, iproute2 5.15.0). Onde marcado *(lab)*, exige o laboratório do
> [03](03-instalacao.md) §9. Onde marcado *(root)*, exige privilégio.

---

## Exemplo 1 — Ver quem está vivo agora *(executado)*

**Problema:** listar só os vizinhos confirmados neste instante.

```bash
ip neigh show nud reachable
```
```
10.209.0.1   dev enp2s0 lladdr 6c:31:0e:44:44:04 REACHABLE
10.209.1.31  dev enp2s0 lladdr 00:50:56:ab:aa:0a REACHABLE
10.209.2.134 dev enp2s0 lladdr d0:94:66:88:88:08 REACHABLE
```
**Explicação:** `REACHABLE` significa confirmação nos últimos ~30 s. É a lista de "com quem eu
realmente estou falando agora", útil para separar tráfego ativo de entradas velhas.

---

## Exemplo 2 — Descobrir o MAC de um IP sem pingar *(executado)*

**Problema:** você precisa do MAC do gateway, mas não quer o ruído de um `ping`.

```bash
ip neigh get 10.209.0.1 dev enp2s0
```
```
10.209.0.1 dev enp2s0 lladdr 6c:31:0e:44:44:04 REACHABLE
```
**Explicação:** `get` força a resolução naquele momento e devolve o resultado. Funciona mesmo
contra hosts que ignoram ICMP — porque um host **tem** de responder ARP para existir na rede,
mas **não** é obrigado a responder `ping`.

---

## Exemplo 3 — Retrato da rede por fabricante *(executado)*

**Problema:** cheguei numa rede e quero saber que tipo de equipamento existe, sem escanear.

```bash
ip -j neigh show | python3 -c '
import json,sys,re,collections
oui={}
for l in open("/usr/share/nmap/nmap-mac-prefixes"):
    m=re.match(r"^([0-9A-Fa-f]{6})\s+(.+)",l)
    if m: oui[m.group(1).lower()]=m.group(2).strip()
c=collections.Counter()
for e in json.load(sys.stdin):
    mac=e.get("lladdr")
    if mac: c[oui.get(mac.replace(":","")[:6].lower(),"?")]+=1
for v,n in c.most_common(): print(f"{n:>3}x {v}")
'
```
```
  3x VMware
  1x Cisco Systems
  1x Ricoh Company
  1x Asustek Computer
  1x Dell
```
**Explicação:** três VMs num hipervisor VMware, um roteador Cisco, uma impressora Ricoh, um
desktop ASUS e uma estação Dell — deduzidos **passivamente**, sem enviar um pacote. É o
[07-projeto-modelo](07-projeto-modelo/) em uma linha.

---

## Exemplo 4 — Ver a máquina de estados ao vivo *(executado)*

**Problema:** entender *quando* o kernel reverifica um vizinho.

```bash
ip monitor neigh &          # imprime cada mudança em tempo real
ping -c1 10.209.0.197 >/dev/null
```
Saída (resumida) do monitor:
```
10.209.0.197 dev enp2s0 lladdr 64:c6:d2:55:55:05 DELAY
10.209.0.197 dev enp2s0 lladdr 64:c6:d2:55:55:05 REACHABLE
...
10.209.0.197 dev enp2s0 lladdr 64:c6:d2:55:55:05 STALE
```
**Explicação:** `ip monitor neigh` é o osciloscópio da tabela. Deixe rodando enquanto reproduz
um problema; cada transição aparece no instante em que ocorre. Ferramenta de depuração
subutilizada.

---

## Exemplo 5 — Detectar IP duplicado antes de causar caos *(root)*

**Problema:** vou atribuir `10.209.0.50` a um servidor novo. Alguém já usa?

```bash
sudo arping -D -c 2 -I enp2s0 10.209.0.50
echo "exit=$?"
```
- `exit=0` → ninguém respondeu, o IP está livre.
- `exit=1` → **alguém respondeu**: o IP está em uso, e o `arping` mostra o MAC do ocupante.

**Explicação:** `-D` é *Duplicate Address Detection*. Rodar isto antes de configurar um IP
estático evita o clássico "configurei e derrubei o servidor de outra pessoa" — um dos incidentes
de rede mais comuns e mais evitáveis.

---

## Exemplo 6 — Limpar uma entrada envenenada/velha *(root)*

**Problema:** troquei a placa de rede de um servidor; minha máquina insiste no MAC antigo.

```bash
sudo ip neigh flush dev enp2s0        # limpa tudo desta interface
# ou, cirúrgico:
sudo ip neigh del 10.209.0.50 dev enp2s0
ping -c1 10.209.0.50                   # força re-resolução com o MAC novo
```
**Explicação:** o cache guarda o mapeamento antigo até envelhecer (minutos). `flush` força a
reconstrução imediata. É também o primeiro reflexo diante de suspeita de ARP spoofing — embora
não *resolva* o ataque (o atacante reenvenena), confirma o diagnóstico ao ver o MAC "errado"
reaparecer.

---

## Exemplo 7 — Proteger o gateway contra spoofing *(root)*

**Problema:** endurecer um servidor crítico contra ARP spoofing do gateway.

```bash
GW_IP=10.209.0.1
GW_MAC=$(ip neigh show $GW_IP | grep -oE '([0-9a-f]{2}:){5}[0-9a-f]{2}')
sudo ip neigh replace $GW_IP lladdr $GW_MAC dev enp2s0 nud permanent
ip neigh show $GW_IP
# 10.209.0.1 dev enp2s0 lladdr 6c:31:0e:44:44:04 PERMANENT
```
**Explicação:** uma entrada `PERMANENT` **ignora** qualquer ARP reply recebido — então um
atacante não consegue reescrever o MAC do gateway no seu cache. Custo: se o gateway trocar de
MAC de verdade (troca de hardware, failover de VRRP), você precisa atualizar à mão. É defesa de
host, complementar ao *Dynamic ARP Inspection* no switch ([18](18-seguranca.md)).

---

## Exemplo 8 — Mapear o segmento inteiro *(root, lab ou autorizado)*

**Problema:** inventário completo de quem responde na sub-rede.

```bash
sudo arp-scan --localnet --interface=enp2s0
```
```
Interface: enp2s0, ...
10.209.0.1    6c:31:0e:44:44:04   Cisco Systems, Inc
10.209.1.31   00:50:56:ab:aa:0a   VMware, Inc.
10.209.2.134  d0:94:66:88:88:08   Dell Inc.
...
N packets received by filter, ...
```
**Explicação:** `arp-scan` dispara ARP request para **cada** IP da sub-rede e monta a lista de
quem respondeu, já com fabricante. É a varredura mais rápida e confiável na LAN, porque ARP
**não pode** ser bloqueado por firewall de host (a máquina precisa dele para funcionar).
⚠️ Só na sua rede ou com autorização — em rede corporativa isto dispara IDS ([03](03-instalacao.md) §10).

---

## Exemplo 9 — Capturar e ler o handshake ARP *(root)*

**Problema:** ver, com os próprios olhos, o request e o reply.

```bash
sudo tcpdump -i enp2s0 -e -n arp &
ping -c1 10.209.0.197 >/dev/null
```
```
d0:94:66:99:99:99 > ff:ff:ff:ff:ff:ff, ARP, Request who-has 10.209.0.197 tell 10.209.2.168, length 46
64:c6:d2:55:55:05 > d0:94:66:99:99:99, ARP, Reply 10.209.0.197 is-at 64:c6:d2:55:55:05, length 46
```
**Explicação:** repare que o **request vai para `ff:ff:ff:ff:ff:ff`** (broadcast — todos
recebem) e o **reply volta em unicast** direto para quem perguntou. Esse é o protocolo inteiro,
em duas linhas. O `-e` mostra os MAC do quadro Ethernet; sem ele, você só vê a parte lógica.

---

## Exemplo 10 — Painel vivo da tabela *(executado)*

**Problema:** acompanhar a tabela mudando durante um teste.

```bash
watch -n1 'ip -br neigh show | sort'
```
**Explicação:** atualiza a cada segundo. Combine com um `ping` num terminal ao lado e veja as
entradas piscando entre `DELAY`, `REACHABLE` e `STALE`. Para produção, prefira o
`ip monitor neigh` do exemplo 4, que registra o histórico em vez de só a foto atual.

---

## Exemplo 11 — Montar um ARP request byte a byte com Scapy *(root, Scapy)*

**Problema:** entender o pacote construindo-o campo a campo.

```python
#!/usr/bin/env python3
from scapy.all import ARP, Ether, srp, get_if_hwaddr, conf

iface = conf.iface
meu_mac = get_if_hwaddr(iface)
alvo_ip = "10.209.0.1"

# quadro Ethernet: destino = broadcast, tipo = 0x0806 (ARP)
quadro = Ether(dst="ff:ff:ff:ff:ff:ff")
# corpo ARP: op=1 (request), origem = eu, destino = o IP que quero resolver
pergunta = ARP(op=1, hwsrc=meu_mac, pdst=alvo_ip)

resp, _ = srp(quadro / pergunta, timeout=2, iface=iface, verbose=0)
for enviado, recebido in resp:
    print(f"{recebido.psrc} está em {recebido.hwsrc}")   # psrc/hwsrc do REPLY
```
Saída esperada:
```
10.209.0.1 está em 6c:31:0e:44:44:04
```
**Explicação:** você acabou de reimplementar o `arping`. `op=1` é request, `op=2` seria reply.
`pdst` é o IP-alvo; `hwsrc`/`psrc` são o seu MAC/IP de origem. O reply chega com `psrc` = IP
resolvido e `hwsrc` = o MAC procurado. Confronte com a [anatomia do pacote](12-anatomia-do-pacote.md).

---

## Exemplo 12 — Anunciar-se após um failover (ARP gratuito) *(root)*

**Problema:** um IP virtual migrou para este servidor; preciso que a rede atualize o cache
**imediatamente**, sem esperar o envelhecimento.

```bash
sudo arping -U -c 3 -I enp2s0 10.209.0.100    # -U: unsolicited (gratuitous) ARP
```
**Explicação:** *gratuitous ARP* é um ARP que ninguém pediu, anunciando "o IP X agora está no
MAC Y". Todos os que tinham `10.209.0.100` em cache atualizam na hora. É exatamente o que
fazem soluções de alta disponibilidade (VRRP/keepalived, IPs flutuantes de nuvem) no instante
do failover, e o que faz o tráfego "virar" para o novo servidor em milissegundos em vez de
minutos. Detalhado em [15-variacoes-do-protocolo](15-variacoes-do-protocolo.md) §2.

---

## Exemplo 13 — Auditoria em CI: reprovar rede com anomalia *(executado)*

**Problema:** um pipeline que falha se a tabela de um host mostrar sinal de spoofing.

```bash
ip neigh show > /tmp/captura.txt
python3 07-projeto-modelo/arpinspect.py --file /tmp/captura.txt --check
echo "resultado do pipeline: $?"     # 0 = ok, 1 = anomalia real
```
Contra o arquivo de spoofing de exemplo do projeto:
```bash
python3 07-projeto-modelo/arpinspect.py --file 07-projeto-modelo/exemplo-spoofing.txt --check
# exit=1  (detectou IP com dois MACs E MAC servindo vários IPs)
```
**Explicação:** *(caso real de produção)* é assim que se leva análise de rede para dentro de
CI/CD ou de um agente de monitoramento: separa-se ruído informativo (`[info]`) de anomalia
acionável, e só a segunda muda o código de saída. Padrão de toda ferramenta de segurança
automatizada. *(executado — ver [07-projeto-modelo](07-projeto-modelo/))*

---

## Exemplo 14 — Dimensionar o cache num nó com muitos vizinhos *(root, produção)*

**Problema:** *(caso real de produção)* um nó de Kubernetes/roteador Linux loga
`neighbour: arp_cache: neighbor table overflow!` e perde conectividade intermitente.

```bash
# diagnóstico: quantas entradas contra o teto?
ip neigh show | wc -l
sysctl net.ipv4.neigh.default.gc_thresh3      # o teto rígido (padrão 1024)

# correção permanente em /etc/sysctl.d/99-neigh.conf:
cat <<'EOF' | sudo tee /etc/sysctl.d/99-neigh.conf
net.ipv4.neigh.default.gc_thresh1 = 4096
net.ipv4.neigh.default.gc_thresh2 = 8192
net.ipv4.neigh.default.gc_thresh3 = 16384
EOF
sudo sysctl --system
```
**Explicação:** quando o número de vizinhos passa de `gc_thresh3`, o kernel **recusa criar
entradas novas** e o host não consegue mais resolver MACs — a rede "cai" para destinos novos
enquanto os antigos funcionam. É a causa nº 1 de bugs bizarros de conectividade em clusters
grandes e roteadores Linux. A raiz teórica (broadcast e tabela crescem com o nº de hosts) está
em [60-teoria-avancada](60-teoria-avancada.md) §3. A regra de ouro: **domínio de camada 2
grande demais** — a solução definitiva é segmentar, não só aumentar o teto.

---

## Autoteste

1. Você precisa do MAC de um host que bloqueia `ping`. Como obtém sem ICMP? (exemplos 2, 5, 11)
2. Escreva o comando que lista só os vizinhos mortos. (cap. 05 §1)
3. Por que o request ARP vai para `ff:ff:ff:ff:ff:ff` mas o reply não? (exemplo 9)
4. Qual comando roda **antes** de atribuir um IP estático, e o que o código de saída informa?
5. Um IP virtual migrou de servidor. Que pacote faz a rede "virar" na hora, e qual comando o
   envia? (exemplo 12)
6. Um roteador Linux loga `neighbor table overflow`. Qual o diagnóstico e a correção? (exemplo 14)
7. No `arpinspect --check`, por que uma entrada `FAILED` **não** reprova o pipeline mas um IP
   com dois MACs reprova? (exemplo 13 e [07-projeto-modelo](07-projeto-modelo/))

---

**Fontes:** execuções reais nesta máquina, 14/08/2026; `man arping`, `man arp-scan`,
`man tcpdump`; documentação do Scapy (scapy.readthedocs.io).

**Próximo:** [07-projeto-modelo/README.md](07-projeto-modelo/README.md) ou o núcleo em
[10-fundamentos.md](10-fundamentos.md).
