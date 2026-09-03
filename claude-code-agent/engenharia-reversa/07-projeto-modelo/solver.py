#!/usr/bin/env python3
"""
solver.py — solucionador AUTOMÁTICO do crackme (projeto-modelo de RE)
====================================================================

Este script encontra, SOZINHO, as três respostas do ./crackme — sem que a
resposta esteja escrita aqui. Ele demonstra três técnicas reais de engenharia
reversa automatizada, cada uma refletindo como um humano ataca cada nível:

  Nível 1  ->  "string harvesting + oráculo": colhe todas as strings legíveis
               do binário e testa cada uma contra o próprio programa.
               (É o que você faz à mão com `strings` + tentativa e erro.)

  Nível 2  ->  "ataque de chave XOR + oráculo": o texto claro não está no
               binário, só a versão cifrada. Varremos o arquivo, aplicamos XOR
               com todas as 256 chaves possíveis, e testamos os trechos que
               viram texto legível contra o programa. Nenhuma chave é chutada
               à mão — todas são tentadas.

  Nível 3  ->  "busca por restrições": após reverter a lógica (soma dos dígitos
               = 42, primeiro bloco múltiplo de 7, formato AAAA-BBBB-CCCC),
               codificamos essas REGRAS e deixamos o computador enumerar um
               serial válido, confirmando contra o binário. Espelha o que um
               reverser faz: entende as regras, depois gera uma entrada válida.
               (Alternativa profissional: execução simbólica com angr — ver
               comentário em solve_nivel3.)

O ponto pedagógico: em RE, o BINÁRIO É O ORÁCULO. Você não precisa ter certeza
da sua teoria — você testa a entrada candidata contra o programa real e ele diz
sim ou não. Todo este solver é construído em torno dessa ideia.

Uso:
    python3 solver.py ./crackme
Funciona também no binário SEM símbolos (./crackme_stripped), porque nenhuma
etapa depende de nomes de função — só do comportamento observável.
"""

import re
import string
import subprocess
import sys


def oraculo(binario: str, nivel: int, tentativa: str) -> bool:
    """Testa uma tentativa contra o programa real. É a única fonte de verdade.

    Retorna True se o crackme imprime "Acesso concedido". Note que NÃO
    inspecionamos a lógica interna aqui — só o comportamento, como uma
    caixa-preta. É o que torna o método robusto a ofuscação de nomes.
    """
    try:
        res = subprocess.run(
            [binario, str(nivel), tentativa],
            capture_output=True, text=True, timeout=5,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
    return "Acesso concedido" in res.stdout


def strings_do_binario(caminho: str, minimo: int = 4):
    """Extrai sequências ASCII imprimíveis do arquivo — igual ao `strings`.

    Um programa guarda literais de texto (como senhas em texto claro) na seção
    .rodata; elas aparecem como runs de bytes imprimíveis. Colhemos todas.
    """
    with open(caminho, "rb") as f:
        dados = f.read()
    padrao = re.compile(rb"[\x20-\x7e]{%d,}" % minimo)
    return [m.group().decode("ascii", "replace") for m in padrao.finditer(dados)]


def solve_nivel1(binario: str):
    """Colhe strings do binário e testa cada uma. A senha em texto claro cai."""
    print("[nivel 1] colhendo strings e testando contra o programa...")
    candidatos = strings_do_binario(binario)
    for s in candidatos:
        if oraculo(binario, 1, s):
            return s
    return None


def _bytes_das_secoes(binario: str):
    """Extrai os bytes das seções de DADOS (.rodata/.data) via objdump.

    Por que só as seções de dados? Porque é onde vivem constantes e arrays como
    o segredo cifrado — e restringir a busca a ~algumas centenas de bytes torna
    o ataque de chave instantâneo, em vez de varrer o arquivo inteiro (incluindo
    código executável, onde não há senhas).
    """
    dados = bytearray()
    for secao in (".rodata", ".data", ".data.rel.ro"):
        out = subprocess.run(
            ["objdump", "-s", "-j", secao, binario],
            capture_output=True, text=True,
        ).stdout
        for linha in out.splitlines():
            m = re.match(r"\s+[0-9a-f]+\s+([0-9a-f ]{1,35})", linha)
            if m:
                dados += bytes.fromhex(m.group(1).replace(" ", ""))
    return bytes(dados)


def solve_nivel2(binario: str):
    """Ataque de chave XOR: nenhuma chave é assumida, todas as 256 são testadas.

    Passos (o que um reverser faz ao suspeitar de XOR de byte único):
      1. pega os bytes das seções de dados (onde o segredo cifrado mora);
      2. desliza janelas e aplica XOR com cada uma das 256 chaves;
      3. mantém as decodificações que "têm cara de senha" (só caracteres de
         senha plausíveis) — filtro que derruba 99% do ruído;
      4. testa os sobreviventes no oráculo, dos mais "limpos" para os menos.
    Nada da resposta está embutido aqui: a chave 0x42 e o texto "GhidraRadare"
    emergem da varredura e são confirmados pelo programa real.
    """
    print("[nivel 2] extraindo secoes de dados e varrendo 256 chaves XOR...")
    dados = _bytes_das_secoes(binario)
    if not dados:
        return None

    charset_senha = set((string.ascii_letters + string.digits + "_-.").encode())
    candidatos = set()
    for L in range(6, 25):
        for i in range(len(dados) - L + 1):
            janela = dados[i:i + L]
            for k in range(1, 256):                 # k=0 = texto claro (nivel 1)
                dec = bytes(b ^ k for b in janela)
                if all(b in charset_senha for b in dec):
                    candidatos.add(dec.decode("ascii"))

    # ordena: primeiro os que parecem mais uma senha (só letras/dígitos, mais longos)
    def escore(s):
        return (all(c.isalnum() for c in s), len(s))
    ordenados = sorted(candidatos, key=escore, reverse=True)

    print(f"[nivel 2] {len(ordenados)} candidatos plausiveis; testando no oraculo...")
    for cand in ordenados:
        if oraculo(binario, 2, cand):
            return cand
    return None


def solve_nivel3(binario: str):
    """Busca por restrições, derivadas da engenharia reversa da função nivel3.

    Regras recuperadas do binário (ver SOLUCAO.md para o passo a passo):
      R1: formato AAAA-BBBB-CCCC (14 chars, 3 blocos de 4 digitos)
      R2: a soma dos 12 digitos e' 42
      R3: o primeiro bloco (como numero) e' multiplo de 7

    Em vez de forca bruta cega em 10^12, enumeramos apenas o que satisfaz R3 e
    completamos os digitos para satisfazer R2, confirmando cada palpite no
    oraculo. Encontra um serial valido em milissegundos.

    ALTERNATIVA PROFISSIONAL (execucao simbolica):
        import angr, claripy
        proj = angr.Project(binario)
        # ... cria estado com serial simbolico em argv[2], explora ate o bloco
        # que imprime "Acesso concedido", e pede ao solucionador SMT um valor.
        # Nao exige entender as regras — o SMT as deduz do proprio codigo.
        # Deixamos como exercicio no laboratorio (70-pratica.md), pois angr e'
        # pesado; a busca por restricoes abaixo e' auto-suficiente e verificavel.
    """
    print("[nivel 3] busca por restricoes (bloco1 multiplo de 7, soma 42)...")
    for bloco1 in range(0, 10000, 7):                 # R3: multiplos de 7
        d = [(bloco1 // 1000) % 10, (bloco1 // 100) % 10,
             (bloco1 // 10) % 10, bloco1 % 10]
        soma1 = sum(d)
        resto = 42 - soma1                            # R2: falta para 42
        if not (0 <= resto <= 72):                    # 8 digitos: max 72
            continue
        # distribui `resto` entre os 8 digitos dos blocos 2 e 3
        for combo in _particoes_8_digitos(resto):
            b1 = f"{bloco1:04d}"
            b2 = "".join(map(str, combo[:4]))
            b3 = "".join(map(str, combo[4:]))
            serial = f"{b1}-{b2}-{b3}"
            if oraculo(binario, 3, serial):
                return serial
    return None


def _particoes_8_digitos(alvo: int):
    """Gera algumas atribuicoes de 8 digitos (0-9) que somam `alvo`.

    Nao enumeramos todas (seriam muitas) — geramos as primeiras validas, o
    suficiente para o oraculo confirmar. Estrategia gulosa + poucas variacoes.
    """
    if alvo < 0 or alvo > 72:
        return
    # guloso: enche com 9s e ajusta o ultimo
    base = []
    restante = alvo
    for _ in range(8):
        v = min(9, restante)
        base.append(v)
        restante -= v
    if restante == 0:
        yield base
    # algumas permutacoes para robustez
    yield sorted(base)
    yield sorted(base, reverse=True)


def main():
    if len(sys.argv) != 2:
        print(f"uso: {sys.argv[0]} ./crackme")
        return 2
    binario = sys.argv[1]

    achados = {}
    achados[1] = solve_nivel1(binario)
    achados[2] = solve_nivel2(binario)
    achados[3] = solve_nivel3(binario)

    print("\n=== RESULTADO ===")
    ok = True
    for nivel in (1, 2, 3):
        resp = achados[nivel]
        if resp is None:
            print(f"nivel {nivel}: NAO RESOLVIDO")
            ok = False
        else:
            # confirmacao final no oraculo
            confere = oraculo(binario, nivel, resp)
            print(f"nivel {nivel}: {resp!r}  ->  {'CONFIRMADO' if confere else 'FALHOU'}")
            ok = ok and confere
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
