# 11 · História

**Nível:** iniciante → intermediário · **Data:** 31/08/2026

Trinta e dois anos de protocolo, contados pelos acidentes. Não é curiosidade:
**quase toda regra estranha do TLS de hoje é cicatriz de um ataque específico**.
Quem conhece a história não precisa decorar as recomendações — elas passam a ser óbvias.

---

## Linha do tempo

| Ano | Evento | O que mudou para sempre |
|---|---|---|
| 1994 | Netscape projeta o **SSL 1.0** | nunca lançado: os próprios revisores o quebraram antes |
| 1995 | **SSL 2.0** | primeiro em produção; quebrado em pouco tempo |
| 1996 | **SSL 3.0** (Freier, Karlton, Kocher) | reescrita completa; durou 18 anos |
| 1999 | **TLS 1.0** (RFC 2246) | o protocolo vira padrão IETF; muda de nome por política |
| 2006 | **TLS 1.1** (RFC 4346) | conserta o IV previsível do CBC (pré-BEAST) |
| 2008 | **TLS 1.2** (RFC 5246) | SHA-256, AEAD (GCM), fim do MD5 embutido |
| 2011 | **BEAST** e **DigiNotar** | ataque prático em CBC; primeira CA a falir por invasão |
| 2012–13 | **CRIME**, **Lucky13**, **RC4 quebrado** | morre a compressão TLS; morre o RC4 |
| 2013 | **Revelações de Snowden** | migração em massa para sigilo futuro (ECDHE) |
| 2014 | **Heartbleed**, **POODLE** | bug em C vaza memória; SSL 3.0 é aposentado |
| 2014 | **Let's Encrypt** anunciado | certificado deixa de ser um produto e vira infraestrutura |
| 2015 | **FREAK**, **Logjam** | as cifras "de exportação" dos anos 1990 cobram o preço |
| 2016 | **DROWN**, **Sweet32** | SSLv2 residual e 3DES caem |
| 2018 | **TLS 1.3** (RFC 8446, agosto) | reescrita: 1-RTT, tudo cifrado, só AEAD, sem RSA-transporte |
| 2018 | **CT obrigatório** no Chrome | toda emissão passa a ser pública e auditável |
| 2020 | Validade cai para **398 dias** | fim dos certificados de 2 e 3 anos |
| 2021 | Fim do TLS 1.0/1.1 nos navegadores | conclusão de uma década de transição |
| 2024 | Chrome e Firefox ligam **ML-KEM híbrido** por padrão | começa a era pós-quântica em produção |
| 2025 | **Ballot SC-081v3** aprovado (abril) | cronograma: 200 dias em 2026, 100 em 2027, 47 em 2029 |
| 2026 | **15/01** — Let's Encrypt: certificados de **6 dias** e para **endereço IP** | vida curta vira produto de prateleira |
| 2026 | **03/03** — **RFC 9849**: ECH publicado | o SNI finalmente pode ser cifrado |
| 2026 | **15/03** — validade máxima cai para **200 dias** | renovação manual deixa de ser viável |

---

## 1. 1994–1996: a Netscape inventa comércio na web

**O problema:** a web de 1993 era acadêmica e completamente em claro. A Netscape
queria vender. Ninguém digita número de cartão em texto puro.

**A solução:** Taher Elgamal, cientista-chefe da Netscape (o mesmo do criptossistema
ElGamal, de 1985), liderou o SSL. A versão **1.0 nunca saiu**: revisores internos
acharam falhas graves — entre elas, ausência de proteção de integridade, permitindo
alterar mensagens sem detecção.

O **SSL 2.0** (1995) foi lançado e tinha problemas estruturais: mesma chave para
cifra e autenticação, MAC fraco baseado em MD5, e — o pior — o handshake **não era
protegido**, permitindo que um atacante forçasse cifras fracas sem ser notado.

O **SSL 3.0** (1996) foi uma reescrita, com Paul Kocher (que depois descobriria
Spectre e Meltdown). Introduziu o conceito de handshake autenticado por um `Finished`
que resume tudo que foi negociado. É o antepassado direto do TLS de hoje.

**Lição que sobreviveu:** *a negociação precisa ser autenticada retroativamente*.
Sem isso, tudo o mais é inútil, porque o atacante escolhe o algoritmo mais fraco.

---

## 2. 1999: a política renomeia o protocolo

Quando o IETF assumiu o padrão, a Microsoft se opôs a padronizar algo chamado "SSL",
de propriedade da concorrente Netscape. O grupo de trabalho renomeou para **TLS 1.0**.
Tim Dierks, um dos autores, relatou depois que a mudança foi uma concessão política
explícita para que a Microsoft aceitasse o padrão.

Tecnicamente, **TLS 1.0 é SSL 3.1** — a própria numeração interna do protocolo diz
isso (`0x0301`). Por isso, até hoje, "certificado SSL" continua sendo o nome comercial
de algo que não usa SSL há um quarto de século.

**Lição:** padrões são artefatos políticos tanto quanto técnicos. Isso explica
compromissos estranhos que você vai encontrar em qualquer RFC.

---

## 3. 2011–2013: a década em que o CBC caiu

Três ataques em sequência atacaram a mesma construção — cifra de bloco em modo CBC com
MAC-then-Encrypt:

- **BEAST** (2011): explorava o **IV previsível** do CBC no TLS 1.0. O TLS 1.1 já
  havia corrigido em 2006, mas quase ninguém tinha migrado — cinco anos de aviso
  ignorado. O ataque forçou a migração.
- **CRIME** (2012): explorava a **compressão** TLS. Se o atacante injeta texto na
  requisição e observa o tamanho do registro comprimido, descobre o cookie de sessão
  byte a byte. **Compressão + segredo no mesmo fluxo = vazamento.** A compressão TLS
  foi removida. (O irmão **BREACH**, de 2013, faz o mesmo com a compressão do HTTP,
  e continua tecnicamente possível até hoje.)
- **Lucky13** (2013): ataque de **canal lateral por tempo** no preenchimento do CBC.
  A verificação do padding demorava um pouco mais ou menos conforme o palpite. A
  correção — código de tempo constante — é notoriamente difícil de acertar.

**Lição:** MAC-then-Encrypt foi uma escolha de ordem errada, e por 15 anos rendeu
ataques. O TLS 1.3 só admite **AEAD**, onde cifra e autenticação são uma operação
projetada em conjunto. Ordem de operações em criptografia não é detalhe estético.

---

## 4. 2013: Snowden e o sigilo futuro

Em junho de 2013 as revelações de Edward Snowden documentaram programas de coleta em
massa de tráfego. A comunidade fez uma conta simples e desconfortável: se o tráfego
está sendo **gravado**, então qualquer vazamento futuro de chave privada de servidor
decifra retroativamente **anos** de comunicação.

Isso transformou o ECDHE de "opção cara" em obrigação. Entre 2013 e 2016 o
sigilo futuro passou de minoria a maioria absoluta do tráfego. Em 2018 o TLS 1.3
**removeu** a alternativa.

**Lição:** o modelo de ameaça não é abstrato. Ele muda quando se descobre o que o
adversário realmente faz — e a engenharia muda junto.

---

## 5. 2014: Heartbleed, e o dia em que a internet trocou de chaves

**CVE-2014-0160.** Não foi falha do protocolo: foi um bug de duas linhas no OpenSSL,
na implementação da extensão *heartbeat*. O código lia o tamanho declarado pelo
cliente e copiava essa quantidade de bytes da memória — **sem verificar se o cliente
tinha realmente enviado tanto**. Pedindo "me devolva 64 KB" com 1 byte de dado,
o atacante recebia 64 KB de memória do processo do servidor: chaves privadas,
senhas, cookies de sessão.

O impacto foi único na história do TLS por três motivos:

1. **Não deixava rastro.** Não aparecia em log nenhum. Ninguém sabe o que foi levado.
2. **Atingiu ~17% dos servidores HTTPS do mundo.**
3. **Não bastava corrigir**: era preciso **trocar todas as chaves e revogar todos os
   certificados** — o que expôs, na prática, que a infraestrutura de revogação não
   aguentava o tranco.

Consequências duradouras: nasceram o **LibreSSL** (fork do OpenBSD, que apagou
~90 mil linhas do OpenSSL em semanas) e o **BoringSSL** (Google); o OpenSSL, que era
mantido por essencialmente uma pessoa e meia com US$ 2.000/ano de doações, passou a
receber financiamento pela **Core Infrastructure Initiative**.

**Lição, e ela é econômica:** infraestrutura crítica sustentada por trabalho voluntário
não remunerado é um risco sistêmico. O problema não era técnico; era de financiamento.

No mesmo ano, o **POODLE** enterrou o SSL 3.0 explorando o preenchimento do CBC —
e, pior, explorando o fato de que clientes faziam *downgrade* voluntário para SSL 3.0
quando o handshake TLS falhava, o que um atacante podia provocar à vontade.

**Lição:** *fallback* automático para versão antiga anula a proteção de versão.
Daí a extensão `TLS_FALLBACK_SCSV`, e daí o TLS 1.3 codificar a defesa anti-downgrade
diretamente nos bytes finais do `ServerHello.random`.

---

## 6. 2015: a conta dos anos 1990 chega

**FREAK** e **Logjam** exploraram as cifras **EXPORT**: nos anos 1990, a lei dos EUA
classificava criptografia forte como munição, e software exportado era obrigado a usar
chaves de no máximo 512 bits (RSA) ou 40 bits (simétrica). Essas suites permaneceram
no código por compatibilidade — vinte anos depois, quando fatorar 512 bits custava
poucas centenas de dólares em nuvem, um atacante podia **forçar** o servidor a usá-las.

**Lição, e é a mais importante deste arquivo:** *backdoor por decreto é dívida técnica
com juros compostos*. As restrições de exportação acabaram em 2000; os ataques
chegaram em 2015. Enfraquecimento deliberado não é temporário nem contido — vaza para
todos, inclusive para quem o exigiu. Este é o argumento técnico central contra
qualquer proposta de "acesso excepcional" à criptografia, e ele é histórico, não teórico.

---

## 7. 2018: TLS 1.3, a reescrita

Dez anos depois do 1.2, e quatro anos de trabalho na IETF (28 rascunhos). A filosofia
mudou: em vez de acrescentar opções, **remover tudo que já se mostrou perigoso**.

**O que saiu:**

| Removido | Por causa de |
|---|---|
| transporte de chave por RSA | falta de sigilo futuro; ataques Bleichenbacher/ROBOT |
| todas as cifras CBC | BEAST, Lucky13, POODLE |
| RC4 | viés estatístico |
| compressão | CRIME |
| renegociação | CVE-2009-3555 e complexidade |
| grupos DH personalizados | Logjam |
| assinatura estática DH/ECDH | sem sigilo futuro |
| MD5 e SHA-1 na negociação | colisões |
| ChangeCipherSpec (viraram bytes de compatibilidade) | complexidade sem função |

**O que entrou:**

- **1-RTT por padrão** (era 2-RTT): o cliente já manda o `key_share` no `ClientHello`,
  apostando no grupo que o servidor provavelmente aceita.
- **0-RTT opcional** na retomada: latência zero, com a ressalva de que dados 0-RTT
  são **sujeitos a repetição** por construção — só para requisições idempotentes.
- **Tudo cifrado a partir do `ServerHello`**, inclusive o certificado do servidor e as
  extensões. No TLS 1.2, o certificado ia em claro e qualquer observador via com quem
  você falava.
- **Escalonamento de chaves com HKDF**: chaves distintas para cada fase e direção.
- **Assinatura sobre o transcript inteiro** (`CertificateVerify`), fechando classes
  inteiras de ataques de confusão de estado.

**Percalço real:** o TLS 1.3 quebrou equipamentos de rede intermediários (*middleboxes*)
que assumiam formatos do TLS 1.2. A solução foi o *middlebox compatibility mode* —
mensagens falsas de `ChangeCipherSpec` e um número de versão mentiroso, incluídos no
padrão **só para enganar equipamento quebrado**. É o exemplo mais didático de
**ossificação**: a internet ficou tão cheia de intermediários que inspecionam o
tráfego que evoluir um protocolo exige disfarçá-lo. Esse aprendizado moldou o QUIC,
que cifra quase todo o cabeçalho justamente para que nenhum intermediário possa
depender do formato — e portanto não possa impedir sua evolução.

---

## 8. 2015–2026: Let's Encrypt muda a economia

Antes de 2015, um certificado custava de US$ 50 a US$ 500 por ano, exigia processo
manual e era renovado à mão. A consequência estrutural: **HTTPS era privilégio de
quem tinha orçamento**, e o resto da web ficava em claro.

O Let's Encrypt (ISRG, anunciado em 2014, aberto ao público em 2015) fez três coisas
simultâneas: preço **zero**, emissão **automatizada** por um protocolo aberto (**ACME**,
depois RFC 8555), e validade **curta** (90 dias) — o que **força** a automação e torna
o vazamento de chave um problema com prazo de validade.

Efeito medido: a fatia de páginas carregadas por HTTPS no Firefox saltou de ~30% (2014)
para mais de 90% (2024 em diante). Poucas intervenções técnicas mudaram tanto a web.

**Quem paga a conta:** patrocinadores corporativos (Mozilla, Chrome, Cisco, AWS,
Meta e outros) e doações. Custo operacional da ordem de alguns milhões de dólares por
ano para emitir bilhões de certificados. Discutido em [80-custos-e-licencas.md](80-custos-e-licencas.md).

**A continuação lógica, em 2026:** certificados de **6 dias** e para **endereço IP**,
disponíveis desde 15/01/2026, e a redução obrigatória da validade máxima pública —
**200 dias em 15/03/2026**, 100 em 2027, 47 em 2029. A tese é explícita: *revogação
nunca funcionou; vida curta substitui revogação*.

---

## 9. 2024–2026: a transição pós-quântica

A ameaça é o algoritmo de Shor (1994): um computador quântico suficientemente grande
fatoraria RSA e resolveria o logaritmo discreto em curvas elípticas — quebrando de uma
vez a troca de chaves e as assinaturas do TLS clássico. Esse computador não existe hoje.

O que torna isso urgente mesmo assim é o **"colher agora, decifrar depois"**
(*harvest now, decrypt later*): um adversário grava tráfego cifrado hoje e o decifra
quando tiver a máquina. Para dados com sigilo de 10 ou 20 anos, o risco **já é atual**.

Cronologia: o NIST padronizou o **ML-KEM** (antes Kyber) como FIPS 203 em agosto de
2024. Chrome ligou o híbrido **X25519MLKEM768** por padrão em 2024, Firefox em seguida,
Apple em outubro de 2025, e a Akamai tornou padrão em toda a rede em janeiro–março de
2026. Em abril de 2026, mais de dois terços do tráfego TLS humano que chega à
Cloudflare já usa troca de chaves híbrida pós-quântica.

**Por que "híbrido" (X25519 **e** ML-KEM juntos):** o segredo final combina os dois.
Se o ML-KEM tiver uma falha ainda desconhecida — é criptografia jovem —, a segurança
clássica do X25519 sustenta. Se um computador quântico surgir, o ML-KEM sustenta.
É cinto e suspensório, e é a decisão certa para uma transição.

**O que ainda não migrou:** as **assinaturas**. ML-DSA e SLH-DSA são grandes demais
(assinaturas de 2 a 8 KB contra 64 bytes) para caber confortavelmente no handshake, e
trocá-las exige que todas as CAs e todos os root stores mudem. Detalhes e o debate
atual em [65-estado-da-arte.md](65-estado-da-arte.md).

---

## 10. As oito lições que atravessam os 32 anos

1. **Complexidade é a inimiga.** Cada opção negociável do TLS 1.2 virou vetor de
   ataque. O TLS 1.3 ficou mais seguro principalmente por ter **menos**.
2. **Compatibilidade retroativa mata.** FREAK, Logjam, DROWN e POODLE existiram
   porque código velho continuou lá "por precaução".
3. **Fallback automático anula a negociação.** Se falhar e tentar de novo mais fraco,
   o atacante só precisa provocar a falha.
4. **Autentique a negociação inteira, retroativamente.** Foi a lição de 1996 e
   continua sendo a espinha dorsal.
5. **Enfraquecimento deliberado volta como ataque, vinte anos depois.**
6. **Bug de implementação é tão fatal quanto falha de projeto** — e infraestrutura
   crítica precisa de financiamento, não de boa vontade.
7. **Automação é segurança.** Certificado curto e renovação automática eliminam uma
   classe inteira de incidentes que nenhuma criptografia resolveria.
8. **Migrações levam uma década.** TLS 1.1 corrigiu o BEAST em 2006; o ataque
   aconteceu em 2011 porque ninguém migrou. Comece cedo — vale para o pós-quântico agora.

---

## Autoteste

1. Por que o SSL 1.0 nunca foi lançado?
2. Por que o protocolo mudou de nome para TLS em 1999?
3. O que BEAST, CRIME e Lucky13 têm em comum, e o que o TLS 1.3 fez a respeito?
4. O que exatamente era o bug do Heartbleed, e por que corrigir o software não bastou?
5. Qual é a lição do FREAK/Logjam sobre criptografia enfraquecida por lei?
6. Cite cinco coisas removidas pelo TLS 1.3 e o ataque que motivou cada uma.
7. O que é *middlebox compatibility mode* e o que ele revela sobre a internet?
8. Como o Let's Encrypt mudou a economia do HTTPS, e quem paga a conta?
9. O que é "colher agora, decifrar depois" e por que torna o pós-quântico urgente hoje?
10. Por que a troca de chaves pós-quântica é **híbrida**?
11. Das oito lições, qual você aplicaria ao sistema que está construindo agora?

*Respostas: §1, §2, §3, §5, §6, §7, §7, §8, §9, §9, §10.*

---

**Próximo:** [12-handshake.md](12-handshake.md) — o handshake, mensagem a mensagem.
