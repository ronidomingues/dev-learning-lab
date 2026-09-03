# Ethical Hacking — Mapa do Assunto

`Nível: do zero absoluto ao de pesquisa` · `Última atualização: 12/08/2026`
`Versões de referência: Kali Linux 2026.2 · Burp Suite 2026.4.x · Metasploit Framework 6.4.131 · OWASP Top 10:2025`

---

## O que é este material

Um curso completo sobre **hacking ético** — a prática autorizada de atacar sistemas para
encontrar as falhas antes que um criminoso encontre. Cobre o que é, como se entra na carreira,
o passo a passo real, como funciona cada técnica por dentro, quanto custa, e onde está a
fronteira em agosto de 2026.

Ele responde, na ordem em que as perguntas aparecem na vida real:

1. **O que é isso, afinal, e é legal?** → [`01`](01-introducao-leigo.md) e [`12`](12-etica-lei-e-contrato.md)
2. **Eu tenho o que é preciso para começar?** → [`02`](02-pre-requisitos.md)
3. **Como monto o laboratório sem quebrar nada nem cometer crime?** → [`03`](03-instalacao.md)
4. **Como invado minha primeira máquina hoje?** → [`04`](04-como-comecar.md)
5. **Qual é o passo a passo da carreira, mês a mês?** → [`25`](25-carreira-passo-a-passo.md)
6. **Como funciona cada técnica por dentro?** → Bloco B, do `13` ao `23`
7. **Como isso vira dinheiro e quanto custa?** → Blocos D e E

### Três avisos que valem o curso inteiro

1. **Sem autorização por escrito, não é hacking ético — é crime.** No Brasil, art. 154-A do
   Código Penal (Leis 12.737/2012 e 14.155/2021). Leia [`12`](12-etica-lei-e-contrato.md)
   **antes** de rodar qualquer ferramenta contra qualquer coisa que não seja seu.
2. **A parte técnica é a menor parte do trabalho.** O que separa um profissional de um
   entusiasta é o relatório ([`24`](24-relatorio-e-comunicacao.md)), não o exploit.
3. **Não existe "curso que forma hacker".** Existe rotina de laboratório sustentada por anos.
   O material inteiro está desenhado para dar essa rotina, não para dar certificado.

---

## O que você saberá ao final

- Explicar a um leigo o que é um teste de invasão e por que empresas pagam por isso.
- Saber exatamente o que é e o que não é legal, e como se proteger contratualmente.
- Montar um laboratório completo e isolado, em qualquer sistema operacional.
- Executar as cinco fases de um pentest: reconhecimento, varredura, exploração,
  pós-exploração, relatório.
- Ler e usar as metodologias reais do mercado (PTES, OWASP WSTG, NIST SP 800-115, MITRE ATT&CK).
- Encontrar e explorar as classes do OWASP Top 10:2025 em ambiente autorizado — e explicar
  a causa-raiz de cada uma, não só o payload.
- Atacar e defender um domínio Active Directory, que é onde a maior parte do dinheiro está.
- Entender exploração de memória a ponto de escrever um *buffer overflow* de pilha do zero.
- Escrever um relatório que um diretor entenda e um desenvolvedor consiga corrigir.
- Escolher entre pentest, bug bounty, red team, AppSec e purple team com dados de custo real.
- Saber quais certificações valem dinheiro no Brasil em 2026 e quais são só selo.

---

## Roteiro de leitura

### Caminho "quero entender do que se trata" (uma tarde)
[`01`](01-introducao-leigo.md) → [`12`](12-etica-lei-e-contrato.md) → [`25`](25-carreira-passo-a-passo.md) → [`80`](80-custos-e-licencas.md)

### Caminho do iniciante absoluto (primeiros 3 meses)
[`01`](01-introducao-leigo.md) → [`02`](02-pre-requisitos.md) → [`03`](03-instalacao.md) →
[`04`](04-como-comecar.md) → [`10`](10-fundamentos.md) → [`12`](12-etica-lei-e-contrato.md) →
[`06`](06-exemplos.md) → [`07-projeto-modelo/`](07-projeto-modelo/README.md) → [`70`](70-pratica.md)

### Caminho do pentester de rede
[`13`](13-metodologias-e-frameworks.md) → [`14`](14-reconhecimento-e-osint.md) →
[`15`](15-varredura-e-enumeracao.md) → [`16`](16-vulnerabilidades-e-exploracao.md) →
[`17`](17-pos-exploracao-e-movimentacao.md) → [`19`](19-redes-e-wireless.md) →
[`20`](20-active-directory.md) → [`24`](24-relatorio-e-comunicacao.md)

### Caminho do hacker web / bug bounty
[`18`](18-seguranca-web.md) → [`05`](05-manual-de-uso.md) → [`06`](06-exemplos.md) →
[`07-projeto-modelo/`](07-projeto-modelo/README.md) → [`21`](21-nuvem-e-containers.md) →
[`70`](70-pratica.md) → [`85`](85-cursos-e-certificacoes.md)

### Caminho do pesquisador
[`10`](10-fundamentos.md) → [`11`](11-historia.md) → [`16`](16-vulnerabilidades-e-exploracao.md) →
[`60`](60-teoria-avancada.md) → [`65`](65-estado-da-arte.md) → [`95`](95-referencias.md)

### Caminho de quem contrata ou decide
[`01`](01-introducao-leigo.md) → [`12`](12-etica-lei-e-contrato.md) →
[`13`](13-metodologias-e-frameworks.md) → [`24`](24-relatorio-e-comunicacao.md) →
[`80`](80-custos-e-licencas.md) → [`75`](75-armadilhas.md)

---

## Estrutura dos arquivos

### Bloco A · Porta de entrada
| Arquivo | Conteúdo | Nível |
|---|---|---|
| [`01-introducao-leigo.md`](01-introducao-leigo.md) | O que é hacking ético sem uma linha de jargão | iniciante |
| [`02-pre-requisitos.md`](02-pre-requisitos.md) | O que saber antes, tempo realista, rota de resgate | iniciante |
| [`03-instalacao.md`](03-instalacao.md) | Laboratório completo por SO: virtualização, Kali, alvos, Burp, Docker | iniciante |
| [`04-como-comecar.md`](04-como-comecar.md) | Do lab pronto à primeira máquina invadida | iniciante |
| [`05-manual-de-uso.md`](05-manual-de-uso.md) | Referência de comandos por tarefa: nmap, ffuf, Burp, Metasploit, netexec | intermediário |
| [`06-exemplos.md`](06-exemplos.md) | 14 exemplos completos, do trivial ao caso real | intermediário |
| [`07-projeto-modelo/`](07-projeto-modelo/README.md) | App vulnerável + pentest completo + relatório + correção | intermediário |

### Bloco B · Núcleo
| Arquivo | Conteúdo | Nível |
|---|---|---|
| [`10-fundamentos.md`](10-fundamentos.md) | Vocabulário, CIA, risco, CVE/CVSS, superfície de ataque, modelos mentais | iniciante |
| [`11-historia.md`](11-historia.md) | Do MIT de 1959 ao mercado de exploits de 2026 | iniciante |
| [`12-etica-lei-e-contrato.md`](12-etica-lei-e-contrato.md) | Lei brasileira, LGPD, escopo, RoE, safe harbor, casos reais | **obrigatório** |
| [`13-metodologias-e-frameworks.md`](13-metodologias-e-frameworks.md) | PTES, OSSTMM, NIST 800-115, OWASP WSTG, MITRE ATT&CK, Kill Chain | intermediário |
| [`14-reconhecimento-e-osint.md`](14-reconhecimento-e-osint.md) | Passivo, ativo, OSINT, subdomínios, vazamentos, pegada humana | intermediário |
| [`15-varredura-e-enumeracao.md`](15-varredura-e-enumeracao.md) | TCP/IP na prática, nmap por dentro, enumeração de serviços | intermediário |
| [`16-vulnerabilidades-e-exploracao.md`](16-vulnerabilidades-e-exploracao.md) | Classes de bug, exploit, shell, memória, buffer overflow passo a passo | avançado |
| [`17-pos-exploracao-e-movimentacao.md`](17-pos-exploracao-e-movimentacao.md) | Escalada de privilégio, persistência, pivoting, credenciais | avançado |
| [`18-seguranca-web.md`](18-seguranca-web.md) | OWASP Top 10:2025 explicado por causa-raiz, com laboratório | intermediário |
| [`19-redes-e-wireless.md`](19-redes-e-wireless.md) | ARP, DNS, MITM, VLAN, 802.11, WPA2/WPA3 | avançado |
| [`20-active-directory.md`](20-active-directory.md) | Kerberos, NTLM, ACL, caminhos de ataque, BloodHound | avançado |
| [`21-nuvem-e-containers.md`](21-nuvem-e-containers.md) | IAM, metadata service, S3, Kubernetes, escape de container | avançado |
| [`22-mobile-e-hardware.md`](22-mobile-e-hardware.md) | Android/iOS, IoT, firmware, rádio, canal lateral | avançado |
| [`23-engenharia-social.md`](23-engenharia-social.md) | Phishing autorizado, pretexting, físico, e os limites éticos | intermediário |
| [`24-relatorio-e-comunicacao.md`](24-relatorio-e-comunicacao.md) | O produto que o cliente compra: estrutura, CVSS, retest, reunião | **obrigatório** |
| [`25-carreira-passo-a-passo.md`](25-carreira-passo-a-passo.md) | **Plano de 24 meses**, papéis, portfólio, primeiro emprego | iniciante |
| [`60-teoria-avancada.md`](60-teoria-avancada.md) | Indecidibilidade, mitigações de memória, fuzzing, execução simbólica | pesquisa |
| [`65-estado-da-arte.md`](65-estado-da-arte.md) | Agentes de IA ofensiva, memory-safe, pós-quântica, supply chain | pesquisa |

### Bloco C · Prática e erros
| Arquivo | Conteúdo |
|---|---|
| [`70-pratica.md`](70-pratica.md) | 12 laboratórios progressivos, do `nmap localhost` ao domínio inteiro |
| [`75-armadilhas.md`](75-armadilhas.md) | 25 erros clássicos, mitos e por que persistem |

### Bloco D · Economia e ecossistema
| Arquivo | Conteúdo |
|---|---|
| [`80-custos-e-licencas.md`](80-custos-e-licencas.md) | Preços de tudo com data de consulta, licenças, custo oculto, salários |
| [`85-cursos-e-certificacoes.md`](85-cursos-e-certificacoes.md) | Cursos gratuitos PT/EN/FR e certificações que valem (e as que não) |

### Bloco E · Fontes
| Arquivo | Conteúdo |
|---|---|
| [`90-bibliografia.md`](90-bibliografia.md) | Livros comentados, o que envelheceu, o que é legalmente gratuito |
| [`95-referencias.md`](95-referencias.md) | Papers, specs, docs, pessoas a seguir, feeds |
| [`GLOSSARIO.md`](GLOSSARIO.md) | ~170 termos definidos |

---

## As 12 camadas de profundidade — onde cada uma está

| # | Camada | Onde |
|---|---|---|
| 1 | Intuição para leigo | `01` |
| 2 | Definição informal | `01`, `10` |
| 3 | Por que existe | `11` |
| 4 | Ambiente e primeiro uso | `03`, `04` |
| 5 | Fundamentos formais | `10`, `13` |
| 6 | Mecânica interna | `15`, `16`, `19`, `20` |
| 7 | Implementação prática | `05`, `06`, `07`, `70` |
| 8 | Casos de uso reais | `06` (ex. 13–14), `24`, `07-projeto-modelo/` |
| 9 | Trade-offs e alternativas | `13`, `75`, `25` |
| 10 | Economia do assunto | `80`, `85` |
| 11 | Profundidade de pesquisa | `60` |
| 12 | Estado da arte | `65` |

---

## Status por bloco

| Bloco | Status | Observação |
|---|---|---|
| A · Porta de entrada | ✅ | Instalação pesquisada na web em 12/08/2026 (Kali 2026.2) |
| B · Núcleo | ✅ | 18 arquivos, do `10` ao `65` |
| C · Prática e erros | ✅ | 12 laboratórios, 25 armadilhas |
| D · Economia | ✅ | Preços consultados em 12/08/2026, com fonte |
| E · Fontes | ✅ | Bibliografia e referências verificadas |
| Glossário | ✅ | ~170 termos |

**Pendente:** nada de estrutura. Reavaliar [`65`](65-estado-da-arte.md) e
[`80`](80-custos-e-licencas.md) a cada 6 meses — o mercado de certificação e o de IA ofensiva
mudam rápido. Se o OWASP publicar a lista 2028, revisar [`18`](18-seguranca-web.md).

---

## Autoteste do mapa

1. Qual arquivo você **precisa** ler antes de rodar qualquer ferramenta contra qualquer alvo?
2. Onde está a resposta direta para "como começo a carreira, mês a mês"?
3. Qual é a diferença de caminho de leitura entre quem quer fazer bug bounty e quem quer
   fazer pentest de rede?
4. Em qual arquivo está a explicação de por que empresas pagam por isso?
5. Se você só tem uma tarde, quais quatro arquivos lê?
