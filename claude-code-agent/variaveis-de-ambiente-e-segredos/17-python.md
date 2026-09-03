# 17 · Python — do `.env` à produção

`Nível: intermediário` · `Atualizado em: 14/08/2026`
`Base: Python 3.10.12 · python-dotenv 1.2.3 — verificados nesta máquina`

---

## 1. A biblioteca padrão já resolve o essencial

```python
import os

os.environ["VAR"]                  # KeyError se não existir  ← falha rápida de graça
os.environ.get("VAR")              # None se não existir
os.environ.get("VAR", "padrão")    # com padrão
os.getenv("VAR", "padrão")         # sinônimo de .get
"VAR" in os.environ                # existe?
os.environ["NOVA"] = "x"           # define para ESTE processo e seus filhos futuros
del os.environ["NOVA"]             # remove
```

**Python tem uma vantagem sobre Node aqui**, e vale explorá-la: `os.environ["X"]`
**lança `KeyError`** se a variável não existir. Isso é falha rápida embutida.
Em Node, `process.env.X` devolve `undefined` em silêncio, e o erro aparece três
camadas adiante, disfarçado.

```python
# ✅ para variável obrigatória, prefira o acesso por índice
DATABASE_URL = os.environ["DATABASE_URL"]   # KeyError: 'DATABASE_URL' — claro e imediato
```

⚠️ **`os.environ` só é lido uma vez, na importação do módulo `os`.**
Se um código C dentro de uma biblioteca chamar `setenv()` diretamente, `os.environ`
não enxerga. É raro, mas existe — e a recíproca também: `os.environ["X"]="1"` chama
`putenv()`, logo o valor **é** visto por subprocessos.

---

## 2. `python-dotenv`

```bash
pip install "python-dotenv>=1.2.2"
```

> 🔒 **Atualize para ≥ 1.2.2.** Versões anteriores tinham falha em `set_key()` e
> `unset_key()`: elas seguiam **links simbólicos** ao reescrever o `.env`, permitindo
> sobrescrever arquivos fora do lugar previsto. Verificado nesta máquina: **1.2.3**.

```python
from dotenv import load_dotenv, dotenv_values, find_dotenv

load_dotenv()                       # lê ./.env e injeta em os.environ
load_dotenv(override=True)          # ⚠️ sobrescreve o ambiente — quase nunca é o que você quer
load_dotenv(find_dotenv())          # sobe a árvore de diretórios procurando .env
config = dotenv_values(".env")      # devolve um dict SEM tocar em os.environ
```

**`dotenv_values` é subestimada.** Ela não polui o ambiente do processo, o que
significa que os valores **não vazam para subprocessos**. Em um script que chama
`ffmpeg`, `git` ou qualquer binário de terceiro, isso é uma redução real de superfície.

### Precedência, medida

Já comprovado em [12-formato-dotenv.md](12-formato-dotenv.md) e no
[projeto-modelo](07-projeto-modelo/README.md): sem `override=True`, o **ambiente
vence o arquivo**. É a propriedade que permite o `.env` sumir em produção.

### As duas divergências de parsing que só o Python tem

Medidas nesta máquina, em 14/08/2026, contra o Node:

| No `.env` | Node `--env-file` | `python-dotenv` 1.2.3 |
|---|---|---|
| `SENHA=abc#123` | `"abc"` | `"abc#123"` |
| `URL=${BASE}/v1` | `"${BASE}/v1"` literal | **expande** para `"valor/v1"` |

Se o seu sistema tem serviços em Python e em Node lendo o **mesmo** `.env`, essas
duas linhas se comportam de forma diferente em cada um. Use o subconjunto seguro.

---

## 3. `pydantic-settings` — o que eu usaria em projeto sério

```bash
pip install "pydantic-settings>=2.14"
```

```python
from typing import Literal
from pydantic import Field, PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",              # lido só se existir; em produção não existe
        env_file_encoding="utf-8",
        env_prefix="",                # ou "LOJA_" para evitar colisão
        extra="ignore",               # ignora variáveis do sistema que não são nossas
        case_sensitive=False,
        secrets_dir="/run/secrets",   # 🔑 Docker/K8s de graça — ver abaixo
    )

    # obrigatórias: sem valor padrão
    database_url: PostgresDsn
    api_key: SecretStr                # não aparece em repr, str, log ou traceback
    session_secret: SecretStr = Field(min_length=32)

    # opcionais: com padrão e restrição
    port: int = Field(default=3000, ge=1, le=65535)
    log_level: Literal["debug", "info", "warn", "error"] = "info"
    ambiente: Literal["development", "test", "production"] = "development"

    @field_validator("api_key")
    @classmethod
    def sem_chave_de_teste_em_producao(cls, v: SecretStr, info):
        if info.data.get("ambiente") == "production" and v.get_secret_value().startswith("sk_test_"):
            raise ValueError("chave de teste em produção")
        return v


settings = Settings()   # ValidationError listando TODOS os erros de uma vez
```

### As três razões pelas quais isto vence o código à mão

**1. `SecretStr` faz o mascaramento ser o padrão, não a lembrança.**

```python
print(settings)
# database_url=PostgresDsn('postgres://...') api_key=SecretStr('**********') …

settings.api_key                       # SecretStr('**********')
settings.api_key.get_secret_value()    # só AQUI o valor real aparece
```

Um `logger.info(settings)` distraído — a causa de vazamento mais comum depois do
commit acidental — **não vaza nada**. E o valor real só sai quando alguém escreve
`.get_secret_value()`, que é uma linha visível em revisão de código.

**2. `secrets_dir` implementa o padrão Docker/Kubernetes sem código.**
Com `secrets_dir="/run/secrets"`, o campo `api_key` é lido do arquivo
`/run/secrets/api_key` se ele existir. É o padrão `_FILE` do
[06-exemplos.md #7](06-exemplos.md), de graça.

**3. Reporta todos os erros de uma vez**, e com o caminho de cada campo.

### Múltiplas fontes, em ordem própria

```python
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

class Settings(BaseSettings):
    @classmethod
    def settings_customise_sources(cls, settings_cls, init_settings,
                                   env_settings, dotenv_settings, file_secret_settings):
        # ordem = precedência (a primeira vence)
        return (init_settings, env_settings, file_secret_settings, dotenv_settings,
                fonte_do_cofre)   # sua função que busca no Vault/AWS
```

É assim que se pluga um cofre mantendo tudo o mais igual.

---

## 4. Django

```python
# settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]     # KeyError se faltar — correto
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = [h for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h]
```

| Item | Produção | Se errar |
|---|---|---|
| `DEBUG` | **`False`** | a página de erro do Django mostra **todo o `settings.py`** e o ambiente da requisição a qualquer visitante |
| `SECRET_KEY` | do ambiente, 50+ caracteres aleatórios | sessões forjáveis, tokens CSRF quebráveis, links de reset de senha falsificáveis |
| `ALLOWED_HOSTS` | lista explícita | *Host header poisoning* |
| `DATABASES` | do ambiente | — |

> 🚨 **`DEBUG=True` em produção é para Django o que `APP_DEBUG=true` é para Laravel:**
> a falha nº 1, e a mais explorada por varredores automáticos. O Django ao menos
> **oculta** valores de chaves que parecem sensíveis na página de erro (heurística por
> nome: `API`, `TOKEN`, `KEY`, `SECRET`, `PASS`, `SIGNATURE`) — o que ajuda e **não
> é garantia**: `DATABASE_URL`, com a senha embutida, não casa com nenhum desses
> nomes.

E a armadilha do booleano, de novo:

```python
DEBUG = os.environ.get("DJANGO_DEBUG", False)   # ❌ "false" é uma string NÃO VAZIA
bool("false")                                    # True  ← DEBUG ligado em produção
```

Bibliotecas úteis: `django-environ` (com `env.bool()`, `env.db()`) e `dj-database-url`
(converte `DATABASE_URL` no dicionário `DATABASES`).

---

## 5. FastAPI / Flask

```python
# config.py
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_key: SecretStr

@lru_cache
def get_settings() -> Settings:
    return Settings()     # instanciado uma vez; o cache evita reler a cada requisição
```

```python
# main.py
from fastapi import Depends, FastAPI

app = FastAPI()

@app.get("/health")
def health(cfg: Settings = Depends(get_settings)):
    return {"ok": True}
```

O `Depends` + `lru_cache` é o idioma da comunidade, e tem um benefício além do
desempenho: nos testes você sobrescreve a dependência
(`app.dependency_overrides[get_settings] = …`) e testa qualquer configuração sem
mexer em `os.environ` — que é global e vaza entre testes.

Flask:

```python
app.config.from_prefixed_env()   # Flask 2.2+: lê tudo que começa com FLASK_
```

---

## 6. Armadilhas específicas de Python

### 6.1 `os.environ` é global e vaza entre testes

```python
# ❌ suja o ambiente para os testes seguintes, e a ordem passa a importar
def test_algo():
    os.environ["API_KEY"] = "teste"

# ✅ pytest, isolado e revertido automaticamente
def test_algo(monkeypatch):
    monkeypatch.setenv("API_KEY", "teste")
    monkeypatch.delenv("OUTRA", raising=False)
```

Melhor ainda: **função pura de configuração**, que recebe o dicionário do ambiente
como parâmetro. É como o [projeto-modelo](07-projeto-modelo/equivalentes/config.py)
foi escrito, e por isso ele testa dezenas de cenários sem tocar em `os.environ`.

### 6.2 Notebooks e o kernel de vida longa

Em Jupyter, o kernel dura horas. `load_dotenv()` no início, edição do `.env` depois,
e o valor antigo continua em memória — sem `override=True` nem reinício do kernel,
nada muda. E, pior: um `print(os.environ)` numa célula deixa **todo o ambiente
salvo dentro do arquivo `.ipynb`** — que costuma ir para o Git.

```bash
# ganho barato: tire as saídas dos notebooks antes de commitar
pip install nbstripout && nbstripout --install
```

### 6.3 `multiprocessing` e o método de início

```python
# fork (padrão em Linux até 3.13): o filho herda o ambiente inteiro
# spawn (padrão em macOS e Windows; padrão em Linux a partir do 3.14):
#   um Python novo é iniciado e o ambiente é RECONSTRUÍDO
```

Código que funciona em Linux e falha em macOS por causa disso é comum, e a mudança
de padrão do Linux no 3.14 vai reproduzir a surpresa para muita gente. Se a sua
configuração precisa estar nos workers, **passe-a explicitamente**, não confie em herança.

### 6.4 Segredo em memória

```python
senha = os.environ["SENHA"]
del senha                # ❌ não apaga: strings são imutáveis e o GC decide quando
```

Se o modelo de ameaça inclui despejo de memória, use `bytearray`:

```python
b = bytearray(os.environ["SENHA"], "utf-8")
usar(b)
for i in range(len(b)):
    b[i] = 0            # zera de verdade
del os.environ["SENHA"] # remove a cópia do ambiente do processo
```

Mesma avaliação honesta do capítulo de Node: para a maioria dos sistemas isso é
teatro. O atacante que despeja a sua memória já ganhou.

---

## 7. Produção

```python
# app.py — não menciona dotenv em lugar nenhum obrigatório
import os
from config import settings          # valida e explode cedo se algo faltar

# Em desenvolvimento, quem carrega o .env é o comando:
#   dotenv run -- uvicorn app:app --reload
# ou o pydantic-settings, via env_file=".env" (que simplesmente não acha nada em prod)
```

```ini
# /etc/systemd/system/minha-app.service
[Service]
User=minhaapp
EnvironmentFile=/etc/minha-app/env
ExecStartPre=/opt/minha-app/.venv/bin/python -c "from config import settings; print('config ok')"
ExecStart=/opt/minha-app/.venv/bin/gunicorn app:app -w 4 -b 127.0.0.1:8000
RestartPreventExitStatus=78
```

Gunicorn/uvicorn com múltiplos workers: **a configuração é carregada no processo-mestre
e herdada pelos workers**. Trocar o `.env` não afeta workers vivos — é preciso
`systemctl reload` ou `kill -HUP`.

---

## 8. Receituário Python

| Situação | Faça |
|---|---|
| Variável obrigatória | `os.environ["X"]` (KeyError é seu amigo) |
| Projeto sério | `pydantic-settings` com `SecretStr` |
| Script pequeno | `os.environ.get` + validação à mão |
| Não poluir subprocessos | `dotenv_values()` em vez de `load_dotenv()` |
| Docker/K8s | `secrets_dir="/run/secrets"` |
| Testes | `monkeypatch.setenv`, ou função pura recebendo o dict |
| Django | `DEBUG=False`, `SECRET_KEY` do ambiente, `ALLOWED_HOSTS` explícito |
| FastAPI | `@lru_cache` + `Depends(get_settings)` |
| Notebooks | `nbstripout`, e nunca `print(os.environ)` |

---

## Autoteste

1. Por que `os.environ["X"]` é preferível a `os.environ.get("X")` para variável obrigatória?
2. Qual a diferença prática entre `load_dotenv()` e `dotenv_values()` do ponto de vista de subprocessos?
3. Que falha de segurança motivou a atualização para `python-dotenv` ≥ 1.2.2?
4. O que `SecretStr` protege, e em que momento exato o valor real aparece?
5. O que `secrets_dir` do `pydantic-settings` implementa sem você escrever código?
6. `DEBUG = os.environ.get("DJANGO_DEBUG", False)` com `DJANGO_DEBUG=false`. Qual o valor de `DEBUG`? Por quê?
7. O Django oculta valores sensíveis na página de erro. Por que isso não protege a `DATABASE_URL`?
8. Por que `monkeypatch.setenv` é melhor que `os.environ["X"]="y"` num teste?
9. O que muda entre `fork` e `spawn` no `multiprocessing`, e por que isso importa aqui?
10. Cite as duas divergências medidas de parsing entre `python-dotenv` e o carregador nativo do Node.

---

**Medido nesta máquina em 14/08/2026:** Python 3.10.12, `python-dotenv` 1.2.3,
divergências de parsing contra Node v24.18.0 (ver [12-formato-dotenv.md](12-formato-dotenv.md)).
**Não executado aqui:** `pydantic-settings`, Django, FastAPI, gunicorn —
conteúdo vindo da documentação oficial de cada projeto, consultada em 14/08/2026.

**Próximo:** [18-outras-plataformas.md](18-outras-plataformas.md) · Voltar ao [mapa](00-MAPA.md)
