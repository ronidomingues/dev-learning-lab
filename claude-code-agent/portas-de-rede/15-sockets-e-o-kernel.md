# 15 · Sockets e o kernel — o que o `ss` faz por dentro

**Nível:** avançado · **Última atualização:** 14/08/2026
Todas as saídas de `/proc` deste arquivo foram lidas desta máquina em 14/08/2026.

---

## O objetivo deste arquivo

Depois de lê-lo, `ss -tulpn` deixa de ser um comando e vira uma sequência de operações que
você poderia reescrever. Não sobra caixa-preta. E, como efeito colateral, você entende
exatamente por que a coluna `Process` fica vazia sem `sudo`.

---

## 1. A tabela de sockets é um arquivo de texto

Rode:

```bash
head -5 /proc/net/tcp
```

**Saída real:**

```
  sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode
   0: 0100007F:AB13 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 10056 2 ...
   1: 00000000:008B 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 8081  1 ...
   2: 00000000:01BD 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 8080  1 ...
   3: 0100007F:0CEA 00000000:0000 0A 00000000:00000000 00:00000000 00000000   129        0 12303 1 ...
```

Isto é a tabela de sockets TCP do kernel, exposta como texto. **Qualquer usuário pode ler.**
É daqui que o `netstat` tira tudo.

### Decodificando a linha 3, campo a campo

```
   3: 0100007F:0CEA 00000000:0000 0A ... 129 ... 12303
   │       │    │        │        │      │        │
   │       │    │        │        │      │        └─ inode do socket
   │       │    │        │        │      └────────── uid do dono (129)
   │       │    │        │        └───────────────── estado: 0A = LISTEN
   │       │    │        └────────────────────────── endereço remoto: nenhum
   │       │    └─────────────────────────────────── porta local: 0x0CEA = 3306
   │       └──────────────────────────────────────── IP local: 0100007F
   └──────────────────────────────────────────────── índice da linha
```

**`0100007F` é `127.0.0.1`.** Parece embaralhado porque está em **ordem de bytes do host**
(little-endian no x86): o inteiro de 32 bits foi despejado exatamente como estava na memória.

```
bytes na memória:  01 00 00 7F
lidos como inteiro little-endian:  0x7F000001
0x7F = 127, 0x00 = 0, 0x00 = 0, 0x01 = 1  →  127.0.0.1
```

**`0x0CEA` = 3306** — MySQL. E `uid 129` é o usuário `mysql` desta máquina.

Confirme cruzando com o `ss`:

```bash
ss -tlnp 'sport = :3306'
# LISTEN 0 151 127.0.0.1:3306 0.0.0.0:*
```

Bate.

### Um exemplo melhor ainda, do `/proc/net/udp`

```
  604: 3500007F:0035 00000000:0000 07 ... 101 ... 1809
```

- `3500007F` → bytes `7F 00 00 35` → **127.0.0.53**
- `0035` → **53**
- `07` em UDP significa "não conectado" (`UNCONN`)
- `uid 101` → `systemd-resolve`

É o resolvedor de DNS local. E ele mostra, em dado bruto, o ponto do
[`04`](04-como-comecar.md): **loopback não é só `127.0.0.1`**.

### Por que hexadecimal em ordem de host?

Porque em 1993, quando essa interface foi criada, ela era um **artefato de depuração** que
alguém expôs para facilitar a vida. Imprimir o inteiro como estava era a coisa mais barata a
fazer. Nunca foi projetado como API pública.

Depois virou API pública porque o `netstat` passou a depender dela, e aí não pôde mais mudar.
**É uma decisão histórica documentada** — e um bom exemplo de como "interface acidental"
vira contrato permanente.

Implementação em 12 linhas, no `inventario.py` do
[projeto-modelo](07-projeto-modelo/README.md), com cinco testes cobrindo os casos.

---

## 2. Onde está o PID? Em lugar nenhum.

Olhe a tabela de novo. **Não há coluna de PID.** Só um número de i-node.

O kernel não guarda "qual processo é dono deste socket", porque a pergunta é mal posta: um
socket pode ser compartilhado por vários processos (depois de um `fork()`), passado entre
processos por `SCM_RIGHTS`, ou não pertencer a nenhum (`TIME_WAIT` sobrevive ao processo).

### Como o `ss -p` descobre, então

Ele faz a busca **ao contrário**, e é caro:

```
1. Lê /proc/net/tcp        → obtém a lista de i-nodes
2. Para CADA processo em /proc/<pid>/
3.   Para CADA descritor em /proc/<pid>/fd/
4.     Lê o link simbólico
5.     Se for "socket:[12345]", associa o i-node 12345 àquele PID
```

Veja um descritor de verdade:

```bash
ls -l /proc/self/fd
```
```
lr-x------ 1 ronivaldo ronivaldo 64 ago 14 14:22 0 -> /dev/null
l-wx------ 1 ronivaldo ronivaldo 64 ago 14 14:22 1 -> pipe:[2102117]
lr-x------ 1 ronivaldo ronivaldo 64 ago 14 14:22 3 -> /proc/228344/fd
```

Um socket apareceria como `4 -> socket:[2050580]`.

### **É por isso que a coluna `Process` fica vazia sem `sudo`**

Repare nas permissões acima: `lr-x------`. Só o dono lê. A tabela `/proc/net/tcp` é pública,
mas `/proc/<pid>/fd` de **outro usuário** não é.

Consequência exata, que você viu no [`04`](04-como-comecar.md):

```
LISTEN 0 50  0.0.0.0:445  0.0.0.0:*                    ← porta visível, dono invisível
LISTEN 0 511 127.0.0.1:35633 0.0.0.0:* users:(("code",pid=55375,fd=92))   ← seu processo
```

**Isto não é falha da ferramenta. É a permissão do Unix funcionando exatamente como
projetada:** você pode saber que a porta está ocupada (informação de recurso compartilhado),
mas não pode inspecionar os processos alheios (informação privada).

---

## 3. Por que o `ss` é rápido e o `netstat` é lento

| | `netstat` | `ss` |
|---|---|---|
| Fonte | `/proc/net/tcp` (texto) | **netlink** `NETLINK_INET_DIAG` (binário) |
| Filtragem | Em espaço de usuário, depois de ler tudo | **Dentro do kernel** |
| Custo com 100 mil sockets | Dezenas de segundos | Menos de 1 s |

O `ss` fala com o kernel por um socket `AF_NETLINK`, mandando uma **estrutura de filtro**.
O kernel percorre suas tabelas internas e devolve **só o que casa**, em formato binário.

Quando você escreve:

```bash
ss -tan 'sport = :443'
```

esse filtro é compilado num pequeno programa de bytecode e avaliado no kernel. Comparado a
`ss -tan | grep :443`, que copia tudo para o espaço de usuário e joga 99 % fora, a diferença
em um servidor grande é de ordem de grandeza.

**É o mesmo princípio do BPF** (que nasceu para filtro de pacotes, em 1992) e que hoje, como
eBPF, faz muito mais. Ver [`65-estado-da-arte.md`](65-estado-da-arte.md).

---

## 4. Um socket é um arquivo — e o que isso custa

```
$ lsof -nP -iTCP:8099 -sTCP:LISTEN
COMMAND    PID      USER   FD   TYPE  DEVICE  NODE NAME
python3 221761 ronivaldo    3u  IPv4 2050580  TCP  127.0.0.1:8099 (LISTEN)
```

Aquele `3u` é o descritor 3. O mesmo tipo de número de um arquivo em disco.

**Consequências práticas, todas do mesmo fato:**

```bash
ulimit -n                    # limite por processo
```
```
1048576
```
```bash
cat /proc/sys/fs/file-max    # limite do sistema inteiro
```
```
9223372036854775807
```

*(Nesta máquina os limites são altos. Em containers e distros mais antigas, `ulimit -n`
costuma ser 1024 — e é o motivo nº 1 de `Too many open files` em produção.)*

- Cada conexão consome um descritor. 10 000 conexões = 10 001 descritores (com o de escuta).
- **`Too many open files` numa aplicação de rede quase nunca é sobre arquivos.** São sockets.
- Um socket vazado (`CLOSE_WAIT`) é um descritor vazado.
- `read()`, `write()`, `close()`, `select()`, `poll()`, `epoll()` funcionam nos dois.

Contar descritores de um processo, em tempo real:

```bash
ls /proc/<PID>/fd | wc -l
cat /proc/<PID>/limits | grep 'open files'
```

---

## 5. A memória por socket — onde os bytes esperam

```bash
ss -tm
```

**Saída real:**

```
skmem:(r1280,rb131072,t0,tb87040,f2816,w0,o0,bl0,d0)
```

| Campo | Significa |
|---|---|
| `r` | bytes na fila de recepção **agora** |
| `rb` | tamanho do buffer de recepção (131 072 = 128 KB) |
| `t` | bytes na fila de transmissão agora |
| `tb` | tamanho do buffer de transmissão |
| `d` | **datagramas descartados** — se for > 0, você está perdendo dados |

Os buffers são ajustáveis:

```bash
sysctl net.ipv4.tcp_rmem net.ipv4.tcp_wmem      # mínimo / padrão / máximo
sysctl net.core.rmem_max net.core.wmem_max
```

**Onde isso importa:** o produto banda × latência. Numa conexão de 1 Gbit/s com 100 ms de
RTT, você precisa de ~12 MB "em voo" para saturar o enlace. Com buffer de 128 KB, você
atinge no máximo ~10 Mbit/s — **independente da banda contratada**.

Esse é o motivo real de transferências intercontinentais serem lentas mesmo com link gordo,
e é ajustável. O Linux moderno faz auto-ajuste, mas o teto (`rmem_max`) continua sendo seu.

---

## 6. Como o kernel escolhe o socket de destino

Chegou um pacote. Kernel precisa achar o socket. O algoritmo, simplificado:

```
1. Monta a chave (IP orig, porta orig, IP dest, porta dest)
2. Procura na tabela de hash "established" por essa quádrupla exata
   └─ achou? entrega. Fim.
3. Não achou. Procura na tabela "listening" pela porta de destino:
   a) socket com bind no IP exato de destino     ← mais específico vence
   b) socket com bind em 0.0.0.0                 ← curinga
4. Achou LISTEN e o pacote é SYN?  → inicia handshake
   Achou LISTEN e não é SYN?       → RST
   Não achou nada?                 → RST  ("Connection refused")
```

**O passo 3 é o que explica a hierarquia de bind.** Um socket em `192.168.0.5:8080` tem
precedência sobre um em `0.0.0.0:8080` para pacotes que chegam naquele IP. É por isso que
esses dois **podem** coexistir, enquanto `0.0.0.0:8080` e `127.0.0.1:8080` conflitam
(o curinga já cobre o loopback).

Com `SO_REUSEPORT`, o passo 3 ganha um sorteio: havendo N sockets equivalentes, o kernel
escolhe um por hash da quádrupla — garantindo que todos os pacotes de uma mesma conexão
caiam sempre no mesmo processo.

---

## 7. Namespaces de rede — por que o `ss` "não vê" o container

Um *network namespace* é uma pilha de rede inteira e separada: interfaces próprias, tabela
de roteamento própria, **tabela de sockets própria**, regras de firewall próprias.

```bash
ls -l /proc/<PID>/ns/net       # em qual namespace o processo está
sudo lsns -t net               # lista todos os namespaces de rede
sudo nsenter -t <PID> -n ss -tulpn    # roda ss DENTRO do namespace daquele processo
ip netns list                  # namespaces nomeados (os do Docker não aparecem aqui)
```

**Isto resolve o mistério** de "o serviço está rodando, o container está de pé, e `ss` não
mostra porta nenhuma": o socket existe, mas em outra tabela.

O `docker run -p 8080:80` não faz o container escutar na 8080 do host. Ele:

1. faz o `docker-proxy` (ou uma regra de DNAT) escutar na 8080 do host;
2. encaminha para a 80 do namespace do container.

São **dois** sockets, em duas tabelas, e o `ss` do host só vê o primeiro.
Detalhes em [`20-containers-nuvem-e-k8s.md`](20-containers-nuvem-e-k8s.md).

---

## 8. Reimplementar o `ss` — o que o projeto-modelo faz

```python
def _decodifica_endereco(campo: str) -> tuple[str, int]:
    hex_ip, hex_porta = campo.split(":")
    porta = int(hex_porta, 16)
    if len(hex_ip) == 8:                          # IPv4
        bruto = struct.pack("<I", int(hex_ip, 16))   # "<" = little-endian
        return socket.inet_ntop(socket.AF_INET, bruto), porta
    palavras = [int(hex_ip[i:i+8], 16) for i in range(0, 32, 8)]   # IPv6
    bruto = b"".join(struct.pack("<I", p) for p in palavras)
    return socket.inet_ntop(socket.AF_INET6, bruto), porta
```

Doze linhas substituem o `ss` na parte de decodificação. O resto do
[`inventario.py`](07-projeto-modelo/inventario.py) faz o mapeamento i-node → PID.

Testes que provam que está certo (todos passando):

```python
_decodifica_endereco("0100007F:0016") == ("127.0.0.1", 22)
_decodifica_endereco("00000000:0050") == ("0.0.0.0", 80)
_decodifica_endereco("A802D10A:1F90") == ("10.209.2.168", 8080)
```

**Por que fazer isso importa pedagogicamente:** depois de escrever essas linhas, você não
tem mais como acreditar que o `ss` "sabe" algo mágico. Ele lê a mesma tabela que você acabou
de ler, e faz a mesma busca por i-node que você acabou de entender.

---

## Autoteste

1. Decodifique `0100007F:1F90` e `00000000:01BB` à mão. Que endereço e porta são?
2. Por que `3500007F` é `127.0.0.53` e não `53.0.0.127`?
3. Onde está o PID na tabela `/proc/net/tcp`? Como o `ss -p` o descobre, e por que isso é caro?
4. Explique, citando permissões de arquivo, por que `ss -tulpn` sem `sudo` mostra a porta
   mas não o processo alheio. Por que isso é correto e não um defeito?
5. Cite duas razões pelas quais `ss` é mais rápido que `netstat` num servidor com 100 mil
   conexões.
6. Por que `Too many open files` numa aplicação de rede geralmente não é sobre arquivos?
7. Você tem 1 Gbit/s e 100 ms de RTT, com buffer de recepção de 128 KB. Qual vazão máxima
   você alcança? O que precisa mudar?
8. Um container está rodando e `ss -tulpn` no host não mostra a porta interna dele. Explique,
   e diga o comando que revela.
9. Por que `0.0.0.0:8080` e `127.0.0.1:8080` conflitam, mas `192.168.0.5:8080` e
   `0.0.0.0:8080` podem coexistir? Use o algoritmo de busca do kernel na resposta.

---

*Próximo: [`16-catalogo-de-portas.md`](16-catalogo-de-portas.md) — as portas, uma a uma.*
