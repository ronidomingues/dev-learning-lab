# 11 · História — de onde veio o hacking (e a ética)

`Nível: iniciante` · `Última atualização: 12/08/2026`

Saber a história não é enfeite: ela explica por que as ferramentas são como são, por que as
leis existem, e por que certos debates se repetem. Quem conhece a história reconhece a moda
que está voltando.

---

## 1. A palavra "hack" nasceu boa (1955–1970)

O termo "hack" surgiu no **Tech Model Railroad Club** e no laboratório de IA do **MIT**, nos
anos 1950–60. "Hack" era uma solução engenhosa, um truque elegante; "hacker" era quem
dominava um sistema a fundo e o dobrava para fazer algo novo. **Não havia conotação criminosa.**
A cultura valorizava curiosidade, mão na massa, compartilhar conhecimento e desconfiar da
autoridade — a chamada **ética hacker**, depois catalogada por Steven Levy em *Hackers* (1984).

**Por que importa:** a tensão original — curiosidade que "mexe onde não devia" — é a mesma
tensão ética da profissão hoje. A diferença que a lei impôs foi a **autorização**.

## 2. Phreaking: o telefone antes do computador (1960–1980)

Antes de redes de dados, hackear era hackear o **telefone**. Os *phreakers* descobriram que a
rede telefônica americana usava tons no próprio canal de voz para sinalização. **John Draper
("Captain Crunch")** notou que o apito de brinde da cereal Cap'n Crunch emitia exatamente
2600 Hz — o tom que liberava chamadas de longa distância grátis. Nasceram as *blue boxes* —
que dois jovens chamados **Steve Wozniak e Steve Jobs** venderam antes de fundar a Apple.

**Lição que atravessa décadas:** a falha do phreaking era **sinalização no mesmo canal dos
dados** (*in-band signaling*). A rede confiava em algo que o usuário controlava. É o mesmo erro
conceitual do "não confie no cliente" de hoje — a solução foi separar sinalização de voz
(*out-of-band*, sistema SS7). Falhas mudam de roupa, não de natureza.

## 3. Os primeiros worms e a primeira lei (1980s)

- **1983** — o filme *WarGames* populariza a imagem do adolescente que invade sistemas
  militares. O pânico moral que ele gerou influenciou diretamente a legislação.
- **1986** — os EUA aprovam o **Computer Fraud and Abuse Act (CFAA)**, a primeira grande lei
  anti-invasão. Até hoje é a base (e a polêmica) do direito penal informático americano.
- **1988** — o **Morris Worm**, escrito por Robert Tappan Morris, se espalha e derruba boa
  parte da internet nascente. Foi a primeira condenação sob o CFAA. Morris hoje é professor
  do MIT — símbolo de que a linha entre pesquisa e crime é a autorização.

**Por que importa:** o CFAA e seus equivalentes (no Brasil, a Lei 12.737/2012) criaram a
distinção jurídica entre o white hat e o black hat. Antes disso, "hacking" era ambíguo; depois,
sem autorização passou a ser crime. Ver [`12-etica-lei-e-contrato.md`](12-etica-lei-e-contrato.md).

## 4. A profissionalização (1990s)

- Surgem grupos como **L0pht** e **Cult of the Dead Cow**, que fazem *full disclosure* —
  publicar falhas para forçar fabricantes a corrigir. Em 1998, o L0pht diz ao Senado dos EUA
  que poderia "derrubar a internet em 30 minutos". Nasce o debate **full disclosure ×
  responsible disclosure** que continua vivo.
- **1995** — Dan Farber e Wietse Venema lançam o **SATAN**, primeiro scanner de vulnerabilidade
  de rede amplamente usado. A imprensa entra em pânico com "ferramenta que ensina a invadir".
- **1997** — surge o **nmap**, de Gordon "Fyodor" Lyon. Continua sendo a ferramenta mais usada
  do campo, quase 30 anos depois. Ver [`15`](15-varredura-e-enumeracao.md).
- **1998** — o termo **"penetration testing"** já é usado comercialmente; empresas começam a
  contratar testes autorizados como serviço.

## 5. A era do crime organizado e do Estado (2000s)

O hacking sai do quarto do adolescente e vira **indústria** — dos dois lados.

- **Crime como negócio:** botnets, roubo de cartão em escala, malware como serviço. O motivo
  passa a ser dinheiro, não curiosidade.
- **Estados entram no jogo:** o worm **Stuxnet** (descoberto em 2010), atribuído a EUA/Israel,
  sabotou centrífugas nucleares iranianas usando **quatro 0-days** do Windows. Foi a prova
  pública de que armas cibernéticas patrocinadas por Estados eram reais. Mudou a percepção do
  campo para sempre.
- **Metasploit (2003)**, de H.D. Moore, transforma exploração num framework acessível.
  Comprado pela Rapid7 em 2009. Democratizou o exploit — para o bem e para o mal.
- **OWASP** é fundada em 2001; o primeiro **OWASP Top 10** sai em 2003 e vira a referência de
  segurança web. Ver [`18`](18-seguranca-web.md).

## 6. Bug bounty e a legitimação (2010s)

O que antes terminava em processo passou a terminar em cheque:

- **2013** — nasce a **HackerOne**; a **Bugcrowd** vem no mesmo período. Empresas passam a
  **pagar** pesquisadores por falhas, dentro de regras públicas. O "grey hat" que mandava
  e-mail com medo de processo agora tem um canal legal e remunerado.
- Programas de bug bounty de Google, Microsoft, Apple, e até do **Departamento de Defesa dos
  EUA** ("Hack the Pentagon", 2016) tornam o hacking ético mainstream.
- **Snowden (2013)** expõe a vigilância em massa e reacende o debate sobre 0-days: governos os
  **compram e estocam** em vez de reportar. Nasce o mercado cinza de exploits (Zerodium e
  outros pagam seis/sete dígitos por 0-day de iPhone).

**Debate ainda aberto:** é ético um pesquisador vender um 0-day para um broker que o revende a
governos? Onde termina a pesquisa e começa a arma? Não há consenso. Ver [`65`](65-estado-da-arte.md).

## 7. A década atual (2020–2026)

- **Ransomware** vira a maior ameaça prática: grupos criptografam redes inteiras e cobram
  resgate, muitas vezes com "dupla extorsão" (também vazam os dados). Isso aumentou a demanda
  por pentest e red team.
- **Cadeia de suprimentos** entra em foco: **SolarWinds (2020)** — atacantes comprometeram a
  atualização de um software usado por milhares de organizações, incluindo o governo dos EUA.
  **Log4Shell (CVE-2021-44228, dez/2021)** — uma falha numa biblioteca de log ubíqua expôs
  meio mundo em dias. Resultado: em 2025, a OWASP adiciona **A03 – Software Supply Chain
  Failures** ao Top 10.
- **Regulação aperta:** LGPD (Brasil, 2020), NIS2 e **Cyber Resilience Act** (UE, em vigor por
  etapas até dez/2027) transferem responsabilidade para fabricantes — o motor econômico atual
  da profissão.
- **IA ofensiva:** a partir de 2024–2025, agentes de IA começam a encontrar e explorar falhas
  de forma autônoma. Em jun/2025, o agente da **XBOW** chega ao topo do ranking de bug bounty
  da HackerOne nos EUA. É a virada tecnológica em curso. Ver [`65`](65-estado-da-arte.md).

## 8. Linha do tempo condensada

```
1955–60  MIT: nasce "hack" (sentido positivo)
1971     Captain Crunch: phreaking com 2600 Hz
1983     WarGames; pânico moral
1986     CFAA (1ª grande lei anti-invasão, EUA)
1988     Morris Worm; 1ª condenação
1995     nmap está a caminho; SATAN
1997     nmap 1.0
2001     OWASP fundada
2003     Metasploit; 1º OWASP Top 10
2009     Rapid7 compra Metasploit
2010     Stuxnet revelado (arma de Estado, 4 0-days)
2012     Brasil: Lei 12.737 (Carolina Dieckmann)
2013     HackerOne/Bugcrowd; Snowden
2016     Hack the Pentagon
2020     SolarWinds; LGPD entra em vigor
2021     Log4Shell
2025     OWASP Top 10:2025 (supply chain entra); XBOW no topo do bug bounty
2026     IA ofensiva em produção; CRA europeu em implementação
```

## 9. O que a história ensina ao iniciante

1. **A autorização é a invenção jurídica que criou a profissão.** Sem ela, você é o Morris de
   1988, não o professor do MIT de hoje.
2. **As falhas se repetem em roupas novas.** "Não confie no canal que o usuário controla"
   (phreaking, 1971) é "não confie no cliente" (web, 2026).
3. **A economia manda.** O campo cresce quando o custo do defeito é jogado no fabricante
   (regulação) ou quando pagar por falha fica mais barato que sofrer o vazamento (bug bounty).
4. **Toda ferramenta é dual.** SATAN, Metasploit, nmap, e agora IA — todas geraram pânico de
   "isso ensina a invadir" e todas viraram instrumento de defesa. O pânico é previsível; a
   ferramenta, inevitável.

---

## Autoteste

1. Qual era o sentido original de "hacker", e onde ele nasceu?
2. Qual falha conceitual o phreaking explorava, e como ela se parece com falhas web atuais?
3. Qual foi a primeira grande lei anti-invasão, e o que o Morris Worm tem a ver com ela?
4. O que o Stuxnet provou ao mundo?
5. Como o bug bounty mudou a situação legal do pesquisador de segurança?
6. Que dois incidentes levaram a OWASP a criar a categoria de cadeia de suprimentos em 2025?
7. Segundo a história, qual é a "invenção" que separa o hacking ético do crime?
8. Dê um exemplo de como "as falhas se repetem em roupas novas".
