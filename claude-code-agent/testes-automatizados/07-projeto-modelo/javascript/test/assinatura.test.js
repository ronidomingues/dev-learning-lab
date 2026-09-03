/**
 * Máquina de estados — espelho de `tests/test_assinatura.py`.
 *
 * O padrão da tabela de transições é idêntico ao do Python. A diferença é que
 * `node:test` não tem `parametrize`: geramos os `it()` num laço. Funciona igual
 * e é até mais flexível; o que se perde é o relatório com `ids` bonitos que o
 * pytest dá de graça.
 */

import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { Assinatura, Estado, MAX_TENTATIVAS, TransicaoInvalida } from '../src/assinatura.js';
import { CATALOGO } from '../src/plano.js';

const HOJE = '2026-08-12';

/** Object mother: cria uma assinatura com os campos que o teste precisa. */
function nova(estado = Estado.ATIVA, extras = {}) {
  const a = Assinatura.criar('a1', 'ana@exemplo.br', CATALOGO.pro, HOJE);
  a.estado = estado;
  return Object.assign(a, extras);
}

describe('criação', () => {
  it('começa ativa', () => {
    assert.equal(nova().estado, Estado.ATIVA);
  });

  it('primeira cobrança é um ciclo à frente', () => {
    assert.equal(Assinatura.criar('a1', 'a@x', CATALOGO.pro, HOJE).proximaCobranca, '2026-09-11');
  });

  it('plano anual cobra em 365 dias', () => {
    assert.equal(Assinatura.criar('a1', 'a@x', CATALOGO.anual, HOJE).proximaCobranca, '2027-08-12');
  });

  it('nasce sem ciclos pagos', () => {
    assert.equal(nova().ciclosPagos, 0);
  });

  it('não compartilha o array de histórico entre instâncias', () => {
    // Bug clássico de JavaScript: `historico = []` como valor padrão de
    // parâmetro é criado a cada chamada (ok), mas se fosse propriedade de
    // protótipo ou default de objeto reaproveitado, TODAS as assinaturas
    // compartilhariam a mesma lista. O `[...historico]` no construtor garante
    // a cópia — e este teste é o que impede a "otimização" de removê-lo.
    const a = nova();
    const b = nova();
    a.pausar();
    assert.deepEqual(b.historico, []);
  });
});

// ---------------------------------------------------------------------------
// Tabela de transições: [estado inicial, ação, estado final ou null se proibida]
// ---------------------------------------------------------------------------
const ACOES = {
  pausar: (a) => a.pausar(),
  retomar: (a) => a.retomar(HOJE),
  cancelar: (a) => a.cancelar(),
  pagar: (a) => a.registrarPagamento(HOJE),
  falhar: (a) => a.registrarFalha(),
};

const TABELA = [
  [Estado.ATIVA, 'pausar', Estado.PAUSADA],
  [Estado.ATIVA, 'retomar', null],
  [Estado.ATIVA, 'cancelar', Estado.CANCELADA],
  [Estado.ATIVA, 'pagar', Estado.ATIVA],
  [Estado.ATIVA, 'falhar', Estado.INADIMPLENTE],
  [Estado.PAUSADA, 'pausar', null],
  [Estado.PAUSADA, 'retomar', Estado.ATIVA],
  [Estado.PAUSADA, 'cancelar', Estado.CANCELADA],
  [Estado.PAUSADA, 'pagar', null],
  [Estado.PAUSADA, 'falhar', null],
  [Estado.INADIMPLENTE, 'pausar', null],
  [Estado.INADIMPLENTE, 'retomar', null],
  [Estado.INADIMPLENTE, 'cancelar', Estado.CANCELADA],
  [Estado.INADIMPLENTE, 'pagar', Estado.ATIVA],
  [Estado.INADIMPLENTE, 'falhar', Estado.INADIMPLENTE],
  [Estado.CANCELADA, 'pausar', null],
  [Estado.CANCELADA, 'retomar', null],
  [Estado.CANCELADA, 'cancelar', null],
  [Estado.CANCELADA, 'pagar', null],
  [Estado.CANCELADA, 'falhar', null],
];

describe('tabela de transições', () => {
  for (const [inicial, acao, final] of TABELA) {
    it(`${inicial} + ${acao} → ${final ?? 'PROIBIDO'}`, () => {
      const a = nova(inicial);
      if (final === null) {
        assert.throws(() => ACOES[acao](a), TransicaoInvalida);
        assert.equal(a.estado, inicial, 'transição proibida não pode mudar o estado');
      } else {
        ACOES[acao](a);
        assert.equal(a.estado, final);
      }
    });
  }

  it('a tabela cobre todas as combinações (meta-teste)', () => {
    const esperado = Object.values(Estado)
      .flatMap((e) => Object.keys(ACOES).map((a) => `${e}|${a}`))
      .sort();
    const coberto = TABELA.map(([e, a]) => `${e}|${a}`).sort();
    assert.deepEqual(coberto, esperado);
  });
});

describe('vencimento', () => {
  const casos = [
    ['2026-08-11', false, 'dia antes'],
    ['2026-08-12', true, 'no dia, inclusive'],
    ['2026-08-13', true, 'dia depois'],
  ];

  for (const [hoje, vencida, rotulo] of casos) {
    it(`fronteira: ${rotulo}`, () => {
      const a = nova(Estado.ATIVA, { proximaCobranca: '2026-08-12' });
      assert.equal(a.estaVencida(hoje), vencida);
    });
  }

  for (const estado of [Estado.PAUSADA, Estado.CANCELADA]) {
    it(`${estado} nunca vence`, () => {
      const a = nova(estado, { proximaCobranca: '2020-01-01' });
      assert.equal(a.estaVencida(HOJE), false);
    });
  }

  it('inadimplente continua vencendo para ser retentada', () => {
    const a = nova(Estado.INADIMPLENTE, { proximaCobranca: HOJE });
    assert.equal(a.estaVencida(HOJE), true);
  });
});

describe('pagamento', () => {
  it('empurra o vencimento um ciclo', () => {
    const a = nova(Estado.ATIVA, { proximaCobranca: HOJE });
    a.registrarPagamento(HOJE);
    assert.equal(a.proximaCobranca, '2026-09-11');
  });

  it('conta o ciclo', () => {
    const a = nova();
    a.registrarPagamento(HOJE);
    a.registrarPagamento(HOJE);
    assert.equal(a.ciclosPagos, 2);
  });

  it('zera as tentativas de falha', () => {
    const a = nova(Estado.INADIMPLENTE, { tentativasFalhas: 2 });
    a.registrarPagamento(HOJE);
    assert.equal(a.tentativasFalhas, 0);
    assert.equal(a.estado, Estado.ATIVA);
  });

  it('o novo vencimento conta do dia do pagamento, não do vencimento antigo', () => {
    const a = nova(Estado.ATIVA, { proximaCobranca: HOJE });
    a.registrarPagamento('2026-08-17');
    assert.equal(a.proximaCobranca, '2026-09-16');
  });
});

describe('inadimplência', () => {
  it('primeira falha deixa inadimplente', () => {
    const a = nova();
    a.registrarFalha();
    assert.equal(a.estado, Estado.INADIMPLENTE);
    assert.equal(a.tentativasFalhas, 1);
  });

  it('cancela na terceira falha', () => {
    const a = nova();
    for (let i = 0; i < MAX_TENTATIVAS; i += 1) a.registrarFalha();
    assert.equal(a.estado, Estado.CANCELADA);
  });

  it('não cancela na segunda', () => {
    const a = nova();
    for (let i = 0; i < MAX_TENTATIVAS - 1; i += 1) a.registrarFalha();
    assert.equal(a.estado, Estado.INADIMPLENTE);
  });

  it('o histórico registra o motivo do cancelamento', () => {
    const a = nova();
    for (let i = 0; i < MAX_TENTATIVAS; i += 1) a.registrarFalha();
    assert.equal(a.historico.at(-1), 'cancelada por inadimplência');
  });
});

describe('pausa', () => {
  it('retomar reinicia o ciclo do dia da retomada', () => {
    const a = nova(Estado.ATIVA, { proximaCobranca: '2026-08-14' });
    a.pausar();
    a.retomar('2026-11-20');
    assert.equal(a.proximaCobranca, '2026-12-20');
  });

  it('cliente não paga pelo tempo pausado', () => {
    const a = nova(Estado.ATIVA, { proximaCobranca: HOJE });
    a.pausar();
    a.retomar('2027-08-12');
    assert.equal(a.ciclosPagos, 0);
  });
});

describe('invariantes sob sequências aleatórias', () => {
  // Não é property-based testing de verdade (sem shrinking), mas é o que se
  // consegue sem dependência: 500 sequências pseudoaleatórias com semente fixa,
  // para o teste ser determinístico. Ver test/propriedades.test.js para a
  // versão com fast-check.
  function aleatorioComSemente(semente) {
    let estado = semente;
    return () => {
      estado = (estado * 1103515245 + 12345) & 0x7fffffff;
      return estado / 0x7fffffff;
    };
  }

  it('nenhuma sequência de ações produz estado incoerente', () => {
    const rnd = aleatorioComSemente(42);
    const nomes = Object.keys(ACOES);

    for (let caso = 0; caso < 500; caso += 1) {
      const a = Assinatura.criar('a1', 'ana@x', CATALOGO.pro, HOJE);
      const quantas = Math.floor(rnd() * 25);
      for (let i = 0; i < quantas; i += 1) {
        const acao = nomes[Math.floor(rnd() * nomes.length)];
        try {
          ACOES[acao](a);
        } catch (erro) {
          if (!(erro instanceof TransicaoInvalida)) throw erro;
        }
      }
      assert.ok(Object.values(Estado).includes(a.estado));
      assert.ok(a.tentativasFalhas >= 0 && a.tentativasFalhas <= MAX_TENTATIVAS);
      assert.ok(a.ciclosPagos >= 0);
      assert.ok(a.proximaCobranca >= a.inicio);
      if (a.estado === Estado.ATIVA) assert.equal(a.tentativasFalhas, 0);
    }
  });

  it('cancelamento é absorvente', () => {
    const a = nova();
    a.cancelar();
    for (const acao of Object.values(ACOES)) {
      assert.throws(() => acao(a), TransicaoInvalida);
    }
    assert.equal(a.estado, Estado.CANCELADA);
  });
});
