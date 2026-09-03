# 90 · Bibliografia comentada

> **Nível:** todos
> **Data:** 14/08/2026
> Livros reais, com edição e por que ler. **Nada inventado** — onde não tenho certeza de um
> ISBN, cito só autor, título e editora. ARP é sempre um capítulo, nunca um livro; indico o
> **capítulo/tema** relevante em cada obra.

---

## 1. Os dois clássicos de redes (leia um destes primeiro)

### Kurose & Ross — *Redes de Computadores e a Internet: uma abordagem top-down*
- **Autores:** James F. Kurose, Keith W. Ross · **Editora:** Pearson · **Edição:** 8ª (2021, orig.
  em inglês; edições em PT-BR existem, geralmente uma atrás).
- **Nível:** iniciante → intermediário. **O melhor primeiro livro de redes.**
- **ARP onde:** capítulo de camada de enlace (cap. 6 na 7ª/8ª ed.) — ARP, endereçamento MAC,
  Ethernet, switches. Explicação clara e didática, alinhada ao [10](10-fundamentos.md)/[13](13-o-ciclo-de-resolucao.md).
- **Por que ler:** a abordagem *top-down* (da aplicação para o fio) faz o ARP fazer sentido no
  contexto certo. **Não envelheceu** — os fundamentos são estáveis.
- **PT-BR:** tradução boa e amplamente usada em cursos brasileiros.

### Tanenbaum & Wetherall (& Feamster) — *Redes de Computadores*
- **Autores:** Andrew S. Tanenbaum, David J. Wetherall, Nick Feamster · **Editora:** Pearson ·
  **Edição:** 6ª (2021, inglês; 5ª ed. em PT-BR, 2011).
- **Nível:** intermediário. Mais *bottom-up* e detalhado no hardware/enlace que o Kurose.
- **ARP onde:** capítulo de camada de enlace/rede — resolução de endereço, Ethernet.
- **Por que ler:** clássico, profundo em camada 2. A 5ª PT-BR está datada em alguns tópicos
  (SDN, nuvem), mas os fundamentos de ARP continuam válidos.

> **Escolha:** se for ler só um, **Kurose** para começar. Tanenbaum como segundo, para
> profundidade de enlace.

---

## 2. A obra de referência para o protocolo por dentro

### W. Richard Stevens — *TCP/IP Illustrated, Volume 1: The Protocols*
- **Autores:** W. Richard Stevens; 2ª ed. revista por Kevin R. Fall · **Editora:** Addison-Wesley
  · **Edição:** 2ª (2011). 1ª ed. de 1994.
- **Nível:** intermediário → avançado. **A referência para "ver o protocolo acontecer".**
- **ARP onde:** **capítulo 4 é inteiramente sobre ARP** (na 1ª ed.; reorganizado na 2ª), com
  capturas reais, gratuitous ARP, proxy ARP, o cache. É a inspiração do método deste curso (ver
  no fio, decodificar à mão).
- **Por que ler:** ninguém explicou protocolos com capturas reais melhor que Stevens. **Clássico
  que continua valendo** — o ARP não mudou desde que ele escreveu. Só o Vol. 1 interessa aqui.
- **PT-BR:** houve tradução da 1ª ed.; a 2ª é mais fácil achar em inglês.

---

## 3. Segurança de camada 2

### Yusuf Bhaiji — *Network Security Technologies and Solutions* (CCIE Professional Development)
- **Editora:** Cisco Press · **Ano:** 2008. **Nível:** avançado.
- **ARP onde:** ARP spoofing, DAI, DHCP snooping, port security — o lado de defesa do
  [18](18-seguranca.md). Datado em produtos, **atual nos conceitos** de defesa de camada 2.

### Chris Sanders — *Practical Packet Analysis* (Using Wireshark)
- **Editora:** No Starch Press · **Edição:** 3ª (2017). **Nível:** iniciante → intermediário.
- **ARP onde:** análise de ARP no Wireshark, incluindo cenários de problema. **Ótimo companheiro
  prático** do [12](12-anatomia-do-pacote.md) e [70](70-pratica.md). Envelheceu pouco.

---

## 4. Linux / administração de rede

### Christian Benvenuti — *Understanding Linux Network Internals*
- **Editora:** O'Reilly · **Ano:** 2005. **Nível:** avançado → pesquisa.
- **ARP onde:** capítulos sobre a implementação de ARP e do subsistema de vizinhos no kernel
  Linux — o material por trás do [14](14-a-tabela-por-dentro.md) e [60](60-teoria-avancada.md).
- **Ressalva:** **datado** (kernel 2.6). Os detalhes de código mudaram; os **conceitos** (NUD,
  cache, gc) permanecem. Leia pela arquitetura, não pelas linhas exatas.

### Documentação do kernel — *Documentation/networking/* e `man 7 arp`
- **Custo:** grátis. **Nível:** avançado. A fonte viva e atualizada para os sysctls do
  [16](16-arp-em-cada-sistema.md) e a semântica de `arp_ignore`/`arp_announce`.

---

## 5. Legalmente gratuito

| Obra | Onde | Nota |
|---|---|---|
| **RFC 826** e correlatas (903, 1027, 5227, 4861) | [rfc-editor.org](https://www.rfc-editor.org/) | domínio público; a fonte primária |
| **Documentação do kernel Linux** | kernel.org / `man` | GPL/aberta |
| **Beej's Guide to Network Programming** | beej.us | grátis; contexto de sockets, toca em endereçamento |
| **Material universitário PT/FR** | ver [85](85-cursos-e-certificacoes.md) | PDFs abertos (Olivier Glück etc.) |
| **Wireshark Wiki / User's Guide** | wireshark.org | grátis, prático |

---

## 6. Como montar sua estante (recomendação)

1. **Kurose & Ross** — a base. Se comprar um, é este.
2. **Stevens, TCP/IP Illustrated Vol. 1** — para o ARP por dentro. Clássico atemporal.
3. **Chris Sanders, Practical Packet Analysis** — para as mãos no Wireshark.
4. **RFC 826** (grátis) — leia a fonte, são 10 páginas.
5. Kernel docs + Benvenuti — só se for para o nível de implementação/pesquisa.

Para *este assunto* especificamente, **Stevens cap. 4 + RFC 826 + este material** já levam do
zero ao avançado sem gastar nada além do Stevens (opcional).

---

## Autoteste

1. Qual livro ler primeiro para redes, e por quê a abordagem dele ajuda a entender ARP?
2. Qual obra é a referência para "ver o protocolo acontecer", e onde está o ARP nela?
3. Qual livro cobre a implementação de ARP no kernel, e qual a ressalva sobre ele?
4. Onde estudar a **defesa** de camada 2 (DAI, DHCP snooping) em livro?
5. Cite três fontes **legalmente gratuitas** para este assunto.
6. Por que "Stevens não envelheceu" para ARP, mesmo sendo de 1994/2011?
7. Monte a estante mínima para dominar só ARP gastando o mínimo.

---

**Fontes:** catálogos das editoras (Pearson, Addison-Wesley, O'Reilly, No Starch, Cisco Press);
rfc-editor.org. Edições conferidas onde possível em 14/08/2026; onde houver dúvida de ISBN, citei
só autor/título/editora, conforme a regra do preset.

**Próximo:** [95-referencias.md](95-referencias.md)
