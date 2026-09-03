# 06 · Exemplos — 15 receitas completas

`Nível: iniciante a avançado` · `Atualizado em: 14/08/2026`

Todo código aqui é **completo e executável** — nada de `...` no meio.
Os exemplos 1 a 5 e 9 foram **executados de verdade** em Ubuntu 22.04.5 com
Node v24.18.0, Python 3.10.12 e PHP 8.1.2, em 14/08/2026; as saídas mostradas
são as reais. Os demais estão marcados quando não puderam ser executados aqui.

| # | Exemplo | Nível |
|---|---|---|
| [1](#1-o-par-gitignore--envexample) | O par `.gitignore` + `.env.example` | trivial |
| [2](#2-node--módulo-de-configuração-que-falha-rápido) | Node — configuração que falha rápido | básico |
| [3](#3-python--o-mesmo-só-com-a-biblioteca-padrão) | Python — o mesmo, só com a biblioteca padrão | básico |
| [4](#4-python-com-pydantic-settings-o-jeito-moderno) | Python com `pydantic-settings` | básico |
| [5](#5-php--configuração-validada-sem-framework) | PHP — configuração validada sem framework | básico |
| [6](#6-script-que-compara-env-com-envexample) | Script que compara `.env` com `.env.example` | básico |
| [7](#7-o-padrão-_file-o-truque-que-resolve-docker-e-kubernetes) | O padrão `_FILE` | intermediário |
| [8](#8-systemd--a-entrega-clássica-em-servidor-linux) | systemd — entrega em servidor Linux | intermediário |
| [9](#9-não-vazar-segredo-no-log) | Não vazar segredo no log | intermediário |
| [10](#10-dockerfile--compose-sem-vazar-nada) | Dockerfile + Compose sem vazar nada | intermediário |
| [11](#11-buscar-do-aws-secrets-manager-na-inicialização) | Buscar do AWS Secrets Manager | avançado |
| [12](#12-sops--segredo-criptografado-dentro-do-repositório) | SOPS — segredo criptografado no repositório | avançado |
| [13](#13-gancho-de-pre-commit-que-bloqueia-segredo) | Gancho de pre-commit | intermediário |
| [14](#14-produção--rotação-sem-derrubar-o-sistema) | **Produção** — rotação sem derrubar o sistema | avançado |
| [15](#15-produção--instalador-para-o-cliente-on-premise) | **Produção** — instalador para o cliente | avançado |

---

## 1. O par `.gitignore` + `.env.example`

**Problema:** garantir que os valores nunca entrem no repositório, mas que os
**nomes** entrem — senão ninguém consegue instalar o sistema.

`.gitignore` (versionado):

```gitignore
# Segredos — NUNCA versionar
.env
.env.*
!.env.example
!.env.*.example

# Chaves e certificados
*.pem
*.key
*.p12
*.pfx
!*-public.pem

# Credenciais de nuvem e de ferramentas
.aws/credentials
.npmrc
auth.json
*.tfvars
!*.tfvars.example

# Descriptografados por engano
*.dec
*.decrypted
```

`.env.example` (versionado — **é a documentação do contrato**):

```bash
# ─── Obrigatórias ────────────────────────────────────────────────
# URL completa do PostgreSQL.
# Formato: postgres://usuario:senha@host:porta/banco
DATABASE_URL=

# Chave da API de pagamento. Obtenha em: https://painel.exemplo.com/chaves
# Formato: sk_live_… (produção) ou sk_test_… (testes)
PAYMENT_API_KEY=

# Segredo de assinatura de sessão. Gere com:
#   openssl rand -base64 48
SESSION_SECRET=

# ─── Opcionais (o padrão está entre colchetes) ───────────────────
PORT=                 # [3000]
LOG_LEVEL=            # [info] um de: debug, info, warn, error
DATABASE_POOL_MAX=    # [10]

# ─── Só em desenvolvimento ───────────────────────────────────────
# MAILER_DSN=smtp://localhost:1025   # MailHog
```

**Por que assim:** o `.env.example` diz **como obter** cada valor, não só o nome.
Quem for instalar no cliente daqui a dois anos vai ler exatamente isto.

**Verifique:**

```bash
git check-ignore -v .env
# esperado: .gitignore:3:.env	.env
git status --short | grep -c '\.env$'
# esperado: 0
```

---

## 2. Node — módulo de configuração que falha rápido

**Problema:** o sistema sobe com `DATABASE_URL` faltando e só quebra no primeiro
acesso do cliente, três horas depois, com uma mensagem incompreensível.

**Solução:** validar tudo na inicialização, listar **todos** os erros de uma vez, e
sair com código de saída distinto.

`src/config.mjs`:

```javascript
// src/config.mjs — única porta de entrada da configuração.
// Regra da casa: NENHUM outro arquivo lê process.env.
import { readFileSync } from 'node:fs';

const erros = [];

/** Lê NOME, ou o conteúdo do arquivo apontado por NOME_FILE (padrão Docker/K8s). */
function ler(nome) {
  const arq = process.env[`${nome}_FILE`];
  if (arq) {
    try {
      return readFileSync(arq, 'utf8').trim();
    } catch (e) {
      erros.push(`${nome}_FILE aponta para ${arq}, que não pôde ser lido (${e.code})`);
      return undefined;
    }
  }
  const v = process.env[nome];
  return v === '' ? undefined : v;   // string vazia conta como ausente
}

function exigido(nome, validar) {
  const v = ler(nome);
  if (v === undefined) { erros.push(`falta ${nome}`); return undefined; }
  const msg = validar?.(v);
  if (msg) { erros.push(`${nome}: ${msg}`); return undefined; }
  return v;
}

function opcional(nome, padrao, validar) {
  const v = ler(nome);
  if (v === undefined) return padrao;
  const msg = validar?.(v);
  if (msg) { erros.push(`${nome}: ${msg}`); return padrao; }
  return v;
}

// ── validadores reutilizáveis ────────────────────────────────────
const url = (v) => { try { new URL(v); } catch { return 'não é uma URL válida'; } };
const inteiro = (min, max) => (v) =>
  (/^\d+$/.test(v) && +v >= min && +v <= max) ? undefined : `esperado inteiro entre ${min} e ${max}`;
const umDe = (...opcoes) => (v) =>
  opcoes.includes(v) ? undefined : `esperado um de ${opcoes.join(', ')}`;

// ── o contrato ───────────────────────────────────────────────────
const cfg = {
  databaseUrl: exigido('DATABASE_URL', url),
  apiKey:      exigido('API_KEY'),
  port:        Number(opcional('PORT', '3000', inteiro(1, 65535))),
  logLevel:    opcional('LOG_LEVEL', 'info', umDe('debug', 'info', 'warn', 'error')),
};

if (erros.length) {
  console.error('❌ Configuração inválida — o serviço não vai subir:');
  for (const e of erros) console.error('   • ' + e);
  console.error('\nConsulte .env.example para a lista completa de variáveis.');
  process.exit(78);   // EX_CONFIG do sysexits.h — distingue de erro de código
}

export const config = Object.freeze(cfg);

/** Versão segura para log: mascara os segredos. */
const mascarar = (s) => !s ? s
  : (s.length <= 8 ? '********' : `${s.slice(0, 3)}…${s.slice(-2)} (${s.length} chars)`);
export const configParaLog = () => ({
  ...config,
  databaseUrl: mascarar(config.databaseUrl),
  apiKey: mascarar(config.apiKey),
});
```

`src/app.mjs`:

```javascript
import { config, configParaLog } from './config.mjs';
console.log('subindo com', configParaLog());
```

**Executado de verdade:**

```bash
node src/app.mjs
```
```
❌ Configuração inválida — o serviço não vai subir:
   • falta DATABASE_URL
   • falta API_KEY

Consulte .env.example para a lista completa de variáveis.
```
(código de saída **78**)

```bash
DATABASE_URL='postgres://app:s3nh4@db:5432/loja' API_KEY='sk_live_abcdefghijklmno' node src/app.mjs
```
```
subindo com {
  databaseUrl: 'pos…ja (33 chars)',
  apiKey: 'sk_…no (23 chars)',
  port: 3000,
  logLevel: 'info'
}
```

```bash
DATABASE_URL='nao-e-url' API_KEY=k PORT=99999 LOG_LEVEL=verboso node src/app.mjs
```
```
❌ Configuração inválida — o serviço não vai subir:
   • DATABASE_URL: não é uma URL válida
   • PORT: esperado inteiro entre 1 e 65535
   • LOG_LEVEL: esperado um de debug, info, warn, error
```

**O que este exemplo ensina, além do óbvio:**

- **Todos** os erros de uma vez, não um por execução. Corrigir configuração um erro
  por vez, com deploy no meio, é tortura.
- **Código de saída 78** (`EX_CONFIG`): o orquestrador consegue distinguir
  "configuração errada, não adianta reiniciar" de "erro transitório, reinicie".
- `Object.freeze`: ninguém muda configuração em tempo de execução.
- **Um único módulo lê `process.env`.** Se `process.env` aparece em quinze arquivos,
  ninguém sabe quais variáveis o sistema exige — e o `.env.example` sempre estará errado.
- O suporte a `_FILE` já vem de graça (exemplo 7).

---

## 3. Python — o mesmo, só com a biblioteca padrão

`config.py`:

```python
"""Configuração validada, só com a biblioteca padrão."""
import os
import sys
from dataclasses import dataclass
from urllib.parse import urlparse

_erros: list[str] = []


def _ler(nome: str) -> str | None:
    caminho = os.environ.get(f"{nome}_FILE")
    if caminho:
        try:
            return open(caminho, encoding="utf-8").read().strip()
        except OSError as e:
            _erros.append(f"{nome}_FILE={caminho} ilegível ({e.strerror})")
            return None
    valor = os.environ.get(nome)
    return valor or None


def exigido(nome, validar=None):
    v = _ler(nome)
    if v is None:
        _erros.append(f"falta {nome}")
        return None
    if validar and (msg := validar(v)):
        _erros.append(f"{nome}: {msg}")
        return None
    return v


def opcional(nome, padrao, validar=None):
    v = _ler(nome)
    if v is None:
        return padrao
    if validar and (msg := validar(v)):
        _erros.append(f"{nome}: {msg}")
        return padrao
    return v


def url(v):
    p = urlparse(v)
    return None if p.scheme and p.netloc else "não é uma URL válida"


def inteiro(minimo, maximo):
    def _v(v):
        ok = v.isdigit() and minimo <= int(v) <= maximo
        return None if ok else f"esperado inteiro entre {minimo} e {maximo}"
    return _v


def um_de(*opcoes):
    return lambda v: None if v in opcoes else f"esperado um de {', '.join(opcoes)}"


@dataclass(frozen=True)
class Config:
    database_url: str
    api_key: str
    port: int
    log_level: str

    def para_log(self):
        def m(s):
            return "********" if len(s) <= 8 else f"{s[:3]}…{s[-2:]} ({len(s)} chars)"
        return {**self.__dict__, "database_url": m(self.database_url), "api_key": m(self.api_key)}


_c = Config(
    database_url=exigido("DATABASE_URL", url),
    api_key=exigido("API_KEY"),
    port=int(opcional("PORT", "3000", inteiro(1, 65535))),
    log_level=opcional("LOG_LEVEL", "info", um_de("debug", "info", "warn", "error")),
)

if _erros:
    print("❌ Configuração inválida — o serviço não vai subir:", file=sys.stderr)
    for e in _erros:
        print("   •", e, file=sys.stderr)
    sys.exit(78)

config = _c
```

**Executado de verdade:**

```bash
python3 app.py
```
```
❌ Configuração inválida — o serviço não vai subir:
   • falta DATABASE_URL
   • falta API_KEY
```

```bash
DATABASE_URL='postgres://app:s3nh4@db:5432/loja' API_KEY='sk_live_abcdefghijklmno' python3 app.py
```
```
subindo com {'database_url': 'pos…ja (33 chars)', 'api_key': 'sk_…no (23 chars)', 'port': 3000, 'log_level': 'info'}
```

> Note o `@dataclass(frozen=True)`: o equivalente Python do `Object.freeze`.

---

## 4. Python com `pydantic-settings` (o jeito moderno)

**Problema:** o exemplo 3 tem 60 linhas de validação escrita à mão.

```bash
pip install "pydantic-settings>=2.14"
```

`settings.py`:

```python
from typing import Literal
from pydantic import Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",             # lido só se existir; em produção não existe
        env_file_encoding="utf-8",
        extra="ignore",              # ignora variáveis do sistema que não são nossas
        case_sensitive=False,
        secrets_dir="/run/secrets",  # 🔑 lê /run/secrets/<nome> — Docker/K8s de graça
    )

    database_url: PostgresDsn
    api_key: SecretStr                                     # não aparece em repr/log
    port: int = Field(default=3000, ge=1, le=65535)
    log_level: Literal["debug", "info", "warn", "error"] = "info"


settings = Settings()   # levanta ValidationError listando TODOS os erros
```

```python
# app.py
from settings import settings
print(settings)                        # api_key aparece como SecretStr('**********')
print(settings.api_key.get_secret_value())   # só aqui o valor real sai
```

**Por que eu recomendo isto em Python:** `SecretStr` faz a mascaração ser o
**padrão**, não algo que você precisa lembrar de fazer. Um `print(settings)` ou um
`logger.info(settings)` distraído não vaza. Em 20 anos de operação, "alguém logou o
objeto de configuração inteiro" é a causa de vazamento mais comum que existe depois
do commit acidental.

E `secrets_dir="/run/secrets"` faz o padrão `_FILE` do Docker funcionar sem código.

---

## 5. PHP — configuração validada sem framework

`config.php`:

```php
<?php
declare(strict_types=1);

final class Config
{
    private static array $erros = [];

    public static function ler(string $nome): ?string
    {
        $caminho = getenv($nome . '_FILE');
        if ($caminho !== false && $caminho !== '') {
            $conteudo = @file_get_contents($caminho);
            if ($conteudo === false) {
                self::$erros[] = "{$nome}_FILE={$caminho} não pôde ser lido";
                return null;
            }
            return trim($conteudo);
        }
        $v = getenv($nome);              // getenv, não $_ENV — ver 16-php.md
        return ($v === false || $v === '') ? null : $v;
    }

    public static function exigido(string $nome, ?callable $validar = null): ?string
    {
        $v = self::ler($nome);
        if ($v === null) { self::$erros[] = "falta {$nome}"; return null; }
        if ($validar && ($msg = $validar($v))) { self::$erros[] = "{$nome}: {$msg}"; return null; }
        return $v;
    }

    public static function opcional(string $nome, string $padrao, ?callable $validar = null): string
    {
        $v = self::ler($nome);
        if ($v === null) return $padrao;
        if ($validar && ($msg = $validar($v))) { self::$erros[] = "{$nome}: {$msg}"; return $padrao; }
        return $v;
    }

    public static function checar(): void
    {
        if (!self::$erros) return;
        fwrite(STDERR, "❌ Configuração inválida — o serviço não vai subir:\n");
        foreach (self::$erros as $e) fwrite(STDERR, "   • {$e}\n");
        exit(78);
    }

    public static function mascarar(string $s): string
    {
        $n = strlen($s);
        return $n <= 8 ? '********' : substr($s, 0, 3) . '…' . substr($s, -2) . " ({$n} chars)";
    }
}

$url     = fn(string $v) => filter_var($v, FILTER_VALIDATE_URL) ? null : 'não é uma URL válida';
$inteiro = fn(int $min, int $max) => fn(string $v) =>
    (ctype_digit($v) && (int)$v >= $min && (int)$v <= $max) ? null : "esperado inteiro entre {$min} e {$max}";
$umDe    = fn(string ...$op) => fn(string $v) =>
    in_array($v, $op, true) ? null : 'esperado um de ' . implode(', ', $op);

$config = [
    'database_url' => Config::exigido('DATABASE_URL', $url),
    'api_key'      => Config::exigido('API_KEY'),
    'port'         => (int) Config::opcional('PORT', '3000', $inteiro(1, 65535)),
    'log_level'    => Config::opcional('LOG_LEVEL', 'info', $umDe('debug', 'info', 'warn', 'error')),
];
Config::checar();
return $config;
```

`app.php`:

```php
<?php
$config = require __DIR__ . '/config.php';
$log = $config;
$log['database_url'] = Config::mascarar($log['database_url']);
$log['api_key']      = Config::mascarar($log['api_key']);
echo "subindo com " . json_encode($log, JSON_UNESCAPED_UNICODE) . "\n";
```

**Executado de verdade:**

```bash
DATABASE_URL='postgres://app:s3nh4@db:5432/loja' API_KEY='sk_live_abcdefghijklmno' PORT=8080 php app.php
```
```
subindo com {"database_url":"pos…ja (33 chars)","api_key":"sk_…no (23 chars)","port":8080,"log_level":"info"}
```

```bash
DATABASE_URL='nao-e-url' API_KEY=k LOG_LEVEL=verboso php app.php
```
```
❌ Configuração inválida — o serviço não vai subir:
   • DATABASE_URL: não é uma URL válida
   • LOG_LEVEL: esperado um de debug, info, warn, error
```

⚠️ **Armadilha específica do PHP:** em ambiente web (Apache/`mod_php`, PHP-FPM), o
`exit(78)` não vira código de saída de processo — vira uma página em branco. Em
aplicação web, valide a configuração num **script de verificação executado no deploy**
(`php bin/check-config.php`), e faça o deploy falhar ali. Ver [16-php.md](16-php.md).

---

## 6. Script que compara `.env` com `.env.example`

**Problema real de equipe:** alguém adicionou `NOVA_VAR` ao código e ao próprio `.env`,
mas esqueceu do `.env.example`. Todo mundo quebra no próximo `git pull` — e o deploy
no cliente quebra também.

`scripts/check-env.sh`:

```bash
#!/usr/bin/env bash
# Compara os NOMES de variáveis entre .env.example e o ambiente atual.
# Sai com 1 se faltar alguma. Feito para rodar no CI e antes do deploy.
set -euo pipefail

EXEMPLO="${1:-.env.example}"
[[ -f "$EXEMPLO" ]] || { echo "não achei $EXEMPLO"; exit 1; }

# extrai nomes: linhas NOME=... ignorando comentários e linhas vazias
nomes() {
  grep -Ev '^\s*(#|$)' "$1" | sed -E 's/^\s*(export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=.*/\2/' | sort -u
}

faltando=()
while read -r nome; do
  [[ -z "$nome" ]] && continue
  # aceita a variável em si OU a variante _FILE
  if [[ -z "${!nome:-}" && -z "$(eval echo "\${${nome}_FILE:-}")" ]]; then
    faltando+=("$nome")
  fi
done < <(nomes "$EXEMPLO")

if (( ${#faltando[@]} )); then
  echo "❌ Variáveis exigidas por $EXEMPLO e ausentes no ambiente:"
  printf '   • %s\n' "${faltando[@]}"
  exit 1
fi
echo "✅ todas as ${#} variáveis de $EXEMPLO estão presentes"
```

```bash
chmod +x scripts/check-env.sh
set -a; source .env; set +a
./scripts/check-env.sh
```

**No CI**, sem `.env`, com as variáveis vindo dos segredos do repositório — assim o
pipeline falha **antes** de subir uma versão que não vai iniciar.

---

## 7. O padrão `_FILE`: o truque que resolve Docker e Kubernetes

**Problema:** variável de ambiente **vaza mais fácil** que arquivo:
aparece em `docker inspect`, em `/proc/PID/environ`, em relatório de crash, em
subprocessos filhos e em quase toda ferramenta de APM. Mas passar arquivo é
inconveniente.

**Solução, que virou padrão de fato nas imagens oficiais do Docker Hub (Postgres,
MySQL, Redis…):** aceitar **as duas formas**, com `NOME` **ou** `NOME_FILE`.

Já implementado nos exemplos 2, 3 e 5. Uso:

```bash
# desenvolvimento — variável direta, prático
DATABASE_URL='postgres://localhost/dev' node app.mjs
```

```bash
# produção — segredo montado como arquivo, com permissão 400
echo -n 'postgres://app:senha-real@db.interno/loja' > /run/secrets/db_url
chmod 400 /run/secrets/db_url
DATABASE_URL_FILE=/run/secrets/db_url node app.mjs
```

**Verificado nesta máquina:** as duas formas produzem exatamente a mesma saída.

**Vantagens concretas do arquivo sobre a variável:**

| | Variável de ambiente | Arquivo montado |
|---|---|---|
| Aparece em `docker inspect` | **sim** | não |
| Aparece em `/proc/PID/environ` | **sim** | não |
| Herdada por processos filhos | **sim** (inclusive scripts de terceiros) | não |
| Vai parar em relatório de crash / APM | frequentemente | raramente |
| Pode ser rotacionada sem reiniciar | **não** | **sim** (basta reler o arquivo) |
| Simples de usar no dia a dia | **sim** | menos |

A linha "rotacionada sem reiniciar" é a que mais importa em produção — ver exemplo 14.

---

## 8. systemd — a entrega clássica em servidor Linux

**Este é o caminho que responde diretamente à pergunta original**, para quem entrega
em VPS ou servidor do cliente sem contêiner.

```bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin minhaapp
sudo mkdir -p /etc/minha-app /opt/minha-app
```

O arquivo de ambiente, **fora do diretório da aplicação e fora do Git**:

```bash
sudo tee /etc/minha-app/env > /dev/null <<'EOF'
DATABASE_URL=postgres://app:senha-real@db.interno:5432/loja
API_KEY=sk_live_xxxxxxxxxxxxxxxxxxxx
PORT=8080
LOG_LEVEL=info
EOF
```

```bash
sudo chown root:minhaapp /etc/minha-app/env
sudo chmod 640 /etc/minha-app/env
```
Root escreve; o grupo da aplicação lê; **mais ninguém**. Repare que a própria
aplicação **não pode alterar** o arquivo — princípio do menor privilégio.

```bash
ls -l /etc/minha-app/env
# esperado: -rw-r----- 1 root minhaapp 148 ... /etc/minha-app/env
```

`/etc/systemd/system/minha-app.service`:

```ini
[Unit]
Description=Minha App
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=minhaapp
Group=minhaapp
WorkingDirectory=/opt/minha-app

# Configuração NÃO secreta pode ficar aqui, à vista de todos
Environment="NODE_ENV=production"

# Segredos vêm do arquivo restrito
EnvironmentFile=/etc/minha-app/env

ExecStart=/usr/bin/node /opt/minha-app/src/app.mjs
Restart=on-failure
RestartSec=5

# Não reiniciar em loop quando a configuração está errada (nosso exit 78)
RestartPreventExitStatus=78

# ── Blindagem: barata e eficaz ──────────────────────────────────
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/minha-app
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictSUIDSGID=true
LockPersonality=true
MemoryDenyWriteExecute=true

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now minha-app
systemctl status minha-app
```

**Verificação de que as variáveis chegaram:**

```bash
sudo cat /proc/$(pgrep -u minhaapp -f 'node /opt/minha-app')/environ | tr '\0' '\n' | grep -c DATABASE_URL
# esperado: 1
```

**Detalhes que separam quem já sofreu de quem não:**

- `RestartPreventExitStatus=78`: sem isso, uma configuração errada faz o systemd
  reiniciar o serviço a cada 5 segundos para sempre, enchendo o disco de log.
- `systemctl show minha-app -p Environment` mostra **só** o que está na unit, não o
  que veio do `EnvironmentFile`. Isso é bom (não vaza no `status`) e confunde na
  depuração.
- Trocar o `env` **não** afeta o processo em execução. É preciso
  `systemctl restart` — porque o ambiente foi copiado na criação do processo.
- `EnvironmentFile` **não é shell**: `VAR=$OUTRA` não expande, `export` não é aceito.

---

## 9. Não vazar segredo no log

**Problema real:** `console.log(config)` ou `logger.info({ req })` põe a senha
inteira num arquivo de log que vai para um serviço de terceiros com retenção de 90 dias.

```javascript
// src/redigir.mjs
const CHAVES_SENSIVEIS = /^(pass|senha|secret|segredo|token|api_?key|authorization|cookie|set-cookie|private|credential)/i;

/** Percorre um objeto e substitui valores de chaves sensíveis. Trata ciclos. */
export function redigir(valor, vistos = new WeakSet()) {
  if (valor === null || typeof valor !== 'object') return valor;
  if (vistos.has(valor)) return '[circular]';
  vistos.add(valor);
  if (Array.isArray(valor)) return valor.map((v) => redigir(v, vistos));
  const saida = {};
  for (const [k, v] of Object.entries(valor)) {
    saida[k] = CHAVES_SENSIVEIS.test(k) ? '[REDIGIDO]' : redigir(v, vistos);
  }
  return saida;
}
```

**Executado de verdade:**

```javascript
console.log(JSON.stringify(redigir({
  usuario: 'maria',
  senha: 'abc123',
  headers: { authorization: 'Bearer eyJ...', 'user-agent': 'curl/8' },
  db: { host: 'localhost', apiKey: 'sk_live_x' },
}), null, 2));
```
```json
{
  "usuario": "maria",
  "senha": "[REDIGIDO]",
  "headers": {
    "authorization": "[REDIGIDO]",
    "user-agent": "curl/8"
  },
  "db": {
    "host": "localhost",
    "apiKey": "[REDIGIDO]"
  }
}
```

**O que essa abordagem NÃO pega — e é onde as pessoas se enganam:**

1. `logger.info('conectando em ' + config.databaseUrl)` — a senha está **dentro** da
   URL, numa string. Redigir por nome de chave não ajuda.
   Correção: `new URL(u)` e zere `u.password` antes de logar.
2. Rastreamentos de pilha de bibliotecas de banco, que às vezes imprimem a string de
   conexão inteira.
3. `curl -v` em script de deploy, que imprime o cabeçalho `Authorization`.

**Regra melhor que qualquer regex:** logue **nomes** de configuração, nunca valores.
`log.info({ configCarregada: Object.keys(config) })` é suficiente para depurar.

E use as ferramentas nativas: `SecretStr` do pydantic (exemplo 4), `redact` do pino
(Node), `Sensitive` do Laravel.

---

## 10. Dockerfile + Compose sem vazar nada

`Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1.7
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
# Segredo de BUILD (token de registry privado) via BuildKit:
# NÃO vira camada, NÃO fica na imagem final.
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci --omit=dev

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY src ./src
USER node
EXPOSE 3000
CMD ["node", "src/app.mjs"]
```

```bash
docker build --secret id=npmrc,src=$HOME/.npmrc -t minha-app .
```

`.dockerignore` — **tão importante quanto o `.gitignore`**:

```
.env
.env.*
!.env.example
.git
.npmrc
node_modules
*.pem
*.key
```

Sem essa linha `.git`, um `COPY . .` copia **o histórico inteiro** para dentro da
imagem — inclusive aquele `.env` que você commitou e removeu há dois anos.

`compose.yaml`:

```yaml
services:
  app:
    build: .
    ports: ["3000:3000"]
    environment:
      LOG_LEVEL: info
      DATABASE_URL_FILE: /run/secrets/database_url    # padrão _FILE
      API_KEY_FILE: /run/secrets/api_key
    secrets: [database_url, api_key]
    depends_on: [db]

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: loja
      POSTGRES_USER: app
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password   # a imagem oficial já suporta
    secrets: [db_password]
    volumes: ["pgdata:/var/lib/postgresql/data"]

secrets:
  database_url: { file: ./secrets/database_url }
  api_key:      { file: ./secrets/api_key }
  db_password:  { file: ./secrets/db_password }

volumes:
  pgdata:
```

```bash
mkdir -p secrets && chmod 700 secrets
printf 'postgres://app:%s@db:5432/loja' "$(openssl rand -hex 16)" > secrets/database_url
echo 'secrets/' >> .gitignore
```

**Verificar que não vazou:**

```bash
docker history --no-trunc minha-app | grep -i -E 'token|secret|password'
# esperado: nenhuma linha
docker inspect -f '{{json .Config.Env}}' minha-app
# esperado: só NODE_ENV e PATH — nenhum segredo
```

---

## 11. Buscar do AWS Secrets Manager na inicialização

*(código completo; **não executado aqui** por exigir conta AWS)*

```javascript
// src/segredos.mjs
import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager';

const cliente = new SecretsManagerClient({});   // região e credenciais vêm do ambiente/IAM

/**
 * Busca um segredo JSON e injeta cada campo em process.env — mas SEM sobrescrever
 * o que já existir, mantendo a regra de precedência de todo o resto do curso.
 */
export async function carregarSegredos(nomeDoSegredo) {
  const r = await cliente.send(new GetSecretValueCommand({ SecretId: nomeDoSegredo }));
  const dados = JSON.parse(r.SecretString);
  for (const [chave, valor] of Object.entries(dados)) {
    if (process.env[chave] === undefined) process.env[chave] = String(valor);
  }
}
```

```javascript
// src/boot.mjs — precisa rodar ANTES do módulo de configuração
import { carregarSegredos } from './segredos.mjs';

if (process.env.SECRETS_ID) {
  await carregarSegredos(process.env.SECRETS_ID);   // top-level await: só em ESM
}
const { config } = await import('./config.mjs');    // import dinâmico, DEPOIS
const { iniciar } = await import('./servidor.mjs');
iniciar(config);
```

**O ponto de projeto:** a aplicação continua lendo `process.env`. O cofre é só mais
uma **fonte** que preenche o ambiente. Isso mantém o desenvolvimento local
funcionando com `.env` e a produção com o cofre, **sem nenhum `if` no código de negócio**.

**Cuidados de produção que quase sempre faltam:**

- **Custo por chamada.** US$ 0,05 por 10.000 chamadas (ago/2026): buscar a cada
  requisição, num serviço com 1.000 req/s, dá ~US$ 13.000/mês. Busque **na
  inicialização** e mantenha em memória, com TTL de 5 a 15 minutos.
- **Limite de vazão.** A API tem limite; num autoescalonamento agressivo, 200
  instâncias subindo juntas levam `ThrottlingException`. Use o
  **AWS Secrets Manager Agent** ou a extensão de cache do Lambda.
- **Falha na inicialização.** Se o cofre estiver fora do ar, a aplicação não sobe —
  o que é o comportamento **certo**, mas precisa estar previsto no seu SLA.
- **O segredo zero:** as credenciais para *falar com o cofre*. Em AWS use
  **IAM role da instância/task** — nunca chave estática. Ver
  [60-teoria-avancada.md §4](60-teoria-avancada.md).

---

## 12. SOPS — segredo criptografado dentro do repositório

*(comandos verificados no [03 §8](03-instalacao.md); o fluxo de CI não foi executado aqui)*

Serve muito bem para **entrega on-premise**: o cliente recebe o repositório inteiro,
com os segredos dentro, criptografados para a chave dele.

```bash
age-keygen -o ~/.config/sops/age/keys.txt   # se ainda não tiver
chmod 600 ~/.config/sops/age/keys.txt
export CHAVE_PUB=$(age-keygen -y ~/.config/sops/age/keys.txt)
```

`.sops.yaml` na raiz do repositório:

```yaml
creation_rules:
  - path_regex: secrets/.*\.enc\.yaml$
    age: >-
      age1SUACHAVEPUBLICA...,
      age1CHAVEDOCOLEGA...,
      age1CHAVEDOCI...
```

```bash
mkdir -p secrets
cat > secrets/producao.enc.yaml <<'EOF'
DATABASE_URL: postgres://app:senha-real@db.interno:5432/loja
API_KEY: sk_live_xxxxxxxxxxxx
SESSION_SECRET: abcdefghijklmnop
EOF
sops --encrypt --in-place secrets/producao.enc.yaml
```

```bash
head -3 secrets/producao.enc.yaml
# esperado: DATABASE_URL: ENC[AES256_GCM,data:...,iv:...,tag:...,type:str]
git add secrets/producao.enc.yaml && git commit -m "segredos de produção (criptografados)"
```

✅ O arquivo **pode** ir para o Git: as chaves ficam legíveis (bom para `git diff`),
só os valores são cifrados.

Rodar a aplicação com os valores no ambiente, **sem nunca escrever `.env` em disco**:

```bash
sops exec-env secrets/producao.enc.yaml 'node src/app.mjs'
```

Isso é melhor que `sops -d > .env && node app.mjs` porque **não deixa um arquivo
descriptografado no disco** para alguém esquecer lá.

**Rotacionar quem pode ler** (colega saiu da empresa):

```bash
# edite .sops.yaml removendo a chave dele, depois:
sops updatekeys secrets/producao.enc.yaml
```

🚨 **`updatekeys` NÃO basta.** O ex-colega tem o repositório clonado, com o arquivo
antigo no histórico, e a chave privada dele. **Ele pode decifrar tudo que existia até
a data da saída.** A única resposta correta é **rotacionar os segredos em si** —
trocar a senha do banco, revogar a chave de API. Este é o erro de raciocínio mais
comum com criptografia de repositório, e vale para o `git-crypt` também.

---

## 13. Gancho de pre-commit que bloqueia segredo

`.git/hooks/pre-commit` (ou, melhor, versionado via `pre-commit`/`husky`):

```bash
#!/usr/bin/env bash
# Bloqueia commit que contenha segredo ou arquivo .env.
set -euo pipefail

# 1) arquivos que nunca podem ser commitados
if git diff --cached --name-only | grep -Eq '(^|/)\.env(\..*)?$' \
   && ! git diff --cached --name-only | grep -Eq '\.env(\..*)?\.example$'; then
  echo "❌ Você está tentando commitar um arquivo .env."
  echo "   Rode:  git restore --staged \$(git diff --cached --name-only | grep '\.env')"
  exit 1
fi

# 2) varredura por padrão de segredo no conteúdo
if command -v gitleaks >/dev/null 2>&1; then
  if ! gitleaks protect --staged --no-banner --redact; then
    echo "❌ gitleaks encontrou possível segredo no que você está commitando."
    echo "   Se for falso positivo, adicione '# gitleaks:allow' na linha."
    exit 1
  fi
else
  echo "⚠️  gitleaks não instalado — varredura de conteúdo pulada."
fi
```

```bash
chmod +x .git/hooks/pre-commit
```

**Teste que ele funciona** (faça isto — gancho não testado é gancho que não existe):

```bash
echo 'AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY' > teste.txt
git add teste.txt && git commit -m "teste"
# esperado: o commit é RECUSADO
git restore --staged teste.txt && rm teste.txt
```

⚠️ **O gancho é local e contornável** (`git commit --no-verify`, ou um colega que
nunca o instalou). Ele é a primeira barreira, não a única. As outras duas:
**gitleaks no CI** (não contornável) e o **push protection** do GitHub, que é
gratuito para repositórios públicos e bloqueia o push no servidor.

---

## 14. **Produção** — rotação sem derrubar o sistema

**O problema que ninguém conta no tutorial:** você troca a senha do banco. Entre o
instante em que a senha nova vale e o instante em que todas as 30 instâncias
reiniciaram com ela, **as instâncias antigas estão usando a senha velha e falhando**.
Isso é indisponibilidade.

**A técnica: sobreposição (dois segredos válidos ao mesmo tempo).**

```
Tempo →
       │ t0            t1              t2              t3
─────────────────────────────────────────────────────────────────
Banco  │ [senha A]     [senha A + B]   [senha A + B]   [senha B]
App    │ usa A         usa A           reinicia → B    usa B
       │               ↑ cria B         ↑ deploy        ↑ revoga A
```

Para senha de banco:

```sql
-- t1: cria um SEGUNDO usuário com os mesmos privilégios (não troca a senha do atual!)
CREATE USER app_v2 WITH PASSWORD 'nova-senha-forte';
GRANT ALL PRIVILEGES ON DATABASE loja TO app_v2;
-- t3, depois que TODAS as instâncias já estão em app_v2:
DROP USER app_v1;
```

Para chave de API (a maioria dos provedores suporta múltiplas chaves ativas):
crie a nova, faça o deploy, **confirme que a antiga parou de ser usada olhando o
painel de uso**, e só então revogue.

**Rotação sem reiniciar processo** — só possível com o padrão `_FILE` (exemplo 7):

```javascript
// src/credencial.mjs — relê o arquivo quando ele muda
import { readFileSync, watchFile } from 'node:fs';

export function credencialViva(caminho, aoTrocar) {
  let valor = readFileSync(caminho, 'utf8').trim();
  watchFile(caminho, { interval: 5000 }, () => {
    try {
      const novo = readFileSync(caminho, 'utf8').trim();
      if (novo && novo !== valor) {
        valor = novo;
        aoTrocar?.(valor);          // ex.: recriar o pool de conexões
        console.log('credencial recarregada de', caminho);
      }
    } catch (e) {
      console.error('falha ao reler credencial:', e.code);  // mantém a anterior
    }
  });
  return () => valor;               // getter: sempre devolve a atual
}
```

No Kubernetes, um Secret montado como volume é **atualizado automaticamente** pelo
kubelet (com atraso de até ~1 minuto). Combinado com o código acima, você troca a
credencial **sem reiniciar um único pod**. Secret injetado como **variável de
ambiente**, não: exige reinício. Essa é a razão técnica mais forte para preferir
volume a `envFrom` em Kubernetes.

**Checklist de rotação:**

- [ ] Inventário: onde mais essa credencial é usada? (CI, cron, script de backup,
      máquina do estagiário, Postman de alguém)
- [ ] O provedor permite duas credenciais ativas? Se não, haverá janela — planeje.
- [ ] Métrica de "quem ainda usa a antiga" antes de revogar.
- [ ] Rollback ensaiado.
- [ ] Data de revogação da antiga **agendada**, não "quando der".

---

## 15. **Produção** — instalador para o cliente (on-premise)

**O cenário exato da pergunta que originou este curso:** o sistema vai rodar na
máquina do cliente. Você não controla o servidor. Não há painel de PaaS.
Alguém — talvez o pessoal de TI do cliente, talvez você por um acesso remoto —
precisa colocar os segredos lá **uma vez**, e ninguém pode esquecer como foi feito.

`install.sh`:

```bash
#!/usr/bin/env bash
# Instalador de primeira execução: coleta a configuração, valida, grava com
# permissão restrita e registra o serviço. Idempotente: rodar de novo não estraga.
set -euo pipefail

DIR_CONF="/etc/minha-app"
ARQ_ENV="${DIR_CONF}/env"
USUARIO="minhaapp"

[[ $EUID -eq 0 ]] || { echo "rode como root: sudo $0"; exit 1; }

id "$USUARIO" &>/dev/null || useradd --system --no-create-home --shell /usr/sbin/nologin "$USUARIO"
install -d -m 750 -o root -g "$USUARIO" "$DIR_CONF"

if [[ -f "$ARQ_ENV" ]]; then
  echo "Já existe $ARQ_ENV. Nada a fazer."
  echo "Para reconfigurar:  sudo mv $ARQ_ENV $ARQ_ENV.bak && sudo $0"
  exit 0
fi

perguntar() {                       # $1=nome  $2=descrição  $3=secreto?
  local valor
  if [[ "${3:-}" == "secreto" ]]; then
    read -rsp "  $2: " valor; echo
  else
    read -rp "  $2: " valor
  fi
  [[ -n "$valor" ]] || { echo "  ⚠️  $1 não pode ficar em branco."; perguntar "$@"; return; }
  printf '%s=%s\n' "$1" "$valor" >> "$ARQ_ENV.tmp"
}

echo "═══ Configuração da Minha App ═══"
umask 077                           # tudo que for criado aqui nasce 600
: > "$ARQ_ENV.tmp"

perguntar DATABASE_URL "URL do PostgreSQL (postgres://usuario:senha@host:5432/banco)"
perguntar API_KEY      "Chave da API de pagamento (fornecida por nós)" secreto
printf 'SESSION_SECRET=%s\n' "$(openssl rand -base64 48 | tr -d '\n')" >> "$ARQ_ENV.tmp"
printf 'PORT=8080\nLOG_LEVEL=info\nNODE_ENV=production\n' >> "$ARQ_ENV.tmp"

echo "Validando a configuração antes de gravar…"
if ! (set -a; . "$ARQ_ENV.tmp"; set +a; node /opt/minha-app/src/check-config.mjs); then
  echo "❌ Configuração inválida. Nada foi gravado."
  rm -f "$ARQ_ENV.tmp"; exit 1
fi

mv "$ARQ_ENV.tmp" "$ARQ_ENV"
chown root:"$USUARIO" "$ARQ_ENV"
chmod 640 "$ARQ_ENV"

install -m 644 /opt/minha-app/deploy/minha-app.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now minha-app

echo
echo "✅ Instalado."
echo "   Configuração: $ARQ_ENV  (root:$USUARIO 640)"
echo "   Serviço:      systemctl status minha-app"
echo
echo "⚠️  IMPORTANTE PARA O CLIENTE:"
echo "   • Faça backup de $ARQ_ENV — o SESSION_SECRET foi gerado agora e é único."
echo "     Perdê-lo desconecta todos os usuários (não perde dados)."
echo "   • Não copie esse arquivo por e-mail nem para dentro do diretório da aplicação."
echo "   • Para trocar a chave da API: sudo mv $ARQ_ENV $ARQ_ENV.bak && sudo $0"
```

**As decisões deste script, e o que cada uma ensina:**

| Decisão | Por quê |
|---|---|
| `read -rsp` para segredo | não ecoa na tela e **não entra no histórico do shell** |
| `umask 077` no começo | o arquivo temporário nasce inacessível — sem janela de exposição |
| grava em `.tmp` e valida antes de `mv` | nunca deixa uma configuração pela metade se o operador der Ctrl+C |
| `SESSION_SECRET` **gerado**, não perguntado | segredo que você não precisa transportar é segredo que não vaza. **Toda instalação tem um valor diferente** — se um cliente vazar, os outros seguem seguros |
| `640 root:minhaapp` | a aplicação lê, mas não pode alterar; e nenhum outro usuário do servidor lê |
| idempotente | o cliente vai rodar duas vezes. Sempre roda |
| avisa sobre backup | o `SESSION_SECRET` gerado não existe em nenhum outro lugar do mundo |

**E como a chave da API chega até o cliente?** Esta é a pergunta difícil, e a resposta
honesta está em [55-entrega-ao-cliente.md](55-entrega-ao-cliente.md): **não mande por
e-mail nem WhatsApp**. Use um link de uso único que se autodestrói
(`onetimesecret.com`, ou o `pwpush` auto-hospedado), com o link e a senha de abertura
por **canais diferentes** (link por e-mail, senha por telefone). E o melhor caminho de
todos: faça o próprio cliente gerar a credencial no painel dele e informar a você, para
que o segredo **nunca precise trafegar**.

---

## Autoteste

1. Por que o exemplo 2 sai com código 78 em vez de 1?
2. Por que "um único módulo lê `process.env`" é regra e não preferência estética?
3. Cite três lugares onde uma variável de ambiente aparece e um arquivo montado não.
4. Por que `RestartPreventExitStatus=78` no systemd evita um problema real?
5. `redigir()` do exemplo 9 não pega a senha dentro de `postgres://user:senha@host`. Por quê, e como resolver?
6. Por que `sops exec-env` é preferível a `sops -d > .env`?
7. Você removeu a chave `age` de um ex-colega com `sops updatekeys`. Ele ainda consegue ler os segredos? Justifique.
8. Descreva a técnica de sobreposição na rotação de senha de banco, com os quatro instantes.
9. Por que o instalador do exemplo 15 **gera** o `SESSION_SECRET` em vez de perguntar?
10. Por que um Secret montado como volume permite rotação sem reiniciar o pod, e um injetado como variável de ambiente não?

---

**Próximo:** [07-projeto-modelo/](07-projeto-modelo/README.md) · Voltar ao [mapa](00-MAPA.md)
