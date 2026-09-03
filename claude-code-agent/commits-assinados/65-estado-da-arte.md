# 65 · Estado da arte — agosto de 2026

> Nível: avançado · **Fotografia de 13/08/2026** · Este arquivo envelhece rápido; reavalie a
> cada 6 meses

O que está em uso, o que mudou nos últimos anos, o que está em disputa e para onde a coisa
parece caminhar. Tudo com data, e com a separação explícita entre **fato**, **consenso** e
**minha leitura**.

---

## 1. Onde estamos, em números e versões

| Peça | Versão atual | Data | Nota |
|---|---|---|---|
| Git | **2.55.0** | 11/08/2026 | rumo ao Git 3.0, previsto para o fim de 2026 |
| OpenSSH | **10.5** | 11/08/2026 | 10.4 trouxe ML-DSA 44 + Ed25519 experimental |
| GnuPG | **2.5.21** | 02/07/2026 | série 2.5 é a estável; **2.4 fora de suporte desde 30/06/2026** |
| Gpg4win | **5.1.0** | 29/07/2026 | traz GnuPG 2.5.16; só 64 bits |
| GitHub CLI | **2.97.0** | 31/07/2026 | — |
| gitsign (Sigstore) | **0.16.0** | 06/05/2026 | continua sem `Verified` no GitHub |

**Fato:** assinatura por SSH é hoje o caminho padrão para quem começa. Ela existe no Git desde
novembro de 2021 e no GitHub desde 23/08/2022, e em quatro anos deslocou o GPG do papel de
recomendação padrão em praticamente toda documentação nova.

**Consenso:** a barreira nunca foi criptográfica, era de ergonomia. Remover peças (agente,
pinentry, servidor de chaves, subchaves, validade) foi o que mudou a adoção.

---

## 2. O que mudou desde 2022

| Mudança | Quando | Efeito |
|---|---|---|
| GitHub verifica assinatura SSH | 08/2022 | derruba a barreira de entrada |
| Sigstore/`gitsign` amadurece | 2022–2026 | assinatura sem chave vira viável tecnicamente, e continua bloqueada no selo do GitHub |
| Rulesets substituem branch protection | 2023 | exigência de assinatura passa a ter escopo de organização e modo `evaluate` |
| Artifact Attestations do GitHub em GA | 06/2024 | proveniência SLSA de build, assinada, para artefatos |
| RFC 9580 (OpenPGP renovado) | 07/2024 | primeira atualização real do padrão em 17 anos |
| xz-utils | 03/2024 | recalibra a expectativa sobre o que assinatura resolve |
| npm com proveniência via Sigstore, e 2FA obrigatório em pacotes de alto impacto | 2025–2026 | o Sigstore vence no ecossistema de pacotes enquanto perde no selo de commit |
| GnuPG 2.4 sai de suporte | 30/06/2026 | boa parte dos tutoriais na internet passa a instalar versão sem suporte |
| ML-DSA experimental no OpenSSH | 07/2026 | começa a transição pós-quântica em assinatura |

---

## 3. Os três debates abertos

### Debate 1 — chave de longa duração × identidade efêmera

**A tese do Sigstore:** chave de longa duração é responsabilidade que ninguém quer. Substitua
por identidade OIDC + certificado de 10 minutos + log de transparência. Nada persistente para
vazar, nada para rotacionar, nada para revogar.

**A objeção:** você troca "confio na chave da Ana" por "confio no provedor de identidade da
Ana, no Fulcio e no Rekor". São três dependências novas, todas online, todas operadas por
terceiros. E o modelo de segurança passa a depender de gossip entre verificadores, que é a
parte não resolvida ([60 § 5](60-teoria-avancada.md)).

**Onde está a disputa em 13/08/2026:** o Sigstore **venceu** em proveniência de artefatos
(npm, PyPI, containers, GitHub Artifact Attestations) e **não entrou** em assinatura de commit,
porque o GitHub não incluiu a raiz do Sigstore no conjunto de confiança dele. Quatro anos
assim.

**Minha leitura:** essa divisão não é acidental. Proveniência de build é sobre *máquinas*, e
identidade efêmera de máquina é natural. Assinatura de commit é sobre *pessoas*, e pessoas
têm continuidade — a chave de longa duração modela essa continuidade de forma direta. Suspeito
que a divisão persista, e que a pergunta certa não seja "qual vence", e sim "as duas camadas
são complementares?". Acho que são.

### Debate 2 — assinatura resolve segurança de cadeia de suprimentos?

**A favor:** fecha o vetor de escrita forjada, dá atribuição em incidente, é pré-requisito de
qualquer esquema de proveniência, e é exigido por regulação que está chegando.

**Contra:** o xz-utils tinha tudo assinado. Malware que rouba chave assina. Colaborador
mal-intencionado assina. O que impede código malicioso é revisão, análise e diversidade de
mantenedores — nada disso é criptografia.

**Consenso emergente**, e eu concordo: assinatura é **necessária e insuficiente**. Ela é a
camada de *atribuição* de um edifício que precisa também de proveniência de build (SLSA),
revisão, análise estática e gestão de dependências. Apresentá-la como solução é o que produz
teatro de segurança.

### Debate 3 — o SHA-1 do Git

**Fato:** o Git ainda usa SHA-1 por padrão. SHA-256 existe desde 2020, e o GitHub não o
suporta.

**A defesa:** a detecção de colisão mitiga o ataque conhecido; forjar um commit colidente que
seja código plausível é muito mais difícil do que os exemplos de PDF; e o custo do ataque é
alto frente a alternativas mais baratas.

**A crítica:** "mitigado" não é "resolvido", o custo cai todo ano, e a migração só fica mais
cara quanto mais se espera.

**Minha leitura:** isto vai ficar como está até que alguém com poder de coordenação (o
GitHub, na prática) decida pagar a conta da interoperabilidade. Não é um problema técnico em
aberto; é um problema de incentivo. E é o exemplo mais didático que conheço de que segurança
não avança por mérito.

---

## 4. Regulação — o que efetivamente chega em 2026 e 2027

**Fato**, e é o que mais deve mudar a prioridade das empresas europeias e de quem vende para
elas — o **Cyber Resilience Act**:

| Data | O que passa a valer |
|---|---|
| 10/12/2024 | entrada em vigor |
| 11/06/2026 | regras para organismos de avaliação de conformidade |
| **11/09/2026** | **obrigação de reportar vulnerabilidade em exploração ativa à ENISA em 24 h**, relatório em 72 h, final em 14 dias |
| 11/12/2027 | conformidade plena: produto com elementos digitais só entra no mercado europeu com marcação CE |

Sanções previstas: até € 15 milhões ou 2,5 % do faturamento mundial anual, o que for maior.

Nos EUA, a ordem executiva 14028 (2021) já havia estabelecido SBOM e proveniência como
requisito para fornecedores federais.

**A leitura prática:** nada disso exige, com essas palavras, "assine seus commits". Exigem
**proveniência e rastreabilidade** — e assinatura é a forma mais barata de começar a produzir
as duas. Quem tratar isso como caixa a marcar em 2027 vai pagar mais caro do que quem
implantou em 2026.

---

## 5. O que está estável e não vai mudar tão cedo

Útil saber onde é seguro investir tempo:

- **Ed25519** como algoritmo padrão. Nada no horizonte clássico o ameaça.
- **SSHSIG** como formato de assinatura SSH. Estável desde 2019, sem sinal de sucessor.
- **O modelo do GitHub** (chave cadastrada + e-mail verificado). Sem indício de mudança.
- **`gpg.format ssh`** no Git. Consolidado.
- **A distinção entre DCO (`-s`) e assinatura (`-S`)**. Vai continuar confundindo gente.

---

## 6. Para onde parece ir — previsões, marcadas como tal

> **Isto é opinião, não fato.** Estou registrando para poder ser cobrado depois.

1. **A assinatura por SSH continua ganhando espaço**, e o GPG se retrai para nichos onde
   subchave e revogação formal importam de verdade: distribuições Linux, projetos com muitos
   verificadores independentes, setores regulados. *Confiança: alta.*
2. **O `gitsign` não vai virar padrão de assinatura de commit** enquanto o GitHub não mudar o
   conjunto de confiança dele, e não vejo incentivo para isso. *Confiança: média-alta.*
3. **Proveniência de build (SLSA, attestations) passa a importar mais que assinatura de
   commit** na conversa sobre cadeia de suprimentos, porque responde à pergunta que
   assinatura não responde: *este binário veio deste código?* *Confiança: alta.*
4. **A migração pós-quântica de assinatura será híbrida e lenta**, começando por ambientes
   regulados, e o tamanho das assinaturas será um atrito real em repositórios grandes.
   *Confiança: média.*
5. **O SHA-1 do Git continua onde está** por mais alguns anos. *Confiança: média-alta.*
6. **Vai aparecer pressão por "assinatura de intenção"** — distinguir criptograficamente
   "revisei e aprovei" de "minha ferramenta assinou automaticamente". Hoje são
   indistinguíveis, e isso é a raiz do teatro de segurança do assunto. Não sei de nada
   concreto nessa direção. *Confiança: baixa.*

---

## 7. O que reavaliar, e quando

| Item | Frequência | O que checar |
|---|---|---|
| versões (§ 1) | 6 meses | Git, GnuPG, OpenSSH, Gpg4win |
| `gitsign` no GitHub | 6 meses | mudou o `unknown_signature_type`? |
| pós-quântico | 6 meses | ML-DSA saiu de experimental no OpenSSH? |
| SHA-256 no Git | 12 meses | o GitHub passou a hospedar? |
| CRA e regulação | 6 meses | as datas de 09/2026 e 12/2027 se confirmaram? |
| preços ([80](80-custos-e-licencas.md)) | 6 meses | — |
| cursos ([85](85-cursos-e-certificacoes.md)) | 12 meses | links quebrados |

---

## Autoteste

1. Por que a assinatura por SSH deslocou o GPG, se a criptografia é equivalente?
2. Onde o Sigstore venceu, e onde não entrou? Por quê?
3. Qual é o consenso emergente sobre assinatura e segurança de cadeia de suprimentos?
4. Por que o SHA-1 do Git continua onde está?
5. Que data de 2026 muda obrigações concretas na Europa, e qual é a obrigação?
6. Cite três coisas estáveis, em que é seguro investir tempo.
7. Qual pergunta a proveniência de build responde e a assinatura de commit não?

*(Respostas: 1 — a barreira era de ergonomia, não criptográfica; SSH removeu peças. 2 — venceu
em proveniência de artefatos (npm, PyPI, containers, attestations) e não entrou em assinatura
de commit, porque o GitHub não confia na raiz do Sigstore. 3 — é necessária e insuficiente:
resolve atribuição, não malícia nem qualidade. 4 — falta de incentivo para pagar a
interoperabilidade; é problema econômico, não técnico. 5 — 11/09/2026: reportar vulnerabilidade
em exploração ativa à ENISA em 24 h. 6 — Ed25519, SSHSIG, o modelo do GitHub, `gpg.format ssh`.
7 — "este binário veio deste código?".)*

---

**Fontes consultadas em 13/08/2026:** git-scm.com · openssh.com/releasenotes.html ·
gnupg.org/news.html · gpg4win.org · github.com/sigstore/gitsign/releases ·
docs.github.com (rulesets, artifact attestations, commit signature verification) ·
digital-strategy.ec.europa.eu (Cyber Resilience Act) · eprint.iacr.org/2020/014.

**Próximo:** [70-pratica.md](70-pratica.md).
