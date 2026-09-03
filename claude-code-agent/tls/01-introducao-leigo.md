# 01 · O que é TLS — para quem nunca ouviu falar

**Nível:** iniciante · **Pré-requisito:** nenhum · **Data:** 31/08/2026

Este arquivo não usa nenhum termo técnico sem antes explicá-lo com uma coisa do mundo real.

---

## 1. O problema, sem computadores

Imagine que você quer mandar a senha do seu banco para o seu banco, e o único jeito
de mandar é escrever num **cartão-postal** e entregar ao carteiro.

O cartão-postal tem três problemas:

1. **Todo mundo lê.** O carteiro lê. O vizinho lê. Quem manuseia no centro de
   distribuição lê. A senha está escrita à vista de todos.
2. **Qualquer um pode alterar.** Alguém no caminho apaga "transferir R$ 10" e
   escreve "transferir R$ 10.000". Você não tem como saber.
3. **Você não sabe se o destinatário é quem diz ser.** Você escreveu "Banco X" no
   envelope, mas quem recebeu foi um sujeito que colocou uma placa "Banco X" na
   porta da casa dele.

A internet é literalmente isso. Um dado que sai do seu computador atravessa o
roteador de casa, o provedor, três ou quatro operadoras de trânsito, e o data center
de destino. Em cada um desses pontos, alguém pode ler e alterar.

**TLS é o conjunto de três invenções que resolve esses três problemas ao mesmo tempo.**

---

## 2. A solução, ainda sem computadores

### Problema 1 — todo mundo lê → o envelope lacrado

Em vez do cartão-postal, você usa um envelope opaco e lacrado. Quem pega no caminho
vê que existe uma carta, vê de quem vem e para onde vai, mas **não vê o conteúdo**.

Em TLS isso se chama **confidencialidade** (o conteúdo é ilegível para quem não é o destinatário).

Note o que o envelope **não** esconde: que você mandou uma carta, e para quem.
TLS tem exatamente a mesma limitação — quem observa a rede vê *que* você acessou
um site e *qual* (pelo endereço IP e, na maioria dos casos, pelo nome do site
escrito em claro no início da conversa). Vê "você falou com o banco por 4 minutos e
trocou 300 KB". Não vê o que foi dito. Guarde isso: **é a fonte de metade dos
mal-entendidos sobre HTTPS**.

### Problema 2 — qualquer um altera → o lacre que se rompe

Sua carta vai dentro de um envelope com um lacre de cera. Se alguém abrir e refechar,
o lacre fica quebrado e o destinatário percebe. Melhor ainda: cada folha leva no rodapé
um número calculado a partir do texto — mude uma vírgula e o número não bate.

Em TLS isso se chama **integridade** (dá para detectar qualquer alteração) e
**autenticidade da mensagem** (só quem tem a chave consegue produzir um lacre válido).

Detalhe importante: TLS **não impede** que alguém altere os bytes no caminho.
Fisicamente, qualquer um pode. O que TLS garante é que a alteração **será detectada**
e a conexão será derrubada. Detectar, não impedir.

### Problema 3 — não sei quem é o destinatário → o cartório

Este é o problema difícil, e a solução é a mais estranha das três.

Você não conhece o Banco X pessoalmente. Mas você conhece — e confia — em um cartório.
O Banco X vai ao cartório, prova de forma presencial que é o Banco X, e o cartório
emite um **documento carimbado** dizendo: "o portador desta é o Banco X, e a assinatura
dele é esta aqui".

Agora, quando você fala com alguém que se diz Banco X, ele te mostra o documento
carimbado. Você reconhece o carimbo do cartório (porque você já tem uma cópia do
carimbo dele guardada em casa), e desafia o sujeito a assinar uma frase que você
acabou de inventar. Se a assinatura bater com a do documento, é ele.

Em TLS:

| Analogia | Nome técnico |
|---|---|
| cartório | **CA** — *Certificate Authority*, Autoridade Certificadora |
| documento carimbado | **certificado** (formato X.509) |
| carimbo do cartório | **assinatura digital da CA** |
| cópia do carimbo que você guarda em casa | **âncora de confiança** (*trust anchor*), no seu **repositório de raízes** |
| assinar a frase que você inventou | prova de posse da **chave privada** |

O seu computador já vem de fábrica com uma lista de cartórios reconhecidos — algo
entre 100 e 170 deles, dependendo do sistema. Essa lista é o **repositório de
certificados raiz** (*root store*). Quem decide o que entra nessa lista são a Apple,
a Microsoft, a Google e a Mozilla. Você não decide. Isso é, ao mesmo tempo,
o que faz o sistema funcionar e o seu ponto mais frágil — voltaremos a isso no
[13-certificados-e-pki.md](13-certificados-e-pki.md).

---

## 3. Então, o que é TLS em uma frase

> **TLS é um protocolo que transforma um canal de rede qualquer — que é público,
> lido e alterável por qualquer um no caminho — em um canal privado, íntegro e
> com o outro lado identificado.**

"Protocolo" aqui significa: um **roteiro de conversa combinado de antemão**, com
mensagens numeradas, na ordem certa, com formato exato. Como um roteiro de
casamento: "agora o padre pergunta, agora o noivo responde". Se alguém falar fora
de ordem ou fora do formato, a conversa é abortada.

---

## 4. Onde você já usou TLS hoje sem saber

- O **cadeado** na barra do navegador. `https://` = HTTP dentro de TLS.
- WhatsApp, Telegram e Signal falando com os servidores deles.
- Seu e-mail sendo baixado (IMAP sobre TLS, porta 993) e enviado (SMTP, porta 465/587).
- O aplicativo do banco no celular.
- O `git push` para o GitHub via HTTPS.
- Praticamente toda chamada de API entre servidores em qualquer empresa.
- A atualização do seu sistema operacional (o download é verificado, e quase sempre baixado, por TLS).

Em agosto de 2026, a fatia de páginas carregadas com HTTPS no Firefox e no Chrome
passa de 90% em quase todos os países medidos. O padrão inverteu: hoje, **não usar
TLS é a exceção que precisa de justificativa**.

---

## 5. O que TLS **não** faz — e isso derruba muita gente

Esta é a seção mais importante deste arquivo. O cadeado verde é a coisa mais mal
compreendida da internet.

| Muita gente acha que… | A verdade |
|---|---|
| "cadeado = site confiável" | **Falso.** Cadeado significa "a conversa é privada e é com o dono deste domínio". Um site de golpe pode ter cadeado — e tem. Golpistas emitem certificado gratuito em segundos. |
| "HTTPS protege meus dados no servidor" | **Falso.** TLS protege *em trânsito*. Chegando no servidor, os dados são decifrados. Se o servidor for invadido ou o dono for desonesto, TLS não ajudou em nada. |
| "com HTTPS ninguém sabe quais sites eu acesso" | **Falso.** O IP de destino é visível. O nome do site também, na maioria dos casos (o campo SNI viaja em claro; o ECH, que resolve isso, só foi virar RFC em março de 2026 e ainda tem adoção baixa). E as consultas de DNS costumam ser em claro. |
| "TLS impede o hacker de mexer nos meus dados" | Impede que ele mexa **sem ser notado**. A conexão cai; o dado não passa alterado. |
| "TLS é criptografia ponta a ponta" | **Depende do que você chama de ponta.** É ponta a ponta entre *seu navegador* e *o servidor que termina o TLS* — que muitas vezes é um CDN ou um balanceador, não a aplicação. Não é o mesmo que a criptografia ponta a ponta do Signal, onde nem o servidor lê. |
| "SSL e TLS são coisas diferentes" | São o mesmo protocolo em épocas diferentes. SSL é o nome antigo (1994–1996), TLS é o nome desde 1999. Todas as versões de SSL estão mortas e proibidas. Quando alguém diz "certificado SSL", quer dizer certificado TLS — é vocabulário fossilizado do mercado. |
| "preciso comprar certificado para ter cadeado" | **Falso desde 2015.** O Let's Encrypt emite de graça, automatizado, e é aceito por todo navegador. |

---

## 6. Uma conversa TLS, contada como diálogo

Simplificado, mas com a ordem real do TLS 1.3 (a versão atual, de 2018):

```
NAVEGADOR: Oi. Falo TLS 1.3. Sei fazer estas cifras: [lista].
           Já vou adiantando: aqui está metade de um segredo que inventei agora.
           Ah — quero falar com "banco.com.br".

SERVIDOR:  Oi. Também falo TLS 1.3. Escolhi esta cifra da sua lista.
           Aqui está a minha metade do segredo.
           << a partir daqui tudo já é cifrado >>
           Este é o meu certificado, carimbado pela CA Fulana, dizendo que
           sou o dono de banco.com.br.
           E aqui está a minha assinatura de tudo que conversamos até agora,
           feita com a chave privada que só o dono do certificado tem.
           Terminei.

NAVEGADOR: (confere o carimbo da CA contra a lista que tenho guardada)
           (confere que o certificado realmente diz "banco.com.br")
           (confere que não venceu)
           (confere a assinatura)
           Fechado. Terminei.
           GET /saldo HTTP/1.1 ...
```

Duas coisas nesse diálogo merecem atenção agora, e serão dissecadas no
[12-handshake.md](12-handshake.md):

1. **As duas metades do segredo.** Cada lado gera um número secreto, manda uma
   "metade pública" dele, e ambos conseguem calcular *o mesmo* segredo final que
   ninguém que só ouviu a conversa consegue calcular. Isso é a **troca de chaves
   de Diffie–Hellman**, e é o truque mais elegante da criptografia moderna: dois
   estranhos gritando num salão lotado combinam uma senha que ninguém no salão descobre.
2. **Só o servidor se identifica.** No caso comum da web, o servidor prova quem é;
   você, não. Você prova quem é depois, por dentro do túnel, com usuário e senha.
   Quando os dois lados se identificam com certificado, chama-se **mTLS** (TLS mútuo)
   — comum entre servidores, raro entre pessoas.

---

## 7. Por que isso existe: a história em três parágrafos

Até 1994, a web não tinha criptografia nenhuma. Tudo era cartão-postal. Isso era
tolerável enquanto a internet era acadêmica e ninguém comprava nada.

Em 1994 a Netscape quis vender coisas pela web e percebeu que ninguém digitaria o
número do cartão de crédito num cartão-postal. Um engenheiro chamado Taher Elgamal
liderou a criação do **SSL** (*Secure Sockets Layer*). A versão 1.0 era tão ruim que
nunca foi lançada. A 2.0 saiu em 1995 e foi quebrada. A 3.0, de 1996, durou quase
20 anos até ser aposentada por um ataque chamado POODLE.

Em 1999 o protocolo virou padrão aberto da IETF e mudou de nome para **TLS 1.0** —
politicamente, para não carregar a marca de uma empresa. Vieram TLS 1.1 (2006),
TLS 1.2 (2008) e finalmente **TLS 1.3** (agosto de 2018), que jogou fora tudo que
tinha se mostrado perigoso em 24 anos de cicatrizes. Hoje só TLS 1.2 e 1.3 são
aceitáveis; TLS 1.3 é o que você deve preferir. A história completa, com as
lições de cada acidente, está em [11-historia.md](11-historia.md).

---

## 8. As três perguntas do título deste curso

**O que é?** Um protocolo de rede que cria um canal cifrado, íntegro e autenticado
sobre um canal inseguro. Fica entre o TCP (que só entrega bytes) e o HTTP (que fala
o conteúdo). Daí o nome: *Transport Layer Security*.

**Para que serve?** Para que dados sensíveis atravessem uma rede hostil sem serem
lidos nem alterados, e para que você tenha certeza de com quem está falando.
Na prática: comércio eletrônico, banco, login, API, e-mail, atualização de software,
e — cada vez mais — simplesmente tudo, porque provedores e governos injetavam
publicidade e rastreadores em páginas HTTP em claro.

**O que faz?** Quatro coisas, nesta ordem: (1) negocia qual versão e quais algoritmos
os dois lados usarão; (2) combina uma chave secreta compartilhada sem nunca transmiti-la;
(3) verifica a identidade do servidor por certificado; (4) cifra e autentica cada
pedaço de dado dali em diante, com números de sequência para impedir reordenação e repetição.

**Como configurar?** Está em [03-instalacao.md](03-instalacao.md) (instalar),
[04-como-comecar.md](04-como-comecar.md) (primeiro HTTPS no ar),
[16-acme-e-automacao.md](16-acme-e-automacao.md) (certificado real e automático) e
[17-configuracao-de-servidores.md](17-configuracao-de-servidores.md) (nginx, Apache,
Caddy, HAProxy, Node, Python — com configuração completa e comentada).

---

## 9. Se você só vai ler um arquivo deste curso

Faça isto agora, num terminal, e leia a saída (é seguro, só mostra informação):

```bash
curl -sv https://example.com -o /dev/null 2>&1 | grep -Ei "SSL connection|subject|issuer|ALPN|TLSv"
```

Você verá a versão do TLS negociada, a cifra escolhida, o dono do certificado
(*subject*) e quem o emitiu (*issuer*). Em três segundos você viu, na vida real,
tudo o que este arquivo descreveu.

---

## Autoteste

1. Quais são os três problemas do "cartão-postal" e qual garantia do TLS resolve cada um?
2. TLS impede que um atacante altere os bytes no caminho? Justifique.
3. O que o cadeado do navegador garante e o que ele **não** garante?
4. Por que o servidor precisa de um certificado, e por que o navegador (em geral) não precisa?
5. Um observador da rede que vê você acessando um site por HTTPS descobre o quê?
6. Qual é a diferença entre SSL e TLS?
7. Por que a criptografia do TLS não é a mesma coisa que a criptografia ponta a ponta do Signal?
8. Um site de golpe pode ter cadeado verde? Por quê?

*Respostas: §2, §2 (integridade detecta, não impede), §5, §6, §5, §5, §5, §5.*

---

**Próximo:** [02-pre-requisitos.md](02-pre-requisitos.md) — o que ter e saber antes de pôr a mão.
