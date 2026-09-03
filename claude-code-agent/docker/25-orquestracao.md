# 25 · Orquestração — quando um servidor não basta

`Nível: intermediário → avançado` · `Última atualização: 11/08/2026`

Container resolve empacotamento. Orquestração resolve **onde**, **quantos** e **o que fazer
quando falha**. Este arquivo mostra a ponte, sem transformar o material num curso de Kubernetes.

---

## 1. Os problemas que a orquestração resolve

Com um servidor e o Compose, você já tem `restart: unless-stopped`. O que **não** tem:

| Problema | Compose | Orquestrador |
|---|---|---|
| A máquina morre | ❌ tudo cai | ✅ reagenda em outro nó |
| Deploy sem interrupção | ⚠️ manual, com dois containers | ✅ rolling update com rollback |
| Escalar conforme a carga | ❌ manual | ✅ autoscaling |
| Balancear entre nós | ❌ | ✅ mesh de serviço embutido |
| Colocar o serviço onde há recurso | ❌ | ✅ scheduler com afinidade e taints |
| Segredos distribuídos e cifrados | ⚠️ arquivo | ✅ gerenciado e cifrado |
| Configuração declarativa reconciliada | ⚠️ imperativo | ✅ loop de reconciliação |
| Descoberta de serviço entre máquinas | ❌ | ✅ DNS de cluster |

**A pergunta certa não é "devo usar Kubernetes?", e sim "quantos dos problemas acima eu tenho
hoje?".** Se a resposta for zero ou um, Compose num servidor é a escolha correta, e adotar
Kubernetes é comprar complexidade sem contrapartida.

---

## 2. As opções, honestamente comparadas

| | **Compose** | **Swarm** | **Nomad** | **Kubernetes** |
|---|---|---|---|---|
| Máquinas | 1 | várias | várias | várias |
| Tempo até produzir | horas | dias | dias | semanas a meses |
| Complexidade conceitual | baixa | baixa | média | **alta** |
| Autoscaling | não | não (só escala manual) | sim | sim |
| Ecossistema | pequeno | **estagnado** | médio | **enorme** |
| Suporte de nuvem gerenciado | não | não | limitado | **todos** |
| Mercado de trabalho | — | pouco | pouco | **dominante** |
| Custo operacional | mínimo | baixo | médio | alto |
| Quando escolher | 1 servidor | 2–10 servidores, equipe pequena | Cargas mistas (VM + container) | Escala, múltiplas equipes, nuvem |

### Sobre o Swarm — a avaliação honesta

O Swarm mode continua embutido no Docker Engine, funciona e é **substancialmente** mais simples
que o Kubernetes: você reaproveita quase todo o `compose.yaml`.

```bash
docker swarm init
docker stack deploy -c compose.yaml minha-app
docker service ls
docker service scale minha-app_api=5
docker service update --image ghcr.io/org/api:1.5 minha-app_api    # rolling update
docker service rollback minha-app_api
```

**O problema não é técnico, é de ecossistema.** O desenvolvimento praticamente parou, os
fornecedores de nuvem não o oferecem gerenciado, ferramentas novas assumem Kubernetes, e
contratar quem conheça Swarm é difícil.

*Opinião profissional, com discordância legítima:* para 2 a 10 servidores, com uma equipe
pequena e sem exigência de autoscaling, **Swarm ainda é a decisão tecnicamente mais racional** —
entrega 80% do valor com 15% da complexidade. Mas é uma aposta em tecnologia estagnada, e você
deve tomá-la com os olhos abertos. Se houver perspectiva de crescer o time ou migrar para
nuvem, vá direto ao Kubernetes.

---

## 3. Swarm em 20 minutos

```bash
# No primeiro nó (manager)
docker swarm init --advertise-addr 192.168.1.10
# ele imprime um comando 'docker swarm join --token ...'

# Nos demais nós (workers)
docker swarm join --token SWMTKN-1-xxx 192.168.1.10:2377

docker node ls
```

`compose.yaml` para stack (a seção `deploy:` passa a ser respeitada):

```yaml
services:
  api:
    image: ghcr.io/org/api@sha256:abc...
    networks: [interna]
    deploy:
      replicas: 3
      update_config:
        parallelism: 1           # uma réplica por vez
        delay: 10s
        order: start-first       # sobe a nova antes de derrubar a antiga → sem queda
        failure_action: rollback
      rollback_config:
        parallelism: 0           # rollback de todas de uma vez
      restart_policy:
        condition: on-failure
        max_attempts: 3
      resources:
        limits: { cpus: "1.0", memory: 512M }
      placement:
        constraints: [node.role == worker]
        preferences: [spread: node.labels.zona]
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1:3000/saude"]
      interval: 10s
      start_period: 30s
    secrets: [db_senha]

secrets:
  db_senha:
    external: true      # criado com: docker secret create db_senha arquivo.txt

networks:
  interna:
    driver: overlay
    attachable: true
```

```bash
docker secret create db_senha ./senha.txt
docker stack deploy -c compose.yaml minha-app
docker service ps minha-app_api           # onde cada réplica está rodando
docker service logs -f minha-app_api
```

**O que o Swarm dá de graça:** *routing mesh* (qualquer nó aceita a conexão e a encaminha à
réplica correta), rede overlay cifrada opcional, segredos cifrados em repouso e em trânsito,
rolling update com rollback automático em falha.

**O que ele não dá:** autoscaling, controle de admissão, CRDs, ecossistema.

---

## 4. Kubernetes — o mínimo para atravessar a ponte

O que muda no vocabulário:

| Docker/Compose | Kubernetes | Observação |
|---|---|---|
| container | **container** (dentro de um Pod) | |
| — | **Pod** | Menor unidade agendável: 1+ containers compartilhando rede e volumes |
| serviço do Compose | **Deployment** | Gerencia réplicas de Pods e o rolling update |
| `deploy.replicas` | **ReplicaSet** | Gerenciado pelo Deployment |
| nome DNS do serviço | **Service** | IP e DNS estáveis para um conjunto de Pods |
| `ports:` | **Service** + **Ingress** | Ingress termina TLS e roteia por host/caminho |
| volume nomeado | **PersistentVolumeClaim** | Provisionado por uma StorageClass |
| `environment:` | **ConfigMap** | Configuração não sensível |
| `secrets:` | **Secret** | ⚠️ base64, **não** cifrado por padrão em etcd |
| `healthcheck` | **livenessProbe** + **readinessProbe** + **startupProbe** | Três, não uma |
| `deploy.resources` | `resources.requests` / `.limits` | `requests` guia o agendamento |
| `restart:` | `restartPolicy` (sempre, num Deployment) | |
| rede do projeto | **Namespace** + NetworkPolicy | Namespace não isola rede por si só |
| `docker compose up` | `kubectl apply -f` | Declarativo e reconciliado |

Equivalente mínimo do nosso serviço:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  selector:
    matchLabels: { app: api }
  template:
    metadata:
      labels: { app: api }
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        seccompProfile: { type: RuntimeDefault }
      containers:
        - name: api
          image: ghcr.io/org/api@sha256:abc...
          ports: [{ containerPort: 3000 }]
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef: { name: db, key: url }
          resources:
            requests: { memory: "128Mi", cpu: "100m" }
            limits:   { memory: "512Mi", cpu: "1000m" }
          livenessProbe:
            httpGet: { path: /vivo, port: 3000 }
            initialDelaySeconds: 15
          readinessProbe:
            httpGet: { path: /saude, port: 3000 }
            periodSeconds: 5
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities: { drop: ["ALL"] }
          volumeMounts: [{ name: tmp, mountPath: /tmp }]
      volumes: [{ name: tmp, emptyDir: {} }]
---
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector: { app: api }
  ports: [{ port: 80, targetPort: 3000 }]
```

Note quantos dos conceitos são **os mesmos** que você já aprendeu: usuário não-root,
capabilities descartadas, raiz somente leitura, limites de recurso, sondas. O Kubernetes muda a
sintaxe e o escopo, não os fundamentos.

### `requests` × `limits` — a distinção que causa incidentes

- **`requests`**: o que o scheduler reserva. Se você pedir menos do que usa, o nó fica
  superprovisionado e tudo degrada junto.
- **`limits`**: o teto. Memória acima do limite = OOM kill. CPU acima = **throttling**, não
  morte.

*Prática de campo consolidada:* defina `requests` de memória **iguais** aos `limits` (memória não
é compressível; ficar sem ela mata) e **não defina limite de CPU** em cargas latência-sensíveis
(CPU é compressível; o limite só introduz throttling desnecessário quando há folga na máquina).
Isso é debatido, mas a experiência com throttling em produção pesa a favor.

### Distribuições leves, para aprender e para a borda

```bash
# k3s — Kubernetes completo em um binário, ideal para homelab e edge
curl -sfL https://get.k3s.io | sh -
sudo k3s kubectl get nodes

# kind — cluster dentro de containers Docker, ótimo para CI e estudo
kind create cluster --name estudo
kubectl get nodes

# minikube — VM local
minikube start
```

---

## 5. O caminho de migração, na ordem que funciona

1. **Containerize corretamente.** Sem estado na camada de escrita, configuração por ambiente,
   sinais tratados, healthchecks reais, log em stdout. **Este material inteiro é este passo.**
2. **Opere com Compose num servidor.** Descubra os problemas reais de operação com uma
   ferramenta simples.
3. **Automatize o build e a publicação.** CI produzindo imagem assinada, referenciada por
   digest.
4. **Externalize o estado.** Banco gerenciado ou com replicação própria, sessão em Redis,
   arquivos em armazenamento de objetos.
5. **Só então** avalie orquestração — e escolha com base em quantos dos problemas da seção 1
   você realmente tem.

**Pular direto do passo 1 para o 5 é o erro clássico**, e é caro: você acaba depurando
Kubernetes e a aplicação ao mesmo tempo, sem saber qual dos dois está errado.

*Opinião profissional:* uma aplicação bem containerizada roda em qualquer orquestrador com
esforço pequeno. Uma aplicação mal containerizada não é salva por orquestrador nenhum — só fica
mal orquestrada, em escala.

---

## 6. Sinais de que chegou a hora (e de que não chegou)

**Chegou a hora quando:**
- Uma máquina não aguenta mais a carga, e escalar verticalmente ficou caro demais.
- A indisponibilidade da máquina única passou a ser inaceitável para o negócio.
- Há várias equipes disputando a mesma infraestrutura e você precisa de isolamento e quota.
- A carga varia muito e pagar pelo pico o tempo todo saiu caro.
- Você já opera dezenas de serviços e o `compose.yaml` virou incontrolável.

**Não chegou quando:**
- "Todo mundo usa." (Todo mundo tem problemas que você não tem.)
- "Fica bem no currículo." (Legítimo como motivação pessoal; ruim como decisão de arquitetura —
  e vale dizer isso em voz alta na reunião.)
- Você tem 3 serviços e 100 usuários.
- Ninguém na equipe conhece Kubernetes e não há orçamento para aprender direito.

**O custo escondido:** um cluster Kubernetes exige alguém cuidando de atualizações, CNI, CSI,
ingress, certificados, RBAC, políticas, observabilidade e do próprio cluster. Em nuvem
gerenciada (EKS/GKE/AKS) a fatia de controle sai por volta de US$ 70–100/mês por cluster,
**além** dos nós — e a maior parte do custo continua sendo o tempo de gente.

---

## 7. Alternativas que dispensam orquestrador

Nem toda escala precisa de Kubernetes:

| Opção | Modelo | Bom para |
|---|---|---|
| **Fly.io, Railway, Render** | PaaS sobre container | Aplicações pequenas e médias, sem operação |
| **AWS App Runner / Google Cloud Run** | Container serverless | Cargas HTTP com tráfego variável; escala a zero |
| **AWS ECS + Fargate** | Orquestrador gerenciado, sem Kubernetes | Quem já está na AWS e quer simplicidade |
| **Compose + vários servidores + proxy** | Manual | Cargas previsíveis, equipe pequena |
| **Nomad** | Orquestrador simples | Cargas mistas (containers, binários, VMs) |

**Cloud Run e ECS/Fargate merecem consideração séria antes do Kubernetes.** Você entrega a
mesma imagem OCI, paga por uso e não opera plano de controle nenhum. Para muitas equipes, essa é
a resposta certa — e é frequentemente pulada por inércia cultural.

---

## Autoteste

1. Cite quatro problemas que a orquestração resolve e o Compose não.
2. Qual é a "pergunta certa" antes de adotar Kubernetes, e por que ela é melhor que "devo usar
   Kubernetes?"
3. Por que o Swarm é tecnicamente adequado para 2–10 servidores, e por que ainda assim pode ser
   má escolha?
4. Traduza para Kubernetes: serviço do Compose, volume nomeado, healthcheck, rede do projeto.
5. Qual é a diferença entre `requests` e `limits`, e por que a recomendação difere entre memória
   e CPU?
6. Descreva os cinco passos de migração na ordem correta, e explique o custo de pular o 2 e o 4.
7. Cite três sinais de que **não** chegou a hora de adotar Kubernetes.
8. Por que uma aplicação mal containerizada não é salva por orquestrador nenhum?
9. Quando Cloud Run ou ECS/Fargate seriam a resposta certa em vez de um cluster?
10. O que o Swarm dá de graça que você teria de montar à mão com Compose?
