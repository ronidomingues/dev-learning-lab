# 65 · Estado da arte — agosto de 2026

`Nível: pesquisa` · `Pesquisado na web em 31/08/2026` · **Este arquivo envelhece rápido. Reavalie a cada 6 meses.**

> O que mudou de fato, o que só mudou no marketing, o que está em aberto, e o que já morreu.

---

## 65.1 O que realmente mudou desde 2022

| Mudança | Impacto real | Confiança |
|---|---|---|
| **LLMs como parceiro de conversa disponível 24 h** | ⭐ **grande** — resolve o gargalo histórico de "não tenho com quem praticar" | alta |
| **Geração de insumo sob medida por nível** | ⭐ grande — texto e diálogo em qualquer assunto, calibrado por nível CEFR, em segundos | alta |
| **Transcrição automática quase perfeita** | grande — qualquer áudio do mundo virou material com transcrição | alta |
| **Avaliação automática de pronúncia por fonema** | médio — útil como retorno, imperfeito | média |
| **Tradução automática de qualidade alta** | ambíguo — ver §65.5 | alta |
| **CEFR Companion Volume (2020) consolidado** | médio — mediação e interação online entraram nos currículos | alta |
| **FSRS substituindo SM-2 na repetição espaçada** | médio — ~20–30% menos revisões para a mesma retenção | alta |
| **Consolidação de exames online** (DET, Linguaskill) | médio — barateou e agilizou a certificação | alta |

---

## 65.2 O que a pesquisa diz sobre IA no aprendizado de idiomas

Este é o ponto quente de 2026 e o mais sujeito a exagero. Separando:

### O que tem apoio razoável

- **Redução de ansiedade.** Praticar com uma IA que não julga reduz a ansiedade de fala, e a
  ansiedade é um bloqueador documentado ([60](60-teoria-avancada.md) §60.10). Efeito plausível e
  relatado consistentemente.
- **Volume de produção.** Um aprendiz com acesso a um interlocutor ilimitado produz muito mais.
  Como produção é um gargalo real ([10](10-fundamentos.md) §10.6), isso deve ajudar.
- **Insumo calibrado.** Gerar texto de nível A2 sobre o assunto que você gosta ataca diretamente
  o problema do `i+1` — historicamente resolvido com material didático genérico e chato.
- **Explicação sob demanda.** Perguntar "por que aqui é *for* e não *since*?" e receber resposta
  imediata acelera a percepção (interface fraca, §60.4).

### O que é frágil ou não sustentado

⚠️ **Limitação documentada e séria:** avaliações de tutores conversacionais baseados em LLM
apontam que eles **priorizam fluência sobre correção** e **deixam passar erros gramaticais
sutis** — ou seja, podem **reforçar** o erro do aprendiz em vez de corrigi-lo, exatamente o
mecanismo da fossilização (§60.9). Um interlocutor que sempre entende você não gera pressão
comunicativa para melhorar.

⚠️ **Alegações de mercado sem base:** afirmações do tipo "fluência conversacional em 6–8 meses
com IA versus 12–18 meses no método tradicional" circulam em blogs comerciais e **não têm estudo
controlado por trás**. As horas necessárias (§2.4) não mudaram porque a tecnologia mudou; o que
mudou foi a **facilidade de acumular** essas horas.

⚠️ **Ausência de estudos longitudinais.** Praticamente toda a evidência sobre tutores LLM é de
curto prazo (semanas), amostra pequena, e mede ganho em testes imediatos. O campo não tem, em
2026, um estudo robusto de um ano comparando IA com professor humano.

### Como usar IA sem se prejudicar — recomendações operacionais

| Faça | Não faça |
|---|---|
| pedir **correção explícita**: *"Correct every grammar mistake I make, list them at the end"* | conversar sem pedir correção e achar que está sendo corrigido |
| pedir alternativas naturais: *"How would a native say this?"* | aceitar a primeira formulação como "a" correta |
| gerar insumo calibrado: *"Write a 300-word text at B1 level about Kubernetes"* | pedir tradução e estudar a tradução |
| usar como **parceiro de fala** para volume | usar **em vez de** falar com pessoas |
| pedir explicação de um erro seu | pedir que escreva o texto por você |
| verificar em corpus (SkELL) o que a IA afirmou sobre uso | tomar afirmação de LLM sobre frequência ou naturalidade como fato |

> **Minha recomendação profissional:** a IA é o **melhor parceiro de treino** já disponível e um
> **péssimo juiz do seu progresso**. Use-a para volume, insumo e explicação; use pessoas e corpus
> para calibrar o que é natural; e use exames externos para medir o nível.

---

## 65.3 Ferramentas: o panorama em agosto de 2026

| Categoria | Estado | Observação |
|---|---|---|
| **Repetição espaçada** | Anki 26.08.1, FSRS consolidado | gratuito e insuperado; ver [03](03-instalacao.md) |
| **Apps de curso** | Duolingo com camada de IA (Video Call, Roleplay no plano Max); *Explain My Answer* passou a ser gratuito em jan/2026 | úteis para hábito e A1–A2; insuficientes sozinhos acima disso |
| **Tutores LLM** | maduros para conversação e explicação | ver ressalvas §65.2 |
| **Avaliação de pronúncia** | análise por fonema disponível em vários apps | útil como retorno, não como veredito |
| **Legendas e imersão** | Language Reactor, asbplayer, Migaku | maduro |
| **Correção de escrita** | LanguageTool (aberto, self-hostable), Grammarly, LLMs | LanguageTool local para texto sensível |
| **Corpora públicos** | SkELL, COCA, iWeb, Youglish | ⭐ subutilizados; são a fonte objetiva sobre uso real |
| **Exames** | DET (US$ 70) barateou o acesso; Linguaskill; EF SET gratuito | ver [85](85-cursos-e-certificacoes.md) |

---

## 65.4 O que continua igual — e é o mais importante deste arquivo

Nenhuma dessas coisas mudou com a IA:

1. **As horas.** ~600 horas guiadas até B2 continuam sendo ~600 horas. A tecnologia mudou a
   **qualidade e a disponibilidade** do contato, não a quantidade necessária.
2. **A necessidade de insumo compreensível abundante.** Continua sendo o motor.
3. **A necessidade de produção com feedback.** Continua.
4. **A ordem natural de aquisição.** Nenhuma tecnologia acelera o `-s` da terceira pessoa.
5. **O gargalo da escuta.** Segmentação e formas reduzidas continuam exigindo exposição maciça.
6. **A constância bate a intensidade.** Continua.
7. **A curva logarítmica.** O platô B1→B2 continua lá.

> Toda vez que alguém anunciar que a tecnologia X "revoluciona o aprendizado de idiomas", teste a
> alegação contra esta lista de sete. Nenhuma tecnologia até agosto de 2026 mexeu em nenhum dos
> sete itens.

---

## 65.5 A pergunta desconfortável: vale a pena aprender inglês na era da tradução automática?

Alegação corrente: com tradução simultânea de alta qualidade, aprender língua vira hobby.

**Argumentos a favor:** a tradução escrita é boa o bastante para consumo de conteúdo; a legendagem
automática funciona; a tradução de fala em tempo real já é usável em cenários simples.

**Argumentos contra — e eu os considero decisivos, para o inglês especificamente:**

1. **Latência e fluidez social.** Conversa real é negociação em tempo real, com sobreposição,
   humor e interrupção. Tradução mediada quebra o ritmo, e o custo social disso é alto.
2. **Confiança e responsabilidade.** Em contexto profissional, jurídico ou médico, ninguém assina
   embaixo de uma tradução automática. A responsabilidade continua sendo de quem entende.
3. **Assimetria de poder na sala.** Quem depende de tradução participa menos, é interrompido mais,
   e é lido como menos competente — justo ou não. Isso é observável em qualquer reunião mista.
4. **O inglês é a língua da fonte.** Documentação, papers, discussão técnica, código e comentário
   nascem em inglês. Ler traduzido é sempre ler com atraso e com perda.
5. **Custo de oportunidade invertido.** Aprender inglês nunca foi tão barato: material infinito e
   gratuito, parceiro de conversa disponível. O denominador da razão custo/benefício despencou.

**Minha posição, declarada como opinião profissional:** para **outras** línguas, o argumento da
tradução automática tem força real — pode não valer a pena aprender norueguês para uma viagem.
Para o **inglês**, não tem: ele é a língua de acesso ao conhecimento e ao trabalho, e mediação
custa caro exatamente nos momentos em que mais importa.

---

## 65.6 O que está morto ou morrendo

| Prática | Status | O que a substituiu |
|---|---|---|
| Método de tradução gramatical (traduzir textos como base do curso) | ☠️ morto desde os anos 1970 | insumo + uso |
| Método audiolingual ("repita depois de mim", laboratório de línguas) | ☠️ morto | prática comunicativa |
| Ensinar sem áudio, só escrita | ☠️ morto | tudo com som desde o dia 1 |
| Listas de vocabulário descontextualizado | 🪦 morrendo | frases e chunks ([20](20-vocabulario.md) §20.5) |
| "Estilos de aprendizagem" | ☠️ refutado, ainda vendido | ver [60](60-teoria-avancada.md) §60.10 |
| Perseguir sotaque nativo como meta | 🪦 morrendo | inteligibilidade internacional (ELF) |
| CD-ROM, fita, laboratório de idiomas | ☠️ morto | qualquer celular |
| SM-2 como agendador padrão | 🪦 sendo substituído | FSRS |
| Aula particular como **única** fonte de contato | 🪦 caro e insuficiente | aula + volume de insumo próprio |
| Cursos de anos em escola de idiomas como único caminho | 🪦 questionado | autodidatismo estruturado + conversação paga pontual |

---

## 65.7 Problemas em aberto (2026)

Se você fizesse pesquisa em SLA hoje, estas são as fronteiras:

1. **Interface explícito↔implícito.** Ainda sem resolução. Falta uma medida boa de conhecimento
   implícito que não seja contaminada pelo explícito.
2. **O que exatamente limita o adulto.** Plasticidade, interferência da L1, volume de insumo e
   identidade atuam juntos; ninguém separou as contribuições.
3. **Eficácia real de tutores LLM no longo prazo.** Nenhum estudo longitudinal robusto até agosto
   de 2026. É a lacuna mais gritante do campo agora.
4. **Modelagem individual.** Aptidão, memória de trabalho e motivação predizem parte da variância;
   a maior parte segue inexplicada.
5. **Medidas de fluência que se transfiram.** Ganho medido em laboratório frequentemente não
   aparece em uso real.
6. **Norma para ELF.** Se a maioria dos falantes é não-nativa, o que é "correto"? Deve o exame
   avaliar pela norma nativa? Debate aberto, com consequências práticas em certificação.
7. **Replicação.** Quanto da literatura pré-2015 sobrevive a replicação com poder estatístico
   adequado? Os primeiros resultados do movimento de replicação sugerem que tamanhos de efeito
   caem.

---

## 65.8 Previsões, declaradas como especulação

Sem valor de fato. Marcadas para você poder cobrar depois.

| Previsão | Confiança |
|---|---|
| Tutor LLM vira padrão de fato para prática de fala em 2–3 anos | alta |
| Exames de proficiência migram para adaptativo com IA, e o preço cai | média |
| Aparece nos próximos anos o primeiro estudo longitudinal sério sobre tutores LLM — e o resultado será "ajuda, mas menos do que o marketing diz" | média |
| Escolas de idiomas presenciais encolhem; conversação com humano vira serviço premium pontual | média-alta |
| Nada disso muda o número de horas necessárias | ⭐ alta |

---

## Fontes consultadas (31/08/2026)

- Avaliação de tutores conversacionais com LLM (estudo de métodos mistos): https://arxiv.org/pdf/2508.05156
- Duolingo Max — Video Call e Roleplay; *Explain My Answer* gratuito a partir de jan/2026:
  https://duolingo.fandom.com/wiki/Duolingo_Max · https://fastcompanybrasil.com/news/duolingo-lanca-recursos-de-ia-em-plano-max-veja-quanto-custa-no-brasil/
- Eficácia de cursos do Duolingo em leitura e escuta (CALICO Journal): https://utppublishing.com/doi/10.1558/cj.26704
- CEFR Companion Volume 2020 (Conselho da Europa): https://rm.coe.int/common-european-framework-of-reference-for-languages-learning-teaching/16809ea0d4
- FSRS — algoritmo e dados de treino: https://github.com/open-spaced-repetition/fsrs4anki
- Anki 26.08.1: https://apps.ankiweb.net/
- Duolingo English Test — preço e mapeamento para o CEFR: https://englishtest.duolingo.com/

*Alegações de blogs comerciais sobre "fluência em 6–8 meses com IA" foram encontradas na pesquisa
e estão registradas aqui como **não sustentadas por estudo controlado**.*

---

## Autoteste

1. Cite três mudanças reais desde 2022 e uma que é mais marketing que substância.
2. Qual é a limitação documentada mais séria dos tutores LLM, e a que fenômeno da §60.9 ela se liga?
3. Como pedir correção a uma IA de forma que ela realmente corrija?
4. Liste os sete pontos que **não** mudaram. Por que essa lista é útil?
5. Dê os cinco argumentos contra "não vale mais a pena aprender inglês".
6. Por que o argumento da tradução automática é mais forte para o norueguês que para o inglês?
7. Cite três práticas mortas e o que as substituiu.
8. Quais são os três problemas em aberto que você considera mais consequentes?
9. Por que a crise de replicação importa para quem só quer aprender inglês?

**Próximo:** [70-pratica.md](70-pratica.md).
