# Glossário — Portas de Rede

**Última atualização:** 14/08/2026
Termos técnicos em inglês aparecem com a tradução usual; quando o campo usa o termo em
inglês, é ele que está em destaque. Referências cruzadas em **negrito**.

---

## A

**ACK** — *acknowledgment*. Flag do TCP que confirma o recebimento de dados. Um pacote com
SYN+ACK é a segunda etapa do **handshake**.

**ACL** — *access control list*. Lista de regras de permissão, tipicamente por IP e porta.

**AF_INET / AF_INET6 / AF_UNIX / AF_NETLINK** — famílias de **socket**: IPv4, IPv6, arquivo
local, e comunicação com o kernel, respectivamente.

**AGPL** — licença que estende a obrigação de fornecer o código-fonte a quem usa o software
**pela rede**. Relevante para o `masscan`.

**Amplificação** — ataque em que um pedido pequeno com IP de origem forjado gera uma
resposta grande enviada à vítima. Só é possível em **UDP**. Ver **BCP 38**.

**`accept()`** — chamada de sistema que retira uma conexão pronta da fila e devolve **um
socket novo**. Não abre porta nenhuma.

**Aberta (porta)** — estado em que uma sondagem recebeu SYN-ACK: existe processo escutando.

---

## B

**Backlog** — tamanho da fila de conexões já estabelecidas pelo kernel, esperando
**`accept()`**. Aparece na coluna `Send-Q` de uma linha `LISTEN`. No Linux, a capacidade
efetiva é `backlog + 1`.

**Banner** — o que um serviço envia ao ser conectado. Frequentemente revela produto e versão
antes de qualquer autenticação.

**BCP 38** (RFC 2827) — prática recomendada de filtrar, na borda, pacotes com IP de origem
forjado. É a defesa estrutural contra **amplificação**. Adoção parcial por problema de
incentivo.

**BGP** — protocolo de roteamento entre sistemas autônomos, porta 179/TCP. Alvo histórico de
ataques de reset que motivaram o RFC 5961 e a aleatorização de **porta efêmera**.

**`bind()`** — chamada de sistema que **reserva** o par (IP, porta) para um socket. É ela
que "abre a porta".

**BPF / eBPF** — mecanismo de execução de programas verificados dentro do kernel. Base do
filtro do `ss`, do `tcpdump`, e da observabilidade moderna.

---

## C

**CGNAT** — *Carrier-Grade NAT* (RFC 6598). Vários assinantes compartilhando um IPv4 público,
com endereços internos em `100.64.0.0/10`. Impede abrir portas de entrada.

**`CLOSE_WAIT`** — estado TCP em que o outro lado fechou e **o seu programa não chamou
`close()`**. Não expira. É o único estado que aponta o defeito diretamente para a aplicação.

**Connection ID** — identificador de conexão do **QUIC**. Substitui a **quádrupla** como
identidade, permitindo migração entre redes.

**`connect()`** — chamada de sistema que inicia uma conexão. Faz um **`bind()`** implícito
numa **porta efêmera** se você não tiver feito um explícito.

**conntrack** — tabela de rastreamento de conexões do netfilter. Ter estado é o que permite
a um firewall distinguir resposta de conexão nova.

**`cwnd`** — *congestion window*. Janela de congestionamento do TCP, em segmentos. Visível em
`ss -ti`.

---

## D

**DCCP** — transporte com datagramas e controle de congestionamento (RFC 4340). Tem portas.
Praticamente sem uso.

**Demultiplexação** — separar, no destino, fluxos que chegaram por um canal comum. É
**a** função da porta.

**Descritor de arquivo** (*file descriptor*, fd) — número inteiro que identifica um recurso
aberto por um processo. **Um socket é um descritor de arquivo.**

**DNAT** — tradução do endereço de **destino**. É o mecanismo do *port forwarding* e da
publicação de porta do Docker.

**DoH / DoT / DoQ** — DNS sobre HTTPS (443/TCP), sobre TLS (853) e sobre QUIC (853/UDP).

**DROP** — ação de firewall que descarta o pacote **sem avisar**. Produz **timeout** no
cliente e faz a porta aparecer como **filtrada**.

---

## E

**`EADDRINUSE`** (errno 98) — `Address already in use`. O par (IP, porta) já está reservado,
ou há um **`TIME_WAIT`** ocupando.

**`EADDRNOTAVAIL`** (errno 99) — acabaram as **portas efêmeras**. Sintoma de esgotamento.

**`ECONNREFUSED`** (errno 111) — `Connection refused`. Chegou um RST: a máquina existe e
ninguém escuta ali.

**ECH** — *Encrypted Client Hello*. Cifra o **SNI**, removendo a última pista de metadado
no handshake TLS. A porta continua visível.

**`EMFILE`** (errno 24) — `Too many open files`. Estourou o `ulimit -n`. Em aplicação de rede,
quase sempre são sockets, não arquivos.

**Efêmera (porta)** — porta de origem atribuída automaticamente pelo kernel. No Linux,
tipicamente `32768–60999`; o RFC 6335 define `49152–65535`.

**Egress** — tráfego de saída. Cobrado por provedores de nuvem, e um custo oculto de porta
exposta sob DDoS.

**`EXPOSE`** — instrução de Dockerfile. **É documentação; não publica porta nenhuma.**

---

## F

**Fechada (porta)** — estado em que a sondagem recebeu RST: a máquina respondeu, e não há
serviço ali.

**Filtrada (porta)** — estado em que nada voltou. Alguém descartou em silêncio. Distinguir de
**fechada** é a informação mais subestimada da varredura.

**FLP** — resultado de Fischer, Lynch e Paterson (1985): não há consenso determinístico
garantido em sistema assíncrono com uma falha. Implica que todo *health check* é um chute
calibrado.

**Flag day** — 1º de janeiro de 1983, migração da ARPANET de NCP para TCP/IP. A última
mudança incompatível bem-sucedida da internet.

---

## H

**Handshake de três vias** — SYN → SYN-ACK → ACK. Três é o mínimo para cada lado saber que
seu número de sequência inicial foi recebido. Ver **dois generais**.

**Hitlist** — lista de endereços IPv6 conhecidos, coletada passivamente. Substitui a
varredura exaustiva, inviável em IPv6.

---

## I

**IANA** — *Internet Assigned Numbers Authority*. Mantém o registro de portas. Origem: a
proposta de "um czar" no RFC 349, de Jon Postel, em 1972.

**ICMP** — protocolo de mensagens de controle. **Não tem portas** — tem tipo e código.
O tipo 3 código 3 ("port unreachable") é como se descobre porta **UDP** fechada.

**ICMPv6** — equivalente no IPv6, e **essencial**: o *Neighbor Discovery* depende dele.
Bloqueá-lo por inteiro quebra a rede. Ver RFC 4890.

**`INADDR_ANY`** — o endereço `0.0.0.0`. Escutar em **todas** as interfaces.

**i-node** — número que identifica um socket na tabela do kernel. É a única chave em
`/proc/net/tcp`; o PID precisa ser descoberto varrendo `/proc/<pid>/fd`.

**IPv4-mapeado** — `::ffff:127.0.0.1`. Um endereço IPv4 embutido em notação IPv6
(RFC 4291 §2.5.5.2). Armadilha clássica de script de auditoria.

---

## L

**`LISTEN`** — estado de um socket passivo, esperando conexões. **Não existe em UDP.**

**`listen()`** — chamada que marca o socket como passivo e define o **backlog**.

**Loopback** — todo o bloco `127.0.0.0/8` e `::1`. Tráfego que nunca sai da máquina.
**Não é só `127.0.0.1`** — o `systemd-resolved` usa `127.0.0.53`.

**`lsof`** — *list open files*. Lista descritores abertos, inclusive sockets. Único caminho
prático no macOS.

---

## M

**masscan** — scanner **sem estado**, de 2013. Usa pilha TCP/IP própria e codifica a
identidade do alvo no número de sequência inicial, o que elimina memória por sonda.

**mDNS** — *multicast DNS*, 5353/UDP. Descoberta de serviços na rede local (Bonjour, Avahi).

**MSL** — *Maximum Segment Lifetime*. Tempo máximo que um segmento pode vagar pela rede.
`TIME_WAIT` dura 2×MSL — no Linux, 60 s fixos.

**mTLS** — TLS mútuo: os dois lados apresentam certificado. Base da autorização por
identidade em **service mesh**.

---

## N

**NAT** — tradução de endereços. Reescreve IP e frequentemente **porta**. Também chamado de
PAT quando enfatiza a porta.

**Netfilter** — o subsistema de filtragem do kernel Linux. `iptables` e `nftables` são
interfaces para ele.

**Netlink** — interface binária de comunicação com o kernel. É como o `ss` obtém os dados,
e o motivo de ele ser muito mais rápido que o `netstat`.

**Network namespace** — pilha de rede isolada: interfaces, rotas, **tabela de sockets** e
firewall próprios. É o que torna um container um container, em termos de rede.

**Nmap** — scanner de portas de 1997, de Gordon Lyon. Licença **NPSL**, não GPL pura.

**NPSL** — *Nmap Public Source License*. Derivada da GPLv2 com restrições; uso comercial
embutido pode exigir licença paga.

---

## O

**`open|filtered`** — classificação do Nmap em varredura UDP quando não houve resposta.
Significa **"não foi possível determinar"**. Reportá-la como "aberta" é falso positivo.

---

## P

**PAT** — *Port Address Translation*. Nome mais preciso para o NAT que multiplexa várias
máquinas internas num IP público reescrevendo a porta de origem.

**PMTU black hole** — falha em que pacotes grandes somem porque o ICMP tipo 3 código 4 foi
bloqueado. Sintoma: conexão abre, requisições pequenas passam, grandes travam.

**Porta** — inteiro sem sinal de 16 bits (1–65535) no cabeçalho de transporte, usado para
**demultiplexar** pacotes entre sockets.

**Port knocking / SPA** — técnica de manter a porta invisível até uma sequência (ou um pacote
autenticado) liberar o acesso. Funciona; custa complexidade operacional.

**PREROUTING** — cadeia do netfilter avaliada **antes** de o pacote encontrar um socket. É
onde `DNAT` e `REDIRECT` agem, e por isso uma porta pode parecer aberta sem processo algum.

**Privilegiada (porta)** — porta abaixo de 1024. Exige privilégio no Unix por uma convenção
de ~1980. Windows nunca teve a restrição.

---

## Q

**Quádrupla** (*4-tuple*) — `(IP origem, porta origem, IP destino, porta destino)`.
Identifica uma conexão TCP. É ela, e não a porta, que precisa ser única.

**QUIC** — transporte confiável e cifrado sobre **UDP** (RFC 9000, 2021). Identifica conexões
por **connection ID**, não pela quádrupla.

---

## R

**`Recv-Q`** — coluna do `ss`. Em `LISTEN`, é a **fila de conexões prontas**. Em
`ESTABLISHED`, são bytes não lidos pela aplicação.

**REDIRECT** — ação de NAT que desvia a conexão para outra porta local. Causa comum de o
`nmap` ver portas que o `ss` não vê.

**REJECT** — ação de firewall que descarta **e avisa**. Produz "recusada" rápido. Melhor que
`DROP` dentro da rede interna, por facilitar o diagnóstico.

**Rice, teorema de** — toda propriedade não-trivial da função computada por um programa é
indecidível. Implica que não existe identificação automática perfeita de serviço.

**RST** — flag TCP de reset. Encerra ou recusa abruptamente. Produz `Connection refused`.

---

## S

**`Send-Q`** — coluna do `ss`. Em `LISTEN`, é o **backlog** efetivo. Em `ESTABLISHED`, são
bytes enviados e ainda não confirmados.

**Service mesh** — camada de proxies (Envoy) que intercepta todo o tráfego entre serviços.
Move o controle de acesso de (IP, porta) para **identidade criptográfica**.

**SCTP** — transporte com múltiplos fluxos e *multi-homing* (RFC 9260). Tem portas. Usado em
telecomunicações; não decolou fora delas porque middleboxes não o entendem.

**SNI** — *Server Name Indication*. Nome do host no handshake TLS. Visível ao observador,
exceto com **ECH**.

**Socket** — ponto final de comunicação. No Unix, um **descritor de arquivo**. API criada no
BSD 4.2, em 1983, e essencialmente inalterada desde então.

**`SO_REUSEADDR`** — opção de socket que permite `bind()` mesmo havendo um **`TIME_WAIT`** no
mesmo endereço local. Segura e recomendada em servidores.

**`SO_REUSEPORT`** (Linux 3.9, 2013) — permite **vários processos** escutando no mesmo
(IP, porta), com o kernel distribuindo. Exceção real à regra "uma porta, um dono".

**`somaxconn`** — teto do sistema para o **backlog**. O efetivo é `min(backlog, somaxconn)`.

**SYN cookies** — defesa contra SYN flood: quando a fila enche, o servidor codifica o estado
no número de sequência em vez de armazená-lo. Inventada por Dan Bernstein em 1996.

**SYN scan** (`-sS`) — varredura que manda SYN, recebe SYN-ACK e responde RST, sem completar
a conexão. Chamada de *stealth* nos anos 1990; hoje trivialmente detectável.

---

## T

**Tarpit** — serviço que responde a tudo, ou que responde muito devagar, para desperdiçar o
tempo de quem varre. Torna a varredura indistinguível de uma máquina com tudo aberto.

**`tcp_tw_recycle`** — parâmetro **REMOVIDO do kernel na versão 4.12 (2017)** por quebrar
clientes atrás de NAT. Material que ainda o recomenda é anterior a 2017.

**`tcp_tw_reuse`** — parâmetro **válido e seguro**, que permite reaproveitar sockets em
`TIME_WAIT` para conexões **de saída**. Não confundir com o anterior.

**`TIME_WAIT`** — estado de quem **fecha primeiro**. Dura 60 s no Linux (fixo em
`TCP_TIMEWAIT_LEN`). Existe para absorver pacotes atrasados e para poder retransmitir o ACK
final.

**TPROXY** — mecanismo de proxy transparente do netfilter. Como `REDIRECT`, produz portas
"abertas" sem processo escutando.

---

## U

**UDP** — transporte sem conexão, sem garantia, sem estado (RFC 768, 1980). Cabeçalho de
8 bytes. **Não existe `LISTEN` em UDP** — o estado observável é `UNCONN`.

**`ulimit -n`** — limite de descritores por processo. Em aplicação de rede, é o teto de
conexões simultâneas.

**`UNCONN`** — estado exibido pelo `ss` para sockets UDP com `bind()`.

---

## V

**VXLAN** — encapsulamento de rede em 4789/UDP, usado em nuvem e containers.

---

## X

**XDP** — *eXpress Data Path*. Ponto de gancho eBPF no driver da placa de rede, antes da
pilha do kernel. É o filtro mais rápido possível no Linux.

---

## Z

**Zero trust** — modelo em que a localização na rede não confere confiança. Cada serviço
autentica cada cliente. Move o controle de (IP, porta) para identidade.

**ZMap** — scanner sem estado publicado na USENIX Security 2013. Varre a IPv4 inteira em
dezenas de minutos.

---

## Conceitos com nome próprio

**Dois generais (paradoxo dos)** — problema provadamente insolúvel de acordo sobre um canal
não confiável. É por isso que o **handshake de três vias** é o mínimo, e por que não existe
certeza mútua absoluta em TCP.

**Cinco porquês (regra dos)** — método deste curso: perguntar "por que é assim?" até chegar
a uma lei física, uma decisão histórica documentada, um trade-off econômico explícito, ou
uma convenção declaradamente arbitrária. *"Porque o padrão define"* não é uma parada legítima.

**Small services** — portas 7 (echo), 9 (discard), 13 (daytime), 17 (QOTD) e 19 (chargen).
Propostas em 1972; hoje desligadas por padrão porque servem para **amplificação**.

**As três faixas** (RFC 6335) — System (0–1023), User (1024–49151),
Dynamic/Private (49152–65535).

**Os três desfechos** — aberta (SYN-ACK), fechada (RST), filtrada (silêncio).

**As duas visões** — de dentro (`ss`, verdade absoluta local) e de fora (`nmap`, verdade do
caminho). Quando discordam, a divergência é a informação.

---

*Voltar ao [`00-MAPA.md`](00-MAPA.md).*
