# Glossário

`Atualizado em: 14/08/2026` · Todo termo técnico usado neste curso, definido.
Termos em inglês são mantidos quando é assim que o campo os usa.

---

## A

**AEAD** (*Authenticated Encryption with Associated Data*) — criptografia que garante
**confidencialidade e integridade** ao mesmo tempo. AES-GCM e ChaCha20-Poly1305 são
AEAD; AES-CBC sozinho não é. Ver [60 §1](60-teoria-avancada.md).

**AES-256-GCM** — cifra simétrica padrão da indústria, em modo autenticado.
O nonce **nunca** pode repetir com a mesma chave.

**age** — ferramenta moderna de criptografia de arquivo, criada por Filippo Valsorda.
Substitui o GPG para este uso: chaves curtas, sem cadeia de confiança.

**Ambiente** (*environment*) — o vetor de strings `NOME=valor` que o kernel entrega
ao processo no `execve`. Ver [10 §1](10-fundamentos.md).

**ANPD** — Agência Nacional de Proteção de Dados. Órgão brasileiro que regula a LGPD
e recebe comunicações de incidente.

**Argon2id** — função de derivação de chave a partir de senha, recomendada desde 2015.
Deliberadamente lenta e consumidora de memória.

**Atestação remota** — o hardware prova criptograficamente **o que está rodando**,
antes de receber um segredo. Ver [60 §4d](60-teoria-avancada.md).

**AppRole** — método de autenticação do Vault/OpenBao baseado em `role_id` + `secret_id`.
Concentra o problema do segredo zero num único par.

**Auto-unseal** — destravar o Vault automaticamente usando um KMS ou TPM.
**Obrigatório em produção**; sem ele, humanos precisam destravá-lo a cada reinício.

## B

**Base64** — **codificação**, não criptografia. `base64 -d` desfaz. Secrets do
Kubernetes usam base64, e confundir os dois é o mal-entendido nº 1 da área.

**Bootstrap de segredo** — ver **Segredo zero**.

**BUSL 1.1** (*Business Source License*) — licença do HashiCorp Vault desde agosto de
2023. Permite uso e modificação; proíbe oferecer como serviço concorrente. Cada
versão vira MPL 2.0 quatro anos depois.

**BuildKit** — construtor de imagens do Docker que suporta `--mount=type=secret`,
a única forma correta de usar segredo em tempo de build.

## C

**Camada** (*layer*) — unidade imutável de uma imagem de contêiner. Um `RUN rm` numa
camada posterior **não apaga** o conteúdo da anterior.

**Capability** — privilégio granular do Linux (`CAP_NET_BIND_SERVICE` etc.),
alternativa ao "tudo ou nada" do root.

**Certificado de vida curta** — certificado válido por horas em vez de anos.
Base do modelo SPIFFE.

**`clear_env`** — diretiva do PHP-FPM que limpa o ambiente herdado. Padrão `yes`.
Ver [16 §5](16-php.md).

**Configuração** — tudo que muda entre lugares de execução sem que o código mude.
Nem toda configuração é segredo.

**ConfigMap** — objeto do Kubernetes para configuração **não sensível**.

**Credencial dinâmica** — credencial criada sob demanda pelo cofre, com validade
curta, e destruída na expiração. Ver [40 §2](40-cofres-de-segredos.md).

**Criptografia de envelope** — cifrar os dados com uma DEK e cifrar a DEK com uma KEK.
Base de todo cofre moderno. Ver [60 §3](60-teoria-avancada.md).

**cwd** (*current working directory*) — diretório de onde o comando foi executado.
As bibliotecas de `.env` procuram o arquivo **aqui**, não ao lado do código.

## D

**DEK** (*Data Encryption Key*) — chave que cifra os dados, na criptografia de envelope.

**direnv** — carrega e **descarrega** variáveis ao entrar e sair de um diretório.
Exige `direnv allow` porque o `.envrc` é script executável.

**`.dockerignore`** — o que **não** entra na imagem. Deve conter `.env` e `.git`.

**dotenv** — família de bibliotecas que lê um `.env` e injeta no ambiente.
Criada em 2012, em Ruby, **para desenvolvimento local**.

**dotenvx** — sucessor comercial do `dotenv`, com `.env` criptografado. Resolve
transporte, não gestão. Ver [15 §6](15-node.md).

**DPAPI** — API do Windows que cifra dados com uma chave derivada da conta de usuário
ou da máquina. Análogo do `systemd-creds`.

## E

**`.env`** — arquivo de texto com `NOME=valor` por linha. **Não tem especificação**;
cada biblioteca implementa um dialeto. Ver [12](12-formato-dotenv.md).

**`.env.example`** — versão versionada do `.env`, **sem valores**. É o **contrato** de
quais variáveis o sistema exige.

**`environ`** — variável global de C (`extern char **environ`) que aponta para o
ambiente do processo.

**`EnvironmentFile`** — diretiva do systemd que carrega variáveis de um arquivo.
**Não é shell**: sem expansão, sem `export`, sem `$(comando)`.

**ESO** (*External Secrets Operator*) — operador CNCF que sincroniza segredos de um
cofre externo para Secrets do Kubernetes.

**Entropia** — medida de imprevisibilidade. Um segredo de 256 bits tem 256 bits de
entropia **se** gerado por fonte criptográfica.

**`EX_CONFIG` (78)** — código de saída de `sysexits.h` para "erro de configuração".
Permite ao orquestrador distinguir configuração errada de erro transitório.

**`execve`** — chamada de sistema que substitui a imagem do processo e **recebe o
ambiente como parâmetro**. ⭐ É a origem de tudo neste curso.

## F

**Falha rápida** (*fail fast*) — validar tudo na inicialização e recusar subir se
algo estiver errado, em vez de quebrar depois, em produção.

**FHE** (*Fully Homomorphic Encryption*) — computar sobre dados cifrados sem
decifrar. Possível desde 2009; impraticável para este problema em 2026.

**`fork`** — chamada que cria um processo filho **copiando** o ambiente do pai.
A cópia é de mão única: o filho não altera o pai.

## G

**`getenv()`** — função que lê uma variável do ambiente. **Em PHP, não é equivalente
a `$_ENV`** — ver [16 §1](16-php.md).

**gitleaks** — varredor de segredos por expressão regular. MIT, rápido, ideal para
pre-commit e CI.

**`.gitignore`** — lista do que o Git ignora. **Só afeta arquivos não rastreados.**

## H

**HSM** (*Hardware Security Module*) — dispositivo físico que guarda chaves e faz
operações criptográficas sem nunca exportá-las.

## I

**Identidade de carga de trabalho** (*workload identity*) — provar quem o serviço é
sem senha, usando a atestação da plataforma. Ver SPIFFE.

**IMDS / IMDSv2** — serviço de metadados de instância da AWS, que entrega credenciais
temporárias. O **v2** exige token via `PUT`, mitigando exploração por SSRF.

**iO** (*Indistinguishability Obfuscation*) — noção teórica de ofuscação.
Construções existem desde 2013; impraticáveis.

## K

**KEK** (*Key Encryption Key*) — a chave-mestra, que cifra as DEKs. Fica no KMS/HSM e
idealmente nunca é exportável.

**KMS** (*Key Management Service*) — serviço que guarda chaves-mestras e faz operações
com elas sem exportá-las.

**KMS v2** — versão atual do provedor de criptografia em repouso do Kubernetes.
O v1 está obsoleto desde a 1.28 e desativado desde a 1.29.

## L

**Lease** (*concessão*) — validade de um segredo entregue por um cofre. Renovável e
revogável.

**LGPD** — Lei Geral de Proteção de Dados (Lei 13.709/2018). Impõe obrigações em caso
de vazamento de dados pessoais.

**`LoadCredential`** — diretiva do systemd que entrega um segredo como **arquivo** num
`tmpfs` privado do serviço, sem passar pelo ambiente. ⭐ Subestimada.

## M

**Mascaramento** (*masking*) — substituir parte do segredo ao exibi-lo
(`sk_…23 (23 chars)`), preservando utilidade para diagnóstico.

**Menor privilégio** — dar a cada identidade só o que ela precisa. O princípio que
limita o estrago de qualquer comprometimento.

**Modelo de ameaça** (*threat model*) — a resposta a "contra quem estou me defendendo?".
Sem ele, "seguro" não significa nada. Ver [60 §2](60-teoria-avancada.md).

**MPL 2.0** — Mozilla Public License. Copyleft por arquivo. Licença do SOPS e do OpenBao.

## N

**`NEXT_PUBLIC_` / `VITE_` / `REACT_APP_`** — prefixos que fazem a variável ser
**embutida no JavaScript entregue ao navegador**. **Nunca** para segredo.

**Nonce** — número usado uma vez. Em AES-GCM, **repetir o nonce com a mesma chave
quebra a segurança do esquema**.

## O

**OIDC** (*OpenID Connect*) — protocolo de identidade. No CI, permite obter
credenciais temporárias da nuvem **sem armazenar nenhum segredo**.

**OpenBao** — fork do HashiCorp Vault 1.14 (última versão MPL 2.0), sob a Linux
Foundation. Versão 2.0 em setembro de 2024.

**`open_basedir`** — diretiva do PHP que restringe quais diretórios um script pode
ler. Em hospedagem compartilhada, é o que impede outro cliente de ler o seu `.env`.

**`override`** — opção que faz o `.env` **sobrescrever** o ambiente. Praticamente
nunca é o que você quer.

## P

**Parameter Store** — serviço da AWS, **gratuito** até 10.000 parâmetros no nível
Standard, com `SecureString` cifrado por KMS. A alternativa subestimada ao Secrets Manager.

**PKCE** — extensão do OAuth que dispensa segredo do cliente em aplicações públicas.

**Precedência** — a ordem em que as fontes de configuração vencem umas às outras.
Regra geral: **ambiente > `.env` > padrão do código**. Ver [10 §5](10-fundamentos.md).

**`/proc/<pid>/environ`** — arquivo do Linux que expõe o ambiente de um processo.
Legível pelo dono e pelo root. **É o limite de proteção de variável de ambiente.**

**Processo** — instância em execução de um programa. Variável de ambiente pertence ao
processo, não ao sistema.

**`pull_request_target`** — gatilho do GitHub Actions que **recebe segredos**.
Fazer checkout do código do fork nele é uma via clássica de exfiltração.

**Push protection** — bloqueio de push no servidor quando o commit contém padrão de
segredo conhecido. Gratuito em repositórios públicos do GitHub.

## R

**RBAC** — controle de acesso baseado em papéis. Em Kubernetes, é a **fronteira real**
de proteção de Secrets, não o objeto Secret em si.

**Redação** (*redaction*) — substituir valores sensíveis no log por `[REDIGIDO]`.
Por nome de chave é necessário e **insuficiente** (não pega senha dentro de URL).

**`RestartPreventExitStatus`** — diretiva do systemd que impede reinício para
determinados códigos de saída. Com `78`, evita loop eterno em configuração errada.

**Rotação** — trocar um segredo por outro. Ver **Sobreposição**.

## S

**`SecretStr`** — tipo do pydantic que impede o valor de aparecer em `repr`, log ou
traceback. Torna o mascaramento o **padrão**.

**Secret (Kubernetes)** — objeto que guarda dados sensíveis. **Base64, não criptografia**;
exige `EncryptionConfiguration` para estar cifrado no etcd.

**Segredo** — dado cuja **utilidade depende de sua confidencialidade**. Ver
[10 §9](10-fundamentos.md).

**Segredo zero** (*secret zero* / *bootstrapping problem*) — ⭐ a credencial necessária
para obter as outras credenciais. Onde guardá-la é o problema mais fundamental da
área. Ver [60 §4](60-teoria-avancada.md).

**Selo / seal** — estado inicial do Vault, em que ele não responde a nada até ser
destravado.

**Shellshock (CVE-2014-6271)** — falha em que variável de ambiente virava execução de
código. Consequência direta do modelo do CGI.

**Sobreposição** — técnica de rotação em que **duas credenciais são válidas ao mesmo
tempo**, eliminando a janela de indisponibilidade. Ver [45 §4](45-rotacao-e-ciclo-de-vida.md).

**SOPS** (*Secrets OPerationS*) — criptografa **valores** dentro de YAML/JSON/ENV,
mantendo as chaves legíveis. Sandbox da CNCF.

**SPIFFE / SPIRE** — padrão e implementação de identidade de carga de trabalho.
Emite **SVIDs** de vida curta após atestação.

**SSRF** (*Server-Side Request Forgery*) — induzir o servidor a buscar uma URL
arbitrária. Com IMDSv1, vira comprometimento total da conta de nuvem.

**SVID** (*SPIFFE Verifiable Identity Document*) — certificado X.509 ou JWT de vida
curta que materializa a identidade SPIFFE.

**`sysexits.h`** — cabeçalho C com códigos de saída convencionais. `EX_CONFIG` é 78.

**`systemd-creds`** — utilitário que cifra credenciais com uma chave selada no TPM.
O arquivo cifrado **só decifra naquela máquina**.

## T

**TPM 2.0** (*Trusted Platform Module*) — chip que guarda chaves e mede o que a
máquina carregou. Base da atestação local.

**Transit** — motor do Vault/OpenBao que **cifra sem guardar**: a aplicação manda o
texto e recebe o cifrado, sem nunca ver a chave.

**trufflehog** — varredor que **verifica** se a credencial encontrada ainda está ativa,
chamando o provedor. AGPL-3.0.

**Twelve-Factor App** — manifesto de 2011. O **Fator III** define "configuração no
ambiente" e é o documento fundador deste assunto.

## U

**`umask`** — máscara que define a permissão padrão de arquivos novos.
`umask 077` faz tudo nascer `600`.

## V

**Vault** — cofre de segredos da HashiCorp, hoje produto IBM. Licença BUSL 1.1 desde
agosto de 2023.

**`variables_order`** — diretiva do `php.ini` que decide quais superglobais são
montadas. Sem o `E`, **`$_ENV` fica vazio**.

## W

**White-box cryptography** — tentativa de esconder a chave de quem controla a
execução. **Teoricamente impossível** no caso geral; todos os esquemas propostos
foram quebrados.

## Z

**Zero Trust** — modelo em que nenhuma rede é confiável por padrão e toda requisição
é autenticada e autorizada. Contexto do SPIFFE.

---

**Voltar ao [mapa](00-MAPA.md)**
