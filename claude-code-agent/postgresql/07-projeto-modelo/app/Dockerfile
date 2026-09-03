# syntax=docker/dockerfile:1
# Imagem da aplicação. Multi-stage enxuto, não-root. Ver o curso de Docker para os detalhes.

FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
# Se não houver lockfile ainda, 'npm install' resolve; com lockfile, 'npm ci' é reprodutível.
RUN --mount=type=cache,target=/root/.npm \
    if [ -f package-lock.json ]; then npm ci --omit=dev; else npm install --omit=dev; fi

FROM node:22-alpine AS producao
ENV NODE_ENV=production
WORKDIR /app
COPY --from=deps --chown=node:node /app/node_modules ./node_modules
COPY --chown=node:node . .
USER node
EXPOSE 3000
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s \
  CMD wget -qO- http://127.0.0.1:3000/saude || exit 1
CMD ["node", "src/server.js"]
