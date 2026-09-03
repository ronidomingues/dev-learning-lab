# Glossário — Ethical Hacking

`Última atualização: 12/08/2026`

Todos os termos técnicos usados no curso, definidos. Termos em inglês são mantidos quando é
assim que o campo os usa, com a tradução na primeira menção. Ordenado alfabeticamente.

---

## A

- **AAA** — Authentication, Authorization, Accounting: identificar quem é, o que pode, e
  registrar o que fez.
- **ACL (Access Control List)** — lista que define quem pode acessar um recurso.
- **Active Directory (AD)** — serviço de diretório da Microsoft que gerencia identidade e
  acesso em redes Windows. Ver [`20`](20-active-directory.md).
- **AppSec** — Application Security; segurança de aplicações.
- **ARP (Address Resolution Protocol)** — traduz IP em endereço MAC na rede local; não
  autentica, base do ARP spoofing. Ver [`19`](19-redes-e-wireless.md).
- **AS-REP Roasting** — ataque que pede material cifrado com o hash de contas AD sem
  pré-autenticação, para quebra offline.
- **ASLR (Address Space Layout Randomization)** — randomiza endereços de memória para dificultar
  exploração. Ver [`16`](16-vulnerabilidades-e-exploracao.md).
- **ASN (Autonomous System Number)** — identifica os blocos de IP de uma organização na internet.
- **Autenticação (authN)** — provar identidade ("quem é você?").
- **Autorização (authZ)** — decidir permissões ("o que você pode?").

## B

- **Backdoor** — acesso oculto deixado num sistema para retorno futuro.
- **Banner grabbing** — ler a "apresentação" de um serviço para descobrir versão.
- **Bind shell** — shell em que você conecta a uma porta aberta no alvo (oposto de reverse).
- **Black box** — teste sem informação prévia do alvo. Ver [`10`](10-fundamentos.md).
- **Black hat** — atacante sem autorização, criminoso.
- **BloodHound** — ferramenta que mapeia caminhos de ataque em AD como grafo.
- **Blue team** — equipe de defesa (monitora, detecta, responde).
- **Buffer overflow** — escrever além do limite de um buffer, corrompendo memória adjacente.
  Ver [`16`](16-vulnerabilidades-e-exploracao.md).
- **Bug bounty** — programa que paga por vulnerabilidades encontradas, dentro de regras públicas.
- **Burp Suite** — proxy de interceptação, a principal ferramenta de teste web.

## C

- **C2 (Command and Control)** — infraestrutura pela qual um atacante controla máquinas
  comprometidas.
- **CIA** — Confidencialidade, Integridade, Disponibilidade: a tríade da segurança.
- **CFI (Control-Flow Integrity)** — mitigação que verifica se saltos vão a alvos legítimos.
- **Cobalt Strike** — framework comercial de C2 usado em red team (e abusado por criminosos).
- **CTF (Capture The Flag)** — competição/desafio de segurança onde se busca "flags".
- **CVE (Common Vulnerabilities and Exposures)** — identificador único de uma vulnerabilidade.
- **CVSS (Common Vulnerability Scoring System)** — nota de severidade de 0 a 10.
- **CWE (Common Weakness Enumeration)** — catálogo de classes de fraqueza.

## D

- **DAST** — Dynamic Application Security Testing; análise executando a aplicação.
- **DCSync** — ataque que faz o Domain Controller replicar hashes de credenciais ao atacante.
- **Defesa em profundidade** — múltiplas camadas de segurança independentes.
- **DoS/DDoS** — negação de serviço; sobrecarregar para derrubar. **Fora de escopo** na maioria
  dos pentests.
- **Domain Admin (DA)** — grupo que controla um domínio AD; o "xeque-mate".
- **DNS (Domain Name System)** — traduz nomes em endereços IP.

## E

- **EDR (Endpoint Detection and Response)** — software de defesa que detecta atividade maliciosa
  em máquinas.
- **Enumeração** — extrair informação detalhada de um serviço/sistema. Ver [`15`](15-varredura-e-enumeracao.md).
- **EPSS** — probabilidade de uma CVE ser explorada nos próximos 30 dias.
- **Escalada de privilégio** — passar de acesso limitado a admin/root. Ver [`17`](17-pos-exploracao-e-movimentacao.md).
- **Evil twin** — ponto de acesso Wi-Fi falso que imita um legítimo.
- **Exploit** — código/técnica que transforma uma vulnerabilidade em ação.
- **Exfiltração** — extrair dados de um sistema comprometido.

## F

- **FIDO2/Passkey** — autenticação forte, resistente a phishing (chave física/biométrica).
- **Firewall** — controla quais conexões passam por IP/porta.
- **Fuzzing** — enviar entradas geradas para provocar falhas. Ver [`60`](60-teoria-avancada.md).

## G

- **Golden ticket** — TGT forjado com o hash da conta krbtgt; persistência quase indelével em AD.
- **Grey box** — teste com informação parcial do alvo.
- **Grey hat** — quem age sem autorização alegando boa intenção (juridicamente, crime).
- **GTFOBins** — base que documenta como abusar de binários Unix para escalar privilégio.

## H

- **Handshake (TCP)** — troca SYN → SYN/ACK → ACK que abre uma conexão TCP.
- **Hash** — função de mão única; guarda-se o hash da senha, não a senha.
- **Hashcat** — quebrador de hashes acelerado por GPU.
- **HSTS** — cabeçalho que força HTTPS, mitigando SSL stripping.
- **HTTP/HTTPS** — protocolo da web; HTTPS é HTTP sobre TLS (cifrado).

## I

- **IAM (Identity and Access Management)** — gestão de identidade e acesso; o perímetro da nuvem.
- **IDOR (Insecure Direct Object Reference)** — acessar objeto de outro trocando um
  identificador. Ver [`18`](18-seguranca-web.md).
- **IDS/IPS** — sistemas de detecção/prevenção de intrusão.
- **Impacket** — coleção de ferramentas Python para protocolos de rede/AD.
- **Injeção** — entrada do usuário vira parte de uma linguagem interpretada (SQL, comando, etc.).
- **IoT (Internet of Things)** — dispositivos conectados; notoriamente inseguros. Ver [`22`](22-mobile-e-hardware.md).

## K

- **Kali Linux** — distribuição com ferramentas ofensivas pré-instaladas.
- **KEV (Known Exploited Vulnerabilities)** — catálogo da CISA de CVEs sendo exploradas.
- **Kerberos** — protocolo de autenticação por tickets, usado no AD.
- **Kerberoasting** — pedir tickets de contas de serviço AD para quebra offline. Ver [`20`](20-active-directory.md).
- **Kill chain** — modelo das etapas de um ataque direcionado.

## L

- **LAPS** — solução da Microsoft para senhas de admin local únicas por máquina.
- **Lateral movement (movimentação lateral)** — alcançar outros hosts a partir de um comprometido.
- **LFI/RFI** — Local/Remote File Inclusion; incluir arquivos no servidor.
- **LGPD** — Lei Geral de Proteção de Dados (Brasil, Lei 13.709/2018).
- **LLMNR/NBT-NS** — protocolos de resolução de nome do Windows, abusados por poisoning.
- **LOLBAS** — binários nativos do Windows úteis a atacantes.

## M

- **MAC address** — endereço físico de uma interface de rede (camada 2).
- **Meterpreter** — payload/shell avançado do Metasploit.
- **Metasploit** — framework de exploração.
- **MFA (autenticação multifator)** — exigir dois ou mais fatores de autenticação.
- **MITM (Man-in-the-Middle)** — atacante posicionado entre duas partes que se comunicam.
- **MITRE ATT&CK** — taxonomia de táticas e técnicas de adversário.
- **msfvenom** — gerador de payloads do Metasploit.

## N

- **NAT (Network Address Translation)** — traduz endereços entre redes (ex.: privada↔pública).
- **netexec (nxc)** — ferramenta de enumeração/ataque a SMB/AD; sucessor do CrackMapExec.
- **n-day** — vulnerabilidade conhecida e corrigida, presente em sistemas não atualizados.
- **nmap** — o scanner de portas e serviços padrão do campo.
- **NX/DEP** — marca a memória como não-executável para impedir shellcode. Ver [`16`](16-vulnerabilidades-e-exploracao.md).
- **NTLM** — protocolo de autenticação legado do Windows; o hash é a credencial.

## O

- **OSINT (Open Source Intelligence)** — coleta de informação de fontes abertas. Ver [`14`](14-reconhecimento-e-osint.md).
- **OWASP** — Open Worldwide Application Security Project; produz o Top 10, WSTG, ASVS.
- **0-day (zero-day)** — vulnerabilidade desconhecida do fabricante, sem patch.

## P

- **Pass-the-hash** — autenticar com o hash NTLM sem conhecer a senha. Ver [`06`](06-exemplos.md).
- **Path traversal** — usar `../` para acessar arquivos fora da pasta permitida.
- **Payload** — o código que roda após a exploração (ex.: reverse shell).
- **Pentest (penetration test)** — teste de invasão autorizado.
- **Persistência** — manter acesso após reinício/reautenticação.
- **Phishing** — induzir vítima a clicar/entregar credencial por mensagem falsa.
- **Pivoting** — usar um host comprometido como trampolim para redes internas.
- **Porta (port)** — número que identifica um serviço num host (ex.: 443 = HTTPS).
- **Pós-exploração** — ações após o acesso inicial (escalar, coletar, movimentar).
- **Prepared statement** — query parametrizada; defesa definitiva contra SQLi.
- **Proxy** — intermediário de tráfego (ex.: Burp entre navegador e servidor).
- **PTES** — Penetration Testing Execution Standard.
- **Purple team** — red e blue trabalhando juntos para melhorar detecção.

## R

- **RAT (Remote Access Trojan)** — malware de acesso remoto.
- **RCE (Remote Code Execution)** — executar código arbitrário remotamente; das falhas mais graves.
- **Recon (reconhecimento)** — fase de coleta de informação sobre o alvo.
- **Red team** — equipe que simula adversário real, testando também a detecção.
- **Reverse shell** — shell em que o alvo conecta de volta ao atacante (fura firewall de entrada).
- **RoE (Rules of Engagement)** — regras de engajamento de um teste (escopo, janela, limites).
- **ROP (Return-Oriented Programming)** — reusar trechos de código existente para contornar NX.
- **Rootkit** — malware que se esconde no nível do sistema.

## S

- **SAST** — Static Application Security Testing; análise do código sem executar.
- **SBOM (Software Bill of Materials)** — inventário de componentes de um software.
- **SIEM** — sistema que agrega e correlaciona logs para detecção.
- **SOC (Security Operations Center)** — centro de operações de segurança (defesa).
- **Shell** — acesso à linha de comando de um sistema.
- **Shellcode** — código de máquina, tipicamente para abrir um shell.
- **SQLi (SQL Injection)** — injeção em consultas SQL. Ver [`18`](18-seguranca-web.md).
- **SSRF (Server-Side Request Forgery)** — forçar o servidor a fazer requisições escolhidas pelo
  atacante; perigoso na nuvem (metadata). Ver [`21`](21-nuvem-e-containers.md).
- **Stack canary** — valor secreto que detecta overflow de pilha.
- **SUID** — bit que faz um binário rodar com a identidade do dono (fonte de escalada).
- **Superfície de ataque** — soma dos pontos por onde se poderia atacar.

## T

- **TCP/UDP** — protocolos de transporte; TCP é confiável (com handshake), UDP não.
- **TGT/TGS** — tickets do Kerberos (concessor de tickets / de serviço).
- **TLS (Transport Layer Security)** — protocolo de criptografia que protege HTTPS e outros.
- **TTP** — Tactics, Techniques and Procedures (comportamento do adversário).

## V

- **Vetor de ataque** — o caminho específico usado num ataque concreto.
- **Vishing** — phishing por voz (telefone).
- **VulnHub** — repositório de VMs vulneráveis para prática.
- **Vulnerabilidade** — fraqueza que pode ser explorada.

## W

- **WAF (Web Application Firewall)** — filtro que inspeciona tráfego web; contornável.
- **White box** — teste com informação completa (código, credenciais).
- **White hat** — profissional que age com autorização documentada.
- **Wordlist** — lista de palavras (senhas, nomes) para força bruta/fuzzing.
- **WPA2/WPA3** — protocolos de segurança Wi-Fi. Ver [`19`](19-redes-e-wireless.md).
- **Write-up** — relato escrito da resolução de um desafio/máquina.

## X

- **XSS (Cross-Site Scripting)** — injeção de script no navegador de outro usuário. Ver [`18`](18-seguranca-web.md).

## Z

- **Zero trust** — modelo que não confia na rede; verifica sempre, cifra tudo fim a fim.
- **ZAP (OWASP ZAP)** — proxy de interceptação open source, alternativa ao Burp.
