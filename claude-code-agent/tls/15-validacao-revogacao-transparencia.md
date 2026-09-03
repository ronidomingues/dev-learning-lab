# 15 · Validação, revogação e transparência

**Nível:** avançado · **Data:** 31/08/2026

O capítulo que a indústria preferiria não ter. **Revogação de certificados nunca
funcionou direito**, e a resposta que prevaleceu em 2026 não foi consertá-la: foi
tornar os certificados tão curtos que a revogação deixe de importar.

---

## 1. O problema

Você emitiu um certificado válido por 90 dias. No dia 10, a chave privada vaza.
Como avisar o mundo inteiro que aquele certificado não vale mais?

Parece simples. Não é. Todo mecanismo proposto esbarra na mesma trinca:

1. **Disponibilidade** — se o cliente não conseguir consultar a lista, ele deve
   bloquear (e derrubar a internet quando a CA cair) ou seguir em frente
   (e a revogação vira decoração)?
2. **Privacidade** — perguntar à CA "este certificado ainda vale?" **revela à CA
   qual site você está visitando**, em tempo real.
3. **Escala** — são centenas de milhões de certificados ativos; distribuir e atualizar
   listas para bilhões de clientes é caro.

---

## 2. CRL — a lista de revogados

A CA publica periodicamente um arquivo assinado com os **números de série** revogados.

```bash
# ver uma CRL (a do projeto-modelo, gerada de verdade nesta máquina)
openssl crl -in 07-projeto-modelo/pki/ca.crl -noout -text | head -20
```

Saída real (trecho, 31/08/2026):

```
Certificate Revocation List (CRL):
        Version 2 (0x1)
        Signature Algorithm: ecdsa-with-SHA256
        Issuer: O = Cofre TLS, CN = Cofre TLS Root CA
        Last Update: Aug 31 19:43:09 2026 GMT
        Next Update: Sep  7 19:43:09 2026 GMT
        CRL extensions:
            X509v3 CRL Number:
                4096
Revoked Certificates:
    Serial Number: 377C08685C7BDF3C77A5C0BE6654C7A16FEDC327
        Revocation Date: Aug 31 19:43:09 2026 GMT
        CRL entry extensions:
            X509v3 CRL Reason Code:
                Key Compromise
```

Repare no `Next Update`: **uma semana**. Uma revogação feita hoje só chega a quem
consulta a CRL depois da próxima publicação. Esse atraso, aqui de 7 dias, é a essência
do problema — e em CAs públicas costumava ser da mesma ordem.

| Vantagem | Problema |
|---|---|
| simples, assinada, funciona offline | **tamanho**: CRLs de CAs grandes chegam a dezenas de MB |
| não vaza qual site você visita | **atraso**: `Next Update` costuma ser de dias — a revogação de hoje só vale amanhã |
| um download serve para muitos certificados | baixar dezenas de MB antes de abrir um site é inviável em rede móvel |

**Veredito:** navegadores **abandonaram** a CRL clássica há mais de uma década.
Continua útil em **PKI interna**, onde o número de certificados é pequeno e você
controla os clientes — é exatamente o uso do [projeto-modelo](07-projeto-modelo/README.md).

---

## 3. OCSP — perguntar sobre um certificado só

*Online Certificate Status Protocol* (RFC 6960): o cliente pergunta ao respondedor da
CA sobre **um** certificado, e recebe `good`, `revoked` ou `unknown`, assinado.

```bash
url=$(openssl x509 -in cert.pem -noout -ocsp_uri)
openssl ocsp -issuer cadeia.pem -cert cert.pem -url "$url" -no_nonce -text 2>&1 | grep -E "Cert Status|This Update"
# esperado: Cert Status: good
```

Resolveu o tamanho. Criou três problemas piores:

### 3.1 Privacidade

**O cliente informa à CA, em tempo real, qual site está visitando.** A CA — e quem
observar a rede, já que OCSP tradicionalmente roda em **HTTP em claro** — monta um
histórico de navegação. É o problema mais grave, e é de projeto.

### 3.2 Latência

Uma consulta HTTP extra, síncrona, antes de renderizar a página. Em rede móvel, pode
custar centenas de milissegundos.

### 3.3 *Soft-fail* — e este é o defeito fatal

Se a consulta OCSP falhar (rede ruim, respondedor fora do ar, portal cativo de Wi-Fi),
o que o navegador faz?

- **Hard-fail** (bloquear): uma queda do respondedor da CA derruba metade da web.
  Já aconteceu, e é inaceitável comercialmente.
- **Soft-fail** (seguir em frente): é o que **todos** fazem.

E aí a conclusão desconfortável, formulada por Adam Langley (Google) em 2012 numa
frase que ficou famosa no campo: **verificação de revogação em soft-fail é como um
cinto de segurança que arrebenta em qualquer batida**. Um atacante que consegue fazer
um MITM também consegue bloquear a consulta OCSP — é a mesma posição de rede.
Ou seja: **exatamente quando você precisaria da revogação, ela não funciona.**

---

## 4. OCSP stapling — a correção que também está saindo de cena

O servidor consulta o OCSP periodicamente e **anexa** (*staple*) a resposta assinada e
datada ao próprio handshake TLS.

```
handshake normal:  cliente → servidor (TLS)  +  cliente → CA (OCSP)   ← vaza, atrasa
com stapling:      cliente → servidor (TLS, já com a resposta OCSP dentro)
```

Resolve privacidade (o cliente não fala com a CA) e latência (zero requisição extra).

```nginx
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/letsencrypt/live/DOMINIO/chain.pem;
resolver 1.1.1.1 8.8.8.8 valid=300s;   # sem isto, falha SILENCIOSAMENTE
```

```bash
echo | openssl s_client -connect exemplo.com.br:443 -servername exemplo.com.br -status 2>&1 | grep -A2 "OCSP Response Status"
# com stapling:  OCSP Response Status: successful (0x0)
# sem stapling:  OCSP response: no response sent
```

**Mas ainda não resolve o soft-fail:** um servidor malicioso simplesmente **não anexa**
nada, e o cliente segue em frente. A correção seria a extensão **`must-staple`**
(RFC 7633), que marca no certificado "exija o staple ou recuse". Praticamente ninguém
usou: se o stapling do seu servidor falhar por 5 minutos, o site fica **inacessível**,
e o ganho de segurança não compensou o risco operacional para a maioria.

> **Novidade que muda o cenário:** desde 2024–2025 o próprio ecossistema começou a
> **desligar o OCSP**. O Let's Encrypt anunciou o fim dos serviços de OCSP, e os
> *Baseline Requirements* do CA/B Forum passaram a tratar o OCSP como opcional e a CRL
> como obrigatória para as CAs. A direção é clara: **abandonar a consulta on-line e
> apostar em vida curta**. Confirme o estado atual antes de projetar em cima disso —
> este é um ponto em movimento.

---

## 5. As soluções proprietárias dos navegadores

Como nada acima funcionava, os navegadores construíram os próprios mecanismos:

| Mecanismo | Navegador | Como funciona |
|---|---|---|
| **CRLSets** | Chrome | o Google agrega revogações importantes numa lista **pequena e curada**, distribuída pelo mecanismo de atualização. Cobre uma fração do total — só o que o Google julga relevante |
| **OneCRL** | Firefox | igual em espírito: lista curada de intermediários e certificados revogados de alto impacto |
| **CRLite** | Firefox (em implantação progressiva) | comprime **todas** as revogações conhecidas num filtro probabilístico em cascata — poucos MB para centenas de milhões de certificados, atualizado várias vezes ao dia. Tecnicamente, a coisa mais interessante do campo |

**CRLite merece destaque:** usa filtros de Bloom em cascata, projetados de modo que os
falsos positivos da primeira camada sejam corrigidos pela seguinte. O resultado é uma
estrutura que responde "revogado / não revogado" **sem consultar ninguém**, offline,
com atualizações pequenas. É a resposta técnica mais elegante ao problema — e demorou
25 anos para aparecer.

---

## 6. A resposta que venceu: vida curta

Se o certificado vale 6 dias, uma chave vazada é útil por no máximo 6 dias.
**Vida curta substitui revogação.** É a tese explícita do ecossistema em 2026.

| Data | Validade máxima de certificado público |
|---|---|
| até 2015 | 5 anos |
| 2015 | 39 meses |
| 2018 | 825 dias |
| set/2020 | **398 dias** |
| **15/03/2026** | **200 dias** |
| 15/03/2027 | 100 dias |
| 15/03/2029 | **47 dias** |

Cronograma aprovado pelo **Ballot SC-081v3** do CA/B Forum, em abril de 2025, com
**29 votos a favor e zero contra** — unanimidade rara, que mostra o consenso.

E o Let's Encrypt foi além: desde **15/01/2026**, oferece o perfil `shortlived`, com
**160 horas (pouco mais de 6 dias)** de validade, e certificados para **endereço IP**
— estes últimos **somente** na modalidade de 6 dias, porque o controle de um IP muda
de mãos com muito mais frequência que o de um domínio.

**Por que 47 dias, e não 30 ou 60?** Aritmética operacional: 47 = 1 mês (31) + 1/3 de
mês (15) + 1 dia de folga. Permite ciclos mensais com margem para renovar cedo e
tolerar falhas. É uma **convenção arbitrária escolhida por conveniência de calendário**
— e a fonte diz isso explicitamente.

### 6.1 O que isso exige de você

| Antes | A partir de 2026–2029 |
|---|---|
| renovação manual anual | **impossível** |
| lembrete no calendário | **impossível** |
| planilha de certificados | inventário automatizado obrigatório |
| um humano no processo | ACME de ponta a ponta, com alerta quando a automação falha |

Se hoje você renova certificado à mão, tem até março de 2027 (100 dias) para que isso
deixe de ser sustentável, e março de 2029 para que seja inviável. **Automatize agora**:
[16-acme-e-automacao.md](16-acme-e-automacao.md).

---

## 7. Certificate Transparency — a defesa que funcionou

CT (RFC 6962, e a versão 2.0 na RFC 9162) resolve um problema **diferente** da
revogação, e resolve bem: **como saber que uma CA emitiu um certificado indevido para
o seu domínio?**

### 7.1 Como funciona

1. Toda CA pública deve submeter cada certificado a **logs públicos**, do tipo
   *append-only*, criptograficamente auditáveis (árvores de Merkle).
2. O log devolve um **SCT** (*Signed Certificate Timestamp*), uma promessa assinada de
   que o certificado será incluído.
3. O certificado carrega os SCTs (numa extensão), ou eles chegam pelo handshake.
4. **O Chrome recusa, desde abril de 2018, qualquer certificado público sem SCTs
   suficientes.** Ou seja: certificado que não é público não funciona.
5. **Monitores** (qualquer um pode rodar um) observam os logs e alertam.

O ponto genial: a CA não pode emitir em segredo. Se emitir, fica registrado
publicamente e para sempre. Não impede a emissão — **torna-a detectável em horas**.

### 7.2 Use isso hoje, custa nada

```bash
# tudo que já foi emitido para um domínio
curl -s "https://crt.sh/?q=exemplo.com.br&output=json" | \
  python3 -c "
import sys, json
for r in json.load(sys.stdin)[:20]:
    print(r['not_before'][:10], '|', r['issuer_name'][:45], '|', r['name_value'].replace(chr(10),' '))"
```

Serviços de monitoramento gratuitos que mandam e-mail quando alguém emite para o seu
domínio: **crt.sh**, **Cert Spotter** (SSLMate), **Facebook CT Monitor**, **Censys**.
Configurar leva cinco minutos e é a única defesa prática contra uma CA comprometida.

### 7.3 Efeitos colaterais reais

- **Vazamento de nomes internos.** Se você emitir um certificado público para
  `homologacao-financeiro-novo.exemplo.com.br`, esse nome vira **público e permanente**.
  Atacantes varrem os logs de CT em busca de alvos. Use **certificado curinga** ou uma
  **CA interna** para nomes que não devem ser divulgados.
- **É uma ferramenta de reconhecimento.** A primeira coisa que um pentester faz é
  consultar o crt.sh do alvo. Faça você primeiro.

---

## 8. Como está a validação hoje, na prática

| Verificação | Chrome | Firefox | curl/OpenSSL padrão |
|---|---|---|---|
| assinatura da cadeia | ✅ | ✅ | ✅ |
| validade temporal | ✅ | ✅ | ✅ |
| nome (SAN) | ✅ | ✅ | ✅ |
| SCT / Certificate Transparency | ✅ obrigatório | parcial | ❌ |
| CRL clássica | ❌ | ❌ | só se você mandar |
| OCSP on-line | ❌ (removido) | limitado | só se você mandar |
| OCSP stapling | ✅ se presente | ✅ se presente | com `-status` |
| lista curada (CRLSets/OneCRL/CRLite) | ✅ | ✅ | ❌ |

**Leitura honesta desta tabela:** para um certificado de servidor comum, **a revogação
essencialmente não é verificada** pelos clientes. A segurança real vem de (a) vida
curta, (b) Certificate Transparency, (c) listas curadas para incidentes graves.

---

## 9. Resumo em uma página

```
                     Chave privada vazou. E agora?

  ┌── CRL ──────────► grande, atrasada. Boa em PKI INTERNA (poucos certs, clientes seus)
  │
  ├── OCSP ─────────► vaza privacidade, adiciona latência, SOFT-FAIL = inútil contra
  │                   um atacante de rede. Está sendo desativado pelo ecossistema.
  │
  ├── OCSP stapling ► resolve privacidade e latência. Não resolve o soft-fail
  │                   (must-staple resolveria, mas ninguém usa: risco operacional).
  │
  ├── CRLSets /
  │   OneCRL / ─────► curadoria dos navegadores. Cobre incidentes graves.
  │   CRLite          CRLite é a melhor solução técnica existente.
  │
  └── VIDA CURTA ───► ✅ O QUE VENCEU. 200 dias (2026) → 100 (2027) → 47 (2029);
                       6 dias já disponíveis. Automação deixa de ser opcional.

  E, em paralelo:
      CT ───────────► não é revogação: é DETECÇÃO de emissão indevida.
                       É a defesa que realmente funcionou. Monitore hoje.
```

---

## Autoteste

1. Quais são os três problemas estruturais de qualquer esquema de revogação?
2. Por que os navegadores abandonaram a CRL clássica, e onde ela ainda faz sentido?
3. O que o OCSP revela à CA, e por quê isso é grave?
4. Explique soft-fail e por que ele torna a revogação inútil contra um atacante de rede.
5. O que o OCSP stapling resolve e o que ele **não** resolve?
6. Por que quase ninguém usa `must-staple`?
7. O que é CRLite e por que ele é tecnicamente interessante?
8. Qual é o cronograma de redução da validade máxima, e qual ballot o definiu?
9. Por que 47 dias e não 30?
10. Como o Certificate Transparency detecta uma CA comprometida, e por que ele não impede a emissão?
11. Qual é o efeito colateral de emitir certificado público para um host interno?
12. Na prática, hoje, a revogação de um certificado de servidor comum é verificada?

*Respostas: §1, §2, §3.1, §3.3, §4, §4, §5, §6, §6, §7.1, §7.3, §8.*

---

**Próximo:** [16-acme-e-automacao.md](16-acme-e-automacao.md) — como nunca mais renovar à mão.
