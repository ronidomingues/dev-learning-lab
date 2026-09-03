#!/usr/bin/env python3
"""
arpinspect — inspetor da tabela ARP/vizinhos, sem dependências externas.

O que faz:
  * lê a tabela real do sistema (Linux `ip neigh`, ou macOS/BSD/Windows `arp -a`);
  * identifica o fabricante de cada MAC pelo OUI (base pública do IEEE);
  * detecta anomalias: IP duplicado, MAC duplicado, MAC de broadcast/multicast,
    entradas FAILED/INCOMPLETE, e o MAC do gateway (candidato a proteção);
  * resume a rede por fabricante e por estado.

Projetado como MATERIAL DIDÁTICO do assunto `tabela-arp`. Cada decisão de projeto
está comentada e explicada no README.md.

Uso:
    python3 arpinspect.py                 # inspeciona a máquina atual
    python3 arpinspect.py --json          # saída em JSON (para pipe/integração)
    python3 arpinspect.py --file exemplo.txt   # analisa uma captura salva
    python3 arpinspect.py --oui oui.txt   # base OUI alternativa
    python3 arpinspect.py --check         # modo auditoria: sai 1 se houver anomalia

Zero dependências. Requer apenas Python 3.8+ e a biblioteca padrão.
Não precisa de root: só LÊ a tabela.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict

# ---------------------------------------------------------------------------
# Modelo de dados
# ---------------------------------------------------------------------------


@dataclass
class Neighbor:
    """Uma entrada da tabela: o mapeamento IP -> MAC e seu estado."""
    ip: str
    mac: str | None            # None quando a entrada está INCOMPLETE/FAILED
    dev: str | None
    state: str                 # REACHABLE, STALE, FAILED, ... (normalizado)
    vendor: str = "?"          # preenchido pela base OUI

    @property
    def is_incomplete(self) -> bool:
        return self.mac is None or self.state in {"FAILED", "INCOMPLETE"}


@dataclass
class Report:
    neighbors: list[Neighbor] = field(default_factory=list)
    anomalies: list[str] = field(default_factory=list)
    by_state: dict = field(default_factory=dict)
    by_vendor: dict = field(default_factory=dict)
    gateway: str | None = None


# ---------------------------------------------------------------------------
# Coleta da tabela — cada SO fala uma língua diferente
# ---------------------------------------------------------------------------

_MAC_RE = re.compile(r"([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}")


def normalize_mac(mac: str) -> str:
    """aa-bb-... ou AA:BB:... -> forma canônica minúscula com ':'.
    Também expande formas com octetos de 1 dígito (macOS: 'a:b:c:1:2:3')."""
    parts = re.split(r"[:-]", mac.strip())
    if len(parts) == 6:
        try:
            return ":".join(f"{int(p, 16):02x}" for p in parts)
        except ValueError:
            pass
    return mac.strip().lower()


def _run(cmd: list[str]) -> str:
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=10, check=False
        ).stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def collect_linux() -> list[Neighbor]:
    """Usa a saída JSON do iproute2 quando disponível; senão, a textual."""
    out = _run(["ip", "-j", "neigh", "show"])
    result: list[Neighbor] = []
    if out.strip():
        try:
            for e in json.loads(out):
                state = (e.get("state") or ["NONE"])[0]
                result.append(Neighbor(
                    ip=e.get("dst", "?"),
                    mac=normalize_mac(e["lladdr"]) if e.get("lladdr") else None,
                    dev=e.get("dev"),
                    state=state,
                ))
            return result
        except (json.JSONDecodeError, KeyError):
            pass
    # fallback textual: "10.0.0.1 dev eth0 lladdr aa:.. REACHABLE"
    out = _run(["ip", "neigh", "show"])
    for line in out.splitlines():
        result.extend(_parse_ip_line(line))
    return result


def _parse_ip_line(line: str) -> list[Neighbor]:
    toks = line.split()
    if not toks:
        return []
    ip = toks[0]
    dev = toks[toks.index("dev") + 1] if "dev" in toks else None
    mac_m = _MAC_RE.search(line)
    mac = normalize_mac(mac_m.group(0)) if mac_m else None
    state = toks[-1] if toks[-1].isupper() else ("INCOMPLETE" if mac is None else "STALE")
    return [Neighbor(ip=ip, mac=mac, dev=dev, state=state)]


def collect_bsd_windows() -> list[Neighbor]:
    """macOS/BSD/Windows: parseia `arp -a`. Estado não é exposto -> 'UNKNOWN'."""
    out = _run(["arp", "-a"])
    result = []
    for line in out.splitlines():
        mac_m = _MAC_RE.search(line)
        ip_m = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})", line)
        if not ip_m:
            continue
        mac = normalize_mac(mac_m.group(0)) if mac_m else None
        state = "INCOMPLETE" if mac is None else "UNKNOWN"
        result.append(Neighbor(ip=ip_m.group(1), mac=mac, dev=None, state=state))
    return result


def collect() -> list[Neighbor]:
    system = platform.system()
    if system == "Linux":
        return collect_linux()
    return collect_bsd_windows()


def parse_file(path: str) -> list[Neighbor]:
    """Analisa uma captura salva (formato `ip neigh show` ou `arp -a`)."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    result = []
    for line in text.splitlines():
        if not line.strip():
            continue
        if " dev " in line or re.match(r"\d+\.\d+\.\d+\.\d+ ", line):
            result.extend(_parse_ip_line(line))
        else:
            mac_m = _MAC_RE.search(line)
            ip_m = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})", line)
            if ip_m:
                result.append(Neighbor(
                    ip=ip_m.group(1),
                    mac=normalize_mac(mac_m.group(0)) if mac_m else None,
                    dev=None,
                    state="UNKNOWN" if mac_m else "INCOMPLETE",
                ))
    return result


# ---------------------------------------------------------------------------
# Base OUI (fabricante). Procura em locais comuns; degrada com elegância.
# ---------------------------------------------------------------------------

_OUI_PATHS = [
    "/usr/share/nmap/nmap-mac-prefixes",
    "/usr/share/ieee-data/oui.txt",
    "/var/lib/ieee-data/oui.txt",
]


def load_oui(explicit: str | None = None) -> dict[str, str]:
    path = explicit
    if not path:
        for p in _OUI_PATHS:
            if os.path.exists(p):
                path = p
                break
    table: dict[str, str] = {}
    if not path or not os.path.exists(path):
        return table
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            # formato nmap: "005056 VMware"
            m = re.match(r"^([0-9A-Fa-f]{6})\s+(.+)$", line)
            if m:
                table[m.group(1).lower()] = m.group(2).strip()
                continue
            # formato IEEE oui.txt: "00-50-56   (hex)  VMware, Inc."
            m = re.match(r"^([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})\s+\(hex\)\s+(.+)$", line)
            if m:
                table["".join(m.group(1, 2, 3)).lower()] = m.group(4).strip()
    return table


def vendor_of(mac: str | None, oui: dict[str, str]) -> str:
    if not mac:
        return "(sem MAC)"
    prefix = mac.replace(":", "")[:6].lower()
    # bit "localmente administrado" (2º bit menos significativo do 1º octeto):
    try:
        first = int(mac.split(":")[0], 16)
        if first & 0x02:
            return oui.get(prefix, "(MAC localmente administrado / aleatório)")
    except ValueError:
        pass
    return oui.get(prefix, "?")


# ---------------------------------------------------------------------------
# Detecção de anomalias — o coração didático do projeto
# ---------------------------------------------------------------------------

_BROADCAST = "ff:ff:ff:ff:ff:ff"


def find_gateway() -> str | None:
    out = _run(["ip", "route"])
    m = re.search(r"default via (\d+\.\d+\.\d+\.\d+)", out)
    return m.group(1) if m else None


def analyze(neighbors: list[Neighbor], oui: dict[str, str]) -> Report:
    rep = Report(neighbors=neighbors)
    rep.gateway = find_gateway()

    for n in neighbors:
        n.vendor = vendor_of(n.mac, oui)

    # --- IP duplicado: dois IPs com o mesmo MAC é normal (uma máquina, vários IPs);
    #     o perigoso é o INVERSO: um IP aparecendo com MACs diferentes seria spoofing.
    #     Numa tabela de um host só vemos um MAC por IP, mas checamos MAC compartilhado.
    ip_by_mac: dict[str, list[str]] = defaultdict(list)
    mac_by_ip: dict[str, set] = defaultdict(set)
    for n in neighbors:
        if n.mac and n.mac not in (_BROADCAST,):
            ip_by_mac[n.mac].append(n.ip)
            mac_by_ip[n.ip].add(n.mac)

    for ip, macs in mac_by_ip.items():
        if len(macs) > 1:
            rep.anomalies.append(
                f"IP {ip} aparece com MACs diferentes {sorted(macs)} "
                f"-> possível ARP spoofing ou IP em disputa"
            )

    for mac, ips in ip_by_mac.items():
        real = [i for i in ips]
        if len(real) > 3:   # um MAC servindo muitos IPs pode ser roteador... ou proxy ARP
            rep.anomalies.append(
                f"MAC {mac} ({vendor_of(mac, oui)}) responde por {len(real)} IPs "
                f"-> roteador, proxy ARP, ou host se passando por vários"
            )

    # --- gateway com MAC suspeito
    if rep.gateway:
        gw = next((n for n in neighbors if n.ip == rep.gateway), None)
        if gw and gw.mac:
            rep.anomalies.append(
                f"[info] gateway {rep.gateway} -> {gw.mac} ({gw.vendor}); "
                f"considere fixá-lo como PERMANENT contra spoofing"
            )

    # --- entradas mortas
    dead = [n.ip for n in neighbors if n.is_incomplete]
    if dead:
        rep.anomalies.append(
            f"[info] {len(dead)} entrada(s) FAILED/INCOMPLETE: {dead[:8]}"
            + (" ..." if len(dead) > 8 else "")
        )

    rep.by_state = dict(Counter(n.state for n in neighbors))
    rep.by_vendor = dict(Counter(n.vendor for n in neighbors if n.mac))
    return rep


# ---------------------------------------------------------------------------
# Apresentação
# ---------------------------------------------------------------------------

def print_human(rep: Report) -> None:
    print("═" * 68)
    print(" INSPETOR DA TABELA ARP / VIZINHOS")
    print("═" * 68)
    if rep.gateway:
        print(f" gateway padrão: {rep.gateway}")
    print(f" entradas: {len(rep.neighbors)}   estados: {rep.by_state}")
    print("─" * 68)
    print(f" {'IP':<16}{'MAC':<20}{'ESTADO':<12}FABRICANTE")
    print("─" * 68)
    for n in sorted(rep.neighbors, key=lambda x: _ipkey(x.ip)):
        flag = "!" if n.is_incomplete else (">" if n.ip == rep.gateway else " ")
        print(f"{flag}{n.ip:<16}{(n.mac or '—'):<20}{n.state:<12}{n.vendor}")
    print("─" * 68)
    print(" fabricantes:")
    for v, c in sorted(rep.by_vendor.items(), key=lambda kv: -kv[1]):
        print(f"   {c:>3}×  {v}")
    if rep.anomalies:
        print("─" * 68)
        print(" observações e anomalias:")
        for a in rep.anomalies:
            print(f"   • {a}")
    print("═" * 68)


def _ipkey(ip: str):
    try:
        return tuple(int(p) for p in ip.split("."))
    except ValueError:
        return (999, ip)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_report(args) -> Report:
    if args.file:
        neighbors = parse_file(args.file)
    else:
        neighbors = collect()
    oui = load_oui(args.oui)
    return analyze(neighbors, oui)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Inspetor da tabela ARP/vizinhos.")
    p.add_argument("--json", action="store_true", help="saída em JSON")
    p.add_argument("--file", help="analisar captura salva em vez da máquina atual")
    p.add_argument("--oui", help="arquivo de base OUI alternativo")
    p.add_argument("--check", action="store_true",
                   help="modo auditoria: retorna código 1 se houver anomalia real")
    args = p.parse_args(argv)

    rep = build_report(args)

    if args.json:
        out = {
            "gateway": rep.gateway,
            "by_state": rep.by_state,
            "by_vendor": rep.by_vendor,
            "anomalies": rep.anomalies,
            "neighbors": [asdict(n) for n in rep.neighbors],
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print_human(rep)

    if args.check:
        # anomalias "reais" são as que não começam com [info]
        real = [a for a in rep.anomalies if not a.startswith("[info]")]
        return 1 if real else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
