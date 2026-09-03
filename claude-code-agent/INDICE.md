# Índice de Assuntos

Repositório de aprendizado profundo. Cada assunto vive em sua própria subpasta,
com curso completo do zero absoluto ao nível de pesquisa.

Comece qualquer assunto pelo arquivo `00-MAPA.md` da respectiva subpasta.
As regras de produção do material estão em [`CLAUDE.md`](CLAUDE.md).

---

## Estrutura que todo assunto deve ter

| Bloco | Faixa | Contém |
|---|---|---|
| **A · Porta de entrada** | 01–09 | introdução para leigos, pré-requisitos, **manual de instalação passo a passo**, como começar, manual de uso, exemplos, projeto-modelo executável |
| **B · Núcleo** | 10–69 | fundamentos → história → mecânica interna → teoria avançada → estado da arte |
| **C · Prática e erros** | 70–79 | laboratórios, exercícios, armadilhas e mitos |
| **D · Economia e ecossistema** | 80–89 | custos, licenças, cursos gratuitos (PT/EN/FR), certificações |
| **E · Fontes** | 90–99 | bibliografia comentada, referências, specs, papers |
| **—** | — | `GLOSSARIO.md` |

Legenda de status: ✅ completo · 🟡 parcial · ⬜ pendente

---

## Assuntos cobertos

### [jwt](jwt/00-MAPA.md)
O que é um JSON Web Token, como se usa, como funciona por dentro — e **quando não usar**.
Da analogia da pulseira de parque ao ML-DSA pós-quântico. Anatomia byte a byte, a criptografia
de HMAC/ECDSA/EdDSA do zero, claims com semântica exata, JWKS e rotação de chave sem downtime,
ciclo de vida da sessão com rotação de refresh e detecção de reuso, onde guardar o token no
cliente, OAuth 2.0 e OIDC, ataques e defesas com as CVEs de 2026, operação em produção,
e um arquivo inteiro argumentando que, para a maioria dos sistemas, um cookie de sessão comum
é a escolha certa.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 29 documentos + projeto-modelo executável, ~12.900 linhas. Bloco A completo
  (instalação por SO cobrindo Node/Python/Java/Go/OpenSSL/`jwt-cli`/Docker, com PATH,
  permissões, proxy corporativo, desinstalação e 13 erros literais; 14 exemplos completos em
  cinco linguagens, incluindo dois casos de produção). Núcleo do 10 ao 65 (fundamentos →
  história → anatomia byte a byte → claims → assinatura JWS → JWE → chaves e rotação →
  ciclo de vida da sessão → armazenamento no cliente → OAuth/OIDC → ataques → **quando não
  usar** → operação → teoria avançada → estado da arte de ago/2026). 12 laboratórios,
  25 armadilhas + 12 mitos, custos com data e câmbio, cursos PT/EN/FR pesquisados na web,
  bibliografia com edições conferidas, ~130 termos no glossário.
- **Projeto-modelo:** `07-projeto-modelo/` — API de notas (`cofre-de-notas`) com **JWS
  implementado do zero sobre `node:crypto`, zero dependências**: ES256 com `kid` por
  thumbprint RFC 7638, refresh opaco com rotação e detecção de reuso, lista de negação por
  `jti`, logout que mata as duas credenciais, JWKS público, CLI de rotação de chave.
  **54 testes — metade deles são ataques** (`alg:none` e variações de caixa, confusão
  RS256→HS256, `kid` com travessia de caminho, `crit` desconhecido, token de outra audiência).
- **Verificação:** 54/54 testes executados e aprovados (Node v24.18.0). Fluxo completo
  exercitado com `curl` real: registrar → login → rota protegida → refresh → reuso detectado →
  logout → token revogado; rotação de chave executada pela CLI. O teste de thumbprint
  **reproduz o vetor oficial da RFC 7638**. Exemplos com `jose` 6.2.8 e PyJWT 2.13.0
  executados. Versões, CVEs de 2026, preços e cursos pesquisados na web em 14/08/2026.
- **Base:** Node v24.18.0 · Python 3.10.12 · OpenSSL 3.0.2 · OpenJDK 17.0.19 · Docker 29.1.3 ·
  Ubuntu 22.04.5 · `jose` 6.2.8 · PyJWT 2.13.0 · RFC 9901 (SD-JWT) · RFC 9964 (ML-DSA).
- **Pendente:** nada de estrutura. Reavaliar `65-estado-da-arte.md` e `80-custos-e-licencas.md`
  a cada seis meses; `03-instalacao.md` a cada CVE relevante de biblioteca JWT.
- *Última atualização: 14/08/2026*

---

### [portas-de-rede](portas-de-rede/00-MAPA.md)
Como se verificam as portas de uma máquina, quais são elas, para que servem, quais os
protocolos, e como testá-las e descobri-las. Da caixa postal numerada à quádrupla, aos 12
estados do TCP, ao `/proc/net/tcp` decodificado à mão. **As duas visões** (de dentro com `ss`,
de fora com `nmap`) e o que cada divergência entre elas significa. Catálogo de ~120 portas com
risco, incluindo automação industrial. Firewall, NAT, CGNAT, containers e Kubernetes.
Do leigo total ao teorema de Rice e ao esgotamento de porta efêmera.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 27 documentos + projeto-modelo executável, ~12.000 linhas. Bloco A completo
  (instalação de **todo o conjunto** — `ss`, `lsof`, `nmap`, `netcat`, `socat`, `tcpdump`,
  Wireshark, PowerShell, WSL2 — nos três SOs, com PATH, permissões sem `sudo`, proxy,
  desinstalação, 13 erros literais e alternativa sem instalar nada; **manual de uso por tarefa**
  com filtros de kernel do `ss`; 15 exemplos). Núcleo do 10 ao 65 (fundamentos → história →
  camadas → **TCP por dentro** → **UDP/ICMP/SCTP/QUIC** → **sockets e o kernel** →
  **catálogo de portas** → **descoberta e varredura** → firewall/NAT → exposição →
  containers/k8s → teoria avançada → estado da arte de ago/2026). 14 laboratórios,
  30 armadilhas + 9 mitos, custos e licenças com data, cursos PT/EN/FR pesquisados na web,
  RFCs desde 1971, glossário com ~140 termos.
- **Projeto-modelo:** `07-projeto-modelo/` — **auditor de portas** em Python puro (zero
  dependências) com três subcomandos: `local` reimplementa o `ss` lendo `/proc/net/{tcp,udp}`
  e resolvendo i-node→PID; `varrer` faz varredura TCP concorrente com banner e **guarda de
  autorização** (recusa alvo não privado sem `--autorizado`); `comparar` confronta as duas
  visões. Catálogo de ~70 portas com julgamento de risco por **(porta, escopo)**, saída JSON e
  código de saída para CI. Mais um alvo de laboratório com gabarito. **41 testes, executados
  e passando.**
- **Achado real durante a escrita:** o `nmap` reportou **25 portas abertas** em `127.0.0.1`
  onde o `ss` confirmava **8** — conexões completam sem nenhum processo escutando. Investigado,
  reproduzido à mão, e **declarado como não confirmado** (faltou `sudo` para ler
  `iptables -t nat`). Virou o caso didático central do assunto: *"a porta está aberta" é uma
  afirmação sobre o caminho inteiro, não sobre um processo.*
- **Verificação:** saídas reais desta máquina (Ubuntu 22.04.5, kernel 6.8.0-136,
  iproute2 5.15.0, nmap 7.80, Python 3.10.12). Foram **medidos**: `TIME_WAIT` com e sem
  `SO_REUSEADDR`; `listen(2)` aceitando **3** conexões (`backlog+1`) com `Recv-Q 3 / Send-Q 2`;
  `ECONNREFUSED` em socket **UDP** via ICMP; as quatro mensagens de erro clássicas, literais;
  banners reais de Apache 2.4.52 e MySQL 8.0.46 (que entrega a versão **antes** da
  autenticação); faixa efêmera `32768-60999`; `/proc/net/tcp` decodificado e conferido contra
  o `ss`. Versões, IANA, adoção de HTTP/3 e IPv6, preços e cursos pesquisados na web em
  14/08/2026.
- **Não executado (declarado no material):** macOS e Windows; `nmap -sS`/`-sU`/`-O`,
  `tcpdump` e eBPF (exigem root, ausente); regras de `iptables`/`nft`; Docker e Kubernetes;
  varredura de alvo externo (por escolha).
- **Pendente:** nada de estrutura. Reavaliar `65-estado-da-arte.md` a cada 6 meses (QUIC e
  IPv6 mudam rápido); `80`/`03` a cada 6 meses; `85` a cada ano. Os arquivos `10` a `16`
  descrevem coisas de 1981 e quase não envelhecem.
- *Última atualização: 14/08/2026*

---

### [tabela-arp](tabela-arp/00-MAPA.md)
O que é a tabela ARP: a lista IP→MAC que cada máquina mantém para entregar pacotes no próprio
segmento, e o protocolo de 1982 que a preenche. Do "caderninho do porteiro" ao pacote byte a
byte, à máquina de estados NUD, ARP spoofing e DAI, VLAN/Wi-Fi/VRRP/Docker/Kubernetes/nuvem,
o NDP do IPv6, e a teoria (carga de broadcast Θ(N²), o trilema seguro/sem-estado/sem-infra,
teorema de Rice). Estado da arte de ago/2026: EVPN ARP suppression, eBPF.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 27 documentos + projeto-modelo executável. Bloco A completo (instalação por SO com
  ferramentas de leitura/captura/varredura, Scapy, lab isolado em VM/Docker/namespaces, PATH,
  captura sem root via `setcap`, proxy, desinstalação e tabela de erros literais; 14 exemplos).
  Núcleo do 10 ao 65 (fundamentos → história → **pacote byte a byte** → ciclo de resolução →
  **máquina de estados NUD e coletor de lixo** → variações (gratuitous/proxy/RARP/InARP) →
  ARP em cada SO → redes reais → **segurança/spoofing/DAI** → diagnóstico → **NDP/IPv6** →
  teoria avançada → estado da arte). 12 laboratórios, armadilhas + 8 mitos, custos com licenças,
  cursos PT/EN/FR pesquisados na web, RFCs e código do kernel, glossário com ~70 termos.
- **Projeto-modelo:** `07-projeto-modelo/` — `arpinspect`, inspetor da tabela sem dependências:
  lê `ip -j neigh`/`arp -a`, identifica fabricante por OUI (base IEEE do nmap), detecta IP com
  MACs diferentes (spoofing), MAC servindo vários IPs, MAC local-administrado e entradas mortas;
  saída humana/JSON e modo `--check` para CI. **19 testes, executados e passando.**
- **Verificação:** saídas reais desta máquina (Ubuntu 22.04.5, kernel 6.8.0-136, iproute2
  5.15.0); transições `STALE→DELAY→REACHABLE→STALE` e `INCOMPLETE→FAILED` **medidas segundo a
  segundo**; `arpinspect` rodado contra a tabela real e o arquivo de spoofing (19/19 verdes);
  erros reais de `flush`/captura sem root reproduzidos. MACs tiveram os 3 últimos octetos
  mascarados por privacidade da rede (OUI real preservado). Versões, EVPN, cursos e RFC 826
  pesquisados na web em 14/08/2026.
- **Não executado (declarado):** comandos macOS/Windows/Cisco; captura (`tcpdump`/Wireshark) e
  varredura (`arp-scan`/`arping`) — exigem root, ausente no ambiente; labs de ataque (lab isolado).
- **Pendente:** nada de estrutura. Reavaliar `65-estado-da-arte.md` e `03-instalacao.md` a cada
  6 meses; `80`/`85` a cada ano.
- *Última atualização: 14/08/2026*

---

### [portas-logicas](portas-logicas/00-MAPA.md)
As peças com que todo computador é feito: o que é uma porta lógica, **quantas existem e para
que servem**, como um transistor vira porta, como portas viram somador, memória e CPU, e onde
exatamente as portas de um chip real são gastas. Do interruptor de luz ao argumento de
contagem de Shannon e ao limite de Landauer.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 22 documentos + projeto-modelo executável, ~10.500 linhas. Bloco A completo
  (instalação de 5 tecnologias nos três SOs, com versões testadas, PATH, permissões, proxy,
  desinstalação, tabela de erros literais e a alternativa **sem instalar nada**; manual de
  referência com as 7 portas, as 16 funções, identidades booleanas, série 7400, operadores
  Verilog e atalhos do Logisim; **12 exemplos completos**). Núcleo do 10 ao 65 (álgebra
  booleana e completude funcional → história de Boole a 2026 → CMOS transistor a transistor →
  combinacionais → sequenciais, timing e metaestabilidade → da porta ao processador RISC-V →
  **a resposta longa à pergunta que originou o assunto** → complexidade de circuitos, AC⁰,
  provas naturais, Landauer e lógica reversível → estado da arte de ago/2026: N2/18A, GAA,
  backside power, CFET, silício aberto, quântica). 12 laboratórios, 20 armadilhas + 8 mitos,
  custos com data e câmbio, cursos PT/EN/FR pesquisados na web, bibliografia com edições
  verificadas, ~140 termos no glossário.
- **A resposta em uma linha:** **7 tipos** clássicos de porta (16 funções possíveis de 2
  entradas; centenas de células numa biblioteca industrial) e, num notebook de 2026,
  **~2,5 a 5 bilhões de unidades** — sendo ~20% dos transistores memória, que não é porta.
  Servem para seis coisas: decidir, calcular, escolher, endereçar, lembrar e vigiar.
- **Projeto-modelo:** `07-projeto-modelo/` — **um computador de 4 bits construído
  exclusivamente com portas NAND**, em Python puro sem dependências: ULA de 8 operações,
  registradores, RAM, contador de programa, decodificador 4→16, 13 instruções, e um
  **contador de portas** que responde à pergunta do curso com número medido.
- **Verificação:** **executado em 14/08/2026** (Python 3.10.12, Ubuntu 22.04.5). Suíte com
  **76 testes, 76 aprovados** (vários exaustivos, cobrindo todas as 256 entradas de somador,
  subtrator, ULA e comparador). O computador multiplica 3×5 em 46 instruções e 39.678
  avaliações de NAND. Censo estrutural: **829 portas** — a mesma ordem de grandeza do Intel
  4004 de 1971. Exemplos em Python conferidos um a um; **os exemplos em Verilog não puderam
  ser compilados** no ambiente de escrita (sem Icarus Verilog e sem permissão para instalar),
  o que está declarado no topo do `06-exemplos.md`.
- **Base:** Logisim-evolution 4.1.0 (15/02/2026) · Digital 0.31 · Icarus Verilog 13.0 ·
  contagens de transistores da Wikipédia e panorama de fabricação pesquisados em 14/08/2026.
- **Pendente:** nada de estrutura. Reavaliar `65-estado-da-arte.md` e `80-custos-e-licencas.md`
  a cada ~12 meses.
- *Última atualização: 14/08/2026*

---

### [power-bi](power-bi/00-MAPA.md)
A plataforma de BI da Microsoft: o que é, como funciona por dentro, como se trabalha com ela
e o que ela pode (e não pode) fazer. Do "imagine uma cozinha" ao limite de Shannon.
Instalação por SO (inclusive os contornos para macOS e Linux, onde o Desktop **não** roda),
Power Query e *query folding*, **modelagem dimensional**, DAX até o contexto de avaliação,
VertiPaq e desempenho medido, modos de armazenamento, serviço, RLS e governança,
PBIP/TMDL com Git e CI, Fabric — e um capítulo franco sobre **quando não usar Power BI**.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 34 documentos + projeto-modelo executável, ~18.000 linhas. Bloco A completo
  (instalação por SO com Store/exe/winget/MSI, WebView2, gateway, ferramentas externas,
  PATH, permissões sem admin, proxy e certificado interno, convivência de versões,
  desinstalação completa e **12 erros literais**; manual de uso consultável por tarefa;
  **15 exemplos completos**, dois deles casos reais — carga incremental de 400 milhões de
  linhas e OEE de planta industrial). Núcleo do 10 ao 65 (fundamentos → história →
  arquitetura → Power Query/M → **modelagem dimensional** → DAX → **contexto de avaliação**
  → inteligência de tempo → visualização → interatividade → modos de armazenamento →
  **VertiPaq por dentro** → desempenho → serviço → segurança → DevOps → Fabric →
  **alternativas** → teoria avançada → estado da arte de ago/2026). 14 laboratórios com
  critério de aceite, **32 armadilhas + 10 mitos**, custos com data e câmbio, cursos
  PT/EN/FR pesquisados na web, bibliografia sem ISBN inventado, ~200 termos no glossário.
- **Projeto-modelo:** `07-projeto-modelo/` — distribuidora de tintas industriais
  ("Tintas Aurora"), 60.621 linhas de fato, **duas tabelas de fato em granularidades
  diferentes** ligadas pela ponte `dMes`, RLS com três escopos que **falha fechada**, e
  **8 defeitos plantados de propósito** (CNPJ duplicado, devolução com sinal trocado,
  desconto em escala errada, produto sem cadastro, data com século errado, preço zero,
  meta faltando, UF suja). Modelo inteiro em **TMDL versionável** + 43 medidas comentadas
  em `.dax`. **Gerador e validador executados e verificados.**
- **Verificação:** `gerar_dados.py` executado (1,4 s, 7 CSVs, 4,12 MB) e `validar.py`
  executado (**25 verificações estruturais ok, 8 defeitos localizados, 0 falhas, saída 0**).
  Os números do gabarito são a saída real do programa: faturamento tratado
  R$ 167.700.759,11 contra R$ 169.361.358,06 do cálculo ingênuo — **os defeitos inflam o
  número em 0,99%**. O validador também confere a consistência entre os `.tmdl` e os
  cabeçalhos dos CSVs (8 tabelas, 8 relacionamentos). Todos os links internos verificados.
- **Base:** Power BI Desktop de julho/2026 · Python 3.10.12 · Ubuntu 22.04.5 · preços,
  cursos, certificação e estado da arte pesquisados na web em 14/08/2026 (Pro US$ 14,
  PPU US$ 24, F64 ≈ US$ 8.410/mês, PL-300 com renovação anual gratuita, **DAX UDF em GA
  desde junho/2026**, org apps com audiências em GA desde julho/2026).
- **Não executado (declarado em cada arquivo):** tudo o que exige o Power BI Desktop —
  ele **não roda em Linux**, que é o ambiente de escrita. Isso inclui abrir o modelo TMDL,
  as telas do `04`, os 14 laboratórios e a publicação no Service. Onde há uma tela ou
  saída que não vi, o texto diz *"esperado"*; os tempos de otimização do `22` e os
  tamanhos do `21` estão marcados como **ilustrativos**.
- **Pendente:** nada de estrutura. Reavaliar `65-estado-da-arte.md` e `05-manual-de-uso.md`
  a cada 3 meses (o produto tem cadência mensal); `80-custos-e-licencas.md` a cada 6 meses;
  `03-instalacao.md` e `85-cursos-e-certificacoes.md` a cada ano.
- *Última atualização: 14/08/2026*

---

### [optimistic-locking](optimistic-locking/00-MAPA.md)
Controle de concorrência otimista: como dois usuários editam o mesmo dado sem que um apague o
trabalho do outro, **sem travar nada e sem ninguém esperar**. Do *lost update* explicado com
uma ficha de papel à teoria de serializabilidade, passando por coluna de versão, `ETag`/`If-Match`,
retentativa com jitter, ORMs (JPA, EF Core, ActiveRecord, Django), MVCC e isolamento,
sistemas distribuídos (CAS, leases, fencing tokens, CRDTs) e a UX do conflito.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 27 documentos + projeto-modelo executável. Bloco A completo (instalação por SO de
  Node/Docker/PostgreSQL/JDK/Python/.NET com PATH, permissões, proxy, desinstalação, tabela de
  erros literais e alternativa sem instalar nada; manual de referência por tarefa; **14 exemplos**,
  5 deles executados e verificados). Núcleo do 10 ao 65 (fundamentos e write skew → história de
  1976 a 2026 → anatomia do bug → tokens de versão e problema ABA → otimista vs. pessimista com
  as fórmulas de custo → isolamento, MVCC e SSI → ORMs → HTTP e projeto de API → sistemas
  distribuídos → retentativa e idempotência → UX do conflito → teoria da serializabilidade e
  5 limites teóricos → estado da arte de ago/2026). 12 laboratórios, 28 armadilhas + 9 mitos,
  custos com data e câmbio, cursos PT/EN/FR pesquisados na web, 18 papers, glossário com ~90 termos.
- **Projeto-modelo:** `07-projeto-modelo/` — **Catálogo Otimista**, API de produtos em Node com
  **zero dependências** (SQLite embutido, HTTP nativo, `node:test`). Tem os **dois caminhos
  ligados de propósito** — protegido e inseguro — e um script que roda a mesma carga nos dois:
  no modo inseguro **10 de 20 edições desaparecem sem erro nenhum**; no modo seguro, zero perdas
  ao custo de 3,35 escritas por edição. **Executado e verificado.**
- **Verificação:** `npm test` → **21/21 aprovados**, incluindo uma corrida real com 20 clientes
  HTTP concorrentes disputando a mesma linha; as duas demonstrações executadas; sequência de
  `curl` com `200`/`412`/`428`/`400` exercitada contra o servidor real; exemplos 5, 6 e 7 rodados
  com saída transcrita. Preços, cursos, papers e panorama pesquisados na web em 14/08/2026.
- **Base:** Node v24.18.0 · Ubuntu 22.04.5 LTS · PostgreSQL 18.6 · RFC 9110 · Kung & Robinson (1981).
- **Pendente:** nada de estrutura. Reavaliar `65-estado-da-arte.md` em fev/2027 (ou quando o
  PostgreSQL 19 sair do beta); reconferir preços, links de cursos e versões de instalação a
  cada 6 meses.
- *Última atualização: 14/08/2026*

---

### [claude-code](claude-code/00-MAPA.md)
O agente de programação de linha de comando da Anthropic: o que é um agente (laço agêntico,
contexto, ferramentas), **todos os comandos** (CLI, barra, atalhos, ferramentas), e o que
separa quem tira 10× de quem tira 1,2×. Instalação por SO, engenharia de contexto, permissões,
hooks, skills, subagentes, MCP, plugins, headless/CI, segurança, custos reais e escala em time.
Do leigo total à atenção quadrática e ao teorema de Rice.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 30 documentos + projeto-modelo executável. Bloco A completo (instalação por SO
  com instalador nativo/apt/dnf/apk/Homebrew/WinGet/npm/Docker, verificação de assinatura GPG,
  PATH, permissões, proxy, desinstalação, tabela de erros literais e alternativa sem instalar
  nada; **manual de referência com todos os comandos de barra, flags de CLI, atalhos e
  ferramentas**; 14 exemplos). Núcleo do 10 ao 65 (fundamentos → história → anatomia da sessão
  → contexto e memória → ferramentas → permissões → configuração → hooks → skills → subagentes
  → MCP → plugins → git/GitHub/CI → headless e SDK → segurança → **o ofício do profissional**
  → times e escala → teoria avançada → estado da arte de ago/2026). 12 laboratórios,
  28 armadilhas + 9 mitos, custos com data e câmbio, cursos PT/EN/FR pesquisados na web,
  bibliografia e ~10 papers, glossário com ~150 termos.
- **Projeto-modelo:** `07-projeto-modelo/` — API de tarefas em Node (zero dependências,
  20 testes) **acompanhada de um `.claude/` completo**: 3 hooks (bloqueio de segredos,
  suíte após edição, contexto na abertura), subagente revisor sem poder de edição, 2 skills
  (uma com `context: fork`), comando no formato antigo, regra com `paths:`, política de
  permissões, e um **script que valida a própria configuração** (17 verificações).
  **Executado e verificado.**
- **Verificação:** `claude --version` → 2.1.231. Suíte 20/20; validador 17 ok / 0 problemas;
  os três hooks testados com JSON de evento simulado, inclusive o caminho de falha
  (`exit 2` devolvendo `'baixa' !== 'media'` ao agente); API exercitada com `curl` real;
  `claude -p` e `--output-format json` executados, com custo real medido (US$ 0,19 e
  47.811 tokens de leitura de cache). Preços, cursos e panorama pesquisados na web em 13/08/2026.
- **Base:** Claude Code 2.1.231 · Node v24.18.0 · Ubuntu 22.04.5 · documentação oficial de
  code.claude.com consultada em 13/08/2026 · preços de claude.com/pricing e platform.claude.com.
- **Não executado (declarado no material):** instalação em macOS e Windows; `Dockerfile` do
  `03`; exemplos 6, 7 e 14 do `06`; esqueleto de servidor MCP do `20`; Agent SDK;
  os 12 laboratórios do `70`; o roteiro interativo do projeto-modelo.
- **Pendente:** nada de estrutura. Reavaliar `05-manual-de-uso.md` e `65-estado-da-arte.md`
  a cada 3–4 meses (a superfície muda várias vezes por semana); `80` a cada 6 meses;
  `85` a cada ano.
- *Última atualização: 13/08/2026*

---

### [commits-assinados](commits-assinados/00-MAPA.md)
Como configurar commits assinados por **GPG ou SSH no GitHub**, passo a passo — e o que o selo
`Verified` realmente prova. Do "qualquer um pode commitar no seu nome" ao objeto commit por
dentro, `allowed_signers`, rulesets, bots e CI, e daí a EUF-CMA, colisão de SHA-1, logs de
transparência e assinatura pós-quântica.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 26 documentos + laboratório executável, ~7.700 linhas. Bloco A completo
  (instalação de **todo o conjunto** — Git, GnuPG, `gpg-agent`, `pinentry`, OpenSSH, `gh` —
  por SO, com PATH, permissões, proxy, desinstalação e 12 erros literais; **as duas trilhas
  lado a lado** no `04`; 14 exemplos, dois deles casos reais). Núcleo do 10 ao 65
  (fundamentos → história → **anatomia do commit** → GPG a fundo → SSH/SSHSIG a fundo →
  verificação no GitHub → agentes e hardware → automação/CI → política de equipe →
  como escolher → teoria avançada → estado da arte de ago/2026). 12 laboratórios,
  26 armadilhas, custos com data, cursos PT/EN/FR pesquisados, RFCs e papers, glossário com
  ~90 termos.
- **Projeto-modelo:** `07-projeto-modelo/` — laboratório descartável em **15 atos** que gera
  chaves SSH e GPG de brinquedo, assina pelos dois métodos, verifica, e então **quebra a
  verificação de cinco formas** para mostrar cada código de `%G?`. Não toca em `~/.gnupg`,
  `~/.ssh` nem `~/.gitconfig` (usa `GNUPGHOME` e `$TMPDIR` próprios). Inclui script de
  auditoria usável em CI, hook `pre-commit` e workflow do GitHub Actions.
  **Executado e verificado.**
- **Verificação:** todas as saídas mostradas são **reais** — inclusive as falhas. Foram
  medidos na prática os códigos `G`, `B`, `U`, `N`, `Y` e `R`; o payload assinado foi
  reconstruído à mão e verificado **sem o Git**; a estrutura binária SSHSIG foi decodificada
  (173 bytes); confirmou-se que a sintaxe `key::` exige Git ≥ 2.35 e que **o Git não compara
  o assinante com o autor do commit**.
- **Base:** Git 2.34.1 · GnuPG 2.2.27 · OpenSSH 8.9p1 · Ubuntu 22.04.5 LTS. Versões atuais,
  preços, cursos e prazos regulatórios pesquisados na web em 13/08/2026 (Git 2.55.0,
  GnuPG 2.5.21 com a série 2.4 fora de suporte, OpenSSH 10.5, Gpg4win 5.1.0, `gh` 2.97.0).
- **Não executado (declarado no material):** instalação em macOS e Windows; YubiKey e cartão
  OpenPGP; o selo `Verified` na tela do GitHub; o workflow de CI.
- **Pendente:** nada de estrutura. Reavaliar `65-estado-da-arte.md` e
  `80-custos-e-licencas.md` a cada 6 meses; `85-cursos-e-certificacoes.md` a cada ano.
- *Última atualização: 13/08/2026*

---

### [agentes-de-ia](agentes-de-ia/00-MAPA.md)
O que são agentes de IA e como usar o **Claude Code** — do "imagine que você contrata um
cozinheiro" à indecidibilidade de Rice. O laço agêntico linha a linha, projeto de
ferramentas (ACI), contexto e compactação, **MCP por dentro**, subagentes e worktrees,
hooks, permissões e **injeção de prompt**, skills e plugins, construir o próprio agente,
avaliação honesta, e a fronteira de ago/2026. Referência completa de **comandos, flags e
atalhos** do Claude Code 2.1.231.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 24 documentos + projeto-modelo executável. Bloco A completo (instalação por
  SO com todas as tecnologias — Claude Code, Node/nvm, Python/uv, gh, Docker —, PATH,
  permissões, proxy, integridade GPG, desinstalação, tabela de erros literais e alternativa
  sem instalar nada; 12 exemplos, dois deles de produção). Núcleo do 10 ao 65 (fundamentos
  → história → **anatomia do laço** → ferramentas → contexto → MCP → subagentes → hooks e
  segurança → skills → construir o seu → avaliação → teoria → estado da arte).
  14 laboratórios, 30 armadilhas e 9 mitos, custos com data de consulta, cursos PT/EN/FR
  pesquisados na web, ~18 papers, glossário com ~60 termos.
- **Projeto-modelo:** `07-projeto-modelo/` — gerenciador de tarefas exposto a um agente por
  duas vias com o **mesmo domínio**: um servidor MCP escrito à mão (JSON-RPC 2.0, **zero
  dependências**) e um laço agêntico de ~120 linhas. Mais `CLAUDE.md`, `.mcp.json`, hook
  `PostToolUse`, regras de permissão, skill e subagente. **19 testes de contrato,
  executados e passando**, sem rede nem chave de API.
- **Verificação:** `teste_mcp.py` executado (19/19 verdes; a saída no README é a real);
  diálogo JSON-RPC manual conferido; `claude --help` da versão instalada usado como fonte
  do manual de comandos. Preços, cursos, versões e estado da arte pesquisados na web em
  13/08/2026.
- **Base:** Claude Code 2.1.231 · Python 3.10.12 · Node v24.18.0 · Ubuntu 22.04.
- **Não executado (declarado no material):** `agente_minimo.py` (exige chave de API); a
  sessão interativa com MCP/skill/hook/subagente (exige assinatura); os 14 laboratórios;
  instalação em macOS e Windows; os números de benchmark do `65` (compilações públicas).
- **Pendente:** capítulo sobre agentes fora de código; comparativo de frameworks
  (LangGraph, CrewAI, AutoGen, smolagents); segundo projeto-modelo em TypeScript; uso de
  computador.
- *Última atualização: 13/08/2026*

---

### [testes-automatizados](testes-automatizados/00-MAPA.md)
O que são testes automatizados e o que são testes unitários — **em Python e em JavaScript,
lado a lado**. Do primeiro `assert` à indecidibilidade: partição e fronteira, os cinco dublês,
clássica × mockista, TDD, pytest por dentro, `node:test`/Vitest/Jest, integração e E2E,
cobertura e mutação, **testabilidade e projeto de código**, CI, e a fronteira de ago/2026
(geração de teste por LLM, testar código gerado por IA).

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 25 documentos + projeto-modelo **duplo**. Bloco A completo (instalação por SO com
  `uv`/`nvm`, PATH, permissões, proxy, desinstalação, tabela de erros literais e alternativa
  sem instalar nada; 12 exemplos executados). Núcleo do 10 ao 65 (fundamentos → história →
  pirâmide → unidade a fundo → dublês → TDD → pytest → JavaScript → integração/E2E →
  cobertura e mutação → **testabilidade** → CI → teoria avançada → estado da arte).
  12 laboratórios, 26 armadilhas, custos com data, cursos PT/EN/FR pesquisados,
  ~40 papers e docs, glossário com ~130 termos.
- **Projeto-modelo:** `07-projeto-modelo/` — cobrança recorrente de assinaturas, o **mesmo
  domínio implementado duas vezes**. Python: **190 testes**, cobertura 98,7 %, suíte rápida
  em 1,98 s. JavaScript: **245 testes** com `node:test` (zero dependência) + **52** em
  Vitest, 100 % de linha, suíte rápida em 0,29 s. Cobre dinheiro em centavos, tempo
  injetado, gateway HTTP contra servidor real, SQLite, teste de contrato fake × real,
  propriedades com Hypothesis. **Executado e verificado.**
- **Verificação:** todos os exemplos do `06` e as saídas do `04` foram **executados**, e as
  saídas mostradas são as reais. O `19-cobertura-e-metricas.md` traz um **experimento de
  mutação executado** (7 mutantes, 3 sobreviventes, com a lacuna real de cada um analisada).
  As semânticas de igualdade do `17` foram conferidas em Node e Vitest. Versões, preços e
  cursos pesquisados na web em 12–13/08/2026.
- **Base:** pytest 9.1.1 · coverage 7.15.4 · Hypothesis 6.165.3 · Python 3.10.12 ·
  Node v24.18.0 · Vitest 4.1.10 · Jest 30.4.2 · Playwright 1.62.1.
- **Não executado (declarado no material):** instalação em Windows e macOS; Jest 30;
  Playwright; Testcontainers; os 12 laboratórios do `70-pratica.md`.
- **Pendente:** nada de estrutura. Reavaliar `65-estado-da-arte.md` e
  `80-custos-e-licencas.md` a cada 6 meses; `85-cursos-e-certificacoes.md` a cada ano.
- *Última atualização: 13/08/2026*

---

### [ethical-hacking](ethical-hacking/00-MAPA.md)
O que é hacking ético, como se entra na carreira e o passo a passo real. Da regra de ouro
legal (art. 154-A do CP) às cinco fases do pentest, OWASP Top 10:2025, Active Directory,
nuvem, exploração de memória e a fronteira de IA ofensiva. Laboratório completo por SO, plano
de carreira de 24 meses, custos e certificações que valem (e as que não valem).
Do leigo total à indecidibilidade (teorema de Rice).

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 33 documentos + projeto-modelo executável. Bloco A completo (instalação do
  laboratório por SO — Kali 2026.2, VirtualBox/VMware/KVM, alvos, Docker, Burp, isolamento de
  rede — com tabela de erros literais; 14 exemplos, dois deles casos reais de bug bounty e
  pentest interno). Núcleo do 10 ao 65 (fundamentos → história → **ética/lei/contrato** →
  metodologias → recon → varredura → exploração/buffer overflow → pós-exploração → web
  (OWASP 2025) → redes/wireless → Active Directory → nuvem/containers → mobile/hardware →
  engenharia social → **relatório** → **carreira passo a passo** → teoria avançada → estado
  da arte). 12 laboratórios, 25 armadilhas, custos com data, cursos PT/EN/FR pesquisados,
  bibliografia e referências verificadas, glossário com ~170 termos.
- **Projeto-modelo:** `07-projeto-modelo/` — app web vulnerável (Node, zero dependências) com
  5 falhas plantadas mapeadas ao OWASP Top 10:2025 (IDOR, injection, path traversal, auth,
  misconfig), escopo/RoE, roteiro manual, versão corrigida e relatório. Bateria automatizada
  confirma **5/5 na versão vulnerável e 0/5 no retest da corrigida**. **Executado e verificado**
  (Node v24.18.0).
- **Ênfase pedagógica:** ética e legalidade como pré-condição (não como rodapé); o relatório
  como produto; e o caminho de carreira honesto (pentester quase nunca é primeiro emprego).
- **Base:** Kali 2026.2 · Burp 2026.4.x · Metasploit 6.4.131 · OWASP Top 10:2025 · preços,
  cursos e certificações pesquisados na web em 12/08/2026.
- **Pendente:** nada de estrutura. Reavaliar `65-estado-da-arte.md` (IA ofensiva muda rápido) e
  `80`/`85` (preços e certificações) a cada 6 meses.
- *Última atualização: 12/08/2026*

---

### [bert](bert/00-MAPA.md)
O modelo que lê (e não escreve): o que é BERT, por que **não** é um LLM pequeno, como
instalar, afinar, avaliar e servir em produção com latência de milissegundos. Tokenização,
atenção calculada à mão, MLM, embeddings e busca semântica, a família (RoBERTa, DistilBERT,
DeBERTa, ModernBERT, mmBERT, moBERTo), custo real encoder × LLM, e a fronteira de ago/2026.
Do leigo aos limites em `TC⁰` e à pseudo-verossimilhança.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 25 documentos + projeto-modelo executável. Bloco A completo (manual de
  instalação por SO com tabela de erros e comparativo v4 → v5 do `transformers`; 12 exemplos
  com saída real). Núcleo do 10 ao 65 (fundamentos → história → tokenização → arquitetura →
  pré-treino → fine-tuning → embeddings/RAG → família → avaliação → produção →
  BERTologia → teoria avançada → estado da arte). 12 laboratórios, armadilhas, custos com
  data, cursos PT/EN/FR pesquisados, ~45 papers, glossário com ~130 termos.
- **Projeto-modelo:** `07-projeto-modelo/` — triagem de chamados de suporte em português
  com BERTimbau. 180 exemplos rotulados, treino em **60 s de CPU**, F1 macro 0,912,
  API FastAPI com health check (35–43 ms), 11 testes. **Executado e verificado.**
- **Verificação:** ambiente instalado e testado de verdade (`torch` 2.13.0+cpu,
  `transformers` 5.15.0, `datasets` 5.0.1, Python 3.10.12); todos os exemplos dos arquivos
  `04`, `06` e `13` executados, com as saídas reais documentadas — inclusive as que expõem
  falhas do modelo (busca semântica errando "esqueci minha senha"; atalho espúrio em
  "nota fiscal"). API do `transformers` 5 conferida contra o código-fonte.
- **Base:** transformers 5.15.0 · torch 2.13.0 · BERTimbau / ModernBERT · preços,
  cursos e papers pesquisados na web em 12/08/2026.
- **Pendente:** nada de estrutura. Reavaliar `65-estado-da-arte.md` e
  `80-custos-e-licencas.md` a cada 6 meses. Se o **moBERTo** (jun/2026) ganhar adoção,
  promovê-lo a modelo padrão dos exemplos em português.
- *Última atualização: 12/08/2026*

---

### [apis](apis/00-MAPA.md)
O que é uma API, o que é REST de verdade (as 6 restrições de Fielding, HATEOAS, o modelo de
Richardson), quais estilos existem — REST, RPC, gRPC, GraphQL, SOAP, WebSocket, SSE, webhook,
mensageria, MCP — e como escolher entre eles. HTTP por dentro, design, segurança, contratos
OpenAPI, operação e evolução sem quebrar clientes.
Do leigo aos limites teóricos (dois generais, FLP, CAP, subtipagem de contratos).

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 26 documentos + projeto-modelo executável, ~15.400 linhas. Bloco A completo
  (instalação por SO, primeira chamada e primeira API em 40 min, 15 exemplos, referência de
  métodos/status/cabeçalhos). Núcleo do 10 ao 65 (fundamentos → história → HTTP → REST →
  design → estilos → segurança → contratos → operação → **19-como-escolher** → teoria →
  estado da arte de ago/2026). 10 laboratórios, armadilhas, custos, cursos PT/EN/FR,
  bibliografia, referências, glossário (~130 termos + tabela de status).
- **Projeto-modelo:** `07-projeto-modelo/` — API de biblioteca, **zero dependências**.
  Contrato OpenAPI 3.1 escrito à mão, auth por escopo, paginação por cursor, ETag/If-Match,
  Idempotency-Key, rate limit, RFC 9457, log estruturado, desligamento gracioso.
  **50 testes executados e aprovados** (Node v24.18.0).
- **Verificação:** exemplos 2–12 e 15 do `06-exemplos.md` **executados**; saídas documentadas
  são as reais. Três bugs reais encontrados pelos próprios testes durante a escrita
  (roteador, HEAD/RFC 9110, cabeçalhos no 429) e corrigidos. Preços e specs pesquisados na
  web em 11/08/2026 (OpenAPI 3.2.0; 4.0 ainda não existe; HTTP/3 estagnado em ~20–35%).
- **Não executado:** exemplos 13 (GraphQL) e 14 (gRPC) — declarado no arquivo; `Dockerfile`
  do projeto-modelo não foi construído (sem Docker no ambiente de escrita).
- *Última atualização: 11/08/2026*

---

### [sql](sql/00-MAPA.md)
A linguagem: o que é SQL, para que serve e como usar — do primeiro `SELECT` à cota AGM e aos
limites de expressividade. Ordem de execução, junções e **cardinalidade**, agregação, CTEs,
funções de janela, `NULL` e ponto flutuante, **séries temporais de sensor**, modelagem, transações,
índices e desempenho medido, dialetos (7 bancos + PI System), SQL com Python/DuckDB.
Com um bloco inteiro de **aplicações para engenharia química**: balanço de massa, rendimento,
CEP e Cp/Cpk, OEE, racionalização de alarmes, LIMS, manutenção preditiva e energia.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 32 documentos + projeto-modelo executável. Bloco A completo (instalação por SO com
  caminho sem `sudo`, proxy, PATH, desinstalação e tabela de erros literais; **15 exemplos
  executados**, dois deles casos reais — liberação de lote e carga incremental idempotente).
  Núcleo do 10 ao 65 (fundamentos → história → `SELECT` → junções → agregação → CTEs → janelas →
  tipos/`NULL` → séries temporais → DDL/modelagem → DML/transações → índices → views/camada
  semântica → dialetos → Python → **30-engenharia-quimica** → teoria avançada → estado da arte de
  ago/2026). 12 laboratórios com soluções comentadas, 28 armadilhas, custos com data, cursos
  PT/EN/FR pesquisados, ~25 papers e normas ISA, glossário com ~170 termos.
- **Projeto-modelo:** `07-projeto-modelo/` — **historiador de uma planta de resina alquídica em
  batelada**, só com a biblioteca padrão do Python. 8 tabelas `STRICT` + 7 views, 30 dias de
  operação sintética (78 bateladas, 8 instrumentos a 1/min, **344.640 leituras**, 28,6 MB),
  laboratório, alarmes e paradas. **8 defeitos plantados de propósito** — buraco de aquisição,
  sensor travado, qualidade ruim, excursão de temperatura, erro de balanço, espículas de
  instrumento — cada um com a consulta que o acha e o teste que garante. 14 consultas analíticas
  (pivô, *gaps and islands*, CEP/Cpk, OEE, Pareto, correlação, regressão). **31 testes, todos
  passando.**
- **Verificação:** medições reais, não estimadas. Índice: `SCAN` 17,8 ms → `COVERING INDEX` 0,5 ms;
  predicado não-*sargable* 5,0 ms → 0,1 ms (**50×**). Transação: **131,50 s com um `COMMIT` por
  linha contra 0,03 s com uma transação — 4.311×**. DuckDB: CSV 13,3 MB → Parquet 3,3 MB, consulta
  153 ms → 21 ms. As mensagens de erro do `04` e do `03` são literais (inclusive o
  `GLIBC_2.38 not found` do binário oficial do SQLite em Ubuntu 22.04, reproduzido).
- **Ênfase pedagógica:** a cardinalidade de junção como causa nº 1 de número errado
  (`SUM` de 389 t virando 1.536 t, medido); o dado que **não** está lá; e a distinção entre o que
  o SQL calcula e o que faz sentido físico — pH logarítmico, grandezas intensivas, integral de
  vazão sobre lacuna.
- **Base:** SQLite 3.37.2 · Python 3.10.12 · DuckDB 1.5.5 · Ubuntu 22.04.5 · SQL:2023 ·
  preços, cursos e versões pesquisados na web em 13/08/2026.
- **Não executado (declarado no material):** instalação em Windows e macOS; PostgreSQL (sem
  servidor no ambiente de escrita); Docker; os 12 laboratórios como enunciados; consultas ao
  PI System.
- **Pendente:** nada de estrutura. Reavaliar `65-estado-da-arte.md` e `80-custos-e-licencas.md` a
  cada 6 meses; `03-instalacao.md` e `85-cursos-e-certificacoes.md` a cada ano.
- *Última atualização: 13/08/2026*

---

### [postgresql](postgresql/00-MAPA.md)
O banco de dados relacional: o que é e o que é "relacional", SQL do básico ao avançado (JOINs,
janelas, CTEs), modelagem e normalização, tipos ricos (JSONB, arrays, uuidv7), índices, MVCC e
transações, o planejador, arquitetura interna (WAL, processos), extensões (PostGIS, pgvector),
replicação, segurança, administração e custos.
Do leigo à álgebra relacional, ao teorema CAP e aos limites da distribuição.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 28 arquivos + projeto-modelo executável (uma biblioteca: esquema com regras no banco,
  funções PL/pgSQL, app Node com `pg` e testes de integração). Bloco A completo (instalação por SO
  e Docker/nuvem, primeiros passos no psql, manual de uso, 14 exemplos incluindo pgvector). Núcleo
  do 10 ao 65 (fundamentos → SQL → tipos → índices → MVCC → planejador → arquitetura interna →
  extensões → replicação → segurança → administração → teoria avançada → estado da arte de
  ago/2026). 10 laboratórios, armadilhas, custos, cursos PT/EN/FR, certificações, bibliografia,
  referências, glossário (~90 termos).
- **Verificação:** versões/preços/cursos pesquisados na web em 11/08/2026 (PostgreSQL 18). Projeto:
  JS validado e testes pulam corretamente sem banco (5 pulados, 0 falhas); o SQL do esquema não
  pôde ser executado contra um Postgres real no ambiente de escrita — declarado no README do projeto.
- *Última atualização: 11/08/2026*

---

### [docker](docker/00-MAPA.md)
O que é um container e o que é o Docker, como usar (imagens, volumes, redes, Compose), como
funciona por dentro (namespaces, cgroups, OverlayFS, runtime), segurança, operação em produção,
distribuição e cadeia de suprimentos, e quando partir para orquestração.
Do leigo à teoria de agendamento e aos limites de isolamento.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 27 arquivos + projeto-modelo executável. Bloco A completo (instalação por SO,
  primeiros passos, manual de uso, 14 exemplos, app "mural de recados" com testes que rodam e
  passam). Núcleo do 10 ao 65 (fundamentos → imagens/camadas → isolamento → runtime →
  armazenamento → redes → Dockerfile → Compose → registries → segurança → observabilidade →
  orquestração → teoria avançada → estado da arte de ago/2026). 10 laboratórios, armadilhas,
  custos, cursos PT/EN/FR, certificações, bibliografia, referências, glossário (~90 termos).
- **Verificação:** versões/preços/prazos pesquisados na web em 11/08/2026 (Engine 29.7.1, limites
  do Hub, EU CRA). Projeto-modelo: 22 testes executados e aprovados (Node v24.18.0); `docker build`
  não pôde ser executado no ambiente de escrita — declarado no README do projeto.
- *Última atualização: 11/08/2026*

---

### [salesforce](salesforce/00-MAPA.md)
O CRM e a plataforma: o que é, como se começa do zero, como funciona por dentro
(modelo de dados, segurança em cinco camadas, Apex, LWC, integração, multi-inquilino),
quanto custa de verdade, e onde estudar de graça até a certificação.
Do leigo à teoria de isolamento de performance e limites computacionais.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 27 documentos + projeto-modelo executável (Bloco A completo, incluindo manual
  de instalação por SO com tabela de erros; Bloco B com 13 arquivos de fundamentos a
  estado da arte; 10 laboratórios; custos com data de consulta; cursos PT/EN/FR pesquisados
  na web; bibliografia e referências verificadas; ~150 termos no glossário).
- **Projeto-modelo:** `07-projeto-modelo/` — gestão de ordens de serviço de manutenção.
  2 objetos, trigger com handler, camadas Selector/Service, LWC, permission set,
  25 métodos de teste, seed idempotente. Roda com `sf project deploy start`.
- **Base:** Summer '26 · API 67.0 · CLI 2.146.x · preços consultados em 11/08/2026.
- **Pendente:** nada de estrutura. Reavaliar `65-estado-da-arte.md` e
  `80-custos-e-licencas.md` a cada release (fev/jun/out).
- *Última atualização: 11/08/2026*

---

### [spa-single-page-application](spa-single-page-application/00-MAPA.md)
O que é uma SPA, como funciona por dentro (roteamento, estado, renderização, dados), quando usar
e quando não usar, e as arquiteturas híbridas (SSR, ilhas, RSC) que a sucederam.
Do leigo à teoria de reconciliação e limites algorítmicos.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| 🟡 | ✅ | ✅ | ⬜ | 🟡 | ✅ |

- **Feito:** 19 arquivos, ~5.700 linhas. Núcleo completo (fundamentos → Fiber, signals, limites teóricos), prática com 7 laboratórios, armadilhas, estado da arte de ago/2026, glossário com ~120 termos.
- **Pendente:** os módulos criados na revisão do preset — `02-pre-requisitos`, `03-instalacao`, `04-como-comecar`, `05-manual-de-uso`, `06-exemplos`, `07-projeto-modelo/`, `80-custos-e-licencas`, `85-cursos-e-certificacoes`, `90-bibliografia` (hoje o material de livros está embutido em `17-referencias.md`).
- **Nota:** este assunto foi produzido antes da revisão do preset e usa a numeração antiga (00–17). Ao completar os blocos pendentes, renumerar para o esquema de blocos.
- *Última atualização: 11/08/2026*

---

### [curso-docker](curso-docker/00-indice.md)
**Curso prático aplicado**, complementar ao assunto [`docker`](docker/00-MAPA.md).
Enquanto `docker/` cobre a teoria completa (namespaces, cgroups, OverlayFS, runtime, registries),
este aqui vai direto ao ofício: escrever Dockerfile enxuto, orquestrar com Compose, decidir
armazenamento e rede, endurecer container e depurar com método — usando três projetos reais do
usuário como estudo de caso (FlixARD, sistema financeiro estudantil, CFTV com MotionEye).

> **Estrutura própria**, não a de blocos do preset: segue o roteiro em 10 módulos definido
> explicitamente pelo usuário no pedido (`00-indice.md` + `01-fundamentos/` … `09-proximos-passos.md`),
> com exercício e solução comentada por módulo.

| Estrutura | Exercícios | Projeto executável | Glossário | Validação |
|---|---|---|---|---|
| própria (10 módulos) | ✅ 5 | ✅ | ✅ | 🟡 estática |

- **Feito:** 21 documentos + 3 projetos executáveis, ~4.900 linhas. Módulos: fundamentos ·
  Dockerfile (diretivas, cache de camadas, multi-stage) · Compose (anatomia, variáveis) ·
  armazenamento · redes (modos, DNS interno) · segurança (não-root, secrets, checklist de
  hardening) · depuração (logs/exec, catálogo de erros literais) · projeto aplicado ·
  próximos passos (Swarm vs Kubernetes). Cinco exercícios com solução comentada.
- **Projeto-modelo:** `08-projeto-aplicado/app-fastapi/` — API FastAPI + SQLAlchemy async
  (catálogo de mídias) com config 12-factor, `/health` que executa `SELECT 1` de verdade,
  Dockerfile multi-stage não-root com healthcheck sem `curl`, e compose com Postgres.
  Mais dois composes aplicados: `flixard/` (proxy único, rede `internal`, bind mount de mídia)
  e `sistema-financeiro/` (secrets em arquivo, `read_only`, `cap_drop: ALL`, backup em loop).
- **Verificação:** **o daemon do Docker não estava acessível** (socket `root:docker`, usuário
  fora do grupo, `sudo` com senha) — o usuário optou por validação estática. Foram **executados**:
  4/4 testes do projeto (pytest), a API sob `uvicorn` com `curl` real (`/health` 200,
  `POST /media` 201), o healthcheck nos dois estados (exit 0 e 1), `hadolint` em todos os
  Dockerfiles (**zero avisos**) e `docker compose config` em todos os composes (**todos válidos**).
  Versões conferidas na API do PyPI e tags de imagem na API do Docker Hub em 18/08/2026.
  **Não executados:** `docker build` e `docker compose up` — tamanhos de imagem e tempos de
  build estão marcados no material como estimativas, não medições.
- **Três bugs reais** encontrados na validação viraram material didático: (1) `importlib.reload`
  criando um `Base` novo e deixando o `create_all` sobre metadata vazio; (2) healthcheck em
  Python falhando com **502** enquanto o `curl` respondia **200**, porque o `no_proxy` da máquina
  tem espaço depois da vírgula e o `urllib` não faz o match — container ficaria `unhealthy` com
  a aplicação no ar; (3) `python:3.12-slim` já aponta para **trixie** (confirmado por digest
  idêntico ao de `3.12-slim-trixie`), então o pino `build-essential=12.9`, que é de bookworm,
  quebraria o build.
- **Base:** Docker CLI 29.1.3 · Docker Compose v5.5.0 · hadolint 2.15.1 · Python 3.10.12 ·
  FastAPI 0.141.1 · SQLAlchemy 2.0.52 · Ubuntu 22.04.
- **Pendente:** rodar `docker build`/`compose up` quando houver acesso ao daemon e substituir as
  estimativas de tamanho e tempo por medições. Reavaliar versões e tags a cada ~6 meses.
- *Última atualização: 18/08/2026*

### [hospedagem-de-aplicacoes-web](hospedagem-de-aplicacoes-web/00-MAPA.md)
**Onde e como hospedar um sistema web de quatro peças** — frontend, backend, PostgreSQL e Redis.
Responde à pergunta "quais são hoje as plataformas gratuitas e as melhores", com números reais,
data de consulta e as ressalvas que as tabelas de marketing escondem. Do "o que é hospedar"
à teoria de filas, cold start, pool de conexões e custo marginal de provedor multi-inquilino.
Inclui um capítulo inédito sobre **Brasil**: quem tem região em São Paulo, quanto custa a
distância em milissegundos, e o que a LGPD exige de fato.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 27 documentos + projeto-modelo executável, ~7.500 linhas. Bloco A completo
  (instalação de **todo o conjunto** — Git, Node com gerenciador de versões, Docker/Compose,
  `psql`, `redis-cli`, `gh` e **sete CLIs de plataforma** — nos três SOs, com PATH, permissões
  sem `sudo`, proxy e certificado corporativo, convivência de versões, desinstalação completa,
  **15 erros literais** e alternativa sem instalar nada; manual de uso **por tarefa**;
  **14 exemplos completos e executáveis**). Núcleo do 10 ao 65: fundamentos (IaaS→BaaS, estado,
  latência) → história (1991→2026) → **anatomia de um deploy em 10 etapas** → **quatro catálogos**
  (backend, PostgreSQL, Redis, frontend) → **cinco arquiteturas de referência** → Brasil/LGPD →
  operação → economia do gratuito → teoria avançada → estado da arte de ago/2026.
  12 laboratórios, **32 armadilhas + 8 mitos**, custos com data de consulta e conversão em BRL,
  cursos PT/EN/FR pesquisados na web, bibliografia comentada, glossário com ~160 termos.
- **Projeto-modelo:** `07-projeto-modelo/` — **EncurtaLink**, encurtador de URLs com API Node,
  PostgreSQL, Redis e frontend, em arquitetura de **porta e adaptador**: dois adaptadores de
  repositório (Postgres e memória) e dois de cache (Redis e memória). Roda **sem banco, sem
  Docker e sem `npm install`** em modo memória. Traz cache-aside, limite de taxa por IP,
  bloqueio de SSRF, health check que distingue crítico de degradado, encerramento gracioso,
  migrador próprio, `Dockerfile` multi-stage não-root, `compose.yaml`, `render.yaml`, `fly.toml`
  e CI com serviços efêmeros. **40 testes, executados e aprovados.**
- **Resposta direta à pergunta que originou o assunto** (em `40-arquiteturas-de-referencia.md`):
  pilha 100% gratuita (Cloudflare Pages + Workers + Neon `sa-east-1` + Upstash, R$ 0, sem cartão);
  pilha com região no Brasil por ~US$ 5 (Fly.io `gru`); pilha profissional por ~US$ 35;
  VPS soberano por ~€ 6 mais 3 a 6 h/mês de operação; e corporativa. Cada uma com teto de
  crescimento e **gatilho de troca**.
- **Verificação:** 40 testes executados (Node v24.18.0, Ubuntu 22.04.5); servidor no ar e
  conferido por `curl`; `SIGTERM` observado. Preços, limites, regiões, licenças, cursos e
  câmbio (US$ 1 ≈ R$ 5,20) **pesquisados na web em 18/08/2026**.
- **Não executado (declarado no material):** nenhum deploy real nas plataformas; `docker build`
  e `docker compose up` (daemon inacessível no ambiente de escrita); validação dos manifestos
  com `render blueprints validate` e `flyctl config validate`; preços da Hetzner marcados como
  aproximados porque a página oficial não expôs os valores.
- **Pendente:** nada de estrutura. **Este é o assunto que envelhece mais rápido da pasta**:
  reavaliar `20`/`25`/`30`/`35`/`65`/`80` a cada **6 meses**; `03`/`45`/`85` a cada ano.
- *Última atualização: 18/08/2026*

---

---

### [variaveis-de-ambiente-e-segredos](variaveis-de-ambiente-e-segredos/00-MAPA.md)
**O que fazer com o `.env` quando o sistema sai do desenvolvimento e vai para o cliente.**
Responde à pergunta em três frases — o arquivo não vai, o conteúdo vai, o código não muda —
e depois demonstra o porquê e o como em **Node, PHP, Python, Java, .NET, Go, Ruby e Rust**,
sobre **systemd, `LoadCredential`, Docker, Compose, Kubernetes, PaaS, serverless, hospedagem
compartilhada e na máquina do cliente**. Do `execve` de 1979 à criptografia de envelope,
ao problema do segredo zero e ao SPIFFE.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 30 documentos + projeto-modelo executável, ~11.900 linhas. Bloco A completo
  (instalação de **nove tecnologias** — Git, Node, PHP+Composer, Python, Docker, direnv,
  SOPS+age, gitleaks, OpenBao — nos três SOs, com PATH, permissões sem `sudo`, proxy e
  certificado interno, convivência de versões, desinstalação e **13 erros literais**;
  manual de uso por tarefa; **15 exemplos completos**). Núcleo do 10 ao 65: fundamentos
  (`execve`, `/proc/PID/environ`, precedência) → história (1979→2026) → **o formato `.env`
  que não tem padrão** → um capítulo por linguagem → **por que não existe segredo no
  navegador** → entrega em produção por cenário → CI/CD e OIDC → cofres → rotação com
  sobreposição → resposta a vazamento → **entrega on-premise ao cliente** → teoria avançada
  → estado da arte de ago/2026. 12 laboratórios, **30 armadilhas + 10 mitos**, custos com
  data e câmbio, cursos PT/EN/FR pesquisados na web, glossário com ~110 termos.
- **Projeto-modelo:** `07-projeto-modelo/` — API de recados em Node, **zero dependências**,
  com módulo de configuração puro e testável (valida tudo, reporta todos os erros, sai com
  **78/`EX_CONFIG`**), padrão `_FILE`, log com redação em duas camadas, rota `/config`
  mascarada para suporte, unit systemd blindada, **instalador para a máquina do cliente**,
  Dockerfile/Compose e **os mesmos contratos reescritos em Python e PHP**.
  **43 testes, 43 aprovados.**
- **Verificação (medições, não suposições):** suíte 43/43; servidor executado e exercitado
  com `curl` real; **precedência ambiente × `.env` travada por teste em processo real**;
  **divergências de parsing medidas** entre Node `--env-file`, `dotenv` 17.4.2 e
  `python-dotenv` 1.2.3 (o `#` sem aspas trunca em um e não no outro; a expansão `${VAR}`
  funciona em um e não no outro); **`variables_order = GPCS` confirmado em PHP, com `$_ENV`
  vazio e `getenv()` funcionando**; padrão `_FILE` verificado ponta a ponta nas três
  linguagens, incluindo a prova de que o segredo **não** aparece em `/proc/<pid>/environ`;
  laboratório de vazamento executado inteiro, com `git filter-repo`; `ARG_MAX`, herança
  pai/filho e `setenv` invisível em `/proc`. Preços, licenças, cursos e câmbio pesquisados
  na web em 14 e 18/08/2026.
- **Base:** Ubuntu 22.04.5 · Node v24.18.0 · npm 12.0.1 · Python 3.10.12 · PHP 8.1.2 ·
  Docker 29.1.3 · git 2.34.1 · dotenv 17.4.2 · python-dotenv 1.2.3.
- **Não executado (declarado no material):** `docker build`/`compose up` (usuário fora do
  grupo `docker`); `install.sh` e a unit systemd (exigem root); SOPS, age, gitleaks, OpenBao,
  Composer, `phpdotenv` e `pydantic-settings` (não instalados na máquina); instalação em
  macOS e Windows; exemplos de Java, .NET, Go, Ruby e Rust.
- **Pendente:** nada de estrutura. Reavaliar `65` e `80` a cada 6 meses, `03` a cada 6 meses,
  `85` a cada ano.
- *Última atualização: 18/08/2026*

---

### [processamento-de-sinais](processamento-de-sinais/00-MAPA.md)
Do sinal analógico ao espectro na tela: amostragem e Nyquist, Fourier, DFT/FFT, transformada Z,
filtros FIR e IIR, análise espectral e janelas. Responde diretamente **"por onde começar"** e
**"que matemática aprender"** — com roteiro de 3 meses e a fatia exata de matemática que o campo
usa. **Dois projetos-modelo executáveis**, um de áudio e um de pesquisa espacial.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 36 documentos. Bloco A completo (instalação por SO com tabela de 12 erros
  literais; 12 exemplos executados incluindo DTMF por Goertzel, limpeza de ECG, filtro casado
  e dither; manual de notação + API por tarefa + equivalência MATLAB). Núcleo do `10` ao `65`
  (fundamentos e convolução → história → **`12-matematica-do-zero.md`** → sistemas LTI →
  Fourier → amostragem → DFT/FFT → transformada Z → FIR → IIR → análise espectral →
  multitaxa → processos estocásticos → filtragem adaptativa → wavelets → áudio e fala →
  comunicações e SDR → imagens 2-D → ponto fixo e hardware → DSP e aprendizado de máquina →
  teoria avançada → estado da arte). 14 laboratórios, 30 armadilhas + 10 mitos, custos com
  data, cursos PT/EN/FR pesquisados na web, bibliografia com 4 livros legalmente gratuitos,
  papers seminais e normas, e glossário com ~130 termos.
- **Projetos-modelo:** `07-projeto-modelo/` — `sinal`, afinador e filtrador de áudio
  (25 testes, precisão de 0,1 cent). `08-projeto-espacial/` — **`cosmos`, sinais do espaço
  profundo** (56 testes): equação do radiômetro, dispersão interestelar, detecção de pulsar
  por folding e enlace de espaço profundo com código PN e Doppler, acompanhado de um curso
  aplicado de 6 documentos que vai do problema científico ao código linha a linha.
- **Verificação:** todo bloco de código foi executado; as saídas publicadas são reais.
  81 testes passando, zero links internos quebrados. Quatro achados contrariaram o folclore
  da área e ficaram registrados como medição: o sobressinal de ~9 % na resposta ao degrau
  **não** é eliminado por janelamento; `signal.resample` é mais preciso que `resample_poly`
  no miolo e pior nas bordas; medir a variância de um estimador espectral ao longo da
  frequência dá resultado errado; e o estimador de SNR por máximo tem piso de 3,22 σ em
  ruído puro.
- **Pendente:** nada de estrutura. Reavaliar `65` e `80` a cada 6 meses, `03` a cada
  6 meses, `85` a cada ano.
- *Última atualização: 19/08/2026*

---

### [engenharia-de-prompt](engenharia-de-prompt/00-MAPA.md)
O que é um Engenheiro de Prompt, o que o cargo realmente exige em 2026, e como se tornar um
do zero. Da analogia do estagiário genial e amnésico à teoria de por que a cadeia de
pensamento **aumenta a classe de problemas solucionáveis**. A tese que atravessa o curso é
que **o ativo não é o prompt, é a avaliação** — e o material trata avaliação, custo,
segurança e carreira com a mesma seriedade das técnicas de redação.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 28 documentos + projeto-modelo executável, ~7.300 linhas. Bloco A completo (instalação
  cobrindo Python/uv/SDK/Node/promptfoo/DSPy/ollama nos três SOs, com PATH, permissões,
  proxy corporativo, desinstalação e 11 erros literais; 12 exemplos com verificação
  executada, dois deles de produção). Núcleo do `10` ao `65` (fundamentos → história →
  anatomia do prompt → técnicas com ficha de custo e modo de falha → saída estruturada →
  contexto e RAG → **avaliação** → ferramentas e agentes → custo/latência/cache →
  segurança e injeção → a profissão → otimização automática → teoria avançada → estado da
  arte de ago/2026). 14 laboratórios, 25 armadilhas + 12 mitos, custos com data e câmbio,
  cursos PT/EN/FR pesquisados na web, bibliografia com edições e ISBN conferidos, 77
  verbetes no glossário.
- **Projeto-modelo:** `07-projeto-modelo/` — `triador`, triagem de chamados de suporte
  **em stdlib puro, zero dependências**: três versões de prompt versionadas, 22 casos
  rotulados à mão, extração tolerante + validação estrita, laço de correção com o erro
  literal do validador, arnês de avaliação com tabela comparativa, estimativa de custo e
  portão de CI. Provedor **simulado** roda offline (sem chave de API) e provedor real da
  Anthropic atrás da mesma interface. **23 testes.**
- **Verificação:** 23/23 testes aprovados (Python 3.10.12). Todos os trechos de código dos
  arquivos `06`, `14`, `20`, `30` e `45` foram executados e as saídas publicadas são as
  reais — três delas foram corrigidas no texto depois de a execução contrariar o que estava
  escrito. Avaliação medida: prompt ingênuo 0%, estruturado 82%, com exemplos 91% (22
  casos). 223 links internos, zero quebrados. Versões, preços (com câmbio de 19/08/2026),
  cursos e edições de livro pesquisados na web em 19/08/2026.
- **Achados registrados como medição:** a busca gulosa do otimizador de `45` cai numa
  armadilha real (98% a 570 tokens quando existia 99% a 480); a seleção de exemplos por
  sobreposição de palavras acerta 1 de 3 — demonstrando por que se usa embedding; e dois
  erros do projeto-modelo sobrevivem ao few-shot por motivos diferentes (um pede regra
  nova, outro pede exemplo novo).
- **Pendente:** nada de estrutura. Reavaliar `65` e `80` a cada 6 meses, `03` a cada
  6 meses, `85` e `40` a cada ano.
- *Última atualização: 19/08/2026*

---

### [criptografia](criptografia/00-MAPA.md)
O que é criptografia, como funciona por dentro e como se começa do zero. Do bilhete
na sala de aula ao acordo híbrido pós-quântico X25519+ML-KEM-768. Ferramentas reais
(OpenSSL, GPG, age), exemplos executados de verdade e um projeto-modelo que implementa
ChaCha20-Poly1305 e X25519 em Python puro, conferidos contra os vetores dos RFCs.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | 🟡 | ⬜ | ⬜ | ⬜ | ⬜ |

- **Feito:** Bloco A completo (`01`–`07`), com manual de instalação cobrindo Python,
  OpenSSL, GnuPG, age e bibliotecas nos três sistemas operacionais, 13 exemplos
  **executados** (saídas reais, inclusive medições de tempo) e projeto-modelo `cofre`
  com **46 testes aprovados**. Do núcleo, `10-fundamentos` e `11-historia`.
- **Verificação:** o `cofre` bate com os vetores oficiais dos RFCs 8439, 7748, 5869 e
  7914, e produz bytes **idênticos aos do OpenSSL** (teste de interoperabilidade).
  Versões, preços e datas pesquisados na web em 19/08/2026.
- **Pendente:** núcleo `12`–`26`, `60`, `65`; blocos C, D, E e o glossário.
- *Última atualização: 19/08/2026*

---

### [investimentos-brasil](investimentos-brasil/00-MAPA.md)
Onde colocar dinheiro no Brasil de hoje, do zero absoluto à teoria de apreçamento.
Nasceu da pergunta "qual a maneira mais segura e lucrativa de investir R$ 6.000?" —
e a responde com as contas feitas: com a Selic a 14,00% e o IPCA a 4,44%, o ativo mais
seguro do país paga ~9% reais ao ano. Abrir conta, IR e IOF na mão, marcação a mercado,
FGC e o caso Banco Master, carteira por prazo, Markowitz e CAPM, e um simulador em
Python que compara qualquer produto pelo que sobra no bolso.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** curso completo, 23 arquivos. Bloco A com manual de instalação cobrindo o
  ambiente **financeiro** (corretora, 2FA, adesão ao Tesouro Direto, gov.br, Registrato,
  Área do Investidor da B3) e o **técnico** (Python nos três sistemas operacionais),
  com tabela de erros literais; **13 exemplos com as contas executadas**, incluindo dois
  casos reais (liquidação do Banco Master e dívida de cartão). Núcleo com fundamentos,
  história (de 1861 ao pêndulo 2020–2026), mecânica dos títulos, tributação, risco e
  garantias, renda variável, carteira, teoria avançada e estado da arte datado.
- **Projeto-modelo:** `07-projeto-modelo/` — `simulador`, **em stdlib puro, zero
  dependências**: modela IR regressivo, IOF de 30 dias, come-cotas, custódia da B3 e
  carência, com CLI de três comandos (`comparar`, `plano`, `impostos`), configuração
  por JSON com validação e exportação CSV. **31 testes aprovados** (Python 3.10.12).
- **Verificação:** todos os números publicados nas tabelas foram **produzidos rodando o
  código** — nenhum foi estimado. 166 links internos, zero quebrados. Selic, CDI, IPCA,
  Focus, taxas do Tesouro, tarifas da B3, regras do FGC, legislação, cursos e preços de
  certificação pesquisados na web em 20/08/2026.
- **Achado central registrado:** com a Selic em 14,00% e o IPCA em 4,44%, "mais seguro"
  e "mais lucrativo" quase deixam de se opor no Brasil — o pós-fixado soberano entrega
  ~11,5% líquidos (6,7% reais) sem carência e sem oscilação, contra 8,34% da poupança.
  A diferença medida sobre R$ 6.000 em um ano é de R$ 256, com risco idêntico.
- **Pendente:** nada de estrutura. Reavaliar `65` e `95` a cada 3 meses, `14` a cada
  6 meses ou a cada mudança tributária, e `indicadores.py` a cada reunião do Copom.
- *Última atualização: 20/08/2026*

---

### [estatistica-descritiva](estatistica-descritiva/00-MAPA.md)
O que são média, mediana, desvio padrão e **erro** — e o que cada uma significa na realidade.
Da gangorra e do rio de 1,20 m de profundidade média até e-values e predição conformal.
Todo código executado de verdade, com as saídas reais; projeto-modelo que produz um relatório
estatístico e **avisa quando não se deve acreditar nele**.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | 🟡 | ⬜ | ⬜ | ⬜ |

- **Feito:** Blocos A (`01`–`07`) e B (`10`–`20`, `60`, `65`) completos; `70-pratica` com 14
  laboratórios. 14 exemplos executados (Simpson com os dados reais de Charig 1986, Anscombe,
  cauda em microsserviços, comparações múltiplas). Projeto-modelo `resumo`: CLI em **stdlib
  puro**, com distribuição t de Student implementada do zero, bootstrap, camada de diagnóstico
  que recomenda mediana em vez de média quando os dados são assimétricos — **83 testes
  passando**.
- **Verificação:** a t implementada bate com as tabelas impressas até a 4ª casa; simulações
  reproduzem Bessel, TCL, cobertura real de IC (81% com z=1,96 e n=3) e p-hacking (5% → 29%
  ao espiar os dados). Versões pesquisadas na web em 20/08/2026.
- **Pendente:** `75-armadilhas`, blocos D (`80`, `85`) e E (`90`, `95`), `GLOSSARIO.md`.
- *Última atualização: 20/08/2026*

---

### [engenharia-de-software-com-ia](engenharia-de-software-com-ia/00-MAPA.md)
**"O que é um dev que sabe usar IA?"** — a resposta desenvolvida, justificada e
transformada em prática. A tese: não é quem escreve prompts melhores, é **quem
consegue verificar mais rápido do que a máquina produz**. Da analogia da serraria
ao teorema de Rice. Manual de instalação de seis blocos de tecnologia nos três
sistemas operacionais; os quatro modos de uso; o laço do agente sem caixa-preta
(com um agente funcional em 80 linhas); especificação com critérios decidíveis e
EARS; a pirâmide de verificação, teste de mutação e cobertura do diff; método de
revisão para código de máquina (porque a pista visual do revisor desapareceu);
injeção indireta de prompt com CVEs reais, trinca letal e slopsquatting; e a
evidência de produtividade lida **com a metodologia junto** — METR, DORA,
LinearB, GitClear e Stack Overflow, sem propaganda e sem ceticismo de ocasião.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 35 documentos + projeto-modelo executável, ~9.900 linhas. Bloco A
  completo (instalação cobrindo terminal/Git/ripgrep/Node/Python/Docker/6 agentes
  de CLI e IDE/gitleaks/pre-commit/uv/mise/Spec Kit/MCP, com PATH, permissões sem
  `sudo`, proxy corporativo com certificado interno, convivência de versões,
  desinstalação completa e 14 erros literais; 12 exemplos completos, incluindo
  dois casos de produção — triagem de teste instável no CI e migração de 400
  arquivos com portão e amostragem estratificada). Núcleo do 10 ao 65
  (fundamentos → história de 1957 a 2026 → o modelo por dentro → quatro modos de
  uso → o repositório como prompt → o laço agêntico → especificação → verificação
  → revisão → arquitetura → Git → CI/CD → segurança → lei → evidência →
  níveis → carreira → times → teoria → estado da arte). 14 laboratórios,
  24 armadilhas + 14 mitos + 3 erosões, custos com data e câmbio, cursos PT/EN/FR
  pesquisados na web, bibliografia com ISBNs conferidos, ~70 termos no glossário.
- **Projeto-modelo:** `07-projeto-modelo/` — **`portao`**, portão de verificação
  para código gerado por IA, em **Python stdlib puro, zero dependências**. Cinco
  regras: escopo (tocou só no que devia?), tamanho (cabe numa revisão?), segredos
  (padrões conhecidos + entropia de Shannon), pacotes (dependência nova e
  detecção de alucinação) e critérios (todo `CA-NN` da especificação tem teste?).
  Duas severidades, escape anotado, modo offline determinístico por padrão,
  relatório em texto e JSON. **49 testes aprovados** (Python 3.10.12).
- **Verificação:** 49/49 testes executados e aprovados; **dois defeitos reais
  foram encontrados pelos próprios testes durante a construção e corrigidos**.
  A ferramenta foi executada sobre os dois diffs de exemplo e a saída publicada
  no README é a saída real (código 0 no limpo, código 1 e 5 bloqueios no sujo).
  O projeto se submete à própria regra de critérios. 342 links internos, zero
  quebrados. Versões, preços, câmbio (US$ 1 = R$ 5,19), CVEs, cursos e edições de
  livro pesquisados na web em 20/08/2026.
- **Achado central registrado:** a produção dobrou e o ganho líquido foi de ~10%
  (LinearB, 8,1 M de PRs) — o resto virou **estoque na fila de revisão**, que
  subiu 91%. Ao mesmo tempo, a duplicação de blocos subiu 81% desde 2023 e o
  código movido (sinal de refatoração) caiu de 21% para 3,8% (GitClear, 623 M de
  alterações). O gargalo não é escrever; é decidir se é seguro fundir.
- **Nota de método:** agregadores consultados durante a pesquisa afirmaram que o
  Gemini CLI havia sido descontinuado — falso, o repositório oficial está ativo —
  e publicaram tabelas de benchmark com números que não batem com as fontes
  originais. O curso registra isso e usa apenas fontes primárias.
- **Base:** Ubuntu 22.04.5 LTS · Python 3.10.12 · Node v24.18.0 · npm 12.0.1 ·
  Git 2.34.1 · Docker 29.7.2 · ripgrep 14.1.1 · Claude Code 2.1.237.
- **Pendente:** nada de estrutura. Reavaliar `65-estado-da-arte.md` e
  `80-custos-e-licencas.md` a cada 3 meses; `03-instalacao.md` e
  `85-cursos-e-certificacoes.md` a cada 6 meses; `22-seguranca.md` a cada CVE
  relevante de agente de codificação; `24-produtividade` a cada novo DORA,
  LinearB ou GitClear.
- *Última atualização: 20/08/2026*

### [ingles-do-basico-ao-fluente](ingles-do-basico-ao-fluente/00-MAPA.md)
Curso completo de inglês, do "não sei dizer meu nome" ao nível de pesquisa em aquisição de
segunda língua. Trata o assunto como engenharia, não como matéria escolar: por que o brasileiro
trava (segmentação e formas reduzidas, não vocabulário), quantas horas de fato separam o zero do
B2, e o que a evidência sustenta sobre método. Inclui fonética e fonologia com os contrastes que
faltam ao ouvido brasileiro, gramática do núcleo à estrutura da informação, as quatro habilidades
com protocolo de treino, pragmática (por que educação em inglês é gramática), inglês de trabalho
em tecnologia, teoria de SLA nível pós-graduação, e um sistema de estudo executável em Python.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 29 documentos na raiz + 5 no projeto-modelo, ~10.400 linhas. Bloco A completo
  (manual de ambiente de estudo cobrindo Anki/AnkiDroid/AnkiWeb/AnkiConnect, LanguageTool
  self-hosted, GoldenDict-ng, Kiwix, mpv/ffmpeg/yt-dlp e Audacity, nos três sistemas
  operacionais, com PATH, permissões, proxy corporativo com a armadilha do `no_proxy`,
  desinstalação completa e 12 erros literais; 12 exemplos completos, incluindo dois casos reais
  de produção — pull request/code review e entrevista comportamental STAR). Núcleo do 10 ao 65
  (fundamentos e CEFR 2020 com mediação → história da língua do proto-germânico à Grande Mudança
  Vocálica → fonética com os oito contrastes vocálicos ausentes no português, ritmo acentual,
  formas fracas e os cinco processos de fala conectada → ortografia e falsos cognatos →
  vocabulário com Zipf e os limiares de 95%/98% de Nation → gramática do núcleo e avançada
  (Aktionsart, modalidade epistêmica, clivadas, hedging) → as quatro habilidades com protocolo
  → pragmática e ELF → inglês para tecnologia com RFC 2119 → SLA nível pesquisa → estado da arte
  de ago/2026). 14 laboratórios, 12 armadilhas + 12 mitos, custos com data e câmbio, cursos
  PT/EN/FR pesquisados na web, bibliografia com edições conferidas, ~130 termos no glossário.
- **Projeto-modelo:** `07-projeto-modelo/` — **Projeto Ponte**, sistema pessoal de estudo com
  **zero dependências** (só biblioteca padrão do Python): 50 frases A1–B2 com IPA, tradução e
  alvo de cloze em TSV; `gerar_deck.py` valida os dados e produz dois arquivos importáveis no
  Anki (reconhecimento + produção, 100 cartões), com filtros por nível e por assunto;
  `estudo.py` registra sessões em JSONL append-only e monta um painel com sequência de dias,
  distribuição por habilidade e projeção até o nível-alvo; mais currículo de 12 semanas,
  protocolo de shadowing, diário de estudo e rubrica de autoavaliação.
- **Verificação:** **42/42 testes executados e aprovados** (Python 3.10.12), incluindo os
  caminhos ruins — arquivo ausente, JSON corrompido, divisão por zero na projeção, filtro que
  zera o resultado. O validador **rejeitou a linha 015 do TSV na primeira execução** (trecho de
  cloze inexistente na frase) e o dado foi corrigido: o projeto se submete à própria regra.
  299 links internos, zero quebrados. Preços de exames, câmbio (US$ 1 = R$ 5,17 · € 1 = R$ 6,02),
  versões (Anki 26.08.1), cursos e edições de livro pesquisados na web em 31/08/2026.
- **Achado central registrado:** a maior parte do que o brasileiro "não entende" ao ouvir são
  **palavras que ele já sabe**, na forma reduzida (`to` → /tə/, `going to` → /ˈɡənə/,
  *what do you* → /ˈwʌdəjə/). É um problema de reconhecimento, não de vocabulário — e portanto
  tratável em semanas, não em anos. Quase todo mundo o diagnostica na camada errada e estuda
  mais vocabulário, sem melhorar.
- **Nota de método:** blogs comerciais encontrados na pesquisa afirmam "fluência conversacional
  em 6–8 meses com IA contra 12–18 meses no método tradicional". Não há estudo controlado por
  trás disso, e o curso registra a alegação como não sustentada. A literatura sobre tutores LLM
  aponta o contrário como risco: eles priorizam fluência sobre correção e deixam passar erro
  sutil — o mecanismo exato da fossilização.
- **Base:** Ubuntu 22.04.5 LTS · Python 3.10.12 · Anki 26.08.1 · ffmpeg 4.4.2 · mpv 0.34.1.
- **Pendente:** nada de estrutura. Reavaliar `65-estado-da-arte.md`, `80-custos-e-licencas.md`,
  `85-cursos-e-certificacoes.md` e `03-instalacao.md` a cada 6 meses; `90-bibliografia.md` a cada
  12 meses. Extensões possíveis: inglês acadêmico, inglês para imigração, e ampliar o baralho de
  50 para 500 frases.
- *Última atualização: 31/08/2026*

---

### [uv-python](uv-python/00-MAPA.md)
O **uv**, o gerenciador de pacotes e projetos Python escrito em Rust pela Astral — do primeiro
comando à prova de que resolver dependências é NP-completo. Cobre os 23 comandos, o modelo de
três camadas (`pyproject.toml` → `uv.lock` → `.venv`), o algoritmo PubGrub e a resolução
universal com *forking*, cache e hard links, gerenciamento de Python sem pyenv, scripts PEP 723,
workspaces de monorepo, build e publicação com Trusted Publishing, Docker/CI, migração de
pip/Poetry/conda **com rota de volta**, e uma análise honesta do risco depois da aquisição da
Astral pela OpenAI em 19/03/2026.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 28 documentos + projeto-modelo executável: **~10.600 linhas de material** e 679 linhas de código Python. Bloco A completo
  (instalação por SO cobrindo Linux em 5 famílias, macOS Intel/ARM, Windows nativo e WSL2,
  Docker, além de Git, VS Code, compilador e ferramentas — com PATH, permissões, proxy
  corporativo com certificado interno, convivência de versões, desinstalação completa,
  **16 erros literais** e alternativa sem instalar nada; manual dos **23 comandos** organizado
  por tarefa; **14 exemplos completos**, dois deles de produção). Núcleo do 10 ao 65
  (fundamentos e as 15 PEPs → história de 1991 a 2026 → modelo de projeto → **resolução
  PubGrub e forking** → cache e hard links → Python gerenciado → `uvx` e PEP 723 → workspaces →
  build e publicação → Docker/CI → migração → segurança da cadeia de suprimentos → teoria
  avançada → estado da arte de 31/08/2026). 14 laboratórios, 24 armadilhas + 10 mitos, custos
  com data e câmbio, cursos PT/EN/FR pesquisados na web, bibliografia com ISBNs conferidos,
  ~70 termos no glossário.
- **Projeto-modelo:** `07-projeto-modelo/` — **`lockspect`**, ferramenta de linha de comando que
  lê um `uv.lock` e explica o que há dentro dele (resumo, árvore, "quem depende de quê", JSON).
  Layout `src/`, backend `uv_build`, grupos `dev`/`lint` separados, extra opcional, marcador de
  ambiente real (`tomli ; python_version < '3.11'`), `main()` testável que devolve código de
  saída, quatro códigos de saída distintos, normalização PEP 503, e um script **PEP 723**
  independente do projeto (`scripts/comparar_locks.py`).
- **Verificação:** **25/25 testes executados e aprovados** (pytest, Python 3.10.12), cobertura
  de **96%**, `ruff check` e `ruff format --check` limpos, `uv build` gerando sdist e wheel, e o
  script PEP 723 executado com saída conferida. Também foram executados de verdade: `uv init`,
  `add`, `run`, `sync`, `lock`, `export` (requirements.txt e pylock.toml), `tree`, `version`,
  `python list/install/pin` (com download automático do CPython 3.14.7), `uvx`, `uv tool`,
  `venv`, `pip install`, `format`, `check`, `audit`, `cache size`, e um **workspace completo
  montado do zero**. **Benchmark medido nesta máquina:** `pip` 23,5 s × `uv` sem cache 3,6 s ×
  `uv` com cache 3,0 s (fastapi + pandas). **Hard links provados** com `ls -li` (contagem de
  links = 4). Versões, preços, cursos e a aquisição pela OpenAI pesquisados na web em 31/08/2026.
- **Achado central registrado:** a velocidade é o gancho, não o valor. O que justifica adotar é a
  **unificação** — uma ferramenta no lugar de sete — e a distinção entre **declaração**
  (`pyproject.toml`), **resolução** (`uv.lock`) e **materialização** (`.venv`), que é a origem de
  quase todos os erros de quem usa uv sem entendê-lo. O curso também registra, com números
  próprios, que o "100× mais rápido" da propaganda vale **com cache quente**; numa instalação
  nova dominada por rede, medi **7×**.
- **Nota de risco registrada:** a Astral foi adquirida pela OpenAI em 19/03/2026 e o produto
  comercial (`pyx`) foi descontinuado. A licença MIT/Apache-2.0 impede que o uv "feche", mas não
  há fundação nem governança independente. O curso trata isso como **risco de estagnação**, não
  de cobrança, e documenta a mitigação: `pyproject.toml` padrão PEP 621 e saída em um comando
  (`uv export --format pylock.toml`).
- **Base:** Ubuntu 22.04.5 LTS · uv 0.12.7 · Python 3.10.12 e 3.14.7.
- **Pendente:** nada de estrutura. Os Dockerfiles do arquivo 19 seguem a documentação oficial mas
  **não puderam ser construídos** nesta máquina (sem acesso ao daemon Docker) — está sinalizado
  no topo do arquivo. Reavaliar `65-estado-da-arte.md`, `80-custos-e-licencas.md` e
  `03-instalacao.md` **a cada 3 meses** (o uv lança a cada 1–2 semanas) e
  `85-cursos-e-certificacoes.md` a cada 6 meses.
- *Última atualização: 31/08/2026*

### [tls](tls/00-MAPA.md)
O protocolo que põe o **S** no HTTPS. Da analogia do envelope lacrado até a análise formal
do handshake: certificados X.509 campo a campo, a PKI e por que ela é o elo mais frágil,
o handshake do TLS 1.3 com bytes reais capturados, a criptografia por baixo (ECDHE, AEAD,
HKDF), revogação e por que ela nunca funcionou, ACME e automação, configuração comentada
de nginx/Apache/Caddy/HAProxy/Node/Python/Go/Java, mTLS e PKI interna, TLS fora do HTTPS
(e-mail, DNS cifrado, QUIC, IoT), desempenho medido, o catálogo de ataques de 1995 a 2020,
e o estado da arte de ago/2026 — ML-KEM híbrido, ECH (RFC 9849), validade de 200 dias e
Merkle Tree Certificates.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 28 documentos + projeto-modelo executável, ~10.900 linhas. Bloco A completo
  (instalação cobrindo OpenSSL, curl, Python, Node, mkcert, certbot, nginx, Caddy,
  testssl.sh, Wireshark e Docker nos três SOs, com PATH, permissões, proxy corporativo com
  CA interna, convivência de versões do OpenSSL, desinstalação e 16 erros literais;
  14 exemplos completos, 3 deles de produção). Núcleo do 10 ao 65 (fundamentos → história
  → handshake mensagem a mensagem → X.509 e PKI → criptografia do TLS → revogação e
  Certificate Transparency → ACME → configuração de servidores → mTLS e PKI interna →
  TLS além do HTTPS → desempenho e operação → ataques e defesas → teoria avançada →
  estado da arte). 12 laboratórios, 28 armadilhas + 12 mitos, custos com data de consulta
  e câmbio, cursos PT/EN/FR pesquisados na web, bibliografia com edições conferidas,
  ~150 termos no glossário.
- **Projeto-modelo:** `07-projeto-modelo/` — `cofre-tls`: API de notas com **mTLS**,
  **CA própria operada com `openssl ca`** (base de emissão `index.txt`, número de série,
  **CRL de verdade**), perfis de emissão separados para `serverAuth` e `clientAuth`,
  autorização por identidade do certificado, e clientes de teste que incluem um
  **revogado**, um **vencido** e um assinado por uma **CA intrusa**. Zero dependências —
  só a biblioteca padrão do Python e o `openssl`.
- **Verificação:** **32/32 testes executados e aprovados** (Python 3.10.12, OpenSSL 3.0.2,
  Ubuntu 22.04.5, em 31/08/2026). Metade deles são ataques: sem certificado
  (`certificate required`), CA desconhecida (`unknown ca`), revogado (`certificate revoked`),
  vencido (`certificate expired`), nome de servidor errado, CA errada no cliente e TLS 1.1.
  Fluxo completo exercitado com `curl` e com o cliente próprio. `openssl speed` rodado para
  os números de desempenho do arquivo 20; `ClientHello` real capturado com
  `openssl s_client -trace` para o arquivo 12. Versões, preços, RFCs de 2026, cronograma do
  CA/B Forum e cursos pesquisados na web em 31/08/2026.
- **Pendente:** nada de estrutura. Saídas contra **hosts públicos** estão marcadas como
  *saída típica* (não *saída real*): a máquina em que o material foi escrito só alcança a
  internet por proxy corporativo, o que impede a conexão TLS direta necessária para
  capturá-las — os comandos estão corretos e prontos para o leitor executar. Reavaliar
  `65-estado-da-arte.md` **a cada 3 meses** (MTC, ECH e a redução de validade estão em
  movimento), `80-custos-e-licencas.md` e `03-instalacao.md` a cada 6 meses.
- *Última atualização: 31/08/2026*

### [n8n](n8n/00-MAPA.md)
Automação de fluxos e orquestração de agentes de IA com n8n — da analogia da esteira
de montagem ao limite teórico de por que *exactly-once* não existe. Manual de instalação
por Docker nos três sistemas operacionais (com proxy corporativo e CA interna), modelo de
itens e item linking a fundo, expressões, gatilhos e o novo agendador durável, task
runners e o que o modo interno significa para a segurança, confiabilidade e idempotência,
queue mode com workers e Redis, segurança, IA/LangChain/MCP, custos com data e câmbio, e a
**Sustainable Use License explicada com o texto original** — inclusive o que você **não**
pode fazer sem contrato comercial.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 31 documentos + projeto-modelo executável, ~9.100 linhas. Bloco A completo
  (instalação cobrindo Docker em Debian/Ubuntu, Fedora/RHEL, macOS Intel e Apple Silicon,
  Windows nativo e WSL2, one-line setup, Compose com Postgres e npm como legado, com PATH,
  permissões, proxy corporativo, `no_proxy` malformado, CA interna, convivência de versões,
  atualização, desinstalação completa e **19 mensagens de erro literais**; 14 exemplos
  completos, sendo dois casos de produção). Núcleo do 10 ao 65 (fundamentos → história de
  EAI/ESB até a Série C → modelo de dados e cardinalidade → expressões → nós e credenciais →
  fluxo de controle → gatilhos e **agendador durável** → Code node e task runners →
  **erros e idempotência** → arquitetura interna → escala e queue mode → segurança →
  ciclo de vida e preparação para o n8n 3.0 → IA, agentes e MCP → API pública e Embed →
  teoria avançada → estado da arte de set/2026). 14 laboratórios com critério de aceitação,
  22 armadilhas + 12 mitos + 7 más práticas, custos com data e câmbio, cursos PT/EN/FR
  pesquisados na web, bibliografia que **explica por que não recomendar os livros de n8n
  existentes**, ~110 termos no glossário.
- **Projeto-modelo:** `07-projeto-modelo/` — **`central-de-pedidos`**: API de recebimento
  de pedidos construída inteiramente em n8n, com **Postgres**, 4 workflows
  (receber com validação e resposta 202/400, consultar com 200/404, relatório agendado em
  CSV, e **Error Workflow** gravando falhas), **idempotência garantida por chave primária**
  (`ON CONFLICT DO NOTHING`), consulta parametrizada contra injeção de SQL, `retryOnFail`
  só onde é seguro, poda de execuções ligada desde o primeiro dia, `Makefile` com o ciclo
  completo e script de teste de ponta a ponta com 6 verificações.
- **Verificação:** n8n **2.36.9** instalado e executado de verdade (Node 24.18.0,
  Ubuntu 22.04.5, em 01/09/2026). `n8n --help`, `export:nodes` (**910 tipos de nó**),
  `import:workflow`, `import:credentials`, `publish:workflow` e `execute --rawOutput`
  executados — as tabelas de CLI e as saídas nó a nó do curso são reais. Webhook exercitado
  de ponta a ponta com `curl`: os 4 workflows do projeto importados e publicados numa
  instância real, com **HTTP 400** e a lista de erros de validação, e **HTTP 202** com o
  pedido aceito. Versões, preços, licença, cursos PT/EN/FR e estado da arte pesquisados na
  web em 01/09/2026.
- **Pendente:** o trecho do projeto-modelo que depende do **Postgres em contêiner**
  (gravação, consulta 200/404, relatório em CSV e registro de erros) **não foi executado**:
  a máquina em que o material foi escrito só alcança a internet por proxy corporativo e o
  *daemon* do Docker não tem esse proxy configurado, o que impede baixar as imagens. Os
  comandos e o SQL estão corretos e o `make testar` verifica exatamente esses pontos.
  **Revisar o curso inteiro em outubro de 2026**, quando o n8n 3.0 remove a instalação por
  npm, os nós Function/Function Item/Item Lists e o AI Agent v1. Reavaliar
  `65-estado-da-arte.md` a cada 3 meses; `80-custos-e-licencas.md` e `03-instalacao.md`
  a cada 6 meses.
- *Última atualização: 01/09/2026*

---

### [mcp](mcp/00-MAPA.md)
**Model Context Protocol** — o padrão aberto que conecta aplicações de IA a ferramentas,
dados e sistemas. Do "estagiário trancado na sala" à teoria de por que a injeção de prompt
não tem solução. Cobre a revisão **`2026-07-28`**, a maior reescrita do protocolo: sem
sessões, sem `initialize`, com MRTR — mecânica que **quase todo material publicado antes
de agosto de 2026 ensina errado**. Servidores e clientes em Python e TypeScript, a fita
JSON-RPC crua, os dois transportes, OAuth 2.1 com validação de audiência, o registry,
Tasks e MCP Apps, custo real em reais, e um arquivo inteiro sobre o que a segurança do
MCP **não** resolve.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 30 documentos + projeto-modelo executável, ~12.000 linhas. Bloco A completo
  (instalação cobrindo Python/`uv`, Node/`fnm`, os dois SDKs, Inspector, Docker e hosts
  nos três SOs, com PATH, permissões, **proxy corporativo e CA interna**, desinstalação e
  14 erros literais; **15 exemplos completos**, treze executados, dois de produção).
  Núcleo do 10 ao 65 (fundamentos → história revisão a revisão → arquitetura e as três
  fronteiras de confiança → JSON-RPC byte a byte → transportes → primitivas de servidor e
  de cliente → **MRTR** → versionamento e as duas eras → OAuth 2.1 → **segurança** →
  clientes e hosts → registry → extensões → **projeto de ferramentas** → produção →
  teoria avançada → estado da arte de 01/09/2026). 12 laboratórios, 38 armadilhas e
  12 mitos, custos com data e câmbio, cursos PT/EN/FR pesquisados na web, bibliografia
  com edições conferidas, ~110 termos no glossário.
- **Projeto-modelo:** `07-projeto-modelo/` — **`biblioteca-mcp`**: acervo e empréstimos,
  com domínio separado da camada MCP, **confirmação humana via MRTR** (o parâmetro
  resolvido não aparece no `inputSchema`, e há teste provando), transações com condição no
  `WHERE` contra concorrência, SQL parametrizado, conexão em `mode=ro` para leitura, teto
  duplo de linhas, e `Makefile` com o ciclo completo. **15 testes — 9 deles de caminho
  ruim ou de defesa** (ISBN inexistente, sem exemplar, mesmo leitor duas vezes, recusa do
  usuário, limite absurdo, injeção de SQL, e o parâmetro de confirmação que não pode vazar
  para o modelo).
- **Verificação:** SDK Python **`mcp` 2.1.1** e SDKs TypeScript
  **`@modelcontextprotocol/server`/`client` 2.0.0** instalados e executados de verdade
  (uv 0.12.7 / Python 3.12.14 / Node v24.18.0, Ubuntu 22.04.5, em 01/09/2026). **JSON-RPC
  cru capturado sobre stdio** (`server/discover`, `tools/list`, `tools/call`, ferramenta
  inexistente, erro `-32022`) — todo JSON marcado como "real" no curso veio daí.
  **Streamable HTTP exercitado com `curl`**: `200` com JSON, **`400` + `-32020`** por
  `Mcp-Name` ausente, **`403`** por `Origin` inválido. **Inspector 2.4.0** em modo CLI.
  Projeto-modelo: `uv sync` + **15/15 testes aprovados em 3,96 s**. Quatro descobertas de
  campo registradas no curso (só `ToolError` entrega a mensagem ao modelo; retorno `dict`
  não gera `outputSchema`; `NoBackChannelError` no `ctx.elicit()`; `camelCase` no fio ×
  `snake_case` no objeto Python). Especificação, changelogs das cinco revisões, roadmap de
  22/08/2026, licenças, preços, câmbio e cursos pesquisados na web em 01/09/2026.
- **Pendente:** as seções de **macOS e Windows** do `03-instalacao.md` não foram
  executadas nesta máquina (estão marcadas com ⚠️; os comandos vêm da documentação
  oficial). O **fluxo completo de OAuth** do `18-autorizacao.md` não foi exercitado —
  exige um servidor de autorização real. A **publicação no MCP Registry** do
  `21-registro-e-distribuicao.md` não foi executada — exige conta e pacote publicado.
  **Revisar `65-estado-da-arte.md` a cada 3 meses** (o roadmap prevê redesenho de
  `tools/call`, descoberta progressiva e HTTP/2 sobre stdio, todos capazes de quebrar
  servidores); `80-custos-e-licencas.md` e `03-instalacao.md` a cada 6 meses. **Revisão
  geral em 28/07/2027**, quando termina a janela de doze meses de Roots, Sampling,
  Logging e HTTP+SSE.
- *Última atualização: 01/09/2026*

---

### [pentest](pentest/00-MAPA.md)
**Pentest** — teste de intrusão, de invasão, *penetration test*: o serviço profissional de
atacar um sistema **com autorização por escrito** para descobrir, provar e documentar como
ele quebra. Complementa [`ethical-hacking`](ethical-hacking/00-MAPA.md) sem repeti-lo: aqui o
foco é **o engajamento contratado** — escopo, *Rules of Engagement*, cadeia de custódia de
evidência, classificação de risco com CVSS 4.0 + EPSS + KEV, o **relatório como produto**,
reteste, conformidade (PCI DSS 11.4, LGPD, DORA/TIBER-EU) e a economia do setor. Do "arrombador
contratado" para leigos ao teorema de Rice, passando pela fronteira de 2026: agentes autônomos
de IA, PTaaS e CTEM.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 38 documentos + projeto-modelo executável, ~5.700 linhas. Bloco A completo
  (laboratório por SO — Kali 2026.2, VirtualBox/VMware/KVM/UTM, rede isolada, Docker, Burp,
  ferramentas Python/Go, com PATH, permissões, proxy corporativo, desinstalação e ~20 erros
  literais; 14 exemplos, dois deles casos reais de bug bounty e pentest interno). Núcleo do 10
  ao 65 (fundamentos → história → **lei/contrato/ética** (art. 154-A) → **escopo e
  pré-engajamento** → metodologias (PTES/NIST/OWASP/ATT&CK) → recon → varredura → análise →
  exploração → pós-exploração → web/API → rede/AD → nuvem → mobile → engenharia social/red team
  → **evidência** → **classificação de risco** → **relatório** → **reteste** → **conformidade** →
  gestão de equipe → carreira → teoria (Rice) → estado da arte de 01/09/2026). 14 laboratórios,
  28 armadilhas + 12 mitos, custos com data e câmbio, cursos PT/EN/FR pesquisados na web,
  bibliografia e referências verificadas, ~90 termos no glossário.
- **Projeto-modelo:** `07-projeto-modelo/` — **um engajamento inteiro**: `escopo-e-roe.md`
  (contrato), `alvo/app.js` (app vulnerável, Node, zero deps, 6 vulns comentadas), `roteiro.md`
  (plano mapeado ao PTES), `testar.js` (runner que explora, **prova e grava evidência**,
  zero deps) e `relatorio-exemplo.md` (o produto: sumário executivo → achados → remediação).
- **Verificação:** projeto rodado ponta a ponta (Node v24.18.0) — o runner explora as 6
  vulnerabilidades (2 críticas, 2 altas, 1 média, 1 baixa) e gera `resumo.json` + 6 arquivos de
  evidência reproduzível. Versões (Kali 2026.2, Nmap 7.99, Metasploit 6.5.2, Nuclei v10.4.3,
  BloodHound CE 9.5, Burp 2026.x), normas (PCI DSS 4.0.1, CVSS 4.0, DORA/TIBER-EU), preços
  (OSCP/CPTS/PNPT, Burp/Nessus, mercado BR) e cursos PT/EN/FR pesquisados na web em 01/09/2026.
- *Última atualização: 01/09/2026*

---

### [streamlit](streamlit/00-MAPA.md)
Como transformar um script Python numa aplicação web — e como fazer isso **bem**.
Nasceu de duas perguntas: *como fazer um dashboard profissional* e *como fazer um site
funcional com backend*. Da analogia da planilha ao modelo formal `V : S → T`, passando pelo
modelo de rerun (a ideia central, da qual tudo o mais é consequência), cache e isolamento
entre usuários, layout e KPIs que informam, paleta **validada** contra daltonismo, backend
com migração e transação, autenticação OIDC com papéis em duas camadas, testes sem
navegador, e deploy atrás de proxy com WebSocket.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 35 documentos + projeto-modelo executável. Bloco A completo (manual de
  instalação cobrindo Python/uv/venv/conda, Streamlit e seus extras, editor, Git, Docker e
  banco nos três sistemas operacionais, com PATH, permissões, proxy corporativo,
  desinstalação e 18 erros literais; **12 exemplos executados**, dois deles casos de
  produção). Núcleo do 10 ao 65 (fundamentos → história → **modelo de execução** →
  session_state e identidade de widget → cache → fragments → **layout e KPIs** →
  **gráficos e validação de cor** → tabelas → multipágina → tema → **backend/banco** →
  **autenticação e papéis** → **arquitetura em camadas** → tarefas longas → componentes →
  arquivos → streaming e chat → **deploy** → **segurança** → **testes** → **quando não
  usar** → teoria avançada → estado da arte de 02/09/2026). 14 laboratórios,
  28 armadilhas + 14 mitos + 12 más práticas, custos com data e câmbio, cursos PT/EN/FR
  pesquisados na web, bibliografia com ISBN conferido, ~85 termos no glossário.
- **Projeto-modelo:** `07-projeto-modelo/` — **Painel Comercial**: painel executivo com KPIs
  comparados e gráficos + CRUD completo de pedidos + edição em lote de clientes + página de
  administração com importação tudo-ou-nada e auditoria. `nucleo/` **não importa
  `streamlit`** (é o que torna a regra de negócio testável e reaproveitável): migração
  versionada, transação, PBKDF2 com comparação em tempo constante, SQL 100% parametrizado
  com lista branca para nomes de coluna, dinheiro em centavos inteiros. Tema com barra
  lateral escura, filtros ligados à URL (`bind="query-params"`), Dockerfile com usuário sem
  privilégio e `HEALTHCHECK`.
- **Verificação:** **43/43 testes executados e aprovados** (27 do núcleo em pytest puro +
  16 da interface com `AppTest`, sem navegador); servidor levantado e `/_stcore/health`
  respondendo; banco populado com 4.000 pedidos determinísticos. Assinaturas de API
  extraídas por `inspect.signature` do pacote **1.63.0 instalado** (não da documentação);
  endpoints do servidor testados com `curl`. A paleta original **reprovou** num validador de
  daltonismo (vermelho × verde, ΔE 1,4 em deuteranopia) e a correção está documentada como
  estudo de caso. Um **defeito da 1.63.0 foi encontrado e isolado**
  (`AppTest.date_input().set_value()` é no-op). Preços, cursos e livros pesquisados na web em
  02/09/2026.
- *Última atualização: 02/09/2026*

---

### [engenharia-reversa](engenharia-reversa/00-MAPA.md)
Como um programa executável guarda segredos, e como um humano recupera a lógica que o
compilador escondeu. Da analogia do bolo/receita à descompilação neural com LLM (2026).
Assembly x86-64 e ARM64 do zero, formatos ELF/PE/Mach-O byte a byte, análise estática
(desmontar/descompilar) e dinâmica (GDB/Frida/tracing), a pilha e as convenções de chamada,
estruturas de dados no binário (struct/vtable/C++), ofuscação/packers e anti-análise,
análise de malware, caça a vulnerabilidades (ROP/fuzzing), firmware e mobile, execução
simbólica e os limites teóricos (indecidibilidade), e a linha legal (Lei 9.609/98 omissa no
Brasil, DMCA §1201, Diretiva 2009/24/CE).

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** 33 documentos + projeto-modelo executável. Bloco A completo (manual de
  instalação cobrindo GCC/GDB/binutils, Ghidra/Java 21, radare2/rizin/Cutter, IDA Free,
  Frida, x64dbg, jadx/apktool/dnSpy, binwalk/QEMU e a família Python de RE — Capstone/angr/
  pwntools/LIEF — nos três sistemas operacionais, com PATH, permissões, venv, proxy,
  desinstalação e tabela de erros literais; alternativa sem instalar nada com godbolt/dogbolt;
  12 exemplos completos, dois de produção). Núcleo do 10 ao 65 (fundamentos → história →
  **arquitetura e assembly** → formatos de binário → estática → dinâmica → **pilha e
  convenções** → estruturas de dados → ofuscação/packers → anti-análise → malware →
  vulnerabilidades → firmware → mobile/managed → teoria avançada → estado da arte de
  03/09/2026). 12 laboratórios, 12 erros + 10 mitos + 6 más práticas, custos com data e
  câmbio (IDA/Binary Ninja/GREM/OSED), cursos PT/EN/FR pesquisados na web, bibliografia
  comentada (Yurichev gratuito), ~120 termos no glossário.
- **Projeto-modelo:** `07-projeto-modelo/` — **crackme de 3 níveis** (senha em texto claro →
  XOR de byte único → serial validado por regras, estilo licença) + **solucionador
  automático em Python** que resolve os três sozinho, ilustrando três técnicas reais
  (string harvesting, ataque de chave XOR e busca por restrições), com o **binário como
  oráculo** (funciona até no binário *stripped*). Compila em 3 variantes (`-g`, stripped,
  `-O2 -s`) para o aluno ver como símbolos e otimização mudam a dificuldade. `SOLUCAO.md`
  traz o gabarito à mão com **desmontagem real** (incl. o `imul 0x92492493` = `% 7`).
- **Verificação:** **make check com 21 asserções + solver 3/3 em duas variantes, tudo
  aprovado** (Ubuntu 22.04, GCC 11.4, GDB 12.1, Python 3.10, binutils 2.38). Solver
  cronometrado em ~6 s, confirmado no binário sem símbolos. Versões de ferramentas (Ghidra
  12.1.3, radare2 6.2.0, Frida 17.17.0, JDK 21), preços (hex-rays, Binary Ninja, SANS/OffSec)
  e cursos pesquisados na web em 03/09/2026.
- *Última atualização: 03/09/2026*

---

<!--
Formato de cada entrada:

### [nome-do-assunto](nome-do-assunto/00-MAPA.md)
Descrição em uma a três linhas.

| A | B | C | D | E | Glossário |
|---|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- **Feito:** …
- **Pendente:** …
- *Última atualização: DD/MM/AAAA*
-->
