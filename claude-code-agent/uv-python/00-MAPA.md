# uv — do primeiro comando ao algoritmo de resolução

> **Curso completo sobre o `uv`**, o gerenciador de pacotes e projetos Python escrito em
> Rust pela Astral.
> **Escrito em:** 31/08/2026 · **Versão de referência:** uv **0.12.7** (lançada em
> 27/08/2026) · **Verificado em:** Ubuntu 22.04.5 LTS, x86-64, Python 3.10.12 e 3.14.7.

---

## O que você saberá ao final

**Nível de uso:**
- instalar o uv em Linux, macOS e Windows (nativo e WSL2), com verificação a cada passo;
- criar projetos, adicionar dependências, executar código — sem nunca ativar um ambiente
  virtual à mão;
- escrever scripts de um arquivo só com dependências declaradas (PEP 723);
- usar e instalar ferramentas de terminal sem poluir nada (`uvx`, `uv tool`);
- gerenciar várias versões de Python sem `pyenv`;
- montar workspaces de monorepo com um único lockfile;
- construir e publicar pacotes no PyPI com Trusted Publishing.

**Nível de entendimento:**
- explicar as três camadas — declaração, resolução, materialização — e por que confundi-las
  causa quase todos os erros;
- entender o algoritmo **PubGrub** e por que as mensagens de erro do uv são legíveis;
- entender **resolução universal** e *forking*, e por que um lock serve para todas as
  plataformas;
- entender por que a instalação é rápida: hard links, cache de wheels extraídos, PEP 658;
- provar que resolução de dependências é NP-completa, e explicar por que funciona mesmo assim;
- avaliar com honestidade o risco de fornecedor depois da aquisição pela OpenAI.

**Nível de operação:**
- Dockerfiles com camadas corretas, CI com portões que pegam o erro certo;
- defesa contra confusão de dependência, typosquatting e pacote comprometido;
- migração real, com rota de volta, de pip, Poetry, Pipenv e conda.

---

## Roteiro de leitura

### Se você tem 1 hora
[01](01-introducao-leigo.md) → [03](03-instalacao.md) (só a seção do seu SO) →
[04](04-como-comecar.md)

### Se você tem um fim de semana
Bloco A inteiro (01 a 07) → labs 1 a 5 do [70](70-pratica.md) → [75](75-armadilhas.md)

### Se você quer dominar (3 a 5 semanas)
Tudo, na ordem numérica, fazendo os laboratórios.

### Se você já usa uv e quer profundidade
[12](12-o-modelo-de-projeto.md) → [13](13-resolucao-de-dependencias.md) →
[14](14-cache-e-instalacao.md) → [60](60-teoria-avancada.md) → [65](65-estado-da-arte.md)

### Se você precisa decidir se adota (gestão/liderança técnica)
[01](01-introducao-leigo.md) → [11](11-historia.md#7-a-entrada-do-uv-2024) →
[80](80-custos-e-licencas.md) → [65 §2](65-estado-da-arte.md#2-o-evento-de-2026-a-aquisição-pela-openai) →
[20 §9](20-migracao-de-pip-poetry-conda.md#9-rota-de-volta-o-seu-seguro)

---

## Os arquivos

### Bloco A · Porta de entrada — ✅ completo

| # | Arquivo | Nível | O que traz |
|---|---|---|---|
| 01 | [introducao-leigo](01-introducao-leigo.md) | iniciante | a analogia da cozinha, o problema real, medição de velocidade feita nesta máquina |
| 02 | [pre-requisitos](02-pre-requisitos.md) | iniciante | o que saber, tempo realista, requisitos de hardware, **rota de resgate** |
| 03 | [instalacao](03-instalacao.md) | iniciante | **manual de campo**: Linux (5 famílias), macOS, Windows nativo e WSL2, Docker, PATH, permissões, proxy corporativo, convivência de versões, desinstalação completa, **16 erros literais**, alternativa sem instalar nada |
| 04 | [como-comecar](04-como-comecar.md) | iniciante | do ambiente pronto ao programa rodando; os três modos de uso; os 5 primeiros erros |
| 05 | [manual-de-uso](05-manual-de-uso.md) | iniciante→interm. | **referência de todos os 23 comandos**, organizada por tarefa; configuração; o que está obsoleto; atalhos de quem usa há tempo |
| 06 | [exemplos](06-exemplos.md) | todos | **14 receitas completas**, incluindo 2 casos de produção (Docker e CI/CD completos) |
| 07 | [projeto-modelo/](07-projeto-modelo/README.md) | interm. | **`lockspect`** — aplicação inteira que lê e explica um `uv.lock`. **25 testes passando, 96% de cobertura, executada e verificada** |

### Bloco B · Núcleo — ✅ completo

| # | Arquivo | Nível | O que traz |
|---|---|---|---|
| 10 | [fundamentos](10-fundamentos.md) | interm. | vocabulário completo, as três camadas, como o `import` funciona, as 5 razões da velocidade, as 15 PEPs que importam |
| 11 | [historia](11-historia.md) | interm. | 1991 a 2026: do `distutils` à aquisição pela OpenAI. Por que o Python demorou 30 anos |
| 12 | [o-modelo-de-projeto](12-o-modelo-de-projeto.md) | interm. | `pyproject.toml`, `uv.lock` e `.venv` campo a campo; layout `src/`; merge de lock |
| 13 | [resolucao-de-dependencias](13-resolucao-de-dependencias.md) | avançado | PubGrub, forking, estratégias, constraints/overrides/exclusions, depuração de conflito |
| 14 | [cache-e-instalacao](14-cache-e-instalacao.md) | avançado | anatomia do cache, hard links provados com `ls -li`, os 4 link modes, PEP 658, benchmark reproduzível |
| 15 | [gerenciamento-de-python](15-gerenciamento-de-python.md) | interm.→avanç. | `python-build-standalone`, ordem de descoberta, free-threading, comparação com pyenv/conda/Docker |
| 16 | [ferramentas-e-scripts](16-ferramentas-e-scripts.md) | interm. | `uvx`, `uv tool`, PEP 723 em profundidade, lock de script |
| 17 | [workspaces-e-monorepo](17-workspaces-e-monorepo.md) | avançado | workspace verificado do zero, quando **não** usar, publicação de membros |
| 18 | [publicacao-e-build-backend](18-publicacao-e-build-backend.md) | avançado | PEP 517, escolha de backend, release completo, Trusted Publishing |
| 19 | [uv-em-docker-e-ci](19-uv-em-docker-e-ci.md) | avançado | 3 padrões de Dockerfile, 7 regras de ouro, GitHub Actions, GitLab, pre-commit, systemd, Lambda, air-gapped |
| 20 | [migracao](20-migracao-de-pip-poetry-conda.md) | interm.→avanç. | de pip, pip-tools, Poetry, Pipenv, PDM e conda; tabela de tradução; **rota de volta** |
| 21 | [seguranca-e-cadeia-de-suprimentos](21-seguranca-e-cadeia-de-suprimentos.md) | avançado | modelo de 6 ameaças, confusão de dependência, cooldown, SBOM, confiar no próprio uv |
| 60 | [teoria-avancada](60-teoria-avancada.md) | **pesquisa** | prova de NP-completude por redução do 3-SAT, PubGrub formal, resolução universal formalizada, 5 problemas em aberto |
| 65 | [estado-da-arte](65-estado-da-arte.md) | pesquisa | números de adoção, a aquisição pela OpenAI analisada, `ty`, PEP 751, fronteiras abertas |

### Bloco C · Prática e erros — ✅ completo

| # | Arquivo | O que traz |
|---|---|---|
| 70 | [pratica](70-pratica.md) | **14 laboratórios progressivos** (10–14 h) + 4 opções de projeto final + autoavaliação |
| 75 | [armadilhas](75-armadilhas.md) | **24 armadilhas**, **10 mitos** desmontados, más práticas e por que persistem, anti-checklist |

### Bloco D · Economia e ecossistema — ✅ completo

| # | Arquivo | O que traz |
|---|---|---|
| 80 | [custos-e-licencas](80-custos-e-licencas.md) | preços com data (31/08/2026), MIT/Apache explicado, custos ocultos, aprisionamento, quem paga a conta |
| 85 | [cursos-e-certificacoes](85-cursos-e-certificacoes.md) | cursos gratuitos **pesquisados na web** em PT, EN e FR; certificações (e por que não existe uma de uv); trilhas de estudo |

### Bloco E · Fontes — ✅ completo

| # | Arquivo | O que traz |
|---|---|---|
| 90 | [bibliografia](90-bibliografia.md) | livros com ISBN conferido, o que envelheceu, o que é legalmente gratuito |
| 95 | [referencias](95-referencias.md) | specs, 19 PEPs, código-fonte, pessoas, onde perguntar, como saber que este material envelheceu |
| — | [GLOSSARIO](GLOSSARIO.md) | ~70 termos definidos + tabela de siglas |

---

## Status

| Bloco | Status | Observação |
|---|---|---|
| **A · Porta de entrada** | ✅ | projeto-modelo **executado**: 25/25 testes, 96% de cobertura, build gerado |
| **B · Núcleo** | ✅ | 14 documentos, do vocabulário à prova de NP-completude |
| **C · Prática e erros** | ✅ | 14 laboratórios, 24 armadilhas, 10 mitos |
| **D · Economia** | ✅ | preços datados, cursos pesquisados na web em PT/EN/FR |
| **E · Fontes** | ✅ | tudo verificável, nada inventado |

**Nada pendente.**

### O que foi verificado executando de verdade

- instalação, `uv init`, `uv add`, `uv run`, `uv sync`, `uv lock`, `uv export`
  (requirements.txt, pylock.toml), `uv tree`, `uv build`, `uv version`;
- `uv python list/install/pin`, incluindo o download automático de CPython 3.14.7;
- `uvx`, `uv tool install/list`, `uv venv`, `uv pip install`;
- `uv format`, `uv check`, `uv audit`, `uv cache size` (os quatro em preview);
- um **workspace completo** montado do zero, com `uv workspace list` e `uv sync --all-packages`;
- um script **PEP 723** executado, com download de interpretador;
- **benchmark** `pip` × `uv` (23,5 s × 3,6 s × 3,0 s);
- **hard links** provados com `ls -li` (contagem de links = 4);
- o **projeto-modelo inteiro**: sync, testes, cobertura, lint, formatação e build.

### O que **não** pôde ser executado nesta sessão

- `docker build` dos exemplos (sem acesso ao daemon Docker nesta máquina) — os
  Dockerfiles seguem a documentação oficial e estão marcados como tal em
  [19](19-uv-em-docker-e-ci.md);
- publicação real no PyPI/TestPyPI (exigiria conta e publicação pública);
- comandos de macOS e Windows — vêm da documentação oficial, e isso está dito no
  [03](03-instalacao.md);
- os exemplos 3, 4, 8, 9, 10, 13 e 14 do [06](06-exemplos.md) não foram rodados ponta a
  ponta (os comandos e a sintaxe foram conferidos individualmente) — está sinalizado no
  topo daquele arquivo.

---

## Uma frase para levar

> O uv é rápido, e isso é o que faz você experimentar. O que faz você ficar é ele
> substituir **sete ferramentas por uma** — e o que faz você **entender** é a distinção
> entre declaração (`pyproject.toml`), resolução (`uv.lock`) e materialização (`.venv`).
> Se você guardar só uma coisa deste curso, guarde essa distinção.

---

**Comece aqui:** [01-introducao-leigo.md](01-introducao-leigo.md)
**Índice geral da pasta:** [../INDICE.md](../INDICE.md)
