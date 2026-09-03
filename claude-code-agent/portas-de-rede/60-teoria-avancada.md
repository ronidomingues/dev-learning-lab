# 60 · Teoria avançada — limites, aritmética e provas

**Nível:** pesquisa · **Última atualização:** 14/08/2026

Este arquivo trata do que **não pode** ser feito, e por quê. Limites de recurso, limites de
informação, limites de decidibilidade. É a camada 11 da curva de profundidade do curso.

---

## 1. O espaço de portas como recurso finito

### A aritmética do esgotamento

Uma conexão TCP é identificada pela quádrupla. Para conexões **de saída** de uma máquina
para um **mesmo** serviço remoto, três dos quatro elementos são fixos:

```
( IP_origem , PORTA_origem , IP_destino , PORTA_destino )
   fixo        VARIÁVEL       fixo         fixo
```

Logo, o número máximo de conexões simultâneas para aquele destino é exatamente o **tamanho
da faixa efêmera**.

Medido nesta máquina:

```
$ cat /proc/sys/net/ipv4/ip_local_port_range
32768	60999          →  28.232 portas
```

Mas o limite real é pior, porque cada porta fica presa em `TIME_WAIT` por 60 s após o
fechamento:

```
        28.232 portas
  C =  ───────────────  ≈  470 conexões novas por segundo
          60 segundos
```

**470 conexões/s.** Não é um número teórico distante: é a taxa em que um serviço de API
razoavelmente carregado opera. Ao atingi-la, o sintoma é `EADDRNOTAVAIL` (errno 99) — e
nenhum recurso da máquina está no limite. Nem CPU, nem memória, nem banda.

### As formas de aumentar C, e quanto cada uma vale

| Ação | Novo C | Ganho | Custo |
|---|---|---|---|
| Baseline | 470/s | — | — |
| `ip_local_port_range = 10240 65535` | ~921/s | **1,96×** | Risco de colidir com serviços em portas altas |
| `tcp_tw_reuse = 1` | limitado pelo RTT, não pelo `TIME_WAIT` | **grande** | Seguro para saída |
| +1 IP de origem | 2× | **linear em IPs** | Custo de IP |
| +1 porta de destino (ex.: sharding) | 2× | linear | Complexidade de arquitetura |
| **Keep-alive / pool** | **ilimitado** | **elimina o problema** | Nenhum. É só fazer certo. |

**A conclusão profissional:** ajustar `sysctl` é adiar. A correção é **parar de abrir
conexão nova a cada requisição**. Um pool de 50 conexões persistentes serve dezenas de
milhares de requisições por segundo usando 50 portas.

Todo ajuste de `sysctl` nessa área deve ser lido como o que é: um paliativo enquanto se
conserta a aplicação.

### Por que isso é, na raiz, um problema de 1980

O campo de porta tem 16 bits porque, em 1980, cada bit no cabeçalho custava tempo de
transmissão em enlaces de 50 kbit/s. A decisão foi correta para o contexto. Ela não pode ser
revista porque mudar o formato do cabeçalho TCP quebra compatibilidade com toda a internet —
a impossibilidade estabelecida em 1º de janeiro de 1983.

**Esta é uma parada legítima da regra dos cinco porquês:** um trade-off econômico explícito
entre o custo de transição e o benefício, resolvido em favor da compatibilidade.

O QUIC contorna, não resolve: ele identifica conexões por *connection ID* em vez da
quádrupla, o que remove o acoplamento à porta. Mas o UDP subjacente ainda tem 16 bits.

---

## 2. Entropia da porta de origem — quanto vale a aleatoriedade

Um atacante *fora do caminho* (*off-path*) que queira injetar dados numa conexão TCP alheia
precisa acertar **simultaneamente**:

| Campo | Bits de incerteza |
|---|---|
| Porta de origem | até ~15 (na prática, menos) |
| Número de sequência | 32 |
| **Total** | **~47** |

O espaço é grande — mas não infinito, e a história mostra que ele foi explorado.

### O ataque que motivou tudo

Nos anos 2000, sessões **BGP** entre roteadores usavam TCP e eram alvo de ataques de reset:
bastava forjar um RST com sequência dentro da janela para derrubar a sessão. Como as janelas
TCP são grandes, "dentro da janela" é bem mais fácil que "exatamente igual". Derrubar sessões
BGP significa desestabilizar o roteamento da internet.

A resposta foi em três frentes:

- **RFC 5961** (2010) — endurecimento das regras de aceitação de RST e SYN;
- **RFC 6056** (2011) — algoritmos de **aleatorização de porta de origem**;
- **TCP-AO / TCP-MD5** — autenticação criptográfica dos segmentos BGP.

O RFC 6056 descreve cinco algoritmos, com trade-offs entre entropia e reuso. A recomendação
converge para o **algoritmo 3** (*double-hash*): a porta é uma função de hash da quádrupla
mais um segredo, o que dá boa imprevisibilidade **sem** repetir a mesma porta para o mesmo
destino em curto intervalo.

### O caso paralelo, mais famoso: DNS

Em 2008, Dan Kaminsky mostrou que envenenar o cache de um resolvedor DNS era prático:
o atacante só precisava acertar um ID de transação de **16 bits** antes da resposta legítima
chegar. Com paralelismo, minutos.

A correção emergencial, coordenada globalmente, foi **aleatorizar também a porta de origem
UDP**, elevando a incerteza de 16 para ~32 bits.

> **A lição geral:** a porta de origem, que parece um detalhe de implementação sem
> importância, é um **componente de segurança**. Um sistema que a escolha
> sequencialmente — ou que sempre use a mesma — está criando uma vulnerabilidade que não
> aparece em nenhuma varredura.

Verificação prática: abra várias conexões e observe se as portas de origem são sequenciais.
No Linux moderno, não são.

---

## 3. Limites teóricos da varredura

### O problema fundamental: inferência sob incerteza

Uma varredura de portas não *lê* um estado. Ela **infere** um estado a partir de um
comportamento observado, num canal que perde e reordena mensagens.

Formalmente, você observa uma resposta `r` e quer inferir o estado `s ∈ {aberta, fechada,
filtrada}`. O canal introduz:

- **perda** — sua sonda ou a resposta podem sumir;
- **atraso** — a resposta pode chegar após o seu timeout;
- **adulteração ativa** — um firewall pode forjar RST, um honeypot pode forjar SYN-ACK.

**Consequência 1 — nenhum resultado é conclusivo em uma única sonda.** É por isso que o
`nmap` retransmite, e por que `--max-retries 0` troca velocidade por falsos negativos.

**Consequência 2 — na presença de um adversário ativo, o problema é indecidível.** Um alvo
que responde SYN-ACK em **todas** as portas (um *tarpit*, ou o LaBrea de 2001) faz uma
varredura reportar 65 535 portas abertas. Nenhum algoritmo distingue isso de uma máquina que
realmente tem tudo aberto, **porque a única evidência disponível é exatamente a mesma**.

Isto não é uma limitação da ferramenta. É uma consequência de o observador só ter acesso ao
canal.

**Consequência 3 — o resultado é uma medição, com data e validade.** Uma varredura diz o que
era verdade naquele instante, daquele ponto de vista. Relatório de varredura sem carimbo de
tempo e sem origem declarada é de utilidade limitada.

### O paradoxo dos dois generais

O handshake de três vias existe porque o problema abaixo é **provadamente insolúvel**:

> Dois generais em colinas opostas precisam atacar simultaneamente. Só podem se comunicar
> por mensageiros que atravessam o vale inimigo e podem ser capturados. **Não existe
> protocolo, com número finito de mensagens, que garanta acordo.**

Prova por contradição: suponha um protocolo mínimo com `n` mensagens. A última mensagem não
pode ser essencial — quem a enviou não sabe se ela chegou, então precisa poder agir sem
confirmação dela. Logo existe um protocolo com `n-1` mensagens. Por indução, `n = 0`, o que
é absurdo.

**A consequência para o TCP:** não existe "conexão estabelecida com certeza mútua". Três vias
é o mínimo para que **cada lado saiba que seu número de sequência inicial foi recebido** —
o que basta na prática, mas não é certeza absoluta e nunca poderá ser.

É a razão de existir `TIME_WAIT` (a última mensagem pode se perder e precisa poder ser
retransmitida) e de o fechamento de conexão TCP ser notoriamente sutil.

### FLP e o que ele diz sobre o resto

O resultado de **Fischer, Lynch e Paterson (1985)** prova que, num sistema assíncrono com um
único processo que pode falhar, **não existe algoritmo determinístico de consenso que sempre
termine**.

A relação com o nosso assunto é direta: você **nunca** consegue distinguir, com certeza,
"o serviço caiu" de "o serviço está lento". Todo *health check* — todo balanceador, todo
Kubernetes — usa timeout, e timeout é um chute calibrado, não uma decisão correta.

É por isso que balanceadores derrubam serviços saudáveis sob carga, e é por isso que
"aumentar o timeout" e "diminuir o timeout" estão os dois errados: não há valor certo.

---

## 4. Complexidade da varredura

### Custo assintótico

Varrer `h` hosts × `p` portas é `O(h·p)` sondas. O tempo depende inteiramente do
paralelismo `k` e do timeout `t`:

```
T ≈ (h · p / k) · t_efetivo
```

Onde `t_efetivo` é:

- **microssegundos** para portas fechadas (chega RST na hora);
- **o timeout inteiro** para portas filtradas.

**Daí o comportamento observável:** uma varredura contra alvo sem firewall termina em
milissegundos; a mesma varredura contra alvo protegido leva minutos.

Medido neste material:

```
$ nmap -sT -Pn 127.0.0.1
Nmap done: 1 IP address (1 host up) scanned in 0.09 seconds     ← nada filtrado
```

### O teto do paralelismo

`k` não pode crescer indefinidamente:

| Limite | Onde bate |
|---|---|
| `ulimit -n` | `-sT` consome um descritor por sonda em voo |
| Tabela de conntrack | O firewall no caminho fica sem espaço |
| Banda | Sondas perdidas → falsos negativos |
| Detecção | IDS bloqueia você no meio do trabalho |

Existe um **ponto ótimo**: acima de certo `k`, a perda induzida obriga a retransmitir e o
tempo total **piora**. É por isso que `nmap -T5` frequentemente é mais lento e menos preciso
que `-T4` — a documentação do Nmap é explícita sobre isso e a maioria das pessoas ignora.

### O salto sem estado: `masscan` e `ZMap` (2013)

A restrição `k ≤ ulimit -n` desaparece se você **não guardar estado por sonda**.

O truque: codificar a identificação do alvo no próprio **número de sequência inicial** do
SYN enviado, como uma função hash com chave secreta:

```
ISN = HMAC(chave, IP_destino ‖ porta_destino)
```

Quando o SYN-ACK volta, seu campo de ACK é `ISN + 1`. O scanner recalcula o HMAC e verifica
se bate. **Zero memória por sonda.**

O resultado: os 4 bilhões de endereços IPv4 varridos numa porta em **dezenas de minutos**,
com uma máquina e um enlace de 10 Gbit/s. O ZMap foi apresentado na USENIX Security 2013.

**A consequência é permanente e vale enunciar:** desde 2013, **toda porta exposta à internet
é descoberta em minutos, continuamente, por vários atores independentes**. Qualquer modelo
de ameaça que suponha "vai levar tempo até me encontrarem" está errado desde então.

### E o IPv6 muda tudo

O espaço IPv4 tem 2³² ≈ 4,3 × 10⁹ endereços. Varrível.
Uma **única sub-rede** IPv6 típica (`/64`) tem 2⁶⁴ ≈ 1,8 × 10¹⁹ endereços.

Varrer uma `/64` a 10 milhões de sondas por segundo levaria cerca de **58 mil anos**.

**Varredura exaustiva de IPv6 é computacionalmente inviável.** A descoberta de alvos em IPv6
mudou de natureza: passou a depender de

- registros DNS e Certificate Transparency;
- endereços previsíveis (`::1`, `::80`, EUI-64 derivado do MAC);
- listas de *hitlists* coletadas passivamente;
- e tráfego observado.

Isto é uma mudança **qualitativa**, não quantitativa: em IPv6, "obscuridade" volta a ter
algum valor real — pela primeira vez desde 2013. É uma das poucas afirmações deste curso em
que segurança por obscuridade tem defesa técnica.

---

## 5. Teoria de filas aplicada ao backlog

A fila de `accept()` é uma fila M/M/1 clássica. Com chegada a taxa `λ` e serviço a taxa `μ`:

```
ρ = λ / μ                      utilização
L = ρ / (1 - ρ)                comprimento médio da fila
W = 1 / (μ - λ)                tempo médio de espera
```

**A consequência prática, que engenheiro nenhum deveria ignorar:** quando `ρ → 1`, `L → ∞`.
A fila não cresce linearmente com a carga — ela **explode** perto da saturação.

Um serviço a 80 % de utilização tem fila média de 4. A 95 %, de 19. A 99 %, de 99.
É por isso que sistemas parecem saudáveis e depois colapsam de repente: a região perigosa é
estreita.

**E isso é observável em um comando:**

```bash
ss -tln        # a coluna Recv-Q numa linha LISTEN É o L desta fórmula
```

Medido no experimento do [`13-tcp-por-dentro.md`](13-tcp-por-dentro.md):

```
State  Recv-Q Send-Q Local Address:Port
LISTEN 3      2          127.0.0.1:46189
```

`Recv-Q 3` com `Send-Q 2`: fila cheia, e as conexões seguintes foram descartadas em
silêncio. `ρ` era efetivamente infinito, porque `μ = 0` — ninguém chamava `accept()`.

**Dimensionar backlog é escolher o comportamento sob sobrecarga:** backlog grande absorve
rajadas mas aumenta a latência de cauda (a conexão espera em vez de falhar); backlog pequeno
falha rápido e permite ao cliente tentar outro servidor. Não há resposta universal — há uma
decisão de projeto que deveria ser consciente e quase nunca é.

---

## 6. O limite da inspeção: teorema de Rice

Fecha o assunto com o limite mais fundamental de todos.

> **Teorema de Rice (1953):** toda propriedade não-trivial da *função* computada por um
> programa é indecidível.

Aplicado ao nosso tema: **não existe algoritmo que decida, para todo serviço, qual protocolo
ele fala.**

O `nmap -sV` funciona por **heurística**: manda sondas conhecidas e casa respostas contra
padrões conhecidos. Funciona muito bem na prática porque os serviços do mundo real são
poucos e bem-comportados. Mas é impossível, em geral:

- um serviço pode falar HTTP nos primeiros 100 pedidos e SSH depois;
- pode responder conforme o IP de origem (é o que um *honeypot* faz);
- pode exigir um segredo antes de revelar qualquer coisa (*port knocking*, SPA).

**Corolários operacionais:**

1. Nenhum inventário de serviços é completo por construção — apenas *bom o bastante*.
2. Não existe firewall de aplicação perfeito. Todo DPI é heurística; toda heurística tem
   falso positivo e falso negativo.
3. A defesa não pode se basear em identificar corretamente o que passa. Precisa se basear em
   **negar por padrão** e permitir por exceção explícita.

O mesmo teorema aparece no assunto [`agentes-de-ia`](../agentes-de-ia/00-MAPA.md) desta pasta,
e em [`ethical-hacking`](../ethical-hacking/00-MAPA.md). Não é coincidência: é o limite
externo de qualquer análise automatizada de comportamento de programa.

---

## 7. Problemas em aberto

1. **Como fazer descoberta de ativos em IPv6 em escala?** A varredura exaustiva morreu.
   As alternativas atuais (DNS, CT, hitlists) são incompletas e enviesadas. Área ativa de
   pesquisa.

2. **Como observar rede com QUIC sem quebrar a criptografia?** Operadores perderam
   visibilidade que usavam para engenharia de tráfego legítima. As propostas de "sinais
   explícitos" (bit de *spin*, por exemplo) são um compromisso desconfortável entre
   privacidade e operabilidade, e não há consenso.

3. **A quádrupla vale a pena como identidade?** QUIC já abandonou. Se a identidade de fluxo
   migrar para um identificador criptográfico, toda a instrumentação de rede construída
   sobre `(IP, porta)` — netflow, conntrack, ACLs — precisa ser repensada.

4. **Esgotamento de porta em escala de nuvem.** NATs de operadora precisam multiplexar
   milhares de assinantes sobre poucos IPv4 — e mantêm tabelas de tradução gigantes.
   É um limite estrutural do IPv4 que só o IPv6 resolve.

5. **Dimensionamento automático de backlog.** Continua sendo escolhido por chute em quase
   todo lugar. Um controlador que ajuste `somaxconn` a partir da latência de cauda observada
   é ideia antiga e ainda pouco implementada.

---

## Autoteste

1. Deduza, do zero, o número máximo de conexões novas por segundo para um mesmo destino,
   dada a faixa efêmera e a duração do `TIME_WAIT`. Faça a conta para `10240–65535`.
2. Por que ampliar `ip_local_port_range` é um paliativo e keep-alive é a correção?
3. Por que a porta de origem precisa ser imprevisível? Cite o ataque histórico que motivou
   a exigência, em TCP e em DNS.
4. Enuncie o paradoxo dos dois generais e explique por que ele implica que o handshake TCP
   não dá certeza absoluta.
5. Por que `nmap -T5` pode ser mais lento e menos preciso que `-T4`? Use o modelo de tempo
   da seção 4.
6. Explique o truque de estado zero do `masscan`/`ZMap`. Que consequência permanente ele
   teve para modelagem de ameaças?
7. Por que varredura exaustiva de IPv6 é inviável? Faça a estimativa de tempo. Em que isso
   muda o valor da obscuridade?
8. Numa fila M/M/1, por que a fila explode perto de `ρ = 1`? Em qual coluna do `ss` você
   observa isso?
9. O que o teorema de Rice implica sobre a identificação automática de serviços? Enuncie os
   três corolários operacionais.
10. Escolher o tamanho do backlog é escolher o quê, exatamente, sob sobrecarga?

---

*Próximo: [`65-estado-da-arte.md`](65-estado-da-arte.md) — onde está a fronteira em ago/2026.*
