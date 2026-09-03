# 22 · Firmware e sistemas embarcados

**Nível:** avançado · **Data:** 03/09/2026

Roteadores, câmeras IP, fechaduras "inteligentes", carros, PLCs industriais, o seu roteador
Wi-Fi: todos rodam **firmware** — software embarcado, muitas vezes sem fonte, cheio de falhas, e
raramente atualizado. É uma das fronteiras mais quentes (e menos protegidas) do RE. As
diferenças em relação a reverter um `.exe` de desktop são grandes o suficiente para merecer
capítulo próprio.

---

## 1. O que muda em relação a desktop

| Aspecto | Desktop | Embarcado/firmware |
|---|---|---|
| **Arquitetura** | x86-64 majoritário | **ARM, MIPS, RISC-V, PowerPC, Xtensa** — diversidade enorme |
| **SO** | Windows/Linux/macOS | Linux embarcado, RTOS, ou **bare-metal** (sem SO) |
| **Obtenção do binário** | baixar o `.exe` | **extrair** do dispositivo/imagem — o passo difícil |
| **Símbolos/proteções** | variados | quase sempre stripped, sem ASLR/NX, cheio de bugs |
| **Depuração** | trivial | via **JTAG/SWD/UART**, hardware físico |

O trabalho começa **antes** do Ghidra: você precisa *obter* e *entender o layout* do firmware.

---

## 2. Obter o firmware — as vias

1. **Download do fabricante:** a mais fácil. Sites de suporte publicam imagens de atualização.
2. **Interceptar a atualização:** capturar o binário que o dispositivo baixa (OTA).
3. **Dump por software:** se houver shell (UART/telnet/SSH), copiar a partição de flash
   (`/dev/mtd*`) via `dd`/`nanddump`.
4. **Dump por hardware:** ler o chip de flash diretamente:
   - **UART** (console serial): frequentemente dá shell ou bootloader (U-Boot).
   - **JTAG/SWD:** depuração de hardware; ler/escrever memória e flash.
   - **Chip-off / SPI/I2C:** conectar um programador (ex.: um CH341A + `flashrom`) direto no
     chip de memória e ler seus bytes.

O dump de hardware é onde RE encontra eletrônica: identificar pinos, `baud rate`, o chip
(datasheet), e soldar. Ferramentas: analisador lógico, multímetro, `flashrom`, `sigrok`.

---

## 3. Desmontar a imagem — binwalk e amigos

Uma imagem de firmware é um "sanduíche": bootloader + kernel + **sistema de arquivos** +
dados. **binwalk** identifica e extrai as camadas por assinaturas mágicas:

```bash
binwalk firmware.bin              # lista o que há dentro (kernel, squashfs, jffs2, ...)
binwalk -e firmware.bin           # extrai (cuidado com --run-as; extração é código de terceiros)
binwalk -E firmware.bin           # gráfico de entropia (regiões cifradas/comprimidas)
```
Sistemas de arquivos comuns: **SquashFS** (só-leitura, o mais comum), **JFFS2**, **UBIFS**,
**CramFS**. Extraído, você tem uma árvore Linux: `/bin`, `/etc`, `/www` (interface web),
binários da aplicação — e é aí que os bugs moram (o servidor web em C, o serviço de CGI).

**Firmware cifrado:** entropia alta e uniforme = imagem cifrada; você precisa achar a chave
(muitas vezes no bootloader, num estágio anterior não cifrado) ou dumpar a RAM já descriptada.

---

## 4. Reverter binários de outra arquitetura

Os executáveis extraídos são ARM/MIPS. Você:
- Abre no **Ghidra/IDA** (ambos suportam dezenas de arquiteturas).
- **Emula** para rodá-los no seu PC:
  ```bash
  qemu-mips ./binario_mips            # user-mode: roda um binário isolado
  # ou emular o sistema inteiro:
  qemu-system-arm ...                 # com FIRMADYNE/FirmAE para "bootar" o firmware
  ```
- **FirmAE/FIRMADYNE** automatizam emular firmware de roteador inteiro (com a interface web) no
  PC — permitindo fuzzing e testes dinâmicos sem o hardware.

Alvos frequentes de bug: o **servidor web embutido** (parâmetros de CGI sem validação →
command injection/overflow), serviços de rede proprietários, e **credenciais/chaves hardcoded**
(`strings` no firmware acha senhas de fábrica e certificados com assustadora frequência).

---

## 5. Depuração de hardware (JTAG/UART) — o essencial

- **UART:** 3 fios (TX, RX, GND) + terra; identifique o `baud` (115200 é comum). Um adaptador
  USB-serial + `screen`/`picocom` te dá o console de boot — às vezes um shell root direto, às
  vezes o U-Boot (onde você pode alterar o `bootargs` para ganhar shell).
- **JTAG/SWD:** depuração real do processador. Ferramentas: **OpenOCD** + um probe (FTDI,
  J-Link, Black Magic Probe). Permite parar a CPU, ler registradores, dumpar RAM/flash,
  colocar breakpoints em hardware — o "GDB do metal".

---

## 6. Por que firmware é tão vulnerável (e tão importante)

- **Ciclo de atualização quebrado:** muitos dispositivos nunca recebem patch; um bug vale por
  anos. Botnets como **Mirai** exploraram exatamente isso (credenciais padrão em câmeras/DVRs).
- **Sem mitigations:** frequentemente sem ASLR, NX, canário — exploração é "fácil" comparada a
  desktop moderno.
- **Escala e criticidade:** de roteadores domésticos a infraestrutura industrial (ICS/SCADA) e
  automotivo. O impacto de um bug pode ser físico.
- **Superfície opaca:** sem fonte, sem documentação — só o RE revela o que o dispositivo
  realmente faz (inclusive *backdoors* e telemetria não divulgada).

---

## 7. Ética e segurança física

- Analise **seus próprios** dispositivos, ou sob autorização. Pesquisa de segurança de IoT tem
  crescido em proteção legal, mas mexer com dispositivos de terceiros/infra crítica sem
  autorização é crime e pode ser perigoso.
- **Divulgação coordenada** com o fabricante e, quando aplicável, com CERTs — dispositivos
  críticos (médicos, industriais, automotivos) exigem cuidado redobrado: um PoC público pode ter
  consequências físicas.
- Cuidado físico: soldar, fontes de tensão, e o risco de *brick* (inutilizar) o dispositivo.
  Trabalhe com backups do firmware original.

---

## Autoteste

1. Liste três formas de **obter** o firmware de um dispositivo, da mais fácil à mais invasiva.
2. O que o `binwalk` faz, e quais sistemas de arquivos você espera encontrar dentro de uma imagem?
3. Como você reverte e **roda** um binário MIPS sem ter o hardware alvo?
4. O que uma entropia alta e uniforme numa imagem de firmware sugere, e o que fazer a respeito?
5. Diferencie o que **UART** e **JTAG** te dão no acesso a um dispositivo.
6. Por que sistemas embarcados são, em geral, mais fáceis de explorar que desktops modernos?
7. Que cuidados éticos e físicos extras a análise de firmware exige?
