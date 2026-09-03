# 75 · Armadilhas, mitos e más práticas

`Nível: todos` · `Última atualização: 11/08/2026`

O catálogo dos erros que todo mundo comete, por que persistem e como sair de cada um. Organizado
por frequência com que aparecem na vida real.

---

## Parte 1 — Os oito erros que travam o iniciante

### 1. `-p` invertido → "connection refused"

```bash
docker run -p 80:8080 nginx    # ❌ nginx escuta na 80
docker run -p 8080:80 nginx    # ✅
```
`-p` é **`host:container`**, de fora para dentro. Diagnóstico: `docker port NOME` mostra o
mapeamento real; `docker logs` mostra em que porta o app subiu.

### 2. App em `127.0.0.1` dentro do container → "connection refused" com container saudável

Dentro do container, `127.0.0.1` é o loopback **dele**, não a sua máquina. O app precisa escutar
em `0.0.0.0`.

| Framework | Correção |
|---|---|
| Flask | `app.run(host="0.0.0.0")` |
| Express/Node | `app.listen(3000, "0.0.0.0")` |
| Vite | `--host` (ou `server.host: true`) |
| Rails | `-b 0.0.0.0` |
| .NET | `ASPNETCORE_URLS=http://0.0.0.0:8080` |
| Django | `runserver 0.0.0.0:8000` |

Diagnóstico: `docker exec NOME ss -tlnp` — se aparece `127.0.0.1:porta`, achou.

### 3. Container sai na hora com `Exited (0)`

```bash
docker run -d ubuntu     # STATUS: Exited (0)
```
O container vive enquanto o PID 1 viver. `ubuntu` tem `CMD ["bash"]`; sem terminal, o bash lê
EOF e termina. Dê a ele um processo que fique de pé, ou `-it` para um terminal. Diagnóstico:
`docker logs NOME`; `docker inspect --format '{{.State.ExitCode}}' NOME`.

### 4. Editar arquivo dentro do container e perder tudo

```bash
docker exec -it app vi /app/config.json    # some no docker rm
```
Container não é servidor. Edite no host e reconstrua, ou use bind mount no desenvolvimento.

### 5. `docker compose down -v` apagou o banco

O `-v` remove volumes. Sem confirmação. Use `docker compose down` no dia a dia; reserve `-v`
para quando você **quer** zerar. E faça backup antes.

### 6. Build refaz tudo a cada mudança de código

Ordem errada no Dockerfile. `COPY package*.json` **antes** de `COPY . .` e do `npm ci`. Ver
[17-dockerfile-e-build.md](17-dockerfile-e-build.md#3-o-cache-na-prática).

### 7. Arquivos do container pertencem ao root no host

O processo rodou como root e escreveu num bind mount. Rode com
`--user "$(id -u):$(id -g)"`, ou crie um usuário com o UID certo na imagem. Ver
[15-armazenamento-e-volumes.md](15-armazenamento-e-volumes.md#3-bind-mounts-e-o-problema-de-permissão).

### 8. `docker stop` demora exatos 10 segundos

Sinal de que o `SIGTERM` está sendo ignorado. Duas causas: forma shell no `CMD`
(`CMD node app.js` em vez de `CMD ["node","app.js"]`), ou o app não trata `SIGTERM` sendo PID 1.
Use a forma exec e `tini`/`--init`.

---

## Parte 2 — Os mitos, e a realidade

| Mito | Realidade |
|---|---|
| "Container é uma VM leve" | Não há virtualização nem kernel próprio. É processo restrito. Ver [10](10-fundamentos.md) |
| "Container é seguro por padrão" | O padrão é razoável, não é isolamento forte. Kernel compartilhado |
| "Preciso de microserviços para usar Docker" | Container empacota; microserviço é decisão organizacional. Independentes |
| "`latest` é a versão mais recente" | É só a tag padrão, e é reescrita a cada push. Perigosa em produção |
| "Alpine é sempre melhor por ser menor" | Para Python quebra wheels e força compilar; use `slim`. Ver [12](12-imagens-e-camadas.md) |
| "Rodei `rm` do segredo, então sumiu" | A camada anterior o mantém. Recuperável do registry |
| "cgroups garantem isolamento de desempenho" | Só de recursos contabilizáveis. Cache L3 e barramento vazam. Ver [60](60-teoria-avancada.md) |
| "Docker vai morrer por causa do Wasm/Kubernetes" | Wasm ocupa nicho; K8s usa containers OCI por baixo. Coexistem |
| "Container não tem estado" | Pode ter — em volume. Não deve ter na camada de escrita |
| "Se passa no scanner, está seguro" | Scanner vê CVE de versão, não configuração errada nem lógica |
| "`EXPOSE` publica a porta" | É documentação. Quem publica é `-p` |
| "Preciso de Kubernetes para produção" | Para um servidor, Compose é adequado. Ver [25](25-orquestracao.md) |

---

## Parte 3 — Más práticas que persistem (e por quê)

### Rodar como root

**Por que persiste:** funciona, e as imagens oficiais frequentemente vêm assim por
compatibilidade. **Por que é ruim:** amplia o impacto de qualquer escape; cria arquivos com dono
errado. **Correção:** `USER` não-root, sempre.

### `:latest` em produção

**Por que persiste:** é o padrão, e "funciona na minha máquina". **Por que é ruim:** deploy
imprevisível, rollback impossível, ataque de reescrita de tag. **Correção:** tag semântica +
digest.

### Um `RUN` por linha

```dockerfile
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*
```
**Por que persiste:** parece mais legível. **Por que é ruim:** camadas extras, cache do `update`
desatualizado (erro 404), o `rm` não reduz nada. **Correção:** encadeie com `&&` na mesma
camada.

### Instalar mais do que precisa

**Por que persiste:** conveniência ("vou precisar de `vim` para depurar"). **Por que é ruim:**
cada pacote é superfície de ataque e CVE. **Correção:** base mínima; depure com `nsenter` ou
container efêmero anexado, não com ferramentas embutidas.

### `--privileged` como muleta

**Por que persiste:** resolve "permission denied" na hora. **Por que é ruim:** é root no host
sem barreira. **Correção:** `--cap-add` específico, `--device` específico. Ver
[20-seguranca.md](20-seguranca.md).

### Montar o socket do Docker

**Por que persiste:** Portainer, Watchtower e agentes de CI pedem. **Por que é ruim:** root no
host. **Correção:** proxy de socket com allow-list, ou API por TLS/SSH.

### Segredo em variável de ambiente

**Por que persiste:** é o jeito mais fácil e todo tutorial faz. **Por que é ruim:** aparece em
`inspect`, `/proc/PID/environ`, logs de crash, e é herdado por filhos. **Correção:** arquivo em
tmpfs (`secrets:`) ou gerenciador de segredos.

### Não limitar recurso

**Por que persiste:** funciona até o dia em que não funciona. **Por que é ruim:** um vazamento
derruba o host inteiro. **Correção:** `--memory` e `--pids-limit` em todo container de produção.

### Não limitar log

**Por que persiste:** o padrão não avisa. **Por que é ruim:** enche o disco em semanas, e o
sintoma parece não ter relação. **Correção:** `max-size`/`max-file` no `daemon.json`.

### Um processo de banco em bind mount

**Por que persiste:** parece prático poder ver os arquivos. **Por que é ruim:** copy-on-write e
semântica de `fsync` degradam ou corrompem. **Correção:** volume nomeado; backup por `pg_dump`.

---

## Parte 4 — Armadilhas de plataforma

### macOS / Windows

| Armadilha | Correção |
|---|---|
| I/O de disco lento em bind mount | VirtioFS (mac); no WSL, projeto em `~`, nunca em `/mnt/c` |
| RAM "sumindo" | A VM do Docker reserva RAM fixa; ajuste nas Settings |
| `host.docker.internal` não existe no Linux | `--add-host=host.docker.internal:host-gateway` |
| Imagem ARM64 não roda / roda emulada e lenta | `--platform linux/amd64`, ou build multi-arch |
| `--network host` não funciona como esperado | "host" é a VM, não a sua máquina |

### Linux

| Armadilha | Correção |
|---|---|
| `permission denied` no socket | Entrar no grupo `docker` e **relogar** |
| Bind mount bloqueado no Fedora/RHEL | SELinux: use `:z`/`:Z` |
| Sub-rede do Docker colide com a VPN | Mudar `bip`/`default-address-pools` no `daemon.json` |
| `ufw` não protege porta publicada | `-p 127.0.0.1:...`, ou cadeia `DOCKER-USER` |
| CRLF quebra script no container | `dos2unix`; `.gitattributes` com `eol=lf` |

---

## Parte 5 — Referência rápida de diagnóstico

```bash
# Por que o container morreu?
docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}} {{.State.Error}}' NOME
docker logs --tail 100 NOME

# Códigos de saída
# 0=terminou (não era serviço) · 1=erro do app · 125=erro do Docker
# 126=não executável · 127=comando não encontrado
# 137=SIGKILL (quase sempre OOM) · 139=SIGSEGV · 143=SIGTERM (parada normal)

# A imagem está gorda?
docker history IMAGEM
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock wagoodman/dive IMAGEM

# O disco encheu?
docker system df
sudo du -sh /var/lib/docker/* | sort -hr | head

# A rede não conecta?
docker port NOME
docker exec NOME ss -tlnp
docker run --rm --network container:NOME nicolaka/netshoot

# O que este container pode fazer (segurança)?
docker inspect --format 'priv={{.HostConfig.Privileged}} user={{.Config.User}}' NOME
```

---

## Parte 6 — O anti-checklist

Se você faz **qualquer** um destes, pare e corrija:

- [ ] `:latest` em produção
- [ ] Container rodando como root sem necessidade
- [ ] `--privileged` fora de um caso justificado e documentado
- [ ] Socket do Docker montado sem proxy
- [ ] Segredo em `ARG`, `ENV` ou `-e`
- [ ] Banco de dados em bind mount
- [ ] Nenhum limite de memória em produção
- [ ] Nenhum limite de tamanho de log
- [ ] Deploy por tag, não por digest
- [ ] `.dockerignore` ausente
- [ ] Imagem nunca escaneada
- [ ] Backup nunca testado com restauração real
- [ ] `docker stop` demorando 10 s (sinais não tratados)
- [ ] Porta de banco publicada em `0.0.0.0`

---

## Autoteste

1. Um container está de pé e mesmo assim dá "connection refused". Cite as duas causas mais
   prováveis e como distinguir.
2. Por que "container é uma VM leve" é falso, e qual é a consequência prática do erro?
3. Explique por que apagar um segredo num `RUN` posterior não o remove da imagem.
4. Por que Alpine é boa escolha para Go e má escolha para Python?
5. Cite três más práticas que persistem e a razão de cada uma persistir.
6. Por que `ufw deny` não protege uma porta publicada, e quais são as duas correções?
7. Exit code 137: o que é e qual comando confirma a causa?
8. Por que segredo em variável de ambiente é ruim? Cite três formas de vazamento.
9. Um `docker stop` demora 10 segundos. Quais são as duas causas e as correções?
10. Passe pelo anti-checklist e identifique quais itens se aplicam a algo que você já fez.
