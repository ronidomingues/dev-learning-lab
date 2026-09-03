# 12 · Tipos de teste e as formas da carteira

`Nível: intermediário` · `Última atualização: 12/08/2026`

---

## 1. O problema da taxonomia

Não existe classificação canônica de tipos de teste. O que existe são **quatro eixos
independentes** que as pessoas misturam ao conversar, e daí vem metade das discussões
improdutivas do campo.

| Eixo | Pergunta | Valores |
|---|---|---|
| **Escopo** | quanto do sistema entra? | unitário · integração · sistema · ponta a ponta |
| **Objetivo** | o que se quer saber? | funcional · desempenho · segurança · usabilidade · acessibilidade |
| **Visibilidade** | você vê o código? | caixa-preta · caixa-branca · caixa-cinza |
| **Execução** | quem executa? | manual · automatizado |

"Teste de carga" é um objetivo, não um escopo. "Teste de aceitação" é um objetivo (validar
com o cliente), que pode ser feito em qualquer escopo. Quando alguém disser "isso não é
teste unitário, é de integração", pergunte de qual eixo está falando.

Este curso trata sobretudo de **funcional + automatizado**, atravessando todos os escopos.

---

## 2. Os escopos, com fronteiras honestas

### 2.1 Unitário

**Definição operacional** (a mesma de [10-fundamentos.md](10-fundamentos.md)): verifica um
comportamento, roda em milissegundos, não toca I/O, e pode rodar em qualquer ordem.

```python
def test_desconto_favorece_o_cliente_no_meio_centavo():
    assert Dinheiro(1999).aplicar_desconto(10).centavos == 1799
```

| | |
|---|---|
| ✅ **compra** | diagnóstico preciso (o teste aponta a função), velocidade, muitos casos por segundo |
| ❌ **não compra** | nenhuma garantia de que as peças se encaixam |
| 💰 **custo** | baixo para escrever, **médio para manter** — sofre com refatoração se mal escrito |

### 2.2 Integração

Verifica que **duas ou mais peças conversam**. E aqui há uma ambiguidade real que vale
nomear, porque duas comunidades usam a palavra para coisas diferentes:

| Sentido | O que integra | Exemplo |
|---|---|---|
| **integração estreita** | seu código com **uma** dependência externa real | seu repositório + SQLite de verdade |
| **integração larga** | vários módulos seus, sem dependência externa | serviço + repositório + domínio, tudo em memória |

No mundo Java/enterprise, "integração" costuma ser o primeiro sentido. No mundo
front-end/Testing Library, costuma ser o segundo. Diga qual você quer dizer.

```javascript
it('a data faz ida e volta sem perder o dia', () => {
  const repo = new RepositorioSQLite(':memory:');   // ← banco de verdade
  repo.salvar(assinatura);
  assert.equal(repo.buscar('a1').proximaCobranca, '2026-02-28');
});
```

| | |
|---|---|
| ✅ **compra** | pega erro de SQL, de serialização, de contrato, de configuração |
| ❌ **não compra** | não cobre o fluxo do usuário |
| 💰 **custo** | precisa de infraestrutura (container, banco), mais lento (10–500 ms) |

### 2.3 Sistema / ponta a ponta (E2E)

Exercita o sistema inteiro como um usuário faria: navegador → servidor → banco → e-mail.

```javascript
test('cliente compra e recebe confirmação', async ({ page }) => {
  await page.goto('/produtos/cafe');
  await page.getByRole('button', { name: 'Comprar' }).click();
  await page.getByLabel('Cartão').fill('4111111111111111');
  await page.getByRole('button', { name: 'Finalizar' }).click();
  await expect(page.getByText('Pedido confirmado')).toBeVisible();
});
```

| | |
|---|---|
| ✅ **compra** | a única evidência de que o sistema **funciona de verdade** |
| ❌ **não compra** | diagnóstico: falhou "em algum lugar" entre cinco sistemas |
| 💰 **custo** | **alto**, e crescendo: lento (segundos a minutos), frágil, caro de manter |

### 2.4 A fronteira é borrada, e tudo bem

Onde termina o unitário e começa a integração? Não há linha objetiva. O que existe é um
**contínuo de custo e de escopo**, e a taxonomia serve para conversar, não para julgar.

Um critério prático que funciona melhor que a taxonomia: **classifique pelo custo, não pelo
nome.** Duas gavetas bastam:

- **rápidos e isolados** → rodam a cada salvamento;
- **lentos ou com dependência** → rodam antes do commit e no CI.

É o que o projeto-modelo faz, com o marcador `integracao` (pytest) e a convenção
`*.integracao.test.js` (Node).

---

## 3. Outros escopos que aparecem no caminho

| Nome | O que verifica | Quando vale |
|---|---|---|
| **teste de contrato** | duas implementações do mesmo contrato se comportam igual | sempre que houver um fake ([exemplo 10](06-exemplos.md)) |
| **teste de contrato de consumidor** (Pact) | o produtor da API não quebrou o consumidor | microsserviços de times diferentes |
| **teste de componente** | um módulo com suas dependências internas, sem as externas | front-end (renderizar um componente) |
| **teste de fumaça** (*smoke*) | "sobe e responde?" | após o deploy, em 30 segundos |
| **teste de caracterização** | registra o comportamento atual, certo ou errado | código legado ([exemplo 11](06-exemplos.md)) |
| **teste de regressão** | um bug específico não volta | após todo bug corrigido |
| **teste de aprovação/snapshot** | a saída não mudou | saída grande e estável |
| **teste de mutação** | mede a qualidade da **suíte**, não do código | [19](19-cobertura-e-metricas.md) |

---

## 4. A pirâmide de Cohn

```
                    /\
                   /  \       ponta a ponta
                  /    \      poucos · lentos · frágeis · caros
                 /------\
                /        \    integração / serviço
               /          \   alguns · médios
              /------------\
             /              \  unitários
            /                \ muitos · rápidos · baratos
           /------------------\
```

**A regra por trás:** quanto mais alto, mais caro por teste e mais frágil. Logo, empurre a
verificação para o nível mais baixo em que ela ainda faça sentido.

**A justificativa aritmética** (desenvolvida em [10-fundamentos.md](10-fundamentos.md) §7):
a confiabilidade de um teste E2E é o **produto** das confiabilidades das partes. Cinco
componentes a 99,5 % dão 97,5 % — falha 1 em 40 sem bug nenhum.

**O antipadrão que ela combate:** o **sorvete de casquinha** (*ice-cream cone*) — a pirâmide
invertida, com montanhas de teste manual e de interface e quase nada embaixo.

```
       \--------------------/
        \   teste manual   /
         \----------------/
          \  E2E / UI    /
           \------------/
            \integração/
             \--------/
              \unit. /
               \----/
```

Sintomas de que seu time está aqui: a suíte leva mais de 30 minutos; existe uma planilha de
casos de teste manuais; "roda de novo" é a resposta padrão a um vermelho.

---

## 5. As críticas legítimas à pirâmide

Levar a pirâmide como dogma produz seus próprios problemas. As objeções que se sustentam:

**1. Os preços mudaram.** A pirâmide é de 2009, quando E2E era Selenium com Internet
Explorer. Em 2026, Playwright *headless* com paralelismo roda 200 testes de navegador em
poucos minutos, com repetição automática e rastro de execução. O topo continua sendo o mais
caro — mas por um fator menor do que era.

**2. "Unitário" incentiva testar estrutura.** Ler "muitos testes unitários" como "um teste
por classe" produz suítes que quebram a cada refatoração — exatamente o pilar mais valioso
sendo destruído. A pirâmide não diz isso, mas é como muita gente a lê.

**3. Ela não fala de risco.** Uma função de cálculo de imposto e um formatador de data não
merecem o mesmo esforço. A pirâmide é sobre proporções; o critério que deveria governar é
**consequência da falha × probabilidade da falha**.

**4. Ela não se aplica igual a todo tipo de sistema.** Uma biblioteca pura é quase toda
unitária. Um *pipeline* de dados é quase todo integração. Um *proxy* é quase todo E2E,
porque ele **não tem** lógica própria — ele é a integração.

---

## 6. As formas alternativas

### 6.1 Testing Trophy (Kent C. Dodds, 2018)

```
        ┌───────────┐
        │    E2E    │
      ┌─┴───────────┴─┐
      │               │
      │  integração   │   ← o maior peso
      │               │
      └─┬───────────┬─┘
        │ unitários │
        └─┬───────┬─┘
     ┌────┴───────┴────┐
     │ análise estática │   ← tipos, lint: "testes" grátis
     └──────────────────┘
```

Duas ideias, ambas boas:

- **A base é a análise estática.** TypeScript, `mypy`, ESLint e Ruff pegam classes inteiras
  de erro sem que você escreva teste nenhum. Não considerá-los é ignorar a camada mais
  barata que existe.
- **O peso vai para a integração**, com a frase que resume a proposta: *"escreva testes. não
  muitos. principalmente de integração."*

**Contexto e limite:** o troféu nasceu no mundo React, onde "unitário de um componente"
frequentemente significa testar detalhe de implementação, e "integração" significa renderizar
uma árvore de componentes em memória — o que é **rápido**. Transportar o troféu para um
back-end onde "integração" significa subir Postgres e Kafka não funciona: você perde o laço
rápido.

### 6.2 Losango / favo de mel (Spotify)

Para arquiteturas de microsserviços, propõe-se um **losango**: pouco unitário, muito teste
de integração/contrato, pouco E2E. O raciocínio: num serviço pequeno, a lógica própria é
pouca e o risco está nas fronteiras.

### 6.3 A forma que este curso recomenda

**Nenhuma forma fixa.** Um método, em três passos:

1. **Liste o que dói se quebrar.** Cobrança errada, perda de dado, vazamento, indisponibilidade.
2. **Para cada risco, pergunte: qual é o teste mais barato que o detecta?** Muitas vezes é
   unitário; às vezes só o E2E detecta; às vezes um tipo estático já resolve.
3. **Mantenha o laço rápido separado.** Qualquer que seja a proporção, tem de existir um
   subconjunto que roda em segundos.

A forma resultante emerge do sistema. Num projeto de biblioteca ela vai parecer uma
pirâmide; num *gateway* vai parecer um losango; num front-end, um troféu. Todos estão certos
para o seu contexto.

---

## 7. Comparação lado a lado

| | Unitário | Integração | E2E |
|---|---|---|---|
| **Tempo típico** | 0,1–5 ms | 10–500 ms | 1 s – 5 min |
| **Quantos** | centenas a milhares | dezenas a centenas | unidades a dezenas |
| **Roda quando** | a cada salvamento | antes do commit | no CI, antes do deploy |
| **Precisa de** | nada | banco, container, servidor local | ambiente completo |
| **Diagnóstico** | preciso (a função) | médio (a fronteira) | ruim ("quebrou em algum lugar") |
| **Fragilidade** | baixa, se bem escrito | média | alta |
| **Custo de manutenção** | baixo | médio | **alto e crescente** |
| **Pega erro de** | lógica, cálculo, fronteira | SQL, serialização, contrato, config | fluxo, integração real, JS de navegador |
| **Não pega** | montagem errada | fluxo do usuário | causa raiz |
| **Determinismo** | total | alto | **problemático** |

---

## 8. Os cinco porquês: por que E2E é tão caro de manter?

**1. Por quê?** Porque ele quebra por motivos que não são bugs.

**2. Por que quebra sem bug?** Porque depende de tempo (a página carregou?), de dados (o
usuário de teste ainda existe?), de rede, e de seletores de interface que mudam a cada
ajuste de layout.

**3. Por que o tempo é um problema tão grande?** Porque a interface é **assíncrona sem
contrato**: não existe um sinal padronizado de "terminei de renderizar". O teste precisa
**adivinhar** quando checar. Daí vêm o `sleep(2)` e os *waits* explícitos.

**4. Por que não existe esse sinal?** Porque a web foi projetada para documentos que carregam
progressivamente, não para aplicações com estado observável de fora. Não há API padrão que
diga "estou ocioso e estável". *(O `document.readyState` responde sobre o carregamento do
documento, não sobre a sua aplicação.)*

**5. Por que ninguém padronizou isso?** Porque exigiria que toda biblioteca de interface
declarasse seu estado de forma uniforme, e não há autoridade que imponha isso ao ecossistema
JavaScript. **Parada legítima: é uma limitação arquitetural da plataforma web**, não um
descuido de quem faz as ferramentas.

**O que a indústria fez em vez disso:** ferramentas modernas (Playwright, Cypress) embutem
**auto-espera** — elas tentam a ação repetidamente até o elemento ficar acionável, com
tempo-limite. É uma heurística boa, não uma solução. Por isso E2E continua sendo o teste
mais caro, mesmo em 2026.

---

## 9. Quantos testes de cada tipo?

Não existe número certo, mas existem **sinais de que a proporção está errada**:

| Sintoma | Provável desequilíbrio | O que fazer |
|---|---|---|
| a suíte leva > 10 min | E2E demais, ou integração sem isolamento | mover verificações para baixo |
| bugs de lógica chegam em produção | poucos unitários, ou unitários triviais | testar regra, não getter |
| o sistema quebra na montagem, com tudo verde | falta integração | um teste de fiação por caminho crítico |
| todo *refactor* quebra 40 testes | unitários acoplados à estrutura | testar comportamento observável |
| a suíte é vermelha "às vezes" | E2E frágil, ou estado compartilhado | isolar, ou apagar o teste |
| ninguém confia na suíte | *flaky* normalizado | **pare tudo e conserte isso primeiro** |

A última linha é a mais importante do arquivo. Uma suíte em que o vermelho não significa
nada é pior que suíte nenhuma, porque custa manutenção e dá falsa sensação de segurança.

---

## 10. Onde o projeto-modelo se encaixa

| Camada | Python | JavaScript | Tempo |
|---|---|---|---|
| unitário puro | 175 | 220 | 1,98 s / 0,29 s |
| integração (SQLite, HTTP local) | 15 | 23 | ~1,5 s |
| ponta a ponta (processo) | — | 2 | ~0,1 s |

Proporção ≈ **90 / 9 / 1**. Não foi planejado assim; **emergiu** do design: como a regra de
negócio está em módulos puros e as dependências entram por injeção, quase tudo é testável
sem I/O. Essa é a tese de [20-testabilidade-e-design.md](20-testabilidade-e-design.md): a
forma da pirâmide é consequência da arquitetura, não uma meta a perseguir.

---

## Autoteste

1. Cite os quatro eixos de classificação e diga em qual "teste de carga" se encaixa.
2. Quais são os dois sentidos de "teste de integração", e por que a ambiguidade importa?
3. Dê o critério prático de duas gavetas que substitui a taxonomia no dia a dia.
4. Qual antipadrão a pirâmide combate, e quais são os três sintomas dele?
5. Enuncie as quatro críticas legítimas à pirâmide.
6. Qual é a camada da base do Testing Trophy, e por que ela é "grátis"?
7. Por que o troféu não transporta bem para um back-end com Postgres e Kafka?
8. Descreva o método de três passos que este curso recomenda no lugar de uma forma fixa.
9. Por que não existe um sinal padronizado de "a página está pronta"? Vá até a parada legítima.
10. Seu time tem tudo verde e o sistema quebra na montagem. Qual é o desequilíbrio?
11. Por que a proporção do projeto-modelo "emergiu" em vez de ter sido planejada?
