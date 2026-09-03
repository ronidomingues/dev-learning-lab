# Exercício — Fundamentos

> **Tente resolver antes de rolar até a solução.** A resposta está na segunda
> metade do arquivo, depois do separador.

## Enunciado

### Parte A — investigação

1. Baixe a imagem `nginx:1.29-alpine` e descubra **quantas camadas** ela tem e
   qual é a maior.
2. Rode dois containers dessa mesma imagem ao mesmo tempo, em portas diferentes
   do host (8081 e 8082), com nomes `web1` e `web2`.
3. Crie um arquivo `/tmp/teste.txt` **dentro** do `web1`. Confirme que ele
   **não** existe no `web2`. Explique por quê.
4. Remova o `web1`, recrie um container com o mesmo nome e mesma imagem.
   O arquivo voltou? Por quê?
5. Descubra quanto espaço o Docker ocupa no seu disco, separado por categoria.

### Parte B — raciocínio

6. Você tem 5 imagens diferentes, todas com `FROM python:3.12-slim`, cada uma
   com ~30 MB de código próprio. `docker images` mostra 5 linhas de ~73 MB.
   O disco tem 365 MB a menos? Justifique.

7. Um colega escreveu:
   ```dockerfile
   FROM python:3.12-slim
   COPY credenciais.json /app/
   RUN python configurar.py && rm /app/credenciais.json
   ```
   Ele afirma que está seguro porque apagou o arquivo. Ele está certo?
   Se não, mostre como um atacante recuperaria o arquivo.

8. Explique por que este comando não faz o que parece:
   ```bash
   docker run -p 80:8080 nginx:1.29-alpine
   ```

---
---
---

# SOLUÇÃO COMENTADA

## Parte A

### 1. Camadas da imagem

```bash
docker pull nginx:1.29-alpine
docker history nginx:1.29-alpine
```

Saída no formato:

```
IMAGE          CREATED       CREATED BY                                      SIZE
a1b2c3d4e5f6   2 weeks ago   CMD ["nginx" "-g" "daemon off;"]                0B
<missing>      2 weeks ago   STOPSIGNAL SIGQUIT                              0B
<missing>      2 weeks ago   EXPOSE map[80/tcp:{}]                           0B
<missing>      2 weeks ago   ENTRYPOINT ["/docker-entrypoint.sh"]            0B
<missing>      2 weeks ago   COPY docker-entrypoint.sh / # buildkit          1.62kB
<missing>      2 weeks ago   RUN /bin/sh -c set -x && apkArch="$(cat...      13.4MB
<missing>      3 weeks ago   /bin/sh -c #(nop) ADD file:...in /               7.8MB
```

Para ordenar por tamanho:

```bash
docker history nginx:1.29-alpine --format '{{.Size}}\t{{.CreatedBy}}' | sort -h -r | head -3
```

**O que observar:** a maior camada é o `RUN` que instala o nginx via `apk`.
Instruções como `EXPOSE`, `CMD` e `ENTRYPOINT` ocupam **0 B** — são metadados,
não alteram o filesystem. E o `<missing>` não é erro: camadas intermediárias de
imagens baixadas não recebem ID local, só a final recebe.

### 2. Dois containers da mesma imagem

```bash
docker run -d --name web1 -p 8081:80 nginx:1.29-alpine
docker run -d --name web2 -p 8082:80 nginx:1.29-alpine
docker ps
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8081   # 200
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082   # 200
```

Repare que **as portas do host diferem, a do container é a mesma (80)**. Cada
container tem sua própria pilha de rede — não há conflito no 80 interno. O
conflito só existiria no host.

### 3. Isolamento do filesystem

```bash
docker exec web1 sh -c 'echo "oi" > /tmp/teste.txt'
docker exec web1 cat /tmp/teste.txt    # oi
docker exec web2 cat /tmp/teste.txt    # cat: can't open '/tmp/teste.txt': No such file
```

**Por quê:** os dois containers compartilham as camadas **somente-leitura** da
imagem, mas cada um tem sua **própria camada de escrita**. Escrever no `web1`
grava na camada dele. O `web2` continua vendo apenas a imagem original.

Analogia: dois processos rodando o mesmo `/usr/bin/python`. O binário é um só; a
memória de cada processo é privada.

### 4. O arquivo não volta

```bash
docker rm -f web1
docker run -d --name web1 -p 8081:80 nginx:1.29-alpine
docker exec web1 cat /tmp/teste.txt
# cat: can't open '/tmp/teste.txt': No such file or directory
```

**Por quê:** a camada de escrita é criada junto com o container e destruída
junto com ele. O `docker rm` apagou aquela camada. O novo container nasceu com
uma camada de escrita vazia por cima da mesma imagem imutável.

**A lição central do módulo:** container é descartável por natureza. Se o dado
precisa sobreviver, ele **não pode** morar na camada de escrita — precisa de
volume ([módulo 04](../04-armazenamento/bind-mount-vs-volume.md)).

### 5. Uso de disco

```bash
docker system df
```

```
TYPE            TOTAL   ACTIVE  SIZE      RECLAIMABLE
Images          12      2       3.421GB   2.883GB (84%)
Containers      5       2       142.3MB   98.11MB (68%)
Local Volumes   8       1       1.204GB   1.108GB (92%)
Build Cache     47      0       2.116GB   2.116GB (100%)
```

Detalhe por item: `docker system df -v`.

**O que observar:** o *Build Cache* costuma ser o maior vilão e é o mais seguro
de limpar (`docker builder prune`). Já `Local Volumes` reclaimable alto é um
alerta — pode haver dado seu ali. Nunca rode `prune --volumes` sem olhar antes.

## Parte B

### 6. Não, o disco não tem 365 MB a menos

`docker images` mostra o **tamanho lógico** de cada imagem — o total que ela
ocuparia sozinha. Como todas compartilham as mesmas camadas de
`python:3.12-slim`, essa base é armazenada **uma única vez**.

Conta real: 43 MB (base compartilhada) + 5 × 30 MB (código próprio) ≈ **193 MB**,
não 365 MB.

Para ver o número verdadeiro:

```bash
docker system df
# a coluna SIZE de Images é o uso real em disco, já descontando o compartilhamento
```

**Consequência prática:** padronizar a imagem base entre seus projetos economiza
disco de verdade e acelera o `pull` (camadas já presentes não são baixadas de
novo). É um bom motivo para o FlixARD e o sistema financeiro usarem a mesma base.

### 7. Não, ele não está seguro — e é grave

Camadas são **aditivas**. A camada do `COPY` gravou o arquivo; a camada do `RUN`
apenas registrou um marcador de exclusão por cima. O conteúdo continua na
imagem, e é trivial extrair:

```bash
# Caminho 1: ver que a camada existe e o que ela fez
docker history --no-trunc imagem-do-colega

# Caminho 2: extrair o filesystem em camadas e ler o arquivo
docker save imagem-do-colega -o imagem.tar
mkdir extraido && tar -xf imagem.tar -C extraido
# cada blob é uma camada; a que veio do COPY contém credenciais.json
grep -rl "credenciais" extraido/ 2>/dev/null

# Caminho 3: o mais direto — criar um container a partir da camada
#            intermediária, anterior ao rm
docker history imagem-do-colega        # pegar o ID da camada antes do RUN
docker run --rm -it <id-da-camada> cat /app/credenciais.json
```

**As três formas corretas:**

```dockerfile
# 1) Multi-stage: o segredo fica num estágio descartado
FROM python:3.12-slim AS configuracao
COPY credenciais.json /app/
RUN python configurar.py && cp resultado.conf /saida.conf

FROM python:3.12-slim
COPY --from=configuracao /saida.conf /app/   # só o resultado atravessa
```

```dockerfile
# 2) BuildKit secret: o arquivo é montado durante o RUN e nunca vira camada
RUN --mount=type=secret,id=cred,target=/tmp/credenciais.json \
    python configurar.py
# docker build --secret id=cred,src=./credenciais.json .
```

```
# 3) Nem chegar perto do build context
echo "credenciais.json" >> .dockerignore
```

**E o mais importante:** se essa imagem já foi publicada, o segredo está
comprometido. Apagar a imagem não desfaz o download de quem já baixou.
**Rotacione a credencial.**

### 8. As portas estão invertidas

```bash
docker run -p 80:8080 nginx:1.29-alpine
```

A sintaxe é `-p HOST:CONTAINER`. O comando acima diz: "escute na porta **80 do
host** e encaminhe para a **8080 do container**". Mas o nginx escuta na **80**
dentro do container, não na 8080. Ninguém atende na 8080.

Resultado: o `docker run` **funciona**, o container sobe **saudável**, e
`curl http://localhost:80` devolve `Empty reply from server` ou timeout. É o pior
tipo de erro — silencioso, sem mensagem, e você procura no lugar errado.

Correto:

```bash
docker run -p 80:80 nginx:1.29-alpine     # host 80 -> container 80
docker run -p 8080:80 nginx:1.29-alpine   # host 8080 -> container 80
```

**Como diagnosticar quando acontecer:**

```bash
docker port <container>              # mostra o mapeamento efetivo
docker exec <container> netstat -tlnp  # em que porta o processo REALMENTE escuta
```

Regra para nunca mais errar: **o número da direita é o que a aplicação escuta.**
Ele é ditado pela aplicação e você não escolhe. O da esquerda é seu.

---
[← conceitos](conceito.md) · [módulo 02: Dockerfile →](../02-dockerfile/diretivas-completas.md) · [índice](../00-indice.md)
