# 4 · Como começar — do ambiente pronto ao primeiro resultado

**Nível:** iniciante · **Escrito em:** 20/08/2026

> Este arquivo assume o ambiente do [03-instalacao](03-instalacao.md) já pronto.
> Não repetimos instalação aqui.

---

## O que você vai ter ao final deste arquivo

Um ciclo completo de trabalho profissional com agente, feito uma vez, do começo
ao fim:

```
especificar → delegar → verificar → revisar → commitar
```

Não é "hello world de IA". É o **hábito** que separa L2 de L3 na escala do
[01](01-introducao-leigo.md). Se você só fizer isto do arquivo inteiro e repetir
todo dia, já valeu.

Tempo: **40 minutos**.

---

## O erro que 90% das pessoas comete no primeiro dia

Abrir o agente numa base de código real, sem preparo, e pedir:

> *"melhora esse projeto"*

E receber 600 linhas alteradas em 14 arquivos, sem saber o que aconteceu.

Vamos fazer o oposto: um projeto novo, minúsculo, onde você consegue conferir
**cada coisa**. O objetivo não é o resultado — é você conseguir enxergar o
mecanismo.

---

## Passo 1 · Criar o campo de provas

```bash
mkdir -p ~/lab-ia/conversor && cd ~/lab-ia/conversor
git init
```

*O que faz:* cria uma pasta e um repositório Git vazio.

**Por que o `git init` vem antes de tudo:** o Git é o seu botão de desfazer. Sem
ele, "a IA estragou tudo" é irreversível; com ele, é `git checkout .`. Nunca
solte um agente numa pasta que não é um repositório.

**Verificação:**

```bash
git status
# esperado:
# On branch main
# No commits yet
# nothing to commit (create/copy files and use "git add" to track)
```

---

## Passo 2 · Escrever a especificação ANTES de qualquer código

Esta é a inversão que importa. Você não vai pedir código; vai **definir o que
significa estar certo**.

```bash
cat > ESPEC.md <<'EOF'
# Conversor de unidades — especificação

## Objetivo
Uma função `converter(valor, de, para)` em Python que converte entre unidades
de temperatura.

## Unidades suportadas
`"C"` (Celsius), `"F"` (Fahrenheit), `"K"` (Kelvin).

## Critérios de aceitação
1. converter(0, "C", "F") == 32.0
2. converter(100, "C", "F") == 212.0
3. converter(0, "C", "K") == 273.15
4. converter(-40, "C", "F") == -40.0
5. converter(32, "F", "C") == 0.0
6. Converter para a mesma unidade devolve o valor inalterado.
7. Unidade desconhecida levanta `ValueError` com a unidade citada na mensagem.
8. Temperatura abaixo do zero absoluto (-273.15 C) levanta `ValueError`.

## Restrições
- Apenas biblioteca padrão do Python. Zero dependências.
- Uma função pública; funções auxiliares podem existir.
- Comparações de float com tolerância de 1e-9.

## Fora de escopo
Interface de linha de comando, outras grandezas, internacionalização.
EOF
```

Leia os critérios de novo. Repare em três coisas:

| O que fizemos | Por quê |
|---|---|
| Critérios são **executáveis**, não adjetivos | "converter(-40,'C','F') == -40.0" é verificável; "deve ser preciso" não é |
| Incluímos **casos de erro** (7 e 8) | O modelo, deixado sozinho, escreve o caminho feliz e esquece o resto. Esse é o viés mais previsível dele |
| Escrevemos **"fora de escopo"** | Sem isso, o agente entrega uma CLI, um `README`, um `setup.py` e um `Dockerfile` que você não pediu |

> **O caso -40 não está ali por acaso.** É o único ponto onde as escalas Celsius
> e Fahrenheit coincidem. Se a fórmula estiver invertida, esse caso passa
> mesmo assim — por isso ele **sozinho** não prova nada, mas junto com o 0 e o
> 100 fecha o cerco. Escolher casos de teste que discriminam entre implementações
> erradas é uma habilidade, e é a habilidade central de quem verifica máquina.

---

## Passo 3 · Escrever o teste você mesmo

Sim, você. À mão. Desta vez.

```bash
cat > test_conversor.py <<'EOF'
import math
import pytest
from conversor import converter


def perto(a, b):
    return math.isclose(a, b, abs_tol=1e-9)


def test_celsius_para_fahrenheit():
    assert perto(converter(0, "C", "F"), 32.0)
    assert perto(converter(100, "C", "F"), 212.0)


def test_celsius_para_kelvin():
    assert perto(converter(0, "C", "K"), 273.15)


def test_ponto_de_coincidencia():
    assert perto(converter(-40, "C", "F"), -40.0)


def test_fahrenheit_para_celsius():
    assert perto(converter(32, "F", "C"), 0.0)


def test_mesma_unidade():
    assert perto(converter(25, "C", "C"), 25.0)


def test_unidade_desconhecida():
    with pytest.raises(ValueError) as erro:
        converter(10, "C", "X")
    assert "X" in str(erro.value)


def test_abaixo_do_zero_absoluto():
    with pytest.raises(ValueError):
        converter(-300, "C", "K")
EOF
```

Instale o pytest e rode:

```bash
uv run --with pytest pytest -q
```

*O que faz:* cria um ambiente temporário com o pytest e roda os testes.

**Se você não instalou o `uv`**, use qualquer uma destas alternativas — o resto
do arquivo funciona igual, só troque o comando:

```bash
python3 -m pip install --user pytest && python3 -m pytest -q
```

```bash
pipx run pytest -q
```

**Saída esperada — e ela DEVE falhar:**

```
ImportError: cannot import name 'converter' from 'conversor'
```

ou

```
ModuleNotFoundError: No module named 'conversor'
```

**Se o teste passou, algo está errado** — você não tem `conversor.py` ainda.
Um teste que passa antes de existir a implementação não está testando nada.

> **Por que escrever o teste à mão da primeira vez:** porque você precisa sentir a
> diferença. Daqui a duas semanas você vai deixar o agente escrever os testes
> também — e aí precisa saber reconhecer um teste que **finge** verificar. O teste
> falso mais comum gerado por IA é `assert resultado is not None`. Ele passa
> sempre e não prova nada.

---

## Passo 4 · Delegar

Agora chame o agente. Os comandos abaixo são para o Claude Code; a lógica é
idêntica em qualquer ferramenta do Bloco 4 do [03](03-instalacao.md).

```bash
claude
```

E, dentro da sessão, digite:

```
Leia ESPEC.md e test_conversor.py.

Implemente conversor.py de forma que todos os testes passem.

Regras:
- Não altere test_conversor.py.
- Não crie nenhum outro arquivo.
- Apenas biblioteca padrão.
- Rode `uv run --with pytest pytest -q` e não pare até passar tudo.
```

Repare no que esse pedido tem, item por item:

| Elemento | Função |
|---|---|
| "Leia X e Y" | Ancora o agente nos artefatos certos antes de agir |
| "Não altere o teste" | **A trava mais importante.** Sem ela, um agente encurralado às vezes ajusta o teste em vez do código |
| "Não crie outro arquivo" | Controla o raio de explosão |
| "Rode … e não pare até passar" | Fecha o laço: o agente ganha um sensor e se autocorrige |

**O que você vai ver:** o agente lê os arquivos, escreve `conversor.py`, roda o
pytest, provavelmente falha em um caso, lê o erro, corrige, roda de novo, passa.

Isso leva de 30 segundos a 3 minutos. **Assista.** Não faça outra coisa nesta
primeira vez — você está aprendendo a reconhecer o comportamento normal para
depois reconhecer o anormal.

---

## Passo 5 · Verificar (a parte que ninguém faz)

O agente disse que passou. Ótimo. **Confirme você mesmo**, num terminal
separado:

```bash
uv run --with pytest pytest -q
```

**Saída esperada:**

```
.......                                                       [100%]
7 passed in 0.02s
```

Agora as três perguntas que definem o ofício:

### Pergunta 1 — o teste ainda é o meu teste?

```bash
git diff --stat
git status --short
```

**Esperado:** `conversor.py` aparece como novo (`??`) e `test_conversor.py`
**não** aparece como modificado.

Se `test_conversor.py` foi modificado, você acabou de aprender a lição mais
importante do curso na prática: **o agente otimiza para o sinal que você deu.**
Você disse "faça os testes passarem". Mudar o teste faz os testes passarem.

### Pergunta 2 — o teste está medindo alguma coisa?

Sabote a implementação de propósito e veja se o teste percebe:

```bash
python3 - <<'EOF'
import re, pathlib
p = pathlib.Path("conversor.py")
src = p.read_text()
p.with_suffix(".py.bak").write_text(src)
# troca o primeiro 9/5 por 5/9 — inverte a fórmula
p.write_text(src.replace("9 / 5", "5 / 9", 1).replace("9/5", "5/9", 1))
EOF
uv run --with pytest pytest -q
```

**Esperado:** falha. Se passar, seus testes não cobrem o que você achava.

Restaure:

```bash
mv conversor.py.bak conversor.py
uv run --with pytest pytest -q
# esperado: 7 passed
```

> Isso se chama **teste de mutação**, e é o jeito mais rápido de descobrir se uma
> suíte de testes é decorativa. Vale ouro quando a suíte foi escrita por IA. Mais
> em [17-verificacao-e-testes](17-verificacao-e-testes.md).

### Pergunta 3 — eu entendo o que entrou?

```bash
cat conversor.py
```

Leia. São 20 linhas. Você consegue explicar cada uma?

Se sim, você está no controle. Se não, **pergunte ao agente** — mas pergunte
sobre o *porquê*, não sobre o *quê*:

```
Por que você escolheu passar por Kelvin como unidade intermediária em vez de
converter direto entre cada par?
```

A resposta a essa pergunta te ensina algo. "O que essa linha faz" não ensina.

---

## Passo 6 · Commitar com honestidade

```bash
git add -A
git commit -m "feat: conversor de temperatura C/F/K

Implementação gerada por agente a partir de ESPEC.md.
Testes escritos manualmente antes da implementação.
Verificado: 7/7 passando; teste de mutação confirma cobertura da fórmula."
```

**Por que registrar que foi gerado:** daqui a seis meses, quando alguém achar um
bug, saber que o código veio de agente muda a estratégia de investigação —
procura-se em lugares diferentes. Não é confissão de culpa; é metadado útil.
Trato da política de atribuição em [23-licenca-propriedade-e-lei](23-licenca-propriedade-e-lei.md).

---

## O ciclo do dia a dia

O que você acabou de fazer, generalizado:

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   1. ESPECIFICAR      O que é "certo"? Escrito, executável.  │
│         ↓                                                    │
│   2. INSTRUMENTAR     Como a máquina saberá que acertou?     │
│         ↓             (teste, tipo, linter, comando)         │
│   3. DELEGAR          Escopo estreito + travas explícitas    │
│         ↓                                                    │
│   4. VERIFICAR        Você roda. Não acredita no relato.     │
│         ↓                                                    │
│   5. REVISAR          Lê o diff com o método do arquivo 18   │
│         ↓                                                    │
│   6. INTEGRAR         Commit pequeno, mensagem honesta       │
│         ↓                                                    │
│   └──────► volta ao 1 com o próximo pedaço                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Onde está o tempo, na prática (minha estimativa de ofício):**

| Etapa | Fração do tempo | Antes da IA |
|---|---|---|
| 1. Especificar | 25% | 10% |
| 2. Instrumentar | 20% | 10% |
| 3. Delegar | 5% | 50% (era "escrever") |
| 4–5. Verificar e revisar | 40% | 20% |
| 6. Integrar | 10% | 10% |

A conclusão que a tabela grita: **o trabalho não sumiu, ele migrou para as
pontas.** Quem só automatizou a etapa 3 e manteve tudo o mais igual ganhou pouco
— e é exatamente esse o perfil que aparece nos estudos onde a IA não acelera
ninguém ([24](24-produtividade-o-que-diz-a-evidencia.md)).

---

## Os cinco primeiros erros de uso (não de instalação)

### Erro 1 — pedir grande demais

**Sintoma:** "implemente o sistema de autenticação" → 900 linhas, 12 arquivos,
nada testável, você desiste de revisar e aceita.

**Por quê:** a probabilidade de acerto cai com o tamanho da tarefa, e a sua
capacidade de revisar cai junto. As duas curvas descem ao mesmo tempo.

**Correção:** a regra do **diff revisável**. Se você não consegue revisar o
resultado em 10 minutos, a tarefa é grande demais. Fatie até caber.

### Erro 2 — não dizer o que **não** fazer

**Sintoma:** você pediu uma função e recebeu função + CLI + README + testes +
`Dockerfile` + refatoração de três arquivos vizinhos.

**Por quê:** o modelo foi treinado em código de projetos completos. Na ausência
de limite, ele reproduz o que viu: projetos completos.

**Correção:** "fora de escopo" explícito, como no `ESPEC.md`. E `git diff --stat`
antes de qualquer coisa, para ver o raio de explosão.

### Erro 3 — aceitar o relato em vez do resultado

**Sintoma:** "os testes passam" → você commita → o CI quebra.

**Por quê:** o agente pode ter rodado num diretório diferente, com um ambiente
diferente, ou ter interpretado uma saída ambígua com otimismo. Também pode
simplesmente estar errado: o relato final é texto gerado, não é a saída do
comando.

**Correção:** **rode você.** Sempre. É um comando. Não há desculpa.

### Erro 4 — a espiral do "não funciona"

**Sintoma:** você diz "não funciona", ele muda algo, você diz "ainda não
funciona", ele muda outra coisa. Vinte minutos depois o código está pior e
ninguém sabe por quê.

**Por quê:** "não funciona" carrega zero informação. O agente precisa chutar
qual das dez coisas possíveis você quis dizer, e cada chute errado polui o
contexto com mais lixo.

**Correção:** cole a **saída literal do erro**, com stack trace, e o comando
exato que você rodou. E se der duas rodadas sem progresso: **pare, desfaça**
(`git checkout .`), e recomece com contexto novo. Insistir num contexto
contaminado é jogar dinheiro fora — o modelo agora está condicionado pelas
tentativas anteriores erradas.

### Erro 5 — deixar a sessão crescer até o infinito

**Sintoma:** depois de uma hora, o agente esquece o que você disse no começo,
repete coisas já feitas, ou fica lento e caro.

**Por quê:** a **janela de contexto** é finita. Quando enche, a ferramenta
resume ou descarta o começo — e o que era instrução vira lembrança vaga.

**Correção:** uma sessão por tarefa. Terminou, commitou, **começa sessão nova**
(`/clear` no Claude Code). O que precisa sobreviver entre sessões vai para
arquivo: `AGENTS.md`, `ESPEC.md`, comentário no código. Mais em
[14-contexto-e-o-repositorio](14-contexto-e-o-repositorio.md).

---

## Bônus: dê ao repositório um `AGENTS.md`

Você acabou de repetir "use só a biblioteca padrão" e "rode o pytest com uv".
Isso é instrução permanente, não instrução de tarefa. Escreva no lugar certo:

```bash
cat > AGENTS.md <<'EOF'
# Instruções para agentes

## Comandos
- Rodar testes: `uv run --with pytest pytest -q`
- Formatar: `uv run --with ruff ruff format .`
- Verificar: `uv run --with ruff ruff check .`

## Regras deste repositório
- Apenas biblioteca padrão do Python. Nenhuma dependência nova sem eu aprovar.
- Nunca edite arquivos `test_*.py` para fazer um teste passar.
- Toda mudança de comportamento precisa de um teste que falharia sem ela.
- Comparação de float sempre com `math.isclose`, nunca `==`.

## Fora de escopo por padrão
CLI, empacotamento, CI, Docker — só se eu pedir explicitamente.
EOF
```

`AGENTS.md` é um **formato aberto**, adotado por mais de 60.000 projetos e
mantido pela Agentic AI Foundation (Linux Foundation) desde dezembro de 2025;
mais de 20 ferramentas o leem, entre elas Codex, Cursor, Copilot, Gemini CLI,
Aider, Zed, Jules e Devin. O Claude Code usa `CLAUDE.md` com a mesma função e
também lê `AGENTS.md`.

**Verificação de que funcionou:** comece uma sessão nova e peça algo que viole
uma regra — por exemplo, "adicione a biblioteca `requests` ao projeto". Um
agente que leu o arquivo vai questionar, não obedecer.

---

## Para onde ir agora

| Você quer | Vá para |
|---|---|
| Mais receitas prontas | [06-exemplos](06-exemplos.md) — 12 exemplos completos |
| Referência de comandos e opções | [05-manual-de-uso](05-manual-de-uso.md) |
| Um projeto inteiro, executável, que **é** a lição | [07-projeto-modelo](07-projeto-modelo/README.md) |
| Entender por que tudo isso funciona | [10-fundamentos](10-fundamentos.md) |

---

## Autoteste

1. Por que o `git init` vem antes de qualquer interação com o agente?
2. Por que escrevemos a especificação **antes** do código, e o que faz um
   critério de aceitação ser bom?
3. Por que o caso `-40 °C = -40 °F` sozinho não prova que a fórmula está certa?
4. Qual é a trava mais importante do pedido do Passo 4, e o que acontece sem ela?
5. O agente disse "7 testes passando". Quais são as três perguntas que você faz
   antes de acreditar?
6. O que é um teste de mutação e por que ele importa mais quando os testes foram
   escritos por IA?
7. Enuncie a regra do diff revisável.
8. Você disse "não funciona" duas vezes e o código piorou. O que fazer?
9. Por que uma sessão longa fica pior, e onde deve morar a informação que precisa
   sobreviver entre sessões?
10. Na tabela de distribuição de tempo, qual etapa encolheu e quais cresceram?
    Que conclusão prática isso traz?

---

**Anterior:** [03-instalacao](03-instalacao.md) ·
**Próximo:** [05-manual-de-uso](05-manual-de-uso.md)
