# Depuração: logs, exec, inspect

> **Nível:** intermediário
> **Última verificação:** 18/08/2026

## 1. Log em container é stream, não arquivo

A regra que muda tudo: **a aplicação escreve em `stdout`/`stderr`, e o Docker
captura**. Escrever em arquivo dentro do container é o erro nº 1 de
observabilidade — o arquivo morre com o container, e ninguém o lê.

```python
# ✅ certo, em container
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# ❌ errado
logging.basicConfig(filename="/var/log/app.log")
```

E em Python, `PYTHONUNBUFFERED=1` é obrigatório: sem ele o stdout fica em buffer
e seus logs só aparecem quando o buffer enche — ou nunca, se o processo travar.
É a causa do clássico "meu container não loga nada".

## 2. `docker logs`

```bash
docker compose logs -f api            # acompanhar (follow)
docker compose logs --tail=100 api    # últimas 100 linhas
docker compose logs --since=10m       # últimos 10 minutos
docker compose logs -t api            # com carimbo de tempo
docker compose logs                   # todos os serviços, intercalados

docker logs -f --tail=50 <container>  # sem compose
```

O mais útil no dia a dia:

```bash
docker compose logs -f --tail=100 api
```

`--tail` evita despejar horas de log; `-f` acompanha dali em diante.

### O container morreu — como ver o log dele

```bash
docker compose logs api          # funciona mesmo com o container parado
docker ps -a                     # ver o exit code
```

O **exit code** já diz muito:

| Código | Significado |
|---|---|
| 0 | terminou normalmente (para um serviço, geralmente é bug) |
| 1 | erro genérico da aplicação |
| 125 | erro do próprio Docker (opção inválida) |
| 126 | comando encontrado mas não executável (falta `chmod +x`) |
| 127 | **comando não encontrado** (típico: caminho errado no `CMD`) |
| 137 | **SIGKILL** — quase sempre OOM (memória) |
| 139 | SIGSEGV — falha de segmentação |
| 143 | SIGTERM — parada limpa |

O **137** é o mais importante: significa que o kernel matou o processo por
falta de memória. Confirme:

```bash
docker inspect <container> --format '{{.State.OOMKilled}}'
# true = foi OOM
```

### Limitar o log (senão o disco enche)

```yaml
services:
  api:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

Sem isso, o log cresce sem limite. É uma causa comum e evitável de disco cheio
em servidor de homelab que roda há meses.

## 3. `docker exec` — entrar no container

```bash
docker compose exec api sh            # shell
docker compose exec api bash          # se a imagem tiver bash
docker compose exec -u root api sh    # como root (para depurar permissão)
docker compose exec api env           # ver as variáveis
docker compose exec api ls -la /app/data
```

Imagens `slim` e `alpine` frequentemente **não têm `bash`** — use `sh`. Se nem
`sh` existir (distroless), veja a seção 5.

### `exec` vs `run`

| | `exec` | `run` |
|---|---|---|
| Container | um **já em execução** | cria um **novo** |
| Estado | o real, com os dados atuais | limpo |
| Uso | investigar o que está acontecendo | rodar tarefa pontual |

```bash
docker compose exec api sh              # investigar o container vivo
docker compose run --rm api pytest      # rodar testes num container novo
```

Erro comum: usar `run` para investigar. Você entra num container **novo**, não
vê os dados do que está com problema, e conclui erradamente que está tudo bem.

## 4. `docker inspect` — a fonte da verdade

```bash
# Está saudável?
docker inspect <container> --format '{{.State.Health.Status}}'

# Por que o healthcheck falha? (mostra a saída dos últimos testes)
docker inspect <container> --format '{{json .State.Health}}' | python3 -m json.tool

# Foi morto por falta de memória?
docker inspect <container> --format '{{.State.OOMKilled}}'

# Qual o IP e em que redes está?
docker inspect <container> --format '{{json .NetworkSettings.Networks}}' | python3 -m json.tool

# O que está montado onde?
docker inspect <container> --format '{{json .Mounts}}' | python3 -m json.tool

# Qual comando ele está rodando de verdade?
docker inspect <container> --format '{{.Config.Cmd}} {{.Config.Entrypoint}}'

# Tem segredo vazando no ambiente?
docker inspect <container> | grep -iE 'password|secret|token'
```

O segundo comando é o mais valioso e o menos conhecido: quando um container fica
`unhealthy`, o `inspect` guarda a **saída** dos últimos healthchecks. Em vez de
adivinhar, você lê o erro exato.

## 5. Depurar imagem sem shell

Imagem distroless ou `scratch` não tem `sh`. Duas técnicas:

### Anexar um container de ferramentas à mesma rede e PID

```bash
docker run --rm -it \
  --network container:minha-api \
  --pid container:minha-api \
  nicolaka/netshoot
```

Dentro dele, você compartilha a **rede** e a **lista de processos** do alvo:

```bash
ps aux                      # vê os processos do container alvo
curl localhost:8000/health  # o localhost é o dele
dig db
netstat -tlnp
tcpdump -i any port 5432
```

### `docker debug` (Docker Desktop)

```bash
docker debug <container>
```

Anexa um shell com ferramentas a qualquer container, inclusive distroless, sem
modificar a imagem. Requer Docker Desktop com assinatura Pro ou superior.

## 6. Outros comandos que resolvem

```bash
docker stats                        # CPU/memória em tempo real, por container
docker stats --no-stream            # uma leitura só

docker top <container>              # processos, do lado de fora
docker port <container>             # mapeamento de portas efetivo
docker diff <container>             # o que MUDOU no filesystem desde a imagem
docker cp <container>:/app/log.txt ./  # copiar arquivo para fora

docker events                       # eventos em tempo real (útil em restart loop)
```

`docker diff` é subestimado: mostra exatamente o que o container escreveu
(`A` = adicionado, `C` = alterado, `D` = removido). Ótimo para descobrir que a
aplicação está gravando num lugar que deveria ser volume.

`docker stats` responde na hora a "por que está lento" — e se a memória está
colada no limite, você achou o motivo do exit 137.

## 7. Roteiro de diagnóstico

Siga nesta ordem. Cada passo elimina uma classe de causas:

```
1. docker compose ps          → está rodando? healthy? qual exit code?
       │
       ├─ não está rodando  → docker compose logs <svc>   (por que morreu?)
       │                       docker ps -a                (exit code?)
       │
       ├─ restart loop      → docker compose logs --tail=50
       │                       docker inspect ... OOMKilled
       │
       ├─ unhealthy         → docker inspect ... .State.Health  (saída do check)
       │
       └─ up e healthy, mas não responde
                            → docker port <c>              (porta certa?)
                              docker compose exec <c> netstat -tlnp
                                                           (escuta em 0.0.0.0?)
                              curl de dentro                (app responde?)
                              docker network inspect        (rede certa?)
```

O quarto ramo é o mais frequente e o mais mal diagnosticado. A sequência
`docker port` → `netstat` de dentro → `curl` de dentro isola em três comandos
se o problema é mapeamento, bind ou aplicação.

## 8. Um caso real deste curso

Durante a escrita, o healthcheck do projeto modelo falhava enquanto o `curl`
funcionava — o mesmo endereço, resultados diferentes:

```bash
curl -s http://127.0.0.1:8000/health
# {"status":"ok","database":"ok"}      HTTP 200

python healthcheck.py; echo $?
# 1                                     ← unhealthy
```

O diagnóstico foi rodar o cliente que falhava e **ler o traceback completo**, em
vez de confiar no exit code:

```python
import urllib.request, traceback
try:
    with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=3) as r:
        print(r.status)
except Exception:
    traceback.print_exc()
```

```
urllib.error.HTTPError: HTTP Error 502: cannotconnect
```

`502` de um servidor local é impossível — 502 é resposta de **proxy**. Daí:

```bash
env | grep -i proxy
# HTTP_PROXY=http://...
# no_proxy=localhost, 127.0.0.0/8, ::1     ← note os espaços
```

O `curl` tolera espaço depois da vírgula no `no_proxy`; o `urllib` do Python
não, conclui que precisa de proxy e manda `127.0.0.1` para o proxy corporativo.

**A lição de método:** quando duas ferramentas discordam sobre o mesmo endereço,
a diferença está no **cliente**, não no servidor. E um código de status
impossível (502 local) é a pista que aponta para a camada intermediária.

O caso completo está no [módulo 08](../08-projeto-aplicado/dockerfile-fastapi-sqlalchemy.md).

## 9. Autoteste

1. Por que log em arquivo dentro do container é erro?
2. O que `PYTHONUNBUFFERED=1` resolve?
3. Exit code 137: o que é e como confirmar?
4. Diferença entre `exec` e `run` para investigar um problema.
5. Container `unhealthy`: qual comando mostra **por quê**?
6. Como depurar uma imagem sem shell?
7. Para que serve `docker diff`?
8. Container up e healthy mas não responde: quais três comandos, em ordem?

---
[troubleshooting →](troubleshooting-comum.md) · [índice](../00-indice.md)
