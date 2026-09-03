// Demonstração visual do lost update, lado a lado.
//
//   node test/demo-corrida.js inseguro   -> mostra escritas evaporando
//   node test/demo-corrida.js seguro     -> mostra a versão salvando tudo
//
// Os dois rodam a MESMA carga: N clientes leem o mesmo registro, acrescentam a
// própria marca à descrição e gravam. A única diferença é a guarda no UPDATE.

import { abrirBanco, semear } from '../src/db.js';
import { criarServidor } from '../src/server.js';
import { criarCliente } from '../src/cliente.js';

const modo = process.argv[2] ?? 'seguro';
const N = Number(process.argv[3] ?? 20);

const db = abrirBanco(':memory:');
semear(db);
const servidor = criarServidor(db);
await new Promise((r) => servidor.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${servidor.address().port}`;
const cliente = criarCliente(base);

const inicial = (await cliente.obter(1)).produto.descricao;
const t0 = process.hrtime.bigint();

let tentativas = N;
if (modo === 'inseguro') {
  await Promise.all(
    Array.from({ length: N }, (_, i) =>
      cliente.editarSemProtecao(1, (p) => ({ descricao: `${p.descricao}|${i}` }))
    )
  );
} else {
  const rs = await Promise.all(
    Array.from({ length: N }, (_, i) =>
      cliente.editar(1, (p) => ({ descricao: `${p.descricao}|${i}` }), {
        autor: `cli${i}`,
        tentativas: 100,
        baseMs: 1,
      })
    )
  );
  tentativas = rs.reduce((s, r) => s + r.tentativasGastas, 0);
}

const msTotal = Number(process.hrtime.bigint() - t0) / 1e6;
const fim = (await cliente.obter(1)).produto;
const marcas = fim.descricao.slice(inicial.length).split('|').filter(Boolean);

console.log(`\nmodo .................. ${modo}`);
console.log(`clientes .............. ${N}`);
console.log(`edições sobreviventes . ${marcas.length} de ${N}`);
console.log(`edições PERDIDAS ...... ${N - marcas.length}`);
console.log(`versão final .......... ${fim.version}`);
console.log(`escritas HTTP gastas .. ${tentativas} (${(tentativas / N).toFixed(2)}x por edição)`);
console.log(`tempo ................. ${msTotal.toFixed(1)} ms`);
console.log(
  marcas.length === N
    ? '\nResultado: nada se perdeu. O preço foi a retentativa.\n'
    : `\nResultado: ${N - marcas.length} edições sumiram sem erro nenhum. Ninguém foi avisado.\n`
);

servidor.close();
