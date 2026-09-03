# 16 · Especificação e plano — a habilidade que subiu de preço

**Nível:** intermediário · **Escrito em:** 20/08/2026

---

## Por que este arquivo existe

Se a geração de código virou barata, a **definição do que deve ser gerado**
virou o item caro. Especificar sempre foi habilidade de engenharia; a diferença
é que antes ela era diluída ao longo da implementação — você descobria o que
queria enquanto escrevia.

Com um agente, você não escreve. Então ou você descobre **antes**, ou descobre
**depois**, olhando 400 linhas que resolvem o problema errado.

---

## 1 · O que é uma especificação boa

**Definição operacional:**

> Uma especificação é boa quando duas pessoas competentes, lendo-a
> separadamente, produzem implementações **funcionalmente equivalentes** — e
> quando ambas conseguem decidir, sem consultar ninguém, se uma dada
> implementação satisfaz ou não.

Repare que a definição não fala em detalhe nem em tamanho. Fala em
**convergência** e **decidibilidade**.

### Os cinco componentes

| Componente | Pergunta que responde | Erro se faltar |
|---|---|---|
| **Objetivo** | Que problema isto resolve? | Resolve o problema errado |
| **Critérios de aceitação** | Como sei que está pronto? | Ninguém sabe se acabou |
| **Restrições** | O que não pode? | Solução inviável ou dependência indesejada |
| **Fora de escopo** | O que explicitamente não é? | Escopo explode |
| **Contexto** | O que já existe e como se encaixa? | Reinventa o que já tem |

---

## 2 · Critério de aceitação: o coração

Um critério de aceitação é bom quando é **decidível por alguém que não
participou da conversa**.

| Ruim | Bom |
|---|---|
| "a busca deve ser rápida" | "p95 da busca < 300 ms com 100 mil registros" |
| "tratar erros adequadamente" | "CEP inválido → HTTP 422 com `{erro: 'cep_invalido'}`" |
| "código limpo" | *(não é critério de aceitação; é padrão de projeto — vai para o `AGENTS.md`)* |
| "compatível com o legado" | "o `GET /v1/pedidos` devolve o mesmo JSON de hoje, campo a campo" |
| "seguro" | "sem o cabeçalho `Authorization`, todo endpoint devolve 401" |

### O teste dos três dedos

Para cada critério, pergunte:

1. **É observável?** Consigo apontar para algo — saída, código HTTP, tempo,
   arquivo?
2. **É decidível?** Duas pessoas chegam ao mesmo veredito?
3. **É executável?** Consigo escrever um teste que o verifica?

Se as três respostas forem "sim", o critério vira teste automaticamente — e aí
você atravessou a ponte entre especificar e verificar, que é a tese do curso.

Se a terceira for "não", ainda pode ser um critério válido (ex.: "a interface
segue o guia de marca"), mas ele exigirá julgamento humano toda vez. **Minimize
esses.**

### Numere os critérios

```markdown
- **CA-01** Pedido sem itens devolve 422 com `{erro: "pedido_vazio"}`.
- **CA-02** Frete para CEP da lista de exceção usa a tabela local.
- **CA-03** Falha na API dos Correios devolve o último valor em cache (TTL 6 h).
- **CA-04** Cache vazio + API fora → 503, sem valor inventado.
```

Numerar não é burocracia. Permite:

- o agente citar o critério que está implementando;
- o teste citar o critério que cobre;
- **um portão automático verificar que todo critério tem teste** — exatamente a
  regra `criterios` do [projeto-modelo](07-projeto-modelo/README.md).

O CA-04 acima é o tipo de critério que só aparece se você **pensar em falha**.
Modelo, deixado sozinho, escreve o caminho feliz.

---

## 3 · Escrevendo especificação **com** a IA

O uso mais rentável do agente aqui não é escrever a especificação — é
**atacá-la**.

### Passo 1 — rascunho seu

Escreva mal, rápido, à mão. Cinco linhas bastam.

### Passo 2 — entrevista

```
Isto é um rascunho de especificação. NÃO implemente e NÃO reescreva.

Faça o papel de analista cético:
1. Que ambiguidades existem? Para cada uma, as interpretações possíveis.
2. Que casos de borda não estão tratados?
3. Que caminhos de erro faltam?
4. Que suposições sobre o sistema atual eu estou fazendo sem dizer?
5. Que decisão desta especificação seria cara de reverter depois?

<rascunho>
```

### Passo 3 — decida você

Ele lista; **você escolhe**. Isso é irredutível: a escolha depende de objetivos
que não estão no repositório.

### Passo 4 — critérios executáveis

```
Transforme as decisões acima em critérios de aceitação numerados (CA-01, ...).
Cada um deve ser observável e verificável por um teste automatizado.
Se algum não puder ser, marque com [manual] e explique por quê.
```

### Passo 5 — teste antes de implementar

```
Escreva os testes para CA-01 a CA-07. Só os testes.
Cada teste cita no nome ou em comentário o CA que cobre.
Eles devem FALHAR agora — a implementação não existe.
Rode e me mostre as falhas.
```

**Agora sim** você delega a implementação. E delega com uma rede embaixo.

---

## 4 · *Spec-driven development* (SDD)

Em 2026, o método formalizou-se. A tese: **a especificação é o artefato
primário; o código é uma saída regenerável.**

### Ferramentas

| Ferramenta | Origem | Característica |
|---|---|---|
| **GitHub Spec Kit** | GitHub, código aberto | CLI + templates; fluxo especificar → planejar → tarefas → implementar; suporta ~29 integrações (Claude Code, Copilot, Cursor, Codex, Gemini CLI, Windsurf, Kiro CLI, goose, Roo Code…) |
| **AWS Kiro** | AWS | IDE onde a especificação é objeto de primeira classe; usa notação **EARS**, vinda de requisitos aeroespaciais |
| **OpenSpec, BMAD, Tessl** | comunidade / *startups* | Variações do mesmo fluxo |

### EARS em 60 segundos

*Easy Approach to Requirements Syntax* — cinco moldes que eliminam ambiguidade:

| Molde | Forma | Exemplo |
|---|---|---|
| Ubíquo | O sistema **deve** \<resposta\> | O sistema deve registrar toda tentativa de login. |
| Dirigido por evento | **Quando** \<gatilho\>, o sistema deve \<resposta\> | Quando o pagamento for aprovado, o sistema deve emitir a nota. |
| Dirigido por estado | **Enquanto** \<estado\>, o sistema deve \<resposta\> | Enquanto o pedido estiver em análise, o sistema deve bloquear a edição. |
| Indesejado | **Se** \<condição\>, **então** o sistema deve \<resposta\> | Se o CEP for inválido, então o sistema deve devolver 422. |
| Opcional | **Onde** \<funcionalidade\>, o sistema deve \<resposta\> | Onde a integração fiscal estiver ativa, o sistema deve enviar o XML. |

Parece rígido e é **exatamente por isso que funciona**: "Quando/Se/Enquanto"
força você a nomear o gatilho, e nomear o gatilho é onde a ambiguidade morre.

Você não precisa de ferramenta para usar EARS. Precisa de disciplina.

### A crítica honesta ao SDD

Já dei a versão longa no [11-historia](11-historia.md). Resumindo:

**A favor:** ataca a causa raiz certa (deriva de intenção). Relatos de adotantes
iniciais mencionam taxas de acerto de primeira muito maiores em tarefas não
triviais — números de fornecedor, trate com ceticismo, mas a direção é
plausível.

**Contra:** é a terceira tentativa histórica da mesma ideia (síntese formal nos
anos 70, MDA nos 90). As duas anteriores morreram do mesmo mal: **divergência
entre especificação e código depois da primeira edição manual**. Ninguém
resolveu isso ainda.

**Minha recomendação, marcada como opinião:** adote a **prática** (especificar
antes, critérios numerados, testes derivados dos critérios) sem se casar com a
**ferramenta**. A prática é gratuita, portátil e não expira. A ferramenta pode
não existir em dois anos.

---

## 5 · Plano: o degrau entre especificação e código

Especificação diz **o quê**. Plano diz **como e em que ordem**.

### O pedido padrão

```
Modo de planejamento. NÃO altere nenhum arquivo.

Com base em ESPEC.md, produza um plano:

1. Arquivos a criar ou alterar, com o motivo de cada um.
2. Ordem de execução, com a dependência entre os passos.
3. Para cada passo, como verificar que ele funcionou.
4. Riscos: o que pode quebrar, o que é incerto.
5. O que você faria diferente da especificação, e por quê.

Grave em PLANO.md e pare.
```

O item 5 é o que mais rende. É onde ele aponta que o CA-03 é impossível como
está escrito, ou que já existe algo parecido em outro módulo.

### Como avaliar um plano em 3 minutos

| Pergunta | Sinal de alarme |
|---|---|
| Os arquivos listados fazem sentido? | Aparece arquivo que você não esperava |
| A ordem respeita as dependências? | Passo 2 usa o que o passo 5 cria |
| Cada passo tem verificação? | "verificar manualmente" em tudo |
| Os riscos são específicos? | "pode haver problemas de performance" |
| Ele discorda de algo? | Concordância total é sinal de leitura rasa |

**Corrigir plano custa 30 segundos. Corrigir código custa meia hora.** Essa
razão — cerca de 60 para 1 — é a melhor relação custo-benefício disponível em
todo o fluxo de trabalho com agentes.

---

## 6 · Tamanho da fatia

Regra prática, calibrada por experiência:

> **Uma tarefa delegável deve caber num diff que você revisa em 10 minutos.**

Na prática: 50 a 300 linhas, 1 a 5 arquivos.

| Tamanho | Prognóstico |
|---|---|
| < 50 linhas | Provavelmente não valia delegar; você faria mais rápido |
| 50–300 linhas | **Ponto ótimo** |
| 300–800 linhas | Só com testes fortes cobrindo a área |
| > 800 linhas | Fatie. Sem exceção |

### Como fatiar

Corte por **verificabilidade**, não por arquivo.

Ruim: "primeiro o backend, depois o frontend."
Bom: "primeiro o endpoint devolvendo dado fixo com teste; depois a consulta real
com teste; depois o cache com teste."

Cada fatia deve terminar num estado **verificável e íntegro**. Isso tem nome —
*walking skeleton* (Alistair Cockburn) — e a razão para isso importar com IA é
específica: **cada fatia verificável é um ponto de sincronização entre a
intenção e o resultado.** Sem eles, a deriva só aparece no fim.

---

## Autoteste

1. Qual é a definição operacional de "especificação boa"?
2. Cite os cinco componentes e o erro que ocorre se cada um faltar.
3. Aplique o teste dos três dedos a: "o relatório deve ser fácil de entender".
4. Por que numerar critérios não é burocracia? Cite os três usos.
5. Por que o CA-04 do exemplo ("cache vazio + API fora → 503") é o tipo de
   critério que só aparece com esforço deliberado?
6. Qual é o uso mais rentável da IA na fase de especificação — e por que não é
   escrever a especificação?
7. O que é EARS? Cite três dos cinco moldes e por que a rigidez ajuda.
8. Qual é a crítica histórica ao SDD e qual é a recomendação prática?
9. Qual é a razão custo-benefício entre corrigir plano e corrigir código?
10. Enuncie a regra do tamanho da fatia e explique por que se corta por
    verificabilidade e não por arquivo.

---

**Anterior:** [15-o-loop-do-agente](15-o-loop-do-agente.md) ·
**Próximo:** [17-verificacao-e-testes](17-verificacao-e-testes.md)
