# Próximos passos: Swarm, Kubernetes e o que vem depois

> **Nível:** intermediário → avançado
> **Última verificação:** 18/08/2026

## 1. Onde você está

Terminando este curso, você sabe empacotar uma aplicação, orquestrar vários
serviços numa máquina, persistir dados, segmentar rede e endurecer container.

**Isso resolve seus três projetos.** FlixARD, sistema financeiro e CFTV rodam em
um servidor local, e Compose é a ferramenta certa para um servidor local.

A pergunta deste módulo é: **quando isso deixa de bastar?**

## 2. O limite do Compose

Compose gerencia containers **em uma máquina**. Ele não sabe:

- distribuir containers entre várias máquinas;
- mover um container quando a máquina morre;
- fazer deploy sem downtime, com rollback automático;
- escalar conforme a carga.

Se você nunca vai precisar disso, **pare aqui**. O maior erro de arquitetura que
se vê hoje é adotar Kubernetes para rodar três serviços em um servidor.

### Sinais de que você passou do ponto

- Precisa de **alta disponibilidade** — o serviço não pode cair quando a máquina
  cai.
- Tem **mais de uma máquina** e está gerenciando cada uma na mão.
- Precisa de **deploy sem downtime** com rollback automático.
- A carga varia muito e você quer **escala automática**.
- Você tem **equipe** e precisa de controle de acesso e limites por time.

Nenhum sinal? Compose está certo. Um ou dois? Talvez Swarm. Vários, e é seu
trabalho? Kubernetes.

## 3. Docker Swarm

Orquestrador embutido no próprio Docker. Você já sabe 80% dele.

```bash
docker swarm init                     # em uma máquina
docker swarm join --token ... <ip>    # nas outras
docker stack deploy -c compose.yaml minha-stack
```

O mesmo `compose.yaml`, com as chaves `deploy:` passando a valer de verdade:

```yaml
services:
  api:
    image: minha-api:1.0.0
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first      # sobe o novo antes de derrubar o velho
        failure_action: rollback
      restart_policy:
        condition: on-failure
      resources:
        limits: {cpus: "1.0", memory: 512m}
```

**O que Swarm dá sobre Compose:** múltiplas máquinas, réplicas com balanceamento,
rolling update com rollback, secrets **criptografados em repouso** (aqui sim,
diferente do Compose standalone), rede overlay entre máquinas.

**A questão incômoda: Swarm está morto?** Não, mas está em manutenção. A Mirantis
(que comprou o Docker Enterprise) mantém, e há correções de segurança. Não há
desenvolvimento de recursos novos relevantes desde ~2020, e o ecossistema — CNCF,
ferramentas, vagas, material — foi todo para o Kubernetes.

**Opinião profissional, não consenso:** para homelab de 2 a 3 máquinas, Swarm é
tecnicamente a escolha mais sensata — 10% da complexidade do Kubernetes para 80%
do benefício, e você já sabe a sintaxe. Mas se o objetivo for **empregabilidade**,
o tempo é melhor investido em Kubernetes. Muita gente respeitável discorda e diz
para pular Swarm por completo; o argumento contrário é o risco de investir numa
tecnologia sem futuro claro.

## 4. Kubernetes

O padrão de fato para orquestração distribuída. E uma mudança de modelo mental,
não só de sintaxe.

| Conceito | Compose | Kubernetes |
|---|---|---|
| Unidade | service | **Pod** (um ou mais containers juntos) |
| Réplicas | `--scale` | **Deployment** / ReplicaSet |
| Rede interna | DNS do Compose | **Service** (ClusterIP) |
| Entrada externa | `ports:` | **Ingress** / LoadBalancer |
| Volume | `volumes:` | **PersistentVolumeClaim** |
| Config | `environment:` | **ConfigMap** |
| Segredo | `secrets:` | **Secret** (base64, **não** criptografado por padrão!) |
| Arquivo | `compose.yaml` | vários manifests YAML |

Um `compose.yaml` de 30 linhas vira ~120 linhas de manifests. Essa é a taxa de
entrada.

### A ideia central: reconciliação

Compose é **imperativo** — você manda subir, ele sobe. Kubernetes é
**declarativo com reconciliação**: você descreve o estado desejado ("quero 3
réplicas saudáveis") e um controlador trabalha continuamente para que a
realidade bata com a descrição. Matou um pod? Ele recria. A máquina caiu? Ele
recria em outra.

Essa diferença é o que dá auto-recuperação — e é também a origem da complexidade.

### Distribuições leves para começar

| Opção | Para que serve |
|---|---|
| **k3s** | Kubernetes completo em ~50 MB. **A melhor escolha para homelab** — roda até em Raspberry Pi |
| **kind** | cluster em containers Docker; ótimo para aprender e testar em CI |
| **minikube** | cluster local em VM; clássico para estudo |
| **k3d** | k3s dentro de Docker; parte do jeito mais rápido de subir |

Comece com **k3s** se quiser algo que dure, ou **kind** se for só para estudar.

### Aviso sobre Secrets no Kubernetes

Um `Secret` do Kubernetes é **base64, não criptografia**. Base64 é codificação,
qualquer um decodifica. Sem configurar criptografia em repouso no etcd (ou usar
Sealed Secrets, External Secrets Operator, Vault), o segredo está praticamente em
texto claro para quem tiver acesso ao cluster. Muita gente descobre isso tarde.

## 5. Alternativas ao Docker

O Docker não é mais a única implementação. Os padrões OCI (formato de imagem e
runtime) tornaram tudo intercambiável.

| Ferramenta | O que é | Quando considerar |
|---|---|---|
| **Podman** | compatível com Docker, **sem daemon**, rootless por desenho | quer segurança melhor sem abrir mão da sintaxe; padrão no Fedora/RHEL |
| **containerd** | o runtime que o próprio Docker usa por baixo | é o que o Kubernetes usa direto hoje |
| **Buildah** | só constrói imagens, sem daemon | build em CI sem privilégio |
| **BuildKit** | o construtor moderno, já embutido no Docker | você já usa (`--mount=type=cache`) |
| **nerdctl** | CLI estilo Docker para containerd | quando o ambiente já é containerd |

Sobre o **Podman**: `alias docker=podman` funciona para a maioria dos comandos, e
`podman-compose` cobre boa parte do Compose. A vantagem real é arquitetural — não
há daemon root, cada container é um processo filho do seu usuário. Se você está
começando do zero e valoriza segurança, vale considerar seriamente.

## 6. O que estudar depois, em ordem

Sugestão de sequência, com o porquê de cada etapa:

1. **Registry próprio** (Harbor, ou o registry do GitHub). Você vai precisar de um
   lugar para suas imagens antes de qualquer orquestração.
2. **CI/CD** (GitHub Actions). Build e push automáticos a cada commit. É o que
   torna tudo repetível — e é o degrau com melhor retorno logo após este curso.
3. **Proxy reverso com TLS** (Caddy ou Traefik). Você já usa no FlixARD; aprofunde
   em roteamento, autenticação e certificados.
4. **Observabilidade** (Prometheus + Grafana + Loki). Quando algo quebra às 3h,
   você quer gráfico, não `docker logs`.
5. **Backup automatizado e testado** (restic, Duplicati). Você já tem o serviço de
   backup do sistema financeiro; falta a rotina de restauração.
6. **Kubernetes com k3s** — só depois dos cinco anteriores.

Repare que Kubernetes é o **último**. Os cinco primeiros trazem benefício
imediato aos seus projetos; Kubernetes só compensa depois que eles existem.

## 7. Aplicado aos seus projetos

| Projeto | Recomendação | Por quê |
|---|---|---|
| **CFTV (MotionEye)** | **fique no Compose, para sempre** | uma máquina, uma câmera, sem necessidade de escala. Já está em produção e funcionando — não mexa |
| **FlixARD** | Compose agora; Swarm **se** virar 2+ máquinas | streaming é I/O e CPU, não concorrência de requisições. Orquestração não resolveria nada hoje |
| **Sistema financeiro** | Compose + CI/CD + backup testado | se crescer para usuários reais, o próximo passo é uma VPS gerenciada, não Kubernetes |

**A recomendação honesta:** nenhum dos três precisa de Kubernetes. Se você quiser
aprendê-lo, aprenda por interesse e empregabilidade — não porque seus projetos
exijam. Adotar orquestração distribuída para três serviços numa máquina é
trocar problemas simples e conhecidos por problemas complexos e novos.

## 8. Autoteste

1. Cite três coisas que o Compose não faz.
2. Quais sinais indicam que você passou do ponto do Compose?
3. O que o Swarm dá sobre o Compose? Cite três.
4. Qual a diferença de modelo mental entre Compose e Kubernetes?
5. Por que um `Secret` do Kubernetes não é seguro por padrão?
6. Qual a vantagem arquitetural do Podman sobre o Docker?
7. Por que Kubernetes é o **último** item da lista de estudo?
8. Qual dos seus três projetos justifica orquestração distribuída? Justifique.

---
[← módulo 08](08-projeto-aplicado/compose-sistema-financeiro.md) · [glossário](GLOSSARIO.md) · [índice](00-indice.md)
