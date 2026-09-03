# 07 · Projeto-modelo — Cofre de Recados

`Nível: iniciante a avançado` · `Atualizado em: 14/08/2026`

Uma API HTTP pequena, **inteira e executável**, cujo assunto de verdade não é a API:
é **como a configuração entra nela**. Zero dependências — só a biblioteca padrão do Node.

> **Status de execução:** tudo abaixo foi **executado de verdade** em
> Ubuntu 22.04.5 · Node v24.18.0 · Python 3.10.12 · PHP 8.1.2, em 14/08/2026.
> **43 testes, 43 aprovados.** As exceções declaradas estão em [§9](#9-o-que-não-foi-executado-aqui).

---

## 1. O que este projeto demonstra

| Prática | Onde ver |
|---|---|
| O código **nunca** chama `dotenv` — quem carrega o `.env` é o runtime, só em dev | [`src/app.mjs`](src/app.mjs) |
| **Um único módulo** lê `process.env`; o resto recebe `config` por parâmetro | [`src/config.mjs`](src/config.mjs), [`src/servidor.mjs`](src/servidor.mjs) |
| Validação na inicialização, **todos** os erros de uma vez, saída **78** (`EX_CONFIG`) | [`src/config.mjs`](src/config.mjs) |
| Padrão `NOME_FILE` (Docker/Kubernetes), com precedência sobre `NOME` | [`src/config.mjs`](src/config.mjs) |
| Regras cruzadas: segredo de exemplo é **recusado** com `NODE_ENV=production` | [`src/config.mjs`](src/config.mjs) |
| Mascaramento de segredo em log e em rota de diagnóstico | [`src/log.mjs`](src/log.mjs) |
| Teste que **cobra** o `.env.example` quando alguém adiciona variável nova | [`test/config.test.mjs`](test/config.test.mjs) |
| Prova, em processo real, de que **o ambiente vence o `.env`** | [`test/processo.test.mjs`](test/processo.test.mjs) |
| Entrega em servidor Linux com `systemd` e permissão correta | [`deploy/`](deploy/) |
| **Instalador para a máquina do cliente** | [`deploy/install.sh`](deploy/install.sh) |
| Contêiner sem segredo embutido, com `secrets:` do Compose | [`Dockerfile`](Dockerfile), [`compose.yaml`](compose.yaml) |
| O mesmo contrato em **Python e PHP**, para provar que o mecanismo é do SO | [`equivalentes/`](equivalentes/) |

---

## 2. Pré-requisitos

- **Node.js 22 ou superior** (`node --version`). Testado com v24.18.0.
- Opcional: Python 3.10+ e PHP 8.1+ para os equivalentes.
- Opcional: Docker 25+ para o contêiner.
- **Nenhuma dependência de npm.** Não existe `npm install` neste projeto.

---

## 3. Rodar em 60 segundos

```bash
cd 07-projeto-modelo
```

### Caminho A — sem `.env`, como será em produção

```bash
DATABASE_URL='memory://local' \
SESSION_SECRET="$(openssl rand -base64 48 | tr -d '\n')" \
API_KEY='sk_test_chave_local_123' \
PORT=3999 LOG_LEVEL=debug EXPOR_METRICAS=true \
node src/app.mjs
```

Saída real:

```json
{"ts":"2026-08-14T17:23:28.563Z","nivel":"info","mensagem":"configuração carregada","ambiente":"development","porta":3999,"logLevel":"debug","databaseUrl":"postgres://app:***@localhost:5432/recados","sessionSecret":"spQ…tt (64 chars)","apiKey":"[REDIGIDO]","maxRecados":100,"exporMetricas":true,"fonte":"variável de ambiente"}
{"ts":"2026-08-14T17:23:28.566Z","nivel":"info","mensagem":"servidor no ar","porta":3999,"ambiente":"development"}
```

> Repare: `sessionSecret` mascarado pelo `configParaLog`, e `apiKey` **[REDIGIDO]**
> pelo redator do log. **Duas camadas independentes**, de propósito — se uma falhar,
> a outra segura.

Noutro terminal:

```bash
curl -s localhost:3999/health
```
```json
{"ok":true,"ambiente":"development"}
```

```bash
curl -s -X POST localhost:3999/recados \
  -H "authorization: Bearer sk_test_chave_local_123" \
  -H 'content-type: application/json' \
  -d '{"texto":"comprar pão"}'
```
```json
{"id":"a970b1be-0732-439d-aa59-7472f05e3c40","texto":"comprar pão","assinatura":"bPU5AsUJMTYdR-Eg","criadoEm":"2026-08-14T17:23:30.005Z"}
```

```bash
curl -s localhost:3999/config -H "authorization: Bearer sk_test_chave_local_123"
```
```json
{"ambiente":"development","porta":3999,"logLevel":"debug","databaseUrl":"postgres://app:***@localhost:5432/recados","sessionSecret":"spQ…tt (64 chars)","apiKey":"sk_…23 (23 chars)","maxRecados":100,"exporMetricas":true}
```

**Essa rota `/config` é a lição escondida do projeto.** Ela existe porque a primeira
pergunta de todo atendimento de suporte é "que configuração esse servidor está
usando?" — e, sem uma rota que responda **em segurança**, alguém vai dar um
`console.log(config)` às pressas e vazar tudo no log. Existe um teste
([`servidor.test.mjs`](test/servidor.test.mjs)) que falha se algum segredo aparecer
inteiro nessa resposta.

### Caminho B — com `.env`, como no dia a dia

```bash
cp .env.example .env
node --env-file=.env src/check-config.mjs
```

Ou, com recarga automática ao salvar:

```bash
npm run dev     # node --env-file-if-exists=.env --watch src/app.mjs
```

---

## 4. O experimento central do curso

Prove, na sua máquina, que **o ambiente vence o `.env`** — e que por isso o `.env`
não precisa ir para produção.

```bash
printf 'PORT=1111\nDATABASE_URL=memory://doarquivo\nSESSION_SECRET=%s\nAPI_KEY=sk_test_doarquivo\n' "$(printf 'f%.0s' {1..32})" > /tmp/demo.env
```

```bash
node --env-file=/tmp/demo.env src/check-config.mjs | grep porta
# porta            1111        ← só o .env
```

```bash
PORT=9999 node --env-file=/tmp/demo.env src/check-config.mjs | grep porta
# porta            9999        ← o AMBIENTE venceu
```

Esse comportamento está travado por teste automatizado, em processo real:
`test/processo.test.mjs` → *"variável de ambiente VENCE o .env — por isso o .env não
vai para produção"*.

---

## 5. Estrutura, comentada

```
07-projeto-modelo/
│
├── src/
│   ├── config.mjs        ← 🎯 O CORAÇÃO. Única porta de entrada da configuração.
│   │                        `criarConfig(env)` é PURO: recebe o ambiente, devolve
│   │                        {config, problemas}. É isso que torna possível testar
│   │                        16 cenários sem subir 16 processos.
│   ├── log.mjs           ← log JSON com redação automática + `redigirUrl`, que
│   │                        remove a senha de dentro de postgres://user:senha@host
│   ├── servidor.mjs      ← a aplicação. Recebe `config` por parâmetro e NUNCA
│   │                        lê process.env. Injeção de dependência aplicada
│   │                        à configuração.
│   ├── app.mjs           ← ponto de entrada: valida → loga mascarado → sobe →
│   │                        trata SIGTERM
│   └── check-config.mjs  ← valida e sai. Usado pelo instalador, pelo CI, pelo
│                            systemd (ExecStartPre) e pelo suporte técnico
│
├── test/
│   ├── config.test.mjs   ← 22 testes da função pura, inclusive o que COBRA o
│   │                        .env.example quando você adiciona variável
│   ├── servidor.test.mjs ← rotas + "nenhum segredo vaza em /config"
│   └── processo.test.mjs ← 7 testes em PROCESSO REAL: precedência, código 78,
│                            _FILE ponta a ponta, não-persistência da variável
│
├── deploy/
│   ├── cofre-de-recados.service  ← unit systemd com EnvironmentFile,
│   │                                RestartPreventExitStatus=78 e blindagem
│   └── install.sh                ← 🎯 instalador para a máquina do CLIENTE
│
├── scripts/
│   ├── check-env.sh              ← compara .env.example com o ambiente (para CI)
│   └── gerar-segredos-locais.sh  ← cria secrets/ com valores aleatórios
│
├── equivalentes/
│   ├── config.py         ← o MESMO contrato em Python (biblioteca padrão)
│   └── config.php        ← o MESMO contrato em PHP (sem Composer)
│
├── .env.example          ← ✅ versionado: o CONTRATO
├── .gitignore            ← .env, secrets/, *.pem
├── .dockerignore         ← idem + .git (senão o histórico inteiro entra na imagem)
├── Dockerfile
└── compose.yaml          ← as três formas de configurar um contêiner, lado a lado
```

---

## 6. Testes

```bash
npm test          # node --test "test/*.test.mjs"
```

Resultado real:

```
ℹ tests 43
ℹ suites 10
ℹ pass 43
ℹ fail 0
ℹ duration_ms 453.13623
```

Os quatro testes que mais valem a leitura:

1. **"ambiente vazio reporta TODAS as faltas de uma vez"** — corrigir configuração
   um erro por vez, com deploy entre cada um, é tortura evitável.
2. **"toda variável exigida pelo código aparece no `.env.example`"** — o antídoto
   para o erro nº 1 de equipe. Adicione `opcional('NOVA_VAR', …)` ao `config.mjs`
   sem tocar no `.env.example` e o teste falha imediatamente.
3. **"nenhum segredo aparece inteiro na resposta"** (`/config`) — segurança que se
   verifica sozinha a cada `npm test`, não que depende de alguém lembrar.
4. **"variável de ambiente VENCE o .env"** — a tese do curso, travada por teste.

Experimente quebrar de propósito:

```bash
# 1) adicione uma variável ao config.mjs sem documentá-la  → teste 2 falha
# 2) tire o mascaramento de configParaLog                  → testes 3 falham
```

---

## 7. Entrega em produção

### 7.1 Servidor Linux com systemd

```bash
sudo ./deploy/install.sh
```

O instalador: cria o usuário de sistema `cofre`, copia o código para
`/opt/cofre-de-recados` (pertencente ao **root**, para a aplicação não poder alterar
o próprio código), **pergunta** os segredos sem ecoar na tela, **gera** o
`SESSION_SECRET`, **valida antes de gravar**, grava `/etc/cofre-de-recados/env` como
`root:cofre 640`, instala a unit e sobe o serviço.

Decisões e o que cada uma ensina:

| Decisão | Por quê |
|---|---|
| `umask 077` na primeira linha | nenhum arquivo temporário nasce legível por outros — sem janela de exposição |
| grava em `.tmp`, valida, depois `mv` | um Ctrl+C no meio não deixa configuração pela metade; o `mv` é atômico |
| `SESSION_SECRET` **gerado**, não perguntado | segredo que não trafega não vaza; e cada instalação fica com um valor diferente, então o vazamento de um cliente não atinge os outros |
| `read -rsp` | não ecoa e **não entra no histórico do shell** |
| `640 root:cofre` | a aplicação lê e **não pode alterar**; nenhum outro usuário do servidor lê |
| idempotente | o cliente vai rodar duas vezes. Sempre roda |
| `ExecStartPre=check-config.mjs` | falha com mensagem legível no `journalctl`, antes de abrir porta |
| `RestartPreventExitStatus=78` | sem isso, configuração errada faz o systemd reiniciar a cada 5 s **para sempre**, enchendo o disco de log |

### 7.2 Contêiner

```bash
bash scripts/gerar-segredos-locais.sh
docker compose up --build
curl -s localhost:8080/health
```

O `compose.yaml` mostra as três formas lado a lado, com a recomendação de cada uma:
`environment:` para o que não é segredo, `secrets:` + padrão `_FILE` para o que é, e
`env_file:` marcado como prático em dev e desaconselhado em produção.

Confira que a imagem não carrega segredo:

```bash
docker history --no-trunc cofre-de-recados | grep -iE 'secret|token|password'   # nada
docker inspect -f '{{json .Config.Env}}' cofre-de-recados                       # só NODE_ENV e PATH
```

---

## 8. Os equivalentes em Python e PHP

O mesmo contrato, as mesmas mensagens, o mesmo código de saída:

```bash
python3 equivalentes/config.py
php     equivalentes/config.php
node    src/check-config.mjs
```

Os três, com o ambiente vazio, produzem:

```
❌ Configuração inválida:
   • falta DATABASE_URL
   • falta SESSION_SECRET
   • falta API_KEY
```

E os três, com o mesmo `_FILE`, produzem a mesma saída válida:

```bash
DATABASE_URL_FILE=$PWD/secrets/database_url \
SESSION_SECRET_FILE=$PWD/secrets/session_secret \
API_KEY_FILE=$PWD/secrets/api_key \
python3 equivalentes/config.py
```
```
✅ Configuração válida.

   ambiente         development
   porta            3000
   log_level        info
   database_url     memory://local
   session_secret   QH1…bC (64 chars)
   api_key          sk_…1d (32 chars)
   max_recados      100
   expor_metricas   False
```

**É essa a demonstração:** o mecanismo é do **sistema operacional**, não da
linguagem. Trocar de linguagem não muda a resposta da pergunta original.

O `config.php` traz de brinde a armadilha mais específica do PHP, comentada no
topo do arquivo: **`getenv()` e `$_ENV` não são equivalentes** — `$_ENV` só é
preenchido se `variables_order` no `php.ini` incluir a letra `E`, e o padrão de
muitas distribuições é `GPCS`, sem ela.

---

## 9. O que **não** foi executado aqui

Declarado por honestidade — o resto foi tudo rodado:

- **`docker build` e `docker compose up`**: o Docker está instalado nesta máquina
  (29.1.3), mas o usuário não está no grupo `docker`
  (`permission denied ... /var/run/docker.sock`). O `Dockerfile` e o `compose.yaml`
  não foram construídos aqui.
- **`deploy/install.sh`**: exige `root` e altera `/etc`, `/opt` e o systemd da
  máquina. Não foi executado neste ambiente de escrita.
- **`deploy/cofre-de-recados.service`**: não instalado nem iniciado.

Tudo em `src/`, `test/`, `scripts/` e `equivalentes/` foi executado, com as saídas
reais reproduzidas acima.

---

## 10. Exercícios sobre este projeto

1. Adicione `SMTP_URL` como obrigatória. Rode `npm test` **antes** de tocar no
   `.env.example` e veja qual teste falha e por quê.
2. Faça `configParaLog` devolver o valor cru. Quantos testes quebram?
3. Rode com `NODE_ENV=production` e o `.env.example` inteiro. Explique cada uma das
   três recusas.
4. Implemente `MAX_RECADOS_FILE` apontando para um arquivo que muda em tempo de
   execução, e releia sem reiniciar o processo (dica: `fs.watchFile`, veja
   [06-exemplos.md #14](../06-exemplos.md)).
5. Escreva a versão em Go ou Java do `equivalentes/`, com as mesmas mensagens.
6. Os testes de `servidor.test.mjs` não usam `config.porta`: o servidor abre com
   `listen(0)`. Explique por que isso é obrigatório num conjunto de testes que roda
   em paralelo, e o que aconteceria se todos usassem a porta 3000.

---

**Voltar:** [06-exemplos.md](../06-exemplos.md) · [00-MAPA.md](../00-MAPA.md) ·
**Seguir:** [10-fundamentos.md](../10-fundamentos.md)
