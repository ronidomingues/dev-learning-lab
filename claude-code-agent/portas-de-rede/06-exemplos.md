# 06 · Exemplos — 15 receitas completas

**Nível:** iniciante a avançado · **Última atualização:** 14/08/2026
Cada exemplo é: **problema → solução → explicação**. Todo código é completo e executável.
As saídas marcadas *(real)* foram executadas em Ubuntu 22.04.5, kernel 6.8.0-136, em
14/08/2026. Os exemplos 12 e 13 não foram executados e isso está dito neles.

---

## 1 · "A porta 8080 está ocupada e eu não sei por quem"

**Problema:** seu servidor não sobe. `Address already in use`.

```bash
ss -tlnp | grep :8080
```

Se vier vazio, o dono é de outro usuário:

```bash
sudo ss -tlnp | grep :8080
```

Ainda vazio? Então não é um processo comum — é container ou redirecionamento:

```bash
sudo lsof -nP -iTCP:8080                    # inclui conexões, não só LISTEN
docker ps --format '{{.Names}}\t{{.Ports}}' | grep 8080
sudo iptables -t nat -S | grep 8080
```

**Encerrar o dono:**

```bash
fuser -k -n tcp 8080          # mata quem estiver na 8080/tcp
```

**Explicação.** A busca segue uma ordem de escopo crescente: seu usuário → todos os usuários
→ outro *namespace* de rede → regra de kernel. Pular etapas é o que faz alguém reiniciar a
máquina por um problema de dois comandos.

---

## 2 · "Quais portas desta máquina são alcançáveis de fora?"

**Problema:** você quer a lista curta, a que importa para segurança.

```bash
ss -tulpn | grep -vE '127\.0\.0\.|\[::1\]'
```

Melhor ainda, com julgamento:

```bash
cd 07-projeto-modelo && python3 auditor.py local --apenas-expostas
```

**Saída real** *(recortada)*:

```
CRITICO   tcp    0.0.0.0:445    todas-interfaces  (sem permissão)  microsoft-ds: ... Alvo de EternalBlue/WannaCry.
CRITICO   tcp    0.0.0.0:139    todas-interfaces  (sem permissão)  netbios-ssn: SMB sobre NetBIOS. Legado; use 445.
ATENCAO   tcp    :::80          todas-interfaces  (sem permissão)  http: Web sem criptografia.
OK        udp    0.0.0.0:5353   todas-interfaces  (sem permissão)  mdns: exposição usual para este serviço

RESUMO: 35 sockets em escuta · 14 crítico(s) · 19 atenção · 2 ok
```

**Explicação.** `grep -v 127.0.0` remove o que só a própria máquina alcança. O que sobra é
sua **superfície de ataque local**. Se essa lista tem linhas que você não sabe explicar,
você tem trabalho a fazer — e é exatamente esse o ponto do exercício.

---

## 3 · Provar que `bind` restringe mais e melhor que firewall

**Problema:** entender por que "escutar em 127.0.0.1" é uma medida de segurança.

```bash
# Terminal 1 — escuta SÓ em loopback
python3 -m http.server 8099 --bind 127.0.0.1
```

```bash
# Terminal 2
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8099/    # 200
curl -sS -m 3 http://10.209.2.168:8099/                            # do IP externo
```

**Saída real:**

```
200
curl: (7) Failed to connect to 10.209.2.168 port 8099 after 0 ms: Conexão recusada
```

Agora troque o bind e repita:

```bash
python3 -m http.server 8099 --bind 0.0.0.0
curl -s -o /dev/null -w '%{http_code}\n' http://10.209.2.168:8099/   # agora responde 200
```

**Explicação.** O `bind()` diz ao kernel **em qual endereço** o socket aceita conexões.
Com `127.0.0.1`, pacotes que chegam por qualquer outra interface nem chegam ao socket — são
descartados na pilha, antes de qualquer regra de firewall.

Isso é superior a filtrar porque:
- não há regra para alguém remover por engano;
- sobrevive a reinstalação de firewall, mudança de distro, migração para container;
- é uma linha de configuração do próprio serviço, versionada junto com ele.

**A hierarquia, para gravar:** desligue o serviço > restrinja o `bind` > filtre no firewall.

---

## 4 · Ver o `TIME_WAIT` acontecer, e entender o `SO_REUSEADDR`

**Problema:** "matei o processo e a porta continua ocupada".

```python
#!/usr/bin/env python3
"""time_wait.py — demonstra TIME_WAIT e SO_REUSEADDR."""
import socket, subprocess, time

srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", 0)); srv.listen(1)
porta = srv.getsockname()[1]

cli = socket.socket(); cli.connect(("127.0.0.1", porta))
conn, _ = srv.accept()

conn.close()          # O SERVIDOR fecha primeiro → o SERVIDOR fica em TIME_WAIT
cli.close(); srv.close()
time.sleep(0.2)

print(subprocess.run(["ss", "-tan", f"( sport = :{porta} or dport = :{porta} )"],
                     capture_output=True, text=True).stdout)

for nome, reusar in (("sem SO_REUSEADDR", False), ("com SO_REUSEADDR", True)):
    s = socket.socket()
    if reusar:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("127.0.0.1", porta)); s.listen(1)
        print(f"{nome}: bind+listen OK"); s.close()
    except OSError as e:
        print(f"{nome}: {e}")
```

**Saída real:**

```
State     Recv-Q Send-Q Local Address:Port  Peer Address:Port
TIME-WAIT 0      0          127.0.0.1:33527    127.0.0.1:48654

sem SO_REUSEADDR: [Errno 98] Address already in use
com SO_REUSEADDR: bind+listen OK
```

**Explicação.** Quem **fecha primeiro** entra em `TIME_WAIT` e fica lá por 2×MSL (no Linux,
60 s fixos). Existe para que pacotes atrasados da conexão velha não sejam entregues a uma
conexão nova com a mesma quádrupla.

`SO_REUSEADDR` diz ao kernel: *"deixe eu fazer bind mesmo havendo um TIME_WAIT com esse
endereço local"*. É seguro para um servidor que está reiniciando, e é por isso que
**todo servidor sério liga essa opção** — incluindo o `alvo_laboratorio.py` do projeto-modelo.

O detalhe completo está em [`13-tcp-por-dentro.md`](13-tcp-por-dentro.md).

---

## 5 · Ver o *backlog* estourar

**Problema:** entender a coluna `Recv-Q` de uma linha `LISTEN`, e o que acontece quando o
serviço para de aceitar conexões.

```python
#!/usr/bin/env python3
"""backlog.py — servidor que escuta mas NUNCA chama accept()."""
import socket, subprocess

srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", 0))
srv.listen(2)                       # backlog de apenas 2
porta = srv.getsockname()[1]

clientes = []
for i in range(6):
    c = socket.socket(); c.settimeout(1)
    try:
        c.connect(("127.0.0.1", porta))
        clientes.append(c)
        print(f"conexão {i+1}: aceita pelo kernel")
    except Exception as e:
        print(f"conexão {i+1}: {type(e).__name__} {e}")

print(subprocess.run(["ss", "-tln", f"sport = :{porta}"],
                     capture_output=True, text=True).stdout)
srv.close()
```

**Saída real:**

```
conexão 1: aceita pelo kernel
conexão 2: aceita pelo kernel
conexão 3: aceita pelo kernel
conexão 4: TimeoutError timed out
conexão 5: TimeoutError timed out
conexão 6: TimeoutError timed out

State  Recv-Q Send-Q Local Address:Port
LISTEN 3      2          127.0.0.1:46189
```

**Explicação — leia com atenção, porque há três lições aqui:**

1. **O kernel aceita conexões sozinho.** As três primeiras completaram o handshake sem que o
   programa chamasse `accept()` uma única vez. Do ponto de vista do cliente, a conexão
   "funcionou". Ela está na fila.
2. **`Recv-Q` num socket `LISTEN` é o tamanho da fila** (3), e `Send-Q` é o **backlog**
   configurado (2). Não são bytes.
3. **`listen(2)` aceitou 3.** O Linux usa `backlog + 1` como capacidade efetiva. Detalhe de
   implementação, documentado no `listen(2)` — e uma boa lembrança de que "o padrão diz X"
   e "o seu kernel faz X" nem sempre coincidem.

**O uso prático:** se num servidor de produção você vir `Recv-Q` alto e preso numa linha
`LISTEN`, o processo está vivo mas travado. Não é problema de rede. É a aplicação não
aceitando. Esse diagnóstico, em um comando, já salvou muita madrugada.

---

## 6 · Descobrir o que realmente fala numa porta (sem `nmap -sV`)

**Problema:** a porta está aberta. E daí? Qual é o serviço?

```bash
# 1. o serviço fala primeiro? (SSH, SMTP, FTP, MySQL falam)
timeout 2 nc 127.0.0.1 3306 | head -c 120 | xxd | head -4

# 2. fala HTTP?
printf 'GET / HTTP/1.0\r\n\r\n' | timeout 2 nc 127.0.0.1 80 | head -8

# 3. fala TLS?
openssl s_client -connect 127.0.0.1:443 </dev/null 2>&1 | head -12
```

**Saídas reais:**

```
# porta 80
HTTP/1.1 200 OK
Date: Fri, 14 Aug 2026 16:39:35 GMT
Server: Apache/2.4.52 (Ubuntu)

# porta 3306
8.0.46-0ubuntu0.22.04.3 ... caching_sha2_password
```

**Explicação.** Serviços dividem-se em dois grupos:

- **Os que falam primeiro** (SSH, SMTP, FTP, POP3, MySQL, Redis): basta conectar e ler.
- **Os que esperam** (HTTP, TLS, e a maioria dos binários): é preciso enviar uma sonda.

É por isso que um scanner precisa de uma **base de sondas**. O `nmap -sV` tem milhares delas
em `/usr/share/nmap/nmap-service-probes`, acumuladas em 25 anos. Reproduzir isso é o
exercício 3 do [projeto-modelo](07-projeto-modelo/README.md).

**A observação de segurança:** o MySQL entregou versão, distribuição e nível de patch
**antes de qualquer autenticação**. Quem varre não precisa de credencial para saber se você
aplicou a correção do mês passado.

---

## 7 · Comparar o que o kernel vê com o que a rede responde

**Problema:** `ss` e `nmap` discordam. Quem está certo?

```bash
cd 07-projeto-modelo
python3 auditor.py comparar -p 1-10000
```

**Saída real:**

```
CONFRONTO — 127.0.0.1, 10000 portas testadas

  concordam (kernel diz LISTEN e a rede conecta): 8
    [80, 139, 445, 631, 3001, 3306, 5173, 9050]

  só o kernel vê (LISTEN mas a conexão não completa): 3
        53  → escuta em IP específico que não é 127.0.0.1, ou firewall local
      9789, 9879

  só a rede vê (conecta, mas NENHUM processo escuta): 2
      2222, 3128  → redirecionamento no kernel, proxy transparente, agente de segurança
```

**Explicação — os dois estão certos, sobre coisas diferentes:**

- **Porta 53 "só o kernel vê":** o `systemd-resolved` escuta em `127.0.0.53:53`. Todo o
  bloco `127.0.0.0/8` é loopback — 16 milhões de endereços. Um teste contra `127.0.0.1`
  não alcança `127.0.0.53`.
- **Portas 2222 e 3128 "só a rede vê":** `connect()` completa e **nenhum processo escuta**.
  Só há uma explicação: uma regra no kernel redireciona a conexão antes de ela chegar a um
  socket. Confirme com:

```bash
sudo iptables -t nat -S | grep -E 'REDIRECT|DNAT|TPROXY'
sudo nft list ruleset | grep -E 'redirect|dnat|tproxy'
```

Na máquina onde este curso foi escrito, o `nmap` chegou a reportar **25** portas abertas em
`127.0.0.1` das quais o `ss` confirmava 8. Não foi possível confirmar a causa sem `sudo`, e
este material diz isso em vez de inventar. A hipótese mais provável é um agente de segurança
corporativo.

**A lição:** *"a porta está aberta"* é uma afirmação sobre o **caminho inteiro**, não sobre
um processo.

---

## 8 · Achar vazamento de descritor (`CLOSE_WAIT` crescente)

**Problema:** o serviço vai degradando ao longo de horas até parar com `Too many open files`.

```bash
watch -n 5 "ss -tan | awk 'NR>1{print \$1}' | sort | uniq -c | sort -rn"
```

**Saída real desta máquina:**

```
   1524 TIME-WAIT
     33 LISTEN
     29 ESTAB
     14 CLOSE-WAIT
```

Se `CLOSE-WAIT` estiver alto e **crescendo**, localize o culpado:

```bash
ss -tanp state close-wait | head -20
sudo lsof -nP -p <PID> | wc -l            # quantos descritores esse processo tem
cat /proc/<PID>/limits | grep 'open files'
ls /proc/<PID>/fd | wc -l                 # contagem exata, em tempo real
```

**Explicação.** `CLOSE_WAIT` significa: *o outro lado fechou, e o seu programa ainda não
chamou `close()`*. É o único estado do TCP que aponta o dedo diretamente para o seu código.

O kernel **não pode** resolver sozinho: ele não sabe se você ainda quer ler os dados que
sobraram no buffer. Então o socket fica lá, ocupando um descritor, para sempre.

Causa quase sempre a mesma: tratamento de exceção que abandona o socket sem `finally: close()`,
ou pool de conexões que não devolve. Em Python, `with socket.socket() as s:` resolve; em
Java, `try-with-resources`; em Go, `defer conn.Close()`.

**Diferença de `TIME_WAIT`:** `TIME_WAIT` é o TCP funcionando corretamente e some sozinho em
60 s. `CLOSE_WAIT` é bug e não some nunca.

---

## 9 · Auditar um servidor remoto que você administra

**Problema:** validar que o servidor expõe só o que deveria.

```bash
# 1. De dentro (a verdade)
ssh servidor "ss -tulpn | grep -vE '127\.0\.0\.|\[::1\]'"

# 2. De fora (o que o mundo vê)
nmap -sV -Pn --top-ports 1000 servidor.exemplo.com

# 3. A pergunta que fecha a auditoria: existe algo em 2 que não está em 1?
```

Automatizado, com o projeto-modelo:

```bash
ssh servidor 'cd /opt/auditor && python3 auditor.py local --json' > inventario.json
python3 -c "
import json
d = json.load(open('inventario.json'))
for s in d:
    if s['exposto'] and s['severidade'] == 'critico':
        print(f\"{s['protocolo']:>4} {s['ip_local']}:{s['porta_local']:<6} {s['motivo']}\")
"
```

**Explicação.** As duas visões respondem perguntas diferentes e **as duas são necessárias**:

| Só a visão de dentro | Só a visão de fora |
|---|---|
| Você não sabe se o firewall funciona | Você não sabe o que existe atrás do filtro |
| Não vê NAT nem balanceador | Não identifica o processo dono |
| Não vê o que o provedor de nuvem bloqueia | Não vê serviço que subiu depois da varredura |

Item 3 é o que importa: **algo aparecendo de fora que não aparece de dentro** significa NAT,
balanceador, proxy ou — no pior caso — que você varreu a máquina errada.

---

## 10 · Encontrar um serviço de desenvolvimento esquecido exposto

**Problema:** alguém subiu um servidor de teste em `0.0.0.0` e foi embora de férias.

```bash
ss -tlnp | awk '$4 !~ /127\.0\.0\.|\[::1\]/ && $4 ~ /:[0-9]{4,5}$/ {print}'
```

Com o projeto-modelo, que sabe o que é faixa efêmera:

```bash
python3 auditor.py local --apenas-expostas | grep -i 'efêmera'
```

**Saída real:**

```
ATENCAO  udp  :::33120     todas-interfaces  porta na faixa efêmera escutando para fora — quase sempre um servidor de desenvolvimento esquecido
ATENCAO  udp  0.0.0.0:47045 todas-interfaces  porta na faixa efêmera escutando para fora — quase sempre um servidor de desenvolvimento esquecido
```

**Explicação.** Um serviço que escuta numa porta **da faixa efêmera** (aqui, 32768–60999) é
quase sempre acidental: aquele intervalo é o de portas de **origem**, atribuídas
automaticamente. Um servidor deliberado usa número escolhido.

E o padrão delator: `0.0.0.0` + porta alta + o processo é `node`, `python`, `java` ou
`ruby` = servidor de desenvolvimento. Frameworks de desenvolvimento escutam em `0.0.0.0`
por padrão para funcionar dentro de container, e ninguém troca de volta ao rodar direto na
máquina.

---

## 11 · Testar se um firewall de nuvem realmente bloqueia

**Problema:** você configurou o Security Group. Funcionou mesmo?

```bash
# De uma máquina FORA da nuvem, contra o IP público:
nmap -Pn --reason -p 22,80,443,3306,5432,6379,27017 <ip-público>
```

Resultado esperado de um servidor web bem configurado:

```
PORT     STATE    SERVICE  REASON
22/tcp   open     ssh      syn-ack ttl 52
80/tcp   open     http     syn-ack ttl 52
443/tcp  open     https    syn-ack ttl 52
3306/tcp filtered mysql    no-response
5432/tcp filtered postgres no-response
6379/tcp filtered redis    no-response
```

**Explicação.** `--reason` é o que torna esse teste conclusivo:

| REASON | Significa |
|---|---|
| `syn-ack` | Chegou lá e tem serviço |
| `reset` | Chegou lá, **não** tem serviço — mas a máquina respondeu |
| `no-response` | Alguém no caminho descartou. **É o que você quer ver.** |
| `admin-prohibited` | Um roteador respondeu ICMP dizendo que bloqueou |

**`filtered` com `no-response` é o resultado desejado** para uma porta de banco. `closed`
com `reset` também impede o acesso, mas confirma que a máquina existe e está viva —
informação que você não precisava dar.

**Não executado neste material** (não havia instância de nuvem no ambiente de escrita).
A saída acima é ilustrativa do formato; o formato de `--reason` foi verificado localmente.

---

## 12 · Publicar um serviço de container corretamente

**Problema:** `docker run -p 8080:80` deixou o serviço aberto para a internet inteira.

```bash
# ERRADO: escuta em todas as interfaces
docker run -d -p 8080:80 nginx

# CERTO: escuta só em loopback do host
docker run -d -p 127.0.0.1:8080:80 nginx
```

Confira a diferença:

```bash
ss -tlnp | grep 8080
# errado: 0.0.0.0:8080  →  docker-proxy
# certo:  127.0.0.1:8080 → docker-proxy
```

**Explicação.** A sintaxe `-p` tem uma forma completa que quase ninguém usa:
`-p [IP_do_host:]porta_host:porta_container`. Sem o IP, o Docker assume `0.0.0.0`.

**E há uma armadilha maior:** o Docker escreve regras direto na tabela `nat` do netfilter,
em cadeias avaliadas **antes** das do `ufw`. Um `ufw deny 8080` **não** bloqueia um container
publicado em 8080. Não é bug de nenhum dos dois — é a ordem de avaliação do netfilter.

```bash
sudo iptables -t nat -S DOCKER            # as regras que o Docker criou
```

Detalhes em [`20-containers-nuvem-e-k8s.md`](20-containers-nuvem-e-k8s.md).

**Não executado** (sem Docker no ambiente de escrita). Comandos conforme a documentação
oficial do Docker; ver [`docker`](../docker/00-MAPA.md) nesta pasta.

---

## 13 · Caso real de produção — esgotamento de porta efêmera

**Problema real.** Um serviço em Kubernetes começa a falhar sob carga com
`connect: cannot assign requested address` (`EADDRNOTAVAIL`). Não é DNS, não é firewall,
não é o banco. Falha só no pico.

**Diagnóstico:**

```bash
sysctl net.ipv4.ip_local_port_range
# 32768 60999   → 28232 portas de origem disponíveis

ss -tan state time-wait | wc -l
# 27000 e subindo

ss -tan 'dst 10.0.5.20' | wc -l           # todas para o mesmo destino
```

**A conta que explica tudo:**

O sistema esgota portas de origem quando faz muitas conexões **para o mesmo destino
(IP, porta)**. Porque a quádrupla precisa ser única:

```
(IP_origem, PORTA_origem, IP_destino, PORTA_destino)
```

Com `IP_origem`, `IP_destino` e `PORTA_destino` fixos, sobra **só** a porta de origem para
variar. São 28 232 combinações. Cada uma fica presa 60 s em `TIME_WAIT` depois de fechada.

> **28 232 ÷ 60 s ≈ 470 conexões novas por segundo.** Acima disso, você esgota — sem
> nenhum recurso da máquina estar no limite.

Nesta máquina, a faixa foi conferida: `32768-60999 = 28232 portas`.

**As correções, em ordem de qualidade:**

```bash
# 1. A CORREÇÃO DE VERDADE: pare de abrir conexão nova a cada requisição.
#    Use keep-alive / pool de conexões. Isto elimina o problema, não o adia.

# 2. Ampliar a faixa (ganha ~1,3×; adia, não resolve)
sudo sysctl -w net.ipv4.ip_local_port_range="10240 65535"

# 3. Reaproveitar TIME_WAIT em conexões de saída (seguro)
sudo sysctl -w net.ipv4.tcp_tw_reuse=1

# 4. Mais IPs de origem: cada IP adicional multiplica o espaço
```

⚠️ **Não use `tcp_tw_recycle`.** Ele foi **removido do kernel na versão 4.12** (2017)
porque quebrava clientes atrás de NAT de forma silenciosa e intermitente. Tutorial que ainda
o recomenda é de antes de 2017 — e isso é um bom teste de frescor de qualquer material de
rede que você encontrar.

**Explicação de fundo.** A causa-raiz é a decisão de 1980 de usar 16 bits para o número da
porta. Naquele momento, 65 mil parecia infinito. Hoje, um único serviço bem carregado chega
ao teto. Análise completa em [`60-teoria-avancada.md`](60-teoria-avancada.md).

**Não executado** neste ambiente (exigiria carga real). Os números da faixa e a aritmética
foram verificados; a saída de `ss` sob carga é ilustrativa.

---

## 14 · Caso real de produção — "o serviço está no ar mas o balanceador diz que não"

**Problema real.** A aplicação responde ao `curl` local. O health check do balanceador falha.
Ninguém entende.

**O roteiro de diagnóstico, na ordem certa:**

```bash
# 1. O serviço escuta? Em qual endereço?
ss -tlnp | grep :8080
# LISTEN 0 511 127.0.0.1:8080  ← ACHOU. Escuta só em loopback.
```

E acabou. O balanceador vem de outra máquina; loopback não o alcança. O `curl` local
funcionava porque o teste era feito **de dentro**.

Se não fosse isso, os passos seguintes seriam:

```bash
# 2. Responde do IP da interface?
curl -sS -m 3 http://$(hostname -I | awk '{print $1}'):8080/health

# 3. Responde de outra máquina?
nc -zv <ip> 8080

# 4. Firewall local?
sudo nft list ruleset | grep 8080
sudo iptables -L INPUT -n -v | grep 8080

# 5. Firewall de nuvem? (Security Group / NSG)

# 6. O health check bate no caminho certo?
curl -v http://<ip>:8080/health     # o path e o status esperado batem?
```

**Explicação.** A ordem é do mais barato e mais provável para o mais caro e mais raro.
Quem começa pelo passo 4 gasta horas. O passo 1 resolve talvez metade dos casos, e custa
três segundos.

**A pergunta que fecha o diagnóstico em uma frase:** *"o `curl` que funcionou rodou na
mesma máquina que o serviço?"* Se sim, ele não testou nada de rede.

---

## 15 · Um "porta-scan" honesto em 20 linhas de Python

**Problema:** entender o que um scanner realmente faz. Sem mágica.

```python
#!/usr/bin/env python3
"""scan_minimo.py — o núcleo de qualquer scanner TCP, sem enfeite."""
import socket, sys
from concurrent.futures import ThreadPoolExecutor

def testar(host: str, porta: int, timeout: float = 0.5) -> str | None:
    s = socket.socket(); s.settimeout(timeout)
    try:
        s.connect((host, porta))
        return "aberta"
    except socket.timeout:
        return "filtrada"          # ninguém respondeu: firewall descartou
    except ConnectionRefusedError:
        return None                # RST: fechada. Não interessa reportar.
    except OSError:
        return None
    finally:
        s.close()

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    portas = range(1, 10001)
    with ThreadPoolExecutor(max_workers=200) as pool:
        for porta, estado in zip(portas, pool.map(lambda p: testar(host, p), portas)):
            if estado:
                nome = "?"
                try:
                    nome = socket.getservbyport(porta, "tcp")
                except OSError:
                    pass
                print(f"{porta:>6}/tcp  {estado:<9} {nome}")
```

```bash
python3 scan_minimo.py 127.0.0.1
```

**Explicação — três coisas que este código ensina e que a maioria dos tutoriais omite:**

1. **Um scanner é `connect()` num laço.** Não há magia. `nmap -sT` faz exatamente isto.
   O que separa este script do `nmap` é o `-sS` (que forja pacotes e não completa o
   handshake), a base de sondas do `-sV`, e 25 anos de tratamento de casos extremos.

2. **Os três desfechos precisam ser distintos.** Quem escreve `except: pass` perde a
   diferença entre "fechada" e "filtrada" — e essa diferença é a informação mais valiosa
   da varredura.

3. **`getservbyport` é um chute, não uma leitura.** Ele consulta `/etc/services`, que é uma
   tabela de convenções. Ele diz "o que costuma estar aí", não "o que está aí". Toda vez
   que uma ferramenta mostra o nome do serviço sem `-sV`, é isso que está acontecendo.

⚠️ **Alvo padrão `127.0.0.1` de propósito.** Não aponte para máquina de terceiro.

---

## Autoteste

1. No exemplo 5, `listen(2)` aceitou 3 conexões. Por quê? E o que `Recv-Q 3 / Send-Q 2`
   significa numa linha `LISTEN`?
2. Qual a diferença entre `TIME_WAIT` e `CLOSE_WAIT` — em causa, em duração, e em quem
   precisa consertar?
3. Por que restringir o `bind` a `127.0.0.1` é melhor que uma regra de firewall que bloqueia
   a mesma porta? Dê dois motivos.
4. No exemplo 7, a porta 53 aparecia no `ss` mas não na varredura de `127.0.0.1`. Qual é a
   explicação exata?
5. Faça a conta do exemplo 13 para uma faixa efêmera de `10240-65535`. Quantas conexões
   novas por segundo para o mesmo destino o sistema aguenta?
6. Por que `-p 8080:80` no Docker é diferente de `-p 127.0.0.1:8080:80`, e por que `ufw`
   não protege o primeiro?
7. No exemplo 15, o que exatamente diferencia esse script do `nmap -sS`? Cite duas coisas.
8. Um colega mostra um `curl` local funcionando e diz que o serviço está no ar. Que pergunta
   você faz antes de acreditar?

---

*Próximo: [`07-projeto-modelo/`](07-projeto-modelo/README.md) — o auditor completo · ou [`10-fundamentos.md`](10-fundamentos.md) para começar o núcleo.*
