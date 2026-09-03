# 75 · Armadilhas, mitos e más práticas

> **Nível:** todos · **Atualizado em:** 31/08/2026 · **uv 0.12.7**
> 24 armadilhas e 10 mitos, com a correção e o porquê de cada um.

---

## Parte I — Armadilhas de instalação e ambiente

### A1. Instalar o uv com `pip`

```bash
pip install uv    # ❌
```
Você instala a ferramenta que gerencia ambientes **dentro de** um ambiente. Quando esse
ambiente some, o uv some. `uv self update` não funciona.

**Correção:** instalador oficial ([03-instalacao](03-instalacao.md)).

### A2. O terminal antigo que não vê o uv

Instalou, `uv: command not found`. O terminal já estava aberto quando o `PATH` mudou.

**Correção:** `source $HOME/.local/bin/env`, ou abrir terminal novo. **No Windows, é
obrigatório abrir um novo** — não existe `source`.

### A3. Dois `uv` no `PATH`

Instalou por Homebrew, depois pelo instalador oficial. "Atualizei mas a versão não muda."

**Diagnóstico:** `which -a uv`. **Correção:** remova um dos dois.

### A4. Projeto em `/mnt/c` no WSL2

Tudo funciona, tudo é 10 a 100 vezes mais lento, e nada explica.

**Correção:** mova para `/home/voce/`. Não é ajuste fino; é a diferença entre usável e
não usável.

### A5. `sudo uv` ou `sudo pip`

Cria arquivos de root em `~/.cache/uv`; os comandos seguintes do seu usuário falham com
`Permission denied`.

**Correção:** `sudo chown -R "$USER:$USER" ~/.cache/uv ~/.local/share/uv` — e nunca mais.

### A6. Versão do uv não fixada no CI

Segunda-feira o CI quebrou e ninguém mudou nada. Saiu uma versão nova do uv.

**Correção:** `version: "0.12.7"` no `setup-uv`, e `required-version` no `pyproject.toml`.

---

## Parte II — Armadilhas de projeto

### A7. Não versionar o `uv.lock`

A mais grave de todas, e a mais comum. Sem o lock no Git, você tem `pip install` com
outro nome.

**Correção:** `git add uv.lock`. **Sempre.** Aplicações e bibliotecas.

### A8. Versionar o `.venv`

Repositório de 400 MB, caminhos absolutos da máquina de quem commitou, conflitos de merge
insolúveis.

**Correção:** `.gitignore` com `.venv/`. O `uv init` já cria.

### A9. Editar o `uv.lock` à mão

É artefato gerado. Qualquer edição é sobrescrita no próximo `uv lock` — ou, pior,
sobrevive e produz um estado inconsistente.

**Correção:** mude o `pyproject.toml`.

### A10. Resolver conflito de merge do `uv.lock` linha a linha

Horas perdidas e alta chance de gerar um lock inválido.

**Correção:**
```bash
git checkout --theirs uv.lock && uv lock && git add uv.lock
```

### A11. `pytest` em `[project] dependencies`

Todo mundo que instalar sua biblioteca recebe o pytest junto.

**Correção:** `uv add --group dev pytest`.

### A12. Confundir extra com grupo

**Regra:** o **usuário** da sua biblioteca pode querer? → extra. Só quem **desenvolve**
precisa? → grupo. Ver [05-manual-de-uso](05-manual-de-uso.md#3-grupos-extras-e-a-diferença-entre-eles).

### A13. `requires-python` largo demais

`>=3.8` num projeto de 2026 força o resolvedor a achar versões que funcionem em 3.8 —
e você recebe bibliotecas de anos atrás sem entender por quê.

**Correção:** declare a faixa que você realmente suporta e testa.

### A14. Limite superior especulativo

`"pandas>=2.0,<3.0"` "por precaução" torna o **seu** pacote impossível de coinstalar no
dia em que o pandas 3 sair, e ninguém a jusante pode consertar.

**Correção:** `>=2.0` e um teste no CI que rode com a versão mais nova. Ver
[60-teoria-avancada](60-teoria-avancada.md#5-sobre-limites-superiores-o-argumento-formal).

### A15. `uv pip install` dentro de um projeto com lock

Instala no `.venv` sem registrar em lugar nenhum. O próximo `uv sync` **remove** o pacote,
e você acha que o uv "está com bug".

**Correção:** `uv add`. Se for temporário, `uv run --with PACOTE`.

### A16. Editar um arquivo dentro do `.venv` para depurar

Com `link-mode = hardlink` (o padrão), você está editando o **inode compartilhado**: a
mudança aparece em todos os seus projetos e contamina o cache.

**Correção:** `uv pip install -e /caminho/do/fonte`, ou `UV_LINK_MODE=copy`, ou
`uv sync --reinstall` depois para restaurar.

---

## Parte III — Armadilhas de Docker e CI

### A17. `COPY . .` antes do `uv sync`

Cada mudança de código reinstala todas as dependências. Builds de 4 minutos que
deveriam levar 10 segundos.

**Correção:** duas camadas, com `--no-install-project` na primeira
([19-uv-em-docker-e-ci](19-uv-em-docker-e-ci.md)).

### A18. `uv sync` sem `--locked` na imagem

A imagem pode ser construída com versões diferentes das que você testou, e nada avisa.

**Correção:** `--locked` em toda imagem e todo CI.

### A19. `uv run` no `CMD` do container

Cada início de container verifica e sincroniza o ambiente — devagar, e possivelmente
tentando rede num pod sem saída.

**Correção:** `ENV PATH="/app/.venv/bin:$PATH"` e chamar `python` direto.

### A20. Esquecer `UV_LINK_MODE=copy` no Docker

`failed to create hardlink ... Invalid cross-device link`.

### A21. Cron sem caminho absoluto do uv

O `PATH` do cron é mínimo e não inclui `~/.local/bin`. O script "funciona quando eu rodo
à mão" e nunca de madrugada.

**Correção:** `/home/svc/.local/bin/uv run --script /opt/x.py` no `crontab`.

### A22. Empacotar para Lambda a partir de um Mac ARM

Você sobe wheels `macosx_arm64` para um runtime Linux x86-64.

**Correção:** `--python-platform x86_64-manylinux2014 --python-version 3.13`.

---

## Parte IV — Armadilhas de segurança

### A23. Índice extra sem `explicit = true`

Abre a porta para confusão de dependência. Ver
[21-seguranca](21-seguranca-e-cadeia-de-suprimentos.md#3-ameaça-2--confusão-de-dependência).

**Correção:** `default = true` (se o índice espelha o PyPI) ou `explicit = true` +
`[tool.uv.sources]`.

### A24. `--allow-insecure-host` que ficou no script

Colocado para "resolver rápido" um erro de TLS num sábado, e nunca removido. Você desligou
a proteção contra MITM em produção.

**Correção:** `UV_SYSTEM_CERTS=1` ou instalar o certificado da empresa no SO.

---

## Parte V — Dez mitos

### M1. "O uv substitui o pip completamente"

**Falso, com nuance.** Substitui para 95% dos usos. Mas: `pip` continua sendo o que roda
dentro de muitos ambientes de build, o que o `ensurepip` instala, e o que muita
ferramenta invoca internamente. Ele não vai sumir e não deveria.

### M2. "O uv é 100× mais rápido"

**Verdade parcial, e o contexto importa.** 80–115× é o número **com cache quente**,
recriando um ambiente conhecido. Numa instalação genuinamente nova, dominada por
download, medi **7×** nesta máquina. Os dois números são reais e medem coisas diferentes.

### M3. "Preciso instalar Python antes do uv"

**Falso.** O uv instala o Python. É um dos pontos fortes dele.

### M4. "Preciso ativar o ambiente virtual"

**Falso.** `uv run` resolve. `activate` continua funcionando, mas virou opcional.

### M5. "Bibliotecas não devem versionar lockfile"

**Desatualizado.** A orientação clássica vinha de uma confusão: o lock **não** afeta quem
instala a sua biblioteca (só o `pyproject.toml` importa). Versioná-lo garante que **seus
testes** rodem sempre no mesmo ambiente. Ganho sem custo.

### M6. "O uv é da OpenAI, então vai virar pago"

**Falso, e vale distinguir os riscos.** Licença MIT/Apache é irrevogável para o código já
publicado; um fork é sempre possível. O risco real é estagnação ou desvio de roadmap, não
cobrança. Ver [65-estado-da-arte](65-estado-da-arte.md#2-o-evento-de-2026-a-aquisição-pela-openai).

### M7. "O `uv.lock` é um padrão"

**Falso.** É formato próprio do uv. O padrão é o `pylock.toml` (PEP 751), para o qual o uv
exporta.

### M8. "O Python do uv é diferente / não é o CPython de verdade"

**Falso na substância, verdadeiro na margem.** É CPython oficial, compilado de forma
relocável e estática. As diferenças aparecem em casos específicos (software que embute
`libpython`, política de OpenSSL do SO). Ver
[15-gerenciamento-de-python](15-gerenciamento-de-python.md#2-de-onde-vêm-esses-pythons).

### M9. "Workspace serve para qualquer monorepo"

**Falso.** Um workspace = **uma** resolução. Se dois membros precisam de versões
incompatíveis da mesma dependência, workspace é a ferramenta errada.

### M10. "`uv format` e `uv check` substituem ruff e mypy no projeto"

**Falso para projetos sérios.** Eles baixam a versão que o uv escolher, não a que está no
seu lock — nesta máquina, `uv format` trouxe Ruff 0.15.22 enquanto `uv tool install ruff`
trouxe 0.16.5. Para CI reprodutível, declare as ferramentas no grupo `lint`.

---

## Parte VI — Más práticas que persistem, e por quê

| Má prática | Por que persiste | O que fazer |
|---|---|---|
| `requirements.txt` sem versões | está em milhares de tutoriais desde 2010, e "funciona" no dia em que você escreve | `uv add` + `uv.lock` |
| `pip install` no Python do sistema | é o que a primeira aula de Python ensina há 15 anos | `uv add` / `uv tool install` |
| `sudo pip install` | resolve o erro de permissão que o usuário está vendo agora | nunca; o erro é sintoma, não problema |
| Um ambiente virtual para tudo | evita "gerenciar muitos ambientes" — medo baseado no custo antigo de disco | um por projeto; hard links tornam isso barato |
| Commitar `.venv` | "assim funciona igual para todos" | commitar o `uv.lock` |
| Limites superiores por precaução | intuição de segurança, invertida na prática | `>=` + teste no CI |
| Não usar lockfile em biblioteca | conselho correto de 2015, repetido sem contexto | versionar |
| `latest` em imagem Docker | conveniência imediata | tag com versão exata |
| Token de PyPI em secret quando OIDC existe | inércia; funciona | Trusted Publishing |

---

## O anti-checklist — se você faz algo desta lista, pare

- [ ] ❌ `pip install uv`
- [ ] ❌ `.venv/` no Git
- [ ] ❌ `uv.lock` **fora** do Git
- [ ] ❌ editar o `uv.lock` à mão
- [ ] ❌ `sudo` em qualquer comando de pacote Python
- [ ] ❌ `uv sync` sem `--locked` no CI ou em imagem
- [ ] ❌ `COPY . .` antes de instalar dependências no Dockerfile
- [ ] ❌ `uv run` no `CMD` do container
- [ ] ❌ índice extra sem `explicit = true`
- [ ] ❌ `--allow-insecure-host` em qualquer lugar permanente
- [ ] ❌ `pytest` em `[project] dependencies`
- [ ] ❌ limite superior sem ter observado a quebra
- [ ] ❌ projeto em `/mnt/c` no WSL2
- [ ] ❌ versão do uv não fixada no CI

---

## Autoteste

1. Por que instalar o uv com `pip` é ruim, e o que quebra?
2. Explique a armadilha do hard link ao depurar dentro do `.venv`.
3. Qual é a forma correta de resolver um conflito de merge no `uv.lock`?
4. Por que `pytest` não deve ir em `[project] dependencies`?
5. Desmonte o mito "uv é 100× mais rápido" com precisão.
6. Por que "bibliotecas não versionam lockfile" está desatualizado?
7. Qual é o risco real da aquisição pela OpenAI — e qual **não** é?
8. Por que `uv format` não substitui o Ruff declarado no grupo `lint`?
9. Cite três más práticas que persistem por inércia de tutoriais antigos.
10. Escolha três itens do anti-checklist e explique o estrago concreto de cada um.

---

**Próximo:** [80-custos-e-licencas.md](80-custos-e-licencas.md)
