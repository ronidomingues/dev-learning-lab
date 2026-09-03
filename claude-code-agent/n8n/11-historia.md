# 11 · História — de onde veio isso e por quê

`Nível: intermediário` · `Pesquisado na web em 01/09/2026`

---

Entender a história do campo não é curiosidade: é o que permite reconhecer, em
2026, qual moda vai passar e qual mudança é estrutural.

---

## 1. A pré-história: EAI e ESB (1990–2005)

O problema é antigo. Nos anos 1990, uma empresa média já tinha ERP, CRM, folha de
pagamento e sistema de estoque, comprados de fornecedores diferentes, e nenhum
falava com o outro. Cada par de sistemas conectado exigia um programa próprio.
Com N sistemas, você tinha até N×(N−1)/2 conexões. Dez sistemas = 45 integrações.

A resposta da indústria foi o **ESB** (*Enterprise Service Bus*, barramento de
serviços corporativo): em vez de todo mundo falar com todo mundo, todos falam com
um barramento central que traduz. TIBCO, webMethods, IBM MQ/ESB, Oracle Fusion,
Mule ESB. Reduziu N² para N.

**Por que caiu em desuso?** Três razões, e a terceira é a que interessa:
1. O barramento virou um monólito: uma mudança exigia mexer no centro.
2. O custo era proibitivo — licenças de seis dígitos e consultoria obrigatória.
3. **A web mudou o problema.** Com REST e JSON, o transporte deixou de ser difícil.
   O que restou de difícil foi *autenticação, paginação e semântica*. Um barramento
   pesado resolvia o problema errado.

O ESB não morreu: virou *iPaaS* (*integration Platform as a Service*) — a mesma
ideia, na nuvem, por assinatura. MuleSoft, Boomi, Workato, Celigo.

## 2. A ideia visual: Yahoo Pipes (2007–2015)

**Yahoo Pipes** (fev/2007) foi o primeiro produto de massa com a interface de
"caixas ligadas por fios" para dados da web: pegue este RSS, filtre por palavra,
junte com aquele, publique. Não vingou comercialmente — o Yahoo o desligou em
setembro de 2015 —, mas fixou o vocabulário visual que praticamente todo mundo
copiou depois, inclusive o n8n.

**A linhagem é ainda mais antiga.** A ideia de *dataflow programming* — programa
como grafo de operadores ligados por canais de dados — é dos anos 1960–70
(a tese de Jack Dennis no MIT, LabVIEW da National Instruments em 1986, Max/MSP
para áudio em 1988). O n8n não inventou o paradigma; ele o aplicou a APIs web.

## 3. O mercado de massa: IFTTT e Zapier (2010–2019)

- **IFTTT** (2010) — "*if this then that*". Um gatilho, uma ação. Simples ao ponto
  de ser limitado, e voltado ao consumidor final.
- **Zapier** (2011) — o mesmo modelo, mas para trabalho: milhares de aplicativos,
  fluxos lineares, preço por tarefa executada. Provou que existia um mercado enorme
  de gente que precisa integrar e não vai programar.
- **Integromat** (2012, depois **Make**) — trouxe o canvas visual com ramificações
  e iteradores, mais poderoso que o Zapier.
- **Microsoft Flow / Power Automate** (2016) — a mesma ideia dentro do Office 365.

Todos com uma característica comum: **fechados e na nuvem de terceiros**. Seus
dados, suas chaves de API e sua lógica de negócio rodando na infraestrutura deles.

## 4. n8n: 2019 até hoje

| Data | Marco |
|---|---|
| **Início de 2019** | **Jan Oberhauser** começa a escrever o n8n no apartamento dele, em Berlim |
| **4 de outubro de 2019** | Código publicado no GitHub. Fundador solo |
| **Março de 2020** | Seed de **US$ 1,5 milhão**, co-liderada por Sequoia Capital e firstminute capital |
| **Abril de 2021** | Série A de **US$ 12 milhões**, liderada pela Felicis Ventures |
| **2022–2024** | Crescimento constante; o produto ganha queue mode, RBAC, projetos, e o ecossistema de nós explode |
| **2023** | Chegam os nós de **LangChain**: AI Agent, Chat Model, Vector Store, Memory |
| **Março de 2025** | Série B de **€ 55 milhões (≈ US$ 60 mi)**, liderada pela Highland Europe |
| **Outubro de 2025** | Série C de **US$ 180 milhões**, liderada pela Accel, avaliando a empresa em **US$ 2,5 bilhões**. Total captado: ~US$ 240 milhões |
| **2026** | **n8n 2.0**: endurecimento — Python nativo substitui Pyodide, binário sai da memória, `Publish` separado do `Save`, pooling de SQLite |
| **Outubro de 2026 (anunciado)** | **n8n 3.0**: instalação **só por Docker**; remoção dos nós Function/Function Item/Item Lists, do AI Agent v1 e de `$getPairedItem` |

**A virada que explica a avaliação de US$ 2,5 bilhões não foi a automação — foi a IA.**
Entre 2023 e 2025, "orquestrar chamadas de API" e "orquestrar agentes de IA"
revelaram-se o **mesmo problema técnico**: encadear passos, tratar erro, manter
estado, chamar ferramentas externas. O n8n já tinha o motor; só precisou de nós
novos. Ferramentas nascidas para automação de escritório viraram, sem se
reposicionar, plataformas de agentes.

## 5. A decisão que definiu o produto: a licença

O n8n **não é software livre** no sentido da OSI. Ele usa a **Sustainable Use
License**, que autoriza uso e modificação "apenas para fins internos de negócio ou
uso pessoal/não comercial", e distribuição apenas gratuita e não comercial.

Isso é chamado de **fair-code** — termo cunhado pela própria n8n: código aberto para
ler e estender, com restrições comerciais definidas pelo autor.

*Por que fizeram isso?* Trade-off econômico explícito. O modelo puramente open
source tinha um problema conhecido: um provedor de nuvem grande pega o código,
vende como serviço gerenciado, e quem escreveu não vê um centavo (foi o que
aconteceu com Elasticsearch, MongoDB e Redis, todos os quais mudaram de licença
pelo mesmo motivo). A Sustainable Use License bloqueia exatamente esse caso,
mantendo tudo o mais aberto.

*O preço dessa escolha:* o n8n não pode ser chamado de open source sem ressalva,
não entra em repositórios de distribuições que exigem licenças OSI, e cria uma
zona cinzenta para agências e consultorias. Detalhes práticos, com o que pode e o
que não pode, em [80-custos-e-licencas.md](80-custos-e-licencas.md).

## 6. O que a história ensina (opinião profissional, marcada como tal)

1. **A interface visual sobreviveu; o barramento central não.** Toda tentativa de
   centralizar a integração num componente único falhou por acoplamento. O que
   sobreviveu foi a *representação* visual, que é sobre comunicação humana.
2. **O ciclo se repete a cada 10 anos com nome novo:** EAI → ESB → SOA → iPaaS →
   low-code → agentes de IA. O problema é o mesmo desde 1995: sistemas que não se
   falam. Desconfie de quem promete que desta vez é diferente.
3. **A pergunta certa nunca foi "visual ou código?"**, e sim "onde fica a
   fronteira?". Quem tenta fazer tudo no visual produz monstros; quem despreza o
   visual reescreve encanamento a vida inteira. O ponto de equilíbrio, na minha
   experiência: **o visual expressa a topologia; o código expressa a transformação.**
4. **A autogestão foi de nicho a diferencial.** Em 2019 parecia teimosia; com LGPD,
   GDPR, dados de saúde e agora com prompts e dados de clientes indo para modelos
   de IA, virou requisito contratual em muitos setores.

---

## Autoteste

1. Qual problema o ESB resolvia, e por que a matemática N×(N−1)/2 importa?
2. Por que o ESB caiu em desuso? Cite as três razões, com destaque para a terceira.
3. O que foi o Yahoo Pipes e o que ele deixou de herança?
4. De que década vem a ideia de *dataflow programming*? Cite dois exemplos anteriores à web.
5. Que característica o Zapier, o IFTTT, o Make e o Power Automate têm em comum e o
   n8n não tem?
6. Quando o n8n foi publicado no GitHub, e por quem?
7. Qual foi a avaliação da Série C e o que ela realmente estava precificando?
8. Por que a n8n escolheu uma licença que não é OSI? Que precedente do mercado
   justifica a escolha?
9. Explique por que "orquestrar APIs" e "orquestrar agentes de IA" são o mesmo
   problema de engenharia.

---

*Fontes consultadas em 01/09/2026: [Wikipedia — n8n](https://en.wikipedia.org/wiki/N8n),
[PitchBook — Série C](https://pitchbook.com/news/articles/ai-agent-startup-n8n-lands-2-5b-valuation-with-180m-series-c),
[n8n LICENSE.md no GitHub](https://github.com/n8n-io/n8n/blob/master/LICENSE.md),
[docs.n8n.io — changelog v2.0 e v3.0](https://docs.n8n.io/changelog).*

*Anterior: [10-fundamentos.md](10-fundamentos.md) · Próximo: [12-o-modelo-de-dados.md](12-o-modelo-de-dados.md)*
