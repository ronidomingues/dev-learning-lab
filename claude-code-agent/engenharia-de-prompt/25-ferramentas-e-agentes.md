# 25 · Ferramentas e agentes — quando o prompt vira sistema

**Nível:** avançado · **Escrito em:** 19/08/2026

Em 2026, a maior parte do prompt profissional **não é escrita para um humano
ler a resposta**. É escrita para um laço automático que chama funções, lê
resultados e decide o próximo passo. Este arquivo cobre a parte que é de
engenharia de prompt; o resto está em
[agentes-de-ia](../agentes-de-ia/00-MAPA.md).

---

## 25.1 · O laço, em cinco linhas

```
1. você envia: instrução + lista de ferramentas disponíveis + a tarefa
2. o modelo responde: "quero chamar buscar_pedido(numero='10493827')"
3. VOCÊ executa a função. O modelo não executa nada.
4. você devolve o resultado como uma mensagem de resultado de ferramenta
5. volta ao passo 2, até o modelo responder sem pedir ferramenta
```

**O ponto que muda tudo:** o modelo nunca executa nada. Ele **pede**. Todo o
poder — e toda a responsabilidade de segurança — é do seu código.

---

## 25.2 · A descrição da ferramenta é prompt

É onde mais se ganha e onde menos gente investe. Uma descrição ruim produz a
ferramenta certa chamada na hora errada, ou a errada chamada com convicção.

**Ruim:**

```python
{"name": "buscar_pedido", "description": "Busca um pedido."}
```

**Bom:**

```python
{
  "name": "buscar_pedido",
  "description": (
      "Busca um pedido pelo número. "
      "USE quando o cliente citar um número de pedido de 8 dígitos. "
      "NÃO USE para faturas (use buscar_fatura) nem para status de entrega "
      "(use rastrear_entrega). "
      "Devolve status, data, itens e valor total. "
      "Se o pedido não existir, devolve {\"erro\": \"nao_encontrado\"} — "
      "nesse caso, peça o número ao cliente em vez de tentar outro."
  ),
  "input_schema": {
      "type": "object",
      "properties": {
          "numero": {
              "type": "string",
              "description": "Exatamente 8 dígitos, sem pontos, traços ou espaços. Ex.: 10493827",
          }
      },
      "required": ["numero"],
      "additionalProperties": False,
  },
}
```

Os quatro elementos que fazem a diferença: **quando usar**, **quando não usar
(com o encaminhamento certo)**, **o que devolve**, e **o que fazer no caso de
erro**. Sem o segundo, ferramentas parecidas são confundidas; sem o quarto, o
modelo entra em laço tentando variações.

---

## 25.3 · Projetar o conjunto de ferramentas

| Princípio | Por quê |
|---|---|
| **Poucas e distintas** | 30 ferramentas parecidas confundem; junte por domínio |
| **Nomes sem ambiguidade** | `buscar_pedido` e `consultar_pedido` no mesmo conjunto é receita de erro |
| **Granularidade de tarefa, não de endpoint** | `agendar_visita` vale mais que três chamadas primitivas encadeadas pelo modelo |
| **Erro informativo no resultado** | `{"erro": "cpf_invalido", "dica": "11 dígitos"}` conserta o comportamento; `500` não |
| **Idempotência quando possível** | o modelo vai repetir chamadas; garanta que repetir não duplica pedido |
| **Confirmação em ação destrutiva** | enviar e-mail, apagar, pagar: passe por aprovação humana |

> **Quando o conjunto passa de ~20 ferramentas**, a lista sozinha ocupa
> milhares de tokens em toda chamada. As saídas modernas são: carregamento
> sob demanda (o modelo busca a ferramenta que precisa) e agrupamento por
> domínio. Ver [agentes-de-ia](../agentes-de-ia/13-ferramentas-e-tool-use.md).

---

## 25.4 · Erro de ferramenta é prompt também

Quando a função falha, o que você devolve **é o contexto com que o modelo vai
decidir o próximo passo**. Compare:

| Devolução | O que o modelo faz |
|---|---|
| `Error: 500` | tenta de novo, igual, várias vezes |
| `{"erro": "timeout", "acao": "tente novamente uma vez; se falhar, informe o cliente que o sistema está lento"}` | tenta uma vez e comunica |
| `{"erro": "nao_encontrado", "acao": "peça o número correto ao cliente"}` | pede o número |

**Regra:** toda mensagem de erro devolvida a um modelo deve conter **o que
aconteceu** e **o que fazer agora**. Isso é escrever prompt, ainda que esteja
dentro de um `except` no seu código.

---

## 25.5 · O prompt de sistema de um agente

Muda de forma em relação ao prompt de tarefa única. O que ele precisa ter:

```
1. Papel e escopo — o que você faz e o que você NÃO faz
2. Objetivo — como se parece a tarefa concluída
3. Política de ferramentas — quando chamar, quantas vezes tentar, quando parar
4. Política de parada — quando desistir e escalar para humano
5. Política de incerteza — o que fazer quando faltar informação (perguntar,
   não supor)
6. Formato do resultado final
7. Restrições invioláveis — o que nunca fazer, mesmo que pedido
```

Os itens 3, 4 e 5 são os que quase todo mundo esquece e são a causa dos
comportamentos mais caros:

- **Sem política de parada:** o agente tenta 40 vezes, gasta US$ 12 numa tarefa
  de US$ 0,02, e ainda falha.
- **Sem política de incerteza:** ele **supõe** o dado que falta — e supõe com
  confiança.
- **Sem política de tentativa:** um erro transitório vira laço infinito.

```
<politica_de_parada>
- Máximo de 6 chamadas de ferramenta por pedido do cliente.
- Se a mesma ferramenta falhar duas vezes com o mesmo erro, pare.
- Ao parar sem concluir, responda: "PRECISO_ESCALAR: <motivo em 1 frase>".
- Nunca invente um resultado que a ferramenta não devolveu.
</politica_de_parada>
```

---

## 25.6 · Quando **não** usar agente

| Situação | Use |
|---|---|
| passos conhecidos e fixos | código comum chamando o modelo em cada etapa (*workflow*) |
| erro é caro e irreversível | fluxo com aprovação humana |
| latência importa muito | chamada única |
| a tarefa é determinística | função, não modelo |

**Opinião profissional, e forte:** a maior parte do que é vendido como "agente"
seria mais barato, mais rápido e mais confiável como um encadeamento fixo de
chamadas. Agente se justifica quando o **caminho** é desconhecido de antemão —
não quando o caminho é conhecido e alguém achou moderno deixar o modelo
descobrir de novo a cada execução.

---

## 25.7 · Avaliar um agente

Não dá para avaliar só a resposta final. O que se mede:

| Métrica | O que revela |
|---|---|
| taxa de conclusão da tarefa | o essencial |
| número de passos até concluir | eficiência e custo |
| **chamadas de ferramenta erradas** | descrição de ferramenta ruim |
| chamadas repetidas idênticas | falta política de tentativa |
| custo médio e **cauda de custo** (p95) | a cauda é o que quebra o orçamento |
| taxa de escalonamento | calibragem da política de parada |
| ações destrutivas evitadas | segurança |

**Meça o p95, não a média.** Numa distribuição típica de agente, 5% das
execuções custam 10× a mediana; é essa cauda que aparece na fatura.

---

## Autoteste

1. Quem executa a ferramenta, e por que essa resposta é a base da segurança?
2. Quais quatro elementos toda descrição de ferramenta precisa ter?
3. Por que a mensagem de erro devolvida ao modelo é considerada prompt?
4. Cite as três políticas que faltam na maioria dos prompts de agente e o
   custo concreto de cada ausência.
5. Quando um encadeamento fixo é melhor que um agente?
6. Por que medir p95 de custo em vez da média?
