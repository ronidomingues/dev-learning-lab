# Compose aplicado ao sistema financeiro estudantil

> **Nível:** avançado
> **Última verificação:** 18/08/2026
> **Arquivo executável:** [`sistema-financeiro/compose.yaml`](sistema-financeiro/compose.yaml) — validado com `docker compose config`

## O que muda quando o dado é financeiro

O FlixARD guarda filmes. Se vazar, é constrangedor. Este sistema guarda **dado
financeiro pessoal**. Se vazar, é dano real e possivelmente obrigação legal
(LGPD). Isso muda três coisas de forma não-negociável:

1. **Segredo não vai em `environment:`** — vai por Docker secret.
2. **Backup é parte da arquitetura**, não tarefa que você lembra de fazer.
3. **A aplicação roda sem privilégio nenhum** — filesystem read-only,
   capabilities zeradas, sem escalada.

O resto (redes separadas, healthcheck, limites) é igual ao FlixARD, e está
explicado [lá](compose-flixard.md).

## Decisão 1 — secrets em arquivo, não em variável de ambiente

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

### Por que variável de ambiente é ruim para segredo

Não é superstição. São quatro vazamentos concretos:

| Onde vaza | Comando que revela |
|---|---|
| Metadados do container | `docker inspect <container>` mostra todo o `Env` |
| Processo | qualquer processo do container lê `/proc/1/environ` |
| Logs de orquestrador | crash dumps e eventos frequentemente serializam o ambiente |
| Filhos | todo subprocesso herda o ambiente inteiro, inclusive o que ele não deveria ver |

Com secret montado como arquivo em `/run/secrets/`, o `docker inspect` mostra só
o **nome** do secret. O conteúdo está num tmpfs, em RAM, com permissão restrita.

### Como a aplicação lê

O padrão `_FILE` (usado por Postgres, MySQL e boa parte das imagens oficiais):

```python
import os
from pathlib import Path

def ler_segredo(nome: str, padrao: str | None = None) -> str:
    """Lê de <NOME>_FILE se existir; senão cai para <NOME>."""
    caminho = os.getenv(f"{nome}_FILE")
    if caminho and Path(caminho).exists():
        return Path(caminho).read_text().strip()
    valor = os.getenv(nome, padrao)
    if valor is None:
        raise RuntimeError(f"segredo obrigatório ausente: {nome}")
    return valor

DATABASE_URL = ler_segredo("DATABASE_URL")
```

O `.strip()` não é detalhe: um `echo senha > arquivo` grava `\n` no fim, e a
senha com quebra de linha falha a autenticação com uma mensagem que não ajuda
em nada (`password authentication failed`). Esse `\n` invisível já custou
muitas horas a muita gente.

### A limitação honesta

Docker secrets fora do Swarm são **arquivos do host**. Não há criptografia em
repouso nem rotação automática — o ganho é não vazar em `inspect`, log e
ambiente, o que já é grande. Para criptografia de verdade, o próximo degrau é
HashiCorp Vault, SOPS ou o gerenciador de segredos da nuvem. Ver
[secrets e variáveis sensíveis](../06-seguranca/secrets-e-variaveis-sensiveis.md).

E o essencial: **a pasta `secrets/` nunca vai para o git**. Há um
`.gitignore` dentro dela que ignora tudo menos ele mesmo.

## Decisão 2 — publicar só no loopback

```yaml
ports:
  - "127.0.0.1:8000:8000"
```

`"8000:8000"` faz o Docker escutar em `0.0.0.0` — **toda a sua LAN** alcança a
API. Com o prefixo `127.0.0.1:`, só o próprio host alcança; o acesso externo
passa obrigatoriamente pelo proxy reverso, com TLS e autenticação.

E aqui vai o detalhe que quase ninguém sabe até levar um susto: **o Docker
escreve regras de iptables que passam por cima do UFW**. Você pode ter o
`ufw deny 8000` ativo e a porta continuar aberta para a rede, porque a regra do
Docker é avaliada antes. O prefixo de loopback é o que realmente resolve.

## Decisão 3 — endurecimento do container

```yaml
read_only: true
tmpfs:
  - /tmp:size=64m
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
```

| Diretiva | O que impede | O que você perde |
|---|---|---|
| `read_only: true` | atacante gravar webshell ou binário no container | precisa declarar em `tmpfs` tudo que a app escreve |
| `tmpfs: /tmp` | — | conteúdo some no restart (é o desejado) |
| `no-new-privileges` | escalada via binário `setuid` (o truque clássico pós-invasão) | nada, na prática |
| `cap_drop: ALL` | quase toda manipulação de kernel, rede e dispositivo | se precisar de porta < 1024, requer `cap_add: NET_BIND_SERVICE` |

`cap_drop: ALL` é o mais subestimado. Por padrão o Docker concede ~14
capabilities do kernel que praticamente nenhuma aplicação web usa — incluindo
`CAP_CHOWN`, `CAP_SETUID` e `CAP_NET_RAW` (que permite forjar pacote e fazer
ARP spoofing na rede do Docker). Remover tudo e reconceder só o necessário é a
postura correta.

Ordem prática: suba com `cap_drop: ALL`, veja o que quebra, reconceda o mínimo.
Quase nunca quebra nada.

## Decisão 4 — backup como serviço

```yaml
backup:
  image: postgres:17-alpine
  entrypoint: ["/bin/sh", "/backup.sh"]
```

O script faz `pg_dump | gzip` a cada 24 h em `./backup` (bind mount, para você
conseguir levar embora) e apaga o que passa de 14 dias.

Três decisões deliberadas:

- **Mesma imagem do Postgres**, porque as versões do `pg_dump` e do servidor
  precisam ser compatíveis. `pg_dump` mais antigo que o servidor **recusa** rodar.
- **Loop com `sleep`, não cron.** Menos peças, e o log vai para `docker logs`.
  Um cron dentro de container escreve em arquivo que ninguém lê.
- **Bind mount, não volume nomeado**, para o dump ser acessível ao seu
  script de sincronização para outra máquina.

E a frase que está escrita como comentário no próprio script porque é a mais
importante da página: *um backup que nunca foi restaurado não é um backup — é
esperança*. Marque no calendário e teste a restauração:

```bash
gunzip -c backup/financeiro_2026-08-18_030000.sql.gz \
  | docker compose exec -T db psql -U financeiro -d teste_restore
```

## Como rodar

```bash
cd 08-projeto-aplicado/sistema-financeiro

# 1) Gerar segredos de verdade (não use os de exemplo)
openssl rand -base64 32 > secrets/db_password.txt
SENHA=$(cat secrets/db_password.txt)
echo "postgresql+asyncpg://financeiro:${SENHA}@db:5432/financeiro" > secrets/database_url.txt
chmod 600 secrets/*.txt

# 2) Validar e subir
docker compose config --quiet
docker compose up -d

# 3) Conferir o endurecimento
docker compose exec api id                    # uid=10001
docker compose exec api touch /teste          # deve FALHAR: read-only
docker compose exec api cat /run/secrets/db_password   # o segredo está aqui
docker inspect $(docker compose ps -q api) | grep -i password   # não deve achar nada
```

O terceiro e o quarto comando juntos são a demonstração: o segredo é legível
**dentro** do container e invisível **de fora**.

## Verificação executada

```bash
docker compose config --quiet
# saída obtida: (vazio) -> válido

docker compose config | grep -A2 'cap_drop\|read_only\|no-new-privileges'
# saída obtida:
#     cap_drop:
#       - ALL
#     read_only: true
#       - no-new-privileges:true
```

**Não validado:** `up` de fato, e portanto o comportamento em runtime do
`read_only` e do `cap_drop` (daemon indisponível na máquina de escrita).

## Erros que você provavelmente vai cometer

| Sintoma | Causa raiz | Correção |
|---|---|---|
| `password authentication failed` mesmo com a senha certa | `\n` no fim do arquivo de secret | `.strip()` ao ler; gerar com `printf` em vez de `echo` |
| App quebra com `Read-only file system` | `read_only: true` sem `tmpfs` para o que ela escreve | mapear o caminho em `tmpfs:` |
| `permission denied` ao abrir socket na porta 80 | `cap_drop: ALL` tirou `NET_BIND_SERVICE` | usar porta ≥ 1024 (é o certo), ou `cap_add: NET_BIND_SERVICE` |
| Backup gera arquivo de 0 byte | `pg_dump` roda antes do banco aceitar conexão | `depends_on: condition: service_healthy` |
| `pg_dump: server version mismatch` | imagem do backup mais antiga que a do banco | usar a mesma tag nos dois |
| Segredo commitado por acidente | `secrets/` fora do `.gitignore` | rotacionar o segredo **e** reescrever o histórico — arquivo commitado é arquivo vazado |

## Autoteste

1. Cite dois lugares concretos onde uma senha em `environment:` vaza.
2. O que o padrão `_FILE` resolve, e por que o `.strip()` importa?
3. Qual a diferença prática entre `"8000:8000"` e `"127.0.0.1:8000:8000"`?
4. Por que o `ufw deny 8000` pode não ter efeito nenhum?
5. O que `cap_drop: ALL` remove que sua API web provavelmente não usa?
6. Por que o container de backup usa a mesma imagem do banco?
7. Docker secrets fora do Swarm são criptografados em repouso? Qual é o ganho real?
8. Um segredo foi commitado e você já removeu o arquivo. Está resolvido?

---
[← FlixARD](compose-flixard.md) · [próximos passos →](../09-proximos-passos.md) · [índice](../00-indice.md)
