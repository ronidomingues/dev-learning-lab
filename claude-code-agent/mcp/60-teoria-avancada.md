# 60 · Teoria avançada — os limites, e por que eles são limites

`Nível: pesquisa` · `Escrito em 01/09/2026`

Aqui saímos do "como se usa" para o "o que é possível". Cada seção termina numa parada
legítima: uma lei, uma prova, uma decisão histórica, ou um problema de pesquisa aberto.

---

## 1. Por que "exatamente uma vez" não existe

### 1.1 O resultado

MCP roda sobre canais que podem perder mensagens, e a revisão `2026-07-28` **removeu**
retomada de fluxo e reentrega. Consequência direta: se um `tools/call` não devolveu
resposta, o cliente **não sabe** se a ferramenta executou.

Isto não é limitação de implementação. É o **problema dos dois generais**, provado
impossível: não existe protocolo, com número finito de mensagens sobre um canal não
confiável, que garanta a dois participantes o conhecimento comum de um acordo.

**Parada legítima: teorema de impossibilidade.** Não há solução, só mitigação.

### 1.2 O que dá para ter

| Semântica | Como | Custo |
|---|---|---|
| **no máximo uma vez** | não repetir nunca | perde operação quando a resposta se perde |
| **pelo menos uma vez** | repetir até obter resposta | duplica efeito |
| **efetivamente uma vez** | pelo menos uma vez **+ idempotência no receptor** | exige chave de idempotência e armazenamento |

MCP oferece "no máximo uma vez" por omissão. **A responsabilidade da idempotência é sua**
— e a spec praticamente admite isso ao recomendar handles explícitos e ao remover a
reentrega.

Agrava o caso: **o cliente do MCP é um modelo**, que repete chamadas por razões próprias
(perdeu o resultado do contexto, o usuário reformulou, a resposta demorou). Numa API HTTP
comum, a retentativa é decisão de código; aqui é decisão estatística.

### 1.3 Por que a spec removeu a retomada

Os cinco porquês:

1. **Por que remover `Last-Event-ID`?** Porque exige o servidor **manter um buffer** de
   mensagens já enviadas, por fluxo, para poder reenviá-las.
2. **Por que isso é caro?** Porque é estado por conexão — exatamente o que a reescrita
   sem estado eliminou.
3. **Por que não guardar o buffer num armazenamento compartilhado?** Porque o custo de
   escrever toda notificação num Redis para cobrir uma queda rara é desproporcional.
4. **Por que a alternativa (reemitir) é aceitável?** Porque, sem sessão, reemitir é barato:
   qualquer réplica atende, e a requisição carrega tudo que precisa.
5. **Por que isso não resolve o problema dos dois generais?** **Não resolve.** Só o
   transfere para a camada de aplicação, onde a idempotência pode ser expressa em termos
   do domínio ("já existe pedido com esta chave"). É a única camada em que o problema
   tem solução prática. **Parada: trade-off explícito, documentado.**

---

## 2. Injeção de prompt: por que continua aberto

### 2.1 O enunciado

Dado um modelo de linguagem $M$ que recebe um contexto $C = I \parallel D$, onde $I$ são
instruções confiáveis e $D$ é dado não confiável, **existe uma função que garanta que $M$
trate $D$ apenas como dado?**

**Resposta, em 2026: não se conhece nenhuma.**

### 2.2 Por que é difícil

O problema é que $I$ e $D$ estão no **mesmo espaço de representação**. Não há um bit de
"isto é instrução". Em arquiteturas de von Neumann clássicas o mesmo problema existe
(código e dado na mesma memória) e a solução foi **hardware**: bit NX, W^X, MMU. O modelo
de linguagem não tem MMU.

Tentativas conhecidas, e por que cada uma falha:

| Abordagem | Falha porque |
|---|---|
| **Delimitadores** (`<dados>...</dados>`) | o atacante escreve o delimitador de fechamento |
| **Marcação por posição** ("o que vem depois é dado") | a atenção não respeita posição de forma garantida |
| **Classificador de injeção** antes do modelo | classificador é um modelo; herda o mesmo problema e tem falsos negativos |
| **Treinamento de hierarquia de instrução** | reduz a taxa, não elimina; é defesa estatística contra ataque adversarial |
| **Isolamento de capacidade** (o modelo que lê dado não tem ferramentas) | funciona, **mas** restringe drasticamente o que o agente faz |
| **Aprovação humana** | fadiga; e ofuscação Unicode mostra que a tela pode mentir |

### 2.3 A formulação específica do MCP

No MCP, $D$ inclui coisas que a maioria dos textos não classifica como "dado":

1. **descrições de ferramenta** — entram no contexto **antes** de qualquer chamada
   (*line jumping*);
2. **schemas**, inclusive os `description` de cada campo;
3. **resultados** de ferramenta;
4. **`instructions`** do servidor;
5. **nomes** de ferramenta, recurso e prompt.

Isso torna a superfície maior que a de um RAG comum: em RAG, o texto malicioso precisa ser
recuperado; aqui, ele já está no catálogo.

### 2.4 O limite teórico da defesa

Um resultado informal, mas útil de raciocinar:

> Se o modelo precisa **entender** $D$ para ser útil, e "entender" inclui inferir intenção
> a partir de linguagem natural, então distinguir "intenção descrita em $D$" de "intenção
> instruída em $I$" exige exatamente a capacidade que se quer restringir.

**Parada legítima: problema de pesquisa aberto.** Não há defesa completa conhecida em
2026. O que existe é **defesa em profundidade**: reduzir o dano (menor privilégio,
sandbox, verbos estreitos), aumentar a visibilidade (aprovação com descrição completa,
Unicode normalizado, auditoria) e diminuir a exposição (poucos servidores, de origem
conhecida).

---

## 3. Segurança por capacidade — e o que o MCP herdou

### 3.1 O modelo

Na segurança por **capacidade** (*capability*, Dennis & Van Horn, 1966), autoridade e
designação são a **mesma coisa**: possuir a referência ao objeto **é** ter o direito de
usá-lo. Não existe consulta a uma lista de permissões separada.

O oposto é a **ACL**: o nome é público, e o acesso é decidido consultando uma lista.

### 3.2 O problema do delegado confuso, formalmente

Descrito por Norm Hardy (1988): um programa com autoridade $A$ que executa uma operação
sob a designação de um usuário com autoridade $B \subset A$ pode ser induzido a usar $A$
onde só $B$ era devido.

É exatamente o ataque de [19 §2](19-seguranca.md): o proxy MCP tem autoridade sobre a API
do terceiro; o atacante fornece a designação (`redirect_uri`); o proxy usa a própria
autoridade a serviço da designação alheia.

**A solução canônica na literatura de capacidades é estrutural**: não separar designação
de autoridade. A solução do MCP é **processual** — consentimento por cliente, validação
exata de `redirect_uri`, `state` de uso único. Funciona **se implementada corretamente**,
e por isso a spec dedica páginas a ela.

### 3.3 Onde o MCP fica

| Elemento | Modelo |
|---|---|
| **Token OAuth com audiência** | capacidade (posse = autoridade, restrita ao recurso) |
| **Escopos** | híbrido: a capacidade carrega os direitos, mas o servidor ainda decide |
| **Handle de estado** | **explicitamente NÃO é capacidade**: a spec manda validar a autorização do chamador a cada uso |
| **Nome de ferramenta** | designação pura; a autoridade vem do token |

A decisão sobre handles é interessante e correta: um handle *parece* uma capacidade
(string opaca, imprevisível), e a spec proíbe tratá-lo como tal. Motivo: handles vazam
com facilidade — aparecem no contexto do modelo, em log, na tela do usuário. Uma
capacidade que vaza rotineiramente não é uma boa capacidade.

**Parada legítima: decisão de projeto documentada**, tomada contra o modelo teórico puro
por razões operacionais.

---

## 4. Por que sem estado, formalmente

### 4.1 O enunciado

Seja um serviço com $N$ réplicas atrás de um balanceador. Se o processamento de uma
requisição $r_i$ depende de estado estabelecido por $r_j$ ($j < i$) numa réplica
específica, então:

- ou o balanceador precisa de **afinidade** (rotear $r_i$ para a mesma réplica),
- ou o estado precisa estar em **armazenamento compartilhado**,
- ou o sistema está **errado**.

### 4.2 O custo de cada saída

**Afinidade de sessão:** a perda de uma réplica derruba as sessões nela; o balanceamento
fica desigual; o deploy exige drenagem; e autoescala não pode reduzir réplicas livremente.

**Estado compartilhado:** toda requisição paga uma ida ao armazenamento; o armazenamento
vira ponto único de falha; e você adquire um problema de consistência que não tinha.

**Sem estado:** a requisição carrega tudo. Custo: mais bytes por requisição, e a
complexidade sai do transporte e entra na aplicação (`requestState` cifrado, handles).

### 4.3 A escolha do MCP, e o preço

O MCP escolheu **sem estado**, e pagou:

| Ganho | Preço |
|---|---|
| escala horizontal comum | `_meta` repetido em toda requisição |
| deploy comum | `requestState` precisa de HMAC/AEAD, com principal, TTL e vínculo à requisição |
| serverless viável | MRTR é mais complexo que uma requisição de volta |
| queda de réplica é benigna | sem retomada de SSE |

**Parada legítima: trade-off econômico e operacional explícito**, com os SEPs
[2575](https://modelcontextprotocol.io/seps/2575-stateless-mcp) e
[2322](https://modelcontextprotocol.io/seps/2322-MRTR) como registro histórico.

Vale notar o que o MCP fez de elegante: `requestState` é **estado transportado pelo
cliente**, cifrado pelo servidor. É o mesmo truque dos *cookies de sessão criptografados*
e dos *JWT stateless*: o servidor não guarda; o cliente carrega; a integridade é
criptográfica. E, como todo truque desse tipo, herda o mesmo problema — **revogação e
uso único não vêm de graça**, e a spec diz isso explicitamente.

---

## 5. Descoberta em tempo de execução e o limite de contexto

### 5.1 A tensão

Descoberta em tempo de execução é uma qualidade central do MCP: o catálogo é lido a cada
sessão, não compilado. Mas ela cria uma tensão dura:

Seja $T$ o conjunto de ferramentas disponíveis, $|d_t|$ o custo em tokens da descrição de
$t$, e $W$ a janela de contexto. É preciso que

$$\sum_{t \in T} |d_t| + |\text{conversa}| \le W$$

Com $|T|$ crescendo (vários servidores, dezenas de ferramentas cada), o catálogo consome
a janela **antes** da conversa. E, pior: descrições longas melhoram a escolha individual
mas pioram a escolha global, ao empurrar $|T|$ efetivo para baixo.

### 5.2 As saídas conhecidas

| Saída | Ideia | Problema |
|---|---|---|
| **Curadoria manual** | o usuário liga só o necessário | fricção; e o usuário não sabe de antemão |
| **Descoberta progressiva** | uma "ferramenta de buscar ferramentas"; o catálogo entra sob demanda | uma ida a mais; e o modelo pode não saber que deve buscar |
| **Cache de prompt** | `ttlMs` e ordem determinística maximizam acertos | reduz custo, não ocupação |
| **Roteamento hierárquico** | um modelo pequeno escolhe o servidor; o grande escolhe a ferramenta | latência e um ponto de erro a mais |
| **Compressão de descrição** | descrições mínimas, detalhes sob demanda | piora a escolha |

**Parada: problema aberto, com trabalho em curso.** *Progressive discovery* é uma das
cinco prioridades do roadmap de 22/08/2026, sob o Core Primitives WG, explicitamente
articulado com o trabalho de caching.

### 5.3 O paralelo histórico

Este é **o mesmo problema** que matou os plugins de ChatGPT em 2023: specs OpenAPI grandes
demais para o contexto. O MCP evitou-o por um tempo com catálogos pequenos; o crescimento
do ecossistema o trouxe de volta.

**Lição geral, e vale para qualquer protocolo com consumidor de contexto limitado:**
descoberta em tempo de execução é gratuita enquanto o catálogo é pequeno, e vira o custo
dominante quando não é. Todo sistema que resolveu isso — DNS, service discovery,
importações de linguagem — resolveu com **hierarquia e busca**, não com listagem completa.

---

## 6. Provas de propriedades do protocolo

### 6.1 Isolamento de dados entre servidores

**Afirmação.** No MCP `2026-07-28`, um servidor $S_1$ não pode obter, **pelo protocolo**,
dado que $S_2$ devolveu ao host.

**Argumento.** Cada cliente fala com exatamente um servidor. Servidores não iniciam
requisição. Não há método pelo qual $S_1$ endereça $S_2$ ou o cliente de $S_2$. As únicas
mensagens que $S_1$ recebe são requisições do seu próprio cliente, cujo conteúdo é
decidido pelo host. ∎

**A ressalva que anula a utilidade prática.** A afirmação vale para **dados**, não para
**influência**. $S_1$ pode devolver texto que induz o modelo a chamar $S_2$ e, depois, a
mandar o resultado a $S_1$. O host permitiria, porque cada passo isolado parece legítimo.

Isto é uma **falha de fluxo de informação**, e o arcabouço certo para pensá-la é o de
*non-interference* (Goguen & Meseguer, 1982): um sistema é não interferente se as ações
de alta sensibilidade não afetam as observações de baixa. **O MCP não é não interferente**,
e não pode ser enquanto um agente puder ler de uma fonte e escrever em outra.

**Parada: propriedade formal violada por construção.** A única correção conhecida é
restringir capacidade — um agente que lê de $S_1$ não escreve em $S_2$ —, o que na prática
mata a composição, que é o princípio de projeto nº 2 do MCP.

### 6.2 A negociação de versão termina

**Afirmação.** O laço "requisição → `-32022` → repetir com versão de `supported`" termina.

**Argumento.** `data.supported` é finito e devolvido pelo servidor. Um cliente que escolhe
sempre uma versão ainda não tentada da lista esgota-a em no máximo $|supported|$ passos.
Se nenhuma for mutuamente suportada, o cliente reporta erro. ∎

**A ressalva.** O término depende de o cliente **não** repetir a mesma versão. A spec diz
"escolher uma versão mutuamente suportada", não "uma ainda não tentada". Um cliente
ingênuo que sempre pega `supported[0]` entra em laço contra um servidor que devolve uma
lista sem interseção com o que ele fala. **Trate o conjunto de versões tentadas
explicitamente.**

### 6.3 O laço do MRTR não termina sozinho

**Afirmação.** Nada no protocolo garante o término do laço de MRTR.

**Argumento.** A spec diz que servidores **PODEM** devolver `InputRequiredResult` em várias
tentativas seguidas da mesma requisição, "se quiserem repetidamente perguntar ao usuário
até ter o que precisam". Não há limite normativo de rodadas. Um servidor malicioso, ou com
defeito, pode responder `input_required` indefinidamente. ∎

**Consequência normativa para quem escreve cliente:** o teto de rodadas
(`input_required_max_rounds` no SDK Python) **não é uma otimização, é um requisito de
segurança**. Sem ele, um servidor mantém o cliente e o usuário em laço.

---

## 7. Comparação formal com protocolos vizinhos

| | **LSP** | **MCP** | **gRPC** | **GraphQL** |
|---|---|---|---|---|
| Base | JSON-RPC 2.0 | JSON-RPC 2.0 | HTTP/2 + Protobuf | HTTP + linguagem própria |
| Descoberta | capacidades, no `initialize` | `server/discover`, por requisição | reflexão (opcional) | introspecção de esquema |
| Estado | sessão por documento | **nenhum** | por stream | nenhum |
| Consumidor | determinístico (o editor) | **estatístico (o modelo)** | determinístico | determinístico |
| Schema | tipos fixos, na spec | **JSON Schema em tempo de execução** | Protobuf, compilado | SDL, compilado |
| Servidor→cliente | requisições permitidas | **proibidas** (MRTR) | streams bidirecionais | subscriptions |
| Custo de escrever servidor | médio | **muito baixo** | alto (codegen) | médio-alto |

**A diferença que explica quase tudo:** o consumidor do MCP é estatístico. Por isso o
schema é lido em tempo de execução (não compilado), as descrições são em linguagem
natural (não comentários), erros de execução carregam texto para o modelo se corrigir, e a
aprovação humana é parte do desenho.

---

## 8. Problemas em aberto

Lista honesta do que ninguém resolveu, em 01/09/2026:

1. **Injeção de prompt.** Sem defesa completa conhecida. §2.
2. **Não interferência entre servidores.** Incompatível com composição livre. §6.1.
3. **Escala de catálogo.** Descoberta progressiva é a aposta atual, sem resultado ainda. §5.
4. **Identidade de agente.** Um agente autônomo que age por um usuário ausente, e que
   delega a subagentes com autoridade menor, não tem modelo padronizado. É prioridade nº 3
   do roadmap: DPoP, Workload Identity Federation, ID-JAG, RFC 8693.
5. **Confiança em servidor de terceiro.** O registry verifica namespace, não comportamento.
   Assinatura de código e atestação de proveniência ainda não estão no protocolo.
6. **Semântica do resultado de ferramenta.** `content` e `structuredContent` podem vir
   juntos, e isso "confundiu autores de servidor e de cliente e produziu implementações
   divergentes" — palavras do roadmap. Redesenho previsto.
7. **Composição de primitivas assíncronas.** Tasks, `subscriptions/listen` e progresso são
   três respostas a "o servidor ainda não terminou" que não compartilham ciclo de vida,
   modelo de cancelamento nem superfície de erro. O roadmap chama isso de "revisão de
   composição" e é a prioridade nº 1.

---

## 9. Autoteste

1. Enuncie o problema dos dois generais e explique por que ele impede "exatamente uma vez" no MCP.
2. Quais três semânticas de entrega existem, e qual o MCP oferece por omissão?
3. Por que a spec removeu a retomada de SSE? Onde está a parada legítima do argumento?
4. Formule o problema da injeção de prompt e explique por que delimitadores não resolvem.
5. O que a superfície de injeção do MCP inclui além dos resultados de ferramenta?
6. Defina "delegado confuso" formalmente e mostre onde ele aparece no MCP.
7. Por que a spec proíbe tratar handle de estado como capacidade, se ele parece uma?
8. Prove o isolamento de dados entre servidores — e explique por que a prova não ajuda tanto quanto parece.
9. Por que o laço de negociação de versão termina, e por que o do MRTR não termina sozinho?
10. Qual característica do MCP explica quase todas as suas diferenças em relação ao LSP?

---

**Anterior:** [24 · Operação e produção](24-operacao-e-producao.md) · **Próximo:** [65 · Estado da arte](65-estado-da-arte.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Referências teóricas: problema dos dois generais (Akkoyunlu, Ekanadham & Huber, 1975;
Gray, 1978); segurança por capacidade (Dennis & Van Horn, *Programming Semantics for
Multiprogrammed Computations*, CACM 1966); delegado confuso (Norm Hardy, *The Confused
Deputy*, ACM OSR 1988); não interferência (Goguen & Meseguer, *Security Policies and
Security Models*, IEEE S&P 1982).
Referências normativas: [SEP-2575 (stateless)](https://modelcontextprotocol.io/seps/2575-stateless-mcp),
[SEP-2322 (MRTR)](https://modelcontextprotocol.io/seps/2322-MRTR),
[SEP-2549 (TTL)](https://modelcontextprotocol.io/seps/2549-TTL-for-list-results),
[Roadmap de 22/08/2026](https://modelcontextprotocol.io/development/roadmap).
As análises formais das seções 4 a 6 são deste material e estão declaradas como
argumento, não como resultado publicado. Consultas em 01/09/2026.*
