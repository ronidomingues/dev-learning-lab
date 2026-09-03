# syntax=docker/dockerfile:1
#
# Dockerfile do projeto-modelo — multi-stage com três estágios:
#   base        camada comum, para não repetir configuração
#   dev         com --watch, usado pelo perfil de desenvolvimento
#   testes      roda a suíte e falha o build se algum teste quebrar
#   producao    o que vai para o servidor: mínimo, sem root, com healthcheck
#
# Construir só um estágio:  docker build --target dev -t mural:dev .

# ---------------------------------------------------------------------------
# base — tudo que os outros estágios compartilham
# ---------------------------------------------------------------------------
FROM node:22-alpine AS base

# tini é um init de 10 KB: vira PID 1, repassa sinais ao processo real e colhe zumbis.
# Sem ele (ou sem `--init`), um processo filho órfão nunca é colhido e a tabela de processos
# do container acumula zumbis até estourar o pids-limit.
RUN apk add --no-cache tini

WORKDIR /app

# O diretório de dados é criado NA IMAGEM, já com o dono certo. Isso importa: quando um volume
# nomeado vazio é montado sobre um caminho que existe na imagem, o Docker copia o conteúdo E as
# permissões daquele caminho para o volume. É assim que um container sem root consegue escrever
# num volume — sem isso, o volume nasceria pertencendo ao root e o app tomaria EACCES.
RUN mkdir -p /dados && chown -R node:node /dados /app

ENV NODE_ENV=production \
    ARQUIVO_DADOS=/dados/recados.json \
    PORT=3000 \
    HOST=0.0.0.0

# ---------------------------------------------------------------------------
# dev — recarga automática, código vindo por bind mount
# ---------------------------------------------------------------------------
FROM base AS dev
ENV NODE_ENV=development
COPY --chown=node:node app/package.json ./package.json
COPY --chown=node:node app/src ./src
COPY --chown=node:node app/test ./test
USER node
EXPOSE 3000
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "--watch", "src/server.js"]

# ---------------------------------------------------------------------------
# testes — estágio dedicado. `docker build --target testes .` falha se um teste falhar,
# o que transforma o próprio build num portão de qualidade.
# ---------------------------------------------------------------------------
FROM base AS testes
ENV NODE_ENV=test
COPY --chown=node:node app/package.json ./package.json
COPY --chown=node:node app/src ./src
COPY --chown=node:node app/test ./test
USER node
# `node --test` sem argumento descobre os arquivos *.test.js sozinho — funciona igual no
# Node 22 e no 24. Passar um diretório mudou de comportamento entre versões; não faça isso.
RUN node --test

# ---------------------------------------------------------------------------
# producao — imagem final
# ---------------------------------------------------------------------------
FROM base AS producao

# Metadados no padrão OCI: aparecem no `docker inspect` e em ferramentas de inventário.
LABEL org.opencontainers.image.title="mural-de-recados" \
      org.opencontainers.image.description="Projeto-modelo do curso de Docker" \
      org.opencontainers.image.source="https://github.com/exemplo/mural" \
      org.opencontainers.image.licenses="MIT"

# Somente o necessário para EXECUTAR. Testes e ferramental ficam de fora — menos tamanho
# e menos superfície de ataque.
COPY --chown=node:node app/package.json ./package.json
COPY --chown=node:node app/src ./src

# Trocar de usuário DEPOIS dos COPY: as camadas de cópia precisam de permissão de escrita.
USER node

EXPOSE 3000

# O healthcheck bate na rota que realmente exercita o disco. Um healthcheck que só devolve 200
# sem tocar na dependência crítica declara "saudável" um container incapaz de trabalhar.
# start-period dá carência ao boot: falhas ali não contam como unhealthy.
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/saude || exit 1

# tini como PID 1; o node é o filho que recebe os sinais corretamente.
ENTRYPOINT ["/sbin/tini", "--"]
# Forma exec (lista JSON), nunca a forma shell — é o que garante que o SIGTERM chegue ao node.
CMD ["node", "src/server.js"]
