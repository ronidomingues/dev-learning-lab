# 75 · Armadilhas, erros clássicos e mitos

`Nível: todos` · `Atualizado em 18/08/2026`

32 armadilhas e 8 mitos. Cada uma com **sintoma, causa, correção e custo real**. Se você ler um
arquivo só deste curso depois do [`40`](40-arquiteturas-de-referencia.md), leia este.

---

## Bloco 1 · Deploy e configuração

### 1. Escutar em `127.0.0.1` dentro de um container
**Sintoma:** `no open ports detected`, `502 Bad Gateway`, deploy "sucesso" com site fora.
**Causa:** `127.0.0.1` dentro do container é só o próprio container.
**Correção:** `server.listen(port, "0.0.0.0")`.
**Custo:** 2 horas de confusão na primeira vez. É **o erro nº 1 de todos os tempos**.

### 2. Porta fixa no código
**Sintoma:** idem.
**Correção:** `process.env.PORT || 3000`.

### 3. Mudar variável de ambiente e não reimplantar
**Sintoma:** "mudei a chave da API e não mudou nada".
**Causa:** a maioria das plataformas só injeta variáveis em novo deploy.
**Correção:** force um deploy. No Fly, `secrets set` já reinicia.

### 4. Segredo em variável de frontend
**Sintoma:** nenhum — até alguém encontrar sua chave.
**Causa:** `VITE_*`, `NEXT_PUBLIC_*` e `REACT_APP_*` são **embutidas no JavaScript** enviado ao
navegador.
**Correção:** segredo **nunca** no frontend. Chame o backend.
**Custo:** já custou faturas de cinco dígitos em chaves de nuvem vazadas.

### 5. `.env` no repositório
**Sintoma:** e-mail do GitHub avisando de segredo exposto (o *secret scanning* funciona).
**Correção:** `.gitignore`, **rotacione a credencial** e só depois limpe o histórico.
**Custo:** existem robôs varrendo commits públicos em **segundos**.

### 6. "Resolver" o cold start com um cron que pinga o serviço
**Sintoma:** funciona… até a plataforma notar.
**Causa:** manter serviço gratuito acordado artificialmente viola os termos da maioria das
plataformas e consome as 750 h/mês do Render em ~31 dias — ou seja, **você fica sem cota no fim
do mês**.
**Correção:** pague os US$ 7, ou aceite o sono, ou use plataforma que não dorme (Koyeb,
Northflank).

### 7. Não tratar `SIGTERM`
**Sintoma:** erros esporádicos de conexão a cada deploy; requisições cortadas.
**Correção:** `server.close()` + fechar pool + `process.exit(0)`, com prazo máximo.

### 8. Node como PID 1 sem init
**Sintoma:** `SIGTERM` ignorado; container morto à força.
**Correção:** `dumb-init` ou `tini` no `ENTRYPOINT`.

### 9. `latest` como tag de imagem
**Sintoma:** "não mudamos nada e quebrou".
**Correção:** fixe versão e, idealmente, digest SHA-256.

### 10. `npm install` em CI
**Sintoma:** build reproduzível na sexta, quebrado na segunda.
**Correção:** `npm ci`.

### 11. Imagem de arquitetura errada (Apple Silicon)
**Sintoma:** `exec format error`, ou container lentíssimo.
**Causa:** imagem `arm64` construída no Mac indo para servidor `amd64`.
**Correção:** `docker buildx build --platform linux/amd64,linux/arm64`.

---

## Bloco 2 · Banco de dados

### 12. Conexão nova a cada requisição
**Sintoma:** `too many clients already`; latência crescente.
**Correção:** um pool por processo, com `max` pequeno.

### 13. Pool grande demais
**Sintoma:** o banco cai quando você escala a aplicação.
**Causa:** `instâncias × max` estoura o `max_connections`.
**Correção:** faça a multiplicação antes. Use a Lei de Little
([`60`](60-teoria-avancada.md), seção 3.2).

### 14. Não saber que o plano gratuito **expira**
**Sintoma:** banco sumiu.
**Causa:** Render Postgres gratuito **expira 30 dias após a criação** (14 dias de carência).
**Correção:** lembrete no calendário no dia em que criar. Ou use Neon/Supabase.

### 15. Não saber que o projeto **pausa**
**Sintoma:** portfólio fora do ar quando o recrutador abriu.
**Causa:** Supabase Free pausa projetos após 7 dias de inatividade.
**Correção:** despause no painel; para algo que importa, Pro (US$ 25) ou Neon.

### 16. Migração destrutiva no mesmo deploy do código
**Sintoma:** erros intermitentes durante o rollout que somem sozinhos.
**Causa:** código velho e novo rodam juntos por minutos.
**Correção:** *expand/contract*.

### 17. `CREATE INDEX` sem `CONCURRENTLY` em tabela grande
**Sintoma:** escrita travada; timeouts em cascata.
**Correção:** `CONCURRENTLY`, fora de transação.

### 18. `UPDATE` gigante numa transação
**Sintoma:** o deploy trava; o WAL cresce; o `VACUUM` não acompanha.
**Correção:** lotes com commit, conforme [`50`](50-operacao-e-ciclo-de-vida.md), seção 4.

### 19. Pooler em modo transaction com prepared statements
**Sintoma:** `prepared statement "s1" already exists`, aleatório.
**Causa:** o modo transaction troca a conexão física entre comandos.
**Correção:** `?pgbouncer=true` (Prisma), `statement_cache_size=0`, ou modo session.

### 20. Banco em região diferente da aplicação
**Sintoma:** tudo lento sem consulta lenta no `EXPLAIN`.
**Correção:** mesma região. É a otimização de maior retorno que existe.

### 21. Achar que "compatível com PostgreSQL" é PostgreSQL
**Sintoma:** `pg_dump` não funciona; extensão não existe; migração impossível.
**Correção:** teste `pg_dump`/`pg_restore` **antes** de escolher.

---

## Bloco 3 · Redis / cache

### 22. `KEYS *` em produção
**Sintoma:** o servidor inteiro congela.
**Causa:** varre todo o espaço de chaves, e o Redis executa comandos em uma thread só.
**Correção:** `SCAN` com cursor.

### 23. Chave de cache sem os parâmetros
**Sintoma:** **usuário A vê dados do usuário B.** Falha de segurança, não de performance.
**Correção:** inclua tudo que altera o resultado — inclusive o identificador do usuário.

### 24. Redis como única fonte de verdade
**Sintoma:** dados sumiram após um reinício.
**Causa:** planos gratuitos frequentemente não persistem (Render Key Value: 25 MB, **sem
persistência**).
**Correção:** o que não pode sumir vai para o PostgreSQL.

### 25. `maxmemory-policy` errada
**Sintoma:** `OOM command not allowed when used memory > 'maxmemory'`, ou mensagens de fila
desaparecendo.
**Correção:** `allkeys-lru` para cache; **`noeviction` para fila**. Nunca inverta.

### 26. Polling em vez de `BLOCK`
**Sintoma:** cota do Upstash esgotada em dias.
**Causa:** polling a cada 100 ms = **864 mil comandos/dia** (a cota gratuita mensal é 500 mil).
**Correção:** `BRPOP`/`XREAD BLOCK`.

### 27. Redis exposto na internet sem senha
**Sintoma:** o servidor vira minerador de criptomoeda.
**Correção:** `bind 127.0.0.1`, `requirepass`, firewall.
**Custo:** comprometimento total da máquina. Ocorre em **minutos**, não dias.

### 28. Não medir a cota antes de escolher o plano
**Sintoma:** `ERR max daily request limit exceeded` no meio do mês.
**Correção:** requisições/dia × comandos por requisição × 30. Faça a conta.

---

## Bloco 4 · Custo, operação e processo

### 29. Não configurar limite de gasto
**Sintoma:** fatura de US$ 400 por um laço que disparou invocações.
**Correção:** AWS Budgets com alerta em US$ 1; Vercel Spend Management; cartão virtual com
limite baixo.

### 30. Cadastro barrado e achar que é erro seu
**Sintoma:** conta recusada sem explicação.
**Causa:** filtro antifraude — camadas gratuitas sofrem abuso pesado.
**Correção:** use conta GitHub com histórico, e-mail não descartável, e tente de outra rede.

### 31. Confiar no backup do provedor sem testar
**Sintoma:** no dia do incidente, o backup não restaura.
**Correção:** uma restauração de teste por trimestre.
**Custo:** este é o único erro desta lista que é **irreversível**.

### 32. Usar plano Hobby da Vercel em projeto comercial
**Sintoma:** conta suspensa.
**Causa:** as *fair use guidelines* restringem o Hobby a uso não comercial e pessoal.
**Correção:** Pro (US$ 20/assento) ou Cloudflare Pages, que permite uso comercial no gratuito.

---

## Os 8 mitos

### Mito 1 — "Serverless é sempre mais barato"
**Falso.** Serverless é mais barato para tráfego **intermitente**. Para carga constante, uma
instância dedicada é mais barata, às vezes por uma ordem de grandeza. O ponto de virada
costuma ficar entre 20% e 40% de utilização média.

### Mito 2 — "Preciso de Kubernetes para ser profissional"
**Falso.** Kubernetes resolve orquestração de dezenas de serviços com times independentes. Para
uma aplicação e um banco, ele adiciona uma camada inteira de complexidade sem resolver nenhum
problema seu. A maioria das empresas que o adotou cedo demais reverteu.

### Mito 3 — "A nuvem é sempre mais cara que um servidor próprio"
**Depende, e a conta honesta raramente é feita.** Some ao servidor: energia, link redundante,
reposição de hardware, e **o seu tempo**. A nuvem é cara para carga previsível e constante;
é barata para carga variável, para começar, e para não ter equipe de infraestrutura.

### Mito 4 — "Free tier não serve para nada sério"
**Falso.** Cloudflare Pages serve site comercial com tráfego ilimitado, de graça. O que não
serve para produção é **camada gratuita que dorme, pausa ou expira** — e não perceber essa
diferença é que dá errado.

### Mito 5 — "Edge é sempre mais rápido"
**Falso, e frequentemente o contrário.** Código na borda com banco central pode ser mais lento
que um servidor único perto do banco, porque a viagem que se repete é app↔banco, não
usuário↔app.

### Mito 6 — "Preciso escalar horizontalmente desde o início"
**Falso.** Uma máquina de 8 núcleos e 32 GB atende mais tráfego do que 95% dos sistemas em
produção recebem. Escala vertical é mais simples, mais barata e resolve por anos.

### Mito 7 — "Docker deixa a aplicação mais lenta"
**Praticamente falso em Linux.** Container é um processo comum com namespaces; a sobrecarga de
CPU é desprezível. O que custa é o *overlay filesystem* em I/O intenso e — em macOS e Windows —
a VM Linux por baixo, onde volumes montados do host são realmente lentos.

### Mito 8 — "Cache resolve performance"
**Perigosamente incompleto.** Cache **esconde** consulta ruim. Quando a taxa de acerto cai
(deploy, invalidação, pico de chaves novas), o problema volta amplificado, porque agora o
tráfego cresceu. Índice e correção de N+1 primeiro; cache depois.

---

## Checklist "não vou me arrepender"

Antes de considerar um sistema pronto para receber usuários:

- [ ] Escuta em `0.0.0.0:$PORT`
- [ ] Trata `SIGTERM`
- [ ] `/health` verifica banco e cache, com timeout, e distingue crítico de degradado
- [ ] Um pool, com `max` calculado, e a multiplicação por número de instâncias feita
- [ ] App e banco na mesma região
- [ ] Migrações versionadas e compatíveis para trás
- [ ] Segredos fora do Git e fora do frontend
- [ ] **Backup automático, externo e restaurado ao menos uma vez**
- [ ] Monitoramento externo com alerta
- [ ] Limite de gasto configurado
- [ ] Rate limit nas rotas sensíveis
- [ ] Banco e Redis inacessíveis pela internet
- [ ] Você sabe onde fica o botão de rollback — e já usou
- [ ] Você sabe o que expira, o que pausa e o que dorme na sua pilha, com datas

---

## Autoteste

1. Qual é o erro nº 1 de todos os tempos, e qual a correção de uma linha?
2. Por que um cron que pinga o serviço gratuito é uma péssima ideia — dê o argumento numérico.
3. Explique a armadilha 23 e por que ela é uma falha de segurança, não de performance.
4. Qual é a `maxmemory-policy` certa para cache e qual para fila? O que acontece se inverter?
5. Faça a conta da armadilha 26.
6. Qual das 32 armadilhas é irreversível?
7. Desmonte o mito "edge é sempre mais rápido" com um exemplo numérico.
8. Por que cache não deve ser o primeiro passo de otimização?
