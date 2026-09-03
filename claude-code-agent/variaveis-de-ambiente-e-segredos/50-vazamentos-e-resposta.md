# 50 · Vazamentos — prevenir, detectar e responder

`Nível: intermediário a avançado` · `Atualizado em: 14/08/2026`

> **Se você acabou de descobrir um vazamento, vá direto para a
> [§4 — as duas primeiras horas](#4-resposta-a-incidente--as-duas-primeiras-horas).**
> Leia o resto depois.

---

## 1. A regra que organiza tudo

> **Segredo que vazou está queimado. Ponto.**
> Não existe "apagar do Git e ficar tudo bem". A única resposta correta é
> **rotacionar**. Todo o resto — reescrever histórico, apagar mensagens, pedir para
> a pessoa deletar — é limpeza cosmética que se faz **depois**, e nunca no lugar.

Por quê, concretamente:

- **Robôs varrem o GitHub em tempo real.** Uma chave da AWS num repositório público é
  encontrada e usada em **menos de um minuto**. Não é lenda: é o modelo de negócio de
  uma indústria inteira, que minera criptomoeda na sua conta.
- Se o repositório é público, alguém já **forkou** ou clonou. Forks não somem quando
  você reescreve o histórico.
- Nos serviços de hospedagem, objetos Git "órfãos" continuam acessíveis por URL
  direta por um tempo, mesmo depois de um force-push.
- Backups, espelhos, caches de CI, imagens Docker publicadas, o Slack, a máquina de
  quem já saiu.

---

## 2. Prevenir — quatro camadas, e por que precisam ser quatro

| Camada | Ferramenta | Contornável? | Custo |
|---|---|---|---|
| 1. Antes de escrever | `.gitignore` (do projeto **e** global) | sim (`git add -f`) | zero |
| 2. Antes do commit | gancho `pre-commit` + gitleaks | sim (`--no-verify`) | minutos |
| 3. No servidor | **push protection** do GitHub/GitLab | não | zero em repo público |
| 4. Contínua | secret scanning + gitleaks no CI | não | minutos |

Nenhuma sozinha basta: 1 e 2 são locais e contornáveis; 3 depende da plataforma e dos
padrões que ela conhece; 4 encontra depois do fato. **Juntas, cobrem quase tudo.**

### Camada 1 — `.gitignore` global, hoje

```bash
git config --global core.excludesfile ~/.gitignore_global
printf '.env\n.env.*\n!.env.example\n*.pem\n*.key\nid_rsa\nid_ed25519\n.aws/credentials\n' >> ~/.gitignore_global
```

Isso protege **você** em todos os repositórios. O `.gitignore` do projeto (versionado)
continua obrigatório, porque protege a **equipe**.

### Camada 2 — gancho de pre-commit

Script completo em [06-exemplos.md #13](06-exemplos.md). Versionado com `pre-commit`:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.28.0
    hooks: [{ id: gitleaks }]
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: detect-private-key
      - id: check-added-large-files
```

```bash
pip install pre-commit && pre-commit install
```

**Teste que funciona** — gancho não testado é gancho que não existe:

```bash
echo 'AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY' > t.txt
git add t.txt && git commit -m teste     # deve ser RECUSADO
git restore --staged t.txt && rm t.txt
```

### Camada 3 — push protection

O **GitHub secret scanning é gratuito e automático em repositórios públicos**, e a
**push protection** bloqueia o push no servidor para dezenas de tipos de segredo
conhecidos — inclusive em repositórios públicos gratuitos. Em 2026 a lista de
detectores com bloqueio por padrão continuou crescendo (Airtable, Databricks, Heroku,
PostHog, Shopify, entre outros).

Verifique em: Settings → Code security → Secret scanning.

### Camada 4 — CI

```yaml
- run: |
    docker run --rm -v "$PWD:/repo" zricethezav/gitleaks:latest \
      git /repo --no-banner --redact --exit-code 1
```

`--redact` é obrigatório: sem ele, o gitleaks **imprime o segredo** no log do CI, que
fica guardado por 90 dias. Encontrar o vazamento não pode criar um segundo.

---

## 3. Detectar o que já está lá

### Varredura de histórico

```bash
gitleaks git . --no-banner --redact
```

```bash
# trufflehog: VERIFICA se a credencial ainda está ativa
docker run --rm -v "$PWD:/repo" trufflesecurity/trufflehog:latest \
  git file:///repo --only-verified
```

**A diferença entre as duas ferramentas é conceitual, e vale entender:**
o gitleaks pergunta *"esta string parece um segredo?"* — é um motor de regex, roda em
menos de um segundo num diff, licença MIT, ideal para pre-commit e CI.
O trufflehog pergunta *"esta credencial funciona agora?"* — chama o provedor para
verificar. É mais lento e insubstituível numa varredura de histórico, porque separa
o achado real dos milhares de falsos positivos que um histórico longo produz.

**O stack pragmático de 2026:** gitleaks no pre-commit e no CI + trufflehog nas
varreduras de histórico + secret scanning da plataforma.

### Outros lugares para procurar (as pessoas só olham o Git)

```bash
# no histórico do shell
grep -riE '(password|secret|token|api_?key)=' ~/.bash_history ~/.zsh_history 2>/dev/null

# em imagens Docker
docker history --no-trunc minha-imagem | grep -iE 'secret|token|password'
docker run --rm -it --entrypoint sh minha-imagem -c 'ls -la /app; cat /app/.env 2>/dev/null'

# no seu site (o clássico do PHP)
curl -s -o /dev/null -w '%{http_code}\n' https://seusite.com.br/.env
# esperado: 403 ou 404

# em bundles de front-end
grep -rE '(sk_live|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|xox[bp]-)' dist/ build/

# em notebooks
grep -rl 'os.environ' *.ipynb | xargs grep -l 'sk_\|AKIA' 2>/dev/null
```

---

## 4. Resposta a incidente — as duas primeiras horas

**A ordem importa mais que a velocidade.** Fazer na ordem errada destrói evidência ou
prolonga a exposição.

### ⏱️ 0–15 min — CONTER

**1. Rotacione ou revogue. Primeiro. Antes de qualquer outra coisa.**

```bash
aws iam delete-access-key --access-key-id AKIA...          # AWS
# Stripe: painel → Developers → API keys → Roll key
# banco: ALTER USER app WITH PASSWORD 'nova';  (ou crie novo usuário)
```

Não "avise o time primeiro". Não "investigue primeiro". Não "espere a janela de
manutenção". **Revogue.** Um serviço fora do ar por 10 minutos é infinitamente melhor
que uma credencial ativa nas mãos de terceiros.

**2. Confirme que a credencial antiga morreu:**

```bash
AWS_ACCESS_KEY_ID=AKIA... AWS_SECRET_ACCESS_KEY=... aws sts get-caller-identity
# esperado: InvalidClientTokenId
```

### ⏱️ 15–60 min — AVALIAR

**3. O que essa credencial permitia?** Escreva. Seja pessimista.

**4. Foi usada por outra pessoa?**

```bash
aws cloudtrail lookup-events --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=AKIA... --max-results 50
```

Procure em todo log disponível: IPs desconhecidos, geografias improváveis, horários
esquisitos, volume anômalo. No banco: `pg_stat_activity`, log de conexões. No
provedor de API: painel de uso.

**5. Qual foi a janela de exposição?**

```bash
git log -S 'sk_live_' --oneline --all      # quando o segredo entrou no histórico
git log --format='%H %ad %an' --date=iso -1 <commit>
```

Público desde então? Quantos clones/forks? A janela define a gravidade.

### ⏱️ 1–2 h — ERRADICAR E COMUNICAR

**6. Limpe o histórico** — agora sim, e sabendo que é cosmético:

```bash
pip install git-filter-repo
git filter-repo --path .env --invert-paths --force
```

Ou, para um valor específico:

```bash
echo 'sk_live_abc123==>REMOVIDO' > substituicoes.txt
git filter-repo --replace-text substituicoes.txt
```

```bash
git push origin --force --all
git push origin --force --tags
```

🚨 **O que `git filter-repo` NÃO resolve:**
- forks e clones existentes;
- objetos em cache no servidor de hospedagem;
- **todo mundo do time precisa reclonar** — quem fizer `git pull` reintroduz o commit;
- backups, espelhos, imagens Docker, logs de CI.

**Peça ao suporte da plataforma que remova as referências em cache** — o GitHub faz
isso mediante solicitação.

**7. Comunique.**

| Para quem | Quando | O quê |
|---|---|---|
| Time | imediatamente | o que aconteceu, o que já foi feito, o que precisam fazer (reclonar) |
| Segurança/gestão | < 1 h | escopo, janela, evidência de uso indevido |
| **Clientes afetados** | conforme a lei | ver abaixo |
| Provedor da credencial | se houve uso indevido | Stripe, AWS etc. costumam ajudar |

⚠️ **LGPD (Lei 13.709/2018), Brasil:** se o vazamento pode acarretar risco ou dano
relevante aos titulares, é obrigatório comunicar a **ANPD** e os titulares em prazo
razoável. A ANPD estabeleceu o prazo de **3 dias úteis** para a comunicação de
incidente. **Consulte o jurídico** — este curso não é aconselhamento legal, e a
decisão de notificar não é técnica.

**8. Post-mortem sem culpados**, em até uma semana:

- Como o segredo entrou? (a resposta quase nunca é "fulano foi descuidado")
- Qual camada de prevenção faltava?
- Quanto tempo até detectar? Como reduzir?
- A rotação funcionou? Quanto demorou? O que deu errado?
- Qual mudança de **processo** impede a repetição?

> **Cultura importa aqui.** Um time que pune quem commitou o `.env` é um time onde a
> próxima pessoa vai esconder o erro por três dias. E três dias de exposição é o
> desastre; o commit em si é só um acidente.

---

## 5. Casos concretos

### Caso A — `.env` commitado num repositório privado

Menos grave, **não** trivial: todos os colaboradores atuais e passados têm acesso,
está nos clones locais deles, e nos backups.

Ação: rotacionar tudo o que estava no arquivo; limpar o histórico; verificar quem
teve acesso ao repositório desde a data do commit.

### Caso B — chave da AWS num repositório público

**Emergência.** Robôs acham em menos de um minuto e criam instâncias caras para
minerar criptomoeda. Já houve contas com dezenas de milhares de dólares em horas.

```bash
aws iam delete-access-key --access-key-id AKIA...        # 1. AGORA
aws cloudtrail lookup-events --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=AKIA...
aws ec2 describe-instances --query 'Reservations[].Instances[?State.Name==`running`]' --output table
# 2. em TODAS as regiões — os atacantes usam as menos vigiadas
```

Depois: abra chamado no suporte da AWS. Eles costumam perdoar cobrança fraudulenta
quando você agiu rápido e documentou.

### Caso C — `.env` acessível pela web (`https://site/.env`)

Se `curl -o /dev/null -w '%{http_code}' https://seusite/.env` devolve **200**, o
vazamento **está acontecendo agora** e há varredores testando esse caminho
continuamente.

1. bloqueie no servidor web (regra do [16-php.md §6](16-php.md));
2. rotacione tudo;
3. veja no log de acesso quem baixou:
   ```bash
   grep -E 'GET /\.env' /var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -rn
   ```
4. corrija a estrutura: o `.env` não pode estar em diretório servido.

### Caso D — segredo no log

Retenção costuma ser de 30 a 90 dias, o log foi para um serviço de terceiro, e vários
sistemas o indexaram.

1. rotacione;
2. apague o que der (muitos serviços não permitem apagar seletivamente);
3. **corrija a origem** — adicione redação ([06-exemplos.md #9](06-exemplos.md));
4. verifique quem tem acesso ao serviço de log. Frequentemente é mais gente do que
   tem acesso à produção, o que inverte todo o seu modelo de controle.

---

## 6. Checklist de resposta (imprima)

```
[ ]  1. ROTACIONAR / REVOGAR                    ← primeiro, sempre
[ ]  2. Confirmar que a credencial antiga morreu
[ ]  3. Mapear o que ela permitia
[ ]  4. Procurar uso indevido nos logs
[ ]  5. Determinar a janela de exposição
[ ]  6. Limpar o histórico (git filter-repo) + pedir limpeza de cache à plataforma
[ ]  7. Avisar o time (todos precisam RECLONAR)
[ ]  8. Avaliar obrigação legal de notificação (LGPD/ANPD) com o jurídico
[ ]  9. Procurar o MESMO segredo em outros lugares (logs, imagens, backups, Slack)
[ ] 10. Instalar a camada de prevenção que faltava
[ ] 11. Post-mortem sem culpados, em até 7 dias
[ ] 12. Adicionar o caso ao inventário de segredos
```

---

## Autoteste

1. Por que "apagar do Git" não resolve um vazamento?
2. Quais são as quatro camadas de prevenção, e por que nenhuma basta sozinha?
3. Por que `gitleaks` sem `--redact` no CI cria um segundo vazamento?
4. Qual a diferença conceitual entre gitleaks e trufflehog?
5. Qual é o **primeiro** passo da resposta a incidente, e por que não é "avisar o time"?
6. O que `git filter-repo` não resolve? Cite quatro coisas.
7. Por que todo mundo precisa reclonar depois de um `filter-repo`?
8. No caso da chave AWS pública, por que verificar **todas** as regiões?
9. Qual o prazo estabelecido pela ANPD para comunicação de incidente?
10. Por que punir quem commitou o `.env` piora a segurança do time?

---

**Fontes consultadas em 14/08/2026:** docs.github.com (secret scanning, push
protection, removing sensitive data) · github.com/newren/git-filter-repo ·
github.com/gitleaks/gitleaks · trufflesecurity.com · gov.br/anpd (comunicação de
incidente de segurança) · Lei 13.709/2018 (LGPD).
**Aviso:** o conteúdo sobre LGPD é orientação geral, **não é aconselhamento jurídico**.

**Próximo:** [55-entrega-ao-cliente.md](55-entrega-ao-cliente.md) · Voltar ao [mapa](00-MAPA.md)
