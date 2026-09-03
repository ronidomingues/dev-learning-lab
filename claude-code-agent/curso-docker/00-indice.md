# Curso de Docker — do zero à produção

> **Criado em:** 18/08/2026
> **Para:** desenvolvedor com experiência em Python, iniciante em Docker
> **Projetos de referência:** FlixARD (streaming local), sistema financeiro
> estudantil, CFTV do quarto (MotionEye)

Curso completo e prático, com exemplos **validados por execução real** sempre
que possível. Cada módulo tem seção de erros reais, tabelas de decisão e
autoteste.

---

## Como este curso foi verificado

Transparência sobre o que é medido e o que é fundamentado.

**Ambiente de escrita:** Docker CLI 29.1.3 · Docker Compose v5.5.0 ·
hadolint 2.15.1 · Python 3.10.12 (Linux) — em 18/08/2026.

**O daemon do Docker não estava acessível** nessa máquina (socket `root:docker`,
usuário fora do grupo, `sudo` com senha). A validação foi feita assim:

| Frente | Ferramenta | Resultado |
|---|---|---|
| Aplicação do projeto modelo | `pytest` | **4 testes passando** |
| API em execução | `uvicorn` + `curl` | `/health` 200, `POST /media` 201 |
| Healthcheck | execução direta | exit 0 com app no ar, exit 1 sem |
| Dockerfiles | `hadolint` | **zero avisos** em todos os publicados |
| Arquivos compose | `docker compose config` | **todos válidos** |
| Versões de dependência | API do PyPI | conferidas em 18/08/2026 |
| Tags de imagem base | API do Docker Hub | existência, data e tamanho conferidos |

**Não validado:** `docker build` e `docker compose up` de fato. Portanto,
tamanhos de imagem e tempos de build no texto são **estimativas fundamentadas,
não medições** — e estão marcados como tal onde aparecem.

**Três bugs reais** foram encontrados durante essa validação e viraram material
didático: um erro de `importlib.reload` no teste, um healthcheck derrubado por
proxy corporativo, e um pino de versão apt que quebraria o build por causa de
migração silenciosa de suite do Debian.

---

## Relação com o assunto `docker/` deste repositório

Este repositório já tem um curso de Docker **teórico e completo** em
[`../docker/`](../docker/00-MAPA.md). Os dois são complementares, não concorrentes:

| | [`docker/`](../docker/00-MAPA.md) | **`curso-docker/`** (este) |
|---|---|---|
| Foco | como funciona **por dentro** | como **fazer**, na prática |
| Cobre | namespaces, cgroups, OverlayFS, runtime, registries, teoria de agendamento | Dockerfile, Compose, volumes, redes, hardening, depuração |
| Estrutura | blocos A–E do preset | 10 módulos com exercício por módulo |
| Estudos de caso | app genérica | **seus três projetos reais** |

**Se você quer entender o mecanismo** (por que um container é isolado, o que o kernel faz),
vá para `docker/`. **Se você quer containerizar sua API hoje**, fique aqui.

Os módulos deste curso não repetem a teoria de baixo nível — quando ela importa, há um
apontamento.

---

## Roteiro de leitura

### Trilha completa, em ordem

| # | Módulo | Nível | O que você sai sabendo |
|---|---|---|---|
| 01 | [Fundamentos](01-fundamentos/conceito.md) · [exercício](01-fundamentos/exercicio.md) | iniciante | imagem vs container, camadas, registry, tags |
| 02 | [Diretivas](02-dockerfile/diretivas-completas.md) · [Cache](02-dockerfile/cache-de-camadas.md) · [Multi-stage](02-dockerfile/multi-stage-build.md) · [exercício](02-dockerfile/exercicio.md) | iniciante → avançado | escrever Dockerfile enxuto, rápido e seguro |
| 03 | [Anatomia do Compose](03-compose/anatomia-docker-compose.md) · [Variáveis](03-compose/variaveis-de-ambiente.md) · [exercício](03-compose/exercicio.md) | iniciante → intermediário | orquestrar múltiplos serviços numa máquina |
| 04 | [Bind mount vs volume](04-armazenamento/bind-mount-vs-volume.md) · [exercício](04-armazenamento/exercicio.md) | intermediário | onde os dados moram e como não perdê-los |
| 05 | [Modos de rede](05-redes/bridge-host-none.md) · [DNS interno](05-redes/dns-interno-entre-servicos.md) · [exercício](05-redes/exercicio.md) | intermediário | comunicação entre serviços e isolamento |
| 06 | [Não-root](06-seguranca/usuario-nao-root.md) · [Secrets](06-seguranca/secrets-e-variaveis-sensiveis.md) · [Checklist](06-seguranca/checklist-hardening.md) | intermediário → avançado | endurecer container e não vazar segredo |
| 07 | [Logs e exec](07-debugging/logs-e-exec.md) · [Troubleshooting](07-debugging/troubleshooting-comum.md) | todos | diagnosticar com método, não por tentativa |
| 08 | [**FastAPI + SQLAlchemy**](08-projeto-aplicado/dockerfile-fastapi-sqlalchemy.md) · [FlixARD](08-projeto-aplicado/compose-flixard.md) · [Financeiro](08-projeto-aplicado/compose-sistema-financeiro.md) | intermediário → avançado | aplicar tudo aos seus projetos reais |
| 09 | [Próximos passos](09-proximos-passos.md) | avançado | quando (e se) migrar para Swarm ou Kubernetes |
| — | [**GLOSSÁRIO**](GLOSSARIO.md) | — | todos os termos definidos |

### Atalhos por objetivo

| Se você quer... | Vá direto para |
|---|---|
| **Containerizar sua API FastAPI agora** | [módulo 08](08-projeto-aplicado/dockerfile-fastapi-sqlalchemy.md) + [projeto executável](08-projeto-aplicado/app-fastapi/) |
| Entender por que o build está lento | [cache de camadas](02-dockerfile/cache-de-camadas.md) |
| Resolver um erro específico | [troubleshooting](07-debugging/troubleshooting-comum.md) |
| Decidir bind mount ou volume | [módulo 04](04-armazenamento/bind-mount-vs-volume.md) |
| Parar de vazar senha | [secrets](06-seguranca/secrets-e-variaveis-sensiveis.md) |
| Auditar o que já está no ar | [checklist](06-seguranca/checklist-hardening.md) |
| Saber se precisa de Kubernetes | [módulo 09](09-proximos-passos.md) |

---

## Projeto executável

[`08-projeto-aplicado/app-fastapi/`](08-projeto-aplicado/app-fastapi/) — API
FastAPI + SQLAlchemy async pequena mas **inteira**: config por ambiente,
tratamento de erro, `/health` que testa o banco, testes, Dockerfile multi-stage
não-root e compose com Postgres.

```bash
cd 08-projeto-aplicado/app-fastapi
docker compose up --build
curl http://localhost:8000/health
```

Sem Docker:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q                                          # 4 passed
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Também executáveis:
[`flixard/compose.yaml`](08-projeto-aplicado/flixard/compose.yaml) ·
[`sistema-financeiro/compose.yaml`](08-projeto-aplicado/sistema-financeiro/compose.yaml)

---

## Ferramentas de validação (instalam sem sudo)

Úteis mesmo sem daemon — foram como este curso se verificou:

```bash
# Plugin do Compose
mkdir -p ~/.docker/cli-plugins
curl -fsSL -o ~/.docker/cli-plugins/docker-compose \
  https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64
chmod +x ~/.docker/cli-plugins/docker-compose

# hadolint — linter de Dockerfile
mkdir -p ~/.local/bin
curl -fsSL -o ~/.local/bin/hadolint \
  https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64
chmod +x ~/.local/bin/hadolint
```

```bash
hadolint Dockerfile              # audita boas práticas
docker compose config --quiet    # valida YAML sem daemon
```

Ponha os dois no seu CI.

---

## Para liberar o daemon nesta máquina

O curso foi escrito sem acesso ao daemon. Para rodar os exemplos:

```bash
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker                    # ou logout/login
docker run --rm hello-world
```

**Antes de rodar:** pertencer ao grupo `docker` **equivale a ter root** na
máquina — quem está no grupo pode montar `/` num container. Em homelab pessoal é
o padrão aceito, mas é uma decisão consciente de segurança, não uma formalidade.
A alternativa mais segura é [rootless mode ou
Podman](06-seguranca/usuario-nao-root.md).

---

## Convenções

- **Nível** e **data de verificação** no topo de cada arquivo.
- Toda afirmação verificada traz o **comando e a saída obtida**.
- O que **não** foi executado está marcado explicitamente.
- Opinião profissional é separada de consenso, sempre que houver risco de
  confusão.
- Cada arquivo termina com **autoteste** (5 a 9 perguntas).
- Exercícios trazem enunciado e **solução comentada** no mesmo arquivo, após um
  separador — tente antes de rolar.
