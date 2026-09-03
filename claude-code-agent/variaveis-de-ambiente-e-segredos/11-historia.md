# 11 · História — como chegamos ao `.env` (e por que ele não deveria ir para produção)

`Nível: intermediário` · `Atualizado em: 14/08/2026`

Entender a linha do tempo resolve metade das dúvidas de projeto, porque quase toda
prática estranha de hoje é a cicatriz de um problema de ontem.

---

## Linha do tempo

```
1971  Unix V1        │ não há ambiente. Configuração = recompilar.
1979  Unix V7        │ execve() ganha envp[]; nasce `environ`. ⭐ A forma atual.
1988  POSIX.1        │ padroniza environ, getenv, e a convenção MAIÚSCULAS.
1990s CGI            │ o servidor web passa a requisição via variável de ambiente.
                     │ Primeira vez que dado do usuário entra no ambiente. Erro fundador.
1995  PHP            │ configuração em arquivo .php versionado. Padrão da década.
2005  Rails          │ database.yml — "não commite este arquivo". Ninguém obedece.
2007  Heroku fundada │ não há disco persistente; configuração PRECISA vir de fora.
2011  12-Factor App  │ ⭐ Fator III: "armazene as configurações no ambiente".
2012  dotenv (Ruby)  │ Brandon Keepers: simular o ambiente do Heroku LOCALMENTE.
2013  dotenv (Node), python-dotenv, phpdotenv — a ideia se espalha.
2013  Docker         │ `-e` e `--env-file`. O contêiner consagra o modelo.
2014  Shellshock     │ CVE-2014-6271: variável de ambiente vira execução de código.
2015  Vault 0.1      │ HashiCorp: cofre com credencial DINÂMICA.
2015  SOPS (Mozilla) │ criptografar valores e versionar no Git.
2016  K8s Secrets    │ …que são base64, e todo mundo confunde com criptografia.
2017  AWS Secrets Mgr│ cofre gerenciado; GCP e Azure seguem.
2019  GitHub secret scanning — a plataforma começa a caçar o que vazou.
2021  OIDC no CI     │ ⭐ fim da chave estática no pipeline.
2023  Vault → BUSL   │ agosto: a licença muda; nasce o fork OpenBao (Linux Foundation).
2023  Node 20.6      │ ⭐ `--env-file` nativo. A biblioteca dotenv vira opcional.
2025  IBM conclui a compra da HashiCorp; Vault Enterprise vira produto IBM.
2026  SOPS/ESO na CNCF, OpenBao 2.x, push protection do GitHub por padrão.
```

---

## 1. 1979 — o ambiente nasce, e nasce sem tipo

Antes do Unix V7, configuração era **recompilar**. Havia `#define PORTA 3000` no
código, e mudar a porta significava novo binário.

O V7 introduziu `execve` com `envp[]` e a global `environ`. A motivação original
não tinha nada de configuração de aplicação: era `TERM` (que tipo de terminal você
está usando?), `PATH` (onde procurar programas) e `HOME`. Eram informações que o
shell precisava repassar aos programas, e nenhuma delas era segredo.

**Consequência que carregamos até hoje:** o mecanismo foi projetado para
*ambiente de execução*, não para *credencial*. Todas as tensões deste curso —
o ambiente ser legível pelo root, ser herdado por filhos, aparecer em relatório de
crash — vêm de estarmos usando para segredo uma coisa desenhada para `TERM=vt100`.

---

## 2. 1990s — CGI, ou o pecado original

O CGI (*Common Gateway Interface*) resolveu "como o servidor web passa a requisição
ao programa?" com: **coloque tudo em variáveis de ambiente**. `QUERY_STRING`,
`HTTP_USER_AGENT`, `REMOTE_ADDR`.

Foi engenhoso e foi desastroso: pela primeira vez, **dados controlados por um
estranho na internet** entravam no ambiente de um processo do servidor.

Em 2014, essa decisão explodiu no **Shellshock** (CVE-2014-6271). O bash tinha um
recurso de exportar *funções* por variável de ambiente. Um servidor CGI colocava o
cabeçalho `User-Agent` numa variável. Logo:

```
User-Agent: () { :; }; /bin/cat /etc/passwd
```

…executava comandos no servidor. Vinte anos entre a decisão de projeto e a
detonação.

**Lição permanente:** variável de ambiente **influencia o comportamento do processo**,
não só o informa. `LD_PRELOAD`, `PYTHONPATH`, `NODE_OPTIONS`, `BASH_ENV` carregam
código. Por isso, um serviço que aceita variáveis de fonte não confiável precisa de
**lista de permissão**, nunca de lista de bloqueio.

---

## 3. 2007–2011 — o Heroku força a mão

O Heroku tinha uma restrição arquitetural: **o sistema de arquivos é efêmero**.
Ao reiniciar, tudo que você escreveu em disco some. Isso tornou impossível o padrão
da época (arquivo de configuração colocado no servidor por alguém, uma vez).

A solução foi `heroku config:set DATABASE_URL=…`, e a plataforma injetava a variável
no processo a cada início.

Em 2011, Adam Wiggins destilou o aprendizado no **The Twelve-Factor App**.
O Fator III diz:

> *"O app doze-fatores armazena as configurações em variáveis de ambiente"*, e
> *"um teste decisivo é verificar se a base de código poderia ter seu código aberto
> a qualquer momento, sem comprometer nenhuma credencial."*

**O que o Twelve-Factor acertou** e continua valendo:
separar configuração de código; um artefato de build só, promovido entre ambientes;
paridade dev/prod; o teste do código aberto.

**O que envelheceu, e é honesto dizer:**

| Afirmação de 2011 | Situação em 2026 |
|---|---|
| "variáveis de ambiente são o mecanismo" | são **um** mecanismo; para segredo, arquivo montado e cofre são superiores (ver [10 §3](10-fundamentos.md)) |
| "não agrupe por ambiente (dev/staging/prod)" | continua certo, e continua sendo ignorado |
| implícito: um conjunto plano de chaves basta | configuração hierárquica e tipada (pydantic, Spring) resolve melhor |
| implícito: segredo estático é aceitável | credencial **dinâmica** de vida curta é o padrão superior desde ~2015 |

Opinião minha, não consenso: o Twelve-Factor é um documento excelente que hoje é
citado como escritura. Ele foi escrito por uma PaaS, para as restrições daquela PaaS,
em 2011. Use-o como princípio ("configuração fora do código"), não como
implementação obrigatória ("logo, tudo em `process.env`").

---

## 4. 2012 — o `.env` nasce, e nasce **explicitamente para desenvolvimento**

Brandon Keepers criou o `dotenv` em Ruby com um objetivo declarado no próprio README:

> *"Guarde a configuração no ambiente… Mas não é sempre prático definir variáveis
> de ambiente na máquina de desenvolvimento."*

Ou seja: o `.env` foi criado para **simular localmente** o que o Heroku fazia em
produção. Ele nunca foi proposto como formato de entrega.

**A distorção aconteceu por dois caminhos, ambos compreensíveis:**

1. **Tutoriais.** "Crie um `.env`" virou o passo 2 de todo tutorial, sem a frase
   "e em produção você não usa isto". Quem aprendeu assim nunca viu a alternativa.
2. **VPS baratas.** Quando o mundo saiu do Heroku para o DigitalOcean/Hetzner, o
   caminho de menor esforço foi `scp .env servidor:` — e funcionava.

É exatamente por isso que a sua pergunta é tão comum: **a resposta nunca esteve no
material onde o `.env` foi aprendido.**

---

## 5. 2013–2016 — contêiner, e a normalização do modelo

O Docker consagrou variável de ambiente como interface de configuração
(`-e`, `--env-file`, `ENV` no Dockerfile) — e, junto, criou três armadilhas novas:

- `ENV SEGREDO=x` no Dockerfile **grava o valor na camada da imagem**, para sempre,
  visível com `docker history` por qualquer um que baixe a imagem;
- `docker inspect` mostra todas as variáveis de um contêiner;
- `--build-arg` **também** vaza, apesar de parecer temporário.

Foi como resposta a isso que nasceu, nas imagens oficiais do Docker Hub, o padrão
**`NOME_FILE`** — `POSTGRES_PASSWORD_FILE`, `MYSQL_ROOT_PASSWORD_FILE`. Nunca foi
padronizado por ninguém; virou convenção porque funciona. É o que o
[projeto-modelo](07-projeto-modelo/README.md) implementa.

O Kubernetes (2016) trouxe o objeto `Secret` — e um mal-entendido que dura até hoje:
o valor é apenas **base64**, e base64 é codificação, não criptografia. Sem
`EncryptionConfiguration`, o segredo está legível no etcd e em qualquer backup dele.

---

## 6. 2015–2021 — cofres, e a virada conceitual

O **Vault** (2015) trouxe a mudança de mentalidade mais importante da área:
**credencial dinâmica**. Em vez de guardar a senha do banco, o Vault tem permissão de
**criar usuários no banco** e entrega à aplicação um usuário novo, válido por 1 hora.

Isso inverte a economia do vazamento:

| | Segredo estático | Credencial dinâmica |
|---|---|---|
| Vazou, e daí? | vale até alguém perceber e rotacionar | expira em minutos, sozinha |
| Quem usou? | impossível saber, é a mesma senha para todos | cada instância tem a sua — dá para rastrear |
| Rotação | projeto, com janela de indisponibilidade | é o funcionamento normal |

Em 2021, o **OIDC no CI** aplicou a mesma ideia à esteira de entrega: em vez de
guardar uma chave da AWS nos segredos do GitHub, o Actions apresenta um token de
identidade assinado pelo GitHub, e a AWS devolve credenciais temporárias. **Zero
segredo de longa duração armazenado.**

---

## 7. 2023 — duas mudanças que ainda estão sendo digeridas

**Agosto de 2023, licença do Vault.** A HashiCorp trocou MPL 2.0 por **BUSL 1.1**.
Engenheiros da IBM forkaram a última versão MPL (1.14.0) e criaram o **OpenBao**,
hoje sob a Linux Foundation. A IBM concluiu a compra da HashiCorp no início de 2025;
a versão paga virou **IBM Vault Enterprise**. Detalhes e recomendação em
[40-cofres-de-segredos.md](40-cofres-de-segredos.md) e
[80-custos-e-licencas.md](80-custos-e-licencas.md).

**Setembro de 2023, Node 20.6.** Chega o `--env-file` nativo. Depois vieram
`process.loadEnvFile()` (21.7) e `--env-file-if-exists` (22.9). Em Node moderno, a
biblioteca `dotenv` passou a ser opcional — embora continue com dezenas de milhões
de downloads semanais, porque a inércia de ecossistema é enorme.

---

## 8. Onde estamos, em uma frase

> Passamos de **"recompile para mudar a porta"** (1971) para **"a aplicação não tem
> segredo nenhum: ela prova quem é, e recebe uma credencial de 15 minutos"** (2026).

O `.env` é um degrau intermediário dessa escada, criado em 2012 para um problema
local, e que ficou grande demais por acidente pedagógico. Este curso é sobre subir
os degraus seguintes na medida certa para o seu caso — e
[75-armadilhas.md](75-armadilhas.md) é claro sobre isto: para um sistema pequeno,
`EnvironmentFile` com `chmod 640` é uma resposta **legítima e final**, não uma
vergonha. Nem todo mundo precisa de cofre.

---

## Autoteste

1. Para que serviam as primeiras variáveis de ambiente do Unix V7? Eram segredos?
2. O que o CGI fez de novo em relação ao ambiente, e como isso resultou no Shellshock 20 anos depois?
3. Qual restrição de arquitetura do Heroku forçou o modelo do Twelve-Factor?
4. Enuncie o "teste decisivo" do Fator III.
5. Qual era o propósito declarado do `dotenv` original, e como ele foi distorcido?
6. Por que `ENV SEGREDO=x` num Dockerfile é pior que `-e SEGREDO=x` no `docker run`?
7. De onde veio o padrão `NOME_FILE`, e por que ele nunca foi padronizado formalmente?
8. Explique a inversão econômica que a credencial dinâmica provoca no custo de um vazamento.
9. O que mudou na licença do Vault em 2023, e o que é o OpenBao?
10. Cite duas afirmações do Twelve-Factor que envelheceram, e por quê.

---

**Fontes consultadas em 14/08/2026:** 12factor.net/pt_br/config ·
github.com/bkeepers/dotenv (README) · `man 7 environ` · CVE-2014-6271 ·
github.com/openbao/openbao · nodejs.org/api/cli.html#--env-fileconfig ·
docs.docker.com · kubernetes.io/docs/tasks/administer-cluster/encrypt-data.

**Próximo:** [12-formato-dotenv.md](12-formato-dotenv.md) · Voltar ao [mapa](00-MAPA.md)
