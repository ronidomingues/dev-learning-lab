# 2 · Pré-requisitos

**Nível:** iniciante · **Escrito em:** 20/08/2026

---

Este curso é sobre **como programar bem com máquinas que programam**. Ele não
ensina a programar do zero. Este arquivo diz, sem otimismo, o que você precisa
ter antes, onde conseguir, e o que fazer se faltar.

---

## Conhecimento indispensável

Sem isto, o material não funciona — você conseguirá ler, mas não conseguirá
julgar nada do que a IA produzir, que é o ponto inteiro do curso.

| # | Você precisa saber | Como testar se sabe | Onde aprender |
|---|---|---|---|
| 1 | **Programar em alguma linguagem** | Escrever, sem consultar nada, uma função que lê um arquivo de texto, conta as palavras e imprime as 5 mais frequentes | [CS50 (Harvard, legendado)](https://cs50.harvard.edu/x/) · [Curso em Vídeo — Python (Gustavo Guanabara)](https://www.cursoemvideo.com/curso/python-3-mundo-1/) |
| 2 | **Ler código que você não escreveu** | Abrir um projeto no GitHub que você nunca viu e explicar em 3 frases o que ele faz e por onde começa | Prática: clone um projeto pequeno e leia. Não há atalho. |
| 3 | **Linha de comando** | `cd`, `ls`, `grep`, cano (`\|`), redirecionamento `>`, variável de ambiente, código de saída (`$?`) | [MIT Missing Semester](https://missing.csail.mit.edu/) |
| 4 | **Git, de verdade** | `branch`, `commit`, `diff`, `rebase` vs. `merge`, resolver conflito, `git bisect` | [Pro Git em português (grátis)](https://git-scm.com/book/pt-br/v2) · [commits-assinados](../commits-assinados/00-MAPA.md) desta pasta |
| 5 | **Escrever e rodar um teste automatizado** | Escrever um teste que falha, fazer passar, e explicar por que ele prova algo | [testes-automatizados](../testes-automatizados/00-MAPA.md) desta pasta — **este é o pré-requisito mais importante do curso** |
| 6 | **Ler uma mensagem de erro até o fim** | Dado um *stack trace*, apontar a linha do *seu* código que causou | Prática |

### Por que o item 5 é o mais importante

Porque a única coisa que escala junto com a IA é a verificação automática.
Julgamento humano não escala: seu dia continua tendo 8 horas. Um teste roda
1.000 vezes por dia de graça.

Se você não sabe escrever um teste que prova algo, você vai ficar preso no
nível L2 da escala do [01](01-introducao-leigo.md) para sempre, porque a única
forma que sobra de conferir a máquina é ler tudo à mão — e ler tudo à mão anula
o ganho.

**Se você tiver que escolher um único pré-requisito para investir, escolha
teste.** É contraintuitivo e é a coisa mais rentável deste curso.

---

## Conhecimento que ajuda muito (mas dá para começar sem)

| Você sabendo | O que destrava |
|---|---|
| **Tipagem estática** (TypeScript, tipos em Python, Go, Java) | O compilador vira um segundo revisor gratuito do código da IA. Ganho grande e barato. |
| **Como funciona um LLM por dentro** (token, janela de contexto, amostragem) | Você para de brigar com o modelo e passa a explorar o mecanismo. Coberto no [12](12-o-modelo-por-dentro.md); [engenharia-de-prompt](../engenharia-de-prompt/00-MAPA.md) aprofunda. |
| **CI/CD** (integração contínua) | Permite pôr o portão de verificação onde ele importa: entre o agente e a `main`. Ver [21](21-ci-cd-e-agentes-em-producao.md). |
| **Docker** | Isolar o agente do seu sistema de arquivos e das suas credenciais. Ver [docker](../docker/00-MAPA.md) desta pasta. |
| **Segurança de aplicação** | Injeção de prompt indireta é injeção. Quem já entende SQL injection entende em 10 minutos. Ver [ethical-hacking](../ethical-hacking/00-MAPA.md). |
| **Inglês de leitura** | A documentação primária muda semanalmente e quase nunca é traduzida a tempo. Não precisa falar; precisa ler. |
| **Revisão de código** (já ter revisado PR de outra pessoa) | O [18](18-revisao-de-codigo-gerado.md) parte daí. |

---

## Conhecimento explicitamente **não** exigido

Para evitar que você adie o curso à toa:

- **Matemática de aprendizado de máquina.** Você não vai treinar modelo nenhum.
  Álgebra linear, cálculo, estatística — nada disso é necessário aqui.
- **Saber treinar ou ajustar (*fine-tune*) modelos.** Assunto diferente.
- **Python especificamente.** Os exemplos usam Python e JavaScript porque é
  preciso escolher; os conceitos são independentes de linguagem.
- **Já ter usado alguma ferramenta de IA.** O [03](03-instalacao.md) começa do
  zero absoluto.

---

## Ambiente: o que você precisa ter

### Hardware

| Item | Mínimo | Recomendado | Por quê |
|---|---|---|---|
| RAM | 8 GB | 16 GB+ | O trabalho pesado roda na nuvem; a RAM é para o seu editor, containers e testes em paralelo |
| Disco livre | 10 GB | 50 GB+ | Ferramentas, runtimes, imagens de container, *worktrees* do Git |
| CPU | qualquer x86-64 ou ARM64 dos últimos 8 anos | — | Nada disso é intensivo em CPU local |
| Internet | estável, ~5 Mbps | — | Cada passo do agente é uma ida e volta à rede. Latência alta atrapalha mais que banda baixa |
| GPU | **não é necessária** | — | Só se você quiser rodar modelo local (ver [80](80-custos-e-licencas.md)) |

**Rodar modelo local não é pré-requisito e, sendo franco, em agosto de 2026
ainda não é competitivo para trabalho agêntico sério em hardware de consumo.**
Detalhes e a exceção (privacidade absoluta) estão no [80](80-custos-e-licencas.md).

### Sistema operacional

Qualquer um dos três. Ordem de conforto para trabalho agêntico, na minha
experiência:

1. **Linux** — melhor. Tudo que o agente executa é comando POSIX.
2. **macOS** — praticamente empatado com Linux.
3. **Windows com WSL2** — funciona bem, e é o caminho recomendado no Windows.
4. **Windows nativo (PowerShell)** — funciona, mas metade das instruções da
   internet vai falhar e o agente vai propor comando de shell errado com
   frequência.

### Contas

| Serviço | Necessário? | Cartão de crédito? | Camada gratuita |
|---|---|---|---|
| **GitHub** | Sim, na prática | Não | Sim. GitHub Copilot Free: 2.000 *completions*/mês |
| **Claude (Anthropic)** | Um provedor é preciso | Não no plano Free | Free: uso básico, Claude Code incluído com limites baixos |
| **OpenAI** | Alternativa | Sim, para API | Chat gratuito; API é pré-paga |
| **Google (Gemini)** | Alternativa | Não para Gemini CLI | Gemini CLI tem camada gratuita generosa |

Preços exatos, com data de consulta, no [80-custos-e-licencas](80-custos-e-licencas.md).

> **Aviso a quem está no Brasil:** as cobranças são em dólar, entram no cartão
> com IOF e *spread* cambial. Um plano de US$ 20 sai perto de R$ 120–130
> dependendo do câmbio e do banco. Não é preço de aplicativo; é preço de
> ferramenta profissional. Trate como tal ao decidir.

---

## Tempo realista até cada nível

Honesto, não otimista. Assume que os pré-requisitos indispensáveis já estão de
pé e que você já programa.

| Nível (escala do [01](01-introducao-leigo.md)) | Tempo | O que você consegue fazer |
|---|---|---|
| **L1** — autocompletar | 1 hora | Instalar, aceitar sugestões, sentir o ritmo |
| **L2** — conversar | 1 semana de uso | Perguntar bem, avaliar resposta, adaptar |
| **L3** — delegar com verificação | **2 a 4 meses de uso diário** | Delegar tarefa de meio dia e confiar no portão, não na leitura |
| **L4** — projetar o ambiente | **6 a 12 meses** | Repositório onde agentes acertam de primeira; instrumentação e métrica |
| **L5** — operar em escala | **1 a 2 anos, e depende da organização** | Vários agentes, mudança de processo do time |

### Por que L3 leva meses e não semanas

Porque o que você está construindo não é habilidade de prompt — é
**calibração**. Calibração é saber, **antes** de mandar, se a tarefa vai voltar
boa. Isso só se aprende por acumulação de casos: você precisa ter sido queimado
o suficiente para desenvolver intuição sobre onde o modelo mente.

Não dá para acelerar lendo. Dá para acelerar **anotando**: mantenha um arquivo
de "coisas que a IA errou no meu sistema". Em três meses ele vale mais que
qualquer curso — inclusive este.

### Quanto tempo para ler este material

| Percurso | Tempo |
|---|---|
| Só o [01](01-introducao-leigo.md) | 25 min |
| Bloco A inteiro, sem fazer o projeto | 4 h |
| Bloco A com o projeto rodando | 1 dia |
| Curso completo, lendo | ~20 h |
| Curso completo, com os laboratórios do [70](70-pratica.md) | ~60 h |

---

## Rota de resgate — se faltar um pré-requisito

Não desista do curso. Faça o desvio mínimo.

### Falta o item 1 (não sabe programar)

**Pare aqui.** Sério. Vá fazer o CS50 ou o Curso em Vídeo até conseguir escrever
o exercício do teste 1 sem ajuda. Estimativa realista: **3 a 6 meses**, 1 h/dia.

Ironia útil: você pode usar IA para *aprender* a programar (pedindo explicação,
não solução) e isso funciona muito bem. Mas pedir a solução para não aprender é
a forma mais rápida de garantir que você nunca vá para L3.

### Falta o item 5 (não sabe testar)

Desvio de **1 semana**. Leia
[testes-automatizados](../testes-automatizados/00-MAPA.md), o Bloco A e o
`13-teste-unitario-a-fundo.md`. Depois volte. É o desvio com maior retorno de
todo este curso.

### Falta o item 3 ou 4 (shell ou Git fracos)

Desvio de **2 a 3 dias**. Missing Semester (aulas 1, 2, 5 e 6) e Pro Git
(capítulos 2 e 3). Você pode fazer isso *usando* IA como tutor — é um dos
melhores usos dela.

### Falta dinheiro

Caminho 100% gratuito, viável e sem cartão de crédito:

1. **GitHub Copilot Free** — 2.000 *completions*/mês, sem cartão.
2. **Gemini CLI** — camada gratuita com login Google.
3. **Claude Free** — Claude Code incluído com limite baixo; dá para os
   laboratórios menores.
4. **GitHub Codespaces** — 60 h/mês grátis na conta pessoal; ambiente pronto no
   navegador, sem instalar nada.
5. Se você for estudante: **GitHub Student Developer Pack** dá Copilot Pro
   gratuito enquanto durar a matrícula.

O [80](80-custos-e-licencas.md) traz o roteiro do gratuito com os limites de
cada um e onde exatamente eles acabam.

### Falta máquina

Use **GitHub Codespaces** (grátis até 60 h/mês) ou **Google Cloud Shell**
(gratuito, com um editor no navegador). O [03](03-instalacao.md) tem a seção
"sem instalar nada" logo no começo, exatamente para este caso.

### Falta inglês

Dá para começar. O material aqui é em português e os cursos em PT estão listados
no [85](85-cursos-e-certificacoes.md). Mas invista em **inglês de leitura
técnica** em paralelo — o vocabulário é pequeno (umas 500 palavras cobrem 95% da
documentação) e a defasagem da tradução, neste assunto, é de meses.

---

## Uma advertência sobre pré-requisito invisível

Existe um pré-requisito que não é técnico e que derruba mais gente que todos os
outros: **disposição para desconfiar de algo que soa competente.**

Modelos de linguagem produzem texto com a cadência de quem sabe. Não há
hesitação, não há "acho que", não há a pausa que um colega humano faria antes de
chutar. Se você é do tipo que aceita afirmação bem formulada como evidência,
esta ferramenta vai te machucar de formas criativas.

O antídoto é mecânico, não emocional: **nunca aceite por leitura o que você pode
aceitar por execução.** Rodou? Passou? Cobre o caso que importa? Então entra.
Não rodou? Então é hipótese, não resultado — não importa quão bem escrita.

---

## Autoteste

1. Qual é o pré-requisito mais importante deste curso, e por que ele é
   contraintuitivo?
2. Por que julgamento humano não escala junto com a IA, e o que escala?
3. Você tem 8 GB de RAM e nenhuma GPU. Isso te impede de fazer o curso? Por quê?
4. Por que chegar ao L3 leva meses e não semanas? O que exatamente está sendo
   construído nesse tempo?
5. Cite três formas de fazer o curso inteiro gastando R$ 0,00.
6. Qual é o único pré-requisito que não é técnico, e qual é o antídoto mecânico
   para a sua falta?
7. Você não sabe escrever testes. Qual é a rota de resgate e quanto tempo ela
   leva?
8. Por que tipagem estática é listada como "ajuda muito" num curso sobre IA?

---

**Anterior:** [01-introducao-leigo](01-introducao-leigo.md) ·
**Próximo:** [03-instalacao](03-instalacao.md) — o manual de campo.
