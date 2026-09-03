# 80 · Custos e licenças

`Nível: todos` · `**Preços consultados em 12/08/2026**` · `Câmbio usado: US$ 1 ≈ R$ 5,15`

> **Primeira linha, para tirar a dúvida principal:** aprender e usar BERT é
> **gratuito**. Os modelos são abertos, as bibliotecas são livres, e ele roda no
> computador que você já tem. Você só paga se escolher pagar — por GPU, por nuvem ou por
> serviço gerenciado. Quem paga a conta está explicado na seção 6.

---

## 1 · O que é gratuito

| Item | Custo | Licença |
|---|---|---|
| **BERT original** (Google) | US$ 0 | Apache 2.0 |
| **BERTimbau** (NeuralMind/Unicamp) | US$ 0 | MIT |
| **ModernBERT** (Answer.AI + LightOn) | US$ 0 | Apache 2.0 |
| **mmBERT**, **NeoBERT** | US$ 0 | MIT / Apache 2.0 |
| **transformers**, **datasets**, **tokenizers**, **accelerate** (Hugging Face) | US$ 0 | Apache 2.0 |
| **PyTorch** | US$ 0 | BSD-3-Clause |
| **sentence-transformers** | US$ 0 | Apache 2.0 |
| **scikit-learn**, **pandas**, **NumPy** | US$ 0 | BSD-3-Clause |
| Baixar modelos do Hugging Face Hub | US$ 0, sem conta obrigatória | — |
| **Google Colab** (GPU T4, com limites) | US$ 0 | — |
| **Kaggle Notebooks** (~30 h/semana de GPU) | US$ 0 | — |

**Nenhum item deste curso exige cartão de crédito.** Todo o material, incluindo o
[projeto-modelo](07-projeto-modelo/README.md), roda em CPU comum ou em GPU gratuita.

---

## 2 · Licenças: o que você pode fazer

| Licença | Uso comercial | Modificar | Redistribuir | Obrigação |
|---|---|---|---|---|
| **Apache 2.0** | sim | sim | sim | manter aviso de copyright; concede patentes |
| **MIT** | sim | sim | sim | manter aviso de copyright |
| **BSD-3-Clause** | sim | sim | sim | manter aviso; não usar o nome para endosso |
| **CC-BY-NC** | **NÃO** | sim | sim | não comercial — cuidado |
| **Llama Community License** | sim, com teto de usuários | sim | com condições | específica; leia |

**A pilha padrão deste curso é 100% permissiva** e pode ser usada comercialmente sem
pagar nada e sem abrir seu código.

### Três armadilhas de licença que já custaram caro a gente

1. **O modelo é livre, os dados de treino podem não ser.** Um modelo treinado em corpus
   proprietário pode carregar restrições que não aparecem no arquivo `LICENSE`. Leia o
   *model card* inteiro, não só a etiqueta.
2. **Modelos CC-BY-NC existem no Hub e parecem iguais aos outros.** Vários modelos de
   embedding e rerankers populares são não-comerciais. Verifique **antes** de colocar em
   produção — descobrir depois é caro.
3. **Modelo afinado herda a licença do modelo base.** Se você afinar um modelo NC, seu
   modelo resultante também é NC. Não existe lavagem de licença por fine-tuning.

**Verifique sempre:** a página do modelo no Hub mostra a licença no topo. Em caso de
dúvida em contexto comercial, consulte o jurídico — este arquivo não é aconselhamento legal.

---

## 3 · Onde o dinheiro aparece de verdade

O software é grátis; o projeto não é. Custo típico de um projeto real de classificação:

| Item | Fatia do custo | Comentário |
|---|---|---|
| **Rotulagem de dados** | 40–60% | o maior de todos, e o mais subestimado |
| **Engenharia** (dados, treino, avaliação) | 25–40% | semanas de pessoa, não de GPU |
| **Infraestrutura de treino** | 2–10% | GPU por horas, não por meses |
| **Inferência em produção** | 5–15% | contínuo, mas barato com encoder |
| **Manutenção e retreino** | 10–20%/ano | esquecido em 90% dos orçamentos |

**Rotulagem, com números:** um anotador rotulando texto curto faz de 100 a 400 itens por
hora. Para 5.000 exemplos: 15 a 50 horas. A R$ 40/h internos, isso é **R$ 600 a R$ 2.000**;
com fornecedor especializado e dupla anotação, 2 a 4× isso. Domínio técnico (jurídico,
médico) exige especialista e o custo pode decuplicar.

---

## 4 · Custo de computação

### Treinar (afinar)

| Cenário | Onde | Tempo | Custo |
|---|---|---|---|
| 200 exemplos, BERT-base | CPU do seu notebook | 1 min | R$ 0 |
| 5.000 exemplos, BERT-base | Colab grátis (T4) | 5 min | R$ 0 |
| 50.000 exemplos, BERT-base | Colab grátis (T4) | 40 min | R$ 0 |
| 50.000 exemplos, BERT-large | GPU alugada (L4) | 1,5 h | ~US$ 1,20 (≈ R$ 6) |
| MLM contínuo, 500 MB de texto | GPU alugada (A100) | 10 h | ~US$ 45 (≈ R$ 230) |
| Pré-treino do zero, BERT-base | cluster | dias | US$ 2.000–10.000 |

**Você não vai pré-treinar do zero.** Essa linha existe só para mostrar a escala do
presente que o Google, a Meta e a Answer.AI deram ao mundo.

### Servir em produção

Preços de referência, consultados em 12/08/2026:

| Opção | Preço | Observação |
|---|---|---|
| Sua própria máquina/VPS com CPU | R$ 50–300/mês | resolve a maioria dos casos |
| AWS EC2 `g6.xlarge` (1× L4) | US$ 0,8048/h ≈ **US$ 580/mês** | só se precisar de GPU 24×7 |
| AWS EC2 `g5.xlarge` (1× A10G) | US$ 1,006/h ≈ US$ 725/mês | geração anterior, mais cara |
| Hugging Face Inference Endpoints — CPU | a partir de **US$ 0,033/h** | cobrado por minuto; escala a zero |
| Hugging Face Inference Endpoints — GPU | US$ 0,50/h (T4) a US$ 74/h (topo) | idem |
| Hugging Face Spaces — CPU básico | **grátis** | para demonstração |
| Hugging Face Spaces — GPU | US$ 0,40/h (T4 small) a US$ 23,50/h (8× L40S) | |

**Conta que quase ninguém faz:** 1 milhão de classificações por dia é ~12 por segundo em
média. Com ONNX int8 em 4 núcleos de CPU, isso cabe folgado numa máquina de
**R$ 150–300/mês**. Provisionar GPU para essa carga é desperdiçar de 20 a 100× o valor.

### Planos do Hugging Face (12/08/2026)

| Plano | Preço | Para quem |
|---|---|---|
| Free | US$ 0 | todo mundo que só baixa e publica modelos públicos |
| PRO | **US$ 9/mês** | 10× armazenamento privado, 20× créditos de inferência, 8× cota ZeroGPU |
| Team | **US$ 20/usuário/mês** | SSO, log de auditoria, grupos de recurso |
| Enterprise | **US$ 50/usuário/mês** | SCIM, suporte dedicado, limites máximos |
| Armazenamento no Hub | US$ 12/TB/mês (público), US$ 18/TB/mês (privado) | egress e CDN incluídos |

Google Colab Pro custa **US$ 9,99–11,99/mês** (as fontes divergem, e o preço varia por
região) e Colab Pro+ **US$ 49,99/mês**, ambos por sistema de "unidades de computação" —
não por horas garantidas. Confira o valor em BRL na própria página de compra antes de
assinar.

---

## 5 · A comparação que decide o projeto: encoder × LLM

Este é o número que costuma fechar a discussão. Considere **1 milhão de classificações de
texto curto** (~200 tokens de entrada, ~10 de saída).

**Via API de LLM** (preços da API da Anthropic, consultados em 12/08/2026):

| Modelo | Entrada | Saída | Custo de 1 milhão de classificações |
|---|---|---|---|
| Claude Haiku 4.5 | US$ 1 / MTok | US$ 5 / MTok | ~US$ 250 (≈ **R$ 1.290**) |
| Claude Sonnet 5 | US$ 3 / MTok | US$ 15 / MTok | ~US$ 750 (≈ **R$ 3.860**) |
| Claude Opus 5 | US$ 5 / MTok | US$ 25 / MTok | ~US$ 1.250 (≈ **R$ 6.440**) |

(Conta: 1M × 200 tokens = 200 MTok de entrada; 1M × 10 = 10 MTok de saída. *Prompt caching*
e a API de lotes reduzem isso substancialmente — a de lotes pela metade — mas não mudam a
ordem de grandeza da comparação.)

**Via BERT afinado, na sua máquina:**

| Item | Custo |
|---|---|
| Servidor CPU 4 núcleos, mês inteiro | ~R$ 200 |
| Processar 1 milhão de textos (ONNX int8, ~4 h de CPU) | incluso no mês |
| **Total** | **~R$ 200/mês, para qualquer volume que caiba na janela** |

**Diferença: uma a duas ordens de grandeza** — e essa é exatamente a conclusão da
literatura de 2026 sobre seleção de modelo com consciência de custo
([65-estado-da-arte.md](65-estado-da-arte.md)).

**Mas some o custo humano antes de decidir:** o BERT exige rotulagem (R$ 600–2.000) e
engenharia (2 a 6 semanas). O ponto de equilíbrio aparece nesta pergunta:

```
Volume mensal baixo  (< ~50 mil/mês)  → LLM via API. O custo humano do BERT não se paga.
Volume mensal alto   (> ~500 mil/mês) → BERT afinado. A economia paga a engenharia em semanas.
Zona intermediária                     → híbrido: LLM rotula 2.000 exemplos, BERT serve o resto.
```

O padrão híbrido é o que mais cresceu, e é honestamente o melhor conselho para a maioria
dos times: **pague caro uma vez pelo rótulo, barato para sempre pela inferência.**

---

## 6 · Quem paga a conta, e por quê

Se tudo é grátis, alguém está financiando. Entender isso ajuda a prever o que vai
continuar existindo:

| Quem | O que dá | Por que dá |
|---|---|---|
| **Google, Meta, Microsoft** | modelos e pesquisa | atrair talento, definir o padrão que roda melhor na infra deles, publicar para recrutar |
| **Hugging Face** | Hub, bibliotecas, largura de banda | modelo *freemium*: o grátis cria o ecossistema, a receita vem de PRO, Enterprise, Endpoints e armazenamento |
| **NVIDIA** | CUDA, bibliotecas, otimizações | vender GPU. O software gratuito é o que torna a GPU indispensável |
| **Universidades** (Unicamp, JHU) | modelos como BERTimbau e mmBERT | pesquisa pública financiada por agências de fomento |
| **Answer.AI, LightOn** | ModernBERT | reputação, consultoria e produtos ao redor |

**Consequência prática:** o risco de o BERT "ficar pago" é baixíssimo — pesos publicados
sob Apache 2.0/MIT não podem ser retirados retroativamente. Já os *serviços* (Hub,
Endpoints, Colab) podem mudar de preço a qualquer momento. Se algo é crítico para você,
**guarde uma cópia local dos pesos** e não dependa de download em produção
([19-producao-e-otimizacao.md](19-producao-e-otimizacao.md)).

---

## 7 · Custos ocultos

Os que costumam faltar no orçamento:

| Custo oculto | Ordem de grandeza | Como evitar |
|---|---|---|
| **Rotulagem contínua** | recorrente, para sempre | orçar retreino anual desde o início |
| **Retreino por deriva** | 1 a 4 vezes por ano | monitorar deriva ([19](19-producao-e-otimizacao.md)) |
| **Armazenamento de modelos** | GB por versão | política de retenção; não guarde tudo |
| **Egress de nuvem** | US$ 0,08–0,12/GB (AWS/GCP) | manter modelo e serviço na mesma região; o HF não cobra egress |
| **Tempo de espera de GPU gratuita** | horas perdidas | Kaggle tem cota mais previsível que Colab |
| **Aprisionamento em API** | 100% do custo, se precisar sair | encoder próprio é justamente a saída |
| **Conformidade / LGPD** | jurídico, DPIA | encoder local reduz muito o problema |
| **Rotatividade de pessoas** | conhecimento que evapora | model card e README obrigatórios |

**Sobre aprisionamento:** este é o argumento estratégico mais forte a favor de encoders
próprios. Um modelo afinado que você treinou é **seu**: roda em qualquer lugar, não muda
sozinho, não sobe de preço e não é descontinuado por decisão de terceiro. Modelos de API
já foram aposentados com meses de aviso — e todo mundo que dependia deles teve que migrar
no prazo do fornecedor.

---

## 8 · Alternativas gratuitas a cada serviço pago

| Serviço pago | Alternativa grátis | O que você perde |
|---|---|---|
| HF Inference Endpoints | seu próprio FastAPI + Docker | você opera, escala e monitora |
| HF PRO (armazenamento privado) | repositório Git com LFS, ou bucket próprio | integração com o Hub |
| Colab Pro | Kaggle (~30 h/semana) | menos flexibilidade de ambiente |
| Banco vetorial gerenciado | FAISS local ou pgvector | operação por sua conta |
| Anotação (Labelbox, Scale) | doccano, Label Studio (auto-hospedados) | gestão de anotadores e QA |
| Rastreamento de experimentos (W&B pago) | MLflow ou TensorBoard locais | colaboração e histórico gerenciado |

O padrão do curso é sempre a coluna do meio.

---

## Autoteste

1. Qual é o custo de licença para usar BERTimbau comercialmente?
2. Quais são as três armadilhas de licença? Por que fine-tuning não "lava" uma licença NC?
3. Qual é a maior fatia de custo de um projeto real, e quanto ela costuma pesar?
4. Quanto custa afinar um BERT-base com 50 mil exemplos? E pré-treinar do zero?
5. Faça a conta: 1 milhão de classificações por LLM (Haiku) versus por BERT em CPU própria.
6. A partir de que volume mensal o BERT afinado começa a compensar? Qual é o padrão híbrido?
7. Quem paga a conta do Hugging Face, e o que isso implica sobre o que pode mudar de preço?
8. Cite três custos ocultos e como evitá-los.
9. Por que aprisionamento é o argumento estratégico mais forte a favor de encoder próprio?

---

## Fontes consultadas (12/08/2026)

- [Hugging Face — Pricing](https://huggingface.co/pricing) — planos, armazenamento, Spaces, Inference Endpoints
- [Hugging Face — Inference Providers pricing](https://huggingface.co/docs/inference-providers/pricing)
- [AWS EC2 — g6.xlarge / g5.xlarge](https://instances.vantage.sh/aws/ec2/g5.xlarge) — US$ 0,8048/h e US$ 1,006/h em us-east-1
- [Google Colab — pricing](https://cloud.google.com/colab/pricing)
- Preços da API da Anthropic (Haiku 4.5, Sonnet 5, Opus 5) — conforme tabela oficial vigente em 12/08/2026
- Câmbio USD/BRL ≈ 5,15 — [investing.com](https://br.investing.com/currencies/usd-brl), [wise.com](https://wise.com/br/currency-converter/dolar-hoje)
- Licenças verificadas nos *model cards*: [neuralmind/bert-base-portuguese-cased](https://huggingface.co/neuralmind/bert-base-portuguese-cased) (MIT), [answerdotai/ModernBERT-base](https://huggingface.co/answerdotai/ModernBERT-base) (Apache 2.0), [google-research/bert](https://github.com/google-research/bert) (Apache 2.0)

> Preços mudam. **Reconfira antes de tomar decisão financeira** — esta página tem data e
> ela é o que separa informação de desinformação.

---

*Anterior: [75-armadilhas.md](75-armadilhas.md) · Próximo: [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md)*
