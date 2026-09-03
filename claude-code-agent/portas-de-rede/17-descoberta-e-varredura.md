# 17 · Descoberta e varredura — como testar e descobrir portas

**Nível:** intermediário a avançado · **Última atualização:** 14/08/2026
Exemplos executados contra `127.0.0.1` em 14/08/2026. As técnicas que exigem root
(`-sS`, `-sU`, `-O`) **não foram executadas** — está dito onde aparecem.

---

## Antes de tudo: a lei

Varrer portas de máquina de terceiro **sem autorização escrita** é, no Brasil,
potencialmente enquadrável no **art. 154-A do Código Penal** (invasão de dispositivo
informático, com a redação da Lei 14.155/2021), e viola o contrato de praticamente todo
provedor de internet e de nuvem.

Três regras que valem para este arquivo inteiro:

1. **Alvo padrão é `127.0.0.1`.** Tudo aqui funciona contra a própria máquina.
2. **Rede corporativa exige aviso prévio, por escrito**, mesmo sendo você o administrador.
   Varredura dispara IDS e vira incidente. Cinco minutos de e-mail evitam uma conversa muito
   pior depois.
3. **`scanme.nmap.org`** é mantido pelo projeto Nmap com autorização explícita para ser
   varrido. É o único alvo público que este material recomenda — com moderação.

O enquadramento completo está em [`ethical-hacking`](../ethical-hacking/00-MAPA.md) nesta
pasta.

---

## 1. As duas visões — e por que você precisa das duas

Existem **duas** formas de descobrir portas, e elas respondem a perguntas diferentes.
Confundi-las produz relatório errado.

| | **De dentro** (inventário) | **De fora** (varredura) |
|---|---|---|
| Pergunta | "O que meu sistema abriu?" | "O que aquele host me mostra?" |
| Ferramenta | `ss`, `lsof`, `Get-NetTCPConnection` | `nmap`, `nc`, `masscan` |
| Fonte do dado | Tabela de sockets do kernel | Respostas da rede |
| Confiabilidade | **Verdade absoluta** | Verdade **do caminho** |
| Mostra o processo dono | **Sim** | Não |
| Funciona remotamente | Não | **Sim** |
| Vê NAT, firewall, proxy | Não | **Sim** |
| Precisa de acesso à máquina | Sim | Não |

**Nenhuma das duas é suficiente.** A de dentro não sabe se o firewall funciona. A de fora
não sabe o que existe atrás do filtro.

### Quando elas discordam — a tabela de diagnóstico

Esta é a tabela mais útil do arquivo:

| Dentro (`ss`) | Fora (`nmap`) | O que está acontecendo |
|---|---|---|
| LISTEN | aberta | Coerente. Serviço no ar e alcançável. |
| LISTEN | **fechada** | O serviço morreu entre as duas medições, ou você varreu outra máquina |
| LISTEN | **filtrada** | ✅ **Firewall funcionando.** É o resultado desejado para porta interna |
| LISTEN em `127.0.0.1` | fechada/filtrada de fora | ✅ Bind restrito. Correto. |
| LISTEN em `127.0.0.53` | fechada em `127.0.0.1` | Loopback ≠ `127.0.0.1`. Todo `127.0.0.0/8` é loopback |
| **nada** | **aberta** | ⚠️ **Redirecionamento no kernel, proxy transparente, NAT ou honeypot** |
| nada | fechada | Coerente. Não há nada ali. |

O caso ⚠️ é o mais instrutivo, e aconteceu de verdade durante a escrita deste curso.

### O caso real

Na máquina de escrita, um `nmap -sT -Pn 127.0.0.1` reportou **25 portas abertas**:

```
23/tcp    open  telnet
25/tcp    open  smtp
53/tcp    open  domain
80/tcp    open  http
110/tcp   open  pop3
143/tcp   open  imap
389/tcp   open  ldap
443/tcp   open  https
587/tcp   open  submission
3128/tcp  open  squid-http
8080/tcp  open  http-proxy
9200/tcp  open  wap-wsp
...
```

O `ss -tlnp` confirmava **8**. Testando à mão:

```bash
timeout 3 bash -c 'exec 3<>/dev/tcp/127.0.0.1/23' && echo CONECTOU
```
```
porta 23: CONECTOU
porta 25: CONECTOU
porta 143: CONECTOU
porta 8080: CONECTOU
porta 12345: recusou/timeout      ← porta aleatória alta: recusa normalmente
porta 54321: recusou/timeout
```

**Portas conhecidas conectam; portas arbitrárias não.** Isso descarta "tudo conecta" e
aponta para uma **lista específica** de portas sendo redirecionada — a assinatura de um
agente de segurança corporativo, um proxy de inspeção, ou um honeypot de detecção interna.

Não foi possível confirmar sem `sudo`, e este material diz isso em vez de inventar. Os
comandos que fechariam o diagnóstico:

```bash
sudo iptables -t nat -S | grep -E 'REDIRECT|DNAT|TPROXY'
sudo nft list ruleset | grep -E 'redirect|dnat|tproxy'
```

**A lição:** *"a porta está aberta"* é uma afirmação sobre o **caminho inteiro**, não sobre
um processo. E é por isso que a resposta certa para "como se verifica as portas de uma
máquina" é **"de dois jeitos, e compare"**.

---

## 2. Técnicas de varredura TCP

| Técnica | Flag | Root? | Como funciona | Detecta |
|---|---|---|---|---|
| **Connect** | `-sT` | não | `connect()` completo, três vias | aberta/fechada/filtrada |
| **SYN** | `-sS` | sim | SYN → SYN-ACK → **RST** (não completa) | idem, mais rápido |
| **ACK** | `-sA` | sim | Manda ACK sem conexão | **se há firewall com estado** |
| **Window** | `-sW` | sim | Variante do ACK, olha a janela | aberta vs. fechada em alguns SOs |
| **FIN / NULL / Xmas** | `-sF -sN -sX` | sim | Flags inválidas | funciona em pilhas antigas |
| **Maimon** | `-sM` | sim | FIN+ACK | idem |
| **Idle / zombie** | `-sI` | sim | Usa terceiro host como refletor | **oculta sua origem** |

### `-sT` × `-sS`: a diferença que importa

```
-sT (connect):    você → SYN → alvo
                  você ← SYN-ACK ← alvo
                  você → ACK → alvo          ← conexão COMPLETA
                  você → FIN/RST → alvo      ← e agora fecha

-sS (SYN):        você → SYN → alvo
                  você ← SYN-ACK ← alvo
                  você → RST → alvo          ← aborta. Nunca completou.
```

| | `-sT` | `-sS` |
|---|---|---|
| Privilégio | Nenhum | Root (pacote bruto) |
| Pacotes por porta | 4 | 3 |
| Gera log na aplicação | **Sim** (o `accept()` acontece) | Não |
| Consome socket seu | Sim (sujeito a `ulimit -n`) | Não |
| Velocidade | Mais lento | ~30 % mais rápido |

O `-sS` era chamado de *stealth scan* nos anos 1990 porque a aplicação não registrava nada.
**Hoje não é discreto**: qualquer IDS reconhece a assinatura "SYN seguido de RST" em
segundos. O nome ficou por inércia.

### As varreduras de flag inválida — e por que quase não funcionam mais

`-sF`, `-sN`, `-sX` exploram uma frase do RFC 793: uma porta **fechada** deve responder RST
a um segmento sem SYN/ACK/RST; uma porta **aberta** deve ignorar.

Funciona em pilhas que seguem o RFC à risca. **Não funciona no Windows**, que responde RST
em ambos os casos — o que, ironicamente, transformou a técnica num método de detecção de
sistema operacional.

Hoje têm valor sobretudo histórico e didático: mostram que "aberta" e "fechada" são
conclusões **inferidas de comportamento**, não fatos lidos de algum lugar.

### Varredura UDP

```bash
sudo nmap -sU --top-ports 20 alvo
sudo nmap -sU -sV -p 53,123,161,500,1900 alvo    # com sondas específicas
```

Lenta e ambígua pelas razões do [`14-udp-e-os-outros.md`](14-udp-e-os-outros.md): a
ausência de resposta não distingue "aberta e calada" de "filtrada", e o limite de taxa de
ICMP do alvo obriga a esperar.

**Estratégia profissional:** nunca varra UDP às cegas. Sonde as portas que importam, com
`-sV` para mandar consultas reais do protocolo.

---

## 3. Descoberta de hosts — antes de varrer portas

```bash
nmap -sn 192.168.0.0/24            # quem está vivo, sem varrer portas
nmap -sn -PR 192.168.0.0/24        # por ARP (só rede local — é o mais confiável)
nmap -Pn alvo                      # PULA a descoberta, assume vivo
```

⚠️ **`-Pn` é quase sempre necessário hoje.** O Windows bloqueia ICMP echo por padrão desde
o XP SP2, e a maioria dos provedores de nuvem também. Sem `-Pn`, o `nmap` conclui "host
seems down" e não varre nada:

```
Note: Host seems down. If it is really up, but blocking our ping probes, try -Pn
```

Na rede local, `-PR` (ARP) é o método mais confiável que existe: ARP não pode ser bloqueado
sem quebrar a rede.

---

## 4. Identificação de serviço e versão

```bash
nmap -sV alvo                          # o mais útil de todos
nmap -sV --version-intensity 9 alvo    # mais sondas, mais lento
nmap -A alvo                           # -sV + -O + -sC + traceroute
```

### Como funciona por dentro

1. Conecta na porta aberta.
2. **Espera** — muitos serviços falam primeiro.
3. Se não vier nada, envia sondas de `/usr/share/nmap/nmap-service-probes`.
4. Casa a resposta contra milhares de expressões regulares.
5. Reporta produto, versão e, quando dá, o sistema operacional.

```bash
wc -l /usr/share/nmap/nmap-service-probes    # o tamanho do acervo
```

**É esse acervo, não o código, que constitui o fosso competitivo do Nmap.** São 25 anos de
curadoria de submissões da comunidade. Qualquer um escreve um scanner de portas num fim de
semana — o [projeto-modelo](07-projeto-modelo/README.md) faz isso em 60 linhas. Ninguém
reconstrói a base de sondas.

### À mão, sem `nmap`

```bash
timeout 2 nc alvo 22 | head -1                              # SSH fala primeiro
printf 'GET / HTTP/1.0\r\n\r\n' | timeout 2 nc alvo 80      # HTTP precisa de sonda
timeout 2 nc alvo 3306 | head -c 60 | xxd                   # MySQL: versão no binário
openssl s_client -connect alvo:443 </dev/null 2>/dev/null | head
```

**Saídas reais** desta máquina:

```
Server: Apache/2.4.52 (Ubuntu)
8.0.46-0ubuntu0.22.04.3 ... caching_sha2_password
```

Versão exata, distribuição e nível de patch — **antes de qualquer autenticação**. É
comportamento normal do protocolo, não erro de configuração. E é por isso que "banner" é
tratado como informação sensível em auditoria.

Reduzir o que vaza:

```apache
# Apache — /etc/apache2/conf-enabled/security.conf
ServerTokens Prod          # passa a dizer só "Apache", sem versão
ServerSignature Off
```

⚠️ **Isso é ofuscação, não proteção.** Esconder a versão não corrige a falha; apenas obriga
o atacante a testar o exploit em vez de escolher. Vale a pena (reduz ruído automatizado), mas
não substitui atualizar. Diga isso ao auditor que pedir "remova o banner" como se fosse a
correção.

---

## 5. Detecção de sistema operacional

```bash
sudo nmap -O alvo
sudo nmap -O --osscan-guess alvo
```

Baseia-se em **impressão digital da pilha TCP/IP**: cada sistema implementa detalhes
opcionais do RFC de um jeito próprio — valor inicial de TTL, tamanho de janela, ordem das
opções TCP, resposta a flags inválidas, geração de ISN.

Um atalho útil que funciona sem root, olhando só o TTL de um `ping`:

| TTL inicial típico | Provável sistema |
|---|---|
| 64 | Linux, macOS, Android |
| 128 | Windows |
| 255 | equipamento de rede (Cisco, Solaris) |

O TTL decresce um por roteador atravessado. TTL 58 numa resposta sugere Linux a 6 saltos.
Grosseiro, mas surpreendentemente útil — e é a primeira coisa que se olha numa saída de
`nmap --reason`.

**Não executado** neste material: `-O` exige root.

---

## 6. Ferramentas além do `nmap`

| Ferramenta | Foco | Velocidade | Quando usar |
|---|---|---|---|
| **`nmap`** | Precisão e profundidade | Média | O padrão. Comece e termine aqui. |
| **`masscan`** | Escala de internet | Altíssima | Faixas gigantes. Pilha TCP própria, sem estado |
| **`ZMap`** | Pesquisa acadêmica | Altíssima | Varredura da IPv4 inteira |
| **`RustScan`** | Descoberta rápida + `nmap` | Alta | Acha portas em segundos e entrega ao `nmap` |
| **`naabu`** | Automação (ProjectDiscovery) | Alta | Integra com `nuclei`, `subfinder` |
| **`nc`** | Uma porta, à mão | — | Teste pontual |
| **`Test-NetConnection`** | Uma porta, no Windows | — | Idem |

*(Versões conferidas na web em 14/08/2026: Nmap 7.991 é a atual — 7.99 saiu em 26/03/2026.
RustScan v2.4.1 e naabu v2.3.4 aparecem em comparativos recentes.)*

### `masscan` e `ZMap` — o salto conceitual de 2013

Ambos publicados em 2013, e ambos fazem a mesma coisa radical: **não usam a pilha TCP/IP do
sistema operacional**. Eles montam os pacotes à mão, mandam sem guardar estado, e
reconhecem as respostas por um truque — codificam a identificação do alvo no próprio número
de sequência inicial.

**Sem estado = sem limite de memória.** É isso que permite varrer os 4 bilhões de endereços
IPv4 em dezenas de minutos com uma máquina e um enlace de 10 Gbit/s.

```bash
# ATENÇÃO: só contra faixas suas. Isto satura enlaces e dispara todos os alertas.
masscan 10.0.0.0/8 -p80,443 --rate 10000
```

O `--rate` **não é sugestão**: sem ele, o `masscan` tenta usar toda a banda disponível e
derruba a sua própria rede antes de incomodar o alvo.

**A consequência para defesa:** desde 2013, toda porta exposta à internet é encontrada em
**minutos**, não em semanas. Qualquer suposição de "ninguém vai achar" morreu naquele ano.

### Descoberta passiva — sem tocar no alvo

| Serviço | O que faz |
|---|---|
| [Shodan](https://www.shodan.io/) | Varre a internet continuamente e indexa banners |
| [Censys](https://search.censys.io/) | Idem, com foco em certificados e ativos |
| [ZoomEye](https://www.zoomeye.org/) | Equivalente chinês |
| Certificate Transparency (`crt.sh`) | Revela subdomínios pelos certificados emitidos |

```
# consultas típicas no Shodan
port:2375 country:BR
product:MongoDB port:27017
"MySQL" version:"8.0" org:"Minha Empresa"
```

**Duas leituras, e as duas são verdadeiras:**

- **Para o atacante:** o reconhecimento fica gratuito e invisível. Ele não toca no seu alvo,
  então você não tem log nenhum.
- **Para o defensor:** é a melhor ferramenta de *asset discovery* que existe. Procure a
  **sua** organização no Shodan hoje. É comum encontrar coisas que ninguém sabia que
  existiam — e é assim que se descobrem os servidores que um estagiário subiu em 2019.

Preços em [`80-custos-e-licencas.md`](80-custos-e-licencas.md).

---

## 7. Ser encontrado: o lado da defesa

### Detectar quem varre você

```bash
# conexões meio-abertas chegando
ss -tan state syn-recv | head

# no log do firewall (se você registra DROPs)
sudo journalctl -k | grep -i 'IN=.*DPT='

# ferramentas
sudo apt install psad         # detecção de varredura
sudo apt install fail2ban     # bloqueio automático por padrão de log
```

**A assinatura de uma varredura:** muitas portas distintas, do mesmo IP de origem, num
intervalo curto. `fail2ban` e `psad` procuram exatamente isso.

### Dificultar sem se enganar

| Medida | Ajuda? | Verdade honesta |
|---|---|---|
| **Fechar o serviço** | ✅✅✅ | A única que realmente resolve |
| **Bind em `127.0.0.1`** | ✅✅✅ | Quase tão boa, e não depende de regra |
| **Restringir origem no firewall** | ✅✅ | Boa. Precisa ser mantida |
| **DROP em vez de REJECT** | ✅ | Deixa a varredura lenta. Não impede |
| **Mudar de porta (22 → 2222)** | ⚠️ | **Não é segurança.** Reduz ruído de log. Um scan completo acha em segundos |
| **Port knocking / SPA** | ✅ | Funciona de verdade, mas complica operação |
| **Esconder o banner** | ⚠️ | Ofuscação. Reduz ruído automatizado, não corrige nada |
| **Tarpit / honeypot** | ✅ | Bom como detecção, não como bloqueio |

**Sobre mudar o SSH da 22 para outra porta** — a opinião profissional deste material,
declarada como opinião: **faça, mas saiba por quê.** O ganho real é que 99 % das tentativas
automatizadas contra a 22 somem do seu log, o que torna as tentativas restantes visíveis.
Isso tem valor operacional genuíno. O que **não** acontece é ficar mais seguro contra um
atacante que dedicou dez segundos a varrer você. Chamar isso de "segurança" leva a relaxar
no que importa: chave em vez de senha, `fail2ban`, e atualização.

---

## 8. Roteiro completo de auditoria

```bash
# ── 1. De dentro: o que existe
ss -tulpn > /tmp/dentro.txt
ss -tulpn | grep -vE '127\.0\.0\.|\[::1\]'      # só o exposto
cd 07-projeto-modelo && python3 auditor.py local --json > /tmp/inventario.json

# ── 2. De fora, da mesma rede: o que a rede local vê
nmap -sV -Pn -p- --min-rate 1000 <ip-interno> -oA /tmp/interno

# ── 3. De fora, da internet: o que o mundo vê
nmap -sV -Pn --top-ports 1000 <ip-público> -oA /tmp/externo

# ── 4. Passivo: o que já está indexado
#     consulte o Shodan/Censys pelo IP e pelo domínio

# ── 5. Confronte
#     algo em 3 que não está em 1?  → NAT, balanceador, ou máquina errada
#     algo em 1 que não está em 3?  → firewall funcionando ✅
#     algo em 4 que não está em 3?  → um ativo que você não sabia que existia ⚠️
```

O passo 5 é a auditoria. Os passos 1–4 são só coleta.

---

## Autoteste

1. `ss` mostra `LISTEN` e `nmap` mostra `filtered`. Isso é um problema? O que significa?
2. `nmap` mostra `open` e `ss` não mostra nada. Cite três explicações possíveis e o comando
   que distingue entre elas.
3. Qual a diferença entre `-sT` e `-sS`? Cite duas consequências práticas, além da velocidade.
4. Por que `-sF`/`-sN`/`-sX` não funcionam contra Windows — e como essa falha virou uma
   funcionalidade?
5. Por que `-Pn` é quase sempre necessário hoje? O que acontece sem ele contra um servidor
   Windows?
6. O que o `masscan` faz de radicalmente diferente do `nmap`, e por que isso permite varrer
   a internet inteira?
7. Um auditor exige que você remova o banner do Apache. A recomendação faz sentido? Responda
   com precisão, sem cair em nenhum dos dois extremos.
8. Como a descoberta passiva (Shodan) muda o jogo para o atacante e para o defensor?
9. Trocar o SSH da porta 22 para a 2222 é uma medida de segurança? Argumente os dois lados
   e dê sua recomendação.

---

*Próximo: [`18-firewall-nat-e-o-caminho.md`](18-firewall-nat-e-o-caminho.md) — por que a porta que você abriu não responde.*
