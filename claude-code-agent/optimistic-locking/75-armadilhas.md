# 75 · Armadilhas, mitos e más práticas

`Nível: intermediário → avançado` · `Atualizado em: 14/08/2026`

Vinte e oito armadilhas e nove mitos. Cada armadilha traz o **sintoma** (como ela se
manifesta), a **causa** e a **correção**. A ordem é aproximadamente a da frequência com que
eu as encontro em revisão de código.

---

## Parte I — Armadilhas de implementação

### A1. Ignorar o número de linhas afetadas

**Sintoma.** Usuários dizem "salvei e não salvou". Zero erros no log.
**Causa.** A guarda existe no `WHERE`, mas ninguém confere o retorno do `UPDATE`.
**Correção.** `if (res.changes === 0) throw new ConflitoDeVersao(...)`. Sempre.

É a armadilha nº 1 do assunto e a mais barata de corrigir. Um sistema com a coluna `version`
e sem essa checagem tem **zero** proteção com aparência total de proteção.

### A2. Retentar sem reler

**Sintoma.** Taxa de erro constante, imune a aumentar o número de tentativas.
**Causa.** O bloco retentado usa o token lido antes do laço.
**Correção.** A leitura tem de estar **dentro** do bloco retentado. Ver [lab 3](70-pratica.md#lab-3--retentar-sem-reler).

### A3. Cliente escolhendo a versão nova

**Sintoma.** Conflitos passam despercebidos de vez em quando; dados inconsistentes sem
explicação.
**Causa.** `SET version = ?` com valor vindo do cliente. Dois clientes podem mandar `8`.
**Correção.** `SET version = version + 1`, calculado pelo banco.

### A4. Versão em `timestamp`

**Sintoma.** Conflitos não detectados sob carga; ou `412` eterno depois de uma migração.
**Causa.** Resolução insuficiente, relógio para trás, perda de precisão na serialização.
**Correção.** Inteiro incremental. Ver [`13 §3.2`](13-tokens-de-versao.md#32-timestamp-a-armadilha-mais-popular).

### A5. ETag fraco com `If-Match`

**Sintoma.** **Todas** as escritas retornam `412`, para todos os clientes, desde sempre.
**Causa.** `If-Match` usa comparação forte (RFC 9110); `W/"7"` nunca casa. O Express gera
ETags fracos por padrão em JSON.
**Correção.** `app.set('etag', 'strong')`, ou gere o ETag a partir da versão.

### A6. Servidor que aceita `PUT` sem `If-Match`

**Sintoma.** Um cliente novo "esquece" o cabeçalho e passa a sobrescrever tudo em silêncio.
**Causa.** A pré-condição é sugerida, não exigida.
**Correção.** Responda `428 Precondition Required`.

### A7. `If-Match: *` tratado como proteção

**Sintoma.** Idem A6, com aparência de estar tudo certo nos logs.
**Causa.** `*` significa só "o recurso existe".
**Correção.** Recuse `*` em rotas de escrita, ou no mínimo registre um aviso.

### A8. Versão que não atravessa a fronteira da API

**Sintoma.** Proteção perfeita no banco, lost updates constantes na aplicação.
**Causa.** O DTO omite `version` "porque é detalhe técnico".
**Correção.** A versão é parte do contrato. Inclua no DTO e no `ETag`.

### A9. Caminhos de escrita alternativos

**Sintoma.** Um job noturno apaga edições feitas durante o dia.
**Causa.** Importações, `update_all`, SQL cru e scripts de correção não passam pelo ORM.
**Correção.** Audite todos os caminhos de escrita, não só o principal. É o achado mais comum
do [lab 12](70-pratica.md#lab-12--auditar-um-sistema-real).

### A10. Usar versão em contador

**Sintoma.** Taxa de conflito altíssima num campo que "não deveria conflitar".
**Causa.** Um delta comutativo modelado como substituição.
**Correção.** `UPDATE x = x ± n WHERE guarda`.

### A11. Versão na linha errada (granularidade)

**Sintoma.** O total do pedido não bate com a soma dos itens, e ninguém viu conflito nenhum.
**Causa.** A invariante é sobre o agregado; a versão está nos filhos.
**Correção.** Versão no agregado, ou `OPTIMISTIC_FORCE_INCREMENT`. Ver [`13 §5`](13-tokens-de-versao.md#5-granularidade-onde-colocar-a-versão).

### A12. Confundir conflito com erro do sistema

**Sintoma.** Painel cheio de `500`; alertas disparando; o serviço está saudável.
**Causa.** `40001` e `OptimisticLockException` tratados como falha inesperada.
**Correção.** São resultados **esperados**. Mapeie para `412`/`409` e para uma métrica própria.

### A13. Retentar o que não é retentável

**Sintoma.** Um bug de validação vira cinco chamadas em vez de uma; cota de API queimada.
**Causa.** O predicado de retentativa é largo demais (`catch (e) { retry }`).
**Correção.** Retente **apenas** conflito: `412`, `40001`, `40P01`, `OptimisticLockException`.

### A14. Efeito externo dentro do bloco retentado

**Sintoma.** Cliente recebe três e-mails; ou é cobrado duas vezes.
**Causa.** `enviarEmail()` dentro do laço de retentativa.
**Correção.** Efeito externo depois do sucesso, ou padrão outbox. Ver [`19 §4`](19-retentativa-e-idempotencia.md#4-efeitos-externos-dentro-de-um-bloco-retentado).

### A15. Retentativa sem jitter

**Sintoma.** A taxa de conflito não cai com o backoff.
**Causa.** Todos voltam no mesmo instante.
**Correção.** *Full jitter*: `aleatorio(0, min(teto, base·2^i))`.

### A16. Retentativa sem limite

**Sintoma.** Uma linha quente derruba o serviço; CPU a 100%, vazão perto de zero.
**Causa.** Laço infinito "para não perder dados".
**Correção.** Orçamento de tempo + limite de tentativas + erro claro no fim.

### A17. Retentativa em várias camadas

**Sintoma.** Sob degradação, a carga no serviço de baixo multiplica por 27.
**Causa.** 3 camadas × 3 tentativas.
**Correção.** Retente em uma camada só, ou use orçamento global de retentativa.

### A18. Transação longa com escrita

**Sintoma.** Um relatório que grava nunca consegue confirmar; falha sempre em `40001`.
**Causa.** A validação para trás sempre vitima a transação mais nova/longa.
**Correção.** Separe leitura de escrita; encurte a transação; ou escale para pessimista após
`k` falhas. Ver [`60 §2.1`](60-teoria-avancada.md#21-validação-para-trás-backward-validation).

### A19. `SELECT ... FOR UPDATE` segurando durante interação humana

**Sintoma.** Conexões esgotadas; `Lock wait timeout exceeded`; o `VACUUM` não avança.
**Causa.** Lock adquirido no `GET` e liberado (talvez) no `POST`.
**Correção.** É exatamente o problema que o optimistic locking resolve. Use OCC, ou um lease.

### A20. Comparar ponto flutuante na checagem versionless

**Sintoma.** Conflitos aleatórios em campos monetários.
**Causa.** Igualdade de `float`/`double`, e conversões entre linguagens.
**Correção.** Coluna de versão explícita. E guarde dinheiro em inteiro de centavos.

### A21. `NULL` na checagem versionless

**Sintoma.** Linhas com campo nulo nunca conseguem ser atualizadas.
**Causa.** `WHERE campo = NULL` é sempre falso.
**Correção.** `IS NOT DISTINCT FROM` (PostgreSQL), `<=>` (MySQL).

### A22. MySQL: `affectedRows` conta linhas **encontradas**

**Sintoma.** Falso conflito quando o usuário salva sem mudar nada.
**Causa.** Por padrão o cliente MySQL reporta *rows matched*, não *rows changed*.
**Correção.** `useAffectedRows` / `CLIENT_FOUND_ROWS`, ou garanta que a versão sempre muda.

### A23. Depender do `REPEATABLE READ` para proteger

**Sintoma.** Depois de migrar de PostgreSQL para MySQL, os lost updates voltam. Sem erro.
**Causa.** O `REPEATABLE READ` do MySQL **não aborta**; o do PostgreSQL aborta.
**Correção.** Não delegue ao nível de isolamento. A guarda explícita funciona em todo banco.

### A24. `xmin` como token durável

**Sintoma.** Depois de um `pg_upgrade` ou `VACUUM FULL`, todos os clientes recebem `412`.
**Causa.** O `xmin` não é preservado por operações de manutenção.
**Correção.** Coluna própria para qualquer token que sobreviva a uma requisição.

### A25. `save()` de entidade detached com versão nula (JPA)

**Sintoma.** Registros **duplicados** em vez de atualizados.
**Causa.** O Spring Data usa a versão para decidir entre `persist` e `merge`.
**Correção.** Carregue a entidade gerenciada, ou copie a versão do DTO.

### A26. Não distinguir `404` de conflito

**Sintoma.** O cliente retenta indefinidamente um recurso que foi apagado.
**Causa.** "Zero linhas" mapeado sempre para conflito.
**Correção.** Um `SELECT` extra **só no caminho de falha**. Ver [`06 §2`](06-exemplos.md#2--distinguir-não-existe-de-conflito).

### A27. Lock distribuído sem fencing token

**Sintoma.** Raríssimo, catastrófico e irreproduzível: dois processos escrevem "ao mesmo tempo".
**Causa.** Pausa de GC maior que o lease. Ver [`18 §4`](18-sistemas-distribuidos.md#4-fencing-tokens-por-que-o-lease-sozinho-não-basta).
**Correção.** Token monotônico verificado **pelo recurso**.

### A28. Não medir

**Sintoma.** Discussões sobre concorrência baseadas em opinião.
**Causa.** Não existe métrica de conflito.
**Correção.** `conflitos / escritas` por rota, e distância de versão. É a correção com maior
retorno de toda esta lista.

---

## Parte II — Mitos

### M1. "Optimistic locking não usa lock nenhum"

**Falso, com precisão.** Existe um lock **interno ao comando**, de microssegundos, que o banco
adquire para executar o `UPDATE` — é ele que torna a validação atômica. O que não existe é
lock mantido **entre** a leitura e a escrita. É a essa janela que o "otimista" se refere.

### M2. "Se eu usar `SERIALIZABLE`, não preciso de coluna de versão"

**Falso.** `SERIALIZABLE` protege **dentro** de uma transação. A janela entre o `GET` e o
`PUT` do usuário abrange **duas transações diferentes**, separadas por minutos. Nenhum nível
de isolamento tem opinião sobre ela — nem poderia.

### M3. "Conflito é raro, não preciso tratar"

**Perigoso.** Conflito raro significa que o caminho de tratamento é **pouco exercitado**, não
que é dispensável. Um caminho de erro nunca testado é um caminho de erro quebrado. E "raro"
costuma ser medido em desenvolvimento, com um usuário.

### M4. "Aumentar o número de tentativas resolve"

**Falso na maioria dos casos.** Se a causa é não reler, mais tentativas não mudam nada
(lab 3). Se a causa é contenção estrutural, mais tentativas trocam erro por latência e
escondem o problema. Tentativa é analgésico, não antibiótico.

### M5. "O ORM cuida disso"

**Meia verdade.** Ele cuida do `UPDATE` que **ele** gera. Não cuida do SQL cru, dos jobs em
lote, da API HTTP, dos DTOs, nem do que o usuário vê quando dá conflito. A proteção quase
sempre existe no caminho principal e falta nos laterais.

### M6. "Pessimista é mais seguro"

**Falso.** Os dois são corretos quando bem implementados. O pessimista troca conflito por
**deadlock, timeout e fila**, que são modos de falha diferentes, não ausência de falha. E ele
é **inaplicável** quando a janela inclui um ser humano.

### M7. "CRDT resolve tudo"

**Falso.** CRDT garante **convergência**, não **invariante**. "Saldo não fica negativo" não é
expressável sem coordenação — é o resultado CALM, um teorema, não uma limitação de biblioteca.
E convergir não é acertar: o merge automático de texto produz frases que nenhum autor escreveu.

### M8. "Basta o `updated_at` que eu já tenho"

**Falso.** Resolução insuficiente, relógio que anda para trás, perda de precisão na
serialização, e a dúvida de qual relógio é o válido. Ver [`13 §3.2`](13-tokens-de-versao.md#32-timestamp-a-armadilha-mais-popular).

### M9. "Isso só importa em escala"

**Falso, e é o mito mais caro.** O *lost update* precisa de **dois** usuários, não de dois
milhões. Um sistema interno com 30 pessoas produz conflitos todo mês; a diferença é que
ninguém percebe, porque não há erro e não há métrica.

---

## Parte III — Revisão de código: perguntas

Para colar no seu template de pull request:

1. Este `UPDATE` grava um valor **absoluto** derivado de uma leitura anterior?
2. Se sim, a versão lida está no `WHERE`?
3. O número de linhas afetadas é conferido?
4. Quem incrementa a versão — o banco ou o cliente?
5. O bloco retentado **relê** o estado?
6. O predicado de retentativa exclui erros permanentes?
7. Há efeito externo dentro do bloco retentado?
8. A rota HTTP exige `If-Match` e responde `428` sem ele?
9. O `ETag` é forte?
10. O `412` devolve o estado atual?
11. A versão está na granularidade da invariante de negócio?
12. Existem caminhos de escrita que não passam por aqui?
13. O usuário recebe uma mensagem que ele entende?
14. Existe métrica de conflito para esta rota?

---

## Autoteste

1. Qual armadilha produz "proteção com aparência total e efeito zero"?
2. Por que aumentar tentativas raramente resolve? Cite dois casos distintos.
3. Corrija a frase "optimistic locking não usa lock nenhum".
4. Por que `SERIALIZABLE` não dispensa a coluna de versão?
5. Qual mito é o mais caro, e por quê?
6. Cite três caminhos de escrita que costumam escapar da proteção.
7. Que armadilha aparece só depois de migrar de PostgreSQL para MySQL?
8. Qual é a correção de maior retorno de toda a lista?
