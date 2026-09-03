# Docker e Containers — Mapa do Assunto

`Nível: do zero absoluto ao de pesquisa` · `Última atualização: 11/08/2026`
`Versões de referência: Docker Engine 29.7.1 · Compose v2 · containerd 2.x`

---

## O que é este material

Um curso completo sobre **Docker e containers**: o que são, como usar, como funcionam por
dentro, quando **não** usar, a economia do ecossistema e a fronteira de pesquisa em agosto de
2026.

Ele responde, na ordem em que as perguntas aparecem na vida real:

1. **O que é isso e por que existe?** → [`01`](01-introducao-leigo.md) e [`11`](11-historia.md)
2. **Como começo hoje, sem quebrar nada?** → [`02`](02-pre-requisitos.md) a
   [`07`](07-projeto-modelo/README.md)
3. **Como funciona por dentro, e onde estão os limites?** → Bloco B
4. **Como opero isso em produção sem me arrepender?** → [`20`](20-seguranca.md),
   [`21`](21-observabilidade-e-operacao.md)
5. **Quanto custa e onde estudo mais?** → Blocos D e E

Container **não** é máquina virtual, **não** exige microserviços e **não** é seguro por padrão.
Este material insiste nesses três pontos porque são a origem da maior parte dos erros.

---

## O que você saberá ao final

- Explicar a um leigo o que é um container e por que "na minha máquina funciona" deixou de ser
  problema.
- Instalar todo o ferramental, em qualquer SO, e sair do zero a uma aplicação rodando.
- Escrever um Dockerfile de produção: multi-stage, não-root, cache eficiente, imagem enxuta,
  sinais tratados, healthcheck honesto.
- Operar aplicações multi-container com Compose: redes, volumes, dependências, segredos.
- Explicar namespaces, cgroups e OverlayFS a ponto de depurar sem o `docker`.
- Distribuir imagens com segurança: registries, digest, SBOM, assinatura, escaneamento.
- Endurecer containers e saber quando o isolamento padrão **não** basta (micro-VM, gVisor).
- Observar e operar: logs, métricas, throttling, encerramento gracioso, backup testado.
- Decidir com fundamento quando (e quando não) partir para orquestração.
- Estimar custo de verdade — licença, pulls, egress, e o custo de gente.

---

## Roteiro de leitura

### Caminho rápido (um fim de semana, "quero entender e mexer")
`01` → `02` → `03` → `04` → `06` → `07-projeto-modelo/` → `75`

### Caminho do desenvolvedor
`01` → `03` → `04` → `10` → `12` → `15` → `16` → `17` → `18` → `07-projeto-modelo/` → `70` → `75`

### Caminho de quem vai operar em produção
`01` → `10` → `17` → `18` → `19` → `20` → `21` → `25` → `70` → `75`

### Caminho de arquiteto / pesquisador
todo o Bloco B em ordem, com peso em `13` → `14` → `60` → `65`, depois `95`

### Caminho de quem decide (compra, arquitetura, contratação)
`01` → `11` → `25` → `80` → `65` → `75`

---

## Arquivos

### BLOCO A · Porta de entrada (01–09)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [01-introducao-leigo.md](01-introducao-leigo.md) | iniciante | O que é, para que serve, por que existe. Zero jargão. |
| [02-pre-requisitos.md](02-pre-requisitos.md) | iniciante | O que saber e ter antes. Tempo realista. Rota de resgate. |
| [03-instalacao.md](03-instalacao.md) | iniciante | Manual de campo: Engine/Desktop, Compose, Git por SO. Proxy, PATH, desinstalar, erros. |
| [04-como-comecar.md](04-como-comecar.md) | iniciante | Do ambiente pronto à primeira imagem, volume e Compose rodando. |
| [05-manual-de-uso.md](05-manual-de-uso.md) | intermediário | Referência consultável de comandos, flags e padrões. |
| [06-exemplos.md](06-exemplos.md) | intermediário | 14 receitas completas, do trivial ao CI/CD e proxy com TLS. |
| [07-projeto-modelo/](07-projeto-modelo/README.md) | intermediário | App completo (mural de recados) que roda de verdade, com 10 laboratórios. |

### BLOCO B · Núcleo (10–69)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [10-fundamentos.md](10-fundamentos.md) | iniciante→interm. | Definição formal, os quatro substantivos, cinco modelos mentais, os cinco porquês. |
| [11-historia.md](11-historia.md) | iniciante→interm. | 1979→2026: chroot, cgroups, Docker, a guerra dos orquestradores, o dockershim. |
| [12-imagens-e-camadas.md](12-imagens-e-camadas.md) | interm.→avançado | Formato OCI, camadas, cache de build, tamanho, vazamento de segredo. |
| [13-isolamento-namespaces-cgroups.md](13-isolamento-namespaces-cgroups.md) | avançado | Container à mão sem Docker; os 7 namespaces, cgroups v2, capabilities, seccomp. |
| [14-runtime-e-arquitetura.md](14-runtime-e-arquitetura.md) | avançado | CLI→dockerd→containerd→shim→runc→processo. OCI config, BuildKit, drivers. |
| [15-armazenamento-e-volumes.md](15-armazenamento-e-volumes.md) | interm.→avançado | Volumes, bind mounts, permissões (UID/GID, SELinux), backup, desempenho. |
| [16-redes.md](16-redes.md) | interm.→avançado | Bridge, host, macvlan, DNS interno, publicação de porta, o firewall furado. |
| [17-dockerfile-e-build.md](17-dockerfile-e-build.md) | interm.→avançado | Cada instrução, cache, multi-stage, escolha de base, linting, erros de build. |
| [18-compose-e-multicontainer.md](18-compose-e-multicontainer.md) | intermediário | `depends_on`, variáveis, sobreposição, perfis, watch, escala, Compose em produção. |
| [19-registries-e-distribuicao.md](19-registries-e-distribuicao.md) | interm.→avançado | Registries, tags vs digest, cadeia de suprimentos (SBOM, assinatura), registry próprio. |
| [20-seguranca.md](20-seguranca.md) | avançado | Modelo de ameaça, as 10 medidas, o que anula o isolamento, incidentes. |
| [21-observabilidade-e-operacao.md](21-observabilidade-e-operacao.md) | interm.→avançado | Logs, métricas, healthchecks, encerramento gracioso, diagnóstico, backup. |
| [25-orquestracao.md](25-orquestracao.md) | interm.→avançado | Quando um servidor não basta. Swarm, Kubernetes, a ponte, quando **não** ir. |
| [60-teoria-avancada.md](60-teoria-avancada.md) | pesquisa | NP-dificuldade do agendamento, isolamento de desempenho, throttling, provas. |
| [65-estado-da-arte.md](65-estado-da-arte.md) | pesquisa | Agosto/2026: Engine 29, Wasm, cadeia de suprimentos legal, IA, eBPF. |

### BLOCO C · Prática e erros (70–79)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [70-pratica.md](70-pratica.md) | todos | 10 laboratórios progressivos com critério de aprovação. |
| [75-armadilhas.md](75-armadilhas.md) | todos | Os 8 erros de iniciante, os mitos, as más práticas e por que persistem. |

### BLOCO D · Economia e ecossistema (80–89)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [80-custos-e-licencas.md](80-custos-e-licencas.md) | todos | Engine grátis, Desktop pago, limites do Hub, egress, o custo de gente. |
| [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) | todos | Cursos grátis PT/EN/FR e o mapa das certificações (DCA, KCNA, CKA). |

### BLOCO E · Fontes (90–99)

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [90-bibliografia.md](90-bibliografia.md) | todos | Livros com edição, nível e o que envelheceu. |
| [95-referencias.md](95-referencias.md) | todos | Specs OCI, docs, código-fonte, papers, pessoas, como o material foi verificado. |
| [GLOSSARIO.md](GLOSSARIO.md) | todos | ~90 termos definidos. |

---

## Status por bloco

| Bloco | Status | Observação |
|---|---|---|
| A · Porta de entrada | ✅ | 6 documentos + projeto-modelo executável (testes rodam e passam) |
| B · Núcleo | ✅ | 15 documentos, fundamentos → arquitetura interna → teoria → estado da arte |
| C · Prática e erros | ✅ | 10 laboratórios + catálogo de armadilhas |
| D · Economia | ✅ | Preços e cursos consultados em 11/08/2026 |
| E · Fontes | ✅ | Bibliografia, referências e glossário |

Legenda: ✅ completo · 🟡 parcial · ⬜ pendente

---

## Aviso de validade

Docker e o ecossistema de containers mudam rápido. Este material foi escrito sobre:

- **Docker Engine:** 29.7.1 (04/08/2026) · **Compose:** v2 · **containerd:** série 2.x
- **Data das consultas de preço, versão e curso:** 11/08/2026
- **Câmbio para ordens de grandeza:** US$ 1 ≈ R$ 5,40

O que envelhece mais rápido, em ordem: [`65-estado-da-arte`](65-estado-da-arte.md) e
[`80-custos-e-licencas`](80-custos-e-licencas.md) (meses), [`03-instalacao`](03-instalacao.md) e
[`85-cursos-e-certificacoes`](85-cursos-e-certificacoes.md) (releases / ~1 ano). O núcleo
conceitual ([`10`](10-fundamentos.md), [`13`](13-isolamento-namespaces-cgroups.md),
[`14`](14-runtime-e-arquitetura.md), [`60`](60-teoria-avancada.md)) envelhece em década — porque
namespaces, cgroups e o formato OCI são estáveis.

**Nota de verificação:** o projeto-modelo teve sua suíte de testes **executada e aprovada** (22
testes, Node v24.18.0) e a aplicação foi rodada fora de container; o `docker build`/`compose up`
não puderam ser executados no ambiente de escrita (sem socket do daemon). Detalhes no
[README do projeto](07-projeto-modelo/README.md) e em [95-referencias.md](95-referencias.md).

---

## Autoteste do mapa

1. Container é uma máquina virtual? Qual é a única diferença estrutural, e o que decorre dela?
2. Qual arquivo você leria primeiro para justificar (ou desaconselhar) adotar Kubernetes?
3. Qual bloco você consulta se seu container está reiniciando em laço em produção?
4. Onde estão os limites teóricos (o que **não** dá para fazer com containers)?
5. Por que o núcleo conceitual envelhece em década e o estado da arte em meses?
