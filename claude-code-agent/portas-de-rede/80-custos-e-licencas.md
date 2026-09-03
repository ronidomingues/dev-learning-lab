# 80 · Custos e licenças

**Nível:** todos · **Preços consultados na web em 14/08/2026**
**Câmbio usado:** 1 USD ≈ **R$ 5,19** (cotação de referência de 14/08/2026, via
[Investing.com](https://br.investing.com/currencies/usd-brl)). Câmbio muda; use os valores em
BRL apenas como ordem de grandeza.

---

## A primeira linha, que é a mais importante

**Todo o conhecimento e praticamente todo o ferramental deste curso são gratuitos e de
código aberto.** `ss`, `lsof`, `nmap`, `netcat`, `socat`, `tcpdump`, Wireshark, `nftables`,
`iptables`, `masscan`, `ZMap`, `RustScan`, `naabu` — nenhum cobra nada, nenhum exige
cadastro, nenhum pede cartão de crédito.

Você pode aprender e trabalhar com este assunto no nível profissional **gastando zero**.

O que custa dinheiro está em três categorias, e vale saber quais são:

1. **Inteligência pronta** (Shodan, Censys) — pagar para não ter que varrer você mesmo.
2. **Certificação** — pagar por um papel, não por conhecimento.
3. **O custo oculto de uma porta aberta** — a categoria que ninguém orça, e a mais cara.

---

## 1. Ferramentas — licenças e o que elas permitem

| Ferramenta | Licença | Uso comercial | Observação |
|---|---|---|---|
| **`iproute2`** (`ss`) | GPL-2.0+ | ✅ livre | Já vem no Linux |
| **`net-tools`** (`netstat`) | GPL-2.0 | ✅ livre | Obsoleto |
| **`lsof`** | Licença própria estilo BSD | ✅ livre | Permissiva, exige atribuição |
| **`Nmap`** | **NPSL** ⚠️ | **Ver abaixo** | Não é GPL pura |
| **`Npcap`** | **Proprietária** ⚠️ | **Restrita** | Ver abaixo |
| **`netcat` (OpenBSD)** | BSD | ✅ livre | |
| **`ncat`** (Nmap) | NPSL | mesma do Nmap | |
| **`socat`** | GPL-2.0 | ✅ livre | |
| **`tcpdump` / `libpcap`** | BSD 3-cláusulas | ✅ livre | |
| **`Wireshark`** | GPL-2.0+ | ✅ livre | |
| **`masscan`** | AGPL-3.0 ⚠️ | Cuidado se for serviço | AGPL alcança uso em rede |
| **`ZMap`** | Apache-2.0 | ✅ livre | |
| **`RustScan`** | GPL-3.0 | ✅ livre | |
| **`naabu`** | MIT | ✅ livre | |
| **`nftables`/`iptables`** | GPL-2.0 | ✅ livre | |

### ⚠️ A licença do Nmap merece leitura, não suposição

O Nmap **não é GPL comum**. Desde a versão 7.90 (2020) usa a **NPSL** (*Nmap Public Source
License*), derivada da GPLv2 com restrições adicionais.

O ponto que importa na prática: **embutir o Nmap num produto comercial fechado, ou vendê-lo
como parte de um serviço, pode exigir licença comercial paga**. O projeto vende essa licença
via Nmap Software LLC.

**O que é claramente permitido:** usar o Nmap no seu trabalho, em pentest pago, em auditoria
interna, em CI, em script próprio, em consultoria.

**Onde surge a dúvida:** distribuir o binário dentro do seu produto, ou construir um SaaS
cuja funcionalidade central é rodar Nmap para clientes.

**Se o seu caso é o segundo, leia a licença e, se houver dinheiro envolvido, consulte
jurídico.** Este material não dá parecer legal — aponta que existe uma pergunta a fazer, que
a maioria das pessoas não sabe que existe.

### ⚠️ Npcap — a peça proprietária do conjunto

O Npcap (captura de pacotes no Windows, necessário ao Nmap e ao Wireshark lá) tem
**licença proprietária**:

- gratuito para uso pessoal e interno;
- **redistribuição dentro de produto comercial exige licença paga** (há uma edição OEM);
- há limite de instalações no uso gratuito, conforme os termos vigentes.

É a única peça deste conjunto com essa restrição. Verifique os termos atuais em
[npcap.com](https://npcap.com/) antes de embutir em qualquer coisa.

### ⚠️ masscan e AGPL

A AGPL-3.0 estende a obrigação de disponibilizar o código-fonte a quem **usa o software pela
rede**, não só a quem recebe o binário. Se você construir um serviço web que roda `masscan`
no servidor, a AGPL pode alcançar seu código. É uma armadilha comum em produtos de segurança.

---

## 2. Serviços pagos de descoberta

### Shodan

| Plano | Preço (14/08/2026) | ≈ BRL/mês | Para quem |
|---|---|---|---|
| Conta gratuita | US$ 0 | R$ 0 | Poucos resultados, sem filtro avançado |
| **Membership** (vitalícia) | **US$ 49, pagamento único** | ≈ R$ 254 **uma vez** | **Estudo. É a melhor relação custo-benefício de segurança que existe.** |
| Freelancer | US$ 69/mês | ≈ R$ 358 | Profissional autônomo |
| Small Business | US$ 359/mês | ≈ R$ 1.863 | Equipe |
| Corporate | US$ 1.099/mês | ≈ R$ 5.704 | Empresa |
| Enterprise | sob consulta | — | Volume alto |

*(Fonte: compilações de preço consultadas em 14/08/2026 — [TrustRadius](https://www.trustradius.com/products/shodan/pricing),
[SoftwareSuggest](https://www.softwaresuggest.com/shodan/pricing). Confirme sempre em
[account.shodan.io/billing](https://account.shodan.io/billing) antes de comprar.)*

**Opinião profissional, declarada:** a Membership vitalícia de US$ 49 é a compra de melhor
retorno deste assunto inteiro. Não é uma assinatura, não renova, e desbloqueia filtros
suficientes para auditar a superfície exposta da sua própria organização de forma séria.
O Shodan costuma fazer promoções (Black Friday em torno de US$ 5) — vale esperar por elas.

### Censys

Preço inicial reportado em torno de **US$ 62** (≈ R$ 322) em compilações de 2026, com uma
camada gratuita de consultas limitadas. Os planos empresariais são sob consulta.

*(Fonte: [SoftwareSuggest — Censys pricing](https://www.softwaresuggest.com/censys/pricing),
consultado em 14/08/2026. Confirme em [censys.com](https://censys.com/).)*

### Alternativas gratuitas

| Serviço | O que dá | Limite |
|---|---|---|
| [Shodan gratuito](https://www.shodan.io/) | Busca básica | Poucos resultados |
| [Censys Search](https://search.censys.io/) | Busca por host e certificado | Consultas/mês limitadas |
| [crt.sh](https://crt.sh/) | Certificate Transparency | **Totalmente gratuito** |
| [ZoomEye](https://www.zoomeye.org/) | Equivalente chinês | Camada gratuita |
| **Varrer você mesmo** | Tudo, dos seus alvos | Seu tempo e sua banda |

**crt.sh merece destaque:** é gratuito, sem cadastro, e revela subdomínios pelos certificados
emitidos. Para descoberta de ativos da própria organização, entrega uma fração enorme do
valor do Shodan a custo zero.

---

## 3. Laboratórios e ambiente

| Recurso | Custo |
|---|---|
| Sua própria máquina | **R$ 0** — cobre 100 % do curso |
| VirtualBox / KVM | **R$ 0** |
| Docker | **R$ 0** (Docker Desktop tem restrição para empresa grande — ver [`docker`](../docker/00-MAPA.md)) |
| WSL2 | **R$ 0**, incluso no Windows |
| Oracle Cloud Always Free | **R$ 0** — VMs ARM permanentes. **Exige cartão para validar** |
| Google Cloud e2-micro | camada gratuita, **exige cartão** |
| AWS free tier | 12 meses, **exige cartão** |
| VPS (Hetzner, Contabo, brasileiros) | ~US$ 4–8/mês (≈ R$ 21–42) |
| **`scanme.nmap.org`** | **R$ 0** — alvo autorizado pelo projeto Nmap |
| TryHackMe | grátis com limite; assinatura ~US$ 14/mês (≈ R$ 73) |
| Hack The Box | grátis com limite; VIP ~US$ 14/mês (≈ R$ 73) |

⚠️ **"Camada gratuita que exige cartão" é um custo oculto real.** Vários casos de conta de
nuvem "gratuita" com fatura inesperada vêm de tráfego de saída ou de recurso deixado ligado.
Se você usar nuvem para estudar, **configure alerta de orçamento em US$ 1** no primeiro dia.

---

## 4. Custos ocultos — a categoria que ninguém orça

### 4.1 O custo de uma porta aberta

| Item | Ordem de grandeza |
|---|---|
| Ransomware por RDP exposto | resgate + parada + recuperação. Casos brasileiros na casa de centenas de milhares a milhões de reais |
| Vazamento de banco exposto | LGPD: multa de até **2 % do faturamento**, limitada a R$ 50 milhões por infração |
| Servidor usado para mineração | fatura de nuvem inesperada — casos documentados de dezenas de milhares de dólares em dias |
| IP em lista de bloqueio (proxy aberto) | e-mail da empresa para de ser entregue. Dias de trabalho para sair |
| Investigação de incidente | R$ 30–100 mil para resposta terceirizada, no mercado brasileiro |

**Comparação que fecha o argumento:** um `ss -tulpn` semanal custa cinco minutos. O
[projeto-modelo](07-projeto-modelo/README.md) deste curso automatiza isso e sai com código
de erro utilizável em CI — custo zero. A assimetria entre o custo da prevenção e o do
incidente é de várias ordens de grandeza, e é o argumento mais fácil de vender para uma
diretoria.

### 4.2 Egress — o custo que a nuvem cobra e ninguém prevê

Provedores de nuvem cobram **tráfego de saída**. Uma varredura ou uma transferência grande
gera egress.

Ordens de grandeza (consulte a tabela vigente do seu provedor — mudam):
tipicamente entre **US$ 0,05 e US$ 0,12 por GB** (≈ R$ 0,26 a R$ 0,62/GB) nas grandes nuvens,
com os primeiros GB do mês gratuitos.

Um serviço exposto que vira alvo de DDoS gera egress **que você paga**. Já houve faturas de
cinco dígitos por isso.

### 4.3 Aprisionamento (*lock-in*)

| Onde | Como acontece |
|---|---|
| Security Groups | Regras escritas no formato do provedor. Migrar exige reescrever tudo |
| Ferramenta de varredura comercial | Histórico e relatórios em formato fechado |
| Service mesh | Política amarrada ao produto |

**A defesa:** manter o inventário de portas em formato próprio e neutro — JSON, versionado
em git. É exatamente o que `auditor.py local --json` produz, e é uma decisão de arquitetura
barata que se paga na primeira migração.

### 4.4 Treinamento e tempo

O custo real deste assunto é **tempo de pessoa**. Pelas estimativas do
[`02-pre-requisitos.md`](02-pre-requisitos.md): 15–25 h até o nível confortável,
60–100 h até competente. A um custo-hora de R$ 80–150, são R$ 5 mil a R$ 15 mil de tempo por
pessoa até a competência — e é o melhor investimento desta lista.

---

## 5. Certificações — o que custa

Detalhes e avaliação de valor em [`85-cursos-e-certificacoes.md`](85-cursos-e-certificacoes.md).

| Certificação | Preço (14/08/2026) | ≈ BRL |
|---|---|---|
| **CompTIA Network+ (N10-009)** | US$ 399 direto; **US$ 338–385** via revendedor | ≈ R$ 2.070 / R$ 1.754–1.998 |
| **Cisco CCNA (200-301)** | US$ 300 + impostos locais | ≈ R$ 1.557 + |
| CompTIA Security+ | ~US$ 4xx | ≈ R$ 2.100+ |
| OSCP (Offsec) | ~US$ 1.749+ | ≈ R$ 9.075+ |

*(Fontes consultadas em 14/08/2026: compilações de preço de
[Total Seminars](https://totalsem.com/comptia-network-plus-exam-cost/) e
[DiviTrain](https://www.divitrain.com/blogs/it-certifications/cisco-ccna-exam-cost-2026-full-breakdown).
A CompTIA reajustou os preços de toda a linha em junho de 2026 — o Network+ passou de
US$ 390 para US$ 399. Confirme sempre em comptia.org e cisco.com antes de comprar.)*

**Nota importante:** a versão atual do Network+ é a **N10-009**, não a N10-010. Materiais que
citam a N10-010 estão à frente do que existe.

---

## 6. Quanto custa começar, na prática

| Cenário | Custo |
|---|---|
| Aprender tudo deste curso | **R$ 0** |
| Ambiente completo de laboratório em VM | **R$ 0** |
| Auditar a sua organização | **R$ 0** (ferramentas) + tempo |
| Auditar com inteligência pronta | **R$ 254**, uma vez (Shodan Membership) |
| Certificar-se | R$ 1.500 – 2.100 (Network+ ou CCNA) |
| Ignorar tudo isso | **potencialmente milhões**, uma vez |

---

## 7. Quem paga a conta das ferramentas gratuitas?

Pergunta legítima. Software livre não é grátis de produzir.

| Ferramenta | Quem sustenta |
|---|---|
| `iproute2`, kernel Linux | Empresas que dependem do Linux (Red Hat, Google, Meta, Intel...) |
| **Nmap** | **Licenciamento comercial da NPSL** + o Npcap OEM. É o modelo do projeto |
| Wireshark | Sysdig (patrocinador) + comunidade |
| `tcpdump`/`libpcap` | Comunidade, com apoio institucional histórico |
| `masscan` | Autor individual (Robert Graham) |
| ZMap | Universidade de Michigan, financiamento de pesquisa |
| Shodan | **É pago.** É o modelo de negócio, não um projeto aberto |

**A leitura honesta:** o Nmap é gratuito para você porque outras pessoas pagam licença
comercial. Isso é sustentável e legítimo — e é a razão de a licença dele merecer leitura
antes de embutir em produto.

---

## Autoteste

1. Qual é a única ferramenta deste curso com licença proprietária, e o que ela restringe?
2. Você vai embutir varredura de portas num produto SaaS comercial. Quais duas licenças
   desta página exigem atenção jurídica, e por quê?
3. Por que a Membership vitalícia do Shodan é apresentada aqui como a melhor relação
   custo-benefício? Qual alternativa gratuita entrega parte do valor?
4. Cite três custos ocultos de uma porta aberta que não aparecem em nenhum orçamento.
5. Por que "camada gratuita que exige cartão" é um risco real? Qual é a primeira medida a
   tomar?
6. Quem paga o desenvolvimento do Nmap, se ele é gratuito para você?
7. Faça a conta: uma equipe de 5 pessoas até o nível "competente", a R$ 120/h. Compare com
   o custo típico de uma resposta a incidente.

---

*Próximo: [`85-cursos-e-certificacoes.md`](85-cursos-e-certificacoes.md).*
