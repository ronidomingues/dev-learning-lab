# 11 · História — como o campo nasceu e para onde foi

**Nível:** iniciante · **Data:** 03/09/2026

Entender a história explica **por que** as ferramentas e práticas de hoje são como são. Cada
técnica surgiu para resolver um problema concreto de sua época.

---

## Antes do software: a engenharia reversa industrial

Engenharia reversa é mais velha que o computador. Na Segunda Guerra e na Guerra Fria, países
copiavam equipamento inimigo: o bombardeiro soviético **Tupolev Tu-4** (1947) foi uma cópia
reversa, rebite a rebite, de B-29 americanos capturados. A indústria química e farmacêutica
reverte moléculas concorrentes há mais de um século. A ideia — *partir do produto e recuperar
o projeto* — é a mesma; só mudou o objeto.

**Lição que atravessa as décadas:** reverter sempre foi uma faca de dois gumes (inovação e
cópia), e a lei sempre correu atrás da técnica. Isso não mudou.

---

## Linha do tempo do software

| Período | Marco | Por que importou |
|---|---|---|
| **1950s–60s** | Programação direta em assembly; *core dumps* impressos | "Reverter" era ler o próprio dump; nasce o hábito de pensar em registradores e memória |
| **1970s** | Unix, C, o montador/desmontador como ferramenta | Surge a distinção fonte × binário que torna o RE necessário |
| **Início 1980s** | Micros pessoais; **cópia e proteção de jogos** | A guerra de "crackers" × esquemas de proteção nasce no Apple II / C64 / Spectrum |
| **1985** | **DEBUG** do DOS; primeiros desmontadores para PC | RE vira acessível a hobbistas |
| **1990** | **SoftICE** (depurador em nível de kernel, Windows) | Padrão-ouro por 15 anos; permitia depurar o que rodava "abaixo" do SO |
| **1991** | **IDA** (Interactive Disassembler), por Ilfak Guilfanov | Muda tudo: desmontagem *interativa* com renomeação, tipos, banco de dados persistente |
| **1998** | **DMCA** (EUA) e diretivas de cópia | A lei entra pesado: anticircunvenção. RE ganha zonas cinzentas jurídicas |
| **1999** | **DeCSS** (quebra da proteção de DVDs por engenharia reversa) | Caso emblemático de RE × direito autoral; Jon Lech Johansen processado |
| **2000s** | Ascensão do **malware** em massa | A análise de malware profissionaliza o RE; nascem sandboxes e antivírus modernos |
| **2005** | **Hex-Rays Decompiler** (plugin do IDA) | O descompilador vira produto: assembly → pseudo-C, produtividade dispara |
| **2008** | **OllyDbg**, **IDA Pro** dominam Windows | Era de ouro do RE de desktop |
| **2010** | **Stuxnet** revertido publicamente | Malware de Estado-nação; RE vira geopolítica. Mostra o teto de complexidade do campo |
| **2014** | **radare2** ganha tração (open-source) | Alternativa livre e programável ao IDA |
| **2019** | **Ghidra** liberado pela **NSA** (open-source) | Democratiza um descompilador de nível militar. Divisor de águas: qualidade top, custo zero |
| **2016–hoje** | **Frida**, instrumentação dinâmica | Reverter apps móveis/desktop vivos em JavaScript; muda o RE mobile |
| **2019** | **Binary Ninja** amadurece; API/`IL` de análise | Foco em automação e *intermediate languages* de análise |
| **2024–2026** | **Descompilação neural (LLM)**: LLM4Decompile e sucessores | IA que traduz binário → C legível; a fronteira atual ([`65`](65-estado-da-arte.md)) |

---

## Três batalhas que moldaram o campo

### 1. Crackers × proteção de cópia (1980s–90s)
Os primeiros "engenheiros reversos" de massa foram adolescentes removendo proteção de jogos.
Isso criou a cultura dos **crackmes** (desafios feitos para treinar), das *scene groups*, e
das técnicas de patching que hoje se ensinam de forma legítima. A indústria respondeu com
*dongles*, ativação online e ofuscação — a corrida armamentista que continua
([`18`](18-ofuscacao-e-packers.md), [`19`](19-anti-analise.md)).

### 2. Interoperabilidade × direito autoral (1990s)
Empresas queriam que seus programas conversassem com formatos fechados de concorrentes.
Tribunais americanos (**Sega v. Accolade**, 1992; **Sony v. Connectix**, 2000) firmaram que
**reverter para interoperabilidade pode ser *fair use***. A Europa consagrou isso na diretiva
de software (91/250/CEE, depois 2009/24/CE). Foi o que legalizou emuladores e libs abertas.

### 3. Malware × defensores (2000s–hoje)
A explosão de vírus, worms e depois ransomware transformou o RE de nicho em **profissão de
segurança**. Cada família de malware nova força técnicas novas de análise; cada técnica de
análise força os autores a se esconderem melhor. É o motor que mais financia o campo hoje.

---

## Por que Ghidra (2019) foi tão importante

Até 2019, o descompilador sério (Hex-Rays/IDA) custava milhares de dólares — uma barreira que
mantinha o RE de alto nível restrito a empresas e governos. Quando a **NSA** liberou o
**Ghidra** como open-source (Apache 2.0), colocou um descompilador de qualidade militar na mão
de qualquer estudante. O efeito: uma geração inteira aprendeu RE sem pagar licença, cursos
floresceram, e a IDA teve de repensar preços (ver [`80-custos-e-licencas.md`](80-custos-e-licencas.md)).
Este curso é filho dessa mudança — ensina com ferramenta gratuita porque **ela existe e é boa**.

*(Opinião do autor, marcada como tal:* a liberação do Ghidra foi o evento mais importante para
a democratização do RE na década de 2010; nada mais chega perto.)*

---

## O que se repete (padrões que voltam)

- **Toda proteção é temporária.** Do dongle ao DRM à ofuscação por IA — cada esquema compra
  tempo, nenhum é definitivo. A razão é o teorema do [`10-fundamentos.md`](10-fundamentos.md):
  o código roda em claro em algum momento.
- **A lei sempre chega depois da técnica** e raramente a acompanha. Por isso as zonas
  cinzentas (o Brasil é um exemplo: lei de software omissa sobre RE).
- **Ferramenta livre acaba vencendo em alcance.** SoftICE morreu; IDA reina em nichos; mas o
  volume de novos reversos aprende em Ghidra/r2/GDB.

---

## Autoteste

1. Dê um exemplo de engenharia reversa **anterior ao computador** e diga o que ele tem em
   comum com reverter software.
2. Por que a IDA (1991) foi um divisor de águas em relação aos desmontadores anteriores?
3. O que os casos *Sega v. Accolade* e *Sony v. Connectix* firmaram, e por que isso importa
   para emuladores?
4. Explique, em uma frase, por que a liberação do Ghidra (2019) mudou o acesso ao campo.
5. Qual é o "motor econômico" que mais financia a engenharia reversa hoje, e por quê?
6. Cite dois padrões históricos que "se repetem" e a razão técnica de um deles.
