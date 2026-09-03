# 70 · Prática — 14 laboratórios

**Nível:** todos (marcado por laboratório)
**Data:** 14/08/2026

Cada laboratório tem: **objetivo**, **pré-requisito**, **enunciado**, **critério de
aceite** e **dica**. Faça na ordem; eles se apoiam.

Todos usam a base do [`07-projeto-modelo/`](07-projeto-modelo/README.md). Gere-a antes:

```bash
cd 07-projeto-modelo
python3 gerar_dados.py
python3 validar.py          # guarde a saída: é o gabarito
```

> **Aviso:** os laboratórios **não foram executados nesta sessão** (o Power BI Desktop não
> roda em Linux — ver [`00-MAPA.md`](00-MAPA.md)). Os critérios de aceite são derivados do
> gabarito do `validar.py`, esse sim executado e verificado. Se algum critério não bater,
> desconfie primeiro do seu modelo, depois do enunciado — e me diga.

---

## Lab 1 — Conectar e tipar direito

**Nível:** iniciante · **Tempo:** 40 min · **Cobre:** [`13`](13-power-query-e-m.md)

**Enunciado.** Conecte os sete CSVs de `dados/`. Para cada tabela:

1. use um **parâmetro** `PastaDados` em vez de caminho fixo;
2. tipe **todas** as colunas explicitamente, com localidade declarada;
3. renomeie as consultas com o nome final (`fVendas`, `dProduto`, …);
4. **não carregue** nenhuma consulta auxiliar que criar.

**Critério de aceite:**
- [ ] Mudar `PastaDados` para outra pasta faz tudo funcionar sem editar consulta.
- [ ] Nenhuma coluna com tipo `any` (ícone `ABC/123`).
- [ ] `fVendas` tem 60.621 linhas; `dCliente`, 426; `dProduto`, 25.
- [ ] As datas aparecem como `dd/mm/aaaa`, não como texto nem número.

**Dica.** As datas estão em ISO (`aaaa-mm-dd`). Use **Alterar Tipo → Usando Localidade →
Inglês (Estados Unidos)**. Se você usar pt-BR, `2024-03-05` pode virar erro ou data errada.

---

## Lab 2 — Auditar antes de modelar

**Nível:** iniciante · **Tempo:** 45 min · **Cobre:** [`13`](13-power-query-e-m.md) §6.3

**Enunciado.** Antes de criar qualquer relacionamento, use **Mesclar Consultas → Anti
Esquerda** para responder, no Power Query:

1. Quantas linhas de `fVendas` têm `SK_Produto` que não existe em `dProduto`?
2. Quantas têm `SK_Cliente` órfão?
3. Quantas têm `Data` que não existe em `dCalendario`?
4. Quantos `CNPJ` aparecem em mais de uma linha de `dCliente`?

**Critério de aceite** (confira contra o `validar.py`):
- [ ] 39 vendas com produto órfão, todas com `SK_Produto = 999`.
- [ ] 0 clientes órfãos.
- [ ] 14 vendas com data fora do calendário; as datas são de 2124.
- [ ] 6 CNPJs duplicados.

**Dica.** Para o item 4, use **Agrupar Por** `CNPJ` com contagem, depois filtre `> 1`.

**Por que este lab vem antes da modelagem:** porque descobrir órfãos **depois** de montar
o modelo custa horas de confusão. Auditoria primeiro é o hábito profissional.

---

## Lab 3 — Tratar os defeitos sem apagar linhas

**Nível:** intermediário · **Tempo:** 1 h · **Cobre:** [`13`](13-power-query-e-m.md)

**Enunciado.** No Power Query, implemente o tratamento dos oito defeitos, **sem remover
nenhuma linha**:

1. `QuantidadeAjustada` — devolução sempre negativa;
2. `DescontoAjustado` — dividir por 100 quando `> 1`;
3. `MotivoSuspeita` — texto concatenado com todos os problemas da linha;
4. `LinhaConfiavel` — "Não" quando a data é impossível;
5. em `dCliente`: `UF` normalizada com `Text.Upper(Text.Trim(...))`, preservando a crua;
6. em `dProduto`: acrescente a linha `999 · (sem cadastro)`.

**Critério de aceite:**
- [ ] `fVendas` continua com 60.621 linhas.
- [ ] `MotivoSuspeita` não vazio em pelo menos 500 linhas.
- [ ] `dProduto` tem 26 linhas.
- [ ] `dCliente[UF]` tem exatamente **11** valores distintos (eram 19).

**Dica.** O código de referência está em
[`07-projeto-modelo/modelo/definition/tables/fVendas.tmdl`](07-projeto-modelo/modelo/definition/tables/fVendas.tmdl).
**Tente antes de olhar.**

---

## Lab 4 — Montar o esquema estrela

**Nível:** intermediário · **Tempo:** 45 min · **Cobre:** [`14`](14-modelagem-dimensional.md)

**Enunciado.**
1. Crie `dMes` como tabela calculada, a partir de `dCalendario`.
2. Crie os **8 relacionamentos** do modelo.
3. Marque `dCalendario` como tabela de data.
4. Ordene `Mes` por `NumMes`.
5. Oculte todas as colunas técnicas.
6. Desligue a Data/hora automática.

**Critério de aceite:**
- [ ] Todos os relacionamentos são 1:*, com direção única — **exceto** `dMes ↔ dCalendario`.
- [ ] A relação `dCalendario[Data] → fVendas[DataEntrega]` existe e está **inativa**.
- [ ] Nenhuma coluna `SK_*` visível no painel Dados.
- [ ] Um gráfico com `dCalendario[Mes]` no eixo mostra jan, fev, mar… na ordem certa.

**Pergunta para responder por escrito:** por que `dMes ↔ dCalendario` precisa ser
bidirecional, e por que isso não cria ambiguidade?

---

## Lab 5 — As primeiras medidas, conferidas

**Nível:** intermediário · **Tempo:** 1 h · **Cobre:** [`15`](15-dax-fundamentos.md)

**Enunciado.** Crie a tabela `_Medidas` e as medidas do bloco `01 Base` de
[`07-projeto-modelo/modelo/medidas.dax`](07-projeto-modelo/README.md). Formate cada uma.

**Critério de aceite** — os valores **exatos** do gabarito:

| Medida | Esperado |
|---|---|
| `Faturamento Líquido` | R$ 167.700.759,11 |
| `Custo Total` | R$ 117.824.185,26 |
| `Margem Bruta` | R$ 49.876.573,85 |
| `Margem %` | 29,74% |
| `Quantidade Vendida` | 518.713 |
| `Notas Fiscais` | 24.784 |
| `Ticket Médio` | R$ 6.766,49 |

**Se não bater:** você provavelmente esqueceu o filtro `LinhaConfiavel = "Sim"`, ou está
usando `Quantidade` em vez de `QuantidadeAjustada`, ou `Desconto` em vez de
`DescontoAjustado`. **Diferenças de centavos são aceitáveis; de reais, não.**

---

## Lab 6 — O erro de contagem de clientes

**Nível:** intermediário · **Tempo:** 30 min · **Cobre:** [`14`](14-modelagem-dimensional.md) §4.2

**Enunciado.** Crie as duas medidas — `Clientes Ativos` (por `CNPJ`) e
`Clientes Ativos (contando SK)` — e coloque-as lado a lado num cartão e numa matriz por
ano.

Depois responda por escrito:

1. Qual é a diferença, e por que ela existe?
2. Em que ano a diferença aparece, e por quê?
3. Se este fosse um relatório de comissionamento por número de clientes atendidos, qual
   seria o prejuízo?

**Critério de aceite:**
- [ ] A diferença é de exatamente **6** clientes no período total.
- [ ] A diferença **não** aparece em 2024 e 2025 isoladamente. Explique.

**Dica.** Olhe `plantar_cliente_duplicado` em `gerar_dados.py`: as vendas movidas para a
SK nova são de 2026.

---

## Lab 7 — Inteligência de tempo

**Nível:** avançado · **Tempo:** 1 h 30 · **Cobre:** [`17`](17-dax-inteligencia-de-tempo.md)

**Enunciado.** Crie: `Faturamento AA`, `Δ vs AA`, `Δ % vs AA`, `Faturamento YTD`,
`Faturamento YTD AA`, `Faturamento MAT`, `Média Móvel 3M`,
`Faturamento (meses fechados)` e `Faturamento por Dia Útil`.

**Critério de aceite:**

| Verificação | Esperado |
|---|---|
| `Faturamento Líquido` em 2024 | R$ 58.747.805,39 |
| em 2025 | R$ 68.179.435,59 |
| em 2026 (parcial, até 31/07) | R$ 40.773.518,14 |
| `Δ % vs AA` em 2025 | ≈ **+16,1%** |
| `Δ % vs AA` em 2024 | **em branco** (não há 2023) |
| `Faturamento YTD` em dez/2025 | = o total de 2025 |
| `Faturamento MAT` em jul/2026 | soma de ago/2025 a jul/2026 |

**Armadilha proposital:** se `Δ % vs AA` em 2024 mostrar +100%, sua medida não protege
contra `BLANK`. Corrija.

**Extra:** por que `Δ % vs AA` em 2026 mostra uma queda enorme, e o que fazer a respeito?

---

## Lab 8 — Metas e granularidade mista

**Nível:** avançado · **Tempo:** 1 h 30 · **Cobre:** [`14`](14-modelagem-dimensional.md) §5

**Enunciado.**
1. Crie `Meta`, `Atingimento %`, `Meta Proporcional`, `Atingimento Proporcional %`,
   `Gap para Meta` e `Status da Meta`.
2. Monte uma matriz `Vendedor` × `Mês` com `Atingimento %`.
3. Adicione `Produto` às linhas e observe o que acontece.

**Critério de aceite:**
- [ ] A matriz por vendedor e mês mostra percentuais plausíveis (60%–140%).
- [ ] Existem **7** pares mês/vendedor com venda e **sem** meta — e a célula fica em branco,
      não em erro nem em zero.
- [ ] Ao adicionar `Produto`, `Status da Meta` avisa "sem meta nesta granularidade".
- [ ] `Meta Proporcional` filtrando **um único dia** é ≈ 1/30 da meta do mês.

**Pergunta:** por que a meta se repete em todos os produtos quando você adiciona `Produto`?
O que isso ensina sobre granularidade?

---

## Lab 9 — As três respostas de "% do total"

**Nível:** avançado · **Tempo:** 1 h · **Cobre:** [`16`](16-dax-contexto-de-avaliacao.md) §6

**Enunciado.** Crie `% do Total Geral`, `% do Total Visível` e `% da Categoria`
(este último removendo apenas o filtro de `Produto`).

Monte uma matriz com `Categoria` e `Produto` aninhados, as três medidas, e uma segmentação
de `Ano`.

**Critério de aceite:**
- [ ] Sem filtro de ano, `% do Total Geral` e `% do Total Visível` são **iguais**.
- [ ] Com `Ano = 2026` selecionado, elas **divergem**.
- [ ] A soma de `% do Total Visível` na coluna dá exatamente 100%.
- [ ] `Tintas` fica com ≈ **63,9%** do total (todo o período).

**Escreva:** qual das três você usaria por padrão num relatório executivo, e por quê?

---

## Lab 10 — Pareto e ABC

**Nível:** avançado · **Tempo:** 1 h 30 · **Cobre:** [`06`](06-exemplos.md) §6

**Enunciado.** Implemente `Acumulado Pareto`, `% Acumulado Pareto` e `Classe ABC`.
Monte um gráfico combinado: colunas de faturamento por produto (ordenado desc) e linha do
percentual acumulado.

**Critério de aceite:**
- [ ] A curva sobe monotonicamente até 100%.
- [ ] Os produtos de classe A somam ≈ 80% do faturamento.
- [ ] Filtrar `Categoria = "Tintas"` **recalcula** a classificação (agora dentro de tintas).
- [ ] Filtrar por ano também recalcula.

**Extra (importante):** meça o tempo do visual com o Analisador de Desempenho.
Depois mude o eixo de `Produto` (25 itens) para `Cliente` (426 itens) e meça de novo.
**Anote a diferença e explique.**

---

## Lab 11 — Segurança por linha

**Nível:** avançado · **Tempo:** 1 h · **Cobre:** [`24`](24-seguranca-e-governanca.md)

**Enunciado.**
1. Carregue `dSeguranca` (sem relacionamento com nada).
2. Crie a função `VendasRestritas` com os três escopos.
3. Adicione a regra que esvazia `dSeguranca`.
4. Teste com **Exibir como** para: um vendedor, um gerente, a diretoria e um e-mail
   inexistente.

**Critério de aceite:**
- [ ] `ana.ramalho@tintasaurora.com.br` vê **só** as vendas dela.
- [ ] `gerente.sul@tintasaurora.com.br` vê os **três** vendedores do Sul.
- [ ] `diretoria@tintasaurora.com.br` vê o total: R$ 167.700.759,11.
- [ ] `ninguem@empresa.com` vê **zero** — não o total. (Falha fechada!)
- [ ] Com RLS ativa, `dSeguranca` mostra no máximo 1 linha.

**Pergunta obrigatória:** cite três coisas que esta RLS **não** protege.

---

## Lab 12 — A página de auditoria

**Nível:** intermediário · **Tempo:** 1 h 30 · **Cobre:** [`19`](19-interatividade-e-relatorios.md) §5.2

**Enunciado.** Construa a página de auditoria com:

- cartões: `Linhas na Origem`, `Linhas Suspeitas`, `% Linhas Suspeitas`,
  `Linhas Descartadas`, `Impacto dos Defeitos`, `Erro na Contagem de Clientes`,
  `CNPJs Duplicados`, `Meses sem Meta`;
- uma tabela de `fVendas` filtrada por `MotivoSuspeita <> ""`, com NF, data, produto,
  vendedor e o motivo;
- dois cartões lado a lado: `Faturamento Ingênuo (sem tratamento)` e
  `Faturamento Líquido`.

**Critério de aceite:**
- [ ] `Impacto dos Defeitos` ≈ **R$ 1.660.598,94**.
- [ ] `Erro na Contagem de Clientes` = **6**.
- [ ] `CNPJs Duplicados` = **6**.
- [ ] `Meses sem Meta` = **7**.
- [ ] `Linhas Descartadas` = **14**.

**Reflexão obrigatória, por escrito:** se você entregasse este relatório **sem** esta
página, que decisões erradas ele permitiria?

---

## Lab 13 — Otimização com medição

**Nível:** avançado · **Tempo:** 2 h · **Cobre:** [`21`](21-vertipaq-por-dentro.md), [`22`](22-desempenho.md)

**Enunciado.**

**Parte A — tamanho.**
1. Abra o VertiPaq Analyzer (DAX Studio → Advanced → View Metrics).
2. Anote o tamanho total e as 5 maiores colunas.
3. Aplique: remova colunas não usadas; troque `Desconto` cru por só o ajustado; arredonde
   `PrecoUnitario` e `CustoUnitario` para 2 casas.
4. Meça de novo.

**Parte B — velocidade.**
1. Crie **de propósito** esta medida ruim:
   ```dax
   Vendas Tintas (ruim) =
   SUMX(
       fVendas,
       IF( RELATED( dProduto[Categoria] ) = "Tintas",
           fVendas[QuantidadeAjustada] * fVendas[PrecoUnitario],
           0 )
   )
   ```
2. Meça no DAX Studio com Server Timings e Clear Cache. Anote FE, SE e procure
   `CallbackDataID`.
3. Reescreva com `CALCULATE` e meça de novo.

**Critério de aceite:**
- [ ] Redução mensurável no tamanho (anote o número real do **seu** modelo).
- [ ] A versão ruim tem `CallbackDataID`; a boa, não.
- [ ] A versão boa tem proporção FE/SE claramente melhor.
- [ ] **As duas versões devolvem o mesmo número.** Se não, uma está errada.

**Este é o laboratório mais valioso do conjunto.** Meça tudo, anote tudo.

---

## Lab 14 — PBIP, Git e Best Practice Analyzer

**Nível:** avançado · **Tempo:** 2 h · **Cobre:** [`25`](25-ciclo-de-vida-e-devops.md)

**Enunciado.**
1. Ative o formato PBIP e salve o projeto.
2. `git init`, `.gitignore` adequado, primeiro commit.
3. Explore a estrutura de pastas; abra um `.tmdl` num editor de texto.
4. Mude uma medida no Desktop, salve, e rode `git diff`. **Leia o diff.**
5. Instale o Tabular Editor 2 e rode o **Best Practice Analyzer**.
6. Corrija ao menos **cinco** dos problemas apontados; documente por que **não** corrigiu
   os outros.

**Critério de aceite:**
- [ ] O repositório não contém `.pbix` nem `dados/`.
- [ ] O `git diff` de uma alteração de medida mostra **poucas linhas**, legíveis.
- [ ] O BPA aponta problemas reais (provavelmente: a relação bidirecional, colunas sem
      `summarizeBy`, medidas sem formato).
- [ ] Você escreveu a justificativa da relação bidirecional em vez de simplesmente
      "corrigi-la".

**A lição do item final:** ferramentas de análise estática apontam sintomas. Julgar quais
são problemas de verdade é trabalho humano — e documentar a exceção é parte do trabalho.

---

## Desafios extras

| # | Desafio | Nível |
|---|---|---|
| A | Regenere com `--semente 42` e `--clientes 5000`. Que medida fica lenta primeiro? Por quê? | avançado |
| B | Crie um grupo de cálculo "Tempo" com 6 itens e elimine 30 medidas | avançado |
| C | Crie um parâmetro de campo "Métrica" com 5 opções e reduza 5 gráficos a 1 | intermediário |
| D | Implemente a segmentação dinâmica RFM ([`06`](06-exemplos.md) §8) e meça o custo | pesquisa |
| E | Escreva uma UDF em DAX para "variação percentual protegida" e use-a em 5 medidas | avançado |
| F | Escreva testes de medida em DAX e rode-os por XMLA num script | pesquisa |
| G | Reproduza **todas** as verificações do `validar.py` como medidas DAX da pasta `99 Auditoria` | avançado |
| H | Crie o layout de celular do relatório e teste no app | intermediário |

---

## Autoavaliação

Marque o que você consegue fazer **sem consultar**:

- [ ] Conectar, parametrizar e tipar corretamente (Labs 1, 3)
- [ ] Auditar integridade antes de modelar (Lab 2)
- [ ] Montar um esquema estrela e justificar cada relacionamento (Lab 4)
- [ ] Escrever medidas base e **conferi-las contra um oráculo** (Lab 5)
- [ ] Explicar por que contar `SK` infla clientes (Lab 6)
- [ ] Escrever inteligência de tempo protegida contra `BLANK` (Lab 7)
- [ ] Resolver granularidade mista (Lab 8)
- [ ] Escolher entre as três respostas de "% do total" (Lab 9)
- [ ] Implementar Pareto e entender seu custo (Lab 10)
- [ ] Implementar RLS que falha fechada (Lab 11)
- [ ] Construir uma página de auditoria (Lab 12)
- [ ] Diagnosticar FE × SE e corrigir `CallbackDataID` (Lab 13)
- [ ] Versionar em PBIP e rodar o BPA (Lab 14)

**10 ou mais:** você é um analista de BI competente. **13:** você está acima da média do
mercado brasileiro em 2026.
