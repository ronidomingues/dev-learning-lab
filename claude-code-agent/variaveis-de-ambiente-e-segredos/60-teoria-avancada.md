# 60 · Teoria avançada — o que sustenta tudo isso por baixo

`Nível: pesquisa` · `Atualizado em: 14/08/2026`

Este arquivo reintroduz do zero a criptografia necessária e vai até a fronteira:
criptografia de envelope, o problema do segredo zero, identidade de carga de
trabalho, atestação remota e os limites teóricos do que é possível.

---

## 1. O mínimo de criptografia, do zero

### Simétrica

Uma chave, usada para cifrar e decifrar.

```
texto claro + chave ──[AES-256-GCM]──► texto cifrado + tag de autenticação
```

**AES-256-GCM** é o padrão atual. O `GCM` importa: é um modo **autenticado**
(*AEAD* — Authenticated Encryption with Associated Data), que garante duas coisas ao
mesmo tempo — **confidencialidade** (ninguém lê) e **integridade** (ninguém altera
sem que se perceba).

Modos antigos como CBC dão só confidencialidade. Sem autenticação, um atacante pode
modificar o texto cifrado e provocar comportamento previsível — a família dos ataques
de *padding oracle*. Se você vir CBC sem HMAC num sistema em 2026, é dívida técnica
com juros.

⚠️ **A regra que quebra sistemas em GCM:** o **nonce nunca pode repetir** com a mesma
chave. Repetir nonce em GCM não vaza "um pouco" — permite recuperar a chave de
autenticação e forjar mensagens. Por isso as bibliotecas sérias geram o nonce
internamente e não deixam você escolher.

### Assimétrica

Um par: **pública** (distribuível) e **privada** (segredo).

```
cifrar com a PÚBLICA   ──► só a privada decifra   (confidencialidade)
assinar com a PRIVADA  ──► qualquer um verifica   (autenticidade)
```

É milhares de vezes mais lenta que a simétrica. Por isso, na prática, **nunca** se
cifra um documento inteiro com chave assimétrica — cifra-se uma chave simétrica.
Que é exatamente o §3.

### Derivação de chave

Transformar uma senha (baixa entropia, escolhida por humano) numa chave
criptográfica (alta entropia):

```
senha + sal + custo ──[Argon2id / scrypt / PBKDF2]──► chave de 256 bits
```

O **custo** é o ponto: essas funções são **deliberadamente lentas** e consomem
memória, para que testar bilhões de senhas por segundo em GPU seja inviável.

| Função | Situação em 2026 |
|---|---|
| **Argon2id** | ⭐ recomendada (vencedora da Password Hashing Competition, 2015) |
| **scrypt** | boa alternativa |
| **bcrypt** | aceitável; limite de 72 bytes na entrada |
| **PBKDF2** | mínimo aceitável; use ≥ 600.000 iterações com SHA-256 |
| **MD5, SHA-1, SHA-256 puro** | ❌ **nunca** para senha — são rápidos demais **por projeto** |

> A confusão mais comum da área: SHA-256 é uma **boa função de hash** e uma **péssima
> função de senha**, exatamente porque é rápida. As duas coisas não são o mesmo
> problema.

---

## 2. Modelo de ameaça: contra quem você está se defendendo?

Sem responder isso, "seguro" não significa nada. Escala prática, do mais fraco ao
mais forte:

| # | Adversário | Variável de ambiente protege? | O que protege |
|---|---|---|---|
| 0 | Commit acidental no Git | ✅ **sim** | `.gitignore` + varredura |
| 1 | Curioso lendo o repositório | ✅ sim | idem |
| 2 | Outro usuário sem privilégio no mesmo servidor | ✅ sim (`chmod 640`) | permissões |
| 3 | Backup ou snapshot vazado | 🟡 parcial | criptografia em repouso |
| 4 | Aplicação comprometida (RCE) | ❌ **não** | menor privilégio, credencial dinâmica |
| 5 | Root no servidor | ❌ **não** | atestação, HSM, enclave |
| 6 | Administrador do hipervisor / provedor de nuvem | ❌ não | computação confidencial |
| 7 | Acesso físico ao hardware | ❌ não | HSM, TPM, resistência a violação |
| 8 | Estado-nação com acesso à cadeia de suprimentos | ❌ não | fora do alcance da maioria |

**Variável de ambiente cobre os níveis 0 a 2 e nada mais.** Isso não é falha: é o
alcance do mecanismo, e para a esmagadora maioria dos sistemas é suficiente, porque
os níveis 0 a 2 são de onde vêm quase todos os incidentes reais.

**A pergunta que ordena qualquer decisão deste curso:**
*qual é o nível mais alto que eu preciso mesmo enfrentar?* Investir em nível 5+
enquanto o nível 0 está aberto (um `.env` no repositório) é o erro de alocação mais
comum em segurança.

---

## 3. Criptografia de envelope

O padrão que sustenta **todos** os cofres modernos: KMS da AWS/GCP/Azure, SOPS,
Kubernetes com KMS v2, `systemd-creds`.

```
   ┌──────────────────────────────────────────────────────────────┐
   │  1. Gera uma DEK (Data Encryption Key) aleatória, de 256 bits │
   │  2. Cifra os DADOS com a DEK       (simétrico, rápido)        │
   │  3. Cifra a DEK com a KEK          (a chave-mestra, no KMS)   │
   │  4. Guarda: [DEK cifrada] + [dados cifrados]                  │
   │  5. DESCARTA a DEK em claro da memória                        │
   └──────────────────────────────────────────────────────────────┘

   Para ler:  KMS decifra a DEK ──► a DEK decifra os dados
```

**Por que essa indireção existe — quatro razões concretas:**

1. **Desempenho.** Cifrar 1 GB com chamadas de rede ao KMS é impraticável;
   cifrar 32 bytes (a DEK), não.
2. **Rotação barata.** Trocar a KEK exige recifrar **apenas as DEKs**, não os
   terabytes de dados. É a diferença entre minutos e semanas.
3. **A chave-mestra nunca sai do HSM.** No KMS da AWS, a KEK **nunca** é exportável.
   Nem você consegue lê-la.
4. **Múltiplos destinatários.** No SOPS, a DEK é cifrada uma vez para cada chave
   `age`. Adicionar alguém à equipe não recifra os valores — acrescenta uma cópia
   da DEK cifrada.

É exatamente o que você vê no rodapé de um arquivo SOPS:

```yaml
sops:
    age:
        - recipient: age1abc...
          enc: |
            -----BEGIN AGE ENCRYPTED FILE-----   ← a DEK cifrada para esta pessoa
        - recipient: age1def...
          enc: |
            -----BEGIN AGE ENCRYPTED FILE-----   ← a MESMA DEK, cifrada para outra
```

---

## 4. O problema do segredo zero

> **Para guardar segredos com segurança, você precisa de um cofre.
> Para falar com o cofre, você precisa de uma credencial.
> Onde você guarda ESSA credencial?**

É uma regressão infinita, e é o problema mais fundamental — e mais ignorado — da área.

```
   segredos da aplicação
        └── protegidos pela credencial do cofre
              └── protegida por…?
                    └── protegida por…?
                          └── ⟳
```

**As cinco formas de quebrar a regressão**, em ordem crescente de robustez:

### (a) Aceitar um segredo em texto no fim da cadeia

`RAILS_MASTER_KEY` no ambiente. A chave `age` do SOPS em `~/.config`.
Um `AppRole secret_id` do Vault num arquivo.

**Ganho real:** de N segredos você passa a 1. Menos superfície, menos rotação.
**Limite:** o último segredo continua exposto.

### (b) Ancorar no hardware

```bash
sudo systemd-creds encrypt --name=api_key entrada.txt saida.cred
```

A chave é selada no **TPM 2.0** da placa-mãe. O arquivo cifrado **só decifra naquela
máquina** — copiá-lo para outra não adianta. O segredo passa a ser uma propriedade do
hardware, não um dado transportável.

Mesma ideia: DPAPI com escopo `LocalMachine` no Windows, Secure Enclave no macOS.

### (c) Ancorar na identidade da plataforma

```
Instância EC2 ──► IMDSv2 ──► credenciais temporárias da IAM role
Pod no K8s ──► token da ServiceAccount ──► auth do Vault
GitHub Actions ──► token OIDC ──► role na nuvem
```

**Não há segredo zero.** A identidade vem de quem **criou** o processo, e é atestada
por ele. Esta é a solução moderna, e é a razão pela qual usar a nuvem "direito" é
mais seguro que gerenciar segredos à mão.

⚠️ Mas cria uma superfície nova: **SSRF vira comprometimento total.** Se a sua
aplicação pode ser induzida a buscar uma URL arbitrária, o atacante pede
`http://169.254.169.254/latest/meta-data/iam/security-credentials/` e recebe as
credenciais da instância. Foi assim que aconteceu o vazamento da Capital One em 2019
(~100 milhões de registros). O **IMDSv2**, que exige um token via `PUT` com cabeçalho
próprio, mitiga isso — **exija IMDSv2** e desative o v1.

### (d) Atestação remota

O hardware **prova criptograficamente** o que está rodando, e só então recebe o segredo:

```
1. A máquina mede o que carregou (firmware → bootloader → kernel → aplicação)
2. O TPM assina essas medidas com uma chave que nunca sai dele
3. O cofre verifica a assinatura e as medidas esperadas
4. Só então libera o segredo
```

Uma máquina com kernel adulterado produz medidas diferentes e **não recebe nada**.
É o mecanismo por trás do Confidential Computing.

### (e) Não ter segredo nenhum

O ideal, e cada vez mais alcançável:

- **mTLS com certificados de vida curta** (SPIFFE/SPIRE): a identidade é o
  certificado, emitido por atestação e válido por horas;
- **Assinatura em vez de segredo compartilhado**: webhooks verificados por chave
  pública, não por segredo simétrico compartilhado;
- **Credencial dinâmica de vida curta**: nada persiste tempo suficiente para valer
  o roubo.

---

## 5. Identidade de carga de trabalho: SPIFFE e SVID

**SPIFFE** (*Secure Production Identity Framework For Everyone*) — projeto graduado
da CNCF — padroniza como um serviço prova quem é, sem senha.

```
spiffe://empresa.com.br/ns/producao/sa/api-pagamentos
        └──── domínio ────┘└──── caminho da carga ────┘
```

O **SVID** (*SPIFFE Verifiable Identity Document*) é a materialização dessa
identidade: um certificado X.509 ou um JWT, **de vida curta** (tipicamente 1 hora),
emitido automaticamente pelo agente SPIRE **após atestar** o processo — por seu
namespace no Kubernetes, seu UID no Linux, sua identidade na nuvem.

```
┌──────────┐  atesta   ┌───────────┐  emite   ┌──────────┐
│ Servidor │◄──────────│  Agente   │─────────►│ Carga de │
│  SPIRE   │           │  SPIRE    │  SVID    │ trabalho │
└──────────┘           └───────────┘  (1 h)   └──────────┘
                             │
                    "este PID pertence ao
                     pod X, no namespace Y,
                     com a imagem Z"
```

**O que isso muda de verdade:** duas cargas de trabalho estabelecem mTLS entre si sem
nenhum segredo compartilhado, sem senha, sem chave de API. A identidade é **derivada
da plataforma** e **verificável**. É a materialização da opção (e) do §4.

É a base de service meshes (Istio, Linkerd) e da autenticação sem segredo entre
serviços. **É para onde a área está indo**, e a direção é clara.

---

## 6. Limites teóricos

Vale saber o que é impossível, para não perseguir.

### 6.1 O problema da caixa branca

> **Impossível:** esconder uma chave criptográfica de alguém que controla o ambiente
> de execução.

Se o programa precisa da chave para funcionar, e o adversário controla a máquina, ele
observa o programa usando a chave. Criptografia de caixa branca
(*white-box cryptography*) tenta dificultar isso; academicamente, **todos** os
esquemas propostos foram quebrados. Ela aumenta o custo do ataque em horas ou dias,
não em ordens de grandeza.

**Consequência direta e prática:** [20-frontend-e-build-time.md](20-frontend-e-build-time.md)
e a Regra 2 de [55-entrega-ao-cliente.md](55-entrega-ao-cliente.md) não são
recomendações — são **teoremas** aplicados.

### 6.2 Ofuscação indistinguível (iO)

A pergunta teórica: existe um jeito de embaralhar um programa de modo que ele revele
**nada** além do que sua saída revela?

- 2001: Barak *et al.* provam que **ofuscação de caixa preta** (o ideal forte) é
  **impossível** em geral.
- 2013: Garg *et al.* propõem candidatos para **iO**, uma noção mais fraca e
  possivelmente atingível.
- 2020: Jain, Lin e Sahai constroem iO a partir de premissas bem fundamentadas —
  um marco teórico enorme.
- 2026: continua **teórico**. As construções são muitas ordens de grandeza lentas
  demais para uso real.

Se um dia for prático, muda tudo neste curso. Não conte com isso.

### 6.3 Criptografia totalmente homomórfica (FHE)

Computar sobre dados cifrados sem decifrar. Gentry (2009) provou ser possível.
Em 2026, é prático apenas em nichos (operações simples, dados pequenos, custo entre
1.000× e 1.000.000× maior). Esquemas parciais (Paillier, aditivo) já são usados em
produção em casos específicos.

### 6.4 Computação confidencial

Enclaves de hardware (Intel SGX/TDX, AMD SEV-SNP, ARM CCA) executam código em memória
cifrada, **inclusive contra o hipervisor** — o nível 6 da tabela do §2. É o que há de
mais avançado em uso comercial.

Ressalva honesta: o histórico do SGX é sofrível. Ataques de canal lateral
(Foreshadow, Plundervolt, SGAxe, ÆPIC Leak) o quebraram repetidamente, e a Intel
descontinuou o SGX em processadores de consumo. AMD SEV-SNP e Intel TDX são as
apostas atuais em servidor. **Não é magia**, e você está confiando no fabricante do
silício.

---

## 7. A regra dos cinco porquês: por que ainda usamos segredos compartilhados?

**1. Por que a maioria dos sistemas ainda usa senha estática de banco de dados?**
Porque é o que o protocolo do banco suporta bem e o que toda biblioteca implementa.

**2. Por que os protocolos de banco foram desenhados assim?**
PostgreSQL (1996), MySQL (1995), Oracle (anos 1980) nasceram num mundo de rede
confiável dentro do datacenter. A autenticação por senha era adequada ao modelo
de ameaça da época.

**3. Por que não trocaram, se hoje existem alternativas melhores?**
Compatibilidade e inércia de ecossistema. PostgreSQL suporta certificado de cliente e
SCRAM desde sempre; quase ninguém configura, porque exige PKI, e PKI exige
gerenciar ciclo de vida de certificados — que é um problema tão grande quanto o
original.

**4. Por que gerenciar certificados é tão difícil?**
Porque exige uma autoridade certificadora, distribuição, revogação (CRL/OCSP, que
funcionam mal) e **renovação antes de expirar**. Um certificado vencido derruba a
produção com a mesma eficiência de uma senha errada — e com um sintoma pior, porque
ninguém está olhando.

**5. Então é impossível?**
Não: é **caro**, e o custo caiu muito. Let's Encrypt + ACME (2016) provaram que
automação resolve o ciclo de vida de certificados na escala da internet. SPIFFE/SPIRE
faz o mesmo dentro do datacenter. **A barreira é organizacional, não técnica** —
e este é o ponto de parada legítimo: um **trade-off econômico explícito**.
Senha estática custa zero para configurar e um incidente eventual; PKI automatizada
custa semanas de engenharia e quase nenhum incidente. A maioria das empresas ainda
escolhe a primeira, e para muitas delas **está certo**.

---

## 8. O estado ideal, e o quanto ele é atingível

```
Nível 0  segredo em texto no código                         ← inaceitável
Nível 1  segredo em .env fora do Git                        ← o mínimo
Nível 2  segredo em arquivo com permissão restrita          ← a maioria está aqui
Nível 3  segredo cifrado em repouso, ancorado em hardware   ← systemd-creds + TPM
Nível 4  segredo em cofre, com auditoria                    ← empresas médias
Nível 5  credencial dinâmica de vida curta                  ← empresas maduras
Nível 6  identidade de carga de trabalho, sem segredo       ← SPIFFE/SPIRE
Nível 7  atestação remota, enclave                          ← fronteira
```

**Onde parar é uma decisão econômica, não moral.** Um sistema no nível 2, com
inventário, rotação anual e monitoramento, é mais seguro na prática que um sistema no
nível 5 mal operado — onde o Vault selado às 3h da manhã leva alguém a "resolver"
copiando os segredos para um arquivo temporário que fica lá para sempre.

**Suba um nível de cada vez, e só quando o anterior estiver sólido.**

---

## Autoteste

1. Por que AES-GCM é preferível a AES-CBC, e o que significa "AEAD"?
2. O que acontece se um nonce se repetir em GCM com a mesma chave?
3. Por que SHA-256 é bom para integridade e péssimo para senha?
4. Contra quais níveis da escala de adversários uma variável de ambiente protege?
5. Explique criptografia de envelope e as quatro razões pelas quais ela existe.
6. Por que adicionar um destinatário num arquivo SOPS não recifra os valores?
7. Enuncie o problema do segredo zero e cite as cinco formas de quebrá-lo.
8. Como o IMDSv2 mitiga a exploração de SSRF, e qual incidente famoso ilustra o risco?
9. O que é um SVID, e por que sua vida curta é essencial ao modelo?
10. Por que "esconder a chave no binário" é teoricamente impossível, e o que Barak *et al.* provaram em 2001?
11. Qual é o trade-off econômico explícito que mantém senhas estáticas em uso?
12. Por que um sistema no nível 2 bem operado pode ser mais seguro que um no nível 5 mal operado?

---

**Fontes consultadas em 14/08/2026:** NIST SP 800-38D (GCM) · NIST SP 800-57 ·
Barak et al., *On the (Im)possibility of Obfuscating Programs* (CRYPTO 2001) ·
Garg et al. (FOCS 2013) · Jain, Lin & Sahai, *Indistinguishability Obfuscation from
Well-Founded Assumptions* (STOC 2021) · Gentry, *A Fully Homomorphic Encryption
Scheme* (2009) · spiffe.io · docs.aws.amazon.com (KMS envelope encryption, IMDSv2) ·
freedesktop.org (systemd-creds).

**Próximo:** [65-estado-da-arte.md](65-estado-da-arte.md) · Voltar ao [mapa](00-MAPA.md)
