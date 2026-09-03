"""
inventario.py — descobre as portas ABERTAS LOCALMENTE lendo /proc, sem chamar `ss`.

Por que reimplementar o `ss`: porque assim não sobra caixa-preta. O `ss` e o
`netstat` fazem exatamente isto — leem /proc/net/tcp (ou falam com o kernel via
netlink, no caso do `ss`) e cruzam o número de i-node do socket com os
descritores de arquivo em /proc/<pid>/fd para descobrir o dono. Depois de ler
este arquivo você nunca mais vai olhar a saída do `ss` como mágica.

Só funciona em Linux. Em macOS/Windows a fonte de dados é outra — veja o
`03-instalacao.md` e o `05-manual-de-uso.md` do curso.
"""

from __future__ import annotations

import os
import socket
import struct
from dataclasses import dataclass, field
from pathlib import Path

PROC = Path("/proc")

# Estados TCP, conforme include/net/tcp_states.h do kernel Linux.
# O /proc/net/tcp mostra o estado em hexadecimal.
ESTADOS_TCP = {
    0x01: "ESTABLISHED", 0x02: "SYN_SENT",  0x03: "SYN_RECV",
    0x04: "FIN_WAIT1",   0x05: "FIN_WAIT2", 0x06: "TIME_WAIT",
    0x07: "CLOSE",       0x08: "CLOSE_WAIT", 0x09: "LAST_ACK",
    0x0A: "LISTEN",      0x0B: "CLOSING",   0x0C: "NEW_SYN_RECV",
}


@dataclass
class Socket:
    protocolo: str          # "tcp" | "udp"
    familia: str            # "IPv4" | "IPv6"
    ip_local: str
    porta_local: int
    ip_remoto: str
    porta_remota: int
    estado: str
    inode: int
    uid: int
    pid: int | None = None
    processo: str | None = None
    cmdline: str = ""

    @property
    def escopo(self) -> str:
        """
        A pergunta que mais importa: quem alcança esta porta?

        Cuidado com '::ffff:127.0.0.1': é um endereço IPv4 embutido em IPv6
        (IPv4-mapped, RFC 4291 §2.5.5.2). Um socket IPv6 que aceita IPv4 mostra
        os pares IPv4 nesse formato. Quem trata isso como texto e testa
        `ip == "127.0.0.1"` classifica loopback como exposto — erro comum em
        script de auditoria caseiro.
        """
        ip = self.ip_local
        if ip.startswith("::ffff:"):
            ip = ip[7:]                # desembrulha o IPv4 mapeado
        if ip == "::1" or ip.startswith("127."):
            return "loopback"          # só a própria máquina
        if ip in ("0.0.0.0", "::"):
            return "todas-interfaces"  # qualquer um que alcance qualquer IP seu
        return "interface-especifica"

    @property
    def exposto(self) -> bool:
        return self.escopo != "loopback"


def _decodifica_endereco(campo: str) -> tuple[str, int]:
    """
    Converte 'B701A8C0:0016' em ('192.168.1.183', 22).

    O /proc/net/tcp grava o IP em hexadecimal, em ordem de bytes do HOST
    (little-endian no x86) — por isso o endereço parece embaralhado.
    Não é ofuscação: é o inteiro de 32 bits despejado como está na memória.
    """
    hex_ip, hex_porta = campo.split(":")
    porta = int(hex_porta, 16)

    if len(hex_ip) == 8:                      # IPv4
        bruto = struct.pack("<I", int(hex_ip, 16))
        return socket.inet_ntop(socket.AF_INET, bruto), porta

    # IPv6: quatro palavras de 32 bits, cada uma em ordem do host.
    palavras = [int(hex_ip[i:i + 8], 16) for i in range(0, 32, 8)]
    bruto = b"".join(struct.pack("<I", p) for p in palavras)
    return socket.inet_ntop(socket.AF_INET6, bruto), porta


def _le_tabela(caminho: Path, protocolo: str, familia: str) -> list[Socket]:
    if not caminho.exists():
        return []
    linhas = caminho.read_text().splitlines()[1:]   # descarta o cabeçalho
    saida: list[Socket] = []
    for linha in linhas:
        c = linha.split()
        if len(c) < 10:
            continue
        ip_l, porta_l = _decodifica_endereco(c[1])
        ip_r, porta_r = _decodifica_endereco(c[2])
        cod = int(c[3], 16)
        if protocolo == "tcp":
            estado = ESTADOS_TCP.get(cod, f"?{cod:02X}")
        else:
            # UDP não tem máquina de estados; o kernel usa 07 para "não conectado".
            estado = "UNCONN" if cod == 0x07 else ESTADOS_TCP.get(cod, "ESTAB")
        saida.append(Socket(
            protocolo=protocolo, familia=familia,
            ip_local=ip_l, porta_local=porta_l,
            ip_remoto=ip_r, porta_remota=porta_r,
            estado=estado, uid=int(c[7]), inode=int(c[9]),
        ))
    return saida


def _mapa_inode_para_processo() -> dict[int, tuple[int, str, str]]:
    """
    Percorre /proc/<pid>/fd/* procurando links do tipo 'socket:[12345]'.

    Só enxerga processos que o usuário atual pode ler. Rodando sem root você
    verá as portas de TODO mundo (a tabela /proc/net/tcp é pública) mas o dono
    aparecerá vazio para processos alheios — exatamente o que acontece com o
    `ss -tlnp` sem sudo. Isso não é bug: é a permissão funcionando.
    """
    mapa: dict[int, tuple[int, str, str]] = {}
    for dir_pid in PROC.iterdir():
        if not dir_pid.name.isdigit():
            continue
        pid = int(dir_pid.name)
        try:
            nome = (dir_pid / "comm").read_text().strip()
            cmdline = (dir_pid / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace").strip()
            for fd in (dir_pid / "fd").iterdir():
                try:
                    alvo = os.readlink(fd)
                except OSError:
                    continue
                if alvo.startswith("socket:["):
                    mapa[int(alvo[8:-1])] = (pid, nome, cmdline)
        except (PermissionError, FileNotFoundError, ProcessLookupError):
            continue          # processo de outro usuário, ou morreu no meio da varredura
    return mapa


def coletar(apenas_escutando: bool = True) -> list[Socket]:
    """Devolve os sockets locais, já com o processo dono resolvido quando possível."""
    sockets: list[Socket] = []
    sockets += _le_tabela(PROC / "net/tcp", "tcp", "IPv4")
    sockets += _le_tabela(PROC / "net/tcp6", "tcp", "IPv6")
    sockets += _le_tabela(PROC / "net/udp", "udp", "IPv4")
    sockets += _le_tabela(PROC / "net/udp6", "udp", "IPv6")

    if apenas_escutando:
        sockets = [s for s in sockets
                   if (s.protocolo == "tcp" and s.estado == "LISTEN")
                   or (s.protocolo == "udp" and s.estado == "UNCONN")]

    mapa = _mapa_inode_para_processo()
    for s in sockets:
        if s.inode in mapa:
            s.pid, s.processo, s.cmdline = mapa[s.inode]
    return sockets


def resumo_de_estados() -> dict[str, int]:
    """Conta os sockets TCP por estado. Útil para flagrar TIME_WAIT descontrolado."""
    contagem: dict[str, int] = {}
    for s in _le_tabela(PROC / "net/tcp", "tcp", "IPv4") + _le_tabela(PROC / "net/tcp6", "tcp", "IPv6"):
        contagem[s.estado] = contagem.get(s.estado, 0) + 1
    return dict(sorted(contagem.items(), key=lambda kv: -kv[1]))


def faixa_efemera() -> tuple[int, int]:
    """De onde saem as portas de origem dos SEUS clientes."""
    try:
        a, b = (PROC / "sys/net/ipv4/ip_local_port_range").read_text().split()
        return int(a), int(b)
    except OSError:
        return (32768, 60999)   # padrão histórico do Linux
