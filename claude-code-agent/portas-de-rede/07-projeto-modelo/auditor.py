#!/usr/bin/env python3
"""
auditor.py — CLI do projeto.

Três subcomandos, que correspondem às três perguntas do curso:

  local     "quais portas MINHA máquina abriu, e quem alcança cada uma?"
  varrer    "quais portas AQUELE host mostra para mim?"
  comparar  "o que o de dentro e o de fora dizem de diferente — e por quê?"

Zero dependências externas: só a biblioteca padrão do Python 3.10+.
"""

from __future__ import annotations

import argparse
import os
import sys

import relatorio
import varredura
from inventario import coletar, resumo_de_estados


def cmd_local(args) -> int:
    sockets = coletar(apenas_escutando=not args.tudo)
    if args.apenas_expostas:
        sockets = [s for s in sockets if s.exposto]
    if args.json:
        print(relatorio.para_json(sockets))
    else:
        print(relatorio.texto(sockets, cor=not args.sem_cor))
        if args.estados:
            print("\nESTADOS TCP NESTE MOMENTO:")
            for estado, n in resumo_de_estados().items():
                print(f"  {estado:<14} {n}")
    # Código de saída utilizável em CI: 1 se houver algo crítico.
    return 1 if any(relatorio.classificar(s)[0] == "critico" for s in sockets) else 0


def cmd_varrer(args) -> int:
    portas = varredura.expandir_portas(args.portas)
    if not varredura.eh_alvo_local(args.host) and not args.autorizado:
        print(f"RECUSADO: '{args.host}' não é loopback nem faixa privada.\n"
              f"Varrer host de terceiro sem autorização é crime (art. 154-A do CP) e\n"
              f"quebra o contrato do seu provedor. Se você TEM autorização escrita para\n"
              f"este alvo, repita com --autorizado.", file=sys.stderr)
        return 2
    print(f"varrendo {args.host}: {len(portas)} portas, timeout {args.timeout}s, "
          f"{args.paralelismo} conexões simultâneas...", file=sys.stderr)
    res = varredura.varrer(args.host, portas, args.timeout, args.paralelismo, args.banner)
    if args.json:
        import json
        from dataclasses import asdict
        print(json.dumps([asdict(r) for r in res], indent=2, ensure_ascii=False))
    else:
        print(relatorio.texto_varredura(res, args.host, cor=not args.sem_cor))
    return 0


def cmd_comparar(args) -> int:
    """
    O experimento mais instrutivo do projeto.

    Cruza o que o kernel diz (inventário) com o que a rede responde (varredura)
    no MESMO host, e nomeia cada divergência. Foi assim que, ao escrever este
    curso, descobrimos que a máquina de trabalho tinha um interceptador de
    tráfego respondendo por 17 portas que nenhum processo estava escutando.
    """
    sockets = coletar()
    locais_tcp = {s.porta_local for s in sockets if s.protocolo == "tcp"}
    portas = varredura.expandir_portas(args.portas)
    res = varredura.varrer("127.0.0.1", portas, args.timeout, args.paralelismo, args.banner)
    abertas_rede = {r.porta for r in res if r.estado == varredura.ABERTA}

    so_kernel = sorted(p for p in locais_tcp if p in set(portas) and p not in abertas_rede)
    so_rede = sorted(abertas_rede - locais_tcp)
    ambos = sorted(abertas_rede & locais_tcp)

    print(f"CONFRONTO — 127.0.0.1, {len(portas)} portas testadas\n")
    print(f"  concordam (kernel diz LISTEN e a rede conecta): {len(ambos)}")
    print(f"    {ambos}\n")
    print(f"  só o kernel vê (LISTEN mas a conexão não completa): {len(so_kernel)}")
    for p in so_kernel:
        print(f"    {p:>6}  → escuta em IP específico que não é 127.0.0.1, ou firewall local")
    print()
    print(f"  só a rede vê (conecta, mas NENHUM processo escuta): {len(so_rede)}")
    for p in so_rede:
        print(f"    {p:>6}  → redirecionamento no kernel (iptables/nftables REDIRECT ou "
              f"TPROXY), proxy transparente, agente de segurança, ou honeypot")
    if so_rede:
        print("\n  Como confirmar (precisa de root):")
        print("    sudo iptables -t nat -S | grep -E 'REDIRECT|DNAT|TPROXY'")
        print("    sudo nft list ruleset | grep -E 'redirect|dnat|tproxy'")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="auditor",
        description="Auditor de portas de rede — do inventário local à varredura.",
        epilog="Use com responsabilidade. Varredura sem autorização é ilegal.",
    )
    sub = p.add_subparsers(dest="comando", required=True)

    a = sub.add_parser("local", help="inventaria as portas abertas nesta máquina")
    a.add_argument("--json", action="store_true", help="saída em JSON")
    a.add_argument("--tudo", action="store_true", help="inclui conexões, não só quem escuta")
    a.add_argument("--apenas-expostas", action="store_true", help="omite o que só escuta em loopback")
    a.add_argument("--estados", action="store_true", help="mostra o histograma de estados TCP")
    a.add_argument("--sem-cor", action="store_true")
    a.set_defaults(func=cmd_local)

    b = sub.add_parser("varrer", help="testa portas de um host pela rede")
    b.add_argument("host")
    b.add_argument("-p", "--portas", default="top100",
                   help="'22', '1-1024', '22,80,443', 'top100', 'all' (padrão: top100)")
    b.add_argument("-t", "--timeout", type=float, default=1.0)
    b.add_argument("-P", "--paralelismo", type=int, default=100)
    b.add_argument("--banner", action="store_true", help="tenta ler o banner de cada porta aberta")
    b.add_argument("--autorizado", action="store_true",
                   help="declara autorização escrita para varrer alvo não privado")
    b.add_argument("--json", action="store_true")
    b.add_argument("--sem-cor", action="store_true")
    b.set_defaults(func=cmd_varrer)

    c = sub.add_parser("comparar", help="confronta o inventário local com a varredura de 127.0.0.1")
    c.add_argument("-p", "--portas", default="1-10000")
    c.add_argument("-t", "--timeout", type=float, default=0.3)
    c.add_argument("-P", "--paralelismo", type=int, default=200)
    c.add_argument("--banner", action="store_true")
    c.set_defaults(func=cmd_comparar)

    args = p.parse_args(argv)

    if args.comando in ("local", "comparar") and not os.path.exists("/proc/net/tcp"):
        print("ERRO: /proc/net/tcp não existe. Este subcomando só funciona em Linux.\n"
              "Em macOS use  lsof -i -P -n | grep LISTEN\n"
              "Em Windows use Get-NetTCPConnection -State Listen", file=sys.stderr)
        return 3

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
