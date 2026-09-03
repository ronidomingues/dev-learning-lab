# `triador` — projeto-modelo de engenharia de prompt

**Nível:** iniciante → intermediário · **Testado em:** Python 3.10.12, 19/08/2026

Um sistema de triagem de chamados de suporte. Pequeno, mas **inteiro**: prompt
versionado, extração e validação de saída, laço de correção, conjunto rotulado,
arnês de avaliação com portão de CI, estimativa de custo e 23 testes.

É deliberadamente o projeto mais chato possível. Classificar chamado não é
glamouroso — mas é exatamente o formato de 80% do trabalho remunerado de
engenharia de prompt, e exercita tudo que importa.

---

## O que ele ensina

| Decisão de projeto | O que ela ensina |
|---|---|
| Prompt em **arquivo separado e versionado** (`prompts/v*.md`) | prompt é artefato de código, não string enterrada no meio da função |
| **Três versões** do mesmo prompt | melhoria de prompt é medida, não sentida |
| `extrair_json` tolerante + `validar` estrito | o modelo é entrada não confiável; o contrato é seu, não dele |
| Laço de **correção com o erro literal** do validador | a recuperação mais barata que existe |
| `dados/casos.jsonl` com rótulos | sem conjunto rotulado você não tem engenharia, tem opinião |
| `avaliar.py --limite` com código de saída | regressão de prompt tem que quebrar o build |
| Provedor **simulado** e provedor **real** com a mesma interface | testar sem gastar, e trocar de fornecedor sem reescrever |
| Custo estimado por mil chamados | prompt bom que custa 3× pode ser prompt ruim |

---

## Pré-requisitos

- Python **3.10 ou superior** (`python3 --version`).
- Nada mais para o caminho padrão.
- Para rodar contra a API real: `pip install anthropic` e uma chave em
  `ANTHROPIC_API_KEY` (veja [`.env.example`](.env.example)).

---

## Como rodar

```bash
cd 07-projeto-modelo
```

**1. Classificar um chamado:**

```bash
python3 triador.py --chamado "Fui cobrado duas vezes na fatura de agosto"
```

Saída esperada:

```json
{"categoria": "cobranca", "urgencia": "normal", "resumo": "Fui cobrado duas vezes na fatura de agosto"}
```

**2. Ver o prompt ruim falhando (o ponto do exercício):**

```bash
python3 triador.py --prompt prompts/v1_ingenuo.md --bruto \
  --chamado "Fui cobrado duas vezes na fatura de agosto"
echo "código de saída: $?"
```

Saída esperada: a resposta crua com cerca de markdown e frase de cortesia, e
no stderr `saída inválida após 2 tentativa(s): categoria fora do conjunto:
'tecnico'`, com **código de saída 1**.

**3. Avaliar e comparar as três versões:**

```bash
python3 avaliar.py --erros
```

Saída real da execução de 19/08/2026:

```
conjunto: dados/casos.jsonl (22 casos) · provedor: simulado

prompt                    válido  fmt.limpo  categoria  urgência   ambos    US$/1k
----------------------------------------------------------------------------------
v1_ingenuo.md                0%         0%         0%        0%      0%     1.240
v2_estruturado.md          100%       100%        86%       95%     82%     2.325
v3_fewshot.md              100%       100%        95%       95%     91%     3.140

melhor: v3_fewshot.md — 91% de acerto completo
```

Leia a tabela da direita para a esquerda: a v3 acerta mais **e custa 2,5×** a
v1 por chamado, porque exemplos ocupam tokens de entrada em toda requisição.
Essa é a conversa que engenheiro de prompt tem com o financeiro.

**4. Portão de CI:**

```bash
python3 avaliar.py --prompt prompts/v3_fewshot.md --limite 0.9
echo "código de saída: $?"   # 0 = passou
```

**5. Testes:**

```bash
python3 -m unittest -v
# esperado: Ran 23 tests ... OK
```

**6. Contra a API real (opcional, custa dinheiro):**

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python3 avaliar.py --provedor anthropic --prompt prompts/v3_fewshot.md
```

22 casos × ~700 tokens de entrada ≈ 15 mil tokens de entrada por rodada.
A US$ 5,00 por milhão (Claude Opus 5, preço de 19/08/2026), isso dá
**menos de US$ 0,10 por rodada completa**.

---

## Estrutura

```
07-projeto-modelo/
├── README.md              este arquivo
├── provedor.py            SimulatedProvider (offline) e AnthropicProvider (real)
├── triador.py             extração, validação, laço de correção, CLI
├── avaliar.py             arnês de avaliação, tabela comparativa, portão de CI
├── test_triador.py        23 testes, nenhum precisa de rede
├── prompts/
│   ├── v1_ingenuo.md      o prompt que todo mundo escreve primeiro
│   ├── v2_estruturado.md  papel + conjunto fechado + regras + formato
│   └── v3_fewshot.md      v2 + 4 exemplos que cobrem os casos de fronteira
├── dados/
│   └── casos.jsonl        22 chamados rotulados à mão
├── requirements.txt       só para o provedor real
└── .env.example           modelo de configuração
```

---

## Honestidade sobre o provedor simulado

**`SimulatedProvider` não é um modelo de linguagem.** É uma caricatura
determinística de 60 linhas que reage a *características* do prompt:

- se o prompt não proíbe texto ao redor, ele embrulha em ```` ```json ```` e
  puxa conversa;
- se o prompt não enumera as categorias, ele inventa rótulo plausível
  (`financeiro` em vez de `cobranca`);
- se o prompt não tem exemplos, ele deixa a palavra "erro" dominar o sentido da
  frase e chama de `bug` um chamado de cobrança.

Os três comportamentos são falhas reais e frequentes de modelos pequenos, e é
por isso que a caricatura ensina. Mas **a tabela acima mede o arnês, não a
qualidade do prompt**. Para medir prompt de verdade é preciso rodar
`--provedor anthropic` — que é justamente o exercício 6.

Dois erros sobrevivem à v3, e isso é proposital:

- **c14** ("Ninguém da equipe consegue entrar no painel desde ontem") — deveria
  ser urgência alta por afetar vários usuários, e nenhuma versão acerta. Erro
  de *regra*: a definição de "alta" no prompt não cobre esse caso.
- **c22** ("Urgente: o certificado SSL expirou") — cai em `duvida`. Erro de
  *cobertura*: não há exemplo de incidente de infraestrutura.

Nenhum dos dois se resolve escrevendo o prompt "com mais capricho". Um pede
regra nova, o outro pede exemplo novo. Saber distinguir os dois casos é metade
do ofício.

---

## Exercícios

1. Corrija o **c14** mexendo só na regra 3 da v2 e da v3. Rode `avaliar.py` e
   confirme que a urgência sobe para 100% **sem derrubar** as outras métricas.
2. Adicione um quinto exemplo à v3 que resolva o **c22**. Meça antes e depois.
3. Crie a `v4` removendo os exemplos e colocando as mesmas lições como regras
   em texto. Ela fica mais barata? Fica pior? Meça — não chute.
4. Acrescente ao conjunto 5 chamados escritos por você, incluindo um ambíguo de
   propósito. Se você mesmo não sabe rotulá-lo, o modelo também não saberá:
   o problema é da taxonomia, não do prompt.
5. Faça `avaliar.py` medir também **consistência**: rode o mesmo caso 3 vezes e
   conte quantas vezes a resposta muda. Com o simulado dá 0% de variação (é
   determinístico); com a API real, não.
