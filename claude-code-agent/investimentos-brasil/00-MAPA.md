# 00 · Mapa — Investimentos no Brasil

**Curso completo, do zero absoluto ao nível de pesquisa.**
*Criado em 20/08/2026 · dados de mercado desta data*

> **Aviso.** Material **educacional**. Não é recomendação personalizada de
> investimento — para isso é preciso registro na CVM (Res. 19/2021 ou 178/2023), e
> quem escreve isto não o tem, nem conhece a sua situação. Todo número tem data e
> fonte; confira antes de agir. Preço e lei mudam.

---

## A pergunta que originou este curso

> *"Hoje no Brasil, qual a maneira mais segura e lucrativa para investir R$ 6.000 ou mais?"*

**Resposta curta, com os números de 20/08/2026:**

Segurança e lucratividade normalmente se opõem — mas o Brasil de agora é uma anomalia
mundial: **o ativo mais seguro do país paga cerca de 9% ao ano acima da inflação**
(Selic 14,00%, IPCA 4,44% em 12 meses). Você não precisa correr risco para ter retorno
real alto.

Em ordem, e sem pular etapa:

1. **Quite dívida cara.** Rotativo do cartão custa centenas de % ao ano; nenhum
   investimento legal chega perto. Isso vem antes de tudo.
2. **Se você não tem reserva de emergência, estes R$ 6.000 são ela.** Vá para
   pós-fixado com liquidez diária: **Tesouro Reserva** (lançado em 11/05/2026, 24×7,
   sem oscilação, a partir de R$ 1), **Tesouro Selic** (custódia zero até R$ 10 mil)
   ou **CDB de liquidez diária a 100%+ do CDI**, dentro do FGC. Rende ~**11,5%
   líquidos ao ano**, cerca de **6,7% reais**.
3. **Se a reserva já existe**, aí sim há decisão: **LCI/LCA isenta de IR** para prazos
   médios (carência de 6 meses), e **Tesouro IPCA+** para longo prazo, travando hoje
   cerca de **IPCA + 6,65%** — patamar historicamente alto.
4. **Renda variável só depois disso**, em fatia pequena e via ETF de índice. Com a
   Selic a 14%, a bolsa precisa render ~13% ao ano só para **empatar** com o título
   público.
5. **Fuja de:** poupança (rende 8,34%, R$ 256 a menos por ano que o topo da lista, com
   o mesmo risco), fundos DI com taxa acima de 0,5%, e qualquer coisa que prometa muito
   acima do mercado sem explicar por quê.

Os números estão calculados, e reproduzíveis, em [06-exemplos.md](06-exemplos.md) e no
[07-projeto-modelo](07-projeto-modelo/).

---

## O que você saberá ao final

- Decidir **sozinho** onde colocar qualquer valor, por qualquer prazo, comparando pelo
  **líquido** e não pelo anunciado.
- Calcular IR, IOF, come-cotas e equivalência isento × tributado de cabeça ou em código.
- Explicar marcação a mercado, duration e por que seu título "caiu" sem você ter perdido.
- Saber o que o FGC cobre, até quanto, e em quanto tempo paga de verdade.
- Reconhecer fraude, venda enviesada e produto caro antes de assinar.
- Entender por que o juro brasileiro é o que é — e por que isso não é permanente.
- Ler a teoria (Markowitz, CAPM, fatores, estrutura a termo) e saber onde ela falha.

---

## Roteiro de leitura

**Se você só quer resolver os R$ 6.000 hoje (2 horas):**
[01](01-introducao-leigo.md) → [04](04-como-comecar.md) → [06, exemplo 1](06-exemplos.md)
→ [16, seção 2](16-risco-e-garantias.md)

**Se quer aprender de verdade (rota completa, ~30 horas):**
todos os arquivos, na ordem numérica.

**Se já investe e quer o que não sabe:**
[12](12-renda-fixa.md) → [14](14-tributacao.md) → [60](60-teoria-avancada.md) →
[65](65-estado-da-arte.md) → [75](75-armadilhas.md)

---

## Arquivos

### Bloco A · Porta de entrada
| Arquivo | O que tem | Nível |
|---|---|---|
| [01-introducao-leigo.md](01-introducao-leigo.md) | o que é investir, sem jargão; a anomalia brasileira de 2026; o tripé; a árvore de decisão | iniciante |
| [02-pre-requisitos.md](02-pre-requisitos.md) | conhecimento, documentos, dívida, reserva; tempo realista; rota de resgate | iniciante |
| [03-instalacao.md](03-instalacao.md) | abrir conta, 2FA, Tesouro Direto, gov.br, Registrato, Área do Investidor da B3; Python e planilha nos três sistemas; PATH, permissões, proxy, desinstalar; tabela de erros | iniciante |
| [04-como-comecar.md](04-como-comecar.md) | do ambiente pronto aos R$ 6.000 aplicados; o teste dos R$ 100; ciclo do dia a dia; declaração; 5 erros de uso | iniciante |
| [05-manual-de-uso.md](05-manual-de-uso.md) | referência: como se lê taxa, catálogo de produtos, tabelas de IR e IOF, FGC, calendário, fórmulas, atalhos, o que está obsoleto | iniciante/intermediário |
| [06-exemplos.md](06-exemplos.md) | **13 casos com as contas executadas**, incluindo dois casos reais (Banco Master e dívida de cartão) | iniciante/intermediário |
| [07-projeto-modelo/](07-projeto-modelo/) | **`simulador`**: compara produtos pelo líquido. Python puro, 31 testes, CLI com 3 comandos | prático |

### Bloco B · Núcleo
| Arquivo | O que tem | Nível |
|---|---|---|
| [10-fundamentos.md](10-fundamentos.md) | valor do dinheiro no tempo, juros compostos, Fisher, risco × volatilidade, liquidez, curva de juros; **os cinco porquês do juro alto brasileiro** | intermediário |
| [11-historia.md](11-historia.md) | 1861 à hiperinflação, confisco de 1990, Plano Real, tripé, Tesouro Direto, corretagem zero, o pêndulo 2020–2026 | intermediário |
| [12-renda-fixa.md](12-renda-fixa.md) | preço de título, marcação a mercado, duration e convexidade, NTN-B, cupom, como o banco precifica seu CDB, escada de títulos | intermediário/avançado |
| [14-tributacao.md](14-tributacao.md) | IR regressivo, IOF, come-cotas, isenções, Lei 15.270/2025, renda variável e DARF, declaração | intermediário |
| [16-risco-e-garantias.md](16-risco-e-garantias.md) | hierarquia de segurança, FGC em detalhe e o caso Banco Master, avaliação de emissor, fraude, diversificação, vieses | intermediário |
| [20-renda-variavel.md](20-renda-variavel.md) | ações, ETFs, FIIs, exterior; por que juro alto derruba a bolsa; quanto de risco faz sentido | intermediário |
| [24-carteira-e-alocacao.md](24-carteira-e-alocacao.md) | prazo × produto, a pirâmide, alocações concretas, rebalanceamento, previdência, política de investimento | intermediário |
| [60-teoria-avancada.md](60-teoria-avancada.md) | Markowitz, CAPM, fatores, eficiência, estrutura a termo, Kelly, dinâmica da dívida | pesquisa |
| [65-estado-da-arte.md](65-estado-da-arte.md) | a fotografia de agosto de 2026, ciclo monetário, tributação, Tesouro Reserva, FGC, Drex, tendências | avançado |

### Bloco C · Prática e erros
| Arquivo | O que tem |
|---|---|
| [70-pratica.md](70-pratica.md) | 9 laboratórios (do orçamento à API do BCB) + **gabaritos comentados** dos autotestes |
| [75-armadilhas.md](75-armadilhas.md) | 7 armadilhas caras, 14 mitos, más práticas da indústria, erros de intermediário, o teste das três frases |

### Bloco D · Economia e ecossistema
| Arquivo | O que tem |
|---|---|
| [80-custos-e-licencas.md](80-custos-e-licencas.md) | custo real por produto, quem paga a "corretagem zero", custos ocultos, licenças regulatórias, preços de certificação |
| [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) | cursos gratuitos em **PT, EN e FR**, pesquisados na web; certificações e o que valem de verdade |

### Bloco E · Fontes
| Arquivo | O que tem |
|---|---|
| [90-bibliografia.md](90-bibliografia.md) | livros comentados por nível, o que é legalmente gratuito, o que envelheceu |
| [95-referencias.md](95-referencias.md) | indicadores com data e fonte, legislação, fatos datados, ferramentas, nota metodológica |
| [GLOSSARIO.md](GLOSSARIO.md) | todos os termos técnicos do curso |

---

## Status

| Bloco | Status | Observação |
|---|---|---|
| **A · Porta de entrada** | ✅ | 01–07 completos; projeto-modelo com 31 testes aprovados |
| **B · Núcleo** | ✅ | 10, 11, 12, 14, 16, 20, 24, 60, 65 |
| **C · Prática e erros** | ✅ | 70 (9 laboratórios + gabaritos), 75 |
| **D · Economia e ecossistema** | ✅ | 80, 85 — preços e cursos pesquisados na web em 20/08/2026 |
| **E · Fontes** | ✅ | 90, 95, GLOSSARIO |

**Verificação:** todos os números das tabelas comparativas foram **produzidos rodando
o código** de [07-projeto-modelo](07-projeto-modelo/) (Python 3.10.12, 31 testes
aprovados, doctests dos módulos passando). Indicadores, legislação, cursos e preços
foram pesquisados na web em 20/08/2026.

**Manutenção recomendada:**

| Arquivo | Revisar a cada |
|---|---|
| [65-estado-da-arte.md](65-estado-da-arte.md), [95-referencias.md](95-referencias.md) | **3 meses** (Selic, IPCA, Focus, taxas) |
| [14-tributacao.md](14-tributacao.md) | **6 meses**, ou quando houver MP/PL tributário |
| [03-instalacao.md](03-instalacao.md), [80-custos-e-licencas.md](80-custos-e-licencas.md) | 6 meses |
| [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md), [90-bibliografia.md](90-bibliografia.md) | 12 meses |
| `07-projeto-modelo/indicadores.py` | a cada reunião do Copom (8 por ano) |

---

## Nada ficou pendente de estrutura

Todos os blocos obrigatórios estão escritos. O que **não** está aqui, por escolha
declarada:

- **Análise fundamentalista de empresas específicas** — fora do escopo de um curso
  sobre onde investir R$ 6.000; exige contabilidade e um curso próprio.
- **Derivativos e day trade** — mencionados e desaconselhados; ensinar a operá-los
  contrariaria o que a evidência mostra para o investidor pessoa física.
- **Criptoativos** — tratados apenas como classe de risco e como vetor de fraude.
  Merecem assunto próprio nesta pasta, se você quiser.
- **Planejamento sucessório e tributário avançado** — assunto de especialista, e depende
  de patrimônio muito maior.
