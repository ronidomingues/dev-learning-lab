# 20 · Testabilidade e projeto de código

`Nível: intermediário → avançado` · `Última atualização: 13/08/2026`

**Este é o arquivo mais importante do curso.**

O motivo: quase todo mundo trava no mesmo lugar. Aprende pytest num fim de semana, escreve
testes de funções puras com facilidade, e então tenta testar o código do trabalho — que fala
com banco, chama API, lê a data de hoje e monta as próprias dependências — e descobre que
não dá.

A conclusão natural e errada é *"preciso de uma ferramenta melhor de mock"*. A conclusão
certa é: **o código está mal desenhado, e o teste é só quem descobriu**.

---

## 1. Testabilidade não é uma propriedade do teste

> **Testabilidade** é a facilidade com que se pode colocar um trecho de código num estado
> conhecido, executá-lo, e observar o resultado.

As três palavras: **colocar em estado**, **executar**, **observar**. Se qualquer uma delas
for difícil, o código é intestável — e nenhuma biblioteca conserta isso.

| Sintoma no teste | Causa no código |
|---|---|
| 30 linhas de setup | o código exige um universo montado |
| preciso de 6 mocks | o objeto tem 6 colaboradores |
| não consigo verificar nada | o resultado não é observável (vai direto para o banco) |
| o teste é lento | o código faz I/O no meio da regra |
| o teste quebra em fevereiro | o código lê o relógio por dentro |
| só dá para testar pela interface | toda a lógica está no controlador |

**O teste é um segundo cliente do seu código.** Se ele reclama, o primeiro cliente também
vai reclamar — só que mais tarde e mais caro.

---

## 2. Os cinco inimigos da testabilidade

### 2.1 Estado global e singleton

```python
# ❌ inimigo
CONFIGURACAO = carregar_do_arquivo("/etc/app.conf")

def calcular_frete(peso):
    return peso * CONFIGURACAO["taxa"]
```

Para testar com outra taxa você precisa reescrever o global — e ele vaza para o teste
seguinte.

```python
# ✅ dependência explícita
def calcular_frete(peso, taxa):
    return peso * taxa
```

Em JavaScript o problema é mais insidioso, porque **o módulo é um singleton**: qualquer
`export let` é estado compartilhado entre todos os arquivos de teste do mesmo worker.

### 2.2 Construção interna de dependências (`new` escondido)

```python
# ❌ inimigo: o serviço decide COM QUEM fala
class ServicoRenovacao:
    def __init__(self):
        self.gateway = GatewayHttp("https://api.pagamento.com", os.environ["TOKEN"])
        self.repo = RepositorioPostgres(os.environ["DATABASE_URL"])
```

Não há como substituir nada. O teste precisa de rede e banco.

```python
# ✅ quem constrói é quem chama
class ServicoRenovacao:
    def __init__(self, repositorio, gateway, relogio, notificador):
        ...
```

Isso é **injeção de dependência**, e não precisa de framework nenhum: é passar parâmetro.

### 2.3 Efeito colateral escondido no meio da lógica

```python
# ❌ decidir e fazer, misturados
def processar_pedido(pedido):
    total = sum(i.preco for i in pedido.itens)
    if total > 100_00:
        total -= total // 10
    enviar_email(pedido.cliente, f"Total: {total}")     # ← I/O no meio
    banco.gravar(pedido.id, total)                      # ← I/O no meio
    return total
```

Para testar o cálculo, você é obrigado a mockar e-mail e banco.

```python
# ✅ decidir → devolver → outra camada faz
def calcular_total(pedido) -> tuple[int, list[Efeito]]:
    total = sum(i.preco for i in pedido.itens)
    if total > 100_00:
        total -= total // 10
    return total, [EnviarEmail(pedido.cliente, total), Gravar(pedido.id, total)]
```

Agora a regra é uma função pura, testável com `assert`. Os efeitos são **dados** que outra
camada executa. Esse padrão tem vários nomes — *functional core, imperative shell*, comando
como dado, arquitetura hexagonal — e é a técnica de maior retorno deste arquivo.

### 2.4 Relógio, aleatoriedade e identificadores

```python
# ❌ o teste depende do dia em que roda
def esta_vencida(self):
    return date.today() >= self.proxima_cobranca

# ✅ o tempo é um parâmetro
def esta_vencida(self, hoje: date):
    return hoje >= self.proxima_cobranca
```

Vale igual para `random`, `uuid4()`, `os.urandom` e qualquer leitura de ambiente.

### 2.5 Herança profunda e métodos estáticos

Herança de três níveis torna impossível saber onde um comportamento é decidido. Método
estático não pode ser substituído sem *monkeypatch*. **Composição** resolve os dois casos e
tem testabilidade melhor.

---

## 3. A técnica principal: separar decidir de fazer

```
┌─────────────────────────────────────────────────────────┐
│                    BORDA (imperativa)                   │
│   lê arquivo · chama API · grava banco · imprime        │
│   ── fina, sem lógica, coberta por 1 teste de fumaça ── │
│                                                         │
│   ┌─────────────────────────────────────────────────┐   │
│   │              NÚCLEO (funcional)                 │   │
│   │   regras · cálculos · validações · decisões     │   │
│   │   ── zero I/O · 100% testável com assert ──     │   │
│   └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Regra prática:** empurre o I/O para fora e para cima. Toda decisão que puder ser tomada com
os dados já em mãos deve estar numa função que não conhece o mundo.

**Exemplo concreto do projeto-modelo:**

- `dinheiro.py`, `plano.py`, `assinatura.py` → **núcleo**, 100 % de cobertura, testes em
  microssegundos, zero dublê;
- `relogio.py`, `gateway.py`, `repositorio.py` → **contratos** + implementação real + dublês;
- `servico.py` → orquestra, recebe tudo por injeção, testado com dublês;
- `cli.py` → **borda**, um teste de fumaça, sem regra nenhuma.

O resultado mensurável: 175 dos 190 testes rodam sem tocar nada externo, em 1,98 s.

---

## 4. Injeção de dependência sem framework

Quatro formas, da mais simples à mais elaborada:

### 4.1 Parâmetro com valor-padrão — a mais barata

```javascript
export async function comRepeticao(acao, { dormir = esperar } = {}) { ... }
```

A produção nem sabe que existe; o teste substitui numa linha. É a técnica do
[exemplo 7](06-exemplos.md), e faz a suíte ir de 2 s para 94 ms.

```python
def processar(pedido, agora=None):
    agora = agora or datetime.now()
```

> **Cuidado com o valor-padrão mutável em Python:** `def f(itens=[])` cria a lista **uma
> vez**, na definição, e ela é compartilhada por todas as chamadas. Use `None` como
> sentinela.

### 4.2 Construtor

```python
class ServicoRenovacao:
    def __init__(self, repositorio, gateway, relogio, notificador):
```

O padrão para objetos com várias dependências. Se a lista passar de quatro ou cinco, é sinal
de que o objeto faz coisas demais.

### 4.3 Protocolo / interface

```python
from typing import Protocol

class Relogio(Protocol):
    def hoje(self) -> date: ...
```

Em Python, `Protocol` é **tipagem estrutural**: quem tem o método satisfaz o contrato, sem
herdar nada. Isso documenta a fronteira e deixa o verificador de tipos ajudar.

Em JavaScript não há equivalente em tempo de execução — a fronteira é convenção mais
**teste de contrato**. TypeScript recupera a garantia estática.

### 4.4 Composition root

Um lugar só, na borda, que monta o grafo de objetos:

```python
def main():
    repo = RepositorioSQLite(os.environ["BANCO"])
    gateway = GatewayHttp(os.environ["URL_PAGAMENTO"], os.environ["TOKEN"])
    servico = ServicoRenovacao(repo, gateway, RelogioDoSistema(), NotificadorEmail())
    print(servico.renovar_vencidas())
```

**Não use container de injeção de dependência** a menos que o grafo seja realmente grande.
Ele troca um problema visível (montagem explícita) por um invisível (mágica de resolução), e
piora o diagnóstico de erro.

---

## 5. Código legado: por onde começar

Definição de Michael Feathers, e é a melhor que existe:

> **Código legado é código sem testes.**

Não é código velho, nem escrito por outra pessoa. É código sem rede.

### 5.1 O dilema, e a saída

> Para mudar com segurança, preciso de testes.
> Para escrever testes, preciso mudar o código.

A saída de Feathers, em cinco passos:

**1. Identifique o ponto de mudança.** Não tente testar o sistema; testar o pedaço que você
vai tocar.

**2. Encontre as costuras** (*seams*). Uma costura é um ponto onde se pode alterar o
comportamento **sem editar naquele ponto**:

| Costura | Python | JavaScript |
|---|---|---|
| parâmetro com padrão | `def f(hoje=None)` | `function f({ agora = Date.now } = {})` |
| atributo de módulo | `monkeypatch.setattr("mod.X", ...)` | `vi.mock('./mod.js')` |
| método sobrescrevível | subclasse de teste | idem |
| variável de ambiente | `monkeypatch.setenv` | `vi.stubEnv` |
| import | `patch("mod.dep")` | `vi.mock` |

**3. Escreva um teste de caracterização.** Registre o comportamento **atual**, certo ou
errado ([exemplo 11](06-exemplos.md)). Não tente consertar nada ainda.

**4. Refatore com a rede no lugar.** A refatoração de maior retorno é sempre a mesma:
**extrair a lógica pura**.

```python
# antes: 80 linhas, com SQL e HTTP no meio
def processar_lote():
    linhas = banco.query("SELECT ...")
    for l in linhas:
        if l["status"] == "P" and l["valor"] > 1000:
            api.post("/aprovar", {"id": l["id"]})
            banco.execute("UPDATE ... WHERE id = %s", l["id"])

# depois: a decisão sai, e vira testável
def decidir_aprovacoes(linhas) -> list[int]:            # ← função pura, testável
    return [l["id"] for l in linhas
            if l["status"] == "P" and l["valor"] > 1000]

def processar_lote(banco, api):                          # ← borda fina
    linhas = banco.query("SELECT ...")
    for id_ in decidir_aprovacoes(linhas):
        api.post("/aprovar", {"id": id_})
        banco.execute("UPDATE ... WHERE id = %s", id_)
```

**5. Só agora** escreva os testes de verdade sobre `decidir_aprovacoes`.

### 5.2 A regra do escoteiro, aplicada a testes

Não pare o projeto para "adicionar testes". Faça isto:

- todo **bug corrigido** ganha um teste que o reproduz — sem exceção;
- todo **arquivo tocado** ganha um teste, mesmo que pequeno;
- toda **função nova** nasce testada.

Em seis meses o núcleo mais mexido — que é o que mais quebra — está coberto, sem nunca ter
existido um "projeto de testes".

---

## 6. Sinais de que o problema é o projeto, não o teste

| Você está fazendo isto no teste | Corrija isto no código |
|---|---|
| `patch` em mais de 2 lugares | dependências implícitas → injete |
| montar 5 objetos para testar 1 | acoplamento → extraia |
| ler o banco para verificar o resultado | o método não devolve nada → devolva |
| `sleep` para esperar | assincronia sem sincronização → exponha um sinal |
| subclasse "de teste" sobrescrevendo métodos | herança no lugar de composição |
| testar através da interface gráfica | lógica no controlador → mova para o domínio |
| `monkeypatch` no relógio | injete o relógio |
| `if os.environ.get("TESTE")` no código de produção | **nunca faça isto** (seção 7) |

---

## 7. O antipadrão proibido: código que sabe que está em teste

```python
# ❌❌❌ NUNCA
def cobrar(valor):
    if os.environ.get("AMBIENTE") == "teste":
        return {"aprovada": True}
    return gateway_real.cobrar(valor)
```

Três razões pelas quais isto é grave:

1. **O caminho de produção nunca é exercitado.** Você testa um programa diferente do que
   entrega.
2. **Um erro de configuração vira incidente:** se `AMBIENTE=teste` vazar para produção, o
   sistema aprova tudo.
3. **Cria uma porta de fraude.** Quem controlar a variável de ambiente controla a cobrança.

A alternativa é sempre a mesma: **injeção**. O dublê entra pela porta da frente, no
`composition root` do teste, e o código de produção não sabe que ele existe.

---

## 8. Os cinco porquês: por que código testável é código melhor?

**1. Por quê?** Porque testabilidade exige dependências explícitas, e dependências explícitas
tornam o código legível.

**2. Por que explicitar dependências torna legível?** Porque a assinatura passa a dizer a
verdade. `def cobrar(cliente, valor)` que por dentro abre conexão, lê ambiente e chama três
APIs é uma **assinatura mentirosa**: ela promete uma função e entrega um subsistema.

**3. Por que a assinatura mentirosa é cara?** Porque quem lê precisa abrir o corpo para saber
o que a função faz — e depois o corpo das funções que ela chama. O custo de entender cresce
em cascata, e é ele que domina o tempo de manutenção.

**4. Por que o custo de entender domina?** Porque programadores passam a maior parte do tempo
**lendo** código, não escrevendo. Isso é uma regularidade observada há décadas em estudos de
manutenção de software, e é a razão de a legibilidade valer mais que a concisão.

**5. Então testabilidade é um proxy para quê, exatamente?** Para **acoplamento explícito e
baixo**. Um módulo testável é um módulo cujas dependências são poucas, declaradas e
substituíveis — que é a definição operacional de bom acoplamento desde Parnas (1972).

**Parada legítima: é o princípio de ocultação de informação de David Parnas**, de *On the
Criteria To Be Used in Decomposing Systems into Modules* (1972). Testabilidade não é uma
virtude independente; é um **sintoma observável** de um princípio de projeto que já tinha 20
anos quando o teste automatizado se popularizou. É por isso que a correlação é tão forte: as
duas coisas medem a mesma propriedade subjacente.

---

## 9. Arquiteturas que nascem testáveis

Não é preciso adotar nenhuma delas por inteiro; o que importa é a ideia comum.

| Arquitetura | Ideia central |
|---|---|
| **Hexagonal / Ports & Adapters** (Cockburn, 2005) | o domínio define portas; adaptadores implementam; o domínio não conhece I/O |
| **Cebola** (Palermo, 2008) | dependências apontam para dentro; o núcleo não depende de nada |
| **Limpa** (Martin, 2012) | mesma ideia, com nomes de camadas |
| **Functional core, imperative shell** (Bernhardt, 2012) | núcleo puro; casca faz I/O |

**A ideia comum, e a única coisa que você precisa levar:** *dependências apontam para dentro;
o que fala com o mundo fica na borda.*

**Aviso, como opinião:** adotar a nomenclatura completa dessas arquiteturas em um projeto
pequeno produz mais pastas do que benefício. A ideia central cabe em três camadas —
domínio, casos de uso, borda — e o projeto-modelo mostra que isso basta para uma aplicação
inteira.

---

## 10. Um exercício de refatoração para testabilidade

Código de partida, intestável de propósito:

```python
import os
import smtplib
from datetime import date

import psycopg


def enviar_cobrancas():
    con = psycopg.connect(os.environ["DATABASE_URL"])
    hoje = date.today()
    linhas = con.execute(
        "SELECT id, email, valor, vencimento FROM faturas WHERE paga = false"
    ).fetchall()
    for id_, email, valor, vencimento in linhas:
        dias = (hoje - vencimento).days
        if dias == 0:
            assunto = "Sua fatura vence hoje"
        elif dias > 0:
            assunto = f"Fatura vencida há {dias} dias"
        else:
            continue
        servidor = smtplib.SMTP(os.environ["SMTP_HOST"])
        servidor.sendmail("cobranca@app.br", email, f"Subject: {assunto}\n\nR$ {valor}")
        servidor.quit()
        con.execute("UPDATE faturas SET avisada = true WHERE id = %s", (id_,))
```

**Sua tarefa, em quatro passos:**

1. Extraia a decisão — `decidir_avisos(faturas, hoje) -> list[Aviso]` — como função pura.
2. Teste essa função: vence hoje, vencida há 1 dia, vencida há 30, **vence amanhã**
   (fronteira!), lista vazia.
3. Injete banco, e-mail e relógio no que sobrou.
4. Escreva **um** teste de integração da borda, com fakes.

A solução comentada está em [70-pratica.md](70-pratica.md), laboratório 8.

**Dica sobre a fronteira:** a versão original tem um bug. `dias < 0` cai no `continue`, mas
`dias == 0` e `dias > 0` avisam. Qual é o comportamento para uma fatura que vence **amanhã**?
E para uma que venceu **hoje de manhã** num fuso diferente do servidor? Escrever o teste é o
que faz essas perguntas aparecerem.

---

## Autoteste

1. Defina testabilidade com as três palavras-chave.
2. Cite os cinco inimigos da testabilidade, com um exemplo de cada.
3. Explique "separar decidir de fazer" e por que é a técnica de maior retorno.
4. Qual é a forma mais barata de injeção de dependência, e qual armadilha do Python ela tem?
5. Por que **não** usar um container de injeção de dependência num projeto pequeno?
6. Enuncie a definição de código legado de Feathers e explique por que ela é boa.
7. O que é uma "costura"? Dê dois exemplos em Python e dois em JavaScript.
8. Descreva os cinco passos de Feathers para mexer em código legado.
9. Por que `if os.environ["AMBIENTE"] == "teste"` no código de produção é grave? Três razões.
10. Percorra os cinco porquês até Parnas e explique a relação entre testabilidade e acoplamento.
11. Qual é a ideia comum às arquiteturas hexagonal, cebola, limpa e *functional core*?
12. No exercício da seção 10, qual é a fronteira que o código original trata de forma duvidosa?
