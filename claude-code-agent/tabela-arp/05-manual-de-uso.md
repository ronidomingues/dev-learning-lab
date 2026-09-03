# 05 · Manual de uso — referência consultável

> **Nível:** iniciante → intermediário
> **Data:** 14/08/2026
> Referência organizada **por tarefa**, não por ordem alfabética. Guarde este arquivo aberto
> enquanto trabalha. Comandos testados em Ubuntu 22.04.5 / iproute2 5.15.0, salvo indicação.

---

## Mapa rápido: qual comando para qual sistema

| Tarefa | Linux (moderno) | Linux/macOS (legado) | Windows (PowerShell) | Windows (clássico) |
|---|---|---|---|---|
| Listar tudo | `ip neigh show` | `arp -a -n` | `Get-NetNeighbor` | `arp -a` |
| Uma entrada | `ip neigh show <ip>` | `arp -n <ip>` | `Get-NetNeighbor <ip>` | `arp -a <ip>` |
| Adicionar estática | `ip neigh add ...` | `arp -s <ip> <mac>` | `New-NetNeighbor ...` | `arp -s <ip> <mac>` |
| Remover | `ip neigh del ...` | `arp -d <ip>` | `Remove-NetNeighbor ...` | `arp -d <ip>` |
| Limpar tudo | `ip neigh flush all` | — | `Remove-NetNeighbor` | `netsh int ip delete arpcache` |
| Enviar ARP | `arping <ip>` | `arping <ip>` | (via `Test-Connection`) | — |
| Varrer segmento | `arp-scan -l` | `nmap -sn <rede>` | `arp -a` após ping sweep | — |

> **Obsoleto, mas você vai encontrar:** o comando `arp` (do pacote `net-tools`) está
> **descontinuado** no Linux desde ~2011 e não é instalado por padrão em distros modernas.
> Funciona, mas não mostra estados NUD nem IPv6. Prefira `ip neigh`. O `net-tools` teve seu
> último lançamento em 2021 e não tem mais manutenção ativa. Em Windows e macOS, `arp` continua
> sendo padrão.

---

## 1. Ler a tabela (Linux, `ip neigh`)

```bash
ip neigh show                      # tudo (IPv4 + IPv6)
ip neigh show <ip>                 # uma entrada
ip neigh show dev enp2s0           # só de uma interface
ip neigh show nud reachable        # filtrar por estado (reachable|stale|delay|
                                   #   probe|incomplete|failed|permanent|noarp)
ip -s neigh show <ip>              # com estatísticas de tempo (used a/b/c, probes)
ip -s -d neigh show <ip>           # + detalhes (ref count)
ip -4 neigh show                   # só IPv4 (o "ARP" clássico)
ip -6 neigh show                   # só IPv6 (NDP)
ip -j neigh show                   # saída JSON (para scripts)
ip -br neigh show                  # formato breve
ip neigh get <ip> dev enp2s0       # resolver sob demanda e retornar
```

Atalho pouco conhecido: `ip n` é abreviação de `ip neigh`, e `ip n s` de `ip neigh show`.
O `iproute2` aceita qualquer prefixo não ambíguo.

## 2. Ler a tabela (macOS / BSD, `arp`)

```bash
arp -a                             # tudo, com resolução de nomes (lento)
arp -a -n                          # tudo, sem resolver nomes (rápido, literal)
arp -n <ip>                        # uma entrada
arp -a -i en0                      # só da interface en0
ndp -a                             # o equivalente IPv6 no macOS
```

## 3. Ler a tabela (Windows)

```powershell
Get-NetNeighbor                                    # tudo
Get-NetNeighbor -AddressFamily IPv4                # só IPv4
Get-NetNeighbor -State Reachable                   # filtrar por estado
Get-NetNeighbor -InterfaceAlias 'Ethernet'         # por interface
Get-NetNeighbor | Select IPAddress,LinkLayerAddress,State | Format-Table -AutoSize
```
```cmd
arp -a                             :: clássico, todas as interfaces
arp -a -N 10.209.2.168             :: entradas da interface com esse IP
```

Mapa de estados do Windows ↔ Linux: `Reachable`↔`REACHABLE`, `Stale`↔`STALE`,
`Delay`↔`DELAY`, `Probe`↔`PROBE`, `Incomplete`↔`INCOMPLETE`, `Unreachable`↔`FAILED`,
`Permanent`↔`PERMANENT`.

## 4. Adicionar entrada estática

Estática = `PERMANENT`, não envelhece, não é sobrescrita por ARP recebido. Usos: fixar o MAC
do gateway como defesa anti-spoofing ([18](18-seguranca.md)); dispositivos que não respondem
ARP; ambientes de teste.

```bash
# Linux
sudo ip neigh add 10.0.0.50 lladdr aa:bb:cc:dd:ee:ff dev enp2s0 nud permanent
# se já existe e você quer trocar:
sudo ip neigh replace 10.0.0.50 lladdr aa:bb:cc:dd:ee:ff dev enp2s0 nud permanent
```
```bash
# macOS/BSD
sudo arp -s 10.0.0.50 aa:bb:cc:dd:ee:ff
```
```powershell
# Windows (admin)
New-NetNeighbor -IPAddress 10.0.0.50 -LinkLayerAddress aa-bb-cc-dd-ee-ff -InterfaceAlias Ethernet
```
```cmd
:: Windows clássico (admin) — note os hífens no MAC
arp -s 10.0.0.50 aa-bb-cc-dd-ee-ff
```

> **Cuidado:** entrada estática que fica desatualizada "esconde" o host de você. Documente toda
> entrada estática e reveja quando trocar hardware.

## 5. Remover / limpar

```bash
# Linux — uma entrada
sudo ip neigh del 10.0.0.50 dev enp2s0
# Linux — limpar tudo (força re-resolução na próxima vez)
sudo ip neigh flush all
sudo ip neigh flush dev enp2s0            # só de uma interface
sudo ip neigh flush nud stale             # só as velhas
ip -statistics neigh flush all            # verboso: diz quantas apagou
```
```bash
# macOS/BSD
sudo arp -d 10.0.0.50                     # uma
sudo arp -a -d                            # todas (BSD)
```
```powershell
Remove-NetNeighbor -IPAddress 10.0.0.50 -Confirm:$false
```
```cmd
netsh interface ip delete arpcache        :: Windows, limpa tudo (admin)
```

Limpar o cache é seguro: a pilha reconstrói sob demanda. É a primeira coisa a tentar quando
suspeita de entrada envenenada ou de MAC trocado por troca de hardware.

## 6. Enviar ARP manualmente (`arping`)

```bash
sudo arping -c 3 10.209.0.1               # 3 requests ARP para o IP; mostra o MAC e o RTT
sudo arping -c 3 -I enp2s0 10.209.0.1     # forçar a interface
sudo arping -D -I enp2s0 10.209.0.50      # -D: detecção de IP duplicado (DAD)
sudo arping -U -I enp2s0 10.209.2.168     # -U: enviar ARP gratuito (anunciar-se)
sudo arping -A -I enp2s0 10.209.2.168     # -A: ARP gratuito tipo reply
```

`arping` é a única forma de testar alcance de camada 2 **sem** ICMP — funciona mesmo contra
hosts que bloqueiam `ping`. E `-D` é a maneira canônica de perguntar "esse IP já está em uso?"
antes de assumi-lo.

## 7. Varrer o segmento inteiro

```bash
sudo arp-scan --localnet                  # ARP em toda a sua sub-rede; lista IP+MAC+fabricante
sudo arp-scan --interface=enp2s0 10.209.0.0/20
sudo arp-scan -l -x                        # saída "plana", boa para script
sudo nmap -sn 10.209.0.0/24                # ping sweep; na LAN usa ARP automaticamente
sudo nmap -PR -sn 10.209.0.0/24            # força descoberta por ARP (-PR)
```
`arp-scan` mostra o fabricante de cada MAC consultando a base OUI do IEEE que ele embute.
Numa rede desconhecida, é o retrato mais rápido de "o que existe aqui".

## 8. Ajustar o comportamento do cache (sysctl, Linux)

Parâmetros do subsistema de vizinhos. Ver todos:
```bash
sysctl -a | grep 'net.ipv4.neigh.enp2s0'
```
Os que importam (com o valor padrão desta máquina):

| Parâmetro | Padrão | O que controla |
|---|---|---|
| `base_reachable_time_ms` | 30000 | quanto tempo uma entrada fica `REACHABLE` sem reconfirmar |
| `delay_first_probe_time` | 5 | segundos em `DELAY` antes de sondar |
| `gc_stale_time` | 60 | quando uma `STALE` sem uso vira candidata a remoção |
| `mcast_solicit` | 3 | quantos ARP request em broadcast antes de `FAILED` |
| `ucast_solicit` | 3 | quantas sondagens unicast em `PROBE` |
| `retrans_time_ms` | 1000 | intervalo entre tentativas |
| `gc_thresh1` | 128 | abaixo disso, o GC nem roda (entradas garantidas) |
| `gc_thresh2` | 512 | limite "flexível"; acima, GC agressivo após 5 s |
| `gc_thresh3` | 1024 | **teto rígido**: acima, entradas novas são recusadas |

Alterar (temporário, até reiniciar):
```bash
sudo sysctl -w net.ipv4.neigh.default.gc_thresh3=4096
```
Permanente — em `/etc/sysctl.d/99-arp.conf`:
```
net.ipv4.neigh.default.gc_thresh1 = 1024
net.ipv4.neigh.default.gc_thresh2 = 4096
net.ipv4.neigh.default.gc_thresh3 = 8192
```
depois `sudo sysctl --system`. Isso é o que se ajusta em roteadores Linux, nós de Kubernetes e
qualquer host com muitos vizinhos ([14](14-a-tabela-por-dentro.md) §7).

## 9. Controlar o ARP por interface

```bash
# ver flags de ARP da interface
ip link show enp2s0                        # procure NOARP se ARP estiver desligado
# desligar ARP numa interface (raro; enlaces ponto a ponto)
sudo ip link set enp2s0 arp off
sudo ip link set enp2s0 arp on
```
sysctls de política ARP (todos default 0; detalhados em [18](18-seguranca.md) e [16](16-arp-em-cada-sistema.md)):

| sysctl | Efeito quando = 1 |
|---|---|
| `arp_ignore` | seletividade em responder ARP para IPs de outras interfaces |
| `arp_announce` | qual IP de origem anunciar em requests |
| `arp_filter` | responder só pela interface "dona" da rota |
| `arp_accept` | criar entrada ao receber ARP gratuito de IP desconhecido |
| `proxy_arp` | responder ARP por IPs de outra sub-rede (proxy ARP — [15](15-variacoes-do-protocolo.md)) |

## 10. Capturar pacotes ARP

```bash
sudo tcpdump -i enp2s0 -n arp             # só ARP, sem resolver nomes
sudo tcpdump -i enp2s0 -e -n arp          # -e: mostra os MAC do quadro Ethernet
sudo tcpdump -i enp2s0 -n 'arp and host 10.209.0.1'
```
Leitura típica de uma linha do `tcpdump`:
```
ARP, Request who-has 10.209.0.1 tell 10.209.2.168, length 46
ARP, Reply 10.209.0.1 is-at 6c:31:0e:44:44:04, length 46
```
"who-has X tell Y" = request; "X is-at MAC" = reply. Wireshark mostra o mesmo em árvore,
campo a campo — filtro de exibição: `arp`.

---

## 11. Padrões que só quem usa há anos conhece

- **`ip neigh get` em vez de `ping`** para checar camada 2 sem depender de ICMP nem sujar
  estatística de ping.
- **`ip mon neigh`** (`ip monitor neigh`) transmite **em tempo real** toda mudança na tabela.
  Deixe rodando num terminal enquanto reproduz um problema — você vê cada transição de estado
  no instante em que acontece. É a ferramenta de depuração mais subutilizada do conjunto.
- **`watch -n1 'ip -br neigh'`** para um painel vivo da tabela.
- **`arping -D` antes de configurar IP estático** evita o clássico "configurei e derrubei outra
  máquina que já usava esse IP".
- **Filtrar `nud failed`** dá um mapa gratuito de tentativas frustradas — sinal precoce de
  varredura ou de host caído.
- **`ip neigh flush dev X` após trocar um switch/placa** poupa esperar o envelhecimento natural
  quando um MAC muda.
- No Windows, **`Get-NetNeighbor | Where State -eq 'Reachable'`** filtra melhor que qualquer
  parsing do `arp -a`.

---

## 12. Tabela de "eu quero... → use..."

| Eu quero... | Comando |
|---|---|
| ...saber o MAC de um IP vizinho | `ip neigh get <ip> dev <if>` |
| ...listar tudo que minha máquina conhece | `ip neigh show` |
| ...ver o que está morto na rede | `ip neigh show nud failed` |
| ...um mapa de quem existe no segmento | `sudo arp-scan --localnet` |
| ...saber se um IP já está em uso antes de usá-lo | `sudo arping -D -I <if> <ip>` |
| ...forçar re-resolução de tudo | `sudo ip neigh flush all` |
| ...proteger o MAC do gateway contra spoofing | `sudo ip neigh add <gw-ip> lladdr <gw-mac> dev <if> nud permanent` |
| ...ver mudanças na tabela ao vivo | `ip monitor neigh` |
| ...capturar o handshake ARP | `sudo tcpdump -i <if> -e -n arp` |
| ...suportar mais vizinhos (rede grande) | ajustar `gc_thresh*` (§8) |
| ...anunciar meu IP à rede (após failover) | `sudo arping -U -I <if> <meu-ip>` |

---

## Autoteste

1. Qual a diferença de saída entre `ip neigh show` e `arp -n` na mesma máquina Linux?
2. Você vai configurar `10.0.0.50` numa máquina nova. Que comando roda antes, e por quê?
3. Como você fixa o MAC do gateway de forma que ARP recebido não o sobrescreva?
4. Qual comando mostra, em tempo real, cada mudança de estado da tabela?
5. Um nó de Kubernetes loga `neighbour table overflow`. Quais três sysctls você ajusta?
6. Por que `arping` consegue testar um host que ignora `ping`?
7. No `tcpdump`, o que significa a linha `ARP, Request who-has 10.0.0.1 tell 10.0.0.9`?

---

**Fontes:** `man ip-neighbour(8)`, `man arp(8)`, `man arping(8)`, `man arp-scan(1)` locais;
documentação Microsoft `Get-NetNeighbor`/`New-NetNeighbor`; execuções em 14/08/2026.

**Próximo:** [06-exemplos.md](06-exemplos.md)
