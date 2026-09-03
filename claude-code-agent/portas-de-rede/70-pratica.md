# 70 · Prática — 14 laboratórios

**Nível:** iniciante a avançado · **Última atualização:** 14/08/2026

Todos os laboratórios rodam contra **`127.0.0.1`**. Nenhum exige rede externa. Os que
exigem `sudo` estão marcados 🔑 e trazem alternativa quando existe.

**Formato:** objetivo → passos → o que observar → gabarito comentado.
Faça antes de ler o gabarito. Ler o gabarito primeiro é como ler o final do livro.

---

## Lab 1 · Inventário da sua própria máquina

**Nível:** iniciante · **Tempo:** 20 min

**Objetivo:** produzir a lista de portas expostas da sua máquina e **explicar cada linha**.

```bash
ss -tulpn > /tmp/tudo.txt
ss -tulpn | grep -vE '127\.0\.0\.|\[::1\]' > /tmp/expostas.txt
wc -l /tmp/tudo.txt /tmp/expostas.txt
```

**Tarefa:** para **cada** linha de `/tmp/expostas.txt`, responda por escrito:
1. Que serviço é?
2. Quem precisa alcançá-lo?
3. Se você o desligasse hoje, o que quebraria?

**O que observar:** a quantidade de linhas que você **não** sabe explicar.

**Gabarito comentado.** Numa estação de trabalho típica você vai encontrar entre 5 e 40
sockets expostos. Os suspeitos habituais e o que fazer:

| Se aparecer | Provavelmente é | Ação |
|---|---|---|
| `0.0.0.0:631` | CUPS (impressão) | Desligar se não imprime pela rede |
| `0.0.0.0:445`, `:139`, `:137` | Samba | Desligar se não compartilha arquivos |
| `0.0.0.0:5353` | Avahi/mDNS | Normal em desktop; desligar em servidor |
| `0.0.0.0:3000/5173/8080` | Servidor de desenvolvimento | Trocar o bind para `127.0.0.1` |
| Porta alta em `0.0.0.0` | Quase sempre acidental | Investigar |

Nesta máquina de escrita, o resultado real foi **35 sockets expostos, 14 classificados como
críticos** — a maioria Samba e NetBIOS que ninguém sabia estarem ativos. É o resultado
típico, e é o ponto do laboratório.

---

## Lab 2 · Abrir, verificar, fechar

**Nível:** iniciante · **Tempo:** 15 min

```bash
# Terminal 1
python3 -m http.server 8099 --bind 127.0.0.1

# Terminal 2 — antes, durante e depois
ss -tlnp | grep 8099
nc -zv 127.0.0.1 8099
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8099/
curl -sS -m 3 http://$(hostname -I | awk '{print $1}'):8099/
# agora derrube o Terminal 1 (Ctrl+C) e repita tudo
```

**Perguntas:** por que o teste pelo IP externo falhou? Quanto tempo depois de matar o
processo a porta parou de responder?

**Gabarito.** O `--bind 127.0.0.1` restringe o socket ao loopback: pacotes que chegam por
outra interface não alcançam o socket. A saída real, medida:

```
curl: (7) Failed to connect to 10.209.2.168 port 8099 after 0 ms: Conexão recusada
```

Repare no `after 0 ms` — recusa instantânea, não bloqueio. E o `LISTEN` morre **junto com o
processo**, instantaneamente: não há atraso. O que pode persistir por 60 s é o `TIME_WAIT`
de conexões que existiram, não o socket de escuta. É o Lab 5.

---

## Lab 3 · Os três desfechos

**Nível:** iniciante · **Tempo:** 15 min

```bash
python3 -m http.server 8099 --bind 127.0.0.1 &
nc -zv 127.0.0.1 8099          # aberta
nc -zv 127.0.0.1 8098          # fechada
curl -sS -m 5 http://10.255.255.1:80/    # filtrada (IP inalcançável)
```

**O que observar: o tempo de cada um.**

**Gabarito.** Saídas reais:

```
Connection to 127.0.0.1 8099 port [tcp/*] succeeded!
nc: connect to 127.0.0.1 port 8098 (tcp) failed: Connection refused
curl: (28) Connection timed out after 5000 milliseconds
```

Aberta e fechada respondem em **microssegundos** (chega SYN-ACK ou RST). Filtrada custa o
**timeout inteiro** — 5 s aqui. Essa diferença de tempo é a assinatura de firewall, e é a
razão de varredura contra alvo protegido ser lenta por construção.

---

## Lab 4 · Ler o `/proc` à mão

**Nível:** intermediário · **Tempo:** 30 min

```bash
head -5 /proc/net/tcp
```

**Tarefa:** decodifique três linhas **à mão**, sem programa: IP local, porta, estado.
Depois confira com `ss -tlnp`.

**Gabarito.** Linha real desta máquina:

```
   3: 0100007F:0CEA 00000000:0000 0A ... 129 ... 12303
```

- `0100007F` → bytes `01 00 00 7F` → lido little-endian → `0x7F000001` → **127.0.0.1**
- `0CEA` → **3306** (MySQL)
- `0A` → **LISTEN**
- `129` → uid do usuário `mysql`

Confirmação: `ss -tlnp 'sport = :3306'` mostra `LISTEN 0 151 127.0.0.1:3306`. Bate.

**Bônus** — do `/proc/net/udp`: `3500007F:0035` → bytes `7F 00 00 35` → **127.0.0.53:53**.
É o `systemd-resolved`, e é a prova de que loopback não é só `127.0.0.1`.

---

## Lab 5 · Provocar e resolver o `TIME_WAIT`

**Nível:** intermediário · **Tempo:** 25 min

Use o script do exemplo 4 de [`06-exemplos.md`](06-exemplos.md).

**Tarefa:** responda com medição, não com teoria:
1. Quem ficou em `TIME_WAIT` — cliente ou servidor? Mude quem fecha primeiro e refaça.
2. Quanto tempo dura, medido com `watch`?
3. O `SO_REUSEADDR` permite o `bind`. Ele elimina o `TIME_WAIT`?

**Gabarito.** Saída real:

```
TIME-WAIT 0 0 127.0.0.1:33527 127.0.0.1:48654
sem SO_REUSEADDR: [Errno 98] Address already in use
com SO_REUSEADDR: bind+listen OK
```

1. Fica com **quem fecha primeiro**. Invertendo, o `TIME_WAIT` troca de lado.
2. **60 s no Linux**, fixo em `TCP_TIMEWAIT_LEN`. Não é configurável por `sysctl` —
   `tcp_fin_timeout` controla `FIN_WAIT_2`, não isto.
3. **Não.** O socket antigo continua em `TIME_WAIT`; `SO_REUSEADDR` só permite que um socket
   **novo** faça `bind` no mesmo endereço local. Confirme com `ss -tan state time-wait`.

---

## Lab 6 · Estourar o backlog

**Nível:** intermediário · **Tempo:** 25 min

Use o script do exemplo 5 de [`06-exemplos.md`](06-exemplos.md).

**Tarefa:** varie `listen(n)` para 0, 1, 5 e 128. Quantas conexões cada um aceita antes de
travar? Compare com `Send-Q` do `ss -tln`.

**Gabarito.** Com `listen(2)`, a saída real foi:

```
conexão 1: aceita   conexão 2: aceita   conexão 3: aceita
conexão 4: TimeoutError   conexão 5: TimeoutError   conexão 6: TimeoutError

LISTEN 3 2 127.0.0.1:46189
```

**`backlog + 1`** — o Linux aceita um a mais que o pedido. `Recv-Q 3` é a fila; `Send-Q 2` é
o backlog. As conexões excedentes **deram timeout, não recusa**: com a fila cheia, o kernel
descarta o SYN em silêncio, e o cliente retransmite achando que houve perda.

Teste também `listen(4096)` com `net.core.somaxconn = 128`: o `Send-Q` mostrará **128**.
O backlog efetivo é `min(backlog, somaxconn)`.

---

## Lab 7 · Confrontar as duas visões 🔑 (parcial)

**Nível:** intermediário · **Tempo:** 30 min

```bash
cd 07-projeto-modelo
python3 auditor.py comparar -p 1-10000
```

**Tarefa:** para cada divergência, explique a causa. Se houver "só a rede vê", investigue:

```bash
sudo iptables -t nat -S | grep -E 'REDIRECT|DNAT|TPROXY'
```

**Gabarito.** Saída real desta máquina:

```
concordam: 8    [80, 139, 445, 631, 3001, 3306, 5173, 9050]
só o kernel vê: 3    (53, 9789, 9879)
só a rede vê:   2    (2222, 3128)
```

- **53:** o `systemd-resolved` escuta em `127.0.0.53`, não em `127.0.0.1`.
- **2222 e 3128:** conexão completa sem processo escutando. Só há uma explicação —
  redirecionamento no kernel. Na máquina de escrita, o `nmap` chegou a reportar **25**
  portas assim; o padrão (só portas conhecidas conectam, portas aleatórias não) aponta para
  agente de segurança corporativo ou proxy de inspeção. Não foi possível confirmar sem
  `sudo`, e este material diz isso em vez de inventar.

---

## Lab 8 · Identificar serviço sem `nmap -sV`

**Nível:** intermediário · **Tempo:** 30 min

```bash
timeout 2 nc 127.0.0.1 22 | head -1
printf 'GET / HTTP/1.0\r\n\r\n' | timeout 2 nc 127.0.0.1 80 | head -8
timeout 2 nc 127.0.0.1 3306 | head -c 80 | xxd
openssl s_client -connect 127.0.0.1:443 </dev/null 2>&1 | head -12
```

**Tarefa:** classifique cada serviço em "fala primeiro" ou "espera sonda". Depois compare
com `nmap -sV -p 22,80,443,3306 127.0.0.1`.

**Gabarito.** Saídas reais:

```
# 80  → Server: Apache/2.4.52 (Ubuntu)
# 3306 → 8.0.46-0ubuntu0.22.04.3 ... caching_sha2_password
```

**Falam primeiro:** SSH, SMTP, FTP, POP3, MySQL, Redis.
**Esperam sonda:** HTTP, TLS, e a maioria dos protocolos binários.

O MySQL entrega versão, distribuição e nível de patch **antes da autenticação** — é
comportamento normal do protocolo, e é por isso que "banner" é informação sensível.

---

## Lab 9 · Esgotar portas efêmeras (com cuidado)

**Nível:** avançado · **Tempo:** 30 min

⚠️ Faça em VM ou container. Isto pode afetar outras conexões da máquina.

```python
#!/usr/bin/env python3
"""esgota.py — abre conexões até acabarem as portas de origem."""
import socket

srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", 0)); srv.listen(1024)
porta = srv.getsockname()[1]

conexoes = []
try:
    while True:
        c = socket.socket(); c.connect(("127.0.0.1", porta))
        conexoes.append(c)
        if len(conexoes) % 1000 == 0:
            print(len(conexoes), flush=True)
except OSError as e:
    print(f"parou em {len(conexoes)}: errno {e.errno} — {e.strerror}")
```

**Tarefa:** em quantas conexões parou? Compare com `ulimit -n` e com a faixa efêmera.

**Gabarito.** Existem **dois** tetos, e o menor vence:

```bash
ulimit -n                                    # aqui: 1048576
cat /proc/sys/net/ipv4/ip_local_port_range   # aqui: 32768 60999 = 28232
```

- Se parar com `EMFILE` (24), o limite foi de **descritores** — aumente `ulimit -n`.
- Se parar com `EADDRNOTAVAIL` (99), acabaram as **portas de origem**.

Na maioria dos sistemas com `ulimit` baixo (1024, comum em containers), você bate no
descritor primeiro e nunca vê o esgotamento de porta. Aumente o `ulimit` para chegar ao
segundo limite — que é o interessante.

A conta completa está em [`60-teoria-avancada.md`](60-teoria-avancada.md).

---

## Lab 10 · Ver o handshake 🔑

**Nível:** intermediário · **Tempo:** 25 min

```bash
# Terminal 1
sudo tcpdump -i lo -nn -c 12 'port 8099'

# Terminal 2
python3 -m http.server 8099 --bind 127.0.0.1 &
curl -s http://127.0.0.1:8099/ > /dev/null
```

**Tarefa:** identifique na saída: SYN, SYN-ACK, ACK, os dados, e o fechamento. Conte os
pacotes de uma requisição HTTP completa.

**Gabarito esperado:** `[S]` → `[S.]` → `[.]` (handshake), `[P.]` com o GET, `[P.]` com a
resposta, `[F.]`/`[.]` no fechamento. Cerca de 10 pacotes para buscar uma página. É isso que
o keep-alive economiza ao reutilizar a conexão.

**Sem `sudo`:** use `strace -e trace=network -f python3 -c "..."` para ver as chamadas de
sistema — não é o mesmo, mas mostra a sequência `socket`/`connect`/`send`/`recv`/`close`.

**Não executado** neste material (sem `sudo` no ambiente de escrita).

---

## Lab 11 · Auditoria com o projeto-modelo

**Nível:** intermediário · **Tempo:** 40 min

```bash
cd 07-projeto-modelo
python3 testes.py                                  # 41 testes
python3 auditor.py local --apenas-expostas
python3 auditor.py local --json > /tmp/inv.json
echo "código de saída: $?"
```

**Tarefas:**
1. Adicione ao `catalogo.py` cinco portas que a **sua** empresa usa.
2. Faça `classificar()` rebaixar a severidade quando o processo dono for esperado
   (`sshd` em 22 não é o mesmo que `nc` em 22).
3. Escreva um teste que prove a mudança **antes** de implementá-la.

**Gabarito.** O ponto do exercício 2 é notar que **o processo dono é uma informação de risco
tão importante quanto a porta**. `sshd` na 22 é o serviço legítimo; qualquer outra coisa na
22 é anomalia grave. A ferramenta como está não distingue — e a maioria das ferramentas
comerciais também não.

---

## Lab 12 · Detectar quem varre você 🔑

**Nível:** avançado · **Tempo:** 40 min

```bash
# Terminal 1 — observe
watch -n 1 "ss -tan state syn-recv | wc -l"

# Terminal 2 — varra a si mesmo
nmap -sT -p 1-10000 127.0.0.1

# Com privilégio, veja os pacotes
sudo tcpdump -i lo -nn 'tcp[tcpflags] & tcp-syn != 0 and not tcp[tcpflags] & tcp-ack != 0'
```

**Tarefa:** qual é a assinatura de uma varredura, em uma frase? Escreva uma regra conceitual
de detecção.

**Gabarito.** Assinatura: **muitas portas distintas, do mesmo IP de origem, num intervalo
curto, com alta proporção de conexões que não trocam dados.**

Regra conceitual: `> N portas distintas do mesmo IP em T segundos → alerta`. É exatamente o
que `psad` e `fail2ban` implementam. Os parâmetros `N` e `T` são o compromisso entre falso
positivo (um monitor legítimo checando 20 portas) e falso negativo (varredura lenta,
distribuída em horas — que é como um atacante cuidadoso opera).

---

## Lab 13 · Portas em container 🔑

**Nível:** avançado · **Tempo:** 40 min · exige Docker

```bash
docker run -d --name t1 -p 8080:80 nginx
docker run -d --name t2 -p 127.0.0.1:8081:80 nginx

ss -tlnp | grep -E ':(8080|8081)'
curl -sS -m 3 http://$(hostname -I | awk '{print $1}'):8080/ | head -3
curl -sS -m 3 http://$(hostname -I | awk '{print $1}'):8081/ | head -3

PID=$(docker inspect -f '{{.State.Pid}}' t1)
sudo nsenter -t $PID -n ss -tulpn
sudo iptables -t nat -S DOCKER

docker rm -f t1 t2
```

**Tarefa:** por que `ss` do host não mostra o nginx escutando na 80? Quantos sockets existem
para o `-p 8080:80`?

**Gabarito.** **Dois** sockets, em duas tabelas: o `docker-proxy` no host (`0.0.0.0:8080`)
e o nginx no namespace do container (`0.0.0.0:80`). Mais uma regra de DNAT no `PREROUTING`.
O `ss` do host só vê o primeiro; `nsenter` mostra o segundo.

O `t2`, publicado em `127.0.0.1:8081`, **não responde** pelo IP externo. É a correção de uma
linha que resolve o problema do `ufw` não bloquear containers.

**Não executado** neste material (sem Docker no ambiente de escrita).

---

## Lab 14 · Auditoria completa de um alvo autorizado

**Nível:** avançado · **Tempo:** 60 min

⚠️ Alvo: `scanme.nmap.org` (autorizado pelo projeto Nmap) **ou** uma VM sua. Nada mais.

```bash
nmap -sn scanme.nmap.org                                  # está vivo?
nmap -Pn --top-ports 100 --reason scanme.nmap.org         # o que responde e POR QUÊ
nmap -sV -Pn -p 22,80 scanme.nmap.org                     # o que fala em cada porta
nmap -Pn -p 22,80 -oA /tmp/scanme scanme.nmap.org         # salva os três formatos
```

**Tarefa:** produza um relatório de uma página com: alvo, data, hora, ferramenta e versão,
técnica usada, portas encontradas com evidência (`REASON`), e — o mais importante — **o que
você NÃO conseguiu determinar e por quê**.

**Gabarito.** A última seção é o que separa relatório profissional de despejo de saída de
ferramenta. Ela deve dizer coisas como:

- portas classificadas como `filtered` não foram confirmadas: ausência de resposta não
  distingue firewall de perda de pacote;
- UDP não foi varrido (custo/tempo), portanto serviços UDP não estão cobertos;
- a varredura reflete o caminho de rede **daquele ponto de origem**, naquele instante;
- versões vêm de banner, que pode ser configurado para mentir.

Um relatório que não enumera suas próprias limitações induz o leitor a conclusões que os
dados não sustentam. Ver [`ethical-hacking`](../ethical-hacking/00-MAPA.md) nesta pasta,
capítulo de relatório.

---

## Sequência sugerida

| Se você é… | Faça, nesta ordem |
|---|---|
| Iniciante | 1 → 2 → 3 → 8 |
| Desenvolvedor | 1 → 2 → 5 → 6 → 13 |
| Administrador / SRE | 1 → 4 → 7 → 9 → 11 → 12 |
| Segurança | todos, com atenção ao 7, 12 e 14 |

---

*Próximo: [`75-armadilhas.md`](75-armadilhas.md) — os 30 erros clássicos.*
