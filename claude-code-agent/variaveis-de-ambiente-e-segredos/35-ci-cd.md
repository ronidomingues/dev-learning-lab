# 35 · CI/CD — onde os segredos entram na esteira

`Nível: intermediário a avançado` · `Atualizado em: 14/08/2026`

O pipeline de entrega é, ao mesmo tempo, **o lugar que mais precisa de credenciais** e
**o lugar mais fácil de exfiltrá-las**: ele executa código de terceiros (ações,
dependências), roda em máquina que você não controla, e tem acesso a tudo.

---

## 1. O modelo de ameaça do CI, em uma imagem

```
   pull request de um estranho
              │
              ▼
   ┌──────────────────────────────────────┐
   │  runner do CI                        │
   │  • executa SEU código                │
   │  • executa AÇÕES de terceiros        │ ← v3 pode virar outra coisa amanhã
   │  • executa DEPENDÊNCIAS (postinstall)│ ← npm install roda scripts arbitrários
   │  • tem acesso aos SEGREDOS           │
   │  • tem rede de saída livre           │ ← exfiltração é um curl
   └──────────────────────────────────────┘
              │
              ▼
     produção
```

**Consequência:** qualquer código que rode no seu pipeline com acesso a segredos pode
enviá-los para fora, e você não vai perceber. Já aconteceu em larga escala com
pacotes npm comprometidos que procuravam variáveis de ambiente do CI e as postavam
em um servidor remoto.

Daí as três regras que orientam tudo neste arquivo:

1. **Menos segredo é melhor que segredo protegido.** Use OIDC.
2. **Menos escopo é melhor que menos segredo.** Segredo por ambiente, não global.
3. **Fixe versões de terceiros por hash**, não por tag móvel.

---

## 2. GitHub Actions

### O básico

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        env:
          API_TOKEN: ${{ secrets.API_TOKEN }}   # só neste passo, não no job inteiro
        run: ./deploy.sh
```

| Conceito | O que é |
|---|---|
| `secrets.X` | valor criptografado; **mascarado** nos logs |
| `vars.X` | valor em texto; **não** mascarado — só para configuração pública |
| Segredo de **organização** | compartilhado por vários repositórios |
| Segredo de **ambiente** | ligado a um `environment:`, com aprovação manual opcional |

### Regras práticas

```yaml
# ❌ segredo no nível do JOB: todos os passos o enxergam, inclusive ações de terceiros
env:
  API_TOKEN: ${{ secrets.API_TOKEN }}

# ✅ segredo só no passo que precisa
steps:
  - run: ./deploy.sh
    env:
      API_TOKEN: ${{ secrets.API_TOKEN }}
```

```yaml
# ✅ fixe ações por hash de commit — uma tag pode ser movida
- uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608  # v4.1.0
```

```yaml
# ✅ permissões mínimas no topo do workflow
permissions:
  contents: read
```

### O mascaramento **não** é garantia

O GitHub substitui o valor exato por `***` nos logs. Mas isso falha quando:

```yaml
- run: echo "${{ secrets.TOKEN }}" | base64      # ❌ o base64 NÃO é mascarado
- run: echo "${{ secrets.TOKEN }}" | rev         # ❌ invertido também não
- run: |
    echo "${{ secrets.TOKEN }}" | fold -w1       # ❌ um caractere por linha
```

Para valores derivados em tempo de execução, marque explicitamente:

```yaml
- run: |
    VALOR=$(gerar-token.sh)
    echo "::add-mask::$VALOR"
    echo "TOKEN=$VALOR" >> "$GITHUB_ENV"
```

E o clássico:

```yaml
- run: set -x           # ❌ imprime cada comando com as variáveis expandidas
```

### 🚨 `pull_request_target` — a armadilha que já vazou muita coisa

```yaml
on: pull_request          # ✅ NÃO recebe segredos em PR de fork. É proteção.
on: pull_request_target   # ⚠️ RECEBE segredos, e roda no contexto do repositório base
```

```yaml
# ☠️ PADRÃO PROIBIDO
on: pull_request_target
jobs:
  build:
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}   # ← código do ESTRANHO
      - run: npm install && npm test                        # ← executa com SEGREDOS
```

Qualquer pessoa abre um PR com um `postinstall` no `package.json` e os seus segredos
saem por um `curl`. Se você **precisa** de `pull_request_target`, não faça checkout do
código do fork, ou faça em um job separado **sem** segredos.

### OIDC — a resposta certa para nuvem

Em vez de guardar uma chave da AWS nos segredos do repositório, o Actions apresenta um
token de identidade assinado pelo GitHub, e a AWS devolve credenciais **temporárias**:

```yaml
permissions:
  id-token: write        # obrigatório para OIDC
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/github-deploy
      aws-region: sa-east-1
      # sem access key, sem secret key — NENHUM segredo armazenado
```

Do lado da AWS, a política de confiança da role restringe **qual repositório e qual
ramo** podem assumi-la:

```json
{
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
      "token.actions.githubusercontent.com:sub": "repo:minha-org/meu-repo:ref:refs/heads/main"
    }
  }
}
```

⚠️ **O erro fatal aqui** é usar `StringLike` com `repo:minha-org/*` ou, pior,
`repo:*`. Isso permite que **qualquer repositório do GitHub** assuma a sua role.
Já causou comprometimentos reais. Use `StringEquals` com o caminho completo, e
inclua o ramo ou o ambiente.

Funciona igual com GCP (Workload Identity Federation), Azure (Federated Credentials),
HashiCorp Vault (auth JWT) e Kubernetes.

| | Chave estática | OIDC |
|---|---|---|
| Armazenada em algum lugar | sim, indefinidamente | **não** |
| Validade | até alguém rotacionar | ~1 hora |
| Se vazar do log | acesso duradouro | expira sozinha |
| Escopo | o que a chave permitir | restringível por repo/ramo/ambiente |
| Rotação | tarefa manual recorrente | inexistente — não há o que rotacionar |

---

## 3. GitLab CI

```yaml
deploy:
  stage: deploy
  environment: production        # variáveis de ambiente protegido
  script:
    - ./deploy.sh
```

| Recurso | Como |
|---|---|
| Variável mascarada | flag "Masked" — exige ≥ 8 caracteres e alfabeto base64 |
| Variável protegida | só em ramos/tags **protegidos** — impede PR malicioso |
| Arquivo | tipo "File": o valor vira arquivo e a variável recebe o **caminho** ⭐ |
| OIDC | `id_tokens:` com `aud:` |

O tipo **File** do GitLab é o padrão `_FILE` embutido na plataforma, e é
subutilizado — perfeito para chave PEM e para o
[projeto-modelo](07-projeto-modelo/README.md).

⚠️ **Sempre marque "Protected"** em segredo de produção. Sem isso, qualquer pessoa
que consiga criar um ramo consegue ler o segredo com um `echo` no `.gitlab-ci.yml`.

---

## 4. Nunca escreva o `.env` no disco do runner

```yaml
# ❌ deixa o arquivo no runner; em runner auto-hospedado, ele PERSISTE
- run: echo "${{ secrets.ENV_FILE }}" > .env

# ✅ passe por variável, ou por stdin, sem tocar o disco
- run: ./deploy.sh
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}

# ✅ com SOPS: decifra e injeta no ambiente, sem arquivo intermediário
- run: sops exec-env secrets/producao.enc.yaml './deploy.sh'
```

⚠️ **Runner auto-hospedado é um caso especialmente perigoso:** o espaço de trabalho
é reaproveitado entre execuções, inclusive de repositórios diferentes. Um `.env`
escrito ali pode ser lido pelo job seguinte. Use runners efêmeros.

---

## 5. Deploy: como o segredo chega ao servidor

### Opção A — SSH com o segredo já no servidor (mais simples e mais segura)

```yaml
- name: Deploy
  run: |
    ssh deploy@servidor 'cd /opt/app && git pull && systemctl restart minha-app'
```

O `/etc/minha-app/env` **já está lá** e nunca passa pelo CI. **O pipeline não tem
acesso aos segredos da aplicação — só à chave de deploy.** Menos superfície,
menos coisa para vazar. É o que eu recomendaria por padrão.

### Opção B — CI injeta a configuração

```yaml
- run: |
    ssh deploy@servidor "sudo install -m 640 -o root -g app /dev/stdin /etc/minha-app/env" <<< "$CONFIG"
  env:
    CONFIG: ${{ secrets.PROD_ENV }}
```

Necessário quando a infraestrutura é recriada a cada deploy (imutável). Aceite que
o CI passa a ser um alvo de alto valor e proteja-o de acordo.

### Opção C — o servidor busca do cofre

```
CI → apenas dispara o deploy
Servidor → autentica no cofre (por identidade de máquina) → busca os segredos
```

O melhor modelo: o CI **nunca** vê segredo de produção. É o que Vault + agente,
ou instância com IAM role, permitem. Ver
[40-cofres-de-segredos.md](40-cofres-de-segredos.md).

---

## 6. Varredura de segredo no pipeline

```yaml
- name: Procurar segredo vazado
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Ou, sem depender de ação de terceiro:

```yaml
- run: |
    docker run --rm -v "$PWD:/repo" zricethezav/gitleaks:latest \
      git /repo --no-banner --redact --exit-code 1
```

`--redact` importa: sem ele, o gitleaks **imprime o segredo encontrado no log do CI**,
que fica guardado por 90 dias. Encontrar o vazamento não pode criar um segundo.

Camadas complementares:

| Camada | Ferramenta | Contornável? |
|---|---|---|
| Antes do commit | gancho `pre-commit` + gitleaks | sim (`--no-verify`) |
| No servidor, antes de aceitar | **push protection** do GitHub | não (sem bypass explícito) |
| No CI | gitleaks/trufflehog | não |
| Contínua | secret scanning da plataforma | não |

O **push protection do GitHub é gratuito e ativo por padrão em repositórios
públicos**, e bloqueia o push com padrões conhecidos. Para repositório privado,
depende do plano — mas o gitleaks no CI cobre o mesmo.

Diferença entre as duas ferramentas mais usadas: **gitleaks** é um motor de regex,
rápido (menos de um segundo num diff), licença MIT — ideal para pre-commit e CI.
**trufflehog** *verifica* se a credencial encontrada ainda está **ativa**, chamando
o provedor — mais lento, e insubstituível numa varredura de histórico, porque separa
o achado real do falso positivo.

---

## 7. Checklist de pipeline

- [ ] Nenhum segredo em texto no arquivo do workflow (só `${{ secrets.X }}`).
- [ ] `permissions:` mínimo no topo do workflow.
- [ ] Segredo declarado **por passo**, não por job.
- [ ] Ações de terceiros fixadas por **hash de commit**.
- [ ] Nada de `pull_request_target` com checkout do código do fork.
- [ ] **OIDC** em vez de chave estática, onde a nuvem suportar.
- [ ] Condição OIDC com `StringEquals` e caminho completo do repositório.
- [ ] Segredos de produção em `environment:` com aprovação manual.
- [ ] Sem `set -x` e sem `echo` de valor derivado de segredo.
- [ ] gitleaks com `--redact` no pipeline.
- [ ] Runners auto-hospedados efêmeros.
- [ ] Nenhum `.env` escrito no disco do runner.
- [ ] Rotação da chave de deploy agendada (data no calendário, não "quando der").
- [ ] Alguém revisa trimestralmente **quem** tem acesso aos segredos do repositório.

---

## Autoteste

1. Por que `on: pull_request` não recebe segredos de um fork, e por que isso é proteção?
2. Descreva o padrão proibido com `pull_request_target` e como ele exfiltra segredo.
3. Cite três formas de burlar o mascaramento de log do GitHub Actions.
4. O que muda, do ponto de vista de risco, ao trocar chave estática por OIDC?
5. Qual é o erro fatal na condição de confiança de uma role OIDC, e como se corrige?
6. Por que fixar ações por hash em vez de tag?
7. Por que `gitleaks` sem `--redact` no CI cria um segundo problema?
8. Qual a diferença prática entre gitleaks e trufflehog?
9. Por que a "Opção A" de deploy (segredo já no servidor) reduz a superfície de ataque?
10. Por que runner auto-hospedado exige cuidado extra com arquivos no espaço de trabalho?

---

**Fontes consultadas em 14/08/2026:** docs.github.com/actions (security hardening,
OIDC, secret scanning) · docs.gitlab.com/ee/ci/variables · github.com/gitleaks/gitleaks ·
github.blog/changelog (secret scanning, 2026).

**Próximo:** [40-cofres-de-segredos.md](40-cofres-de-segredos.md) · Voltar ao [mapa](00-MAPA.md)
