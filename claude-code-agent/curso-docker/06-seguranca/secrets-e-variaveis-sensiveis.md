# Secrets e variáveis sensíveis

> **Nível:** intermediário → avançado
> **Última verificação:** 18/08/2026

## 1. As quatro formas erradas, em ordem de gravidade

### 1º pior — segredo no Dockerfile

```dockerfile
ENV DB_PASSWORD=SenhaSuperSecreta123
```

Fica gravado na imagem **para sempre**. Qualquer pessoa que baixe a imagem lê:

```bash
docker inspect imagem | grep -i password
docker history --no-trunc imagem | grep -i password
```

Se a imagem foi publicada, o segredo está comprometido. Apagar a imagem não
desfaz o download de quem já baixou. **Rotacione.**

### 2º — segredo em `--build-arg`

```bash
docker build --build-arg SENHA=x .
```

`ARG` não vai para a imagem final, o que dá falsa sensação de segurança. Mas o
comando **aparece no `docker history`**, e é recuperável por quem tiver a imagem.

### 3º — arquivo copiado e "apagado"

```dockerfile
COPY credenciais.json /app/
RUN configurar && rm /app/credenciais.json
```

[Camadas são aditivas](../01-fundamentos/conceito.md). O arquivo continua na
camada do `COPY`. Extração:

```bash
docker save imagem -o img.tar && mkdir x && tar -xf img.tar -C x
grep -rl "credencial" x/
```

### 4º — segredo em `environment:`

O menos grave dos quatro, e ainda assim ruim. Vaza em quatro lugares:

| Onde | Como se vê |
|---|---|
| Metadados | `docker inspect <container>` mostra todo o `Env` |
| Processo | `cat /proc/1/environ` de dentro do container |
| Logs | crash dumps e eventos de orquestrador serializam o ambiente |
| Filhos | todo subprocesso herda o ambiente inteiro |

O quarto é o mais subestimado: se sua aplicação chama um binário externo, esse
binário recebe **todas** as suas senhas, precise ou não.

## 2. A forma certa em runtime: secret montado como arquivo

```yaml
services:
  api:
    environment:
      DATABASE_URL_FILE: /run/secrets/database_url   # o CAMINHO
    secrets:
      - database_url

secrets:
  database_url:
    file: ./secrets/database_url.txt
```

O Docker monta o conteúdo em `/run/secrets/database_url`, num **tmpfs** (RAM),
com permissão restrita. O `docker inspect` mostra só o **nome** do secret.

### Lendo na aplicação — o padrão `_FILE`

Convenção usada por Postgres, MySQL e a maioria das imagens oficiais:

```python
import os
from pathlib import Path


def ler_segredo(nome: str, padrao: str | None = None) -> str:
    """Lê de <NOME>_FILE se existir; senão cai para <NOME>."""
    caminho = os.getenv(f"{nome}_FILE")
    if caminho:
        arquivo = Path(caminho)
        if arquivo.exists():
            # .strip() OBRIGATÓRIO — ver explicação abaixo
            return arquivo.read_text(encoding="utf-8").strip()
        raise RuntimeError(f"{nome}_FILE aponta para {caminho}, que não existe")

    valor = os.getenv(nome, padrao)
    if valor is None:
        raise RuntimeError(f"segredo obrigatório ausente: {nome}")
    return valor


DATABASE_URL = ler_segredo("DATABASE_URL")
```

Com pydantic-settings:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir="/run/secrets")
    database_url: str        # lido de /run/secrets/database_url automaticamente
```

### O `\n` que custa horas

```bash
echo "minha-senha" > secrets/db_password.txt    # grava "minha-senha\n"
```

A senha com quebra de linha falha a autenticação com
`password authentication failed` — mensagem que não sugere em nada a causa.
Você confere a senha caractere por caractere, ela está certa, e nada funciona.

Duas defesas, use as duas:

```bash
printf 'minha-senha' > secrets/db_password.txt   # sem \n
```
```python
Path(caminho).read_text().strip()                 # tolerante
```

### A limitação honesta

Docker secrets **fora do Swarm** são apenas arquivos do host montados em tmpfs.
Não há criptografia em repouso nem rotação automática. O ganho real é:

- não vaza em `docker inspect`;
- não vaza para subprocessos;
- não vaza em log de orquestrador;
- fica em RAM, não em disco do container.

Já é bastante. Para criptografia em repouso e rotação, o próximo degrau é Vault,
SOPS ou o gerenciador da nuvem — assunto do [módulo 09](../09-proximos-passos.md).

## 3. Segredo em tempo de build

Às vezes o **build** precisa de segredo: token de registry privado, chave SSH
para repositório privado. A solução é `RUN --mount=type=secret`:

```dockerfile
# syntax=docker/dockerfile:1

RUN --mount=type=secret,id=pip_token \
    PIP_INDEX_URL="https://$(cat /run/secrets/pip_token)@pypi.empresa.com/simple" \
    pip install -r requirements.txt
```

```bash
docker build --secret id=pip_token,src=./token.txt .
```

O arquivo é montado **durante** aquele `RUN` e **nunca vira camada**. Não aparece
em `docker history`, não fica na imagem.

Para chave SSH existe uma variante que nem expõe a chave:

```dockerfile
RUN --mount=type=ssh git clone git@github.com:empresa/privado.git
```
```bash
docker build --ssh default .
```

O container fala com o **agente SSH** do host; a chave privada nunca entra.

## 4. Higiene de arquivos

`.gitignore`:

```
.env
.env.*
!.env.example
secrets/
*.pem
*.key
```

`.dockerignore` — **igualmente importante e sempre esquecido**:

```
.env
.env.*
!.env.example
secrets/
*.pem
*.key
.git
```

Sem a segunda lista, um `COPY . .` leva seus segredos para dentro da imagem.

E dentro da pasta de segredos, um `.gitignore` que se autoprotege:

```
# secrets/.gitignore
*
!.gitignore
```

Assim a pasta existe no repositório (para o compose não falhar), mas nenhum
conteúdo dela é rastreado.

## 5. Já commitei um segredo. E agora?

Nesta ordem, sem pular etapas:

1. **Rotacione o segredo imediatamente.** Trocar a senha é a única ação que
   realmente resolve. Tudo abaixo é limpeza.
2. **Remova do histórico** — o arquivo está em todos os commits anteriores:
   ```bash
   pip install git-filter-repo
   git filter-repo --path secrets/db_password.txt --invert-paths
   git push --force --all      # coordene com a equipe antes
   ```
3. **Se o repositório é público, presuma vazamento total.** Há bots que varrem o
   GitHub em tempo real procurando credenciais. Minutos bastam.
4. **Audite o uso.** Logs de acesso do banco, do provedor de nuvem, do serviço.

O passo 1 é o único que importa de verdade. Muita gente faz o 2 e acha que
resolveu — não resolveu.

## 6. Verificação

Ferramentas que valem instalar:

```bash
# Varrer o repositório inteiro (inclusive histórico) por segredos
docker run --rm -v "$(pwd)":/repo zricethezav/gitleaks:latest detect -s /repo -v

# Varrer imagem por vulnerabilidades E segredos
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image --scanners vuln,secret minha-api:1.0
```

E as conferências manuais que você deve fazer antes de publicar qualquer imagem:

```bash
docker inspect minha-api:1.0 | grep -iE 'password|secret|token|key'
docker history --no-trunc minha-api:1.0 | grep -iE 'password|secret|token'
```

Se qualquer um dos dois retornar algo, **não publique**.

## 7. Erros que você provavelmente vai cometer

| Sintoma | Causa raiz | Correção |
|---|---|---|
| `password authentication failed` com a senha certa | `\n` no fim do arquivo | `printf` e `.strip()` |
| Segredo em `docker inspect` | está em `environment:` ou `ENV` | migrar para `secrets:` |
| `/run/secrets/x: no such file` | secret não declarado no serviço | adicionar em `secrets:` do serviço, além do bloco global |
| Segredo na imagem apesar do `rm` | camadas são aditivas | `--mount=type=secret` ou multi-stage |
| `.env` foi para a imagem | ausente do `.dockerignore` | acrescentar |
| Segredo commitado | falta de `.gitignore` | **rotacionar** e depois limpar histórico |
| Subprocesso recebeu senha que não devia | herança de ambiente | secret em arquivo |

## 8. Autoteste

1. Ordene da pior para a menos ruim: `ENV`, `--build-arg`, `environment:`.
2. Cite os quatro lugares onde uma senha em `environment:` vaza.
3. Por que o `.strip()` é obrigatório ao ler secret de arquivo?
4. O que `RUN --mount=type=secret` garante que um `COPY` + `rm` não garante?
5. Docker secrets fora do Swarm são criptografados? Qual é o ganho real?
6. Segredo commitado: qual é o **primeiro** passo, e por quê?
7. Por que o `.dockerignore` importa tanto quanto o `.gitignore`?
8. Dois comandos para auditar uma imagem antes de publicar.

---
[← usuário não-root](usuario-nao-root.md) · [checklist →](checklist-hardening.md) · [índice](../00-indice.md)
