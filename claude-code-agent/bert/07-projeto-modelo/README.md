# Projeto-modelo · Triagem automática de chamados de suporte

`Nível: intermediário` · `Executado e verificado em 12/08/2026`

Uma aplicação **pequena mas inteira**: lê chamados de suporte em português, classifica em
quatro categorias, expõe o resultado por linha de comando e por HTTP, e tem testes.
Roda em **CPU comum, em menos de um minuto de treino**.

Não é um trecho de tutorial. Tem tratamento de erro, configuração externa, divisão correta
dos dados, limiar de confiança e uma seção honesta com o que ele **não** faz bem.

---

## O que ele faz

```
"o sistema caiu e dá erro 500 ao abrir o painel"   →  TECNICO       (98,0% de confiança)
"quanto custa o plano com mais usuários"           →  COMERCIAL     (94,7%)
"minha fatura veio com valor errado"               →  FINANCEIRO    (96,6%)
"solicito o cancelamento do contrato"              →  CANCELAMENTO  (95,9%)
```

Categorias: `FINANCEIRO`, `TECNICO`, `COMERCIAL`, `CANCELAMENTO`.
Modelo base: **BERTimbau** (`neuralmind/bert-base-portuguese-cased`), BERT-base pré-treinado
em português do Brasil, licença MIT.

---

## Pré-requisitos

- Python 3.10+ e o ambiente do [`../03-instalacao.md`](../03-instalacao.md) pronto
- ~2 GB de disco livre (440 MB do modelo base + ~420 MB do modelo treinado + checkpoints)
- **GPU não é necessária** — o treino inteiro leva ~60 s em CPU

---

## Como rodar — comandos exatos

```bash
cd bert/07-projeto-modelo
```

```bash
python3.12 -m venv .venv && source .venv/bin/activate     # Linux/macOS
# .venv\Scripts\Activate.ps1                              # Windows PowerShell
```

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu   # ou o canal CUDA
```

```bash
pip install -r requirements.txt
```

```bash
python treinar.py
```

```bash
python prever.py "não consigo acessar o sistema desde ontem"
```

```bash
pytest -q testes/
```

```bash
uvicorn api:app --port 8000
```

```bash
curl -X POST http://localhost:8000/prever \
     -H "Content-Type: application/json" \
     -d '{"texto": "quero cancelar meu contrato"}'
```

---

## Saída real do treino

Execução de **12/08/2026**, Ubuntu, Python 3.10.12, `torch` 2.13.0+cpu,
`transformers` 5.15.0, sem GPU, com a configuração padrão:

```
[dados] 180 exemplos, 4 classes
categoria
FINANCEIRO      45
TECNICO         45
COMERCIAL       45
CANCELAMENTO    45
[divisão] treino=122 validação=22 teste=36
[treino] modelo base: neuralmind/bert-base-portuguese-cased | acelerador: CPU

=== Resultado no conjunto de teste ===
              precision    recall  f1-score   support

CANCELAMENTO      1.000     0.667     0.800         9
   COMERCIAL      1.000     1.000     1.000         9
  FINANCEIRO      0.818     1.000     0.900         9
     TECNICO      0.900     1.000     0.947         9

    accuracy                          0.917        36
   macro avg      0.930     0.917     0.912        36

Matriz de confusão (linha = verdadeiro, coluna = previsto)
              CANCELAMENTO  COMERCIAL  FINANCEIRO  TECNICO
CANCELAMENTO             6          0           2        1
COMERCIAL                0          9           0        0
FINANCEIRO               0          0           9        0
TECNICO                  0          0           0        9
```

Tempo total: **~61 segundos** em CPU (treino 6 épocas + avaliação + salvamento).
Na API, a latência medida por requisição ficou em **35 a 43 ms**, em CPU.

**Leia a matriz de confusão, não só a acurácia.** Ela conta a história real: `COMERCIAL`,
`FINANCEIRO` e `TECNICO` saíram perfeitos em *recall*, e todos os erros do modelo estão numa
linha só — `CANCELAMENTO`, que perdeu 3 dos 9 (2 viraram `FINANCEIRO`, 1 virou `TECNICO`).
Faz sentido linguístico: "cancelei mês passado e continuam me cobrando" é um chamado que
pertence honestamente às duas categorias. Nenhuma dessas informações aparece no número
"91,7% de acurácia".

---

## Estrutura de pastas

```
07-projeto-modelo/
├── config.py             # TODA a configuração, sobrescrevível por variável de ambiente
├── treinar.py            # carrega → divide → tokeniza → treina → avalia → salva
├── prever.py             # inferência: CLI + função `prever()` reutilizável
├── api.py                # FastAPI: POST /prever e GET /saude
├── requirements.txt      # dependências com versões mínimas
├── .gitignore            # impede que 420 MB de pesos entrem no Git
├── dados/
│   └── chamados.csv      # 180 chamados sintéticos rotulados (45 por classe)
├── testes/
│   └── test_projeto.py   # 11 testes: dados, tokenização, predição, erro
├── modelo-treinado/      # (gerado por treinar.py — ~417 MB, fora do Git)
└── checkpoints/          # (gerado durante o treino — apague depois, ~1,3 GB)
```

---

## O que cada decisão de projeto ensina

### 1. Divisão em **três** conjuntos, não dois

```python
treino=122   validação=22   teste=36
```

- **Treino** — o modelo ajusta os pesos aqui.
- **Validação** — usado a cada época para escolher o melhor checkpoint
  (`load_best_model_at_end=True`, `metric_for_best_model="f1_macro"`).
- **Teste** — usado **uma vez só**, no fim.

Por que três? Porque escolher o melhor checkpoint *olhando* a validação já contamina a
validação: ela deixou de ser uma medida imparcial e virou parte do treino. Se você reportar o
número da validação como resultado final, está reportando um número inflado. É o erro mais
comum e mais silencioso do campo. Ver [`../75-armadilhas.md`](../75-armadilhas.md).

### 2. Divisão **estratificada** e sem duplicatas

```python
train_test_split(df, stratify=rotulos, random_state=config.semente)
df = df.drop_duplicates(subset=[config.coluna_texto])
```

Sem `stratify`, uma classe pode ficar sub-representada no teste por puro azar do sorteio.
Sem `drop_duplicates`, o mesmo texto pode aparecer em treino **e** em teste — o modelo
"acerta" porque decorou, e a métrica vira ficção. Isso é *vazamento de dados* (`data leakage`),
e existe um teste no projeto que falha se você introduzir uma duplicata no CSV.

### 3. `f1_macro`, não acurácia, como métrica de seleção

Aqui as classes estão perfeitamente balanceadas (45 cada), então os dois números quase
coincidem. Em produção nunca é assim: uma classe costuma ter 10× mais exemplos. A acurácia
premia quem acerta a classe grande e ignora a pequena; a F1 macro dá o mesmo peso a cada
classe e denuncia o modelo preguiçoso. Definir a métrica errada é escolher otimizar a coisa
errada — e o modelo vai obedecer.

### 4. Padding por lote, não por conjunto

```python
tokenizador(lote["text"], truncation=True, max_length=128)   # sem padding aqui
data_collator=DataCollatorWithPadding(tokenizador)           # o collator preenche por lote
```

Preencher tudo com zeros até 128 tokens desperdiça cálculo em textos curtos: o custo da
atenção cresce com o **quadrado** do comprimento. Preenchendo só até o maior item de cada
lote, o treino fica sensivelmente mais rápido sem mudar o resultado. Ver
[`../13-arquitetura-encoder.md`](../13-arquitetura-encoder.md).

### 5. `model.eval()` e `torch.no_grad()` na inferência

Sem `eval()`, o *dropout* continua ligado e a **mesma frase devolve respostas diferentes** a
cada chamada — um bug que passa despercebido em teste manual e aparece como "o modelo está
instável" em produção. Sem `no_grad()`, o PyTorch monta o grafo de derivadas à toa: mais
memória, mais lentidão.

### 6. Carregar o modelo **uma vez** por processo

```python
@functools.lru_cache(maxsize=1)
def carregar(): ...
```

E, na API, carregar na subida do serviço (`lifespan`), não na primeira requisição. Sem isso,
cada requisição relê 417 MB do disco e a latência sai de ~40 ms para vários segundos. É o
erro de produção nº 1 com modelos desta família.

### 7. Limiar de confiança e a rota para o humano

```python
encaminhar_para_humano = confianca < 0.60
```

Um classificador **sempre** devolve alguma classe, inclusive para texto que não pertence a
nenhuma. O limiar cria a saída "não sei", que é o que permite integrar o modelo a um processo
real sem que ele decida errado com convicção. Onde colocar o limiar é decisão de negócio, não
de engenharia: quanto custa um erro *versus* quanto custa a revisão humana?

### 8. Configuração fora do código

Nenhum caminho ou hiperparâmetro está *hardcoded* no meio da lógica. Tudo em `config.py`,
sobrescrevível por ambiente:

```bash
EPOCAS=10 TAXA_APRENDIZADO=2e-5 python treinar.py
MODELO_BASE=answerdotai/ModernBERT-base python treinar.py    # troca o modelo, mesmo código
```

### 9. Semente fixa

```python
set_seed(42)
```

Sem isso, dois treinos idênticos dão números diferentes e você não consegue saber se a
melhora veio da sua mudança ou do acaso. Em GPU, mesmo com semente, resta uma
não-determinicidade residual — explicada em [`../03-instalacao.md`](../03-instalacao.md#reprodutibilidade).

---

## Experimentos reais deste projeto (e a lição que vale mais que o código)

Todos rodados nesta mesma máquina, mesma semente, mudando **uma** variável por vez:

| Exemplos no CSV | Épocas | Taxa de aprendizado | Acurácia (teste) | F1 macro (teste) | Confiança típica |
|---|---|---|---|---|---|
| 100 | 4 | 3e-5 | 0,800 | 0,801 | 35–45% |
| 100 | 6 | 5e-5 | 0,650 | 0,641 | 72–84% |
| 100 | 10 | 5e-5 | 0,700 | 0,696 | 83–88% |
| **180** | **4** | **3e-5** | **0,917** | **0,915** | 46–70% |
| **180** | **6** | **5e-5** | **0,917** | **0,912** | **95–98%** ← padrão |

Três conclusões, e a primeira é a mais importante que este projeto tem a ensinar:

1. **Mais dados venceu qualquer ajuste de hiperparâmetro.** Passar de 100 para 180 exemplos
   levou a F1 de ~0,70 para ~0,91. Nenhuma combinação de épocas e taxa de aprendizado chegou
   perto disso com 100 exemplos. Se seu modelo está ruim, a resposta quase sempre é **rotular
   mais dados**, não mexer nos números.
2. **Com poucos dados, a variação entre execuções é enorme.** Com 100 exemplos, a F1 pulou de
   0,64 a 0,80 só mudando as épocas — e com 20 exemplos de teste, essa diferença é ruído,
   não sinal. Anunciar "melhorei o modelo de 0,64 para 0,80" ali seria desonesto.
3. **Acurácia e confiança são coisas separadas.** As duas últimas linhas empatam em acurácia,
   mas a confiança vai de ~50% para ~96%. Treinar mais deixou o modelo mais *convicto*, não
   mais *correto*. Isso importa muito quando existe um limiar de decisão.

---

## O que este modelo NÃO faz bem (limitações honestas)

- **Não sabe dizer "isso não é comigo".** Perguntado sobre "qual a receita de bolo de cenoura",
  ele responde `COMERCIAL` com 73% de confiança — acima do limiar de 60%. O *softmax* é
  confiante mesmo fora do domínio em que foi treinado; ele normaliza entre as 4 classes que
  conhece e nunca soma "nenhuma delas". Detectar entrada fora de distribuição exige mecanismo
  próprio: uma classe `OUTROS` no treino, um detector por distância no espaço de embeddings,
  ou calibração de temperatura. Ver [`../75-armadilhas.md`](../75-armadilhas.md).
- **Aprendeu atalhos do vocabulário.** "não consigo emitir nota fiscal, dá erro de certificado"
  é claramente `TECNICO`, mas o modelo diz `FINANCEIRO` com 95% — a expressão "nota fiscal"
  aparece quase sempre em chamados financeiros neste conjunto, e ele agarrou essa correlação.
  A correção é dados, não código: exemplos que quebrem o atalho.
- **180 exemplos sintéticos não são um conjunto de dados de verdade.** Foram escritos para
  serem separáveis. Chamados reais vêm com erro de digitação, gíria, print colado, assinatura
  de e-mail e mais de um assunto na mesma mensagem.
- **Não há monitoramento nem *drift*.** Em produção, a distribuição dos chamados muda
  (lançamento de produto, mudança de política) e o modelo se degrada em silêncio.
  Ver [`../19-producao-e-otimizacao.md`](../19-producao-e-otimizacao.md).
- **Não há autenticação na API.** É um exemplo didático, não um serviço público.

---

## Exercícios para estender

Em ordem crescente de dificuldade:

1. Acrescente uma categoria `ELOGIO` com 45 exemplos e retreine. O que acontece com as outras?
2. Troque `MODELO_BASE` por `distilbert-base-multilingual-cased` e compare F1 × tempo de treino.
3. Adicione ao CSV cinco chamados ambíguos entre `FINANCEIRO` e `CANCELAMENTO`. A matriz de confusão piora onde você espera?
4. Crie uma classe `OUTROS` com textos fora do domínio e veja o efeito na "receita de bolo de cenoura".
5. Exporte o modelo para ONNX (`optimum-cli export onnx`) e meça o ganho de latência em CPU — ver [`../19-producao-e-otimizacao.md`](../19-producao-e-otimizacao.md).
6. Substitua o classificador por busca por similaridade com `sentence-transformers` (sem treinar nada) e compare — ver [`../16-embeddings-e-busca-semantica.md`](../16-embeddings-e-busca-semantica.md).
7. Implemente validação cruzada de 5 folds em vez da divisão única e reporte média ± desvio. Com dados assim pequenos, é o certo a fazer.

---

## Limpeza

O treino deixa ~1,7 GB em disco:

```bash
rm -rf checkpoints/          # ~1,3 GB, só serve durante o treino
rm -rf modelo-treinado/      # ~417 MB, o modelo final — apague só se não for usar
hf cache scan                # o modelo base baixado fica em ~/.cache/huggingface
```

---

## Autoteste

1. Por que três conjuntos (treino/validação/teste), e o que acontece se você reportar o número da validação?
2. O que é vazamento de dados neste projeto, e qual teste o impede?
3. Por que `f1_macro` e não acurácia como `metric_for_best_model`?
4. O que quebra se você esquecer `model.eval()` na inferência?
5. Olhando a matriz de confusão, qual classe é a mais difícil e por quê?
6. Qual mudança teve o maior efeito no resultado: hiperparâmetros ou quantidade de dados?
7. Por que o modelo responde com 73% de confiança a uma pergunta sobre bolo de cenoura, e como se resolve isso?
8. Por que `modelo-treinado/` está no `.gitignore`?

---

*Volta para: [`../00-MAPA.md`](../00-MAPA.md) · Aprofunde em [`../15-fine-tuning.md`](../15-fine-tuning.md)*
