# Projeto-modelo — Auditor de Portas

**Nível:** intermediário · **Executado e verificado em:** 14/08/2026, Ubuntu 22.04.5 LTS, Python 3.10.12

Uma aplicação pequena porém inteira que responde às três perguntas do curso:

1. **Quais portas minha máquina abriu, e quem alcança cada uma?** (lendo `/proc`, sem chamar `ss`)
2. **Quais portas aquele host mostra para mim?** (varredura TCP `connect()` concorrente)
3. **Por que as duas respostas discordam?** (o subcomando `comparar` — a parte mais instrutiva)

Zero dependências externas. Só a biblioteca padrão do Python 3.10+.

---

## Aviso legal, antes de qualquer comando

Varrer portas da **sua** máquina e da **sua** rede é administração de sistemas normal.
Varrer máquina de terceiro sem autorização escrita é, no Brasil, potencialmente enquadrável
no **art. 154-A do Código Penal** (invasão de dispositivo informático, redação da Lei
14.155/2021), e viola o contrato de praticamente todo provedor de internet e de nuvem.

O programa se recusa a varrer alvos fora de loopback e das faixas privadas (RFC 1918) sem a
flag `--autorizado`. Essa flag é **uma declaração sua**, não uma permissão nossa — e ela existe
para te obrigar a parar meio segundo e pensar antes de digitar.

---

## Pré-requisitos

| Item | Versão mínima | Como conferir |
|---|---|---|
| Python | 3.10 | `python3 --version` |
| Sistema | Linux (kernel com `/proc/net/tcp`) | `ls /proc/net/tcp` |

O subcomando `varrer` funciona em qualquer sistema com Python. Os subcomandos `local` e
`comparar` leem `/proc` e portanto **só funcionam em Linux** — em macOS e Windows, o programa
avisa e indica o comando equivalente. Não é limitação de preguiça: a fonte de dados de sockets
nesses sistemas é outra API (`sysctl`/`libproc` no macOS, `GetExtendedTcpTable` no Windows),
e reimplementá-las esconderia a lição em vez de mostrá-la.

Nada precisa ser instalado. Nada precisa de `sudo` — e o que você **não** enxerga sem `sudo`
é parte do que o projeto ensina.

---

## Como rodar

```bash
cd 07-projeto-modelo

# 1. a suíte de testes (39 s de leitura, 0,3 s de execução)
python3 testes.py

# 2. o que esta máquina expõe
python3 auditor.py local --apenas-expostas

# 3. o mesmo, em JSON, para pipeline de CI
python3 auditor.py local --json | python3 -m json.tool | head -40

# 4. varredura da própria máquina, com leitura de banner
python3 auditor.py varrer 127.0.0.1 -p top100 --banner

# 5. o confronto: kernel × rede
python3 auditor.py comparar -p 1-10000
```

Em outro terminal, para ter um gabarito do que deveria aparecer:

```bash
python3 alvo_laboratorio.py --base 19000
```

---

## Estrutura

```
07-projeto-modelo/
├── auditor.py            CLI. Três subcomandos = as três perguntas do curso.
├── inventario.py         Lê /proc/net/{tcp,tcp6,udp,udp6} e resolve inode → PID.
│                         É o `ss` reimplementado, para não sobrar caixa-preta.
├── varredura.py          Scanner TCP connect() concorrente + banner + guarda de autorização.
├── catalogo.py           Base de ~70 portas: nome, protocolo de aplicação, e RISCO SE EXPOSTA.
│                         O /etc/services diz o nome; o julgamento é este arquivo.
├── relatorio.py          Onde catálogo encontra inventário e vira decisão.
├── alvo_laboratorio.py   Sobe portas controladas para você varrer com gabarito.
└── testes.py             41 testes (unittest, biblioteca padrão).
```

---

## O que cada decisão de projeto ensina

### 1. Ler `/proc` à mão em vez de chamar `ss`

`inventario._decodifica_endereco` converte `0100007F:0016` em `("127.0.0.1", 22)`.
O IP está em **hexadecimal, na ordem de bytes do host** — little-endian no x86, por isso
`127.0.0.1` vira `0100007F` e parece embaralhado. Não é ofuscação: é o inteiro de 32 bits
despejado como estava na memória do kernel, em 1993, quando ninguém imaginou que isso
viraria interface pública. É o motivo de o `netstat` ser lento (relê e reprocessa texto)
e de o `ss` ser rápido (fala netlink, binário, e filtra no kernel).

Depois de escrever essas 12 linhas você nunca mais vai olhar a saída do `ss` como mágica.

### 2. Resolver o dono do socket cruzando i-node com `/proc/<pid>/fd`

Não existe campo "PID" na tabela de sockets. O kernel só grava o número de i-node do socket.
Para descobrir o dono é preciso varrer **todos** os processos procurando um link simbólico
`socket:[12345]`. É por isso que `ss -tlnp` sem `sudo` mostra a porta mas não o processo:
a tabela `/proc/net/tcp` é legível por todos, mas `/proc/<pid>/fd` de outro usuário não é.

Isso aparece na saída real deste projeto como `(sem permissão)` — e é a resposta certa,
não uma falha.

### 3. Classificar pelo par (porta, escopo), nunca pela porta sozinha

A tese central. Postgres em `127.0.0.1:5432` é higiene; o **mesmo** Postgres em
`0.0.0.0:5432` é um incidente esperando data. O `relatorio.classificar` implementa
exatamente isso, e há dois testes lado a lado provando que a única diferença entre `ok` e
`critico` é o IP de bind.

Ferramenta que classifica risco por número de porta produz relatório inútil: ou grita com
tudo, ou não grita com nada.

### 4. Distinguir os três desfechos de `connect()`

```
conecta        → ABERTA    (veio SYN-ACK: existe processo escutando)
ECONNREFUSED   → FECHADA   (veio RST: a máquina existe, ninguém escuta ali)
timeout        → FILTRADA  (nada voltou: alguém descartou em silêncio)
```

O terceiro caso é o que separa "não tem serviço" de "tem firewall" — e é a informação que
o iniciante joga fora ao escrever `if conecta: print("aberta")`.

### 5. `allow_reuse_address = True` no laboratório

Sem isso, reiniciar o `alvo_laboratorio.py` em menos de ~60 segundos falha com
`Address already in use`, porque o socket anterior ainda está em `TIME_WAIT`.
Uma linha de código que existe por causa de uma decisão de projeto do TCP de 1981.

### 6. `--json` e código de saída

`auditor.py local` sai com **1** se houver algo classificado como crítico. Isso o torna
utilizável como *gate* de pipeline:

```bash
python3 auditor.py local --apenas-expostas --sem-cor || echo "bloqueando o deploy"
```

Tutorial nenhum faz isso; sistema de produção nenhum vive sem.

### 7. Uma limitação deliberada, deixada à vista

O leitor de banner só envia sonda para portas que **ele já sabe** que falam HTTP
(`varredura.SONDAS`). Rode contra o laboratório e veja: a porta 19000 (que fala primeiro)
entrega o banner; a 19001, que é HTTP num número desconhecido, aparece como `(sem banner)`.

Esse é exatamente o problema que o `nmap -sV` resolve com uma base de milhares de sondas e
expressões regulares (`nmap-service-probes`). Escrever essa base é o trabalho de 25 anos que
separa um script de fim de semana de uma ferramenta. Deixamos a lacuna aparente de propósito
— e ela é o exercício 3 do `70-pratica.md`.

---

## Saída real — executada em 14/08/2026

### Suíte de testes

```
$ python3 testes.py
...
Ran 41 tests in 0.318s

OK
```

### Inventário local (recortado)

```
$ python3 auditor.py local --apenas-expostas --sem-cor
INVENTÁRIO DE PORTAS LOCAIS
faixa efêmera deste host: 32768-60999  (28232 portas de origem disponíveis)

          PROTO  ENDEREÇO LOCAL             ESCOPO               PROCESSO                 MOTIVO
------------------------------------------------------------------------------------------------
CRITICO   tcp    0.0.0.0:445                todas-interfaces     (sem permissão)          microsoft-ds: Compartilhamento de arquivos Windows. Alvo de EternalBlue/WannaCry.
CRITICO   tcp    0.0.0.0:139                todas-interfaces     (sem permissão)          netbios-ssn: SMB sobre NetBIOS. Legado; use 445.
CRITICO   udp    0.0.0.0:137                todas-interfaces     (sem permissão)          netbios-ns: Resolução de nomes NetBIOS. Legado.
ATENCAO   tcp    :::80                      todas-interfaces     (sem permissão)          http: Web sem criptografia.
ATENCAO   tcp    0.0.0.0:3001               todas-interfaces     MainThread[187918]       serviço não catalogado exposto — identifique antes de liberar
ATENCAO   udp    :::33120                   todas-interfaces     (sem permissão)          porta na faixa efêmera escutando para fora — quase sempre um servidor de desenvolvimento esquecido
OK        udp    0.0.0.0:5353               todas-interfaces     (sem permissão)          mdns: exposição usual para este serviço

RESUMO: 35 sockets em escuta · 14 crítico(s) · 19 atenção · 2 ok
$ echo $?
1
```

### Varredura com banner

```
$ python3 auditor.py varrer 127.0.0.1 -p top100 -t 2 -P 50 --banner --sem-cor
VARREDURA DE 127.0.0.1 — 98 portas testadas

PORTA    SERVIÇO ESPERADO       ms       BANNER / EVIDÊNCIA
-------------------------------------------------------------------------------
23       telnet                 0.6      (sem banner)
25       smtp                   0.6      (sem banner)
80       http                   0.4      HTTP/1.1 200 OK Date: Fri, 14 Aug 2026 16:39:35 GMT Server: Apache/2.4.52 (Ubuntu) ...
139      netbios-ssn            1.4      (sem banner)
445      microsoft-ds           1.7      (sem banner)
631      ipp                    1.7      (sem banner)
3306     mysql                  0.6      [    8.0.46-0ubuntu0.22.04.3 ... caching_sha2_password
5000     (dev)                  0.7      (sem banner)
8080     http-alt               0.3      (sem banner)
27017    mongodb                0.7      (sem banner)

abertas: 10 · fechadas (RST): 73 · filtradas (silêncio): 15
```

Repare em duas coisas nessa saída, ambas reais:

- **O MySQL entrega a versão exata antes de qualquer autenticação.** `8.0.46-0ubuntu0.22.04.3`
  diz a versão, a distribuição e o nível de patch. Quem varre não precisa invadir para saber
  se você aplicou a correção do mês passado.
- **O Apache diz `Apache/2.4.52 (Ubuntu)`** porque `ServerTokens` está no padrão da distro.

### O confronto — e o achado

```
$ python3 auditor.py comparar -p 1-10000
CONFRONTO — 127.0.0.1, 10000 portas testadas

  concordam (kernel diz LISTEN e a rede conecta): 8
    [80, 139, 445, 631, 3001, 3306, 5173, 9050]

  só o kernel vê (LISTEN mas a conexão não completa): 3
        53  → escuta em IP específico que não é 127.0.0.1, ou firewall local
      9789  → escuta em IP específico que não é 127.0.0.1, ou firewall local
      9879  → escuta em IP específico que não é 127.0.0.1, ou firewall local

  só a rede vê (conecta, mas NENHUM processo escuta): 2
      2222  → redirecionamento no kernel, proxy transparente, agente de segurança, ou honeypot
      3128  → redirecionamento no kernel, proxy transparente, agente de segurança, ou honeypot
```

**O caso da porta 53:** o `systemd-resolved` escuta em `127.0.0.53:53`, não em `127.0.0.1:53`.
São endereços de loopback diferentes (todo o `127.0.0.0/8` é loopback). O kernel vê o LISTEN;
a varredura de `127.0.0.1` não alcança. Isso não é bug de nenhum dos dois — é o motivo pelo
qual "escutar em loopback" é uma frase imprecisa.

**O caso das portas 2222 e 3128:** `connect()` completa, mas **nenhum processo** está escutando.
Só há uma explicação possível: uma regra no kernel está redirecionando a conexão para outro
lugar antes que ela chegue a um socket. Na máquina onde este curso foi escrito — um notebook
corporativo — o `nmap` chegou a reportar 25 portas "abertas" em `127.0.0.1` (23, 25, 110, 143,
389, 443, 587, 3128, 5000, 7001, 8080, 8090, 8888, 9200, 10000, 1801, 2222...) das quais o
`ss` só confirmava 8. Não conseguimos confirmar a causa sem `sudo`, e **estamos dizendo isso
em vez de inventar**. As hipóteses, em ordem de plausibilidade: agente de segurança corporativo
com regra `REDIRECT`, proxy transparente de inspeção, ou um honeypot de detecção interna.

O comando que resolveria (e que você deve rodar na sua máquina):

```bash
sudo iptables -t nat -S | grep -E 'REDIRECT|DNAT|TPROXY'
sudo nft list ruleset | grep -E 'redirect|dnat|tproxy'
```

Esse achado — descoberto durante a escrita, não planejado — é a melhor demonstração possível
da tese do subcomando: **"a porta está aberta" é uma afirmação sobre o caminho inteiro, não
sobre um processo.**

---

## O que foi executado e o que não foi

**Executado e verificado nesta máquina (14/08/2026):** os 41 testes; os três subcomandos;
o `alvo_laboratorio.py` com varredura do próprio gabarito antes e depois de encerrar
(3 abertas → 0 abertas, 6 fechadas); as saídas mostradas acima são reais, inclusive as
divergências.

**Não executado:** `local` e `comparar` em macOS e Windows (o programa recusa e indica o
equivalente); varredura de rede externa (por escolha, não por limitação).

---

## Exercícios sobre este código

1. `catalogo.py` cataloga ~70 portas. Adicione as 10 que **sua** empresa usa e que não estão lá.
2. Faça `classificar()` rebaixar a severidade quando o processo dono for conhecido e esperado
   (ex.: `sshd` em 22 não deveria gritar tanto quanto um `nc -l` em 22).
3. Implemente a base de sondas: leia `/usr/share/nmap/nmap-service-probes` e use as
   expressões regulares dele para identificar serviço e versão. Compare seu resultado com
   `nmap -sV` na mesma porta. (É a lacuna deliberada da seção 7.)
4. Acrescente `varrer --udp`. Descubra por que é muito mais difícil, e por que o `nmap -sU`
   é lento. Dica: leia [`14-udp-e-os-outros.md`](../14-udp-e-os-outros.md) antes.
5. Faça o `local` guardar um histórico em JSON e alertar quando uma porta **nova** aparecer.
   É assim que ferramenta de detecção de mudança funciona de verdade.

---

*Ver também: [`04-como-comecar.md`](../04-como-comecar.md) · [`70-pratica.md`](../70-pratica.md) · [`75-armadilhas.md`](../75-armadilhas.md)*
