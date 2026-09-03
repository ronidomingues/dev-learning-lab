# 23 · Licença, propriedade e lei

**Nível:** intermediário · **Escrito em:** 20/08/2026

> **Isto não é aconselhamento jurídico.** É um mapa do terreno, escrito por
> engenheiro, para você saber **quais perguntas levar ao advogado** e quais
> decisões técnicas tomar enquanto a poeira não assenta. O direito nesta área
> está em movimento e varia por jurisdição.

---

## 1 · As quatro perguntas distintas

Muita confusão vem de tratar como uma só coisa o que são quatro:

| # | Pergunta | Quem responde |
|---|---|---|
| 1 | O treinamento em código alheio foi lícito? | Tribunais, e varia por país |
| 2 | Quem é dono do código que saiu? | Lei de direito autoral |
| 3 | O código gerado pode reproduzir trecho licenciado? | Fato técnico + risco |
| 4 | Quem responde se der problema? | Contrato e responsabilidade civil |

---

## 2 · Quem é dono da saída

### Estados Unidos

O Copyright Office e os tribunais têm sustentado, de forma consistente, que
**obra gerada sem autoria humana não é protegível por direito autoral**. A
consequência prática: código puramente gerado, sem intervenção humana
significativa, pode cair em domínio público nos EUA.

Isso importa para quem constrói produto: **você pode não conseguir impedir que
um concorrente copie a parte que a máquina escreveu.**

Contribuição humana significativa (seleção, edição, arranjo, estrutura) restaura
proteção sobre essa contribuição.

### Brasil

A Lei 9.610/98 protege "criações do espírito", e a doutrina majoritária exige
**autoria humana**. Não há, até 20/08/2026, decisão consolidada específica sobre
código gerado por IA no país. Discussões legislativas sobre regulação de IA
seguiam em curso; qualquer afirmação categórica aqui envelheceria mal.

**Postura prudente:** trate código gerado como **não protegido por conta
própria** e garanta contribuição humana documentada no que for
estrategicamente seu.

### União Europeia

O AI Act traz obrigações de transparência para fornecedores de modelos
(incluindo sobre dados de treino). Ele regula **quem fornece o modelo**, não
resolve a titularidade da saída, que segue as leis nacionais de direito autoral.

---

## 3 · Contaminação por licença

### O risco

Modelos treinados em código aberto podem, ocasionalmente, reproduzir trechos
substanciais de código licenciado. Se esse trecho vem de código GPL e entra no
seu produto proprietário, você tem um problema de licença — independentemente de
ter sido intencional.

Vale calibrar: reprodução literal e longa é **rara** nos modelos atuais; trechos
curtos e idiomáticos não são protegíveis de qualquer forma (não há originalidade
numa função de duas linhas que só existe de um jeito). O risco se concentra em
**blocos longos e distintivos**.

### Mitigações

| Mitigação | Como |
|---|---|
| **Filtro do fornecedor** | Copilot tem o *duplication detection filter*, que suprime sugestões que casam com código público. Ligue-o |
| **Varredura de origem** | Scanners de composição de software (Black Duck, FOSSA, ScanCode) detectam trechos com origem conhecida |
| **Política de blocos longos** | Bloco gerado com mais de N linhas em código proprietário: verificar antes |
| **Busca manual** | Trecho suspeito e distintivo: procure entre aspas no GitHub |

### Indenização dos fornecedores

Vários fornecedores oferecem indenização contratual contra reivindicações de
direito autoral pela saída — geralmente **condicionada** a você ter os filtros
ligados e ao uso conforme os termos.

**Leia as condições.** A indenização típica não cobre: uso com filtro desligado,
violação dos termos de uso, ou reivindicações que não sejam de direito autoral
(patente, segredo comercial). E cobre o **fornecedor** defendendo você, não
necessariamente o custo total do incidente.

---

## 4 · O que o seu contrato provavelmente diz

Leia antes de colar código do seu empregador ou cliente em qualquer serviço.

| Cláusula típica | Implicação |
|---|---|
| Confidencialidade | Enviar código do cliente a um serviço de terceiro pode violar, mesmo que o serviço prometa não treinar |
| Titularidade da obra | Se a saída não é protegível, a cláusula "todo trabalho pertence à empresa" pode não alcançá-la |
| Conformidade (SOC 2, ISO 27001, LGPD) | Exige controle sobre onde o dado trafega |
| Restrição de subcontratação | Um serviço de IA pode ser interpretado como subprocessador |

**Pergunta que resolve 80% dos casos:** *o meu contrato ou a política da empresa
permite enviar este código para este serviço específico?*

Se não houver política, **peça uma**. E, enquanto não houver, use as versões
empresariais com garantia de não-treinamento e retenção zero, ou modelo
autohospedado.

---

## 5 · LGPD e dado pessoal

Se o código, os testes ou os logs que você manda ao agente contêm **dado
pessoal**, você está tratando dado pessoal e a LGPD se aplica.

| Situação | Risco |
|---|---|
| *Fixture* de teste com CPF real | Tratamento sem base legal |
| Log de produção colado no chat para depurar | Transferência internacional sem salvaguarda |
| Dump de banco no contexto | Idem, em escala |
| Captura de tela com dado de cliente | Idem |

**Regras práticas:**

1. Dado de teste é **sintético**. Sempre. Não é preciosismo — é o único jeito de
   não pensar nisso a cada tarefa.
2. Anonimize log antes de colar. Ou peça ao agente para escrever o script que
   anonimiza, e rode você.
3. Verifique se o fornecedor oferece **residência de dados** e o que ele retém.
4. Se você é o controlador, o fornecedor pode ser **operador** — e isso exige
   contrato específico.

> Um agente que roda com acesso ao banco de produção resolve o problema de
> depuração e cria um problema de conformidade muito maior. Não faça.

---

## 6 · Atribuição: a política que eu recomendo

Não existe obrigação legal geral de declarar uso de IA em código privado. Mas
há três razões práticas fortes para registrar:

1. **Investigação.** Saber a origem muda onde você procura o bug.
2. **Métrica honesta.** Sem registro, você não sabe o que está acontecendo na
   sua base.
3. **Confiança.** Descobrir depois que metade do sistema foi gerada e ninguém
   avisou é como o time perde confiança em quem entregou.

Formato sugerido (do [20-git-e-fluxo-de-trabalho](20-git-e-fluxo-de-trabalho.md)):

```
Assisted-by: claude-code/2.1.237
Review-level: full | sampled | gate-only
```

### Em código aberto

Cada projeto tem sua política. Alguns exigem declaração; alguns proíbem
contribuição gerada; a maioria não tem regra. **Leia o `CONTRIBUTING.md` antes
de abrir PR.** Mandar PR gerado sem revisão para um projeto mantido por
voluntários é transferir o seu trabalho para eles — e virou um problema real de
comunidade em 2025–2026.

---

## 7 · Responsabilidade — a parte sem ambiguidade

Aqui não há discussão jurídica em aberto:

> **Você é responsável pelo código que você integra.** "O agente escreveu" não é
> defesa em lugar nenhum — nem contratual, nem regulatório, nem perante o
> cliente, nem na retrospectiva da equipe.

Consequências práticas:

- Você precisa **entender** o suficiente para responder por aquilo.
- Você precisa **conseguir consertar** quando quebrar.
- Você precisa **saber explicar** por que está daquele jeito.

Se as três não valem para algum trecho que você aprovou, você não aprovou — você
apostou.

---

## Autoteste

1. Quais são as quatro perguntas distintas que costumam ser confundidas?
2. Nos EUA, código puramente gerado é protegível? Qual é a consequência prática?
3. Qual é a postura prudente no Brasil, dado o estado do direito em 08/2026?
4. Em que tipo de trecho se concentra o risco real de contaminação por licença?
5. Cite três mitigações contra contaminação.
6. O que a indenização típica dos fornecedores **não** cobre?
7. Qual é a pergunta que resolve 80% dos casos contratuais?
8. Por que dado de teste deve ser sintético, e por que isso é economia de esforço?
9. Cite as três razões práticas para registrar atribuição.
10. Enuncie a regra de responsabilidade e as três consequências práticas dela.

---

**Anterior:** [22-seguranca](22-seguranca.md) ·
**Próximo:** [24-produtividade-o-que-diz-a-evidencia](24-produtividade-o-que-diz-a-evidencia.md)
