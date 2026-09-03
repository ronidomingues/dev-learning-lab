#!/usr/bin/env python3
"""
testes.py — suíte do projeto. Roda com:  python3 testes.py

Testa o que é testável sem rede externa: decodificação do /proc, classificação
de risco, expansão de faixas de portas, e o comportamento real do scanner
contra sockets que o próprio teste abre.
"""

from __future__ import annotations

import socket
import threading
import unittest

import catalogo
import inventario
import relatorio
import varredura


class TestDecodificacaoProc(unittest.TestCase):
    """O /proc grava o IP em hexadecimal, na ordem de bytes do host."""

    def test_ipv4_loopback(self):
        # 0100007F = 0x7F000001 lido little-endian = 127.0.0.1 ; 0x0016 = 22
        self.assertEqual(inventario._decodifica_endereco("0100007F:0016"),
                         ("127.0.0.1", 22))

    def test_ipv4_qualquer_interface(self):
        self.assertEqual(inventario._decodifica_endereco("00000000:0050"),
                         ("0.0.0.0", 80))

    def test_ipv4_endereco_real(self):
        # 10.209.2.168 -> bytes 0A D1 02 A8 -> little-endian: A802D10A
        self.assertEqual(inventario._decodifica_endereco("A802D10A:1F90"),
                         ("10.209.2.168", 8080))

    def test_ipv6_curinga(self):
        ip, porta = inventario._decodifica_endereco("00000000000000000000000000000000:01BB")
        self.assertEqual((ip, porta), ("::", 443))

    def test_porta_efemera_alta(self):
        self.assertEqual(inventario._decodifica_endereco("0100007F:FFFF")[1], 65535)


class TestEstados(unittest.TestCase):
    def test_listen_e_0a(self):
        self.assertEqual(inventario.ESTADOS_TCP[0x0A], "LISTEN")

    def test_time_wait_e_06(self):
        self.assertEqual(inventario.ESTADOS_TCP[0x06], "TIME_WAIT")

    def test_todos_os_estados_cobertos(self):
        # O kernel define 12 estados na enum tcp_states.h (1..12).
        self.assertEqual(sorted(inventario.ESTADOS_TCP), list(range(1, 13)))


class TestEscopo(unittest.TestCase):
    def _sock(self, ip: str) -> inventario.Socket:
        return inventario.Socket("tcp", "IPv4", ip, 5432, "0.0.0.0", 0, "LISTEN", 1, 1000)

    def test_loopback_nao_e_exposto(self):
        s = self._sock("127.0.0.1")
        self.assertEqual(s.escopo, "loopback")
        self.assertFalse(s.exposto)

    def test_curinga_e_exposto(self):
        s = self._sock("0.0.0.0")
        self.assertEqual(s.escopo, "todas-interfaces")
        self.assertTrue(s.exposto)

    def test_ip_especifico_e_exposto(self):
        s = self._sock("192.168.0.10")
        self.assertEqual(s.escopo, "interface-especifica")
        self.assertTrue(s.exposto)

    def test_loopback_ipv6(self):
        s = inventario.Socket("tcp", "IPv6", "::1", 5432, "::", 0, "LISTEN", 1, 1000)
        self.assertFalse(s.exposto)

    def test_ipv4_mapeado_em_ipv6_ainda_e_loopback(self):
        # Pegadinha real: '::ffff:127.0.0.1' É loopback. Ver RFC 4291 §2.5.5.2.
        s = inventario.Socket("tcp", "IPv6", "::ffff:127.0.0.1", 9789, "::", 0, "LISTEN", 1, 1000)
        self.assertEqual(s.escopo, "loopback")
        self.assertFalse(s.exposto)

    def test_ipv4_mapeado_publico_continua_exposto(self):
        s = inventario.Socket("tcp", "IPv6", "::ffff:10.0.0.5", 9789, "::", 0, "LISTEN", 1, 1000)
        self.assertTrue(s.exposto)


class TestClassificacao(unittest.TestCase):
    """A tese central do projeto: o risco é do par (porta, escopo)."""

    def test_postgres_em_loopback_e_ok(self):
        s = inventario.Socket("tcp", "IPv4", "127.0.0.1", 5432, "0.0.0.0", 0, "LISTEN", 1, 1000)
        self.assertEqual(relatorio.classificar(s)[0], "ok")

    def test_mesmo_postgres_exposto_e_critico(self):
        s = inventario.Socket("tcp", "IPv4", "0.0.0.0", 5432, "0.0.0.0", 0, "LISTEN", 1, 1000)
        self.assertEqual(relatorio.classificar(s)[0], "critico")

    def test_https_exposto_e_ok(self):
        s = inventario.Socket("tcp", "IPv4", "0.0.0.0", 443, "0.0.0.0", 0, "LISTEN", 1, 1000)
        self.assertEqual(relatorio.classificar(s)[0], "ok")

    def test_porta_efemera_exposta_vira_atencao(self):
        ini, _ = inventario.faixa_efemera()
        s = inventario.Socket("tcp", "IPv4", "0.0.0.0", ini + 7, "0.0.0.0", 0, "LISTEN", 1, 1000)
        sev, motivo = relatorio.classificar(s)
        self.assertEqual(sev, "atencao")
        self.assertIn("efêmera", motivo)

    def test_docker_api_sem_tls_e_critico(self):
        s = inventario.Socket("tcp", "IPv4", "0.0.0.0", 2375, "0.0.0.0", 0, "LISTEN", 1, 1000)
        self.assertEqual(relatorio.classificar(s)[0], "critico")


class TestCatalogo(unittest.TestCase):
    def test_443_tcp_e_udp_sao_servicos_diferentes(self):
        tcp = catalogo.consultar(443, "tcp")
        udp = catalogo.consultar(443, "udp")
        self.assertNotEqual(tcp.proto_app, udp.proto_app)
        self.assertIn("QUIC", udp.proto_app)

    def test_faixas_iana(self):
        self.assertIn("sistema", catalogo.descrever_faixa(22))
        self.assertIn("usuário", catalogo.descrever_faixa(8080))
        self.assertIn("efêmeras", catalogo.descrever_faixa(50000))

    def test_nome_do_sistema_bate_com_etc_services(self):
        # Se este teste falhar, o /etc/services da sua distro é diferente — não é bug.
        self.assertEqual(catalogo.nome_do_sistema(22, "tcp"), "ssh")


class TestExpansaoDePortas(unittest.TestCase):
    def test_unica(self):
        self.assertEqual(varredura.expandir_portas("22"), [22])

    def test_lista(self):
        self.assertEqual(varredura.expandir_portas("22,80,443"), [22, 80, 443])

    def test_faixa(self):
        self.assertEqual(varredura.expandir_portas("20-25"), [20, 21, 22, 23, 24, 25])

    def test_mistura_e_ordena_sem_repetir(self):
        self.assertEqual(varredura.expandir_portas("80,20-22,80"), [20, 21, 22, 80])

    def test_all_tem_65535(self):
        self.assertEqual(len(varredura.expandir_portas("all")), 65535)

    def test_porta_invalida_levanta(self):
        with self.assertRaises(ValueError):
            varredura.expandir_portas("70000")


class TestVarreduraReal(unittest.TestCase):
    """Sobe sockets de verdade e confere os três desfechos do connect()."""

    @classmethod
    def setUpClass(cls):
        cls.srv = socket.socket()
        cls.srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        cls.srv.bind(("127.0.0.1", 0))
        cls.srv.listen(8)
        cls.porta_aberta = cls.srv.getsockname()[1]

        def aceita():
            while True:
                try:
                    c, _ = cls.srv.accept()
                    c.sendall(b"220 teste pronto\r\n")
                    c.close()
                except OSError:
                    return

        cls.t = threading.Thread(target=aceita, daemon=True)
        cls.t.start()

        # Uma porta comprovadamente fechada: abre, descobre o número, fecha.
        tmp = socket.socket()
        tmp.bind(("127.0.0.1", 0))
        cls.porta_fechada = tmp.getsockname()[1]
        tmp.close()

    @classmethod
    def tearDownClass(cls):
        cls.srv.close()

    def test_porta_aberta(self):
        r = varredura.testar_porta("127.0.0.1", self.porta_aberta, timeout=2)
        self.assertEqual(r.estado, varredura.ABERTA)
        self.assertIsNotNone(r.latencia_ms)

    def test_banner_e_lido(self):
        r = varredura.testar_porta("127.0.0.1", self.porta_aberta, timeout=2, pegar_banner=True)
        self.assertIn("220 teste pronto", r.banner)

    def test_porta_fechada_da_recusa(self):
        r = varredura.testar_porta("127.0.0.1", self.porta_fechada, timeout=2)
        self.assertEqual(r.estado, varredura.FECHADA)

    def test_varredura_concorrente_encontra_a_aberta(self):
        alvo = [self.porta_aberta, self.porta_fechada]
        res = {r.porta: r.estado for r in varredura.varrer("127.0.0.1", alvo, timeout=2)}
        self.assertEqual(res[self.porta_aberta], varredura.ABERTA)
        self.assertEqual(res[self.porta_fechada], varredura.FECHADA)


class TestGuardaDeAutorizacao(unittest.TestCase):
    def test_loopback_e_local(self):
        self.assertTrue(varredura.eh_alvo_local("127.0.0.1"))

    def test_rfc1918_e_local(self):
        self.assertTrue(varredura.eh_alvo_local("192.168.1.1"))
        self.assertTrue(varredura.eh_alvo_local("10.0.0.1"))
        self.assertTrue(varredura.eh_alvo_local("172.16.0.1"))

    def test_ip_publico_nao_e_local(self):
        self.assertFalse(varredura.eh_alvo_local("1.1.1.1"))

    def test_cli_recusa_alvo_publico_sem_flag(self):
        import auditor
        self.assertEqual(auditor.main(["varrer", "8.8.8.8", "-p", "53"]), 2)


class TestInventarioAoVivo(unittest.TestCase):
    """Roda contra o /proc de verdade. Pulado fora do Linux."""

    def setUp(self):
        import os
        if not os.path.exists("/proc/net/tcp"):
            self.skipTest("sem /proc: não é Linux")

    def test_coleta_devolve_sockets(self):
        socks = inventario.coletar()
        self.assertGreater(len(socks), 0, "nenhum socket em escuta? improvável")

    def test_so_devolve_listen_e_unconn(self):
        for s in inventario.coletar():
            self.assertIn(s.estado, ("LISTEN", "UNCONN"))

    def test_encontra_o_socket_que_este_teste_abriu(self):
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        porta = s.getsockname()[1]
        try:
            achados = [x for x in inventario.coletar()
                       if x.porta_local == porta and x.protocolo == "tcp"]
            self.assertEqual(len(achados), 1)
            self.assertEqual(achados[0].estado, "LISTEN")
            self.assertEqual(achados[0].ip_local, "127.0.0.1")
            # O processo dono somos nós — o mapeamento inode→pid tem de acertar.
            import os
            self.assertEqual(achados[0].pid, os.getpid())
        finally:
            s.close()

    def test_faixa_efemera_e_plausivel(self):
        ini, fim = inventario.faixa_efemera()
        self.assertLess(ini, fim)
        self.assertGreaterEqual(ini, 1024)
        self.assertLessEqual(fim, 65535)

    def test_json_e_valido(self):
        import json
        dados = json.loads(relatorio.para_json(inventario.coletar()))
        self.assertIsInstance(dados, list)
        if dados:
            self.assertIn("severidade", dados[0])
            self.assertIn("escopo", dados[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
