"""Interface de linha de comando do `sinal`.

    python -m sinal gerar    saida.wav --f0 440 --dur 2
    python -m sinal analisar saida.wav
    python -m sinal filtrar  saida.wav limpo.wav --passa-alta 80
    python -m sinal figura   saida.wav painel.png
"""

from __future__ import annotations

import argparse
import sys

import numpy as np

from . import __version__, filtros, frequencia, geracao, io_wav, medidas
from .config import Config, ConfiguracaoInvalida


def _cmd_gerar(args, cfg: Config) -> int:
    x = geracao.sinal_de_teste(
        f0=args.f0, duracao=args.dur, taxa=args.taxa,
        harmonicos=args.harmonicos, rms_ruido=args.ruido,
        freq_rede=cfg.frequencia_rede, amp_rede=args.zumbido,
    )
    io_wav.escrever_wav(args.saida, x, args.taxa)
    print(f"gravado: {args.saida}")
    print(f"  f0 verdadeira ...... {args.f0:.3f} Hz")
    print(f"  taxa ............... {args.taxa} Hz")
    print(f"  duração ............ {args.dur:.2f} s ({len(x)} amostras)")
    print(f"  harmônicos ......... {args.harmonicos}")
    print(f"  ruído (RMS) ........ {args.ruido:.4f}")
    print(f"  zumbido de rede .... {args.zumbido:.4f} @ {cfg.frequencia_rede:.0f} Hz")
    return 0


def _cmd_analisar(args, cfg: Config) -> int:
    x, taxa = io_wav.ler_wav(args.entrada)
    n = len(x)
    niveis = medidas.medir_niveis(x, cfg.limiar_clip)

    print(f"arquivo ................ {args.entrada}")
    print(f"taxa de amostragem ..... {taxa} Hz  (Nyquist = {taxa / 2:.0f} Hz)")
    print(f"duração ................ {n / taxa:.3f} s  ({n} amostras)")
    n_analise = min(n, taxa)  # o estimador usa 1 s central
    print(f"resolução espectral .... {taxa / n_analise:.2f} Hz/bin"
          f"  (janela de análise = {n_analise} amostras)")
    print()
    print(f"pico ................... {niveis.pico:.4f}  ({niveis.pico_dbfs:+.2f} dBFS)")
    print(f"RMS .................... {niveis.rms:.4f}  ({niveis.rms_dbfs:+.2f} dBFS)")
    print(f"fator de crista ........ {niveis.fator_de_crista_db:.2f} dB"
          f"   (senoide pura = 3,01 dB)")
    print(f"componente DC .......... {niveis.dc:+.6f}")
    print(f"amostras ceifadas ...... {niveis.amostras_ceifadas}"
          f"  ({100 * niveis.amostras_ceifadas / n:.3f} %)")

    frac_rede = medidas.energia_em_faixa(
        x, taxa, cfg.frequencia_rede - 5, cfg.frequencia_rede + 5)
    print(f"energia em {cfg.frequencia_rede:.0f}±5 Hz .... {100 * frac_rede:.2f} %"
          + ("   ← zumbido de rede provável" if frac_rede > 0.01 else ""))
    print()

    try:
        est = frequencia.estimar_f0(x, taxa, cfg.f0_min, cfg.f0_max, cfg.n_fft)
    except ValueError as e:
        print(f"não foi possível estimar f0: {e}", file=sys.stderr)
        return 2

    print("estimativa de f0")
    print(f"  FFT + parábola ....... {est.fft:9.3f} Hz")
    print(f"  HPS .................. {est.hps:9.3f} Hz")
    print(f"  autocorrelação ....... {est.autocorrelacao:9.3f} Hz")
    print(f"  consenso (mediana) ... {est.consenso:9.3f} Hz"
          + ("" if est.concordam else "   ← métodos DIVERGEM, desconfie"))

    nota = frequencia.nota_mais_proxima(est.consenso, args.a4)
    seta = "sustenido ↑" if nota.desvio_cents > 0 else "bemol ↓"
    print()
    print(f"nota ................... {nota.nome}"
          f"  (ideal {nota.freq_ideal:.3f} Hz com A4={args.a4:.1f})")
    print(f"desvio ................. {nota.desvio_cents:+.1f} cents  {seta}")
    veredito = ("afinado" if abs(nota.desvio_cents) < 5 else
                "aceitável" if abs(nota.desvio_cents) < 15 else "DESAFINADO")
    print(f"veredito ............... {veredito}")

    thd = medidas.thd_db(x, taxa, est.consenso)
    print(f"THD (5 harmônicos) ..... {thd:.2f} dB  ({100 * 10 ** (thd / 20):.2f} %)")
    return 0


def _cmd_filtrar(args, cfg: Config) -> int:
    x, taxa = io_wav.ler_wav(args.entrada)
    y = x
    aplicados = []

    if args.remover_zumbido:
        y = filtros.remover_zumbido(y, taxa, cfg.frequencia_rede,
                                    n_harmonicos=args.harmonicos_rede)
        aplicados.append(f"notch {cfg.frequencia_rede:.0f} Hz "
                         f"× {args.harmonicos_rede} harmônicos")
    if args.passa_alta:
        sos = filtros.sos_passa_alta(args.passa_alta, taxa, ordem=args.ordem)
        y = filtros.aplicar_sos(sos=sos, x=y, fase_zero=not args.causal)
        aplicados.append(f"passa-alta Butterworth {args.passa_alta} Hz "
                         f"ordem {args.ordem}")
    if args.passa_baixa:
        sos = filtros.sos_passa_baixa(args.passa_baixa, taxa, ordem=args.ordem)
        y = filtros.aplicar_sos(sos=sos, x=y, fase_zero=not args.causal)
        aplicados.append(f"passa-baixa Butterworth {args.passa_baixa} Hz "
                         f"ordem {args.ordem}")

    if not aplicados:
        print("nenhum filtro pedido; use --remover-zumbido, --passa-alta ou "
              "--passa-baixa", file=sys.stderr)
        return 2

    io_wav.escrever_wav(args.saida, y, taxa)
    antes = medidas.medir_niveis(x)
    depois = medidas.medir_niveis(y)
    print(f"gravado: {args.saida}")
    for a in aplicados:
        print(f"  · {a}")
    print(f"  fase ............... {'causal' if args.causal else 'zero (filtfilt)'}")
    print(f"  RMS antes .......... {antes.rms_dbfs:+.2f} dBFS")
    print(f"  RMS depois ......... {depois.rms_dbfs:+.2f} dBFS")
    print(f"  energia removida ... {100 * (1 - depois.rms ** 2 / max(antes.rms ** 2, 1e-20)):.2f} %")
    return 0


def _cmd_figura(args, cfg: Config) -> int:
    x, taxa = io_wav.ler_wav(args.entrada)
    from . import graficos
    caminho = graficos.painel(x, taxa, args.saida, titulo=str(args.entrada),
                              f_max_plot=args.f_max)
    print(f"figura gravada: {caminho}")
    return 0


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sinal",
        description="Analisador, afinador e filtrador de áudio (projeto-modelo "
                    "do curso de Processamento de Sinais).")
    p.add_argument("--version", action="version", version=f"sinal {__version__}")
    sub = p.add_subparsers(dest="comando", required=True)

    g = sub.add_parser("gerar", help="sintetiza um WAV de teste com f0 conhecida")
    g.add_argument("saida")
    g.add_argument("--f0", type=float, default=440.0)
    g.add_argument("--dur", type=float, default=2.0)
    g.add_argument("--taxa", type=int, default=44100)
    g.add_argument("--harmonicos", type=int, default=5)
    g.add_argument("--ruido", type=float, default=0.02, help="RMS do ruído branco")
    g.add_argument("--zumbido", type=float, default=0.05, help="amplitude da rede")
    g.set_defaults(func=_cmd_gerar)

    a = sub.add_parser("analisar", help="mede níveis, estima f0 e nota musical")
    a.add_argument("entrada")
    a.add_argument("--a4", type=float, default=440.0,
                   help="referência de afinação (440 padrão, 415 barroco)")
    a.set_defaults(func=_cmd_analisar)

    f = sub.add_parser("filtrar", help="aplica filtros e grava novo WAV")
    f.add_argument("entrada")
    f.add_argument("saida")
    f.add_argument("--remover-zumbido", action="store_true")
    f.add_argument("--harmonicos-rede", type=int, default=3)
    f.add_argument("--passa-alta", type=float, default=None, metavar="HZ")
    f.add_argument("--passa-baixa", type=float, default=None, metavar="HZ")
    f.add_argument("--ordem", type=int, default=4)
    f.add_argument("--causal", action="store_true",
                   help="usa sosfilt (tempo real) em vez de filtfilt (fase zero)")
    f.set_defaults(func=_cmd_filtrar)

    v = sub.add_parser("figura", help="gera PNG com onda, espectro e espectrograma")
    v.add_argument("entrada")
    v.add_argument("saida")
    v.add_argument("--f-max", type=float, default=5000.0)
    v.set_defaults(func=_cmd_figura)
    return p


def main(argv: list[str] | None = None) -> int:
    args = construir_parser().parse_args(argv)
    try:
        cfg = Config.do_ambiente()
        return args.func(args, cfg)
    except (io_wav.ErroDeAudio, filtros.ErroDeFiltro, ConfiguracaoInvalida) as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
