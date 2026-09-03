# 16 · Redes — como containers falam entre si e com o mundo

`Nível: intermediário → avançado` · `Última atualização: 11/08/2026`

Rede é onde a maioria dos problemas "estranhos" de container mora. A boa notícia: o modelo é
pequeno e, uma vez entendido, não surpreende mais.

---

## 1. O que o Docker cria por baixo

Ao instalar, o Docker cria uma bridge chamada `docker0` (uma placa de rede virtual, como um
switch de software) e uma sub-rede privada, tipicamente `172.17.0.0/16`.

```bash
ip addr show docker0
# esperado: inet 172.17.0.1/16 — este é o gateway dos containers na bridge padrão

docker network ls
# esperado: bridge, host, none (as três criadas na instalação)
```

Ao subir um container, acontece o seguinte:

```
   HOST                                       CONTAINER
 ┌──────────────────────────────┐          ┌──────────────────────┐
 │  eth0  192.168.1.50          │          │  eth0  172.17.0.2    │
 │    │                         │          │       ▲              │
 │    │  ┌──────────────────┐   │          │       │              │
 │    └──┤ NAT (iptables /  │   │          └───────┼──────────────┘
 │       │      nftables)   │   │                  │ par veth
 │       └────────┬─────────┘   │                  │
 │           ┌────▼─────┐       │                  │
 │           │ docker0  ├───────┼──────────────────┘
 │           │172.17.0.1│       │
 │           └──────────┘       │
 └──────────────────────────────┘
```

Um **par veth** é como um cabo virtual com duas pontas: uma dentro do namespace de rede do
container (aparece como `eth0`), outra no host (`veth1a2b3c`), plugada na bridge.

```bash
docker run -d --name r nginx:alpine
docker exec r ip addr show eth0        # o IP interno
ip link | grep veth                    # a outra ponta, no host
docker exec r ip route                 # default via 172.17.0.1
docker rm -f r
```

---

## 2. Os drivers de rede

| Driver | O que faz | Quando usar |
|---|---|---|
| `bridge` | Rede virtual isolada com NAT (padrão) | 95% dos casos |
| `host` | Sem namespace de rede: o container usa a pilha do host | Máximo desempenho, muitas portas. ⚠️ Só Linux |
| `none` | Só loopback | Processamento sem rede |
| `overlay` | Rede entre vários hosts (VXLAN) | Swarm, cluster |
| `macvlan` | O container ganha MAC e IP na sua LAN física | Aparelhos que precisam ser vistos na rede (Pi-hole, Home Assistant) |
| `ipvlan` | Como macvlan, compartilhando o MAC | Ambientes que limitam MACs por porta |

### `host` — o que se ganha e o que se perde

```bash
docker run -d --network host nginx:alpine
curl localhost:80        # funciona — o nginx escutou direto na porta 80 do host
```

Ganho: sem NAT, sem tradução; latência e vazão praticamente nativas. Serviços que abrem
centenas de portas (SIP, jogos, alguns protocolos P2P) ficam viáveis.

Perda: **nenhum isolamento de rede**; o `-p` deixa de existir (e é ignorado com um aviso); dois
containers não podem escutar na mesma porta; e no macOS/Windows o "host" é a VM, não a sua
máquina — o que faz o comportamento diferir da expectativa.

### `macvlan` — o container como um aparelho na sua LAN

```bash
docker network create -d macvlan \
  --subnet=192.168.1.0/24 \
  --gateway=192.168.1.1 \
  -o parent=eth0 \
  lan

docker run -d --network lan --ip 192.168.1.90 --name pihole pihole/pihole
```

O container recebe `192.168.1.90` e responde a outros aparelhos da rede como se fosse um
dispositivo físico.

**A pegadinha clássica:** por padrão, **o host não consegue falar com o container macvlan** (e
vice-versa), porque o tráfego não passa pela bridge do kernel. A correção é criar uma interface
macvlan também no host:

```bash
sudo ip link add macvlan-host link eth0 type macvlan mode bridge
sudo ip addr add 192.168.1.200/32 dev macvlan-host
sudo ip link set macvlan-host up
sudo ip route add 192.168.1.90/32 dev macvlan-host
```

E mais duas: muitas redes Wi-Fi não permitem múltiplos MACs por associação (macvlan não funciona
em Wi-Fi na maioria dos casos), e o servidor DHCP da sua rede não conhece esses IPs — reserve-os
fora da faixa DHCP.

---

## 3. DNS interno: a regra que resolve tudo

> **Na bridge padrão (`bridge`), NÃO há resolução por nome.**
> **Em qualquer rede criada por você — inclusive as do Compose — há.**

```bash
# Bridge padrão: não resolve
docker run -d --name a nginx:alpine
docker run --rm alpine ping -c1 a
# esperado: bad address 'a'

# Rede criada: resolve
docker network create minha
docker run -d --network minha --name b nginx:alpine
docker run --rm --network minha alpine ping -c1 b
# esperado: 64 bytes from 172.x.x.x

docker rm -f a b && docker network rm minha
```

Por dentro: o Docker embute um resolvedor em `127.0.0.11` dentro do namespace de rede do
container, e o `/etc/resolv.conf` gerado aponta para ele.

```bash
docker run --rm --network minha alpine cat /etc/resolv.conf
# esperado: nameserver 127.0.0.11
```

**Por que a bridge padrão não tem DNS?** Compatibilidade histórica. Ela é anterior às redes
definidas pelo usuário e ao mecanismo de `--link` (hoje obsoleto). Mudar o comportamento
quebraria configurações antigas. É uma **decisão histórica documentada**, não uma limitação
técnica — e a recomendação oficial há anos é: crie sempre uma rede.

### Aliases e múltiplas redes

```bash
docker network create app
docker run -d --network app --network-alias banco --name postgres-prod postgres:16
docker run --rm --network app alpine nslookup banco     # resolve pelo alias
```

No Compose, o **nome do serviço** é o nome DNS. Se houver réplicas, o DNS devolve **todos** os
IPs, e o cliente (ou o nginx) faz o balanceamento.

---

## 4. Publicação de portas — como funciona de verdade

```bash
docker run -d -p 8080:80 nginx:alpine
```

O Docker escreve regras de NAT:

```bash
sudo iptables -t nat -L DOCKER -n | grep 8080
# esperado: DNAT ... tcp dpt:8080 to:172.17.0.2:80
```

Formas de publicar:

```bash
-p 8080:80                  # TODAS as interfaces do host — visível na LAN
-p 127.0.0.1:8080:80        # ✅ só no loopback
-p 192.168.1.50:8080:80     # numa interface específica
-p 8080:80/udp              # UDP
-p 8000-8010:8000-8010      # faixa
-P                          # publica tudo do EXPOSE em portas altas aleatórias
```

> ### ⚠️ O Docker fura o seu firewall — e isso surpreende quase todo mundo
>
> As regras do Docker vão para a cadeia `DOCKER` da tabela `nat`, que é processada **antes** das
> regras de `INPUT` que o `ufw` gerencia. Resultado: `ufw deny 5432` **não** impede o acesso a
> um container publicado com `-p 5432:5432`.
>
> ```bash
> sudo ufw status                 # diz que a porta está bloqueada
> nmap -p 5432 IP_DA_MAQUINA      # de outra máquina: a porta está aberta
> ```
>
> **As três correções, em ordem de qualidade:**
>
> 1. **Publique só no loopback:** `-p 127.0.0.1:5432:5432`. Simples e eficaz.
> 2. **Use a cadeia `DOCKER-USER`,** que é avaliada antes das regras do Docker:
>    ```bash
>    sudo iptables -I DOCKER-USER -i eth0 ! -s 10.0.0.0/8 -j DROP
>    ```
> 3. **Não publique.** Serviços internos (banco, cache) não precisam de `ports:` — o proxy fala
>    com eles pela rede do Compose.
>
> Na Engine 29 há suporte **experimental** a `nftables` como backend, ajustável com
> `"firewall-backend": "nftables"` no `daemon.json`. O comportamento é funcionalmente
> equivalente, mas **quem usa a cadeia `DOCKER-USER` do iptables precisa revisar as regras**.

---

## 5. Como um container alcança o host

| Cenário | Como |
|---|---|
| Docker Desktop (macOS/Win) | `host.docker.internal` — já funciona |
| Linux | Adicione `--add-host=host.docker.internal:host-gateway` |
| Linux, alternativa | Use o IP do gateway: normalmente `172.17.0.1` |
| Compose | `extra_hosts: ["host.docker.internal:host-gateway"]` |

```bash
docker run --rm --add-host=host.docker.internal:host-gateway alpine \
  ping -c1 host.docker.internal
```

Caso típico: o container precisa falar com um banco que roda direto na máquina do
desenvolvedor.

---

## 6. Segmentação de rede como camada de segurança

Este é o uso mais subaproveitado do modelo de rede.

```yaml
services:
  proxy:
    networks: [publica, interna]     # ponte entre os dois mundos
    ports: ["443:443"]

  api:
    networks: [interna]              # não alcança a internet
    # sem ports:

  db:
    networks: [interna]
    # sem ports:

networks:
  publica:
  interna:
    internal: true      # ← sem rota de saída para a internet
```

O que `internal: true` garante:

```bash
docker compose exec api wget -qO- --timeout=3 https://example.com
# esperado: falha — não há rota
docker compose exec api wget -qO- http://db:5432
# esperado: alcança (mesma rede)
```

**Por que isso importa:** se a API for comprometida por uma vulnerabilidade de dependência, o
atacante não consegue baixar ferramentas, nem exfiltrar dados por HTTP, nem contatar um servidor
de comando e controle. Custa **uma linha** de YAML e elimina o passo mais comum de uma cadeia de
ataque.

*Opinião profissional:* de todas as medidas de segurança em container, `internal: true` é a de
melhor relação custo-benefício, e a menos usada.

---

## 7. Redes overlay (multi-host)

Conectam containers em máquinas diferentes, encapsulando o tráfego em **VXLAN** (UDP 4789).

```bash
docker swarm init
docker network create -d overlay --attachable minha-overlay
docker service create --name web --network minha-overlay --replicas 3 nginx:alpine
```

Portas necessárias entre os nós: TCP 2377 (gerência do cluster), TCP/UDP 7946 (descoberta), UDP
4789 (VXLAN).

Custo real: encapsulamento VXLAN acrescenta cabeçalho e reduz o MTU efetivo. **Problemas de MTU
são a causa nº 1 de "funciona com pacote pequeno e trava com pacote grande"** em overlay —
tipicamente um TLS handshake que completa e uma transferência que congela.

```bash
docker network create -d overlay --opt com.docker.network.driver.mtu=1450 rede
```

Criptografia opcional (IPsec), com custo de CPU:
```bash
docker network create -d overlay --opt encrypted rede-segura
```

---

## 8. Depuração de rede — o procedimento

Use `nicolaka/netshoot`, que traz `dig`, `curl`, `tcpdump`, `ss`, `nmap`, `iperf`, `mtr`.

```bash
# Entrar no NAMESPACE DE REDE do container alvo, sem alterar a imagem dele
docker run --rm -it --network container:MEU_CONTAINER nicolaka/netshoot
# lá dentro:
ss -tlnp            # o que está escutando
dig outro-servico   # o DNS interno resolve?
curl -v http://outro-servico:3000/saude
tcpdump -i any port 5432 -nn
```

### A árvore de diagnóstico

```
"não consigo conectar"
   │
   ├─ De FORA para o container?
   │    ├─ docker ps mostra "0.0.0.0:8080->80/tcp"?  → se não, faltou -p
   │    ├─ docker logs: o app diz em que porta subiu?
   │    ├─ O app escuta em 0.0.0.0 ou em 127.0.0.1?  → 127.0.0.1 é o erro nº 1
   │    │    docker exec X ss -tlnp   → veja o endereço de bind
   │    └─ Outro processo já usa a porta do host?  → ss -tlnp | grep :8080
   │
   ├─ Entre containers?
   │    ├─ Estão na MESMA rede?  → docker network inspect REDE
   │    ├─ Está na bridge padrão?  → não há DNS ali; crie uma rede
   │    ├─ Usou o nome do SERVIÇO (não do container, não o IP)?
   │    └─ O alvo já subiu?  → depends_on com condition: service_healthy
   │
   └─ Do container para a internet?
        ├─ A rede é `internal: true`?  → é o comportamento esperado
        ├─ DNS resolve?  → docker exec X nslookup github.com
        ├─ Rota existe?  → docker exec X ip route
        └─ Proxy corporativo configurado?  → ver 03-instalacao.md
```

### Os erros e o que significam

| Erro | Causa quase sempre |
|---|---|
| `connection refused` | O alvo não está escutando naquela porta/endereço. App em `127.0.0.1`, ou ainda subindo |
| `connection timed out` | Firewall, rota ausente, ou o alvo está em outra rede |
| `bad address 'nome'` / `Name does not resolve` | Bridge padrão (sem DNS), ou nome errado, ou o alvo ainda não existe |
| `no route to host` | Redes diferentes, ou `internal: true` |
| `address already in use` | Outro processo do host ocupa a porta |
| TLS handshake trava em overlay | **MTU** |

---

## 9. Configurações de rede no daemon

```json
// /etc/docker/daemon.json
{
  "bip": "172.30.0.1/16",
  "default-address-pools": [
    { "base": "172.31.0.0/16", "size": 24 }
  ],
  "dns": ["1.1.1.1", "8.8.8.8"],
  "mtu": 1450,
  "ipv6": true,
  "fixed-cidr-v6": "fd00::/80",
  "iptables": true,
  "userland-proxy": false
}
```

| Chave | Para que serve |
|---|---|
| `bip` | Muda a sub-rede da `docker0` — **necessário quando 172.17.x colide com a rede da empresa/VPN** |
| `default-address-pools` | Faixas para as redes criadas depois; evita esgotamento e colisão |
| `dns` | Servidores DNS injetados nos containers |
| `mtu` | Essencial sob VPN, overlay ou nuvem com MTU reduzido |
| `userland-proxy` | `false` usa só NAT (mais rápido, menos memória); `true` mantém o `docker-proxy` |
| `iptables: false` | Desliga a manipulação de firewall pelo Docker. ⚠️ Você passa a ser responsável por tudo |

> **Colisão de sub-rede é um problema real e frequente:** se a VPN corporativa usa
> `172.17.0.0/16`, todos os containers deixam de alcançar a rede da empresa e o sintoma parece
> aleatório. Mudar `bip` e `default-address-pools` resolve.

---

## 10. Boas práticas, condensadas

1. **Sempre crie uma rede** (ou use o Compose, que cria uma). Nunca dependa da bridge padrão.
2. **Uma rede por aplicação**, no mínimo. Idealmente, separe borda de interna.
3. **`internal: true`** para tudo que não precisa de internet.
4. **Publique apenas o necessário**, e prefira `127.0.0.1:porta:porta`.
5. **Nunca use IP de container** em configuração: use o nome do serviço.
6. **`-p` ignora o `ufw`.** Trate isso como fato, não como bug.
7. **Ajuste o MTU** em VPN, overlay e nuvem, antes de perder um dia com "trava em arquivo
   grande".
8. **Mude a faixa padrão** se ela colidir com sua rede corporativa.

---

## Autoteste

1. Explique o que é um par `veth` e onde ficam suas duas pontas.
2. Por que `ping outro-container` falha na bridge padrão e funciona numa rede criada por você?
   Qual é a razão histórica disso?
3. Em `-p 127.0.0.1:8080:80`, o que cada um dos três campos significa?
4. Por que `ufw deny 5432` não protege um container publicado com `-p 5432:5432`? Dê duas
   correções.
5. O que `internal: true` garante, e por que é a medida de segurança de melhor custo-benefício?
6. Um container macvlan não é alcançável a partir do host. Por quê, e como resolver?
7. Um TLS handshake completa mas a transferência trava numa rede overlay. Qual é a suspeita nº 1?
8. Qual comando entra no namespace de rede de um container sem modificar a imagem dele?
9. `connection refused` versus `connection timed out`: o que cada um sugere?
10. Sua VPN corporativa usa `172.17.0.0/16`. O que quebra e qual chave do `daemon.json` corrige?
