# 60 · Teoria avançada

> Nível: pesquisa · Atualizado em 14/08/2026
> Pré-requisitos: [14-assinatura-jws.md](14-assinatura-jws.md) e conforto com
> notação de probabilidade. Onde há afirmação não consensual, está marcada.

---

## 60.1 · O que "seguro" significa formalmente

Segurança criptográfica não é uma propriedade absoluta — é uma afirmação da forma:

> *Nenhum adversário limitado a recursos R consegue vencer o jogo J com
> probabilidade maior que ε.*

Três componentes, e todos importam:

- **o jogo** (o que conta como vitória);
- **o limite de recursos** (tempo, número de consultas);
- **a hipótese** (o problema difícil sobre o qual tudo repousa).

Uma afirmação sem os três é marketing.

### O jogo do JWS: EUF-CMA

*Existential Unforgeability under Chosen Message Attack.*

```
Experimento EUF-CMA(A, Σ, λ):
  1. (sk, pk) ← Σ.Gerar(1^λ)
  2. Q ← ∅
  3. (m*, σ*) ← A^{O_sk}(pk)
       onde O_sk(m): Q ← Q ∪ {m}; devolve Σ.Assinar(sk, m)
  4. A vence sse  Σ.Verificar(pk, m*, σ*) = 1  ∧  m* ∉ Q
```

Σ é **EUF-CMA-seguro** se, para todo adversário A em tempo polinomial,

```
Pr[A vence] ≤ negl(λ)
```

onde `negl` é desprezível: menor que `1/p(λ)` para todo polinômio `p`, a partir de
algum `λ`.

**A força do modelo** está no que ele concede ao adversário: a chave pública, e
assinaturas de quantas mensagens ele quiser, escolhidas por ele, adaptativamente.
É um modelo generoso, e é por isso que uma prova nele vale muito.

**Variante mais forte: SUF-CMA** (*strong unforgeability*). O adversário também vence
se produzir uma assinatura **diferente** para uma mensagem que já consultou.
Ed25519 é SUF-CMA; ECDSA **não é** — dada `(r,s)` válida, `(r, −s mod n)` também
verifica em implementações que não canonicalizam `s`.

**Isso importa em JWT?** Marginalmente, e vale saber onde: se você usa o token como
chave de deduplicação ou de cache, duas assinaturas válidas para o mesmo payload
significam dois "tokens diferentes" com o mesmo significado — e o `jti` de uso único
falha se você deduplicar pelo token e não pelo `jti`. É mais um argumento para
**nunca usar o token inteiro como chave**.

---

## 60.2 · A cadeia de reduções do HS256

O que sustenta a segurança de um token HS256, do topo à base:

```
JWS com HS256 é EUF-CMA-seguro
        ⇐ HMAC-SHA256 é um MAC seguro
        ⇐ HMAC é um PRF (Bellare, 2006), se a função de compressão for um PRF
        ⇐ a função de compressão do SHA-256 é um PRF   ← HIPÓTESE NÃO PROVADA
        ⇐ a chave tem entropia suficiente               ← RESPONSABILIDADE SUA
```

Três observações honestas:

**1. A base não é provada.** "A função de compressão do SHA-256 é um PRF" é uma
conjectura, sustentada por 25 anos de criptanálise sem sucesso. Toda a criptografia
prática repousa em conjecturas desse tipo — não há prova incondicional, e não haverá
enquanto P ≟ NP estiver em aberto.

**2. A prova de Bellare (2006) melhorou a de 1996.** A original exigia que a função de
compressão fosse resistente a colisões; a de 2006 exige apenas que seja um PRF — uma
hipótese mais fraca, portanto uma prova mais forte. Consequência prática:
HMAC-SHA1 continuou aceitável para MAC mesmo depois de SHA-1 cair para colisão, porque
colisão não quebra a hipótese do PRF.

**3. O último elo é o seu.** A prova assume chave uniformemente aleatória de tamanho
adequado. `HMAC("senha123", m)` satisfaz a matemática e falha na prática, porque a
premissa de entropia foi violada. **Nenhuma prova protege contra premissa falsa** — e
é aí que quase todos os incidentes reais acontecem.

---

## 60.3 · ECDSA e o modelo do oráculo aleatório

ECDSA tem prova de segurança apenas em modelos idealizados:

- no **modelo do grupo genérico** (Brown, 2001), tratando o grupo da curva como uma
  caixa preta;
- ou no **modelo do oráculo aleatório** (ROM), tratando o hash como uma função
  verdadeiramente aleatória.

**Por que isso é insatisfatório.** Canetti, Goldreich e Halevi (1998) exibiram
esquemas **provadamente seguros no ROM e inseguros com qualquer função de hash
concreta**. O ROM, portanto, não é uma prova — é evidência de que não há falha
estrutural óbvia.

**Consenso da área, declarado como consenso:** provas no ROM são consideradas
evidência forte e são aceitas na prática, apesar da objeção teórica. Nenhum esquema
usado em produção foi quebrado por causa do ROM.

### A fragilidade real do ECDSA: o nonce

A assinatura ECDSA usa um valor aleatório `k`:

```
r = (k·G).x  mod n
s = k⁻¹ (H(m) + r·d)  mod n         d = chave privada
```

Com dois `s` usando o mesmo `k`:

```
s₁ = k⁻¹(H(m₁) + r·d)
s₂ = k⁻¹(H(m₂) + r·d)

k = (H(m₁) − H(m₂)) / (s₁ − s₂)  mod n
d = (s₁·k − H(m₁)) / r           mod n
```

**Duas divisões modulares e a chave privada está na sua mão.** Não é criptanálise —
é álgebra do ensino médio sobre um corpo finito.

Casos reais: PlayStation 3 (2010, `k` constante); carteiras Bitcoin em Android (2013,
gerador defeituoso).

Pior ainda: **vazamento parcial** de `k` também basta. Com poucos bits de viés em
algumas centenas de assinaturas, ataques de rede escondida (*hidden number problem*,
via reticulados e LLL) recuperam a chave. É o que motivou as implementações em tempo
constante.

**A mitigação:** RFC 6979 (ECDSA determinístico), com `k = HMAC(d, H(m))`. Elimina a
dependência do gerador aleatório. **Recomendação:** nunca implemente ECDSA à mão. Esta
é a razão.

---

## 60.4 · Por que o Ed25519 é melhor por projeto

| Falha do ECDSA | Como o Ed25519 elimina |
|---|---|
| `k` repetido → chave recuperável | `r = H(prefixo_da_chave ‖ m)` — determinístico por definição |
| canal lateral por tempo | fórmulas completas, sem ramificação dependente de segredo |
| maleabilidade de `s` | verificação exige `s` na forma canônica → SUF-CMA |
| curva com parâmetros de origem obscura | Curve25519 tem derivação pública e justificada |
| validação de ponto esquecida | codificação torna pontos inválidos irrelevantes |

**A lição de engenharia**, que transcende criptografia: *a primitiva mais segura é a
que torna o uso incorreto impossível, não a que documenta o uso correto*. É o mesmo
princípio da lista fechada de algoritmos em [20](20-ataques-e-defesas.md).

---

## 60.5 · O teorema informal da revogação

Uma formulação que vale a pena tornar explícita:

> **Nenhum sistema de credenciais pode, simultaneamente, ter (a) verificação sem
> comunicação com uma autoridade e (b) revogação com atraso zero.**

**Esboço de argumento.** Suponha que valham (a) e (b). Considere o instante `t` em que
a autoridade revoga a credencial `C`. Um verificador `V` que não se comunica com
ninguém tem, em `t+ε`, exatamente a mesma informação que tinha em `t−ε`: a credencial
apresentada e seu estado local. Logo, `V` decide igual nos dois instantes, e a
revogação não teve efeito. Contradição. ∎

O argumento é **teórico da informação**, não computacional: a informação "foi
revogada" precisa **atravessar** da autoridade ao verificador, e essa travessia tem
custo e latência maiores que zero.

**Corolário prático:** as três formas de aproximação são exaustivas.

| Estratégia | O que se sacrifica |
|---|---|
| Vida curta (`exp`) | atraso ≤ vida; ganha-se carga de renovação |
| Lista de negação | (a): há comunicação, mas com estado pequeno |
| *Push* de revogação | consistência eventual e complexidade |

Não há uma quarta. Toda proposta que promete "revogação instantânea de JWT sem
estado" está escondendo uma dessas três — em geral a segunda.

**Onde isso deixa de valer:** se o próprio verificador **for** a autoridade (monolito),
(a) é trivialmente satisfeita porque não há travessia. É exatamente o argumento de
[21-quando-nao-usar.md](21-quando-nao-usar.md).

---

## 60.6 · Custo da lista de negação: filtros de Bloom

Um filtro de Bloom guarda um conjunto com falsos positivos e **zero falsos
negativos** — que é a direção certa para uma lista de negação: pode-se recusar
indevidamente (irritante), nunca aceitar um token revogado (catastrófico).

Tamanho ótimo, para `n` elementos e taxa de falso positivo `p`:

```
m = −n·ln p / (ln 2)²     bits
k = (m/n)·ln 2            funções de hash
```

Para `n = 100.000` revogações vivas e `p = 0,001`:

```
m ≈ 1,44 Mbit ≈ 180 KB     k ≈ 10
```

**180 KB replicáveis em toda instância**, atualizáveis por difusão, consultáveis em
memória sem rede. Um em mil usuários deslogados vê um 401 espúrio — e a mitigação é
simples: no falso positivo, consulte a lista real. O filtro vira um **atalho para o
caso comum** (não revogado), não a decisão final.

**Limitação:** o filtro de Bloom clássico não suporta remoção, e a faxina por
expiração é essencial. Soluções: filtro *counting*, filtro *cuckoo* (suporta remoção),
ou simplesmente reconstruir o filtro periodicamente — com janela de 15 minutos,
reconstruir a cada minuto é barato.

**Opinião profissional:** para quase todo sistema, um `SET` de Redis com TTL é mais
simples e suficiente. O filtro de Bloom vale quando a latência da consulta é
inaceitável e o volume é alto — e é uma decisão a tomar com medição, não por
elegância.

---

## 60.7 · Diferenciais de analisador (*parser differentials*)

Uma classe de vulnerabilidade que não é criptográfica e que a análise formal do
esquema de assinatura **não** cobre.

A premissa implícita de todo sistema com JWT: **todos os componentes interpretam o
mesmo token da mesma forma**. Quando não interpretam, surge um ataque.

| Ambiguidade | Comportamentos divergentes observados |
|---|---|
| chaves JSON duplicadas | primeira ocorrência / última ocorrência / erro |
| Unicode e escapes | `A` vs. `A`; normalização NFC/NFD |
| números fora do intervalo seguro | `double` (JS) vs. inteiro arbitrário (Python) |
| base64url com preenchimento inesperado | aceito por uns, recusado por outros |
| bytes após o terceiro segmento | ignorados por uns, erro em outros |
| `alg` como array em vez de string | coerção frouxa vs. erro de tipo |

**O ataque geral:** o gateway lê `{"sub":"ana","sub":"admin"}` como `ana` e autoriza;
o serviço interno lê como `admin`. A assinatura é válida nos dois — a criptografia
está intacta e é irrelevante.

**Defesa estrutural:** o mesmo princípio do JOSE original. *Verifique e consuma o
mesmo objeto*. Na prática: uma única biblioteca de análise em toda a organização; e
recuse — não normalize — entrada ambígua. Normalizar é criar uma transformação, e
transformações entre verificação e uso são exatamente o problema.

**Nota de pesquisa:** esta é, na minha leitura, a área menos explorada
academicamente do assunto. Há trabalho sistemático sobre diferenciais em analisadores
de X.509 e de HTTP; para JOSE, a literatura é esparsa. É um bom tema para quem procura
problema aberto com impacto prático.

---

## 60.8 · Verificação formal

Provar que a **primitiva** é segura não prova que o **protocolo** é.

| Ferramenta | Modelo | Aplicação típica |
|---|---|---|
| **ProVerif** | modelo simbólico (Dolev–Yao) | alcançabilidade de estados ruins |
| **Tamarin** | simbólico, com estado mutável | protocolos com sessão e chave de longa duração |
| **CryptoVerif** | modelo computacional | provas com limites concretos |
| **F\***, EasyCrypt | provas assistidas | implementações verificadas |

Resultados relevantes já obtidos com essas ferramentas: análise formal do TLS 1.3
(que influenciou o desenho final do padrão), de fluxos do OAuth, e do OIDC. Em vários
casos as ferramentas encontraram ataques reais em protocolos publicados — o que é o
melhor argumento a favor delas.

**O que costuma sobrar de fora**, e onde os ataques reais moram:

- o modelo simbólico assume criptografia perfeita (não modela viés de nonce);
- o modelo assume um analisador único e não ambíguo (não modela 60.7);
- o modelo assume que a implementação corresponde à especificação.

---

## 60.9 · O horizonte pós-quântico

**O que muda com um computador quântico criptograficamente relevante (CRQC):**

| Primitiva | Algoritmo quântico | Efeito |
|---|---|---|
| RSA, ECDSA, EdDSA | **Shor** | **quebra total** — a chave privada é recuperável da pública |
| HMAC-SHA256 | **Grover** | segurança de 256 → ~128 bits: **ainda seguro** |
| AES-256 | Grover | 256 → ~128 bits: ainda seguro |

**A assimetria que orienta a prioridade:**

- **Cifra** sofre de "colher agora, decifrar depois": o adversário grava hoje o
  tráfego cifrado e o decifra em 2040. **A urgência é hoje.**
- **Assinatura** não tem esse problema: uma assinatura quebrada em 2040 não permite
  forjar um token que já expirou em 2026. **A urgência é menor**, e proporcional à
  vida útil da chave e do que ela certifica.

Para JWT, cujos tokens duram minutos, a migração de assinatura é menos urgente que
para certificados raiz (que duram 20 anos) ou para firmware assinado.

**Estado do padrão em 2026:** a **RFC 9964** (mai/2026) define ML-DSA (FIPS 204) para
JOSE e COSE. Ver [65-estado-da-arte.md](65-estado-da-arte.md).

**O custo é o obstáculo real:**

| Esquema | Assinatura | Chave pública |
|---|---|---|
| Ed25519 | 64 B | 32 B |
| ECDSA P-256 | 64 B | 64 B |
| **ML-DSA-44** | **~2.420 B** | ~1.312 B |
| SLH-DSA (menor variante) | ~7.856 B | 32 B |

Uma assinatura ML-DSA-44 é **38× maior** que uma Ed25519. Num token que vai em todo
cabeçalho HTTP, isso é uma mudança de categoria: o token sai de ~300 bytes para
~3,5 KB — perto do limite de cookie e no caminho do limite do nginx.

**Opinião profissional:** o JWT tal como usado hoje — token curto em cabeçalho HTTP —
é estruturalmente hostil a assinaturas pós-quânticas. Ou os limites de cabeçalho
mudam, ou o access token volta a ser por referência, ou surge um esquema PQ com
assinatura pequena. **Considero esta a tensão não resolvida mais interessante do
assunto para os próximos dez anos.** É previsão, não fato.

---

## 60.10 · Problemas em aberto

Para quem procura tema de pesquisa com impacto prático:

1. **Diferenciais de analisador em JOSE.** Estudo sistemático, com *fuzzing*
   diferencial entre as principais bibliotecas. Área subexplorada (60.7).

2. **Revogação com custo sublinear e atraso limitado.** Existe estrutura melhor que
   Bloom para o padrão específico "entradas com TTL curto e uniforme"? Acumuladores
   criptográficos são um caminho, com custo computacional hoje proibitivo.

3. **Assinatura pós-quântica compacta.** O gargalo real da migração. Esquemas
   baseados em isogenias prometiam assinaturas pequenas; SIDH caiu em 2022, mas
   SQIsign continua ativo.

4. **Formalização do ciclo de vida completo.** As análises formais cobrem os fluxos
   do OAuth; a rotação de refresh com detecção de reuso, a queima de família e a
   interação com falsos positivos de concorrência não têm modelo formal publicado que
   eu conheça.

5. **Prova de posse sem estado no cliente.** DPoP exige que o cliente mantenha uma
   chave. Há como amarrar um token ao portador sem isso? (Provavelmente não, e um
   resultado de impossibilidade seria valioso.)

6. **Privacidade em SD-JWT sob correlação.** A divulgação seletiva esconde claims,
   mas a assinatura do emissor é a mesma em todas as apresentações — permitindo
   correlacionar. Provas de conhecimento zero resolveriam, a um custo computacional
   hoje alto para dispositivo móvel.

---

## Autoteste

1. Enuncie o experimento EUF-CMA. O que o adversário recebe de graça?
2. Qual a diferença entre EUF-CMA e SUF-CMA? Onde ela importa em JWT?
3. Escreva a cadeia de reduções do HS256. Qual elo não é provado, e qual é seu?
4. Por que a prova de Bellare de 2006 é mais forte que a de 1996?
5. O que o resultado de Canetti–Goldreich–Halevi diz sobre o ROM, e por que a
   comunidade ainda aceita provas nesse modelo?
6. Derive a chave privada a partir de duas assinaturas ECDSA com o mesmo `k`.
7. Enuncie e argumente o teorema informal da revogação. Por que ele é de teoria da
   informação e não de complexidade?
8. Calcule o tamanho de um filtro de Bloom para 1 milhão de revogações com `p = 10⁻⁴`.
9. Descreva um ataque de diferencial de analisador e explique por que a criptografia
   é irrelevante nele.
10. Por que a urgência pós-quântica é menor para assinatura que para cifra? E por que
    o tamanho da assinatura ML-DSA é um problema estrutural para JWT?
