# 90 · Bibliografia comentada

**Nível:** todos · **Última atualização:** 14/08/2026
Edições e disponibilidade gratuita conferidas na web em 14/08/2026. Onde houver incerteza
sobre edição ou tradução, está dito. **Nenhum ISBN foi inventado** — quando não há certeza,
citamos apenas autor, título e editora.

---

## Como usar esta lista

Portas de rede não têm um livro próprio — o assunto é um capítulo de redes e um capítulo de
segurança. A lista abaixo está ordenada por **o que você quer fazer**, não por importância
abstrata.

| Você quer… | Comece por |
|---|---|
| Entender redes do zero | Kurose & Ross |
| Entender o TCP a fundo | Fall & Stevens (*TCP/IP Illustrated*) |
| **Programar sockets** | Beej's Guide (**gratuito**) → Stevens (*UNP*) |
| Varrer e auditar | Lyon (*Nmap Network Scanning*) — **metade gratuita** |
| Entender o kernel Linux | Benvenuti / Rosen |
| Desempenho e observabilidade | Gregg |
| Ler sem gastar nada | Beej, Peterson & Davie, Kozierok, RFCs |

---

## 1. Redes — os livros-texto

### Kurose, James F.; Ross, Keith W. — *Computer Networking: A Top-Down Approach*
**Pearson · 9ª edição, setembro de 2025** *(edição confirmada na web em 14/08/2026)*

**Nível:** iniciante a intermediário.

**O que faz melhor que os outros:** a abordagem "de cima para baixo" — começa pela aplicação
(HTTP, que você já conhece) e desce até os bits. Para o nosso assunto, isso é ideal: você vê
a porta aparecer no capítulo de camada de transporte já sabendo por que ela é necessária.

**Novidades da 9ª edição** que importam aqui: cobertura de **HTTP/3 e QUIC**, Wi-Fi 6, 5G, e
discussão atualizada de segurança. É a razão de preferir a 9ª à 8ª.

**Em português:** existe tradução da Pearson Brasil (*Redes de Computadores e a Internet:
uma abordagem top-down*), historicamente de boa qualidade. **A tradução da 9ª edição pode
ainda não ter saído** — confirme antes de comprar. Se só houver a 8ª em português, ela
continua excelente, faltando QUIC.

**Preço (14/08/2026):** eTextbook Pearson+ ~US$ 64,98 (≈ R$ 337) com acesso vitalício;
impresso ~US$ 193 (≈ R$ 1.002). **Não é gratuito.**

**Onde não basta:** é um livro-texto de graduação. Não te ensina a operar, diagnosticar nem
usar ferramenta.

---

### Peterson, Larry L.; Davie, Bruce S. — *Computer Networks: A Systems Approach*
**Morgan Kaufmann · e uma edição aberta mantida em [systemsapproach.org](https://book.systemsapproach.org/)**

**Nível:** intermediário. **✅ Legalmente gratuito** na versão aberta.

**O que faz melhor:** perspectiva de **projeto de sistemas** — por que os protocolos são como
são, quais trade-offs foram feitos. Complementa Kurose em vez de competir.

**Recomendação:** se você não vai gastar dinheiro, **este é o seu livro-texto de redes**.
A versão aberta é mantida pelos autores e atualizada.

---

### Tanenbaum, Andrew S.; Feamster, Nick; Wetherall, David — *Computer Networks*
**Pearson · 6ª edição, 2021**

**Nível:** intermediário. **Em português:** *Redes de Computadores*, Pearson Brasil.

**O que faz melhor:** a escrita do Tanenbaum. Denso, com senso de humor, e forte na parte
baixa da pilha (enlace, físico), onde o Kurose é mais leve.

**Envelheceu?** Parcialmente. É "de baixo para cima", o que é menos didático para quem começa
hoje. A 6ª edição atualizou bastante, mas o livro carrega décadas de estrutura.

---

## 2. TCP/IP — a fonte

### Fall, Kevin R.; Stevens, W. Richard — *TCP/IP Illustrated, Volume 1: The Protocols*
**Addison-Wesley · 2ª edição, 2011**

**Nível:** avançado. **É o livro definitivo sobre o TCP.**

**O que faz melhor que todo o resto:** ele **mostra os pacotes**. Cada afirmação vem
acompanhada de uma captura real, decodificada campo a campo. O
[`13-tcp-por-dentro.md`](13-tcp-por-dentro.md) deste curso é uma versão condensada do que
esse livro faz em 200 páginas — com muito mais rigor.

**Se você só ler um livro deste assunto na vida, leia este.**

**Envelheceu?** A 2ª edição é de 2011, então **não tem QUIC nem HTTP/3**. Mas o TCP em si não
mudou: tudo que ele diz sobre handshake, estados, `TIME_WAIT`, janelas e retransmissão
continua exato em 2026. É a definição de clássico que continua valendo.

**Em português:** houve tradução do volume 1 da 1ª edição (Stevens sozinho, 1994). Da 2ª
edição, **não temos confirmação de tradução** — trate como provavelmente inexistente.

⚠️ **Sobre o Volume 2** (implementação) e o **Volume 3**: são de 1995–96 e descrevem código
BSD daquela época. Valor hoje é histórico. Não comece por eles.

---

### Kozierok, Charles M. — *The TCP/IP Guide*
**No Starch Press, 2005 · e [tcpipguide.com](http://www.tcpipguide.com/free/) ✅ gratuito online**

**Nível:** iniciante a intermediário.

**O que faz melhor:** cobertura exaustiva e didática, com diagramas. A versão online é
gratuita e completa.

**Envelheceu?** É de 2005. Sem QUIC, sem IPv6 moderno, sem TLS 1.3. Mas para entender
**portas, TCP e UDP** — que não mudaram — continua excelente e é grátis.

---

## 3. Programação de sockets

### Hall, Brian "Beej" — *Beej's Guide to Network Programming*
**[beej.us/guide/bgnet](https://beej.us/guide/bgnet/) · ✅ totalmente gratuito, atualizado**

**Nível:** iniciante a intermediário.

**A melhor recomendação desta página inteira em relação custo-benefício** — porque o custo
é zero e a qualidade é alta.

**O que faz melhor:** explica `socket()`, `bind()`, `listen()`, `accept()`, `connect()` com
clareza, humor e código completo. Depois de lê-lo, o
[`10-fundamentos.md`](10-fundamentos.md) e o [`15-sockets-e-o-kernel.md`](15-sockets-e-o-kernel.md)
deste curso viram consequência óbvia.

**Onde não basta:** é em C, e não cobre desempenho em escala.

---

### Stevens, W. Richard; Fenner, Bill; Rudoff, Andrew M. — *UNIX Network Programming, Vol. 1: The Sockets Networking API*
**Addison-Wesley · 3ª edição, 2003**

**Nível:** avançado. **É a referência definitiva da API de sockets.**

**Envelheceu?** A API **não mudou** — é a mesma de 1983. O que falta: `epoll` moderno,
`io_uring`, `SO_REUSEPORT` (que é de 2013). Ou seja: os fundamentos estão perfeitos, os
capítulos de desempenho estão datados.

**Opinião:** compre usado. É caro novo e você vai consultá-lo, não lê-lo de capa a capa.

---

## 4. Varredura e segurança

### Lyon, Gordon "Fyodor" — *Nmap Network Scanning*
**Nmap Project, 2009 · ✅ [cerca de metade do livro está online, legalmente gratuita](https://nmap.org/book/)**

**Nível:** intermediário a avançado.

**O que faz melhor:** é escrito **pelo autor do Nmap**. Explica não só como usar cada
técnica, mas por que ela funciona, o que ela prova, e onde ela mente. Os capítulos sobre
tipos de varredura e sobre detecção de sistema operacional não têm equivalente em lugar
nenhum.

**Envelheceu?** É de 2009. As flags e conceitos centrais continuam válidos; faltam os
recursos posteriores (NSE evoluiu muito, IPv6, novas técnicas). **A referência sempre atual
é o [Nmap Reference Guide](https://nmap.org/book/man.html) online, gratuito.**

**Recomendação:** leia os capítulos gratuitos. Se você trabalha com segurança, compre o livro.

---

### Sanders, Chris — *Practical Packet Analysis*
**No Starch Press · 4ª edição (verifique a edição corrente antes de comprar)**

**Nível:** iniciante a intermediário.

**O que faz melhor:** ensina Wireshark a partir de problemas reais. É o caminho prático para
transformar o [`13-tcp-por-dentro.md`](13-tcp-por-dentro.md) em habilidade.

---

### Kim, Peter — *The Hacker Playbook 3* · e outros de pentest
Ver [`ethical-hacking`](../ethical-hacking/00-MAPA.md) nesta pasta, que tem uma bibliografia
dedicada e mais atual para segurança ofensiva.

---

## 5. Kernel Linux e desempenho

### Benvenuti, Christian — *Understanding Linux Network Internals*
**O'Reilly, 2005**

**Nível:** pesquisa.

**O que faz:** percorre o código da pilha de rede do Linux, estrutura por estrutura. É onde
você entende de verdade o que acontece entre o pacote chegar e o socket receber.

**Envelheceu?** **Bastante** — descreve o kernel 2.6. Estruturas mudaram, o netfilter mudou,
o eBPF nem existia. Ainda assim, os **conceitos** (caminho do pacote, `sk_buff`, filas)
continuam válidos, e não há substituto moderno de qualidade equivalente. Leia sabendo disso.

---

### Rosen, Rami — *Linux Kernel Networking: Implementation and Theory*
**Apress, 2013**

**Nível:** pesquisa. Mais recente que o Benvenuti (kernel 3.x), estrutura parecida.
Mesma ressalva de idade, menos acentuada.

---

### Gregg, Brendan — *BPF Performance Tools* (Addison-Wesley, 2019) e *Systems Performance* (2ª ed., 2020)

**Nível:** avançado.

**Por que estão aqui:** são a ponte entre "eu sei o que é uma porta" e "eu sei diagnosticar
um sistema de produção". O *BPF Performance Tools* é a referência do ferramental de eBPF
citado no [`65-estado-da-arte.md`](65-estado-da-arte.md) — `tcpconnect`, `tcpaccept`,
`tcplife`, `tcpretrans`.

**Envelheceu?** O eBPF evolui rápido, então detalhes de API mudaram desde 2019. A
**metodologia** não envelheceu, e é ela que vale.

---

## 6. Clássicos que continuam valendo × livros datados

| Continua valendo | Por quê |
|---|---|
| Fall & Stevens, *TCP/IP Illustrated v1* (2011) | O TCP não mudou |
| Stevens, *UNP v1* (2003) | A API de sockets não mudou |
| Beej's Guide (atualizado) | Idem, e é grátis |
| Lyon, *Nmap* (2009) | Os conceitos de varredura não mudaram |
| Kozierok (2005) | Fundamentos de TCP/UDP |

| Datado | Por quê |
|---|---|
| *TCP/IP Illustrated* v2 e v3 (1995–96) | Código BSD de 1995 |
| Benvenuti (2005) | Kernel 2.6 |
| Qualquer coisa que recomende `tcp_tw_recycle` | Removido do kernel em 2017 |
| Qualquer coisa que ensine só `netstat` no Linux | `ss` é o padrão há uma década |
| Qualquer coisa anterior a 2021 sobre "a porta 443" | Não incorporou QUIC/HTTP/3 |

---

## 7. Leitura mínima gratuita — o caminho de custo zero

Se você não vai gastar nada, esta sequência entrega mais que a maioria dos cursos pagos:

```
1. Beej's Guide to Network Programming          (grátis, ~8 h)
2. Peterson & Davie, edição aberta               (grátis, ~30 h)
3. Nmap Book — capítulos gratuitos               (grátis, ~10 h)
4. Kozierok, The TCP/IP Guide online             (grátis, consulta)
5. RFC 9293 (TCP consolidado, 2022)              (grátis, ~4 h)
6. Este curso, com os laboratórios do `70`       (grátis)
```

**Total: R$ 0** e cerca de 60 horas até um nível que muita gente não alcança pagando.

---

## Autoteste

1. Qual livro desta lista você compraria se pudesse comprar **um só**, e por quê?
2. Um livro de 2011 sobre TCP ainda vale em 2026. Por quê? Qual parte dele **não** vale?
3. Qual é o melhor recurso **gratuito** para aprender a API de sockets?
4. Você quer entender varredura de portas a fundo, sem gastar. O que lê, e onde está?
5. Por que o *TCP/IP Illustrated* volumes 2 e 3 não valem o tempo hoje, se o volume 1 vale?
6. Monte uma trilha de leitura de custo zero para os próximos dois meses.

---

*Próximo: [`95-referencias.md`](95-referencias.md) — RFCs, specs e fontes primárias.*
