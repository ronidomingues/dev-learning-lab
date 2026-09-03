# 01 · O que é o uv — explicado para quem nunca programou

> **Nível:** iniciante · **Atualizado em:** 31/08/2026 · **uv de referência:** 0.12.7

---

## 1. A analogia: a cozinha e a lista de compras

Imagine que você vai cozinhar uma receita que um amigo te mandou. A receita diz:

> "Use farinha, fermento e leite."

Você vai ao mercado, compra os três, cozinha, dá certo. Uma semana depois você manda
a mesma receita para outra pessoa. Ela compra farinha, fermento e leite — mas o fermento
que ela achou é de outra marca, mais forte. O bolo dela cresce demais e desanda.

A receita estava certa. Os **ingredientes** é que não eram os mesmos.

Programar em Python é exatamente isso. Seu programa é a receita. Os ingredientes são
**bibliotecas** — pedaços de código prontos que outras pessoas escreveram e publicaram
(para fazer gráficos, falar com a internet, ler planilhas). E o problema clássico do
Python, por mais de vinte anos, foi este: *na sua máquina funciona, na do colega não*.

O **uv** é a ferramenta que resolve isso. Ele é, ao mesmo tempo:

1. o **carrinho de compras** que busca os ingredientes;
2. a **nota fiscal detalhada** que registra a marca e o lote exatos de cada um;
3. a **despensa separada** de cada receita, para que a farinha de um projeto não se
   misture com a de outro;
4. e até o **fogão** — ele instala o próprio Python para você.

Uma frase para guardar:

> **uv é um programa único, muito rápido, que cuida de tudo que um projeto Python
> precisa para rodar igual em qualquer computador.**

---

## 2. Por que isso é um problema de verdade

Antes de falar do uv, é preciso entender o buraco que ele preenche. Cinco fatos:

**Fato 1 — Python não vem com uma despensa por receita.**
Quando você instala uma biblioteca no Python "do sistema", ela vai para um lugar só,
compartilhado por todos os seus programas. Se o projeto A precisa da versão 1 e o
projeto B precisa da versão 2, um dos dois quebra. Sempre.

**Fato 2 — a solução tradicional era manual e frágil.**
A saída inventada nos anos 2000 foi o **ambiente virtual** (*virtual environment*):
uma pasta que finge ser uma instalação de Python só sua. Funciona, mas você precisa
lembrar de criar, de ativar, de desativar, e de repetir isso em cada máquina.

**Fato 3 — "a lista de ingredientes" era vaga.**
O arquivo tradicional `requirements.txt` costuma dizer `requests` — sem versão. Hoje
isso instala a versão de hoje; ano que vem, outra. Sua receita muda sozinha enquanto
você dorme.

**Fato 4 — as ferramentas eram muitas e não conversavam.**
Para fazer o trabalho completo você precisava aprender e instalar: `pip` (instalar),
`venv` (isolar), `pyenv` (trocar versão do Python), `pipx` (instalar programas de
linha de comando), `pip-tools` ou `poetry` (travar versões), `build` e `twine`
(empacotar e publicar). Sete ferramentas, sete jeitos de configurar, sete manuais.

**Fato 5 — era lento.**
Montar o ambiente de um projeto médio levava dezenas de segundos a minutos. Isso
acontece em cada máquina de cada pessoa, e em cada execução automatizada do servidor.
Multiplicado por milhares de vezes por dia numa empresa, vira dinheiro real.

O uv ataca os cinco de uma vez.

---

## 3. O que o uv faz, em português claro

| O que você quer | O que você digita | O que acontece |
|---|---|---|
| Começar um projeto novo | `uv init meuprojeto` | cria a pasta com tudo pronto |
| Usar uma biblioteca | `uv add requests` | baixa, instala, **e anota a versão exata** |
| Rodar seu programa | `uv run main.py` | prepara o ambiente sozinho e executa |
| Reproduzir na máquina do colega | `uv sync` | reconstrói o ambiente **idêntico** |
| Usar um programa pronto sem instalar | `uvx ruff check` | roda e descarta |
| Ter outra versão do Python | `uv python install 3.13` | baixa o Python, sem mexer no do sistema |

Repare no que **não** aparece nessa tabela: criar ambiente virtual, ativar ambiente
virtual, escolher onde o Python está, escrever arquivo de dependências à mão. O uv faz
tudo isso por baixo, sem pedir licença e sem você precisar saber.

---

## 4. A parte que impressiona: a velocidade

Isto não é propaganda — é uma medição feita nesta máquina, em 31/08/2026,
instalando `fastapi` e `pandas` (dois pacotes populares que arrastam dezenas de outros):

| Ferramenta | Tempo |
|---|---|
| `pip install` (ambiente novo) | **23,5 s** |
| `uv pip install` **sem** cache | **3,6 s** |
| `uv pip install` com cache quente | **3,0 s** |

Cerca de **7 vezes mais rápido** neste teste, que foi limitado pela internet.
Em cenários dominados por cache local — recriar um ambiente que você já teve —
a diferença chega facilmente a **10 a 100 vezes**, porque o uv não copia arquivos:
ele cria *hard links* (atalhos no nível do disco) a partir de um cache central.

> **Opinião profissional, marcada como tal:** velocidade não seria motivo suficiente
> para trocar de ferramenta. O motivo real é a **unificação** — uma ferramenta em vez
> de sete — e o **lockfile universal**, que discuto no arquivo 13. A velocidade é o
> que faz as pessoas experimentarem; a unificação é o que faz elas ficarem.

---

## 5. Quem fez, e por que isso importa

O uv é feito pela **Astral**, empresa fundada por Charlie Marsh, a mesma do **Ruff**
(um verificador de estilo de código Python igualmente rápido). Foi lançado em
**15 de fevereiro de 2024**, escrito na linguagem **Rust** — que compila para um
programa único, sem depender de Python para funcionar. Esse detalhe tem consequência
prática: o uv consegue instalar o *próprio Python*, porque não precisa de Python para
existir.

Em **19 de março de 2026**, a OpenAI anunciou a aquisição da Astral, e a equipe passou
a integrar o time do Codex. As ferramentas seguem abertas e com licença permissiva
(MIT/Apache-2.0), mas a governança mudou de dono. Isso é um fato relevante para quem
vai apostar no uv em produção, e está discutido com honestidade em
[65-estado-da-arte.md](65-estado-da-arte.md) e em [80-custos-e-licencas.md](80-custos-e-licencas.md).

---

## 6. O que o uv **não** é

Confusões comuns, corrigidas de uma vez:

- **Não é uma linguagem nova.** Você continua escrevendo Python normal.
- **Não é um editor de código.** Continue usando VS Code, PyCharm, Vim, o que preferir.
- **Não é o conda.** O conda gerencia também bibliotecas de sistema em C/Fortran e
  ambientes científicos inteiros; o uv gerencia pacotes Python (com wheels binários).
  Para 90% dos casos o uv basta e é melhor; para alguns casos científicos pesados,
  o conda ainda tem vantagem. Comparação honesta em [20-migracao.md](20-migracao-de-pip-poetry-conda.md).
- **Não substitui o Git.** Git versiona o *seu* código; o uv versiona as *dependências*.
- **Não é obrigatório.** `pip` continua funcionando e não vai acabar amanhã.

---

## 7. Uma volta completa, em cinco linhas

Se você quiser ver do que se trata antes de ler mais qualquer coisa:

```bash
uv init bolo            # cria o projeto
cd bolo
uv add requests         # adiciona um ingrediente, com versão travada
uv run python -c "import requests; print(requests.get('https://example.com').status_code)"
# esperado: 200
```

Não houve `python -m venv`. Não houve `source .venv/bin/activate`. Não houve
`pip install`. O uv criou o ambiente virtual, resolveu as versões, escreveu o
`uv.lock`, instalou e executou. Foi isso que mudou.

---

## 8. Os cinco porquês, aplicados

Vamos até o fundo em uma pergunta só, para você ver o padrão que este curso usa.

**Por que o Python precisa de ambientes virtuais?**
Porque a instalação de pacotes é global por padrão: tudo vai para uma pasta
`site-packages` única.

**Por que ela é global por padrão?**
Porque o `import` do Python resolve nomes por uma lista de caminhos (`sys.path`), e o
desenho original, de 1991, assumia uma única biblioteca compartilhada na máquina —
como faziam as linguagens da época (Perl, Tcl).

**Por que ninguém consertou isso na própria linguagem?**
Porque consertar exigiria mudar o mecanismo de `import` e quebrar compatibilidade com
todo o código existente. A comunidade escolheu, repetidamente, a compatibilidade.
Foi uma **decisão histórica documentada**, não um descuido.

**Por que a solução (o ambiente virtual) é uma pasta e não algo mais elegante?**
Porque a pasta é o truque mais barato que engana o `sys.path` sem tocar no interpretador:
um `.venv/bin/python` que aponta para o interpretador real e um `pyvenv.cfg` que
redireciona a busca de pacotes. É um *hack* que funcionou tão bem que virou padrão
(PEP 405, de 2012).

**Por que o uv não elimina o ambiente virtual, então?**
**Trade-off econômico explícito:** eliminar exigiria um mecanismo de import próprio e
quebraria a compatibilidade com todo o ecossistema — editores, depuradores, servidores.
O uv escolheu **automatizar o hack em vez de substituí-lo**: ele cria e mantém o `.venv`
para você, e você quase nunca precisa saber que ele existe. É pior teoricamente, é
muito melhor na prática.

Esse é o padrão do curso: não paramos em "é assim porque é o padrão".

---

## Autoteste

1. Em uma frase, o que o uv resolve que o `pip` sozinho não resolve?
2. Por que um `requirements.txt` com `requests` sem versão é um problema?
3. Qual a diferença entre o *carrinho de compras* e a *nota fiscal* na analogia — e que
   arquivos reais correspondem a cada um?
4. Por que o fato de o uv ser escrito em Rust permite que ele instale o próprio Python?
5. Cite duas das sete ferramentas que o uv substitui e diga o que cada uma fazia.
6. O uv elimina o ambiente virtual? Justifique com o trade-off apresentado.
7. Qual mudança de dono aconteceu com o uv em 2026, e por que isso pode importar para
   quem o adota em produção?

---

**Fontes desta página:** medições executadas localmente em 31/08/2026 (uv 0.12.7,
Ubuntu 22.04, Python 3.10.12); [astral.sh/blog/uv](https://astral.sh/blog/uv) (15/02/2024);
[openai.com/index/openai-to-acquire-astral](https://openai.com/index/openai-to-acquire-astral/) (19/03/2026).

**Próximo:** [02-pre-requisitos.md](02-pre-requisitos.md)
