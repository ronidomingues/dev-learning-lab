# 11 · História — de onde vieram os containers e que problema resolveram

`Nível: iniciante → intermediário` · `Última atualização: 11/08/2026`

Este arquivo existe porque quase toda decisão estranha do Docker tem explicação histórica. Saber
a história é o que separa "isso é assim" de "isso é assim **porque**".

---

## Linha do tempo em uma tela

```
1979  chroot                       isolar a visão do sistema de arquivos
1982  chroot no BSD                idem, difundido
2000  FreeBSD Jails                isolamento de processo + rede, para hospedagem
2004  Solaris Zones                zonas com recursos controlados
2005  OpenVZ                       containers em Linux, com kernel modificado
2006  Process Containers (Google)  → renomeado para cgroups
2008  cgroups no kernel 2.6.24     limitação de recursos entra oficialmente no Linux
2008  LXC                          primeiro conjunto completo em Linux puro
2011  Warden (Cloud Foundry)       containers como plataforma
2013  Docker 0.1 (março)           ★ o ponto de virada
2013  Docker Hub                   distribuição pública de imagens
2014  Docker 1.0 · Kubernetes      produção + orquestração
2015  OCI · CNCF                   padronização, fim do risco de aprisionamento
2015  runC doado                   runtime de referência
2016  containerd                   runtime de alto nível
2017  Moby · Kubernetes vence      Docker vira upstream; K8s vence a guerra dos orquestradores
2018  Podman 1.0 · gVisor          alternativa sem daemon; sandbox de syscalls
2019  Mirantis compra Docker EE    Docker Inc. foca em desenvolvedores
2020  "K8s remove o Docker"        dockershim descontinuado — pânico desproporcional
2021  Docker Desktop passa a cobrar de empresas grandes
2022  dockershim removido de fato (K8s 1.24) · Wasm entra na conversa
2023  BuildKit padrão · Docker Scout · Wasm no Docker Desktop
2025  Docker Hub aperta limites de pull (abril) · Docker Model Runner
2026  Engine 29: containerd image store por padrão, nftables experimental
```

---

## Ato 1 — A pré-história (1979–2012): a ideia existia, faltava a embalagem

### `chroot` (1979)

Bill Joy acrescenta ao Unix V7 uma chamada que muda o diretório raiz de um processo. Motivo
original: **testar builds e instalações num ambiente limpo**, sem sujar o sistema.

Isolava só o sistema de arquivos. E era escapável: um processo root com um descritor de
diretório aberto antes do `chroot` conseguia sair. A lição que ficou — **isolamento parcial
não é isolamento** — voltaria a ser aprendida várias vezes.

### FreeBSD Jails (2000)

Poul-Henning Kamp implementa *jails* para um provedor de hospedagem que precisava separar
clientes na mesma máquina. Acrescenta ao `chroot` o isolamento de processos, de usuários e de
rede (cada jail com seu IP).

Aqui já está quase tudo que chamamos de container. **Faltava o que faltaria por mais 13 anos:
um jeito de empacotar e distribuir o conteúdo do jail.**

### Solaris Zones (2004) e OpenVZ (2005)

Zones acrescentam controle fino de recursos e uma noção de "marca" (rodar Linux dentro de uma
zone Solaris). OpenVZ traz containers para o Linux, mas com um **kernel modificado** — o que
impediu a adoção ampla, porque exigia trocar o kernel da distribuição.

### cgroups (2006–2008) — a peça que faltava no Linux

Paul Menage e Rohit Seth, no Google, escrevem os *Process Containers*. O Google rodava milhares
de trabalhos por máquina no Borg e precisava garantir que um trabalho não roubasse CPU e
memória dos outros. Renomeado para **cgroups**, entra no kernel 2.6.24 em janeiro de 2008.

Combinado com os namespaces, que vinham sendo adicionados desde 2002, **o Linux passou a ter
tudo de que um container precisa** — em kernel padrão, sem patch.

### LXC (2008)

Primeiro conjunto de ferramentas a juntar namespaces + cgroups em Linux puro. Funcionava. Era
usado por gente que sabia o que estava fazendo. E era **difícil**: configuração extensa,
nenhum formato de distribuição, cada instalação era artesanal.

> **A lição central da pré-história:** de 2008 a 2013, todos os recursos técnicos do container
> já existiam no kernel Linux padrão. O que não existia era **experiência de uso**. A revolução
> de 2013 não foi tecnológica — foi de embalagem.

---

## Ato 2 — 2013: o Docker aparece

### O contexto

A dotCloud era uma PaaS francesa (Solomon Hykes, Sebastien Pahl, Kamel Founadi) que usava LXC
internamente para isolar aplicações de clientes. Havia construído ferramental interno para
tornar isso viável. O negócio de PaaS não decolava.

Em **março de 2013**, na PyCon, Hykes faz um *lightning talk* de 5 minutos e libera o
ferramental interno como código aberto. Em **outubro**, a empresa se renomeia para Docker, Inc.

### O que o Docker realmente inventou

Nenhuma das peças isoladas era nova. **A combinação era.**

| Peça | Já existia? | O que o Docker fez |
|---|---|---|
| Isolamento de processo | Sim (LXC) | Usou o LXC no começo; depois escreveu o `libcontainer` |
| Sistema de arquivos em camadas | Sim (AUFS, UnionFS) | Fez dele o **formato de distribuição** |
| Empacotamento | Não, nesse formato | Criou a **imagem**: unidade portátil e endereçada por conteúdo |
| Descrição do build | Não | Criou o **Dockerfile**: build versionável em texto |
| Distribuição pública | Não | Criou o **Docker Hub**: `docker run redis` funciona sem saber nada de Redis |
| Experiência de uso | **Não** | `docker run` em uma linha, com saída legível |

*Opinião profissional, não consenso:* a peça mais subestimada é o **Docker Hub**. O formato de
imagem sem um lugar público para buscá-las teria sido mais uma ferramenta de nicho. O que
mudou o comportamento de milhões de desenvolvedores foi poder subir qualquer tecnologia com uma
linha, sem ler manual. Foi um efeito de rede, não uma inovação de kernel.

### Por que pegou tão rápido

Três problemas convergiam na época:

1. **A explosão da complexidade de dependências.** Aplicações web modernas tinham dezenas de
   dependências com versões conflitantes. "Funciona na minha máquina" havia deixado de ser
   piada e virado custo.
2. **A nuvem tinha virado commodity, mas a implantação não.** Ninguém queria repetir Chef e
   Puppet convergindo servidores por dez minutos.
3. **A pressão por velocidade de entrega.** Deploy semanal virou deploy diário, e o gargalo era
   a diferença entre ambientes.

O Docker atacou os três com o mesmo artefato.

---

## Ato 3 — 2014–2017: orquestração e a guerra dos padrões

Uma vez que rodar um container ficou trivial, a pergunta seguinte apareceu imediatamente: **e
mil containers, em cem máquinas?**

| Ano | Evento |
|---|---|
| 2014 | Google libera o **Kubernetes**, destilado de 15 anos de Borg |
| 2014 | CoreOS lança o **rkt**, criticando o daemon monolítico e o modelo de segurança do Docker |
| 2015 | Docker responde com o **Swarm mode**, integrado ao Engine |
| 2015 | Apache **Mesos**/Marathon disputa o mesmo espaço |
| 2015 | **OCI** é criada; Docker doa o `runC` |
| 2015 | **CNCF** é criada; Kubernetes é o projeto fundador |
| 2016 | **containerd** é extraído do Docker e doado |
| 2017 | AWS lança EKS; Docker Inc. anuncia suporte a Kubernetes no Desktop |

**Em 2017 a disputa estava decidida:** Kubernetes venceu a orquestração; Docker permaneceu como
a ferramenta de desenvolvimento e o formato de imagem. rkt foi arquivado em 2020. Mesos foi
para a manutenção mínima em 2021.

### Por que o Kubernetes venceu

Cinco razões, em ordem de peso na minha leitura:

1. **Governança neutra.** Sob a CNCF, nenhum fornecedor controlava o projeto. Swarm era da
   Docker Inc.; adotá-lo era apostar numa empresa.
2. **A herança do Borg.** O Kubernetes já nasceu com respostas para problemas que só aparecem em
   escala real — e que quem estava começando ainda nem conhecia.
3. **Extensibilidade.** CRDs e operadores permitiram que o ecossistema estendesse a plataforma
   sem esperar o projeto principal.
4. **Todos os provedores de nuvem o adotaram**, porque nenhum queria a plataforma do concorrente.
5. **Modelo declarativo.** Descrever o estado desejado envelheceu melhor que emitir comandos.

E o que o Swarm fazia melhor — e ainda faz: **ser simples**. Para 3 servidores e 10 serviços,
Swarm continua sendo tecnicamente adequado e muito mais barato de operar. Perdeu por dinâmica
de ecossistema, não por mérito técnico isolado.

---

## Ato 4 — 2018–2022: comoditização, dessacralização e o susto

### O Docker deixa de ser insubstituível

| Ano | Evento | Consequência |
|---|---|---|
| 2018 | **Podman 1.0** (Red Hat) | Sem daemon, rootless por padrão, CLI compatível |
| 2018 | **gVisor** (Google) | Sandbox de syscalls em espaço de usuário |
| 2018 | **Kata Containers** | Containers dentro de micro-VMs |
| 2018 | **BuildKit** | Build paralelo, cache melhor, segredos |
| 2019 | **Mirantis compra a Docker Enterprise** | Docker Inc. fica com o produto de desenvolvedor |
| 2019 | **Buildah, Skopeo, crun** | O ferramental se fragmenta em peças pequenas |

### O episódio do dockershim (2020) — e o pânico que ele causou

Em dezembro de 2020, o Kubernetes anunciou a descontinuação do **dockershim**, o adaptador que
permitia ao kubelet falar com o Docker Engine. Manchetes anunciaram que "o Kubernetes está
removendo o Docker".

**O que realmente aconteceu:** o Kubernetes definiu, em 2016, uma interface chamada **CRI**
(*Container Runtime Interface*). `containerd` e CRI-O a implementam nativamente. O Docker
Engine, não — ele é anterior à CRI e tem funcionalidades que o Kubernetes não usa (build, rede
própria, Compose). O `dockershim` era código de adaptação que o time do Kubernetes mantinha de
graça, dentro do próprio projeto, para um único fornecedor. Foi removido em 2022 (K8s 1.24).

**O que mudou para você:** essencialmente nada.
- As imagens continuam sendo as mesmas — são OCI, não "imagens Docker".
- O `docker build` continua produzindo imagens que rodam em qualquer Kubernetes.
- Só quem operava clusters precisou trocar o runtime do nó para `containerd` — e o `containerd`
  já era o que o Docker usava por baixo.

**A lição real do episódio:** o Docker havia se tornado sinônimo de container no vocabulário
popular, e essa confusão custou semanas de pânico à indústria inteira. Precisão de vocabulário
tem valor operacional.

---

## Ato 5 — 2021–2026: o modelo de negócio e a maturidade

### A mudança de licença (2021)

Em agosto de 2021, a Docker Inc. alterou os termos do **Docker Desktop**: passou a exigir
assinatura paga para empresas com mais de 250 funcionários **ou** mais de US$ 10 milhões de
receita anual.

Reação previsível e legítima: empresas migraram para Podman Desktop, Rancher Desktop, colima,
OrbStack. Também previsível e legítimo: a Docker Inc. precisava de receita — o Docker Engine é
Apache 2.0 e sempre foi gratuito; manter um app de desktop para macOS e Windows custa dinheiro.

**Ponto que costuma se perder no debate:** a mudança **nunca** afetou o Docker Engine no Linux,
que continua livre. Muita gente migrou de ferramenta sem precisar.

### Os limites do Docker Hub (2025)

Em **1º de abril de 2025**, entrou em vigor a política atual de limites de *pull*:

| Situação | Limite |
|---|---|
| Sem autenticação | **10 pulls/hora**, por endereço IP |
| Conta gratuita autenticada | **100 pulls/hora** |
| Pro, Team, Business | Ilimitado, sob uso justo |

Consequência prática mais dolorosa: pipelines de CI em IP compartilhado quebraram em massa. A
resposta da indústria foi acelerar a migração para GHCR, ECR Public e espelhos internos.
*Interpretação:* o Docker Hub foi, por uma década, uma infraestrutura pública crítica financiada
por uma única empresa privada. Isso não era sustentável, e a correção veio de uma vez.

### Onde estamos em agosto de 2026

- **Docker Engine 29** (29.7.1, de 04/08/2026): o **containerd image store** virou o padrão em
  instalações novas, e há suporte experimental a **nftables** como backend de firewall, em
  substituição ao iptables legado.
- **containerd 2.x** e **CRI-O** dominam os clusters; **Podman 5** e alternativas avançam nas
  máquinas de desenvolvimento.
- **OCI é o padrão inquestionado.** O registry deixou de ser "lugar de imagem" e virou
  armazenamento de artefatos genéricos: SBOMs, assinaturas, políticas, gráficos Helm, modelos de
  IA.
- A conversa se deslocou de "como rodo containers" para **cadeia de suprimentos** (proveniência,
  assinatura, SBOM), **isolamento mais forte** (micro-VMs, gVisor) e **runtimes alternativos**
  (WebAssembly).

Detalhes em [65-estado-da-arte.md](65-estado-da-arte.md).

---

## O que a história ensina, em quatro lições

**1. A tecnologia raramente vence pela tecnologia.** Containers existiam havia 13 anos quando o
Docker apareceu. Ganhou quem resolveu a experiência de uso e a distribuição.

**2. Padrão aberto é o que preserva o investimento.** A OCI é a razão pela qual sua imagem de
2016 ainda roda hoje, em runtimes que nem existiam então. Sem ela, teríamos formatos
incompatíveis por fornecedor.

**3. Quem controla o formato não controla o mercado.** O Docker criou o formato e perdeu a
orquestração para um projeto de governança neutra. Foi doar o `runC` e o `containerd` — e não
retê-los — o que manteve o formato relevante.

**4. Infraestrutura pública gratuita tem um dono, e ele tem contas a pagar.** Docker Hub,
npm, PyPI: quando a conta chega, os termos mudam. Planeje espelho e alternativa **antes** de o
pipeline quebrar.

---

## Autoteste

1. Todos os recursos de kernel para containers existiam desde 2008. Por que a adoção massiva só
   veio em 2013–2015?
2. Qual das invenções do Docker você considera a mais decisiva, e por quê? Defenda a escolha.
3. O que exatamente era o `dockershim`, por que foi removido, e o que mudou na sua vida?
4. Cite três razões pelas quais o Kubernetes venceu o Swarm, e uma coisa em que o Swarm é melhor.
5. A mudança de licença de 2021 afetou o Docker Engine no Linux? Justifique.
6. Que problema de negócio o Google estava resolvendo quando criou os cgroups em 2006?
7. Por que a criação da OCI em 2015 foi, no longo prazo, mais importante para você do que
   qualquer versão do Docker?
8. Que mudança de 01/04/2025 quebrou pipelines de CI no mundo inteiro, e qual foi a resposta da
   indústria?
9. O que mudou na Docker Engine 29 em relação ao armazenamento de imagens, e por que só afeta
   instalações novas?

---

### Fontes consultadas (11/08/2026)

- [Docker (software) — Wikipedia](https://en.wikipedia.org/wiki/Docker_(software)) — cronologia geral
- [endoflife.date — Docker Engine](https://endoflife.date/docker-engine) — Engine 29.7.1, 04/08/2026
- [Docker Engine v29 Release — Docker Blog](https://www.docker.com/blog/docker-engine-version-29/) e [Linuxiac](https://linuxiac.com/docker-engine-29-containerd-becomes-default-experimental-nftables-support/) — containerd image store padrão, nftables experimental
- [GitLab Support — Docker Hub rate limiting](https://support.gitlab.com/hc/en-us/articles/20028360858140-Docker-Hub-rate-limiting-impacts-GitLab-pipelines) — limites vigentes desde 01/04/2025
