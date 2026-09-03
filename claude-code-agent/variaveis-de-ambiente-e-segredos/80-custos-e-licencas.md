# 80 · Custos e licenças

`Nível: todos` · **Preços consultados em 14/08/2026**
`Câmbio usado: US$ 1,00 ≈ R$ 5,20 (cotação consultada em 18/08/2026)`

> ⚠️ **Preço sem data é desinformação.** Todos os valores abaixo têm a data da
> consulta. Reconfira antes de decidir — esta área muda de preço com frequência, e o
> câmbio muda mais ainda.

---

## 1. Resposta curta: quase tudo é gratuito

**A boa notícia é a primeira coisa que você precisa saber:** fazer isso **certo**
custa **R$ 0,00** para a esmagadora maioria dos projetos.

| O que | Custo |
|---|---|
| Variáveis de ambiente | grátis (é do sistema operacional) |
| `.gitignore`, `.env.example` | grátis |
| `dotenv`, `python-dotenv`, `phpdotenv` | grátis (MIT/BSD) |
| `--env-file` nativo do Node | grátis |
| systemd `EnvironmentFile` / `LoadCredential` | grátis |
| Docker secrets, Compose | grátis |
| Kubernetes Secrets + KMS | grátis (o KMS da nuvem custa ~US$ 1/chave/mês) |
| **SOPS + age** | grátis (MPL 2.0 / BSD) |
| **OpenBao** | grátis (MPL 2.0) |
| **gitleaks** | grátis (MIT) |
| **GitHub secret scanning + push protection** (repositório público) | grátis |
| **AWS Parameter Store** (Standard, até 10.000 parâmetros) | **grátis** |
| Este curso inteiro | grátis |

**Quem paga a conta do que é gratuito:**

- `dotenv`, `gitleaks`, SOPS, age: voluntários e empresas que os usam. `gitleaks` tem
  patrocínio; SOPS é sandbox da CNCF (Linux Foundation), com infraestrutura paga por
  membros corporativos.
- **OpenBao**: Linux Foundation, financiada por membros — IBM, e depois outras
  empresas que dependem do projeto.
- **GitHub secret scanning grátis em repositório público**: a Microsoft se beneficia
  de um ecossistema com menos vazamentos, e vende a versão para repositório privado.
- **AWS Parameter Store gratuito**: isca para você usar mais AWS. O Secrets Manager,
  esse sim, é pago.

Você paga quando precisa de **auditoria, rotação automática e credencial dinâmica** —
não de "guardar em segurança".

---

## 2. Cofres gerenciados na nuvem

Todos consultados em **14/08/2026**.

### AWS Secrets Manager

| Item | Preço | Em BRL (aprox.) |
|---|---|---|
| Por segredo, por mês | **US$ 0,40** | ~R$ 2,08 |
| Por 10.000 chamadas de API | **US$ 0,05** | ~R$ 0,26 |
| Réplica em outra região | conta como segredo adicional | — |
| Camada gratuita permanente | **não existe** | — |

Clientes novos da AWS recebem até US$ 200 em créditos de Free Tier (válidos por até
6 meses após a criação da conta, expirando em 12 meses), utilizáveis em serviços
elegíveis — não é uma camada gratuita permanente do serviço.

**Exemplo real:** 20 segredos + 500.000 chamadas/mês =
`20 × 0,40 + 50 × 0,05` = **US$ 10,50/mês** ≈ R$ 55.

⚠️ **A conta que explode:** buscar o segredo a cada requisição. Um serviço com
1.000 req/s faz ~2,6 bilhões de chamadas/mês = **US$ 13.000/mês** ≈ R$ 67.600.
Sempre cache com TTL ([30 §8](30-entrega-em-producao.md)).

> 💡 **A alternativa gratuita dentro da própria AWS:** o **Systems Manager Parameter
> Store**, tipo `SecureString`, é **gratuito** até 10.000 parâmetros (nível Standard),
> criptografa com KMS e integra com IAM, ECS e Lambda igual. O que ele **não** faz:
> rotação gerenciada e credencial dinâmica. Para quem só precisa guardar com
> segurança e controlar acesso, economiza 100% do custo.

### Google Secret Manager

| Item | Preço | Em BRL (aprox.) |
|---|---|---|
| Versão ativa, por mês, por local | **US$ 0,06** | ~R$ 0,31 |
| Por 10.000 operações de acesso | **US$ 0,03** | ~R$ 0,16 |
| Operações de gerência (criar, destruir) | **gratuitas** | — |
| Notificação de rotação | US$ 0,05 por rotação | ~R$ 0,26 |
| **Camada gratuita mensal** | **6 versões ativas + 10.000 acessos + 3 rotações** | — |

O mais barato dos três grandes, com folga, e o único com camada gratuita permanente.

⚠️ **A pegadinha:** você paga por **versão ativa**, não por segredo. Um segredo com
84 versões antigas ainda habilitadas custa 84 × US$ 0,06 = US$ 5,04/mês **sozinho**.
Desabilite ou destrua versões antigas.

### Azure Key Vault

| Item | Preço | Em BRL (aprox.) |
|---|---|---|
| 10.000 operações de segredo (Standard) | **US$ 0,03** | ~R$ 0,16 |
| Chave protegida por HSM (Premium) | ~US$ 1,00/chave/mês + US$ 0,15 por 10.000 operações | ~R$ 5,20 |
| Managed HSM (Standard B1) | ~US$ 3,20 por 10.000 transações | ~R$ 16,64 |

Não cobra por segredo armazenado — só por operação. Para quem armazena muito e lê
pouco, é o mais barato.

### Comparação para um caso típico

10 segredos, 100.000 leituras/mês:

| Serviço | Custo/mês | Em BRL |
|---|---|---|
| AWS Parameter Store (Standard) | **US$ 0,00** | R$ 0,00 |
| Google Secret Manager | ~US$ 0,87 | ~R$ 4,52 |
| Azure Key Vault (Standard) | ~US$ 0,30 | ~R$ 1,56 |
| AWS Secrets Manager | ~US$ 4,50 | ~R$ 23,40 |
| OpenBao autogerenciado | US$ 0 de licença + **VM** (~US$ 20–40/mês) + **seu tempo** | ~R$ 104–208 + tempo |

**A última linha é o ponto:** "autogerenciado é grátis" ignora a VM, o backup, a alta
disponibilidade, o auto-unseal e as horas de quem opera. Para 10 segredos, o cofre
gerenciado é **muito** mais barato que o gratuito.

---

## 3. SaaS de gestão de segredos

| Serviço | Gratuito | Pago | Modelo de cobrança |
|---|---|---|---|
| **Doppler** | até 3 usuários | ~US$ 8/usuário/mês (Developer, até 25) · ~US$ 21/usuário/mês (Team) | por **usuário** |
| **Infisical Cloud** | até 5 identidades | ~US$ 18/identidade/mês (Pro) | por **identidade** |
| **1Password Secrets Automation** | — | adicional sobre o plano de time | por conta de serviço |
| **HCP Vault** (gerenciado) | — | varia por cluster e tamanho | por hora de cluster |

⚠️ **A diferença entre "usuário" e "identidade" é a armadilha de custo desta seção.**
No Doppler, cobra-se por **pessoa**. No Infisical, "identidade" conta **humanos e
máquinas** — cada serviço, cada ambiente de CI, cada worker. Um time de 5 pessoas com
20 serviços paga por 5 no Doppler e por até 25 no Infisical. **Simule com os seus
números antes de assinar.**

Doppler: a partir de 3 usuários é ~US$ 8/usuário/mês; recursos de segurança
(RBAC, SAML SSO, MFA, change requests) só no plano Team, a ~US$ 21/usuário/mês
(preços de junho de 2026). Para uma equipe de 8 pessoas no Team: ~US$ 168/mês
≈ **R$ 874/mês**.

---

## 4. Licenças — o que cada uma permite

| Software | Licença | Uso comercial | Modificar | SaaS concorrente | Observação |
|---|---|---|---|---|---|
| `dotenv` (Node) | BSD-2 | ✅ | ✅ | ✅ | permissiva |
| `python-dotenv` | BSD-3 | ✅ | ✅ | ✅ | permissiva |
| `vlucas/phpdotenv` | BSD-3 | ✅ | ✅ | ✅ | permissiva |
| **SOPS** | MPL 2.0 | ✅ | ✅ (copyleft por arquivo) | ✅ | CNCF sandbox |
| **age** | BSD-3 | ✅ | ✅ | ✅ | — |
| **gitleaks** | MIT | ✅ | ✅ | ✅ | — |
| **trufflehog** | AGPL-3.0 | ✅ | ⚠️ | ⚠️ | **AGPL: oferecer como serviço obriga a publicar suas modificações** |
| **OpenBao** | MPL 2.0 | ✅ | ✅ | ✅ | Linux Foundation |
| **HashiCorp Vault** | **BUSL 1.1** | ✅ | ✅ | ❌ | vira MPL 2.0 **4 anos** após cada versão |
| **Infisical** | MIT + partes proprietárias | ✅ | ✅ | ⚠️ | modelo *open core* |
| **Docker Desktop** | proprietária | ⚠️ | ❌ | — | **pago** para empresas com >250 funcionários **ou** >US$ 10 mi de receita anual |
| Kubernetes, ESO | Apache 2.0 | ✅ | ✅ | ✅ | — |

**As três linhas que exigem atenção jurídica:**

1. **Vault (BUSL 1.1):** você **pode** usar internamente, inclusive comercialmente.
   O que é proibido é oferecer o Vault como serviço concorrente da HashiCorp/IBM.
   Para 99% dos leitores, **não muda nada**. Migrar para OpenBao por causa da licença
   é decisão de governança e de risco futuro, não de conformidade hoje.
2. **trufflehog (AGPL-3.0):** usar internamente é livre. Se você **oferecer** um
   serviço baseado nele, precisa disponibilizar suas modificações. Passe pelo jurídico.
3. **Docker Desktop:** o critério é objetivo — mais de 250 funcionários **ou** mais de
   US$ 10 milhões de receita anual exige assinatura paga. Alternativas gratuitas:
   Podman Desktop, Rancher Desktop, colima (macOS), ou Docker Engine direto no Linux.

---

## 5. Custos ocultos

Estes não aparecem na página de preços e são os que decidem o projeto.

| Custo oculto | Ordem de grandeza |
|---|---|
| **Operar um cofre autogerenciado** | 4–20 h/mês de engenharia. A R$ 150/h, **R$ 600–3.000/mês** — mais caro que qualquer cofre gerenciado |
| **Alta disponibilidade do cofre** | 3 VMs em vez de 1, mais o armazenamento do Raft |
| **Auto-unseal** | exige KMS da nuvem (~US$ 1/mês) ou TPM. **Sem ele, um humano destrava a cada reinício** |
| **Chamadas de API não previstas** | o item que mais surpreende — ver o exemplo de US$ 13.000 no §2 |
| **Egress entre nuvens** | cofre numa nuvem e aplicação em outra: US$ 0,08–0,12/GB |
| **Latência** | +5 a 50 ms por busca. Com autoescalonamento agressivo, isso vira "inicialização lenta" |
| **Migração e aprisionamento** | trocar de cofre = reescrever integrações + rotacionar tudo |
| **Treinamento** | 1–2 dias por pessoa para operar Vault com segurança |
| **Um incidente causado pelo cofre** | o cofre indisponível derruba **todas** as aplicações que dependem dele |
| **Auditoria/certificação** | SOC 2 e ISO 27001 custam dezenas de milhares de reais, e o cofre é só um item da lista |

> **A conta que ninguém faz:** um cofre autogerenciado para proteger 15 segredos de um
> sistema pequeno custa mais em tempo de engenharia, por mês, do que o prejuízo
> esperado do risco que ele mitiga. Isso não é argumento contra cofres — é argumento a
> favor de **dimensionar** a decisão. Ver [40 §4](40-cofres-de-segredos.md).

---

## 6. Recomendação por porte

| Porte | Solução | Custo/mês |
|---|---|---|
| Projeto pessoal, 1 servidor | `.env` + systemd `LoadCredential` + gitleaks | **R$ 0** |
| Startup, 2–5 pessoas, 1 nuvem | cofre nativo da nuvem (Parameter Store na AWS) | **R$ 0 a 25** |
| Startup com equipe distribuída | Doppler ou Infisical (plano gratuito enquanto couber) | **R$ 0 a 400** |
| Empresa média, multi-nuvem | OpenBao autogerenciado | ~R$ 300 de infra + **tempo** |
| Empresa com conformidade | cofre gerenciado + auditoria | R$ 500 a 5.000 + consultoria |
| Entrega on-premise ao cliente | **SOPS + age** + instalador | **R$ 0** |

---

## 7. Autoteste

1. Por que se pode dizer que "fazer isso certo custa R$ 0,00" para a maioria dos projetos?
2. Qual é a diferença de modelo de cobrança entre AWS Secrets Manager e Google Secret Manager?
3. Como o Google Secret Manager pode ficar caro sem que você adicione segredos novos?
4. Qual serviço da AWS é gratuito e resolve a maioria dos casos? O que ele **não** faz?
5. Qual é a diferença entre cobrar por "usuário" e por "identidade", e por que ela importa?
6. O que a licença BUSL 1.1 do Vault proíbe, e por que provavelmente não afeta você?
7. Que cuidado a licença AGPL do trufflehog exige?
8. Quando o Docker Desktop passa a ser pago?
9. Cite três custos ocultos de um cofre autogerenciado.
10. Por que um cofre autogerenciado pode ser **mais caro** que um gerenciado para 10 segredos?

---

**Fontes consultadas em 14/08/2026:** aws.amazon.com/secrets-manager/pricing ·
aws.amazon.com/systems-manager/pricing · cloud.google.com/secret-manager/pricing ·
azure.microsoft.com/pricing/details/key-vault · doppler.com/pricing ·
infisical.com/pricing · docker.com/pricing · github.com/getsops/sops (LICENSE) ·
github.com/trufflesecurity/trufflehog (LICENSE) · openbao.org ·
cotação USD/BRL consultada em 18/08/2026 (~5,20) via br.investing.com.
**Todos os valores em BRL são conversões aproximadas e mudam com o câmbio.**

**Próximo:** [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) · Voltar ao [mapa](00-MAPA.md)
