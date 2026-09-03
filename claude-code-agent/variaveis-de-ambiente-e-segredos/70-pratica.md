# 70 · Prática — 12 laboratórios

`Nível: iniciante a avançado` · `Atualizado em: 14/08/2026`

Cada laboratório tem: **objetivo**, **tempo**, **passos**, **verificação** e
**o que você deveria ter aprendido**. Faça na ordem — os últimos dependem dos primeiros.

> Os laboratórios 1 a 6 e 11 foram **executados de verdade** nesta máquina
> (Ubuntu 22.04.5, Node v24.18.0, Python 3.10.12, PHP 8.1.2) em 14/08/2026.
> Os laboratórios 7 a 10 e 12 exigem Docker com permissão, root, ou conta em nuvem —
> estão marcados como **não executados aqui**.

| # | Laboratório | Tempo | Nível |
|---|---|---|---|
| [1](#lab-1--o-ambiente-é-do-processo) | O ambiente é do processo | 10 min | iniciante |
| [2](#lab-2--precedência-medida-com-as-próprias-mãos) | Precedência, medida | 15 min | iniciante |
| [3](#lab-3--a-divergência-de-parsing-entre-linguagens) | A divergência de parsing | 20 min | intermediário |
| [4](#lab-4--configuração-que-falha-rápido) | Configuração que falha rápido | 30 min | intermediário |
| [5](#lab-5--o-padrão-_file) | O padrão `_FILE` | 20 min | intermediário |
| [6](#lab-6--redação-de-log) | Redação de log | 25 min | intermediário |
| [7](#lab-7--vaze-um-segredo-numa-imagem-docker-de-propósito) | Vaze numa imagem Docker | 30 min | intermediário |
| [8](#lab-8--systemd-do-zero) | systemd do zero | 45 min | intermediário |
| [9](#lab-9--sops--age) | SOPS + age | 40 min | avançado |
| [10](#lab-10--cofre-local-com-openbao) | Cofre local com OpenBao | 60 min | avançado |
| [11](#lab-11--simule-um-vazamento-e-responda) | Simule um vazamento | 45 min | avançado |
| [12](#lab-12--rotação-com-sobreposição) | Rotação com sobreposição | 60 min | avançado |

---

## Lab 1 — O ambiente é do processo

**Objetivo:** internalizar que variável de ambiente pertence a um processo, não ao
sistema. **10 min.**

```bash
mkdir -p ~/lab-env && cd ~/lab-env
printf 'console.log("X =", process.env.X ?? "(indefinida)");\n' > x.js
```

```bash
node x.js                      # (indefinida)
X=1 node x.js                  # 1
node x.js                      # (indefinida)  ← não persistiu
export X=2
node x.js                      # 2
```

Abra **outro terminal** e rode `echo $X`. Sai vazio.

Agora a parte que quase ninguém testa:

```bash
export X=pai
bash -c 'echo "filho vê: $X"; export X=filho; echo "filho mudou: $X"'
echo "pai continua: $X"
```

Saída real medida:
```
filho vê: pai
filho mudou: filho
pai continua: pai
```

**Verificação:**
```bash
cat /proc/$$/environ | tr '\0' '\n' | grep '^X='
# esperado: X=pai
```

**Aprendizado:** herança é de mão única. O filho recebe uma **cópia**; nada que ele
faça sobe. É por isso que `./script.sh` com `export` não muda seu shell, mas
`source script.sh` muda.

---

## Lab 2 — Precedência, medida com as próprias mãos

**Objetivo:** provar que o ambiente vence o `.env`. **15 min.**

```bash
cd ~/lab-env
printf 'X=do-arquivo\n' > .env
printf '.env\n' > .gitignore && chmod 600 .env
```

```bash
node --env-file=.env x.js       # do-arquivo
X=do-ambiente node --env-file=.env x.js
```

Saída real: `X = do-ambiente` — **o ambiente venceu**.

Agora prove que a aplicação funciona **sem** o arquivo:

```bash
mv .env .env.guardado
node x.js                       # (indefinida)
X=producao node x.js            # producao   ← funcionou sem .env nenhum
mv .env.guardado .env
```

**Aprendizado:** o `.env` só preenche o que ainda não existe. Em produção as
variáveis já existem, então o arquivo é dispensável — **e é essa a resposta da
pergunta que originou o curso**.

---

## Lab 3 — A divergência de parsing entre linguagens

**Objetivo:** ver, na prática, que `.env` não tem padrão. **20 min.**

```bash
cd ~/lab-env && cat > .env <<'EOF'
SIMPLES=valor
HASH_SEM_ASPAS=abc#123
EXPANSAO=${SIMPLES}/api
EOF
```

```bash
node --env-file=.env -e 'console.log(JSON.stringify({h:process.env.HASH_SEM_ASPAS, e:process.env.EXPANSAO}))'
```
Saída real: `{"h":"abc","e":"${SIMPLES}/api"}`

```bash
python3 -m venv .venv && ./.venv/bin/pip install -q python-dotenv
./.venv/bin/python -c "from dotenv import dotenv_values; v=dotenv_values('.env'); print(repr(v['HASH_SEM_ASPAS']), repr(v['EXPANSAO']))"
```
Saída real: `'abc#123' 'valor/api'`

**Verificação:** as duas saídas são **diferentes** para as mesmas duas linhas.

**Aprendizado:** um `#` sem aspas trunca o valor em Node e não em Python; a expansão
funciona em Python e não em Node. Se serviços em linguagens diferentes leem o mesmo
`.env`, **use só o subconjunto seguro** de [12-formato-dotenv.md](12-formato-dotenv.md).

---

## Lab 4 — Configuração que falha rápido

**Objetivo:** escrever um módulo de configuração que valida tudo e reporta todos os
erros de uma vez. **30 min.**

Copie [`07-projeto-modelo/src/config.mjs`](07-projeto-modelo/src/config.mjs) para um
projeto seu e adapte o contrato. Depois:

```bash
cd 07-projeto-modelo
node src/check-config.mjs                     # deve falhar listando 3 faltas, exit 78
echo "exit=$?"
```

Saída real:
```
❌ Configuração inválida:
   • falta DATABASE_URL
   • falta SESSION_SECRET
   • falta API_KEY
exit=78
```

```bash
DATABASE_URL='nao-e-url' SESSION_SECRET=curto API_KEY=k PORT=99999 node src/check-config.mjs
```

**Exercícios:**
1. Acrescente `SMTP_URL` como obrigatória e rode `npm test` **antes** de tocar no
   `.env.example`. Qual teste falha? Por quê?
2. Faça `PORT=0`. É aceito? Deveria?
3. Troque o `exit(78)` por `exit(1)`. Que informação o orquestrador perde?

**Aprendizado:** validar na inicialização transforma um erro obscuro de 3h da manhã
numa mensagem clara no deploy.

---

## Lab 5 — O padrão `_FILE`

**Objetivo:** provar que a mesma aplicação aceita variável **ou** arquivo. **20 min.**

```bash
cd 07-projeto-modelo && bash scripts/gerar-segredos-locais.sh
```

```bash
DATABASE_URL_FILE=$PWD/secrets/database_url \
SESSION_SECRET_FILE=$PWD/secrets/session_secret \
API_KEY_FILE=$PWD/secrets/api_key \
node src/check-config.mjs
```

Saída real:
```
✅ Configuração válida.
   databaseUrl      memory://local
   sessionSecret    QH1…bC (64 chars)
   apiKey           sk_…1d (32 chars)
```

**Verificação — o valor não aparece no ambiente do processo:**

```bash
DATABASE_URL_FILE=$PWD/secrets/database_url \
SESSION_SECRET_FILE=$PWD/secrets/session_secret \
API_KEY_FILE=$PWD/secrets/api_key \
node -e 'setTimeout(()=>{},4000)' &
NODEPID=$!
sleep 0.7
cat /proc/$NODEPID/environ | tr '\0' '\n' | grep -c 'sk_test'
cat /proc/$NODEPID/environ | tr '\0' '\n' | grep API_KEY
kill $NODEPID
```

Saída real medida:
```
0
API_KEY_FILE=/caminho/do/projeto/secrets/api_key
```

Só o **caminho** está no ambiente. O segredo, não.

**Aprendizado:** o padrão `_FILE` tira o segredo do ambiente do processo. É a
diferença entre aparecer e não aparecer em `docker inspect`, em `/proc/PID/environ`,
em relatório de crash e nos subprocessos filhos.

---

## Lab 6 — Redação de log

**Objetivo:** provar que a redação funciona, e descobrir o que ela **não** pega. **25 min.**

```bash
cd 07-projeto-modelo && node --test "test/*.test.mjs" 2>&1 | tail -6
```

Saída real: `pass 43 / fail 0`.

Agora **quebre de propósito**, para ver os testes cumprindo o papel deles:

1. Em `src/config.mjs`, faça `configParaLog` devolver `{...config}` sem mascarar.
   Rode `npm test`. Quantos testes falham?
2. Em `src/log.mjs`, remova `senha` da expressão `CHAVES_SENSIVEIS`. Rode de novo.
3. Reverta tudo.

**A parte importante — o que a redação por nome de chave não pega:**

```bash
node -e '
import("./src/log.mjs").then(({redigir, redigirUrl}) => {
  const url = "postgres://app:senha-secreta@db:5432/loja";
  console.log("só redigir():", JSON.stringify(redigir({ databaseUrl: url })));
  console.log("com redigirUrl():", redigirUrl(url));
});'
```

Saída real:
```
só redigir(): {"databaseUrl":"postgres://app:senha-secreta@db:5432/loja"}
com redigirUrl(): postgres://app:***@db:5432/loja
```

**Aprendizado:** `databaseUrl` não casa com a expressão de nomes sensíveis, e a senha
está **dentro** da string. Redação por nome de chave é necessária e **insuficiente**.

---

## Lab 7 — Vaze um segredo numa imagem Docker, de propósito

**⚠️ Não executado aqui** (o usuário desta máquina não está no grupo `docker`).
**Objetivo:** ver com os próprios olhos que camada de imagem é para sempre. **30 min.**

```dockerfile
# Dockerfile.ruim
FROM alpine
ENV API_KEY=sk_live_segredo_de_teste_123
RUN echo "$API_KEY" > /tmp/chave.txt
RUN rm /tmp/chave.txt          # "apaguei"
CMD ["sh"]
```

```bash
docker build -f Dockerfile.ruim -t vazamento-demo .
docker history --no-trunc vazamento-demo | grep -i 'sk_live'
docker inspect -f '{{json .Config.Env}}' vazamento-demo
```

**Verificação (o soco no estômago) — extraia a camada onde o arquivo "apagado" está:**

```bash
docker save vazamento-demo -o demo.tar && mkdir -p demo && tar -xf demo.tar -C demo
grep -r 'sk_live' demo/ | head
```

Agora o jeito certo:

```dockerfile
# syntax=docker/dockerfile:1.7
FROM alpine
RUN --mount=type=secret,id=chave cat /run/secrets/chave > /dev/null
CMD ["sh"]
```

```bash
echo 'sk_live_segredo' > chave.txt
docker build --secret id=chave,src=chave.txt -t seguro-demo .
docker history --no-trunc seguro-demo | grep -c 'sk_live'    # esperado: 0
```

**Aprendizado:** `RUN rm` não apaga o conteúdo da camada anterior. Camada é imutável
e viaja com a imagem para todo registry e toda máquina que a baixar.

---

## Lab 8 — systemd do zero

**⚠️ Não executado aqui** (exige root). **Objetivo:** entregar como se entrega de
verdade num servidor Linux. **45 min.** Numa VM ou contêiner descartável.

```bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin labapp
sudo install -d -m 750 -o root -g labapp /etc/lab-app
sudo install -d -m 755 -o root -g root /opt/lab-app
sudo cp -r 07-projeto-modelo/src /opt/lab-app/
```

```bash
sudo tee /etc/lab-app/env > /dev/null <<EOF
DATABASE_URL=memory://local
SESSION_SECRET=$(openssl rand -base64 48 | tr -d '\n')
API_KEY=sk_live_$(openssl rand -hex 12)
NODE_ENV=production
PORT=8080
EOF
sudo chown root:labapp /etc/lab-app/env && sudo chmod 640 /etc/lab-app/env
```

Use a unit de
[07-projeto-modelo/deploy/](07-projeto-modelo/deploy/cofre-de-recados.service),
ajustando os caminhos.

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now lab-app
curl -s localhost:8080/health
sudo cat /proc/$(pgrep -u labapp -f 'node /opt/lab-app')/environ | tr '\0' '\n' | grep -c SESSION_SECRET
# esperado: 1
```

**Experimentos que ensinam mais que o caminho feliz:**

1. Estrague o `DATABASE_URL` e reinicie. O serviço reinicia em loop? (Não, se
   `RestartPreventExitStatus=78` estiver lá.) Remova a linha e veja a diferença em
   `journalctl -u lab-app -f`.
2. Como outro usuário, tente `cat /etc/lab-app/env`. Deve dar "Permissão negada".
3. Mude o `env` e **não** reinicie. `curl localhost:8080/config` mostra o valor novo?
   (Não — e você sabe por quê: `execve`.)
4. Troque `EnvironmentFile` por `LoadCredential` + `%d` ([30 §3](30-entrega-em-producao.md))
   e repita o teste 2 do `/proc`. O segredo sumiu do ambiente?

---

## Lab 9 — SOPS + age

**⚠️ Não executado aqui** (o SOPS não está instalado nesta máquina).
**Objetivo:** versionar segredo criptografado. **40 min.**

Instale conforme [03 §8](03-instalacao.md).

```bash
age-keygen -o ~/.config/sops/age/keys.txt && chmod 600 ~/.config/sops/age/keys.txt
export SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt
export CHAVE=$(age-keygen -y ~/.config/sops/age/keys.txt)
```

```bash
mkdir -p lab-sops/secrets && cd lab-sops && git init -q
cat > .sops.yaml <<EOF
creation_rules:
  - path_regex: secrets/.*\.enc\.yaml$
    age: $CHAVE
EOF
cat > secrets/prod.enc.yaml <<'EOF'
DATABASE_URL: postgres://app:senha-real@db:5432/loja
API_KEY: sk_live_xxxxxxxx
EOF
sops --encrypt --in-place secrets/prod.enc.yaml
```

```bash
head -2 secrets/prod.enc.yaml     # ENC[AES256_GCM,...]
git add -A && git commit -qm "segredos cifrados"
```

**Verificações que ensinam:**

1. `git show HEAD:secrets/prod.enc.yaml | grep -c senha-real` → **0**.
2. `sops exec-env secrets/prod.enc.yaml 'env | grep API_KEY'` → aparece.
3. **Nenhum arquivo em claro ficou no disco.** Confirme com `ls -la`.
4. Edite um valor com `sops secrets/prod.enc.yaml` e faça `git diff`. Só a linha
   alterada muda — as chaves continuam legíveis. **É isso que justifica o SOPS.**
5. Gere uma segunda chave `age`, acrescente ao `.sops.yaml`, rode `sops updatekeys`.
   Agora responda: o dono da **primeira** chave ainda consegue ler as versões
   antigas guardadas no histórico do Git? (Sim. Ver
   [40 §5](40-cofres-de-segredos.md).)

---

## Lab 10 — Cofre local com OpenBao

**⚠️ Não executado aqui** (exige Docker). **Objetivo:** entender cofre e credencial
dinâmica. **60 min.**

```bash
docker run --rm -d --name bao -p 8200:8200 \
  -e BAO_DEV_ROOT_TOKEN_ID=raiz openbao/openbao:latest \
  server -dev -dev-listen-address=0.0.0.0:8200
export BAO_ADDR=http://127.0.0.1:8200 BAO_TOKEN=raiz
```

```bash
bao kv put secret/lab-app API_KEY=sk_live_do_cofre DATABASE_URL=postgres://x
bao kv get secret/lab-app
bao kv get -field=API_KEY secret/lab-app
```

Integre com o projeto-modelo, sem tocar no código de negócio:

```bash
API_KEY=$(bao kv get -field=API_KEY secret/lab-app) \
DATABASE_URL=$(bao kv get -field=DATABASE_URL secret/lab-app) \
SESSION_SECRET=$(openssl rand -base64 48 | tr -d '\n') \
node 07-projeto-modelo/src/check-config.mjs
```

**Depois, o que realmente importa:**

1. Crie uma **política** que só permita ler `secret/lab-app`, e um token com ela.
   Tente ler outro caminho. Deve ser negado.
2. Suba um PostgreSQL em contêiner e configure o motor `database` para **credencial
   dinâmica** ([40 §2](40-cofres-de-segredos.md)). Peça duas credenciais seguidas e
   confirme que os usuários são diferentes.
3. `bao lease revoke -prefix database/creds/` e verifique no banco que o usuário
   sumiu.
4. `docker restart bao`. O que acontece? (Em modo `-dev`, tudo se perde. Em produção,
   ele fica **selado**. É o motivo de auto-unseal existir.)

---

## Lab 11 — Simule um vazamento e responda

**Objetivo:** praticar a resposta a incidente **antes** de precisar dela. **45 min.**

```bash
mkdir -p ~/lab-vazamento && cd ~/lab-vazamento && git init -q
printf 'AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\nAWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\n' > .env
git add -f .env && git -c user.email=lab@lab -c user.name=lab commit -qm "config"
printf 'app\n' > app.js && git add app.js && git -c user.email=lab@lab -c user.name=lab commit -qm "app"
printf '.env\n' > .gitignore && git rm --cached -q .env && git add .gitignore
git -c user.email=lab@lab -c user.name=lab commit -qm "remove .env (achando que resolveu)"
```

*(Chaves de exemplo da documentação pública da AWS — não são credenciais reais.)*

**Agora prove que "remover" não removeu:**

```bash
git log --oneline
git show HEAD~1:.env
```
Saída real: o arquivo aparece inteiro, com as duas chaves.

```bash
git log -S 'AKIAIOSFODNN7EXAMPLE' --oneline --all
```
Saída real: mostra o commit exato em que o segredo entrou.

**Responda ao incidente, na ordem certa:**

1. **Rotacionar** — aqui é simulado; na vida real é o **primeiro** passo, antes de
   qualquer investigação.
2. Determinar a janela: `git log --format='%ad %an' --date=iso <commit>`.
3. Limpar:
   ```bash
   pip install --quiet git-filter-repo
   git filter-repo --path .env --invert-paths --force
   ```
   Saída real:
   ```
   Parsed 3 commits
   New history written in 0.03 seconds; now repacking/cleaning...
   Completely finished after 0.11 seconds.
   ```
   ```bash
   git log --oneline
   # e4285ee remove .env
   # 78a7436 app          ← o commit "config" DESAPARECEU: ficou vazio e foi descartado
   git show HEAD~1:.env
   # fatal: path '.env' exists on disk, but not in 'HEAD~1'
   git log -S 'AKIAIOSFODNN7EXAMPLE' --oneline --all | wc -l
   # 0
   ```
   Repare no efeito colateral: **os hashes de todos os commits mudaram**. É por isso
   que todo mundo precisa reclonar — quem fizer `git pull` reintroduz o histórico antigo.
4. Escreva, em três linhas, o post-mortem: como entrou, qual camada faltava, o que muda.

**Aprendizado:** o histórico do Git guarda tudo. `git rm --cached` remove do próximo
commit, **não do passado**. E mesmo o `filter-repo` não alcança forks, clones e caches.

---

## Lab 12 — Rotação com sobreposição

**⚠️ Não executado aqui** (exige Docker). **Objetivo:** rotacionar sem derrubar. **60 min.**

```bash
docker run --rm -d --name pg -e POSTGRES_PASSWORD=admin -p 5432:5432 postgres:16-alpine
sleep 5
docker exec -i pg psql -U postgres <<'SQL'
CREATE DATABASE loja;
CREATE USER app_v1 WITH PASSWORD 'senha-antiga';
GRANT ALL PRIVILEGES ON DATABASE loja TO app_v1;
SQL
```

**Faça primeiro do jeito ERRADO**, para sentir a dor:

```bash
docker exec -i pg psql -U postgres -c "ALTER USER app_v1 WITH PASSWORD 'senha-nova';"
PGPASSWORD=senha-antiga psql -h localhost -U app_v1 -d loja -c 'select 1'
# esperado: falha de autenticação — TODA instância que ainda não reiniciou está fora
```

**Agora do jeito CERTO — sobreposição:**

```bash
# t1: cria o SEGUNDO usuário, sem tocar no primeiro
docker exec -i pg psql -U postgres -d loja <<'SQL'
CREATE USER app_v2 WITH PASSWORD 'senha-nova-forte';
GRANT ALL PRIVILEGES ON DATABASE loja TO app_v2;
GRANT ALL ON ALL TABLES IN SCHEMA public TO app_v2;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO app_v2;
SQL
```

```bash
# t2: as DUAS funcionam ao mesmo tempo
PGPASSWORD=senha-nova psql -h localhost -U app_v1 -d loja -c 'select 1'
PGPASSWORD=senha-nova-forte psql -h localhost -U app_v2 -d loja -c 'select 1'
```

```bash
# t2→t3: quem ainda usa a antiga?
docker exec -i pg psql -U postgres -c \
  "SELECT usename, count(*) FROM pg_stat_activity WHERE usename LIKE 'app%' GROUP BY 1;"
```

```bash
# t3: só depois de confirmar
docker exec -i pg psql -U postgres -d loja -c 'REASSIGN OWNED BY app_v1 TO app_v2; DROP OWNED BY app_v1; DROP USER app_v1;'
docker rm -f pg
```

**Aprendizado:** rotação sem sobreposição é indisponibilidade planejada. E o
`ALTER DEFAULT PRIVILEGES` é o passo esquecido que produz um erro semanas depois,
na primeira tabela nova.

---

## Projeto final

Pegue **um sistema seu, real**, e aplique tudo:

- [ ] `.gitignore` com `.env`, e `gitleaks git .` sem achados no histórico
- [ ] `.env.example` completo, com **como obter** cada valor
- [ ] Um único módulo lê o ambiente, valida tudo, falha com código 78
- [ ] Nenhum segredo em log — confirmado por teste automatizado
- [ ] Padrão `_FILE` suportado
- [ ] A aplicação sobe **sem** `.env`, só com o ambiente
- [ ] Entrega definida: systemd/`LoadCredential`, contêiner ou PaaS
- [ ] CI com gitleaks e `--redact`
- [ ] Inventário de segredos preenchido ([45 §7](45-rotacao-e-ciclo-de-vida.md))
- [ ] Uma rotação **ensaiada**, com o tempo cronometrado

Se marcar os dez, você está acima da média do mercado. Sério.

---

## Autoteste

Responda **sem consultar** — são as conclusões dos laboratórios.

1. No Lab 1, por que a mudança feita pelo shell filho não afeta o pai?
2. No Lab 2, qual vence: o `.env` ou o ambiente? Qual consequência prática disso?
3. No Lab 3, quais duas linhas do `.env` se comportam de forma diferente em Node e Python?
4. No Lab 4, por que o código de saída é 78 e não 1?
5. No Lab 5, o que aparece em `/proc/<pid>/environ` quando se usa `_FILE`?
6. No Lab 6, por que `redigir()` sozinho não protege a `DATABASE_URL`?
7. No Lab 7, por que `RUN rm chave.txt` não remove o segredo da imagem?
8. No Lab 8, o que `RestartPreventExitStatus=78` evita?
9. No Lab 9, quem consegue ler as versões antigas depois de um `sops updatekeys`?
10. No Lab 11, por que os hashes de commit mudam após o `git filter-repo`, e o que isso obriga o time a fazer?
11. No Lab 12, o que acontece se você pular a fase de sobreposição?

---

**Próximo:** [75-armadilhas.md](75-armadilhas.md) · Voltar ao [mapa](00-MAPA.md)
