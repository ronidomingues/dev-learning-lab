# 70 · Prática — 14 laboratórios progressivos

**Nível:** iniciante → avançado · **Escrito em:** 19/08/2026

Cada laboratório tem **objetivo**, **passos**, **critério de sucesso** e
**armadilha esperada**. Os marcados com 💻 rodam sem chave de API; os marcados
com 💳 consomem crédito (centavos).

Faça na ordem. O laboratório 3 é o divisor de águas — quem o completa está no
nível 2 de [02-pre-requisitos](02-pre-requisitos.md).

---

## Lab 1 💻 · O prompt ruim, de propósito

**Objetivo:** sentir na pele a diferença entre pedido vago e especificação.

1. Escolha uma tarefa sua de verdade (classificar e-mail, extrair dado de nota
   fiscal, resumir ata).
2. Escreva o prompt mais natural que lhe ocorrer. Rode em 5 casos.
3. Anote **todos** os defeitos da saída — formato, invenção, tom, tamanho.
4. Para cada defeito, escreva **uma linha** de instrução que o corrija.
5. Rode de novo, nos mesmos 5 casos.

**Sucesso:** você tem uma lista de defeitos → regras, e cada regra tem origem
documentada.
**Armadilha:** escrever regra para defeito que você imaginou, e não observou.

---

## Lab 2 💻 · Vinte casos rotulados

**Objetivo:** o ativo mais importante da sua carreira.

1. Colete 20 entradas reais (ou o mais próximo disso que conseguir).
2. **Antes** de rotular, escreva o critério em 5 linhas.
3. Rotule à mão. Cronometre.
4. Peça a outra pessoa que rotule 10 dos 20, sem ver os seus rótulos.
5. Meça a discordância entre vocês.

**Sucesso:** arquivo `.jsonl` com 20 casos e a taxa de discordância humana
anotada.
**Armadilha:** escolher só casos fáceis. Inclua o ambíguo, o vazio e o gigante.
**Por que importa:** a discordância humana é o teto do seu sistema
([20](20-avaliacao-e-evals.md)).

---

## Lab 3 💻 · O arnês de avaliação ⭐

**Objetivo:** parar de achar e começar a medir. **Este é o divisor de águas.**

1. Rode o [projeto-modelo](07-projeto-modelo/README.md):
   `python3 avaliar.py --erros`.
2. Leia `avaliar.py` inteiro. São ~150 linhas; entenda cada uma.
3. Reescreva-o para o **seu** conjunto do Lab 2.
4. Rode duas versões do seu prompt e compare.

**Sucesso:** um comando seu que imprime uma tabela com duas versões e sai com
código ≠ 0 abaixo do limite.
**Armadilha:** anunciar melhora com 20 casos. Calcule o intervalo com
`intervalo.py` de [20 §20.4](20-avaliacao-e-evals.md) **antes** de comemorar.

---

## Lab 4 💻 · Ablação

**Objetivo:** descobrir quanto do seu prompt é peso morto.

1. Divida seu prompt em blocos nomeados (papel, regras, exemplos, formato).
2. Remova **um** e rode a avaliação. Anote métrica e tokens.
3. Repita para cada bloco. Monte a tabela.
4. Remova permanentemente tudo que não moveu a métrica.

**Sucesso:** tabela bloco × métrica × custo, e um prompt menor com a mesma
qualidade.
**Armadilha:** remover dois blocos de uma vez.
**Resultado típico:** 20% a 40% do prompt sai sem prejuízo.

---

## Lab 5 💻 · Caça ao formato quebrado

**Objetivo:** construir o extrator e o validador de saída.

1. Junte 10 saídas mal formatadas: com cerca de markdown, com preâmbulo,
   truncada, com vírgula sobrando, com aspas curvas, com `N/A` no lugar de
   `null`.
2. Escreva `extrair_json` e `validar` que lidem com todas.
3. Escreva teste para cada caso.

**Sucesso:** suíte verde, incluindo o caso truncado (que deve **falhar**
explicitamente, não passar).
**Armadilha:** um extrator tão tolerante que aceita lixo. Tolerância na
extração, rigor na validação.

---

## Lab 6 💳 · Poucos exemplos, bem escolhidos

**Objetivo:** few-shot dirigido por erro.

1. Rode seu conjunto e colete os erros.
2. Agrupe por **tipo** de erro.
3. Escreva **um** exemplo por tipo — no máximo 5.
4. Meça antes/depois, e meça também o custo por chamada.

**Sucesso:** ganho de métrica com justificativa por tipo de erro, e o custo
adicional calculado.
**Armadilha:** colocar 15 exemplos "por segurança". Meça 5 contra 15: o ganho
raramente paga.

---

## Lab 7 💻 · Cache: encontre o invalidador

**Objetivo:** entender por que o cache não pega.

1. Monte um prompt com: papel (estável), lista de ferramentas (estável),
   carimbo de data (volátil) e a pergunta.
2. Coloque o carimbo **no topo**. Anote a estrutura.
3. Mova o carimbo para **o fim**, junto da pergunta.
4. Explique, por escrito, por que o cache funciona em (3) e não em (2).
5. 💳 Se tiver chave: rode as duas versões duas vezes e compare os tokens
   lidos do cache na resposta.

**Sucesso:** você consegue explicar casamento por prefixo a um colega em 2
minutos.
**Armadilha:** achar que o cache é "por conteúdo". É por **prefixo exato**.

---

## Lab 8 💻 · Calculadora de custo

**Objetivo:** falar de dinheiro com números.

1. Adapte `custo.py` de [30 §30.2](30-custo-latencia-caching.md) ao seu caso.
2. Calcule quatro cenários: sem cache, com cache, modelo menor, cache + lote.
3. Escreva uma recomendação de **cinco linhas** para um gestor: quanto custa
   hoje, quanto custaria, o que se perde.

**Sucesso:** a recomendação cabe em cinco linhas e tem números.
**Armadilha:** esquecer a saída na conta. Frequentemente ela domina.

---

## Lab 9 💻 · Red team no seu próprio sistema

**Objetivo:** descobrir seus buracos antes que outro descubra.

1. Pegue os 12 ataques de [35 §35.6](35-seguranca-e-injecao.md).
2. Rode todos contra o seu prompt.
3. Para cada sucesso do ataque, escreva a **asserção negativa** que o detecta.
4. Acrescente ao conjunto de avaliação. Corrija o que der para corrigir **no
   código**, não só no prompt.
5. Analise seu sistema pela trinca letal: quais das três pernas ele tem?

**Sucesso:** 12 casos adversariais no CI e uma análise escrita da trinca.
**Armadilha:** corrigir só com instrução no prompt e se dar por satisfeito.

---

## Lab 10 💳 · Comparação de modelos

**Objetivo:** escolher modelo com dado, não com fé.

1. Rode o mesmo conjunto no modelo grande e no pequeno.
2. Monte a tabela: acerto, custo por mil, latência média e p95.
3. Identifique **em quais casos** o pequeno erra. Há padrão?
4. Se houver, projete a cascata ([06, exemplo 11](06-exemplos.md)) e estime.

**Sucesso:** uma decisão de modelo justificada por três números.
**Armadilha:** comparar em conjuntos diferentes, ou rodar uma vez só.

---

## Lab 11 💻 · RAG mínimo, com recuperação medida

**Objetivo:** separar erro de busca de erro de geração.

1. Pegue 30 documentos seus. Fatie por estrutura.
2. **Olhe 20 trechos com os próprios olhos.** Corrija o fatiador.
3. Monte 20 perguntas e anote **qual trecho** contém a resposta.
4. Implemente busca simples (pode ser por palavras) e meça **Recall@5**.
5. Só então gere resposta com citação, e verifique se o id citado existe.

**Sucesso:** Recall@5 medido, e você sabe dizer se o gargalo é busca ou
geração.
**Armadilha:** ir direto para a geração e passar semanas ajustando prompt com
Recall@5 de 60%.

---

## Lab 12 💳 · Agente com política de parada

**Objetivo:** autonomia com limite.

1. Defina duas ferramentas de leitura (busca e consulta).
2. Escreva o prompt de sistema com as sete partes de
   [25 §25.5](25-ferramentas-e-agentes.md), incluindo política de parada.
3. Rode 20 tarefas. Meça: conclusão, passos, custo médio e **p95**, taxa de
   escalonamento.
4. Introduza uma falha proposital numa ferramenta. O agente para ou entra em
   laço?

**Sucesso:** o agente para com `PRECISO_ESCALAR` em vez de girar; p95 medido.
**Armadilha:** sem limite de passos, a conta cresce silenciosamente.

---

## Lab 13 💻 · Otimização automática de brinquedo

**Objetivo:** entender a estrutura da busca antes de usar framework.

1. Rode `otimizador.py` de [45 §45.2](45-otimizacao-automatica.md).
2. Modifique a função de pontuação para refletir **seu** caso (quais partes
   ajudam, quais interagem).
3. Compare guloso e exaustivo. Monte a fronteira de Pareto.
4. Explique por escrito onde o guloso erra e por quê.

**Sucesso:** você prevê o resultado da busca antes de rodá-la.
**Armadilha:** confundir a simulação com medição real. Ela ensina a estrutura,
não o seu número.

---

## Lab 14 💳 · O projeto de portfólio

**Objetivo:** o artefato que consegue entrevista.

Um problema real, de ponta a ponta:

- [ ] conjunto rotulado com critério escrito (≥ 50 casos)
- [ ] três versões de prompt, com métrica de cada uma
- [ ] intervalo de confiança nas comparações
- [ ] extração e validação de saída, com testes
- [ ] avaliação em CI, com portão
- [ ] custo por mil execuções, com preço datado
- [ ] 12 casos adversariais e a análise da trinca letal
- [ ] README com problema, métrica, antes/depois, custo e **um trade-off
      explicado**

**Sucesso:** um repositório público que um avaliador técnico entende em 5
minutos.
**Armadilha:** projeto bonito sem número. Sem métrica, é demonstração — e
demonstração não contrata ninguém.

---

## Autoavaliação final

| Consigo... | Nível |
|---|---|
| escrever prompt com papel, regras, exemplos e formato | 1 |
| extrair e validar JSON com robustez | 1 |
| montar conjunto rotulado e arnês de avaliação | **2** |
| dizer se uma diferença de métrica é significativa | **2** |
| fazer ablação e podar prompt | 2 |
| calcular e reduzir custo com cache e escolha de modelo | 2 |
| separar erro de recuperação de erro de geração | 3 |
| projetar agente com política de parada e medir p95 | 3 |
| fazer red team e analisar pela trinca letal | 3 |
| usar otimização automática com conjunto de validação separado | 4 |
