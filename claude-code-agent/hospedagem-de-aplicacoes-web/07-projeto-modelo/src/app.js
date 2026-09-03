import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { ErroDominio } from "./erros.js";

const INDEX = fileURLToPath(new URL("../public/index.html", import.meta.url));

/**
 * Cria o handler HTTP. Recebe o serviço já pronto — nenhuma dependência de
 * infraestrutura é construída aqui. É o que permite testar com adaptadores em memória.
 */
export function criarApp({ servico, config }) {
  return async function handler(req, res) {
    const inicio = process.hrtime.bigint();
    const url = new URL(req.url, `http://${req.headers.host ?? "localhost"}`);
    const caminho = url.pathname;

    const responder = (status, corpo, cabecalhos = {}) => {
      const texto = typeof corpo === "string" ? corpo : JSON.stringify(corpo);
      res.writeHead(status, {
        "content-type": typeof corpo === "string" ? "text/html; charset=utf-8" : "application/json; charset=utf-8",
        "cache-control": "no-store",
        ...cabecalhos,
      });
      res.end(texto);
      const ms = Number(process.hrtime.bigint() - inicio) / 1e6;
      // Log estruturado em JSON: é o que qualquer coletor de log entende sem parser próprio.
      console.log(JSON.stringify({
        nivel: status >= 500 ? "erro" : "info",
        metodo: req.method, caminho, status, ms: Number(ms.toFixed(1)),
      }));
    };

    // CORS: a origem permitida vem da configuração, nunca "*" com credenciais.
    if (config.corsOrigem) {
      res.setHeader("access-control-allow-origin", config.corsOrigem);
      res.setHeader("vary", "origin");
    }
    if (req.method === "OPTIONS") {
      res.setHeader("access-control-allow-methods", "GET,POST,OPTIONS");
      res.setHeader("access-control-allow-headers", "content-type");
      return responder(204, "");
    }

    try {
      // ---- Saúde -------------------------------------------------------
      if (caminho === "/health" && req.method === "GET") {
        const s = await servico.saude();
        return responder(s.ok ? 200 : 503, s);
      }

      // ---- Frontend ----------------------------------------------------
      if ((caminho === "/" || caminho === "/index.html") && req.method === "GET") {
        const html = await readFile(INDEX, "utf8");
        return responder(200, html, { "cache-control": "public, max-age=60" });
      }

      // ---- API: criar --------------------------------------------------
      if (caminho === "/api/links" && req.method === "POST") {
        const corpo = await lerJson(req);
        const link = await servico.criarLink({
          destino: corpo.destino,
          slug: corpo.slug,
          ip: ipDoCliente(req),
        });
        return responder(201, link, { location: link.url_curta });
      }

      // ---- API: detalhe ------------------------------------------------
      const m = caminho.match(/^\/api\/links\/([^/]+)$/);
      if (m && req.method === "GET") {
        return responder(200, await servico.detalhe(decodeURIComponent(m[1])));
      }

      // ---- API: estatísticas -------------------------------------------
      if (caminho === "/api/stats" && req.method === "GET") {
        return responder(200, await servico.estatisticas());
      }

      // ---- Redirecionamento (o caminho quente) -------------------------
      const slug = caminho.slice(1);
      if (req.method === "GET" && slug && !slug.includes("/")) {
        const { destino } = await servico.resolver(slug);
        // 302 e não 301: 301 é cacheado pelo navegador PARA SEMPRE, e você perde
        // a métrica e a capacidade de mudar o destino. Erro clássico de encurtador.
        return responder(302, "", { location: destino, "cache-control": "no-store" });
      }

      return responder(404, { erro: "rota não encontrada", codigo: "nao_encontrado" });
    } catch (e) {
      if (e instanceof ErroDominio) {
        const cabecalhos = e.retryAfter ? { "retry-after": String(e.retryAfter) } : {};
        return responder(e.status, { erro: e.message, codigo: e.codigo }, cabecalhos);
      }
      // Erro inesperado: loga o detalhe, devolve mensagem genérica.
      // Vazar stack trace para o cliente é entregar o mapa da casa.
      console.error(JSON.stringify({ nivel: "erro", msg: e.message, stack: e.stack }));
      return responder(500, { erro: "erro interno", codigo: "interno" });
    }
  };
}

const LIMITE_CORPO = 16 * 1024;   // 16 KB. Sem limite, um POST gigante derruba o processo.

function lerJson(req) {
  return new Promise((resolve, reject) => {
    let bruto = "";
    req.on("data", (parte) => {
      bruto += parte;
      if (bruto.length > LIMITE_CORPO) {
        reject(new ErroDominio("corpo_grande", "corpo da requisição excede 16 KB", 413));
        req.destroy();
      }
    });
    req.on("end", () => {
      if (!bruto) return resolve({});
      try { resolve(JSON.parse(bruto)); }
      catch { reject(new ErroDominio("json_invalido", "corpo não é JSON válido", 400)); }
    });
    req.on("error", reject);
  });
}

/**
 * IP do cliente. Só confie no cabeçalho que o SEU proxy escreve.
 * `x-forwarded-for` vindo da internet aberta é forjável — e é assim que se burla
 * um limitador de taxa mal feito.
 */
export function ipDoCliente(req) {
  return req.headers["cf-connecting-ip"]
      ?? req.headers["fly-client-ip"]
      ?? req.headers["x-forwarded-for"]?.split(",")[0]?.trim()
      ?? req.socket?.remoteAddress
      ?? "desconhecido";
}
