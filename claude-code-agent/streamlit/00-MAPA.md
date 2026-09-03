# Streamlit — do primeiro `st.write` ao painel em produção

> **Curso completo sobre Streamlit**, a biblioteca Python que transforma um
> script linear numa aplicação web.
> **Escrito em:** 02/09/2026 · **Versão de referência:** Streamlit **1.63.0**
> (publicada em 01/09/2026) · **Verificado em:** Ubuntu 22.04.5 LTS, x86-64,
> Python 3.10.12, pandas 2.3.3, plotly 7.0.0, uv 0.12.7.

Este material nasceu de duas perguntas:

> **Como fazer um dashboard profissional?**
> **Como fazer um site funcional com "backend"?**

A primeira é respondida no eixo [16](16-layout-e-design.md) →
[17](17-graficos-e-visualizacao.md) → [18](18-tabelas-e-edicao.md) →
[20](20-tema-e-identidade-visual.md).
A segunda, no eixo [21](21-backend-dados-e-conexoes.md) →
[22](22-autenticacao-e-autorizacao.md) → [23](23-arquitetura-de-app-real.md) →
[28](28-deploy-e-operacao.md) → [29](29-seguranca.md) → [30](30-testes.md).
As duas se encontram no [projeto-modelo](07-projeto-modelo/README.md), que é uma
aplicação inteira, executável e testada.

---

## O que você saberá ao final

**Nível de uso**
- instalar Streamlit e todo o conjunto ao redor, em Linux, macOS e Windows;
- montar um painel com filtros, indicadores, gráficos e exportação;
- construir CRUD com validação, transação, auditoria e papéis;
- publicar em contêiner, atrás de proxy, com HTTPS e autenticação.

**Nível de entendimento**
- explicar o modelo de rerun e derivar dele o cache, o `session_state` e os
  fragmentos;
- escolher entre `cache_data` e `cache_resource` sem hesitar, e saber o que dá
  errado ao trocar;
- entender como a identidade de um widget é calculada — e o que mudou em 2026;
- descrever o protocolo (WebSocket + protobuf + Arrow) e por que o deploy dói;
- provar por que memorização automática é indecidível, e por que o cache precisa
  de anotação humana.

**Nível de julgamento**
- projetar um painel que passa no teste dos cinco segundos;
- **validar** uma paleta em vez de escolhê-la por gosto;
- separar `nucleo/` de `paginas/`, e saber quando **não** vale a pena;
- diagnosticar lentidão medindo, na ordem certa;
- dizer, com argumento, quando **não** usar Streamlit.

---

## Roteiro de leitura

### Se você tem 1 hora
[01](01-introducao-leigo.md) → [03](03-instalacao.md) (só a seção do seu sistema)
→ [04](04-como-comecar.md)

### Se você tem um fim de semana
Bloco A inteiro ([01](01-introducao-leigo.md) a [07](07-projeto-modelo/README.md))
→ [12](12-modelo-de-execucao-e-rerun.md) → [14](14-cache-e-dados.md)
→ [16](16-layout-e-design.md) → labs 1 a 6 de [70](70-pratica.md)

### Se a sua pergunta é "**dashboard profissional**"
[16](16-layout-e-design.md) → [17](17-graficos-e-visualizacao.md) →
[18](18-tabelas-e-edicao.md) → [20](20-tema-e-identidade-visual.md) →
[14](14-cache-e-dados.md) → [15](15-fragments-e-performance.md) →
[`paginas/painel.py`](07-projeto-modelo/paginas/painel.py)

### Se a sua pergunta é "**site com backend**"
[21](21-backend-dados-e-conexoes.md) → [22](22-autenticacao-e-autorizacao.md) →
[23](23-arquitetura-de-app-real.md) → [19](19-multipagina-e-navegacao.md) →
[29](29-seguranca.md) → [30](30-testes.md) → [28](28-deploy-e-operacao.md) →
[projeto-modelo](07-projeto-modelo/README.md) inteiro

### Se você quer dominar (4 a 6 semanas)
Tudo, na ordem numérica, fazendo os 14 laboratórios de [70](70-pratica.md).

---

## Os arquivos

### Bloco A · Porta de entrada

| # | Arquivo | O que tem |
|---|---|---|
| 01 | [introducao-leigo](01-introducao-leigo.md) | o que é, para que serve, por que existe — zero jargão |
| 02 | [pre-requisitos](02-pre-requisitos.md) | o que saber antes, tempo realista, rota de resgate |
| 03 | [instalacao](03-instalacao.md) | **manual de campo**: Python, uv, Streamlit, extras, editor, Git, Docker, banco — nos três sistemas, com PATH, permissões, proxy corporativo, desinstalação e 18 erros literais |
| 04 | [como-comecar](04-como-comecar.md) | do ambiente pronto ao painel na tela; os 5 primeiros erros de uso |
| 05 | [manual-de-uso](05-manual-de-uso.md) | referência por tarefa, com **assinaturas extraídas do pacote instalado**; o que está obsoleto; 12 truques |
| 06 | [exemplos](06-exemplos.md) | **12 exemplos completos e executados**, do trivial a dois casos de produção |
| 07 | [projeto-modelo/](07-projeto-modelo/README.md) | **aplicação inteira**: painel + CRUD + login + papéis + migração + auditoria + 43 testes + Docker |

### Bloco B · Núcleo

| # | Arquivo | O que tem |
|---|---|---|
| 10 | [fundamentos](10-fundamentos.md) | as cinco entidades, os três tipos de memória, o protocolo, os cinco porquês do rerun |
| 11 | [historia](11-historia.md) | 2018 até 2026, com datas; por que a Snowflake comprou; o padrão que se repete |
| 12 | [modelo-de-execucao-e-rerun](12-modelo-de-execucao-e-rerun.md) | **o arquivo mais importante do curso** |
| 13 | [session-state-e-widgets](13-session-state-e-widgets.md) | as três regras de escrita, identidade de widget, formulários, estado na URL |
| 14 | [cache-e-dados](14-cache-e-dados.md) | os dois decoradores, a chave de cache, TTL como decisão de negócio, memória |
| 15 | [fragments-e-performance](15-fragments-e-performance.md) | a ordem correta de otimizar; orçamento de desempenho |
| 16 | [layout-e-design](16-layout-e-design.md) | **o dashboard profissional**: hierarquia, KPIs, os quatro estados, acessibilidade |
| 17 | [graficos-e-visualizacao](17-graficos-e-visualizacao.md) | escolher a forma, **validar a cor**, ajustar a marca, 12 anti-padrões |
| 18 | [tabelas-e-edicao](18-tabelas-e-edicao.md) | `column_config`, seleção, `data_editor`, tabelas grandes |
| 19 | [multipagina-e-navegacao](19-multipagina-e-navegacao.md) | `st.navigation`, portão de login, organização de arquivos |
| 20 | [tema-e-identidade-visual](20-tema-e-identidade-visual.md) | tema completo, fonte própria, ícones, e por que evitar CSS |
| 21 | [backend-dados-e-conexoes](21-backend-dados-e-conexoes.md) | **o backend**: banco, migração, transação, SQL sem injeção, dinheiro e fuso |
| 22 | [autenticacao-e-autorizacao](22-autenticacao-e-autorizacao.md) | `st.login` OIDC, papéis, as duas camadas, login caseiro |
| 23 | [arquitetura-de-app-real](23-arquitetura-de-app-real.md) | camadas, configuração, erros, e **quando não vale a pena** |
| 24 | [tarefas-longas-e-concorrencia](24-tarefas-longas-e-concorrencia.md) | threads, filas, o botão "parar" que não para |
| 25 | [componentes-customizados](25-componentes-customizados.md) | as três saídas, componente sem build, critérios de adoção |
| 26 | [arquivos-e-uploads](26-arquivos-e-uploads.md) | upload validado, onde guardar, download, estáticos |
| 27 | [tempo-real-e-streaming](27-tempo-real-e-streaming.md) | `write_stream`, chat, `run_every` com a conta feita, e o que o Streamlit não faz |
| 28 | [deploy-e-operacao](28-deploy-e-operacao.md) | Docker, nginx com WebSocket, réplicas, Kubernetes, observabilidade |
| 29 | [seguranca](29-seguranca.md) | modelo de ameaça, injeção, XSS, isolamento, LGPD |
| 30 | [testes](30-testes.md) | a pirâmide, `AppTest`, e um defeito da 1.63.0 encontrado aqui |
| 31 | [quando-nao-usar-streamlit](31-quando-nao-usar-streamlit.md) | comparação honesta com Dash, Reflex, Gradio, NiceGUI, BI |
| 60 | [teoria-avancada](60-teoria-avancada.md) | `V : S → T`, reconciliação, indecidibilidade do cache, os sete limites teóricos |
| 65 | [estado-da-arte](65-estado-da-arte.md) | setembro de 2026: Starlette, fragmentos paralelos, SiS, debates abertos |

### Bloco C · Prática e erros

| # | Arquivo | O que tem |
|---|---|---|
| 70 | [pratica](70-pratica.md) | **14 laboratórios** com critério de aceite e armadilha esperada |
| 75 | [armadilhas](75-armadilhas.md) | **28 armadilhas + 14 mitos + 12 más práticas**, com o porquê de cada uma persistir |

### Bloco D · Economia e ecossistema

| # | Arquivo | O que tem |
|---|---|---|
| 80 | [custos-e-licencas](80-custos-e-licencas.md) | Apache 2.0, hospedagem com preço e data, custo do Snowflake, custos ocultos, três orçamentos |
| 85 | [cursos-e-certificacoes](85-cursos-e-certificacoes.md) | cursos PT/EN/FR pesquisados; **não existe certificação oficial**; como avaliar um curso em 30 s |

### Bloco E · Fontes

| # | Arquivo | O que tem |
|---|---|---|
| 90 | [bibliografia](90-bibliografia.md) | livros com edição e ISBN conferidos; o que é legalmente gratuito |
| 95 | [referencias](95-referencias.md) | documentação, código-fonte comentado, specs, e **como este curso foi verificado** |
| — | [GLOSSARIO](GLOSSARIO.md) | ~85 termos definidos |

---

## As 12 camadas de profundidade

Conforme a regra deste repositório, o assunto atravessa todas:

| # | Camada | Onde |
|---|---|---|
| 1 | intuição para leigo | [01](01-introducao-leigo.md) |
| 2 | definição informal | [01](01-introducao-leigo.md), [10](10-fundamentos.md) |
| 3 | por que existe | [01](01-introducao-leigo.md) §3, [11](11-historia.md) |
| 4 | ambiente e primeiro uso | [03](03-instalacao.md), [04](04-como-comecar.md) |
| 5 | fundamentos formais | [10](10-fundamentos.md), [12](12-modelo-de-execucao-e-rerun.md) |
| 6 | mecânica interna | [12](12-modelo-de-execucao-e-rerun.md), [13](13-session-state-e-widgets.md), [14](14-cache-e-dados.md), [60](60-teoria-avancada.md) |
| 7 | implementação prática | [06](06-exemplos.md), [07](07-projeto-modelo/README.md), [70](70-pratica.md) |
| 8 | casos de uso reais | [06](06-exemplos.md) §10 e §12, [28](28-deploy-e-operacao.md) |
| 9 | trade-offs e alternativas | [31](31-quando-nao-usar-streamlit.md), [23](23-arquitetura-de-app-real.md) §3 |
| 10 | economia do assunto | [80](80-custos-e-licencas.md) |
| 11 | profundidade de pesquisa | [60](60-teoria-avancada.md) |
| 12 | estado da arte | [65](65-estado-da-arte.md) |

---

## O que este curso tem de diferente

**Tudo foi verificado, não copiado.**

- as **assinaturas de API** do [05](05-manual-de-uso.md) saíram de
  `inspect.signature` sobre a instalação 1.63.0, não da documentação;
- os **endpoints** do [28](28-deploy-e-operacao.md) foram testados com `curl`
  contra um servidor rodando;
- os **12 exemplos** do [06](06-exemplos.md) foram executados com `AppTest`, e as
  interações principais exercitadas;
- o **projeto-modelo** roda: 43 testes passam, o servidor sobe, o banco é
  populado;
- a **paleta de cores** foi submetida a um validador de daltonismo — **reprovou**,
  e a correção está documentada em [17](17-graficos-e-visualizacao.md) §4 como
  estudo de caso;
- um **defeito da 1.63.0** foi encontrado, isolado e registrado
  ([75](75-armadilhas.md), armadilha 24);
- preços, cursos e livros foram **pesquisados na web em 02/09/2026**, com as
  fontes listadas em cada arquivo.

---

## Status

| Bloco | Status | Observação |
|---|---|---|
| **A · Porta de entrada** (01–07) | ✅ completo | inclui projeto-modelo executável e testado |
| **B · Núcleo** (10–65) | ✅ completo | 24 documentos |
| **C · Prática e erros** (70–75) | ✅ completo | 14 labs, 28 armadilhas, 14 mitos |
| **D · Economia e ecossistema** (80–85) | ✅ completo | pesquisado na web em 02/09/2026 |
| **E · Fontes** (90–95 + glossário) | ✅ completo | edições e links conferidos |

**Total:** 35 documentos + projeto-modelo com 23 arquivos de código.

**Nada pendente.**

**O que envelhece e quando revisar:**

| Arquivo | Revisar quando |
|---|---|
| [03](03-instalacao.md) | a cada ~6 meses, ou ao mudar versão de Python/uv |
| [65](65-estado-da-arte.md) | a cada ~3 meses (é o que envelhece mais rápido) |
| [80](80-custos-e-licencas.md) | a cada ~6 meses (preços e câmbio) |
| [85](85-cursos-e-certificacoes.md) | a cada ~12 meses (links expiram) |
| [05](05-manual-de-uso.md) | a cada versão maior do Streamlit |
| [75](75-armadilhas.md) §24 | quando o defeito do `date_input` for corrigido |

---

*Última atualização: 02/09/2026 · Streamlit 1.63.0*
