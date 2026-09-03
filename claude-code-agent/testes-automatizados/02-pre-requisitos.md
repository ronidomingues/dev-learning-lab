# 02 · Pré-requisitos

`Nível: iniciante` · `Última atualização: 12/08/2026`

---

## 1. Conhecimento

### 1.1 Indispensável

Sem isto, o material não faz sentido. Não é vergonha nenhuma faltar — a coluna "onde
aprender" existe justamente para isso.

| O que você precisa saber | Como saber se sabe | Onde aprender |
|---|---|---|
| **Escrever uma função** em Python **ou** JavaScript | Você consegue escrever uma função que recebe dois números e devolve a soma, sem consultar nada. | [Curso em Vídeo — Python 3](https://www.cursoemvideo.com/curso/python-3-mundo-1/) (PT, grátis) · [javascript.info](https://javascript.info/) (EN, grátis) |
| **Chamar uma função** e usar o retorno | Você entende a diferença entre `f` e `f()`. | idem |
| **Tipos básicos**: número, texto, lista/array, dicionário/objeto | Você sabe o que é `[1, 2, 3]` e o que é `{"a": 1}`. | idem |
| **`if` / `for`** | Você lê um laço sem tropeçar. | idem |
| **Usar o terminal** | Você consegue `cd` até uma pasta e rodar um comando. | [Comandos de terminal, básico](https://ubuntu.com/tutorials/command-line-for-beginners) (EN) |
| **Instalar um programa** no seu sistema | Você já instalou algo pelo terminal ou pelo instalador oficial. | [03-instalacao.md](03-instalacao.md) cobre tudo passo a passo |

> **Não é preciso saber programar bem.** Testes são, ironicamente, uma das melhores formas
> de *aprender* a programar bem. Você só precisa conseguir escrever e rodar código.

### 1.2 Ajuda muito (mas dá para começar sem)

| O que | Por que ajuda | Onde aprender |
|---|---|---|
| **Git** | O ciclo real é: muda → testa → commita. E CI só existe com Git. | [Pro Git, em português, grátis](https://git-scm.com/book/pt-br/v2) |
| **Funções e classes** (POO básica) | Metade do material fala de objetos, dependências e injeção. | qualquer curso da linguagem |
| **Exceções** (`try/except`, `try/catch`) | Testar o caminho de erro é metade do valor de uma suíte. | idem |
| **SQL básico** | O projeto-modelo usa SQLite para o teste de integração. | [`postgresql/`](../postgresql/00-MAPA.md) desta mesma pasta |
| **HTTP básico** | Testes de API são o caso de produção mais comum. | [`apis/`](../apis/00-MAPA.md) desta mesma pasta |
| **Inglês de leitura** | A maior parte da documentação e das mensagens de erro está em inglês. | — |

### 1.3 Não é pré-requisito, ao contrário do que dizem

Desfazendo mitos que afastam iniciante:

- **Matemática.** Não precisa. Nem para teste de propriedades — a intuição basta.
- **Experiência prévia com "QA".** Este material não pressupõe nenhuma.
- **Saber TDD.** TDD é ensinado *aqui* ([15-tdd.md](15-tdd.md)); não é entrada, é conteúdo.
- **Ter um projeto grande.** O projeto-modelo já está pronto e roda.
- **Saber as duas linguagens.** Escolha uma. O material foi escrito para que Python e
  JavaScript sejam intercambiáveis, e as tabelas de tradução permitem trocar depois.

## 2. Ambiente

### 2.1 Software

Escolha **uma** trilha. Você pode fazer a outra depois — o esforço de migrar, com este
material, é de umas duas horas.

| | Trilha Python | Trilha JavaScript |
|---|---|---|
| Runtime | Python **3.10 ou superior** (recomendado 3.13 ou 3.14) | Node.js **20 ou superior** (recomendado 24 LTS) |
| Corredor de testes | `pytest` 8 ou 9 | `node:test` (embutido, ≥ 20) ou Vitest 4 |
| Editor | qualquer um; VS Code tem a melhor integração | idem |
| Instalar? | sim, o pytest | **não**, o `node:test` já vem junto |

Detalhe: a versão **mínima** para acompanhar o projeto-modelo é Python 3.10 (usa `match`) e
Node 24 (usa `import.meta.main`, `node:sqlite` sem flag e `using`). Versões mais antigas
funcionam para 90 % do material; o que quebra está anotado no
[03-instalacao.md](03-instalacao.md).

### 2.2 Sistema operacional

Qualquer um. Linux, macOS e Windows estão cobertos passo a passo no
[03-instalacao.md](03-instalacao.md). No Windows, a recomendação é **WSL2** — mas o caminho
nativo também está documentado, com as diferenças reais.

### 2.3 Hardware

Testes automatizados são a área de software com o requisito mais modesto que existe.

| Recurso | Mínimo | Confortável |
|---|---|---|
| RAM | 2 GB | 8 GB |
| Disco livre | 500 MB (Python + pytest) · 100 MB (Node puro) · +300 MB se usar Vitest | 5 GB |
| Processador | qualquer coisa dos últimos 15 anos | mais núcleos = suíte paralela mais rápida |
| Internet | só para instalar | — |

Exceções, para você não ser pego de surpresa mais adiante:

- **Playwright / Selenium** (testes de navegador) baixam navegadores completos: ~500 MB a
  1 GB, e pedem bem mais RAM.
- **Testcontainers** (banco de dados descartável em container) exige Docker e alguns GB.

Nada disso é necessário para os blocos A, B e C.

### 2.4 Conta em serviço

**Nenhuma é necessária** para todo o material principal. Detalhamento em
[80-custos-e-licencas.md](80-custos-e-licencas.md).

Ficam opcionais:

| Serviço | Para quê | Precisa de cartão? |
|---|---|---|
| GitHub | integração contínua ([21-ci-e-automacao.md](21-ci-e-automacao.md)) | não, camada gratuita generosa |
| Codecov / Coveralls | painel de cobertura | não, grátis para repositório público |

## 3. Tempo realista até cada nível

Números honestos, para alguém com os pré-requisitos indispensáveis, estudando com as mãos
no teclado. Se você só ler, multiplique por 0,3 o resultado — e não vai aprender.

| Nível | O que você consegue fazer | Tempo focado | Em semanas, a 1 h/dia útil |
|---|---|---|---|
| **Primeira luz verde** | rodar um teste seu | **40 min** | dia 1 |
| **Operacional** | testar suas funções puras, usar `parametrize`/`it.each`, ler o relatório de falha | 8–12 h | 2 a 3 semanas |
| **Autônomo** | usar fixtures e dublês, testar código que fala com banco e rede, separar unitário de integração | 30–45 h | 2 meses |
| **Fluente** | projetar para testabilidade, TDD com naturalidade, montar CI, decidir o que **não** testar | 100–150 h | 5 a 7 meses |
| **Referência no time** | resolver suíte lenta e *flaky*, teste de propriedades e mutação, definir estratégia | 400 h+ e **projetos reais** | 1,5 a 3 anos |
| **Pesquisa** | ler e produzir artigo sobre adequação de critérios, geração automática, oráculos | anos | — |

**Onde quase todo mundo trava:** entre "operacional" e "autônomo", no momento em que o
código a testar tem banco, data ou rede no meio. A resposta desse curso a esse ponto é o
capítulo [20-testabilidade-e-design.md](20-testabilidade-e-design.md), e é o mais importante
do material inteiro.

**Aviso contra otimismo:** "aprender pytest" leva um fim de semana. "Aprender a testar" leva
anos, porque a parte difícil não é a ferramenta — é decidir **o que** verificar e **como**
desenhar o código para que isso seja possível.

## 4. Rota de resgate

Se algum pré-requisito faltar, não pare. Faça isto:

### 4.1 "Não sei programar em nenhuma das duas linguagens"

Faça **8 a 12 horas** de uma delas — só até conseguir escrever uma função com `if` e `for`.
Não precisa mais que isso. Sugestões gratuitas:

- **Python, em português:** [Curso em Vídeo, Python 3 Mundo 1](https://www.cursoemvideo.com/curso/python-3-mundo-1/)
- **Python, em inglês:** [Python for Everybody](https://www.py4e.com/) (Univ. de Michigan, grátis)
- **JavaScript, em português:** [Curso em Vídeo, JavaScript](https://www.cursoemvideo.com/curso/javascript/)
- **JavaScript, em inglês:** [javascript.info](https://javascript.info/)

Depois volte para o [04-como-comecar.md](04-como-comecar.md).

### 4.2 "Não consigo instalar nada nesta máquina"

Vá direto para a seção **"Alternativa sem instalar nada"** do
[03-instalacao.md](03-instalacao.md). Você consegue rodar Python **e** JavaScript com testes
inteiramente no navegador, de graça, sem cadastro em alguns casos. Comece hoje pelo
navegador e instale quando puder.

### 4.3 "Não sei usar o terminal"

Você só precisa de quatro comandos para todo este material:

```bash
cd nome-da-pasta      # entrar numa pasta
cd ..                 # voltar uma pasta
ls                    # listar o que tem aqui (no Windows nativo: dir)
pwd                   # onde estou? (no Windows nativo: cd sem argumento)
```

Aprenda esses quatro e siga. O resto você aprende no caminho.

### 4.4 "Meu código no trabalho é legado e não dá para testar"

Esse é o caso mais comum do mundo real, e tem capítulo próprio:
[20-testabilidade-e-design.md](20-testabilidade-e-design.md), seção "Código legado". Resumo
do resumo: não tente testar tudo. Comece por um **teste de caracterização** — um teste que
apenas registra o que o código faz hoje, certo ou errado — e use-o como rede antes de mexer.

### 4.5 "Meu time não quer escrever testes"

Não é um problema técnico e este material não vai resolvê-lo sozinho. O que costuma
funcionar, em ordem:

1. escreva teste só para o **próximo bug** que aparecer, mostrando que ele não volta;
2. deixe a suíte **rápida**, senão ninguém roda;
3. não pregue; mostre o tempo economizado numa mudança arriscada;
4. só depois disso proponha regra de cobertura mínima — e proponha baixa.

Argumentos que **não** funcionam: cobertura como meta, comparação com outro time, e citar
autoridade. Isso está detalhado em [75-armadilhas.md](75-armadilhas.md).

## 5. Checklist antes de seguir

Marque tudo antes de ir para o [03-instalacao.md](03-instalacao.md):

- [ ] Escolhi uma trilha: Python **ou** JavaScript.
- [ ] Consigo escrever e rodar uma função na linguagem escolhida.
- [ ] Consigo abrir um terminal e navegar até uma pasta.
- [ ] Tenho ~500 MB de disco livre.
- [ ] Reservei uns 40 minutos seguidos para a primeira luz verde.

Se algum item ficou vazio, a seção 4 tem a saída.

---

## Autoteste

1. Qual é o único pré-requisito de conhecimento realmente indispensável?
2. Você precisa saber TDD antes de começar? Por quê?
3. Qual a versão mínima de Python e de Node para o projeto-modelo, e o que quebra abaixo dela?
4. Quanto disco o caminho JavaScript puro consome, e por que tão pouco?
5. Quanto tempo focado, realisticamente, até você conseguir testar código que fala com um banco de dados?
6. Onde a maioria das pessoas trava, e qual capítulo responde a isso?
7. Você não consegue instalar nada na máquina do trabalho. Qual é o plano?
8. Cite dois argumentos que **não** funcionam para convencer um time a testar.
