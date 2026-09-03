# 16 · ACME e automação de certificados

**Nível:** intermediário · **Data:** 31/08/2026

Como obter, instalar e renovar certificados públicos **sem nunca tocar no processo**.
A partir de 15/03/2026 a validade máxima é de 200 dias; em 2027 serão 100; em 2029, 47.
Este arquivo deixou de ser conveniência e virou requisito operacional.

---

## 1. O que é ACME

**ACME** (*Automatic Certificate Management Environment*, RFC 8555) é um protocolo
padrão para: provar que você controla um domínio, pedir um certificado, e renová-lo —
tudo por API, sem humano no meio.

Foi criado pela ISRG junto com o Let's Encrypt (2015) e padronizado na IETF em 2019.
Hoje é implementado também por ZeroSSL, BuyPass, Google Trust Services e várias CAs
comerciais — **não é um protocolo de um fornecedor só**, e isso importa para não ficar
preso a um deles.

### O fluxo, em cinco passos

```
1. CONTA        cliente gera um par de chaves e registra uma conta na CA
                     │
2. PEDIDO       "quero um certificado para exemplo.com.br e www.exemplo.com.br"
                     │
3. DESAFIO      a CA responde: "prove que você controla esses nomes; escolha
                 HTTP-01, DNS-01 ou TLS-ALPN-01"
                     │
4. VALIDAÇÃO    o cliente cumpre o desafio; a CA verifica de vários pontos da rede
                     │
5. EMISSÃO      o cliente envia um CSR; a CA devolve o certificado assinado
                 (e o cliente REPETE tudo isso automaticamente antes do vencimento)
```

**A chave privada nunca sai da sua máquina.** A CA só vê o CSR (chave pública + nomes).

---

## 2. Os três desafios, e quando usar cada um

| Desafio | Como prova | Exige | Emite curinga? |
|---|---|---|---|
| **HTTP-01** | serve um arquivo em `http://SEU.DOMINIO/.well-known/acme-challenge/TOKEN` | **porta 80** aberta para a internet | ❌ |
| **DNS-01** | publica um registro `TXT` em `_acme-challenge.SEU.DOMINIO` | acesso de API ao seu provedor de DNS | ✅ |
| **TLS-ALPN-01** | responde um handshake TLS especial com ALPN `acme-tls/1` | **porta 443**, e o servidor precisa suportar | ❌ |

**Como escolher:**

- **HTTP-01** é o padrão e o mais simples. Use se o servidor é alcançável na porta 80.
- **DNS-01** é o único que emite **curinga**, o único que funciona para servidor sem IP
  público (rede interna, atrás de NAT), e o único que dispensa portas abertas.
  Em troca, exige guardar um **token de API do DNS** — que é uma credencial poderosa.
  Dê a ele o menor escopo possível (só edição de DNS, só naquela zona).
- **TLS-ALPN-01** serve quando a porta 80 está bloqueada mas a 443 não. É o que o
  Caddy usa como alternativa automática.

> **Redirecionamento é permitido no HTTP-01.** A CA segue redirecionamentos, inclusive
> de HTTP para HTTPS. Isso permite centralizar todos os desafios num único servidor —
> um truque útil em ambientes com muitos hosts.

---

## 3. Let's Encrypt: os números que importam

| Item | Valor (consultado em 31/08/2026) |
|---|---|
| Preço | **US$ 0** |
| Validade padrão | 90 dias |
| Perfil `shortlived` | **160 horas (~6 dias)**, disponível desde 15/01/2026 |
| Certificado para **endereço IP** | sim, desde 15/01/2026 — **só** no perfil de 6 dias |
| Certificados por domínio registrado | 50 por semana |
| Nomes por certificado | 100 |
| Renovações duplicadas | 5 por semana (mesmo conjunto exato de nomes) |
| Contas por IP | 10 por 3 horas |
| Falhas de validação | 5 por conta/host/hora |
| Ambiente de teste (*staging*) | limites muito folgados, certificado não confiável |

**A regra que evita o desastre:** **teste sempre no staging primeiro.**

```bash
certbot certonly --dry-run -d exemplo.com.br
# ou explicitamente:
certbot certonly --server https://acme-staging-v02.api.letsencrypt.org/directory -d exemplo.com.br
```

Bater no limite de 50 por semana significa **ficar sem certificado por até 7 dias**,
sem apelação. Acontece tipicamente com contêineres que não persistem os certificados e
pedem novos a cada reinício ([06 Exemplo 12](06-exemplos.md)).

---

## 4. Os clientes ACME — qual usar

| Cliente | Linguagem | Melhor para | Nota |
|---|---|---|---|
| **Caddy** | Go | **quem quer parar de pensar nisso** | não é um cliente: é um servidor web que faz TLS sozinho. Recomendação nº 1 para casos novos |
| **certbot** | Python | uso geral, servidores tradicionais | oficial da EFF; muitos plugins; pesado |
| **lego** | Go | automação, binário único, muitos provedores de DNS | ótimo em CI e em imagens enxutas |
| **acme.sh** | shell puro | hospedagem compartilhada, sistemas sem Python | roda em quase tudo; leia o script antes de confiar |
| **cert-manager** | Go | **Kubernetes** | padrão de facto no cluster |
| **Traefik / nginx-proxy-manager** | — | quem já usa esses proxies | ACME embutido |
| **win-acme** | .NET | Windows/IIS | integra com o repositório do Windows |

> ### Opinião profissional
> **Se você está começando um serviço novo em 2026, use Caddy.** A configuração inteira
> de HTTPS é o nome do domínio no arquivo — sem certbot, sem cron, sem plugin, sem
> renovação, sem `fullchain.pem` trocado por `cert.pem`. Ele elimina, por construção,
> as quatro causas mais comuns de incidente de TLS.
> O contra-argumento honesto: nginx tem uma década a mais de conhecimento acumulado,
> muito mais gente que sabe depurá-lo, e módulos que o Caddy não tem. Se a sua equipe
> já opera nginx bem, trocar só por causa do ACME não se justifica — use certbot.

---

## 5. Receitas completas

### 5.1 Caddy — o caminho de menor esforço

```caddyfile
# /etc/caddy/Caddyfile
exemplo.com.br {
    reverse_proxy localhost:3000
}
```

```bash
sudo systemctl reload caddy
```

É isso. O Caddy: resolve o domínio, escolhe o desafio, obtém o certificado, configura
TLS com padrões seguros, renova automaticamente, faz OCSP stapling, redireciona HTTP
para HTTPS e serve HTTP/2 e HTTP/3.

```bash
sudo journalctl -u caddy -f | grep -i certificate
# esperado: "certificate obtained successfully"
```

### 5.2 certbot com nginx (edita a configuração para você)

```bash
sudo certbot --nginx -d exemplo.com.br -d www.exemplo.com.br
```
Obtém o certificado **e** insere as diretivas no seu `nginx.conf`.

```bash
sudo certbot certificates
# esperado: lista com "VALID: 89 days" (ou o que restar)
```

```bash
sudo systemctl list-timers | grep certbot
# esperado: certbot.timer  — a renovação já está agendada duas vezes ao dia
sudo certbot renew --dry-run
# esperado: "Congratulations, all simulated renewals succeeded"
```

**Modo `certonly`** (você mesmo configura o servidor — preferível quando a configuração
é versionada em Git e você não quer que um programa a edite):

```bash
sudo certbot certonly --webroot -w /var/www/certbot \
  -d exemplo.com.br -d www.exemplo.com.br \
  --key-type ecdsa --preferred-chain "ISRG Root X1"
```

### 5.3 DNS-01 com curinga (Cloudflare)

```bash
sudo apt install -y python3-certbot-dns-cloudflare
printf 'dns_cloudflare_api_token = SEU_TOKEN\n' | sudo tee /root/.cloudflare.ini
sudo chmod 600 /root/.cloudflare.ini      # a permissão importa: é uma credencial
sudo certbot certonly \
  --dns-cloudflare --dns-cloudflare-credentials /root/.cloudflare.ini \
  -d exemplo.com.br -d '*.exemplo.com.br'
```

Crie o token com escopo **`Zone:DNS:Edit` apenas na zona necessária**. Um token global
de conta num servidor de borda é um risco desproporcional ao problema que resolve.

### 5.4 Certificado de 6 dias (perfil `shortlived`)

```bash
certbot certonly --webroot -w /var/www/certbot \
  --preferred-profile shortlived \
  -d exemplo.com.br
```

Com 6 dias de validade, a renovação passa a rodar **várias vezes por dia**. Só faz
sentido com automação madura e monitoramento — mas é o futuro para quem quer eliminar
revogação do modelo de ameaça.

### 5.5 Certificado para endereço IP

```bash
certbot certonly --standalone \
  --preferred-profile shortlived \
  -d 203.0.113.10
```

Só existe na modalidade de 6 dias, e o desafio precisa ser HTTP-01 ou TLS-ALPN-01
(não há DNS para um IP). Útil para APIs acessadas por IP, appliances e nós de
infraestrutura sem nome.

### 5.6 Kubernetes com cert-manager

Ver [06 Exemplo 13](06-exemplos.md), que traz o manifesto completo e o problema de
recarga do certificado.

---

## 6. O gancho de recarga — a parte que todo mundo esquece

Obter o certificado novo não adianta se o servidor continuar servindo o antigo em
memória.

```bash
# certbot: script executado APÓS cada renovação bem-sucedida
sudo tee /etc/letsencrypt/renewal-hooks/deploy/recarregar.sh >/dev/null <<'EOF'
#!/bin/sh
set -e
systemctl reload nginx     # reload, não restart: não derruba conexões abertas
systemctl reload postfix 2>/dev/null || true
docker kill --signal=HUP proxy 2>/dev/null || true
EOF
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/recarregar.sh
```

```bash
sudo certbot renew --dry-run    # o dry-run EXECUTA os hooks: teste real
```

**Serviços que exigem `restart` e não aceitam `reload`** (Postfix em algumas
configurações, Dovecot, aplicações Java): planeje a janela, ou implemente recarga do
certificado dentro da aplicação.

---

## 7. Monitoramento: a automação também quebra

Automatizar não elimina o risco; **muda** o risco de "esqueci de renovar" para
"a renovação falhou silenciosamente por seis semanas". Monitore o resultado, não o processo.

```bash
# de fora, do jeito que o usuário vê (script completo em 06 Exemplo 2)
echo | openssl s_client -connect exemplo.com.br:443 -servername exemplo.com.br 2>/dev/null \
  | openssl x509 -noout -checkend 1209600 || echo "ALERTA: vence em menos de 14 dias"
```

**Alerte em duas camadas:**

1. **preventiva** — "vence em menos de 21 dias" (com validade de 90) ou "menos de 2
   dias" (com validade de 6). Dá tempo de agir.
2. **de saúde da automação** — "o `certbot.timer` não roda há 48 horas", "o último
   `renew` falhou". Detecta a causa antes do sintoma.

O Let's Encrypt envia e-mail de aviso de expiração, mas **não conte com isso**: o
endereço muda, o e-mail cai em spam, e o serviço já sinalizou a intenção de reduzir
esses avisos. Monitore você.

---

## 8. Erros comuns e o que fazer

| Erro | Causa | Correção |
|---|---|---|
| `Timeout during connect (likely firewall problem)` | HTTP-01 sem porta 80 alcançável | libere a 80, ou use DNS-01 |
| `Invalid response from http://.../.well-known/acme-challenge/...: 404` | o webroot não é o que o servidor serve, ou há redirecionamento para HTTPS mal feito | confirme com `curl http://dominio/.well-known/acme-challenge/teste` |
| `too many certificates already issued for: exemplo.com.br` | limite de 50/semana | espere; use staging para testar; **persista os certificados** |
| `DNS problem: NXDOMAIN looking up A for ...` | o domínio não resolve, ou o DNS ainda não propagou | `dig +short A dominio` |
| `Incorrect TXT record ... found at _acme-challenge` | propagação de DNS lenta | `--dns-cloudflare-propagation-seconds 60` |
| certificado renovado mas o site serve o antigo | falta o gancho de recarga | §6 |
| `unable to get local issuer certificate` nos clientes | apontou para `cert.pem` em vez de `fullchain.pem` | corrija o caminho |
| `The client lacks sufficient authorization` | CAA proíbe a CA, ou o desafio falhou | `dig +short CAA dominio` |
| Caddy pedindo certificados sem parar | volume `/data` não persistido | monte o volume |

---

## 9. Quando **não** usar ACME público

| Situação | O que usar |
|---|---|
| serviços internos, sem nome público | **CA interna** ([18](18-mtls-e-pki-interna.md), [projeto-modelo](07-projeto-modelo/README.md)) |
| mTLS entre serviços | CA interna, cert-manager, step-ca, Vault PKI |
| desenvolvimento local | **mkcert** ([03 §2.5](03-instalacao.md)) |
| dispositivo sem internet | CA interna, com certificado embarcado |
| nome que não deve aparecer publicamente | CA interna — lembre que ACME público publica tudo em CT ([15 §7.3](15-validacao-revogacao-transparencia.md)) |

---

## Autoteste

1. Quais são os cinco passos do fluxo ACME, e o que a CA **nunca** vê?
2. Compare os três desafios. Qual é o único que emite curinga, e o que ele exige em troca?
3. Quais são os limites de emissão do Let's Encrypt que mais causam incidente?
4. Por que testar no ambiente de staging antes?
5. Em que caso você recomendaria Caddy em vez de certbot, e em que caso o contrário?
6. O que é o gancho de recarga (*deploy hook*) e por que ele é esquecido?
7. Automatizar a renovação elimina o risco? O que passa a ser preciso monitorar?
8. Como se obtém um certificado para um endereço IP, e qual é a restrição?
9. Cite quatro situações em que ACME público **não** é a resposta.
10. Um cliente reclama de `unable to get local issuer certificate` depois de uma renovação. Primeira hipótese?

*Respostas: §1, §2, §3, §3, §4, §6, §7, §5.5, §9, §8.*

---

**Próximo:** [17-configuracao-de-servidores.md](17-configuracao-de-servidores.md) — a configuração real, comentada.
