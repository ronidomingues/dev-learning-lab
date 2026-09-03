# 90 · Bibliografia comentada

`Nível: todos` · `Última atualização: 12/08/2026`

Livros com autor, título, editora e ano, comentados: nível, o que fazem melhor, e se
envelheceram. **Nada inventado** — onde não tenho certeza de edição/ISBN, cito só autor e
título. O que é legalmente gratuito está marcado com 🆓.

---

## 1. Fundamentos e visão geral

- **Georgia Weidman — *Penetration Testing: A Hands-On Introduction to Hacking*** (No Starch
  Press, 2014). Nível: iniciante. **O melhor primeiro livro de pentest.** Prático, do
  laboratório ao exploit. Envelheceu em ferramentas específicas (é de 2014), mas a **estrutura
  e o método continuam válidos**. Comece por ele.

- **Patrick Engebretson — *The Basics of Hacking and Penetration Testing*** (Syngress, 2ª ed.
  2013). Nível: iniciante. Curto, direto, as quatro fases. Datado em ferramentas, bom para a
  lógica geral.

- **The Cyber Mentor (Heath Adams) — material do "Practical Ethical Hacking"** (curso, não
  livro). Cito aqui porque, para muitos, substitui o livro introdutório com vantagem por ser
  prático e atual. Ver [`85`](85-cursos-e-certificacoes.md).

## 2. Web — a especialidade mais procurada

- **Dafydd Stuttard & Marcus Pinto — *The Web Application Hacker's Handbook*** (Wiley, 2ª ed.
  2011). Nível: intermediário/avançado. **O clássico de segurança web.** Ainda ensina os
  conceitos como ninguém, mas **está datado** (2011, antes de muitos frameworks modernos). Os
  autores são os criadores do Burp; hoje a **PortSwigger Web Security Academy** ([`85`](85-cursos-e-certificacoes.md))
  é a continuação viva e gratuita deste livro — 🆓 e atualizada. Recomendo o livro pelos
  conceitos e a Academy pela prática atual.

- **Michal Zalewski — *The Tangled Web: A Guide to Securing Modern Web Applications*** (No
  Starch, 2011). Nível: avançado. Profundo sobre o modelo de segurança do navegador. Datado em
  detalhes, brilhante nos princípios.

- **OWASP — *Web Security Testing Guide (WSTG)*** e ***Application Security Verification
  Standard (ASVS)*** 🆓. Não são livros comerciais, são os documentos de referência do campo,
  gratuitos e **atualizados**. Leitura obrigatória para web. Ver [`13`](13-metodologias-e-frameworks.md).

## 3. Exploração e sistemas

- **Jon Erickson — *Hacking: The Art of Exploitation*** (No Starch Press, 2ª ed. 2008). Nível:
  intermediário/avançado. **Clássico atemporal** para entender exploração de memória do zero,
  com C e assembly. As mitigações modernas ([`16`](16-vulnerabilidades-e-exploracao.md),
  [`60`](60-teoria-avancada.md)) vieram depois, mas os **fundamentos são perenes**. Vem com CD/
  ambiente para praticar.

- **Chris Anley et al. — *The Shellcoder's Handbook*** (Wiley, 2ª ed. 2007). Nível: avançado.
  Exploração de binário a fundo. Datado nas mitigações, sólido nos conceitos.

- **Bruce Dang, Alexandre Gazet, Elias Bachaalany — *Practical Reverse Engineering*** (Wiley,
  2014). Nível: avançado. Engenharia reversa x86/x64/ARM.

## 4. Redes e análise

- **Kevin Fall & Richard Stevens — *TCP/IP Illustrated, Vol. 1*** (Addison-Wesley, 2ª ed. 2011).
  Nível: intermediário. **A referência de TCP/IP.** Não é de hacking, mas entender rede a esse
  nível separa o pentester bom do medíocre ([`15`](15-varredura-e-enumeracao.md)).

- **Chris Sanders — *Practical Packet Analysis*** (No Starch, 3ª ed. 2017). Nível: iniciante/
  intermediário. Wireshark na prática. Continua atual.

- **James Kurose & Keith Ross — *Computer Networking: A Top-Down Approach*** (Pearson). Nível:
  iniciante. O livro-texto de redes; material de apoio 🆓 no site dos autores. Há tradução em
  português. Ótimo pré-requisito.

## 5. Active Directory e Windows

- Para AD, o melhor material é **online e gratuito**: documentação do BloodHound, blogs da
  SpecterOps, o **Orange Cyberdefense GOAD**, e o **HTB Academy** ([`20`](20-active-directory.md)).
  O campo muda rápido demais para livro impresso acompanhar — prefira as fontes vivas de
  [`95`](95-referencias.md).

## 6. Malware e defesa (para entender o outro lado)

- **Michael Sikorski & Andrew Honig — *Practical Malware Analysis*** (No Starch, 2012). Nível:
  intermediário/avançado. **A bíblia da análise de malware.** Datado em ferramentas, insuperável
  em método.

- **Richard Bejtlich — *The Practice of Network Security Monitoring*** (No Starch, 2013). Nível:
  intermediário. O lado blue; entender detecção te faz melhor atacante ([`25`](25-carreira-passo-a-passo.md)).

## 7. Fator humano e cultura

- **Kevin Mitnick — *The Art of Deception*** (Wiley, 2002) e ***The Art of Intrusion*** (2005).
  Nível: leigo/iniciante. Engenharia social por quem foi lenda dela. Datados tecnicamente,
  atemporais na psicologia ([`23`](23-engenharia-social.md)).

- **Christopher Hadnagy — *Social Engineering: The Science of Human Hacking*** (Wiley, 2ª ed.
  2018). Nível: intermediário. O tratado moderno de engenharia social.

- **Cliff Stoll — *The Cuckoo's Egg*** (1989). Nível: leigo. Narrativa real de caça a um
  invasor nos anos 80. **Leitura deliciosa e formativa** sobre a mentalidade investigativa.

- **Steven Levy — *Hackers: Heroes of the Computer Revolution*** (1984). A história da cultura
  hacker ([`11`](11-historia.md)).

## 8. Criptografia (para quem vai a fundo)

- **Jean-Philippe Aumasson — *Serious Cryptography*** (No Starch, 2ª ed. 2024). Nível:
  intermediário. **A melhor introdução moderna à cripto aplicada**, incluindo pós-quântica na
  2ª edição. Atual.

- **Niels Ferguson, Bruce Schneier, Tadayoshi Kohno — *Cryptography Engineering*** (Wiley,
  2010). Nível: intermediário. Como usar cripto sem se enganar. Envelheceu em detalhes, sólido
  no julgamento.

## 9. Referências rápidas e específicas

- **OccupyTheWeb — *Linux Basics for Hackers*** (No Starch, 2019). Nível: iniciante. Linux
  focado em quem quer hackear. Bom se você é fraco em terminal.
- **TJ O'Connor — *Violent Python*** (Syngress, 2012). Nível: iniciante/intermediário.
  Automatizar tarefas ofensivas em Python. Datado na sintaxe (Python 2!), útil na ideia.
- **Peter Yaworski — *Real-World Bug Hunting*** (No Starch, 2019). Nível: intermediário. Bug
  bounty com casos reais. Ótimo para quem foca em web/bounty.

## 10. Como usar esta lista

- **Não compre tudo.** Comece com **um** introdutório (Weidman) + a **PortSwigger Academy** 🆓
  para web. Isso já sustenta seus primeiros 6 meses.
- **Livro impresso envelhece; prática online não.** Para ferramentas e AD/nuvem, prefira as
  fontes vivas de [`95`](95-referencias.md). Livros valem pelos **conceitos perenes**.
- **No Starch Press** é a editora com o melhor catálogo de segurança — vale seguir os lançamentos.

---

## Autoteste

1. Qual é o melhor primeiro livro de pentest, e qual é a ressalva sobre a idade dele?
2. Por que o *Web Application Hacker's Handbook* é recomendado junto com a PortSwigger Academy,
   e não sozinho?
3. Qual livro ensina exploração de memória do zero e por que seus fundamentos são perenes apesar
   das mitigações modernas?
4. Por que, para Active Directory, o material online é preferível a livro impresso?
5. Cite um livro do "lado blue" e por que ele te torna melhor atacante.
6. Qual livro moderno de criptografia inclui pós-quântica, e de que ano é a edição?
7. Qual é a estratégia recomendada de "por onde começar" sem gastar muito?
