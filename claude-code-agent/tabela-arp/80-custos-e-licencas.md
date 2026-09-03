# 80 · Custos e licenças

> **Nível:** todos
> **Data da consulta de preços: 14/08/2026.** Preço sem data é desinformação — reconfirme.

---

## Primeira linha, sem rodeios

> **O ARP e todo o software para estudá-lo e operá-lo em Linux são 100% gratuitos e de código
> aberto. Estudar este assunto do zero ao nível de pesquisa custa R$ 0,00.** O único custo real
> é **tempo** ([02](02-pre-requisitos.md) §5) e, se você não tiver hardware, alguns reais de
> nuvem opcionais. Não há licença a comprar, conta obrigatória nem cartão de crédito.

Quem "paga a conta"? O protocolo é um padrão da Internet (STD 37) de domínio público; as
ferramentas são mantidas por comunidades (kernel Linux, iproute2, Wireshark Foundation) e
empresas que dependem delas. O custo de manutenção é bancado por quem lucra com a
infraestrutura — não repassado a você.

---

## 1. O protocolo em si

| Item | Custo | Licença |
|---|---|---|
| Especificação (RFC 826 e correlatas) | grátis | domínio público (RFCs são livres) |
| Usar ARP | grátis | é parte de qualquer pilha TCP/IP |

---

## 2. Ferramentas de linha de comando (as essenciais)

| Ferramenta | Custo | Licença | Observação |
|---|---|---|---|
| **iproute2** (`ip neigh`) | grátis | GPL-2.0 | já vem no Linux |
| **net-tools** (`arp`) | grátis | GPL-2.0 | obsoleto, mas grátis |
| **tcpdump** | grátis | BSD-3 | libpcap por baixo (BSD) |
| **arping** (iputils) | grátis | BSD/GPL | pacote `iputils-arping` |
| **arp-scan** | grátis | GPL-3.0 | inclui base OUI |
| **arpwatch** | grátis | BSD/LBNL | monitor de mudanças |
| **Scapy** | grátis | GPL-2.0 | Python |

Todas *open source*. Você pode ler o código, modificar e redistribuir (respeitando a GPL onde
aplica). **Nenhuma** exige conta, chave ou pagamento.

---

## 3. Ferramentas gráficas / de rede

| Ferramenta | Custo | Licença | Custo oculto |
|---|---|---|---|
| **Wireshark** | grátis | GPL-2.0 | nenhum; no Windows usa Npcap (ver abaixo) |
| **Npcap** (captura no Windows) | grátis para uso pessoal | licença própria da Nmap | **redistribuição comercial embutida** exige licença paga (OEM) |
| **nmap** | grátis | NPSL (derivada de GPL) | uso é grátis; **embutir nmap em produto comercial** pode exigir licença |
| **VirtualBox** (lab) | grátis | GPL-2.0 (base) | o *Extension Pack* tem licença PUEL (grátis só para uso pessoal/educacional) |
| **Docker Desktop** (lab) | grátis para uso individual/pequeno | proprietária | **empresas com >250 funcionários ou >US$ 10 mi/ano pagam** assinatura; Docker Engine no Linux é grátis (Apache-2.0) |

> **Armadilha de licença mais comum:** achar que "nmap/Npcap é grátis" cobre **embutir** essas
> ferramentas num produto que você vende. Uso pessoal e profissional interno: grátis.
> Redistribuir dentro de um produto comercial: leia a licença, pode custar. Para *aprender e
> operar*, tudo aqui é grátis.

---

## 4. Custos de laboratório (opcionais)

Se você não tem uma máquina para montar o lab do [03](03-instalacao.md) §9:

| Opção | Custo (14/08/2026) | Observação |
|---|---|---|
| Sua própria máquina + VMs/Docker/namespaces | **R$ 0** | recomendado |
| **Google Cloud Shell** | grátis (com conta Google) | ~50 h/semana, efêmero |
| **Play with Docker / Killercoda** | grátis (com conta) | sessões de ~4 h |
| VM pequena na nuvem (AWS `t3.micro`, etc.) | ~US$ 5–10/mês se ligada 24/7; centavos por hora avulsa | **desligue quando não usar** — o custo oculto nº 1 é esquecer ligado |
| Camada gratuita AWS/GCP/Azure | 12 meses limitados | exige **cartão de crédito** no cadastro, mesmo no grátis |

**Onde a camada gratuita acaba:** as nuvens pedem cartão e cobram por *egress* (tráfego de
saída), IP público ocioso, e recursos deixados ligados. Para este assunto você não precisa de
nuvem — o lab local é gratuito e melhor (camada 2 real). Só considere nuvem se não tiver hardware.

---

## 5. Hardware — o custo real (baixo)

ARP não consome recursos; qualquer máquina dos últimos 15 anos basta ([02](02-pre-requisitos.md)
§4.1). Para os labs de ataque, 3 VMs pequenas cabem em **8 GB de RAM**. Disco: ~300 MB para
Wireshark, alguns GB por VM. Nada aqui exige comprar equipamento.

Switch gerenciado (para praticar DAI de verdade, [18](18-seguranca.md)): **não é necessário** —
a teoria e a config estão no material. Se quiser hardware para praticar, um switch gerenciado
usado (Cisco Catalyst antigo, ou um MikroTik/TP-Link gerenciado novo) custa de **R$ 150 a R$ 600**
no mercado de usados/entrada em 14/08/2026 — investimento opcional de quem vai trabalhar com redes.

---

## 6. Comparativo: gratuito vs. pago

Não há "versão paga do ARP". Onde aparece custo é em **plataformas de rede** que suprimem/gerenciam
ARP em escala:

| Categoria | Open source / grátis | Comercial | O que se ganha pagando |
|---|---|---|---|
| Inspeção de pacote | Wireshark, tcpdump | (nenhum domina) | — |
| Monitor de spoofing | arpwatch | XDR/NDR corporativos (Darktrace, etc.) | correlação, IA, suporte, escala |
| Switch com DAI | software (nftables em roteador Linux) | Cisco, Arista, Juniper | hardware, EVPN, suporte, garantia |
| Fabric com ARP suppression | FRR + Linux (montável) | Cisco ACI, Arista, NVIDIA Cumulus | integração pronta, suporte, escala de DC |

O que se perde indo de comercial para open source: **suporte, integração pronta e responsabilidade
de terceiro** — não capacidade técnica. O que se perde no caminho inverso: dinheiro e, às vezes,
liberdade (aprisionamento de fornecedor em fabrics proprietários).

---

## 7. Custos ocultos a vigiar

- **Nuvem ligada e esquecida** — o clássico. Desligue VMs de lab.
- **Cartão exigido no "grátis"** das nuvens — não é cobrança, mas é atrito e risco de esquecer.
- **Licença de redistribuição** de nmap/Npcap se você **embutir** em produto (não em uso).
- **Aprisionamento** em fabric proprietário de data center — migrar depois custa caro.
- **Tempo** — o maior custo real deste assunto, e o mais subestimado ([02](02-pre-requisitos.md) §5).

---

## Autoteste

1. Quanto custa aprender e operar ARP em Linux? Quem banca as ferramentas?
2. "nmap é grátis" — em que cenário isso deixa de ser verdade?
3. Onde a camada gratuita das nuvens "acaba", e por que você não precisa dela aqui?
4. Docker Desktop é grátis para você? Depende de quê?
5. O que se ganha e o que se perde ao trocar um switch com DAI comercial por um roteador Linux?
6. Qual é o maior custo real deste assunto?
7. Cite três custos ocultos e como evitá-los.

---

**Fontes (consultadas em 14/08/2026):** licenças oficiais dos projetos (GPL, BSD, Apache, NPSL,
Npcap, Docker Desktop, VirtualBox PUEL); páginas de preço de AWS/GCP; mercado de usados para
switches (ordem de grandeza). Preços em nuvem e hardware mudam — reconfirme.

**Próximo:** [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md)
