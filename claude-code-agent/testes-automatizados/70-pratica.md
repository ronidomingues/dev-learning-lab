# 70 · Prática — 12 laboratórios

`Nível: iniciante → avançado` · `Última atualização: 13/08/2026`

Ordem crescente de dificuldade. Cada laboratório tem **objetivo**, **enunciado**,
**critério de pronto** e **solução comentada** (recolhida, para você tentar antes).

Faça na linguagem que escolheu. Onde a diferença importa, os dois lados aparecem.

---

## Lab 1 — O primeiro teste que falha de propósito · ⏱ 15 min

**Objetivo:** ver vermelho e entender a mensagem.

**Enunciado.** Escreva `dividir(a, b)` e três testes: divisão normal, divisão por zero e
divisão que dá resultado fracionário. **Antes de implementar**, rode e confirme que os três
falham. Depois implemente e confirme que os três passam.

**Critério de pronto:**
- [ ] você viu os três vermelhos antes de escrever qualquer implementação;
- [ ] você consegue explicar cada linha da mensagem de falha;
- [ ] a divisão por zero levanta uma exceção, não devolve `None` nem `Infinity`.

<details><summary>Solução</summary>

```python
import pytest


def dividir(a, b):
    if b == 0:
        raise ZeroDivisionError("não dá para dividir por zero")
    return a / b


def test_divisao_exata():
    assert dividir(10, 2) == 5


def test_divisao_fracionaria():
    assert dividir(1, 3) == pytest.approx(0.3333333333333333)


def test_divisao_por_zero_explode():
    with pytest.raises(ZeroDivisionError, match="dividir por zero"):
        dividir(1, 0)
```

**Pontos de atenção.** Em JavaScript, `1 / 0` devolve `Infinity` sem erro — o teste da
divisão por zero é o que força a decisão de projeto. E `dividir(1, 3) == 0.333...` só
funciona com tolerância; `pytest.approx` / `toBeCloseTo` existem exatamente para isso.
</details>

---

## Lab 2 — Partição e fronteira · ⏱ 30 min

**Objetivo:** escolher casos com método, não por intuição.

**Enunciado.** Implemente `preco_ingresso(idade, e_estudante)`:

```
idade < 0            → ValueError
0 ≤ idade < 3        → grátis
3 ≤ idade < 12       → meia (R$ 15,00)
12 ≤ idade < 60      → inteira (R$ 30,00), meia se estudante
idade ≥ 60           → meia
idade > 120          → ValueError
```

Antes de codar, escreva num papel: as **classes de equivalência** e, para cada fronteira, os
**três** valores (anterior, exato, seguinte). Só então escreva os testes.

**Critério de pronto:**
- [ ] pelo menos 15 casos, todos justificáveis;
- [ ] as fronteiras 3, 12, 60, 0 e 120 têm os três valores cada;
- [ ] você usou `parametrize` / `it.each`, não 15 funções copiadas.

<details><summary>Solução (recorte)</summary>

```python
FRONTEIRAS = [
    (-1, "erro"), (0, 0), (2, 0), (3, 1500), (11, 1500),
    (12, 3000), (59, 3000), (60, 1500), (120, 1500), (121, "erro"),
]

@pytest.mark.parametrize(("idade", "esperado"), FRONTEIRAS)
def test_fronteiras_sem_estudante(idade, esperado):
    if esperado == "erro":
        with pytest.raises(ValueError):
            preco_ingresso(idade, e_estudante=False)
    else:
        assert preco_ingresso(idade, e_estudante=False) == esperado


@pytest.mark.parametrize("idade", [12, 30, 59])
def test_estudante_paga_meia_na_faixa_inteira(idade):
    assert preco_ingresso(idade, e_estudante=True) == 1500


@pytest.mark.parametrize("idade", [0, 2, 3, 11, 60, 120])
def test_estudante_nao_muda_nada_fora_da_faixa_inteira(idade):
    assert preco_ingresso(idade, True) == preco_ingresso(idade, False)
```

O último teste é o que a maioria esquece: o estudante **não** deve pagar mais nem menos onde
o desconto já se aplica. É uma regra que só aparece quando você organiza por classe.
</details>

---

## Lab 3 — Ler a saída de falha · ⏱ 20 min

**Objetivo:** transformar a mensagem de erro em diagnóstico.

**Enunciado.** Pegue o projeto-modelo, quebre-o de três formas diferentes e, **sem olhar o
diff**, descubra o que foi mudado só pela saída dos testes:

```bash
cd 07-projeto-modelo/python
# 1
sed -i 's/hoje >= self.proxima_cobranca/hoje > self.proxima_cobranca/' assinaturas/assinatura.py
pytest -q --tb=line | head -25
```

Depois desfaça (`git checkout assinaturas/`) e repita com outras duas mutações à sua escolha.

**Critério de pronto:**
- [ ] você identificou o arquivo e a linha só pela saída;
- [ ] você sabe dizer por que **18** testes ficaram vermelhos, e não 1;
- [ ] você experimentou `--tb=line`, `--tb=short`, `-x`, `--lf`.

---

## Lab 4 — Fixtures e limpeza · ⏱ 40 min

**Objetivo:** montar cenário sem repetição e com teardown garantido.

**Enunciado.** Escreva um `RegistroDeArquivos` que grava eventos em um arquivo de texto
(`registrar(evento)`, `ler_todos()`, `limpar()`). Teste com `tmp_path`. Depois:

1. crie uma fixture `registro` que devolve um objeto pronto e vazio;
2. crie uma fixture `registro_com_tres_eventos` que **usa** a primeira;
3. adicione uma fixture de escopo `module` que cria uma pasta compartilhada e prove, com um
   teste, que ela é criada **uma vez só**;
4. faça uma fixture levantar exceção **antes** do `yield` e observe que o teardown não roda.

**Critério de pronto:**
- [ ] nenhum teste escreve em caminho fixo;
- [ ] `pytest --setup-show` mostra a árvore que você esperava;
- [ ] você sabe explicar a diferença entre `E` e `F` na saída.

---

## Lab 5 — Os quatro dublês · ⏱ 60 min

**Objetivo:** escolher o dublê certo para cada situação.

**Enunciado.** Um `ServicoDeBoasVindas` que, ao receber um cadastro:
- valida o e-mail (regra sua);
- grava no repositório;
- envia e-mail de boas-vindas;
- registra a data do cadastro.

Escreva **um** teste usando cada tipo:
- **stub** para o relógio;
- **fake** para o repositório;
- **spy** para o e-mail;
- **sabotador** para o e-mail fora do ar (o cadastro deve ser gravado mesmo assim);
- **mock** para verificar que o e-mail recebeu o endereço correto.

**Critério de pronto:**
- [ ] o serviço não constrói nenhuma dependência por dentro;
- [ ] o teste do sabotador prova que o cadastro sobreviveu à falha do e-mail;
- [ ] você consegue justificar, para cada teste, por que aquele dublê e não outro.

<details><summary>Dica sobre o ponto difícil</summary>

O teste do sabotador é o que revela o desenho. Se `enviar_email` estiver no meio da função,
uma exceção dele aborta a gravação. Você vai precisar de `try/except` em volta do envio — e
essa necessidade **só aparece** quando você escreve o teste. É o efeito do
[capítulo 20](20-testabilidade-e-design.md) na prática.
</details>

---

## Lab 6 — Teste de contrato · ⏱ 60 min

**Objetivo:** impedir que o fake minta.

**Enunciado.** Escreva duas implementações de `Cache`: `CacheMemoria` (dict) e
`CacheArquivo` (JSON em disco). Contrato: `set(chave, valor, ttl)`, `get(chave)`,
`apagar(chave)`, `limpar()`. Escreva **uma** bateria de 10 testes e rode nas duas.

Depois **quebre** uma delas de propósito (por exemplo, o `CacheArquivo` não expira nada) e
confirme que a bateria pega.

**Critério de pronto:**
- [ ] fixture parametrizada (Python) ou laço sobre implementações (JS);
- [ ] a bateria cobre expiração, chave inexistente, sobrescrita e `limpar`;
- [ ] você documentou, com um teste, alguma divergência que decidiu **aceitar**.

<details><summary>Dica sobre TTL</summary>

Não use `time.sleep(2)` para testar expiração. **Injete o relógio.** Se você se pegar
escrevendo `sleep`, releia o [capítulo 20](20-testabilidade-e-design.md) §2.4.
</details>

---

## Lab 7 — Testes de propriedade · ⏱ 60 min

**Objetivo:** escrever leis, não exemplos.

**Enunciado.** Implemente `comprimir(texto)` e `descomprimir(dados)` com *run-length
encoding* (`"aaabbc"` → `"a3b2c1"`). Escreva:

1. a propriedade de ida e volta: `descomprimir(comprimir(t)) == t`;
2. a propriedade de que comprimir é determinístico;
3. a propriedade de que o resultado nunca é maior que `2 × len(t)`;
4. dois testes de exemplo, para ancorar a leitura.

**Critério de pronto:**
- [ ] a Hypothesis (ou fast-check) encontrou pelo menos um contraexemplo que você não previu;
- [ ] você sabe dizer qual foi o contraexemplo **encolhido** e por que ele é mínimo.

<details><summary>Spoiler do contraexemplo</summary>

Texto com **dígitos**. `"a11"` comprime para `"a1112"`… e descomprimir vira ambíguo. A
propriedade de ida e volta acha isso em segundos, e o encolhimento entrega o menor caso.
A correção é escapar dígitos ou mudar o formato — e essa decisão de projeto **só aparece
porque você escreveu a lei**.
</details>

---

## Lab 8 — Refatorar para testabilidade · ⏱ 90 min

**Objetivo:** o laboratório central do curso.

**Enunciado.** Pegue o código intestável da seção 10 do
[capítulo 20](20-testabilidade-e-design.md) — `enviar_cobrancas()`, com banco, SMTP e
`date.today()` embutidos. Refatore em quatro passos:

1. extraia `decidir_avisos(faturas, hoje) -> list[Aviso]`, pura;
2. escreva os testes dela: vence hoje, vencida há 1 dia, há 30, **vence amanhã**, lista vazia;
3. injete banco, e-mail e relógio no que sobrou;
4. escreva **um** teste da borda, com fakes.

**Critério de pronto:**
- [ ] `decidir_avisos` não importa `psycopg`, `smtplib` nem `datetime`;
- [ ] os testes da regra rodam em milissegundos, sem dublê nenhum;
- [ ] você descobriu e documentou o comportamento para "vence amanhã".

<details><summary>Solução comentada</summary>

```python
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Aviso:
    id_fatura: int
    email: str
    assunto: str
    valor_centavos: int


def decidir_avisos(faturas, hoje: date) -> list[Aviso]:
    """Núcleo puro: decide, não faz.

    Regra confirmada com a área de cobrança: avisa NO dia do vencimento e
    depois; não avisa antes. "Vence amanhã" NÃO gera aviso — que é o
    comportamento do código original, agora explícito e testado.
    """
    avisos = []
    for f in faturas:
        dias = (hoje - f.vencimento).days
        if dias < 0:
            continue
        assunto = "Sua fatura vence hoje" if dias == 0 else f"Fatura vencida há {dias} dias"
        avisos.append(Aviso(f.id, f.email, assunto, f.valor_centavos))
    return avisos


def enviar_cobrancas(repositorio, correio, relogio):
    """Borda: só faz. Nenhuma decisão aqui."""
    hoje = relogio.hoje()
    for aviso in decidir_avisos(repositorio.faturas_em_aberto(), hoje):
        correio.enviar(aviso.email, aviso.assunto, f"R$ {aviso.valor_centavos / 100:.2f}")
        repositorio.marcar_avisada(aviso.id_fatura)
```

**O que se ganhou:** `decidir_avisos` tem 10 linhas, zero import de infraestrutura, e é
testável com `assert` puro. `enviar_cobrancas` tem 5 linhas e nenhuma regra — um teste de
fumaça com fakes basta.

**A pergunta que o teste fez aparecer:** "vence amanhã" (`dias == -1`). O código original
caía no `continue`, mas ninguém sabia se era intencional. Ao escrever o teste, você é
**obrigado** a perguntar — e a resposta vira um *docstring* e um teste com nome.
</details>

---

## Lab 9 — Teste de integração com banco · ⏱ 90 min

**Objetivo:** exercitar o banco de verdade sem sujeira entre testes.

**Enunciado.** Usando o `RepositorioSQLite` do projeto-modelo como modelo, escreva um
repositório de pedidos e teste:

1. ida e volta de todos os campos, incluindo data e decimal;
2. `ON CONFLICT DO UPDATE` (salvar duas vezes não duplica);
3. consulta com filtro e ordenação determinística;
4. o esquema é idempotente (abrir duas vezes não explode);
5. um teste que prova que **cada teste vê um banco limpo**.

Depois faça a mesma bateria rodar contra Postgres com Testcontainers, e implemente o padrão
**transação + rollback**.

**Critério de pronto:**
- [ ] a suíte roda em `:memory:` em menos de 1 s;
- [ ] a mesma bateria passa nos dois bancos;
- [ ] os testes de integração estão marcados e excluídos do laço rápido.

---

## Lab 10 — API HTTP · ⏱ 90 min

**Objetivo:** testar um servidor de verdade.

**Enunciado.** Estenda a API do [exemplo 8](06-exemplos.md) com:
- `DELETE /tarefas/:id` (204 se apagou, 404 se não existia);
- `GET /tarefas?feita=true` (filtro);
- paginação com `?limite=&cursor=`;
- cabeçalho `ETag` no `GET /tarefas/:id` e `412` em `If-Match` desatualizado.

**Critério de pronto:**
- [ ] cada rota tem teste de sucesso **e** de erro;
- [ ] os códigos 400, 404, 412 e 422 estão distinguidos e testados;
- [ ] a porta é efêmera (`listen(0)`) e o servidor sobe uma vez só.

---

## Lab 11 — Domar um teste instável · ⏱ 60 min

**Objetivo:** reconhecer e consertar as quatro fontes de indeterminismo.

**Enunciado.** Este arquivo tem quatro testes propositalmente instáveis. Rode-o 20 vezes
(`for i in $(seq 20); do pytest -q; done`) e conserte cada um.

```python
import random
import time
from datetime import date, datetime


def test_1_relogio():
    """Quebra virando o mês."""
    assert datetime.now().day <= 28


def test_2_aleatoriedade():
    """Quebra 1 vez em 10."""
    assert random.randint(1, 10) != 7


def test_3_tempo_de_execucao():
    """Quebra em máquina carregada."""
    inicio = time.time()
    sum(range(100_000))
    assert time.time() - inicio < 0.001


ESTADO = []


def test_4a_estado_compartilhado():
    ESTADO.append(1)
    assert len(ESTADO) == 1


def test_4b_estado_compartilhado():
    ESTADO.append(2)
    assert len(ESTADO) == 1
```

**Critério de pronto:**
- [ ] 20 execuções seguidas, todas verdes;
- [ ] com `pytest -p randomly` (ordem embaralhada), continua verde;
- [ ] você nomeou a fonte de indeterminismo de cada um.

<details><summary>Direção das correções</summary>

1. injete a data; teste a regra, não "hoje";
2. injete o gerador, ou fixe a semente — e note que fixar a semente **esconde** o problema em
   vez de resolvê-lo, se a regra de negócio depende do sorteio;
3. **não teste tempo com relógio.** Se a exigência é de desempenho, isso é *benchmark*, não
   teste — use `pytest-benchmark` com estatística, num job separado;
4. estado no nível do módulo → fixture com escopo de função.
</details>

---

## Lab 12 — Mutação sobre a sua própria suíte · ⏱ 90 min

**Objetivo:** descobrir que a sua suíte é mais fraca do que a cobertura sugere.

**Enunciado.** Sobre o código do Lab 2 (`preco_ingresso`), com cobertura de ramo em 100 %:

1. aplique **10 mutações à mão**: `>=`→`>`, `<`→`<=`, trocar constantes, inverter `and`/`or`,
   remover uma linha, trocar `True`/`False`, trocar a ordem de dois `if`;
2. anote quantas sobreviveram;
3. escreva os testes que matam as sobreviventes;
4. só então rode `mutmut run` (ou `npx stryker run`) e compare com o seu resultado manual.

**Critério de pronto:**
- [ ] você encontrou pelo menos uma sobrevivente antes de rodar a ferramenta;
- [ ] você identificou pelo menos um **mutante equivalente** (impossível de matar) e sabe
      justificar;
- [ ] você consegue explicar por que a cobertura era 100 % e mesmo assim havia lacunas.

---

## Como se autoavaliar

Ao fim dos 12, você deve conseguir responder sem consultar:

| Pergunta | Lab |
|---|---|
| como escolho os casos de teste? | 2 |
| como leio uma falha? | 3 |
| como monto cenário sem repetição? | 4 |
| qual dublê usar em cada situação? | 5 |
| como garanto que o fake não mente? | 6 |
| como escrevo uma lei em vez de um exemplo? | 7 |
| **como torno testável um código que não é?** | **8** |
| como testo contra banco sem sujeira? | 9 |
| como testo uma API? | 10 |
| como conserto um teste instável? | 11 |
| como sei se minha suíte tem força? | 12 |

Se travar no 8, volte ao [capítulo 20](20-testabilidade-e-design.md). É o que separa quem
sabe usar pytest de quem sabe testar.
