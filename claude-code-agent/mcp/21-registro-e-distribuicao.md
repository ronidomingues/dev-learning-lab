# 21 · Registro e distribuição — publicar e encontrar servidores

`Nível: intermediário` · `Escrito em 01/09/2026`

---

## 1. O que é o MCP Registry

> **Atenção:** o MCP Registry está em **pré-visualização** (*preview*). Mudanças que
> quebram, ou reinicialização de dados, podem acontecer antes da disponibilidade geral.

É o **repositório oficial e centralizado de metadados** de servidores MCP publicamente
acessíveis, apoiado por Anthropic, GitHub, PulseMCP e Microsoft.

Oferece:

- um lugar só para o autor publicar metadados do servidor;
- **gestão de namespace por verificação de DNS** (ou de conta GitHub);
- uma **API REST** para clientes e agregadores descobrirem servidores;
- informação padronizada de instalação e configuração.

**O que ele não é:** um repositório de código nem de binários. Ele guarda **metadados que
apontam** para npm, PyPI, Docker Hub etc. `weather-mcp` mora no npm; o registry mapeia
"weather v1.2.0" → `npm:weather-mcp`.

```
   Autor  ──publica pacote──►  npm / PyPI / Docker Hub
     │
     └────publica metadado──►  MCP Registry  ──API──►  agregadores/marketplaces
                                                            │
                                                            └──►  hosts (Claude, VS Code…)
```

**O registry não é para ser consumido diretamente pelos hosts.** A arquitetura prevista é:
hosts consomem **agregadores** (marketplaces), que puxam do registry oficial de tempos em
tempos (a orientação é algo como uma vez por hora). O registry publica uma
**especificação OpenAPI** que outros registries podem implementar para oferecer a mesma
interface — inclusive registries **privados** de empresa.

---

## 2. O que entra e o que não entra

**Entra:** servidor de código aberto ou fechado, **desde que** o método de instalação
seja público (pacote no npm, imagem no Docker Hub) **ou** o servidor em si seja
publicamente acessível (endpoint remoto não restrito a rede privada).

**Não entra:** servidores privados — acessíveis a um conjunto estreito de usuários.
Exemplos que a documentação dá: `mcp.acme-corp.internal`, ou
`npx -y @acme/mcp --registry https://artifactory.acme-corp.internal/npm`.
Para isso, hospede o **seu próprio** registry privado.

> O código do registry oficial **não** é projetado para auto-hospedagem, e os mantenedores
> não dão suporte a esse caso. Se você bifurcar, mantém e opera por conta própria.

---

## 3. Publicando um servidor — passo a passo

Fluxo oficial com a CLI `mcp-publisher`, para um servidor em TypeScript publicado no npm.

### 3.1 Pré-requisitos

- Node.js;
- conta no **npm** (o registry só guarda metadados; o pacote vai para o npm);
- conta no **GitHub** (há [outros métodos de autenticação](https://modelcontextprotocol.io/registry/authentication), inclusive **DNS**).

### 3.2 Marcar o pacote

O registry verifica que o pacote corresponde ao metadado. Para npm, acrescente
`mcpName` ao `package.json`:

```diff
 {
   "name": "@meu-usuario/mcp-weather-server",
   "version": "1.0.1",
+  "mcpName": "io.github.meu-usuario/weather",
   "main": "index.js",
```

Com autenticação por GitHub, `mcpName` **tem de** começar com `io.github.meu-usuario/`.

### 3.3 Publicar o pacote

```bash
npm install && npm run build
```

```bash
npm adduser          # se ainda não estiver autenticado
npm publish --access public
```

### 3.4 Instalar a CLI

```bash
curl -L "https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/').tar.gz" | tar xz mcp-publisher && sudo mv mcp-publisher /usr/local/bin/
```

Ou, no macOS: `brew install mcp-publisher`

```bash
mcp-publisher --help
# esperado:
# MCP Registry Publisher Tool
# Commands:
#   init     Create a server.json file template
#   login    Authenticate with the registry
#   logout   Clear saved authentication
#   publish  Publish server.json to the registry
```

### 3.5 Criar o `server.json`

```bash
mcp-publisher init
```

Gera algo como:

```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.github.meu-usuario/weather",
  "description": "An MCP server for weather information.",
  "repository": {
    "url": "https://github.com/meu-usuario/mcp-weather-server",
    "source": "github"
  },
  "version": "1.0.1",
  "packages": [
    {
      "registryType": "npm",
      "identifier": "@meu-usuario/mcp-weather-server",
      "version": "1.0.1",
      "transport": { "type": "stdio" },
      "environmentVariables": [
        { "name": "YOUR_API_KEY", "description": "Sua chave de API",
          "isRequired": true, "format": "string", "isSecret": true }
      ]
    }
  ]
}
```

> O `name` do `server.json` **tem de** ser igual ao `mcpName` do `package.json`.

O campo `environmentVariables`, com `isSecret: true`, é o que permite ao host pedir a
credencial ao usuário e guardá-la no lugar certo (em `env`, não em `args`).

### 3.6 Autenticar e publicar

```bash
mcp-publisher login github
```

```
To authenticate, please:
1. Go to: https://github.com/login/device
2. Enter code: ABCD-1234
```

```bash
mcp-publisher publish
```

```
Publishing to https://registry.modelcontextprotocol.io...
✓ Successfully published
✓ Server io.github.meu-usuario/weather version 1.0.1
```

### 3.7 Conferir

```bash
curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.meu-usuario/weather"
```

### 3.8 Erros comuns

| Mensagem | O que fazer |
|---|---|
| `Registry validation failed for package` | falta a informação de validação (ex.: `mcpName` no `package.json`) |
| `Invalid or expired Registry JWT token` | `mcp-publisher login github` de novo |
| `You do not have permission to publish this server` | o método de autenticação não casa com o formato do namespace. Com GitHub, o nome tem de começar com `io.github.seu-usuario/` |

---

## 4. Namespaces e confiança

Nomes seguem **DNS reverso**: `io.github.usuario/servidor` ou `com.exemplo/servidor`.
Isso amarra o nome a uma conta GitHub verificada ou a um domínio verificado — só o dono
legítimo publica naquele namespace. É o mecanismo de **autenticidade** do registry.

Com autenticação por **DNS**, você usa o seu próprio domínio como prefixo, o que é o
caminho para servidor corporativo público.

### 4.1 O que o registry **não** faz

Seja franco com você mesmo sobre isto:

| O registry garante | O registry **não** garante |
|---|---|
| que quem publicou controla o namespace | que o código é seguro |
| que o metadado aponta para o pacote declarado | que o pacote faz o que diz |
| que spam é removível por moderação manual | que a versão de amanhã continua benigna |

**Varredura de segurança é delegada:** aos registries de pacote (npm, PyPI, Docker Hub,
que fazem a própria varredura) e aos agregadores a jusante (que podem acrescentar
verificações, notas e curadoria). O registry oficial foca em **autenticação de namespace
e hospedagem de metadados**.

**Antispam:** exigência de verificação de namespace (GitHub, DNS ou desafio HTTP);
limites de caracteres e validação por expressão regular em campos livres; e **remoção
manual** por moderação. Em consideração para o futuro: limite de taxa mais estrito,
detecção por IA e denúncia pela comunidade.

> **Consequência prática, e é a mais importante deste arquivo:** estar no registry
> **não é** um selo de segurança. Trate como o npm: o nome é verificado, o
> comportamento não. Ver [19 · Segurança](19-seguranca.md).

---

## 5. Servidores remotos

Servidores remotos são publicáveis: em vez de um `packages`, o `server.json` declara o
endpoint. Isso permite ao host conectar sem instalar nada — o modelo de distribuição que
mais cresce, porque elimina o passo mais frágil (instalação na máquina do usuário).

Detalhes em [Publishing Remote Servers](https://modelcontextprotocol.io/registry/remote-servers).

---

## 6. Automação com GitHub Actions

O registry documenta um fluxo de publicação por
[GitHub Actions](https://modelcontextprotocol.io/registry/github-actions). O padrão sensato:

```
tag no git ──► CI ──► testes ──► npm publish ──► mcp-publisher publish
```

Duas regras de higiene:

1. **Nunca publique sem testar.** Um servidor MCP quebrado no registry vira erro na
   máquina de outra pessoa, num host que ela não controla.
2. **Versione o `server.json`** e mantenha a versão dele igual à do pacote. Divergência
   é a causa nº 1 de falha de validação.

---

## 7. Distribuição sem o registry

O registry é novo e está em preview. Boa parte do ecossistema ainda distribui assim:

| Forma | Como o usuário instala | Prós | Contras |
|---|---|---|---|
| **npm / PyPI** | `npx -y meu-servidor` / `uvx meu-servidor` | familiar; sem passo extra | usuário precisa do runtime |
| **Imagem Docker** | `docker run --rm -i meu/servidor` | isolamento; sem runtime | mais pesado; montagens a configurar |
| **Binário único** (Go, Rust) | baixar e executar | sem dependência | um artefato por plataforma |
| **Servidor remoto** | só uma URL | **nada a instalar**; você atualiza sozinho | precisa de OAuth, hospedagem, SLA |
| **Código-fonte** | `git clone` + rodar | transparente | fricção alta |

**Recomendação:** se o servidor é local, distribua por **npm ou PyPI** (é o que os hosts
esperam no `command`) **e** ofereça uma **imagem Docker** para quem quer isolamento —
o que, depois de ler o arquivo 19, deveria ser todo mundo que usa servidor de terceiro.

---

## 8. Escolhendo um servidor de terceiro

Lista de verificação antes de conectar qualquer servidor à sua máquina:

- [ ] o código é aberto e você **leu** as ferramentas que ele expõe?
- [ ] quantas ferramentas ele expõe? (Sessenta ferramentas é bandeira vermelha de
      contexto e de superfície.)
- [ ] há alguma ferramenta genérica de execução (`shell`, `eval`, `executar_sql`)?
- [ ] que credenciais ele pede, e qual o **escopo mínimo** de cada uma?
- [ ] ele precisa de rede? Dá para rodar sem?
- [ ] ele está no registry, sob um namespace verificado que corresponde a quem você acha
      que é o autor?
- [ ] o pacote tem histórico de manutenção, ou apareceu na semana passada?
- [ ] você consegue rodá-lo em container, com montagem somente-leitura?
- [ ] o nome é parecido demais com o de um servidor popular? (*typosquatting*)

---

## 9. Autoteste

1. O que o MCP Registry hospeda, e o que ele **não** hospeda?
2. Por que os hosts não devem consumir o registry oficial diretamente?
3. Que tipos de servidor **não** entram no registry? Dê os dois exemplos da documentação.
4. Qual campo do `package.json` amarra o pacote npm ao nome no registry? Que restrição existe com autenticação GitHub?
5. O que o registry garante e o que ele explicitamente **não** garante?
6. A quem o registry delega a varredura de segurança?
7. Por que publicar um servidor **remoto** elimina o passo mais frágil da distribuição?
8. Cite três formas de distribuir um servidor local, com prós e contras.
9. Por que "sessenta ferramentas" é bandeira vermelha?
10. Como o namespace por DNS reverso previne *typosquatting* — e o que ele não previne?

---

**Anterior:** [20 · Clientes e hosts](20-clientes-e-hosts.md) · **Próximo:** [22 · Extensões](22-extensoes.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Fontes: [Sobre o registry](https://modelcontextprotocol.io/registry/about),
[Quickstart de publicação](https://modelcontextprotocol.io/registry/quickstart),
[Autenticação](https://modelcontextprotocol.io/registry/authentication),
[Tipos de pacote](https://modelcontextprotocol.io/registry/package-types),
[Servidores remotos](https://modelcontextprotocol.io/registry/remote-servers),
[Política de moderação](https://modelcontextprotocol.io/registry/moderation-policy),
[Agregadores](https://modelcontextprotocol.io/registry/registry-aggregators).
Consultas em 01/09/2026.*
