# Projeto-modelo — Mural de Recados

`Nível: intermediário` · `Última atualização: 11/08/2026`

Uma aplicação **pequena porém inteira** que roda de verdade: API HTTP + página web,
persistência em volume, proxy reverso, testes, healthcheck, encerramento gracioso, limites de
recurso e endurecimento de segurança.

Não é um trecho de código. É o esqueleto do que você encontraria numa implantação real,
reduzido ao mínimo que ainda ensina.

---

## O que este projeto ensina

| Conceito | Onde está no código |
|---|---|
| Multi-stage build com 4 estágios | [`Dockerfile`](Dockerfile) |
| Cache de camadas e `.dockerignore` | [`.dockerignore`](.dockerignore) |
| Container sem root, com `USER` | `Dockerfile`, estágio `producao` |
| `tini` como PID 1 e repasse de sinais | `Dockerfile` + `server.js` |
| Encerramento gracioso no `SIGTERM` | [`app/src/server.js`](app/src/server.js) |
| Configuração por ambiente, falhando rápido | [`app/src/config.js`](app/src/config.js) |
| Log estruturado em stdout | [`app/src/log.js`](app/src/log.js) |
| Volume nomeado e escrita atômica | [`app/src/repositorio.js`](app/src/repositorio.js) |
| Healthcheck que exercita a dependência real | `Dockerfile` + `app/src/rotas.js` |
| Liveness × readiness (`/vivo` × `/saude`) | `app/src/rotas.js` |
| Redes separadas, uma delas `internal` | [`compose.yaml`](compose.yaml) |
| `depends_on: condition: service_healthy` | `compose.yaml` |
| Perfis do Compose (prod / dev / testes) | `compose.yaml` |
| Limites de memória, CPU e capabilities | `compose.yaml` |
| Sistema de arquivos raiz somente leitura + tmpfs | `compose.yaml` |
| Proxy reverso e DNS por nome de serviço | [`nginx/default.conf`](nginx/default.conf) |
| Testes rodando dentro do build | `Dockerfile`, estágio `testes` |
| Backup e restauração de volume | [`Makefile`](Makefile) |

---

## Pré-requisitos

- Docker Engine **≥ 24** (testado com a série 29) — veja [../03-instalacao.md](../03-instalacao.md)
- `docker compose` **v2** (com espaço, não hífen)
- `make` (opcional — todos os comandos têm equivalente direto abaixo)
- **Nenhuma dependência de npm.** O projeto usa só a biblioteca padrão do Node 22+, então o
  build não precisa de rede para instalar pacotes e é reproduzível em qualquer lugar.

---

## Como rodar — comandos exatos

```bash
cd homelab/learn-process/docker/07-projeto-modelo

# 1. Configuração
cp .env.example .env

# 2. Subir (constrói, sobe e ESPERA os healthchecks passarem)
docker compose up -d --build --wait
#    equivalente:  make subir

# 3. Verificar
curl -s http://localhost:8080/saude
# esperado: {"status":"ok","recados":0,"ambiente":"production"}

# 4. Usar a API
curl -s -X POST http://localhost:8080/api/recados \
  -H 'Content-Type: application/json' \
  -d '{"autor":"Roni","texto":"primeiro recado containerizado"}'
# esperado: 201 com o recado, incluindo id (UUID) e criadoEm (ISO-8601)

curl -s http://localhost:8080/api/recados
# esperado: {"total":1,"recados":[{...}]}

# 5. Abrir a página no navegador
#    http://localhost:8080

# 6. Derrubar (os dados PERMANECEM no volume)
docker compose down
#    equivalente:  make derrubar
```

### Outros modos

```bash
make testes      # docker compose --profile testes run --rm testes
make dev         # docker compose --profile dev up --build   → http://localhost:3000, com recarga
make logs        # docker compose logs -f
make shell       # docker compose exec api sh
make backup      # salva o volume em ./backups/
make limpar      # ⚠️ docker compose down -v — APAGA os recados
make             # lista todos os alvos
```

---

## Estrutura de pastas

```
07-projeto-modelo/
├── compose.yaml            # a stack: proxy + api, mais os perfis dev e testes
├── Dockerfile              # 4 estágios: base → dev / testes / producao
├── .dockerignore           # o que NÃO entra no contexto de build (inclusive segredos)
├── .env.example            # modelo da configuração; copie para .env
├── Makefile                # atalhos legíveis para os comandos longos
│
├── nginx/
│   └── default.conf        # proxy reverso: única porta exposta ao host
│
└── app/
    ├── package.json        # sem dependências — de propósito
    ├── src/
    │   ├── server.js       # PID 1: sobe, trata sinais, encerra com elegância
    │   ├── config.js       # ambiente → configuração validada, falhando rápido
    │   ├── log.js          # log JSON de uma linha, em stdout
    │   ├── repositorio.js  # persistência atômica em volume + fila de escrita
    │   └── rotas.js        # roteamento, validação e tratamento de erro
    └── test/
        ├── repositorio.test.js   # 12 testes de unidade
        └── rotas.test.js         # 10 testes de integração HTTP
```

---

## O que cada decisão de projeto ensina

### 1. Quatro estágios no Dockerfile, não um

`base` concentra o que é comum; `dev` traz recarga automática; `testes` **roda a suíte durante
o build** — se um teste falhar, a imagem não é produzida; `producao` leva só o necessário para
executar.

*O que se aprende:* multi-stage não serve só para "diminuir a imagem". Serve para separar
propósitos. O estágio `testes` transforma o build num portão de qualidade que funciona igual na
sua máquina e no CI, sem duplicar configuração.

### 2. `tini` como PID 1

Sem um init de verdade, o processo Node vira PID 1 e o kernel trata PID 1 de forma especial:
sinais sem tratador registrado são **ignorados**, e processos órfãos nunca são colhidos.

*O que se aprende:* por que tantos containers demoram exatos 10 segundos para parar. O `tini`
custa 10 KB e resolve os dois problemas.

### 3. `SIGTERM` tratado explicitamente no `server.js`

`docker stop` manda `SIGTERM`, espera (por padrão) 10 segundos e manda `SIGKILL`. Quem não
trata `SIGTERM` perde toda requisição em curso a cada deploy — que o usuário vê como erro 502.

*O que se aprende:* o encerramento gracioso tem um **prazo próprio**
(`prazoEncerramentoMs = 8000`) menor que o do Docker. Se as conexões não fecharem a tempo, o
processo sai por conta própria em vez de ser morto à força.

### 4. Escrita atômica no `repositorio.js`

Grava em `recados.json.tmp` e só então `rename`. No mesmo sistema de arquivos, `rename` é
atômico no Linux: ou está o arquivo antigo, ou o novo, nunca metade.

*O que se aprende:* container **morre a qualquer momento** — por deploy, por OOM, por
reagendamento. Código que assume "vou terminar de escrever" produz corrupção. Esta é a diferença
entre um exemplo de tutorial e código que aguenta um `kill -9`.

### 5. Fila de escrita serializando as gravações

Duas requisições simultâneas leem o mesmo estado, cada uma acrescenta o seu recado, e uma
sobrescreve a outra — *lost update*. A fila (`#enfileirar`) elimina isso. Há um teste
específico para essa condição de corrida.

*O que se aprende:* concorrência não some porque o app está em container. Ela só fica mais
visível, porque containers são replicados.

### 6. Healthcheck que **escreve no disco**

`/saude` chama `repositorio.verificarSaude()`, que grava um arquivo-sonda. Um healthcheck que
devolve `{"status":"ok"}` sem tocar na dependência crítica declara "saudável" um container com
o volume cheio ou somente leitura.

*O que se aprende:* healthcheck ruim é pior que nenhum, porque dá falsa confiança. E a distinção
entre `/vivo` (liveness: "reinicie-me") e `/saude` (readiness: "não me mande tráfego") é o que
evita reinícios em cascata quando uma dependência oscila.

### 7. Duas redes, uma delas `internal: true`

`proxy` está em `borda` e em `interna`. `api` está **só** em `interna`, que não tem rota para a
internet. Não existe `ports:` no serviço `api`.

*O que se aprende:* o modelo de rede é a sua primeira camada de defesa. Se a api for
comprometida, o atacante não consegue nem exfiltrar dados por HTTP, porque a rede não tem saída.

### 8. `read_only: true`, `cap_drop: ALL`, `no-new-privileges`

O sistema de arquivos raiz é somente leitura (com um `/tmp` em RAM), o container não tem
nenhuma *capability* do kernel, e nenhum binário setuid pode elevar privilégio.

*O que se aprende:* essas três linhas eliminam classes inteiras de exploração e custam
praticamente nada. A maioria das aplicações web funciona assim sem nenhuma alteração — só não
se faz por desconhecimento.

### 9. `${NOME_DO_MURAL:?mensagem}` no Compose

Se a variável não existir, o `docker compose up` **aborta com uma mensagem explícita**, em vez
de subir com valor vazio.

*O que se aprende:* falhar cedo e alto. O orquestrador sabe lidar com "não subiu"; ele não sabe
lidar com "subiu errado".

### 10. Zero dependências de npm

Não há `node_modules`, `package-lock.json` nem `npm ci` no build.

*O que se aprende:* é uma escolha **deliberada** deste material didático — o build fica
reproduzível sem rede e o Dockerfile fica legível sem o ruído de lockfile. Em um projeto real
você **terá** dependências, e aí valem os padrões do
[06-exemplos.md](../06-exemplos.md#4-dockerfile-node-com-multi-stage-e-cache-eficiente):
`COPY package*.json` antes de `COPY . .`, `npm ci` (não `npm install`) e
`RUN --mount=type=cache`.

---

## Laboratórios com este projeto

Faça-os na ordem. Cada um demonstra na prática algo que só se entende mexendo.

### Lab 1 — O container é descartável
```bash
docker compose up -d --wait
curl -X POST localhost:8080/api/recados -H 'Content-Type: application/json' \
  -d '{"autor":"eu","texto":"sobrevivo?"}'
docker compose down          # remove os containers
docker compose up -d --wait  # recria do zero
curl -s localhost:8080/api/recados
```
**Esperado:** o recado continua lá. **Por quê:** ele está no volume `mural_dados-mural`, não na
camada de escrita do container.

### Lab 2 — E o volume, não
```bash
docker compose down -v       # o -v apaga o volume
docker compose up -d --wait
curl -s localhost:8080/api/recados
```
**Esperado:** `{"total":0,"recados":[]}`. **Lição:** `down -v` não pede confirmação. Em produção,
esse comando já apagou muito banco de dados.

### Lab 3 — Falhar rápido
```bash
NOME_DO_MURAL= docker compose up api
```
**Esperado:** o Compose aborta antes de criar o container, citando a variável pelo nome.
Agora remova o `:?` do `compose.yaml` e repita: o container sobe e **morre** no boot, com o
erro vindo do `config.js`. Compare as duas mensagens — a primeira é muito melhor.

### Lab 4 — Encerramento gracioso
```bash
docker compose up -d --wait
time docker compose stop api
```
**Esperado:** menos de 1 segundo. Agora troque no `Dockerfile` a linha
`CMD ["node", "src/server.js"]` por `CMD node src/server.js` (forma shell), reconstrua e repita.
**Esperado:** exatos 10 segundos, porque o `/bin/sh` intermediário não repassa o `SIGTERM`.

### Lab 5 — Limite de memória e OOM
```bash
docker compose up -d --wait
docker stats --no-stream $(docker compose ps -q api)
# MEM USAGE / LIMIT mostra ".../ 256MiB"

# Force o estouro:
docker compose exec api node -e "const a=[]; while(true) a.push(Buffer.alloc(10*1024*1024))"
docker inspect --format '{{.State.OOMKilled}} {{.State.ExitCode}}' $(docker compose ps -q api)
```
**Esperado:** `true 137`. **Lição:** 137 = 128 + 9 (SIGKILL) é quase sempre OOM. E o limite
converteu "o servidor caiu" em "um container reiniciou".

### Lab 6 — Isolamento de rede
```bash
docker compose exec api wget -qO- --timeout=3 https://example.com || echo "sem saída — correto"
docker compose exec proxy wget -qO- --timeout=3 http://api:3000/saude
```
**Esperado:** a api não alcança a internet (rede `internal`); o proxy alcança a api pelo **nome
do serviço**, resolvido pelo DNS interno do Docker em `127.0.0.11`.

### Lab 7 — Sistema de arquivos somente leitura
```bash
docker compose exec api sh -c 'echo teste > /app/arquivo.txt'   # deve falhar
docker compose exec api sh -c 'echo teste > /tmp/arquivo.txt'   # deve funcionar (tmpfs)
docker compose exec api sh -c 'echo teste > /dados/arquivo.txt' # deve funcionar (volume)
```
**Lição:** `read_only: true` não impede o app de trabalhar — só o obriga a declarar onde escreve.

### Lab 8 — O build como portão de qualidade
Introduza um bug em `app/src/repositorio.js` (por exemplo, remova o `.trim()` da validação de
autor) e rode:
```bash
docker build --target testes -t mural:teste .
```
**Esperado:** o build **falha** no estágio `testes`, e nenhuma imagem de produção é gerada.

### Lab 9 — Backup e restauração
```bash
make backup
make limpar                 # apaga tudo
docker compose up -d --wait
make restaurar
curl -s localhost:8080/api/recados
```
**Esperado:** os recados voltam. **Lição:** um backup nunca restaurado não é um backup.

### Lab 10 — Onde o tamanho está
```bash
make tamanho
docker history mural-de-recados:1.0
```
Identifique qual camada é a maior. **Esperado:** a base `node:22-alpine`. **Pergunta para
levar adiante:** como chegar perto de 10 MB? (Resposta: `gcr.io/distroless/nodejs22`, ou trocar
de linguagem — veja o [exemplo 6](../06-exemplos.md#6-go-imagem-de-8-mb-com-scratch).)

---

## Próximos passos — como evoluir este projeto

Na ordem em que fazem sentido:

1. **Trocar o arquivo JSON por Postgres.** Acrescente um serviço `db` com healthcheck, um
   serviço `migracao` com `service_completed_successfully`, e um driver no `package.json`. É
   quando o `.dockerignore`, o `npm ci` e o cache de build passam a importar de verdade.
2. **Publicar a imagem** no GHCR e fazer deploy por *digest*, com o pipeline do
   [exemplo 12](../06-exemplos.md#12-produção--pipeline-de-ci-completo-no-github-actions).
3. **Escanear e assinar**: `trivy image` e `cosign sign`.
4. **Métricas**: expor `/metricas` em formato Prometheus e acrescentar Prometheus + Grafana.
5. **Escalar**: `docker compose up -d --scale api=3` e observar o nginx balancear entre as
   réplicas — momento em que o estado em arquivo local mostra a sua limitação, e por isso mesmo
   ensina por que serviços replicados guardam estado fora do container.

---

## Verificação feita neste material

Sejamos precisos sobre o que foi testado e o que não foi:

- ✅ **A suíte de testes foi executada e passou**: 22 testes, 2 suítes, em Node v24.18.0, em
  11/08/2026 — 12 testes de unidade do repositório e 10 de integração HTTP.
- ✅ **A aplicação foi executada fora de container** e verificada de ponta a ponta: `/saude`,
  `POST /api/recados`, `GET /api/recados`, a página HTML e o encerramento gracioso via `SIGTERM`
  (menos de 1 segundo, com a linha `encerrado com elegância` no log).
- ⚠️ **O `docker build` e o `docker compose up` não puderam ser executados no ambiente em que
  este material foi escrito** (sem acesso ao socket do daemon). O `Dockerfile` e o
  `compose.yaml` seguem as práticas verificadas na documentação oficial na data acima, mas
  **rode-os você mesmo** e trate qualquer divergência como um exercício legítimo do
  [Lab 8](#lab-8--o-build-como-portão-de-qualidade). O material não afirma o que não verificou.

---

## Autoteste

1. Por que o estágio `testes` existe se os testes já rodam com `npm test`?
2. O que acontece se você remover `tini` do Dockerfile e parar o container?
3. Por que o `repositorio.js` grava em `.tmp` antes de renomear?
4. O serviço `api` não tem `ports:`. Como o navegador chega até ele?
5. Qual é a diferença entre `/vivo` e `/saude`, e qual sonda o orquestrador usa para reiniciar?
6. Por que `read_only: true` exige um `tmpfs` em `/tmp`?
7. `docker compose down` e `docker compose down -v`: qual apaga os recados?
8. Se você rodar `--scale api=3`, o que quebra neste projeto e por quê?
9. Por que o `mkdir /dados && chown node:node /dados` no Dockerfile é necessário mesmo com o
   volume sendo criado pelo Compose?
