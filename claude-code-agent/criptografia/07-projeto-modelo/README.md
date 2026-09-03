# `cofre` — projeto-modelo de criptografia aplicada

**Nível:** intermediário · **Última verificação:** 19/08/2026 ·
**Testado em:** Python 3.10.12, Ubuntu 22.04.5 LTS

Uma ferramenta de linha de comando **pequena mas inteira** que cifra e decifra
arquivos. Não é um trecho de exemplo: tem formato de arquivo versionado,
tratamento de erro, códigos de saída, permissões corretas nos arquivos de chave,
escrita atômica e 46 testes — dos quais 19 comparam as primitivas com os
**vetores de teste oficiais dos RFCs**.

Tudo em **Python puro da biblioteca padrão**. Zero dependências. Roda em
qualquer máquina com Python 3.8+.

> ⚠️ **Não use isto em produção.** As primitivas aqui produzem bytes idênticos
> aos do OpenSSL (há testes que provam), mas **não são de tempo constante** e
> não apagam segredos da memória. Isso é deliberado: o objetivo é você **ver**
> a matemática, não escondê-la atrás de uma biblioteca. Em produção use
> [`age`](https://github.com/FiloSottile/age), libsodium ou a biblioteca
> `cryptography`. O porquê está em
> [25-canais-laterais-e-implementacao.md](../25-canais-laterais-e-implementacao.md).

---

## O que ele faz

| Modo | Como protege | Para quê |
|---|---|---|
| **Senha** | scrypt (N=2¹⁵=32768, r=8, p=1 → 32 MiB por tentativa) → ChaCha20-Poly1305 | backup pessoal, arquivo que só você reabre |
| **Chave pública** | X25519 efêmero → HKDF-SHA256 → ChaCha20-Poly1305 | mandar arquivo para alguém, sem combinar senha antes |

---

## Pré-requisitos

- Python **3.8 ou superior** (usa `hashlib.scrypt`, que exige OpenSSL 1.1+ por baixo).
- Nada mais. Sem `pip install`, sem rede.

Confira:

```bash
python3 --version
# esperado: Python 3.8.0 ou superior
python3 -c "import hashlib; print(hashlib.scrypt(b'a', salt=b'b'*16, n=2, r=8, p=1).hex()[:8])"
# esperado: 8 caracteres hexadecimais; se der ValueError, seu Python foi
# compilado sem OpenSSL — veja ../03-instalacao.md
```

---

## Comandos exatos para rodar

```bash
cd criptografia/07-projeto-modelo

# 1. Conferir as primitivas contra os RFCs (leva menos de 1 segundo)
python3 cofre.py autoteste

# 2. Rodar a suíte inteira
./executar-testes.sh

# 3. Cifrar um arquivo com senha
echo "minha chave do cofre da vovó é 1985" > segredo.txt
python3 cofre.py cifrar --entrada segredo.txt --saida segredo.cofre

# 4. Ver que o conteúdo sumiu
xxd segredo.cofre | head -3

# 5. Decifrar
python3 cofre.py decifrar --entrada segredo.cofre --saida devolvido.txt
diff segredo.txt devolvido.txt && echo "idênticos"

# 6. Gerar um par de chaves
python3 cofre.py chave-nova --saida minha.chave

# 7. Selar um arquivo para uma chave pública (copie a chave impressa acima)
python3 cofre.py selar --para cofre1pub:... --entrada segredo.txt --saida carta.cofre

# 8. Abrir com a chave privada
python3 cofre.py abrir --chave minha.chave --entrada carta.cofre --saida carta.txt
```

Saída real do passo 1, nesta máquina, em 19/08/2026:

```
[ok ] RFC 8439 2.8.2 AEAD (etiqueta)
[ok ] RFC 8439 2.5.2 Poly1305
[ok ] RFC 7748 6.1 X25519 (segredo compartilhado)
[ok ] RFC 5869 A.1 HKDF-SHA256
autoteste: tudo certo
```

Saída real do passo 2:

```
Ran 46 tests in 0.870s

OK
```

### Sem digitar senha (automação e testes)

```bash
COFRE_SENHA='senha-de-teste' python3 cofre.py cifrar \
    --entrada segredo.txt --saida segredo.cofre --forcar
```

Repare que **não existe** uma opção `--senha`. Isso é uma decisão de projeto:
argumentos de linha de comando aparecem em `ps aux` para qualquer usuário da
máquina e ficam no histórico do shell. A variável de ambiente é só um pouco
melhor (vaza para processos filhos e para `/proc/<pid>/environ`) e existe
exclusivamente para automação.

---

## Estrutura de pastas

```
07-projeto-modelo/
├── cofre.py                        ponto de entrada (só chama cofrelib.cli)
├── executar-testes.sh              roda autoteste + suíte
├── cofrelib/
│   ├── __init__.py                 aviso de "não use em produção" e versão
│   ├── chacha20.py                 cifra de fluxo   (RFC 8439 §2.1–2.4)
│   ├── poly1305.py                 MAC de uso único (RFC 8439 §2.5)
│   ├── aead.py                     os dois juntos   (RFC 8439 §2.8)
│   ├── x25519.py                   Diffie-Hellman   (RFC 7748)
│   ├── kdf.py                      scrypt (RFC 7914) e HKDF (RFC 5869)
│   ├── chaves.py                   arquivos de chave, base64 e permissões
│   ├── formato.py                  cabeçalho versionado e autenticado
│   └── cli.py                      argparse, códigos de saída, escrita atômica
└── testes/
    ├── test_vetores_oficiais.py    19 testes contra os RFCs
    ├── test_formato_e_cli.py       23 testes de formato, chaves e CLI
    └── test_interoperabilidade.py  4 testes contra o OpenSSL (pulados se ausente)
```

Ordem de leitura recomendada: `chacha20.py` → `poly1305.py` → `aead.py` →
`x25519.py` → `kdf.py` → `formato.py`. Cada arquivo é curto e o comentário do
topo explica **por que** aquela peça existe, não só o que ela faz.

---

## O formato de arquivo, byte a byte

```
 modo senha (0x01)                         modo chave pública (0x02)
 ┌────────────────────────────────┐        ┌────────────────────────────────┐
 │ 0..5   "COFRE1"                │        │ 0..5   "COFRE1"                │
 │ 6      versão = 1              │        │ 6      versão = 1              │
 │ 7      modo   = 1              │        │ 7      modo   = 2              │
 │ 8      log2(N) do scrypt       │        │ 8..39  chave pública efêmera   │
 │ 9      r                       │        ├────────────────────────────────┤
 │ 10     p                       │        │ 40..   criptograma || etiqueta │
 │ 11..26 sal (16 B)              │        └────────────────────────────────┘
 │ 27..38 nonce (12 B)            │
 ├────────────────────────────────┤         tudo acima da linha dupla
 │ 39..   criptograma || etiqueta │         entra como AAD — é autenticado
 └────────────────────────────────┘         mas não é cifrado
```

Um arquivo de 18 bytes de conteúdo, no modo senha, ocupa 73 bytes:
39 de cabeçalho + 18 de criptograma + 16 de etiqueta. Criptografia autenticada
**sempre** cresce; quem promete "cifra sem overhead" está omitindo a etiqueta —
e, sem etiqueta, não há integridade.

---

## O que cada decisão de projeto ensina

| Decisão | Lição |
|---|---|
| **Cabeçalho inteiro como AAD** | Sem isso, o atacante troca `log2 N = 15` por `12` e o arquivo fica 8× mais barato de quebrar, sem tocar no criptograma. O teste `test_rebaixar_o_custo_do_scrypt_no_cabecalho_e_detectado` demonstra o ataque sendo bloqueado. |
| **Nonce zero no modo chave pública** | Nonce só precisa ser único *para aquela chave*. Como a chave sai de uma efêmera nova a cada arquivo, o par (chave, nonce) nunca repete. Copiar esse padrão para chave fixa seria catastrófico — e é por isso que o comentário no código grita isso. |
| **Sal e nonce aleatórios no modo senha** | Dois arquivos com o mesmo conteúdo e a mesma senha produzem bytes diferentes. Criptograma determinístico vaza igualdade — foi assim que o ECB do "pinguim do Tux" virou meme. |
| **`hmac.compare_digest` na etiqueta** | Comparação com `==` sai no primeiro byte diferente. Essa diferença de tempo é medível pela rede e reduz a forja de 2¹²⁸ para ~4 mil tentativas. |
| **Verificar antes de decifrar** | Encrypt-then-MAC. A ordem inversa obriga o receptor a processar dados não autenticados: é a raiz de POODLE, Lucky13 e todos os *padding oracles*. |
| **Faixa aceita de `log2 N` (10 a 22)** | Um arquivo pode ser hostil. `log2 N = 40` não é uma senha forte, é um pedido de negação de serviço com 140 TiB de RAM. |
| **`os.open` com modo 0600** | Criar o arquivo e depois chamar `chmod` deixa uma fresta em que outro usuário lê a chave. A permissão vai na criação. |
| **Recusar chave com permissão frouxa** | O `ssh` faz o mesmo, e por bom motivo: um `chmod 644` acidental no `~/.ssh/id_ed25519` é indistinguível de um comprometimento. |
| **Escrita atômica (`os.replace`)** | Processo morto no meio da gravação não pode deixar um arquivo meio cifrado. Perder dados é uma falha de segurança (disponibilidade). |
| **Erro genérico "senha incorreta ou arquivo adulterado"** | Distinguir as duas causas entrega um oráculo ao atacante. |
| **Versão no byte 6** | O dia em que o ChaCha20-Poly1305 for substituído, os arquivos antigos continuam legíveis. Formato sem versão é dívida técnica com juros compostos. |
| **`os.urandom`, nunca `random`** | `random` é Mersenne Twister: observando 624 saídas, reconstrói-se o estado interno e prevê-se todo o resto. |

---

## Desempenho medido (nesta máquina, 19/08/2026)

Intel Core i3-10100T @ 3.00 GHz, Ubuntu 22.04.5, Python 3.10.12, OpenSSL 3.0.2.

| Operação | Tempo | Vazão |
|---|---|---|
| `cofrelib` AEAD, 1 MiB | 2 763 ms | 0,36 MiB/s |
| OpenSSL ChaCha20-Poly1305, 1 MiB | 1,45 ms | 688 MiB/s |
| OpenSSL AES-256-GCM (blocos de 16 KiB) | — | 3 596 MB/s |
| `cofrelib` X25519, uma operação | 2 ms | — |
| OpenSSL X25519 | 0,038 ms | 26 270 op/s |
| scrypt N=2¹⁵ (32 MiB) | 122 ms | — |

Python puro é **~1 900× mais lento** que o OpenSSL na mesma cifra. Esse número
é a resposta honesta para "por que não escrevo minha própria criptografia?" —
e ele é o *menos* importante dos motivos. Os outros estão em
[75-armadilhas.md](../75-armadilhas.md).

---

## Exercícios sobre o projeto

1. Rode `python3 cofre.py cifrar` duas vezes no mesmo arquivo com a mesma
   senha e compare os resultados com `cmp`. Por que diferem? Quais bytes são
   iguais?
2. Abra um `.cofre` num editor hexadecimal e mude **um bit** do criptograma.
   Tente decifrar. Qual código de saída você recebe?
3. Mude o byte 8 (o `log2 N`) de 15 para 12 e tente decifrar. Explique a
   mensagem de erro em termos de AAD.
4. Meça o tempo de `--log-n 15` e `--log-n 20`. Quanto custa cada bit a mais
   de trabalho para o atacante?
5. Implemente `cofre.py assinar` usando HMAC-SHA256 e explique por que isso
   **não** é uma assinatura digital de verdade.
6. Acrescente compressão antes de cifrar. Pesquise "CRIME/BREACH" e explique
   por que essa "melhoria" pode vazar o conteúdo.

Respostas comentadas em [70-pratica.md](../70-pratica.md), laboratório 9.
