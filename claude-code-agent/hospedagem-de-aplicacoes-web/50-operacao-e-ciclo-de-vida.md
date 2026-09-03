# 50 · Operação — o que vem depois do primeiro deploy

`Nível: intermediário a avançado` · `Atualizado em 18/08/2026`

Hospedar é fácil. **Operar** é o trabalho. Este capítulo cobre o que separa "está no ar" de
"posso confiar nisso".

---

## 1. Domínio

**Comprar.** Registrador é diferente de hospedagem. Recomendações honestas:

| Registrador | Observação |
|---|---|
| **Registro.br** | obrigatório para `.br`; barato (~R$ 40/ano), interface antiga, sem enrolação |
| **Cloudflare Registrar** | vende **a preço de custo**, sem margem, com WHOIS privado incluído. Não vende `.com.br` |
| **Namecheap, Porkbun** | bons preços, sem armadilha de renovação |
| ⚠️ promoções de R$ 5 no primeiro ano | a renovação costuma custar 5 a 10× — leia o preço do **segundo** ano |

**Delegar o DNS.** Aponte os *nameservers* do domínio para quem vai gerenciar as zonas
(Cloudflare é a escolha padrão: gratuito, rápido, com API). Isso é independente de onde o site
está hospedado.

**Registros que você vai criar:**

| Objetivo | Tipo | Exemplo |
|---|---|---|
| Subdomínio para a app | `CNAME` | `app` → `meu-app.onrender.com` |
| Domínio raiz | `A`/`AAAA`, ou `ALIAS`/*flattening* | `@` → IP ou alias |
| E-mail (envio) | `TXT` (SPF), `TXT` (DKIM), `TXT` (DMARC) | veja abaixo |
| Verificação de propriedade | `TXT` | valor dado pela plataforma |

**TTL.** É o tempo que os resolvedores guardam a resposta. Antes de uma migração, **baixe o
TTL para 300 s com pelo menos 24 h de antecedência**; depois de estabilizar, volte para
3600 s. Quem esquece isso passa horas com metade dos usuários no servidor velho.

```bash
dig +short app.exemplo.com.br
dig +trace exemplo.com.br | tail -5      # vê a delegação inteira
dig @1.1.1.1 exemplo.com.br SOA          # confirma qual servidor é autoritativo
```

---

## 2. TLS

Hoje é resolvido: a plataforma emite e renova sozinha, via Let's Encrypt (ACME). Você só
precisa saber depurar.

```bash
curl -sI https://app.exemplo.com.br | head -3
openssl s_client -connect app.exemplo.com.br:443 -servername app.exemplo.com.br </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
```

**A configuração que mais confunde: os modos SSL da Cloudflare.**

| Modo | Navegador↔Cloudflare | Cloudflare↔origem | Veredito |
|---|---|---|---|
| Off | HTTP | HTTP | nunca |
| **Flexible** | HTTPS | **HTTP** | ⚠️ **evite**: gera laço de redirecionamento se a origem força HTTPS, e o trecho final é aberto |
| Full | HTTPS | HTTPS, **sem validar** o certificado | aceitável para origem com certificado autoassinado |
| **Full (strict)** | HTTPS | HTTPS validado | ✅ **o correto** |

`ERR_TOO_MANY_REDIRECTS` logo depois de colocar o site atrás da Cloudflare = modo Flexible +
aplicação redirecionando para HTTPS. Troque para Full (strict).

---

## 3. Segredos

Regras, em ordem de importância:

1. **Nunca no Git.** `.env` no `.gitignore`; versione `.env.example` sem valores.
2. **Segredo que foi ao Git está queimado.** Remover no commit seguinte não resolve: ele fica
   no histórico, nos forks e nos caches. **Rotacione.**
3. **Use o cofre da plataforma** (`flyctl secrets`, Render Environment, `wrangler secret`).
4. **Em CI, use `secrets` do provedor**, nunca texto no YAML.
5. **Nunca imprima o valor**, só a chave.
6. **Prefira credenciais com expiração** a senhas eternas.
7. **Um segredo por ambiente.** A mesma senha em desenvolvimento e produção anula a separação.

Detecção e limpeza:

```bash
gitleaks detect --source .            # varre o histórico procurando segredo
trufflehog git file://.               # alternativa
```

Se vazou: **rotacione primeiro**, reescreva o histórico depois (`git filter-repo`), e assuma
que alguém já copiou. Existem robôs que varrem o GitHub em segundos procurando chaves da AWS.

---

## 4. Migrações de banco

O tema com maior potencial de estrago.

**As cinco regras:**

1. **Sempre por ferramenta com histórico** (node-pg-migrate, Prisma, Drizzle, Flyway, Alembic).
2. **Sempre compatível para trás.** Durante o rollout, código velho e novo rodam juntos.
3. **Nunca renomeie nem remova coluna no mesmo deploy que muda o código.** Use
   *expand/contract* (veja [`12`](12-anatomia-de-um-deploy.md), etapa 9).
4. **Índice em tabela grande, sempre `CONCURRENTLY`** — senão você trava escritas.
5. **Migração longa (`UPDATE` em milhões de linhas) roda em lotes, fora do deploy.**

```sql
-- Errado: trava a tabela inteira e o deploy estoura o timeout
UPDATE pedido SET status = 'novo' WHERE status IS NULL;

-- Certo: em lotes, com pausa, sem segurar transação longa
DO $$
DECLARE afetadas int;
BEGIN
  LOOP
    UPDATE pedido SET status = 'novo'
    WHERE id IN (SELECT id FROM pedido WHERE status IS NULL LIMIT 5000);
    GET DIAGNOSTICS afetadas = ROW_COUNT;
    EXIT WHEN afetadas = 0;
    COMMIT;
    PERFORM pg_sleep(0.1);
  END LOOP;
END $$;
```

**`ALTER TABLE` que trava e `ALTER TABLE` que não trava** (PostgreSQL 11+):

| Operação | Trava? |
|---|---|
| `ADD COLUMN` sem default | não (instantâneo) |
| `ADD COLUMN ... DEFAULT valor` | **não**, desde a versão 11 (antes reescrevia a tabela) |
| `ADD COLUMN ... NOT NULL` sem default | **sim**, e falha se houver linhas |
| `DROP COLUMN` | não (só marca) |
| `ALTER COLUMN TYPE` | **sim, reescreve a tabela** — o mais perigoso |
| `ADD CONSTRAINT ... NOT VALID` seguido de `VALIDATE` | não trava (é o truque certo) |
| `CREATE INDEX` | **sim** |
| `CREATE INDEX CONCURRENTLY` | não (mas não pode estar em transação) |

---

## 5. Backup — o único item irreversível

**A regra 3-2-1:** três cópias, em dois meios diferentes, uma fora do local.
Na prática moderna: o backup do provedor + um `pg_dump` seu em outro provedor.

```bash
pg_dump -Fc --no-owner "$DATABASE_URL" > backup.dump
pg_restore --list backup.dump | head          # o arquivo é legível?
```

**Automatize** com o workflow do [`06-exemplos.md`](06-exemplos.md), exemplo 12 (GitHub
Actions + `pg_dump` + GPG + artefato ou R2). Custa zero.

**Teste a restauração.** Um backup nunca restaurado não é backup — é esperança. Marque um
lembrete trimestral:

```bash
createdb teste_restauracao
pg_restore --no-owner --clean --if-exists -d teste_restauracao backup.dump
psql teste_restauracao -c "SELECT count(*) FROM tabela_principal;"
dropdb teste_restauracao
```

**Defina e escreva dois números**, porque eles definem quanto você precisa investir:

- **RPO** (*Recovery Point Objective*): quanto de dado você aceita perder. Backup diário ⇒
  RPO de 24 h.
- **RTO** (*Recovery Time Objective*): em quanto tempo você precisa estar de pé.

Se o RPO real do negócio é 1 hora e você faz backup diário, **você tem um problema hoje**, não
no dia do incidente. E não esqueça: **também é preciso apagar** (LGPD, art. 16) — backup eterno
com dado pessoal é passivo jurídico.

---

## 6. CI/CD

Pipeline mínimo defensável:

```
push → lint → testes → build → deploy em staging → teste de fumaça → deploy em produção
                ↑                                                          │
                └────────────── falhou? não avança ────────────────────────┘
```

O YAML completo está em [`05-manual-de-uso.md`](05-manual-de-uso.md), seção 12. Pontos que
importam:

- **`npm ci`, nunca `npm install`** em CI.
- **Serviços efêmeros** (Postgres e Redis como `services:`) para testar de verdade.
- **Deploy só a partir da branch padrão**, e só se os testes passarem.
- **Ambiente de preview por pull request** quando a plataforma oferece (Render, Vercel,
  Netlify, Cloudflare, Northflank) — revisar visualmente antes de mesclar vale muito.
- **Tempo total abaixo de 10 minutos.** Acima disso, as pessoas param de fazer deploys
  pequenos, e deploy grande é onde moram os incidentes.

---

## 7. Observabilidade

Três pilares, e o que usar de graça:

| Pilar | O que responde | Ferramenta gratuita |
|---|---|---|
| **Logs** | o que aconteceu | painel da plataforma (retenção curta), Better Stack, Axiom, Grafana Loki |
| **Métricas** | quanto e com que frequência | painel da plataforma, Grafana Cloud (plano gratuito), Prometheus |
| **Traces** | por onde passou e onde demorou | Sentry, Grafana Tempo, OpenTelemetry |

**Log estruturado, sempre.** Uma linha JSON por evento:

```js
console.log(JSON.stringify({
  nivel: "info", evento: "pedido_criado",
  pedido_id: id, usuario_id: uid, ms: duracao, trace_id: traceId,
}));
```

Por quê: texto livre exige parser frágil; JSON é filtrável por campo em qualquer coletor. E
**nunca** registre senha, token, cartão ou dado pessoal desnecessário.

**Os quatro sinais de ouro** (do livro *Site Reliability Engineering*, do Google):

| Sinal | O que medir | Alerta razoável |
|---|---|---|
| **Latência** | p50, p95, **p99** | p99 > 1 s por 5 minutos |
| **Tráfego** | requisições por segundo | queda de 80% em relação ao normal |
| **Erros** | taxa de 5xx | > 1% por 5 minutos |
| **Saturação** | CPU, memória, conexões do banco, disco | disco > 80%, conexões > 80% do limite |

**Monitoramento externo é obrigatório.** A plataforma não avisa que caiu. UptimeRobot e Better
Stack têm plano gratuito que checa a cada 3–5 minutos e manda alerta.

> **Alerta que não gera ação deve ser apagado.** Fadiga de alerta é o que faz alguém ignorar
> o aviso que realmente importava. Se um alerta dispara toda semana e ninguém faz nada, ele
> está mentindo — ou o limiar está errado, ou o problema é aceitável.

---

## 8. Escala — na ordem certa

Quando ficar lento, siga esta ordem. Ela é decrescente em retorno por esforço:

1. **Meça.** Sem `EXPLAIN ANALYZE` e sem p99, você está adivinhando.
2. **Índice.** 80% das lentidões de aplicação CRUD são varredura sequencial evitável.
3. **N+1.** Uma consulta por item de lista. Corrija com `JOIN` ou carregamento em lote.
4. **Cache.** Só depois de 2 e 3 — cache mascara consulta ruim e a dívida volta maior.
5. **Vertical.** Máquina maior. Simples, imediato, com teto.
6. **Horizontal.** Mais instâncias. Exige stateless de verdade.
7. **Réplica de leitura.** Distribui leitura; **atenção ao atraso de replicação** (ler logo
   após escrever pode devolver dado velho).
8. **Particionar / fragmentar (*sharding*).** Complexidade alta. Última opção.

> **A escrita é o gargalo final.** Leitura escala com cache e réplica; escrita, não. Todo
> sistema que cresce muito acaba enfrentando o limite de escrita de um único primário. Se você
> chegar lá, [`60-teoria-avancada.md`](60-teoria-avancada.md) discute as saídas.

---

## 9. Segurança operacional — o mínimo

- [ ] Banco e Redis **nunca** expostos à internet (bind em `127.0.0.1` ou rede privada)
- [ ] TLS em tudo, inclusive entre app e banco (`sslmode=require`)
- [ ] Senhas fortes e distintas por ambiente
- [ ] Dependências atualizadas (`npm audit`, Dependabot)
- [ ] Rate limit nas rotas de autenticação
- [ ] Cabeçalhos de segurança (`X-Content-Type-Options`, `Referrer-Policy`, CSP)
- [ ] CORS restrito à sua origem, não `*`
- [ ] Consulta parametrizada sempre (nada de concatenar SQL)
- [ ] Erro genérico ao cliente; detalhe só no log
- [ ] Container como usuário sem privilégio
- [ ] Acesso administrativo com 2FA
- [ ] Menor privilégio no banco: a aplicação **não** precisa ser superusuário

Veja também [`ethical-hacking`](../ethical-hacking/00-MAPA.md) e
[`variaveis-de-ambiente-e-segredos`](../variaveis-de-ambiente-e-segredos/01-introducao-leigo.md).

---

## 10. Quando quebrar — o roteiro de incidente

```
1. ESTANCAR      rollback do último deploy. Antes de entender. A prioridade é o usuário.
2. COMUNICAR     avise quem depende. Silêncio custa mais confiança que a falha.
3. DIAGNOSTICAR  o que mudou? (deploy, migração, variável, provedor, pico, cota estourada)
4. CORRIGIR      preferir rolar para frente a improvisar em produção.
5. ESCREVER      post-mortem SEM CULPADO: linha do tempo, causa, o que evita a repetição.
```

**As cinco perguntas que resolvem a maioria dos incidentes:**

1. O que mudou nas últimas 24 horas?
2. O health check está passando? O que ele diz?
3. O banco está aceitando conexões? Quantas estão abertas?
4. Alguma cota estourou (comandos do Redis, banda, minutos de build, créditos)?
5. É problema meu ou do provedor? (verifique a página de status)

**Post-mortem sem culpado** não é gentileza: é engenharia. Onde se procura culpado, as pessoas
escondem informação, e você perde a chance de consertar a causa real. A causa quase nunca é
uma pessoa; é um sistema que permitiu o erro.

---

## Autoteste

1. Por que baixar o TTL antes de uma migração de DNS, e com quanta antecedência?
2. O que é o modo Flexible da Cloudflare e que erro literal ele produz?
3. Um segredo vazou no Git. Qual é a primeira ação, e por quê não é apagar o commit?
4. Quais operações de `ALTER TABLE` travam a tabela, e qual é o truque para adicionar constraint sem travar?
5. O que são RPO e RTO, e como você descobre se o seu backup atual é insuficiente?
6. Cite os quatro sinais de ouro e um alerta razoável para cada um.
7. Qual é a ordem correta de otimização quando o sistema fica lento, e por que cache não é o primeiro passo?
8. Quais são os cinco passos do roteiro de incidente, e por que "estancar" vem antes de "diagnosticar"?

---

### Fontes consultadas (18/08/2026)

- Google — *Site Reliability Engineering* (os quatro sinais de ouro; disponível gratuitamente em sre.google/books)
- PostgreSQL 18 — documentação de `ALTER TABLE`, `CREATE INDEX CONCURRENTLY` e bloqueios
- Let's Encrypt / RFC 8555 (ACME)
- Cloudflare — documentação dos modos de SSL/TLS
- OpenTelemetry — especificação de traces e métricas
- Lei nº 13.709/2018 (LGPD), art. 16 (eliminação) e art. 46 (segurança)
