# 02 · Pré-requisitos

`Nível: iniciante` · `Atualizado em: 14/08/2026`

---

## 1. Conhecimento

### Indispensável

| Você precisa saber | Por quê | Onde aprender |
|---|---|---|
| **Usar um terminal**: `cd`, `ls`, `cat`, editar arquivo, executar comando | tudo neste curso passa por linha de comando | [Terminal Linux — Diolinux (YouTube, PT)](https://www.youtube.com/results?search_query=curso+terminal+linux+diolinux) · `man bash` |
| **Git básico**: `add`, `commit`, `push`, `.gitignore` | o eixo do problema é "o que vai e o que não vai para o repositório" | [Git — Curso em Vídeo (PT, grátis)](https://www.cursoemvideo.com/curso/git-e-github/) |
| **Rodar um programa** na sua linguagem: `node app.js`, `python app.py`, `php app.php` | é o que produz o processo que recebe as variáveis | qualquer curso introdutório da linguagem |
| **O que é um processo** (um programa em execução) | variável de ambiente é propriedade de um processo, não do sistema | [10-fundamentos.md](10-fundamentos.md) deste curso cobre o necessário |

### Ajuda muito (mas dá para começar sem)

| Assunto | Por quê | Onde aprender |
|---|---|---|
| **Docker** | metade das entregas modernas passa por contêiner | [`docker/`](../docker/00-MAPA.md) nesta pasta |
| **Permissões de arquivo Unix** (`chmod`, `chown`, `umask`) | a diferença entre um `.env` seguro e um exposto no servidor é literalmente `chmod 600` | [03-instalacao.md §7](03-instalacao.md) |
| **Cliente/servidor e HTTP** | entender por que "no navegador não existe segredo" | [`apis/`](../apis/00-MAPA.md) nesta pasta |
| **Criptografia simétrica vs. assimétrica** | necessário para o bloco de cofres e criptografia de envelope | [60-teoria-avancada.md](60-teoria-avancada.md) reintroduz do zero |
| **systemd** | a forma padrão de rodar serviço em Linux desde ~2015 | [30-entrega-em-producao.md](30-entrega-em-producao.md) |
| **CI/CD** (GitHub Actions ou similar) | é onde os segredos entram no processo de entrega | [35-ci-cd.md](35-ci-cd.md) |

### O que você **não** precisa saber

- Criptografia avançada. O curso ensina o necessário.
- Kubernetes. Há um capítulo, mas ele é opcional e marcado como tal.
- Uma linguagem específica. O curso cobre Node, PHP e Python lado a lado.

---

## 2. Ambiente

### Mínimo para acompanhar o Bloco A (01–07)

| Item | Mínimo | Recomendado | Observação |
|---|---|---|---|
| Sistema operacional | Windows 10, macOS 12, ou qualquer Linux | Linux ou macOS; no Windows, **WSL2** | o modelo de variáveis de ambiente do Windows nativo difere; ver [03 §5](03-instalacao.md) |
| Terminal | qualquer | `bash` ou `zsh` | PowerShell também é coberto |
| Git | 2.30+ | 2.40+ | `git --version` |
| Editor | qualquer | VS Code + extensão DotENV | |
| Espaço em disco | 500 MB | 5 GB (com Docker) | |
| Memória | 2 GB | 8 GB | Docker/Kubernetes local pede mais |
| Conexão | necessária para instalar | | o projeto-modelo roda offline depois de instalado |

### Por trilha

| Se você vai seguir a trilha… | Instale |
|---|---|
| **Node** | Node.js 22 LTS ou 24 LTS |
| **PHP** | PHP 8.2+ e Composer 2 |
| **Python** | Python 3.11+ e `pip` |
| **Contêineres** | Docker Engine 25+ ou Podman 5+ |
| **Kubernetes (opcional)** | `kind` ou `minikube` + `kubectl` |
| **Cofres (opcional)** | Vault/OpenBao binário, ou conta em AWS/GCP/Azure |

Tudo isso está com passo a passo em [03-instalacao.md](03-instalacao.md).

### Contas em serviços

**Nenhuma é obrigatória** para os blocos A, B e C. Para o bloco de cofres na nuvem
você precisará de uma conta em nuvem — e **todas exigem cartão de crédito mesmo no
plano gratuito** (AWS, GCP, Azure). Alternativa sem cartão: rodar **OpenBao** ou
**Infisical** localmente em contêiner, o que o curso cobre. Ver
[80-custos-e-licencas.md](80-custos-e-licencas.md).

---

## 3. Tempo realista

Sendo honesto — estes números pressupõem estudo com as mãos no teclado, não leitura passiva.

| Objetivo | Tempo | O que você consegue fazer |
|---|---|---|
| **Parar de errar** — entender o problema e nunca mais commitar um `.env` | **2 a 3 horas** | ler 01, 10, 75 e configurar `.gitignore` + `gitleaks` |
| **Entregar direito um projeto pequeno** | **1 a 2 dias** | blocos A e o capítulo da sua linguagem + [30](30-entrega-em-producao.md); sabe subir com systemd ou Docker com segredos fora do repositório |
| **Nível profissional de equipe** | **2 a 4 semanas** de uso real | CI/CD com segredos, rotação, detecção de vazamento, resposta a incidente, cofre gerenciado |
| **Nível arquiteto/segurança** | **3 a 6 meses** | modelo de ameaça próprio, identidade de carga de trabalho, criptografia de envelope, auditoria, conformidade |
| **Fronteira de pesquisa** | **1 ano+** | atestação remota, enclaves, SPIFFE em escala, criptografia sem segredo persistente |

**Onde as pessoas travam** (por experiência): não é a teoria. É a etapa
"o segredo precisa chegar ao servidor, e alguém precisa colocá-lo lá pela primeira vez"
— o **problema do segredo zero**, tratado em [60-teoria-avancada.md §4](60-teoria-avancada.md).
Todo mundo esbarra nele e a maioria não sabe que tem nome.

---

## 4. Rota de resgate — o que fazer se faltar um pré-requisito

| Falta | Rota curta (hoje) | Rota completa |
|---|---|---|
| **Terminal** | faça só o [04-como-comecar.md](04-como-comecar.md); ele mostra cada comando literal | curso de Linux básico, 6–10 h |
| **Git** | crie um `.gitignore` com uma linha `.env` e siga | curso de Git, 8–12 h |
| **Docker** | pule os capítulos de contêiner; use a trilha `systemd` | [`docker/`](../docker/00-MAPA.md), 2–3 dias |
| **Nuvem / cartão de crédito** | use OpenBao local em contêiner (grátis, sem conta) | criar conta depois |
| **Criptografia** | leia [60 §1](60-teoria-avancada.md), que reintroduz do zero | *Serious Cryptography* (ver [90](90-bibliografia.md)) |
| **Nenhum servidor para praticar** | use `docker compose` local, que simula o servidor | VPS de US$ 4–6/mês, ou camada gratuita da Oracle Cloud |
| **A empresa não deixa instalar nada** | use GitHub Codespaces ou um Playground online — ver [03 §11](03-instalacao.md) | — |

---

## 5. Autoteste — você está pronto?

Responda antes de seguir. Se errar 3 ou mais, volte aos pré-requisitos.

1. Abra um terminal e mostre o valor da variável `HOME`. Qual comando?
2. O que faz uma linha `.env` dentro de um arquivo `.gitignore`?
3. Qual a diferença entre `git rm .env` e `git rm --cached .env`?
4. O que significa `chmod 600 arquivo`?
5. Um programa em execução é a mesma coisa que o arquivo do programa em disco?
6. Se você digita `export X=1` no terminal e abre outro terminal, `X` existe lá?

<details>
<summary>Respostas</summary>

1. `echo $HOME` (Linux/macOS) ou `echo $env:HOME` / `$env:USERPROFILE` (PowerShell).
2. Faz o Git ignorar arquivos chamados `.env` **que ainda não estão rastreados**.
   Se o arquivo já foi commitado, o `.gitignore` não tem efeito sobre ele.
3. `git rm` apaga do disco **e** do índice; `git rm --cached` só do índice —
   o arquivo continua no seu disco, e é o que você quer para um `.env`.
4. Dono pode ler e escrever; grupo e outros não podem nada.
5. Não. O arquivo em disco é o **programa**; a instância em execução é o **processo**.
   Variáveis de ambiente pertencem ao processo.
6. Não. Cada terminal é um processo com sua própria cópia do ambiente.
   Essa é a resposta mais importante da lista — se você errou esta, leia
   [10-fundamentos.md](10-fundamentos.md) com atenção.

</details>

---

**Próximo:** [03-instalacao.md](03-instalacao.md) · Voltar ao [mapa](00-MAPA.md)
