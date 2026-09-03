# 02 · Pré-requisitos — o que saber, ter e instalar antes

`Nível: iniciante` · `Última atualização: 12/08/2026`

Este arquivo é o filtro honesto. Ele diz o que você precisa saber antes, quanto tempo leva
de verdade, e o que fazer se faltar alguma coisa.

**Nada aqui é bloqueio permanente.** Todo pré-requisito tem uma rota de resgate na seção 6.

---

## 1. Conhecimento — indispensável

Se um destes faltar, você vai travar em duas semanas. Não é elitismo: são as coisas que
aparecem em *todo* material intermediário sem serem explicadas.

### 1.1 Linha de comando Linux

**Por quê:** ~95% das ferramentas ofensivas são de linha de comando, e a maioria dos alvos
de servidor é Linux. Você vai viver no terminal.

**O mínimo que precisa saber fazer sem pesquisar:**

| Tarefa | Comandos |
|---|---|
| Navegar e listar | `cd`, `ls -la`, `pwd`, `tree` |
| Ler e editar arquivo | `cat`, `less`, `nano` ou `vim` (o básico do `vim`: `i`, `Esc`, `:wq`) |
| Buscar | `grep -r`, `find / -name`, `which` |
| Encadear | `|` (pipe), `>` e `>>` (redirecionamento), `&&` |
| Permissões | `chmod +x`, `chown`, entender `rwx` e o que `root` significa |
| Processos e rede | `ps aux`, `kill`, `ss -tulpn`, `ip a` |
| Pacotes | `apt install`, `apt update` |
| Texto | `cut`, `sort`, `uniq -c`, `wc -l`, `awk '{print $1}'`, `sed 's/a/b/'` |

**Onde aprender (gratuito):**
- [OverTheWire — Bandit](https://overthewire.org/wargames/bandit/) — 34 níveis, é *o* padrão
  do campo para isso. Faça do 0 ao 20. Leva de 8 a 15 horas. É a melhor recomendação isolada
  deste arquivo inteiro.
- [Linux Journey](https://linuxjourney.com/) — leitura estruturada, em inglês.
- [Curso de Linux — Bóson Treinamentos (YouTube, PT)](https://www.youtube.com/c/BosonTreinamentos) — em português.

**Teste de suficiência:** consegue explicar o que este comando faz, sem executar?
```bash
grep -rn "password" /etc 2>/dev/null | cut -d: -f1 | sort -u | head -20
```
Se sim, você passou. (Resposta: busca recursivamente a palavra `password` em `/etc` mostrando
número de linha, joga fora os erros de permissão, extrai só o nome do arquivo, remove
duplicatas e mostra os 20 primeiros.)

### 1.2 Redes TCP/IP — o modelo mental

**Por quê:** hacking é, quase sempre, fazer um computador falar com outro de um jeito que ele
não deveria aceitar. Sem entender como eles falam, você só copia comando.

**O mínimo:**

- O que é endereço IP, máscara de sub-rede e gateway. O que significa `192.168.1.0/24`.
- Diferença entre IP público e privado (RFC 1918) e o que NAT faz.
- O que é uma **porta** e o que significa uma porta estar aberta, fechada ou filtrada.
- Diferença entre **TCP** (confiável, com aperto de mão de três vias) e **UDP** (sem garantia).
- O que o **DNS** faz e o caminho de uma consulta.
- O que acontece, em ordem, quando você digita um endereço no navegador e aperta Enter.
  (Pergunta clássica de entrevista, e não é por acaso: ela cobre DNS, TCP, TLS, HTTP e
  renderização de uma vez.)
- As camadas — modelo OSI de 7 camadas e o modelo TCP/IP de 4. Você não precisa decorar, mas
  precisa saber em que camada está o problema quando alguém disser "ataque de camada 2".

**Onde aprender (gratuito):**
- [Curso de Redes — Bóson Treinamentos (YouTube, PT)](https://www.youtube.com/playlist?list=PLucm8g_ezqNoNHU8tjVeHmRGBFnjDIlxD)
- [Computer Networking: A Top-Down Approach — Kurose & Ross](https://gaia.cs.umass.edu/kurose_ross/index.php) — o livro-padrão; o site tem material aberto. Há tradução para o português (Pearson).
- Este repositório: se existir a pasta `redes-de-computadores`, comece por ela.
- [TryHackMe — trilha "Pre Security"](https://tryhackme.com/path/outline/presecurity) — gratuita.

**Teste de suficiência:** explique em voz alta a diferença entre um `SYN scan` e um
`connect scan` do nmap. Se não souber, leia [`15-varredura-e-enumeracao.md`](15-varredura-e-enumeracao.md)
— ele ensina isso do zero, mas é mais fácil se o TCP já estiver na cabeça.

### 1.3 Como a web funciona

**Por quê:** a maior parte dos alvos, das vagas e do dinheiro em bug bounty está na web.

**O mínimo:**
- HTTP: método (`GET`, `POST`, `PUT`, `DELETE`), status (`200`, `301`, `401`, `403`, `500`),
  cabeçalhos, corpo.
- O que é um **cookie** e o que é uma **sessão**.
- Diferença entre o que roda no **cliente** (navegador, JavaScript) e no **servidor**.
  Isto é a origem conceitual de metade das falhas web: validação feita só no cliente.
- HTML e um pouco de JavaScript — o suficiente para ler, não para escrever bem.
- O que é uma **API REST** e o que é **JSON**.
- Same-origin policy: por que uma página de um site não pode ler os dados de outro.

**Onde aprender:** se existir a pasta `apis` neste repositório, ela cobre HTTP e REST em
profundidade. Fora daqui: [MDN Web Docs em português](https://developer.mozilla.org/pt-BR/).

### 1.4 Inglês técnico de leitura

**Por quê:** e não há como contornar. As ferramentas, a documentação, os *write-ups*, os
avisos de vulnerabilidade, os exames de certificação e 90% do conteúdo bom são em inglês.
O material em português é bom para começar e insuficiente para continuar.

**O mínimo:** ler documentação técnica com dicionário. Não precisa falar nem escrever bem
no começo — mas precisa ler sem sofrer.

**Rota de resgate:** leia com tradutor no começo, sem vergonha. Em 6 meses de exposição
diária o vocabulário técnico se repete tanto que a barreira cai. O vocabulário de segurança
é de umas 500 palavras.

---

## 2. Conhecimento — ajuda muito (mas não trava)

| Assunto | Por que ajuda | Onde aprender |
|---|---|---|
| **Python** | Automatizar, adaptar exploits públicos, escrever ferramenta própria. É a língua franca ofensiva. | [Curso em Vídeo — Python (PT, gratuito)](https://www.cursoemvideo.com/curso/python-3-mundo-1/) |
| **Windows e Active Directory** | Onde está o dinheiro corporativo. A maioria dos pentests internos é AD. | [`20-active-directory.md`](20-active-directory.md) deste curso |
| **Programação em geral** | Você lê código para achar bug. Qualquer linguagem serve para criar o hábito. | qualquer curso de lógica |
| **SQL** | Injeção de SQL ainda é campeã de impacto. Precisa saber `SELECT`, `UNION`, `WHERE`. | pasta `postgresql` deste repositório |
| **Docker / containers** | Todo laboratório moderno e boa parte dos alvos de nuvem. | pasta `docker` deste repositório |
| **Git** | Portfólio, ferramentas, e vazamento de segredo em histórico de commit é achado comum. | qualquer tutorial |
| **Nuvem (AWS/Azure/GCP)** | Onde está a superfície nova. Diferencial forte em 2026. | [`21-nuvem-e-containers.md`](21-nuvem-e-containers.md) |
| **Assembly x86-64 e C** | Só para exploração de binário / pesquisa de vulnerabilidade. Não precisa para começar. | [`16`](16-vulnerabilidades-e-exploracao.md) e [`60`](60-teoria-avancada.md) |

---

## 3. Ambiente — hardware e software

### 3.1 Hardware mínimo e recomendado

| Item | Mínimo doloroso | Recomendado | Confortável |
|---|---|---|---|
| **RAM** | 8 GB | 16 GB | 32 GB |
| **CPU** | 4 núcleos com virtualização (VT-x / AMD-V) | 6–8 núcleos | 8+ núcleos |
| **Disco** | 100 GB livres, HDD | 250 GB **SSD** | 500 GB+ NVMe |
| **Rede** | qualquer | qualquer | adaptador Wi-Fi USB com modo monitor, se for fazer wireless |

**Explicação franca dos números.** O gargalo não é CPU, é RAM e disco. Um laboratório
mínimo roda o Kali (4 GB) e um alvo (2 GB) ao mesmo tempo — com 8 GB você fica no limite e
o navegador com 20 abas vai matar sua máquina. Com 16 GB você roda Kali + 2 alvos + navegador
sem pensar. Um laboratório de Active Directory (1 controlador de domínio + 2 estações) pede
16 GB **só para as VMs** — por isso a linha "confortável" tem 32.

Cada VM ocupa de 20 a 60 GB. Kali completo, ~25 GB. Windows Server, ~40 GB. Some.

**Virtualização precisa estar ligada na BIOS/UEFI.** É o erro nº 1 de quem começa: a VM não
liga e a pessoa acha que o software está quebrado. Verificação:

```bash
# Linux — se retornar 0, a virtualização está desligada na BIOS
grep -Ec '(vmx|svm)' /proc/cpuinfo
```
```powershell
# Windows PowerShell — deve dizer True
(Get-CimInstance Win32_Processor).VirtualizationFirmwareEnabled
```

Se der 0 / False: reinicie, entre na BIOS (geralmente `Del`, `F2` ou `F10` no boot), procure
por *Intel VT-x*, *AMD-V*, *SVM Mode* ou *Virtualization Technology*, e habilite.

### 3.2 Sistema operacional do hospedeiro

| Hospedeiro | Veredito |
|---|---|
| **Linux (Ubuntu/Fedora/Debian)** | Melhor caminho. Menos atrito, virtualização nativa (KVM), você aprende Linux só de usar. |
| **Windows 11** | Perfeitamente viável com VirtualBox/VMware ou WSL2. É o que a maioria usa. |
| **macOS Apple Silicon (M1–M4)** | Viável, com ressalva: Kali roda em ARM64, mas parte dos alvos e binários de laboratório é x86-64 e vai exigir emulação lenta (UTM/QEMU) ou uma VM na nuvem. Veja [`03-instalacao.md`](03-instalacao.md) §7. |
| **macOS Intel** | Sem ressalvas. |
| **Chromebook / tablet** | Não. Use laboratório na nuvem (TryHackMe/HTB pelo navegador). |

**Regra que salva emprego:** o Kali (ou qualquer distro ofensiva) vai numa **máquina virtual**,
não no seu computador principal. Motivo: isolamento. Ferramenta ofensiva roda com privilégio,
vem de fonte variada, e alvo de laboratório é intencionalmente vulnerável. Se você rodar
alvo vulnerável na mesma rede da sua casa sem isolamento, você acabou de expor a sua casa.

### 3.3 Contas em serviços — quais criar

| Serviço | Precisa? | Gratuito? | Cartão? |
|---|---|---|---|
| [TryHackMe](https://tryhackme.com) | Muito recomendado | Camada gratuita real | Não |
| [Hack The Box](https://hackthebox.com) | Recomendado depois | Máquinas ativas gratuitas | Não |
| [PortSwigger Web Security Academy](https://portswigger.net/web-security) | **Sim** | 100% gratuito, 250+ labs | Não |
| [GitHub](https://github.com) | Sim — portfólio | Sim | Não |
| [OverTheWire](https://overthewire.org) | Sim | Sim, sem conta | Não |
| [HackerOne](https://hackerone.com) / [Bugcrowd](https://bugcrowd.com) | Depois de 6 meses | Sim | Só para receber pagamento |
| Provedor de nuvem (AWS/Azure/GCP) | Opcional | Camada gratuita | **Sim, exige cartão** |

Detalhes de preço, limite da camada gratuita e onde ela acaba: [`80-custos-e-licencas.md`](80-custos-e-licencas.md).

---

## 4. Pré-requisito não técnico — e é o que mais elimina gente

### 4.1 Tolerância à frustração

A profissão é, estatisticamente, falhar. Você vai tentar 30 coisas e 29 não funcionam.
Se você desanima quando algo não funciona na terceira tentativa, esta carreira vai ser
sofrimento diário. Não é força de vontade — é gosto. Algumas pessoas acham divertido bater
numa parede por 6 horas até achar a fresta. Se você é essa pessoa, você já sabe.

### 4.2 Disciplina de anotação

Quem não anota, refaz. Escolha uma ferramenta de notas hoje e use desde o primeiro laboratório:
[Obsidian](https://obsidian.md) (gratuito, arquivos locais em Markdown — minha recomendação),
[CherryTree](https://www.giuspen.net/cherrytree/) (clássico do meio), ou uma pasta com
arquivos `.md` no Git. O formato importa menos que o hábito.

### 4.3 Ética que aguenta pressão

Você vai ter, cedo, o poder técnico de fazer coisa ilegal e a chance de fazê-la sem ser pego —
provavelmente antes de ter maturidade de carreira. Isso é um teste real, não retórica.
Um único episódio destrói a carreira: o setor é pequeno, checa antecedentes, e ninguém
contrata quem tem processo por invasão. Leia [`12-etica-lei-e-contrato.md`](12-etica-lei-e-contrato.md).

---

## 5. Tempo realista até cada nível

Baseado em pessoas reais, não em propaganda de curso. Assume **estudo consistente**, não
maratona. Se você estuda 2h/dia úteis + 4h no fim de semana, isso é ~14h/semana.

| Nível | O que você consegue fazer | Tempo a 14h/semana | Tempo a 5h/semana |
|---|---|---|---|
| **Pré-requisitos** (Linux, redes, web) | Sobreviver a um material intermediário | 2–4 meses | 6–10 meses |
| **Iniciante funcional** | Resolver máquinas "fáceis" do HTB/THM seguindo raciocínio próprio | +3–4 meses | +8–12 meses |
| **Júnior empregável** | Passar em entrevista de pentest júnior / SOC; eJPT ou PJPT no bolso | 10–18 meses | 2–3 anos |
| **Pentester pleno** | Conduzir um teste sozinho, do escopo ao relatório; OSCP/CPTS/PNPT | 2–4 anos | 4–6 anos |
| **Sênior / especialista** | Liderar red team, achar 0-day, virar referência num nicho | 5–10 anos | — |
| **Pesquisador** | Publicar vulnerabilidade nova em software popular, falar em conferência | 6–12 anos | — |

**Sendo brutalmente honesto sobre isso:** qualquer anúncio de "seja um hacker profissional em
30 dias" está mentindo ou está vendendo o nível "iniciante funcional" como se fosse o júnior
empregável. O tempo até o **primeiro salário** costuma ser de 12 a 24 meses para quem já
trabalha em TI, e de 24 a 36 meses para quem vem de fora da área. Isso é o normal, não o
fracasso.

**O que acelera de verdade** (em ordem de impacto):
1. Já trabalhar em TI — suporte, infra, rede, dev, SOC. Corta o tempo praticamente pela metade.
2. Prática com as mãos > vídeo assistido. 1h de laboratório vale 4h de vídeo.
3. Escrever *write-ups* públicos do que você resolveu. Consolida e vira portfólio ao mesmo tempo.
4. Comunidade — Discord de plataforma, grupo local, conferência (BSides, H2HC, Roadsec no Brasil).
5. Inglês. Multiplica o material disponível por 10.

**O que desacelera:** colecionar cursos sem praticar; pular fundamento para ir direto ao
exploit; assistir vídeo achando que é estudo; ficar 8 meses escolhendo a "melhor" certificação.

---

## 6. Rota de resgate — o que fazer se faltar algo

| Falta | O que fazer **hoje** |
|---|---|
| **Não sei Linux** | Pare tudo e faça OverTheWire Bandit 0→20. 2 semanas. Não é opcional. |
| **Não sei redes** | Trilha "Pre Security" do TryHackMe (gratuita) + Kurose cap. 1–3. 3 semanas. |
| **Não sei web** | PortSwigger Academy, seção "Getting started". Gratuito, no navegador, sem instalar nada. |
| **Não sei programar** | Comece por Python. Automatize algo chato do seu dia. 1 mês. Não estude "programação" no vazio. |
| **Inglês fraco** | Leia write-ups com tradutor. Todo dia um. 3 meses e a barreira cai. |
| **Computador fraco (< 8 GB)** | Use laboratório na nuvem: TryHackMe e HTB rodam no navegador. Zero instalação. Veja [`03`](03-instalacao.md) §1. |
| **Sem tempo** | 45 min/dia consistentes batem 8h de sábado. Sério. |
| **Sem dinheiro** | O caminho 100% gratuito existe e está mapeado em [`85-cursos-e-certificacoes.md`](85-cursos-e-certificacoes.md). |
| **Não trabalho com TI** | Entre por uma porta lateral: suporte, help desk, NOC, SOC nível 1. Aceite o salário baixo por 12 meses; é o pedágio mais rápido. |

---

## 7. Checklist antes de ir para o `03-instalacao.md`

- [ ] Sei navegar, ler, buscar e encadear comandos no terminal Linux sem consultar.
- [ ] Sei o que é IP, porta, TCP, UDP e DNS.
- [ ] Sei a diferença entre o que roda no navegador e o que roda no servidor.
- [ ] Consigo ler documentação técnica em inglês (com dicionário, tudo bem).
- [ ] Tenho ao menos 8 GB de RAM e 100 GB livres — ou aceitei o caminho de nuvem.
- [ ] Virtualização está habilitada na BIOS (comando de verificação da §3.1 retorna > 0 / True).
- [ ] Escolhi uma ferramenta de anotação e ela está instalada.
- [ ] **Li e entendi que testar sem autorização é crime** — ou vou ler
      [`12-etica-lei-e-contrato.md`](12-etica-lei-e-contrato.md) antes de rodar qualquer coisa.

Marcou tudo? → [`03-instalacao.md`](03-instalacao.md).
Faltou algo? → seção 6 acima. Não pule; você volta para cá de qualquer jeito, só que 3 meses
mais frustrado.

---

## Autoteste

1. Por que a linha de comando Linux é indispensável e não "ajuda muito"?
2. O que este comando faz: `ss -tulpn | grep LISTEN`?
3. Por que 8 GB de RAM é chamado de "mínimo doloroso" em vez de simplesmente "mínimo"?
4. Por que o Kali deve rodar em máquina virtual e não no computador principal?
5. Quanto tempo, de forma realista, até o primeiro salário na área para quem já trabalha
   com TI? E para quem vem de fora?
6. Cite três coisas que aceleram o aprendizado e três que o desaceleram.
7. Você tem 6 GB de RAM e um notebook antigo. Qual é a sua rota?
8. Qual pré-requisito não técnico elimina mais gente, e por quê?
9. Por que estudar inglês é considerado um multiplicador e não um detalhe?
