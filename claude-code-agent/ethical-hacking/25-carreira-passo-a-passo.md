# 25 · Carreira — o passo a passo, mês a mês

`Nível: iniciante` · `Última atualização: 12/08/2026`

Este é o arquivo que responde diretamente "como inicio nessa carreira e qual o passo a passo".
É um plano realista, não uma promessa de curso. Ajuste os prazos à sua vida — a **ordem** é o
que importa.

---

## 1. A verdade que ninguém vende antes de você pagar

**Pentester quase nunca é primeiro emprego.** A esmagadora maioria dos profissionais chegou lá
por uma porta lateral: suporte, redes, infraestrutura, desenvolvimento ou SOC. Isso não é
burocracia do mercado — é que **você não quebra bem o que nunca construiu ou operou**. Quem
nunca administrou um Active Directory tem dificuldade de atacá-lo com profundidade; quem nunca
programou tem dificuldade de achar bug em código.

Então o "passo a passo" tem duas fases que se sobrepõem:
1. **Construir a base** (fundamentos + um primeiro emprego em TI, se você não tem).
2. **Especializar em ofensiva** (laboratório, certificação, portfólio, primeira vaga de segurança).

Se você **já trabalha em TI**, pule direto para a fase 2 e some ~12–18 meses.
Se vem **de fora**, conte 24–36 meses até o primeiro salário na área. Isso é o normal.

## 2. Mapa de papéis — para onde você pode ir

"Ethical hacker" não é um cargo único. É uma família:

| Papel | O que faz | Porta de entrada boa? |
|---|---|---|
| **SOC Analyst (Blue)** | monitora, detecta, responde a incidentes | ✅ **melhor porta de entrada** |
| **Pentester (rede/infra)** | testa redes internas/externas, AD | meta comum |
| **AppSec / Pentester web** | testa aplicações e APIs, revisa código | ✅ boa se você programa |
| **Red Teamer** | simula adversário real, longa duração | sênior; não é entrada |
| **Bug Bounty Hunter** | falhas pagas por resultado, autônomo | complemento, renda instável |
| **Cloud Security** | segurança de AWS/Azure/GCP, K8s | crescente, bem pago |
| **Purple Team** | integra ataque e defesa | intermediário/sênior |
| **Vuln Researcher / Exploit Dev** | acha 0-day, escreve exploit | nicho, muito técnico |

**Recomendação honesta:** mire **SOC** ou **AppSec** como primeiro emprego de segurança, mesmo
que seu sonho seja red team. Você entra, ganha salário, vê o lado defensivo (que te faz um
atacante muito melhor), e migra em 1–2 anos. Tentar entrar direto como pentester sênior sem
base é a receita da frustração.

## 3. O plano de 24 meses (para quem começa quase do zero)

Assume ~14h/semana de estudo consistente. Ajuste para a sua realidade — dobrar o tempo, dobra
a velocidade; metade, metade.

### Meses 1–3 · Fundamentos (a base inegociável)
- **Linux:** OverTheWire Bandit 0→20. ([`02`](02-pre-requisitos.md) §1.1)
- **Redes:** TryHackMe "Pre Security" + noções de TCP/IP. ([`02`](02-pre-requisitos.md) §1.2)
- **Web:** como HTTP funciona, cliente × servidor. ([`02`](02-pre-requisitos.md) §1.3)
- **Ética e lei:** leia [`12`](12-etica-lei-e-contrato.md) inteiro. Interiorize a regra de ouro.
- **Ambiente:** monte o laboratório ([`03`](03-instalacao.md)) e invada o Metasploitable ([`04`](04-como-comecar.md)).
- **Hábito:** escolha a ferramenta de notas e comece a anotar tudo hoje.
- **Meta do trimestre:** resolver uma máquina "fácil" seguindo raciocínio próprio.

### Meses 4–6 · Primeiro contato ofensivo
- **Web a fundo:** PortSwigger Web Security Academy — as trilhas de SQLi, XSS, Access Control.
- **Trilha estruturada:** TryHackMe "Jr Penetration Tester" ou "Complete Beginner".
- **Prática:** 15–20 máquinas fáceis (THM/HTB), **escrevendo write-up de cada uma**.
- **Primeira certificação (opcional, barata):** **eJPT** (INE, ~US$ 299) ou **PJPT** (TCM).
  Não pelo selo — pela estrutura de estudo e por ter algo no currículo. Ver [`85`](85-cursos-e-certificacoes.md).
- **Meta:** completar o projeto-modelo ([`07`](07-projeto-modelo/README.md)) e entender cada falha.

### Meses 7–12 · Consolidação + (se preciso) primeiro emprego em TI
- **Se você NÃO trabalha com TI:** este é o momento de conseguir um emprego de **suporte, help
  desk, NOC ou SOC nível 1**. Aceite o salário de entrada. É o pedágio mais rápido para a área
  e você aprende operando de verdade. Não subestime: 12 meses de SOC valem ouro num currículo
  de segurança.
- **Active Directory:** monte o GOAD ([`20`](20-active-directory.md)) e faça a cadeia completa.
  É o que mais cai em entrevista de pentest.
- **Prática:** máquinas médias, mais AD, mais web real.
- **Portfólio:** GitHub com seus write-ups e ferramentas simples que você escreveu.
- **Comunidade:** entre em Discords, vá a um evento (BSides, Roadsec, H2HC no Brasil).
- **Meta:** você resolve máquinas médias sozinho e tem 20+ write-ups públicos.

### Meses 13–18 · Especialização e certificação de peso
- **Escolha um foco:** rede/AD (→ OSCP/CPTS/PNPT) **ou** web/API (→ CBBH/BSCP + bug bounty).
- **Certificação séria:**
  - **HTB CPTS** (~US$ 210 + assinatura Academy) — prático, muito respeitado, custo-benefício.
  - **PNPT** (TCM, ~US$ 499) — prático, com relatório e componente de AD, ótimo valor.
  - **OSCP** (OffSec, ~US$ 1.749) — o mais reconhecido pelo RH, caro, difícil.
  - Ver comparação honesta em [`85`](85-cursos-e-certificacoes.md).
- **Bug bounty (se web):** comece na HackerOne/Bugcrowd, programas com escopo amplo, expectativa
  realista (ver [`80`](80-custos-e-licencas.md)).
- **Meta:** uma certificação prática no bolso + portfólio sólido.

### Meses 19–24 · Transição para vaga de segurança
- **Candidate-se** a vagas de pentester júnior, AppSec júnior, analista de segurança ofensiva.
  Muitas são remotas.
- **Prepare-se para entrevista:** explique a cadeia de um pentest, mostre write-ups, saiba
  explicar (não só executar) as técnicas. Entrevista técnica pergunta "por quê", não só "qual
  comando".
- **Networking real:** a maioria das primeiras vagas vem de indicação da comunidade, não de
  candidatura fria. Esteja presente.
- **Meta:** primeiro emprego com "segurança" no título.

## 4. Se você já trabalha com TI — o plano acelerado (12–18 meses)

Você já tem a base operacional. Foque:
1. **Meses 1–2:** fundamentos ofensivos (PortSwigger Academy + THM Jr Pentester).
2. **Meses 3–6:** laboratório pesado — HTB/THM médias, GOAD, projeto-modelo, write-ups.
3. **Meses 6–10:** certificação prática (CPTS ou PNPT), especialização no seu forte (se você é
   dev → AppSec; se é infra → AD/rede).
4. **Meses 9–15:** candidatar-se **internamente** primeiro (migrar para o time de segurança da
   sua própria empresa é a transição mais fácil que existe) e externamente.

Migração interna é o atalho mais subestimado. Sua empresa já confia em você; o time de
segurança prefere alguém que conhece o ambiente.

## 5. O portfólio — o que realmente conta

Certificado abre porta; **portfólio prova competência**. Construa desde o mês 1:
- **Write-ups** de máquinas/labs que você resolveu (blog, GitHub, Medium). Mostram raciocínio.
- **Ferramentas** que você escreveu, mesmo simples (um script que automatiza uma enumeração).
- **Contribuições** a projetos open source de segurança.
- **CVEs ou reconhecimentos** de bug bounty (o mais forte, se conseguir).
- **CTFs:** participação e ranking, se você curte.

> **Opinião profissional:** um candidato com 30 write-ups bem escritos e sem OSCP costuma ser
> mais empregável que um com OSCP e nenhum portfólio. O certificado diz "passei numa prova"; o
> portfólio diz "eu penso assim, todo dia". Contrata-se o segundo.

## 6. Habilidades não técnicas que decidem a carreira

- **Escrita.** Relatório é o produto ([`24`](24-relatorio-e-comunicacao.md)). Quem escreve bem
  sobe mais rápido. Treine escrevendo write-ups.
- **Comunicação com não técnicos.** Traduzir risco técnico em risco de negócio é raro e caro.
- **Ética sob pressão.** Um deslize acaba a carreira ([`12`](12-etica-lei-e-contrato.md)).
- **Aprendizado contínuo.** O campo muda todo mês. Quem para de estudar, obsoletece em 2 anos.
- **Gestão de frustração.** Já falado em [`02`](02-pre-requisitos.md) §4.1: a profissão é falhar
  muito. Se isso te destrói, reconsidere.

## 7. Erros de carreira que custam anos

| Erro | Consequência | Correção |
|---|---|---|
| Colecionar cursos sem praticar | sabe falar, não sabe fazer | 1h de lab > 4h de vídeo |
| Ficar 8 meses escolhendo a "melhor" cert | tempo perdido | escolha uma e comece hoje |
| Pular fundamento para ir ao exploit | trava no primeiro alvo diferente do tutorial | volte à base |
| Ignorar o lado defensivo | atacante raso | passe por SOC/blue, te faz melhor |
| Não escrever write-ups | sem portfólio, sem consolidação | escreva um por semana |
| Isolar-se | vagas vêm de rede | comunidade, eventos, Discord |
| Esperar o "momento certo" para se candidatar | ele nunca vem | candidate-se antes de se sentir pronto |

## 8. Expectativa financeira (resumo — detalhes em [`80`](80-custos-e-licencas.md))

- **SOC júnior / suporte (porta de entrada):** salário de entrada de TI.
- **Pentester júnior/pleno:** cresce rápido; a área paga acima da média de TI.
- **Sênior / especialista / cloud / red team:** entre os melhores salários de TI, muitos remotos
  para o exterior.
- **Bug bounty:** renda **muito** variável; complemento, não substituto, até você ser muito bom.

Números concretos com fonte e data em [`80-custos-e-licencas.md`](80-custos-e-licencas.md).

## 9. Roteiro de um dia de estudo produtivo

Para não se perder: 45–90 min/dia bem usados batem 8h de sábado disperso.
```
10 min  — revisar notas de ontem
40 min  — laboratório com as mãos (uma máquina, um lab da PortSwigger)
15 min  — escrever o que aprendeu (write-up, mesmo curto)
5 min   — anotar a próxima dúvida a investigar
```

---

## Autoteste

1. Por que pentester quase nunca é primeiro emprego, e qual é a melhor porta de entrada?
2. Qual é a diferença de tempo esperada entre quem já trabalha com TI e quem vem de fora?
3. Por que passar pelo lado defensivo (SOC/blue) te torna um atacante melhor?
4. Na ordem do plano, o que vem antes: certificação de peso (OSCP) ou fundamentos + portfólio?
5. Por que um portfólio de write-ups pode valer mais que um certificado?
6. Qual é o atalho de transição mais subestimado para quem já trabalha na empresa?
7. Cite três erros de carreira que custam anos e a correção de cada um.
8. Qual é a estrutura de um dia de estudo produtivo, e por que a prática vem antes do vídeo?
