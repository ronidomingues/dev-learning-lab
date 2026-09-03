# 65 · Estado da arte — agosto de 2026

`Nível: pesquisa` · **`Instantâneo de 11/08/2026`**

> ⚠️ **É o arquivo que envelhece mais rápido deste material.** Se você está lendo em 2027 ou
> depois, trate como registro histórico e confira as fontes no rodapé.

---

## 1. O panorama em uma tabela

| Item | Estado em 11/08/2026 |
|---|---|
| HTTP | RFCs **9110–9114** (jun/2022) são a referência |
| **OpenAPI** | **3.2.0** (set/2025) é a versão corrente. **4.0 "Moonwalk" não existe** |
| JSON Schema | draft **2020-12** |
| Problem Details | **RFC 9457** (jul/2023), substituindo o 7807 |
| UUID | **RFC 9562** (mai/2024), com **UUIDv7** |
| AsyncAPI | **3.0** (dez/2023) |
| **HTTP/3** | **~20–35%** do tráfego, conforme a metodologia — **estagnado** |
| **MCP** | padrão de facto para agentes; revisão de **jul/2026** move para stateless |
| gRPC | consolidado em comunicação interna |
| GraphQL | maduro; adoção estabilizada em nicho, sem crescimento explosivo |
| Node.js | **24.x** é o Active LTS (até 20/10/2026); 26.x assume depois |

---

## 2. OpenAPI 3.2 e o adiamento da 4.0

**O que a 3.2.0 trouxe** (set/2025), sem quebrar compatibilidade com a 3.1:

| Novidade | Por que importa |
|---|---|
| **Streaming de primeira classe** | descreve **SSE**, **JSON Lines** e multipart — antes era impossível documentar um endpoint de streaming |
| **Tags hierárquicas** | organiza APIs grandes em árvore, não numa lista plana |
| **`additionalOperations`** | métodos HTTP customizados (`QUERY`, WebDAV) |
| **Device Authorization Flow** | fluxo OAuth de dispositivo passa a ser descritível |

**O suporte a streaming é a mudança mais consequente.** Com o crescimento de respostas
transmitidas — sobretudo o *streaming* de modelos de linguagem via SSE —, havia uma lacuna
real: você não conseguia descrever no contrato um endpoint que devolve eventos ao longo do
tempo. Isso agora existe.

**Sobre a 4.0 "Moonwalk":** em projeto desde 2024, **sem data de entrega** e com pouco
avanço público. A recomendação da própria OpenAPI Initiative é usar as versões 3.x.

> **O que fazer:** adote **3.1** como piso e **3.2** se sua ferramenta já suportar.
> **Não espere pela 4.0** — planejar migração para uma versão sem data é planejar nada.

---

## 3. HTTP/3: a estagnação e o que ela ensina

**Os números de 2026**, e a divergência entre eles é informativa:

| Fonte / metodologia | Medida |
|---|---|
| Sites que **suportam** HTTP/3 (W3Techs, mai/2026) | ~39% |
| Tráfego na borda da Cloudflare | ~35% |
| **Requisições efetivamente servidas** (medições independentes) | **~20–21%**, com queda registrada em jul/2026 |

**A divergência é a informação:** muitos sites **suportam**, poucas requisições **usam**. O
cliente negocia e frequentemente cai para HTTP/2.

**Por que estagnou:**

1. **UDP bloqueado** em muitas redes corporativas e de operadora. QUIC roda sobre UDP; sem
   ele, o cliente volta para TCP.
2. **Ganho pequeno em rede boa.** HTTP/3 brilha com perda de pacote; em fibra e datacenter,
   a diferença some.
3. **Custo de CPU maior** — QUIC roda em espaço de usuário, sem a otimização de décadas que
   o TCP tem no kernel.
4. **Complexidade operacional**: ferramentas de depuração, balanceadores e firewalls
   maduros para TCP, imaturos para QUIC.

> **A lição, que vale além do HTTP/3:** superioridade técnica não produz adoção sozinha.
> Adoção depende de **ganho perceptível** e **custo de transição**. HTTP/2 foi adotado
> rapidamente porque o ganho sobre o /1.1 era grande e o custo era zero para a aplicação.
> HTTP/3 tem ganho marginal na maioria dos casos e custo operacional real.
>
> **Recomendação prática:** habilite HTTP/2 sem hesitar. Trate HTTP/3 como otimização
> opcional, com fallback garantido, e meça antes de comemorar.

---

## 4. MCP e a virada dos agentes

**O estado:** MCP saiu de proposta da Anthropic (nov/2024) para **padrão de facto**, com
adoção por OpenAI, Google e Microsoft, e um ecossistema de dezenas de milhares de servidores
publicados.

**A mudança de julho de 2026 é arquitetural e merece atenção:** a especificação moveu-se
para um modelo **stateless**.

**Por que isso importa:** o modelo com estado exigia que cada conexão agente↔servidor
mantivesse contexto vivo, o que impede balanceamento simples, cache e escala horizontal.
Stateless permite que a infraestrutura de agentes use a **mesma pilha da web** — proxies,
CDNs, balanceadores, réplicas sem coordenação.

> **Reconheça o padrão:** isso é exatamente a segunda restrição de REST
> ([13-rest-e-restful.md](13-rest-e-restful.md) §2.2), redescoberta 26 anos depois num
> contexto novo. Fielding descreveu por que a web escalou; o ecossistema de agentes está
> chegando à mesma conclusão pelo mesmo caminho — tentando escalar e esbarrando no estado.

**O que MCP continua não sendo:** substituto de REST, padrão de API de propósito geral, ou
camada de orquestração. Um servidor MCP é, tipicamente, um **invólucro sobre a sua API
existente**.

---

## 5. APIs com dois públicos: programadores e agentes

**A tendência mais consequente para quem projeta APIs em 2026**, e é uma mudança de
requisito, não de tecnologia.

| | Programador | Agente de IA |
|---|---|---|
| O que lê | documentação, exemplos, código | **descrição da ferramenta**, schema |
| Como descobre o que fazer | busca, tutorial, Stack Overflow | a descrição textual e os nomes |
| Tolera ambiguidade | sim (pergunta, testa, deduz) | **não** — escolhe errado com confiança |
| Custo de erro | tempo | ação errada executada |

**Consequências concretas de design:**

1. **A descrição virou requisito funcional.** `"processa dados"` faz o agente escolher a
   ferramenta errada. `"Cria uma ordem de serviço para um equipamento. Use quando o usuário
   relatar defeito. Não use para manutenção preventiva — para isso use agendarManutencao."`
   é o que funciona. Descrever **quando não usar** é tão importante quanto descrever o uso.

2. **Nomes semânticos importam mais.** `POST /os` é opaco; `criarOrdemDeServico` carrega
   significado que o modelo usa.

3. **Erros precisam ser acionáveis em linguagem natural.** `422 {"campo": "cpf"}` não diz ao
   agente o que fazer. `"O CPF deve ter 11 dígitos numéricos, sem pontuação"` diz.

4. **Idempotência ficou mais importante, não menos.** Agentes retentam com liberalidade e
   sem a intuição humana sobre quando isso é perigoso.

5. **Autorização granular ficou crítica.** Um agente com um token amplo e uma instrução
   ambígua é uma superfície de risco nova. Escopos estreitos e confirmação humana em
   operações irreversíveis deixaram de ser exagero.

> **Minha opinião profissional, separada dos fatos acima:** a hipótese mais interessante
> aqui é a de [13-rest-e-restful.md](13-rest-e-restful.md) §7.5 — **agentes podem ser o
> "cliente genérico" que HATEOAS sempre pressupôs e que nunca existiu**, porque era caro
> demais escrever. Um agente que descobre as ações possíveis lendo os links e as descrições
> da resposta é exatamente o consumidor para o qual a hipermídia foi desenhada. Se isso se
> confirmar, o cálculo de custo/benefício da hipermídia muda de sinal pela primeira vez em
> 25 anos. **É especulação fundamentada, não previsão.**

---

## 6. O que não mudou, e não deve mudar

Vale registrar, porque é onde investir tempo de estudo:

- **HTTP** — a semântica dos RFCs 9110+ é a mesma desde os anos 90, consolidada.
- **As seis restrições de REST** — 26 anos, ainda a melhor análise de por que a web escalou.
- **Idempotência, retentativa, backoff** — decorrem de limites teóricos, não de moda.
- **Os limites teóricos** — dois generais, FLP, CAP: são matemática.
- **OWASP API Top 10** — BOLA é a nº 1 há anos e continuará sendo, porque a causa é
  estrutural ([16-seguranca.md](16-seguranca.md) §10).
- **JSON** — dominante desde 2010; nenhum substituto no horizonte para a borda.
- **Contrato como fonte da verdade** — a ideia só se fortaleceu.

**Distribua o estudo de acordo:** quem estudar HTTP, REST, idempotência e os limites
teóricos terá conhecimento útil em 2040. Quem estudar a API da ferramenta da moda terá
conhecimento útil por dois anos.

---

## 7. O que observar nos próximos 12 meses

1. **A OpenAPI 4.0 sai do papel?** Se continuar parada, a 3.x consolida-se como o padrão
   duradouro — o que é bom para estabilidade.
2. **HTTP/3 retoma ou continua estagnado?** Se a queda de meados de 2026 persistir, será o
   primeiro caso de um padrão do IETF perdendo adoção depois de lançado — e valeria estudo.
3. **MCP resiste à concorrência de padrões?** Padrão de facto sem governança neutra é
   frágil; observe se ele migra para uma fundação.
4. **APIs começam a publicar contrato duplo** (OpenAPI + descrições para agente) de forma
   padronizada, ou continua improvisado?
5. **Hipermídia volta?** O sinal seria APIs grandes publicando links de ação em respostas,
   motivadas por consumo por agentes.
6. **Custo de gateway.** Com preços de US$ 1 a US$ 30 por milhão de chamadas conforme o
   fornecedor ([80-custos-e-licencas.md](80-custos-e-licencas.md)), a pressão por
   alternativas open-source auto-hospedadas tende a crescer.

---

## 8. O que eu diria a quem começa hoje

Em ordem de prioridade, com justificativa:

1. **Aprenda HTTP a fundo.** É o investimento com maior meia-vida deste material.
2. **Aprenda a ler um RFC.** Comece pelo 9110. A fonte primária é mais clara que a maioria
   dos tutoriais e não envelhece.
3. **Domine `curl` e o DevTools.** São as ferramentas que funcionam em qualquer API, para
   sempre.
4. **Entenda idempotência de verdade**, não como palavra. É o conceito que mais separa quem
   escreve integração que funciona de quem escreve integração que duplica.
5. **Escreva um contrato antes de escrever a API.** Uma vez que seja, para sentir a diferença.
6. **Leia a tese do Fielding, capítulo 5.** São ~30 páginas e explicam a arquitetura da web.
7. **Não persiga o estilo da moda.** Aprenda REST bem; os outros são variações sobre os
   mesmos trade-offs, e você os aprende em dias quando precisar.

---

## Autoteste

1. Qual é a versão corrente do OpenAPI, e o que fazer sobre a 4.0?
2. Por que os números de adoção de HTTP/3 divergem tanto entre fontes? O que a divergência informa?
3. Cite quatro motivos para a estagnação do HTTP/3. Qual lição geral isso ensina?
4. O que mudou no MCP em julho de 2026, e a qual restrição de REST isso corresponde?
5. Cite cinco consequências de design de ter agentes como consumidores.
6. Por que a descrição de uma ferramenta virou requisito funcional?
7. Qual é a hipótese sobre hipermídia e agentes? Ela é fato ou especulação?
8. Cite quatro coisas que não mudaram. Como isso deve guiar seu estudo?

---

### Fontes consultadas (11/08/2026)

- OpenAPI Initiative — SIG Moonwalk (estado da 4.0) — https://github.com/OAI/sig-moonwalk
- OpenAPI Initiative — *Moonwalk 2025 update* — https://www.openapis.org/blog/2025/02/05/moonwalk-2025-update
- APIScout — *OpenAPI 3.2: What's New & Migration Guide 2026* — https://apiscout.dev/guides/openapi-4-whats-new-migration-guide-2026
- Cloudflare — *Radar Year in Review* — https://blog.cloudflare.com/radar-2025-year-in-review/
- Medições independentes de adoção de HTTP/3 em 2026 (W3Techs, TechnologyChecker, Cloudflare Radar) — ver §3
- Model Context Protocol — *The 2026-07-28 Specification* — https://blog.modelcontextprotocol.io/posts/2026-07-28/
- Model Context Protocol — *The 2026 MCP Roadmap* — https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/
- Node.js Release Working Group — https://github.com/nodejs/Release
- IETF — RFCs 9110–9114, 9457, 9562 — https://www.rfc-editor.org/
