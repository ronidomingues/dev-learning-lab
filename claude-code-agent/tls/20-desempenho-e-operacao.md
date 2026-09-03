# 20 · Desempenho e operação

**Nível:** avançado · **Data:** 31/08/2026

Quanto o TLS custa de verdade, onde o custo está, e como operá-lo sem incidentes.
Os números de CPU abaixo foram **medidos nesta máquina** com `openssl speed` em
31/08/2026 (OpenSSL 3.0.2, CPU x86-64 com AES-NI).

---

## 1. "TLS é lento" — o mito e o número

Em 2010 isso tinha algum fundamento. Hoje, não. O Google publicou, quando ligou HTTPS
por padrão no Gmail em 2010, que a mudança custou **menos de 1% de CPU adicional**,
**menos de 10 KB de memória por conexão** e **menos de 2% de tráfego de rede** — sem
nenhum hardware novo. É a citação canônica do assunto, de Adam Langley.

Medição local, para você ter ordem de grandeza:

```bash
openssl speed -seconds 1 ecdsap256 rsa2048
openssl speed -seconds 1 -evp aes-128-gcm
```

Saída real desta máquina:

```
                              sign     verify   sign/s  verify/s
rsa 2048 bits              0.000567s 0.000016s   1763.0   60793.0
256 bits ecdsa (nistp256)    0.0000s   0.0001s  45031.0   15492.0

AES-128-GCM        8192 bytes: 5.487.696 kB/s   (~5,5 GB/s por núcleo)
ChaCha20-Poly1305  8192 bytes: 2.104.926 kB/s   (~2,1 GB/s por núcleo)
```

**O que esses números dizem:**

1. **Assinar com RSA-2048: ~1.763 por segundo.** Como o servidor assina uma vez por
   handshake completo, um núcleo sustenta ~1.700 handshakes novos/s. Com ECDSA P-256:
   **~45.000/s** — 25× mais. É por isso que certificados EC importam para quem tem escala.
2. **Verificar é o inverso.** RSA verifica ~60.000/s e ECDSA ~15.000/s. Ou seja: RSA
   é caro para o **servidor** e barato para o **cliente**; ECDSA, o contrário. Como o
   servidor é quem tem gargalo, ECDSA vence.
3. **A cifra simétrica é essencialmente gratuita:** 5,5 GB/s por núcleo. Saturar
   10 Gbit/s (1,25 GB/s) consome ~23% de **um** núcleo. O tráfego não é o problema.
4. **ChaCha20 rende ~38% do AES-GCM aqui** — porque esta CPU tem AES-NI. Numa CPU sem
   AES-NI a relação se inverte, e é exatamente por isso que se oferece as duas e se
   deixa o **cliente** escolher ([17 §2](17-configuracao-de-servidores.md)).

> **Conclusão prática:** o custo do TLS está **no handshake**, não no tráfego. Toda
> otimização séria de TLS é sobre **evitar handshakes completos**.

---

## 2. Latência: onde os milissegundos vão

Com 50 ms de RTT entre cliente e servidor:

| Etapa | TLS 1.2 | TLS 1.3 | TLS 1.3 + retomada | QUIC 0-RTT |
|---|---|---|---|---|
| DNS | 50 ms | 50 ms | 50 ms | 50 ms |
| TCP handshake | 50 ms | 50 ms | 50 ms | — (fundido) |
| TLS handshake | 100 ms | 50 ms | 0 ms* | 0 ms |
| primeiro byte da resposta | 50 ms | 50 ms | 50 ms | 50 ms |
| **total** | **250 ms** | **200 ms** | **150 ms** | **100 ms** |

\* a retomada em 1-RTT ainda gasta um RTT no handshake, mas ele acontece **em paralelo**
com o envio dos dados quando há 0-RTT.

**As alavancas, em ordem de impacto:**

1. **Reduzir o RTT.** Um CDN ou um POP mais próximo corta 100 ms. Nenhuma otimização
   de cifra chega perto disso. Esta é, disparada, a alavanca nº 1.
2. **Retomada de sessão.** Elimina o handshake completo em visitas subsequentes.
3. **TLS 1.3 em vez de 1.2.** Um RTT a menos, de graça.
4. **Reuso de conexão** (keep-alive, HTTP/2, pool de conexões no cliente). Um cliente
   que abre conexão nova a cada requisição paga o handshake toda vez — erro comum em
   código de servidor que chama API.
5. **OCSP stapling.** Remove uma consulta HTTP síncrona do caminho crítico.
6. **Certificado menor.** Cadeia ECDSA curta cabe em menos pacotes; RSA-4096 com três
   intermediários pode estourar a janela inicial de congestionamento e custar um RTT extra.

---

## 3. Retomada de sessão na prática

| Mecanismo | Estado | Entre máquinas? | Sigilo futuro |
|---|---|---|---|
| **Session ID / cache** | no servidor | não, sem cache compartilhado | ✅ preservado |
| **Session tickets** | no cliente | sim | ⚠️ depende da rotação da chave de ticket |
| **PSK do TLS 1.3 (`psk_dhe_ke`)** | ticket + nova troca ECDHE | sim | ✅ preservado |

```nginx
ssl_session_cache   shared:SSL:50m;   # ~200.000 sessões
ssl_session_timeout 1d;
ssl_session_tickets off;              # ver [17 §2.1]
```

**Medir se está funcionando:**

```bash
# handshake completo vs. retomado
openssl s_client -connect exemplo.com.br:443 -servername exemplo.com.br \
  -sess_out /tmp/s.pem </dev/null >/dev/null 2>&1
openssl s_client -connect exemplo.com.br:443 -servername exemplo.com.br \
  -sess_in /tmp/s.pem </dev/null 2>&1 | grep -E "Reused|New"
# esperado: "Reused, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384"
```

No nginx, exponha a taxa de reuso no log e observe-a:

```nginx
log_format tls '$remote_addr $ssl_protocol $ssl_cipher reused=$ssl_session_reused';
```

Taxa de reuso abaixo de 50% em tráfego de navegador é sinal de configuração errada
(cache pequeno demais, ou balanceador espalhando o mesmo cliente entre nós).

---

## 4. 0-RTT: quando vale e quando é perigoso

| Vale | Não vale |
|---|---|
| `GET` de conteúdo estático | qualquer `POST`, `PUT`, `DELETE` |
| APIs idempotentes | operações financeiras |
| pré-conexão a CDN | qualquer coisa com efeito colateral |

O risco não é teórico nem corrigível: **dados 0-RTT podem ser repetidos** por um
atacante que capture o pacote, porque não houve nada de novo trocado que prove frescor.

```nginx
ssl_early_data on;

location / {
    proxy_pass http://app;
    # a aplicação PRECISA saber que aquilo veio em 0-RTT e recusar o que não for seguro
    proxy_set_header Early-Data $ssl_early_data;
}
```

A aplicação deve responder **425 Too Early** para requisições não idempotentes que
chegaram com `Early-Data: 1`.

---

## 5. Terminação e offload

| Estratégia | Quando |
|---|---|
| **na aplicação** | serviço único, tráfego moderado |
| **em proxy reverso** (nginx/HAProxy) | o padrão; centraliza certificado e configuração |
| **no balanceador da nuvem** (ALB, GCLB) | gerenciado; o certificado vive lá |
| **no CDN** (Cloudflare, Fastly, Akamai) | melhor latência possível: termina perto do usuário |
| **em hardware/aceleradora** | raro hoje; a CPU moderna já é rápida o bastante |

**A pergunta que importa não é "quanto custa", é "onde o texto claro existe".**
Terminar no CDN significa que o CDN **lê tudo** — inclusive senhas e dados pessoais.
É uma decisão de confiança e, no Brasil, de **LGPD** (o CDN é operador de dados
pessoais e isso precisa estar previsto em contrato), não uma decisão técnica.

---

## 6. Observabilidade

**O que registrar em log** (nginx):

```nginx
log_format tls_json escape=json '{'
  '"ts":"$time_iso8601",'
  '"host":"$host",'
  '"proto":"$ssl_protocol",'
  '"cipher":"$ssl_cipher",'
  '"curve":"$ssl_curve",'          # nginx ≥1.21.5
  '"reused":"$ssl_session_reused",'
  '"sni":"$ssl_server_name",'
  '"alpn":"$ssl_alpn_protocol",'
  '"client_dn":"$ssl_client_s_dn",'   # mTLS
  '"client_verify":"$ssl_client_verify",'
  '"status":$status,'
  '"handshake_time":$ssl_handshake_time'  # nginx ≥1.27
'}';
```

**As quatro métricas que valem alerta:**

| Métrica | Por quê |
|---|---|
| **dias até o vencimento** de cada certificado | evita o incidente mais comum e mais bobo |
| **taxa de erro de handshake** | um pico indica configuração quebrada, cliente antigo, ou ataque |
| **fatia de TLS 1.2 × 1.3** | mostra quando é seguro desligar o 1.2 |
| **taxa de reuso de sessão** | queda repentina = cache quebrado ou balanceamento errado |

Painel mínimo, sem instalar nada:

```bash
awk -F'"' '{print $4, $8}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head
```

---

## 7. Depuração em produção

```bash
# 1. O que o cliente vê
curl -vI https://exemplo.com.br 2>&1 | grep -E "SSL|TLS|subject|issuer|ALPN"

# 2. O que foi negociado
echo | openssl s_client -connect exemplo.com.br:443 -servername exemplo.com.br -brief

# 3. Erros de handshake no servidor
sudo journalctl -u nginx -f | grep -i ssl
sudo tail -f /var/log/nginx/error.log | grep -i "SSL_"

# 4. Quantas conexões ativas e em que estado
ss -tan state established '( dport = :443 or sport = :443 )' | wc -l

# 5. Handshakes por segundo (aproximado, pelo log)
awk -v d="$(date -d '1 min ago' +%d/%b/%Y:%H:%M)" '$0 ~ d' /var/log/nginx/access.log | wc -l

# 6. Capturar apenas handshakes que FALHARAM
sudo tshark -i any -f "port 443" -Y "tls.alert_message" -T fields \
  -e ip.src -e tls.alert_message.desc
```

**Erros no log do nginx e o que significam:**

| Log | Causa |
|---|---|
| `SSL_do_handshake() failed ... no shared cipher` | cliente antigo demais, ou lista de cifras restritiva demais |
| `SSL_do_handshake() failed ... unknown ca` | mTLS: cliente com certificado de outra CA |
| `SSL_read() failed ... bad certificate` | certificado de cliente malformado |
| `SSL_do_handshake() ... http request` | alguém falou HTTP em claro na porta 443 (varredura, ou cliente mal configurado) |
| `no suitable key share` | grupos incompatíveis |

---

## 8. Rotina de operação

**Diária (automatizada):**
- verificar validade de todos os certificados, de fora
- confirmar que o serviço de renovação rodou
- checar novos certificados nos logs de CT para os seus domínios

**Semanal:**
- revisar erros de handshake (picos, clientes novos falhando)
- conferir se há CVE nova na sua pilha TLS (`apt list --upgradable | grep ssl`)

**Mensal:**
- rodar `testssl.sh` ou SSL Labs e comparar com o mês anterior
- revisar a fatia de TLS 1.2 e decidir sobre desligá-lo

**Trimestral / semestral:**
- ensaiar a **rotação de CA interna** ([18 §6](18-mtls-e-pki-interna.md))
- revisar a lista de cifras contra a recomendação atual da Mozilla
- testar o procedimento de emergência (§9)

---

## 9. Procedimento de emergência: chave privada comprometida

Escreva isto **antes** de precisar. Ordem importa.

```
1. GERE UMA CHAVE NOVA. Nunca reemita com a mesma chave.
      openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out nova.key

2. EMITA UM CERTIFICADO NOVO e coloque em produção.
      certbot certonly --force-renewal --key-type ecdsa -d exemplo.com.br
      → recarregue os serviços; confirme com curl que o novo está no ar

3. REVOGUE O ANTIGO.
      certbot revoke --cert-path /caminho/antigo/cert.pem --reason keyCompromise
      (aceite que a revogação tem efeito limitado — [15](15-validacao-revogacao-transparencia.md))

4. INVALIDE AS SESSÕES.
      limpe o cache de sessão e as chaves de ticket; reinicie (não recarregue) o servidor.
      Sessões retomadas com a chave antiga continuariam válidas.

5. INVESTIGUE COMO VAZOU.
      backup? repositório? log? dump de memória? acesso indevido?
      Se você não sabe como vazou, não sabe se ainda está vazando.

6. PROCURE OUTROS USOS DA MESMA CHAVE.
      grep -rl "BEGIN.*PRIVATE KEY" /etc /opt /srv 2>/dev/null
      Chaves são copiadas entre serviços com mais frequência do que se admite.

7. MONITORE OS LOGS DE CT por emissões que você não fez.

8. ESCREVA O POST-MORTEM. O incidente só termina quando a causa raiz é corrigida.
```

---

## Autoteste

1. Onde está o custo de CPU do TLS: no handshake ou no tráfego? Justifique com números.
2. Por que ECDSA é melhor que RSA para o servidor, mas o inverso vale para o cliente?
3. Qual é a alavanca nº 1 de latência em TLS, e por que ela supera qualquer escolha de cifra?
4. Compare os três mecanismos de retomada quanto ao sigilo futuro.
5. Como medir se a retomada de sessão está funcionando?
6. Quando 0-RTT é seguro, e o que a aplicação deve responder para o que não é?
7. Terminar TLS no CDN é uma decisão técnica? Justifique.
8. Cite as quatro métricas de TLS que merecem alerta.
9. O log mostra `no shared cipher`. Duas hipóteses?
10. Liste, em ordem, os oito passos do procedimento de chave comprometida. Por que revogar vem **depois** de emitir o novo?

*Respostas: §1, §1, §2, §3, §3, §4, §5, §6, §7, §9.*

---

**Próximo:** [21-ataques-e-defesas.md](21-ataques-e-defesas.md) — o catálogo completo.
