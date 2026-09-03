# 07 · Projeto-modelo — **Projeto Ponte**

`Nível: iniciante → intermediário` · `Testado em Python 3.10.12 · Ubuntu 22.04.5 · 31/08/2026`

> **Nota de reinterpretação.** Inglês não é software, mas um "projeto-modelo" precisa **rodar**.
> Este é um sistema pessoal de estudo, completo e executável: dados reais, dois programas em
> Python (biblioteca padrão, zero dependências), 42 testes automatizados, e um currículo de
> 12 semanas que usa o resto do curso.
>
> **O que ele produz:** um baralho de 100 cartões pronto para importar no Anki, e um painel do
> seu progresso com sequência de dias, distribuição por habilidade e projeção até o nível-alvo.

---

## O que é

O "Projeto Ponte" é a ponte entre **saber o que fazer** (o resto deste curso) e **fazer todo dia**.
Ele resolve os três problemas que matam o estudo autodidata de idioma:

| Problema | Como o projeto resolve |
|---|---|
| "Não sei o que estudar hoje" | [plano-12-semanas.md](plano-12-semanas.md) diz, dia a dia |
| "Meus cartões do Anki são ruins" | `gerar_deck.py` produz cartões de frase (reconhecimento + produção), validados |
| "Não sei se estou progredindo" | `estudo.py` mede horas, constância e distribuição por habilidade |

---

## Pré-requisitos

| Item | Versão mínima | Verificar com |
|---|---|---|
| Python | 3.9 | `python3 --version` |
| Anki | 25.02 | `anki --version` |
| Nada mais | — | — |

Se algum faltar, veja [../03-instalacao.md](../03-instalacao.md).

---

## Como rodar — comandos exatos

```bash
cd 07-projeto-modelo
```

**1. Validar os dados sem escrever nada:**
```bash
python3 scripts/gerar_deck.py --dry-run
```

**2. Gerar os arquivos de importação:**
```bash
python3 scripts/gerar_deck.py
```
Saída real desta execução:
```
=== Projeto Ponte · geração de baralho ===
frases selecionadas : 50
cartões de reconhecimento: 50
cartões de produção (cloze): 50
total de cartões    : 100

por nível:
  A1:  10
  A2:  10
  B1:  16
  B2:  14

por assunto:
  apresentacao     4
  conectivos       4
  email            5
  entrevista       2
  narrativa        2
  opiniao          6
  passado          4
  pedido           3
  reuniao          6
  rotina           6
  tecnologia       5
  viagem           3

arquivos escritos
```

**3. Gerar só uma fatia (é assim que se usa no dia a dia):**
```bash
python3 scripts/gerar_deck.py --max-cefr A2                # só o básico
python3 scripts/gerar_deck.py --tag reuniao email          # só inglês de trabalho
python3 scripts/gerar_deck.py --tag tecnologia --out /tmp/x
```

**4. Importar no Anki:**
- `Arquivo → Importar` → `saida/anki-reconhecimento.tsv`
  → tipo de nota **Básico** · baralho `Ingles::Ponte` · separador **Tab**
  → campo 1 = Frente, campo 2 = Verso, campo 3 = **Tags**
- Repita com `saida/anki-producao.tsv`, escolhendo o tipo de nota **Cloze**
  → campo 1 = Texto, campo 2 = Extra, campo 3 = Tags

**5. Registrar o estudo do dia:**
```bash
python3 scripts/estudo.py registrar --min 45 --hab escuta vocabulario --nota "6 Minute English"
```

**6. Ver o painel:**
```bash
python3 scripts/estudo.py relatorio
```
Saída real, com os 14 dias de exemplo que acompanham o projeto:
```
=== Projeto Ponte · relatório de estudo ===
sessões registradas : 14 em 14 dias distintos
tempo total         : 9.4 h (565 min)
primeiro registro   : 2026-08-18
último registro     : 2026-08-31

sequência atual     : 14 dia(s)
maior sequência     : 14 dia(s)
média dos últimos 14 dias: 40 min/dia (meta: 40 min/dia — ok)

distribuição por habilidade:
  escuta         3.2 h  33.6%  ############################
  vocabulario    2.2 h  23.0%  ###################
  fala           1.8 h  18.6%  ###############
  leitura        1.2 h  13.3%  ###########
  escrita        0.8 h   8.4%  #######
  gramatica      0.3 h   3.1%  ##

alvo: B2 (~600 h guiadas)
  faltam 591 h; no ritmo atual de 40 min/dia, são ~28.9 meses (por volta de 2029-01-25)
```

**7. Rodar os testes:**
```bash
python3 -m unittest discover -s testes
```
Saída real:
```
............................................
----------------------------------------------------------------------
Ran 42 tests in 0.047s

OK
```

---

## Estrutura de pastas

```
07-projeto-modelo/
├── README.md                    ← você está aqui
├── config.json                  ← nível-alvo, meta diária, caminhos. Todo ajuste é aqui
├── plano-12-semanas.md          ← o currículo: o que fazer em cada dia
├── roteiro-shadowing.md         ← o protocolo de treino de fala, passo a passo
│
├── deck/
│   └── frases-nucleo.tsv        ← ⭐ OS DADOS: 50 frases A1–B2 com IPA, tradução e alvo de cloze
│
├── scripts/
│   ├── gerar_deck.py            ← valida o TSV e gera os 2 arquivos de importação do Anki
│   └── estudo.py                ← registra sessões (JSONL) e monta o relatório
│
├── testes/
│   └── test_projeto.py          ← 42 testes: validação, geração, sequência, projeção, integração
│
├── diario/
│   └── exemplo-2026-08-31.md    ← modelo de diário de estudo preenchido
│
├── avaliacao/
│   └── rubrica-cefr.md          ← como se autoavaliar sem enganar a si mesmo
│
└── saida/                       ← gerado; pode apagar e regerar
    ├── anki-reconhecimento.tsv
    ├── anki-producao.tsv
    ├── relatorio.txt
    └── registro.jsonl           ← seu histórico de estudo (⚠️ faça backup deste)
```

---

## O que cada decisão de projeto ensina

Estas escolhas não são arbitrárias — cada uma é uma lição sobre aprender idiomas, ou sobre
escrever software que dura.

### 1. Os dados são um TSV, não um banco nem um JSON

**Por quê:** você vai editar esse arquivo à mão, toda semana, pelo resto do curso. TSV abre em
qualquer editor e em planilha, dá diff limpo no Git e não tem sintaxe para errar.
**Lição de idioma:** o material de estudo tem de ser **seu**. Baralho baixado pronto tem taxa de
abandono altíssima porque as frases são de outra pessoa, sobre a vida de outra pessoa.

### 2. Cada frase gera **dois** cartões, não um

**Por quê:** reconhecer (inglês → sentido) e produzir (lacuna dentro da frase) são habilidades
**diferentes**, e a segunda não vem de graça com a primeira.
**Lição de idioma:** é exatamente por isso que gente que "entende tudo mas não fala" existe. Só
treinou a direção receptiva. Ver [../10-fundamentos.md](../10-fundamentos.md) §10.3.

### 3. O cloze precisa existir literalmente na frase — e isso é um teste

O validador rejeita `cloze: "better than"` numa frase que diz `a better idea than`.
**Por quê:** um cartão quebrado só aparece três semanas depois, no meio de uma revisão, quando
você já não lembra de onde veio. Erro que se descobre tarde é o mais caro.
Esse erro **aconteceu de verdade** ao montar este projeto — a linha `015` foi rejeitada pelo
validador na primeira execução, e por isso está correta hoje.

### 4. O registro é JSONL append-only

**Por quê:** registrar nunca reescreve o arquivo, então uma queda no meio da gravação perde no
máximo a última linha. E o leitor **ignora linha corrompida com aviso** em vez de derrubar o
relatório inteiro — dado de dois anos não pode ser refém de um byte errado.

### 5. A sequência não zera se você ainda não estudou hoje

Um detalhe de três linhas em `sequencia_atual()`. Abrir o painel às 8h e ver "sequência: 0"
depois de 40 dias seguidos é desmotivador e **falso**.
**Lição de idioma:** constância é a variável que mais prevê sucesso. Proteja a percepção dela.

### 6. A projeção vem com um aviso colado

O relatório imprime, sempre: *"a projeção é aritmética, não promessa"*.
**Por quê:** número em tela vira compromisso na cabeça de quem lê. Se você não pode garantir,
diga que não pode — no software e no material didático.

### 7. Tem tratamento de erro, configuração e testes

O que tutorial não tem e projeto real tem:
- **erro**: toda falha vira mensagem em português com o número da linha, não traceback;
- **configuração**: `config.json` separa o que muda (meta, nível-alvo) do que não muda (código);
- **teste**: 42 casos, incluindo os caminhos ruins (arquivo faltando, JSON corrompido,
  divisão por zero na projeção, filtro que zera o resultado).

---

## Como estender

| Quero... | Faça |
|---|---|
| adicionar minhas frases | acrescente linhas em `deck/frases-nucleo.tsv` e rode `--dry-run` |
| criar um assunto novo | use uma `tag` nova; ela aparece sozinha no relatório |
| gerar áudio dos cartões | instale o add-on **HyperTTS** no Anki e rode sobre o campo Frente |
| mandar direto para o Anki, sem importar | instale o **AnkiConnect** e faça `POST` em `http://127.0.0.1:8765` com a ação `addNotes` (ver [../03-instalacao.md](../03-instalacao.md) §03.5) |
| mudar o nível-alvo | edite `nivel_alvo` em `config.json` |

---

## Autoteste

1. Por que cada frase vira dois cartões, e o que isso previne?
2. O que acontece se o campo `cloze` não existir dentro do campo `en`? Por que falhar cedo é melhor?
3. Por que o registro é JSONL append-only e não um JSON único?
4. Rode `python3 scripts/gerar_deck.py --max-cefr A1 --tag entrevista --dry-run`. Qual o código de saída e por quê?
5. Que arquivo deste projeto você precisa incluir no backup, e por quê?
6. Cite dois itens que este projeto tem e um tutorial normal não teria.

**Próximo:** [plano-12-semanas.md](plano-12-semanas.md).
