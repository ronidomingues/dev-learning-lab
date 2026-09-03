# 75 · Armadilhas, mitos e más práticas

**Nível:** todos · Atualizado em 13/08/2026

Trinta armadilhas, agrupadas. Para cada uma: o que é, por que persiste e a
correção.

---

## A. Erros de uso

### A1. Pedido vago e a culpa transferida
"Melhore esse código." O agente adivinha, refatora o que você não queria, e a
conclusão vira "a IA não presta". **Correção:** todo pedido deve permitir
responder "como eu saberia que deu certo?".

### A2. Não dar contra o que verificar
Sem teste, sem comando, sem saída esperada, o agente não fecha o laço.
**Correção:** dê o critério junto com o pedido.

### A3. Uma sessão, cinco assuntos
Contexto acumulado de uma tarefa atrapalha a próxima. Sintomas: esquece,
repete, ignora regras. **Correção:** `/clear` ao trocar de assunto.

### A4. Aprovar sem ler
`Yes, don't ask again` para `Bash` genérico é onde os acidentes moram.
**Correção:** allowlist específica, `/fewer-permission-prompts`.

### A5. Achar que ele lembra de ontem
Cada sessão começa do zero. **Correção:** `CLAUDE.md` para o que persiste,
`/resume` para retomar de fato.

### A6. Não commitar antes
Sem commit, revisar é difícil e desfazer é pior. **Correção:** commit limpo
antes, `git diff` depois.

### A7. Deixar rodar sem olhar
Se ele pegou o caminho errado na terceira ação, esperar até a trigésima
desperdiça tempo e dinheiro. **Correção:** `Esc` interrompe; digitar uma
correção redireciona sem parar.

### A8. Pedir tarefa grande de uma vez
`n` grande sem verificação no meio → composição de erro
([60 §2](60-teoria-avancada.md#2-composição-de-erro)). **Correção:** fatie,
verifique entre as fatias.

---

## B. Erros de configuração

### B9. `CLAUDE.md` inchado
Documentação que o agente descobriria lendo o código, paga em toda sessão.
**Correção:** `/doctor`; a pergunta é "ele descobriria isso sozinho?".

### B10. Regra crítica só na conversa
Ela morre na compactação. **Correção:** `CLAUDE.md` (se depende de julgamento)
ou hook (se precisa valer sempre).

### B11. Instrução onde deveria haver hook
"Sempre rode o lint" é uma sugestão. **Correção:** `PostToolUse`.

### B12. Vinte servidores MCP conectados
Contexto e latência pagos em toda sessão por ferramentas que você usa uma vez
por mês. **Correção:** `/context`, `/mcp disable`, tool search.

### B13. `--dangerously-skip-permissions` como hábito
O nome é literal. **Correção:** allowlist específica; bypass só em contêiner
descartável.

### B14. Skill que é roteiro passo a passo para tarefa de julgamento
Modelos atuais seguem o roteiro em vez de resolver o problema, e o resultado
piora. **Correção:** prescreva onde a ordem é frágil; descreva objetivo e
restrições onde há espaço de solução.

### B15. Duas instalações do Claude Code
Configuração editada não "pega". **Correção:** `which -a claude`,
`claude doctor`.

---

## C. Erros de construção de agente

### C16. Guardar só o texto da resposta
`tool_use_id` órfão; o turno seguinte quebra.
**Correção:** `content` inteiro.

### C17. Resultados em mensagens separadas
Não dá erro. Ensina o modelo a não paralelizar. **Correção:** todos numa
mensagem de usuário.

### C18. Exceção em vez de `is_error`
O agente morre na primeira ferramenta que falha. **Correção:** erro vira
conteúdo, com `is_error: true`.

### C19. Mensagem de erro genérica
`"Erro: inválido"` produz a mesma tentativa de novo. **Correção:** diga como
corrigir.

### C20. Sem limite de voltas, sem orçamento, sem timeout
Ciclo silencioso queimando créditos, ou processo travado. **Correção:** as
quatro travas do [12 §7](12-anatomia-do-loop-agentico.md#7-condições-de-parada--e-todas-as-que-faltam).

### C21. Ler `content[0]` sem checar `stop_reason`
`IndexError` na primeira recusa, em produção. **Correção:** cheque antes.

### C22. Timestamp no prompt de sistema
Cache sempre frio; custo triplica sem qualquer erro visível.
**Correção:** estável primeiro, volátil depois; verifique
`cache_read_input_tokens`.

### C23. Descrição de ferramenta de uma linha
Ferramenta ignorada ou usada errado. **Correção:** 3–4 frases, com gatilho e
com o "quando não usar".

### C24. Ferramenta que devolve um despejo gigante
Cinco chamadas e o contexto acabou. **Correção:** resuma, ofereça caminho para
o detalhe.

---

## D. Mitos

### M1. "Agentes vão substituir programadores"
Alguém precisa decidir o que construir, julgar o resultado e responder pelo
incidente. O que mudou foi a proporção do trabalho, não a existência dele.
**Por que persiste:** vende bem, e demos são impressionantes.

### M2. "Basta o prompt certo"
Ferramentas, contexto e verificação decidem mais que redação de prompt.
**Por que persiste:** prompt é a única alavanca visível para quem só usa o
chat.

### M3. "Mais agentes, melhor"
Multiagente só ganha por **isolamento de contexto** e **independência de
julgamento**. Sem uma das duas, é pipeline caro.
**Por que persiste:** parece sofisticado e é fácil de demonstrar.

### M4. "Contexto de 1 milhão resolve a memória"
*Lost in the middle* + custo quadrático. Cabe ≠ é usado bem.
**Por que persiste:** o número é grande e concreto.

### M5. "88% no benchmark = 88% no meu repositório"
Arnês diferente, base diferente, contaminação, e uma fração das soluções
"corretas" passa por motivo errado.
**Por que persiste:** número único é fácil de comunicar.

### M6. "É determinístico se eu puser temperatura 0"
Nunca foi totalmente; e nos modelos atuais os parâmetros de amostragem foram
removidos. **Por que persiste:** hábito de APIs antigas.

### M7. "Autônomo quer dizer sem humano"
Na prática, quer dizer "humano em pontos escolhidos". A pergunta certa é
*onde*. **Por que persiste:** "autônomo" é palavra de marketing.

### M8. "Modelo maior resolve"
Frequentemente `effort` mais alto, uma ferramenta melhor ou um sinal de
verificação rendem mais — e custam menos.
**Por que persiste:** trocar o nome do modelo é a mudança mais fácil de fazer.

### M9. "IA vai verificar se o código está correto"
Teorema de Rice: não existe verificador geral. Existe verificação parcial.
**Por que persiste:** confunde-se "encontra muitos bugs" com "prova ausência
de bugs".

---

## E. Más práticas de segurança

### S25. Tratar entrada de terceiro como confiável
Issue, PR, página web, retorno de MCP: tudo pode conter instrução hostil.
**Correção:** privilégio mínimo, sem rede de saída, humano para o
irreversível.

### S26. Defender injeção só com instrução no prompt
É o mesmo canal que o atacante usa. **Correção:** limite o **estrago** —
capacidade, não persuasão.

### S27. Segredo legível pelo agente
Entrou no contexto, foi para a API e ficou no transcrito local.
**Correção:** `deny` de leitura.

### S28. Servidor MCP de terceiro sem auditoria
Código que roda na sua máquina e escreve no seu prompt, e que pode mudar
depois da instalação. **Correção:** leia, fixe a versão, escopo mínimo de
credencial.

### S29. Credencial ampla em agente autônomo
Token de admin num agente de CI amplia qualquer falha ao máximo.
**Correção:** menor privilégio, curta duração, escopo restrito.

### S30. Deixar transcritos numa máquina compartilhada
`~/.claude/projects/` guarda a conversa inteira em texto claro.
**Correção:** `claude project purge`, e política de retenção.

---

## Os cinco erros que mais custam, se você só lembrar de cinco

1. **Não dar contra o que verificar** (A2) — o laço não fecha.
2. **Regra crítica só na conversa** (B10) — some na compactação.
3. **Sem limite de voltas e de orçamento** (C20) — a conta.
4. **Entrada de terceiro tratada como confiável** (S25) — o incidente.
5. **Acreditar em benchmark público** (M5) — a decisão errada de adoção.

---

## Autoteste

1. Você pediu "melhore esse código" e o resultado veio ruim. De quem é o erro,
   e qual é a correção mecânica?
2. Uma regra dada no minuto 3 foi ignorada no minuto 90. Por quê, e onde ela
   deveria estar?
3. Devolver `tool_result` em mensagens separadas dá erro? O que acontece?
4. Por que M4 ("1 milhão resolve a memória") é falso? Cite os dois mecanismos.
5. Por que S26 (defender injeção pelo prompt) é fraco?
6. Qual mito você acreditava antes deste curso?
7. Dos cinco erros mais caros, qual é o mais provável na sua situação hoje, e
   o que você vai mudar?
