# 55 · A economia do gratuito — por que existe, quem paga, quando acaba

`Nível: intermediário` · `Atualizado em 18/08/2026`

Este capítulo responde à parte da sua pergunta que os catálogos não respondem: **por que
alguém lhe dá computação de graça, e o que isso significa para o risco do seu projeto.**

---

## 1. Ninguém dá nada de graça (e isso é bom)

Toda camada gratuita tem uma fonte de pagamento. São seis, e identificar qual delas sustenta o
seu provedor é o melhor previsor de quanto tempo aquele plano vai durar.

| # | Modelo | Como se sustenta | Exemplos | Durabilidade |
|---|---|---|---|---|
| 1 | **Aquisição de cliente** | 1% converte e paga pelos 99% | Render, Railway, Neon, Supabase | ⚠️ média — depende do funil fechar |
| 2 | **Resíduo de outro negócio** | a infraestrutura já existe para outra coisa | **Cloudflare** (a rede existe para CDN e segurança) | ✅ **alta** |
| 3 | **Investimento de risco** | queima de capital por participação de mercado | plataformas novas em rodada de captação | ❌ **baixa** |
| 4 | **Bem público / marketing técnico** | reputação, contratação, ecossistema | Oracle Cloud Free, GitHub Actions em repositório público | ⚠️ média |
| 5 | **Open source com serviço pago** | o código é grátis; o gerenciado é pago | Supabase, Coolify, Dokploy | ✅ alta (o código não some) |
| 6 | **Isca de aprisionamento** | grátis para entrar, caro para sair | serviços proprietários sem exportação | ❌ perigosa |

**A pergunta a fazer antes de confiar num plano gratuito:**

> *Para esta empresa, o que eu uso de graça é resíduo de outro negócio, ou é o produto
> principal?*

Se é resíduo (modelo 2), dura. Se é o produto (modelo 1 e 3), é uma linha de custo que alguém
vai olhar na próxima reunião de conselho. **A Cloudflare pode dar 100.000 requisições por dia
para sempre porque a rede está lá de qualquer jeito. O Render não pode dar computação
permanente sem sono, porque computação *é* o produto dele.**

---

## 2. A matemática do custo marginal

Por que 100.000 requisições/dia custam quase nada para a Cloudflare?

Uma requisição num isolate V8 consome ~1 ms de CPU e ~3 MB de memória por poucos
milissegundos. Um servidor moderno tem 128 núcleos. Ignorando sobrecarga:

```
128 núcleos × 86.400 s/dia = 11,06 milhões de segundos de CPU por dia
                            = 11,06 bilhões de milissegundos

100.000 requisições/dia × 1 ms = 100.000 ms por usuário gratuito

11,06 bilhões ÷ 100 mil = ~110.000 usuários gratuitos no limite,
                          em UM servidor — se todos usassem a cota inteira.
```

Na prática, **a maioria dos usuários gratuitos usa 1% da cota**, o que multiplica esse número
por cem. O custo marginal de mais um usuário gratuito é, literalmente, frações de centavo.

Agora refaça a conta para um **banco de dados de 1 GB**:

```
1 GB ocupado 24 h/dia, 365 dias/ano, replicado 3× para durabilidade = 3 GB reais,
mais backup, mais o processo Postgres consumindo RAM enquanto existe.

Custo: centavos a poucos dólares por mês — POR USUÁRIO, TODO MÊS, use ele ou não.
```

**É por isso que a computação gratuita é generosa e o armazenamento gratuito é mesquinho.**
Não é maldade; é a estrutura de custo. Guarde esta frase:

> **Cômputo tem custo marginal quase zero e escala a zero. Estado tem custo marginal real e
> nunca escala a zero.**

---

## 3. Por que camadas gratuitas morrem

Cinco causas, em ordem de frequência histórica:

**1. Abuso em escala.** Mineração de criptomoeda, spam, phishing, proxies para contornar
bloqueios. Foi a razão declarada do Heroku em 2022. O padrão é sempre o mesmo: milhares de
contas automatizadas queimam a margem que os poucos pagantes sustentavam.

**2. Mudança do custo do capital.** Entre 2010 e 2021, dinheiro barato financiou generosidade
como estratégia de crescimento. Com a alta de juros de 2022–2023, "crescimento a qualquer
custo" virou "caminho para a lucratividade" — e o plano gratuito é a primeira linha a ser
cortada.

**3. Aquisição.** O comprador tem outra planilha. Heroku sob a Salesforce é o caso didático.

**4. O funil não fecha.** Se usuários gratuitos não viram pagantes numa taxa suficiente, o
plano é marketing que não converte. É a hipótese mais provável para várias mortes de 2025–2026.

**5. Mudança de posicionamento.** A empresa decide mirar o mercado corporativo. Usuário
gratuito deixa de ser cliente potencial e passa a ser custo e ruído no suporte.

---

## 4. Os sinais de que a sua camada gratuita vai acabar

Aprenda a lê-los; eles aparecem meses antes do anúncio.

| Sinal | O que costuma significar |
|---|---|
| Passaram a exigir cartão de crédito "só para verificação" | atrito deliberado para reduzir volume de gratuitos |
| Passaram a exigir verificação por telefone/documento | combate a abuso, com corte de volume como efeito |
| O plano gratuito sumiu da página de preços (mas ainda funciona) | vão descontinuar para novos e depois para todos |
| Criaram um plano intermediário barato (US$ 5) | preparando a migração de quem está no gratuito |
| Reduziram um limite "para melhorar a experiência" | teste de reação antes do corte maior |
| Trocaram limites explícitos por "créditos" | previsibilidade para eles, teto rígido para você (Netlify, abr/2026) |
| A empresa foi comprada | reavaliação garantida |
| Rodada de captação com foco declarado em "eficiência" | corte no gratuito é a fruta mais baixa |

**O que fazer ao ver dois ou mais destes sinais:** não é entrar em pânico. É **verificar que o
seu plano de saída existe** — tem `Dockerfile`? tem `pg_dump` funcionando? o backup está fora
do provedor? Se as três respostas forem sim, a mudança vira um fim de semana chato, não uma
crise.

---

## 5. O custo que não está na fatura

| Custo oculto | Como se manifesta | Como estimar |
|---|---|---|
| **Migração** | 1 a 12 semanas de trabalho | horas × custo/hora, e **multiplique por 2** |
| **Aprisionamento** | você aceita aumento porque sair é pior | veja acima |
| **Egress** | US$ 0,09/GB na AWS; 1 TB = ~US$ 90/mês | GB de saída × preço |
| **Seu tempo de operação** | 0 a 8 h/mês, conforme a camada | horas × custo/hora |
| **Incidente** | queda × receita por hora + confiança | receita/hora × horas, mais o intangível |
| **Curva de aprendizado** | 20 a 200 h por plataforma nova | some ao custo do primeiro ano |
| **Suporte** | US$ 29 a 2.500/mês nos planos sérios | consulte antes de precisar |
| **Câmbio e IOF** | +3,5% de IOF e oscilação de 10–15% ao ano | some 15% à conta em dólar |

> **A conta que quase ninguém faz.** Uma equipe de três pessoas que gasta 6 horas por mês
> operando um VPS para economizar US$ 25/mês está gastando ~R$ 600 de tempo para economizar
> R$ 130. Isso pode valer a pena por outros motivos (aprendizado, controle, soberania) —
> mas **não é economia**, e apresentar como economia é erro de análise.

---

## 6. Como usar camada gratuita com responsabilidade

Um conjunto de regras que resistiu ao teste do tempo:

1. **Use gratuito para o que pode cair.** Frontend, cache, ambiente de testes, laboratório.
2. **Pague pelo que não pode sumir.** Banco de dados. US$ 5 a 25/mês é barato perto de perder
   dados de cliente.
3. **Tenha `Dockerfile`.** Uma tarde de trabalho, anos de opção de saída.
4. **Tenha backup fora do provedor.** Automatizado e **testado**.
5. **Não use serviço proprietário sem exportação** para dado que importa.
6. **Leia os termos sobre uso comercial.** Vercel Hobby e GitHub Pages têm restrição, e
   contas já foram suspensas.
7. **Monitore de fora.** A plataforma não avisa que caiu.
8. **Anote a data de validade.** Render Postgres gratuito expira em 30 dias; créditos da AWS,
   em 6 meses; trial da Railway, em 30 dias. Coloque no calendário no dia em que criar.
9. **Releia esta decisão a cada 6 meses.** Este é o setor que mais muda.

---

## 7. E se você for cobrado sem esperar?

Acontece, e há um caminho.

**Prevenção:**
- prefira plataformas que **pausam em vez de cobrar** no plano gratuito (Vercel Hobby,
  Netlify Free, Cloudflare Free);
- configure **limite de gasto** onde existir (Vercel *Spend Management*, AWS Budgets,
  Railway *usage limits*);
- use um **cartão virtual com limite baixo** para serviços em teste;
- **AWS Budgets com alerta em US$ 1** é o primeiro comando de quem abre conta na AWS.

**Se a cobrança veio:**
1. Descubra a causa exata na fatura detalhada (quase sempre é egress, um recurso esquecido
   ligado, ou um laço que disparou invocações).
2. **Desligue o recurso** antes de discutir.
3. Abra um chamado explicando. **AWS, GCP e Azure costumam perdoar a primeira cobrança
   acidental de conta pequena** — não é direito, é prática comum. Seja educado, objetivo e
   mostre que corrigiu.
4. Documente o que causou, para não repetir.

---

## Autoteste

1. Quais são os seis modelos de sustentação de camada gratuita, e qual é o mais durável?
2. Faça a conta que explica por que 100 mil requisições/dia custam quase nada à Cloudflare.
3. Enuncie a frase sobre cômputo e estado, e explique por que ela decide a generosidade dos planos.
4. Cite quatro causas históricas da morte de camadas gratuitas.
5. Liste cinco sinais de que um plano gratuito vai acabar.
6. Qual é o custo oculto mais caro, e como estimá-lo?
7. Enuncie as nove regras de uso responsável de camada gratuita.
8. O que fazer, na ordem, se você receber uma cobrança inesperada?
