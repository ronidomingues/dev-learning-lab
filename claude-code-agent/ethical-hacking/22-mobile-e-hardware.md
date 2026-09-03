# 22 · Mobile, IoT e hardware

`Nível: avançado` · `Última atualização: 12/08/2026`

Especialidades que estendem o hacking para além do servidor: aplicativos móveis, dispositivos
IoT, firmware e hardware. Este arquivo é um panorama de entrada — cada um destes é uma carreira
inteira. O objetivo é você saber que existem, o que os define, e por onde começar.

---

## 1. Segurança mobile (Android e iOS)

### O que muda em relação à web
Um app móvel é um **cliente que você controla fisicamente**. Isso inverte suposições: o código
do app está no seu dispositivo, você pode descompilá-lo, interceptar seu tráfego, e ver o que
os desenvolvedores acharam que estava "escondido". A regra "não confie no cliente"
([`10`](10-fundamentos.md)) vale em dobro.

### As classes de falha (OWASP Mobile Top 10 / MASVS)
| Classe | Exemplo |
|---|---|
| Armazenamento inseguro | senha/token em texto no dispositivo, logs, backups |
| Comunicação insegura | sem TLS, sem *certificate pinning*, ou pinning contornável |
| Autenticação/autorização fracas | lógica de auth no cliente, API sem checagem |
| Criptografia ruim | chave hardcoded no APK, algoritmo fraco |
| Engenharia reversa | segredos no código, falta de ofuscação |
| Code tampering | app não detecta ter sido modificado |

### Ferramental
- **MobSF (Mobile Security Framework):** análise estática e dinâmica automatizada — melhor
  ponto de partida.
- **Frida** e **objection:** *instrumentação dinâmica* — alterar o app em execução (burlar
  pinning, root detection, ler variáveis). Ferramenta central do mobile.
- **apktool / jadx:** descompilar APK Android para ler o código.
- **Burp com proxy no dispositivo:** interceptar a API do app (onde mora a maioria das falhas
  reais — o backend, não o app).

> **Opinião profissional:** a maioria das falhas "de app" está de fato na **API** que o app
> consome. Um pentest mobile competente gasta mais tempo na API (é web/[`18`](18-seguranca-web.md))
> do que no app em si. O app é o mapa para achar a API e como ela é chamada.

**Laboratório:** [OWASP MASTG](https://mas.owasp.org) tem apps propositalmente vulneráveis
(*crackmes*), DIVA, InsecureBankv2, iGoat.

## 2. IoT (Internet das Coisas)

Dispositivos IoT — câmeras, roteadores, fechaduras, sensores — combinam o pior de vários
mundos: software velho, sem atualização, com senha padrão, e agora conectados à internet. A
botnet **Mirai (2016)** derrubou parte da internet usando câmeras com senha `admin/admin`.

### Superfícies
- **Rede:** serviços expostos (telnet!, UPnP, protocolos proprietários), senhas padrão.
- **Firmware:** o software do dispositivo — extraível, analisável, cheio de segredos.
- **Aplicativo/nuvem:** o app que controla e a API na nuvem.
- **Rádio:** Wi-Fi, Bluetooth/BLE, Zigbee, Z-Wave, LoRa, sub-GHz.
- **Físico:** portas de debug (UART, JTAG), memória flash.

### Firmware
```bash
binwalk -e firmware.bin        # extrai o sistema de arquivos do firmware
# procurar: senhas, chaves, binários, versões vulneráveis
grep -r "password" _firmware.extracted/
firmware-mod-kit, firmwalker    # ferramentas de análise
```
Você monta o sistema de arquivos extraído e o trata como um Linux comum: procura segredos,
binários vulneráveis, contas de backdoor.

## 3. Rádio (RF) e SDR

**SDR (Software-Defined Radio)** — um rádio controlado por software (ex.: HackRF, RTL-SDR)
permite receber e transmitir em amplo espectro. Usos ofensivos: capturar e repetir sinais de
controle remoto (carros, portões — *replay attack*), analisar protocolos sem fio proprietários,
BLE. É uma especialidade fascinante e de nicho. Ferramentas: GNU Radio, Universal Radio Hacker.

## 4. Hardware e canais laterais

O nível mais baixo:
- **Interfaces de debug:** UART, JTAG, SWD dão acesso direto ao processador — console, dump de
  memória, muitas vezes root sem senha. Ferramenta: analisador lógico, Bus Pirate, JTAGulator.
- **Dump de memória flash:** ler o chip diretamente (SPI flash com clip, `flashrom`).
- **Ataques de canal lateral (side-channel):** extrair segredos observando **consumo de
  energia**, **tempo**, ou **emissão eletromagnética** durante operações criptográficas.
  *Timing attacks*, DPA (análise diferencial de potência). Base teórica em [`60`](60-teoria-avancada.md).
- **Fault injection (glitching):** provocar erro (variar tensão/clock) para pular uma
  verificação (ex.: pular a checagem de senha do bootloader). ChipWhisperer é a plataforma de
  estudo.

## 5. Onde isto se encaixa na carreira

Estas são **especializações**, geralmente escolhidas depois de uma base em rede/web/AD. O
mercado é menor e mais concentrado (fabricantes de dispositivo, pesquisa, red teams avançados),
mas a concorrência é menor e o valor por profissional é alto. Não comece por aqui; chegue aqui.

**Ordem sugerida de entrada:** mobile é o mais próximo do que você já sabe (é web + cliente
controlado), sendo a transição natural. IoT/firmware exige Linux embarcado. Rádio e hardware
exigem equipamento e eletrônica.

## 6. Os cinco porquês: por que IoT é tão inseguro?

**Por quê 1** — Por que dispositivos IoT são notoriamente inseguros?
Porque rodam software velho, sem atualização, muitas vezes com credencial padrão e serviços
expostos.

**Por quê 2** — Por que não atualizam e usam senha padrão?
Porque o fabricante otimiza para **custo unitário e time-to-market**, não para segurança. Um
mecanismo de atualização seguro e senhas únicas por dispositivo custam engenharia que não
aparece no preço de prateleira.

**Por quê 3** — Por que o mercado não pune isso?
Porque o comprador escolhe por preço e função, não por segurança (que é invisível na compra), e
o custo do dispositivo inseguro cai sobre **terceiros** (a vítima do DDoS da botnet), não sobre
o comprador nem o fabricante. Externalidade clássica.

**Por quê 4** — Por que a externalidade persiste?
Está começando a ser corrigida por lei: o **Cyber Resilience Act** europeu (em vigor por etapas
até dez/2027) e leis de IoT (Califórnia, Reino Unido) proíbem senha padrão e exigem
atualização. É o mesmo motor regulatório de [`01`](01-introducao-leigo.md) §6.

**Por quê 5** — Qual é a parada?
Um **trade-off econômico com externalidade**, em correção regulatória lenta: enquanto segurança
for custo invisível na compra e o dano recair sobre terceiros, o fabricante racional corta
segurança. Só a regulação (internalizando o custo) muda a conta. Até lá — e por muitos anos de
legado já vendido — o IoT continuará sendo o alvo mais fácil da internet.

---

## Autoteste

1. Por que "não confie no cliente" vale em dobro para apps móveis?
2. Onde está, na prática, a maioria das falhas de um app móvel — no app ou na API? Por quê?
3. Para que serve o Frida/objection num pentest mobile?
4. O que o `binwalk` faz e por que ele é o começo da análise de firmware?
5. O que é um ataque de canal lateral? Dê um exemplo.
6. Por que essas áreas são "especializações para chegar", não "portas de entrada"?
7. Por que o IoT é tão inseguro, e o que está mudando isso? Leve o porquê até o fim.
