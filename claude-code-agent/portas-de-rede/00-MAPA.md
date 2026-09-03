# Portas de Rede — Mapa do Assunto

**Nível:** do leigo absoluto à pesquisa · **Última atualização:** 14/08/2026

---

## A pergunta que originou este material

> *Como se verifica as portas de rede de uma máquina? Quais são elas e para que servem?
> Quais os protocolos delas? Como testar e descobri-las?*

São quatro perguntas, e elas têm profundidades muito diferentes. A primeira parece de
comando (`ss -tulpn`) e é de **modelo mental**: existem duas maneiras de "verificar", e
elas respondem a perguntas diferentes. A terceira parece trivial ("TCP ou UDP") e é onde
mora o mal-entendido mais comum do assunto inteiro.

**Resposta curta, para quem tem pressa** — o resto do material é o *porquê* de cada linha:

```bash
# Linux — o que MINHA máquina abriu
ss -tulpn

# macOS
lsof -nP -iTCP -sTCP:LISTEN ; lsof -nP -iUDP

# Windows (PowerShell)
Get-NetTCPConnection -State Listen | Select LocalAddress,LocalPort,OwningProcess

# O que AQUELE host mostra para mim
nmap -sV -Pn <alvo>          # só com autorização
```

---

## O que você saberá ao final

- Explicar o que é uma porta **sem usar a palavra "porta"** — e por que a analogia da
  "porta de um prédio" atrapalha mais do que ajuda.
- Ler `ss`, `netstat`, `lsof`, `Get-NetTCPConnection` e `nmap` sem depender de decoreba,
  porque você saberá **de onde cada um tira o dado**.
- Saber por que `ss` e `nmap` discordam — e o que cada discordância significa.
- Dizer, de cabeça, para que serve cada uma das ~60 portas que aparecem em 95 % das máquinas.
- Explicar por que a porta 443 pode ser **dois serviços diferentes** ao mesmo tempo
  (TCP/TLS e UDP/QUIC) e por que isso não é conflito.
- Entender a quádrupla `(IP origem, porta origem, IP destino, porta destino)` e, a partir
  dela, responder sozinho por que um servidor aguenta 50 mil conexões na porta 80.
- Diagnosticar `Address already in use`, `Connection refused`, `Connection timed out` e
  `Permission denied` em 30 segundos cada, sabendo a causa e não o feitiço.
- Decidir, com critério, o que fechar e o que deixar aberto — e por que fechar no `bind`
  é melhor que fechar no firewall.
- Saber quando parar de confiar no número da porta: o que é *port-agnostic* na rede de 2026.

---

## Roteiro de leitura

### Se você nunca ouviu falar disso
`01` → `04` → `06` → `10`. Umas 3 horas. Ao final você inventaria e entende sua máquina.

### Se você já usa `netstat` mas no automático
`10` → `12` → `13` → `16` → `17` → `75`. É onde o modelo mental se conserta.

### Se você trabalha com segurança ou infraestrutura
Tudo, na ordem. Dê atenção especial a `17`, `18`, `19`, `20` e `75`.

### Se você quer só a referência
`05-manual-de-uso.md` e `16-catalogo-de-portas.md`. São feitos para consulta, não para leitura linear.

---

## Arquivos

### Bloco A · Porta de entrada

| Arquivo | O que tem |
|---|---|
| [`01-introducao-leigo.md`](01-introducao-leigo.md) | O que é uma porta, com zero jargão. A analogia certa e por que a comum é ruim. |
| [`02-pre-requisitos.md`](02-pre-requisitos.md) | O que saber antes, onde aprender, quanto tempo leva de verdade, e a rota de resgate. |
| [`03-instalacao.md`](03-instalacao.md) | Manual de campo: `ss`, `lsof`, `nmap`, `tcpdump`, `netcat`, `socat`, PowerShell, WSL2 — nos três SOs. Erros literais, PATH, permissões, desinstalação. |
| [`04-como-comecar.md`](04-como-comecar.md) | Do ambiente pronto ao primeiro inventário completo em 15 minutos, com verificação. |
| [`05-manual-de-uso.md`](05-manual-de-uso.md) | Referência consultável: toda flag de `ss`, `lsof`, `nmap`, `netstat`, PowerShell, por tarefa. |
| [`06-exemplos.md`](06-exemplos.md) | 15 receitas completas, do "quem está usando a 8080" a dois casos reais de produção. |
| [`07-projeto-modelo/`](07-projeto-modelo/README.md) | **Auditor de portas** em Python puro: lê `/proc` à mão, varre, e confronta as duas visões. 41 testes. |

### Bloco B · Núcleo

| Arquivo | O que tem |
|---|---|
| [`10-fundamentos.md`](10-fundamentos.md) | Multiplexação, a quádrupla, socket, bind/listen/accept. O vocabulário inteiro. |
| [`11-historia.md`](11-historia.md) | De 1970 ao NCP, ao RFC 793, ao `/etc/services`, à IANA. Por que 22 é SSH. |
| [`12-onde-a-porta-vive.md`](12-onde-a-porta-vive.md) | A pilha camada a camada. O que sabe de porta e o que não sabe. |
| [`13-tcp-por-dentro.md`](13-tcp-por-dentro.md) | Handshake, os 12 estados, TIME_WAIT, backlog, RST. Com capturas reais. |
| [`14-udp-e-os-outros.md`](14-udp-e-os-outros.md) | UDP, ICMP (que não tem porta), SCTP, DCCP, QUIC. Por que varrer UDP é difícil. |
| [`15-sockets-e-o-kernel.md`](15-sockets-e-o-kernel.md) | A API de sockets, `/proc/net/tcp`, netlink, o que `ss` faz por dentro. |
| [`16-catalogo-de-portas.md`](16-catalogo-de-portas.md) | **As portas, uma a uma.** ~120 entradas com serviço, protocolo, risco e o que fazer. |
| [`17-descoberta-e-varredura.md`](17-descoberta-e-varredura.md) | As duas visões. Todas as técnicas de varredura, o que cada uma prova, e a lei. |
| [`18-firewall-nat-e-o-caminho.md`](18-firewall-nat-e-o-caminho.md) | Por que a porta que você abriu não responde. NAT, CGNAT, port forwarding, túneis. |
| [`19-exposicao-e-seguranca.md`](19-exposicao-e-seguranca.md) | Superfície de ataque, bind vs. firewall, portas que já causaram desastre. |
| [`20-containers-nuvem-e-k8s.md`](20-containers-nuvem-e-k8s.md) | Namespaces de rede, `-p 8080:80`, Security Groups, Services e NodePort. |
| [`60-teoria-avancada.md`](60-teoria-avancada.md) | Espaço de portas como recurso finito, esgotamento efêmero, entropia de porta de origem, limites teóricos da varredura. |
| [`65-estado-da-arte.md`](65-estado-da-arte.md) | Ago/2026: QUIC, eBPF, varredura da internet inteira em minutos, o fim do número de porta como sinal. |

### Bloco C · Prática e erros

| Arquivo | O que tem |
|---|---|
| [`70-pratica.md`](70-pratica.md) | 14 laboratórios progressivos, com gabarito. |
| [`75-armadilhas.md`](75-armadilhas.md) | 30 erros clássicos e 9 mitos, com o porquê de cada um persistir. |

### Bloco D · Economia e ecossistema

| Arquivo | O que tem |
|---|---|
| [`80-custos-e-licencas.md`](80-custos-e-licencas.md) | Preço de tudo (quase tudo é grátis), licenças, e o custo oculto de porta aberta. Consulta de 14/08/2026. |
| [`85-cursos-e-certificacoes.md`](85-cursos-e-certificacoes.md) | Cursos gratuitos PT/EN/FR pesquisados na web, e certificações que valem. |

### Bloco E · Fontes

| Arquivo | O que tem |
|---|---|
| [`90-bibliografia.md`](90-bibliografia.md) | Livros, com edição, nível, e o que envelheceu. |
| [`95-referencias.md`](95-referencias.md) | RFCs, registro da IANA, código-fonte do kernel, pessoas a seguir. |
| [`GLOSSARIO.md`](GLOSSARIO.md) | ~140 termos. |

---

## Status dos blocos

| Bloco | Status | Observação |
|---|---|---|
| A · Porta de entrada | ✅ | Projeto-modelo executado, 41 testes verdes |
| B · Núcleo | ✅ | 13 arquivos, do fundamento ao estado da arte |
| C · Prática e erros | ✅ | 14 laboratórios, 30 armadilhas |
| D · Economia e ecossistema | ✅ | Pesquisado na web em 14/08/2026 |
| E · Fontes | ✅ | RFCs e registro IANA verificados |
| Glossário | ✅ | |

---

## O que foi executado durante a escrita

Este material não foi escrito de memória. As saídas mostradas são reais, colhidas em
**Ubuntu 22.04.5 LTS, kernel 6.8.0-136, em 14/08/2026**, com `iproute2-5.15.0`,
`nmap 7.80`, `Python 3.10.12`, `curl 7.81.0`, `OpenSSL 3.0.2`.

Foram efetivamente executados e conferidos: `ss` em todas as formas do `05`; `nmap -sT`
contra `127.0.0.1`; leitura direta de `/proc/net/tcp` e conferência contra o `ss`;
`bind()` em porta 0, em porta ocupada e em porta < 1024 sem privilégio (as três mensagens
de erro do `04` são literais); UDP contra porta fechada (o `ECONNREFUSED` via ICMP);
`getservbyname`/`getservbyport`; captura de banner de Apache e MySQL; e os 41 testes do
projeto-modelo.

**Não executado, e declarado onde aparece:** os comandos de macOS e Windows (não há essas
máquinas no ambiente de escrita — as sintaxes vêm da documentação oficial citada no `95`);
`nmap -sS`, `-sU` e `-O` completos (exigem root, que não estava disponível); as regras de
`iptables`/`nft` de exemplo; e os laboratórios do `70` como enunciados.

**Versões atuais das ferramentas (pesquisado na web em 14/08/2026):** Nmap 7.991 é a
última versão da série 7.x (7.99 saiu em 26/03/2026). A máquina de escrita tem a 7.80,
de 2019 — o que é típico de repositório de distribuição LTS e está anotado onde importa.

---

## Assuntos vizinhos nesta pasta

- [`tabela-arp`](../tabela-arp/00-MAPA.md) — **a camada logo abaixo.** Antes de o pacote
  chegar à porta, ele precisa achar o MAC do próximo salto. Leia junto com o
  [`12-onde-a-porta-vive.md`](12-onde-a-porta-vive.md).
- [`ethical-hacking`](../ethical-hacking/00-MAPA.md) — varredura como fase de um pentest, com o enquadramento legal completo.
- [`docker`](../docker/00-MAPA.md) — namespaces de rede e publicação de portas.
- [`apis`](../apis/00-MAPA.md) — o que roda em cima de HTTP, uma vez que a porta está aberta.

> ⚠️ **Não confunda com [`portas-logicas`](../portas-logicas/00-MAPA.md)**, que trata de AND,
> OR e NAND — os circuitos de que um chip é feito. Mesma palavra, assuntos sem nenhuma
> relação. E cuidado com uma terceira: em equipamento de rede, "porta" é o **conector físico**
> onde se enfia o cabo. Um switch de 24 portas tem 24 buracos, não 24 números TCP.
