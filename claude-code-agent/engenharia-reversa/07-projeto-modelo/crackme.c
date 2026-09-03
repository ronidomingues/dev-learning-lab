/*
 * crackme.c — alvo de treino de engenharia reversa
 * ================================================
 *
 * Um "crackme" é um programa feito DE PROPÓSITO para ser revertido: ele pede
 * uma senha/serial e você deve descobrir, analisando o binário, qual entrada
 * o faz imprimir "Acesso concedido". É o campo de treino legítimo do RE.
 *
 * Este crackme tem três níveis de dificuldade crescente, para exercitar:
 *   - nível 1: comparação de string em texto claro (achável com `strings`)
 *   - nível 2: senha derivada por transformação (XOR) — não aparece no binário
 *   - nível 3: verificação por checksum de serial — precisa entender a lógica
 *
 * COMPILAR (ver README.md):   make
 * A solução (o "gabarito" para conferir seu trabalho) está em SOLUCAO.md.
 *
 * Nada aqui é malicioso: é um programa de console que só compara strings.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* -------------------------------------------------------------------------
 * NÍVEL 1 — a senha está literalmente no binário.
 * Objetivo do aluno: achá-la com `strings` ou vendo o `.rodata`.
 * ------------------------------------------------------------------------- */
static int nivel1(const char *tentativa) {
    /* A string "senha secreta" abaixo vai parar na seção .rodata do ELF,
     * legível com `strings ./crackme`. É o primeiro "aha" do iniciante. */
    const char *senha = "engenharia-reversa-2026";
    return strcmp(tentativa, senha) == 0;
}

/* -------------------------------------------------------------------------
 * NÍVEL 2 — a senha correta NÃO aparece no binário.
 * O que aparece é a versão "cifrada" (XOR byte a byte com a chave 0x42).
 * O aluno precisa: (a) achar o array cifrado, (b) entender o XOR, (c) reverter.
 * XOR é reversível: se c = p ^ k, então p = c ^ k.
 * ------------------------------------------------------------------------- */
static const unsigned char SEGREDO_CIFRADO[] = {
    /* "GhidraRadare" XOR 0x42 — gerado em tempo de escrita, verificado no teste */
    0x05, 0x2a, 0x2b, 0x26, 0x30, 0x23, 0x10, 0x23, 0x26, 0x23, 0x30, 0x27
};
#define SEGREDO_LEN (sizeof(SEGREDO_CIFRADO))
#define XOR_KEY 0x42

static int nivel2(const char *tentativa) {
    if (strlen(tentativa) != SEGREDO_LEN) return 0;
    for (size_t i = 0; i < SEGREDO_LEN; i++) {
        unsigned char esperado = SEGREDO_CIFRADO[i] ^ XOR_KEY;
        if ((unsigned char)tentativa[i] != esperado) return 0;
    }
    return 1;
}

/* -------------------------------------------------------------------------
 * NÍVEL 3 — um "serial" no formato AAAA-BBBB-CCCC (12 dígitos, 3 blocos de 4).
 * Regras que o serial deve satisfazer (o aluno descobre revertendo):
 *   R1: são exatamente 14 chars: 4 dígitos, '-', 4 dígitos, '-', 4 dígitos.
 *   R2: a soma de TODOS os 12 dígitos é 42.
 *   R3: o primeiro bloco, lido como número, é múltiplo de 7.
 * Há muitos seriais válidos — de propósito: espelha esquemas reais de licença.
 * ------------------------------------------------------------------------- */
static int eh_digito(char c) { return c >= '0' && c <= '9'; }

static int nivel3(const char *serial) {
    if (strlen(serial) != 14) return 0;                    /* R1: tamanho */
    if (serial[4] != '-' || serial[9] != '-') return 0;    /* R1: hífens  */

    int soma = 0;
    int idx[12] = {0,1,2,3, 5,6,7,8, 10,11,12,13};
    for (int i = 0; i < 12; i++) {
        char c = serial[idx[i]];
        if (!eh_digito(c)) return 0;                       /* R1: dígitos */
        soma += (c - '0');
    }
    if (soma != 42) return 0;                              /* R2: soma 42 */

    int bloco1 = (serial[0]-'0')*1000 + (serial[1]-'0')*100
               + (serial[2]-'0')*10   + (serial[3]-'0');
    if (bloco1 % 7 != 0) return 0;                         /* R3: mult. 7 */

    return 1;
}

static void uso(const char *prog) {
    fprintf(stderr,
        "uso: %s <nivel 1|2|3> <tentativa>\n"
        "  exemplo: %s 1 minha-tentativa\n", prog, prog);
}

int main(int argc, char **argv) {
    if (argc != 3) { uso(argv[0]); return 2; }

    int nivel = atoi(argv[1]);
    const char *tentativa = argv[2];
    int ok = 0;

    switch (nivel) {
        case 1: ok = nivel1(tentativa); break;
        case 2: ok = nivel2(tentativa); break;
        case 3: ok = nivel3(tentativa); break;
        default: uso(argv[0]); return 2;
    }

    if (ok) {
        printf("[+] Acesso concedido ao nivel %d. Bom trabalho, engenheiro(a) reverso(a).\n", nivel);
        return 0;
    } else {
        printf("[-] Acesso negado. Tente de novo.\n");
        return 1;
    }
}
