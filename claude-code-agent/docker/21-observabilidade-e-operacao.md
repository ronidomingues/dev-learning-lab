# 21 · Observabilidade e operação

`Nível: intermediário → avançado` · `Última atualização: 11/08/2026`

Rodar container é fácil. Operar container é a especialidade. Este arquivo é sobre o que
acontece depois do primeiro deploy.

---

## 1. Logs

### A regra fundamental

> **Container escreve log em `stdout`/`stderr`. Ponto.**

Não em arquivo. Não em syslog dentro do container. Não com rotação própria. O processo emite; a
plataforma decide onde aquilo vai parar. Isso é o *factor XI* dos Twelve-Factor App, e vale
porque:

- container é efêmero — arquivo dentro dele some com ele;
- arquivo de log dentro do container **enche o disco do host** sem que ninguém veja;
- a plataforma (Docker, Kubernetes, ECS) já sabe coletar, rotacionar e agregar stdout.

### Drivers de log

```bash
docker system info | grep "Logging Driver"
```

| Driver | `docker logs` funciona? | Uso |
|---|---|---|
| `json-file` (padrão) | sim | Desenvolvimento e servidor único. **Sem limite por padrão** |
| `local` | sim | Formato binário, mais eficiente, **com rotação por padrão** |
| `journald` | sim | Integra com `journalctl`, retenção do systemd |
| `syslog` | **não** | Envio a servidor central |
| `fluentd` / `gelf` | **não** | Agregação (EFK, Graylog) |
| `awslogs` / `gcplogs` | **não** | Nuvem |
| `none` | **não** | Quando o app já envia por outro caminho |

> **A configuração que todo servidor deveria ter** — sem ela, um container falante enche o
> disco em semanas, e o sintoma aparece como "aplicação sem relação nenhuma parou de funcionar":

```json
// /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
```
```bash
sudo systemctl restart docker    # vale para containers criados DEPOIS
```

```bash
# Achar o log que encheu o disco
sudo find /var/lib/docker/containers -name "*-json.log" -size +100M -exec ls -lh {} \;
# Zerar um log sem parar o container (medida de emergência)
sudo truncate -s 0 /var/lib/docker/containers/<ID>/<ID>-json.log
```

### Log estruturado

Uma linha JSON por evento, com campos consistentes. Isso transforma log em dado consultável.

```javascript
console.log(JSON.stringify({
  ts: new Date().toISOString(),
  nivel: 'info',
  msg: 'requisição',
  rota: 'GET /api/pedidos',
  status: 200,
  ms: 42,
  trace_id: req.headers['x-trace-id'],   // correlação entre serviços
}));
```

Regras que evitam retrabalho:

- **Um evento por linha.** Stack trace multi-linha quebra a correlação; serialize a pilha num
  campo.
- **Campos com nomes estáveis.** Renomear campo depois quebra dashboards e alertas.
- **Nunca registre segredo, token ou dado pessoal.** Log vaza com muito mais facilidade que
  banco.
- **Inclua um identificador de correlação** (`trace_id`) propagado entre serviços.

### Agregação

```yaml
# Loki + Promtail — a opção mais leve para servidor único
  loki:
    image: grafana/loki:3.0.0
    command: ["-config.file=/etc/loki/local-config.yaml"]
    volumes: [loki-dados:/loki]

  promtail:
    image: grafana/promtail:3.0.0
    volumes:
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./promtail.yaml:/etc/promtail/config.yml:ro
```

| Solução | Perfil |
|---|---|
| **Loki + Grafana** | Leve; indexa rótulos, não o conteúdo. Barato de operar |
| **Elasticsearch + Kibana** | Busca completa; caro em memória e operação |
| **OpenSearch** | Fork do Elasticsearch, licença Apache 2.0 |
| **Vector** | Coletor/roteador muito eficiente; bom substituto de Fluentd/Logstash |
| **CloudWatch / Cloud Logging** | Gerenciado; simples e caro em volume |

---

## 2. Métricas

### O que o Docker já dá

```bash
docker stats                                   # ao vivo
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
```

Para coleta automática, **cAdvisor** expõe métricas de container em formato Prometheus:

```yaml
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.49.1
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    ports: ["8081:8080"]

  prometheus:
    image: prom/prometheus:v2.53.0
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prom-dados:/prometheus
    ports: ["9090:9090"]

  grafana:
    image: grafana/grafana:11.1.0
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_SENHA:?}
    volumes: [grafana-dados:/var/lib/grafana]
    ports: ["3001:3000"]
```

`prometheus.yml`:
```yaml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: cadvisor
    static_configs: [{ targets: ["cadvisor:8080"] }]
  - job_name: aplicacao
    static_configs: [{ targets: ["api:3000"] }]
    metrics_path: /metricas
```

### As métricas que importam de verdade

| Métrica | Por que | Alerta razoável |
|---|---|---|
| `container_memory_working_set_bytes / limit` | Proximidade do OOM | > 85% por 5 min |
| `container_cpu_cfs_throttled_periods_total` | **Throttling** — latência sem CPU aparente | qualquer valor sustentado |
| Reinícios por hora | Laço de falha | > 3/h |
| Estado do healthcheck | Serviço degradado | `unhealthy` por 2 min |
| Latência p95/p99 da aplicação | O que o usuário sente | depende do SLO |
| Taxa de erro 5xx | Falha real | > 1% por 5 min |
| Espaço em `/var/lib/docker` | Falha iminente e transversal | > 80% |
| Idade da imagem em produção | Dívida de segurança | > 90 dias |

> **O throttling é a métrica mais subutilizada.** Latência alta com CPU "ociosa" quase sempre é
> throttling de cgroup: o container gasta a cota em 20 ms de um período de 100 ms e fica 80 ms
> parado. Ver [13-isolamento-namespaces-cgroups.md](13-isolamento-namespaces-cgroups.md#o-throttling-de-cpu-que-ninguém-vê).

### Os quatro sinais de ouro (SRE)

**Latência · Tráfego · Erros · Saturação.** Se você só puder instrumentar quatro coisas, sejam
essas. E meça **latência de requisições com erro separadamente** — erro rápido puxa a média para
baixo e esconde o problema.

---

## 3. Healthchecks

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/saude || exit 1
```

```bash
docker inspect --format '{{json .State.Health}}' NOME | jq
# Status: starting | healthy | unhealthy   + os últimos 5 resultados
```

### Liveness × readiness — a distinção que evita cascata

| Sonda | Pergunta | Ação em falha |
|---|---|---|
| **Liveness** (`/vivo`) | O processo está de pé e responsivo? | **Reiniciar** |
| **Readiness** (`/saude`) | Consigo atender agora? | **Tirar do balanceamento** (sem reiniciar) |

O Docker tem apenas um `HEALTHCHECK` (semântica de readiness); o Kubernetes separa os dois.
Implemente **ambos os endpoints** de qualquer forma — a distinção é da aplicação, não da
plataforma.

**Por que importa:** se o banco cair, todas as réplicas ficam "não prontas". Com liveness
apontando para o banco, **todas reiniciam ao mesmo tempo** e o boot em massa piora a situação.
Liveness deve testar só o processo; readiness testa as dependências.

**Regras de um healthcheck decente:**

- Exercite a dependência crítica (uma consulta rápida ao banco, uma escrita no disco). Um `200`
  fixo é otimismo travestido de monitoramento.
- Seja rápido (< 1 s) e barato: ele roda a cada 30 s, em todas as réplicas, para sempre.
- Use `start_period` generoso para aplicações de boot lento (JVM, migrações).
- Não faça o healthcheck depender de serviço externo de terceiro — você importa a
  indisponibilidade dele.

---

## 4. Encerramento gracioso e deploy sem queda

```
docker stop  →  SIGTERM  →  espera (10s por padrão)  →  SIGKILL
```

A sequência correta dentro da aplicação:

1. Recebe `SIGTERM`.
2. **Marca-se como não pronta** (readiness falha) — o balanceador para de mandar tráfego.
3. Espera as requisições em curso terminarem.
4. Fecha conexões de banco, descarrega buffers.
5. Sai com código 0.

```yaml
services:
  api:
    stop_grace_period: 30s      # aumente se o app precisa de mais que 10s
    stop_signal: SIGTERM
```

**Os três erros que causam 502 no deploy:**

1. **Forma shell no `CMD`** — o `/bin/sh` não repassa o sinal.
2. **App sem tratador de `SIGTERM`** — como PID 1, o sinal é simplesmente ignorado.
3. **Sair imediatamente ao receber o sinal** — as requisições em curso morrem no meio.

Rolling update manual com Compose:

```bash
docker compose pull
docker compose up -d --wait --no-deps api    # --wait espera ficar healthy
```

Para deploy realmente sem interrupção com um servidor só, é preciso duas instâncias e um proxy
que remova a antiga do rodízio antes de derrubá-la — o que o Swarm e o Kubernetes fazem
nativamente.

---

## 5. Diagnóstico de produção — o procedimento

### O container reinicia em laço

```bash
docker ps -a                                       # STATUS: Restarting (1) 3 seconds ago
docker logs --tail 100 NOME                        # funciona com o container parado
docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}} {{.State.Error}}' NOME
docker inspect --format '{{.RestartCount}}' NOME
```

| Exit code | Causa |
|---|---|
| 0 | Terminou "normalmente" — o processo não era de longa duração |
| 1 | Erro da aplicação; leia os logs |
| 137 | SIGKILL — **quase sempre OOM**; confira `OOMKilled` |
| 139 | SIGSEGV — falha de segmentação |
| 143 | SIGTERM — parada normal |
| 125/126/127 | Erro do Docker / não executável / comando não encontrado |

### O container está lento

```bash
docker stats --no-stream NOME
# CPU% perto do limite?  → throttling
# MEM próximo do limite? → GC agressivo, swap, OOM iminente

# Throttling, o dado que fecha o diagnóstico
CG=/sys/fs/cgroup/system.slice/docker-$(docker inspect -f '{{.Id}}' NOME).scope
cat $CG/cpu.stat | grep -E 'nr_throttled|throttled_usec'

# I/O de disco
docker exec NOME cat /proc/1/io
```

### A memória cresce sem parar

```bash
docker stats --no-stream NOME
docker exec NOME cat /sys/fs/cgroup/memory.current /sys/fs/cgroup/memory.max
docker exec NOME cat /sys/fs/cgroup/memory.stat | head -20
```

Cuidado com a leitura: `container_memory_usage_bytes` **inclui cache de página**, que é
recuperável. A métrica correta para "quanto o processo realmente precisa" é
`container_memory_working_set_bytes`. Muito alarme falso vem dessa confusão.

### Ninguém conecta no serviço

Ver a árvore de diagnóstico em [16-redes.md](16-redes.md#8-depuração-de-rede--o-procedimento).

---

## 6. Atualização de containers

### Manual, com Compose (recomendado)

```bash
docker compose pull
docker compose up -d --wait
docker image prune -af --filter "until=168h"
```

### Automática, com Watchtower — e por que eu não recomendaria em produção

```yaml
  watchtower:
    image: containrrr/watchtower
    volumes: [/var/run/docker.sock:/var/run/docker.sock]
    command: --interval 3600 --cleanup --label-enable
```

*Opinião profissional:* Watchtower é excelente em homelab e perigoso em produção. Ele **puxa a
tag** e reinicia — ou seja, faz deploy de código que ninguém testou, no meio da noite, sem
rollback. Além disso, exige o socket do Docker montado, com todo o risco descrito em
[20-seguranca.md](20-seguranca.md).

Em produção: atualização é uma **decisão**, disparada por pipeline, com imagem testada,
referenciada por digest e com rollback pronto.

---

## 7. Backup operacional

```bash
#!/usr/bin/env bash
# backup-diario.sh
set -euo pipefail

DESTINO=/backups/$(date +%F)
mkdir -p "$DESTINO"

# 1) Dumps lógicos dos bancos (NÃO copie arquivos de banco a quente)
docker compose exec -T db pg_dump -U app --no-owner app | gzip > "$DESTINO/db.sql.gz"

# 2) Volumes de arquivos
for v in $(docker volume ls -q --filter label=com.docker.compose.project=minhaapp); do
  docker run --rm -v "$v":/d:ro -v "$DESTINO":/b alpine \
    tar czf "/b/${v}.tgz" -C /d .
done

# 3) A configuração também é dado
tar czf "$DESTINO/config.tgz" compose.yaml nginx/ .env.example

# 4) Verificação — backup não verificado não é backup
for f in "$DESTINO"/*.tgz "$DESTINO"/*.gz; do
  gzip -t "$f" || { echo "CORROMPIDO: $f" >&2; exit 1; }
done

# 5) Fora do local (regra 3-2-1)
rclone sync "$DESTINO" remoto:backups/$(date +%F)

# 6) Retenção
find /backups -maxdepth 1 -type d -mtime +30 -exec rm -rf {} +
```

E, trimestralmente, **restaure num ambiente descartável e verifique**. Backup nunca restaurado é
esperança, não backup.

---

## 8. Uma stack de observabilidade completa

```yaml
name: observabilidade

services:
  prometheus:
    image: prom/prometheus:v2.53.0
    command:
      - --config.file=/etc/prometheus/prometheus.yml
      - --storage.tsdb.retention.time=30d
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prom-dados:/prometheus
    networks: [obs]
    restart: unless-stopped

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.49.1
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    networks: [obs]
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:v1.8.1
    command: ["--path.rootfs=/host"]
    volumes: ["/:/host:ro,rslave"]
    networks: [obs]
    restart: unless-stopped

  loki:
    image: grafana/loki:3.0.0
    volumes: [loki-dados:/loki]
    networks: [obs]
    restart: unless-stopped

  promtail:
    image: grafana/promtail:3.0.0
    volumes:
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - ./promtail.yaml:/etc/promtail/config.yml:ro
    networks: [obs]
    restart: unless-stopped

  grafana:
    image: grafana/grafana:11.1.0
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_SENHA:?}
      GF_USERS_ALLOW_SIGN_UP: "false"
    volumes: [grafana-dados:/var/lib/grafana]
    ports: ["127.0.0.1:3001:3000"]
    networks: [obs]
    restart: unless-stopped

  alertmanager:
    image: prom/alertmanager:v0.27.0
    volumes: ["./alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro"]
    networks: [obs]
    restart: unless-stopped

volumes: { prom-dados: , loki-dados: , grafana-dados: }
networks: { obs: }
```

Alertas mínimos (`alertas.yml` do Prometheus):

```yaml
groups:
  - name: containers
    rules:
      - alert: ContainerReiniciando
        expr: rate(container_start_time_seconds[15m]) > 0.003
        for: 10m
        annotations: { summary: "{{ $labels.name }} está reiniciando em laço" }

      - alert: MemoriaPertoDoLimite
        expr: container_memory_working_set_bytes / container_spec_memory_limit_bytes > 0.85
        for: 5m
        annotations: { summary: "{{ $labels.name }} acima de 85% do limite de memória" }

      - alert: CPUEstrangulada
        expr: rate(container_cpu_cfs_throttled_periods_total[5m]) > 0
        for: 10m
        annotations: { summary: "{{ $labels.name }} sofrendo throttling de CPU" }

      - alert: DiscoQuaseCheio
        expr: node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} < 0.2
        for: 5m
        annotations: { summary: "menos de 20% de disco livre" }
```

---

## 9. Rotina operacional

**Diária (automatizada):** backup com verificação · alertas ativos · espaço em disco.

**Semanal:** revisar reinícios e containers `unhealthy` · `docker system df` · revisar CVEs
novas nas imagens em produção.

**Mensal:** atualizar imagens base · testar restauração de backup · revisar alertas que
dispararam sem ação (ruído) e incidentes sem alerta (cobertura).

**Trimestral:** revisar limites de recurso contra o uso real · revisar configuração de segurança
· exercício de recuperação de desastre.

---

## Autoteste

1. Por que a aplicação deve escrever log em stdout e não em arquivo? Dê duas razões concretas.
2. Qual configuração de log todo servidor deveria ter, e o que acontece sem ela?
3. Diferencie liveness de readiness e explique a cascata que a confusão entre as duas provoca.
4. Um container tem exit code 137. Qual é a causa mais provável e qual comando confirma?
5. Latência alta, CPU aparentemente ociosa. Qual métrica você consulta e onde?
6. Qual é a diferença entre `container_memory_usage_bytes` e `container_memory_working_set_bytes`,
   e qual usar em alerta?
7. Descreva os cinco passos de um encerramento gracioso correto.
8. Cite os três erros que causam 502 durante o deploy.
9. Por que Watchtower é ótimo em homelab e ruim em produção?
10. Cite os quatro sinais de ouro e uma métrica de container para cada um.
