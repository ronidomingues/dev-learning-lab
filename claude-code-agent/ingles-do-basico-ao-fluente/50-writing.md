# 50 · Escrita — o gênero de maior risco e maior retorno

`Nível: intermediário → avançado` · `Última atualização: 31/08/2026`

> Escrever é a habilidade que mais rende profissionalmente: um e-mail circula, um documento fica,
> um comentário de code review é lido por quem você nunca vai conhecer. E é também a única em que
> você tem **tempo** — o que significa que não há desculpa para o erro que você sabe corrigir.

---

## 50.1 Por que escrever também melhora a fala

Escrever é produção **sem pressão de tempo**. Isso permite:

- buscar a palavra que não veio (e assim ativá-la para a próxima vez);
- notar o buraco no seu conhecimento — o "gap noticing" de Swain
  ([10-fundamentos](10-fundamentos.md) §10.6);
- receber correção precisa, o que a fala raramente permite.

> **Regra prática:** o assunto que você escreve numa semana, você fala na seguinte.
> Se um tema trava você em reunião, escreva cinco frases sobre ele à noite.

---

## 50.2 O princípio que governa toda a escrita inglesa

O inglês escrito é organizado de forma **dedutiva e explícita**: a conclusão vem primeiro, o
suporte depois.

```
INGLÊS                              PORTUGUÊS ACADÊMICO/FORMAL (tendência)
┌─ afirmação principal              ┌─ contexto
│  ├─ evidência 1                   │  ├─ desenvolvimento
│  ├─ evidência 2                   │  ├─ mais desenvolvimento
│  └─ implicação                    └─ conclusão
```

Isso não é superioridade cultural — é convenção de gênero, e é forte. Um texto brasileiro
"bem escrito", traduzido literalmente, é lido em inglês como **enrolação que não chega ao ponto**.
E o inverso: um texto inglês bem escrito soa, para o leitor brasileiro, seco e apressado.

**Regra operacional:** a primeira frase do parágrafo diz do que ele trata (*topic sentence*).
A primeira frase do documento diz a que ele veio.

---

## 50.3 As sete regras que consertam 80% do texto de brasileiro

### 1 · Chegue ao ponto no primeiro parágrafo
❌ *"I hope this message finds you well. As you may know, our team has been working on several
initiatives over the past quarter, and one of them relates to the database, which..."*
✅ *"I'm writing about the database migration. We need a decision by Friday."*

### 2 · Frases curtas
Alvo: 15–20 palavras em média. Se passar de 30, quebre. O português tolera períodos longos; o
inglês profissional não.

### 3 · Voz ativa por padrão
❌ *"It was decided by the team that the feature would be postponed."* (13 palavras, agente
escondido)
✅ *"The team postponed the feature."* (5 palavras)
Passiva **só** quando o agente é irrelevante ou quando a estrutura da informação pede
([30-gramatica-avancada](30-gramatica-avancada.md) §30.3).

### 4 · Verbo em vez de nominalização
❌ *"We performed an analysis of the data."* ✅ *"We analyzed the data."*
❌ *"the implementation of the validation"* ✅ *"validating"*

### 5 · Corte os intensificadores vazios
`very, really, quite, actually, basically, definitely, in order to, at this point in time`.
❌ *"This is a very important issue that we should definitely address."*
✅ *"We should address this."*

### 6 · Uma ideia por parágrafo
Parágrafo de trabalho: 3–5 frases. Parágrafo de meia página não é lido.

### 7 · Listas para opções, tabelas para comparações
Se você está enumerando alternativas em texto corrido, a decisão fica escondida. Numere.

---

## 50.4 Registro — escolher entre germânico e latino

A herança de 1066 ([11-historia](11-historia.md) §11.4) é a sua régua de formalidade:

| Informal (germânico, curto) | Formal (latino, longo) |
|---|---|
| get | obtain, receive |
| buy | purchase |
| ask | request, inquire |
| start | commence, initiate |
| end | conclude, terminate |
| show | demonstrate, indicate |
| help | assist |
| need | require |
| find out | determine, ascertain |
| put off | postpone |
| set up | establish, configure |
| deal with | address, handle |

**Como usar:**
- **E-mail de trabalho, documentação, chat:** predominantemente **germânico**. Direto e claro.
- **Proposta comercial, contrato, artigo acadêmico:** mais **latino**.
- **Nunca misture no mesmo parágrafo** sem motivo — soa desconjuntado.

⚠️ **Erro comum:** o brasileiro acha que palavra latina = inglês bom, porque ela se parece com o
português culto. O resultado é um e-mail que soa como circular de repartição. Em comunicação de
time, **germânico vence**.

---

## 50.5 Coesão — por que seu texto "parece solto"

Quase nunca é falta de conectivo. É falta de **encadeamento temático**
([30-gramatica-avancada](30-gramatica-avancada.md) §30.3):

```
Frase 1:  [conhecido A] .................. [novo B]
Frase 2:  [conhecido B] .................. [novo C]
Frase 3:  [conhecido C] .................. [novo D]
```

**Ruim (cada frase começa do zero):**
> *We tested the migration. Six hours is the duration. A maintenance window is necessary. The
> support team has fewer people on Saturdays.*

**Bom (cada frase parte da anterior):**
> *We tested the migration on staging. **The test** took six hours, which means **we'd need a
> maintenance window**. **That window** would have to fall on a weekend — and **weekends** are
> when the support team is thinnest.*

Ferramentas de coesão: repetir a palavra-chave (⭐ e **repetir é bom** em inglês técnico —
sinônimo elegante confunde), pronomes, `this`/`that` + substantivo (*this approach*, *that
decision*), e só então conectivos.

---

## 50.6 Os gêneros que você vai escrever

### E-mail profissional
Estrutura completa e comentada em [06-exemplos](06-exemplos.md) §Exemplo 8.
Esqueleto: **assunto acionável → contexto em uma linha → o ponto → opções em lista →
recomendação → pedido com prazo → fecho**.

### Mensagem de chat (Slack/Teams)
| Regra | Por quê |
|---|---|
| **uma mensagem, não sete** | cada envio gera uma notificação |
| pergunta + contexto juntos | ❌ *"Hi"* e esperar resposta é hostil ao tempo do outro |
| thread para desdobramentos | mantém o canal legível |
| `cc @fulano` para envolver alguém | — |

❌ *"Hey"* … [3 min] … *"you there?"* … [2 min] … *"quick question"*
✅ *"Hey — quick question: do we still need the staging DB after Friday? Asking because I'd like to shut it down."*

### Documento / relatório
```
1. Sumário executivo   (3 linhas: o que é, o que se decidiu, o que se pede)
2. Contexto            (por que este documento existe)
3. Opções              (em tabela)
4. Recomendação        (com o porquê)
5. Próximos passos     (quem faz o quê, até quando)
6. Anexos
```
⭐ O **sumário executivo primeiro** não é opcional em ambiente internacional. Muita gente lê só ele.

### Currículo (AmE: *resume*; BrE: *CV*)
- **Verbos de ação no passado, com número:** *"Reduced build time by 40% by parallelizing tests."*
- ❌ *"Was responsible for the tests"* — passivo, vago, sem resultado.
- Uma página (EUA) ou duas (Europa). Sem foto, sem idade, sem estado civil (EUA/Reino Unido —
  incluir pode até criar problema legal para quem recruta).

### Escrita acadêmica
Recursos centrais: **hedging** ([30](30-gramatica-avancada.md) §30.8), verbos de relato com
avaliação ([30](30-gramatica-avancada.md) §30.7), voz passiva quando o agente é irrelevante,
nominalização moderada, e citação rigorosa.

---

## 50.7 Revisão — o processo, em três passadas

Não tente corrigir tudo de uma vez. Sua atenção é serial.

| Passada | Foco | Pergunta |
|---|---|---|
| **1 · Estrutura** | organização | o ponto está no começo? A ordem faz sentido? Sobra parágrafo? |
| **2 · Frase** | clareza | alguma frase passa de 30 palavras? Voz passiva sem motivo? Nominalização? |
| **3 · Superfície** | gramática, grafia | artigos, `-s` de 3ª pessoa, preposições, contável/incontável |

⭐ **Leia em voz alta na passada 3.** Você ouve o que não vê — em qualquer língua.

**Ferramentas:**
- **LanguageTool** (grátis, e pode rodar local — ver [03-instalacao](03-instalacao.md) §03.7) —
  gramática e estilo
- **Hemingway Editor** (web, grátis) — sinaliza frase longa e voz passiva
- **SkELL / Ozdic** — checar colocação
- **Um LLM** — útil para "isto soa natural?"; ⚠️ ver as ressalvas em
  [65-estado-da-arte](65-estado-da-arte.md) §65.3

---

## 50.8 Checklist de e-mail profissional

Antes de enviar:

- [ ] O assunto diz **o que é e o que preciso**.
- [ ] O ponto principal está nas **três primeiras linhas**.
- [ ] Há um **pedido específico com prazo**.
- [ ] As opções estão em lista, não em texto corrido.
- [ ] Eu dei uma **recomendação**, não só alternativas.
- [ ] Nenhuma frase passa de 30 palavras.
- [ ] Cortei `very`, `really`, `basically`, `in order to`.
- [ ] Verifiquei `its/it's`, `your/you're`, `their/there/they're`.
- [ ] O tom está **consultivo**, não formal demais nem seco demais.
- [ ] Se o e-mail é uma reclamação, eu esperei 20 minutos antes de enviar.

---

## 50.9 Rotina de escrita

| Frequência | Exercício | Tempo |
|---|---|---|
| diária | 5 frases sobre o dia, ou 1 parágrafo sobre o que leu | 8 min |
| semanal | reescrever um e-mail real seu, aplicando §50.3 | 15 min |
| semanal | um comentário/post em comunidade em inglês (⭐ retorno real de gente real) | 10 min |
| mensal | um texto de 500 palavras sobre o seu campo | 45 min |

**Correção:** LanguageTool para superfície; um LLM ou uma pessoa para naturalidade. E guarde os
textos — reler o que você escreveu há seis meses é a medida mais honesta de progresso em escrita.

---

## 50.10 Os cinco porquês: por que o inglês escrito é tão direto?

1. Porque a convenção do gênero profissional anglófono põe a conclusão primeiro.
2. Por que essa convenção? Porque ela otimiza para o **leitor que vai parar de ler no meio** —
   o modelo da pirâmide invertida.
3. De onde vem esse modelo? Do jornalismo americano do século XIX, que precisava que a notícia
   sobrevivesse a cortes de espaço e a falhas na transmissão telegráfica.
4. Por que se espalhou para o e-mail e o relatório? Porque a cultura corporativa americana
   adotou a mesma economia de atenção, e ela se globalizou junto com as multinacionais.
5. **Parada — decisão histórica documentada + economia de atenção.** Não é uma propriedade da
   língua inglesa: é uma convenção de gênero com origem datável, que hoje é norma internacional.
   Escrever "à brasileira" em inglês não é errado gramaticalmente — é **fora da convenção**, e
   custa a leitura.

---

## Autoteste

1. Por que escrever melhora a fala?
2. Descreva a diferença de organização entre um texto brasileiro e um inglês.
3. Cite as sete regras do §50.3 e aplique três a um e-mail seu.
4. Reescreva sem nominalização: *"We performed an evaluation of the performance."*
5. Quando usar vocabulário germânico e quando usar latino?
6. Seu texto "parece solto". Qual é a causa mais provável e como se conserta?
7. Qual a estrutura de um relatório profissional e qual seção muita gente lê sozinha?
8. Por que ❌ *"Was responsible for the tests"* num currículo?
9. Descreva as três passadas de revisão e o que se olha em cada uma.
10. De onde vem a convenção de "conclusão primeiro"?

**Próximo:** [55-pragmatica-e-variacao.md](55-pragmatica-e-variacao.md).
