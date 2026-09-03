# 04 · Como começar — do zero ao primeiro resultado

`Nível: iniciante` · `Atualizado em: 14/08/2026`

> Pressupõe o ambiente do [03-instalacao.md](03-instalacao.md). Se você só tem um
> terminal e o Node (ou Python, ou PHP), já dá para fazer **tudo** deste arquivo.
> **Todos os comandos e todas as saídas abaixo foram executados de verdade**
> em Ubuntu 22.04.5 com Node v24.18.0, Python 3.10.12 e PHP 8.1.2, em 14/08/2026.

---

## Passo 0 · Ver o ambiente que já existe

Antes de criar variável nenhuma, olhe as que você já tem:

```bash
printenv | head -10
```

Você vai ver `PATH`, `HOME`, `USER`, `LANG`, `SHELL` e outras. Ninguém "instalou"
isso: são o ambiente que o seu shell recebeu do processo que o iniciou.

Veja uma só:

```bash
echo $HOME
# esperado: /home/seu-usuario
```

**Já aprendeu o mecanismo inteiro.** O resto é ferramenta ao redor dele.

---

## Passo 1 · O menor programa possível que lê uma variável

Crie uma pasta e um arquivo:

```bash
mkdir -p ~/lab-env && cd ~/lab-env
```

**Node** — `ola.js`:

```javascript
// ola.js — lê MEU_NOME do ambiente; se não existir, usa um padrão.
console.log("Olá,", process.env.MEU_NOME ?? "estranho");
```

**Python** — `ola.py`:

```python
# ola.py
import os
print("Olá,", os.environ.get("MEU_NOME", "estranho"))
```

**PHP** — `ola.php`:

```php
<?php
// ola.php
$nome = getenv("MEU_NOME") ?: "estranho";
echo "Olá, $nome\n";
```

Rode sem definir nada:

```bash
node ola.js
```
```
Olá, estranho
```

✅ **Verificação:** apareceu `estranho`. O programa leu o ambiente, não achou a
variável, e usou o padrão. Se deu erro de sintaxe, confira se copiou o arquivo inteiro.

---

## Passo 2 · Passar a variável **só para aquele comando**

```bash
MEU_NOME=Ronivaldo node ola.js
```
```
Olá, Ronivaldo
```

Agora rode de novo, sem o prefixo:

```bash
node ola.js
```
```
Olá, estranho
```

✅ **Verificação e a lição:** a variável **não ficou**. Ela existiu apenas no processo
que você acabou de criar, e morreu com ele. Isso é a propriedade mais importante de
variável de ambiente e a razão de ela ser boa para segredo: **não é um arquivo, não
tem persistência, não sobra em disco**.

Em PowerShell não existe esse prefixo; use:

```powershell
$env:MEU_NOME="Ronivaldo"; node ola.js
```

---

## Passo 3 · `export` — valer para a sessão inteira

```bash
export MEU_NOME=Maria
node ola.js
```
```
Olá, Maria
```

```bash
python3 ola.py
```
```
Olá, Maria
```

✅ Todo programa iniciado a partir **deste** terminal agora herda `MEU_NOME`.
Abra **outro** terminal e rode `echo $MEU_NOME`: sai vazio. Cada terminal é um
processo com sua própria cópia do ambiente. Não existe "variável global do sistema"
para processos já em execução.

Para remover:

```bash
unset MEU_NOME
```

---

## Passo 4 · O arquivo `.env`

Digitar variável na mão a cada comando não escala quando são quinze delas.
Daí o `.env`.

```bash
cat > .env <<'EOF'
MEU_NOME=vindo-do-env
DATABASE_URL=postgres://app:senha-de-brincadeira@localhost:5432/loja
PORT=3000
EOF
```

**Antes de qualquer outra coisa**, proteja-o:

```bash
git init -q 2>/dev/null; printf '.env\n' > .gitignore && chmod 600 .env
```

```bash
ls -l .env
# esperado: -rw------- 1 seu-usuario seu-usuario ... .env
```

### Node ≥ 20.6 — sem biblioteca nenhuma

```bash
node --env-file=.env ola.js
```
```
Olá, vindo-do-env
```

✅ Funcionou sem instalar nada. O Node leu o arquivo, injetou em `process.env`, e o
seu código continua o mesmo — ele não sabe que existe um `.env`.

### Python

```bash
pip install python-dotenv
```

`ola_dotenv.py`:

```python
# ola_dotenv.py
from dotenv import load_dotenv
import os

load_dotenv()   # lê .env do diretório atual e injeta em os.environ
print("Olá,", os.environ.get("MEU_NOME", "estranho"))
```

```bash
python3 ola_dotenv.py
# esperado: Olá, vindo-do-env
```

### PHP

```bash
composer require vlucas/phpdotenv
```

`ola_dotenv.php`:

```php
<?php
// ola_dotenv.php
require __DIR__ . '/vendor/autoload.php';

$dotenv = Dotenv\Dotenv::createImmutable(__DIR__);
$dotenv->safeLoad();   // safeLoad não explode se o .env não existir — o certo em produção

echo "Olá, " . ($_ENV['MEU_NOME'] ?? 'estranho') . "\n";
```

```bash
php ola_dotenv.php
# esperado: Olá, vindo-do-env
```

---

## Passo 5 · A regra de precedência — o experimento que muda tudo

Este é o passo que quase nenhum tutorial mostra, e é **a chave para entender por que
o `.env` não precisa ir para produção**.

Defina a variável no ambiente **e** deixe o `.env` com outro valor:

```bash
export MEU_NOME=Maria
node --env-file=.env ola.js
```
```
Olá, Maria
```

**Leia de novo.** O `.env` diz `vindo-do-env`. O ambiente diz `Maria`.
**O ambiente ganhou.**

Confirme com valor passado só naquele comando:

```bash
MEU_NOME=CLI node --env-file=.env ola.js
```
```
Olá, CLI
```

> **A regra:** o carregador de `.env` (nativo do Node, `python-dotenv` com o padrão,
> `phpdotenv` com `createImmutable`) **só preenche o que ainda não existe**.
> Variável já presente no ambiente **não é sobrescrita**.

E é por isso que a resposta da pergunta inicial funciona:

> Em produção, **as variáveis já existem no ambiente** (postas pelo systemd, pelo
> Docker, pelo painel do PaaS…). Mesmo que um `.env` sobrasse por acidente,
> as de verdade venceriam. E se você **não** enviar o `.env`, o programa funciona
> exatamente igual — porque ele nunca leu o arquivo, ele leu o **ambiente**.
>
> **O `.env` é um dispositivo para preencher o ambiente quando ninguém mais o preencheu.**

`unset MEU_NOME` antes de seguir.

---

## Passo 6 · O ciclo de trabalho do dia a dia

```
   ┌──────────────────────────────────────────────────────┐
   │  1. clonar o projeto                                 │
   │     git clone ...                                    │
   ├──────────────────────────────────────────────────────┤
   │  2. copiar o contrato                                │
   │     cp .env.example .env                             │
   ├──────────────────────────────────────────────────────┤
   │  3. preencher os valores locais                      │
   │     (senhas de brincadeira, banco local)             │
   ├──────────────────────────────────────────────────────┤
   │  4. rodar                                            │
   │     node --env-file=.env src/app.js                  │
   ├──────────────────────────────────────────────────────┤
   │  5. faltou variável? o programa AVISA e PARA         │
   │     "Configuração inválida: falta DATABASE_URL"      │
   ├──────────────────────────────────────────────────────┤
   │  6. adicionou variável nova?                         │
   │     → acrescente ao .env.example E commite ESSE      │
   └──────────────────────────────────────────────────────┘
```

O passo 5 merece destaque: **valide a configuração na inicialização e falhe rápido**.
Um sistema que sobe com `DATABASE_URL` indefinida e só quebra três horas depois,
no primeiro acesso do cliente, é um sistema mal configurado. Como fazer isso:
[06-exemplos.md #3](06-exemplos.md) e o [projeto-modelo](07-projeto-modelo/README.md).

O passo 6 é o mais esquecido em equipe: quem adiciona variável e não atualiza o
`.env.example` quebra a máquina de todo mundo no próximo `git pull`.

---

## Passo 7 · Simule produção agora, na sua máquina

Você não precisa de servidor para ver como será em produção. Rode **sem** o `.env`,
passando as variáveis pelo ambiente — que é literalmente o que o systemd, o Docker e
o Heroku fazem:

```bash
mv .env .env.guardado
```

```bash
node ola.js
# esperado: Olá, estranho    ← sem .env, sem variáveis
```

```bash
MEU_NOME=producao DATABASE_URL=postgres://real PORT=8080 node ola.js
# esperado: Olá, producao    ← funcionou sem .env nenhum
```

✅ **Esse é o experimento inteiro deste curso.** Se a sua aplicação passa neste teste
— rodar sem `.env`, recebendo tudo pelo ambiente — ela está pronta para produção.
Se ela quebra porque `dotenv.config()` não achou o arquivo, você tem um acoplamento
para consertar, e o conserto está em [15-node.md](15-node.md), [16-php.md](16-php.md)
ou [17-python.md](17-python.md).

```bash
mv .env.guardado .env
```

---

## Passo 8 · Os cinco primeiros erros de uso (não de instalação)

### 1. `dotenv` carregado depois de quem precisa dele

```javascript
// ❌ ERRADO
import { pool } from './db.js';   // db.js já leu process.env.DATABASE_URL aqui — vazia
import 'dotenv/config';
```
Em ESM, **todos os `import` são resolvidos antes de qualquer linha executar**, e na
ordem em que aparecem. `db.js` roda antes do dotenv.

```javascript
// ✅ CERTO
import 'dotenv/config';           // primeiro de tudo
import { pool } from './db.js';
```
Melhor ainda: `node --env-file=.env app.js` — o ambiente já está pronto antes do
primeiro byte do seu código.

### 2. O `.env` não é encontrado

As bibliotecas procuram no **diretório de trabalho atual** (de onde você rodou o
comando), **não** ao lado do arquivo de código.

```bash
cd ~/lab-env/src && node ../ola.js     # não acha o .env que está em ~/lab-env
```

Correção: rode da raiz do projeto, ou passe o caminho:

```javascript
import { config } from 'dotenv';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
config({ path: join(dirname(fileURLToPath(import.meta.url)), '..', '.env') });
```

### 3. Aspas que viram parte do valor

```bash
# .env
SENHA="abc123"
```
O carregador **nativo do Node** e o `dotenv` removem as aspas.
Mas se você fizer `export SENHA="abc123"` no shell, o shell também remove — e se
você escrever `SENHA='"abc123"'`, as aspas ficam. Regra prática: **não use aspas
salvo quando o valor tiver espaço ou `#`**.

```bash
node --env-file=.env -e 'console.log(JSON.stringify(process.env.SENHA))'
# esperado: "abc123"   ← e não "\"abc123\""
```

### 4. Tudo vira string

```javascript
process.env.PORT           // "3000" — string, não número
process.env.DEBUG          // "false" — e Boolean("false") === true !!
```

```javascript
// ✅
const port = Number(process.env.PORT ?? 3000);
const debug = process.env.DEBUG === 'true';
```
Em Python, `os.environ["DEBUG"]` também é `"false"`, e `bool("false")` é `True`.
Este erro derruba produção com frequência assustadora.

### 5. Cifrão e crase dentro do valor

```bash
# .env
SENHA=abc$123
```
Alguns carregadores tentam expandir `$123`; o nativo do Node **não expande**; o
`dotenv` expande só com o plugin `dotenv-expand`. Resultado: a mesma senha funciona
numa linguagem e falha em outra.

**Recomendação profissional:** gere segredos com alfabeto seguro
(`A–Z a–z 0–9 - _`), fugindo de `$`, `` ` ``, `"`, `'`, `\` e `#`. Você evita uma
classe inteira de bug que só aparece em produção, às 3h da manhã.

```bash
openssl rand -base64 32 | tr -d '/+=' | head -c 32; echo
# gera uma senha forte sem caracteres problemáticos
```

---

## Passo 9 · Higiene mínima antes de fechar o terminal

```bash
git status --short
# esperado: NENHUMA linha mencionando .env
```

```bash
grep -q '^\.env$' .gitignore && echo "protegido" || echo "PERIGO: adicione .env ao .gitignore"
```

```bash
history | grep -iE 'password|secret|token|key=' | head
```
Se aparecer alguma coisa, você digitou um segredo no terminal e ele está no
`~/.bash_history` em texto puro. Limpe com `history -d <número>` e considere o
segredo comprometido se a máquina for compartilhada.

> **Dica que só quem já se queimou conhece:** em bash, um comando iniciado com
> **espaço** não entra no histórico, se `HISTCONTROL` incluir `ignorespace`:
> ```bash
> export HISTCONTROL=ignorespace
>  export TOKEN=abc123     # ← repare no espaço antes de "export"
> ```

---

## Para onde ir agora

| Se você quer… | Vá para |
|---|---|
| ver 12 receitas prontas | [06-exemplos.md](06-exemplos.md) |
| um sistema inteiro funcionando | [07-projeto-modelo/](07-projeto-modelo/README.md) |
| entender por que funciona assim | [10-fundamentos.md](10-fundamentos.md) |
| **a resposta direta da sua pergunta original** | [30-entrega-em-producao.md](30-entrega-em-producao.md) |
| a referência de comandos | [05-manual-de-uso.md](05-manual-de-uso.md) |

---

## Autoteste

1. Você roda `MEU_NOME=X node app.js`. Depois roda `node app.js`. Por que a variável sumiu?
2. `.env` diz `PORT=3000`; o ambiente diz `PORT=8080`. Qual vence, e por quê isso é útil?
3. Por que `import 'dotenv/config'` precisa vir antes dos outros `import`?
4. `process.env.DEBUG` vale `"false"`. `if (process.env.DEBUG)` entra no `if`? Por quê?
5. Como você comprova, na sua máquina, que a aplicação está pronta para rodar sem `.env`?
6. Por que gerar senha sem `$` e `#` evita bug de produção?
7. O que `chmod 600 .env` impede, concretamente, num servidor com vários usuários?

---

**Próximo:** [05-manual-de-uso.md](05-manual-de-uso.md) · Voltar ao [mapa](00-MAPA.md)
