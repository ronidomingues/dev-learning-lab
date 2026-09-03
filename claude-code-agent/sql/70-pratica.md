# 70 — Laboratórios e exercícios

Nível: iniciante → avançado · Data: 13/08/2026

Doze laboratórios progressivos, todos sobre o banco do
[projeto-modelo](07-projeto-modelo/). Cada um tem **objetivo, enunciado,
critério de sucesso verificável e dica** — a solução comentada está no final
do arquivo.

```bash
cd 07-projeto-modelo
python3 scripts/gerar_dados.py
```

⚠️ **Estes laboratórios não foram executados na escrita deste material** (as
soluções foram; os enunciados intermediários, não). Se algum critério de
sucesso não bater no seu ambiente, verifique primeiro se regerou o banco com a
semente padrão 42.

---

## Nível 1 — Consulta simples

### Lab 1 · Reconhecimento (30 min)

**Objetivo:** nunca escrever consulta sobre um banco que você não olhou.

1. Liste as tabelas e o DDL de cada uma.
2. Para cada tabela, conte as linhas.
3. Para `leitura`, descubra o intervalo de tempo e quantos tags distintos há.
4. Descubra quantas leituras existem de cada qualidade.
5. Para cada tag, encontre mínimo, máximo e média — e diga quais valores são
   fisicamente implausíveis.

**Sucesso:** você consegue descrever o banco em cinco frases sem consultar
mais nada, e apontou pelo menos uma anomalia.

**Dica:** `SELECT name, sql FROM sqlite_master WHERE type='table';`

---

### Lab 2 · O primeiro relatório (45 min)

**Objetivo:** `WHERE`, `GROUP BY`, `ORDER BY`, filtro de data correto.

Produza, para o **dia 10/07/2026**:
- média, mínimo e máximo de cada tag do reator, por hora;
- só dados de qualidade `BOA`;
- ordenado por tag e hora.

**Sucesso:** 24 linhas por tag, exceto onde houver falha de aquisição.

**Armadilha proposital:** se você escrever
`WHERE ts BETWEEN '2026-07-10' AND '2026-07-11'`, vai pegar uma linha a mais
(a das 00:00:00 do dia 11). Use `>= ... AND < ...`.

---

### Lab 3 · Contexto de batelada (1 h)

**Objetivo:** junção temporal.

Para cada batelada concluída, calcule:
- duração real em horas;
- temperatura média, mínima e máxima do TI-101 durante a batelada;
- número de leituras usadas.

**Sucesso:** o número de bateladas bate com
`SELECT COUNT(*) FROM batelada WHERE status='CONCLUIDA'` (**77**). Se der
diferente, sua junção está errada.

**Dica:** intervalo semiaberto, e confira se cabe filtrar o tag antes da
junção.

---

## Nível 2 — Junções e agregação

### Lab 4 · Cardinalidade (45 min)

**Objetivo:** sentir o *fan-out* na pele.

1. `SELECT SUM(carga_kg) FROM batelada` — anote o número.
2. Junte com `analise_lab` e some de novo. Anote.
3. Explique a diferença.
4. Corrija de **três formas diferentes** (agregar antes; `EXISTS`; agregar
   depois com `MAX`).

**Sucesso:** as três formas dão **389.335,0 kg**.

---

### Lab 5 · Anti-join (30 min)

**Objetivo:** achar o que não existe.

1. Bateladas sem nenhuma análise de laboratório.
2. Tags cadastrados sem nenhuma leitura (se houver).
3. Dias do mês sem nenhuma batelada iniciada.
4. Tags que nunca dispararam alarme.

**Sucesso:** o item 1 devolve exatamente **B-2026-0040**, a batelada abortada.

**Dica:** para o item 3 você precisa **gerar** os dias — CTE recursiva.

---

### Lab 6 · Balanço de massa (1 h)

**Objetivo:** `HAVING`, tolerância declarada, diagnóstico.

1. Calcule o erro de balanço de cada batelada.
2. Liste as que passam de 0,5%.
3. Descubra **qual insumo** está causando a diferença.
4. Calcule o custo do erro, supondo R$ 8/kg de solvente.

**Sucesso:** você identifica que o erro é sempre no solvente, sempre ~+12%
sobre a proporção de receita, e sempre nas mesmas bateladas.

---

## Nível 3 — Funções de janela

### Lab 7 · Taxa de aquecimento (1 h)

**Objetivo:** `LAG`, `LEAD`, Δt real.

Para a batelada B-2026-0001, calcule a taxa de aquecimento (°C/min) em cada
minuto da fase de aquecimento, e encontre:
- a taxa máxima;
- o minuto em que ela ocorre;
- a taxa média da fase.

**Sucesso:** a taxa média fica em torno de 1,9 °C/min (o modelo do gerador
sobe de 40 a ~180 °C em 75 minutos).

**Armadilha:** divida pelo Δt **real**, não por 1. No dia 14/07 isso muda o
resultado.

---

### Lab 8 · *Gaps and islands* (1 h 30)

**Objetivo:** o padrão mais útil do SQL analítico.

1. Encontre todos os períodos contínuos em que TI-101 ficou acima de 190 °C.
2. Para cada período: início, fim, duração, pico.
3. **Agrupe períodos separados por menos de 5 minutos** — eles são o mesmo
   distúrbio (*chattering*).
4. Compare o número de períodos antes e depois do agrupamento.

**Sucesso:** o passo 3 reduz o número de eventos. No dia 09/07 há dois blocos
separados por 2 minutos que devem virar um.

---

### Lab 9 · Carta de controle completa (2 h)

**Objetivo:** CEP de verdade.

1. Carta X̄ das médias de temperatura de reação por batelada, com LC, LSC, LIC.
2. Implemente a **regra 1** (ponto além de 3σ).
3. Implemente a **regra 2** (9 pontos seguidos do mesmo lado).
4. Implemente a **regra 3** (6 pontos consecutivos subindo ou descendo).
5. Calcule Cp e Cpk contra a especificação 175–185 °C.

**Sucesso:** a regra 1 aponta as bateladas 23 e 57.

---

## Nível 4 — Integração e produção

### Lab 10 · Qualidade do dado (1 h 30)

**Objetivo:** o roteiro de defesa antes de confiar em qualquer número.

Escreva **uma consulta para cada** um dos seis itens do checklist de
[17-tipos-e-nulos.md](17-tipos-e-nulos.md) §8, adaptada a este banco. Depois:

1. Quantifique o impacto: a média de AI-101 muda quanto se você filtrar a
   qualidade?
2. Calcule a cobertura temporal de cada tag.
3. Produza um "boletim de saúde do dado" de uma tela só.

**Sucesso:** seu boletim identifica as oito anomalias plantadas, listadas no
[README do projeto](07-projeto-modelo/README.md).

---

### Lab 11 · Relatório automatizado (2 h)

**Objetivo:** sair da consulta interativa para o entregável.

Escreva um script Python que:
1. receba o mês como argumento;
2. abra o banco **somente leitura**;
3. produza: OEE, rendimento médio, top 5 causas de parada, lotes retidos;
4. grave um CSV e imprima um resumo;
5. devolva código de saída ≠ 0 se não houver dado no período;
6. tenha ao menos **três testes** com `unittest`.

**Sucesso:** `python3 relatorio.py 2026-07` funciona, e
`python3 relatorio.py 2025-01` falha com mensagem clara e código 1.

---

### Lab 12 · Otimização (2 h)

**Objetivo:** medir, diagnosticar, corrigir, medir de novo.

1. Escreva uma consulta que leve mais de **500 ms** (a de sensor travado
   serve — ela leva ~900 ms).
2. Rode `EXPLAIN QUERY PLAN` e interprete cada linha.
3. Proponha **duas** melhorias: uma reescrevendo a consulta, outra criando
   índice.
4. Meça as três versões (original, reescrita, com índice), cinco execuções
   cada, e relate o **mínimo**.
5. Meça o custo do índice: tamanho do banco antes e depois, e tempo de
   inserção de 10.000 linhas com e sem ele.

**Sucesso:** você tem uma tabela com cinco números e uma recomendação
justificada — inclusive a possibilidade de a recomendação ser "não crie o
índice, porque o custo de escrita não compensa".

---

## Desafios (sem gabarito)

1. **Detecção de deriva de instrumento.** TI-101 e TI-201 têm relação física
   conhecida. Detecte quando essa relação muda de forma sustentada — é
   descalibração, e é diferente de mudança de processo.
2. **Reconciliação de dados.** Implemente a reconciliação clássica de balanço
   de massa por mínimos quadrados, ajustando as medidas para fechar o balanço,
   ponderando pela incerteza de cada instrumento. Até onde dá para ir só em SQL?
3. **Previsão de rendimento.** Usando apenas condições disponíveis **até o fim
   da fase de reação**, preveja o rendimento antes da descarga. Meça o erro
   contra o realizado.
4. **Consulta unificada.** Junte processo, laboratório, alarme e parada numa
   view única "história completa da batelada", que caiba numa tela por lote.
5. **Custo do alarme.** Quanto custa cada alarme espúrio, medido em tempo de
   atenção do operador? Modele e defenda o número.

---

## Soluções comentadas

<details>
<summary><b>Lab 4 — as três correções do fan-out</b></summary>

```sql
-- 1. agregar ANTES de juntar
SELECT SUM(b.carga_kg)
  FROM batelada b
  LEFT JOIN (SELECT batelada_id, COUNT(*) AS n
               FROM analise_lab GROUP BY batelada_id) a USING (batelada_id);

-- 2. EXISTS (não multiplica)
SELECT SUM(carga_kg) FROM batelada b
 WHERE EXISTS (SELECT 1 FROM analise_lab a WHERE a.batelada_id = b.batelada_id)
    OR NOT EXISTS (SELECT 1 FROM analise_lab a WHERE a.batelada_id = b.batelada_id);

-- 3. agregar depois, com MAX (a carga é a mesma nas 4 linhas do grupo)
SELECT SUM(carga) FROM (
    SELECT b.batelada_id, MAX(b.carga_kg) AS carga
      FROM batelada b LEFT JOIN analise_lab a USING (batelada_id)
     GROUP BY b.batelada_id);
```
As três devolvem **389.335,0**. A primeira é a melhor: é a que continua certa
quando alguém adiciona um quinto ensaio.
</details>

<details>
<summary><b>Lab 8 — agrupar eventos próximos</b></summary>

```sql
WITH eventos AS (
    -- gaps and islands padrão: acha os blocos contíguos
    WITH m AS (SELECT ts, valor, CASE WHEN valor > 190 THEN 1 ELSE 0 END AS alto
                 FROM v_leitura_boa WHERE tag_id = 'TI-101'),
         b AS (SELECT *, ROW_NUMBER() OVER (ORDER BY ts)
                       - ROW_NUMBER() OVER (PARTITION BY alto ORDER BY ts) AS g
                 FROM m)
    SELECT MIN(ts) AS inicio, MAX(ts) AS fim, MAX(valor) AS pico
      FROM b WHERE alto = 1 GROUP BY g
),
com_lacuna AS (
    -- segunda passada: marca o início de um DISTÚRBIO (>5 min do anterior)
    SELECT *,
           CASE WHEN (julianday(inicio)
                      - julianday(LAG(fim) OVER (ORDER BY inicio))) * 1440 > 5
                  OR LAG(fim) OVER (ORDER BY inicio) IS NULL
                THEN 1 ELSE 0 END AS novo
      FROM eventos
),
disturbios AS (
    SELECT *, SUM(novo) OVER (ORDER BY inicio ROWS UNBOUNDED PRECEDING) AS d
      FROM com_lacuna
)
SELECT d, MIN(inicio) AS inicio, MAX(fim) AS fim, COUNT(*) AS blocos,
       ROUND(MAX(pico), 2) AS pico
  FROM disturbios GROUP BY d ORDER BY inicio;
```
**O padrão aplicado duas vezes**: uma para achar os blocos acima do limite,
outra para agrupar os blocos próximos. É a técnica geral.
</details>

<details>
<summary><b>Lab 9 — regra 3 de Nelson (6 pontos monotônicos)</b></summary>

```sql
WITH p AS (
    SELECT b.ts_inicio, f.batelada_id, AVG(f.valor) AS media
      FROM v_leitura_fase f JOIN batelada b USING (batelada_id)
     WHERE f.tag_id = 'TI-101' AND f.fase = 'reacao'
     GROUP BY b.ts_inicio, f.batelada_id
),
dir AS (
    SELECT *, CASE WHEN media > LAG(media) OVER (ORDER BY ts_inicio) THEN 1
                   WHEN media < LAG(media) OVER (ORDER BY ts_inicio) THEN -1
                   ELSE 0 END AS sentido
      FROM p
),
blocos AS (
    SELECT *, ROW_NUMBER() OVER (ORDER BY ts_inicio)
            - ROW_NUMBER() OVER (PARTITION BY sentido ORDER BY ts_inicio) AS g
      FROM dir
)
SELECT sentido, MIN(ts_inicio) AS de, MAX(ts_inicio) AS ate, COUNT(*) AS seguidos
  FROM blocos WHERE sentido <> 0
 GROUP BY sentido, g
HAVING COUNT(*) >= 5      -- 5 variações = 6 pontos
 ORDER BY de;
```
Repare no `>= 5`: seis **pontos** produzem cinco **variações**. Errar isso por
um é o bug clássico da regra 3.
</details>

---

## Como saber que você aprendeu

Você não precisa de certificado. Precisa de conseguir, sozinho:

- [ ] Descrever um banco desconhecido em cinco consultas.
- [ ] Escrever uma junção de três tabelas **conferindo a cardinalidade**.
- [ ] Explicar por que um `LEFT JOIN` virou `INNER` sem alguém te contar.
- [ ] Escrever uma média móvel com a moldura correta, de primeira.
- [ ] Ler um `EXPLAIN QUERY PLAN` e dizer o que está errado.
- [ ] Encontrar dado faltante que ninguém sabia que faltava.
- [ ] Refazer um relatório da sua planta e **explicar a diferença** para a
      planilha original.
- [ ] Recusar um número — seu ou de outra pessoa — porque a consulta que o
      gerou tem um problema que você consegue nomear.

O último item é o que separa quem usa SQL de quem confia em SQL.

---

*Próximo: [75-armadilhas.md](75-armadilhas.md).*
