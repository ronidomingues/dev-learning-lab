# 70 · Prática — 12 laboratórios progressivos

> **Nível:** iniciante → avançado
> **Data:** 14/08/2026
> Cada lab: **objetivo → passos → verificação → o que você aprendeu**. Os de ataque (9–11) só no
> laboratório isolado do [03](03-instalacao.md) §9. Onde marcado *(root)* ou *(lab)*, respeite.

---

## Lab 1 — Ler e entender a sua tabela *(sem root)*

**Objetivo:** decodificar cada campo. **Passos:**
```bash
ip neigh show
ip -s -d neigh show $(ip route | grep -oP 'default via \K\S+')
```
**Verificação:** você consegue explicar IP, `lladdr`, estado e o `used a/b/c` de uma linha.
**Aprendeu:** a leitura básica ([04](04-como-comecar.md) §2).

---

## Lab 2 — Retrato por fabricante *(sem root)*

**Objetivo:** deduzir o que existe na rede sem escanear. **Passos:** rode o
[07-projeto-modelo](07-projeto-modelo/):
```bash
python3 07-projeto-modelo/arpinspect.py
```
**Verificação:** a saída lista fabricantes e aponta o gateway. **Aprendeu:** OUI, inventário
passivo ([01](01-introducao-leigo.md) §4).

---

## Lab 3 — A máquina de estados ao vivo *(sem root)*

**Objetivo:** ver `STALE→DELAY→REACHABLE→STALE`. **Passos:** o experimento do
[04](04-como-comecar.md) §6 (escolha um IP `STALE`, `ping -c1`, observe a cada segundo).
**Verificação:** você mediu ~5 s em `DELAY` e ~15–45 s em `REACHABLE`. **Aprendeu:** NUD
([14](14-a-tabela-por-dentro.md)).

---

## Lab 4 — INCOMPLETE → FAILED *(sem root)*

**Objetivo:** ver a resolução falhar. **Passos:** escolha um IP livre da sua sub-rede
(confirme que não responde), `ping -c1 -W1 &`, observe:
```bash
for i in $(seq 0 6); do printf "t=%02d %s\n" "$i" "$(ip neigh show <ip-livre>)"; sleep 1; done
```
**Verificação:** viu 3× `INCOMPLETE` (1/s) depois `FAILED`. **Aprendeu:** `mcast_solicit`,
por que o fracasso é guardado ([13](13-o-ciclo-de-resolucao.md) §4).

---

## Lab 5 — Ler os parâmetros do cache *(sem root)*

**Objetivo:** ligar os tempos observados aos sysctls. **Passos:**
```bash
sysctl net.ipv4.neigh.$(ip route|grep -oP 'dev \K\S+'|head -1).{base_reachable_time_ms,delay_first_probe_time,mcast_solicit,gc_stale_time}
ip ntable show dev $(ip route|grep -oP 'dev \K\S+'|head -1) | head
```
**Verificação:** os números batem com o que você mediu no Lab 3/4. **Aprendeu:** de onde vêm os
tempos ([14](14-a-tabela-por-dentro.md) §3).

---

## Lab 6 — Monitor em tempo real *(sem root)*

**Objetivo:** capturar cada transição. **Passos:**
```bash
ip monitor neigh &
ping -c1 <um-vizinho>
# observe as linhas DELAY/REACHABLE/STALE aparecendo
kill %1
```
**Verificação:** você viu as mudanças no instante em que ocorreram. **Aprendeu:** a ferramenta
de depuração do [05](05-manual-de-uso.md) §11.

---

## Lab 7 — Dois "hosts" com namespaces *(root, zero instalação)*

**Objetivo:** ver um ciclo ARP completo entre dois nós que você criou. **Passos:** o roteiro de
namespaces do [03](03-instalacao.md) §9.3. Depois:
```bash
sudo ip netns exec h1 ip neigh show      # veja h2 aprendido
```
**Verificação:** a tabela de `h1` tem `10.0.0.2` com o MAC de `veth2`. **Aprendeu:** ARP num
segmento controlado, sem VM.

---

## Lab 8 — Laboratório em VMs *(lab, VirtualBox)*

**Objetivo:** montar a base dos labs de ataque. **Passos:** 3 VMs em rede interna `arplab`
([03](03-instalacao.md) §9.1), IPs `192.168.99.10/.11/.12`. `ping` entre elas; `arp-scan
--localnet` de uma. **Verificação:** cada VM enxerga as outras duas por ARP. **Aprendeu:**
isolamento correto para experimentar com segurança.

---

## Lab 9 — Capturar o handshake ARP *(root ou lab)*

**Objetivo:** ver request e reply no fio. **Passos:** o [06](06-exemplos.md) exemplo 9
(`tcpdump -e -n arp` + `ping`). Abra também no Wireshark com filtro `arp`. **Verificação:** você
identifica `who-has`/`tell`/`is-at` e a assimetria broadcast/unicast. **Aprendeu:** a
[anatomia](12-anatomia-do-pacote.md) na prática.

---

## Lab 10 — Construir ARP com Scapy *(root, Scapy)*

**Objetivo:** montar um request campo a campo e reimplementar o `arping`. **Passos:** o
[06](06-exemplos.md) exemplo 11 e a seção 5 do [12](12-anatomia-do-pacote.md). **Verificação:**
seu script imprime o MAC do alvo; `bytes(pkt).hex()` bate com a decodificação manual.
**Aprendeu:** o pacote deixou de ser abstrato.

---

## Lab 11 — Observar (e defender-se de) spoofing *(SOMENTE lab isolado)*

> ⚠️ Só nas VMs do Lab 8. Nunca em rede alheia ([18](18-seguranca.md) aviso legal).

**Objetivo:** ver o cache ser envenenado e a defesa funcionar. **Passos:**
1. na VM "vítima", `ip monitor neigh &` e anote o MAC do gateway virtual;
2. na VM "atacante", use `arpspoof`/`ettercap`/Scapy para anunciar o IP do gateway com o MAC do
   atacante (payload não reproduzido aqui — está na doc das ferramentas);
3. na vítima, veja o MAC do gateway **mudar** no monitor;
4. **defenda:** fixe o gateway como `PERMANENT` ([18](18-seguranca.md) §5) e repita — o cache
   não muda mais.

**Verificação:** com `PERMANENT`, o envenenamento não altera a entrada. **Aprendeu:** a mecânica
do ataque e a eficácia (e o limite) da defesa de host.

---

## Lab 12 — Auditoria em CI *(sem root)*

**Objetivo:** transformar análise de rede em porta de qualidade. **Passos:** o
[06](06-exemplos.md) exemplo 13:
```bash
ip neigh show > /tmp/cap.txt
python3 07-projeto-modelo/arpinspect.py --file /tmp/cap.txt --check; echo "exit=$?"
python3 07-projeto-modelo/arpinspect.py --file 07-projeto-modelo/exemplo-spoofing.txt --check; echo "exit=$?"
```
**Verificação:** a rede sã sai `0`; o arquivo de spoofing sai `1`. **Aprendeu:** separar ruído
`[info]` de anomalia acionável e refletir no código de saída.

---

## Desafios (sem solução aqui)

1. Escreva um script que compara a tabela ARP atual com uma linha de base salva e alerta em toda
   mudança de par IP↔MAC (um mini-`arpwatch`). Dica: `ip -j neigh` + `diff`.
2. Meça, com `tcpdump`, quantos ARP request/s a sua rede gera em 5 min. Estime a carga de
   broadcast de uma `/16` a partir do seu `/N` usando a fórmula N² do [60](60-teoria-avancada.md).
3. Configure `arp_ignore=1`/`arp_announce=2` numa VM multi-homed e comprove que o "ARP flux"
   sumiu ([16](16-arp-em-cada-sistema.md) §1).
4. No lab, case os timers de ARP e MAC para eliminar *unicast flooding* e comprove com `tcpdump`
   nas portas ([17](17-arp-em-redes-reais.md) §4).

---

**Fontes:** execuções e roteiros desta máquina, 14/08/2026; documentação das ferramentas citadas.

**Próximo:** [75-armadilhas.md](75-armadilhas.md)
