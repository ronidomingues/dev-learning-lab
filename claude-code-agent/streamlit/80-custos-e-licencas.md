# 80 · Custos e licenças

> **Nível:** todos
> **Data da consulta de preços: 02/09/2026.** Preço sem data é desinformação.
> **Câmbio usado: US$ 1,00 = R$ 5,16** (USD/BRL em 02/09/2026; oscilou entre
> 5,14 e 5,22 na semana anterior). Os valores em reais são **ordem de grandeza**,
> não cotação: confira antes de orçar.
> Preços de nuvem mudam sem aviso. **Confirme no site do fornecedor.**

---

## 1. O Streamlit em si é **gratuito**

**Licença: Apache 2.0.** Verificado nos metadados do pacote 1.63.0 instalado
(`License-Expression: Apache-2.0`).

O que a Apache 2.0 permite, sem pagar nada e sem pedir permissão:

- uso comercial, inclusive em produto pago;
- modificação e distribuição;
- uso privado, sem publicar suas mudanças;
- **concessão explícita de patentes** dos contribuidores (é o que a MIT não tem, e
  é a razão de departamentos jurídicos preferirem Apache 2.0).

O que ela exige:

- manter o aviso de copyright e a cópia da licença;
- indicar as mudanças significativas, se você distribuir uma versão modificada.

O que ela **não** exige:

- abrir o seu código (não é copyleft, diferente da GPL);
- pagar royalty;
- pedir autorização.

**Conclusão prática:** você pode construir e vender um produto sobre Streamlit
sem dever nada a ninguém.

### Quem paga a conta, então?

A **Snowflake**, que comprou a empresa em março de 2022 por cerca de US$ 800
milhões. O retorno vem de *Streamlit in Snowflake*: quando a sua app roda dentro
do armazém de dados deles, a computação é cobrada em créditos. O projeto aberto é
o funil.

**Isso é sustentável?** É o mesmo modelo do Power BI para a Microsoft e do VS Code
(gratuito, vende nuvem). Enquanto o Streamlit trouxer clientes para o Snowflake,
ele é investimento, não custo. O risco não é o código fechar — é o roteiro
priorizar o que serve ao produto pago. Ver
[65-estado-da-arte.md](65-estado-da-arte.md).

---

## 2. Licença das dependências

Verificado no pacote 1.63.0:

| Dependência | Licença | Comercial? |
|---|---|---|
| pandas, numpy, pyarrow | BSD-3 / Apache 2.0 | sim |
| altair | BSD-3 | sim |
| starlette, uvicorn, anyio | BSD-3 / MIT | sim |
| protobuf | BSD-3 | sim |
| pillow | MIT-CMU | sim |
| **plotly** (opcional) | MIT | sim |
| **matplotlib** (opcional) | licença própria, estilo BSD | sim |
| **SQLAlchemy** (extra `sql`) | MIT | sim |
| **Authlib** (extra `auth`) | **BSD-3**, com licença comercial opcional para uso avançado | conferir |

**Um cuidado com componentes da comunidade:** `streamlit-aggrid` embute o AG Grid,
cuja versão **Enterprise é paga**. A Community serve para a maioria dos casos, mas
usar um recurso Enterprise sem licença é violação. Confira antes.

**Auditoria automática:**

```bash
pip install pip-licenses && pip-licenses --format=markdown
pip install pip-audit && pip-audit
```

---

## 3. Hospedagem — a tabela de custos (02/09/2026)

| Opção | Preço | Em reais (aprox.) | Cartão? | Serve para |
|---|---|---|---|---|
| **Streamlit Community Cloud** | **grátis** | — | não | protótipo, portfólio, uso interno leve |
| **Hugging Face Spaces** (CPU básico) | **grátis** | — | não | demonstração de modelo |
| **GitHub Codespaces** | 60 h/mês grátis | — | não | desenvolvimento |
| **Hetzner CX23 / CPX22** | € 5,49 / € 7,99 por mês | ~R$ 33 / R$ 49 | sim | **o melhor custo-benefício** |
| **DigitalOcean Droplet** (2 vCPU/2 GB) | US$ 18/mês | ~R$ 93 | sim | quando quer interface simples |
| **Render Starter** (0,5 CPU/512 MB) | US$ 7/mês | ~R$ 36 | sim | app pequeno, deploy fácil |
| **Render Standard** (1 CPU/2 GB) | US$ 25/mês | ~R$ 129 | sim | app de produção pequeno |
| **Railway Hobby** | US$ 5/mês + uso | ~R$ 26 + uso | sim | cobrança por segundo |
| **Fly.io** | só uso, por segundo | variável | sim | sem plano fixo desde out/2024 |
| **Google Cloud Run** | por uso; camada gratuita mensal | variável | sim | tráfego irregular |
| **Streamlit in Snowflake** | créditos Snowflake | ver abaixo | sim | quando os dados já estão lá |

**Recomendação, e é opinião:** para painel interno de empresa, uma VPS Hetzner de
~€ 8/mês com Docker e nginx atende dezenas de usuários e custa menos que uma
assinatura de streaming. Se você não quer administrar servidor, Render Standard.

**Um alerta sobre PaaS com hibernação:** planos gratuitos que "dormem" após 15
minutos são péssimos para painel — o primeiro acesso do dia leva ~1 minuto, e o
usuário conclui que está quebrado.

---

## 4. Streamlit Community Cloud: onde a camada gratuita acaba

**É gratuito de verdade, sem cartão.** E tem limites duros (verificados na
documentação e nos canais oficiais em 02/09/2026):

| Limite | Valor |
|---|---|
| Memória | **~1 GB** por app |
| Hibernação | após **12 h** sem tráfego (qualquer visitante acorda) |
| Apps públicos | ilimitados |
| **Apps privados** | **1** |
| Domínio próprio | não |
| Região | **Estados Unidos**, sem opção |
| Atualizações do GitHub | 5 por minuto |
| Repositório | precisa ser **GitHub** |

**Onde ela acaba, na prática:**

1. **1 GB de memória.** Um DataFrame de 300 MB, em cache, com três entradas,
   estoura. É a causa de "This app has gone over its resource limits".
2. **Um app privado.** Duas ferramentas internas já não cabem.
3. **Região nos EUA.** Para dado pessoal de brasileiro, isso exige base legal e
   salvaguardas de transferência internacional sob a LGPD. Frequentemente é
   impeditivo.
4. **Hibernação.** Painel que alguém abre uma vez por semana estará sempre
   dormindo.

---

## 5. Streamlit in Snowflake: quanto custa

Não há preço "do Streamlit". Você paga a **computação do Snowflake**, em créditos.

Ordem de grandeza (AWS, região US East, sob demanda, 02/09/2026 — **confirme**,
porque varia por edição, região e provedor):

| Edição | US$ por crédito (aprox.) |
|---|---|
| Standard | ~2 |
| Enterprise | ~3 |
| Business Critical | ~4 |

Consumo de um *warehouse*: **X-Small 1 crédito/h**, Small 2, Medium 4, Large 8 —
dobrando a cada tamanho. Cobrança **por segundo**, com mínimo de 60 segundos a
cada vez que o warehouse acorda.

**Conta de exemplo** (X-Small, Standard, ~US$ 2/crédito):

| Uso | Horas/mês | Custo |
|---|---|---|
| 1 usuário, 2 h/dia útil | ~44 h | ~US$ 88 (~R$ 454) |
| 5 usuários, 2 h/dia útil, mesmo warehouse | ~44 h | ~US$ 88 |
| aberto o dia todo, todo dia útil | ~176 h | ~US$ 352 (~R$ 1.816) |

**O detalhe que estoura orçamento:** o warehouse fica ligado enquanto houver
sessão ativa. Uma aba esquecida aberta **mantém a computação ligada**. Configure
`AUTO_SUSPEND` agressivo (60 s) e monitore.

**A novidade de 2026:** desde 09/03/2026, o *container runtime* (Snowpark
Container Services) está em disponibilidade geral — com GPU, pacotes Python
amplos e **sem hibernação**. "Sem hibernação" também significa "sem parar de
cobrar". Leia com atenção.

---

## 6. Os custos ocultos

Onde o orçamento estoura de verdade:

| Custo | Ordem de grandeza | Como evitar |
|---|---|---|
| **Tráfego de saída** (egress) | AWS/GCP ~US$ 0,09/GB; Hetzner inclui 20 TB | Hetzner, ou cache no navegador |
| **Consultas ao banco** | por consulta no BigQuery; por segundo no Snowflake | cache com TTL — reduz 10× a 100× |
| **`run_every` esquecido** | multiplica consultas por usuário conectado | TTL de cache; intervalos maiores |
| **Aba esquecida aberta** | mantém sessão, memória e (em SiS) computação | `disconnectedSessionTTL`; `AUTO_SUSPEND` |
| **Sua hora de manutenção** | **o maior de todos** | testes e arquitetura em camadas |
| **Migrar depois** | reescrever a app | separe `nucleo/` desde o início |
| **Componente comercial** | AG Grid Enterprise etc. | verifique a licença antes |
| **Certificado TLS** | Let's Encrypt é grátis | automatize a renovação |
| **Observabilidade** | Datadog cobra por host e por GB de log | Prometheus + Grafana, ou Loki |

**Sobre o maior custo de todos:** um painel malfeito consome horas de manutenção
todo mês. Quatro horas mensais de uma pessoa custam mais que qualquer VPS do
mundo. É o argumento econômico para arquitetura e testes.

---

## 7. Aprisionamento de fornecedor

**Streamlit puro: risco baixo.** É uma biblioteca Python sob Apache 2.0. Sai daqui
e roda em qualquer lugar.

**Community Cloud: risco baixo.** O código está no seu GitHub; migrar para um
contêiner é meia hora.

**Streamlit in Snowflake: risco médio.** A app pode usar `SnowflakeConnection`,
*caller's rights*, e integração com objetos do Snowflake. Sair exige reescrever a
camada de dados — que é exatamente o `nucleo/repositorio.py` se você seguiu
[23-arquitetura-de-app-real.md](23-arquitetura-de-app-real.md).

**Componentes da comunidade: risco variável.** Um componente abandonado que quebra
numa atualização do Streamlit é um problema real, e a saída é reescrever aquela
tela.

---

## 8. Alternativas gratuitas, e o que se perde

| Em vez de | Use | O que se perde |
|---|---|---|
| Streamlit Community Cloud | VPS + Docker | conveniência; ganha memória, região e privacidade |
| Snowflake | PostgreSQL | escala massiva; ganha custo previsível |
| Datadog | Prometheus + Grafana + Loki | integração pronta; ganha custo zero de licença |
| AG Grid Enterprise | `st.dataframe` + `st.pagination` | pivot e agrupamento avançados |
| Auth0 | Keycloak autogerido | um serviço a menos; ganha um servidor a mais para cuidar |
| Docker Desktop (empresa grande) | Podman, Rancher Desktop, ou Docker Engine no WSL2 | interface gráfica |

---

## 9. Três orçamentos reais

**A · Painel interno, 20 pessoas, dados em PostgreSQL já existente**

| Item | Mensal |
|---|---|
| VPS Hetzner CPX22 (2 vCPU / 4 GB) | € 7,99 (~R$ 49) |
| Domínio (rateado) | ~R$ 5 |
| TLS (Let's Encrypt) | R$ 0 |
| **Total** | **~R$ 54/mês** |

**B · Portfólio público**

| Item | Mensal |
|---|---|
| Community Cloud | R$ 0 |
| **Total** | **R$ 0** |

**C · Ferramenta interna com login, 100 pessoas, alta disponibilidade**

| Item | Mensal |
|---|---|
| 2 VPS (4 GB cada) | ~R$ 100 |
| PostgreSQL gerenciado | ~R$ 80 a 250 |
| Backup em objeto | ~R$ 10 |
| Monitoramento (autogerido) | R$ 0 (+ a VPS) |
| **Total** | **~R$ 200 a 400/mês** |

Para comparação: uma licença de BI comercial por usuário costuma custar entre
US$ 10 e US$ 30 por pessoa por mês. Com 100 pessoas, isso é US$ 1.000 a 3.000
mensais — de 15 a 75 vezes o orçamento C. É o argumento econômico mais forte a
favor de uma app própria, e a contrapartida é que a manutenção é sua.

---

## 10. Checklist de custo antes de subir

- [ ] Sei quantos usuários simultâneos, não só cadastrados.
- [ ] Estimei a memória por sessão (medida, não chutada).
- [ ] Todo cache tem TTL, e todo `run_every` tem a conta feita.
- [ ] Sei o custo por consulta do meu banco.
- [ ] Verifiquei a licença de cada componente de terceiro.
- [ ] Sei em que país o dado vai ficar.
- [ ] Tenho alerta de custo configurado no provedor.
- [ ] Considerei o custo da minha hora de manutenção.

---

## Autoteste

1. Qual é a licença do Streamlit e o que ela permite e exige? Qual é a diferença
   relevante para a MIT?
2. Quem paga a conta do Streamlit gratuito, e por qual mecanismo?
3. Cite quatro limites do Community Cloud e diga onde cada um "acaba" na prática.
4. Por que a região do Community Cloud pode ser impeditiva no Brasil?
5. Como se calcula o custo de *Streamlit in Snowflake*? Que detalhe estoura o
   orçamento?
6. Cite cinco custos ocultos e como evitar cada um.
7. Qual é o maior custo de todos, e qual é o argumento econômico que ele produz?
8. Compare o orçamento C com uma licença de BI por usuário. Qual é a contrapartida?

---

## Fontes consultadas (02/09/2026)

- Metadados do pacote `streamlit` 1.63.0 (licença, dependências) — verificação local
- Documentação do Streamlit Community Cloud e canais oficiais — <https://docs.streamlit.io/deploy/streamlit-community-cloud>
- Preço de créditos e tamanhos de warehouse do Snowflake — guias de preço de 2026
  (Flexera, Revefi) e documentação da Snowflake
- Snowflake, *SiS container runtime GA* (09/03/2026) — <https://docs.snowflake.com/en/release-notes/2026/other/2026-03-09-sis-container-runtime-ga>
- Comparativos de preço Render / Railway / Fly.io (2026) — hostim.dev, render.com/articles
- Comparativos Hetzner / DigitalOcean (2026) — betterstack.com, apicalculators.com
- Câmbio USD/BRL em 02/09/2026 — Investing.com / TradingView
