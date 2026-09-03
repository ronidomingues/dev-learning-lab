# 23 · Ciclo de vida: versionar, promover, migrar

`Nível: avançado` · `01/09/2026`

---

Um workflow é software em produção. Este arquivo é sobre tratá-lo como tal.

---

## 1. Save × Publish (a mudança do n8n 2.0)

| | n8n 1.x | n8n 2.0+ |
|---|---|---|
| `Save` num fluxo ativo | **atualizava a produção na hora** | guarda o rascunho |
| Publicar | não existia como ato separado | **`Publish`** promove a versão salva |

*Por que mudou?* Porque um botão servia a duas intenções ("guardar meu trabalho" e
"colocar no ar"), e era trivial publicar uma edição pela metade sem perceber.
É uma correção de design tardia e correta.

Pela CLI (verificado em 2.36.9):

```bash
n8n publish:workflow   --id=<id>     # publica
n8n unpublish:workflow --id=<id>     # despublica
n8n update:workflow                  # [DEPRECADO] — não use
```

> **Pegadinha confirmada na prática:** a CLI avisa
> *"Changes will not take effect if n8n is running. Please restart n8n"*.
> Publicar por CLI **exige reiniciar** para que os webhooks sejam registrados.

---

## 2. Ambientes

O ideal — desenvolvimento, homologação, produção — esbarra numa realidade: o
recurso oficial de **Environments** (com *source control* Git) é **licenciado**.

### 2.1 Com licença

*Settings → Source control*: você conecta um repositório Git, cada instância aponta
para um branch, e o fluxo é `push` na dev → `pull` na produção. Existem
**variáveis por ambiente** (`$vars`), o que evita `if ambiente === 'prod'` espalhado.

### 2.2 Sem licença (o que a maioria faz)

Funciona, dá trabalho e é honesto:

```bash
# --- na instância de desenvolvimento ---
docker compose exec n8n n8n export:workflow --all --separate --output=/home/node/.n8n/exp
docker compose cp n8n:/home/node/.n8n/exp ./workflows
git add workflows && git commit -m "fluxo de cobrança: trata 429"

# --- na instância de produção ---
git pull
docker compose cp ./workflows n8n:/tmp/wf
docker compose exec n8n n8n import:workflow --separate --input=/tmp/wf
docker compose exec n8n n8n publish:workflow --id=<id>
docker compose restart n8n
```

**Os quatro problemas desse caminho, e o que fazer:**

| Problema | Contorno |
|---|---|
| Credenciais não vão junto (e ainda bem) | Crie uma vez em cada ambiente com **o mesmo id e nome**; assim o JSON do workflow casa |
| IDs de workflow precisam bater | Fixe o `id` no JSON exportado (é o que o [projeto-modelo](07-projeto-modelo/workflows/) faz) |
| Valores por ambiente (URLs, chaves) | Use `$env` (se permitido) ou uma tabela/Data Table de configuração lida no início do fluxo |
| Ninguém revisa diff de JSON de workflow | Escreva no commit **o que** mudou; o diff sozinho é ilegível |

> **Truque que funciona bem:** um workflow `config-ambiente` que devolve um item com
> as URLs e parâmetros daquele ambiente, chamado como sub-workflow pelos demais.
> Só ele muda entre ambientes; os outros ficam idênticos.

---

## 3. Workflow history

Recurso de histórico interno (versões anteriores do fluxo, com restauração).
Retenção controlada por `N8N_WORKFLOW_HISTORY_PRUNE_TIME` e afins; a **profundidade
depende do plano** (na prática, alguns dias na base e mais nos planos pagos).

Serve para "ontem funcionava". **Não substitui Git**: não tem branch, revisão,
mensagem de commit nem relação com o resto do seu código.

---

## 4. Pacotes `.n8np` (n8n 2.x)

Formato oficial para exportar **um conjunto** — workflows, pastas ou um projeto
inteiro — resolvendo dependências de sub-workflow. Na importação, o n8n reconcilia
credenciais, variáveis, data tables, tags, pastas e projetos.

Útil para migrar de instância ou entregar uma solução pronta a um cliente. Há
limites de tamanho e requisitos de licença por recurso — veja
[Limits and permissions](https://docs.n8n.io/build/manage-workflows/n8n-packages/limits-and-permissions.md).

---

## 5. Atualizar o n8n com segurança

```bash
# 1) BACKUP (banco + chave). Sem exceção.
# 2) leia as notas de versão entre a sua e a alvo
# 3) teste numa instância paralela apontando para uma CÓPIA do banco
docker run -d --name n8n-teste -p 5679:5678 -v n8n_teste:/home/node/.n8n n8nio/n8n:2.38.1
# 4) só então:
docker compose pull && docker compose up -d
```

**Regra de ouro:** as migrações de banco do n8n vão **só para frente**. Um volume
tocado por uma versão nova não volta para a antiga. Rollback = trocar a imagem
**e restaurar o banco**.

### Migrações grandes

| Salto | Ferramenta | Principais quebras |
|---|---|---|
| **1.x → 2.0** | [v2.0 Migration tool](https://docs.n8n.io/changelog/v20-migration-tool) — varre a instância e aponta incompatibilidades | Pyodide removido; binário em memória removido; `sqlite-pooled` padrão; `Save`≠`Publish`; parser de `.env` mudou (crase, multilinha) |
| **2.x → 3.0** (out/2026) | anunciada | **npm/npx deixa de existir**; Function/Function Item/Item Lists removidos; AI Agent v1 removido; `$getPairedItem` removido; Chat Hub removido; import por URL removido; rotação de chave ligada por padrão; limites de compressão reduzidos (2 GiB→256 MiB; 5.000→1.000 entradas) |

**O que fazer hoje, se você está em 1.x ou 2.x:**

1. Se instalou por **npm**, planeje a migração para Docker **agora**.
2. Procure nós **Function**, **Function Item** e **Item Lists** e troque por
   **Code**, **Split Out**/**Aggregate**/**Sort**/**Limit**/**Remove Duplicates**.
3. Procure `$getPairedItem` e troque por `$('nó').item` / `itemMatching()`.
4. Procure agentes de IA em modos antigos (Conversational, ReAct, Plan-and-Execute,
   OpenAI Functions, SQL) e migre para o AI Agent atual.
5. Se algum fluxo descomprime arquivo grande, meça: os limites caem no 3.0.

---

## 6. Testar workflows

O n8n tem recursos de **avaliação** (*evaluations*), pensados para fluxos de IA mas
úteis em geral: casos de teste com entradas e saídas esperadas, métricas e execução
em paralelo (com limite de concorrência próprio por plano).

Sem isso, o que dá para fazer hoje:

| Técnica | Como |
|---|---|
| **Pin data** | Congela a entrada; o fluxo passa a ser determinístico |
| **`n8n execute --id=<id>`** | Executa pela CLI; bom para CI |
| **`n8n execute-batch`** | Vários fluxos de uma vez — teste de regressão |
| **Fluxo de teste** | Um workflow que chama os outros com entradas conhecidas e compara |
| **Teste de fora** | Script `curl` contra os webhooks — é o que o [projeto-modelo](07-projeto-modelo/scripts/testar.sh) faz |

> **Recomendação:** para fluxo que importa, escreva um script de teste externo. Ele
> sobrevive a mudanças internas do n8n, roda em CI e não depende da interface.

---

## 7. Documentar o fluxo

Ferramentas que existem e quase ninguém usa:

- **Sticky notes** (`Shift+S`): caixas de texto no canvas. Explique o **porquê**,
  não o **o quê** — o "o quê" já está nos nós.
- **Renomear nós** com nomes de negócio: `Buscar cliente no CRM` em vez de `HTTP Request1`.
  (Renomeie **antes** de escrever expressões — ver [13](13-expressoes.md).)
- **Notes** por nó, com *Display note in flow*.
- **Tags** e **pastas** para organizar a lista.
- Um sticky no canto com: dono, o que dispara, o que acontece se falhar, quem avisar.

---

## Autoteste

1. O que mudou entre `Save` e `Publish` do 1.x para o 2.0, e por quê?
2. Qual pegadinha existe ao publicar pela CLI?
3. Sem licença, como versionar workflows em Git? Cite os quatro problemas.
4. Por que fixar o `id` no JSON exportado?
5. Qual truque evita `if ambiente === 'prod'` espalhado pelos fluxos?
6. Workflow history substitui Git? Justifique.
7. Por que rollback de versão exige restaurar o banco?
8. Cite cinco quebras anunciadas do n8n 3.0.
9. Quais cinco ações tomar hoje para se preparar para o 3.0?
10. Qual forma de teste sobrevive melhor a mudanças internas do n8n, e por quê?

---

*Anterior: [22-seguranca.md](22-seguranca.md) · Próximo: [24-ia-e-agentes.md](24-ia-e-agentes.md)*
