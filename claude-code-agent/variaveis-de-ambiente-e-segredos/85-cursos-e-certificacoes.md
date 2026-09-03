# 85 · Cursos gratuitos e certificações

`Nível: todos` · **Pesquisado na web em 18/08/2026**

> ⚠️ **Aviso honesto, e ele muda como você deve ler este arquivo:**
> **não existe curso dedicado a "variáveis de ambiente e segredos"** — o assunto é
> transversal. Ele aparece como **módulo** dentro de cursos de Docker, Kubernetes,
> DevOps, AppSec e da documentação oficial de cada ferramenta.
> Este arquivo aponta os **módulos certos** dentro dos melhores cursos gratuitos,
> em vez de fingir que existe uma trilha pronta.
>
> Links podem expirar. O ano de publicação está indicado quando conhecido.

---

## 1. 🇧🇷 Português — a prioridade

### 1.1 Segurança de aplicações — o contexto onde o assunto vive

| Curso | Autor | Onde | Duração | Nível | Vale? |
|---|---|---|---|---|---|
| **AppSec Starter** | Conviso | YouTube (aulas abertas) + [blog.convisoappsec.com](https://blog.convisoappsec.com/treinamento-online-e-gratuito-sobre-seguranca-de-aplicacoes-conheca-o-appsec-starter/) | ~10 h | iniciante | ⭐ **Sim.** O melhor material gratuito de AppSec em português. Cobre OWASP Top 10, modelagem de ameaças e gestão de configuração sensível em linguagem acessível |
| **Curso gratuito OWASP Top 10** | comunidade | [playlist no YouTube](https://www.youtube.com/playlist?list=PLEqTHftpM91OZzAIOwMcAuQ4ciK1n4_Ll) | ~6 h | iniciante | Sim — inclui A02 (Falhas Criptográficas) e A05 (Configuração Insegura), que são exatamente este assunto |
| **Desenvolvimento de Software Seguro** | PUC-Rio (curso livre) | [especializacao.ccec.puc-rio.br](https://especializacao.ccec.puc-rio.br/cursos-livres/desenvolvimento-software-seguro) | variável | intermediário | Sim, pela chancela institucional; cobre OWASP SKF e princípios de projeto seguro |

**Vá direto ao que interessa:** no OWASP Top 10, procure **A05:2021 — Security
Misconfiguration** e **A02:2021 — Cryptographic Failures**. São, literalmente, os
capítulos deste curso na taxonomia da indústria.

### 1.2 Docker e Kubernetes — onde os segredos aparecem na prática

| Curso | Autor | Onde | Duração | Nível | Vale? |
|---|---|---|---|---|---|
| **Descomplicando o Docker** | Jeferson Fernando (LINUXtips) | [playlist no YouTube](https://www.youtube.com/playlist?list=PLg7nVxv7fa6dxsV1ftKI8FAm4YD6iZuI4) | ~15 h | iniciante | ⭐ **Sim.** Didática excelente; veja as aulas de variáveis de ambiente e Docker secrets |
| **Descomplicando o Kubernetes** | LINUXtips | [linuxtips.io](https://linuxtips.io/descomplicando-o-kubernetes/) (parte em vídeo aberto; treinamento pago) | ~40 h | intermediário | Sim para o conteúdo aberto. Cobre **ConfigMaps e Secrets**, mapeamento em variáveis e consumo por volume — o §6 do [30](30-entrega-em-producao.md) |
| **Curso de Kubernetes** | Fabricio Veronez | canal do YouTube dele | variável | intermediário | Sim. Conteúdo prático e atualizado, em português |

⚠️ **Separando o gratuito do "gratuito para assistir":** a LINUXtips publica muito
conteúdo aberto no YouTube e vende os treinamentos completos com laboratório e
comunidade. O que está no YouTube é gratuito de verdade; a plataforma é paga.

### 1.3 A documentação oficial em português

| Recurso | Link | Por que importa |
|---|---|---|
| **The Twelve-Factor App — Fator III (Configurações)** | [12factor.net/pt_br/config](https://12factor.net/pt_br/config) | 10 minutos de leitura. **É o documento fundador deste assunto**, e está traduzido |
| Documentação do Docker | docs.docker.com | tem tradução parcial; as seções de `secrets` e BuildKit são essenciais |
| Documentação do Kubernetes | kubernetes.io/pt-br/ | tradução em bom estado; veja Secrets e "Encrypting Confidential Data at Rest" |
| Cartilha de Segurança (CERT.br) | [cartilha.cert.br](https://cartilha.cert.br/) | fundamentos de segurança em português, gratuito, de uma fonte séria |

---

## 2. 🇬🇧 Inglês

### 2.1 Gratuito de verdade

| Curso | Autor | Onde | Duração | Ano | Vale? |
|---|---|---|---|---|---|
| **HashiCorp Vault Tutorials** | HashiCorp | [developer.hashicorp.com/vault/tutorials](https://developer.hashicorp.com/vault/tutorials) | 20–40 h | atualizado | ⭐⭐ **A melhor fonte gratuita do assunto, em qualquer idioma.** Laboratórios guiados, do "getting started" a credencial dinâmica e auto-unseal |
| **Introduction to HashiCorp Vault** | Armon Dadgar (CTO da HashiCorp) | YouTube (~26 min) | 26 min | — | ⭐ Sim. A melhor explicação de *secret sprawl* que existe. Comece por aqui |
| **OpenBao Documentation** | Linux Foundation | [openbao.org/docs](https://openbao.org/docs/) | — | 2024–26 | Sim, e é a alternativa de licença aberta |
| **OWASP Cheat Sheet: Secrets Management** | OWASP | [cheatsheetseries.owasp.org](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_CheatSheet.html) | 1 h de leitura | atualizado | ⭐ **Sim.** Denso, prático, sem marketing. Leia depois deste curso |
| **Kubernetes: Encrypting Data at Rest** | kubernetes.io | docs oficiais | 2 h | atual | Sim — é a referência sobre KMS v2 |
| **Class Central — Vault/Secrets** | agregador | [classcentral.com/subject/hashicorp-vault](https://www.classcentral.com/subject/hashicorp-vault) | — | — | Útil como índice: filtra 100+ cursos por "gratuito" |

### 2.2 "Gratuito para assistir, pago para certificar"

| Plataforma | O que é grátis | O que é pago |
|---|---|---|
| **KodeKloud** | alguns laboratórios introdutórios | trilha completa e certificados |
| **Coursera** (ex.: *HashiCorp Vault Foundations*) | assistir em modo *audit* | certificado |
| **Pluralsight** | teste gratuito | assinatura |
| **AppSecEngineer** | amostras | curso completo |
| **Udemy** | promoções ocasionais | o curso |

**Seja franco consigo:** para este assunto específico, os tutoriais oficiais da
HashiCorp (gratuitos) são **melhores** que a maioria dos cursos pagos. Pague por curso
só se você precisar do certificado para um processo seletivo.

---

## 3. 🇫🇷 Francês

| Recurso | Autor | Onde | Gratuito? | Vale? |
|---|---|---|---|---|
| **Documentation DevSecOps** | Stéphane Robert | [blog.stephane-robert.info](https://blog.stephane-robert.info/) | ✅ **sim** | ⭐⭐ **O melhor recurso francófono da área.** Mais de mil páginas estruturadas, com trilha *Apprendre → Pratiquer → Valider → Certifier*, incluindo Linux, Ansible, Terraform, Kubernetes, CI/CD e **gestão de segredos** |
| **HashiCorp Vault : gérez vos secrets en toute sécurité** | Stéphane Robert | [blog.stephane-robert.info/docs/securiser/secrets/hashicorp-vault/](https://blog.stephane-robert.info/docs/securiser/secrets/hashicorp-vault/) | ✅ sim | ⭐ Sim. Trata diretamente do assunto: centralizar armazenamento, acesso e rotação em vez de espalhar em arquivos de configuração e variáveis de ambiente |
| **devopssec.fr** | comunidade | [devopssec.fr](https://devopssec.fr/) | ✅ sim | Sim — cursos abertos de DevOps e arquitetura de nuvem |
| **Tuto Technique : Introduction à HashiCorp Vault avec Kubernetes** | HashiCorp France | hashicorp.com (recursos) | ✅ sim | Sim, tutorial em vídeo passo a passo |
| **Installer et utiliser Vault** | dev2root | [dev2root.ovh/notes/vault-secret-manager](https://dev2root.ovh/notes/vault-secret-manager) | ✅ sim | Sim, guia prático da versão comunitária |
| Zenika, Ambient IT, Learni Group, Udemy FR | — | — | ❌ **pagos** | formações presenciais/online pagas, com preparação para certificação |

---

## 4. Certificações

### 4.1 A única diretamente relacionada

**HashiCorp Certified: Vault Associate (003)**

| Item | Detalhe |
|---|---|
| Custo | **US$ 70,50** + impostos locais (~R$ 367, câmbio de 18/08/2026) |
| Formato | online, com supervisão remota |
| Escopo | alinhada ao **Vault 1.16** — recursos do Vault 2.0 estão **fora** do escopo |
| Conteúdo | métodos de autenticação, motores de segredos, políticas, tokens, identidade, arquitetura, alta disponibilidade, recuperação de desastre, log de auditoria |
| Público | engenheiros de nuvem em segurança, desenvolvimento ou operação |
| Preparação gratuita | os [tutoriais oficiais](https://developer.hashicorp.com/vault/tutorials) cobrem quase tudo |

**Vale a pena?** Opinião minha: **sim, se** você trabalha ou quer trabalhar com Vault
em empresa que o usa — o mercado reconhece as certificações HashiCorp. **Não**, se o
objetivo é aprender o assunto: os tutoriais gratuitos ensinam mais, e a certificação
está atrelada a **uma ferramenta**, não ao conceito.

⚠️ Nota de contexto: com a compra pela IBM concluída no início de 2025, o programa de
certificação pode mudar de marca ou de estrutura. Confirme na página oficial antes de
comprar o exame.

### 4.2 Certificações onde o assunto é um módulo

| Certificação | Custo aprox. | Peso do assunto |
|---|---|---|
| **CKS** (Certified Kubernetes Security Specialist) | ~US$ 395 | ⭐ alto — "Minimize Microservice Vulnerabilities" cobre Secrets, criptografia em repouso e políticas |
| **CKA** (Certified Kubernetes Administrator) | ~US$ 395 | médio — ConfigMaps e Secrets |
| **AWS Security – Specialty** | ~US$ 300 | alto — KMS, Secrets Manager, IAM |
| **Terraform Associate** | ~US$ 70,50 | baixo — gestão de variáveis sensíveis |
| **CompTIA Security+** | ~US$ 400 | baixo-médio — criptografia e gestão de credenciais |

### 4.3 Certificados gratuitos — e a verdade sobre eles

| Emissor | O que exige | Vale no mercado? |
|---|---|---|
| **Fundação Bradesco** (escolavirtual.bradesco.com.br) | conclusão do curso | 🟡 reconhecido no Brasil para nível básico; não é técnico específico |
| **FGV Online** (cursos livres até 30 h) | conclusão | 🟡 boa reputação institucional; conteúdo introdutório |
| **AWS Skill Builder** (trilhas gratuitas) | conclusão | 🟡 crachá, não certificação |
| **Google Cloud Skills Boost** | laboratórios | 🟡 crachá |
| **Microsoft Learn** | módulos | 🟡 crachá |
| **Cursos em Vídeo** | conclusão | 🟡 popular no Brasil, nível introdutório |
| **freeCodeCamp** | projetos | 🟡 simbólico, mas os projetos podem entrar no portfólio |

**Sendo direto:** certificado gratuito de conclusão tem **valor simbólico**, não de
mercado. Ele mostra iniciativa e nada mais. **O que abre porta neste assunto é
portfólio:** um repositório com configuração validada, `.env.example` bem escrito,
gitleaks no CI, instalador com permissões corretas e um README explicando as decisões.
O [projeto-modelo](07-projeto-modelo/README.md) é exatamente esse artefato — adapte-o
para um sistema seu.

---

## 5. Roteiro sugerido de estudo externo

**Semana 1 — fundamentos (grátis, ~4 h)**
1. [12factor.net/pt_br/config](https://12factor.net/pt_br/config) — 10 min
2. *Introduction to HashiCorp Vault*, com Armon Dadgar — 26 min
3. [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_CheatSheet.html) — 1 h
4. Os laboratórios 1 a 6 de [70-pratica.md](70-pratica.md) — 2 h

**Semana 2 — contêineres (grátis, ~10 h)**
5. Descomplicando o Docker (LINUXtips), aulas de variáveis e secrets
6. Laboratórios 7 e 8 de [70-pratica.md](70-pratica.md)

**Semana 3–4 — cofre (grátis, ~15 h)**
7. Tutoriais oficiais do Vault: *Getting Started* → *Dynamic Secrets* → *Auth Methods*
8. Laboratórios 9, 10 e 12

**Depois — se quiser certificação**
9. Vault Associate (003), estudando pelos tutoriais oficiais
10. Ou CKS, se o seu mundo é Kubernetes

---

## Autoteste

1. Por que não existe um curso dedicado a "variáveis de ambiente e segredos"?
2. Quais itens do OWASP Top 10 correspondem diretamente a este assunto?
3. Qual é o melhor recurso gratuito em português para o contexto de AppSec?
4. Qual é o melhor recurso gratuito em francês, e por quê?
5. Por que os tutoriais oficiais da HashiCorp podem valer mais que um curso pago?
6. Quanto custa o exame Vault Associate (003), e a qual versão do Vault ele é alinhado?
7. Qual a diferença entre um "crachá" de plataforma de nuvem e uma certificação?
8. O que, na prática, abre mais portas que um certificado gratuito de conclusão?

---

**Pesquisado na web em 18/08/2026.** Fontes: youtube.com (playlists citadas) ·
blog.convisoappsec.com · linuxtips.io · especializacao.ccec.puc-rio.br ·
12factor.net/pt_br · developer.hashicorp.com/vault/tutorials · openbao.org ·
cheatsheetseries.owasp.org · classcentral.com/subject/hashicorp-vault ·
blog.stephane-robert.info · devopssec.fr · dev2root.ovh · hashicorp.com/certification.
**Preços de exame e disponibilidade de curso mudam — reconfira antes de pagar.**

**Próximo:** [90-bibliografia.md](90-bibliografia.md) · Voltar ao [mapa](00-MAPA.md)
