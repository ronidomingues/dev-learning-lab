# 80 · Custos e licenças

> **Nível:** todos · **Preços consultados em 31/08/2026.**
> **Preço sem data é desinformação.** Confira nas fontes do rodapé antes de usar estes
> números em uma decisão de compra.
> Câmbio de referência: **US$ 1 = R$ 5,1820**, cotação do dólar comercial consultada
> em 31/08/2026 às 17h27 (AwesomeAPI). Use-o só para ordem de grandeza.

---

## 1. A resposta curta

**O uv é inteiramente gratuito.** Sem plano pago, sem camada premium, sem cadastro, sem
cartão de crédito, sem limite de uso, sem telemetria obrigatória. Não existe versão
"Enterprise" nem funcionalidade retida atrás de licença.

**Quem paga a conta, então?**

- **De fev/2024 a mar/2026:** a **Astral**, empresa com capital de risco, bancava o
  desenvolvimento. A estratégia declarada era manter as ferramentas gratuitas e vender
  produtos que se integrassem verticalmente a elas — o que originou o `pyx`, um registro
  de pacotes comercial, lançado em beta em agosto de 2025.
- **Desde 19/03/2026:** a **OpenAI**, que adquiriu a Astral e integrou a equipe ao time do
  Codex. O `pyx` foi descontinuado e sua infraestrutura de índice para GPU foi aberta.
  Não há hoje nenhum produto pago associado ao uv.

**A leitura honesta:** o uv é financiado como **investimento estratégico em ferramental de
desenvolvimento**, não como produto. Isso significa que o financiamento é sólido enquanto
a estratégia se mantiver, e é exatamente essa dependência que constitui o risco discutido
em [65-estado-da-arte](65-estado-da-arte.md#2-o-evento-de-2026-a-aquisição-pela-openai).

---

## 2. Licença

| Item | Licença |
|---|---|
| **uv** | **MIT** *ou* **Apache-2.0**, à sua escolha (licenciamento duplo) |
| `python-build-standalone` (os Pythons) | Python Software Foundation License (o CPython) + licenças dos componentes estáticos (OpenSSL, SQLite, etc.) |
| Imagens Docker oficiais | mesma licença do uv + licenças da imagem base (Debian/Alpine) |
| `uv_build` (build backend) | mesma do uv |
| Ruff e `ty` (usados por `uv format`/`uv check`) | MIT |

### O que MIT/Apache-2.0 permite

| Você pode | Sem obrigação de |
|---|---|
| usar comercialmente, sem limite | pagar |
| distribuir junto com o seu produto | abrir o seu código |
| modificar e criar um fork | publicar as modificações |
| embutir num produto fechado | pedir permissão |
| usar em qualquer número de máquinas | contar assentos |

**Obrigações reais** (mínimas): preservar o aviso de copyright e o texto da licença ao
**redistribuir** o uv. Se você só o usa para construir seu software, não há obrigação
nenhuma.

### Por que licença dupla MIT **ou** Apache-2.0?

É a convenção do ecossistema Rust. A MIT é a mais permissiva e a mais compreendida
juridicamente; a Apache-2.0 acrescenta uma **concessão explícita de patentes** e uma
cláusula de retaliação, que muitos departamentos jurídicos corporativos exigem. Ao
oferecer as duas, o projeto atende tanto quem quer simplicidade quanto quem precisa da
proteção de patente. **Você escolhe qual seguir; não precisa cumprir as duas.**

### Compatibilidade com GPL

Tanto MIT quanto Apache-2.0 são compatíveis com a GPLv3. A Apache-2.0 **não** é compatível
com a GPLv2 (por causa da cláusula de patentes) — nesse caso específico, use a MIT. E, de
todo modo, isso raramente importa: você **usa** o uv para construir, não o **linka** ao
seu código.

---

## 3. Custos reais de usar o uv

### 3.1 Custo direto: zero

Não há nada a pagar pelo uv.

### 3.2 Custos indiretos honestos

| Item | Custo | Comentário |
|---|---|---|
| **Espaço em disco — cache** | 200 MB a 5 GB | nesta máquina, **217 MB** após um dia de testes (`uv cache size`). Cresce; `uv cache prune` controla |
| **Espaço — Pythons gerenciados** | ~100–150 MB por versão instalada | quatro versões ≈ 500 MB |
| **Espaço — ferramentas** | ~10–100 MB por ferramenta | ambiente isolado por ferramenta |
| **Banda na primeira instalação** | 35 MB (Python) + os pacotes | depois, o cache resolve |
| **Tempo de aprendizado** | 1 a 5 semanas até fluência | ver [02-pre-requisitos](02-pre-requisitos.md#3-tempo-realista-de-estudo) |
| **Tempo de migração** | 1 h (projeto simples) a 1 semana (monorepo grande) | ver [20-migracao](20-migracao-de-pip-poetry-conda.md) |
| **Risco de fornecedor** | difícil de precificar | mitigado pela licença permissiva e pelo `pyproject.toml` padrão |

### 3.3 A economia que ele gera

Este é o lado que costuma justificar a migração numa conversa com gestão.

Suponha uma equipe de **10 pessoas**, cada uma esperando por instalação de dependências
**8 vezes ao dia**. Com `pip`, cada espera é ~25 s; com `uv`, ~3 s.

```
Economia por pessoa/dia:  8 × 22 s ≈ 3 min
Equipe de 10, 220 dias úteis: 10 × 3 × 220 ≈ 6.600 min ≈ 110 h/ano
```

E em CI, onde o efeito é direto e faturado:

Suponha **80 execuções de CI por dia**, cada uma economizando 40 s de instalação, em
runners Linux 2-core do GitHub Actions a **US$ 0,006/min** (preço de 31/08/2026, após a
redução anunciada para 2026):

```
80 × 40 s = 3.200 s/dia ≈ 53 min/dia
53 × 22 dias = ~1.170 min/mês
1.170 × US$ 0,006 ≈ US$ 7/mês ≈ R$ 36/mês
```

> **Sendo honesto com os números:** US$ 7/mês não paga o café. **O ganho financeiro
> direto em CI é pequeno na maioria das equipes.** O ganho real é de **tempo humano e de
> latência de feedback** — 110 h/ano de espera eliminada, e ciclos de PR mais curtos.
> Desconfie de qualquer cálculo de ROI que dependa só da conta do CI; e, num monorepo com
> centenas de execuções por dia e runners maiores, a conta muda de ordem de grandeza.

---

## 4. Custos do ecossistema ao redor

Aqui está o que **de fato** custa dinheiro num projeto Python.

| Serviço | Camada gratuita | Onde ela acaba | Preço pago (31/08/2026) |
|---|---|---|---|
| **PyPI** (publicar/instalar) | ✅ totalmente gratuito | limite de ~100 MB por arquivo (exceções mediante pedido); sem limite de projetos | — |
| **TestPyPI** | ✅ gratuito | — | — |
| **GitHub Actions** (repo público) | ✅ ilimitado | — | — |
| **GitHub Actions** (repo privado) | 2.000 min Linux/mês + 500 MB de artefatos | ao passar disso | **US$ 0,006/min** Linux 2-core; US$ 0,010 Windows; US$ 0,062 macOS |
| **GitHub Codespaces** (pessoal) | 120 core-hours/mês + 15 GB-mês | ~60 h numa máquina de 2 núcleos | por hora, conforme o tamanho |
| **Docker Hub** | gratuito com limites de *pull* | limites de taxa para anônimos | planos por assento |
| **ghcr.io** (imagens do uv) | gratuito para públicas | — | — |
| **Artifactory / Nexus / Cloudsmith** (índice privado) | Nexus OSS e devpi são gratuitos | recursos avançados | milhares de dólares/ano nas versões comerciais |
| **Anaconda** (canais `defaults`) | ⚠️ **licença paga obrigatória** para organizações com 200+ funcionários/contratados | — | Starter ~US$ 15/usuário/mês; Business ~US$ 50/mês por assento; ambos até 15 assentos, acima disso é negociado |
| **conda-forge** | ✅ gratuito, sempre | — | — |

> ⚠️ **A pegadinha mais cara do mundo Python, e ela não é do uv:** os **canais `defaults`
> da Anaconda** exigem licença comercial para organizações grandes. Muita empresa
> descobriu isso ao receber uma cobrança retroativa. Se você usa conda, **use
> `conda-forge`**, que é livre. Isso é, aliás, um argumento financeiro real a favor de
> migrar para uv onde for possível — ver [20-migracao](20-migracao-de-pip-poetry-conda.md#6-de-conda--o-caso-difícil-e-honesto).

---

## 5. Custos ocultos e aprisionamento

### 5.1 O que **não** aprisiona você

| | Por quê |
|---|---|
| `pyproject.toml` | é **PEP 621 padrão** — pip, Poetry 2, Hatch e PDM leem |
| Wheels e sdists produzidos | formato padrão; indistinguíveis dos de qualquer outro backend |
| Pacotes instalados | são os mesmos do PyPI |
| Ambientes virtuais | `.venv` comum, PEP 405 |
| `uv.lock` | ❗ formato próprio — **mas** exportável com um comando |

### 5.2 Onde há acoplamento real

| Acoplamento | Gravidade | Saída |
|---|---|---|
| `uv.lock` | baixa | `uv export --format pylock.toml` ou `requirements.txt` |
| `[tool.uv]` no `pyproject.toml` | baixa | outras ferramentas simplesmente ignoram a seção |
| `uv_build` como build backend | **média** | trocar por `hatchling` custa 3 linhas |
| Workspaces | média | vira projetos separados com `path` sources |
| `[tool.uv.sources]` | média | vira instalação manual ou índice configurado por fora |
| Scripts de CI que chamam `uv` | baixa | tradução direta ([20-migracao](20-migracao-de-pip-poetry-conda.md#7-tabela-de-tradução-de-comandos)) |

**Custo estimado para sair do uv em um projeto médio: algumas horas.** É o argumento mais
forte a favor de entrar.

### 5.3 O custo que ninguém contabiliza

**Divergência dentro da equipe.** Metade usando Poetry e metade usando uv, no mesmo
repositório, com dois lockfiles que discordam, é pior que qualquer uma das duas
ferramentas sozinha. **Migre a equipe inteira, ou não migre.**

---

## 6. Alternativas gratuitas equivalentes

Todas as alternativas relevantes também são gratuitas — este não é um mercado onde se
paga por ferramenta:

| Ferramenta | Licença | O que se perde ao trocar o uv por ela |
|---|---|---|
| **pip + venv** | MIT | velocidade, lock universal, gerenciamento de Python, workspaces |
| **pip-tools** | BSD-3 | modo projeto, gerenciamento de Python, workspaces |
| **Poetry** | MIT | velocidade (~10×), gerenciamento de Python, `uvx` |
| **PDM** | MIT | velocidade, maturidade de ecossistema |
| **Hatch** | MIT | velocidade, lock universal |
| **conda/mamba** | BSD-3 (o software) | velocidade e o ecossistema PyPI completo — **ganha** bibliotecas não-Python |
| **Pixi** | BSD-3 | ecossistema PyPI — **ganha** conda-forge com ergonomia moderna |
| **Nix** | LGPL-2.1 | simplicidade — **ganha** reprodutibilidade de sistema inteiro |

---

## 7. Recomendação por perfil

| Perfil | Recomendação | Custo |
|---|---|---|
| Estudante / aprendendo Python | **uv**, desde o primeiro dia | R$ 0 |
| Freelancer / projetos pequenos | **uv** | R$ 0 |
| Startup, equipe de 5–50 | **uv**, com CI e lock versionado | R$ 0 + ~1 semana de migração |
| Empresa grande, com índice privado | **uv** + Artifactory/Nexus, com `explicit = true` | custo do índice, que você já tem |
| Ciência de dados com binários pesados | **conda-forge** (não `defaults`) + uv para pacotes Python | R$ 0 se evitar os canais da Anaconda |
| Setor regulado (auditoria, SBOM) | **uv** + `uv export --format cyclonedx1.5` + `exclude-newer` | R$ 0 |
| Ambiente sem rede | **uv** + espelho interno ou wheels pré-baixados | custo do espelho |

---

## Autoteste

1. Quanto custa o uv? Quem financia, e o que mudou em 19/03/2026?
2. Por que licenciamento duplo MIT **ou** Apache-2.0? O que a segunda acrescenta?
3. Você precisa abrir seu código por usar uv? E se distribuir o binário do uv junto?
4. Faça a conta de economia de CI para 80 execuções/dia — e diga por que ela **não** é o
   melhor argumento de migração.
5. Qual é a maior pegadinha de custo do ecossistema Python, e ela é do uv?
6. Qual é o único acoplamento real do uv, e como sair dele?
7. Qual é o "custo que ninguém contabiliza" numa migração?
8. Quanto ocupa o cache do uv, e como você mede e controla isso?
9. Numa empresa de 500 pessoas usando conda, o que você verificaria imediatamente?
10. Para um setor regulado que exige SBOM, o uv gera custo adicional? Qual comando atende?

---

**Fontes (todas consultadas em 31/08/2026):**
licença em [github.com/astral-sh/uv](https://github.com/astral-sh/uv) (LICENSE-MIT e
LICENSE-APACHE) ·
[openai.com/index/openai-to-acquire-astral](https://openai.com/index/openai-to-acquire-astral/) ·
[pydevtools.com — encerramento do pyx](https://pydevtools.com/blog/astral-winds-down-pyx-open-sources-gpu-packaging/) ·
[github.com/resources/insights/2026-pricing-changes-for-github-actions](https://github.com/resources/insights/2026-pricing-changes-for-github-actions) ·
[github.blog — mudança de preços do Actions (16/12/2025)](https://github.blog/changelog/2025-12-16-coming-soon-simpler-pricing-and-a-better-experience-for-github-actions/) ·
[anaconda.com/pricing](https://www.anaconda.com/pricing) e
[anaconda.com/pricing/business](https://www.anaconda.com/pricing/business) ·
[docs.github.com — Codespaces billing](https://docs.github.com/en/billing/managing-billing-for-github-codespaces/about-billing-for-github-codespaces) ·
`uv cache size` executado localmente.
Os valores de GitHub Actions e Anaconda vêm de páginas de preço e de análises de
terceiros; **confirme no site oficial antes de decidir uma compra.**

**Próximo:** [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md)
