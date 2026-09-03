# 85 · Cursos gratuitos e certificações

> **Nível:** todos
> **Data da pesquisa: 14/08/2026.** Links podem expirar; o ano de cada curso está indicado.
>
> **Aviso honesto:** **não existe** curso ou certificação "de tabela ARP" — é um tópico dentro
> de **redes de computadores**. Então este arquivo aponta (a) o material que cobre ARP
> especificamente e (b) os cursos de redes onde ARP é uma aula, indicando **onde** ele aparece.

---

## 1. Português (prioridade) — vídeo, gratuito

| Curso | Autor/Instituição | Plataforma | Nível | Ano | Vale? |
|---|---|---|---|---|---|
| **Curso de Redes de Computadores** (playlist) | **Bóson Treinamentos** (Fábio dos Reis) | [YouTube](https://www.youtube.com/c/bosontreinamentos) | iniciante→interm. | atualizado | **Sim.** A referência gratuita em PT. Tem aulas específicas de **ARP**, camada de enlace, MAC, Ethernet. Comece por aqui. |
| **Redes de Computadores (20h)** | **Curso em Vídeo** (Gustavo Guanabara) | [cursoemvideo.com](https://www.cursoemvideo.com/curso/redes-de-computadores/) | iniciante | recente | **Sim** para a base (IP, sub-rede, DHCP). ARP é tocado de leve; ótimo para os pré-requisitos do [02](02-pre-requisitos.md). |
| **Estrutura e Funcionamento das Redes** (Google) | Google | [Coursera](https://www.coursera.org/learn/redes-computadores) (audit grátis) | iniciante | 2023+ | **Sim** (assistir grátis). Explica como ARP liga as camadas. Certificado é pago. |
| Aulas avulsas "Protocolo ARP" | vários | [YouTube](https://www.youtube.com/results?search_query=protocolo+arp) | iniciante | vários | Úteis como complemento pontual; qualidade varia. |

> **Recomendação PT:** Bóson para ARP e camada 2; Curso em Vídeo para a base de IP/sub-rede que
> o [02](02-pre-requisitos.md) exige.

---

## 2. Inglês — vídeo, gratuito

| Curso | Autor/Instituição | Plataforma | Nível | Ano | Vale? |
|---|---|---|---|---|---|
| **The Bits and Bytes of Computer Networking** | Google | [Coursera](https://www.coursera.org/learn/computer-networking) (audit grátis) | iniciante | 2020+ (mantido) | **Sim.** Cobre ARP no contexto de resolução de endereço. Certificado pago; assistir é grátis. |
| **Introduction to TCP/IP** | Yonsei University | [Coursera](https://www.coursera.org/learn/tcpip) (audit grátis) | interm. | recente | **Sim.** Tem lições específicas de **ARP**. |
| **Free "ARP – The Address Resolution Protocol"** | instrutor independente | [Udemy](https://www.udemy.com/course/undertanding-arp/) | iniciante | — | **Talvez.** Curso curto **só de ARP**, com experimentos em Wireshark. Bom se você quer foco total no tópico. |
| **Computer Networking (Full Course)** | vários (freeCodeCamp, NetworkChuck, PowerCert) | [YouTube](https://www.youtube.com/c/NetworkChuck) | iniciante | 2023+ | **Sim.** NetworkChuck e PowerCert têm explicações visuais excelentes de ARP em poucos minutos. |
| **Wireshark** (análise, inclui ARP) | Chris Greer, David Bombal | YouTube | interm. | recente | **Sim** para ver ARP no fio (complementa o [09](12-anatomia-do-pacote.md)/[70](70-pratica.md)). |

---

## 3. Francês — vídeo/recursos, gratuito

| Recurso | Autor/Instituição | Formato | Nível | Ano | Vale? |
|---|---|---|---|---|---|
| **Les bits et les octets des réseaux informatiques** | Google | [Coursera FR](https://fr.coursera.org/learn/les-bits-et-les-octets-des-reseaux-informatiques) (audit grátis) | iniciante | mantido | **Sim.** Versão francesa do curso Google; cobre ARP. |
| **Les protocoles Ethernet, ARP et ICMP** (Olivier Glück) | Univ. Lyon 1 | PDF em [bestcours](https://www.bestcours.com/reseaux) / [courspdf](https://www.courspdf.net/) | interm. | acadêmico | **Sim.** Material universitário sólido, foco em Ethernet/ARP/ICMP. Não é vídeo, mas é denso e correto. |
| **Comprendre le protocole ARP** | LinkedIn Learning | vídeo (trechos grátis) | iniciante | recente | Parcial: alguns vídeos abertos; curso completo é pago. |
| **Cours ARP + Scapy** | reseaux.progwmj.ca | web | interm. | recente | **Sim** para a prática com Scapy ([70](70-pratica.md) lab 10). |
| **FRAMEIP — Entête ARP** | frameip.com | web | interm. | referência | **Sim.** Decodificação do cabeçalho ARP em francês, boa para o [12](12-anatomia-do-pacote.md). |

---

## 4. Documentação oficial com trilha de aprendizado

- **RFC 826** — a fonte primária, curta e legível ([rfc-editor.org](https://www.rfc-editor.org/info/rfc826)).
- **`man ip-neighbour(8)`, `man arp(8)`, `man arping(8)`, `man arp-scan(1)`** — no seu terminal.
- **Documentação Cisco** de ARP/DAI (para o lado de switch/roteador — [18](18-seguranca.md)).
- **Wireshark Wiki — Address Resolution Protocol** (dissecção e filtros).

---

## 5. Certificações — a verdade franca

**Não há certificação de "tabela ARP".** ARP é um tópico avaliado dentro de certificações de
redes. As que **valem no mercado** e cobrem ARP:

| Certificação | Emissor | Custo (14/08/2026) | ARP cai? | Valor de mercado |
|---|---|---|---|---|
| **CCNA** | Cisco | ~US$ 300 (exame) | **sim**, e a fundo (ARP, DAI, MAC table) | **Alto.** A referência da indústria em redes. |
| **Network+** | CompTIA | ~US$ 370 | **sim** | Alto, neutro de fabricante. |
| **CCNP Enterprise** | Cisco | ~US$ 300/exame | sim (EVPN, ARP suppression) | Alto, avançado. |
| **JNCIA** | Juniper | grátis/baixo (promoções) | sim | Médio (nicho Juniper). |
| **Certificações Linux** (LPIC-1, etc.) | LPI | ~US$ 200 | ARP/`ip neigh` no escopo | Médio-alto para SysAdmin. |

**Certificadores gratuitos (certificado sem custo):**

- **Cisco Networking Academy** — cursos gratuitos ("Networking Essentials", "CCNA: Introduction
  to Networks") com **certificado de conclusão gratuito** (não é o CCNA pago, mas cobre ARP a
  fundo e tem valor de portfólio). Recomendado.
- **freeCodeCamp**, **Coursera (audit)** — dão certificado **só se pagar**; assistir é grátis.
- **Fortinet, Juniper** — trilhas gratuitas com certificados de conclusão gratuitos em alguns
  níveis.

> **Franqueza sobre certificados:** o certificado **gratuito de conclusão** (Cisco NetAcad,
> Fortinet) tem valor **simbólico/de portfólio** — mostra esforço, não é exigido por empregador.
> O que o mercado realmente valoriza é a **certificação paga com exame proctorado** (CCNA,
> Network+), porque ela prova conhecimento verificado por terceiro. Para *aprender* ARP, os
> gratuitos bastam e sobram. Para *sinalizar competência a um empregador de redes*, o CCNA é o
> divisor de águas — mas é investimento, não gasto obrigatório para este assunto.

---

## 6. Trilha recomendada (gratuita, do zero)

1. **Base de IP/sub-rede:** Curso em Vídeo (PT) ou o curso Google (audit).
2. **ARP especificamente:** Bóson Treinamentos (PT) + este material (`01`–`20`).
3. **Ver no fio:** vídeos de Wireshark (Chris Greer) + [70](70-pratica.md) labs 9–10.
4. **Aprofundar redes:** Cisco NetAcad "Introduction to Networks" (certificado grátis).
5. **Se for trabalhar com redes:** estudar para o **CCNA** (pago) ou **Network+**.

---

## Autoteste

1. Existe certificação "de ARP"? Onde ARP é realmente avaliado?
2. Qual o melhor recurso gratuito em PT para ARP e camada 2?
3. Qual a diferença entre "assistir grátis no Coursera" e "ter o certificado"?
4. Que certificado gratuito tem valor de portfólio, e qual pago tem valor de mercado real?
5. Onde ver ARP no fio, na prática, além deste material?
6. Monte, em uma linha, a trilha gratuita do zero até "ver ARP no Wireshark".
7. Para quem quer emprego em redes, vale pagar o CCNA? Por quê (e por que não é obrigatório para
   *este* assunto)?

---

**Fontes (pesquisadas na web em 14/08/2026):** YouTube (Bóson, Curso em Vídeo, NetworkChuck,
Chris Greer); Coursera (Google, Yonsei) PT/EN/FR; Udemy (curso de ARP); bestcours/courspdf e
frameip (FR); páginas de certificação Cisco/CompTIA/Juniper/LPI; Cisco Networking Academy.
Preços de exame são aproximados e mudam — reconfirme no site do emissor.

**Próximo:** [90-bibliografia.md](90-bibliografia.md)
