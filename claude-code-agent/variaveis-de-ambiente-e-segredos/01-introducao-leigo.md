# 01 · O que é isso, para um leigo total

`Nível: iniciante` · `Atualizado em: 14/08/2026`

---

## A pergunta que originou este curso

> "No desenvolvimento eu criei um arquivo `.env` com senhas e chaves.
> Quando o sistema vai para o cliente, para produção, o que se faz com esse arquivo?"

A resposta curta, para você já saber onde vamos chegar:

> **O arquivo `.env` não vai.**
> O que vai é o **conteúdo** dele — e por um caminho diferente, escolhido conforme
> onde o sistema roda. O `.env` é uma **conveniência de desenvolvimento**, não um
> formato de entrega.

O resto deste curso é o porquê, o como, e os dez jeitos diferentes de fazer isso
certo em Node, PHP, Python, Java, contêiner, servidor Linux, nuvem e na máquina do cliente.

---

## 1. A analogia: o crachá e o cofre

Imagine que o seu programa é um **funcionário novo** que chega todo dia de manhã
no escritório para trabalhar.

Para trabalhar, ele precisa de coisas:

- Saber **em qual andar** ele vai trabalhar hoje (o escritório de testes ou o de verdade).
- A **chave do arquivo** onde estão os documentos (a senha do banco de dados).
- O **cartão corporativo** para pagar coisas em nome da empresa (a chave da API de pagamento).

Existem quatro maneiras de dar isso a ele:

| Maneira | O que é, na prática |
|---|---|
| **Tatuar na testa dele** | escrever a senha dentro do código-fonte |
| **Escrever num papel no bolso do casaco dele** | colocar num arquivo `.env` que viaja junto com o programa |
| **Entregar na portaria, todo dia, quando ele chega** | variáveis de ambiente injetadas pelo sistema no momento em que o programa inicia |
| **Dar a ele um crachá que abre o cofre, e o cofre entrega o que ele precisa na hora** | um **cofre de segredos** (Vault, AWS Secrets Manager…) que ele consulta em tempo de execução |

Tatuar na testa é o pior: a tatuagem vai junto quando ele muda de emprego
(o código vai para o GitHub, e a senha vai junto).

O papel no bolso é o `.env`: bom para o estágio, mas o casaco fica largado em
qualquer lugar, e qualquer um que pegue o casaco tem a senha.

A entrega na portaria é o **jeito padrão em produção**.

O cofre é o jeito de quem tem muitos funcionários, muitos andares e auditoria.

Este curso te leva do papel no bolso até o cofre — passando por cada degrau,
sabendo por que cada degrau existe e quanto ele custa.

---

## 2. Definindo as palavras (sem jargão ainda)

### Configuração

Tudo aquilo que **muda entre um lugar de execução e outro**, sem que o programa mude.

O mesmo programa roda:

- no seu notebook, falando com um banco de dados de brincadeira;
- no servidor de testes da empresa, falando com um banco de dados de testes;
- no servidor do cliente, falando com o banco de dados de verdade.

O **código é o mesmo**. O que muda é o **endereço do banco, o usuário e a senha**.
Isso é configuração.

> **Teste prático para saber se algo é configuração:**
> se o valor for diferente entre o seu notebook e o servidor do cliente, é configuração.
> Se for igual em todos os lugares, não é — é código, e pode ficar no código.

### Segredo

Um pedaço de configuração que **causa prejuízo se alguém de fora souber**.

Exemplos: senha do banco, chave de API do gateway de pagamento, chave privada de
assinatura, token de acesso ao serviço de e-mail.

Nem toda configuração é segredo. `PORT=3000` é configuração e não é segredo.
`DATABASE_PASSWORD=xyz` é as duas coisas.

Essa distinção importa muito: **segredo e não-segredo seguem caminhos diferentes
em produção**. Confundir os dois é a origem de metade dos problemas.

### Variável de ambiente

Um par **nome = valor** que o sistema operacional entrega ao programa **no instante
em que o programa é iniciado**.

Você já usa uma sem saber: quando você digita `git` no terminal e ele funciona,
é porque existe uma variável de ambiente chamada `PATH` dizendo em quais pastas
o sistema deve procurar programas.

Veja as suas agora (Linux/macOS):

```bash
printenv | head -20
```

Ou no Windows PowerShell:

```powershell
Get-ChildItem Env: | Select-Object -First 20
```

Cada linha ali é uma variável de ambiente. Elas não estão "num arquivo" — estão
na memória do processo do seu terminal, e são copiadas para todo programa que ele inicia.

### Arquivo `.env`

Um arquivo de texto, com uma linha `NOME=valor` por vez, que **uma biblioteca lê e
converte em variáveis de ambiente** quando o programa começa.

```
DATABASE_URL=postgres://app:senha123@localhost:5432/loja
STRIPE_SECRET_KEY=sk_test_51Abc...
PORT=3000
```

Repare em duas coisas:

1. O `.env` **não é uma tecnologia do sistema operacional**. É uma convenção
   inventada por programadores. O Linux não sabe o que é um `.env`.
2. Ele existe **só para simular, no seu notebook, a entrega que em produção
   é feita de outro jeito**.

Essa segunda frase é a chave de todo o curso.

---

## 3. Por que isso virou um problema famoso

Antes de 2011, a prática comum era ter arquivos como:

```
config/database.dev.php
config/database.staging.php
config/database.prod.php
```

todos versionados no repositório, com senhas dentro. O programa escolhia qual ler
conforme uma flag. Funcionava — e vazou o mundo inteiro.

Em 2011, Adam Wiggins (co-fundador do Heroku) publicou o
[**The Twelve-Factor App**](https://12factor.net/pt_br/config), um manifesto de doze
regras para aplicações que rodam na nuvem. O **Fator III** diz:

> *"Armazene as configurações no ambiente."*

A justificativa dele, em uma frase que vale citar:

> *"Um teste decisivo para saber se uma aplicação tem todas as configurações
> corretamente fatoradas fora do código é verificar se a base de código poderia
> ter seu código aberto a qualquer momento, sem comprometer nenhuma credencial."*

Faça esse teste agora, mentalmente, no seu projeto. Se você tornasse o repositório
público neste minuto, vazaria alguma coisa? Se sim, você tem trabalho a fazer —
e este curso é sobre isso.

A partir daí, a comunidade criou bibliotecas `.env` em toda linguagem
(`dotenv` em Node, `python-dotenv`, `phpdotenv`, `dotenv` em Ruby…) e a prática se
espalhou. **Mas a biblioteca `.env` foi criada para o desenvolvimento local, e um
número enorme de pessoas passou a usá-la em produção sem perceber que estava
resolvendo um problema diferente.**

É exatamente aí que você está agora, ao fazer a pergunta.

---

## 4. Os quatro erros que quase todo mundo comete uma vez

Não é vergonha: praticamente todo desenvolvedor faz pelo menos um destes.

**Erro 1 — commitar o `.env`.**
Você adiciona ao Git sem pensar. Meses depois o repositório fica público, ou um
ex-funcionário sai com uma cópia, ou um robô que varre o GitHub encontra a chave.
Robôs encontram chaves da AWS em **menos de um minuto** depois do push.
Não é lenda urbana; é o modo de operação padrão da indústria de mineração de chaves.

**Erro 2 — mandar o `.env` por WhatsApp/Slack/e-mail para o colega.**
O segredo agora existe em um servidor que não é seu, indexado, com backup, para sempre.

**Erro 3 — colocar segredo no `.env` do front-end.**
Em React, Vue, Angular, Next.js, Vite: variáveis com prefixos como `VITE_`,
`NEXT_PUBLIC_`, `REACT_APP_` são **embutidas no arquivo JavaScript que vai para o
navegador**. Qualquer visitante do site lê com Ctrl+U. Não existe segredo no front-end.
Isso tem arquivo próprio neste curso: [20-frontend-e-build-time.md](20-frontend-e-build-time.md).

**Erro 4 — copiar o `.env` para o servidor do cliente via `scp` e considerar o
assunto resolvido.**
Funciona. É melhor do que o Erro 1. Mas cria um arquivo de senhas em texto puro
num servidor, sem controle de quem leu, sem rotação, sem auditoria, e que ninguém
lembra que existe até o dia do incidente. Para muitos projetos pequenos é aceitável —
**desde que seja uma escolha consciente**, com permissão de arquivo correta e
dono correto, não um acidente. Este curso mostra como fazer isso direito e quando
não basta.

---

## 5. O mapa da resposta, em uma imagem

```
                      ┌──────────────────────────────┐
                      │   Onde o valor MORA          │
                      └──────────────────────────────┘

  DESENVOLVIMENTO                    PRODUÇÃO
  ───────────────                    ────────

  arquivo .env                       ┌── servidor Linux próprio
  na sua máquina,                    │   → systemd EnvironmentFile (chmod 600)
  fora do Git                        │
        │                            ├── contêiner Docker
        │                            │   → -e / --env-file / Docker secrets
        │  MESMO CÓDIGO,             │
        │  MESMAS VARIÁVEIS  ──────► ├── Kubernetes
        │                            │   → Secret + External Secrets Operator
        │                            │
        │                            ├── PaaS (Heroku, Render, Vercel, Railway)
        │                            │   → painel/CLI do provedor
        │                            │
        │                            ├── serverless (Lambda, Cloud Run)
        │                            │   → configuração da função + cofre
        │                            │
        │                            └── máquina do CLIENTE (on-premise)
        │                                → instalador que pergunta e grava
        │                                  com permissão restrita
        ▼
  process.env.DATABASE_URL   ←  o código NUNCA sabe de onde veio
  os.environ["DATABASE_URL"]
  $_ENV['DATABASE_URL']
```

A linha inferior é o ponto inteiro: **seu código lê variável de ambiente e pronto**.
Quem coloca a variável lá muda conforme o lugar. Se o seu código chama
`dotenv.config()` obrigatoriamente, você amarrou o programa ao `.env` e perdeu
essa liberdade — e é isso que se conserta.

---

## 6. O que você vai saber ao terminar este curso

- Por que variável de ambiente existe, desde a chamada de sistema `execve` do Unix.
- Como entregar configuração em **Node, PHP, Python, Java, .NET, Go e Ruby**,
  com o código de cada um.
- Como fazer isso em **systemd, Docker, Docker Compose, Kubernetes, PaaS,
  serverless, hospedagem compartilhada de PHP e na máquina do cliente**.
- Por que `NEXT_PUBLIC_` não é segredo, e o que fazer no lugar.
- O que é um cofre de segredos, quanto custa cada um (com preços de agosto de 2026)
  e quando ele não vale a pena.
- Como **rotacionar** um segredo sem derrubar o sistema.
- O que fazer nas primeiras duas horas depois de um vazamento — na ordem certa.
- Por que o `git filter-repo` sozinho **não resolve** um segredo vazado.
- A teoria: criptografia de envelope, KMS, o **problema do segredo zero**,
  identidade de carga de trabalho (SPIFFE), atestação.

---

## Autoteste

1. Explique, sem usar a palavra "arquivo", o que é uma variável de ambiente.
2. Dê um exemplo de configuração que **não** é segredo e um que é.
3. Qual é o "teste decisivo" do Twelve-Factor para saber se a configuração está
   corretamente separada do código?
4. Por que o `.env` não é uma tecnologia do sistema operacional?
5. Uma chave de API colocada em `REACT_APP_STRIPE_KEY` está protegida? Por quê?
6. Se `.env` não vai para produção, o que vai no lugar dele?
7. Por que copiar o `.env` para o servidor com `scp` é "melhor que commitar, mas
   ainda insuficiente"? Cite dois problemas que isso deixa em aberto.

---

**Fontes consultadas:** [12factor.net/pt_br/config](https://12factor.net/pt_br/config) ·
consultado em 14/08/2026.

**Próximo:** [02-pre-requisitos.md](02-pre-requisitos.md) · Voltar ao [mapa](00-MAPA.md)
