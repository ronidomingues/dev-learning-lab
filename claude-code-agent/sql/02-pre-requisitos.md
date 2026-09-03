# 02 — Pré-requisitos

Nível: iniciante · Data: 13/08/2026

O SQL é, de longe, a linguagem de computador mais acessível a quem não é
programador. Isso não é marketing: foi um objetivo explícito de projeto em 1974
e o motivo do nome original SEQUEL, *Structured **English** Query Language*.
A barreira de entrada é genuinamente baixa. Este arquivo diz exatamente quão
baixa, e onde ficam os degraus de verdade.

---

## 1. Conhecimento

### 1.1 Indispensável

| Pré-requisito | Por que | Onde aprender se faltar |
|---|---|---|
| Saber usar uma planilha (linhas, colunas, filtro, `SOMASE`, tabela dinâmica) | O modelo mental de tabela, filtro e agrupamento é literalmente o mesmo | Você já sabe. Se não, qualquer curso básico de Excel/LibreOffice, 4 h |
| Ler inglês técnico básico | Palavras-chave (`SELECT`, `WHERE`, `JOIN`), mensagens de erro e documentação | Não precisa falar. Precisa reconhecer ~50 palavras. A [lista está no glossário](GLOSSARIO.md) |
| Abrir um terminal e digitar um comando | Instalação e primeiro uso | [03-instalacao.md](03-instalacao.md) ensina cada comando com o que ele faz |
| Noção de arquivo e pasta | Saber onde o banco está gravado | Conhecimento geral de computador |

**É só isso.** Não é preciso saber programar. Não é preciso saber
álgebra relacional. Não é preciso saber o que é um índice B-tree.

### 1.2 Ajuda muito (mas dá para começar sem)

| Item | Onde ajuda | Onde aprender |
|---|---|---|
| Python básico | Automatizar consultas, gerar gráfico, transformar resultado | [24-sql-com-python.md](24-sql-com-python.md); ou o curso *Python para Zumbis* (PT, gratuito) |
| Lógica booleana (E, OU, NÃO) | Escrever `WHERE` complexo sem errar | Qualquer curso de lógica; ver também [17-tipos-e-nulos.md](17-tipos-e-nulos.md) — a lógica do SQL tem **três** valores, não dois |
| Estatística descritiva | Média, desvio, quartil, correlação são funções SQL | Você já viu na graduação |
| Git | Versionar suas consultas (e você deve) | Não coberto aqui |
| Modelagem de dados | Projetar tabelas, não só consultar | [19-ddl-e-modelagem.md](19-ddl-e-modelagem.md) |

### 1.3 Especificamente para engenheiro químico

Nada de novo — mas o que você já tem vale muito:

- **Balanço de massa e energia** → é `SUM` com `GROUP BY` e uma tolerância.
- **Controle estatístico de processo** → é média, desvio e limites, tudo em SQL.
- **P&ID e nomenclatura ISA-5.1** → é o esquema de nomes dos tags no banco.
- **Noção de instrumentação** → é o que separa "o dado está errado" de "o
  processo está errado", e nenhum analista de dados tem isso.

Esta última linha é a mais importante do arquivo. **A parte difícil da análise
de dado de planta não é o SQL — é saber que uma temperatura de 300 °C num
reator de resina é um termopar rompido e não uma excursão.** Isso você tem e o
cientista de dados não. O SQL é o que falta.

---

## 2. Ambiente

### 2.1 Mínimo absoluto

| Item | Requisito |
|---|---|
| Sistema operacional | Windows 10+, macOS 12+, ou qualquer Linux dos últimos 8 anos |
| Memória | 2 GB livres (SQLite roda em 100 kB de RAM; o problema é o resto do sistema) |
| Disco | 200 MB para as ferramentas; mais o tamanho dos seus dados |
| Internet | Só para baixar. Depois, nada — SQLite e DuckDB funcionam sem rede |
| Conta em serviço | **Nenhuma**. Nada aqui exige cadastro, e-mail ou cartão |
| Privilégio de administrador | **Não é necessário** se você seguir o caminho recomendado |

Esta última linha resolve o problema real de quem trabalha em indústria: o
notebook corporativo bloqueado. **O Python já vem instalado em Linux e macOS e
traz o SQLite embutido**; no Windows, o instalador do Python funciona sem
administrador (opção "Install for me only"). Ver
[03-instalacao.md](03-instalacao.md), seção "Rede corporativa e máquina
bloqueada".

### 2.2 O que este curso usa

| Ferramenta | Versão testada | Papel | Obrigatória? |
|---|---|---|---|
| **SQLite** | 3.37.2 (embutida no Python 3.10.12) | Banco principal dos exemplos e do projeto | **Sim** — e já está no seu Python |
| Python | 3.10.12 | Roda o projeto-modelo e os testes | **Sim**, mas só a biblioteca padrão |
| `sqlite3` CLI | 3.53.4 (versão atual, jul/2026) | Cliente de linha de comando | Não — conveniente |
| **PostgreSQL** | 18.6 | Segundo dialeto, o padrão de mercado open-source | Não — só para comparação |
| **DuckDB** | 1.5.5 | SQL analítico sobre CSV/Parquet, sem servidor | Não — mas mude de ideia depois de ler o [23](23-dialetos.md) |
| Editor de texto | qualquer | Escrever as consultas | Sim (VS Code, Notepad++, vim, o que for) |

**Nenhuma delas é paga. Nenhuma exige cadastro.** Ver
[80-custos-e-licencas.md](80-custos-e-licencas.md) para o detalhe das licenças
e para o que muda quando o banco é Oracle ou SQL Server da empresa.

---

## 3. Tempo realista até cada nível

Medidas em horas de estudo **com as mãos no teclado**. Ler não conta; ler é
metade do tempo e um quarto do aprendizado.

| Marco | Você consegue | Horas | Arquivos deste curso |
|---|---|---|---|
| Primeiro resultado na tela | Criar tabela, inserir, consultar | 1–2 h | [03](03-instalacao.md), [04](04-como-comecar.md) |
| Consulta de uma tabela | `SELECT`, `WHERE`, `ORDER BY`, `LIMIT` | +4 h | [12](12-consulta-select.md) |
| Cruzar tabelas | `JOIN` interno e externo, sem errar a cardinalidade | +8 h | [13](13-juncoes.md) |
| Resumir dados | `GROUP BY`, `HAVING`, agregações | +6 h | [14](14-agregacao-e-grupos.md) |
| **Autônomo no trabalho** | Tudo acima + subconsultas e CTEs + datas | **+10 h (≈ 30 h no total)** | [15](15-subconsultas-e-ctes.md), [17](17-tipos-e-nulos.md) |
| Análise de série temporal | Funções de janela, média móvel, *gaps and islands* | +15 h | [16](16-funcoes-de-janela.md), [18](18-series-temporais.md) |
| Criar e modelar | `CREATE TABLE`, normalização, restrições, transações | +20 h | [19](19-ddl-e-modelagem.md), [20](20-dml-e-transacoes.md) |
| Fazer render | Ler plano, índices, reescrever consulta lenta | +20 h | [21](21-indices-e-desempenho.md) |
| Nível de pesquisa | Álgebra relacional, complexidade, otimização | +40 h e um livro | [60](60-teoria-avancada.md) |

**A honestidade que os cursos não dão:** as primeiras 30 horas rendem 90% do
valor prático. As 100 seguintes rendem os 10% restantes — e é neles que mora a
diferença entre uma consulta que roda em 40 ms e uma que roda em 40 minutos.
Para um engenheiro de processo, chegar às 30 horas já muda o trabalho.

**Onde as pessoas travam**, em ordem de frequência:

1. `JOIN` — especificamente, entender por que o resultado tem mais linhas do
   que a tabela original. É a **cardinalidade**, e está no [13](13-juncoes.md).
2. `NULL` — não é zero, não é vazio, e `NULL = NULL` é falso. [17](17-tipos-e-nulos.md).
3. `GROUP BY` — por que não se pode colocar qualquer coluna no `SELECT`. [14](14-agregacao-e-grupos.md).
4. A ordem de execução — `WHERE` roda antes de `SELECT`, e por isso o apelido
   de coluna não funciona no `WHERE`. [12](12-consulta-select.md).

---

## 4. Rota de resgate

**"Não sei usar terminal."**
Use o [04-como-comecar.md](04-como-comecar.md) pelo caminho do Python, que é
copiar e colar num arquivo e rodar. Ou use um editor gráfico: **DB Browser for
SQLite** (gratuito, roda em tudo — <https://sqlitebrowser.org>). Você vai
precisar do terminal um dia, mas não hoje.

**"Meu notebook é corporativo e não posso instalar nada."**
Três saídas, em ordem de preferência:
1. Python já instalado? `python --version`. Se sim, você já tem SQLite.
2. Não? Use <https://sqlime.org> ou <https://sqliteonline.com> — rodam SQLite
   dentro do navegador, sem enviar seus dados a lugar nenhum (é WebAssembly).
   **Cuidado ainda assim**: não cole dado de produção da empresa em site
   nenhum sem autorização, mesmo que a página jure processar localmente.
3. Peça ao TI o SQLite. É um único arquivo executável, sem instalador, sem
   serviço, sem porta de rede. É o pedido mais fácil de aprovar que existe.

**"Não sei nada de programação e travei no primeiro erro."**
Erro de SQL é quase sempre uma destas cinco coisas: vírgula faltando, aspas
erradas, nome de coluna errado, ponto-e-vírgula esquecido, ou tabela que não
existe. A tabela de erros literais está em
[03-instalacao.md](03-instalacao.md) (erros de instalação) e
[75-armadilhas.md](75-armadilhas.md) (erros de uso).

**"Sei o suficiente de SQL, quero só a parte de engenharia química."**
Vá direto para [30-engenharia-quimica.md](30-engenharia-quimica.md) e
[18-series-temporais.md](18-series-temporais.md). Volte ao
[16-funcoes-de-janela.md](16-funcoes-de-janela.md) quando encontrar `OVER`.

**"Preciso disso para ontem, para um relatório específico."**
[04-como-comecar.md](04-como-comecar.md) → [06-exemplos.md](06-exemplos.md).
Ache o exemplo mais parecido com o seu problema e adapte. Volte ao resto
depois.

**"Minha empresa usa Oracle / SQL Server / SAP HANA, não SQLite."**
Aprenda em SQLite mesmo. Uns 85% do que você vai escrever é idêntico. As
diferenças estão catalogadas em [23-dialetos.md](23-dialetos.md), com tabela de
tradução. Aprender o dialeto do trabalho depois custa poucas horas; aprender
SQL custa as 30 horas.

---

## 5. O que NÃO é pré-requisito (e que costumam dizer que é)

- **Saber programar.** Não é. A confusão vem de SQL ser ensinado dentro de
  cursos de programação.
- **Saber administrar banco de dados.** Instalar, fazer backup, configurar
  replicação — nada disso é necessário para *consultar*. São profissões
  diferentes (DBA × analista).
- **Ter um servidor.** SQLite e DuckDB são arquivos. Não há servidor, não há
  porta, não há senha.
- **Saber matemática avançada.** A álgebra relacional está no
  [60-teoria-avancada.md](60-teoria-avancada.md) porque é bonita e explica
  *por que* o SQL funciona, não porque seja necessária para usá-lo.
- **Inglês fluente.** ~50 palavras-chave, todas no [glossário](GLOSSARIO.md).

---

## Autoteste

1. Qual é o único conhecimento verdadeiramente indispensável para começar?
2. Por que "não preciso de privilégio de administrador" é relevante para quem
   trabalha na indústria?
3. Quantas horas, realisticamente, até você conseguir cruzar duas tabelas sem
   ajuda?
4. Quais são os quatro assuntos em que a maioria das pessoas trava, e em que
   arquivo cada um está?
5. Você é engenheiro químico e não sabe programar. O que você tem que um
   cientista de dados não tem, e por que isso importa mais que o SQL?
6. Seu notebook é bloqueado pelo TI. Quais são as três saídas, em ordem?
7. Sua empresa usa Oracle. Vale a pena aprender em SQLite? Por quê?

---

*Próximo: [03-instalacao.md](03-instalacao.md).*
