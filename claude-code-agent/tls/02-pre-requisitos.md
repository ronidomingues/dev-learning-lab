# 02 · Pré-requisitos

**Nível:** iniciante · **Data:** 31/08/2026

O que você precisa saber, ter e instalar antes de começar — com a verdade sobre
quanto tempo cada nível leva e o que fazer se faltar alguma peça.

---

## 1. Conhecimento

### 1.1 Indispensável (sem isso o material não faz sentido)

| Pré-requisito | O quanto | Onde aprender |
|---|---|---|
| **Usar um terminal** | abrir, navegar com `cd`/`ls`, rodar um comando, ler a saída, entender código de saída | [The Missing Semester of Your CS Education (MIT, grátis)](https://missing.csail.mit.edu/) · [curso-docker/03](../curso-docker/) tem uma introdução |
| **Editar um arquivo de texto** | `nano`, `vim` ou VS Code — abrir, editar, salvar | qualquer tutorial de `nano` de 10 minutos |
| **Cliente e servidor** | saber que um programa "escuta" numa porta e outro "conecta" | [portas-de-rede](../portas-de-rede/00-MAPA.md) |
| **O que é um IP e um nome de domínio** | que `example.com` vira um IP via DNS | [portas-de-rede/10](../portas-de-rede/) |
| **O que é HTTP** | requisição, resposta, cabeçalho, código 200/404 | [apis](../apis/00-MAPA.md) |

### 1.2 Ajuda muito (dá para começar sem, mas você vai voltar aqui)

| Pré-requisito | Por que ajuda | Onde aprender |
|---|---|---|
| **Noções de criptografia** | TLS é uma montagem de primitivas; sem saber o que é uma chave pública, o handshake vira mágica | [criptografia](../criptografia/00-MAPA.md) — leia `01`, `10` e `11`, é suficiente |
| **TCP/IP básico** | entender por que TLS roda "sobre" TCP e o que muda no QUIC | [portas-de-rede](../portas-de-rede/00-MAPA.md) |
| **Um pouco de Python ou Node** | os exemplos e o projeto-modelo são em Python; há exemplos em Node, Go e Java | [engenharia-de-software-com-ia](../engenharia-de-software-com-ia/00-MAPA.md) |
| **Docker** | vários laboratórios ficam triviais com container; sem ele há caminho alternativo | [curso-docker](../curso-docker/) |
| **DNS na prática** | apontar um registro A é pré-requisito para emitir certificado real | [hospedagem-de-aplicacoes-web](../hospedagem-de-aplicacoes-web/00-MAPA.md) |

### 1.3 O que **não** é pré-requisito (embora pareça)

- **Matemática avançada.** Só o arquivo [60-teoria-avancada.md](60-teoria-avancada.md)
  exige — e ele avisa. Você pode configurar TLS de produção a vida inteira sem
  saber o que é uma curva elíptica. Saber ajuda a não fazer besteira, mas não é porta de entrada.
- **Saber programar em C.** Só se você for ler o código do OpenSSL, o que é opcional.
- **Ter servidor próprio.** Quase tudo roda em `localhost`. Só a parte de certificado
  público (Let's Encrypt) exige um domínio e uma máquina alcançável da internet — e
  há um caminho alternativo com desafio DNS ou com o ambiente de teste (*staging*).

---

## 2. Ambiente

### 2.1 Mínimo absoluto

| Item | Requisito |
|---|---|
| Sistema operacional | Linux, macOS ou Windows 10/11 (com WSL2 recomendado) |
| Memória | 2 GB livres. Wireshark com captura grande pede mais |
| Disco | ~2 GB para todas as ferramentas do [03](03-instalacao.md); ~200 MB só para o essencial |
| Rede | conexão à internet; se houver proxy corporativo, leia a seção específica do [03](03-instalacao.md#rede-corporativa) |
| Privilégio | conta com `sudo`/Administrador para instalar pacotes e para escutar em portas < 1024 |

### 2.2 Software (detalhado no [03-instalacao.md](03-instalacao.md))

| Ferramenta | Versão mínima | Para quê | Obrigatório? |
|---|---|---|---|
| **OpenSSL** | 3.0 (3.5+ para ML-KEM) | inspecionar, gerar, testar TLS | **sim** |
| **curl** | 7.70 | testar conexões | **sim** |
| **Python** | 3.9 | exemplos e projeto-modelo | **sim** |
| Node.js | 20 | exemplos em JS | não |
| mkcert | 1.4 | certificados locais confiáveis sem dor | recomendado |
| certbot ou Caddy | qualquer atual | certificado público automático | só na parte de ACME |
| nginx | 1.24 | configuração de servidor real | só no [17](17-configuracao-de-servidores.md) |
| Wireshark | 4.0 | ver o handshake no fio | recomendado no [70](70-pratica.md) |
| testssl.sh | 3.0.6 | auditoria de configuração | recomendado |
| Docker | 24 | laboratórios isolados | opcional, facilita muito |

### 2.3 Contas em serviço

| Serviço | Precisa? | Custo | Cartão de crédito? |
|---|---|---|---|
| Let's Encrypt | só para certificado público real | gratuito | **não** |
| Um domínio (`.com.br`, `.dev`, …) | só para certificado público real | R$ 40–70/ano típico | sim, para registrar |
| Uma VM com IP público | só para o desafio HTTP-01 | a partir de ~US$ 4/mês | sim |
| SSL Labs / Hardenize | opcional, teste online | gratuito | não |

> **Você não precisa de nada disso para 90% do curso.** Uma CA própria em `localhost`
> exercita exatamente a mesma mecânica. Detalhes de preço em [80-custos-e-licencas.md](80-custos-e-licencas.md).

---

## 3. Tempo realista

Honesto, não otimista. Assume estudo concentrado, com as mãos no teclado.

| Nível | O que você consegue fazer | Arquivos | Tempo |
|---|---|---|---|
| **Sobrevivência** | pôr HTTPS no ar num site, renovando sozinho, sem entender por dentro | 01, 03, 04, 16 | **3 a 5 horas** |
| **Operacional** | configurar nginx/Caddy direito, diagnosticar erro de certificado, montar CA interna, fazer mTLS | + 05, 06, 07, 13, 17, 18, 75 | **20 a 30 horas** |
| **Competente** | entender o handshake, escolher cifras com critério, avaliar risco, auditar configuração alheia, responder a CVE | + 10, 11, 12, 14, 15, 20, 21, 70 | **60 a 90 horas** |
| **Especialista** | discutir trade-offs de protocolo, ler RFC como documento de trabalho, planejar migração PQ, projetar PKI de empresa | + 19, 60, 65 | **6 a 12 meses de convívio** |
| **Pesquisa** | provar propriedades, achar ataque novo, contribuir com a IETF | 60, 65, 90, 95 + papers | **anos** |

**Onde as pessoas travam, em ordem de frequência:**

1. **Confundir formatos de arquivo** (PEM, DER, PKCS#12, JKS) e passar o arquivo errado
   para o programa errado. Resolvido no [13](13-certificados-e-pki.md) e no [05](05-manual-de-uso.md).
2. **Não entender a cadeia** e servir só o certificado folha, sem os intermediários.
   Funciona no seu navegador (que tem cache) e falha no `curl` do cliente. Clássico.
3. **Achar que TLS 1.3 basta** e deixar TLS 1.0 habilitado "por compatibilidade".
4. **Renovação manual** — e o certificado vence às 3h da manhã de um domingo.
5. **Chave privada versionada no Git.** Acontece toda semana, em toda empresa.

---

## 4. Rota de resgate — se faltar um pré-requisito

| Falta… | Rota curta (para hoje) | Rota certa (para a semana) |
|---|---|---|
| terminal | use o terminal do VS Code; copie e cole os comandos deste curso literalmente | Missing Semester (MIT), 2 aulas |
| criptografia | leia só [criptografia/01](../criptografia/01-introducao-leigo.md); aceite "chave pública cifra, privada decifra" como caixa-preta por ora | [criptografia](../criptografia/00-MAPA.md) blocos A e 10–11 |
| rede/HTTP | aceite "cliente abre conexão na porta 443 do servidor" | [portas-de-rede](../portas-de-rede/00-MAPA.md) e [apis](../apis/00-MAPA.md) |
| domínio próprio | use `mkcert` e `localhost` — 100% do aprendizado, 0% do custo | registre um `.dev` ou `.xyz` barato quando quiser praticar ACME de verdade |
| máquina com IP público | use o desafio **DNS-01** (não exige porta 80 aberta) ou o *staging* do Let's Encrypt | VM de US$ 4–5/mês; veja [80](80-custos-e-licencas.md) |
| permissão de administrador | use Docker (`docker run` traz OpenSSL, nginx e curl prontos) ou os playgrounds online listados no [03](03-instalacao.md) | peça ao TI, ou use uma VM pessoal |
| tempo | faça só a trilha "precisa colocar HTTPS no ar hoje" do [00-MAPA.md](00-MAPA.md) | volte para o núcleo depois; o material não some |

---

## 5. Verificação: você está pronto?

Rode isto. Se as quatro linhas saírem sem erro, pode ir para o [03](03-instalacao.md)
— e talvez pular boa parte dele.

```bash
openssl version                 # espera-se: OpenSSL 3.x
curl --version | head -1        # espera-se: curl 7.7x ou 8.x
python3 --version               # espera-se: Python 3.9+
echo | openssl s_client -connect example.com:443 -brief 2>&1 | head -8
```

A última linha deve mostrar algo como:

```
Protocol version: TLSv1.3
Ciphersuite: TLS_AES_256_GCM_SHA384
Peer certificate: CN=*.example.com
Hash used: SHA256
Verification: OK
```

Se apareceu `Verification: OK`, seu sistema tem o repositório de raízes funcionando
e você acabou de fazer, à mão, o que o navegador faz milhares de vezes por dia.

---

## Autoteste

1. Qual é o único pré-requisito de conhecimento que, se faltar, torna este curso inviável?
2. Por que matemática avançada **não** é pré-requisito?
3. Quanto tempo, honestamente, até conseguir configurar nginx com TLS e diagnosticar um erro?
4. Você não tem domínio nem servidor público. O que faz para praticar mesmo assim?
5. Cite três erros que travam iniciantes, segundo a §3.
6. Que comando prova, em uma linha, que seu repositório de raízes funciona?
7. Por que `sudo` aparece nos requisitos, se TLS não é um programa a ser executado como root?

*Respostas: §1.1 (terminal), §1.3, §3 (20–30 h), §4 (mkcert + localhost), §3, §5, §2.1 (instalar pacotes e portas <1024).*

---

**Próximo:** [03-instalacao.md](03-instalacao.md) — o manual de campo.
