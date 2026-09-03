# 65 · Estado da arte — agosto de 2026

`Nível: pesquisa` · `Atualizado em: 14/08/2026`
`⚠️ Este arquivo envelhece rápido. Reavalie a cada 6 meses.`

---

## 1. O que mudou nos últimos três anos

| Quando | O quê | Consequência prática |
|---|---|---|
| set/2023 | **Node 20.6** ganha `--env-file` | a biblioteca `dotenv` passa a ser opcional |
| ago/2023 | **Vault muda para BUSL 1.1** | nasce o **OpenBao**, hoje na Linux Foundation |
| 2023 | **SOPS** entra na CNCF (sandbox) | criptografia de arquivo ganha governança neutra |
| 2021→ | **OIDC no CI** vira padrão | fim da chave estática no pipeline |
| 2024 | **OpenBao 2.0** (set/2024) | fork maduro e pronto para produção |
| início/2025 | **IBM conclui a compra da HashiCorp** | Vault Enterprise vira produto IBM |
| 2025–26 | **push protection do GitHub** expande | bloqueio no servidor, grátis em repositórios públicos |
| 2024–26 | **KMS v2** no Kubernetes; v1 obsoleto (1.28) e desligado (1.29) | criptografia do etcd deixa de ser opcional na prática |
| 2026 | **External Secrets Operator** na linha 2.x, projeto CNCF | padrão dominante para segredos em K8s |

---

## 2. As quatro tendências de fundo

### 2.1 Do segredo para a identidade

A mudança mais importante, e ela é conceitual:

```
   ANTES                              AGORA
   "eu sei a senha"                   "eu SOU o serviço X, e posso provar"
   segredo compartilhado              identidade atestada pela plataforma
   estático, indefinido               credencial derivada, de 1 hora
   vaza → acesso duradouro            vaza → expira sozinha
```

Materializações em uso: OIDC no CI, IAM roles, ServiceAccounts do Kubernetes,
SPIFFE/SPIRE, Workload Identity Federation. O objetivo declarado do setor é
**não haver segredo a guardar**.

**Onde essa transição está travada:** APIs de terceiros. A Stripe, o gateway de
pagamento local, o ERP do cliente — todos ainda emitem chave estática. Enquanto
existir `sk_live_…`, existirá segredo a guardar. Esse é o gargalo real, e é comercial,
não técnico.

### 2.2 Do "guardar bem" para o "expirar rápido"

Credencial de vida curta é mais eficaz que credencial bem guardada. É a diferença
entre reduzir a **probabilidade** do vazamento e reduzir o **impacto** dele — e o
segundo é mais confiável, porque não depende de ninguém acertar sempre.

### 2.3 Da detecção posterior para o bloqueio no ponto de entrada

```
2015: descobrimos meses depois, por acaso
2019: secret scanning avisa depois do push
2023: push protection bloqueia NO SERVIDOR
2026: bloqueio por padrão, com dezenas de detectores, grátis em repo público
```

### 2.4 Da ferramenta para a plataforma

Segredo deixou de ser "uma ferramenta que eu instalo" e virou "uma propriedade da
plataforma onde eu rodo": Cloud Run monta segredo como arquivo, ECS injeta do
Secrets Manager, Fly tem `secrets set`, o Kubernetes tem ESO. **A tendência é a
aplicação não saber que existe um cofre** — e isso é bom, é o mesmo desacoplamento
que este curso defende desde o [04](04-como-comecar.md).

---

## 3. O que está em disputa agora

### 3.1 OpenBao vs. IBM Vault

| | Vault (IBM) | OpenBao |
|---|---|---|
| Licença | BUSL 1.1 (→ MPL 2.0 após 4 anos) | MPL 2.0 |
| Governança | IBM | Linux Foundation |
| Ecossistema | maior, mais integrações | crescendo; API compatível |
| Suporte comercial | IBM | várias empresas independentes |
| Adotantes públicos | enorme base instalada | Nvidia entre os oficiais |

**Minha leitura:** o OpenBao venceu a disputa de legitimidade (Linux Foundation,
adotantes de peso, suporte comercial plural) e ainda não venceu a de ecossistema.
Para projeto novo autogerenciado, eu escolheria OpenBao. Para quem já paga
Enterprise e depende de recursos exclusivos, migrar por ideologia é caro e
provavelmente errado.

### 3.2 Cofre externo vs. plataforma nativa

Duas escolas:

- **cofre único, multi-nuvem** (Vault/OpenBao): uma fonte da verdade, uma auditoria,
  uma política. Custo: mais um sistema crítico para operar.
- **nativo de cada plataforma** (AWS SM + Azure KV + GCP SM): zero operação, IAM já
  integrado. Custo: política e auditoria fragmentadas, aprisionamento.

Não há vencedor. A escolha correta depende de quantas nuvens você usa e de quanto a
sua equipe consegue operar. **Se você tem uma nuvem só, o nativo quase sempre ganha.**

### 3.3 O debate sobre rotação periódica

Já tratado em [45 §5](45-rotacao-e-ciclo-de-vida.md). Segue sem consenso, com o NIST
de um lado (para senhas humanas) e a conformidade tradicional do outro. A saída
prática que ganha força: **tornar a rotação automática**, e assim o debate perde
sentido.

### 3.4 IA e segredos — o assunto novo

Duas frentes que não existiam em 2022:

**(a) Assistentes de código vazando segredo.** Ferramentas que leem o repositório
inteiro podem sugerir uma chave real vista em outro arquivo, ou incluir o conteúdo do
`.env` no contexto enviado ao provedor do modelo. Mitigação: `.aiignore`/exclusões de
contexto, e nunca deixar segredo em texto no diretório do projeto — que é a mesma
recomendação de sempre, agora com mais um motivo.

**(b) Agentes autônomos com credenciais.** Um agente que executa comandos precisa de
credenciais, e o modelo de menor privilégio para agentes ainda é assunto em aberto.
Escopo, aprovação humana para ações destrutivas e credenciais de vida curta são o
que existe hoje. É a fronteira mais quente, e a menos madura.

---

## 4. Ferramentas para acompanhar

| Ferramenta | O que faz | Vale a pena? |
|---|---|---|
| **OpenBao** | cofre completo, fork do Vault | ✅ padrão autogerenciado |
| **SOPS + age** | criptografia de arquivo versionável | ✅ excelente custo-benefício |
| **External Secrets Operator** | cofre → Secret do K8s | ✅ padrão em Kubernetes |
| **SPIRE** | identidade de carga de trabalho (SPIFFE) | ✅ se você tem muitos serviços |
| **Infisical** | cofre com boa interface, open source | 🟡 promissor; avalie o modelo por identidade |
| **Doppler** | SaaS de segredos, boa experiência | 🟡 pago por usuário |
| **gitleaks** | varredura por regex, rápida | ✅ obrigatória |
| **trufflehog** | varredura com **verificação** de credencial ativa | ✅ para histórico |
| **dotenvx** | `.env` criptografado | 🟡 resolve transporte, não gestão; SOPS faz melhor |
| **systemd-creds** | credencial cifrada com TPM | ⭐ subestimada, gratuita, ótima |
| **Sealed Secrets** | segredo cifrado versionável em K8s | 🟡 ESO costuma ser melhor |
| **Teller / Envkey** | agregadores de fonte de configuração | 🟡 nicho |

---

## 5. Problemas em aberto

1. **O segredo zero permanece.** Atestação por TPM e identidade de plataforma
   resolvem em casos específicos; **não** há solução geral para servidor físico
   arbitrário sem hardware confiável.
2. **APIs de terceiros ainda emitem chave estática.** Enquanto isso não mudar, o
   modelo "sem segredo" é inatingível na ponta.
3. **Auditoria de uso, não de acesso.** Sabemos quem **leu** o segredo; não sabemos
   o que ele **fez** com ele depois. O elo entre leitura e ação é opaco.
4. **Ausência de padrão para `.env`.** Cada carregador diverge, e ninguém tem
   autoridade para padronizar ([12](12-formato-dotenv.md)).
5. **Rotação em sistemas legados.** Muito software não suporta duas credenciais
   simultâneas, o que impede a técnica de sobreposição e força janela de queda.
6. **Segredos em modelos de IA.** Um modelo treinado ou com contexto contendo
   segredo pode reproduzi-lo. Não há técnica madura de "desaprender" um valor.
7. **Multi-inquilino e custódia.** Guardar segredo de cliente ainda é resolvido
   caso a caso, sem padrão de mercado.

---

## 6. O que eu apostaria para 2027–2030

Explicitamente **especulação minha**, não previsão fundamentada:

| Aposta | Confiança |
|---|---|
| Identidade de carga de trabalho (SPIFFE ou equivalente) vira padrão em plataformas gerenciadas | **alta** |
| `.env` continua vivo em desenvolvimento local, sem substituto | **alta** |
| Todo grande provedor de API oferece OIDC/mTLS além da chave estática | média |
| Atestação por TPM/TDX vira padrão para segredo em servidor físico | média |
| Chave estática de API deixa de ser emitida por provedores novos | baixa |
| iO ou FHE ficam práticos para este problema | **muito baixa** |
| Alguém finalmente padroniza o formato `.env` | **muito baixa** |

**O que **não** vai mudar:** a pergunta que originou este curso continuará sendo
feita, porque continuará ausente do material onde as pessoas aprendem o `.env`.

---

## Autoteste

1. Cite as quatro tendências de fundo e dê um exemplo concreto de cada.
2. Por que "do segredo para a identidade" está travado nas APIs de terceiros?
3. Por que reduzir impacto é mais confiável que reduzir probabilidade?
4. Qual a situação do OpenBao frente ao Vault em agosto de 2026?
5. Quando o cofre nativo da nuvem vence o cofre único multi-nuvem?
6. Cite duas frentes novas de risco trazidas por ferramentas de IA.
7. Por que a auditoria de cofre registra o acesso mas não o uso, e por que isso é um problema em aberto?
8. Por que sistemas legados impedem a técnica de sobreposição?
9. Qual mudança de 2026 tornou o bloqueio de segredo no servidor acessível de graça?

---

**Fontes consultadas em 14/08/2026:** openbao.org · linuxfoundation.org ·
cncf.io (SOPS, external-secrets) · github.blog/changelog (secret scanning, 2026) ·
kubernetes.io (KMS v2) · nodejs.org (release notes) · spiffe.io ·
techtarget.com (cobertura da adoção do OpenBao pela Nvidia).

**Próximo:** [70-pratica.md](70-pratica.md) · Voltar ao [mapa](00-MAPA.md)
