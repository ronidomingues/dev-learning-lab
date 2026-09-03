# 13 · Os quatro modos de uso — e qual escolher

**Nível:** intermediário · **Escrito em:** 20/08/2026

---

## O erro de tratar "usar IA" como uma coisa só

Existem quatro modos, e eles têm perfis de risco, custo e ganho **radicalmente
diferentes**. Boa parte da confusão do mercado — inclusive estudos que se
contradizem — vem de misturar todos sob o mesmo nome.

```
                 controle do dev              autonomia da máquina
    ┌──────────────────────────────────────────────────────────►
    │
 1  │ COMPLETAR    você digita, ela adivinha o fim
 2  │ CONVERSAR    você pergunta, ela responde, você aplica
 3  │ EDITAR       você aponta, ela altera, você aprova o diff
 4  │ AGIR         você delega, ela trabalha, você recebe o resultado
    │
    ▼
```

---

## Modo 1 · Completar

**O que é:** sugestão de linha ou bloco enquanto você digita.
**Ferramentas:** GitHub Copilot, Cursor Tab, Supermaven, Codeium.

| Dimensão | Avaliação |
|---|---|
| Ganho | Pequeno e constante (~5–15% do tempo de digitação) |
| Risco | Baixo por sugestão, **acumulativo** |
| Revisão | Embutida — você lê ao aceitar |
| Custo | Baixo; muitas vezes gratuito |

### O risco real, que não é o óbvio

O perigo não é a sugestão errada — essa você vê. É a **deriva por aceitação
fácil**: `Tab`, `Tab`, `Tab`, e meia hora depois existe um arquivo que você não
projetou, só aprovou linha a linha.

Sintoma clássico: a sugestão propõe uma abordagem ligeiramente diferente da que
você tinha em mente, você aceita porque está pronta, e o desenho do código passa
a ser a média estatística do GitHub em vez da sua decisão.

**Antídoto:** decida a assinatura e a estrutura **antes** de digitar. Se você
sabe onde quer chegar, a sugestão acelera; se não sabe, ela decide por você.

### Quando desligar

- Escrevendo criptografia, autenticação ou qualquer coisa de segurança.
- Escrevendo teste. **Um teste sugerido pelo modelo tende a testar o que o
  código faz, não o que ele deveria fazer** — e aí o teste vira uma tautologia.
- Aprendendo algo novo. A sugestão remove o esforço, e o esforço é onde o
  aprendizado mora.

---

## Modo 2 · Conversar

**O que é:** você pergunta, recebe explicação e código, decide o que fazer.
**Ferramentas:** qualquer chat; painel lateral do editor.

| Dimensão | Avaliação |
|---|---|
| Ganho | Alto para **entender**, médio para produzir |
| Risco | Baixo — nada é escrito sem você |
| Revisão | Total, por construção |
| Custo | Baixo a médio |

### O uso subvalorizado: perguntar, não pedir

A maioria usa o chat para pedir código. O uso com melhor retorno é usá-lo para
**entender**:

```
Explique o que este trecho faz e por que ele existe. Depois liste três
situações em que ele se comportaria de forma inesperada.
```

```
Qual é o trade-off entre estas duas abordagens no MEU caso, dado que o volume
é de 200 requisições por segundo e a consistência precisa ser forte?
```

```
Isso que eu escrevi está errado em algum caso de borda? Seja específico e
mostre a entrada que quebra.
```

### O antipadrão do modo 2

Colar o código, pedir melhoria, colar de volta **sem entender a mudança**. Você
tem todo o custo cognitivo de integrar e nenhum benefício de compreensão. É o
pior dos dois mundos, e é o modo dominante em 2026 entre quem está em L2.

---

## Modo 3 · Editar

**O que é:** você aponta arquivos ou trechos, descreve a mudança, e a ferramenta
produz um *diff* que você aprova ou rejeita.
**Ferramentas:** Aider, Cursor Composer, Claude Code em uso pontual.

| Dimensão | Avaliação |
|---|---|
| Ganho | **Alto** |
| Risco | Médio, controlável |
| Revisão | Diff explícito antes de aplicar |
| Custo | Médio |

### Por que este é o modo mais subestimado

É o ponto de equilíbrio. Você ganha a velocidade da máquina e **mantém o diff
como unidade de decisão** — que é exatamente onde a revisão humana ainda é
barata.

**Minha recomendação profissional, marcada como opinião:** a maior parte do
trabalho diário de quem está entre L2 e L4 deveria acontecer no modo 3, não no
modo 4. O modo 4 é sedutor e é onde se perde o controle primeiro.

### Como fazer bem

1. **Escolha os arquivos você.** Não deixe o agente decidir o que tocar.
2. **Uma mudança conceitual por vez.** "Extraia a validação" e "adicione o
   campo" são dois pedidos.
3. **Leia o diff inteiro.** Se ele não cabe na tela, o pedido era grande demais.
4. **Rejeite sem culpa.** Rejeitar e reformular custa 30 segundos; aceitar algo
   que você não entendeu custa semanas.

---

## Modo 4 · Agir

**O que é:** você descreve um objetivo; o agente lê, escreve, executa, corrige,
por muitos passos, e volta com o resultado.
**Ferramentas:** Claude Code, Codex, Copilot Agent, Devin, Jules.

| Dimensão | Avaliação |
|---|---|
| Ganho | **Muito alto quando dá certo** |
| Risco | **Alto** |
| Revisão | Você recebe o resultado pronto — e aí está o problema |
| Custo | Alto |

### A regra que torna o modo 4 seguro

> O modo 4 só é profissional quando existe **verificação automática** cobrindo o
> que importa. Sem isso, ele é modo 2 com passos extras e menos supervisão.

Checklist antes de delegar em modo 4:

- [ ] O repositório tem testes que rodam em menos de 5 minutos?
- [ ] Existe um comando único que diz "está bom" ou "não está"?
- [ ] O escopo do que ele pode tocar está limitado?
- [ ] Existe *branch* separado ou *worktree*?
- [ ] Existe um portão antes da `main` (ver [projeto-modelo](07-projeto-modelo/README.md))?
- [ ] O agente está sem acesso a segredos de produção?

**Menos de quatro caixas marcadas: não use o modo 4.** Use o modo 3.

### O sinal de que você perdeu o controle

Você não consegue mais explicar como o sistema funciona **sem abrir o editor**.

Esse é o alarme. Quando ele toca, pare de delegar por alguns dias, leia o que
entrou, e reconstrua o modelo mental. Não existe atalho: o custo de recuperar
compreensão perdida é maior que o de nunca tê-la perdido.

---

## Tabela de decisão

| Situação | Modo | Por quê |
|---|---|---|
| Escrevendo código que você já sabe escrever | 1 | Acelera digitação sem ceder decisão |
| Não entendo este código | 2 | Risco zero, ganho enorme |
| Decidindo entre duas arquiteturas | 2 | Explora o espaço; a decisão é sua |
| Bug conhecido, correção pequena | 3 | Diff pequeno, revisão barata |
| Refatoração com escopo claro | 3 | Diff é a unidade certa |
| Escrevendo teste para código existente | 3 ou 4 | Teste tem verificação natural: rode-o |
| Migração mecânica repetitiva | 4 **com portão** | Volume alto, verificação automatizável |
| Feature nova em área bem coberta por testes | 4 | Os testes são a rede |
| Feature nova em área sem teste | 3, e **escreva o teste primeiro** | Sem rede, não pule |
| Segurança, criptografia, autenticação | 2, e revise à mão | Erro é invisível e caro |
| Transformação determinística (renomear em massa) | **Nenhum** — use `sed`/`comby` | Ver [exemplo 4](06-exemplos.md) |
| Protótipo descartável de fim de semana | 4 sem cerimônia | Se morre amanhã, o custo de manutenção é zero |

---

## O modo 5 que está nascendo: agentes assíncronos

Em 2026 consolidou-se um quinto modo: você abre uma *issue*, marca o agente, e
ele trabalha **na nuvem**, sem você presente, e abre um PR. GitHub Copilot
Coding Agent, Jules, Codex na nuvem, Devin.

| Dimensão | Avaliação |
|---|---|
| Ganho | Alto para tarefa bem definida e verificável |
| Risco | **Alto** — ninguém observa durante a execução |
| Revisão | Só no PR, depois de tudo pronto |

**Onde funciona:** dependência a atualizar, teste faltando, correção de lint,
tarefa de "boa primeira contribuição", tradução de documentação.

**Onde falha:** qualquer coisa que exija decisão no meio do caminho. Sem humano
presente, a decisão é tomada em silêncio e você só descobre no PR — quando o
custo de reverter já é alto.

> **O número que resume o problema:** PRs de agente esperam 5,3× mais tempo
> para alguém começar a revisar (LinearB, 2026). O modo 5 desloca trabalho para
> a fila de revisão, que já é o gargalo. **Aumentar a produção sem aumentar a
> capacidade de revisão não aumenta a entrega — aumenta o estoque.** Isso é
> teoria das restrições básica, e vale aqui inteirinho.

---

## Autoteste

1. Quais são os quatro modos e como eles diferem em controle e risco?
2. Qual é o risco real do modo 1, e por que ele não é a sugestão errada?
3. Em que três situações vale desligar o autocompletar?
4. Qual é o uso subvalorizado do modo 2, e qual é o antipadrão dele?
5. Por que o modo 3 é o ponto de equilíbrio, e por que ele é subestimado?
6. Enuncie a regra que torna o modo 4 profissional.
7. Cite quatro itens do checklist do modo 4. Quantos precisam estar marcados?
8. Qual é o sinal de que você perdeu o controle do sistema, e o que fazer?
9. Quando a resposta certa é "nenhum modo"?
10. Por que o modo 5 pode aumentar o estoque em vez da entrega?

---

**Anterior:** [12-o-modelo-por-dentro](12-o-modelo-por-dentro.md) ·
**Próximo:** [14-contexto-e-o-repositorio](14-contexto-e-o-repositorio.md)
