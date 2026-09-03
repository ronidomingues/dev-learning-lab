# 01 · O que é hospedar um sistema web — para quem nunca viu isso

`Nível: iniciante` · `Sem pré-requisito nenhum` · `Atualizado em 18/08/2026`

---

## 1. A pergunta antes da pergunta

Você abre `www.algumacoisa.com.br` no celular e uma tela aparece. De onde ela veio?

Ela veio de **um computador de outra pessoa, ligado agora, em algum lugar do mundo**, que
estava esperando exatamente esse pedido. Esse é o segredo inteiro. Não há nuvem. Há o
computador de outra pessoa, num galpão com ar-condicionado, fibra óptica e gerador a diesel
no porão.

**Hospedar** (em inglês, *hosting*) é a atividade de manter esse computador ligado, acessível
pela internet e respondendo aos pedidos do seu sistema. Você pode fazer isso com uma máquina
sua embaixo da mesa — muita gente fez, por anos — ou pode alugar essa capacidade de alguém que
já tem o galpão, a fibra e o gerador. Alugar é o que quase todo mundo faz hoje, e é do que
este curso trata.

---

## 2. A analogia do restaurante

Um sistema web tem quatro peças. Elas quase sempre aparecem juntas, e cada uma tem um trabalho
diferente. Pense num restaurante:

```
┌──────────────────────────────────────────────────────────────────┐
│                         O RESTAURANTE                            │
│                                                                  │
│  SALÃO E CARDÁPIO          ┌──────────────┐                      │
│  (o que o cliente vê)  →   │   FRONTEND   │  HTML, CSS, imagens  │
│                            └──────┬───────┘                      │
│                                   │ pedido                       │
│  COZINHA                   ┌──────▼───────┐                      │
│  (quem prepara)        →   │   BACKEND    │  a lógica, as regras │
│                            └───┬──────┬───┘                      │
│                                │      │                          │
│  DESPENSA (tudo guardado)  ┌───▼──┐ ┌─▼──────┐  BANCADA          │
│  frio, organizado,     →   │POSTGR│ │ REDIS  │  ← o que está     │
│  nunca some                │ ESQL │ │        │    à mão, quente  │
│                            └──────┘ └────────┘                   │
└──────────────────────────────────────────────────────────────────┘
```

**Frontend** — o salão e o cardápio. É o que chega ao navegador do cliente: as telas, os
botões, as cores. São arquivos prontos, iguais para todo mundo, que só precisam ser entregues
rápido. Um cardápio impresso: você imprime uma vez e distribui mil cópias.

**Backend** — a cozinha. É o programa que recebe o pedido ("quero ver meus pedidos", "quero
cadastrar este cliente"), decide se você tem permissão, faz a conta, busca o que precisa e
devolve a resposta. É onde moram as **regras do negócio**. Diferente do cardápio, a cozinha
tem que *pensar* a cada pedido.

**PostgreSQL** — a despensa. É onde ficam os dados que **não podem sumir nunca**: usuários,
pedidos, notas fiscais, saldos. Organizada, com etiqueta em tudo, com regras rígidas
("não existe pedido sem cliente"). É lenta comparada à bancada, mas é confiável: se faltar
luz, o que estava na despensa continua lá. PostgreSQL é o nome de um programa específico de
despensa — o mais respeitado da categoria, gratuito e de código aberto.

**Redis** — a bancada da cozinha. É onde ficam as coisas de acesso **imediato e frequente**:
o molho já pronto, a sessão de quem acabou de entrar, o contador de "quantas vezes esse
usuário tentou a senha". Fica na memória RAM, e por isso é 100 a 1.000 vezes mais rápido que
a despensa. Em troca, **se faltar luz, a bancada some**. Você nunca guarda a única cópia de
algo na bancada. Redis é o nome do programa mais conhecido dessa categoria.

> **Por que separar despensa e bancada?** Porque disco e memória têm físicas diferentes.
> Ler um dado da memória RAM leva cerca de 100 nanossegundos; de um disco SSD, cerca de
> 100 microssegundos — **mil vezes mais**. E a memória custa muito mais caro por gigabyte e
> perde tudo ao desligar. Você usa a memória para o pouco que é usado o tempo todo, e o disco
> para o muito que precisa sobreviver. Essa não é uma convenção de programador: é consequência
> de como transistores e discos funcionam.

---

## 3. Onde essas quatro peças moram

Aqui está a parte que confunde iniciantes: **elas não precisam morar no mesmo lugar**.

Nos anos 2000, moravam. Você alugava "uma hospedagem", jogava seus arquivos PHP lá por FTP,
e o banco MySQL estava na mesma máquina. Um lugar, uma conta, uma fatura.

Hoje, o normal é o contrário: cada peça mora num serviço especializado, de empresas
diferentes, e elas conversam pela internet.

```
seu navegador
     │
     ├──► frontend na Cloudflare Pages (borda global, grátis)
     │
     └──► backend no Render (Oregon, EUA, grátis com sono)
               │
               ├──► PostgreSQL na Neon (São Paulo, grátis até 0,5 GB)
               └──► Redis na Upstash (grátis até 500 mil comandos/mês)
```

Parece complicado. Tem uma vantagem enorme: **cada peça tem custo, escala e falha
independente**. O frontend pode aguentar um milhão de visitas sem tocar no backend. O banco
pode crescer sem que você troque o servidor da aplicação. E — o ponto que interessa à sua
pergunta — **cada uma dessas peças tem alguém oferecendo uma versão gratuita**, porque cada
uma é um mercado disputado.

A desvantagem: quatro contas, quatro painéis, quatro faturas, quatro políticas de preço que
mudam sem avisar, e latência entre as peças (um backend em Oregon falando com um banco em São
Paulo paga em torno de 170 ms em cada ida e volta — veja [`45`](45-brasil-latencia-e-lgpd.md)).

---

## 4. "Grátis" — o que essa palavra esconde

Existem exatamente três tipos de grátis em hospedagem. Confundir os três é o erro mais caro
que um iniciante comete.

| Tipo | Como funciona | Exemplo em 18/08/2026 | Risco |
|---|---|---|---|
| **Grátis permanente com teto** | Você usa até um limite. Passou, para ou cobra. | Cloudflare Workers: 100.000 requisições/dia, sem prazo | O teto pode ser reduzido; o serviço pode fechar |
| **Grátis com degradação** | Funciona, mas mal de propósito, para você querer pagar | Render: seu backend **dorme** após 15 min sem acesso e demora ~1 min para acordar | Usuário real percebe. Não serve para produção |
| **Crédito temporário** | Você ganha dinheiro de brinde, que acaba | AWS: US$ 100–200 em créditos, plano gratuito expira em 6 meses | **Vira fatura sem aviso claro.** É onde as pessoas se queimam |

E há um quarto, que não é grátis mas parece: **grátis para começar, caro para sair**. Você
constrói tudo em cima de um serviço proprietário e, quando o preço sobe, migrar custa três
meses de trabalho. Isso se chama *vendor lock-in*, aprisionamento de fornecedor. É o custo
oculto mais caro de todos, e nenhuma tabela de preço o mostra.

> **Opinião profissional, declarada como opinião:** para aprender e para projetos pessoais,
> use camada gratuita à vontade — é dinheiro que sobra no seu bolso e nada de mal acontece se
> o serviço cair. Para qualquer coisa de que outra pessoa dependa (um cliente, um TCC com
> prazo, uma loja), **use camada gratuita para o frontend e para o cache, e pague pelo banco
> de dados**. O banco é onde mora o que você não pode perder, e US$ 5 a US$ 25 por mês é
> barato comparado a explicar a um cliente que os dados sumiram porque o projeto foi pausado
> por inatividade.

---

## 5. Por que isso existe: o problema que a hospedagem resolve

Nada disso apareceu porque alguém achou bonito. Vale a pena perguntar *por quê* cinco vezes:

1. **Por que não rodo o sistema no meu computador?**
   Porque ele precisa estar ligado 24 horas, com endereço fixo na internet, e ninguém quer
   que a apresentação ao cliente caia porque você fechou o notebook.

2. **Por que não compro um servidor e deixo na empresa?**
   Muita gente faz. Mas você passa a ser responsável por energia, refrigeração, link
   redundante, backup, troca de disco às 3h da manhã e segurança física. Isso é um emprego,
   não um detalhe.

3. **Por que não alugo só uma máquina virtual e cuido do resto?**
   Você pode — e o capítulo [`20`](20-catalogo-backend-paas.md) mostra que isso voltou à
   moda em 2024–2026 por ser 5 a 20 vezes mais barato. Mas você ainda instala, configura,
   atualiza, monitora e conserta. Custa tempo. Se o seu tempo vale R$ 100/hora, cinco horas
   por mês de manutenção equivalem a R$ 500 — mais caro que qualquer plano gerenciado
   equivalente.

4. **Por que existe uma plataforma que faz tudo isso por US$ 7?**
   Porque ela faz para dez mil clientes ao mesmo tempo na mesma infraestrutura. O custo fixo
   (galpão, equipe, ferramenta) se dilui. Isso se chama **economia de escala em serviço
   multi-inquilino**, e é a razão econômica de a computação em nuvem existir.

5. **E por que uma parte disso é dada de graça?**
   Porque o custo marginal de mais um usuário pequeno é quase zero e a chance de ele virar
   pagante é alta. É aquisição de cliente pagando o próprio custo. Quando essa conta deixa de
   fechar — porque houve abuso em massa, ou porque investidores exigiram lucro — **a camada
   gratuita morre**. Foi o que aconteceu com o Heroku em 28 de novembro de 2022 e com o
   Fly.io em 2024. Veja [`55-economia-do-gratuito.md`](55-economia-do-gratuito.md).

---

## 6. Um mapa dos nomes que você vai ouvir

Você não precisa decorar agora. Só precisa não travar quando eles aparecerem.

| Nome | Em uma frase |
|---|---|
| **Servidor** | Um computador cujo trabalho é responder pedidos de outros computadores |
| **VPS** | Uma fatia de um servidor grande, alugada como se fosse uma máquina só sua |
| **Nuvem / cloud** | Alugar computação por hora, sob demanda, via API, sem contrato longo |
| **PaaS** | "Plataforma como serviço": você entrega o código, ela cuida do resto (Render, Railway) |
| **Serverless** | Você paga só quando alguém usa; entre os pedidos, não existe servidor seu ligado |
| **Container** | Uma caixa com seu programa e tudo de que ele precisa, que roda igual em qualquer lugar |
| **Docker** | O programa que criou e popularizou containers |
| **Deploy** | O ato de colocar uma nova versão do sistema no ar |
| **CDN** | Rede de máquinas espalhadas pelo mundo que guardam cópias do seu frontend perto do usuário |
| **Edge** | Rodar código nessas máquinas espalhadas, não num único data center |
| **Cold start** | O atraso de quando um serviço adormecido precisa acordar antes de responder |
| **Free tier** | Camada gratuita |
| **Vendor lock-in** | Aprisionamento: o custo de sair de um fornecedor |

Todos estes e mais ~140 estão definidos em [`GLOSSARIO.md`](GLOSSARIO.md).

---

## 7. A resposta curta à sua pergunta, em uma tabela

Detalhes, números e ressalvas nos capítulos [`20`](20-catalogo-backend-paas.md) a
[`40`](40-arquiteturas-de-referencia.md). Isto aqui é o mapa mental:

| Peça | Melhor gratuito hoje (18/08/2026) | Melhor pago barato | Se for pra valer |
|---|---|---|---|
| **Frontend** | **Cloudflare Pages** (requisições a arquivos estáticos ilimitadas) | Cloudflare Workers Paid US$ 5/mês | Cloudflare ou Vercel Pro |
| **Backend** | **Cloudflare Workers** (100k req/dia) ou **Render Free** (com sono) | **Render US$ 7/mês** ou Hetzner + Coolify (~€ 4,49) | Render/Railway Pro, Fly.io, Northflank |
| **PostgreSQL** | **Neon** (0,5 GB, com região São Paulo) ou **Supabase** (500 MB) | Neon Launch / Supabase Pro US$ 25 | RDS, Cloud SQL, Aiven, Neon Scale |
| **Redis** | **Upstash** (256 MB, 500k comandos/mês) | Upstash pay-as-you-go | Redis Cloud, Valkey no ElastiCache, ou próprio |

**Se você quer uma única recomendação para começar hoje, de graça, sem cartão de crédito:**
frontend na Cloudflare Pages, backend no Render (aceitando o sono de 15 minutos), banco na
Neon com região `sa-east-1` (São Paulo), cache na Upstash. O passo a passo está em
[`04-como-comecar.md`](04-como-comecar.md).

---

## 8. O que este material *não* vai dizer

- Não vai dizer que existe uma plataforma melhor que todas. Não existe; existe a melhor para
  o seu caso, e o caso muda.
- Não vai esconder que boa parte das camadas gratuitas de hoje não existirá em 2029.
- Não vai recomendar a moda do momento sem dizer o preço da moda anterior.

---

## Autoteste

1. Explique, sem usar a palavra "servidor", o que acontece entre você digitar um endereço e a tela aparecer.
2. Por que o Redis é rápido e por que isso o torna perigoso como único lugar de guardar um dado?
3. Quais são os três tipos de "grátis" e qual deles costuma gerar fatura inesperada?
4. Por que as quatro peças de um sistema web moderno costumam morar em empresas diferentes? Cite uma vantagem e uma desvantagem.
5. Qual é o custo oculto que nenhuma tabela de preço mostra?
6. Por que uma empresa oferece um plano gratuito se ele lhe custa dinheiro?
7. Em que situação este capítulo recomenda **pagar** mesmo havendo alternativa gratuita, e por quê?
