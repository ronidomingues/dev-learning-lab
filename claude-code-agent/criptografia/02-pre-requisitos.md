# 02 · Pré-requisitos

**Nível:** iniciante · **Última atualização:** 19/08/2026

Este arquivo é honesto a ponto de ser desagradável. Criptografia é um dos
poucos assuntos em que "aprender pela metade" é **pior que não aprender**:
quem sabe o suficiente para escrever código que cifra, mas não o suficiente
para saber o que está errado, constrói sistemas que parecem funcionar e não
protegem nada.

---

## 1. Conhecimento

### Indispensável

| O que | Em que nível | Onde aprender |
|---|---|---|
| **Linha de comando** | criar pastas, redirecionar saída, variáveis de ambiente, pipes | [Missing Semester do MIT](https://missing.csail.mit.edu/), aulas 1 e 2 (em inglês, com legendas); em português, o [Curso de Terminal do Linux](https://www.youtube.com/results?search_query=curso+terminal+linux) — procure um com mais de 3 h |
| **Uma linguagem de programação** | ler e escrever ~100 linhas com laços, funções e listas | Python é o padrão de fato no estudo de criptografia |
| **Bytes, bits e hexadecimal** | saber que 1 byte = 8 bits, ler `0x41` como 65 e como `'A'` | [portas-logicas](../portas-logicas/00-MAPA.md) desta pasta, arquivos 10 e 11 |
| **Codificação de texto** | por que UTF-8 existe, o que é Base64 e que **Base64 não é criptografia** | [variaveis-de-ambiente-e-segredos](../variaveis-de-ambiente-e-segredos/00-MAPA.md) |
| **Aritmética modular básica** | "que horas são 5 h depois das 22 h" — resto de divisão | Khan Academy, [Aritmética Modular](https://pt.khanacademy.org/computing/computer-science/cryptography) (em português) |

### Ajuda muito (mas dá para começar sem)

| O que | Onde entra no curso | Onde aprender |
|---|---|---|
| **Redes TCP/IP** | 20-tls-por-dentro, 21-pki | [portas-de-rede](../portas-de-rede/00-MAPA.md) e [tabela-arp](../tabela-arp/00-MAPA.md) |
| **HTTP e cabeçalhos** | TLS, HSTS, certificados | [apis](../apis/00-MAPA.md) |
| **Álgebra linear** | reticulados, criptografia pós-quântica | qualquer curso introdutório; só é exigido no arquivo 60 |
| **Teoria dos números** | RSA, curvas elípticas, provas | é ensinada no próprio curso, nos arquivos 17 e 18 |
| **Probabilidade** | entropia, provas de segurança, paradoxo do aniversário | básico de contagem já basta |
| **Inglês técnico de leitura** | RFCs, papers, documentação | inevitável a partir do nível intermediário |

### O que você **não** precisa

- Não precisa de faculdade de matemática. A parte formal deste curso é
  autocontida e construída do zero.
- Não precisa saber C. Ajuda no arquivo 25 (canais laterais), e só.
- Não precisa de hardware especial. Nenhum laboratório aqui exige HSM,
  YubiKey ou placa de vídeo.

---

## 2. Ambiente

| Item | Mínimo | Recomendado |
|---|---|---|
| Sistema operacional | Windows 10, macOS 12, ou qualquer Linux com kernel 5.x | Linux ou WSL2 — todas as ferramentas nascem lá primeiro |
| **Python** | 3.8 (por causa de `hashlib.scrypt`) | 3.11+ |
| **OpenSSL** | 1.1.1 | 3.5 LTS (suporte até 08/04/2030) |
| RAM | 2 GB | 8 GB (o scrypt sozinho pede 32 MiB por tentativa) |
| Disco | 500 MB | 2 GB, se for compilar OpenSSL |
| Conta em serviço | **nenhuma** | uma conta gratuita em nuvem, só para o arquivo 80 |
| Internet | para instalar e para os RFCs | — |

Nada neste curso exige cartão de crédito. Nenhum laboratório custa dinheiro.

---

## 3. Tempo realista

Números para uma pessoa que já programa, estudando com o material aberto e
fazendo os laboratórios. Se você não programa, some 40%.

| Meta | Tempo | O que você consegue fazer |
|---|---|---|
| Entender e conversar sobre o assunto | **6 a 10 h** | arquivos 01, 10, 11 e 12; explicar TLS na reunião sem falar besteira |
| Usar com segurança no dia a dia | **25 a 40 h** | Bloco A completo + 12 a 16 + 70; cifrar arquivos, gerar chaves, escolher biblioteca, revisar código alheio |
| Nível profissional aplicado | **120 a 200 h** | núcleo inteiro; projetar o uso de criptografia num sistema, operar rotação de chaves, ler um relatório de auditoria |
| Nível de pesquisa | **1 000 h ou mais, ao longo de anos** | arquivos 60 e 65, mais os livros de [90-bibliografia.md](90-bibliografia.md) e leitura contínua de papers |

**Sobre honestidade de prazos:** quem diz "aprenda criptografia em 30 dias"
está vendendo curso. Dan Boneh leva 12 semanas só na parte simétrica e
assimétrica básica, com alunos de Stanford em dedicação integral. O que se
consegue em um mês é usar bibliotecas corretamente — o que já é muito, e é
provavelmente o que você precisa.

---

## 4. Autoavaliação de 6 perguntas

Se você acerta 5, pode ir direto para o [03-instalacao.md](03-instalacao.md).
Se acerta 3 ou menos, faça a rota de resgate abaixo antes.

1. Quantos valores diferentes cabem em 1 byte?
2. O que `0x1F` vale em decimal?
3. Qual o resto de 17 dividido por 5? E de 2⁵ dividido por 7?
4. Escreva um comando que salve a saída de `ls` num arquivo.
5. Base64 protege um segredo? Por quê?
6. Em Python, o que `b"abc"` tem de diferente de `"abc"`?

*Respostas:* 1) 256. 2) 31. 3) 2 e 4 (32 = 4·7 + 4). 4) `ls > lista.txt`.
5) Não — é só uma re-representação, reversível por qualquer pessoa, sem chave.
6) `b"abc"` é uma sequência de bytes; `"abc"` é texto Unicode. Criptografia
opera sobre bytes, sempre; a conversão explícita entre os dois é fonte
constante de bug.

---

## 5. Rota de resgate

**Se travou nas perguntas 1, 2 ou 6 (bytes e representação)**
→ 3 h: [portas-logicas](../portas-logicas/00-MAPA.md), arquivos 01 e 10.
Depois abra um `python3` e brinque: `bytes([65,66])`, `"AB".encode()`,
`(0x1f)`, `int.from_bytes(b"\x01\x00", "big")`.

**Se travou na 3 (aritmética modular)**
→ 2 h: Khan Academy, módulo de aritmética modular, em português. Faça os
exercícios de "operador mod" e "exponenciação modular". É o único pré-requisito
matemático real.

**Se travou na 4 (terminal)**
→ 4 h: Missing Semester, aulas 1 e 2. Sem terminal, metade do curso fica
inacessível — todas as ferramentas de criptografia são de linha de comando.

**Se travou na 5**
→ Leia agora: Base64 é uma **codificação**, não uma cifra. Ela existe para
transportar bytes por canais que só aceitam texto. `echo c2VncmVkbw== | base64 -d`
devolve o conteúdo para qualquer pessoa, sem chave nenhuma. Confundir os dois é
o erro nº 1 de iniciante, e já vazou senha de produção em empresa grande.

**Se você não programa em nenhuma linguagem**
→ 20 a 30 h em Python básico antes de continuar. Você consegue ler os arquivos
01, 10 e 11 mesmo assim — eles não têm código.

---

## 6. Postura mental (o pré-requisito que ninguém lista)

Três hábitos que separam quem aprende criptografia de quem decora:

1. **Desconfie de si mesmo.** Se seu código cifra e decifra corretamente, isso
   não prova nada. Cifra quebrada também cifra e decifra corretamente. A prova
   é conferir com vetores de teste oficiais e com uma implementação
   independente — como faz o [projeto-modelo](07-projeto-modelo/README.md).
2. **Não invente.** A resposta certa para 99% das perguntas de projeto é "use
   a construção padrão da biblioteca padrão". A criatividade em criptografia
   aplicada é quase sempre um bug com nome bonito.
3. **Pergunte "contra quem?".** Nenhum sistema é "seguro" no vácuo. Seguro
   contra um colega curioso, contra um administrador de rede, contra o
   provedor de nuvem ou contra um Estado-nação são quatro projetos diferentes.
   Isso se chama **modelo de ameaça**, e é o primeiro passo de qualquer
   trabalho sério ([10-fundamentos.md](10-fundamentos.md), seção 6).

---

## Autoteste

1. Qual é a versão mínima de Python exigida por este curso, e por quê?
2. Quanto tempo, realisticamente, até você conseguir usar criptografia com
   segurança no dia a dia?
3. Você precisa saber álgebra linear para começar? A partir de qual arquivo
   ela aparece?
4. Por que "meu código cifra e decifra certo" não é evidência de correção?
5. O que é um modelo de ameaça, e por que ele vem antes da escolha do
   algoritmo?
6. Cite o pré-requisito matemático real deste curso e onde estudá-lo em
   duas horas.

---

**Anterior:** [01-introducao-leigo.md](01-introducao-leigo.md) ·
**Próximo:** [03-instalacao.md](03-instalacao.md)
