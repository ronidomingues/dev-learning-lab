# 80 · Custos e licenças

> Nível: todos · **Preços consultados na web em 13/08/2026** · Câmbio usado:
> **US$ 1 ≈ R$ 5,17** (faixa observada no dia: R$ 5,16–5,19). Preço sem data é
> desinformação; se você está lendo isto meses depois, reconfira.

---

## Primeira linha: assinar commits é gratuito

Todo o caminho principal deste curso custa **zero**: Git, OpenSSH, GnuPG, conta no GitHub,
cadastro de chaves, o selo `Verified` e o ruleset em repositório público. Não há camada
gratuita com pegadinha, não pedem cartão de crédito, e não há limite de commits assinados.

**Quem paga a conta, então?**

| Peça | Quem sustenta | Modelo |
|---|---|---|
| **Git** | Software Freedom Conservancy, com contribuições de GitHub, GitLab, Google, Microsoft | trabalho corporativo doado, porque todos dependem dele |
| **OpenSSH** | projeto OpenBSD, com doações e patrocínio corporativo | infraestrutura crítica mantida por poucas pessoas |
| **GnuPG** | g10 Code (empresa de Werner Koch), doações, governo alemão | quase quebrou em 2015; ver [11-historia.md](11-historia.md) |
| **GitHub** | Microsoft | o gratuito atrai; a receita vem de Team, Enterprise, Actions, Copilot |
| **Sigstore** | Linux Foundation, com Google, Red Hat, Chainguard, GitHub | bem público financiado por quem lucra com o ecossistema |

O incentivo do GitHub em manter isso gratuito é direto: quanto mais gente com identidade
forte na plataforma, mais valiosa a plataforma. Não há sinal de que isso mude — mas é útil
notar que o **modelo de confiança** deste assunto ([10 § 4](10-fundamentos.md)) depende de uma
empresa cuja política pode mudar.

---

## 1. Licenças

| Software | Licença | O que permite | Restrições comerciais |
|---|---|---|---|
| **Git** | GPL-2.0 | usar, modificar, distribuir | modificações distribuídas devem ser GPL; **usar não contamina nada** |
| **OpenSSH** | BSD (várias, todas permissivas) | praticamente tudo | manter o aviso de copyright |
| **GnuPG** | GPL-3.0 | usar, modificar, distribuir | GPL-3 tem cláusulas de patente e anti-*tivoization*; **usar continua livre** |
| **libgcrypt** | LGPL-2.1+ | vincular a software proprietário | — |
| **Gpg4win** | GPL | idem | — |
| **GitHub CLI** | MIT | tudo | nenhuma |
| **Sigstore / cosign / gitsign** | Apache-2.0 | tudo, com concessão de patente | — |

**O mal-entendido corporativo mais comum:** "GnuPG é GPL-3, não podemos usar na empresa". A
GPL trata da **distribuição** de obras derivadas. Rodar `gpg` para assinar seus commits não
torna o seu código GPL, do mesmo modo que compilar com o GCC não torna o binário GPL. Só há
questão se você **embutir e redistribuir** o GnuPG dentro do seu produto — e mesmo aí existe
a `libgcrypt` sob LGPL.

**Nenhum item deste curso exige licença comercial.**

---

## 2. Serviços — o que é grátis e onde acaba

| Serviço | Grátis | Onde acaba | Preço acima disso (13/08/2026) |
|---|---|---|---|
| Conta GitHub | ilimitada | — | — |
| Repositórios privados | ilimitados | — | — |
| Cadastro de chaves (SSH/GPG) | ilimitado | — | — |
| Selo `Verified` | sempre | — | — |
| **Ruleset exigindo assinatura** | **repositório público** | repositório **privado** exige plano pago | **Team: US$ 4/usuário/mês** (~R$ 21) |
| GitHub Actions (CI de verificação) | 2.000 min/mês em conta Free | — | por minuto, acima |
| Codespaces | 120 horas-núcleo e 15 GB-mês | — | por uso |
| Enterprise | — | — | a partir de **US$ 21/usuário/mês** (~R$ 109) |

> A linha que importa para a maioria: **se o seu repositório é privado e você quer *exigir*
> assinatura, precisa do plano Team.** Assinar continua grátis; o que custa é a trava
> automática. A alternativa gratuita é fazer a verificação na CI — o que é uma trava mais
> fraca (roda depois do push), mas custa zero. O workflow está em
> [`07-projeto-modelo/ci/`](07-projeto-modelo/ci/verificar-assinaturas.yml).

---

## 3. Hardware — opcional

Preços de tabela do fabricante, 13/08/2026. Some **imposto de importação e frete** ao comprar
do Brasil: na prática, o valor final costuma ficar entre 1,8× e 2,2× o preço em dólar.

| Item | Preço | ~BRL | Serve para |
|---|---|---|---|
| **YubiKey 5 NFC** (USB-A) | US$ 58 | ~R$ 300 | FIDO2 (`ed25519-sk`) **e** cartão OpenPGP |
| **YubiKey 5C NFC** (USB-C) | ~US$ 58–65 | ~R$ 300–336 | idem |
| YubiKey 5 FIPS | mais caro | — | só se houver exigência regulatória |
| Nitrokey 3A NFC | ~€ 60 | ~R$ 360 | alternativa europeia, código aberto |
| **Cartão OpenPGP** simples + leitora | ~US$ 30–60 | ~R$ 155–310 | só GPG |

**Custo real de adoção com hardware**, e é aqui que o orçamento estoura:

```
2 tokens por pessoa (o segundo é backup)      2 × R$ 300  = R$ 600
importação e frete (estimativa)                            + R$ 400
tempo de configuração e suporte (~2 h)                     + o seu custo/hora
────────────────────────────────────────────────────────────────────
por pessoa, ordem de grandeza                             ~R$ 1.000 + tempo
```

Para 30 pessoas, algo em torno de **R$ 30 mil**, além do suporte contínuo (token perdido,
token esquecido em casa, PIN bloqueado). **Minha opinião:** vale para quem publica software
que terceiros instalam e para pessoas com acesso privilegiado a produção; é exagero para uma
equipe inteira de aplicação interna.

---

## 4. Software pago, opcional

| Ferramenta | Preço (13/08/2026) | ~BRL/mês | Vale? |
|---|---|---|---|
| **1Password Individual** | US$ 3,99/mês no anual (US$ 47,88/ano); US$ 4,99 no mensal | ~R$ 21 | se você **já usa** para senhas, o agente SSH vem junto e é ótimo |
| 1Password Teams/Business | mais caro, por usuário | — | idem, em escala |
| **Secretive** (macOS) | **grátis**, código aberto | — | chave no Secure Enclave; a melhor relação custo-benefício do macOS |
| Keeper | por usuário | — | menos maduro para este uso |

> O 1Password aumentou o plano Individual em 27/03/2026, de US$ 35,88 para US$ 47,88 ao ano.
> Comprar 1Password **só** para assinar commits não se justifica: o `ssh-agent` do sistema
> faz o trabalho de graça.

---

## 5. Custos ocultos — os que ninguém orça

| Custo | Ordem de grandeza | Por que ninguém prevê |
|---|---|---|
| **Tempo de configuração** | 10 min (SSH) a 1 h (GPG) por pessoa | parece trivial, e é, até a décima pessoa |
| **Suporte contínuo** | ~1 h/pessoa/ano | chave vencida, máquina nova, "parou de funcionar" |
| **Implantação em equipe** | ~10 h de trabalho, 6 semanas de calendário | o gargalo é social ([18](18-politica-de-equipe.md)) |
| **Bots e automação quebrados** | 2 a 8 h por pipeline | descoberto **depois** de ligar a trava |
| **Aprisionamento leve no GitHub** | difícil de medir | os selos e a verificação de identidade são dele; migrar de plataforma leva junto o modelo de confiança (as assinaturas em si viajam com o repositório) |
| **Plano Team só para o ruleset** | US$ 4/usuário/mês | quem tem repositório privado descobre no fim |
| **Chave perdida** | horas + risco | sem backup nem certificado de revogação |
| **Retreinamento** | recorrente | rotatividade da equipe |

Para uma equipe de 20 pessoas, uma estimativa honesta do **primeiro ano**:

```
configuração inicial     20 × 0,5 h  =  10 h
implantação e política                 10 h
correção de bots                        8 h
suporte no primeiro ano  20 × 1 h   =  20 h
──────────────────────────────────────────
                                      ~48 h
+ plano Team (se privado)  20 × US$ 4 × 12 = US$ 960/ano (~R$ 4.960)
```

Ou seja: **o custo real é tempo, não licença.** E cai muito nos anos seguintes.

---

## 6. Alternativas gratuitas, e o que se perde

| Em vez de | Use | O que se perde |
|---|---|---|
| YubiKey | `ssh-agent` com `-t 8h` | a chave continua em disco: malware que leia `~/.ssh` consegue copiá-la |
| YubiKey (macOS) | **Secretive** | nada relevante, se você só usa macOS |
| 1Password | `ssh-agent` do sistema | sincronização entre máquinas e desbloqueio por biometria |
| Ruleset em repo privado | verificação na CI | a trava passa a ser posterior ao push, e contornável por quem edita o workflow |
| GitHub | GitLab / Gitea / Forgejo | nada de essencial: os três verificam assinatura; muda o modelo de identidade |
| GnuPG | assinatura por SSH | subchaves, expiração nativa e revogação formal |

---

## 7. O argumento de custo para a liderança

- **Licença:** R$ 0.
- **Hardware:** opcional; só para quem tem acesso privilegiado.
- **Tempo:** ~48 h no primeiro ano para 20 pessoas; ~15 h/ano depois.
- **Único custo recorrente possível:** plano Team (US$ 4/usuário/mês) se o repositório for
  privado **e** você quiser a trava automática.
- **Contrapartida:** fecha o vetor de escrita forjada com credencial roubada, dá atribuição em
  incidente, e é a base do que exigências de proveniência (CRA, EO 14028) vão cobrar.
- **O que não comprar junto:** a ideia de que isso substitui revisão de código.

---

## Autoteste

1. Assinar commits custa alguma coisa? Onde aparece o primeiro custo real em dinheiro?
2. Por que "GnuPG é GPL-3, não podemos usar" é um mal-entendido?
3. Qual é o maior custo oculto de uma implantação em equipe?
4. Você tem repositório **privado** e quer exigir assinatura sem pagar. Qual a alternativa, e
   o que se perde?
5. Vale comprar YubiKey para toda a equipe? Justifique.
6. Quem paga a conta do GitHub manter isso gratuito, e qual é o incentivo?
7. Por que comprar dois tokens em vez de um?

*(Respostas: 1 — não; o primeiro custo em dinheiro é o plano Team, necessário para ruleset em
repositório privado. 2 — a GPL trata da distribuição de obras derivadas; usar `gpg` não
contamina o seu código. 3 — tempo: implantação, suporte e conserto de bots. 4 — verificação na
CI; perde-se a trava no momento do push, e ela passa a ser contornável por quem edita o
workflow. 5 — em geral não: vale para quem publica software que terceiros instalam e para
acessos privilegiados; o custo por pessoa gira em torno de R$ 1.000 mais suporte. 6 — a
Microsoft, via GitHub; o incentivo é identidade forte na plataforma, que a torna mais valiosa.
7 — token único é ponto único de falha, e perdê-lo significa perder a identidade.)*

---

**Fontes consultadas em 13/08/2026:** yubico.com/store (YubiKey 5 NFC, US$ 58) ·
1password.com e cobertura do reajuste de 27/03/2026 (Individual US$ 47,88/ano) ·
github.com/pricing (Free / Team US$ 4 / Enterprise a partir de US$ 21 por usuário/mês) ·
docs.github.com (rulesets em repositório público no Free; camada gratuita de Codespaces) ·
cotação USD/BRL de 13/08/2026 (Wise, Investing.com, TradingView).
Preços de hardware **não** incluem impostos e frete para o Brasil.

**Próximo:** [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md).
