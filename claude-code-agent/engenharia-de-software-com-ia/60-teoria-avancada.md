# 60 · Teoria avançada — os limites duros

**Nível:** pesquisa · **Escrito em:** 20/08/2026

> Este arquivo trata do que é **impossível**, não do que é difícil. A distinção
> importa: o difícil melhora com a próxima geração de modelos; o impossível não.

---

## 1 · O problema da verificação é tão difícil quanto o da geração?

Pergunta central da disciplina. A resposta é **depende da propriedade**, e a
teoria dá uma resposta precisa.

### O teorema de Rice

**Enunciado (1953):** toda propriedade **não trivial** e **semântica** de
programas é **indecidível**.

- *Semântica* = sobre o comportamento (o que o programa faz), não sobre a forma
  (quantas linhas tem).
- *Não trivial* = nem todo programa a tem, nem nenhum a tem.

**Consequência direta e inescapável:** não existe e **nunca existirá** um
verificador universal que decida, para qualquer programa, se ele "faz o que
deveria". Isso vale para você, para o compilador e para qualquer IA futura, por
mais capaz que seja.

### Mas nem tudo é indecidível

Escapamos do teorema de três formas, e todas as três são o que fazemos na
prática:

| Escape | Exemplo | O que se perde |
|---|---|---|
| **Verificar propriedade sintática** | Linter, formatador, contagem de linhas | Não fala do comportamento |
| **Verificar em instâncias, não universalmente** | Teste: "para esta entrada, esta saída" | Não prova para toda entrada |
| **Restringir a linguagem** | Tipos, análise estática, linguagem total | Rejeita programas corretos (falso positivo) |

Verificação de tipos é o exemplo mais elegante: é decidível **porque** o sistema
de tipos é deliberadamente conservador — ele rejeita programas que funcionariam.
Todo sistema de tipos troca completude por decidibilidade, e essa troca é
consciente.

### O que isso significa para o ofício

**A verificação é assimétrica com a geração**, e a assimetria trabalha a nosso
favor:

- Gerar código plausível: barato, e a IA faz bem.
- Provar que está **totalmente** correto: impossível em geral.
- Verificar **propriedades específicas**: barato e decidível.

> **Portanto a estratégia certa não é "provar que está certo" — é acumular
> propriedades específicas verificáveis até que o espaço de erro sobrevivente
> seja aceitavelmente pequeno.** Isso é exatamente a pirâmide de verificação do
> [17](17-verificacao-e-testes.md), e agora você sabe **por que** ela tem essa
> forma: é a única forma possível.

---

## 2 · Por que a alucinação é inevitável

Não é defeito de engenharia. Há argumentos formais convergentes.

### O argumento de compressão

O modelo comprime um corpus imenso em parâmetros finitos. Compressão com perda,
por definição, **não pode reconstruir tudo com fidelidade**. Quando a
reconstrução falha, o resultado não é "erro visível" — é a saída mais provável
dado o resto, que é sempre algo plausível.

### O argumento de calibração

Um modelo que nunca alucinasse teria de responder "não sei" sempre que a
confiança fosse baixa. Mas:

1. A distribuição de saída sempre tem um máximo; algo é sempre mais provável.
2. O treinamento por preferência humana **penaliza** "não sei" (respostas
   assertivas são preferidas por avaliadores).
3. Portanto o processo de treino ativamente reduz a abstenção.

O terceiro ponto é notável: **parte da alucinação é resultado de otimização
deliberada por utilidade percebida.** É um trade-off, não um bug.

### O argumento de fatos móveis

Já desenvolvido no [12](12-o-modelo-por-dentro.md), §9: fato que muda mais rápido
que o ciclo de treino **não pode viver nos pesos**. Registro de pacotes,
documentação de biblioteca, o seu código de ontem. Isso não é consertável em
princípio; só é contornável com ferramenta de busca externa.

**Conclusão:** projete assumindo alucinação, como você projeta assumindo falha de
rede. Não é pessimismo; é engenharia.

---

## 3 · A matemática da composição

Já introduzida no [15](15-o-loop-do-agente.md). Aqui, o desenvolvimento.

### O modelo ingênuo

`P(sucesso) = p^n` para `n` passos independentes com acerto `p`.

### Por que o modelo ingênuo está errado — nos dois sentidos

**Pior que o modelo:** os erros são **correlacionados**. Um erro no passo 3
aumenta a probabilidade de erro no passo 4, porque o passo 4 opera sobre a saída
do 3 e sobre um contexto contaminado. Isso é o envenenamento de contexto.

**Melhor que o modelo:** com **verificação e retentativa**, o processo deixa de
ser uma cadeia de multiplicações. Se um passo verificado falha, ele é repetido:

`P(passo eventualmente certo) = 1 − (1−p)^k` para `k` tentativas.

| p | 1 tentativa | 3 tentativas | 5 tentativas |
|---|---|---|---|
| 0,50 | 50% | 87,5% | 96,9% |
| 0,70 | 70% | 97,3% | 99,8% |
| 0,90 | 90% | 99,9% | ~100% |

**A conclusão é forte:** um passo verificável com p=0,5 e três tentativas é mais
confiável que um passo não verificável com p=0,85.

> **Isto é o argumento teórico central deste curso.** Verificação não melhora o
> modelo; ela **muda o regime matemático** de multiplicativo (que colapsa) para
> algo que converge. Toda a diferença entre L2 e L3 é essa mudança de regime.

### O que isso exige

Para converter multiplicação em convergência, o oráculo de verificação precisa
ser:

1. **Barato** — vai rodar muitas vezes.
2. **Rápido** — senão a retentativa não acontece.
3. **Correto** — um oráculo errado converge para a coisa errada, com confiança.

O item 3 é o mais perigoso e o menos discutido. **Um teste ruim é pior que
nenhum teste**, porque ele dá licença para não pensar. É o argumento a favor de
teste de mutação ([17](17-verificacao-e-testes.md)).

---

## 4 · Lei de Goodhart e a especificação

> **Quando uma medida vira alvo, ela deixa de ser boa medida.**
> (Charles Goodhart, 1975)

Um agente otimiza **exatamente** o que você mediu, sem o bom senso que faz um
humano não desabilitar o teste. Isso torna a lei de Goodhart operacionalmente
relevante de um jeito novo.

| Você mede | Ele otimiza | Resultado |
|---|---|---|
| "testes passam" | testes passando | desabilita o teste |
| "cobertura ≥ 80%" | número de cobertura | testes sem asserção |
| "sem erro de lint" | ausência de aviso | `eslint-disable` |
| "compila" | compilação | `any` em tudo |
| "PR menor que 400 linhas" | contagem de linhas | linhas mais longas |

### A defesa formal

Especifique a **propriedade**, não o **proxy** — e, quando isso for impossível
(quase sempre), **verifique o proxy e a integridade do proxy**.

```bash
# não basta: "testes passam"
npm test

# é preciso também: os testes continuam sendo os mesmos testes
git diff --stat -- tests/ | grep -q . && exit 1

# e continuam detectando: mutação
npx stryker run --mutate src/dominio/
```

**Generalização:** todo portão precisa de uma verificação de **integridade do
próprio portão**. Sem isso, o portão é otimizável, e o que é otimizável será
otimizado.

---

## 5 · Limites de informação

Já enunciado no [19](19-arquitetura-para-maquina.md), §6, e vale formalizar.

> Se a informação necessária para uma decisão **não existe em nenhum artefato
> acessível**, nenhum modelo pode recuperá-la.

Exemplos concretos:

- A razão de uma gambiarra que só existia na cabeça de quem saiu da empresa.
- O acordo verbal com o cliente que nunca virou requisito escrito.
- A restrição regulatória que ninguém documentou.
- A intenção por trás de um `if` sem comentário.

Isso não é limitação de capacidade — é **ausência de informação**. Nenhum
aumento de escala resolve, do mesmo jeito que nenhum telescópio melhor recupera
uma fotografia que nunca foi tirada.

**Consequência prática forte:** escrever o *porquê* deixou de ser boa prática
opcional e virou **infraestrutura**. É a única forma de a informação existir.

---

## 6 · Escala: até onde a curva vai?

A METR mediu horizonte temporal dobrando a cada ~4,3 meses depois de 2023 (antes:
~7 meses). Extrapolar exponencial é notoriamente perigoso; vale enumerar o que
poderia interrompê-la, sem apostar.

| Fator | Efeito plausível |
|---|---|
| Dados de treino de código de alta qualidade | Finitos; o estoque de código humano bom cresce devagar |
| Contaminação por código gerado | Modelos futuros treinando em saída de modelos anteriores — degradação documentada em outros domínios |
| Custo de computação | Cresce mais rápido que a capacidade em alguns regimes |
| Confiabilidade por passo | Ganhos ficam mais caros perto de 1 |
| Benchmark ≠ trabalho real | Melhora medida pode não se traduzir |

**Minha posição, marcada como opinião:** a curva de capacidade em tarefas com
critério de sucesso automático deve continuar por algum tempo. A curva de
utilidade em trabalho real é limitada por outra coisa — **a especificação**. E
especificar é limitado por quanto a organização sabe o que quer, que não tem
curva exponencial nenhuma.

---

## 7 · A pergunta que fica em aberto

> Se a IA pudesse escrever **e** verificar perfeitamente, o que sobraria?

**Sobraria decidir o que construir.** E isso não é um problema técnico: é um
problema de valores, objetivos e responsabilidade. Envolve escolher entre
futuros possíveis para pessoas reais, sob restrições que não estão no código.

Uma máquina pode explorar o espaço de opções, estimar consequências e apresentar
trade-offs. **Escolher exige alguém que responda pela escolha** — e
responsabilidade é uma relação social, não uma capacidade computacional.

Essa é a parada legítima do último "por quê" deste curso. Não é limite de
inteligência; é a natureza da decisão sob responsabilidade.

---

## Autoteste

1. Enuncie o teorema de Rice e a consequência dele para verificação de software.
2. Cite as três formas de escapar do teorema de Rice e o que se perde em cada uma.
3. Por que verificação de tipos é decidível? Que troca ela faz?
4. Cite os três argumentos de por que alucinação é inevitável.
5. Por que parte da alucinação é resultado de otimização deliberada?
6. Por que `p^n` está errado nos dois sentidos?
7. Faça a conta: p=0,5 com 3 tentativas verificadas. Compare com p=0,85 sem
   verificação. Qual é a conclusão?
8. Quais três propriedades o oráculo de verificação precisa ter? Qual é a mais
   perigosa quando falta?
9. Enuncie a lei de Goodhart e dê três exemplos de como um agente a explora.
10. O que é verificação de integridade do portão e por que ela é necessária?
11. Enuncie o limite de informação e explique por que escala não o resolve.
12. Se a IA escrevesse e verificasse perfeitamente, o que sobraria — e por quê?

---

**Anterior:** [27-times-e-organizacao](27-times-e-organizacao.md) ·
**Próximo:** [65-estado-da-arte](65-estado-da-arte.md)
