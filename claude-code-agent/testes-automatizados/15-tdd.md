# 15 · TDD — desenvolvimento guiado por testes

`Nível: intermediário` · `Última atualização: 12/08/2026`

---

## 1. O que é, em uma frase

**TDD** (*Test-Driven Development*) é escrever o teste **antes** do código, num ciclo curto
de três passos, repetido dezenas de vezes por dia.

```
        ┌──────────────────────────────────────┐
        │                                      │
        ▼                                      │
  ┌───────────┐      ┌───────────┐      ┌──────┴──────┐
  │ 🔴 RED    │─────▶│ 🟢 GREEN  │─────▶│ 🔵 REFACTOR │
  │           │      │           │      │             │
  │ escreva um│      │ faça      │      │ limpe, com  │
  │ teste que │      │ passar do │      │ os testes   │
  │ FALHA     │      │ jeito mais│      │ verdes o    │
  │           │      │ simples   │      │ tempo todo  │
  └───────────┘      └───────────┘      └─────────────┘
      ~30 s              ~1 min              ~1 min
```

Formalizado por Kent Beck em *Test-Driven Development: By Example* (2002), embora a prática
já existisse no XP desde 1999. Beck sempre disse que redescobriu a ideia num manual antigo
de programação, dos anos 1960 — "escreva as saídas esperadas na fita, depois programe até a
fita bater".

---

## 2. As três leis (Robert C. Martin)

1. Você não escreve código de produção enquanto não tiver um teste que falha.
2. Você não escreve mais teste do que o suficiente para falhar — não compilar **é** falhar.
3. Você não escreve mais código de produção do que o suficiente para passar no teste atual.

São regras deliberadamente severas. Servem para **aprender** o ritmo; ninguém as segue ao pé
da letra o dia inteiro depois de anos de prática, e tudo bem.

---

## 3. Um exemplo completo, do zero

Vamos construir a função `parcelar(total, n)` do
[exemplo 5](06-exemplos.md), desta vez com TDD.

### Ciclo 1 — o caso mais simples que pode falhar

🔴 **RED**

```python
# test_parcelas.py
from parcelas import parcelar


def test_uma_parcela_e_o_total_inteiro():
    assert parcelar(100, 1) == [100]
```

```bash
$ pytest -q
ModuleNotFoundError: No module named 'parcelas'
```

Não compilar é falhar. Este é um RED válido.

🟢 **GREEN** — o mais simples que passa. Sim, mesmo que seja "trapaça":

```python
# parcelas.py
def parcelar(total, n):
    return [total]
```

```bash
$ pytest -q
1 passed
```

🔵 **REFACTOR** — nada a limpar ainda.

> **"Isso é trapaça!"** É, e é de propósito. O código está *correto para tudo o que foi
> especificado até agora*. O que força a generalização é o próximo teste — e é isso que
> mantém o passo pequeno.

### Ciclo 2 — forçando a generalização

🔴 **RED**

```python
def test_duas_parcelas_de_valor_igual():
    assert parcelar(100, 2) == [50, 50]
```

```
E       assert [100] == [50, 50]
```

🟢 **GREEN**

```python
def parcelar(total, n):
    return [total // n] * n
```

Os dois testes passam.

### Ciclo 3 — o caso que revela o bug

🔴 **RED**

```python
def test_o_resto_nao_pode_sumir():
    assert sum(parcelar(100, 3)) == 100
```

```
E       assert 99 == 100
E        +  where 99 = sum([33, 33, 33])
```

**Aqui está o valor do TDD.** Você não encontrou esse caso porque foi esperto; encontrou
porque estava perguntando *"que outro caso pode falhar?"* em vez de *"como implemento isso?"*.

🟢 **GREEN**

```python
def parcelar(total, n):
    base, resto = divmod(total, n)
    return [base + 1] * resto + [base] * (n - resto)
```

🔵 **REFACTOR** — agora sim: a validação, os nomes, o *docstring*.

```python
def parcelar(total_centavos: int, n: int) -> list[int]:
    """Divide um total em n parcelas, distribuindo o resto nas primeiras."""
    if n <= 0:
        raise ValueError("n deve ser positivo")
    base, resto = divmod(total_centavos, n)
    return [base + 1] * resto + [base] * (n - resto)
```

E o teste da validação vem, como sempre, primeiro:

```python
def test_n_zero_e_recusado():
    with pytest.raises(ValueError):
        parcelar(100, 0)
```

### O que aconteceu

Em três ciclos de dois minutos, você produziu: uma função correta, quatro testes que
documentam as regras, e **descobriu um bug de arredondamento antes de escrever a linha que o
conteria**.

---

## 4. As duas estratégias de GREEN

Beck descreve três formas de fazer o teste passar. Duas importam:

| Estratégia | Quando |
|---|---|
| **Óbvio** (*obvious implementation*) | você sabe a resposta e ela é curta — escreva-a |
| **Triangulação** | você não tem certeza da generalização — force com um segundo caso |
| **Fake it** (devolver a constante) | quando estiver travado; é o passo mais lento e mais seguro |

O erro do iniciante é usar sempre "fake it" e achar TDD ridículo. O erro do experiente é
usar sempre "óbvio" e escrever 40 linhas entre um teste e outro — aí não é mais TDD, é
teste-depois com etapas extras.

**Regra prática:** use "óbvio" por padrão; **caia para "fake it" quando um teste ficar
vermelho por um motivo que você não previu.** Passo pequeno é remédio para incerteza.

---

## 5. Dentro para fora × fora para dentro

Duas escolas, e a diferença é grande na prática.

| | *Inside-out* (Detroit / clássica) | *Outside-in* (Londres / mockista) |
|---|---|---|
| começa por | as peças de domínio | o caso de uso, na borda |
| dublês | poucos | muitos, no começo |
| descobre o desenho | de baixo para cima | de cima para baixo |
| risco | construir peças que não se encaixam | mockar demais e travar o desenho cedo |
| bom para | domínio bem entendido, biblioteca | requisito vindo do usuário, aplicação |

**Na prática, quase todo mundo mistura:** desce até onde o problema está claro, sobe quando
não está. É legítimo, e o purismo aqui não paga.

---

## 6. O que TDD entrega de verdade

Separando o que a evidência sustenta do que é folclore.

### 6.1 O que se sustenta

**a) Testabilidade por construção.** Impossível escrever código intestável quando o teste
vem primeiro. Esse é, na opinião de quem escreve, o principal benefício — maior que a suíte
resultante.

**b) O teste realmente falha.** Você **viu** o vermelho. Um teste escrito depois pode nunca
ter falhado, e um teste que nunca falhou é uma hipótese não verificada.

**c) Especificação antes de implementação.** Você é obrigado a decidir *o que* antes de *como*.
Metade dos bugs de requisito aparece aqui.

**d) Escopo controlado.** A terceira lei impede a "engenharia especulativa": você para de
escrever a generalização que ninguém pediu.

**e) Feedback em segundos.** O laço curto reduz o tempo entre cometer o erro e descobri-lo —
que é a variável que mais afeta o custo de correção.

### 6.2 O que **não** se sustenta

**"TDD produz código melhor, comprovadamente."** Os estudos empíricos são inconclusivos. Há
trabalhos mostrando ganho de qualidade com custo de tempo; há outros mostrando que o ganho
some quando se controla pelo **número de testes** — ou seja, o benefício vem de *ter testes*,
não da *ordem* em que foram escritos. Uma replicação bem conhecida (Fucci et al., ~2016)
concluiu que a ordem importa menos do que a granularidade e a uniformidade do ciclo.

**Posição honesta:** TDD é uma **disciplina pessoal com bom retorno**, não um resultado
científico estabelecido. Quem afirmar o contrário está vendendo alguma coisa. Use porque
funciona para você e para o seu time — e meça isso, em vez de apelar a autoridade.

**"TDD substitui projeto."** Não. TDD ajuda a descobrir a interface local, não a arquitetura.
Nenhuma quantidade de ciclos vermelho-verde vai lhe dizer se você precisa de fila ou de
banco.

**"TDD dispensa outros testes."** Não. Ele produz testes unitários; integração e E2E
continuam necessários.

---

## 7. Onde TDD funciona mal

Ser honesto sobre isso é o que separa quem usa a ferramenta de quem a professa.

| Situação | Por que atrapalha | O que fazer |
|---|---|---|
| **você não sabe o que quer construir** | não dá para escrever a asserção sem o oráculo | prototipe primeiro; **jogue fora**; depois faça TDD |
| **exploração de API desconhecida** | você não sabe o que a biblioteca devolve | escreva um script exploratório; depois teste |
| **interface visual** | "está bonito" não é asserção | teste a lógica; a aparência com revisão visual/snapshot |
| **desempenho** | o oráculo é uma medida ruidosa | *benchmark*, não teste |
| **código de cola sem lógica** | não há o que especificar | teste de fumaça e siga |
| **prova de conceito descartável** | ela vai ser jogada fora | não teste; **e jogue fora mesmo** |
| **aprendizado de máquina** | a saída correta é probabilística | teste propriedades e limites, não valores |

O caso mais comum é o primeiro. Beck tem uma resposta boa para ele: chama-se *spike* — um
experimento sem teste, deliberadamente descartável, feito para **aprender**. Depois de
aprender, você apaga e refaz com TDD.

---

## 8. Os cinco porquês: por que escrever o teste antes muda o desenho do código?

**1. Por quê?** Porque o teste é o **primeiro cliente** da sua função, e você sente a
inconveniência da interface antes de haver código apoiado nela.

**2. Por que sentir a inconveniência muda alguma coisa?** Porque montar o cenário é
trabalhoso. Se para testar `enviar_fatura()` você precisa de um banco, um servidor SMTP e um
relógio, escrever esse setup dói — e a dor chega **antes** de você ter investido no desenho.

**3. Por que a dor chegar antes importa?** Porque depois há custo afundado. Com a função
pronta e integrada em três lugares, mudar a assinatura vira "refatoração grande", e a saída
de menor esforço passa a ser "monta o universo no teste" ou "não testa".

**4. Por que a saída de menor esforço vence?** Porque times sob prazo escolhem o caminho de
menor resistência imediata — e essa é uma regularidade observável, não um defeito moral.

**5. Então o mecanismo do TDD é qual, exatamente?** É **antecipar o custo do acoplamento
para o momento em que ele ainda é barato de evitar**. É economia comportamental, não mágica.

**Parada legítima: trade-off econômico com componente comportamental.** E isso explica por
que TDD funciona para algumas pessoas e não para outras: quem já sente a dor do acoplamento
sem precisar do teste chega ao mesmo desenho por outro caminho.

---

## 9. TDD em JavaScript: um ciclo real

```bash
node --test --watch
```

🔴 **RED** — `slug.test.js`

```javascript
import assert from 'node:assert/strict';
import { test } from 'node:test';

import { slug } from './slug.js';

test('converte para minúsculas e troca espaço por hífen', () => {
  assert.equal(slug('Meu Primeiro Post'), 'meu-primeiro-post');
});
```

```
Cannot find module './slug.js'
```

🟢 **GREEN**

```javascript
export function slug(texto) {
  return texto.toLowerCase().replaceAll(' ', '-');
}
```

🔴 **RED** — o caso brasileiro

```javascript
test('remove acentos', () => {
  assert.equal(slug('Ação e Coração'), 'acao-e-coracao');
});
```

🟢 **GREEN**

```javascript
export function slug(texto) {
  return texto
    .normalize('NFD')                 // separa a letra do acento: "ç" → "c" + "̧"
    .replace(/\p{Diacritic}/gu, '')   // remove os acentos que sobraram soltos
    .toLowerCase()
    .replaceAll(' ', '-');
}
```

> `\p{Diacritic}` é uma *Unicode property escape*, disponível desde o ES2018 e disponível no
> Node atual. Exige a bandeira `u` (ou `v`). A alternativa antiga era a faixa de
> combinantes `[̀-ͯ]`, que cobre menos casos.

🔴 **RED** — pontuação e espaços repetidos

```javascript
test('remove pontuação e colapsa espaços', () => {
  assert.equal(slug('  Olá,   mundo!!!  '), 'ola-mundo');
});
```

🟢 **GREEN** + 🔵 **REFACTOR**

```javascript
export function slug(texto) {
  return texto
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')   // qualquer não-alfanumérico vira hífen
    .replace(/^-+|-+$/g, '');      // tira hífens das pontas
}
```

Repare que a terceira versão é **mais simples** que a segunda, e que só foi possível
descobri-la porque os três testes davam a rede para trocar a implementação inteira. Esse é o
🔵 fazendo o seu trabalho.

---

## 10. Erros comuns de quem está começando com TDD

| Erro | Sintoma | Correção |
|---|---|---|
| passo grande demais | 40 linhas entre RED e GREEN | um teste, uma decisão |
| pular o RED | escreve teste e código juntos | escreva o teste, **rode**, veja vermelho |
| pular o REFACTOR | código feio se acumula | é a etapa mais pulada e a mais valiosa |
| testar a implementação | mocka tudo desde o começo | teste o comportamento observável |
| começar pelo caso difícil | trava por 40 minutos | comece pelo trivial; triangule |
| TDD em código de cola | esforço sem retorno | reconheça onde não se aplica (seção 7) |
| não apagar testes | 12 testes cobrindo a mesma coisa | teste também é código; delete o redundante |

O último merece ênfase: **apagar teste é permitido.** Muitos testes escritos durante o
processo eram andaimes para chegar ao desenho. Se três testes verificam a mesma regra, deixe
o mais claro.

---

## 11. Vale a pena?

Recomendação honesta, separada por contexto:

| Contexto | Recomendação |
|---|---|
| lógica de negócio, cálculos, regras | **sim, quase sempre** — é onde TDD brilha |
| bug corrigido | **sim, sempre** — escreva o teste que reproduz, depois conserte |
| API nova, contrato definido | **sim** |
| exploração, protótipo | não — *spike*, e jogue fora |
| interface visual | parcialmente — a lógica sim, a aparência não |
| código legado | não diretamente — caracterize primeiro ([cap. 20](20-testabilidade-e-design.md)) |
| script de uso único | não |

**O caso "bug corrigido" é o de maior retorno e o de menor resistência política.** Ninguém
discute escrever um teste que reproduz um bug real. É o melhor lugar para introduzir TDD num
time cético, e costuma converter mais gente do que qualquer argumento.

---

## Autoteste

1. Enuncie o ciclo de três passos e o tempo típico de cada um.
2. Por que "não compilar" conta como RED válido?
3. No ciclo 1 do exemplo, `return [total]` é trapaça. Justifique por que isso é correto.
4. Diferencie "implementação óbvia", triangulação e *fake it*. Quando cair para *fake it*?
5. Cite três benefícios de TDD que se sustentam e um que não se sustenta.
6. O que a evidência empírica diz sobre TDD produzir código melhor?
7. Descreva três situações em que TDD atrapalha, e o que fazer em cada uma.
8. O que é um *spike* e por que ele é compatível com TDD?
9. Percorra os cinco porquês de "escrever o teste antes muda o desenho" até a parada legítima.
10. No exemplo do `slug`, por que a terceira versão é mais simples que a segunda?
11. Qual é a etapa mais pulada do ciclo, e por que isso é caro?
12. Qual é o melhor ponto de entrada para introduzir TDD num time cético?
