# 19 · Produção — servir rápido, barato e sem sustos

`Nível: avançado` · `Última atualização: 12/08/2026`

Do modelo treinado ao serviço que aguenta carga. É onde a maior parte dos projetos de PLN
morre — não por qualidade do modelo, mas por engenharia.

---

## 1 · As quatro alavancas de desempenho

Em ordem de retorno por hora de trabalho:

| # | Alavanca | Ganho típico | Custo de implementar |
|---|---|---|---|
| 1 | **Agrupar em lote** | 4× a 20× | 10 minutos |
| 2 | **Reduzir `max_length`** | até 4× | 5 minutos |
| 3 | **ONNX Runtime + quantização int8** | 2× a 4× | 1 a 3 horas |
| 4 | **Modelo menor (destilação)** | 2× a 6× | 1 dia (ou grátis, se já existir) |

As duas primeiras são quase gratuitas e quase sempre esquecidas. Ganho medido neste curso:
**4,3× só agrupando** ([06-exemplos.md, exemplo 10](06-exemplos.md#10--produção-1-classificar-500-mil-textos-sem-esperar-um-dia)).

**Antes de qualquer otimização, meça.** É comum descobrir que 70% da latência está no
pré-processamento em Python, ou numa consulta ao banco, e não no modelo.

---

## 2 · Quantização

Reduzir a precisão numérica dos pesos: menos memória, mais velocidade, um pouco de qualidade.

| Precisão | Bytes/peso | BERT-base | Perda típica | Onde roda |
|---|---|---|---|---|
| `float32` | 4 | 440 MB | — | tudo |
| `bfloat16` | 2 | 220 MB | ~0 | GPU Ampere+ |
| `float16` | 2 | 220 MB | ~0 | GPU |
| **`int8`** | 1 | **110 MB** | 0,5 a 2 pontos | **CPU e GPU** |
| `int4` | 0,5 | 55 MB | 2 a 5 pontos | raro em encoders |

**Quantização dinâmica** (a mais simples; pesos em int8, ativações calculadas na hora):

```python
import torch
from transformers import AutoModelForSequenceClassification

modelo = AutoModelForSequenceClassification.from_pretrained("./modelo-treinado").eval()
quantizado = torch.quantization.quantize_dynamic(modelo, {torch.nn.Linear}, dtype=torch.qint8)
torch.save(quantizado.state_dict(), "modelo_int8.pt")
```

Funciona bem em CPU, sem dado de calibração, em uma linha. Para GPU e para o melhor
resultado, o caminho é ONNX ou TensorRT.

**Sempre reavalie depois de quantizar.** A perda é pequena *em média* e pode ser grande numa
classe específica. Rode o mesmo conjunto de teste e compare a matriz de confusão, não só a
média.

---

## 3 · ONNX Runtime

ONNX é um formato intermediário; o ONNX Runtime executa com otimizações de grafo (fusão de
operações, eliminação de nós) e kernels especializados.

```bash
pip install "optimum[onnxruntime]"
optimum-cli export onnx --model ./modelo-treinado ./modelo-onnx/
```

```python
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer, pipeline

modelo = ORTModelForSequenceClassification.from_pretrained("./modelo-onnx")
tok = AutoTokenizer.from_pretrained("./modelo-onnx")
p = pipeline("text-classification", model=modelo, tokenizer=tok)
print(p("meu boleto não chegou"))
```

Quantizando o modelo ONNX para int8:

```bash
optimum-cli onnxruntime quantize --onnx_model ./modelo-onnx --avx512_vnni -o ./modelo-onnx-int8
```

Ganho típico em CPU: **2× a 4×** com ONNX, e mais com int8. Em CPUs Intel com AVX-512 VNNI o
ganho de int8 é maior. **Meça na sua máquina** — a variação entre CPUs é grande.

---

## 4 · Destilação: fabricar seu próprio modelo pequeno

Se DistilBERT genérico não existe para o seu caso, você pode destilar o **seu** modelo
afinado. É o caminho de melhor relação qualidade/latência quando você tem dados não rotulados
em abundância.

```
seu BERT afinado (professor)
        │  gera "rótulos moles" (distribuições) para muito texto NÃO rotulado
        ▼
modelo pequeno (aluno) aprende a imitar essas distribuições
```

```python
import torch, torch.nn.functional as F

def perda_destilacao(logits_aluno, logits_professor, y, T=2.0, alfa=0.5):
    """Combina imitar o professor (KL) com acertar o rótulo (entropia cruzada)."""
    suave = F.kl_div(
        F.log_softmax(logits_aluno / T, dim=-1),
        F.softmax(logits_professor / T, dim=-1),
        reduction="batchmean",
    ) * (T ** 2)                       # T² compensa o encolhimento do gradiente
    dura = F.cross_entropy(logits_aluno, y)
    return alfa * suave + (1 - alfa) * dura
```

**Por que a temperatura `T`?** Ela suaviza a distribuição do professor, revelando as
probabilidades pequenas das classes erradas — que é justamente onde está o "conhecimento
escuro" que ensina a estrutura do problema. Com `T=1`, a distribuição costuma ser tão
concentrada que quase não há sinal além do rótulo.

Resultado típico: aluno com 4 a 6 camadas, 2 a 3× mais rápido, perdendo 1 a 3 pontos de F1.
Quanto mais texto não rotulado você tiver para a destilação, menor a perda.

---

## 5 · Servir: da API ao contêiner

O código de referência está em [07-projeto-modelo/api.py](07-projeto-modelo/api.py). Os
princípios:

| Princípio | Por quê |
|---|---|
| **Carregar o modelo na subida**, não na requisição | evita 2 s de latência no primeiro pedido e faz erro de deploy aparecer no deploy |
| `model.eval()` + `torch.no_grad()` | correção e memória |
| **Um processo por CPU física**, threads do torch em 1 | `torch.set_num_threads(1)` + várias réplicas escala melhor que um processo com N threads |
| **Agrupamento dinâmico** (micro-batching) | acumular 10 ms de requisições e processar juntas multiplica a vazão |
| **Health check** que carrega o modelo | orquestrador não manda tráfego para réplica quebrada |
| **Timeout e limite de tamanho** | texto de 1 MB não pode derrubar o serviço |
| Fixar versão do modelo e do tokenizador | reprodutibilidade e rollback |

### Dockerfile enxuto

```dockerfile
FROM python:3.12-slim

WORKDIR /app
# Instalar o torch de CPU explicitamente evita baixar ~3 GB de CUDA sem uso
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# O modelo vai na imagem: build determinístico, sem download em runtime.
# (Alternativa: montar um volume ou baixar de um bucket na subida.)
COPY modelo-treinado/ ./modelo-treinado/
COPY *.py ./

ENV HF_HUB_OFFLINE=1 \
    TOKENIZERS_PARALLELISM=false \
    OMP_NUM_THREADS=1

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/saude')"
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

`HF_HUB_OFFLINE=1` é uma proteção importante: garante que o contêiner **nunca** tente baixar
nada em produção. Sem isso, uma falha de rede ou uma mudança no Hub derruba seu serviço numa
madrugada.

Curso completo de Docker nesta pasta: [`../docker/00-MAPA.md`](../docker/00-MAPA.md).

---

## 6 · Dimensionamento: quanta máquina eu preciso?

Ordens de grandeza para BERT-base, texto de ~128 tokens:

| Configuração | Vazão aproximada |
|---|---|
| CPU, 4 núcleos, `float32`, um a um | 30 a 80 textos/s |
| CPU, 4 núcleos, lote 32 | 150 a 400 textos/s |
| CPU, 4 núcleos, ONNX int8, lote 32 | 400 a 1.200 textos/s |
| GPU T4, lote 64 | 2.000 a 5.000 textos/s |
| GPU A100, lote 128 | 10.000+ textos/s |

Conta para planejar: **1 milhão de textos por dia** = ~12 por segundo em média, mas o pico
costuma ser 5 a 10× a média. Com 120 textos/s de pico, **uma CPU de 4 núcleos com ONNX
resolve**. É comum ver times provisionando GPU para cargas que rodariam folgadas numa
máquina de R$ 200/mês.

---

## 7 · Monitoramento

O modelo não avisa quando começa a errar. Instrumente:

| Sinal | Como medir | Alerta quando |
|---|---|---|
| Latência p50/p95/p99 | histograma por requisição | p99 sobe 2× |
| Vazão | requisições/s | — |
| **Distribuição das classes previstas** | contagem por classe, por dia | muda mais de X% |
| **Confiança média** | média das probabilidades máximas | cai de forma sustentada |
| **Taxa de "não sei"** | fração abaixo do limiar | sobe (sinal precoce de deriva) |
| Comprimento da entrada | percentis | muda de perfil |
| Erros 4xx/5xx | contagem | — |

**A deriva (*drift*) é o inimigo silencioso.** O modelo não quebra: ele degrada. Sinais de
que chegou a hora de retreinar: a distribuição das classes previstas muda sem motivo de
negócio, a confiança média cai, e a taxa de casos abaixo do limiar sobe.

O padrão de operação saudável: **amostre 1% do tráfego, mande para revisão humana, e use isso
como conjunto de avaliação contínuo**. É o único jeito de medir qualidade real em produção,
onde não existe gabarito. Esses mesmos exemplos revisados viram dados de retreino — o ciclo
se fecha sozinho.

---

## 8 · Checklist de produção

- [ ] Modelo e tokenizador versionados juntos, com revisão fixada
- [ ] Carregamento na subida do serviço, com health check que exercita o modelo
- [ ] `model.eval()` e `torch.no_grad()`
- [ ] Limite de tamanho de entrada e timeout
- [ ] Latência p95/p99 medida sob carga realista, não com uma requisição
- [ ] Agrupamento em lote onde o padrão de tráfego permite
- [ ] `HF_HUB_OFFLINE=1` (sem download em runtime)
- [ ] Limiar de confiança e rota para revisão humana
- [ ] Métricas de deriva instrumentadas
- [ ] Amostragem de tráfego para avaliação contínua
- [ ] Plano de rollback: como voltar ao modelo anterior em minutos
- [ ] Model card publicado ([18-avaliacao-e-benchmarks.md](18-avaliacao-e-benchmarks.md))
- [ ] Dados de entrada tratados conforme a LGPD (retenção, anonimização, base legal)

---

## Autoteste

1. Qual é a otimização de maior retorno por hora de trabalho, e quanto ela rendeu na medição deste curso?
2. Por que medir antes de otimizar? O que costuma aparecer na medição?
3. O que é quantização dinâmica e por que ela é a primeira a tentar em CPU?
4. Por que é obrigatório reavaliar o modelo depois de quantizar?
5. Por que a destilação usa temperatura, e o que acontece com `T=1`?
6. Por que carregar o modelo na subida do serviço, e não na primeira requisição?
7. Para que serve `HF_HUB_OFFLINE=1` num contêiner de produção?
8. Você precisa processar 1 milhão de textos por dia. Precisa de GPU?
9. Cite três sinais de deriva que você pode monitorar sem ter o gabarito.
10. Como medir qualidade em produção, onde não existe rótulo verdadeiro?

---

## Fontes

- [Optimum — ONNX Runtime](https://huggingface.co/docs/optimum/onnxruntime/overview)
- [PyTorch — Quantization](https://pytorch.org/docs/stable/quantization.html)
- Hinton, Vinyals & Dean (2015). *Distilling the Knowledge in a Neural Network*. [arXiv:1503.02531](https://arxiv.org/abs/1503.02531)
- Sanh et al. (2019). *DistilBERT*. [arXiv:1910.01108](https://arxiv.org/abs/1910.01108)

---

*Anterior: [18-avaliacao-e-benchmarks.md](18-avaliacao-e-benchmarks.md) · Próximo: [20-interpretabilidade-e-bertologia.md](20-interpretabilidade-e-bertologia.md)*
