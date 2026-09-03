# 02 · Pré-requisitos — o que saber e o que ter antes de começar

`Nível: iniciante` · `Atualizado em: 01/09/2026`

---

Este arquivo é honesto de propósito. É melhor descobrir agora que falta uma peça
do que descobrir no meio do [03-instalacao.md](03-instalacao.md).

---

## 1. Conhecimento

### 1.1 Indispensável

Sem isto você trava. Não é opcional.

| Você precisa saber | Como testar se sabe | Onde aprender se não sabe |
|---|---|---|
| **Usar um terminal**: abrir, navegar entre pastas (`cd`), listar (`ls`/`dir`), rodar um comando, ler a saída, saber que `Ctrl+C` interrompe | Consegue rodar `cd ~ && ls -la` e explicar o que apareceu? | [Linux Journey — Command Line](https://linuxjourney.com/lesson/the-shell) (EN, gratuito); no Windows, o [tutorial de PowerShell da Microsoft](https://learn.microsoft.com/pt-br/powershell/scripting/learn/ps101/01-getting-started) (PT) |
| **O que é JSON** e como ler um objeto aninhado | Sabe dizer o que é `{"cliente": {"nome": "Ana", "tags": ["vip"]}}` e como se chega em `"vip"`? | [json.org](https://www.json.org/json-pt.html) (PT, 10 minutos) |
| **O que é uma API HTTP**: URL, método (`GET`/`POST`), cabeçalho, corpo, código de status (200, 401, 404, 500) | Sabe a diferença entre 401 e 403? | A pasta [`apis/`](../apis/00-MAPA.md) deste repositório |
| **Copiar e colar com atenção** | Sério. Metade dos erros de instalação é uma aspa perdida. | — |

### 1.2 Ajuda muito (e você vai querer, cedo ou tarde)

| Assunto | Por que ajuda | Onde aprender |
|---|---|---|
| **Docker** — imagem, contêiner, volume, `compose` | É a forma oficial e, a partir do n8n 3.0 (out/2026), **a única** de rodar o n8n autogerido | [`curso-docker/`](../curso-docker/00-indice.md) ou [`docker/`](../docker/00-MAPA.md) deste repositório |
| **JavaScript básico** — `map`, `filter`, template string, `async/await` | O node Code e as expressões são JavaScript. Dá para viver sem, mas você fica com metade da ferramenta | [JavaScript.info em português](https://javascript.info/) |
| **SQL básico** — `SELECT`, `INSERT`, `WHERE`, `JOIN` | Quase todo fluxo sério toca um banco | [`postgresql/`](../postgresql/00-MAPA.md) deste repositório |
| **Autenticação de APIs** — API key, OAuth 2.0, token Bearer | Conectar qualquer serviço externo é, em 90% dos casos, resolver autenticação | [`jwt/`](../jwt/00-MAPA.md) e a pasta `apis/` |
| **Redes básicas** — porta, `localhost`, DNS, proxy reverso, HTTPS | Necessário para expor webhooks e para pôr o n8n em produção | [`portas-de-rede/`](../portas-de-rede/00-MAPA.md), [`tls/`](../tls/00-MAPA.md) |
| **Git** | Versionar fluxos, e o recurso oficial de *source control* é Git | — |

### 1.3 O que você NÃO precisa saber

Para desfazer o medo:

- Não precisa saber TypeScript nem compilar nada.
- Não precisa saber Kubernetes (só se for escalar de verdade — arquivo [21](21-escala-e-producao.md)).
- Não precisa saber administrar Postgres (SQLite serve para aprender).
- Não precisa saber nada de IA para usar o n8n; a parte de agentes é opcional e
  fica no arquivo [24](24-ia-e-agentes.md).

---

## 2. Ambiente — máquina, sistema e contas

### 2.1 Requisitos de máquina

Números reais, não os do folheto:

| Cenário | RAM | CPU | Disco | Observação |
|---|---|---|---|---|
| **Aprender** (n8n só, SQLite) | 2 GB livres | 2 vCPU | 2 GB | Roda no seu notebook sem sentir |
| **Aprender com o "one-line setup"** (n8n + sandbox de IA) | **4 GB livres** | 2 vCPU | ~8 GB | O sandbox é Docker-dentro-de-Docker; é ele que pesa |
| **Produção pequena** (n8n + Postgres) | 4 GB | 2 vCPU | 20 GB + crescimento do banco | Um VPS de ~US$ 12–20/mês dá conta |
| **Produção com fila** (main + workers + Redis + Postgres) | 8–16 GB | 4+ vCPU | 50 GB+ | Veja [21-escala-e-producao.md](21-escala-e-producao.md) |

> **Cuidado clássico:** o consumo de memória do n8n é dominado pelos **dados que
> passam pelo fluxo**, não pelo n8n em si. Um fluxo que baixa um CSV de 200 MB e
> o converte para itens pode usar vários GB. Isso é explicado em
> [21-escala-e-producao.md](21-escala-e-producao.md) e em [75-armadilhas.md](75-armadilhas.md).

### 2.2 Sistema operacional

- **Linux** — caminho de primeira classe. Debian/Ubuntu e Fedora/RHEL cobertos no arquivo 03.
- **macOS** — Intel e Apple Silicon, ambos suportados (a imagem Docker tem `arm64`).
- **Windows** — **use WSL2**. Nativo funciona para brincar, mas dá problema com
  permissões de arquivo, finais de linha e caminhos de volume. Justificativa detalhada em
  [03-instalacao.md](03-instalacao.md).

### 2.3 Versões mínimas de software

Verificado em **01/09/2026**:

| Software | Mínimo | Recomendado | Como conferir |
|---|---|---|---|
| Docker Engine | 20.10 | 24+ | `docker --version` |
| Docker Compose | **v2** (plugin `docker compose`) | v2.24+ | `docker compose version` |
| Node.js (só se for instalar por npm — caminho em extinção) | 20 LTS | 22 LTS | `node --version` |
| Navegador | Chrome/Edge/Firefox/Safari atual | — | O editor é uma aplicação web moderna; IE e navegadores antigos não funcionam |

> **Aviso com data — o mais importante deste arquivo.**
> O **n8n 3.0, previsto para outubro de 2026**, remove o suporte a instalação via
> `npm install n8n` / `npx n8n`. A partir dele, autogerir n8n significa **Docker**.
> Se você está começando agora, comece por Docker e ignore o caminho npm.
> Fonte: [docs.n8n.io/changelog/v30-breaking-changes](https://docs.n8n.io/changelog/v30-breaking-changes), consultado em 01/09/2026.

### 2.4 Contas em serviços

Para o **núcleo** do curso: **nenhuma**. Nem cartão de crédito, nem cadastro.
O n8n autogerido pede que você crie um usuário **local**, na sua própria instância —
é um cadastro no seu banco de dados, não em um serviço remoto.

Vai precisar de conta apenas se quiser:

| Para | Conta necessária | Custa? |
|---|---|---|
| Usar o **n8n Cloud** em vez de autogerir | Conta n8n.io | Teste gratuito; depois a partir de € 20/mês (veja [80](80-custos-e-licencas.md)) |
| Usar os **nós de IA** (AI Agent, Chat Model) | Chave de API de um provedor (Anthropic, OpenAI, Google, ou um modelo local via Ollama) | Sim, por uso — Ollama local é gratuito |
| Conectar Google Sheets, Slack, Notion etc. | Conta no serviço em questão | Depende do serviço |
| Expor **webhooks** para a internet a partir da sua máquina | Um túnel (Cloudflare Tunnel, ngrok) ou um VPS | Há camadas gratuitas |

---

## 3. Tempo realista até cada nível

Estimativas honestas, para uma pessoa que atende os pré-requisitos indispensáveis
e estuda de forma concentrada. Não são otimistas de propósito.

| Nível | O que você consegue fazer | Tempo |
|---|---|---|
| **Primeiro fluxo na tela** | Um webhook que responde algo | **30–60 minutos** (incluindo instalar) |
| **Útil de verdade** | Fluxos com IF, laço, HTTP Request, credenciais, tratamento de erro | **15–25 horas** |
| **Confiável** | Você entende item linking, idempotência, retry, sub-workflows, e seus fluxos não quebram silenciosamente | **60–100 horas**, com prática real |
| **Produção séria** | Queue mode, Postgres, poda de execuções, monitoramento, versionamento em Git, segurança | **150–250 horas**, e exige ter operado algo de verdade |
| **Fundo do poço** | Escrever nós próprios, ler o código do motor de execução, discutir semântica de execução | **400+ horas** e experiência prévia em engenharia de software |

**A parte que ninguém conta:** dos que "sabem n8n", a maioria parou no segundo
nível. O salto do segundo para o terceiro — *fluxos que não mentem sobre terem
funcionado* — é onde está o valor profissional. É o assunto dos arquivos
[18](18-erros-e-confiabilidade.md) e [75](75-armadilhas.md).

---

## 4. Rota de resgate — o que fazer se falta um pré-requisito

| Falta | Faça isto agora | Continua o curso? |
|---|---|---|
| **Terminal** | 1 hora no Linux Journey ou no tutorial de PowerShell | Sim, depois disso |
| **Docker** | Use a seção "sem instalar nada" do [03](03-instalacao.md) hoje, e leia [`curso-docker/`](../curso-docker/00-indice.md) em paralelo | **Sim, siga adiante** |
| **JSON** | 15 minutos em json.org. É genuinamente pequeno | Sim |
| **HTTP/API** | Leia a pasta [`apis/`](../apis/00-MAPA.md), pelo menos os fundamentos | Sim, mas você tropeça no arquivo [14](14-nos-e-integracoes.md) |
| **JavaScript** | Não pare. Siga até o arquivo [13](13-expressoes.md) e aprenda o JS necessário lá, sob demanda | Sim |
| **Máquina fraca (< 4 GB livres)** | Use o Docker **sem** o sandbox de IA (compose mínimo do arquivo 03), ou o n8n Cloud gratuito, ou um VPS de US$ 5 | Sim |
| **Windows sem WSL2** | Instale o WSL2 (um comando, está no arquivo 03) | Sim |
| **Rede corporativa com proxy** | Seção "Rede corporativa" do [03](03-instalacao.md) — há armadilhas específicas, inclusive com `no_proxy` | Sim |
| **Não pode instalar nada na máquina** | Use o n8n Cloud (teste gratuito) ou GitHub Codespaces | Sim, com perdas na parte de operação |

---

## 5. Checklist antes de abrir o arquivo 03

```bash
# 1) Terminal funciona e você sabe onde está
pwd

# 2) Tem Docker? (caminho recomendado)
docker --version
docker compose version
docker info | head -5     # precisa responder sem erro de permissão

# 3) Tem espaço em disco?
df -h .                   # queira ao menos 10 GB livres

# 4) Tem memória?
free -h                   # Linux/WSL. macOS: use o Monitor de Atividade
```

Se `docker info` falhar com `permission denied`, isso é normal e tem conserto —
está resolvido no [03-instalacao.md](03-instalacao.md), seção "Permissões".

Se você não tem Docker e não pode instalar, vá direto para a
[alternativa sem instalar nada](03-instalacao.md#alternativa-sem-instalar-nada).

---

## Autoteste

1. Quais são os **quatro** conhecimentos indispensáveis, e por que JSON é um deles?
2. Por que Docker deixou de ser "recomendado" e passou a ser praticamente obrigatório?
   A partir de qual versão e quando?
3. Quanto de RAM livre o "one-line setup" pede, e **por que** ele pede mais que o n8n sozinho?
4. Qual é o consumo de memória que realmente importa no n8n — o do programa ou o dos dados?
5. Você precisa de cartão de crédito para fazer este curso inteiro? Justifique.
6. Quantas horas, honestamente, até fluxos **confiáveis**? O que separa esse nível do anterior?
7. Você está no Windows e não quer WSL2. Que problemas concretos vai encontrar?
8. Falta-lhe JavaScript. Você deve parar o curso? O que a rota de resgate manda fazer?

---

*Anterior: [01-introducao-leigo.md](01-introducao-leigo.md) · Próximo: [03-instalacao.md](03-instalacao.md)*
