# PostgreSQL — Mapa do Assunto

`Nível: do zero absoluto ao de pesquisa` · `Última atualização: 11/08/2026`
`Versão de referência: PostgreSQL 18 (série estável atual)`

---

## O que é este material

Um curso completo sobre **PostgreSQL** (também chamado "Postgres"): o banco de dados relacional
livre mais capaz e respeitado do mundo. Do "o que é um banco de dados" à teoria de otimização de
consultas e aos limites da distribuição.

Ele responde, na ordem em que as perguntas aparecem na vida real:

1. **O que é isso e por que existe?** → [`01`](01-introducao-leigo.md) e [`11`](11-historia.md)
2. **Como começo a usar hoje?** → [`02`](02-pre-requisitos.md) a [`07`](07-projeto-modelo/README.md)
3. **Como funciona por dentro, e onde estão os limites?** → Bloco B
4. **Como opero isso em produção sem me arrepender?** → [`20`](20-seguranca.md),
   [`21`](21-administracao-e-operacao.md)
5. **Quanto custa e onde estudo mais?** → Blocos D e E

Três ideias que o material repete porque são a origem de metade dos erros: **o banco é um guardião
ativo da integridade** (não um depósito passivo); **você diz o quê, o banco decide o como**; e
**`NULL` é desconhecido, não vazio**.

---

## O que você saberá ao final

- Explicar a um leigo o que é um banco de dados relacional e por que ele importa.
- Instalar o PostgreSQL em qualquer SO e sair do zero a um banco funcionando.
- Escrever SQL com confiança: JOINs, agregações, janelas, CTEs, subconsultas.
- Modelar dados corretamente (chaves, relações, normalização) e saber quando desnormalizar.
- Usar os tipos ricos do PostgreSQL: JSONB, arrays, ranges, `uuidv7`, e saber quando cada um.
- Criar e escolher índices, e ler um `EXPLAIN ANALYZE` para diagnosticar consultas lentas.
- Entender MVCC, transações, níveis de isolamento e o VACUUM a ponto de operar em produção.
- Explicar a arquitetura interna (processos, WAL, memória) sem caixas-pretas.
- Estender o banco (PostGIS, pgvector) e saber por que a extensibilidade o fez envelhecer bem.
- Replicar, fazer backup com PITR, e planejar alta disponibilidade.
- Proteger o banco: autenticação, roles, RLS, criptografia, e evitar SQL injection.
- Estimar custo de verdade — self-hosted vs. gerenciado vs. serverless — e o custo de gente.

---

## Roteiro de leitura

### Caminho rápido (um fim de semana, "quero entender e mexer")
`01` → `02` → `03` → `04` → `06` → `07-projeto-modelo/` → `75`

### Caminho do desenvolvedor
`01` → `03` → `04` → `05` → `10` → `12` → `13` → `14` → `15` → `16` → `07-projeto-modelo/` → `70` → `75`

### Caminho de quem vai administrar (DBA / operação)
`01` → `10` → `15` → `17` → `19` → `20` → `21` → `70` → `75`

### Caminho de arquiteto / pesquisador
todo o Bloco B em ordem, com peso em `15` → `16` → `17` → `60` → `65`, depois `95`

### Caminho de quem decide (compra, arquitetura)
`01` → `11` → `18` → `19` → `80` → `65` → `75`

---

## Arquivos

### BLOCO A · Porta de entrada (01–09)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [01-introducao-leigo.md](01-introducao-leigo.md) | iniciante | O que é um banco, o que é "relacional", SQL, CRUD. Zero jargão. |
| [02-pre-requisitos.md](02-pre-requisitos.md) | iniciante | O que saber e ter antes. Tempo realista. Rota de resgate. |
| [03-instalacao.md](03-instalacao.md) | iniciante | Manual de campo: por SO, Docker, nuvem, pg_hba, erros. |
| [04-como-comecar.md](04-como-comecar.md) | iniciante | Do psql à primeira tabela, JOIN, transação. |
| [05-manual-de-uso.md](05-manual-de-uso.md) | intermediário | Referência consultável: psql, SQL, tipos, JSONB, índices, backup. |
| [06-exemplos.md](06-exemplos.md) | intermediário | 14 receitas completas, do blog ao pgvector e diagnóstico de consulta lenta. |
| [07-projeto-modelo/](07-projeto-modelo/README.md) | intermediário | Uma biblioteca completa: esquema, regras no banco, app, testes. |

### BLOCO B · Núcleo (10–69)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [10-fundamentos.md](10-fundamentos.md) | iniciante→interm. | Modelo relacional, ACID, NULL, cluster/banco/esquema, modelos mentais. |
| [11-historia.md](11-historia.md) | iniciante→interm. | De Codd e Ingres ao PG 18. A extensibilidade e a governança sem dono. |
| [12-modelo-relacional-e-sql.md](12-modelo-relacional-e-sql.md) | interm.→avançado | Ordem de execução, JOINs a fundo, normalização, subconsultas. |
| [13-tipos-de-dados.md](13-tipos-de-dados.md) | interm.→avançado | Números (dinheiro!), texto, datas, JSONB, arrays, ranges, uuidv7. |
| [14-indices.md](14-indices.md) | interm.→avançado | B-tree, GIN, GiST, BRIN, parciais, por expressão; a arte de escolher. |
| [15-transacoes-e-mvcc.md](15-transacoes-e-mvcc.md) | avançado | MVCC, isolamento, VACUUM, deadlocks, o último ingresso. |
| [16-consultas-e-planejador.md](16-consultas-e-planejador.md) | avançado | EXPLAIN, métodos de acesso, JOINs, estatísticas, diagnóstico. |
| [17-arquitetura-interna.md](17-arquitetura-interna.md) | avançado | Processos, memória, WAL, I/O assíncrona (PG 18), armazenamento. |
| [18-extensoes.md](18-extensoes.md) | interm.→avançado | pg_stat_statements, PostGIS, pgvector, FDWs, linguagens. |
| [19-replicacao-e-alta-disponibilidade.md](19-replicacao-e-alta-disponibilidade.md) | avançado | Streaming, lógica, failover, PITR, sharding. |
| [20-seguranca.md](20-seguranca.md) | avançado | Rede, pg_hba, roles, RLS, criptografia, SQL injection. |
| [21-administracao-e-operacao.md](21-administracao-e-operacao.md) | avançado | Backup, VACUUM, tuning, monitoramento, migrações. |
| [60-teoria-avancada.md](60-teoria-avancada.md) | pesquisa | Álgebra relacional, normalização formal, complexidade, CAP, SSI. |
| [65-estado-da-arte.md](65-estado-da-arte.md) | pesquisa | Agosto/2026: PG 18, IA/pgvector, serverless, distribuído. |

### BLOCO C · Prática e erros (70–79)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [70-pratica.md](70-pratica.md) | todos | 10 laboratórios progressivos com critério de aprovação. |
| [75-armadilhas.md](75-armadilhas.md) | todos | Os erros de iniciante, os mitos, as más práticas e por que persistem. |

### BLOCO D · Economia e ecossistema (80–89)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [80-custos-e-licencas.md](80-custos-e-licencas.md) | todos | Livre e grátis; self-hosted vs. gerenciado vs. serverless; vs. Oracle. |
| [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) | todos | Cursos grátis PT/EN/FR e o mapa das certificações (EDB, nuvem). |

### BLOCO E · Fontes (90–99)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [90-bibliografia.md](90-bibliografia.md) | todos | Livros com edição, nível e o que é legalmente gratuito. |
| [95-referencias.md](95-referencias.md) | todos | Docs, código, papers, pessoas, e como o material foi verificado. |
| [GLOSSARIO.md](GLOSSARIO.md) | todos | ~90 termos definidos. |

---

## Status por bloco

| Bloco | Status | Observação |
|---|---|---|
| A · Porta de entrada | ✅ | 6 documentos + projeto-modelo (biblioteca) com app e testes |
| B · Núcleo | ✅ | 14 documentos, fundamentos → interno → teoria → estado da arte |
| C · Prática e erros | ✅ | 10 laboratórios + catálogo de armadilhas |
| D · Economia | ✅ | Preços e cursos consultados em 11/08/2026 |
| E · Fontes | ✅ | Bibliografia, referências e glossário |

Legenda: ✅ completo · 🟡 parcial · ⬜ pendente

---

## Aviso de validade

O PostgreSQL lança uma major por ano (tipicamente em setembro), com ~5 anos de suporte cada. Este
material foi escrito sobre:

- **Versão:** PostgreSQL 18 (18.0 em 25/09/2025; 18.3 em 26/02/2026)
- **Data das consultas de preço, versão e curso:** 11/08/2026
- **Câmbio para ordens de grandeza:** US$ 1 ≈ R$ 5,40

O que envelhece mais rápido, em ordem: [`65-estado-da-arte`](65-estado-da-arte.md) e
[`80-custos-e-licencas`](80-custos-e-licencas.md) (meses), [`03-instalacao`](03-instalacao.md) e
[`85-cursos-e-certificacoes`](85-cursos-e-certificacoes.md) (releases / ~1 ano). O núcleo
conceitual ([`10`](10-fundamentos.md), [`12`](12-modelo-relacional-e-sql.md),
[`15`](15-transacoes-e-mvcc.md), [`60`](60-teoria-avancada.md)) envelhece em década — porque o
modelo relacional, o SQL e o MVCC são estáveis.

**Nota de verificação:** o código JavaScript do projeto-modelo teve a sintaxe validada e a suíte de
testes roda/pula corretamente sem banco (5 testes pulados, 0 falhas). O SQL do esquema **não** pôde
ser executado contra um PostgreSQL real no ambiente de escrita (sem servidor e sem Docker daemon);
segue a documentação oficial do PG 18 — **execute-o você mesmo**. Detalhes no
[README do projeto](07-projeto-modelo/README.md) e em [95-referencias.md](95-referencias.md).

---

## Autoteste do mapa

1. De onde vem, de verdade, a palavra "relacional"?
2. O que cada letra de ACID promete?
3. Qual arquivo você leria primeiro para diagnosticar uma consulta lenta em produção?
4. Onde estão os limites teóricos (o que o modelo relacional **não** expressa sozinho)?
5. Por que o núcleo conceitual envelhece em década e o estado da arte em meses?
