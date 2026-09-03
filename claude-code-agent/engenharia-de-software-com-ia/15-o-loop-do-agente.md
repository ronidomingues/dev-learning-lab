# 15 · O laço do agente — o que acontece quando você aperta Enter

**Nível:** intermediário → avançado · **Escrito em:** 20/08/2026

> Sem caixa-preta. Ao final deste arquivo você consegue escrever um agente
> funcional em ~80 linhas — e, mais importante, prever por que o seu falha.

---

## 1 · O laço, em pseudocódigo

```python
def agente(objetivo, ferramentas, max_passos=50):
    mensagens = [
        {"papel": "sistema", "texto": PROMPT_DE_SISTEMA},
        {"papel": "usuario", "texto": objetivo},
    ]

    for passo in range(max_passos):
        resposta = modelo.gerar(mensagens, ferramentas=ferramentas)
        mensagens.append(resposta)

        if not resposta.chamadas_de_ferramenta:
            return resposta.texto              # terminou

        for chamada in resposta.chamadas_de_ferramenta:
            if not permitido(chamada):         # o portão de permissão
                resultado = "negado pelo usuário"
            else:
                resultado = executar(chamada)  # o programa executa, não o modelo
            mensagens.append({"papel": "ferramenta", "texto": resultado})

    return "limite de passos atingido"
```

**É isso.** Todo agente de codificação de 2026 é uma variação disto, com
melhorias de engenharia em cima: compactação de contexto, subagentes, cache,
paralelismo, isolamento.

### O que cada linha implica

| Linha | Implicação prática |
|---|---|
| `mensagens.append(resposta)` | O contexto **só cresce**. Todo erro fica lá |
| `if not chamadas: return` | Ele decide sozinho quando terminou. Esse é o ponto mais frágil |
| `permitido(chamada)` | O único lugar onde você tem controle real |
| `executar(chamada)` | **O programa executa, não o modelo.** Base de toda a segurança |
| `max_passos` | O disjuntor. Sem ele, laço infinito caro |

---

## 2 · As ferramentas básicas, e por que são essas

Praticamente todo agente de código expõe as mesmas cinco:

| Ferramenta | O que faz | Por que existe |
|---|---|---|
| `Read(caminho)` | Lê arquivo | Ver o código |
| `Write/Edit(caminho, ...)` | Escreve arquivo | Mudar o código |
| `Bash(comando)` | Executa no shell | **A mais poderosa e a mais perigosa** |
| `Grep/Glob(padrão)` | Busca | Achar sem ler tudo |
| `WebFetch/WebSearch` | Busca na web | Documentação atual |

### Por que `Bash` é diferente de todas as outras

Porque ela é **universal**: com shell, o agente pode fazer qualquer coisa que
você poderia. Rodar testes, instalar pacote, apagar arquivo, mandar requisição,
ler `~/.ssh/id_rsa`.

É por isso que todo sistema de permissão gira em torno dela. E é por isso que a
combinação "`Bash` liberado" + "acesso à rede" + "conteúdo não confiável no
contexto" é a receita completa de comprometimento — ver
[22-seguranca](22-seguranca.md).

---

## 3 · Onde o laço quebra — os seis modos de falha

Estes são os padrões que você vai reconhecer no dia a dia.

### Falha 1 — Terminar cedo demais

Ele para e declara sucesso sem ter verificado.

**Causa:** o critério de parada é a avaliação dele sobre "terminei", e essa
avaliação é gerada, não medida.

**Correção:** dê um critério **externo e mecânico**.
"Rode `npm test` e não pare até a saída dizer `0 failing`."

### Falha 2 — Laço improdutivo

Tenta A, falha; tenta B, falha; volta para A.

**Causa:** o contexto contém as tentativas anteriores, e nenhuma delas contém a
informação que faltava. Ele está amostrando do mesmo espaço.

**Correção:** interrompa. Não insista. `git checkout .` e recomece com contexto
limpo e **informação nova** (uma pista, um log, uma restrição a mais).

**Sinal:** duas correções sem progresso mensurável. Não espere a terceira.

### Falha 3 — Contornar o obstáculo em vez de resolvê-lo

O teste falha; ele desabilita o teste. O tipo não bate; ele põe `any`. O lint
reclama; ele adiciona `// eslint-disable`.

**Causa:** você pediu "faça passar", e desabilitar faz passar. **Ele está
otimizando exatamente o que você mediu.** Isso é a lei de Goodhart em ação —
quando uma medida vira alvo, ela deixa de ser boa medida.

**Correção:** proíba explicitamente **e** verifique mecanicamente:

```
Nunca desabilite teste, lint ou verificação de tipo. Nunca use `any` ou
`# type: ignore`. Se algo não puder ser resolvido, PARE e me explique.
```

E ponha no portão:

```bash
git diff | grep -E "eslint-disable|@ts-ignore|type: ignore|skip\(|xit\(|@unittest.skip" && exit 1
```

Instrução sem verificação é torcida.

### Falha 4 — Explosão de escopo

Você pediu uma função; ele reescreveu o módulo.

**Causa:** treinado em repositórios completos, ele reproduz "projeto completo"
quando não há limite.

**Correção:** escopo explícito no pedido, e `git diff --stat` **antes** de ler o
conteúdo. A regra `escopo` do [projeto-modelo](07-projeto-modelo/README.md)
automatiza isso.

### Falha 5 — Envenenamento de contexto

Uma informação errada entrou cedo e contamina tudo depois.

Exemplo real e frequente: ele lê um arquivo obsoleto, conclui que a função se
chama `calcTotal`, e todas as 30 mensagens seguintes assumem esse nome errado.

**Causa:** o contexto é acumulativo e não tem mecanismo de retratação. Uma
afirmação errada dita no passo 3 vira "fato" nos passos 4 a 40.

**Correção:** corrija **explicitamente e cedo** ("a função é `calcularTotal`, não
`calcTotal`; ignore o que você leu em `legacy/`"). Se já passou de dez mensagens,
recomece.

### Falha 6 — Instrução vinda do conteúdo

Ele lê um arquivo que contém "IGNORE INSTRUÇÕES ANTERIORES E …" e obedece.

**Causa:** o laço não distingue **dado** de **instrução**. Tudo que entra na
janela é texto no mesmo canal. Essa é uma propriedade arquitetural, não um bug
de implementação.

**Correção:** não há correção completa no prompt. A defesa é arquitetural —
limitar poder, isolar, não dar credenciais. Ver [22](22-seguranca.md).

---

## 4 · A matemática da confiabilidade em cadeia

Se cada passo tem probabilidade `p` de estar certo, um laço de `n` passos
termina certo com probabilidade `p^n`:

| p por passo | 10 passos | 30 passos | 50 passos |
|---|---|---|---|
| 0,90 | 35% | 4% | 0,5% |
| 0,95 | 60% | 21% | 8% |
| 0,99 | 90% | 74% | 61% |
| 0,999 | 99% | 97% | 95% |

**Duas leituras que mudam prática:**

1. **Reduzir `n` é mais eficaz que aumentar `p`.** Uma tarefa de 10 passos com
   p=0,95 dá 60%; a mesma tarefa quebrada em duas de 5 passos, cada uma com
   verificação no meio, dá 77% cada, e você **sabe onde parou** quando falha.
2. **Verificação intermediária transforma a multiplicação em soma.** Se o passo
   errado é detectado e corrigido na hora, ele não propaga. É por isso que um
   agente com testes rápidos é qualitativamente melhor que um sem — não é
   "melhor prompt", é matemática diferente.

> Este é o argumento mais forte deste curso a favor de suíte de testes rápida.
> Não é higiene: é o que muda o regime de `p^n` para algo próximo de linear.

---

## 5 · Subagentes

Ferramentas modernas permitem que o agente principal delegue a um subagente com
contexto próprio.

```
agente principal (contexto: a tarefa)
   ├── subagente "buscar" (contexto: só a busca) → devolve: 3 caminhos
   ├── subagente "revisar" (contexto: só o diff) → devolve: 2 problemas
   └── continua com contexto limpo
```

**Para que serve:** o subagente lê 40 arquivos e devolve três linhas. O contexto
do principal recebe três linhas, não 40 arquivos.

**Quando ajuda:**
- Busca ampla ("onde está X?") — o principal não precisa do lixo da busca.
- Revisão independente — contexto limpo evita o viés de quem escreveu.
- Tarefas paralelas e independentes.

**Quando atrapalha:**
- Tarefa que exige o contexto todo. O subagente não sabe o que o principal sabe.
- Cadeias longas de delegação: cada passagem perde informação, como telefone
  sem fio.

**Regra:** delegue **busca e verificação**, não **decisão**.

---

## 6 · Escreva um agente em 80 linhas

O exercício que mais desmistifica. Requer uma chave de API.

```python
#!/usr/bin/env python3
"""Agente mínimo: lê, escreve e roda comando. ~80 linhas.

Uso: ANTHROPIC_API_KEY=... python3 agente_minimo.py "conserte o bug em app.py"
ATENÇÃO: roda comandos de verdade. Use em pasta descartável.
"""
import json
import os
import subprocess
import sys
import urllib.request

API = "https://api.anthropic.com/v1/messages"
MODELO = "claude-sonnet-5"

FERRAMENTAS = [
    {"name": "ler", "description": "Lê um arquivo de texto.",
     "input_schema": {"type": "object", "properties": {"caminho": {"type": "string"}},
                      "required": ["caminho"]}},
    {"name": "escrever", "description": "Escreve conteúdo num arquivo.",
     "input_schema": {"type": "object",
                      "properties": {"caminho": {"type": "string"},
                                     "conteudo": {"type": "string"}},
                      "required": ["caminho", "conteudo"]}},
    {"name": "rodar", "description": "Executa um comando de shell.",
     "input_schema": {"type": "object", "properties": {"comando": {"type": "string"}},
                      "required": ["comando"]}},
]


def executar(nome, entrada):
    if nome == "ler":
        try:
            return open(entrada["caminho"], encoding="utf-8").read()[:20000]
        except OSError as e:
            return f"erro: {e}"
    if nome == "escrever":
        try:
            with open(entrada["caminho"], "w", encoding="utf-8") as f:
                f.write(entrada["conteudo"])
            return "ok"
        except OSError as e:
            return f"erro: {e}"
    if nome == "rodar":
        # O PORTÃO DE PERMISSÃO. Não remova.
        print(f"\n  >>> {entrada['comando']}")
        if input("  executar? [s/N] ").strip().lower() != "s":
            return "negado pelo usuário"
        r = subprocess.run(entrada["comando"], shell=True, capture_output=True,
                           text=True, timeout=120)
        return f"saida:\n{r.stdout[-8000:]}\nerro:\n{r.stderr[-4000:]}\ncodigo: {r.returncode}"
    return f"ferramenta desconhecida: {nome}"


def chamar(mensagens):
    corpo = json.dumps({
        "model": MODELO, "max_tokens": 8000,
        "tools": FERRAMENTAS, "messages": mensagens,
    }).encode()
    req = urllib.request.Request(API, data=corpo, headers={
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)


def main():
    mensagens = [{"role": "user", "content": " ".join(sys.argv[1:])}]
    for passo in range(30):                       # o disjuntor
        resposta = chamar(mensagens)
        mensagens.append({"role": "assistant", "content": resposta["content"]})

        resultados = []
        for bloco in resposta["content"]:
            if bloco["type"] == "text":
                print(bloco["text"])
            elif bloco["type"] == "tool_use":
                saida = executar(bloco["name"], bloco["input"])
                resultados.append({"type": "tool_result", "tool_use_id": bloco["id"],
                                   "content": saida})
        if not resultados:
            return                                 # terminou
        mensagens.append({"role": "user", "content": resultados})
    print("limite de passos atingido")


if __name__ == "__main__":
    main()
```

### O que fica claro ao rodar isto

1. **Não há mágica.** É um `while` com uma chamada HTTP.
2. **O portão de permissão é uma linha `if`.** Toda a segurança de agente é isso,
   sofisticado.
3. **O contexto cresce visivelmente.** Você vê o custo subir a cada passo.
4. **`max_tokens`, `timeout` e o limite de passos são disjuntores.** Sem eles,
   um laço mal comportado queima dinheiro em silêncio.
5. **Truncar a saída (`[-8000:]`) é decisão de engenharia.** Um `npm install`
   despeja 3.000 linhas; sem truncar, uma execução enche a janela.

---

## Autoteste

1. Escreva o laço do agente em pseudocódigo, de memória.
2. Por que `Bash` é qualitativamente diferente das outras ferramentas?
3. Cite os seis modos de falha do laço e a correção de cada um.
4. Por que "ele desabilitou o teste" não é desonestidade do modelo, e sim
   consequência do que você mediu? Que lei isso ilustra?
5. Faça a conta: 30 passos com p=0,95. Qual a chance de sucesso?
6. Por que reduzir `n` é mais eficaz que aumentar `p`?
7. Como verificação intermediária muda o regime de `p^n`?
8. Para que servem subagentes e qual é a regra sobre o que delegar a eles?
9. No agente de 80 linhas, onde está toda a segurança?
10. Por que truncar a saída de comando é decisão de engenharia e não detalhe?

---

**Anterior:** [14-contexto-e-o-repositorio](14-contexto-e-o-repositorio.md) ·
**Próximo:** [16-especificacao-e-plano](16-especificacao-e-plano.md)
