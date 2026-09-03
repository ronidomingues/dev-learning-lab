# 65 · Estado da arte — onde o uv está em 31 de agosto de 2026

> **Nível:** pesquisa · **Este arquivo envelhece rápido.**
> **Consultado e escrito em:** 31/08/2026. **Versão de referência:** uv 0.12.7,
> lançada em **27/08/2026**.
> Se você está lendo isto meses depois, confira as fontes do rodapé antes de confiar em
> qualquer número.

---

## 1. Onde o uv está, em números

| Métrica | Valor | Data / fonte |
|---|---|---|
| Última versão | **0.12.7** | 27/08/2026, GitHub Releases |
| Cadência de release | ~1 a 2 por semana (0.12.5, 0.12.6 e 0.12.7 saíram entre 22 e 27/08/2026) | GitHub Releases |
| Estrelas no GitHub | ~85.000 (eram ~36.100 em jan/2025) | levantamentos de terceiros, 2026 |
| Downloads mensais | ~28,1 milhões | levantamentos de terceiros, 2026 |
| Fatia dos downloads do PyPI feitos **pelo** uv | ~13,3% | idem |
| Presença em repositórios Python criados em 2026 | ~30% | [aleyan.com — "Why aren't we uv yet?"](https://aleyan.com/blog/2026-why-arent-we-uv-yet/) |
| Popularidade relativa ao `requirements.txt` | ~44% | idem |
| Ferramenta mais "admirada" | 74,2% | Stack Overflow Developer Survey 2025 |
| Licença | MIT **ou** Apache-2.0 | repositório |

> **Aviso de qualidade das fontes:** as métricas de estrelas, downloads e fatia de mercado
> vêm de levantamentos de terceiros (blogs técnicos e análises de repositórios), não de um
> relatório oficial auditado. Trate-as como **ordem de grandeza**, não como número exato.
> A tendência — crescimento rápido e consistente — é bem sustentada por várias fontes
> independentes; os dígitos, não.

**A leitura sóbria:** ~30% dos repositórios novos é adoção enorme para dois anos e meio de
existência, e é **minoria**. O `requirements.txt` continua sendo o mais comum, e vai
continuar por anos — há milhões de projetos legados que não têm motivo para mudar. Quem
diz que "todo mundo já usa uv" está no seu próprio nicho.

---

## 2. O evento de 2026: a aquisição pela OpenAI

**19 de março de 2026** — a OpenAI anunciou a aquisição da Astral. A equipe passou a
integrar o time do **Codex**.

**O que foi dito:**
- `uv`, `ruff` e `ty` permanecem código aberto, com licença MIT/Apache-2.0;
- a OpenAI declarou intenção de continuar dando suporte aos produtos abertos da Astral;
- Charlie Marsh afirmou, em entrevista posterior ao *Talk Python* (episódio #552), que a
  cadência de release do uv se manteve durante a aquisição, que o `ty` segue com alvo de
  release estável em 2026, e que a equipe está limpando o *backlog* de recursos.

**O que não foi dito:**
- nenhuma transferência para fundação;
- nenhum comitê independente de mantenedores;
- nenhuma garantia formal de continuidade além da licença.

Sobre isso, Marsh argumentou publicamente que "confiança se resolve com atos, não com
anúncios", e chegou a dizer que considera possível a equipe escrever **mais** código
aberto na OpenAI do que escrevia na Astral.

**Consequência imediata:** o **`pyx`** — o registro comercial lançado em beta em agosto de
2025 — foi **descontinuado**. O serviço encerrou, parou de aceitar cadastros, e a
infraestrutura de índice para GPU e wheels pré-construídos foi **aberta em código livre**.

### Como avaliar isso, com honestidade

| Sinal | Peso |
|---|---|
| ✅ A cadência de release se manteve (três versões na última semana de agosto de 2026) | forte, verificável |
| ✅ Licença permissiva mantida — um fork é sempre viável | forte, estrutural |
| ✅ O produto comercial encerrado elimina o conflito "open core" | moderado |
| ⚠️ Nenhuma estrutura de governança independente | **é o risco real** |
| ⚠️ Roadmap agora sujeito às prioridades do Codex | moderado, especulativo |
| ⚠️ Uma ferramenta de infraestrutura crítica do ecossistema Python sob controle de uma única empresa de IA | é uma questão política legítima, não técnica |

**Minha posição, explicitamente marcada como opinião:** eu continuo usando e recomendando
o uv. O risco não é o uv "fechar" — a licença impede, e o código está distribuído em
milhões de cópias. O risco é **estagnação ou desvio de rumo em dois a três anos**. A
mitigação é barata e você deve adotá-la de qualquer jeito: mantenha o `pyproject.toml`
padrão PEP 621, versione o lock, e saiba que
`uv export --format pylock.toml` te dá uma porta de saída num comando. Ver
[20-migracao](20-migracao-de-pip-poetry-conda.md#9-rota-de-volta-o-seu-seguro).

---

## 3. O que há de novo na série 0.12 (agosto de 2026)

Da 0.12.7, lançada em 27/08/2026:

- substituição de instalações de Python gerenciado ao atualizar para um **build** mais
  novo da mesma versão;
- suporte a **s390x, ppc64le e loongarch64** na resolução multiplataforma — sinal claro
  de que o uv está entrando em ambientes de mainframe e HPC;
- repetição de download com credenciais quando o Azure Storage nega acesso anônimo
  (`UV_AZURE_ENDPOINT_URL`);
- **cache endereçado por conteúdo** (`content-addressed-cache`, em preview): hashes de
  diretório baseados em conteúdo para deduplicar wheels extraídos. É a evolução natural
  do `archive-v0` descrito em [14-cache](14-cache-e-instalacao.md).

Recursos ainda em **preview** na 0.12.7 (verificados nesta máquina):

| Comando | Estado | Aviso emitido |
|---|---|---|
| `uv format` | preview (usa Ruff) | `warning: uv format is experimental` |
| `uv check` | preview (usa `ty`) | `warning: uv check is experimental` |
| `uv audit` | preview | `warning: uv audit is experimental` |
| `uv cache size` | preview | `warning: uv cache size is experimental` |

> **A tendência que esses quatro comandos revelam:** o uv está deixando de ser um
> gerenciador de pacotes e virando **o ponto único de entrada de todo o ferramental
> Python** — formatar, verificar tipos, auditar. É a mesma trajetória do `cargo`, que
> tem `cargo fmt`, `cargo clippy`, `cargo audit`.
>
> **Isso é bom ou ruim?** Minha opinião: bom para quem está começando e para scripts
> (uma ferramenta, zero configuração); e eu **não** uso em projetos sérios, porque quero
> a versão do Ruff e do verificador de tipos **travada no meu lock**, não escolhida pelo
> uv. Note que nesta máquina o `uv format` baixou Ruff 0.15.22 enquanto
> `uv tool install ruff` trouxe 0.16.5 — são canais diferentes, e essa divergência é
> exatamente o tipo de coisa que você não quer num pipeline de CI.

---

## 4. `ty` — o verificador de tipos

Escrito em Rust pela mesma equipe, ex-"Red Knot". Alvo declarado de **release estável em
2026**; em 31/08/2026 continua em beta, com releases frequentes (a última consultada é de
26/08/2026). O `uv check` já o usa por baixo.

**O que muda se ele der certo:** hoje o mercado é `mypy` (o de referência, escrito em
Python, lento em bases grandes) e `pyright` (da Microsoft, TypeScript, rápido, mas
acoplado ao ecossistema Node). Um verificador em Rust, rápido, com integração nativa ao
gerenciador de pacotes, muda a economia da verificação de tipos em Python — do jeito que
o Ruff mudou a de lint.

**O que ainda não está claro:** compatibilidade com o corpo enorme de anotações e stubs
escritos para o `mypy`, e com plugins (o do Django, por exemplo, é essencial para muita
gente). É o mesmo desafio que o Ruff enfrentou e venceu — mas tipos são
significativamente mais difíceis que lint.

---

## 5. PEP 751 (`pylock.toml`) — o padrão de lockfile

**Situação em 31/08/2026:**

- a PEP foi aceita em 2025;
- o uv **exporta** (`uv export --format pylock.toml`) e **consome** (`uv pip install`,
  `uv pip sync`, `uv pip compile` aceitam `pylock.toml`);
- o `uv.lock` **continua sendo o formato nativo**;
- o Poetry discute suporte; o `pip` avança na leitura.

**Por que o uv não adotou como nativo** — e isto é o debate técnico mais interessante do
momento: o `pylock.toml` foi projetado para **instalação**, não para desenvolvimento. Ele
não representa grupos de dependências (PEP 735), membros de workspace, nem conjuntos de
extras declaradamente conflitantes. Adotá-lo como formato nativo custaria recursos que o
uv já entrega.

**Minha previsão, marcada como especulação:** o `pylock.toml` vai se firmar como o formato
de **intercâmbio e de deploy** — o que atravessa a fronteira entre ferramentas e entra em
scanners de segurança e plataformas de deploy — e cada ferramenta manterá o seu formato
rico para desenvolvimento. É o mesmo padrão de `.tar.gz` versus o formato interno de cada
gerenciador. Não é o desfecho que a PEP idealizou, mas é o estável.

---

## 6. As fronteiras abertas do empacotamento Python

### 6.1 GPU e o ecossistema de ML — o problema não resolvido

Instalar PyTorch com a variante certa de CUDA continua sendo o caso mais doloroso do
empacotamento Python. Os wheels são gigantes (2–3 GB), específicos por versão de CUDA, e
o PyPI tem limite de tamanho de arquivo. O `pyx` da Astral existia em boa parte para
resolver isso — e foi descontinuado, com a infraestrutura de índice para GPU aberta.

O uv oferece o ferramental (`explicit = true` nos índices, `[tool.uv.sources]` com
marcadores, `conflicts`) que **torna o problema administrável**, mas não o elimina.
Ver o exemplo 13 em [06-exemplos](06-exemplos.md).

**Está em aberto.** Nenhuma solução limpa existe em 2026.

### 6.2 Free-threading (PEP 703)

Builds `freethreaded` são oficiais desde o 3.13, e saíram do status experimental no 3.14.
O uv suporta (`uv python install 3.14t`). O gargalo é o **ecossistema de wheels**: cada
extensão C precisa de um build `cp314t`, e muitas ainda não têm.

Estamos naquele ponto do ciclo em que a ferramenta está pronta e o ecossistema não.
Meu palpite: 2027–2028 para uso mainstream em produção.

### 6.3 Empacotar aplicações, não bibliotecas

O Python ainda não tem um bom caminho para "entregue este programa a um usuário final que
não sabe o que é Python". `PyInstaller`, `Nuitka`, `Briefcase` e `py2app` existem e todos
têm arestas.

O uv **não resolve isso** — e não pretende. É a lacuna mais visível que ele deixa.
Há discussões sobre um "modo aplicação" que produza um bundle autocontido; nada concreto
em 31/08/2026.

### 6.4 A concorrência

| Ferramenta | Situação em 2026 |
|---|---|
| **pip** | ativo, essencial, e a base de tudo. Não vai morrer; incorporou lições (resolvedor, `--require-hashes`, suporte a PEP 751) |
| **Poetry** | maduro, adotou PEP 621 no 2.0, ainda muito usado. A recomendação da própria comunidade é "não migre sem uma dor concreta" |
| **PDM** | nicho, tecnicamente sólido |
| **Hatch** | forte no build, apadrinhado pela PyPA |
| **Pixi** | interessante: um "uv do conda", em Rust, para o ecossistema conda-forge. Vale acompanhar se você é da área científica |
| **conda/mamba** | continua insubstituível no seu nicho (binários não-Python) |

> **Nota sobre o Pixi:** é o desenvolvimento que eu mais acompanho fora do uv. Se ele
> resolver o caso científico com a mesma ergonomia, a combinação Pixi + uv cobre 100% do
> espaço — e o conda vira legado.

---

## 7. Como acompanhar depois desta data

| Fonte | O que traz |
|---|---|
| [github.com/astral-sh/uv/releases](https://github.com/astral-sh/uv/releases) | changelog real, a cada 1–2 semanas |
| [github.com/astral-sh/uv/blob/main/CHANGELOG.md](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md) | histórico completo |
| [docs.astral.sh/uv](https://docs.astral.sh/uv/) | documentação viva |
| [discuss.python.org — categoria Packaging](https://discuss.python.org/c/packaging/14) | onde as PEPs de empacotamento são debatidas de verdade |
| [peps.python.org](https://peps.python.org/) | o texto normativo |
| [blog.pypi.org](https://blog.pypi.org/) | mudanças de política e segurança do PyPI |
| [talkpython.fm](https://talkpython.fm/) | entrevistas com os envolvidos |

**Como reconhecer que este arquivo envelheceu:** rode `uv --version`. Se o resultado for
0.13 ou superior, houve uma quebra de compatibilidade de minor desde que isto foi escrito
— leia o changelog antes de seguir os exemplos de configuração.

---

## Autoteste

1. Qual a fatia de repositórios Python novos que usa uv em 2026 — e por que a leitura
   "todo mundo já usa" é errada?
2. O que foi anunciado, e o que **não** foi, na aquisição pela OpenAI?
3. Qual é o risco real da aquisição, na avaliação deste curso, e qual a mitigação?
4. O que aconteceu com o `pyx`, e o que isso sugere sobre a estratégia comercial?
5. Cite os quatro comandos em preview na 0.12.7 e a tendência que eles revelam.
6. Por que este curso recomenda **não** usar `uv format`/`uv check` em projetos sérios?
7. Por que o uv não adotou o `pylock.toml` como formato nativo?
8. Qual é o problema de empacotamento que continua sem solução limpa em 2026?
9. O que falta para o free-threading ser usável em produção?
10. Qual lacuna o uv deixa explicitamente sem cobrir?

---

**Fontes (todas consultadas em 31/08/2026):**
[github.com/astral-sh/uv/releases/tag/0.12.7](https://github.com/astral-sh/uv/releases/tag/0.12.7) ·
[openai.com/index/openai-to-acquire-astral](https://openai.com/index/openai-to-acquire-astral/) ·
[simonwillison.net/2026/mar/19/openai-acquiring-astral](https://simonwillison.net/2026/mar/19/openai-acquiring-astral/) ·
[pydevtools.com — Astral winds down pyx](https://pydevtools.com/blog/astral-winds-down-pyx-open-sources-gpu-packaging/) ·
[talkpython.fm/episodes/show/552](https://talkpython.fm/episodes/show/552/astral-joins-openai) ·
[aleyan.com/blog/2026-why-arent-we-uv-yet](https://aleyan.com/blog/2026-why-arent-we-uv-yet/) ·
[github.com/astral-sh/ty/releases](https://github.com/astral-sh/ty/releases) ·
[github.com/astral-sh/uv/issues/12584](https://github.com/astral-sh/uv/issues/12584) (PEP 751) ·
[PEP 751](https://peps.python.org/pep-0751/) · [PEP 703](https://peps.python.org/pep-0703/) ·
Stack Overflow Developer Survey 2025 · avisos de preview reproduzidos localmente com
uv 0.12.7.

**Próximo:** [70-pratica.md](70-pratica.md)
