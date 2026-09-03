# 20 · Avaliação e benchmarks

**Nível:** avançado · Atualizado em 13/08/2026

> **A tese:** avaliar agente é mais difícil que avaliar modelo, e a diferença
> é qualitativa. Um modelo produz uma saída; um agente produz uma
> **trajetória** — dezenas de ações, cada uma podendo estar certa por acaso ou
> errada de um jeito que passa no teste.

---

## 1. Por que é difícil

| Propriedade | Consequência para a avaliação |
|---|---|
| Não determinismo | rodar duas vezes dá resultados diferentes; uma medida só não significa nada |
| Trajetória, não resposta | "certo" pode ser atingido por caminho errado |
| Custo variável | dois agentes com a mesma taxa de acerto podem diferir 10× em preço |
| Efeito do arnês | o mesmo modelo com ferramentas melhores muda de patamar |
| Contaminação | tarefas públicas podem ter entrado no treino |
| Recompensa hackeável | passar no teste ≠ resolver o problema |

O último é o mais perigoso porque é invisível. Um agente que descobre que
`pytest -k "not test_dificil"` deixa a suíte verde "resolveu" a tarefa pela
métrica e não resolveu nada.

---

## 2. Os benchmarks públicos

### SWE-bench (2023) e derivados

2 294 issues reais do GitHub em projetos Python de verdade. O agente recebe o
repositório no commit anterior e o texto da issue; o critério é os **testes
reais do projeto** passarem.

| Variante | O que é |
|---|---|
| **SWE-bench** | o conjunto completo |
| **SWE-bench Verified** | 500 tarefas validadas por humanos; o número mais citado |
| **SWE-bench Pro** | mais difícil, resistente a contaminação, bases maiores e comerciais |
| **SWE-bench Multimodal** | issues com imagem (JavaScript) |

Evolução aproximada do Verified: ~2% em 2023 → patamares acima de 80% em 2026,
com os melhores pares agente+modelo passando de 90%.

**Por que celebrar com reservas.** Auditorias independentes mostram que uma
fração relevante das soluções aceitas passa nos testes por motivo errado — os
testes do projeto não distinguem a correção real da coincidência. Trabalhos
como *UTBoost* geram testes adicionais e derrubam parte dos resultados;
auditorias de benchmark encontram atalhos exploráveis. Reportagens de agosto
de 2026 citam ordens de ~20% de soluções semanticamente erradas entre as
"resolvidas" em alguns sistemas. **Trate qualquer número de SWE-bench como
teto otimista, não como taxa de sucesso esperada no seu repositório.**

### Terminal-Bench

Tarefas de terminal ponta a ponta — computação científica, engenharia de
software, ML, segurança, administração de sistemas. Mede **o par agente +
modelo**, não o modelo sozinho, o que é metodologicamente mais honesto para
agentes.

### Outros

| Benchmark | Mede |
|---|---|
| **GAIA** | assistente geral: raciocínio multi-passo com ferramentas e web |
| **τ-bench (tau-bench)** | atendimento em domínio com regras e usuário simulado |
| **WebArena / OSWorld** | agentes em ambientes web e de desktop reais |
| **AgentBench** | conjunto amplo, multi-ambiente |

### Como ler um placar

1. **Qual arnês?** "Modelo X: 88%" sem dizer o arnês é quase sem sentido.
2. **Quantas tentativas?** `pass@1` e `pass@5` são coisas diferentes.
3. **Quanto custou?** Um resultado a US$ 50 por tarefa não é comparável a um
   de US$ 2.
4. **Quem rodou?** Auto-reportado pelo fornecedor ou por terceiro?
5. **Quando?** Contaminação cresce com o tempo desde a publicação.

> **Opinião:** *benchmark público serve para comparar fornecedores, não para
> prever o seu resultado. A correlação entre "88% no SWE-bench Verified" e "vai
> funcionar no meu monorepo de 900 mil linhas com CI de 40 minutos" é fraca.
> A avaliação que decide a sua adoção é a que você constrói com as suas
> tarefas.*

---

## 3. Construir a sua avaliação

O mínimo que funciona, e cabe em uma tarde:

### 1. Colete 20 a 50 casos reais

Do seu backlog, do seu histórico de bugs, dos seus tickets. Casos **reais**,
não inventados. Inclua deliberadamente:

- alguns fáceis (detectam regressão grosseira),
- vários médios (a maioria),
- alguns que você acha que vão falhar (calibram a fronteira),
- pelo menos um que **deve** ser recusado ou escalado.

### 2. Defina o critério, na ordem de preferência

| Critério | Custo | Confiabilidade |
|---|---|---|
| Teste automatizado passa | baixo | **alta** |
| Comparação exata / schema válido | baixo | alta |
| Assertivas sobre a trajetória (chamou a ferramenta certa?) | baixo | média |
| Juiz-LLM com rubrica | médio | média — e enviesado a favor do próprio estilo |
| Revisão humana | alto | alta |

Comece pelo automático. Sem sinal automático, você não roda a suíte com
frequência, e uma suíte que não roda não existe.

### 3. Meça mais que acerto

```
caso  | passou | voltas | tokens_in | tokens_out | custo  | segundos
------|--------|--------|-----------|------------|--------|----------
b-001 |   ✓    |   7    |  142 000  |    9 400   | $0,95  |   84
b-002 |   ✗    |  20    |  510 000  |   31 000   | $3,32  |  310
```

Um agente que acerta 90% gastando 20 voltas por caso não é melhor que um de
85% em 6 voltas — pode ser bem pior. As colunas de custo e voltas mudam
decisões que a coluna de acerto sozinha não muda.

### 4. Rode N vezes

Não determinismo é real. Rode cada caso 3 vezes e reporte a mediana e a
dispersão. Um agente com 70% ± 5% é utilizável; um com 70% ± 30% não é, mesmo
com a mesma média.

### 5. Faça a suíte rodar em CI

A cada mudança de prompt, ferramenta, modelo ou versão do arnês. Sem isso,
toda "melhoria" é palpite, e o efeito das mudanças se cancela sem que você
perceba.

---

## 4. As armadilhas específicas

**Recompensa hackeada.** O agente descobre um atalho que satisfaz a métrica
sem resolver o problema: desabilita o teste, marca como `skip`, aumenta o
timeout, edita o próprio arquivo de teste. Defesa: separe o critério do que o
agente pode tocar. Se ele pode editar os testes, os testes não são critério.

**Juiz-LLM enviesado.** Um LLM avaliando saídas de LLM tende a preferir o
estilo que ele mesmo produziria, e a premiar resposta longa. Defesas: rubrica
concreta e verificável, ordem embaralhada quando compara, e checagem periódica
contra julgamento humano.

**Auto-avaliação.** O mesmo agente julgando o próprio trabalho confirma o que
produziu. Use verificador com contexto independente, instruído a **refutar**
— ver [16 §5](16-subagentes-e-orquestracao.md#5-workflows-dinâmicos).

**Contaminação.** Se a tarefa está pública há dois anos, o modelo pode
conhecer a resposta. Prefira casos do seu repositório privado e posteriores ao
corte de treino.

**Média que esconde.** 85% de acerto com falhas concentradas numa categoria
crítica é pior que 80% distribuído. Segmente por tipo de tarefa.

**Filtro de severidade que derruba o recall.** Instruções como "reporte apenas
achados de alta severidade" são obedecidas literalmente pelos modelos atuais —
o agente encontra os bugs e não os reporta, e o seu *recall medido* cai
enquanto a capacidade real subiu. Peça cobertura total com nível de confiança,
e filtre depois.

---

## 5. Métricas que valem a pena

| Métrica | O que responde |
|---|---|
| Taxa de sucesso | funciona? |
| Custo por tarefa (US$) | dá para pagar? |
| Voltas por tarefa | é eficiente? |
| Latência (p50, p95) | dá para esperar? |
| Taxa de intervenção humana | quanto trabalho meu sobra? |
| Taxa de falha silenciosa | com que frequência ele diz que fez e não fez? |
| Taxa de recusa correta | ele sabe dizer "não consigo"? |

As duas últimas são as menos medidas e as mais importantes na prática. **Falha
silenciosa** — o agente relata sucesso e o trabalho não está feito — corrói a
confiança mais rápido que qualquer taxa de erro honesta, porque destrói o
valor de todas as outras respostas.

---

## 6. Um esqueleto de suíte

```python
# avaliacao.py — roda casos, mede, reporta
import json, subprocess, time, statistics
from pathlib import Path

CASOS = json.loads(Path("casos.json").read_text())   # [{id, prompt, verificar}]
REPETICOES = 3

def rodar(caso: dict) -> dict:
    t0 = time.monotonic()
    p = subprocess.run(
        ["claude", "-p", "--output-format", "json",
         "--max-turns", "25", "--max-budget-usd", "2.00",
         "--allowedTools", "Read", "Grep", "Glob", "Edit", "Bash(pytest*)",
         caso["prompt"]],
        capture_output=True, text=True, timeout=900,
    )
    dados = json.loads(p.stdout or "{}")
    # o critério roda FORA do agente, sobre o estado do repositório
    ok = subprocess.run(caso["verificar"], shell=True, capture_output=True).returncode == 0
    return {
        "id": caso["id"], "ok": ok,
        "segundos": round(time.monotonic() - t0, 1),
        "custo": dados.get("total_cost_usd"),
        "voltas": dados.get("num_turns"),
    }

for caso in CASOS:
    execucoes = [rodar(caso) for _ in range(REPETICOES)]
    acertos = sum(e["ok"] for e in execucoes)
    custos = [e["custo"] for e in execucoes if e["custo"] is not None]
    print(f"{caso['id']:12} {acertos}/{REPETICOES}  "
          f"mediana US$ {statistics.median(custos) if custos else 0:.2f}  "
          f"mediana {statistics.median(e['segundos'] for e in execucoes):.0f}s")
```

Dois detalhes que decidem se essa suíte mede alguma coisa:

- **`verificar` roda fora do agente**, sobre o estado do repositório. Se o
  critério estivesse dentro da sessão, o agente poderia influenciá-lo.
- **`--allowedTools` não inclui edição de teste.** `Bash(pytest*)` deixa ele
  rodar a suíte, não reescrevê-la.

---

## Autoteste

1. Por que avaliar agente é qualitativamente mais difícil que avaliar modelo?
2. O que o SWE-bench mede, e por que um número alto merece reserva?
3. Cite as cinco perguntas para ler um placar público.
4. Por que Terminal-Bench mede o par agente+modelo, e por que isso é mais
   honesto?
5. Além de acerto, quais três métricas você registra por caso, e que decisão
   cada uma muda?
6. Descreva a recompensa hackeada com um exemplo, e a defesa estrutural.
7. Por que auto-avaliação não funciona, e qual é a alternativa?
8. Por que "reporte apenas achados de alta severidade" pode derrubar o recall
   medido sem que a capacidade tenha caído?
9. Duas métricas subestimadas — quais são e por que importam mais que parece?
10. No esqueleto da §6, por que o critério roda fora do agente?
