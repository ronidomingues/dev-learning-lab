# 60 · Teoria avançada — os limites que decidem o tamanho de uma rede

> **Nível:** pesquisa
> **Data:** 14/08/2026
> Aqui o assunto encontra a matemática. Por que endereços são dois, por que o broadcast decide o
> teto de camada 2, e por que nenhum protocolo desse tipo pode ser seguro, sem estado e sem
> infraestrutura ao mesmo tempo.

---

## 1. Por que dois espaços de endereço são teoricamente necessários

O IP é **hierárquico** (agregável); o MAC é **plano** (não agregável). Isto não é acidente de
implementação — é uma necessidade de teoria da informação sobre roteamento.

Um roteador precisa decidir o próximo salto olhando o endereço de destino. Se os endereços forem
planos (sem estrutura), a tabela de roteamento precisa de **uma entrada por destino** — tamanho
Θ(N) para N destinos. Com N ≈ 5×10¹⁰ dispositivos já fabricados, isso é impossível na memória de
um roteador.

A hierarquia permite **agregação de prefixos** (CIDR): "tudo que casa com `10.209.0.0/20` vai
por aqui" — uma entrada cobre 4094 destinos. A tabela encolhe para Θ(número de prefixos), que
cresce muito mais devagar que Θ(N). A tabela BGP global tem ~1 milhão de prefixos em 2026 para
bilhões de destinos — a agregação é o que torna a Internet computável.

Mas o MAC **não pode** ser hierárquico: ele identifica hardware fabricado independentemente, sem
coordenação de localização. Um endereço não pode ser ao mesmo tempo (a) atribuído de fábrica sem
saber onde o dispositivo vai operar e (b) hierárquico por localização. **Logo, dois espaços são
necessários** — um agregável para rotear, um plano para identificar — e algo tem de traduzir
entre eles no último salto. Esse algo é o ARP.

> **Parada legítima (lei/estrutura matemática):** a impossibilidade de um único endereço ser
> simultaneamente "estável de fábrica" e "hierárquico por localização" é o motivo teórico de o
> ARP existir. Não é escolha de engenharia; é consequência de o roteamento escalável exigir
> agregação e a identificação de hardware exigir estabilidade.

---

## 2. O custo do broadcast: modelo formal

Seja um domínio de broadcast (segmento) com **N** hosts. Cada ARP request é entregue a **todos**
os N: custo de entrega Θ(N) por request, contra Θ(1) de um unicast.

Suponha que cada host inicia, em média, **r** resoluções por segundo (novos fluxos, entradas
expirando). A taxa total de requests no segmento é **N·r**, e cada um custa N entregas:

$$
\text{carga de broadcast} \;\propto\; N \cdot r \cdot N \;=\; r\,N^2
$$

**O custo de broadcast cresce com o quadrado do número de hosts.** Dobrar o segmento quadruplica
a carga de ARP. Além disso, **cada host processa todos os broadcasts** (mesmo os que não lhe
dizem respeito) — uma interrupção de CPU por pacote —, então o custo agregado de CPU também é
Θ(N²).

Isto — não a exaustão de endereços — é o motivo prático de segmentos de camada 2 serem mantidos
pequenos (≈ `/24`). Uma `/16` (65 mil hosts) teria carga de broadcast ~65 000² / 254² ≈ **66 mil
vezes** a de uma `/24`. É por isso que "`/16` de camada 2 única" é erro de projeto
([02](02-pre-requisitos.md) §2.2, [10](10-fundamentos.md) §4): não é opinião, é a curva N².

---

## 3. O teto da tabela de vizinhos

A cada host alcançável corresponde, potencialmente, uma entrada na tabela de vizinhos. A memória
é Θ(N_ativos). O kernel impõe um teto rígido (`gc_thresh3`, [14](14-a-tabela-por-dentro.md) §7)
porque memória de kernel não paginável é finita.

Quando N_ativos > `gc_thresh3`, o sistema **recusa novas entradas** — falha de disponibilidade
proporcional ao tamanho do domínio. Combinando com §2: um domínio grande demais falha por **dois**
lados — carga de broadcast Θ(N²) e esgotamento de tabela Θ(N). Ambos empurram para a mesma
conclusão de engenharia: **segmentar**. Aumentar `gc_thresh` adia o segundo limite mas não toca
no primeiro.

---

## 4. O trilema: seguro, sem estado, sem infraestrutura — escolha dois

Uma afirmação (opinião fundamentada do autor, no espírito dos teoremas de impossibilidade de
sistemas distribuídos como FLP e CAP; **não** é um teorema formal publicado):

> Um protocolo de resolução de endereço de enlace não pode ser, ao mesmo tempo,
> **(a) seguro** (resistente a falsificação), **(b) sem estado global/infraestrutura** e
> **(c) sem confiança pré-estabelecida** entre as partes.

Argumento informal. Segurança contra falsificação exige que uma resposta seja **verificável** —
que o receptor distinga "X realmente está no MAC Y" de uma mentira. Verificação requer **ou**
(i) uma raiz de confiança compartilhada (chaves — infraestrutura, viola *b*), **ou** (ii) um
segredo/relação prévia entre as partes (viola *c*), **ou** (iii) uma autoridade consultável
(estado global, viola *b*). Sem nenhum dos três, qualquer host pode emitir bytes
indistinguíveis dos de outro — que é exatamente o ARP de 1982: escolheu *b* e *c*, sacrificou
*a*.

As soluções reais confirmam o trilema escolhendo pares diferentes:

| Solução | Abre mão de | Mantém |
|---|---|---|
| ARP (1982) | segurança | sem infraestrutura, sem confiança prévia |
| SEND/CGA (IPv6) | "sem infraestrutura" (precisa de cripto/CGA) | segurança, sem autoridade central |
| DAI + DHCP snooping | "sem estado" (o switch mantém a base) | segurança, sem cripto nos hosts |
| EVPN ARP suppression | "sem infraestrutura" (plano de controle BGP) | segurança e escala |

Toda defesa de camada 2 é, no fundo, **reintroduzir uma das três coisas que o ARP dispensou**.
Não há almoço grátis: você paga em chaves, em estado no switch, ou em um plano de controle.

---

## 5. Análise da máquina de estados como controle de custo

A máquina NUD ([14](14-a-tabela-por-dentro.md)) é um **otimizador do trade-off frescor × custo
de broadcast**. Formalize os custos:

- **custo de broadcast** por reverificação: alto (Θ(N) de incômodo);
- **custo de erro** por usar um mapeamento obsoleto: pacotes perdidos até detectar;
- **frequência de mudança** de um mapeamento: baixa (hosts raramente trocam de MAC).

A política ótima, dado que mudanças são raras, é: **usar o cache agressivamente** (STALE envia na
hora — minimiza latência e broadcast), **reverificar preguiçosamente** (só ao usar, com atraso),
e **confirmar de graça** quando uma camada superior já prova a alcançabilidade (o atalho do TCP,
[14](14-a-tabela-por-dentro.md) §4). A aleatorização de `base_reachable_time` é uma
**dessincronização** para evitar ressonância de reverificações — analogia direta com o problema
de sincronização de TCP (Van Jacobson) e com jitter em sistemas periódicos.

O NUD é, portanto, um exemplo limpo de projeto de cache sob custo de invalidação assimétrico:
invalidar cedo demais custa broadcast Θ(N); tarde demais custa alguns pacotes. Como Θ(N) ≫
alguns pacotes para N grande, a política inclina-se fortemente para "confiar e verificar
preguiçosamente".

---

## 6. Fronteira com a teoria da computação

Um aceno ao teorema de Rice (como nos outros assuntos desta pasta): decidir, em geral, se um MAC
observado numa resposta ARP corresponde ao "host legítimo pretendido" é indecidível **na ausência
de uma raiz de confiança** — porque "legítimo" é uma propriedade semântica do comportamento do
sistema, não sintática do pacote. Nenhuma inspeção do pacote resolve; só uma âncora externa
(chave, base de snooping, autoridade) torna a propriedade decidível. Isto reencontra o §4 por
outro caminho: a segurança de camada 2 não pode emergir da sintaxe do ARP; precisa de um
oráculo externo. É a versão computacional do trilema.

---

## Autoteste

1. Por que dois espaços de endereço são teoricamente necessários, e não apenas uma comodidade?
2. Derive a carga de broadcast em função de N e explique por que ela é Θ(N²).
3. Quantas vezes mais broadcast tem uma `/16` do que uma `/24`, aproximadamente? Mostre a conta.
4. Enuncie o trilema seguro/sem-estado/sem-infraestrutura e classifique DAI e SEND nele.
5. Por que aumentar `gc_thresh3` não resolve o problema de fundo de um segmento grande?
6. Explique o NUD como otimizador de um trade-off com custo de invalidação assimétrico.
7. Ligue o teorema de Rice à impossibilidade de o ARP ser seguro por si só.

---

**Fontes:** RFC 826; teoria de roteamento e agregação (CIDR, RFC 4632); analogia com FLP
(Fischer-Lynch-Paterson 1985) e CAP (Brewer/Gilbert-Lynch); Van Jacobson sobre sincronização;
teorema de Rice. As formulações de "trilema" e a análise N² são exposições do autor a partir
desses princípios, sinalizadas como tal. Consultado em 14/08/2026.

**Próximo:** [65-estado-da-arte.md](65-estado-da-arte.md)
