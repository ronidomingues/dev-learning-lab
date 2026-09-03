# 24 · Segurança e governança

**Nível:** avançado
**Data:** 14/08/2026

Segurança em BI tem uma característica peculiar: o produto **existe para espalhar
informação**. Toda medida de segurança luta contra o propósito da ferramenta. Por isso o
tema é mal resolvido na maioria das empresas — e por isso vale entendê-lo bem.

---

## 1. As camadas

```
┌────────────────────────────────────────────────────────────────┐
│ 1 · LOCATÁRIO (tenant)                                         │
│     Configurações globais: quem pode publicar na web, exportar,│
│     usar visuais não certificados, criar workspaces…            │
├────────────────────────────────────────────────────────────────┤
│ 2 · CAPACIDADE                                                 │
│     Quem administra, quais workspaces vivem nela                │
├────────────────────────────────────────────────────────────────┤
│ 3 · WORKSPACE                                                  │
│     Admin / Membro / Colaborador / Visualizador                 │
├────────────────────────────────────────────────────────────────┤
│ 4 · ITEM (modelo, relatório, app)                              │
│     Ler, Reescrever, Recompartilhar, Build                      │
├────────────────────────────────────────────────────────────────┤
│ 5 · DADOS DENTRO DO MODELO                                     │
│     RLS (linhas) · OLS (tabelas e colunas)                      │
├────────────────────────────────────────────────────────────────┤
│ 6 · O DADO QUE SAI                                             │
│     Rótulos de confidencialidade + Microsoft Purview            │
│     Protege o arquivo Excel/PDF DEPOIS de exportado             │
└────────────────────────────────────────────────────────────────┘
```

A camada 6 é a menos conhecida e a mais interessante: é a única que continua valendo
**depois** que o dado saiu do Power BI.

---

## 2. RLS — segurança em nível de linha

### 2.1 As duas formas

**Estática** — uma função por grupo, com filtro fixo:

```dax
-- Função "Sudeste", na tabela dCliente
dCliente[Regiao] = "Sudeste"
```

Simples e rápida. Não escala: 12 regiões = 12 funções para manter.

**Dinâmica** — uma função só, que consulta quem está perguntando:

```dax
-- Função "VendasRestritas", na tabela dVendedor
VAR UsuarioAtual = USERPRINCIPALNAME()
VAR Escopo = LOOKUPVALUE( dSeguranca[Escopo], dSeguranca[Email], UsuarioAtual )
VAR SKUsuario = LOOKUPVALUE( dSeguranca[SK_Vendedor], dSeguranca[Email], UsuarioAtual )
VAR EquipeUsuario = LOOKUPVALUE( dSeguranca[Equipe], dSeguranca[Email], UsuarioAtual )
RETURN
    SWITCH(
        Escopo,
        "Tudo",     TRUE(),
        "Vendedor", dVendedor[SK_Vendedor] = SKUsuario,
        "Equipe",   dVendedor[Equipe] = EquipeUsuario,
        FALSE()          -- ← FALHA FECHADA
    )
```

Implementação completa e comentada em
[`07-projeto-modelo/modelo/definition/roles/VendasRestritas.tmdl`](07-projeto-modelo/modelo/definition/roles/VendasRestritas.tmdl).

### 2.2 Os princípios de projeto

**1. Filtre a dimensão, não o fato.** 12 linhas avaliadas por consulta em vez de 60
milhões. Mais rápido e muito mais fácil de auditar.

**2. Falhe fechada.** Quem não está na tabela de segurança recebe `FALSE()` — nenhuma
linha. O contrário (ver tudo por omissão) é como vazamentos acontecem.

**3. Proteja a própria tabela de segurança.** Ocultar não protege — quem consulta o modelo
pelo Excel ou por XMLA vê tabelas ocultas. Aplique uma regra que a esvazie:

```dax
-- na mesma função, na tabela dSeguranca:
dSeguranca[Email] = USERPRINCIPALNAME()
```

**4. Teste antes de publicar.** Modelagem → **Exibir como** → marque a função e informe um
e-mail em "Outro usuário".

**5. Atribua no Service.** Modelo semântico → **Segurança** → adicione usuários ou (melhor)
**grupos do Entra ID** à função. **Sem esse passo, a RLS não faz absolutamente nada** —
é o erro mais comum de todos.

**6. Prefira grupos a usuários.** Entrada e saída de pessoas vira gestão de grupo, não
alteração de modelo.

### 2.3 O que a RLS NÃO protege

Escreva isto na parede:

| Não protege | Por quê |
|---|---|
| **O arquivo `.pbix`** | Quem tem o arquivo tem **todos** os dados. RLS é segurança de consumo no Service |
| **Quem é Admin/Membro/Colaborador do workspace** | Só Visualizadores são filtrados |
| **Contra inferência por agregado** | Uma medida "% do total geral" revela o total da empresa |
| **Metadados** | Nomes de tabelas, colunas, medidas e a estrutura são visíveis |
| **Contra exportação** | O usuário exporta o que **pode ver** — mas pode ver muito |

### 2.4 O ataque por inferência — e ele é real

Suponha RLS por vendedor, e uma medida inocente:

```dax
% do Total Geral = DIVIDE( [Faturamento], CALCULATE( [Faturamento], REMOVEFILTERS() ) )
```

O vendedor vê seu faturamento (R$ 1,2 M) e vê "2,4%". Duas divisões depois, ele sabe o
faturamento da empresa (R$ 50 M) — informação que ele não deveria ter.

Pior: com um pouco de paciência e vários recortes, é possível reconstruir valores de
terceiros.

**A RLS filtra linhas. Ela não impede que agregados vazem informação sobre as linhas
filtradas.** Este é o mesmo problema que a literatura de **privacidade diferencial** trata,
e não há solução completa no Power BI.

**Mitigações práticas:**

1. Não exponha medidas de "% do total geral" em modelos com RLS. Use `ALLSELECTED`.
2. Se o total da empresa é sensível, ele não deve estar no mesmo modelo.
3. Para casos realmente sensíveis, **modelos separados** por público — mais caro, mais
   seguro.

### 2.5 RLS e desempenho

RLS é reavaliada a cada consulta. Uma expressão com `LOOKUPVALUE` numa tabela de 50 mil
linhas, avaliada milhares de vezes por dia, custa.

Otimizações: filtre a dimensão; use `CONTAINS`/`IN` em vez de `LOOKUPVALUE` quando
possível; mantenha a tabela de segurança pequena; evite RLS que atravesse muitas relações.

**Cuidado especial com relações bidirecionais:** elas podem fazer a segurança propagar por
caminhos inesperados. Revise **todas** as relações bidirecionais ao implementar RLS.

---

## 3. OLS — segurança em nível de objeto

Esconde **tabelas ou colunas inteiras** de determinados perfis.

Configurada apenas via **Tabular Editor** ou XMLA (não há interface no Desktop):

```
Role "Comercial" → Table Permissions → dFolhaPagamento → None
Role "Comercial" → Column Permissions → dFuncionario[Salario] → None
```

**Diferença fundamental para a RLS:**

| | RLS | OLS |
|---|---|---|
| Esconde | Linhas | Tabelas e colunas |
| O usuário sabe que existe? | Sim (vê a coluna, com menos linhas) | **Não** (o objeto some) |
| Efeito colateral | Nenhum | **Visuais que usam o objeto quebram** |

O efeito colateral é sério: um relatório com um gráfico de salários simplesmente **falha**
para quem não tem acesso, com mensagem de erro. Planeje relatórios separados por perfil,
ou aceite o erro como comportamento.

---

## 4. Rótulos de confidencialidade

> **Rótulo de confidencialidade** (*sensitivity label*) — uma marcação do Microsoft Purview
> (`Público`, `Interno`, `Confidencial`, `Altamente Confidencial`) aplicada a itens do
> Power BI e **herdada pelos arquivos exportados**.

**Por que é a camada mais poderosa:** ela é a única que continua valendo depois que o dado
saiu. Um Excel exportado de um modelo rotulado como "Confidencial" nasce criptografado,
com as permissões do rótulo, e permanece protegido mesmo se for anexado a um e-mail
externo.

**Como funciona:**

1. Rótulos definidos no Microsoft Purview (fora do Power BI).
2. Aplicados a modelos, relatórios, dashboards, dataflows.
3. **Herança:** um relatório herda o rótulo do modelo; um Excel exportado herda o do
   relatório.
4. Podem ser **obrigatórios** (não se publica sem rotular) e **automáticos** (por regra).

**Limitação honesta:** a proteção depende do ecossistema Microsoft 365. Um PDF exportado e
impresso não tem proteção nenhuma. Rótulo é controle, não é impossibilidade.

---

## 5. Configurações de locatário — o que ajustar primeiro

Portal de administração → Configurações de locatário. As que mais importam:

| Configuração | Recomendação | Por quê |
|---|---|---|
| **Publicar na Web** | **Desabilitar** (ou grupo restrito com aprovação) | ☠ Maior fonte de vazamento |
| Exportar para Excel | Permitir com rótulos | Proibir empurra para cópia manual, que é pior |
| Exportar para `.csv` | Avaliar | |
| **Baixar `.pbix`** | Restringir | O arquivo baixado **ignora a RLS** |
| Visuais não certificados | **Restringir** | Podem enviar dados para fora |
| Criar workspaces | Grupo definido | Evita proliferação |
| Compartilhar com usuários externos | Restringir a domínios aprovados | |
| Endpoint XMLA | Somente leitura por padrão | Gravação é poder de administrador |
| Convidados (B2B) | Política explícita | |
| Copilot e recursos de IA | Decisão consciente e documentada | Ver §7 |

**As três primeiras ações de um administrador novo**, em ordem:

1. Auditar quem já publicou na web (há um relatório de administração para isso) e desligar.
2. Restringir download de `.pbix` em workspaces com RLS.
3. Ativar métricas de uso e o inventário via API de scanner.

---

## 6. Inventário e auditoria

### 6.1 API de scanner

Endpoint `POST /admin/workspaces/getInfo` devolve o inventário completo do locatário:
workspaces, itens, donos, fontes de dados, medidas, permissões.

**É a base de qualquer governança séria.** Com isso você responde:

- Quantos modelos existem? Quantos duplicados?
- Que fontes são usadas, e por quem?
- Quantos relatórios apontam para o `C:\` de alguém?
- Quem tem acesso a quê?

### 6.2 Log de auditoria

Eventos do Power BI vão para o log unificado do Microsoft 365 (retenção conforme a
licença). Registra: visualização de relatório, exportação, compartilhamento, alteração de
permissão, download de `.pbix`, criação e exclusão.

**Use para:** investigar incidentes, comprovar conformidade, medir adoção real.

### 6.3 Métricas de uso

Por relatório: visualizações, usuários únicos, dispositivo, distribuição por dia.
Alimenta a decisão de aposentadoria ([`23`](23-servico-colaboracao-e-atualizacao.md) §6).

---

## 7. Governança que funciona

**Opinião do autor**, baseada no que vi dar certo e errado.

### 7.1 O modelo de três camadas

```
┌─────────────────────────────────────────────────────────────┐
│  CERTIFICADO — o time de dados mantém                       │
│  Modelos corporativos, definições oficiais, SLA de suporte  │
│  Mudança = processo. Confiança = alta                       │
├─────────────────────────────────────────────────────────────┤
│  PROMOVIDO — a área de negócio mantém                       │
│  Modelos departamentais, com dono nomeado                   │
│  Mudança = ágil. Confiança = média                          │
├─────────────────────────────────────────────────────────────┤
│  EXPLORATÓRIO — qualquer um                                 │
│  "Meu workspace", análises pontuais                         │
│  Sem promessa. Confiança = nenhuma, e está tudo bem         │
└─────────────────────────────────────────────────────────────┘
```

**A chave é a camada de baixo existir e ser aceita.** Governança que proíbe a exploração
não elimina a exploração — ela a empurra para o Excel, onde não há visibilidade nenhuma.
Deixe as pessoas explorarem; garanta que saibam que aquilo não é oficial.

### 7.2 O que documentar (o mínimo)

Para cada item **certificado ou promovido**:

- **dono do dado** (quem responde pela regra) e **dono técnico** (quem mantém);
- **fonte** e frequência de atualização;
- **definição de cada medida**, em português — use as descrições `///`;
- **o que não está incluído** (o mais importante e o mais esquecido);
- classificação de confidencialidade;
- data da última revisão.

### 7.3 Padrões que valem impor

| Padrão | Por quê |
|---|---|
| Nomenclatura (`fVendas`, `dCliente`, `WS-Vendas-PROD`) | Buscável, previsível |
| Tema corporativo obrigatório | Identidade e acessibilidade |
| **Best Practice Analyzer** no CI | Pega 80% dos problemas automaticamente |
| Camada semântica para domínios centrais | Um número, não cinco |
| Página "sobre" em todo relatório certificado | Documentação onde a dúvida acontece |
| Revisão anual de itens | Aposentar o que morreu |

### 7.4 O que NÃO funciona

- **Proibir o Power BI Desktop.** As pessoas usam Excel, que é pior.
- **Exigir aprovação de TI para todo relatório.** Cria fila, e a fila cria contorno.
- **Documento de governança de 60 páginas.** Ninguém lê. Prefira regras automatizadas.
- **Certificar tudo.** Certificação sem capacidade de manutenção é promessa falsa.
- **Contar com treinamento como controle.** Treinamento ensina; configuração impede.

---

## 8. Copilot e IA — a nova superfície

Recursos de IA (Copilot, agentes, *semantic model authoring skill*) trazem questões novas:

| Questão | O que considerar |
|---|---|
| Que dados o Copilot acessa? | Os que o **usuário** já pode acessar. RLS é respeitada |
| Os dados treinam o modelo? | A Microsoft declara que **não** para os modelos base; confirme os termos vigentes |
| Onde os dados são processados? | Depende da região do locatário e das configurações |
| O Copilot pode errar? | **Sim.** Resposta plausível e errada é o modo de falha típico |
| Quem é responsável pelo número? | **Quem publica.** "O Copilot escreveu" não é defesa |

**Recomendação prática:** habilite o Copilot de forma consciente, comece por um grupo
piloto, e **exija revisão humana de qualquer medida gerada** antes de ir para um modelo
certificado. Um DAX plausível e errado é mais perigoso que um DAX que não compila.

Ver [`26-fabric-e-ecossistema.md`](26-fabric-e-ecossistema.md) e
[`65-estado-da-arte.md`](65-estado-da-arte.md).

---

## 9. Os cinco porquês: por que a RLS não protege o arquivo `.pbix`?

1. **Por que quem tem o `.pbix` vê tudo?**
   Porque o arquivo contém o **modelo inteiro**, com todos os dados comprimidos. A RLS é
   um conjunto de regras aplicadas **em tempo de consulta pelo servidor**, não uma
   criptografia dos dados.

2. **Por que não criptografar as linhas por perfil dentro do arquivo?**
   Porque o motor precisa dos dados **descomprimidos e legíveis** para varrer e agregar. E
   porque a RLS é dinâmica — `USERPRINCIPALNAME()` só existe quando há um usuário
   autenticado, o que não acontece num arquivo em disco.

3. **Por que não exigir autenticação para abrir o arquivo?**
   Porque o Power BI Desktop precisa funcionar offline, e porque o arquivo é um formato
   aberto que várias ferramentas leem. Qualquer verificação seria local e, portanto,
   contornável.

4. **Por que a Microsoft não fecha isso?**
   Porque fechar exigiria abandonar o modelo de arquivo local — que é a base do
   *self-service BI* desde 2009. É uma tensão de projeto herdada, não um descuido.

5. **Parada legítima — princípio geral de segurança.**
   Vale a regra: **quem controla o meio de execução controla os dados**. É o mesmo motivo
   pelo qual DRM não funciona plenamente e pelo qual "segurança do lado do cliente" nunca
   é segurança. A resposta correta não é técnica dentro do Power BI: é **não distribuir o
   arquivo** — restringir o download de `.pbix` no locatário e distribuir por app.

---

## 10. Autoteste

1. Descreva as seis camadas de segurança e diga qual continua valendo fora do Power BI.
2. Diferencie RLS estática e dinâmica, com um exemplo de cada.
3. Cite os seis princípios de projeto de RLS.
4. Por que ocultar a tabela de segurança não a protege?
5. Cite cinco coisas que a RLS **não** protege.
6. Explique o ataque por inferência e três mitigações.
7. Qual a diferença entre RLS e OLS, e qual é o efeito colateral da OLS?
8. Por que os rótulos de confidencialidade são a camada mais poderosa, e qual seu limite?
9. Cite as três primeiras ações de um administrador novo.
10. Descreva o modelo de três camadas de governança e por que a camada de baixo é essencial.
11. Cite três coisas que não funcionam em governança de BI, e por quê.
12. Explique por que a RLS não protege o `.pbix`, chegando ao princípio geral.

---

**Próximo:** [`25-ciclo-de-vida-e-devops.md`](25-ciclo-de-vida-e-devops.md).
