# 01 · O que é o n8n — explicado para quem nunca ouviu falar

`Nível: iniciante` · `Sem jargão` · `Atualizado em: 01/09/2026`

---

## 1. A analogia: a linha de montagem de escritório

Imagine uma padaria. Chega uma encomenda por telefone. Alguém anota num papel.
Alguém leva o papel para a cozinha. A cozinha assa. Alguém embala. Alguém liga
para o cliente avisando que ficou pronto. Alguém lança a venda no caderno.

Seis pessoas, seis passos, e o **papel andando entre elas**.

Agora troque a padaria por uma empresa e o papel por dados:

- chega um formulário preenchido no site;
- alguém copia os dados para a planilha;
- alguém confere se o CPF é válido;
- alguém cria o cliente no sistema de vendas;
- alguém manda um e-mail de boas-vindas;
- alguém avisa o time no chat.

Se você trocar cada "alguém" por um programa e o "papel" por um pacotinho de
dados que passa de um programa para o outro, você acabou de descrever o n8n.

> **n8n é uma esteira: você desenha as estações de trabalho e a ordem entre elas,
> e a esteira carrega os dados de uma estação para a próxima, sozinha, para sempre.**

Essa esteira desenhada tem um nome próprio: **workflow** (fluxo de trabalho).
Cada estação é um **node** (nó). O pacotinho de dados que anda é um **item**.
Cada vez que a esteira roda do começo ao fim é uma **execution** (execução).

Esses quatro termos — workflow, node, item, execution — são 90% do vocabulário.
Guarde-os. Tudo o mais é detalhe.

---

## 2. O que você vê na tela

Você abre o navegador em um endereço, vê uma tela branca com um botão de `+`, e
começa a arrastar caixinhas e ligá-las com fios:

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Recebe um   │─────▶│  Confere se  │─────▶│  Grava no    │
│  formulário  │      │  é válido    │      │  banco       │
└──────────────┘      └──────┬───────┘      └──────────────┘
     GATILHO                 │
                             │ (se inválido)
                             ▼
                      ┌──────────────┐
                      │ Avisa no chat│
                      └──────────────┘
```

A primeira caixinha é sempre especial: é o **gatilho** (*trigger*), aquilo que faz
a esteira ligar. Pode ser "alguém mandou dados para este endereço",
"são 8 da manhã de segunda", "chegou e-mail novo", "alguém falou comigo no chat".

Sem gatilho, o fluxo é um desenho parado. Com gatilho, é um funcionário que nunca
dorme, nunca esquece e nunca digita o CPF errado.

---

## 3. Para que serve, na prática, com exemplos reais

Nada de exemplos abstratos. Coisas que gente de verdade faz com n8n:

| Problema real | O que o fluxo faz |
|---|---|
| "Toda nota fiscal que chega por e-mail eu tenho que baixar o PDF e renomear" | Gatilho de e-mail → extrai anexo → lê o número da nota → renomeia → joga no Drive |
| "Preciso saber quando um concorrente muda o preço" | Gatilho de horário (de hora em hora) → busca a página → compara com o valor anterior → se mudou, manda no WhatsApp |
| "O time de vendas não sabe quando um lead preenche o formulário" | Gatilho de webhook → valida → cria no CRM → posta no canal do Slack com o resumo |
| "Quero um robô de atendimento que responda com base nos meus manuais" | Gatilho de chat → busca trechos relevantes dos manuais → manda para um modelo de IA → responde |
| "Toda segunda eu monto o mesmo relatório na mão" | Gatilho semanal → consulta o banco → monta a planilha → envia por e-mail |
| "Dois sistemas da empresa não se falam" | Gatilho de mudança no sistema A → transforma o formato → grava no sistema B |

Repare no padrão: **algo acontece → pego dados → mexo nos dados → coloco em outro lugar**.
Isso tem nome no mercado: **integração** e **automação de processos**.
O n8n é uma ferramenta para desenhar isso sem escrever um programa inteiro.

---

## 4. Por que isso existe? (o problema que fez nascer)

Antes de existir ferramenta assim, você tinha três opções, todas ruins:

**Opção 1 — fazer na mão.** Barato de começar, caríssimo de manter. Uma pessoa
copiando dados oito horas por dia é uma pessoa cara errando 2% das vezes.

**Opção 2 — escrever um programa.** Funciona, mas: alguém precisa saber programar,
alguém precisa hospedar, alguém precisa cuidar quando quebra às 3 da manhã, e
cada integração nova é um projeto novo. A parte cara não é escrever — é *manter*.
Um script que lê e-mail, fala com o CRM e posta no Slack tem três autenticações,
três formatos de dados e três formas de falhar. E ele quebra silenciosamente.

**Opção 3 — comprar uma ferramenta de integração corporativa.** Existiam desde os
anos 1990 (chamavam-se ESB, *Enterprise Service Bus*, e depois iPaaS). Funcionam,
custam dezenas de milhares por ano, exigem consultoria e levam meses.

O que ferramentas como o n8n fizeram foi ocupar o buraco no meio: **poder de
programa, esforço de desenho**. Você desenha 80% e escreve código só nos 20% que
o desenho não resolve. Esse "escrever só onde precisa" tem nome de mercado:
**low-code** (pouco código).

E há um quarto motivo, específico do n8n, que veremos no arquivo
[11-historia.md](11-historia.md): as ferramentas concorrentes eram **serviços
na nuvem de terceiros**. Seus dados, suas senhas de sistemas e seus processos
passavam pela máquina de outra empresa. Muita gente não pode, ou não quer, isso.
O n8n pode rodar **na sua própria máquina**.

---

## 5. Os cinco porquês — por que o n8n é como é

Vamos aplicar a regra da casa: não parar no primeiro nível.

**1. Por que existe um n8n?**
Porque conectar sistemas na mão é caro e errado, e escrever código para cada
conexão é caro de manter.

**2. Por que é caro de manter escrever esse código?**
Porque cada sistema tem sua autenticação, seu formato, seus limites de uso e
seus modos de falhar. O código de "negócio" é 10% — os outros 90% são encanamento
repetido: autenticar, paginar, tentar de novo, tratar erro, registrar o que houve.

**3. Por que esse encanamento se repete tanto?**
Porque a indústria padronizou o *transporte* (HTTP, JSON, OAuth 2.0) mas nunca
padronizou a *semântica*. Todo mundo fala JSON sobre HTTP; ninguém concorda no
que é um "cliente". Então o transporte pode ser resolvido uma vez por uma
ferramenta — e é exatamente isso que um node do n8n é: encanamento resolvido.

**4. Por que uma ferramenta visual, e não uma biblioteca de código?**
Porque quem conhece o processo (o pessoal de operações, de vendas, de suporte)
não é quem programa. Uma tela com caixas e fios é um **artefato compartilhado**:
a pessoa de negócio lê o desenho e diz "aqui está errado". Um arquivo de 400
linhas de TypeScript não é lido por ninguém fora da engenharia. Isso é ganho de
comunicação, não de digitação. *(Opinião profissional, não consenso: essa é a
verdadeira razão pela qual o low-code sobrevive, e não a promessa de "programar
sem programador" — que quase nunca se cumpre.)*

**5. Por que o n8n insiste em poder rodar na sua máquina, se hospedar dá trabalho?**
Decisão histórica documentada e deliberada: o fundador, Jan Oberhauser, publicou
o código-fonte no GitHub em **4 de outubro de 2019**, num momento em que o líder
de mercado (Zapier) era 100% fechado e 100% na nuvem. O diferencial competitivo
que restava para um entrante era exatamente o que o líder não podia oferecer:
**o código na sua mão e os dados na sua infraestrutura**. Foi estratégia, não
ideologia. E a licença escolhida — que **não** é software livre no sentido estrito
(veja [80-custos-e-licencas.md](80-custos-e-licencas.md)) — mostra que a intenção
era comercial desde o começo.

Parada legítima alcançada: decisão histórica documentada + trade-off econômico explícito.

---

## 6. O que o n8n NÃO é

Tão importante quanto o que ele é. Guarde para não se frustrar:

- **Não é um substituto para programar.** Fluxos complexos viram um emaranhado
  pior de manter que código. Existe um ponto de virada; ele será discutido em
  [75-armadilhas.md](75-armadilhas.md).
- **Não é um sistema de processamento de dados em massa.** Se você precisa
  transformar 50 milhões de linhas, isso é trabalho de banco de dados ou de
  ferramenta de ETL, não de n8n. Ele passa os dados **na memória** entre nós.
- **Não é um servidor de aplicação.** Dá para expor um endpoint HTTP com o node
  Webhook, e às vezes isso é ótimo; mas uma API de produto com milhares de
  requisições por segundo não é trabalho para ele.
- **Não é grátis para tudo.** É gratuito para uso interno da sua empresa. Se você
  quiser hospedar fluxos *dos seus clientes* ou embutir o n8n no seu produto,
  precisa de licença paga. Detalhes, com o texto da licença, em
  [80-custos-e-licencas.md](80-custos-e-licencas.md).
- **Não é "sem manutenção".** Todo fluxo é um programa em produção. Ele quebra
  quando a API do outro lado muda. A diferença é que ele quebra *visivelmente*.

---

## 7. Como o n8n se compara ao que você talvez já conheça

| Ferramenta | Modelo | Roda na sua máquina? | Ponto forte | Ponto fraco |
|---|---|---|---|---|
| **n8n** | Nós + fios, low-code | **Sim** | Controle total, código onde precisa, forte em IA | Você cuida do servidor |
| **Zapier** | Gatilho + ações lineares | Não | Facílimo, milhares de apps | Caro no volume, lógica limitada |
| **Make** (ex-Integromat) | Nós + fios visual | Não | Visual excelente, barato | Fechado, sem autogestão |
| **Power Automate** | Fluxos Microsoft | Parcial | Integra o mundo Microsoft/365 | Preso ao ecossistema |
| **Apache Airflow** | Código Python, DAGs | Sim | Padrão de dados/ETL | Não é para integração de apps, exige programador |
| **Escrever você mesmo** | Código | Sim | Sem limites | Manutenção é sua, para sempre |

A comparação honesta e com números está em
[80-custos-e-licencas.md](80-custos-e-licencas.md). Aqui basta a regra prática:

> Se você não pode ou não quer que seus dados passem por servidor de terceiros,
> ou se seu volume é grande o bastante para que o preço por execução doa,
> o n8n entra na conversa. Se são cinco automações simples e ninguém liga para
> onde os dados passam, o Zapier resolve em uma tarde e você não lê mais nada disto.

---

## 8. O nome

`n8n` lê-se **"n-eight-n"** (ou, em português, "ene-oito-ene"). É uma
**numerônimo**: `nodemation` → `n` + as 8 letras `odematio` + `n`. O termo
`nodemation` era a junção de *node* (nó) com *automation* (automação).

Não tem significado profundo. É só um nome curto e disponível como domínio.
Conta como "convenção arbitrária" na regra dos cinco porquês.

---

## 9. O caminho daqui em diante

Você acabou de ler a camada 1 (intuição) e a camada 3 (por que existe).
A ordem sugerida é:

1. [02-pre-requisitos.md](02-pre-requisitos.md) — o que você precisa saber e ter antes.
2. [03-instalacao.md](03-instalacao.md) — pôr o n8n para rodar, no seu sistema.
3. [04-como-comecar.md](04-como-comecar.md) — o primeiro fluxo funcionando.
4. [10-fundamentos.md](10-fundamentos.md) — aí sim, os conceitos com nome e sobrenome.

Se você tem pressa e só quer ver a ferramenta funcionando hoje, pule direto para
a seção "**Alternativa sem instalar nada**" do
[03-instalacao.md](03-instalacao.md#alternativa-sem-instalar-nada).

---

## Autoteste

Responda sem olhar para cima:

1. Explique, sem usar as palavras "workflow" e "node", o que o n8n faz.
2. O que é um **gatilho** e por que um fluxo sem gatilho é inútil?
3. Cite três problemas do dia a dia de uma empresa que o n8n resolveria.
4. Qual é a diferença essencial entre o n8n e o Zapier — a que faz um existir
   apesar do outro?
5. Por que "escrever um programa" costuma ser mais caro do que parece? Qual é a
   proporção entre código de negócio e código de encanamento?
6. Cite duas coisas que o n8n **não** é, e explique por quê.
7. O n8n é software livre? (A resposta honesta é "não exatamente" — você saberá
   defendê-la depois de ler o arquivo 80.)
8. De onde vem o nome "n8n"?

---

*Próximo: [02-pre-requisitos.md](02-pre-requisitos.md)*
