# 17 · Automação, bots e CI

> Nível: intermediário → avançado · Atualizado em 13/08/2026

O dia em que você liga a exigência de assinatura, o robô para. Este arquivo trata dos
commits que **não** são feitos por gente: liberadores de versão, Dependabot, bots de
formatação, scripts de migração. E do erro conceitual que mais se comete aqui — confundir
*signoff* com assinatura.

---

## 1. Primeiro: `-s` não é `-S`

| | `git commit -s` | `git commit -S` |
|---|---|---|
| nome | `--signoff` | `--gpg-sign` |
| o que faz | acrescenta `Signed-off-by: Nome <email>` ao final da mensagem | acrescenta uma assinatura criptográfica |
| criptografia | **nenhuma** | sim |
| pode ser forjado? | **trivialmente** — é texto | não, sem a chave |
| o que significa | **DCO**: declaração jurídica de que você tem o direito de contribuir aquele código | prova de posse de chave |
| nasceu | 2004, no kernel Linux, depois do processo da SCO | 2012 |

Os dois são úteis e resolvem problemas **diferentes**: o DCO é um instrumento de licenciamento
(você afirma ter o direito de contribuir), a assinatura é um instrumento de atribuição. Muitos
projetos exigem os dois.

```bash
git commit -s -S -m "corrige X"    # os dois de uma vez
```

Se alguém na sua organização disser "já exigimos DCO, não precisamos assinar", a resposta
curta é: DCO é uma linha de texto que qualquer um digita.

---

## 2. As quatro maneiras de um bot assinar

### a) Commit pela API do GitHub — **a mais simples, e a que eu recomendo**

Commits criados pela API REST/GraphQL são assinados **pelo GitHub** e saem `Verified`, sem
que você precise gerenciar chave nenhuma.

```bash
gh api --method PUT repos/{owner}/{repo}/contents/VERSION \
  -f message="chore: bump para 1.4.0" \
  -f content="$(printf '1.4.0' | base64)" \
  -f sha="$(gh api repos/{owner}/{repo}/contents/VERSION --jq .sha)" \
  -f branch=main
```

Ou, para várias mudanças de uma vez, a mutação GraphQL `createCommitOnBranch`:

```bash
gh api graphql -f query='
  mutation($input: CreateCommitOnBranchInput!) {
    createCommitOnBranch(input: $input) { commit { url } }
  }' -f input='{
    "branch": {"repositoryNameWithOwner":"org/repo","branchName":"main"},
    "message": {"headline":"chore: atualiza dependências"},
    "expectedHeadOid": "'"$(git rev-parse HEAD)"'",
    "fileChanges": {"additions":[{"path":"package-lock.json","contents":"<base64>"}]}
  }'
```

**Vantagens:** zero segredo para vazar, zero chave para rotacionar, sempre `Verified`.
**Desvantagens:** você não usa `git push` — precisa montar a chamada com o conteúdo em base64,
e o `expectedHeadOid` é obrigatório (o que, na verdade, é bom: dá atomicidade).

### b) GitHub App com chave própria

Um GitHub App tem identidade própria e um token de instalação de curta duração. Combinado
com a API acima, é o arranjo mais limpo para automação séria: o bot tem cara de bot no
histórico, e permissões mínimas e auditáveis.

### c) Chave dedicada num *secret*

O caminho tradicional. Funciona, e tem custo de manutenção real.

```yaml
- name: Configurar assinatura
  env:
    CHAVE_PRIVADA: ${{ secrets.BOT_SSH_SIGNING_KEY }}
  run: |
    mkdir -p ~/.ssh && chmod 700 ~/.ssh
    printf '%s\n' "$CHAVE_PRIVADA" > ~/.ssh/bot_signing
    chmod 600 ~/.ssh/bot_signing
    ssh-keygen -y -f ~/.ssh/bot_signing > ~/.ssh/bot_signing.pub
    git config --global gpg.format ssh
    git config --global user.signingkey ~/.ssh/bot_signing.pub
    git config --global commit.gpgsign true
    git config --global user.name  "Robô de Release"
    git config --global user.email "bot@empresa.com"
```

> `ssh-keygen -y` **deriva** a pública da privada. Assim você guarda um segredo só, em vez
> de dois, e não há risco de as duas metades divergirem.

Requisitos para o `Verified` aparecer: a chave precisa estar cadastrada como *Signing key*
numa conta (a do bot), e `bot@empresa.com` precisa ser um e-mail verificado **daquela conta**.

**O que sempre dá errado neste caminho, na ordem em que costuma acontecer:**

1. a chave do bot é uma conta de máquina que ninguém administra, e a senha se perde;
2. o segredo nunca é rotacionado, porque rotacioná-lo quebra o pipeline num dia útil;
3. o e-mail do bot não está verificado, e o `Verified` nunca aparece;
4. a chave vaza num log de CI porque alguém pôs `set -x` no passo errado.

### d) `gitsign` (Sigstore) — sem chave nenhuma

```yaml
permissions:
  id-token: write        # o OIDC do Actions
  contents: write
steps:
  - run: |
      go install github.com/sigstore/gitsign@latest
      git config --local commit.gpgsign true
      git config --local gpg.x509.program gitsign
      git config --local gpg.format x509
      git commit -m "assinado sem chave"
```

O `gitsign` troca o token OIDC do runner por um certificado de ~10 minutos emitido pelo
Fulcio, assina, registra no log de transparência Rekor, e descarta a chave privada. Nada
persistente para vazar — é conceitualmente o desenho mais adequado para CI que existe hoje.

**A ressalva decisiva, verificada em 13/08/2026:** o GitHub **não marca essas assinaturas como
`Verified`** (`reason: unknown_signature_type`), porque a raiz do Sigstore não faz parte do
conjunto de confiança dele. Portanto, num repositório com ruleset exigindo assinatura, o
`gitsign` **não passa**. Ele é excelente e ainda não serve para o caso principal — situação
que dura desde 2022 e não deu sinal de mudar.

---

## 3. Comparação

| Método | Segredo a guardar | `Verified` no GitHub | Passa no ruleset | Complexidade |
|---|---|---|---|---|
| **API do GitHub** | nenhum | **sim** | **sim** | baixa |
| **GitHub App** | chave privada do App | sim | sim | média |
| **Chave em secret** | chave privada | sim, se bem configurado | sim | média, com manutenção |
| **gitsign** | nenhum | **não** | **não** | média |

**Recomendação:** API do GitHub para 90 % dos casos. GitHub App quando o bot precisa de
identidade e permissões próprias. Chave em secret só quando o bot roda **fora** do GitHub
(Jenkins, GitLab CI, servidor próprio) e precisa dar `git push`.

---

## 4. Dependabot, Renovate e afins

- **Dependabot** assina os commits dele com a chave do GitHub — vêm `Verified` de fábrica,
  sem configuração.
- **Renovate**, como GitHub App, também. Como bot auto-hospedado, cai no caso (c).
- **Bots de formatação** (`pre-commit.ci`, `black`, `prettier` em CI) normalmente **não**
  assinam e são a primeira coisa a quebrar ao ligar a exigência. Duas saídas: migrá-los para
  a API, ou fazê-los comentar no PR em vez de commitar — que costuma ser melhor de qualquer
  forma, porque commit automático em PR alheio atrapalha o autor.

---

## 5. Verificar na CI

O workflow completo está em
[`07-projeto-modelo/ci/verificar-assinaturas.yml`](07-projeto-modelo/ci/verificar-assinaturas.yml).
Os três pontos que decidem se ele funciona:

**1. Histórico completo.**

```yaml
- uses: actions/checkout@v5
  with:
    fetch-depth: 0     # sem isto o clone é raso e não há o que auditar
```

Com o padrão `fetch-depth: 1`, `git log base..head` percorre zero commits e o teste passa
sempre. É a falha silenciosa mais comum destes workflows.

**2. Intervalo certo.** Audite `base..head` do PR, não o histórico inteiro — senão o primeiro
commit não assinado de 2019 reprova todo PR para sempre.

**3. Perguntar ao GitHub, não à máquina.** Na CI você não tem `allowed_signers`, então o
melhor que a verificação local alcança é `[U]`. O veredito real:

```bash
gh api "repos/${GITHUB_REPOSITORY}/pulls/${PR}/commits" --paginate \
   --jq '.[] | select(.commit.verification.verified == false) | .sha' > nao_verificados.txt
[ ! -s nao_verificados.txt ]
```

---

## 6. Rodando fora do GitHub

Jenkins, GitLab CI, servidor próprio: aí não há API que assine por você, e o caminho é (c).
Duas regras que evitam incidente:

**Nunca ponha a chave privada em variável de ambiente exposta no log.**

```bash
set +x                                    # antes de qualquer coisa
printf '%s\n' "$CHAVE" > ~/.ssh/bot       # não use echo com a variável em linha de comando
chmod 600 ~/.ssh/bot
```

**Prefira um cofre com credencial de curta duração** (Vault, AWS Secrets Manager com IAM,
GCP Secret Manager) a um segredo estático de CI. O ganho não é teórico: segredo estático de
CI é o que aparece em quase toda análise de incidente de cadeia de suprimentos.

---

## 7. Assinar releases, não só commits

Se o seu artefato final é um binário, um pacote ou uma imagem de container, assinar commits
não cobre o que os usuários realmente baixam. Ferramentas próprias para isso:

| Artefato | Ferramenta |
|---|---|
| tag de release | `git tag -s` (você já sabe) |
| binários / arquivos soltos | `cosign sign-blob`, ou `gpg --detach-sign` |
| imagens de container | `cosign sign` |
| pacotes npm | `npm publish --provenance` (proveniência via Sigstore) |
| pacotes Python | *attestations* do PyPI via Trusted Publishing |
| geral | SLSA, In-toto |

Detalhe importante e frequentemente ignorado: `npm publish --provenance` e as *attestations*
do PyPI usam **Sigstore**, e funcionam bem — o obstáculo do `gitsign` é específico do selo de
commit do GitHub, não do Sigstore em geral.

---

## Autoteste

1. Qual a diferença entre `-s` e `-S`, e por que confundi-los é grave?
2. Por que commits feitos pela API do GitHub saem `Verified` sem nenhum segredo?
3. Cite os quatro problemas típicos do caminho "chave dedicada em secret".
4. Por que `ssh-keygen -y` reduz a superfície de erro num pipeline?
5. Por que o `gitsign` não resolve o caso principal em 2026, apesar de ser o desenho mais
   adequado?
6. Qual configuração faz um workflow de verificação passar sempre sem testar nada?
7. Por que auditar `base..head` e não o histórico inteiro?
8. Assinar commits cobre a segurança do binário que os usuários baixam?

*(Respostas: 1 — `-s` é texto (DCO), `-S` é criptografia; tratar DCO como prova de autoria é
tratar uma linha digitável como evidência. 2 — o commit é criado no servidor, e o GitHub o
assina com a chave dele. 3 — conta de máquina sem dono; segredo nunca rotacionado; e-mail do
bot não verificado; vazamento em log de CI. 4 — deriva a pública da privada, então só um
segredo precisa ser guardado e as metades não divergem. 5 — o GitHub não confia na raiz do
Sigstore e devolve `unknown_signature_type`, o que reprova no ruleset. 6 — `fetch-depth: 1`,
o padrão do `actions/checkout`. 7 — senão um commit antigo não assinado reprova todo PR para
sempre. 8 — não; para isso existem `cosign`, proveniência de npm/PyPI e tag assinada.)*

---

**Próximo:** [18-politica-de-equipe.md](18-politica-de-equipe.md).
