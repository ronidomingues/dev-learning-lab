# 23 · Projeto de ferramentas — a engenharia que decide se funciona

`Nível: intermediário → avançado` · `Escrito em 01/09/2026`

> Escrever `tools/call` é trivial. Escrever uma ferramenta que um modelo usa
> **corretamente na décima vez**, sem inventar argumento, sem entupir o contexto e sem
> entrar em laço, é a parte difícil — e a que quase nenhum material cobre.
>
> Este arquivo é opinião fundamentada em prática, marcada como tal. A spec dá orientação
> mínima sobre nomes; o resto é ofício.

---

## 1. O modelo mental que muda tudo

> **O usuário da sua API é um modelo estatístico que decide pelo nome, pela descrição e
> pelo schema — e que não vê o seu código.**

Consequências diretas:

| Se… | Então… |
|---|---|
| o nome é ambíguo | o modelo chama a ferramenta errada, e nenhum compilador reclama |
| a descrição é incompleta | o modelo inventa argumento |
| a mensagem de erro não instrui | o modelo repete o mesmo erro em laço |
| o resultado é enorme | o modelo raciocina pior, e você paga por isso |
| há dez ferramentas parecidas | o modelo escolhe quase ao acaso |
| o schema aceita qualquer coisa | o modelo manda qualquer coisa |

---

## 2. Nomes

### O que a spec exige

- 1 a 128 caracteres; sensível a maiúsculas;
- só `A-Z a-z 0-9 _ - .`;
- sem espaço, vírgula ou caractere especial;
- únicos dentro do servidor.

### O que a prática ensina

| Ruim | Bom | Por quê |
|---|---|---|
| `get` | `buscar_pedido_por_id` | `get` o quê? |
| `search` | `buscar_livros_por_titulo` | colide com todo servidor |
| `do_thing` | `cancelar_assinatura` | o verbo tem de ser o verbo do negócio |
| `query` | `listar_pedidos_por_status` | "query" convida a mandar SQL |
| `handle_request` | `criar_ticket_de_suporte` | nome de implementação, não de domínio |
| `tool1` | qualquer coisa | sério |

**Regras que funcionam:**

1. **Verbo + substantivo + qualificador**: `buscar_pedido_por_id`, `listar_pedidos_por_status`.
2. **Palavras do domínio do usuário**, não do seu código.
3. **Distinguíveis entre si**: se dois nomes diferem por uma palavra, o modelo vai
   confundi-los. `listar_usuarios` e `listar_usuarios_ativos` é pedir problema; prefira
   uma ferramenta com parâmetro `apenas_ativos`.
4. **Prefixo do domínio quando o servidor cobre vários**: `fatura_emitir`,
   `fatura_cancelar`, `cliente_criar`. Ajuda o modelo a agrupar.
5. **Consistência de idioma.** Escolha português **ou** inglês para todos os nomes. Misturar
   é a pior opção — ambos funcionam, a mistura não.

---

## 3. Descrições

A descrição é a **documentação da API para o modelo**. Ela precisa de cinco coisas:

```python
@server.tool()
def buscar_pedido_por_id(pedido_id: str) -> Pedido:
    """Busca UM pedido pelo identificador exato (ex.: 'PED-4711').        # 1. o que faz

    Não faz busca por texto livre nem por nome de cliente —               # 2. o que NÃO faz
    para isso, use `listar_pedidos`.                                      # 3. o que usar então

    O identificador é obtido em `listar_pedidos` ou informado             # 4. onde obter a entrada
    pelo usuário.

    Devolve erro se o pedido não existir.                                 # 5. o caso ruim
    """
```

O item 2 é o mais subestimado. **Dizer o que a ferramenta não faz previne mais erro do
que dizer o que ela faz** — porque o erro típico do modelo é usar a ferramenta próxima.

### Padrões que funcionam

| Padrão | Exemplo |
|---|---|
| **Exemplo no texto** | "ex.: `PED-4711`" |
| **Apontar a ferramenta vizinha** | "para busca por texto, use `listar_pedidos`" |
| **Marcar efeito colateral** | "**ALTERA** o acervo" |
| **Declarar custo/limite** | "no máximo 50 linhas por chamada" |
| **Declarar vida útil de handle** | "cestas expiram após 24 h" |
| **Ordem de uso** | "use `buscar_livros` primeiro para obter o ISBN" |

### Anti-padrões

- descrição vazia ou de uma palavra;
- copiar a docstring interna, cheia de detalhe de implementação;
- prometer o que a ferramenta não faz ("busca inteligente em tudo");
- descrição de 5.000 caracteres — o custo é multiplicado por toda conversa;
- **instruções ao modelo que contradizem o host** ("sempre chame esta ferramenta
  primeiro", "não avise o usuário"). Isso é *tool poisoning*, mesmo feito de boa-fé.

---

## 4. `instructions` do servidor

O campo `instructions` do `MCPServer` é onde se ensina a **ordem** e a **política** de uso
do conjunto. É subutilizado e vale muito:

```python
server = MCPServer(
    "biblioteca",
    instructions=(
        "Use `buscar_livros` para encontrar um livro pelo título ou autor e obter o ISBN. "
        "Só então use `emprestar_livro` ou `devolver_livro`, que exigem o ISBN exato. "
        "Empréstimos duram 14 dias. Sempre confirme com o usuário antes de emprestar."
    ),
)
```

Sem isso, o modelo tenta `emprestar_livro` com o **título** no campo `isbn`.

---

## 5. Schemas

### 5.1 Restrinja

```python
# ❌ o modelo manda qualquer coisa
def buscar(termo: str, limite: int) -> list[str]: ...

# ✅ o schema já recusa o absurdo, e a mensagem é útil
def buscar(
    termo: Annotated[str, Field(description="Trecho do título ou do autor. Mínimo 2 caracteres.",
                                min_length=2, max_length=80)],
    limite: Annotated[int, Field(description="Máximo de resultados (1 a 25).", ge=1, le=25)] = 10,
) -> ResultadoBusca: ...
```

Ganhos, todos de uma vez: o cliente valida antes de chegar em você; a `description` de
cada campo entra no schema que o modelo lê; a falha vira **erro de execução** com texto
que o modelo consegue corrigir; e você não escreve `if` nenhum.

### 5.2 Prefira `enum` a string livre

```python
Status = Literal["novo", "pago", "enviado", "cancelado"]
```

O modelo **vai** inventar `"pendente"` se você aceitar `str`. Com `Literal`, o schema já
lista os valores e o modelo escolhe entre eles.

### 5.3 Poucos parâmetros obrigatórios

Cada obrigatório é uma chance de o modelo inventar. Padrão sensato: um ou dois
obrigatórios, o resto com valor padrão.

### 5.4 Tipos declarados para saída estruturada

⚠️ Medido nesta máquina: `-> dict` e `-> list[str]` **não** geram `outputSchema`, e
`structured_content` volta `None`. Declare `BaseModel`/`TypedDict` quando quiser saída
estruturada.

### 5.5 Não repita o schema na descrição

O modelo já vê o schema. Repetir tipos e limites na descrição gasta contexto sem ganho.
Use a descrição para o que **não** cabe no schema: semântica, ordem de uso, efeito
colateral.

---

## 6. Granularidade — o erro mais comum

### 6.1 Ferramenta genérica demais

```python
@server.tool()
def executar_sql(query: str) -> list[dict]:
    """Executa uma consulta SQL."""
```

Por que é ruim, em ordem de gravidade:

1. **Superfície de ataque máxima.** Uma injeção de prompt bem-sucedida vira acesso
   irrestrito ao banco.
2. **O modelo escreve SQL errado**, contra um esquema que ele não conhece direito.
3. **Você não pode limitar, cachear nem auditar por operação** — tudo é "executar_sql".
4. **Impossível de evoluir.** Mudou o esquema, quebrou tudo silenciosamente.

### 6.2 Ferramenta específica demais

```python
buscar_pedido_por_id, buscar_pedido_por_cliente, buscar_pedido_por_data,
buscar_pedido_por_status, buscar_pedido_por_valor, buscar_pedido_por_produto  # ...
```

Por que é ruim: entope o contexto; o modelo escolhe quase ao acaso entre nomes parecidos;
e combinações ficam impossíveis.

### 6.3 O ponto de equilíbrio

**Uma ferramenta por *intenção do usuário*, com parâmetros para as variações.**

```python
@server.tool()
def listar_pedidos(
    cliente: str | None = None,
    status: Status | None = None,
    desde: str | None = None,
    limite: int = 20,
) -> Resultado:
    """Lista pedidos, filtrando por qualquer combinação de cliente, status e data inicial.
    Sem filtro, devolve os mais recentes. Máximo 50 por chamada."""
```

Teste: se você consegue nomear a ferramenta com **uma frase do usuário** ("quero ver os
pedidos do fulano que ainda não foram enviados"), a granularidade está certa.

**Quantas ferramentas por servidor?** Opinião: até **15** é confortável; **15 a 30** exige
`instructions` muito boa; **acima de 30** é sinal de que o servidor deveria ser dois, ou
de que você mapeou endpoints em vez de intenções. Sessenta ferramentas num servidor é uma
bandeira vermelha — de contexto e de superfície.

---

## 7. Retorno

### 7.1 O orçamento

Tudo que a ferramenta devolve **entra no contexto**. Custa tokens, disputa espaço e
degrada o raciocínio.

| Devolver | Custo aproximado |
|---|---|
| 40.000 linhas de `SELECT *` | dezenas de milhares de tokens, contexto estourado |
| 20 linhas + `total` + `tem_proxima` | dezenas de tokens |
| resumo + `resource_link` | pouquíssimo, e o cliente busca **se** precisar |

### 7.2 Devolva o que ajuda o próximo passo

```python
# ❌ o modelo não sabe se acabou
return {"itens": [...]}

# ✅ o modelo sabe o que fazer em seguida
return Pagina(total=250, pagina=2, itens=[...], tem_proxima=True)
```

### 7.3 Nomeie os campos para humanos

`devolver_ate` é melhor que `dt_dev`. O modelo entende ambos, mas erra menos com o
primeiro — e o log fica legível para você.

### 7.4 Marque o que foi truncado

```python
if truncado:
    texto += f"\n[Truncado: havia {total} resultados. Refine o filtro ou pagine.]"
```

Sem isso o modelo conclui sobre um conjunto que ele acha completo.

---

## 8. Erros

Já visto em [15 §2.6](15-primitivas-do-servidor.md) e [06 §3](06-exemplos.md), mas é
onde mais se ganha, então repetimos a regra:

**Uma boa mensagem de erro tem três partes:**

1. **o que aconteceu**, com o valor recebido;
2. **por que**, ou o que era esperado;
3. **o que fazer em seguida**, nomeando a ferramenta certa quando houver.

```python
raise ToolError(
    f"Não existe livro com ISBN {isbn!r}. "                  # 1
    f"O ISBN tem 13 dígitos. "                               # 2
    f"Use `buscar_livros` para achar o ISBN pelo título."    # 3
)
```

E lembre: **no SDK Python 2.x, só `ToolError`/`ResourceError` entregam a mensagem ao
modelo.** Uma exceção crua vira `Error executing tool <nome>`.

---

## 9. Determinismo e idempotência

Duas propriedades que os modelos exigem sem pedir:

**Determinismo.** Mesma entrada, mesma saída, mesma ordem. Um `SELECT` sem `ORDER BY`
devolve ordens diferentes, o modelo vê "mudou" e reage a ruído. A spec pede ordem
determinística em `tools/list`; **estenda isso a todo resultado seu**.

**Idempotência em operações de escrita.** O modelo repete chamadas — porque perdeu o
resultado do contexto, porque a resposta demorou, porque o usuário reformulou. Se
`criar_pedido` não for idempotente, você cria três pedidos.

```python
@server.tool()
def criar_pedido(
    cliente: str,
    itens: list[str],
    chave_idempotencia: Annotated[str, Field(
        description="Identificador único desta tentativa. Reenviar a MESMA chave "
                    "devolve o pedido já criado, sem duplicar.")],
) -> Pedido:
    ...
```

Ou torne a duplicata detectável e **devolva o registro existente com uma nota**, em vez
de criar outro ou de falhar.

---

## 10. Ferramentas destrutivas

Quatro camadas, na ordem:

1. **Não exista.** A melhor ferramenta destrutiva é a que você não expôs. Precisa mesmo
   de `apagar_cliente`, ou basta `arquivar_cliente`?
2. **Escopo estreito.** `cancelar_pedido(pedido_id)` em vez de `executar_operacao(op, alvo)`.
3. **Confirmação por elicitação (MRTR).** O parâmetro resolvido **não aparece no schema**,
   então o modelo não pode forjá-lo. Ver [16 §2](16-primitivas-do-cliente.md).
4. **Reversibilidade.** Exclusão lógica com janela de recuperação, não `DELETE` físico.

E na descrição, diga em maiúsculas: `ALTERA`, `APAGA`, `IRREVERSÍVEL`.

> Não confie em `annotations.destructiveHint`: a spec manda os clientes tratarem
> anotações como **não confiáveis**. Use-as, mas como cortesia — não como controle.

---

## 11. Como testar o projeto (não a implementação)

O teste que importa não é "a função soma certo". É "**o modelo usa isto certo?**".

| Teste | Como |
|---|---|
| **Descrição existe e é substantiva** | asserção de tamanho mínimo em `tools/list` |
| **O parâmetro secreto não vaza** | asserção sobre as chaves do `inputSchema` |
| **O teto é respeitado** | chamar com `limite=10000` e conferir o erro |
| **A mensagem de erro instrui** | asserção de que o texto **nomeia a ferramenta vizinha** |
| **Sem colisão de nomes** | asserção sobre a lista completa, ordenada |
| **Ordem determinística** | duas chamadas, mesmo resultado |
| **Idempotência** | duas chamadas com a mesma chave, um registro |
| **Uso real pelo modelo** | roteiro com 10 pedidos em linguagem natural; medir quantas vezes ele escolheu certo |

O último é o único que realmente responde à pergunta, e é o mais raro de ver.
Vale automatizar: um script que manda dez pedidos ao modelo com o seu catálogo e conta os
acertos. Quando você mudar um nome, esse número muda — e você descobre antes do usuário.

---

## 12. Lista de verificação

- [ ] nome: verbo + substantivo + qualificador, do domínio do usuário
- [ ] nomes distinguíveis entre si, e não colidindo com o óbvio (`search`, `get`)
- [ ] idioma consistente em todo o servidor
- [ ] descrição com: o que faz · o que **não** faz · qual usar então · exemplo · caso ruim
- [ ] `instructions` do servidor ensinando a **ordem** de uso
- [ ] schema restringido (`min`/`max`, `enum`/`Literal`, `description` por campo)
- [ ] poucos parâmetros obrigatórios
- [ ] tipo de retorno declarado (para haver `outputSchema`)
- [ ] uma ferramenta por **intenção**, não por endpoint
- [ ] menos de ~15 ferramentas, ou `instructions` excelente
- [ ] retorno paginado, com `total` e `tem_proxima`
- [ ] truncamento **avisado** no texto
- [ ] erros com as três partes, usando `ToolError`
- [ ] ordem determinística em todo resultado
- [ ] escrita idempotente, ou duplicata detectável
- [ ] destrutivas: escopo estreito, confirmação por MRTR, reversíveis
- [ ] testes sobre **contrato** (descrição, schema, mensagem), não só sobre lógica

---

## 13. Autoteste

1. Por que "o modelo é o usuário da sua API" muda o projeto? Cite três consequências.
2. Por que dizer o que a ferramenta **não** faz previne mais erro do que dizer o que faz?
3. Cite quatro problemas de uma ferramenta `executar_sql`, em ordem de gravidade.
4. Qual o teste prático para saber se a granularidade está certa?
5. Por que `Literal["novo","pago"]` é melhor que `str`?
6. O que um resultado paginado precisa devolver além dos itens, e por quê?
7. Por que ordem determinística importa para um consumidor que é um LLM?
8. Por que idempotência é obrigatória em ferramenta de escrita usada por um modelo?
9. Quais são as quatro camadas de proteção de uma ferramenta destrutiva?
10. Descreva um teste que mede se **o modelo** usa a sua ferramenta corretamente.

---

**Anterior:** [22 · Extensões](22-extensoes.md) · **Próximo:** [24 · Operação e produção](24-operacao-e-producao.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Orientação normativa sobre nomes: [Tools · Tool Names](https://modelcontextprotocol.io/specification/2026-07-28/server/tools#tool-names)
e [SEP-986](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/1603).
Ordem determinística e cache: [changelog 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/changelog).
Comportamento de `outputSchema` e de `ToolError` medido nesta máquina (`mcp` 2.1.1) em
01/09/2026. O restante é opinião profissional, declarada como tal.*
