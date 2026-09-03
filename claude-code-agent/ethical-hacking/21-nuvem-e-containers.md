# 21 · Nuvem e containers

`Nível: avançado` · `Última atualização: 12/08/2026`

A superfície de ataque migrou para a nuvem. Onde antes havia servidores num prédio, hoje há
IAM, buckets, funções serverless e Kubernetes. Este arquivo cobre os ataques específicos desse
mundo — e por que eles são diferentes.

> ⚖️ **Atenção especial ao escopo em nuvem:** o ativo é do cliente, mas a infraestrutura é do
> provedor (AWS/Azure/GCP). Você precisa da autorização do cliente **e** respeitar as políticas
> de pentest do provedor. Ver [`12`](12-etica-lei-e-contrato.md) §5.

---

## 1. Por que a nuvem muda o modelo de ataque

Na infraestrutura tradicional, o perímetro era a rede. Na nuvem, **o perímetro é a
identidade** (IAM). Você raramente "invade um servidor" pela rede; você **abusa de uma
permissão mal configurada**. A pergunta muda de "qual porta está aberta?" para "o que essa
credencial pode fazer?".

**Modelo de responsabilidade compartilhada:** o provedor protege a nuvem (hardware, hipervisor);
**o cliente** protege o que está *na* nuvem (configuração, IAM, dados). A maioria esmagadora
dos incidentes de nuvem é **erro de configuração do cliente**, não falha do provedor. É aí que
o pentester atua.

## 2. IAM — o coração e o calcanhar

**IAM (Identity and Access Management)** define quem pode fazer o quê. Os ataques:
- **Permissões excessivas:** uma credencial de app com `AdministratorAccess` "para não dar
  erro". Comprometa o app, herde o admin.
- **Escalada de privilégio via IAM:** encadear permissões aparentemente inócuas (ex.:
  `iam:PassRole` + criar recurso) para virar admin. `pacu` (AWS) e `ScoutSuite` automatizam a
  busca.
- **Chaves vazadas:** `AWS_ACCESS_KEY` em repositório público, log, ou no metadata service.
  Achado nº 1 em nuvem. Ver [`14`](14-reconhecimento-e-osint.md) §7.

```bash
# Com uma credencial, enumere o que ela pode (AWS)
aws sts get-caller-identity            # quem sou eu?
aws iam get-account-authorization-details 2>/dev/null
pacu                                    # framework de exploração AWS
scout suite aws                         # auditoria de configuração
```

## 3. SSRF + Metadata Service — o ataque emblemático da nuvem

Cada instância na nuvem tem um **metadata service** num IP fixo (`169.254.169.254`) que entrega
informação da instância — **incluindo credenciais IAM temporárias**. Se você achar um **SSRF**
([`18`](18-seguranca-web.md) §3) numa aplicação na nuvem, você força o servidor a buscar essas
credenciais:
```
http://169.254.169.254/latest/meta-data/iam/security-credentials/<role>
```
Isso foi a raiz do vazamento da **Capital One (2019)**: um SSRF levou às credenciais IAM, que
levaram aos buckets S3 com dados de 100 milhões de pessoas. **Defesa:** IMDSv2 (exige token,
mitiga SSRF ingênuo), menor privilégio na role, e corrigir o SSRF.

## 4. Armazenamento exposto (S3 e equivalentes)

Buckets S3 (AWS), Blob (Azure), GCS (GCP) mal configurados como **públicos** são clássicos:
```bash
aws s3 ls s3://empresa-backups --no-sign-request   # sem credencial — está público?
```
Nomes previsíveis (`empresa-backup`, `empresa-dev`, `empresa-logs`) permitem enumerar. Ferramentas:
`s3scanner`, dorks. **Defesa:** *block public access*, políticas de bucket restritas, criptografia.

## 5. Containers — escape e abuso

Container **não é** fronteira de segurança forte por padrão (ver a pasta `docker` deste
repositório). Ataques:
- **Container privilegiado / com socket do Docker montado:** `--privileged` ou
  `/var/run/docker.sock` dentro do container = root no host. Trivial de escapar.
- **Grupo `docker`:** membro do grupo docker monta `/` do host num container → root. Ver
  [`17`](17-pos-exploracao-e-movimentacao.md).
- **Capabilities excessivas, namespaces compartilhados.**
- **Imagem com segredo/CVE:** credenciais embutidas na imagem, camadas com dados apagados só
  na aparência.

```bash
# Dentro de um container comprometido, checar caminhos de escape:
./deepce.sh                 # Docker Enumeration & Escalation
cat /proc/1/cgroup          # estou num container? qual?
ls -la /var/run/docker.sock # socket montado = escape fácil
capsh --print               # capabilities perigosas?
```

## 6. Kubernetes — a superfície nova

Kubernetes (K8s) orquestra containers e trouxe sua própria superfície:
- **API server exposto** sem autenticação forte.
- **RBAC mal configurado:** um pod com service account poderoso → controle do cluster.
- **Secrets** em texto (base64 não é criptografia), etcd exposto.
- **Pods privilegiados**, escape para o nó, movimentação entre nós.
- **Kubelet** exposto na porta 10250.

```bash
kubectl auth can-i --list          # o que meu token pode?
# Ferramentas: kube-hunter (descoberta), kube-bench (CIS), peirates (exploração)
```
**Defesa:** RBAC mínimo, Pod Security Standards, network policies, secrets criptografados,
não expor a API.

## 7. Serverless e "as-a-service"

Funções (Lambda, Cloud Functions) e serviços gerenciados mudam o alvo: menos SO para atacar,
mais **configuração e permissão**. Ataques focam em: variáveis de ambiente com segredo,
permissões da role da função, injeção via evento, dependências (supply chain — A03).

## 8. Estratégia de pentest em nuvem

```
1. Recon: achar ativos na nuvem (ASN, S3 público, subdomínios apontando para *.amazonaws.com)
2. Se tem credencial: enumerar IAM (o que ela pode) → escalar
3. Se tem app: procurar SSRF → metadata → credencial IAM
4. Buckets/storage: checar exposição pública
5. Containers/K8s: se comprometeu um, buscar escape e abuso de service account
6. Mapear tudo a configuração incorreta; recomendar menor privilégio
```
Ferramentas de auditoria (ScoutSuite, Prowler, kube-bench) dão o panorama de configuração
rápido — muito do valor em nuvem é achar o *misconfig*, não escrever exploit.

## 9. Os cinco porquês: por que a nuvem vaza tanto por configuração?

**Por quê 1** — Por que a maioria dos vazamentos de nuvem é erro de configuração, não de exploit?
Porque na nuvem a segurança **é** a configuração: um clique errado em "público" ou uma role
larga expõe dados sem precisar de nenhuma falha de software.

**Por quê 2** — Por que se configura errado com tanta frequência?
Porque o IAM da nuvem é imensamente complexo (milhares de permissões, interações não óbvias) e
a pressão é entregar rápido — o caminho fácil é dar permissão a mais "para funcionar".

**Por quê 3** — Por que o modelo é tão complexo?
Porque expressa flexibilidade real (todo caso de uso possível) — e flexibilidade e simplicidade
de configuração segura são objetivos em tensão. Um sistema que faz tudo é difícil de configurar
com segurança.

**Por quê 4** — Por que o provedor não torna o seguro o padrão?
Cada vez mais torna (block public access agora é padrão no S3, IMDSv2 empurrado). Mas o padrão
seguro às vezes quebra casos de uso legítimos, gerando atrito — e o cliente afrouxa.

**Por quê 5** — Qual é a parada?
Um **trade-off entre flexibilidade e configurabilidade segura**, agravado pela
responsabilidade compartilhada: o provedor entrega poder e joga a segurança da configuração no
cliente, que não tem tempo nem expertise para acertar milhares de permissões. Enquanto o poder
do IAM crescer mais rápido que a capacidade média de configurá-lo, a nuvem vazará por
configuração — e é por isso que auditoria de configuração de nuvem é uma das especialidades que
mais cresce em 2026.

---

## Autoteste

1. Por que se diz que "na nuvem o perímetro é a identidade"?
2. Explique o modelo de responsabilidade compartilhada e onde o pentester atua.
3. Como um SSRF numa app em nuvem leva ao roubo de credenciais IAM? (cite o caso Capital One)
4. O que o IMDSv2 muda em relação ao ataque de metadata?
5. Por que estar no grupo `docker` equivale a ser root no host?
6. Cite três formas de escapar ou abusar de um container comprometido.
7. No Kubernetes, por que "secrets em base64" não é proteção?
8. Por que a nuvem vaza tanto por configuração e não por exploit? Leve o porquê até o fim.
