# 19 · Arquitetura legível por máquina

**Nível:** avançado · **Escrito em:** 20/08/2026

---

## A pergunta que organiza o arquivo

> Se um dos leitores do meu código agora é uma máquina literal, sem memória e
> sem acesso ao corredor da empresa, **o que isso muda no projeto do sistema?**

Resposta curta e um pouco decepcionante: **quase nada de novo, e tudo de
prioridade.** As práticas que tornam um sistema legível por agente são as mesmas
que sempre tornaram um sistema legível por humano novo. O que mudou é que o
custo de ignorá-las virou imediato e mensurável.

---

## 1 · O agente é o desenvolvedor recém-chegado — permanentemente

Modelo mental útil: pense num colega competente que **entra na equipe hoje, toda
vez**. Ele:

- não conhece o histórico;
- não sabe quais decisões foram deliberadas e quais foram acidente;
- não tem com quem perguntar no corredor;
- lê o que está escrito e assume que é verdade;
- só enxerga o que cabe na janela dele.

Tudo que ajuda esse colega ajuda o agente, e vice-versa. **Este é o teste que eu
uso para decidir se uma prática vale:** ela ajudaria o recém-chegado?

---

## 2 · As sete propriedades que mais rendem

### 2.1 Localidade — a mudança cabe num lugar

> **Localidade de comportamento:** para entender o que este código faz, quanto
> eu preciso ler além dele?

Alta localidade significa que a mudança cabe na janela de contexto e o agente
não precisa adivinhar o resto.

| Baixa localidade | Alta localidade |
|---|---|
| Herança profunda | Composição explícita |
| Injeção mágica por decorador | Parâmetro passado |
| `Observer` disperso | Chamada direta |
| Configuração espalhada | Um objeto de configuração |
| *Metaprogramming* | Código escrito |

> **Isso não é anti-abstração.** Abstração boa **aumenta** localidade: você lê
> a interface e não precisa do resto. Abstração ruim a destrói: você precisa
> abrir cinco arquivos para saber o que acontece.

### 2.2 Nomes que não mentem

O agente **confia no nome**. Se `validarEmail` também normaliza, ele vai chamar
achando que só valida, e o bug vai ser invisível na revisão — porque a linha
parece certa.

| Sintoma | Correção |
|---|---|
| Verbo errado (`get` que cria) | `obterOuCriar` |
| Função que faz duas coisas | Duas funções |
| `data`, `info`, `handle`, `process`, `manager` | Nome do que é |
| Abreviação local | Palavra inteira |

Nome ruim custava tempo de leitura. Agora causa **erro sistemático**, porque a
máquina não tem a desconfiança que um humano teria.

### 2.3 Tornar o estado ilegal impossível de representar

O princípio mais poderoso da lista, e o mais subutilizado.

```typescript
// ruim: 8 combinações, 5 delas sem sentido
type Pedido = {
  status: 'rascunho' | 'pago' | 'cancelado';
  pagoEm?: Date;
  motivoCancelamento?: string;
};

// bom: só existem os 3 estados válidos
type Pedido =
  | { status: 'rascunho' }
  | { status: 'pago'; pagoEm: Date }
  | { status: 'cancelado'; motivoCancelamento: string };
```

**Por que isso é diferente com IA:** o agente preenche campos plausíveis. Se
`pagoEm` existe no tipo, ele preenche `pagoEm` num pedido cancelado — e nenhum
teste vai reclamar, porque nenhum teste imaginou esse caso.

Com o tipo-soma, o compilador reprova. **Você transferiu uma regra de negócio da
sua cabeça para uma verificação de custo zero** — a tese do
[10-fundamentos](10-fundamentos.md), aplicada ao desenho de tipos.

### 2.4 Fronteiras que a máquina consegue ver

Uma fronteira só é real se algo a verifica.

```
src/
├── dominio/      ← regra de negócio. Não importa NADA de fora
├── aplicacao/    ← casos de uso. Importa dominio
├── adapters/     ← banco, HTTP, fila. Importa aplicacao e dominio
└── web/          ← rotas. Importa aplicacao
```

Verificação mecânica com `import-linter`, ArchUnit ou `dependency-cruiser`
(ver [17](17-verificacao-e-testes.md)).

Sem verificação, a fronteira é folclore — e o agente atravessa folclore sem
hesitar, porque para ele são só arquivos.

### 2.5 Um comando para cada coisa

```makefile
setup:   ## instala tudo
	npm ci

test:    ## roda todos os testes
	npm test

check:   ## lint + tipos + testes — o portão local
	npm run lint && npx tsc --noEmit && npm test

fix:     ## conserta o que é automático
	npm run lint -- --fix && npm run format
```

Por que rende tanto: **`make check` é o sensor do agente**. Um comando único que
responde "está bom?" é o que torna o laço convergente em vez de errático.

Sem isso, o agente adivinha o comando, erra, tenta outro, e cada tentativa
polui o contexto.

### 2.6 Erros que ensinam

```python
# inútil: o agente não tem o que fazer com isso
raise ValueError("erro")

# útil: ele lê e se corrige sozinho
raise ValueError(
    f"CEP {cep!r} tem {len(cep)} dígitos; esperado 8. "
    f"Use apenas números, sem hífen. Exemplo: '01310100'."
)
```

Mensagem de erro é **interface de programação** quando o consumidor é um agente
num laço. Boa mensagem transforma uma falha em uma correção; má mensagem
transforma em três tentativas às cegas.

Regra: toda mensagem de erro deve conter **o que veio, o que se esperava e o que
fazer**.

### 2.7 Documentar o *porquê*, nunca o *quê*

O *quê* está no código e o agente lê melhor que você. O *porquê* não está em
lugar nenhum.

```python
# ruim
# incrementa o contador
contador += 1

# bom
# Pulamos a primeira linha porque o fornecedor manda um cabeçalho
# mesmo quando o arquivo está vazio (contrato de 2019, ver ADR-007).
proxima = linhas[1:]
```

---

## 3 · O trade-off honesto: monólito vs. serviços

| Aspecto | Monólito | Muitos serviços |
|---|---|---|
| O agente enxerga o todo? | Sim, se couber na janela | Não. Cada repositório é uma ilha |
| Raio de explosão de um erro | Grande | Contido |
| Teste local completo | Fácil | Difícil |
| Verificar contrato entre partes | Compilador | Teste de contrato, ou nada |

**Minha leitura, marcada como opinião:** a IA favorece **módulos bem definidos
dentro de um repositório** — o "monólito modular". Motivo: o agente precisa ver
o suficiente para entender e pouco o suficiente para não se perder. Um
repositório com fronteiras verificadas dá as duas coisas; dez repositórios dão
isolamento e tiram compreensão.

Isso **não** é argumento contra microsserviços quando a razão deles é
organizacional (times independentes, escalas diferentes). É argumento contra
fragmentar por moda.

---

## 4 · O risco novo: entropia arquitetural acelerada

Aqui está o dado que deveria preocupar mais gente.

GitClear, analisando 623 milhões de alterações entre 2023 e 2026:

| Indicador | 2022 | 2023 | 2026 |
|---|---|---|---|
| Duplicação de blocos (por milhão de linhas alteradas) | — | 40,3 | **73,0** (+81%) |
| Código **movido** (sinal de refatoração) | 21% | 13% | **3,8%** |
| Copiar-e-colar | 9,4% | — | **15,7%** |

Leia as duas últimas linhas juntas: antes da IA, refatorar era preferido a
duplicar na proporção de cerca de 2 para 1. Hoje a preferência inverteu com
folga.

### Por que isso acontece, mecanicamente

1. O agente **não conhece o sistema todo** — só o que está na janela. Ele não
   sabe que já existe uma função equivalente três pastas adiante.
2. **Duplicar é local; reaproveitar é global.** Duplicar cabe no contexto;
   reaproveitar exige conhecer o resto.
3. **Duplicar sempre funciona.** Reaproveitar pode quebrar quem já usa. O
   caminho de menor resistência é duplicar, e o agente segue o caminho de menor
   resistência por construção.
4. **Ninguém mede duplicação**, então ninguém corrige.

### Contramedidas concretas

| Medida | Como |
|---|---|
| Medir | `jscpd`, `PMD CPD`, SonarQube — no CI, com tendência ao longo do tempo |
| Falhar o portão | Bloquear se o diff introduzir bloco duplicado acima de N linhas |
| Perguntar antes | "Antes de escrever, procure com `rg` se já existe algo equivalente e me diga o que achou" |
| Agendar consolidação | Uma tarefa periódica dedicada a deduplicar. Não vai acontecer sozinha |
| Índice de módulos | Uma seção no `AGENTS.md` dizendo onde ficam os utilitários comuns |

> **A contramedida mais barata é a terceira**, e quase ninguém faz. Uma frase no
> `AGENTS.md` — *"antes de criar função utilitária, procure em `src/comum/`"* —
> muda o comportamento na maioria das vezes.

---

## 5 · Padrões que ganharam e perderam valor

Marcado como **opinião fundamentada**, não consenso.

### Ganharam

| Padrão | Por quê |
|---|---|
| Tipos fortes e domínio tipado | Verificação grátis do código gerado |
| Funções puras | Testáveis sem cerimônia; alta localidade |
| Imutabilidade | Elimina uma classe inteira de erro que o agente comete |
| Composição sobre herança | Localidade |
| Erros explícitos (`Result`, tipos de erro) | O agente vê o caminho de erro no tipo |
| Monólito modular com fronteiras verificadas | Compreensível e contido |
| Documentação executável (teste, exemplo rodável) | Nunca desatualiza em silêncio |

### Perderam

| Padrão | Por quê |
|---|---|
| Metaprogramação e geração dinâmica | Ilegível para máquina e para gente |
| Herança profunda | Destrói localidade |
| "Código autoexplicativo" sem comentário de porquê | O *porquê* nunca esteve no código |
| Convenção sobre configuração levada ao extremo | Convenção implícita é invisível para quem chega |
| DRY levado ao extremo | Abstração prematura custa mais que duplicação controlada — e agora há duplicação demais **e** abstração prematura demais |
| Repositórios minúsculos e fragmentados | Cada um é uma ilha sem contexto |

---

## 6 · Cinco porquês: por que "arquitetura boa para IA" é só arquitetura boa

**Por que o agente precisa de fronteiras claras?**
Porque ele só enxerga o que cabe no contexto.

**Por que isso é diferente de um humano?**
Não é — é a mesma limitação, mais estreita e mais literal. Humano também não
segura 200 mil linhas na cabeça; ele compensa com memória de longo prazo,
conversa e intuição acumulada.

**Por que o agente não compensa?**
Porque ele não tem memória entre sessões nem acesso ao corredor. Toda a
compensação precisa estar **escrita**.

**Por que isso muda a arquitetura?**
Não muda o que é bom. Muda o **preço de ser ruim**: antes, arquitetura ruim era
paga em onboarding lento e bug ocasional, difuso e distante. Agora é paga a cada
tarefa, visivelmente, em tokens e retrabalho.

**Por que a IA não pode simplesmente ficar boa o suficiente para lidar com
arquitetura ruim?**
Porque a dificuldade não é de capacidade do leitor — é **informação que não
existe em lugar nenhum**. Se a razão de uma gambiarra só existe na cabeça de
alguém que saiu da empresa, nenhum modelo, por maior que seja, pode recuperá-la.
Essa é a parada legítima: é um limite de informação, não de inteligência.

---

## Autoteste

1. Qual é o teste que decide se uma prática de arquitetura vale a pena?
2. O que é localidade de comportamento? Dê dois exemplos de baixa e dois de alta.
3. Por que "abstração boa aumenta localidade" não contradiz a defesa de
   localidade?
4. Por que nome que mente causa **erro sistemático** com agentes?
5. Mostre em código como tornar um estado ilegal impossível de representar, e
   explique por que isso importa mais com IA.
6. Por que uma fronteira sem verificação automática é folclore?
7. Por que `make check` é a coisa mais valiosa que você pode dar a um agente?
8. Cite os três elementos que toda mensagem de erro deve conter.
9. Duplicação subiu 81% e código movido caiu de 21% para 3,8%. Explique
   mecanicamente por que, em quatro razões.
10. Cite três padrões que ganharam e três que perderam valor, com o motivo.
11. Por que a IA não pode "ficar boa o suficiente" para lidar com arquitetura
    ruim? Qual é a natureza desse limite?

---

**Anterior:** [18-revisao-de-codigo-gerado](18-revisao-de-codigo-gerado.md) ·
**Próximo:** [20-git-e-fluxo-de-trabalho](20-git-e-fluxo-de-trabalho.md)
