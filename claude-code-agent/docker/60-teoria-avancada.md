# 60 · Teoria avançada — limites, provas e resultados formais

`Nível: pesquisa` · `Última atualização: 11/08/2026`

Este arquivo trata do que **não pode** ser feito e do que **custa quanto**, com o rigor que a
literatura permite. Containers são engenharia de sistemas, não um campo com teoremas próprios —
mas se apoiam em resultados formais de três áreas: **teoria do escalonamento**, **isolamento de
desempenho** e **segurança de sistemas**.

Onde não há resultado formal, o texto diz isso explicitamente, em vez de emprestar autoridade
matemática a uma prática de engenharia.

---

## 1. Agendamento de containers é NP-difícil

**O problema:** dado um conjunto de containers, cada um com uma demanda de recursos em várias
dimensões (CPU, memória, disco, rede), e um conjunto de máquinas com capacidades, aloque os
containers minimizando o número de máquinas usadas.

Isso é **empacotamento vetorial** (*vector bin packing*), a generalização multidimensional do
*bin packing*.

**Resultado 1 — o problema é NP-difícil.** Já o *bin packing* unidimensional está entre os 21
problemas NP-completos de Karp (1972), por redução a partir do *partition*. A versão vetorial
o contém como caso particular.

**Resultado 2 — nem aproximar é fácil.** Para *bin packing* unidimensional, não existe algoritmo
de aproximação com razão melhor que 3/2 a menos que P = NP (segue diretamente da NP-completude
do *partition*: decidir se 2 caixas bastam já é NP-completo). Para a versão *d*-dimensional, os
melhores limites conhecidos de inaproximabilidade crescem com a dimensão — a dificuldade
**aumenta** com o número de recursos considerados simultaneamente.

**Resultado 3 — heurísticas simples são boas na prática.** *First Fit Decreasing* garante, no
caso unidimensional, no máximo `11/9 · OPT + 6/9` caixas (Dósa, 2007, refinando o limite clássico
de Johnson). É por isso que schedulers reais usam heurísticas gulosas com pontuação, não solução
ótima.

**Consequência prática:** o scheduler do Kubernetes não busca o ótimo. Ele filtra nós viáveis
(*predicates*) e pontua os que sobraram (*priorities*), escolhendo o melhor da amostra. É uma
decisão consciente de trocar otimalidade por latência de decisão — em um cluster de milhares de
nós, tomar a decisão em milissegundos vale mais que economizar 3% de máquinas.

E é por isso que **`requests` importa mais que `limits`**: o `requests` é a entrada do
empacotamento. Pedir menos do que se usa quebra a premissa do algoritmo e produz nós
sobrecarregados enquanto o scheduler ainda os considera livres.

---

## 2. Isolamento de desempenho: o resultado negativo

**A pergunta formal:** cgroups garantem que um container não afete o desempenho de outro?

**A resposta é não**, e é demonstrável. cgroups particionam recursos **contabilizáveis** (ciclos
de CPU, páginas de memória, IOPS). Não particionam recursos **compartilhados e não
contabilizados**:

| Recurso compartilhado | Por que não é particionável | Efeito observável |
|---|---|---|
| Cache L3 da CPU | Compartilhado entre núcleos; sem contabilidade por processo | *Noisy neighbor*: um container que varre memória despeja o cache dos outros |
| Largura de banda de memória | Barramento único | Vazão cai para todos |
| TLB | Compartilhado | Mais *page walks* |
| Filas do controlador de disco | Reordenação no dispositivo | Latência de I/O imprevisível |
| Buffers do NIC, cache ARP | Compartilhados no kernel | Perda de pacote sob rajada |
| Locks e estruturas do kernel | Globais por definição | Contenção em `mmap_sem`, `inode` locks |
| Entropia (`/dev/random`) | Pool compartilhado | Bloqueio em geração de chave |

**Mitigações parciais existem, e são de hardware:** Intel RDT/CAT (*Cache Allocation
Technology*) e AMD QoS permitem particionar o cache L3 por classe de serviço. Isso é
raramente usado fora de operadores de nuvem, porque exige suporte de hardware, configuração de
BIOS e integração no orquestrador.

**A afirmação correta, portanto, é:** *cgroups fornecem isolamento de desempenho para recursos
contabilizáveis, sob a hipótese de que os recursos não contabilizados não estão saturados.* Essa
hipótese é rotineiramente violada em produção — e é a origem da maior parte das anomalias de
latência que "não aparecem nas métricas".

---

## 3. O throttling de CFS: um problema quantificável

O Linux implementa o limite de CPU via *CFS bandwidth control*: uma **cota** (`cpu.max`) a cada
**período** (100 ms por padrão). Esgotada a cota, todas as threads do cgroup são suspensas até o
próximo período.

**A consequência formal.** Seja `Q` a cota por período `P`, e `n` o número de threads
executáveis. Se as `n` threads rodam em paralelo, a cota é consumida em `Q/n` unidades de tempo
de parede. O container fica suspenso por:

```
    tempo_suspenso = P − Q/n
```

Para `Q = 100 ms`, `P = 100 ms` (`--cpus 1.0`) e `n = 8` threads: a cota se esgota em 12,5 ms e
o container fica **87,5 ms parado** em cada período de 100 ms.

**O resultado é contraintuitivo:** um container com `--cpus 1.0` e 8 threads pode ter latência
de cauda **muito pior** que o mesmo container com 1 thread, mesmo consumindo a mesma CPU total.
Foi esse fenômeno que motivou uma série de correções no kernel (a partir da 5.14, com melhor
distribuição das fatias entre CPUs) e a recomendação, hoje comum, de **não impor limite de CPU**
em cargas latência-sensíveis.

```bash
# Meça no seu ambiente
CG=/sys/fs/cgroup/system.slice/docker-$(docker inspect -f '{{.Id}}' NOME).scope
cat $CG/cpu.stat
# nr_periods, nr_throttled, throttled_usec
# throttled_usec / (nr_periods * 100000) = fração do tempo suspenso
```

**A mitigação estrutural** é alinhar o paralelismo interno da aplicação à cota:
`GOMAXPROCS` (Go), `-XX:ActiveProcessorCount` (JVM), `UV_THREADPOOL_SIZE` (Node),
`OMP_NUM_THREADS` (OpenMP). Bibliotecas como `automaxprocs` fazem isso lendo o cgroup.

---

## 4. Limites de isolamento de segurança

### O argumento de superfície de ataque

Formalize a superfície como o conjunto de pontos de entrada acessíveis ao adversário:

| Modelo | Superfície aproximada |
|---|---|
| Container (runc) | **~350 syscalls** do Linux, menos as ~40 bloqueadas por seccomp → ~310 |
| gVisor | ~20 syscalls do host (o Sentry implementa o resto em espaço de usuário) |
| Micro-VM (Firecracker) | ~5 dispositivos virtio + a interface KVM |
| Processo comum sem container | ~350 syscalls, sem restrição adicional |

Isso não é um teorema: número de syscalls **não** é medida rigorosa de risco (uma syscall
explorável pesa mais que cem seguras). Mas é a métrica que a literatura de segurança de sistemas
usa como proxy, e a diferença de ordem de grandeza entre container e micro-VM é real e
consistente com o histórico de CVEs.

### O que a história das vulnerabilidades mostra

Escapes documentados de container concentram-se em três categorias, e a distribuição é
informativa:

1. **Bugs de kernel** — `waitid` (CVE-2017-5123), Dirty COW (CVE-2016-5195), `io_uring` em
   diversos anos. **Container não protege**: o kernel é a fronteira, e ela é compartilhada.
2. **Bugs do runtime** — o caso canônico é **CVE-2019-5736**, no `runc`: um container
   conseguia sobrescrever o binário `/proc/self/exe` do próprio runc no host, obtendo execução
   como root na próxima invocação. A correção foi clonar o binário para memória a cada execução.
3. **Configuração errada** — `--privileged`, socket montado, bind mount de `/`. **É a categoria
   mais comum na prática**, e é inteiramente evitável.

**A conclusão defensável:** a categoria 3 domina a estatística de incidentes reais. Investir em
higiene de configuração tem retorno maior que investir em runtime exótico — até o ponto em que
o modelo de ameaça inclua adversário hostil com código arbitrário, quando (1) passa a dominar e
a micro-VM se torna necessária.

### O limite fundamental

> **Teorema informal do isolamento compartilhado:** se dois domínios de execução compartilham um
> componente de confiança (o kernel), então o isolamento entre eles é no máximo tão forte quanto
> a corretude desse componente.

Isso não é um resultado profundo — é quase uma tautologia. Mas é a formulação que torna a
decisão de arquitetura óbvia: **se você não confia na corretude do kernel para o seu modelo de
ameaça, containers não são a resposta.** É exatamente por isso que AWS Lambda, Google Cloud Run
e Fly.io colocam containers dentro de micro-VMs: eles executam código arbitrário de terceiros
desconhecidos.

---

## 5. Custo teórico do copy-on-write

O OverlayFS faz CoW **em granularidade de arquivo**, não de bloco.

Seja `S` o tamanho do arquivo e `k` o número de bytes escritos. O custo da primeira escrita é:

```
    C_primeira(S, k) = O(S)      — copia o arquivo inteiro para a camada superior
    C_seguintes(k)   = O(k)      — escreve direto na cópia
```

**Consequência quantificada:** escrever 1 byte no meio de um arquivo de 1 GB custa 1 GB de I/O.
Para um banco de dados que atualiza páginas de 8 KB dentro de arquivos de gigabytes, o custo é
proibitivo — e é a razão formal, não folclórica, para "nunca coloque banco de dados na camada de
escrita".

Sistemas com CoW em granularidade de bloco (btrfs, ZFS) não têm esse problema: o custo é
`O(tamanho_do_bloco)`. É por isso que os drivers `btrfs` e `zfs` do Docker existem, e por que
alguns operadores os preferem apesar da complexidade adicional.

**Custo de leitura em função da profundidade.** Numa pilha de `L` camadas, resolver um caminho
exige, no pior caso, `L` consultas de metadados até encontrar o arquivo (ou o whiteout que o
esconde). O OverlayFS mitiga com cache de dentry, mas o pior caso permanece `O(L)` — o que
sustenta a recomendação empírica de manter as imagens abaixo de algumas dezenas de camadas.

---

## 6. Deduplicação: o ganho é combinatório

Seja um conjunto de `n` imagens, cada uma com `m` camadas, sobre um universo de `U` camadas
distintas. O armazenamento com endereçamento por conteúdo é:

```
    Espaço = Σ_{c ∈ U} tamanho(c)      — cada camada guardada UMA vez
```

em vez de `Σ_{i=1..n} Σ_{j=1..m} tamanho(c_ij)`.

O fator de economia é `(n·m)/|U|` — o **grau médio de compartilhamento**. Concretamente: 50
microserviços sobre a mesma `node:22-alpine` armazenam essa base uma vez em vez de 50 vezes.
Com 50 MB de base, são 2,45 GB economizados **por host**, e o mesmo fator na banda de rede a
cada pull.

**O corolário operacional é forte:** padronizar a imagem base numa organização não é preferência
estética; é uma decisão com efeito multiplicativo mensurável em disco, banda e tempo de deploy.
E é o argumento formal a favor das *golden base images* corporativas.

---

## 7. Tempo de partida: a análise

```
   T_total = T_pull + T_extração + T_setup + T_processo
```

| Termo | Ordem de grandeza | Depende de |
|---|---|---|
| `T_pull` | 0 (cache local) a dezenas de segundos | Tamanho e banda |
| `T_extração` | 100 ms – vários segundos | Tamanho, CPU (descompressão), I/O |
| `T_setup` | **1–10 ms** | Criação de namespaces, cgroups, rede |
| `T_processo` | ms a minutos | A aplicação (JVM é o caso patológico) |

**O termo que o container controla é `T_setup`, e ele é minúsculo.** "Containers iniciam em
milissegundos" é verdade sobre `T_setup` e falso sobre `T_total` na primeira execução.

Isso explica a direção da pesquisa:

- **Lazy pulling** (eStargz, SOCI, Nydus): iniciar o container **antes** de a imagem estar
  inteira no disco, buscando blocos sob demanda. Reduz `T_pull` + `T_extração` de dezenas de
  segundos para segundos em imagens grandes — o que se tornou crítico com imagens de IA de
  vários gigabytes.
- **Snapshot/restore de VM** (Firecracker): restaurar um processo já inicializado, eliminando
  `T_processo`. É como o AWS Lambda ataca o *cold start*.
- **Pré-aquecimento**: manter um conjunto de containers ociosos prontos. Troca custo por
  latência.

---

## 8. O modelo formal da OCI Runtime Spec

A especificação define um **bundle** como o par `(config.json, rootfs/)` e uma máquina de estados
com cinco estados e transições bem definidas:

```
   [creating] ──create──▶ [created] ──start──▶ [running] ──(processo sai)──▶ [stopped]
                                                    │                            │
                                                    └──────kill──────────────────┘
                                                                                 │
                                                                              delete
                                                                                 ▼
                                                                            (removido)
```

A especificação impõe obrigações verificáveis:

- `create` **deve** ser idempotente quanto ao ID (dois `create` com o mesmo ID falham).
- O estado **deve** ser consultável por `state`, retornando JSON com um esquema fixo.
- Hooks (`prestart`, `createRuntime`, `createContainer`, `startContainer`, `poststart`,
  `poststop`) **devem** executar em pontos definidos, e falha em hook **deve** abortar a operação.

**Por que isso é teoricamente relevante:** é um contrato suficientemente preciso para permitir
implementações independentes intercambiáveis. `runc`, `crun`, `youki`, `runsc` e `kata-runtime`
foram escritos por equipes diferentes, em linguagens diferentes, com modelos de isolamento
radicalmente diferentes — e são substituíveis sem alterar as camadas superiores. Essa é a mesma
propriedade que fez o TCP/IP e o POSIX terem sucesso: **a interface, não a implementação, é o
ativo duradouro**.

---

## 9. Problemas em aberto

| Problema | Estado em ago/2026 |
|---|---|
| **Isolamento de desempenho previsível sem hardware dedicado** | Aberto. RDT/CAT ajuda parcialmente; contenção de barramento de memória continua sem solução |
| **Verificação formal de perfis seccomp** | Pesquisa incipiente. Não há método prático para provar que um perfil é suficiente e mínimo para um dado binário |
| **Cold start abaixo de 1 ms com isolamento forte** | Firecracker chega a ~125 ms; isolados de V8 chegam a <1 ms mas só para JS/Wasm. A lacuna persiste |
| **Deduplicação semântica entre imagens** | Camadas dedupicam por hash exato. Dois `apt install curl` em bases distintas não compartilham nada, embora o conteúdo seja quase idêntico |
| **Ataques de canal lateral entre containers** | Mitigação em software é cara; separação física continua sendo a única resposta forte |
| **Reprodutibilidade bit a bit de builds** | `SOURCE_DATE_EPOCH` resolve timestamps; ordenação de arquivos, aleatoriedade em compiladores e resolução dinâmica de dependências continuam abertos |
| **Migração ao vivo de containers** | CRIU funciona em casos restritos; estado de rede, descritores abertos e memória compartilhada permanecem difíceis |

---

## 10. Leituras primárias

| Trabalho | Por que ler |
|---|---|
| Karp (1972), *Reducibility Among Combinatorial Problems* | A origem da NP-completude do bin packing |
| Johnson (1973), tese sobre *bin packing*; Dósa (2007) | Os limites de aproximação de First Fit Decreasing |
| Verma et al. (2015), *Large-scale cluster management at Google with Borg*, EuroSys | O sistema do qual o Kubernetes descende; a fonte primária sobre escalonamento em escala |
| Agache et al. (2020), *Firecracker: Lightweight Virtualization for Serverless Applications*, NSDI | O trade-off isolamento × cold start, quantificado |
| Young et al. (2019), *The True Cost of Containing: A gVisor Case Study*, HotCloud | Medição honesta da sobrecarga de gVisor |
| Harter et al. (2016), *Slacker: Fast Distribution with Lazy Docker Containers*, FAST | Mostrou que 76% do tempo de start é pull/extração e apenas 6,4% dos dados são lidos — a origem do lazy pulling |
| Menage (2007), *Adding Generic Process Containers to the Linux Kernel*, Linux Symposium | O artigo original dos cgroups |
| OCI Runtime Spec e Image Spec | As especificações; leitura curta e esclarecedora |

Referências completas em [95-referencias.md](95-referencias.md).

---

## Autoteste

1. Por que agendar containers é NP-difícil, e por que schedulers reais não buscam o ótimo?
2. Qual é a razão de aproximação de First Fit Decreasing, e por que isso justifica heurísticas
   gulosas?
3. Enuncie o resultado negativo sobre isolamento de desempenho e cite três recursos não
   particionáveis.
4. Deduza a fórmula do tempo suspenso por throttling e calcule para `--cpus 1.0` com 4 threads.
5. Por que "número de syscalls" é um proxy imperfeito de superfície de ataque, e por que ainda
   assim é usado?
6. Enuncie o teorema informal do isolamento compartilhado e derive dele uma decisão de
   arquitetura.
7. Qual é o custo assintótico da primeira escrita em CoW por arquivo, e como btrfs muda isso?
8. Deduza o fator de economia da deduplicação por conteúdo e aplique a 50 serviços com base
   comum de 50 MB.
9. Decomponha `T_total` de partida e diga qual termo o container realmente otimiza.
10. Cite três problemas em aberto e o que impede a solução de cada um.
