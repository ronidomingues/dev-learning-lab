# syntax=docker/dockerfile:1.7
# Imagem de produção em três estágios. Ver 06-exemplos.md, exemplo 8, para o porquê de cada linha.

FROM node:24.18.0-slim AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
# npm ci exige lockfile; se não houver, cai para install (só acontece no primeiro clone).
RUN --mount=type=cache,target=/root/.npm \
    if [ -f package-lock.json ]; then npm ci --omit=dev; else npm install --omit=dev; fi

FROM node:24.18.0-slim AS runtime
ENV NODE_ENV=production
RUN apt-get update && apt-get install -y --no-install-recommends dumb-init \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY package.json ./
COPY src ./src
COPY sql ./sql
COPY public ./public

USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:'+(process.env.PORT||3000)+'/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "src/server.js"]
