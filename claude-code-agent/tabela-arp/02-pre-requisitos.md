# 02 · Pré-requisitos

> **Nível:** iniciante
> **Data:** 14/08/2026

Este arquivo responde: *o que preciso saber, ter e instalar antes de começar — e o que faço
se me faltar alguma coisa?*

---

## 1. Conhecimento

### 1.1 Indispensável

Sem isso, o material dos capítulos 10 em diante fica ininteligível.

| Você precisa saber | Como testar se sabe | Onde aprender se não sabe |
|---|---|---|
| **Usar um terminal**: abrir, digitar comando, ler saída, entender que `$` não faz parte do comando | Rode `ls` (Linux/macOS) ou `dir` (Windows) e explique a saída | [Curso em Vídeo — Linux básico](https://www.cursoemvideo.com/) · `man bash` |
| **O que é um endereço IP** e que ele tem quatro números de 0–255 | Diga qual é o seu, sem consultar | seção 2 deste arquivo, e [10-fundamentos](10-fundamentos.md) §2 |
| **O que é uma rede local** vs. **a Internet** | Explique por que o roteador da sua casa tem dois endereços | [01-introducao-leigo](01-introducao-leigo.md) §2 |
| **Hexadecimal**: saber que `ff` = 255 e que dois dígitos hex = 1 byte | Converta `0x0806` para decimal (resposta: 2054) | seção 3 deste arquivo |
| **Bit e byte**: 1 byte = 8 bits | Quantos bytes tem um MAC de 48 bits? (resposta: 6) | seção 3 deste arquivo |

### 1.2 Ajuda muito (mas dá para começar sem)

| Assunto | Por que ajuda | Onde |
|---|---|---|
| **Máscara de sub-rede e notação CIDR** (`/24`, `/20`) | É o que decide se o ARP será usado ou não para um destino. Sem isso, o capítulo 13 fica mecânico em vez de compreensível | seção 2.2 deste arquivo |
| **O modelo de camadas** (OSI ou TCP/IP) | Dá o vocabulário: "camada 2", "camada 3" | [10-fundamentos](10-fundamentos.md) §1 |
| **Python básico** | Só para o [07-projeto-modelo](07-projeto-modelo/) e alguns exemplos | qualquer curso introdutório |
| **Virtualização** (VirtualBox, KVM, Docker) | Permite montar um laboratório com 3 máquinas e ver ARP de verdade sem mexer na rede real | assunto [docker](../docker/00-MAPA.md) desta pasta |
| **Wireshark** | Ver o pacote ARP com os próprios olhos vale por dez páginas de texto | [70-pratica](70-pratica.md) lab 3 |
| **TCP/IP em geral** | Contexto | assunto [apis](../apis/00-MAPA.md) §HTTP, e Kurose (veja [90-bibliografia](90-bibliografia.md)) |

### 1.3 O que você **não** precisa saber

Para poupar você de estudar o que não vai usar aqui:

- não precisa saber programar em C, nem ler código do kernel (o capítulo
  [60](60-teoria-avancada.md) mostra trechos, mas explica cada um);
- não precisa saber configurar roteador Cisco (o capítulo
  [16](16-arp-em-cada-sistema.md) mostra os comandos, mas você não precisa ter um);
- não precisa de conta em nuvem, nem de cartão de crédito, nem de licença de nada.
  **Este assunto é 100% gratuito de estudar** — veja [80-custos-e-licencas](80-custos-e-licencas.md);
- não precisa de IPv6 funcionando (mas se tiver, o capítulo [20](20-ipv6-e-ndp.md) fica melhor).

---

## 2. O mínimo de rede que você precisa, agora

Se a tabela 1.1 assustou, esta seção resolve. São dez minutos.

### 2.1 Endereço IP

Um IPv4 é um número de **32 bits**, escrito como quatro grupos de 8 bits em decimal:

```
10.209.2.168
│  │   │  │
└──┴───┴──┴─ cada um vai de 0 a 255 (8 bits = 2⁸ = 256 valores)
```

Descubra o seu:

```bash
# Linux
ip -br addr show
# macOS
ifconfig | grep "inet "
```
```powershell
# Windows
ipconfig
```

Nesta máquina:

```
enp2s0  UP  10.209.2.168/20  fe80::16d7:8354:f414:7684/64
```

### 2.2 Máscara e o que é "a minha rede"

Aquele `/20` é a **máscara de sub-rede** em notação CIDR. Ele diz: *"os 20 primeiros bits
deste endereço identificam a rede; os 12 restantes identificam a máquina dentro dela."*

```
IP     10.209.2.168  =  00001010 11010001 00000010 10101000
/20                     └──────── 20 bits ───────┘└─ 12 bits ─┘
                              rede                  máquina
rede   10.209.0.0/20
faixa  10.209.0.1  até  10.209.15.254   (2¹² − 2 = 4094 endereços úteis)
```

**Por que isso importa para o ARP?** Porque é exatamente esse cálculo que a sua máquina faz,
para cada pacote que sai, para decidir entre duas coisas:

- destino **dentro** de `10.209.0.0/20` → *"é vizinho, vou resolver o MAC **dele** por ARP"*;
- destino **fora** → *"não é vizinho, vou resolver o MAC do **gateway** por ARP e entregar
  para ele"*.

Essa é a decisão central de todo o assunto. Está detalhada em
[13-o-ciclo-de-resolucao](13-o-ciclo-de-resolucao.md) §2.

Máscaras comuns:

| CIDR | Máscara decimal | Endereços úteis | Onde se vê |
|---|---|---|---|
| `/30` | 255.255.255.252 | 2 | enlaces ponto a ponto entre roteadores |
| `/24` | 255.255.255.0 | 254 | o padrão de rede doméstica e de VLAN pequena |
| `/23` | 255.255.254.0 | 510 | escritório médio |
| `/20` | 255.255.240.0 | 4094 | rede corporativa grande — **e já perto do limite prático** |
| `/16` | 255.255.0.0 | 65534 | quase sempre um erro de projeto em camada 2 |

O "erro de projeto" da última linha é justificado quantitativamente no
[60-teoria-avancada](60-teoria-avancada.md) §3: broadcast cresce com o quadrado do número de
hosts, e a tabela de vizinhos tem teto.

### 2.3 Gateway

O **gateway padrão** (*default gateway*) é o roteador para onde vai tudo que não é da sua rede.

```bash
ip route | grep default
# default via 10.209.0.1 dev enp2s0 proto static metric 20100
```

`10.209.0.1` é o gateway desta máquina. Guarde esse número: metade dos diagnósticos de rede
começa perguntando "a entrada ARP do gateway está boa?".

### 2.4 Endereço MAC

Já explicado em [01](01-introducao-leigo.md) §2. Descubra o seu:

```bash
ip -br link show
# enp2s0  UP  d0:94:66:99:99:99 <BROADCAST,MULTICAST,UP,LOWER_UP>
```

---

## 3. O mínimo de hexadecimal

O pacote ARP é descrito em bytes, e bytes se escrevem em hexadecimal. Dez minutos aqui
economizam confusão no capítulo [12](12-anatomia-do-pacote.md).

- **Hexadecimal** é base 16: os dígitos vão de `0` a `9` e depois `a`,`b`,`c`,`d`,`e`,`f`
  (que valem 10 a 15).
- **Um dígito hex = 4 bits.** Dois dígitos hex = 8 bits = **1 byte**. Por isso MAC (48 bits =
  6 bytes) é escrito com 12 dígitos hex em 6 pares.
- O prefixo `0x` marca "isto é hexadecimal": `0x0806`.

| Hex | Decimal | Onde aparece neste curso |
|---|---|---|
| `0x0001` | 1 | tipo de hardware = Ethernet; e opcode = request |
| `0x0002` | 2 | opcode = reply |
| `0x0800` | 2048 | EtherType de IPv4 (e "tipo de protocolo" no ARP) |
| `0x0806` | 2054 | **EtherType do ARP** — o número que identifica o pacote |
| `0x8035` | 32821 | EtherType do RARP |
| `0x8100` | 33024 | EtherType de VLAN (802.1Q) |
| `0xff` | 255 | byte cheio; `ff:ff:ff:ff:ff:ff` = broadcast |

Conversão rápida no terminal, útil o tempo todo:

```bash
printf '%d\n' 0x0806     # 2054
printf '0x%04x\n' 2054   # 0x0806
```
```python
>>> int("0806", 16)
2054
```

---

## 4. Ambiente

### 4.1 Requisitos mínimos

| Item | Mínimo | Observação |
|---|---|---|
| **Sistema operacional** | Linux, macOS ou Windows 10+ | os três têm ferramentas de ARP nativas; Linux tem as melhores |
| **Privilégio** | usuário comum para **ler**; administrador/root para **alterar e capturar** | você consegue fazer ~60% do curso sem `sudo` |
| **Rede** | **qualquer rede com pelo menos outro dispositivo** — Wi-Fi de casa serve | numa máquina isolada a tabela fica vazia e o curso perde o sentido |
| **Hardware** | qualquer coisa dos últimos 15 anos | ARP não consome nada |
| **Disco** | ~300 MB se instalar Wireshark; ~5 MB se ficar só na linha de comando | |
| **Internet** | só para baixar as ferramentas | o estudo em si é offline |
| **Conta em serviço** | **nenhuma** | |
| **Cartão de crédito** | **nenhum** | |

### 4.2 O aviso importante sobre a rede

> **Não faça os laboratórios de ataque (capítulo [18](18-seguranca.md), labs 9–11 do
> [70](70-pratica.md)) na rede da empresa, da faculdade ou do provedor.**
>
> *ARP spoofing* é interceptação de comunicação alheia. No Brasil, fazer isso sem autorização
> escrita cai no **art. 154-A do Código Penal** (invasão de dispositivo informático,
> pena de 1 a 4 anos) e possivelmente na Lei Geral de Proteção de Dados. Não é zona cinzenta.
>
> Faça num laboratório isolado — três VMs numa rede *host-only*, ou três containers numa rede
> Docker interna. O [03-instalacao](03-instalacao.md) §9 monta esse laboratório do zero,
> e o [07-projeto-modelo](07-projeto-modelo/) roda inteiro sem tocar em rede alheia.
> Veja também o assunto [ethical-hacking](../ethical-hacking/00-MAPA.md) desta pasta.

### 4.3 Situações que atrapalham

| Situação | Efeito | O que fazer |
|---|---|---|
| Máquina sozinha na rede (sem outros dispositivos) | tabela ARP com 1 entrada ou vazia | conecte-se a uma rede com mais gente, ou monte o lab do §9 do [03](03-instalacao.md) |
| Wi-Fi corporativo com **isolamento de cliente** | você só enxerga o gateway | idem |
| VPN ativa | o tráfego não passa por Ethernet; a tabela fica pobre | desative durante o estudo |
| Rede só IPv6 | não haverá ARP nenhum | vá para o [20-ipv6-e-ndp](20-ipv6-e-ndp.md) |
| Container sem `NET_ADMIN` | não dá para alterar a tabela | rode com `--cap-add=NET_ADMIN` |
| macOS 15+ / Windows 11 com firewall estrito | captura exige permissão explícita | veja [03](03-instalacao.md) §5 e §6 |

---

## 5. Tempo realista de estudo

Sem otimismo. Números de quem já ensinou isso e viu onde as pessoas travam.

| Objetivo | Tempo | O que você consegue fazer |
|---|---|---|
| **Ler a tabela e entender o que vê** | **30–45 min** | `01` + `04`. Suficiente para diagnosticar "está morto ou está vivo?" |
| **Usar no dia a dia com desenvoltura** | **4–6 h** | `01`–`06`. Ler estados, limpar cache, criar entrada estática, fazer o diagnóstico do `19` |
| **Entender o protocolo de verdade** | **12–20 h** | + `10`–`15`. Decodificar um pacote ARP à mão, explicar gratuitous ARP e proxy ARP sem consultar |
| **Nível operacional profissional** | **40–60 h** | + `16`–`19`, `70`, `75`. Projetar segmentação, dimensionar `gc_thresh`, configurar DAI, investigar incidente |
| **Nível de projeto/pesquisa** | **80–120 h** | + `20`, `60`, `65`. Discutir escala de camada 2, ler o código do kernel, avaliar ARP suppression em EVPN |

Observações honestas:

- a **primeira hora rende muito** — este é um assunto raro em que o retorno inicial é enorme.
  Ler a tabela ARP resolve problemas reais no primeiro dia;
- o **planalto vem no capítulo 14** (a máquina de estados). É a parte que exige releitura.
  Se travar ali, faça o lab 5 do [70](70-pratica.md) antes de continuar;
- o material do capítulo [17](17-arp-em-redes-reais.md) só "cai a ficha" para quem já
  administrou uma rede com VLAN. Se for o seu caso, ele vale sozinho o curso;
- este assunto **não envelhece**. O protocolo é de 1982 e não mudou. O que você aprender aqui
  vale por décadas — coisa rara em tecnologia. O que envelhece é o ecossistema em volta
  (ferramentas, nuvem), coberto nos capítulos `65` e `85`.

---

## 6. Rota de resgate

O que fazer se faltar um pré-requisito, sem abandonar o curso.

### "Não sei o que é máscara de sub-rede"

Faça só a seção 2.2 deste arquivo e a calculadora abaixo. Não precisa dominar sub-redes,
precisa entender *uma* pergunta: "este IP está na minha rede ou não?"

```bash
# Está 10.209.5.7 na minha rede 10.209.0.0/20? Sem instalar nada:
python3 -c "
import ipaddress
rede = ipaddress.ip_network('10.209.0.0/20')
for ip in ['10.209.5.7', '10.209.20.1', '8.8.8.8']:
    print(ip, 'na rede' if ipaddress.ip_address(ip) in rede else 'FORA -> vai pelo gateway')
"
```
```
10.209.5.7 na rede
10.209.20.1 FORA -> vai pelo gateway
8.8.8.8 FORA -> vai pelo gateway
```
*(executado nesta máquina, Python 3.10.12)*

### "Não tenho outra máquina na rede"

Três saídas, da mais barata para a mais completa:

1. **Use o celular no mesmo Wi-Fi.** Duas máquinas já bastam para ver um ciclo ARP inteiro.
2. **Docker** (uma linha, sem VM): `docker network create lab && docker run --rm -it --network lab alpine sh`.
   Suba dois containers e faça um pingar o outro. Detalhes em [03](03-instalacao.md) §9.2.
3. **Três VMs em rede *host-only*** no VirtualBox — o laboratório completo, necessário para os
   labs de ataque. [03](03-instalacao.md) §9.1.

### "Não posso instalar nada nesta máquina"

Você ainda consegue fazer **70% do curso**: `arp -a` e `ip neigh` já existem em toda
instalação padrão de Windows, macOS e Linux. O que você perde é a captura (Wireshark/tcpdump)
e os labs de ataque. Alternativas sem instalar em [03](03-instalacao.md) §2.

### "Não sei Python"

Só o [07-projeto-modelo](07-projeto-modelo/) e três exemplos do
[06](06-exemplos.md) usam Python, e todos rodam sem você entender o código. Leia a saída,
não a implementação. Volte ao código depois.

### "Travei no capítulo 14 (estados NUD)"

Sintoma clássico. Faça isto, nesta ordem:

1. rode o experimento de transição de estado do [04](04-como-comecar.md) §6 na sua máquina —
   ver acontecer resolve mais que reler;
2. leia o [13](13-o-ciclo-de-resolucao.md) de novo, focando no *porquê* de cada estado existir;
3. desenhe a máquina de estados no papel, com os tempos ao lado de cada seta;
4. só então volte ao 14.

---

## 7. Checklist antes de seguir

Marque tudo antes de ir para o [03-instalacao](03-instalacao.md):

- [ ] Sei abrir um terminal e rodar um comando.
- [ ] Sei qual é o meu IP e a minha máscara.
- [ ] Sei qual é o meu gateway.
- [ ] Sei qual é o MAC da minha placa.
- [ ] Sei dizer se `10.x.y.z` está ou não na minha rede.
- [ ] Sei que dois dígitos hexadecimais formam um byte.
- [ ] Estou numa rede com pelo menos mais um dispositivo (ou sei como criar um lab).
- [ ] Entendi que os laboratórios de ataque só se fazem em rede própria e isolada.

Se todos estão marcados, você pode inclusive pular o `03` e ir direto para o
[04-como-comecar](04-como-comecar.md) — nas instalações padrão de Linux, macOS e Windows,
as ferramentas de leitura **já estão instaladas**.

---

## Autoteste

1. Sua máquina é `192.168.1.50/24` e o gateway é `192.168.1.1`. Ela vai falar com
   `192.168.2.10`. De qual endereço ela vai buscar o MAC por ARP, e por quê?
2. Quantos bytes tem um endereço MAC? E um IPv4? Como você chegou a esses números?
3. Quanto vale `0x0806` em decimal, e o que esse número identifica?
4. Por que estudar ARP numa máquina isolada da rede não funciona?
5. Cite dois motivos legais e um técnico para não fazer ARP spoofing na rede da empresa.
6. Você tem 4 horas. Qual é a rota de leitura com melhor retorno, e o que ela deixa de fora?
7. Uma rede `/16` de camada 2 única é considerada erro de projeto. Sem ler o capítulo 60,
   arrisque o motivo.

---

**Fontes consultadas:** documentação `man ip-neighbour(8)` (iproute2 5.15.0, local);
Código Penal brasileiro, art. 154-A; execuções locais em 14/08/2026.

**Próximo:** [03-instalacao.md](03-instalacao.md)
