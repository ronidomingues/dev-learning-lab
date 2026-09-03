# syntax=docker/dockerfile:1.7
#
# Imagem sem NENHUM segredo dentro. Comprove depois de construir:
#   docker history --no-trunc cofre-de-recados | grep -iE 'secret|token|password'
#   docker inspect -f '{{json .Config.Env}}' cofre-de-recados
#
FROM node:22-alpine AS runtime

# Se houvesse dependências privadas, o token do registry entraria assim —
# via BuildKit, que NÃO grava o segredo em nenhuma camada:
#   RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci --omit=dev
# e o build seria:  docker build --secret id=npmrc,src=$HOME/.npmrc .
# Este projeto tem zero dependências, então nem isso é preciso.

WORKDIR /app
ENV NODE_ENV=production

COPY package.json ./
COPY src ./src

# Roda como usuário sem privilégio (a imagem oficial já traz o usuário "node").
USER node

EXPOSE 3000

# Falha rápida: o contêiner nem sobe se a configuração estiver errada.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:'+(process.env.PORT||3000)+'/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

CMD ["node", "src/app.mjs"]
