# DNS interno: como containers se encontram

> **Nível:** intermediário
> **Última verificação:** 18/08/2026

## 1. O problema

Sua API precisa falar com o Postgres. Qual endereço usar?

- `localhost`? Não — dentro do container, `localhost` é o **próprio container**.
- `172.17.0.3`? Não — o IP muda a cada recriação do container.
- IP do host? Frágil, e dá a volta desnecessária por fora.

A resposta é **o nome do serviço**:

```yaml
DATABASE_URL: postgresql+asyncpg://appuser:senha@db:5432/appdb
                                                 ^^
                                    o nome do serviço no compose
```

## 2. Como funciona

Toda rede criada pelo usuário (e toda rede do Compose é criada pelo usuário) tem
um **servidor DNS embutido** em `127.0.0.11`, dentro do namespace de rede de cada
container.

```
container "api" pergunta:   "quem é db?"
        │
        ▼
   127.0.0.11  (DNS embutido do Docker)
        │
        ▼
   "db é 172.18.0.3"
```

Você pode ver isso de dentro de qualquer container:

```bash
docker compose exec api cat /etc/resolv.conf
# nameserver 127.0.0.11

docker compose exec api getent hosts db
# 172.18.0.3       db
```

O DNS resolve, na mesma rede:

| Nome | Resolve? |
|---|---|
| nome do **serviço** (`db`) | sim — é o que você deve usar |
| `container_name` explícito | sim |
| **alias** definido em `networks.<rede>.aliases` | sim |
| nome do container gerado (`projeto-db-1`) | sim |
| serviço em **outra** rede à qual o container não pertence | **não** |

## 3. A porta é sempre a INTERNA

O erro conceitual mais comum do módulo:

```yaml
services:
  api:
    environment:
      # ❌ ERRADO — 5433 é a porta do HOST
      DATABASE_URL: postgresql://user:senha@db:5433/app
  db:
    image: postgres:17-alpine
    ports:
      - "5433:5432"     # host 5433 -> container 5432
```

O mapeamento `5433:5432` existe para o **host**. Entre containers, o tráfego não
passa por ele — vai direto pela rede interna, na porta em que o Postgres
realmente escuta: **5432**.

```yaml
      # ✅ CERTO
      DATABASE_URL: postgresql://user:senha@db:5432/app
```

Corolário importante: **você não precisa de `ports:` para containers
conversarem entre si.** O `ports:` serve exclusivamente para acesso a partir do
host. Um banco sem `ports:` continua perfeitamente acessível pela API — e fica
inacessível para a sua LAN, que é o desejado.

## 4. Isolamento por rede

Estar no mesmo compose não basta — é preciso estar na **mesma rede**:

```yaml
services:
  proxy:
    networks: [borda, interna]
  api:
    networks: [interna]
  db:
    networks: [interna]

networks:
  borda:
  interna:
    internal: true
```

| De → Para | Resolve? |
|---|---|
| proxy → api | sim (ambos em `interna`) |
| api → db | sim |
| proxy → db | sim (ambos em `interna`) |

Se o `proxy` estivesse **só** em `borda`, `proxy → db` falharia com
`bad address 'db'` — que é exatamente o efeito desejado quando se quer segmentar.

`internal: true` remove o gateway padrão: containers nessa rede não têm rota
para a internet. Ótimo para banco; problema para um serviço que precise buscar
algo externo — esse precisa também de uma rede não-interna.

## 5. Alcançar o host a partir do container

Situação comum em homelab: o container precisa falar com um serviço que roda
**no host** (o MotionEye instalado nativamente, por exemplo).

```yaml
services:
  api:
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

Depois, `http://host.docker.internal:8765` alcança a porta 8765 do host.

No macOS e no Windows, `host.docker.internal` já existe por padrão. **No Linux,
não** — é preciso a linha `extra_hosts` acima. É uma diferença que confunde
muita gente que segue tutorial escrito para macOS.

## 6. Aliases e múltiplos nomes

```yaml
services:
  db:
    networks:
      interna:
        aliases:
          - postgres
          - banco-principal
```

Agora `db`, `postgres` e `banco-principal` resolvem para o mesmo container.

Útil em migração: você renomeia o serviço mas mantém o nome antigo como alias,
e nada quebra enquanto você atualiza as referências.

## 7. Balanceamento por DNS com réplicas

```bash
docker compose up -d --scale api=3
```

O nome `api` passa a resolver para **três** IPs. O DNS do Docker devolve a lista
em ordem rotativa — um balanceamento rudimentar.

Duas limitações honestas:

1. **Clientes fazem cache de DNS.** Muita biblioteca resolve uma vez e reusa a
   conexão para sempre, anulando o rodízio.
2. **Não há verificação de saúde no DNS.** Um container `unhealthy` continua na
   lista até ser removido.

Para balanceamento de verdade, use um proxy reverso (Caddy, nginx, Traefik) na
frente. O DNS round-robin serve para casos simples e tolerantes a falha.

E note: com `--scale`, você **não pode** ter `ports:` fixo no serviço — três
containers não cabem na mesma porta do host. Outro motivo para o proxy.

## 8. Diagnosticar problemas de DNS

Sua imagem de produção não tem ferramentas de rede (e não deve ter). Anexe um
container que tenha:

```bash
docker run --rm -it --network container:<nome-do-container-alvo> nicolaka/netshoot
```

Dentro dele, você está na **mesma pilha de rede** do alvo:

```bash
getent hosts db          # resolve?
dig db                   # detalhe da resolução
nc -zv db 5432           # a porta responde?
curl -v http://api:8000/health
ip addr                  # qual IP eu tenho
tcpdump -i any port 5432 # ver o tráfego
```

Sem o netshoot, o mínimo com o que a maioria das imagens tem:

```bash
docker compose exec api getent hosts db        # resolve o nome
docker compose exec api python -c \
  "import socket;print(socket.gethostbyname('db'))"
```

E para ver a topologia:

```bash
docker network ls
docker network inspect <projeto>_interna
# a seção "Containers" lista quem está conectado e com que IP
```

## 9. Os cinco porquês

1. **Por que usar o nome e não o IP?** Porque o IP muda a cada recriação.
2. **Por que o IP muda?** Porque é atribuído dinamicamente pelo IPAM ao criar o
   container, do pool da rede.
3. **Por que não fixar o IP?** Dá para fixar, mas você passa a gerenciar
   alocação na mão, e qualquer conflito impede o container de subir. Nome é mais
   robusto.
4. **Por que o Docker resolve nomes sozinho, em vez de usar `/etc/hosts`?** Ele
   já tentou: o mecanismo antigo, `--link`, escrevia em `/etc/hosts`. O problema
   é que o arquivo é escrito na **criação** — se o container de destino for
   recriado com outro IP, a entrada fica errada e ninguém atualiza.
5. **Por que DNS resolve isso?** Porque a resolução acontece **a cada consulta**,
   refletindo o estado atual. **Parada legítima: decisão de arquitetura, e a
   razão de `--link` ser legado desde 2016.**

## 10. Erros que você provavelmente vai cometer

| Mensagem | Causa raiz | Correção |
|---|---|---|
| `could not translate host name "db"` | serviços em redes diferentes, ou nome errado | conferir `networks:`; usar o nome do **serviço** |
| `bad address 'db'` | bridge padrão, sem DNS | usar Compose ou rede criada |
| `connection refused` com nome resolvendo | porta errada (usou a do host) | usar a porta **interna** |
| Funciona do host, não de outro container | usou `localhost` no container | `localhost` é o próprio container |
| `host.docker.internal` não resolve no Linux | não existe por padrão | `extra_hosts: ["host.docker.internal:host-gateway"]` |
| `--scale` falha | `ports:` fixo com várias réplicas | remover `ports:` e usar proxy |
| Tráfego não balanceia entre réplicas | cliente faz cache de DNS | proxy reverso na frente |

## 11. Autoteste

1. Por que `localhost` não serve para um container falar com outro?
2. Se o compose mapeia `"5433:5432"`, qual porta a API deve usar?
3. Preciso de `ports:` para a API falar com o banco? Justifique.
4. Dois serviços no mesmo compose não se enxergam. Primeira coisa a verificar?
5. Como um container alcança um serviço rodando no host, no Linux?
6. Duas limitações do balanceamento por DNS.
7. Como depurar rede numa imagem sem `curl` nem `dig`?
8. Por que `--link` foi abandonado em favor do DNS interno?

---
[← modos de rede](bridge-host-none.md) · [exercício →](exercicio.md) · [índice](../00-indice.md)
