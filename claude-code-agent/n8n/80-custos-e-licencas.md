# 80 · Custos e licenças

`Nível: todos` · **Preços consultados em 01/09/2026** · Câmbio do mesmo dia: **€ 1 ≈ R$ 6,01** · **US$ 1 ≈ R$ 5,16**

> **Preço sem data é desinformação.** Tudo aqui vale para 01/09/2026. Confira antes
> de decidir; a n8n reajusta e reestrutura planos com frequência.

---

## 1. A resposta curta

- **Autogerido:** o software é **gratuito**, sem limite de execuções, sem cartão de
  crédito. Você paga servidor e o seu tempo.
- **n8n Cloud:** a partir de **€ 20/mês** (≈ **R$ 120/mês**) no plano anual.
- **A licença não é open source.** É *fair-code*: uso interno da sua empresa, sim;
  hospedar fluxos **de clientes** ou embutir no seu produto, **não** sem contrato.

Se você parar de ler aqui, leia ao menos a [seção 4](#4-a-licença-sustainable-use-license).

---

## 2. n8n Cloud — planos e preços

Consultado em [n8n.io/pricing](https://n8n.io/pricing/) em **01/09/2026**.
O preço é em **euros** e cobrado por **execução de workflow** (não por passo — uma
execução com 40 nós conta como **uma**, e essa é uma diferença importante frente ao
Zapier).

| Plano | Preço/mês (anual) | ≈ BRL/mês | Execuções/mês | Simultâneas | Projetos | Destaques |
|---|---|---|---|---|---|---|
| **Starter** | € 20 | ≈ R$ 120 | 2.500 | 5 | 1 | usuários ilimitados, ~2.300 créditos de IA/mês, suporte por fórum |
| **Pro** | € 50 | ≈ R$ 300 | 10.000 | 20 | 3 | papéis de admin, insights de 7 dias, histórico de workflow, até ~13.700 créditos de IA |
| **Business** | € 667 | ≈ R$ 4.010 | 40.000 | — | 6 | **SSO/SAML/LDAP**, insights de 30 dias, **opção autogerida**, controle de versão por Git |
| **Enterprise** | sob consulta | — | sob medida | 200+ | ilimitados | insights de 365 dias, suporte com SLA, cofre externo de segredos |

Notas verificadas:

- A cobrança mensal é ~20% mais cara; o anual economiza cerca de **17%**.
- **Usuários, workflows e passos por workflow são ilimitados em todos os planos.**
  O que escala o preço é **execução**.
- Teste gratuito de Starter/Pro **sem cartão**; o teste de Business exige cartão e
  dura 14 dias.
- Reportagens de compradores em 2026 situam o Enterprise entre **US$ 2.000 e
  US$ 3.000/mês** (≈ R$ 10.300 a R$ 15.500). É estimativa de terceiros, **não** preço
  oficial — trate como ordem de grandeza.

### O salto Pro → Business

De € 50 para € 667 é **13×** o preço para 4× as execuções. Você não está comprando
execuções: está comprando **SSO, governança e a opção autogerida licenciada**.
Se você precisa de SSO, esse é o preço. Se não precisa, o salto é difícil de
justificar — e é exatamente o ponto onde a maioria migra para autogestão.

---

## 3. Autogerido — o custo real

O software é gratuito. A conta é outra:

| Item | Custo típico/mês | Observação |
|---|---|---|
| VPS pequeno (2 vCPU, 4 GB) | US$ 10–20 ≈ **R$ 52–103** | Hetzner é o mais barato; DigitalOcean/Contabo próximos |
| VPS de produção (4 vCPU, 8 GB) | US$ 25–50 ≈ **R$ 129–258** | |
| Postgres gerenciado (opcional) | US$ 15–50 ≈ **R$ 77–258** | Ou no mesmo VPS, de graça |
| Backup externo (S3/Backblaze) | US$ 1–5 ≈ **R$ 5–26** | |
| Domínio | ~R$ 40/**ano** | |
| TLS (Let's Encrypt) | **R$ 0** | |
| Monitoramento | R$ 0–50 | Uptime Kuma autogerido é gratuito |
| **Total de infraestrutura** | **≈ R$ 60 a R$ 400/mês** | |
| **O seu tempo** | **2 a 6 h/mês** | Atualizar, monitorar, apagar fogo |

**A linha que decide.** Se a sua hora vale R$ 100 e você gasta 4 h/mês, são
R$ 400/mês de custo invisível — mais que qualquer plano Pro. Autogerir compensa
quando:

1. Os dados **não podem** sair da sua infraestrutura (o motivo mais comum e o mais legítimo).
2. O volume é alto (dezenas de milhares de execuções/mês).
3. Você precisa de módulos externos, Python com bibliotecas, ou controle fino.
4. Você já opera servidores e o custo marginal de mais um é pequeno.

**Não compensa** se você tem menos de 2.500 execuções/mês, não tem restrição de
dados e ninguém no time gosta de operar servidor. Nesse caso, € 20/mês é barato.

### Custos ocultos do autogerido

| Custo oculto | Como aparece |
|---|---|
| **Crescimento do banco** | Sem poda, o disco enche e você paga upgrade — ou fica fora do ar |
| **Atualizações** | Uma versão menor quase toda semana; alguém precisa acompanhar |
| **Migração 1.x→2.0 e 2.x→3.0** | Trabalho real, com quebras ([23](23-ciclo-de-vida-e-versionamento.md)) |
| **RBAC ausente** | Ou você licencia, ou opera **N instâncias** (custo × N) |
| **Docker Desktop em empresa** | Licença paga acima do porte definido pela Docker Inc. — Docker Engine no Linux e Colima são gratuitos |
| **APIs de terceiros** | Não são do n8n, mas entram na conta do projeto |
| **LLM** | Pode facilmente superar tudo o mais somado ([24](24-ia-e-agentes.md#9-custo-e-observabilidade)) |

---

## 4. A licença: Sustainable Use License

**O n8n não é open source pela definição da OSI.** Ele é *fair-code*, sob a
**Sustainable Use License, versão 1.0**. Trecho central, do `LICENSE.md` do
repositório oficial:

> *"You may use or modify the software only for your own internal business purposes
> or for non-commercial or personal use. You may distribute the software or provide
> it to others only if you do so free of charge for non-commercial purposes."*

Em português: **use e modifique à vontade para fins internos do seu negócio ou uso
pessoal; distribua apenas gratuitamente e para fins não comerciais.**

Além disso, no mesmo arquivo:

- Arquivos com **`.ee.` no nome ou `.ee` no diretório** **não** estão sob essa
  licença — exigem licença Enterprise (ficam sob `LICENSE_EE.md`).
- Branches diferentes de `master` **não são licenciadas**.
- O GitHub classifica a licença do repositório como **"Other"** — não como uma
  licença aberta reconhecida.

### O que você PODE fazer

| Cenário | Pode? |
|---|---|
| Rodar n8n na sua empresa, para processos internos | ✅ |
| Modificar o código para uso interno | ✅ |
| Rodar num SaaS **seu**, usando **suas** credenciais, processando webhooks do seu produto | ✅ (uso interno) |
| **Prestar consultoria** construindo fluxos n8n para clientes | ✅ — não é preciso acordo de licença separado |
| Distribuir sua versão modificada, de graça e sem fim comercial, mantendo os avisos | ✅ |

### O que você NÃO pode sem licença comercial

| Cenário | Precisa |
|---|---|
| Hospedar fluxos e **credenciais dos seus clientes** na sua instância | **Licença Enterprise** |
| Oferecer "n8n gerenciado" como produto | **Licença Enterprise** |
| **Embutir** o n8n dentro do seu produto (OEM), com sua marca | **Licença de Embed** — parceria comercial, normalmente com valor anual relevante e/ou participação na receita |
| Usar os arquivos `.ee.` | **Licença Enterprise** |

> **A linha divisória, na prática:** *de quem são as credenciais que passam pela
> instância?* Se são **suas**, é uso interno. Se são **dos seus clientes**, é
> comercial. É essa a pergunta que determina o lado da linha.

> **Aviso honesto:** isto é interpretação técnica, não parecer jurídico. Se você vai
> construir um negócio em cima do n8n, **fale com a n8n e com um advogado antes**,
> não depois. Já vi produto pronto descobrir a restrição na véspera do lançamento.

### Por que a licença é assim

Trade-off econômico explícito, e o precedente é conhecido: com licença OSI, um
provedor de nuvem grande pega o código, vende como serviço gerenciado e quem
escreveu não vê nada. Foi o que motivou Elasticsearch, MongoDB e Redis a trocarem
de licença. A Sustainable Use License bloqueia esse caso específico e deixa o resto
aberto. É defensável — e tem o custo de não ser open source.

---

## 5. Recursos por edição (o que é pago)

| Recurso | Community (gratuito) | Pago |
|---|---|---|
| Workflows, nós, execuções | ✅ ilimitado | |
| Todos os nós, inclusive IA | ✅ | |
| API pública | ✅ | |
| Queue mode, workers | ✅ | |
| Data tables | ✅ (200 MiB por padrão) | |
| MFA, verificação de e-mail | ✅ | |
| Auditoria por CLI (`n8n audit`) | ✅ | |
| **Rastreamento LangSmith (autogerido)** | ✅ **todas as edições** | ❌ não existe no Cloud |
| **RBAC, projetos, permissões** | ❌ | ✅ |
| **SSO SAML/OIDC, LDAP** | ❌ | ✅ Enterprise |
| **Source control (Git) e ambientes** | ❌ | ✅ |
| **Variáveis (`$vars`)** | ❌ | ✅ |
| **Cofre externo de segredos** | ❌ | ✅ Enterprise |
| **Log streaming / log de auditoria** | ❌ | ✅ Enterprise |
| **Multi-main (alta disponibilidade)** | ❌ | ✅ Enterprise |
| **Armazenamento externo de binário (S3)** | ❌ | ✅ |
| **Ver workers na interface** | ❌ | ✅ Enterprise |

**O que dói mais no gratuito, em ordem:** RBAC, source control e variáveis por
ambiente. As três juntas são o que faz uma empresa com vários times licenciar.

---

## 6. Comparação de custo com os concorrentes

Cenário: **10.000 operações por mês**, preços de 01/09/2026 (os de terceiros são
ordens de grandeza — confirme na fonte).

| Ferramenta | Unidade cobrada | Custo aproximado/mês | Observação |
|---|---|---|---|
| **n8n Cloud Pro** | **execução** (fluxo inteiro) | € 50 ≈ **R$ 300** | 40 nós = 1 execução |
| **n8n autogerido** | — | **R$ 60–400** (infra) | + seu tempo |
| **Zapier** | **task** (cada passo!) | tipicamente **US$ 100–300+** | 10 mil execuções de 5 passos = **50 mil tasks** |
| **Make** | **operação** (cada passo) | dezenas de dólares | Mais barato que Zapier no volume |
| **Power Automate** | por usuário ou por fluxo | US$ 15/usuário/mês | Faz sentido se você já paga M365 |

> **A diferença estrutural que decide muita coisa:** o n8n cobra por **execução**;
> Zapier e Make cobram por **passo**. Quanto mais complexo o fluxo, maior a
> vantagem do n8n. Um fluxo de 30 passos rodando 5.000 vezes: 5.000 execuções no
> n8n, **150.000 tasks** no Zapier. Não é uma diferença de percentual; é de ordem
> de grandeza.

---

## 7. Alternativas gratuitas e abertas de verdade

Se a licença fair-code é um problema para o seu caso:

| Ferramenta | Licença | O que você ganha | O que perde |
|---|---|---|---|
| **Activepieces** | MIT (partes) | Licença mais permissiva, interface parecida | Muito menos integrações e comunidade |
| **Windmill** | AGPLv3 | Rápido, *code-first* (TS/Python), ótimo para quem programa | Menos "visual"; público diferente |
| **Apache Airflow** | Apache 2.0 | Padrão de engenharia de dados, maduríssimo | Não é integração de apps; exige Python e engenheiro |
| **Temporal** | MIT | Garantias de durabilidade muito superiores ([60](60-teoria-avancada.md#8-comparação-formal-com-airflow-e-temporal)) | Sem editor visual; exige código determinístico |
| **Huginn** | MIT | Veterano, leve | Interface datada, comunidade pequena |
| **Node-RED** | Apache 2.0 | Excelente em IoT e eventos | Fraco em integrações SaaS |
| **Dify / Langflow** | abertas | Focadas em IA/agentes, > 100 mil estrelas cada | Não são ferramentas de integração geral |

**Recomendação honesta:** para 90% dos casos internos de empresa, a Sustainable Use
License **não atrapalha em nada** — você está no lado permitido da linha. Trocar de
ferramenta por causa dela só faz sentido se o seu produto **é** a automação.

---

## 8. Quem paga a conta do n8n gratuito

Pergunta legítima. A resposta: **capital de risco e clientes corporativos.**
US$ 240 milhões captados até a Série C de outubro de 2025 (avaliação de US$ 2,5 bi).
O gratuito é o funil: adoção → dependência → necessidade de RBAC, SSO e suporte →
licença.

**O que isso significa para você:** o produto gratuito continuará bom, porque ele é
a estratégia de distribuição. E os recursos de **governança** continuarão pagos,
porque são a estratégia de receita. Planeje com essa divisão em mente — ela não vai
mudar.

---

## Autoteste

1. Quanto custa o plano Starter do n8n Cloud, em euros e em reais, e em que data?
2. Qual é a unidade de cobrança do n8n? E a do Zapier? Por que isso muda tudo?
3. Um fluxo de 30 passos rodando 5.000 vezes: quantas unidades em cada ferramenta?
4. Qual o custo real mensal de autogerir, incluindo o invisível?
5. Cite três situações em que autogerir compensa e uma em que não.
6. O n8n é open source? Cite o nome exato da licença e a restrição central.
7. Qual é a pergunta que determina se o seu uso é interno ou comercial?
8. Consultoria construindo fluxos para clientes precisa de licença especial?
9. Cite os três recursos licenciados que mais doem na edição gratuita.
10. Quem paga a conta do n8n gratuito, e o que isso implica sobre o futuro?

---

*Fontes consultadas em 01/09/2026: [n8n.io/pricing](https://n8n.io/pricing/),
[n8n LICENSE.md](https://github.com/n8n-io/n8n/blob/master/LICENSE.md),
[docs.n8n.io — Choose how to use n8n](https://docs.n8n.io/choose-how-to-use-n8n.md),
[PitchBook — Série C](https://pitchbook.com/news/articles/ai-agent-startup-n8n-lands-2-5b-valuation-with-180m-series-c).
Câmbio de 01/09/2026 (≈ € 1 = R$ 6,01; US$ 1 = R$ 5,16) via cotações de mercado —
use como ordem de grandeza, não para orçamento.*

*Anterior: [75-armadilhas.md](75-armadilhas.md) · Próximo: [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md)*
