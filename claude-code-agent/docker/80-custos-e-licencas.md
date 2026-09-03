# 80 · Custos e licenças

`Nível: todos` · **Preços consultados em 11/08/2026** · `Câmbio usado: US$ 1 ≈ R$ 5,40 (ordem de grandeza)`

> **Aviso de validade:** preço sem data é desinformação. Todos os valores abaixo têm a data de
> consulta explícita. Preços de nuvem e de assinatura mudam com frequência — **confirme na
> fonte** antes de decidir. Onde não confirmei um número exato, o texto diz isso.

---

## 1. A resposta curta

**O Docker Engine é gratuito e software livre (Apache 2.0). Rodar containers não custa licença.**

O que custa dinheiro é:
- o **Docker Desktop** em empresas grandes (o app, não o Engine);
- **pulls** acima do limite no Docker Hub;
- **armazenamento e tráfego** em registries de nuvem;
- **imagens base endurecidas** comerciais (opcional);
- e, sempre, **o tempo das pessoas** — que é o maior custo real, e o que ninguém coloca na
  planilha.

---

## 2. Docker Engine — o que é grátis

| Componente | Licença | Custo |
|---|---|---|
| Docker Engine (dockerd, CLI) | **Apache 2.0** | Grátis, para qualquer uso, inclusive comercial |
| BuildKit, buildx | Apache 2.0 | Grátis |
| Docker Compose v2 | Apache 2.0 | Grátis |
| containerd, runc | Apache 2.0 (CNCF) | Grátis |

**Quem paga a conta do que é grátis?** A Docker Inc. (via assinaturas do Desktop e do Hub), os
provedores de nuvem e a CNCF (mantenedora do containerd e do runc, financiada por membros
corporativos). O Engine é o "produto de entrada" que sustenta a venda do resto.

---

## 3. Docker Desktop — onde entra a cobrança

Docker Desktop é o **aplicativo gráfico** para macOS, Windows e Linux. É o que muda de preço, não
o Engine.

### Planos (consultados em 11/08/2026)

| Plano | Preço (anual) | Para quem |
|---|---|---|
| **Personal** | **US$ 0** | Uso pessoal, educação, open source não comercial, e empresas pequenas |
| **Pro** | **~US$ 9/usuário/mês** | Desenvolvedor individual profissional |
| **Team** | **~US$ 15/usuário/mês** | Times, com gestão centralizada |
| **Business** | **~US$ 24/usuário/mês** | Empresa: SSO, SCIM, endurecimento, política |

### A regra que define se você paga

**Docker Desktop é gratuito** para:
- uso pessoal;
- educação;
- projetos open source não comerciais;
- **empresas com menos de 250 funcionários E menos de US$ 10 milhões de receita anual.**

**É pago** (assinatura Pro/Team/Business por usuário) para empresas que ultrapassem **qualquer**
dos dois limites acima.

> **Note o "E":** os dois critérios precisam ser satisfeitos para o uso gratuito. Uma startup de
> 30 pessoas com US$ 15 milhões de receita **precisa pagar**; uma ONG de 300 pessoas com US$ 2
> milhões de receita **também** — o limite de funcionários basta para exigir licença.

### Custos ocultos do Desktop

- **Consumo de recursos:** a VM reserva RAM (2–8 GB) e CPU mesmo ociosa.
- **Auditoria de conformidade:** provar quem usa Desktop numa empresa grande dá trabalho — é um
  custo administrativo real.
- **Migração** se decidir trocar: retreinar a equipe nas alternativas.

### Como evitar o custo, legalmente

O Engine e as alternativas cobrem quase tudo, com licença livre:

| Alternativa | Plataforma | Licença | Ressalva |
|---|---|---|---|
| **Docker Engine** | Linux | Apache 2.0 | Sem GUI; é o próprio Docker |
| **Podman + Podman Desktop** | Linux, mac, Win | Apache 2.0 | `alias docker=podman` cobre 90% |
| **Rancher Desktop** | Linux, mac, Win | Apache 2.0 | Traz Kubernetes junto |
| **colima** | mac | Apache 2.0 | Só CLI; leve |
| **OrbStack** | mac | **Proprietário** | Pago para uso comercial; o mais rápido |
| **Docker Engine no WSL2** | Win | Apache 2.0 | Sem o app; ver [03](03-instalacao.md) |

*Recomendação:* em Linux, nunca pague — use o Engine. Em empresa grande que já usa macOS/Windows,
avalie honestamente: o custo de suporte interno das alternativas pode exceder a licença. Em
organização com restrição orçamentária, Podman Desktop é maduro e sem ressalva técnica
relevante.

---

## 4. Docker Hub — armazenamento e o limite de pull

### Planos (consultados em 11/08/2026)

| Plano | Preço | Repositórios privados | Pulls |
|---|---|---|---|
| **Personal** | US$ 0 | 1 | 100/hora (autenticado) |
| **Pro** | ~US$ 9/mês | ilimitados | ilimitado (uso justo) |
| **Team** | ~US$ 15/usuário/mês | ilimitados | ilimitado |
| **Business** | ~US$ 24/usuário/mês | ilimitados | ilimitado |

### Os limites de pull — o custo que quebra CI (vigente desde 01/04/2025)

| Situação | Limite |
|---|---|
| **Sem autenticação** | **10 pulls/hora**, por IP |
| **Conta gratuita autenticada** | **100 pulls/hora** |
| Pro / Team / Business | Ilimitado, uso justo |

Impacto real: um runner de CI em IP compartilhado esgota os 10 pulls em minutos e o pipeline
quebra com `toomanyrequests`. Isso é custo — de tempo e de confiabilidade — mesmo sendo "grátis".

**Mitigações (custo baixo ou zero):**
- autenticar no CI (grátis, sobe para 100/h);
- espelho puxador na sua rede (`registry:2` como pull-through cache);
- registries alternativos: **GHCR** e **Quay** têm público ilimitado.

---

## 5. Registries de nuvem — o custo por GB e por egress

Você paga por **armazenamento** e, sobretudo, por **transferência de saída (egress)**. Valores
são **ordens de grandeza aproximadas, consultados em 11/08/2026** — confirme na calculadora de
cada provedor.

| Registry | Armazenamento | Egress | Grátis |
|---|---|---|---|
| **GHCR** | Na cota do GitHub | Generoso | Público ilimitado |
| **Quay.io** | Plano gratuito para público | — | Público ilimitado |
| **AWS ECR** | ~US$ 0,10/GB/mês | **Egress padrão da AWS** (~US$ 0,09/GB saindo) | 500 MB/mês (privado), 12 meses |
| **AWS ECR Public** | Grátis até certo limite | Grátis para o mundo | Sim |
| **Google Artifact Registry** | ~US$ 0,10/GB/mês | Egress padrão do GCP | 0,5 GB |
| **Azure ACR** | Por nível (Basic/Std/Premium) | Egress padrão | Camada limitada |

> **O egress é o custo que surpreende.** Uma imagem de 1 GB puxada 1.000 vezes por dia por nós
> em outra rede = ~1 TB/dia de saída. A ~US$ 0,09/GB, são ~US$ 90/dia só de transferência.
> **Correção:** registry na mesma região dos nós (egress intra-região costuma ser grátis),
> imagens menores, cache/espelho local. É onde imagem enxuta vira economia direta.

---

## 6. O custo de rodar containers na nuvem

Container não tem licença, mas a **infraestrutura** que o executa, sim. Comparação de modelos
(ordens de grandeza, 11/08/2026 — confirme):

| Modelo | Cobrança | Bom para | Cuidado |
|---|---|---|---|
| **VM própria + Docker** | Por hora da VM | Carga previsível | Você opera tudo |
| **AWS ECS + Fargate** | vCPU-hora + GB-hora | Sem gerenciar servidor | Mais caro por unidade que EC2 |
| **Google Cloud Run** | Por requisição + CPU/RAM usados; **escala a zero** | Tráfego variável | Cold start; caro sob tráfego alto constante |
| **AWS Lambda (container)** | Por invocação + duração | Picos, eventos | Limite de imagem; cold start |
| **Kubernetes gerenciado (EKS/GKE/AKS)** | ~US$ 70–100/mês pelo *control plane* + nós | Escala, multi-serviço | Complexidade operacional (a maior fatia é tempo de gente) |
| **Kubernetes próprio (k3s numa VM)** | Só a VM | Homelab, aprendizado | Você é o SRE |

**A regra de bolso:** para tráfego constante, VM ou nós reservados são mais baratos por unidade.
Para tráfego intermitente, serverless (Cloud Run/Lambda) evita pagar pela ociosidade. O erro
caro é rodar carga constante em serverless caro por unidade, ou provisionar cluster grande para
carga pequena.

---

## 7. Imagens base endurecidas — o custo novo de 2026

Surgiu uma categoria comercial: **imagens base com CVEs próximas de zero e SLA de correção**.

| Produto | Modelo | Licença/preço |
|---|---|---|
| **Docker Hardened Images** | Assinatura (Docker) | Comercial; consulte |
| **Chainguard Images** | Algumas grátis, catálogo completo pago | Comercial |
| **Minimus** | Comercial | Consulte |
| **distroless** (Google) | **Grátis** | Apache 2.0 — você faz o escaneamento |

**A conta a fazer:** você paga por imagens mantidas sem CVE, ou paga o tempo da sua equipe para
manter `distroless` + escaneamento + atualização disciplinada. Para times pequenos sem
especialista em segurança, a assinatura pode sair mais barata que o tempo. Para times com essa
competência, `distroless` grátis resolve. Ver [65-estado-da-arte.md](65-estado-da-arte.md#4-cadeia-de-suprimentos-de-boa-prática-a-obrigação-legal).

---

## 8. O custo que ninguém coloca na planilha

O maior custo do Docker **não é licença nem nuvem — é tempo de gente**:

- **Aprendizado:** 60–100 horas até competência produtiva (ver
  [02-pre-requisitos.md](02-pre-requisitos.md)).
- **Operação:** alguém cuida de atualizações, backups, segurança, disco cheio às 3 da manhã.
- **Depuração:** a curva de "por que não conecta / por que está lento / por que encheu o disco".
- **A dívida de complexidade** de adotar orquestração cedo demais — frequentemente o custo
  invisível mais alto de todos.

*Opinião profissional:* a decisão financeira mais impactante em containers raramente é
"Desktop pago ou grátis?". É **"orquestração agora ou depois?"**. Adotar Kubernetes cedo demais
custa, em tempo de equipe, muito mais que qualquer licença de Desktop. Ver
[25-orquestracao.md](25-orquestracao.md).

---

## 9. Cenários de custo, do zero ao corporativo

| Cenário | Configuração | Custo mensal aproximado |
|---|---|---|
| **Aprendiz** | Play with Docker / Engine no Linux / Codespaces | **US$ 0** |
| **Dev solo (Linux)** | Docker Engine + GHCR + VPS US$ 5 | **~US$ 5** |
| **Dev solo (Mac)** | Docker Desktop Personal (grátis) ou colima | **US$ 0** |
| **Homelab** | k3s ou Compose numa máquina própria | **custo de energia** |
| **Startup < 250 pessoas, < US$ 10M** | Desktop grátis + GHCR + Cloud Run | **baixo, escala com uso** |
| **Empresa média** | Desktop Team (20 devs) + ECR + EKS | **~US$ 300 (Desktop) + ~US$ 100 (control plane) + nós + tempo** |
| **Empresa grande** | Desktop Business + Hardened Images + registry corporativo | **licenças por usuário + assinaturas + equipe de plataforma** |

---

## 10. Como não gastar à toa

1. **Em Linux, use o Engine.** Nunca pague Desktop onde ele não agrega.
2. **Autentique no Docker Hub** — os 100 pulls/h grátis resolvem a maioria dos CI.
3. **Imagens menores = menos egress e menos armazenamento.** Multi-stage se paga.
4. **Registry na mesma região dos nós.** Egress intra-região costuma ser grátis.
5. **Escala a zero** (Cloud Run/Lambda) para carga intermitente; **nós reservados** para carga
   constante.
6. **Não adote Kubernetes antes de precisar.** É o gasto de tempo mais alto e mais evitável.
7. **Configure retenção no registry desde o primeiro dia**, antes de a conta de armazenamento
   crescer.

---

## Autoteste

1. O Docker Engine custa licença? E o Docker Desktop? Qual é a diferença entre os dois?
2. Uma empresa de 30 pessoas com US$ 15 milhões de receita pode usar Docker Desktop de graça?
   Justifique com a regra do "E".
3. Quais são os limites de pull do Docker Hub hoje, e por que isso é um custo mesmo sendo
   "grátis"?
4. Por que o egress é o custo de registry que mais surpreende, e como reduzi-lo?
5. Quando serverless (Cloud Run) sai mais barato que VM, e quando sai mais caro?
6. Qual é a decisão financeira de maior impacto em containers, na opinião do autor? Por quê?
7. Você quer evitar pagar Docker Desktop numa empresa. Cite três alternativas livres e a
   ressalva de cada.
8. Imagem endurecida paga ou `distroless` grátis: qual é a conta que decide?
9. Qual é o custo que "ninguém coloca na planilha", e por que ele domina?
10. Liste três formas concretas de reduzir o custo de rodar containers na nuvem.

---

### Fontes consultadas (11/08/2026)

- [Docker Pricing — página oficial](https://www.docker.com/pricing/) — planos Personal/Pro/Team/Business (valores aproximados; confirme na fonte)
- [Docker Docs — Usage and rate limits](https://docs.docker.com/docker-hub/usage/) — limites de pull vigentes desde 01/04/2025
- [Docker Subscription Service Agreement / FAQ](https://www.docker.com/legal/docker-subscription-service-agreement/) — regra dos 250 funcionários e US$ 10M de receita
- Calculadoras de preço da AWS, Google Cloud e Azure — **ordens de grandeza; sempre confirmar na fonte antes de decidir**
