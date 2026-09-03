# Engenharia de Software com IA — mapa do curso

**Do zero absoluto ao nível de pesquisa, em português.**
Escrito em 20/08/2026 · Ambiente de verificação: Ubuntu 22.04.5 LTS ·
Python 3.10.12 · Node v24.18.0 · Git 2.34.1 · Docker 29.7.2 ·
Claude Code 2.1.237

---

## A pergunta que originou este material

> *"O que é um dev que sabe usar IA?"*

A resposta que este curso desenvolve, justifica e ensina a executar:

> **É quem consegue verificar mais rápido do que a máquina consegue produzir.**

Não é quem escreve prompts melhores. Não é quem conhece mais ferramentas. É quem
**converte julgamento humano em verificação automática** rápido o bastante para
aceitar trabalho de máquina sem perder o controle do sistema.

Toda a estrutura do curso decorre disso:

```
   geração barata  ──►  verificação vira o gargalo  ──►  verificação humana
                                                          não escala
                                                                │
                        ┌───────────────────────────────────────┘
                        ▼
   só verificação automática escala  ──►  a habilidade é converter
                                          julgamento em verificação
```

---

## O que você saberá ao final

- Explicar, sem jargão, o que mudou no ofício — e o que **não** mudou.
- Instalar e operar as ferramentas atuais nos três sistemas operacionais, sem
  depender de nenhuma em particular.
- Escrever especificação que um agente executa sem inventar, com critérios
  numerados e verificáveis.
- Montar o **portão de verificação** que decide o que entra no repositório.
- Revisar código gerado por máquina com um método deliberado — porque a pista
  visual que você usava com código humano desapareceu.
- Projetar repositório e arquitetura legíveis por agente.
- Reconhecer e defender contra as ameaças novas: injeção indireta de prompt,
  pacote alucinado, vazamento de segredo por agente.
- Ler a evidência sobre produtividade sem ser enganado por vendedor nem por
  cético.
- Saber quanto custa, em dólar e em real, e onde o custo escapa.
- Reconhecer em que nível você está — e o que falta para o próximo.

---

## Se você tem pouco tempo

| Tempo | Leia |
|---|---|
| **25 minutos** | [01-introducao-leigo](01-introducao-leigo.md) |
| **1 hora** | [01](01-introducao-leigo.md) + [04-como-comecar](04-como-comecar.md) |
| **1 dia** | Bloco A inteiro, com o [projeto-modelo](07-projeto-modelo/README.md) rodando |
| **1 semana** | Bloco A + [10](10-fundamentos.md), [13](13-os-quatro-modos-de-uso.md), [16](16-especificacao-e-plano.md), [17](17-verificacao-e-testes.md), [18](18-revisao-de-codigo-gerado.md) |
| **1 mês** | Tudo, com os 14 laboratórios do [70-pratica](70-pratica.md) |

**Se você só quer o essencial:** [17-verificacao-e-testes](17-verificacao-e-testes.md).
É o arquivo mais importante do curso.

**Se você quer saber em que nível está:** [25-niveis-do-dev-com-ia](25-niveis-do-dev-com-ia.md).

**Se você lidera um time:** [24](24-produtividade-o-que-diz-a-evidencia.md) +
[27](27-times-e-organizacao.md).

**Se você é júnior e está preocupado:** [26-carreira-e-mercado](26-carreira-e-mercado.md), §3.

---

## Roteiro

### Bloco A · Porta de entrada

| # | Arquivo | Nível | O que tem |
|---|---|---|---|
| 01 | [introducao-leigo](01-introducao-leigo.md) | iniciante | A analogia da serraria, a escala L0–L5, os três mal-entendidos que precisam morrer |
| 02 | [pre-requisitos](02-pre-requisitos.md) | iniciante | O que saber antes, tempo realista por nível, rota de resgate, caminho de custo zero |
| 03 | [instalacao](03-instalacao.md) | iniciante | **Manual de campo:** 6 blocos de tecnologia, três SOs, PATH, permissões, proxy corporativo, desinstalação, 14 erros literais |
| 04 | [como-comecar](04-como-comecar.md) | iniciante | O ciclo completo em 40 minutos, com verificação e teste de mutação à mão |
| 05 | [manual-de-uso](05-manual-de-uso.md) | intermediário | Referência por tarefa: sessão, contexto, permissões, headless, custo, o que está obsoleto |
| 06 | [exemplos](06-exemplos.md) | todos | **12 exemplos completos**, incluindo 2 casos de produção |
| 07 | [projeto-modelo/](07-projeto-modelo/README.md) | intermediário | **`portao`** — portão de verificação executável, zero dependências, 49 testes |

### Bloco B · Núcleo

| # | Arquivo | Nível | O que tem |
|---|---|---|---|
| 10 | [fundamentos](10-fundamentos.md) | intermediário | A tese, a aritmética de por que a revisão não escala, os 4 modelos mentais, a regra de ouro |
| 11 | [historia](11-historia.md) | intermediário | De FORTRAN (1957) ao SDD (2026); por que MDA morreu e o que isso prevê |
| 12 | [o-modelo-por-dentro](12-o-modelo-por-dentro.md) | intermediário | Token, janela, amostragem, cache, ferramentas — e o **mapa de onde ele erra** |
| 13 | [os-quatro-modos-de-uso](13-os-quatro-modos-de-uso.md) | intermediário | Completar · conversar · editar · agir (+ o modo 5 assíncrono) |
| 14 | [contexto-e-o-repositorio](14-contexto-e-o-repositorio.md) | intermediário | "O repositório é o prompt": `AGENTS.md`, ADRs, gestão de sessão |
| 15 | [o-loop-do-agente](15-o-loop-do-agente.md) | avançado | O laço sem caixa-preta, os 6 modos de falha, a matemática de `p^n`, **agente em 80 linhas** |
| 16 | [especificacao-e-plano](16-especificacao-e-plano.md) | intermediário | Critérios decidíveis, EARS, SDD com crítica histórica, tamanho da fatia |
| 17 | [verificacao-e-testes](17-verificacao-e-testes.md) | avançado | **O arquivo central.** Pirâmide, mutação, propriedade, arquitetura, portão, cobertura do diff |
| 18 | [revisao-de-codigo-gerado](18-revisao-de-codigo-gerado.md) | avançado | Método em 6 passos, leitura dirigida em 6 passadas, catálogo de defeitos |
| 19 | [arquitetura-para-maquina](19-arquitetura-para-maquina.md) | avançado | Localidade, estados ilegais impossíveis, e a entropia arquitetural medida |
| 20 | [git-e-fluxo-de-trabalho](20-git-e-fluxo-de-trabalho.md) | intermediário | Regras não negociáveis, worktrees, atribuição, recuperação, fluxo completo |
| 21 | [ci-cd-e-agentes-em-producao](21-ci-cd-e-agentes-em-producao.md) | avançado | "O agente propõe, o CI decide", portão em Actions, dependências, métricas |
| 22 | [seguranca](22-seguranca.md) | avançado | Injeção indireta com CVEs reais, trinca letal, slopsquatting, isolamento, MCP |
| 23 | [licenca-propriedade-e-lei](23-licenca-propriedade-e-lei.md) | intermediário | Titularidade, contaminação, LGPD, atribuição, responsabilidade |
| 24 | [produtividade-o-que-diz-a-evidencia](24-produtividade-o-que-diz-a-evidencia.md) | avançado | METR, DORA, LinearB, GitClear, Stack Overflow — **com a metodologia junto** |
| 25 | [niveis-do-dev-com-ia](25-niveis-do-dev-com-ia.md) | intermediário | Rubrica L0–L5 com evidência observável, autoavaliação, perguntas de entrevista |
| 26 | [carreira-e-mercado](26-carreira-e-mercado.md) | intermediário | O que evaporou, o problema do júnior sem consolo, cargos, mercado brasileiro |
| 27 | [times-e-organizacao](27-times-e-organizacao.md) | avançado | Sequência de adoção, política mínima, capacidade de revisão, erosão de conhecimento |
| 60 | [teoria-avancada](60-teoria-avancada.md) | pesquisa | Teorema de Rice, inevitabilidade da alucinação, a matemática que verificação muda, Goodhart |
| 65 | [estado-da-arte](65-estado-da-arte.md) | avançado | Agosto/2026: capacidade, consensos, disputas, fronteiras, previsões datadas |

### Bloco C · Prática e erros

| # | Arquivo | O que tem |
|---|---|---|
| 70 | [pratica](70-pratica.md) | **14 laboratórios** progressivos + projeto final |
| 75 | [armadilhas](75-armadilhas.md) | 24 armadilhas, 14 mitos, 3 erosões de longo prazo |

### Bloco D · Economia e ecossistema

| # | Arquivo | O que tem |
|---|---|---|
| 80 | [custos-e-licencas](80-custos-e-licencas.md) | Preços de 20/08/2026 em USD e BRL, custos ocultos, licenças, modelo local |
| 85 | [cursos-e-certificacoes](85-cursos-e-certificacoes.md) | PT/EN/FR pesquisados na web, GH-300 detalhada, o que é certificado vs. certificação |

### Bloco E · Fontes

| # | Arquivo | O que tem |
|---|---|---|
| 90 | [bibliografia](90-bibliografia.md) | 15 obras com edição e ISBN conferidos; o que é legalmente gratuito |
| 95 | [referencias](95-referencias.md) | Só fontes primárias, com aviso sobre agregadores |
| — | [GLOSSARIO](GLOSSARIO.md) | ~70 termos definidos |

---

## As 12 camadas de profundidade

| # | Camada | Onde |
|---|---|---|
| 1 | Intuição para leigo | [01](01-introducao-leigo.md) — a serraria |
| 2 | Definição informal | [01](01-introducao-leigo.md) |
| 3 | Por que existe | [11-historia](11-historia.md) |
| 4 | Ambiente e primeiro uso | [03](03-instalacao.md), [04](04-como-comecar.md) |
| 5 | Fundamentos formais | [10](10-fundamentos.md), [12](12-o-modelo-por-dentro.md) |
| 6 | Mecânica interna | [15-o-loop-do-agente](15-o-loop-do-agente.md) — sem caixa-preta |
| 7 | Implementação prática | [06](06-exemplos.md), [07-projeto-modelo](07-projeto-modelo/README.md) |
| 8 | Casos de uso reais | [06](06-exemplos.md), exemplos 11 e 12 |
| 9 | Trade-offs e alternativas | [13](13-os-quatro-modos-de-uso.md), [19](19-arquitetura-para-maquina.md), [75](75-armadilhas.md) |
| 10 | Economia | [80](80-custos-e-licencas.md), [26](26-carreira-e-mercado.md), [27](27-times-e-organizacao.md) |
| 11 | Profundidade de pesquisa | [60-teoria-avancada](60-teoria-avancada.md) |
| 12 | Estado da arte e fronteira | [65-estado-da-arte](65-estado-da-arte.md) |

---

## O projeto-modelo

[`07-projeto-modelo/`](07-projeto-modelo/README.md) — **`portao`**, um portão de
verificação para código gerado por IA.

- **Python 3.10+, zero dependências.** Nem uma.
- Cinco regras: **escopo** (tocou só no que devia?) · **tamanho** (cabe numa
  revisão?) · **segredos** (vazou credencial?) · **pacotes** (dependência nova
  ou alucinada?) · **critérios** (todo `CA-NN` tem teste?).
- **49 testes, todos passando**, executados em Python 3.10.12.
- Dois diffs de exemplo: um limpo, um com as três falhas reais de agente (teste
  alterado, pacote alucinado, credencial colada).
- Verifica a si mesmo: os 12 critérios do `ESPEC.md` são citados pelos testes.
- **Nenhuma linha de IA dentro dele** — um portão precisa ser determinístico.

Ele existe porque é **a lição**: a ferramenta que ninguém instala e que é a
única que ainda vai importar daqui a cinco anos.

---

## Convenções deste material

- **Data no topo** de todo arquivo que envelhece.
- **Nível marcado** em cada arquivo.
- **Autoteste ao final** de cada arquivo — 8 a 12 perguntas.
- **Fato, consenso e opinião separados explicitamente.** Onde escrevo "minha
  opinião" ou "marcado como aposta", é isso mesmo.
- **Nenhum número, livro, link ou preço inventado.** Onde não confirmei, omiti.
- **Fontes primárias**, com data de consulta no rodapé dos arquivos pesquisados.

---

## Status

| Bloco | Status |
|---|---|
| A · Porta de entrada | ✅ completo |
| B · Núcleo | ✅ completo (10 → 65) |
| C · Prática e erros | ✅ completo |
| D · Economia e ecossistema | ✅ completo |
| E · Fontes | ✅ completo |
| Glossário | ✅ completo |

**Manutenção:** ver [95-referencias](95-referencias.md), §8 — o que reavaliar e
com que frequência.

---

## Por onde começar

Vá para [01-introducao-leigo](01-introducao-leigo.md).
