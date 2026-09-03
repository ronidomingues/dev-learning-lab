# 28 · Deploy e operação

> **Nível:** avançado · **Escrito em:** 02/09/2026 · Streamlit 1.63.0
> Os endpoints da seção 2 foram **verificados** contra um servidor 1.63.0 rodando
> localmente em 02/09/2026, não copiados de documentação.

---

## 1. As opções, comparadas

| Onde | Custo | Esforço | Privado? | Escala | Quando |
|---|---|---|---|---|---|
| **Community Cloud** | grátis | mínimo | 1 app privado | ~1 GB de RAM | protótipo, portfólio, uso interno leve |
| **Contêiner em VPS** (Hetzner, DigitalOcean, EC2) | US$ 5–40/mês | médio | sim | você decide | **o melhor custo-benefício** |
| **PaaS** (Render, Railway, Fly.io, Cloud Run, App Service) | US$ 7–50/mês | baixo | sim | automática | quando não quer administrar servidor |
| **Kubernetes** | variável | alto | sim | alta | quando a empresa já tem |
| **Streamlit in Snowflake** | créditos Snowflake | baixo | sim | gerenciada | quando os dados já estão lá |

Preços com data em [80-custos-e-licencas.md](80-custos-e-licencas.md).

---

## 2. Endpoints do servidor (verificados na 1.63.0)

| Caminho | Serve para |
|---|---|
| `/_stcore/health` | verificação de saúde — devolve `ok` |
| `/healthz` | atalho para o mesmo |
| `/_stcore/stream` | **o WebSocket** — o proxy precisa repassar isto |
| `/_stcore/upload_file` | destino do `file_uploader` |
| `/_stcore/host-config` | configuração que o front lê na partida |
| `/_stcore/metrics` | métricas (formato Prometheus) |
| `/_stcore/allowed-message-origins` | origens permitidas para mensagens do host |

Todos responderam 200 (e o `stream`, 101 Switching Protocols) num servidor 1.63.0
em 02/09/2026.

---

## 3. Streamlit Community Cloud

O caminho de menor esforço, e é gratuito.

1. Código num repositório do **GitHub** (é obrigatório).
2. `requirements.txt` na raiz, com versões fixadas.
3. <https://share.streamlit.io> → conecte o GitHub → escolha repositório, branch e
   arquivo.
4. Segredos em **Settings → Secrets** (o mesmo formato do `secrets.toml`).

**Limites, verificados na documentação e nos fóruns oficiais em 02/09/2026:**

- **~1 GB de memória** por app;
- **app dorme após 12 horas sem tráfego** (qualquer visitante o acorda);
- **apps públicos ilimitados; 1 app privado**;
- sem domínio próprio;
- hospedado nos **Estados Unidos**, sem opção de região — o que tem implicação de
  LGPD se houver dado pessoal;
- atualizações do GitHub limitadas a 5 por minuto;
- roda sobre Debian; o gerenciador de pacotes não pode ser misturado.

**O erro nº 1 no Community Cloud:** "This app has gone over its resource limits."
É o limite de ~1 GB. Causas, em ordem: DataFrame grande em cache, cache sem TTL,
lista crescendo no `session_state`. Ver [14](14-cache-e-dados.md).

**Dependências de sistema:** um `packages.txt` na raiz instala pacotes `apt`
(por exemplo, `libgl1` para o OpenCV).

---

## 4. Docker

O `Dockerfile` do [projeto-modelo](07-projeto-modelo/Dockerfile), comentado:

```dockerfile
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependências numa camada própria: o COPY do código não invalida esta.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Usuário sem privilégio: se alguém escapar do processo, não é root.
RUN useradd --create-home --uid 10001 painel \
 && mkdir -p /dados && chown -R painel:painel /dados /app
USER painel

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; \
      sys.exit(0 if urllib.request.urlopen('http://localhost:8501/_stcore/health').read()==b'ok' else 1)"

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", "--server.address=0.0.0.0", \
     "--server.headless=true", "--browser.gatherUsageStats=false"]
```

**As quatro linhas que mais importam:**

1. **`--server.address=0.0.0.0`** — sem isso, o Streamlit escuta só no localhost
   *de dentro* do contêiner, e a porta publicada não chega em ninguém. É o erro
   nº 1 de Streamlit em Docker.
2. **`--server.headless=true`** — não tenta abrir navegador nem pede e-mail.
3. **`HEALTHCHECK`** em `/_stcore/health` — o orquestrador precisa de sinal melhor
   que "o processo existe".
4. **`USER painel`** — rodar como root em contêiner é desnecessário e é achado
   garantido em qualquer auditoria.

`compose.yaml`:

```yaml
services:
  painel:
    build: .
    ports: ["8501:8501"]
    environment:
      PAINEL_AMBIENTE: prod
    volumes:
      - painel-dados:/dados       # sem isto, cada deploy apaga o banco
    restart: unless-stopped
volumes:
  painel-dados:
```

---

## 5. Proxy reverso — a parte que todo mundo erra

**O Streamlit usa WebSocket.** Qualquer proxy no caminho precisa repassá-lo, e
com tempo limite longo. O padrão do nginx é 60 segundos, e o Streamlit mantém a
conexão aberta indefinidamente — daí o sintoma clássico: **"Connecting..." a cada
minuto**.

```nginx
server {
    listen 443 ssl http2;
    server_name painel.empresa.com;

    ssl_certificate     /etc/letsencrypt/live/painel.empresa.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/painel.empresa.com/privkey.pem;

    # Precisa ser MAIOR que o server.maxUploadSize do Streamlit,
    # senão o nginx recusa com 413 antes de o app ver o arquivo.
    client_max_body_size 250M;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;

        # --- WebSocket: as duas linhas que fazem tudo funcionar ---
        proxy_set_header Upgrade    $http_upgrade;
        proxy_set_header Connection "upgrade";

        # --- Para o Streamlit saber quem ele é atrás do proxy ---
        # sem X-Forwarded-Proto, o redirecionamento do OIDC volta em http://
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host  $host;

        # --- Tempo limite: MAIOR que a sua tarefa mais longa ---
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;

        proxy_buffering off;      # streaming aparece na hora, não em blocos
    }
}
```

Traefik, com rótulos no compose:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.painel.rule=Host(`painel.empresa.com`)"
  - "traefik.http.routers.painel.entrypoints=websecure"
  - "traefik.http.routers.painel.tls.certresolver=le"
  - "traefik.http.services.painel.loadbalancer.server.port=8501"
```

O Traefik trata WebSocket automaticamente — é uma das razões para preferi-lo
quando não há um nginx já instalado.

### Servir num subcaminho

```bash
streamlit run app.py --server.baseUrlPath=painel
```

```nginx
location /painel/ {
    proxy_pass http://127.0.0.1:8501/painel/;
    # ... o resto igual
}
```

O `baseUrlPath` precisa bater com o caminho do nginx, **com** e **sem** a barra
final consistentes. É a fonte de metade dos "a página carrega mas fica em
branco".

---

## 6. Várias réplicas: sessão fixa é obrigatória

O `session_state` mora na **memória do processo**. Com duas réplicas e sem sessão
fixa (*sticky sessions*), a requisição vai para o processo A e o WebSocket para o
B — que não conhece a sessão.

```nginx
upstream painel {
    ip_hash;                    # o mais simples: fixa por IP de origem
    server 127.0.0.1:8501;
    server 127.0.0.1:8502;
}
```

No Kubernetes:

```yaml
apiVersion: v1
kind: Service
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP: { timeoutSeconds: 10800 }
```

**Limite honesto do `ip_hash`:** vários usuários atrás do mesmo NAT corporativo
caem todos no mesmo processo. Para distribuição melhor, use afinidade por cookie
(`sticky` no nginx comercial, ou o módulo `nginx-sticky-module`; no Traefik,
`loadbalancer.sticky.cookie`).

**E o deploy?** Trocar a versão **derruba todas as sessões**. Não há como evitar
com o modelo do Streamlit. O que dá para fazer:

- avisar antes (banner com data da manutenção);
- deployar fora do horário de uso;
- garantir que o estado que importa está no banco, não no `session_state` — o que,
  de novo, é a arquitetura de [23](23-arquitetura-de-app-real.md).

---

## 7. Kubernetes: o essencial

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: painel }
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: painel
        image: registry.empresa.com/painel:1.4.2      # tag imutável, nunca :latest
        ports: [{ containerPort: 8501 }]
        env:
          - name: PAINEL_AMBIENTE
            value: prod
          - name: PAINEL_BANCO_URL
            valueFrom: { secretKeyRef: { name: painel-segredos, key: banco-url } }
        readinessProbe:
          httpGet: { path: /_stcore/health, port: 8501 }
          initialDelaySeconds: 10
        livenessProbe:
          httpGet: { path: /_stcore/health, port: 8501 }
          initialDelaySeconds: 30
          periodSeconds: 30
        resources:
          requests: { memory: "512Mi", cpu: "250m" }
          limits:   { memory: "2Gi",   cpu: "1000m" }
```

**Sobre o limite de memória:** se ele for baixo demais, o `OOMKiller` mata o
processo e **todas** as sessões daquele pod caem, sem aviso e sem log útil.
Meça o uso real antes de apertar. `terminationGracePeriodSeconds` alto (120 s ou
mais) dá tempo de as sessões terminarem o que estavam fazendo.

---

## 8. Observabilidade

### Logs

```python
import logging, sys, json

class FormatoJSON(logging.Formatter):
    def format(self, r):
        return json.dumps({
            "nivel": r.levelname, "msg": r.getMessage(),
            "logger": r.name, "hora": self.formatTime(r),
            **getattr(r, "extra", {}),
        }, ensure_ascii=False)

h = logging.StreamHandler(sys.stdout)
h.setFormatter(FormatoJSON())
logging.getLogger("painel").addHandler(h)
```

Log em JSON numa linha é o que permite consultar depois (Loki, CloudWatch,
Elastic). Log solto em texto vira arqueologia.

### Métricas

O endpoint `/_stcore/metrics` já expõe métricas no formato Prometheus. Com
`server.unsafeMetricsUserAttributes` configurado, dá para rotular por usuário
(útil para contar visitantes únicos; cuidado com dado pessoal).

### Erros

Sentry funciona normalmente:

```python
import sentry_sdk
sentry_sdk.init(dsn=st.secrets["sentry"]["dsn"],
                environment=CFG.ambiente, traces_sample_rate=0.1)
```

### O que monitorar

| Métrica | Alerta quando |
|---|---|
| memória do processo | > 80% do limite |
| sessões ativas | crescimento sem queda (sessões não coletadas) |
| tempo de resposta do banco | p95 acima do seu orçamento |
| erros por minuto | qualquer aumento súbito |
| reinícios do contêiner | > 0 fora de deploy |

---

## 9. Configuração de produção

```toml
[server]
headless = true
address = "0.0.0.0"
port = 8501
enableXsrfProtection = true          # NÃO desligue
enableCORS = true
allowedHosts = ["painel.empresa.com"]   # contra rebinding de DNS
maxUploadSize = 50
websocketPingInterval = 20
disconnectedSessionTTL = 120

[client]
showErrorDetails = "none"            # nada de traceback na tela do usuário
toolbarMode = "minimal"

[browser]
gatherUsageStats = false

[logger]
level = "info"
```

`server.allowedHosts` (com o endurecimento de segurança da 1.60) é a defesa contra
*DNS rebinding*: vazio, o Streamlit aceita qualquer cabeçalho `Host`, para não
quebrar proxies de configuração dinâmica. Em produção com domínio conhecido,
preencha.

`server.trustedUserHeaders` mapeia cabeçalhos HTTP para dentro de `st.user` — é
como um proxy de autenticação (oauth2-proxy, Cloudflare Access) entrega a
identidade para a app. **Só use com um proxy confiável na frente**: se o app for
acessível diretamente, qualquer um forja o cabeçalho.

---

## 10. Lista de verificação antes de publicar

**Segurança**
- [ ] HTTPS, com redirecionamento de HTTP.
- [ ] Autenticação (OIDC ou proxy).
- [ ] `showErrorDetails = "none"`.
- [ ] `enableXsrfProtection = true`.
- [ ] `allowedHosts` preenchido.
- [ ] Segredos por variável de ambiente, fora da imagem.
- [ ] Contêiner com usuário sem privilégio.

**Confiabilidade**
- [ ] `HEALTHCHECK` / probes em `/_stcore/health`.
- [ ] `restart: unless-stopped` ou equivalente.
- [ ] Volume persistente para o que precisa sobreviver.
- [ ] Backup do banco, **testado restaurando**.
- [ ] `proxy_read_timeout` maior que a tarefa mais longa.
- [ ] Sessão fixa, se houver mais de uma réplica.

**Operação**
- [ ] Versões fixadas (`requirements.txt` ou `uv.lock`).
- [ ] Imagem com tag imutável, nunca `:latest`.
- [ ] Log em JSON, coletado.
- [ ] Alerta de memória e de erro.
- [ ] Procedimento de volta atrás documentado e testado.

**Produto**
- [ ] Tema e `toolbarMode` de produção.
- [ ] "About" com fonte do dado e horário de atualização.
- [ ] Alguém sabe a quem reclamar (e está escrito na tela).

---

## Autoteste

1. Quais são os endpoints do Streamlit e para que serve cada um?
2. Quais são as duas linhas do nginx que fazem o WebSocket funcionar, e qual é o
   sintoma de esquecê-las?
3. Por que `--server.address=0.0.0.0` em contêiner?
4. Que configuração do nginx é obrigatória para tarefa longa, e para upload grande?
5. Por que sessão fixa é obrigatória com mais de uma réplica? Qual é o limite do
   `ip_hash`?
6. O que acontece com as sessões durante um deploy, e o que fazer a respeito?
7. Cite três limites do Community Cloud e o erro mais comum lá.
8. Para que serve `server.allowedHosts`, e por que ele vem vazio por padrão?
9. O que `server.trustedUserHeaders` faz, e qual é o pré-requisito de segurança?
10. Cinco itens da lista de verificação de segurança antes de publicar.
