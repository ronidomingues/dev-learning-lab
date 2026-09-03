# 16 · ARP em cada sistema — Linux, macOS, Windows, roteadores

> **Nível:** intermediário → avançado
> **Data:** 14/08/2026
> O protocolo no fio é o mesmo em todo lugar. O que muda é a **política** de cada sistema:
> quando responder, quando aprender, quanto tempo guardar, como você inspeciona.

---

## 1. Linux — o mais configurável

O Linux expõe o comportamento ARP por interface, via `sysctl net.ipv4.conf.<if>.*` e
`net.ipv4.neigh.<if>.*`. Os que importam:

| sysctl | Padrão | Efeito |
|---|---|---|
| `arp_ignore` | 0 | 0 = responde ARP para qualquer IP local em qualquer interface; 1 = só se o IP-alvo for da interface que recebeu; até 8 (mais restritivo) |
| `arp_announce` | 0 | qual IP de origem usar em requests: 0 = qualquer; 2 = o "melhor" da sub-rede do alvo |
| `arp_filter` | 0 | 1 = cada interface responde só pelos IPs que ela roteia (útil em multi-homing) |
| `arp_accept` | 0 | 1 = cria entrada ao receber gratuitous ARP de IP novo (mais exposto a spoofing) |
| `proxy_arp` | 0 | 1 = liga proxy ARP ([15](15-variacoes-do-protocolo.md) §3) |

O par **`arp_ignore=1` + `arp_announce=2`** é a receita clássica para servidores com múltiplas
interfaces ou com IP virtual (balanceadores DSR/LVS), porque o padrão do Linux tem o **"ARP
flux"**: com o default, um host multi-homed responde ARP por *todos* os seus IPs em *todas* as
interfaces, o que confunde a rede. Endurecer esses dois sysctls resolve.

Comportamento de aprendizado do Linux: por padrão ele **atualiza** uma entrada existente ao ver
tráfego, mas **não cria** entrada a partir de request de terceiros sem `arp_accept=1` — o que
limita (não elimina) a poluição de cache.

Inspeção e tempos: tudo no [14](14-a-tabela-por-dentro.md). Comandos no [05](05-manual-de-uso.md).

---

## 2. macOS / BSD

- Ferramenta: `arp` (BSD, não a do net-tools) e `ndp` para IPv6.
- Não expõe estados NUD tão explicitamente no `arp -a` (mostra o mapeamento e às vezes flags).
- Tempo de expiração padrão do cache: da ordem de **~20 minutos** para entradas em uso (mais
  longo que o "STALE aos 30 s" do Linux, porque a semântica é diferente — o BSD guarda mais e
  reverifica menos agressivamente).
- Controle fino via `sysctl net.link.ether.inet.*`:
  - `net.link.ether.inet.max_age` — idade máxima de uma entrada;
  - `net.link.ether.inet.arp_unicast_lim`, `host_down_time`, etc.
- Entrada estática: `sudo arp -s <ip> <mac>` (some ao reiniciar; para permanente, um daemon ou
  script de boot).

macOS moderno randomiza o MAC do Wi-Fi por rede (privacidade) — então o MAC que você vê de um
iPhone/Mac numa rede é **local-administrado** (bit `0x02`) e não revela fabricante. O
[07-projeto-modelo](07-projeto-modelo/) detecta e rotula isso.

---

## 3. Windows

- Ferramentas: `arp` (clássico) e o moderno **`Get-NetNeighbor`/`New-NetNeighbor`/
  `Remove-NetNeighbor`** (PowerShell). `netsh interface ip ... neighbors` ainda existe, legado.
- Windows **tem** máquina de estados equivalente ao NUD e a expõe no campo `State`
  (`Reachable`, `Stale`, `Delay`, `Probe`, `Incomplete`, `Permanent`, `Unreachable`).
- Desde o Windows Vista, o cache tem tempo de alcance base semelhante ao do NUD (~15–45 s de
  `Reachable`, também aleatorizado), muito mais próximo do Linux que do BSD clássico — porque a
  pilha de rede do Windows foi reescrita (a "Next Generation TCP/IP stack") adotando o modelo do
  RFC 4861.
- Configuração via `Set-NetIPInterface` (ex.: `-ReachableTime`, `-BaseReachableTime`) e políticas
  por interface. Entrada estática: `New-NetNeighbor -IPAddress .. -LinkLayerAddress .. -InterfaceAlias ..`.

Tradução de estados Windows↔Linux está na tabela do [05](05-manual-de-uso.md) §3.

---

## 4. Roteadores e switches (Cisco / genérico)

Aqui o vocabulário muda e é fácil se perder — atenção à distinção do
[17](17-arp-em-redes-reais.md).

**Roteador (camada 3) — tem tabela ARP**, porque termina IPs e precisa resolver MACs:
```
show ip arp                 ! a tabela ARP do roteador (IP → MAC → interface/VLAN → idade)
show ip arp 10.0.0.1
clear ip arp                ! limpa
arp 10.0.0.9 00aa.bbcc.ddee arpa   ! entrada estática (note o formato de MAC Cisco: 3 grupos)
```
- Idade padrão do cache ARP num roteador Cisco: **4 horas** (14400 s) — muito mais longa que a
  de um host, porque um roteador tem milhares de vizinhos estáveis e reverificar toda hora seria
  broadcast demais. Ajustável por interface: `arp timeout <segundos>`.
- **Descasamento clássico:** o cache ARP (4 h) costuma durar mais que a **tabela MAC do switch**
  (5 min, §5). Isso cria o "*unicast flooding*": o roteador sabe o MAC (ARP ainda válido) mas o
  switch esqueceu por qual porta ele está, então inunda o quadro por todas as portas. Sintoma de
  rede com timers mal casados. Ver [17](17-arp-em-redes-reais.md) §4.

**Switch (camada 2) — NÃO tem tabela ARP**, tem **tabela MAC/CAM** (MAC → porta):
```
show mac address-table      ! MAC → porta física → VLAN (isto NÃO é ARP)
```
Um switch só olha ARP se tiver funções L3 (SVI) ou de segurança (DAI — [18](18-seguranca.md)).

---

## 5. Tabela comparativa

| Aspecto | Linux | macOS/BSD | Windows | Roteador Cisco |
|---|---|---|---|---|
| Ver tabela | `ip neigh` | `arp -a -n` | `Get-NetNeighbor` | `show ip arp` |
| Estados NUD expostos | sim | parcial | sim | não (idade) |
| Vida em `REACHABLE` | ~15–45 s | ~20 min | ~15–45 s | 4 h (timeout ARP) |
| Estática | `ip neigh add ... permanent` | `arp -s` | `New-NetNeighbor` | `arp <ip> <mac> arpa` |
| Config de política | `sysctl net.ipv4.conf/neigh` | `sysctl net.link.ether` | `Set-NetIPInterface` | `arp timeout`, etc. |
| Aprende de gratuitous ARP | não, salvo `arp_accept=1` | configurável | sim, com validação | sim, com DAI opcional |

> **Cuidado com o "tempo de cache".** Comparar "30 s do Linux" com "4 h do Cisco" e concluir que
> "o Linux esquece rápido" é enganoso: são **coisas diferentes**. O "30 s" do Linux é o tempo em
> `REACHABLE` antes de virar `STALE` (e `STALE` ainda é usável e pode durar mais); o "4 h" do
> Cisco é o tempo até a entrada ser **removida**. Compare removível-com-removível: o Linux
> remove uma `STALE` ociosa após `gc_stale_time` (60 s) só se houver pressão de memória. Os
> números não são diretamente comparáveis.

---

## 6. Por que as políticas divergem (os porquês)

**P: Por que o roteador guarda ARP por 4 h e o host por dezenas de segundos?**
R: Economia de broadcast × frescor. Um roteador tem milhares de vizinhos estáveis; reverificar
cada um a cada 30 s geraria broadcast massivo sem ganho (os mapeamentos raramente mudam num
core de rede). Um host tem poucos vizinhos e se beneficia de detectar rápido uma mudança (VM
migrou, laptop trocou de rede). **Trade-off explícito**, não capricho.

**P: Por que o Linux não aprende de gratuitous ARP por padrão e o Windows sim?**
R: Escolha de postura de segurança × conveniência. Aprender de gratuitous ARP facilita failover
transparente (Windows prioriza "funcionar sozinho"), mas abre porta a envenenamento (Linux
prioriza não confiar em pacote não solicitado). Nenhuma está "certa"; refletem filosofias.

---

## Autoteste

1. Um servidor Linux com duas placas confunde a rede respondendo ARP por todos os IPs em todas
   as interfaces. Que dois sysctls corrigem isso e o que fazem?
2. Por que o cache ARP de um roteador Cisco dura 4 h e o de um host, segundos? É o mesmo "tempo"?
3. Um switch tem tabela ARP? Justifique. O que ele tem no lugar?
4. O que causa *unicast flooding* e como os timers de ARP e de MAC se relacionam com isso?
5. Você vê um MAC `02:...` no macOS de um colega numa rede Wi-Fi. O que o bit `0x02` indica?
6. Traduza `Get-NetNeighbor -State Stale` para o comando Linux equivalente.
7. Por que comparar "Linux esquece em 30 s" com "Cisco em 4 h" é uma comparação errada?

---

**Fontes:** `man 7 arp` (Linux); documentação Apple `arp(8)`/`ndp(8)`; Microsoft `Get-NetNeighbor`
e "Next Generation TCP/IP stack"; documentação Cisco IOS `show ip arp`/`arp timeout`. Sysctls
lidos localmente. Consultado em 14/08/2026. (Tempos de macOS/Windows/Cisco vêm da documentação,
não de execução nesta máquina — declarado.)

**Próximo:** [17-arp-em-redes-reais.md](17-arp-em-redes-reais.md)
