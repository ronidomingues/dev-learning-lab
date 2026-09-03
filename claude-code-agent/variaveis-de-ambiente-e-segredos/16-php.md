# 16 · PHP — do `.env` à produção

`Nível: intermediário` · `Atualizado em: 14/08/2026`
`Base: PHP 8.1.2 (Ubuntu 22.04.5) — medições verificadas nesta máquina`

PHP é a linguagem com **mais armadilhas específicas** neste assunto, por três motivos
que nenhuma outra tem: o modelo de execução por requisição, a divergência entre
`getenv()` e `$_ENV`, e a hospedagem compartilhada. Este arquivo trata dos três.

---

## 1. A armadilha nº 1: `getenv()` ≠ `$_ENV`

**Medido nesta máquina, agora:**

```bash
php -r 'var_dump(ini_get("variables_order"));'
```
```
string(4) "GPCS"
```

```bash
FOO=bar php -r 'var_dump($_ENV["FOO"] ?? "AUSENTE em \$_ENV"); var_dump(getenv("FOO"));'
```
```
string(16) "AUSENTE em $_ENV"
string(3) "bar"
```

**Leia de novo.** A variável `FOO` **existe** no ambiente do processo. `getenv("FOO")`
a devolve. `$_ENV["FOO"]` **não existe**.

### Por quê

A diretiva `variables_order` do `php.ini` diz quais superglobais o PHP monta:

| Letra | Superglobal |
|---|---|
| `E` | `$_ENV` |
| `G` | `$_GET` |
| `P` | `$_POST` |
| `C` | `$_COOKIE` |
| `S` | `$_SERVER` |

O padrão recomendado pela distribuição — e o desta máquina — é **`GPCS`**:
**sem o `E`**. Logo, `$_ENV` nasce vazio, por decisão de desempenho (evitar copiar
o ambiente inteiro a cada requisição).

### O que isso causa na vida real

```php
// ❌ funciona na máquina do desenvolvedor (php.ini com E), quebra no servidor
$senha = $_ENV['DB_PASSWORD'];
```

E o pior: **quebra em silêncio**, devolvendo `null`, que vira string vazia, que vira
uma tentativa de conexão com senha em branco.

### A regra

```php
// ✅ funciona em qualquer configuração
$senha = getenv('DB_PASSWORD');
if ($senha === false || $senha === '') {
    throw new RuntimeException('DB_PASSWORD ausente');
}
```

`getenv()` lê direto do ambiente do processo, sem depender de `variables_order`.
É o que o [projeto-modelo](07-projeto-modelo/equivalentes/config.php) usa.

> ⚠️ **Complicação adicional:** o `phpdotenv` com `createImmutable()` popula
> `$_ENV` **e** `$_SERVER` **e** `getenv()`. Então, num projeto com `phpdotenv`,
> `$_ENV` funciona — em desenvolvimento. Em produção, sem `.env`, com as variáveis
> vindo do PHP-FPM, `$_ENV` volta a estar vazio. **É exatamente a combinação que
> produz "funciona em dev, quebra em produção".**

### Complicação nº 2: `getenv()` e thread-safety

Em SAPIs multithread (ZTS: Apache com `mpm_worker`, ou o antigo `php-cgi`), a
documentação do PHP alerta que `getenv()`/`putenv()` não são thread-safe. Na prática,
PHP-FPM (que é multiprocesso, não multithread) não sofre disso, e é o que
praticamente todo mundo usa hoje. Se você está num Apache com `mpm_worker` + `mod_php`,
é mais um motivo para migrar para PHP-FPM.

---

## 2. A armadilha nº 2: o modelo por requisição

Node e Python carregam a configuração **uma vez** e servem milhares de requisições.
PHP, no modelo clássico, **reinicia a cada requisição**.

```
Node:   [inicia] → valida config → [req][req][req][req]…  (config validada 1×)
PHP:    [req: inicia → lê .env → valida → responde → morre]
        [req: inicia → lê .env → valida → responde → morre]
        [req: inicia → lê .env → valida → responde → morre]
```

Consequências:

| Consequência | Impacto |
|---|---|
| O `.env` é **lido do disco a cada requisição** | I/O desnecessário; mensurável sob carga |
| Validação de configuração roda a cada requisição | desperdício |
| `exit(78)` não vira código de saída de processo | vira **página em branco** ou erro 500 |
| "Falha rápida na inicialização" não existe | precisa de outro mecanismo |

### A solução: valide no deploy, não na requisição

```php
// bin/check-config.php — roda no deploy, no CI, no instalador. NUNCA em requisição.
#!/usr/bin/env php
<?php
declare(strict_types=1);
require __DIR__ . '/../vendor/autoload.php';

[$config, $problemas] = criar_config();

if ($problemas) {
    fwrite(STDERR, "❌ Configuração inválida:\n");
    foreach ($problemas as $p) fwrite(STDERR, "   • {$p}\n");
    exit(78);
}
echo "✅ Configuração válida.\n";
```

```bash
# no deploy — o pipeline PARA aqui se a configuração estiver errada
php bin/check-config.php || exit 1
```

Esta é a diferença de projeto mais importante entre PHP e as outras linguagens do
curso, e quase nenhum tutorial menciona.

### E se você usa FrankenPHP, RoadRunner, Swoole ou Laravel Octane?

Aí o PHP passa a ter processo de longa duração, e o modelo fica igual ao do Node:
a configuração é carregada **uma vez**, na inicialização do worker. Duas consequências:

- ✅ a falha rápida volta a funcionar, e você **deve** usá-la;
- ⚠️ **trocar o `.env` não tem mais efeito imediato** — é preciso reiniciar os
  workers. Quem vem do PHP clássico se surpreende com isso.

---

## 3. `phpdotenv` — uso correto

```bash
composer require vlucas/phpdotenv
```

Versão atual da linha 5.6 em ago/2026: **v5.6.3** (27/12/2025), com suporte oficial
a PHP 8.5. Exige PHP ≥ 7.2.5.

```php
<?php
require __DIR__ . '/vendor/autoload.php';

// createImmutable: NÃO sobrescreve variável já existente no ambiente.
// É o comportamento certo — o ambiente de produção vence o arquivo.
$dotenv = Dotenv\Dotenv::createImmutable(__DIR__);

// safeLoad(): não explode se o .env não existir.
// ESTE É O PONTO. Em produção não há .env, e a aplicação precisa subir mesmo assim.
$dotenv->safeLoad();
```

| Método | Comportamento | Quando usar |
|---|---|---|
| `createImmutable()` | não sobrescreve o ambiente | **sempre** |
| `createMutable()` | sobrescreve | praticamente nunca — um `.env` esquecido derruba a produção |
| `createUnsafeImmutable()` | também popula `getenv()` | quando código legado usa `getenv()` |
| `load()` | **exceção** se faltar o arquivo | só em desenvolvimento |
| `safeLoad()` | silencioso se faltar | **produção** |

Validação embutida, que quase ninguém usa e deveria:

```php
$dotenv->required(['DATABASE_URL', 'API_KEY'])->notEmpty();
$dotenv->required('PORT')->isInteger();
$dotenv->required('LOG_LEVEL')->allowedValues(['debug', 'info', 'warn', 'error']);
$dotenv->ifPresent('SENTRY_DSN')->notEmpty();
```

⚠️ Isso lança na **primeira** falha, não lista todas. Para o relatório completo,
use o acumulador do [projeto-modelo](07-projeto-modelo/equivalentes/config.php).

### Migração da versão 4 para a 5

Mudou o comportamento de `$_ENV`/`getenv()` e a API de criação. Se você herdou um
projeto com `phpdotenv` 4, leia o `UPGRADING.md` do projeto antes de atualizar —
a quebra é **silenciosa**, não é erro de sintaxe.

---

## 4. Laravel

### O essencial

```php
// ❌ NUNCA fora de config/*.php
$chave = env('STRIPE_SECRET');

// ✅ config/services.php
return ['stripe' => ['secret' => env('STRIPE_SECRET')]];

// ✅ no resto da aplicação
$chave = config('services.stripe.secret');
```

**Por que essa regra existe, e é a mais importante do Laravel neste assunto:**

```bash
php artisan config:cache
```

Esse comando — **obrigatório em produção**, por desempenho — serializa toda a
configuração em `bootstrap/cache/config.php` e faz o Laravel **parar de ler o `.env`
completamente**. A função `env()` passa a devolver `null` em qualquer lugar que não
seja um arquivo de `config/`.

Resultado clássico: a aplicação funciona em desenvolvimento, o deploy roda
`config:cache`, e a integração de pagamento passa a receber `null` como chave.
O erro aparece **só no primeiro pagamento real**, horas depois.

### Checklist de produção Laravel

```bash
php artisan config:cache     # obrigatório; e reexecute a cada troca de .env
php artisan route:cache
php artisan view:cache
php artisan config:clear     # em desenvolvimento, se o cache atrapalhar
```

| Item | Valor em produção | Se errar |
|---|---|---|
| `APP_DEBUG` | **`false`** | a página de erro do Whoops mostra **todo o ambiente**, com senhas, para qualquer visitante. É o vazamento mais comum de Laravel |
| `APP_ENV` | `production` | telas de debug e ferramentas de dev habilitadas |
| `APP_KEY` | gerado com `php artisan key:generate` | sessões e dados criptografados ilegíveis; trocá-lo invalida tudo que foi cifrado |
| `.env` | fora do `public/` | ver §6 |
| `bootstrap/cache/config.php` | **contém os segredos em texto** | `chmod 640`, dono correto, e **fora do repositório** |

> 🚨 **`APP_DEBUG=true` em produção é a falha nº 1 de Laravel.** A tela de erro do
> Ignition/Whoops lista as variáveis de ambiente da requisição. Um erro qualquer numa
> rota pública entrega o `.env` inteiro. Existem varredores automatizados na internet
> procurando exatamente isso.

### Laravel e o mundo real

Laravel espera `.env` no servidor — é o design dele. Isso é aceitável desde que:

- o arquivo esteja **fora** do diretório servido pelo servidor web;
- tenha `chmod 640`, dono `root`, grupo do usuário do PHP-FPM;
- **não** seja o único mecanismo em ambientes com mais de um servidor —
  aí use variáveis do PHP-FPM (§5) ou um cofre com `config:cache` no deploy.

---

## 5. Servir PHP em produção: onde as variáveis entram de verdade

### PHP-FPM (o caminho recomendado)

```ini
; /etc/php/8.3/fpm/pool.d/minha-app.conf
[minha-app]
user = minhaapp
group = minhaapp
listen = /run/php/minha-app.sock

; Configuração NÃO secreta
env[APP_ENV] = production
env[APP_DEBUG] = false

; ⚠️ Segredo aqui fica legível por quem lê este arquivo. chmod 640 nele.
env[DATABASE_URL] = "postgres://app:senha@db/loja"

; Alternativa melhor: use systemd para injetar no processo-mestre do FPM,
; e aqui só repasse o nome (sem "=" repassa do ambiente do FPM):
env[API_KEY] = $API_KEY
```

```bash
sudo chmod 640 /etc/php/8.3/fpm/pool.d/minha-app.conf
sudo systemctl restart php8.3-fpm
```

⚠️ **`clear_env`**: por padrão o PHP-FPM **limpa** o ambiente herdado
(`clear_env = yes`), justamente para o processo do site não enxergar o ambiente do
sistema. Se você injetou variáveis pelo systemd e elas "somem", é isto.
Colocar `clear_env = no` funciona — e **expõe todo o ambiente do FPM a todos os
pools**, o que em servidor com vários sites é ruim. Prefira `env[NOME] = $NOME`,
que repassa só o que você listar.

### Apache + `mod_php`

```apache
<VirtualHost *:80>
    SetEnv APP_ENV production
    # ⚠️ NÃO ponha segredo aqui: o arquivo costuma ser 644 e legível por todos
</VirtualHost>
```

Ou, via `.htaccess`:

```apache
SetEnv APP_ENV production
```

🚨 **`.htaccess` com segredo é perigoso**: ele fica **dentro** do diretório servido.
Uma configuração errada do servidor pode entregá-lo como texto. Já aconteceu muito.

### Hospedagem compartilhada (cPanel, Locaweb, HostGator…)

O cenário mais frequente da pergunta original no Brasil, e o mais desconfortável:

- você **não** controla o `php.ini` nem o pool do FPM;
- **outros clientes** rodam no mesmo servidor;
- muitas vezes não há acesso SSH.

O que dá para fazer, em ordem de preferência:

1. **Painel do provedor**: cPanel tem "Variáveis de ambiente" em alguns planos, ou o
   `.htaccess` do MultiPHP. Use se existir.
2. **`.env` fora do `public_html`**:
   ```
   /home/usuario/
     ├── config/.env          ← 600, FORA da web
     └── public_html/
         └── index.php        ← Dotenv::createImmutable('/home/usuario/config')
   ```
3. **Aceite o risco e documente.** Em hospedagem compartilhada, o
   administrador do provedor lê tudo, sempre. Isso não é falha sua — é o modelo do
   produto. Se o dado for sensível de verdade, **hospedagem compartilhada é a
   decisão errada**, não a configuração.

⚠️ Verifique se `open_basedir` está ativo (`php -i | grep open_basedir`). Se não
estiver, um script PHP de **outro cliente** do servidor pode ler o seu `.env`.

---

## 6. O erro que derruba empresa: `.env` acessível pela web

Se o `.env` estiver dentro do diretório servido, e o servidor não estiver
configurado para bloqueá-lo:

```
https://seusite.com.br/.env
```

…devolve o arquivo. Existem varredores automatizados que testam esse caminho em
faixas inteiras de IP, o dia inteiro.

**Teste agora, no seu site:**

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://seusite.com.br/.env
# esperado: 403 ou 404.  Se vier 200, você tem um incidente EM CURSO.
```

Bloqueio no nginx:

```nginx
location ~ /\.(env|git|htaccess) {
    deny all;
    return 404;
}
```

Apache:

```apache
<FilesMatch "^\.env">
    Require all denied
</FilesMatch>
```

**Mas a correção de verdade é estrutural:** o `.env` não deve estar em diretório
servido. A raiz da web deve ser `public/`, e o `.env` um nível acima. Framework
moderno (Laravel, Symfony) já faz isso; código legado quase nunca.

E se veio 200: [50-vazamentos-e-resposta.md](50-vazamentos-e-resposta.md), agora.

---

## 7. Symfony

Symfony tem o modelo mais bem resolvido dos frameworks PHP:

```bash
# .env — versionado, SÓ com valores padrão não secretos
APP_ENV=prod
DATABASE_URL="postgresql://app:!ChangeMe!@127.0.0.1:5432/app"
```

```bash
# .env.local — NÃO versionado, valores reais da máquina
DATABASE_URL="postgresql://app:senha-real@db.interno:5432/loja"
```

Precedência (do mais forte ao mais fraco): ambiente real → `.env.local.php` →
`.env.$APP_ENV.local` → `.env.local` → `.env.$APP_ENV` → `.env`.

Em produção:

```bash
composer dump-env prod
```

Isso compila tudo em `.env.local.php` — um array PHP puro, sem parsing a cada
requisição. É o equivalente ao `config:cache` do Laravel, e tem a **mesma pegadinha**:
o arquivo gerado **contém os segredos em texto**, precisa de permissão restrita e não
pode ir para o repositório.

### O cofre nativo do Symfony

```bash
php bin/console secrets:generate-keys
php bin/console secrets:set DATABASE_PASSWORD
php bin/console secrets:set --local DATABASE_PASSWORD   # valor de dev
```

Os segredos cifrados ficam em `config/secrets/prod/` e **podem ser versionados**; a
chave de decifração (`prod.decrypt.private.php`) **não**. É SOPS embutido no
framework, e funciona bem. Mesma limitação de todos os esquemas assim: a chave
privada ainda precisa chegar ao servidor por algum caminho — o
[problema do segredo zero](60-teoria-avancada.md).

---

## 8. Receituário PHP

| Situação | Faça |
|---|---|
| Ler variável | **`getenv()`**, nunca `$_ENV` direto |
| Carregar `.env` em dev | `createImmutable()` + `safeLoad()` |
| Validar configuração | script no **deploy**, não na requisição |
| Laravel | tudo em `config/*.php` + `config:cache`; `APP_DEBUG=false` |
| Symfony | `.env.local` + `composer dump-env prod`, ou o cofre nativo |
| Servidor próprio | PHP-FPM com `env[]` no pool, arquivo `640` |
| Hospedagem compartilhada | `.env` fora do `public_html`, `600`; e saiba o que você não controla |
| Verificação obrigatória | `curl https://seusite/.env` deve dar 403/404 |
| Segredo grande (chave PEM) | arquivo montado + padrão `_FILE`, nunca variável |

---

## Autoteste

1. Por que `$_ENV['FOO']` pode estar vazio enquanto `getenv('FOO')` funciona? Qual diretiva controla isso?
2. Por que `exit(78)` não serve como falha rápida numa aplicação web PHP? O que fazer no lugar?
3. Por que `env()` fora de `config/` quebra no Laravel depois de `config:cache`?
4. Qual é o efeito de `APP_DEBUG=true` em produção, e por que ele é catastrófico?
5. O que `clear_env` faz no PHP-FPM, e por que `clear_env = no` é uma correção ruim?
6. Como você testa, em um comando, se o seu `.env` está exposto na web?
7. Em hospedagem compartilhada, o que `open_basedir` protege?
8. O que `composer dump-env prod` gera, e que cuidado esse arquivo exige?
9. Por que FrankenPHP/Octane muda o raciocínio sobre carregamento de configuração?
10. Qual a diferença entre `createImmutable` e `createMutable`, e por que a segunda é perigosa?

---

**Medido nesta máquina em 14/08/2026:** PHP 8.1.2, `variables_order = GPCS`,
`$_ENV` vazio com variável presente no ambiente e `getenv()` funcionando.
**Não executado aqui:** Composer, `phpdotenv`, Laravel, Symfony, PHP-FPM
(o Composer não está instalado nesta máquina) — esse conteúdo vem da documentação
oficial de cada projeto, consultada em 14/08/2026.

**Próximo:** [17-python.md](17-python.md) · Voltar ao [mapa](00-MAPA.md)
