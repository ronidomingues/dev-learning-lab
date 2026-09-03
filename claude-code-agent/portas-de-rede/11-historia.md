# 11 · História — como chegamos aqui

**Nível:** intermediário · **Última atualização:** 14/08/2026
Fontes primárias (RFCs) citadas ao longo do texto e listadas em
[`95-referencias.md`](95-referencias.md). Datas verificadas na web em 14/08/2026.

---

## Por que ler história de protocolo

Porque quase tudo que é estranho em portas de rede é **arqueologia**, não engenharia.
O limite de 65 535, a restrição das portas baixas, a divergência entre a faixa efêmera do
padrão e a do Linux, o fato de a porta 80 ser HTTP — nada disso tem justificativa técnica
atual. São decisões tomadas por pessoas identificáveis, em datas identificáveis, num mundo
que não existe mais.

Saber disso muda seu comportamento profissional: você para de procurar razão técnica onde
há convenção, e para de aceitar "é assim porque o padrão diz".

---

## 1969–1971 · Antes da porta existia o *socket*

A ARPANET entrou no ar em outubro de 1969 com quatro nós. O protocolo de host a host era o
**NCP** (*Network Control Program*), e ele já tinha o problema que a porta resolve: como
mandar dados para o programa certo dentro de uma máquina.

A solução do NCP chamava-se **socket** — e era diferente do que chamamos de socket hoje.
Um socket do NCP era um número de 32 bits, e havia uma convenção peculiar: **sockets pares
eram de recepção e ímpares de envio**. Cada conexão usava um par.

- **RFC 33** (fev/1970), de Steve Crocker e outros, formaliza o protocolo host-a-host.
- **RFC 147** (mai/1971), de Joel Winett, chama-se literalmente *"The Definition of a Socket"*.

Note a data: **1971**. A ideia de "um número que identifica um destino dentro de uma máquina"
tem mais de meio século.

---

## 1972 · Jon Postel inventa o czar dos números

O problema apareceu rápido: se cada instituição escolhe seu número para o Telnet, ninguém
conecta em ninguém.

Em **30 de maio de 1972**, Jon Postel — então na UCLA — publica a
[**RFC 349, "Proposed Standard Socket Numbers"**](https://www.rfc-editor.org/rfc/rfc349).
O documento é curto e propõe duas coisas que moldaram a internet inteira:

1. **Uma tabela de números padronizados.** A alocação inicial proposta:

   | Faixa | Uso |
   |---|---|
   | 0–63 | funções padrão de toda a rede |
   | 64–127 | funções específicas do host |
   | 128–239 | reservado para o futuro |
   | 240–255 | experimental |

   E, dentro dos padrões: socket **1** para Telnet, **3** para transferência de arquivos,
   **5** para *Remote Job Entry*, **7** para Echo, **9** para Discard.

   Repare: **echo em 7 e discard em 9 sobrevivem até hoje** no `/etc/services` de qualquer
   Linux. São os números de porta mais antigos ainda em uso — 54 anos.

2. **Um czar.** Nas palavras do documento, deveria haver *"a czar"* encarregado de distribuir
   os números oficiais e de manter e publicar a lista.

Postel se tornou esse czar, e permaneceu no papel por 26 anos, até morrer em 1998. A função
que ele criou para si mesmo virou a **IANA** — *Internet Assigned Numbers Authority*. É
provavelmente o caso mais bem-sucedido de "uma pessoa mantendo um arquivo de texto" da
história da computação.

**Esta é a resposta ao "por que existe um registro de portas": porque um sujeito em 1972
propôs que existisse, e ele mesmo se ofereceu para manter.**

---

## 1973–1981 · A porta de 16 bits nasce

O NCP não escalava. Vint Cerf e Bob Kahn publicam em 1974 o trabalho que separa a entrega
de pacotes (IP) do controle de conexão (TCP). O socket de 32 bits do NCP se decompõe em
`(endereço IP, porta)` — e a palavra **porta** entra no vocabulário.

Os documentos que congelam o formato:

| Data | RFC | O quê |
|---|---|---|
| ago/1980 | **RFC 768** | UDP. Portas de origem e destino, 16 bits cada. |
| set/1981 | **RFC 791** | IP. **Não tem porta** — e nunca teve. |
| set/1981 | **RFC 793** | TCP. Portas de 16 bits, os 11 estados, o handshake de três vias. |

### Por que 16 bits — os cinco porquês

**1.** Porque o campo no cabeçalho tem 16 bits.

**2.** Por que 16 e não 32? Porque cada bit adicionado ao cabeçalho é enviado em **todo
pacote**, para sempre. Um campo de 32 bits para porta de origem e outro para destino
custaria 4 bytes a mais por pacote.

**3.** Por que 4 bytes importavam? Porque em 1980 os enlaces da ARPANET eram de **50 kbit/s**.
Um cabeçalho TCP de 20 bytes já era ~4 % de um pacote típico da época. Cada byte era
negociado.

**4.** Por que 65 536 pareceu suficiente? Porque um host da época era um mainframe rodando
talvez uma dúzia de serviços. A ideia de uma máquina precisar de dezenas de milhares de
portas simultâneas era ficção científica.

**5.** Por que não foi consertado depois? Porque mudar o tamanho do campo quebra
compatibilidade com **todo equipamento existente**. É a mesma razão pela qual o IPv4 tem
32 bits de endereço até hoje, 30 anos depois de todo mundo saber que não bastava.
O IPv6 levou de 1998 a hoje para chegar a uma adoção parcial. **Aqui paramos: é um
trade-off econômico explícito entre custo de transição e benefício.**

O aperto é real e mensurável hoje — ver [`60-teoria-avancada.md`](60-teoria-avancada.md).

---

## 1983 · Dois eventos que fixaram tudo

**1º de janeiro de 1983 — o "flag day".** A ARPANET migra do NCP para TCP/IP num único dia.
Cerca de 400 hosts. Foi caótico e funcionou. **Foi a última vez na história em que foi
possível trocar o protocolo fundamental da internet de uma só vez** — e é por isso que
nenhuma mudança incompatível conseguiu passar desde então.

**BSD 4.2 — a API de sockets.** Bill Joy e a equipe de Berkeley publicam a interface
`socket()`, `bind()`, `listen()`, `accept()`, `connect()`. A decisão de projeto genial:
**fazer um socket parecer um descritor de arquivo**, para que `read()` e `write()`
funcionassem nele.

Essa API tem 43 anos e **não mudou**. O código Python do
[projeto-modelo](07-projeto-modelo/README.md) chama as mesmas funções, com os mesmos nomes e
a mesma semântica, que um programa em C de 1983.

Poucas interfaces na computação tiveram vida tão longa. Vale perguntar por quê — e a
resposta honesta é: porque ela é boa o bastante, e porque o custo de substituí-la sempre
foi maior que o incômodo de conviver com suas asperezas (que existem: `getaddrinfo` é
horroroso, e a semântica de `close()` em socket é notoriamente sutil).

---

## 1980–1992 · A tabela cresce, e depois estoura

A faixa "bem conhecida" original era **0–255**, herdada da proposta de Postel de 1972.

Ela ficou pequena. A [**RFC 1340**](https://www.rfc-editor.org/rfc/rfc1340.html)
(julho de 1992), de Joyce Reynolds e Jon Postel, registra a mudança com a sobriedade de
sempre:

> *"For many years the assigned ports were in the range 0-255. Recently, the range for
> assigned ports managed by the IANA has been expanded to the range 0-1023."*

E ali também está escrita, em texto, a regra que gera a mensagem `Permission denied` que
você reproduziu no [`04`](04-como-comecar.md):

> *"The Well Known Ports are controlled and assigned by the IANA and on most systems can
> only be used by system (or root) processes or by programs executed by privileged users."*

Repare na formulação: *"on most systems"*. **Não é uma exigência do padrão.** É a descrição
de um comportamento de fato dos Unixes da época. O Windows nunca implementou, e não viola
padrão nenhum por isso.

### Por que o Unix restringiu as portas baixas

Contexto de 1980: uma máquina Unix era compartilhada por dezenas de pessoas — professores,
alunos, pesquisadores. Se qualquer usuário pudesse escutar na porta 25, ele poderia se passar
pelo servidor de e-mail da instituição e coletar senhas. A porta baixa virou uma **credencial
fraca de autoridade**: "quem está aqui foi autorizado pelo administrador da máquina".

Hoje a premissa evaporou. Sua máquina não é compartilhada, e ninguém, em lugar nenhum,
confia numa porta baixa como prova de coisa alguma. A restrição continua por
compatibilidade — e produz, todo dia, a decisão errada de rodar servidores como root.

O kernel Linux oferece a válvula de escape desde a versão 4.11 (2017):

```bash
sysctl net.ipv4.ip_unprivileged_port_start
```

---

## 1988–1997 · A varredura de portas vira uma coisa

### 1988 — o Morris worm

Em 2 de novembro de 1988, Robert Tappan Morris solta o primeiro worm de internet. Ele se
espalhava explorando o `fingerd` (porta 79), o `sendmail` (porta 25) e senhas fracas de
`rsh`/`rexec`. Estimativas da época falam em ~6 000 máquinas afetadas — uma fração
significativa da internet de então.

**Consequência direta:** a criação do CERT/CC, e o nascimento da ideia de que *saber quais
portas uma máquina expõe* é uma questão de segurança e não só de administração.

### 1995 — SATAN

Dan Farmer e Wietse Venema lançam o **SATAN** (*Security Administrator Tool for Analyzing
Networks*) em abril de 1995. Foi a primeira ferramenta de varredura amplamente distribuída,
e gerou pânico na imprensa — havia previsões sérias de que a internet cairia no dia do
lançamento. Não caiu.

O debate que o SATAN abriu — *"publicar ferramenta de ataque ajuda ou atrapalha a defesa?"* —
continua idêntico hoje, palavra por palavra, sobre outras ferramentas. Farmer chegou a
perder o emprego por causa do lançamento.

### 1997 — o Nmap

Em setembro de 1997, Gordon Lyon (**Fyodor**) publica o Nmap na revista *Phrack* nº 51.
Um artigo, um `.tar.gz`, ~2 000 linhas de C.

O que fez o Nmap vencer e ainda ser o padrão 29 anos depois:

1. **Catalogou e nomeou as técnicas.** SYN, FIN, Xmas, NULL, ACK, connect. O vocabulário
   de varredura que usamos hoje foi cunhado ali.
2. **Detecção de sistema operacional por impressão digital da pilha TCP/IP.** A ideia de
   que a máquina se identifica pelo *jeito* como implementa o protocolo, não pelo que ela diz.
3. **Uma base de dados curada, mantida por décadas.** `nmap-services` e
   `nmap-service-probes`. É esse acúmulo, e não o código, que constitui o fosso competitivo.

O Nmap está na sua máquina agora. Rode `nmap --version` e olhe a data.

---

## 2003–2017 · As portas em manchete

| Ano | Evento | Porta | Lição |
|---|---|---|---|
| **2003** | SQL Slammer: infecta a internet em ~10 minutos | **1434/UDP** | Um único datagrama UDP de 376 bytes. Sem handshake, a propagação é limitada só pela banda. |
| **2003** | Blaster | 135/TCP | RPC da Microsoft exposto à internet por padrão |
| **2008** | Conficker | 445/TCP | SMB. Milhões de máquinas |
| **2016** | Mirai | **23/TCP** (Telnet) | Câmeras e roteadores com senha padrão. Telnet, em 2016. |
| **2017** | WannaCry / NotPetya | **445/TCP** | SMB de novo. Bilhões de dólares em prejuízo |
| **2018** | Amplificação memcached | **11211/UDP** | Ataque de 1,35 Tbit/s contra o GitHub. Fator de amplificação ~51 000× |

**O padrão que atravessa todos:** nenhum deles precisou de uma falha desconhecida na porta.
Todos precisaram de uma porta **acessível de onde não deveria ser**. A palavra que descreve
a causa-raiz de cada linha dessa tabela é *exposição*, não *vulnerabilidade*.

O memcached de 2018 merece nota: o serviço respondia a UDP por padrão, e uma consulta de
15 bytes gerava resposta de até 750 KB. Após o incidente, o projeto desabilitou UDP por
padrão. Foi uma correção de **configuração padrão**, não de código — e é o exemplo canônico
de que padrões inseguros são falhas de projeto.

---

## 2011 · O regime atual

A [**RFC 6335**](https://www.rfc-editor.org/rfc/rfc6335.html) (agosto de 2011) — de Cotton,
Eggert, Touch, Westerlund e Cheshire — é o documento que rege o registro hoje. Ela:

- consolidou as três faixas: **System (0–1023)**, **User (1024–49151)**,
  **Dynamic/Private (49152–65535)**;
- unificou o registro de **nomes de serviço** com o de números;
- e, o mais importante na prática, **desencorajou explicitamente novas atribuições**.

Esse último ponto é uma mudança de filosofia. A IANA passou a dizer, em essência: *"pare de
pedir números; use o DNS-SD, use SRV records, negocie a porta em vez de codificá-la"*.
A razão é aritmética — 49 151 portas de usuário, e uma indústria de software que cresce mais
rápido do que isso.

Na prática, a indústria ignorou. Ninguém registra a porta 3000, 5000, 8000 ou 8080, e todo
mundo as usa.

---

## 2012–2026 · QUIC muda o jogo

O Google começa a experimentar o **QUIC** por volta de 2012–2013: um transporte novo, sobre
UDP, com criptografia obrigatória e multiplexação sem bloqueio de cabeça de fila.

- **RFC 9000** (maio/2021) — QUIC padronizado pelo IETF.
- **RFC 9114** (junho/2022) — HTTP/3, que roda sobre QUIC.

**O impacto no nosso assunto é grande e pouco discutido:**

1. **A porta 443/UDP passou a importar.** Firewalls que liberavam "443" pensando em TCP
   passaram a bloquear HTTP/3 sem querer. É um dos motivos de a adoção ser desigual.

2. **A visibilidade caiu.** Em TCP+TLS, um observador na rede vê o handshake TCP e o SNI
   em claro no `ClientHello`. Em QUIC, quase tudo é cifrado desde o primeiro pacote —
   inclusive parte do que antes era metadado.

3. **Varredura ficou mais difícil.** Não há SYN-ACK. Não há estado no meio. Descobrir um
   serviço QUIC exige falar QUIC.

**Números de adoção, agosto de 2026** — e as fontes discordam de propósito, porque medem
coisas diferentes:

| Fonte | Métrica | Valor |
|---|---|---|
| W3Techs | Sites que **suportam** HTTP/3 | ~39 % |
| Cloudflare | Tráfego na borda deles | ~35 % |
| TechnologyChecker | **Carregamentos de página** servidos por HTTP/3 | ~21 % |

*Suportar* e *ser usado* são coisas diferentes; a diferença entre 39 % e 21 % é
principalmente essa. Sempre pergunte qual é o denominador.

O maior obstáculo apontado nas fontes de 2026 é justamente o nosso assunto: **proxies
corporativos que não deixam passar UDP na 443**.

---

## Linha do tempo

```
1969  ARPANET no ar. NCP. "Sockets" de 32 bits, pares e ímpares.
1971  RFC 147 — "The Definition of a Socket"
1972  RFC 349 — Postel propõe números padrão E propõe um "czar". Nasce a IANA.
      Telnet=1, FTP=3, Echo=7, Discard=9.  ← Echo e Discard sobrevivem até hoje
1974  Cerf & Kahn separam TCP de IP. O socket vira (IP, porta).
1980  RFC 768 — UDP. Portas de 16 bits.
1981  RFC 793 — TCP. 16 bits, 11 estados, handshake de 3 vias.
1983  Flag day: NCP → TCP/IP. BSD 4.2 publica a API de sockets. ← inalterada desde então
1988  Morris worm (fingerd/79, sendmail/25). Nasce o CERT.
1992  RFC 1340 — faixa "well-known" vai de 0–255 para 0–1023.
1995  SATAN. O debate sobre publicar ferramenta de varredura.
1997  Nmap, na Phrack 51. Nomeia as técnicas de varredura.
2003  SQL Slammer (1434/UDP): internet infectada em ~10 min.
2011  RFC 6335 — as três faixas atuais. IANA desencoraja novas atribuições.
      RFC 6056 — aleatorização de porta efêmera vira exigência de segurança.
2013  ZMap e masscan: a internet inteira varrida em minutos.
2017  WannaCry (445/TCP). Kernel Linux 4.12 REMOVE tcp_tw_recycle.
2021  RFC 9000 — QUIC. 443/UDP passa a ser um serviço de verdade.
2022  RFC 9114 — HTTP/3.
2026  HTTP/3 entre 21 % e 39 % conforme a métrica. Proxies corporativos são o gargalo.
```

---

## O que a história ensina, em três frases

1. **Quase todo número de porta é arbitrário.** Foi escolhido por alguém, num dia, porque
   estava livre. Procurar significado técnico é perder tempo.

2. **Nada incompatível passa depois de 1983.** O flag day foi a última janela. É por isso
   que convivemos com 16 bits, com portas privilegiadas e com IPv4 — e é por isso que o
   QUIC teve de ser construído **por cima** do UDP em vez de ser um transporte novo de
   verdade: só passa o que se disfarça de algo que já é permitido.

3. **Todo desastre desta tabela foi de exposição, não de porta.** Nenhum atacante "abriu"
   nada. Eles encontraram aberto.

---

## Autoteste

1. Quem propôs a existência de um registro central de números de porta, quando, e em que
   documento? Que cargo esse documento inventou?
2. Duas portas propostas em 1972 continuam no `/etc/services` do seu Linux hoje. Quais são?
3. Por que o campo de porta tem 16 bits? Leve a resposta até uma decisão econômica, não pare
   no "porque o RFC diz".
4. A restrição de porta < 1024 aparece em qual documento, e com que redação? Por que a
   formulação dele significa que o Windows não viola padrão nenhum ao ignorá-la?
5. O que o "flag day" de 1º de janeiro de 1983 tem a ver com o fato de o QUIC rodar sobre
   UDP em vez de ser um protocolo de transporte novo?
6. O que Slammer, WannaCry e Mirai têm em comum quanto à causa-raiz? O que isso sugere sobre
   onde investir esforço de defesa?
7. Três fontes reportam adoção de HTTP/3 em 39 %, 35 % e 21 % em 2026. Elas se contradizem?
   O que explica a diferença?
8. Por que a RFC 6335 desencoraja novas atribuições de porta, e por que a indústria a ignora?

---

*Próximo: [`12-onde-a-porta-vive.md`](12-onde-a-porta-vive.md) — a pilha, camada a camada.*
