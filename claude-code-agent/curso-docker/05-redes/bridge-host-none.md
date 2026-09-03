# Modos de rede: bridge, host, none (e os outros)

> **Nível:** intermediário
> **Última verificação:** 18/08/2026

## 1. O problema

Um container precisa de rede — mas quanta? Falar com a internet? Ser alcançado
de fora? Falar com outros containers? Cada resposta tem um custo de isolamento,
e o Docker oferece modos diferentes para cada combinação.

## 2. Os modos

| Modo | Container tem IP próprio? | Alcança a internet? | É alcançado do host? | Uso típico |
|---|---|---|---|---|
| `bridge` (padrão) | sim | sim (via NAT) | só via `-p` | 95% dos casos |
| `host` | não, usa a pilha do host | sim | **todas as portas, direto** | descoberta na LAN, alto desempenho |
| `none` | só loopback | **não** | não | processamento isolado |
| `container:<nome>` | compartilha com outro | conforme o outro | conforme o outro | sidecar, depuração |
| `macvlan` | sim, IP na sua LAN | sim | sim, como máquina física | aparelho que precisa de IP na rede |

## 3. `bridge` — o padrão

O Docker cria uma ponte virtual (`docker0`) e conecta os containers nela. Cada
container ganha IP privado (`172.17.0.0/16`, tipicamente) e sai para a internet
via NAT.

```
  host (192.168.1.10)
   │
   ├── docker0 (172.17.0.1)  ← a ponte
   │     ├── container A (172.17.0.2)
   │     └── container B (172.17.0.3)
   │
   └── eth0 → LAN → internet
```

De fora, os containers não existem. Para alcançá-los, você publica porta:

```bash
docker run -d -p 8080:80 nginx:1.29-alpine
```

O Docker escreve uma regra de NAT: tudo que chega na 8080 do host é encaminhado
para a 80 do container.

### Bridge padrão vs bridge definida por você — a diferença que importa

Existem duas coisas chamadas "bridge", e a confusão é frequente:

| | Bridge padrão (`docker0`) | Bridge que você cria |
|---|---|---|
| Como se usa | automático, sem `--network` | `docker network create minha-rede` |
| **DNS por nome de container** | **NÃO funciona** | **funciona** |
| Isolamento | todos os containers juntos | só quem você conectar |
| Compose | não usa | **é o que o Compose cria** |

```bash
# Bridge PADRÃO: sem DNS
docker run -d --name db postgres:17-alpine
docker run --rm alpine ping -c1 db
# ping: bad address 'db'          ← não resolve

# Bridge PRÓPRIA: com DNS
docker network create minha-rede
docker run -d --name db --network minha-rede postgres:17-alpine
docker run --rm --network minha-rede alpine ping -c1 db
# 64 bytes from 172.18.0.2         ← resolve
```

**Por que essa diferença existe?** Decisão histórica: a bridge padrão é de 2013,
anterior ao DNS embutido. O mecanismo antigo era `--link`, hoje legado. Quando o
DNS interno chegou (Docker 1.10, 2016), mudar o comportamento da rede padrão
quebraria instalações existentes — então o recurso novo foi só para redes novas.
**Parada legítima: compatibilidade retroativa.**

Consequência prática: **sempre crie uma rede.** O Compose já faz isso por você,
que é mais um motivo para usá-lo mesmo com um único container.

## 4. `host` — sem isolamento de rede

```bash
docker run -d --network host nginx:1.29-alpine
```

O container usa a pilha de rede do host diretamente. Não há NAT, não há `-p`
(seria ignorado): o nginx escuta na porta 80 **do host**.

**Quando usar:**

- **Descoberta na LAN** — mDNS, SSDP, DLNA. Um servidor Plex/Jellyfin que precisa
  ser descoberto pela TV não funciona atrás de NAT, porque broadcast não
  atravessa a bridge.
- **Desempenho de rede extremo** — sem NAT, elimina-se uma camada. Relevante
  para carga muito alta de pacotes pequenos.
- **Muitas portas dinâmicas** — servidor SIP/RTP que abre faixas grandes.

**O que se perde:**

- **Isolamento de porta.** O container pode ocupar qualquer porta do host,
  inclusive conflitando com serviços existentes.
- **Todas as portas ficam expostas.** Não há `-p` para escolher o que publicar.
  Se a aplicação abrir uma porta de administração, ela está na sua LAN.
- **Só funciona no Linux.** No macOS e no Windows, o "host" é a VM Linux
  interna, não a sua máquina — o modo não faz o que você espera.

**Recomendação:** só quando um dos três casos acima realmente se aplicar. Usar
`host` para "resolver" problema de conectividade quase sempre esconde um erro de
configuração de bridge.

## 5. `none` — sem rede nenhuma

```bash
docker run --rm --network none alpine ip addr
# só o loopback
```

Serve para processamento que não deve falar com nada: converter um arquivo,
rodar código não confiável, processar dado sensível.

```bash
# Converter um vídeo sem que o container possa acessar a rede
docker run --rm --network none \
  -v "$(pwd)":/dados \
  linuxserver/ffmpeg -i /dados/entrada.mp4 /dados/saida.webm
```

Isolamento forte e barato. Subutilizado.

## 6. `container:<nome>` — compartilhar a pilha

```bash
docker run --rm -it --network container:minha-api nicolaka/netshoot
```

O segundo container usa **exatamente** a rede do primeiro: mesmo IP, mesmas
portas, mesmo `localhost`.

É a melhor técnica de depuração que existe em Docker. Sua imagem de produção não
tem `curl`, `dig` nem `tcpdump` (e não deve ter). Com isso você anexa um
container cheio de ferramentas à rede dela, sem sujar a imagem:

```bash
docker run --rm -it --network container:minha-api nicolaka/netshoot
# dentro:
curl localhost:8000/health     # o localhost É o da API
dig db
tcpdump -i any port 5432
```

## 7. `macvlan` — IP de verdade na sua LAN

```bash
docker network create -d macvlan \
  --subnet=192.168.1.0/24 \
  --gateway=192.168.1.1 \
  -o parent=eth0 \
  rede-lan
```

O container aparece na sua rede como uma máquina física, com IP e MAC próprios.
O roteador o enxerga.

**Quando faz sentido em homelab:** um Pi-hole que precisa ser o DNS da rede,
ou um serviço que precisa de IP fixo visível pelos outros aparelhos.

**A armadilha clássica:** por desenho do macvlan, o **host não fala com o
container** e vice-versa, mesmo estando na mesma rede física. Você acessa de
qualquer outro aparelho, menos da máquina que o hospeda. A solução exige criar
uma interface macvlan adicional no host. É complexidade real — só adote se
precisar mesmo.

## 8. Portas: as três formas de publicar

```bash
-p 8080:80              # 0.0.0.0:8080 -> toda a LAN alcança
-p 127.0.0.1:8080:80    # só o host alcança
-p 8080:80/udp          # protocolo explícito
-P                      # publica todo EXPOSE em portas aleatórias
```

A diferença entre as duas primeiras é a decisão de segurança mais frequente em
homelab. `-p 5432:5432` num Postgres expõe o banco para qualquer aparelho da
casa — incluindo a TV, o aspirador e o celular da visita.

### O aviso sobre firewall

**As regras de iptables do Docker são avaliadas antes das do UFW.** Você pode ter

```bash
sudo ufw deny 5432
```

e a porta continuar acessível, porque o Docker insere regras na cadeia
`DOCKER-USER`/`nat`, que é processada antes. Isso surpreende praticamente todo
mundo na primeira vez.

Duas defesas confiáveis:

1. **Publicar só no loopback**: `127.0.0.1:5432:5432`.
2. **Não publicar**: se só outros containers precisam, não use `ports:`.

Regras no `DOCKER-USER` funcionam, mas exigem saber o que se está fazendo.
A regra prática é simples: **se não precisa ser alcançado do host, não publique.**

## 9. Erros que você provavelmente vai cometer

| Sintoma | Causa raiz | Correção |
|---|---|---|
| `bad address 'db'` | containers na bridge **padrão**, sem DNS | criar rede (ou usar Compose) |
| `connection refused` na porta publicada | app escutando em `127.0.0.1` dentro do container | `--host 0.0.0.0` |
| `port is already allocated` | porta do host ocupada | `docker ps`; trocar a porta |
| `-p` ignorado | `--network host` não usa publicação | remover `-p` ou sair do modo host |
| Banco acessível da LAN mesmo com UFW negando | iptables do Docker antes do UFW | `127.0.0.1:` no `ports:` |
| Container sem internet | rede com `internal: true` | adicionar rede externa ao serviço |
| macvlan funciona de outros aparelhos, menos do host | isolamento por desenho do macvlan | interface macvlan adicional no host |
| TV não acha o servidor de mídia | broadcast não atravessa NAT da bridge | `--network host` |

## 10. Autoteste

1. Por que DNS por nome não funciona na bridge padrão, mas funciona numa rede
   criada por você?
2. Cite dois casos em que `--network host` é a escolha certa, e o que se perde.
3. Para que serve `--network none`? Dê um exemplo concreto.
4. Como depurar rede num container que não tem `curl` nem `dig`?
5. Diferença prática entre `-p 8080:80` e `-p 127.0.0.1:8080:80`.
6. Por que `ufw deny 5432` pode não proteger nada?
7. Qual a armadilha clássica do macvlan?
8. Por que `-p` não tem efeito em `--network host`?

---
[DNS interno →](dns-interno-entre-servicos.md) · [índice](../00-indice.md)
