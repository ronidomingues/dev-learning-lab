# 95 · Referências — specs, RFCs, código-fonte e pessoas

**Nível:** todos · **Última atualização:** 14/08/2026
Links verificados em 14/08/2026. Todos os RFCs são gratuitos, permanentes e canônicos.

---

## 1. O registro oficial de portas

**[IANA — Service Name and Transport Protocol Port Number Registry](https://www.iana.org/assignments/service-names-port-numbers)**

A fonte da verdade. Atualizado pela IANA em **11/08/2026**, conforme consultado em 14/08/2026.
Disponível em CSV, XML e HTML.

| Recurso | Link |
|---|---|
| Registro completo (CSV) | [service-names-port-numbers.csv](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.csv) |
| Formulário de solicitação | [iana.org/form/ports-services](https://www.iana.org/form/ports-services) |
| Números de protocolo IP (o campo `protocol`) | [protocol-numbers](https://www.iana.org/assignments/protocol-numbers) |
| Tipos e códigos ICMP | [icmp-parameters](https://www.iana.org/assignments/icmp-parameters) |

**Sua cópia local:** `/etc/services` — nesta máquina, 361 linhas contra milhares no registro
da IANA. É um recorte curado pela distribuição, não o registro inteiro.

---

## 2. RFCs fundamentais

### O núcleo — leia estes

| RFC | Ano | Título | Por que importa |
|---|---|---|---|
| **[768](https://www.rfc-editor.org/rfc/rfc768)** | 1980 | User Datagram Protocol | **Três páginas.** Leia inteiro hoje |
| **[791](https://www.rfc-editor.org/rfc/rfc791)** | 1981 | Internet Protocol | O IP. **Sem portas** |
| **[793](https://www.rfc-editor.org/rfc/rfc793)** | 1981 | Transmission Control Protocol | O original. Estados, handshake, portas |
| **[9293](https://www.rfc-editor.org/rfc/rfc9293)** | 2022 | TCP (consolidado) | **Substitui o 793.** É o que você deve citar hoje |
| **[6335](https://www.rfc-editor.org/rfc/rfc6335)** | 2011 | Procedimentos da IANA para portas | Define as três faixas atuais |

**Sobre o RFC 9293:** ele consolidou o RFC 793 e ~20 documentos de errata e extensão em um
texto único, em 2022. Se você for citar "o RFC do TCP" num documento profissional, cite o
9293. O 793 continua sendo a referência histórica.

### Portas, segurança e comportamento

| RFC | Ano | Assunto |
|---|---|---|
| [6056](https://www.rfc-editor.org/rfc/rfc6056) | 2011 | **Aleatorização de porta de origem.** Os cinco algoritmos |
| [5961](https://www.rfc-editor.org/rfc/rfc5961) | 2010 | Endurecimento do TCP contra ataques cegos (o caso BGP) |
| [1337](https://www.rfc-editor.org/rfc/rfc1337) | 1992 | *TIME-WAIT Assassination Hazards* — por que o TIME_WAIT existe |
| [6191](https://www.rfc-editor.org/rfc/rfc6191) | 2011 | Reduzir o TIME_WAIT com timestamps |
| [2827](https://www.rfc-editor.org/rfc/rfc2827) | 2000 | **BCP 38** — filtragem de origem contra amplificação |
| [1812](https://www.rfc-editor.org/rfc/rfc1812) | 1995 | Requisitos de roteadores; limite de taxa de ICMP |
| [4890](https://www.rfc-editor.org/rfc/rfc4890) | 2007 | **O que se pode filtrar de ICMPv6 sem quebrar a rede** |

### Transporte moderno

| RFC | Ano | Assunto |
|---|---|---|
| [9000](https://www.rfc-editor.org/rfc/rfc9000) | 2021 | **QUIC** |
| [9001](https://www.rfc-editor.org/rfc/rfc9001) | 2021 | QUIC + TLS |
| [9114](https://www.rfc-editor.org/rfc/rfc9114) | 2022 | **HTTP/3** |
| [9260](https://www.rfc-editor.org/rfc/rfc9260) | 2022 | SCTP (consolidado) |
| [4340](https://www.rfc-editor.org/rfc/rfc4340) | 2006 | DCCP |
| [8446](https://www.rfc-editor.org/rfc/rfc8446) | 2018 | TLS 1.3 |

### E-mail, endereçamento e outros

| RFC | Ano | Assunto |
|---|---|---|
| [6409](https://www.rfc-editor.org/rfc/rfc6409) | 2011 | Submissão de e-mail (**por que 587**) |
| [8314](https://www.rfc-editor.org/rfc/rfc8314) | 2018 | TLS implícito em e-mail (**por que 465 voltou**) |
| [4291](https://www.rfc-editor.org/rfc/rfc4291) | 2006 | Arquitetura de endereços IPv6 (**`::ffff:` em §2.5.5.2**) |
| [1918](https://www.rfc-editor.org/rfc/rfc1918) | 1996 | Faixas privadas |
| [6598](https://www.rfc-editor.org/rfc/rfc6598) | 2012 | **CGNAT** — `100.64.0.0/10` |
| [3022](https://www.rfc-editor.org/rfc/rfc3022) | 2001 | NAT tradicional |

### Os documentos históricos

| RFC | Data | Por que ler |
|---|---|---|
| **[349](https://www.rfc-editor.org/rfc/rfc349)** | **30/05/1972** | **Postel propõe números padrão e "um czar".** Nasce a IANA. Telnet=1, Echo=7, Discard=9 |
| [147](https://www.rfc-editor.org/rfc/rfc147) | 1971 | *The Definition of a Socket* |
| [433](https://www.rfc-editor.org/rfc/rfc433) | 1972 | *Socket Number List* — a primeira tabela |
| **[1340](https://www.rfc-editor.org/rfc/rfc1340)** | 07/1992 | **Expande "well-known" de 0–255 para 0–1023** e descreve a restrição de privilégio |
| [1700](https://www.rfc-editor.org/rfc/rfc1700) | 1994 | *Assigned Numbers* — o último em papel |
| [3232](https://www.rfc-editor.org/rfc/rfc3232) | 2002 | Substitui o 1700 por uma base online |

**O RFC 349 é curto e vale ler na íntegra.** São duas páginas onde uma pessoa propõe uma
instituição que existe até hoje.

---

## 3. Código-fonte — a verdade final

### Kernel Linux

| Arquivo | O que contém |
|---|---|
| [`include/net/tcp_states.h`](https://github.com/torvalds/linux/blob/master/include/net/tcp_states.h) | **A enumeração dos 12 estados TCP** |
| [`include/net/tcp.h`](https://github.com/torvalds/linux/blob/master/include/net/tcp.h) | `TCP_TIMEWAIT_LEN` — os 60 s fixos |
| [`net/ipv4/tcp_ipv4.c`](https://github.com/torvalds/linux/blob/master/net/ipv4/tcp_ipv4.c) | Onde `/proc/net/tcp` é gerado |
| [`net/ipv4/inet_connection_sock.c`](https://github.com/torvalds/linux/blob/master/net/ipv4/inet_connection_sock.c) | Escolha de porta efêmera |
| [`Documentation/networking/ip-sysctl.rst`](https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt) | **Todo `sysctl` de rede, documentado** |

**A `ip-sysctl` é a referência que resolve discussões.** Quando alguém afirmar o que um
parâmetro faz, é ali que se confere.

### Ferramentas

| Projeto | Repositório |
|---|---|
| iproute2 (`ss`) | [git.kernel.org/pub/scm/network/iproute2](https://git.kernel.org/pub/scm/network/iproute2/iproute2.git) |
| Nmap | [github.com/nmap/nmap](https://github.com/nmap/nmap) |
| `nmap-service-probes` | [github.com/nmap/nmap/blob/master/nmap-service-probes](https://github.com/nmap/nmap/blob/master/nmap-service-probes) |
| masscan | [github.com/robertdavidgraham/masscan](https://github.com/robertdavidgraham/masscan) |
| ZMap | [github.com/zmap/zmap](https://github.com/zmap/zmap) |
| RustScan | [github.com/bee-san/RustScan](https://github.com/bee-san/RustScan) |
| naabu | [github.com/projectdiscovery/naabu](https://github.com/projectdiscovery/naabu) |
| BCC (eBPF) | [github.com/iovisor/bcc](https://github.com/iovisor/bcc) |
| Wireshark | [gitlab.com/wireshark/wireshark](https://gitlab.com/wireshark/wireshark) |

**O `nmap-service-probes` merece uma visita.** É o arquivo que contém 25 anos de curadoria
de sondas e expressões regulares. Abri-lo mostra, melhor que qualquer texto, o que realmente
custa construir um identificador de serviços.

---

## 4. Papers e trabalhos seminais

| Trabalho | Ano | Por que importa |
|---|---|---|
| Cerf & Kahn, *A Protocol for Packet Network Intercommunication* | 1974 | O paper que separa TCP de IP |
| Fischer, Lynch, Paterson, *Impossibility of Distributed Consensus with One Faulty Process* | 1985 | **FLP.** Por que health check é sempre um chute |
| Durumeric, Wustrow, Halderman, *ZMap: Fast Internet-Wide Scanning* — USENIX Security | **2013** | **A internet varrida em minutos.** Muda modelagem de ameaça |
| Bernstein, SYN cookies | 1996 | A defesa contra SYN flood |
| Kaminsky, envenenamento de cache DNS | 2008 | Por que a porta de origem precisa ser aleatória |
| Langner, *Stuxnet* | 2011–13 | Análise do ataque a CLPs Siemens (porta 102) |

---

## 5. Documentação oficial das ferramentas

| Ferramenta | Documentação |
|---|---|
| **`ss`** | `man ss` · [manpages.debian.org/ss](https://manpages.debian.org/) |
| **`nmap`** | [nmap.org/book/man.html](https://nmap.org/book/man.html) — **a referência canônica** |
| **`lsof`** | `man lsof` (é longo e vale) |
| `tcpdump` | [tcpdump.org/manpages](https://www.tcpdump.org/manpages/tcpdump.1.html) |
| Filtros pcap | [pcap-filter(7)](https://www.tcpdump.org/manpages/pcap-filter.7.html) |
| `nftables` | [wiki.nftables.org](https://wiki.nftables.org/) |
| Wireshark | [wireshark.org/docs](https://www.wireshark.org/docs/) |
| PowerShell NetTCPIP | [learn.microsoft.com/powershell/module/nettcpip](https://learn.microsoft.com/powershell/module/nettcpip/) |
| Docker networking | [docs.docker.com/network](https://docs.docker.com/network/) |
| Kubernetes Services | [kubernetes.io/docs/concepts/services-networking](https://kubernetes.io/docs/concepts/services-networking/service/) |
| Npcap | [npcap.com](https://npcap.com/) |

---

## 6. Serviços e dados públicos

| Serviço | Para quê |
|---|---|
| [scanme.nmap.org](http://scanme.nmap.org/) | **Alvo autorizado** para praticar varredura |
| [shodan.io](https://www.shodan.io/) | Índice da internet exposta |
| [search.censys.io](https://search.censys.io/) | Idem, com foco em certificados |
| [crt.sh](https://crt.sh/) | Certificate Transparency — **gratuito** |
| [Google IPv6 statistics](https://www.google.com/intl/en/ipv6/statistics.html) | Adoção de IPv6 |
| [Cloudflare Radar](https://radar.cloudflare.com/) | Tráfego, HTTP/3, protocolos |
| [Internet Society Pulse](https://pulse.internetsociety.org/) | Métricas de saúde da internet |
| [W3Techs](https://w3techs.com/) | Adoção de tecnologias web |

---

## 7. Pessoas e organizações a acompanhar

| Quem | Por quê |
|---|---|
| **Gordon Lyon (Fyodor)** | Autor do Nmap. [nmap.org](https://nmap.org/) |
| **Brendan Gregg** | Desempenho e eBPF. [brendangregg.com](https://www.brendangregg.com/) |
| **Robert Graham** | Autor do masscan. [Errata Security](https://blog.erratasec.com/) |
| **Zakir Durumeric** | ZMap, Censys, varredura em escala |
| **Chris Greer** | Análise de pacotes ([YouTube](https://www.youtube.com/@ChrisGreer)) |
| **Cloudflare Blog** | [blog.cloudflare.com](https://blog.cloudflare.com/) — QUIC, DDoS, dados de escala |
| **APNIC Blog** | [blog.apnic.net](https://blog.apnic.net/) — medição de internet, IPv6 |
| **IETF TSVWG** | O grupo de trabalho de transporte |
| **eBPF Foundation** | [ebpf.foundation](https://ebpf.foundation/) |

---

## 8. Como as afirmações deste curso foram verificadas

Para que você possa auditar este material:

**Executado localmente** — Ubuntu 22.04.5 LTS, kernel 6.8.0-136-generic, x86_64, 14/08/2026:

| O quê | Como |
|---|---|
| `ss` em todas as formas do `05` | Executado; saídas reais |
| `/proc/net/tcp` e `/proc/net/udp` | Lidos e decodificados à mão, conferidos contra `ss` |
| `nmap -sT -Pn 127.0.0.1` | Executado (Nmap 7.80) |
| A divergência `ss` × `nmap` | Reproduzida e investigada; **causa não confirmada, e dito** |
| `bind()` em porta 0, ocupada e <1024 | As três mensagens de erro são literais |
| UDP para porta fechada → `ECONNREFUSED` | Executado |
| `TIME_WAIT` e `SO_REUSEADDR` | Executado; saída real |
| Backlog: `listen(2)` aceita 3 | Executado e medido |
| Banners de Apache e MySQL | Capturados de verdade |
| `getservbyname` / `getservbyport` | Executado |
| Faixa efêmera `32768-60999` | Lida de `/proc` |
| Projeto-modelo: **41 testes** | Executados, todos passando |

**Pesquisado na web em 14/08/2026** (com fonte citada no arquivo correspondente):
versões de Nmap, Npcap e Wireshark; registro da IANA; adoção de HTTP/3 e de IPv6; preços de
Shodan, Censys e certificações; cursos em PT/EN/FR; edições de livros; câmbio USD/BRL.

**Declaradamente NÃO executado:** comandos de macOS e Windows (sem essas máquinas);
`nmap -sS`, `-sU`, `-O` (exigem root); `tcpdump` (idem); regras de `iptables`/`nft`;
Docker e Kubernetes (indisponíveis); eBPF/`bpftrace` (exige root); varredura de alvo externo
(por escolha).

---

## Autoteste

1. Qual RFC você deve citar hoje ao referenciar "o padrão do TCP", e por que não o 793?
2. Onde está definido que a faixa efêmera é 49152–65535, e por que o Linux não a segue?
3. Que RFC explica por que `::ffff:127.0.0.1` existe, e em qual seção?
4. Onde, no código-fonte do kernel, está a constante que fixa o `TIME_WAIT` em 60 s?
5. Qual arquivo do Nmap contém as sondas de identificação de serviço, e por que ele é o
   verdadeiro diferencial do projeto?
6. Cite o trabalho de 2013 que mudou permanentemente a modelagem de ameaça em relação a
   portas expostas, e explique o que ele demonstrou.
7. Que documento diz quais tipos de ICMPv6 podem ser filtrados sem quebrar a rede?

---

*Próximo: [`GLOSSARIO.md`](GLOSSARIO.md).*
