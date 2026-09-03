# 70 · Prática — dez laboratórios

`Nível: todos` · `Atualizado: 11/08/2026`

Cada laboratório tem: **objetivo**, **pré-requisito**, **passos**, **critério de aprovação**
(objetivo e verificável) e **por que isso importa**. Faça na ordem. Não pule o critério de
aprovação — é ele que distingue "eu li" de "eu sei".

Ambiente: uma org Developer Edition ([03-instalacao.md](03-instalacao.md) §2).

| # | Laboratório | Trilha | Tempo |
|---|---|---|---|
| 1 | Modelagem de dados sem código | admin | 1 h |
| 2 | Segurança em camadas | admin | 1,5 h |
| 3 | Automação com Flow | admin | 2 h |
| 4 | Relatórios e painéis | admin | 1 h |
| 5 | Primeiro trigger bulk-safe | dev | 2 h |
| 6 | Testes que realmente testam | dev | 2 h |
| 7 | LWC com Apex e refresh | dev | 2,5 h |
| 8 | Batch sobre volume | dev | 2 h |
| 9 | Integração idempotente | dev | 3 h |
| 10 | Investigação de performance | avançado | 2 h |

---

## Lab 1 — Modelagem de dados sem código

**Objetivo.** Modelar um domínio completo pela interface e entender as consequências de
cada escolha.

**Cenário.** Uma escola de idiomas: **Curso**, **Turma**, **Aluno**, **Matrícula**.

**Passos.**

1. Crie o objeto **Curso__c** (`Setup → Object Manager → Create → Custom Object`):
   - Record Name: Text, "Nome do Curso".
   - Campos: `Nivel__c` (picklist restrita: Básico/Intermediário/Avançado),
     `Carga_Horaria__c` (Number 4,0), `Ativo__c` (Checkbox, default true).
2. Crie **Turma__c** com:
   - Record Name: AutoNumber `TUR-{0000}`.
   - `Curso__c`: **Master-Detail** para Curso__c.
   - `Inicio__c` (Date), `Vagas__c` (Number 3,0), `Professor__c` (Lookup para User).
3. Crie **Aluno__c** com Record Name Text e `Email__c` (Email, **unique**, **External Id**).
4. Crie **Matricula__c** — o objeto de junção:
   - Record Name AutoNumber `MAT-{00000}`.
   - **Dois master-details**: primeiro `Turma__c`, depois `Aluno__c`.
   - `Situacao__c` (picklist restrita: Ativa/Trancada/Concluída/Cancelada).
   - `Nota_Final__c` (Number 4,2).
5. Em **Turma__c**, crie o rollup `Matriculas_Ativas__c` = COUNT de Matricula__c
   com filtro `Situacao__c = Ativa`.
6. Em **Turma__c**, crie a fórmula `Vagas_Restantes__c` = `Vagas__c - Matriculas_Ativas__c`.
7. Em **Matricula__c**, crie a validation rule `Turma_Sem_Vaga`:
   ```text
   AND(
     ISPICKVAL(Situacao__c, "Ativa"),
     ISNEW(),
     Turma__r.Vagas_Restantes__c <= 0
   )
   ```
8. Crie as abas dos quatro objetos e um app "Escola" com elas.
9. Cadastre: 2 cursos, 3 turmas, 5 alunos, e matricule até estourar a validação.

**Critério de aprovação.**
- [ ] Ao criar a matrícula que excede as vagas, a mensagem de erro aparece no campo certo.
- [ ] `Vagas_Restantes__c` atualiza sozinho ao trancar uma matrícula.
- [ ] Apagar uma Turma apaga suas Matrículas (teste com uma turma descartável).
- [ ] Você consegue explicar por que o rollup só foi possível ali.

**Por que importa.** Você exercitou master-detail, junção N:N, rollup, fórmula e validação —
o núcleo do trabalho de um administrador — e sentiu o efeito cascata da exclusão.

**Pergunta para pensar:** o que aconteceria se `Turma__c` fosse Lookup em vez de
Master-Detail em `Matricula__c`? O que você perderia?

---

## Lab 2 — Segurança em camadas

**Objetivo.** Provar, na prática, que as cinco camadas são independentes.

**Pré-requisito.** Lab 1.

**Passos.**

1. Mude o OWD de **Aluno__c** para **Private** (`Setup → Sharing Settings`).
2. Crie dois usuários (Setup → Users):
   - `professor@suaorg.teste` — perfil Standard User.
   - `coordenador@suaorg.teste` — perfil Standard User.
3. Crie papéis: **Coordenação** e, abaixo dela, **Professor**. Atribua os usuários.
4. Crie o permission set **Escola_Basico** com: Read/Create/Edit nos quatro objetos e FLS
   em todos os campos. Atribua aos dois usuários.
5. Faça login como professor (`Setup → Users → Login`). Crie um aluno.
6. Faça login como coordenador. **Você vê o aluno criado pelo professor?** (Deve ver, pela
   hierarquia.)
7. Faça login como professor de novo. Ele vê alunos criados pelo coordenador? (Não deve.)
8. Crie uma **sharing rule** em Aluno__c: registros do papel Coordenação → Read para o
   papel Professor. Teste de novo.
9. Remova o FLS de `Nota_Final__c` do permission set. Faça login como professor: o campo
   sumiu da tela **e do relatório**.
10. Dê `View All` em Aluno__c ao permission set. Remova a sharing rule. O professor vê tudo?

**Critério de aprovação.**
- [ ] Você consegue explicar, para cada teste, **qual camada** produziu o resultado.
- [ ] Você demonstrou que FLS e acesso a registro são independentes.
- [ ] Você demonstrou que `View All` ignora o OWD e a hierarquia.

**Por que importa.** Ninguém entende o modelo de segurança lendo — só testando com dois
usuários. E "no meu usuário funciona" é a frase que precede todo incidente.

---

## Lab 3 — Automação com Flow

**Objetivo.** Escrever Flows corretos e sentir a diferença entre Before e After Save.

**Passos.**

1. **Before-Save Flow** em `Matricula__c`:
   - Gatilho: criação. Otimize para: *Fast Field Updates*.
   - Se `Situacao__c` for vazio, atribua "Ativa".
   - Ative e teste.
2. **After-Save Flow** em `Matricula__c`:
   - Gatilho: criação ou atualização, quando `Situacao__c` mudar para "Concluída".
   - Ação: criar um registro em um objeto `Certificado__c` (crie-o: Aluno lookup,
     Turma lookup, `Emitido_em__c` Date).
   - Adicione **fault path** com uma mensagem clara.
3. **Scheduled Flow**: todo dia às 6h, encontre turmas que começam hoje e envie e-mail ao
   professor.
4. **Screen Flow**: um assistente de matrícula — tela 1 escolhe o aluno, tela 2 escolhe a
   turma (mostrando vagas restantes), tela 3 confirma. Publique como ação em Aluno__c.
5. **O experimento que ensina:** crie um Flow record-triggered *After-Save* em `Aluno__c`
   que atualiza um campo **do próprio aluno**. Salve um aluno e olhe o debug log
   (`Setup → Debug Logs`, nível FINEST). Conte quantas vezes o ciclo de gravação rodou.
   Depois refaça como **Before-Save** e compare.

**Critério de aprovação.**
- [ ] O experimento do passo 5 mostrou dois ciclos no After-Save e um no Before-Save.
- [ ] Todos os Flows têm fault path.
- [ ] Você consegue dizer onde cada Flow entra na ordem de execução.

**Por que importa.** A diferença Before/After é a decisão de maior impacto em performance
de Flow, e é invisível até você medir.

---

## Lab 4 — Relatórios e painéis

**Objetivo.** Dominar a ferramenta que resolve 90% dos pedidos de "preciso de um dashboard".

**Passos.**

1. Report Type customizado: `Turma__c` com `Matricula__c` (com e sem).
2. Relatório **Summary**: matrículas agrupadas por Curso e por Situação, com contagem.
3. Relatório **Matrix**: Curso × Nível, com média de `Nota_Final__c`.
4. Adicione um **bucket field** agrupando notas em Baixa (<6), Média (6–8), Alta (>8).
5. Adicione uma **fórmula de resumo** (`PARENTGROUPVAL`) mostrando o % de cada situação
   sobre o total do curso.
6. Crie um **dashboard** com 4 componentes, incluindo um gráfico de rosca e uma métrica.
7. Agende o envio do dashboard por e-mail toda segunda às 8h.
8. Crie um **Reporting Snapshot**: grave a contagem de matrículas ativas por turma num
   objeto customizado, diariamente. Depois faça um relatório de tendência sobre ele.

**Critério de aprovação.**
- [ ] O relatório Matrix mostra médias corretas, conferidas na mão.
- [ ] A fórmula de resumo mostra percentuais que somam 100% por grupo.
- [ ] O snapshot gravou pelo menos uma linha.

**Por que importa.** Relatórios nativos são gratuitos, respeitam segurança automaticamente
e resolvem quase tudo. Muita gente compra BI para fazer o que o produto já faz.
**Reporting Snapshot é a resposta para "como vejo a evolução ao longo do tempo?"** — que os
relatórios normais não respondem, porque só mostram o estado atual.

---

## Lab 5 — Primeiro trigger bulk-safe

**Objetivo.** Escrever um trigger no padrão canônico e provar que ele é bulk-safe.

**Passos.**

1. Crie o trigger `MatriculaTrigger` no padrão de
   [15-apex.md](15-apex.md) §3.1 (trigger vazio + handler).
2. Regra: ao criar uma matrícula, se a turma não tiver vagas, `addError` na matrícula.
   *(Sim, a validation rule do Lab 1 já faz isso. Faça em Apex também, num objeto de teste
   separado, para comparar as duas abordagens.)*
3. Regra: ao concluir uma matrícula, atualizar `Ultima_Conclusao__c` no Aluno.
4. **Escreva a versão errada primeiro**, com SOQL dentro do laço.
5. No Execute Anonymous, insira 200 matrículas de uma vez. Veja o erro:
   `Too many SOQL queries: 101`.
6. Corrija com o padrão de três passos (Set → Map → itere).
7. Meça:
   ```apex
   Integer soql0 = Limits.getQueries();
   Integer dml0  = Limits.getDmlStatements();
   insert minhasDuzentas;
   System.debug('SOQL: ' + (Limits.getQueries() - soql0));
   System.debug('DML: '  + (Limits.getDmlStatements() - dml0));
   ```

**Critério de aprovação.**
- [ ] Você **viu** o erro `Too many SOQL queries: 101` antes de corrigir.
- [ ] Depois da correção: ≤ 3 SOQL e ≤ 2 DML para 200 registros.
- [ ] Existe apenas **um** trigger no objeto.
- [ ] Você consegue explicar quando usar `addError` e quando usar validation rule.

**Por que importa.** Ver o erro acontecer ensina mais que ler sobre ele. E você vai
reconhecê-lo instantaneamente quando aparecer em produção.

---

## Lab 6 — Testes que realmente testam

**Objetivo.** Distinguir cobertura de qualidade.

**Passos.**

1. Escreva um teste para o trigger do Lab 5 que **cobre 100% e não tem nenhum `Assert`**.
   Rode e veja a cobertura em `Setup → Apex Test Execution`.
2. Agora **quebre o handler de propósito** (inverta uma condição). Rode o teste. **Ele passa.**
   Guarde essa sensação.
3. Reescreva o teste com asserções de verdade:
   - caminho feliz;
   - caminho de erro (turma sem vaga);
   - caso de borda (turma com exatamente 1 vaga);
   - **teste bulk com 200 registros**;
   - `System.runAs` com um usuário não-administrador.
4. Use `@TestSetup` para os dados comuns.
5. Rode com `--code-coverage` e compare a cobertura antes e depois. *(Provavelmente é a
   mesma — este é o ponto do laboratório.)*
6. Quebre o handler de novo. Agora o teste **deve** falhar.

**Critério de aprovação.**
- [ ] Você demonstrou um teste com 100% de cobertura que não detecta um bug.
- [ ] A suíte final falha quando você introduz o bug.
- [ ] O teste bulk usa 200 registros e passa.
- [ ] Nenhum teste usa `SeeAllData=true`.

**Por que importa.** A plataforma só mede cobertura. **A qualidade é responsabilidade sua**,
e a maioria do Apex do mundo não tem essa qualidade.

---

## Lab 7 — LWC com Apex e refresh

**Objetivo.** Construir um componente completo e resolver o problema de cache.

**Passos.**

1. Crie um LWC `painelTurma` para a página de registro de `Turma__c`.
2. Método Apex `@AuraEnabled(cacheable=true)` que lista as matrículas da turma.
3. Exiba em `lightning-datatable`, com coluna de ação "Trancar".
4. Método Apex `@AuraEnabled` (sem cacheable) que tranca a matrícula.
5. **Faça errado primeiro:** chame o método de trancar e não atualize a tabela.
   Observe que a linha continua "Ativa" na tela.
6. Corrija com `refreshApex()` — guardando o **objeto do wire**, não só `.data`.
7. Adicione: spinner durante a operação, toast de sucesso e de erro, botão desabilitado
   durante o processamento.
8. Use `AuraHandledException` no Apex e verifique a mensagem que chega ao componente.
   Depois troque por uma exceção comum e veja `"Script-thrown exception"`.
9. Escreva um teste Jest que mocka o Apex e verifica a renderização.

**Critério de aprovação.**
- [ ] A tabela atualiza após trancar, sem recarregar a página.
- [ ] O erro do Apex chega ao usuário com mensagem legível.
- [ ] Duplo clique no botão não executa a ação duas vezes.
- [ ] O teste Jest passa em menos de 5 segundos.

**Por que importa.** O ciclo "carregar → agir → atualizar" é 80% do trabalho de front-end
na plataforma, e o problema de cache do `@wire` derruba todo iniciante.

---

## Lab 8 — Batch sobre volume

**Objetivo.** Processar mais registros do que cabe numa transação.

**Passos.**

1. Gere 50.000 registros de `Aluno__c` com um script:
   ```apex
   List<Aluno__c> lote = new List<Aluno__c>();
   for (Integer i = 0; i < 10000; i++) {
       lote.add(new Aluno__c(Name = 'Aluno ' + i, Email__c = 'a' + i + '@teste.invalid'));
   }
   insert lote;   // rode 5 vezes, mudando o prefixo do e-mail
   ```
   *(Atenção à cota de 5 MB da Developer Edition. Se estourar, use 10.000 e ajuste o lab.)*
2. Escreva um Batch que calcula um campo `Classificacao__c` a partir da média de notas.
3. Implemente `Database.Stateful` para contar processados e erros.
4. No `finish`, grave um registro de log num objeto `Job_Log__c`.
5. Rode com tamanho de lote **200**. Anote o tempo total em `Setup → Apex Jobs`.
6. Rode com **50** e com **1000**. Compare tempo e erros.
7. Introduza um cálculo caro (um laço de 10.000 iterações por registro) e veja o
   `Apex CPU time limit exceeded` no lote de 1000.
8. Agende com `System.schedule` para as 2h.

**Critério de aprovação.**
- [ ] Você processou mais de 10.000 registros.
- [ ] Você tem números concretos comparando três tamanhos de lote.
- [ ] Você **provocou** o erro de CPU e sabe qual parâmetro o resolve.
- [ ] O `Job_Log__c` registrou a execução.

**Por que importa.** Tamanho de lote é o parâmetro mais importante e menos entendido de
Batch Apex. Só se aprende medindo.

---

## Lab 9 — Integração idempotente

**Objetivo.** Construir uma integração que sobrevive à realidade.

**Pré-requisito.** Um endpoint de teste — use https://httpbin.org, https://webhook.site,
ou um Heroku/ngrok próprio.

**Passos.**

1. Crie o objeto de fila `Integracao__c` com os campos do Exemplo 13 de
   [06-exemplos.md](06-exemplos.md).
2. Crie a Named Credential apontando para o endpoint de teste.
3. Trigger que enfileira ao concluir uma matrícula (upsert por chave de idempotência).
4. Queueable que processa a fila e faz o callout.
5. **Teste o caminho feliz** com um mock.
6. **Teste a falha:** aponte para uma URL que devolve 500 (`httpbin.org/status/500`).
   Verifique o backoff exponencial e a contagem de tentativas.
7. **Teste a duplicata:** enfileire o mesmo registro duas vezes. Verifique que só existe
   uma linha, graças ao `unique`.
8. Implemente o circuit breaker e prove que ele abre após 5 falhas seguidas.
9. Escreva os testes com `HttpCalloutMock` cobrindo: 200, 409, 400, 500 e timeout.

**Critério de aprovação.**
- [ ] Enfileirar duas vezes o mesmo registro produz **uma** linha.
- [ ] Após 5 falhas, o circuito abre e nenhum callout novo é feito.
- [ ] Um erro 400 não é retentado; um 500 é.
- [ ] Um erro 409 é tratado como sucesso.
- [ ] Todos os testes passam sem callout real.

**Por que importa.** Este é o laboratório que mais se aproxima de trabalho real de produção.
Se você fizer só um da lista, faça este.

---

## Lab 10 — Investigação de performance

**Objetivo.** Diagnosticar por que algo está lento, com evidência.

**Passos.**

1. **Crie o problema:** adicione três Flows After-Save em `Matricula__c`, uma validation
   rule com fórmula pesada, e um trigger com um laço aninhado O(n²).
2. Insira 200 matrículas. Meça: `Setup → Debug Logs`, nível `FINEST` em ApexCode.
3. Abra o log na **Developer Console** e use a aba **Execution Overview / Timeline** para
   ver onde o tempo foi.
4. Identifique o maior consumidor de CPU.
5. Corrija o laço O(n²) usando `Map`. Meça de novo.
6. Converta os Flows After-Save em Before-Save onde possível. Meça de novo.
7. Use o **Query Plan** da Developer Console (ative em Preferences) numa consulta com
   `WHERE campo_nao_indexado__c = 'x'`. Anote o `Cost`. Depois filtre por
   `CreatedDate` e compare.
8. Escreva um relatório de uma página: sintoma → medição → causa → correção → medição final.

**Critério de aprovação.**
- [ ] Você tem números de CPU **antes e depois** de cada correção.
- [ ] Você identificou o consumidor dominante com evidência do log, não por palpite.
- [ ] Você mostrou a diferença de `Cost` no Query Plan entre campo indexado e não indexado.
- [ ] O relatório cabe em uma página.

**Por que importa.** Diagnosticar performance é a habilidade que separa sênior de pleno.
E "acho que é o Flow" não é diagnóstico — número é.

---

## Projeto final integrador

Junte tudo. Escolha **um** domínio real do seu trabalho ou da sua vida (oficina mecânica,
consultório, clube, ONG, imobiliária) e construa:

- [ ] modelo de dados com ao menos 4 objetos, um deles de junção;
- [ ] segurança com OWD restritivo, 2 papéis, permission sets e ao menos uma sharing rule;
- [ ] automação: 1 Flow Before-Save, 1 After-Save, 1 trigger com handler;
- [ ] 1 LWC funcional na página de registro;
- [ ] 1 Batch agendado;
- [ ] 1 integração idempotente com sistema externo;
- [ ] suíte de testes com > 85% de cobertura **e asserções reais**;
- [ ] tudo versionado em Git, com README explicando as decisões;
- [ ] um relatório e um dashboard.

**Critério:** outra pessoa consegue clonar o repositório, rodar
`sf project deploy start` numa org limpa, executar o seed e usar o sistema — seguindo só o
seu README.

Se você conseguir isso, está pronto para trabalhar. Use o
[07-projeto-modelo/](07-projeto-modelo/README.md) como referência de estrutura.

---

## Autoteste

1. No Lab 1, por que o rollup só foi possível com master-detail?
2. No Lab 2, qual camada de segurança produziu cada resultado observado?
3. No Lab 3, quantos ciclos de gravação o After-Save gerou? E o Before-Save?
4. No Lab 5, com quantas SOQL e DML o trigger corrigido processa 200 registros?
5. No Lab 6, como um teste com 100% de cobertura pode não detectar um bug?
6. No Lab 7, por que a tabela não atualizava, e qual foi a correção exata?
7. No Lab 8, qual parâmetro resolve `Apex CPU time limit exceeded` num Batch?
8. No Lab 9, por que 409 é sucesso e 400 não é retentado?
9. No Lab 10, qual foi o consumidor dominante de CPU e como você provou isso?
