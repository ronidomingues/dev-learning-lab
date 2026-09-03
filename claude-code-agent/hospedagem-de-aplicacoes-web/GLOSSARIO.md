# Glossário — hospedagem de aplicações web

`Atualizado em 18/08/2026` · ~160 termos

Termos técnicos em inglês são mantidos como o campo os usa, com a tradução na primeira
ocorrência. Ordem alfabética.

---

## A

**ACID** — conjunto de garantias de um banco transacional: Atomicidade, Consistência,
Isolamento, Durabilidade. É o que o PostgreSQL oferece e o Redis não.

**ACME** (*Automatic Certificate Management Environment*) — protocolo (RFC 8555) que permite
emitir certificados TLS automaticamente. É o que o Let's Encrypt usa.

**AGPLv3** — licença livre que estende a GPL para software servido pela rede: quem modifica e
oferece como serviço precisa disponibilizar o código. Licença opcional do Redis 8+.

**Always Free** — nomenclatura da Oracle para os recursos gratuitos permanentes, distintos dos
créditos de teste.

**API REST** — interface HTTP em que recursos têm URLs e verbos (GET, POST…).

**Aprisionamento** (*vendor lock-in*) — custo de trocar de fornecedor. O custo oculto mais caro
em hospedagem.

**Autoescala** (*autoscaling*) — ajuste automático do número de instâncias conforme a carga.

**Autovacuum** — processo do PostgreSQL que recolhe versões antigas de linha criadas pelo MVCC.

## B

**BaaS** (*Backend as a Service*) — plataforma que entrega banco, autenticação e storage
prontos. Ex.: Supabase, Firebase.

**Backpressure** (contrapressão) — mecanismo que faz um sistema sobrecarregado recusar ou
atrasar trabalho em vez de aceitar tudo e colapsar.

**Blue-green** — estratégia de rollout com dois ambientes completos; troca-se o tráfego de um
para o outro.

**Bloat** (inchaço) — espaço desperdiçado numa tabela do PostgreSQL por versões antigas ainda
não recolhidas.

**BSL** (*Business Source License*) — licença fonte-disponível que proíbe oferecer o software
como serviço concorrente, e converte-se em licença livre após um prazo. Usada por Dragonfly e
Terraform.

**Buildpack** — conjunto de regras que transforma código-fonte em imagem de container sem
`Dockerfile`. Usado por Heroku, Render, Railway.

## C

**CaaS** (*Container as a Service*) — plataforma que roda a sua imagem de container. Ex.: Cloud
Run, Fly.io.

**Cache-aside** — padrão de cache em que a aplicação consulta o cache, e em caso de ausência
consulta a fonte e grava no cache.

**CAP (teorema)** — em sistemas distribuídos, na presença de partição de rede é preciso
escolher entre consistência e disponibilidade.

**CDN** (*Content Delivery Network*) — rede de servidores distribuídos que guardam cópias do
conteúdo perto do usuário.

**cgroups** — mecanismo do kernel Linux que limita CPU, memória e I/O de um grupo de processos.
Junto com namespaces, é o que faz um container.

**CI/CD** — integração contínua e entrega/implantação contínua.

**CNAME** — registro DNS que aponta um nome para outro nome. **Não pode existir no domínio
raiz** (RFC 1034).

**Cold start** (partida a frio) — atraso da primeira requisição quando não há instância viva.

**Container** — processo isolado por namespaces e cgroups. **Não** é máquina virtual.

**Copy-on-write** — técnica em que uma cópia só é materializada quando alguém escreve. É o que
torna instantâneo o branch de banco da Neon.

**CORS** — mecanismo do navegador que controla quais origens podem chamar sua API.

**CSPRNG** — gerador de números aleatórios criptograficamente seguro. `crypto.randomBytes`, não
`Math.random`.

**CU-hora** (*compute unit hour*) — unidade de cobrança de computação da Neon.

## D

**Data Act** — Regulamento (UE) 2023/2854. O artigo 29 proíbe taxas de troca de provedor a
partir de 12/01/2027.

**DDoS** — ataque de negação de serviço distribuído.

**Deploy** — ato de colocar uma versão do sistema no ar.

**Digest** — identificador SHA-256 imutável de uma imagem de container. Diferente de tag.

**DNS** — sistema que traduz nomes em endereços IP.

**Docker** — a ferramenta que popularizou containers.

**DPA** (*Data Processing Agreement*) — contrato entre controlador e operador de dados pessoais.

**Durable Object** — abstração da Cloudflare para estado com coordenação, com uma instância
única por chave.

**Dyno** — nome do Heroku para uma instância de aplicação.

## E

**Edge** (borda) — execução de código em muitas localidades próximas do usuário.

**Egress** — tráfego de saída. A linha de fatura que mais surpreende.

**Expand/contract** — padrão de migração em que se adiciona antes de remover, mantendo
compatibilidade durante o rollout.

## F

**FaaS** (*Function as a Service*) — você entrega uma função; a plataforma cuida de todo o resto.

**Firecracker** — hipervisor de microVM criado pela AWS, usado por Lambda e Fly.io.

**FinOps** — disciplina de gestão de custo de nuvem.

**Free tier** — camada gratuita.

## G

**Graceful shutdown** (encerramento gracioso) — encerrar terminando as requisições em
andamento, ao receber `SIGTERM`.

## H

**Health check** — verificação periódica de saúde de uma instância.

**Hipervisor** — camada que executa máquinas virtuais.

**Horizontal (escala)** — mais instâncias. Exige aplicação sem estado.

**Hyperdrive** — serviço da Cloudflare que faz pool e cache de consultas a PostgreSQL a partir
da borda.

## I

**IaaS** (*Infrastructure as a Service*) — aluguel de máquina virtual crua.

**IaC** (*Infrastructure as Code*) — infraestrutura definida em arquivos versionados.

**Idempotente** — operação que pode ser repetida sem mudar o resultado. Requisito de qualquer
consumidor de fila "pelo menos uma vez".

**Índice** — estrutura que acelera busca no banco.

**Ingress** — tráfego de entrada (grátis em quase todo provedor).

**IOF** — imposto brasileiro sobre operações de câmbio; 3,5% em compras internacionais em 2026.

**Isolate** — sandbox do V8 usado pelos Cloudflare Workers. Inicia em milissegundos.

## J

**Jamstack** — arquitetura de site estático pré-construído + APIs.

**Jitter** — variação aleatória aplicada a um TTL ou a um intervalo de retentativa, para evitar
sincronização em massa.

**JWT** — token assinado que carrega afirmações. Não é revogável antes de expirar.

## K

**Kubernetes (k8s)** — orquestrador de containers. Provavelmente desnecessário para o seu caso.

**KV** (*key-value*) — armazenamento chave-valor. Workers KV é eventualmente consistente.

## L

**Latência de cauda** — os percentis altos (p95, p99), que dominam a experiência real.

**LGPD** — Lei nº 13.709/2018, marco brasileiro de proteção de dados pessoais.

**Let's Encrypt** — autoridade certificadora gratuita; certificados de 90 dias.

**Liveness** — sonda que responde "o processo está vivo?". **Não deve** checar dependências.

**Lei de Little** — `L = λ × W`. Usada para dimensionar pool de conexões.

**LRU** (*least recently used*) — política de descarte que remove o menos usado recentemente.

## M

**MAU** (*monthly active users*) — usuários ativos mensais; unidade de cobrança da Supabase.

**MicroVM** — máquina virtual mínima, com isolamento forte e partida rápida (Firecracker).

**Migração** — mudança versionada de esquema de banco.

**MVCC** — controle de concorrência multiversão do PostgreSQL: leitores não bloqueiam
escritores.

## N

**Namespaces** — mecanismo do kernel que dá a um processo sua própria visão de rede, processos
e sistema de arquivos.

**NAT Gateway** — recurso da AWS que custa ~US$ 33/mês só por existir. Causa frequente de
fatura inesperada.

**N+1** — antipadrão em que se faz uma consulta por item de uma lista.

## O

**OCI** — pode ser *Open Container Initiative* (padrão de imagem de container) ou *Oracle Cloud
Infrastructure*. O contexto decide.

**OOMKilled** — processo morto pelo kernel por estourar o limite de memória.

**Orquestrador** — sistema que agenda e supervisiona containers.

## P

**p50 / p95 / p99** — percentis de latência. O p99 é o que gera reclamação.

**PaaS** (*Platform as a Service*) — você entrega o código; ela cuida do resto.

**PACELC** — extensão do CAP: *if Partition then Availability or Consistency, Else Latency or
Consistency*. Mais útil na prática.

**PgBouncer / Supavisor** — poolers de conexão para PostgreSQL.

**PID 1** — o primeiro processo de um container; precisa tratar sinais ou usar um init.

**Pool de conexões** — conjunto de conexões reutilizadas. Evita abrir uma por requisição.

**PoP** (*point of presence*) — localidade de uma CDN.

**Postmortem** — relatório de incidente. Deve ser **sem culpado**.

## Q

**QUIC** — protocolo de transporte sobre UDP; base do HTTP/3.

## R

**Rate limit** — limitação de taxa de requisições.

**Readiness** — sonda que responde "posso receber tráfego?". **Deve** checar dependências.

**Redis** — banco de estruturas de dados em memória. Desde a versão 8, tri-licenciado
(AGPLv3 / RSALv2 / SSPLv1).

**Região** — localidade física de um data center. `sa-east-1` é São Paulo.

**Réplica de leitura** — cópia do banco que serve leituras, com atraso de replicação.

**RESP** — protocolo de comunicação do Redis/Valkey.

**RLS** (*Row Level Security*) — segurança por linha no PostgreSQL, desde a versão 9.5.

**Rollback** — voltar à versão anterior.

**Rolling update** — troca de versão instância a instância.

**RPO** (*Recovery Point Objective*) — quanto de dado você aceita perder.

**RTO** (*Recovery Time Objective*) — em quanto tempo você precisa estar de pé.

**RTT** (*round-trip time*) — tempo de ida e volta na rede.

## S

**SaaS** — software como serviço.

**Serverless** — modelo em que não há servidor seu ligado entre requisições.

**Sharding** (fragmentação) — dividir os dados entre vários bancos. Complexo; última opção.

**SIGTERM** — sinal que a plataforma envia para pedir encerramento antes de matar o processo.

**Single-flight** — técnica em que apenas uma requisição reconstrói um valor de cache; as
demais esperam.

**Slug** — no Heroku, o pacote de deploy; neste curso, também o apelido curto de uma URL.

**SLO / SLI / SLA** — objetivo, indicador e acordo de nível de serviço.

**SNI** — extensão do TLS que informa qual domínio está sendo acessado, permitindo vários
certificados no mesmo IP.

**SPA** (*Single Page Application*) — aplicação que roda inteira no navegador.

**SPF / DKIM / DMARC** — registros DNS que autenticam envio de e-mail.

**SSPL** — licença fonte-disponível criada pela MongoDB; não aprovada pela OSI.

**SSR** (*server-side rendering*) — renderização de HTML no servidor.

**SSRF** (*server-side request forgery*) — ataque em que se faz o servidor requisitar um
endereço interno. Por isso o projeto-modelo bloqueia hosts privados.

**Stateful / Stateless** — com estado / sem estado. A divisão que explica tudo em hospedagem.

**Stampede** (estampida) — muitas requisições perdendo o cache ao mesmo tempo e batendo na
fonte juntas.

**Stale-while-revalidate** — servir o valor velho enquanto se busca o novo.

**Sticky session** — roteamento que amarra um usuário a uma instância. Sinal de estado no lugar
errado.

**Streams (Redis)** — estrutura de log com grupos de consumidores; base de fila confiável.

## T

**Tail at scale** — fenômeno em que a cauda de latência domina a experiência quando há muitos
componentes.

**TLS** — criptografia de transporte. HTTPS é HTTP sobre TLS.

**Trace** — registro do caminho de uma requisição entre serviços.

**TTL** (*time to live*) — tempo de validade, seja de um registro DNS ou de uma chave de cache.

**Twelve-Factor** — as doze regras que tornam uma aplicação hospedável.

## U

**Upstash** — provedor de Redis serverless cobrado por comando.

## V

**Valkey** — fork do Redis 7.2.4 sob licença BSD, mantido pela Linux Foundation. Padrão nas
distribuições Linux e nos serviços gerenciados em 2026.

**VACUUM** — recolhimento de versões antigas de linha no PostgreSQL.

**Vertical (escala)** — máquina maior. Simples, com teto.

**VPC** — rede privada virtual dentro de um provedor.

**VPS** — servidor virtual privado; uma fatia de uma máquina física.

## W

**WAF** (*Web Application Firewall*) — filtro de requisições maliciosas.

**WAL** (*write-ahead log*) — registro do PostgreSQL escrito antes da mudança; base da
durabilidade e da replicação.

**WASM / WASI** — WebAssembly e sua interface de sistema. Aposta de longo prazo para
portabilidade com partida rápida.

**Webhook** — requisição HTTP disparada por um evento (ex.: `git push` acionando o deploy).

**Worker** — processo de segundo plano, sem porta HTTP. **Não existe no plano gratuito do
Render.**

**Workers (Cloudflare)** — plataforma de execução na borda usando isolates V8.

## Z

**Zero-downtime deploy** — troca de versão sem indisponibilidade. Exige rollout gradual **e**
migração compatível para trás.

**Zona (de disponibilidade)** — subdivisão de uma região, com energia e rede independentes.
