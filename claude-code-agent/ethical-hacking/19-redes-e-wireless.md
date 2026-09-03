# 19 · Redes e wireless — camada 2, MITM e Wi-Fi

`Nível: avançado` · `Última atualização: 12/08/2026`

Ataques de rede exploram a confiança embutida nos protocolos que fazem a internet funcionar.
Este arquivo cobre a rede local (camada 2), interceptação (MITM), e Wi-Fi.

> ⚖️ Ataques de rede afetam **todos** os dispositivos do segmento — inclusive os que não são
> alvo. Só em laboratório isolado ou com escopo que explicitamente os inclua. ARP spoofing na
> rede errada derruba a rede de terceiros. Ver [`12`](12-etica-lei-e-contrato.md).

---

## 1. Por que a rede local é insegura por design

Os protocolos base da LAN foram criados nos anos 1980, quando a rede era um ambiente confiável.
Eles **não autenticam**. Essa confiança ingênua é a raiz de quase todo ataque de camada 2.

## 2. ARP e o ataque de envenenamento (ARP spoofing)

**ARP** (Address Resolution Protocol) traduz IP → endereço MAC na rede local. O problema:
qualquer máquina pode dizer "eu sou o IP X" e **ninguém verifica**.

```
Vítima:   "quem tem 192.168.1.1 (o gateway)?"
Atacante: "sou eu!" (mentira — envia um ARP reply forjado)
→ a vítima passa a mandar todo tráfego destinado ao gateway PARA O ATACANTE
```

Resultado: **man-in-the-middle**. O atacante fica entre a vítima e o gateway, vê (e pode
alterar) todo o tráfego.
```bash
# Habilitar encaminhamento (para a vítima não perder conexão)
sysctl -w net.ipv4.ip_forward=1
# Envenenar (bettercap é o padrão atual; ettercap é o clássico)
bettercap -iface eth0 -eval "set arp.spoof.targets 192.168.1.50; arp.spoof on; net.sniff on"
```
**Defesa:** *Dynamic ARP Inspection* (DAI) no switch, port security, segmentação, e — a real
proteção — **criptografia fim a fim** (HTTPS/TLS), que torna o MITM incapaz de ler o conteúdo
mesmo interceptando.

## 3. Outros ataques de camada 2

| Ataque | Mecanismo | Defesa |
|---|---|---|
| **MAC flooding** | encher a tabela CAM do switch até ele virar hub e replicar tudo | port security |
| **DHCP spoofing** | responder DHCP mais rápido que o legítimo → dar gateway/DNS falso | DHCP snooping |
| **VLAN hopping** | escapar da VLAN via double-tagging ou DTP | desligar DTP, VLAN nativa dedicada |
| **STP attack** | virar root bridge → redirecionar tráfego | BPDU guard |
| **LLMNR/NBT-NS poisoning** | responder a consultas de nome do Windows → capturar hashes | desligar LLMNR/NBT-NS (ver [`20`](20-active-directory.md)) |

**LLMNR/NBT-NS poisoning** merece destaque: é o passo 2 do Exemplo 14 ([`06`](06-exemplos.md)).
O Windows, quando o DNS falha, pergunta "quem é `\\fileserver`?" via broadcast. O **Responder**
responde "sou eu" e captura o hash NetNTLMv2 de quem tenta autenticar. É um dos ataques mais
produtivos em pentest interno — e a defesa (desligar esses protocolos legados) é grátis.
```bash
responder -I eth0        # captura hashes; depois quebra com hashcat -m 5600
```

## 4. Interceptação e o que a criptografia mudou

Antigamente, MITM = ler tudo (HTTP, e-mail, senhas em texto). Hoje, **HTTPS/TLS** protege o
conteúdo: mesmo interceptando, o atacante vê tráfego cifrado. Isso mudou o jogo:
- **SSL stripping** (forçar downgrade para HTTP) foi mitigado por **HSTS** e HTTPS onipresente.
- O valor do MITM hoje está mais em: metadados, hosts sem TLS, certificados mal validados, e
  ataques a autenticação (capturar hashes de rede como acima).
- Ferramentas: **bettercap** (suíte moderna), **mitmproxy** (para HTTP/S com CA instalada, como
  o Burp), **Wireshark**/**tcpdump** (análise passiva).

```bash
tcpdump -i eth0 -w captura.pcap        # captura para análise
wireshark captura.pcap                 # analisa (filtros: http, dns, tcp.port==445)
```

## 5. Wi-Fi — fundamentos e ataques

### Modo monitor e captura
Wi-Fi exige um adaptador que suporte **modo monitor** (ver quadros de todos, não só os
seus) e **injeção** (chipsets comuns: Atheros, alguns Realtek/Ralink). Adaptador USB dedicado
costuma ser necessário — o interno do notebook raramente serve.
```bash
sudo airmon-ng start wlan0        # coloca em modo monitor (vira wlan0mon)
sudo airodump-ng wlan0mon         # lista redes e clientes ao redor
```

### WPA2-PSK — o ataque de handshake
WPA2 pessoal (com senha compartilhada) é atacado capturando o **handshake de 4 vias** (quando
um cliente conecta) e quebrando **offline**:
```bash
# 1. Focar na rede alvo e capturar
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w captura wlan0mon
# 2. Forçar um cliente a reconectar (deauth) para capturar o handshake
sudo aireplay-ng --deauth 5 -a AA:BB:CC:DD:EE:FF wlan0mon
# 3. Quebrar offline
hashcat -m 22000 captura.hc22000 /usr/share/wordlists/rockyou.txt
```
**Por que funciona:** o handshake contém material derivado da senha. Você não quebra na rede —
leva para casa e testa milhões de senhas offline. **A defesa é a senha:** longa e aleatória
torna a quebra inviável (o espaço de busca explode). Senha fraca cai em minutos.

### WPA3 e o estado atual (2026)
WPA3 substitui o handshake por **SAE** (*Simultaneous Authentication of Equals* / Dragonfly),
que resiste a ataque offline de dicionário — a grande melhoria. Mas: adoção ainda parcial,
modo de transição (WPA2/WPA3) reintroduz fraquezas, e houve falhas de implementação
("Dragonblood", 2019). Redes corporativas usam **WPA2/WPA3-Enterprise** (802.1X/RADIUS, sem
senha compartilhada) — atacada por *evil twin* e captura de credencial, não por handshake.

### Evil twin e captura de credencial
Criar um ponto de acesso falso com o mesmo nome (SSID) da rede legítima; clientes ou usuários
conectam e entregam credenciais. Ferramentas: `hostapd`, `eaphammer`, `wifiphisher`. Muito
eficaz contra redes Enterprise e contra usuários desatentos. **Defesa:** validação de
certificado do servidor no cliente (802.1X bem configurado), educação, WIPS.

## 6. Estratégia num pentest de rede interna

1. Conectar, obter IP (DHCP), mapear a sub-rede.
2. **Responder** para colher hashes (LLMNR/NBT-NS) — passivo e produtivo.
3. Enumerar SMB/AD (ver [`20`](20-active-directory.md)).
4. Considerar MITM/ARP só se necessário e no escopo — é intrusivo e barulhento.
5. Documentar cada técnica → MITRE ATT&CK; apontar as defesas grátis (desligar LLMNR,
   assinatura SMB, segmentação).

## 7. Os cinco porquês: por que ARP não autentica?

**Por quê 1** — Por que qualquer máquina pode mentir no ARP?
Porque o protocolo, por design, aceita respostas sem verificar a identidade de quem responde.

**Por quê 2** — Por que foi projetado sem autenticação?
Porque em ~1982, quando o ARP foi definido (RFC 826), a rede local era um ambiente físico
confiável — poucos computadores, todos de gente conhecida, num prédio. Autenticar era resolver
um problema que não existia. **Decisão histórica documentada.**

**Por quê 3** — Por que não corrigiram depois?
Porque ARP está embutido em bilhões de dispositivos e na base do IPv4. Trocá-lo quebraria a
compatibilidade de toda a internet local existente. O custo de mudar o protocolo supera o de
mitigar por fora.

**Por quê 4** — Por que não migrar para algo autenticado (como o IPv6 tentou com SEND)?
Porque a inércia de adoção é imensa e as mitigações por fora (DAI, port security, e sobretudo
TLS fim a fim) resolvem o risco prático "bom o suficiente" a custo menor.

**Por quê 5** — Qual é a parada?
Uma **decisão histórica congelada por compatibilidade**: o ARP nasceu num mundo confiável, e o
custo de trocá-lo globalmente sempre superou o de compensar com criptografia na camada de cima.
A verdadeira defesa contra MITM hoje não é consertar o ARP — é **assumir que a rede é hostil** e
cifrar tudo fim a fim. Este é o modelo *zero trust*: não confiar na rede é aceitar que o ARP
nunca vai ser confiável.

---

## Autoteste

1. Por que o ARP permite que uma máquina se passe por outra?
2. Descreva o ARP spoofing e por que ele resulta em MITM.
3. Por que HTTPS/TLS reduziu drasticamente o valor do MITM tradicional?
4. O que o Responder faz e por que é tão produtivo em pentest interno?
5. Explique por que WPA2-PSK é quebrado offline e por que a senha é a defesa real.
6. O que o WPA3 (SAE) melhora em relação ao WPA2, e qual a ressalva de adoção em 2026?
7. O que é um ataque evil twin e contra quem é eficaz?
8. Por que o ARP não autentica, e qual é a defesa moderna de verdade? Leve o porquê até o fim.
