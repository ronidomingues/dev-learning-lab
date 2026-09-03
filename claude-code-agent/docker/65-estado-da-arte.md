# 65 · Estado da arte — agosto de 2026

`Nível: pesquisa` · `Data de referência: 11/08/2026` · **Este é o arquivo que envelhece mais rápido.**

O que está estabelecido, o que está em disputa e o que ainda é aposta. Onde uma afirmação vem de
fonte secundária ou é minha leitura, o texto diz isso.

---

## 1. O panorama em uma tabela

| Camada | Situação em ago/2026 |
|---|---|
| **Formato de imagem** | OCI, indiscutido. O registry virou depósito genérico de artefatos |
| **Runtime de baixo nível** | `runc` domina; `crun` avança; `youki` (Rust) amadurecendo |
| **Runtime de alto nível** | `containerd` 2.x é o padrão de fato; CRI-O em OpenShift |
| **Engine de desenvolvimento** | Docker Engine 29; Podman 5, colima, OrbStack, Rancher Desktop disputando o desktop |
| **Orquestração** | Kubernetes venceu. A disputa migrou para o que roda **em cima** dele |
| **Build** | BuildKit padrão; cache remoto e multi-arch como higiene básica |
| **Segurança** | Deslocou-se do isolamento para a **cadeia de suprimentos** |
| **Fronteira ativa** | WebAssembly, isolamento confidencial, imagens "zero CVE", cargas de IA |

---

## 2. O que a Docker Engine 29 mudou

Duas mudanças estruturais, ambas verificadas na documentação oficial:

**1. O containerd image store passou a ser o padrão em instalações novas.** O armazenamento de
camadas e conteúdo deixa de usar o backend histórico do Docker e passa ao `containerd`. Efeitos:
suporte nativo a multi-plataforma local (`--load` de várias arquiteturas), snapshotters
plugáveis (o que destrava *lazy pulling*) e convergência com o que roda no Kubernetes.

> **Detalhe que importa na prática:** a mudança vale para **instalações novas**. Atualizar da 28
> para a 29 não migra automaticamente o seu store existente. Duas máquinas da mesma equipe podem
> ter comportamentos diferentes conforme tenham sido instaladas antes ou depois.

**2. Suporte experimental a nftables** como backend de firewall, ativável com
`"firewall-backend": "nftables"` no `daemon.json`. As regras são funcionalmente equivalentes às
de iptables, **mas quem usa a cadeia `DOCKER-USER`** para restringir acesso precisa reescrevê-la.
O `iptables` está em substituição gradual em todas as distribuições Linux há anos; o Docker é
dos últimos grandes projetos a migrar.

A versão corrente na data de referência é a **29.7.1**, publicada em **04/08/2026**.

---

## 3. WebAssembly: a aposta que amadureceu parcialmente

**A promessa:** módulos Wasm iniciam em microssegundos, ocupam kilobytes, rodam com isolamento
por design (sem syscalls — só o que a plataforma expõe via WASI) e são portáteis entre
arquiteturas sem recompilar.

**Onde está em agosto de 2026:**

- O **shim `runwasi`** integra runtimes Wasm ao `containerd`. Fontes secundárias reportam que a
  Docker Engine 29 estabilizou esse shim, permitindo executar cargas Wasm com pegada de memória
  muito menor que a de um container Alpine equivalente. *Não confirmei essa estabilização na
  documentação oficial da Docker na data desta escrita; trate como reportado, não como
  verificado.*
- **WASI Preview 2** e o **Component Model** destravaram a composição de módulos e o acesso a
  I/O de forma padronizada — o que era o principal bloqueio para cargas de servidor.
- Kubernetes executa Wasm via `RuntimeClass` apontando para o shim, sem alteração no restante do
  cluster.

**O que Wasm resolve bem hoje:** funções sem estado, plugins e extensões (Envoy, proxies), edge
computing, execução de código não confiável de usuários, cold start crítico.

**O que ainda não resolve:** threads e I/O bloqueante maduros, ecossistema de bibliotecas
comparável, depuração e observabilidade, cargas com estado.

*Minha leitura, não consenso:* Wasm **não** substituirá containers para aplicações de servidor
convencionais nesta década. Ele ocupa a faixa onde container é pesado demais: funções muito
curtas, plugins e execução de código de terceiros. A previsão de 2019, de que "Wasm mataria o
Docker", não se realizou e não parece caminho provável — os dois coexistem sob o mesmo runtime,
o que é uma vitória do modelo OCI, não uma substituição.

---

## 4. Cadeia de suprimentos: de boa prática a obrigação legal

Este é **o** deslocamento do biênio, e ele deixou de ser técnico.

### Sigstore graduou; a regulação chegou

- **Sigstore atingiu o status de projeto graduado da CNCF em outubro de 2025**, o que consolidou
  a assinatura *keyless* como padrão da indústria.
- O **EU Cyber Resilience Act (CRA)** entrou na fase de aplicação. Conforme reportado por fontes
  do setor: as **obrigações de notificação de vulnerabilidade passam a valer em 11/09/2026**, e
  a regulação **entra em vigor plenamente em 11/12/2027**. O CRA exige que fabricantes de
  produtos com elementos digitais **mantenham SBOM** e a disponibilizem a reguladores mediante
  solicitação.

**A consequência para quem publica software na Europa:** SBOM e gestão de vulnerabilidade
deixaram de ser diferencial e passaram a ser requisito de conformidade, com prazo. Isso muda a
economia de todo o ecossistema de imagens.

### O efeito prático: "zero CVE" virou expectativa de linha de base

Surgiu uma categoria comercial de **imagens base endurecidas com CVEs próximas de zero** e SLA
de correção — Docker Hardened Images, Chainguard Images, Minimus e concorrentes. O argumento de
venda é direto: em vez de sua equipe caçar e corrigir CVEs em imagens base, você paga por
imagens mantidas nesse estado.

*Avaliação profissional:* a proposta é legítima e resolve um problema real de custo de
manutenção. Duas ressalvas honestas: (1) "zero CVE" refere-se a **CVEs conhecidas na data do
escaneamento** em uma base minimalista — não é uma propriedade de segurança absoluta; (2) é uma
nova forma de aprisionamento a fornecedor na camada mais básica da sua pilha. A alternativa
gratuita continua sendo `distroless` + escaneamento próprio + disciplina de atualização, que
custa tempo de equipe em vez de licença.

### O que se tornou higiene mínima em 2026

```bash
docker buildx build --sbom=true --provenance=true -t org/app:1.0 --push .
cosign sign --yes org/app@sha256:...
trivy image --severity CRITICAL,HIGH --ignore-unfixed org/app:1.0
```
E, do lado da execução, uma política de admissão que **verifica** — Kyverno, Sigstore Policy
Controller ou OPA Gatekeeper ingerindo atestados SLSA e **VEX** (o formato que declara "esta CVE
não é explorável no meu contexto", reduzindo o ruído dos scanners).

---

## 5. Isolamento: o retorno da máquina virtual

O ciclo se fechou. Depois de uma década vendendo "containers substituem VMs", a indústria
convergiu para **containers dentro de VMs**:

| Tecnologia | Onde está em ago/2026 |
|---|---|
| **Firecracker** | Base do AWS Lambda e Fargate; ~125 ms de boot; usado também por Fly.io |
| **Kata Containers** | Maduro; RuntimeClass no Kubernetes; adoção em nuvens públicas e ambientes regulados |
| **gVisor** | Base do Google Cloud Run e do GKE Sandbox; sobrecarga de 10–30% em I/O |
| **Confidential Containers** | Projeto CNCF; usa AMD SEV-SNP, Intel TDX e ARM CCA para cifrar memória **em uso** |

**Confidential computing é a fronteira relevante:** a memória do container permanece cifrada
mesmo para o hipervisor e o operador da nuvem, com atestação remota do estado. Casos de uso —
processar dado de saúde ou financeiro em nuvem pública sem confiar no provedor; inferência de
modelo proprietário em infraestrutura de terceiro. Hoje ainda é caro, imaturo em ferramental e
dependente de hardware específico. *Aposta pessoal:* será commodity até o fim da década, movida
pela regulação de dados mais do que pela demanda técnica.

---

## 6. IA mudou os requisitos de container

Cargas de IA quebraram três premissas do modelo tradicional:

| Premissa antiga | Realidade com IA |
|---|---|
| Imagens de dezenas a centenas de MB | **Dezenas de GB** (CUDA, cuDNN, PyTorch, pesos) |
| Cold start de segundos é aceitável | Carregar um modelo pode levar minutos |
| Container não precisa de acesso a hardware especial | GPU é obrigatória e precisa ser particionada |
| Estado fica em banco | Pesos de modelo são artefatos gigantes e imutáveis |

As respostas em desenvolvimento:

- **Lazy pulling** (eStargz, SOCI, Nydus) — iniciar antes de a imagem inteira estar baixada. O
  *containerd image store* como padrão na Engine 29 é pré-requisito para isso ficar acessível no
  Docker.
- **Modelos como artefatos OCI** — distribuir pesos pelo registry, com as mesmas garantias de
  digest, assinatura e cache das imagens.
- **Particionamento de GPU** — NVIDIA MIG e time-slicing expostos como recurso agendável.
- **Docker Model Runner** — a Docker Inc. passou a oferecer execução local de LLMs com APIs
  compatíveis com OpenAI e Ollama, empacotadas no fluxo de container.
- **MCP Catalog e MCP Toolkit** — catálogo curado de servidores MCP com um gateway que faz
  proxy, log e controle das conexões usadas por agentes de IA.

*Leitura da estratégia:* a Docker Inc. está se posicionando como **camada de governança e
isolamento para agentes de IA** — sandbox, catálogo curado, imagens endurecidas. Faz sentido:
executar código gerado por agente é exatamente o problema de "rodar código não confiável" que
containers atacam, e é um mercado novo onde a marca tem tração. Se isso se sustenta
comercialmente, ainda não dá para dizer.

---

## 7. eBPF: a camada que está reescrevendo a rede e a observabilidade

eBPF permite executar programas verificados no kernel sem módulos. Aplicado a containers:

| Ferramenta | O que faz |
|---|---|
| **Cilium** | CNI que substitui kube-proxy e iptables; política de rede em L3–L7 |
| **Tetragon** | Observação e aplicação de política em nível de syscall, com contexto de processo |
| **Falco** | Detecção de comportamento anômalo em execução |
| **Pixie / Parca / Coroot** | Observabilidade sem instrumentar a aplicação |

**Por que importa:** o `iptables` não escala para milhares de serviços (as regras são avaliadas
linearmente); eBPF usa mapas de hash. Além disso, correlacionar evento de kernel com o container
e o processo de origem é exatamente o que faltava para a segurança em execução ser acionável.

A migração do Docker para nftables (seção 2) é parte do mesmo movimento maior: **o plano de
dados de rede está saindo do iptables**.

---

## 8. Debates abertos, com os dois lados

### "Docker Desktop vale a assinatura?"

**A favor:** integração superior em macOS e Windows, atualização automática, Scout,
funcionalidades de segurança gerenciada, suporte. Para uma empresa, um desenvolvedor perdendo
duas horas com colima já custa mais que um ano de licença.

**Contra:** o Engine é livre; as alternativas (Podman Desktop, Rancher Desktop, colima) cobrem a
maior parte dos casos; e é aprisionamento numa camada que deveria ser commodity.

*Minha posição:* em Linux, não há motivo para Docker Desktop. Em macOS e Windows, pague se a
empresa pode — o custo de suporte interno das alternativas costuma exceder a licença. Em
organização com restrição orçamentária ou de conformidade, Podman Desktop é uma escolha
madura e sem ressalva técnica relevante.

### "Kubernetes é complexo demais para a maioria?"

**A favor da crítica:** a maioria das equipes que o adota tem menos de dez serviços e um pico de
tráfego previsível. A complexidade operacional é real e recorrente.

**Contra:** a alternativa costuma ser um conjunto de scripts caseiros que reimplementa mal um
subconjunto do Kubernetes, sem documentação nem comunidade. E o mercado de trabalho o exige.

*Minha posição:* a crítica é válida para **um** servidor e questionável a partir de cinco. O erro
mais comum não é escolher Kubernetes; é escolhê-lo antes de resolver containerização, CI e
externalização de estado. Ver [25-orquestracao.md](25-orquestracao.md).

### "Imagens 'zero CVE' pagas resolvem o problema?"

Tratado na seção 4. Em resumo: resolvem um custo real, criam uma dependência nova, e o "zero" é
relativo à data e ao escopo do escaneamento.

---

## 9. Previsões para 2027–2028 — e o que as invalidaria

Explicitamente **especulação**, com o critério de falsificação junto:

| Previsão | Confiança | O que a invalidaria |
|---|---|---|
| SBOM obrigatório em produção regulada na UE | **alta** | Adiamento da aplicação do CRA |
| Lazy pulling padrão para imagens grandes | alta | Custo de armazenamento cair a ponto de tornar o pull irrelevante |
| Wasm consolidado em nicho, sem substituir containers | média-alta | WASI resolver threads e I/O e o ecossistema de bibliotecas fechar a lacuna |
| Confidential containers como commodity em nuvem | média | Custo de hardware ou falha de confiança nas TEEs (já houve ataques a SGX) |
| Docker Desktop com mais recursos exclusivos de assinatura | alta | Pressão competitiva de OrbStack e Podman |
| Assinatura verificada na admissão como padrão | média | Atrito operacional maior que o benefício percebido |
| Consolidação dos fornecedores de imagem endurecida | média | Uma alternativa aberta boa o bastante surgir |

---

## 10. O que **não** mudou, e provavelmente não vai mudar

Vale terminar por aqui, porque é o que sustenta o resto do material:

- **O formato OCI.** Uma imagem de 2016 roda hoje. Aposte nele.
- **Namespaces e cgroups.** A base do isolamento no Linux não vai ser substituída.
- **Multi-stage e imagem enxuta.** Continua sendo a maior alavanca de tamanho e segurança.
- **"Container é processo."** O modelo mental permanece o mesmo.
- **Estado vive em volume ou fora do container.** Verdade estrutural, não moda.
- **Tratar sinais, healthcheck honesto, log em stdout, configuração por ambiente.** Continuam
  separando quem opera de quem sofre.

Ferramenta muda; fundamento não. É por isso que os arquivos 10 a 21 deste material envelhecem em
década, e este aqui envelhece em meses.

---

## Autoteste

1. Quais foram as duas mudanças estruturais da Engine 29, e por que a primeira só vale para
   instalações novas?
2. Onde Wasm ganha de container hoje, e onde ainda não ganha?
3. Que obrigação legal passa a valer em 11/09/2026 e o que ela exige na prática?
4. Por que "zero CVE" é uma afirmação relativa? Cite duas ressalvas.
5. Por que a indústria voltou a colocar containers dentro de VMs? Cite três produtos que fazem
   isso.
6. Quais três premissas do modelo de container as cargas de IA quebraram, e qual é a resposta a
   cada uma?
7. Como eBPF muda a rede de containers, e o que isso tem a ver com a migração para nftables?
8. Apresente os dois lados do debate sobre a assinatura do Docker Desktop e defenda uma posição.
9. Escolha uma previsão da seção 9 e descreva um evento concreto que a invalidaria.
10. Cite três fundamentos que não mudaram e explique por que são estáveis.

---

### Fontes consultadas (11/08/2026)

- [Docker Engine v29 Release — Docker Blog](https://www.docker.com/blog/docker-engine-version-29/) · [Docker Engine 29 release notes](https://docs.docker.com/engine/release-notes/29/) · [Linuxiac — Containerd Becomes Default, Experimental nftables Support](https://linuxiac.com/docker-engine-29-containerd-becomes-default-experimental-nftables-support/)
- [endoflife.date — Docker Engine](https://endoflife.date/docker-engine) — 29.7.1, 04/08/2026
- [Container Runtime Alternatives 2026 Deep Dive — youngju.dev](https://www.youngju.dev/blog/culture/2026-05-16-container-runtime-alternatives-2026-containerd-cri-o-podman-runc-gvisor-kata-youki-wasmedge-firecracker-deep-dive.en) — panorama de runtimes; **fonte secundária** para a estabilização do shim runwasi na Engine 29
- [Docker Docs — Model Runner](https://docs.docker.com/ai/model-runner/) · [Bret Fisher — Docker AI, Model Runner e MCP Toolkit](https://www.bretfisher.com/blog/docker-ai-model-runner-and-mcp-toolkit) · [Collabnix — What's New in Docker in 2026](https://collabnix.com/whats-new-in-docker-in-2026-sandboxes-hardened-images-and-the-ai-native-container-platform/)
- [Docker — EU Cyber Resilience Act (CRA): Overview](https://www.docker.com/blog/eu-cyber-resilience-act-overview/) · [RapidFort — EU CRA for Containers & Kubernetes](https://www.rapidfort.com/blog/eu-cyber-resilience-act-what-it-means-for-containers-and-kubernetes) — prazos de 11/09/2026 e 11/12/2027
- [Minimus — Container Image Governance Guide 2026](https://www.minimus.io/post/container-image-governance) — Sigstore graduado na CNCF em out/2025; VEX e políticas de admissão
- [Help Net Security — eBPF com Cilium, Tetragon e SBOMs](https://www.helpnetsecurity.com/2025/06/18/ebpf-cilium-tetragon-sboms-security/)
