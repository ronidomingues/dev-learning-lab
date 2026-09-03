# 03 · Manual de instalação do ambiente de estudo

`Nível: iniciante` · `Pesquisado na web em 31/08/2026` · `Testado em Ubuntu 22.04.5 LTS · x86_64`

> **Nota de reinterpretação.** Inglês não é uma ferramenta de software, então este arquivo foi
> reinterpretado conforme o [CLAUDE.md](../CLAUDE.md): ele é o **manual de montagem do ambiente
> de estudo**. Mas atenção — não é um arquivo simbólico: o ambiente moderno de aprendizado de
> idiomas **é** um conjunto de software real, com instalação real, PATH real e erros reais.
> Tudo abaixo é comando executável.
>
> **Você não precisa de nada disso para começar hoje.** Leia o §03.0 primeiro.

---

## 03.0 Alternativa sem instalar nada — comece em 5 minutos

Se você instalar dez programas antes de aprender a primeira palavra, você vai desistir na
instalação. Este é o caminho mínimo, tudo no navegador, zero instalação:

| Necessidade | Ferramenta no navegador | Link | Custo |
|---|---|---|---|
| Descobrir seu nível | EF SET | https://www.efset.org/ | grátis |
| Lições estruturadas | British Council LearnEnglish | https://learnenglish.britishcouncil.org/ | grátis |
| Escuta graduada | BBC Learning English | https://www.bbc.co.uk/learningenglish | grátis |
| Escuta lenta com transcrição | VOA Learning English | https://learningenglish.voanews.com/ | grátis |
| Dicionário com áudio | Cambridge Dictionary | https://dictionary.cambridge.org/ | grátis |
| Cartões de memória | AnkiWeb (versão web do Anki) | https://ankiweb.net/ | grátis, só conta |
| Correção de escrita | LanguageTool (site) | https://languagetool.org/ | grátis com limite |

**Faça isto agora, antes de continuar lendo:** crie a conta no AnkiWeb (§03.3) e faça o EF SET.
São 55 minutos e você já tem nível medido e um lugar para guardar palavras. O resto deste
arquivo é otimização — importante, mas depois.

---

## 03.1 O conjunto completo, e o que cada peça resolve

```
                       ┌──────────────────────────────┐
   INSUMO              │  yt-dlp · mpv · asbplayer    │  vídeo/áudio real, com legenda
   (o que entra)       │  AntennaPod / podcasts       │
                       │  Language Reactor (browser)  │  legenda dupla, clique→dicionário
                       └───────────────┬──────────────┘
                                       │ palavras e frases colhidas
                                       ▼
   MEMÓRIA             ┌──────────────────────────────┐
   (o que fica)        │  Anki + AnkiConnect + FSRS   │  repetição espaçada
                       │  AnkiDroid / AnkiMobile      │  revisão no celular
                       │  AnkiWeb                     │  sincronização
                       └───────────────┬──────────────┘
                                       │
                                       ▼
   CONSULTA            ┌──────────────────────────────┐
                       │  Cambridge / Merriam-Webster │  dicionário online
                       │  GoldenDict-ng + Wiktionary  │  dicionário offline
                       │  Kiwix                       │  Wikipédia offline
                       └───────────────┬──────────────┘
                                       │
                                       ▼
   PRODUÇÃO            ┌──────────────────────────────┐
   (o que sai)         │  Audacity / gravador do cel. │  gravar-se e ouvir
                       │  LanguageTool                │  revisar o que você escreve
                       │  espeak-ng / TTS do sistema   │  ouvir o que você escreve
                       └──────────────────────────────┘
```

| Peça | Obrigatória? | Licença | Custo |
|---|---|---|---|
| **Anki** (desktop) | ✅ sim | AGPL-3.0 (código aberto) | grátis |
| **AnkiDroid** (Android) | recomendada | GPL-3.0 | grátis |
| **AnkiMobile** (iOS) | opcional | proprietária | pago — ver [80](80-custos-e-licencas.md) |
| **AnkiWeb** | recomendada | serviço | grátis |
| **LanguageTool** (extensão) | recomendada | LGPL-2.1 (motor) | grátis com limite |
| **Language Reactor** (extensão) | opcional | proprietária | grátis com limite |
| **mpv + ffmpeg + yt-dlp** | opcional | GPL/LGPL | grátis |
| **GoldenDict-ng** | opcional | GPL-3.0 | grátis |
| **Python 3.10+** | só para o [07-projeto-modelo](07-projeto-modelo/) | PSF | grátis |

Ordem recomendada de instalação: **Anki → conta AnkiWeb → app do celular → extensão do navegador
→ o resto, se e quando doer a falta.**

---

## 03.2 Anki (computador)

O Anki é o único software realmente indispensável deste curso. Ele implementa **repetição
espaçada**: mostra cada cartão pouco antes de você esquecer. Ver o porquê em
[20-vocabulario](20-vocabulario.md) §20.6.

**Versão testada: Anki 26.08.1, consultada em https://apps.ankiweb.net em 31/08/2026.**
Versão mínima recomendada: **25.02** (a partir daí o agendador FSRS está maduro e é o padrão
para novos usuários). Evite versões anteriores a 23.10 — não têm FSRS.

### 03.2.1 Linux — família Debian/Ubuntu (Ubuntu, Debian, Mint, Pop!_OS)

**Método recomendado: tarball oficial.** O pacote `anki` dos repositórios da distro costuma
estar *anos* atrasado — o do Ubuntu 22.04 é da série 2.1.x. Não use.

**Passo 1 — instalar as bibliotecas de que a interface depende.**

```bash
sudo apt update && sudo apt install -y zstd libxcb-xinerama0 libxcb-cursor0 libnss3 libxcb-icccm4 libxcb-keysyms1
```
*O que faz:* instala o descompactador `zstd` e as bibliotecas gráficas Qt exigidas pelo Anki.

Verificação:
```bash
zstd --version
# esperado: *** Zstandard CLI ... v1.4.8 (ou superior)
```
*Se der `command not found`:* o `apt install` falhou. Reveja a saída do passo 1 — quase sempre
é falta de rede ou proxy (§03.14).

**Passo 2 — baixar o pacote.**

Abra https://apps.ankiweb.net e baixe o arquivo `anki-<versão>-linux-qt6.tar.zst`
(ou `anki-<versão>-linux-x86_64.tar.zst`, conforme a nomenclatura da versão).
Pela linha de comando, com a URL copiada do site:

```bash
cd ~/Downloads && curl -LO "<cole-aqui-a-URL-do-tar.zst>"
```
*O que faz:* baixa o pacote para `~/Downloads`.

**Passo 3 — extrair e instalar.**

```bash
cd ~/Downloads && tar xaf anki-*-linux-*.tar.zst && cd anki-*-linux-* && sudo ./install.sh
```
*O que faz:* descompacta e copia os arquivos para `/usr/local`, criando o atalho no menu.

Verificação:
```bash
anki --version
# esperado: 26.08.1
```
*Se der `command not found: anki`:* `/usr/local/bin` não está no PATH. Ver §03.12.

**Método alternativo — Flatpak** (bom se você não quer mexer em `/usr/local`, ou se a distro é
imutável tipo Fedora Silverblue):

```bash
sudo apt install -y flatpak && flatpak install -y flathub net.ankiweb.Anki
```
```bash
flatpak run net.ankiweb.Anki --version
```
*Trade-off:* o Flatpak roda em sandbox. Add-ons que chamam programas externos (TTS do sistema,
`ffmpeg`) podem não enxergar o resto da máquina, e o AnkiConnect exige liberar rede local.
**Recomendação:** use o tarball; caia no Flatpak só se o tarball não subir.

### 03.2.2 Linux — família Fedora/RHEL (Fedora, RHEL, Rocky, Alma)

A documentação oficial do Anki não traz instruções para Fedora. Os nomes de pacote mudam:

```bash
sudo dnf install -y zstd libxcb xcb-util-cursor nss libxkbcommon-x11
```
*O que faz:* equivalentes Fedora das bibliotecas do passo 1 do Debian.

Depois, os mesmos passos 2 e 3 acima (tarball + `sudo ./install.sh`).

Se a interface não abrir, o Flatpak é a saída prática no Fedora:
```bash
sudo dnf install -y flatpak && flatpak install -y flathub net.ankiweb.Anki
```

**Wayland:** em Fedora recente o padrão é Wayland e o Anki às vezes abre com fonte minúscula ou
tela preta. Contorno:
```bash
env QT_QPA_PLATFORM=xcb anki
```
Se resolver, torne permanente adicionando `export QT_QPA_PLATFORM=xcb` ao `~/.bashrc` (§03.12).

### 03.2.3 macOS

**Requisito:** macOS 13 (Ventura) ou superior, conforme a página oficial consultada em 31/08/2026.

**Método recomendado: instalador oficial.**

1. Baixe o `.dmg` em https://apps.ankiweb.net.
   - **Apple Silicon (M1/M2/M3/M4)**: escolha o pacote *Apple Silicon*.
   - **Intel**: escolha o pacote *Intel*.
   - Em dúvida:
     ```bash
     uname -m
     # esperado: arm64 (Apple Silicon) ou x86_64 (Intel)
     ```
2. Abra o `.dmg` e arraste **Anki** para *Applications*.
3. Na primeira abertura: **clique com o botão direito → Abrir** (não duplo clique), e confirme.
   *Por quê:* o Gatekeeper bloqueia a primeira execução de apps fora da App Store; o menu de
   contexto oferece a exceção que o duplo clique não oferece.

Verificação:
```bash
/Applications/Anki.app/Contents/MacOS/anki --version
# esperado: 26.08.1
```

**Método alternativo — Homebrew:**
```bash
brew install --cask anki
```
*O que faz:* baixa e instala o mesmo `.dmg`, sem cliques.
Verificação: `brew list --cask anki`.
*Trade-off:* o Homebrew às vezes demora alguns dias para publicar a versão nova.

> **Apple Silicon:** rodar o pacote Intel sob Rosetta 2 funciona, mas fica visivelmente mais
> lento em coleções grandes e algumas bibliotecas de áudio quebram. Use o pacote nativo.

### 03.2.4 Windows

**Requisito:** Windows 10 (x64) ou 11 (inclusive ARM), conforme a página oficial em 31/08/2026.

**Caminho recomendado: instalação nativa. Não use WSL2 para o Anki.**
*Por quê:* o Anki é um aplicativo gráfico com áudio. No WSL2 ele exige WSLg, o áudio é instável
e o acesso ao seu perfil do Windows passa por um sistema de arquivos de rede lento. WSL2 é
excelente para o Linux de desenvolvimento; é a ferramenta errada aqui.

**Passo 1 — baixar e instalar.**

Baixe o `anki-<versão>-windows-qt6.exe` em https://apps.ankiweb.net e execute.
Aceite o caminho padrão (`%LOCALAPPDATA%\Programs\Anki`) — instalar em `C:\Program Files` exige
elevação e cria dor de cabeça com add-ons que escrevem na própria pasta.

**Alternativa por linha de comando (winget, já embutido no Windows 11):**
```powershell
winget install --id Anki.Anki -e
```
*O que faz:* baixa e instala a versão oficial sem interação.

Verificação (PowerShell):
```powershell
& "$env:LOCALAPPDATA\Programs\Anki\anki.exe" --version
# esperado: 26.08.1
```
*Se der "não é reconhecido como nome de cmdlet":* o caminho está errado. Descubra com:
```powershell
Get-ChildItem -Path C:\ -Filter anki.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
```

**Windows ARM (Surface, Copilot+ PC):** existe pacote nativo desde 2025; se não achar, o pacote
x64 roda por emulação, com perda de desempenho aceitável para uso normal.

**Antivírus:** alguns antivírus corporativos põem o `anki.exe` em quarentena por ser um
executável Python empacotado sem assinatura corporativa. Se o app sumir depois da instalação,
procure na quarentena antes de reinstalar.

---

## 03.3 Conta AnkiWeb e aplicativos de celular

### Conta AnkiWeb (grátis, sem cartão)

1. Acesse https://ankiweb.net e clique em *Sign Up*.
2. Confirme o e-mail.
3. No Anki do computador: **Ferramentas → Preferências → Sincronização**, cole o e-mail e a
   senha, e clique em **Sincronizar** (ou tecle `Y`).

Verificação: a barra inferior mostra `Sync complete`. Entrando em https://ankiweb.net você vê
seus baralhos.

**Limite real:** a conta gratuita do AnkiWeb comporta coleções de até algumas centenas de MB e
mídia limitada — mais que suficiente para vocabulário; apertado se você colar vídeo em cada
cartão. Não corte vídeo dentro dos cartões; use imagem estática e áudio curto.

### Android — AnkiDroid (grátis, código aberto)

- Google Play: `AnkiDroid Flashcards` (`com.ichi2.anki`)
- Ou, sem Google, pela F-Droid: https://f-droid.org/en/packages/com.ichi2.anki/

Verificação: abra → menu ⋮ → *Sincronizar*; os baralhos do computador aparecem.

### iOS — AnkiMobile (pago)

É o **único** app oficial no iOS e custa uma licença única (ver [80-custos-e-licencas](80-custos-e-licencas.md)).
A receita dele financia o desenvolvimento do Anki inteiro, que é gratuito em todo o resto.

**Alternativa gratuita no iPhone:** use https://ankiweb.net pelo Safari e adicione à tela de
início. Funciona, revisa e sincroniza; perde o modo offline e alguns tipos de cartão.

---

## 03.4 Configuração inicial do Anki — os cinco ajustes que importam

Instalar e sair com os padrões é desperdiçar metade da ferramenta.

1. **Ative o FSRS.** *Opções do baralho → FSRS → ligar.*
   O FSRS (*Free Spaced Repetition Scheduler*) substitui o antigo SM-2, é treinado em centenas
   de milhões de revisões reais e agenda ~20–30% menos revisões para a mesma retenção.
   Está disponível desde a versão 23.10 e é o padrão para novas instalações nas versões 25.x+;
   **em coleções antigas migradas ele pode estar desligado — confira.**
2. **Retenção desejada: 0,90.** É o padrão e o ponto de equilíbrio. Subir para 0,95 aumenta as
   revisões diárias em quase 50% para ganhar 5 pontos de retenção — mau negócio.
   Depois de ~1.000 revisões, clique em **Optimize** para o FSRS ajustar os parâmetros ao **seu**
   esquecimento.
3. **Limite de cartões novos por dia: comece com 10.** Cada cartão novo gera ~8–10 revisões ao
   longo dos meses. 30 novos/dia viram 250 revisões/dia em três meses e você abandona. Aumente
   só quando o número de revisões estabilizar.
4. **Desligue o "enterrar" agressivo e ligue `Show answer timer`** se você tende a ficar 40 s
   olhando para o cartão. Regra: se não veio em 8 segundos, é "de novo".
5. **Backup automático:** *Preferências → Backups* — mantenha pelo menos 30 diários. O Anki já
   faz isso, mas confira o caminho e leia o §03.16.

---

## 03.5 Add-ons do Anki — os úteis e o risco

**Aviso de segurança, não decorativo:** add-on de Anki é **código Python arbitrário rodando com
as suas permissões de usuário**. Não há sandbox. Instale apenas add-ons conhecidos, com muitas
avaliações, e não instale nada que você não vá usar.

Instalação: *Ferramentas → Add-ons → Obter Add-ons* e cole o código numérico do add-on, obtido
em https://ankiweb.net/shared/addons — **pegue o código no site, não de listas de terceiros:
os códigos mudam e listas antigas fazem você instalar outra coisa.**

| Add-on | Para quê | Observação |
|---|---|---|
| **AnkiConnect** | abre uma API local (`http://127.0.0.1:8765`) para que navegador e scripts criem cartões | é a peça que liga o Language Reactor e o [07-projeto-modelo](07-projeto-modelo/) ao Anki |
| **HyperTTS** | gera áudio de pronúncia automaticamente para os cartões | sucessor do AwesomeTTS, que está descontinuado |
| **Review Heatmap** | mostra a constância em calendário | puramente motivacional, e funciona |
| **Advanced Browser** | busca e edição em massa | útil a partir de ~2.000 cartões |

Verificação do AnkiConnect (com o Anki **aberto**):
```bash
curl -s -X POST http://127.0.0.1:8765 -d '{"action":"version","version":6}'
# esperado: {"result": 6, "error": null}
```
*Se retornar vazio ou erro de conexão:* o Anki está fechado, o add-on não foi instalado, ou —
caso clássico — **o seu proxy corporativo está sequestrando `127.0.0.1`**. Ver §03.14.

---

## 03.6 Dicionários

### Online (o que você vai usar 95% do tempo)

| Dicionário | Por que | Link |
|---|---|---|
| **Cambridge** | definições em inglês simples + áudio britânico e americano + nível CEFR de cada palavra | https://dictionary.cambridge.org/ |
| **Merriam-Webster** | referência do inglês americano, etimologia boa | https://www.merriam-webster.com/ |
| **Longman (LDOCE)** | definições escritas com um vocabulário controlado de 2.000 palavras — o melhor para iniciante | https://www.ldoceonline.com/ |
| **Youglish** | ouve a palavra em centenas de vídeos reais, por sotaque | https://youglish.com/ |
| **Linguee** | tradução **com contexto** de textos reais bilíngues | https://www.linguee.com.br/ |
| **Ozdic / SkELL** | **colocações**: com que palavras aquela palavra costuma andar | https://skell.sketchengine.eu/ |

> **Regra de ouro:** a partir do nível A2, use **dicionário monolíngue** (inglês→inglês) como
> padrão e bilíngue como socorro. O bilíngue ensina uma equivalência falsa; o monolíngue ensina
> o conceito e ainda te dá mais insumo. Ver [45-reading](45-reading.md) §45.5.

### Offline — GoldenDict-ng (Linux/Windows/macOS)

Para estudar sem internet, ou para consultar em 50 ms em vez de 2 s.

Debian/Ubuntu:
```bash
sudo apt install -y goldendict-ng || sudo apt install -y goldendict
```
Fedora:
```bash
sudo dnf install -y goldendict-ng || sudo dnf install -y goldendict
```
macOS:
```bash
brew install --cask goldendict-ng
```
Windows: instalador em https://github.com/xiaoyifang/goldendict-ng/releases

Verificação: abra o programa; ele deve iniciar mesmo sem nenhum dicionário carregado.

Depois é preciso **alimentar** o GoldenDict com arquivos de dicionário (formatos `.dsl`,
`.ifo`/StarDict, `.mdx`). O caminho legalmente limpo é usar dumps do **Wiktionary**, que é
CC BY-SA. Não baixe pacotes de dicionários comerciais pirateados — é violação de direito autoral
e, na prática, a maior fonte de arquivos com malware nesse nicho.

### Enciclopédia offline — Kiwix

Wikipédia inteira em inglês, offline, para leitura extensiva sem internet:
```bash
# Linux
sudo apt install -y kiwix    # ou: flatpak install flathub org.kiwix.desktop
```
Baixe o arquivo `.zim` de https://library.kiwix.org/ — a versão "simple English" tem ~1 GB e é
**excelente** para B1: textos reais, vocabulário controlado.

---

## 03.7 Extensões de navegador

Funcionam em Chrome, Edge, Brave e (a maioria) Firefox. Instale pela loja oficial do navegador;
extensão de idioma é um alvo comum de clones maliciosos, então **confira o desenvolvedor e o
número de usuários**.

| Extensão | O que faz | Custo |
|---|---|---|
| **LanguageTool** | corrige gramática e estilo em qualquer caixa de texto | grátis até ~10.000 caracteres por checagem |
| **Language Reactor** | legendas duplas em Netflix/YouTube, clique na palavra → definição, exportar para Anki | grátis com limites; ver [80](80-custos-e-licencas.md) |
| **Anki Quick Adder / ankiconnect helpers** | manda a palavra selecionada direto para o Anki | grátis |

**LanguageTool sem enviar seu texto para a nuvem** (importante se você escreve documento de
trabalho): o motor é código aberto e roda local via Docker.

```bash
docker run --rm -d -p 8010:8010 --name languagetool erikvl87/languagetool
```
*O que faz:* sobe o servidor do LanguageTool na sua máquina, na porta 8010.

Verificação:
```bash
curl -s --noproxy '*' -X POST http://localhost:8010/v2/check \
  -d "language=en-US" -d "text=I has a apple" | head -c 200
# esperado: um JSON com "matches":[ ... ] apontando os dois erros
```
Depois, na extensão: *Configurações → Servidor local → `http://localhost:8010/v2`*.

*Nota:* o `--noproxy '*'` do `curl` acima não é enfeite. Ver o §03.14 — proxy corporativo mal
configurado é a causa nº 1 de "o servidor local não responde".

---

## 03.8 Áudio e vídeo — insumo real

Estes são opcionais, mas transformam qualquer vídeo do mundo em material de estudo.

### mpv (tocador que permite legenda dupla e velocidade variável)

```bash
# Debian/Ubuntu
sudo apt install -y mpv
# Fedora
sudo dnf install -y mpv
# macOS
brew install mpv
# Windows
winget install --id mpv.net -e
```
Verificação:
```bash
mpv --version | head -1
# esperado: mpv 0.34.1 (ou superior)
```

### ffmpeg (corta e converte áudio — usado para gerar o áudio dos cartões)

```bash
sudo apt install -y ffmpeg        # Debian/Ubuntu
sudo dnf install -y ffmpeg-free   # Fedora (ou ffmpeg do RPM Fusion)
brew install ffmpeg               # macOS
winget install --id Gyan.FFmpeg -e  # Windows
```
Verificação:
```bash
ffmpeg -version | head -1
# esperado: ffmpeg version 4.4.2 (ou superior)
```

Exemplo real de uso — extrair 6 segundos de áudio para colar num cartão do Anki:
```bash
ffmpeg -ss 00:12:31 -t 6 -i aula.mp4 -vn -acodec libmp3lame -q:a 4 trecho.mp3
```

### yt-dlp (baixa vídeo, áudio e **legendas**)

```bash
# recomendado em qualquer SO com Python: instalação isolada por usuário
python3 -m pip install --user --upgrade yt-dlp
```
Verificação:
```bash
yt-dlp --version
# esperado: uma data no formato AAAA.MM.DD, recente
```
*Se a versão for antiga (ex.: `2022.04.08`, que é o que vem no repositório do Ubuntu 22.04),*
*atualize:* o YouTube quebra versões velhas em semanas. `python3 -m pip install --user -U yt-dlp`.

Baixar **só a legenda em inglês** de um vídeo (o uso mais valioso, e o mais leve):
```bash
yt-dlp --write-auto-sub --sub-lang en --skip-download --convert-subs srt "<URL>"
```

> ⚖️ **Aviso legal, sem rodeios.** Baixar conteúdo protegido por direito autoral para uso pessoal
> é uma zona cinzenta que varia por país, e **burlar DRM** (o caso de Netflix, Prime, Disney+) é
> ilegal na maioria das jurisdições e viola os termos de uso. Baixe de fontes explicitamente
> livres: podcasts com feed RSS aberto, TED Talks (CC BY-NC-ND), vídeos sob Creative Commons,
> conteúdo de domínio público (LibriVox, Project Gutenberg), material da VOA (domínio público
> dos EUA). Para streaming pago, use as legendas **dentro** do serviço (é para isso que o
> Language Reactor existe) em vez de extrair arquivos.

### Audacity (gravar-se — a ferramenta mais ignorada e mais eficaz)

```bash
sudo apt install -y audacity     # Debian/Ubuntu
sudo dnf install -y audacity     # Fedora
brew install --cask audacity     # macOS
winget install --id Audacity.Audacity -e   # Windows
```
No celular, o gravador nativo já resolve. O que importa é **ouvir a própria gravação ao lado da
do nativo**. Ver [40-speaking](40-speaking.md) §40.6.

---

## 03.9 Podcasts

| SO | App recomendado | Por quê |
|---|---|---|
| Android | **AntennaPod** (código aberto, F-Droid/Play) | velocidade variável, download offline, sem conta |
| iOS | Apple Podcasts (nativo) ou Pocket Casts | idem |
| Desktop | qualquer navegador, ou `mpv <url-do-mp3>` | — |

Ajuste que muda tudo: **velocidade 0,8× no começo, 1,0× depois, 1,25× quando ficar fácil.**
Reduzir velocidade não é trapaça — é dar ao seu cérebro o tempo que ele ainda precisa para
segmentar as palavras. Ver [35-listening](35-listening.md).

---

## 03.10 Teclado: digitar em inglês e digitar IPA

**Aspas e traços:** o inglês usa `'` (apóstrofo reto) em *don't*, *it's*. Se o seu sistema
substitui automaticamente por `’`, tudo bem em texto corrido, mas quebra código e senhas.

**Digitar símbolos do IPA** (ə, ɪ, ʌ, θ, ð, ŋ) — necessário se você anotar pronúncia:

- **Mais simples e multiplataforma:** copie de https://ipa.typeit.org/
- **Linux:** ative a tecla *compose* ou use `Ctrl+Shift+U` seguido do código Unicode
  (ex.: `Ctrl+Shift+U` `2 5 9` `Enter` → `ə`).
- **macOS:** *Ajustes → Teclado → Fontes de entrada → Unicode Hex Input*, depois `Option`+código.
- **Windows:** o app *Character Map*, ou `Win + .` para o painel de símbolos.

Você não precisa digitar IPA para aprender inglês. Precisa **ler** IPA — isso sim, e o
[05-manual-de-uso](05-manual-de-uso.md) ensina.

---

## 03.11 Python (só para o projeto-modelo)

O [07-projeto-modelo](07-projeto-modelo/) traz scripts que geram baralhos e medem seu progresso.
Eles usam **só a biblioteca padrão** — nenhuma dependência para instalar.

```bash
python3 --version
# esperado: Python 3.10.12 (ou superior; mínimo 3.9)
```

- **Linux:** já vem instalado. Se faltar: `sudo apt install -y python3` / `sudo dnf install -y python3`.
- **macOS:** `brew install python@3.12` (o Python do sistema é antigo e a Apple desaconselha usá-lo).
- **Windows:** `winget install --id Python.Python.3.12 -e` — e **marque "Add python.exe to PATH"**
  se usar o instalador gráfico. Sem isso, `python` não é reconhecido no terminal.

---

## 03.12 PATH e variáveis de ambiente

O **PATH** é a lista de pastas onde o terminal procura programas. Quando você instala algo e o
terminal diz `command not found`, o programa quase sempre **está lá** — só não está no PATH.

Ver o PATH atual:
```bash
echo "$PATH"
# esperado: uma lista separada por ':' contendo /usr/local/bin e ~/.local/bin
```

Descobrir onde um programa foi parar:
```bash
command -v anki || ls -l /usr/local/bin/anki
```

Adicionar `~/.local/bin` (onde o `pip install --user` coloca os executáveis, como o `yt-dlp`):

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```
*O que faz:* acrescenta a pasta ao PATH toda vez que um terminal novo abrir.

**Em qual arquivo?**

| Shell / SO | Arquivo |
|---|---|
| bash (Linux) | `~/.bashrc` |
| zsh (macOS desde Catalina, e Linux com zsh) | `~/.zshrc` |
| fish | `~/.config/fish/config.fish` (sintaxe diferente: `fish_add_path ~/.local/bin`) |
| PowerShell (Windows) | `$PROFILE` — veja o caminho com `echo $PROFILE` |

**Por que "não pegou"?** Porque esses arquivos são lidos **quando o terminal abre**. A mudança
não afeta terminais já abertos. Feche e abra, ou force:
```bash
source ~/.bashrc && echo "$PATH"
```

No Windows, depois de mexer em variáveis pelo painel de Sistema, é preciso **fechar e reabrir o
terminal** — e, em alguns casos, deslogar. Verificação:
```powershell
$env:PATH -split ';'
```

---

## 03.13 Permissões — onde `sudo` estraga

Regra: **nunca instale pacotes Python globais com `sudo`.**

```bash
sudo pip install yt-dlp      # ❌ NÃO FAÇA
python3 -m pip install --user yt-dlp   # ✅
```

**Por que é problema, e não só "má prática":** o `pip` como root escreve dentro de
`/usr/lib/python3/dist-packages`, o mesmo diretório gerenciado pelo `apt`/`dnf`. Os dois
gerenciadores não conversam. O resultado típico é o `pip` sobrescrever uma biblioteca de que
uma ferramenta do sistema depende — e, em distros baseadas em Python, isso **quebra o próprio
gerenciador de pacotes**, deixando a máquina sem como instalar ou remover nada. Já custou
reinstalação de sistema para muita gente.

Em Python 3.11+ o próprio pip recusa e mostra `error: externally-managed-environment`. A saída
correta é `--user`, `pipx` ou um ambiente virtual:
```bash
python3 -m venv ~/.venvs/ingles && source ~/.venvs/ingles/bin/activate
```

**No Anki:** rode-o como usuário normal, sempre. Se você abrir o Anki com `sudo` uma única vez,
os arquivos da sua coleção passam a pertencer ao root e o Anki normal deixa de conseguir
gravar. Conserto:
```bash
sudo chown -R "$USER":"$USER" ~/.local/share/Anki2
```

---

## 03.14 Rede corporativa: proxy, certificado, firewall

Se você estuda no computador da empresa, esta seção economiza horas.

**Configurar o proxy para o terminal:**
```bash
export http_proxy="http://usuario:senha@proxy.empresa.com:8080"
export https_proxy="$http_proxy"
export no_proxy="localhost,127.0.0.1,::1"
```

⚠️ **A armadilha que derruba mais gente:** o `no_proxy` precisa incluir `localhost` **e**
`127.0.0.1` **e** `::1`, separados por vírgula **sem espaços**. Um `no_proxy` malformado
(com espaços, ou com `http://` na frente, ou faltando `127.0.0.1`) faz as bibliotecas HTTP do
Python e o `curl` mandarem para o proxy corporativo até as chamadas a `localhost` — e aí o
AnkiConnect (`127.0.0.1:8765`) e o LanguageTool local (`localhost:8010`) "não respondem", sem
nenhuma mensagem de erro útil. Sintoma clássico: `curl` funciona com `--noproxy '*'` e falha sem.

Teste:
```bash
curl -s -o /dev/null -w '%{http_code}\n' --noproxy '*' http://127.0.0.1:8765
# se der 200/405 com --noproxy e falhar sem, o problema é o proxy, não o serviço
```

**No Anki (interface):** *Ferramentas → Preferências → Rede* aceita as variáveis de ambiente do
sistema. Se a sincronização falhar com erro de SSL, o motivo costuma ser **certificado interno**:
a empresa intercepta o TLS com uma autoridade certificadora própria.

Instalar o certificado da empresa no Linux:
```bash
sudo cp certificado-empresa.crt /usr/local/share/ca-certificates/ && sudo update-ca-certificates
```
No macOS: *Keychain Access → System → Certificados → arrastar → marcar como "Always Trust"*.
No Windows: `certlm.msc` → *Autoridades de Certificação Raiz Confiáveis*.

**Firewall:** a sincronização do AnkiWeb usa HTTPS na porta 443 — quase nunca é bloqueada.
Já o `youtube.com` e o `ankiweb.net` às vezes caem em bloqueio de categoria "entretenimento".
Nesse caso, estude offline (Anki + arquivos baixados em casa) e sincronize fora da rede.

---

## 03.15 Convivência de versões

- **Anki:** só uma versão instalada por vez, mas você pode manter **duas coleções separadas**
  (perfis). *Arquivo → Trocar Perfil.* Use um perfil por língua, nunca baralhos misturados de
  línguas diferentes no mesmo perfil — os relatórios ficam inúteis.
- **Voltar para uma versão anterior do Anki:** todas ficam em
  https://github.com/ankitects/anki/releases. Instalar por cima funciona.
  ⚠️ **Downgrade destrutivo:** abrir a coleção com uma versão nova pode atualizar o formato do
  banco de dados, e a versão antiga então se recusa a abrir. **Exporte um backup `.colpkg`
  antes de qualquer atualização.**
- **Python:** use `pyenv` (Linux/macOS) ou o *py launcher* (`py -3.12`, Windows) se precisar de
  várias versões. Para este curso, uma serve.

---

## 03.16 Reprodutibilidade e backup — a parte que você só valoriza depois de perder

A sua coleção do Anki é o ativo mais valioso do seu estudo. Dois anos de vocabulário coletado
não se recupera.

**Backup manual completo (faça hoje):**
*Arquivo → Exportar → Pacote de Coleção do Anki (`.colpkg`)*, com mídia incluída.
Guarde fora da máquina (nuvem, HD externo, pendrive).

Onde a coleção vive:

| SO | Caminho |
|---|---|
| Linux | `~/.local/share/Anki2/` |
| macOS | `~/Library/Application Support/Anki2/` |
| Windows | `%APPDATA%\Anki2\` |

Backup por linha de comando (Linux/macOS), com o Anki **fechado**:
```bash
tar czf ~/backup-anki-$(date +%F).tar.gz -C ~/.local/share Anki2
```
Verificação:
```bash
tar tzf ~/backup-anki-$(date +%F).tar.gz | head -3
# esperado: listar Anki2/, Anki2/prefs21.db, ...
```

> **Sincronizar não é fazer backup.** O AnkiWeb replica o que você fez — inclusive a exclusão
> acidental de um baralho. Backup é uma cópia **congelada no tempo**, guardada em outro lugar.

**Reprodutibilidade do ambiente:** registre as versões que você usa num arquivo do próprio
repositório de estudo, do mesmo jeito que se faz com software:
```bash
{ anki --version; python3 --version; ffmpeg -version | head -1; yt-dlp --version; } > ~/ambiente-ingles.txt
```

---

## 03.17 Atualizar — e voltar atrás

| Software | Atualizar | Voltar atrás |
|---|---|---|
| **Anki (tarball)** | baixe o novo `.tar.zst` e repita o `sudo ./install.sh` | reinstale a versão antiga do GitHub Releases — **restaurando o `.colpkg` de backup** |
| **Anki (macOS/Windows)** | o próprio app avisa; ou `brew upgrade --cask anki` / `winget upgrade Anki.Anki` | idem |
| **AnkiDroid** | pela loja | APK antigo no GitHub do AnkiDroid |
| **Add-ons** | *Ferramentas → Add-ons → Verificar atualizações* | *Add-ons → selecionar → Ver arquivos* e restaurar manualmente; ou desinstalar |
| **yt-dlp** | `python3 -m pip install --user -U yt-dlp` | `pip install --user yt-dlp==<versão>` |

**Regra de campo:** não atualize o Anki **na véspera de uma prova ou de uma semana cheia**. E
nunca atualize sem `.colpkg` recente. Add-on incompatível com versão nova é o problema mais
comum, e o sintoma é o Anki abrir com uma tela de erro em vermelho na inicialização — que se
resolve iniciando com os add-ons desligados:
```bash
anki --safemode
```

---

## 03.18 Desinstalar por completo

Desinstalar o programa **não** apaga a sua coleção — e nem deve. Se você quer apagar tudo mesmo,
faça os dois passos.

### Linux (tarball)
```bash
sudo /usr/local/share/anki/uninstall.sh 2>/dev/null || sudo rm -rf /usr/local/share/anki /usr/local/bin/anki /usr/local/share/applications/anki.desktop
```
Dados e configurações (⚠️ irreversível):
```bash
rm -rf ~/.local/share/Anki2 ~/.local/share/anki ~/.config/Anki2
```
Flatpak: `flatpak uninstall --delete-data net.ankiweb.Anki`

### macOS
```bash
rm -rf /Applications/Anki.app
rm -rf ~/Library/Application\ Support/Anki2
rm -rf ~/Library/Saved\ Application\ State/net.ankiweb.dtop.savedState
rm -f  ~/Library/Preferences/net.ankiweb.dtop.plist
```
Ou, se instalou por Homebrew: `brew uninstall --zap --cask anki`.

### Windows
1. *Configurações → Aplicativos → Anki → Desinstalar* (ou `winget uninstall Anki.Anki`).
2. Restos:
```powershell
Remove-Item -Recurse -Force "$env:APPDATA\Anki2"
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\Programs\Anki"
```

### Conta AnkiWeb
Excluir a conta é feito só pelo site: https://ankiweb.net → *Account → Delete account*.
Desinstalar o programa não apaga nada do servidor.

### O resto
```bash
python3 -m pip uninstall -y yt-dlp
sudo apt remove --purge -y mpv ffmpeg audacity goldendict-ng && sudo apt autoremove -y
docker rm -f languagetool 2>/dev/null; docker rmi erikvl87/languagetool 2>/dev/null
```

---

## 03.19 Requisitos reais

| Recurso | Mínimo | Confortável | Observação |
|---|---|---|---|
| **Disco** | ~700 MB (Anki) | ~10 GB | com áudios, dicionários offline e um `.zim` do Kiwix |
| **Memória** | 2 GB | 4 GB+ | o Anki fica pesado acima de ~50.000 cartões com mídia |
| **CPU/arquitetura** | x86_64 ou ARM64 | — | há pacote nativo para Apple Silicon e Windows ARM |
| **Conta obrigatória** | nenhuma para o Anki local; AnkiWeb só se quiser sincronizar | — | — |
| **Cartão de crédito** | **não** para nada listado como grátis aqui | — | AnkiMobile (iOS) é o único item pago do conjunto essencial |
| **Internet** | só para baixar e sincronizar | — | o Anki revisa 100% offline |

---

## 03.20 Solução de problemas — mensagens literais

| Mensagem | Causa provável | Correção |
|---|---|---|
| `command not found: anki` | `/usr/local/bin` fora do PATH, ou o `install.sh` não rodou | `ls -l /usr/local/bin/anki`; se existir, ver §03.12; se não, refaça o passo 3 do §03.2.1 |
| `qt.qpa.plugin: Could not load the Qt platform plugin "xcb"` | faltam bibliotecas gráficas do Qt | rode o `apt install` do passo 1 (§03.2.1) — em especial `libxcb-cursor0`; em Wayland, tente `QT_QPA_PLATFORM=xcb anki` |
| `error: externally-managed-environment` (pip) | Python 3.11+ protege os pacotes do sistema | use `python3 -m pip install --user ...`, `pipx`, ou um `venv` (§03.13) |
| `EACCES: permission denied` / `Permission denied` ao gravar em `~/.local/share/Anki2` | o Anki já foi executado com `sudo` alguma vez | `sudo chown -R "$USER":"$USER" ~/.local/share/Anki2` |
| `Anki failed to load your collection file` / `DBError: database is locked` | duas instâncias abertas, ou desligamento no meio de uma gravação | feche tudo, `pkill anki`, reabra; se persistir, *Ferramentas → Verificar Banco de Dados*; em último caso, restaure o `.colpkg` |
| `Unable to connect to AnkiWeb` / `SSL: CERTIFICATE_VERIFY_FAILED` | proxy corporativo interceptando TLS | instale o certificado interno (§03.14) |
| `Error connecting to AnkiConnect` (na extensão do navegador) | Anki fechado, add-on ausente, ou `no_proxy` sem `127.0.0.1` | abra o Anki; teste com `curl --noproxy '*'` (§03.5 e §03.14) |
| `ERROR: unable to download video data: HTTP Error 403: Forbidden` (yt-dlp) | versão do yt-dlp desatualizada | `python3 -m pip install --user -U yt-dlp` |
| `This add-on is not compatible with your version of Anki` | add-on antigo | atualize os add-ons; se travar a inicialização, `anki --safemode` |
| `App can't be opened because Apple cannot check it` (macOS) | Gatekeeper na primeira execução | botão direito → **Abrir** → *Abrir* de novo no diálogo |
| `python não é reconhecido como um comando interno` (Windows) | instalador rodou sem "Add to PATH" | reinstale marcando a opção, ou use `py -3` |
| `Sync conflict: local and remote collections differ` | você editou nos dois lados sem sincronizar | escolha **com cuidado** qual lado vence — o outro é descartado. Exporte `.colpkg` antes |

---

## 03.21 Checklist "ambiente pronto"

Rode um comando por linha. Se todos passarem, siga para o [04-como-comecar](04-como-comecar.md).

```bash
anki --version                    # → 26.08.1 (ou superior)
```
```bash
python3 --version                 # → Python 3.10.12 (ou superior)
```
```bash
ffmpeg -version | head -1         # → ffmpeg version 4.4.2 (ou superior)   [opcional]
```
```bash
mpv --version | head -1           # → mpv 0.34.1 (ou superior)             [opcional]
```
```bash
yt-dlp --version                  # → data recente                          [opcional]
```
```bash
curl -s --noproxy '*' -X POST http://127.0.0.1:8765 -d '{"action":"version","version":6}'
# → {"result": 6, "error": null}   (com o Anki aberto)                      [opcional]
```

E, fora do terminal:

- [ ] Anki abre e sincroniza com o AnkiWeb (`Sync complete`).
- [ ] FSRS ligado, retenção 0,90, 10 cartões novos/dia.
- [ ] AnkiDroid/AnkiWeb no celular mostra os mesmos baralhos.
- [ ] Um `.colpkg` de backup salvo **fora** do computador.
- [ ] Extensão do LanguageTool instalada no navegador.
- [ ] Fone de ouvido testado com um áudio da BBC Learning English.

---

## Fontes consultadas (31/08/2026)

- Anki — download, versão 26.08.1 e requisitos por SO: https://apps.ankiweb.net/
- Anki — manual de instalação em Linux (tarball, dependências): https://docs.ankiweb.net/platform/linux/installing.html
- Anki — releases anteriores: https://github.com/ankitects/anki/releases
- FSRS — algoritmo, disponibilidade desde a versão 23.10, treinamento e otimização: https://github.com/open-spaced-repetition/fsrs4anki
- AnkiDroid na F-Droid: https://f-droid.org/en/packages/com.ichi2.anki/
- LanguageTool — planos e servidor local: https://languagetool.org/ · https://help.languagetool.org/
- EF SET — teste gratuito de nivelamento: https://www.efset.org/
- Kiwix — biblioteca de arquivos `.zim`: https://library.kiwix.org/
- GoldenDict-ng — releases: https://github.com/xiaoyifang/goldendict-ng/releases

*Versões locais usadas na verificação: Ubuntu 22.04.5 LTS · Python 3.10.12 · ffmpeg 4.4.2 · mpv 0.34.1 · zstd presente · x86_64.*

---

## Autoteste

1. Qual é o caminho para começar a estudar hoje sem instalar nada?
2. Por que não se deve usar o pacote `anki` do repositório do Ubuntu?
3. O que é o FSRS e por que é preciso conferi-lo numa coleção antiga?
4. Explique, tecnicamente, por que `sudo pip install` pode quebrar o gerenciador de pacotes.
5. Você roda o LanguageTool local e a extensão não conecta. Qual é a primeira hipótese e como se testa em um comando?
6. Qual a diferença entre sincronizar e fazer backup? O que cada um protege?
7. `command not found: anki`, mas o arquivo existe em `/usr/local/bin`. O que está errado e onde se corrige?
8. Por que baixar legendas da Netflix com `yt-dlp` é diferente, juridicamente, de baixar um TED Talk?
9. Onde fica a sua coleção do Anki nos três sistemas operacionais?

**Próximo:** [04-como-comecar.md](04-como-comecar.md) — do ambiente pronto às suas primeiras frases em inglês.
