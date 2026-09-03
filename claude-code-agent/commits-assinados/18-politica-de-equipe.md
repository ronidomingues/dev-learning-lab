# 18 · Política de equipe — exigir assinatura sem travar o time

> Nível: intermediário → avançado · Atualizado em 13/08/2026

A parte técnica leva 20 minutos. A implantação leva semanas, porque o problema é social. Este
arquivo é o roteiro que funciona, e o inventário do que quebra.

---

## 1. As duas travas do GitHub, e a diferença que importa

| | **Ruleset** | **Branch protection rule** |
|---|---|---|
| status | o mecanismo atual | legado, ainda funciona |
| escopo | repositório **ou organização inteira** | um repositório |
| aplicação em camadas | rulesets se somam entre si e com as regras antigas | não |
| modo "só avisar" | **sim** (`Evaluate`) | não |
| o que verifica ao exigir assinatura | apenas os commits **não alcançáveis a partir de outros ramos** | não verifica, a menos que você também restrinja a criação de ramos |
| disponibilidade | público no Free; privado no Pro/Team/Enterprise | idem |

**Use ruleset.** O modo `Evaluate` sozinho já justifica: ele registra o que *teria* sido
bloqueado, sem bloquear nada. É a diferença entre descobrir os problemas antes ou depois de
travar a equipe numa sexta-feira.

### Criar o ruleset

Pela interface: *Settings → Rules → Rulesets → New branch ruleset*
→ alvo `main` → marque **Require signed commits**.

Pela API, que é o caminho para replicar em vários repositórios:

```bash
gh api --method POST repos/{owner}/{repo}/rulesets \
  -f name='Exigir assinatura em main' \
  -f target='branch' \
  -f enforcement='evaluate' \
  -F 'conditions[ref_name][include][]=refs/heads/main' \
  -F 'rules[][type]=required_signatures'
```

> `enforcement` aceita `disabled`, `evaluate` e `active`. Comece em `evaluate`.

Ver o que teria sido bloqueado:

```bash
gh api repos/{owner}/{repo}/rulesets/{id}/history
gh api "orgs/{org}/rulesets/rule-suites?rule_suite_result=fail" --paginate
```

---

## 2. O roteiro de implantação, em seis semanas

Este é o plano que eu recomendo, e cada fase existe por causa de um jeito específico de dar
errado.

### Semana 0 — medir antes de decidir

```bash
# quantos commits, e de quem, entrariam em desacordo?
gh api "repos/$ORG/$REPO/commits?since=$(date -d '90 days ago' +%F)" --paginate \
  --jq '.[] | [.commit.verification.verified, .commit.author.name] | @tsv' \
| sort | uniq -c | sort -rn
```

Se a resposta for "80 % já assina", o resto é fácil. Se for "12 %", você tem um projeto de
mudança organizacional, não uma configuração.

Inventarie também, e isto é o que se esquece:
- quais **bots** commitam neste repositório;
- quem usa **cliente gráfico** (o suporte a assinatura varia muito);
- quem trabalha de **mais de uma máquina**;
- se algum fluxo depende de **Rebase and merge**.

### Semana 1 — documentar e anunciar

Um documento interno de uma página, com os comandos prontos, apontando para o
[04-como-comecar.md](04-como-comecar.md). Anuncie a data em que a trava entra, e **não a
antecipe**.

### Semanas 2–3 — mutirão

Uma sessão de 30 minutos onde todo mundo configura junto resolve mais que três semanas de
mensagens. Os quatro comandos:

```bash
ssh-keygen -t ed25519 -C "$(git config --get user.email)" -f ~/.ssh/id_assinatura
gh ssh-key add ~/.ssh/id_assinatura.pub --type signing --title "$(hostname)"
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_assinatura.pub
git config --global commit.gpgsign true
git config --global tag.gpgSign true
```

Circule pela sala conferindo a lista de **SSH signing keys** de cada um. Cadastrar como
*Authentication key* é o erro que mais aparece nesse momento.

### Semana 4 — ligar em `evaluate` e medir de novo

Deixe rodando uma semana. Cada falha registrada é uma conversa que você não vai ter no dia da
trava.

### Semana 5 — ligar em `active` numa segunda-feira de manhã

Nunca numa sexta. Nunca na véspera de uma release. Tenha alguém de plantão para o dia.

### Semana 6 — retrospectiva e automação

Adicione ao onboarding de pessoas novas. Adicione a verificação à CI
([17](17-automacao-e-ci.md)). Documente o procedimento de saída (§ 5).

---

## 3. O que quebra — inventário

| O que quebra | Por quê | Solução |
|---|---|---|
| **Bots de release e de formatação** | não assinam | migrar para a API do GitHub ([17](17-automacao-e-ci.md)) |
| **Rebase and merge** | o GitHub não consegue assinar commits criados no servidor por esse caminho | desabilite o botão em *Settings → Pull Requests*; use merge ou squash |
| **Clientes gráficos** | suporte irregular a assinatura | atualizar, configurar, ou commitar pelo terminal |
| **Quem trabalha de duas máquinas** | a segunda não está configurada | uma chave por máquina, todas cadastradas |
| **Commits importados** (`git am`, migração de outro sistema) | vêm sem assinatura | re-assinar em lote antes de importar |
| **Submódulos** | o ruleset é por repositório | ruleset de organização |
| **Colaboradores externos** | não têm as instruções, nem contexto | ruleset com *bypass* explícito, ou onboarding do PR |
| **Histórico antigo** | milhares de commits sem assinatura | ver § 4 |

---

## 4. O histórico antigo

A pergunta que sempre vem: *"e os 8.000 commits que já existem?"*

**Deixe-os em paz.** Três razões:

1. Reescrever o histórico muda todos os hashes, quebra referências de issues, PRs, releases,
   *changelogs*, marcadores em ferramentas de deploy e todo clone local de todo mundo.
2. Re-assinar commits antigos com a sua chave, hoje, seria uma afirmação **falsa** —
   você estaria criando evidência criptográfica de que assinou algo em 2019 que na verdade
   assinou hoje. Isso corrói exatamente o valor do mecanismo.
3. Não resolve nada: o ruleset olha os commits **novos**.

O que funciona é traçar uma linha e documentá-la:

```markdown
## Política de assinatura
A partir de 15/09/2026, todos os commits em `main` são assinados e verificados.
Commits anteriores a essa data não são assinados — isso é esperado.
```

E, se você quiser um marco criptográfico do ponto de virada, **assine uma tag** ali:

```bash
git tag -s marco-assinatura -m "A partir daqui, todos os commits são assinados"
git push origin marco-assinatura
```

Isso é honesto e é útil: a tag assinada atesta o estado do histórico naquele momento, sem
mentir sobre o passado.

---

## 5. Onboarding e offboarding

### Entrada

Checklist para o primeiro dia:

- [ ] gerar chave de assinatura
- [ ] cadastrar como **Signing key**
- [ ] verificar o e-mail corporativo na conta do GitHub
- [ ] `git config --global` das quatro linhas
- [ ] fazer um commit de teste e confirmar o `Verified`
- [ ] (se a equipe versiona) acrescentar a chave ao `allowed_signers`

### Saída — o que quase ninguém faz

Quando alguém sai, a chave de assinatura **continua funcionando** para tudo que já foi
assinado (por desenho, [15 § 3](15-verificacao-no-github.md)), e a conta continua podendo
assinar se ainda tiver acesso.

- [ ] remover a pessoa da organização (isso é o que corta o acesso de escrita)
- [ ] no `allowed_signers` versionado, **não apague a linha** — ponha
      `valid-before="<data de saída>"`, para o passado continuar verificável
- [ ] se houver suspeita de comprometimento, aí sim: revogar, e reavaliar o que foi assinado

### Rotação e perda de chave

| Situação | O que fazer |
|---|---|
| troca de notebook | chave nova; a antiga ganha `valid-before`; remova-a do GitHub |
| chave perdida (sem vazamento) | chave nova; o passado continua verificado |
| **chave comprometida** | remova do GitHub **imediatamente**; revogue (GPG); audite tudo que ela assinou desde a data provável do vazamento; comunique |
| chave GPG vencida | `gpg --quick-set-expire`, e reenvie a pública ao GitHub |

---

## 6. Versionar o `allowed_signers`: o debate

Guardar `.github/allowed_signers` no repositório permite que qualquer pessoa clone e verifique
o histórico sem montar nada. A objeção é legítima: **quem tem escrita no repositório pode se
acrescentar ao arquivo**.

A objeção é verdadeira e, ainda assim, versionar costuma valer a pena — desde que se entenda o
papel de cada peça:

| Peça | Papel |
|---|---|
| `allowed_signers` versionado | **conveniência de verificação** para quem clona |
| ruleset do GitHub | **controle de acesso** — consulta as chaves das contas, não o arquivo |
| revisão de PR | é o que impede a alteração indevida do próprio arquivo |

Se o arquivo é protegido por revisão obrigatória (e um `CODEOWNERS` apontando para o time de
segurança), alterá-lo exige aprovação — o que já é mais do que a maioria dos controles tem.

Quem não pode aceitar essa premissa não deve versionar: distribua o arquivo por outro canal,
ou gere-o da API ([06 § 7](06-exemplos.md)).

---

## 7. O argumento para a liderança

Se você precisa aprovar isso com alguém que não é técnico, os quatro pontos que funcionam:

1. **Custo:** zero em licença, ~20 minutos por pessoa, uma vez.
2. **Atribuição:** em incidente ou auditoria, "foi essa pessoa" deixa de ser suposição.
3. **Contenção:** credencial roubada deixa de bastar para injetar código no nome de alguém —
   e credencial roubada é o vetor mais comum que existe.
4. **Conformidade:** exigências de proveniência de software (EO 14028 nos EUA, CRA europeu)
   caminham nessa direção; é mais barato fazer agora.

E o ponto de honestidade, que você deve dizer antes que alguém descubra: **isso não impede
código malicioso.** No caso do xz-utils, o backdoor entrou com commits perfeitamente
assinados. Assinatura resolve *quem*, não *o quê*. Vender além disso é como se constrói
confiança indevida em um controle — e é o que faz a próxima auditoria doer.

---

## Autoteste

1. Por que usar ruleset em vez de branch protection rule?
2. Para que serve o modo `evaluate`, e por que pular essa fase é caro?
3. Cite quatro coisas que quebram ao ligar a exigência.
4. Por que **não** re-assinar o histórico antigo? Dê a razão ética, além da técnica.
5. O que fazer no `allowed_signers` quando alguém sai da empresa?
6. Qual é a objeção legítima a versionar o `allowed_signers`, e por que ainda assim vale?
7. Que botão de merge precisa ser desabilitado, e por quê?
8. Qual é o limite honesto que você deve declarar ao propor isso à liderança?

*(Respostas: 1 — escopo de organização, camadas e, sobretudo, o modo `evaluate`. 2 — registra o
que teria sido bloqueado sem bloquear; pular significa descobrir os problemas com a equipe já
travada. 3 — bots, *Rebase and merge*, clientes gráficos, segunda máquina de cada pessoa,
commits importados, colaboradores externos. 4 — tecnicamente quebra hashes e referências;
eticamente, cria evidência falsa de que você assinou no passado algo que assinou hoje. 5 —
acrescentar `valid-before` com a data de saída, em vez de apagar a linha. 6 — quem tem escrita
pode se acrescentar ao arquivo; vale porque o arquivo é conveniência de verificação, e o
controle de acesso é o ruleset, com o arquivo protegido por revisão. 7 — *Rebase and merge*,
porque o GitHub não consegue assinar os commits que cria por esse caminho. 8 — que assinatura
resolve atribuição, não qualidade nem malícia — como o xz-utils demonstrou.)*

---

**Próximo:** [19-como-escolher.md](19-como-escolher.md).
