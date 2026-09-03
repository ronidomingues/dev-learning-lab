# 12 · Ética, lei e contrato — o arquivo que protege sua liberdade

`Nível: iniciante → obrigatório` · `Última atualização: 12/08/2026`

> Este é o arquivo mais importante do curso e o menos técnico. A diferença entre um
> profissional e um réu não é habilidade — é **autorização documentada**. Leia inteiro antes
> de apontar qualquer ferramenta para qualquer coisa que não seja sua.

**Aviso:** não sou advogado e isto não é aconselhamento jurídico. É um mapa do terreno legal
escrito por um profissional, com os dispositivos citados textualmente para você conferir na
fonte. Para um contrato real, envolva um advogado.

---

## 1. A regra de ouro, sem exceção

**Sem autorização expressa, por escrito, de quem tem poder para autorizar, e dentro de um
escopo definido — testar é crime.** Não importa a intenção. Não importa se você "só olhou".
Não importa se você avisou depois. A lei brasileira pune o **acesso não autorizado**, não o
dano.

Três perguntas antes de todo teste:
1. Tenho autorização **por escrito**?
2. Quem assinou tem **autoridade** para autorizar (é dono do sistema, não um terceiro)?
3. O que vou fazer está **dentro do escopo** que foi autorizado?

Se qualquer resposta for "não" ou "não sei" — **pare**.

## 2. A lei brasileira, artigo por artigo

### 2.1 Art. 154-A do Código Penal — Invasão de dispositivo informático

Introduzido pela **Lei 12.737/2012** ("Lei Carolina Dieckmann") e endurecido pela
**Lei 14.155/2021**. O texto vigente (após 2021):

> **Art. 154-A.** Invadir dispositivo informático alheio, conectado ou não à rede de
> computadores, com o fim de obter, adulterar ou destruir dados ou informações sem autorização
> expressa ou tácita do usuário do dispositivo ou de instalar vulnerabilidades para obter
> vantagem ilícita:
> **Pena – reclusão, de 1 (um) a 4 (quatro) anos, e multa.**

**Pontos que você precisa entender:**

- **A Lei 14.155/2021 removeu** a exigência de "mediante violação indevida de mecanismo de
  segurança". Antes, argumentava-se que sem quebrar uma proteção não havia crime. **Agora não
  precisa quebrar nada** — acessar sem autorização já configura. Um IDOR "só trocando o número
  na URL" cabe aqui.
- **Não é preciso causar dano.** "Obter" dados já basta. Você não precisa apagar nem roubar.
- A pena **aumenta** se houver prejuízo econômico, se os dados forem obtidos/divulgados, e se
  a vítima for autoridade pública. Chega a **reclusão de 2 a 5 anos** em qualificadoras.

### 2.2 Outros dispositivos que podem incidir

| Dispositivo | Quando incide |
|---|---|
| **Art. 266 CP** (interrupção de serviço) | derrubar/interromper serviço telemático — DoS |
| **Art. 313-A/B CP** | inserção/alteração de dados em sistema da administração pública |
| **Art. 171 CP** (estelionato) e §2º-A | fraude eletrônica (Lei 14.155/2021 criou a modalidade "fraude eletrônica", com pena maior) |
| **Lei 9.296/1996** | interceptação de comunicações sem ordem judicial |
| **LGPD (Lei 13.709/2018)** | tratamento indevido de dados pessoais (esfera cível/administrativa, multas altas) |
| **Marco Civil (Lei 12.965/2014)** | princípios de uso da internet, guarda de logs |

### 2.3 O que isso significa na prática

- **Escanear** um site que não é seu, sem autorização, com nmap → já é acesso/tentativa
  indevidos. Sim, um `nmap` pode ser enquadrado.
- **Testar credenciais** ("será que admin/admin funciona?") num sistema alheio → tentativa de
  acesso não autorizado.
- **Achar uma falha por acaso e "só confirmar"** → você cruzou a linha ao confirmar.
- **Avisar a empresa depois** ("achei essa falha, corrige aí") → confissão por escrito de um
  crime. Já houve gente processada exatamente assim, no Brasil e no exterior.

> **O caso que todo mundo cita:** nos EUA, jornalistas e pesquisadores foram ameaçados de
> processo sob o CFAA por acessar dados que estavam publicamente expostos (o caso do repórter
> do Missouri que "viu o código-fonte" de um site do governo em 2021). A lição vale aqui: a
> exposição do alvo **não** é autorização. Que a porta esteja aberta não te dá direito de entrar.

## 3. Bug bounty é autorização — mas só dentro das regras

Programas de bug bounty (HackerOne, Bugcrowd, YesWeHack, Intigriti) são uma **autorização
pública e condicional**. Você pode testar **os alvos listados**, **do jeito que as regras
permitem**, e nada além.

**O que te tira da proteção legal, mesmo num programa:**
- Testar um domínio/ativo **fora do escopo** listado.
- Usar técnica **proibida** (DoS, engenharia social contra funcionários, ataque físico).
- **Acessar dados de terceiros** além do mínimo para provar (varrer 100 mil registros reais).
- **Extrair, guardar ou divulgar** dados. Você prova o padrão com dado seu ou mínimo, e para.
- Violar o **safe harbor**: leia se o programa oferece "porto seguro" jurídico. Sem ele, a
  empresa **pode** processar mesmo achado válido — raro, mas possível.

**Sempre leia:** o `policy` do programa, o `scope` (in/out), o `Safe Harbor` e o
`security.txt` ([RFC 9116](https://www.rfc-editor.org/rfc/rfc9116)) do alvo, se existir.

## 4. Divulgação: full × responsible × coordinated

Você achou uma falha (num programa, ou num software que você usa legitimamente). E agora?

| Modelo | O que é | Prós/contras |
|---|---|---|
| **Full disclosure** | publicar tudo imediatamente | força correção; expõe usuários enquanto não há patch |
| **Responsible / coordinated disclosure** | avisar o fabricante em privado, dar prazo (ex. 90 dias), publicar depois | padrão ético atual; equilibra pressão e proteção |
| **Non-disclosure** | nunca publicar | comum quando há NDA; ruim se o fabricante ignora |

**Padrão recomendado (CVD — Coordinated Vulnerability Disclosure):** reportar em privado,
combinar prazo, publicar depois da correção (ou após o prazo, se ignorado). O prazo de 90 dias
do Google Project Zero virou referência informal do setor.

> **Cuidado brasileiro:** "responsible disclosure" te protege eticamente, **não
> necessariamente juridicamente**. Se você achou a falha **testando sem autorização**, avisar
> bem não apaga o acesso indevido. A ordem correta é: autorização primeiro, achado depois.

## 5. O contrato de um pentest profissional — o que precisa ter

Num trabalho pago, estes documentos protegem você e o cliente:

1. **Contrato de prestação de serviço** — objeto, prazo, valor, confidencialidade.
2. **Autorização de teste ("get out of jail letter")** — o documento que diz, com assinatura
   de quem tem autoridade, que você está autorizado a testar tais ativos, em tal janela.
   **Leve uma cópia (física ou digital) durante o teste.** Se o SOC do cliente te detectar e a
   polícia for chamada, esse papel é o que te separa de uma noite na delegacia.
3. **Regras de Engajamento (RoE)** — escopo (in/out), janela, técnicas permitidas e proibidas,
   tratamento de dados, contato de emergência, o que fazer se achar uma invasão real prévia.
4. **NDA** — confidencialidade dos achados.
5. **Seguro de responsabilidade civil profissional** — se você quebra algo caro por acidente.

Modelo de escopo e RoE: veja [`07-projeto-modelo/escopo-e-roe.md`](07-projeto-modelo/escopo-e-roe.md).

**Autoridade importa.** Quem assina precisa ser dono do sistema. Cuidado com:
- Testar um sistema que o cliente **usa mas não é dono** (SaaS de terceiro, nuvem). Você
  precisa da autorização **do provedor** também — AWS, Azure e GCP têm políticas específicas
  de pentest, algumas exigindo aviso prévio.
- Testar aplicação hospedada em provedor que **proíbe** scanning nos termos de uso.
- Um gerente autorizando teste de um sistema de outro departamento sem poder para isso.

## 6. Limites éticos que a lei não cobre (mas você deve respeitar)

- **Não olhe o que não precisa.** Achou acesso ao banco? Prove com um registro, não leia o
  prontuário médico de ninguém. Curiosidade não é escopo.
- **Engenharia social tem gente do outro lado.** Um phishing de teste pode humilhar um
  funcionário. Combine antes como os "pegos" serão tratados — treinamento, nunca punição.
- **Descoberta acidental de crime real.** Se durante um teste você encontra sinais de invasão
  em andamento, ou conteúdo ilegal, **pare, documente minimamente e escale** para o contato
  de emergência e, conforme o caso, autoridades. Não investigue por conta.
- **Dados de menores, saúde, biometria** têm proteção reforçada (LGPD art. 11 e 14). Trate com
  cuidado extra ou evite.

## 7. Erros que acabam com carreiras (casos reais e recorrentes)

| Erro | O que aconteceu | Lição |
|---|---|---|
| "Só testei um pouquinho fora do escopo" | achado excelente, mas em ativo não autorizado → não pago e risco de processo | escopo é lei, não sugestão |
| Testar em cliente da empresa sem avisar a segurança dela | SOC detecta, RH aciona justa causa | rede corporativa exige autorização formal |
| Guardar dump de cliente "para o portfólio" | vazamento depois; quebra de NDA e LGPD | destrua dados após entregar; anonimização e permissão para portfólio |
| Publicar write-up de cliente sem permissão | processo por quebra de confidencialidade | portfólio só com permissão escrita |
| "Achei essa falha no seu site, me contrata?" (e-mail não solicitado) | interpretado como extorsão/acesso indevido | nunca teste para prospectar; use bug bounty |

## 8. Checklist ético-legal antes de todo teste

- [ ] Tenho **autorização por escrito**, assinada por quem tem **autoridade**.
- [ ] O **escopo** (o que pode e o que não pode) está claro e documentado.
- [ ] Sei a **janela** de tempo permitida.
- [ ] Sei quais **técnicas são proibidas** (DoS? social? físico?).
- [ ] Tenho um **contato de emergência** e sei quando parar.
- [ ] Se for provedor terceiro/nuvem, tenho a autorização **do provedor** também.
- [ ] Vou tratar dados achados com **mínimo acesso** e **destruição** depois.
- [ ] Se for bug bounty: li `policy`, `scope`, `safe harbor` e sei o que é fora de escopo.
- [ ] Tenho uma cópia da autorização **comigo** durante o teste.

Se você não consegue marcar tudo, você não está fazendo hacking ético. Está correndo risco.

---

## Autoteste

1. Segundo o art. 154-A do CP após a Lei 14.155/2021, é preciso "quebrar um mecanismo de
   segurança" para configurar o crime? E é preciso causar dano?
2. Por que avisar uma empresa sobre uma falha que você achou testando **sem autorização** pode
   piorar a sua situação, em vez de melhorar?
3. Um bug bounty autoriza você a testar qualquer coisa do alvo? O que te tira da proteção?
4. O que é uma "get out of jail letter" e por que você a leva impressa no teste?
5. Diferencie full disclosure, responsible disclosure e coordinated disclosure.
6. Você está testando um sistema que o cliente hospeda na AWS. De quem mais você precisa de
   autorização, além do cliente?
7. Durante um teste autorizado você ganha acesso ao banco de dados de saúde. Qual é a conduta
   correta em relação aos dados?
8. Cite três erros que acabam com carreiras e a lição de cada um.
