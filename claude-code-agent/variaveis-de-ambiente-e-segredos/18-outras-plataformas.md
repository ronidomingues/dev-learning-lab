# 18 · Java, .NET, Go, Ruby, Rust e as demais

`Nível: intermediário` · `Atualizado em: 14/08/2026`

O mecanismo é do sistema operacional, então a resposta é a mesma em toda linguagem.
O que muda é o **idioma local**: como cada ecossistema prefere ler, validar e tipar.
Este arquivo é referência de consulta — vá direto à sua.

> ⚠️ Nenhum exemplo deste arquivo foi executado nesta máquina (só Node, Python e PHP
> estão instalados). O conteúdo vem da documentação oficial de cada plataforma,
> consultada em 14/08/2026.

---

## 1. Java / Spring Boot

### Java puro

```java
String url = System.getenv("DATABASE_URL");           // null se não existir
Map<String, String> tudo = System.getenv();           // imutável

// falha rápida
String obrigatoria = Optional.ofNullable(System.getenv("DATABASE_URL"))
    .orElseThrow(() -> new IllegalStateException("falta DATABASE_URL"));
```

⚠️ **Java não permite alterar o próprio ambiente.** `System.getenv()` devolve um mapa
imutável, e não existe `setenv`. Isso é decisão de projeto da JVM, e tem
consequência prática: bibliotecas de `.env` em Java (`dotenv-java`) **não** injetam em
`System.getenv()` — elas mantêm um mapa próprio. Código que lê `System.getenv()`
direto **não enxerga** o `.env`. É a pegadinha nº 1 de Java neste assunto.

Use `System.getProperty()` (propriedades de sistema, essas sim alteráveis) ou o
mecanismo do framework.

### Spring Boot — o modelo mais completo do mercado

```yaml
# application.yml
spring:
  datasource:
    url: ${DATABASE_URL}                 # obrigatória: falha na inicialização se faltar
    password: ${DB_PASSWORD:}            # com padrão vazio
server:
  port: ${PORT:8080}                     # padrão 8080
```

**Relaxed binding**: `DATABASE_URL`, `database.url`, `database-url` e `databaseUrl`
são a mesma propriedade. Isso resolve, sozinho, a incompatibilidade entre a convenção
`MAIÚSCULA_COM_UNDERSCORE` do ambiente e a `ponto.separado` do Java.

```java
@ConfigurationProperties(prefix = "app")
@Validated
public record AppConfig(
    @NotBlank String apiKey,
    @Min(1) @Max(65535) int port,
    @NotNull Duration timeout          // "PT30S" ou "30s" — conversão automática
) {}
```

Isso é o equivalente do `pydantic-settings`: tipado, validado, e o Spring **falha na
inicialização** listando todos os erros.

**Ordem de precedência (do mais forte ao mais fraco), simplificada:**
argumentos de linha de comando → variáveis de ambiente → `application-{perfil}.yml`
→ `application.yml` → padrões no código.

### Segredos em Spring

```yaml
spring:
  config:
    import:
      - optional:configtree:/run/secrets/     # ⭐ cada ARQUIVO vira uma propriedade
      - optional:vault://                     # Spring Cloud Vault
```

`configtree` é o padrão `_FILE` do Docker/Kubernetes embutido no framework:
o arquivo `/run/secrets/db.password` vira a propriedade `db.password`. É a melhor
solução da lista, e pouca gente conhece.

⚠️ **Cuidado com o Actuator:** o endpoint `/actuator/env` expõe **todas** as
propriedades. O Spring mascara por heurística de nome (`password`, `secret`, `key`,
`token`), mas nomes fora do padrão passam. **Não exponha `/actuator/env`
publicamente**, nunca.

---

## 2. .NET / C#

```csharp
var s = Environment.GetEnvironmentVariable("DATABASE_URL");
```

O modelo do ASP.NET Core é por camadas, e é bom:

```csharp
var builder = WebApplication.CreateBuilder(args);
// ordem padrão (a última vence):
//   appsettings.json → appsettings.{Environment}.json → User Secrets (só em Dev)
//   → variáveis de ambiente → argumentos de linha de comando

builder.Services.AddOptions<ConfigApp>()
    .Bind(builder.Configuration.GetSection("App"))
    .ValidateDataAnnotations()
    .ValidateOnStart();          // ⭐ falha na INICIALIZAÇÃO, não na primeira requisição
```

**A convenção de aninhamento** — que confunde quem vem de outra plataforma:

```bash
# corresponde a { "ConnectionStrings": { "Default": "..." } }
ConnectionStrings__Default="Server=db;Database=loja"
#                ^^ dois underscores = um nível de aninhamento
```

Em Linux use `__` (dois underscores); `:` também funciona no Windows, mas não é
portátil.

### User Secrets — só em desenvolvimento

```bash
dotnet user-secrets init
dotnet user-secrets set "ConnectionStrings:Default" "Server=localhost;..."
```

Grava em `~/.microsoft/usersecrets/<id>/secrets.json`, **fora** do projeto — logo
fora do Git por construção. É a melhor solução de desenvolvimento local entre todas
as plataformas deste curso, e é ativa **apenas** quando `ASPNETCORE_ENVIRONMENT=Development`.

Em produção: variáveis de ambiente, Azure Key Vault
(`builder.Configuration.AddAzureKeyVault(...)`) ou arquivos montados.

---

## 3. Go

```go
import "os"

valor := os.Getenv("DATABASE_URL")               // "" se não existir — sem distinção
valor, existe := os.LookupEnv("DATABASE_URL")    // ⭐ distingue vazio de ausente
os.Environ()                                     // []string{"K=V", ...}
```

Use **sempre** `LookupEnv`. `Getenv` não diferencia `VAR=` (definida e vazia) de
`VAR` inexistente — e essa diferença importa, como visto em
[15-node.md §3.1](15-node.md).

Configuração idiomática, sem dependência:

```go
type Config struct {
    DatabaseURL string
    Port        int
    LogLevel    string
}

func Carregar() (*Config, error) {
    var problemas []string

    exigido := func(nome string) string {
        v, ok := os.LookupEnv(nome)
        if !ok || v == "" {
            problemas = append(problemas, "falta "+nome)
        }
        return v
    }

    cfg := &Config{DatabaseURL: exigido("DATABASE_URL")}

    porta := 3000
    if s, ok := os.LookupEnv("PORT"); ok {
        n, err := strconv.Atoi(s)
        if err != nil || n < 1 || n > 65535 {
            problemas = append(problemas, "PORT inválida: "+s)
        } else {
            porta = n
        }
    }
    cfg.Port = porta

    if len(problemas) > 0 {
        return nil, fmt.Errorf("configuração inválida:\n  • %s", strings.Join(problemas, "\n  • "))
    }
    return cfg, nil
}
```

Bibliotecas conhecidas: `github.com/joho/godotenv` (o `.env` de Go),
`github.com/caarlos0/env` (tags em struct, minha preferida pela simplicidade),
`spf13/viper` (completa e pesada).

```go
type Config struct {
    DatabaseURL string `env:"DATABASE_URL,required"`
    Port        int    `env:"PORT" envDefault:"3000"`
}
cfg, err := env.ParseAs[Config]()   // caarlos0/env
```

Vantagem estrutural do Go aqui: o binário é estático, e a configuração é o **único**
insumo externo. Isso torna o "artefato único promovido entre ambientes" trivialmente
verdadeiro.

---

## 4. Ruby / Rails

```ruby
ENV['DATABASE_URL']                      # nil se não existir
ENV.fetch('DATABASE_URL')                # KeyError — ⭐ falha rápida
ENV.fetch('PORT', '3000')                # com padrão
```

```ruby
# Gemfile
gem 'dotenv-rails', groups: [:development, :test]   # ⭐ NÃO em produção
```

Repare no `groups:` — a própria gem documenta que não deve ser carregada em produção.
É a comunidade mais explícita a esse respeito entre todas do curso.

### Rails credentials — o cofre embutido

```bash
EDITOR=vim rails credentials:edit --environment production
```

Gera dois arquivos:

- `config/credentials/production.yml.enc` — **criptografado, vai para o Git**;
- `config/credentials/production.key` — a chave, **NÃO vai para o Git**.

```ruby
Rails.application.credentials.stripe[:secret_key]
```

Em produção, a chave chega pela variável `RAILS_MASTER_KEY` — que é, literalmente,
o **segredo zero** ([60-teoria-avancada.md §4](60-teoria-avancada.md)). Todo o
esquema reduz N segredos a 1, o que é um ganho real, mas não elimina o problema —
apenas o concentra.

---

## 5. Rust

```rust
use std::env;

match env::var("DATABASE_URL") {
    Ok(v) => println!("{v}"),
    Err(env::VarError::NotPresent) => eprintln!("falta DATABASE_URL"),
    Err(env::VarError::NotUnicode(_)) => eprintln!("valor não é UTF-8 válido"),
}
```

Rust é a única linguagem da lista que **força** você a tratar o caso "não é UTF-8
válido" — o tipo `Result` não deixa ignorar. É um detalhe pedante que salva quem
lida com valores vindos de sistemas legados.

```rust
// config.rs com serde + envy
#[derive(serde::Deserialize)]
struct Config {
    database_url: String,
    #[serde(default = "porta_padrao")]
    port: u16,
}
let config: Config = envy::from_env()?;   // erro claro listando o campo faltante
```

⚠️ Desde o Rust 1.80, `std::env::set_var` é `unsafe` em edições novas: alterar o
ambiente em processo multithread é uma condição de corrida real (outro thread pode
estar lendo `environ` no mesmo instante). É o mesmo problema que a documentação do
PHP menciona para `getenv()` em SAPI multithread — Rust apenas o torna visível no
sistema de tipos.

---

## 6. Tabela comparativa

| Plataforma | Ler | Falha rápida idiomática | `.env` local | Cofre nativo |
|---|---|---|---|---|
| **Node** | `process.env.X` | você implementa | `--env-file` nativo | — |
| **Python** | `os.environ["X"]` | `KeyError` de graça | `python-dotenv` | — |
| **PHP** | `getenv('X')` | você implementa | `phpdotenv` | Symfony secrets |
| **Java/Spring** | `System.getenv` | `@Validated` + `ValidateOnStart` | `dotenv-java` (limitada) | Spring Cloud Vault, `configtree` |
| **.NET** | `Environment.GetEnvironmentVariable` | `.ValidateOnStart()` | User Secrets | Azure Key Vault |
| **Go** | `os.LookupEnv` | você implementa | `godotenv` | — |
| **Ruby** | `ENV.fetch` | `KeyError` de graça | `dotenv-rails` | Rails credentials |
| **Rust** | `env::var` | `Result` obriga | `dotenvy` | — |

**Padrão que se repete:** as plataformas que **falham na inicialização** (Spring,
.NET com `ValidateOnStart`, Python com `KeyError`) produzem menos incidentes de
produção do que as que devolvem nulo em silêncio. Onde a sua não faz isso,
**implemente você**, como no [projeto-modelo](07-projeto-modelo/README.md).

---

## 7. Bancos, filas e a "URL única"

Vale notar um padrão que atravessa todas as linguagens:

```bash
DATABASE_URL=postgres://usuario:senha@host:5432/banco?sslmode=require
REDIS_URL=rediss://:senha@host:6379/0
AMQP_URL=amqps://usuario:senha@host:5671/vhost
```

Uma variável em vez de cinco (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS`, `DB_NAME`).
Nasceu no Heroku e virou universal.

**Vantagens:** uma coisa só para configurar e rotacionar; formato padronizado;
todo cliente moderno de banco aceita.

**Desvantagens reais, que quase ninguém menciona:**

- a senha fica **embutida numa string** — logo, redação por nome de chave não a pega
  (é por isso que o [projeto-modelo](07-projeto-modelo/src/log.mjs) tem `redigirUrl`);
- caracteres especiais na senha precisam de codificação percentual: uma senha com
  `@` ou `/` **quebra o parsing da URL**, e o erro resultante é obscuro;
- rotacionar só a senha exige reescrever a string inteira.

```bash
# senha "p@ss/w0rd" precisa virar:
DATABASE_URL=postgres://app:p%40ss%2Fw0rd@host:5432/loja
```

Mais um argumento para gerar segredos no alfabeto `A–Za–z0–9-_`.

---

## Autoteste

1. Por que `System.getenv()` em Java não enxerga o que uma biblioteca de `.env` carregou?
2. O que é *relaxed binding* no Spring, e qual incompatibilidade ele resolve?
3. O que `optional:configtree:/run/secrets/` faz, e a qual padrão do Docker corresponde?
4. Como se representa `{"ConnectionStrings": {"Default": …}}` numa variável de ambiente no .NET em Linux?
5. Por que `os.LookupEnv` é preferível a `os.Getenv` em Go?
6. Por que a gem `dotenv-rails` é declarada só nos grupos de desenvolvimento e teste?
7. O que é o `RAILS_MASTER_KEY` do ponto de vista do problema do segredo zero?
8. Por que `std::env::set_var` virou `unsafe` no Rust?
9. Cite duas desvantagens concretas do padrão `DATABASE_URL` única.
10. Uma senha com `@` quebra a `DATABASE_URL`. Como se resolve, e como se evita?

---

**Fontes consultadas em 14/08/2026:** docs.spring.io (Externalized Configuration) ·
learn.microsoft.com (Configuration in ASP.NET Core) · pkg.go.dev/os ·
guides.rubyonrails.org (Security / credentials) · doc.rust-lang.org/std/env ·
github.com/caarlos0/env · github.com/joho/godotenv.
**Nenhum exemplo deste arquivo foi executado nesta máquina.**

**Próximo:** [20-frontend-e-build-time.md](20-frontend-e-build-time.md) · Voltar ao [mapa](00-MAPA.md)
