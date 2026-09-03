# 75 · Armadilhas, mitos e más práticas

`Nível: intermediário` · `Escrito em 01/09/2026`

Erros clássicos, por que persistem, e a correção. Cada armadilha traz o **sintoma real**,
porque é assim que ela chega até você.

---

## Parte I · Armadilhas de ambiente

### A1 · `print()` no servidor stdio
**Sintoma:** o servidor "conecta e cai", sem erro claro no host.
**Causa:** `stdout` é a fita JSON-RPC; qualquer byte fora do formato corrompe a conversa.
**Correção:** `logging.basicConfig(stream=sys.stderr)`; em TypeScript, `console.error`.
**Por que persiste:** `print` é o primeiro reflexo de depuração de todo programador, e o
sintoma não aponta para a causa.

### A2 · Caminho relativo na configuração do host
**Sintoma:** funciona no terminal, não funciona no Claude Desktop.
**Causa:** o host não roda no diretório do seu projeto.
**Correção:** caminho **absoluto** para o comando e para `--directory`.

### A3 · O host não herda o seu PATH
**Sintoma:** `command not found: uv`, só no host.
**Causa:** no macOS, aplicativos abertos pelo Finder não herdam o PATH do shell.
**Correção:** caminho absoluto do binário (`/Users/você/.local/bin/uv`).

### A4 · Não reiniciar o host
**Sintoma:** a mudança "não pegou".
**Causa:** um processo herda o ambiente ao nascer; o servidor stdio é lançado uma vez.
**Correção:** feche o aplicativo **por completo** (não só a janela) e reabra.

### A5 · Segredo em `args`
**Sintoma:** o token aparece em `ps aux` e nos logs do host.
**Correção:** use `env` (stdio) ou `headers` (HTTP).
**Por que persiste:** `args` é onde tudo o mais vai, e o vazamento é invisível no dia a dia.

### A6 · `sudo pip install` / `sudo npm -g`
**Sintoma:** `EACCES` depois, e ferramentas do sistema quebradas.
**Correção:** `uv`, `fnm`, `npx` — tudo em `$HOME`, sem `sudo`.

### A7 · `no_proxy` com espaços
**Sintoma:** o cliente Python tenta falar com `127.0.0.1` **pelo proxy corporativo**.
**Causa:** vários clientes HTTP não fazem `strip()` dos itens da lista.
**Correção:** `NO_PROXY="localhost,127.0.0.1,::1"`, sem espaço nenhum.

---

## Parte II · Armadilhas de projeto

### A8 · A ferramenta genérica
**Sintoma:** parece elegante; vira incidente.
**Exemplo:** `executar_sql(query)`, `shell(comando)`, `http_request(url, method, body)`.
**Por que é ruim:** superfície de ataque máxima; o modelo escreve errado; impossível de
limitar, cachear ou auditar por operação.
**Correção:** verbos do domínio.
**Por que persiste:** é menos código para escrever, e "dá mais poder ao modelo" soa bem
até o primeiro `DROP TABLE`.

### A9 · Sessenta ferramentas num servidor
**Sintoma:** o modelo escolhe errado; o custo de token dispara em toda mensagem.
**Causa:** mapeou endpoints, não intenções.
**Correção:** uma ferramenta por **intenção**, com parâmetros para as variações; ou
divida em dois servidores.

### A10 · Descrição vazia, ou copiada da docstring interna
**Sintoma:** o modelo não usa a ferramenta, ou usa a errada.
**Correção:** o que faz · o que **não** faz · qual usar então · exemplo · caso ruim.

### A11 · Nomes indistinguíveis
**Sintoma:** o modelo alterna entre `listar_usuarios` e `listar_usuarios_ativos` sem critério.
**Correção:** uma ferramenta com parâmetro `apenas_ativos: bool`.

### A12 · `SELECT *`
**Sintoma:** conta de tokens alta, contexto estourado, respostas piores.
**Correção:** pagine, resuma, use `resource_link`.
**Por que persiste:** funciona no teste com 10 linhas.

### A13 · Exceção crua em vez de `ToolError`
**Sintoma:** o modelo recebe `Error executing tool X` e não consegue se corrigir.
**Correção:** `ToolError` com mensagem em três partes (o que · por que · o que fazer).

### A14 · Estado global no servidor
**Sintoma:** funciona local; com duas réplicas, "some" metade das vezes.
**Causa:** desde `2026-07-28` não há sessão, e réplicas não compartilham memória.
**Correção:** handle explícito + armazenamento compartilhado.

### A15 · Tratar handle como autenticação
**Sintoma:** um usuário acessa o carrinho de outro.
**Causa:** o servidor confia na posse do handle.
**Correção:** guardar como `<user_id>:<handle>`, com `user_id` do token **verificado**.

### A16 · Sem idempotência em escrita
**Sintoma:** três pedidos idênticos criados.
**Causa:** o modelo repete a chamada — porque perdeu o resultado do contexto, porque a
resposta demorou, porque o usuário reformulou.
**Correção:** chave de idempotência, ou detectar a duplicata e devolver o registro existente.

### A17 · Sem teto em parâmetro numérico
**Sintoma:** `limite=10000` derruba o banco.
**Causa:** o modelo **vai** tentar.
**Correção:** `Field(ge=1, le=25)` no schema **e** revalidação no servidor.

### A18 · Ordem não determinística
**Sintoma:** o modelo reage a "mudanças" que são só reordenação; testes intermitentes.
**Correção:** `ORDER BY` explícito em tudo. A spec pede em `tools/list`; estenda a todo resultado.

---

## Parte III · Armadilhas do protocolo

### A19 · Achar que existe sessão
**Sintoma:** o servidor supõe que a segunda chamada vem do mesmo usuário.
**Correção:** reler [10 §7](10-fundamentos.md). *Uma conexão aberta não é uma conversa.*

### A20 · `await ctx.elicit(...)` dentro da ferramenta
**Sintoma:** `NoBackChannelError: this transport context has no back-channel`.
**Correção:** `Annotated[..., Resolve(fn)]` com `Elicit(...)`.

### A21 · Inspecionar `requestState`
**Sintoma:** funciona hoje, quebra na próxima versão do servidor.
**Causa:** a spec **proíbe** o cliente inspecionar, analisar, alterar ou supor formato.
**Correção:** ecoe idêntico.

### A22 · Não validar `requestState` no servidor
**Sintoma:** um cliente adultera o estado e pula uma verificação.
**Correção:** HMAC ou AEAD, com principal autenticado, TTL e identificador da requisição
de origem. E, se precisar ser de uso único, garanta isso **do lado do servidor** — as
medidas anteriores limitam replay, não garantem unicidade.

### A23 · Laço de MRTR sem teto
**Sintoma:** o cliente fica preso perguntando ao usuário para sempre.
**Causa:** a spec **permite** o servidor responder `input_required` indefinidamente.
**Correção:** teto de rodadas. Não é otimização, é requisito de segurança.

### A24 · Esperar requisição do servidor
**Sintoma:** cliente com roteador de requisições de entrada que nunca dispara.
**Causa:** desde `2026-07-28`, servidores **não iniciam requisição**.
**Correção:** apague o código.

### A25 · Cabeçalho HTTP que não bate com o corpo
**Sintoma:** `400` com `-32020 HeaderMismatch`.
**Causa comum e não óbvia:** um balanceador ou WAF reescreveu um cabeçalho `Mcp-*`.
**Correção:** não reescreva; ou revalide depois da reescrita.

### A26 · Não tratar ausência de `resultType`
**Sintoma:** falha ao falar com servidor de revisão anterior.
**Correção:** ausente = `"complete"`, por exigência da spec.

### A27 · Não aceitar `-32002`
**Sintoma:** "recurso não encontrado" vira erro genérico com servidores antigos.
**Correção:** aceite `-32002` **e** `-32602`.

### A28 · `cacheScope: "public"` numa lista que varia por token
**Sintoma:** um usuário vê as ferramentas de outro.
**Causa:** um intermediário compartilhado cacheou a resposta.
**Correção:** `"private"` sempre que o conteúdo depender da autorização.

### A29 · Log que não chega
**Sintoma:** `logging_callback` registrado, nada acontece.
**Causa:** servidor moderno só emite `notifications/message` para requisições que optaram
via `io.modelcontextprotocol/logLevel`.
**Correção:** `log_level="info"` no cliente.

---

## Parte IV · Armadilhas de segurança

### A30 · Aceitar token sem validar audiência
**Sintoma:** nenhum — até virar incidente.
**Correção:** validar `aud`. É a regra mais dura da spec de autorização.

### A31 · Repassar o token do cliente adiante
**Sintoma:** logs da API a jusante mostram identidade errada; controles contornados.
**Correção:** obtenha token próprio (troca de token, client credentials, credencial ligada
ao usuário).

### A32 · Não validar `Origin` no servidor HTTP local
**Sintoma:** nenhum — até uma página web falar com o seu servidor.
**Correção:** validar e responder `403`; ligar só em `127.0.0.1`.

### A33 · Buscar URL de descoberta sem proteção de SSRF
**Sintoma:** credenciais de instância vazadas via `169.254.169.254`.
**Correção:** HTTPS obrigatório, bloqueio de faixas privadas com **biblioteca**, validação
de redirecionamento, proxy de saída.

### A34 · Confiar em `annotations` e em `serverInfo`
**Sintoma:** você tratou como somente-leitura algo que escreve.
**Causa:** são **autodeclarados**. A spec manda tratar anotações como não confiáveis.
**Correção:** classifique você mesmo, do seu lado.

### A35 · Truncar a descrição na tela de aprovação
**Sintoma:** o usuário aprova sem ver a instrução maliciosa que o modelo leu.
**Correção:** mostrar completa, com Unicode normalizado e invisíveis destacados.

### A36 · "Aprovar sempre" sem vínculo à definição
**Sintoma:** *rug pull* — a ferramenta muda depois da aprovação.
**Correção:** vincular ao hash da definição; revogar automaticamente quando mudar.

### A37 · Rodar servidor de terceiro sem sandbox
**Sintoma:** você deu ao autor do servidor acesso ao seu `~/.ssh`.
**Correção:** container, montagem somente-leitura do mínimo, sem rede quando possível.

### A38 · Instalar 30 servidores "para experimentar"
**Sintoma:** contexto estourado, custo alto, superfície enorme.
**Correção:** poucos, de origem conhecida, e desligue o que não usa.

---

## Parte V · Mitos

### M1 · "MCP é seguro porque tem OAuth"
**Falso.** OAuth resolve *quem pode chamar*. Não resolve *o servidor está mentindo para o
modelo*. As duas coisas são ortogonais.

### M2 · "O servidor MCP não pode ver a minha conversa, então é seguro"
**Meia verdade.** Não vê os dados. Mas influencia o modelo pelo texto que devolve, e pode
induzir chamadas a outros servidores. O protocolo isola **dados**, não **influência**.

### M3 · "MCP substitui APIs REST"
**Falso.** Servidores MCP normalmente **chamam** APIs REST por dentro. MCP é a camada de
descoberta e invocação para um consumidor não determinístico.

### M4 · "Mais ferramentas = servidor melhor"
**Falso, e caro.** Cada ferramenta custa contexto em **toda** mensagem e aumenta a chance
de escolha errada.

### M5 · "Se está no registry oficial, é confiável"
**Falso.** O registry verifica **namespace**, não comportamento. Varredura de segurança é
delegada aos registries de pacote e aos agregadores.

### M6 · "MCP é da Anthropic"
**Desatualizado.** Desde 09/12/2025 pertence à Agentic AI Foundation, da Linux Foundation,
cofundada por Anthropic, Block e OpenAI.

### M7 · "Sampling deixa o servidor usar IA de graça"
**Depreciado em `2026-07-28`.** Adoção quase nula, exige canal de volta que não existe
mais, e o modelo de custo nunca foi resolvido. Chame a API do provedor.

### M8 · "Roots limita o que o servidor pode acessar"
**Falso, e perigoso acreditar.** Roots era uma **dica**, nunca controle de acesso. Um
servidor malicioso ignorava. Depreciado. Confinamento se faz com sandbox e permissão de
sistema de arquivos.

### M9 · "Preciso de OAuth para escrever um servidor MCP"
**Falso.** Em stdio, credencial vem do ambiente. A spec **desaconselha** seguir a
especificação de autorização em stdio.

### M10 · "Anotações de ferramenta são garantias"
**Falso.** `readOnlyHint: true` é uma afirmação do servidor sobre si mesmo. A spec manda
os clientes tratarem anotações como **não confiáveis**.

### M11 · "Estruturei a saída, então o cliente valida"
**Só se você declarou o tipo.** Retorno anotado como `dict` ou `list[str]` **não** gera
`outputSchema` no SDK Python 2.x, e `structuredContent` volta nulo. Verificado em prática.

### M12 · "MCP é estável agora"
**Otimista demais.** Cinco revisões em vinte meses, com remoções. A política de doze meses
dá previsibilidade, mas o roadmap de agosto de 2026 já prevê **redesenhar `tools/call`**,
que é mudança que quebra para todo servidor.

---

## Autoteste

1. Por que `print()` derruba um servidor stdio, e por que o sintoma engana?
2. Qual armadilha de ambiente faz o servidor funcionar no terminal e falhar no Claude Desktop? Cite duas.
3. Por que `executar_sql` é sedutor, e quais são os quatro problemas dele?
4. Qual armadilha aparece só quando você passa de uma para duas réplicas?
5. Por que idempotência não é opcional quando o consumidor é um modelo?
6. Quais três coisas o servidor deve pôr dentro do `requestState` protegido?
7. Por que o teto de rodadas do MRTR é requisito de segurança, e não otimização?
8. Quando `cacheScope: "public"` vira vazamento entre usuários?
9. Desminta os mitos M2 e M5, com a razão exata.
10. Qual mito você mesmo acreditava antes deste curso?

---

**Anterior:** [70 · Prática](70-pratica.md) · **Próximo:** [80 · Custos e licenças](80-custos-e-licencas.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Armadilhas A13, A20, A28, A29 e o mito M11 foram medidos nesta máquina (`mcp` 2.1.1,
`@modelcontextprotocol/server` 2.0.0) em 01/09/2026. As demais decorrem da especificação
`2026-07-28` e das páginas oficiais de segurança e de autorização, citadas nos arquivos
[18](18-autorizacao.md) e [19](19-seguranca.md).*
