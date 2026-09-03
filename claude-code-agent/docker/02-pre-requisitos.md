# 02 · Pré-requisitos

`Nível: iniciante` · `Última atualização: 11/08/2026`

O que você precisa **saber**, **ter** e **decidir** antes de abrir o
[03-instalacao.md](03-instalacao.md).

---

## 1. Conhecimento

### Indispensável

| Pré-requisito | Por que é indispensável | Onde aprender |
|---|---|---|
| **Usar um terminal** — abrir, navegar (`cd`, `ls`, `pwd`), ler saída de erro | O Docker é essencialmente uma CLI. Sem terminal, não há Docker. | [Linux Journey — Command Line](https://linuxjourney.com/lesson/the-shell) · [Curso em Vídeo — Linux (PT)](https://www.youtube.com/playlist?list=PLHz_AreHm4dlKP6QQCekuIPky1CiwmdI6) |
| **Caminhos de arquivo** — absoluto vs. relativo, `.`, `..`, `~` | Volumes, `COPY` e *build context* são todos sobre caminhos. Erro de caminho é o erro nº 1. | Mesma fonte acima |
| **Noção de processo** — o que é um programa em execução, o que é PID | Um container **é** um processo. Sem esse modelo mental, tudo vira mágica. | [10-fundamentos.md](10-fundamentos.md) cobre o necessário |
| **Noção de porta de rede** — o que é `localhost:8080`, cliente e servidor | Publicar porta (`-p`) é metade do uso cotidiano. | [16-redes.md](16-redes.md) cobre o necessário |
| **Editar um arquivo de texto** e salvar | Dockerfile e Compose são arquivos de texto. | Qualquer editor: VS Code, nano, vim |

### Ajuda muito (mas dá para começar sem)

| Pré-requisito | Onde isso aparece | Rota de resgate |
|---|---|---|
| **Git** | Você vai versionar Dockerfile e Compose junto do código; CI/CD parte daí | Aprenda o mínimo: `clone`, `add`, `commit`, `push` |
| **YAML** | `compose.yaml` é YAML. Indentação com espaços, nunca TAB | 20 minutos em [learnxinyminutes.com/yaml](https://learnxinyminutes.com/docs/yaml/) resolvem |
| **Alguma linguagem de programação** | Para construir sua própria imagem em vez de só usar as prontas | Não bloqueia: você pode passar semanas só rodando imagens de terceiros |
| **Fundamentos de Linux** — permissões, UID/GID, `/etc`, `/var` | O container roda Linux mesmo que seu desktop seja Windows. Problema de permissão em volume é 100% sobre UID/GID | [Linux Journey](https://linuxjourney.com) · aparece explicado em [15-armazenamento-e-volumes.md](15-armazenamento-e-volumes.md) |
| **Redes: DNS, NAT, sub-rede** | Bridge networks, resolução de nome entre serviços | Explicado do zero em [16-redes.md](16-redes.md) |
| **HTTP e APIs** | A maioria dos exemplos sobe um serviço web | Não bloqueia |

### O que **não** é pré-requisito (apesar do que dizem)

- **Kubernetes.** É o contrário: containers vêm antes. Quem começa por Kubernetes aprende os
  dois pela metade.
- **Ser administrador de sistemas.** Docker foi feito para desenvolvedores.
- **Saber compilar kernel, escrever em Go, entender syscalls.** Isso é o Bloco B avançado, não
  a porta de entrada.

---

## 2. Ambiente

### Hardware — mínimo real, não o do folheto

| Recurso | Mínimo funcional | Confortável | Observação |
|---|---|---|---|
| **CPU** | 2 núcleos, x86-64 ou ARM64 | 4+ núcleos | Build de imagem é o que mais consome |
| **RAM** | 4 GB (Linux) · 8 GB (macOS/Windows) | 16 GB | Em macOS/Windows a VM do Docker reserva RAM fixa |
| **Disco livre** | 20 GB | 60 GB+ | Imagens acumulam rápido. É o recurso que acaba primeiro |
| **Arquitetura** | x86-64 (amd64) ou ARM64 (aarch64) | — | Apple Silicon é ARM64: nem toda imagem tem build ARM64 |
| **Virtualização** | habilitada na BIOS/UEFI | — | Obrigatória em Windows e macOS; **não** é necessária em Linux |

> **Cicatriz de campo:** disco cheio por imagens e volumes órfãos é, disparado, o incidente
> mais comum em máquina de desenvolvedor. Reserve espaço e conheça `docker system df`
> antes de precisar dele às 3 da manhã.

### Sistema operacional

| SO | Situação | Recomendação |
|---|---|---|
| **Linux** (kernel ≥ 5.10, recomendado ≥ 6.1) | Ambiente nativo. Sem VM no meio, performance total | Melhor experiência. É onde containers realmente rodam |
| **Windows 10/11 com WSL2** | Containers Linux rodam numa VM leve gerenciada pelo WSL2 | **Caminho recomendado no Windows**. Requer WSL2, não WSL1 |
| **Windows nativo (Hyper-V)** | Funciona, mas performance de disco pior e mais atrito | Só se WSL2 não for possível |
| **macOS** (Intel ou Apple Silicon) | Roda numa VM Linux escondida | Funciona bem. I/O de disco em bind mount é o ponto fraco |
| **Windows containers** | Containers que rodam Windows de verdade, só em host Windows | Nicho (.NET Framework legado). Não é o que este material cobre |

> **Regra que economiza horas:** container Linux só roda sobre kernel Linux. Em macOS e
> Windows há sempre uma VM Linux no meio — visível ou não. Isso não é detalhe: explica a
> lentidão de I/O e o consumo de RAM nessas plataformas.

### Contas e serviços

| Conta | Obrigatória? | Para quê | Custo |
|---|---|---|---|
| **Docker Hub** | Não para usar; **sim** na prática | Sem login: 10 *pulls* por hora por IP. Com conta grátis: 100/hora | Grátis (plano Personal) |
| **Docker Desktop** (licença) | Depende da empresa | Grátis para uso pessoal, educação, open source não comercial e empresas com < 250 funcionários **e** < US$ 10 mi de receita anual | Ver [80-custos-e-licencas.md](80-custos-e-licencas.md) |
| **GitHub** | Não | GHCR (registry gratuito), Codespaces, CI | Grátis |

> **Sem cartão de crédito** em nenhum dos itens acima no plano gratuito (verificado em
> 11/08/2026).

---

## 3. Decisão que você precisa tomar antes de instalar

Existem dois caminhos, e escolher errado custa retrabalho:

| | **Docker Engine** (CLI + daemon) | **Docker Desktop** (app gráfico) |
|---|---|---|
| Plataforma | Linux apenas | Linux, macOS, Windows |
| Interface | Só linha de comando | GUI + CLI |
| Licença | Apache 2.0, livre para tudo | Grátis com limites; paga em empresa grande |
| Consumo | Nenhum extra | VM dedicada, ~2 GB RAM em repouso |
| Recomendação | **Servidor e desktop Linux** | **macOS e Windows** |

Alternativas legítimas ao Docker Desktop, se a licença for problema: **Podman Desktop**,
**Rancher Desktop**, **colima** (macOS), **OrbStack** (macOS, pago, muito rápido). Comparadas
em [80-custos-e-licencas.md](80-custos-e-licencas.md).

---

## 4. Tempo realista de estudo

Números honestos, assumindo estudo consistente e prática com as mãos. Se alguém prometer
"Docker em 1 hora", entendeu-se `docker run`, não Docker.

| Nível | O que você consegue fazer | Tempo realista |
|---|---|---|
| **Sobrevivência** | Rodar imagens prontas, publicar porta, ler logs, subir um Postgres | **3–5 horas** |
| **Produtivo em dev** | Escrever Dockerfile decente, usar Compose, montar volume, depurar container | **15–25 horas** (1 a 2 semanas) |
| **Competente** | Multi-stage, cache de build eficiente, redes, healthcheck, imagem enxuta e segura, CI | **60–100 horas** (2 a 3 meses) |
| **Produção** | Operar sob carga, limites de recurso, log e métrica, segurança, registry privado, multi-arch | **200–400 horas** (6 meses a 1 ano, com produção real) |
| **Profundidade interna** | Entender namespaces/cgroups/OverlayFS a ponto de depurar sem `docker`, escrever runtime, avaliar gVisor/Kata | **500+ horas** e trabalho no assunto |

**A cicatriz que ninguém conta:** o salto difícil não é do 1 para o 2, é do 3 para o 4. Rodar
container é fácil; operar container com estado, rede e segurança em produção é uma
especialidade inteira.

---

## 5. Rota de resgate — falta um pré-requisito, e agora?

| O que falta | Rota mais curta |
|---|---|
| **Nunca usei terminal** | Faça 2 horas de linha de comando básica **antes**. Insistir sem isso gera frustração falsa ("Docker é difícil" quando o difícil é o `cd`). |
| **Máquina fraca / sem disco** | Use ambiente na nuvem: [Play with Docker](https://labs.play-with-docker.com) (grátis, sessões de 4h) ou GitHub Codespaces (60h/mês grátis). Ver [03-instalacao.md](03-instalacao.md#alternativa-sem-instalar-nada). |
| **Windows sem WSL2 / sem permissão de admin** | Play with Docker ou Codespaces. Ou uma VM Linux num serviço de nuvem barato. |
| **Empresa proíbe Docker Desktop** | Instale Podman Desktop ou Rancher Desktop — mesmos comandos, licença livre. `alias docker=podman` cobre 90% do uso. |
| **Não sei programar** | Passe o Bloco A inteiro usando **imagens prontas** (nginx, postgres, redis). Só volte ao Dockerfile quando tiver algo seu para empacotar. |
| **Não sei YAML** | Comece só com `docker run`. Compose entra no [04-como-comecar.md](04-como-comecar.md), e o YAML necessário é trivial. |
| **Não sei Linux** | Não bloqueia o começo. Bloqueia no `75-armadilhas.md` (permissão de volume, usuário não-root). Aprenda `chown`, UID/GID e permissões quando chegar lá. |

---

## 6. Checklist antes de seguir

```bash
# 1. Terminal abre e responde
echo "ok"
# esperado: ok

# 2. Você sabe onde está
pwd
# esperado: um caminho absoluto, ex.: /home/seu-usuario

# 3. Há disco livre suficiente (>= 20 GB)
df -h /
# esperado: coluna "Avail" com 20G ou mais

# 4. Arquitetura da máquina
uname -m
# esperado: x86_64 (amd64) ou aarch64/arm64

# 5. Só em Linux — versão do kernel (>= 5.10)
uname -r
# esperado: 6.8.0-... ou similar

# 6. Só em Linux — virtualização NÃO é necessária, mas confira o suporte a cgroup v2
stat -fc %T /sys/fs/cgroup/
# esperado: cgroup2fs   (se vier "tmpfs", você está em cgroup v1 — funciona, mas é legado)
```

Passou nos seis? Vá para [03-instalacao.md](03-instalacao.md).

---

## Autoteste

1. Por que "saber Kubernetes" **não** é pré-requisito para Docker — e por que a ordem inversa
   prejudica o aprendizado?
2. Qual é o recurso de hardware que costuma acabar primeiro numa máquina de desenvolvedor com
   Docker, e por quê?
3. Em qual dos três sistemas operacionais **não** existe uma VM entre você e o container? Que
   consequência prática isso tem?
4. Sua empresa tem 400 funcionários. Você pode usar Docker Desktop gratuitamente? E Docker
   Engine?
5. Quantos *pulls* por hora você consegue do Docker Hub sem fazer login? E com conta gratuita?
6. Você tem 3 horas por semana. Quanto tempo até conseguir escrever um Dockerfile decente com
   Compose?
7. Cite duas rotas de resgate para alguém que não pode instalar nada na própria máquina.
