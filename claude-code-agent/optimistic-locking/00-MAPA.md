# Optimistic Locking — Mapa do Assunto

`Nível: do zero absoluto ao de pesquisa` · `Última atualização: 14/08/2026`
`Base verificada: Node v24.18.0 · Ubuntu 22.04.5 LTS · PostgreSQL 18.6 · RFC 9110`

---

## O que é este material

Um curso completo sobre **optimistic locking** (controle de concorrência otimista): a técnica
que permite dois usuários trabalharem sobre o mesmo dado sem que um apague o trabalho do
outro — **sem travar nada e sem ninguém esperar**.

O problema que ela resolve chama-se **lost update** (atualização perdida), e é o bug mais
silencioso e mais caro da computação com dados compartilhados: ele não gera erro, não aparece
no log, passa em todos os testes, e cobra a conta meses depois, quando os números não fecham.

Três ideias que este material repete porque são a origem de metade dos erros:

1. **Otimista não impede o conflito; impede o dano do conflito.**
2. **Quem detecta o conflito não é o banco — é o `if` que você escreve depois do `UPDATE`.**
   Zero linhas afetadas é a detecção, e ignorá-la é ter proteção zero com aparência total.
3. **Detectar é a parte fácil.** Decidir o que acontece com o conflito é produto, não banco de
   dados, e é onde os projetos se diferenciam.

O material responde, na ordem em que as perguntas aparecem na vida real:

1. **O que é isso e por que existe?** → [`01`](01-introducao-leigo.md), [`11`](11-historia.md)
2. **Como faço funcionar hoje?** → [`02`](02-pre-requisitos.md) a [`07`](07-projeto-modelo/README.md)
3. **Como funciona por dentro e onde estão os limites?** → Bloco B
4. **Como opero isso sem me arrepender?** → [`19`](19-retentativa-e-idempotencia.md), [`75`](75-armadilhas.md)
5. **Quanto custa e onde estudo mais?** → Blocos D e E

---

## O que você saberá ao final

- Explicar lost update a um leigo, sem usar a palavra "transação".
- Reproduzir o bug de forma determinística e provar que ele acontece no seu sistema.
- Escrever a guarda otimista correta em SQL, de cabeça, e saber por que ela é atômica.
- Escolher, com números, entre otimista, pessimista, delta atômico, fila e CRDT.
- Escolher o token de versão certo (inteiro, hash, UUID, `xmin`, `rowversion`) e a granularidade.
- Implementar retentativa que converge — e saber quando **não** retentar.
- Expor a proteção numa API HTTP com `ETag`, `If-Match`, `412` e `428`, sem os erros que
  derrubam integrações reais.
- Usar `@Version`, `rowversion`, `lock_version` e equivalentes sem cair nas armadilhas de cada um.
- Distinguir o que o nível de isolamento resolve do que só a versão resolve — e por que você
  precisa dos dois.
- Reconhecer *write skew* e saber que optimistic locking por linha **não** o detecta.
- Aplicar o mesmo raciocínio em sistemas distribuídos: CAS, leases, fencing tokens, CRDTs.
- Projetar a experiência de conflito: mesclar, perguntar ou refazer.
- Medir taxa de conflito e distância de versão, e usar esses números para decidir.
- Ler o paper de 1981 e a teoria de serializabilidade sem se perder.

---

## Roteiro de leitura

### Caminho rápido (90 minutos — "quero parar de perder dados")
[`01`](01-introducao-leigo.md) → [`04`](04-como-comecar.md) → [`75`](75-armadilhas.md)

### Caminho prático (um fim de semana — "vou implementar")
`01` → `02` → `03` → `04` → `06` → [`07-projeto-modelo/`](07-projeto-modelo/README.md) →
`16` → `17` → `19` → `75`

### Caminho completo (do zero à pesquisa)
Todos os arquivos em ordem numérica. Faça os laboratórios de [`70`](70-pratica.md) ao chegar
neles, não depois.

### Caminho por papel

| Papel | Leia |
|---|---|
| **Desenvolvedor de aplicação** | `01`, `04`, `05`, `06`, `16`, `17`, `19`, `75` |
| **Projetista de API** | `01`, `13`, `17`, `19`, `20`, `75` |
| **DBA / SRE** | `10`, `12`, `14`, `15`, `18`, `19`, `75`, `80` |
| **Arquiteto** | `10`, `13`, `14`, `15`, `18`, `20`, `65` |
| **Estudante / pesquisador** | `10`, `11`, `15`, `60`, `65`, `90`, `95` |
| **Quem só quer resolver um bug hoje** | `04 §6`, `75 Parte I` |

---

## Os arquivos

### Bloco A · Porta de entrada (01–09) — ✅ completo

| Arquivo | Nível | Do que trata |
|---|---|---|
| [`01-introducao-leigo.md`](01-introducao-leigo.md) | iniciante | A ficha na gaveta: lost update, otimista vs. pessimista, sem jargão |
| [`02-pre-requisitos.md`](02-pre-requisitos.md) | iniciante | O que saber e ter antes; tempo realista; rota de resgate |
| [`03-instalacao.md`](03-instalacao.md) | iniciante | Manual de campo: Node, Docker, PostgreSQL, JDK, Python, .NET, por SO; PATH, permissões, proxy, desinstalação, tabela de erros |
| [`04-como-comecar.md`](04-como-comecar.md) | iniciante | Do ambiente pronto ao conflito detectado na tela, com saída verificada |
| [`05-manual-de-uso.md`](05-manual-de-uso.md) | intermediário | Referência consultável: SQL, ORMs, HTTP, NoSQL, erros, retentativa |
| [`06-exemplos.md`](06-exemplos.md) | iniciante→avançado | 14 receitas completas, 5 delas executadas e verificadas |
| [`07-projeto-modelo/`](07-projeto-modelo/README.md) | iniciante→intermediário | Catálogo Otimista: API completa em Node, zero dependências, 21 testes |

### Bloco B · Núcleo (10–69) — ✅ completo

| Arquivo | Nível | Do que trata |
|---|---|---|
| [`10-fundamentos.md`](10-fundamentos.md) | intermediário | Vocabulário formal, as anomalias, as três fases, write skew, os cinco porquês |
| [`11-historia.md`](11-historia.md) | intermediário | De 1976 a 2026: 2PL, Kung & Robinson, a web, os ORMs, o NoSQL, o SSI |
| [`12-anatomia-do-lost-update.md`](12-anatomia-do-lost-update.md) | intermediário | As 4 formas do bug, como provar que acontece, a matemática da janela |
| [`13-tokens-de-versao.md`](13-tokens-de-versao.md) | intermediário→avançado | O contrato de um token, as 8 opções comparadas, ABA, granularidade |
| [`14-otimista-vs-pessimista.md`](14-otimista-vs-pessimista.md) | intermediário→avançado | A escolha com números: fórmulas, regimes, o terceiro caminho |
| [`15-isolamento-e-mvcc.md`](15-isolamento-e-mvcc.md) | avançado | O que o banco já faz, MVCC, SSI, `FOR UPDATE`, locks consultivos |
| [`16-orms-e-frameworks.md`](16-orms-e-frameworks.md) | intermediário | JPA, EF Core, ActiveRecord, Django, Node, GraphQL, gRPC e as armadilhas de cada um |
| [`17-http-e-apis.md`](17-http-e-apis.md) | intermediário→avançado | `ETag`/`If-Match`/`412`/`428`, o debate 409 vs 412, projeto de API |
| [`18-sistemas-distribuidos.md`](18-sistemas-distribuidos.md) | avançado | CAS, escritas condicionais, leases, fencing tokens, vector clocks, CRDTs |
| [`19-retentativa-e-idempotencia.md`](19-retentativa-e-idempotencia.md) | avançado | Quando retentar, backoff com jitter, chave de idempotência, outbox, métricas |
| [`20-ux-e-resolucao-de-conflitos.md`](20-ux-e-resolucao-de-conflitos.md) | intermediário→avançado | As 5 respostas ao conflito, merge de três vias, evitar o conflito, a mensagem |
| [`60-teoria-avancada.md`](60-teoria-avancada.md) | pesquisa | Serializabilidade, grafo de precedência, prova da validação, 5 limites teóricos |
| [`65-estado-da-arte.md`](65-estado-da-arte.md) | pesquisa | Panorama de agosto de 2026: híbridos, épocas, local-first, o que segue aberto |

### Bloco C · Prática e erros (70–79) — ✅ completo

| Arquivo | Do que trata |
|---|---|
| [`70-pratica.md`](70-pratica.md) | 12 laboratórios, do "ver o bug" a "auditar um sistema real" |
| [`75-armadilhas.md`](75-armadilhas.md) | 28 armadilhas com sintoma/causa/correção, 9 mitos, checklist de revisão |

### Bloco D · Economia e ecossistema (80–89) — ✅ completo

| Arquivo | Do que trata |
|---|---|
| [`80-custos-e-licencas.md`](80-custos-e-licencas.md) | Licenças das ferramentas, custo de implementar, e **onde o conflito aparece na fatura** |
| [`85-cursos-e-certificacoes.md`](85-cursos-e-certificacoes.md) | Cursos gratuitos em PT, EN e FR, pesquisados na web; a verdade sobre certificação |

### Bloco E · Fontes (90–99) — ✅ completo

| Arquivo | Do que trata |
|---|---|
| [`90-bibliografia.md`](90-bibliografia.md) | Livros comentados, com o capítulo a ler e o que é legalmente gratuito |
| [`95-referencias.md`](95-referencias.md) | 18 papers, RFCs, documentação oficial, código-fonte para ler, pessoas |
| [`GLOSSARIO.md`](GLOSSARIO.md) | ~90 termos definidos + tabela de códigos de erro |

---

## O projeto-modelo

[`07-projeto-modelo/`](07-projeto-modelo/README.md) — **Catálogo Otimista**: uma API de
produtos, pequena mas inteira, com optimistic locking ponta a ponta (coluna de versão →
guarda no `UPDATE` → `ETag`/`If-Match` → `412` → retentativa com jitter).

**Zero dependências.** Roda só com Node 24, usando o SQLite embutido, o servidor HTTP nativo
e o runner de testes nativo.

Ele tem, de propósito, **os dois caminhos ligados** — o protegido e o inseguro — e um script
que roda a mesma carga nos dois:

```
modo .................. inseguro          modo .................. seguro
edições sobreviventes . 10 de 20          edições sobreviventes . 20 de 20
edições PERDIDAS ...... 10                edições PERDIDAS ...... 0
versão final .......... 21                versão final .......... 21
escritas HTTP gastas .. 20 (1.00x)        escritas HTTP gastas .. 67 (3.35x)
tempo ................. 64.0 ms           tempo ................. 239.7 ms
```

A versão final é 21 nos dois. Ter a coluna `version` não protege nada — **usá-la no `WHERE`
é que protege**. E a correção custou 3,35× mais escritas: esse é o preço do otimismo sob
contenção máxima.

**Verificação (14/08/2026):** `npm test` → 21 testes, 21 aprovados, incluindo uma corrida real
com 20 clientes HTTP concorrentes. As duas demonstrações executadas. A sequência de `curl`
com `200`/`412`/`428`/`400` exercitada contra o servidor real.

---

## As 12 camadas de profundidade

Conforme o preset desta pasta. Onde cada uma foi atravessada:

| # | Camada | Onde |
|---|---|---|
| 1 | Intuição para leigo | [`01`](01-introducao-leigo.md) |
| 2 | Definição informal | [`01`](01-introducao-leigo.md), [`10 §1`](10-fundamentos.md) |
| 3 | Por que existe (história) | [`11`](11-historia.md) |
| 4 | Ambiente e primeiro uso | [`03`](03-instalacao.md), [`04`](04-como-comecar.md) |
| 5 | Fundamentos formais | [`10`](10-fundamentos.md) |
| 6 | Mecânica interna | [`12`](12-anatomia-do-lost-update.md), [`13`](13-tokens-de-versao.md), [`15`](15-isolamento-e-mvcc.md) |
| 7 | Implementação prática | [`06`](06-exemplos.md), [`07`](07-projeto-modelo/README.md), [`16`](16-orms-e-frameworks.md) |
| 8 | Casos de uso reais | [`06 §13–14`](06-exemplos.md), [`17`](17-http-e-apis.md), [`18`](18-sistemas-distribuidos.md) |
| 9 | Trade-offs e alternativas | [`14`](14-otimista-vs-pessimista.md), [`20`](20-ux-e-resolucao-de-conflitos.md) |
| 10 | Economia | [`80`](80-custos-e-licencas.md) |
| 11 | Profundidade de pesquisa | [`60`](60-teoria-avancada.md) |
| 12 | Estado da arte | [`65`](65-estado-da-arte.md) |

---

## Se você tem só cinco minutos

```sql
-- 1. Você leu a versão 7.
SELECT id, saldo, version FROM conta WHERE id = 42;

-- 2. Grave dizendo o que leu. Esta linha é o optimistic locking inteiro:
UPDATE conta
   SET saldo = 150, version = version + 1
 WHERE id = 42 AND version = 7;

-- 3. Se afetou ZERO linhas, alguém escreveu antes de você.
--    O banco NÃO dá erro. Quem detecta é o seu código.
```

Se o seu sistema faz o passo 2 mas ignora o passo 3, ele tem uma coluna de versão bonita e
**nenhuma proteção**. Comece por [`04-como-comecar.md`](04-como-comecar.md).

---

## Status e pendências

| Bloco | Status | Observação |
|---|---|---|
| A · Porta de entrada | ✅ | 7 documentos + projeto executável e verificado |
| B · Núcleo | ✅ | 13 documentos, do vocabulário à fronteira de pesquisa |
| C · Prática e erros | ✅ | 12 laboratórios · 28 armadilhas · 9 mitos |
| D · Economia e ecossistema | ✅ | Preços com data; cursos PT/EN/FR pesquisados na web |
| E · Fontes | ✅ | 18 papers, RFCs, docs oficiais, código-fonte |
| Glossário | ✅ | ~90 termos |

**Nada de estrutura está pendente.** O que precisa de manutenção periódica:

- [`65-estado-da-arte.md`](65-estado-da-arte.md) — reavaliar em **fevereiro de 2027**, ou
  quando o PostgreSQL 19 sair do beta.
- [`80-custos-e-licencas.md`](80-custos-e-licencas.md) — preços de nuvem mudam; reconferir a
  cada 6 meses.
- [`85-cursos-e-certificacoes.md`](85-cursos-e-certificacoes.md) — links de vídeo saem do ar;
  reconferir a cada 6 meses.
- [`03-instalacao.md`](03-instalacao.md) — versões de Node e PostgreSQL avançam; reconferir a
  cada release maior.
