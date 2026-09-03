# 95 · Referências — specs, docs, ferramentas, pessoas, feeds

`Nível: todos` · `Última atualização: 12/08/2026`

As fontes primárias e vivas do campo. Diferente da bibliografia ([`90`](90-bibliografia.md)),
aqui estão specs, documentação oficial, ferramentas, pessoas a seguir e feeds — o que se
consulta e acompanha, não o que se lê de capa a capa.

---

## 1. Padrões e frameworks (fontes primárias)

| Recurso | O que é | Link |
|---|---|---|
| **OWASP Top 10** | as 10 classes de risco web mais críticas | [owasp.org/Top10](https://owasp.org/Top10/) |
| **OWASP WSTG** | guia de teste de segurança web | [owasp.org/www-project-web-security-testing-guide](https://owasp.org/www-project-web-security-testing-guide/) |
| **OWASP ASVS** | padrão de verificação (critério passa/não passa) | [owasp.org/www-project-application-security-verification-standard](https://owasp.org/www-project-application-security-verification-standard/) |
| **OWASP MASTG/MASVS** | mobile | [mas.owasp.org](https://mas.owasp.org) |
| **OWASP Top 10 for LLM** | segurança de aplicações com LLM | [genai.owasp.org](https://genai.owasp.org) |
| **MITRE ATT&CK** | táticas e técnicas de adversário | [attack.mitre.org](https://attack.mitre.org) |
| **MITRE D3FEND** | contramedidas defensivas | [d3fend.mitre.org](https://d3fend.mitre.org) |
| **PTES** | Penetration Testing Execution Standard | [pentest-standard.org](http://www.pentest-standard.org) |
| **NIST SP 800-115** | guia técnico de teste de segurança | [csrc.nist.gov](https://csrc.nist.gov) |
| **CIS Controls / Benchmarks** | controles e hardening priorizados | [cisecurity.org](https://www.cisecurity.org) |

## 2. Bases de vulnerabilidade e ameaça

| Recurso | O que é |
|---|---|
| **CVE** ([cve.org](https://www.cve.org)) / **NVD** ([nvd.nist.gov](https://nvd.nist.gov)) | identificadores e detalhes de vulnerabilidades |
| **CWE** ([cwe.mitre.org](https://cwe.mitre.org)) | catálogo de classes de fraqueza |
| **CISA KEV** ([cisa.gov/kev](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)) | vulnerabilidades comprovadamente exploradas — prioridade de correção |
| **EPSS** ([first.org/epss](https://www.first.org/epss/)) | probabilidade de exploração |
| **Exploit-DB** ([exploit-db.com](https://www.exploit-db.com)) | exploits públicos (base do `searchsploit`) |
| **CVSS calculator** ([first.org/cvss](https://www.first.org/cvss/calculator/)) | cálculo de severidade |

## 3. Referências de técnicas (consulta diária)

| Recurso | Para quê |
|---|---|
| **GTFOBins** ([gtfobins.github.io](https://gtfobins.github.io)) | abusar de binários Unix (escalada) |
| **LOLBAS** ([lolbas-project.github.io](https://lolbas-project.github.io)) | binários nativos do Windows |
| **HackTricks** ([book.hacktricks.wiki](https://book.hacktricks.wiki)) | **a enciclopédia ofensiva** — receitas para quase tudo |
| **PayloadsAllTheThings** ([github.com/swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)) | payloads por classe de falha |
| **revshells.com** ([revshells.com](https://www.revshells.com)) | gera reverse shells em qualquer linguagem |
| **The Hacker Recipes** ([thehacker.recipes](https://www.thehacker.recipes)) | técnicas, forte em AD |
| **CrackStation / hashes.com** | consulta de hashes já quebrados |

## 4. Documentação de ferramentas essenciais

- **nmap:** [nmap.org/book](https://nmap.org/book/) — o livro oficial, gratuito, do Fyodor.
- **Metasploit:** [docs.metasploit.com](https://docs.metasploit.com)
- **Burp Suite:** [portswigger.net/burp/documentation](https://portswigger.net/burp/documentation)
- **impacket:** [github.com/fortra/impacket](https://github.com/fortra/impacket)
- **netexec:** [netexec.wiki](https://www.netexec.wiki)
- **BloodHound:** [bloodhound.specterops.io](https://bloodhound.specterops.io)
- **ffuf, nuclei, subfinder (ProjectDiscovery):** [docs.projectdiscovery.io](https://docs.projectdiscovery.io)

## 5. Pessoas e organizações a acompanhar

> Seguir quem faz o campo é a forma mais rápida de ficar atualizado. Uma amostra representativa,
> não exaustiva:

- **SpecterOps** (BloodHound, AD) — blog técnico de referência em Active Directory.
- **PortSwigger Research** (James Kettle / "albinowax") — pesquisa web de ponta (request
  smuggling, web cache, etc.).
- **Project Zero (Google)** — pesquisa de 0-day e política de divulgação.
- **Orange Cyberdefense / mxrch / Orange Tsai** — pesquisa ofensiva de alto nível.
- **The Cyber Mentor, IppSec, John Hammond, LiveOverflow, STÖK** — educadores (ver [`85`](85-cursos-e-certificacoes.md)).
- **Daniel Miessler** — newsletter/analise de segurança.
- Comunidades: **/r/netsec**, **/r/AskNetsec**, Discords de HTB/TryHackMe.

## 6. Feeds e newsletters (para não perder a fronteira)

- **The Hacker News**, **BleepingComputer** — notícias diárias.
- **Krebs on Security** (Brian Krebs) — jornalismo investigativo de cibercrime.
- **tl;dr sec** (newsletter) — resumo semanal de AppSec.
- **CTFtime** ([ctftime.org](https://ctftime.org)) — calendário de CTFs.
- **Risky Business** (podcast) — semanal, o panorama do setor.
- **Darknet Diaries** (podcast) — histórias reais, ótimo para leigos e para motivação.

## 7. Brasil — comunidade e eventos

- **Roadsec** — maior evento de segurança itinerante do Brasil.
- **H2HC (Hackers to Hackers Conference)** — a conferência técnica brasileira de referência.
- **BSides** (várias cidades) — eventos comunitários acessíveis.
- **Comunidades:** grupos brasileiros no Discord/Telegram, DEF CON Groups locais.
- **Papers/legislação:** texto da Lei 12.737/2012 e 14.155/2021 no [Planalto](http://www.planalto.gov.br),
  LGPD (Lei 13.709/2018), materiais da ANPD.

## 8. Papers e leituras seminais (amostra)

- Turing, A. (1936). *On Computable Numbers* — o problema da parada ([`60`](60-teoria-avancada.md)).
- Rice, H. G. (1953). *Classes of recursively enumerable sets and their decision problems*.
- Thompson, K. (1984). *Reflections on Trusting Trust* — confiança em compiladores/supply chain.
- Saltzer & Schroeder (1975). *The Protection of Information in Computer Systems* — os
  princípios de design seguro (menor privilégio etc.).
- Aleph One (1996). *Smashing the Stack for Fun and Profit* — o texto fundador da exploração de
  pilha ([`16`](16-vulnerabilidades-e-exploracao.md)).
- Dolev & Yao (1983). *On the security of public key protocols* — o modelo do atacante de rede.

## 9. Como usar estas referências

- **Diariamente:** HackTricks, GTFOBins, PayloadsAllTheThings, docs da ferramenta do momento.
- **Ao encontrar uma CVE:** NVD → KEV (está sendo explorada?) → EPSS → Exploit-DB.
- **Para se manter atualizado:** um feed + um podcast + seguir 5 pesquisadores. 30 min/semana.
- **Não tente ler tudo.** Consulte sob demanda; acompanhe uma fatia estreita a fundo.

---

## Autoteste

1. Onde você confirma se uma CVE está sendo **ativamente explorada**?
2. Qual recurso consultar para abusar de um binário Unix com SUID? E para binário Windows?
3. O que é o HackTricks e como ele se usa?
4. Cite três feeds/podcasts para acompanhar a fronteira sem se afogar.
5. Quais são os dois principais eventos técnicos de segurança no Brasil?
6. Qual paper de 1936 é o alicerce teórico da impossibilidade de um scanner perfeito?
7. Qual é a estratégia recomendada para "se manter atualizado" sem tentar ler tudo?
