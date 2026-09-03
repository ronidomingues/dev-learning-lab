# `cofre-tls` — projeto-modelo

**Nível:** intermediário · **Data:** 31/08/2026
**Verificado:** 32/32 testes executados e aprovados em Ubuntu 22.04.5, Python 3.10.12,
OpenSSL 3.0.2, em 31/08/2026.

Uma **API de notas protegida por mTLS**, com uma **autoridade certificadora própria**,
revogação por CRL e autorização por identidade do certificado.
**Zero dependências**: só a biblioteca padrão do Python e o `openssl` que você já tem.

Não é um trecho de código: é um sistema pequeno e inteiro, com os pedaços que
tutoriais omitem — tratamento de erro, configuração por ambiente, base de dados de
emissão, revogação, testes de ataque.

---

## Por que este projeto e não um "hello world com HTTPS"

Um servidor HTTPS com certificado autoassinado ensina uma coisa só: como carregar um
arquivo `.pem`. Este projeto exercita o que realmente aparece no trabalho:

| Conceito | Onde ele aparece aqui |
|---|---|
| ser uma CA de verdade (base, série, CRL) | `pki/openssl-ca.cnf`, `criar-pki.sh` |
| perfis de emissão separados (`serverAuth` × `clientAuth`) | `pki/openssl-ca.cnf` |
| SAN, e por que o CN não basta | `criar-pki.sh` §2 |
| mTLS: autenticação pelo certificado | `servidor.py::montar_contexto` |
| **autorização não é autenticação** | `servidor.py::PERMISSOES` |
| revogação que funciona de verdade | CRL + `VERIFY_CRL_CHECK_LEAF` |
| verificação de nome no lado do cliente | `cliente.py::contexto`, teste 44 |
| falha de TLS ≠ erro HTTP | `cliente.py::chamar` |
| testar o "não" e não só o "sim" | `testes/test_cofre.py` classe `TesteAtaques` |

---

## Pré-requisitos

| Item | Versão mínima | Confira com |
|---|---|---|
| Python | 3.9 | `python3 --version` |
| OpenSSL (linha de comando) | 3.0 | `openssl version` |
| Bash + `date` do GNU coreutils | — | `date -u -d "1 day ago" +%y%m%d%H%M%SZ` |

> **macOS:** o `date` do BSD não aceita `-d "1 day ago"`. Instale o do GNU
> (`brew install coreutils`) e rode o script com `PATH="$(brew --prefix coreutils)/libexec/gnubin:$PATH"`.
> **Windows:** use WSL2. Ver [../03-instalacao.md](../03-instalacao.md#5-windows--nativo-e-wsl2).

Nenhuma conta, nenhum domínio, nenhuma porta privilegiada. Tudo em `localhost:8443`.

---

## Como rodar — comandos exatos

```bash
cd tls/07-projeto-modelo

# 1. Criar toda a PKI (CA, servidor, 3 clientes, 1 revogado, 1 vencido, 1 intruso)
./criar-pki.sh

# 2. Rodar a suíte completa de testes  →  esperado: "Ran 32 tests ... OK"
./executar-testes.sh

# 3. Subir o servidor (deixe rodando neste terminal)
python3 servidor.py
#    esperado: cofre-tls ouvindo em https://127.0.0.1:8443/ (CRL: sim)
```

Em **outro terminal**:

```bash
./cliente.py --como admin    saude
./cliente.py --como escritor criar "minha primeira nota"
./cliente.py --como leitor   listar
./cliente.py --como leitor   criar "isto deve dar 403"
./cliente.py --como admin    apagar 1
./cliente.py --como banido   listar     # revogado
./cliente.py --como vencido  listar     # expirado
./cliente.py --como intruso  listar     # CA desconhecida
```

Saída real desta sequência (executada em 31/08/2026):

```
[admin] HTTP 200: {"estado": "ok", "voce": "admin"}
[escritor] HTTP 201: {"id": 1, "texto": "minha primeira nota", "autor": "escritor"}
[leitor] HTTP 200: {"notas": [{"id": 1, "texto": "minha primeira nota", "autor": "escritor"}]}
[leitor] HTTP 403: {"erro": "'leitor' não pode 'escrever'"}
[admin] HTTP 204: {}
[banido]  HTTP 0: {"erro_tls": "[SSL: SSLV3_ALERT_CERTIFICATE_REVOKED] sslv3 alert certificate revoked"}
[vencido] HTTP 0: {"erro_tls": "[SSL: SSLV3_ALERT_CERTIFICATE_EXPIRED] sslv3 alert certificate expired"}
[intruso] HTTP 0: {"erro_tls": "[SSL: TLSV1_ALERT_UNKNOWN_CA] tlsv1 alert unknown ca"}
```

> ### Leia com atenção as três últimas linhas
> `HTTP 0` não é um código de status: é a ausência de HTTP. As três tentativas foram
> barradas **no handshake TLS**, antes de existir uma requisição. Nenhum byte de
> aplicação chegou ao servidor, nenhuma rota foi consultada, nenhum log de acesso foi
> escrito. Esta é a diferença prática entre autenticação no TLS e autenticação na
> aplicação: com mTLS, o atacante nunca chega a falar com o seu código.

Com `curl`:

```bash
curl --cacert pki/ca.crt --cert pki/admin.crt --key pki/admin.key https://localhost:8443/saude
# {"estado": "ok", "voce": "admin"}

curl --cacert pki/ca.crt https://localhost:8443/saude
# curl: (56) OpenSSL SSL_read: ... alert certificate required
```

---

## Estrutura de pastas

```
07-projeto-modelo/
├── README.md               este arquivo
├── criar-pki.sh            monta a PKI inteira do zero; idempotente (--forcar refaz)
├── servidor.py             a API com mTLS, CRL e autorização por CN
├── cliente.py              cliente de linha de comando, uma identidade por vez
├── executar-testes.sh      cria a PKI se faltar e roda os 32 testes
├── testes/
│   └── test_cofre.py       10 testes de PKI · 11 de autorização · 8 de ataque · 3 de conexão
└── pki/                    (gerado)
    ├── openssl-ca.cnf      configuração da CA: perfis, política, base de dados
    ├── ca.crt / ca.key     a raiz (EC P-384, 10 anos)
    ├── ca.crl              lista de revogação
    ├── ca-com-crl.pem      CA + CRL concatenados — o que o servidor carrega
    ├── index.txt           BASE DE EMISSÃO: V=válido, R=revogado, E=expirado
    ├── serial / crlnumber  contadores
    ├── novos/              cópia de todo certificado já emitido
    ├── servidor.crt/.key   CN=cofre.interno, SAN=localhost/127.0.0.1
    ├── admin|escritor|leitor.*   clientes legítimos, com poderes diferentes
    ├── banido.*            emitido e depois REVOGADO
    ├── vencido.*           emitido com validade no passado
    └── intruso-ca.* / intruso.*  uma segunda CA e um cliente dela que se diz "admin"
```

---

## O que cada decisão de projeto ensina

### 1. `openssl ca` em vez de `openssl x509 -req`

Quase todo tutorial usa `openssl x509 -req` para assinar. É mais simples e **não
permite revogar**: sem base de emissão (`index.txt`) e sem número de série
controlado, não existe como dizer "o certificado nº 4 não vale mais". `openssl ca`
obriga a manter essa base — é a diferença entre gerar certificados e **operar uma CA**.

Veja a base depois de rodar o script:

```bash
awk -F'\t' '{printf "%s  %s\n", $1, $6}' pki/index.txt
# V  /O=Cofre TLS/CN=cofre.interno
# V  /O=Cofre TLS/CN=admin
# R  /O=Cofre TLS/CN=banido       ← revogado
# E  /O=Cofre TLS/CN=vencido      ← expirado (marcado por `openssl ca -updatedb`)
```

### 2. `extendedKeyUsage` diferente para servidor e cliente

O certificado do servidor tem só `serverAuth`; o dos clientes, só `clientAuth`.
Sem essa separação, o certificado de um cliente serve para **se passar por um
servidor seu** — e, num ambiente com mTLS, isso permite a um serviço comprometido
interceptar tráfego dos outros. Custa uma linha de configuração. O teste 04 e o 05
verificam que a separação existe.

### 3. `copy_extensions = none`

Está explícito no `openssl-ca.cnf`. Se estivesse em `copyext`, quem envia o CSR
escolhe as próprias extensões — inclusive `basicConstraints=CA:TRUE`, e você acaba
de emitir uma **autoridade certificadora** para quem pediu um certificado de cliente.
A partir daí ele forja qualquer identidade da sua PKI. Essa é uma vulnerabilidade
real, com histórico, e o padrão do OpenSSL é `none` justamente por isso.

### 4. Revogação por CRL, checada de verdade

```python
ctx.load_verify_locations(str(CA_E_CRL))          # CA + CRL no mesmo arquivo
ctx.verify_flags |= ssl.VERIFY_CRL_CHECK_LEAF     # sem isto, a CRL é decoração
```

Muita gente gera CRL e nunca a consulta. Sem a segunda linha, o `banido` entra
normalmente. Prove: rode `COFRE_CHECAR_CRL=0 python3 servidor.py` e tente
`./cliente.py --como banido saude` — passa. Ligue de volta e ele é barrado.
É um experimento de dez segundos que vale mais que dez páginas sobre revogação.

**Limite honesto desta abordagem:** a CRL é lida do disco no *start* do processo.
Revogar alguém às 10h só surte efeito no próximo restart. Numa PKI de verdade
isso se resolve com OCSP, ou — mais comum e mais robusto hoje — com certificados
de vida curtíssima, como no Exemplo 13 de [../06-exemplos.md](../06-exemplos.md).
Ver [../15-validacao-revogacao-transparencia.md](../15-validacao-revogacao-transparencia.md).

### 5. Autorização separada da autenticação

```python
PERMISSOES = {"admin": {"ler","escrever","apagar"},
              "escritor": {"ler","escrever"},
              "leitor": {"ler"}}
```

O TLS respondeu "**quem** é você" (CN=leitor, comprovado criptograficamente).
Ele **não** responde "o que você pode fazer". Sistemas com mTLS que param na
autenticação dão a todos os clientes da CA acesso total — o erro mais comum de
service mesh mal configurado. O teste 23 (`leitor` tenta criar → 403) existe
para provar que a separação está lá.

Numa PKI maior, não use o CN para isso: use um SAN do tipo URI, no estilo SPIFFE
(`spiffe://empresa/ns/prod/sa/pedidos`), que carrega ambiente e namespace.
Ver [../18-mtls-e-pki-interna.md](../18-mtls-e-pki-interna.md).

### 6. Versão mínima explícita

```python
ctx.minimum_version = ssl.TLSVersion.TLSv1_2
```

O padrão do Python 3.10 já é bom. Mas "o padrão é bom" é uma promessa do runtime,
não sua. Fixar a versão mínima é o que torna a sua garantia auditável, e o que
impede que uma mudança de imagem base afrouxe silenciosamente o que você prometeu
num relatório de conformidade.

### 7. Metade dos testes são ataques

```
TestePKI          10 testes   a PKI foi construída como deveria?
TesteAutorizacao  11 testes   o caminho feliz e os 403/400/404
TesteAtaques       8 testes   sem cert · outra CA · revogado · vencido ·
                              nome errado · CA errada no cliente · TLS 1.1 ·
                              verificação realmente ligada
TesteConexao       3 testes   negocia TLS 1.3? cifra é AEAD? contexto correto?
```

Uma suíte de TLS que só testa o caminho feliz passa igualzinho com a verificação
desligada. Os testes que importam são os que exigem que o sistema **recuse**.

### 8. Um detalhe de ambiente que virou teste

O teste 44 (nome errado) usa socket cru em vez de `urllib`. Motivo: `urllib`
respeita `HTTPS_PROXY`, e um `no_proxy` com faixa CIDR (`127.0.0.0/8`) — que a
maioria dos clientes **não** interpreta — faz a conexão local sair pelo proxy
corporativo. O erro observado passa a ser outro e o teste falha por um motivo que
nada tem a ver com TLS. Isso aconteceu de verdade ao escrever este projeto.
Lição: **teste de TLS não pode depender do ambiente de rede de quem executa**.

---

## Configuração por ambiente

| Variável | Padrão | Para quê |
|---|---|---|
| `COFRE_ENDERECO` | `127.0.0.1` | interface de escuta |
| `COFRE_PORTA` | `8443` | porta |
| `COFRE_CERT` / `COFRE_CHAVE` | `pki/servidor.*` | identidade do servidor |
| `COFRE_CA` | `pki/ca-com-crl.pem` | âncoras + CRL |
| `COFRE_CHECAR_CRL` | `1` | `0` desliga a checagem de revogação (para o experimento do §4) |
| `COFRE_LOG` | `INFO` | `DEBUG` mostra cada requisição |

---

## Experimentos sugeridos

1. **Desligar a CRL** (`COFRE_CHECAR_CRL=0`) e ver o `banido` entrar. Religar e vê-lo cair.
2. **Trocar `CERT_REQUIRED` por `CERT_OPTIONAL`** em `servidor.py` e observar que o
   cliente sem certificado passa no handshake — e que `_identidade()` devolve `None`.
   É exatamente o bug que transforma mTLS em decoração.
3. **Emitir um cliente novo** com o `criar-pki.sh` como base, adicioná-lo a
   `PERMISSOES`, e ver a autorização funcionar sem nenhuma mudança no TLS.
4. **Capturar o handshake** com `tshark -i lo -f "port 8443" -Y tls.handshake` e
   comparar com o [../12-handshake.md](../12-handshake.md).
5. **Revogar o `escritor`** (`openssl ca -config pki/openssl-ca.cnf -revoke pki/escritor.crt`,
   depois `-gencrl`), regerar `ca-com-crl.pem`, reiniciar e confirmar a recusa.
6. **Quebrar de propósito**: apague o SAN do certificado do servidor e veja o cliente
   recusar com "hostname mismatch" — mesmo com a CA correta.

---

## O que este projeto deliberadamente **não** faz

Ser honesto sobre os limites é parte do material.

| Não faz | Por quê / o que usar em produção |
|---|---|
| chave da CA em HSM ou máquina offline | aqui ela está em disco, com modo 600. Em produção: HSM, ou raiz offline emitindo um intermediário |
| OCSP | só CRL. OCSP exige um respondedor HTTP; ver [../15](../15-validacao-revogacao-transparencia.md) |
| renovação automática | é o assunto de [../16-acme-e-automacao.md](../16-acme-e-automacao.md); em cluster, cert-manager |
| persistência das notas | memória. Um banco não mudaria nada do que é ensinado sobre TLS |
| recarga de certificado sem restart | ver Exemplo 13 de [../06-exemplos.md](../06-exemplos.md) |
| identidade no estilo SPIFFE | usa CN, que é o suficiente para ensinar; ver [../18](../18-mtls-e-pki-interna.md) |

---

## Autoteste

1. Por que `openssl ca` e não `openssl x509 -req`?
2. O que aconteceria se `copy_extensions` fosse `copyext` e um atacante enviasse um CSR?
3. O cliente `intruso` tem `CN=admin`. Por que ele não vira admin?
4. Qual é a única linha que separa "gerar uma CRL" de "checar a CRL"?
5. Por que `HTTP 0` nas três últimas linhas da saída, e não `HTTP 403`?
6. Por que o certificado do servidor não pode ter `clientAuth`?
7. Qual é o limite honesto da revogação por CRL neste projeto?
8. Por que metade dos testes verifica falhas?
9. Como você provaria, em dez segundos, que a checagem de CRL está mesmo ativa?

*Respostas: §1, §3, §Como rodar (barrado no handshake, CA desconhecida), §4, §Como rodar (caixa), §2, §4, §7, §Experimentos 1.*

---

**Voltar:** [../00-MAPA.md](../00-MAPA.md) · **Próximo:** [../10-fundamentos.md](../10-fundamentos.md)
