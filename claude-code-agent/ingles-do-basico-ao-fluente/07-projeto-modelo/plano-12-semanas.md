# Plano de 12 semanas — do zero ao primeiro A2/B1 funcional

`Nível: iniciante` · `Carga: 40–60 min/dia, 6 dias por semana` · `Total: ~50 h`

> 50 horas não fazem ninguém fluente — e este plano não promete isso. Elas fazem duas coisas
> que valem mais no começo: **instalam o hábito** e **provam para você que funciona**.
> Ao fim das 12 semanas você deve estar em A2 sólido (ou B1, se já sabia algo), com um sistema
> que roda sozinho a partir daí.

---

## A estrutura de todo dia

| Bloco | Tempo | O quê |
|---|---|---|
| **R** · Revisar | 10–15 min | Anki, até zerar |
| **A** · Absorver | 20–30 min | o material da semana |
| **C** · Colher | 5 min | 3–5 frases → `deck/frases-nucleo.tsv` |
| **P** · Produzir | 5–10 min | a tarefa da semana |

Ao fim: `python3 scripts/estudo.py registrar --min <N> --hab <habilidades>`

**Domingo é folga.** Folga programada não quebra sequência; folga não programada quebra o hábito.

---

## Semanas 1–4 · Fundação

| Semana | Absorver | Produzir | Ler do curso |
|---|---|---|---|
| **1** | *Let's Learn English* (VOA), 2 episódios/dia | dizer o diálogo do 04 nos dois papéis | [01](../01-introducao-leigo.md), [04](../04-como-comecar.md) |
| **2** | BBC Learning English, nível *Beginner* | apresentar-se em 60 s, gravando **todo dia** | [05 §05.2](../05-manual-de-uso.md) — o IPA |
| **3** | mesmo material da semana 2, **sem** legenda na 2ª passada | descrever sua rotina em 8 frases | [12](../12-fonetica-e-fonologia.md) §12.1–12.5 |
| **4** | *6 Minute English*, com transcrição | contar seu fim de semana no passado | [25](../25-gramatica-nucleo.md) §25.1–25.6 |

**Marco da semana 4:** você diz 20 frases sobre si mesmo sem consultar nada.
Regrave a apresentação da semana 2 e compare. Guarde as duas.

---

## Semanas 5–8 · Ouvido e volume

| Semana | Absorver | Produzir | Ler do curso |
|---|---|---|---|
| **5** | *6 Minute English* **sem** transcrição na 1ª passada | shadowing, 10 min/dia ([roteiro-shadowing.md](roteiro-shadowing.md)) | [35](../35-listening.md) |
| **6** | Simple English Wikipedia sobre o **seu** assunto | escrever 5 frases/dia sobre o que leu | [20](../20-vocabulario.md) |
| **7** | um canal de YouTube do seu hobby, legenda **em inglês** | narrar seu dia em voz alta, 3 min | [40](../40-speaking.md) |
| **8** | ⭐ **semana da escuta pura**: 40 min/dia só ouvindo, nada de texto | responder em voz alta 5 perguntas sobre o áudio | [35](../35-listening.md) §35.3 |

**Marco da semana 8:** você entende a ideia geral de um *6 Minute English* na primeira vez.
Se não: normal. Volte para material mais fácil por duas semanas e retome. Não force.

---

## Semanas 9–12 · Uso

| Semana | Absorver | Produzir | Ler do curso |
|---|---|---|---|
| **9** | os exemplos 4, 5 e 9 do [06](../06-exemplos.md) | escrever 3 e-mails reais (mesmo que não envie) | [50](../50-writing.md) |
| **10** | um podcast do seu campo, sem material didático | ⭐ **primeira conversa com uma pessoa** — troca de idiomas, professor, colega | [55](../55-pragmatica-e-variacao.md) |
| **11** | série/filme com legenda em inglês, 1 episódio | recontar o episódio em 3 min, gravando | [45](../45-reading.md) |
| **12** | revisão: reassista o material da semana 1 | refazer o EF SET · comparar a gravação com a da semana 2 | [70](../70-pratica.md) |

**Marco da semana 12:**
1. EF SET refeito e comparado com o da semana 0.
2. As duas gravações (semana 2 e semana 12) ouvidas em sequência. **Esta é a prova.**
3. `python3 scripts/estudo.py relatorio` — veja horas, sequência e o que ficou de fora.

---

## Regras que valem as 12 semanas

1. **Nunca zere um dia.** 10 min de Anki conta. Sequência quebrada é o começo do fim.
2. **Se o material dói, é difícil demais.** Troque, sem culpa. Insumo que você não entende não é
   insumo, é ruído.
3. **Colha no máximo 5 frases por dia.** Ver [75-armadilhas](../75-armadilhas.md) §75.2.
4. **Fale em voz alta todo dia.** Sussurrar articulando vale; ler mentalmente não.
5. **Não estude gramática mais de 15% do tempo.** Ela é mapa, não estrada.
6. **Grave-se a cada 4 semanas**, sempre o mesmo texto. É a única forma de perceber progresso.

---

## Se você já não é iniciante

Pule as semanas 1–4 e comece na 5. Substitua todo material didático por **material real do seu
campo** desde o primeiro dia, e desloque o peso para produção: 60% produzir, 40% absorver.
O gargalo de quem "já sabe mas não fala" nunca é insumo — é uso.

---

## Autoteste

1. Quais são os quatro blocos do dia e qual deles não pode faltar no dia ruim?
2. Por que o domingo é folga programada?
3. Qual é o marco da semana 8 e o que fazer se você não atingi-lo?
4. Por que gravar a mesma apresentação nas semanas 2 e 12?
5. Qual o teto de tempo dedicado à gramática, e por quê?
