# 75 · Armadilhas, mitos e más práticas

`Nível: todos` · `01/09/2026`

---

Este arquivo é a lista de cicatrizes. Cada item aqui custou tempo, dinheiro ou
credibilidade de alguém.

---

## Parte I · 22 armadilhas

### Grupo A — dados e cardinalidade

**1. Confundir "um item com uma lista" com "uma lista de itens".**
Sintoma: "só processou o primeiro". Cura: `Split Out`.
**A armadilha mais frequente do n8n, disparado.**

**2. Não perceber o multiplicador de chamadas.**
Um Split Out que gera 500 itens antes de um HTTP Request faz **500 requisições**.
Se roda a cada minuto: 720 mil por dia. Já rendeu bloqueio por abuso e conta salgada.
Cura: contar itens antes de rodar; usar batching.

**3. Quebrar o item linking em Code node e culpar o n8n.**
`Can't determine which item to use` não é bug: é o n8n se recusando a adivinhar.
Cura: declarar `pairedItem` ([12](12-o-modelo-de-dados.md#43-como-preservar-a-correspondência-no-code-node)).

**4. Usar `$('Nó').item` como se fosse `JOIN`.**
Funciona até a cardinalidade mudar. Quando a correspondência é por chave de
negócio, use **Merge → Combine by Matching Fields**.

**5. `Merge` por posição em produção.**
Passa no teste (as fontes vêm ordenadas) e falha quando uma devolve um item a menos.
Cura: casar por chave.

**6. Ramo que não recebe item some em silêncio.**
Nem erro, nem aviso. O fluxo "termina verde" sem fazer nada.
Cura: `Always Output Data` + tratamento explícito do caso vazio.

### Grupo B — expressões e código

**7. Procurar o corpo do webhook em `$json` em vez de `$json.body`.**

**8. Renomear um nó depois de escrever expressões.**
As conexões e as expressões referenciam o **nome**. Nada é atualizado.

**9. `plus(7, 'days')` dentro do Code node.**
Não dá erro. Simplesmente não faz o que você quer. Cura: `plus({ days: 7 })`.

**10. Comparação de tipos frouxa.**
`"10" > "9"` é `false`. Cura: `typeValidation: strict` e conversão explícita.

**11. Expressão de dez linhas dentro de um campo.**
Não tem teste, não tem leitura, não tem histórico. Cura: node Code.

**12. `catch` vazio.**
Transforma falha em sucesso silencioso — o pior estado possível.

### Grupo C — operação

**13. Não ligar a poda de execuções.**
**O problema operacional nº 1 do n8n autogerido.** O banco cresce até encher o
disco, e aí você está fazendo `DELETE` em lotes às 2 da manhã.

**14. Perder a `N8N_ENCRYPTION_KEY`.**
Todas as credenciais viram lixo cifrado. Backup do banco não salva.

**15. Esquecer `GENERIC_TIMEZONE`.**
O padrão é UTC. Seu relatório "das 8h" sai às 5h.

**16. Esquecer `WEBHOOK_URL` atrás de proxy ou túnel.**
O nó mostra `localhost` e o provedor externo não alcança.

**17. Esquecer `PGDATA` no Postgres 18.**
O banco é escrito fora do volume e **reaparece vazio** no próximo boot.

**18. Ligar `Retry On Fail` em operação não idempotente.**
Não é resiliência: é duplicação automatizada. Dois e-mails, dois pedidos, dois débitos.

**19. Rodar task runners em modo interno em produção.**
Quem pode editar um workflow lê todas as credenciais da instância.
Não é exótico: é o comportamento documentado.

**20. `Save` sem `Publish`.**
Você edita, testa, fecha o navegador. A produção continua com a versão antiga.

### Grupo D — projeto

**21. O fluxo-monstro de 80 nós.**
Ninguém entende, ninguém mexe, e mudar qualquer coisa dá medo. Cura: sub-workflows
e sticky notes.

**22. Nenhum Error Workflow.**
Falhas em produção viram linhas no histórico que ninguém abre.

---

## Parte II · 12 mitos

**Mito 1 — "n8n é open source."**
**Falso, tecnicamente.** É *fair-code*, sob a **Sustainable Use License**, que
restringe uso comercial a "fins internos de negócio". O GitHub classifica a licença
como *"Other"*. Ler [80-custos-e-licencas.md](80-custos-e-licencas.md) antes de
construir um produto em cima **não é opcional**.

**Mito 2 — "low-code significa que não precisa saber programar."**
Falso, e é o mito mais caro do setor. Você não precisa **digitar** muito código.
Você continua precisando entender dados, tipos, erros, idempotência, autenticação e
concorrência. Low-code muda a superfície, não a natureza do problema.

**Mito 3 — "autogerir é grátis."**
O software é. Servidor, backup, monitoramento, atualização, TLS e o **seu tempo**
não são. Contas em [80](80-custos-e-licencas.md).

**Mito 4 — "ramos paralelos rodam em paralelo."**
Falso. O n8n executa em profundidade, ramo por ramo. Dois ramos levam `t₁ + t₂`.

**Mito 5 — "o n8n garante que a execução acontece exatamente uma vez."**
Falso — e nenhum sistema distribuído garante. O que existe é *at-least-once* mais
idempotência ([60](60-teoria-avancada.md#4-garantias-de-entrega-e-o-teorema-que-não-dá-para-burlar)).

**Mito 6 — "n8n substitui um desenvolvedor."**
Falso. Ele muda **o que** o desenvolvedor faz: menos encanamento, mais desenho e
mais operação. Times que demitiram esperando isso reaprenderam da forma cara.

**Mito 7 — "quanto mais nós, mais profissional."**
Ao contrário. O fluxo bom é o que qualquer um lê em trinta segundos.

**Mito 8 — "preciso de um agente de IA."**
Quase sempre não. Se você consegue enumerar os casos, use `Switch` + chain: mais
barato, mais rápido, testável. Agente é para quando o caminho depende do conteúdo
de forma que você não consegue enumerar.

**Mito 9 — "o n8n aguenta processar milhões de registros."**
Falso, e é limite de projeto, não de máquina: ele materializa a saída de cada nó
por completo ([60](60-teoria-avancada.md#7-o-limite-arquitetural-enunciado-com-precisão)).
Para volume, use o banco ou uma ferramenta de ETL — com o n8n orquestrando.

**Mito 10 — "webhook é sempre melhor que polling."**
Quase sempre, não sempre. Webhook exige ser alcançável da internet, exige autenticar,
exige tolerar reenvio e **perde eventos quando você está fora do ar**. Polling é
tolerante a queda. A escolha é de engenharia, não de moda.

**Mito 11 — "o Pin data é só para desenvolvimento."**
Cuidado: dado fixado pode valer também em produção nas versões em que ele fica
marcado no fluxo. Despine antes de publicar.

**Mito 12 — "vou instalar por npm porque é mais simples."**
**Some no n8n 3.0, em outubro de 2026.** Instalar por npm hoje é criar trabalho de
migração para daqui a poucos meses.

---

## Parte III · Más práticas que persistem, e por quê

### 1. Copiar fluxo de tutorial do YouTube e pôr em produção

**Por que persiste:** funciona na demonstração, e a demonstração é convincente.
**O problema:** tutoriais otimizam para o caminho feliz em 12 minutos. Não tem
tratamento de erro, nem idempotência, nem poda, nem Error Workflow.
**O que fazer:** use como esqueleto; acrescente o [checklist de produção](18-erros-e-confiabilidade.md#8-checklist-de-produção).

### 2. Credencial de administrador para tudo

**Por que persiste:** funciona de primeira e ninguém quer brigar com escopos.
**O problema:** um fluxo comprometido tem acesso total ao sistema conectado.
**O que fazer:** uma credencial por finalidade, com o menor escopo que funciona.

### 3. Segredos escritos dentro do nó

**Por que persiste:** é mais rápido do que criar credencial.
**O problema:** o segredo entra no JSON exportado, no Git e nos dados de execução.
**O que fazer:** credencial, sempre. Se for valor de configuração, `$vars` ou uma
tabela de configuração.

### 4. Polling de um minuto "porque é mais rápido"

**Por que persiste:** parece grátis quando você autogere.
**O problema:** 43.200 execuções/mês por fluxo, banco crescendo, API alheia irritada.
**O que fazer:** webhook, ou o maior intervalo que o negócio aceitar.

### 5. Um n8n para a empresa inteira, na edição Community

**Por que persiste:** RBAC é licenciado e o orçamento é apertado.
**O problema:** **não há isolamento** — todo mundo alcança todas as credenciais.
**O que fazer:** ou licenciar, ou **subir instâncias separadas por time**. A segunda
é barata, legítima e quase ninguém considera.

### 6. Testar só o caminho feliz

**Por que persiste:** testar erro dá trabalho e não aparece na demonstração.
**O problema:** o caminho feliz é o que menos acontece em integração.
**O que fazer:** teste com entrada vazia, entrada malformada, serviço fora do ar,
**e o mesmo evento duas vezes**.

### 7. Não documentar nada porque "o canvas é autoexplicativo"

**Por que persiste:** o canvas realmente parece autoexplicativo — para quem acabou
de construí-lo.
**O problema:** três meses depois, nem você entende por que aquele IF existe.
**O que fazer:** sticky notes explicando o **porquê**, nomes de nó em linguagem de
negócio, e um sticky de cabeçalho com dono, gatilho e o que fazer se falhar.

---

## O teste de fogo

Antes de dizer que um fluxo está pronto, responda em voz alta:

1. Se rodar duas vezes com a mesma entrada, o que acontece?
2. Se falhar no item 37 de 200, o que já foi feito e o que não foi?
3. Se este fluxo **parar de rodar**, quanto tempo até alguém perceber?
4. Se a API do outro lado mudar o formato amanhã, o fluxo falha alto ou grava lixo?
5. Se eu sair da empresa, outra pessoa consegue manter isto?

Quem responde as cinco entrega automação. Quem não responde entrega uma demonstração.

---

## Autoteste

1. Qual é a armadilha mais frequente do n8n e qual nó a resolve?
2. Por que `Can't determine which item to use` não é bug?
3. Por que `Merge by position` passa no teste e falha em produção?
4. O n8n é open source? Responda com precisão.
5. Ramos "paralelos" no canvas rodam em paralelo? Qual o tempo total?
6. Por que "webhook é sempre melhor que polling" é um mito?
7. Cinco pessoas numa instância Community compartilham o quê? Qual a saída barata?
8. Por que copiar fluxo de tutorial para produção dá errado?
9. Enuncie as cinco perguntas do teste de fogo.

---

*Anterior: [70-pratica.md](70-pratica.md) · Próximo: [80-custos-e-licencas.md](80-custos-e-licencas.md)*
