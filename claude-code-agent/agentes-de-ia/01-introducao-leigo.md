# 01 · O que é um agente de IA

**Nível:** iniciante · **Zero jargão** · Atualizado em 13/08/2026

---

## A diferença entre pedir uma receita e contratar um cozinheiro

Você quer um bolo.

**Caminho 1 — o chatbot.** Você pergunta "como faço um bolo de cenoura?".
Recebe um texto perfeito: ingredientes, temperatura, tempo. O texto é ótimo.
E você continua sem bolo. Todo o trabalho — comprar, medir, misturar, assar,
provar, corrigir o sal — continua sendo seu.

**Caminho 2 — o cozinheiro.** Você diz "quero um bolo de cenoura para
domingo". Ele abre a geladeira (e descobre que não tem ovo), vai ao mercado,
volta, mistura, põe no forno, **espeta um palito para ver se assou**, e se
sair cru devolve ao forno por mais dez minutos. No domingo você tem bolo.

Um **agente de IA** é o caminho 2.

A diferença não está na inteligência: o chatbot pode saber tanto de bolo
quanto o cozinheiro. A diferença é que o cozinheiro tem **mãos** (pode abrir a
geladeira, mexer a panela) e tem um **ciclo**: age, olha o resultado, corrige,
age de novo — até o bolo estar pronto.

Guarde essas três palavras. Elas são o assunto inteiro:

| Palavra | No cozinheiro | No agente de IA |
|---|---|---|
| **Objetivo** | "bolo de cenoura para domingo" | o que você pediu |
| **Ferramentas** | geladeira, forno, faca, mercado | ler arquivo, rodar comando, buscar na web |
| **Ciclo** | espeta o palito, volta ao forno | tenta, verifica, corrige, repete |

---

## Por que isso é novo

Programas de computador sempre tiveram "mãos". Um script que renomeia mil
arquivos tem mãos. O que ele não tem é **julgamento**: alguém precisou dizer,
antes, exatamente o que fazer, em que ordem, e o que fazer se der errado. Um
script é uma receita escrita com antecedência.

Os modelos de linguagem — o que está por trás do ChatGPT, do Claude, do
Gemini — trouxeram julgamento, mas nasceram sem mãos. Eles produzem texto e
só. Pergunte "o teste está passando?" e o modelo, sozinho, não tem como
saber: ele nunca rodou nada.

Um agente é a costura das duas coisas: **um modelo que decide + ferramentas
que executam + um laço que repete até terminar.** Nenhuma das três peças é
nova. A combinação, funcionando de forma confiável, é de 2023 em diante — e
só ficou realmente boa em 2025–2026.

> **Sua opinião profissional é bem-vinda a partir daqui.** Ao longo do curso,
> tudo que for opinião minha estará marcado assim. Esta é a primeira: *a
> palavra "agente" foi tão usada em propaganda que perdeu o sentido em 2024–
> 2025. Quando alguém disser "agente", pergunte: ele decide o próximo passo
> sozinho, ou eu escrevi o fluxograma? Se você escreveu o fluxograma, é um
> **workflow** — o que é ótimo, e frequentemente melhor. Só não é um agente.*

---

## O Claude Code, concretamente

O **Claude Code** é um agente de IA da Anthropic que mora no seu terminal —
aquela tela preta com texto. Você digita `claude` na pasta de um projeto, e a
partir daí conversa em português normal.

O que muda em relação a conversar com um chatbot no navegador: ele **está
dentro da sua pasta**. Ele pode ler seus arquivos, escrevê-los, rodar
comandos (`git status`, `npm test`, `python meuscript.py`), buscar na web e
ver o resultado de tudo isso.

Um diálogo real se parece com isto:

```
> os testes do módulo de pagamento estão falhando, descubra por quê

● Vou rodar a suíte para ver o erro.
  Bash(npm test -- payments)
  ⎿  FAIL src/payments/refund.test.ts
        expected 1500, received 1499

● O erro é de arredondamento. Vou ler o cálculo.
  Read(src/payments/refund.ts)
  ⎿  42 linhas

● Achei: linha 28 usa Math.floor onde deveria ser Math.round.
  Edit(src/payments/refund.ts)

● Rodando de novo para confirmar.
  Bash(npm test -- payments)
  ⎿  PASS  12 testes

  Era arredondamento de centavos no reembolso parcial: `Math.floor`
  descartava a fração em vez de arredondar. Corrigido na linha 28.
```

Olhe a estrutura, não o conteúdo. Ele **rodou** o teste (não adivinhou o
erro), **leu** o arquivo, **editou**, e **rodou de novo para verificar**. Esse
último passo é o palito no bolo, e é o que separa um agente de um gerador de
texto convincente.

---

## Quatro perguntas que todo iniciante faz

### "Ele pode apagar meus arquivos?"

Pode — se você deixar. Por padrão, ele **pergunta** antes de editar arquivos
ou rodar comandos, e você aprova um a um. Existem modos mais soltos, que você
escolhe conscientemente (`Shift+Tab` alterna entre eles). Além disso, toda
edição de arquivo é reversível: `Esc` duas vezes desfaz.

O que **não** é reversível é o mundo lá fora. Se ele rodar um comando que
apaga uma tabela no banco de produção, não existe desfazer. Por isso ele
pergunta antes de comandos com efeito externo, e por isso o capítulo
[17-hooks-permissoes-seguranca.md](17-hooks-permissoes-seguranca.md) existe.

### "Ele envia meu código para a internet?"

Sim, e não há como não enviar: o modelo roda nos servidores da Anthropic. O
que vai é o que entra no contexto — os arquivos que ele lê, os comandos que
ele roda e as saídas deles. O que não vai são arquivos que ele nunca abriu.
Se isso é aceitável no seu caso é uma decisão de política, não técnica;
[80-custos-e-licencas.md](80-custos-e-licencas.md) trata do assunto,
incluindo as opções de retenção zero de dados para empresas.

### "Preciso saber programar?"

Para o Claude Code, sim — pelo menos o básico. Não porque você vá digitar
código, mas porque **você é quem revisa**. Um agente que escreve 200 linhas
que você não sabe ler é um passivo, não um ativo. Ele erra, e erra com
convicção.

Para entender *agentes de IA* como assunto, não. Este arquivo e o
[10-fundamentos.md](10-fundamentos.md) não exigem programação.

### "Isso substitui programador?"

Não em 2026, e a razão é chata: alguém precisa decidir o que construir,
julgar se ficou bom, e responder quando quebrar em produção. O que mudou de
verdade é a proporção — muito menos tempo digitando, muito mais tempo
especificando e revisando. Quem escreve especificação ruim recebe software
ruim mais rápido do que antes.

---

## Onde os agentes já são usados de verdade

Fora do marketing, os usos que se sustentam em 2026 têm uma coisa em comum:
**existe uma forma barata de verificar se deu certo.**

| Uso | Como se verifica |
|---|---|
| Corrigir bug com teste que reproduz | o teste passa ou não |
| Migração mecânica em muitos arquivos | compila e a suíte continua verde |
| Revisão de código | um humano lê os achados |
| Pesquisa com fontes citadas | você abre os links |
| Triagem de tickets | o humano confirma ou reclassifica |

E os usos que decepcionam têm o defeito oposto: nada checa o resultado.
"Escreva a estratégia da empresa" produz um texto plausível que ninguém sabe
avaliar — e plausível-mas-errado é pior que obviamente errado, porque passa.

---

## O caminho daqui

Se você quer **usar** o Claude Code hoje:
[02](02-pre-requisitos.md) → [03](03-instalacao.md) → [04](04-como-comecar.md)
→ [05](05-manual-de-uso.md).

Se você quer **entender** agentes como assunto, e depois usar:
[10](10-fundamentos.md) → [11](11-historia.md) → [12](12-anatomia-do-loop-agentico.md).

O mapa completo está em [00-MAPA.md](00-MAPA.md).

---

## Autoteste

1. Qual é a diferença entre um chatbot e um agente, em uma frase, sem usar a
   palavra "inteligente"?
2. Das três palavras-chave (objetivo, ferramentas, ciclo), qual falta num
   programa comum de computador?
3. No diálogo do módulo de pagamento, qual passo é "o palito no bolo"? O que
   aconteceria se ele fosse omitido?
4. Por que uma edição de arquivo é reversível e um comando que altera um banco
   de dados remoto não é?
5. Um colega diz "montei um agente que resume os e-mails da noite e manda no
   Slack, sempre nessa ordem". Isso é agente ou workflow? Por quê?
6. Dê um exemplo de tarefa em que um agente provavelmente decepciona, e diga
   qual característica está faltando.
7. Por que "plausível mas errado" é considerado pior que "obviamente errado"
   quando o assunto é agente?
