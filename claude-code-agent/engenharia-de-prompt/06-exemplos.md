# 6 · Exemplos — 12 casos, do trivial ao de produção

**Nível:** iniciante → avançado · **Escrito em:** 19/08/2026

Cada exemplo tem: **problema → prompt → código de verificação → o que ele
ensina**. Todo código Python aqui roda em Python 3.10+ **sem instalar nada**;
o que precisa da API está marcado com 💳 e traz a saída esperada.

> **Convenção deste arquivo:** o *prompt* é sempre mostrado inteiro, e a
> *verificação* é sempre código. Prompt sem verificação é opinião.

---

## Exemplo 1 · Extrair campos de texto livre

**Problema.** Transformar mensagens de contato em registros de CRM.

```
Extraia os dados de contato do texto delimitado.

Responda com apenas o JSON, sem texto antes ou depois:
{"nome": "...", "email": "...", "telefone": "...", "empresa": "..."}

Regras:
- Use null para o campo que não estiver no texto. Não infira, não complete.
- Telefone: apenas dígitos, com DDD, sem formatação.
- Nome: como escrito no texto, sem títulos ("Sr.", "Dra.").

<texto>
Bom dia, sou o Dr. Paulo Menezes, da Clínica Vitalis. Ligue (31) 98765-4321.
</texto>
```

**Verificação** (roda local, sobre a saída do modelo):

```python
# verificar_contato.py
import json, re, sys

ESPERADOS = {"nome", "email", "telefone", "empresa"}

def verificar(bruto: str) -> list[str]:
    problemas = []
    try:
        d = json.loads(bruto)
    except json.JSONDecodeError as e:
        return [f"JSON inválido: {e}"]
    if set(d) != ESPERADOS:
        problemas.append(f"chaves erradas: {sorted(d)}")
    tel = d.get("telefone")
    if tel is not None and not re.fullmatch(r"\d{10,11}", str(tel)):
        problemas.append(f"telefone fora do formato: {tel!r}")
    if d.get("nome", "").startswith(("Dr.", "Dra.", "Sr.", "Sra.")):
        problemas.append("título não foi removido do nome")
    return problemas

if __name__ == "__main__":
    saida = sys.stdin.read()
    p = verificar(saida)
    print("OK" if not p else "\n".join(p))
```

```bash
echo '{"nome":"Paulo Menezes","email":null,"telefone":"31987654321","empresa":"Clínica Vitalis"}' \
  | python3 verificar_contato.py
# esperado: OK
```

**O que ensina.** As três regras existem porque, sem elas, o modelo
respectivamente: inventa e-mail plausível, devolve `(31) 98765-4321` num dia e
`+55 31 98765-4321` no outro, e mantém "Dr.". Cada regra do prompt deveria
nascer de um erro observado — não de imaginação.

---

## Exemplo 2 · Classificar com conjunto fechado

**Problema.** Rotear chamados para quatro filas.

Este exemplo está implementado, medido e testado por inteiro em
[07-projeto-modelo](07-projeto-modelo/README.md). Resultado medido em
19/08/2026, 22 casos: prompt ingênuo 0%, estruturado 82%, com exemplos 91%.

**O que ensina.** A diferença entre 0% e 82% não foi "escrever melhor" — foi
**enumerar as categorias** e **fixar o formato**. Ganhos grandes quase sempre
vêm de especificação faltando, não de refinamento estilístico.

---

## Exemplo 3 · Reescrever tom sem alterar fatos

**Problema.** Transformar respostas técnicas em respostas ao cliente, sem
mudar nenhum dado.

```
Reescreva a resposta técnica abaixo para um cliente leigo.

Restrições invioláveis:
1. Não altere nenhum número, data, valor ou nome próprio.
2. Não acrescente informação que não esteja no original — inclusive promessas
   de prazo.
3. Não remova nenhuma informação factual.
4. Máximo de 4 frases. Tom cordial e direto, sem "peço desculpas pelo
   transtorno".

<resposta_tecnica>
Incidente identificado: degradação no cluster db-03 entre 14h12 e 15h47 do dia
12/08. 1.284 requisições retornaram 503. Correção aplicada às 15h47.
</resposta_tecnica>
```

**Verificação** — a métrica correta aqui é *preservação de fatos*:

```python
# verificar_tom.py
import re

def numeros(texto: str) -> set[str]:
    """Extrai todo token numérico relevante: horas, datas, quantidades."""
    return set(re.findall(r"\d+(?:[.,:/]\d+)*", texto))

ORIGINAL = ("Incidente identificado: degradação no cluster db-03 entre 14h12 e "
            "15h47 do dia 12/08. 1.284 requisições retornaram 503. "
            "Correção aplicada às 15h47.")

def verificar(reescrita: str) -> list[str]:
    faltando = numeros(ORIGINAL) - numeros(reescrita)
    inventados = numeros(reescrita) - numeros(ORIGINAL)
    problemas = []
    if faltando:
        problemas.append(f"fatos numéricos perdidos: {sorted(faltando)}")
    if inventados:
        problemas.append(f"números inventados: {sorted(inventados)}")
    if reescrita.count(".") > 6:
        problemas.append("provavelmente passou de 4 frases")
    return problemas or ["OK"]

print(verificar(
    "Entre 14h12 e 15h47 do dia 12/08, nosso banco de dados db-03 ficou lento. "
    "Nesse período, 1.284 requisições falharam com o código 503. "
    "A correção foi aplicada às 15h47 e o serviço voltou ao normal."))
```

```bash
python3 verificar_tom.py
# esperado: ['OK']
```

**O que ensina.** Tarefa "subjetiva" quase sempre esconde um núcleo objetivo
mensurável. Aqui o núcleo é: nenhum número some, nenhum número aparece. Meça
esse núcleo automaticamente e reserve o julgamento humano para o resto.

---

## Exemplo 4 · Resumir com limite duro

**Problema.** Resumo que precisa caber num campo de 200 caracteres do banco.

```
Resuma o texto delimitado em no máximo 200 caracteres.

- Uma única frase, sem ponto final.
- Priorize: o que aconteceu, com quem, quando.
- Não use "este texto fala sobre".

<texto>
{{TEXTO}}
</texto>
```

**Verificação e recuperação:**

```python
# resumir_com_limite.py
LIMITE = 200

def aceitar(resumo: str) -> bool:
    return len(resumo) <= LIMITE and resumo.count(".") == 0

def instrucao_de_correcao(resumo: str) -> str:
    return (f"Seu resumo tem {len(resumo)} caracteres; o limite é {LIMITE}. "
            f"Reescreva cortando {len(resumo) - LIMITE} caracteres, "
            f"preservando quem, o quê e quando.")

exemplo = "x" * 240
print(aceitar(exemplo), "|", instrucao_de_correcao(exemplo))
```

```bash
python3 resumir_com_limite.py
# esperado: False | Seu resumo tem 240 caracteres; o limite é 200. Reescreva cortando 40 caracteres, preservando quem, o quê e quando.
```

**O que ensina.** Modelo **não conta caracteres com precisão** — ele não vê
caracteres, vê tokens ([10-fundamentos](10-fundamentos.md)). Peça o limite,
verifique por programa, e devolva o número exato que faltou cortar. Devolver o
erro **quantificado** é muito mais eficaz que repetir "seja mais curto".

---

## Exemplo 5 · Traduzir com glossário obrigatório

**Problema.** Traduzir documentação mantendo termos da empresa intactos.

```
Traduza o texto de inglês para português do Brasil.

<glossario_obrigatorio>
Estes termos NÃO devem ser traduzidos, em nenhuma circunstância:
- workspace  (mantenha "workspace")
- deploy     (mantenha "deploy")
- rollback   (mantenha "rollback")
</glossario_obrigatorio>

Regras: mantenha a formatação markdown, os blocos de código intactos e os
nomes de produto como estão.

<texto>
{{TEXTO}}
</texto>
```

**Verificação:**

```python
# verificar_glossario.py
GLOSSARIO = ["workspace", "deploy", "rollback"]
PROIBIDOS = {"workspace": ["espaço de trabalho", "área de trabalho"],
             "deploy": ["implantação", "implementação"],
             "rollback": ["reversão", "retrocesso"]}

def verificar(origem: str, traducao: str) -> list[str]:
    problemas = []
    baixa = traducao.lower()
    for termo in GLOSSARIO:
        if termo in origem.lower() and termo not in baixa:
            problemas.append(f"termo obrigatório sumiu: {termo}")
        for ruim in PROIBIDOS[termo]:
            if ruim in baixa:
                problemas.append(f"traduziu indevidamente: {ruim}")
    return problemas or ["OK"]

print(verificar("Run a deploy, then rollback if needed.",
                "Execute um deploy e faça rollback se necessário."))
print(verificar("Run a deploy.", "Execute uma implantação."))
```

```bash
python3 verificar_glossario.py
# esperado:
# ['OK']
# ['termo obrigatório sumiu: deploy', 'traduziu indevidamente: implantação']
```

**O que ensina.** Restrição verificável vale dez vezes mais que restrição
subjetiva. "Traduza bem" não é testável; "estes 3 termos não podem ser
traduzidos" é — e vira portão de CI.

---

## Exemplo 6 · Gerar SQL sem abrir buraco de segurança

**Problema.** Perguntas em português viram consulta ao banco.

```
Você gera consultas SQL somente-leitura para PostgreSQL.

<esquema>
pedidos(id int, cliente_id int, valor numeric, status text, criado_em date)
clientes(id int, nome text, cidade text)
</esquema>

Regras invioláveis:
1. Apenas SELECT. Nunca INSERT, UPDATE, DELETE, DROP, ALTER, GRANT, COPY.
2. Use apenas as tabelas e colunas do esquema acima.
3. Todo valor vindo do usuário vira parâmetro numerado ($1, $2), nunca
   concatenado no texto da consulta.
4. Sempre inclua LIMIT 100.

Responda com apenas o JSON:
{"sql": "...", "parametros": [...]}

Pergunta: {{PERGUNTA}}
```

**Verificação — a parte que realmente protege:**

```python
# validar_sql.py
import re

PROIBIDAS = re.compile(
    r"\b(insert|update|delete|drop|alter|grant|truncate|copy|create)\b", re.I)
TABELAS_OK = {"pedidos", "clientes"}

def validar(sql: str) -> list[str]:
    problemas = []
    if not sql.strip().lower().startswith("select"):
        problemas.append("não começa com SELECT")
    if PROIBIDAS.search(sql):
        problemas.append("contém palavra-chave de escrita")
    if ";" in sql.strip().rstrip(";"):
        problemas.append("múltiplas instruções (';' no meio)")
    if "limit" not in sql.lower():
        problemas.append("sem LIMIT")
    for tabela in re.findall(r"\bfrom\s+(\w+)|\bjoin\s+(\w+)", sql, re.I):
        nome = (tabela[0] or tabela[1]).lower()
        if nome not in TABELAS_OK:
            problemas.append(f"tabela fora do esquema: {nome}")
    if re.search(r"'[^']*'", sql):
        problemas.append("literal em aspas: deveria ser parâmetro")
    return problemas or ["OK"]

print(validar("SELECT nome FROM clientes WHERE cidade = $1 LIMIT 100"))
print(validar("SELECT * FROM clientes; DROP TABLE pedidos;"))
print(validar("SELECT * FROM usuarios WHERE nome = 'admin' LIMIT 10"))
```

```bash
python3 validar_sql.py
# esperado:
# ['OK']
# ['contém palavra-chave de escrita', "múltiplas instruções (';' no meio)", 'sem LIMIT']
# ['tabela fora do esquema: usuarios', 'literal em aspas: deveria ser parâmetro']
```

**O que ensina.** As regras no prompt reduzem a chance de SQL perigoso; **elas
não a eliminam**. Quem garante é o validador, e — em produção — um usuário de
banco com permissão apenas de leitura. Regra geral: **prompt reduz
probabilidade; arquitetura garante propriedade.**

---

## Exemplo 7 · Texto solto para tabela

**Problema.** Notas de reunião viram linhas de planilha.

```
Extraia as decisões do texto para um array JSON. Cada item:
{"decisao": "...", "responsavel": "...", "prazo": "AAAA-MM-DD ou null"}

Regras:
- Somente decisões tomadas. Ignore sugestões, dúvidas e "vamos pensar".
- responsavel: primeiro nome apenas; null se não houver dono explícito.
- prazo: converta "sexta que vem" usando a data da reunião ({{DATA}}) como
  referência; se ambíguo, use null em vez de chutar.
- Devolva [] se não houver decisão nenhuma.

<notas>
{{NOTAS}}
</notas>
```

**Verificação:**

```python
# verificar_decisoes.py
import json, re
from datetime import date

def verificar(bruto: str, data_reuniao: date) -> list[str]:
    try:
        itens = json.loads(bruto)
    except json.JSONDecodeError as e:
        return [f"JSON inválido: {e}"]
    if not isinstance(itens, list):
        return ["esperava um array"]
    problemas = []
    for i, it in enumerate(itens):
        if set(it) != {"decisao", "responsavel", "prazo"}:
            problemas.append(f"item {i}: chaves {sorted(it)}")
        prazo = it.get("prazo")
        if prazo is not None:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", prazo):
                problemas.append(f"item {i}: prazo fora do formato: {prazo}")
            elif date.fromisoformat(prazo) < data_reuniao:
                problemas.append(f"item {i}: prazo no passado: {prazo}")
    return problemas or ["OK"]

print(verificar('[{"decisao":"Migrar o banco","responsavel":"Ana","prazo":"2026-08-28"}]',
                date(2026, 8, 19)))
print(verificar('[{"decisao":"x","responsavel":null,"prazo":"28/08/2026"}]',
                date(2026, 8, 19)))
```

```bash
python3 verificar_decisoes.py
# esperado:
# ['OK']
# ['item 0: prazo fora do formato: 28/08/2026']
```

**O que ensina.** Data relativa ("sexta que vem") é a fonte silenciosa de erro
número um em extração. O modelo **não sabe que dia é hoje** — a data tem de
entrar no prompt. E "se ambíguo, use null" evita a invenção confiante.

---

## Exemplo 8 · Roteamento com escape e limiar

**Problema.** Encaminhar ao time certo, e **saber quando não sabe**.

```
Classifique a mensagem em uma das filas: vendas, suporte, financeiro, juridico,
outro.

Use "outro" quando a mensagem não pertencer claramente a nenhuma das quatro.
É melhor devolver "outro" do que forçar um encaixe.

Devolva também sua confiança, de 0 a 1, calibrada assim:
- 0.9+ : a mensagem cita explicitamente o assunto da fila
- 0.6–0.9 : o assunto está implícito, mas é o mais provável
- <0.6 : você está adivinhando

Responda com apenas: {"fila": "...", "confianca": 0.0}
```

```python
# rotear.py
LIMIAR = 0.6

def rotear(resposta: dict) -> str:
    if resposta["fila"] == "outro" or resposta["confianca"] < LIMIAR:
        return "fila_humana"
    return resposta["fila"]

print(rotear({"fila": "financeiro", "confianca": 0.93}))
print(rotear({"fila": "juridico", "confianca": 0.41}))
print(rotear({"fila": "outro", "confianca": 0.99}))
```

```bash
python3 rotear.py
# esperado:
# financeiro
# fila_humana
# fila_humana
```

**O que ensina.** Duas coisas, e a segunda é desconfortável:

1. Toda taxonomia precisa de uma saída de escape, senão o caso raro vai para a
   categoria errada com toda a confiança do mundo.
2. **A "confiança" que o modelo declara não é probabilidade calibrada** — é
   texto gerado. Ela correlaciona o suficiente para servir de triagem grosseira
   e **não** o suficiente para decisão automática de alto risco. Calibração de
   verdade se faz medindo: separe por faixa declarada e conte o acerto real de
   cada faixa. Ver [60-teoria-avancada §calibração](60-teoria-avancada.md).

---

## Exemplo 9 · Modelo como juiz (avaliação automática)

**Problema.** Avaliar 500 respostas de atendimento sem ler as 500.

```
Você avalia respostas de atendimento. Seja rigoroso: a nota alta é exceção.

<criterios>
1. Correção factual (0–2): não contradiz a base de conhecimento fornecida.
2. Completude (0–2): responde tudo que foi perguntado.
3. Tom (0–1): cordial, direto, sem jargão.
</criterios>

Avalie primeiro, some depois. Responda com apenas:
{"correcao": 0, "completude": 0, "tom": 0, "total": 0, "justificativa": "..."}

A justificativa deve citar o trecho exato que motivou o desconto.

<base_de_conhecimento>{{BASE}}</base_de_conhecimento>
<pergunta>{{PERGUNTA}}</pergunta>
<resposta_avaliada>{{RESPOSTA}}</resposta_avaliada>
```

```python
# juiz.py — verificações que o juiz também precisa passar
def validar_nota(n: dict) -> list[str]:
    problemas = []
    limites = {"correcao": 2, "completude": 2, "tom": 1}
    for campo, teto in limites.items():
        if not (0 <= n.get(campo, -1) <= teto):
            problemas.append(f"{campo} fora da escala: {n.get(campo)}")
    soma = sum(n.get(c, 0) for c in limites)
    if n.get("total") != soma:
        problemas.append(f"total {n.get('total')} != soma {soma}")
    if len(n.get("justificativa", "")) < 20:
        problemas.append("justificativa vazia demais para ser auditável")
    return problemas or ["OK"]

print(validar_nota({"correcao": 2, "completude": 1, "tom": 1, "total": 4,
                    "justificativa": "Não mencionou o prazo de 5 dias úteis."}))
print(validar_nota({"correcao": 3, "completude": 1, "tom": 1, "total": 4,
                    "justificativa": "ok"}))
```

```bash
python3 juiz.py
# esperado:
# ['OK']
# ['correcao fora da escala: 3', 'total 4 != soma 5', 'justificativa vazia demais para ser auditável']
```

**O que ensina.** O juiz automático é a ferramenta mais útil e mais perigosa da
avaliação. Vieses documentados que você **precisa** controlar:

| Viés | Como se manifesta | Mitigação |
|---|---|---|
| **posição** | prefere a primeira (ou a última) resposta em comparações | rode A/B e B/A e descarte quando discordar |
| **verbosidade** | prefere resposta longa | fixe faixa de tamanho ou desconte explicitamente |
| **autofavorecimento** | o modelo prefere texto gerado por ele mesmo | use juiz de outra família de modelo |
| **generosidade** | dá nota alta por padrão | escala curta, "nota alta é exceção", rubrica com âncoras |

E a regra inegociável: **calibre o juiz contra rótulo humano** em ao menos 50
casos, e reporte a concordância. Juiz não validado é gerador de números
bonitos. Ver [20-avaliacao-e-evals](20-avaliacao-e-evals.md).

---

## Exemplo 10 · Few-shot dinâmico (escolher exemplos por similaridade)

**Problema.** Você tem 400 exemplos rotulados; cabem 5 no prompt. Quais mandar?

Resposta: os 5 **mais parecidos com o caso atual**, escolhidos em tempo de
execução. Em produção, a similaridade vem de *embeddings*; aqui está a versão
sem dependência nenhuma, boa o bastante para entender o mecanismo:

```python
# fewshot_dinamico.py — seleção por similaridade de Jaccard, sem bibliotecas
import re

BANCO = [
    ("Fui cobrado duas vezes na fatura", "cobranca"),
    ("O boleto veio com valor errado", "cobranca"),
    ("Erro 500 ao salvar o formulário", "bug"),
    ("A tela de relatórios trava", "bug"),
    ("Esqueci minha senha", "acesso"),
    ("Minha conta está bloqueada", "acesso"),
    ("Como faço para trocar de plano?", "duvida"),
]

def tokens(t: str) -> set[str]:
    return set(re.findall(r"\w+", t.lower()))

def similaridade(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    return len(ta & tb) / len(ta | tb) if ta | tb else 0.0

def escolher(caso: str, k: int = 3) -> list[tuple[str, str]]:
    return sorted(BANCO, key=lambda e: similaridade(caso, e[0]), reverse=True)[:k]

def montar_prompt(caso: str) -> str:
    exemplos = "\n".join(
        f'<exemplo>entrada: "{t}"\nsaida: {{"categoria": "{c}"}}</exemplo>'
        for t, c in escolher(caso))
    return f"<exemplos>\n{exemplos}\n</exemplos>\n\nentrada: \"{caso}\"\nsaida:"

print(montar_prompt("O boleto do meu plano veio errado"))
```

```bash
python3 fewshot_dinamico.py
# saída real da execução em 19/08/2026:
# <exemplos>
# <exemplo>entrada: "O boleto veio com valor errado"
# saida: {"categoria": "cobranca"}</exemplo>
# <exemplo>entrada: "Erro 500 ao salvar o formulário"
# saida: {"categoria": "bug"}</exemplo>
# <exemplo>entrada: "Como faço para trocar de plano?"
# saida: {"categoria": "duvida"}</exemplo>
# </exemplos>
#
# entrada: "O boleto do meu plano veio errado"
# saida:
```

**Olhe a saída com atenção: só um dos três exemplos é de cobrança.** O segundo
entrou por causa da palavra "erro"/"errado" e o terceiro por causa de "plano".
Isso não é bug do código — é a limitação real da similaridade por palavras
(Jaccard), que não sabe que "boleto" e "cobrado" falam da mesma coisa. É
exatamente por esse motivo que sistemas de produção usam *embeddings*
(representações vetoriais de sentido) em vez de sobreposição de tokens. Ver
[15-contexto-e-rag](15-contexto-e-rag.md).

**O que ensina.** Few-shot dinâmico costuma bater few-shot fixo com o mesmo
número de exemplos, porque cada chamada gasta seus tokens com o que é
relevante *para aquele caso*. Preço: você perde o cache de prompt — o prefixo
muda toda vez ([30](30-custo-latencia-caching.md)). Trade-off real, medível,
sem resposta universal.

---

## Exemplo 11 · 🏭 Produção — cascata de modelos

**Problema real.** 200 mil mensagens/mês para moderar. O modelo grande resolve
com 97% de acerto e custa caro. O pequeno acerta 89% e custa 5× menos.

**Solução.** Cascata: o pequeno resolve o fácil, o grande resolve o duvidoso.

```python
# cascata.py — a matemática da decisão, sem chamar API
CUSTO_PEQUENO = 1.0     # unidades arbitrárias por mensagem
CUSTO_GRANDE = 5.0
ACERTO_PEQUENO = 0.89
ACERTO_GRANDE = 0.97

def simular(fracao_escalada: float, acerto_pequeno_nos_faceis: float = 0.98):
    """fracao_escalada: quanto do tráfego o pequeno manda para o grande."""
    custo = CUSTO_PEQUENO + fracao_escalada * CUSTO_GRANDE
    acerto = ((1 - fracao_escalada) * acerto_pequeno_nos_faceis
              + fracao_escalada * ACERTO_GRANDE)
    return custo, acerto

print(f"{'estratégia':<28} {'custo':>7} {'acerto':>8}")
print(f"{'só o grande':<28} {CUSTO_GRANDE:>7.2f} {ACERTO_GRANDE:>8.1%}")
print(f"{'só o pequeno':<28} {CUSTO_PEQUENO:>7.2f} {ACERTO_PEQUENO:>8.1%}")
for f in (0.10, 0.20, 0.30):
    c, a = simular(f)
    print(f"{'cascata, escala ' + f'{f:.0%}':<28} {c:>7.2f} {a:>8.1%}")
```

```bash
python3 cascata.py
# esperado:
# estratégia                     custo   acerto
# só o grande                     5.00    97.0%
# só o pequeno                    1.00    89.0%
# cascata, escala 10%             1.50    97.9%
# cascata, escala 20%             2.00    97.8%
# cascata, escala 30%             2.50    97.7%
```

**Leia com ceticismo — inclusive esta tabela.** O número que decide tudo é
`acerto_pequeno_nos_faceis`: **só a medição diz** se o modelo pequeno sabe
reconhecer o que é fácil. Se ele escalar os casos errados, a cascata custa mais
e acerta menos que qualquer um dos dois sozinho. Meça antes de acreditar.

**Como o pequeno decide escalar:** confiança declarada abaixo do limiar, ou
divergência entre duas execuções, ou presença de gatilhos definidos por você
(ambiguidade, menção jurídica, valor alto).

**O que ensina.** Em produção, a pergunta raramente é "qual o melhor prompt?".
É "qual arranjo de modelo, prompt e limiar entrega o acerto exigido pelo menor
custo?". Isso é engenharia de sistema, e é o que separa a faixa salarial.

---

## Exemplo 12 · 🏭 Produção — geração em escala com cache e verificação de fatos

**Problema real.** 50 mil descrições de produto por mês, a partir da ficha
técnica. Requisitos: nenhum dado inventado, tom da marca, custo sob controle.

**Arquitetura do prompt** (a ordem importa, e é por causa do cache):

```
[ESTÁVEL — cacheado]
  1. Papel + manual de marca (2.000 tokens, idêntico em toda chamada)
  2. 6 exemplos de descrições aprovadas (1.500 tokens)
  3. Regras: só use atributos da ficha; nunca invente medida, material ou
     garantia; não use superlativo sem dado ("o melhor" é proibido)
[VOLÁTIL — muda a cada produto]
  4. <ficha_tecnica>...</ficha_tecnica>
```

**Verificação obrigatória antes de publicar:**

```python
# verificar_descricao.py
import re

PROIBIDOS = ["o melhor", "imbatível", "líder de mercado", "número 1",
             "garantia vitalícia"]

def verificar(ficha: dict, descricao: str) -> list[str]:
    problemas = []
    baixa = descricao.lower()

    for termo in PROIBIDOS:
        if termo in baixa:
            problemas.append(f"superlativo/promessa proibida: '{termo}'")

    # Todo número na descrição precisa existir na ficha técnica.
    numeros_ficha = {re.sub(r"[^\d]", "", str(v))
                     for v in ficha.values() if re.search(r"\d", str(v))}
    for n in re.findall(r"\d+(?:[.,]\d+)?", descricao):
        if re.sub(r"[^\d]", "", n) not in numeros_ficha:
            problemas.append(f"número não consta da ficha: {n}")

    if len(descricao) > 600:
        problemas.append(f"passou do limite: {len(descricao)} caracteres")
    return problemas or ["OK"]

FICHA = {"material": "alumínio anodizado", "peso": "1,2 kg",
         "altura": "45 cm", "garantia": "12 meses"}

print(verificar(FICHA, "Suporte em alumínio anodizado, 45 cm de altura e "
                       "1,2 kg. Garantia de 12 meses."))
print(verificar(FICHA, "O melhor suporte do mercado, com 60 cm e garantia "
                       "vitalícia."))
```

```bash
python3 verificar_descricao.py
# esperado:
# ['OK']
# ["superlativo/promessa proibida: 'o melhor'", "superlativo/promessa proibida: 'garantia vitalícia'", 'número não consta da ficha: 60']
```

**A conta de custo** (preços de 19/08/2026, Claude Opus 5: US$ 5,00/milhão de
entrada; leitura de cache custa ~10% da entrada):

| Cenário | Entrada/chamada | 50 mil chamadas | Custo estimado |
|---|---|---|---|
| Sem cache | 3.700 tokens | 185 M tokens | ~US$ 925 |
| Com cache do prefixo estável (3.500 fixos) | 200 novos + 3.500 lidos do cache | 10 M + 175 M a 10% | ~US$ 138 |
| Com cache **e** lote assíncrono (−50%) | idem | idem | ~US$ 69 |

Mesma qualidade, ~13× mais barato. **É por isso que ordem de prompt é assunto
de engenharia, não de estilo.** (Estimativas de ordem de grandeza: não
substituem a fatura; e o custo de *escrita* no cache, cobrado a 1,25×, é
desprezível quando o prefixo é reaproveitado milhares de vezes.)

**O que ensina.** Em escala, o prompt tem duas dimensões: a que produz
qualidade e a que produz conta no fim do mês. Você é responsável pelas duas.

---

## Autoteste

1. Por que a verificação de cada exemplo é código, e não leitura?
2. No exemplo 6, o que garante que não vai rodar `DROP TABLE`: o prompt ou o
   validador? E o que garante de fato, em produção?
3. Por que o modelo erra limite de caracteres, e qual é a correção que
   funciona?
4. Cite três vieses do modelo-juiz e a mitigação de cada um.
5. Few-shot dinâmico melhora o acerto. O que ele **quebra**?
6. Na cascata, qual é o número que decide se a estratégia vale, e por que não
   dá para supô-lo?
7. Por que o manual de marca vai no **começo** do prompt e a ficha técnica no
   fim?
