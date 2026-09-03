# Estatística Descritiva — Mapa do Assunto

`Nível: do zero absoluto ao de pesquisa` · `Última atualização: 20/08/2026`
`Base: Python 3.10.12 · biblioteca padrão apenas · Ubuntu 22.04.5`

> **Status: 🟡 EM PRODUÇÃO.** Blocos A e B completos e verificados; C parcial; D e E pendentes.
> Ver "O que falta", no fim.

---

## A pergunta que originou o material

*"Estatística: o que são desvio padrão, média, mediana, erro e outras medidas nesse contexto?
O que elas significam e representam na realidade?"*

Resposta curta, para não esperar a leitura:

- **Média** = o ponto de equilíbrio da gangorra. Serve para **totais**; quebra com outliers.
- **Mediana** = quem está no meio da fila. Serve para o **caso típico**; ignora magnitude.
- **Desvio padrão** = a distância típica entre um valor qualquer e a média.
- **Erro** = **não é engano**. É a distância inevitável entre o que você mediu e a verdade —
  e ele se divide em **aleatório** (mais dados resolvem) e **sistemático** (mais dados só
  tornam a resposta errada mais precisa).
- **A regra de ouro:** posição sem dispersão é meia informação; e um número sem sua incerteza
  é uma opinião com aparência de fato.

O desenvolvimento completo dessa resposta está em
[01-introducao-leigo.md](01-introducao-leigo.md) e, para "erro", em
[15-erro-e-incerteza.md](15-erro-e-incerteza.md) — o arquivo central do curso.

---

## Roteiros de leitura

| Caminho | Sequência |
|---|---|
| **Só entender** (40 min) | `01` |
| **Emergência** (3 h) | `01` → `04` → `12` → `13` → `15` → `75` |
| **Praticante** (2–3 semanas) | `01` → `02` → `03` → `04` → `06` → `07` → `10` → `12` → `13` → `14` → `15` → `19` → `75` |
| **Quem lê artigo científico** | `10` → `15` → `17` → `18` → `16` → `65` |
| **Quem faz A/B test** | `15` → `17` → `18` → `20` → `65` (§65.3) |
| **Quem só quer a resposta sobre "erro"** | `15` (inteiro), depois `17` |
| **Nível pesquisa** | tudo → `60` → `65` |

---

## Arquivos

### BLOCO A · Porta de entrada — ✅ completo

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [01-introducao-leigo.md](01-introducao-leigo.md) | iniciante | Zero jargão. Gangorra, fila, o rio de 1,20 m, o bar com Bill Gates |
| [02-pre-requisitos.md](02-pre-requisitos.md) | iniciante | O que é bloqueante (pouco), tempos honestos, rota de resgate |
| [03-instalacao.md](03-instalacao.md) | iniciante | Manual de campo: Python, R, JASP, jamovi, planilha, 3 SOs, PATH, proxy, 14 erros literais |
| [04-como-comecar.md](04-como-comecar.md) | iniciante | Do ambiente pronto ao primeiro resumo honesto, com saídas reais |
| [05-manual-de-uso.md](05-manual-de-uso.md) | intermediário | Notação + API por tarefa + equivalência Python/NumPy/pandas/R/planilha/SQL |
| [06-exemplos.md](06-exemplos.md) | inic./avançado | **14 exemplos executados**, incl. Simpson (Charig 1986), Anscombe, cauda em microsserviços |
| [07-projeto-modelo/](07-projeto-modelo/README.md) | intermediário | `resumo`: relatório que **avisa quando não acreditar nele**. **83 testes passando** |

### BLOCO B · Núcleo — ✅ completo

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [10-fundamentos.md](10-fundamentos.md) | inic./int. | População × amostra, escalas de Stevens, medidas como problemas de minimização |
| [11-historia.md](11-historia.md) | iniciante | 1662 a 2026. Graunt, Gauss, Quetelet, Galton, Gosset, Fisher, Tukey, Efron |
| [12-medidas-de-posicao.md](12-medidas-de-posicao.md) | intermediário | Média provada, mediana provada, aparada, geométrica, harmônica, quantis |
| [13-medidas-de-dispersao.md](13-medidas-de-dispersao.md) | intermediário | 🔑 O `n−1` medido, MAD, IQR, CV, Chebyshev, por que variâncias somam |
| [14-forma-e-distribuicoes.md](14-forma-e-distribuicoes.md) | int./avançado | Assimetria, o mito da curtose, log-normal, Pareto, Cauchy que não converge |
| [15-erro-e-incerteza.md](15-erro-e-incerteza.md) | int./avançado | 🔑 **O coração do curso.** DP × EP, IC, margem, propagação, GUM, viés-variância |
| [16-relacao-entre-variaveis.md](16-relacao-entre-variaveis.md) | int./avançado | Correlação, suas 5 falhas, colisor, Simpson, causa |
| [17-amostragem-lgn-tcl.md](17-amostragem-lgn-tcl.md) | int./avançado | Literary Digest, LGN, TCL medido, `EP = σ/√n` derivado, tamanho de amostra |
| [18-inferencia-p-e-ic.md](18-inferencia-p-e-ic.md) | avançado | Valor-p e as 6 coisas que ele não é; p-hacking medido; taxa de base |
| [19-robustez-e-outliers.md](19-robustez-e-outliers.md) | int./avançado | Ponto de ruptura medido, mascaramento, a cerca que erra 7,7% |
| [20-visualizacao-de-medidas.md](20-visualizacao-de-medidas.md) | intermediário | O que cada gráfico esconde; ECDF; regras de honestidade |
| [60-teoria-avancada.md](60-teoria-avancada.md) | pesquisa | Bessel demonstrada, Cramér-Rao, função de influência, bootstrap, Stein |
| [65-estado-da-arte.md](65-estado-da-arte.md) | pesquisa | e-values, conformal, DML, privacidade diferencial, onde a reforma chegou |

### BLOCO C · Prática e erros — 🟡 parcial

| Arquivo | Status |
|---|---|
| [70-pratica.md](70-pratica.md) | ✅ 14 laboratórios |
| `75-armadilhas.md` | ⬜ **pendente** |

### BLOCO D · Economia e ecossistema — ⬜ pendente

| Arquivo | Status |
|---|---|
| `80-custos-e-licencas.md` | ⬜ pendente |
| `85-cursos-e-certificacoes.md` | ⬜ pendente (exige busca web em PT/EN/FR) |

### BLOCO E · Fontes — ⬜ pendente

| Arquivo | Status |
|---|---|
| `90-bibliografia.md` | ⬜ pendente |
| `95-referencias.md` | ⬜ pendente |
| `GLOSSARIO.md` | ⬜ pendente |

---

## Verificação

- **Todo código publicado foi executado** em Python 3.10.12 (Ubuntu 22.04.5) em 20/08/2026.
  As saídas mostradas são as reais; três afirmações do texto foram corrigidas depois de a
  execução as contrariar.
- **Projeto-modelo:** 83 testes, todos passando. A distribuição t implementada do zero bate
  com as tabelas impressas até a 4ª casa (`t(0,95; 9) = 2,2622`).
- **Um bug real do projeto foi mantido como lição**: o detector de separador decimal leu
  alturas de 1,734 m como 1.734, e o episódio virou a seção 7 do README do projeto.
- Versões de software pesquisadas na web em 20/08/2026 (Python 3.14.7/3.13.15, NumPy 2.5.2,
  R 4.6.1 "Happy Hop", JASP 0.98.1, jamovi 28.2).

## O que falta

`75-armadilhas.md`, blocos D (`80`, `85`) e E (`90`, `95`), e o `GLOSSARIO.md`.
