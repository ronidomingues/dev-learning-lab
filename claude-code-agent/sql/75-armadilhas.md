# 75 — Armadilhas, mitos e más práticas

Nível: todos · Data: 13/08/2026

Vinte e oito itens. Ordenados por quanto custam quando acontecem, não por
dificuldade. Os primeiros dez respondem pela maioria dos números errados que
circulam em relatório de planta.

---

## Parte I — As que dão número errado sem dar erro

### 1. O leque do `JOIN` (*fan-out*)

**Sintoma:** a soma aumentou e você não sabe por quê.

Medido: `SUM(carga_kg)` = **389.335 kg**; depois de juntar com `analise_lab`
(4 ensaios por batelada) = **1.536.422 kg**. Quase 4× — nenhum erro, nenhum
aviso.

**Correção:** conte antes e depois de todo `JOIN`. Agregue antes de juntar.
Ver [13-juncoes.md](13-juncoes.md).

**Por que persiste:** o resultado é plausível. 1.536 toneladas não parece
absurdo se você não sabe a resposta certa.

---

### 2. `WHERE valor = NULL`

**Sintoma:** zero linhas, nenhum erro.

`NULL` é "desconhecido". `NULL = NULL` é desconhecido, não verdadeiro.

**Correção:** `IS NULL` / `IS NOT NULL`.

---

### 3. `NOT IN` com `NULL`

```sql
SELECT * FROM t WHERE x NOT IN (SELECT y FROM outra);   -- y é anulável
```
Se **um único** `y` for `NULL`, o resultado é **sempre vazio**. E vazio é
interpretado como "não há nenhum caso", que é a conclusão oposta.

**Correção:** `NOT EXISTS`, sempre.

---

### 4. `BETWEEN` com data

```sql
WHERE ts BETWEEN '2026-07-01' AND '2026-07-31'
```
Perde tudo do dia 31 depois das 00:00:00.

**Correção:** `>= '2026-07-01' AND < '2026-08-01'`. Intervalo semiaberto,
sempre.

**Por que persiste:** o `BETWEEN` lê bonito, e o erro é de um dia em trinta —
3%, o suficiente para passar despercebido e o bastante para mudar uma meta.

---

### 5. Divisão inteira

```sql
SELECT 7/2;                 -- 3
SELECT 100 * aprovadas / total;   -- 0 se aprovadas < total
```

**Correção:** `100.0 * a / b`. O `.0` precisa vir **no começo**.

---

### 6. Média de razões × razão de somas

```sql
AVG(rendimento_pct)                       -- 90,65
100.0*SUM(produzido_kg)/SUM(carga_kg)     -- 90,60
```
Aqui a diferença é pequena porque as cargas são parecidas. Com uma batelada de
500 kg e outra de 50.000, a primeira forma dá peso igual às duas — e o número
fica muito errado.

**Correção:** para rendimento, disponibilidade, OEE, taxa de refugo — quase
sempre você quer a razão de somas.

---

### 7. `AVG` ignora `NULL` silenciosamente

`COUNT(*)` = 43.080; `COUNT(valor)` = 43.060. A média foi de 43.060, e o
relatório vai dizer 43.080.

**Pior:** sensor falha justamente em condição extrema. Os nulos **não são
aleatórios**, e ignorá-los enviesa a média para o lado bonito.

**Correção:** traga `COUNT(*)` junto com toda média, sempre.

---

### 8. Média de dado transiente

```
hora 05:00 → média 83,4 °C, mínimo 49,8, máximo 180,4
```
A média descreve um reator que nunca existiu — ele estava resfriando.

**Correção:** filtre por fase ou regime; traga sempre min e máx.

---

### 9. Somar o que não se soma

Temperatura, pressão, pH e concentração são **intensivas**: `SUM` não
significa nada. Vazão é **taxa**: some `vazão × Δt`. Nível é **estado**.

**Caso especial cruel:** pH é logarítmico. A média aritmética de pH 3 e pH 7
não é 5 — a correta passa pela concentração de H⁺.

**Correção:** ver [30-engenharia-quimica.md](30-engenharia-quimica.md) §10.3.

---

### 10. Código de falha legado (`-9999`)

Historiadores antigos, sem `NULL`, marcavam falha com `-9999`, `-999` ou
`999999`. Uma média que os inclua é lixo — e sai plausível o bastante para
passar.

**Correção:** `NULLIF(valor, -9999)` **na carga**, e documente.

---

## Parte II — As que dão erro (e são fáceis de resolver)

### 11. Apelido no `WHERE`

`WHERE media > 100` com `media` sendo `AVG(...) AS media` → o `WHERE` roda
antes do `SELECT`. Use `HAVING`, ou repita a expressão, ou passe a matemática
para o lado da constante.

### 12. Aspas trocadas

`WHERE tag_id = "TI-101"` → `no such column: TI-101` (ou pior, no MySQL,
funciona e ensina o hábito errado). `'texto'`, `"identificador"`.

### 13. Coluna fora do `GROUP BY`

`SELECT tag_id, ts, AVG(valor) ... GROUP BY tag_id` → erro em PostgreSQL;
**resultado arbitrário** em SQLite e MySQL. A permissividade é pior.

### 14. Vírgula sobrando

`SELECT a, b, FROM t` → erro de sintaxe. Escolha uma convenção de vírgula
(início ou fim de linha) e mantenha.

### 15. Faltou `COMMIT`

Nada foi salvo, nenhum erro. Em Python, `con.commit()` ou `with con:`.

---

## Parte III — Desempenho

### 16. Função na coluna do `WHERE`

```sql
WHERE substr(ts,1,10) = '2026-07-10'    -- 5,0 ms
WHERE ts >= '2026-07-10' AND ts < '2026-07-11'   -- 0,1 ms
```
**Cinquenta vezes**, medido, mesma resposta. O índice para de funcionar quando
a coluna está embrulhada.

### 17. `SELECT *` em produção

Impede índice de cobertura (medido: 17,8 ms → 0,5 ms), traz dado inútil, e
quebra o código quando alguém adiciona coluna.

### 18. `COMMIT` por linha

**131,50 s contra 0,03 s** para 20.000 linhas — **4.311×**. Cada `COMMIT`
força um `fsync` no disco.

### 19. `OFFSET` grande

`OFFSET 100000` produz e descarta 100 mil linhas — e ainda pode pular
registros se o dado mudar entre páginas. Use paginação por chave.

### 20. `LIKE '%algo'`

Curinga no início impede o índice. `LIKE 'algo%'` usa.

### 21. Índice demais

Índice acelera leitura e **atrasa toda escrita**. Numa tabela de série
temporal com escrita contínua, um índice a mais é custo permanente. Crie
depois de medir, não antes.

### 22. Laço de aplicação no lugar de um `UPDATE`

Buscar 10.000 linhas, alterar em Python, gravar uma a uma. Milhares de vezes
mais lento que um `UPDATE ... FROM`. E não é atômico.

---

## Parte IV — Mitos

### 23. "`COUNT(1)` é mais rápido que `COUNT(*)`"

**Falso** em todo banco moderno há mais de vinte anos. São idênticos no plano.
`COUNT(*)` é o padrão e diz o que faz.

### 24. "Subconsulta é sempre mais lenta que `JOIN`"

**Falso.** O otimizador reescreve a maioria das subconsultas como junção.
`EXISTS` frequentemente é **mais** rápido, porque para na primeira ocorrência e
não multiplica linhas.

### 25. "`DISTINCT` conserta duplicata do `JOIN`"

**Falso e perigoso.** `DISTINCT` remove linhas totalmente idênticas; se elas
diferem em qualquer coluna, continuam lá e a soma continua inflada. `DISTINCT`
como remédio de junção é sintoma de bug não diagnosticado.

### 26. "SQL não escala"

Confunde SQL (a linguagem) com uma implementação específica. PostgreSQL roda
bancos de dezenas de terabytes; o SQLite está em mais de um trilhão de
instalações. O que não escala é uma modelagem ruim.

### 27. "NoSQL é mais rápido"

Para *um padrão específico de acesso*, às vezes. Para consulta ad hoc, junção
e agregação, quase nunca. E a maioria dos produtos NoSQL sobreviventes acabou
adicionando uma linguagem parecida com SQL.

### 28. "O ORM me poupa de saber SQL"

**Falso**, e é a mentira mais cara da lista. O ORM gera SQL; quando ele gera o
problema de N+1 consultas ou uma junção cartesiana, você precisa saber ler SQL
para descobrir. ORM sem SQL é depuração no escuro.

---

## Erros de instrumentação que o SQL não vê

Estes não são erros de SQL. São a razão de um engenheiro de processo ser
melhor analista de dado de planta do que um cientista de dados.

| Sintoma no dado | Causa física | O SQL avisa? |
|---|---|---|
| Valor constante por horas | Transmissor travado, tomada de impulso entupida | **Não** |
| 300 °C num reator de resina | Termopar rompido (lê fundo de escala) | Não |
| Vazão negativa | Fluxo reverso, ou sensor invertido na instalação | Não |
| Degrau brusco sem transiente | Recalibração, ou troca de instrumento | Não |
| Ruído aumentando | Cavitação, folga mecânica, aterramento ruim | Não |
| Valor "bom demais" | Dado sintetizado por um controle em manual | Não |
| Espícula isolada de 9,9 bar | Falha eletrônica — **com qualidade BOA** | Não |
| Correlação perfeita entre dois tags | Podem ser o mesmo sinal duplicado no SDCD | Não |

O último merece atenção: **dois tags perfeitamente correlacionados frequentemente
são o mesmo sinal**, replicado por engano em duas malhas. Um modelo treinado
com os dois "descobre" uma relação que é tautologia.

---

## Vinte segundos que evitam a maioria dos erros

Antes de aceitar qualquer número:

```sql
SELECT COUNT(*) FROM sua_consulta;          -- 1. o total faz sentido?
-- 2. min, máx e n vieram junto da média?
-- 3. o intervalo de data é semiaberto?
-- 4. algum JOIN mudou a contagem de linhas?
-- 5. você filtrou qualidade e nulos?
-- 6. a grandeza que você somou é somável?
```

Seis perguntas. É mais do que a maioria dos relatórios que circulam recebe.

---

## Autoteste

1. Por que o *fan-out* é a armadilha nº 1, e como se detecta em dez segundos?
2. Por que `NOT IN` com `NULL` é pior que dar erro?
3. `BETWEEN` com data perde quanto? Por que ninguém percebe?
4. Quando a média de razões difere muito da razão de somas?
5. Por que os nulos de um sensor **não** são aleatórios?
6. Qual foi o ganho medido de reescrever `substr(ts,1,10)=...`?
7. Quantas vezes mais lento é um `COMMIT` por linha? Por quê?
8. Por que `DISTINCT` não conserta duplicata de junção?
9. Cite três erros de instrumentação que o SQL nunca vai apontar.
10. Escreva as seis perguntas de verificação, de memória.

---

*Próximo: [80-custos-e-licencas.md](80-custos-e-licencas.md).*
