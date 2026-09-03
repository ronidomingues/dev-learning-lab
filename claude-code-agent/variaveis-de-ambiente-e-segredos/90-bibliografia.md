# 90 · Bibliografia comentada

`Nível: todos` · **Edições verificadas em 18/08/2026**

> ⚠️ **Não existe livro sobre "variáveis de ambiente e segredos".** É um assunto
> transversal, tratado como capítulo dentro de livros de segurança, DevOps e
> arquitetura. Esta lista aponta **o capítulo certo dentro do livro certo**.
>
> **Nenhum ISBN é citado aqui.** A regra desta pasta é nunca inventar número —
> confirme edição e ISBN na editora antes de comprar.

---

## 1. Comece por aqui (e é de graça)

### **The Twelve-Factor App** — Adam Wiggins, 2011

- 📖 [12factor.net/pt_br](https://12factor.net/pt_br/) · **gratuito** · **em português**
- **Leia o Fator III (Configurações).** São 10 minutos.
- **Por que ler:** é o documento fundador do assunto. Tudo o que este curso discute
  parte daqui, inclusive as críticas.
- **Envelheceu?** Em parte — ver [11-historia.md §3](11-historia.md). Os princípios
  valem; algumas implementações ficaram datadas.

### **OWASP Secrets Management Cheat Sheet**

- 📖 [cheatsheetseries.owasp.org](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_CheatSheet.html)
  · **gratuito** · atualizado continuamente
- **Por que ler:** denso, prático, sem marketing. É a referência que a indústria usa.
- **Nível:** intermediário. Leia depois deste curso, não antes.

### **Security Engineering** — Ross Anderson, 3ª edição, Wiley, 2020

- 📖 **Gratuito e legal:** todos os capítulos em
  [cl.cam.ac.uk/archive/rja14/book.html](https://www.cl.cam.ac.uk/archive/rja14/book.html)
  — o autor negociou com a editora a liberação integral, confirmada em novembro de 2024.
- **Nível:** intermediário a avançado. ~1.200 páginas.
- **O que faz melhor que os outros:** ensina a **pensar em modelo de ameaça**, não a
  aplicar receitas. Nenhum livro chega perto nisso.
- **Capítulos relevantes aqui:** 4 (protocolos), 5 (criptografia), 6 (controle de
  acesso), 21 (economia da segurança).
- **Envelheceu?** Não. É o livro mais citado da área, e a 3ª edição é recente.
- **Nota:** Ross Anderson faleceu em março de 2024. Não haverá 4ª edição dele.

---

## 2. Criptografia

### **Serious Cryptography** — Jean-Philippe Aumasson, 2ª edição, No Starch Press, 2024

- **Nível:** intermediário. ~400 páginas.
- **O que faz melhor:** explica AES-GCM, AEAD, derivação de chave e os erros reais de
  implementação **sem** exigir matemática pesada, e **sem** simplificar ao ponto de
  enganar. É o equilíbrio mais difícil de achar nesta área, e ele acerta.
- **Leia para:** entender de verdade o [60-teoria-avancada.md §1](60-teoria-avancada.md).
- **Envelheceu?** Não — a 2ª edição é de outubro de 2024 e inclui criptografia
  pós-quântica.
- **Tradução em português:** não conheço uma da 2ª edição. Se encontrar, confirme se
  é da edição atual.

### **Applied Cryptography** — Bruce Schneier, edição de 20 anos, Wiley, 2015

- **Nível:** avançado. Clássico histórico.
- **Aviso honesto:** o próprio Schneier diz que o livro fez as pessoas acharem que
  criptografia resolve problemas de segurança, o que é falso. **Leia como história**,
  não como manual. Para prática, use o Aumasson.

---

## 3. DevOps, entrega e operação

### **The DevOps Handbook** — Gene Kim, Jez Humble, Patrick Debois, John Willis, 2ª edição, IT Revolution, 2021

- **Nível:** iniciante a intermediário.
- **Relevante aqui:** as partes sobre segurança na esteira de entrega e sobre
  "shift left" — colocar a verificação de segredo no pre-commit, não na auditoria anual.
- **Tradução em português:** existe ("Manual de DevOps", Alta Books). Verifique se é
  da 2ª edição.

### **Continuous Delivery** — Jez Humble e David Farley, Addison-Wesley, 2010

- **Nível:** intermediário. **Clássico que continua valendo.**
- **Relevante:** o princípio de "construa o binário uma vez, promova entre ambientes"
  é o motivo pelo qual configuração precisa vir de fora — e é o argumento contra o
  build-time replacement do front-end ([20](20-frontend-e-build-time.md)).
- **Envelheceu?** As ferramentas sim; os princípios não.

### **Site Reliability Engineering** — Betsy Beyer et al., O'Reilly, 2016

- 📖 **Gratuito e legal:** [sre.google/books](https://sre.google/books/)
- **Relevante:** os capítulos sobre gestão de configuração e sobre resposta a
  incidente. O capítulo de *postmortem culture* é a base do que
  [50 §4](50-vazamentos-e-resposta.md) recomenda.

### **Release It!** — Michael Nygard, 2ª edição, Pragmatic Bookshelf, 2018

- **Nível:** intermediário.
- **Relevante:** o padrão *fail fast* aplicado à configuração — a justificativa
  conceitual do módulo de configuração do [projeto-modelo](07-projeto-modelo/README.md).
- **Um dos livros mais subestimados de engenharia de software.**

---

## 4. Contêineres e Kubernetes

### **Container Security** — Liz Rice, O'Reilly, 2020

- **Nível:** intermediário a avançado.
- **O que faz melhor:** explica namespaces, cgroups e capabilities **de verdade**,
  com código. Depois disso, "por que o grupo `docker` é equivalente a root" deixa de
  ser dogma e passa a ser óbvio.
- **Relevante:** capítulos sobre passagem de segredos a contêineres e sobre camadas
  de imagem.
- **Envelheceu?** Parcialmente — o Docker mudou desde 2020. Os fundamentos, não.

### **Kubernetes: Up and Running** — Kelsey Hightower, Brendan Burns, Joe Beda, 3ª edição, O'Reilly, 2022

- **Nível:** iniciante a intermediário.
- **Relevante:** capítulos de ConfigMaps e Secrets.
- **Atenção:** a 3ª edição é de 2022 e **não** cobre KMS v2 nem o estado atual do
  External Secrets Operator. Complemente com a documentação oficial.
- **Tradução em português:** a Novatec publica traduções de O'Reilly; verifique a edição.

---

## 5. Arquitetura

### **Building Microservices** — Sam Newman, 2ª edição, O'Reilly, 2021

- **Relevante:** o capítulo sobre configuração e o sobre segurança tratam
  diretamente de "onde mora o segredo quando há 40 serviços".

### **Microservices Patterns** — Chris Richardson, Manning, 2018

- **Relevante:** o padrão *Externalized Configuration*, com as variantes
  *push* (variável de ambiente) e *pull* (a aplicação busca do cofre) — exatamente a
  distinção de [40 §7](40-cofres-de-segredos.md).

### **Zero Trust Networks** — Evan Gilman e Doug Barth, O'Reilly (2ª edição, 2024)

- **Nível:** avançado.
- **Relevante:** é a fundamentação teórica do que [60 §5](60-teoria-avancada.md)
  chama de identidade de carga de trabalho. Leia se SPIFFE/SPIRE lhe interessou.

---

## 6. Modelagem de ameaça

### **Threat Modeling: Designing for Security** — Adam Shostack, Wiley, 2014

- **Nível:** intermediário.
- **Por que ler:** dá método para responder "contra quem estou me defendendo?" —
  a pergunta que ordena todas as decisões de [60 §2](60-teoria-avancada.md).
- **Envelheceu?** Os exemplos sim; o método não.

### **Agile Application Security** — Laura Bell, Michael Brunton-Spall, Rich Smith, Jim Bird, O'Reilly, 2017

- **Relevante:** capítulo sobre gestão de segredos em times ágeis; trata do lado
  **organizacional**, que é onde a maioria dos programas falha.

---

## 7. Em português

Sendo honesto: **o material de qualidade neste assunto é majoritariamente em inglês.**
O que existe em português:

| Obra | Situação |
|---|---|
| **The Twelve-Factor App** | ✅ traduzido, gratuito, bom — [12factor.net/pt_br](https://12factor.net/pt_br/) |
| Documentação do Kubernetes | ✅ tradução ativa em kubernetes.io/pt-br |
| **Cartilha de Segurança** (CERT.br) | ✅ gratuita, fundamentos gerais — [cartilha.cert.br](https://cartilha.cert.br/) |
| Traduções da Novatec/Alta Books (O'Reilly, IT Revolution) | 🟡 existem; **confirme a edição** antes de comprar — traduções costumam ficar uma edição atrás |
| Livro nacional dedicado ao assunto | ❌ não conheço nenhum |

**Sobre qualidade de tradução, minha opinião:** as traduções técnicas da Novatec são
geralmente boas. O risco maior não é a tradução, é o **atraso de edição** — comprar a
tradução de uma 1ª edição quando a 3ª já saiu, num assunto que muda rápido, é pior que
ler o original em inglês.

---

## 8. Ordem de leitura sugerida

```
1. Twelve-Factor, Fator III                        10 min   grátis · PT
2. OWASP Secrets Management Cheat Sheet             1 h     grátis
3. Security Engineering, caps. 4–6 (Anderson)       6 h     grátis
4. Release It!, capítulo de fail fast               2 h
5. Container Security (Rice)                       10 h
6. Serious Cryptography (Aumasson)                 15 h
7. Zero Trust Networks                             12 h
```

Os três primeiros são gratuitos e cobrem 80% do que você precisa.

---

## Autoteste

1. Por que não existe um livro dedicado a este assunto?
2. Qual livro está legalmente disponível de graça, e por qual acordo?
3. Por que ler *Applied Cryptography* como história e não como manual?
4. Que princípio de *Continuous Delivery* fundamenta a crítica ao build-time replacement?
5. O que *Container Security* explica que torna óbvio o risco do grupo `docker`?
6. Qual é o risco de comprar uma tradução em português neste assunto?
7. Que padrão de *Microservices Patterns* corresponde à distinção push/pull de segredos?

---

**Edições verificadas em 18/08/2026** em: cl.cam.ac.uk/archive/rja14/book.html ·
lightbluetouchpaper.org (anúncio da liberação da 3ª edição, nov/2024) ·
nostarch.com/serious-cryptography-2nd-edition · sre.google/books ·
12factor.net/pt_br · cheatsheetseries.owasp.org.
**Nenhum ISBN foi citado, por política desta pasta. Confirme edição na editora.**

**Próximo:** [95-referencias.md](95-referencias.md) · Voltar ao [mapa](00-MAPA.md)
