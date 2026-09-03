# 15 · Node.js — do `.env` à produção

`Nível: intermediário` · `Atualizado em: 14/08/2026`
`Base: Node v24.18.0 · dotenv 17.4.2 — verificados nesta máquina`

---

## 1. A decisão de partida: `dotenv` ou nativo?

Desde o Node 20.6.0 (setembro de 2023) existe `--env-file` nativo. Desde 22.9.0,
`--env-file-if-exists`. Desde 21.7.0, `process.loadEnvFile()`.

| | `--env-file` nativo | `dotenv` (npm) |
|---|---|---|
| Dependência | zero | uma (mais a cadeia de suprimentos dela) |
| Node mínimo | 20.6 | qualquer |
| Expansão `${VAR}` | **não** | só com `dotenv-expand` |
| Arquivo ausente | erro (use `--env-file-if-exists`) | silencioso |
| Sobrescreve variável existente | não | só com `override: true` |
| Múltiplos arquivos | sim, repetindo a flag | sim, com array em `path` |
| Chamável do código | `process.loadEnvFile()` | `require('dotenv').config()` |
| Criptografia embutida | não | via `dotenvx` (produto separado) |

**Minha recomendação, e é opinião, não consenso:** em projeto novo com Node ≥ 22, use
o **nativo**. Menos uma dependência num lugar onde a dependência processa segredo, e
o código fica idêntico em dev e produção. Se você depende de expansão, resolva a
expansão **no código**, que é o lugar certo para lógica.

Quando eu ainda usaria `dotenv`: base de código antiga em Node 18; monorepo que
carrega vários `.env` com regras de precedência complicadas; time que já usa
`dotenvx` para criptografia.

---

## 2. O padrão correto, e por que a ordem importa

```json
{
  "scripts": {
    "start": "node src/app.mjs",
    "dev": "node --env-file-if-exists=.env --watch src/app.mjs"
  }
}
```

Repare: **`start` não menciona `.env`**. Em produção, o `.env` não existe, e o
`start` funciona porque as variáveis já estão no ambiente. É o mesmo `package.json`
nos dois lugares.

### O erro de ordem em ESM

```javascript
// ❌ ERRADO — e falha silenciosamente, que é o pior tipo de falha
import { pool } from './db.js';    // db.js lê process.env.DATABASE_URL AQUI (undefined)
import 'dotenv/config';            // tarde demais
```

Em ESM, **todos os `import` são resolvidos e executados antes de qualquer instrução
do módulo**, na ordem em que aparecem. `db.js` roda primeiro.

```javascript
// ✅ funciona
import 'dotenv/config';
import { pool } from './db.js';
```

```bash
# ✅✅ melhor: o ambiente está pronto antes do primeiro byte do seu código
node --env-file-if-exists=.env src/app.mjs
```

Em CommonJS o problema é menor (`require` é síncrono e na ordem), mas a solução da
flag continua sendo a mais limpa.

---

## 3. As armadilhas específicas de Node

### 3.1 Tudo é string, e `undefined` é silencioso

```javascript
process.env.PORT          // "3000"  — string
process.env.DEBUG         // "false" — e Boolean("false") === true
process.env.NAO_EXISTE    // undefined, sem aviso nenhum
Number(process.env.PORT)  // 3000
Number("")                // 0    ⚠️ string vazia vira ZERO, não NaN
Number(undefined)         // NaN
```

A linha `Number("") === 0` já causou incidente real: `PORT=` (vazio) vira porta 0,
que em `listen()` significa "escolha uma porta livre qualquer" — e o serviço sobe
numa porta aleatória, saudável para o health check e invisível para o balanceador.

Por isso o [projeto-modelo](07-projeto-modelo/src/config.mjs) trata **string vazia
como ausente**.

### 3.2 `process.env` não é um objeto normal

```javascript
process.env.X = 42;
typeof process.env.X;        // "string"  ← converteu sozinho
process.env.Y = undefined;
process.env.Y;               // "undefined"  ← a STRING, não o valor
delete process.env.Y;        // é assim que se remove de verdade
Object.keys(process.env).length;
```

E, no Windows, o acesso é **case-insensitive**; no Linux, não. Código que lê
`process.env.Path` funciona na máquina do colega e falha em produção.

### 3.3 `NODE_OPTIONS` executa código

```bash
NODE_OPTIONS="--require /tmp/malicioso.js" node app.js
```

Se um atacante controla o ambiente do seu processo, ele **executa código dentro
dele**. Não é falha do Node — é o modelo. Consequência: um serviço que recebe
variáveis de fonte não confiável (por exemplo, um construtor de builds
multi-inquilino) precisa de **lista de permissão** de nomes.

### 3.4 `NODE_ENV` não é o que muitos pensam

`NODE_ENV=production` **não** faz o Node ficar mais rápido nem mais seguro por si.
Ele é apenas uma convenção que bibliotecas leem (Express desliga stack traces
detalhados; React usa o build de produção; `npm install` pula `devDependencies`).

O erro comum é usar `NODE_ENV` como chave de decisão para tudo:

```javascript
// ❌ acopla comportamento ao nome do ambiente
if (process.env.NODE_ENV === 'production') { usarTLS(); }

// ✅ cada comportamento tem a sua própria variável
if (config.tlsHabilitado) { usarTLS(); }
```

O motivo é concreto: no dia em que você precisar de TLS em homologação, a primeira
versão exige alterar código; a segunda, só configuração.

---

## 4. Frameworks

### Next.js — o mais perigoso da lista

| Prefixo | Onde vale | É segredo? |
|---|---|---|
| sem prefixo | só no servidor (Server Components, Route Handlers, `getServerSideProps`) | pode ser |
| `NEXT_PUBLIC_` | **embutido no JavaScript enviado ao navegador** | **NUNCA** |

```javascript
// ❌ CATASTRÓFICO — vai para o bundle, qualquer visitante lê
const chave = process.env.NEXT_PUBLIC_STRIPE_SECRET_KEY;

// ✅ chave secreta só em código de servidor
export async function POST(req) {
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
}
```

⚠️ **A substituição acontece em tempo de *build*.** Trocar a variável no painel da
Vercel **não** muda um `NEXT_PUBLIC_` já construído — é preciso reconstruir. Isso
significa que a variável pública está **congelada dentro do artefato**, e o artefato
não é mais promovível entre ambientes. Detalhes em
[20-frontend-e-build-time.md](20-frontend-e-build-time.md).

### Express

```javascript
import express from 'express';
import { config } from './config.mjs';   // já validado

const app = express();
app.set('trust proxy', config.confiarNoProxy);
app.listen(config.porta);
```

Evite `app.get('env')` — ele lê `NODE_ENV` e reintroduz o acoplamento do §3.4.

### NestJS

```typescript
@Module({
  imports: [ConfigModule.forRoot({
    isGlobal: true,
    validationSchema: Joi.object({          // valida na inicialização
      DATABASE_URL: Joi.string().uri().required(),
      PORT: Joi.number().port().default(3000),
    }),
    validationOptions: { abortEarly: false }, // 🔑 reporta TODOS os erros
  })],
})
export class AppModule {}
```

`abortEarly: false` é o detalhe que quase todo mundo esquece — sem ele, você conserta
um erro de configuração por deploy.

---

## 5. Produção

### 5.1 Não empacote o `.env`

```jsonc
// package.json
{
  "files": ["src", "package.json"]   // o .env NUNCA entra no pacote publicado
}
```

E no `.dockerignore`, `.env` e `.git` — ver [06-exemplos.md #10](06-exemplos.md).

### 5.2 `pino` com redação, para o log

```javascript
import pino from 'pino';

export const log = pino({
  level: config.logLevel,
  redact: {
    paths: [
      'req.headers.authorization',
      'req.headers.cookie',
      '*.password', '*.senha', '*.token', '*.apiKey',
      'config.databaseUrl',
    ],
    censor: '[REDIGIDO]',
  },
});
```

A redação por caminho do `pino` é mais rápida que percorrer objeto à mão, mas **não
pega senha embutida em URL**. Ver `redigirUrl` em
[07-projeto-modelo/src/log.mjs](07-projeto-modelo/src/log.mjs).

### 5.3 Não deixe segredo vazar em relatório de erro

```javascript
process.on('uncaughtException', (e) => {
  log.error({ tipo: e.name, mensagem: e.message }, 'exceção não capturada');
  // ❌ NUNCA: log.error({ env: process.env })
  process.exit(1);
});
```

Ferramentas de APM (Sentry, Datadog, New Relic) coletam o ambiente por padrão em
algumas configurações. **Confira a configuração de cada uma** — é um caminho de
vazamento silencioso e com retenção longa.

### 5.4 Segredo em memória: o que dá e o que não dá

Uma pergunta que sempre aparece: *dá para apagar o segredo da memória depois de usar?*

```javascript
// tentativa comum, e ela NÃO funciona
let senha = process.env.SENHA;
usar(senha);
senha = null;   // ❌ a string original continua no heap até o GC decidir
```

Strings em JavaScript são **imutáveis** e o coletor de lixo não dá garantia de
quando (nem se) sobrescreve a memória. Se o modelo de ameaça inclui despejo de
memória, o caminho é `Buffer`:

```javascript
const b = Buffer.from(process.env.SENHA, 'utf8');
usar(b);
b.fill(0);                 // zera de verdade os bytes
delete process.env.SENHA;  // remove a cópia do ambiente do processo
```

Ainda assim, a cópia original que veio no `execve` pode persistir. Honestamente:
para a maioria dos sistemas, isso é teatro de segurança — o atacante que consegue
despejar a memória do seu processo já ganhou. Vale o esforço só em software que
manipula chave-mestra ou material criptográfico de terceiros.

---

## 6. Alternativa: `dotenvx`

O autor do `dotenv` mantém o **`dotenvx`**, que criptografa o `.env` com uma chave
pública, permitindo commitar o `.env` cifrado:

```bash
npx @dotenvx/dotenvx encrypt      # gera .env criptografado + .env.keys
npx @dotenvx/dotenvx run -- node app.js
```

**A avaliação honesta:** ele resolve *transporte* do segredo, não *gestão*. A chave
privada continua tendo de chegar ao servidor por algum caminho (o problema do
segredo zero), e não há rotação, auditoria de acesso nem credencial dinâmica. É
melhor que `scp .env`, e é bem pior que um cofre. Como concorrente direto, o **SOPS**
faz a mesma coisa, é agnóstico de linguagem e é sandbox da CNCF — eu preferiria SOPS.
Comparação em [40-cofres-de-segredos.md](40-cofres-de-segredos.md).

---

## 7. Receituário

| Situação | Faça |
|---|---|
| Projeto novo, Node ≥ 22 | `--env-file-if-exists` em dev; nada em produção |
| Node 18 ou anterior | atualize; se não puder, `dotenv` importado primeiro |
| Precisa de expansão | monte a string no código |
| Monorepo | um `config.mjs` por serviço, todos com o mesmo formato |
| TypeScript | valide com `zod`/`valibot` e exporte o tipo inferido |
| Serverless (Lambda) | variáveis na configuração da função + cofre com cache no `init` |
| Precisa mostrar a config no suporte | rota autenticada devolvendo a versão **mascarada** |

Exemplo com `zod`, que é o que eu faria em TypeScript:

```typescript
import { z } from 'zod';

const Esquema = z.object({
  DATABASE_URL: z.string().url(),
  PORT: z.coerce.number().int().min(1).max(65535).default(3000),
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
  API_KEY: z.string().min(8),
});

const r = Esquema.safeParse(process.env);
if (!r.success) {
  console.error('❌ Configuração inválida:');
  for (const e of r.error.issues) console.error(`   • ${e.path.join('.')}: ${e.message}`);
  process.exit(78);
}
export const config = Object.freeze(r.data);
export type Config = z.infer<typeof Esquema>;   // tipo derivado do esquema, de graça
```

`safeParse` (e não `parse`) é o que permite listar **todos** os erros; `z.coerce`
resolve o "tudo é string".

---

## Autoteste

1. A partir de qual versão do Node existe `--env-file`? E `--env-file-if-exists`? Por que a segunda é a certa em produção?
2. Por que `import 'dotenv/config'` precisa ser o primeiro `import` em ESM?
3. `PORT=` (vazio). O que `Number(process.env.PORT)` devolve, e que incidente isso causa?
4. Por que `NEXT_PUBLIC_` nunca pode conter segredo, e por que trocá-lo no painel não basta?
5. O que `NODE_ENV=production` realmente faz? Cite dois efeitos reais.
6. Por que `senha = null` não apaga o segredo da memória em JavaScript?
7. Qual a diferença entre `parse` e `safeParse` do zod, no contexto de configuração?
8. Por que `NODE_OPTIONS` transforma controle do ambiente em execução de código?
9. Em que caso você ainda escolheria `dotenv` em vez do carregador nativo?

---

**Próximo:** [16-php.md](16-php.md) · Voltar ao [mapa](00-MAPA.md)
