# 75 · Armadilhas, mitos e más práticas

> **Nível:** todos · **Atualizado em:** 13/08/2026 · Claude Code 2.1.231

28 erros. Para cada um: o que é, **por que persiste** (a parte que os outros materiais
omitem) e a correção.

---

## A · Erros conceituais

### 1. Achar que `CLAUDE.md` é configuração

**O erro:** escrever no `CLAUDE.md` uma regra crítica e supor que ela será cumprida.
**Por que persiste:** o arquivo parece configuração — nome de arquivo, sintaxe estruturada,
lugar fixo. Mas ele é entregue ao modelo como **mensagem de usuário** ([`12`](12-anatomia-de-uma-sessao.md)).
**Correção:** consequência grave → hook. Média → `CLAUDE.md`. É a escada de garantia do
[`25`](25-o-oficio-do-profissional.md).

### 2. Confundir fluência com correção

**O erro:** aceitar porque está bem escrito e confiante.
**Por que persiste:** em humanos, fluência correlaciona com competência. Em modelos, não —
a confiança da saída não carrega informação sobre a correção dela ([`10`](10-fundamentos.md)).
**Correção:** verificação automática. Sempre.

### 3. "Ele lembra do que conversamos"

**O erro:** dar instrução importante no chat e esperar que dure.
**Por que persiste:** a interface é uma conversa, e conversas humanas têm memória.
**Correção:** o que precisa durar vai para arquivo. Compactação apaga o resto ([`12`](12-anatomia-de-uma-sessao.md)).

### 4. Achar que contexto maior é melhor

**O erro:** despejar o projeto inteiro "para ele ter tudo".
**Por que persiste:** intuição de que mais informação nunca prejudica.
**Correção:** *lost in the middle* é fato medido ([`60`](60-teoria-avancada.md)). Curadoria vence tamanho.

### 5. Tratar o agente como oráculo de decisão

**O erro:** "qual banco devo usar?" e seguir a resposta.
**Por que persiste:** ele responde bem, com prós e contras plausíveis.
**Correção:** ele não conhece seu contexto, seu time, seu orçamento nem seus próximos três
anos. Use-o para **enumerar** alternativas; decida você.

### 6. Achar que ferramenta melhor compensa repositório ruim

**O erro:** trocar de agente porque "este não funciona no nosso código".
**Por que persiste:** é mais fácil trocar de ferramenta do que arrumar a suíte de testes.
**Correção:** a dispersão entre repositórios é maior que entre ferramentas ([`65`](65-estado-da-arte.md)).

### 7. "Prompt melhor resolve"

**O erro:** reescrever o pedido pela quinta vez.
**Por que persiste:** "engenharia de prompt" virou um gênero literário próprio.
**Correção:** depois da segunda tentativa, o problema é de **ambiente**: falta contexto,
falta oráculo, ou a tarefa não é adequada.

---

## B · Erros de uso

### 8. Não commitar antes de começar

**Por que persiste:** parece burocrático até o dia em que não é.
**Correção:** `git add -A && git commit -m "antes do claude"`. Trinta segundos.

### 9. Nunca usar `/clear`

**Por que persiste:** parece desperdício jogar fora contexto "que pode ser útil".
**Correção:** contexto velho custa **e** confunde. Assunto novo, contexto novo.

### 10. Deixar rodando sem olhar

**Por que persiste:** parece autonomia; parece que você está economizando tempo.
**Correção:** se errou no minuto 2, os 18 seguintes foram desperdício **e** contaminaram o
contexto ([`60`](60-teoria-avancada.md), correlação positiva de erros).

### 11. Aprovar diff sem ler

**Por que persiste:** cansaço; o diff é grande; "os testes passaram".
**Correção:** testes passando não é correção ([`60`](60-teoria-avancada.md)). Diffs pequenos
tornam a revisão viável — a causa raiz é o tamanho, não a preguiça.

### 12. Pedido vago

**Por que persiste:** é mais rápido de digitar, e às vezes funciona.
**Correção:** os quatro elementos do [`25`](25-o-oficio-do-profissional.md): objetivo,
critério de sucesso, restrição, formato de saída.

### 13. Não interromper

**Por que persiste:** parece grosseiro; parece que "vai que ele se acerta".
**Correção:** `Esc` é gratuito e a hesitação é cara.

### 14. Fazer o agente ler o log inteiro

**Por que persiste:** é o caminho de menor esforço para você.
**Correção:** `grep`/`tail` primeiro. Você conhece o formato do log; ele não.

### 15. Sessão única o dia inteiro

**Por que persiste:** o cache faz parecer barato, e é confortável.
**Correção:** cache reduz o custo por token, mas o contexto ainda cresce. Sessão por tarefa.

### 16. Delegar a leitura do código que você precisa entender

**Por que persiste:** o resumo é bom e economiza tempo hoje.
**Correção:** se você vai manter aquele código, leia você. Resumo perfeito não substitui ter
percorrido o caminho ([`25`](25-o-oficio-do-profissional.md), Pilar 4).

---

## C · Erros de configuração

### 17. `--dangerously-skip-permissions` na máquina de trabalho

**Por que persiste:** os prompts irritam, e a flag resolve na hora.
**Correção:** `/fewer-permission-prompts`, allowlist, `acceptEdits`, `/sandbox`. Se precisar
mesmo da flag: contêiner ([`24`](24-seguranca.md)).

### 18. `CLAUDE.md` de 800 linhas

**Por que persiste:** documentar parece sempre virtude.
**Correção:** custa em toda sessão **e** é seguido pior. Mire abaixo de 200 linhas; procedimento
vira skill, convenção vira regra com `paths:`.

### 19. Cinco servidores MCP conectados

**Por que persiste:** integração parece progresso, e cada servidor foi útil uma vez.
**Correção:** é o único custo **recorrente por mensagem**. `/context all` para medir; prefira
CLI onde existir ([`20`](20-mcp.md)).

### 20. Hook sem `chmod +x` ou sem shebang

**Por que persiste:** falha **em silêncio** — não há mensagem de erro na tela.
**Correção:** o validador do projeto-modelo (`npm run verificar`) pega isso em um segundo.

### 21. `exit 1` esperando bloqueio

**Por que persiste:** a convenção Unix diz que 1 é falha.
**Correção:** só o **2** bloqueia por código. Ou devolva JSON de decisão ([`17`](17-hooks.md)).

### 22. Hook lento em `PostToolUse`

**Por que persiste:** funcionou bem quando a suíte tinha 20 testes.
**Correção:** filtre por arquivo, use `async`, ou troque por verificação mais rápida
(`tsc --noEmit`, lint).

### 23. Configurar tudo antes de usar

**Por que persiste:** preparação parece responsabilidade.
**Correção:** configuração especulativa envelhece mal e ninguém do time lembra por que
existe. Acrescente quando a dor aparecer.

### 24. Não versionar a configuração

**Por que persiste:** "é só a minha configuração".
**Correção:** `.claude/settings.json`, `agents/`, `skills/`, `rules/` e `CLAUDE.md` vão para
o git. `settings.local.json` e `CLAUDE.local.md` ficam de fora.

---

## D · Erros em escala

### 25. Medir por linhas aceitas

**Por que persiste:** é a métrica mais fácil de coletar e sobe sozinha.
**Correção:** meça tempo de ciclo de PR, taxa de reversão e custo por dev ([`26`](26-times-e-escala.md)).

### 26. Adotar sem arrumar o repositório

**Por que persiste:** adotar ferramenta é projeto visível; arrumar testes não é.
**Correção:** são o mesmo projeto. Piloto em repositórios que já têm testes.

### 27. Merge automático de PR de agente

**Por que persiste:** parece o próximo passo natural da automação.
**Correção:** revisão é o gargalo, não a geração. Automatizar merge é automatizar o gargalo
errado — e é o único erro desta lista que pode ir direto para produção.

### 28. Agente em CI sem teto de gasto

**Por que persiste:** funcionou nos primeiros dez PRs.
**Correção:** `--max-budget-usd` e `--max-turns`, **sempre**. Um laço patológico num runner é
uma fatura silenciosa.

---

## Mitos

| Mito | Realidade |
|---|---|
| "Substitui programadores" | Move o trabalho para especificar, verificar e decidir. Versão 2026 de uma frase dita sobre COBOL, CASE tools e programação visual ([`11`](11-historia.md)) |
| "Escreve código melhor que humano" | Escreve código **mais rápido**. Melhor depende de existir critério — e de alguém o ter definido |
| "Com contexto de 1 M você joga o projeto inteiro" | Caber não é entender ([`60`](60-teoria-avancada.md)) |
| "Só serve para código simples" | Falso pelo outro lado. Ele é forte em trabalho mecânico **em escala**, que costuma ser complexo, e fraco onde não há critério |
| "Precisa de máquina potente" | O modelo roda no servidor. Sua máquina roda testes |
| "É só usar um prompt melhor" | Depois da segunda tentativa, o problema é o ambiente |
| "Prompt secreto de mil linhas resolve tudo" | Prompt gigante consome contexto e reduz aderência. O oposto do que promete |
| "Se os testes passam, está certo" | Dijkstra, 1970: testes mostram presença, nunca ausência de bugs |
| "Um dia não vamos precisar revisar" | Rice, 1953: correção é indecidível em geral. Não é limitação de modelo |

---

## O diagnóstico em uma tabela

Quando algo dá errado, comece por aqui:

| Sintoma | Causa mais provável | Primeiro movimento |
|---|---|---|
| Ignora minha regra | Regra vaga, ou camada errada | `/context`; se carregou, vire hook |
| Esqueceu o que eu disse | Compactação | Escreva no `CLAUDE.md` |
| Lento e caro | Contexto inflado | `/context all` |
| Configuração não pega | JSON inválido, escopo errado | `claude doctor`, `/status` |
| Hook não roda | `chmod`, shebang, matcher | `npm run verificar` do projeto-modelo |
| Resultado genérico | Falta contexto ou oráculo | Dê o dado; defina o critério |
| Quebra a suíte e não percebe | Falta hook `PostToolUse` | [`17`](17-hooks.md) |
| Muda coisa que não pedi | Escopo largo demais | Modo plano; peça um arquivo por vez |
| Subagente inútil | Prompt de delegação subespecificado | Ele não herda seu contexto ([`19`](19-subagentes.md)) |

---

## Autoteste

1. Qual é o erro conceitual nº 1, e qual a correção estrutural?
2. Por que fluência não indica correção, e o que fazer a respeito?
3. Por que "prompt melhor" para de funcionar depois da segunda tentativa?
4. Por que hook sem `chmod +x` é tão comum? Como pegar isso em um segundo?
5. Qual código de saída bloqueia num hook, e por que a intuição Unix engana?
6. Qual dos 28 erros pode ir direto para produção? Por que ele parece razoável?
7. Desmonte três dos mitos com um argumento cada.
8. Você delegou a leitura de um módulo que vai manter. Que erro foi esse, e por que ele é tentador?
