<?php
/**
 * config.php — o MESMO contrato do src/config.mjs, em PHP, sem framework
 * e sem nenhuma dependência do Composer.
 *
 * Detalhe crítico do PHP, que não existe em Node nem em Python:
 * `getenv()` e `$_ENV` NÃO são equivalentes. `$_ENV` só é preenchido se a
 * diretiva `variables_order` do php.ini incluir a letra "E", e o padrão de
 * muitas distribuições é "GPCS" — sem o E. Por isso este arquivo usa
 * `getenv()`, que funciona em qualquer configuração. Ver ../../16-php.md.
 *
 * Rode:
 *   php equivalentes/config.php
 *   DATABASE_URL=memory://x SESSION_SECRET=... API_KEY=... php equivalentes/config.php
 */
declare(strict_types=1);

const SEGREDO_DE_EXEMPLO = 'desenvolvimento-apenas-troque-isto-em-producao';
const CHAVES_SECRETAS = ['session_secret', 'api_key', 'database_url'];

final class Validadores
{
    public static function url(string ...$esquemas): callable
    {
        return function (string $valor) use ($esquemas): ?string {
            $partes = parse_url($valor);
            if ($partes === false || empty($partes['scheme']) || empty($partes['host'])) {
                return 'não é uma URL válida';
            }
            if ($esquemas && !in_array($partes['scheme'], $esquemas, true)) {
                return 'esquema deve ser um de ' . implode(', ', $esquemas) . " (veio \"{$partes['scheme']}\")";
            }
            return null;
        };
    }

    public static function inteiro(int $min, int $max): callable
    {
        return fn(string $v): ?string =>
            (ctype_digit($v) && (int) $v >= $min && (int) $v <= $max)
                ? null : "esperado inteiro entre {$min} e {$max}";
    }

    public static function umDe(string ...$opcoes): callable
    {
        return fn(string $v): ?string =>
            in_array($v, $opcoes, true) ? null : 'esperado um de ' . implode(', ', $opcoes);
    }

    public static function minimo(int $n): callable
    {
        return fn(string $v): ?string =>
            strlen($v) >= $n ? null : "precisa ter ao menos {$n} caracteres (tem " . strlen($v) . ')';
    }

    public static function booleano(string $v): ?string
    {
        return in_array($v, ['true', 'false'], true) ? null : 'esperado "true" ou "false"';
    }
}

final class Configuracao
{
    /** @var string[] */
    public array $problemas = [];
    private array $env;

    public function __construct(?array $env = null)
    {
        // getenv() sem argumento devolve TODO o ambiente — funciona mesmo sem "E"
        // em variables_order.
        $this->env = $env ?? getenv();
    }

    private function ler(string $nome): ?string
    {
        $caminho = $this->env[$nome . '_FILE'] ?? null;
        if ($caminho !== null && $caminho !== '') {
            $conteudo = @file_get_contents($caminho);
            if ($conteudo === false) {
                $this->problemas[] = "{$nome}_FILE aponta para \"{$caminho}\", que não pôde ser lido";
                return null;
            }
            return trim($conteudo);
        }
        $valor = $this->env[$nome] ?? null;
        return ($valor === null || $valor === '') ? null : $valor;   // "" conta como ausente
    }

    public function exigido(string $nome, ?callable $validar = null): ?string
    {
        $v = $this->ler($nome);
        if ($v === null) {
            $this->problemas[] = "falta {$nome}";
            return null;
        }
        if ($validar && ($msg = $validar($v)) !== null) {
            $this->problemas[] = "{$nome}: {$msg}";
            return null;
        }
        return $v;
    }

    public function opcional(string $nome, string $padrao, ?callable $validar = null): string
    {
        $v = $this->ler($nome);
        if ($v === null) return $padrao;
        if ($validar && ($msg = $validar($v)) !== null) {
            $this->problemas[] = "{$nome}: {$msg}";
            return $padrao;
        }
        return $v;
    }

    public static function mascarar(?string $valor): ?string
    {
        if ($valor === null || $valor === '') return $valor;
        $n = strlen($valor);
        if ($n <= 8) return '********';
        return substr($valor, 0, 3) . '…' . substr($valor, -2) . " ({$n} chars)";
    }

    /** postgres://app:senha@host/db → postgres://app:***@host/db */
    public static function redigirUrl(?string $texto): ?string
    {
        if ($texto === null) return null;
        $p = parse_url($texto);
        if ($p === false || empty($p['pass'])) return $texto;
        return str_replace(':' . $p['pass'] . '@', ':***@', $texto);
    }
}

/** @return array{0: array, 1: string[]} */
function criar_config(?array $env = null): array
{
    $c = new Configuracao($env);

    $ambiente = $c->opcional('NODE_ENV', 'development', Validadores::umDe('development', 'test', 'production'));
    $bruta = [
        'ambiente'       => $ambiente,
        'porta'          => $c->opcional('PORT', '3000', Validadores::inteiro(1, 65535)),
        'log_level'      => $c->opcional('LOG_LEVEL', 'info', Validadores::umDe('debug', 'info', 'warn', 'error')),
        'database_url'   => $c->exigido('DATABASE_URL', Validadores::url('postgres', 'postgresql', 'memory')),
        'session_secret' => $c->exigido('SESSION_SECRET', Validadores::minimo(32)),
        'api_key'        => $c->exigido('API_KEY', Validadores::minimo(8)),
        'max_recados'    => $c->opcional('MAX_RECADOS', '100', Validadores::inteiro(1, 100000)),
        'expor_metricas' => $c->opcional('EXPOR_METRICAS', 'false', 'Validadores::booleano'),
    ];

    if ($ambiente === 'production') {
        if ($bruta['session_secret'] === SEGREDO_DE_EXEMPLO) {
            $c->problemas[] = 'SESSION_SECRET: o valor de exemplo não pode ser usado com NODE_ENV=production';
        }
        if (str_starts_with($bruta['api_key'] ?? '', 'sk_test_')) {
            $c->problemas[] = 'API_KEY: chave de teste (sk_test_…) com NODE_ENV=production';
        }
        if (str_starts_with($bruta['database_url'] ?? '', 'memory:')) {
            $c->problemas[] = 'DATABASE_URL: banco em memória com NODE_ENV=production perde tudo a cada reinício';
        }
    }

    $config = [
        'ambiente'       => $bruta['ambiente'],
        'porta'          => (int) $bruta['porta'],
        'log_level'      => $bruta['log_level'],
        'database_url'   => $bruta['database_url'],
        'session_secret' => $bruta['session_secret'],
        'api_key'        => $bruta['api_key'],
        'max_recados'    => (int) $bruta['max_recados'],
        'expor_metricas' => $bruta['expor_metricas'] === 'true',
    ];

    return [$config, $c->problemas];
}

function config_para_log(array $config): array
{
    $saida = [];
    foreach ($config as $chave => $valor) {
        $saida[$chave] = in_array($chave, CHAVES_SECRETAS, true) && is_string($valor)
            ? Configuracao::mascarar($valor)
            : $valor;
    }
    return $saida;
}

// ── executável quando chamado direto pela CLI ──────────────────────────────
if (PHP_SAPI === 'cli' && isset($argv[0]) && realpath($argv[0]) === realpath(__FILE__)) {
    [$config, $problemas] = criar_config();

    if ($problemas) {
        fwrite(STDERR, "\n❌ Configuração inválida:\n");
        foreach ($problemas as $p) fwrite(STDERR, "   • {$p}\n");
        fwrite(STDERR, "\nConsulte .env.example para a lista completa de variáveis.\n\n");
        exit(78); // EX_CONFIG
    }

    echo "✅ Configuração válida.\n\n";
    $visao = config_para_log($config);
    $visao['database_url'] = Configuracao::redigirUrl($config['database_url']);
    foreach ($visao as $chave => $valor) {
        printf("   %-16s %s\n", $chave, is_bool($valor) ? var_export($valor, true) : (string) $valor);
    }
    echo "\n";
}
