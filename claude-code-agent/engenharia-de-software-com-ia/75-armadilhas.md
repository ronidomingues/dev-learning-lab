# 75 · Armadilhas, mitos e más práticas

**Nível:** intermediário · **Escrito em:** 20/08/2026

---

## Parte I — 24 armadilhas

### Sobre delegação

**1. Delegar o que você não sabe avaliar.**
A violação da regra de ouro. Sintoma: aprovar porque "parece certo".
*Correção:* a pergunta operacional — "se voltar sutilmente errado, eu percebo?"

**2. Pedidos grandes demais.**
A probabilidade de acerto cai com o tamanho **e** a sua capacidade de revisar cai
junto. As duas curvas descem ao mesmo tempo.
*Correção:* regra do diff revisável — 10 minutos.

**3. Não dizer o que não fazer.**
Sem "fora de escopo", você recebe CLI, README, Dockerfile e refatoração.
*Correção:* escopo negativo explícito, e `git diff --stat` antes de ler.

**4. Aceitar o relato em vez do resultado.**
"Os testes passam" é texto gerado, não saída de comando.
*Correção:* rode você. É um comando.

**5. Insistir em contexto contaminado.**
Duas correções sem progresso e você está pagando para piorar.
*Correção:* `git checkout .` e sessão nova.

**6. Sessão eterna.**
Contexto poluído, custo alto, atenção degradada.
*Correção:* uma tarefa, uma sessão. `ESTADO.md` entre elas.

**7. Delegar transformação determinística.**
`sed` é mais rápido, mais barato e reprodutível.
*Correção:* peça ao agente a **regra**, não a aplicação.

**8. Deixar o agente resolver conflito de merge.**
Ele escolhe o lado mais completo, não o correto. Já apagou correção de segurança.
*Correção:* conflito é sempre seu.

### Sobre verificação

**9. Confiar em teste gerado sem verificar o teste.**
`assert x is not None` passa sempre.
*Correção:* teste de mutação, ao menos uma vez, à mão.

**10. Cobertura como métrica de qualidade.**
Mede execução, não detecção.
*Correção:* cobertura **do diff** + mutação nos módulos críticos.

**11. Portão sem verificação de integridade do portão.**
Se "testes passam" é o alvo, alterar o teste é a otimização.
*Correção:* verifique que os testes não mudaram; procure `skip`, `ignore`, `any`.

**12. Suíte lenta.**
Acima de 10 minutos o agente para de rodar e passa a adivinhar.
*Correção:* Lab 6 do [70-pratica](70-pratica.md).

**13. Portão que bloqueia tudo.**
Fadiga de alerta → desativação → nenhum portão.
*Correção:* duas severidades. Bloqueie o objetivo e caro; avise o heurístico.

**14. Revisar código antes de revisar os testes.**
Se os testes são decorativos, o resto da revisão é teatro.
*Correção:* teste primeiro, sempre.

### Sobre segurança

**15. Agente com acesso a `.env`.**
Credencial no contexto, no log do provedor, no histórico da sessão.
*Correção:* `deny` de leitura + não ter segredo de produção na máquina.

**16. Instalar pacote sugerido sem verificar.**
~20% das amostras geradas citam pacote inexistente.
*Correção:* lockfile, `npm ci`, portão de dependência.

**17. Ignorar injeção indireta porque "não vai acontecer comigo".**
CVEs com CVSS acima de 9 em 2025–2026 dizem o contrário.
*Correção:* trinca letal — remova uma das três pernas.

**18. Conectar MCP sem ler.**
Cada servidor é código de terceiro com o seu contexto.
*Correção:* oficial, versão fixa, um por necessidade real.

**19. `--dangerously-skip-permissions` fora de container.**
*Correção:* autonomia total exige raio de explosão finito.

### Sobre organização

**20. Adotar antes de instrumentar.**
Comprar licença e esperar ganho, sem portão nem teste.
*Correção:* medir → consertar o gargalo → instrumentar → adotar.

**21. Aumentar a produção sem aumentar a revisão.**
+98% de PRs, +91% de tempo de revisão, ~10% de ganho líquido.
*Correção:* limite de tamanho de PR e revisão proporcional ao risco.

**22. Medir "percentual de código de IA".**
Inflável, sem correlação com valor, e incentiva o comportamento errado.
*Correção:* vazão da `main`, estabilidade, tempo de revisão.

**23. Não medir duplicação.**
+81% desde 2023, e ninguém olha.
*Correção:* `jscpd`/SonarQube no CI, com tendência.

**24. Sem política escrita.**
Cada um inventa a sua; a mais permissiva define o risco de todos.
*Correção:* uma página, oito perguntas ([27](27-times-e-organizacao.md)).

---

## Parte II — 14 mitos

### Mito 1 · "IA vai substituir programadores"

**Por que persiste:** vende manchete, ação e curso.
**O que é verdade:** a tarefa média, bem definida e com muito exemplo público
está evaporando. A porta de entrada estreitou.
**O que é falso:** o ofício acabou. Especificar, verificar e responder por
consequência não são automatizáveis — o último por razão estrutural, não
técnica ([60](60-teoria-avancada.md)).

### Mito 2 · "Prompt engineering é a habilidade do futuro"

**Por que persiste:** foi verdade em 2023 e virou identidade profissional.
**O que é verdade:** saber comunicar intenção com precisão sempre importa.
**O que é falso:** técnicas de prompt são a habilidade. Cada geração de modelo
torna prompt elaborado menos necessário. Persona e "pense passo a passo" já são
obsoletos.

### Mito 3 · "Não precisa mais aprender a programar"

**O que é falso:** você não consegue julgar o que não entende. Sem julgamento,
teto em L2, permanente.
**A ironia:** IA é excelente **professora** de programação, se você pedir
explicação em vez de solução.

### Mito 4 · "A IA me deixa 10× mais rápido"

**O que a evidência diz:** ~10% de ganho líquido organizacional em times com
adoção intensa (LinearB); ganho muito desigual por tipo de tarefa; e devs
experientes erraram o **sinal** da própria estimativa (METR).
**O que é verdade:** em tarefas específicas — boilerplate, tradução de formato,
código novo em área conhecida — o ganho é enorme.

### Mito 5 · "A IA escreve código melhor que o meu"

**O que é verdade:** ela escreve código mais **idiomático** e mais **completo**
que o seu apressado das 18h de sexta.
**O que é falso:** "melhor". Ela não conhece o seu sistema, o seu negócio nem as
suas restrições. Bom código é código certo **para o contexto**.

### Mito 6 · "Testes gerados por IA são suficientes"

Quatro padrões de falha documentados no [17](17-verificacao-e-testes.md). Um
teste tautológico é pior que nenhum: dá licença para não pensar.

### Mito 7 · "Janela de 1 milhão resolve o contexto"

**O que é falso:** atenção não é uniforme; encher a janela piora o resultado; e
custo é dominado por tokens de entrada reenviados a cada passo.

### Mito 8 · "Modelo local resolve privacidade e custo"

**O que é verdade:** resolve privacidade, quando ela é requisito absoluto.
**O que é falso:** que seja competitivo em trabalho agêntico em hardware de
consumo, ou mais barato considerando hardware, energia e tempo de engenharia.

### Mito 9 · "Basta escrever um prompt melhor"

**O que é falso** para: alucinação (não há sinal interno), injeção indireta (não
há autenticação de origem no contexto), aritmética exata (tokens não são
números), fatos posteriores ao treino (não estão nos pesos).
**Regra:** se o problema é estrutural, a solução é arquitetural.

### Mito 10 · "Vibe coding é o futuro do trabalho profissional"

**O que é verdade:** é ótimo para protótipo descartável, prova de ideia, script
de uma vez, aprender biblioteca nova.
**O que é falso:** que sirva para código que alguém vai manter. Troca custo de
escrita por custo de manutenção — bom negócio se o código morre amanhã, péssimo
se vive cinco anos.

### Mito 11 · "Agentes autônomos substituem o processo de engenharia"

**O que é falso:** eles **exigem mais** processo, não menos. Autonomia sem
portão é aposta. O DORA é claro: o retorno vem do sistema organizacional.

### Mito 12 · "SDD resolve o problema da deriva"

**O que é verdade:** ataca a causa certa e a prática vale.
**O que é falso:** que seja resolvido. É a terceira tentativa histórica da mesma
ideia, e a divergência espec-código após edição manual continua sem solução.

### Mito 13 · "Benchmarks dizem qual modelo usar"

**O que é falso:** benchmarks saturam, contaminam-se, e não representam o seu
código. Pior: em 2026, muitas "tabelas de benchmark" na web são geradas por IA e
**contêm números falsos**.
**O que fazer:** Lab 12 do [70-pratica](70-pratica.md) — o seu próprio conjunto.

### Mito 14 · "Se os testes passam, pode fundir"

**O que é falso:** os testes verificam o que alguém pensou em verificar. Não
pegam duplicação, decisão arquitetural ruim, requisito mal entendido, ou o
problema errado resolvido perfeitamente.

---

## Parte III — as três armadilhas de longo prazo

Estas não doem hoje. Doem em 18 meses.

### A · Erosão de competência

**O mecanismo:** julgamento é músculo. Se você nunca escreve, nunca depura,
nunca lê código com esforço, a capacidade de **avaliar** atrofia. E avaliar é a
única coisa que sustenta o seu valor.

**O ciclo vicioso:**
```
delego mais → escrevo menos → julgo pior → delego mais porque
"não sei fazer" → julgo ainda pior
```

**Contramedidas:**
- Uma tarefa por semana **inteiramente à mão**, deliberadamente.
- Ao aprender algo novo, escreva a primeira versão sozinho.
- Pergunte "por quê" em vez de "faça".
- Depure sem ajuda antes de pedir ajuda.

> **Isto vale principalmente para quem já é bom.** Quem está começando precisa de
> mais prática, não de menos; quem já sabe corre o risco de perder o que sabe sem
> perceber, porque a perda é lenta e o feedback é tardio.

### B · Erosão de conhecimento coletivo

O código existe e ninguém o entende. Consequências em ordem: depuração lenta →
estimativa ruim → arquitetura ruim → dependência da ferramenta.
Contramedidas no [27-times-e-organizacao](27-times-e-organizacao.md), §5.

### C · Erosão estrutural

Duplicação +81%, refatoração de 21% para 3,8%. Ninguém mede, ninguém corrige, e
o custo aparece na manutenção — anos depois, quando a causa já não é atribuível.

**Contramedida:** medir, com tendência, e agendar consolidação. Não vai acontecer
sozinho.

---

## O antídoto geral

Se você guardar uma coisa deste arquivo:

> **Toda vez que a IA te fizer produzir mais, pergunte: eu aumentei também a
> minha capacidade de verificar?**
>
> Se não, você não ficou mais produtivo. Você ficou mais endividado.

---

## Autoteste

1. Cite as cinco armadilhas de delegação que você mais comete.
2. Por que "aceitar o relato" é diferente de "aceitar o resultado"?
3. Por que teste tautológico é pior que nenhum teste?
4. O que é verificação de integridade do portão? Dê um exemplo.
5. Desmonte o mito "prompt engineering é a habilidade do futuro" em duas frases.
6. Em que situação o *vibe coding* é a escolha certa? Qual é o critério?
7. Cite quatro problemas que **não** se resolvem com prompt melhor, e por quê.
8. Por que "se os testes passam, pode fundir" é falso?
9. Descreva o ciclo vicioso da erosão de competência e três contramedidas.
10. Por que a erosão estrutural é a mais difícil de combater?
11. Enuncie o antídoto geral com as suas palavras.

---

**Anterior:** [70-pratica](70-pratica.md) ·
**Próximo:** [80-custos-e-licencas](80-custos-e-licencas.md)
