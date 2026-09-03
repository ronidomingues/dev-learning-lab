# 60 · Teoria avançada

**Nível:** pesquisa · **Data:** 31/08/2026
**Pré-requisitos:** [12](12-handshake.md), [14](14-criptografia-do-tls.md), noções de
probabilidade e de teoria da computação. Nada aqui é necessário para operar TLS.

O que significa dizer que "o TLS 1.3 é seguro" — e o que essa afirmação **não** cobre.

---

## 1. O que é uma prova de segurança

Uma prova de segurança em criptografia **nunca** diz "é impossível quebrar". Ela diz:

> Se existir um adversário que quebre o protocolo P com vantagem ε em tempo t,
> então existe um adversário que resolve o problema difícil D com vantagem ε′ ≈ ε/q
> em tempo t′ ≈ t.

Isto é uma **redução**. A conclusão real é: *quebrar P não é mais fácil do que resolver D*.
Se você acredita que D é difícil (fatoração, logaritmo discreto, LWE), então acredita
que P é seguro.

Três coisas que uma prova sempre carrega e que quase sempre são omitidas na divulgação:

1. **O modelo.** O que o adversário pode fazer, e o que se assume idealizado.
2. **As hipóteses.** Quais problemas se assume difíceis, e quais primitivas se assume
   ideais (ROM, PRF, etc.).
3. **A perda de justeza** (*tightness loss*). O fator `q` acima é real: se a redução
   perde um fator de 2^30, uma prova "de 128 bits" pode entregar 98 bits de segurança
   concreta para os parâmetros escolhidos.

---

## 2. Os dois mundos: simbólico e computacional

| | **Simbólico** (Dolev–Yao) | **Computacional** (redução) |
|---|---|---|
| Criptografia | caixa-preta perfeita; termos algébricos | funções sobre bits, com probabilidade |
| Adversário | controla a rede, não quebra a cripto | qualquer algoritmo de tempo polinomial |
| Automação | **alta** (Tamarin, ProVerif) | baixa (provas à mão; CryptoVerif ajuda) |
| Encontra | falhas de **lógica** do protocolo | falhas de **redução criptográfica** |
| Não vê | ataques probabilísticos, canais laterais | erros de lógica em detalhes de estado |

Os dois são necessários e complementares. É por isso que o TLS 1.3 foi analisado
pelos dois durante o desenho — algo inédito para um protocolo desse porte.

---

## 3. O modelo ACCE

Antes de 2012 não havia sequer uma **definição** adequada do que "TLS é seguro"
significaria. O problema: o TLS não é um protocolo de acordo de chaves puro (a chave é
usada dentro do próprio handshake, no `Finished`), então as definições clássicas de
AKE (*Authenticated Key Exchange*) não se aplicam.

**ACCE** (*Authenticated and Confidential Channel Establishment*), de Jager, Kohlar,
Schäge e Schwenk (CRYPTO 2012), resolveu isso definindo segurança do **canal inteiro**
— estabelecimento e uso juntos —, e não da chave isoladamente.

O jogo, em resumo: o adversário controla todas as sessões, pode corromper partes,
e no final escolhe uma sessão-alvo "limpa" e tenta distinguir se o que ela transporta
é o texto real ou lixo. Se a vantagem dele for desprezível, o protocolo é ACCE-seguro.

**O resultado, e a ironia:** provou-se que o TLS 1.2 com **ECDHE** é ACCE-seguro,
enquanto o TLS 1.2 com **RSA-transporte** só é demonstrável sob hipóteses bem mais
fortes e artificiais. A teoria confirmou, com anos de antecedência, o que a prática
descobriria dolorosamente com o ROBOT.

---

## 4. O TLS 1.3 e a análise durante o desenho

O TLS 1.3 é o primeiro protocolo de larga escala projetado **com** verificação formal
acontecendo em paralelo aos rascunhos, e não depois.

| Trabalho | Método | Contribuição |
|---|---|---|
| **Cremers, Horvat, Scott, van der Merwe** (S&P 2016) | Tamarin, sobre o Draft 10 | primeira análise simbólica ampla; encontrou problemas de autenticação em 0-RTT/PSK |
| **Cremers et al.** (CCS 2017) | Tamarin, Draft 21 | modelo simbólico completo, fiel ao formato de fio; **é o modelo reaproveitado até hoje** para analisar variantes |
| **Bhargavan, Blanchet, Kobeissi** (S&P 2017) | ProVerif + CryptoVerif | simbólico **e** computacional; Drafts 18 e 20 |
| **Dowling, Fischlin, Günther, Stebila** | prova à mão, modelo multi-estágio | segurança das chaves de cada estágio do escalonamento |
| **miTLS / Project Everest** | implementação verificada (F*) | código com prova, não só o papel |

**Achados que mudaram o padrão:** a análise formal levou a mudanças reais no protocolo,
principalmente em torno do 0-RTT e da retomada por PSK, e à decisão de **assinar o
transcript inteiro** no `CertificateVerify`. É o argumento mais forte que existe a favor
de verificação formal em protocolos: ela pagou-se antes do lançamento.

---

## 5. O que continua **fora** das provas

Esta seção é a razão de o arquivo existir.

| Fora do escopo | Por quê |
|---|---|
| **Canais laterais** | os modelos não têm noção de tempo de execução, cache ou consumo. Lucky13 e Raccoon são invisíveis para eles |
| **Bugs de implementação** | Heartbleed e "goto fail" não violaram nenhuma prova: o código simplesmente não era o protocolo provado |
| **A PKI** | as provas assumem que "a parte honesta tem a chave certa". Quem garante isso é a PKI, que **não** tem prova — é um sistema social |
| **Ossificação e *middleboxes*** | o modelo assume dois participantes; a realidade tem dezenas de intermediários |
| **0-RTT contra repetição** | a repetição é **admitida** pelo padrão. Não é falha da prova: é uma propriedade que o protocolo não promete |
| **Uso incorreto pela aplicação** | verificação desligada, cookie sem `Secure`, conteúdo misto |
| **Aleatoriedade ruim** | toda prova assume um gerador uniforme. Sem isso, tudo cai (Debian OpenSSL, 2008; ECDSA em Android, 2013) |

> **A distância entre "provado seguro" e "seguro"** é exatamente a distância entre o
> modelo e o mundo. Uma prova é uma afirmação precisa e valiosa sobre um objeto
> matemático. O que roda no seu servidor é um programa em C compilado por um compilador
> com otimizações, rodando num sistema operacional multiusuário, numa CPU com execução
> especulativa. **Todos os ataques reais dos últimos 15 anos aconteceram nessa distância.**

---

## 6. Fronteiras abertas de pesquisa

### 6.1 KEMTLS — autenticação por KEM em vez de assinatura

Proposta de Schwabe, Stebila e Wiggers (CCS 2020): substituir a **assinatura** do
servidor por um **encapsulamento de chave**. O servidor prova posse da chave privada
decapsulando um segredo, em vez de assinar.

**Motivação:** no mundo pós-quântico, as assinaturas são enormes (ML-DSA: ~2,4 KB;
SLH-DSA: 8–30 KB) enquanto os KEMs são relativamente compactos (ML-KEM-768: ~1,1 KB).
KEMTLS troca o caro pelo barato.

**Custo:** o handshake fica **implicitamente** autenticado — o cliente só tem certeza da
identidade do servidor depois de receber dados. Para HTTPS isso é aceitável; para
outros usos, não. Foi verificado formalmente em Tamarin (eprint 2022/1111), reusando
o modelo de Cremers et al.

**Status:** pesquisa consolidada, mas **não** é o caminho que a indústria seguiu — ver
[65 §3](65-estado-da-arte.md), sobre Merkle Tree Certificates.

### 6.2 O problema do tamanho na autenticação pós-quântica

O núcleo do problema, em números:

```
Hoje (ECDSA P-256):        cadeia + SCTs + assinaturas  ≈   3 KB
Com ML-DSA ingênuo:                                     ≈  14,7 KB
```

Por que isso importa tanto: a **janela inicial de congestionamento** do TCP é de ~10
pacotes (~14 KB). Estourar isso obriga a esperar um RTT a mais antes de completar o
handshake — e em rede móvel isso é perceptível. Mais: `ClientHello` maior que a MTU
revelou *middleboxes* que não lidam com fragmentação.

Linhas de ataque ao problema: **Merkle Tree Certificates** (a que venceu, [65 §3](65-estado-da-arte.md)),
supressão de certificados intermediários por cache, compressão de certificados
(RFC 8879), e KEMTLS.

### 6.3 Provas com justeza (*tight*) e segurança concreta

Muitas provas do TLS perdem fatores grandes na redução. Trabalhos recentes buscam
reduções justas, para que a escolha de parâmetros seja **derivada** da prova em vez de
convencional. É teoria com consequência prática direta: sem justeza, "128 bits de
segurança" é uma etiqueta, não um número.

### 6.4 Verificação de implementações, não só de protocolos

**Project Everest** (Microsoft Research, INRIA e outros) produziu o **miTLS** e o
**HACL\***, uma biblioteca criptográfica **verificada em F\*** — com prova de correção
funcional, ausência de vazamento por tempo e segurança de memória. Partes do HACL\*
estão em produção no **Firefox** (via NSS) e no **Linux**.

**Por que isso importa mais que provas de protocolo:** Heartbleed e goto fail foram
bugs de implementação. Provar o protocolo não os pegaria; provar o código, sim.

### 6.5 Privacidade além do conteúdo

ECH resolve o SNI. Continuam expostos: o **IP de destino** e o **padrão de tráfego**.
Linhas ativas: *Oblivious HTTP* (RFC 9458), que separa quem sabe o quê entre dois
servidores; MASQUE/proxying sobre QUIC (base do Private Relay da Apple); e defesas
contra *website fingerprinting* por análise de tamanhos e tempos — problema em aberto,
com resultados de aprendizado de máquina cada vez mais fortes do lado do atacante.

### 6.6 Segurança pós-comprometimento

TLS dá sigilo **futuro** (o passado fica protegido se a chave vazar depois). Não dá
**segurança pós-comprometimento**: se o atacante obtém o estado da sessão agora, ele
lê tudo daqui para a frente. Protocolos de mensageria (Signal, com *double ratchet*)
resolvem isso com rechaveamento contínuo. O `KeyUpdate` do TLS 1.3 é um passo tímido
nessa direção — e a pergunta "vale a pena trazer *ratcheting* completo para o TLS?"
está em aberto.

---

## 7. Como ler um paper desta área

1. **Ache o modelo antes de tudo.** Simbólico ou computacional? Que capacidades o
   adversário tem? O que é idealizado?
2. **Ache as hipóteses.** Gap-DH? LWE? Modelo do oráculo aleatório?
3. **Ache a perda de justeza.** Costuma estar escondida no enunciado do teorema.
4. **Ache a seção "limitations".** É a parte mais honesta e a menos lida.
5. **Pergunte:** este resultado sobrevive a uma implementação real, com canais laterais
   e uma PKI imperfeita?

**Por onde começar, na ordem:**

- Cremers, Horvat, Hoyland, Scott, van der Merwe — *A Comprehensive Symbolic Analysis
  of TLS 1.3* (CCS 2017). O modelo Tamarin de referência.
- Bhargavan, Blanchet, Kobeissi — *Verified Models and Reference Implementations for
  the TLS 1.3 Standard Candidate* (IEEE S&P 2017).
- Jager, Kohlar, Schäge, Schwenk — *On the Security of TLS-DHE in the Standard Model*
  (CRYPTO 2012). O paper que criou o ACCE.
- Schwabe, Stebila, Wiggers — *Post-Quantum TLS Without Handshake Signatures* (CCS 2020). KEMTLS.
- Georgiev et al. — *The Most Dangerous Code in the World* (CCS 2012). Não é teoria,
  e talvez seja o mais útil de todos.

Links em [95-referencias.md](95-referencias.md).

---

## Autoteste

1. O que uma prova de segurança realmente afirma? O que ela nunca afirma?
2. Quais são os três elementos que toda prova carrega e que a divulgação costuma omitir?
3. Compare o modelo simbólico e o computacional: o que cada um encontra e o que cada um não vê?
4. Por que as definições clássicas de AKE não serviam para o TLS, e o que o ACCE fez?
5. Qual resultado do ACCE antecipou, na teoria, o que o ROBOT mostraria na prática?
6. Cite duas mudanças no TLS 1.3 motivadas por análise formal durante o desenho.
7. Liste cinco coisas que ficam fora de qualquer prova de segurança do TLS.
8. O que é KEMTLS, que problema resolve, e qual é o custo?
9. Por que 14,7 KB de dados de autenticação é um problema, e o que a janela de congestionamento tem a ver?
10. Qual é a diferença entre sigilo futuro e segurança pós-comprometimento?
11. Ao ler um paper da área, quais são os cinco passos?

*Respostas: §1, §1, §2, §3, §3, §4, §5, §6.1, §6.2, §6.6, §7.*

---

**Próximo:** [65-estado-da-arte.md](65-estado-da-arte.md) — onde o campo está em agosto de 2026.
