# 80 · Custos e licenças

**Nível:** todos · **Preços consultados na web em:** 03/09/2026
**Câmbio de referência:** US$ 1 ≈ R$ 5,40 (aprox., set/2026 — confira a cotação do dia).

> **Preço sem data é desinformação.** Tudo abaixo tem data de consulta. Valores em moeda
> original **e** ordem de grandeza em BRL. Ferramentas de RE mudam de política de preço com
> frequência (a IDA virou assinatura em 2024; o Binary Ninja mexeu em preços em 2026) — sempre
> confirme na fonte oficial antes de comprar.

---

## 1. A boa notícia: o essencial é gratuito

**Você aprende e trabalha em RE sério gastando R$ 0.** A pilha central é toda livre:

| Ferramenta | Licença | Custo |
|---|---|---|
| **Ghidra** | Apache 2.0 (open-source) | Grátis |
| **GDB** (+ pwndbg/GEF) | GPL | Grátis |
| **radare2 / rizin / Cutter** | LGPL/GPL | Grátis |
| **binutils** (objdump, readelf, nm) | GPL | Grátis |
| **Capstone / Keystone / Unicorn** | BSD | Grátis |
| **angr** | BSD | Grátis |
| **Frida** | wxWindows/LGPL | Grátis |
| **x64dbg** | GPLv3 | Grátis |
| **jadx / apktool / dnSpyEx / ILSpy** | Apache/MIT/GPL | Grátis |
| **YARA / capa / FLOSS** | Apache/BSD | Grátis |
| **REMnux / Kali / FLARE VM** | livres (agregados) | Grátis |

**Quem paga a conta?** Ghidra é bancado pela **NSA** (interesse próprio: capacitar a
comunidade de segurança e recrutar). radare2/rizin/angr vêm de academia e comunidade. Frida é
mantido por um núcleo pequeno + patrocínios. O modelo é: ferramenta livre, monetização via
suporte, treinamento, ou o próprio interesse institucional do mantenedor.

---

## 2. Ferramentas comerciais — quando e quanto

Você **não precisa** delas para aprender. Empresas as compram por conforto, suporte e nichos.

### IDA (Hex-Rays) — o padrão histórico da indústria
Desde **1º/10/2024**, IDA é vendida **só por assinatura** (acabaram as licenças perpétuas).
Preços consultados em hex-rays.com/pricing em **03/09/2026** (por ano, USD ≈ BRL):

| Plano | Preço/ano | ~BRL/ano | Inclui |
|---|---|---|---|
| **IDA Free** | US$ 0 | R$ 0 | Decompiler x86/x64 na nuvem; debugger local x86/x64 |
| **IDA Home** | US$ 365 | ~R$ 2.000 | 2 decompiladores de uma família (x86/ARM/MIPS/PPC/RISC-V); uso não-comercial |
| **IDA Pro Essential** | US$ 1.099 | ~R$ 5.900 | 2 decompiladores na nuvem; 60+ processadores; debug remoto |
| **IDA Pro Expert-2** | US$ 2.999 | ~R$ 16.200 | 2 decompiladores **locais**; 60+ processadores |
| **IDA Pro Expert-4/6** | ~US$ 4.9k–6.9k | ~R$ 26k–37k | 4 ou 6 decompiladores locais |
| **IDA Pro Ultimate** | US$ 8.599 | ~R$ 46.400 | Todos os decompiladores locais |

Add-ons: Teams US$ 999/ano, licença flutuante US$ 1.700+/ano, Private Lumina US$ 299/ano.
**Leitura honesta:** IDA Pro é para quem reverte profissionalmente arquiteturas exóticas e
precisa do decompiler mais maduro. Para aprender e para 90% do trabalho, **Ghidra basta**.

### Binary Ninja (Vector 35)
Modelo diferente: **compra única** que inclui 1 ano de updates; a licença **não expira**.
Preços (mudança anunciada com a versão 6.0, ~19/08/2026):

| Edição | Preço | ~BRL | Nota |
|---|---|---|---|
| **Binary Ninja Free** (cloud/limitada) | US$ 0 | R$ 0 | Versão gratuita para experimentar |
| **Non-Commercial** | US$ 199 | ~R$ 1.075 | Uso pessoal/estudo (baixou de US$ 299 em 2026) |
| **Commercial** | ~US$ 449+ | ~R$ 2.400+ | Uso profissional |

Muitos gostam do Binary Ninja pela API/IL limpa para automação. É uma alternativa acessível à
IDA, mas ainda opcional frente ao Ghidra.

### Outras
- **Hopper** (macOS/Linux, popular no Mac): licença única na casa das ~US$ 100 (confirme).
- **JEB Decompiler** (Android/nativo, PNF Software): assinatura profissional (centenas a
  milhares de USD/ano).
- **Detect It Easy, x64dbg, dnSpy**: grátis.

---

## 3. Licenças — o que você pode fazer com cada ferramenta

| Licença | Permite | Cuidado |
|---|---|---|
| **Apache 2.0** (Ghidra) | Uso comercial, modificar, redistribuir; concede patentes | Manter avisos de licença |
| **GPL/LGPL** (GDB, radare2, x64dbg) | Uso comercial e modificação | Distribuir modificações do próprio programa sob GPL (copyleft) — relevante se você *redistribui a ferramenta*, não os resultados |
| **BSD/MIT** (Capstone, angr) | Quase tudo, inclusive fechar derivados | Manter aviso de copyright |
| **Proprietária/assinatura** (IDA) | Só o que o contrato diz; termina se a assinatura acaba | Ler a EULA: uso, transferência, engenharia reversa *da própria ferramenta* |

**Nota importante:** a licença da *ferramenta* não determina a legalidade de reverter um
*alvo* — isso é regido por direito autoral, contratos (EULA do alvo) e lei penal, não pela
licença do Ghidra. Ver a moldura legal na seção 6.

---

## 4. Custos ocultos

- **Hardware:** RAM (16 GB+ confortável), disco (100 GB+ com VMs), CPU com virtualização. Uma
  máquina decente para análise de malware pode custar o que você economiza em software.
- **Tempo de aprendizado:** o maior custo real. Meses a anos ([`02-pre-requisitos.md`](02-pre-requisitos.md)).
- **Nuvem/sandbox:** VMs em nuvem para análise, ou serviços de sandbox (any.run, Joe Sandbox,
  Hybrid Analysis têm planos pagos além do free).
- **Treinamento e certificação:** cursos de qualidade (SANS) custam caro — ver seção 5 e o
  arquivo [`85`](85-cursos-e-certificacoes.md).
- **Aprisionamento (lock-in):** um projeto grande anotado em IDA `.idb` não abre no Ghidra sem
  reimportar; escolher a ferramenta é assumir um custo de migração futuro.

---

## 5. Certificações — a ordem de grandeza (detalhe em [`85`](85-cursos-e-certificacoes.md))

Preços consultados em **03/09/2026**:

| Cert | Emissor | Ordem de preço | ~BRL |
|---|---|---|---|
| **GREM** (Reverse-Engineering Malware) | GIAC/SANS | Exame US$ ~999–1.299; curso FOR610 ~US$ 8.600 | Exame ~R$ 5,4k–7k; curso ~R$ 46k |
| **OSED** (EXP-301, exploit dev) | OffSec | Bundle ~US$ 1.749; Learn One ~US$ 2.749/ano | ~R$ 9,4k–14,8k |
| **eLearnSecurity / INE** (RE/malware) | INE | Assinatura mensal/anual (dezenas–centenas USD) | variável |

**Franqueza:** certificações caras (SANS) têm peso de mercado real em vagas de DFIR/malware,
mas **não são pré-requisito para aprender** nem para muitos empregos. O portfólio (writeups,
crackmes resolvidos, CVEs, contribuições) frequentemente vale mais que o certificado.

---

## 6. A moldura legal (resumo; aprofundado adiante)

Reverter uma ferramenta é uma coisa; reverter um **alvo** é regido por:
- **Direito autoral + EULA do alvo:** muitas EULAs proíbem RE (restrição contratual).
- **Lei penal de acesso não autorizado:** CFAA (EUA), **Lei 12.737/2012** (Brasil, invasão de
  dispositivo).
- **DMCA §1201 (EUA):** proíbe *contornar proteção*, com isenções permanentes para
  interoperabilidade e pesquisa de segurança (revisadas a cada 3 anos; última em out/2024).
- **UE (Diretiva 2009/24/CE):** autoriza descompilação para **interoperabilidade**.
- **Brasil (Lei 9.609/98, Lei do Software):** **omissa** sobre engenharia reversa — não a
  proíbe expressamente nem a protege como a lei europeia. Zona cinzenta; interpreta-se via
  direito autoral e limitações. (Ver [`95-referencias.md`](95-referencias.md).)

**Regra prática:** ferramentas grátis + alvos legítimos (seus, crackmes, CTFs, autorizados) =
zero custo e zero risco legal para aprender.

---

## Autoteste

1. É possível aprender e trabalhar com RE gastando R$ 0? Cite a pilha e quem financia o Ghidra.
2. O que mudou na comercialização da IDA em outubro de 2024, e qual o preço do plano gratuito hoje?
3. Diferencie o modelo de licença do Binary Ninja do da IDA.
4. A licença do Ghidra (Apache 2.0) determina se é legal reverter um dado alvo? Justifique.
5. Liste três custos **ocultos** de fazer RE profissionalmente.
6. Qual a ordem de preço do exame GREM e do curso SANS FOR610, e valem a pena para quem?
7. No Brasil, a Lei do Software proíbe engenharia reversa? Responda com precisão.

---

*Fontes consultadas em 03/09/2026:* hex-rays.com/pricing (IDA Free/Home/Pro), binary.ninja
(mudança de preços 6.0, jul/2026), páginas de release (Binary Ninja purchase), SANS/GIAC
(FOR610/GREM), OffSec (EXP-301/OSED), U.S. Copyright Office (9º ciclo §1201, out/2024),
EUR-Lex (Diretiva 2009/24/CE), Planalto (Lei 9.609/98, Lei 12.737/2012).
