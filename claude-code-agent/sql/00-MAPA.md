# SQL — do zero ao nível de pesquisa

Curso completo. Do "o que é uma tabela" à cota AGM e aos limites de
expressividade. Com **aplicação específica para engenharia química**.

Data de produção: **13/08/2026** · Ambiente verificado: Ubuntu 22.04.5 LTS,
Python 3.10.12, SQLite 3.37.2, DuckDB 1.5.5

---

## O que você saberá ao final

- **Escrever** consultas de qualquer complexidade: junções, agregação,
  subconsultas, CTEs, funções de janela.
- **Modelar** dados: chaves, restrições, normalização, séries temporais,
  cadastro que muda ao longo do tempo.
- **Fazer render**: ler um plano de execução, escolher índice, reescrever
  consulta lenta — com números medidos, não com fé.
- **Não errar**: cardinalidade de junção, `NULL`, ponto flutuante, fuso
  horário, dado faltante, média de razões.
- **Aplicar em planta**: balanço de massa, rendimento, CEP, OEE, alarmes,
  laboratório, manutenção, energia.
- **Entender por baixo**: álgebra relacional, complexidade, otimização,
  serializabilidade, e o que o SQL não pode fazer.

---

## Como usar este material

| Se você… | Comece por |
|---|---|
| Nunca viu SQL | [01](01-introducao-leigo.md) → [03](03-instalacao.md) → [04](04-como-comecar.md) |
| Precisa de um relatório para amanhã | [04](04-como-comecar.md) → [06-exemplos.md](06-exemplos.md) |
| É engenheiro químico e quer ver a aplicação | [30-engenharia-quimica.md](30-engenharia-quimica.md) |
| Já sabe o básico e quer profundidade | [13](13-juncoes.md) → [16](16-funcoes-de-janela.md) → [18](18-series-temporais.md) |
| Tem uma consulta lenta | [21-indices-e-desempenho.md](21-indices-e-desempenho.md) |
| Quer só a referência de sintaxe | [05-manual-de-uso.md](05-manual-de-uso.md) |
| Quer praticar | [70-pratica.md](70-pratica.md) e [07-projeto-modelo/](07-projeto-modelo/README.md) |
| Quer a teoria | [60-teoria-avancada.md](60-teoria-avancada.md) |

---

## Roteiro de leitura completo

### Bloco A · Porta de entrada

| # | Arquivo | O quê | Nível |
|---|---|---|---|
| 01 | [introducao-leigo](01-introducao-leigo.md) | O que é SQL, sem jargão nenhum. Por que existe. Onde já está rodando na sua vida | iniciante |
| 02 | [pre-requisitos](02-pre-requisitos.md) | O que saber e ter. Tempo realista. Rota de resgate para máquina bloqueada | iniciante |
| 03 | [instalacao](03-instalacao.md) | Manual por SO (Linux/macOS/Windows/WSL2), sem `sudo`, proxy, PATH, desinstalação, tabela de erros literais | iniciante |
| 04 | [como-comecar](04-como-comecar.md) | Do ambiente pronto ao primeiro resultado. Ordem de execução. Os 5 primeiros erros | iniciante |
| 05 | [manual-de-uso](05-manual-de-uso.md) | Referência consultável por tarefa. O que está obsoleto | todos |
| 06 | [exemplos](06-exemplos.md) | **15 exemplos executados**, dois deles casos reais de produção | iniciante→avançado |
| 07 | [projeto-modelo/](07-projeto-modelo/README.md) | **Historiador de planta química completo**: 344 mil leituras, 14 análises, 31 testes | intermediário |

### Bloco B · Núcleo

| # | Arquivo | O quê | Nível |
|---|---|---|---|
| 10 | [fundamentos](10-fundamentos.md) | Modelo relacional, chaves, álgebra, ACID, independência de dados | iniciante→interm. |
| 11 | [historia](11-historia.md) | Codd, SEQUEL, System R, Oracle, o padrão — e por que o SQL é esquisito | iniciante |
| 12 | [consulta-select](12-consulta-select.md) | A ordem de execução e suas cinco consequências | iniciante |
| 13 | [juncoes](13-juncoes.md) | **Cardinalidade**, tipos de junção, junção temporal, `ON` × `WHERE` | intermediário |
| 14 | [agregacao-e-grupos](14-agregacao-e-grupos.md) | `GROUP BY`, `HAVING`, estatística sem `STDDEV`, média de razões | intermediário |
| 15 | [subconsultas-e-ctes](15-subconsultas-e-ctes.md) | `EXISTS` × `IN` × `JOIN`, CTE, recursão | intermediário |
| 16 | [funcoes-de-janela](16-funcoes-de-janela.md) | `OVER`, molduras, *gaps and islands* — o recurso que muda tudo | interm.→avançado |
| 17 | [tipos-e-nulos](17-tipos-e-nulos.md) | Ponto flutuante, `STRICT`, lógica de três valores, `NULL` × zero × vazio | intermediário |
| 18 | [series-temporais](18-series-temporais.md) | Dado de sensor: modelagem, buracos, reamostragem, registro por exceção, retenção | interm.→avançado |
| 19 | [ddl-e-modelagem](19-ddl-e-modelagem.md) | `CREATE TABLE`, restrições, normalização, cadastro que muda (SCD), migração | intermediário |
| 20 | [dml-e-transacoes](20-dml-e-transacoes.md) | `INSERT`/`UPDATE`/`DELETE`, *upsert*, ACID, isolamento, **131 s × 0,03 s** | intermediário |
| 21 | [indices-e-desempenho](21-indices-e-desempenho.md) | B-tree, *sargable*, índice composto e de cobertura, plano, receita de consulta lenta | interm.→avançado |
| 22 | [views-e-analitico](22-views-e-analitico.md) | Views, camada semântica, modelagem em estrela, SQL gerado por BI, teste | intermediário |
| 23 | [dialetos](23-dialetos.md) | Tabela de tradução entre 7 bancos. SQLite × DuckDB. Oracle, SQL Server, PI System | intermediário |
| 24 | [sql-com-python](24-sql-com-python.md) | `sqlite3`, injeção de SQL, pandas, DuckDB, SQLAlchemy, script de relatório | intermediário |
| **30** | [**engenharia-quimica**](30-engenharia-quimica.md) | **Balanço de massa, rendimento, CEP, OEE, alarmes, LIMS, manutenção, energia, trilha de 90 dias** | interm.→avançado |
| 60 | [teoria-avancada](60-teoria-avancada.md) | Álgebra e cálculo relacional, complexidade, cota AGM, formas normais, otimização, serializabilidade | pesquisa |
| 65 | [estado-da-arte](65-estado-da-arte.md) | SQL:2023, PostgreSQL maximalismo, Iceberg, vetores, texto→SQL — **ago/2026** | avançado |

### Bloco C · Prática e erros

| # | Arquivo | O quê |
|---|---|---|
| 70 | [pratica](70-pratica.md) | 12 laboratórios progressivos + 5 desafios + soluções comentadas |
| 75 | [armadilhas](75-armadilhas.md) | 28 armadilhas e mitos, ordenados por quanto custam |

### Bloco D · Economia e ecossistema

| # | Arquivo | O quê |
|---|---|---|
| 80 | [custos-e-licencas](80-custos-e-licencas.md) | Licenças, preços de Oracle/SQL Server/nuvem com data, custos ocultos, aprisionamento |
| 85 | [cursos-e-certificacoes](85-cursos-e-certificacoes.md) | Cursos gratuitos em PT/EN/FR, certificados gratuitos e pagos, trilha recomendada |

### Bloco E · Fontes

| # | Arquivo | O quê |
|---|---|---|
| 90 | [bibliografia](90-bibliografia.md) | Livros comentados, com o que é legalmente gratuito |
| 95 | [referencias](95-referencias.md) | Padrão ISO, ~25 papers seminais, docs oficiais, código-fonte, normas ISA, pessoas |
| — | [GLOSSARIO](GLOSSARIO.md) | ~170 termos definidos |

---

## O projeto-modelo

[`07-projeto-modelo/`](07-projeto-modelo/README.md) — **historiador de uma
planta de resina alquídica em batelada**, com Python e nada mais.

```bash
cd 07-projeto-modelo
python3 scripts/gerar_dados.py     # ~5 s → 344.640 leituras, 28,6 MB
python3 scripts/consultar.py       # 14 análises
python3 -m unittest discover -s testes -v   # 31 testes
```

- 8 tabelas com `STRICT`, restrições e índices comentados; 7 views.
- 30 dias de operação sintética: 78 bateladas, 8 instrumentos a 1/min,
  laboratório, alarmes e paradas.
- **8 defeitos plantados de propósito** — buraco de aquisição, sensor travado,
  qualidade ruim, excursão de temperatura, erro de balanço, espículas de
  instrumento — cada um com a consulta que o acha e o teste que garante.
- 14 consultas analíticas, todas comentadas, cobrindo pivô, *gaps and islands*,
  CEP, OEE, Pareto, correlação e regressão.

**Executado e verificado.** Resultados reais no
[README do projeto](07-projeto-modelo/README.md).

---

## Status

| Bloco | Status | Conteúdo |
|---|---|---|
| **A · Porta de entrada** | ✅ | 7 documentos + projeto executável |
| **B · Núcleo** | ✅ | 18 documentos (10 → 65) |
| **C · Prática e erros** | ✅ | 12 laboratórios, 28 armadilhas |
| **D · Economia** | ✅ | Preços com data (13/08/2026), cursos PT/EN/FR pesquisados |
| **E · Fontes** | ✅ | ~25 papers, docs, normas ISA, glossário com ~170 termos |

**Total: 32 documentos + projeto-modelo.**

### O que foi executado

Todo o projeto-modelo (31 testes passando), os 15 exemplos do
[06](06-exemplos.md), todas as saídas do [04](04-como-comecar.md) incluindo as
mensagens de erro literais, as medições de índice do [21](21-indices-e-desempenho.md),
a medição de transação do [20](20-dml-e-transacoes.md), as semânticas de tipo e
`NULL` do [17](17-tipos-e-nulos.md), o comportamento de moldura do
[16](16-funcoes-de-janela.md), e as soluções dos laboratórios 4, 7 e 8.

### O que **não** foi executado (declarado no ponto)

Instalação em Windows e macOS; PostgreSQL (sem servidor no ambiente de
escrita); Docker; os 12 laboratórios como enunciados; consultas ao PI System.

### Manutenção

| Arquivo | Reavaliar |
|---|---|
| [65-estado-da-arte](65-estado-da-arte.md) | a cada 6 meses |
| [80-custos-e-licencas](80-custos-e-licencas.md) | a cada 6 meses |
| [03-instalacao](03-instalacao.md) | a cada 12 meses (versões) |
| [85-cursos-e-certificacoes](85-cursos-e-certificacoes.md) | a cada 12 meses (links) |

---

## Assuntos relacionados nesta pasta

- [`../postgresql/`](../postgresql/00-MAPA.md) — o banco em si: MVCC, planejador,
  arquitetura interna, replicação, administração.
- [`../apis/`](../apis/00-MAPA.md) — como expor esses dados para outros sistemas.
- [`../docker/`](../docker/00-MAPA.md) — como rodar um banco em container.

---

*Última atualização: 13/08/2026*
