import { createServer } from "node:http";
import { carregarConfig } from "./config.js";
import { criarApp } from "./app.js";
import { criarServico } from "./servico.js";
import { criarRepositorioMemoria } from "./repositorio-memoria.js";
import { criarCacheMemoria } from "./cache-memoria.js";

const config = carregarConfig();

// Escolha de adaptadores em UM lugar só. O resto do sistema não sabe qual venceu.
const repo = config.databaseUrl
  ? (await import("./repositorio-pg.js")).criarRepositorioPg(config.databaseUrl)
  : criarRepositorioMemoria();

const cache = config.redisUrl
  ? (await import("./cache-redis.js")).criarCacheRedis(config.redisUrl)
  : criarCacheMemoria();

if (config.modoMemoria) {
  console.warn(JSON.stringify({
    nivel: "aviso",
    msg: "sem DATABASE_URL: rodando em MODO MEMÓRIA. Os dados somem ao reiniciar.",
  }));
}

const servidor = createServer(criarApp({ servico: criarServico({ repo, cache, config }), config }));

servidor.listen(config.porta, "0.0.0.0", () =>
  console.log(JSON.stringify({ nivel: "info", msg: `ouvindo em 0.0.0.0:${config.porta}`, modo: `${repo.tipo}+${cache.tipo}` })));

// Encerramento gracioso. A plataforma manda SIGTERM e espera alguns segundos
// antes de matar o container. Sem isto, todo deploy corta requisições em andamento.
let encerrando = false;
for (const sinal of ["SIGTERM", "SIGINT"]) {
  process.on(sinal, async () => {
    if (encerrando) return;
    encerrando = true;
    console.log(JSON.stringify({ nivel: "info", msg: `${sinal} recebido, encerrando` }));
    servidor.close();
    const prazo = setTimeout(() => process.exit(1), 10_000);  // não espere para sempre
    await Promise.allSettled([repo.fechar(), cache.fechar()]);
    clearTimeout(prazo);
    process.exit(0);
  });
}
