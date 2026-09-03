# 26 · Times e escala — o que muda quando são 300 pessoas

> **Nível:** avançado · **Atualizado em:** 13/08/2026 · Claude Code 2.1.231

Tudo que funciona para uma pessoa muda de natureza em escala. Este arquivo é sobre adoção,
controle, medição e as coisas que só dão errado com muita gente.

---

## 1. Configuração gerenciada

Organizações não pedem: elas **impõem**. Configuração gerenciada tem precedência sobre
tudo, e nem usuário nem projeto podem anulá-la.

| Sistema | Onde |
|---|---|
| Linux / WSL | `/etc/claude-code/managed-settings.json` |
| macOS | `/Library/Application Support/ClaudeCode/managed-settings.json` ou plist `com.anthropic.claudecode` |
| Windows | `C:\Program Files\ClaudeCode\managed-settings.json` ou registro `HKLM\SOFTWARE\Policies\ClaudeCode` |
| Servidor | Console de administração da claude.ai, ou gateway auto-hospedado |

Também há `managed-settings.d/` com vários `*.json` mesclados em ordem alfabética — útil
para separar política de segurança, de custo e de ferramentas em arquivos distintos.

Distribua por MDM, Group Policy, Ansible ou Puppet. Modelo de política em
[`24-seguranca.md`](24-seguranca.md), seção 7.

E há o `CLAUDE.md` gerenciado, que vale em toda sessão da máquina:

```json
{ "claudeMd": "Sempre rode `make lint` antes de commitar.\nNunca faça push direto na main." }
```

**A divisão que importa:** configuração para o que precisa ser **imposto tecnicamente**;
`CLAUDE.md` para o que é **orientação de comportamento**. Confundir os dois gera política
que não é seguida e reclamação de que "a ferramenta não obedece".

---

## 2. Custo em escala

**[fato, documentação oficial consultada em 13/08/2026]** Em implantações corporativas, a
média fica em torno de **US$ 13 por dev por dia ativo** e **US$ 150–250 por dev por mês**,
com 90% dos usuários abaixo de US$ 30 por dia ativo.

Onde ver e como limitar, por tipo de contrato:

| Contrato | Ver gasto | Limitar | Relatório por usuário |
|---|---|---|---|
| Team / Enterprise | relatório de gasto no analytics da organização | limites de gasto nas configurações de admin | CSV; Enterprise Analytics API no plano Enterprise |
| Console (API) | página de uso do Console | limites por workspace | painel do Console; Claude Code Analytics API |
| Bedrock / Google Cloud / Foundry | faturamento do provedor | orçamento do provedor | OpenTelemetry ou gateway |

Em Team e Enterprise, o uso sai de uma **cota por assento** com janelas móveis de 5 horas e
semanal, compartilhada com o Claude chat. Créditos de uso permitem passar da cota, com
limites de gasto por organização, grupo ou pessoa.

**Recomendação de limites de taxa** (TPM/RPM por usuário), da documentação oficial:

| Tamanho do time | TPM por usuário | RPM por usuário |
|---|---|---|
| 1–5 | 200k–300k | 5–7 |
| 5–20 | 100k–150k | 2,5–3,5 |
| 20–50 | 50k–75k | 1,25–1,75 |
| 50–100 | 25k–35k | 0,62–0,87 |
| 100–500 | 15k–20k | 0,37–0,47 |
| 500+ | 10k–15k | 0,25–0,35 |

A cota cai com o tamanho do time porque a concorrência simultânea diminui proporcionalmente.
Exceção prevista: **treinamento ao vivo com muita gente** — aí a concorrência é máxima e
você precisa de folga temporária.

### As três causas de gasto anômalo

1. **Sessão aberta o dia inteiro.** O contexto inteiro é reenviado a cada turno. Uma
   pergunta de uma linha numa sessão de oito horas cobra pela conversa toda.
2. **Opus como padrão.** Sonnet resolve a maioria por fração do preço.
3. **Servidores MCP demais.** Único custo recorrente por mensagem.

O `/usage` mostra atribuição por skill, subagente, plugin e servidor MCP, e sinaliza
comportamentos (contexto longo, perda de cache) que passem de 10% do uso recente.

---

## 3. Medir de verdade

### OpenTelemetry — funciona em qualquer contrato

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "https://otel.empresa.com"
  }
}
```

É a **única** opção que dá métricas por usuário, em quase tempo real, no seu próprio
observatório, independentemente de provedor — inclusive em Bedrock, Google Cloud e Foundry,
que não mandam métricas de volta para a Anthropic.

### Métricas que valem, e as que enganam

| Métrica | Vale? |
|---|---|
| Custo por dev por dia | **Sim** — é a que orienta orçamento |
| Sessões por dia, DAU | Sim, para medir adoção |
| Linhas aceitas | **Não isoladamente.** Incentiva volume, e volume não é valor |
| Tempo de ciclo de PR | **Sim** — é o resultado que interessa |
| Taxa de reversão / correção pós-merge | **Sim** — é o alerta de qualidade caindo |
| Tempo até o primeiro PR de quem entrou no time | Sim — mede se o agente ajuda a integrar gente |

> **[opinião]** "Linhas de código aceitas" como métrica de sucesso de adoção é o erro
> clássico de programa de IA em empresa. Ela sobe sozinha e não correlaciona com valor
> entregue. Se você medir só isso, vai celebrar um repositório inchado.

---

## 4. Adoção — o que funciona e o que não

**Não funciona:** mandar todo mundo usar; treinamento único de duas horas; medir por linhas
aceitas; deixar cada um descobrir sozinho; proibir por medo e não oferecer alternativa.

**Funciona:**

1. **Piloto com 5–10 pessoas motivadas**, em repositórios que já têm testes. Elas descobrem
   as armadilhas e viram os multiplicadores.
2. **Configuração compartilhada desde cedo.** `.claude/settings.json` versionado, plugin da
   organização ([`21`](21-plugins-e-marketplaces.md)). O ganho do piloto tem que ser copiável.
3. **Investir no repositório, não no prompt.** Suíte lenta é o maior limitador de valor.
   Cortar o tempo de teste pela metade rende mais que qualquer configuração.
4. **Casos de uso concretos**, não "use para tudo": escrever teste para código sem teste,
   migração mecânica, explicar código legado, primeira versão de PR.
5. **Espaço para relato honesto**, inclusive negativo. Um canal onde "isso não funcionou
   para o meu caso" é aceito produz aprendizado real; um canal só de sucesso produz teatro.

### O padrão que se repete

**[opinião]** Times que dão certo têm três coisas antes de adotar: **testes rápidos e
confiáveis**, **convenções escritas** e **PRs pequenos**. Times que não têm essas três
concluem que a ferramenta não funciona — e estão parcialmente certos: para o repositório
deles, não funciona mesmo. A adoção bem-sucedida costuma ser, em boa parte, um projeto de
melhoria de engenharia disfarçado.

---

## 5. O que só dá errado em escala

| Problema | Por quê | Defesa |
|---|---|---|
| Configuração divergente entre 300 máquinas | Cada um ajusta o seu | Configuração gerenciada + plugin da organização |
| Explosão de custo em um time | Um projeto com sessões enormes, Opus fixo | Limites por workspace/grupo, alerta por OTel |
| Plugin não auditado espalhando | Alguém achou um bom no GitHub | `strictKnownMarketplaces`, `blockedMarketplaces` |
| MCP para sistema sensível sem controle | "Só para facilitar" | `allowedMcpServers`, `allowManagedMcpServersOnly` |
| Fila de revisão | Geração barata, revisão cara | Diffs pequenos, revisão em camadas ([`25`](25-o-oficio-do-profissional.md)) |
| Queda de qualidade percebida tarde | Ninguém mede reversão | Métrica de correção pós-merge |
| Segredo em transcrição | Alguém leu `.env` numa sessão | `deny` gerenciado + hook `PreToolUse` |
| Versões diferentes com comportamento diferente | Auto-update em canal `latest` | `autoUpdatesChannel: stable` + `requiredMinimumVersion` |

---

## 6. Onboarding — o roteiro de uma página

O que entregar a quem chega:

1. **Um `.claude/settings.json` no repositório**, já com permissões e hooks.
2. **Um `CLAUDE.md` enxuto**, que a pessoa lê como documentação humana também.
3. **Um documento de meia página** com: o que usar, o que não usar, como pedir ajuda.
4. **Uma sessão de 30 minutos ao vivo**, mostrando alguém trabalhando de verdade — inclusive
   errando e corrigindo. Vale mais que qualquer slide.
5. **Um canal** para dúvidas e relatos.

O que **não** entregar: um manual de 40 páginas. Ninguém lê, e ele desatualiza em um mês.

---

## 7. Os cinco porquês: por que a adoção falha em times com repositório ruim?

1. **Por que o time X reclama e o time Y prospera?**
   O repositório de Y tem testes rápidos; o de X não tem testes ou eles demoram 20 minutos.
2. **Por que isso pesa tanto?**
   Sem oráculo automático, o agente para no plausível e a verificação recai sobre a pessoa —
   que passa a gastar mais tempo revisando do que gastaria escrevendo.
3. **Por que ninguém vê isso antes de adotar?**
   Porque a fraqueza do repositório já era paga em outro lugar: bugs em produção, medo de
   refatorar, integração lenta de gente nova. O agente só concentra essa conta num lugar visível.
4. **Por que a conta aparece agora?**
   Porque a geração de código deixou de ser o gargalo. Quando o gargalo se move, ele expõe o
   próximo — e o próximo era a verificação.
5. **Qual é a conclusão para quem lidera?**
   **Adotar agente e melhorar a engenharia de base são o mesmo projeto.** Tratá-los como
   separados é o que produz aquele piloto que "não deu resultado".
   *(Parada legítima: propriedade estrutural — o agente amplifica o que existe, inclusive a ausência.)*

---

## Fontes consultadas

- *Manage costs effectively*: https://code.claude.com/docs/en/costs (13/08/2026) — média por
  dev, recomendações de TPM/RPM, atribuição no `/usage`.
- *Settings* e *Security*: https://code.claude.com/docs/en/settings, `/security` (13/08/2026).
- *Monitoring usage*: referenciado na documentação de custos para a exportação OpenTelemetry.

---

## Autoteste

1. Onde fica a configuração gerenciada em cada sistema, e o que usuário e projeto podem fazer contra ela?
2. Qual é o custo médio por dev por dia e por mês, segundo a documentação oficial?
3. Por que a cota de TPM por usuário **cai** conforme o time cresce? Qual é a exceção?
4. Cite três métricas que valem e uma que engana. Por que a que engana é tão comum?
5. Quais três características os times bem-sucedidos têm **antes** de adotar?
6. Cite quatro problemas que só aparecem em escala e a defesa de cada um.
7. O que entregar — e o que não entregar — a quem está chegando?
8. Por que "adotar agente e melhorar a engenharia de base são o mesmo projeto"?
