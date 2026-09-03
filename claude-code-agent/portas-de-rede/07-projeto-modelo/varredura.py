"""
varredura.py — descobre portas abertas DE FORA, por tentativa de conexão TCP.

Diferença essencial em relação ao inventario.py:
  - inventario.py pergunta ao PRÓPRIO sistema o que ele abriu  → verdade absoluta,
    mas só funciona na máquina onde você está e onde você tem permissão.
  - varredura.py pergunta à REDE                               → funciona em qualquer
    alvo alcançável, mas devolve a verdade filtrada por firewalls, NAT e proxies.

As duas discordando é informação, não erro. Ver `75-armadilhas.md` do curso.

AVISO LEGAL: varrer máquina de terceiro sem autorização escrita é, no Brasil,
potencialmente enquadrável no art. 154-A do Código Penal (invasão de dispositivo
informático), além de violar o contrato de praticamente todo provedor. Este
programa recusa alvos fora de faixas privadas/loopback a menos que você passe
`--autorizado`, e essa flag é uma declaração sua, não uma permissão nossa.
"""

from __future__ import annotations

import concurrent.futures
import ipaddress
import socket
import ssl
import time
from dataclasses import dataclass

# Sondas que provocam resposta em protocolos que não falam primeiro.
# HTTP não diz nada até você pedir; SSH e SMTP cospem o banner sozinhos.
SONDAS: dict[int, bytes] = {
    80:   b"GET / HTTP/1.0\r\nHost: alvo\r\n\r\n",
    8080: b"GET / HTTP/1.0\r\nHost: alvo\r\n\r\n",
    8000: b"GET / HTTP/1.0\r\nHost: alvo\r\n\r\n",
    3000: b"GET / HTTP/1.0\r\nHost: alvo\r\n\r\n",
    6379: b"PING\r\n",           # Redis responde +PONG a quem chegar
    11211: b"version\r\n",       # memcached responde a versão
}

ABERTA = "aberta"
FECHADA = "fechada"
FILTRADA = "filtrada"


@dataclass
class Resultado:
    host: str
    porta: int
    estado: str
    latencia_ms: float | None = None
    banner: str = ""
    erro: str = ""

    def __str__(self) -> str:
        base = f"{self.host}:{self.porta} {self.estado}"
        if self.latencia_ms is not None:
            base += f" ({self.latencia_ms:.1f} ms)"
        if self.banner:
            base += f" | {self.banner}"
        return base


def _banner(sock: socket.socket, porta: int, espera: float) -> str:
    """Lê o que o serviço fala. Não interpreta: mostra os bytes como texto."""
    sock.settimeout(espera)
    try:
        if porta in SONDAS:
            sock.sendall(SONDAS[porta])
        dados = sock.recv(256)
    except (socket.timeout, OSError):
        return ""
    texto = dados.decode("utf-8", errors="replace").strip()
    return " ".join(texto.split())[:120]


def testar_porta(host: str, porta: int, timeout: float = 1.0,
                 pegar_banner: bool = False) -> Resultado:
    """
    Uma tentativa de connect(). Os três desfechos possíveis e o que cada um significa:

      conecta         → ABERTA    (chegou SYN-ACK: existe processo escutando)
      ECONNREFUSED    → FECHADA   (chegou RST: a máquina existe, ninguém escuta ali)
      timeout         → FILTRADA  (nada voltou: firewall descartou em silêncio)

    O terceiro caso é o que separa "não tem serviço" de "tem firewall".
    """
    inicio = time.perf_counter()
    familia = socket.AF_INET6 if ":" in host else socket.AF_INET
    s = socket.socket(familia, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, porta))
        ms = (time.perf_counter() - inicio) * 1000
        banner = _banner(s, porta, min(timeout, 1.5)) if pegar_banner else ""
        return Resultado(host, porta, ABERTA, ms, banner)
    except socket.timeout:
        return Resultado(host, porta, FILTRADA, erro="timeout")
    except ConnectionRefusedError:
        ms = (time.perf_counter() - inicio) * 1000
        return Resultado(host, porta, FECHADA, ms)
    except OSError as e:
        # ENETUNREACH, EHOSTUNREACH, EACCES do firewall local com REJECT...
        return Resultado(host, porta, FILTRADA, erro=f"{type(e).__name__}: {e}")
    finally:
        s.close()


def varrer(host: str, portas: list[int], timeout: float = 1.0,
           paralelismo: int = 100, pegar_banner: bool = False) -> list[Resultado]:
    """
    Varredura concorrente com pool de threads.

    Por que threads e não asyncio aqui: connect() bloqueante em thread é a forma
    mais simples de deixar isto legível, e o gargalo é a rede, não a CPU nem o GIL.
    Por que 100 e não 5000: cada thread é um socket e um descritor de arquivo;
    passar do `ulimit -n` derruba a varredura com "Too many open files", e uma
    rajada grande demais faz IDS te bloquear no meio do trabalho.
    """
    resultados: list[Resultado] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=paralelismo) as pool:
        futuros = {pool.submit(testar_porta, host, p, timeout, pegar_banner): p
                   for p in portas}
        for f in concurrent.futures.as_completed(futuros):
            resultados.append(f.result())
    return sorted(resultados, key=lambda r: r.porta)


def eh_alvo_local(host: str) -> bool:
    """Loopback, faixas privadas (RFC 1918) e link-local. O resto exige --autorizado."""
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(host) if not _eh_ip(host) else host)
    except (socket.gaierror, ValueError):
        return False
    return ip.is_loopback or ip.is_private or ip.is_link_local


def _eh_ip(texto: str) -> bool:
    try:
        ipaddress.ip_address(texto)
        return True
    except ValueError:
        return False


def certificado_tls(host: str, porta: int, timeout: float = 3.0) -> dict | None:
    """
    Prova que 'porta 443' e 'fala TLS' são coisas independentes: aqui perguntamos
    ao serviço, não ao número. Um HTTPS em 8443 responde; um HTTP em 443 falha.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with socket.create_connection((host, porta), timeout) as bruto:
            with ctx.wrap_socket(bruto, server_hostname=host) as tls:
                return {
                    "protocolo": tls.version(),
                    "cifra": tls.cipher()[0] if tls.cipher() else None,
                    "certificado_der_bytes": len(tls.getpeercert(binary_form=True) or b""),
                }
    except (OSError, ssl.SSLError) as e:
        return {"erro": f"{type(e).__name__}: {e}"}


# Conjuntos prontos de portas.
TOP_100 = [
    7, 20, 21, 22, 23, 25, 53, 67, 68, 69, 80, 88, 102, 110, 111, 123, 135, 137,
    138, 139, 143, 161, 162, 389, 443, 445, 465, 502, 514, 515, 587, 631, 636,
    873, 993, 995, 1080, 1194, 1433, 1521, 1723, 1883, 1900, 2049, 2181, 2375,
    2376, 3000, 3128, 3260, 3306, 3389, 4369, 4444, 5000, 5060, 5432, 5601,
    5672, 5900, 5985, 6000, 6379, 6443, 6667, 7001, 8000, 8006, 8080, 8081,
    8086, 8088, 8443, 8888, 9000, 9042, 9090, 9092, 9100, 9200, 9300, 9418,
    10000, 11211, 15672, 20000, 27017, 27018, 44818, 50000, 5353, 8883, 1521,
    2379, 2380, 10250, 10255, 30000, 32768,
]


def expandir_portas(spec: str) -> list[int]:
    """Aceita '22', '1-1024', '22,80,443', 'top100', 'all'."""
    spec = spec.strip().lower()
    if spec == "top100":
        return sorted(set(TOP_100))
    if spec == "all":
        return list(range(1, 65536))
    portas: set[int] = set()
    for parte in spec.split(","):
        parte = parte.strip()
        if "-" in parte:
            a, b = parte.split("-", 1)
            portas.update(range(int(a), int(b) + 1))
        elif parte:
            portas.add(int(parte))
    invalidas = [p for p in portas if not 1 <= p <= 65535]
    if invalidas:
        raise ValueError(f"portas fora da faixa 1-65535: {sorted(invalidas)[:5]}")
    return sorted(portas)
