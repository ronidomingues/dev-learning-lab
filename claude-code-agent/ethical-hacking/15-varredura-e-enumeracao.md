# 15 · Varredura e enumeração — TCP/IP e nmap por dentro

`Nível: intermediário → avançado` · `Última atualização: 12/08/2026`

Aqui você para de copiar comandos de nmap e passa a entender o que cada pacote faz. Sem isto,
você não interpreta resultados ambíguos nem evade defesas. Cobrimos TCP/IP no nível necessário
e o nmap por dentro.

---

## 1. O modelo de camadas, na prática do ataque

Você não precisa decorar as 7 camadas OSI, mas precisa saber **em que camada está o problema**:

| Camada | Exemplo | Ataque típico |
|---|---|---|
| 7 Aplicação | HTTP, DNS, SMB | SQLi, XSS, abuso de protocolo |
| 4 Transporte | TCP, UDP | scan de porta, SYN flood |
| 3 Rede | IP, ICMP | spoofing de IP, roteamento |
| 2 Enlace | Ethernet, ARP, MAC | ARP spoofing, MAC flooding (ver [`19`](19-redes-e-wireless.md)) |

O modelo TCP/IP condensa em 4 (Aplicação, Transporte, Internet, Enlace). Quando alguém diz
"ataque de camada 2", refere-se ao enlace — mesma rede local, ARP, switch.

## 2. TCP: o aperto de mão de três vias

TCP é confiável: antes de trocar dados, cliente e servidor fazem um **handshake**:

```
Cliente  --- SYN --->        Servidor     "quero conversar"
Cliente  <-- SYN/ACK ---     Servidor     "pode, e eu também"
Cliente  --- ACK --->        Servidor     "combinado"  → conexão aberta
```

Entender isto explica **todos** os tipos de scan:

- **Porta aberta:** o `SYN` recebe `SYN/ACK`.
- **Porta fechada:** o `SYN` recebe `RST` (reset).
- **Porta filtrada (firewall):** o `SYN` não recebe nada (drop silencioso) ou um ICMP de
  "proibido". É por isso que "filtrada" ≠ "fechada": você não sabe se há algo lá, só que algo
  bloqueia.

## 3. Os tipos de varredura do nmap — o que muda por dentro

| Scan | Flag | O que envia | Precisa root? | Furtividade |
|---|---|---|---|---|
| **SYN / half-open** | `-sS` | SYN, e responde o SYN/ACK com RST (não completa) | sim | 🔥 padrão; rápido, não registra conexão completa |
| **TCP connect** | `-sT` | handshake completo (via SO) | não | mais lento, registra conexão (log do serviço) |
| **UDP** | `-sU` | datagrama UDP | sim | lento; ausência de resposta é ambígua |
| **ACK** | `-sA` | só ACK | sim | não acha porta aberta; mapeia regra de firewall |
| **FIN/NULL/Xmas** | `-sF/-sN/-sX` | flags incomuns | sim | evasão de firewalls antigos (RFC 793) |

**Por que o SYN scan (`-sS`) é o padrão:** ele manda o SYN, vê a resposta, e **corta com RST**
antes de completar o handshake. Como a conexão nunca "abre" de fato, muitos serviços não a
registram no log de aplicação — daí "half-open" ou "stealth". Precisa de root porque monta o
pacote TCP na mão (socket cru, `CAP_NET_RAW`). Sem root, o nmap cai para `-sT`, que usa o
sistema operacional para conectar de verdade (mais lento e mais visível). **Este é o motivo de
`sudo nmap`.**

**UDP é diferente e frustrante:** UDP não tem handshake. Sem resposta pode significar "aberto"
ou "filtrado" — ambíguo. Por isso `-sU` é lento (o nmap espera e repete) e você foca nas portas
UDP que importam: 53 (DNS), 161 (SNMP), 123 (NTP), 500 (IKE), 69 (TFTP).

## 4. Detecção de versão e de SO

```bash
sudo nmap -sV --version-intensity 9 ALVO    # sonda o serviço para extrair versão exata
sudo nmap -O ALVO                            # adivinha o SO pela "impressão digital" da pilha TCP
```
- **`-sV`** manda sondas e compara a resposta com uma base de assinaturas (`nmap-service-probes`).
  É o que transforma "porta 21 aberta" em "vsftpd 2.3.4" — a informação que você pesquisa.
- **`-O`** analisa detalhes sutis de como o SO monta pacotes (TTL inicial, tamanho de janela,
  ordem de opções TCP) para adivinhar Windows/Linux/etc. Menos confiável que `-sV`.

## 5. Nmap Scripting Engine (NSE) — o canivete

O nmap tem ~600 scripts em Lua para enumeração e checagem de vulnerabilidade:

```bash
sudo nmap -sC ALVO                                  # scripts da categoria "default" (seguros)
sudo nmap --script smb-enum-shares,smb-os-discovery -p445 ALVO
sudo nmap --script "vuln" ALVO                      # checa vulnerabilidades conhecidas
sudo nmap --script "http-*" -p80,443 ALVO           # todos os scripts HTTP
```
Categorias: `safe`, `default`, `discovery`, `auth`, `vuln`, `exploit`, `intrusive`, `dos`, `brute`.

> ⚠️ **Nunca** rode `--script=all` ou categorias `dos`/`exploit`/`intrusive` em produção sem
> autorização explícita: alguns scripts derrubam serviços. Este é um erro que já custou
> contratos.

## 6. Estratégia de varredura eficiente

Escanear 65535 portas com `-sV -sC` em toda a faixa é lento. A estratégia de veterano é em
etapas:

```bash
# 1. Rápido: descobre QUAIS portas estão abertas (só SYN, todas as portas)
sudo nmap -p- --min-rate 5000 -T4 ALVO -oG portas.txt

# 2. Extraia as portas abertas
PORTAS=$(grep -oP '\d+/open' portas.txt | cut -d/ -f1 | paste -sd,)

# 3. Profundo: só nas portas abertas, com versão e scripts
sudo nmap -sV -sC -p"$PORTAS" ALVO -oA detalhe
```
Assim a parte lenta (`-sV -sC`) só roda nas poucas portas que interessam, não em 65535.
`masscan` e `rustscan` fazem a etapa 1 ainda mais rápido em redes grandes.

## 7. Enumeração — depois de achar, extraia tudo

Achar a porta é 20%. Enumerar o serviço é 80%. Por serviço comum:

| Porta | Serviço | Enumerar com |
|---|---|---|
| 21 | FTP | `nc` (banner), login anônimo, `nmap --script ftp-*` |
| 22 | SSH | versão (CVEs), métodos de auth, chaves fracas |
| 25 | SMTP | `VRFY`/`EXPN` (enumerar usuários), open relay |
| 53 | DNS | transferência de zona (`dig axfr @ALVO empresa.com`) |
| 80/443 | HTTP | `whatweb`, `ffuf`, `nuclei` (ver [`18`](18-seguranca-web.md)) |
| 88 | Kerberos | indica DC de AD (ver [`20`](20-active-directory.md)) |
| 111/2049 | NFS | `showmount -e ALVO` |
| 139/445 | SMB | `netexec smb`, `enum4linux-ng`, sessão nula |
| 161 | SNMP | `snmpwalk -c public` (community padrão vaza muito) |
| 389/636 | LDAP | `ldapsearch`, enumeração de AD |
| 1433/3306/5432 | SQL Server/MySQL/Postgres | versão, credenciais padrão |
| 3389 | RDP | versão, NLA, BlueKeep |

**Achado nº 1 de enumeração:** SMB com **sessão nula** (login vazio) listando
compartilhamentos e usuários; SNMP com community `public`; DNS com transferência de zona
liberada. Todos entregam o mapa da rede de graça.

## 8. Sobre ser detectado

Toda varredura é detectável. O que muda é o quanto:
- `-T4/-T5` são rápidos e barulhentos (bons para lab, arriscados em red team).
- `-T0/-T1/-T2` são lentos e mais furtivos.
- `-Pn` (não pinga) evita o primeiro sinal, mas escaneia tudo mesmo hosts mortos (lento).
- Evasão: `-f` (fragmentar), `-D` (iscas), `--source-port`, `--scan-delay`. Contra IDS moderno,
  isso é fraco — evasão séria é outro tema. Para pentest comum, você **quer** ser eficiente,
  não invisível: o cliente sabe que você está testando.

## 9. Os cinco porquês: por que existe "porta filtrada"?

**Por quê 1** — Por que o nmap às vezes diz "filtered" em vez de aberta/fechada?
Porque não recebeu resposta nenhuma ao SYN — nem SYN/ACK (aberta), nem RST (fechada).

**Por quê 2** — Por que não recebeu resposta?
Porque algo no caminho (firewall) **descartou** o pacote silenciosamente, em vez de responder.

**Por quê 3** — Por que o firewall descarta em silêncio em vez de mandar RST?
Decisão de design defensivo: responder (mesmo com RST) confirma que há um host ali. O silêncio
(`DROP`) esconde a existência do host — não dá ao atacante nem a informação "estou aqui,
fechado".

**Por quê 4** — Por que esconder a existência ajuda a defesa?
Porque aumenta o custo do recon: o atacante não distingue "não existe" de "existe e bloqueado",
e precisa gastar mais tempo/pacotes para desambiguar. Segurança por aumento de custo, não por
impossibilidade.

**Por quê 5** — Qual é a parada?
Uma **decisão de engenharia** com trade-off: `DROP` é mais furtivo mas atrapalha diagnóstico
legítimo de rede e viola o "princípio da menor surpresa" do TCP (que espera RST). `REJECT`
(responder) é mais amigável e menos furtivo. Não há resposta única certa — é escolha do
administrador entre furtividade e diagnosticabilidade. É por isso que "filtered" existe: é a
sombra dessa escolha.

---

## Autoteste

1. Descreva o handshake TCP de três vias e diga o que cada resposta (SYN/ACK, RST, nada)
   significa num scan.
2. Por que o SYN scan (`-sS`) é chamado de "half-open" e por que exige root?
3. O que o nmap faz para transformar "porta 21 aberta" em "vsftpd 2.3.4"?
4. Por que a varredura UDP é lenta e ambígua?
5. Descreva a estratégia de varredura em duas etapas e por que ela é mais rápida.
6. Cite três serviços cuja enumeração frequentemente "entrega o mapa de graça".
7. Por que você **não** roda `--script=all` em produção?
8. Explique por que existe o estado "filtered" e o trade-off por trás dele.
