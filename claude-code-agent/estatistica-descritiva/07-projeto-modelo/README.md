# `resumo` — o relatório estatístico que se recusa a mentir

`Projeto-modelo do assunto` · `Nível: intermediário` · `Última atualização: 20/08/2026`
`Python 3.10+ · zero dependências externas · 83 testes passando`

---

## O que é

Um programa de linha de comando que lê uma coluna numérica de um CSV e produz um relatório
estatístico completo — **e que avisa, em cada caso, quais das medidas que ele acabou de
calcular não devem ser usadas.**

Qualquer biblioteca calcula média e desvio padrão. A parte incomum deste projeto é o módulo
[`resumo/diagnostico.py`](resumo/diagnostico.py): ele examina os dados e emite avisos com
gravidade, explicação e **ação recomendada**. Um aviso que não diz o que fazer é ruído; aqui,
todo aviso termina em uma instrução.

O projeto existe para exercitar, em código executável, os conceitos centrais do curso:
posição, dispersão, forma, quantis, robustez, erro padrão, intervalo de confiança e bootstrap.
Tudo é escrito do zero — inclusive a distribuição t de Student — porque **em estatística
descritiva, ver a conta acontecer é o conteúdo**.

---

## Pré-requisitos

- **Python 3.10 ou superior.** Só isso. Confira com `python3 --version`.
- Nenhuma biblioteca externa. Nenhum `pip install`. Nenhuma conta em serviço.
- Se o Python não estiver instalado: [../03-instalacao.md](../03-instalacao.md).

> **Por que zero dependências?** Três motivos, nesta ordem de importância:
> (1) o objetivo didático exige que cada fórmula esteja visível, não escondida atrás de
> `np.std()`; (2) um projeto sem dependências continua rodando daqui a dez anos, e é isso que
> diferencia material de aprendizado de tutorial que apodrece; (3) elimina a barreira do
> primeiro dia — nada de ambiente virtual, proxy corporativo ou conflito de versão entre
> você e o primeiro resultado.

---

## Como rodar — comandos exatos

```bash
cd estatistica-descritiva/07-projeto-modelo
```

**1. Ver funcionando, sem nenhum arquivo:**

```bash
python3 -m resumo --demo
```

**2. Rodar sobre um CSV de exemplo (formato brasileiro, com sujeira proposital):**

```bash
python3 -m resumo dados/alugueis.csv --coluna aluguel
```

**3. Sobre dados bem comportados, para ver o contraste:**

```bash
python3 -m resumo dados/alturas.csv --coluna altura_m
```

**4. Saída em JSON, para encadear com outro programa:**

```bash
python3 -m resumo dados/alugueis.csv --coluna aluguel --formato json
```

**5. Rodar os testes:**

```bash
python3 -m unittest discover -s testes
```
```
# esperado:
# ...................................................................................
# ----------------------------------------------------------------------
# Ran 83 tests in 0.75s
#
# OK
```

**6. Sobre os seus próprios dados:**

```bash
python3 -m resumo /caminho/do/seu.csv --coluna nome_da_coluna
```

### Todas as opções

```bash
python3 -m resumo --help
```

| Opção | Padrão | Para quê |
|---|---|---|
| `--coluna`, `-c` | primeira coluna numérica | qual coluna analisar |
| `--formato`, `-f` | `texto` | `texto` ou `json` |
| `--confianca` | `0.95` | nível dos intervalos (0,5 a 1,0) |
| `--bootstrap` | `2000` | reamostragens do bootstrap (mínimo 100) |
| `--semente` | `42` | semente do sorteio — **registre-a nos seus relatórios** |
| `--encoding` | `utf-8` | tente `latin-1` para exportações antigas do Excel |
| `--separador` | detectado | `,` ou `;` |
| `--decimal` | detectado | `.` ou `,` — só se a detecção errar |
| `--demo` | — | roda com dados embutidos |

Códigos de saída: `0` sucesso · `1` erro de leitura ou cálculo · `2` erro de uso.

---

## O que a saída mostra

Com dados **bem comportados** (`dados/alturas.csv`), o fim do relatório é:

```
── DIAGNÓSTICO ───────────────────────────────────────────────────────────
  Nenhum aviso. As medidas usuais descrevem bem estes dados.

── FRASE SUGERIDA PARA O RELATÓRIO ───────────────────────────────────────
  Média de 1,7205 (DP 0,083153; IC95% da média: 1,7055 a 1,7355); n = 120.
  Mediana 1,7245, faixa observada de 1,539 a 1,9.
```

Com dados **assimétricos** (salários, aluguéis), o mesmo programa muda de recomendação:

```
── DIAGNÓSTICO ───────────────────────────────────────────────────────────
  [GRAVE] distribuição assimétrica à direita (média/mediana = 2,02)
      Média = 7.060 e mediana = 3.500. Quando as duas divergem tanto, a média
      deixa de descrever o caso típico: ela é puxada pelos valores extremos.
      → Relate a MEDIANA como valor típico. Use a média apenas se a pergunta
        for sobre o TOTAL (folha, faturamento, carga).

  [GRAVE] desvio padrão maior que a média
      DP = 11.506,07 contra média = 7.060 (CV = 1,6298).
      → Considere escala logarítmica, ou relate mediana e IQR. Um intervalo
        média ± DP aqui incluiria valores negativos, que são impossíveis
        nesta variável.

── FRASE SUGERIDA PARA O RELATÓRIO ───────────────────────────────────────
  Mediana de 3.500 (IC95% por bootstrap: 2.500 a 5.200); IQR de 2.650 a 5.600; n = 15.
  p95 = 20.700 e máximo = 48.000.
  A distribuição é assimétrica; a média (7.060) não representa o caso típico
  e não deve ser usada como meta ou expectativa.
```

**A "frase sugerida" é o produto final.** Ela existe para ser copiada e colada — e para que a
escolha entre média e mediana seja tomada pelo diagnóstico, não pela conveniência de quem
escreve o relatório.

O relatório completo tem sete seções: procedência dos dados · posição · dispersão · quantis ·
forma · incerteza · distribuição (histograma e boxplot em ASCII) · diagnóstico · frase final.

---

## Estrutura de pastas

```
07-projeto-modelo/
├── README.md                 este arquivo
├── resumo/
│   ├── __init__.py           versão do pacote
│   ├── __main__.py           CLI: argumentos, validação, códigos de saída   (131 linhas)
│   ├── formato.py            números em pt-BR sem depender de locale         (49 linhas)
│   ├── leitura.py            CSV com contabilidade honesta do descartado    (227 linhas)
│   ├── medidas.py            todas as medidas, escritas do zero             (243 linhas)
│   ├── incerteza.py          t de Student, IC e bootstrap, sem SciPy        (200 linhas)
│   ├── diagnostico.py        ⭐ a camada de honestidade                      (184 linhas)
│   └── relatorio.py          montagem, histograma e boxplot em ASCII        (310 linhas)
├── dados/
│   ├── alugueis.csv          pt-BR, com ausentes, inválido e sentinela −999
│   ├── alturas.csv           bem comportado, quase normal
│   └── notas.csv             escala ordinal de 1 a 5 disfarçada de número
└── testes/
    └── test_resumo.py        83 testes                                      (474 linhas)
```

---

## O que cada decisão de projeto ensina

Esta seção é o motivo de o projeto existir. Cada escolha abaixo é uma lição do curso
materializada em código.

### 1. Variância pelo algoritmo de Welford, não pela fórmula do livro

[`medidas.py:variancia`](resumo/medidas.py) — a forma ingênua `Σx²/n − x̄²` é
matematicamente correta e **numericamente desastrosa**: quando a média é grande e a dispersão
pequena, subtrai-se um número enorme de outro quase igual e sobra ruído de arredondamento.
Ela chega a devolver variância **negativa**, o que é impossível por definição.

O teste `test_welford_evita_cancelamento_catastrofico` usa valores em torno de 10⁹ e verifica
que a variância bate com a dos mesmos dados deslocados para perto de zero.

> **Lição:** fórmula correta no papel ≠ algoritmo correto no computador. Ponto flutuante tem
> 15 a 17 dígitos, e você pode perder todos eles numa subtração.

### 2. Quantis do tipo 7, declarado no código

[`medidas.py:quantil`](resumo/medidas.py) — existem **nove** definições de quantil
(Hyndman & Fan, 1996). O tipo 7 foi escolhido porque é o padrão do NumPy, do pandas, do R e
do `PERCENTIL.INC` do Excel — assim os números deste programa batem com as ferramentas que
o leitor vai usar depois. O teste confere contra a saída conhecida do NumPy.

> **Lição:** quando existe mais de uma convenção, escolher já não basta — é preciso
> **declarar**. Ver [../05-manual-de-uso.md](../05-manual-de-uso.md), §5.6.

### 3. Intervalo da média pela **t de Student**, implementada à mão

[`incerteza.py`](resumo/incerteza.py) — usar `1,96` com `n = 10` produz um intervalo
estreito demais e uma falsa sensação de precisão. O correto é a t, e o projeto a implementa
com a função beta incompleta em fração continuada (algoritmo de Lentz), mais bissecção para
inverter.

Os valores batem com as **tabelas impressas** até a quarta casa: `t(0,95; 9) = 2,2622`,
`t(0,95; 30) = 2,0423`. O teste `test_t_critico_bate_com_a_tabela_impressa` fixa isso.

> **Lição:** "não tenho SciPy" nunca é motivo para usar a aproximação errada. E conferir
> contra uma fonte externa (a tabela) é um teste de verdade; conferir contra a própria saída
> não é teste nenhum.

### 4. Bootstrap para a mediana, com semente obrigatória

[`incerteza.py:ic_bootstrap`](resumo/incerteza.py) — a mediana não tem fórmula simples de
erro padrão. Em vez de suposição, reamostragem. A semente tem valor padrão e vai impressa no
relatório, porque **simulação sem semente registrada não é reprodutível, e o que não é
reprodutível não é evidência**.

### 5. O módulo de diagnóstico é maior que o de relatório em conteúdo, não em linhas

[`diagnostico.py`](resumo/diagnostico.py) — sete verificações, cada uma correspondendo a um
erro real do arquivo [../75-armadilhas.md](../75-armadilhas.md):

| Verificação | Armadilha que ela evita |
|---|---|
| razão média/mediana | relatar média em distribuição assimétrica |
| DP > média em dados positivos | usar "média ± DP" onde isso incluiria valores impossíveis |
| cobertura real de 1 DP ≠ 68% | supor normalidade sem olhar |
| cerca de 1,5×IQR | ignorar outliers — **ou removê-los sem investigar** |
| poucos valores distintos | tirar média de escala ordinal (Likert) |
| excesso de zeros | tratar "não medido" como "zero" |
| múltiplos de 5 ou 10 | reportar mais precisão do que os dados têm |

> **Lição:** a parte difícil da análise não é calcular, é **saber quando não acreditar no que
> se calculou**. Um relatório que só apresenta números terceiriza essa decisão para quem lê —
> e quem lê normalmente não tem como tomá-la.

### 6. Contabilidade explícita do que foi descartado

[`leitura.py`](resumo/leitura.py) e a seção **PROCEDÊNCIA** do relatório: linhas do arquivo,
valores usados, ausentes, inválidos (com exemplos e número da linha) e sentinelas suspeitas
(`-999`, `9999`).

> **Lição:** é aqui que uma análise vira mentira sem ninguém mentir. Se 12% das linhas somem
> na conversão e ninguém conta, o resultado descreve os 88% que sobreviveram — que podem ser
> exatamente os casos fáceis.

### 7. A ambiguidade que não tem solução, e o que fazer com ela

`"1.500"` é mil e quinhentos em pt-BR e um e meio em en-US. **Nenhuma heurística resolve isso
sempre** — a informação não está no dado.

Esta é a lição mais honesta do projeto porque ela **quebrou o próprio projeto durante o
desenvolvimento**: a primeira versão do detector supunha milhar sempre que via três dígitos
depois do ponto, e o arquivo `alturas.csv` foi lido como se as pessoas medissem 1.734
milímetros. O diagnóstico gritou (15 outliers, assimetria −2,2, "dentro de 1 DP: 88%"), o que
é a defesa funcionando — mas o número já estava errado na origem.

A política final, em [`leitura.py`](resumo/leitura.py):

1. se houver **alguma vírgula** na coluna, contar evidências e decidir;
2. se não houver nenhuma, adotar o **ponto** (padrão de intercâmbio, e a escolha menos
   destrutiva);
3. se ainda assim a coluna for suspeita, **declarar a ambiguidade no relatório** e oferecer
   `--decimal` para o usuário decidir.

> **Lição de ofício:** quando a informação não está no dado, o certo não é adivinhar melhor —
> é escolher o padrão menos destrutivo e **avisar**. Há um teste de regressão específico:
> `test_altura_nao_vira_milimetro`.

### 8. Formatação brasileira sem `locale`

[`formato.py`](resumo/formato.py) — `locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')` falha em
contêiner enxuto, em CI e na máquina do colega, e falha **só na hora de rodar**. Formatar à
mão são dez linhas e nunca quebra.

### 9. Testes que conferem contra fonte externa

[`testes/test_resumo.py`](testes/test_resumo.py) — sempre que possível, o valor esperado vem
de fora do projeto: tabela publicada da t, saída conhecida do NumPy, identidade matemática
(desigualdade harmônica ≤ geométrica ≤ aritmética; variância invariante a deslocamento;
`g⁴ = produto dos fatores`).

Três testes merecem menção:

- `test_mad_ignora_outlier_e_dp_nao` — acrescenta um valor absurdo e verifica que o desvio
  padrão cresce mais de 10× enquanto o MAD cresce menos de 2×. É **robustez medida**,
  não afirmada.
- `test_quadruplicar_n_reduz_margem_pela_metade` — a lei da raiz quadrada como asserção.
- `test_todo_aviso_tem_acao` — garante que nenhum aviso seja adicionado sem instrução.

---

## Limitações conhecidas (ditas de propósito)

Nenhum projeto honesto esconde o que não faz.

1. **Uma coluna por vez.** Não há correlação, regressão nem análise multivariada. O assunto
   deste projeto é a descrição univariada; relação entre variáveis é o arquivo
   [../16-relacao-entre-variaveis.md](../16-relacao-entre-variaveis.md).
2. **Tudo em memória.** Um CSV maior que a RAM não passa. Para isso seriam necessários
   algoritmos de uma passada e esboços (t-digest, KLL) — ver
   [../65-estado-da-arte.md](../65-estado-da-arte.md).
3. **O IC bootstrap é percentílico simples**, não BCa (corrigido por viés e aceleração).
   Com `n < 20` e distribuições muito assimétricas, ele é ligeiramente otimista.
4. **Sem teste de normalidade formal** (Shapiro-Wilk, Anderson-Darling). Isso é deliberado:
   com `n` grande, esses testes rejeitam normalidade por desvios irrelevantes; com `n`
   pequeno, não detectam desvios grandes. A **cobertura empírica de 1 DP** é mais informativa
   e mais honesta. Ver [../75-armadilhas.md](../75-armadilhas.md).
5. **Não trata dados ponderados nem delineamento amostral complexo** (estratos, conglomerados,
   pesos de pós-estratificação). Uma pesquisa de opinião real precisa disso, e a fórmula
   `s/√n` **subestima** o erro nesse caso.
6. **Não detecta série temporal.** Se as observações forem correlacionadas no tempo, o erro
   padrão calculado aqui é otimista, às vezes por um fator grande.

---

## Exercícios sobre este código

Em ordem crescente de dificuldade. Todos cabem no projeto sem reescrevê-lo.

1. **Fácil.** Acrescente a **média winsorizada** (em vez de descartar os extremos, substitua-os
   pelo valor do percentil de corte) em `medidas.py`, com teste.
2. **Fácil.** Faça o histograma aceitar `--classes N` pela linha de comando e observe como a
   *aparência* dos dados muda com o número de classes.
3. **Médio.** Acrescente um aviso de **bimodalidade**: divida os dados em duas metades pela
   mediana e verifique se cada metade tem sua própria concentração.
4. **Médio.** Implemente o **z-score modificado** (baseado no MAD, não no DP) como detector
   alternativo de outlier, e compare com a cerca de 1,5×IQR nos três arquivos de `dados/`.
5. **Difícil.** Troque o IC bootstrap percentílico pelo **BCa** e verifique, por simulação,
   se a cobertura real se aproxima mais dos 95% nominais.
6. **Difícil.** Implemente um resumo de **uma passada** com `t-digest` ou reservatório, capaz
   de estimar quantis sem guardar todos os dados, e compare o erro contra o cálculo exato.

---

## Autoteste

1. Por que a variância é calculada por Welford e não por `Σx²/n − x̄²`?
2. Por que o IC da média usa a t de Student e não `1,96`?
3. Por que a semente do bootstrap aparece impressa no relatório?
4. O que a seção PROCEDÊNCIA evita?
5. Por que o projeto não tem teste de normalidade?
6. `"1.500"` numa coluna sem nenhuma vírgula: o que o programa faz, e por quê?
7. Qual é a diferença entre o que este programa faz e o que `df.describe()` faz?

<details><summary>Respostas</summary>

1. Porque a forma ingênua sofre cancelamento catastrófico quando a média é grande e a
   dispersão pequena — chega a devolver variância negativa. Welford é estável.
2. Porque com `n` pequeno a normal produz um intervalo estreito demais. `t(0,95; 9) = 2,2622`
   contra `1,96`: 15% mais largo, e é essa largura que corresponde à confiança declarada.
3. Porque sem ela o resultado não é reproduzível por outra pessoa, e um número que ninguém
   consegue reproduzir não é evidência.
4. Evita que linhas descartadas silenciosamente enviesem o resultado. Se 12% do arquivo não
   converteu, quem lê precisa saber disso antes de olhar a média.
5. Porque com `n` grande esses testes rejeitam normalidade por desvios irrelevantes e com `n`
   pequeno não detectam desvios grandes. A cobertura empírica de 1 DP responde a pergunta que
   realmente importa: *a regra dos 68% vale aqui?*
6. Adota o **ponto** como decimal (1,5) e, se quase todos os valores tiverem três dígitos
   depois do ponto, **declara a ambiguidade** e oferece `--decimal`. Porque a informação não
   está no dado, e adivinhar em silêncio já quebrou este projeto uma vez.
7. `describe()` calcula e cala. Este programa calcula, **diagnostica** e diz qual medida usar —
   e escreve a frase final por você, escolhendo entre média e mediana conforme os dados, não
   conforme a conveniência.

</details>

---

**Voltar ao mapa do assunto:** [../00-MAPA.md](../00-MAPA.md)
