# 02 · Pré-requisitos

> **Nível:** iniciante · **Atualizado em:** 13/08/2026

Este arquivo responde: *o que preciso saber, ter e quanto tempo vai levar de verdade.*
Nada de otimismo de folheto.

---

## 1. Conhecimento

### Indispensável

| O que | Por quê | Onde aprender |
|---|---|---|
| **Usar o terminal** — `cd`, `ls`, `cat`, entender caminho relativo e absoluto | Claude Code **é** um programa de terminal. Sem isso você não abre a porta. | [Linux Journey — Command Line](https://linuxjourney.com/lesson/the-shell) (EN, grátis); [Curso em Vídeo — Linux, aulas 1–8](https://www.youtube.com/playlist?list=PLHz_AreHm4dlKP6QQCekuIPky1CiwmdI6) (PT) |
| **Git básico** — `status`, `diff`, `commit`, `branch`, desfazer | O agente edita seus arquivos. Sem git você não vê o que ele fez nem volta atrás. **Este é o item que mais dói faltar.** | [Pro Git, cap. 1–3](https://git-scm.com/book/pt-br/v2) — grátis e em português |
| **Ler código de alguma linguagem** | Você precisa julgar o que o agente entrega. Não precisa escrever bem; precisa **avaliar**. | qualquer linguagem serve |
| **Saber o que é um teste automatizado** | É o mecanismo que faz o agente se corrigir sozinho. Sem isso você perde metade do valor. | [`../testes-automatizados/00-MAPA.md`](../testes-automatizados/00-MAPA.md) — nesta mesma pasta |

### Ajuda muito

| O que | Por quê |
|---|---|
| Editar `JSON` sem errar vírgula | Toda a configuração é JSON. Vírgula sobrando quebra em silêncio. |
| Shell script básico (`bash`) | Hooks são scripts. Dá para copiar os prontos, mas entender rende muito ([`17`](17-hooks.md)). |
| Noção de HTTP e API | Ajuda a entender MCP e o projeto-modelo ([`../apis/00-MAPA.md`](../apis/00-MAPA.md)). |
| Docker | Para isolar o agente e para o caminho "sem instalar nada" ([`../docker/00-MAPA.md`](../docker/00-MAPA.md)). |
| Inglês de leitura | A documentação oficial é em inglês e muda semanalmente. Tradução automática resolve, mas atrasa. |

### Explicitamente **não** é pré-requisito

- Saber programar bem. Muita gente usa Claude Code para aprender a programar.
- Entender machine learning, transformers, redes neurais. Nada disso é necessário para
  usar bem. É necessário para o [`60-teoria-avancada.md`](60-teoria-avancada.md), e só.
- Ter uma máquina potente. O modelo roda nos servidores da Anthropic, não na sua.

---

## 2. Ambiente

| Item | Mínimo | Recomendado | Observação |
|---|---|---|---|
| **Sistema operacional** | macOS 11+, Ubuntu 20.04+/Debian 10+, Windows 10+ | qualquer um dos três atualizado | No Windows, **WSL2 é o caminho recomendado** ([`03`](03-instalacao.md)) |
| **RAM** | 4 GB | 8 GB+ | O peso é o seu editor e seus testes, não o Claude Code |
| **Disco** | ~500 MB para o binário e caches | 2 GB folgados | Sessões e transcrições acumulam em `~/.claude/` |
| **Rede** | conexão estável | — | **Não funciona offline.** Todo turno é uma chamada de rede |
| **Node.js** | só se instalar via npm (20.6+) | instale pelo binário nativo, que dispensa Node | Ver [`03`](03-instalacao.md) |
| **Terminal** | qualquer um | um com suporte a cores e teclas Alt/Option | iTerm2, Windows Terminal, GNOME Terminal, Ghostty |
| **git** | 2.x | — | Não é obrigatório, mas usar sem git é imprudência |

### Conta e pagamento

Você precisa de **uma** destas:

| Caminho | Custo | Cartão obrigatório? |
|---|---|---|
| Assinatura Claude Pro | US$ 20/mês | Sim |
| Assinatura Claude Max | a partir de US$ 100/mês | Sim |
| Chave de API (Claude Console) | por uso (pré-pago) | Sim |
| Amazon Bedrock / Google Cloud / Microsoft Foundry | conta do provedor | Sim (do provedor) |

> **Não existe camada gratuita permanente do Claude Code.** O plano Free do claude.ai lista
> "Claude Code incluído" na página de preços, mas com limites de uso muito apertados — na
> prática você esbarra neles em minutos de uso agêntico. Trate como demonstração, não como
> caminho de trabalho. Detalhes e alternativas em [`80-custos-e-licencas.md`](80-custos-e-licencas.md).

---

## 3. Tempo realista até cada nível

Escrito por alguém que já viu muita gente subir essa escada. As faixas assumem **uso real
em trabalho**, não estudo isolado.

| Nível | O que você consegue fazer | Tempo com dedicação diária | Tempo com uso ocasional |
|---|---|---|---|
| **Instalado e rodando** | primeira pergunta respondida, primeira edição aceita | 30–60 min | 1 dia |
| **Usuário funcional** | tarefas pequenas do dia a dia, sabe interromper e corrigir rumo | 1 semana | 3–4 semanas |
| **Usuário competente** | `CLAUDE.md` que funciona, permissões ajustadas, plan mode, sabe quando **não** usar | 3–4 semanas | 2–3 meses |
| **Profissional** | hooks, skills, subagentes, controle de contexto, custo sob controle, automação em CI | 3–4 meses | 8–12 meses |
| **Referência do time** | define a configuração da organização, ensina, mede resultado, escolhe onde não vale | 8–12 meses | difícil sem uso intenso |

**O gargalo não é o Claude Code — é o seu repositório.** Em projeto com testes rápidos,
convenções escritas e build de um comando, um profissional se forma em semanas. Em projeto
sem teste, com build de 20 minutos e nenhuma convenção, a mesma pessoa leva um ano e
reclama da ferramenta. Isto não é opinião polêmica: é o padrão que se repete em toda
adoção que dá certo ou errado.

---

## 4. Rota de resgate — se faltar um pré-requisito

| Falta | O que fazer agora, sem travar |
|---|---|
| **Nunca usei terminal** | Faça o mínimo: abra o terminal, `cd` até uma pasta, `ls`. Isso já basta para o [`04`](04-como-comecar.md). O resto se aprende usando — inclusive perguntando ao próprio Claude Code. |
| **Não sei git** | Aprenda **só três comandos hoje**: `git init`, `git add -A && git commit -m "antes do claude"`, `git diff`. Isso já te dá o botão de desfazer. O resto depois. |
| **Não posso instalar nada na máquina** | Use [Claude Code na web](https://claude.ai/code) ou GitHub Codespaces — roda no navegador, nada instalado. Ver [`03`](03-instalacao.md), seção "Sem instalar nada". |
| **Não tenho como pagar** | Comece pelo conceitual: leia [`10`](10-fundamentos.md), [`12`](12-anatomia-de-uma-sessao.md) e [`25`](25-o-oficio-do-profissional.md). São transferíveis para qualquer agente de código, inclusive os de código aberto listados em [`80`](80-custos-e-licencas.md). |
| **Meu projeto não tem teste** | Este é o pré-requisito mais importante e o mais ignorado. Ironia útil: peça ao Claude Code para escrever os primeiros testes. É uma das coisas que ele faz melhor. |
| **Não sei ler JSON** | Copie os exemplos deste curso, mude um valor por vez e rode `npm run verificar` do projeto-modelo, que aponta o erro. |
| **Não sei inglês** | O curso todo está em português. Para a documentação oficial, use tradução do navegador — o vocabulário técnico já está definido no [`GLOSSARIO.md`](GLOSSARIO.md). |

---

## 5. Checagem antes de seguir

Rode isto. Se as quatro primeiras linhas responderem, você está pronto para o [`03`](03-instalacao.md).

```bash
uname -s          # Linux | Darwin (macOS) | MINGW*/MSYS* (Git Bash no Windows)
echo "$SHELL"     # /bin/bash, /bin/zsh, ...
git --version     # git version 2.x
pwd               # e você entende o que este caminho significa
node --version    # opcional: só importa se for instalar via npm
```

Saída real desta máquina, em 13/08/2026:

```
Linux
/bin/bash
git version 2.34.1
/home/ronivaldo/ronidomingues/workspace/gitshared/homelab/learn-process
v24.18.0
```

---

## Autoteste

1. Qual é o único pré-requisito de conhecimento cuja ausência realmente te machuca no primeiro dia, e por quê?
2. Por que este material insiste que testes automatizados são pré-requisito, e não "bom ter"?
3. Existe camada gratuita permanente do Claude Code? Responda com a ressalva correta.
4. Quanto tempo, honestamente, até o nível "profissional"? O que mais influencia essa estimativa?
5. Você não pode instalar nada na máquina do trabalho. Qual é a rota?
6. Por que a potência da sua máquina é quase irrelevante aqui?
7. Seu projeto não tem nenhum teste. Qual é o primeiro movimento?
