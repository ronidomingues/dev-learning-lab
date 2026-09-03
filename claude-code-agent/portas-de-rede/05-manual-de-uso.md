# 05 · Manual de uso — referência por tarefa

**Nível:** iniciante a avançado · **Última atualização:** 14/08/2026
**Organizado por tarefa, não por ordem alfabética.** Procure o que você quer *fazer*.
Comandos verificados em `iproute2 5.15.0`, `lsof 4.93.2`, `nmap 7.80`, `netcat-openbsd 1.218`,
Ubuntu 22.04.5, em 14/08/2026. Os comandos de macOS e Windows vêm da documentação oficial
e **não foram executados** aqui.

---

## Índice de tarefas

| Quero… | Seção |
|---|---|
| Listar o que minha máquina abriu | [1](#1-listar-portas-abertas-na-própria-máquina) |
| Saber quem abriu a porta X | [2](#2-descobrir-o-dono-de-uma-porta) |
| Filtrar a lista sem `grep` | [3](#3-filtros-do-ss--a-parte-que-quase-ninguém-usa) |
| Ver conexões, não só quem escuta | [4](#4-ver-conexões-e-estados) |
| Testar se a porta de alguém responde | [5](#5-testar-uma-porta-de-fora) |
| Varrer um host inteiro | [6](#6-nmap--varredura) |
| Descobrir **qual serviço** está na porta | [7](#7-identificar-o-serviço-e-a-versão) |
| Abrir uma porta à mão para testar | [8](#8-abrir-e-conversar-com-portas-à-mão) |
| Ver os pacotes de verdade | [9](#9-ver-os-pacotes) |
| Fazer isso no macOS | [10](#10-macos) |
| Fazer isso no Windows | [11](#11-windows) |
| Ver e mexer no firewall | [12](#12-firewall-local) |
| Ajustar o comportamento de portas no kernel | [13](#13-sysctl--ajustes-de-kernel) |

---

## 1. Listar portas abertas na própria máquina

### `ss` — o padrão no Linux

```bash
ss -tulpn
```

| Flag | Faz |
|---|---|
| `-t` | TCP |
| `-u` | UDP |
| `-w` | RAW (ICMP etc. — sem porta, mas aparece) |
| `-x` | sockets UNIX (arquivo, não rede — muito usado por bancos e Docker) |
| `-l` | só quem escuta |
| `-a` | tudo (escutando + conectado) |
| `-p` | mostra processo (**precisa de root para ver os alheios**) |
| `-n` | numérico — não traduz porta nem IP |
| `-r` | o contrário: resolve nomes (lento; evite) |
| `-4` / `-6` | só IPv4 / só IPv6 |
| `-e` | detalhes estendidos: uid, inode, cgroup |
| `-i` | informação interna do TCP: RTT, cwnd, retransmissões |
| `-m` | uso de memória do socket |
| `-s` | resumo estatístico |
| `-o` | temporizadores (keepalive, retransmissão) |
| `-Z` | contexto SELinux |
| `-K` | **encerra** os sockets que casarem com o filtro (destrutivo, precisa root) |
| `--no-header` | omite o cabeçalho — útil em script |

**Combinações que valem decorar:**

```bash
ss -tulpn                     # o inventário. Use este 90% das vezes.
ss -tlnp                      # só TCP escutando (lista menor, mais legível)
ss -s                         # resumo: quantos sockets, por estado
ss -tunap                     # tudo, com processos
ss -tulpn | grep -v 127.0.0   # só o que é alcançável de fora  ← o mais útil de todos
```

Saída real de `ss -s` nesta máquina:

```
Total: 1522
TCP:   1570 (estab 51, closed 1486, orphaned 0, timewait 1485)

Transport Total     IP        IPv6
RAW	  1         0         1
UDP	  27        24        3
TCP	  84        77        7
INET	  112       101       11
```

Repare: **1485 sockets em TIME_WAIT**. Numa estação de trabalho isso é irrelevante. Num
servidor, esse número virando dezenas de milhares é o prenúncio de esgotamento de porta
efêmera — ver [`60-teoria-avancada.md`](60-teoria-avancada.md).

### `netstat` — legado, mas você vai encontrar

```bash
netstat -tulpn                # equivalente ao ss -tulpn (Linux)
netstat -an | grep LISTEN     # portátil, funciona em quase tudo
```

**Marcado como obsoleto.** O pacote `net-tools` não recebe desenvolvimento ativo há anos e
foi removido do conjunto padrão de várias distros. Motivo técnico real: o `netstat` lê e
reprocessa `/proc/net/tcp` **como texto** a cada execução, enquanto o `ss` usa a interface
netlink (binária) e consegue **filtrar dentro do kernel**. Num servidor com 100 mil
conexões, `netstat` leva dezenas de segundos e o `ss` leva menos de um.

Aprenda `ss`. Conheça `netstat` porque ele está em todo tutorial antigo e em todo servidor
antigo — e porque no macOS e no Windows ele ainda é o que existe.

### `lsof` — o mais portável

```bash
lsof -i -P -n                             # todos os sockets de rede
lsof -nP -iTCP -sTCP:LISTEN               # só TCP escutando
lsof -nP -iTCP:8080                       # tudo na porta 8080
lsof -nP -i @192.168.0.10                 # tudo falando com aquele IP
lsof -nP -iUDP                            # UDP
lsof -p 1234                              # tudo que o PID 1234 abriu (arquivos inclusive)
```

| Flag | Faz |
|---|---|
| `-i` | filtro de rede: `-i:80`, `-iTCP`, `-iTCP:80`, `-i@host` |
| `-n` | não resolve nomes de host |
| `-P` | não traduz números de porta |
| `-s` | filtro de estado: `-sTCP:LISTEN`, `-sTCP:ESTABLISHED` |
| `-p` | por PID |
| `-u` | por usuário (`-u^root` = tudo **menos** root) |
| `+c 0` | não trunca o nome do comando em 9 caracteres ← muito útil |

**Truque que resolve confusão real:** `lsof` corta o nome do processo em 9 caracteres por
padrão. Por isso você vê `MainThrea` em vez de `MainThread`, e nomes diferentes parecem
iguais. `lsof +c 0 -nP -iTCP -sTCP:LISTEN` mostra o nome inteiro.

### `fuser` — o mais curto

```bash
fuser -n tcp 8080          # quem usa a 8080/tcp → imprime o PID
fuser -v -n tcp 8080       # com usuário e comando
fuser -k -n tcp 8080       # MATA quem estiver usando. Cuidado.
```

---

## 2. Descobrir o dono de uma porta

O caso mais frequente do assunto: *"a porta 8080 está ocupada, por quem?"*

```bash
ss -tlnp | grep :8080                    # Linux, o mais direto
lsof -nP -iTCP:8080 -sTCP:LISTEN         # portátil
fuser -v -n tcp 8080                     # mais curto
```

```powershell
# Windows
Get-Process -Id (Get-NetTCPConnection -LocalPort 8080 -State Listen).OwningProcess
```

**Se o processo não aparece:**

| Sintoma | Causa | Solução |
|---|---|---|
| Coluna `Process` vazia | O dono é de outro usuário | `sudo ss -tlnp` |
| Nada, nem com `sudo` | O socket está em outro *network namespace* (container) | `sudo nsenter -t <pid> -n ss -tlnp`, ou `docker ps` + `docker exec` |
| Porta aparece no `nmap` mas não no `ss` | Redirecionamento no kernel, proxy ou NAT | `sudo iptables -t nat -S \| grep REDIRECT` |

---

## 3. Filtros do `ss` — a parte que quase ninguém usa

O `ss` tem uma linguagem de filtro própria, avaliada **dentro do kernel**. É muito mais
rápido e preciso que `| grep`, e quase ninguém aprende.

```bash
ss -tlnp 'sport = :3306'                        # porta de origem (a local, em LISTEN)
ss -tn 'dport = :443'                           # porta de destino
ss -tn 'dst 10.0.0.5'                           # por IP de destino
ss -tn 'src 192.168.1.0/24'                     # por faixa de origem
ss -tlnp 'sport >= :8000 and sport <= :9000'    # faixa de portas
ss -tan 'state established and ( dport = :443 or sport = :443 )'
ss -tn 'state time-wait'                        # só TIME_WAIT
ss -tn '( sport = :80 or sport = :443 ) and dst 10.0.0.0/8'
```

Saída real de `ss -tlnp 'sport = :3306'`:

```
State  Recv-Q Send-Q Local Address:Port Peer Address:Port Process
LISTEN 0      151        127.0.0.1:3306      0.0.0.0:*
```

**Estados aceitos:** `established`, `syn-sent`, `syn-recv`, `fin-wait-1`, `fin-wait-2`,
`time-wait`, `closed`, `close-wait`, `last-ack`, `listening`, `closing`.
Atalhos: `connected` (tudo menos listening e closed), `synchronized` (established e afins),
`bucket` (time-wait + syn-recv), `big` (o oposto de bucket).

**Por que isso importa:** num servidor com 200 mil sockets, `ss -tan | grep :443` copia
200 mil linhas para o espaço de usuário e joga fora 199 mil. `ss -tan 'sport = :443'`
filtra no kernel. A diferença é de ordem de grandeza.

---

## 4. Ver conexões e estados

```bash
ss -tan                                                    # todas as conexões TCP
ss -tan | awk 'NR>1{print $1}' | sort | uniq -c | sort -rn # histograma de estados
ss -tanp state established                                 # só as estabelecidas, com processo
ss -ti                                                     # com RTT, cwnd, retransmissões
ss -tm                                                     # com memória por socket
ss -to                                                     # com temporizadores
```

Saída real do histograma nesta máquina:

```
   1524 TIME-WAIT
     33 LISTEN
     29 ESTAB
     14 CLOSE-WAIT
```

**Como ler isso como diagnóstico** — é o valor real do comando:

| Estado dominante | Significa |
|---|---|
| `TIME-WAIT` alto | Muitas conexões curtas fechadas **por você**. Normal em cliente HTTP; em servidor, considere keep-alive. |
| `CLOSE-WAIT` alto e **crescente** | **Bug na sua aplicação.** O outro lado fechou e seu código não chamou `close()`. Vazamento de descritor. |
| `SYN-SENT` alto | Você tenta conectar e não recebe resposta. Firewall ou destino fora do ar. |
| `SYN-RECV` alto | Muita conexão meio-aberta chegando. Pode ser SYN flood. |
| `FIN-WAIT-2` alto | Você fechou, o outro lado não responde. Cliente sumindo sem encerrar. |

`ss -ti` mostra, por conexão, coisas que normalmente só aparecem em ferramenta paga:

```
cubic wscale:7,7 rto:201 rtt:0.216/0.083 mss:1448 cwnd:10 bytes_sent:135
bytes_acked:136 segs_out:9 retrans:0/0 send 536Mbps delivery_rate 51Mbps minrtt:0.215
```

`rtt` é o tempo de ida e volta medido; `retrans` são as retransmissões (se subir, há perda);
`cwnd` é a janela de congestionamento; `cubic` é o algoritmo de controle de congestionamento.

---

## 5. Testar uma porta de fora

### `nc` (netcat)

```bash
nc -zv 127.0.0.1 8080            # testa uma porta
nc -zv 127.0.0.1 20-25           # testa uma faixa
nc -zvu 127.0.0.1 53             # UDP (resultado pouco confiável — ver 14)
nc -zv -w 2 host 443             # com timeout de 2 s
```

⚠️ **Existem três `nc` incompatíveis.** Descubra o seu antes:

```bash
nc -h 2>&1 | head -1
```

| Variante | Como identificar | Peculiaridade |
|---|---|---|
| **OpenBSD** (Debian/Ubuntu, macOS) | `OpenBSD netcat` | `-z` funciona. Aceita faixa. Padrão. |
| **`ncat`** (Nmap, Fedora) | `Ncat: Version ...` | `-z` **não existe** — use `--send-only` ou `nmap`. Tem TLS (`--ssl`) e proxy. |
| **GNU netcat** | `GNU netcat` | Sintaxe diferente, raro hoje. |

### Sem instalar nada — bash puro

```bash
timeout 2 bash -c 'exec 3<>/dev/tcp/127.0.0.1/8080' && echo aberta || echo fechada
```
> O `/dev/tcp/HOST/PORTA` é um recurso **do bash**, não um arquivo real. Não existe em
> `sh`, `dash` ou `zsh`. Salva a vida em container mínimo sem `nc` nem `curl`.

### `curl` — para portas que falam HTTP

```bash
curl -sS -m 3 -o /dev/null -w '%{http_code} %{time_connect}s\n' http://host:8080/
curl -v telnet://host:23             # abre a conexão bruta e mostra o handshake
curl -sS --http3 https://host/        # força HTTP/3 → 443/UDP (curl compilado com suporte)
```

### `openssl` — para portas que falam TLS

```bash
openssl s_client -connect host:443 -servername host </dev/null 2>/dev/null | head -20
openssl s_client -connect host:443 -tls1_3 </dev/null
openssl s_client -starttls smtp -connect host:587 </dev/null   # STARTTLS
```
> Serve para responder "essa porta fala TLS?" sem depender do número dela. Um HTTPS na
> 8443 responde; um HTTP na 443 falha na primeira troca.

---

## 6. `nmap` — varredura

> ⚠️ **Só contra alvos seus ou com autorização escrita.** Ver [`02`](02-pre-requisitos.md).

### Tipos de varredura

| Flag | Nome | Precisa root? | O que faz | Quando usar |
|---|---|---|---|---|
| `-sT` | connect | **não** | `connect()` completo do SO | Sem privilégio; padrão nesse caso |
| `-sS` | SYN / "half-open" | sim | Manda SYN, recebe SYN-ACK, manda RST | **O padrão profissional.** Rápido e discreto |
| `-sU` | UDP | sim | Manda datagrama, espera ICMP | Lento e ambíguo — ver [`14`](14-udp-e-os-outros.md) |
| `-sn` | ping scan | não | Só descobre hosts vivos, não varre portas | Mapear a rede primeiro |
| `-sA` | ACK | sim | Descobre se há firewall com estado | Reconhecimento de filtro |
| `-sV` | versão | não | Conversa com o serviço e identifica | **O mais útil de todos** |
| `-O` | SO | sim | Adivinha o sistema pelo comportamento da pilha | Complementar |
| `-sC` | scripts padrão | não | Roda a NSE básica | Bom no reconhecimento inicial |

### Seleção de portas e alvos

```bash
nmap -p 22,80,443 alvo          # portas específicas
nmap -p 1-1024 alvo             # faixa
nmap -p- alvo                   # TODAS as 65535 (demorado)
nmap --top-ports 100 alvo       # as 100 mais comuns (padrão do nmap são 1000)
nmap -p U:53,T:80 alvo          # mistura UDP e TCP
nmap 192.168.0.0/24             # a sub-rede toda
nmap -iL alvos.txt              # lista de um arquivo
nmap --exclude 192.168.0.1 ...  # exclui alvos
```

### Ajuste de velocidade e discrição

```bash
nmap -T0 ... -T5                # T0 paranoico … T3 padrão … T5 insano
nmap --min-rate 1000 alvo       # pelo menos 1000 pacotes/s
nmap --max-retries 1 alvo       # não insiste — mais rápido, menos preciso
nmap -Pn alvo                   # não faz ping antes (obrigatório contra Windows)
nmap -n alvo                    # não resolve DNS (mais rápido)
```

**`-T5` não é "melhor".** Ele perde pacotes e reporta porta aberta como filtrada. Em rede
local, `-T4` é o ponto de equilíbrio. Contra a internet, `-T3` (o padrão) existe por um motivo.

### Saída

```bash
nmap -oN saida.txt alvo         # texto normal
nmap -oX saida.xml alvo         # XML (para ferramenta consumir)
nmap -oG saida.gnmap alvo       # "grepável" — uma linha por host
nmap -oA base alvo              # os três de uma vez
nmap --reason alvo              # POR QUE ele classificou assim ← muito educativo
nmap -v / -vv / -d              # verbosidade / depuração
```

**`--reason` merece destaque.** Ele mostra o pacote que motivou a conclusão:

```
PORT   STATE  SERVICE  REASON
22/tcp open   ssh      syn-ack ttl 64
23/tcp closed telnet   reset ttl 64
25/tcp filtered smtp   no-response
```

Isso transforma o `nmap` de oráculo em instrumento. Use sempre que a resposta te
surpreender.

### Exemplo real, executado nesta máquina

```
$ nmap -sT -Pn 127.0.0.1
Starting Nmap 7.80 ( https://nmap.org ) at 2026-08-14 12:11 -03
Nmap scan report for localhost (127.0.0.1)
Host is up (0.00013s latency).
Not shown: 975 closed ports
PORT      STATE SERVICE
23/tcp    open  telnet
25/tcp    open  smtp
53/tcp    open  domain
80/tcp    open  http
...
Nmap done: 1 IP address (1 host up) scanned in 0.09 seconds
```

⚠️ **A coluna `SERVICE` é um chute baseado no número da porta**, lido de
`/usr/share/nmap/nmap-services`. Ela **não** consultou o serviço. Para saber de verdade,
é preciso `-sV`. Confundir as duas é o erro nº 1 de leitura de saída de `nmap`.

---

## 7. Identificar o serviço e a versão

```bash
nmap -sV alvo                                   # sonda e identifica
nmap -sV --version-intensity 9 alvo             # mais sondas, mais lento, mais preciso
nmap -sV --version-light alvo                   # intensidade 2, rápido
nmap -A alvo                                    # -sV + -O + -sC + traceroute
```

Como funciona por dentro: o `nmap` mantém o arquivo `/usr/share/nmap/nmap-service-probes`
com milhares de sondas e expressões regulares. Ele envia uma sonda, casa a resposta contra
os padrões, e deduz produto e versão. É um trabalho de 25 anos de curadoria — e é
exatamente a lacuna deliberada do [projeto-modelo](07-projeto-modelo/README.md).

**À mão, sem nmap:**

```bash
timeout 2 nc host 22 | head -1            # SSH cospe o banner sozinho
printf 'GET / HTTP/1.0\r\n\r\n' | timeout 2 nc host 80 | head -12
timeout 2 nc host 3306 | head -c 60 | xxd  # MySQL: versão em texto no meio do binário
openssl s_client -connect host:443 </dev/null 2>/dev/null | openssl x509 -noout -subject -dates
```

Saídas reais desta máquina:

```
# porta 80
HTTP/1.1 200 OK
Server: Apache/2.4.52 (Ubuntu)

# porta 3306
8.0.46-0ubuntu0.22.04.3 ... caching_sha2_password
```

O MySQL entrega versão, distribuição **e** nível de patch antes de qualquer autenticação.
Isso é comportamento normal do protocolo, não falha de configuração — e é o motivo de
"banner" ser tratado como informação sensível em auditoria.

---

## 8. Abrir e conversar com portas à mão

### Abrir uma porta para testar

```bash
nc -l 9999                                   # servidor TCP bobo na 9999 (OpenBSD nc)
nc -lk 9999                                  # continua depois que o cliente sai
ncat -l 9999 --keep-open                     # equivalente no ncat
python3 -m http.server 8099 --bind 127.0.0.1 # servidor HTTP de verdade
socat TCP-LISTEN:9999,reuseaddr,fork -       # com socat
```

### Redirecionar e tunelar

```bash
# encaminha a 9000 local para a 80 de outra máquina
socat TCP-LISTEN:9000,reuseaddr,fork TCP:10.0.0.5:80

# expõe um socket UNIX como porta TCP (útil para depurar Docker/MySQL)
socat TCP-LISTEN:2375,reuseaddr,fork UNIX-CONNECT:/var/run/docker.sock

# túnel SSH: a porta 5432 daqui vira a 5432 do banco lá dentro
ssh -L 5432:localhost:5432 usuario@servidor

# túnel reverso: expõe a sua 3000 na 8080 do servidor
ssh -R 8080:localhost:3000 usuario@servidor
```

⚠️ O segundo exemplo (`docker.sock` como TCP) é **exatamente** como se cria acidentalmente
um acesso root remoto sem autenticação. Está aqui para você reconhecer o padrão em
auditoria, não para usar em servidor.

### Conversar com um serviço

```bash
nc host 25                                  # SMTP: digite EHLO teste
nc host 6379                                # Redis: digite PING → +PONG
printf 'GET / HTTP/1.1\r\nHost: x\r\n\r\n' | nc host 80
```

---

## 9. Ver os pacotes

```bash
sudo tcpdump -i any -nn 'tcp port 8080'                # tudo na 8080
sudo tcpdump -i any -nn 'tcp[tcpflags] & tcp-syn != 0' # só SYN (início de conexão)
sudo tcpdump -i any -nn 'udp port 53'                  # DNS
sudo tcpdump -i lo -nn -A 'port 8099'                  # loopback, com o conteúdo em ASCII
sudo tcpdump -i any -nn -w captura.pcap 'port 443'     # grava para abrir no Wireshark
```

| Flag | Faz |
|---|---|
| `-i any` | todas as interfaces (`-i lo` = só loopback) |
| `-nn` | não resolve nomes **nem portas** |
| `-A` | mostra o conteúdo em ASCII |
| `-X` | hexadecimal + ASCII |
| `-c 10` | para depois de 10 pacotes |
| `-w arq` | grava em pcap |
| `-r arq` | lê um pcap |
| `-s 0` | captura o pacote inteiro (padrão moderno já é isso) |

**Como isso ensina:** rode `sudo tcpdump -i lo -nn 'port 8099'` em um terminal e
`curl http://127.0.0.1:8099/` em outro. Você verá o handshake de três vias, os dados e o
fechamento. É o [`13-tcp-por-dentro.md`](13-tcp-por-dentro.md) acontecendo na sua frente.

---

## 10. macOS

**Não executado neste material.** Fonte: páginas de manual do macOS e documentação da Apple.

| Tarefa | Comando |
|---|---|
| Portas TCP escutando | `lsof -nP -iTCP -sTCP:LISTEN` |
| Portas UDP | `lsof -nP -iUDP` |
| Quem usa a porta 8080 | `lsof -nP -i:8080` |
| Tudo, estilo antigo | `netstat -an \| grep LISTEN` |
| Por processo, interativo | `nettop` |
| Firewall de pacotes | `sudo pfctl -sr` (regras) · `sudo pfctl -s state` |
| Firewall de aplicação | `/usr/libexec/ApplicationFirewall/socketfilterfw --listapps` |

⚠️ **`netstat -tulpn` não existe no macOS.** As flags do `netstat` do BSD são outras. `-p`
no BSD significa "protocolo", não "processo". Use `lsof`.

⚠️ **Portas 5000 e 7000** são usadas pelo AirPlay Receiver desde o macOS Monterey.

---

## 11. Windows

**Não executado neste material.** Fonte: documentação da Microsoft (ver `95-referencias.md`).

### PowerShell (preferir)

```powershell
Get-NetTCPConnection -State Listen
Get-NetUDPEndpoint                              # UDP é cmdlet SEPARADO
Get-NetTCPConnection -LocalPort 8080
Get-NetTCPConnection -State Established | Group-Object State
```

O comando completo, com nome do processo — **guarde este**:

```powershell
Get-NetTCPConnection -State Listen |
  Select-Object LocalAddress, LocalPort,
    @{N='Processo';E={(Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName}},
    OwningProcess |
  Sort-Object LocalPort | Format-Table -AutoSize
```

Testar uma porta remota:

```powershell
Test-NetConnection -ComputerName host -Port 443
tnc host -Port 443                              # abreviação
Test-NetConnection host -Port 443 -InformationLevel Detailed
```

### `netstat` do Windows

```powershell
netstat -ano | findstr LISTENING     # -a todas, -n numérico, -o PID
netstat -anob                        # -b mostra o executável (exige administrador, lento)
netstat -s                           # estatísticas por protocolo
```

### Reservas de porta — a causa oculta de "Address already in use" no Windows

```powershell
netsh interface ipv4 show excludedportrange protocol=tcp
```

O Windows **reserva faixas inteiras de portas** para Hyper-V, WSL, Docker Desktop e o
serviço WinNAT. Se o seu serviço não sobe na 50000-50059 e nada aparece no `netstat`, é
quase certamente isso. É um problema que não existe no Linux e que consome tardes inteiras
de quem não sabe do comando acima.

| Tarefa | Comando |
|---|---|
| Firewall: listar regras | `Get-NetFirewallRule -Enabled True \| Format-Table` |
| Firewall: abrir uma porta | `New-NetFirewallRule -DisplayName "app" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow` |
| Redirecionar porta (portproxy) | `netsh interface portproxy add v4tov4 listenport=8080 connectaddress=172.20.1.5 connectport=80` |

O `portproxy` é como se publica um serviço do WSL2 para a rede — é a ponte entre os dois
mundos mencionada no [`03`](03-instalacao.md).

---

## 12. Firewall local

### `nftables` (padrão moderno no Linux)

```bash
sudo nft list ruleset                       # tudo
sudo nft list table inet filter             # uma tabela
sudo nft list ruleset | grep -E 'dport|redirect|dnat'
```

### `iptables` (legado, ainda onipresente)

```bash
sudo iptables -L -n -v                      # filtro, com contadores
sudo iptables -t nat -S                     # ← o comando que revela REDIRECT/DNAT
sudo iptables -t nat -L -n -v
```

**`iptables -t nat -S` é o comando que resolve o mistério** de "o `nmap` vê uma porta que o
`ss` não vê". Se houver uma regra `REDIRECT` ou `DNAT`, ela aparece aqui.

### `ufw` (Ubuntu) e `firewalld` (RHEL)

```bash
sudo ufw status verbose
sudo ufw allow 8080/tcp
sudo ufw allow from 192.168.0.0/24 to any port 5432 proto tcp   # o jeito certo: com origem
sudo ufw delete allow 8080/tcp
```

```bash
sudo firewall-cmd --list-all
sudo firewall-cmd --add-port=8080/tcp --permanent && sudo firewall-cmd --reload
```

⚠️ **Docker fura o `ufw`.** O Docker escreve regras direto na tabela `nat` do iptables, em
cadeias que são avaliadas **antes** das do `ufw`. Um container publicado com `-p 8080:80`
fica acessível mesmo com `ufw deny 8080`. Isso não é bug do `ufw` nem do Docker: é a ordem
de avaliação do netfilter. Ver [`20-containers-nuvem-e-k8s.md`](20-containers-nuvem-e-k8s.md).

---

## 13. `sysctl` — ajustes de kernel

```bash
cat /proc/sys/net/ipv4/ip_local_port_range      # faixa efêmera. Aqui: 32768  60999
sysctl net.ipv4.ip_local_port_range
```

| Parâmetro | Padrão típico | Para que serve |
|---|---|---|
| `net.ipv4.ip_local_port_range` | `32768 60999` | Faixa de portas de origem. Amplie em servidor com muitas conexões de saída. |
| `net.ipv4.ip_unprivileged_port_start` | `1024` | Abaixo disto exige privilégio. Baixe para permitir bind em porta baixa sem root. |
| `net.ipv4.tcp_tw_reuse` | `2` | Reaproveita sockets em TIME_WAIT para conexões **de saída**. |
| `net.core.somaxconn` | `4096` | Teto do backlog de `listen()`. |
| `net.ipv4.tcp_max_syn_backlog` | varia | Fila de conexões meio-abertas. |
| `net.ipv4.tcp_fin_timeout` | `60` | Tempo em FIN_WAIT_2. |
| `net.ipv4.tcp_syncookies` | `1` | Defesa contra SYN flood. **Deixe ligado.** |

```bash
sudo sysctl -w net.ipv4.ip_local_port_range="10240 65535"   # até reiniciar
echo 'net.ipv4.ip_local_port_range = 10240 65535' | sudo tee /etc/sysctl.d/99-portas.conf
sudo sysctl --system                                        # aplica
```

⚠️ **`net.ipv4.tcp_tw_recycle` não existe mais.** Foi **removido** do kernel na versão 4.12
(2017) porque quebrava clientes atrás de NAT de forma silenciosa e intermitente. Tutoriais
que ainda mandam ativá-lo são de antes de 2017 — e são um bom teste de frescor do material
que você está lendo. Use `tcp_tw_reuse`, que é diferente e seguro.

---

## Tabela de equivalências entre sistemas

| Tarefa | Linux | macOS | Windows |
|---|---|---|---|
| Listar portas escutando | `ss -tulpn` | `lsof -nP -iTCP -sTCP:LISTEN` | `Get-NetTCPConnection -State Listen` |
| UDP | `ss -ulpn` | `lsof -nP -iUDP` | `Get-NetUDPEndpoint` |
| Quem usa a porta X | `ss -tlnp \| grep :X` | `lsof -nP -i:X` | `Get-NetTCPConnection -LocalPort X` |
| Testar porta remota | `nc -zv h p` | `nc -zv h p` | `Test-NetConnection h -Port p` |
| Ver pacotes | `tcpdump` | `tcpdump` | `pktmon` / Wireshark |
| Firewall | `nft` / `iptables` / `ufw` | `pfctl` | `Get-NetFirewallRule` |
| Estatísticas | `ss -s` | `netstat -s` | `netstat -s` |

---

## O que está obsoleto

| Obsoleto | Substituto | Por quê |
|---|---|---|
| `netstat` (Linux) | `ss` | `net-tools` sem manutenção; `ss` filtra no kernel |
| `ifconfig` | `ip addr` | Mesmo pacote abandonado |
| `route` | `ip route` | Idem |
| `iptables` | `nftables` | Sintaxe unificada, melhor desempenho. Transição longa: `iptables` ainda é onipresente |
| `net.ipv4.tcp_tw_recycle` | `tcp_tw_reuse` | **Removido do kernel em 4.12** — quebrava NAT |
| Telnet para testar porta | `nc -zv`, `Test-NetConnection` | O cliente telnet nem vem instalado |
| `nmap -sP` | `nmap -sn` | Renomeado na versão 5.x |

---

## Autoteste

1. Por que `ss -tan 'sport = :443'` é preferível a `ss -tan | grep :443` num servidor grande?
2. Você vê 40 000 sockets em `CLOSE-WAIT` e o número só cresce. Onde está o defeito — na
   rede, no outro lado, ou no seu código? Por quê?
3. `nmap` sem `-sV` reportou `3306/tcp open mysql`. Isso prova que há um MySQL ali? Explique.
4. Qual a diferença prática entre `nmap -sT` e `nmap -sS`? Quando você é obrigado a usar o primeiro?
5. No macOS, qual comando substitui `ss -tulpn` — e por que o `netstat` de lá não serve?
6. Um serviço no Windows não sobe na porta 50005 e o `netstat` não mostra ninguém usando.
   Qual comando revela a causa?
7. `ufw deny 8080` está ativo e mesmo assim o container publicado em 8080 responde. Por quê?
8. O que `--reason` acrescenta à saída do `nmap`, e por que isso muda a natureza da ferramenta?

---

*Próximo: [`06-exemplos.md`](06-exemplos.md) — 15 receitas completas.*
