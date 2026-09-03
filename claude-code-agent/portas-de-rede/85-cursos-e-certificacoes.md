# 85 · Cursos gratuitos e certificações

**Nível:** todos · **Pesquisado na web em 14/08/2026**
Links verificados na data da consulta. Cursos gratuitos mudam de status; se um link estiver
quebrado, procure pelo título e pelo autor.

⚠️ **Aviso sobre o assunto:** não existe curso chamado "portas de rede". Portas são um
**capítulo** de redes de computadores e um **pré-requisito** de segurança ofensiva. Os
cursos abaixo são de redes e de varredura — as duas metades da sua pergunta original.

---

## 1. Português — a prioridade

### 1.1 Bóson Treinamentos (Fábio dos Reis) — **a melhor porta de entrada em PT**

| | |
|---|---|
| **Plataforma** | YouTube, gratuito, sem cadastro |
| **Canal** | [youtube.com/@bosontreinamentos](https://www.youtube.com/@bosontreinamentos) |
| **Playlist principal** | [Curso de Redes de Computadores](https://www.youtube.com/playlist?list=PLucm8g_ezqNpGh95n-OdEk06ity7YYfvU) |
| **Vídeo direto ao ponto** | ["Serviços de Rede, Portas TCP e Portas UDP"](https://www.youtube.com/watch?v=Oi4GuP84Xtw) |
| **Nível** | Iniciante a intermediário |
| **Duração** | Dezenas de vídeos curtos; o essencial em ~15 h |
| **Certificado** | Não |

**Por que vale o tempo:** é o material em português com melhor relação didática/densidade
sobre redes. O Fábio explica devagar, define os termos, e não pula etapas. O vídeo específico
sobre portas TCP/UDP cobre exatamente o [`01`](01-introducao-leigo.md) e o
[`10`](10-fundamentos.md) deste curso.

**Onde não basta:** é conceitual. Não te ensina a diagnosticar, e não cobre `ss`, `nmap` nem
containers. Complemente com a prática deste curso.

### 1.2 Curso de Infraestrutura de Redes — Robson Vaamonde

| | |
|---|---|
| **Repositório** | [github.com/vaamonde/infraestrutura](https://github.com/vaamonde/infraestrutura) |
| **Formato** | Repositório GitHub com material e vídeos, atualizado para 2025/2026 |
| **Nível** | Intermediário a avançado |
| **Certificado** | Não |

**Por que vale:** é o material brasileiro mais **prático** de infraestrutura Linux e redes
que existe de graça. Fortemente orientado a comandos e configuração real.

**Onde não basta:** é denso e assume alguma familiaridade com Linux. Não é primeiro contato.

### 1.3 Curso de Redes do MEC / Escola do Trabalhador

| | |
|---|---|
| **Formato** | Online, gratuito, **com certificado** |
| **Onde** | Portais do MEC e parceiros (ver [Guia de TI](https://guiadeti.com.br/noticias/curso-de-redes-de-computadores-gratuito-do-mec/)) |
| **Nível** | Iniciante |

**Franqueza sobre o valor:** o certificado é institucional e serve para comprovar horas
complementares em faculdade ou para pontuação em concurso. **Não tem peso no mercado
privado.** O conteúdo é introdutório e correto.

⚠️ **Cuidado com uma categoria inteira de "cursos gratuitos com certificado"** (Prime Cursos,
Learncafe, Estudante Virtual, Pleno Cursos e similares). O padrão é: o curso é gratuito para
assistir, e o **certificado é pago** (tipicamente R$ 30–60). Não são fraude, mas o
certificado deles não tem reconhecimento de mercado. Se o seu objetivo é aprender, o
Bóson entrega mais. Se é o papel, veja a seção de certificações.

### 1.4 Documentação e comunidade em português

| Recurso | O que é |
|---|---|
| [Guia Foca Linux](https://www.guiafoca.org/) | Guia clássico brasileiro; a seção de rede continua útil |
| [Diolinux](https://www.youtube.com/@Diolinux) | Canal com fundamentos de Linux |
| [Manual do `ss` em português](https://manpages.debian.org/) | `man ss` traduzido nas distros com locale pt_BR |

---

## 2. Inglês

### 2.1 TryHackMe — **a melhor prática guiada, com camada gratuita real**

| Módulo | Link | Grátis? |
|---|---|---|
| **Network Fundamentals** | [tryhackme.com/module/network-fundamentals](https://tryhackme.com/module/network-fundamentals) | Salas iniciais sim |
| **Nmap** | [tryhackme.com/module/nmap](https://tryhackme.com/module/nmap) | Parcial |
| Nmap: The Basics | dentro do módulo acima | Sim |

**Por que vale:** máquina no navegador, sem instalar nada. Você varre um alvo real e
autorizado, com orientação passo a passo. É o complemento prático ideal ao
[`17-descoberta-e-varredura.md`](17-descoberta-e-varredura.md).

**Modelo:** camada gratuita com limite de tempo diário; assinatura ~US$ 14/mês. **A camada
gratuita é suficiente** para o conteúdo de portas e varredura.

### 2.2 Hack The Box Academy

| | |
|---|---|
| **Módulo** | "Network Enumeration with Nmap" |
| **Link** | [academy.hackthebox.com](https://academy.hackthebox.com/) |
| **Grátis?** | Módulos introdutórios sim; os avançados por *cubes* (créditos pagos) |
| **Nível** | Intermediário |

**Por que vale:** é o material mais completo sobre Nmap especificamente. Cobre técnicas de
evasão de firewall que nenhum curso gratuito de rede toca.

Complemento gratuito: as máquinas **Starting Point** do HTB são feitas para quem está
aprendendo enumeração.

### 2.3 Documentação oficial — melhor que a maioria dos cursos

| Recurso | Por que |
|---|---|
| **[Nmap Reference Guide](https://nmap.org/book/man.html)** | Gratuito, completo, escrito pelo autor |
| **[Nmap Network Scanning](https://nmap.org/book/)** | **Metade do livro está online de graça**, legalmente. Ver [`90-bibliografia.md`](90-bibliografia.md) |
| [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/) | **Gratuito.** A melhor introdução a sockets que existe |
| [RFC 793](https://www.rfc-editor.org/rfc/rfc793) / [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293) | O TCP na fonte. RFC 9293 (2022) é a consolidação moderna |
| [Illustrated TCP/IP (Wireshark docs)](https://www.wireshark.org/docs/) | Ilustrado e gratuito |

**O Beej's Guide merece destaque.** É gratuito, escrito com humor, e ensina a API de sockets
melhor que qualquer curso pago. Se você quer entender de verdade o
[`10-fundamentos.md`](10-fundamentos.md) e o [`15-sockets-e-o-kernel.md`](15-sockets-e-o-kernel.md),
é a leitura seguinte.

### 2.4 Cursos universitários abertos

| Curso | Instituição | Grátis? |
|---|---|---|
| Computer Networking (baseado em Kurose & Ross) | várias, em plataformas MOOC | Assistir sim, certificar não |
| [Networking course — Coursera / Google IT Support](https://www.coursera.org/) | Google | Assistir sim; certificado pago |

**Distinção importante que quase nunca é feita:** "gratuito para assistir" ≠ "gratuito para
certificar". Praticamente todo MOOC hoje deixa o conteúdo aberto e cobra pelo certificado
(tipicamente US$ 49–79). Se o seu objetivo é conhecimento, o custo é zero. Se é o papel, não é.

### 2.5 Canais consistentes

| Canal | Foco |
|---|---|
| [NetworkChuck](https://www.youtube.com/@NetworkChuck) | Redes e segurança, muito acessível |
| [David Bombal](https://www.youtube.com/@davidbombal) | Redes, CCNA, entrevistas técnicas |
| [Practical Networking](https://www.youtube.com/@PracticalNetworking) | **O melhor para fundamentos explicados com rigor** |
| [Chris Greer](https://www.youtube.com/@ChrisGreer) | **Análise de pacotes com Wireshark** — complemento direto do `13` |

O Chris Greer é a recomendação mais específica desta lista: ele mostra handshake, `TIME_WAIT`
e retransmissão **em capturas reais**, que é exatamente o que o
[`13-tcp-por-dentro.md`](13-tcp-por-dentro.md) descreve em texto.

---

## 3. Francês

### 3.1 OpenClassrooms — **gratuito e em francês**

| Curso | Link | Duração |
|---|---|---|
| **Concevez votre réseau TCP/IP** | [openclassrooms.com](https://openclassrooms.com/fr/courses/6944606-concevez-votre-reseau-tcp-ip) | ~10 h |
| **Maîtrisez vos applications et réseaux TCP/IP** | [My Mooc](https://www.my-mooc.com/fr/mooc/maitrisez-vos-applications-et-reseaux-tcp-ip/) | ~15 h |

O segundo é a continuação do primeiro e é onde entram **portas TCP/UDP** com detalhe.
Vídeos e material escrito, gratuitos.

### 3.2 FUN MOOC — Sécurité des Réseaux Informatiques

| | |
|---|---|
| **Link** | [fun-mooc.fr](https://www.fun-mooc.fr/en/cours/securite-des-reseaux-informatiques/) |
| **Instituição** | France Université Numérique (consórcio público francês) |
| **Cobre** | Endereços IP/MAC, **números de porta TCP/UDP**, entidades de rede, roteamento |
| **Grátis?** | Sim, para assistir. Certificado costuma ser pago |

**Por que vale mesmo se você não fala francês fluente:** o FUN MOOC é financiado pelo governo
francês e tem rigor acadêmico acima da média dos MOOCs comerciais. Com legendas, é acessível
a quem lê francês técnico.

### 3.3 Agregadores

- [My Mooc](https://www.my-mooc.com/fr/) — catálogo francófono, filtra por gratuito
- [MOOC Francophone](https://mooc-francophone.com/) — idem

---

## 4. Gratuito de verdade × gratuito para assistir

| Recurso | Conteúdo | Certificado |
|---|---|---|
| Bóson Treinamentos | **Gratuito** | Não existe |
| Vaamonde (GitHub) | **Gratuito** | Não existe |
| TryHackMe (camada livre) | **Gratuito** com limite diário | Só nas trilhas pagas |
| HTB Academy (introdutórios) | **Gratuito** | Pago |
| Beej's Guide | **Gratuito** | Não existe |
| Nmap Book (metade) | **Gratuito e legal** | Não existe |
| OpenClassrooms (FR) | **Gratuito** | Pago |
| FUN MOOC | **Gratuito** | Geralmente pago |
| Coursera / edX | Gratuito para assistir | **Pago** (US$ 49–79) |
| "Cursos grátis com certificado" (BR) | Gratuito | **Pago (R$ 30–60), sem valor de mercado** |

---

## 5. Certificações — quais valem e quais não

### O que realmente pesa

| Certificação | Preço (14/08/2026) | Cobre portas? | Vale a pena? |
|---|---|---|---|
| **CompTIA Network+ (N10-009)** | US$ 399 direto / US$ 338–385 revendedor | ✅ Sim, capítulo inteiro | ✅ **Sim, para começar** |
| **Cisco CCNA (200-301)** | US$ 300 + impostos | ✅ Sim | ✅ **Sim, forte no Brasil** |
| CompTIA Security+ | ~US$ 4xx | Parcial | ✅ Sim, para segurança |
| **OSCP (Offsec)** | ~US$ 1.749+ | ✅ Varredura a fundo | ✅ Sim, para pentest — mas é pesada |
| eJPT (INE) | ~US$ 249 | ✅ | 🟡 Boa entrada em pentest |
| CEH (EC-Council) | ~US$ 1.199+ | ✅ | ⚠️ Reconhecida em edital público; **conteúdo criticado** pela comunidade técnica |

*(Preços pesquisados na web em 14/08/2026. A CompTIA reajustou toda a linha em junho de 2026:
o Network+ passou de US$ 390 para US$ 399. **A versão atual é a N10-009** — materiais que
citam N10-010 estão adiantados. Confirme em comptia.org e cisco.com.)*

**Recomendação, declarada como opinião profissional:**

- Se você quer **infraestrutura**: comece pelo **CCNA**. No Brasil ele abre mais portas que o
  Network+, por herança histórica da Cisco no mercado corporativo.
- Se você quer **segurança**: Security+ → eJPT → OSCP, nessa ordem.
- **CEH:** só faça se um edital de concurso ou um cliente exigir nominalmente. A relação
  conteúdo/preço é ruim comparada às alternativas, e isso é consenso amplo entre
  profissionais da área.

### Certificadores gratuitos — a verdade

| Emissor | Custo | Vale no mercado? |
|---|---|---|
| **Cisco Networking Academy** — *Introduction to Networks*, *Networking Basics* | **Gratuito**, certificado de conclusão incluso | 🟡 Vale como **evidência de estudo** em currículo júnior. **Não é o CCNA.** |
| Fortinet NSE 1–3 | Gratuito | 🟡 Institucional; reconhecido dentro do ecossistema Fortinet |
| Juniper Open Learning | Gratuito (o exame às vezes tem voucher promocional) | 🟡 Nicho |
| freeCodeCamp | Gratuito | 🟢 Bom para programação, fraco em redes |
| **Cursos brasileiros "grátis com certificado"** | R$ 30–60 pelo papel | 🔴 **Sem valor de mercado** |

**A resposta franca à pergunta "existe certificação gratuita que vale?":**

Não, no sentido de "abre porta em processo seletivo". O que existe de melhor é a
**Cisco Networking Academy**: o curso *Networking Basics* / *Introduction to Networks* é
genuinamente gratuito, tecnicamente sólido, e emite certificado de conclusão. Num currículo
de quem está começando, ele funciona como sinal de esforço — mas ninguém o confunde com um
CCNA.

**O que substitui certificação melhor do que qualquer certificação:** um repositório público
com o seu próprio auditor de portas, um relatório de auditoria bem-escrito, e a capacidade de
explicar numa entrevista por que `nmap` e `ss` às vezes discordam. Isso demonstra
competência; o papel só demonstra que você pagou a taxa e passou numa prova.

---

## 6. Trilha recomendada

```
Semana 1  →  Bóson: playlist de redes (fundamentos, ~10 h)
             + Blocos A e B deste curso (01 a 16)

Semana 2  →  TryHackMe: Network Fundamentals + Nmap (camada gratuita)
             + Blocos C deste curso (70, 75)

Semana 3  →  Beej's Guide (sockets, EN)
             + Projeto-modelo deste curso, modificado por você

Semana 4  →  Nmap Book (capítulos gratuitos)
             + Auditoria real da sua própria máquina/rede

Depois    →  CCNA ou Network+ se você precisa do papel
             Chris Greer (Wireshark) se você quer profundidade em TCP
```

**Custo total até a competência: R$ 0.** Só depois, se necessário, a certificação.

---

## 7. Como avaliar um material de rede que você encontrar

Cinco testes rápidos que revelam material desatualizado ou ruim:

1. **Manda ativar `tcp_tw_recycle`?** → é anterior a 2017. Descarte.
2. **Ensina `netstat` sem mencionar `ss`?** → é anterior a ~2015 no Linux.
3. **Diz que a porta 443 é sempre TCP?** → não incorporou o HTTP/3.
4. **Trata "mudar a porta do SSH" como medida de segurança séria?** → cuidado com o resto.
5. **Não distingue "fechada" de "filtrada"?** → o autor não entende o assunto.

Este teste vale também para avaliar **este** material. Se você encontrar algo aqui que falhe
nos cinco itens, o material está errado e deve ser corrigido.

---

## Fontes consultadas em 14/08/2026

- [Bóson Treinamentos — canal e playlists](https://www.youtube.com/@bosontreinamentos)
- [GitHub — vaamonde/infraestrutura](https://github.com/vaamonde/infraestrutura)
- [TryHackMe — Network Fundamentals](https://tryhackme.com/module/network-fundamentals) e [Nmap](https://tryhackme.com/module/nmap)
- [Hack The Box Academy](https://academy.hackthebox.com/)
- [OpenClassrooms — Concevez votre réseau TCP/IP](https://openclassrooms.com/fr/courses/6944606-concevez-votre-reseau-tcp-ip)
- [FUN MOOC — Sécurité des Réseaux Informatiques](https://www.fun-mooc.fr/en/cours/securite-des-reseaux-informatiques/)
- Compilações de preço de certificação: [Total Seminars](https://totalsem.com/comptia-network-plus-exam-cost/), [DiviTrain](https://www.divitrain.com/blogs/it-certifications/cisco-ccna-exam-cost-2026-full-breakdown)
- [Nmap Book](https://nmap.org/book/) · [Beej's Guide](https://beej.us/guide/bgnet/)

---

## Autoteste

1. Qual é a diferença entre "gratuito de verdade" e "gratuito para assistir"? Cite um exemplo
   de cada.
2. Existe certificação gratuita de rede que tenha peso real no mercado? Responda com
   franqueza e diga qual é a melhor alternativa gratuita.
3. Qual recurso desta lista você usaria para entender a API de sockets a fundo, e por quê?
4. Você tem R$ 0 e três semanas. Monte a sua trilha.
5. Um recruta te pede uma certificação. CCNA ou Network+? Justifique no contexto brasileiro.
6. Aplique os cinco testes da seção 7 a um material de rede que você já leu. Quantos ele passa?

---

*Próximo: [`90-bibliografia.md`](90-bibliografia.md).*
