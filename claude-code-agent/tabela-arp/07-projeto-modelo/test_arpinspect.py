#!/usr/bin/env python3
"""Testes do arpinspect — rodam com `python3 -m unittest` ou `python3 test_arpinspect.py`.

Cobrem: normalização de MAC, parsing das duas gramáticas (ip neigh / arp -a),
lookup de OUI (incluindo bit localmente-administrado), e as três detecções de
anomalia que são o objetivo didático do projeto. Zero dependências, zero rede.
"""
import io
import os
import tempfile
import unittest

import arpinspect as A


class TestMac(unittest.TestCase):
    def test_normaliza_hifen_e_maiuscula(self):
        self.assertEqual(A.normalize_mac("AA-BB-CC-DD-EE-FF"), "aa:bb:cc:dd:ee:ff")

    def test_expande_octeto_de_um_digito(self):
        # macOS imprime 'a:b:c:1:2:3'
        self.assertEqual(A.normalize_mac("a:b:c:1:2:3"), "0a:0b:0c:01:02:03")

    def test_mac_invalido_passa_reto(self):
        self.assertEqual(A.normalize_mac("incompleto"), "incompleto")


class TestParseIpLine(unittest.TestCase):
    def test_linha_reachable(self):
        n = A._parse_ip_line("10.0.0.1 dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE")[0]
        self.assertEqual(n.ip, "10.0.0.1")
        self.assertEqual(n.mac, "aa:bb:cc:dd:ee:ff")
        self.assertEqual(n.dev, "eth0")
        self.assertEqual(n.state, "REACHABLE")

    def test_linha_failed_sem_mac(self):
        n = A._parse_ip_line("10.0.0.9 dev eth0 FAILED")[0]
        self.assertIsNone(n.mac)
        self.assertEqual(n.state, "FAILED")
        self.assertTrue(n.is_incomplete)

    def test_linha_vazia(self):
        self.assertEqual(A._parse_ip_line(""), [])


class TestOui(unittest.TestCase):
    def setUp(self):
        self.oui = {"005056": "VMware", "6c310e": "Cisco Systems"}

    def test_vendor_conhecido(self):
        self.assertEqual(A.vendor_of("00:50:56:ab:cd:ef", self.oui), "VMware")

    def test_vendor_desconhecido(self):
        self.assertEqual(A.vendor_of("99:99:99:00:00:00", self.oui), "?")

    def test_sem_mac(self):
        self.assertEqual(A.vendor_of(None, self.oui), "(sem MAC)")

    def test_bit_localmente_administrado(self):
        # 0x02 no primeiro octeto: MAC aleatório/local (privacidade Wi-Fi)
        v = A.vendor_of("02:11:22:33:44:55", self.oui)
        self.assertIn("localmente administrado", v)

    def test_carrega_formato_nmap(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write("005056 VMware\n6C310E Cisco Systems\n")
            path = fh.name
        try:
            table = A.load_oui(path)
            self.assertEqual(table["005056"], "VMware")
            self.assertEqual(table["6c310e"], "Cisco Systems")
        finally:
            os.unlink(path)

    def test_carrega_formato_ieee(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write("00-50-56   (hex)  VMware, Inc.\n")
            path = fh.name
        try:
            table = A.load_oui(path)
            self.assertEqual(table["005056"], "VMware, Inc.")
        finally:
            os.unlink(path)


class TestParseFile(unittest.TestCase):
    def test_le_arquivo_ip_neigh(self):
        data = "10.0.0.1 dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE\n10.0.0.9 dev eth0 FAILED\n"
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write(data)
            path = fh.name
        try:
            ns = A.parse_file(path)
            self.assertEqual(len(ns), 2)
            self.assertEqual(ns[0].ip, "10.0.0.1")
            self.assertTrue(ns[1].is_incomplete)
        finally:
            os.unlink(path)

    def test_le_arquivo_arp_a(self):
        data = "? (10.0.0.1) at aa:bb:cc:dd:ee:ff [ether] on en0\n"
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write(data)
            path = fh.name
        try:
            ns = A.parse_file(path)
            self.assertEqual(ns[0].ip, "10.0.0.1")
            self.assertEqual(ns[0].mac, "aa:bb:cc:dd:ee:ff")
        finally:
            os.unlink(path)


class TestAnomalias(unittest.TestCase):
    def _analyze(self, neighbors):
        return A.analyze(neighbors, {"005056": "VMware", "deadbe": "?"})

    def test_detecta_ip_com_dois_macs(self):
        ns = [
            A.Neighbor("10.0.0.1", "aa:bb:cc:00:00:01", "eth0", "REACHABLE"),
            A.Neighbor("10.0.0.1", "de:ad:be:ef:00:99", "eth0", "STALE"),
        ]
        rep = self._analyze(ns)
        self.assertTrue(any("MACs diferentes" in a for a in rep.anomalies),
                        f"esperava anomalia de spoofing, veio: {rep.anomalies}")

    def test_detecta_mac_servindo_muitos_ips(self):
        ns = [A.Neighbor(f"10.0.0.{i}", "00:50:56:11:22:33", "eth0", "REACHABLE")
              for i in range(50, 55)]
        rep = self._analyze(ns)
        self.assertTrue(any("responde por" in a for a in rep.anomalies),
                        f"esperava anomalia de MAC compartilhado, veio: {rep.anomalies}")

    def test_conta_estados(self):
        ns = [
            A.Neighbor("10.0.0.1", "aa:bb:cc:00:00:01", "eth0", "REACHABLE"),
            A.Neighbor("10.0.0.2", None, "eth0", "FAILED"),
            A.Neighbor("10.0.0.3", None, "eth0", "FAILED"),
        ]
        rep = self._analyze(ns)
        self.assertEqual(rep.by_state["FAILED"], 2)
        self.assertEqual(rep.by_state["REACHABLE"], 1)

    def test_rede_saudavel_sem_anomalia_real(self):
        ns = [
            A.Neighbor("10.0.0.10", "00:50:56:00:00:10", "eth0", "REACHABLE"),
            A.Neighbor("10.0.0.11", "00:50:56:00:00:11", "eth0", "STALE"),
        ]
        rep = self._analyze(ns)
        real = [a for a in rep.anomalies if not a.startswith("[info]")]
        self.assertEqual(real, [], f"rede saudável não deveria ter anomalia real: {real}")


class TestIntegracaoArquivoExemplo(unittest.TestCase):
    def test_arquivo_spoofing_do_repo(self):
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(here, "exemplo-spoofing.txt")
        if not os.path.exists(path):
            self.skipTest("arquivo de exemplo ausente")
        ns = A.parse_file(path)
        rep = A.analyze(ns, A.load_oui())
        real = [a for a in rep.anomalies if not a.startswith("[info]")]
        # o arquivo tem BOTH: IP com dois MACs E um MAC servindo 4 IPs
        self.assertTrue(len(real) >= 2, f"esperava >=2 anomalias reais, veio: {real}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
