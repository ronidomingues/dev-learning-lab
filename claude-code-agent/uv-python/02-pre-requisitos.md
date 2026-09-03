# 02 · Pré-requisitos

> **Nível:** iniciante · **Atualizado em:** 31/08/2026

---

## 1. Conhecimento

### Indispensável

| O que | Por que | Onde aprender |
|---|---|---|
| **Abrir e usar um terminal** | o uv é uma ferramenta de linha de comando; não existe interface gráfica oficial | [Linux Journey — Command Line](https://linuxjourney.com/lesson/the-shell) · no Windows, use o **Terminal do Windows** com PowerShell |
| **Navegar em pastas pelo terminal** (`cd`, `ls`/`dir`, `pwd`) | todo comando do uv age sobre "o projeto na pasta atual" | mesma fonte acima |
| **Editar um arquivo de texto** e salvá-lo | você vai editar `pyproject.toml` | qualquer editor; recomendo VS Code |
| **Python básico**: rodar um `.py`, `import`, funções | o uv gerencia Python; ele não ensina Python | [Curso em Vídeo — Python 3 (Gustavo Guanabara)](https://www.youtube.com/playlist?list=PLHz_AreHm4dlKP6QQCekuIPky1CiwmdI6), gratuito, PT-BR |

> **Se você não sabe Python nenhum:** aprenda a rodar um script primeiro. O uv fica
> muito mais fácil depois que a frase "executar um arquivo `.py`" já significa algo
> concreto para você. Duas semanas de Python básico bastam.

### Ajuda muito (mas não bloqueia)

| O que | Por que ajuda |
|---|---|
| **Git básico** | o `uv.lock` deve ser versionado; o `uv init` já cria um repositório |
| Noção de **variáveis de ambiente** e `PATH` | 80% dos problemas de instalação são de `PATH` — ver [variaveis-de-ambiente-e-segredos](../variaveis-de-ambiente-e-segredos/00-MAPA.md) nesta pasta |
| Ter sofrido com `pip` e ambiente virtual antes | você entende o problema que o uv resolve, e valoriza a solução |
| **TOML** (formato de configuração) | `pyproject.toml` e `uv.toml` são TOML; leva 10 minutos: [toml.io](https://toml.io/pt/v1.0.0) |
| **Docker** | para o capítulo de CI/produção — ver [docker](../docker/00-MAPA.md) nesta pasta |
| **Semântica de versões** (SemVer) | para entender `>=`, `~=`, `==` nas dependências. Explicado em [10-fundamentos.md](10-fundamentos.md) |

### Explicitamente **não** é pré-requisito

- Saber Rust (o uv é escrito em Rust; isso é irrelevante para usá-lo).
- Já ter usado Poetry, Pipenv ou conda.
- Ter Python instalado. **O uv instala o Python por você.** Este é um ponto importante
  e contraintuitivo: você pode instalar o uv em uma máquina sem nenhum Python e sair
  rodando código Python em 30 segundos.

---

## 2. Ambiente

### Sistemas operacionais suportados

| SO | Suporte | Observação |
|---|---|---|
| **Linux x86-64 (glibc)** | ✅ primeira classe | Ubuntu 20.04+, Debian 11+, Fedora 38+, RHEL 8+ |
| **Linux ARM64** | ✅ primeira classe | Raspberry Pi 4/5 com SO 64-bit, servidores Graviton |
| **Linux musl (Alpine)** | ✅ | binário `musl` específico; Python gerenciado tem builds musl |
| **macOS 12+ (Intel e Apple Silicon)** | ✅ primeira classe | binários universais separados por arquitetura |
| **Windows 10/11 x86-64** | ✅ primeira classe | nativo, sem precisar de WSL |
| **Windows ARM64** | ✅ | binário próprio |
| Linux s390x, ppc64le, loongarch64 | 🟡 resolução multiplataforma suportada desde 0.12.7 | binários nem sempre disponíveis para todos |

### Hardware — requisitos reais

| Recurso | Mínimo | Confortável | Por quê |
|---|---|---|---|
| **Disco** | ~40 MB para o binário do uv | **5 GB livres** | o cache (`~/.cache/uv`) cresce; nesta máquina, após um dia de testes, ele estava com **217 MB**. Cada Python gerenciado ocupa ~100–150 MB extraídos (o download é ~32–35 MB) |
| **RAM** | 512 MB | 2 GB | a resolução de dependências é feita em memória; projetos com centenas de pacotes e muitos "forks" de plataforma consomem mais |
| **Rede** | qualquer | — | a primeira instalação baixa tudo; depois o cache local resolve |
| **CPU** | qualquer | multi-core | o uv paraleliza download, descompactação e instalação; mais núcleos ajudam de verdade |

### Contas e licenças

**Nenhuma conta é necessária.** O uv é gratuito, código aberto, licenciado sob
MIT **ou** Apache-2.0 (à sua escolha). Não pede cadastro, não pede cartão, não tem
plano pago, não tem telemetria obrigatória. Detalhes e a pergunta "quem paga a conta?"
estão em [80-custos-e-licencas.md](80-custos-e-licencas.md).

Você só vai precisar de conta se for **publicar** um pacote — aí precisa de conta no
[PyPI](https://pypi.org) (gratuita) — ou se usar um índice privado da sua empresa.

---

## 3. Tempo realista de estudo

Sem otimismo de propaganda. Assume alguém que já sabe Python básico e usa terminal.

| Nível | O que você consegue fazer | Tempo | Arquivos deste curso |
|---|---|---|---|
| **Primeiro contato** | instalar, criar projeto, adicionar dependência, rodar | **30–60 minutos** | 03, 04 |
| **Uso diário produtivo** | substituir pip+venv+pipx no seu dia a dia sem pensar | **1 semana de uso real** (não de leitura) | 05, 06, 07 |
| **Confortável** | workspaces, grupos de dependências, extras, CI, Docker, publicar pacote | **3 a 5 semanas** | 10–19 |
| **Avançado** | depurar resolução que falha, `--resolution lowest`, conflitos, overrides, índices privados, ambientes exóticos (CUDA, ARM, musl) | **2 a 4 meses** de exposição a problemas reais | 13, 21, 75 |
| **Nível pesquisa** | entender e discutir o algoritmo de resolução, provar propriedades do lockfile universal, contribuir com o projeto | **6 meses a 1 ano**, e requer conhecer teoria de SAT/PubGrub | 60, 65 |

> **Honestidade:** o "uso diário produtivo" é rápido *de propósito* — o uv foi desenhado
> para isso. O tempo longo está nos **casos de borda**: quando a resolução falha, quando
> um pacote não tem wheel para a sua plataforma, quando a empresa tem proxy com
> certificado próprio. É lá que se separa quem usa de quem entende.

---

## 4. O que instalar antes (resumo — detalhes no 03)

Ordem recomendada:

1. **Um terminal decente** — no Windows, o *Windows Terminal* (já vem no Windows 11).
2. **O uv** — é o passo 1 de verdade; ele traz o resto.
3. **Um editor** — VS Code + extensão *Python* da Microsoft (opcional mas recomendado).
4. **Git** — opcional para os primeiros passos, necessário para trabalhar em equipe.
5. **Python** — ❌ **não instale**. Deixe o uv fazer isso. Se já tiver, ele reaproveita.

Todos os passos, por sistema operacional, com verificação: [03-instalacao.md](03-instalacao.md).

---

## 5. Rota de resgate — o que fazer se faltar um pré-requisito

| Falta | Rota de resgate |
|---|---|
| **Não sei usar o terminal** | Faça só isto: abra o terminal, digite `cd ~`, `ls` (ou `dir`), `mkdir teste`, `cd teste`, `pwd`. Se esses cinco funcionaram, você tem o suficiente para começar. |
| **Não tenho permissão de administrador na máquina** | O instalador oficial do uv **não precisa de sudo/admin** — ele instala em `~/.local/bin`. Este é um dos pontos fortes dele. Siga o método "instalador oficial" no 03. |
| **Não posso instalar nada (máquina bloqueada, curso, laboratório)** | Use uma alternativa sem instalação: GitHub Codespaces ou um container. A seção *"Alternativa sem instalar nada"* do [03-instalacao.md](03-instalacao.md#alternativa-sem-instalar-nada) tem o caminho completo. |
| **Não sei Python** | Faça 2 semanas do Curso em Vídeo (link acima) até saber criar um `.py`, usar `def` e `import`. Volte depois. Não tente aprender os dois ao mesmo tempo. |
| **Estou atrás de proxy corporativo e nada baixa** | Seção *"Rede corporativa"* do [03-instalacao.md](03-instalacao.md#rede-corporativa-proxy-certificado-e-índice-espelhado). Configure `HTTPS_PROXY`, `SSL_CERT_FILE` ou `UV_NATIVE_TLS`. |
| **Uso conda/Anaconda e não posso sair** | Não precisa sair. O uv convive: use `uv pip` dentro do ambiente conda ativo. Ver [20-migracao](20-migracao-de-pip-poetry-conda.md). |
| **Meu projeto usa Poetry e a equipe não quer migrar** | Também não precisa. O uv lê `pyproject.toml` padrão (PEP 621); dá para usar `uvx` e `uv pip` sem tocar no fluxo do time. Migração incremental no arquivo 20. |
| **Minha máquina é muito antiga / pouco disco** | Configure `UV_CACHE_DIR` para um disco externo e rode `uv cache prune` periodicamente. O uv funciona bem em máquinas modestas — foi testado até em Raspberry Pi. |

---

## 6. Checklist antes de ir para o 03

- [ ] Sei abrir um terminal e sei em que pasta estou (`pwd`).
- [ ] Sei criar e apagar uma pasta pelo terminal.
- [ ] Sei o que é um arquivo `.py` e como um `import` funciona.
- [ ] Tenho pelo menos 5 GB livres em disco.
- [ ] Sei se minha máquina é Linux, macOS (Intel ou Apple Silicon) ou Windows.
- [ ] Se estou em rede corporativa, sei se existe proxy (ou sei a quem perguntar).

Marcou todos? Vá para [03-instalacao.md](03-instalacao.md).

---

## Autoteste

1. Preciso ter Python instalado antes de instalar o uv? Justifique.
2. Qual é o único pré-requisito de conhecimento que realmente bloqueia o começo?
3. Quanto tempo é realista até "uso diário produtivo" — e por que o número é baixo?
4. Onde fica e quanto ocupa o cache do uv? Como limpá-lo?
5. Quais licenças o uv usa, e o que isso implica para uso comercial?
6. Você está numa máquina sem permissão de administrador. Ainda dá para instalar o uv? Como?
7. Qual é a rota de resgate para quem não pode instalar absolutamente nada?
8. Por que o tempo até o nível "avançado" é medido em meses de *exposição a problemas*
   e não em horas de leitura?

---

**Próximo:** [03-instalacao.md](03-instalacao.md)
