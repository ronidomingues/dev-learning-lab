# 17 · JavaScript a fundo — `node:test`, Vitest e Jest

`Nível: intermediário → avançado` · `Base: Node 24.18 · Vitest 4.1.10 · Jest 30.4.2` · `13/08/2026`

Este arquivo responde à pergunta *"como fazer testes em JavaScript?"* — incluindo a decisão
que mais consome tempo de quem começa: **qual corredor usar**.

---

## 1. A decisão: qual corredor?

### 1.1 Tabela de decisão

| Seu caso | Escolha |
|---|---|
| biblioteca ou serviço Node, sem front-end | **`node:test`** |
| projeto novo com Vite (React, Vue, Svelte, Solid, Astro) | **Vitest** |
| Nuxt, SvelteKit, Angular moderno | **Vitest** (já vem recomendado) |
| monorepo grande já em Jest, funcionando | **Jest** — não migre sem motivo |
| React Native | **Jest** — o Vitest não tem suporte |
| precisa rodar teste no navegador de verdade | **Vitest** (*browser mode*) ou Playwright |
| CLI, script, ferramenta interna | **`node:test`** |
| TypeScript sem cadeia de compilação montada | **Vitest** |

### 1.2 Comparação honesta

| | `node:test` | Vitest 4 | Jest 30 |
|---|---|---|---|
| **instalar** | nada | 1 pacote (~44 no total) | 1 pacote (+ Babel/ts-jest se TS) |
| **arranque a frio** | mais rápido | rápido | mais lento |
| **modo watch** | sim (`--watch`) | muito rápido (HMR do Vite) | lento em base grande |
| **ESM** | nativo | nativo | estável desde o 30, mas a arquitetura é CJS-first |
| **TypeScript** | precisa de `--experimental-strip-types` ou compilar | nativo | ts-jest ou Babel |
| **asserções** | `node:assert` | `expect` | `expect` |
| **mocks** | `t.mock` | `vi` (mais rico) | `jest` (mais rico) |
| **mock de módulo** | `t.mock.module` (Stability 1.0) | `vi.mock` maduro | `jest.mock` maduro |
| **snapshots** | básico | completo, inline | completo, inline |
| **cobertura** | V8, via flag | V8 ou Istanbul | V8 ou Babel |
| **DOM** | não | jsdom/happy-dom/navegador | jsdom |
| **interface web** | não | `--ui` | não |
| **paralelismo** | por arquivo | *workers* | *workers* |
| **ecossistema** | pequeno | grande e crescendo | o maior |

**Recomendação, declarada como opinião profissional:** para código que roda **no Node**, use
`node:test` — a ausência de dependência vale mais do que qualquer conforto de API, porque
elimina uma classe inteira de problema (versões, `node_modules`, quebra na atualização). Para
código que roda **no navegador**, use Vitest. Jest permanece uma escolha razoável onde já
está e funciona; migrar por moda é desperdício.

---

## 2. `node:test` a fundo

### 2.1 Descoberta

Por padrão, `node --test` procura, recursivamente:

- arquivos `*.test.{js,mjs,cjs}` (e `.ts` com *type stripping*);
- arquivos `*-test.*` e `*_test.*`;
- arquivos chamados `test.*`;
- **tudo** dentro de um diretório chamado `test/`.

E ignora `node_modules/`. Para restringir, passe caminhos ou globs:

```bash
node --test test/unitarios/
node --test "test/**/*.integracao.test.js"
```

### 2.2 A API

```javascript
import assert from 'node:assert/strict';
import { after, afterEach, before, beforeEach, describe, it, test } from 'node:test';

// `test` e `it` são a mesma função. `describe`/`it` para quem vem de Jest;
// `test` com subtestes para quem prefere aninhar sem describe.

test('pai', async (t) => {
  await t.test('filho 1', () => {});
  await t.test('filho 2', () => {});
  // Os `await` são OBRIGATÓRIOS: sem eles, o pai termina antes dos filhos
  // e o resultado é imprevisível. É a pegadinha nº 1 de subtestes.
});

it('com opções', { skip: false, todo: false, only: false, timeout: 5000,
                   concurrency: 2, plan: 3 }, () => {});
```

`plan: 3` (Node 22.4+) declara quantas asserções o teste deve fazer — falha se fizer menos.
É o antídoto para o teste assíncrono que termina antes de verificar.

### 2.3 O objeto `t`

```javascript
it('exemplo', (t) => {
  t.diagnostic('mensagem para o relatório');   // linha ℹ, sem sujar como console.log
  t.skip('pulando no meio');
  t.todo('marcando como pendente');
  t.plan(2);
  t.mock.fn();
  t.mock.method(obj, 'm');
  t.mock.timers.enable({ apis: ['Date'] });
  t.after(() => limpar());        // limpeza deste teste específico
});
```

`t.after()` é subutilizado: limpeza local, sem precisar de `afterEach` no bloco inteiro.

### 2.4 Asserções

```javascript
import assert from 'node:assert/strict';

assert.equal(a, b);                    // === (por causa do /strict)
assert.deepStrictEqual(obj, esperado); // estrutura + tipo + protótipo
assert.ok(x);
assert.match(texto, /regex/);
assert.throws(() => f(), { name: 'RangeError', message: /negativo/ });
await assert.rejects(async () => f(), TypeError);
assert.partialDeepStrictEqual(obj, { a: 1 });   // subconjunto (Node 22.13+)
```

**Sempre `node:assert/strict`.** Sem ele, `assert.equal('1', 1)` passa.

### 2.5 As limitações reais

| Falta | Contorno |
|---|---|
| `expect` com matchers ricos | escreva funções auxiliares de asserção |
| `it.each` | laço `for` gerando `it()` |
| marcadores/tags maduros | convenção de nome de arquivo, ou `--test-name-pattern` |
| mensagem de falha rica em comparação | prefira `assert.equal(a, b)` a `assert.ok(a > b)` |
| DOM | use Vitest, ou `happy-dom` manualmente |
| mock de módulo estável | `t.mock.module` ainda é Stability 1.0 |

---

## 3. Vitest a fundo

### 3.1 Configuração comentada

```javascript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['src/**/*.{test,spec}.{js,ts}'],

    // `globals: false` é o padrão e a recomendação: importar describe/it/expect
    // explicitamente evita colisão de nomes e deixa o editor resolver os tipos.
    // Jest usa globais por herança histórica.
    globals: false,

    environment: 'node',        // 'jsdom' | 'happy-dom' | 'edge-runtime'

    setupFiles: ['./test/setup.js'],

    // 'threads' (worker_threads) é o padrão e o mais rápido.
    // 'forks' (processos) isola melhor — necessário quando o código usa
    // módulos nativos ou mexe em estado de processo.
    pool: 'threads',

    coverage: {
      provider: 'v8',            // 'istanbul' se precisar de relatório mais fiel
      include: ['src/**'],
      reporter: ['text', 'html', 'lcov'],
      thresholds: { lines: 80, branches: 75, functions: 80 },
    },

    // falha se nenhum teste casar com o filtro — evita o "CI verde com 0 testes"
    passWithNoTests: false,

    testTimeout: 5000,
    hookTimeout: 10000,
  },
});
```

### 3.2 O que o Vitest tem e o `node:test` não

```javascript
import { describe, expect, it, vi } from 'vitest';

// parametrização de primeira classe
it.each([
  [100, 10, 900],
  [1999, 10, 1799],
])('%i com %i%% vira %i', (v, p, esperado) => {
  expect(desconto(v, p)).toBe(esperado);
});

// tabela com nomes de coluna
it.each`
  conta  | percentual | esperado
  ${100} | ${10}      | ${10}
  ${200} | ${15}      | ${30}
`('$conta a $percentual% dá $esperado', ({ conta, percentual, esperado }) => {
  expect(gorjeta(conta, percentual)).toBe(esperado);
});

// asserções condicionais
describe.skipIf(process.platform === 'win32')('só em POSIX', () => {});
describe.runIf(process.env.CI)('só em CI', () => {});

// concorrência explícita
it.concurrent('a', async () => {});
it.concurrent('b', async () => {});

// asserção assíncrona que espera até passar (útil em UI)
await expect.poll(() => contador.valor).toBe(3);
await vi.waitFor(() => expect(elemento).toBeVisible());
```

### 3.3 Mocks: `vi`

```javascript
const fn = vi.fn(() => 42);
fn.mockReturnValue(1);
fn.mockReturnValueOnce(1).mockReturnValue(2);
fn.mockResolvedValue({ ok: true });
fn.mockRejectedValueOnce(new Error('boom'));
fn.mockImplementation((a) => a * 2);

expect(fn).toHaveBeenCalledTimes(2);
expect(fn).toHaveBeenCalledWith('ana', expect.any(Number));
expect(fn).toHaveBeenNthCalledWith(2, 'bruno');
expect(fn).toHaveBeenLastCalledWith('carla');
expect(fn.mock.results[0].value).toBe(84);

const espiao = vi.spyOn(objeto, 'metodo');
espiao.mockRestore();
```

**Mock de módulo — e a armadilha do içamento:**

```javascript
// ATENÇÃO: vi.mock é MOVIDO para o topo do arquivo, antes dos imports.
// Isto NÃO funciona:
const valorFalso = 42;
vi.mock('./config.js', () => ({ limite: valorFalso }));
// ReferenceError: Cannot access 'valorFalso' before initialization

// A solução:
const { valorFalso } = vi.hoisted(() => ({ valorFalso: 42 }));
vi.mock('./config.js', () => ({ limite: valorFalso }));

// Para mockar parcialmente, preservando o resto:
vi.mock('./util.js', async (importarOriginal) => {
  const original = await importarOriginal();
  return { ...original, agora: vi.fn(() => '2026-08-13') };
});
```

Limpeza:

```javascript
afterEach(() => {
  vi.clearAllMocks();    // zera contadores
  vi.resetAllMocks();    // zera contadores E implementações
  vi.restoreAllMocks();  // devolve os originais dos spyOn
  vi.useRealTimers();    // ESSENCIAL se usou fake timers
});
```

Ou, na configuração: `restoreMocks: true`, `clearMocks: true`. **Ligue.** Mock que vaza entre
arquivos é a origem clássica de "só falha quando roda a suíte inteira".

---

## 4. Jest 30: o que saber se você já está nele

Jest continua vivo e mantido. As diferenças que importam em relação ao Vitest:

| | Jest | Vitest |
|---|---|---|
| API global por padrão | sim (`describe` sem import) | não (`globals: true` opcional) |
| `jest.mock` içado | sim, pelo Babel | sim, pelo Vite (`vi.hoisted` para contornar) |
| ESM | funciona, mas a arquitetura é CJS-first | nativo |
| TypeScript | `ts-jest` ou `babel-jest` | nativo |
| watch | não é o padrão (`--watch`) | **é** o padrão (`vitest` sem `run`) |
| React Native | suportado | **não suportado** |

**Migrar de Jest para Vitest**, quando faz sentido, é barato porque a API é quase idêntica:

1. `npm i -D vitest` e remova `jest`, `babel-jest`, `ts-jest`;
2. troque `jest.fn` → `vi.fn`, `jest.mock` → `vi.mock`, `jest.spyOn` → `vi.spyOn`
   (ou ligue `globals: true` e mantenha o resto);
3. `jest.config.js` → `vitest.config.js`;
4. `moduleNameMapper` → `resolve.alias` do Vite;
5. **cuidado**: `jest.setTimeout` → `testTimeout` na config; `jest.requireActual` →
   `importarOriginal`.

Não migre se o único ganho for velocidade e a suíte já roda em tempo aceitável.

---

## 5. As armadilhas exclusivas do JavaScript

Esta é a seção mais importante do arquivo. Nenhuma delas existe em Python.

### 5.1 Promessa não aguardada = teste que sempre passa

```javascript
// ERRADO — passa mesmo que validar(-1) não rejeite
it('rejeita negativo', async () => {
  assert.rejects(async () => validar(-1));
});

// CERTO
it('rejeita negativo', async () => {
  await assert.rejects(async () => validar(-1));
});
```

```javascript
// ERRADO em Vitest/Jest
expect(promessa).rejects.toThrow();

// CERTO
await expect(promessa).rejects.toThrow();
```

**Proteção real:** a regra `@typescript-eslint/no-floating-promises` (exige tipos) ou
`vitest/valid-expect` do `eslint-plugin-vitest`. E, no `node:test`, `t.plan(n)`.

### 5.2 Igualdade: `toBe` × `toEqual` × `deepStrictEqual`

```javascript
expect({ a: 1 }).toBe({ a: 1 });          // ❌ falha — Object.is, referências diferentes
expect({ a: 1 }).toEqual({ a: 1 });       // ✅
expect({ a: 1, b: undefined }).toEqual({ a: 1 });        // ✅ toEqual IGNORA undefined
expect({ a: 1, b: undefined }).toStrictEqual({ a: 1 });  // ❌ toStrictEqual não ignora

class Dinheiro { constructor(c) { this.centavos = c; } }
expect(new Dinheiro(1)).toEqual({ centavos: 1 });        // ✅ toEqual ignora a classe
expect(new Dinheiro(1)).toStrictEqual({ centavos: 1 });  // ❌ toStrictEqual compara o tipo
```

**Recomendação:** `toStrictEqual` por padrão. `toEqual` esconde bugs de `undefined` e de tipo.

### 5.3 Estado de módulo é um singleton

```javascript
// contador.js
export let total = 0;
export function incrementar() { total += 1; }
```

Todo arquivo de teste que importar esse módulo **no mesmo worker** compartilha `total`. Em
Python o problema existe igual; em JavaScript ele é agravado pelo cache de módulos ESM, que
**não** pode ser limpo facilmente.

Saídas:
- não tenha estado no nível do módulo (a melhor);
- exporte uma função `reiniciar()` e chame no `beforeEach`;
- `vi.resetModules()` (Vitest) força a reimportação;
- `pool: 'forks'` + `isolate: true` dá um processo por arquivo.

### 5.4 Temporizadores falsos que vazam

```javascript
// SEM este afterEach, todo teste dos arquivos SEGUINTES vê o tempo congelado
afterEach(() => {
  vi.useRealTimers();
});
```

No `node:test` isso não acontece: `t.mock.timers` é restaurado automaticamente ao fim do
teste. É uma vantagem real do corredor embutido.

### 5.5 `this` e funções-seta

```javascript
// Mocha exigia `function () {}` para acessar `this.timeout()`.
// node:test, Vitest e Jest NÃO usam `this` — use funções-seta sem medo.
```

Se você encontrar tutorial dizendo "não use função-seta em testes", ele é da era Mocha.

### 5.6 A extensão no import é obrigatória em ESM

```javascript
import { slug } from './slug';      // ❌ ERR_MODULE_NOT_FOUND
import { slug } from './slug.js';   // ✅
```

O Vitest resolve sem a extensão (herança do Vite), o `node:test` não. Código que passa no
Vitest pode quebrar rodando direto no Node — mais um argumento para testar com o mesmo
resolvedor que a produção usa.

### 5.7 Comparar `NaN`, `-0` e datas

```javascript
// NaN: as ferramentas de teste NÃO usam ===, usam Object.is (SameValue).
// Por isso NaN é igual a NaN aqui, embora `NaN === NaN` seja false na linguagem.
assert.equal(NaN, NaN);              // ✅ passa (assert/strict usa Object.is)
assert.deepStrictEqual(NaN, NaN);    // ✅
expect(NaN).toBe(NaN);               // ✅

// -0: pelo mesmo motivo, 0 e -0 são DIFERENTES para as ferramentas,
// embora `0 === -0` seja true na linguagem. Object.is(0, -0) === false.
expect(0).toBe(-0);                  // ❌ falha
expect(0).toEqual(-0);               // ❌ falha também

expect(new Date('2026-08-13')).toEqual(new Date('2026-08-13'));  // ✅
```

Guarde a regra: **em asserção, a igualdade é `Object.is`, não `===`.** As duas divergem
exatamente em dois pontos — `NaN` e `-0` — e os dois aparecem em código de cálculo.
*(Todos os casos acima foram executados em Node v24.18.0 e Vitest 4.1.10.)*

---

## 6. TypeScript

| Corredor | Como |
|---|---|
| **Vitest** | funciona direto; usa `esbuild`, **não** faz checagem de tipo |
| **Jest** | `ts-jest` (checa tipos, lento) ou `babel-jest` (rápido, não checa) |
| **`node:test`** | `node --experimental-strip-types --test` (Node 22.6+), ou compile antes |

**Ponto que quase todo mundo erra:** Vitest e Babel **removem** os tipos sem verificá-los.
Um erro de tipo não quebra a suíte. A verificação é um passo separado:

```bash
tsc --noEmit        # rode isto no CI, junto com os testes
```

Testar os **tipos** em si (que uma função rejeita o argumento errado) é outra coisa ainda:

```typescript
import { expectTypeOf } from 'vitest';

expectTypeOf(desconto).toBeFunction();
expectTypeOf(desconto).parameter(0).toEqualTypeOf<number>();
// @ts-expect-error — o teste falha se este erro DEIXAR de acontecer
desconto('texto');
```

`@ts-expect-error` é subutilizado: ele é uma asserção de que aquele erro de tipo **deve**
existir.

---

## 7. Testando front-end

Fora do escopo principal deste curso, mas o mínimo para não errar feio:

```javascript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

it('mostra o total quando o item é adicionado', async () => {
  render(<Carrinho />);

  await userEvent.click(screen.getByRole('button', { name: 'Adicionar café' }));

  expect(screen.getByText('R$ 29,90')).toBeInTheDocument();
});
```

O princípio da Testing Library, e a razão de ela ter substituído o Enzyme:

> *"Quanto mais os seus testes se parecem com o modo como o software é usado, mais confiança
> eles dão."*

Consequência prática: **busque por papel de acessibilidade e texto visível**
(`getByRole`, `getByLabelText`), nunca por classe CSS ou estrutura de componente. Um teste
que usa `container.querySelector('.btn-primary')` quebra quando o designer troca a classe —
sem que nada tenha mudado para o usuário. E buscar por papel tem um efeito colateral
excelente: se `getByRole('button')` não acha o seu `<div onClick>`, isso é um **problema de
acessibilidade real** que o teste acabou de denunciar.

---

## 8. Organização

```
projeto/
├── package.json
├── vitest.config.js          (se usar Vitest)
├── src/
│   ├── dinheiro.js
│   └── dinheiro.test.js      ← opção A: teste ao lado do código
└── test/                     ← opção B: pasta separada
    ├── dinheiro.test.js
    └── api.integracao.test.js
```

| | Ao lado (`src/x.test.js`) | Separado (`test/`) |
|---|---|---|
| achar o teste | trivial | precisa procurar |
| refatorar/mover | move junto | esquece de mover |
| empacotar | precisa excluir do build | limpo |
| convenção | Vitest, Jest, React | `node:test`, Node em geral |

**Recomendação:** ao lado para front-end e bibliotecas pequenas; separado para serviços,
onde a distinção unitário/integração importa e vira estrutura de pastas.

---

## 9. `package.json` recomendado

```json
{
  "type": "module",
  "engines": { "node": ">=20" },
  "scripts": {
    "test": "node --test",
    "test:unit": "node --test test/unit/",
    "test:integracao": "node --test test/integracao/",
    "test:watch": "node --test --watch",
    "test:cov": "node --test --experimental-test-coverage",
    "test:ci": "node --test --test-reporter=spec --test-reporter-destination=stdout --test-reporter=junit --test-reporter-destination=resultado.xml"
  }
}
```

O `test:ci` produz saída legível **e** XML para o painel do CI, ao mesmo tempo.

---

## Autoteste

1. Em que caso o `node:test` é a melhor escolha, e em que caso o Vitest é?
2. Por que os `await` são obrigatórios em subtestes do `node:test`?
3. Para que serve `t.plan(3)` e que problema ele resolve?
4. Explique o içamento do `vi.mock` e como `vi.hoisted` o contorna.
5. Qual a diferença entre `toBe`, `toEqual` e `toStrictEqual` para `{a: 1, b: undefined}`?
6. Por que `assert.rejects` sem `await` produz teste que sempre passa? Cite duas proteções.
7. Por que estado no nível do módulo é mais problemático em JavaScript do que em Python?
8. Qual vantagem o `node:test` tem sobre o Vitest quanto a temporizadores falsos?
9. Vitest remove os tipos sem verificá-los. Qual passo você precisa acrescentar ao CI?
10. Por que `getByRole` é melhor que `querySelector('.btn')`, e qual é o efeito colateral bom?
11. Quando faz sentido migrar de Jest para Vitest, e quando não faz?
12. Por que `import './x'` sem extensão passa no Vitest e quebra no Node?

---

## Fontes consultadas (13/08/2026)

- [Node.js — Test runner (API)](https://nodejs.org/api/test.html)
- [Node.js — Collecting code coverage](https://nodejs.org/learn/test-runner/collecting-code-coverage)
- [Vitest vs Jest 2026 — SitePoint](https://www.sitepoint.com/vitest-vs-jest-2026-migration-benchmark/)
- [Jest vs Vitest 2026 — Reintech](https://reintech.io/blog/jest-vs-vitest-2026-testing-framework-comparison)
- Versões conferidas por `npm view` em 12/08/2026: `vitest@4.1.10`, `jest@30.4.2`,
  `@playwright/test@1.62.1`. Execuções locais em Node v24.18.0.
