# 10 · Fundamentos — o modelo relacional, ACID e os modelos mentais

`Nível: iniciante → intermediário` · `Última atualização: 11/08/2026`

O arquivo que transforma "eu sei escrever `SELECT`" em "eu entendo por que o banco funciona
assim". Tudo definido antes de ser usado.

---

## 1. O modelo relacional, formalmente (mas sem dor)

Em 1970, Edgar F. Codd, um matemático da IBM, publicou um artigo que mudou a computação: *A
Relational Model of Data for Large Shared Data Banks*. A ideia central:

> **Represente todos os dados como conjuntos de tuplas (linhas), e manipule-os com operações da
> teoria dos conjuntos.**

Traduzindo os termos formais para os que você já conhece:

| Termo formal (Codd) | Termo do dia a dia | O que é |
|---|---|---|
| **Relação** | Tabela | Um conjunto de linhas com as mesmas colunas |
| **Tupla** | Linha / registro | Um item: um cliente, um pedido |
| **Atributo** | Coluna / campo | Uma propriedade: nome, preço |
| **Domínio** | Tipo de dado | O conjunto de valores válidos (inteiros, textos, datas) |
| **Cardinalidade** | Número de linhas | Quantos itens há |
| **Grau** | Número de colunas | Quantas propriedades |

Por isso "banco **relacional**": não porque as tabelas se relacionam (embora se relacionem), mas
porque cada **tabela é uma relação** no sentido matemático — um conjunto de tuplas. Essa base
teórica não é decoração: é o que torna o SQL **declarativo** (você diz *o quê*, não *como*) e o
que permite ao banco otimizar suas consultas sozinho. Detalhes em
[60-teoria-avancada.md](60-teoria-avancada.md).

### A propriedade que decorre disso: você diz o quê, não como

```sql
SELECT nome FROM clientes WHERE cidade = 'Recife';
```
Você **não** disse "abra o arquivo, leia linha por linha, compare a cidade". Você descreveu o
resultado desejado. O banco decide *como* obtê-lo — varrer a tabela, usar um índice, em que ordem.
Essa separação entre **o quê** (sua consulta) e **o como** (o plano de execução) é a ideia mais
poderosa do modelo, e o assunto de [16-consultas-e-planejador.md](16-consultas-e-planejador.md).

---

## 2. ACID — as quatro garantias que definem um banco sério

Quando você confirma uma transação (`COMMIT`), o PostgreSQL promete quatro coisas, resumidas na
sigla **ACID**:

| Letra | Nome | Promessa | Exemplo de violação (que NÃO acontece) |
|---|---|---|---|
| **A** | Atomicidade | Tudo ou nada: uma transação inteira acontece, ou nenhuma parte | Debitar de uma conta mas não creditar na outra |
| **C** | Consistência | O banco vai de um estado válido a outro; as regras (constraints) sempre valem | Um pedido apontar para um cliente inexistente |
| **I** | Isolamento | Transações simultâneas não se atrapalham; cada uma "acha que está sozinha" | Duas vendas do último ingresso |
| **D** | Durabilidade | O que foi confirmado sobrevive a queda de energia, crash, reboot | Perder uma venda confirmada por falta de luz |

**Por que isto importa mais do que parece:** muitos bancos "modernos" (NoSQL, nos anos 2010)
abriram mão de partes do ACID em nome de velocidade e escala — e depois muitos voltaram atrás,
porque a aplicação tinha que reimplementar essas garantias, mal. O PostgreSQL nunca abriu mão: a
obsessão da comunidade por **não perder nem corromper dados** é a sua reputação central. Cada uma
dessas letras tem um mecanismo por trás:

- **Atomicidade e Durabilidade** vêm do **WAL** (*Write-Ahead Log*): antes de mudar um dado, o
  banco escreve num log o que **vai** fazer. Se cair no meio, ao reiniciar ele reaplica o log. Ver
  [17-arquitetura-interna.md](17-arquitetura-interna.md).
- **Isolamento** vem do **MVCC** (*Multi-Version Concurrency Control*): cada transação vê uma
  "foto" consistente dos dados. Ver [15-transacoes-e-mvcc.md](15-transacoes-e-mvcc.md).
- **Consistência** vem das **constraints** (chaves, `CHECK`, `NOT NULL`) que você declara.

---

## 3. A anatomia de uma tabela

```sql
CREATE TABLE pedidos (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id  BIGINT NOT NULL REFERENCES clientes(id),
    valor       NUMERIC(10,2) NOT NULL CHECK (valor >= 0),
    status      TEXT NOT NULL DEFAULT 'novo',
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Cada elemento é uma decisão sobre integridade:

| Elemento | O que garante | Sem ele |
|---|---|---|
| `BIGINT ... IDENTITY` | Identidade única e automática | Você geraria ids à mão, com risco de colisão |
| `PRIMARY KEY` | Uma linha é identificável de forma única | Não há como referenciar "aquele pedido" |
| `NOT NULL` | O valor sempre existe | Metade dos bugs vem de `NULL` inesperado |
| `REFERENCES clientes(id)` | O cliente existe | Pedidos órfãos, apontando para o nada |
| `CHECK (valor >= 0)` | Regra de negócio no banco | A aplicação teria que lembrar, sempre |
| `DEFAULT 'novo'` | Valor sensato quando omitido | Campos vazios inconsistentes |

> **O modelo mental nº 1:** *o banco é um guardião ativo da integridade, não um depósito passivo.*
> Cada constraint é uma regra que ele impõe a **todos** que escrevem — sua aplicação, um script de
> madrugada, você no `psql` às pressas. Regra no banco = regra que ninguém esquece.

---

## 4. Chaves: primária, estrangeira, candidata

**Chave primária:** a coluna (ou conjunto) que identifica cada linha de forma única e não-nula.
Toda tabela deveria ter uma.

- **Chave natural:** algo do mundo real que já é único (CPF, ISBN, e-mail). Tentador, mas
  arriscado — CPFs mudam de dono? ISBNs se repetem? E-mails trocam? — e vaza informação.
- **Chave substituta (*surrogate*):** um número sem significado (`id`), gerado pelo banco.
  Recomendada na prática: estável, opaca, eficiente.

**Chave estrangeira:** uma coluna que aponta para a chave primária de outra tabela, e cujo valor o
banco **obriga** a existir lá. É o que faz "relacional" funcionar.

**Chave candidata:** qualquer coluna que *poderia* ser primária (é única). Você escolhe uma como
primária; as outras viram `UNIQUE`.

> **Debate real: `SERIAL`/`IDENTITY` vs. `UUID`.** Ids sequenciais são compactos e rápidos, mas
> revelam volume ("o pedido 8.000") e não servem bem a sistemas distribuídos (dois servidores
> gerando o mesmo número). UUIDs são globais e opacos, mas grandes e aleatórios — e a
> aleatoriedade fragmenta índices. O PostgreSQL 18 trouxe `uuidv7()`: UUIDs **ordenados por
> tempo**, que juntam o melhor dos dois — globais e opacos, mas ordenados como um sequencial, sem
> fragmentar o índice. Ver [13-tipos-de-dados.md](13-tipos-de-dados.md).

---

## 5. NULL: o valor que não é um valor

`NULL` significa **"desconhecido"** ou **"não aplicável"** — não "zero", não "vazio", não "falso".
E isso tem consequências que pegam todo iniciante:

```sql
SELECT NULL = NULL;        -- NULL (não é 'true'!) — dois desconhecidos não são "iguais"
SELECT NULL = 5;           -- NULL
SELECT NULL + 1;           -- NULL — qualquer conta com desconhecido é desconhecida
SELECT count(*), count(telefone) FROM clientes;  -- count(coluna) IGNORA os NULL
```

Por isso:
```sql
WHERE telefone = NULL      -- ❌ NUNCA retorna nada
WHERE telefone IS NULL     -- ✅
WHERE telefone IS NOT NULL -- ✅
```

E a **lógica de três valores** (verdadeiro, falso, **nulo**):
```sql
SELECT * FROM t WHERE ativo = true;    -- linhas com ativo NULL NÃO aparecem
SELECT * FROM t WHERE ativo IS NOT true; -- aí sim inclui os NULL
```

`NULL` é uma das maiores fontes de bugs sutis em SQL. Trate-o com respeito; ver
[75-armadilhas.md](75-armadilhas.md). Ferramentas: `COALESCE(x, padrão)` (primeiro não-nulo),
`NULLIF(a, b)` (nulo se iguais), `x IS DISTINCT FROM y` (comparação que trata NULL como valor).

---

## 6. Esquemas, bancos e clusters — a hierarquia

O PostgreSQL organiza tudo em três níveis, e confundi-los causa erros de conexão e permissão:

```
   CLUSTER  (uma instância do servidor, um diretório de dados, uma porta)
     │
     ├── BANCO 'loja'        ← você se conecta a UM banco por vez
     │     ├── esquema 'public'   (o padrão)
     │     │     ├── tabela clientes
     │     │     └── tabela pedidos
     │     └── esquema 'vendas'
     │           └── tabela metas
     │
     ├── BANCO 'blog'
     └── BANCO 'postgres'    (banco administrativo padrão)
     │
     └── ROLES (usuários/grupos) — vivem no CLUSTER, valem para todos os bancos
```

| Nível | O que é | Analogia |
|---|---|---|
| **Cluster** | Uma instância do servidor rodando | Um prédio |
| **Banco de dados** | Um conjunto isolado de dados; você conecta a um | Um andar (você não vê os outros andares de dentro) |
| **Esquema** | Um *namespace* dentro do banco, para organizar tabelas | Uma sala no andar |
| **Tabela** | Os dados | Um armário na sala |
| **Role** | Usuário ou grupo; vive no cluster | Um crachá que abre certas salas |

**Consequências práticas:**
- Uma conexão fala com **um banco**. Para consultar outro, você reconecta (`\c outro`). Não há
  `JOIN` entre bancos diferentes (há entre esquemas do mesmo banco).
- O esquema `public` é o padrão. `search_path` define em quais esquemas o banco procura uma tabela
  não qualificada.
- Roles são do **cluster**: o usuário `app` existe para todos os bancos, mas os privilégios são
  por banco/esquema/tabela. Ver [20-seguranca.md](20-seguranca.md).

---

## 7. Os cinco modelos mentais que valem mais que qualquer comando

**1. "O banco é um guardião da integridade, não um depósito."** Toda regra que você declara
(chave, `CHECK`, `NOT NULL`) é imposta a todos, sempre. Ponha regras no banco.

**2. "Você diz o quê; o banco decide o como."** SQL é declarativo. Quando algo está lento, você
não conserta reescrevendo o "como" — você dá ao banco melhores meios (índices, estatísticas) e
deixa o planejador trabalhar. Ver [16](16-consultas-e-planejador.md).

**3. "Toda escrita é uma transação."** Mesmo um `INSERT` solto roda numa transação implícita. Isso
significa que ele é atômico e durável por padrão. Agrupe operações relacionadas num `BEGIN`/`COMMIT`
explícito quando elas dependem uma da outra.

**4. "Leitores não bloqueiam escritores; escritores não bloqueiam leitores."** É o lema do MVCC.
Uma consulta longa não trava quem está inserindo, e vice-versa — cada um vê sua versão consistente.
Isso é o que faz o Postgres escalar em concorrência. Ver [15](15-transacoes-e-mvcc.md).

**5. "NULL é desconhecido, não vazio."** Toda comparação com `NULL` dá `NULL`. Use `IS NULL`.

---

## 8. Os cinco porquês: por que existe o modelo relacional?

**1. Por que guardamos dados em tabelas com relações, e não num grande arquivo ou objeto?**
Porque isso separa a **estrutura lógica** dos dados de **como** eles são armazenados e acessados
fisicamente — a *independência de dados*.

**2. Por que essa separação (independência de dados) importa?**
Porque permite mudar índices, layout físico e otimizações **sem reescrever as aplicações**. A
consulta `SELECT nome FROM clientes` continua valendo se você adicionar um índice, particionar a
tabela ou mudar o disco.

**3. Por que Codd propôs isso em 1970, se antes havia bancos (hierárquicos, de rede) que
funcionavam?**
Porque os bancos pré-relacionais (IMS da IBM, CODASYL) **amarravam** a aplicação à estrutura
física: para responder uma pergunta nova, o programador tinha que navegar manualmente por ponteiros
entre registros, e mudar a estrutura quebrava todos os programas. Era caro e frágil.

**4. Por que isso era caro e frágil?**
Porque cada consulta era um programa procedural escrito à mão — "vá para o registro do cliente,
siga o ponteiro para o primeiro pedido, siga para o próximo...". Não havia uma linguagem de
consulta; não havia otimizador; a lógica de navegação estava espalhada por todo o código.

**5. Por que ninguém tinha resolvido isso antes de 1970?**
Aqui a cadeia chega a uma **conjunção histórica**: a teoria dos conjuntos e a lógica de predicados
existiam havia décadas, mas faltava (a) alguém que visse a conexão entre elas e o problema de dados
— foi a contribuição específica de Codd, matemático numa empresa de dados — e (b) hardware barato o
suficiente para pagar o custo da abstração. O modelo relacional **troca eficiência de máquina por
produtividade humana e flexibilidade**, e isso só valeu a pena quando o hardware ficou barato o
bastante. É um **trade-off econômico explícito**: os bancos de navegação eram mais rápidos na
máquina de 1970, mas o modelo relacional era mais barato em tempo de gente — e tempo de gente só
ficou mais caro desde então. Por isso ele venceu, e por isso, 55 anos depois, ainda domina.

---

## 9. Vocabulário consolidado

| Termo | Definição |
|---|---|
| **Relação / tabela** | Conjunto de tuplas com os mesmos atributos |
| **Tupla / linha** | Um registro |
| **Atributo / coluna** | Uma propriedade |
| **Domínio / tipo** | Conjunto de valores válidos de uma coluna |
| **Chave primária** | Identificador único e não-nulo da linha |
| **Chave estrangeira** | Referência garantida a uma linha de outra tabela |
| **Constraint (restrição)** | Regra que o banco impõe (`PK`, `FK`, `CHECK`, `UNIQUE`, `NOT NULL`) |
| **ACID** | Atomicidade, Consistência, Isolamento, Durabilidade |
| **NULL** | Ausência de valor (desconhecido/não aplicável) |
| **Cluster** | Uma instância do servidor PostgreSQL |
| **Banco de dados** | Conjunto isolado de dados dentro de um cluster |
| **Esquema** | Namespace de tabelas dentro de um banco |
| **Role** | Usuário ou grupo; vive no cluster |
| **Declarativo** | Descrever o resultado, não os passos |
| **WAL** | Write-Ahead Log — a base de atomicidade e durabilidade |
| **MVCC** | Controle de concorrência por múltiplas versões — a base do isolamento |

Glossário completo em [GLOSSARIO.md](GLOSSARIO.md).

---

## Autoteste

1. De onde vem, de verdade, a palavra "relacional"? (Não é "as tabelas se relacionam".)
2. O que cada letra de ACID promete? Dê um exemplo de violação que o Postgres impede para cada.
3. Qual mecanismo garante Atomicidade e Durabilidade? E Isolamento?
4. Explique por que "você diz o quê, o banco decide o como", e uma consequência prática disso.
5. `NULL = NULL` retorna o quê, e por quê? Como se testa "é nulo" corretamente?
6. Diferencie chave natural de chave substituta, e dê um argumento a favor de cada.
7. Que problema o `uuidv7()` do PG 18 resolve em relação a `SERIAL` e a `UUID` aleatório?
8. Explique a hierarquia cluster → banco → esquema → tabela, e onde vivem as roles.
9. Por que não há `JOIN` entre dois bancos diferentes do mesmo cluster?
10. Percorra os cinco porquês do modelo relacional até a parada. Que tipo de parada é?
