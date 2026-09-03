# 95 · Referências — fontes primárias

**Nível:** todos · **Verificado em: 20/08/2026**

> Só fontes primárias e verificáveis. Nenhum agregador, nenhum "top 10 de 2026".
> **Razão explícita:** durante a pesquisa deste curso, sites agregadores
> afirmaram que o Gemini CLI havia sido descontinuado (falso — o repositório
> oficial está ativo, com releases semanais) e publicaram tabelas de benchmark
> com números que não batem com as fontes originais. Muito desse conteúdo é
> gerado por IA e não verificado. **Vá à fonte.**

---

## 1 · Estudos e medições

| Fonte | O que traz | Link |
|---|---|---|
| **METR — Time Horizons** | Horizonte temporal por modelo; metodologia | https://metr.org/time-horizons/ |
| **METR — dados brutos v1.1** | YAML com horizonte 50%/80% por modelo e data | https://metr.org/assets/benchmark_results_1_1.yaml |
| **METR — estudo de 2025** | O ensaio randomizado dos 19% mais lentos | https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ |
| **METR — paper** | *Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity* | https://arxiv.org/abs/2507.09089 |
| **METR — mudança de desenho (02/2026)** | Por que o experimento randomizado ficou inviável; resultados de fim de 2025 | https://metr.org/blog/2026-02-24-uplift-update/ |
| **DORA 2025** | *State of AI-assisted Software Development*; IA como amplificadora | https://dora.dev/dora-report-2025/ |
| **DORA — PDF** | Relatório completo | https://services.google.com/fh/files/misc/2025_state_of_ai_assisted_software_development.pdf |
| **DORA — ROI 2026** | Retorno vem do sistema organizacional | https://www.infoq.com/news/2026/05/dora-roi-ai-assisted-dev-report/ |
| **LinearB 2026 Benchmarks** | 8,1 M de PRs, 4.800 equipes, 42 países | https://linearb.io/resources/software-engineering-benchmarks-report |
| **GitClear — The Maintainability Gap** | 623 M de alterações; duplicação, refatoração, churn | https://www.gitclear.com/the_ai_code_quality_maintainability_gap |
| **Stack Overflow — trust gap** | 84% de uso, 29% de confiança | https://stackoverflow.blog/2026/02/18/closing-the-developer-ai-trust-gap/ |
| **Stack Overflow — survey 2025** | Dados completos | https://survey.stackoverflow.co/2025/ai |

---

## 2 · Especificações e padrões

| Fonte | Link |
|---|---|
| **AGENTS.md** — especificação oficial | https://agents.md/ |
| **Model Context Protocol** | https://modelcontextprotocol.io/ |
| **GitHub Spec Kit** | https://github.com/github/spec-kit |
| **Conventional Commits** | https://www.conventionalcommits.org/pt-br/ |
| **Semantic Versioning** | https://semver.org/lang/pt-BR/ |
| **ADR (Architecture Decision Records)** | https://adr.github.io/ |

---

## 3 · Documentação de ferramentas

| Ferramenta | Documentação | Código-fonte |
|---|---|---|
| **Claude Code** | https://code.claude.com/docs/ | proprietário |
| **Claude API** | https://platform.claude.com/docs/ | — |
| **OpenAI Codex** | https://developers.openai.com/codex | https://github.com/openai/codex |
| **GitHub Copilot** | https://docs.github.com/copilot | proprietário |
| **Gemini CLI** | — | https://github.com/google-gemini/gemini-cli (Apache 2.0, **ativo**) |
| **Aider** | https://aider.chat/ | https://github.com/Aider-AI/aider (Apache 2.0) |
| **Cursor** | https://docs.cursor.com/ | proprietário |
| **Windsurf** | https://docs.windsurf.com/ | proprietário |

---

## 4 · Segurança

| Fonte | O que traz | Link |
|---|---|---|
| **Microsoft Security** | RCE em frameworks de agente (05/2026) | https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks/ |
| **CSA — Slopsquatting** | Nota de pesquisa (19/04/2026) | https://labs.cloudsecurityalliance.org/research/csa-research-note-slopsquatting-ai-supply-chain-20260419-csa/ |
| **Trend Micro — Slopsquatting** | Quando agentes alucinam pacotes maliciosos | https://www.trendmicro.com/vinfo/us/security/news/cybercrime-and-digital-threats/slopsquatting-when-ai-agents-hallucinate-malicious-packages |
| **Snyk — Package hallucination** | Impacto e mitigação | https://snyk.io/articles/package-hallucinations/ |
| **OWASP Top 10 for LLM Applications** | Taxonomia de riscos | https://owasp.org/www-project-top-10-for-large-language-model-applications/ |
| **CVE-2025-32711 (EchoLeak)** | Exfiltração zero-clique no M365 Copilot | https://nvd.nist.gov/vuln/detail/CVE-2025-32711 |
| **CVE-2025-53773** | Injeção → RCE no GitHub Copilot | https://nvd.nist.gov/vuln/detail/CVE-2025-53773 |
| **CVE-2026-21520** | Injeção indireta no Copilot Studio | https://www.capsulesecurity.io/blog-post/shareleak-taking-the-wheel-of-microsofts-copilot-studio-cve-2026-21520 |
| **gitleaks** | Detecção de segredo | https://github.com/gitleaks/gitleaks |
| **Semgrep** | SAST | https://semgrep.dev/ |

---

## 5 · Papers

> Alguns identificadores abaixo vieram de resultados de busca e **não foram
> lidos na íntegra**. Estão listados como pistas de leitura, não como fonte
> citada — a distinção importa e este curso a faz explicitamente.

### Lidos / citados neste curso

| Referência | Onde é usado |
|---|---|
| Vaswani et al., *Attention Is All You Need*, 2017 — https://arxiv.org/abs/1706.03762 | [11-historia](11-historia.md) |
| Becker, Rush, Barnes, Rein, *Measuring the Impact of Early-2025 AI…*, 2025 — https://arxiv.org/abs/2507.09089 | [24](24-produtividade-o-que-diz-a-evidencia.md) |
| Liu et al., *Lost in the Middle*, 2023 — https://arxiv.org/abs/2307.03172 | [12](12-o-modelo-por-dentro.md) |
| Rice, H. G., *Classes of Recursively Enumerable Sets…*, 1953 | [60](60-teoria-avancada.md) |
| Brooks, F., *No Silver Bullet*, 1986 | [10](10-fundamentos.md), [11](11-historia.md) |
| Goodhart, C., 1975 (lei de Goodhart) | [60](60-teoria-avancada.md) |

### Pistas de leitura (não lidos na íntegra)

| Tema | Identificador |
|---|---|
| Impacto de `AGENTS.md` na eficiência de agentes | arXiv 2601.20404 |
| *Configuration Smells* em `AGENTS.md` | arXiv 2606.15828 |
| Aderência a instruções em arquivos de configuração de agente | arXiv 2605.10039 |
| Ferramentas assistidas por IA são imunes a injeção de prompt? | arXiv 2603.21642 |
| Isolamento, controle de acesso e TOCTOU em agentes de código | arXiv 2607.05743 |
| Governança guiada por especificação | arXiv 2605.01160 |

---

## 6 · Ferramentas citadas no curso

| Categoria | Ferramentas |
|---|---|
| **Verificação de segredo** | gitleaks · trufflehog |
| **Mutação** | mutmut · cosmic-ray (Python) · Stryker (JS/TS) · PIT (Java) · go-mutesting |
| **Propriedade** | hypothesis (Python) · fast-check (JS) · jqwik (Java) · proptest (Rust) |
| **Arquitetura** | import-linter (Python) · ArchUnit (Java) · dependency-cruiser (JS) |
| **Duplicação** | jscpd · PMD CPD · SonarQube |
| **Cobertura do diff** | diff-cover · Codecov · Coveralls |
| **Transformação determinística** | sed · comby · ast-grep · jscodeshift |
| **Contrato** | Pact · Spring Cloud Contract |
| **SAST** | Semgrep · CodeQL · Bandit · gosec |
| **Dependências** | Dependabot · Snyk · osv-scanner |
| **Ambiente** | fnm · nvm · mise · uv · pyenv · Docker · Podman |

---

## 7 · Assuntos relacionados nesta pasta

| Assunto | Quando ler |
|---|---|
| [engenharia-de-prompt](../engenharia-de-prompt/00-MAPA.md) | Para aprofundar prompt, avaliação e RAG |
| [agentes-de-ia](../agentes-de-ia/00-MAPA.md) | Para **construir** agentes, não usá-los |
| [claude-code](../claude-code/00-MAPA.md) | Manual profundo de uma ferramenta específica |
| [testes-automatizados](../testes-automatizados/00-MAPA.md) | **Pré-requisito.** O mais importante deste curso |
| [docker](../docker/00-MAPA.md) | Isolamento de agentes |
| [commits-assinados](../commits-assinados/00-MAPA.md) | Autoria verificável |
| [variaveis-de-ambiente-e-segredos](../variaveis-de-ambiente-e-segredos/00-MAPA.md) | Não vazar credencial |
| [ethical-hacking](../ethical-hacking/00-MAPA.md) | Fundamento de segurança ofensiva |
| [bert](../bert/00-MAPA.md) | Como modelos de linguagem funcionam por dentro |

---

## 8 · Como manter esta lista viva

| Arquivo | Reavaliar |
|---|---|
| [65-estado-da-arte](65-estado-da-arte.md) | A cada **3 meses** |
| [80-custos-e-licencas](80-custos-e-licencas.md) | A cada **3 meses**, ou a cada mudança de modelo de cobrança |
| [03-instalacao](03-instalacao.md) | A cada **6 meses**, ou a cada mudança de versão mínima |
| [85-cursos-e-certificacoes](85-cursos-e-certificacoes.md) | A cada **6 meses** |
| [24-produtividade](24-produtividade-o-que-diz-a-evidencia.md) | A cada relatório DORA / LinearB / GitClear |
| [22-seguranca](22-seguranca.md) | A cada CVE relevante de agente de codificação |

---

## Autoteste

1. Por que este arquivo lista apenas fontes primárias? Dê os dois exemplos
   concretos de falha de agregador citados no topo.
2. Onde estão os dados brutos de horizonte temporal da METR, e por que consultar
   o YAML é diferente de ler um resumo?
3. Qual é a diferença, nesta lista, entre "papers lidos/citados" e "pistas de
   leitura"? Por que a distinção importa?
4. Cite três CVEs de 2025–2026 relevantes para agentes de codificação e o que
   cada uma demonstrou.
5. Onde está a especificação do `AGENTS.md` e quem a mantém?
6. Qual ferramenta você usaria para: detectar segredo · medir mutação · verificar
   fronteira de arquitetura · medir duplicação · medir cobertura do diff?
7. Qual assunto desta pasta é pré-requisito deste curso, e por quê?
8. Com que frequência cada arquivo perecível deve ser reavaliado?

---

**Anterior:** [90-bibliografia](90-bibliografia.md) ·
**Próximo:** [GLOSSARIO](GLOSSARIO.md)
