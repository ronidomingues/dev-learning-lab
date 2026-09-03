# 2 · Pré-requisitos — o que saber e ter antes de começar

**Nível:** iniciante · **Escrito em:** 19/08/2026

---

## Resumo em 30 segundos

Para **usar** bem um modelo: saber ler e escrever com precisão. Só isso.
Para **ser contratado** como engenheiro de prompt em 2026: Python básico,
JSON, git, noção de API, e — o item que quase ninguém tem — saber montar e
interpretar uma avaliação. O resto se aprende no caminho.

---

## Conhecimento

### Indispensável

| Requisito | Por que | Onde aprender |
|---|---|---|
| **Escrever com precisão em português** | prompt é especificação; ambiguidade sua vira erro do modelo. Se você não consegue explicar a tarefa a um humano por escrito, não vai conseguir explicar a um modelo | prática deliberada: escreva a instrução, dê a um colega sem contexto, veja o que ele entendeu errado |
| **Ler inglês técnico** | ~95% da documentação, dos papers e das mudanças de API sai primeiro em inglês, e as traduções chegam meses depois — quando chegam | leia a documentação oficial com tradutor ao lado no começo; em 3 meses você larga o tradutor |
| **Usar o terminal** (cd, ls, editar arquivo, variável de ambiente) | tudo que é profissional roda em linha de comando | [variaveis-de-ambiente-e-segredos](../variaveis-de-ambiente-e-segredos/00-MAPA.md) desta pasta |
| **Pensar em casos de teste** | "o que poderia dar errado aqui?" é a pergunta central do ofício | [testes-automatizados](../testes-automatizados/00-MAPA.md) desta pasta |

### Ajuda muito (e vira indispensável no nível 3)

| Requisito | Por que | Onde aprender |
|---|---|---|
| **Python básico** — variáveis, `if`, `for`, funções, listas, dicionários | é a língua franca da área; toda biblioteca relevante é Python primeiro | [Curso em Vídeo — Python](https://www.youtube.com/playlist?list=PLHz_AreHm4dlKP6QQCekuIPky1CiwmdI6) (gratuito, PT) |
| **JSON** | é o formato em que 90% da saída estruturada trafega | 20 minutos lendo [json.org](https://www.json.org/json-pt.html) |
| **Noção de API HTTP** — requisição, resposta, cabeçalho, chave de autenticação, código de status | você vai chamar a API do modelo o dia inteiro | [apis](../apis/00-MAPA.md) desta pasta |
| **git** | prompt é código: precisa de histórico, revisão e reversão | [commits-assinados](../commits-assinados/00-MAPA.md) desta pasta tem a base de git |
| **Estatística de ensino médio** — porcentagem, média, amostra, intervalo | para não dizer "melhorou 3%" quando a diferença cabe no ruído de 20 casos | [10-fundamentos](10-fundamentos.md) §amostragem e [60-teoria-avancada](60-teoria-avancada.md) |
| **Noção do que é um agente de IA** | prompt hoje quase sempre vive dentro de um agente | [agentes-de-ia](../agentes-de-ia/00-MAPA.md) desta pasta |

### Explicitamente **não** é pré-requisito

- **Saber treinar redes neurais.** Você não vai treinar nada. Vai usar modelos
  prontos. Entender *por dentro* ajuda (e está no [10](10-fundamentos.md) e no
  [60](60-teoria-avancada.md)), mas nessa ordem: usar → medir → entender.
- **Álgebra linear e cálculo.** Só se você for para pesquisa.
- **Diploma em computação.** O mercado desta função contrata por portfólio.
  Ver [40-a-profissao](40-a-profissao.md).
- **Pagar um curso.** Ver [85-cursos-e-certificacoes](85-cursos-e-certificacoes.md):
  o material gratuito oficial é melhor que a maioria do material pago.

---

## Ambiente

| Item | Mínimo | Recomendado | Observação |
|---|---|---|---|
| Sistema operacional | qualquer um com navegador | Linux ou macOS; no Windows, **WSL2** | ver [03-instalacao](03-instalacao.md) |
| RAM | 4 GB | 8 GB+ | o modelo roda no servidor do fornecedor, não no seu PC — a menos que você use modelo local (§ abaixo) |
| Disco | 2 GB | 10 GB | Python + bibliotecas + Node |
| Internet | estável | — | tudo é chamada de rede |
| Python | 3.10 | **3.12 ou 3.13** | 3.14.7 é a mais nova (05/08/2026), mas algumas bibliotecas ainda não a suportam |
| Node.js | 22.22 | **24 LTS (Krypton)** | só para ferramentas de avaliação como o promptfoo |
| Conta em provedor de IA | 1 | 2 (para comparar) | ver [80-custos-e-licencas](80-custos-e-licencas.md) |
| Cartão de crédito | **não obrigatório para começar** | — | há camada gratuita real; a API paga exige crédito pré-pago |

### E se eu quiser rodar modelo na minha máquina?

Aí muda tudo: um modelo aberto de 8 bilhões de parâmetros quantizado pede
~6 GB de RAM e roda devagar em CPU; 30 GB de VRAM para os modelos grandes.
Isto **não é necessário** para aprender engenharia de prompt e você não deve
começar por aí. Mas é útil no nível 4, para iterar sem pagar por chamada.
Ferramenta: `ollama`. Ver [03-instalacao §modelo local](03-instalacao.md#9--opcional-modelo-local-com-ollama).

---

## Tempo realista até cada nível

Números honestos, supondo **estudo consistente, com as mãos**, e contando
apenas quem já tem os pré-requisitos indispensáveis. Se você mentir para si
mesmo aqui, vai se frustrar no mês 2.

| Nível | O que você consegue fazer | Dedicação | Tempo |
|---|---|---|---|
| **0 · Usuário competente** | tirar de um chatbot resultado muito acima da média; saber por que uma resposta veio ruim | 5 h/semana | **2 a 3 semanas** |
| **1 · Prompt em produção** | escrever prompt com papel, formato, regras e exemplos; extrair e validar JSON; chamar a API por código | 8 h/semana | **1 a 2 meses** |
| **2 · Engenheiro de verdade** | montar conjunto rotulado, arnês de avaliação, portão de CI, controle de custo e latência, defesa contra injeção | 10 h/semana | **4 a 6 meses** |
| **3 · Sênior / empregável em vaga boa** | projetar sistemas multi-etapa, RAG, ferramentas/agentes, otimização automática de prompt, decidir modelo por dados | 10 h/semana | **9 a 18 meses** |
| **4 · Fronteira** | contribuir com método novo, ler e reproduzir paper, otimizar prompt como problema de busca | — | **2 anos+** |

**Onde as pessoas travam:** entre o nível 1 e o 2. O salto exige montar
conjunto de teste à mão — trabalho tedioso, sem dopamina, que ninguém posta no
LinkedIn. É exatamente por isso que ele é o diferencial de mercado.

**Opinião profissional, não consenso:** quem chega ao nível 2 em 6 meses e
sabe programar razoavelmente é mais empregável, hoje, do que quem passou 2 anos
colecionando técnicas de prompt sem nunca medir nada.

---

## Rota de resgate — se você não tem um pré-requisito

| Falta | O que fazer |
|---|---|
| **Não sei programar nada** | Não pare o curso. Faça os arquivos [01](01-introducao-leigo.md), [04](04-como-comecar.md), [05](05-manual-de-uso.md), [06](06-exemplos.md) e [75](75-armadilhas.md) inteiros só pela interface web — você chega ao nível 0/1. Em paralelo, 6 semanas de Python básico. Depois volte ao [07-projeto-modelo](07-projeto-modelo/README.md). |
| **Não sei inglês** | Comece com o material em português do [85](85-cursos-e-certificacoes.md) e leia a documentação oficial com tradutor automático. Aviso honesto: você vai receber a informação com 3 a 12 meses de atraso e vai perder a nuance dos termos. Trate o inglês como investimento obrigatório de médio prazo. |
| **Não tenho cartão de crédito / não posso pagar API** | Perfeitamente viável. Camada gratuita de chatbots + [Google AI Studio](https://aistudio.google.com/) (gratuito, com limites) + o provedor **simulado** do [projeto-modelo](07-projeto-modelo/README.md), que roda offline. Detalhes em [80-custos-e-licencas](80-custos-e-licencas.md). |
| **Meu computador é fraco** | Irrelevante para 95% do curso: o processamento é do fornecedor. Se nem Python instalar der, use [Google Colab](https://colab.research.google.com/) — roda no navegador, de graça. |
| **Não tenho tempo** | 30 minutos/dia dá o nível 0 em um mês. Faça na ordem: [01](01-introducao-leigo.md) → [04](04-como-comecar.md) → [06](06-exemplos.md) → [75](75-armadilhas.md). |
| **Não sei se quero a carreira** | Leia [40-a-profissao](40-a-profissao.md) **antes** de investir seis meses. Ele é deliberadamente desconfortável. |

---

## Autoteste

1. Qual é o único pré-requisito realmente inegociável para o nível 0, e por quê?
2. Por que estatística básica aparece na lista de uma função "de escrever texto"?
3. Você tem 10 h/semana e quer estar empregável. Qual é a expectativa honesta
   de prazo, e qual é o degrau em que a maioria desiste?
4. Rodar modelo local é pré-requisito? Quando passa a fazer sentido?
5. Você não sabe programar. Qual é a sequência de arquivos deste curso que
   ainda assim faz sentido, e até onde ela te leva?
6. Por que o curso afirma que treinar redes neurais **não** é pré-requisito —
   e em que ponto entender o interior do modelo passa a ser útil?
