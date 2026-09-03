# Checklist de hardening

> **Nível:** intermediário → avançado
> **Última verificação:** 18/08/2026

Checklist prático, ordenado por **razão custo/benefício**. Se você fizer só os
itens do nível 1, já elimina a maior parte do risco real.

---

## Nível 1 — faça sempre (custo quase zero)

- [ ] **Usuário não-root**, com UID numérico
  ```dockerfile
  USER 10001:10001
  ```
  Ver [usuário não-root](usuario-nao-root.md).

- [ ] **Imagem base mínima e com tag de suite fixa**
  ```dockerfile
  FROM python:3.12-slim-trixie     # não: python:3.12  nem  python:3.12-slim
  ```
  Tag genérica migra de distribuição sem avisar — [caso real documentado](../08-projeto-aplicado/dockerfile-fastapi-sqlalchemy.md).

- [ ] **`.dockerignore` presente**, incluindo `.env`, `secrets/`, `.git`, `*.pem`

- [ ] **Nenhum segredo em `ENV`, `ARG` ou `environment:`** — use `secrets:`

- [ ] **Não publicar portas desnecessárias**
  ```yaml
  ports: ["127.0.0.1:8000:8000"]   # e nada de ports: no banco
  ```
  Lembre: `ufw deny` **não** protege porta publicada pelo Docker.

- [ ] **Multi-stage**, para o compilador não chegar ao runtime

- [ ] **Healthcheck que testa a dependência**, não um 200 fixo

- [ ] **`CMD` em forma exec** (array JSON), para o `SIGTERM` chegar

- [ ] **Versões fixadas** no `requirements.txt` / `package-lock.json`

---

## Nível 2 — endurecimento (custo baixo, exige testar)

- [ ] **Filesystem raiz somente-leitura**
  ```yaml
  read_only: true
  tmpfs:
    - /tmp:size=64m
  ```
  Suba, veja o que quebra, declare em `tmpfs` só o necessário.

- [ ] **Sem escalada de privilégio**
  ```yaml
  security_opt:
    - no-new-privileges:true
  ```
  Bloqueia o truque clássico via binário `setuid`. Custo: nenhum, na prática.

- [ ] **Capabilities zeradas**
  ```yaml
  cap_drop: [ALL]
  # cap_add: [NET_BIND_SERVICE]   # só se REALMENTE precisar de porta < 1024
  ```
  O Docker concede ~14 capabilities por padrão, incluindo `CAP_NET_RAW` (permite
  forjar pacote e fazer ARP spoofing na rede do Docker). Quase nenhuma
  aplicação web usa qualquer uma delas.

- [ ] **Limites de recurso**
  ```yaml
  deploy:
    resources:
      limits: {cpus: "1.0", memory: 512m}
  ```
  Sem limite, um container consome toda a RAM e o OOM killer mata **pelo score** —
  frequentemente o banco, não o culpado.

- [ ] **Segmentação de rede**
  ```yaml
  networks:
    interna: {internal: true}
  ```

- [ ] **`restart: unless-stopped`**, não `always`

- [ ] **Limite de log** (evita disco cheio por log)
  ```yaml
  logging:
    driver: json-file
    options: {max-size: "10m", max-file: "3"}
  ```

---

## Nível 3 — para dado sensível (custo real)

- [ ] **Imagem pinada por digest**
  ```dockerfile
  FROM python:3.12-slim-trixie@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a
  ```
  Máxima reprodutibilidade; custo: atualizar o digest na mão a cada correção.

- [ ] **Scan de vulnerabilidade no CI**
  ```bash
  trivy image --severity HIGH,CRITICAL --exit-code 1 minha-api:1.0
  ```

- [ ] **Scan de segredo no repositório**
  ```bash
  gitleaks detect -s . -v
  ```

- [ ] **Imagem distroless ou `scratch`** — sem shell, sem gerenciador de pacotes.
      Custo: sem `docker exec ... sh` para depurar.

- [ ] **Perfil seccomp/AppArmor customizado** — só se você souber exatamente o
      que está fazendo; o perfil padrão do Docker já bloqueia ~44 syscalls.

- [ ] **Rootless Docker** ou Podman

- [ ] **Assinatura de imagem** (cosign/sigstore), para garantir procedência

- [ ] **Gerenciador de segredos externo** (Vault, SOPS, gerenciador da nuvem)

---

## O que verificar num container já rodando

```bash
# É root?
docker compose exec api id
# esperado: uid=10001

# Filesystem é read-only?
docker compose exec api touch /teste
# esperado: Read-only file system

# Quais capabilities sobraram?
docker inspect <container> --format '{{.HostConfig.CapDrop}} {{.HostConfig.CapAdd}}'

# Tem segredo no ambiente?
docker inspect <container> | grep -iE 'password|secret|token|key'
# esperado: nada

# Que portas estão publicadas, e em qual interface?
docker ps --format 'table {{.Names}}\t{{.Ports}}'
# procure por 0.0.0.0 — cada um é uma decisão consciente?

# Está privilegiado? (deve ser false)
docker inspect <container> --format '{{.HostConfig.Privileged}}'
```

---

## Anti-padrões: nunca faça

| Anti-padrão | Por quê | Alternativa |
|---|---|---|
| `privileged: true` | desliga praticamente todo o isolamento | `devices:` ou `cap_add:` específico |
| Montar `/var/run/docker.sock` | acesso ao socket = **root no host** | proxy de socket com allowlist, ou repensar o desenho |
| `--network host` por conveniência | perde isolamento de porta | bridge com `ports:` |
| `latest` em produção | build não reprodutível | tag de versão ou digest |
| `curl \| sh` no Dockerfile | executa código não verificado | baixar, verificar checksum, executar |
| Segredo em `ENV` | grava na imagem para sempre | `secrets:` |
| Rodar como root "porque é mais fácil" | escala qualquer falha para root | `USER` + `chown` correto |
| `chmod 777` para resolver permissão | qualquer processo escreve | `chown` para o UID certo |

O caso do `docker.sock` merece ênfase: montar o socket dentro de um container
(comum em ferramentas de CI e em painéis como Portainer) dá àquele container o
poder de criar outro container privilegiado montando `/` do host. **É equivalente
a dar root.** Se precisar mesmo, use um proxy de socket com allowlist de
endpoints.

---

## Rotina de manutenção

| Frequência | Ação |
|---|---|
| A cada build | scan de vulnerabilidade |
| Semanal | `docker compose pull` + recriar (correções de base) |
| Mensal | revisar portas publicadas e volumes órfãos |
| Mensal | **testar a restauração de um backup** |
| Trimestral | revisar versões pinadas e digests |

A rotina mensal do backup é a que mais gente pula e a que mais dói. Um backup
que nunca foi restaurado não é um backup — é esperança.

---

## Aplicado aos seus projetos

| Item | FlixARD | Sistema financeiro | CFTV |
|---|---|---|---|
| Não-root | sim | sim | limitado (precisa de `/dev/video0`) |
| `read_only` | opcional | **sim** | não (grava vídeo) |
| `cap_drop: ALL` | sim | **sim** | não (precisa acessar dispositivo) |
| Rede interna | sim | **sim** | sim |
| Secrets | senha do banco | **tudo** | senha da interface |
| Backup automático | recomendado | **obrigatório** | rotacionar gravações |
| Portas publicadas | só 443 (proxy) | só loopback | só loopback |
| Limites de recurso | sim (transcode) | sim | sim (câmera + transcode) |

O CFTV é o caso em que o hardening precisa ceder: acesso a dispositivo é
requisito funcional. A resposta correta não é `privileged: true` — é `devices:`
com a lista exata, isolando a exceção no menor escopo possível.

---

## Autoteste

1. Três itens do nível 1 que você aplicaria hoje, em 10 minutos.
2. Por que `cap_drop: ALL` raramente quebra uma aplicação web?
3. O que `no-new-privileges` impede, concretamente?
4. Por que montar `docker.sock` equivale a dar root no host?
5. Qual o custo real de `read_only: true`, e como descobrir o que declarar?
6. Sem limite de memória, por que o banco costuma ser a vítima?
7. Por que `chmod 777` nunca é a solução de permissão?
8. Qual item da rotina de manutenção é o mais pulado, e por que dói?

---
[← secrets](secrets-e-variaveis-sensiveis.md) · [módulo 07: debugging →](../07-debugging/logs-e-exec.md) · [índice](../00-indice.md)
