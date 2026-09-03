# 01 · Docker e containers para quem nunca ouviu falar

`Nível: iniciante` · `Sem jargão` · `Última atualização: 11/08/2026`

---

## A pergunta que dá origem a tudo

Um programa nunca roda sozinho. Ele depende de outras coisas: uma versão específica de uma
linguagem, um punhado de bibliotecas, arquivos de configuração, variáveis de ambiente, um
banco de dados do outro lado da rede. Esse conjunto de dependências é invisível quando tudo
funciona e é a origem de quase todo sofrimento quando não funciona.

A frase que resume o problema é conhecida e antiga:

> **"Na minha máquina funciona."**

Ela não é preguiça nem má-fé. É uma constatação verdadeira: o programa realmente funciona na
máquina de quem escreveu — porque *aquela* máquina tem exatamente as versões, os caminhos e as
configurações de que ele precisa. Em outra máquina, uma dessas coisas é diferente, e o programa
quebra.

Docker existe para resolver isso de um jeito específico: **em vez de tentar deixar todas as
máquinas iguais, você empacota o programa junto com tudo de que ele precisa e leva o pacote
inteiro para onde quiser**.

---

## A analogia do contêiner de navio

Antes dos anos 1950, carregar um navio era um pesadelo artesanal. Cada mercadoria tinha
formato próprio: sacas de café, barris, engradados, caixas soltas. Estivadores empilhavam
tudo à mão. Carregar e descarregar um navio levava dias, quebrava carga, e cada porto tinha
seu jeito.

Aí veio Malcom McLean com uma ideia entediante e revolucionária: **uma caixa metálica de
tamanho padronizado**. Não interessa o que tem dentro — café, geladeiras, parafusos. Por
fora, todo contêiner é igual. E porque é igual por fora, o guindaste do porto de Santos é
igual ao de Roterdã, o encaixe do caminhão é igual ao do vagão de trem, e o navio é
projetado para encaixar contêineres, não para acomodar sacas.

O ganho não veio da caixa. Veio da **interface padronizada** entre a carga e o mundo.

Um *container* de software é a mesma ideia:

| Mundo físico | Mundo do software |
|---|---|
| A carga (café, geladeira) | Sua aplicação e suas bibliotecas |
| A caixa metálica padronizada | A **imagem** do container |
| O guindaste, o caminhão, o navio | Docker, Kubernetes, o servidor na nuvem |
| "Cabe em qualquer porto" | "Roda em qualquer máquina com um runtime de container" |

E o mesmo alerta vale: **um contêiner não protege a carga de tudo**. Se o navio afundar, ele
afunda junto. Voltaremos a isso quando falarmos de segurança e isolamento.

---

## Então o que é, tecnicamente, um container?

Um container é **um processo comum do sistema operacional que foi enganado**.

Não há mágica, não há máquina virtual, não há emulação. Quando você roda um container, o
sistema operacional inicia um processo normal — como um navegador ou um editor de texto — e
então mente para ele sobre três coisas:

1. **O que ele enxerga.** O processo acha que o sistema de arquivos inteiro é uma pastinha que
   você preparou. Acha que só existem ele e seus filhos rodando na máquina. Acha que tem uma
   placa de rede só dele, com IP próprio. Nada disso é verdade; é uma visão recortada.
2. **Quanto ele pode consumir.** Você diz "esse processo usa no máximo 512 MB de memória e meio
   núcleo de CPU", e o sistema operacional obriga.
3. **O que ele pode fazer.** Você tira dele permissões perigosas — mudar o relógio do sistema,
   carregar módulos do kernel, mexer em dispositivos.

O nome técnico da primeira mentira é **namespace**; da segunda, **cgroup**; da terceira,
**capabilities** e **seccomp**. Todos os três são recursos do **kernel** do Linux — o núcleo do
sistema operacional, o programa que fala com o hardware e arbitra quem usa o quê.

> **Definição informal:** um container é um processo isolado por namespaces, limitado por
> cgroups e restringido por políticas de segurança, executando a partir de um sistema de
> arquivos empacotado (a imagem).

Isso tem uma consequência que muita gente demora a internalizar:

> **Não existe "dentro do container".** Do lado de fora, no `htop` do servidor, o processo do
> seu container aparece como qualquer outro processo, com PID normal. Ele só *acha* que está
> num mundo separado.

---

## E o Docker, o que é?

Docker é a **ferramenta** que torna isso usável por gente normal.

Os recursos do kernel que citei existiam desde 2006–2008. Ninguém os usava diretamente porque
era terrivelmente trabalhoso: você precisava montar o sistema de arquivos à mão, configurar
namespaces com chamadas de sistema, escrever regras de rede. Era possível, mas era artesanal.

Em 2013, o Docker apareceu com três coisas juntas — e é a **combinação** que mudou o mundo,
não cada peça isolada:

1. **Um formato de empacotamento com camadas** — a *imagem*, que você constrói uma vez e
   distribui.
2. **Um jeito de descrever a construção em texto** — o *Dockerfile*, versionável no Git ao lado
   do código.
3. **Um lugar público para guardar e baixar imagens** — o *registry* (Docker Hub), que fez
   `docker run nginx` funcionar sem você saber nada de nginx.

O comando ficou tão simples que virou trivial:

```bash
docker run -d -p 8080:80 nginx
```

Uma linha, e você tem um servidor web funcionando em `http://localhost:8080`. Sem instalar
nginx, sem configurar nada, sem sujar sua máquina. E quando terminar, você apaga o container e
não sobra rastro.

---

## Os três substantivos que você precisa separar

Este é o ponto onde quase todo iniciante se enrola. Preste atenção porque tudo depende disso.

| Termo | O que é | Analogia de programação | Analogia do dia a dia |
|---|---|---|---|
| **Dockerfile** | Um arquivo de texto com a receita de como montar a imagem | Código-fonte | A receita de bolo escrita |
| **Imagem** | O pacote pronto, imutável, em camadas | Binário compilado | O bolo assado e congelado |
| **Container** | Uma instância em execução de uma imagem | Processo rodando | A fatia servida no prato |

Três consequências práticas dessa separação:

- **Uma imagem gera muitos containers.** Assim como um executável gera muitos processos. Você
  pode rodar 50 containers da mesma imagem `nginx` ao mesmo tempo, e eles não se conhecem.
- **A imagem não muda.** Nunca. É imutável por construção. Se você precisa de uma versão nova,
  constrói **outra** imagem. Isso é o que torna "voltar atrás" trivial: você aponta para a
  imagem antiga.
- **O container é descartável.** Se você editar um arquivo dentro de um container e depois
  apagar o container, a edição some. Isso é intencional, e é a causa do erro nº 1 de iniciante:
  perder dados de banco. (Solução: *volumes* — veja [15-armazenamento-e-volumes.md](15-armazenamento-e-volumes.md).)

---

## Container não é máquina virtual

Essa é a comparação mais útil que existe, então vale um diagrama.

```
        MÁQUINA VIRTUAL                          CONTAINER
   ┌───────┬───────┬───────┐             ┌───────┬───────┬───────┐
   │ App A │ App B │ App C │             │ App A │ App B │ App C │
   ├───────┼───────┼───────┤             ├───────┼───────┼───────┤
   │ libs  │ libs  │ libs  │             │ libs  │ libs  │ libs  │
   ├───────┼───────┼───────┤             ├───────┴───────┴───────┤
   │  SO   │  SO   │  SO   │  ~1-10 GB   │   runtime (Docker)    │  ~5-200 MB
   │kernel │kernel │kernel │   cada      ├───────────────────────┤   cada
   ├───────┴───────┴───────┤             │                       │
   │      Hypervisor       │             │  Sistema Operacional  │  ← UM kernel
   ├───────────────────────┤             │   do host (kernel)    │    compartilhado
   │       Hardware        │             ├───────────────────────┤
   └───────────────────────┘             │       Hardware        │
                                         └───────────────────────┘
      Inicia em: minutos                    Inicia em: milissegundos
      Isola em: hardware virtual             Isola em: recursos do kernel
```

A diferença essencial está numa linha só: **a VM traz seu próprio kernel; o container usa o
kernel do host.**

Disso decorre tudo:

| | Máquina virtual | Container |
|---|---|---|
| Tempo de partida | segundos a minutos | milissegundos |
| Tamanho típico | 1–10 GB | 5–500 MB |
| Quantos cabem numa máquina | dezenas | centenas a milhares |
| Isolamento | forte (barreira de hardware) | mais fraco (barreira de software) |
| Pode rodar outro SO? | sim (Windows sobre Linux) | não (mesmo kernel) |
| Uso típico | separar clientes, multi-inquilino hostil | separar aplicações da mesma organização |

**A troca é honesta e explícita:** você ganha velocidade e densidade, e paga com isolamento
mais fraco. Se um atacante escapar de um container, ele cai no host — não numa segunda barreira.
Por isso provedores de nuvem que rodam código de terceiros desconhecidos (AWS Lambda, por
exemplo) colocam containers **dentro** de micro-VMs. O detalhe está em [20-seguranca.md](20-seguranca.md).

---

## Por que isso pegou tanto?

Três razões, em ordem de importância na minha experiência:

**1. Acabou com a diferença entre desenvolvimento e produção.**
Antes, "funciona no meu Ubuntu, quebra no RHEL do servidor" era rotina. Com container, o
artefato que você testou é *bit a bit* o mesmo que roda em produção. Não é "parecido": é o
mesmo.

**2. Fez o software virar um artefato distribuível.**
`docker run postgres:16` sobe um Postgres funcionando em 10 segundos, sem ler manual. Isso
transformou a economia de experimentar tecnologia. Você testa cinco bancos de dados numa tarde.

**3. Tornou possível o resto da infraestrutura moderna.**
Kubernetes, CI/CD moderno, microserviços e boa parte do que se chama de "cloud native" só
existem porque há um artefato padronizado embaixo. Container é a peça de LEGO; o resto é o que
se constrói com ela.

---

## E onde isso não serve?

Honestidade profissional, porque a propaganda costuma omitir:

- **Se você tem uma aplicação só, num servidor só, e ela funciona** — containerizar adiciona
  complexidade e não resolve problema nenhum. Faça se quiser aprender, não porque "é o certo".
- **Se você precisa de isolamento forte contra código hostil** — use VM ou micro-VM.
- **Se você precisa de um kernel diferente** — driver especial, versão específica, outro SO.
  Container não faz isso, por definição.
- **Desktop gráfico, áudio, USB, GPU exclusiva** — dá para fazer, mas dói. Frequentemente uma VM
  é menos sofrimento.
- **macOS e Windows** — containers Linux rodam ali dentro de uma VM escondida. Funciona bem, mas
  a performance de disco é notavelmente pior, e isso derruba projetos com muitos arquivos
  pequenos (`node_modules`, por exemplo).

*Opinião profissional, não consenso:* a maior parte das equipes pequenas que adotou
microserviços em containers teria vivido melhor com um monólito bem feito, containerizado num
único serviço. Container é ótimo; microserviço é uma decisão organizacional cara e independente.

---

## O vocabulário mínimo, tudo definido

| Termo | Definição de uma linha |
|---|---|
| **Kernel** | O núcleo do sistema operacional: fala com o hardware e arbitra recursos entre processos. |
| **Processo** | Um programa em execução, com seu espaço de memória. |
| **Namespace** | Recurso do kernel Linux que recorta o que um processo enxerga (arquivos, rede, outros processos). |
| **cgroup** | *control group* — recurso do kernel que limita quanto um processo pode consumir. |
| **Imagem** | Pacote imutável com o sistema de arquivos e os metadados da aplicação. |
| **Camada** (*layer*) | Um pedaço da imagem; imagens são pilhas de camadas reaproveitáveis. |
| **Container** | Instância em execução de uma imagem. |
| **Dockerfile** | Arquivo texto que descreve como construir uma imagem. |
| **Registry** | Servidor que armazena e distribui imagens (ex.: Docker Hub, GHCR). |
| **Volume** | Área de disco gerenciada pelo Docker que sobrevive à morte do container. |
| **Docker Compose** | Ferramenta que sobe vários containers juntos a partir de um arquivo YAML. |
| **Orquestrador** | Sistema que decide onde e quantos containers rodar num conjunto de máquinas (ex.: Kubernetes). |
| **OCI** | *Open Container Initiative* — o padrão aberto de formato de imagem e de runtime. |

O glossário completo está em [GLOSSARIO.md](GLOSSARIO.md).

---

## O que fazer agora

1. Se quer só experimentar sem instalar nada → há um caminho no
   [03-instalacao.md](03-instalacao.md), seção "Alternativa sem instalar nada".
2. Se quer instalar → [02-pre-requisitos.md](02-pre-requisitos.md) e depois
   [03-instalacao.md](03-instalacao.md).
3. Se quer entender por dentro antes de mexer → [10-fundamentos.md](10-fundamentos.md).

---

## Autoteste

1. Explique, sem usar a palavra "container", o problema que o Docker resolve.
2. Qual é a única diferença estrutural entre uma VM e um container, da qual todas as outras
   decorrem?
3. Se uma imagem é imutável, como se corrige um bug numa aplicação containerizada?
4. Você edita um arquivo dentro de um container em execução e depois roda `docker rm`. O que
   acontece com a edição, e por quê?
5. Por que `docker run nginx` funciona mesmo numa máquina onde o nginx nunca foi instalado?
6. Cite duas situações em que usar container é a escolha errada, e justifique cada uma.
7. Namespace e cgroup resolvem problemas diferentes. Quais?
