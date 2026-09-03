# 24 · Relatório e comunicação — o produto que o cliente compra

`Nível: intermediário → obrigatório` · `Última atualização: 12/08/2026`

O acesso não é o entregável. O **relatório** é. Um pentest brilhante com relatório ruim é um
pentest ruim, porque o cliente não consegue agir. Este arquivo ensina a produzir o documento
que separa o profissional do entusiasta.

> "O relatório é a única parte do teste que o cliente lê inteira, guarda, mostra ao auditor e
> usa para decidir. Escreva-o como tal." — regra que vale a carreira.

---

## 1. Por que o relatório é o produto

- O cliente **não viu** você trabalhar. O relatório é a evidência de que o trabalho existiu.
- Quem **paga** (diretoria) não é quem **corrige** (dev/infra). O relatório precisa falar com
  os dois, em linguagens diferentes.
- É o documento que sobrevive ao teste: vai para auditoria (PCI, LGPD, ISO), para o próximo
  pentester (comparação), e para a defesa do cliente num incidente.
- Reproduzir e corrigir depende **inteiramente** da qualidade da descrição.

Lembre da distribuição de tempo de [`01`](01-introducao-leigo.md): documentação é ~25% da
profissão, mais do que "hackear". Não é acidente.

## 2. Anatomia de um relatório profissional

```
1. Sumário Executivo        (1–2 páginas, para quem DECIDE — sem jargão)
2. Escopo e Metodologia     (o que foi testado, como, quando, limitações)
3. Avaliação de Risco       (visão geral: quantos achados, por severidade)
4. Achados Técnicos         (o coração — um por vulnerabilidade)
5. Recomendações Priorizadas (o que fazer primeiro, e por quê)
6. Conclusão                (postura geral de segurança)
7. Anexos                   (evidências, comandos, ferramentas, glossário)
```

Um exemplo completo e executável está em
[`07-projeto-modelo/relatorio/relatorio-exemplo.md`](07-projeto-modelo/relatorio/relatorio-exemplo.md).

## 3. O Sumário Executivo — a parte mais importante e mais mal feita

**Público:** diretor, CISO, alguém que decide orçamento e **não é técnico**.
**Regra:** se ele lê só esta página, precisa entender **quão ruim é** e **o que fazer**.

O que **deve** ter:
- Uma frase sobre o que foi testado e por quê.
- O veredito em linguagem de negócio: "um atacante externo conseguiu acessar os dados de todos
  os clientes em 2 dias" — não "encontramos um IDOR no endpoint /api/faturas".
- A contagem por severidade e o risco de negócio (multa LGPD, fraude, parada).
- A recomendação de alto nível e a urgência.

O que **não** deve ter: jargão, nomes de ferramenta, CVEs, payloads. Isso é o corpo técnico.

**Erro clássico:** escrever o sumário executivo em "hackês". O diretor não sabe o que é
Kerberoasting; ele sabe o que é "R$ 50 milhões de multa". Traduza impacto técnico em impacto de
negócio. Esta tradução é a habilidade mais valiosa (e rara) da profissão.

## 4. O Achado Técnico — estrutura de cada um

Cada vulnerabilidade recebe um bloco com:

| Campo | Conteúdo |
|---|---|
| **ID e título** | `F-01 · IDOR em /api/conta` |
| **Severidade** | Crítica/Alta/Média/Baixa + score CVSS |
| **Descrição** | o que é a falha, em 2–3 frases |
| **Localização** | endpoint/host/parâmetro exato |
| **Reprodução** | passo a passo que **qualquer um** consegue repetir |
| **Evidência** | print, resposta HTTP, saída de comando |
| **Impacto** | o que um atacante consegue de verdade (em termos de negócio) |
| **Recomendação** | como corrigir, específico e acionável |
| **Referências** | CWE, OWASP, CVE, links |

**A seção de reprodução é sagrada.** Se o dev não consegue reproduzir, ele não corrige — e vai
questionar seu achado. Comandos exatos, valores exatos, ordem exata. Veja o padrão no
projeto-modelo.

**A recomendação precisa ser acionável.** "Melhore a segurança" é inútil. "Aplique verificação
de autorização por objeto na função X, derivando o id da sessão em vez do parâmetro" é
acionável. Sempre que possível, aponte o *como*, não só o *quê*.

## 5. Severidade e CVSS — com honestidade

CVSS ([`10`](10-fundamentos.md) §3) dá um score de 0 a 10. Use, mas com julgamento:
- Calcule cada achado na [calculadora oficial (FIRST)](https://www.first.org/cvss/calculator/).
- **Ajuste ao contexto do cliente.** Uma CVSS 9.8 num sistema interno isolado pode ser risco
  menor que uma 6.5 na borda com dado de cartão. Explique o ajuste — não maquie.
- Considere KEV e EPSS para priorizar (está sendo explorado? qual a chance?).
- **Não infle severidade** para impressionar. Inflar destrói sua credibilidade quando o cliente
  ou outro pentester revisa. Um relatório honesto com 3 achados reais vale mais que um com 30
  inflados.

## 6. A regra dos elos (priorização por cadeia)

Ataque real é uma cadeia ([`06`](06-exemplos.md) ex. 14). O relatório deve **mostrar a cadeia** e
priorizar por **elo**: qual correção, feita primeiro, quebra o caminho mais cedo e com menor
custo. Isso muda a conversa de "corrija estas 30 coisas" (o cliente paralisa) para "corrija
estas 3 primeiro, elas quebram os ataques mais graves" (o cliente age).

Uma tabela de "recomendação → achados que fecha → custo" (como no projeto-modelo) é o formato
que os melhores clientes adoram, porque conecta esforço a resultado.

## 7. Tom e escrita

- **Factual, não sensacionalista.** "Foi possível X" e não "Hackeamos vocês facilmente".
- **Construtivo, não acusatório.** O objetivo é melhorar, não humilhar a equipe do cliente.
- **Preciso.** Evite "pode ser possível que talvez" — teste e afirme, ou diga que não confirmou.
- **Sem culpar pessoas.** Reporte a falha do sistema, não o erro do fulano.
- **Revisado.** Erro de português num relatório caro mina a confiança em tudo. Releia.

## 8. A reunião de entrega (readout)

O relatório não termina em PDF. Há uma reunião:
- **Para executivos:** foque no sumário, no risco de negócio, na priorização. 20 minutos.
- **Para a equipe técnica:** ande pelos achados, tire dúvidas de reprodução, ajude a planejar
  a correção. Aqui você é aliado, não juiz.
- Prepare-se para ser **questionado**. "Isso não é explorável na nossa config" acontece — se
  você tem a evidência, mostre; se o cliente tem razão, ajuste com humildade. Credibilidade se
  ganha aqui.

## 9. Retest — fechar o ciclo

Um pentest sem retest é metade do trabalho. Depois que o cliente corrige, você **reverifica**:
- Confirma que cada achado foi corrigido de fato (não só "achamos que corrigimos").
- Verifica que a correção não abriu outra falha.
- Emite um relatório de retest (ou atualiza o original com o status de cada achado).

O projeto-modelo demonstra isto: a mesma bateria de testes roda contra a versão corrigida e
retorna **0/5**. Essa prova é o que fecha o contrato.

## 10. Os cinco porquês: por que relatório é tão subestimado?

**Por quê 1** — Por que iniciantes menosprezam o relatório?
Porque a parte "legal" é achar a falha; escrever parece burocracia.

**Por quê 2** — Por que parece burocracia se é o produto?
Porque a recompensa emocional está no achado (a descoberta, o "consegui"), não na escrita. O
incentivo psicológico interno desalinha do valor real entregue.

**Por quê 3** — Por que o valor real está na escrita, não no achado?
Porque uma falha que o cliente não entende nem corrige tem valor **zero** para ele. O achado só
vira valor quando comunicado de forma acionável. Segurança entregue = risco reduzido = correção
feita = relatório que permitiu a correção.

**Por quê 4** — Por que então o mercado não seleciona por qualidade de relatório?
Seleciona, mas com atraso: o cliente que compra "carimbo" (Motivo 3 de [`01`](01-introducao-leigo.md))
não valoriza o relatório de imediato — só descobre a diferença no incidente ou na auditoria.

**Por quê 5** — Qual é a parada?
Um **desalinhamento entre a recompensa imediata (o achado) e o valor entregue (a comunicação
que gera correção)**. Quem entende isso cedo — que o relatório *é* o trabalho, não o resumo
dele — se destaca, porque a maioria continua otimizando pela parte divertida. É a habilidade
que mais diferencia carreira, e a menos praticada. Domine o relatório e você será
desproporcionalmente valioso.

---

## Autoteste

1. Por que o relatório, e não o acesso, é o produto de um pentest?
2. Para quem é escrito o sumário executivo, e o que ele **não** deve conter?
3. Qual é o erro clássico do sumário executivo, e qual habilidade o corrige?
4. Cite os campos de um achado técnico. Qual é "sagrado" e por quê?
5. Por que **não** se deve inflar a severidade CVSS?
6. O que é a "regra dos elos" e como ela muda a conversa com o cliente?
7. O que é o retest e por que um pentest sem ele é metade do trabalho?
8. Por que o relatório é tão subestimado por iniciantes? Leve o porquê até o fim.
