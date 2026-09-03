# 58 · Inglês para tecnologia e trabalho remoto internacional

`Nível: intermediário → avançado` · `Última atualização: 31/08/2026`

> Arquivo de aplicação. Se você trabalha (ou quer trabalhar) com tecnologia, este é o retorno
> mais rápido do curso inteiro: o vocabulário é fechado, os gêneros são poucos e repetitivos, e
> dominar ~300 itens já muda a sua vida profissional.

---

## 58.1 Por que este inglês é mais fácil do que parece

| Característica | Consequência |
|---|---|
| vocabulário técnico é **latino** | *implementation, configuration, authentication* — quase idênticas ao português |
| gêneros são poucos e ritualizados | PR, issue, standup, retro, design doc, code review |
| o **conteúdo** você já domina | você adivinha vocabulário pelo contexto com precisão alta |
| a maioria dos interlocutores é **não-nativa** | ELF: ninguém espera sotaque perfeito ([55](55-pragmatica-e-variacao.md) §55.6) |
| é assíncrono na maior parte do tempo | você tem tempo para revisar antes de enviar |

**A parte difícil não é o vocabulário. É a pragmática:** soar colaborativo em vez de ríspido,
discordar sem atritar, pedir sem mandar, e falar em reunião sem travar.

---

## 58.2 As 60 palavras e expressões que você usa toda semana

### Fluxo de trabalho
| Termo | Significado |
|---|---|
| ship / roll out / deploy | colocar em produção |
| roll back / revert | desfazer |
| merge / rebase / cherry-pick | operações de Git |
| branch off / cut a branch | criar ramo |
| PR (*pull request*) / MR | pedido de mesclagem |
| LGTM (*looks good to me*) | aprovado |
| PTAL (*please take another look*) | revise de novo |
| WIP (*work in progress*) | não revise ainda |
| nit / nitpick | detalhe menor, não bloqueia |
| blocker | o que impede o trabalho |
| backlog | fila de trabalho |
| scope creep | escopo inchando |
| tech debt | dívida técnica |
| bandwidth | ⚠️ **tempo/capacidade pessoal**, não internet: *"I don't have bandwidth this week"* |
| on call | de plantão |
| triage | classificar por prioridade |
| spike | investigação com prazo fixo |
| flaky test | teste que falha de forma intermitente |
| edge case / corner case | caso extremo |
| happy path | caminho sem erro |
| regression | algo que voltou a quebrar |
| root cause | causa raiz |
| postmortem | análise pós-incidente |
| workaround | solução paliativa |
| dogfooding | usar o próprio produto |
| bikeshedding | discutir o trivial |
| yak shaving | fazer coisas encadeadas até esquecer o objetivo |
| rubber ducking | explicar em voz alta para achar o erro |

### Reunião e organização
| Termo | Significado |
|---|---|
| standup / daily | reunião curta diária |
| retro (*retrospective*) | o que foi bem/mal |
| sync / 1:1 | reunião de alinhamento / individual |
| offsite | encontro presencial fora |
| action item | tarefa saída da reunião |
| take it offline | tratar fora desta reunião |
| circle back | voltar ao assunto depois |
| loop someone in | incluir alguém |
| heads-up | aviso prévio |
| ballpark (figure) | estimativa grosseira |
| low-hanging fruit | ganho fácil |
| ping me | me chame |
| EOD / EOW / COB | fim do dia / da semana / do expediente |
| ASAP | o quanto antes |
| OOO (*out of office*) | fora do escritório |
| PTO (*paid time off*) | férias/folga |
| async | assíncrono |
| blocked on X | parado esperando X |

⚠️ **Falsos amigos do jargão:** `bandwidth` (tempo, não rede) · `ping` (chamar alguém, não ICMP) ·
`ship` (lançar, não enviar por navio) · `sync` (reunião, não sincronização de dados) ·
`bump` (subir a mensagem, não colidir).

---

## 58.3 Ler documentação — a estrutura que se repete

Toda boa documentação técnica em inglês segue mais ou menos a mesma ordem. Reconhecê-la faz você
achar a informação sem ler tudo:

| Seção | O que tem | Palavras-guia |
|---|---|---|
| Overview / Introduction | o que é, para quê | *provides, allows you to, is designed to* |
| Prerequisites | o que precisa antes | *requires, assumes, must have* |
| Getting Started / Quickstart | o exemplo mínimo | *first, then, finally* |
| Reference / API | tabelas de parâmetros | *returns, accepts, defaults to, optional* |
| Guides / How-to | receitas por tarefa | *to do X, follow these steps* |
| Troubleshooting | erros comuns | *if you see, this usually means* |
| Migration | como sair da versão anterior | *breaking change, deprecated, replaced by* |

### Vocabulário de aviso — o que muda o sentido de tudo

| Termo | Significa |
|---|---|
| **deprecated** | ainda funciona, **vai** ser removido; migre |
| **breaking change** | quebra código existente |
| **experimental / beta / preview** | pode mudar sem aviso |
| **stable / GA** (*general availability*) | pronto para produção |
| **EOL** (*end of life*) | sem suporte, nem de segurança |
| **legacy** | antigo, mantido por compatibilidade |
| **out of scope** | não coberto por este documento |
| **as of version X** | a partir da versão X |
| **prior to version X** | antes da versão X |
| **subject to change** | pode mudar |
| **at your own risk** | sem garantia |
| **note / warning / caution / danger** | escala de gravidade, do menor ao maior |

### RFC 2119 — as palavras com força normativa

Em especificações técnicas (RFCs, padrões W3C, ISO), estas palavras têm significado **definido**:

| Palavra | Significa exatamente |
|---|---|
| **MUST / SHALL / REQUIRED** | obrigatório; não cumprir viola a especificação |
| **MUST NOT / SHALL NOT** | proibido |
| **SHOULD / RECOMMENDED** | há razões válidas para não fazer, mas pondere antes |
| **SHOULD NOT** | desaconselhado, mas pode haver exceção |
| **MAY / OPTIONAL** | totalmente facultativo |

⭐ Confundir `SHOULD` com `MUST` ao ler uma especificação é fonte real de bug de
interoperabilidade. Em documento técnico, essas palavras não são estilo — são contrato.

---

## 58.4 Escrever bem no dia a dia técnico

### Mensagem de commit

```
Fix race condition in session refresh

Two concurrent requests could refresh the same session, and the second
one would overwrite the token issued by the first, logging the user out.

Add a per-session lock so the second request waits and reuses the token.

Fixes #4821
```
**Convenções:** primeira linha no **imperativo** (*Fix*, *Add*, *Remove* — não *Fixed*, não
*Fixing*), até ~50 caracteres, sem ponto final. Linha em branco. Corpo explicando **por quê**,
não o quê (o diff já diz o quê). Referência à issue no fim.

⚠️ Este é o único lugar da comunicação técnica onde o **imperativo puro é a norma** — porque a
frase completa é *"[this commit will] Fix race condition"*, e o sujeito é o commit, não a pessoa.

### Descrição de PR e comentário de review
Modelo completo e as quatro temperaturas de comentário estão em
[06-exemplos](06-exemplos.md) §Exemplo 11.

⚠️ **A regra pragmática mais importante do trabalho técnico:** em texto assíncrono, o imperativo
puro (*"Change this."*, *"Remove it."*) soa como ordem, por transferência do português onde ele é
neutro. Envolva em pergunta ou sugestão: *"Could we...?"*, *"What do you think about...?"*,
*"nit: maybe..."*.

### Reportar um bug
Esqueleto de cinco movimentos em [06-exemplos](06-exemplos.md) §Exemplo 5:
o que acontece → o que não acontece → o que já tentei → quando começou → o que funciona.

### Design doc / RFC interno
```
# Title
## Context / Background     por que estamos falando disso
## Problem                  o que está errado hoje
## Goals / Non-goals        ⭐ non-goals evita metade das discussões
## Proposal                 o que se propõe
## Alternatives considered  ⭐ o que foi descartado e por quê
## Risks / Trade-offs
## Rollout plan
## Open questions
```
⭐ **Non-goals** e **Alternatives considered** são as duas seções que separam um documento
profissional de um amador em cultura de engenharia anglófona. A ausência delas é notada.

---

## 58.5 Reunião — sobreviver e depois participar

Os ~20 blocos essenciais estão em [06-exemplos](06-exemplos.md) §Exemplo 9. Aqui, o que é
específico de reunião técnica remota.

### Standup — o formato fixo (30–60 segundos)
```
"Yesterday I finished the migration script and started on the tests.
 Today I'll wrap up the tests and open the PR.
 I'm blocked on the staging credentials — Ana, could you help with that after this?"
```
Três movimentos: **ontem → hoje → bloqueios**. Prepare em 30 s antes de entrar. Escreva se
precisar. Ler não é vergonha.

### Problemas específicos da chamada remota
| Problema | Frase |
|---|---|
| áudio ruim | *"Sorry, you're breaking up. Could you repeat that?"* |
| falaram junto | *"Sorry, go ahead."* / *"After you."* |
| não sabe se ouviram | *"Can you hear me okay?"* |
| quer compartilhar tela | *"Let me share my screen."* |
| perdeu o fio | *"Sorry, I lost you for a second — where are we?"* |
| precisa sair | *"I have a hard stop at the top of the hour."* |
| quer encerrar o assunto | *"Should we take this offline?"* |

### Apresentar em inglês
- **Escreva a primeira e a última frase.** São as que mais travam.
- Frases curtas. Uma ideia por slide.
- Sinalize a estrutura: *"There are three things I want to cover. First, ..."*
- Ensaie **em voz alta**, cronometrado, três vezes. Não leia mentalmente.
- Prepare a resposta para *"Any questions?"* — incluindo *"Good question. Let me get back to you
  with the exact number."*

---

## 58.6 Entrevista técnica internacional

Formato completo (STAR) e a análise linguística em [06-exemplos](06-exemplos.md) §Exemplo 12.
Aqui, o que é específico da entrevista técnica:

### Pensar em voz alta durante o problema
Esperado em entrevista de código. Silêncio é interpretado como travamento.

```
"Let me make sure I understand the problem. We're given ... and we need to ...
 Is that right?"
"My first thought is a brute-force approach — that'd be O(n²). Let me see if
 we can do better."
"I'm going to use a hash map here to bring the lookup down to constant time."
"Let me trace through an example to make sure this works."
"One edge case I want to handle is an empty input."
```

### Vocabulário de complexidade e arquitetura
*time/space complexity · O(n) "big O of n" · trade-off · bottleneck · scale horizontally ·
throughput · latency · consistency · idempotent · race condition · single point of failure ·
graceful degradation · backward compatible*

### Perguntas para fazer no fim (ter três é obrigatório)
- *"What does success look like in this role in the first six months?"*
- *"How does the team handle code review and on-call?"*
- *"What's the biggest technical challenge the team is facing right now?"*

⚠️ Dizer *"No, I don't have any questions"* é lido como desinteresse. É um erro real que custa
vagas.

---

## 58.7 Como estudar isso, especificamente

| Fonte | Como usar |
|---|---|
| **A documentação que você já lê** | leia em inglês, sempre. Nunca a versão traduzida |
| **O changelog das suas ferramentas** | inglês técnico curto, denso e repetitivo — ideal |
| **Postmortems públicos** (Cloudflare, GitHub, AWS) | ⭐ o melhor material que existe: narrativa técnica real, bem escrita |
| **Conference talks no YouTube** | legenda em inglês; ~40 min do seu assunto |
| **Podcasts técnicos** | conversa real entre não-nativos e nativos |
| **Issues e PRs de projetos open source** | ⭐ pragmática real: veja como as pessoas discordam |
| **Escrever seus commits em inglês** | prática diária, custo zero, retorno alto |
| **Escrever suas notas em inglês** | idem |

> **A recomendação mais eficiente que tenho para dar a um profissional de tecnologia brasileiro:**
> passe **toda** a sua vida técnica para o inglês — sistema operacional, buscas, notas, commits,
> documentação. Isso converte 6–8 horas diárias de trabalho em contato com a língua, sem nenhum
> minuto a mais de estudo. Nenhum curso compete com isso.

---

## 58.8 Armadilhas específicas do brasileiro em time internacional

| Armadilha | Por que acontece | Correção |
|---|---|---|
| imperativo em review | é neutro em português | pergunta ou sugestão ([55](55-pragmatica-e-variacao.md) §55.3) |
| não pedir esclarecimento | vergonha de admitir que não entendeu | *"When you say X, do you mean...?"* — isso é lido como **cuidado**, não como fraqueza |
| dizer "yes" sem entender | evitar constrangimento | custa muito mais caro depois |
| não dar estimativa | medo de errar | dê faixa: *"Roughly two to three days, but let me confirm."* |
| não discordar | hierarquia | discordância técnica fundamentada é **esperada** e valorizada |
| e-mail formal demais | transferência da formalidade escrita brasileira | registro **consultivo** ([30](30-gramatica-avancada.md) §30.12) |
| sumir quando trava | orgulho | *"I'm blocked on X, could use a hand"* é o comportamento esperado |
| não atualizar o status | cultura presencial | em time assíncrono, **quem não escreve não existe** |

---

## 58.9 Os cinco porquês: por que o inglês técnico é tão padronizado?

1. Porque o custo de ambiguidade em documentação técnica é alto e mensurável (bug, incidente,
   incompatibilidade).
2. Por que a padronização reduz esse custo? Porque termos com significado fixo (`MUST`,
   `deprecated`, `breaking change`) eliminam interpretação.
3. Por que existe uma RFC só para isso (a 2119, de 1997)? Porque a IETF percebeu que "should" e
   "must" estavam sendo lidos de formas diferentes por implementadores em países diferentes — e
   isso quebrava a interoperabilidade da internet.
4. Por que isso vazou para fora das RFCs? Porque a cultura de engenharia de software herdou as
   convenções da engenharia de redes, que foi onde a colaboração global assíncrona apareceu
   primeiro.
5. **Parada — decisão histórica documentada.** A RFC 2119 é de março de 1997, autoria de Scott
   Bradner. É um caso raro e bonito de convenção linguística com data, autor e motivo registrados.

---

## Autoteste

1. Por que o inglês técnico é mais fácil do que o inglês geral para um profissional de tecnologia?
2. O que significa *"I don't have bandwidth this week"*?
3. Diferencie `MUST`, `SHOULD` e `MAY` numa especificação. Por que isso importa?
4. O que quer dizer `deprecated`? E `breaking change`?
5. Escreva uma mensagem de commit correta para uma correção de bug. Por que o imperativo aqui é a norma?
6. Reescreva sem soar ríspido: *"Remove this function."*
7. Quais são os três movimentos de um standup?
8. Quais duas seções separam um design doc profissional de um amador?
9. Por que pensar em voz alta é esperado numa entrevista técnica?
10. Qual é a mudança de maior retorno que um profissional de tecnologia brasileiro pode fazer hoje?

**Próximo:** [60-teoria-avancada.md](60-teoria-avancada.md).
