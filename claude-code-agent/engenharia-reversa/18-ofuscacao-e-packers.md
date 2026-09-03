# 18 · Ofuscação e packers — como o código se esconde

**Nível:** avançado · **Data:** 03/09/2026

Se reverter é sempre possível ([`10-fundamentos.md`](10-fundamentos.md)), a defesa só pode
**encarecer** o ataque, não impedi-lo. Ofuscação e packing são as técnicas para isso. Este
arquivo cataloga como o código se esconde e como cada camada se desfaz.

---

## 1. O princípio: adiar, não impedir

Todo esquema de proteção do lado do cliente esbarra no mesmo teto: **em algum momento o código
roda em claro**, e nesse instante é observável. Logo:

- **Ofuscação** transforma o código para ser difícil de *ler* (mas ele ainda roda).
- **Packing/criptografia** esconde o código até a hora de executar (mas ele se **desempacota**
  na memória — e você faz o dump).
- **Anti-análise** ([`19`](19-anti-analise.md)) detecta e atrapalha suas ferramentas.

A métrica correta não é "é seguro?" e sim "**quanto tempo/dinheiro custa quebrar?**". Um bom
esquema transforma minutos em semanas. Nenhum transforma semanas em "impossível".

---

## 2. Packers — comprimir/cifrar e restaurar em runtime

Um **packer** substitui o executável por um pequeno *stub* + o código original comprimido ou
cifrado. Ao rodar, o stub descomprime/decifra o original na memória e salta para ele (o **OEP**,
*Original Entry Point*).

```
  binário packed = [ stub desempacotador ] + [ código original comprimido/cifrado ]
        roda → stub restaura o original na memória → jmp OEP → programa roda normalmente
```

**Sinais de que um binário está packed:**
- `strings` mostra quase nada útil (só o stub).
- **Entropia alta** nas seções de código (dados comprimidos/cifrados parecem aleatórios) —
  ferramentas como `binwalk -E` ou DIE (Detect It Easy) medem isso.
- Poucos imports na IAT (o real é resolvido em runtime).
- Nomes de seção estranhos (`UPX0`, `UPX1`, `.packed`).

### Desempacotar
- **UPX** (o packer honesto): `upx -d BIN`. Só UPX oferece isso.
- **Genérico (dump após unpack):** rode sob depurador, coloque um breakpoint **no OEP** (onde o
  stub termina e salta para o código original — frequentemente um `jmp`/`ret` para uma região
  recém-escrita), e quando parar, **faça o dump da memória**. Ferramentas: **Scylla** (Windows,
  reconstrói a IAT), `x64dbg` + plugins, ou dump manual via GDB/`gcore`.
- **Emulação:** com Unicorn/Qiling, execute só o stub para obter o código desempacotado sem
  rodar o malware inteiro.

Achar o OEP é a arte: heurísticas incluem parar quando a execução salta para uma seção que
acabou de ser escrita (código automodificável), ou usar *hardware breakpoints* de execução na
região de destino.

---

## 3. Ofuscação de código — táticas e contramedidas

| Técnica | O que faz | Como se desfaz |
|---|---|---|
| **Renomeação/strip** | Remove nomes significativos | Renomear você mesmo; usar comportamento, não nomes |
| **String encryption** | Strings cifradas, decifradas em uso | Achar a rotina de decrypt e emulá-la (Unicorn) ou breakpoint após decifrar; FLOSS automatiza |
| **Dead code / junk** | Instruções inúteis para inflar/confundir | Análise de fluxo de dados elimina; descompilador ignora muito |
| **Control-flow flattening** | Transforma o CFG num grande `switch` dirigido por uma variável de estado | Recuperar a máquina de estados; ferramentas/deobfuscators específicos; execução simbólica |
| **Opaque predicates** | Condições sempre-verdadeiras/falsas que criam ramos mortos | Provar a condição (SMT/angr) e podar o ramo morto |
| **Instruction substitution** | Troca `a+b` por sequências equivalentes complicadas | Simplificação algébrica (peephole); IR do descompilador normaliza |
| **Virtualização (VM-based)** | Traduz o código para *bytecode* de uma VM embutida customizada | O mais caro: reverter a VM (o interpretador), recuperar o ISA, escrever um desmontador para ele |

**A mais dura é a virtualização de código** (VMProtect, Themida, Denuvo usam variações). O
código real vira bytecode de uma máquina virtual inventada; você precisa primeiro reverter **o
interpretador** para descobrir a arquitetura fictícia, depois desmontar o bytecode nela. Leva
semanas e é uma especialidade própria. Ainda assim, é *possível* — pesquisadores quebram Denuvo
repetidamente.

---

## 4. String encryption na prática (o caso mais comum)

Malware raramente deixa `http://c2-malicioso.com` em texto claro. Ele guarda cifrado e decifra
em uso. Três formas de recuperar:

1. **Estático + emulação:** ache a função de decrypt, isole-a, rode-a com Unicorn alimentando
   os bytes cifrados. Retorna as strings.
2. **Dinâmico:** breakpoint logo **após** a chamada de decrypt; leia a string já decifrada na
   memória.
3. **Automático:** **FLOSS** (FLARE Obfuscated String Solver, da Mandiant) emula funções de
   decrypt e extrai strings automaticamente. Primeira parada na triagem de malware.

---

## 5. Control-flow flattening — reconhecer e desfazer

O *flattening* substitui o fluxo natural por um laço central com um `switch(estado)`:
```c
estado = 1;
while (estado != 0) {
    switch (estado) {
        case 1: /* bloco A */ estado = 3; break;
        case 3: /* bloco B */ estado = 7; break;
        ...
    }
}
```
O CFG vira uma "estrela" em torno do dispatcher — visualmente inconfundível no *Function Graph*.
Desfazer = recuperar a ordem real dos blocos rastreando as transições de `estado`. Há plugins
(ex.: para Ghidra/IDA) e a **execução simbólica** ([`60`](60-teoria-avancada.md)) ajuda a
reconstruir o fluxo original.

---

## 6. A economia da ofuscação (por que ela existe se é quebrável)

Ofuscação é um cálculo econômico, não de segurança absoluta:

- **DRM de jogos (ex.: Denuvo):** só precisa proteger a *janela de lançamento* (as primeiras
  semanas de vendas). Se atrasa a pirataria em 2–4 semanas, já pagou por si. Quando quebra,
  muitas vezes é removido em patches por custar desempenho.
- **Malware:** ofusca para escapar de antivírus (assinaturas) e atrasar analistas o suficiente
  para a campanha render antes da detecção.
- **Propriedade intelectual:** dificultar o roubo de um algoritmo valioso — eleva o custo de
  copiá-lo acima do de licenciá-lo.

Em todos os casos, a pergunta é **custo × benefício**, e o defensor aceita que a proteção é
temporária. (Opinião do autor: gastar demais em ofuscação para dados/segredos que *deveriam*
estar no servidor é erro de arquitetura — mova o segredo, não o esconda no cliente.)

---

## 7. Fluxo recomendado diante de um binário protegido

1. **Detectar:** DIE/`binwalk -E` (entropia), contar imports, olhar nomes de seção. Está packed?
2. **Desempacotar:** UPX? `upx -d`. Senão, dump após OEP (dinâmico/emulação).
3. **Recuperar strings:** FLOSS; breakpoints após decrypt.
4. **Normalizar ofuscação de fluxo:** deobfuscators, simbólico, ou paciência manual.
5. **Só então** fazer a análise "normal" ([`14`](14-analise-estatica.md)/[`15`](15-analise-dinamica.md)).

---

## Autoteste

1. Enuncie por que packing "adia mas não impede" e onde o código fica exposto.
2. Cite três sinais de que um binário está *packed*.
3. O que é o **OEP** e por que achá-lo é a chave para desempacotar genericamente?
4. Como você recuperaria uma URL de C2 cifrada dentro de um malware? Dê duas abordagens.
5. Descreva *control-flow flattening* e como ele aparece no grafo de fluxo.
6. Por que a **virtualização de código** é a ofuscação mais cara de reverter?
7. Explique, com o exemplo do DRM de jogos, por que ofuscação é uma decisão econômica.
