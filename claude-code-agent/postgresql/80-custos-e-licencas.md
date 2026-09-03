# 80 · Custos e licenças

`Nível: todos` · **Preços consultados em 11/08/2026** · `Câmbio: US$ 1 ≈ R$ 5,40 (ordem de grandeza)`

> **Aviso de validade:** preço sem data é desinformação. Todos os valores têm a data de consulta.
> Preços de nuvem mudam com frequência — **confirme na fonte** antes de decidir. Onde não confirmei
> um número exato, o texto diz isso.

---

## 1. A resposta curta

**O PostgreSQL é software livre e gratuito. Não há licença a pagar, nunca, para nenhum uso —
inclusive comercial.** É esta a sua maior vantagem econômica sobre Oracle e SQL Server, que custam
dezenas de milhares de dólares por servidor.

O que custa dinheiro:
- **Hospedagem** — o servidor onde ele roda (VM, container, ou serviço gerenciado).
- **Serviços gerenciados** — pagar para alguém operar o banco por você (RDS, Cloud SQL, Neon…).
- **Suporte comercial** — opcional, de empresas como EDB, Crunchy Data, Percona.
- E, sempre, **o tempo das pessoas** — o maior custo real, e o que ninguém coloca na planilha.

---

## 2. A licença — o que ela permite

O PostgreSQL usa a **PostgreSQL License**, uma licença permissiva estilo BSD/MIT:

| Você pode | Você deve |
|---|---|
| Usar para qualquer fim, inclusive comercial | Manter o aviso de copyright |
| Modificar o código | (nada além disso) |
| Redistribuir, inclusive num produto pago | — |
| Embutir num produto fechado | — |
| **Não pagar nada, nunca** | — |

Não há "edição community vs. enterprise" no PostgreSQL — há **um** PostgreSQL, completo e gratuito.
(Empresas como EDB vendem *distribuições* com ferramentas extras e suporte, mas o núcleo é o mesmo
projeto livre.)

> **Quem paga a conta do que é grátis?** Uma comunidade global de voluntários e empresas
> patrocinadoras (EDB, Crunchy Data, Microsoft, Amazon, Google e muitas outras contribuem código e
> financiamento). Sem dono único, ninguém pode fechar, comprar ou aumentar o preço — a garantia
> mais valiosa para quem constrói sobre ele. Ver [11-historia.md](11-historia.md).

---

## 3. Rodar você mesmo (self-hosted)

O custo é **só a infraestrutura** — o software é grátis.

| Onde | Custo mensal aproximado (11/08/2026) | Bom para |
|---|---|---|
| Sua máquina / homelab | custo de energia | Aprender, projetos pessoais |
| VPS pequena (1–2 GB RAM) | ~US$ 5–12 | Projetos pequenos, dev |
| VM média na nuvem (4 vCPU, 16 GB) | ~US$ 100–200 | Produção pequena/média |
| Servidor dedicado | variável | Alta performance previsível |

Self-hosted é o mais barato em software (zero) e o mais caro em **tempo**: você opera backup,
atualização, tuning, segurança, monitoramento — tudo do [21-administracao-e-operacao.md](21-administracao-e-operacao.md).

---

## 4. Serviços gerenciados — pagar para não operar

Você paga mais em dinheiro para economizar tempo: o provedor cuida de backup, réplicas,
atualização, alta disponibilidade. **Valores são ordens de grandeza, consultados em 11/08/2026 —
confirme na calculadora de cada um.**

| Serviço | Modelo | Camada gratuita | Observação |
|---|---|---|---|
| **Neon** | Serverless, por uso; escala a zero | **Sim, permanente** (~0,5 GB, ~100h compute/mês) | Adquirido pela Databricks; branching; ótimo para dev e cargas variáveis |
| **Supabase** | Instância + extras (auth, storage); | **Sim** (pausa após inatividade) | Pago a partir de ~US$ 25/mês; "Firebase sobre Postgres" |
| **AWS RDS for PostgreSQL** | Por hora da instância + storage + I/O | 12 meses limitados | O padrão corporativo; ex.: ~US$ 100–150/mês numa instância média |
| **AWS Aurora PostgreSQL** | Armazenamento reescrito, escala | — | Mais caro por unidade; escala e HA melhores |
| **Google Cloud SQL** | Por instância + storage | crédito inicial | Integrado ao GCP |
| **Google AlloyDB** | Postgres turbinado para analytics/IA | — | Mais caro; HTAP |
| **Azure Database for PostgreSQL** | Por instância | crédito inicial | Inclui a variante distribuída (Citus) |
| **DigitalOcean / Render / Railway** | Instância gerenciada simples | limitada | Bom custo-benefício para pequenos |

### Serverless (Neon) vs. instância dedicada (RDS)

| | Serverless (Neon) | Instância dedicada (RDS/VM) |
|---|---|---|
| Cobrança | Por uso; **zero quando ocioso** | Por hora, mesmo ocioso |
| Provisionamento | Instantâneo | Minutos |
| Branching (cópia instantânea) | Sim | Não |
| Melhor para | Dev, preview, cargas variáveis | Carga constante 24/7 |
| Risco de custo | Picos de uso | Ociosidade paga |

> **A conta que decide:** para **carga constante alta 24/7**, uma instância reservada costuma ser
> mais barata por unidade. Para **dev, cargas intermitentes e ambientes de teste**, serverless
> (escala a zero) evita pagar pela ociosidade e pode ser dramaticamente mais barato. Faça a conta
> com o **seu** perfil de carga, não com o preço de tabela. Ver [65-estado-da-arte.md](65-estado-da-arte.md).

### O custo escondido dos gerenciados: egress e I/O

Além da instância e do storage, os provedores de nuvem cobram:
- **Transferência de saída (egress)** — dados saindo da nuvem. Surpreende em cargas de leitura
  intensa de fora.
- **I/O** (em alguns tipos de storage do RDS) — cada operação conta.
- **Backups além da cota**, réplicas, snapshots.
- **Sair do provedor** (*vendor lock-in*) — migrar TB de dados custa tempo e egress. O protocolo
  aberto do PostgreSQL ajuda (você pode `pg_dump` e levar embora), mas o esforço é real.

---

## 5. Suporte comercial (opcional)

O PostgreSQL não tem uma empresa dona, mas várias oferecem suporte pago para quem quer um SLA:

| Empresa | Oferta |
|---|---|
| **EDB** (EnterpriseDB) | Distribuição, ferramentas, suporte, TDE, Oracle-compat |
| **Crunchy Data** | Suporte, Postgres para Kubernetes, gerenciado |
| **Percona** | Suporte multi-banco, ferramentas open source |
| **Cybertec, 2ndQuadrant (parte da EDB), Fujitsu** | Consultoria e suporte |

Faz sentido para empresas que rodam Postgres crítico e querem alguém para chamar às 3 da manhã — o
que, para self-hosted sério, costuma valer o custo.

---

## 6. Comparação com os concorrentes pagos

Onde o "grátis" do PostgreSQL vira economia direta:

| Banco | Licença | Custo típico |
|---|---|---|
| **PostgreSQL** | PostgreSQL License (livre) | **US$ 0** de licença |
| **Oracle Database** | Proprietária | Dezenas de milhares de US$/processador + suporte anual |
| **SQL Server** | Proprietária (Microsoft) | Milhares de US$ por core; edições Express/Developer grátis com limites |
| **MySQL** | GPL / comercial (Oracle) | Grátis (GPL), mas com dono; MariaDB é o fork livre |
| **SQLite** | Domínio público | Grátis (mas é embutido, não cliente-servidor) |

*Interpretação:* migrar de Oracle/SQL Server para PostgreSQL é uma das economias de licença mais
comuns e maiores em TI — governos e grandes empresas fazem isso continuamente. O custo da migração
(reescrever SQL específico, PL/SQL → PL/pgSQL, testar) é real, mas se paga rápido contra licenças de
seis dígitos. Ferramentas de compatibilidade (EDB, ora2pg) ajudam.

---

## 7. Cenários de custo, do zero ao corporativo

| Cenário | Configuração | Custo mensal aproximado |
|---|---|---|
| **Aprendiz** | Local / Neon grátis / DB Fiddle | **US$ 0** |
| **Projeto pessoal** | VPS US$ 5 self-hosted, ou Neon grátis | **US$ 0–5** |
| **Startup (dev + prod pequena)** | Neon/Supabase, escala com uso | **baixo, cresce com uso** |
| **App em produção** | RDS instância média + réplica | **~US$ 200–400** + tempo |
| **Empresa (crítico)** | HA gerenciado ou self-hosted + suporte EDB | **instância + suporte + equipe** |
| **Migração de Oracle** | PostgreSQL + custo único de migração | **economia de 5–6 dígitos/ano em licença** |

---

## 8. Como não gastar à toa

1. **Aprenda de graça** — local ou Neon grátis. Zero custo para dominar o banco.
2. **Self-hosted é barato em software, caro em tempo.** Pese o valor do seu tempo.
3. **Serverless para cargas variáveis; reservado para constantes.** Faça a conta.
4. **Cuidado com egress** — mantenha o banco perto de quem o consome.
5. **Dimensione, não superprovisione.** Comece pequeno; escale por evidência (métricas), não por
   medo.
6. **Réplicas de leitura antes de sharding.** Escalar vertical + réplicas resolve quase tudo, mais
   barato que distribuir.
7. **Se vem de Oracle/SQL Server, calcule a economia de licença** — costuma justificar a migração.

---

## Autoteste

1. O PostgreSQL custa licença? Para uso comercial também?
2. O que a PostgreSQL License permite, e o que ela exige em troca?
3. Quem "paga a conta" do desenvolvimento do PostgreSQL?
4. Self-hosted é grátis em software — então onde está o custo?
5. Quando serverless (Neon) sai mais barato que instância dedicada, e quando sai mais caro?
6. Cite três custos escondidos dos serviços gerenciados na nuvem.
7. Por que migrar de Oracle para PostgreSQL é uma economia comum, e qual é o custo dessa migração?
8. Quando faz sentido pagar por suporte comercial de PostgreSQL?
9. Qual é a diferença de custo de licença entre PostgreSQL e Oracle, em ordem de grandeza?
10. Cite três formas concretas de não gastar à toa com PostgreSQL na nuvem.

---

### Fontes consultadas (11/08/2026)

- [PostgreSQL — License](https://www.postgresql.org/about/licence/) — a PostgreSQL License
- [Bytebase — PostgreSQL Hosting Options 2026: Pricing Comparison](https://www.bytebase.com/blog/postgres-hosting-options-pricing-comparison/) e [Managed PostgreSQL Comparison 2026 — selfhost.dev](https://selfhost.dev/blog/managed-postgresql-comparison-2026/) — **secundárias**, faixas de preço
- [Neon Serverless Postgres Pricing 2026 — Simplyblock](https://vela.simplyblock.io/articles/neon-serverless-postgres-pricing-2026/) — camada gratuita, modelo de uso
- Calculadoras oficiais de AWS RDS, Google Cloud SQL e Azure — **ordens de grandeza; confirmar na fonte antes de decidir**
