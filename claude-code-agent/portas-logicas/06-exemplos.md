# 06 · Exemplos — 12 circuitos completos

**Nível:** iniciante → avançado · **Data:** 14/08/2026

Todo código aqui é **completo e executável**. Nada de `...` no meio.

> **Estado de verificação, declarado:** os exemplos em **Python (1, 2, 4, 6, 7, 12) foram
> executados** em Python 3.10.12 / Ubuntu 22.04.5 em 14/08/2026, e as saídas mostradas nos
> comentários são as saídas reais. Os exemplos em **Verilog não puderam ser compilados**
> no ambiente onde este material foi escrito (Icarus Verilog não estava instalado e não
> havia permissão para instalá-lo). Eles seguem a sintaxe padrão IEEE 1364/1800 e os
> comandos de compilação estão indicados — se algum não compilar na sua máquina, o erro é
> meu, e a correção provável está na versão do simulador. Rode-os antes de confiar.

Cada exemplo segue a mesma forma: **problema → solução → explicação**.

| # | Exemplo | Nível | Tipo |
|---|---|---|---|
| 1 | [Inversor a partir de NAND](#exemplo-1--inversor-a-partir-de-nand) | trivial | Python |
| 2 | [Meio somador](#exemplo-2--meio-somador) | fácil | Python + Verilog |
| 3 | [Somador de 4 bits](#exemplo-3--somador-de-4-bits-com-testbench) | fácil | Verilog |
| 4 | [Multiplexador — o `if` do hardware](#exemplo-4--multiplexador-o-if-do-hardware) | fácil | Python + Verilog |
| 5 | [Decodificador 3→8](#exemplo-5--decodificador-38-endereçamento) | médio | Verilog |
| 6 | [Comparador de magnitude](#exemplo-6--comparador-de-magnitude) | médio | Python |
| 7 | [**Paridade — caso real: UART e ECC**](#exemplo-7--paridade--caso-real-uart-e-memória-ecc) | médio | Python + Verilog |
| 8 | [Display de 7 segmentos](#exemplo-8--decodificador-para-display-de-7-segmentos) | médio | Verilog |
| 9 | [**Anti-repique de botão — caso real**](#exemplo-9--anti-repique-de-botão--caso-real) | médio | Verilog |
| 10 | [Registrador de deslocamento (74HC595)](#exemplo-10--registrador-de-deslocamento-o-74hc595) | médio | Verilog |
| 11 | [Contador de 4 bits com testbench](#exemplo-11--contador-de-4-bits-com-testbench-completo) | avançado | Verilog |
| 12 | [**CRC/LFSR — caso real: Ethernet**](#exemplo-12--lfsr-e-crc--caso-real-ethernet-e-discos) | avançado | Python |

---

## Exemplo 1 — Inversor a partir de NAND

**Problema.** Você só tem portas NAND. Como fazer um NOT?

**Solução.**

```python
def nand(a, b):
    return 0 if (a == 1 and b == 1) else 1

def nao(a):
    """Um inversor com uma única porta NAND: ligue a entrada nos dois pinos."""
    return nand(a, a)

for a in (0, 1):
    print(f"NOT {a} = {nao(a)}")
# NOT 0 = 1
# NOT 1 = 0
```

**Explicação.** `NAND(a,a) = ¬(a·a)`. Pela lei de idempotência, `a·a = a`. Logo o resultado
é `¬a`. Custo: **1 porta**.

Esse truque é o primeiro degrau da prova de que NAND é funcionalmente completa: se você
tem NOT e NAND, tem AND (`NOT(NAND)`), e com AND e NOT tem OR (por De Morgan). Tendo AND,
OR e NOT, você tem tudo. Ver [`10-fundamentos.md`](10-fundamentos.md).

---

## Exemplo 2 — Meio somador

**Problema.** Somar dois bits, tratando corretamente o caso `1+1 = 10`.

**Solução em Python:**

```python
def xor(a, b):
    return 1 if a != b else 0

def e(a, b):
    return 1 if (a == 1 and b == 1) else 0

def meio_somador(a, b):
    return xor(a, b), e(a, b)     # (soma, vai_um)

print(" a b | soma vai-um")
for a in (0, 1):
    for b in (0, 1):
        s, v = meio_somador(a, b)
        print(f" {a} {b} |  {s}     {v}")
#  0 0 |  0     0
#  0 1 |  1     0
#  1 0 |  1     0
#  1 1 |  0     1
```

**Solução em Verilog:**

```verilog
// meio_somador.v
module meio_somador(
    input  wire a,
    input  wire b,
    output wire soma,
    output wire vai_um
);
    assign soma   = a ^ b;   // XOR: 1 quando as entradas diferem
    assign vai_um = a & b;   // AND: 1 só quando ambas são 1
endmodule
```

**Explicação.** A coluna `soma` da tabela-verdade é exatamente a tabela do XOR; a coluna
`vai_um`, a do AND. Esse é o método geral: escreva a tabela, olhe cada coluna de saída, e
procure a porta que a produz.

**Custo:** 6 portas NAND (XOR = 4, AND = 2).

---

## Exemplo 3 — Somador de 4 bits com testbench

**Problema.** Somar dois números de 4 bits, propagando o vai-um.

```verilog
// somador4.v — somador por propagação de vai-um (ripple carry)
module somador_completo(
    input  wire a, b, vem_um,
    output wire soma, vai_um
);
    assign soma   = a ^ b ^ vem_um;
    assign vai_um = (a & b) | ((a ^ b) & vem_um);
endmodule

module somador4(
    input  wire [3:0] a, b,
    input  wire       vem_um,
    output wire [3:0] soma,
    output wire       vai_um
);
    wire c1, c2, c3;
    somador_completo b0(.a(a[0]), .b(b[0]), .vem_um(vem_um), .soma(soma[0]), .vai_um(c1));
    somador_completo b1(.a(a[1]), .b(b[1]), .vem_um(c1),     .soma(soma[1]), .vai_um(c2));
    somador_completo b2(.a(a[2]), .b(b[2]), .vem_um(c2),     .soma(soma[2]), .vai_um(c3));
    somador_completo b3(.a(a[3]), .b(b[3]), .vem_um(c3),     .soma(soma[3]), .vai_um(vai_um));
endmodule
```

**Testbench exaustivo** — testa as 256 combinações:

```verilog
// tb_somador4.v
`timescale 1ns/1ps
module tb_somador4;
    reg  [3:0] a, b;
    wire [3:0] soma;
    wire       vai_um;
    integer i, j, erros;

    somador4 dut(.a(a), .b(b), .vem_um(1'b0), .soma(soma), .vai_um(vai_um));

    initial begin
        erros = 0;
        for (i = 0; i < 16; i = i + 1)
            for (j = 0; j < 16; j = j + 1) begin
                a = i[3:0]; b = j[3:0];
                #1;
                if ({vai_um, soma} !== (i + j)) begin
                    $display("ERRO: %0d + %0d deu %0d", i, j, {vai_um, soma});
                    erros = erros + 1;
                end
            end
        $display("%0d erros em 256 casos", erros);
        $finish;
    end
endmodule
```

Rode com:
```bash
iverilog -o somador4 somador4.v tb_somador4.v && ./somador4
# esperado: 0 erros em 256 casos
```

**Explicação.** O `vai_um` de cada estágio alimenta o `vem_um` do seguinte — daí o nome
*ripple* (ondulação). O defeito é o atraso: o bit 3 só fica correto depois que o vai-um
percorreu todos os anteriores. Para 64 bits isso é inaceitável, e usa-se
**carry-lookahead** ([`20-circuitos-combinacionais.md`](20-circuitos-combinacionais.md)).

Repare também no testbench: com 8 bits de entrada, **testar tudo** custa 256 casos.
Essa possibilidade de verificação exaustiva é um luxo que o software raramente tem.

---

## Exemplo 4 — Multiplexador: o `if` do hardware

**Problema.** Escolher entre dois valores, conforme um sinal de controle.

```python
def nand(a, b):
    return 0 if (a == 1 and b == 1) else 1

def nao(a):
    return nand(a, a)

def mux2(a, b, s):
    """Se s=0 passa `a`; se s=1 passa `b`. Custo: 4 NANDs."""
    ns = nao(s)
    return nand(nand(a, ns), nand(b, s))

for s in (0, 1):
    for a in (0, 1):
        for b in (0, 1):
            print(f"s={s} a={a} b={b} -> {mux2(a, b, s)}")
```

Em Verilog, o mesmo circuito cabe em um caractere:

```verilog
assign y = sel ? b : a;      // a ferramenta de síntese gera exatamente 4 NANDs
```

**Explicação.** Este é o circuito que corresponde ao `if` de uma linguagem de programação —
com uma diferença que muda tudo: **os dois lados são sempre calculados**. Em hardware não
existe curto-circuito. O ramo "não escolhido" está fisicamente lá, consumindo energia,
produzindo um resultado que o mux joga fora.

Consequência prática: em hardware, um `if` **não economiza tempo**; ele custa um mux.
Quem vem de software leva meses para internalizar isso.

Um mux 2ⁿ→1 pode implementar **qualquer** função booleana de n variáveis — é por isso que
as FPGAs são feitas de LUTs (tabelas de consulta), que são muxes com uma memória na entrada.

---

## Exemplo 5 — Decodificador 3→8 (endereçamento)

**Problema.** Transformar um número de 3 bits em "acione exatamente uma entre 8 linhas".

```verilog
// decodificador3x8.v
module decodificador3x8(
    input  wire [2:0] endereco,
    input  wire       habilita,
    output wire [7:0] linha
);
    // Cada linha é um AND que reconhece uma combinação específica.
    assign linha[0] = habilita & ~endereco[2] & ~endereco[1] & ~endereco[0];
    assign linha[1] = habilita & ~endereco[2] & ~endereco[1] &  endereco[0];
    assign linha[2] = habilita & ~endereco[2] &  endereco[1] & ~endereco[0];
    assign linha[3] = habilita & ~endereco[2] &  endereco[1] &  endereco[0];
    assign linha[4] = habilita &  endereco[2] & ~endereco[1] & ~endereco[0];
    assign linha[5] = habilita &  endereco[2] & ~endereco[1] &  endereco[0];
    assign linha[6] = habilita &  endereco[2] &  endereco[1] & ~endereco[0];
    assign linha[7] = habilita &  endereco[2] &  endereco[1] &  endereco[0];
endmodule
```

**Explicação.** Cada saída é um **mintermo**: um AND que só é verdadeiro para uma
combinação exata de entradas. O resultado é uma saída *one-hot* — exatamente um bit em 1.

É assim que uma memória encontra a palavra que você pediu, e é assim que um processador
decide qual instrução executar (é o que o [projeto-modelo](07-projeto-modelo/README.md)
faz com um decodificador 4→16).

**Atenção ao crescimento:** k entradas produzem 2ᵏ saídas, cada uma com um AND de k
entradas. Um decodificador de 32 bits de endereço teria 4 bilhões de saídas — impossível.
Por isso memórias usam decodificação **em dois níveis** (linha e coluna): a matriz é
endereçada por dois decodificadores pequenos em vez de um gigante. Essa é uma das
razões pelas quais DRAM tem os sinais RAS e CAS.

O CI equivalente é o **74138**, e ele é ativo em nível baixo (as saídas são 0 na linha
selecionada) — uma pegadinha clássica de bancada.

---

## Exemplo 6 — Comparador de magnitude

**Problema.** Descobrir se A > B, A = B ou A < B, para números de 4 bits.

```python
def nand(a, b): return 0 if (a == 1 and b == 1) else 1
def nao(a):     return nand(a, a)
def e(a, b):    return nao(nand(a, b))
def ou(a, b):   return nand(nao(a), nao(b))
def xnor(a, b): return nand(nand(a, b), nand(nao(a), nao(b)))   # 1 quando iguais

def comparador4(a, b):
    """a, b: listas de 4 bits, do MAIS significativo para o menos."""
    # Compara do bit mais significativo para baixo. O primeiro bit que difere decide.
    maior = 0
    menor = 0
    iguais_ate_aqui = 1
    for i in range(4):
        maior = ou(maior, e(iguais_ate_aqui, e(a[i], nao(b[i]))))
        menor = ou(menor, e(iguais_ate_aqui, e(nao(a[i]), b[i])))
        iguais_ate_aqui = e(iguais_ate_aqui, xnor(a[i], b[i]))
    return maior, iguais_ate_aqui, menor

def bits(n):
    return [(n >> i) & 1 for i in (3, 2, 1, 0)]

erros = 0
for x in range(16):
    for y in range(16):
        maior, igual, menor = comparador4(bits(x), bits(y))
        if (maior, igual, menor) != (1 if x > y else 0,
                                     1 if x == y else 0,
                                     1 if x < y else 0):
            erros += 1
print(f"{erros} erros em 256 comparações")
# 0 erros em 256 comparações
```

**Explicação.** A ideia é a mesma de comparar dois números decimais à mão: olhe o dígito
mais significativo primeiro; se forem iguais, passe ao próximo. O sinal `iguais_ate_aqui`
carrega essa informação para baixo — é uma **propagação em cadeia**, exatamente como o
vai-um do somador, e com o mesmo problema de atraso.

Alternativa mais barata quando só interessa `>=`: **subtraia e olhe o vai-um**. É o que a
ULA do projeto-modelo faz, e é por isso que processadores implementam comparação
reaproveitando o somador em vez de ter um comparador separado. Uma instrução `cmp` em x86
é literalmente uma subtração cujo resultado é descartado; só as flags ficam.

---

## Exemplo 7 — Paridade — caso real: UART e memória ECC

**Problema.** Detectar se um bit foi corrompido durante uma transmissão ou no
armazenamento.

```python
def nand(a, b): return 0 if (a == 1 and b == 1) else 1
def nao(a):     return nand(a, a)
def xor(a, b):
    n1 = nand(a, b)
    return nand(nand(a, n1), nand(b, n1))

def paridade(bits_lista):
    """Árvore de XOR: devolve 1 se o número de 1s for ímpar. Custo: 4·(N-1) NANDs."""
    r = bits_lista[0]
    for bit in bits_lista[1:]:
        r = xor(r, bit)
    return r

dado = [1, 0, 1, 1, 0, 0, 1, 0]      # 4 uns -> paridade par
p = paridade(dado)
print(f"dado={dado} paridade={p}")   # paridade=0

# Transmissão: envia-se dado + bit de paridade.
transmitido = dado + [p]

# Um bit vira no caminho (ruído na linha):
recebido = transmitido[:]
recebido[3] ^= 1

print("íntegro" if paridade(recebido) == 0 else "ERRO DETECTADO")
# ERRO DETECTADO
```

**Em Verilog, isso é um operador só:**

```verilog
assign paridade = ^dado;      // redução XOR sobre todo o barramento
```

**Onde isso é usado de verdade:**

| Sistema | Como usa |
|---|---|
| **UART** (serial, RS-232) | o nono bit de cada byte é a paridade. É o "8N1" / "8E1" das configurações de porta serial. |
| **Memória ECC** de servidor | usa SECDED (Hamming estendido): 8 bits extras por 64 → **corrige** 1 erro e **detecta** 2. São dezenas de árvores de XOR trabalhando a cada acesso. |
| **RAID 5** | o disco de paridade guarda o XOR dos outros. Se um disco morre, `A ⊕ B ⊕ P = C` recupera o conteúdo. |
| **Barramento PCIe, DDR** | paridade e CRC em cada transação. |

**A limitação, que é grave e vale saber:** paridade detecta um número **ímpar** de bits
trocados. Se dois bits virarem, ela não percebe. Por isso sistemas sérios usam CRC
(exemplo 12) ou códigos de Hamming, não paridade simples.

**Por que XOR e não outra coisa:** porque XOR é associativo, comutativo e sua própria
inversa (`A⊕B⊕B = A`). Essas três propriedades juntas permitem calcular a paridade em
qualquer ordem, em árvore, e desfazer a operação sem informação adicional. Nenhuma outra
porta tem esse conjunto. É a razão de o XOR estar em toda parte onde há detecção de erro
e criptografia.

---

## Exemplo 8 — Decodificador para display de 7 segmentos

**Problema.** Transformar um número de 4 bits (0–9) nos 7 sinais que acendem os segmentos
de um display.

```
     aaaa
    f    b
    f    b
     gggg
    e    c
    e    c
     dddd
```

```verilog
// display7seg.v — decodificador BCD para display de 7 segmentos (ânodo comum: 0 acende)
module display7seg(
    input  wire [3:0] digito,
    output reg  [6:0] segmentos   // ordem: {g,f,e,d,c,b,a}
);
    always @(*) begin
        case (digito)
            4'd0: segmentos = 7'b1000000;
            4'd1: segmentos = 7'b1111001;
            4'd2: segmentos = 7'b0100100;
            4'd3: segmentos = 7'b0110000;
            4'd4: segmentos = 7'b0011001;
            4'd5: segmentos = 7'b0010010;
            4'd6: segmentos = 7'b0000010;
            4'd7: segmentos = 7'b1111000;
            4'd8: segmentos = 7'b0000000;
            4'd9: segmentos = 7'b0010000;
            default: segmentos = 7'b0111111;   // traço: entrada inválida
        endcase
    end
endmodule
```

**Explicação.** Isto é lógica combinacional pura: 4 entradas, 7 saídas, e **cada saída é
uma função booleana independente** das 4 entradas. Minimizadas à mão com mapas de
Karnaugh, dão expressões como:

```
segmento_a = ¬d·¬c·¬b·a + ¬d·c·¬b·¬a + d·¬c·b·a + d·c·¬b·a
```

O `case` do Verilog descreve a mesma coisa de forma legível, e a ferramenta de síntese faz
a minimização — melhor e mais rápido do que qualquer humano. **Esse é o exemplo canônico
de por que ninguém mais minimiza à mão em produção.**

O `default` merece atenção: sem ele, o sintetizador infere um **latch** (porque você não
disse o que fazer nos casos 10–15, e "manter o valor anterior" é o comportamento
implícito). Latch acidental é o bug nº 1 de quem escreve Verilog há pouco tempo — ver
[`75-armadilhas.md`](75-armadilhas.md).

---

## Exemplo 9 — Anti-repique de botão — caso real

**Problema.** Um botão mecânico não fecha o contato uma vez: ele **repica**, gerando
dezenas de transições em 1–20 ms. Um contador ligado direto a um botão conta 7 quando você
apertou uma vez. Isso não é teoria — é o primeiro problema real de todo projeto com botão.

```verilog
// antirepique.v — filtra o repique exigindo estabilidade por N ciclos
module antirepique #(
    parameter CICLOS = 500_000        // 10 ms a 50 MHz
)(
    input  wire clk,
    input  wire botao_cru,
    output reg  botao_limpo
);
    reg [1:0]  sincronizador;         // dois flip-flops contra metaestabilidade
    reg [19:0] contador;

    // Etapa 1: sincronizar o sinal externo com o relógio.
    // Sinal assíncrono ligado direto num flip-flop pode deixá-lo metaestável.
    // Dois flip-flops em série reduzem essa probabilidade a valores desprezíveis.
    always @(posedge clk)
        sincronizador <= {sincronizador[0], botao_cru};

    // Etapa 2: só aceitar a mudança se ela persistir por CICLOS.
    always @(posedge clk) begin
        if (sincronizador[1] != botao_limpo) begin
            if (contador == CICLOS - 1) begin
                botao_limpo <= sincronizador[1];
                contador    <= 0;
            end else
                contador <= contador + 1;
        end else
            contador <= 0;
    end
endmodule
```

**Explicação.** Duas lições de hardware real, e ambas doem quando aprendidas em campo:

1. **O mundo físico é sujo.** Contatos repicam, sinais chegam com ruído, tensões demoram a
   subir. Todo circuito que fala com o mundo externo precisa de filtragem.
2. **Sinal assíncrono precisa ser sincronizado.** Ligar um botão diretamente a um
   flip-flop pode deixá-lo **metaestável** — nem 0 nem 1, por um tempo indefinido. A
   corrente de dois flip-flops ("sincronizador de dois estágios") é a solução padrão da
   indústria. Ver [`30-circuitos-sequenciais.md`](30-circuitos-sequenciais.md).

Um `<=` (atribuição não bloqueante) dentro de `always @(posedge clk)` descreve
flip-flops. Usar `=` ali é outro erro clássico.

---

## Exemplo 10 — Registrador de deslocamento: o 74HC595

**Problema.** Você tem 3 pinos livres no microcontrolador e precisa acionar 8 LEDs.

```verilog
// registrador_deslocamento.v — equivalente ao CI 74HC595
module reg_deslocamento(
    input  wire       clk_serial,     // relógio de entrada de dados
    input  wire       dado_serial,    // um bit por vez
    input  wire       clk_latch,      // "agora publique tudo de uma vez"
    output reg  [7:0] saida_paralela
);
    reg [7:0] deslocador;

    // A cada borda, tudo anda uma casa e o novo bit entra por baixo.
    always @(posedge clk_serial)
        deslocador <= {deslocador[6:0], dado_serial};

    // O latch de saída evita que os LEDs pisquem durante o carregamento.
    always @(posedge clk_latch)
        saida_paralela <= deslocador;
endmodule
```

**Explicação.** É a conversão **série → paralelo**: 8 pulsos de relógio entregam 8 bits
por um fio só. O CI 74HC595 faz exatamente isso, custa poucos reais e é o componente mais
usado do mundo Arduino por um motivo econômico simples: **pinos de microcontrolador são
caros, tempo não é**. Trocar largura por tempo é a decisão de engenharia mais comum que
existe.

O segundo registrador (o de latch) existe porque, sem ele, os LEDs mostrariam o lixo que
está passando enquanto os dados entram. Separar "carregar" de "publicar" é um padrão que
reaparece em toda parte — inclusive nos registradores sombra de um pipeline de CPU.

**Uma linha de Verilog descreve tudo:** `{deslocador[6:0], dado_serial}` — concatenação
que descarta o bit de cima e insere o novo embaixo. Um deslocamento é **refiação**, não
custa porta lógica nenhuma; o custo está nos 8 flip-flops.

---

## Exemplo 11 — Contador de 4 bits com testbench completo

**Problema.** Contar de 0 a 15, com reset e habilitação, e provar que funciona.

```verilog
// contador4.v
module contador4(
    input  wire       clk,
    input  wire       reset_n,      // ativo em nível BAIXO
    input  wire       habilita,
    output reg  [3:0] valor,
    output wire       transbordo
);
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n)
            valor <= 4'd0;             // reset assíncrono
        else if (habilita)
            valor <= valor + 4'd1;     // dá a volta sozinho em 15 -> 0
    end

    assign transbordo = habilita & (valor == 4'd15);
endmodule
```

```verilog
// tb_contador4.v
`timescale 1ns/1ps
module tb_contador4;
    reg clk = 0, reset_n = 0, habilita = 0;
    wire [3:0] valor;
    wire transbordo;
    integer i, erros = 0;

    contador4 dut(.clk(clk), .reset_n(reset_n), .habilita(habilita),
                  .valor(valor), .transbordo(transbordo));

    always #5 clk = ~clk;                    // relógio de 100 MHz

    initial begin
        $dumpfile("contador4.vcd");
        $dumpvars(0, tb_contador4);

        #12 reset_n = 1;                     // solta o reset
        if (valor !== 4'd0) begin $display("ERRO: reset falhou"); erros = erros + 1; end

        habilita = 1;
        for (i = 1; i <= 16; i = i + 1) begin
            @(posedge clk); #1;
            if (valor !== i[3:0]) begin
                $display("ERRO no passo %0d: esperado %0d, obtido %0d", i, i[3:0], valor);
                erros = erros + 1;
            end
        end

        habilita = 0;                        // congela
        @(posedge clk); @(posedge clk); #1;
        if (valor !== 4'd0) begin $display("ERRO: contou com habilita=0"); erros = erros + 1; end

        $display("%0d erros", erros);
        $finish;
    end
endmodule
```

```bash
iverilog -o contador4 contador4.v tb_contador4.v && ./contador4
# esperado: 0 erros
gtkwave contador4.vcd     # para ver as ondas
```

**Explicação.** Três detalhes que separam código de brinquedo de código profissional:

1. **`posedge clk or negedge reset_n`** descreve um flip-flop com reset **assíncrono** —
   ele age mesmo sem relógio. Toda FPGA e todo ASIC precisam disso, porque no instante em
   que a energia sobe ainda não há relógio confiável.
2. **`reset_n` ativo em baixo** é a convenção da indústria: a corrente elétrica em repouso
   (fio puxado para baixo) não deve ativar coisa nenhuma por acidente.
3. **O testbench verifica**, não apenas imprime. Um testbench que só imprime valores exige
   um humano olhando, e humanos não olham 256 linhas com atenção.

---

## Exemplo 12 — LFSR e CRC — caso real: Ethernet e discos

**Problema.** Detectar erros de transmissão de forma muito mais robusta que paridade.

```python
def crc8(dados, polinomio=0x07):
    """CRC-8 (polinômio ATM/ITU 0x07). Em hardware: 8 flip-flops e alguns XOR."""
    crc = 0
    for byte in dados:
        crc ^= byte                        # XOR do byte no registrador
        for _ in range(8):
            if crc & 0x80:                 # olha o bit mais significativo
                crc = ((crc << 1) ^ polinomio) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc

mensagem = b"portas logicas"
c = crc8(mensagem)
print(f"CRC-8 de {mensagem!r} = 0x{c:02X}")

# Corrompendo DOIS bits — o caso que a paridade simples não pega:
corrompida = bytearray(mensagem)
corrompida[0] ^= 0b0000_0011
print("igual" if crc8(bytes(corrompida)) == c else "ERRO DETECTADO")
# ERRO DETECTADO
```

**O circuito equivalente** — um LFSR (*linear feedback shift register*):

```
    ┌───┐  ┌───┐  ┌───┐  ┌───┐  ┌───┐  ┌───┐  ┌───┐  ┌───┐
 ┌─►│ D ├─►│ D ├─►│ D ├─►│ D ├─►│ D ├─►│ D ├─►│ D ├─►│ D ├─┬─►
 │  └───┘  └───┘  └─▲─┘  └───┘  └───┘  └─▲─┘  └─▲─┘  └───┘ │
 │                  │                    │      │          │
 │                 XOR◄──────────────────┴──────┴──────────┤
 └──────────────────┴───────────────────────────────────────┘
        realimentação nos bits indicados pelo polinômio
```

**Onde isso está em produção, agora:**

| Sistema | Uso |
|---|---|
| **Ethernet** | CRC-32 em **todo** quadro. Sua placa de rede calcula isso em hardware, na velocidade do fio, para cada pacote. |
| **SATA, NVMe, USB** | CRC em cada transação de dados |
| **ZIP, PNG, gzip** | CRC-32 para verificar integridade do arquivo |
| **Códigos de barra, QR Code** | Reed-Solomon (o primo mais poderoso, que corrige em vez de só detectar) |
| **Geração de ruído pseudoaleatório** | o mesmo LFSR, usado como gerador de sequência |

**Explicação.** Um CRC é a divisão do dado por um polinômio em aritmética módulo 2 — onde
somar é XOR e não há vai-um. Em hardware, isso vira um registrador de deslocamento com
XORs na realimentação: **algumas dezenas de portas** processando um bit por ciclo de
relógio, ou 32 bits por ciclo nas versões paralelas.

O motivo de ser tão superior à paridade: um CRC-32 bem escolhido detecta **todos** os erros
de até 3 bits, todas as rajadas de até 32 bits, e falha em passar despercebido com
probabilidade ~2⁻³². Paridade falha com probabilidade 1/2 para dois bits trocados.

E o motivo de ser barato o suficiente para estar em todo lugar: só usa XOR e flip-flop, as
duas peças mais simples do catálogo.

---

## Como rodar tudo isto

**Os exemplos em Python** (1, 2, 4, 6, 7, 12): copie o bloco para um arquivo `.py` e rode
`python3 arquivo.py`. Não há dependências.

**Os exemplos em Verilog** (2, 3, 5, 8, 9, 10, 11): salve os módulos e rode

```bash
iverilog -o saida arquivo.v tb_arquivo.v && ./saida
```

**Sem instalar nada:** cole o Verilog em https://www.edaplayground.com/ ou monte o
circuito em https://circuitverse.org/simulator.

---

## Autoteste

1. Por que `NAND(a,a)` é um inversor?
2. Qual porta produz a coluna `soma` de um meio somador, e qual produz o `vai-um`?
3. Por que um `if` em hardware **não** economiza tempo?
4. Quantas saídas tem um decodificador de k entradas? Por que isso limita o tamanho?
5. Que propriedade do XOR o torna a base de paridade, RAID e criptografia?
6. Por que a paridade simples não detecta dois bits trocados?
7. O que acontece se você esquecer o `default` num `case` de Verilog combinacional?
8. Por que um botão precisa de anti-repique **e** de sincronizador? São a mesma coisa?
9. Por que o 74HC595 é tão popular, em termos econômicos?
10. Por que o CRC é tão mais confiável que a paridade, e ainda assim barato em portas?

*(Respostas: 1 — a·a = a, então ¬(a·a) = ¬a; 2 — XOR e AND; 3 — os dois ramos são
calculados sempre, o `if` vira um mux; 4 — 2ᵏ saídas, o que fica impossível para endereços
largos, daí a decodificação em dois níveis; 5 — é associativo, comutativo e sua própria
inversa; 6 — dois erros mantêm a paridade do total; 7 — o sintetizador infere um latch
acidental; 8 — não: o anti-repique filtra ruído mecânico ao longo de milissegundos, o
sincronizador evita metaestabilidade na captura; 9 — pinos de microcontrolador são caros e
tempo é barato, então troca-se largura por tempo; 10 — porque é divisão polinomial, que
espalha a informação de todos os bits, e só usa XOR e flip-flop.)*
