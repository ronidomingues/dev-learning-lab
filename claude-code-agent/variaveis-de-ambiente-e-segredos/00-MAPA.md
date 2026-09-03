# Variáveis de ambiente e segredos — mapa do curso

`Atualizado em: 14/08/2026`

> **A pergunta que originou este curso:**
> *"No desenvolvimento criamos o `.env`, que guarda senhas e chaves secretas.
> Depois do fim do desenvolvimento, quando vai para o cliente, quando finalmente vai
> ser usado o sistema — em Node, em PHP, em Python e em outras — como se faz com esse
> arquivo?"*

---

## A resposta, em três frases

1. **O arquivo `.env` não vai.** Ele fica na sua máquina, no `.gitignore`, e morre ali.
2. **O conteúdo vai** — por um canal escolhido conforme onde o sistema roda, sempre de
   forma que o valor **já esteja no ambiente** quando o processo iniciar.
3. **O código não muda.** Ele lê `process.env` / `os.environ` / `getenv()` e nunca
   sabe de onde veio. É por isso que o mesmo artefato roda em todo lugar.

**Se você só tem 20 minutos**, leia [01-introducao-leigo.md](01-introducao-leigo.md)
e [30-entrega-em-producao.md](30-entrega-em-producao.md). O resto é o porquê.

---

## Roteiros de leitura

### 🚀 Roteiro rápido — "só quero a resposta" (1 h)
```
01 → 04 → 30 → 75
```
Introdução → primeiro experimento → entrega em produção → armadilhas.

### 🎯 Roteiro prático — "vou aplicar no meu projeto" (1 dia)
```
01 → 03 → 04 → 06 → 07-projeto-modelo → o capítulo da sua linguagem (15/16/17) → 30 → 50
```

### 📚 Roteiro completo — do zero ao doutorado (2 a 4 semanas)
```
Bloco A (01→07) → Bloco B (10→65) → Bloco C (70→75) → Bloco D (80→85) → Bloco E (90→95)
```

### 🏢 Roteiro por papel

| Você é… | Leia |
|---|---|
| **Dev que entrega para cliente** | 01, 04, 06, **55**, 30, 50 |
| **Dev front-end** | 01, **20**, 35 |
| **Dev PHP/Laravel** | 01, 04, **16**, 30, 50 |
| **Dev Python/Django** | 01, 04, **17**, 30 |
| **Dev Node/Next** | 01, 04, **15**, **20**, 30 |
| **DevOps / SRE** | 10, 30, 35, 40, 45, 50, 60 |
| **Segurança** | 10, 45, 50, **60**, 65, 75 |
| **Gestor / arquiteto** | 01, 30 (§10), 40 (§4), **80** |

---

## Estrutura

### Bloco A · Porta de entrada (01–09)

| Arquivo | O que traz | Nível |
|---|---|---|
| [01-introducao-leigo.md](01-introducao-leigo.md) | o que é, sem jargão; a analogia do crachá e do cofre; os quatro erros que todo mundo comete | iniciante |
| [02-pre-requisitos.md](02-pre-requisitos.md) | o que saber antes, tempo realista, rota de resgate | iniciante |
| [03-instalacao.md](03-instalacao.md) | manual de campo: Git, Node, PHP, Python, Docker, direnv, SOPS+age, gitleaks, OpenBao — nos três SOs, com PATH, permissões, proxy, desinstalação e tabela de erros literais | iniciante |
| [04-como-comecar.md](04-como-comecar.md) | do zero ao primeiro resultado; **o experimento de precedência que responde a pergunta** | iniciante |
| [05-manual-de-uso.md](05-manual-de-uso.md) | referência consultável por tarefa: shell, `.env`, cada linguagem, systemd, Docker, K8s, CI, SOPS, Vault, gitleaks | iniciante/interm. |
| [06-exemplos.md](06-exemplos.md) | **15 receitas completas**, do `.gitignore` ao instalador para o cliente | iniciante/avançado |
| [07-projeto-modelo/](07-projeto-modelo/README.md) | ⭐ **API executável, zero dependências, 43 testes**, com systemd, Docker, instalador e equivalentes em Python e PHP | todos |

### Bloco B · Núcleo (10–69)

| Arquivo | O que traz | Nível |
|---|---|---|
| [10-fundamentos.md](10-fundamentos.md) | `execve`, `environ`, memória, `/proc/PID/environ`, precedência, limites, o que é "segredo" formalmente | intermediário |
| [11-historia.md](11-historia.md) | de 1979 ao OpenBao; por que o `.env` nasceu para desenvolvimento e virou outra coisa | intermediário |
| [12-formato-dotenv.md](12-formato-dotenv.md) | **o padrão que não existe** — divergências de parsing **medidas** entre Node, dotenv e python-dotenv | intermediário |
| [15-node.md](15-node.md) | `--env-file` vs. `dotenv`, ordem de import, tipos, Next/Nest/Express, segredo em memória | intermediário |
| [16-php.md](16-php.md) | **`getenv()` ≠ `$_ENV`** (medido), modelo por requisição, Laravel `config:cache`, PHP-FPM, hospedagem compartilhada | intermediário |
| [17-python.md](17-python.md) | `os.environ`, `python-dotenv`, `pydantic-settings` com `SecretStr`, Django, FastAPI | intermediário |
| [18-outras-plataformas.md](18-outras-plataformas.md) | Java/Spring, .NET, Go, Ruby/Rails, Rust — e a "URL única" | intermediário |
| [20-frontend-e-build-time.md](20-frontend-e-build-time.md) | **por que não existe segredo no navegador**; `NEXT_PUBLIC_`, artefato congelado, o que fazer no lugar | intermediário |
| [30-entrega-em-producao.md](30-entrega-em-producao.md) | ⭐ **a resposta direta, por cenário**: systemd, `LoadCredential`, Docker, Compose, K8s, PaaS, serverless, Windows | interm./avançado |
| [35-ci-cd.md](35-ci-cd.md) | GitHub Actions, GitLab, OIDC, `pull_request_target`, varredura no pipeline | interm./avançado |
| [40-cofres-de-segredos.md](40-cofres-de-segredos.md) | credencial dinâmica, panorama de 2026, SOPS, Vault/OpenBao, **quando NÃO usar cofre** | avançado |
| [45-rotacao-e-ciclo-de-vida.md](45-rotacao-e-ciclo-de-vida.md) | gerar, distribuir, monitorar, **rotação com sobreposição**, revogar, inventário | avançado |
| [50-vazamentos-e-resposta.md](50-vazamentos-e-resposta.md) | prevenir em 4 camadas, detectar, e **a resposta das duas primeiras horas** | interm./avançado |
| [55-entrega-ao-cliente.md](55-entrega-ao-cliente.md) | ⭐ on-premise: de quem é o segredo, instalador, migração de configuração, suporte sem pedir senha | avançado |
| [60-teoria-avancada.md](60-teoria-avancada.md) | criptografia do zero, modelo de ameaça, envelope, **segredo zero**, SPIFFE, limites teóricos | pesquisa |
| [65-estado-da-arte.md](65-estado-da-arte.md) | agosto de 2026: tendências, disputas em aberto, IA e segredos, apostas para 2030 | pesquisa |

### Bloco C · Prática e erros (70–79)

| Arquivo | O que traz |
|---|---|
| [70-pratica.md](70-pratica.md) | **12 laboratórios** com verificação — 7 deles executados e conferidos nesta máquina |
| [75-armadilhas.md](75-armadilhas.md) | **30 armadilhas + 10 mitos** + os 5 erros que mais custam caro |

### Bloco D · Economia e ecossistema (80–89)

| Arquivo | O que traz |
|---|---|
| [80-custos-e-licencas.md](80-custos-e-licencas.md) | preços de 14/08/2026 em USD e BRL, licenças (BUSL, AGPL, Docker Desktop), custos ocultos |
| [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) | cursos gratuitos em PT/EN/FR pesquisados na web, e a verdade sobre certificados gratuitos |

### Bloco E · Fontes (90–99)

| Arquivo | O que traz |
|---|---|
| [90-bibliografia.md](90-bibliografia.md) | livros comentados, com o que é legalmente gratuito |
| [95-referencias.md](95-referencias.md) | specs, docs oficiais, código-fonte, papers, CVEs históricos |
| [GLOSSARIO.md](GLOSSARIO.md) | ~110 termos definidos |

---

## O que você saberá ao final

- Explicar, a partir de `execve`, **por que** variável de ambiente funciona assim.
- Entregar configuração em **Node, PHP, Python, Java, .NET, Go, Ruby e Rust**.
- Fazer isso em **systemd, Docker, Compose, Kubernetes, PaaS, serverless, hospedagem
  compartilhada e na máquina do cliente**.
- Escrever um módulo de configuração que **falha rápido** e não vaza no log.
- Saber por que `NEXT_PUBLIC_` nunca é segredo — e que isso é um **teorema**, não um conselho.
- Escolher (ou **não** escolher) um cofre, com os preços na mão.
- **Rotacionar sem derrubar o sistema.**
- Responder a um vazamento na ordem certa, nas duas primeiras horas.
- Discutir criptografia de envelope, segredo zero, SPIFFE e os limites teóricos.

---

## Status

| Bloco | Status | Observação |
|---|---|---|
| **A · Porta de entrada** | ✅ completo | 03 cobre 9 tecnologias em 3 SOs; 06 tem 15 exemplos; projeto-modelo com 43 testes aprovados |
| **B · Núcleo** | ✅ completo | 16 arquivos, do `execve` ao estado da arte de ago/2026 |
| **C · Prática e erros** | ✅ completo | 12 laboratórios; 30 armadilhas e 10 mitos |
| **D · Economia e ecossistema** | ✅ completo | preços com data e câmbio; cursos PT/EN/FR pesquisados na web |
| **E · Fontes** | ✅ completo | bibliografia, referências primárias, glossário |

### O que foi executado e verificado nesta máquina

**Ambiente:** Ubuntu 22.04.5 LTS · Node v24.18.0 · npm 12.0.1 · Python 3.10.12 ·
PHP 8.1.2 · Docker 29.1.3 (sem permissão de socket) · git 2.34.1 — em **14/08/2026**.

- ✅ **Projeto-modelo: 43 testes, 43 aprovados.** Servidor executado e exercitado com
  `curl` (rotas `/health`, `/recados`, `/config`, `/metrics`).
- ✅ **Precedência ambiente vs. `.env`** — medida e travada por teste em processo real.
- ✅ **Divergências de parsing** entre Node `--env-file`, `dotenv` 17.4.2 e
  `python-dotenv` 1.2.3 — tabela do [12](12-formato-dotenv.md) é medição, não suposição.
- ✅ **`getenv()` vs. `$_ENV` em PHP** — `variables_order = GPCS` confirmado, `$_ENV` vazio.
- ✅ **Padrão `_FILE`** ponta a ponta em Node, Python e PHP, com verificação de que o
  segredo **não** aparece em `/proc/<pid>/environ`.
- ✅ **Simulação de vazamento e `git filter-repo`** — laboratório 11 executado inteiro.
- ✅ `ARG_MAX`, herança de ambiente pai/filho, `setenv` não aparecendo em `/proc`.

### O que **não** foi executado (declarado por honestidade)

- ❌ `docker build` e `docker compose up` — o usuário desta máquina não está no grupo
  `docker` (`permission denied ... /var/run/docker.sock`). Labs 7, 10, 12 e o
  `Dockerfile`/`compose.yaml` do projeto-modelo **não** foram construídos.
- ❌ `deploy/install.sh` e a unit systemd — exigem `root` e alteram `/etc` e `/opt`.
- ❌ SOPS, age, gitleaks, OpenBao, Composer, `phpdotenv`, `pydantic-settings` — não
  instalados nesta máquina. Conteúdo vindo da documentação oficial, com a data da consulta.
- ❌ Instalação em macOS e Windows.
- ❌ Exemplos de Java, .NET, Go, Ruby e Rust do [18](18-outras-plataformas.md).

### Manutenção sugerida

| Arquivo | Reavaliar a cada |
|---|---|
| [65-estado-da-arte.md](65-estado-da-arte.md) | 6 meses |
| [80-custos-e-licencas.md](80-custos-e-licencas.md) | 6 meses (preços e câmbio) |
| [03-instalacao.md](03-instalacao.md) | 6 meses (versões e comandos) |
| [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) | 12 meses (links expiram) |
| Demais | quando algo mudar de forma relevante |

---

**Voltar ao [índice geral](../INDICE.md)**
