# `portao` — projeto-modelo

**Um portão de verificação para código gerado por IA.**
Pequeno, inteiro, executável, testado. Zero dependências.

**Nível:** intermediário · **Escrito em:** 20/08/2026
**Verificado em:** Python 3.10.12, Ubuntu 22.04.5 LTS — **49/49 testes passando**

---

## Por que este projeto existe

O curso inteiro defende uma tese:

> A geração de código virou commodity. **A verificação virou o gargalo** — e a
> única verificação que escala é a automática.

Um projeto-modelo que fosse "uma API de tarefas com IA" ensinaria a usar a
ferramenta. Este ensina **a coisa que a ferramenta não faz por você**: decidir,
mecanicamente, se uma mudança pode entrar.

O `portao` recebe um *diff* e responde uma pergunta binária: **entra ou não
entra?** Ele é deliberadamente burro — não entende o código, não julga
arquitetura, não opina. Ele verifica cinco propriedades que erram de forma
previsível quando quem escreveu foi uma máquina.

Ele é indiferente à origem do *diff*. Isso é proposital: um portão que só vale
para código de IA é um portão que trata humanos como confiáveis, e isso nunca
foi verdade.

---

## Pré-requisitos

| Item | Versão | Como conferir |
|---|---|---|
| Python | 3.10 ou superior | `python3 --version` |
| Git | qualquer | `git --version` |

Nada mais. Sem `pip install`, sem ambiente virtual, sem lockfile.

> **Por que zero dependências, e não é preciosismo:** este programa existe para
> vigiar a entrada de dependências. Uma ferramenta de segurança de cadeia de
> suprimentos que arrasta 40 pacotes transitivos é uma piada com o próprio
> propósito. É também o que permite rodá-lo em qualquer container mínimo, dentro
> do CI, sem etapa de instalação — que é justamente o passo que ele vigia.

---

## Rodar em 60 segundos

```bash
cd 07-projeto-modelo
```

```bash
python3 run_tests.py
```

Saída esperada:

```
.................................................
----------------------------------------------------------------------
Ran 49 tests in 0.054s

OK
```

Agora rode o portão sobre um *diff* limpo:

```bash
python3 -m portao --diff exemplos/bom.diff --sem-cor
```

```
════════════════════════════════════════════════════════════════════════
PORTÃO DE VERIFICAÇÃO
════════════════════════════════════════════════════════════════════════
APROVADO escopo
APROVADO tamanho
APROVADO segredos
APROVADO pacotes
APROVADO criterios
  ! (testes) — CA-99 citado em teste mas ausente da especificação
      critério removido da espec ou identificador digitado errado
────────────────────────────────────────────────────────────────────────
APROVADO — 0 bloqueios, 1 aviso(s)
════════════════════════════════════════════════════════════════════════
```

```bash
echo $?
# esperado: 0
```

E sobre um *diff* que um agente mal supervisionado poderia produzir:

```bash
python3 -m portao --diff exemplos/ruim.diff --sem-cor
```

```
════════════════════════════════════════════════════════════════════════
PORTÃO DE VERIFICAÇÃO
════════════════════════════════════════════════════════════════════════
REPROVADO escopo
  ✗ tests/test_tamanho.py — arquivo de teste alterado
      o teste é o critério; alterá-lo para fazer o código passar destrói a
      evidência. Use --testes-editaveis quando a tarefa FOR escrever teste.
  ✗ requirements.txt — fora do escopo permitido
      permitido: portao/**, tests/**, exemplos/**, *.md, *.json, *.py
APROVADO tamanho
REPROVADO segredos
  ✗ config/producao.py:2 — possível chave da Anthropic em linha adicionada
      rotacione a credencial ANTES de remover do diff
  ✗ config/producao.py:3 — possível URL com senha em linha adicionada
      rotacione a credencial ANTES de remover do diff
REPROVADO pacotes
  ✗ requirements.txt:2 — dependência nova não aprovada: starlette-reverse-proxy (pypi)
      confirme que o pacote existe e é o que você espera, e então acrescente a
      dependencias_permitidas
APROVADO criterios
  ! (testes) — CA-99 citado em teste mas ausente da especificação
      critério removido da espec ou identificador digitado errado
────────────────────────────────────────────────────────────────────────
REPROVADO — 5 bloqueio(s), 1 aviso(s)
════════════════════════════════════════════════════════════════════════
```

```bash
echo $?
# esperado: 1
```

O `exemplos/ruim.diff` foi construído a partir de falhas reais e recorrentes:
o agente **editou o teste** para fazer passar, **inventou um pacote**
(`starlette-reverse-proxy`, um dos nomes citados na literatura sobre
*slopsquatting*), e **colou credenciais** num arquivo de configuração.

---

## Uso no dia a dia

```bash
# antes de commitar
git add -p
python3 -m portao --staged
```

```bash
# sobre a branch inteira
git diff main...HEAD | python3 -m portao
```

```bash
# só uma regra
python3 -m portao segredos --staged
```

```bash
# com verificação de existência de pacote na rede
python3 -m portao pacotes --staged --online
```

```bash
# saída para máquina
python3 -m portao --staged --formato json
```

### Como gancho de pré-commit

```bash
cat > .git/hooks/pre-commit <<'EOF'
#!/usr/bin/env bash
exec python3 -m portao --staged --sem-cor
EOF
chmod +x .git/hooks/pre-commit
```

### No CI (GitHub Actions)

```yaml
- uses: actions/setup-python@v6
  with:
    python-version: '3.12'
- name: Portão de verificação
  run: |
    git fetch origin ${{ github.base_ref }}
    git diff origin/${{ github.base_ref }}...HEAD \
      | python3 -m portao --sem-cor --online
```

### Opções

| Opção | O que faz |
|---|---|
| `--diff ARQUIVO` | Lê o *diff* de um arquivo em vez do git |
| `--staged` | Usa `git diff --cached` |
| `--base REF` | Base para `git diff` (padrão `HEAD`) |
| `--config CAMINHO` | Configuração (padrão `portao.json`) |
| `--raiz CAMINHO` | Raiz do repositório |
| `--formato texto\|json` | Formato do relatório |
| `--sem-cor` | Sem códigos ANSI (para log e CI) |
| `--testes-editaveis` | Permite alterar teste — use quando a tarefa **for** escrever teste |
| `--online` | Consulta PyPI/npm para checar existência de pacote |

**Códigos de saída:** `0` aprovado · `1` reprovado · `2` erro de uso ou
configuração.

Sem argumento de regra, roda todas. Com um ou mais nomes
(`escopo tamanho segredos pacotes criterios`), roda só aquelas.

---

## Estrutura de pastas

```
07-projeto-modelo/
├── README.md                   este arquivo
├── ESPEC.md                    a especificação, com os critérios CA-01..CA-12
├── portao.json                 configuração deste próprio repositório
├── run_tests.py                executor de testes (unittest, zero deps)
│
├── portao/
│   ├── __init__.py             versão
│   ├── __main__.py             ponto de entrada: `python3 -m portao`
│   ├── cli.py                  argumentos, orquestração, códigos de saída
│   ├── config.py               configuração com padrões e validação
│   ├── diff.py                 leitor de unified diff
│   ├── modelo.py               Achado, Resultado, Severidade
│   ├── relatorio.py            apresentação (texto e JSON)
│   └── regras/
│       ├── escopo.py           tocou só no que devia?
│       ├── tamanho.py          cabe numa revisão humana?
│       ├── segredos.py         vazou credencial?
│       ├── pacotes.py          dependência nova ou alucinada?
│       └── criterios.py        todo critério tem teste?
│
├── tests/                      49 testes; cada um cita o CA que cobre
└── exemplos/
    ├── bom.diff                passa em tudo
    └── ruim.diff               três falhas reais de agente
```

---

## O que cada decisão de projeto ensina

Esta seção é o motivo de o projeto existir. Cada escolha aqui responde a um
princípio do curso.

### 1 · Uma regra é uma função `(Diff, Config) → Resultado`

Contrato estreito, sem estado, sem I/O (exceto `--online`, isolado numa função
só). Consequências:

- Acrescentar regra nova **não toca em nenhuma regra existente**.
- Toda regra é testável sem sistema de arquivos, sem rede, sem git.
- O agente que for adicionar a sexta regra tem um molde óbvio a seguir — e
  código com molde óbvio é código que agente acerta de primeira.

**Lição do curso:** [19-arquitetura-para-maquina](../19-arquitetura-para-maquina.md)
— arquitetura legível por agente não é um estilo novo; é bom design levado a
sério, porque o agente é o leitor mais literal que o seu código já teve.

### 2 · Duas severidades, não uma

`BLOQUEIA` reprova; `AVISA` aparece e deixa passar.

Um portão que reprova por tudo é desativado na primeira semana — e aí não há
portão nenhum. **A calibração da severidade é a decisão de projeto mais
importante de qualquer ferramenta de verificação**, e a que mais se erra.

Regra prática usada aqui: **bloqueia o que é objetivo e caro** (segredo, pacote
não aprovado, teste alterado); **avisa o que é heurístico** (entropia alta,
arquivo grande).

**Lição:** [75-armadilhas](../75-armadilhas.md), sobre fadiga de alerta.

### 3 · Só linhas **adicionadas** são examinadas em busca de segredo

Um `git diff` que **remove** uma chave não deve reprovar — senão você não
consegue nem consertar o problema. Parece óbvio; quase toda implementação
ingênua erra isso, porque varre o arquivo inteiro em vez do *diff*.

Há um teste dedicado a esse caso (`test_ca07_linha_removida_nao_conta`).

### 4 · Falha de rede **nunca** bloqueia

Em `pacotes.py`, `existe_no_registro` devolve `None` quando a rede falha, e
`None` vira aviso, não bloqueio.

Por quê: uma ferramenta de verificação que quebra o fluxo por causa de um
*timeout* é a primeira coisa a ser removida do CI. **A ferramenta precisa
sobreviver à quinta-feira ruim**, senão não está lá na sexta.

### 5 · O escape existe, é explícito e fica visível no diff

`# portao: ignora-segredo` desliga a regra naquela linha.

Toda regra sem escape acaba desligada inteira. Melhor uma exceção anotada, que
aparece no *diff* e que um revisor humano vê, do que a regra apagada do
`portao.json` numa sexta-feira à noite.

### 6 · Modo offline é o padrão

O portão não toca na rede a menos que você peça `--online`. Há um teste que
**prova** isso (`test_ca09_offline_nao_toca_a_rede`), substituindo a função de
rede por um espião e verificando que ela nunca foi chamada.

Por quê: comportamento determinístico é pré-requisito de confiança. E uma
ferramenta que faz requisição silenciosa é uma ferramenta que ninguém instala em
ambiente sério.

### 7 · A regra `criterios` fecha o laço do curso inteiro

Ela lê `ESPEC.md`, extrai os identificadores `CA-NN`, e verifica se **cada um é
citado por algum arquivo de teste**. Rastreabilidade por convenção de texto — a
mesma técnica usada em software aeroespacial há décadas, sem ferramenta nenhuma.

É a única regra que verifica **intenção** em vez de forma. E é a que transforma
a especificação de documento morto em artefato executável.

Este repositório se submete à própria regra: os 12 critérios do `ESPEC.md` são
citados nos testes, e o portão confirma.

### 8 · A configuração tem padrão para tudo, e rejeita chave desconhecida

Sem `portao.json`, ele roda com padrões conservadores. Com `portao.json`
contendo uma chave que ele não conhece, ele **falha** em vez de ignorar.

Por quê: silêncio diante de configuração errada é a fonte nº 1 de "achei que
estava protegido". Um `max_arquivo: 5` (singular, digitado errado) que é
silenciosamente ignorado é pior que nenhuma configuração.

### 9 · Tratamento de erro que projetos reais têm e tutoriais omitem

- Arquivo de *diff* inexistente → código 2, mensagem clara.
- Nome de regra errado → código 2, lista o nome errado.
- Configuração inválida → código 2, nomeia o campo.
- `git` falhando → código 2, mostra o `stderr` do git.
- *Diff* vazio → aprovado, sem exceção.
- Arquivo binário ou ilegível na varredura de critérios → ignorado, sem quebrar.

---

## Limitações conhecidas (ditas por honestidade, não escondidas)

Nenhuma ferramenta é honesta sem esta seção.

| Limitação | Consequência | O que fazer |
|---|---|---|
| `fnmatch` faz `*` cruzar barras | `*.py` em `escopo_permitido` casa com `config/producao.py`, não só com arquivos na raiz | Prefira caminhos explícitos (`portao/**`) e teste sua configuração |
| Detecção de segredo é por padrão e entropia | Não pega credencial de formato novo; dá falso positivo em *hash* longo | Complemente com `gitleaks` ou `trufflehog` no CI |
| `criterios` é busca textual | `CA-99` dentro de uma *fixture* de teste conta como citação — é exatamente o aviso que aparece na saída acima | Por isso órfão é **aviso**, não bloqueio |
| Extração de dependência é heurística | Pode não pegar `pyproject.toml` com formatação incomum | Prefira `requirements.txt` ou revise manualmente |
| Não entende o código | Não pega lógica errada, design ruim, nem regra de negócio violada | **É esse o seu trabalho.** O portão libera o seu tempo para ele |

> A última linha é a mais importante do projeto. **O portão não substitui a
> revisão humana — ele elimina da revisão humana tudo que uma máquina consegue
> conferir**, para que a sua atenção sobre no que só você consegue julgar.

---

## Exercícios

Progressivos. Cada um exercita um conceito diferente do curso.

1. **Fácil.** Acrescente à regra de segredos o padrão de chave do Stripe
   (`sk_live_` seguido de 24+ caracteres alfanuméricos). Escreva o teste
   **primeiro**, veja falhar, então implemente.
2. **Fácil.** Faça o relatório mostrar o total de linhas adicionadas e removidas
   por arquivo. Sem tocar em nenhuma regra — se você precisou tocar, a separação
   entre lógica e apresentação está errada.
3. **Médio.** Crie a regra `comentarios`: reprova se o *diff* adicionar
   `TODO`, `FIXME` ou `XXX` sem um identificador de *issue* ao lado.
4. **Médio.** Faça `--online` consultar em paralelo (`concurrent.futures`) e
   meça a diferença com 10 dependências. Mantenha os 49 testes passando.
5. **Difícil.** Crie a regra `cobertura`: recebe um relatório de cobertura
   (`coverage.json`) e reprova se alguma **linha adicionada no diff** não
   estiver coberta. Esta é a regra mais valiosa que existe para código de
   agente, e a que exige mais cuidado para não virar ruído.
6. **Difícil.** Rode o portão sobre um *diff* que você mesmo gerou pedindo algo
   grande a um agente. Ele reprova? Se aprovou tudo e o código estava ruim,
   **qual regra faltou?** Escreva-a.

---

## Autoteste

1. Por que este projeto tem zero dependências, e por que isso é argumento e não
   preciosismo?
2. Por que existem duas severidades? O que acontece com um portão que só bloqueia?
3. Por que a varredura de segredos só olha linhas adicionadas?
4. Por que falha de rede não pode bloquear o portão?
5. Por que o escape `portao: ignora-segredo` é melhor que não ter escape?
6. Como o teste `test_ca09_offline_nao_toca_a_rede` prova o que promete?
7. O que a regra `criterios` verifica que nenhuma das outras verifica?
8. Por que configuração com chave desconhecida deve falhar em vez de ser ignorada?
9. Cite duas limitações do projeto e o que fazer diante de cada uma.
10. Complete: "o portão não substitui a revisão humana, ele ______".

---

**Volta para:** [00-MAPA](../00-MAPA.md) ·
**Próximo do curso:** [10-fundamentos](../10-fundamentos.md)
