# 25 · Os níveis — rubrica para se autoavaliar sem ilusão

**Nível:** intermediário · **Escrito em:** 20/08/2026

> Este arquivo responde a pergunta que originou o curso de forma **operacional**:
> não "o que é" um dev que sabe usar IA, mas **como se reconhece um**, e como
> saber onde você está.

---

## A rubrica

Cada nível é definido por **comportamento observável**, não por ferramenta,
tempo de uso ou opinião sobre IA.

---

### L0 · Recusa

**Comportamento:** não usa, por princípio, medo, política da empresa ou
desconfiança.

**Evidência:** nenhuma ferramenta instalada; argumenta contra sem ter testado.

**Vale dizer:** L0 **não é burrice**. Há razões legítimas — política de
conformidade, código altamente sensível, domínio onde a IA de fato atrapalha.

**Vale dizer também:** quem está em L0 por preguiça travestida de princípio
perde competitividade em tarefas mecânicas, e isso é mensurável.

**Para sair:** faça o [04-como-comecar](04-como-comecar.md) uma vez, num
projeto descartável. Uma hora.

---

### L1 · Autocompleta

**Comportamento:** aceita sugestões de linha. Não delega tarefa.

**Evidência:**
- Usa Copilot/Cursor Tab e nada mais.
- Fala em termos de "aceitar sugestão".
- Não tem `AGENTS.md` em projeto nenhum.

**Ganho:** pequeno e real (~5–15% do tempo de digitação).
**Risco:** deriva por aceitação fácil (ver [13](13-os-quatro-modos-de-uso.md)).

**Para sair:** use o chat para **entender** código, não para gerar. É o degrau
de menor risco e maior retorno.

---

### L2 · Conversa

**Comportamento:** pergunta, recebe, adapta, cola. O código passa pelas mãos
dele.

**Evidência:**
- Chat aberto o dia todo.
- Cola trechos, adapta, integra.
- Fala em "prompt bom" e coleciona técnicas de prompt.
- Não delega tarefa inteira porque "não confia".

**Ganho:** médio. **Teto:** aqui.

> **Diagnóstico central deste curso:** a maior parte do mercado em agosto de
> 2026 está em **L2 se achando L4**. O sintoma é usar ferramenta de agente
> (modo 4) com hábito de L2: delegar, não verificar, e ler na diagonal.

**Para sair — e este é o degrau que mais gente não sobe:**

Escolha uma tarefa. Antes de pedir qualquer coisa, escreva **como você vai
saber que voltou certo**. Se você não consegue escrever isso, você não está
pronto para delegar aquela tarefa — e essa é a descoberta que faz a pessoa subir.

---

### L3 · Delega com verificação

**Comportamento:** define escopo, delega, e confia no **portão**, não na
leitura.

**Evidência observável:**
- [ ] Escreve critérios de aceitação antes de pedir.
- [ ] Frequentemente escreve o teste antes da implementação.
- [ ] Tem `AGENTS.md` nos projetos, com uma tela.
- [ ] Roda o teste **ele mesmo**, nunca confia no relato.
- [ ] Sabe dizer, para cada tarefa, se vai delegar e por quê.
- [ ] Interrompe (`Esc`) cedo, sem dó.
- [ ] Recomeça com contexto limpo em vez de insistir.
- [ ] Trabalha em branch/*worktree*, commita antes de delegar.
- [ ] Sabe quando **não** usar IA (`sed`, `git bisect`, à mão).

**Ganho:** **aqui começa o ganho real.**
**Tempo típico:** 2 a 4 meses de uso diário.

**O que ainda o limita:** ele verifica bem no que ele mesmo montou; o
repositório em volta ainda não trabalha a favor dele.

**Para sair:** pare de otimizar sessões e comece a otimizar o **repositório**.
Acelere a suíte. Adicione tipos. Escreva o portão.

---

### L4 · Projeta o ambiente

**Comportamento:** trata o repositório como o artefato que determina a qualidade
do que os agentes produzem.

**Evidência observável:**
- [ ] A suíte de testes roda em menos de 5 minutos, e ele **fez isso acontecer**.
- [ ] Existe um comando único (`make check`) que responde "está bom?".
- [ ] Existe portão automático antes da `main`, com escopo, tamanho, segredos e
      dependências.
- [ ] Fronteiras de arquitetura são **verificadas**, não combinadas.
- [ ] Estados ilegais são impossíveis de representar em código novo.
- [ ] Mensagens de erro dizem o que veio, o que se esperava e o que fazer.
- [ ] Existem ADRs para decisões contraintuitivas.
- [ ] Ele mede: cobertura do diff, duplicação, tempo de revisão.
- [ ] Ele consegue explicar por que o repositório está organizado assim.

**Ganho:** **grande e composto** — cada melhoria vale para todas as sessões
futuras, de todas as pessoas.
**Tempo típico:** 6 a 12 meses.
**O que o limita:** precisa de autonomia técnica para investir em coisa que não
aparece no roadmap.

---

### L5 · Opera em escala

**Comportamento:** muda o processo do time, não só o próprio trabalho.

**Evidência observável:**
- [ ] Coordena mais de um agente sem virar o gargalo.
- [ ] Definiu a política de revisão proporcional ao risco, e ela é seguida.
- [ ] Aumentou a **capacidade de revisão**, não só a de produção.
- [ ] Mede vazão da `main` e estabilidade, não "percentual de código de IA".
- [ ] Sabe dizer quanto o time gasta de API por PR fundido.
- [ ] Formou outras pessoas — há mais gente em L3/L4 por causa dele.
- [ ] Sabe recusar: identifica onde a IA não deve entrar e sustenta a decisão.

**Tempo típico:** 1 a 2 anos, e **depende da organização** — L5 exige mandato,
não só habilidade.

---

## Autoavaliação honesta

Responda com sim/não, sem generosidade.

### Bloco A — está em L3?

1. Na sua última tarefa delegada, você escreveu o critério de aceitação **antes**?
2. Você rodou os testes **você mesmo**, ou aceitou o relato?
3. Você consegue nomear três tipos de tarefa que **não** delega, e o porquê?
4. Na última vez que o agente entrou em laço improdutivo, você interrompeu na
   segunda tentativa ou na oitava?
5. Os seus projetos têm `AGENTS.md`? Ele cabe numa tela?

**5 sins = L3. 3–4 = quase. Menos de 3 = L2.**

### Bloco B — está em L4?

6. Quanto tempo leva a sua suíte? Você **mediu** ou está chutando?
7. Existe um comando único que diz se o repositório está saudável?
8. Alguma verificação **bloqueia** o merge, ou tudo depende de alguém olhar?
9. Se um agente adicionasse uma dependência hoje, alguém perceberia
   automaticamente?
10. Você consegue mostrar a tendência de duplicação do seu repositório?

**5 sins = L4. Menos = L3 com ambição.**

### Bloco C — está em L5?

11. O tempo médio até a primeira revisão do seu time subiu ou caiu no último
    trimestre? Você sabe?
12. A política de revisão é escrita e proporcional ao risco?
13. Quanto o time gastou de API no mês passado, por PR fundido?
14. Quantas pessoas subiram de nível por causa da sua atuação?

---

## Como entrevistar para isto

Se você contrata, estas perguntas separam bem. As respostas ruins são as
genéricas.

| Pergunta | Resposta L2 | Resposta L4 |
|---|---|---|
| "Como você usa IA no trabalho?" | Lista ferramentas | Descreve o fluxo: espec → teste → delega → portão → revisa |
| "Conte de uma vez em que a IA te atrapalhou." | "Ela erra às vezes" | Caso concreto, com o que ele mudou no processo depois |
| "Como você sabe que o código gerado está certo?" | "Eu leio" / "os testes passam" | Descreve a pirâmide de verificação e o que cada camada pega |
| "O que você **não** delega?" | "Coisas complexas" | Lista específica, com o critério ("o que eu não conseguiria avaliar") |
| "Como você faria isso num repositório sem testes?" | Delega mesmo assim | Escreve teste de caracterização primeiro |
| "Como você mediria se está valendo a pena?" | "Sinto que sou mais rápido" | Vazão da `main`, tempo de revisão, reversões, custo |

> **A pergunta mais reveladora é a quarta.** Quem responde "coisas complexas"
> não tem critério. Quem responde "o que eu não conseguiria avaliar se voltasse
> errado" entendeu o ofício.

---

## O que **não** define o nível

Para evitar leitura errada da rubrica:

| Não define | Por quê |
|---|---|
| Quantas ferramentas você usa | Cinco ferramentas mal usadas é L1 com cinco assinaturas |
| Quanto você gasta por mês | Gasto alto pode indicar sessão mal gerida |
| Quanto código de IA está na sua base | Métrica inflável e sem correlação com valor |
| Quantos anos de experiência | A METR mediu **seniores** ficando mais lentos |
| Se você é a favor ou contra IA | Postura não é competência |

---

## Autoteste

1. Descreva os seis níveis em uma frase cada.
2. Por que L0 não é necessariamente ignorância?
3. Qual é o diagnóstico central deste curso sobre onde o mercado está?
4. Qual é o degrau que mais gente não sobe, e qual é a descoberta que faz subir?
5. Cite cinco evidências observáveis de L3.
6. Por que o ganho de L4 é "composto"?
7. O que L5 exige além de habilidade?
8. Qual é a pergunta de entrevista mais reveladora e por quê?
9. Cite três coisas que **não** definem o nível.
10. Faça a autoavaliação do Bloco A. Onde você está de verdade?

---

**Anterior:** [24-produtividade-o-que-diz-a-evidencia](24-produtividade-o-que-diz-a-evidencia.md) ·
**Próximo:** [26-carreira-e-mercado](26-carreira-e-mercado.md)
