# Curso Básico de Automações com n8n
**Aula 1: Introdução ao n8n e Agentes de IA**
*Instrutor: Hashtag No Code & IA*

---

## 📌 Visão Geral da Aula
Nesta primeira aula do **Curso Básico de Automações com n8n**, você aprenderá os conceitos fundamentais sobre o que é o **n8n**, como ele funciona e por que ele está revolucionando a produtividade no mercado de trabalho. Compreenda a diferença entre automações condicionais tradicionais e **Agentes de Inteligência Artificial**, além de visualizar casos práticos aplicados a negócios.

---

## 🚀 1. O que é o n8n?

O **n8n** é uma plataforma visual de automação de fluxos de trabalho (no-code / low-code) que permite conectar diferentes aplicativos, bancos de dados, planilhas e APIs de forma simples — arrastando e configurando "caixinhas" (nós/nodes) sem a necessidade de programar.

### Principais Características:
* **Visual e Intuitivo:** Construção de fluxos através de blocos conectáveis.
* **Mais de 500 Integrações Nativas:** Conecta-se com WhatsApp, Gmail, Slack, Google Sheets, Trello, Google Drive, bancos de dados e muito mais.
* **Suporte aos Principais Modelos de IA:** Conectividade com modelos de ponta como OpenAI (ChatGPT), Google Gemini e Anthropic (Claude).
* **Gratuito para Aprendizado:** Pode ser utilizado sem custos durante todo o processo de estudos e desenvolvimento inicial.

---

## 💡 2. Automação Tradicional vs. Agentes de IA

Apesar de ambos automatizarem processos e rodarem 24 horas por dia sem intervenção humana, existem diferenças fundamentais quanto à flexibilidade e tomada de decisão:

| Funcionalidade | Automação Tradicional | Agente de IA (AI Agent) |
| :--- | :--- | :--- |
| **Lógica** | Regras fixas e condicionais pré-definidas (Se A, faça B). | Análise contextual e tomada de decisão autônoma. |
| **Tomada de Decisão** | Não pensa; executa estritamente o fluxo programado. | Utiliza LLMs (ChatGPT, Gemini, Claude) como "cérebro". |
| **Exemplo de Aplicação** | Cliente preenche formulário $ightarrow$ envia e-mail padrão. | Cliente faz uma pergunta $ightarrow$ IA lê a base de conhecimento e responde sob medida. |
| **Adaptação** | Requer alteração manual do fluxo caso surja uma exceção. | Interpreta sentimentos, exceções e contexto variável. |

---

## ⚡ 3. Anatomia de uma Automação no n8n

Toda automação estruturada dentro do n8n segue três etapas fundamentais:

```
[ Gatilho (Trigger) ] ──> [ Processamento de Dados / IA ] ──> [ Ação (Action) ]
```

1. **Gatilho (Trigger):** O evento inicial que dispara a automação.
   * *Exemplos:* Receber uma nova mensagem no WhatsApp, agendamento de horário (ex: 09:00 AM), novo cadastro num formulário, recebimento de e-mail.
2. **Processamento de Dados / Raciocínio de IA:** Filtro, transformação de informações ou decisão cognitiva.
   * *Exemplos:* Leitura de um PDF por visão computacional/IA, classificação de sentimento do cliente, busca em base de conhecimento (RAG).
3. **Ação (Action):** O resultado executado ao final do fluxo.
   * *Exemplos:* Envio de e-mail personalizado, atualização de linha no Google Sheets, notificação em canal corporativo (Slack/Telegram), agendamento no Google Calendar.

---

## 📊 4. Estudo de Casos Práticos Apresentados

### Caso 1: Processamento Automático de Faturas e Notas Fiscais
* **Fluxo:** Recebimento de uma fatura via Telegram/WhatsApp $ightarrow$ Download automático do arquivo $ightarrow$ Extração dos dados $ightarrow$ Registro na planilha Google Sheets $ightarrow$ Upload do comprovante/fatura no Google Drive.
* **Benefício:** Elimina a digitação e conferência manual de notas fiscais pelo setor financeiro.

### Caso 2: Agente de Atendimento e Triagem de Reembolsos
* **Fluxo:** O cliente preenche um formulário de solicitação de reembolso. A IA consulta a base de dados para verificar a data da compra e o histórico financeiro do cliente.
* **Lógica de Decisão:**
  * **Dentro do prazo (7 dias):** Processa a solicitação automaticamente.
  * **Fora do prazo + Cliente VIP (Gasto elevado):** IA identifica o status VIP e encaminha uma mensagem personalizada ao suporte para análise de exceção.
  * **Fora do prazo + Cliente Irritado/Ameaça legal:** IA analisa o tom do comentário (em *caps lock* ou tom agressivo) e aciona o time de atendimento no Slack/Telegram com alerta de prioridade.
  * **Fora do prazo + Cliente comum:** Responde educadamente por e-mail informando o término do prazo contratual.

### Caso 3: Chatbot Inteligente para Suporte e Vendas
* **Fluxo:** Dúvida enviada no site $ightarrow$ Buffer de espera de 10 segundos (para verificar se o usuário ainda está digitando) $ightarrow$ Consulta à base de conhecimento da empresa $ightarrow$ Resposta natural e precisa em segundos.

---

## 🎯 Próximos Passos
Nas próximas aulas do curso básico, você colocará a mão na massa:
1. **Aula 2:** Criação do primeiro fluxo de automação do absoluto zero no n8n.
2. **Aula 3:** Construção e integração do seu primeiro **Agente de IA** funcional.

---
*Material baseado na Aula 1 do Curso Básico de Automações com n8n do canal Hashtag No Code & IA.*
