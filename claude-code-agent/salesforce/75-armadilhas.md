# 75 · Armadilhas, mitos e más práticas

`Nível: todos` · `Atualizado: 11/08/2026`

Catálogo do que dá errado, por que dá errado, e por que essas práticas persistem apesar de
todo mundo saber que são ruins. A última parte é a mais importante: uma má prática que
sobrevive por 15 anos está resolvendo algum problema real para alguém.

---

## 1. Armadilhas de modelagem

### 1.1 A Account guarda-chuva

**O que é.** Uma conta chamada "Clientes", "Pessoa Física" ou "Consumidores" com 300 mil
contatos pendurados.

**Por que dá errado.** *Account data skew* ([12-modelo-de-dados.md](12-modelo-de-dados.md) §7.1):
contenção de bloqueio, `UNABLE_TO_LOCK_ROW`, e recálculo de sharing que trava a org se
alguém mudar o dono da conta.

**Por que persiste.** Porque Person Accounts exige um chamado ao Suporte, é irreversível, e
a alternativa parece funcionar nos primeiros seis meses. O problema aparece quando não há
mais como voltar.

**Correção.** Person Accounts (decida **antes** de carregar dados) ou distribuir os contatos.

### 1.2 Campo que vira lixo

**O que é.** `Campo1__c`, `Novo_Status__c`, `Data_2__c`, `Observacao_TEMP__c` — a org com
400 campos, 250 sem uso.

**Por que dá errado.** Cada campo consome cota, aparece em toda tela de configuração,
polui relatórios, e ninguém sabe se pode apagar porque ninguém sabe quem usa.

**Por que persiste.** Porque criar um campo custa 90 segundos e **apagar custa uma
investigação**. O incentivo é assimétrico e favorece a acumulação.

**Correção.** Preencher o campo `description` de todo campo, sempre; revisão semestral
usando *Field Usage* e o *Optimizer*; e uma regra de time: campo novo só com dono e motivo
registrados.

### 1.3 Multi-select picklist

**O que é.** Um campo com múltipla seleção onde deveria haver um objeto filho.

**Por que dá errado.** É uma string com `;` separando valores. Filtrar é `INCLUDES()`,
agrupar em relatório é sofrível, integrar exige parsing, e não há como adicionar atributos
a cada valor selecionado.

**Por que persiste.** Porque na hora do requisito ("o cliente pode ter vários interesses")
parece a solução óbvia e leva um minuto. O objeto filho leva uma hora e exige uma tela.

**Correção.** Objeto filho, quase sempre. Multi-select só quando os valores são poucos,
estáveis, sem atributos próprios e nunca usados em relatório agrupado.

### 1.4 Recriar objeto padrão

**O que é.** Criar `Cliente__c` porque `Account` "não serve".

**Por que dá errado.** Você perde: relatórios prontos, integrações nativas, funcionalidades
de mobile, IA, Data 360, e a compreensão imediata de qualquer profissional que entre no
projeto. E ganha: um objeto que precisa reimplementar tudo isso.

**Por que persiste.** Porque o objeto padrão tem campos e comportamentos que atrapalham,
e recriar parece mais limpo no dia 1.

**Correção.** Use o padrão. Esconda o que atrapalha com layouts, record types e permissões.

---

## 2. Armadilhas de código

### 2.1 SOQL ou DML dentro de laço

O erro nº 1, sem concorrência. Ver [15-apex.md](15-apex.md) §5.

**Por que persiste.** Porque **funciona no teste manual**. O desenvolvedor cria um registro
pela interface, tudo passa, e o código vai para produção. O erro só aparece no primeiro
import ou na primeira atualização em massa — semanas depois, com o autor em outro projeto.

**Correção estrutural, não individual:** um teste com 200 registros em toda classe de
trigger. É o único mecanismo que pega isso de forma confiável.

### 2.2 Múltiplos triggers no mesmo objeto

**Por que dá errado.** A ordem entre eles é **indefinida pela plataforma**.

**Por que persiste.** Porque criar um trigger novo é mais rápido que entender o handler
existente. É dívida técnica com juros baixos no começo e altos depois.

**Correção.** Um trigger, um handler, com um mecanismo de registro de "handlers de domínio"
se o objeto for muito disputado.

### 2.3 `without sharing` "para funcionar"

**O que é.** O código não enxergava um registro, alguém trocou para `without sharing`, e
funcionou.

**Por que dá errado.** O código passa a enxergar **tudo**, para **todo mundo**. Se ele
alimenta um LWC ou uma API, você acabou de criar um endpoint que vaza a org inteira.

**Por que persiste.** Porque resolve o sintoma em 5 segundos e o problema real (configurar
sharing corretamente) leva horas e envolve outras pessoas.

**Correção.** `with sharing` sempre. Se precisar furar, isole num método pequeno,
`without sharing`, com comentário explicando, e que faça **só** aquela operação.

### 2.4 Cobertura sem asserção

**O que é.** Testes que criam dados, chamam métodos e não verificam nada.

**Por que dá errado.** Você tem 90% de cobertura e zero garantia. O deploy passa; o bug
também.

**Por que persiste.** Porque a plataforma **exige cobertura, não qualidade**, e o incentivo
segue exatamente a métrica. É um caso de manual de Goodhart: quando uma medida vira meta,
ela deixa de ser boa medida.

**Correção.** Regra de time: todo método de teste tem ao menos um `Assert` significativo.
Revisão de código que rejeita teste sem asserção. Nenhuma ferramenta resolve isso — é
cultura.

### 2.5 Try/catch engolindo exceção

```apex
try {
    // ...
} catch (Exception e) {
    // silêncio
}
```

**Por que persiste.** Porque faz o erro sumir da tela do usuário. E some mesmo — junto com
a informação de que algo deu errado.

**Correção.** Ou trate de verdade (com ação de recuperação), ou registre em log estruturado
e relance. Nunca capture sem fazer nada.

### 2.6 `Schema.getGlobalDescribe()` em código quente

**Por que dá errado.** É uma das operações mais caras do Apex, e devolve o describe de
**todos** os objetos da org.

**Por que persiste.** Porque é o primeiro resultado que aparece quando se busca "como
descobrir o tipo de um Id em Apex".

**Correção.** `Id.getSObjectType()`, `Type.forName()`, ou
`Schema.describeSObjects(new List<String>{'Account'})`.

---

## 3. Armadilhas de automação

### 3.1 Automação duplicada em Flow e Apex

**Por que dá errado.** Ordem de execução imprevisível entre as camadas; a mesma regra
aplicada duas vezes; e o pesadelo de depurar um comportamento que muda conforme o contexto
(UI, API, Bulk).

**Por que persiste.** Porque times de admin e de dev trabalham separados e não conversam.
É um problema organizacional que se manifesta como bug técnico.

**Correção.** Uma convenção escrita: por objeto e por regra, uma camada só. E revisão
conjunta de qualquer automação nova.

### 3.2 After-Save alterando o próprio registro

**Por que dá errado.** Gera um segundo ciclo completo de gravação — triggers, validações,
rollups de novo. Dobra o custo e pode causar recursão.

**Por que persiste.** Porque a diferença entre Before e After não é óbvia na interface do
Flow Builder, e o resultado funcional é o mesmo.

**Correção.** Before-Save para alterar o próprio registro. Sempre.

### 3.3 Flows sem *Trigger Order*

**Por que dá errado.** Com dois ou mais Flows record-triggered no mesmo objeto e evento, a
ordem é indefinida. Bugs intermitentes que "às vezes acontecem".

**Correção.** Definir a prioridade em cada Flow. É um campo, leva 10 segundos.

---

## 4. Armadilhas de integração

### 4.1 Sem idempotência

**Por que dá errado.** Um timeout onde a requisição chegou mas a resposta se perdeu produz
duplicata na retentativa. Não é hipótese — é o comportamento esperado de redes.

**Por que persiste.** Porque em ambiente de teste a rede é perfeita e nunca duplica.

**Correção.** External Id `unique` + `upsert`, e header `Idempotency-Key` do lado externo.
Garantia no **banco**, não no código. Ver [06-exemplos.md](06-exemplos.md) §13.

### 4.2 Credencial em Custom Setting

**Por que dá errado.** O segredo entra no metadado, no Git, no backup, no change set e no
retrieve de qualquer desenvolvedor.

**Por que persiste.** Porque Named Credential tem uma curva de configuração maior e a
documentação mudou de forma nos últimos anos (External Credential + Principal), o que
confunde quem aprendeu no modelo antigo.

**Correção.** Named Credential + External Credential. Não há exceção legítima em 2026.

### 4.3 REST comum para carga em massa

**Por que dá errado.** 15.000 chamadas de API por dia numa DE, ou 100.000 numa EE, se
esgotam em minutos com carga registro a registro. Quando o limite estoura, **toda**
integração da empresa para.

**Correção.** Bulk API 2.0.

### 4.4 Não baixar os `failedResults`

**Por que dá errado.** O job termina com status "JobComplete" mesmo com registros falhados.
Você acha que carregou 100 mil e carregou 97 mil.

**Correção.** Baixar e tratar `failedResults` sempre, e alertar se houver qualquer linha.

---

## 5. Mitos

| Mito | Realidade |
|---|---|
| "Salesforce é só arrastar e soltar" | Orgs reais têm dezenas de milhares de linhas de Apex |
| "Não precisa de desenvolvedor" | Precisa, a partir de um nível modesto de complexidade |
| "É caro só a licença" | Licença costuma ser a menor parte; ver [80-custos-e-licencas.md](80-custos-e-licencas.md) |
| "Migrar depois é fácil" | É o projeto mais caro que a empresa vai fazer |
| "Governor limits são frescura" | São o que impede o vizinho de derrubar você; ver [19](19-multitenancy-arquitetura.md) |
| "75% de cobertura significa código testado" | Significa 75% das linhas executadas. Nada mais |
| "Flow é sempre melhor que Apex" | Flow custa mais CPU e é pior de manter acima de ~20 elementos |
| "Apex é uma linguagem ruim" | É uma linguagem *limitada* por motivos arquiteturais defensáveis |
| "Certificação garante emprego" | Ajuda muito a passar no filtro; portfólio decide a entrevista |
| "O Salesforce faz backup dos meus dados" | Restauração ponto a ponto não é garantida no plano padrão; é serviço pago |
| "Change Set é suficiente" | É manual, sem versionamento e sem rollback |
| "Posso testar em produção porque tem sandbox" | Sandbox não tem os dados nem o volume de produção |
| "IA vai substituir o admin" | Muda o trabalho; ainda alguém precisa decidir o que é certo |

---

## 6. Armadilhas de projeto e de gestão

### 6.1 Implantar tudo de uma vez ("big bang")

**Por que dá errado.** Escopo grande, prazo longo, requisito envelhecido, adoção baixa e
nenhum aprendizado antes do final.

**Por que persiste.** Porque a compra é feita em bloco, com orçamento anual, e a consultoria
é remunerada por projeto — o incentivo de todos empurra para escopo grande.

**Correção.** Fatie por processo de negócio. Entregue algo em produção em 8 a 12 semanas.

### 6.2 Customizar antes de entender o padrão

**Por que dá errado.** Você reimplementa mal o que já existia, e depois não consegue usar
funcionalidades novas que assumem o padrão.

**Correção.** Rode três meses com o padrão. A lista de customizações que sobra é
tipicamente um terço da original.

### 6.3 Não ter um dono do produto

**Por que dá errado.** Cada área pede o seu campo, cada consultoria faz do seu jeito, e em
três anos a org é um museu de decisões locais.

**Correção.** Uma pessoa com autoridade para dizer não. É a função mais subestimada de um
programa Salesforce.

### 6.4 Consultoria sem transferência de conhecimento

**Por que dá errado.** A consultoria vai embora e ninguém entende a org. Todo ajuste vira
um novo contrato.

**Por que persiste.** Porque o modelo de receita da consultoria não recompensa a
transferência. Isso não é má-fé — é o incentivo funcionando como desenhado.

**Correção.** Coloque no contrato: documentação, pareamento e pelo menos uma pessoa interna
em tempo integral no projeto desde o dia 1. Sem isso, você está alugando a sua própria org.

---

## 7. As dez frases que precedem um incidente

1. "Vou só mexer direto em produção, é rapidinho."
2. "Não precisa de teste, é uma mudança pequena."
3. "Coloca `without sharing` que resolve."
4. "Depois eu arrumo, agora precisa entregar."
5. "Ninguém usa esse campo, pode apagar."
6. "No meu usuário funciona."
7. "Desativa a validation rule só para essa carga." *(e ninguém religa)*
8. "A consultoria cuida disso."
9. "Vamos deixar o backup para a fase 2."
10. "É só um campo a mais."

---

## 8. Checklist de revisão de código

Use em toda revisão de Apex. Se algum item falhar, não aprove.

- [ ] Nenhuma SOQL, DML, callout ou `sendEmail` dentro de laço.
- [ ] Um trigger por objeto, sem lógica dentro.
- [ ] `with sharing` (ou `inherited sharing`), com justificativa se `without`.
- [ ] `WITH USER_MODE` / `AccessLevel.USER_MODE` — ou exceção comentada.
- [ ] Nenhum `WITH SECURITY_ENFORCED` (não compila em v67+).
- [ ] SOQL dinâmica com bind, nunca com concatenação.
- [ ] Testes com asserções significativas, não só cobertura.
- [ ] Teste com 200 registros em toda classe de trigger.
- [ ] Teste com `System.runAs` para código sensível a permissão.
- [ ] Exceções tratadas ou relançadas, nunca engolidas.
- [ ] `AuraHandledException` em métodos expostos ao LWC.
- [ ] Nenhum Id guardado em `String`.
- [ ] `Decimal` para dinheiro, nunca `Double`.
- [ ] Nenhuma credencial, URL de ambiente ou segredo hardcoded.
- [ ] `Database.insert(lista, false)` onde falha parcial é aceitável.
- [ ] Interruptor de bypass em handlers, para migração.
- [ ] Nomes de API descritivos e definitivos.

---

## Autoteste

1. Por que a Account guarda-chuva parece funcionar por seis meses e depois quebra?
2. Por que "SOQL dentro de laço" persiste, apesar de todo mundo saber que é errado?
3. Qual é o problema estrutural — não individual — que produz testes sem asserção?
4. Por que `without sharing` é uma correção perigosa, e qual é a alternativa disciplinada?
5. Por que a duplicação de automação entre Flow e Apex é um problema organizacional?
6. Sem idempotência, por que a duplicata é inevitável e não apenas provável?
7. Por que consultoria sem transferência de conhecimento persiste? Como se contrata contra isso?
8. Escolha três itens do checklist de revisão e explique o incidente que cada um previne.
