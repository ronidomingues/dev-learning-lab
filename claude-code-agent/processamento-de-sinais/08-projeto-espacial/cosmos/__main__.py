"""CLI do `cosmos` — quatro pipelines de sinais do espaço profundo.

    python -m cosmos radiometro --tsys 25 --banda 100e6 --tau 60
    python -m cosmos dispersao  --dm 50 --f-baixa 400 --f-alta 800
    python -m cosmos pulsar     --periodo 0.714 --dm 50 --figuras saida/
    python -m cosmos enlace     --snr -20 --periodos 4 --figuras saida/
"""

from __future__ import annotations

import argparse
import sys

import numpy as np

from . import aquisicao, deteccao, dispersao, doppler, pulsar, ruido
from .constantes import BANDAS_DSN, C_LUZ, K_DISPERSAO


def _cmd_radiometro(args) -> int:
    """Sensibilidade de uma observação: quanto se enxerga e em quanto tempo."""
    t_sys = ruido.temperatura_de_sistema(
        t_receptor_k=args.t_receptor, t_ceu_k=args.t_ceu,
        t_atmosfera_k=args.t_atmosfera, t_solo_k=args.t_solo)

    print("ORÇAMENTO DE RUÍDO")
    print(f"  receptor (LNA) ......... {args.t_receptor:8.2f} K")
    print(f"  céu (fundo + Galáxia) .. {args.t_ceu:8.2f} K")
    print(f"  atmosfera .............. {args.t_atmosfera:8.2f} K")
    print(f"  solo (spillover) ....... {args.t_solo:8.2f} K")
    print(f"  T_sys TOTAL ............ {t_sys:8.2f} K")
    print()
    p = ruido.potencia_de_ruido(t_sys, args.banda)
    print(f"potência de ruído .......... {p:.4e} W   ({10*np.log10(p/1e-3):.1f} dBm)")
    print(f"largura de banda ........... {args.banda/1e6:.1f} MHz")
    print(f"tempo de integração ........ {args.tau:.1f} s")
    print(f"amostras independentes ..... {args.banda*args.tau:.3e}")
    print()
    dt = ruido.radiometro(t_sys, args.banda, args.tau, args.polarizacoes)
    print(f"SENSIBILIDADE (1 sigma) .... {dt*1e3:.4f} mK")
    print(f"  a 5 sigma detecta ........ {5*dt*1e3:.4f} mK")
    print()
    for alvo_mk in (args.alvo*1e3, args.alvo*1e3/10):
        t = ruido.tempo_necessario(t_sys, args.banda, alvo_mk/1e3,
                                   n_sigma=5.0, n_polarizacoes=args.polarizacoes)
        print(f"  tempo p/ detectar {alvo_mk:7.3f} mK a 5 sigma: {t:10.1f} s"
              f"  ({t/3600:.2f} h)")
    print()
    print("  Nota: a sensibilidade melhora com √τ. Dobrar a sensibilidade")
    print("  exige QUADRUPLICAR o tempo — por isso se investe primeiro em")
    print("  baixar T_sys (criogenia) e alargar a banda.")
    return 0


def _cmd_dispersao(args) -> int:
    """Atraso do plasma interestelar e o que ele mede."""
    atraso = dispersao.atraso_dispersao(args.dm, args.f_baixa, args.f_alta)
    print(f"DISPERSÃO INTERESTELAR   (K = {K_DISPERSAO:.3f} MHz² pc⁻¹ cm³ s)")
    print(f"  DM ..................... {args.dm:.3f} pc·cm⁻³")
    print(f"  banda .................. {args.f_baixa:.1f} – {args.f_alta:.1f} MHz")
    print()
    print(f"  atraso entre as pontas . {atraso:.6f} s")
    print(f"  DM recuperado do atraso  "
          f"{dispersao.dm_a_partir_do_atraso(atraso, args.f_baixa, args.f_alta):.6f}"
          f" pc·cm⁻³")
    print()
    print("  atraso absoluto por canal (em relação a frequência infinita):")
    for f in np.linspace(args.f_baixa, args.f_alta, 5):
        print(f"    {f:7.1f} MHz -> {dispersao.atraso_dispersao(args.dm, f):8.4f} s")
    print()
    largura_canal = (args.f_alta - args.f_baixa)/args.canais
    f_centro = (args.f_alta + args.f_baixa)/2
    dm_max = dispersao.dispersao_maxima_tolerada(largura_canal, f_centro,
                                                 args.largura_pulso)
    print(f"  com {args.canais} canais de {largura_canal:.3f} MHz e pulso de "
          f"{args.largura_pulso*1e3:.1f} ms:")
    print(f"    DM máximo sem borrar dentro do canal: {dm_max:.1f} pc·cm⁻³")
    if args.dm > dm_max:
        print("    ⚠️  o DM pedido EXCEDE esse limite: o pulso será borrado")
        print("        dentro de cada canal. Use mais canais ou dedispersão coerente.")
    return 0


def _cmd_pulsar(args) -> int:
    """Pipeline completo: sintetizar, dedispersar, dobrar, decidir."""
    print("SÍNTESE DA OBSERVAÇÃO")
    espectro, freqs = pulsar.sintetizar_observacao(
        periodo_s=args.periodo, dm=args.dm, duracao_s=args.duracao,
        dt_s=args.dt, f_baixa_mhz=args.f_baixa, f_alta_mhz=args.f_alta,
        n_canais=args.canais, amplitude_pulso=args.amplitude,
        semente=args.semente)
    n_giros = args.duracao/args.periodo
    print(f"  {espectro.shape[0]} canais × {espectro.shape[1]} amostras "
          f"({args.duracao:.0f} s a {args.dt*1e3:.2f} ms)")
    print(f"  período {args.periodo:.6f} s -> {n_giros:.1f} giros observados")
    print(f"  amplitude do pulso / sigma do ruído = {args.amplitude:.3f} "
          f"({20*np.log10(args.amplitude):.1f} dB) — invisível a olho nu")
    print()

    print("BUSCA EM DM")
    dms = np.arange(args.dm_min, args.dm_max + args.dm_passo, args.dm_passo)
    snrs = []
    for dm in dms:
        serie = dispersao.dedispersar(espectro, freqs, dm, args.dt)
        snrs.append(pulsar.snr_perfil(pulsar.dobrar(serie, args.periodo,
                                                    args.dt, args.n_fase)))
    snrs = np.array(snrs)
    i = int(np.argmax(snrs))
    print(f"  {len(dms)} valores testados de {dms[0]:.0f} a {dms[-1]:.0f} pc·cm⁻³")
    print(f"  melhor DM .............. {dms[i]:.2f} pc·cm⁻³   (verdadeiro {args.dm:.2f})")
    print(f"  SNR nesse DM ........... {snrs[i]:.2f} sigma")
    print(f"  SNR em DM = 0 .......... {snrs[0]:.2f} sigma"
          f"   <- se este fosse o maior, seria RFI, não astronomia")
    print()

    serie = dispersao.dedispersar(espectro, freqs, dms[i], args.dt)
    perfil = pulsar.dobrar(serie, args.periodo, args.dt, args.n_fase)
    sem_dedisp = pulsar.snr_perfil(pulsar.dobrar(espectro.sum(axis=0),
                                                 args.periodo, args.dt, args.n_fase))
    print("GANHO DE CADA ETAPA")
    print(f"  somando canais SEM dedispersar ... {sem_dedisp:6.2f} sigma")
    print(f"  com dedispersão correta .......... {snrs[i]:6.2f} sigma"
          f"   ({snrs[i]/sem_dedisp:.1f}× melhor)")
    print(f"  √n_canais (limite teórico) ....... {np.sqrt(args.canais):6.2f}×")
    print()

    n_tent = deteccao.tentativas_independentes_busca(len(dms), 1, args.n_fase)
    r = deteccao.resumo_deteccao(snrs[i], n_tent)
    print("VEREDITO ESTATÍSTICO")
    print(f"  tentativas independentes (limite superior) .. {r['tentativas']}")
    print(f"  probabilidade de falso alarme ............... {r['prob_falso_alarme']:.3e}")
    print(f"  limiar p/ 1 % de falso alarme ............... "
          f"{deteccao.limiar_para_falso_alarme(0.01, n_tent):.2f} sigma")
    print(f"  >>> {r['veredito'].upper()}")

    if args.figuras:
        from . import graficos
        graficos.cascata(espectro, freqs, args.dt, f"{args.figuras}/cascata.png",
                         t_max_s=min(5.0, args.duracao))
        graficos.perfil(perfil, f"{args.figuras}/perfil.png",
                        f"Perfil dobrado — DM={dms[i]:.1f}, SNR={snrs[i]:.1f}σ")
        graficos.curva_dm(dms, snrs, args.dm, f"{args.figuras}/curva_dm.png")
        print(f"\n  figuras gravadas em {args.figuras}/")
    return 0


def _cmd_enlace(args) -> int:
    """Enlace de espaço profundo: Doppler + aquisição por código PN."""
    f_tx = BANDAS_DSN[args.banda][0]
    print(f"ENLACE DE ESPAÇO PROFUNDO — banda {args.banda} "
          f"({f_tx/1e9:.2f} GHz)")
    print(f"  {BANDAS_DSN[args.banda][1]}")
    print()
    print("DOPPLER")
    d1 = doppler.desvio_doppler(f_tx, args.velocidade)
    d2 = doppler.doppler_duas_vias(f_tx, args.velocidade)
    print(f"  velocidade radial ...... {args.velocidade/1e3:+.3f} km/s"
          f"  ({'afastando' if args.velocidade > 0 else 'aproximando'})")
    print(f"  desvio de uma via ...... {d1/1e3:+.3f} kHz")
    print(f"  desvio de duas vias .... {d2/1e3:+.3f} kHz")
    print(f"  sensibilidade .......... {abs(doppler.desvio_doppler(f_tx,1.0)):.3f}"
          f" Hz por (m/s)")
    print(f"  velocidade recuperada .. "
          f"{doppler.velocidade_a_partir_do_desvio(f_tx, d1):+.3f} m/s")
    print()

    codigo = aquisicao.codigo_pn(args.grau)
    n = len(codigo)
    fs = args.fs
    print("CÓDIGO PSEUDOALEATÓRIO")
    print(f"  grau do LFSR ........... {args.grau}  ->  N = {n} chips")
    ac = aquisicao.autocorrelacao_circular(codigo)
    print(f"  autocorrelação: pico {ac[0]:.0f}, lateral máx {ac[1:].max():+.3f}"
          f"  <- exatamente −1: propriedade de Golomb")
    print(f"  ganho de processamento . {aquisicao.ganho_de_processamento_db(n):.2f} dB")
    print()

    print(f"AQUISIÇÃO com SNR de entrada = {args.snr:+.1f} dB")
    rng = np.random.default_rng(args.semente)
    amp = 10 ** (args.snr/20)
    atraso_real, fd_real = args.atraso, args.doppler_teste
    n_total = n * args.periodos
    t = np.arange(n_total)/fs
    limpo = np.tile(np.roll(codigo, atraso_real), args.periodos)
    sinal = limpo * np.exp(2j*np.pi*fd_real*t)
    ruido_c = (rng.standard_normal(n_total) + 1j*rng.standard_normal(n_total))/np.sqrt(2)
    rx = amp*sinal + ruido_c

    d, fd, razao, matriz = aquisicao.adquirir_acumulado(
        rx, codigo, fs, args.faixa_doppler, args.passo_doppler, args.periodos)
    acertou = (d == atraso_real) and abs(fd - fd_real) <= args.passo_doppler
    print(f"  períodos acumulados .... {args.periodos}")
    print(f"  atraso estimado ........ {d} chips   (real {atraso_real})")
    print(f"  Doppler estimado ....... {fd:+.1f} Hz   (real {fd_real:+.1f})")
    print(f"  pico / piso ............ {razao:.2f}")
    print(f"  >>> {'AQUISIÇÃO BEM-SUCEDIDA' if acertou else 'FALHOU — aumente --periodos'}")

    if args.figuras:
        from . import graficos
        graficos.plano_aquisicao(matriz, args.faixa_doppler, args.passo_doppler,
                                 f"{args.figuras}/aquisicao.png")
        print(f"\n  figura gravada em {args.figuras}/aquisicao.png")
    return 0 if acertou else 3


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cosmos",
        description="Processamento de sinais para pesquisa cósmica e espacial.")
    sub = p.add_subparsers(dest="comando", required=True)

    r = sub.add_parser("radiometro", help="sensibilidade e orçamento de ruído")
    r.add_argument("--t-receptor", type=float, default=20.0, metavar="K")
    r.add_argument("--t-ceu", type=float, default=3.0, metavar="K")
    r.add_argument("--t-atmosfera", type=float, default=2.0, metavar="K")
    r.add_argument("--t-solo", type=float, default=5.0, metavar="K")
    r.add_argument("--banda", type=float, default=100e6, metavar="HZ")
    r.add_argument("--tau", type=float, default=60.0, metavar="S")
    r.add_argument("--polarizacoes", type=int, default=2, choices=(1, 2))
    r.add_argument("--alvo", type=float, default=0.01, metavar="K")
    r.set_defaults(func=_cmd_radiometro)

    d = sub.add_parser("dispersao", help="atraso do plasma interestelar")
    d.add_argument("--dm", type=float, default=50.0)
    d.add_argument("--f-baixa", type=float, default=400.0, metavar="MHZ")
    d.add_argument("--f-alta", type=float, default=800.0, metavar="MHZ")
    d.add_argument("--canais", type=int, default=64)
    d.add_argument("--largura-pulso", type=float, default=0.02, metavar="S")
    d.set_defaults(func=_cmd_dispersao)

    u = sub.add_parser("pulsar", help="pipeline completo de detecção de pulsar")
    u.add_argument("--periodo", type=float, default=0.714, metavar="S")
    u.add_argument("--dm", type=float, default=50.0)
    u.add_argument("--duracao", type=float, default=60.0, metavar="S")
    u.add_argument("--dt", type=float, default=1e-3, metavar="S")
    u.add_argument("--f-baixa", type=float, default=400.0, metavar="MHZ")
    u.add_argument("--f-alta", type=float, default=800.0, metavar="MHZ")
    u.add_argument("--canais", type=int, default=64)
    u.add_argument("--amplitude", type=float, default=0.05)
    u.add_argument("--n-fase", type=int, default=64)
    u.add_argument("--dm-min", type=float, default=0.0)
    u.add_argument("--dm-max", type=float, default=100.0)
    u.add_argument("--dm-passo", type=float, default=2.0)
    u.add_argument("--semente", type=int, default=42)
    u.add_argument("--figuras", type=str, default=None, metavar="PASTA")
    u.set_defaults(func=_cmd_pulsar)

    e = sub.add_parser("enlace", help="Doppler e aquisição de código PN")
    e.add_argument("--banda", choices=sorted(BANDAS_DSN), default="X")
    e.add_argument("--velocidade", type=float, default=20000.0, metavar="M/S")
    e.add_argument("--grau", type=int, default=10)
    e.add_argument("--fs", type=float, default=1.023e6, metavar="HZ")
    e.add_argument("--snr", type=float, default=-20.0, metavar="DB")
    e.add_argument("--atraso", type=int, default=317, metavar="CHIPS")
    e.add_argument("--doppler-teste", type=float, default=1500.0, metavar="HZ")
    e.add_argument("--faixa-doppler", type=float, default=3000.0, metavar="HZ")
    e.add_argument("--passo-doppler", type=float, default=250.0, metavar="HZ")
    e.add_argument("--periodos", type=int, default=4)
    e.add_argument("--semente", type=int, default=7)
    e.add_argument("--figuras", type=str, default=None, metavar="PASTA")
    e.set_defaults(func=_cmd_enlace)
    return p


def main(argv: list[str] | None = None) -> int:
    args = construir_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, KeyError) as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
