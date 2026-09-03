/**
 * Testes de comportamento HTTP.
 *
 * Cada teste sobe uma instância própria em porta efêmera (porta 0 = o sistema
 * escolhe uma livre). Isso torna os testes independentes e paralelizáveis, e
 * evita que o rate limit de um teste derrube outro.
 */
import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { criarApp } from '../src/servidor.js';

const LEITOR = 'tok_leitor_demo';
const BIBLIO = 'tok_biblio_demo';

/** Sobe uma instância isolada e devolve um cliente pronto. */
async function comApp(opcoes = {}) {
  const app = criarApp({ semear: true, ...opcoes });
  await new Promise(r => app.listen(0, '127.0.0.1', r));
  const base = `http://127.0.0.1:${app.address().port}`;

  const chamar = (caminho, { token = BIBLIO, chaveIdem, ...init } = {}) => {
    const headers = { ...init.headers };
    if (token) headers.Authorization = `Bearer ${token}`;
    if (init.body && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
    if (chaveIdem) headers['Idempotency-Key'] = chaveIdem;
    return fetch(base + caminho, { ...init, headers });
  };

  return {
    base, chamar, app,
    async fechar() { app.parar(); await new Promise(r => app.close(r)); }
  };
}

const uuid = () => crypto.randomUUID();

// ============================ saúde e contrato ============================

describe('saúde e contrato', () => {
  test('GET /health responde sem autenticação', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/health', { token: null });
      assert.equal(r.status, 200);
      const corpo = await r.json();
      assert.equal(corpo.status, 'ok');
      assert.equal(typeof corpo.uptime_s, 'number');
    } finally { await t.fechar(); }
  });

  test('GET /health/pronto informa o estado das dependências', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/health/pronto', { token: null });
      assert.equal(r.status, 200);
      assert.equal((await r.json()).status, 'pronto');
    } finally { await t.fechar(); }
  });

  test('o contrato lista todas as rotas implementadas', async () => {
    const t = await comApp();
    try {
      const contrato = await (await t.chamar('/openapi.json', { token: null })).json();
      const declaradas = new Set();
      for (const [caminho, metodos] of Object.entries(contrato.paths)) {
        for (const m of Object.keys(metodos)) declaradas.add(`${m.toUpperCase()} ${caminho}`);
      }
      for (const { metodo, padrao } of t.app.rotas.listar()) {
        const chave = `${metodo} ${padrao.replace(/:([A-Za-z_]\w*)/g, '{$1}')}`;
        assert.ok(declaradas.has(chave), `rota ${chave} não está no contrato`);
      }
    } finally { await t.fechar(); }
  });

  test('toda resposta carrega X-Request-Id', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/health', { token: null });
      assert.match(r.headers.get('x-request-id') ?? '', /^[0-9a-f-]{36}$/);
    } finally { await t.fechar(); }
  });

  test('o X-Request-Id do cliente é preservado (correlação entre serviços)', async () => {
    const t = await comApp();
    try {
      const meu = 'meu-id-de-correlacao-123';
      const r = await t.chamar('/health', { token: null, headers: { 'X-Request-Id': meu } });
      assert.equal(r.headers.get('x-request-id'), meu);
    } finally { await t.fechar(); }
  });
});

// ============================ autenticação ============================

describe('autenticação e autorização', () => {
  test('sem token → 401 com WWW-Authenticate', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros', { token: null });
      assert.equal(r.status, 401);
      assert.match(r.headers.get('www-authenticate') ?? '', /Bearer/);
      assert.match(r.headers.get('content-type') ?? '', /application\/problem\+json/);
      const corpo = await r.json();
      assert.equal(corpo.status, 401);
      assert.ok(corpo.type.includes('nao-autenticado'));
    } finally { await t.fechar(); }
  });

  test('token inexistente → 401 invalid_token', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros', { token: 'tok_inventado_por_atacante' });
      assert.equal(r.status, 401);
      assert.match(r.headers.get('www-authenticate') ?? '', /invalid_token/);
    } finally { await t.fechar(); }
  });

  test('esquema errado (Basic) → 401', async () => {
    const t = await comApp();
    try {
      const r = await fetch(`${t.base}/livros`, { headers: { Authorization: 'Basic YWJjOjEyMw==' } });
      assert.equal(r.status, 401);
    } finally { await t.fechar(); }
  });

  test('token válido sem o escopo → 403, não 401', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros', {
        token: LEITOR, method: 'POST', chaveIdem: uuid(),
        body: JSON.stringify({ titulo: 'X', autor: 'Y' })
      });
      assert.equal(r.status, 403);
      const corpo = await r.json();
      assert.equal(corpo.escopo_necessario, 'livros:escrever');
      assert.match(r.headers.get('www-authenticate') ?? '', /insufficient_scope/);
    } finally { await t.fechar(); }
  });
});

// ============================ leitura ============================

describe('leitura de livros', () => {
  test('GET /livros devolve dados e paginação', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros?limite=2');
      assert.equal(r.status, 200);
      const corpo = await r.json();
      assert.equal(corpo.dados.length, 2);
      assert.ok(corpo.paginacao.proximo_cursor, 'deveria haver cursor para a próxima página');
      assert.equal(corpo.paginacao.limite, 2);
    } finally { await t.fechar(); }
  });

  test('a paginação por cursor percorre tudo sem repetir', async () => {
    const t = await comApp();
    try {
      const vistos = new Set();
      let cursorAtual = null;
      for (let i = 0; i < 20; i++) {
        const url = `/livros?limite=2${cursorAtual ? `&cursor=${cursorAtual}` : ''}`;
        const corpo = await (await t.chamar(url)).json();
        for (const l of corpo.dados) {
          assert.ok(!vistos.has(l.id), `item ${l.id} apareceu duas vezes`);
          vistos.add(l.id);
        }
        cursorAtual = corpo.paginacao.proximo_cursor;
        if (!cursorAtual) break;
      }
      assert.equal(vistos.size, 5);
    } finally { await t.fechar(); }
  });

  test('cursor inválido → 400, não 500', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros?cursor=%21%21%21%21');
      assert.equal(r.status, 400);
    } finally { await t.fechar(); }
  });

  test('limite fora da faixa → 400 informando o parâmetro', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros?limite=9999');
      assert.equal(r.status, 400);
      assert.equal((await r.json()).parametro, 'limite');
    } finally { await t.fechar(); }
  });

  test('filtro por autor', async () => {
    const t = await comApp();
    try {
      const corpo = await (await t.chamar('/livros?autor=Machado')).json();
      assert.equal(corpo.dados.length, 1);
      assert.match(corpo.dados[0].autor, /Machado/);
    } finally { await t.fechar(); }
  });

  test('GET /livros/{id} inexistente → 404 em problem+json', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros/nao-existe');
      assert.equal(r.status, 404);
      assert.match(r.headers.get('content-type') ?? '', /application\/problem\+json/);
      const corpo = await r.json();
      assert.ok(corpo.instance.startsWith('/requisicoes/'));
    } finally { await t.fechar(); }
  });
});

// ============================ cache ============================

describe('cache condicional', () => {
  test('ETag + If-None-Match devolve 304 sem corpo', async () => {
    const t = await comApp();
    try {
      const lista = await (await t.chamar('/livros?limite=1')).json();
      const id = lista.dados[0].id;

      const primeira = await t.chamar(`/livros/${id}`);
      const etag = primeira.headers.get('etag');
      assert.ok(etag, 'a resposta deveria trazer ETag');
      assert.match(primeira.headers.get('cache-control') ?? '', /private/);

      const segunda = await t.chamar(`/livros/${id}`, { headers: { 'If-None-Match': etag } });
      assert.equal(segunda.status, 304);
      assert.equal(await segunda.text(), '');
    } finally { await t.fechar(); }
  });

  test('resposta cacheável de coleção não vaza entre identidades (Vary)', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros');
      // Ou é no-store, ou declara Vary: Authorization. Nunca cacheável sem Vary.
      const cc = r.headers.get('cache-control') ?? '';
      const vary = r.headers.get('vary') ?? '';
      assert.ok(cc.includes('no-store') || vary.includes('Authorization'),
        `resposta cacheável sem Vary: Authorization (cc="${cc}", vary="${vary}")`);
    } finally { await t.fechar(); }
  });
});

// ============================ criação ============================

describe('criação de livros', () => {
  const novo = () => ({ titulo: 'Iracema', autor: 'José de Alencar', ano: 1865 });

  test('POST válido → 201 com Location e ETag', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros', {
        method: 'POST', chaveIdem: uuid(), body: JSON.stringify(novo())
      });
      assert.equal(r.status, 201);
      const corpo = await r.json();
      assert.equal(r.headers.get('location'), `/livros/${corpo.id}`);
      assert.ok(r.headers.get('etag'));
      assert.equal(corpo.disponivel, true);
      assert.equal(corpo.versao, 1);
    } finally { await t.fechar(); }
  });

  test('POST sem Idempotency-Key → 400', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros', { method: 'POST', body: JSON.stringify(novo()) });
      assert.equal(r.status, 400);
      assert.ok((await r.json()).type.includes('chave-idempotencia-ausente'));
    } finally { await t.fechar(); }
  });

  test('a MESMA Idempotency-Key não duplica e devolve a resposta original', async () => {
    const t = await comApp();
    try {
      const chave = uuid();
      const corpo = JSON.stringify(novo());

      const r1 = await t.chamar('/livros', { method: 'POST', chaveIdem: chave, body: corpo });
      const r2 = await t.chamar('/livros', { method: 'POST', chaveIdem: chave, body: corpo });

      const a = await r1.json(), b = await r2.json();
      assert.equal(r1.status, 201);
      assert.equal(r2.status, 201);
      assert.equal(a.id, b.id, 'deveria devolver o MESMO recurso');
      assert.equal(r2.headers.get('idempotency-replayed'), 'true');

      const total = (await (await t.chamar('/livros?limite=100')).json()).paginacao.total;
      assert.equal(total, 6, 'deveria ter criado apenas UM livro novo');
    } finally { await t.fechar(); }
  });

  test('mesma chave com corpo diferente → 422', async () => {
    const t = await comApp();
    try {
      const chave = uuid();
      await t.chamar('/livros', { method: 'POST', chaveIdem: chave, body: JSON.stringify(novo()) });
      const r = await t.chamar('/livros', {
        method: 'POST', chaveIdem: chave,
        body: JSON.stringify({ titulo: 'Outro', autor: 'Outro' })
      });
      assert.equal(r.status, 422);
      assert.ok((await r.json()).type.includes('chave-idempotencia-reusada'));
    } finally { await t.fechar(); }
  });

  test('validação falha → 422 listando os campos', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros', {
        method: 'POST', chaveIdem: uuid(),
        body: JSON.stringify({ titulo: '', ano: 3000, preco: 10 })
      });
      assert.equal(r.status, 422);
      const corpo = await r.json();
      const campos = corpo.erros.map(e => e.campo);
      assert.ok(campos.includes('autor'));
      assert.ok(campos.includes('titulo'));
      assert.ok(campos.includes('ano'));
      assert.ok(campos.includes('preco'), 'campo desconhecido deveria ser recusado');
    } finally { await t.fechar(); }
  });

  test('JSON malformado → 400 (e não 500)', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros', {
        method: 'POST', chaveIdem: uuid(),
        headers: { 'Content-Type': 'application/json' },
        body: '{"titulo": '
      });
      assert.equal(r.status, 400);
      assert.ok((await r.json()).type.includes('json-invalido'));
    } finally { await t.fechar(); }
  });

  test('Content-Type errado → 415', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros', {
        method: 'POST', chaveIdem: uuid(),
        headers: { 'Content-Type': 'text/plain' },
        body: 'titulo=x'
      });
      assert.equal(r.status, 415);
    } finally { await t.fechar(); }
  });

  test('ISBN duplicado → 409', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros', {
        method: 'POST', chaveIdem: uuid(),
        body: JSON.stringify({ titulo: 'Cópia', autor: 'Alguém', isbn: '9788572326972' })
      });
      assert.equal(r.status, 409);
      assert.ok((await r.json()).type.includes('isbn-duplicado'));
    } finally { await t.fechar(); }
  });

  test('corpo grande demais → 413', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros', {
        method: 'POST', chaveIdem: uuid(),
        body: JSON.stringify({ titulo: 'x'.repeat(300_000), autor: 'y' })
      });
      assert.equal(r.status, 413);
    } finally { await t.fechar(); }
  });
});

// ============================ concorrência ============================

describe('concorrência otimista', () => {
  async function primeiroLivro(t) {
    const lista = await (await t.chamar('/livros?limite=1')).json();
    const id = lista.dados[0].id;
    const r = await t.chamar(`/livros/${id}`);
    return { id, etag: r.headers.get('etag') };
  }

  test('PATCH sem If-Match → 428', async () => {
    const t = await comApp();
    try {
      const { id } = await primeiroLivro(t);
      const r = await t.chamar(`/livros/${id}`, { method: 'PATCH', body: JSON.stringify({ ano: 1900 }) });
      assert.equal(r.status, 428);
    } finally { await t.fechar(); }
  });

  test('PATCH com If-Match correto → 200 e novo ETag', async () => {
    const t = await comApp();
    try {
      const { id, etag } = await primeiroLivro(t);
      const r = await t.chamar(`/livros/${id}`, {
        method: 'PATCH', headers: { 'If-Match': etag }, body: JSON.stringify({ ano: 1900 })
      });
      assert.equal(r.status, 200);
      const corpo = await r.json();
      assert.equal(corpo.ano, 1900);
      assert.equal(corpo.versao, 2);
      assert.notEqual(r.headers.get('etag'), etag, 'o ETag precisa mudar');
    } finally { await t.fechar(); }
  });

  test('segunda escrita com ETag velho → 412 (lost update evitado)', async () => {
    const t = await comApp();
    try {
      const { id, etag } = await primeiroLivro(t);
      // Ana escreve
      await t.chamar(`/livros/${id}`, {
        method: 'PATCH', headers: { 'If-Match': etag }, body: JSON.stringify({ ano: 1900 })
      });
      // Bruno escreve com o ETag que leu ANTES
      const r = await t.chamar(`/livros/${id}`, {
        method: 'PATCH', headers: { 'If-Match': etag }, body: JSON.stringify({ ano: 2000 })
      });
      assert.equal(r.status, 412);
      assert.ok((await r.json()).etag_atual, 'deveria informar o ETag atual');

      const atual = await (await t.chamar(`/livros/${id}`)).json();
      assert.equal(atual.ano, 1900, 'a alteração de Ana não pode ter sido perdida');
    } finally { await t.fechar(); }
  });
});

// ============================ empréstimos ============================

describe('empréstimos', () => {
  async function idDoPrimeiro(t) {
    return (await (await t.chamar('/livros?limite=1')).json()).dados[0].id;
  }

  test('emprestar torna o livro indisponível', async () => {
    const t = await comApp();
    try {
      const livroId = await idDoPrimeiro(t);
      const r = await t.chamar('/emprestimos', {
        method: 'POST', chaveIdem: uuid(),
        body: JSON.stringify({ livro_id: livroId, pessoa: 'Ana' })
      });
      assert.equal(r.status, 201);
      const emprestimo = await r.json();
      assert.equal(emprestimo.devolvido_em, null);

      const livro = await (await t.chamar(`/livros/${livroId}`)).json();
      assert.equal(livro.disponivel, false);
    } finally { await t.fechar(); }
  });

  test('emprestar duas vezes → 409 (conflito de estado, não 422)', async () => {
    const t = await comApp();
    try {
      const livroId = await idDoPrimeiro(t);
      await t.chamar('/emprestimos', {
        method: 'POST', chaveIdem: uuid(),
        body: JSON.stringify({ livro_id: livroId, pessoa: 'Ana' })
      });
      const r = await t.chamar('/emprestimos', {
        method: 'POST', chaveIdem: uuid(),
        body: JSON.stringify({ livro_id: livroId, pessoa: 'Bruno' })
      });
      assert.equal(r.status, 409);
      assert.ok((await r.json()).type.includes('livro-indisponivel'));
    } finally { await t.fechar(); }
  });

  test('devolver libera o livro, e devolver de novo é idempotente', async () => {
    const t = await comApp();
    try {
      const livroId = await idDoPrimeiro(t);
      const emp = await (await t.chamar('/emprestimos', {
        method: 'POST', chaveIdem: uuid(),
        body: JSON.stringify({ livro_id: livroId, pessoa: 'Ana' })
      })).json();

      const d1 = await t.chamar(`/emprestimos/${emp.id}/devolucao`, { method: 'POST' });
      assert.equal(d1.status, 200);
      assert.ok((await d1.json()).devolvido_em);

      const d2 = await t.chamar(`/emprestimos/${emp.id}/devolucao`, { method: 'POST' });
      assert.equal(d2.status, 200, 'devolver duas vezes não é erro');
      assert.equal(d2.headers.get('idempotency-replayed'), 'true');

      const livro = await (await t.chamar(`/livros/${livroId}`)).json();
      assert.equal(livro.disponivel, true);
    } finally { await t.fechar(); }
  });

  test('emprestar livro inexistente → 404', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/emprestimos', {
        method: 'POST', chaveIdem: uuid(),
        body: JSON.stringify({ livro_id: '00000000-0000-4000-8000-000000000000', pessoa: 'Ana' })
      });
      assert.equal(r.status, 404);
    } finally { await t.fechar(); }
  });
});

// ============================ protocolo ============================

describe('conformidade com HTTP', () => {
  test('método não permitido → 405 com Allow', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros', { method: 'DELETE' });
      assert.equal(r.status, 405);
      const allow = r.headers.get('allow') ?? '';
      assert.ok(allow.includes('GET') && allow.includes('POST'), `Allow inesperado: ${allow}`);
    } finally { await t.fechar(); }
  });

  test('HEAD devolve os mesmos cabeçalhos do GET, sem corpo (RFC 9110)', async () => {
    const t = await comApp();
    try {
      const lista = await (await t.chamar('/livros?limite=1')).json();
      const id = lista.dados[0].id;

      const get = await t.chamar(`/livros/${id}`);
      const head = await t.chamar(`/livros/${id}`, { method: 'HEAD' });

      assert.equal(head.status, 200, 'HEAD não pode devolver 405');
      assert.equal(head.headers.get('etag'), get.headers.get('etag'));
      assert.equal(head.headers.get('content-length'), get.headers.get('content-length'));
      assert.equal(await head.text(), '', 'HEAD não pode ter corpo');
    } finally { await t.fechar(); }
  });

  test('OPTIONS anuncia HEAD junto com GET', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros', { method: 'OPTIONS', token: null });
      const allow = r.headers.get('allow') ?? '';
      assert.ok(allow.includes('GET') && allow.includes('HEAD'), `Allow: ${allow}`);
    } finally { await t.fechar(); }
  });

  test('OPTIONS responde 204 com Allow, sem exigir token', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros', { method: 'OPTIONS', token: null });
      assert.equal(r.status, 204);
      assert.match(r.headers.get('allow') ?? '', /OPTIONS/);
    } finally { await t.fechar(); }
  });

  test('Accept incompatível → 406', async () => {
    const t = await comApp();
    try {
      const r = await t.chamar('/livros', { headers: { Accept: 'application/xml' } });
      assert.equal(r.status, 406);
    } finally { await t.fechar(); }
  });

  test('rota inexistente → 404', async () => {
    const t = await comApp();
    try {
      assert.equal((await t.chamar('/nao-existe')).status, 404);
    } finally { await t.fechar(); }
  });

  test('rate limit: estoura com 429, Retry-After e cabeçalhos de cota', async () => {
    const t = await comApp({ limiteRate: 5, janelaRateMs: 60_000 });
    try {
      let ultima;
      for (let i = 0; i < 7; i++) ultima = await t.chamar('/livros');

      assert.equal(ultima.status, 429);
      assert.ok(Number(ultima.headers.get('retry-after')) > 0);
      assert.equal(ultima.headers.get('x-ratelimit-limit'), '5');
      const corpo = await ultima.json();
      assert.equal(corpo.limite, 5);
    } finally { await t.fechar(); }
  });

  test('o rate limit é por identidade, não global', async () => {
    const t = await comApp({ limiteRate: 3, janelaRateMs: 60_000 });
    try {
      for (let i = 0; i < 4; i++) await t.chamar('/livros', { token: BIBLIO });
      // O leitor tem cota própria e continua passando.
      const r = await t.chamar('/livros', { token: LEITOR });
      assert.equal(r.status, 200);
    } finally { await t.fechar(); }
  });

  test('nenhuma resposta de erro vaza stack trace', async () => {
    const t = await comApp();
    try {
      for (const caminho of ['/nao-existe', '/livros/xyz', '/livros?limite=0']) {
        const texto = await (await t.chamar(caminho)).text();
        assert.ok(!/\bat \/|node_modules|\.js:\d+:\d+/.test(texto),
          `resposta de ${caminho} parece conter stack trace`);
      }
    } finally { await t.fechar(); }
  });
});
