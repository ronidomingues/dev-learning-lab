# 60 · Teoria avançada — o que a assinatura prova, e os seus limites

> Nível: pesquisa · Atualizado em 13/08/2026

Aqui tratamos o assunto com precisão: o que é provado, sob quais hipóteses, e o que
demonstravelmente **não** pode ser provado por esse mecanismo. É o arquivo para ler antes de
apresentar assinatura de commits como controle de segurança a alguém que vá tomar decisão
com base nisso.

---

## 1. A definição formal de segurança de uma assinatura

Um esquema de assinatura digital é uma tripla de algoritmos `(Gen, Sign, Verify)`:

```
Gen(1ⁿ) → (pk, sk)                     gera o par de chaves
Sign(sk, m) → σ                         assina a mensagem m
Verify(pk, m, σ) → {0, 1}               verifica
```

A propriedade que se exige é **EUF-CMA** (*Existential Unforgeability under Chosen Message
Attack*): um adversário que conheça `pk` e possa pedir assinaturas de quantas mensagens
quiser — inclusive escolhidas por ele — não consegue produzir um par `(m*, σ*)` válido para
uma mensagem `m*` que ele nunca pediu, exceto com probabilidade desprezível.

Note com atenção **o que o teorema quantifica**. Ele diz respeito a um adversário que
*não tem `sk`*. Todo o edifício repousa nisso. As três hipóteses são:

| Hipótese | Se falhar |
|---|---|
| `sk` é secreta | o adversário assina como você; **nada** detecta |
| a função de hash é resistente a colisão | o adversário reusa uma assinatura em outro conteúdo (§ 3) |
| o problema matemático subjacente é difícil | tudo cai (§ 6) |

A primeira é a que falha no mundo real. As outras duas são as que fazem papers.

---

## 2. O que a assinatura de commit prova — enunciado preciso

> **Proposição.** Seja `c` um objeto commit contendo o campo `gpgsig` com assinatura `σ`, e
> seja `p` o payload de `c` (o objeto sem o campo `gpgsig`). Se `Verify(pk, p, σ) = 1`, então,
> sob as hipóteses da § 1, alguma entidade com acesso a `sk` executou `Sign(sk, p)` em algum
> momento anterior.

E é só isso. Vamos desmontar cada coisa que **não** decorre:

| Alegação comum | Decorre? | Por quê |
|---|---|---|
| "a pessoa X escreveu este código" | **não** | prova posse de `sk`; a ligação entre `sk` e "X" é externa e social |
| "a pessoa X estava ciente do conteúdo" | **não** | `Sign` é uma operação de máquina; ninguém prova que houve leitura |
| "este commit foi feito na data que consta" | **não** | as datas são campos do payload, escolhidas por quem assinou; podem ser qualquer coisa |
| "o código é seguro" | **não** | nada em `Verify` inspeciona semântica |
| "este é o commit mais recente" | **não** | não há noção de ordem ou de recência numa assinatura |
| "o histórico anterior está íntegro" | **sim, condicionalmente** | o payload inclui `parent`, e a cadeia de hashes é resistente a colisão |

Aquela linha sobre a data merece um parágrafo. `GIT_AUTHOR_DATE` e `GIT_COMMITTER_DATE` são
variáveis de ambiente. Uma assinatura sobre um payload que contém a data prova que a data
*estava lá* quando se assinou, não que o relógio dizia aquilo. **Uma assinatura não é um
carimbo de tempo.** Carimbo de tempo exige uma terceira parte (RFC 3161) ou um log de
transparência (§ 5).

---

## 3. Colisões de hash e o que elas fazem com a assinatura

Como se assina `H(m)` e não `m`, uma colisão `H(m₁) = H(m₂)` com `m₁ ≠ m₂` produz uma
assinatura válida para as duas mensagens. Duas modalidades, com implicações muito diferentes:

| Modalidade | O atacante | Perigo real |
|---|---|---|
| **colisão de prefixo idêntico** | escolhe os dois documentos inteiros | baixo: precisa que a vítima assine algo fabricado por ele |
| **colisão de prefixo escolhido** | escolhe dois prefixos **arbitrários**, e calcula sufixos que colidem | **alto**: permite colidir um documento legítimo com um malicioso |

### Os números do SHA-1

| Marco | Ano | Complexidade | Custo relatado |
|---|---|---|---|
| ataque teórico (Wang et al.) | 2005 | ~2⁶⁹ | — |
| **SHAttered** (Google + CWI), prefixo idêntico | 2017 | ~2⁶³·¹ | 6.500 anos-CPU + 110 anos-GPU |
| **SHA-1 is a Shambles** (Leurent & Peyrin), **prefixo escolhido** | 2020 | ~2⁶³·⁴ | ~US$ 75 mil pela computação realizada, com projeção de queda |

O detalhe que torna o segundo trabalho especialmente relevante aqui: **a aplicação
demonstrada foi contra a rede de confiança do PGP**. Os autores forjaram uma certificação de
chave — exatamente o mecanismo de vinculação de identidade discutido em
[10-fundamentos.md](10-fundamentos.md).

### Por que o Git não caiu

1. **`sha1collisiondetection`.** Desde 2017 o Git usa a biblioteca de Marc Stevens, que
   detecta as estruturas características dos ataques conhecidos e recusa o objeto. Custo:
   cerca de 2× mais lento no cálculo de hash. Limitação: detecta *ataques conhecidos*; é
   mitigação, não prova.
2. **A restrição estrutural.** O objeto colidente precisa ser um commit **sintaticamente
   válido**, com `tree` apontando para um conteúdo plausível, que passe em revisão de código.
   Isso é ordens de grandeza mais difícil que colidir dois PDFs, onde se esconde lixo em
   campos ignorados.
3. **Economia.** Setenta e cinco mil dólares por colisão útil é caro comparado a subornar,
   invadir uma máquina ou apenas contribuir por dois anos e ganhar confiança — que foi,
   afinal, o método do xz-utils.

### A transição para SHA-256

O Git suporta objetos SHA-256 desde a 2.29 (outubro de 2020):

```bash
git init --object-format=sha256 repo
git -C repo commit --allow-empty -m t
git -C repo log --format='%H' -1
# 43b17250db849bd134198ac04a4fae26efebea54bd79ee812df087bc6cc4c5f6   (64 hex, testado)
```

E, seis anos depois, quase ninguém usa. Motivo: **interoperabilidade**. Um repositório SHA-256
não conversa com um SHA-1; o GitHub não o hospeda; a maioria das ferramentas assume 40
caracteres hexadecimais. O código de interoperação entre os dois formatos foi projetado e
segue incompleto.

É o caso didático mais claro de que segurança avança por **custo de coordenação**, não por
mérito técnico. O problema é conhecido desde 2005, a solução existe desde 2020, e a migração
depende de todo o ecossistema mover-se junto — o que ninguém tem incentivo para financiar
sozinho.

---

## 4. O modelo de ameaça, formalizado

Adversários possíveis, e o que a assinatura faz com cada um:

| Adversário | Capacidade | Assinatura de commit protege? |
|---|---|---|
| **A₁** externo, sem credencial | pode ler o repositório público | não é ameaça a este controle |
| **A₂** credencial roubada (token, senha) | escreve no repositório como você | **sim** — é o caso de uso central |
| **A₃** colaborador legítimo, mal-intencionado | escreve e assina com a chave dele | **não** — mas atribui |
| **A₄** máquina do desenvolvedor comprometida | usa `sk` enquanto o agente está destravado | **não** |
| **A₅** chave privada exfiltrada | assina offline, quando quiser | **não** |
| **A₆** a plataforma (GitHub) comprometida ou compelida | reescreve o veredito, cadastra chave falsa | **não**, a menos que se verifique localmente |
| **A₇** rede / intermediário | modifica em trânsito | **sim**, e o TLS já cobria |

Duas leituras importantes desta tabela:

**A₂ é o vetor mais comum do mundo real** — vazamento de token em log, em pacote npm, em
repositório público, em notebook roubado. Fechar A₂ com uma configuração de 10 minutos é uma
das melhores relações custo-benefício disponíveis em segurança de desenvolvimento.

**A₃ é o vetor do xz-utils**, e a assinatura não faz nada contra ele — o backdoor entrou com
commits legitimamente assinados. Contra A₃ só funcionam revisão, análise, diversidade de
mantenedores e desconfiança de contribuições que ganham privilégio rápido demais.

---

## 5. Logs de transparência: o que eles acrescentam, e o problema que sobra

O problema apontado em [15 § 3](15-verificacao-no-github.md) — o veredito congelado, que não
retroage após revogação — é uma instância de um problema mais geral: **uma assinatura não
carrega tempo confiável**, e não há como provar que algo *não* foi assinado.

A resposta da década de 2020 é **transparência**, herdada do Certificate Transparency: além de
assinar, registre a assinatura num log público **apenas-anexação**, estruturado como uma
árvore de Merkle.

```
                 raiz (assinada periodicamente pelo log)
                /                    \
            h(01)                    h(23)
           /     \                  /     \
        h(0)    h(1)             h(2)    h(3)
         |       |                |       |
       reg₀    reg₁             reg₂    reg₃
```

Duas provas ficam disponíveis, ambas de tamanho `O(log n)`:

- **prova de inclusão** — este registro está no log de raiz `R`;
- **prova de consistência** — o log de raiz `R'` (agora) é uma extensão do de raiz `R`
  (antes), sem nada removido ou alterado.

O que isso resolve:

| Problema | Resolve? |
|---|---|
| a assinatura foi mesmo feita antes de tal data | **sim** — a inclusão no log a ancora no tempo |
| revogação não retroage | **sim** — dá para saber o que foi assinado antes da revogação |
| não há como saber se assinaram algo em meu nome | **sim** — o log é auditável, e a ausência é observável |
| e se o log mentir? | **parcialmente** — § abaixo |

É isso que o **Sigstore** implementa: Fulcio emite um certificado efêmero ligado à sua
identidade OIDC, você assina, e o registro vai para o **Rekor**. A chave privada é descartada.
A pergunta deixa de ser "quem tem a chave" e passa a ser "quem controlava aquela identidade
naquele minuto, segundo um log que ninguém pode reescrever".

### O problema que sobra: visão dividida

Um log malicioso pode apresentar **árvores diferentes para vítimas diferentes** — o
*split-view attack*. As provas de inclusão e consistência são internamente coerentes em cada
visão, e nenhuma das duas detecta nada sozinha.

A defesa exige **gossip**: os verificadores precisam trocar entre si as raízes que viram, e
comparar. Isso não é um detalhe de implementação — é um requisito de protocolo. E é a parte
que segue mal resolvida em praticamente todas as implantações reais de transparência, o
Certificate Transparency inclusive.

Formalmente: transparência **não elimina** a necessidade de confiança; ela a **transforma**,
de "confio no emissor" para "confio que a comunidade de verificadores é diversa e conversa
entre si". Isso é uma melhora real. Não é uma prova.

---

## 6. Pós-quântico

Um computador quântico com correção de erro em escala suficiente resolve logaritmo discreto
em curva elíptica e fatoração em tempo polinomial (Shor, 1994). Consequência direta:
**Ed25519, ECDSA e RSA quebram por completo** — não enfraquecem, quebram.

Prazo: não há consenso, e as estimativas sérias variam de "década de 2030" a "talvez nunca em
escala útil". O que **não** depende do prazo é o raciocínio de "colher agora, decifrar
depois" — e aqui vem uma assimetria interessante e pouco notada:

| Uso | Ameaça de "colher agora, decifrar depois" |
|---|---|
| **cifrar** | **alta** — o tráfego capturado hoje é decifrado no futuro |
| **assinar** | **baixa** — quebrar a chave depois não permite forjar assinatura no passado de forma crível, se houver registro de quando cada coisa foi assinada |

Ou seja: a migração pós-quântica é **urgente para cifra e menos urgente para assinatura**.
Isso explica por que a padronização e a implantação começaram pela troca de chaves — o
OpenSSH 10.0 já usa `mlkem768x25519-sha256` como padrão de acordo de chaves — e só agora
chegam à assinatura.

Os padrões do NIST (2024):

| Padrão | Nome | Base | Assinatura | Nota |
|---|---|---|---|---|
| FIPS 204 | **ML-DSA** (Dilithium) | reticulados | ~2,4 KB | o padrão de uso geral |
| FIPS 205 | **SLH-DSA** (SPHINCS+) | hash | ~7–30 KB | conservador; só depende de hash |
| FIPS 206 | FN-DSA (Falcon) | reticulados | ~0,7 KB | em finalização |

Estado em 13/08/2026:

- **OpenSSH 10.4** (06/07/2026) trouxe um esquema **ML-DSA 44 + Ed25519**, híbrido,
  experimental e opcional;
- **OpenPGP** tem a via aberta pela RFC 9580 e o GnuPG 2.5.x traz Kyber (ML-KEM) para cifra;
  assinatura PQC ainda não é o caminho corriqueiro;
- **Git e GitHub** não têm nada específico — eles delegam ao OpenSSH e ao GnuPG.

Duas consequências práticas quando a migração vier: assinaturas de 2,4 KB contra 173 bytes
mudam o tamanho do repositório de forma perceptível, e a abordagem híbrida (clássico +
pós-quântico juntos) será a regra durante toda a transição, porque ninguém quer trocar um
risco conhecido por um algoritmo novo sem histórico de criptanálise.

---

## 7. Limites que não são de implementação

Três resultados que valem enunciar porque não se resolvem com engenharia melhor:

**1. Não há como distinguir o titular da chave de quem tem a chave.** É a definição do
mecanismo, não uma falha. Qualquer sistema que precise dessa distinção precisa de um segundo
fator fora da criptografia — presença física, biometria, testemunho. Tokens com
`verify-required` movem a barra, e não mudam a natureza do problema.

**2. Vinculação de identidade é irredutivelmente social.** "Esta chave pertence à Ana" não é
um enunciado matemático. Toda solução — rede de confiança, autoridade certificadora,
plataforma, log de transparência — apenas escolhe **em quem** você deposita essa confiança.
Não existe a opção de não depositar em ninguém.

**3. Não se prova ausência.** Um log de transparência permite provar que algo *foi* assinado.
Provar que algo *nunca* foi assinado exige ver o log inteiro e confiar que ele é o log — o que
recai em (2).

---

## 8. Problemas em aberto

- **Gossip prático para logs de transparência.** Como fazer verificadores comuns trocarem
  raízes sem infraestrutura dedicada nem custo de privacidade?
- **Migração do SHA-1 no Git.** Existe caminho de interoperação incremental que alguém tenha
  incentivo para financiar?
- **Revogação retroativa.** Como marcar como suspeitos os commits assinados no intervalo
  entre um comprometimento e sua descoberta, sem invalidar trabalho legítimo?
- **Assinatura de intenção.** Como distinguir criptograficamente "assinei porque revisei" de
  "minha ferramenta assinou automaticamente"? Hoje são indistinguíveis, e essa é a raiz de
  boa parte do teatro de segurança do assunto.
- **Custo de assinatura pós-quântica em repositórios grandes.** 2,4 KB por commit, em
  repositórios com milhões de commits.

---

## Autoteste

1. Enuncie EUF-CMA e diga qual das suas hipóteses falha no mundo real.
2. Por que uma assinatura não é um carimbo de tempo?
3. Qual é a diferença prática entre colisão de prefixo idêntico e de prefixo escolhido?
4. Cite três razões pelas quais o Git não caiu com a quebra do SHA-1.
5. Por que a migração para SHA-256 não aconteceu, se a solução existe desde 2020?
6. Contra qual adversário da tabela a assinatura protege bem? Contra qual não faz nada?
7. O que um log de transparência acrescenta, e qual problema permanece?
8. Por que a urgência pós-quântica é menor para assinatura que para cifra?
9. Por que "vinculação de identidade é irredutivelmente social"?

*(Respostas: 1 — nenhum adversário sem `sk` produz par válido para mensagem não consultada;
falha na prática a hipótese de que `sk` é secreta. 2 — as datas são campos do payload,
escolhidos por quem assina; carimbo exige terceira parte ou log. 3 — no de prefixo escolhido o
atacante parte de dois documentos arbitrários, o que permite colidir um legítimo com um
malicioso. 4 — detecção de colisão desde 2017; a exigência de que o objeto colidente seja
código plausível; e o custo, alto frente a alternativas mais baratas de ataque. 5 — falta de
interoperabilidade e ausência de quem financie a coordenação do ecossistema. 6 — protege bem
contra credencial roubada (A₂); não faz nada contra colaborador legítimo mal-intencionado
(A₃). 7 — ancora as assinaturas no tempo e permite auditoria; permanece o ataque de visão
dividida, que exige gossip entre verificadores. 8 — "colher agora, decifrar depois" ameaça
sigilo; quebrar a chave no futuro não forja o passado de forma crível se houver registro
temporal. 9 — porque "esta chave é da Ana" não é enunciado matemático; toda solução apenas
escolhe em quem confiar.)*

---

**Próximo:** [65-estado-da-arte.md](65-estado-da-arte.md).
