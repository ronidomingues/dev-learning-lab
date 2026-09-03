# 26 · Carreira e mercado — sem consolo

**Nível:** intermediário · **Escrito em:** 20/08/2026

> Este arquivo é opinativo por natureza. Vou marcar claramente o que é dado, o
> que é leitura minha, e o que é incerto. Números de salário no Brasil vêm de
> fontes de qualidade desigual — trate como ordem de grandeza, nunca como
> referência.

---

## 1 · O que evaporou

Seja direto: algumas tarefas que sustentavam posições inteiras deixaram de ter
valor de mercado.

| Tarefa | Situação em 08/2026 |
|---|---|
| CRUD e boilerplate | Praticamente sem valor isolado |
| Conversão de formato, tradução de linguagem | Idem |
| Ajuste de CSS a partir de mockup | Muito barato |
| Teste unitário óbvio | Barato |
| Documentação a partir do código | Barato |
| "Programar o que o analista especificou" | O papel está sendo comprimido |

Isso não significa que essas tarefas não sejam feitas — significa que **ninguém
paga bem por saber fazê-las**, porque a alternativa custa centavos.

---

## 2 · O que ficou mais caro

| Habilidade | Por quê |
|---|---|
| **Especificar** | Virou o gargalo de entrada ([16](16-especificacao-e-plano.md)) |
| **Verificar** | Virou o gargalo de saída ([17](17-verificacao-e-testes.md)) |
| **Depurar sistema em produção** | A IA ajuda pouco: o contexto não está em lugar nenhum |
| **Sistema legado hostil** | Onde não há exemplo público, ela se perde |
| **Arquitetura e fronteiras** | E agora com verificação mecânica ([19](19-arquitetura-para-maquina.md)) |
| **Segurança** | Superfície nova e erro invisível ([22](22-seguranca.md)) |
| **Decidir o que construir** | Nunca foi automatizável, e ficou relativamente mais valioso |
| **Responder por consequência** | Ninguém aceita "o agente escreveu" ([23](23-licenca-propriedade-e-lei.md)) |
| **Formar outras pessoas** | Escassez de quem sabe ensinar o ofício novo |

---

## 3 · O problema do júnior — dito com todas as letras

### O mecanismo

A porta de entrada clássica da profissão era **a tarefa pequena, bem definida e
supervisionada**. Era assim que se aprendia: fazendo muitas delas, errando,
sendo corrigido.

Essa é exatamente a tarefa que a IA faz melhor e mais barato.

O resultado é uma armadilha estrutural:

```
Para ser útil hoje  →  precisa saber julgar código
Para saber julgar   →  precisa ter escrito muito código
Para escrever muito →  precisa de tarefas que hoje vão para a máquina
```

### O que dizem os dados

Aqui é preciso cuidado. Há relatos de contração na contratação júnior em vários
mercados, e há análises que atribuem isso à IA. **Também** houve, no mesmo
período, aperto macroeconômico, correção pós-pandemia e mudanças de taxa de
juros. Separar as causas é difícil, e quem afirma com certeza está vendendo
alguma coisa.

**O que eu observo, marcado como observação:** a barra de entrada subiu. A vaga
que antes pedia "sabe programar" hoje pede "sabe programar e consegue julgar o
que a máquina produz" — que é um degrau a mais, não a menos.

### O que fazer se você é júnior — conselho concreto

Cinco coisas, em ordem de eficácia:

**1. Aprenda a programar de verdade primeiro.** Sem atalho. Se você delega antes
de saber, você nunca vai saber julgar, e vai ficar preso em L2 para sempre. É a
diferença entre usar IA como muleta e usar como alavanca.

**2. Use IA como professor, não como executor.** "Explique por que isso funciona"
ensina; "escreve pra mim" não. Essa é a única forma em que a IA acelera o
aprendizado em vez de impedi-lo.

**3. Pule direto para L3.** A sua vantagem competitiva sobre um sênior que está
em L2 é justamente que você não tem hábito antigo para desaprender. Aprenda a
especificar e verificar **desde o começo** — a maioria dos seniores está tendo
que aprender isso depois de 15 anos fazendo diferente.

**4. Especialize onde a IA é fraca.** Sistemas legados, desempenho, segurança,
sistemas distribuídos, domínio de negócio específico (saúde, financeiro, fiscal,
industrial). São áreas com pouco exemplo público e alta consequência.

**5. Construa portfólio que mostre julgamento, não código.** Um repositório com
portão de verificação, ADRs, testes com mutação e um `README` explicando as
decisões vale mais, hoje, que cinco clones de aplicativos. Qualquer um gera
código; poucos demonstram critério.

> **Recado sem consolo:** está mais difícil, sim. E ainda vale a pena, porque a
> demanda por quem **sabe julgar** não caiu — subiu. O caminho ficou mais íngreme
> na base e mais recompensador no meio.

---

## 4 · O que fazer se você é sênior

O risco do sênior é diferente e menos discutido: **a competência que te trouxe
até aqui é parcialmente a que está desvalorizando.**

Se a sua vantagem era escrever código bom rápido, ela encolheu. Se era saber
**o que** escrever e **como provar que está certo**, ela cresceu.

Cinco movimentos:

1. **Migre de L2 para L3 deliberadamente.** Não presuma que anos de experiência
   te colocam em L4 automaticamente — a METR mediu justamente seniores ficando
   mais lentos.
2. **Invista no repositório, não em técnicas de prompt.** É onde o retorno é
   composto ([19](19-arquitetura-para-maquina.md)).
3. **Assuma a formação.** A escassez real é de quem sabe **ensinar** o ofício
   novo. Isso é alavancagem organizacional.
4. **Aprenda a medir.** Quem consegue dizer "nosso tempo de revisão subiu 40% e
   aqui está o que vamos fazer" tem influência; quem tem opinião sobre IA, não.
5. **Não vire o cético de plantão.** Ceticismo bem fundamentado é valioso;
   ceticismo como identidade é obsolescência com boa retórica.

---

## 5 · Cargos e o que eles realmente são

| Cargo anunciado | O que geralmente é |
|---|---|
| **AI Engineer** | Constrói produtos **com** modelos (RAG, agentes, avaliação). Diferente deste curso — ver [agentes-de-ia](../agentes-de-ia/00-MAPA.md) |
| **Prompt Engineer** | Cargo em declínio como título isolado; a habilidade foi absorvida. Ver [engenharia-de-prompt](../engenharia-de-prompt/00-MAPA.md), arquivo `40-a-profissao` |
| **ML Engineer** | Treina e serve modelos. Outra profissão |
| **Software Engineer (AI-assisted)** | O que este curso trata. Cada vez mais, "Software Engineer" sem adjetivo |
| **Developer Experience / Platform** | **Subvalorizado e em alta.** Quem constrói o ambiente onde os agentes funcionam bem |
| **Agent Ops / AI Enablement** | Cargo emergente: política, portão, custo, formação. Ainda sem definição estável |

> **Aposta minha, marcada como aposta:** "AI-assisted" vai desaparecer do título
> em dois ou três anos, do mesmo jeito que "programador de internet" desapareceu.
> Vai virar o padrão. Quem se posicionar como especialista em *usar IA* terá um
> diferencial de prazo curto; quem se posicionar como especialista em
> **especificar e verificar** terá um diferencial durável.

---

## 6 · Mercado brasileiro — ordens de grandeza, com ressalva

**Ressalva forte:** os números abaixo vêm de agregadores e pesquisas de
consultoria de qualidade desigual, consultados em 20/08/2026. Há grande
dispersão entre fontes, entre regiões e entre empresas. Use como **ordem de
grandeza** para calibrar expectativa, nunca como referência para negociação.

| Faixa (CLT, mensal, aproximada) | Observação |
|---|---|
| Dev júnior tradicional | R$ 3.000 – 6.000 |
| Dev pleno | R$ 7.000 – 14.000 |
| Dev sênior | R$ 14.000 – 25.000 |
| Engenharia de IA (júnior) | R$ 8.000 – 12.000 |
| Engenharia de IA (sênior) | R$ 25.000 – 45.000 |

Contexto estrutural que importa mais que os números: o Brasil forma cerca de
53 mil profissionais de TI por ano contra uma demanda estimada em ~159 mil.
**O déficit é de gente qualificada, não de gente.** Isso significa que a barra
de entrada sobe sem que a demanda caia — o pior cenário para quem está entrando
e o melhor para quem consegue atravessar.

E o fator que domina tudo: **trabalho remoto para o exterior**. Um dev brasileiro
em L4 competindo por vaga remota internacional acessa uma faixa salarial
descolada do mercado local. Esse é, na minha leitura, o maior retorno disponível
sobre subir de nível — maior que qualquer negociação interna.

---

## 7 · O que colocar no currículo

**Não coloque:**

- "Experiência com ChatGPT / Copilot / Cursor." Todo mundo tem. Não diferencia.
- "Prompt engineering" como habilidade isolada.
- "Aumentei minha produtividade em 10× com IA." Ninguém acredita, e com razão.

**Coloque:**

- "Reduzi o tempo da suíte de testes de 22 para 4 minutos, o que viabilizou
  delegação com verificação automática."
- "Implantei portão de verificação (escopo, segredos, dependências, cobertura do
  diff) que reprovou N mudanças antes do merge."
- "Migrei 400 componentes com pipeline agente + portão + amostragem estratificada;
  3 semanas estimadas viraram 4 dias, com revisão humana em 100% do código que
  toca pagamento."
- "Reduzi o tempo médio até a primeira revisão de 18 h para 4 h ao instituir
  limite de tamanho de PR."

**O padrão:** resultado mensurável, mecanismo explicado, honestidade sobre o
escopo. É o mesmo padrão que o curso defende para tudo o mais.

---

## Autoteste

1. Cite quatro tarefas que perderam valor de mercado e explique por quê.
2. Cite quatro habilidades que ficaram mais caras e o motivo de cada uma.
3. Descreva a armadilha estrutural do júnior em três linhas.
4. Por que é difícil atribuir a contração na contratação júnior só à IA?
5. Cite os cinco conselhos para júnior, em ordem de eficácia.
6. Qual é o risco específico do sênior, e por que anos de experiência não
   garantem nível alto?
7. Qual é a diferença entre "AI Engineer" e o profissional deste curso?
8. Qual é a aposta sobre o título "AI-assisted", e qual posicionamento é
   durável?
9. Por que o déficit brasileiro de 53 mil formados contra 159 mil de demanda é
   o pior cenário para quem entra e o melhor para quem atravessa?
10. Reescreva "experiência com Copilot" no formato recomendado para currículo.

---

**Anterior:** [25-niveis-do-dev-com-ia](25-niveis-do-dev-com-ia.md) ·
**Próximo:** [27-times-e-organizacao](27-times-e-organizacao.md)
