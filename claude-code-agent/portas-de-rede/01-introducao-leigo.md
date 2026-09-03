# 01 · O que é uma porta de rede

**Nível:** iniciante — zero jargão · **Última atualização:** 14/08/2026

---

## O problema que existia antes de a porta existir

Sua máquina tem **um** endereço na rede. Um só. É o endereço IP — algo como `192.168.0.15`.
É o equivalente ao número da sua casa na rua.

Agora conte quantos programas na sua máquina falam com a internet **ao mesmo tempo**,
neste exato momento: o navegador (com 30 abas), o cliente de e-mail, o Spotify, o backup na
nuvem, o relógio se sincronizando, o antivírus baixando assinaturas, o VS Code conversando
com um servidor, e mais uma dúzia que você não sabe que existem.

Um endereço. Vinte programas. Chega um pacote de dados no seu computador.

**Para qual deles?**

Essa é a pergunta inteira. A porta é a resposta.

---

## A analogia certa (e por que a comum é ruim)

Quase todo texto começa com: *"Imagine que o IP é o endereço do prédio e a porta é o
apartamento."*

Essa analogia está **quase** certa, e o "quase" atrapalha. Porque ela sugere que a porta é
um lugar físico, que existe fixo, que está lá esperando — como o apartamento 302 existe
mesmo quando ninguém mora nele. E não é assim: **uma porta não existe até que um programa
peça para usá-la, e deixa de existir no instante em que esse programa morre.**

A analogia melhor é a **caixa postal com número, dentro de uma empresa**:

> Uma empresa tem um endereço na rua: *Rua das Flores, 100*. Isso é o IP.
> Dentro dela existem várias caixas postais numeradas. Uma carta endereçada a
> "Rua das Flores, 100 — caixa 25" vai para o setor financeiro. "Caixa 80" vai para o
> atendimento ao público.
>
> Mas — e este é o ponto — **a caixa 25 só é atendida se alguém do financeiro tiver
> assumido aquela caixa hoje.** Se ninguém assumiu, a carta volta com um carimbo:
> *"caixa não atendida"*. E se o funcionário do financeiro for embora, a caixa 25 fica
> livre para outro setor pegar amanhã.

Guarde três coisas dessa imagem, porque elas são as três verdades do assunto:

1. **O número é só um crachá.** Não há nada de "financeiro" na caixa 25. Ela é do financeiro
   porque combinaram assim, não porque a caixa tem algo de especial.
2. **A caixa só funciona se alguém a assumiu.** Um programa precisa estar rodando e ter
   pedido aquele número. Sem isso, o número está lá, mas ninguém atende.
3. **Quem assume, atende — e ninguém mais pode assumir aquela caixa ao mesmo tempo.**

---

## Então: o que é uma porta, em uma frase

> Uma porta é um **número de 16 bits** (de 1 a 65535) que acompanha cada pacote de dados,
> e que serve para o sistema operacional saber a qual programa entregar aquele pacote.

Só isso. Não é hardware. Não é um buraco na máquina. Não é uma configuração de rede.
É um **número dentro do pacote**, e uma **tabela dentro do sistema operacional** que
associa números a programas.

Se você abrir um pacote de rede e olhar os bytes, vai ver isso, literalmente:

```
… [ endereço de origem: 192.168.0.15 ] [ endereço de destino: 142.250.79.14 ]
  [ porta de origem: 51234 ] [ porta de destino: 443 ] [ os dados ]
```

Quatro campos que importam. Guarde os quatro — o [`10-fundamentos.md`](10-fundamentos.md)
vai chamá-los de **quádrupla**, e eles explicam tudo.

---

## Por que 65535?

Porque o campo no cabeçalho do pacote tem **16 bits**. Dois elevado a 16 é 65 536, e o
número 0 é reservado. Fim.

E por que 16 bits e não 32? Porque em **1980**, quando o formato foi congelado no
RFC 768 (UDP) e no RFC 793 (TCP), cada bit no cabeçalho custava tempo de transmissão em
linhas de 50 kbit/s, e 65 mil serviços simultâneos por máquina parecia absurdamente
generoso — um mainframe da época rodava talvez uma dúzia. Foi uma decisão de engenharia
razoável em 1980 que hoje, em servidores muito carregados, **aperta**. Voltaremos a esse
aperto no [`60-teoria-avancada.md`](60-teoria-avancada.md), porque ele é real e custa
dinheiro em empresas grandes.

Isso é um exemplo do que este curso vai fazer o tempo todo: perguntar *"por que é assim?"*
até chegar a uma decisão humana datada, e não parar em *"porque o padrão define"*.

---

## As duas pontas: quem espera e quem chega

Aqui está a distinção que, sozinha, resolve metade da confusão dos iniciantes.

Toda conversa de rede tem **dois** lados, e a porta tem papel diferente em cada um.

### O lado que espera — o servidor

Um programa diz ao sistema operacional: *"a partir de agora, tudo que chegar para a porta
80 é meu"*. Ele **reserva** o número.

- Esse número é **escolhido e fixo**. Precisa ser, senão ninguém saberia onde te procurar.
- É por isso que existem convenções: 80 é web, 22 é acesso remoto, 3306 é banco MySQL.
- Um programa nessa situação está **"escutando"** (*listening*). É o que você vê quando roda
  `ss -tulpn`.

### O lado que chega — o cliente

Seu navegador quer falar com o Google. Ele precisa de uma porta **de origem** para receber a
resposta de volta. Mas ele não liga para qual número seja — ninguém vai procurá-lo.

- Então ele pede: *"me dê qualquer número livre"*, e o sistema entrega um da faixa alta —
  nesta máquina, entre **32768 e 60999**.
- Cada aba do navegador pega um número diferente. É assim que as respostas não se misturam.
- Essas portas são chamadas **efêmeras** (*ephemeral*): duram o tempo da conversa e voltam
  para o bolo.

**Consequência prática que quase ninguém enuncia:** quando você roda `ss -tulpn` e vê 30
portas altas estranhas, na maioria das vezes **não** são serviços abertos. São seu navegador
e seus programas conversando para fora. Um "serviço aberto" é só o que aparece como `LISTEN`.

---

## O que é "protocolo" nisso tudo

A pergunta "qual o protocolo da porta?" tem duas respostas, em dois níveis, e confundir os
dois é o erro nº 1 do assunto.

### Nível 1 — o protocolo de transporte: TCP ou UDP

É quem **carrega** o número da porta. Existem dois principais:

| | **TCP** | **UDP** |
|---|---|---|
| Analogia | Ligação telefônica | Cartão-postal |
| Antes de falar | Cumprimenta e combina ("handshake") | Manda e pronto |
| Se um pedaço se perde | Reenvia, garantido | Perdeu, perdeu |
| Ordem de chegada | Garantida | Não garantida |
| Custo | Mais lento para começar | Instantâneo |
| Quem usa | Web, e-mail, SSH, bancos de dados | DNS, vídeo ao vivo, jogos, VPN |

**E aqui está o detalhe que quase todo material erra:** a porta 80 de TCP e a porta 80 de UDP
são **duas portas diferentes**. Numeração separada, tabelas separadas. Podem estar ocupadas
por programas completamente distintos ao mesmo tempo, sem nenhum conflito.

O caso mais importante disso hoje: **443/TCP é HTTPS clássico e 443/UDP é HTTP/3 (QUIC)**.
O mesmo site, o mesmo número, dois transportes. Se seu firewall libera "443" achando que é
uma coisa só, ele está errado — e é exatamente por isso que muitas redes corporativas
acidentalmente bloqueiam HTTP/3 até hoje.

### Nível 2 — o protocolo de aplicação: HTTP, SSH, SMTP…

É a **língua** que os dois programas falam depois que o transporte conectou. HTTP, SSH,
SMTP, DNS, Modbus, e mais mil.

E a verdade desconfortável: **o número da porta não obriga nada.** É uma convenção, não uma
lei. Você pode rodar um servidor SSH na porta 443. Pode rodar um site na porta 22. A rede
não se importa; nenhuma verificação impede. O número é uma **placa na parede**, e placas
podem estar erradas ou mentir de propósito.

Isso tem duas consequências que atravessam o curso inteiro:

- **Para quem administra:** trocar o SSH da 22 para a 2222 não é segurança. É reduzir ruído
  de log. Vale a pena, mas por outro motivo.
- **Para quem investiga:** você não pode concluir "é HTTP porque está na 80". Precisa
  **perguntar ao serviço** — é o que `nmap -sV` faz, e é o assunto do
  [`17-descoberta-e-varredura.md`](17-descoberta-e-varredura.md).

---

## Verificar as portas: as duas perguntas diferentes

Você perguntou "como se verifica". Existem **duas** formas, e elas não respondem à mesma
pergunta. Confundi-las produz relatório errado.

### Forma 1 — perguntar ao próprio sistema (de dentro)

> *"Sistema, quais programas seus reservaram portas?"*

```bash
ss -tulpn          # Linux
```

- **Vantagem:** é a verdade absoluta. O kernel não mente sobre a própria tabela.
- **Limite:** só funciona na máquina onde você está, e você precisa de permissão.
- **Serve para:** inventário, auditoria da sua frota, achar o processo que ocupou a porta.

### Forma 2 — bater na porta pela rede (de fora)

> *"Alô, tem alguém na porta 80 daquela máquina?"*

```bash
nmap <alvo>
```

- **Vantagem:** funciona contra qualquer máquina alcançável, e mostra o que o **atacante** vê.
- **Limite:** a resposta passa por firewalls, NAT e proxies. Ela é a verdade **do caminho**,
  não a verdade da máquina.
- **Serve para:** validar se o firewall funciona, testar a exposição real.

**As duas discordando é informação, não erro.** Um exemplo real, medido na máquina onde este
curso foi escrito:

| Ferramenta | Portas reportadas em `127.0.0.1` |
|---|---|
| `ss` (de dentro) | 8 portas com programa escutando |
| `nmap` (de fora) | 25 portas "abertas" |

Dezessete portas onde `nmap` conecta e **nenhum programa está escutando**. Isso não é bug de
nenhum dos dois: é a assinatura de algo interceptando conexões no caminho — um agente de
segurança corporativo, um proxy transparente, ou um sistema de detecção. O caso completo
está no [README do projeto-modelo](07-projeto-modelo/README.md).

---

## Para que servem as portas mais comuns

Um cartão de bolso. O catálogo completo, com ~120 entradas, está em
[`16-catalogo-de-portas.md`](16-catalogo-de-portas.md).

| Porta | Transporte | Serve para | Se você vê aberto na internet |
|---|---|---|---|
| **22** | TCP | Acesso remoto ao terminal (SSH) | Normal, se com chave e não senha |
| **53** | UDP e TCP | Traduzir nome em IP (DNS) | Só se você é um servidor DNS de propósito |
| **80** | TCP | Site sem criptografia (HTTP) | Aceitável só para redirecionar para 443 |
| **443** | TCP | Site com criptografia (HTTPS) | Normal |
| **443** | **UDP** | Site sobre HTTP/3 (QUIC) | Normal — e é outra porta |
| **25 / 587 / 465** | TCP | Envio de e-mail | Provavelmente errado, se não é servidor de e-mail |
| **3306** | TCP | Banco MySQL | **Grave.** Banco não fica na internet |
| **5432** | TCP | Banco PostgreSQL | **Grave.** Idem |
| **3389** | TCP | Área de trabalho remota do Windows | **Grave.** Alvo nº 1 de ransomware |
| **445** | TCP | Compartilhamento de arquivos Windows | **Grave.** Foi por aqui que o WannaCry entrou |
| **6379** | TCP | Redis | **Grave.** Sem senha por padrão até a versão 6 |
| **27017** | TCP | MongoDB | **Grave.** Sem autenticação por padrão até a 3.6 |

Repare no padrão: **quase tudo que é "grave" é um banco de dados ou um acesso remoto que
alguém deixou escapar sem querer**. Praticamente nenhum vazamento grande dos últimos dez anos
começou com um atacante genial. Começou com uma porta que ninguém sabia que estava aberta.

---

## Os três resultados de bater numa porta

Quando você testa uma porta pela rede, existem exatamente **três** desfechos possíveis.
Saber os três é o que separa quem diagnostica de quem chuta.

| Resultado | O que aconteceu tecnicamente | O que significa |
|---|---|---|
| **Aberta** | Veio um "pode falar" (SYN-ACK) | Existe um programa escutando ali |
| **Fechada** | Veio uma recusa explícita (RST) | A máquina existe e respondeu — mas ninguém escuta nessa porta |
| **Filtrada** | Não veio nada. Silêncio. | Um firewall engoliu seu pacote e não avisou ninguém |

A diferença entre "fechada" e "filtrada" é a informação mais subestimada do assunto:

- **Fechada** significa que a máquina está viva e falando com você.
- **Filtrada** significa que alguém no caminho decidiu que você não merece resposta.

Um firewall bem configurado faz seus pacotes sumirem (DROP) em vez de recusá-los (REJECT),
justamente para não confirmar que a máquina existe. Isso deixa a varredura lenta — cada porta
espera o *timeout* inteiro — e é a razão de `nmap` contra um alvo protegido demorar minutos
em vez de segundos.

---

## Erros que você vai cometer, e o que cada um quer dizer

Estas quatro mensagens cobrem talvez 90 % dos problemas com portas. Decore o significado,
não o texto.

| Mensagem | Tradução honesta | O que fazer |
|---|---|---|
| `Address already in use` | Outro programa já reservou esse número | `ss -tulpn \| grep :<porta>` para achar o culpado |
| `Connection refused` | Chegou lá, ninguém escuta | O serviço está mesmo rodando? Está no IP certo? |
| `Connection timed out` | Nada voltou | Firewall, rota errada, ou máquina desligada |
| `Permission denied` | Você tentou usar porta abaixo de 1024 sem privilégio | Use porta alta, ou dê o privilégio certo (não `sudo`) |

O `04-como-comecar.md` provoca as quatro de propósito, para você ver cada uma acontecer.

---

## Uma última coisa que ninguém te conta cedo o bastante

Você vai passar a vida ouvindo *"feche as portas desnecessárias"*. É bom conselho, mas está
mal formulado, e a formulação errada leva a trabalho errado.

**Você não fecha uma porta. Você para de abri-la.**

Porta não é uma válvula que você gira. Ela está aberta porque **um programa a abriu**. As
opções reais são três, em ordem de qualidade:

1. **Desligar o programa.** Se ninguém usa aquele serviço, ele não devia estar rodando.
   Isso resolve o problema e ainda economiza memória.
2. **Fazer o programa escutar só onde precisa.** Trocar `0.0.0.0:5432` por `127.0.0.1:5432`
   na configuração. A porta continua aberta — para a própria máquina, e para mais ninguém.
3. **Bloquear no firewall.** É a última opção, não a primeira. Firewall é uma camada por
   cima do problema, e camadas por cima falham: a regra some numa reinstalação, o container
   sobe com outra rede, alguém adiciona uma exceção "temporária".

A hierarquia é essa e é sempre essa: **desligue > restrinja o bind > filtre**.
Voltaremos a ela com detalhe no [`19-exposicao-e-seguranca.md`](19-exposicao-e-seguranca.md).

---

## Autoteste

1. Sua máquina tem um endereço IP. Por que ela precisa de portas, se o endereço já a
   identifica na rede?
2. Um colega diz: "a porta 8080 está aberta na minha máquina desde ontem". Que informação
   crítica falta nessa frase para você saber se é problema?
3. Um servidor tem 50 000 clientes conectados na porta 443. Como isso é possível, se
   "só um programa pode ocupar uma porta"? (Se travar, a resposta está no `10`.)
4. `nmap` diz que a porta 8080 de um servidor está *filtrada*. Seu colega conclui: "então
   não tem nada rodando lá". Ele está certo? Por quê?
5. Qual a diferença entre a porta 443/TCP e a porta 443/UDP? Elas podem estar ocupadas por
   programas diferentes ao mesmo tempo?
6. Por que trocar o SSH da porta 22 para a 2222 **não** é uma medida de segurança séria?
   E por que, ainda assim, muita gente faz — com um motivo legítimo?
7. Você precisa impedir que o Postgres da sua máquina seja acessado de fora. Enumere as três
   formas, em ordem da melhor para a pior, e diga por que essa é a ordem.

---

*Próximo: [`02-pre-requisitos.md`](02-pre-requisitos.md) — o que ter e saber antes de seguir.*
