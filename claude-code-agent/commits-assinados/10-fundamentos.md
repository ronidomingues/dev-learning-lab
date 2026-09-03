# 10 · Fundamentos

> Nível: iniciante → intermediário · Atualizado em 13/08/2026

Aqui construímos, do zero, o vocabulário e o modelo mental. Nada de "é assim porque o padrão
manda": cada peça vem com o problema que ela resolve.

---

## 1. Hash: o resumo que denuncia qualquer mudança

**Intuição.** Imagine uma máquina que pega qualquer coisa — um arquivo de 3 KB, um filme de
40 GB, uma frase — e devolve sempre um número de tamanho fixo. Como se fosse um lacre
numérico do conteúdo.

**Definição.** Uma **função de hash criptográfica** transforma uma entrada de tamanho
arbitrário em uma saída de tamanho fixo (o *digest*, ou resumo), com três propriedades:

| Propriedade | O que garante |
|---|---|
| **determinística** | a mesma entrada dá sempre a mesma saída |
| **resistente à pré-imagem** | dado o resumo, não dá para descobrir a entrada |
| **resistente a colisão** | não dá para achar duas entradas diferentes com o mesmo resumo |

**Concreto.** Veja o efeito avalanche — um caractere muda, e o resumo inteiro muda:

```bash
echo -n "commit assinado" | sha256sum
echo -n "commit assinada" | sha256sum
```

```
1c9b09e5e1c3e0ff9f2c5d3ba0f1e5a3... 
7a4f2ae0e4b58cc3ab21f0d9a8a2b0c1...
```

**Por que isso importa aqui.** Assinar 40 GB de dados seria caríssimo. Então **não se assina
o conteúdo: assina-se o resumo dele**. Como o resumo muda a cada byte alterado, assinar o
resumo equivale a assinar o conteúdo — desde que ninguém consiga fabricar dois conteúdos com
o mesmo resumo. Guarde essa condição: é ela que está em jogo quando alguém diz que "o SHA-1
foi quebrado" ([60-teoria-avancada.md](60-teoria-avancada.md)).

---

## 2. Criptografia assimétrica: duas chaves que se completam

**Intuição.** Um cadeado com duas chaves diferentes: uma tranca e a outra destranca. Você
distribui cópias da chave que **destranca** para o mundo inteiro, e guarda a que **tranca**.
Quem receber algo trancado sabe que só você poderia ter trancado.

**Definição.** Um par de chaves é um par de números matematicamente relacionados:

- a **chave privada** — secreta, fica com você;
- a **chave pública** — derivada da privada, distribuída livremente.

E a relação é de mão única: da privada se calcula a pública em milissegundos; da pública para
a privada, ninguém sabe fazer em tempo útil.

**O ponto que confunde todo mundo.** Assimetria serve para duas coisas *opostas*:

| Uso | Você usa a chave... | Qualquer um usa a chave... | Para quê |
|---|---|---|---|
| **cifrar** | pública do destinatário | privada dele | ninguém mais lê |
| **assinar** | **sua privada** | **sua pública** | todos conferem que foi você |

Neste assunto, só o segundo caso importa. **Commit assinado não é commit secreto.** Todo o
conteúdo continua legível por qualquer um. A assinatura acrescenta *procedência*, não sigilo.

**Concreto.** As duas metades de um par Ed25519:

```
# pública — 68 caracteres, pode ir para o mundo:
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINi2+bz2l8XnlynCFEuDzRyQkaC4VJmWOiCCFh4aa6Q0 ana@exemplo.dev

# privada — fica em ~/.ssh/id_assinatura, modo 600, e nunca sai de lá
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
...
```

### Quais algoritmos existem, e qual escolher

| Algoritmo | Tamanho da chave | Assinatura | Veredito em 2026 |
|---|---|---|---|
| **Ed25519** | 256 bits | 64 bytes | **use este**: rápido, curto, sem parâmetros para errar |
| ECDSA P-256 | 256 bits | ~71 bytes | funciona; mais fácil de implementar errado |
| RSA 4096 | 4096 bits | 512 bytes | seguro e lento; escolha conservadora onde algo velho exige |
| RSA 1024 | 1024 bits | — | **não use**: fora do aceitável há mais de uma década |
| DSA | 1024 bits | — | **não use**: removido do OpenSSH |
| ML-DSA (Dilithium) | — | ~2,4 KB | pós-quântico; experimental no OpenSSH 10.4 ([65](65-estado-da-arte.md)) |

Por que Ed25519 e não RSA? Três motivos concretos: chave 16 vezes menor, assinatura 8 vezes
menor, e — o que mais importa na prática — **não tem parâmetros a escolher**. Boa parte das
falhas históricas de ECDSA e RSA veio de escolher mal um parâmetro (o famoso caso do
PlayStation 3, em 2010, foi um *nonce* de ECDSA repetido). Ed25519 não te dá essa corda.

---

## 3. Assinatura digital: juntando as duas peças

**A mecânica, em três passos:**

```
ASSINAR                                   VERIFICAR
─────────────────────────────             ──────────────────────────────
1. resumo = hash(conteúdo)                1. resumo₁ = hash(conteúdo recebido)
2. assinatura = f(resumo, privada)        2. resumo₂ = g(assinatura, pública)
3. envia conteúdo + assinatura            3. resumo₁ == resumo₂ ?  → boa
```

Em Mermaid, para fixar:

```mermaid
flowchart LR
    A[conteúdo do commit] --> B[hash]
    B --> C[resumo]
    C --> D{{assinar com<br/>chave privada}}
    D --> E[assinatura]
    A --> F[objeto commit<br/>conteúdo + assinatura]
    E --> F
    F --> G{{verificar com<br/>chave pública}}
    G -->|resumos batem| H[✔ boa]
    G -->|não batem| I[✘ ruim]
```

**O que uma assinatura válida prova, exatamente:**

> Quem produziu esta assinatura tinha, no momento em que a produziu, acesso à chave privada
> correspondente a esta chave pública. E o conteúdo não mudou um único bit desde então.

Leia de novo, porque o resto do curso é consequência disso. Note o que **não** está ali:
nada sobre *quem é* a pessoa, nada sobre *intenção*, nada sobre *qualidade*.

---

## 4. O problema difícil: de quem é esta chave pública?

A matemática acima é a parte fácil, e está resolvida desde os anos 1970. O problema que
sobra — e que ainda não tem solução limpa — é este:

> Recebi uma chave pública que diz ser da Ana. **Como sei que é da Ana?**

Isso se chama **problema de vinculação de identidade** (*identity binding*), ou, em versão
mais crua, *problema da distribuição de chaves*. Três respostas foram tentadas na história,
e vale conhecer as três porque elas explicam as ferramentas que temos hoje.

### a) Rede de confiança (PGP, 1992)

Cada pessoa assina a chave de quem ela conheceu pessoalmente. Se você confia em três pessoas
que assinaram a chave da Ana, você aceita a chave da Ana. Sem autoridade central.

**Fracassou**, e é importante entender por quê — não foi por falha técnica:

- exigia encontros presenciais (*keysigning parties*) que não escalam;
- a métrica de confiança é subjetiva e ninguém a entendia;
- os servidores de chaves aceitavam qualquer assinatura de qualquer um, o que permitiu
  ataques de *envenenamento* (inundar uma chave com assinaturas falsas até quebrar os
  clientes) — o que efetivamente derrubou a rede SKS em 2019.

Hoje a rede de confiança é história, não prática. Se alguém te propuser montar uma em 2026,
peça um argumento muito bom.

### b) Autoridade certificadora (X.509, S/MIME, TLS)

Uma entidade em quem todos confiam assina as chaves de todos. É o modelo dos certificados de
site (HTTPS) e do S/MIME.

**Funciona**, com um custo: você troca "confiar em muita gente" por "confiar totalmente em
uma". Se a autoridade for comprometida ou coagida, tudo cai junto. E a burocracia é real.

### c) Confiança no primeiro uso, delegada à plataforma (o modelo de fato, hoje)

É o que o GitHub faz, e é bom nomear com franqueza: **o GitHub é a autoridade
certificadora**. Você prova sua identidade a ele uma vez (conta, e-mail verificado, 2FA),
cadastra sua chave pública, e daí em diante ele afirma para os outros que aquela chave é sua.

O selo `Verified` significa, literalmente: *"o GitHub afirma que a chave que assinou este
commit pertence a uma conta que tem este e-mail verificado."* Nada mais, e nada menos.

**A consequência incômoda, e que ninguém gosta de dizer em voz alta:** se o GitHub quiser
mentir, ou se for comprometido, o selo mente junto. A assinatura protege você de outros
usuários e de invasores externos; **não** protege você da plataforma. Para quem precisa disso,
existem transparência de log e verificação local com `allowed_signers` — e as duas têm limites
próprios, discutidos em [60-teoria-avancada.md](60-teoria-avancada.md).

---

## 5. Os cinco porquês, aplicados

Vamos até o fundo em duas perguntas centrais, sem parar no primeiro nível.

### "Por que o Git não verifica identidade sozinho?"

1. **Por quê?** Porque `user.name` e `user.email` são só texto no objeto commit.
2. **Por que são só texto?** Porque o Git não tem noção de conta, login ou usuário.
3. **Por que não tem?** Porque foi projetado para ser **distribuído**: não existe servidor
   central que pudesse manter uma lista de quem é quem.
4. **Por que distribuído?** Porque nasceu em abril de 2005 para o desenvolvimento do kernel
   Linux, com milhares de colaboradores, sem hierarquia central de contas, depois que a
   licença do BitKeeper foi revogada para o projeto.
5. **Por que isso seria incompatível com verificar identidade?** Porque verificar identidade
   exige uma **autoridade** — e uma autoridade é exatamente o ponto central que a arquitetura
   se recusava a ter.

**Parada legítima:** decisão de projeto histórica e documentada. E ela também explica por que
a solução veio como camada de cima (assinatura opcional), e não como mudança no modelo.

### "Por que a assinatura fica dentro do objeto commit e não ao lado?"

1. **Por quê?** Porque o campo `gpgsig` faz parte do objeto commit.
2. **Por que dentro?** Porque assim ela viaja junto: clonar o repositório traz as assinaturas
   sem nenhum protocolo extra.
3. **Por que isso importa?** Porque num sistema distribuído não há de quem "buscar as
   assinaturas depois" — o repositório tem de ser autossuficiente.
4. **Mas se a assinatura está dentro, o que exatamente é assinado?** O objeto commit **sem**
   o campo `gpgsig` — senão seria preciso assinar algo que contém a própria assinatura.
5. **Por que essa solução e não outra?** Porque manter a assinatura fora quebraria a
   propriedade central do Git: o hash de um objeto é função de todo o seu conteúdo. Se a
   assinatura ficasse fora, um commit assinado e o mesmo commit sem assinatura teriam o mesmo
   hash — e não haveria como dizer qual é qual.

**Parada legítima:** consequência necessária do modelo de objetos endereçados por conteúdo.
A mecânica exata está em [12-anatomia-do-commit.md](12-anatomia-do-commit.md).

---

## 6. Vocabulário mínimo

| Termo | Definição |
|---|---|
| **hash / resumo / digest** | saída de tamanho fixo de uma função de hash |
| **colisão** | duas entradas diferentes com o mesmo resumo |
| **par de chaves** | chave privada + chave pública correspondente |
| **impressão digital** (*fingerprint*) | hash da chave pública, usado para identificá-la de forma curta |
| **assinatura** | valor calculado a partir do resumo e da chave privada |
| **verificação** | conferir uma assinatura com a chave pública |
| **UID** (OpenPGP) | nome + e-mail associados a uma chave |
| **subchave** | chave secundária, derivada da principal, para uma finalidade só |
| **revogação** | declaração pública de que uma chave não deve mais ser aceita |
| **namespace** (SSHSIG) | rótulo que separa domínios de uso de uma assinatura |
| **principal** (SSHSIG) | o rótulo de identidade no `allowed_signers` |
| **KDF** | função que transforma sua frase secreta na chave que cifra a chave privada em disco |

O glossário completo está em [GLOSSARIO.md](GLOSSARIO.md).

---

## 7. Onde cada peça aparece na prática

```
sua frase secreta ──KDF──▶ cifra ──▶ ~/.ssh/id_assinatura   (chave privada em disco)
                                            │
                                    ssh-agent (destravada em memória)
                                            │
git commit ──▶ objeto commit ──hash──▶ resumo ──assina──▶ campo gpgsig
                                                              │
                                                          git push
                                                              │
                        GitHub: a chave é de alguma conta? o e-mail é verificado?
                                                              │
                                                        ✔ Verified
```

---

## Autoteste

1. Por que se assina o resumo e não o conteúdo?
2. Qual a diferença entre cifrar e assinar, em termos de qual chave se usa?
3. Um commit assinado é secreto?
4. Enuncie, com precisão, o que uma assinatura válida prova.
5. Por que a rede de confiança do PGP fracassou? Cite duas razões.
6. Em que sentido o GitHub é uma autoridade certificadora?
7. Por que o Git não verifica identidade sozinho? Vá até a raiz histórica.
8. Por que Ed25519 é preferível a RSA hoje, além do tamanho?

*(Respostas: 1 — assinar dados grandes é caro; o resumo representa o conteúdo, desde que não
haja colisão viável. 2 — cifrar usa a pública do destinatário; assinar usa a **sua** privada.
3 — não; o conteúdo permanece legível, a assinatura acrescenta procedência. 4 — que quem
assinou tinha acesso à chave privada correspondente naquele momento, e que o conteúdo não
mudou desde então. 5 — não escalava (exigia encontros presenciais) e os servidores eram
vulneráveis a envenenamento por assinaturas falsas. 6 — ele afirma, para terceiros, que uma
chave pública pertence a uma identidade que ele verificou. 7 — porque nasceu distribuído,
sem servidor central, e verificar identidade exigiria uma autoridade central. 8 — não tem
parâmetros a escolher, e boa parte das falhas históricas veio de parâmetros mal escolhidos.)*

---

**Próximo:** [11-historia.md](11-historia.md).
