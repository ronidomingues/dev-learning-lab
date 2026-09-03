# Cache de camadas: a diferença entre 2 s e 90 s

> **Nível:** intermediário
> **Última verificação:** 18/08/2026

Este é o conhecimento com o melhor retorno por minuto de estudo em todo o
Docker. Não muda o que a imagem faz — muda quantas vezes por dia você espera.

## 1. A regra, em uma frase

> Para cada instrução, o Docker calcula uma chave de cache. Se já existe uma
> camada com aquela chave, ele **reaproveita**. Se não existe, ele executa — e
> a partir daí, **todas as instruções seguintes são reexecutadas**, mesmo as
> idênticas.

A segunda metade é o que importa. O cache não é por instrução isolada: é uma
**cadeia**. Quebrou no meio, tudo abaixo cai junto.

```
FROM python:3.12-slim-trixie   ✅ cache
WORKDIR /app                   ✅ cache
COPY requirements.txt .        ✅ cache
RUN pip install -r req.txt     ✅ cache      ← 88 s economizados
COPY app/ ./app/               ❌ mudou      ← você editou um .py
CMD [...]                      ❌ refaz      ← em cascata, mesmo sem ter mudado
```

## 2. Como a chave de cache é calculada

Depende do tipo de instrução:

| Instrução | A chave considera |
|---|---|
| `RUN` | o **texto literal** do comando (o Docker não executa para comparar) |
| `COPY` / `ADD` | o **conteúdo** dos arquivos (checksum), além do caminho |
| `FROM` | o digest da imagem base |
| `ENV`, `ARG`, `WORKDIR` | o valor |

Duas consequências que pegam todo mundo:

**`RUN` compara texto, não resultado.** `RUN apt-get update` tem sempre o mesmo
texto — o Docker reaproveita a camada por semanas, servindo uma lista de pacotes
velha. Depois `apt-get install` falha com `404 Not Found`. É por isso que
`update` e `install` precisam estar **no mesmo `RUN`**: o texto único amarra os
dois.

**`COPY` compara conteúdo, não data.** Salvar um arquivo sem alterar nada **não**
invalida o cache. Bom saber quando o editor "toca" arquivos ao salvar.

## 3. A ordem correta: do estável ao volátil

Princípio único: **o que muda menos vem primeiro.**

```dockerfile
# syntax=docker/dockerfile:1

# ❌ ERRADO — o pip install refaz a cada edição de código
FROM python:3.12-slim-trixie
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

```dockerfile
# syntax=docker/dockerfile:1

# ✅ CERTO — dependências antes do código
FROM python:3.12-slim-trixie
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

A única diferença é **onde o código é copiado**. Na versão errada, `COPY . .`
invalida o cache a cada caractere digitado, e o `pip install` refaz sempre. Na
certa, o `requirements.txt` viaja sozinho: enquanto ele não mudar, a instalação
é reaproveitada.

### Um detalhe que vale registrar

Ambos os arquivos acima passam **limpos** no `hadolint`:

```bash
hadolint Dockerfile.ruim   # saída obtida: (vazio) — nenhum aviso
hadolint Dockerfile.bom    # saída obtida: (vazio) — nenhum aviso
```

Linter checa sintaxe e boas práticas catalogadas; **não** entende que o seu
código muda mais que suas dependências. Ordenação de cache é decisão de
engenharia, e nenhuma ferramenta vai apontá-la para você.

### Ordem canônica

```dockerfile
FROM ...                    # 1. base           — muda a cada meses
RUN apt-get install ...     # 2. libs do SO     — muda a cada meses
COPY requirements.txt .     # 3. manifesto      — muda a cada semanas
RUN pip install ...         # 4. dependências   — segue o manifesto
COPY app/ ./app/            # 5. seu código     — muda a cada minutos
```

## 4. Cache mount: o nível seguinte

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

Isto monta um diretório persistente **durante** o `RUN`. Ele não vira camada.

A diferença aparece quando o cache **é** invalidado — quando você adiciona uma
dependência. Sem cache mount, o pip rebaixa tudo da internet. Com ele, os wheels
já baixados estão lá e só o pacote novo é buscado.

Equivalentes por ecossistema:

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip      pip install -r requirements.txt
RUN --mount=type=cache,target=/root/.npm            npm ci
RUN --mount=type=cache,target=/go/pkg/mod           go mod download
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt/lists \
    apt-get update && apt-get install -y curl
```

Note que com cache mount para o apt você **não** deve fazer `rm -rf
/var/lib/apt/lists/*` — o diretório é um mount, não uma camada; não incha a
imagem e apagar só desperdiça o cache.

Requer BuildKit, ativo por padrão desde o Docker 23. A linha
`# syntax=docker/dockerfile:1` no topo garante a sintaxe disponível.

## 5. Bind mount de arquivo: evitar o COPY

Padrão mais avançado — usar o arquivo sem copiá-lo para uma camada:

```dockerfile
RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    --mount=type=cache,target=/root/.cache/pip \
    pip install -r /tmp/requirements.txt
```

O `requirements.txt` nunca entra na imagem. Menor, e sem arquivo de build
sobrando no runtime.

## 6. Diagnosticar cache

```bash
# Ver o que foi reaproveitado (procure "CACHED" na saída)
docker build --progress=plain -t app:dev .

# Buildar sem cache nenhum, para comparar tempos
docker build --no-cache -t app:dev .

# Ver o custo de cada camada da imagem pronta
docker history app:dev

# Quanto o cache de build está ocupando
docker system df
docker builder prune          # limpar (seguro: só cache)
```

Na saída de `--progress=plain`, cada passo aparece assim:

```
#8 [4/6] RUN pip install -r requirements.txt
#8 CACHED
```

`CACHED` = reaproveitado. A primeira linha **sem** `CACHED` é o ponto de quebra —
é ali que você deve olhar.

## 7. Cache em CI: o problema do runner efêmero

Na sua máquina o cache é local e funciona sozinho. No CI, cada job começa numa
máquina limpa: **cache zero, sempre**. Builds de 90 s viram 90 s toda vez.

Solução — exportar e importar o cache de um registry:

```bash
docker buildx build \
  --cache-from=type=registry,ref=meuregistry/app:cache \
  --cache-to=type=registry,ref=meuregistry/app:cache,mode=max \
  -t meuregistry/app:1.0.0 --push .
```

`mode=max` exporta o cache de **todos** os estágios, inclusive os intermediários
do multi-stage — importante, porque o padrão (`mode=min`) só guarda o estágio
final e o builder recomeça do zero.

No GitHub Actions, o atalho é `type=gha`:

```yaml
- uses: docker/build-push-action@v6
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## 8. Os cinco porquês do cache

1. **Por que existe cache de camada?** Porque rebuildar tudo a cada mudança seria
   inviável no dia a dia.
2. **Por que dá para reaproveitar com segurança?** Porque camadas são imutáveis
   e endereçadas por conteúdo — mesma entrada, mesma saída.
3. **Por que "mesma entrada" para um `RUN` é o texto, e não o resultado?**
   Porque descobrir o resultado exigiria **executar** o comando, que é
   exatamente o custo que se quer evitar. É uma aproximação deliberada.
4. **Por que essa aproximação é aceitável?** Porque comandos de build deveriam
   ser determinísticos. Quando não são (`apt-get update`, `pip install` sem
   pino), a aproximação falha — e a culpa é do Dockerfile, não do Docker.
5. **Por que então não pinar tudo sempre?** Porque pino tem custo de manutenção
   e quebra quando o repositório remove a versão antiga (é o que acontece com
   `.deb` de segurança). **Parada legítima: trade-off explícito entre
   reprodutibilidade e manutenção.**

## 9. Erros que você provavelmente vai cometer

| Sintoma | Causa raiz | Correção |
|---|---|---|
| build reinstala tudo a cada edição | `COPY . .` antes do install | copiar o manifesto sozinho primeiro |
| `404 Not Found` no `apt-get install` | camada de `update` cacheada há semanas | `update && install` no mesmo `RUN` |
| cache nunca acerta no CI | runner efêmero, cache local inexistente | `--cache-from/--cache-to` em registry |
| build lento mesmo com ordem certa | `.dockerignore` ausente; `.git` no contexto | criar `.dockerignore` |
| multi-stage não cacheia no CI | `mode=min` só exporta o estágio final | `mode=max` |
| disco cheio de cache | acumula sem limite | `docker builder prune` |

## 10. Autoteste

1. Por que invalidar uma camada afeta todas as seguintes?
2. O que o Docker compara para decidir o cache de um `RUN`? E de um `COPY`?
3. Por que `apt-get update` sozinho num `RUN` causa `404` semanas depois?
4. Qual a diferença entre `--mount=type=cache` e uma camada normal?
5. Por que o `hadolint` não aponta erro de ordenação?
6. Por que `mode=max` importa em multi-stage no CI?
7. Como descobrir qual instrução quebrou o cache?

---
[← diretivas](diretivas-completas.md) · [multi-stage →](multi-stage-build.md) · [índice](../00-indice.md)
