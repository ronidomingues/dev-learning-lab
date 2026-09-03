# 20 · Avaliação — o núcleo da profissão

**Nível:** intermediário → avançado · **Escrito em:** 19/08/2026

Se você ler um arquivo só deste curso, leia este. Tudo o mais é técnica; isto
é o que transforma técnica em engenharia — e é o que o mercado paga.

> **Tese deste arquivo:** o ativo de valor de um sistema com LLM **não é o
> prompt**. É o conjunto de avaliação. Prompt se reescreve numa tarde; um
> conjunto de 500 casos rotulados por quem entende do negócio leva meses e não
> se copia de ninguém.

---

## 20.1 · Por que sem avaliação não existe engenharia

Sem conjunto de avaliação você não consegue responder a nenhuma destas
perguntas, todas rotineiras:

- Este prompt novo é melhor que o antigo? **Quanto** melhor?
- O modelo mais barato serve para este caso?
- A atualização do modelo pelo fornecedor quebrou alguma coisa?
- Vale a pena manter estes 8 exemplos que custam 500 tokens por chamada?
- Estamos melhorando ou só mudando?

E o pior sintoma: **sem medição, todo mundo na equipe tem uma opinião, e vence
a de quem fala mais alto.** Com medição, discute-se o conjunto de teste — que é
uma discussão produtiva.

---

## 20.2 · Construir o conjunto rotulado

### Quantos casos?

| Tamanho | Serve para | Não serve para |
|---|---|---|
| 10–20 | apanhar erro grosseiro, primeira iteração | comparar prompts parecidos |
| 50–100 | comparação com diferença grande (>10 pp) | ajuste fino |
| 200–500 | trabalho sério; detecta diferenças de ~5 pp | garantia estatística de 1 pp |
| 1.000+ | sistema maduro, fatiado por segmento | — |

**Comece com 20 hoje** em vez de planejar 500 para o mês que vem. Vinte casos
mudam sua vida; zero casos, não.

### De onde vêm os casos

Em ordem de valor:

1. **Produção real** — a melhor fonte, de longe. Amostre aleatoriamente, não
   escolha "os interessantes".
2. **Erros conhecidos** — todo caso que já quebrou vira caso de teste
   permanente. É o teste de regressão da área.
3. **Casos de fronteira escritos à mão** — o ambíguo, o vazio, o gigante, o
   em outro idioma, o malicioso.
4. **Sintéticos gerados por modelo** — úteis para volume; **enviesados**, porque
   têm a cara do que o modelo gera. Nunca use como conjunto principal.

### Rotular

- **Escreva o critério antes de rotular**, ou você vai rotular por intuição e
  mudar de critério na metade.
- **Duas pessoas rotulam os primeiros 30** e comparam. **A taxa de discordância
  entre humanos é o teto do seu sistema.** Se dois especialistas concordam em
  80% dos casos, nenhum modelo vai passar disso de forma significativa — e
  perseguir 95% é perseguir ruído.
- **Registre o motivo** dos casos difíceis. Esse texto vira regra do prompt ou
  exemplo, depois.
- **Separe conjunto de desenvolvimento e conjunto de validação.** Você vai
  olhar o de desenvolvimento centenas de vezes e, inevitavelmente, ajustar o
  prompt a ele. O de validação você toca raramente. Sem essa separação, você
  mede o quanto decorou.

---

## 20.3 · Que métrica usar

| Tipo | Exemplo | Custo | Confiabilidade |
|---|---|---|---|
| **Determinística** | JSON válido? categoria bate com o rótulo? termo do glossário presente? | ~zero | máxima |
| **Baseada em propriedade** | todo número da saída existe na entrada? o resumo cabe em 200 caracteres? | ~zero | alta |
| **Modelo como juiz** | nota 0–2 de correção factual segundo rubrica | média | **média, e só depois de calibrada** |
| **Humana** | especialista lê e nota | altíssimo | é a referência |

**Estratégia que funciona:** determinístico para tudo que puder; juiz para o
resto; humano para calibrar o juiz e para a amostra semanal.

**Sequência de perguntas para achar a métrica determinística escondida** —
quase toda tarefa "subjetiva" tem uma:

1. Existe algo que **nunca** pode acontecer? (número inventado, categoria
   inexistente, promessa proibida) → verificação binária.
2. Existe algo que **sempre** tem de acontecer? (citar a fonte, responder na
   língua da pergunta) → verificação binária.
3. Existe formato, tamanho ou vocabulário obrigatório? → verificação.
4. O que sobrar é julgamento — e só isso vai para o juiz.

---

## 20.4 · Estatística mínima (a parte que evita vergonha)

Você rodou 20 casos: o prompt A acertou 15 (75%), o B acertou 17 (85%). O B é
melhor?

**Provavelmente você não sabe.** Com 20 casos, o intervalo de confiança é
largo demais para separar os dois.

```python
# intervalo.py — intervalo de confiança de Wilson, 95%, sem dependências
from math import sqrt

def wilson(acertos: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de confiança para uma proporção. Melhor que o normal
    para amostra pequena e para proporções perto de 0 ou 1."""
    if total == 0:
        return (0.0, 1.0)
    p = acertos / total
    denom = 1 + z**2 / total
    centro = (p + z**2 / (2 * total)) / denom
    margem = z * sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denom
    return (max(0.0, centro - margem), min(1.0, centro + margem))

for acertos, total in [(15, 20), (17, 20), (150, 200), (170, 200),
                       (850, 1000), (870, 1000)]:
    lo, hi = wilson(acertos, total)
    print(f"{acertos}/{total} = {acertos/total:6.1%}  IC95%: [{lo:.1%}, {hi:.1%}]")
```

```bash
python3 intervalo.py
```

Saída real (19/08/2026):

```
15/20 =  75.0%  IC95%: [53.1%, 88.8%]
17/20 =  85.0%  IC95%: [64.0%, 94.8%]
150/200 =  75.0%  IC95%: [68.6%, 80.5%]
170/200 =  85.0%  IC95%: [79.4%, 89.3%]
850/1000 =  85.0%  IC95%: [82.7%, 87.1%]
870/1000 =  87.0%  IC95%: [84.8%, 88.9%]
```

Leia com atenção:

- **20 casos:** os intervalos [53%, 89%] e [64%, 95%] se sobrepõem quase
  inteiramente. **A diferença de 10 pontos não é conclusiva.**
- **200 casos:** [69%, 81%] contra [79%, 89%] — sobreposição pequena; agora dá
  para falar em melhora.
- **1.000 casos:** dá para discutir 2 pontos percentuais.

> **A regra que evita o vexame:** antes de anunciar melhora, verifique se os
> intervalos se sobrepõem. Se sobrepõem muito, o que você tem é ruído com
> aparência de resultado. E há um jeito ainda melhor para comparar dois prompts
> **nos mesmos casos**: olhe só os casos em que eles **divergem** (teste de
> McNemar) — é bem mais sensível que comparar as duas taxas globais.

**Ganho de graça:** avalie os dois prompts **exatamente nos mesmos casos**, na
mesma ordem. Comparação pareada elimina a variação do conjunto e é muito mais
sensível que comparar médias de amostras diferentes.

---

## 20.5 · Modelo como juiz, feito direito

Ver [06, exemplo 9](06-exemplos.md) para o prompt e os vieses. Aqui, o
processo:

1. **Escreva a rubrica** com âncoras, escala curta (0–2), uma dimensão por vez.
2. **Rotule 50 casos à mão** com essa rubrica.
3. **Rode o juiz nesses 50** e meça a concordância com o humano.
4. **Se a concordância for baixa**, o problema é quase sempre a rubrica, não o
   modelo. Reescreva as âncoras e repita.
5. **Só então** solte o juiz nos 500.
6. **Reamostre 20 casos por semana** para conferir que ele não derivou.

Reporte sempre a concordância junto com a nota. "Juiz com 87% de concordância
com humano em 50 casos" é um resultado. "O juiz deu 4,3" não é nada.

**Nunca use o mesmo modelo como gerador e juiz sem checar autofavorecimento.**
Se puder, use outra família de modelo para julgar.

---

## 20.6 · Colocar no CI

O portão que impede regressão silenciosa:

```bash
python3 avaliar.py --prompt prompts/v3_fewshot.md --limite 0.90
```

Sai com código 1 se cair abaixo do limite. Em GitHub Actions:

```yaml
# .github/workflows/eval.yml
name: avaliacao-de-prompt
on: [pull_request]
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.13"}
      - run: pip install -r 07-projeto-modelo/requirements.txt
      - name: rodar avaliação
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          cd 07-projeto-modelo
          python3 avaliar.py --provedor anthropic \
                             --prompt prompts/v3_fewshot.md --limite 0.90
```

Três detalhes que decidem se isso funciona ou vira alarme ignorado:

- **Limite abaixo do valor atual**, com folga para o ruído estatístico. Portão
  no valor exato quebra a cada execução por variabilidade e é desligado em duas
  semanas.
- **Custo por execução visível.** Se cada PR gasta US$ 3 em API, alguém vai
  reclamar antes de você perceber.
- **Conjunto pequeno no PR, conjunto completo à noite.** É o mesmo padrão de
  testes unitários rápidos e suíte de integração noturna.

---

## 20.7 · O que medir em produção (avaliação online)

O conjunto de teste é o passado. Produção é o presente.

| Sinal | O que revela |
|---|---|
| taxa de saída inválida | prompt ou modelo degradando |
| taxa de escalonamento humano | dificuldade real do tráfego |
| latência p50/p95 | experiência do usuário; p95 é o que reclama |
| custo por requisição e por resolução | economia do sistema |
| retrabalho do usuário (reformulou a pergunta?) | insatisfação silenciosa |
| divergência entre duas execuções amostradas | instabilidade |
| **deriva da distribuição de entrada** | o tráfego mudou e seu conjunto envelheceu |

A última é a mais importante e a menos monitorada: **o mundo muda**. Um
formulário novo no site, uma promoção, um feriado, e a distribuição dos
chamados muda. Seu conjunto de avaliação, congelado, deixa de representar a
produção — e você continua vendo 96% no painel enquanto o cliente reclama.

**Prática recomendada:** amostre 50 casos reais por mês, rotule, e acrescente
ao conjunto. É uma hora de trabalho mensal que mantém tudo honesto.

---

## 20.8 · Armadilhas da avaliação

| Armadilha | Como se manifesta | Correção |
|---|---|---|
| **Superajuste ao conjunto** | 98% no teste, ruim em produção | conjunto de validação separado, tocado raramente |
| **Vazamento** | casos do teste viraram exemplos no prompt | proibir; conferir |
| **Conjunto não representativo** | só casos fáceis, ou só os que alguém achou interessantes | amostra aleatória de produção |
| **Métrica que não é o objetivo** | 95% de acerto de categoria, mas o cliente reclama do tom | medir o que o negócio quer |
| **Juiz não calibrado** | números lindos, sem relação com a realidade | calibrar contra humano |
| **Comparar em conjuntos diferentes** | "o prompt novo deu 90%" (em outros casos) | comparação pareada |
| **Ignorar variabilidade** | rodou uma vez, comemorou | repetir; intervalo de confiança |
| **Só a média** | 92% no geral, 40% no segmento que mais paga | fatiar por segmento **sempre** |

A penúltima e a última são as que mais custam dinheiro na prática.

---

## 20.9 · Ferramentas

| Ferramenta | O que faz | Observação (19/08/2026) |
|---|---|---|
| **Seu próprio script** | 100 linhas de Python | ✅ comece aqui; é o que o [projeto-modelo](07-projeto-modelo/avaliar.py) faz |
| **promptfoo** | avaliação declarativa em YAML, comparação lado a lado, red teaming | aberto (MIT); **adquirido pela OpenAI em 09/03/2026** |
| **DeepEval, Ragas** | métricas prontas, inclusive de RAG | úteis; entenda a métrica antes de usar |
| **Plataformas de observabilidade** (LangSmith, Braintrust, Langfuse, Phoenix) | traços, conjuntos, avaliação online | valem quando há equipe e volume |

**Opinião profissional:** comece com um script seu. Ferramenta traz vocabulário
e painéis, e esconde o que está sendo calculado. Depois que você já escreveu o
seu, a ferramenta vira conveniência em vez de caixa-preta.

---

## Autoteste

1. Por que o conjunto de avaliação vale mais que o prompt?
2. 15/20 contra 17/20: é melhora? Justifique com o número.
3. O que é a taxa de discordância entre humanos e por que ela é o teto do
   sistema?
4. Por que separar conjunto de desenvolvimento e de validação?
5. Descreva os seis passos para colocar um modelo-juiz em uso.
6. Três detalhes que fazem um portão de CI funcionar em vez de ser ignorado.
7. Qual sinal de produção revela que seu conjunto de avaliação envelheceu?
8. Por que olhar só a média é perigoso? Dê um exemplo de negócio.
