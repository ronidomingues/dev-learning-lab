# 95 · Referências — specs, docs, código, pessoas

`Nível: todos` · `Última atualização: 11/08/2026`

Fontes primárias e verificáveis. Preferência por documentação oficial, especificações e código
sobre artigos de blog. Onde cito blog ou fonte secundária, digo que é isso.

---

## 1. Especificações (as fontes de verdade)

| Spec | Onde | O que define |
|---|---|---|
| **OCI Image Spec** | [github.com/opencontainers/image-spec](https://github.com/opencontainers/image-spec) | Formato da imagem: manifesto, camadas, config, digests |
| **OCI Runtime Spec** | [github.com/opencontainers/runtime-spec](https://github.com/opencontainers/runtime-spec) | Bundle, `config.json`, ciclo de vida, hooks |
| **OCI Distribution Spec** | [github.com/opencontainers/distribution-spec](https://github.com/opencontainers/distribution-spec) | API HTTP do registry |
| **CNI (Container Network Interface)** | [github.com/containernetworking/cni](https://github.com/containernetworking/cni) | Plugins de rede |
| **CSI (Container Storage Interface)** | [github.com/container-storage-interface/spec](https://github.com/container-storage-interface/spec) | Plugins de armazenamento |
| **CRI (Container Runtime Interface)** | parte do Kubernetes | Contrato kubelet ↔ runtime |
| **SLSA** | [slsa.dev](https://slsa.dev) | Níveis de garantia de proveniência |
| **SPDX / CycloneDX** | [spdx.dev](https://spdx.dev) · [cyclonedx.org](https://cyclonedx.org) | Formatos de SBOM |

São curtas e esclarecedoras. Ler a Runtime Spec uma vez dissolve mais dúvidas que dez tutoriais.

---

## 2. Documentação oficial

| Recurso | URL |
|---|---|
| **Docker Docs** | [docs.docker.com](https://docs.docker.com) |
| Referência do Dockerfile | [docs.docker.com/reference/dockerfile](https://docs.docker.com/reference/dockerfile/) |
| Compose Specification | [github.com/compose-spec/compose-spec](https://github.com/compose-spec/compose-spec) |
| Docker Engine release notes | [docs.docker.com/engine/release-notes](https://docs.docker.com/engine/release-notes/) |
| BuildKit | [github.com/moby/buildkit](https://github.com/moby/buildkit) |
| Best practices de Dockerfile | [docs.docker.com/build/building/best-practices](https://docs.docker.com/build/building/best-practices/) |
| Rate limits do Docker Hub | [docs.docker.com/docker-hub/usage](https://docs.docker.com/docker-hub/usage/) |

---

## 3. Código-fonte (para quem quer o fundo do poço)

| Projeto | Repositório | O que é |
|---|---|---|
| **Moby** | [github.com/moby/moby](https://github.com/moby/moby) | O upstream do Docker Engine |
| **containerd** | [github.com/containerd/containerd](https://github.com/containerd/containerd) | Runtime de alto nível (CNCF, graduado) |
| **runc** | [github.com/opencontainers/runc](https://github.com/opencontainers/runc) | Runtime de referência da OCI |
| **crun** | [github.com/containers/crun](https://github.com/containers/crun) | Runtime em C, mais rápido |
| **youki** | [github.com/youki-dev/youki](https://github.com/youki-dev/youki) | Runtime em Rust |
| **Podman** | [github.com/containers/podman](https://github.com/containers/podman) | Engine sem daemon |
| **BuildKit** | [github.com/moby/buildkit](https://github.com/moby/buildkit) | Motor de build |
| **gVisor** | [github.com/google/gvisor](https://github.com/google/gvisor) | Kernel em espaço de usuário |
| **Firecracker** | [github.com/firecracker-microvm/firecracker](https://github.com/firecracker-microvm/firecracker) | Micro-VM |
| **Kata Containers** | [github.com/kata-containers/kata-containers](https://github.com/kata-containers/kata-containers) | Container em micro-VM |
| **runwasi** | [github.com/containerd/runwasi](https://github.com/containerd/runwasi) | Shim Wasm para containerd |

---

## 4. Ferramentas mencionadas neste material

| Ferramenta | O que faz | URL |
|---|---|---|
| **dive** | Analisa camadas e desperdício de imagem | [github.com/wagoodman/dive](https://github.com/wagoodman/dive) |
| **hadolint** | Linter de Dockerfile | [github.com/hadolint/hadolint](https://github.com/hadolint/hadolint) |
| **Trivy** | Vulnerabilidades, segredos, má config | [github.com/aquasecurity/trivy](https://github.com/aquasecurity/trivy) |
| **Grype / Syft** | Escaneamento / SBOM | [github.com/anchore](https://github.com/anchore) |
| **Dockle** | Boas práticas de imagem | [github.com/goodwithtech/dockle](https://github.com/goodwithtech/dockle) |
| **cosign** | Assinatura de imagem | [github.com/sigstore/cosign](https://github.com/sigstore/cosign) |
| **skopeo** | Copiar/inspecionar imagens sem daemon | [github.com/containers/skopeo](https://github.com/containers/skopeo) |
| **netshoot** | Caixa de ferramentas de rede | [github.com/nicolaka/netshoot](https://github.com/nicolaka/netshoot) |
| **Docker Bench** | Auditoria CIS | [github.com/docker/docker-bench-security](https://github.com/docker/docker-bench-security) |
| **Falco** | Detecção em runtime | [github.com/falcosecurity/falco](https://github.com/falcosecurity/falco) |
| **cAdvisor** | Métricas de container | [github.com/google/cadvisor](https://github.com/google/cadvisor) |
| **Watchtower** | Atualização automática (cuidado em produção) | [github.com/containrrr/watchtower](https://github.com/containrrr/watchtower) |
| **gitleaks** | Detecção de segredo | [github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) |

---

## 5. Artigos acadêmicos (fundamentos e teoria)

Referenciados em [60-teoria-avancada.md](60-teoria-avancada.md):

- **Menage, P.** (2007). *Adding Generic Process Containers to the Linux Kernel.* Linux
  Symposium. — a origem dos cgroups.
- **Verma, A. et al.** (2015). *Large-scale cluster management at Google with Borg.* EuroSys. — o
  ancestral do Kubernetes.
- **Agache, A. et al.** (2020). *Firecracker: Lightweight Virtualization for Serverless
  Applications.* USENIX NSDI. — o trade-off isolamento × cold start.
- **Young, E. G. et al.** (2019). *The True Cost of Containing: A gVisor Case Study.* USENIX
  HotCloud. — sobrecarga de gVisor medida.
- **Harter, T. et al.** (2016). *Slacker: Fast Distribution with Lazy Docker Containers.* USENIX
  FAST. — 76% do tempo de start é pull/extração; a origem do lazy pulling.
- **Karp, R.** (1972). *Reducibility Among Combinatorial Problems.* — NP-completude do bin
  packing.
- **Merkel, D.** (2014). *Docker: Lightweight Linux Containers for Consistent Development and
  Deployment.* Linux Journal. — o artigo de divulgação original.

Muitos estão em [usenix.org](https://www.usenix.org) (acesso aberto) e nos anais das
conferências.

---

## 6. Páginas de manual do Linux (fonte primária, gratuita)

```bash
man 7 namespaces
man 7 cgroups
man 7 capabilities
man 2 clone
man 2 unshare
man 2 seccomp
man 8 runc
man 5 dockerd     # se instalado
```

Escritas em grande parte por Michael Kerrisk. São a verdade sobre o que o kernel faz — acima de
qualquer blog.

---

## 7. Blogs e fontes secundárias (marcados como tais)

Úteis, mas **secundários** — verifique contra a documentação oficial:

| Fonte | Perfil |
|---|---|
| [Docker Blog](https://www.docker.com/blog/) | Oficial, mas é marketing além de técnica |
| [Julia Evans (jvns.ca)](https://jvns.ca) | Explicações excelentes de containers e Linux; os *zines* são ótimos |
| [Ivan Velichko (iximiuz.com)](https://iximiuz.com) | Laboratórios interativos e artigos profundos sobre containers |
| [Brendan Gregg (brendangregg.com)](https://www.brendangregg.com) | Desempenho de sistemas, referência |
| [LWN.net](https://lwn.net) | Cobertura profunda de kernel; a melhor fonte sobre mudanças no Linux |
| [endoflife.date](https://endoflife.date) | Datas de fim de vida e versões — usei para confirmar a Engine 29.7.1 |

---

## 8. Pessoas a seguir

Nomes que ajudam a acompanhar o campo (fatos públicos; sem inferir nada além do papel
profissional conhecido):

| Pessoa | Por quê |
|---|---|
| **Liz Rice** | Autoridade em segurança de containers e eBPF; autora e mantenedora |
| **Nigel Poulton** | Educador; autor de *Docker Deep Dive* |
| **Kelsey Hightower** | Referência em Kubernetes e cloud native; *Kubernetes the Hard Way* |
| **Brendan Gregg** | Desempenho de sistemas Linux |
| **Michael Kerrisk** | Autor de *TLPI* e mantenedor das man pages do Linux |
| **Ivan Velichko** | Conteúdo técnico profundo e prático sobre containers |
| **Solomon Hykes** | Criador do Docker (contexto histórico) |
| **Jérôme Petazzoni** | Um dos primeiros engenheiros do Docker; material didático clássico |

---

## 9. Comunidades

| Comunidade | Onde |
|---|---|
| CNCF Slack | [slack.cncf.io](https://slack.cncf.io) |
| Docker Community | [docker.com/community](https://www.docker.com/community/) |
| r/docker | [reddit.com/r/docker](https://www.reddit.com/r/docker/) |
| Stack Overflow | tags `docker`, `docker-compose` |
| Server Fault | operação e produção |

---

## 10. Como este material foi verificado

Transparência sobre a produção:

- **Versões e datas** (Engine 29.7.1, limites do Hub, prazos do CRA): confirmadas por busca em
  **11/08/2026**, com as fontes citadas no rodapé de [03](03-instalacao.md), [11](11-historia.md),
  [19](19-registries-e-distribuicao.md), [65](65-estado-da-arte.md), [80](80-custos-e-licencas.md)
  e [85](85-cursos-e-certificacoes.md).
- **O projeto-modelo** foi **executado**: a suíte de 22 testes passou em Node v24.18.0 e a
  aplicação foi verificada de ponta a ponta fora de container. O `docker build`/`docker compose
  up` **não** puderam ser executados no ambiente de escrita (sem acesso ao socket do daemon), o
  que está declarado no [README do projeto](07-projeto-modelo/README.md).
- **Comandos de exemplo** seguem a documentação oficial vigente na data. Ainda assim: **execute
  na sua máquina.** Versões mudam, e um comando que "deveria funcionar" é uma hipótese até você
  rodá-lo.
- **Onde uma afirmação vem de fonte secundária** (ex.: estabilização do shim runwasi na Engine
  29, estado da certificação DCA), o texto marca isso explicitamente em vez de apresentá-la como
  verificada.

---

## Autoteste

1. Quais são as três especificações da OCI e o que cada uma define?
2. Onde está o código-fonte do Docker Engine, e por que ele não se chama "docker"?
3. Qual página de manual você leria para entender namespaces na fonte?
4. Cite três ferramentas de segurança de imagem e o que cada uma faz.
5. Qual artigo mostrou que a maior parte do tempo de início de um container é pull/extração?
6. Por que blogs são marcados como fonte secundária aqui?
7. Qual fonte foi usada para confirmar a versão 29.7.1 da Engine?
8. O que exatamente foi verificado no projeto-modelo, e o que não pôde ser?
9. Cite duas pessoas a seguir e o motivo de cada uma.
10. Se um comando deste material falhar na sua máquina, o que a seção 10 sugere que você
    conclua?
