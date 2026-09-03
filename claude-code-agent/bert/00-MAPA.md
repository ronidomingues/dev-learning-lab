# BERT — Mapa do Assunto

`Nível: do zero absoluto ao de pesquisa` · `Última atualização: 12/08/2026`
`Base: transformers 5.15.0 · torch 2.13.0 · Python 3.12 · BERTimbau / ModernBERT`

---

## O que é este material

Um curso completo sobre **BERT** e a família de modelos *encoder*: o que é, como funciona
por dentro, como usar em produção, quanto custa, e onde o campo está em agosto de 2026.

A pergunta que originou o material foi *"o que é o BERT (um mini LLM)?"*. A resposta curta
está na primeira página, e vale antecipar aqui: **BERT não é um LLM pequeno — é outra
espécie de modelo.** ChatGPT escreve; BERT lê. Os dois nasceram do mesmo artigo de 2017 e
seguiram caminhos opostos.

Este curso responde, na ordem em que as perguntas realmente aparecem:

1. **O que é isso e por que existe?** → `01` e `11`
2. **Como eu começo hoje, sem gastar nada?** → `02` a `07`
3. **Como funciona por dentro, e onde estão os limites?** → `10` a `65`
4. **Como coloco em produção sem me arrepender?** → `18`, `19`, `75`

---

## O que você saberá ao final

- Explicar para um leigo o que BERT faz e por que ele não é um ChatGPT pequeno.
- Instalar todo o ambiente, em qualquer sistema operacional — ou começar sem instalar nada.
- Afinar um modelo nos seus próprios dados e saber, com honestidade, se ele está bom.
- Escolher entre BERT e LLM com base em custo, latência e volume — com números.
- Entender a atenção a ponto de calculá-la no papel e implementá-la em PyTorch puro.
- Construir busca semântica e a camada de recuperação de um RAG que funciona.
- Servir um modelo com latência de dezenas de milissegundos, em CPU comum.
- Detectar vazamento de dados, atalhos espúrios, viés e deriva antes que virem incidente.
- Ler a literatura da área, incluindo os papers de 2025–2026, com senso crítico.

---

## Roteiro de leitura

### Caminho rápido (uma tarde, "quero entender e mexer")
`01` → `03` → `04` → `07-projeto-modelo/` → `75`

### Caminho do praticante (2 a 3 semanas)
`01` → `02` → `03` → `04` → `06` → `07` → `10` → `15` → `18` → `70` → `75`

### Caminho de quem faz RAG / busca
`01` → `04` → `10` → `16` → `17` → `18` → `19` → `70` (lab 8)

### Caminho de quem coloca em produção
`03` → `07` → `15` → `18` → `19` → `75` → `80`

### Caminho de pesquisa
todo o Bloco B em ordem, com peso em `13`, `14`, `20`, `60`, `65` → depois `95`

### Caminho de quem decide compra
`01` → `11` → `80` → `65` → `75`

---

## Arquivos

### BLOCO A · Porta de entrada (01–09)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [01-introducao-leigo.md](01-introducao-leigo.md) | iniciante | O que é, por que não é um LLM pequeno, para que serve hoje. Zero jargão. |
| [02-pre-requisitos.md](02-pre-requisitos.md) | iniciante | O que saber e ter antes. Tempo realista. Rota de resgate. |
| [03-instalacao.md](03-instalacao.md) | iniciante | Manual de campo: Python, PyTorch, transformers, por SO, com tabela de erros. **Testado.** |
| [04-como-comecar.md](04-como-comecar.md) | iniciante | Do ambiente pronto ao primeiro resultado, com saídas reais. |
| [05-manual-de-uso.md](05-manual-de-uso.md) | intermediário | Referência consultável: classes, tokenizador, Trainer, CLI, obsoletos. |
| [06-exemplos.md](06-exemplos.md) | intermediário | 12 receitas completas e executáveis, com saída real de cada uma. |
| [07-projeto-modelo/](07-projeto-modelo/README.md) | intermediário | Triagem de chamados em português. Treina em 60 s de CPU. **Roda de verdade.** |

### BLOCO B · Núcleo (10–69)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [10-fundamentos.md](10-fundamentos.md) | iniciante→interm. | Vocabulário, modelos mentais, bi-encoder × cross-encoder, o que BERT não faz. |
| [11-historia.md](11-historia.md) | iniciante→interm. | De n-gramas a mmBERT. Por que o BERT é como é (os cinco porquês). |
| [12-tokenizacao-wordpiece.md](12-tokenizacao-wordpiece.md) | intermediário | Como texto vira número. WordPiece, BPE, os bugs clássicos. |
| [13-arquitetura-encoder.md](13-arquitetura-encoder.md) | interm.→avançado | A atenção calculada à mão, número por número. Um bloco em PyTorch puro. |
| [14-pre-treino-mlm-nsp.md](14-pre-treino-mlm-nsp.md) | interm.→avançado | MLM, a regra 80/10/10, por que NSP morreu, custo real do pré-treino. |
| [15-fine-tuning.md](15-fine-tuning.md) | intermediário | A receita padrão, quantos dados, congelamento, o que dá errado. |
| [16-embeddings-e-busca-semantica.md](16-embeddings-e-busca-semantica.md) | interm.→avançado | Sentence-BERT, pooling, busca híbrida, o papel do encoder no RAG. |
| [17-familia-bert.md](17-familia-bert.md) | intermediário | RoBERTa, DistilBERT, DeBERTa, ModernBERT, mmBERT: qual usar e por quê. |
| [18-avaliacao-e-benchmarks.md](18-avaliacao-e-benchmarks.md) | intermediário | Métricas, limiar, vazamento, intervalo de confiança, model card. |
| [19-producao-e-otimizacao.md](19-producao-e-otimizacao.md) | avançado | Lote, ONNX, quantização, destilação, Docker, monitoramento de deriva. |
| [20-interpretabilidade-e-bertologia.md](20-interpretabilidade-e-bertologia.md) | avançado | O que cada camada aprende, atalhos espúrios, viés, por que atenção ≠ explicação. |
| [60-teoria-avancada.md](60-teoria-avancada.md) | pesquisa | Derivações, complexidade, limites em `TC⁰`, pseudo-verossimilhança, problemas abertos. |
| [65-estado-da-arte.md](65-estado-da-arte.md) | avançado | O renascimento dos encoders. ModernBERT, mmBERT, moBERTo. Encoder × LLM, com dados. |

### BLOCO C · Prática e erros (70–79)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [70-pratica.md](70-pratica.md) | todos | 12 laboratórios progressivos, com critério de sucesso, + projeto final. |
| [75-armadilhas.md](75-armadilhas.md) | todos | 8 mitos, erros de dados, modelagem, avaliação, produção e negócio. |

### BLOCO D · Economia e ecossistema (80–89)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [80-custos-e-licencas.md](80-custos-e-licencas.md) | todos | Preços com data, licenças, encoder × LLM em reais, quem paga a conta. |
| [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) | todos | Cursos gratuitos PT/EN/FR pesquisados na web; a verdade sobre certificações. |

### BLOCO E · Fontes (90–99)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [90-bibliografia.md](90-bibliografia.md) | todos | Livros com edição e ano, o que envelheceu, o que é legalmente gratuito. |
| [95-referencias.md](95-referencias.md) | todos | ~45 papers, documentação, código para ler, modelos, pessoas, ferramentas. |
| [GLOSSARIO.md](GLOSSARIO.md) | todos | ~130 termos definidos, do A ao Z. |

---

## As 12 camadas de profundidade, e onde cada uma está

| # | Camada | Onde |
|---|---|---|
| 1 | Intuição para leigo | `01` |
| 2 | Definição informal | `01`, `10` |
| 3 | Por que existe | `11` |
| 4 | Ambiente e primeiro uso | `03`, `04` |
| 5 | Fundamentos formais | `10`, `12` |
| 6 | Mecânica interna | `13`, `14` |
| 7 | Implementação prática | `06`, `07`, `15` |
| 8 | Casos de uso reais | `06`, `16`, `19` |
| 9 | Trade-offs e alternativas | `17`, `18`, `75` |
| 10 | Economia do assunto | `80` |
| 11 | Profundidade de pesquisa | `60`, `20` |
| 12 | Estado da arte e fronteira | `65` |

---

## O que foi verificado de verdade

Este material não confia na memória em nada que possa estar desatualizado:

- **Versões e instalação** — conferidas nos índices oficiais (PyPI, `download.pytorch.org`)
  em 11–12/08/2026. O caminho Linux + CPU foi **executado**, resultando em
  `torch 2.13.0+cpu`, `transformers 5.15.0`, `datasets 5.0.1`.
- **Todos os exemplos de código** dos arquivos `04`, `06` e `13` foram **executados**, e as
  saídas mostradas são as reais — incluindo as que expõem falhas do modelo.
- **O projeto-modelo** foi treinado e avaliado nesta máquina: 0,917 de acurácia, 0,912 de
  F1 macro, 11 testes passando, API respondendo em 35–43 ms.
- **Preços, cursos e papers** — pesquisados na web em 12/08/2026, com data e link no rodapé
  de cada arquivo.
- **API do `transformers` 5** — conferida contra o código-fonte da biblioteca, não contra a
  memória (foi assim que a tabela v4 → v5 do `03` foi montada).

---

## Status por bloco

| Bloco | Status | Observação |
|---|---|---|
| **A · Porta de entrada** | ✅ completo | 7 documentos + projeto executável e testado |
| **B · Núcleo** | ✅ completo | 13 documentos, dos fundamentos aos limites teóricos |
| **C · Prática e erros** | ✅ completo | 12 laboratórios + catálogo de armadilhas |
| **D · Economia** | ✅ completo | preços datados; cursos PT/EN/FR pesquisados |
| **E · Fontes** | ✅ completo | bibliografia verificada, referências reais |
| **Glossário** | ✅ completo | ~130 termos |

**Pendente:** nada de estrutura. Reavaliar `65-estado-da-arte.md` e `80-custos-e-licencas.md`
a cada 6 meses — são os dois arquivos que envelhecem rápido. Se o **moBERTo** ganhar adoção
e derivados, ele passa a ser o modelo padrão dos exemplos em português, no lugar do
BERTimbau.

---

## Por onde começar, agora

Se você leu até aqui e quer só uma coisa para fazer em seguida:

**[01-introducao-leigo.md](01-introducao-leigo.md)** — 15 minutos, sem jargão, e resolve a
confusão entre BERT e LLM de uma vez.

Se você tem pressa e quer código rodando:
**[03-instalacao.md § Colab](03-instalacao.md#alternativa-sem-instalar-nada)** →
**[04-como-comecar.md](04-como-comecar.md)**. Dez minutos até o primeiro resultado.

---

*Volta para o [índice geral](../INDICE.md)*
