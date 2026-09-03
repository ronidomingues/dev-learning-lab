# 20 · A parte difícil: o que fazer com o conflito

`Nível: intermediário → avançado` · `Atualizado em: 14/08/2026`

Detectar o conflito é engenharia. **Decidir o que acontece com ele é produto.** Esta é a
camada que faz optimistic locking ser lembrado como "aquela mensagem irritante" ou como algo
que o usuário nunca percebeu que existia.

Um sistema que detecta perfeitamente e responde `409 Conflict` com um stack trace protegeu os
dados e destruiu a experiência. Não é sucesso.

---

## 1. As cinco respostas possíveis

Em ordem crescente de custo de implementação — e de qualidade percebida.

| # | Resposta | Custo | Quando é a certa |
|---|---|---|---|
| 1 | **Recusar e avisar** | trivial | edição rara, dado crítico, usuário técnico |
| 2 | **Retentar sozinho** | baixo | a operação é função do estado ([`19`](19-retentativa-e-idempotencia.md)) |
| 3 | **Mesclar automaticamente** | médio | campos independentes |
| 4 | **Mostrar as duas versões** | alto | conteúdo, texto, decisões |
| 5 | **Não deixar acontecer** | variável | quando dá para avisar antes |

Sistemas maduros usam **todas as cinco**, escolhendo por tipo de campo. É comum a mesma tela
retentar sozinha um contador, mesclar campos independentes e perguntar sobre o texto.

---

## 2. Resposta 1 — recusar bem

A recusa é legítima. O que não é legítimo é recusar **mal**. Compare:

```
❌  Error: OptimisticLockException: Row was updated or deleted by another
    transaction (or unsaved-value mapping was incorrect):
    [com.empresa.Cliente#42]
```

```
✅  Suas alterações não foram salvas

    Ana Souza editou este cliente há 3 minutos, enquanto você preenchia o
    formulário. Salvar agora apagaria o que ela fez.

    Ela alterou:  telefone  (11) 2222-1111 → (11) 3333-2222
    Você alterou: endereço  Rua A, 100 → Rua B, 200

    [ Manter as duas alterações ]   [ Ver as diferenças ]   [ Descartar as minhas ]
```

O que a segunda tem e a primeira não:

1. **Diz o que aconteceu** em linguagem de quem usa o sistema.
2. **Diz quem** — reduz a sensação de erro aleatório e permite resolver por fora ("vou falar
   com a Ana").
3. **Diz quando** — três minutos é diferente de três dias.
4. **Mostra a diferença**, não o estado inteiro.
5. **Oferece ações**, não um botão "OK" que descarta o trabalho.
6. **Não perde o que a pessoa digitou.** Nunca. Esta é a regra número um: mesmo recusando,
   o rascunho fica na tela.

Um detalhe operacional: para dizer "quem" e "quando", você precisa gravar `atualizado_por` e
`atualizado_em` na tabela. É uma decisão de esquema que precisa ser tomada **antes**, e que
quase sempre é esquecida até o dia em que a mensagem precisa ser escrita.

---

## 3. Resposta 3 — mesclar campo a campo

O algoritmo é o merge de três vias, o mesmo do `git`:

```
base   = o estado que EU li
meu    = o que eu quero gravar
deles  = o estado atual no banco

para cada campo:
    mudou_aqui = meu[c]   != base[c]
    mudou_la   = deles[c] != base[c]

    nem um nem outro  -> nada a fazer
    só eu             -> aplica o meu
    só eles           -> mantém o deles
    os dois, valor IGUAL     -> sem conflito (chegamos à mesma conclusão)
    os dois, valor DIFERENTE -> CONFLITO REAL: precisa de decisão
```

Implementação executável e verificada:
[`06-exemplos.md` § 7](06-exemplos.md#7--merge-campo-a-campo-em-vez-de-recusar).

**Quando mesclar automaticamente é seguro:**

- os campos são independentes (telefone e endereço);
- não existe invariante que os relacione.

**Quando não é:**

- `preco` e `moeda` — mesclar pode produzir 100 **dólares** onde alguém quis 100 reais;
- `data_inicio` e `data_fim` — o merge pode inverter a ordem;
- `status` e qualquer campo que dependa dele;
- qualquer par que apareça junto numa regra de validação.

**Marque os grupos de campos que devem se mover juntos.** Um esquema simples:

```javascript
const gruposAtomicos = [
  ['preco', 'moeda'],
  ['data_inicio', 'data_fim'],
  ['endereco', 'cidade', 'estado', 'cep'],
];
// se qualquer campo do grupo conflita, o grupo inteiro sobe para decisão humana
```

Isso é exatamente o que `@OptimisticLock(excluded = true)` do Hibernate faz na direção oposta:
declarar que um campo **não** participa da checagem. A ferramenta existe; falta usá-la com
critério de domínio.

---

## 4. Resposta 4 — mostrar as duas versões

Para texto e conteúdo, o merge automático é arriscado e a recusa é frustrante. A saída é
mostrar.

Padrões que funcionam, em ordem de esforço:

| Padrão | Exemplo | Esforço |
|---|---|---|
| Diff lado a lado | GitHub, Wikipédia | médio |
| Marcadores de conflito no próprio campo | `<<<<<<< meu ... ======= ... >>>>>>> deles` | baixo, mas assusta quem não é técnico |
| "Sua versão foi salva como rascunho" | Notion, Google Docs offline | médio |
| Merge assistido campo a campo | ferramentas de CRM | alto |

Duas regras não negociáveis:

1. **O trabalho da pessoa não pode sumir.** Se não der para mesclar, salve como rascunho, cópia
   ou revisão. "Suas alterações foram descartadas" é a pior frase possível numa interface.
2. **Mostre a diferença, não os dois textos inteiros.** Ninguém compara dois parágrafos de
   olho e acha a palavra que mudou.

---

## 5. Resposta 5 — evitar o conflito

Sempre a melhor, quando aplicável. Cinco técnicas, da mais simples à mais cara:

### 5.1 Reduzir a janela

Não abra o formulário de edição na tela de listagem. Não pré-carregue "para ficar rápido".
Leia o mais perto possível de gravar. Cortar a janela de 300 s para 5 s reduz o conflito em
quase 60 vezes ([`12`](12-anatomia-do-lost-update.md#4-quanto-custa-a-matemática-da-janela)).

### 5.2 Salvar por campo

Cada campo salvo ao sair do foco (*blur*), com sua própria requisição. Muitos conflitos
possíveis viram nenhum, porque duas pessoas raramente editam o **mesmo campo** ao mesmo tempo.
É o que fazem Notion, Linear e a maioria das ferramentas modernas.

Custo: mais requisições, e a necessidade de tratar salvamento parcial (a pessoa preencheu
metade e fechou a aba).

### 5.3 Presença

Mostrar "Ana está editando este registro" **antes** de a pessoa começar. Não impede nada, mas
muda o comportamento: quase todo mundo espera ou avisa.

Custo: canal em tempo real (WebSocket/SSE) e um registro de presença com expiração — na
prática, um **lease sem exclusividade**. É a técnica com melhor relação custo-benefício da
lista, na minha experiência.

### 5.4 Lease visível

Um passo além: quem entra primeiro tem exclusividade por um prazo, e isso aparece na
interface. É o modelo de "check-out" de sistemas de documentos.

Custo: precisa de política para o lease expirado, para "assumir mesmo assim" e para o usuário
que fechou o navegador. Ver [`18`](18-sistemas-distribuidos.md#3-leases-o-lock-que-não-trava-para-sempre).

### 5.5 Modelar como delta

Se o campo é um contador, uma lista ou um conjunto, modele a operação como **adicionar/remover**
e não como **substituir o valor inteiro**. Duas pessoas adicionando etiquetas diferentes ao
mesmo registro não têm por que conflitar — a menos que você tenha modelado a lista de
etiquetas como um campo de texto que é substituído por completo.

Muitos "conflitos" que vejo em revisão são artefato de modelagem, não do domínio.

---

## 6. Escolher por tipo de campo

Uma política concreta, para copiar e adaptar:

| Tipo de campo | Exemplo | Política |
|---|---|---|
| Contador / saldo | estoque, curtidas | delta atômico — sem conflito |
| Conjunto | etiquetas, participantes | adicionar/remover — merge automático |
| Escalar independente | telefone, cor | merge automático se só um lado mudou |
| Escalar com invariante | preço + moeda | grupo atômico; conflito sobe |
| Texto longo | descrição, artigo | mostrar diff; nunca mesclar sozinho |
| Máquina de estados | `status` do pedido | recusar e explicar a transição inválida |
| Referência | `responsavel_id` | recusar; atribuição dupla é decisão de gente |

---

## 7. Escrevendo a mensagem

Um modelo que funciona, com as quatro partes obrigatórias:

```
[O QUE ACONTECEU]     Suas alterações não foram salvas.
[POR QUE]             {nome} editou este {recurso} {tempo} atrás.
[O QUE MUDOU]         {lista curta de diferenças, campo a campo}
[O QUE FAZER]         {2 a 3 ações concretas, nunca só "OK"}
```

O que evitar:

- **Jargão:** "conflito de versão otimista", "stale object", "412", "concurrency token".
- **Culpar o usuário:** "você tentou salvar dados desatualizados".
- **Vaguidão:** "houve um erro, tente novamente" — tentar de novo com o mesmo formulário vai
  falhar de novo.
- **Botão único.** Um "OK" que descarta trabalho não é uma escolha; é uma perda com etapa
  extra.

Um detalhe de acessibilidade que costuma faltar: a mensagem precisa ser anunciada por leitor
de tela (`role="alert"` ou `aria-live="assertive"`) e o foco precisa ir para ela. Um aviso
visual que só aparece no topo da página passa despercebido para quem navega por teclado.

---

## 8. Um caminho de evolução realista

Quase ninguém constrói o sistema completo de uma vez. Uma ordem que funciona:

1. **Detectar.** Coluna de versão, guarda no `UPDATE`, checagem do retorno. Sem isso, tudo o
   mais é decoração.
2. **Medir.** Taxa de conflito por rota, distância de versão. Agora você sabe onde dói.
3. **Mensagem decente.** Quem, quando, o quê, e não perder o rascunho.
4. **Retentar o que é retentável.** Só o que é função do estado.
5. **Mesclar o que é independente.** Comece pelos campos que os dados mostram que mais
   conflitam.
6. **Reduzir a janela e mostrar presença.** Aqui o conflito começa a desaparecer da vida do
   usuário.
7. **CRDT ou edição colaborativa**, se e somente se o produto for de edição simultânea de
   verdade. É uma mudança de arquitetura, não um ajuste.

O erro comum é pular do 1 para o 7 porque "o Google Docs faz assim". A maioria dos sistemas
para no 5 e está ótima.

---

## Autoteste

1. Liste as cinco respostas possíveis a um conflito e um caso em que cada uma é a certa.
2. Quais são os seis elementos de uma boa mensagem de conflito?
3. Que decisão de esquema você precisa ter tomado **antes** para conseguir dizer "quem editou"?
4. Descreva o merge de três vias e a condição exata de conflito real.
5. Dê três pares de campos que não podem ser mesclados independentemente, e por quê.
6. Por que salvar por campo elimina a maioria dos conflitos?
7. Em que sentido "presença" é um lease sem exclusividade?
8. Qual é a regra inegociável sobre o trabalho já digitado pelo usuário?
