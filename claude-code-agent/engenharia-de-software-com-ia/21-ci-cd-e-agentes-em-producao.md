# 21 · CI/CD e agentes em produção

**Nível:** avançado · **Escrito em:** 20/08/2026

---

## A regra que organiza tudo

> **O agente propõe. O CI decide. Sempre.**

Um sistema não-determinístico não pode ser a autoridade sobre se o código entra.
Não é desconfiança do modelo — é propriedade de projeto: **autoridade exige
reprodutibilidade**, e o modelo não a tem (ver
[12-o-modelo-por-dentro](12-o-modelo-por-dentro.md), §4).

Corolário: **nenhuma etapa que decide contém IA.** No
[projeto-modelo](07-projeto-modelo/README.md) essa regra é levada a sério: não
há uma linha de IA dentro do portão.

---

## 1 · Onde o agente entra no pipeline

```
    dev/agente
        │
        ▼
  ┌─────────────────────────────────────────────┐
  │  PRÉ-COMMIT (local, conveniência)           │
  │  formatador · linter · segredos             │
  └─────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────┐
  │  CI — PORTÃO (obrigatório, sem IA)          │
  │  build · tipos · lint · testes · segredos · │
  │  dependências · escopo · tamanho · cobertura│
  └─────────────────────────────────────────────┘
        │  aprovado
        ▼
  ┌─────────────────────────────────────────────┐
  │  ASSISTENTES (opcional, COM IA, sem poder)  │
  │  revisão automática · triagem de falha ·    │
  │  resumo de PR · sugestão de teste faltando  │
  │  → escrevem COMENTÁRIO, nunca decidem       │
  └─────────────────────────────────────────────┘
        │
        ▼
    revisão humana → merge → deploy
```

**A separação entre as duas caixas do meio é a arquitetura inteira.** Portão
decide e é determinístico. Assistente opina e pode errar sem consequência.

---

## 2 · O portão em GitHub Actions

Exemplo completo e comentado.

```yaml
name: Portão

on:
  pull_request:
    branches: [main]

permissions:
  contents: read          # mínimo necessário

concurrency:
  group: portao-${{ github.head_ref }}
  cancel-in-progress: true    # cancela execução antiga do mesmo PR

jobs:
  rapido:
    name: Verificações rápidas
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0        # o portão precisa do histórico para o diff

      - uses: actions/setup-node@v5
        with:
          node-version: '22'
          cache: 'npm'

      - name: Instalar do lockfile
        run: npm ci             # NUNCA `npm install` no CI

      - name: Formatação
        run: npm run format:check

      - name: Lint
        run: npm run lint

      - name: Tipos
        run: npx tsc --noEmit

      - name: Segredos
        uses: gitleaks/gitleaks-action@v2
        env:
          GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}

      - name: Portão do diff (escopo, tamanho, pacotes, critérios)
        run: |
          git diff origin/${{ github.base_ref }}...HEAD \
            | python3 -m portao --sem-cor --online

      - name: Verificações desabilitadas
        run: |
          if git diff origin/${{ github.base_ref }}...HEAD \
             | grep -E '^\+.*(eslint-disable|@ts-ignore|# type: ignore|\.skip\(|xit\(|@unittest\.skip)'; then
            echo "::error::Verificação desabilitada no diff. Conserte, não desligue."
            exit 1
          fi

  testes:
    name: Testes
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v5
        with: { fetch-depth: 0 }
      - uses: actions/setup-node@v5
        with: { node-version: '22', cache: 'npm' }
      - run: npm ci
      - run: npm test -- --coverage

      - name: Cobertura do diff
        run: |
          npx diff-cover coverage/cobertura-coverage.xml \
            --compare-branch=origin/${{ github.base_ref }} \
            --fail-under=80
```

### As cinco decisões que valem comentar

| Decisão | Por quê |
|---|---|
| `permissions: contents: read` | O padrão do GitHub é generoso demais. Um *workflow* comprometido com escrita pode alterar o repositório |
| `npm ci`, nunca `npm install` | `ci` instala **exatamente** o lockfile e falha se divergir. É a defesa contra dependência que entrou sem passar pelo lockfile |
| `fetch-depth: 0` | Sem o histórico, não há diff contra a base, e metade do portão não funciona |
| `concurrency` com cancelamento | Agente empurra commits em rajada; sem isso você paga por execuções obsoletas |
| Job rápido separado do lento | Falha em 40 segundos em vez de 15 minutos |

---

## 3 · Agente **dentro** do CI: como fazer sem se machucar

Casos legítimos: triagem de falha, revisão automática, atualização de
dependência, resumo de PR, geração de changelog.

### As cinco regras

| Regra | Implementação |
|---|---|
| **1. Nunca decide** | Escreve comentário ou *issue*. Nunca falha o build por opinião dele |
| **2. Permissão mínima** | `contents: read` + só o que precisa (`issues: write`) |
| **3. Sem segredo de produção** | Nunca dê a ele credencial de banco, chave de deploy, token de pagamento |
| **4. Ferramentas restritas** | Lista explícita do que pode executar |
| **5. Teto de tempo e custo** | `timeout-minutes` e limite de passos |

### O perigo específico: `pull_request_target`

```yaml
# PERIGOSO — não faça isto com agente
on:
  pull_request_target:      # roda com segredos do repositório
```

`pull_request_target` executa no contexto do repositório base, **com acesso aos
segredos**, mas fazendo checkout de código de um PR possivelmente externo. Com
um agente lendo o conteúdo desse PR, um atacante escreve instruções num arquivo
e o agente as executa **com os seus segredos na mão**.

**Use `pull_request`** (sem segredos, código não confiável) para tudo que toque
conteúdo de PR externo.

---

## 4 · Dependências: o ponto que a IA piorou

Modelos alucinam nomes de pacote; atacantes registram esses nomes; `install`
executa código. É o *slopsquatting*, e a pesquisa mostra que cerca de **20% das
amostras de código geradas** citam ao menos um pacote inexistente, com **58% dos
nomes se repetindo** entre execuções — ou seja, o alvo é previsível e
registrável.

### Defesas, em ordem de eficácia

| Defesa | O que resolve |
|---|---|
| **Lockfile commitado + `npm ci` / `--require-hashes`** | Impede que qualquer coisa fora do lockfile entre |
| **Portão que bloqueia dependência nova** | Toda adição passa por decisão humana ([projeto-modelo](07-projeto-modelo/README.md)) |
| **Registro espelhado com lista de permissão** | Nem chega a resolver o nome |
| **`--ignore-scripts` na instalação** | Impede `postinstall` de executar |
| **Verificação de existência** | Detecta alucinação; **não** detecta malícia |
| **SCA / SBOM** (Dependabot, Snyk, `osv-scanner`) | Vulnerabilidade conhecida em pacote legítimo |

> **Distinção que salva:** verificar existência protege contra **erro**;
> lockfile e revisão protegem contra **ataque**. O atacante quer que o pacote
> exista. Não confunda as duas coisas — e não pare na primeira.

---

## 5 · Deploy: o que muda

Menos do que parece, e por uma razão boa: **as práticas que protegem contra
código humano ruim protegem contra código de agente ruim.**

O que ficou mais importante:

| Prática | Por que ficou mais importante |
|---|---|
| **Reversão rápida** | Volume de mudança maior = mais reversões |
| **Feature flag** | Desligar sem redeploy; separar entrega de ativação |
| **Deploy progressivo** (canário) | Expor 1% antes de 100% |
| **Observabilidade com linha de base** | Se você não sabia a taxa de erro de ontem, não sabe se piorou |
| **Commits pequenos** | Reverter um commit, não um trimestre |
| **Orçamento de erro** (SLO) | Dá um critério objetivo para desacelerar |

### O que **não** deve mudar

- Agente **não** faz deploy em produção.
- Agente **não** tem credencial de produção.
- Agente **não** roda migração de banco em produção.
- Agente **não** tem acesso a dado pessoal de cliente.

**Motivo, e é o mesmo dos quatro:** essas ações são irreversíveis ou de raio
ilimitado. Automatizar o reversível é economia; automatizar o irreversível é
apostar.

> Assistente de incidente é caso diferente e legítimo: um agente **com acesso
> somente leitura** a logs e métricas, que produz hipóteses. Leitura, não escrita.

---

## 6 · Métricas que importam quando há agentes

As quatro métricas DORA clássicas continuam valendo. Acrescente estas:

| Métrica | O que revela | Linha de base 2026 |
|---|---|---|
| **Tempo até a primeira revisão** | Se a fila virou o gargalo | PR de agente: 1.055 min vs. 201 min (LinearB) |
| **Tamanho médio do PR** | Se as fatias estão grandes demais | IA: 408 linhas vs. 157 no p75 |
| **Taxa de aceitação sem modificação** | Qualidade real do que é gerado | 32,7% (IA) vs. 84,4% (humano) |
| **Cobertura do diff** | Se código novo entra sem verificação | — |
| **Duplicação (tendência)** | Erosão estrutural | +81% desde 2023 (GitClear) |
| **Reversões por semana** | Se a velocidade custou estabilidade | — |
| **Custo de API por PR fundido** | Se o gasto acompanha o valor | — |

### A métrica que eu evitaria

**"Percentual de código escrito por IA."** É irresistível para diretoria e é
péssima, por três razões:

1. Otimizá-la incentiva delegar o que não deveria ser delegado.
2. Ela não se correlaciona com valor entregue.
3. Ela é trivialmente inflável — basta gerar mais linhas, o que é exatamente o
   comportamento que se quer evitar.

Se você precisa reportar algo para a diretoria, reporte **vazão da `main`** e
**estabilidade**. São as que pagam a conta.

---

## Autoteste

1. Enuncie a regra que organiza o pipeline. Por que ela não é desconfiança do
   modelo?
2. Qual é a diferença entre a caixa "portão" e a caixa "assistentes"?
3. Por que `npm ci` e não `npm install` no CI?
4. Por que `fetch-depth: 0` é necessário para o portão?
5. Cite as cinco regras para agente dentro do CI.
6. Por que `pull_request_target` é perigoso com agente? Qual é a alternativa?
7. Qual é a diferença entre proteger-se contra erro e contra ataque no caso de
   dependências?
8. Cite quatro coisas que um agente nunca deve fazer em produção, e a razão
   comum entre elas.
9. Cite quatro métricas úteis quando há agentes e o que cada uma revela.
10. Por que "percentual de código escrito por IA" é uma métrica ruim?

---

**Anterior:** [20-git-e-fluxo-de-trabalho](20-git-e-fluxo-de-trabalho.md) ·
**Próximo:** [22-seguranca](22-seguranca.md)
