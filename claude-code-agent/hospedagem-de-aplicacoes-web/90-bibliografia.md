# 90 · Bibliografia comentada

`Nível: todos` · `Atualizado em 18/08/2026`

Livros com autor, título, editora e edição. Para cada um: **nível**, o que ele faz melhor que
os outros, e **se envelheceu**. O que é legalmente gratuito está marcado com **[GRÁTIS]**.

> **Nada aqui foi inventado.** Onde eu não tinha certeza da edição ou da existência de tradução,
> escrevi isso explicitamente em vez de arriscar.

---

## 1. Os essenciais (se você só ler três)

### **Designing Data-Intensive Applications**, 2ª edição
Martin Kleppmann e Chris Riccomini · O'Reilly · **março de 2026** · ~650 páginas
**Nível:** intermediário → avançado.
**Faz melhor:** explicar *por que* sistemas de dados são como são — replicação, particionamento,
transações, consenso — sem virar catálogo de produto. A 2ª edição atualiza o que mudou desde
2017 (a 1ª edição é de 2017 e ainda é excelente).
**Envelheceu?** A 1ª envelheceu em exemplos, não em conceitos. A 2ª é a versão a comprar hoje.
**Por que importa aqui:** é o livro que explica os capítulos [`60`](60-teoria-avancada.md) e
[`25`](25-catalogo-postgresql.md) em profundidade.

### **Site Reliability Engineering** · **[GRÁTIS]**
Betsy Beyer, Chris Jones, Jennifer Petoff, Niall Richard Murphy (orgs.) · O'Reilly · 2016
**Leitura gratuita e legal:** [sre.google/books](https://sre.google/books/)
**Nível:** intermediário → avançado.
**Faz melhor:** transformar confiabilidade em engenharia mensurável — SLO, orçamento de erro,
os quatro sinais de ouro, postmortem sem culpado.
**Envelheceu?** As partes sobre a infraestrutura interna do Google, sim. Os capítulos de SLO,
alerta, sobrecarga e cultura de incidente, **não** — continuam sendo o padrão do setor.
**Companheiro:** **The Site Reliability Workbook** (2018, também **[GRÁTIS]**), mais prático.

### **The Twelve-Factor App** · **[GRÁTIS]**
Adam Wiggins · 2011 · [12factor.net](https://12factor.net/) (há versão em português)
**Nível:** iniciante → intermediário. Uma hora de leitura.
**Faz melhor:** enunciar, em doze regras curtas, o que torna uma aplicação hospedável.
**Envelheceu?** Parcialmente: o fator sobre logs como fluxo e o vocabulário de "processo"
refletem a era pré-container. **Os fatores III (configuração), VI (sem estado) e IX
(descartabilidade) continuam sendo a diferença entre um sistema fácil e um difícil de hospedar.**

---

## 2. Operação, deploy e cultura

### **The Practice of Cloud System Administration**
Thomas Limoncelli, Strata Chalup, Christina Hogan · Addison-Wesley · 2014
**Nível:** intermediário. **Faz melhor:** operação de sistemas distribuídos com o pé no chão —
capacidade, escala, automação, plantão. **Envelheceu?** Em ferramentas, muito; em princípios,
quase nada. Vale pelos capítulos de projeto operacional.

### **Release It!**, 2ª edição
Michael T. Nygard · Pragmatic Bookshelf · 2018
**Nível:** intermediário. **Faz melhor:** os **padrões de estabilidade** — circuit breaker,
bulkhead, timeout, e os antipadrões que derrubam produção. Escrito a partir de cicatrizes
reais. **Envelheceu?** Não. É atemporal e provavelmente o livro mais útil desta lista para
quem já está em produção.

### **Continuous Delivery**
Jez Humble e David Farley · Addison-Wesley · 2010
**Nível:** intermediário. **Faz melhor:** o pipeline de implantação como conceito.
**Envelheceu?** As ferramentas, completamente. As ideias — build único, promoção entre
ambientes, implantação como não-evento — viraram consenso e continuam certas.

### **Accelerate**
Nicole Forsgren, Jez Humble, Gene Kim · IT Revolution · 2018
**Nível:** todos. **Faz melhor:** provar com dados que **frequência de deploy, tempo de
mudança, taxa de falha e tempo de restauração** predizem desempenho organizacional.
**Envelheceu?** Os dados são de 2014–2017; as métricas DORA seguem vivas e usadas.

### **The DevOps Handbook**, 2ª edição
Gene Kim, Jez Humble, Patrick Debois, John Willis · IT Revolution · 2021
**Nível:** todos. **Faz melhor:** a prática, com estudos de caso. **Envelheceu?** Não.

---

## 3. Containers e orquestração

### **Docker Deep Dive**
Nigel Poulton · autopublicado · edições anuais (a mais recente vale conferir na loja)
**Nível:** iniciante → intermediário. **Faz melhor:** explicar Docker sem enrolação e sem
mitos. **Envelheceu?** O autor reedita todo ano; compre a edição mais nova.

### **Kubernetes: Up and Running**, 3ª edição
Brendan Burns, Joe Beda, Kelsey Hightower, Lachlan Evenson · O'Reilly · 2022
**Nível:** intermediário. **Faz melhor:** introdução escrita por quem criou o Kubernetes.
**Envelheceu?** Parcialmente — o Kubernetes muda rápido. Confirme a edição mais recente.
**Aviso:** se você está montando uma aplicação e um banco, **você não precisa deste livro**.
Veja o mito 2 em [`75-armadilhas.md`](75-armadilhas.md).

### **Designing Distributed Systems**
Brendan Burns · O'Reilly · 2018 (houve distribuição gratuita patrocinada pela Microsoft;
confirme a disponibilidade atual)
**Nível:** intermediário. **Faz melhor:** padrões de container (sidecar, ambassador, adapter)
como vocabulário reutilizável.

---

## 4. Banco de dados

### **PostgreSQL — documentação oficial** · **[GRÁTIS]**
PostgreSQL Global Development Group · [postgresql.org/docs](https://www.postgresql.org/docs/)
**Nível:** todos. **Faz melhor:** ser, ao mesmo tempo, referência e livro-texto. Poucos
projetos têm documentação tão boa. **Envelheceu?** Nunca — acompanha a versão.

### **SQL Performance Explained**
Markus Winand · autopublicado · 2012 · **versão web gratuita e completa** em
[use-the-index-luke.com](https://use-the-index-luke.com/) · **[GRÁTIS parcialmente]**
**Nível:** intermediário. **Faz melhor:** ensinar índices de um jeito que gruda.
**Envelheceu?** Não. Índice B-tree funciona igual desde 1972.

### **Database Reliability Engineering**
Laine Campbell e Charity Majors · O'Reilly · 2017
**Nível:** intermediário → avançado. **Faz melhor:** tratar banco de dados como problema de
operação e confiabilidade, não de administração. **Envelheceu?** Pouco.

### Sobre Redis
**Não recomendo nenhum livro.** *Redis in Action* (Josiah Carlson, Manning, 2013) é bom e
está datado — a maior parte do que mudou (Streams, ACL, cluster moderno, a divisão
Redis/Valkey) veio depois. **Prefira a documentação oficial do Redis e do Valkey**, que são
gratuitas, atuais e curtas.

---

## 5. Fundamentos que sustentam tudo

### **Systems Performance**, 2ª edição
Brendan Gregg · Addison-Wesley · 2020
**Nível:** avançado. **Faz melhor:** metodologia de análise de desempenho (USE, latência) que
funciona em qualquer camada. **Envelheceu?** Não. É a referência.

### **Distributed Systems**, 4ª edição · **[GRÁTIS]**
Andrew S. Tanenbaum e Maarten van Steen · autopublicado · 2023 ·
PDF gratuito em [distributed-systems.net](https://www.distributed-systems.net/)
**Nível:** avançado. **Faz melhor:** rigor acadêmico sobre consistência, replicação e consenso.

### **The Linux Command Line**, 2ª edição · **[GRÁTIS]**
William Shotts · No Starch Press · 2019 · PDF gratuito em
[linuxcommand.org](https://linuxcommand.org/tlcl.php)
**Nível:** iniciante. **Faz melhor:** ser o melhor primeiro livro de terminal que existe.

### **How Linux Works**, 3ª edição
Brian Ward · No Starch Press · 2021
**Nível:** intermediário. **Faz melhor:** explicar o que acontece entre ligar a máquina e ter
um processo rodando. Base direta para entender containers.

### **Computer Networking: A Top-Down Approach**
James Kurose e Keith Ross · Pearson · edições sucessivas (a 8ª é de 2020)
**Nível:** iniciante → intermediário. **Faz melhor:** redes de cima para baixo, começando pela
aplicação. **Há tradução brasileira** ("Redes de Computadores e a Internet", Pearson) —
confirme a edição.

---

## 6. Economia da nuvem

### **Cloud FinOps**, 2ª edição
J. R. Storment e Mike Fuller · O'Reilly · 2023
**Nível:** intermediário. **Faz melhor:** tratar custo de nuvem como disciplina de engenharia,
com processo e responsabilidade. **Envelheceu?** Os números, sim; o método, não.
**Aviso:** é escrito para empresas grandes. Para um projeto pequeno, o bloco D deste curso
cobre o necessário.

### **Web Scalability for Startup Engineers**
Artur Ejsmont · McGraw-Hill · 2015
**Nível:** intermediário. **Faz melhor:** escalar sistemas web com foco em custo e simplicidade.
**Envelheceu?** As tecnologias, sim; os princípios de cache, fila e stateless, não.

---

## 7. Leitura curta que vale mais que muitos livros

| Texto | Autor | Onde | Por quê |
|---|---|---|---|
| *The Tail at Scale* | Jeff Dean, Luiz André Barroso | ACM, 2013 | por que o p99 é o número que importa |
| *Brewer's Conjecture…* (prova do CAP) | Gilbert, Lynch | SIGACT News, 2002 | o teorema, de verdade |
| *Consistency Tradeoffs in Modern Distributed Database System Design* | Daniel Abadi | IEEE Computer, 2012 | PACELC, mais útil que CAP |
| *Firecracker: Lightweight Virtualization for Serverless Applications* | Agache et al. | NSDI, 2020 | como microVMs funcionam |
| *How to do distributed locking* | Martin Kleppmann | martin.kleppmann.com, 2016 | o debate sobre Redlock, dos dois lados |
| *Optimal Probabilistic Cache Stampede Prevention* | Vattani et al. | VLDB, 2015 | a matemática da estampida |
| *Latency Numbers Every Programmer Should Know* | Jeff Dean / Peter Norvig | web | a tabela do capítulo [`10`](10-fundamentos.md), seção 7 |

---

## 8. Sobre edições em português

Existem traduções brasileiras de vários destes títulos (Novatec, Alta Books, Bookman, Pearson).
**Não listo edição e ano de tradução aqui porque não os confirmei em 18/08/2026, e citar
edição errada é pior que não citar.** Duas observações honestas:

- A **qualidade da tradução técnica brasileira é irregular**. Em livros muito técnicos, o
  original em inglês costuma ser mais claro — e mais barato, em versão digital.
- Quando existir versão gratuita legal em inglês (SRE Book, Twelve-Factor, TLCL,
  Tanenbaum, use-the-index-luke), **prefira-a**: é atual, gratuita e revisada.

---

## 9. A ordem que eu recomendaria

```
1º  The Twelve-Factor App                    (1 hora, grátis)
2º  ESTE MATERIAL, blocos A e B              (grátis)
3º  The Linux Command Line                   (se faltar base, grátis)
4º  Docker Deep Dive                         (edição mais recente)
5º  Release It!                              (o mais útil quando já se está em produção)
6º  Site Reliability Engineering, caps. de SLO, alerta e postmortem   (grátis)
7º  Designing Data-Intensive Applications, 2ª ed.
8º  Systems Performance                      (quando quiser ir fundo)
```

---

## Autoteste

1. Quais três livros/textos deste capítulo são gratuitos e legais, e por que a gratuidade não os torna piores?
2. O que envelheceu no Twelve-Factor App, e o que continua valendo?
3. Por que não há recomendação de livro sobre Redis?
4. Qual livro é o mais útil para quem **já está** em produção, e por quê?
5. Que ressalva este capítulo faz sobre traduções brasileiras?
6. Cite dois artigos curtos que valem mais que muitos livros e diga o que cada um resolve.
