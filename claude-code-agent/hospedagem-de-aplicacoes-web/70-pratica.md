# 70 · Prática — 12 laboratórios progressivos

`Nível: iniciante a avançado` · `Atualizado em 18/08/2026`

Cada laboratório tem **objetivo, passos, critério de sucesso e o que ele ensina**. Faça na
ordem. Os de número 9 a 12 simulam incidentes de propósito — são os mais valiosos.

Pré-requisito: ambiente do [`03-instalacao.md`](03-instalacao.md) e o
[`07-projeto-modelo/`](07-projeto-modelo/README.md).

---

## Lab 1 — Primeiro deploy (30 min · iniciante)

**Objetivo.** Do `git init` a uma URL pública HTTPS.

1. Crie a aplicação mínima do [`04-como-comecar.md`](04-como-comecar.md), Parte 0.
2. Publique no GitHub com `gh repo create`.
3. Faça deploy no Render (plano Free).
4. Acesse a URL.

**Sucesso:** `curl -s https://SEU-APP.onrender.com/health` devolve `{"ok":true}`.

**Ensina:** o ciclo completo, e que a plataforma escolhe a porta.

**Experimento obrigatório:** espere 20 minutos sem acessar e cronometre a próxima requisição:
```bash
time curl -s -o /dev/null https://SEU-APP.onrender.com/health
```
Anote o número. É o cold start de que fala [`60`](60-teoria-avancada.md), seção 1.

---

## Lab 2 — Quebre de propósito (20 min · iniciante)

**Objetivo.** Provocar os cinco erros mais comuns e reconhecê-los pela mensagem.

Faça um de cada vez, observe a mensagem exata no log e depois reverta:

| Sabotagem | Erro esperado |
|---|---|
| trocar `0.0.0.0` por `127.0.0.1` | `no open ports detected` / `502` |
| fixar `const port = 3000` ignorando `process.env.PORT` | idem |
| remover `pg` do `package.json` | `Cannot find module 'pg'` no build ou na partida |
| apontar `DATABASE_URL` para um host inexistente | `getaddrinfo ENOTFOUND` |
| tirar `?sslmode=require` da URL | `no pg_hba.conf entry ... no encryption` |

**Sucesso:** você provocou e leu as cinco mensagens.

**Ensina:** reconhecer erro por sintoma é o que separa 10 minutos de 3 horas de depuração.

---

## Lab 3 — Ambiente local completo (30 min · iniciante)

**Objetivo.** Subir a pilha inteira com Docker Compose.

```bash
cd 07-projeto-modelo
docker compose up --build -d
docker compose ps
docker compose exec api npm run migrate
curl -s localhost:3000/health | jq
```

**Sucesso:** `{"ok":true,"banco":"up","cache":"up","modo":"postgres+redis"}`.

**Experimento:** remova `condition: service_healthy` do `depends_on`, rode
`docker compose down && docker compose up`, e observe a API morrer com `ECONNREFUSED`.
Depois devolva. **Ensina:** por que "esperar iniciar" é diferente de "esperar ficar pronto".

---

## Lab 4 — Meça o cache (30 min · iniciante)

**Objetivo.** Ver com números o que o Redis faz.

```bash
# sem cache: force a rota a ir ao banco toda vez
for i in $(seq 1 20); do curl -s -o /dev/null -w "%{time_total}\n" localhost:3000/api/stats; done

# com cache quente (as chamadas seguintes)
for i in $(seq 1 20); do curl -s -o /dev/null -w "%{time_total}\n" localhost:3000/api/stats; done
```

Calcule média e mediana das duas séries.

**Sucesso:** você tem dois números e sabe explicar a diferença.

**Ensina:** cache não é fé, é medição — e a diferença é geralmente de uma ordem de grandeza.

---

## Lab 5 — Estoure o limite de conexões (40 min · intermediário)

**Objetivo.** Reproduzir o gargalo escondido de [`60`](60-teoria-avancada.md), seção 3.

1. No `repositorio-pg.js`, troque o `Pool` por um `Client` novo a cada consulta.
2. Rode `autocannon -c 60 -d 20 http://localhost:3000/api/stats`.
3. Observe os erros e o `pg_stat_activity`:

```sql
SELECT count(*), state FROM pg_stat_activity GROUP BY state;
```

**Sucesso:** você viu `remaining connection slots are reserved` ou `too many clients already`,
e depois viu o problema sumir ao voltar para o pool.

**Ensina:** por que pool não é detalhe, e por que `max` alto não é "mais rápido".

---

## Lab 6 — Migração sem queda (45 min · intermediário)

**Objetivo.** Aplicar *expand/contract*.

1. Acrescente a coluna `titulo text` (nula) via nova migração. Deploy.
2. Faça o código escrever `titulo` e continuar lendo o campo antigo. Deploy.
3. Preencha os registros antigos **em lotes** (veja [`50`](50-operacao-e-ciclo-de-vida.md),
   seção 4).
4. Faça o código ler `titulo`. Deploy.
5. Remova o campo antigo. Deploy.

**Sucesso:** cinco deploys, nenhuma requisição com erro.

**Experimento de contraste:** num banco descartável, faça tudo num deploy só e observe o erro
durante o rollout. **Ensina:** por que migração compatível para trás não é preciosismo.

---

## Lab 7 — Domínio e TLS (30 min · intermediário)

**Objetivo.** Publicar em domínio próprio, com HTTPS válido.

1. Registre um domínio (Registro.br para `.com.br`, ~R$ 40/ano) ou use um que você já tenha.
2. Delegue o DNS à Cloudflare.
3. Crie o `CNAME` apontando para a plataforma.
4. Adicione o domínio no painel da plataforma e aguarde o certificado.

**Sucesso:**
```bash
curl -sI https://app.seudominio.com.br | head -3      # HTTP/2 200
openssl s_client -connect app.seudominio.com.br:443 -servername app.seudominio.com.br \
  </dev/null 2>/dev/null | openssl x509 -noout -dates
```

**Ensina:** a ordem importa — DNS antes do certificado (desafio HTTP-01).

---

## Lab 8 — CI que impede deploy quebrado (45 min · intermediário)

**Objetivo.** Pipeline com testes de verdade.

Use o `.github/workflows/ci.yml` do projeto-modelo. Depois:

1. Quebre um teste de propósito e faça `push` numa branch. Confirme que o CI falha.
2. Abra um PR e confirme que o merge é bloqueado (proteção de branch).
3. Conserte e confirme que passa e implanta.

**Sucesso:** um PR vermelho e um verde, com o deploy só acontecendo no verde.

**Ensina:** CI que não bloqueia nada é decoração.

---

## Lab 9 — Rollback sob pressão (30 min · intermediário) ⚠️

**Objetivo.** Praticar o que você vai precisar num dia ruim.

1. Faça deploy de uma versão que quebra na partida (ex.: `throw new Error("boom")` no topo).
2. **Cronometre**: quanto tempo até você perceber? Até restaurar?
3. Restaure pelo painel.
4. Depois, faça `git revert` e `push`.

**Sucesso:** menos de 5 minutos entre detectar e restaurar, e o repositório consistente.

**Ensina:** rollback pelo painel estanca; `git revert` fecha a ferida. E que você precisa
saber onde fica o botão **antes** da emergência.

---

## Lab 10 — Teste de carga e leitura de percentis (60 min · avançado)

**Objetivo.** Descobrir o seu limite antes que o usuário descubra.

```bash
autocannon -c 10  -d 30 -l http://localhost:3000/api/stats
autocannon -c 50  -d 30 -l http://localhost:3000/api/stats
autocannon -c 200 -d 30 -l http://localhost:3000/api/stats
```

Monte a tabela: concorrência × req/s × p50 × p99 × erros.

**Sucesso:** você identifica o ponto em que o p99 dispara (o "joelho" da curva) e explica por
quê usando a fórmula `1/(1−ρ)` de [`60`](60-teoria-avancada.md), seção 2.

**Ensina:** capacidade é uma curva, não um número; e a degradação não é linear.

---

## Lab 11 — Simule a estampida (45 min · avançado) ⚠️

**Objetivo.** Ver o desastre da seção 4.1 de [`60`](60-teoria-avancada.md) acontecer.

1. Ponha um `await new Promise(r => setTimeout(r, 800))` antes da consulta ao banco, simulando
   uma consulta pesada.
2. Reduza o TTL do cache para 5 s.
3. Rode `autocannon -c 100 -d 30`.
4. Observe o `pg_stat_activity` durante o teste e conte as consultas simultâneas.
5. Aplique o single-flight do [`06-exemplos.md`](06-exemplos.md), exemplo 3.
6. Repita e compare.

**Sucesso:** você mediu N consultas simultâneas antes e ~1 depois.

**Ensina:** uma trava de 15 linhas evita uma queda.

---

## Lab 12 — Restauração de backup, do zero (60 min · avançado) ⚠️

**Objetivo.** O laboratório mais importante deste arquivo.

1. Configure o backup automático do [`06-exemplos.md`](06-exemplos.md), exemplo 12.
2. Espere um ciclo (ou dispare manualmente com `workflow_dispatch`).
3. **Apague o banco de desenvolvimento inteiro.** De propósito. Sério.
4. Restaure a partir do backup, **cronometrando**.
5. Verifique a contagem de linhas de cada tabela.

**Sucesso:** dados de volta, contagens conferindo, e você sabe o seu **RTO real** (o tempo que
cronometrou) e o seu **RPO real** (a distância até o último backup).

**Ensina:** que backup não testado é esperança; e que o número que você imaginava para o RTO
estava errado.

---

## Desafios extras

| # | Desafio | O que exercita |
|---|---|---|
| A | Migre o projeto-modelo do Render para o Fly.io na região `gru` e meça a latência antes e depois de São Paulo | portabilidade e latência |
| B | Rode a pilha inteira num VPS com Coolify, incluindo backup para R2 | auto-hospedagem completa |
| C | Reescreva o backend como Cloudflare Worker usando Hyperdrive | modelo de borda e suas restrições |
| D | Acrescente `stale-while-revalidate` ao cache e meça o p99 | latência de cauda |
| E | Faça um painel no Grafana Cloud com os quatro sinais de ouro | observabilidade |
| F | Provoque um `OOMKilled` limitando a memória do container e leia o que o log mostra (e o que não mostra) | limites de recurso |
| G | Configure alerta externo (UptimeRobot) e derrube o serviço para verificar se o alerta chega | monitoramento |

---

## Autoavaliação

Marque o que você consegue fazer **sem consultar**:

- [ ] Colocar uma aplicação Node no ar com HTTPS e domínio próprio
- [ ] Diagnosticar `502` em menos de 5 minutos
- [ ] Explicar por que o serviço demorou 50 segundos para responder
- [ ] Dimensionar o pool de conexões com base em números
- [ ] Fazer uma migração de esquema sem queda
- [ ] Restaurar um backup e dizer o RTO real
- [ ] Ler um resultado de teste de carga e apontar o gargalo
- [ ] Estimar a fatura mensal de uma pilha antes de contratá-la
- [ ] Escolher entre PaaS e VPS com uma conta escrita, não com opinião

**Menos de 5 marcados:** volte aos labs 1 a 6.
**5 a 7:** faça os labs 9 a 12 — são os que faltam.
**8 ou 9:** você está pronto para operar em produção. Falta só o primeiro incidente real.
