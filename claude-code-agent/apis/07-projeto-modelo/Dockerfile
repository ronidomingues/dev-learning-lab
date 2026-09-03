# Imagem mínima: sem dependências para instalar, o build é uma cópia.
FROM node:24-alpine

# Rodar como root dentro do container é o padrão do Docker e é uma má ideia:
# uma falha de execução remota passa a ter root no container. A imagem oficial
# do Node já traz o usuário "node" — use-o.
WORKDIR /app
COPY --chown=node:node package.json ./
COPY --chown=node:node src ./src
USER node

ENV NODE_ENV=production
ENV PORT=3000
EXPOSE 3000

# Sonda de saúde: o orquestrador precisa saber se o processo está vivo.
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:'+(process.env.PORT||3000)+'/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

# Exec form (sem shell): o processo Node vira PID 1 e RECEBE o SIGTERM,
# que é o que faz o desligamento gracioso funcionar. Com a shell form,
# o sinal ia para o /bin/sh e o Node era morto sem drenar as conexões.
CMD ["node", "src/servidor.js"]
