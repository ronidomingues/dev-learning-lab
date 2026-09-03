# 02 · Pré-requisitos

`Nível: iniciante` · `Atualizado em: 14/08/2026`

Este arquivo diz **o que saber**, **o que ter instalado** e **quanto tempo levar** antes de
seguir. Também traz a **rota de resgate** para cada pré-requisito que faltar.

Optimistic locking é um assunto pequeno na superfície e fundo embaixo. Dá para usar bem
sabendo pouco; dá para errar feio sabendo pouco. Este arquivo separa as duas coisas.

---

## 1. Conhecimento

### Indispensável

| Você precisa saber | Por quê | Onde aprender |
|---|---|---|
| **Ler e escrever `SELECT`, `UPDATE` e `WHERE` em SQL** | A guarda otimista *é* uma cláusula `WHERE`. Sem isso, nada faz sentido. | [`../sql/00-MAPA.md`](../sql/00-MAPA.md) → arquivos `04` a `06` |
| **O que é uma transação e o que ela garante** | Optimistic locking convive com transações; a maioria dos erros vem de confundir os dois. | [`../postgresql/15-transacoes-e-mvcc.md`](../postgresql/15-transacoes-e-mvcc.md) |
| **Que existe mais de um usuário ao mesmo tempo** | Parece óbvio; não é. Quem programa pensando num usuário só nunca vê o problema em desenvolvimento. | [`01-introducao-leigo.md`](01-introducao-leigo.md) |
| **Ler o valor de retorno de uma função** | A detecção é o número de linhas afetadas. Quem ignora retornos não detecta nada. | qualquer linguagem |

### Ajuda muito

| Tema | Por quê | Onde aprender |
|---|---|---|
| **Níveis de isolamento** (`READ COMMITTED`, `REPEATABLE READ`, `SERIALIZABLE`) | Define o que o banco já protege sozinho e o que sobra para você. | [`15-isolamento-e-mvcc.md`](15-isolamento-e-mvcc.md) e a [doc do PostgreSQL](https://www.postgresql.org/docs/current/transaction-iso.html) |
| **HTTP: métodos, cabeçalhos, códigos de status** | A versão do HTTP disso é `ETag`/`If-Match`/`412`. | [`../apis/00-MAPA.md`](../apis/00-MAPA.md) |
| **Um ORM qualquer** (JPA/Hibernate, EF Core, ActiveRecord, Django) | Todos implementam optimistic locking, com nomes diferentes e pegadinhas próprias. | [`16-orms-e-frameworks.md`](16-orms-e-frameworks.md) |
| **JavaScript moderno (`async`/`await`, `fetch`)** | Só para rodar o projeto-modelo. O conceito não depende de linguagem. | — |
| **Sistemas distribuídos: relógios, ordenação, CAS** | Necessário para o Bloco B avançado ([`18`](18-sistemas-distribuidos.md), [`60`](60-teoria-avancada.md)). | [`90-bibliografia.md`](90-bibliografia.md) |

### O que **não** é pré-requisito (e você pode achar que é)

- **Saber teoria de serializabilidade.** Ela está em [`60-teoria-avancada.md`](60-teoria-avancada.md)
  e você chega lá depois, não antes.
- **Ter um banco "de verdade" instalado.** O projeto-modelo roda em SQLite embutido no Node.
- **Trabalhar em escala.** O *lost update* aparece com dois usuários, não com dois milhões.

---

## 2. Ambiente

| Item | Mínimo | Recomendado | Necessário para |
|---|---|---|---|
| Sistema operacional | qualquer um dos três (Linux, macOS, Windows) | — | tudo |
| **Node.js** | 22.5 (quando `node:sqlite` surgiu) | **24 LTS** | projeto-modelo, exemplos em JS |
| Memória | 512 MB livres | 2 GB | projeto-modelo |
| Disco | ~120 MB (só o Node) | 1 GB (com Docker/Postgres) | projeto-modelo / exemplos SQL |
| PostgreSQL *(opcional)* | 14 | 18 | exemplos de isolamento em [`15`](15-isolamento-e-mvcc.md) e [`70`](70-pratica.md) |
| Docker *(opcional)* | 24 | 29 | subir Postgres sem instalar |
| Conta em serviço | **nenhuma** | — | nada aqui exige cadastro |
| Cartão de crédito | **nenhum** | — | — |

Instruções completas de instalação, por sistema operacional, em
[`03-instalacao.md`](03-instalacao.md).

**Alternativa sem instalar nada:** existe. Veja o topo do [`03`](03-instalacao.md) — dá para
fazer os exercícios de SQL em um playground no navegador e só depois montar o ambiente local.

---

## 3. Tempo realista

Números honestos, de quem já ensinou isto. Assumem que você já programa e sabe SQL básico.
Se estiver aprendendo SQL junto, **dobre tudo**.

| Objetivo | Leitura | Prática | Total realista |
|---|---|---|---|
| **Entender a ideia** e explicar a um colega | `01` | — | **40 min** |
| **Usar corretamente** no seu ORM, num CRUD | `01`,`04`,`06`,`16`,`75` | rodar o projeto-modelo | **1 dia** |
| **Projetar** a política de concorrência de um sistema | Bloco A + `10`–`20` | labs 1–7 de [`70`](70-pratica.md) | **1 a 2 semanas** |
| **Discutir com autoridade** — escolher entre OCC, 2PL, SSI, CRDT | tudo até `60` | labs 1–12 | **1 a 2 meses** |
| **Ler e criticar papers** da área | `60`, `65`, `90`, `95` | reimplementar OCC do zero | **6 meses a 1 ano** |

Dois avisos contra o otimismo (o outro tipo):

- **A ideia se aprende em uma hora. O julgamento leva anos.** Saber *que* existe optimistic
  locking é fácil; saber *onde não usar* é o que separa quem já quebrou produção de quem não.
- **A parte difícil não é detectar o conflito — é decidir o que fazer com ele.** Essa parte
  é de produto e de UX, não de banco de dados. Veja [`20`](20-ux-e-resolucao-de-conflitos.md).

---

## 4. Rota de resgate

O que fazer se faltar algum pré-requisito, sem abandonar este material:

| Falta | Rota curta (hoje) | Rota completa |
|---|---|---|
| **SQL** | Leia só o `01` e o `04`; substitua mentalmente `UPDATE ... WHERE version = ?` por "grava se ainda estiver como eu li". | [`../sql/`](../sql/00-MAPA.md), 1–2 semanas |
| **Transações** | Aceite por ora: "transação = tudo ou nada". Suficiente até o `14`. | [`../postgresql/15-transacoes-e-mvcc.md`](../postgresql/15-transacoes-e-mvcc.md) |
| **Node.js** | Não instale nada; leia [`06-exemplos.md`](06-exemplos.md), que tem versões em SQL puro, Java, C#, Python e Ruby. | [`03-instalacao.md`](03-instalacao.md), 20 min |
| **HTTP** | Pule [`17`](17-http-e-apis.md) na primeira passada; ele não é pré-requisito do resto. | [`../apis/`](../apis/00-MAPA.md) |
| **Um banco instalado** | Use o projeto-modelo (SQLite embutido) e o playground do [`03`](03-instalacao.md). | [`../postgresql/03-instalacao.md`](../postgresql/03-instalacao.md) |
| **Tempo** | Leia `01` → `04` → `75`. Nessa ordem, em 90 minutos, você já evita os erros mais caros. | — |

---

## 5. Teste de prontidão

Responda antes de seguir. Se errar mais de dois, volte à tabela acima.

1. O que este comando faz, e quantas linhas ele afeta se `version` for 9?
   ```sql
   UPDATE conta SET saldo = 100, version = version + 1 WHERE id = 1 AND version = 7;
   ```
2. Qual a diferença entre "o comando falhou" e "o comando afetou zero linhas"?
3. O que uma transação garante, em uma frase?
4. Duas requisições HTTP chegam ao seu servidor no mesmo milissegundo. Elas veem o mesmo
   estado do banco?
5. Se você roda `SELECT saldo` e, um segundo depois, `UPDATE saldo = saldo_lido - 10`,
   que problema você acabou de criar?

**Gabarito resumido:** (1) atualiza a conta 1 só se a versão for exatamente 7; sendo 9,
afeta **zero** linhas. (2) Falha lança erro e você é obrigado a tratar; zero linhas é sucesso
silencioso, e ignorá-lo é o bug clássico. (3) Ou tudo dentro dela acontece, ou nada acontece,
e o resultado é durável. (4) Depende do nível de isolamento e do momento do commit — em
`READ COMMITTED`, não necessariamente. (5) Um *lost update*: entre o `SELECT` e o `UPDATE`
alguém pode ter mudado o saldo, e você acabou de sobrescrever a mudança.

---

## Autoteste

1. Qual é o único pré-requisito de conhecimento realmente inegociável, e por quê?
2. Você precisa instalar PostgreSQL para acompanhar este material? E Docker?
3. Quanto tempo, honestamente, até saber *projetar* a política de concorrência de um sistema?
4. Você não sabe SQL e quer aproveitar hoje. Qual é a rota?
5. Por que "detectar o conflito" é a parte fácil?

---

**Próximo:** [`03-instalacao.md`](03-instalacao.md)
