# 80 · Custos, licenças e economia da profissão

`Nível: todos` · `Data de consulta dos preços: 12/08/2026`
`Câmbio de referência usado: US$ 1 ≈ R$ 5,40 (aproximado, agosto/2026). Valores em BRL são ordem de grandeza.`

Quanto custa entrar, quanto custam as ferramentas, quanto se ganha, e quem paga a conta do
ecossistema. **Todo preço tem data de consulta explícita** — preço sem data é desinformação.

---

## 1. O caminho 100% gratuito existe

Antes dos preços: **você pode se tornar empregável gastando R$ 0 em cursos e ferramentas.** O
único custo real é hardware e tempo. O que é grátis de verdade:

| Recurso | O que dá | Custo |
|---|---|---|
| Kali Linux, todas as ferramentas | ambiente ofensivo completo | grátis (open source) |
| PortSwigger Web Security Academy | 250+ labs web, o melhor material web | grátis |
| TryHackMe (camada free) / Hack The Box (máquinas ativas) | prática guiada | grátis |
| OverTheWire, picoCTF, Root-Me, VulnHub | fundamentos e desafios | grátis |
| Metasploitable, DVWA, Juice Shop, GOAD | alvos de laboratório | grátis |
| Documentação, write-ups, YouTube | teoria e casos | grátis |

O que se paga é **conveniência** (labs prontos, VPN, assinaturas) e **credencial** (certificações).
Nada disso é obrigatório para aprender — só acelera e comprova.

## 2. Ferramentas — preços (consulta 12/08/2026)

| Ferramenta | Licença | Preço | Alternativa gratuita |
|---|---|---|---|
| **Kali / Parrot / nmap / Metasploit Framework** | GPL/BSD (open source) | R$ 0 | — |
| **Burp Suite Community** | proprietária, gratuita | R$ 0 | é a versão grátis |
| **Burp Suite Professional** | proprietária | **US$ 499/ano/usuário** (~R$ 2.700) — reajuste global em 06/01/2026 | OWASP ZAP, Caido |
| **Caido** | proprietária, tem tier grátis | free + planos pagos | Community/ZAP |
| **Metasploit Pro** | proprietária | ~milhares/ano (cotação) | Framework (grátis) |
| **Cobalt Strike** (C2, red team) | proprietária | ~US$ 3.540+/ano/usuário | Sliver, Havoc (open source) |
| **Nessus Professional** (scanner) | proprietária | ~US$ 4.000+/ano | OpenVAS/Greenbone |
| **Shodan** | freemium | membership vitalícia em promoções ~US$ 5–49; API paga por uso | Censys (tier grátis) |

**Custo oculto das ferramentas:** o tempo de aprender. Burp Pro se paga na primeira semana de
trabalho web profissional (o Intruder sem limite e o Scanner economizam horas). Para **estudar**,
Community/ZAP bastam — a PortSwigger Academy inteira é resolvível com a Community.

## 3. Certificações — preços (consulta 12/08/2026)

Detalhes de valor de mercado e comparação em [`85-cursos-e-certificacoes.md`](85-cursos-e-certificacoes.md).
Aqui, só os números:

| Certificação | Fornecedor | Preço | Inclui | Reconhecimento |
|---|---|---|---|---|
| **eJPT** | INE | ~US$ 299 (~R$ 1.600) | 1 ano de material + voucher | entrada, bom |
| **PJPT** | TCM Security | ~US$ 299 | curso + exame + retake | entrada, prático |
| **PNPT** | TCM Security | **~US$ 499** (~R$ 2.700) | exame + retake vitalício + 12 meses de curso | crescente, muito respeitado |
| **HTB CPTS** | Hack The Box | **~US$ 210** exame (+ Academy: Silver ~US$ 490/ano inclui 1 voucher) | prático, 10 dias | alto e crescente, ótimo custo-benefício |
| **HTB CBBH/CWES** | Hack The Box | ~US$ 210 | web pentest | bom para web |
| **OSCP / OSCP+** | OffSec | bundle **~US$ 1.749** (curso 90 dias + 1 exame); promo pontual ~US$ 1.499 | PEN-200 + lab + exame | **o mais reconhecido pelo RH**, caro |
| **OSCP — Learn One** | OffSec | ~US$ 2.749/ano | 1 ano de treino + 2 tentativas | idem |
| **CEH** | EC-Council | voucher **~US$ 950–1.199** + US$ 100 taxa; treino oficial US$ 1.950–3.600 | teórico (v13) | popular em RH/gov, **caro e criticado** |
| **CompTIA Security+** | CompTIA | **US$ 439** (após aumento de jun/2026); ~US$ 373 via parceiro | fundamentos | base, exigido em muitas vagas/gov |
| **CompTIA PenTest+** | CompTIA | US$ 439 | pentest intermediário | reconhecido, menos que OSCP |
| **Burp Suite Certified (BSCP)** | PortSwigger | ~US$ 99 | prático web | alto valor para web, barato |

**Custos ocultos de certificação:**
- **Retake:** OSCP US$ 249/tentativa extra; CEH US$ 499; CompTIA compra novo voucher.
- **Manutenção:** CEH US$ 80/ano de membership; CompTIA exige CEUs ou renovação; OffSec/HTB não
  cobram anuidade para manter (as práticas não expiram).
- **Treino oficial:** no CEH, quem não tem 2 anos de experiência é **obrigado** a pagar o
  treino (US$ 1.950+) — custo escondido enorme.
- **Tempo:** OSCP consome centenas de horas. Tempo é o maior custo real.

## 4. Custo de montar o laboratório

| Item | Custo |
|---|---|
| Software (hipervisor, Kali, alvos) | R$ 0 (VirtualBox e VMware Workstation são gratuitos — ver [`03`](03-instalacao.md)) |
| Hardware: PC com 16 GB RAM + SSD | R$ 2.500–5.000 novo; bem menos usado |
| Upgrade de RAM (8→16 GB) numa máquina que você já tem | R$ 150–400 |
| Adaptador Wi-Fi USB com modo monitor (se for fazer wireless) | R$ 150–500 |
| VPS na nuvem (Kali remoto, opcional) | US$ 5–20/mês |
| **Alternativa sem hardware:** labs no navegador (THM/HTB) | assinatura opcional (§5) |

## 5. Assinaturas de plataformas de treino (consulta 12/08/2026)

| Plataforma | Plano | Preço |
|---|---|---|
| **TryHackMe** | Premium anual | ~US$ 100–126/ano (com desconto estudante ~US$ 8/mês) |
| **Hack The Box** | VIP+ (labs) anual | ~US$ 223/ano |
| **HTB Academy** | Silver anual (inclui voucher CPTS) | ~US$ 490/ano |
| **HTB Pro Labs** | anual | ~US$ 490/ano |
| **INE / Pentester Academy** | assinatura | planos variados |
| **PortSwigger Academy** | — | **grátis** |

Dica: promoções de Black Friday/Cyber Monday cortam 20–30%. Vale esperar por elas.

## 6. Quanto se ganha (Brasil e exterior, 2026)

> **Franqueza sobre os dados:** faixas salariais variam muito por região, senioridade, empresa
> e modelo (CLT × PJ × exterior). As fontes públicas (Glassdoor, Indeed) têm alta dispersão e
> inconsistência. Trate os números abaixo como **ordem de grandeza**, não promessa, e confira
> nas fontes citadas para a sua realidade.

**Mercado (fato):** a demanda por segurança cresce mais rápido que a oferta de profissionais
qualificados, no Brasil e no mundo. Muitas vagas de pentest são 100% remotas — inclusive para
empresas do exterior pagando em moeda forte, o que muda a economia da carreira para quem está
no Brasil.

| Faixa (ordem de grandeza, Brasil, CLT/PJ) | Papel |
|---|---|
| entrada de TI | SOC nível 1 / suporte (porta de entrada) |
| acima da média de TI | pentester júnior/pleno |
| entre os melhores de TI | pentester sênior, AppSec sênior, cloud security, red team |
| moeda forte | remoto para exterior (o "pulo do gato" salarial de quem está no Brasil) |

**Bug bounty (renda variável, dados globais das plataformas):**
- Pagamentos médios por falha: US$ 300–5.000, dependendo de severidade e programa; críticos em
  programas grandes chegam a cinco/seis dígitos.
- **Realidade honesta:** iniciantes podem ganhar US$ 500–2.000/mês *se* forem consistentes e
  bons; a maioria ganha pouco ou nada no começo. Top hunters passam de US$ 100 mil/ano, mas são
  exceção. Bug bounty é **complemento e treino**, não substituto de salário, até você ser muito
  bom. Microsoft pagou US$ 17 milhões a 344 pesquisadores em 2025 — muito dinheiro, muito
  concentrado em poucos.

## 7. O modelo econômico do mercado de pentest

Por que existe dinheiro aqui, e de onde vem:

1. **Regulação** (LGPD, PCI DSS, ISO 27001, CRA europeu) **obriga** teste. Este é o maior motor.
   PCI DSS 4.0 exige pentest anual — demanda garantida.
2. **Custo de incidente** > custo de teste. Um vazamento custa milhões (multa + reputação +
   parada); um pentest custa dezenas de milhares.
3. **Exigência de clientes/parceiros:** grandes empresas exigem relatório de pentest dos
   fornecedores. Parte da demanda é por documento (ver [`01`](01-introducao-leigo.md) §2, Motivo 3).

**Preço de um pentest para o cliente:** varia de dezenas a centenas de milhares de reais,
conforme escopo, duração e reputação do fornecedor. Um pentest web pequeno pode custar R$ 15–40
mil; um red team longo, muito mais.

## 8. Licenças — o que você pode e não pode

- **Ferramentas open source (Kali, nmap, Metasploit Framework, ZAP):** GPL/BSD/Apache. Uso
  comercial permitido. Você pode usar num pentest pago sem pagar licença.
- **Burp Pro, Nessus, Cobalt Strike:** proprietárias, licença por usuário/ano. Usar sem licença
  em trabalho comercial é violação (e pirataria de Cobalt Strike é rastreada e associada a
  crime — não faça).
- **Kali:** a distribuição é livre, mas o nome/logo têm marca registrada (OffSec) — não
  redistribua modificado usando a marca.
- **Wordlists e exploits:** geralmente livres; verifique a licença de cada um.
- **Cuidado com Cobalt Strike:** versões pirateadas são vetor de malware e sua posse levanta
  suspeita de atividade criminosa. Alternativas open source (Sliver, Havoc) existem.

## 9. Resumo: quanto custa começar, de verdade

| Cenário | Custo inicial | Custo mensal |
|---|---|---|
| **Mínimo absoluto** (PC que você já tem + tudo grátis) | R$ 0 | R$ 0 |
| **Confortável** (upgrade de RAM + TryHackMe) | R$ 300 | ~R$ 50 |
| **Sério** (PC dedicado + HTB + 1 certificação prática/ano) | R$ 3.000–5.000 | ~R$ 100–300 |
| **Certificação de peso** (OSCP no ano 2) | + US$ 1.749 (uma vez) | — |

**A conclusão honesta:** o dinheiro **não** é a barreira de entrada — o tempo é. Você pode ir
de zero a empregável gastando quase nada além de um computador razoável e ~2 anos de estudo
consistente. As certificações caras vêm depois, quando já fazem sentido, e muitas empresas as
pagam para você.

---

### Fontes consultadas (12/08/2026)
- OffSec (OSCP/PEN-200): [offsec.com](https://www.offsec.com) — bundle US$ 1.749; retake US$ 249
- TCM Security (PNPT/PJPT): [certifications.tcm-sec.com](https://certifications.tcm-sec.com) — PNPT US$ 499
- INE (eJPT): US$ 299
- Hack The Box (CPTS/Academy): [hackthebox.com](https://www.hackthebox.com) — exame US$ 210; Silver US$ 490/ano
- EC-Council (CEH): voucher US$ 950–1.199 + US$ 100 taxa; membership US$ 80/ano
- CompTIA (Security+/PenTest+): US$ 439 (aumento de jun/2026)
- PortSwigger (Burp Pro US$ 499/ano; reajuste 06/01/2026; BSCP US$ 99)
- Dados de mercado/salário: Glassdoor.com.br, Indeed.com.br (alta dispersão — verificar)
- Bug bounty: relatórios HackerOne/Bugcrowd/Intigriti/YesWeHack 2026

---

## Autoteste

1. É possível se tornar empregável gastando R$ 0 em cursos e ferramentas? O que se paga então?
2. Qual é a diferença de reconhecimento e preço entre OSCP, CPTS e PNPT?
3. Cite três custos **ocultos** de certificação.
4. Por que o CEH pode custar muito mais que o preço do voucher?
5. Qual é o maior motor econômico do mercado de pentest?
6. Por que bug bounty é "complemento e treino", não substituto de salário, no começo?
7. Qual é a verdadeira barreira de entrada da carreira: dinheiro ou tempo? Justifique.
8. Por que possuir uma versão pirateada de Cobalt Strike é problema além da questão de licença?
