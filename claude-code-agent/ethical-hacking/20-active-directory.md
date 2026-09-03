# 20 · Active Directory — onde está o dinheiro corporativo

`Nível: avançado` · `Última atualização: 12/08/2026`

A maior parte dos pentests internos corporativos é, no fundo, um pentest de **Active Directory**.
Se você quer emprego em pentest de empresa, este é o assunto que mais paga. Este arquivo cobre
o essencial: como o AD funciona, os ataques centrais, e as defesas.

> ⚖️ Só em laboratório (GOAD — ver §9) ou escopo autorizado. Ataques AD são intrusivos.

---

## 1. O que é Active Directory e por que importa

**Active Directory (AD)** é o serviço de diretório da Microsoft que gerencia identidade e
acesso em redes Windows corporativas: usuários, computadores, grupos, políticas, tudo num
**domínio**. Um servidor **Domain Controller (DC)** é o coração — ele autentica todo mundo.

**Por que é o alvo:** comprometer o AD = comprometer a organização. Com privilégio de **Domain
Admin**, você controla todas as máquinas, todos os usuários, todos os dados. É o "xeque-mate"
do pentest interno. E como o AD é complexo e antigo, está cheio de caminhos de ataque.

## 2. Vocabulário mínimo

| Termo | O que é |
|---|---|
| **Domínio** | fronteira administrativa (ex.: `corp.local`) |
| **Domain Controller (DC)** | servidor que autentica e guarda o AD |
| **Floresta** | conjunto de domínios com confiança entre si |
| **OU** (Organizational Unit) | pasta para organizar objetos |
| **GPO** (Group Policy) | políticas aplicadas a usuários/máquinas |
| **SPN** (Service Principal Name) | identifica um serviço para o Kerberos |
| **Domain Admin (DA)** | o grupo que controla o domínio |
| **NTLM / Kerberos** | os dois protocolos de autenticação |

## 3. Como a autenticação funciona (e onde falha)

### NTLM (legado, ainda onipresente)
Prova identidade por desafio-resposta usando o **hash NTLM** da senha. Problema central: o
hash **é** a credencial — quem tem o hash autentica sem a senha. Daí o **pass-the-hash** (ver
[`06`](06-exemplos.md) ex. 12).

### Kerberos (padrão moderno)
Baseado em tickets. Simplificado:
```
1. Você prova identidade ao DC → recebe um TGT (Ticket Granting Ticket)
2. Apresenta o TGT → recebe um TGS (ticket para um serviço específico)
3. Apresenta o TGS ao serviço → acesso
```
Elegante, mas cada etapa tem um ataque associado. É a riqueza de alvos que faz o AD ser o AD.

## 4. Os ataques centrais do AD

### 4.1 LLMNR/NBT-NS Poisoning + captura de hash
Ponto de partida sem credencial (ver [`19`](19-redes-e-wireless.md) §3). `responder` captura
hashes NetNTLMv2; `hashcat -m 5600` quebra. **Defesa grátis:** desligar LLMNR e NBT-NS por GPO.

### 4.2 AS-REP Roasting
Usuários com "pré-autenticação Kerberos desabilitada" permitem pedir um material cifrado com o
hash deles **sem autenticar**. Quebra offline.
```bash
GetNPUsers.py corp.local/ -usersfile users.txt -no-pass -dc-ip 10.0.0.1
hashcat -m 18200 hashes.txt rockyou.txt
```
**Defesa:** não desabilitar pré-autenticação; senhas fortes.

### 4.3 Kerberoasting
Qualquer usuário autenticado pede tickets (TGS) de contas de serviço (com SPN); parte do
ticket é cifrada com o hash da conta de serviço → quebra offline, indetectável. Ver
[`06`](06-exemplos.md) ex. 11.
```bash
GetUserSPNs.py corp.local/joao:senha -dc-ip 10.0.0.1 -request
hashcat -m 13100 kerb.hash rockyou.txt
```
**Defesa:** **gMSA** (Group Managed Service Accounts — senhas longas, aleatórias, rotacionadas
automaticamente pela Microsoft), ou senhas de serviço de 25+ caracteres.

### 4.4 Pass-the-Hash / Pass-the-Ticket / Overpass-the-Hash
Reutilizar hash NTLM ou ticket Kerberos capturado para autenticar sem a senha. Base da
movimentação lateral. `netexec`, `psexec.py`, `evil-winrm`, mimikatz.
**Defesa:** LAPS (senhas de admin local únicas por máquina), tiering, credential guard.

### 4.5 DCSync
Com privilégio suficiente (direitos de replicação, que Domain Admins têm), pedir ao DC que
"replique" os hashes de **todos** os usuários — inclusive o `krbtgt`.
```bash
secretsdump.py corp.local/admin:senha@10.0.0.1
```
**Defesa:** limitar direitos de replicação, monitorar (evento de replicação anômala).

### 4.6 Golden / Silver Ticket (persistência)
Com o hash da conta **`krbtgt`** (obtido via DCSync), forja-se um TGT válido para **qualquer**
usuário, com validade arbitrária — o **golden ticket**, persistência quase indelével até
rotacionar o `krbtgt` (duas vezes). O **silver ticket** forja um TGS para um serviço específico.
**Defesa:** proteger o `krbtgt`, rotacioná-lo após comprometimento, detecção.

## 5. BloodHound — enxergar os caminhos de ataque

O AD tem tantas relações (quem é membro de quê, quem tem direito sobre quê) que os caminhos de
ataque ficam invisíveis a olho nu. O **BloodHound** coleta essas relações e as desenha como um
**grafo**, revelando o caminho mais curto de "usuário comum que comprometi" até "Domain Admin".
```bash
# Coleta (um dos coletores)
bloodhound-python -u joao -p senha -d corp.local -c all -ns 10.0.0.1
netexec ldap 10.0.0.1 -u joao -p senha --bloodhound --collection All
# Depois, importa no BloodHound CE e roda a query "Shortest Path to Domain Admins"
```
BloodHound transformou o pentest de AD: em vez de tentar às cegas, você vê o mapa. É a
ferramenta que materializa a ideia de "cadeia de ataque" ([`10`](10-fundamentos.md) §7.4).

## 6. O caminho típico (a cadeia)

Este é o Exemplo 14 de [`06`](06-exemplos.md), agora com os nomes técnicos:
```
sem credencial → Responder (LLMNR) → hash NetNTLMv2 → hashcat → 1ª credencial
→ BloodHound → acha caminho → Kerberoasting → hash de serviço → hashcat → conta privilegiada
→ pass-the-hash → host com sessão de DA → dump de credencial → DCSync → Domain Admin → objetivo
```
Cada seta é um ataque desta página. Cada seta tem uma defesa que a quebra. O relatório prioriza
por **elo** ([`24`](24-relatorio-e-comunicacao.md)).

## 7. As defesas que importam (para o relatório)

| Defesa | Quebra qual ataque | Custo |
|---|---|---|
| Desligar LLMNR/NBT-NS | poisoning/captura de hash | grátis (GPO) |
| Assinatura SMB obrigatória | relay NTLM | grátis |
| Senha forte + MFA | força bruta, roasting | baixo |
| gMSA para serviços | Kerberoasting | baixo |
| LAPS | pass-the-hash de admin local | baixo |
| Tiering administrativo | DA em estação → dump | processo |
| Monitorar DCSync/replicação | DCSync, golden ticket | ferramenta |
| Proteger/rotacionar krbtgt | golden ticket | processo |

**A mensagem central do relatório de AD:** a maioria dos elos se quebra com configuração
grátis ou barata. O problema raramente é falta de produto caro — é higiene não feita.

## 8. Azure AD / Entra ID — a nuvem mudou o jogo

Muitas empresas migraram para **Microsoft Entra ID** (o antigo Azure AD) ou híbrido. O modelo
muda: não há mais só DCs on-premises; há identidade na nuvem, tokens OAuth, *conditional
access*, e novos ataques (phishing de token, abuso de aplicativos, *illicit consent grant*,
pivot híbrido on-prem ↔ nuvem). É uma fronteira crescente do pentest em 2026 — ferramentas como
`ROADtools`, `AADInternals`, `GraphRunner`. Ver também [`21`](21-nuvem-e-containers.md).

## 9. Montar o laboratório de AD

- **GOAD (Game of Active Directory)** — [github.com/Orange-Cyberdefense/GOAD](https://github.com/Orange-Cyberdefense/GOAD):
  laboratório AD vulnerável, provisionado com Vagrant + Ansible. Padrão do mercado para estudo.
  Precisa de ~24–32 GB de RAM (ou a versão reduzida "GOAD-Light").
- **Alternativas:** montar à mão com ISOs de avaliação da Microsoft (180 dias), ou usar salas
  de AD do TryHackMe/HTB (sem instalar nada).
- Requisitos e ISOs em [`03-instalacao.md`](03-instalacao.md) §5.4.

## 10. Os cinco porquês: por que o AD é tão explorável?

**Por quê 1** — Por que redes AD quase sempre caem em pentest?
Porque acumulam configurações fracas: LLMNR ligado, senhas de serviço antigas, admin local
reutilizado, DA fazendo login em estação.

**Por quê 2** — Por que essas fraquezas persistem?
Porque o AD prioriza **compatibilidade e funcionamento** sobre segurança: NTLM e LLMNR seguem
ligados por padrão há décadas para não quebrar sistemas legados.

**Por quê 3** — Por que a Microsoft mantém padrões inseguros ligados?
Trade-off de compatibilidade: desligar NTLM/LLMNR por padrão quebraria incontáveis ambientes
corporativos que dependem deles. O custo de quebrar a base instalada supera, para a Microsoft,
o de deixar inseguro-por-padrão com opção de endurecer.

**Por quê 4** — Por que as empresas não endurecem manualmente?
Porque endurecer exige conhecimento, teste e risco de quebrar produção — e o benefício é
invisível até o incidente. Mesma lógica de dívida de segurança de [`17`](17-pos-exploracao-e-movimentacao.md) §10.

**Por quê 5** — Qual é a parada?
Um **trade-off de compatibilidade de longo prazo**: o AD carrega 25 anos de decisões voltadas a
não quebrar o legado, e cada default inseguro é uma dessas decisões. A Microsoft vem
apertando (desabilitando NTLM aos poucos, empurrando Entra ID e senhas gerenciadas), mas a base
instalada muda devagar. É por isso que pentest de AD continuará rendendo por muitos anos — e por
que suas melhores recomendações serão quase sempre "desligue o legado que ninguém desligou".

---

## Autoteste

1. Por que o Active Directory é "onde está o dinheiro corporativo" para um pentester?
2. Explique, em três passos, como o Kerberos autentica.
3. Diferencie AS-REP Roasting de Kerberoasting.
4. Por que o Kerberoasting é indetectável do lado do servidor, e qual defesa o mitiga?
5. O que é DCSync e por que ele é tão poderoso?
6. Como o BloodHound mudou a forma de fazer pentest de AD?
7. Descreva a cadeia típica "sem credencial → Domain Admin".
8. Por que a maioria das defesas de AD é grátis ou barata, e o que isso diz ao cliente?
9. Por que o AD é tão explorável? Leve o porquê até o fim.
