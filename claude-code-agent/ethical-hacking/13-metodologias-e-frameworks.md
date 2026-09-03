# 13 · Metodologias e frameworks

`Nível: intermediário` · `Última atualização: 12/08/2026`

Improvisar não escala e não se defende num tribunal. Metodologia é o que garante cobertura
(você não esqueceu uma área), reprodutibilidade (outro faz igual) e comunicação (o cliente
sabe o que foi feito). Este arquivo é o mapa das metodologias reais que o mercado usa.

---

## 1. Por que seguir uma metodologia

Três razões concretas:
1. **Cobertura.** Sem checklist, você testa o que lembra e esquece o resto. Metodologia é
   memória externa.
2. **Defensabilidade.** "Segui a OWASP WSTG v4.2, seções X a Z" é uma afirmação auditável.
   "Testei umas coisas" não é.
3. **Comparabilidade.** O cliente consegue comparar dois testes e medir evolução ao longo do
   tempo.

Nenhuma metodologia substitui julgamento. Elas são o piso, não o teto.

## 2. As cinco fases (o esqueleto universal)

Independentemente do framework, todo teste segue esta lógica (vista no [`01`](01-introducao-leigo.md)):

```
1. Reconhecimento  → o que existe?        (14)
2. Varredura       → o que responde?      (15)
3. Exploração      → o que quebra?        (16)
4. Pós-exploração  → até onde vai?        (17)
5. Relatório       → o que fazer?         (24)
```

As metodologias abaixo detalham e formalizam essas fases.

## 3. PTES — Penetration Testing Execution Standard

O mais próximo de um "processo de pentest" completo. Sete fases:

| Fase | O que envolve |
|---|---|
| 1. **Pre-engagement** | escopo, RoE, contrato, autorização, objetivos |
| 2. **Intelligence Gathering** | OSINT, recon passivo e ativo |
| 3. **Threat Modeling** | quem atacaria, o que vale, por onde |
| 4. **Vulnerability Analysis** | identificar falhas exploráveis |
| 5. **Exploitation** | comprometer |
| 6. **Post-Exploitation** | impacto, persistência, movimentação, valor do alvo |
| 7. **Reporting** | o entregável |

**Por que gosto do PTES:** ele começa em *pre-engagement* — contrato e autorização são fase 1,
não pré-requisito esquecido. É a metodologia que melhor reflete o trabalho real de ponta a
ponta. Site: [pentest-standard.org](http://www.pentest-standard.org).

## 4. OWASP WSTG — Web Security Testing Guide

**A referência para teste web.** Um checklist enorme e versionado (v4.2 é a estável em 2026)
organizado por categoria: configuração, autenticação, autorização, gestão de sessão,
validação de entrada, tratamento de erro, criptografia, lógica de negócio, cliente, APIs.

Cada teste tem um identificador (ex.: `WSTG-ATHZ-02` para "Testing for Bypassing Authorization
Schema"). Você referencia esses códigos no relatório. Existe também o **OWASP MASTG** para
mobile e o **OWASP ASVS** (padrão de verificação, útil como critério de "passou/não passou").
Ver [`18`](18-seguranca-web.md).

## 5. NIST SP 800-115

Guia técnico do governo americano para *Information Security Testing and Assessment*. Menos
prescritivo que o PTES, mais "oficial". Quatro fases: Planning → Discovery → Attack →
Reporting. Útil quando o cliente é governo ou setor regulado e quer uma referência
institucional. O NIST também publica o **CSF (Cybersecurity Framework)**, que é de gestão, não
de teste — não confunda.

## 6. OSSTMM — Open Source Security Testing Methodology Manual

Metodologia rigorosa e científica de teste de segurança, com foco em **medir** (o conceito de
*RAV* — Risk Assessment Values). Denso, acadêmico, menos usado no dia a dia comercial que
PTES/WSTG, mas influente. Bom quando se quer métrica de segurança comparável ao longo do tempo.

## 7. MITRE ATT&CK — o dicionário de táticas e técnicas

**Não é uma metodologia de teste; é uma taxonomia de comportamento de adversário.** Cataloga o
que atacantes reais fazem, organizado em **táticas** (o "porquê", ex.: *Initial Access*,
*Privilege Escalation*, *Lateral Movement*, *Exfiltration*) e **técnicas** (o "como", com
identificadores como `T1078 – Valid Accounts`).

Usos:
- **Red team:** planejar operação mapeando o que vai emular.
- **Purple team:** medir se o blue detecta cada técnica (matriz de cobertura).
- **Relatório:** mapear cada achado a uma técnica ATT&CK dá linguagem comum com a defesa.

É a lingua franca entre ataque e defesa em 2026. Site: [attack.mitre.org](https://attack.mitre.org).

## 8. Cyber Kill Chain (Lockheed Martin)

Modelo mais antigo e linear das etapas de um ataque direcionado:

```
Reconnaissance → Weaponization → Delivery → Exploitation →
Installation → Command & Control (C2) → Actions on Objectives
```

**Uso e crítica:** ótimo para explicar a leigos e para pensar "onde eu quebro a cadeia".
Criticado por ser linear demais (ataques reais iteram e voltam) e focado em malware/perímetro.
O ATT&CK o superou em granularidade, mas a Kill Chain continua boa para comunicação executiva.

## 9. Como escolher — guia prático

| Situação | Use |
|---|---|
| Pentest completo de rede/infra | **PTES** como espinha |
| Teste de aplicação web/API | **OWASP WSTG** (+ ASVS como critério) |
| Cliente governo/regulado | **NIST SP 800-115** como referência |
| Red team / emulação de adversário | **MITRE ATT&CK** para planejar e reportar |
| Mobile | **OWASP MASTG** |
| Comunicação executiva do ataque | **Cyber Kill Chain** no slide, ATT&CK no anexo |
| Medir maturidade da defesa | **ATT&CK** (cobertura) + purple team |

**Na prática, você combina.** Um pentest web típico: PTES para a moldura de processo, WSTG para
a cobertura técnica, ATT&CK para mapear o que foi feito no relatório. Não são concorrentes; são
camadas.

## 10. Frameworks de gestão que você vai encontrar (mas não são de teste)

Para não confundir na conversa com o cliente:

- **NIST CSF** — framework de *gestão* de risco (Identify, Protect, Detect, Respond, Recover).
- **ISO/IEC 27001/27002** — sistema de gestão de segurança da informação (certificação de org.).
- **CIS Controls** — 18 controles priorizados de defesa. Ótimo para recomendação no relatório.
- **PCI DSS** — exigência do setor de cartões; **manda fazer pentest anual** (req. 11.4). Um
  dos maiores geradores de demanda por pentest no mercado.
- **MITRE D3FEND** — o "irmão defensivo" do ATT&CK, mapeando contramedidas.

## 11. Regra dos cinco porquês: por que padronizar num campo criativo?

**Por quê 1** — Se hacking é criativo, por que engessar com metodologia?
Porque criatividade sem cobertura esquece o óbvio. O bug que derruba a empresa costuma ser o
trivial que ninguém checou, não o genial.

**Por quê 2** — Por que o trivial escapa justamente de quem é bom?
Viés de competência: o especialista foca no interessante e pula o chato. A senha padrão, a
porta esquecida, o backup exposto — o "chato" é onde mora o incidente real.

**Por quê 3** — Por que não confiar só em ferramenta automática para o trivial?
Porque scanner acha o conhecido genérico, mas não a falha de lógica nem o contexto. E dá
falso-negativo silencioso: "não achou" não é "não existe".

**Por quê 4** — Então por que não só checklist, sem criatividade?
Porque checklist acha o previsto; o achado que ganha o contrato é o imprevisto (o endpoint de
PDF esquecido do Exemplo 13). Checklist garante o piso; criatividade busca o teto.

**Por quê 5** — Qual é a parada?
É um **trade-off estrutural**, não resolvível: metodologia dá cobertura reprodutível
(defensável, comparável), criatividade dá profundidade (o achado valioso). Bons testes fazem
os dois — checklist para não esquecer nada, tempo livre para caçar o inesperado. Quem só faz
um dos dois entrega teatro (só checklist) ou aposta (só criatividade).

---

## Autoteste

1. Cite as três razões concretas para seguir uma metodologia.
2. Por que o PTES começa em "pre-engagement", e por que isso importa?
3. Qual metodologia é a referência para teste de aplicação web, e como você a cita num relatório?
4. MITRE ATT&CK é uma metodologia de teste? Se não, o que é e para que serve?
5. Qual a crítica principal à Cyber Kill Chain, e para que ela ainda serve bem?
6. Qual norma **obriga** pentest anual e é grande geradora de demanda de mercado?
7. Por que combinar metodologia (checklist) e criatividade não é opcional, mas estrutural?
8. Diferencie NIST SP 800-115 (teste) de NIST CSF (gestão).
