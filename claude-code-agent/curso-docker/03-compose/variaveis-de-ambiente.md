# Variáveis de ambiente no Compose: .env, ARG, ENV e secrets

> **Nível:** intermediário
> **Última verificação:** 18/08/2026 (Docker Compose v5.5.0)
> Toda regra de precedência abaixo foi **testada empiricamente**, não copiada da documentação.

## 1. Existem DOIS lugares chamados "variável de ambiente"

A confusão que gera 90% dos problemas: as variáveis do **arquivo compose** e as
variáveis **dentro do container** são coisas diferentes.

```yaml
services:
  api:
    image: minha-api:${TAG}        # ← 1) interpolação: substituída ao LER o YAML
    environment:
      APP_ENV: production          # ← 2) ambiente DENTRO do container
```

| | Interpolação `${TAG}` | `environment:` |
|---|---|---|
| Quando é resolvida | ao ler o YAML, na sua máquina | ao criar o container |
| Vem de | `.env` ou do shell | do que você escreveu ali |
| Quem enxerga | o Compose | o processo dentro do container |

O `.env` alimenta **a interpolação**. Ele **não** é injetado automaticamente no
container — para isso existe `env_file:`. Confundir os dois é o erro mais comum
do módulo.

## 2. Precedência — testada, não presumida

### Interpolação: shell **ganha** do `.env`

```yaml
services:
  app:
    image: alpine
    environment:
      VALOR: ${MINHA_VAR:-nao-definida}
```

```bash
echo 'MINHA_VAR=do-arquivo-env' > .env

docker compose config | grep VALOR
# saída obtida:  VALOR: do-arquivo-env

MINHA_VAR=do-shell docker compose config | grep VALOR
# saída obtida:  VALOR: do-shell        ← o shell venceu
```

**Consequência prática:** uma variável esquecida no seu `.bashrc` sobrepõe
silenciosamente o `.env` do projeto. Quando algo "funciona só na sua máquina",
`env | grep` é o primeiro lugar a olhar.

Ordem completa, do mais forte ao mais fraco:

1. `docker compose run -e VAR=x`
2. variável exportada no shell
3. arquivo `.env` do diretório
4. valor padrão no YAML (`${VAR:-padrao}`)

### `environment:` **ganha** de `env_file:`

```yaml
services:
  app:
    image: alpine
    env_file: [runtime.env]        # DUPLICADA=veio-de-env_file
    environment:
      DUPLICADA: veio-de-environment
```

```bash
docker compose config | grep -A3 environment:
# saída obtida:
#       DUPLICADA: veio-de-environment    ← environment venceu
#       SO_NO_ENVFILE: ok                 ← chave só do env_file entrou normalmente
```

Regra: `env_file` é a base, `environment` é a exceção pontual.

## 3. Sintaxe de interpolação

| Sintaxe | Comportamento |
|---|---|
| `${VAR}` | vazio se não definida — **silencioso e perigoso** |
| `${VAR:-padrao}` | usa `padrao` se vazia ou indefinida |
| `${VAR-padrao}` | usa `padrao` só se **indefinida** (vazia continua vazia) |
| `${VAR:?mensagem}` | **falha** com sua mensagem se vazia ou indefinida |
| `${VAR:+valor}` | usa `valor` **se** VAR estiver definida |
| `$$` | um `$` literal (não interpola) |

### Use `${VAR:?}` para tudo que é obrigatório

**Verificação executada** no compose do FlixARD:

```bash
docker compose config --quiet
# saída obtida:
# error while interpolating services.api.environment.DATABASE_URL:
#   required variable POSTGRES_PASSWORD is missing a value: defina POSTGRES_PASSWORD no .env

POSTGRES_PASSWORD=teste docker compose config --quiet
# saída obtida: (vazio) -> válido
```

O Compose **se recusa a subir** sem a variável, com a sua mensagem. Compare com
o alternativo:

```yaml
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}   # ❌ nunca faça isso
```

Aqui o serviço sobe com a senha `postgres` e ninguém percebe até o incidente.
**Default silencioso para segredo é como vazamentos começam.**

### O `$$` que salva o cron

```yaml
command: sh -c "echo Custo: R$$ 100"    # imprime "R$ 100"
```

Um `$` isolado faz o Compose tentar interpolar. Aparece muito em cron
(`$(date)`) e em regex.

## 4. `ARG` vs `ENV` vs `environment:` — a tabela decisiva

```yaml
services:
  api:
    build:
      args:                       # ← ARG: só durante o BUILD
        APP_VERSION: "1.0.0"
    environment:                  # ← ENV: durante a EXECUÇÃO
      APP_ENV: production
```

| | `build.args` (ARG) | `environment:` (ENV) |
|---|---|---|
| Existe durante | build | execução |
| Vai para a imagem? | não | sim |
| Visível em `docker inspect`? | não | **sim** |
| Visível em `docker history`? | **sim** | sim |
| Serve para segredo? | **NÃO** | **NÃO** |
| Muda sem rebuild? | não | sim |

Use `ARG` para o que afeta **como a imagem é construída** (versão de base,
plataforma). Use `environment` para o que muda **entre ambientes** (URL do
banco, nível de log).

Se você precisa rebuildar a imagem para mudar de dev para produção, algo está
como `ARG` que deveria ser `ENV`.

## 5. Segredos: por que nada acima serve

Uma senha em `environment:` vaza em quatro lugares:

| Onde | Como qualquer um vê |
|---|---|
| Metadados | `docker inspect <container>` mostra todo o `Env` |
| Processo | `cat /proc/1/environ` de dentro do container |
| Logs | crash dumps e eventos serializam o ambiente |
| Filhos | todo subprocesso herda o ambiente inteiro |

Um `--build-arg SENHA=x` é ainda pior: fica gravado no `docker history` da
imagem, recuperável por quem a baixar.

### A forma correta: secret montado como arquivo

```yaml
services:
  api:
    environment:
      DATABASE_URL_FILE: /run/secrets/database_url   # o CAMINHO, não o valor
    secrets:
      - database_url

secrets:
  database_url:
    file: ./secrets/database_url.txt
```

Leitura na aplicação, com o padrão `_FILE`:

```python
import os
from pathlib import Path

def ler_segredo(nome: str, padrao: str | None = None) -> str:
    caminho = os.getenv(f"{nome}_FILE")
    if caminho and Path(caminho).exists():
        return Path(caminho).read_text().strip()   # o .strip() é obrigatório
    valor = os.getenv(nome, padrao)
    if valor is None:
        raise RuntimeError(f"segredo obrigatório ausente: {nome}")
    return valor
```

O `.strip()`: `echo senha > arquivo` grava um `\n` no fim, e a senha com quebra
de linha falha a autenticação com `password authentication failed` — mensagem
que não sugere em nada a causa real. Use `printf` ou `.strip()`.

Aprofundamento em
[secrets e variáveis sensíveis](../06-seguranca/secrets-e-variaveis-sensiveis.md).

## 6. Higiene de arquivos

```bash
.env               # ❌ NUNCA no git — valores reais
.env.example       # ✅ no git — chaves com valores fictícios
secrets/           # ❌ NUNCA no git
```

`.gitignore`:

```
.env
.env.*
!.env.example
secrets/
```

E no `.dockerignore` **também** — senão um `COPY . .` leva o `.env` para dentro
da imagem, onde ele fica visível para sempre.

Se um `.env` já foi commitado: remover o arquivo **não basta**. Ele está no
histórico do git. **Rotacione todo segredo** e reescreva o histórico
(`git filter-repo`) se o repositório for público.

## 7. Estratégia por ambiente

```
projeto/
├── compose.yaml              # comum, no git
├── compose.override.yaml     # dev, no git (lido automaticamente)
├── compose.prod.yaml         # produção, no git
├── .env.example              # no git
├── .env                      # local, IGNORADO
└── secrets/                  # IGNORADO
```

```bash
docker compose up -d                                        # dev
docker compose -f compose.yaml -f compose.prod.yaml up -d    # produção
```

Note que a produção **não** usa o override: passar `-f` explicitamente desativa
o carregamento automático do `compose.override.yaml`.

## 8. Erros que você provavelmente vai cometer

| Sintoma | Causa raiz | Correção |
|---|---|---|
| Mudei o `.env` e nada mudou | variáveis são lidas na **criação** do container | `docker compose up -d --force-recreate` |
| Variável vazia dentro do container | confundiu interpolação com `env_file:` | `.env` alimenta `${}`; para injetar, use `env_file:` |
| Valor errado, sem explicação | variável exportada no shell sobrepõe o `.env` | `env \| grep NOME` |
| `Custo: 100` em vez de `Custo: R$ 100` | o `$` foi interpolado | escapar com `$$` |
| Serviço sobe com senha padrão | `${VAR:-padrao}` num segredo | `${VAR:?mensagem}` |
| `password authentication failed` com a senha certa | `\n` no fim do arquivo de secret | `.strip()` / `printf` |
| Senha aparece em `docker inspect` | segredo em `environment:` | migrar para `secrets:` |

## 9. Autoteste

1. Qual a diferença entre `${VAR}` no YAML e uma chave em `environment:`?
2. Uma variável está no `.env` **e** exportada no shell. Qual vence? (você pode
   testar em 10 segundos — como?)
3. `env_file` e `environment` definem a mesma chave. Qual vence?
4. Por que `${SENHA:-postgres}` é perigoso e `${SENHA:?...}` é correto?
5. Cite dois lugares concretos onde uma senha em `environment:` vaza.
6. Por que `--build-arg SENHA=x` é ainda pior?
7. Para que serve `$$`?
8. Removi o `.env` do repositório num commit novo. Resolvido?

---
[← anatomia](anatomia-docker-compose.md) · [exercício →](exercicio.md) · [índice](../00-indice.md)
