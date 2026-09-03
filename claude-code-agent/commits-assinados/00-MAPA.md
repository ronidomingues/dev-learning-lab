# Commits assinados — mapa do assunto

> **Como configurar commits assinados por GPG ou SSH no GitHub, e o que isso realmente
> significa.** Do "qualquer um pode commitar no seu nome" até EUF-CMA, colisão de SHA-1 e
> assinatura pós-quântica.
>
> Produzido em 13/08/2026 · 26 documentos + laboratório executável · ~7.700 linhas

---

## Em uma frase

No Git, o campo "autor" é uma etiqueta que o próprio autor escreve — a assinatura é o que
transforma essa etiqueta em prova.

---

## O que você saberá ao final

**Prático**

- configurar assinatura por **SSH** e por **GPG**, nos três sistemas operacionais, e ter o
  selo `Verified` no GitHub;
- diagnosticar em minutos qualquer `Unverified`, sabendo a que perguntar e a quem;
- ler `%G?` sem consultar tabela, e saber o que fazer com cada código;
- montar `allowed_signers`, aposentar chave sem invalidar o passado, renovar chave vencida;
- fazer bot e CI assinarem, e pôr uma porta de qualidade que reprova de verdade;
- implantar a exigência numa equipe sem travar o time.

**Conceitual**

- por que o Git nasceu sem verificar identidade, e por que isso não vai mudar;
- o que exatamente é assinado dentro de um commit — reconstruído à mão;
- por que rebase e squash "apagam" assinaturas;
- por que o Git dá `G` a uma assinatura atribuída à pessoa errada;
- o que o selo `Verified` prova, e os seus quatro pontos cegos.

**De pesquisa**

- o enunciado formal do que uma assinatura garante, e sob quais hipóteses;
- o estado do SHA-1 no Git e por que a migração para SHA-256 não aconteceu;
- o que logs de transparência acrescentam, e o problema de visão dividida que sobra;
- por que a urgência pós-quântica é menor para assinatura que para cifra.

---

## Roteiro de leitura

### Só quero configurar hoje (30 min)

```
02 (checklist) → 03 (só a sua seção de SO) → 04 (a trilha escolhida)
```

### Quero entender o que estou fazendo (1 dia)

```
01 → 02 → 03 → 04 → 07-projeto-modelo → 06 → 10 → 12 → 15 → 75
```

### Quero implantar na equipe (1 semana)

```
o roteiro acima → 17 → 18 → 19 → 80 → 70 (labs 9 a 12)
```

### Quero dominar o assunto

```
tudo, na ordem numérica
```

---

## Os arquivos

### Bloco A · Porta de entrada

| Arquivo | O que é | Nível |
|---|---|---|
| [01-introducao-leigo.md](01-introducao-leigo.md) | por que qualquer um pode commitar no seu nome — sem jargão | iniciante |
| [02-pre-requisitos.md](02-pre-requisitos.md) | o que saber e ter, tempo realista, rota de resgate | iniciante |
| [03-instalacao.md](03-instalacao.md) | manual de campo: Git, GnuPG, agente, `pinentry`, OpenSSH, `gh` — por SO, com tabela de erros literais | iniciante |
| [04-como-comecar.md](04-como-comecar.md) | **as duas trilhas lado a lado**, do zero ao selo `Verified` | iniciante |
| [05-manual-de-uso.md](05-manual-de-uso.md) | referência por tarefa: config, placeholders, verificação, API | iniciante–intermediário |
| [06-exemplos.md](06-exemplos.md) | 14 receitas completas, incluindo dois casos reais | iniciante–avançado |
| [07-projeto-modelo/](07-projeto-modelo/) | **laboratório executável em 15 atos**, com as falhas de propósito | iniciante–intermediário |

### Bloco B · Núcleo

| Arquivo | O que é | Nível |
|---|---|---|
| [10-fundamentos.md](10-fundamentos.md) | hash, par de chaves, assinatura, e o problema difícil: de quem é esta chave? | iniciante–intermediário |
| [11-historia.md](11-historia.md) | de Zimmermann e o processo criminal ao SSHSIG; por que o campo se chama `gpgsig` | intermediário |
| [12-anatomia-do-commit.md](12-anatomia-do-commit.md) | o objeto por dentro; o payload reconstruído e verificado à mão | intermediário |
| [13-gpg-a-fundo.md](13-gpg-a-fundo.md) | subchaves, expiração, revogação, backup, migração | intermediário–avançado |
| [14-ssh-signing-a-fundo.md](14-ssh-signing-a-fundo.md) | SSHSIG decodificado, `allowed_signers`, KRL, certificados SSH | intermediário–avançado |
| [15-verificacao-no-github.md](15-verificacao-no-github.md) | como o selo é decidido, vigilant mode, e os quatro pontos cegos | intermediário |
| [16-hardware-e-agentes.md](16-hardware-e-agentes.md) | agentes, `pinentry`, YubiKey, "no editor não funciona" | intermediário |
| [17-automacao-e-ci.md](17-automacao-e-ci.md) | bots, `gitsign`, DCO × assinatura, verificação na CI | intermediário–avançado |
| [18-politica-de-equipe.md](18-politica-de-equipe.md) | rulesets, implantação em 6 semanas, o que quebra | intermediário–avançado |
| [19-como-escolher.md](19-como-escolher.md) | árvore de decisão e recomendação por perfil | intermediário |
| [60-teoria-avancada.md](60-teoria-avancada.md) | EUF-CMA, colisões, modelo de ameaça, transparência, pós-quântico | pesquisa |
| [65-estado-da-arte.md](65-estado-da-arte.md) | agosto de 2026: versões, três debates abertos, regulação, previsões | avançado |

### Bloco C · Prática e erros

| Arquivo | O que é |
|---|---|
| [70-pratica.md](70-pratica.md) | 12 laboratórios progressivos, do "forje um commit" à simulação de incidente |
| [75-armadilhas.md](75-armadilhas.md) | 26 armadilhas, más práticas e mitos, com o porquê de cada um persistir |

### Bloco D · Economia e ecossistema

| Arquivo | O que é |
|---|---|
| [80-custos-e-licencas.md](80-custos-e-licencas.md) | gratuito na base; onde aparece o primeiro custo real; licenças; custos ocultos |
| [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) | cursos gratuitos PT/EN/FR e a verdade sobre certificações |

### Bloco E · Fontes

| Arquivo | O que é |
|---|---|
| [90-bibliografia.md](90-bibliografia.md) | livros comentados, com o que é legalmente gratuito marcado |
| [95-referencias.md](95-referencias.md) | RFCs, `PROTOCOL.sshsig`, papers, código-fonte, pessoas |
| [GLOSSARIO.md](GLOSSARIO.md) | ~90 termos definidos, mais a tabela de `%G?` e os pares que se confundem |

---

## As cinco coisas deste curso que você não encontra em tutorial

1. **O Git não compara o assinante com o autor do commit.** Um commit da Ana, com o
   `allowed_signers` dizendo que aquela chave é do Roberto, sai `[G]` com o nome do Roberto.
   Demonstrado no ato 9 do [projeto-modelo](07-projeto-modelo/).
2. **A verificação do GitHub é congelada no tempo.** Revogar a chave hoje não altera o selo
   de nada que já foi verificado — nem deveria, mas as consequências são incômodas
   ([15 § 3](15-verificacao-no-github.md)).
3. **O que exatamente é assinado**, reconstruído à mão e verificado sem o Git
   ([12 § 3](12-anatomia-do-commit.md)).
4. **Chave GPG vencida impede assinar, e não invalida o passado** — o commit falha e não é
   criado; o histórico passa a `[Y]` e continua `Verified` no GitHub.
5. **Assinatura não impede código malicioso.** Os commits do backdoor do xz-utils estavam
   legitimamente assinados.

---

## Estado deste material

| Bloco | Status |
|---|---|
| A · porta de entrada | ✅ completo |
| B · núcleo | ✅ completo |
| C · prática e erros | ✅ completo |
| D · economia e ecossistema | ✅ completo |
| E · fontes | ✅ completo |
| Glossário | ✅ completo |

**Base de testes.** Tudo que aparece como saída de comando neste curso foi **executado** em
13/08/2026, em Ubuntu 22.04.5 LTS com **Git 2.34.1, GnuPG 2.2.27 e OpenSSH 8.9p1** — inclusive
as falhas propositais. Onde o comportamento depende de versão mais nova (a sintaxe `key::`,
`gpg.ssh.revocationFile`), isso está anotado no ponto em que aparece.

**Não executado, e declarado onde aparece:** instalação em macOS e Windows; YubiKey e cartão
OpenPGP; o selo `Verified` na tela do GitHub; os exemplos 11 e 12 do
[06-exemplos.md](06-exemplos.md); o workflow de CI.

**Pesquisado na web em 13/08/2026:** versões (Git 2.55.0, GnuPG 2.5.21, OpenSSH 10.5,
Gpg4win 5.1.0, `gh` 2.97.0), preços, cursos em PT/EN/FR, edições de livros, prazos do
Cyber Resilience Act.

**Quando reavaliar:** [65-estado-da-arte.md](65-estado-da-arte.md) e
[80-custos-e-licencas.md](80-custos-e-licencas.md) a cada 6 meses;
[85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) a cada ano;
[03-instalacao.md](03-instalacao.md) sempre que uma das ferramentas mudar de série.
