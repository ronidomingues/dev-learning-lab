# 65 · Estado da arte — onde estamos em agosto de 2026

**Nível:** pesquisa · **Data desta fotografia: 14/08/2026**
Todos os números desta página foram pesquisados na web em **14/08/2026** e têm fonte
indicada. **Reavalie este arquivo a cada seis meses** — é o que envelhece mais rápido do
curso.

---

## A tese central deste arquivo

> **O número da porta está deixando de ser um sinal útil.**

Durante quarenta anos, `(IP, porta)` foi *a* forma de identificar um serviço, rotear tráfego
e aplicar política de segurança. Em 2026, cada uma dessas três funções está migrando para
outro lugar:

| Função | Antes | Agora |
|---|---|---|
| **Identificar o serviço** | número da porta | SNI, `Host:`, ALPN, identidade SPIFFE |
| **Rotear** | porta → processo | nome de host e caminho de URL, no L7 |
| **Autorizar** | ACL por porta | identidade criptográfica mútua (mTLS) |

Isso **não** significa que portas deixaram de importar — o transporte continua precisando
delas, e o `ss -tulpn` continua sendo o comando mais útil do assunto. Significa que o
**valor informativo** do número caiu bastante, e continua caindo.

---

## 1. Consolidação em 443 — a porta que engoliu as outras

O movimento mais claro da década: **tudo virou HTTPS**.

| Protocolo | Antes | Hoje, cada vez mais |
|---|---|---|
| DNS | 53/UDP | **DoH em 443/TCP** |
| VPN | 1194, 500/4500 | 443, para atravessar firewall |
| RPC | portas próprias | gRPC sobre 443 |
| Mensageria | 5672, 9092 | WebSocket sobre 443 |
| SSH | 22 | tunelado em 443 onde a 22 é bloqueada |
| Administração | portas variadas | painel web em 443 |

**As três forças que causaram isso:**

1. **Firewalls corporativos.** A 443 é a única porta universalmente aberta na saída. Todo
   protocolo que quer funcionar em todo lugar migra para lá — não por mérito técnico, mas
   por sobrevivência. É a mesma lógica que o QUIC seguiu ao escolher UDP.
2. **CDNs e proxies reversos.** Concentrar tudo em 443 permite terminar TLS num lugar só,
   com um certificado só.
3. **Let's Encrypt.** TLS gratuito e automatizado removeu a última barreira econômica.

**Consequência para o defensor, e ela é grave:** *"a porta 443 está aberta"* deixou de ser
uma informação de segurança. Pode ser um site, uma VPN, um túnel SSH, um canal de comando e
controle de malware, ou exfiltração de dados. Distinguir exige inspeção de camada 7 —
justamente o que a criptografia tornou mais difícil.

**A defesa que sobrou:** analisar o *padrão* do tráfego (volume, ritmo, duração, destino),
não o seu conteúdo. É por isso que a monitoração baseada em comportamento cresceu tanto.

---

## 2. QUIC e HTTP/3 — adoção real

| Fonte | Métrica | Valor (2026) |
|---|---|---|
| W3Techs | Sites que **suportam** HTTP/3 | ~39 % |
| Cloudflare | Tráfego na borda deles | ~35 % |
| TechnologyChecker | **Carregamentos de página** servidos | ~21 % |

*(Pesquisado em 14/08/2026. As fontes divergem porque medem denominadores diferentes:
suportar não é ser usado.)*

A adoção mais alta aparece em mercados de uso predominantemente móvel — Itália (~30 %),
Brasil (~29 %), Índia (~29 %) — onde a resistência do QUIC a perda de pacote rende mais.

### O gargalo é exatamente o nosso assunto

As fontes de 2026 são consistentes: o principal obstáculo à adoção de HTTP/3 é que
**muitos proxies corporativos ainda bloqueiam UDP na porta 443**.

Um firewall que libera "443" pensando em TCP silenciosamente impede o HTTP/3. E como
navegadores caem de volta para TCP automaticamente e sem erro, **ninguém percebe** — o
sintoma é só desempenho pior.

**Teste da sua rede, agora:**

```bash
curl --http3 -sS -o /dev/null -w '%{http_version}\n' https://cloudflare.com/
# 3 = passou; 2 = caiu de volta, seu UDP/443 está bloqueado
```

### E o platô

Há indicações, nas fontes de 2026, de que a adoção estagnou em vez de continuar subindo, e
não só por bloqueio: acima de certa banda, a vantagem do QUIC sobre TCP+TLS1.3 diminui, e o
custo de CPU em espaço de usuário passa a pesar. Isso é matéria de debate ativo, e este
material o registra como **debate**, não como conclusão.

---

## 3. IPv6 passou de 50 % — e isso muda a varredura

**Em 28 de março de 2026, as estatísticas do Google registraram 50,10 % de acesso nativo por
IPv6 pela primeira vez** — contra 46,33 % um ano antes, e ~30 % em janeiro de 2020.

*(Fontes: [ISOC Pulse](https://pulse.internetsociety.org/en/blog/2026/04/18-years-later-ipv6-reaches-majority/),
[APNIC Blog](https://blog.apnic.net/2026/04/28/google-hits-50-ipv6/),
[Google IPv6 statistics](https://www.google.com/intl/en/ipv6/statistics.html). Consultado em 14/08/2026.)*

**A consequência para portas e varredura é qualitativa, não gradual:**

- **Varredura exaustiva morreu no IPv6.** Uma `/64` tem 1,8 × 10¹⁹ endereços; a 10 milhões
  de sondas por segundo, seriam ~58 mil anos. A conta está no
  [`60-teoria-avancada.md`](60-teoria-avancada.md).
- **A descoberta virou coleta.** DNS, Certificate Transparency, *hitlists*, endereços
  previsíveis (`::1`, `::80`, EUI-64), tráfego observado passivamente.
- **A obscuridade recuperou algum valor real** — pela primeira vez desde 2013. Um serviço
  num endereço IPv6 aleatório de uma `/64`, sem DNS, é genuinamente difícil de achar.
  É uma das poucas afirmações deste curso que dá defesa técnica a "segurança por
  obscuridade", e ainda assim: **como camada adicional, jamais como controle único**.
- **E o risco espelhado:** muita gente configurou firewall só para IPv4. Se a máquina tem
  IPv6 e as regras não, o serviço está exposto por um caminho que ninguém audita.

```bash
ss -tulpn | grep -E '\[::\]|\[::1\]'      # o que você expõe em IPv6
sudo ip6tables -L -n -v                   # as regras IPv6 existem?
sudo nft list ruleset | grep -i ip6
```

⚠️ **Rode esses três comandos hoje.** Firewall só-IPv4 numa máquina com IPv6 ativo é uma
das exposições mais comuns e menos notadas de 2026.

---

## 4. eBPF — a nova camada de observação e controle

O eBPF permite executar programas verificados **dentro do kernel**, em pontos de gancho
específicos, sem módulos e sem reinicializar.

Em 2026 ele deixou de ser tecnologia emergente e virou substrato de infraestrutura.
Números divulgados em relatórios do setor: a **Datadog** reporta redução de ~35 % de CPU
com um rastreador de conexões baseado em eBPF; a **Meta** reporta até 20 % de redução de
ciclos com o profiler Strobelight.

*(Fontes: [eBPF Foundation](https://ebpf.foundation/new-ebpf-in-production-report-showcases-production-enterprise-outcomes-across-networking-security-and-observability/)
e compilações do setor consultadas em 14/08/2026. São números divulgados pelos próprios
fornecedores — leia como ordem de grandeza, não como medição independente.)*

### O que muda para o nosso assunto

| Antes | Com eBPF |
|---|---|
| `ss` mostra uma fotografia | `bpftrace` mostra **cada** `bind()`/`connect()`, ao vivo |
| Firewall no netfilter | **XDP** filtra no driver, antes do kernel — milhões de pps |
| Balanceamento com iptables | **Cilium/Katran** fazem no eBPF, com muito menos custo |
| Regras por IP e porta | Política por **identidade de serviço**, resolvida no kernel |

```bash
# Ver toda conexão de saída acontecer, ao vivo
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_connect { printf("%s pid=%d\n", comm, pid); }'

# Ferramentas prontas do pacote bpfcc-tools
sudo tcpconnect        # cada connect(), com processo
sudo tcpaccept         # cada accept()
sudo tcplife           # duração e bytes de cada conexão
sudo tcpretrans        # retransmissões, ao vivo
```

**Não executado** neste material (exige root e `bpfcc-tools`, indisponíveis no ambiente de
escrita). Os nomes das ferramentas vêm da documentação do projeto BCC.

**A mudança conceitual:** o `ss` responde *"o que está aberto agora?"*. O eBPF responde
*"quem abriu o quê, quando, e por quanto tempo?"* — a diferença entre um inventário e uma
auditoria contínua.

---

## 5. Zero trust — a porta deixa de ser fronteira

O modelo de perímetro ("dentro é confiável, fora não é") morreu por razões práticas:
trabalho remoto, nuvem, SaaS, containers efêmeros.

O que substitui:

| Perímetro | Zero trust |
|---|---|
| Firewall na borda | Política em **cada** serviço |
| Confiança por localização de rede | Confiança por **identidade verificada** |
| VPN dá acesso à rede toda | Acesso por aplicação, por sessão |
| ACL por `(IP, porta)` | mTLS com identidade SPIFFE/SPIRE |

Na prática, com service mesh, a autorização vira:

```yaml
# "o serviço 'frontend' pode chamar 'api' no método GET"
# — sem mencionar IP nem porta em lugar nenhum
```

**A porta continua existindo** (o transporte precisa dela), mas deixou de ser o mecanismo
de controle. Uma varredura de portas dentro de um cluster com mesh mostra o mesmo conjunto
de portas em todo Pod — 15000, 15001, 15006, 15020 do Envoy — e diz quase nada.

### O que isso não resolve

Vale ser cético onde o marketing não é. Zero trust:

- **não** elimina a necessidade de inventário — você ainda precisa saber o que existe;
- **não** protege contra serviço exposto por engano fora da malha;
- **é** operacionalmente caro, e implementações parciais podem ser piores que um perímetro
  bem-feito, porque criam falsa sensação de cobertura.

**Opinião profissional, declarada:** para a maioria das organizações, um inventário de
portas correto e um firewall bem mantido entregam mais redução de risco por real investido
do que uma implantação parcial de zero trust. As duas coisas não competem, mas a ordem
importa.

---

## 6. Varredura em 2026 — quem varre você

| Ator | O que faz |
|---|---|
| **Shodan, Censys, ZoomEye** | Varrem a internet continuamente e vendem o índice |
| Grupos de pesquisa (Michigan, Max Planck) | Varredura acadêmica, dados publicados |
| **Atacantes automatizados** | Varrem e exploram na mesma passada, em minutos |
| Provedores de nuvem | Varrem os próprios clientes e notificam exposição |
| Seguradoras cibernéticas | Varrem para precificar apólices ⚠️ |

**Uma porta exposta é encontrada em minutos.** Não em dias. Isso é verdade desde o ZMap e o
masscan, em 2013, e não há sinal de reversão.

O item das seguradoras é a novidade da década: sua superfície exposta hoje tem **preço
diretamente atribuído**. Um `ss -tulpn` mal cuidado virou uma linha de custo — o que, na
prática, foi o que finalmente fez algumas diretorias prestarem atenção.

### Ferramentas: o estado atual

| Ferramenta | Situação em 2026 |
|---|---|
| **Nmap** | 7.991 é a atual (7.99 saiu em 26/03/2026). Continua o padrão de precisão |
| **masscan** | Continua o rei da escala bruta |
| **RustScan** | v2.4.1 em comparativos recentes. Acha rápido e entrega ao Nmap |
| **naabu** | v2.3.4. Integra com o ecossistema ProjectDiscovery (`nuclei` etc.) |
| **ZMap** | Padrão da pesquisa acadêmica |

*(Versões pesquisadas na web em 14/08/2026.)*

O padrão de uso convergiu: **descoberta rápida com uma ferramenta sem estado, seguida de
verificação precisa com Nmap.** É o que o RustScan automatiza, e é o fluxo que qualquer
profissional usa manualmente.

---

## 7. Onde a IA entra (e onde não entra)

Sendo honesto sobre o que é real e o que é vendido:

**Real, e em produção:**
- Classificação de tráfego cifrado por características estatísticas (tamanho, ritmo,
  direção) sem descriptografar — funciona razoavelmente para dizer *que tipo* de tráfego é.
- Detecção de anomalia em inventário: "esta máquina abriu uma porta que nunca teve".
- Assistentes que traduzem intenção em regra de firewall e explicam saídas de varredura.

**Exagerado, e vale ceticismo:**
- "IA que descobre vulnerabilidades zero-day varrendo portas" — varredura de porta produz
  informação limitada; nenhum modelo extrai o que não está no canal.
- Classificação de tráfego cifrado com precisão altíssima em ambiente aberto — os números
  publicados costumam vir de conjuntos de dados fechados e não se sustentam em produção.

**A mudança que efetivamente aconteceu:** o custo de escrever ferramenta de rede caiu muito.
O [projeto-modelo](07-projeto-modelo/README.md) deste curso — um auditor completo com
41 testes — é hoje trabalho de horas, não de semanas. Isso vale igualmente para quem
constrói defesa e para quem constrói ataque, e a assimetria continua favorecendo o lado que
só precisa achar **uma** porta.

---

## 8. O que reavaliar, e quando

| Item | Reavaliar |
|---|---|
| Adoção de HTTP/3 e a estagnação | a cada 6 meses |
| IPv6 e o que ela faz com varredura | a cada 6 meses |
| Versões de ferramentas | a cada ano |
| eBPF e ferramental derivado | a cada 6 meses |
| Preços de Shodan/Censys ([`80`](80-custos-e-licencas.md)) | a cada 6 meses |
| Cursos ([`85`](85-cursos-e-certificacoes.md)) | a cada ano |
| Fundamentos (`10` a `16`) | **quase nunca** — TCP não muda |

**A observação que fecha o arquivo:** os arquivos `10` a `16` deste curso descrevem coisas
estabelecidas em 1981 e válidas em 2026. O `65` que você está lendo estará parcialmente
errado em 2027. Invista seu tempo de estudo na proporção inversa da velocidade de mudança.

---

## Fontes consultadas em 14/08/2026

- [ISOC Pulse — "18 Years Later, IPv6 Reaches Majority"](https://pulse.internetsociety.org/en/blog/2026/04/18-years-later-ipv6-reaches-majority/)
- [APNIC Blog — "Google hits 50% IPv6"](https://blog.apnic.net/2026/04/28/google-hits-50-ipv6/)
- [Google IPv6 statistics](https://www.google.com/intl/en/ipv6/statistics.html)
- [eBPF Foundation — "eBPF In Production" report](https://ebpf.foundation/new-ebpf-in-production-report-showcases-production-enterprise-outcomes-across-networking-security-and-observability/)
- [Nmap Change Log](https://nmap.org/changelog.html)
- [IANA — Service Name and Transport Protocol Port Number Registry](https://www.iana.org/assignments/service-names-port-numbers)
- Compilações de adoção de HTTP/3 (W3Techs, Cloudflare, TechnologyChecker), consultadas via busca em 14/08/2026.

---

## Autoteste

1. Enuncie a tese central deste arquivo e dê um exemplo concreto de cada uma das três
   funções da porta migrando para outro lugar.
2. Por que "a porta 443 está aberta" deixou de ser informação de segurança útil? O que
   sobrou como defesa?
3. Três fontes reportam adoção de HTTP/3 em 39 %, 35 % e 21 %. Explique a divergência.
4. Qual comando testa se a **sua** rede permite HTTP/3, e como interpretar a saída?
5. Por que o IPv6 passar de 50 % muda **qualitativamente** a varredura? Que consequência
   isso tem para o valor da obscuridade?
6. Cite a exposição mais comum e menos notada de 2026 relacionada a IPv6, e os comandos que
   a detectam.
7. Qual é a diferença de natureza entre o que o `ss` responde e o que o eBPF responde?
8. Em que zero trust melhora a segurança de portas, e em que ele **não** ajuda? Dê sua
   opinião sobre prioridade, com justificativa.
9. Por que uma seguradora cibernética varre seus clientes, e o que isso mudou na prática?
10. Quais arquivos deste curso envelhecem rápido e quais quase não envelhecem? O que isso
    sugere sobre onde investir tempo de estudo?

---

*Próximo: [`70-pratica.md`](70-pratica.md) — 14 laboratórios.*
