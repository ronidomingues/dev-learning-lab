# Bind mount vs volume: onde os dados realmente moram

> **Nível:** intermediário
> **Última verificação:** 18/08/2026

## 1. O problema

Um container é descartável. Sua camada de escrita morre com ele:

```bash
docker run -d --name db postgres:17-alpine
# ... horas de trabalho, dados inseridos ...
docker rm -f db
# tudo perdido, sem aviso e sem volta
```

Isso não é defeito — é o desenho. Container é processo, e processo não guarda
estado. Mas bancos de dados precisam guardar. A ponte entre as duas coisas é
**montar** um armazenamento externo dentro do container.

## 2. Os três tipos

| | Volume nomeado | Bind mount | tmpfs |
|---|---|---|---|
| Onde fica | `/var/lib/docker/volumes/` | caminho que você escolhe | RAM |
| Quem gerencia | Docker | você | Docker |
| Sobrevive ao `rm` do container | sim | sim | **não** |
| Você abre no explorador de arquivos | não (dono root) | sim | não |
| Funciona igual em Linux/macOS/Windows | **sim** | não (I/O lento fora do Linux) | sim |
| Backup | `docker run --rm -v ...` | `cp`, `rsync` | não se aplica |
| Desempenho | nativo no Linux | nativo no Linux, **ruim** no macOS/Windows | o mais rápido |

Sintaxe:

```yaml
volumes:
  - pgdata:/var/lib/postgresql/data   # volume nomeado (sem / no início)
  - ./config:/app/config              # bind mount (começa com ./ ou /)
  - /srv/midia:/midia:ro              # bind mount absoluto, read-only

tmpfs:
  - /tmp:size=64m                     # tmpfs
```

A regra de leitura: **se o lado esquerdo começa com `/` ou `./`, é bind mount.
Se é um nome simples, é volume.**

## 3. Como decidir — a única pergunta que importa

> **Um humano precisa abrir esse arquivo fora do container?**

- **Sim** → bind mount
- **Não** → volume nomeado

Aplicando:

| Dado | Escolha | Por quê |
|---|---|---|
| Dados do Postgres | volume | ninguém abre os arquivos internos do Postgres na mão |
| Biblioteca de mídia do FlixARD | **bind mount** | você copia filme para lá com rsync/Samba |
| Gravações do CFTV (MotionEye) | **bind mount** | você assiste e arquiva os vídeos por fora |
| Código-fonte em desenvolvimento | **bind mount** | você edita no editor do host |
| Thumbnails gerados | volume | artefato derivado, regenerável |
| Dumps de backup | **bind mount** | você precisa levar para outra máquina |
| Certificados do Caddy | volume | o Caddy gerencia sozinho |
| `/tmp` de app read-only | tmpfs | efêmero por definição |

### Por que não bind mount para tudo?

Parece mais simples — você vê os arquivos. Três problemas reais:

1. **Permissões.** O processo no container é UID 10001; os arquivos no host são
   seus (UID 1000). Resultado: `Permission denied`. Volumes nomeados são criados
   já com o dono certo.
2. **Portabilidade.** `/home/ronivaldo/dados` não existe no servidor. O compose
   deixa de funcionar em outra máquina.
3. **Desempenho fora do Linux.** No macOS e no Windows, bind mount atravessa uma
   camada de tradução de filesystem. Um `npm install` em bind mount no macOS pode
   ser 10× mais lento. Volume nomeado fica dentro da VM Linux e é rápido.

### Por que não volume nomeado para tudo?

Porque quando você precisa dos arquivos, precisa mesmo:

```bash
sudo ls /var/lib/docker/volumes/flixard_midia/_data
# funciona, mas exige sudo, é um caminho ilegível e
# não dá para apontar o Samba para lá de forma sustentável
```

Para a biblioteca de mídia do FlixARD isso é inviável.

## 4. A armadilha do volume anônimo

```bash
docker run -v /app/dados minha-app    # SEM nome do lado esquerdo
```

Isto cria um volume **anônimo** com nome tipo
`3f8a9c...b2e1`. Ele sobrevive ao container, ninguém sabe para que serve, e vai
acumulando.

A imagem do Postgres tem `VOLUME /var/lib/postgresql/data` no Dockerfile. Se
você **não** montar nada ali, cada `docker run` cria um volume anônimo novo.
Rodou 20 vezes durante testes? 20 volumes órfãos com dados dentro.

```bash
docker volume ls -f dangling=true      # ver os órfãos
docker volume prune                    # remover (LEIA a lista antes)
```

É uma das principais causas de "meu disco encheu do nada".

## 5. A armadilha do mount que esconde

Montar por cima de um diretório que já tem conteúdo na imagem **esconde** o
conteúdo original:

```yaml
volumes:
  - ./meu-config:/etc/nginx     # esconde TODA a config do nginx
```

O nginx sobe sem `mime.types`, sem `conf.d`, e falha de um jeito confuso.
Monte o **arquivo específico**, não o diretório:

```yaml
volumes:
  - ./nginx.conf:/etc/nginx/nginx.conf:ro
```

Exceção importante: **volume nomeado vazio** montado sobre diretório com
conteúdo é **pré-populado** com o conteúdo da imagem na primeira vez. Bind mount
**nunca** pré-popula — ele esconde. Comportamentos opostos, e é fonte constante
de confusão.

```
bind mount sobre /etc/nginx      -> conteúdo da imagem some
volume NOVO sobre /etc/nginx     -> conteúdo da imagem é copiado para o volume
volume JÁ USADO sobre /etc/nginx -> conteúdo do volume prevalece
```

## 6. Permissões: o erro que todo mundo leva

```bash
docker compose up
# app: PermissionError: [Errno 13] Permission denied: '/app/dados/arquivo.db'
```

O processo é UID 10001. O diretório do host pertence ao UID 1000 com permissão
`755` — o "outros" pode ler e entrar, mas não escrever.

Três soluções, em ordem de preferência:

```bash
# 1) Alinhar o dono no host (mais limpo para bind mount)
sudo chown -R 10001:10001 ./dados

# 2) Rodar o container com o SEU uid (bom em desenvolvimento)
#    compose:  user: "${UID}:${GID}"
UID=$(id -u) GID=$(id -g) docker compose up

# 3) Usar volume nomeado, e deixar o Docker resolver o dono
```

Em desenvolvimento com bind mount de código, a opção 2 costuma ser a que menos
atrapalha — os arquivos que o container criar pertencerão a você.

## 7. Backup

Volume nomeado não tem caminho conveniente. O padrão é um container efêmero:

```bash
# Backup
docker run --rm \
  -v flixard_pgdata:/origem:ro \
  -v "$(pwd)":/destino \
  alpine tar czf /destino/pgdata-$(date +%F).tar.gz -C /origem .

# Restauração
docker run --rm \
  -v flixard_pgdata:/destino \
  -v "$(pwd)":/origem \
  alpine sh -c "rm -rf /destino/* && tar xzf /origem/pgdata-2026-08-18.tar.gz -C /destino"
```

**Para banco de dados, isso não é o ideal.** Copiar arquivos de um Postgres
**em execução** pode capturar um estado inconsistente. O certo é o dump lógico:

```bash
docker compose exec -T db pg_dump -U appuser appdb | gzip > backup.sql.gz
```

É o que o serviço de backup do
[sistema financeiro](../08-projeto-aplicado/compose-sistema-financeiro.md) faz.

E a regra que vale repetir: **um backup que nunca foi restaurado não é um
backup — é esperança.** Teste a restauração.

## 8. Comandos

```bash
docker volume ls
docker volume inspect <nome>              # ver o Mountpoint real
docker volume create meu-volume
docker volume rm meu-volume
docker volume prune                       # remove os não usados
docker volume ls -f dangling=true         # listar órfãos ANTES de remover

docker inspect <container> --format '{{json .Mounts}}' | python3 -m json.tool
docker system df -v                       # espaço por volume
```

O `docker volume inspect` é o que responde "onde isso está de verdade":

```json
[{ "Name": "flixard_pgdata",
   "Mountpoint": "/var/lib/docker/volumes/flixard_pgdata/_data" }]
```

## 9. Os cinco porquês

1. **Por que dados somem quando o container é removido?** Moram na camada de
   escrita, que é criada e destruída com o container.
2. **Por que a camada de escrita é descartável?** Porque containers são
   projetados como processos: efêmeros, substituíveis, escaláveis.
3. **Por que esse desenho?** Porque a alternativa — container com estado — impede
   substituir uma instância por outra, que é a base de deploy sem downtime e de
   escala horizontal.
4. **Por que isso importa se rodo em uma máquina só?** Porque é o mesmo desenho
   que permite `docker compose up --force-recreate` sem medo. Estado fora do
   container é o que torna o container recriável.
5. **Por que então existe camada de escrita?** Porque processos precisam de
   `/tmp`, cache e logs transitórios. **Parada legítima: decisão de arquitetura
   que separa deliberadamente o efêmero do durável.**

## 10. Erros que você provavelmente vai cometer

| Sintoma | Causa raiz | Correção |
|---|---|---|
| Dados somem no `down` | sem volume, ou rodou `down -v` | declarar volume; cuidado com o `-v` |
| `Permission denied` no diretório montado | UID do container ≠ dono no host | `chown` no host, ou `user:` no compose |
| Config da imagem "desapareceu" | bind mount de diretório escondeu o conteúdo | montar o **arquivo**, não o diretório |
| Volume nomeado veio populado sem eu ter copiado | volume novo é pré-populado pela imagem | comportamento esperado |
| Bind mount vazio no container | caminho do host não existe (o Docker cria vazio) | conferir o caminho absoluto |
| Disco cheio de volumes | volumes anônimos acumulados | `docker volume ls -f dangling=true` e `prune` |
| `npm install` lentíssimo no macOS | bind mount atravessa tradução de FS | volume nomeado para `node_modules` |
| Restauração de backup corrompida | copiou arquivos de banco em execução | usar `pg_dump` |

## 11. Autoteste

1. Qual pergunta única decide entre bind mount e volume nomeado?
2. Por que a biblioteca do FlixARD é bind mount e os thumbnails são volume?
3. O que acontece ao montar bind mount sobre `/etc/nginx`? E volume novo?
4. O que é volume anônimo e por que é problema?
5. Como fazer backup de um volume nomeado sem parar o container?
6. Por que `tar` de um volume de Postgres em execução é arriscado?
7. Por que bind mount é lento no macOS e não no Linux?
8. Container é UID 10001, diretório do host é do UID 1000. Duas soluções.

---
[exercício →](exercicio.md) · [índice](../00-indice.md)
