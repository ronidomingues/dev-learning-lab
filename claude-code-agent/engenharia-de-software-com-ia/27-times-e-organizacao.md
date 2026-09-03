# 27 · Times e organização

**Nível:** avançado · **Escrito em:** 20/08/2026

> Se a IA é amplificadora — e é o achado central do DORA — então o resultado
> depende mais do sistema em volta do que da ferramenta. Este arquivo é sobre o
> sistema.

---

## 1 · O erro de adoção mais comum

```
Comprar licenças  →  esperar ganho  →  medir "% de código de IA"  →  frustração
```

Falha porque otimiza a etapa errada. A escrita não era o gargalo na maioria dos
times; virou-se ainda menos gargalo, e o gargalo real — revisão, decisão,
integração — ficou **pior**, porque agora chega mais coisa nele.

### A sequência que funciona

```
1. MEDIR a linha de base        vazão da main, tempo de revisão, tamanho de PR,
                                reversões, duplicação
2. CONSERTAR o gargalo          quase sempre: suíte lenta, revisão em fila,
                                deploy manual, ambiente que não sobe
3. INSTRUMENTAR                 portão automático, tipos, linter, cobertura do diff
4. ADOTAR                       ferramentas, com política escrita
5. MEDIR de novo                comparar com o passo 1
6. AJUSTAR                      capacidade de revisão, tamanho de PR, política
```

Os passos 1 a 3 são **engenharia de software comum**. É por isso que o DORA
encontra que o retorno vem do sistema organizacional e não da ferramenta: quem
faz 1–3 ganha; quem pula direto para o 4 produz estoque.

---

## 2 · A política mínima escrita

Toda equipe precisa de um documento curto — uma página — respondendo:

| Pergunta | Exemplo de resposta |
|---|---|
| Quais ferramentas são permitidas? | Claude Code e Copilot, contas corporativas |
| O que **não** pode ser enviado? | Código de cliente sob NDA, dado pessoal, segredo |
| O que exige revisão humana 100%? | Autenticação, pagamento, permissão, migração, infra |
| Qual o limite de tamanho de PR? | 400 linhas, verificado no CI |
| Como marcar código gerado? | *Trailer* `Assisted-by:` e `Review-level:` |
| Quem paga e qual o teto? | Orçamento por time, alerta em 80% |
| O que fazer se um segredo vazar? | Rotacionar primeiro; ver runbook |
| Agente pode acessar produção? | Não. Somente leitura de log em incidente |

**Sem política escrita, cada pessoa inventa a sua** — e a mais permissiva define
o risco de todo mundo.

---

## 3 · Onde alocar o esforço de engenharia

Se a IA torna a escrita barata, o investimento migra. Realocação sugerida:

| Área | Antes | Depois | Por quê |
|---|---|---|---|
| Velocidade da suíte | baixa prioridade | **alta** | Determina se o agente converge |
| Plataforma interna / DX | média | **alta** | É o que o DORA aponta como fonte de ROI |
| Portão automático | inexistente | **alta** | Onde a verificação escala |
| Observabilidade | média | **alta** | Volume de mudança maior exige detecção melhor |
| Escrever features | alta | média | Ficou barato |
| Documentação de API | média | baixa | Gerada e verificada automaticamente |

---

## 4 · A capacidade de revisão é o novo gargalo

Dado de 2026: PRs fundidos +98%, tempo de revisão +91%, ganho líquido ~10%.

### Cinco intervenções, em ordem de eficácia

**1. Limite duro de tamanho de PR, verificado no CI.**
A intervenção mais eficaz que conheço. Um limite de 400 linhas força o
fatiamento na origem, onde é barato.

**2. Revisão proporcional ao risco.**

| Risco | Política |
|---|---|
| Pagamento, autenticação, permissão, dado pessoal | 2 revisores humanos |
| Regra de negócio | 1 revisor humano |
| Infraestrutura, CI | 1 revisor humano |
| Teste, documentação, tradução | Portão + amostragem |
| Migração mecânica | Amostragem estratificada |

**3. Empurrar verificação para o portão.**
Cada item que o portão pega é atenção humana liberada.

**4. Revisão como atividade agendada, não interrupção.**
Duas janelas de 45 minutos por dia rendem mais que revisar entre uma coisa e
outra. Revisão exige atenção contínua e tem rendimento decrescente rápido.

**5. Medir e expor a fila.**
Painel simples: PRs abertos há mais de 24 h, 48 h, 72 h. O que não é visível não
é gerido.

---

## 5 · Conhecimento compartilhado — o risco silencioso

O risco menos discutido e, na minha opinião, o mais caro no médio prazo:

> **Quando o código é gerado, ninguém passa pelo processo de entendê-lo
> profundamente.**

Antes, escrever era a forma de aprender o sistema. Quem escreveu o módulo de
frete o conhecia. Agora o módulo existe e o conhecimento não.

Consequências, que aparecem em ordem:

1. Depuração fica mais lenta (ninguém tem o modelo mental).
2. Estimativas pioram (ninguém sabe a real complexidade).
3. Decisões de arquitetura ficam ruins (ninguém sabe o que já existe).
4. O time fica preso à ferramenta (só ela "entende" o sistema).

### Contramedidas

| Prática | Efeito |
|---|---|
| **Revisão como aprendizado**, não como portão | Quem revisa aprende. Alterne revisores de propósito |
| **Rodízio deliberado** de área | Impede ilhas de desconhecimento |
| **ADRs obrigatórios** para decisão contraintuitiva | O porquê fica registrado |
| **"Explique o sistema" na retrospectiva** | Se ninguém consegue, é alarme |
| **Sessões de leitura de código** | Prática esquecida, agora essencial |
| **Escrever à mão de propósito** | Uma tarefa por sprint, para manter o músculo |

O último item é contraintuitivo e eu o defendo com convicção. Julgamento é
músculo; músculo que não trabalha atrofia. Um time que nunca escreve código
perde, em um ano, a capacidade de avaliar código.

---

## 6 · Custo: governança

Ver [80-custos-e-licencas](80-custos-e-licencas.md) para preços. Aqui, o
processo.

| Prática | Por quê |
|---|---|
| Orçamento por time, não por pessoa | Evita microgerência e permite variação natural |
| Alerta em 80% do orçamento | Surpresa no fim do mês é o modo de falha comum |
| Custo por PR fundido | A métrica que liga gasto a valor |
| Revisar assinaturas trimestralmente | Metade das licenças de ferramenta costuma estar ociosa |
| Modelo adequado à tarefa | A alavanca de maior impacto no gasto |

**Ordem de grandeza para calibrar:** um time de 10 pessoas usando agentes
intensamente gasta tipicamente entre US$ 1.500 e US$ 4.000 por mês, somando
assinaturas e API. Isso é menos de 5% do custo do time — o que significa que
**otimizar custo de IA raramente é o problema certo**. O problema certo é
otimizar o tempo das pessoas.

---

## 7 · Formação interna

O que funciona, em ordem de eficácia observada:

1. **Programação em par com quem está em L4.** Nada substitui ver alguém
   trabalhar.
2. **Estudo de caso interno.** Um PR real que deu errado, dissecado em equipe.
   Vale mais que qualquer curso genérico.
3. **`AGENTS.md` como artefato compartilhado.** Escrever junto força a
   explicitar convenções que ninguém sabia que existiam.
4. **Rubrica de níveis** ([25](25-niveis-do-dev-com-ia.md)) usada em 1:1, não em
   avaliação de desempenho. Como mapa, não como nota.

O que **não** funciona: treinamento genérico de "como usar IA". A habilidade é
específica do repositório e do domínio.

---

## 8 · Quando dizer não

Uma equipe madura sabe recusar. Casos em que a resposta certa é **não usar
agente**:

| Situação | Por quê |
|---|---|
| Sistema regulado sem processo de validação definido | O risco de conformidade domina |
| Código sob NDA restrito, sem contrato com o fornecedor | Violação contratual |
| Base sem nenhum teste e sem tempo de criar | Sem rede, delegar é apostar |
| Transformação determinística | `sed` é melhor ([exemplo 4](06-exemplos.md)) |
| Equipe em crise, sem capacidade de revisão | Vai aumentar o estoque |
| Decisão de arquitetura estruturante | Precisa de dono humano |

> **Saber recusar é sinal de maturidade organizacional, não de atraso.** Uma
> equipe que usa IA em tudo tem tanto problema quanto uma que não usa em nada —
> só que os problemas dela aparecem mais tarde e são mais caros.

---

## Autoteste

1. Qual é o erro de adoção mais comum e por que ele falha?
2. Descreva a sequência de seis passos que funciona. Por que os passos 1–3 são
   engenharia comum?
3. Cite cinco perguntas que a política mínima escrita precisa responder.
4. Por que "sem política escrita, a pessoa mais permissiva define o risco"?
5. Cite três áreas que devem receber mais investimento e três menos.
6. Cite as cinco intervenções na capacidade de revisão, em ordem de eficácia.
7. Descreva o risco de conhecimento compartilhado e as quatro consequências em
   ordem.
8. Por que "escrever à mão de propósito" é defensável?
9. Por que otimizar custo de IA raramente é o problema certo?
10. Cite quatro situações em que a resposta certa é não usar agente.

---

**Anterior:** [26-carreira-e-mercado](26-carreira-e-mercado.md) ·
**Próximo:** [60-teoria-avancada](60-teoria-avancada.md)
