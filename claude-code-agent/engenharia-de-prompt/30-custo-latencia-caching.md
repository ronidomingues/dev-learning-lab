# 30 · Custo, latência e cache — a engenharia que aparece na fatura

**Nível:** intermediário → avançado · **Escrito em:** 19/08/2026
**Preços consultados em 19/08/2026.** Confira antes de decidir: mudam.

---

## 30.1 · Como se cobra

Cobra-se por **token**, separadamente na entrada e na saída, com a saída
custando tipicamente **5× a entrada**.

Preços de referência da Anthropic (por milhão de tokens, 19/08/2026):

| Modelo | Entrada | Saída |
|---|---|---|
| Claude Opus 5 | US$ 5,00 | US$ 25,00 |
| Claude Sonnet 5 | US$ 3,00 | US$ 15,00 |
| Claude Haiku 4.5 | US$ 1,00 | US$ 5,00 |

Modificadores que mudam tudo:

| Modificador | Efeito |
|---|---|
| **Escrita no cache** | ~1,25× o preço da entrada (você paga um pouco mais para gravar) |
| **Leitura do cache** | ~0,1× o preço da entrada — **90% de desconto** |
| **Lote assíncrono** (*batch*) | ~50% de desconto, entrada e saída |
| Tokens de pensamento | contam como saída |

**A conta que todo iniciante erra:** o histórico da conversa é **reenviado
inteiro** a cada turno. Uma conversa de 20 turnos com 500 tokens por turno não
custa 10 mil tokens — custa a soma acumulada, que é da ordem de 100 mil.

---

## 30.2 · Calculadora

```python
# custo.py — estimativa de custo mensal. Roda com: python3 custo.py
PRECOS = {  # US$ por milhão de tokens, Anthropic, 19/08/2026
    "opus-5":   {"entrada": 5.00, "saida": 25.00},
    "sonnet-5": {"entrada": 3.00, "saida": 15.00},
    "haiku-4.5": {"entrada": 1.00, "saida": 5.00},
}

def custo(modelo, entrada, saida, chamadas, frac_cache=0.0, lote=False):
    """entrada/saida: tokens por chamada. frac_cache: fração da entrada
    que é lida do cache (0,1× do preço). lote: aplica 50% de desconto."""
    p = PRECOS[modelo]
    ent_cache = entrada * frac_cache
    ent_nova = entrada - ent_cache
    total = (ent_nova * p["entrada"] + ent_cache * p["entrada"] * 0.1
             + saida * p["saida"]) * chamadas / 1_000_000
    return total * (0.5 if lote else 1.0)

CHAMADAS = 50_000
cenarios = [
    ("opus-5,   sem cache",           dict(modelo="opus-5", entrada=3700, saida=300, chamadas=CHAMADAS)),
    ("opus-5,   95% em cache",        dict(modelo="opus-5", entrada=3700, saida=300, chamadas=CHAMADAS, frac_cache=0.95)),
    ("opus-5,   cache + lote",        dict(modelo="opus-5", entrada=3700, saida=300, chamadas=CHAMADAS, frac_cache=0.95, lote=True)),
    ("haiku-4.5, sem cache",          dict(modelo="haiku-4.5", entrada=3700, saida=300, chamadas=CHAMADAS)),
    ("haiku-4.5, cache + lote",       dict(modelo="haiku-4.5", entrada=3700, saida=300, chamadas=CHAMADAS, frac_cache=0.95, lote=True)),
]
print(f"{'cenário':<28} {'US$/mês':>10}")
print("-" * 40)
for nome, kw in cenarios:
    print(f"{nome:<28} {custo(**kw):>10.2f}")
```

```bash
python3 custo.py
```

Saída real (19/08/2026):

```
cenário                         US$/mês
----------------------------------------
opus-5,   sem cache             1300.00
opus-5,   95% em cache           509.12
opus-5,   cache + lote            254.56
haiku-4.5, sem cache              260.00
haiku-4.5, cache + lote            50.91
```

Três leituras que valem mais que a tabela:

1. **O cache sozinho corta ~61% neste perfil** (1300 → 509), sem tocar na
   qualidade.
2. Trocar Opus por Haiku corta 80% — **e pode custar acerto**. Só a avaliação
   diz se compensa.
3. Faça a conta da saída: 300 tokens × US$ 25/M × 50.000 = **US$ 375**. Ou
   seja, dos US$ 509 do cenário com cache, **US$ 375 são saída** — a entrada
   virou detalhe. **Encurtar a saída é a alavanca esquecida**: peça o resumo em
   80 caracteres, não em três parágrafos.

---

## 30.3 · Cache de prompt: como funciona de verdade

**Casamento por prefixo, byte a byte.** O sistema procura o maior prefixo já
visto que seja **idêntico** ao início da sua requisição. Um único byte
diferente lá no começo invalida tudo o que vem depois.

Ordem de renderização (esta é a ordem que importa):

```
1. definições de ferramentas
2. instrução de sistema
3. mensagens
```

Regras práticas:

| Regra | Motivo |
|---|---|
| **estável primeiro, volátil depois** | o prefixo estável é o que se reaproveita |
| prefixo mínimo de ~1024 tokens | abaixo disso, não cacheia — silenciosamente |
| poucos pontos de corte (tipicamente até 4) | são marcadores, não regiões |
| lista de ferramentas em ordem determinística | ordenar diferente = prefixo diferente |
| JSON serializado com chaves ordenadas | idem |

### Os invalidadores silenciosos

Isto é o que faz a taxa de acerto de cache cair sem ninguém entender:

| Invalidador | Onde se esconde |
|---|---|
| **carimbo de data/hora no prompt de sistema** | "Hoje é 19/08/2026 14:32" — muda a cada requisição |
| id de sessão ou de requisição no início | log bem-intencionado |
| ferramentas em ordem não determinística | `set` em Python, dicionário sem ordenação |
| JSON de configuração serializado sem `sort_keys` | ordem varia entre execuções |
| few-shot dinâmico | os exemplos mudam por caso — trade-off consciente |
| troca de modelo ou de parâmetro | cache é por configuração |

**Como detectar:** olhe o campo de tokens lidos do cache na resposta
(`usage.cache_read_input_tokens` na API da Anthropic). Se ele é zero em
requisições repetidas, há um invalidador. É diagnóstico de 30 segundos que
quase ninguém faz.

**Se você precisa da data no prompt** — e frequentemente precisa, para datas
relativas ([06, exemplo 7](06-exemplos.md)) — coloque-a **no fim**, junto do
dado volátil, nunca no topo.

---

## 30.4 · Latência

Duas medidas diferentes, e confundi-las leva a otimizar a coisa errada:

| Medida | O que é | Do que depende |
|---|---|---|
| **TTFT** (tempo até o primeiro token) | quanto o usuário espera para ver algo | tamanho da **entrada**, fila do fornecedor, cache |
| **Tempo total** | até a resposta acabar | tamanho da **saída**, principalmente |

Consequências práticas:

- **Streaming não deixa nada mais rápido** — muda a percepção. E muda muito:
  200 ms para o primeiro token com resposta de 8 s parece rápido; 8 s de tela
  branca parece travado.
- **Cortar a saída é a maior alavanca de tempo total.** Cada token de saída é
  gerado em sequência; não há paralelismo.
- **Cache reduz o TTFT** além do custo, porque o prefixo não precisa ser
  reprocessado.
- **Encadeamento multiplica a latência.** Quatro etapas de 2 s são 8 s. Rode em
  paralelo o que for independente.
- **Pensamento estendido aumenta o tempo** — é raciocínio real sendo gerado.
  Ajuste o nível de esforço à tarefa.

---

## 30.5 · Escolher o modelo por dado

Procedimento, e é sempre o mesmo:

1. Comece pelo modelo **mais capaz**. Estabeleça o teto de qualidade.
2. Rode o mesmo conjunto no modelo mais barato.
3. Compare **acerto, custo e latência** lado a lado.
4. Se a diferença de acerto for irrelevante para o negócio, use o barato.
5. Se for relevante, considere a **cascata** ([06, exemplo 11](06-exemplos.md)).
6. **Refaça isso a cada modelo novo.** A fronteira se move a cada poucos meses,
   e prompts ajustados a um modelo antigo costumam ficar sub-ótimos.

**Erro comum e caro:** escolher o modelo barato "por precaução" antes de medir,
e passar seis meses lutando com prompt para compensar capacidade que faltava. O
tempo de engenharia custa mais que a diferença de API — quase sempre, e por
larga margem.

---

## 30.6 · Onde o dinheiro vaza

| Vazamento | Como aparece | Correção |
|---|---|---|
| histórico inteiro reenviado sem necessidade | custo cresce ao quadrado da conversa | janela, compactação, memória |
| exemplos que não pagam o aluguel | 8 exemplos, 2 fazem efeito | ablação |
| pensamento estendido em tarefa trivial | conta alta em classificação simples | esforço baixo ou desligado |
| repetição por falha de formato | cada retentativa é uma chamada inteira | saída estruturada |
| agente sem limite de passos | cauda de custo altíssima | política de parada |
| cache invalidado sem ninguém notar | custo 10× o esperado, sem sintoma visível | monitorar leitura de cache |
| conjunto de avaliação rodado a cada commit | US$ 3 por PR × 200 PRs/mês | conjunto reduzido no PR, completo à noite |

---

## Autoteste

1. Por que a saída custa 5× a entrada, e o que isso implica na sua escrita?
2. Uma conversa de 20 turnos: por que o custo não é linear?
3. O que é casamento por prefixo e por que um carimbo de data no topo é
   desastroso?
4. Como detectar em 30 segundos que o cache não está sendo aproveitado?
5. Qual é a diferença entre TTFT e tempo total, e qual você reduz cortando a
   saída?
6. Streaming deixa mais rápido? Explique.
7. Por que escolher o modelo barato antes de medir costuma sair caro?
