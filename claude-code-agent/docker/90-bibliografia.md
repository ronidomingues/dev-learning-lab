# 90 · Bibliografia comentada

`Nível: todos` · `Última atualização: 11/08/2026`

Livros, com autor, edição e para que nível servem. **Nada aqui foi inventado**: onde não tenho
certeza de uma edição ou ISBN, cito só autor e título e digo que é aproximado. Confirme a edição
mais recente antes de comprar — livros de tecnologia envelhecem, e alguns destes já têm parte
datada.

---

## 1. Para aprender Docker

### Docker Deep Dive — Nigel Poulton

- **Autor:** Nigel Poulton (Docker Captain)
- **Edição:** atualizada em 2025 (o autor revisa o livro periodicamente; confirme a mais recente)
- **Nível:** iniciante → intermediário
- **Onde:** Leanpub, Amazon, Apple Books, Google Books
- **Por que ler:** é o livro mais popular e mais bem avaliado sobre Docker, e com razão. Poulton
  escreve com clareza incomum, começa do zero e chega a Swarm, redes e segurança. A edição de
  2025 acrescentou capítulos sobre **Wasm containers** e **Docker Model Runner** (LLMs locais).
- **Ressalva honesta:** cobre Swarm com peso que o mercado não dá mais; a parte de orquestração
  envelheceu em relação ao domínio do Kubernetes. O núcleo (imagens, containers, rede,
  armazenamento) continua excelente e atual.
- **Gratuito?** Não. É pago em todas as plataformas. Preço acessível no Leanpub.

### Docker in Action, 2ª edição — Jeff Nickoloff e Stephen Kuenzli

- **Editora:** Manning, 2ª ed. (2019)
- **Nível:** intermediário
- **Por que ler:** mais profundo que o Poulton em operação e em detalhes de runtime. Bom segundo
  livro, para quem já roda containers e quer entender melhor o que acontece por baixo.
- **Ressalva:** 2019 — anterior ao BuildKit padrão, aos avanços de cadeia de suprimentos e às
  mudanças recentes da Engine. O conceitual resiste; ferramentas e comandos, verifique.

### The Docker Book — James Turnbull

- **Nível:** iniciante → intermediário
- **Por que ler:** foi o livro de referência da primeira geração; didático. Turnbull é um bom
  professor.
- **Ressalva:** **datado.** Útil historicamente e para os fundamentos, mas muita coisa mudou.
  Não seria minha primeira escolha em 2026.

---

## 2. Para ir além do Docker (containers e Kubernetes)

### Container Security — Liz Rice

- **Editora:** O'Reilly (2020)
- **Nível:** intermediário → avançado
- **Por que ler:** **a melhor referência sobre segurança de containers.** Liz Rice explica
  namespaces, cgroups, capabilities, seccomp e escapes com uma clareza que este material tentou
  imitar. Se você só for ler um livro além do básico, que seja este.
- **Ressalva:** 2020 — cadeia de suprimentos (SBOM, assinatura, SLSA) evoluiu muito depois;
  complemente com [65-estado-da-arte.md](65-estado-da-arte.md) e a documentação do Sigstore.
- **Gratuito?** A O'Reilly às vezes libera este título em PDF via patrocínio (Aqua Security já
  distribuiu). Procure "Container Security Liz Rice free PDF" — **confirme a legitimidade** antes
  de baixar; o download oficial patrocinado é legal, cópias piratas não.

### Kubernetes Up & Running — Hightower, Burns, Beda

- **Editora:** O'Reilly, 3ª ed. (2022)
- **Nível:** intermediário
- **Por que ler:** escrito por gente que construiu o Kubernetes (Brendan Burns e Joe Beda estão
  entre os criadores). A ponte natural depois deste material, se você for para orquestração.
- **Ressalva:** Kubernetes muda rápido; confira contra a documentação da versão que você usa.

### Kubernetes Patterns — Bilgin Ibryam e Roland Huß

- **Editora:** O'Reilly, 2ª ed. (2023)
- **Nível:** intermediário → avançado
- **Por que ler:** cataloga padrões de projeto para cargas em container. Ótimo para quem já opera
  e quer parar de reinventar.

### Cloud Native DevOps with Kubernetes — Arundel e Domingus

- **Editora:** O'Reilly, 2ª ed. (2022)
- **Nível:** intermediário
- **Por que ler:** conecta container e Kubernetes à prática de DevOps (CI/CD, observabilidade,
  custo). Boa visão de fim a fim.

---

## 3. Fundamentos de sistemas (o "por baixo" dos containers)

### The Linux Programming Interface — Michael Kerrisk

- **Editora:** No Starch Press (2010)
- **Nível:** avançado → referência
- **Por que ler:** **a** referência sobre a interface de programação do Linux. Namespaces,
  processos, sinais, memória — tudo que faz um container ser um container está explicado aqui, na
  fonte. Não é sobre Docker; é sobre o que o Docker usa.
- **Ressalva:** 2010, mas o núcleo de syscalls mudou pouco. É um tijolo de 1.500 páginas — use
  como referência, não como leitura linear.
- **Gratuito?** Não, mas o autor mantém material complementar e as páginas de manual (`man`) que
  ele escreveu são gratuitas e excelentes.

### How Linux Works, 3ª ed. — Brian Ward

- **Editora:** No Starch Press (2021)
- **Nível:** intermediário
- **Por que ler:** contexto de sistema para quem não vem de Linux profundo. Ajuda a entender
  cgroups, processos e o que o container está mentindo para o processo.

### Systems Performance, 2ª ed. — Brendan Gregg

- **Editora:** Addison-Wesley (2020)
- **Nível:** avançado
- **Por que ler:** o livro definitivo sobre desempenho de sistemas Linux, com **um capítulo
  dedicado a containers** (cgroups, throttling, observação). Se você chegou ao ponto de depurar
  latência e throttling de container ([13](13-isolamento-namespaces-cgroups.md),
  [60](60-teoria-avancada.md)), é aqui que se aprofunda.

---

## 4. Para arquitetura e produção

### Designing Data-Intensive Applications — Martin Kleppmann

- **Editora:** O'Reilly (2017)
- **Nível:** intermediário → avançado
- **Por que ler:** não é sobre containers, mas é sobre o problema que os containers **não**
  resolvem: estado, consistência, replicação. Quando você externalizar o estado (passo 4 da
  migração em [25-orquestracao.md](25-orquestracao.md)), este livro é o mapa. Um dos melhores
  livros técnicos desta geração.
- **Nota:** há uma 2ª edição em preparação; confira se já saiu.

### Site Reliability Engineering — Google (Beyer et al.)

- **Editora:** O'Reilly (2016)
- **Nível:** intermediário
- **Por que ler:** os conceitos de SLO, monitoramento e os quatro sinais de ouro que aparecem em
  [21-observabilidade-e-operacao.md](21-observabilidade-e-operacao.md) vêm daqui.
- **Gratuito?** **Sim, legalmente.** O Google disponibiliza o texto completo em
  [sre.google/books](https://sre.google/books/). Também há o *SRE Workbook*, igualmente gratuito.

---

## 5. O que é legalmente gratuito

| Obra | Onde | Observação |
|---|---|---|
| **Site Reliability Engineering** + **SRE Workbook** | [sre.google/books](https://sre.google/books/) | Texto completo, oficial |
| **Documentação oficial do Docker** | [docs.docker.com](https://docs.docker.com) | Melhor que muitos livros pagos |
| **Kubernetes the Hard Way** — Kelsey Hightower | [GitHub](https://github.com/kelseyhightower/kubernetes-the-hard-way) | Tutorial gratuito, clássico |
| **Páginas de manual do Linux** (`man 7 namespaces`, `man 7 cgroups`) | qualquer Linux | Fonte primária, de Michael Kerrisk |
| **Especificações OCI** | [github.com/opencontainers](https://github.com/opencontainers) | Curtas e esclarecedoras |
| **Container Security** — Liz Rice | via patrocínio O'Reilly (confirme a legitimidade) | Frequentemente liberado em PDF |

---

## 6. Recomendação por perfil

| Você é… | Leia, nesta ordem |
|---|---|
| **Iniciante total** | Docker Deep Dive (Poulton) + docs oficiais + prática |
| **Dev que quer produção** | Poulton → Container Security (Rice) → SRE (grátis) |
| **Quem quer entender por baixo** | The Linux Programming Interface (Kerrisk) + Systems Performance (Gregg) |
| **Indo para Kubernetes** | Kubernetes Up & Running → Kubernetes Patterns |
| **Arquiteto** | Designing Data-Intensive Applications + Kubernetes Patterns + SRE |
| **Foco em segurança** | Container Security (Rice) → CKS curriculum → docs Sigstore |

---

## 7. O que **não** recomendo

Sem citar título específico injustamente, um alerta de categoria:

- **Livros de "Docker em 24 horas / para leigos" genéricos** — costumam estar desatualizados e
  raramente vão além do que a documentação oficial gratuita cobre melhor.
- **Qualquer livro de Docker anterior a 2019** como fonte principal — perde BuildKit, Compose
  v2, cadeia de suprimentos e as mudanças recentes de Engine. Bom para história, ruim para
  prática.
- **Cursos/livros que ensinam `docker-compose` (com hífen) e `version:`** — sintaxe obsoleta;
  sinal de material velho.

---

## Autoteste

1. Qual livro você recomendaria a um iniciante total, e qual a ressalva dele?
2. Qual é a melhor referência sobre segurança de containers, e o que a data dela exige que você
   complemente?
3. Cite dois livros legalmente gratuitos e onde obtê-los.
4. Por que "Designing Data-Intensive Applications" aparece numa bibliografia de Docker, se não
   fala de containers?
5. Qual livro consultar para depurar throttling de CPU em container?
6. Por que um livro de Docker de 2018 é problemático como fonte principal em 2026?
7. Qual é a fonte primária, gratuita e sempre atualizada sobre namespaces e cgroups?
8. Monte uma trilha de leitura para quem quer entender containers "por baixo".
9. Por que a documentação oficial pode ser melhor que um livro pago?
10. Que sinais indicam que um material de Docker está desatualizado, só pela sintaxe usada?
