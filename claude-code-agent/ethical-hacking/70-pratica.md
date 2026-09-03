# 70 · Prática — 12 laboratórios progressivos

`Nível: iniciante → avançado` · `Última atualização: 12/08/2026`

Teoria sem mãos é conhecimento morto. Estes 12 laboratórios levam do `nmap localhost` ao
comprometimento de um domínio inteiro. Cada um tem: objetivo, ambiente, passos, verificação e o
que você deve ter aprendido. Faça na ordem.

> ⚖️ Todos rodam no **seu** laboratório ([`03`](03-instalacao.md)) ou em plataformas que
> autorizam explicitamente (THM, HTB, PortSwigger). Nunca contra terceiros. Ver [`12`](12-etica-lei-e-contrato.md).

**Regra de todos os labs:** anote comando + saída à medida que avança. Ao final, escreva um
write-up curto. Quem não anota, refaz.

---

## Lab 1 · Seu primeiro scan (nível: trivial)
**Objetivo:** entender saída de nmap. **Ambiente:** Kali + Metasploitable 2.
```bash
sudo nmap -sV -sC -p- -oN lab1.txt 192.168.56.20
```
**Verificação:** você consegue listar 5 serviços e suas versões, e explicar o que cada flag fez.
**Aprendeu:** ler versões é o mapa do tesouro ([`15`](15-varredura-e-enumeracao.md)).

## Lab 2 · Enumeração de serviço (fácil)
**Objetivo:** extrair informação de um serviço sem exploit. **Ambiente:** Metasploitable 2.
```bash
nc 192.168.56.20 21          # banner do FTP
smbclient -L //192.168.56.20/ -N   # shares SMB anônimos
snmpwalk -v2c -c public 192.168.56.20 2>/dev/null | head
showmount -e 192.168.56.20   # exports NFS
```
**Verificação:** você achou ao menos um share acessível e a versão exata do Samba.
**Aprendeu:** enumeração entrega o mapa de graça ([`15`](15-varredura-e-enumeracao.md) §7).

## Lab 3 · Primeira exploração (fácil)
**Objetivo:** comprometer com e sem Metasploit. **Ambiente:** Metasploitable 2, vsftpd 2.3.4.
Faça o Caminho A (manual) e o Caminho B (msf) de [`04-como-comecar.md`](04-como-comecar.md) §4.
**Verificação:** `id` retorna `uid=0(root)` pelos dois caminhos.
**Aprendeu:** o mecanismo por trás da ferramenta ([`16`](16-vulnerabilidades-e-exploracao.md)).

## Lab 4 · SQL Injection na mão (fácil-médio)
**Objetivo:** do `'` ao dump de credenciais. **Ambiente:** DVWA (Docker, nível "low"→"medium").
Siga [`06-exemplos.md`](06-exemplos.md) ex. 3. Depois automatize com `sqlmap -r req.txt`.
**Verificação:** você extraiu a tabela de usuários manualmente **e** com sqlmap.
**Aprendeu:** por que prepared statements matam a classe ([`18`](18-seguranca-web.md) §4).

## Lab 5 · A trilha web da PortSwigger (médio)
**Objetivo:** dominar as classes web. **Ambiente:** [PortSwigger Academy](https://portswigger.net/web-security) (grátis).
Complete: **SQL injection** (todas), **XSS** (refletido, armazenado, DOM), **Access control**
(todas — é a nº 1). Mínimo: 20 labs.
**Verificação:** 20+ labs resolvidos, com Burp.
**Aprendeu:** o Top 10 na prática, com a melhor ferramenta didática que existe.

## Lab 6 · O projeto-modelo completo (médio)
**Objetivo:** um ciclo de pentest inteiro. **Ambiente:** [`07-projeto-modelo/`](07-projeto-modelo/README.md).
Leia o escopo, faça o roteiro manual, rode o teste automatizado (5/5), estude as correções,
faça o retest (0/5).
**Verificação:** você mapeou cada falha a uma categoria OWASP e entendeu a correção.
**Aprendeu:** que o relatório é o produto ([`24`](24-relatorio-e-comunicacao.md)).

## Lab 7 · Escalada de privilégio Linux (médio)
**Objetivo:** de usuário a root. **Ambiente:** [TryHackMe "Linux PrivEsc"](https://tryhackme.com/room/linuxprivesc) ou uma VulnHub.
```bash
./linpeas.sh
sudo -l ; find / -perm -4000 -type f 2>/dev/null ; getcap -r / 2>/dev/null
```
Use o [GTFOBins](https://gtfobins.github.io) para o binário que achar.
**Verificação:** você escalou por **dois** vetores diferentes (sudo e SUID).
**Aprendeu:** menor privilégio violado ([`17`](17-pos-exploracao-e-movimentacao.md) §3).

## Lab 8 · Reverse shell e estabilização (médio)
**Objetivo:** shell interativo estável. **Ambiente:** qualquer máquina que você comprometeu.
Siga [`06-exemplos.md`](06-exemplos.md) ex. 6, incluindo a estabilização de TTY.
**Verificação:** setas, `Ctrl+C` e `clear` funcionam no shell obtido.
**Aprendeu:** por que reverse fura firewall ([`16`](16-vulnerabilidades-e-exploracao.md) §3).

## Lab 9 · Quebra de senha (médio)
**Objetivo:** hashes → texto. **Ambiente:** hashes coletados nos labs anteriores.
```bash
hashid '<hash>'
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
hashcat -m <tipo> hashes.txt rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```
**Verificação:** quebrou hashes de tipos diferentes (MD5, NTLM, sha512crypt) e sabe por que
bcrypt resiste.
**Aprendeu:** hash é adivinhação, não descriptografia ([`06`](06-exemplos.md) ex. 5).

## Lab 10 · Uma máquina completa do HTB/THM (médio-difícil)
**Objetivo:** do zero ao root, sozinho. **Ambiente:** máquina "easy" do [Hack The Box](https://hackthebox.com) ou THM.
Recon → enumeração → foothold → privesc → flags. **Sem olhar write-up até tentar 2h.**
**Verificação:** user.txt e root.txt, e um write-up seu.
**Aprendeu:** juntar todas as fases sob raciocínio próprio.

## Lab 11 · Active Directory — a cadeia (difícil)
**Objetivo:** de sem-credencial a Domain Admin. **Ambiente:** [GOAD](https://github.com/Orange-Cyberdefense/GOAD) ou trilha AD do HTB.
Execute a cadeia de [`20-active-directory.md`](20-active-directory.md) §6: Responder →
hashcat → BloodHound → Kerberoasting → pass-the-hash → DCSync.
**Verificação:** você chegou a Domain Admin e mapeou cada passo a uma técnica ATT&CK.
**Aprendeu:** o que mais cai em entrevista de pentest corporativo.

## Lab 12 · Pivoting entre redes (difícil)
**Objetivo:** alcançar uma rede interna via host comprometido. **Ambiente:** rede multi-camada
(THM "Wreath", ou pro labs do HTB).
```bash
ssh -D 1080 user@pivot     # ou chisel/ligolo-ng
proxychains nmap -sT 10.10.20.0/24
```
**Verificação:** você escaneou e acessou uma máquina invisível de fora, via pivô.
**Aprendeu:** como um host vira a rede inteira ([`17`](17-pos-exploracao-e-movimentacao.md) §6).

---

## Depois dos 12: rotina sustentável

- **HTB/THM:** uma máquina por semana, subindo a dificuldade. Write-up sempre.
- **PortSwigger Academy:** termine todas as trilhas ao longo de alguns meses.
- **CTFs:** picoCTF, e eventos (CTFtime). Bom para pressão e criatividade.
- **Bug bounty:** quando tiver base web sólida, comece em programa de escopo amplo, expectativa
  realista ([`80`](80-custos-e-licencas.md)).
- **Especialize:** escolha rede/AD ou web/nuvem e aprofunde.

**A meta não é "terminar" — é a rotina.** Ver [`25`](25-carreira-passo-a-passo.md) §9.

---

## Autoteste

1. Por que cada lab pede um write-up ao final?
2. No Lab 3, por que fazer o caminho manual **e** o Metasploit?
3. Qual lab ensina a classe nº 1 do OWASP (Access Control), e onde?
4. Por que o Lab 6 (projeto-modelo) é o que mais se parece com um trabalho real?
5. No Lab 11, qual é a primeira credencial obtida e como?
6. O que o Lab 12 (pivoting) demonstra sobre o valor de um único host comprometido?
7. Depois dos 12 labs, qual é a "meta" real e por quê?
