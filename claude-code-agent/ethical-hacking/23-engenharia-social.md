# 23 · Engenharia social

`Nível: intermediário` · `Última atualização: 12/08/2026`

O elo mais fraco raramente é a tecnologia — é a pessoa. Engenharia social é a arte de manipular
pessoas para obter acesso ou informação. É a técnica mais eficaz e a mais delicada eticamente.

> ⚖️ **Aviso reforçado:** engenharia social atinge **seres humanos**, não máquinas. Exige
> autorização explícita, regras claras sobre como os "pegos" serão tratados (treinamento,
> **nunca** punição), e limites bem definidos. Fazer isto sem autorização é crime e é abuso.
> Ver [`12`](12-etica-lei-e-contrato.md).

---

## 1. Por que funciona: os gatilhos psicológicos

Engenharia social explora atalhos mentais que todos temos. Robert Cialdini os catalogou; o
atacante os usa:

| Gatilho | Como é explorado |
|---|---|
| **Autoridade** | "Sou do TI/diretoria, preciso que você..." |
| **Urgência/escassez** | "Sua conta será bloqueada em 1 hora" |
| **Prova social** | "Todos do seu time já fizeram isso" |
| **Reciprocidade** | fazer um favor pequeno antes de pedir |
| **Afeição/similaridade** | criar rapport, parecer "um dos nossos" |
| **Medo** | "Detectamos um vírus, clique para remover" |

A defesa é **consciência** — treinamento que ensina a pausar e verificar antes de agir sob
esses gatilhos.

## 2. Os vetores

### Phishing (o rei)
E-mail (ou mensagem) que induz a vítima a clicar num link, abrir um anexo, ou entregar
credenciais numa página falsa. Variações:
- **Spear phishing:** direcionado a uma pessoa específica, personalizado com OSINT ([`14`](14-reconhecimento-e-osint.md)).
- **Whaling:** mira executivos (o "peixe grande").
- **Vishing:** por telefone (voz). Muito eficaz; a voz cria pressão e confiança.
- **Smishing:** por SMS.
- **Quishing:** por QR code (contorna filtros de link).

### Pretexting
Criar um cenário falso convincente ("sou o técnico da operadora, preciso confirmar seus dados")
para extrair informação ou acesso. É a espinha de quase toda engenharia social.

### Físico
- **Tailgating/piggybacking:** entrar atrás de alguém autorizado numa porta com crachá.
- **Baiting:** deixar um pendrive "perdido" no estacionamento; a curiosidade faz a vítima
  plugá-lo. (Estudos mostram taxa de plugagem alta — a curiosidade vence o treinamento.)
- **Impersonation:** passar-se por entregador, técnico, funcionário novo.

## 3. Ferramentas (para engajamento autorizado)

- **GoPhish:** framework open source para campanhas de phishing autorizadas — cria a página,
  envia, mede quem clicou/entregou credencial. Padrão de mercado.
- **Evilginx / modlishka:** *reverse proxy* de phishing que captura sessão **e contorna MFA**
  (rouba o token de sessão, não só a senha). Poderoso e perigoso; uso estritamente autorizado.
- **SET (Social-Engineer Toolkit):** clássico, gera páginas clonadas e payloads.
- **Gophish + domínio parecido + certificado válido:** a montagem típica de uma campanha real.

> **Sobre MFA:** MFA reduz muito o risco de phishing de senha, mas *evilginx* mostra que MFA
> baseado em código/push é contornável por proxy de sessão. A defesa forte é **FIDO2/passkeys**
> (chave física/biométrica ligada à origem), que não é phishável por proxy. Recomende isso.

## 4. Como se estrutura uma campanha autorizada

```
1. Autorização e regras (quem, o quê, como tratar os "pegos")
2. OSINT: alvos, padrão de e-mail, temas que ressoam (RH, benefícios, TI)
3. Infraestrutura: domínio parecido, e-mail, página clonada, rastreamento
4. Pretexto: a "isca" (redefinição de senha, novo benefício, comunicado urgente)
5. Envio controlado e medição (aberturas, cliques, credenciais entregues)
6. Relatório: taxa por gatilho, sem expor indivíduos; recomendações de treino
```

**A métrica que importa não é "quantos caíram"** — é o quanto o treinamento melhora isso ao
longo do tempo, e se existe um canal fácil para o funcionário **reportar** o phishing (a taxa
de reporte é um indicador de maturidade melhor que a taxa de clique).

## 5. A ética, com todo o cuidado

Este é o vetor onde o dano humano é real. Princípios inegociáveis:
- **Nunca** use temas que causem pânico genuíno ou dano emocional (falsa morte, demissão,
  doença). Já houve escândalos com "e-mail de bônus falso" que humilharam funcionários.
- **Nunca** exponha indivíduos no relatório. Reporte agregados. O objetivo é o sistema, não
  pegar pessoas.
- Os "pegos" recebem **treinamento**, jamais punição. Punir destrói a cultura de reporte, que é
  a defesa real.
- Combine tudo isso **por escrito, antes**, com RH e liderança.

## 6. A defesa (para o relatório)

- Treinamento contínuo e simulações (com cuidado ético).
- Canal fácil de **reportar** phishing (botão no e-mail).
- MFA forte, preferencialmente **FIDO2/passkeys**.
- Filtros de e-mail, DMARC/SPF/DKIM (dificultam falsificação de remetente).
- Princípio de menor privilégio (limita o dano de uma conta comprometida).
- Verificação fora de banda para pedidos sensíveis ("ligue de volta no número oficial").

## 7. Os cinco porquês: por que a engenharia social é imbatível?

**Por quê 1** — Por que engenharia social funciona mesmo em empresas com boa tecnologia?
Porque ela ataca a pessoa, e a pessoa usa atalhos mentais (autoridade, urgência) que são
rápidos e úteis na vida — e exploráveis.

**Por quê 2** — Por que não "consertamos" a pessoa com treinamento?
Treinamento ajuda, mas os atalhos são **cognição humana básica**, não ignorância. Sob pressão,
tempo curto e volume, até especialistas caem. Não é falta de saber; é como o cérebro funciona.

**Por quê 3** — Por que não remover o humano do processo (automatizar tudo)?
Porque decisões que exigem julgamento, exceção e empatia precisam de pessoas — e é justamente
onde o manipulador entra. Um sistema 100% rígido quebra a operação; a flexibilidade humana que
faz a empresa funcionar é a mesma que o atacante abusa.

**Por quê 4** — Por que a tecnologia (MFA, filtros) não resolve de vez?
Reduz muito, mas o atacante se adapta (evilginx contra MFA, quishing contra filtros de link). É
uma corrida; cada defesa técnica gera uma técnica de contorno que volta a mirar o humano.

**Por quê 5** — Qual é a parada?
Uma **propriedade da condição humana**: enquanto pessoas tomarem decisões (e elas precisam
tomar), a manipulação terá superfície. A defesa não é eliminar o humano — é **reduzir o dano de
um erro** (menor privilégio, MFA forte, verificação fora de banda) e **construir cultura de
reporte**. Você não elimina a engenharia social; você a torna menos rentável. É por isso que
ela é, e continuará sendo, o vetor mais eficaz — e por que a defesa é organizacional, não só
técnica.

---

## Autoteste

1. Cite quatro gatilhos psicológicos e como cada um é explorado.
2. Diferencie phishing, spear phishing, whaling, vishing e quishing.
3. Como o evilginx contorna o MFA, e qual tipo de MFA resiste a isso?
4. Qual métrica de uma campanha importa mais que "quantos caíram", e por quê?
5. Liste três princípios éticos inegociáveis de um engajamento de engenharia social.
6. Por que punir os "pegos" é contraproducente?
7. Por que a engenharia social é imbatível por completo, e o que a defesa realmente busca?
   Leve o porquê até o fim.
