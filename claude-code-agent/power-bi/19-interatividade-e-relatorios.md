# 19 · Interatividade e construção de relatórios

**Nível:** intermediário
**Data:** 14/08/2026

O que separa um relatório do Power BI de um PDF é a interatividade. Este capítulo cobre os
mecanismos, a ordem em que os filtros se combinam (que quase ninguém conhece e que explica
muito comportamento estranho) e os padrões de navegação que funcionam.

---

## 1. A hierarquia de filtros — a ordem que importa

Quando uma medida é avaliada, os filtros vêm de várias origens **ao mesmo tempo** e se
combinam por **interseção** (E lógico), não por substituição.

```
                    ┌─────────────────────────────────────┐
                    │  1. RLS (segurança por linha)       │  ← aplicada primeiro,
                    │     não removível por medida        │     não contornável
                    └──────────────┬──────────────────────┘
                                   │ ∩
                    ┌──────────────▼──────────────────────┐
                    │  2. Filtros de TODAS AS PÁGINAS     │
                    └──────────────┬──────────────────────┘
                                   │ ∩
                    ┌──────────────▼──────────────────────┐
                    │  3. Filtros de PÁGINA               │
                    └──────────────┬──────────────────────┘
                                   │ ∩
                    ┌──────────────▼──────────────────────┐
                    │  4. Segmentações (slicers) da página│
                    └──────────────┬──────────────────────┘
                                   │ ∩
                    ┌──────────────▼──────────────────────┐
                    │  5. Cross-filter / cross-highlight  │
                    │     (clique em outro visual)        │
                    └──────────────┬──────────────────────┘
                                   │ ∩
                    ┌──────────────▼──────────────────────┐
                    │  6. Filtros do VISUAL               │
                    └──────────────┬──────────────────────┘
                                   │ ∩
                    ┌──────────────▼──────────────────────┐
                    │  7. Eixos/legendas do próprio visual│
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │  8. CALCULATE dentro da medida      │  ← o ÚNICO que pode
                    │     (pode SUBSTITUIR os anteriores) │     substituir
                    └─────────────────────────────────────┘
```

**Duas consequências que resolvem muita dúvida:**

1. **Filtros 2 a 7 se intersectam.** Se a página filtra `Ano = 2026` e a segmentação filtra
   `Ano = 2025`, o resultado é vazio. Não há "o mais específico ganha".

2. **Só `CALCULATE` substitui.** É por isso que uma medida com
   `CALCULATE([Fat], dProduto[Categoria]="Tintas")` ignora a segmentação de categoria
   ([`16`](16-dax-contexto-de-avaliacao.md) §5.2). E é por isso que `KEEPFILTERS` existe.

3. **RLS não é contornável por medida.** Nem `ALL()` nem `REMOVEFILTERS()` a removem. Mas
   veja o alerta sobre canais laterais em [`24`](24-seguranca-e-governanca.md).

---

## 2. Filtros e segmentações

### 2.1 Onde colocar cada filtro

| Tipo | Quando usar | Custo |
|---|---|---|
| **Filtro de todas as páginas** | Regra fixa do relatório ("só linhas confiáveis", "só ativos") | Baixo |
| **Filtro de página** | Escopo daquela página | Baixo |
| **Filtro de visual** | Ajuste local ("top 10 apenas") | Baixo |
| **Segmentação** | O **usuário** precisa escolher | Médio (é um visual) |
| **Filtro dentro da medida** | Regra de negócio permanente | Variável |

**Prática:** o que é regra do modelo vai para a medida ou para o Power Query. O que é
escolha do usuário vai para a segmentação. O que é escopo do relatório vai para o painel
de filtros. Confundir os três produz relatórios onde ninguém sabe por que o número mudou.

### 2.2 Tipos de segmentação

| Tipo | Bom para |
|---|---|
| Lista | Poucos itens |
| Suspensa (*dropdown*) | Muitos itens, pouco espaço |
| **Botões** (*button slicer*) | 2 a 6 opções; visual limpo; muito flexível |
| Intervalo numérico | Valores contínuos |
| Intervalo de datas | Períodos |
| Data relativa | "Últimos 30 dias", "Este mês" — **atualiza sozinho** ★ |
| Hierárquica | Categoria → Produto |
| Segmentação por outro visual | Qualquer visual pode filtrar |

**A segmentação de data relativa** é subutilizada. Ela resolve "sempre mostrar os últimos
12 meses" sem nenhum DAX e sem manutenção.

### 2.3 Sincronizar segmentações

**Exibição → Sincronizar segmentações.** Uma segmentação numa página aplica-se a outras.

Painel com duas colunas de caixas de seleção:

- **Sincronizar** — o filtro se aplica àquela página;
- **Visível** — a segmentação aparece naquela página.

**Padrão profissional:** marque "Sincronizar" em todas as páginas e "Visível" só onde faz
sentido. Assim o filtro é consistente sem repetir o controle na tela.

### 2.4 Painel de filtros — configure, não esconda

O painel de filtros do lado direito pode ser:

- **formatado** (cores, fontes, largura) pelo tema;
- **bloqueado** por filtro (o usuário vê mas não altera);
- **ocultado** por filtro;
- **fechado por padrão**, mas acessível.

**Opinião do autor:** esconder o painel de filtros inteiramente é um erro comum. O usuário
precisa poder **ver quais filtros estão ativos**. Um relatório em que o número mudou e
ninguém sabe por quê é um relatório em que ninguém confia. Bloqueie os filtros que não
devem mudar, mas deixe-os visíveis.

---

## 3. Interações entre visuais

Por padrão, clicar num visual afeta os outros. Você controla como:

**Formato → Editar interações**, e então, em cada visual de destino, escolha:

| Ícone | Comportamento |
|---|---|
| ⧉ **Filtrar** | O visual de destino mostra **só** os dados selecionados |
| ◐ **Destacar** (*highlight*) | Mostra a parcela selecionada sobre o total — mantém o contexto |
| ⊘ **Nenhum** | Ignora |

**Quando usar cada um:**

- **Destacar** é melhor para gráficos de barras e colunas: você vê a parte e o todo.
- **Filtrar** é melhor para tabelas, matrizes e cartões, onde "destacar" não faz sentido.
- **Nenhum** para visuais de contexto que devem permanecer fixos (uma meta, um total geral).

**Ganho de desempenho:** desligar interações desnecessárias reduz o número de consultas
disparadas por clique. Numa página com 8 visuais, um clique pode disparar 8 consultas —
ou 3, se você configurar.

---

## 4. Navegação

### 4.1 Drill down (dentro do visual)

Descer numa hierarquia: `Ano → Trimestre → Mês → Dia`, ou `Categoria → Linha → Produto`.

Controles no canto do visual:
- **seta para baixo** — ativa o modo de drill (clicar desce);
- **seta dupla** — expande **todos** os itens para o próximo nível;
- **grade** — mostra o próximo nível **junto** com o atual.

**Cuidado:** hierarquias profundas com alta cardinalidade no último nível (produto, cliente)
geram consultas caras.

### 4.2 Drillthrough (para outra página)

Leva o **contexto do clique** para uma página de detalhe.

**Como configurar:**
1. Crie a página de destino.
2. Arraste o campo (ex.: `dProduto[Produto]`) para o poço **Drill-through** dela.
3. Opcionalmente ative "Manter todos os filtros".
4. Um botão de voltar é criado automaticamente.

**Padrão que funciona bem:** página resumida com poucos visuais → clique com botão direito
num produto → página de detalhe daquele produto com histórico, clientes, margem e
devoluções.

**Vantagem sobre amontoar tudo numa página:** desempenho (a página de detalhe só carrega
quando chamada) e clareza.

### 4.3 Botões, ações e navegação de página

**Inserir → Botões**, com ações:

| Ação | Uso |
|---|---|
| Navegação de página | Menu lateral, abas customizadas |
| Indicador (*bookmark*) | Trocar estado da página |
| Voltar | Retornar da página de detalhe |
| Drill-through | Ir para detalhe explicitamente |
| Q&A | Abrir a caixa de perguntas |
| URL da Web | Link externo |
| Aplicar/Limpar filtros de segmentação | Botão "limpar tudo" |

**Padrão de menu:** um retângulo à esquerda com 5 botões de navegação de página,
**agrupado** no painel Seleção e **copiado** (`Ctrl+C`/`Ctrl+V`) para todas as páginas.
Mantenha as posições idênticas — assim o menu parece fixo enquanto o conteúdo troca.

### 4.4 Indicadores (*bookmarks*)

> **Indicador** — um estado salvo da página: filtros, seleções, visibilidade de objetos,
> ordenação, modo de drill.

**Ao criar, marque só o que deve ser restaurado** (menu do indicador → Dados / Exibição /
Página atual / Todos os visuais ou Selecionados). Um indicador que salva tudo sobrescreve
filtros do usuário e gera comportamento imprevisível.

**Usos legítimos:**

| Padrão | Como |
|---|---|
| Alternar gráfico ↔ tabela | Dois visuais sobrepostos, dois indicadores, dois botões |
| Painel de filtros deslizante | Grupo de segmentações que aparece/some |
| "Cenários" | Vários conjuntos de filtros salvos |
| Apresentação guiada | Modo de exibição de indicadores, em sequência |
| Redefinir | Um indicador com o estado inicial |

**Alternativa que quase sempre é melhor:** **parâmetros de campo**
([`17`](17-dax-inteligencia-de-tempo.md) §6). Onde antes se usavam 4 indicadores e 4
visuais sobrepostos para trocar a métrica, hoje se usa um parâmetro de campo e **um**
visual. Menos objetos, menos manutenção, e o estado fica no filtro (portanto compartilhável
por URL e por indicador de usuário).

### 4.5 Dicas de ferramenta de página (*report page tooltips*)

Uma página inteira como tooltip de um visual.

1. Crie a página; em Formato da página → Tipo de página → **Dica de ferramenta**.
2. Arraste o campo de contexto para o poço "Dicas de ferramenta" da página.
3. No visual de origem: Formato → Dica de ferramenta → Tipo: Página do relatório.

**Ótimo para:** mostrar a série histórica de uma barra sem sair da página.
**Ruim para:** informação essencial — em celular, tooltips são difíceis de acionar.

---

## 5. Padrões de relatório que funcionam

### 5.1 A estrutura de três camadas

```
CAMADA 1 · VISÃO GERAL      "está tudo bem?"
   4 KPIs + 1 gráfico de tendência + 1 de composição
   Responde em 5 segundos, de longe, numa TV
                 │ drillthrough
                 ▼
CAMADA 2 · ANÁLISE          "onde está o problema?"
   Comparações, rankings, decomposição, cascata
   Responde em 2 minutos, sentado
                 │ drillthrough
                 ▼
CAMADA 3 · DETALHE          "qual registro exatamente?"
   Matriz/tabela com o detalhe, exportável
   Responde à pergunta operacional
```

Este é, na minha experiência, o padrão que mais sobrevive ao tempo. O erro típico é tentar
fazer as três camadas na mesma página.

### 5.2 A página de auditoria

Já defendida em [`06-exemplos.md`](06-exemplos.md) §15 e implementada no
[`07-projeto-modelo/`](07-projeto-modelo/README.md). Repito porque é o conselho mais
valioso deste curso:

> **Todo relatório sério tem uma página que mostra os problemas dos próprios dados.**

Conteúdo mínimo: quantas linhas foram descartadas e por quê; quais chaves estão órfãs;
quais períodos estão sem dado; qual a data da última atualização; e o número "ingênuo" ao
lado do oficial.

Um relatório que mostra o próprio erro ganha confiança. Um que finge perfeição a perde na
primeira divergência — e a divergência sempre chega.

### 5.3 A página "sobre"

Última página, geralmente oculta do menu mas acessível:

- o que cada medida significa, em português;
- de onde vem cada dado e com que frequência atualiza;
- quem é o dono do relatório e quem é o dono do dado;
- o que **não** está incluído (o mais importante);
- histórico de mudanças relevantes.

Custa 30 minutos. Economiza dezenas de e-mails por ano e sobrevive à sua saída da empresa.

---

## 6. Recursos de exploração

### 6.1 Perguntas e Respostas (Q&A)

Caixa em linguagem natural. Funciona **na proporção da qualidade do modelo**:

- nomes de tabela e coluna em linguagem de negócio, não técnica;
- **sinônimos** cadastrados (Modelagem → Configuração de P&R → sinônimos);
- termos técnicos e chaves **ocultos**;
- medidas com descrição (`///`).

**Opinião do autor:** Q&A tem valor real como *ferramenta de diagnóstico de modelo*. Se o
Q&A erra muito, o modelo está mal nomeado — e isso afeta também o Copilot e qualquer
agente que consuma o modelo. Vale rodar mesmo que você não pretenda expor o Q&A.

### 6.2 Árvore de decomposição

Exploração guiada: escolha uma medida e vá abrindo por dimensões, com opção de
"maior valor" e "menor valor" automáticos.

Excelente para análise de causa. Limite as dimensões disponíveis, ou o usuário se perde.

### 6.3 Principais Influenciadores

Roda uma análise estatística (regressão logística ou linear, conforme o caso) para
identificar fatores associados a um resultado.

**Aviso sério:** ele encontra **associação**, não causa. O visual usa a palavra "influencia"
na interface, o que é infeliz. Trate como gerador de hipóteses, nunca como prova.

### 6.4 Copilot e narrativa inteligente

Gera resumos em texto sobre o que está na tela. Útil como ponto de partida; **sempre
revise**. Ver [`26-fabric-e-ecossistema.md`](26-fabric-e-ecossistema.md) e
[`65-estado-da-arte.md`](65-estado-da-arte.md).

---

## 7. Os cinco porquês: por que o "destacar" existe além do "filtrar"?

1. **Por que não filtrar sempre, que é mais simples?**
   Porque filtrar **remove o contexto**. Ao clicar em "Tintas", um gráfico de linhas
   filtrado mostra só a série de tintas; destacado, mostra tintas **dentro** do total —
   você vê a proporção.

2. **Por que a proporção importa?**
   Porque a pergunta analítica quase nunca é "quanto de X", e sim "quanto de X **em
   relação a**". Sem o todo, o número não tem escala.

3. **Por que não mostrar os dois lado a lado?**
   Porque duplicaria a área de tela por visual e dobraria as consultas. O destaque resolve
   com uma consulta e um visual — ele desenha o total e sobrepõe a parte.

4. **Por que o destaque não funciona em todo visual?**
   Porque exige uma codificação visual que possa ser **dividida**: uma barra pode ser
   pintada em duas intensidades; um cartão com um número único, não. Por isso cartões e
   tabelas só aceitam "filtrar".

5. **Parada legítima — decorre da geometria da codificação.**
   O comportamento disponível é determinado por como o visual codifica o valor. É a mesma
   raiz do capítulo [`18`](18-visualizacao.md): a forma visual determina o que é possível
   comunicar. Não é limitação de software.

---

## 8. Autoteste

1. Descreva a hierarquia de filtros e diga qual é o único mecanismo que **substitui**.
2. Se a página filtra `Ano=2026` e a segmentação filtra `Ano=2025`, o que aparece?
3. Onde colocar: uma regra fixa do relatório, uma escolha do usuário, uma regra de negócio
   permanente?
4. Para que serve a segmentação de data relativa, e que problema ela elimina?
5. Explique a diferença entre "Filtrar" e "Destacar", e quando usar cada um.
6. Como reduzir o número de consultas disparadas por clique?
7. Quando usar drill down e quando usar drillthrough?
8. Por que parâmetros de campo costumam ser melhores que indicadores para trocar métrica?
9. Descreva a estrutura de três camadas e o erro típico.
10. Cite quatro itens que a página de auditoria deve conter.
11. Por que o Q&A é útil mesmo para quem não pretende expô-lo aos usuários?
12. Qual o problema conceitual do visual "Principais Influenciadores"?

---

**Próximo:** [`20-modos-de-armazenamento.md`](20-modos-de-armazenamento.md) — a decisão de
arquitetura que define o teto do seu projeto.
