#!/usr/bin/env python3
"""
alvo_laboratorio.py — abre um conjunto controlado de portas para você varrer.

Existe porque varrer a própria máquina "como ela está" é confuso: você não sabe
o que deveria estar lá. Aqui você sabe: o programa imprime exatamente o que abriu,
e então a varredura tem gabarito.

Abre, por padrão:
  - 3 portas TCP em 127.0.0.1  (só a própria máquina alcança)
  - 1 porta TCP em 0.0.0.0     (qualquer um na rede alcança — é o ponto da lição)
  - 1 porta UDP em 127.0.0.1
  - 1 porta TCP que ACEITA e cala (para você ver a diferença entre banner e silêncio)

Encerre com Ctrl+C. Nada fica para trás: são sockets de processo, não serviço.
"""

from __future__ import annotations

import argparse
import socket
import socketserver
import sys
import threading

BASE_PADRAO = 19000


class EcoBanner(socketserver.BaseRequestHandler):
    """Fala primeiro, como SSH e SMTP fazem."""
    banner = b"220 laboratorio-de-portas pronto\r\n"

    def handle(self) -> None:
        self.request.sendall(self.banner)
        try:
            dados = self.request.recv(1024)
            if dados:
                self.request.sendall(b"eco: " + dados)
        except OSError:
            pass


class HttpMinimo(socketserver.BaseRequestHandler):
    """Cala até você pedir, como HTTP faz."""

    def handle(self) -> None:
        try:
            self.request.recv(2048)
        except OSError:
            return
        corpo = b"laboratorio de portas\n"
        self.request.sendall(
            b"HTTP/1.1 200 OK\r\nServer: laboratorio/1.0\r\n"
            b"Content-Length: " + str(len(corpo)).encode() + b"\r\n"
            b"Connection: close\r\n\r\n" + corpo
        )


class Mudo(socketserver.BaseRequestHandler):
    """Aceita e não diz nada. É o que a maioria dos serviços binários faz."""

    def handle(self) -> None:
        try:
            self.request.recv(1024)
        except OSError:
            pass


class Servidor(socketserver.ThreadingTCPServer):
    daemon_threads = True
    # Sem isto, reiniciar o laboratório em menos de ~60 s falha com
    # "Address already in use" por causa do TIME_WAIT. Ver 13-tcp-por-dentro.md.
    allow_reuse_address = True


def sobe_tcp(ip: str, porta: int, handler) -> Servidor:
    srv = Servidor((ip, porta), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def sobe_udp(ip: str, porta: int) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, porta))

    def laco():
        while True:
            try:
                dados, origem = s.recvfrom(1024)
                s.sendto(b"udp-eco: " + dados, origem)
            except OSError:
                return

    threading.Thread(target=laco, daemon=True).start()
    return s


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Sobe portas controladas para praticar varredura.")
    p.add_argument("--base", type=int, default=BASE_PADRAO,
                   help=f"primeira porta a usar (padrão {BASE_PADRAO})")
    p.add_argument("--expor", action="store_true",
                   help="abre uma porta em 0.0.0.0 (alcançável pela rede). Cuidado.")
    args = p.parse_args(argv)
    b = args.base

    plano = [
        ("tcp", "127.0.0.1", b + 0, EcoBanner, "fala primeiro (banner tipo SMTP)"),
        ("tcp", "127.0.0.1", b + 1, HttpMinimo, "responde só depois do pedido (tipo HTTP)"),
        ("tcp", "127.0.0.1", b + 2, Mudo, "aceita e cala (tipo protocolo binário)"),
        ("udp", "127.0.0.1", b + 3, None, "UDP: sem conexão, sem LISTEN"),
    ]
    if args.expor:
        plano.append(("tcp", "0.0.0.0", b + 4, HttpMinimo, "EXPOSTA a toda a rede — é o alvo da lição"))

    vivos = []
    print("=" * 78)
    print("LABORATÓRIO DE PORTAS — gabarito do que foi aberto")
    print("=" * 78)
    for proto, ip, porta, handler, nota in plano:
        try:
            vivos.append(sobe_tcp(ip, porta, handler) if proto == "tcp" else sobe_udp(ip, porta))
            print(f"  {proto.upper():<4} {ip}:{porta:<6}  {nota}")
        except OSError as e:
            print(f"  {proto.upper():<4} {ip}:{porta:<6}  FALHOU: {e}")

    faixa = f"{b}-{b + (4 if args.expor else 3)}"
    print("=" * 78)
    print("Agora, em outro terminal:")
    print(f"  python3 auditor.py local --apenas-expostas")
    print(f"  python3 auditor.py varrer 127.0.0.1 -p {faixa} --banner")
    print(f"  ss -tulpn | grep -E ':({'|'.join(str(b + i) for i in range(5))})'")
    print("Ctrl+C encerra e libera tudo.")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\nencerrando; as portas voltam a ficar fechadas imediatamente "
              "(o LISTEN morre com o processo).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
