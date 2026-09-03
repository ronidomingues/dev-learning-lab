# 18 · mTLS e PKI interna

**Nível:** avançado · **Data:** 31/08/2026

Autenticação mútua entre serviços, CA própria em escala, rotação sem downtime,
identidade no estilo SPIFFE e o que muda quando você tem 5, 50 ou 500 serviços.

A prática correspondente está no [projeto-modelo](07-projeto-modelo/README.md), que
implementa e testa tudo isto em pequena escala.

---

## 1. O que é mTLS, e o que ele substitui

No TLS comum, só o **servidor** prova quem é. No **mTLS**, o cliente também apresenta
certificado, e o servidor o valida contra uma CA que ele escolheu confiar.

| Comparado com… | Vantagem do mTLS | Desvantagem |
|---|---|---|
| **chave de API compartilhada** | não trafega segredo; a chave privada nunca sai do cliente; rotação por certificado | infraestrutura de emissão necessária |
| **JWT entre serviços** | autenticação no transporte, antes de qualquer código rodar; não há token para vazar em log | menos flexível para carregar claims |
| **firewall por IP** | identidade criptográfica, não topológica; IPs mudam, contêineres migram | mais peças móveis |
| **VPN / rede privada** | funciona entre nuvens, entre empresas, e sobre a internet | não substitui isolamento de rede — complementa |

**A vantagem estrutural:** com mTLS, uma requisição não autorizada é rejeitada **no
handshake**, antes de tocar o seu código. Não há rota consultada, não há parser de JSON
executado, não há log de aplicação. A superfície de ataque encolhe drasticamente.

Foi exatamente o que os testes do projeto-modelo mostraram: um cliente com certificado
de outra CA recebe `tlsv1 alert unknown ca` e a conexão morre — **`HTTP 0`**, não `HTTP 403`.

---

## 2. Autenticação **não é** autorização

O erro conceitual mais caro deste assunto.

```
mTLS responde:      "você é CN=servico-pedidos, comprovadamente"   ← autenticação
mTLS NÃO responde:  "e você pode chamar DELETE /clientes/42?"      ← autorização
```

Um service mesh configurado só com mTLS dá a **todos** os serviços do mesh acesso a
**todos** os endpoints. É a rede plana de sempre, agora com criptografia.

A autorização precisa ser explícita, na aplicação ou numa política do mesh:

```python
PERMISSOES = {
    "servico-pedidos":     {"GET /estoque", "POST /reservas"},
    "servico-relatorios":  {"GET /estoque", "GET /pedidos"},
}
cn = identidade_do_certificado()
if f"{metodo} {rota}" not in PERMISSOES.get(cn, set()):
    return 403
```

---

## 3. Identidade: pare de usar o CN

O CN é um campo de texto livre, com limite de 64 caracteres, herdado do X.500.
Ele não tem estrutura, não diz ambiente, não diz namespace, e não é único.

**A alternativa madura é o SPIFFE ID**, um URI no SAN:

```
spiffe://empresa.com.br/ns/producao/sa/servico-pedidos
         └── domínio ──┘ └ namespace ┘ └── identidade ──┘
```

```bash
openssl x509 -in cliente.crt -noout -ext subjectAltName
# X509v3 Subject Alternative Name:
#     URI:spiffe://empresa.com.br/ns/producao/sa/servico-pedidos
```

Vantagens concretas: carrega ambiente (produção ≠ homologação — um certificado de
homologação **não** é aceito em produção, o que o CN não garante), é hierárquico
(dá para autorizar por prefixo), e é padronizado (SPIFFE/SPIRE, Istio, Linkerd e
cert-manager falam isso).

Emitindo um SPIFFE ID com a nossa CA:

```bash
openssl x509 -req -in pedido.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -days 1 -out cliente.crt -extfile <(cat <<'EXT'
subjectAltName   = URI:spiffe://empresa.com.br/ns/producao/sa/servico-pedidos
keyUsage         = critical, digitalSignature
extendedKeyUsage = clientAuth
basicConstraints = critical, CA:FALSE
EXT
)
```

---

## 4. Arquiteturas de PKI interna

### 4.1 Raiz única (o que o projeto-modelo faz)

```
Raiz  ──►  folhas
```

✅ simples, ótimo para aprender e para até ~20 serviços.
❌ a chave da raiz é usada todo dia; se vazar, refazer tudo; não dá para separar ambientes.

### 4.2 Raiz offline + intermediários (recomendado a partir de ~20 serviços)

```
Raiz OFFLINE (10-20 anos, em HSM ou máquina sem rede)
  ├── Intermediário "produção"    (3-5 anos, on-line)
  ├── Intermediário "homologação" (3-5 anos, on-line)
  └── Intermediário "dev"         (1 ano)
```

✅ um intermediário comprometido é revogado sem tocar na raiz; ambientes isolados;
a raiz sai do cofre uma vez por ano.
❌ mais cerimônia; exige processo documentado para as operações com a raiz.

**Contenha cada intermediário com `nameConstraints`**, para que o de homologação não
possa emitir para nomes de produção:

```
nameConstraints = critical, permitted;DNS:.hml.empresa.interna
```

### 4.3 Emissão sob demanda, vida curtíssima (o modelo moderno)

```
CA on-line (step-ca / Vault PKI / SPIRE / cert-manager)
   │  emite certificados de 24h — ou de 1h — sob demanda
   ▼
serviços renovam automaticamente, várias vezes ao dia
```

✅ **revogação deixa de ser um problema**: um certificado comprometido morre sozinho
em horas. É o mesmo raciocínio dos certificados públicos de 6 dias
([15 §6](15-validacao-revogacao-transparencia.md)).
❌ exige que a CA esteja sempre disponível — ela vira dependência crítica; e exige
recarga de certificado sem restart.

**Esta é a recomendação para ambientes novos.**

---

## 5. Ferramentas

| Ferramenta | Melhor para | Notas |
|---|---|---|
| **step-ca** (Smallstep) | PKI interna geral | open source (Apache 2.0), suporta ACME, OIDC, SSH; a porta de entrada mais fácil |
| **HashiCorp Vault (PKI)** | quem já usa Vault | integrado a segredos e políticas; atenção à licença BUSL desde 2023 |
| **cert-manager** | Kubernetes | padrão de facto; fala ACME e CAs internas |
| **SPIRE** (SPIFFE) | zero trust, multi-nuvem, cargas heterogêneas | atestação de identidade da carga; a solução mais completa e a mais complexa |
| **Istio / Linkerd** | service mesh | mTLS automático entre pods, sem tocar na aplicação |
| **AWS Private CA / GCP CAS** | quem já está na nuvem | gerenciado; **caro** — ver [80](80-custos-e-licencas.md) |
| **openssl + scripts** | aprender, e PKIs muito pequenas | é o [projeto-modelo](07-projeto-modelo/README.md) |

### step-ca em cinco comandos

```bash
step ca init --name "Empresa" --dns ca.interno --address :8443 --provisioner admin
step-ca $(step path)/config/ca.json &
step ca certificate "servico-pedidos" cliente.crt cliente.key --not-after 24h
step ca renew cliente.crt cliente.key --daemon --expires-in 8h &
step ca revoke --cert cliente.crt
```

O `--daemon` renova sozinho quando falta 1/3 da validade. É o padrão do modelo §4.3.

---

## 6. Rotação sem downtime

O problema: você precisa trocar a CA (chave comprometida, algoritmo obsoleto,
migração pós-quântica) sem derrubar nada.

**A regra:** sempre **adicione antes de remover**, e sempre nesta ordem.

```
Fase 1 · Distribuir a CA nova como confiável (SEM emitir por ela)
         Todo servidor e todo cliente passa a confiar em {CA_antiga, CA_nova}.
         Nada muda no tráfego. Verifique que 100% da frota recebeu.

Fase 2 · Emitir pela CA nova
         Certificados novos são assinados pela CA_nova. Os antigos continuam
         válidos, porque todos ainda confiam nas duas.

Fase 3 · Esperar a validade dos antigos escoar
         Com certificados de 24h: um dia. Com 90 dias: um trimestre.
         (Aqui a vida curta paga sozinha o investimento em automação.)

Fase 4 · Remover a CA_antiga da lista de confiança
         Só depois de confirmar, por telemetria, que ninguém mais a apresenta.
```

**Inverter a ordem derruba tudo.** Se você emitir pela CA nova antes de distribuí-la,
os clientes recusam com `unknown_ca` — e você descobre isso pelo alerta de indisponibilidade.

Instrumente a fase 3:

```bash
# em cada servidor, conte por qual CA os clientes estão se apresentando
grep 'ssl_client_i_dn' /var/log/nginx/access.log | sort | uniq -c
```

---

## 7. O que dá errado em produção

| Problema | Sintoma | Prevenção |
|---|---|---|
| certificado do cliente vencido | serviço para de repente, sem mudança de código | renovação automática + alerta de "expira em <1/3 da validade" |
| CA renovada, clientes não atualizados | `unknown_ca` em massa | ordem do §6 |
| relógio dessincronizado | `certificate not yet valid` | NTP obrigatório; margem de alguns minutos no `notBefore` |
| `verify_client optional` em vez de `on` | mTLS que não autentica nada | teste automatizado que **tenta sem certificado e exige falha** |
| chave privada em imagem de container | vaza no registry, em qualquer camada | monte por volume ou segredo |
| CA sem `pathlen`/`nameConstraints` | um intermediário emite para qualquer nome | restrinja na emissão |
| cabeçalho de identidade não sobrescrito no proxy | cliente forja `X-Client-DN` | `proxy_set_header` sempre ([17 §2.2](17-configuracao-de-servidores.md)) |
| a CA on-line cai | **ninguém consegue renovar** | alta disponibilidade da CA; certificados com folga maior que a janela de recuperação |
| certificado não recarregado após renovação | serve o antigo até vencer | `GetCertificate`/`setSecureContext`/reload no gancho |

> ### A dependência que morde
> No modelo de vida curtíssima (§4.3), **a CA vira uma dependência crítica de tudo**.
> Se ela ficar 25 horas fora do ar e seus certificados durarem 24, o ambiente inteiro
> para. Regra prática: a validade tem de ser **pelo menos 3× maior** que o seu pior
> tempo de recuperação da CA, e a renovação deve começar quando resta 1/3 da validade —
> assim há duas janelas de tentativa antes do vencimento.

---

## 8. mTLS entre organizações

Cenário real: você e um parceiro comercial precisam de uma integração autenticada.

| Modelo | Como | Quando |
|---|---|---|
| **CA de um dos lados** | o parceiro emite; você usa o certificado dele | integração pontual, relação assimétrica |
| **Cada um usa a própria CA** | vocês trocam apenas os **certificados de CA** e cada lado confia no da outra | ✅ o mais comum e o mais limpo |
| **CA pública + fixação** | ambos usam certificados públicos e restringem por SPKI/nome | evita PKI privada; exige monitorar renovações |
| **CA em comum, de terceiro** | uma CA gerenciada emite para os dois | consórcios, setores regulados |

Combine sempre, por escrito: **prazo de validade, procedimento de rotação, canal para
comunicar comprometimento, e como testar**. A falha mais comum em integração B2B com
mTLS não é técnica — é o parceiro renovar o certificado sem avisar.

---

## 9. Quando **não** usar mTLS

Ser honesto sobre isso evita projetos sofridos.

| Situação | Por que evitar | Alternativa |
|---|---|---|
| autenticação de **usuários finais** na web | distribuir e instalar certificado em navegador é péssima experiência; perder o dispositivo é um drama | senha + MFA, passkeys/WebAuthn |
| APIs públicas com muitos clientes desconhecidos | você teria de emitir para cada um | OAuth 2.0, chaves de API |
| equipe sem automação de certificados | você troca um problema por incidentes recorrentes | comece pela automação; mTLS depois |
| um único serviço, sem rede exposta | complexidade sem ganho | firewall + TLS comum |
| protótipo | atrasa o aprendizado | TLS comum; adicione mTLS quando o desenho estabilizar |

**Onde mTLS brilha:** comunicação **serviço-a-serviço**, integração **B2B**,
dispositivos gerenciados (IoT com provisionamento de fábrica) e arquiteturas de
**zero trust** onde a rede não é considerada confiável.

---

## Autoteste

1. Qual é a vantagem estrutural do mTLS sobre uma chave de API, em termos de superfície de ataque?
2. Por que autenticação não é autorização, e o que acontece num mesh que ignora isso?
3. Cite três vantagens concretas do SPIFFE ID sobre o CN.
4. Descreva as três arquiteturas de PKI interna e quando usar cada uma.
5. Para que serve `nameConstraints` num intermediário?
6. Qual é a ordem correta das quatro fases de rotação de CA, e o que acontece se inverter?
7. No modelo de vida curtíssima, qual é a regra de folga entre validade e recuperação da CA?
8. Qual é o modelo mais limpo de mTLS entre duas empresas?
9. Cite três situações em que mTLS é a escolha errada.
10. Como você testaria, automaticamente, que o seu mTLS realmente exige certificado?

*Respostas: §1, §2, §3, §4, §4.2, §6, §7, §8, §9, §7 + [projeto-modelo](07-projeto-modelo/README.md) teste 40.*

---

**Próximo:** [19-tls-alem-do-https.md](19-tls-alem-do-https.md) — e-mail, DNS, QUIC, IoT.
