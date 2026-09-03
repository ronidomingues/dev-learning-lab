// Utilitários de teste: sobe a aplicação inteira com adaptadores em memória,
// numa porta livre (porta 0 = o sistema operacional escolhe).
import { createServer } from "node:http";
import { criarApp } from "../src/app.js";
import { criarServico } from "../src/servico.js";
import { criarRepositorioMemoria } from "../src/repositorio-memoria.js";
import { criarCacheMemoria } from "../src/cache-memoria.js";
import { carregarConfig } from "../src/config.js";

export async function subirApp(env = {}) {
  const config = carregarConfig({ PORT: "0", BASE_URL: "http://teste.local", ...env });
  const repo = criarRepositorioMemoria();
  const cache = criarCacheMemoria();
  const servico = criarServico({ repo, cache, config });
  const servidor = createServer(criarApp({ servico, config }));

  await new Promise((r) => servidor.listen(0, "127.0.0.1", r));
  const { port } = servidor.address();
  const base = `http://127.0.0.1:${port}`;

  return {
    base, repo, cache, servico, config,
    get: (rota, opcoes) => fetch(base + rota, { redirect: "manual", ...opcoes }),
    post: (rota, corpo) => fetch(base + rota, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(corpo),
      redirect: "manual",
    }),
    async fechar() { await new Promise((r) => servidor.close(r)); },
  };
}
