# 75 · Armadilhas e mitos

**Nível:** todos
**Data:** 14/08/2026

32 armadilhas e 10 mitos. Cada armadilha tem **sintoma → causa → correção → prevenção**.
Não é lista de "dicas": é o catálogo de erros que eu vi custarem dinheiro.

---

## Bloco 1 · Dados e Power Query

### 1. Excel como fonte de produção

**Sintoma.** A atualização quebra do nada. Alguém renomeou uma aba, inseriu uma coluna,
digitou "N/A" numa coluna numérica, ou deixou o arquivo aberto (gerando `~$arquivo.xlsx`).

**Causa.** Excel não tem esquema. Não há contrato entre quem produz e quem consome.

**Correção.** Se for inevitável: use **tabelas nomeadas** (não intervalos), filtre `~$` na
leitura, use `MissingField.Ignore`, e trate erros com `try ... otherwise`.

**Prevenção.** Mover a fonte para um lugar com esquema: banco, SharePoint List, ou ao menos
um CSV gerado por processo. **Opinião:** todo projeto que depende de Excel manual tem uma
data de morte; ela só ainda não foi marcada.

---

### 2. Localidade de data

**Sintoma.** `01/02/2026` vira 2 de janeiro. Ou a conversão dá erro só em algumas linhas.

**Causa.** Detecção automática de tipo, com a localidade errada.

**Correção.** **Alterar Tipo → Usando Localidade**, sempre explícito.

**Prevenção.** Padronize as fontes em ISO 8601 (`aaaa-mm-dd`), que é não ambíguo, e
declare `"en-US"` na conversão.

---

### 3. Data/hora automática ligada

**Sintoma.** Arquivo enorme sem explicação; hierarquias de data duplicadas; memória alta.

**Causa.** O Power BI cria uma tabela de datas oculta **por coluna de data** do modelo.

**Correção.** Arquivo → Opções → Arquivo Atual → Carregamento de Dados → desmarcar.

**Prevenção.** Desmarque também nas opções **globais**, para todo arquivo novo. É a
primeira coisa que faço em máquina nova.

---

### 4. Perda de *query folding*

**Sintoma.** Refresh de horas; memória do Mashup Engine subindo.

**Causa.** Um passo não dobrável (índice, coluna personalizada complexa, `Table.Buffer`)
colocado **cedo** na consulta.

**Correção.** Reordene: o que dobra primeiro. Verifique com **Exibir Consulta Nativa**.

**Prevenção.** Sempre confira a consulta nativa na última etapa antes de publicar.

---

### 5. "Combinar Arquivos" automático

**Sintoma.** Quatro consultas auxiliares confusas; a atualização quebra quando um arquivo
é atípico ou está aberto.

**Causa.** O assistente usa o primeiro arquivo como amostra e não filtra temporários.

**Correção e prevenção.** Escreva à mão. Código completo em
[`06-exemplos.md`](06-exemplos.md) §12.

---

### 6. Fonte de dados dinâmica

**Sintoma.** Funciona no Desktop; no Service:
`This dataset includes a dynamic data source...` e a atualização é impossível.

**Causa.** URL montada por concatenação em `Web.Contents`.

**Correção.** Use os parâmetros `RelativePath` e `Query` de `Web.Contents`.

---

### 7. *Formula Firewall*

**Sintoma.** `Formula.Firewall: A consulta 'X' referencia outras consultas...`

**Causa.** Níveis de privacidade incompatíveis entre fontes combinadas numa mesma consulta.

**Correção.** Reestruture: uma consulta por fonte, e uma terceira que as combina. Só em
último caso, desligue a verificação.

---

### 8. Apagar as linhas ruins

**Sintoma.** Os números "ficam certos", mas ninguém corrige a origem, e o problema cresce.

**Causa.** Filtrar o problema em vez de expô-lo.

**Correção.** **Marque, não apague.** Colunas `MotivoSuspeita` e `LinhaConfiavel`, mais uma
página de auditoria. Ver [`07-projeto-modelo/`](07-projeto-modelo/README.md).

**Prevenção.** Cultura: o relatório de erros é tão entregável quanto o de vendas.

---

## Bloco 2 · Modelagem

### 9. Uma tabela grande e achatada

**Sintoma.** Funciona no começo. Depois: sem tabela de datas, sem segunda tabela de fatos,
sem saber o que **não** aconteceu.

**Correção.** Esquema estrela ([`14`](14-modelagem-dimensional.md) §2).

---

### 10. Relacionar duas tabelas de fatos

**Sintoma.** Números inflados; ambiguidade; totais que não fecham.

**Causa.** Fato-com-fato gera muitos-para-muitos.

**Correção.** Dimensões compartilhadas ([`14`](14-modelagem-dimensional.md) §5).

---

### 11. Aceitar o muitos-para-muitos que o Power BI propõe

**Sintoma.** O Power BI cria uma relação `*:*` e você clica em OK.

**Causa.** A coluna do lado "1" tem duplicatas.

**Correção.** Remova as duplicatas **e descubra por quê**. Quase sempre é SCD mal feita,
cadastro duplicado ou granularidade errada.

**Prevenção.** `*:*` só como escolha deliberada, com tabela ponte.

---

### 12. Filtro bidirecional em toda parte

**Sintoma.** Números inexplicáveis; lentidão; RLS que vaza.

**Causa.** Ativado para resolver um problema pontual de segmentação.

**Correção.** Direção única; use `CROSSFILTER` **local** na medida que precisa.

---

### 13. Sem tabela de datas, ou com tabela de datas incompleta

**Sintoma.** `SAMEPERIODLASTYEAR` devolve vazio; meses sem venda somem do gráfico.

**Causa.** Falta a `dCalendario`, ou ela não cobre anos civis inteiros, ou não está marcada.

**Correção.** Os cinco requisitos de [`17`](17-dax-inteligencia-de-tempo.md) §1.

---

### 14. `datetime` na chave de data

**Sintoma.** A relação existe, mas **nenhuma linha** se relaciona.

**Causa.** `2026-03-14 14:32:07` nunca é igual a `2026-03-14 00:00:00`.

**Correção.** Converta para `date` no Power Query.

---

### 15. Contar `SK` em vez da chave de negócio

**Sintoma.** O número de clientes infla e ninguém entende.

**Causa.** SCD tipo 2 ou recadastro: o mesmo CNPJ com duas SK.

**Correção.** `DISTINCTCOUNT(dCliente[CNPJ])`.

**Prevenção.** Documente qual é a chave de negócio de cada dimensão.

---

### 16. Chaves técnicas visíveis

**Sintoma.** Alguém arrasta `SK_Produto` para um gráfico e obtém um resultado sem sentido.

**Correção.** Oculte. **Um modelo bom torna o erro impossível, não apenas desaconselhado.**

---

### 17. Colunas calculadas na tabela de fatos

**Sintoma.** Modelo grande, refresh lento.

**Causa.** Lógica que caberia no Power Query, feita em DAX.

**Correção.** Mova para o M ou para a fonte. **Faça o mais à esquerda possível.**

---

### 18. Floco de neve por preguiça

**Sintoma.** `fVendas → dProduto → dCategoria → dDepartamento`.

**Correção.** Achate. A economia de espaço é irrelevante; a lentidão e a confusão não são.

---

## Bloco 3 · DAX

### 19. `/` em vez de `DIVIDE`

**Sintoma.** `Infinity` ou erro no visual quando o denominador é zero.

**Correção.** `DIVIDE(n, d)` sempre. Sem exceção.

---

### 20. Percentual como coluna calculada

**Sintoma.** O total mostra 350%.

**Causa.** Percentuais são somados linha a linha.

**Correção.** Percentual é **sempre** medida.

---

### 21. `FILTER` sobre a tabela de fatos

**Sintoma.** Medida lenta; FE alto no DAX Studio.

**Correção.** Predicado simples (`CALCULATE([M], fVendas[Qtd] > 100)`) ou filtrar a
dimensão. Reserve `FILTER(tabela, …)` para quando o predicado envolve duas colunas ou uma
medida.

---

### 22. Esquecer o efeito de substituição do `CALCULATE`

**Sintoma.** A segmentação do usuário é ignorada pela medida.

**Causa.** `CALCULATE([M], dProduto[Categoria]="Tintas")` substitui o filtro do usuário.

**Correção.** `KEEPFILTERS` quando você quer interseção — e **diga qual é qual no nome da
medida**.

---

### 23. Iterar a tabela de fatos com transição de contexto

**Sintoma.** Medida de segundos.

**Causa.** `SUMX(fVendas, [Medida])` — 60 milhões de reconstruções de contexto.

**Correção.** Itere a **dimensão**: `SUMX(VALUES(dProduto[Produto]), [Medida])`.

---

### 24. `FORMAT` no eixo

**Sintoma.** Meses em ordem alfabética; eixo que não faz aritmética.

**Causa.** `FORMAT` devolve **texto**.

**Correção.** Formate na propriedade de formato da medida; use colunas com
`Classificar por Coluna`.

---

### 25. Medida usada como filtro

**Sintoma.** "Não consigo arrastar essa medida para a segmentação."

**Causa.** Medidas não filtram, por construção ([`15`](15-dax-fundamentos.md) §13).

**Correção.** Tabela desconectada com os rótulos + medida que classifica.

---

### 26. `VAR` no lugar errado

**Sintoma.** A medida devolve um número plausível e errado.

**Causa.** Uma expressão que deveria ser avaliada uma vez, fora do iterador, está sendo
reavaliada dentro dele.

**Correção.** Declare a `VAR` **antes** do iterador. Ver
[`15-dax-fundamentos.md`](15-dax-fundamentos.md) §5.

---

### 27. Cascata de medidas com 8 níveis

**Sintoma.** Impossível depurar; desempenho ruim.

**Causa.** Cada medida referencia a anterior, indefinidamente.

**Correção.** Achate. Três níveis é um bom teto. Use `VAR` dentro de uma medida em vez de
criar cinco medidas intermediárias que ninguém usa sozinhas.

---

### 28. Copiar DAX da internet sem entender

**Sintoma.** Funciona. Até o dia em que não funciona, e você não sabe por quê.

**Correção.** Antes de usar, explique a medida em uma frase de português. Se não consegue,
não publique. **A IA piorou isso**, porque agora o código vem plausível e sob medida —
ver [`65-estado-da-arte.md`](65-estado-da-arte.md) §4.3.

---

## Bloco 4 · Relatório e operação

### 29. Publicar sem conferir contra a fonte

**Sintoma.** Alguém encontra a divergência antes de você. A confiança acaba ali.

**Correção.** Antes de publicar, pegue **um** número conhecido e confira contra a origem.
Cinco minutos.

**Prevenção.** Testes automatizados de medida ([`25`](25-ciclo-de-vida-e-devops.md) §5.4).

---

### 30. "Publicar na Web" por engano

**Sintoma.** O relatório interno aparece no Google.

**Correção imediata.** Portal de administração → Publicar na Web → remova o código
publicado. Depois **desabilite** a configuração de locatário.

**Prevenção.** Desabilite hoje, antes que aconteça.

---

### 31. RLS que não foi atribuída no Service

**Sintoma.** A RLS "não funciona".

**Causa.** Criar a função no Desktop **não** basta. É preciso atribuir usuários/grupos em
Modelo semântico → Segurança.

**Prevenção.** Checklist de publicação com esse item.

---

### 32. Relatório sem dono

**Sintoma.** Quebra, e ninguém sabe quem cuida. Fica quebrado por meses.

**Correção.** Página "sobre" com dono do dado e dono técnico; workspace de equipe, nunca
"Meu workspace".

---

## Os 10 mitos

### Mito 1 — "Power BI é gratuito"

**Falso pela metade.** O Desktop é gratuito de verdade. **Compartilhar** exige licença.
A conta chega quando o projeto dá certo. Ver [`80`](80-custos-e-licencas.md).

### Mito 2 — "DAX é igual a fórmula de Excel"

**Falso.** A sintaxe é parecida de propósito; a semântica é radicalmente diferente. É a
maior fonte de sofrimento com DAX ([`16`](16-dax-contexto-de-avaliacao.md)).

### Mito 3 — "Modelagem é preciosismo, o importante é o gráfico"

**Falso.** É o contrário: quase todo problema de DAX, de desempenho e de número errado é um
problema de modelagem disfarçado.

### Mito 4 — "DirectQuery é melhor porque é tempo real"

**Falso na maioria dos casos.** É mais lento, mais frágil e mais complexo. Pergunte que
decisão muda com dados de 5 minutos atrás. ([`20`](20-modos-de-armazenamento.md))

### Mito 5 — "Precisamos migrar para o Fabric"

**Falso para a maioria.** Para 20 usuários e um modelo de 500 MB, Pro resolve e custa uma
fração. ([`26`](26-fabric-e-ecossistema.md) §6)

### Mito 6 — "RLS protege os dados"

**Falso.** Protege o **consumo no Service**, para Visualizadores. Não protege o `.pbix`,
não se aplica a Membros/Colaboradores, e não impede inferência por agregado.
([`24`](24-seguranca-e-governanca.md))

### Mito 7 — "Não dá para versionar Power BI"

**Era verdade até 2024.** PBIP e TMDL resolveram. Quem ainda diz isso não atualizou o
conhecimento. ([`25`](25-ciclo-de-vida-e-devops.md))

### Mito 8 — "Quanto mais visuais, melhor o dashboard"

**Falso.** Mais visuais = mais consultas, mais lentidão, menos atenção. 5 a 8 por página.

### Mito 9 — "O Copilot escreve o DAX para mim"

**Perigosamente falso.** Ele escreve DAX **plausível**. Em contexto de avaliação sutil,
erra com confiança. Você continua responsável pelo número.

### Mito 10 — "Se está no dashboard, está certo"

**O mito mais caro de todos.** Um dashboard bonito com número errado é mais perigoso que
nenhum dashboard, porque produz decisão confiante e errada.

---

## O erro que resume todos

> **Confiar no número sem conferir.**

Todas as 32 armadilhas terminam nisso. A defesa não é técnica; é um hábito: **antes de
mostrar qualquer número a alguém, confira um valor conhecido contra a fonte original.**

Cinco minutos de conferência valem mais que cinco horas de gráfico.

---

## Autoteste

1. Por que Excel como fonte de produção tem data de morte marcada?
2. Qual configuração desligar primeiro em máquina nova, e por quê?
3. Como você verifica se perdeu *query folding*?
4. Por que "marcar, não apagar" é superior a filtrar as linhas ruins?
5. O que significa o Power BI propor um relacionamento `*:*` com uma dimensão?
6. Por que `datetime` na chave de data faz a relação parar de funcionar?
7. Qual armadilha explica um total de 350% num percentual?
8. Por que `SUMX(fVendas, [Medida])` é lento, e qual a correção?
9. Cite três coisas que a RLS não protege.
10. Qual é o mito mais caro, e por quê?
11. Qual é o único hábito que previne todas as 32 armadilhas?
