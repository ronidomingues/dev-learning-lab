# 02 · Pré-requisitos

`Nível: iniciante` · `Atualizado: 11/08/2026`

Dez minutos de leitura que evitam horas de frustração.

---

## 1. Conhecimento

### 1.1 Indispensável — para qualquer trilha

| Você precisa saber | Nível suficiente | Onde aprender se faltar |
|---|---|---|
| Usar um navegador e entender o que é uma URL | básico | [12-http-por-dentro.md](12-http-por-dentro.md) §2 já ensina |
| Diferença entre "meu computador" e "um servidor" | conceitual | [10-fundamentos.md](10-fundamentos.md) §3 |
| Ler texto estruturado (chaves, colchetes, aspas) | reconhecer JSON | [05-manual-de-uso.md](05-manual-de-uso.md) §7 |
| Ler inglês técnico | com apoio de tradutor | a maior parte das specs só existe em inglês |

**Sobre o inglês, sem rodeio:** todos os RFCs, a especificação OpenAPI, a documentação da
maioria das APIs e o Stack Overflow estão em inglês. Ler é obrigatório na prática; falar,
não. Este material está em português justamente para reduzir essa barreira, mas ele não
substitui a leitura das fontes primárias em [95-referencias.md](95-referencias.md).

### 1.2 Indispensável — para **consumir** APIs

| Você precisa saber | Nível suficiente |
|---|---|
| Linha de comando | `cd`, executar um comando, ler a saída de erro |
| Uma linguagem de programação, qualquer uma | fazer um laço, um `if`, chamar uma função |
| JSON | ler e escrever à mão |
| Variáveis de ambiente | guardar uma chave de API sem colocá-la no código |

### 1.3 Indispensável — para **construir** APIs

Tudo acima, mais:

| Você precisa saber | Nível suficiente | Onde aprender |
|---|---|---|
| Programação com alguma profundidade | funções, tipos, tratamento de erro, testes | qualquer curso da sua linguagem |
| HTTP | métodos, status, cabeçalhos | [12-http-por-dentro.md](12-http-por-dentro.md) — está aqui |
| Modelagem de dados | o que é uma entidade e um relacionamento | básico de banco relacional |
| Git | `clone`, `commit`, `branch` | https://git-scm.com/book/pt-br/v2 |
| Noção de concorrência | dois pedidos ao mesmo tempo podem se atrapalhar | [60-teoria-avancada.md](60-teoria-avancada.md) §2 |
| Noção de segurança | o que é um segredo e por que não vai no Git | [16-seguranca.md](16-seguranca.md) |

### 1.4 Ajuda muito, mas dá para começar sem

- **TCP/IP e DNS** — entender o que acontece antes do HTTP.
- **TLS/HTTPS** — indispensável ao chegar em [16-seguranca.md](16-seguranca.md).
- **Docker** — facilita muito rodar dependências (banco, fila) sem instalar nada.
- **SQL** — a maioria das APIs guarda dados em algum lugar.
- **Teoria de sistemas distribuídos** — para [60-teoria-avancada.md](60-teoria-avancada.md).

### 1.5 O que **não** é pré-requisito

- **Saber uma linguagem específica.** Os conceitos são idênticos em Python, Java, Go, C#,
  Node, PHP, Rust. O projeto-modelo usa Node.js por ser o de instalação mais simples, não
  por ser o melhor.
- **Saber montar servidor, rede ou infraestrutura.**
- **Ter trabalhado com microsserviços.** Aliás, começar por eles é um erro — ver
  [75-armadilhas.md](75-armadilhas.md) §6.
- **Matemática.** Nada aqui exige, exceto a leitura opcional do arquivo `60`.

---

## 2. Ambiente

### 2.1 Contas

| Item | Custo | Obrigatório? |
|---|---|---|
| Nenhuma conta | — | **Nenhuma conta é necessária** para os capítulos 01 a 06 |
| GitHub (ou GitLab) | grátis | recomendado, para versionar o projeto-modelo |
| Uma chave de API pública qualquer (ex.: um serviço de clima) | grátis | opcional, para o Lab 3 |

**Este é um dos poucos assuntos em que você pode ir do zero ao avançado sem criar
uma única conta e sem gastar nada.** APIs públicas gratuitas e sem cadastro existem em
quantidade suficiente para todo o material.

### 2.2 Máquina

| Recurso | Mínimo | Confortável |
|---|---|---|
| Sistema operacional | Windows 10, macOS 12, ou qualquer Linux atual | qualquer um atualizado |
| RAM | 4 GB | 8 GB |
| Disco livre | 2 GB | 5 GB |
| Conexão | necessária para chamar APIs externas | — |

**Você pode fazer boa parte do material sem instalar nada** — ver
[03-instalacao.md](03-instalacao.md) §1.

### 2.3 Software (instruções completas em [03-instalacao.md](03-instalacao.md))

| Software | Para quê | Obrigatório? |
|---|---|---|
| Navegador atual | primeiras chamadas, DevTools | sim |
| **curl** | chamar APIs pelo terminal | sim (já vem instalado em quase tudo) |
| **jq** | ler JSON no terminal sem enlouquecer | fortemente recomendado |
| **HTTPie** | alternativa amigável ao curl | opcional |
| **Bruno** ou **Postman** ou **Hoppscotch** | cliente gráfico, coleções salvas | recomendado |
| **Node.js 24 LTS** | construir a API do projeto-modelo | trilha de construção |
| **Docker** | subir banco/fila sem instalar | opcional |
| **VS Code** (ou outro editor) | escrever código | trilha de construção |

> **Pegadinha nº 1 de quem começa:** o `curl` do **PowerShell** no Windows **não é o curl**.
> `curl` lá é um apelido para `Invoke-WebRequest`, com sintaxe completamente diferente, e
> todo comando que você copiar da internet vai falhar de forma confusa. Tratado em
> [03-instalacao.md](03-instalacao.md) §3.4.

---

## 3. Tempo realista até cada nível

Estimativas honestas, com **prática**, não só leitura. "Semana" = ~8 h de estudo.

| Marco | Você consegue… | Do zero | Já programando |
|---|---|---|---|
| **Primeira chamada** | fazer um `GET` e ler o JSON | 30 min | 5 min |
| **Consumidor competente** | autenticar, paginar, tratar erro, ler documentação | 2–3 semanas | 3–5 dias |
| **Primeira API própria** | CRUD funcionando com validação e testes | 4–6 semanas | 1 semana |
| **API que você não teria vergonha de publicar** | + OpenAPI, erros padronizados, versionamento, auth | 3 meses | 3–4 semanas |
| **Escolher o estilo certo com argumento** | REST vs. gRPC vs. GraphQL vs. eventos | 6 meses | 2 meses |
| **Projetar a API de um domínio inteiro** | contratos, evolução, governança, SLO | 2 anos | 1 ano |
| **Discutir [60-teoria-avancada.md](60-teoria-avancada.md) com proveito** | idempotência, CAP, subtipagem | — | requer ter operado algo em produção |

**Onde as estimativas costumam falhar:** a parte difícil não é fazer a API funcionar — é
fazê-la **evoluir sem quebrar quem já usa**. Isso não se aprende em tutorial; aprende-se
quebrando a produção de alguém uma vez. [18-operacao-e-ciclo-de-vida.md](18-operacao-e-ciclo-de-vida.md)
tenta poupar você dessa experiência, com sucesso parcial.

---

## 4. Rota de resgate — o que fazer se faltar um pré-requisito

| Está faltando | Não pare. Faça isto: |
|---|---|
| **Programação** | Faça só a trilha de **consumo**: `01`, `03`, `04`, `05`, `06`, `12`, `13`, `19`. Dá para entender APIs profundamente sem escrever uma linha de servidor. |
| **Terminal** | Use um cliente gráfico (Bruno/Postman/Hoppscotch) e o DevTools do navegador. Aprenda o terminal depois — mas aprenda. |
| **HTTP** | Não estude HTTP em outro lugar: [12-http-por-dentro.md](12-http-por-dentro.md) foi escrito para ser o seu curso de HTTP. |
| **JSON** | 15 minutos: https://www.json.org/json-pt.html. É um formato de meia página de regras. |
| **Git** | Comece sem. Adote ao chegar no projeto-modelo. |
| **Node.js** | Faça o projeto-modelo na sua linguagem. O README explica o desenho antes do código, justamente para isso. |
| **Docker** | Tudo no material tem alternativa sem Docker. |
| **Inglês** | Use tradutor de página nos RFCs. Priorize [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) §2 (cursos em português). |
| **Tempo** | Leia `01` → `10` → `13` → `19`. Quatro arquivos, ~2 horas, e você já discute API com propriedade. |

---

## 5. Checklist antes de ir para o `03`

- [ ] Sei qual trilha vou seguir: **consumir** APIs, **construir** APIs, ou **decidir** sobre elas.
- [ ] Tenho um navegador atual.
- [ ] Aceito que vou precisar ler documentação em inglês.
- [ ] Entendi que uma chamada de rede é ~1.000.000× mais lenta que uma chamada de função.

Se marcou tudo: **[03-instalacao.md](03-instalacao.md)**.

---

## Autoteste

1. Quais três conhecimentos são indispensáveis para construir APIs e dispensáveis para consumi-las?
2. Por que este assunto pode ser estudado sem criar nenhuma conta e sem gastar nada?
3. Qual é a pegadinha do `curl` no Windows, e por que ela confunde tanto?
4. Qual é o tempo realista, partindo do zero, até conseguir publicar uma API decente?
5. Segundo este arquivo, qual é a parte realmente difícil de APIs — e por que ela não se aprende em tutorial?
6. Você não sabe programar e tem 2 horas. Qual é a sua rota?
