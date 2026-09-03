"""Interface de linha de comando do cofre."""

import argparse
import getpass
import os
import stat
import sys

from . import VERSAO, aead, chaves, formato, x25519

VARIAVEL_SENHA = "COFRE_SENHA"


def _obter_senha(confirmar: bool) -> str:
    """Lê a senha do ambiente ou do terminal.

    Por que NÃO existe uma opção --senha nesta CLI: argumentos de linha de
    comando aparecem em `ps aux` para todos os usuários da máquina e ficam no
    histórico do shell. A variável de ambiente é apenas um pouco melhor (ela
    vaza para processos filhos e para /proc/<pid>/environ do mesmo usuário) e
    existe aqui só para automação e para os testes.
    """
    do_ambiente = os.environ.get(VARIAVEL_SENHA)
    if do_ambiente:
        return do_ambiente
    senha = getpass.getpass("Senha do cofre: ")
    if not senha:
        raise SystemExit("erro: senha vazia")
    if confirmar:
        if senha != getpass.getpass("Repita a senha: "):
            raise SystemExit("erro: as senhas não conferem")
    return senha


def _ler(caminho: str) -> bytes:
    if caminho == "-":
        return sys.stdin.buffer.read()
    with open(caminho, "rb") as arquivo:
        return arquivo.read()


def _gravar(caminho: str, dados: bytes, forcar: bool, privado: bool = False) -> None:
    """Escrita atômica: grava num temporário e renomeia.

    Se o processo morrer no meio, o arquivo de destino continua íntegro — em
    vez de ficar meio cifrado, que é a maneira mais rápida de perder dados com
    uma ferramenta de criptografia.
    """
    if caminho == "-":
        sys.stdout.buffer.write(dados)
        return
    if os.path.exists(caminho) and not forcar:
        raise SystemExit(f"erro: {caminho} já existe (use --forcar para sobrescrever)")

    temporario = caminho + ".parcial"
    modo = stat.S_IRUSR | stat.S_IWUSR if privado else 0o644
    descritor = os.open(temporario, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, modo)
    with os.fdopen(descritor, "wb") as arquivo:
        arquivo.write(dados)
        arquivo.flush()
        os.fsync(arquivo.fileno())
    os.replace(temporario, caminho)


def _cmd_chave_nova(args) -> int:
    privada = chaves.gerar_privada()
    publica = x25519.chave_publica(privada)
    if os.path.exists(args.saida) and not args.forcar:
        raise SystemExit(f"erro: {args.saida} já existe (use --forcar para sobrescrever)")
    if args.forcar and os.path.exists(args.saida):
        os.remove(args.saida)
    chaves.gravar_privada(args.saida, privada, publica)
    print(f"chave privada gravada em {args.saida} (permissão 600)")
    print(f"chave pública: {chaves.codificar_publica(publica)}")
    return 0


def _cmd_cifrar(args) -> int:
    senha = _obter_senha(confirmar=True)
    dados = _ler(args.entrada)
    _gravar(args.saida, formato.cifrar_com_senha(dados, senha, log_n=args.log_n),
            args.forcar)
    print(f"cifrado: {args.entrada} -> {args.saida}", file=sys.stderr)
    return 0


def _cmd_decifrar(args) -> int:
    senha = _obter_senha(confirmar=False)
    arquivo = _ler(args.entrada)
    try:
        dados = formato.decifrar_com_senha(arquivo, senha)
    except aead.ErroDeAutenticacao:
        print("erro: senha incorreta ou arquivo adulterado", file=sys.stderr)
        return 2
    except formato.ArquivoInvalido as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 3
    _gravar(args.saida, dados, args.forcar)
    return 0


def _cmd_selar(args) -> int:
    publica = chaves.decodificar_publica(args.para)
    dados = _ler(args.entrada)
    _gravar(args.saida, formato.cifrar_para_chave(dados, publica), args.forcar)
    print(f"selado para {args.para}: {args.entrada} -> {args.saida}", file=sys.stderr)
    return 0


def _cmd_abrir(args) -> int:
    privada = chaves.ler_privada(args.chave)
    arquivo = _ler(args.entrada)
    try:
        dados = formato.decifrar_com_chave(arquivo, privada)
    except aead.ErroDeAutenticacao:
        print("erro: chave errada ou arquivo adulterado", file=sys.stderr)
        return 2
    except formato.ArquivoInvalido as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 3
    _gravar(args.saida, dados, args.forcar)
    return 0


def _cmd_autoteste(_args) -> int:
    """Confere as primitivas contra os vetores oficiais dos RFCs."""
    from . import kdf, poly1305

    falhas = 0

    def conferir(nome, obtido, esperado):
        nonlocal falhas
        ok = obtido == esperado
        falhas += 0 if ok else 1
        print(f"[{'ok ' if ok else 'FALHA'}] {nome}")

    chave = bytes(range(0x80, 0xA0))
    nonce = bytes.fromhex("070000004041424344454647")
    aad = bytes.fromhex("50515253c0c1c2c3c4c5c6c7")
    claro = (b"Ladies and Gentlemen of the class of '99: If I could offer you "
             b"only one tip for the future, sunscreen would be it.")
    saida = aead.cifrar(chave, nonce, claro, aad)
    conferir("RFC 8439 2.8.2 AEAD (etiqueta)", saida[-16:].hex(),
             "1ae10b594f09e26a7e902ecbd0600691")
    conferir("RFC 8439 2.5.2 Poly1305",
             poly1305.mac(bytes.fromhex(
                 "85d6be7857556d337f4452fe42d506a8"
                 "0103808afb0db2fd4abff6af4149f51b"),
                 b"Cryptographic Forum Research Group").hex(),
             "a8061dc1305136c6c22b8baf0c0127a9")
    conferir("RFC 7748 6.1 X25519 (segredo compartilhado)",
             x25519.segredo_compartilhado(
                 bytes.fromhex("77076d0a7318a57d3c16c17251b26645"
                               "df4c2f87ebc0992ab177fba51db92c2a"),
                 bytes.fromhex("de9edb7d7b7dc1b4d35b61c2ece43537"
                               "3f8343c85b78674dadfc7e146f882b4f")).hex(),
             "4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742")
    conferir("RFC 5869 A.1 HKDF-SHA256",
             kdf.hkdf(bytes.fromhex("0b" * 22),
                      bytes.fromhex("000102030405060708090a0b0c"),
                      bytes.fromhex("f0f1f2f3f4f5f6f7f8f9"), 42).hex(),
             "3cb25f25faacd57a90434f64d0362f2a2d2d0a90cf1a5a4c5db02d56"
             "ecc4c5bf34007208d5b887185865")
    print("autoteste: tudo certo" if not falhas else f"autoteste: {falhas} falha(s)")
    return 0 if not falhas else 1


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cofre",
        description="Cifra e decifra arquivos com ChaCha20-Poly1305, scrypt e X25519.",
        epilog=f"cofre {VERSAO} — material didático, não use em produção.")
    parser.add_argument("--versao", action="version", version=f"cofre {VERSAO}")
    sub = parser.add_subparsers(dest="comando", required=True)

    p = sub.add_parser("chave-nova", help="gera um par de chaves X25519")
    p.add_argument("--saida", default="cofre.chave", help="arquivo da chave privada")
    p.add_argument("--forcar", action="store_true")
    p.set_defaults(func=_cmd_chave_nova)

    p = sub.add_parser("cifrar", help="cifra um arquivo com senha")
    p.add_argument("--entrada", required=True, help="arquivo de entrada ou - para stdin")
    p.add_argument("--saida", required=True, help="arquivo de saída ou - para stdout")
    p.add_argument("--log-n", type=int, default=15, dest="log_n",
                   help="log2(N) do scrypt; 15 = 32 MiB de RAM por tentativa")
    p.add_argument("--forcar", action="store_true")
    p.set_defaults(func=_cmd_cifrar)

    p = sub.add_parser("decifrar", help="decifra um arquivo protegido por senha")
    p.add_argument("--entrada", required=True)
    p.add_argument("--saida", required=True)
    p.add_argument("--forcar", action="store_true")
    p.set_defaults(func=_cmd_decifrar)

    p = sub.add_parser("selar", help="cifra para uma chave pública")
    p.add_argument("--para", required=True, help="chave pública cofre1pub:...")
    p.add_argument("--entrada", required=True)
    p.add_argument("--saida", required=True)
    p.add_argument("--forcar", action="store_true")
    p.set_defaults(func=_cmd_selar)

    p = sub.add_parser("abrir", help="abre um arquivo selado, com a chave privada")
    p.add_argument("--chave", required=True)
    p.add_argument("--entrada", required=True)
    p.add_argument("--saida", required=True)
    p.add_argument("--forcar", action="store_true")
    p.set_defaults(func=_cmd_abrir)

    p = sub.add_parser("autoteste", help="confere as primitivas contra os RFCs")
    p.set_defaults(func=_cmd_autoteste)

    return parser


def main(argv=None) -> int:
    args = construir_parser().parse_args(argv)
    try:
        return args.func(args)
    except (chaves.ChaveMalFormada, formato.ArquivoInvalido, ValueError) as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 3
    except FileNotFoundError as erro:
        print(f"erro: arquivo não encontrado: {erro.filename}", file=sys.stderr)
        return 4
    except KeyboardInterrupt:
        print("\ninterrompido", file=sys.stderr)
        return 130
