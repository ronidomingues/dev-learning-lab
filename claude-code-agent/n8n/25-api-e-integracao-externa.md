# 25 · API pública, embed e integração externa

`Nível: avançado` · `01/09/2026`

---

Como falar com o n8n **de fora** — automatizar a própria ferramenta, e embuti-la
em outro produto.

---

## 1. API pública REST

### 1.1 Ligar e autenticar

Base: `https://<seu-n8n>/api/v1` · Documentação viva: `https://<seu-n8n>/api/v1/docs`

1. *Settings → n8n API → Create an API key*.
2. Envie no cabeçalho:

```bash
curl -s https://n8n.exemplo/api/v1/workflows \
  -H "X-N8N-API-KEY: $N8N_API_KEY" | jq '.data[] | {id, name, active}'
```

Para desligar completamente (recomendado se ninguém usa):

```yaml
N8N_PUBLIC_API_DISABLED: "true"
```

### 1.2 O que dá para fazer

| Recurso | Operações | Uso típico |
|---|---|---|
| `/workflows` | listar, obter, criar, atualizar, apagar, ativar, desativar | **Gerar fluxos por programa**; promover entre ambientes |
| `/executions` | listar, obter, apagar | Painel próprio, limpeza customizada |
| `/credentials` | criar, apagar, ver esquema | Provisionar credencial por cliente |
| `/tags`, `/projects`, `/users` | organização | Onboarding automatizado |
| `/datatables` | tabelas internas | Alimentar dados de fora |
| `/audit` | relatório de segurança | Rotina de conformidade |
| `/source-control/pull` | puxar do Git | CI/CD (licenciado) |

> **`/credentials` não devolve segredos.** Você cria e apaga; não lê de volta.
> É uma decisão de projeto correta.

### 1.3 O caso que justifica a API: multi-tenant

O padrão mais valioso da API pública é **gerar fluxos por programa**: para cada
cliente novo, seu sistema cria a credencial dele e clona um workflow modelo,
substituindo parâmetros.

```bash
# 1) obter o modelo
curl -s $BASE/workflows/MODELO -H "X-N8N-API-KEY: $K" > modelo.json

# 2) transformar (jq, Python, o que preferir): nome, credencial, parâmetros
jq --arg cli "ACME" '.name = "Sync – " + $cli' modelo.json > novo.json

# 3) criar
curl -s -X POST $BASE/workflows -H "X-N8N-API-KEY: $K" \
  -H 'Content-Type: application/json' --data-binary @novo.json

# 4) ativar
curl -s -X POST $BASE/workflows/<novoId>/activate -H "X-N8N-API-KEY: $K"
```

> **Cuidado de licença.** Hospedar fluxos **dos seus clientes** na sua instância
> deixa de ser "uso interno" e passa a exigir licença comercial. Leia
> [80-custos-e-licencas.md](80-custos-e-licencas.md) **antes** de construir um
> produto sobre isso.

---

## 2. Chamar o n8n a partir do seu sistema

Do mais simples ao mais acoplado:

| Forma | Como | Quando |
|---|---|---|
| **Webhook** | `POST /webhook/<path>` | **O caminho normal.** Simples e desacoplado |
| **API pública** | `POST /workflows/<id>/…` | Quando precisa gerenciar, não só disparar |
| **Formulário** | n8n Form Trigger | Processo com pessoa no meio |
| **Chat** | Chat Trigger (embutível) | Assistente |
| **MCP** | MCP Server Trigger | Agente de IA como consumidor |

Na esmagadora maioria dos casos: **webhook**. Sua aplicação não precisa saber que
existe n8n do outro lado, e você pode trocar a implementação sem tocar nela.

---

## 3. Incorporar o n8n em outro produto (Embed)

Existe um caminho oficial: **n8n Embed**, para quem quer oferecer automação dentro
do próprio produto (o cliente final vê o editor, com a sua marca).

O que ele traz:

- Editor incorporável (iframe), com marca própria.
- **Modo canvas apenas** (`N8N_CANVAS_ONLY`), que esconde navegação e configurações
  e mostra só o canvas.
- SSO delegado por **OAuth 2.0 Token Exchange**, para o usuário do seu produto agir
  dentro do n8n incorporado.
- Provisionamento por API.

**E o principal:** exige **licença de Embed** — na prática, um contrato comercial
com a n8n, com valor anual relevante e/ou participação na receita. Não é uma
variável de ambiente; é um acordo.

> **Se você está avaliando construir um produto sobre o n8n**, faça a conversa
> comercial **antes** de escrever a primeira linha. Descobrir isso com o produto
> pronto é a pior ordem possível.

---

## 4. Alternativas por nível de acoplamento

```
menos acoplado ─────────────────────────────────────────▶ mais acoplado

Webhooks       API pública        Instância por      n8n Embed
(seu sistema   (você gerencia     cliente            (o cliente vê
 nem sabe)      os fluxos)        (isolamento         o n8n dentro
                                   total)             do seu produto)
```

| Opção | Isolamento | Custo operacional | Licença |
|---|---|---|---|
| Webhooks | total | baixo | uso interno ✅ |
| API pública, fluxos seus | bom | médio | uso interno ✅ |
| API pública, fluxos **dos clientes** | fraco | médio | **licença comercial** |
| Uma instância por cliente | total | **alto** | depende do contrato |
| Embed | — | alto | **licença de Embed** |

---

## 5. n8n dentro de CI/CD

```yaml
# exemplo de pipeline: valida e promove os fluxos
- name: Validar JSON dos workflows
  run: for f in workflows/*.json; do python -c "import json,sys;json.load(open('$f'))"; done

- name: Importar em homologação
  run: |
    docker compose exec -T n8n n8n import:workflow --separate --input=/import/workflows
    docker compose exec -T n8n n8n publish:workflow --id=$WF_ID
    docker compose restart n8n

- name: Teste de ponta a ponta
  run: ./scripts/testar.sh https://homologacao.exemplo
```

É exatamente o que o [projeto-modelo](07-projeto-modelo/README.md) faz manualmente
com o `Makefile`. Transformar aquilo num pipeline é meia hora de trabalho.

---

## Autoteste

1. Como se autentica na API pública e como se desliga a API?
2. Por que `/credentials` não devolve os segredos?
3. Descreva o padrão multi-tenant com a API, em quatro passos.
4. Que restrição de licença aparece assim que você hospeda fluxos **de clientes**?
5. Qual a forma mais desacoplada de o seu sistema disparar um fluxo, e por quê?
6. O que é o `N8N_CANVAS_ONLY` e em que contexto aparece?
7. O que a licença de Embed exige, na prática?
8. Ordene por acoplamento: webhooks, instância por cliente, Embed, API pública.
9. Que três passos um pipeline de CI/CD de workflows precisa ter, no mínimo?

---

*Anterior: [24-ia-e-agentes.md](24-ia-e-agentes.md) · Próximo: [60-teoria-avancada.md](60-teoria-avancada.md)*
