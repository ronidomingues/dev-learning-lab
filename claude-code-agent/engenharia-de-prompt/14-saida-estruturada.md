# 14 · Saída estruturada — fazer o modelo falar com o seu programa

**Nível:** intermediário · **Escrito em:** 19/08/2026

Quase toda aplicação séria precisa que a saída do modelo seja **dado**, não
prosa. Este arquivo cobre as três formas de conseguir isso, em ordem de
garantia, e a disciplina de validação que **nenhuma delas dispensa**.

---

## 14.1 · As três formas, e a força de cada uma

| Forma | Como funciona | Garantia | Quando usar |
|---|---|---|---|
| **Pedir no texto** | instrução + esquema literal no prompt | probabilística | protótipo; fornecedor sem suporte |
| **Ferramenta com esquema** | você declara uma função com JSON Schema; o modelo "chama" | alta (com `strict: true`, exata) | quando já se usa ferramentas |
| **Saída estruturada da API** (`output_config.format`) | o servidor restringe a decodificação ao esquema | **a mais alta** | padrão, quando disponível |

**Por que a saída estruturada é qualitativamente diferente?** Porque ela não
persuade o modelo: ela **remove do conjunto de tokens possíveis** tudo que
tornaria o texto inválido segundo o esquema. Um token que quebraria o JSON tem
probabilidade zero de ser escolhido — não porque o modelo se comportou, mas
porque ele não estava disponível. Isso é restrição de decodificação
(*constrained decoding*), e é a única técnica desta área que oferece garantia
sintática de verdade.

**O que ela ainda não garante:** que o *conteúdo* esteja certo. Um CPF com
formato válido e dígito verificador errado passa; uma categoria válida mas
incorreta passa. Sintaxe ≠ semântica. **Valide sempre.**

---

## 14.2 · Escrevendo um esquema que evita erro

```json
{
  "type": "object",
  "properties": {
    "categoria": {
      "type": "string",
      "enum": ["cobranca", "bug", "acesso", "duvida"],
      "description": "Fila de destino. Classifique pelo assunto, não pelas palavras."
    },
    "urgencia": {"type": "string", "enum": ["alta", "normal"]},
    "valor_reclamado": {
      "type": ["number", "null"],
      "description": "Em reais, só se o cliente citar um valor. null se não citar."
    },
    "resumo": {"type": "string", "maxLength": 80}
  },
  "required": ["categoria", "urgencia", "valor_reclamado", "resumo"],
  "additionalProperties": false
}
```

Cinco decisões, e as razões:

| Decisão | Por quê |
|---|---|
| `enum` em vez de `string` livre | elimina a categoria inventada — a falha nº 1 da classificação |
| `["number", "null"]` explícito | sem isto, o modelo devolve `0`, `""` ou `"N/A"` para "não tem" |
| **tudo em `required`**, com `null` permitido | campo opcional some silenciosamente; campo obrigatório anulável é sempre explícito |
| `additionalProperties: false` | impede campos extras inventados (e é exigência de vários modos estritos) |
| `description` em cada campo | **a descrição é prompt** — é lida pelo modelo e muda o resultado |

> **A `description` do esquema é prompt.** Este é o ponto que mais gente
> desperdiça: você pode colocar ali a regra de desambiguação, o formato do
> valor, o que fazer no caso vazio. É instrução no lugar exato onde o modelo
> está decidindo aquele campo.

---

## 14.3 · Validação: o que rodar sobre a saída

Nunca confie no que voltou, nem com decodificação restrita — porque o modelo
pode não estar sob restrição (fornecedor diferente, modo antigo, degradação),
e porque a semântica não é coberta.

Camadas, todas obrigatórias em produção:

1. **Parse** — é JSON mesmo? (trata truncamento e cerca de markdown)
2. **Esquema** — chaves, tipos, enums, tamanhos.
3. **Semântica de negócio** — o valor faz sentido? A data é futura? O total
   bate com a soma?
4. **Referencial** — o id citado existe no seu banco? O trecho citado existe
   mesmo no documento?

Exemplo executável, sem dependências, das camadas 1 a 3:

```python
# validar_saida.py — roda com: python3 validar_saida.py
import json

ENUMS = {"categoria": {"cobranca", "bug", "acesso", "duvida"},
         "urgencia": {"alta", "normal"}}
OBRIGATORIOS = {"categoria", "urgencia", "valor_reclamado", "resumo"}

def validar(bruto: str) -> tuple[dict | None, list[str]]:
    # camada 1 — parse
    try:
        d = json.loads(bruto)
    except json.JSONDecodeError as e:
        return None, [f"JSON inválido ({e.msg}) — verifique truncamento por max_tokens"]
    if not isinstance(d, dict):
        return None, ["esperava um objeto JSON"]

    # camada 2 — esquema
    erros = []
    if set(d) != OBRIGATORIOS:
        faltando, sobrando = OBRIGATORIOS - set(d), set(d) - OBRIGATORIOS
        if faltando:
            erros.append(f"campos ausentes: {sorted(faltando)}")
        if sobrando:
            erros.append(f"campos inventados: {sorted(sobrando)}")
    for campo, validos in ENUMS.items():
        if campo in d and d[campo] not in validos:
            erros.append(f"{campo}={d[campo]!r} fora de {sorted(validos)}")
    valor = d.get("valor_reclamado")
    if valor is not None and not isinstance(valor, (int, float)):
        erros.append(f"valor_reclamado deveria ser número ou null, veio {type(valor).__name__}")
    if isinstance(d.get("resumo"), str) and len(d["resumo"]) > 80:
        erros.append(f"resumo com {len(d['resumo'])} caracteres (máx. 80)")

    # camada 3 — semântica de negócio
    if d.get("urgencia") == "alta" and d.get("categoria") == "duvida":
        erros.append("regra de negócio: dúvida nunca é urgência alta")
    if isinstance(valor, (int, float)) and valor < 0:
        erros.append("valor negativo")

    return d, erros

CASOS = [
    '{"categoria":"cobranca","urgencia":"normal","valor_reclamado":89.9,"resumo":"Cobranca dobrada"}',
    '{"categoria":"financeiro","urgencia":"normal","valor_reclamado":"N/A","resumo":"x"}',
    '{"categoria":"duvida","urgencia":"alta","valor_reclamado":null,"resumo":"x","extra":1}',
    '{"categoria":"bug","urgencia":"normal","valor_reclamado":null,"resumo":"trunc',
]

for i, caso in enumerate(CASOS, 1):
    _, erros = validar(caso)
    print(f"caso {i}: {'OK' if not erros else erros}")
```

```bash
python3 validar_saida.py
```

A saída real, conferida, está no [§14.7](#147--saída-verificada-deste-arquivo)
— vale olhar antes de seguir: os quatro casos cobrem os quatro modos de falha
mais comuns.

---

## 14.4 · Os cinco modos de falha da saída estruturada

| Falha | Sintoma | Causa | Correção |
|---|---|---|---|
| **Truncamento** | JSON que termina no meio | `max_tokens` baixo demais | aumentar `max_tokens`; detectar e repetir |
| **Cerca de markdown** | ` ```json ` em volta | prompt não proibiu | instrução explícita + extração tolerante |
| **Preâmbulo** | "Claro! Aqui está:" antes | idem | idem |
| **Escape divergente** | `\/` ou `\uXXXX` inesperados | variação entre modelos e versões | **sempre** `json.loads`; **nunca** comparar string crua |
| **Campo com "N/A"** | string onde deveria haver `null` | esquema não declarou o tipo nulo | tipo união explícito + descrição do caso vazio |

**Truncamento merece um parágrafo próprio** porque é o mais caro: falha
intermitente, aparece só nos casos longos, passa despercebida em teste com
entrada curta e quebra em produção com a entrada real do cliente. **Sempre
verifique o motivo de parada da resposta** (`stop_reason`): se for
"atingiu o limite de tokens", trate como erro, não como saída.

---

## 14.5 · Streaming com saída estruturada

Se você transmite a resposta em pedaços, **o JSON só é válido no fim**. Duas
consequências:

- não tente parsear pedaço por pedaço com `json.loads` — vai falhar sempre;
- se precisa mostrar progresso ao usuário, ou use um parser incremental
  tolerante, ou mostre um indicador em vez do conteúdo.

Regra de projeto: **nunca envie ao usuário final a saída estruturada crua.**
Ela é interface de máquina. O que o usuário vê é o que o seu programa renderiza
a partir dela — depois de validar.

---

## 14.6 · Quando **não** usar saída estruturada

| Situação | Por quê |
|---|---|
| a saída é texto para humano ler | esquema atrapalha o texto e custa tokens |
| o modelo precisa raciocinar bastante antes | restrição de decodificação pode limitar o raciocínio; use pensamento estendido e estruture só a conclusão |
| você ainda não sabe quais campos quer | descubra com saída livre; estruture quando o formato estabilizar |

Padrão híbrido que funciona bem, e é o que eu recomendo por padrão:
**raciocínio livre em pensamento estendido + conclusão estruturada.**

---

## 14.7 · Saída verificada deste arquivo

Execução real de `validar_saida.py` em 19/08/2026, Python 3.10.12:

```
caso 1: OK
caso 2: ["categoria='financeiro' fora de ['acesso', 'bug', 'cobranca', 'duvida']", 'valor_reclamado deveria ser número ou null, veio str']
caso 3: ["campos inventados: ['extra']", 'regra de negócio: dúvida nunca é urgência alta']
caso 4: ['JSON inválido (Unterminated string starting at) — verifique truncamento por max_tokens']
```

Repare no caso 4: a mensagem do validador **já diz onde investigar**. Mensagem
de erro que aponta a causa provável economiza horas — trate os erros do seu
validador como documentação.

---

## Autoteste

1. Por que a saída estruturada da API é qualitativamente diferente de pedir
   JSON no texto?
2. O que ela **não** garante?
3. Por que declarar todos os campos como obrigatórios, permitindo `null`, é
   melhor que ter campos opcionais?
4. Por que a `description` de cada campo do esquema é considerada prompt?
5. Quais são as quatro camadas de validação, e qual delas exige acesso ao seu
   banco?
6. Como se detecta truncamento e por que ele é o modo de falha mais caro?
7. Em que situação você **não** deve usar saída estruturada?
