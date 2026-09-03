# 02 · Pré-requisitos

`Nível: iniciante` · `Última atualização: 11/08/2026`

O que você precisa **saber**, **ter** e **decidir** antes de abrir o
[03-instalacao.md](03-instalacao.md).

---

## 1. Conhecimento

### Indispensável

| Pré-requisito | Por que | Onde aprender |
|---|---|---|
| **Usar um terminal** — abrir, rodar comandos, ler erros | O `psql` e a administração vivem no terminal | [Linux Journey — Command Line](https://linuxjourney.com/lesson/the-shell) · [Curso em Vídeo Linux (PT)](https://www.youtube.com/playlist?list=PLHz_AreHm4dlKP6QQCekuIPky1CiwmdI6) |
| **Noção de "linhas e colunas"** — já ter usado uma planilha | É o modelo mental de partida de uma tabela | Qualquer experiência com Excel/Sheets basta |
| **Ler e escrever um arquivo de texto** | Scripts SQL são arquivos de texto | Qualquer editor |

### Ajuda muito (mas dá para começar sem)

| Pré-requisito | Onde aparece | Rota de resgate |
|---|---|---|
| **Lógica básica** (E, OU, verdadeiro/falso) | Cláusulas `WHERE`, condições | Aparece naturalmente; explicado no material |
| **Alguma linguagem de programação** | Para conectar uma aplicação ao banco | Não bloqueia: você aprende SQL puro primeiro, no `psql` |
| **Noção de rede** (host, porta, `localhost`) | Conectar cliente ao servidor | Explicado do zero em [03](03-instalacao.md) e [17](17-arquitetura-interna.md) |
| **Fundamentos de conjuntos** (união, interseção) | JOINs e operações de conjunto | Ajuda a intuir; não é pré-requisito formal |
| **Git** | Versionar scripts de esquema e migrações | Aprenda o mínimo quando chegar a migrações |

### O que **não** é pré-requisito (apesar do que dizem)

- **Matemática avançada.** A teoria por trás é elegante, mas você usa o banco sem ela. A teoria
  está no [60-teoria-avancada.md](60-teoria-avancada.md), para quem quiser.
- **Saber administrar servidor Linux.** Para *aprender e desenvolver*, não. Para *operar em
  produção*, sim — e isso é o [21-administracao-e-operacao.md](21-administracao-e-operacao.md).
- **Modelagem de dados formal (normalização).** Você aprende fazendo; a teoria vem depois, em
  [12-modelo-relacional-e-sql.md](12-modelo-relacional-e-sql.md).

---

## 2. Ambiente

### Hardware — mínimo real

| Recurso | Mínimo | Confortável | Observação |
|---|---|---|---|
| **CPU** | 1 núcleo | 2+ | Para aprender, qualquer máquina serve |
| **RAM** | 1 GB livre | 4 GB+ | O Postgres é econômico; um banco de estudo cabe em pouca RAM |
| **Disco** | 1 GB | 10 GB+ | O binário é pequeno (~50 MB); o espaço é para os seus dados |
| **Arquitetura** | x86-64 ou ARM64 | — | Roda em Raspberry Pi tranquilamente |

O PostgreSQL roda confortavelmente em hardware modesto. Um Raspberry Pi hospeda um banco de
homelab sem problema. As exigências reais aparecem só quando você tem muitos dados e muitos
usuários simultâneos — assunto de produção, não de aprendizado.

### Sistema operacional

| SO | Situação | Recomendação |
|---|---|---|
| **Linux** | Ambiente nativo e mais comum em produção | Melhor para aprender "como é de verdade" |
| **macOS** (Intel/Apple Silicon) | Muito bem suportado | Ótimo; via Homebrew ou Postgres.app |
| **Windows** | Suportado, com instalador gráfico | Funciona bem; ou use WSL2 para um ambiente Linux |
| **Container (Docker)** | O jeito mais rápido de subir e descartar | **Recomendado para experimentar**; ver [03](03-instalacao.md) |

> **Dica que economiza tempo:** se você já sabe um pouco de Docker (há um curso inteiro em
> [`../docker`](../docker/00-MAPA.md)), subir um PostgreSQL descartável é um comando só —
> `docker run` — e você não suja a máquina. É o caminho mais rápido para começar hoje.

### Contas e serviços

**Nenhuma conta é obrigatória.** O PostgreSQL é software livre que você baixa e roda. Contas só
entram se você optar por um serviço gerenciado na nuvem (Neon, Supabase, RDS…) — todas com camada
gratuita, detalhadas em [80-custos-e-licencas.md](80-custos-e-licencas.md). **Sem cartão de
crédito** para a maioria das camadas gratuitas de estudo (verificado em 11/08/2026; confirme).

---

## 3. Decisão que você toma antes de instalar

Há quatro caminhos para ter um PostgreSQL. Escolher errado custa retrabalho:

| Caminho | Esforço | Melhor para |
|---|---|---|
| **Nuvem gratuita** (Neon, Supabase) | mínimo — só criar conta | Começar em 2 minutos, sem instalar nada |
| **Docker** | baixo — um comando | Experimentar, descartar, ter várias versões |
| **Instalar no SO** | médio | Aprender administração de verdade; produção num servidor |
| **Playground online** | zero | Testar uma query SQL isolada, sem persistência |

**Recomendação:** para *aprender SQL*, comece num playground online ou numa nuvem gratuita hoje
mesmo. Para *aprender a operar o banco* (o que este curso também cobre), instale localmente ou use
Docker. Você provavelmente vai fazer os dois ao longo do caminho.

---

## 4. Tempo realista de estudo

Números honestos, com prática. "SQL em 1 hora" ensina `SELECT`, não SQL.

| Nível | O que você consegue fazer | Tempo realista |
|---|---|---|
| **Sobrevivência** | Criar tabela, inserir, consultar com `WHERE`, `ORDER BY` | **3–6 horas** |
| **Produtivo** | JOINs, agregações (`GROUP BY`), subconsultas, modelar um esquema simples | **20–40 horas** (2 a 4 semanas) |
| **Competente** | Índices, transações, `EXPLAIN`, tipos ricos (JSONB), funções, boa modelagem | **80–150 horas** (2 a 4 meses) |
| **Administração** | Backup, replicação, tuning, segurança, monitoramento em produção | **200–400 horas** (6 meses a 1 ano com produção real) |
| **Interno / especialista** | MVCC a fundo, planejador, extensões em C, contribuir com o projeto | **500+ horas** e trabalho no assunto |

**A cicatriz que ninguém conta:** o salto difícil não é aprender SQL — é **modelar bem** (decidir
quais tabelas e relações criar) e **operar em produção** (backup que funciona, não perder dado,
lidar com o `VACUUM`). SQL você aprende rápido; essas duas competências separam quem "usa banco"
de quem "cuida de banco".

---

## 5. Rota de resgate — falta um pré-requisito

| O que falta | Rota mais curta |
|---|---|
| **Nunca usei terminal** | Faça 2h de linha de comando básica antes. Ou comece por uma interface gráfica (pgAdmin, DBeaver) e migre ao terminal depois |
| **Máquina fraca / não posso instalar** | Nuvem gratuita ([Neon](https://neon.com), [Supabase](https://supabase.com)) ou playground ([db-fiddle](https://www.db-fiddle.com)). Zero instalação |
| **Não sei programar** | Não bloqueia. Aprenda SQL puro no `psql` primeiro; conectar uma aplicação vem muito depois |
| **Windows sem permissão de admin** | Nuvem gratuita, ou PostgreSQL portátil, ou o `postgres` dentro do WSL2 |
| **Não sei modelar** | Comece copiando esquemas prontos ([06-exemplos.md](06-exemplos.md), [07-projeto-modelo/](07-projeto-modelo/README.md)) e entenda-os. Modelagem se aprende por imitação antes de teoria |
| **Termos em inglês me travam** | Todo termo é traduzido na primeira ocorrência aqui e no [GLOSSARIO.md](GLOSSARIO.md) |

---

## 6. Checklist antes de seguir

```bash
# 1. Terminal responde
echo "ok"
# esperado: ok

# 2. Você sabe onde está
pwd
# esperado: um caminho absoluto

# 3. Há disco livre
df -h .
# esperado: alguns GB em "Avail"

# 4. (Opcional) Docker disponível, se for esse o caminho escolhido
docker --version 2>/dev/null || echo "sem docker — use instalação nativa ou nuvem"
```

Não há muito a conferir: o PostgreSQL é leve e sem pré-requisitos exóticos. Siga para
[03-instalacao.md](03-instalacao.md).

---

## Autoteste

1. Por que "matemática avançada" **não** é pré-requisito para usar PostgreSQL, apesar da teoria
   relacional ser matemática?
2. Qual é o caminho mais rápido para escrever sua primeira query SQL hoje, sem instalar nada?
3. Qual é o salto de aprendizado realmente difícil — e por que não é aprender SQL?
4. Você tem uma máquina fraca e não pode instalar nada. Cite duas rotas de resgate.
5. Quanto tempo, realisticamente, até você modelar um esquema simples e fazer JOINs com
   confiança?
6. Para *aprender SQL* e para *aprender a operar o banco*, os caminhos de instalação recomendados
   são os mesmos? Justifique.
