# 25 · Ciclo de vida e DevOps

**Nível:** avançado
**Data:** 14/08/2026

Até 2023, a crítica técnica mais forte ao Power BI era justa: "não dá para versionar".
PBIP e TMDL encerraram essa crítica. Este capítulo mostra como trabalhar como engenharia
de software — e por que isso deixou de ser opcional.

---

## 1. O problema, na forma que ele aparece

```
📁 Vendas.pbix
📁 Vendas_v2.pbix
📁 Vendas_v2_FINAL.pbix
📁 Vendas_v2_FINAL_revisado.pbix
📁 Vendas_v2_FINAL_revisado_JOÃO.pbix
📁 Vendas_PRODUÇÃO_NÃO_MEXER.pbix
```

Sintomas: ninguém sabe qual é o certo; duas pessoas não conseguem trabalhar ao mesmo
tempo; não há como saber o que mudou entre versões; publicar em produção é um ato de fé.

**Causa:** `.pbix` é um **binário**. O Git o versiona, mas não consegue comparar nem
mesclar. Um arquivo de 300 MB, um commit por dia, é um repositório de 100 GB por ano
sem nenhum benefício.

---

## 2. PBIP e TMDL — a solução

### 2.1 O que são

> **PBIP** (*Power BI Project*) — em vez de um `.pbix` binário, o Power BI salva uma
> **pasta com arquivos de texto**.
>
> **TMDL** (*Tabular Model Definition Language*) — a linguagem em que o **modelo** é
> descrito, em texto legível.
>
> **PBIR** — o formato de texto da definição do **relatório**.

### 2.2 Como ativar

**Arquivo → Opções → Recursos de visualização → Formato de salvamento de projeto do
Power BI** (e as opções de TMDL e PBIR). Depois, **Arquivo → Salvar como → Projeto do
Power BI (.pbip)**.

### 2.3 A estrutura gerada

```
TintasAurora.pbip                  ← ponteiro (JSON pequeno)
TintasAurora.SemanticModel/
├── definition.pbism
├── diagramLayout.json
└── definition/
    ├── model.tmdl                 ← cultura, opções, referências
    ├── database.tmdl
    ├── expressions.tmdl           ← parâmetros e funções M
    ├── relationships.tmdl         ← os relacionamentos
    ├── roles/
    │   └── VendasRestritas.tmdl   ← RLS
    └── tables/
        ├── fVendas.tmdl           ← colunas, tipos, partição M, medidas
        ├── dProduto.tmdl
        └── …
TintasAurora.Report/
├── definition.pbir
├── report.json  (ou definition/ em PBIR)
└── StaticResources/
    └── SharedResources/BaseThemes/…
```

**Tudo isso é texto.** Diff, merge, revisão, busca, script — tudo funciona.

### 2.4 Como é o TMDL

```tmdl
table fVendas

	column NF
		dataType: int64
		formatString: 0
		summarizeBy: none
		sourceColumn: NF

	/// Faturamento líquido: bruto menos descontos.
	/// Definição acordada com o Comercial em 14/08/2026.
	measure 'Faturamento Líquido' = [Faturamento Bruto] - [Descontos Concedidos]
		formatString: \R$ #,0.00;-\R$ #,0.00;\R$ #,0.00

	partition fVendas = m
		mode: import
		source =
				let
				    Origem = LerCsv("fVendas.csv")
				in
				    Origem
```

Um exemplo completo e comentado está em
[`07-projeto-modelo/modelo/definition/`](07-projeto-modelo/README.md).

### 2.5 O que o diff mostra

```diff
 	measure 'Margem %' =
-		DIVIDE( [Margem Bruta], [Faturamento Líquido] )
+		DIVIDE( [Margem Bruta], [Faturamento Bruto] )
 		formatString: 0.00%
```

Uma linha, revisável em pull request, com autor, data e justificativa no commit. **Isto é
o que estava faltando.**

---

## 3. Git

### 3.1 `.gitignore`

```gitignore
# Cache local do Power BI Desktop
**/.pbi/localSettings.json
**/.pbi/cache.abf

# Binários
*.pbix
*.abf

# Dados (se forem gerados ou baixados)
dados/
*.csv
*.parquet
```

**Regra:** `.pbix` fora do Git. Se você precisa de um `.pbix` para distribuir, gere-o a
partir do PBIP, como artefato de build.

### 3.2 Fluxo de trabalho

```
main ────●────────●─────────────●──────► produção
          \      /               \
           ●────●                 ●───── feature/margem-ajustada
        feature/nova-medida
```

1. Branch por mudança.
2. Abrir o PBIP no Desktop, alterar, salvar.
3. `git diff` — **leia o que mudou**. O Desktop às vezes reescreve arquivos com mudanças
   cosméticas; não deixe passar despercebido.
4. Commit com mensagem que explique **o porquê**, não o quê.
5. Pull request com revisão.
6. Merge → pipeline publica.

### 3.3 Conflitos de merge

**Modelo (TMDL):** conflitos são resolvíveis à mão na maioria dos casos. Cada tabela é um
arquivo; duas pessoas em tabelas diferentes não conflitam.

**Relatório (PBIR):** mais complicado — a definição do relatório tem posições, ordem Z e
identificadores. Conflitos em `report.json` são desagradáveis.

**Prática que reduz dor:**

- **Um relatório por pessoa por vez.** Coordene, não conflite.
- **Modelo e relatório em PRs separados**, quando possível.
- Prefira **medidas no modelo** a lógica no relatório — o modelo mescla melhor.

### 3.4 Integração nativa com Git (Fabric)

O workspace do Fabric pode ser **conectado a um repositório** (Azure DevOps ou GitHub).
Mudanças no workspace aparecem como commits; commits aparecem como mudanças pendentes no
workspace, aplicáveis com um clique.

**Vantagem:** funciona sem sair do navegador; é o caminho para quem não tem o Desktop
(Linux, macOS).

**Cuidado:** a sincronização é por workspace inteiro, e nem todo tipo de item é suportado.
Verifique a lista de itens suportados na versão vigente.

---

## 4. Pipelines de implantação

> **Deployment pipeline** — três estágios ligados (Desenvolvimento → Teste → Produção),
> com promoção de conteúdo entre eles.

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  WS-Vendas   │───►│  WS-Vendas   │───►│  WS-Vendas   │
│     DEV      │    │    TESTE     │    │     PROD     │
└──────────────┘    └──────────────┘    └──────────────┘
   analistas         donos de negócio     300 usuários
   publicam          validam              consomem (via app)
```

**Regras de implantação** (*deployment rules*): a cada estágio, trocar automaticamente:

- **parâmetros** (servidor, base, ano inicial);
- **fontes de dados**;
- credenciais permanecem por estágio.

Isso resolve o problema de "o modelo aponta para o banco de dev em produção" — que é
resolvido de forma manual e frágil na maioria das empresas.

**Comparação entre estágios:** o pipeline mostra o que difere antes de promover. Use.

---

## 5. Automação

### 5.1 O que dá para automatizar

| Tarefa | Ferramenta |
|---|---|
| Publicar `.pbix`/PBIP | API REST `imports`, `fabric-cli`, PowerShell |
| Implantar modelo | **XMLA** com Tabular Editor (linha de comando) ★ |
| Disparar atualização | API REST `refreshes` |
| Atualizar partição específica | XMLA (TMSL) |
| Rodar Best Practice Analyzer | **Tabular Editor CLI** ★ |
| Comparar modelos | ALM Toolkit CLI |
| Inventariar o locatário | API de scanner |
| Testar medidas | Consultas DAX via XMLA + asserções |

### 5.2 Um pipeline de CI mínimo

```yaml
# .github/workflows/powerbi.yml (exemplo ilustrativo — adapte)
name: Power BI CI

on:
  pull_request:
    paths:
      - '**/*.tmdl'
      - '**/*.pbir'

jobs:
  validar:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Baixar Tabular Editor 2
        run: |
          Invoke-WebRequest `
            -Uri "https://github.com/TabularEditor/TabularEditor/releases/latest/download/TabularEditor.Portable.zip" `
            -OutFile TE.zip
          Expand-Archive TE.zip -DestinationPath TE

      - name: Best Practice Analyzer
        run: |
          .\TE\TabularEditor.exe `
            ".\TintasAurora.SemanticModel\definition" `
            -A BPARules.json `
            -V

      # -A roda as regras; -V devolve código de saída != 0 se houver erro,
      # o que reprova o PR automaticamente.
```

**Isto é o que separa um time profissional:** o Best Practice Analyzer roda em **todo PR**
e reprova automaticamente relações bidirecionais não justificadas, colunas sem
`summarizeBy`, medidas sem formato, uso de `EARLIER`, colunas de alta cardinalidade e
dezenas de outros itens.

> **Declaração:** o YAML acima **não foi executado** (não há runner Windows nem modelo
> publicado nesta sessão). É um esqueleto realista, não uma comprovação. Adapte caminhos e
> versões.

### 5.3 Implantação por XMLA

```powershell
# Publica o modelo direto no workspace, sem passar pelo .pbix
.\TabularEditor.exe ".\TintasAurora.SemanticModel\definition" `
  -D "powerbi://api.powerbi.com/v1.0/myorg/WS-Vendas-PROD" "TintasAurora" `
  -O -C -P -R -M -E -V
```

**Requer:** capacidade (PPU ou F-SKU) com o endpoint XMLA em **Leitura/Gravação**.

**Vantagem sobre publicar `.pbix`:** implanta **só os metadados**, sem reenviar os dados.
Uma correção de medida vai ao ar em segundos, sem refresh.

### 5.4 Testes automatizados de modelo

Pouco praticado e muito valioso. A ideia: consultas DAX conhecidas com resultados
esperados.

```dax
-- teste_faturamento_2025.dax
EVALUATE
VAR Esperado = 68179435.59
VAR Obtido =
    CALCULATE( [Faturamento Líquido], dCalendario[Ano] = 2025 )
VAR Diferenca = ABS( Obtido - Esperado )
RETURN
    ROW(
        "Teste",     "Faturamento 2025",
        "Esperado",  Esperado,
        "Obtido",    Obtido,
        "Passou",    IF( Diferenca < 0.01, "SIM", "NÃO" )
    )
```

Execute via XMLA num script e falhe o pipeline se algum "Passou" for "NÃO".

**Onde obter os valores esperados:** de uma fonte independente. No projeto-modelo, é
exatamente o que o `validar.py` produz — o **gabarito** da §10 do README foi calculado em
Python, fora do Power BI, e serve como oráculo para o DAX.

Esse é o padrão: **o teste precisa de um oráculo independente do sistema testado.**

---

## 6. Documentação como código

Com PBIP, a documentação pode ser **gerada**:

| Fonte | Gera |
|---|---|
| Descrições `///` das medidas | Dicionário de métricas |
| `relationships.tmdl` | Diagrama do modelo |
| `expressions.tmdl` | Linhagem das fontes |
| API de scanner | Catálogo do locatário |
| DMVs (`INFO.VIEW.MEASURES()`) | Inventário de medidas |

**Prática que recomendo:** um script no CI que lê o TMDL e gera um `MODELO.md` no
repositório, com todas as medidas, suas descrições e suas dependências. Documentação que
não pode ficar desatualizada, porque é derivada do código.

---

## 7. O caminho de adoção

Não tente tudo de uma vez. Ordem que funciona:

| Passo | Esforço | Ganho |
|---|---|---|
| 1. Salvar como PBIP e pôr no Git | 1 h | Alto — histórico e diff |
| 2. Convenções de nome e tema | 2 h | Médio |
| 3. Best Practice Analyzer manual | 1 h | **Alto** |
| 4. Pipeline de implantação (DEV→TESTE→PROD) | 4 h | Alto |
| 5. Separar modelo de relatório | 4 h | Alto |
| 6. Best Practice Analyzer no CI | 8 h | Alto |
| 7. Implantação por XMLA | 8 h | Médio-alto |
| 8. Testes de medida automatizados | 16 h | Alto (e raro) |

**Comece pelo 1 e pelo 3.** Juntos custam duas horas e resolvem os dois piores problemas:
não saber o que mudou e não saber o que está errado.

---

## 8. Os cinco porquês: por que o `.pbix` não podia ser versionado?

1. **Por que o Git não consegue comparar dois `.pbix`?**
   Porque `.pbix` é um contêiner ZIP com componentes binários — inclusive o modelo tabular
   serializado e comprimido. Bytes não têm linhas para comparar.

2. **Por que o modelo era guardado assim?**
   Porque o `.pbix` foi projetado como **formato de execução**, não de fonte: ele carrega
   os dados comprimidos prontos para o motor abrir rápido. Otimizar para carga rápida e
   otimizar para diff são objetivos opostos.

3. **Por que não separaram fonte e artefato desde o começo?**
   Porque o produto de 2015 mirava o analista individual, para quem "um arquivo que abre
   e funciona" era exatamente o requisito. Versionamento não estava no problema que ele
   resolvia.

4. **Por que mudou?**
   Porque a base de usuários mudou. Quando o Power BI virou plataforma corporativa com
   times, revisão e CI/CD, a ausência de diff passou de irrelevante a impeditiva. PBIP e
   TMDL são a resposta a uma pressão de mercado, não a uma epifania técnica.

5. **Parada legítima — princípio de engenharia: separar fonte de artefato.**
   É o mesmo princípio que separa `.c` de `.exe`, `.ts` de `.js`, Dockerfile de imagem.
   A fonte é feita para humanos lerem, revisarem e mesclarem; o artefato é feito para a
   máquina executar. Tentar usar um só arquivo para os dois papéis sempre falha em um
   deles. O Power BI passou oito anos aprendendo isso.

---

## 9. Autoteste

1. Por que `.pbix` no Git não resolve o problema?
2. O que são PBIP, TMDL e PBIR? Qual descreve o quê?
3. Como se ativa o formato PBIP?
4. O que deve estar no `.gitignore` de um projeto Power BI?
5. Por que conflitos de merge são piores no relatório que no modelo, e como reduzir a dor?
6. O que uma regra de implantação (*deployment rule*) resolve?
7. Qual a vantagem de implantar por XMLA em vez de publicar `.pbix`?
8. Escreva a ideia de um teste automatizado de medida. De onde vem o valor esperado?
9. Por que a documentação gerada a partir do TMDL é superior a um wiki?
10. Quais são os dois primeiros passos de adoção, e por quê?
11. Explique por que o `.pbix` não podia ser versionado, chegando ao princípio geral.

---

**Próximo:** [`26-fabric-e-ecossistema.md`](26-fabric-e-ecossistema.md).
