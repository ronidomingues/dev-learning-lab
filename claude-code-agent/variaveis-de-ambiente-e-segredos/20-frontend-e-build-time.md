# 20 · Front-end — por que não existe segredo no navegador

`Nível: intermediário` · `Atualizado em: 14/08/2026`

Este arquivo existe porque é o erro mais caro que se comete com variáveis de ambiente,
e porque a ferramenta **ativamente induz ao erro**: ela chama de "variável de
ambiente" uma coisa que não é variável de ambiente.

---

## 1. A afirmação, sem rodeios

> **Qualquer valor que chegue ao navegador é público.**
> Não existe "esconder no JavaScript". Não existe ofuscação que resolva.
> Não existe minificação que proteja. Se o código do cliente consegue ler,
> o usuário consegue ler.

Isso não é uma limitação a contornar. É uma **propriedade estrutural** do modelo
cliente-servidor: o navegador precisa do valor para executar; logo, o valor está na
máquina do usuário; logo, o usuário o tem.

---

## 2. Onde a confusão nasce

```bash
# .env de um projeto Vite
VITE_API_URL=https://api.exemplo.com
VITE_STRIPE_KEY=sk_live_51Abc...      # ☠️
```

O nome do arquivo é `.env`. A ferramenta chama de "variável de ambiente". A sintaxe
é idêntica à do servidor. **Tudo indica que é o mesmo mecanismo. Não é.**

O que realmente acontece no build:

```javascript
// o que você escreve
const chave = import.meta.env.VITE_STRIPE_KEY;

// o que o bundler GRAVA no arquivo .js entregue ao navegador
const chave = "sk_live_51Abc...";
```

É **substituição textual em tempo de compilação**. Não há leitura de ambiente em
tempo de execução. O valor vira uma **string literal dentro do arquivo público**.

Os prefixos, por ferramenta:

| Ferramenta | Prefixo que vai para o navegador | Acesso |
|---|---|---|
| Vite | `VITE_` | `import.meta.env.VITE_X` |
| Next.js | `NEXT_PUBLIC_` | `process.env.NEXT_PUBLIC_X` |
| Create React App (obsoleto) | `REACT_APP_` | `process.env.REACT_APP_X` |
| Nuxt | `NUXT_PUBLIC_` | `useRuntimeConfig().public.x` |
| SvelteKit | `PUBLIC_` | `import { PUBLIC_X } from '$env/static/public'` |
| Angular | — (usa `environment.ts`) | idem: substituído no build |

**A palavra `PUBLIC` está literalmente no nome em quatro das seis.** É um aviso, não
uma categoria organizacional.

---

## 3. Prove você mesmo, em 30 segundos

```bash
npm run build
grep -r "sk_live" dist/ && echo "☠️ SEGREDO NO BUNDLE" || echo "✅ limpo"
```

Ou, num site já publicado, sem acesso ao código:

```bash
curl -s https://site-alvo.com.br | grep -oE 'src="[^"]*\.js"' | head
curl -s https://site-alvo.com.br/assets/index-abc123.js | grep -oE '(sk_live|AKIA|AIza|xox[bp]-)[A-Za-z0-9_-]{10,}'
```

*(Procedimento correto e amplamente usado; **não executado aqui** por não haver
alvo. Rode no seu próprio site.)*

E o modo mais simples de todos, que qualquer usuário sabe fazer: F12 → aba Network →
qualquer requisição. O cabeçalho `Authorization` está lá, inteiro.

> **Adicione isto ao seu CI.** Um `grep` no `dist/` procurando padrões de chave, que
> falha o build. Custa três linhas e evita a manchete.

---

## 4. Um agravante: a variável fica **congelada** no artefato

Consequência que quase ninguém antecipa: como a substituição é em tempo de build, o
artefato deixa de ser promovível entre ambientes.

```
Servidor (certo):     [um build] → dev → homologação → produção
                       o mesmo artefato, configurado por ambiente ✅

Front-end (realidade): [build dev] → só serve para dev
                       [build hml] → só serve para homologação
                       [build prd] → só serve para produção      ❌ três artefatos
```

Isso **viola o Fator V do Twelve-Factor** ("separe build e run") — e a violação é
imposta pela ferramenta, não é escolha sua.

Efeitos práticos:

- trocar `NEXT_PUBLIC_API_URL` no painel da Vercel **não muda nada** até reconstruir;
- o que você testou em homologação **não é o binário** que foi para produção;
- rollback de configuração exige rollback de build.

**Como escapar:** carregue a configuração pública em **tempo de execução**, não de build.

```javascript
// index.html — servido sem cache, gerado pelo servidor
<script>
  window.__CONFIG__ = { apiUrl: "https://api.exemplo.com", ambiente: "producao" };
</script>
```

```javascript
// no aplicativo
const apiUrl = window.__CONFIG__.apiUrl;
```

Ou um endpoint `/config.json` buscado na inicialização. Assim o **mesmo** bundle
serve os três ambientes, e a configuração volta a ser configuração.
Continua público — mas agora é público **e** promovível.

---

## 5. O que fazer no lugar

### 5.1 Chave secreta → proxy no servidor

```
❌ ERRADO
   navegador ──[sk_live_...]──► API da Stripe

✅ CERTO
   navegador ──[cookie de sessão]──► SEU servidor ──[sk_live_...]──► API da Stripe
```

```javascript
// app/api/pagamentos/route.js  (Next.js, código de SERVIDOR)
import Stripe from 'stripe';
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);   // sem NEXT_PUBLIC_

export async function POST(req) {
  const sessao = await autenticar(req);          // 1. quem é o usuário?
  if (!sessao) return Response.json({ erro: 'não autorizado' }, { status: 401 });

  const { valorEmCentavos } = await req.json();
  if (!Number.isInteger(valorEmCentavos) || valorEmCentavos <= 0) {   // 2. valide!
    return Response.json({ erro: 'valor inválido' }, { status: 400 });
  }

  const intento = await stripe.paymentIntents.create({
    amount: valorEmCentavos,
    currency: 'brl',
    metadata: { usuario: sessao.id },
  });
  return Response.json({ clientSecret: intento.client_secret });   // ✅ este PODE ir
}
```

Repare nos passos 1 e 2: **um proxy sem autenticação e sem validação é apenas a sua
chave secreta com uma URL mais bonita**. Se qualquer um pode chamar
`POST /api/pagamentos` com o valor que quiser, você não protegeu nada — só transferiu
o abuso para a sua conta de nuvem.

### 5.2 Chaves que **são** públicas por projeto

Nem toda chave é segredo. Estas são **projetadas** para ficar no navegador:

| Chave | Pública? | Como se protege de verdade |
|---|---|---|
| `pk_live_…` (Stripe publishable) | **sim** | só cria tokens; não move dinheiro |
| Chave da API do Google Maps | **sim** | restrição por *HTTP referrer* no console |
| `anon key` do Supabase | **sim** | *Row Level Security* no banco — **obrigatória** |
| Chave web do Firebase | **sim** | Firebase Security Rules |
| ID de cliente OAuth | **sim** | *redirect URI* registrada + PKCE |
| `sk_live_…`, `service_role`, `AKIA…` | **NÃO** | nunca chegam ao navegador |

**A lição geral:** a proteção dessas chaves **não** é o segredo — é a **restrição do
lado do servidor** (referrer, RLS, regras, escopo). Uma chave `anon` do Supabase sem
RLS configurada é acesso total ao banco para qualquer visitante, e isso já derrubou
muitas aplicações de produção. Publicar a chave é seguro **só se** a restrição existir.

### 5.3 A regra de decisão

```
Este valor precisa ficar secreto para funcionar?
├── SIM → fica no servidor. Sem exceção. Front-end fala com o SEU servidor.
└── NÃO → pode ir ao navegador. E então:
          ├── qual restrição do lado do servidor o protege de abuso?
          └── carregue-o em tempo de execução, não de build (§4)
```

---

## 6. Mobile e desktop: o mesmo problema, sem o alívio

Aplicativo móvel e Electron **também** entregam o código ao usuário — e ali é ainda
pior, porque o binário fica na máquina dele para sempre.

```bash
# extrair strings de um APK: qualquer pessoa consegue, em minutos
unzip -o app.apk -d app/ && strings app/classes.dex | grep -E 'sk_live|AKIA|AIza'
```

Ferramentas como `apktool`, `jadx` e `Hopper` tornam isso trivial. **Ofuscação
aumenta o tempo do atacante em minutos, não em ordens de grandeza.**

E há um agravante sobre a web: no navegador, você conserta e recarrega; no app,
o usuário precisa **atualizar** — e uma parte da base nunca atualiza. A chave vazada
continua embutida em versões instaladas por anos.

A resposta é a mesma: **proxy no seu servidor**, autenticação por usuário, e
credenciais de vida curta obtidas após o login.

---

## 7. Autoteste

1. Por que "ofuscar o JavaScript" não protege uma chave de API?
2. O que exatamente o bundler faz com `import.meta.env.VITE_X` durante o build?
3. Por que trocar um `NEXT_PUBLIC_` no painel da Vercel não surte efeito imediato?
4. Qual fator do Twelve-Factor o build-time replacement viola, e por quê?
5. Como se carrega configuração pública em tempo de execução, e o que isso resolve?
6. Qual a diferença entre `pk_live_` e `sk_live_` da Stripe?
7. Por que a chave `anon` do Supabase é publicável, e o que a torna perigosa na prática?
8. Um proxy no servidor sem autenticação resolve o problema? Justifique.
9. Escreva o comando que verifica se um segredo vazou no seu `dist/`.
10. Por que a situação é pior em aplicativo móvel do que na web?

---

**Próximo:** [30-entrega-em-producao.md](30-entrega-em-producao.md) · Voltar ao [mapa](00-MAPA.md)
