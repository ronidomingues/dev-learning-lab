# 04 · Como começar — do ambiente pronto ao primeiro resultado

`Nível: iniciante` · `Tempo: 45–75 minutos` · `Última atualização: 11/08/2026`

Este documento **assume o ambiente já instalado** pelo [03-instalacao.md](03-instalacao.md).
Se `docker run --rm hello-world` não imprime "Hello from Docker!", volte lá.

Ao final você terá: rodado um serviço pronto, construído a sua própria imagem, persistido dados
num volume e subido dois containers conversando entre si com Compose. Nessa ordem, porque cada
passo depende do anterior.

---

## Passo 1 — Rodar algo de verdade em 10 segundos

```bash
docker run -d --name web -p 8080:80 nginx:alpine
```

Anatomia do comando — cada pedaço importa:

| Pedaço | Significado |
|---|---|
| `docker run` | crie um container a partir de uma imagem **e** inicie-o |
| `-d` | *detached*: rode em segundo plano e devolva o terminal |
| `--name web` | dê o nome `web` (sem isso o Docker sorteia algo como `nostalgic_hopper`) |
| `-p 8080:80` | publique a porta **80 do container** na porta **8080 do host** |
| `nginx:alpine` | imagem `nginx`, tag `alpine` (variante minúscula, ~10 MB) |

**Verificação:**

```bash
curl -sI http://localhost:8080 | head -1
# esperado: HTTP/1.1 200 OK
```

Ou abra `http://localhost:8080` no navegador: aparece a página "Welcome to nginx!".

> **A ordem de `-p` é `host:container`, e trocá-la é o erro mais comum da semana 1.**
> `-p 8080:80` = "quem chegar na 8080 da minha máquina, mande para a 80 lá dentro".
> `-p 80:8080` faria o contrário e não funcionaria com o nginx, que escuta na 80.
>
> Mnemônico: **de fora para dentro**, esquerda para direita.

```bash
docker ps
# esperado: uma linha com IMAGE nginx:alpine, STATUS "Up X seconds", PORTS "0.0.0.0:8080->80/tcp"
```

### O que acabou de acontecer, por dentro

1. O Docker procurou `nginx:alpine` **localmente**. Não achou.
2. Baixou do Docker Hub, camada por camada (as barras de progresso são as camadas).
3. Criou um sistema de arquivos empilhando essas camadas + uma camada de escrita vazia por cima.
4. Criou namespaces novos (rede, PID, mount…) e iniciou o processo `nginx` dentro deles.
5. Programou uma regra de encaminhamento (iptables/nftables) mandando a porta 8080 do host para
   o IP interno do container.

Cada uma dessas cinco etapas tem um capítulo no Bloco B.

---

## Passo 2 — O ciclo de trabalho do dia a dia

Estes cinco comandos são 80% do seu uso cotidiano. Aprenda-os agora, não depois.

```bash
docker ps                    # o que está rodando
docker ps -a                 # + o que está parado (aqui moram os containers que morreram)
docker logs -f web           # ver a saída do processo, acompanhando (-f = follow, Ctrl+C sai)
docker exec -it web sh       # abrir um shell DENTRO do container que já está rodando
docker stop web              # parar (SIGTERM, e SIGKILL após 10s)
docker rm web                # remover o container parado
```

Experimente o `exec` — é onde o modelo mental se consolida:

```bash
docker exec -it web sh
```
```sh
# você agora está dentro do container
hostname          # um ID hexadecimal, não o nome da sua máquina
ls /              # um sistema de arquivos Linux completo, minúsculo
ps aux            # SÓ o nginx e o seu shell. PID 1 é o nginx!
cat /etc/os-release  # Alpine Linux, mesmo que seu host seja Ubuntu ou macOS
exit
```

> **`ps aux` mostrando apenas dois processos é a demonstração mais direta de namespace que
> existe.** Sua máquina tem centenas de processos rodando; o container enxerga dois. Não é
> filtragem cosmética — é o kernel devolvendo uma visão diferente da tabela de processos.

E o detalhe mais consequente:

> **PID 1 é o seu processo.** No Linux comum, PID 1 é o `init`/`systemd`, que adota processos
> órfãos e responde a sinais. Dentro do container, PID 1 é o seu app — e o kernel trata PID 1 de
> forma especial: **sinais que não têm tratador registrado são ignorados**. É por isso que
> alguns containers demoram exatos 10 segundos para parar: o `SIGTERM` do `docker stop` foi
> ignorado, e o Docker recorreu ao `SIGKILL` depois do timeout. A solução está em
> [17-dockerfile-e-build.md](17-dockerfile-e-build.md) (forma *exec* do `CMD`, `--init`).

Limpe antes de seguir:

```bash
docker stop web && docker rm web
```

---

## Passo 3 — Construir a sua primeira imagem

Rodar imagem dos outros é útil. Empacotar a sua é o que muda seu trabalho.

```bash
mkdir -p ~/docker-primeiros-passos && cd ~/docker-primeiros-passos
```

**`app.js`** — um servidor HTTP mínimo, sem dependência externa:

```javascript
// app.js — servidor HTTP com a biblioteca padrão do Node, sem npm install
const http = require('node:http');

const PORTA = process.env.PORT || 3000;
const NOME  = process.env.NOME || 'mundo';

const servidor = http.createServer((req, res) => {
  if (req.url === '/saude') {                       // usado pelo HEALTHCHECK adiante
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ status: 'ok' }));
  }
  res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });
  res.end(`Olá, ${NOME}! Rodando em ${require('node:os').hostname()}\n`);
});

// Sem isto, o container ignora o SIGTERM e demora 10s para parar.
process.on('SIGTERM', () => {
  console.log('SIGTERM recebido, encerrando com elegância...');
  servidor.close(() => process.exit(0));
});

servidor.listen(PORTA, '0.0.0.0', () => console.log(`ouvindo na porta ${PORTA}`));
```

> **`'0.0.0.0'` e não `'127.0.0.1'`.** Dentro do container, `127.0.0.1` significa "só eu mesmo".
> Se o app escutar apenas ali, o `-p` do host não alcança nada e você vê "connection refused"
> com o container aparentemente saudável. **Esta é a armadilha nº 2 de iniciante** — a nº 1 é
> inverter a ordem do `-p`.

**`Dockerfile`** — a receita:

```dockerfile
# syntax=docker/dockerfile:1
# ^ ativa os recursos modernos do BuildKit; mantenha sempre esta linha

FROM node:22-alpine
# imagem base: Node 22 sobre Alpine Linux (~50 MB contra ~400 MB da variante padrão)

WORKDIR /app
# cria e entra em /app; todos os comandos seguintes rodam a partir daqui

COPY app.js .
# copia do CONTEXTO DE BUILD (a pasta atual, no host) para /app dentro da imagem

USER node
# não rode como root. A imagem oficial do Node já traz o usuário 'node' (UID 1000)

EXPOSE 3000
# DOCUMENTAÇÃO apenas — não publica porta nenhuma. Quem publica é o -p do run

ENV PORT=3000
# valor padrão, sobrescrevível com -e PORT=... no run

CMD ["node", "app.js"]
# comando padrão, na forma EXEC (lista JSON). Nunca use a forma shell aqui — veja abaixo
```

Construa:

```bash
docker build -t meu-app:1.0 .
```
*O que faz:* lê o `Dockerfile` da pasta atual, envia a pasta (o *build context*) ao daemon e
produz uma imagem chamada `meu-app` com a tag `1.0`. **O `.` final é o contexto, não é
decoração** — é a pasta cujo conteúdo o `COPY` pode enxergar.

```bash
docker images meu-app
# esperado: REPOSITORY meu-app, TAG 1.0, SIZE ~140MB
```

Rode:

```bash
docker run -d --name app -p 3000:3000 -e NOME="Roni" meu-app:1.0
curl http://localhost:3000
# esperado: Olá, Roni! Rodando em <id hexadecimal>
curl http://localhost:3000/saude
# esperado: {"status":"ok"}
```

Pare e observe a diferença que o tratador de `SIGTERM` faz:

```bash
time docker stop app
# esperado: menos de 1 segundo (sem o handler, seriam exatos 10s)
docker rm app
```

### Forma *exec* vs. forma *shell* — a diferença que custa caro

```dockerfile
CMD ["node", "app.js"]        # ✅ forma EXEC: o node vira PID 1 e recebe os sinais
CMD node app.js               # ❌ forma SHELL: vira /bin/sh -c "node app.js"
                              #    o PID 1 é o sh, que NÃO repassa SIGTERM ao filho
```

Consequência real: com a forma shell, `docker stop` sempre demora 10 segundos e mata seu
processo à força — sem *graceful shutdown*, sem fechar conexões de banco, sem terminar a
requisição em curso. Em produção, isso é erro 502 no usuário a cada deploy.

---

## Passo 4 — Dados que sobrevivem: volumes

Prove primeiro que o container é descartável:

```bash
docker run -it --name teste alpine sh
```
```sh
echo "informação importantíssima" > /dados.txt
cat /dados.txt
exit
```
```bash
docker rm teste
docker run --rm alpine cat /dados.txt
# esperado: cat: can't open '/dados.txt': No such file or directory
```

O arquivo morreu com o container. Isso é **projeto**, não defeito: a camada de escrita do
container é efêmera por definição.

Agora com volume:

```bash
docker volume create meus-dados
docker run --rm -v meus-dados:/dados alpine sh -c 'echo "agora sobrevive" > /dados/f.txt'
docker run --rm -v meus-dados:/dados alpine cat /dados/f.txt
# esperado: agora sobrevive
```

Dois containers diferentes, ambos já destruídos, e o dado continua lá.

### Volume nomeado vs. bind mount — a distinção que organiza tudo

| | **Volume nomeado** | **Bind mount** |
|---|---|---|
| Sintaxe | `-v meus-dados:/dados` | `-v "$PWD/src:/app/src"` (caminho absoluto) |
| Onde fica | Gerenciado pelo Docker (`/var/lib/docker/volumes/`) | Numa pasta sua, que você escolhe |
| Para que serve | **Estado de produção**: banco de dados, uploads, cache | **Desenvolvimento**: editar código no host e ver dentro do container |
| Portabilidade | Funciona igual em qualquer host | Depende do caminho existir naquela máquina |
| Desempenho em macOS/Windows | Rápido (fica dentro da VM) | Lento (atravessa a fronteira host↔VM) |
| Permissões | Docker ajusta na criação | **Aqui mora a dor**: UID do container ≠ UID do host |

Use o bind mount agora, para o ciclo de desenvolvimento com recarga:

```bash
cd ~/docker-primeiros-passos
docker run -d --name dev -p 3000:3000 -v "$PWD:/app" -w /app node:22-alpine \
  sh -c "node --watch app.js"
```
*O que faz:* monta a pasta atual em `/app`, define `/app` como diretório de trabalho e roda o
Node com `--watch`, que reinicia sozinho a cada alteração de arquivo. **Nenhuma imagem foi
construída** — o código vem do host em tempo real.

Edite o `app.js` (mude o texto do "Olá") e salve. Depois:

```bash
docker logs dev          # deve mostrar o Node reiniciando
curl http://localhost:3000   # o texto novo aparece, sem rebuild
docker rm -f dev
```

> **A regra que organiza a cabeça:** bind mount para **código durante o desenvolvimento**;
> volume nomeado para **dados que precisam viver**. Nunca coloque banco de dados de produção
> em bind mount, e nunca dependa de bind mount para entregar código em produção — em produção,
> o código vai **dentro** da imagem.

---

## Passo 5 — Vários containers juntos: Compose

Aplicação real quase nunca é um container só. Fazer isso com `docker run` exige criar rede à
mão, lembrar a ordem, gerenciar nomes. Compose descreve tudo num arquivo.

**`compose.yaml`** na mesma pasta:

```yaml
# compose.yaml — não precisa de "version:", ele é obsoleto na especificação atual
services:

  app:
    build: .                      # constrói a partir do Dockerfile desta pasta
    ports:
      - "3000:3000"               # host:container
    environment:
      NOME: "mundo containerizado"
      REDIS_URL: "redis://cache:6379"   # 'cache' é o NOME DO SERVIÇO abaixo
    depends_on:
      cache:
        condition: service_healthy      # só sobe quando o redis estiver realmente pronto
    restart: unless-stopped

  cache:
    image: redis:7-alpine
    volumes:
      - dados-redis:/data          # o estado do redis num volume nomeado
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  dados-redis:                     # declara o volume nomeado usado acima
```

```bash
docker compose up -d
# esperado: linhas "Container <pasta>-cache-1  Healthy" e "<pasta>-app-1  Started"
```

```bash
docker compose ps
# esperado: dois serviços, ambos "running"; o cache com "(healthy)"
curl http://localhost:3000
# esperado: Olá, mundo containerizado! ...
```

### As três coisas que o Compose fez por você

1. **Criou uma rede privada** para o projeto. Os dois containers estão nela e em nenhuma outra.
2. **Deu DNS interno**: dentro do container `app`, o nome `cache` resolve para o IP do Redis.
   Você **nunca** usa IP no Compose — usa o nome do serviço.
3. **Respeitou a ordem** graças ao `depends_on` + `healthcheck`. Sem o `condition:
   service_healthy`, o `depends_on` só garante que o container *iniciou*, não que o serviço
   *está pronto* — distinção que causa muita falha intermitente.

Prove o DNS interno:

```bash
docker compose exec app sh -c "nslookup cache"
# esperado: um endereço 172.x.x.x — o IP do container do Redis na rede do projeto
```

Comandos do dia a dia com Compose:

```bash
docker compose up -d          # sobe tudo em segundo plano
docker compose logs -f app    # logs de um serviço
docker compose logs -f        # logs de todos, entrelaçados e coloridos
docker compose ps             # o que está de pé
docker compose exec app sh    # shell num serviço
docker compose restart app    # reinicia um serviço
docker compose up -d --build  # reconstrói a imagem e sobe
docker compose down           # derruba tudo e remove a rede (VOLUMES ficam)
docker compose down -v        # ⚠️ derruba e APAGA OS VOLUMES — perde os dados
```

---

## Os cinco primeiros erros de uso (não de instalação)

Instalação já foi tratada no [03](03-instalacao.md). Estes são os erros do **uso**, na ordem em
que aparecem na vida real:

### 1. `-p` invertido → "connection refused"
```bash
docker run -p 80:8080 nginx     # ❌ nginx escuta na 80, não na 8080
docker run -p 8080:80 nginx     # ✅
```
**Diagnóstico:** `docker port <container>` mostra o mapeamento real; `docker logs` mostra em que
porta o app disse que subiu.

### 2. App escutando em `127.0.0.1` dentro do container → "connection refused" com container saudável
O container tem loopback próprio. `127.0.0.1` lá dentro não é a sua máquina.
**Correção:** faça o app escutar em `0.0.0.0`. Isso vale para Flask (`--host=0.0.0.0`), Vite
(`--host`), Rails (`-b 0.0.0.0`), `dotnet` (`ASPNETCORE_URLS=http://0.0.0.0:8080`) e todos os outros.

### 3. Editar arquivo dentro do container e perder tudo
```bash
docker exec -it app vi /app/config.json    # a edição morre com o container
```
**Correção:** edite no host e reconstrua a imagem, ou use bind mount durante o desenvolvimento.
Container **não é servidor**; é artefato descartável.

### 4. `docker compose down -v` num container de banco
O `-v` apaga volumes. Some o banco inteiro, sem confirmação.
**Correção:** `docker compose down` (sem `-v`) para o dia a dia. Reserve `-v` para quando você
*quer* zerar. E faça backup:
```bash
docker run --rm -v dados-redis:/d -v "$PWD:/b" alpine tar czf /b/backup.tgz -C /d .
```

### 5. Container "sai imediatamente" (`Exited (0)`) e você não entende
```bash
docker run -d ubuntu           # sai na hora
docker ps -a                   # STATUS: Exited (0) 2 seconds ago
```
**Causa:** um container vive exatamente enquanto o processo PID 1 viver. A imagem `ubuntu` tem
`CMD ["bash"]`; sem terminal interativo, o bash lê EOF e termina — e o container com ele.
**Correção:** dê a ele um processo que fique de pé (`nginx`, seu app) ou use `-it` para dar um
terminal:
```bash
docker run -it ubuntu bash     # ✅ agora tem terminal, e o bash fica
```
**Diagnóstico geral de container que morre:** `docker logs <nome>` (funciona mesmo com o
container parado) e `docker inspect --format '{{.State.ExitCode}} {{.State.Error}}' <nome>`.

---

## Limpeza ao terminar

```bash
docker compose down
docker rm -f $(docker ps -aq) 2>/dev/null || true   # remove todos os containers
docker system df                                    # veja o que sobrou de espaço
```

---

## Para onde ir agora

| Se você quer… | Vá para |
|---|---|
| Uma referência de comandos para consultar | [05-manual-de-uso.md](05-manual-de-uso.md) |
| Mais receitas prontas, do trivial ao de produção | [06-exemplos.md](06-exemplos.md) |
| Uma aplicação completa que roda de verdade | [07-projeto-modelo/](07-projeto-modelo/README.md) |
| Entender o que acontece por baixo | [10-fundamentos.md](10-fundamentos.md) |
| Exercícios com critério de aprovação | [70-pratica.md](70-pratica.md) |

---

## Autoteste

1. Em `-p 3000:80`, qual número é o do host e qual é o do container? Como você lembra disso?
2. Você roda `docker run -d ubuntu` e o container morre imediatamente. Explique por quê, em
   termos de PID 1.
3. Qual é a diferença entre `docker stop` e `docker kill`, e em quantos segundos um vira o outro?
4. Seu app responde em `localhost:5000` quando roda direto na máquina, mas dá "connection
   refused" quando containerizado, e o container está de pé. Qual é a hipótese nº 1?
5. Por que `CMD node app.js` e `CMD ["node","app.js"]` produzem comportamentos diferentes ao
   parar o container?
6. Quando usar volume nomeado e quando usar bind mount? Dê um exemplo de cada.
7. No Compose, como o container `app` encontra o container `cache` sem saber o IP dele?
8. Qual é a diferença entre `docker compose down` e `docker compose down -v`, e por que a
   segunda merece medo?
9. `EXPOSE 3000` no Dockerfile publica a porta? Se não, o que ele faz?
