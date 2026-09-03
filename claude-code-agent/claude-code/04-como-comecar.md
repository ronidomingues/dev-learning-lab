# 04 · Como começar — do ambiente pronto ao primeiro resultado

> **Nível:** iniciante · **Atualizado em:** 13/08/2026 · Claude Code 2.1.231
> Assume o ambiente já instalado pelo [`03-instalacao.md`](03-instalacao.md). **Não repita a instalação aqui.**

Meta deste arquivo: em 20 minutos você terá feito o agente ler, planejar, editar e
verificar código — e saberá interromper e desfazer quando ele errar.

---

## Passo 0 · A rede de segurança (30 segundos, não pule)

Antes de deixar qualquer agente editar seus arquivos:

```bash
cd /caminho/do/seu/projeto
git status
```

Se aparecer `not a git repository`, ou se houver mudanças não commitadas:

```bash
git init                                   # só se ainda não for um repositório
git add -A && git commit -m "antes do claude"
```
> Este commit é o seu botão de desfazer definitivo. O `/rewind` do Claude Code cobre a
> sessão; o git cobre tudo. Quem pula este passo aprende do jeito caro.

---

## Passo 1 · Abrir

```bash
claude
```

Você verá a caixa de entrada e, na barra inferior, o modelo ativo e o modo de permissão.
Na primeira vez num diretório, aparece o **diálogo de confiança** perguntando se você
confia naquela pasta — ele existe porque um repositório pode trazer hooks e configurações
que executam código. Confirme só em repositórios que você conhece.

Três teclas que valem o dobro de qualquer prompt:

| Tecla | Efeito |
|---|---|
| `Esc` | **Interrompe o Claude no meio.** A tecla mais importante da ferramenta |
| `Esc` `Esc` | Volta a conversa **e o código** a um ponto anterior (`/rewind`) |
| `Shift+Tab` | Alterna o modo de permissão (padrão → aceitar edições → plano → …) |

---

## Passo 2 · Primeira pergunta (leitura, zero risco)

Digite:

```
o que este projeto faz? responda em 5 linhas
```

O Claude lê alguns arquivos e responde. Repare no que apareceu na tela: linhas de
`Read(...)`, talvez `Glob(...)` ou `Grep(...)`. **São as ferramentas sendo usadas** —
é o laço agêntico funcionando à sua frente ([`10`](10-fundamentos.md)).

Leitura dentro do diretório de trabalho não pede permissão; é seguro por construção.

**Verificação de que deu certo:** a resposta menciona arquivos e conceitos que realmente
existem no seu projeto. Se ela for genérica ("é um projeto JavaScript moderno..."), o
Claude não achou nada relevante — provavelmente você abriu na pasta errada. Confira com
`/status`.

---

## Passo 3 · Deixe ele planejar antes de agir

Agora peça algo que muda código, **mas em modo plano**. Pressione `Shift+Tab` até a barra
mostrar `plan mode`, ou simplesmente:

```
/plan adicionar um teste para o caso em que a entrada está vazia
```

Em modo plano o Claude **só lê**. Ele explora, entende e apresenta um plano para você
aprovar. Nada é escrito antes do seu "sim".

Por que isto importa mais do que parece: o erro caro de um agente quase nunca é digitar
errado — é **entender errado o pedido** e executar quinze passos na direção errada. O modo
plano transforma quinze passos errados em um parágrafo errado, que você corrige em dez
segundos. Este é o hábito que mais separa quem se dá bem de quem reclama da ferramenta.

Leia o plano. Se estiver bom, aprove. Se não, escreva o que está errado — ele replaneja.

---

## Passo 4 · A primeira edição

Aprove o plano. Agora o Claude pede permissão para editar:

```
Edit  test/exemplo.test.js
  ❯ 1. Sim
    2. Sim, e não pergunte mais para este arquivo
    3. Não, e diga o que fazer em vez disso
```

**Escolha 1 nas primeiras vezes.** A opção 2 é conveniência que você compra depois de
confiar. A opção 3 é a mais subestimada: em vez de recusar e recomeçar, você corrige o
rumo ali mesmo, sem perder o contexto já construído.

---

## Passo 5 · Feche o laço — faça-o verificar

Este é o passo que a maioria pula, e é o que separa "gerar código" de "resolver problema":

```
rode os testes e conserte o que falhar
```

O Claude pede permissão para rodar o comando, executa, **lê a saída** e, se houver falha,
edita e roda de novo. Você acabou de ver o laço agêntico fechado: agir → observar → corrigir.

> **A regra de ouro deste curso:** *toda tarefa que você der a um agente deve ter um jeito
> automático de saber se está certa.* Teste, compilador, linter, `curl` que devolve 200.
> Sem isso, você não está delegando trabalho — está delegando a **ilusão** de trabalho, e
> a checagem sobra para você.

---

## Passo 6 · Escreva a memória do projeto

Ainda na sessão:

```
/init
```

O Claude analisa o repositório e propõe um `CLAUDE.md`: comandos de build e teste,
convenções, estrutura. Esse arquivo é lido no início de **toda** sessão futura.

Revise o que ele escreveu e corte tudo que o agente pode descobrir sozinho lendo o código.
O que deve ficar são as coisas que **não** estão no código: por que a arquitetura é assim,
qual biblioteca está proibida e por quê, qual comando roda a suíte rápida. Mire abaixo de
200 linhas — acima disso o custo sobe e a aderência cai ([`13`](13-contexto-e-memoria.md)).

---

## O ciclo de trabalho do dia a dia

```mermaid
flowchart LR
    A[Abrir na pasta certa<br/>claude] --> B[Descrever a tarefa<br/>com critério de sucesso]
    B --> C{Tarefa não trivial?}
    C -->|Sim| D[Shift+Tab → plano]
    C -->|Não| E[Deixar agir]
    D --> F[Ler o plano<br/>corrigir o rumo]
    F --> E
    E --> G{Está indo errado?}
    G -->|Sim| H[Esc<br/>e explicar o desvio]
    H --> B
    G -->|Não| I[Deixar verificar<br/>testes/lint/build]
    I --> J[Revisar o diff<br/>/diff ou git diff]
    J --> K{Tarefa nova<br/>e diferente?}
    K -->|Sim| L[/clear e recomeçar]
    K -->|Não| B
    L --> A
```

Quatro hábitos que compõem esse ciclo:

1. **Abra na raiz certa.** O Claude só escreve na pasta onde foi aberto e abaixo dela.
   Abrir na raiz do monorepo quando você mexe num pacote é convite a distração.
2. **Um assunto por sessão.** Ao trocar de tarefa, `/clear`. Contexto velho não só custa
   tokens: ele **atrapalha**, porque o modelo continua vendo arquivos irrelevantes.
3. **Interrompa cedo.** `Esc` na primeira frase que soar errada. É mais barato do que
   deixar terminar e refazer.
4. **Revise o diff, sempre.** `/diff` ou `git diff`. Aprovar sem ler é onde os problemas
   entram — e você é o responsável pelo que fica no repositório.

---

## Sem terminal interativo: o modo `-p`

O mesmo agente roda em uma linha, o que o torna peça de script e de CI ([`23`](23-headless-e-sdk.md)):

```bash
claude -p "responda apenas com a palavra: pronto"
```

Saída **real** desta máquina em 13/08/2026:

```
pronto
```

Com metadados estruturados:

```bash
claude -p "Quantos blocos test( ) existem em test/tarefas.test.js? Responda so o numero." \
  --allowedTools "Read,Bash(grep *)" --output-format json
```

Trecho **real** da resposta (executado no projeto-modelo, 13/08/2026):

```json
{
  "is_error": false,
  "duration_api_ms": 4411,
  "num_turns": 2,
  "session_id": "84a5e3a3-ca87-4178-a64c-414d8def8b6c",
  "total_cost_usd": 0.1906005,
  "usage": {
    "input_tokens": 4,
    "cache_creation_input_tokens": 16300,
    "cache_read_input_tokens": 47811,
    "output_tokens": 147
  },
  "modelUsage": { "claude-opus-5[1m]": { "contextWindow": 1000000, "costUSD": 0.1906005 } }
}
```

Três lições nesse JSON, e vale parar nelas:

- **`cache_read_input_tokens: 47811` contra `input_tokens: 4`.** Quase todo o contexto veio
  do cache, muito mais barato que tokens novos. É por isso que sessões longas e contínuas
  custam menos do que muitas sessões curtas recomeçadas ([`80`](80-custos-e-licencas.md)).
- **`total_cost_usd: 0,19` para contar testes num arquivo.** Uma pergunta trivial custou
  19 centavos porque arrastou ~64 mil tokens de contexto. Contexto é dinheiro.
- **`num_turns: 2`.** Duas idas ao modelo: uma para decidir usar a ferramenta, outra para
  responder. É o laço agêntico, contabilizado.

---

## Os cinco erros de estreante (de uso, não de instalação)

**1. Pedir vago e culpar a resposta.**
"melhore este código" produz mudança aleatória, porque não existe critério de "melhor".
Troque por: *"reduza a duplicação entre `a.js` e `b.js` extraindo uma função comum; os
testes devem continuar passando"*. Pedido verificável, resultado verificável.

**2. Deixar rodar sozinho por vinte minutos e só então olhar.**
Se o rumo estava errado no minuto 2, você desperdiçou 18 e ainda precisa desfazer.
`Esc` cedo. Não existe prêmio por não interromper.

**3. Nunca usar `/clear`.**
A sessão vira um depósito: arquivos de três tarefas atrás continuam no contexto,
confundindo o modelo e inflando a conta. Tarefa nova, contexto novo.

**4. Escrever regra importante no chat, e não no `CLAUDE.md`.**
"não use a biblioteca X" dito na conversa vale para aquela sessão e some. No `CLAUDE.md`,
vale para todas. E se a regra precisa **ser garantida**, ela nem é texto: é hook ([`17`](17-hooks.md)).

**5. Ligar `--dangerously-skip-permissions` no segundo dia.**
Todo mundo cansa dos prompts de permissão. A saída certa **não** é desligar o freio: é
`/permissions` para liberar o que é seguro (`Bash(npm test)`, `Bash(git diff *)`), ou
`/fewer-permission-prompts`, que analisa seu histórico e propõe a lista. Ver [`15`](15-permissoes-e-modos.md).

---

## Quando algo dá errado

| Sintoma | Primeiro movimento |
|---|---|
| Foi para a direção errada | `Esc`, explique o desvio em uma frase, siga |
| Editou o que não devia | `Esc` `Esc` (rewind) ou `git checkout -- <arquivo>` |
| Está lento e caro | `/context` — veja o que ocupa espaço; provavelmente é hora de `/clear` |
| "Não segue meu CLAUDE.md" | `/context` mostra se ele foi carregado. Se sim, o texto está vago — ou você precisa de hook |
| Erro estranho de ferramenta | `/doctor`, depois `claude --debug` |
| Não sei o que ele fez | `/diff`, `git diff`, `git status` |

---

## Para onde ir agora

- **Referência de tudo que dá para digitar** → [`05-manual-de-uso.md`](05-manual-de-uso.md)
- **14 receitas prontas** → [`06-exemplos.md`](06-exemplos.md)
- **Um repositório inteiro configurado como deve ser** → [`07-projeto-modelo/`](07-projeto-modelo/README.md)
- **Entender o que está acontecendo por baixo** → [`10-fundamentos.md`](10-fundamentos.md)

---

## Autoteste

1. Qual é o passo 0, e por que ele vem antes de qualquer coisa?
2. O que o modo plano evita, concretamente? Por que ele é barato?
3. Qual é "a regra de ouro" deste curso sobre delegar tarefas?
4. No JSON do `-p`, por que `cache_read_input_tokens` ser muito maior que `input_tokens` é uma boa notícia?
5. Qual tecla é a mais importante da ferramenta, e por quê?
6. Por que "não use a biblioteca X" no chat é pior do que no `CLAUDE.md`? E quando nem o `CLAUDE.md` basta?
7. Você cansou dos prompts de permissão. Quais são as duas saídas certas e qual é a errada?
