# 80 · Custos e licenças

`Nível: intermediário` · `Preços consultados em 13/08/2026` · `Câmbio de referência: US$ 1 ≈ R$ 5,40`

> **Preço sem data é desinformação.** Tudo aqui tem data de consulta. Confirme antes de
> decidir: preços de nuvem e de SaaS mudam várias vezes por ano, e a política de camada
> gratuita do GitHub Actions mudou em janeiro de 2026.
>
> **O câmbio é uma referência de ordem de grandeza**, não uma cotação. Converta você mesmo
> na hora de fazer conta séria.

---

## 1. A resposta curta: as ferramentas são gratuitas

**Todas as ferramentas centrais deste curso são de código aberto e gratuitas, para uso
comercial inclusive.**

| Ferramenta | Licença | Custo |
|---|---|---|
| **pytest** | MIT | R$ 0 |
| **pytest-cov**, `coverage.py` | MIT / Apache 2.0 | R$ 0 |
| **Hypothesis** | MPL 2.0 | R$ 0 |
| **`unittest`, `doctest`** | PSF (Python) | R$ 0 |
| **`node:test`** | MIT (Node.js) | R$ 0 |
| **Vitest** | MIT | R$ 0 |
| **Jest** | MIT | R$ 0 |
| **Playwright** | Apache 2.0 | R$ 0 |
| **Selenium / WebDriver** | Apache 2.0 | R$ 0 |
| **Cypress** (código aberto) | MIT | R$ 0 (o **Cloud** é pago) |
| **Testing Library** | MIT | R$ 0 |
| **Testcontainers** | MIT | R$ 0 |
| **Stryker**, **mutmut**, **Cosmic Ray** | Apache 2.0 / MIT | R$ 0 |
| **`tox`, `nox`, `uv`** | MIT / Apache 2.0 | R$ 0 |

**Onde o dinheiro aparece:** não é na ferramenta. É em **tempo de computação** (minutos de
CI), **infraestrutura de navegadores** e **tempo de pessoas**. O terceiro é, de longe, o
maior.

---

## 2. Quem paga a conta das ferramentas gratuitas

Vale entender, porque isso governa a sustentabilidade delas.

| Ferramenta | Quem financia | Risco associado |
|---|---|---|
| **pytest** | doações, Tidelift, patrocínio corporativo, trabalho voluntário | baixo — governança distribuída, mantenedores múltiplos |
| **Node.js / `node:test`** | OpenJS Foundation, patrocínio de empresas | muito baixo |
| **Vitest** | VoidZero (empresa criada em torno do Vite, com capital de risco) | **médio** — modelo de negócio ainda em construção |
| **Jest** | Meta cedeu a governança à OpenJS Foundation em 2022 | baixo |
| **Playwright** | Microsoft, com equipe dedicada | baixo, mas é um único patrocinador |
| **Hypothesis** | doações, consultoria do autor principal | médio — dependência de poucas pessoas |

**Leitura honesta:** "gratuito" não significa "sem risco". Uma ferramenta mantida por uma
empresa pode mudar de licença ou ser abandonada (aconteceu com muitos projetos entre 2018 e
2024). Ferramentas de fundação, com governança distribuída, são mais previsíveis.

**Mitigação prática:** prefira as que têm padrão aberto ou substituto fácil. Trocar de
corredor de testes custa dias; trocar de plataforma de nuvem de testes custa meses.

---

## 3. Licenças: o que cada uma permite

| Licença | Uso comercial | Modificar | Distribuir fechado | Obrigação principal |
|---|---|---|---|---|
| **MIT** | ✅ | ✅ | ✅ | manter o aviso de copyright |
| **Apache 2.0** | ✅ | ✅ | ✅ | aviso + declarar mudanças + concessão de patentes |
| **BSD-3** | ✅ | ✅ | ✅ | aviso, e não usar o nome para endosso |
| **MPL 2.0** | ✅ | ✅ | ✅ | **arquivos modificados** da própria lib voltam abertos |
| **PSF** | ✅ | ✅ | ✅ | aviso |
| **GPL/AGPL** | ✅ | ✅ | ❌ | derivado inteiro precisa ser aberto |

**Nenhuma ferramenta central deste curso é GPL ou AGPL.** Você pode usá-las num produto
proprietário sem obrigação de abrir código.

**Sobre a MPL 2.0 da Hypothesis:** ela é *copyleft de arquivo*. Usar a biblioteca não
contamina nada. Se você **modificar arquivos dela** e distribuir, esses arquivos precisam
continuar sob MPL. Para uso normal (importar e usar), não há obrigação nenhuma.

**Atenção ao ecossistema, não só ao núcleo:** um plugin de pytest ou um pacote npm pode ter
licença diferente. Se a sua empresa audita licenças, rode a verificação:

```bash
pip install pip-licenses && pip-licenses --format=markdown
npx license-checker --summary
```

---

## 4. O custo real nº 1: minutos de CI

### 4.1 GitHub Actions — preços de 13/08/2026

**Repositório público: gratuito e ilimitado.** Esse é o motivo de tanto projeto aberto ter CI
generoso.

**Repositório privado:**

| Plano | Minutos Linux incluídos/mês | Armazenamento |
|---|---|---|
| Free | 2.000 | 500 MB |
| Team (US$ 4/usuário/mês ≈ R$ 22) | 3.000 | 2 GB |
| Enterprise (US$ 21/usuário/mês ≈ R$ 113) | 50.000 | 50 GB |

**Acima do incluído, por minuto** (executores hospedados padrão de 2 núcleos):

| Executor | US$/min | ≈ R$/min | Multiplicador sobre a cota |
|---|---|---|---|
| Linux x86 | 0,006 | 0,032 | **1×** |
| Linux ARM | 0,005 | 0,027 | 1× |
| Windows | 0,010 | 0,054 | **2×** |
| macOS (3–4 núcleos) | 0,062 | 0,335 | **10×** |

**A armadilha do multiplicador:** os minutos **incluídos** são consumidos com multiplicador.
Um minuto de macOS gasta **dez** minutos da sua cota. Uma matriz de 3 versões × 3 SOs numa
suíte de 5 minutos consome, por execução:

```
Linux   3 × 5 ×  1 =  15 min de cota
Windows 3 × 5 ×  2 =  30 min de cota
macOS   3 × 5 × 10 = 150 min de cota
                    ─────────────────
                     195 min por execução
```

Com o plano Free (2.000 min), isso dá **10 execuções por mês**. Dez.

### 4.2 Conta realista de um time

Cenário: 5 pessoas, ~8 PRs/dia, suíte de 6 minutos em Linux, repositório privado.

```
8 PRs/dia × 22 dias      = 176 execuções/mês
× 6 min                  = 1.056 min
+ merges no main (~44)   ≈ 264 min
                          ─────────────
                            1.320 min/mês
```

Cabe no plano Free. **Com `cancel-in-progress`.** Sem ele, cada push em PR aberto gera uma
execução completa, e três pushes por PR triplicam o número.

Se a suíte for de 20 minutos em vez de 6, o mesmo cenário dá ~4.400 min/mês: fora do Free,
fora do Team, e um custo de aproximadamente **US$ 8/mês** (≈ R$ 44) no excedente. Note que o
custo em dinheiro continua irrisório — **o custo caro é a espera das pessoas.**

### 4.3 Comparativo de plataformas

| Plataforma | Camada gratuita | Observação |
|---|---|---|
| **GitHub Actions** | ilimitado em público; 2.000 min/mês em privado | multiplicadores por SO |
| **GitLab CI** | minutos de *compute* mensais no plano Free | cota menor; SaaS ou runner próprio |
| **CircleCI** | créditos mensais no plano Free | modelo de crédito por tamanho de máquina |
| **Runner próprio** | só o custo da máquina | uso do executor auto-hospedado no GitHub segue **gratuito**; uma cobrança por minuto anunciada para 2026 foi **revertida** após reação da comunidade |

**Runner próprio vale a pena quando?** Como regra grosseira, acima de ~20.000 minutos/mês
uma VM dedicada tende a sair mais barata. Mas some o custo de **manter** o runner (segurança,
atualização, isolamento entre jobs) — que é trabalho de pessoa, e pessoa é o item caro.

### 4.4 As três formas de reduzir minutos, por eficácia

1. **`concurrency` com `cancel-in-progress`** — elimina execuções que ninguém vai ler;
2. **separar rápido de lento**, com o lento só no merge para o `main`;
3. **cache de dependências** e imagens *slim*/*alpine*.

E a mais eficaz de todas, que não é de CI: **deixar a suíte rápida.**

---

## 5. Nuvem de navegadores

Só necessária para testar em navegadores/dispositivos que você não tem. Preços de tabela em
**13/08/2026**, para o produto de automação, plano de entrada:

| Serviço | A partir de | ≈ R$/mês | Observação |
|---|---|---|---|
| **BrowserStack Automate** (desktop) | US$ 129/mês | ~700 | desktop + mobile a partir de US$ 199 |
| **Sauce Labs Automate** (desktop) | US$ 129/mês | ~700 | usuários e minutos ilimitados, **1 sessão paralela**; paralelismo extra é cobrado |
| **LambdaTest / TestMu AI** | US$ 15/mês (plano básico) · Automate Pro a partir de US$ 129 | ~80 / ~700 | rebatizado em janeiro de 2026 |

**A variável que define o preço é o paralelismo**, não o volume de testes. Um plano de 1
sessão paralela com uma suíte de 200 testes de 20 s leva mais de 1 hora por execução. É por
isso que planos corporativos com dezenas de sessões chegam à casa das dezenas de milhares de
dólares por ano.

**A alternativa gratuita:** Playwright rodando **no seu próprio CI**, em *headless*, cobre
Chromium, Firefox e WebKit em Linux — que é a maior parte da matriz real. Você paga só os
minutos de CI.

**O que se perde:** navegadores em Windows e macOS reais, versões antigas específicas,
dispositivos móveis físicos, e testes em Safari real (o WebKit do Playwright é próximo, mas
não é o Safari). Se o seu produto depende disso, a nuvem se paga. Se não depende, é gasto
puro.

---

## 6. Painéis de cobertura

| Serviço | Gratuito | Pago |
|---|---|---|
| **Codecov** | repositório público | por usuário/mês em privado |
| **Coveralls** | repositório público | idem |
| **SonarQube Community** | auto-hospedado, gratuito | SonarQube Cloud tem planos pagos |

**Alternativa de custo zero:** `pytest --cov --cov-report=html` ou
`vitest run --coverage` gerando artefato no CI, e `diff-cover` como portão. Cobre 90 % da
necessidade real sem nenhum serviço externo.

---

## 7. O custo que ninguém coloca na planilha: pessoas

Estimativas de ordem de grandeza (**não são medições**; são referências para você calibrar
com seus próprios números):

| Item | Ordem de grandeza |
|---|---|
| escrever testes junto com o código | +20 % a +40 % do tempo de implementação |
| manter a suíte | 5 % a 15 % do tempo do time, continuamente |
| depurar teste instável | **horas** por ocorrência, e recorrente |
| espera pelo CI | tempo da suíte × número de execuções × pessoas envolvidas |
| aprender a testar bem | dezenas a centenas de horas por pessoa |

O item mais caro é o **terceiro**. Um teste instável não custa o tempo de consertá-lo; custa
o tempo de todo mundo que reroda, investiga e desconfia da suíte, todas as vezes.

O segundo mais caro é o **quarto**, e ele é invisível. Uma suíte de 20 minutos, com 8
execuções por dia e 5 pessoas esperando, consome tempo comparável ao de escrever os testes —
todo mês.

**Contra o que isso deve ser comparado:** o custo de um incidente em produção. Uma cobrança
errada, um vazamento, uma indisponibilidade de 2 horas. Se o seu produto move dinheiro,
**um** incidente evitado costuma pagar anos de suíte.

**Onde testar não se paga:** protótipo descartável, script de uso único, prova de conceito
que vai ser jogada fora. Dizer isso em voz alta é honestidade profissional, não preguiça.

---

## 8. Custos ocultos

| Custo oculto | Como aparece |
|---|---|
| **erosão da suíte** | testes sem manutenção viram passivo; ninguém apaga |
| **aprisionamento em ferramenta de nuvem** | seletores e relatórios proprietários; migrar custa meses |
| **armazenamento de artefatos** | vídeo do Playwright a cada execução enche a cota rápido |
| **egresso de dados** | baixar artefato/imagem grande em CI de nuvem paga |
| **licença de IDE** | PyCharm Pro, WebStorm — as versões Community/gratuita cobrem tudo deste curso |
| **treinamento** | curso de teste é barato; **desaprender práticas ruins** é caro |
| **tempo de revisão de PR** | suíte lenta = PR parado = trabalho em progresso acumulado |

**O aprisionamento merece atenção:** ferramentas de teste "sem código" e plataformas com
gravador proprietário prendem você no formato delas. Testes escritos em Playwright ou pytest
são **código seu**, versionado no seu repositório, executável em qualquer lugar. Essa é uma
razão substantiva — e não ideológica — para preferir ferramentas de código aberto.

---

## 9. Recomendação de custo por tamanho de time

| Contexto | Recomendação | Custo mensal |
|---|---|---|
| **estudando sozinho** | tudo local + GitHub público | **R$ 0** |
| **projeto pessoal** | GitHub Actions público, Playwright local | **R$ 0** |
| **startup, 2–5 pessoas** | GitHub Free ou Team, suíte rápida, Playwright no CI | R$ 0 a ~R$ 110 |
| **time de 10–30** | Team/Enterprise, runners próprios se a suíte for pesada | R$ 200 a R$ 3.000 |
| **produto com matriz de navegadores real** | + nuvem de navegadores | + R$ 700 a R$ 5.000 |
| **software regulado (saúde, aviônica, financeiro)** | + ferramentas de cobertura MC-DC e rastreabilidade | dezenas de milhares |

A última linha é outro mundo: normas como **DO-178C** (aviônica) e **IEC 62304** (dispositivo
médico) exigem rastreabilidade requisito→teste e critérios como MC-DC, e as ferramentas
certificadas para isso são caras justamente porque a certificação é cara.

---

## 10. Se você não pode gastar nada

Pilha 100 % gratuita, viável para uso profissional:

```
runtime          Python (PSF) · Node.js (MIT)
corredor         pytest (MIT) · node:test (MIT)
cobertura        coverage.py (Apache 2.0) · V8 embutido
propriedades     Hypothesis (MPL 2.0) · fast-check (MIT)
mutação          mutmut (MIT) · Stryker (Apache 2.0)
navegador        Playwright (Apache 2.0), headless, no próprio CI
banco            Testcontainers (MIT) + Postgres (PostgreSQL License)
CI               GitHub Actions (ilimitado em repo público)
painel           artefato HTML de cobertura no próprio CI
editor           VS Code / VSCodium · PyCharm Community
```

**Não falta nada de essencial nessa lista.** O que se paga em outras pilhas é conveniência,
suporte e infraestrutura que você não quer manter — não capacidade.

---

## Autoteste

1. Qual é a licença do pytest, do Playwright e da Hypothesis, e o que a MPL 2.0 exige?
2. Alguma ferramenta central deste curso impede uso em produto proprietário?
3. Quem financia o Vitest, e por que isso é um risco de médio prazo?
4. Quantos minutos de cota consome 1 minuto de execução em macOS no GitHub Actions?
5. Faça a conta: matriz 3 versões × 3 SOs, suíte de 5 min. Quantos minutos de cota por execução?
6. Qual é a variável que define o preço de uma nuvem de navegadores?
7. O que se perde ao trocar BrowserStack por Playwright headless no próprio CI?
8. Qual é o item de custo mais caro de uma suíte de testes, e por quê?
9. Cite três custos ocultos e explique o do aprisionamento.
10. Em que situações testar **não** se paga?
11. Monte uma pilha profissional de custo zero e diga o que falta nela.

---

## Fontes consultadas (13/08/2026)

- [Pricing changes for GitHub Actions — GitHub](https://github.com/resources/insights/2026-pricing-changes-for-github-actions)
- [Update to GitHub Actions pricing — GitHub Changelog](https://github.blog/changelog/2025-12-16-coming-soon-simpler-pricing-and-a-better-experience-for-github-actions/)
- [GitHub Actions Pricing 2026 — CICDCalculator](https://cicdcalculator.com/github-actions) *(agregador de terceiros)*
- [Per minute charges for self hosted runners — discussão na comunidade GitHub](https://github.com/orgs/community/discussions/182089)
- [BrowserStack vs Sauce Labs: Pricing at Scale (2026) — Autonoma](https://getautonoma.com/blog/browserstack-vs-saucelabs-2026) *(agregador de terceiros)*
- [Sauce Labs vs LambdaTest (2026) — Autonoma](https://getautonoma.com/blog/saucelabs-vs-lambdatest-2026) *(agregador de terceiros)*
- [BrowserStack vs Sauce Labs vs LambdaTest (2026) — QASkills](https://qaskills.sh/blog/browserstack-vs-saucelabs-vs-lambdatest-2026) *(agregador de terceiros)*

> Os preços de BrowserStack, Sauce Labs e LambdaTest vieram de agregadores, não das páginas
> oficiais de preço. **Confirme na fonte primária** antes de contratar — planos de entrada e
> limites de paralelismo mudam com frequência, e há descontos anuais não refletidos aqui.
