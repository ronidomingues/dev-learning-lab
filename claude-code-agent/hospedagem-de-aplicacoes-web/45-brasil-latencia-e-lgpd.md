# 45 · Brasil — latência, regiões e LGPD

`Nível: intermediário` · `Atualizado em 18/08/2026`

Um capítulo que quase nenhum material internacional tem, e que muda a decisão de quem tem
usuários no Brasil.

---

## 1. Quem tem região no Brasil (18/08/2026)

| Serviço | Região no Brasil | Código | Observação |
|---|---|---|---|
| **AWS** | ✅ São Paulo | `sa-east-1` | a mais antiga (2011); preços ~30–50% acima dos EUA |
| **Google Cloud** | ✅ São Paulo · Osasco | `southamerica-east1` / `-west1` | franquia gratuita do Cloud Run **não** vale aqui |
| **Azure** | ✅ Brasil Sul (Campinas) | `brazilsouth` | |
| **Oracle Cloud** | ✅ São Paulo · Vinhedo | `sa-saopaulo-1` / `sa-vinhedo-1` | inclusive no "Always Free" |
| **Fly.io** | ✅ Guarulhos | `gru` | **a única PaaS pequena com região no Brasil** |
| **Neon** | ✅ São Paulo (sobre AWS) | `aws-sa-east-1` | inclusive no plano gratuito |
| **Supabase** | ✅ São Paulo (sobre AWS) | `sa-east-1` | inclusive no plano gratuito |
| **Upstash** | ✅ São Paulo | como primária ou réplica global | |
| **Cloudflare** | ✅ dezenas de PoPs | São Paulo, Rio, Fortaleza, Porto Alegre, Brasília… | borda, não data center de computação dedicado |
| **Magalu Cloud** | ✅ nuvem nacional | — | operação e contrato no Brasil, em real |
| **Render** | ❌ | — | Oregon, Ohio, Virgínia, Frankfurt, Cingapura |
| **Railway** | ❌ | — | EUA, Holanda, Cingapura |
| **Koyeb** | ❌ | — | Frankfurt, Washington |
| **Northflank** | ❌ | — | |
| **Heroku** | ❌ | — | |
| **Vercel / Netlify** | ✅ (borda) | — | funções rodam na borda; o **banco** é que decide a latência |

---

## 2. Quanto custa a distância

Ida e volta (RTT) típica a partir de São Paulo, medida em redes comerciais:

| Destino | RTT | Origem física do número |
|---|---|---|
| São Paulo (mesma região) | **1 a 5 ms** | — |
| Rio de Janeiro | ~10 ms | 430 km |
| Porto Alegre / Fortaleza | 25 a 45 ms | distância nacional |
| **Virgínia (`us-east-1`)** | **~120 ms** | 7.600 km + roteamento |
| **Oregon (`us-west-2`)** | **~170 ms** | 10.500 km |
| Frankfurt | ~200 ms | 9.800 km, rota via EUA em muitos trajetos |
| Cingapura | ~330 ms | quase antípoda |

**O piso físico.** A luz viaja a ~200.000 km/s em fibra. São Paulo–Virgínia são ~7.600 km em
linha reta; a fibra faz mais voltas, mas mesmo no melhor caso a ida e volta custa **~76 ms**.
**Parada legítima: lei física.** Nenhum software vence isso.

### Onde a distância dói de verdade

Não é no usuário → servidor. É no **servidor → banco**, porque essa viagem se repete a cada
consulta:

```
Usuário (SP) ─── 170 ms ──► Backend (Oregon) ─── 2 ms ──► Banco (Oregon)
   página com 8 consultas: 170 + 8×2 + 170 = ~356 ms       ← aceitável

Usuário (SP) ─── 20 ms ───► Backend (SP) ─── 170 ms ──► Banco (Oregon)
   página com 8 consultas: 20 + 8×170 + 20 = ~1.400 ms     ← RUIM

Usuário (SP) ─── 20 ms ───► Backend (SP) ─── 2 ms ──► Banco (SP)
   página com 8 consultas: 20 + 8×2 + 20 = ~56 ms          ← ÓTIMO
```

> **A regra que resume tudo:** *o backend pode estar longe do usuário; o backend nunca pode
> estar longe do banco.* Se você precisar escolher entre "app perto do usuário" e "app perto do
> banco", **escolha perto do banco** — é a viagem que se repete.

Corolário desconfortável: **arquitetura de borda com banco central pode ser mais lenta que um
servidor único**. Rodar código em 300 cidades não ajuda se cada requisição vai buscar dado a
9.000 km. É exatamente por isso que existem Hyperdrive (pool e cache na borda), D1 (banco na
própria borda) e réplicas de leitura regionais.

---

## 3. As três estratégias para o Brasil

### Estratégia 1 — Tudo no Brasil (recomendada quando o público é nacional)

```
Frontend: Cloudflare Pages (PoPs no Brasil)
Backend:  Fly.io gru  ─ ou ─ Cloud Run southamerica-east1  ─ ou ─ VPS na Magalu/Oracle SP
Banco:    Neon sa-east-1  ─ ou ─ Supabase sa-east-1  ─ ou ─ RDS sa-east-1
Cache:    Upstash São Paulo  ─ ou ─ Valkey na mesma máquina
```
Resultado: **20 a 60 ms** de tempo até o primeiro byte. Custo a partir de US$ 2/mês (Pilha B).

### Estratégia 2 — Tudo nos EUA, com cuidado

```
Frontend: CDN (a distância some por cache)
Backend + Banco: MESMA região dos EUA (us-east-1 é ~50 ms mais perto do BR que us-west-2)
```
Resultado: **150 a 250 ms**. Aceitável para painel administrativo, ferramenta interna,
software B2B usado com calma. **Ruim** para e-commerce, checkout e qualquer coisa com muitas
interações curtas — cada clique custa 200 ms.

**Se for para os EUA, prefira a Virgínia (`us-east-1`) a Oregon (`us-west-2`).** São ~50 ms de
diferença de graça, e várias plataformas oferecem as duas.

### Estratégia 3 — Híbrida

Frontend e cache de leitura na borda; escrita e consistência num banco central.
Ex.: Workers + Hyperdrive (cache de consulta na borda) + Neon `sa-east-1`.
Boa quando a leitura domina e a escrita é rara.

---

## 4. LGPD — o que realmente exige atenção

A **Lei nº 13.709/2018 (LGPD)**, em vigor desde setembro de 2020 com sanções desde agosto de
2021, é o marco brasileiro de proteção de dados pessoais. Este material **não é consultoria
jurídica**; o que segue é a leitura prática de quem monta infraestrutura.

### 4.1 A LGPD **não** exige que os dados fiquem no Brasil

Este é o mal-entendido mais comum. **Não há exigência geral de localização de dados.** O que
existe é o **capítulo V (arts. 33 a 36)**, que regula a **transferência internacional**,
permitindo-a quando, entre outras hipóteses:

- o país de destino tiver grau de proteção adequado reconhecido pela ANPD;
- o controlador oferecer garantias — **cláusulas-padrão contratuais**, cláusulas específicas,
  normas corporativas globais ou selos;
- houver consentimento específico e destacado do titular;
- for necessária para execução de contrato ou para cumprimento de obrigação legal.

Em **agosto de 2024**, a ANPD aprovou o **Regulamento de Transferência Internacional de Dados
(Resolução CD/ANPD nº 19/2024)** e publicou o modelo de **cláusulas-padrão contratuais**, com
prazo de adequação para contratos existentes. Ou seja: usar Neon em `us-east-1` é legal — desde
que a base contratual esteja correta.

**Onde a localização vira exigência de fato:**
- setores regulados (financeiro, saúde) com normas próprias do Bacen, da ANS ou do CFM;
- contratos com órgãos públicos, que frequentemente exigem dado em território nacional;
- exigência do seu cliente corporativo, que é a razão mais comum na prática.

### 4.2 O que a LGPD exige e que depende da sua infraestrutura

| Exigência | O que fazer na prática |
|---|---|
| **Segurança adequada** (art. 46) | TLS em trânsito, criptografia em repouso, senha forte, acesso mínimo, banco **nunca** exposto à internet |
| **Registro de operações** (art. 37) | log de acesso a dado pessoal, com retenção definida |
| **Comunicar incidente** (art. 48) | você precisa **saber** que houve incidente: monitoramento e alerta não são opcionais |
| **Eliminação ao fim do tratamento** (art. 16) | saber apagar de verdade — inclusive de backups e do cache. **Redis com dado pessoal precisa de TTL** |
| **Portabilidade** (art. 18, V) | conseguir exportar os dados de um titular |
| **Operador e suboperador** (arts. 5º e 39) | seu provedor é operador; você precisa de contrato (DPA) com ele |

### 4.3 Perguntas para fazer ao provedor antes de assinar

- [ ] Existe **DPA** (acordo de processamento de dados) assinável? Ele menciona a LGPD ou só o GDPR?
- [ ] Em que país/região os dados ficam **em repouso**? E os **backups**?
- [ ] Há criptografia em repouso por padrão?
- [ ] Quais subprocessadores são usados? (o seu PaaS provavelmente roda sobre AWS/GCP)
- [ ] Como é notificado um incidente de segurança, e em quanto tempo?
- [ ] O que acontece com os dados após o encerramento da conta, e em quanto tempo são apagados?

> **Cuidado prático que quase todo mundo esquece:** o **log** é dado pessoal. Se você registra
> IP, e-mail ou identificador de usuário, isso é tratamento — e retenção infinita de log é
> exatamente o tipo de coisa que aparece mal numa auditoria. Defina retenção e cumpra.

---

## 5. Pagamento, câmbio e nota fiscal — a parte chata

Detalhes que só afetam quem paga do Brasil:

- **IOF sobre câmbio** em compras internacionais com cartão de crédito: **3,5%** em 2026.
  A redução gradual que levaria a alíquota a zero foi revertida; ela está fixa em 3,5% salvo
  nova alteração. Some ainda o **spread cambial** do emissor do cartão (costuma ser 1% a 4%),
  que não é imposto e quase ninguém considera.
- **Fatura em dólar** oscila com o câmbio: a mesma assinatura de US$ 25 pode variar dezenas de
  reais entre meses.
- **Nota fiscal / invoice**: quase todos emitem invoice em PDF. Para deduzir como despesa de
  PJ no Brasil, o contador normalmente precisa da invoice **e** do comprovante de câmbio.
- **Provedores nacionais** (Magalu Cloud, Locaweb, KingHost, Hostinger Brasil) faturam em real,
  emitem nota fiscal brasileira e evitam IOF — o preço bruto costuma ser maior, mas o custo
  total pode não ser.
- Alguns provedores aceitam **PIX** ou boleto; a maioria internacional, não.

> **Ordem de grandeza:** US$ 35/mês da Pilha C ≈ R$ 182 + IOF ≈ **R$ 188/mês**, com câmbio a
> R$ 5,20 em 18/08/2026. Ao orçar para um cliente, some uma margem de 10 a 15% para variação
> cambial.

---

## Autoteste

1. Qual é a única PaaS pequena com região no Brasil, e qual o código dela?
2. Enuncie a regra sobre distância entre backend, banco e usuário, e justifique com números.
3. Por que arquitetura de borda pode ser **mais lenta** que um servidor único?
4. Verdadeiro ou falso: a LGPD exige que dados de brasileiros fiquem no Brasil. Justifique.
5. Quais são as bases que permitem transferência internacional, e o que a ANPD aprovou em 2024?
6. Por que um Redis com dado pessoal precisa de TTL?
7. Quanto custa, em reais, a Pilha C, considerando câmbio e IOF?
8. Se for hospedar nos EUA, qual região escolher e por quê?

---

### Fontes consultadas (18/08/2026)

- Lei nº 13.709/2018 (LGPD), especialmente arts. 16, 18, 33 a 36, 37, 46 e 48
- ANPD — Resolução CD/ANPD nº 19/2024 (Regulamento de Transferência Internacional) e modelo de cláusulas-padrão contratuais
- Documentação de regiões: AWS, Google Cloud, Azure, Oracle, Fly.io, Neon, Supabase, Upstash, Cloudflare, Render, Railway
- Medições públicas de latência entre `sa-east-1`, `us-east-1` e `us-west-2`
- Cotação USD/BRL de 18/08/2026 (≈ R$ 5,20) e alíquota de IOF sobre câmbio de 3,5% vigente em 2026 — **confirme ambas antes de orçar**
