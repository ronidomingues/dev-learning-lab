# 18 · Revisar código gerado por máquina

**Nível:** intermediário → avançado · **Escrito em:** 20/08/2026

---

## Por que exige método diferente

Código humano e código de máquina **erram em lugares diferentes**. Revisar os
dois do mesmo jeito significa procurar no lugar errado.

| Código humano | Código de agente |
|---|---|
| Erra por cansaço, pressa, distração | Erra por não conhecer o contexto |
| Erros se agrupam onde foi difícil | Erros se distribuem uniformemente |
| Estilo inconsistente denuncia a parte apressada | Estilo **uniformemente bom** — não há pista visual |
| Nomes às vezes ruins | Nomes plausíveis, às vezes **enganosos** |
| Comentário reflete a intenção | Comentário descreve o código, não a intenção |
| Quem escreveu se lembra do porquê | **Ninguém se lembra do porquê** |

### A pista visual que sumiu

Revisor experiente lê código humano procurando **descontinuidade**: a função
bem escrita seguida do trecho apressado, o nome bom seguido do `tmp2`. A
inconsistência é o marcador de onde olhar.

Código de agente é **uniformemente polido**. Não há descontinuidade. O bug mora
num trecho que parece exatamente igual ao resto.

**Consequência:** você perdeu o seu radar. Precisa de um método deliberado no
lugar dele.

---

## 1 · O método em seis passos

Ordem importa: barato primeiro, e cada passo pode encerrar a revisão.

### Passo 0 — antes de ler qualquer linha

```bash
git diff --stat
```

Três perguntas:

1. **Quantos arquivos?** Mais do que você esperava = escopo explodiu.
2. **Quais arquivos?** Algum que você não esperava = alarme.
3. **Quantas linhas?** Mais de ~400 = devolva antes de ler.

**Devolver aqui custa 10 segundos.** Ler 800 linhas custa uma hora e você vai
ler mal.

### Passo 1 — o portão passou?

Se o [portão](17-verificacao-e-testes.md) reprovou, pare. Não revise código que
já se sabe reprovado; você vai gastar atenção em algo que voltará mudado.

### Passo 2 — os testes são reais?

**Antes do código de produção, leia os testes.** Sempre.

Checklist:

- [ ] Cada teste tem asserção sobre **valor**, não sobre existência?
- [ ] Existe teste para o caminho de **erro**?
- [ ] O teste falharia se eu quebrasse o código? (rode uma mutação à mão)
- [ ] Os *mocks* deixam algo real ser exercido?
- [ ] Nenhum teste foi **alterado** neste diff? (`git diff --stat -- tests/`)

Se os testes são decorativos, **o resto da revisão é teatro** — porque você não
tem rede nenhuma e vai ter que ler tudo com atenção máxima.

### Passo 3 — o diff faz o que foi pedido? Só isso?

Compare com a especificação. Procure especificamente por:

- funcionalidade que ninguém pediu ("já aproveitei e adicionei cache");
- refatoração não solicitada misturada à mudança;
- mudança de comportamento em código vizinho;
- arquivo de configuração alterado "para funcionar".

> **O item mais perigoso da lista é o segundo.** Refatoração misturada com
> mudança de comportamento é irrevisável: você não consegue distinguir o que
> mudou de propósito do que mudou por acidente. Devolva pedindo separação.

### Passo 4 — a leitura dirigida

Aqui está o método que substitui o radar perdido. Leia **procurando cada coisa
específica**, uma passada por categoria. É mais rápido e muito mais eficaz que
ler tudo procurando "problemas".

| Passada | O que procurar | Onde o agente mais erra |
|---|---|---|
| **1. Fronteiras** | limites, `<` vs `<=`, listas vazias, primeiro e último elemento | erro de limite é o defeito nº 1 |
| **2. Nulos e ausentes** | `None`, `undefined`, chave que pode não existir, campo opcional | caminho não feliz é subrepresentado no treino |
| **3. Erros** | `try` sem `except` específico, `catch` vazio, erro engolido, recurso não fechado | ele fecha o caminho feliz e esquece o `finally` |
| **4. Concorrência** | estado compartilhado, `async` sem `await`, transação sem `rollback`, ordem assumida | pouquíssimo exemplo correto no treino |
| **5. Segurança** | entrada não validada, SQL concatenado, segredo em log, permissão não checada | ele reproduz o padrão comum, e o comum é inseguro |
| **6. Duplicação** | isso já existe em outro lugar do sistema? | **o defeito estrutural nº 1 de 2026** |

### Passo 5 — as perguntas de contexto

Só você pode responder:

- Isso duplica algo que já temos? *(GitClear: duplicação de blocos subiu 81%
  desde 2023 — 40,3 → 73,0 por milhão de linhas alteradas)*
- Isso viola uma decisão registrada (ADR)?
- Isso vai atrapalhar a migração que está em andamento?
- Alguém vai conseguir depurar isso daqui a seis meses?

---

## 2 · O catálogo dos defeitos típicos

Reunidos por frequência observada. Use como lista de caça.

### Semântico

| Defeito | Como aparece |
|---|---|
| Nome que mente | `validarEmail` que também normaliza; `getUsuario` que cria se não existir |
| Comentário que descreve, não explica | `// incrementa i` em vez de `// pula o cabeçalho do CSV` |
| Abstração prematura | Interface com uma implementação, `Factory` para um caso |
| Duplicação plausível | Uma segunda função que faz quase o mesmo, 30 linhas adiante |

### Estrutural

| Defeito | Como aparece |
|---|---|
| Camada furada | Domínio importando driver de banco |
| Dependência nova desnecessária | `lodash` para um `map` |
| Configuração embutida | URL, timeout, limite fixos no código |
| Estado global novo | Singleton, variável de módulo mutável |

### Comportamental

| Defeito | Como aparece |
|---|---|
| Erro engolido | `except Exception: pass`, `catch { }` |
| Retorno de erro inventado | Devolve `[]` ou `0` em vez de propagar |
| Comparação de float com `==` | Quase sempre errado com dinheiro |
| Fuso horário implícito | `datetime.now()` sem `tz` |
| N+1 em consulta | Laço com consulta ao banco dentro |

### De verificação

| Defeito | Como aparece |
|---|---|
| Teste alterado para passar | O mais grave. Verifique sempre |
| `skip` / `xit` / `@unittest.skip` adicionados | Teste desligado em vez de consertado |
| `any`, `@ts-ignore`, `# type: ignore` | Camada de tipos desligada |
| Mock que engole o comportamento | Nada real é exercido |

---

## 3 · Usar IA para revisar IA — com limites

Funciona como **primeira passada**, com três condições:

1. **Contexto limpo**, não a mesma sessão que escreveu. Quem escreveu está
   condicionado a achar que está certo.
2. **Escopo restrito** de busca — senão você recebe 40 observações de estilo e
   para de ler na décima.
3. **Você confirma cada achado.** Você assina o comentário, não ele.

O prompt calibrado está no [exemplo 9](06-exemplos.md).

### Onde ela ajuda e onde não

| Ajuda | Não ajuda |
|---|---|
| Recurso não fechado | "isso duplica o módulo X" |
| Erro de limite | "essa abstração está errada" |
| `catch` vazio | "isso viola o ADR-014" |
| Entrada não validada | "isso não é o que o cliente pediu" |
| Teste com asserção vaga | "isso vai atrapalhar a migração" |

**O padrão:** ela pega o que é **local e padronizado**. Ela não pega o que é
**global e contextual**. E o dado de campo confirma: código de IA revela 1,7×
mais problemas que código humano (CodeRabbit, 2026) — o que significa que há
muito material local para uma ferramenta pegar, e é exatamente por isso que a
sua atenção deve ir para o global.

---

## 4 · Revisar em equipe: as políticas que funcionam

### Marque a origem

Etiqueta no PR (`gerado-por-agente`) ou linha no commit. Não é para culpar; é
para o revisor **saber onde procurar** e para você medir depois.

### Limite o tamanho do PR, com número

PRs assistidos por IA são 2,6× maiores no percentil 75 (408 vs. 157 linhas) e
esperam 5,3× mais por revisão (LinearB, 2026). Um limite duro (400 linhas)
verificado automaticamente é a intervenção mais eficaz que conheço para isso.

### Revisão proporcional ao risco

| Risco | Política |
|---|---|
| Dinheiro, autenticação, permissão, dado pessoal | 100% humano, dois revisores |
| Regra de negócio | 100% humano, um revisor |
| Infraestrutura, CI | 100% humano |
| Teste, documentação, tradução, lint | Amostragem + portão |
| Migração mecânica repetitiva | Amostragem estratificada ([exemplo 12](06-exemplos.md)) |

### Meça a capacidade de revisão, não só a de produção

Se a equipe produz mais e revisa igual, o estoque cresce. Métricas úteis:

- tempo até o primeiro comentário (*time to first review*);
- fila de PRs abertos há mais de 48 h;
- fração do código gerado que passa sem modificação (32,7% para IA vs. 84,4%
  para humano é a linha de base de 2026).

> **Teoria das restrições, aplicada:** otimizar uma etapa que não é o gargalo
> não aumenta a vazão do sistema — aumenta o estoque antes do gargalo. Se a
> revisão é o gargalo e você acelera a escrita, você produziu fila.

---

## 5 · O sinal de alerta pessoal

Você está revisando mal se:

- passa mais de 30 minutos num único PR sem pausa;
- se pega pensando "parece certo" em vez de "verifiquei que está certo";
- aprova porque "os testes passam" sem ter olhado os testes;
- não consegue explicar o que a mudança faz sem reler;
- está no quarto PR seguido do dia.

**Contramedida honesta:** revisão é atividade de atenção intensa e tem
rendimento decrescente rápido. Três PRs bem revisados valem mais que dez
aprovados. Se a fila não cabe, o problema é de vazão do time — dizer isso é
mais útil que aprovar mal.

---

## Autoteste

1. Cite quatro diferenças entre onde erra código humano e código de agente.
2. Que pista visual o revisor perde com código de agente, e o que a substitui?
3. O que você faz antes de ler qualquer linha, e quais são as três perguntas?
4. Por que ler os testes antes do código de produção?
5. Por que refatoração misturada com mudança de comportamento é irrevisável?
6. Cite as seis passadas da leitura dirigida e o que cada uma procura.
7. Dê três exemplos de "nome que mente".
8. Quais são as três condições para usar IA revisando IA?
9. O que a IA revisora pega e o que ela não pega? Enuncie o padrão.
10. Explique, com teoria das restrições, por que acelerar a escrita sem acelerar
    a revisão não aumenta a entrega.
11. Cite três sinais de que você está revisando mal.

---

**Anterior:** [17-verificacao-e-testes](17-verificacao-e-testes.md) ·
**Próximo:** [19-arquitetura-para-maquina](19-arquitetura-para-maquina.md)
