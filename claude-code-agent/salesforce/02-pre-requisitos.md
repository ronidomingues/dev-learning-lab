# 02 · Pré-requisitos

`Nível: iniciante` · `Atualizado: 11/08/2026`

Este arquivo existe para você não descobrir no meio do caminho que faltava algo.
Leia inteiro antes de instalar qualquer coisa — são 10 minutos que economizam horas.

---

## 1. Conhecimento

### 1.1 Indispensável — para qualquer trilha

| Você precisa saber | Nível suficiente | Onde aprender se faltar |
|---|---|---|
| Usar um navegador e formulários web | Básico | — |
| Entender o que é um "registro" e um "campo" | Conceito de planilha: linha e coluna | Qualquer tutorial de planilha |
| Ler inglês técnico | Ler documentação com apoio de tradutor | A doc oficial existe em pt-BR parcialmente; a comunidade e os erros, não |
| Noção de processo comercial (o que é um cliente, uma venda, um chamado) | Vocabulário do dia a dia | [01-introducao-leigo.md](01-introducao-leigo.md) |

**Sobre o inglês, sem rodeio:** você consegue tirar a certificação de Administrador em
português — a prova é oferecida em pt-BR. Mas 90% das respostas de erro, dos posts de
comunidade e das discussões de arquitetura estão em inglês. Ler inglês técnico não é
opcional na prática; falar não é necessário.

### 1.2 Indispensável — trilha de **desenvolvedor**

| Você precisa saber | Nível suficiente | Onde aprender se faltar |
|---|---|---|
| Programação orientada a objetos | Classe, objeto, método, herança, interface | Qualquer curso de Java ou C# introdutório |
| Sintaxe estilo Java/C# | Ler e escrever laços, condicionais, coleções | Apex é ~Java 5 com sintaxe quase idêntica |
| SQL básico | `SELECT`, `WHERE`, `JOIN` conceitual | SOQL é um primo pobre e mais rígido do SQL |
| Linha de comando | `cd`, `ls`, executar um binário, ler saída de erro | Ver [03-instalacao.md](03-instalacao.md) §1 |
| Git básico | `clone`, `add`, `commit`, `push`, `branch` | https://git-scm.com/book/pt-br/v2 |
| HTML e CSS | Estrutura de página, seletores | MDN em português |
| JavaScript moderno | `const`/`let`, arrow function, módulos ES, `async/await`, classes | Necessário para LWC — ver [16-lightning-web-components.md](16-lightning-web-components.md) |

> **Se você vem de Java ou C#:** vai se sentir em casa em Apex em um dia. O que vai te
> travar não é a linguagem, é o **ambiente**: limites de execução, o fato de todo código
> rodar dentro de uma transação com teto de consumo, e a obrigação de ter 75% de
> cobertura de testes para publicar em produção.
>
> **Se você vem de JavaScript/Python:** a linguagem vai te irritar (tipagem estática,
> verbosa, sem lambdas ricas), mas LWC é JavaScript moderno padrão e vai te agradar.

### 1.3 Ajuda muito, mas dá para começar sem

- **HTTP e REST** — indispensável quando chegar em [17-integracao-e-apis.md](17-integracao-e-apis.md).
- **OAuth 2.0** — para integrações e para entender o login da CLI.
- **Modelagem relacional / normalização** — evita 80% dos erros de modelagem de dados.
- **Noção de CI/CD** — para [18-devops-e-alm.md](18-devops-e-alm.md).
- **Inglês falado** — só se você quiser trabalhar com times internacionais, onde está o dinheiro.

### 1.4 O que **não** é pré-requisito (e muita gente acha que é)

- Saber administrar servidor, Linux, rede ou banco de dados. Você não tem acesso a nada disso.
- Saber SQL avançado. SOQL não tem `GROUP BY` livre com subqueries arbitrárias, não tem
  `UNION`, e os joins são só pelos relacionamentos declarados. Saber SQL demais até atrapalha
  no começo, porque você tenta coisas que não existem.
- Ter trabalhado com vendas. Ajuda, não é obrigatório.
- Ter diploma. O mercado de Salesforce é, na prática, um dos mais meritocráticos por
  certificação e portfólio que eu conheço.

---

## 2. Ambiente — o que você precisa ter

### 2.1 Conta

| Item | Custo | Obrigatório? | Observação |
|---|---|---|---|
| Conta Trailhead | Grátis | Sim | Ensino oficial; usa e-mail comum |
| Org **Developer Edition** | Grátis, permanente | Sim | Sem cartão de crédito. Ver [03-instalacao.md](03-instalacao.md) §2 |
| Conta GitHub (ou GitLab) | Grátis | Recomendado | Para versionar seu código |
| Cartão de crédito | — | **Não** | Nada neste curso exige pagamento |

**Atenção ao e-mail:** o e-mail que você usar na org Developer Edition fica ligado a ela
**para sempre** e não pode ser reutilizado em outra org DE. Use um e-mail que você controle
e que não vá perder. Truque legítimo e amplamente usado: se seu e-mail é `voce@gmail.com`,
use `voce+sf1@gmail.com`, `voce+sf2@gmail.com` — o Gmail entrega tudo na mesma caixa e o
Salesforce trata como e-mails distintos.

### 2.2 Máquina

| Recurso | Mínimo funcional | Confortável |
|---|---|---|
| Sistema operacional | Windows 10, macOS 12, ou Linux com glibc recente | Qualquer um atualizado |
| Memória RAM | 8 GB | 16 GB |
| Disco livre | 5 GB | 15 GB |
| Processador | x86-64 ou ARM64 (Apple Silicon suportado nativamente) | — |
| Conexão | Estável; a plataforma é 100% online | — |

**Você pode fazer o curso inteiro sem instalar nada** — o Code Builder / ambiente web e o
Developer Console rodam no navegador. Ver [03-instalacao.md](03-instalacao.md) §1.
Isso vale se sua máquina for fraca ou se for um computador corporativo travado.

### 2.3 Software (instruções completas em [03-instalacao.md](03-instalacao.md))

| Software | Para quê | Obrigatório? |
|---|---|---|
| Navegador Chrome ou Edge atual | Usar a plataforma | Sim |
| Node.js LTS (22.x ou 24.x) | Base da Salesforce CLI | Trilha dev |
| Salesforce CLI (`sf`) 2.146.x | Falar com a org pelo terminal | Trilha dev |
| VS Code + Salesforce Extension Pack | Escrever código | Trilha dev |
| Git | Versionar | Trilha dev |
| Java 17 ou 21 (JDK) | Requerido pelo Apex Language Server e pelo Code Analyzer | Trilha dev |

> **Pegadinha clássica:** o Salesforce Extension Pack **não funciona** sem um JDK
> instalado e apontado corretamente. O erro que aparece é críptico ("Java runtime could not
> be located") e trava o autocomplete de Apex. É o problema nº 1 de quem instala pela
> primeira vez. Tratado passo a passo em [03-instalacao.md](03-instalacao.md) §6.

---

## 3. Tempo realista até cada nível

Estas estimativas assumem **estudo com as mãos**, não só leitura, e são honestas —
não otimistas. Um "mês" aqui significa ~10 h/semana.

| Marco | Você consegue… | Do zero | Vindo de outro dev |
|---|---|---|---|
| **Primeira tela** | Criar org, criar objeto e campo, ver dados | 1 dia | 2 horas |
| **Administrador funcional** | Modelar dados, perfis, permission sets, relatórios, Flow simples | 2–3 meses | 3–4 semanas |
| **Certificação Administrator** | Passar na prova oficial | 3–4 meses | 6–8 semanas |
| **Primeiro Apex útil** | Trigger com handler, testes, bulk-safe | +1 mês | +1 semana |
| **Certificação Platform Developer I** | Passar na prova | 6–8 meses | 2–3 meses |
| **Desenvolvedor empregável** | Entregar features numa org real sem quebrar nada | 8–12 meses | 3–6 meses |
| **Sênior** | Decidir Flow vs. Apex, resolver limite, desenhar integração | 3 anos | 1,5–2 anos |
| **Arquiteto** | Desenhar org multi-país, governança, estratégia de dados | 5–8 anos | 4–6 anos |
| **Fronteira** (ler [60](60-teoria-avancada.md) com proveito) | Discutir isolamento multi-inquilino e limites teóricos | — | requer experiência de operação real |

**Onde as estimativas costumam falhar:** a parte difícil de Salesforce não é aprender —
é **desaprender**. Programadores experientes gastam meses brigando com a plataforma
tentando fazer as coisas do jeito que fariam fora dela. A curva não é de conhecimento,
é de aceitação. Isso está catalogado em [75-armadilhas.md](75-armadilhas.md).

---

## 4. Rota de resgate — o que fazer se faltar um pré-requisito

| Está faltando | Não pare. Faça isto: |
|---|---|
| **Programação (qualquer)** | Vá pela trilha de **Administrador**. Ela é completa, empregável e não exige código. Leia `10`, `12`, `13`, `14`, `20`. Volte ao código depois. |
| **Java/OOP** | Faça 2 semanas de Java básico (classe, objeto, coleções, exceções) e volte. Apex é Java simplificado; não precisa de Spring, threads nem generics avançados. |
| **JavaScript** | Pule [16-lightning-web-components.md](16-lightning-web-components.md) por ora e use Flow para tela. Volte depois com JS moderno estudado. |
| **SQL** | Não estude SQL antes — estude SOQL direto em [12-modelo-de-dados.md](12-modelo-de-dados.md). É mais simples e você não pega vícios que não se aplicam. |
| **Git** | Comece pelo Developer Console no navegador (sem Git). Adote Git ao chegar em [18-devops-e-alm.md](18-devops-e-alm.md) — mas adote, não pule. |
| **Terminal** | Use a interface do VS Code (paleta de comandos `Ctrl+Shift+P`) — ela roda a CLI para você. Aprenda o terminal depois. |
| **Máquina fraca / PC corporativo travado** | Use o ambiente web. Ver [03-instalacao.md](03-instalacao.md) §1 "Sem instalar nada". |
| **Inglês** | Use a doc em pt-BR onde existe + tradutor de página. Priorize [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) §2 (cursos em português). |
| **Tempo** | Corte escopo, não profundidade: escolha **uma** trilha (admin **ou** dev) e vá até o fim. Meio admin + meio dev não emprega ninguém. |

---

## 5. Checklist antes de ir para o `03`

- [ ] Tenho um e-mail que controlo e não vou perder.
- [ ] Sei qual trilha vou seguir: administrador, desenvolvedor, ou "só entender".
- [ ] Tenho 5 GB livres em disco (ou decidi usar o ambiente web).
- [ ] Tenho ~1 hora sem interrupção para a instalação.
- [ ] Aceito que a plataforma me obrigará a fazer as coisas do jeito dela.

Se marcou tudo: **[03-instalacao.md](03-instalacao.md)**.

---

## Autoteste

1. Quais três conhecimentos são indispensáveis para a trilha de desenvolvedor e dispensáveis para a de administrador?
2. Por que saber SQL avançado pode atrapalhar no começo?
3. Qual é o tempo realista, com 10 h/semana e partindo do zero, para passar na certificação de Administrador?
4. Por que o e-mail usado na org Developer Edition merece cuidado especial?
5. Você não sabe programar e precisa começar hoje. Qual é a sua rota?
6. Qual é o erro de instalação nº 1 de quem usa VS Code pela primeira vez, e qual sua causa?
7. Segundo este arquivo, qual é a parte mais difícil da curva de aprendizado — e por quê?
