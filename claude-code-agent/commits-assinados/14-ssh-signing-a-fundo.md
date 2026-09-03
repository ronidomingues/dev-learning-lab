# 14 · Assinatura por SSH a fundo

> Nível: intermediário → avançado · Atualizado em 13/08/2026 · Testado com OpenSSH 8.9p1
> **A estrutura binária mostrada abaixo foi decodificada de um commit real deste laboratório.**

O que existe por baixo do `gpg.format ssh`: o formato SSHSIG, os namespaces, o
`allowed_signers` por dentro, revogação, certificados SSH e os limites honestos do modelo.

---

## 1. SSHSIG: o formato

Antes de 2019, uma chave SSH só servia para o protocolo SSH — autenticar sessão. O
**SSHSIG**, introduzido no OpenSSH 8.1 (outubro de 2019), transformou-a numa ferramenta de
assinatura genérica: assine qualquer coisa, verifique contra uma lista de chaves permitidas.

A especificação vive em `PROTOCOL.sshsig`, no código-fonte do OpenSSH. Estrutura do blob:

```
byte[6]   MAGIC = "SSHSIG"
uint32    version = 1
string    publickey          (a chave pública que assinou, embutida)
string    namespace          ("git", no nosso caso)
string    reserved           (vazio, hoje)
string    hash_algorithm     ("sha512")
string    signature          (a assinatura propriamente dita)
```

Decodificação de um commit real deste curso:

```
total: 173 bytes
magic: b'SSHSIG'
version: 1
publickey: 51 bytes -> b'\x00\x00\x00\x0bssh-ed25519\x00\x00\x00 \xa6'...
namespace: b'git'
reserved: b''
hash_algorithm: b'sha512'
signature: 83 bytes
consumido: 173 de 173
```

Três observações que valem ouro na hora de depurar:

1. **A chave pública viaja dentro da assinatura.** Você não precisa saber de antemão quem
   assinou para conseguir *ler* a assinatura — só para decidir se aceita. É por isso que o
   Git consegue dizer `[U]` ("boa, dono desconhecido") em vez de simplesmente falhar.
2. **O hash é SHA-512**, fixo, e é sobre a mensagem — independente do SHA-1 que o Git usa
   para nomear objetos. Os dois problemas são separados.
3. **173 bytes** para tudo. Assinar não engorda o repositório de forma perceptível.

### O que é realmente assinado

Não é a mensagem crua. O OpenSSH assina uma estrutura que **inclui o namespace**:

```
MAGIC || namespace || reserved || hash_algorithm || sha512(mensagem)
```

Isso é o que impede a **confusão de domínio**: uma assinatura feita para o namespace `file`
não pode ser reapresentada como se fosse do namespace `git`, porque o namespace faz parte do
que foi assinado. Não é uma verificação por cima — é criptográfico.

Demonstração real, tentando verificar com o namespace errado:

```
/tmp/allowed_signers:1: key is not permitted for use in signature namespace "file"
Could not verify signature.
```

---

## 2. `allowed_signers` por dentro

```
<principal> [opções,] <tipo> <chave-base64> [comentário]
```

| Opção | Efeito |
|---|---|
| `namespaces="git"` | limita a chave a esse namespace (aceita lista: `"git,file"`) |
| `valid-after="AAAAMMDD[HHMM[SS]]"` | válida a partir de |
| `valid-before="AAAAMMDD[HHMM[SS]]"` | válida até |
| `cert-authority` | é uma autoridade que emite certificados para outras chaves |

### Como o Git usa esse arquivo — e onde está o buraco

O Git **não** procura pelo e-mail do commit. Ele faz o contrário:

```
1. extrai a chave pública de dentro da assinatura
2. ssh-keygen -Y find-principals: "que principal do arquivo tem ESTA chave?"
3. achou → verifica com aquele principal → G, e exibe o principal em %GS
   não achou → U
```

Consequência, demonstrada no ato 9 do [projeto-modelo](07-projeto-modelo/):

```
ff2ebb4  [G]  autor=Ana Souza <ana@exemplo.dev>  assinante=roberto@outraempresa.com
```

O commit é da Ana. O `allowed_signers` diz que aquela chave é do Roberto. O Git responde
`[G]`. **Ele não compara `%GS` com o autor do commit.**

Isso não é bug — é o escopo do mecanismo. A verificação local responde
*"esta chave está na minha lista de chaves aceitas?"*. A pergunta
*"o autor é quem diz ser?"* precisa de algo que ligue chaves a identidades, e isso o
`allowed_signers` não faz: ele apenas registra o rótulo que **você** deu a cada chave.

**Como fechar esse buraco, se você precisa:** compare os campos você mesmo.

```bash
# reprova commits cujo assinante não seja o próprio autor
git log --format='%H|%ae|%GS|%G?' | while IFS='|' read -r h ae gs st; do
  if [ "$st" = "G" ] && [ "$ae" != "$gs" ]; then
    echo "DIVERGE $h — autor=$ae assinante=$gs"
  fi
done
```

Vale para equipes que usam e-mail corporativo como principal. Não vale se as pessoas commitam
com `@users.noreply.github.com` e o principal é outro — nesse caso, monte um mapa explícito.

### Comportamentos medidos

| Situação | `%G?` | Mensagem |
|---|---|---|
| chave presente | `G` | `Good "git" signature for ana@exemplo.dev with ED25519 key SHA256:...` |
| chave ausente | `U` | `No principal matched.` |
| arquivo não configurado | `U` | `Unable to open allowed keys file "": No such file or directory` |
| `valid-before` no passado | `U` | `key has expired: verify time 2026-08-13T12:28:08 > valid-before 2025-01-01T00:00:00` |
| `valid-after` no futuro | `U` | `key is not yet valid: verify time ... < valid-after ...` |
| namespace errado | falha | `key is not permitted for use in signature namespace "file"` |

> **Limitação real e pouco documentada:** as opções de validade são comparadas com a **hora
> da verificação**, não com a data do commit. Ou seja, `valid-before="20260301"` não diz
> "aceite o que foi assinado antes de março"; diz "a partir de março, pare de aceitar esta
> chave". Para o caso de uso normal — aposentar uma chave — funciona bem, porque as
> verificações posteriores é que importam. Para auditoria histórica retroativa, não serve.

### Onde colocar o arquivo

| Local | Quando |
|---|---|
| `~/.config/git/allowed_signers` | pessoal, vale para todos os seus repositórios |
| `.github/allowed_signers` **no repositório** | equipe: qualquer um clona e já verifica |
| gerado por script a partir da API do GitHub | equipes que mudam muito ([06 § 7](06-exemplos.md)) |

O trade-off de versionar está em [18-politica-de-equipe.md](18-politica-de-equipe.md), e é
resumível assim: quem tem escrita no repositório pode se acrescentar ao arquivo. Portanto o
arquivo versionado é **conveniência de verificação**, não controle de acesso.

---

## 3. Revogação

O SSH não tem certificado de revogação como o OpenPGP. Tem **KRL** (*Key Revocation List*):

```bash
ssh-keygen -k -f revogadas.krl chave-comprometida.pub
git config --global gpg.ssh.revocationFile ~/.config/git/revogadas.krl
```

> `gpg.ssh.revocationFile` exige **Git ≥ 2.35** — não existe no 2.34.1 usado nos testes deste
> curso.

Verificar se uma chave está na lista:

```bash
ssh-keygen -Q -f revogadas.krl chave.pub
# imprime "REVOKED" se estiver
```

**Opinião franca:** KRL é pouco usada na prática, e na maioria dos casos você resolve melhor
com `valid-before` no `allowed_signers` — que tem o efeito desejado e não exige um arquivo
binário a mais para distribuir. KRL faz sentido quando você já tem infraestrutura de
certificados SSH (abaixo) e precisa revogar antes do vencimento natural.

E o que realmente importa quando uma chave vaza: **removê-la do GitHub**
(<https://github.com/settings/keys>). Enquanto ela estiver cadastrada lá, commits assinados
com ela continuam saindo `Verified`, independentemente do que diga o seu KRL local.

---

## 4. Certificados SSH — a saída para equipes grandes

Manter um `allowed_signers` com 500 linhas, atualizado a cada contratação e demissão, não
funciona. A solução é a mesma que o TLS usa: uma **autoridade certificadora**.

```bash
# 1. a organização cria a CA (uma vez, e guarda a privada com muito cuidado)
ssh-keygen -t ed25519 -f ca_assinatura -C "CA de assinatura da Empresa"

# 2. cada pessoa recebe um certificado de curta duração para a chave dela
ssh-keygen -s ca_assinatura -I "ana@empresa.com" -n "ana@empresa.com" \
           -V +52w -z 1001 ana.pub
#   -I identidade  -n principal  -V validade  -z número de série
#   gera ana-cert.pub

# 3. o allowed_signers da organização tem UMA linha, e não muda
#    *@empresa.com cert-authority,namespaces="git" ssh-ed25519 AAAA...CA

# 4. quem assina usa o certificado
git config user.signingkey ~/.ssh/ana-cert.pub
```

Ganhos: entrada e saída de pessoas não mexem no arquivo distribuído; a validade é curta e
renovada automaticamente; revogação é por número de série via KRL.

Custos, e são reais: você precisa operar a CA (chave offline, processo de emissão,
automação de renovação), e um comprometimento da CA compromete tudo. Só vale a partir de umas
poucas dezenas de pessoas — abaixo disso, o `allowed_signers` gerado por script é mais barato.

> Uma nota de realidade: **o GitHub não usa esse mecanismo** para decidir o selo. Ele olha as
> chaves cadastradas nas contas. Certificado SSH resolve a *sua* verificação local e a da sua
> CI; não muda o que aparece no site.

---

## 5. Chaves em hardware: `sk-ssh-ed25519`

```bash
ssh-keygen -t ed25519-sk -O resident -O verify-required -f ~/.ssh/id_yubikey
```

| Opção | Efeito |
|---|---|
| `-t ed25519-sk` | a chave privada nasce **dentro** do token e nunca sai |
| `-O resident` | fica guardada no token; recuperável com `ssh-keygen -K` |
| `-O verify-required` | exige PIN, além do toque físico |
| *(padrão)* | exige toque físico a cada assinatura |

O arquivo `~/.ssh/id_yubikey` que fica no disco **não é a chave privada** — é um
identificador que aponta para a chave dentro do token (*key handle*). Copiá-lo para outra
máquina não dá acesso a nada sem o token na mão.

Exige OpenSSH ≥ 8.2 e, no Linux, `libfido2` instalada.

O que isso protege, concretamente: malware que lê `~/.ssh/` não consegue assinar no seu nome,
porque a operação exige presença física. É o vetor que mais cresceu em ataques à cadeia de
suprimentos. O que não protege: um malware ativo enquanto você está trabalhando ainda pode
pedir uma assinatura no momento em que você toca o token para outra coisa.

---

## 6. SSH × GPG: a comparação estrutural

| Dimensão | SSH | GPG |
|---|---|---|
| unidade | uma chave, plana | árvore: primária + subchaves |
| identidade | um rótulo (*principal*) no seu arquivo | UIDs assinados dentro da chave |
| expiração | externa, no `allowed_signers` | interna, assinada pela primária |
| revogação | KRL, externa e pouco usada | certificado de revogação, padronizado |
| rotação sem trocar identidade | **impossível** | possível, via subchaves |
| distribuição | GitHub, ou seu arquivo | GitHub, WKD, keyservers |
| separação de papéis | uma chave por finalidade, por convenção | `[S]`, `[E]`, `[A]` explícitos |
| tamanho da assinatura | ~173 bytes | ~180 a 600 bytes |
| complexidade operacional | baixa | alta |

**A diferença que mais importa** está na terceira linha de baixo: no OpenPGP, sua *identidade*
(a chave primária) sobrevive à troca do *material criptográfico* (as subchaves). No SSH, chave
comprometida é identidade nova, e todo mundo que confiava nela precisa atualizar sua lista.

Para a maior parte das pessoas isso é irrelevante, porque a "lista" é a conta do GitHub e
atualizá-la leva 30 segundos. Para um projeto com milhares de verificadores independentes —
uma distribuição Linux, por exemplo — é decisivo. É por isso que Debian e Fedora continuam
em OpenPGP, e não é teimosia.

---

## Autoteste

1. O que a estrutura SSHSIG carrega além da assinatura, e por que a chave pública vai dentro?
2. Como o namespace impede confusão de domínio? Por que uma checagem por cima não bastaria?
3. Descreva o algoritmo que o Git usa para achar o principal de uma assinatura SSH.
4. Por que `%GS` pode mostrar o nome de alguém que não é o autor do commit?
5. Como reprovar, num script, commits em que assinante ≠ autor?
6. `valid-before` é comparado com qual data? Que limitação isso impõe?
7. Quando um certificado SSH compensa em relação a um `allowed_signers` gerado por script?
8. Por que projetos como Debian continuam em OpenPGP?

*(Respostas: 1 — magic, versão, chave pública, namespace, reserved, algoritmo de hash; a chave
pública vai dentro para que qualquer um consiga ler a assinatura antes de decidir se aceita.
2 — o namespace faz parte do que é assinado, então a assinatura é criptograficamente inválida
em outro namespace. 3 — extrai a chave da assinatura e pergunta ao `allowed_signers` que
principal tem aquela chave. 4 — porque o Git busca por chave, não por e-mail, e exibe o rótulo
que o seu arquivo dá àquela chave. 5 — comparando `%ae` com `%GS` num laço sobre `git log`.
6 — com a hora da verificação; não serve para auditoria histórica retroativa. 7 — a partir de
algumas dezenas de pessoas, quando manter o arquivo distribuído passa a custar mais que operar
a CA. 8 — porque subchaves permitem trocar material criptográfico sem trocar a identidade, e
eles têm milhares de verificadores independentes.)*

---

**Próximo:** [15-verificacao-no-github.md](15-verificacao-no-github.md).
