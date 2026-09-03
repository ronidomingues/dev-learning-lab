# 80 · Custos e licenças

`Nível: intermediário` · `Preços consultados em: 14/08/2026`
`Câmbio de referência: US$ 1,00 ≈ R$ 5,40 (ordem de grandeza; consulte a cotação do dia)`

> **Nota sobre este arquivo.** Optimistic locking é uma **técnica**, não um produto. Não há
> licença, plano ou fatura para ela. Este arquivo foi reinterpretado, como prevê o preset,
> para responder às perguntas que de fato existem: **o que custa aprender**, **o que custa
> implementar**, **o que custa operar** — e onde o custo aparece na fatura sem você perceber.

---

## 1. A técnica em si: gratuita e sem dono

Optimistic locking **não é patenteado, não tem licença e não tem dono**. É um método
publicado em 1981 em periódico científico (Kung & Robinson, ACM TODS). Qualquer pessoa pode
implementá-lo, vendê-lo embutido em produto, ensiná-lo e derivar dele.

Existiu uma patente sobre uma implementação específica (a US 5,247,672, *Transaction processing
system and method with reduced locking*, atribuída à IBM), mas patentes de software dos anos
1990 já expiraram — o prazo é de 20 anos a partir do depósito. **Não há risco de propriedade
intelectual em usar a técnica.**

**Quem paga a conta do conhecimento?** Universidades e centros de pesquisa corporativos —
IBM, Carnegie Mellon, Berkeley — financiados por pesquisa pública e por interesse dos próprios
fabricantes de banco em ter o método padronizado. É o modelo clássico da ciência da computação
acadêmica: publicar em vez de patentear rende mais adoção, e adoção é o que os fabricantes
queriam.

---

## 2. Licenças das ferramentas que a implementam

Tudo o que este curso usa é livre. A coluna que importa é a última.

| Ferramenta | Licença | Uso comercial | Obrigação |
|---|---|---|---|
| **PostgreSQL** | PostgreSQL License (tipo BSD/MIT) | livre | manter o aviso de copyright |
| **SQLite** | domínio público | livre | nenhuma |
| **Node.js** | MIT | livre | manter o aviso |
| **MySQL Community** | GPLv2 (com exceção de FOSS) | livre | **cuidado**: distribuir software ligado ao cliente GPL exige atenção; a Oracle vende licença comercial para isso |
| **MariaDB** | GPLv2 | livre | idem |
| **Hibernate ORM** | Apache 2.0 nas versões recentes (parte do projeto historicamente sob LGPL 2.1; o Hibernate Tools segue LGPL) | livre | avisos e notice |
| **Entity Framework Core** | MIT (v10.0.x) | livre | manter o aviso |
| **Django** | BSD 3 cláusulas | livre | manter o aviso |
| **Rails / ActiveRecord** | MIT | livre | manter o aviso |
| **Redis** | mudou de licença em 2024 (RSALv2/SSPLv1); **Valkey** é o fork sob BSD | ver a versão | **verifique a versão exata** antes de embarcar em produto |
| **Oracle Database** | proprietária | pago | licenciamento por processador ou usuário nomeado |
| **SQL Server** | proprietária (há Express e Developer gratuitos) | pago acima do Express | por núcleo ou CAL |

**Duas armadilhas de licença que valem atenção:**

1. **MySQL sob GPLv2.** Distribuir uma aplicação que embarca o cliente MySQL pode obrigar você
   a liberar o código. Há a *FOSS License Exception* e há licença comercial da Oracle. Se você
   **hospeda** o serviço (SaaS) em vez de distribuir, a GPLv2 não é acionada. Se você
   distribui software instalável, converse com quem entende de licenciamento.
2. **Redis pós-2024.** As licenças RSALv2/SSPLv1 restringem oferecer o Redis como serviço
   gerenciado. Para a maioria dos usos (usar o Redis dentro do seu produto), não muda nada;
   para quem revende, muda tudo. O **Valkey** (fork sob BSD, mantido pela Linux Foundation) é
   a saída se a licença for um problema.

---

## 3. O custo real: implementar

O custo dominante é **tempo de gente**. Estimativas de esforço, para um sistema já existente:

| Trabalho | Esforço | Observação |
|---|---|---|
| Adicionar coluna `version` + guarda no `UPDATE` | 1 a 4 h por agregado | mecânico |
| Migração de dados (backfill da coluna) | 1 h a 1 dia | em tabela grande, exige migração online |
| Propagar a versão até a API (DTO, ETag) | 4 a 16 h | costuma revelar acoplamentos |
| Retentativa com backoff e jitter | 4 a 8 h | uma vez só; depois é biblioteca |
| Tratamento de conflito na interface | **1 a 5 dias por tela** | é aqui que o orçamento vai |
| Merge campo a campo | 2 a 5 dias | só onde compensa |
| Métricas e painel | 4 a 8 h | **faça primeiro**, não por último |
| Testes com concorrência real | 1 a 3 dias | exige infraestrutura de teste |

**Onde o dinheiro realmente vai:** na interface. A parte de banco de dados é barata e
mecânica. Decidir o que o usuário vê, e implementar merge ou diff, é o que consome o orçamento.
Equipes que planejam só a parte técnica entregam a proteção e uma experiência ruim.

### Custo de **não** implementar

O outro lado da conta, e o que costuma faltar na justificativa:

| Item | Ordem de grandeza |
|---|---|
| Investigar "o sistema perdeu meus dados" | 4 a 40 h por incidente, e geralmente sem conclusão |
| Reconciliação manual de dados corrompidos | dias a semanas |
| Perda de confiança do usuário | não quantificável, e demora a voltar |
| Multa/retrabalho em dado regulado (financeiro, saúde) | pode ser a maior linha da tabela |

Um único incidente sério de dados inconsistentes costuma custar mais do que implementar a
proteção no sistema inteiro.

---

## 4. Onde o conflito aparece na fatura

Esta é a seção específica de custo de nuvem, e é onde há surpresas.

### 4.1 DynamoDB — a escrita condicional que falha **também custa**

**Preço em 14/08/2026, região us-east-1, tabela Standard, modo sob demanda:**
**US$ 1,25 por milhão de unidades de requisição de escrita (WRU)** — aproximadamente
**R$ 6,75 por milhão**. Fonte: levantamentos de preço de junho de 2026 (ver rodapé);
confirme na [página oficial de preços do DynamoDB](https://aws.amazon.com/dynamodb/pricing/)
antes de orçar.

Um item de até 1 KB consome 1 WRU; uma escrita condicional consome o mesmo que a não
condicional. **A condicional que falha consome WRU igual.**

Conta de guardanapo, com 10 milhões de escritas por mês numa tabela:

| Taxa de conflito | Escritas cobradas | Custo/mês | Desperdício |
|---|---|---|---|
| 0% | 10,0 mi | ~US$ 12,50 | — |
| 5% | ~10,5 mi | ~US$ 13,16 | US$ 0,66 |
| 30% | ~14,3 mi | ~US$ 17,86 | US$ 5,36 |
| 70% | ~33,3 mi | ~US$ 41,67 | **US$ 29,17** |

Em valores absolutos parece pouco; em tabelas com bilhões de escritas, a mesma proporção vira
dezenas de milhares de dólares. E o número que importa é o **desperdício proporcional**: com
70% de conflito, dois terços da sua fatura de escrita é trabalho jogado fora.

**Economia direta:** use `ReturnValuesOnConditionCheckFailure` (disponível desde 2023). Ele
devolve o item como estava na falha **sem custo adicional de leitura**, poupando um `GetItem`
por conflito.

### 4.2 Outros lugares onde o conflito custa

| Serviço | Como o conflito aparece na conta |
|---|---|
| **Cassandra / ScyllaDB** | *lightweight transactions* (`IF ...`) usam Paxos: 4 idas e voltas em vez de 1. Custo de latência e de capacidade, não item de fatura |
| **Aurora Serverless v2** | retentativas consomem ACU; contenção aumenta ACU consumida |
| **Cloud Functions / Lambda** | você paga por tempo de execução: cada retentativa é tempo faturado |
| **API de terceiro tarifada por chamada** | cada `412` é uma chamada cobrada. Com 3,3 escritas por edição, você paga 3,3× |
| **Egress de rede** | cada retentativa transfere o corpo de novo |
| **Banco gerenciado com IOPS provisionado** | `UPDATE` que afeta zero linhas ainda gasta IOPS de leitura de índice |

**A regra de custo:** em ambiente de nuvem, **taxa de conflito é uma métrica financeira**.
Uma taxa de 30% significa 43% de escritas a mais do que o necessário
(`1/0,7 = 1,43`). Coloque-a no painel de custos, não só no de engenharia.

---

## 5. Custo de acesso ao conhecimento

O que custa para **aprender** o assunto a fundo.

| Recurso | Custo | Alternativa gratuita |
|---|---|---|
| Paper original (Kung & Robinson, ACM DL) | US$ 15–30 avulso, ou assinatura ACM | [cópia aberta hospedada pela CMU](https://www.cs.cmu.edu/~dga/15-712/F07/lectures/12-optimism.pdf) |
| Assinatura ACM Digital Library | ~US$ 99–198/ano (individual) | muitos papers têm pré-print no arXiv ou na página do autor |
| *Designing Data-Intensive Applications*, 2ª ed. (2026) | ~US$ 60–80 impresso · R$ 250–350 no Brasil | capítulos de amostra; [oferta patrocinada pela ScyllaDB](https://lp.scylladb.com/designing-data-intensive-apps-book-offer) já circulou — verifique se ainda vale |
| *Transaction Processing* (Gray & Reuter) | esgotado; usado a US$ 60–150 | bibliotecas universitárias |
| Curso CMU 15-445 | **gratuito** | vídeos, slides e notas públicos |
| Certificação de fornecedor de banco | US$ 100–250 por prova | ver [`85`](85-cursos-e-certificacoes.md) |
| PostgreSQL, Node, SQLite para praticar | **gratuito** | — |

**Custo total mínimo para dominar o assunto: R$ 0,00.** Todo o material essencial —
o paper original, o curso da CMU, a documentação do PostgreSQL, as RFCs, este curso — é
legalmente gratuito. O que se paga é tempo. Ver [`85`](85-cursos-e-certificacoes.md) e
[`90`](90-bibliografia.md).

---

## 6. Comparação: as alternativas e o que cada uma custa

| Estratégia | Custo de implementar | Custo de operar | Custo escondido |
|---|---|---|---|
| **Nada** (ignorar) | zero | zero | corrupção silenciosa de dados |
| **OCC por versão** | baixo | baixo (retentativas) | UX de conflito |
| **Lock pessimista** | baixo | médio (espera, conexões) | deadlock, timeout, conexões presas |
| **`SERIALIZABLE`** | médio (retentativa em todo caminho) | médio a alto | falsos positivos; memória de predicate locks |
| **Fila por chave** | médio a alto | infraestrutura de fila | novo ponto de falha, latência, monitoração |
| **CRDT** | **alto** (muda a arquitetura) | metadados, sincronização | não garante invariante global |
| **Serviço gerenciado de sincronização** | baixo | assinatura mensal | aprisionamento de fornecedor |

**Aprisionamento (vendor lock-in) — onde ele existe de fato:**

- **Baixo:** coluna `version` + `WHERE`. Funciona igual em qualquer banco SQL. É o argumento
  mais forte a favor do OCC manual sobre soluções específicas do fornecedor.
- **Médio:** `rowversion` (SQL Server), `xmin` (PostgreSQL), `@Version` (JPA). Migrar exige
  trabalho, mas o conceito é portátil.
- **Alto:** motores de sincronização gerenciados e formatos proprietários de CRDT. Migrar
  significa reescrever a camada de dados.

---

## 7. Recomendação de custo

1. **Comece medindo.** Uma métrica de conflito custa 4 horas e evita decisões caras baseadas
   em achismo.
2. **A coluna de versão é a opção de menor custo e menor aprisionamento.** Comece por ela,
   sempre.
3. **Orce a interface, não o banco.** A parte técnica é 20% do trabalho.
4. **Em nuvem, trate a taxa de conflito como métrica financeira.**
5. **Não compre nada para aprender este assunto.** Tudo o que importa é gratuito e legal.

---

## Autoteste

1. Existe licença ou patente sobre optimistic locking? Quem financiou o conhecimento?
2. Que cuidado de licença o MySQL exige, e quando ele **não** se aplica?
3. Qual parte da implementação consome mais orçamento, e por quê?
4. No DynamoDB, por que uma escrita condicional que falha custa dinheiro? Como reduzir?
5. Com 30% de conflito, quantas escritas a mais você paga proporcionalmente?
6. Qual estratégia tem o menor aprisionamento de fornecedor? Por quê?
7. Qual é o custo mínimo, em reais, para dominar este assunto?

---

## Fontes consultadas (14/08/2026)

- Preço DynamoDB sob demanda (US$ 1,25 por milhão de WRU, us-east-1, classe Standard):
  levantamentos de [Usage.ai](https://www.usage.ai/blogs/aws/database-savings-plans/dynamodb/on-demand-pricing/),
  [CloudZero](https://www.cloudzero.com/blog/dynamodb-pricing/) e
  [Security Boulevard](https://securityboulevard.com/2026/06/dynamodb-serverless-on-demand-mode-hidden-costs-and-the-complete-2026-pricing-guide/),
  todos de 2026. **Confirme na fonte primária:** <https://aws.amazon.com/dynamodb/pricing/>
- [AWS — DynamoDB reduz o custo de escritas condicionais falhas (2023)](https://aws.amazon.com/about-aws/whats-new/2023/06/amazon-dynamodb-cost-failed-conditional-writes/)
- [AWS Database Blog — tratar erros de escrita condicional sob alta concorrência](https://aws.amazon.com/blogs/database/handle-conditional-write-errors-in-high-concurrency-scenarios-with-amazon-dynamodb/)
- [Hibernate — página de licenças](https://hibernate.org/community/license/)
- [NuGet — Microsoft.EntityFrameworkCore 10.0.11 (MIT)](https://www.nuget.org/packages/microsoft.entityframeworkcore/)
- [Kung & Robinson, ACM TODS 6(2), 1981 — página com paywall](https://dl.acm.org/doi/10.1145/319566.319567) e [cópia aberta na CMU](https://www.cs.cmu.edu/~dga/15-712/F07/lectures/12-optimism.pdf)
- [O'Reilly — *Designing Data-Intensive Applications*, 2ª edição](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/)
