"""Trilha de piseiro própria (sem direitos autorais): tecladinho, baixo, bumbo de paredão, palma e chimbal.

140 BPM, em Lá menor (Am-F-C-G), com o riff do teclado repetindo a cada compasso.
Uso: python3 reels/musica_piseiro.py saida.wav  (ou importar gerar())
"""
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

from musica import NOTA, SR, rng, ruido, soma

BPM = 140
BATIDA = 60 / BPM
COMPASSO = 4 * BATIDA

PROGRESSAO = ["Am", "F", "C", "G"]
RAIZ = {"Am": "A2", "F": "F2", "C": "C3", "G": "G2"}
# Riff do tecladinho: (posição em batidas, nota, duração em batidas) — muda a última nota com o acorde
RIFF = [(0, "E5", 0.5), (0.5, "E5", 0.25), (0.75, "D5", 0.5), (1.25, "C5", 0.5), (1.75, "D5", 0.25),
        (2, "E5", 0.5), (2.5, "G5", 0.5), (3, "A5", 0.5)]
FIM_RIFF = {"Am": "A5", "F": "A5", "C": "G5", "G": "B4"}


def tom_teclado(f, dur):
    """Teclado de piseiro: serra brilhante + quadrada, com vibrato rápido e ataque seco."""
    t = np.arange(int(dur * SR)) / SR
    vib = 1 + 0.006 * np.sin(2 * np.pi * 6.5 * t) * np.minimum(1, t / 0.08)
    fase = 2 * np.pi * f * np.cumsum(vib) / SR
    serra = sum(((-1) ** (k + 1)) * np.sin(k * fase) / k for k in range(1, 12))
    quadrada = sum(np.sin(k * fase * 1.003) / k for k in range(1, 12, 2))
    env = np.minimum(1, t / 0.004) * np.exp(-t * 2.2) * np.minimum(1, (dur - t) / 0.02)
    return 0.35 * (serra + 0.7 * quadrada) * env


def tom_baixo(f, dur):
    t = np.arange(int(dur * SR)) / SR
    s = np.tanh(2.2 * np.sin(2 * np.pi * f * t))
    return s * np.minimum(1, t / 0.003) * np.exp(-t * 4) * np.minimum(1, (dur - t) / 0.01)


def bumbo_paredao():
    t = np.arange(int(0.35 * SR)) / SR
    fase = 2 * np.pi * np.cumsum(45 + 140 * np.exp(-t * 38)) / SR
    return np.tanh(2.5 * np.sin(fase) * np.exp(-t * 9))


def palma():
    s = ruido(0.18, [900, 3500], 22)
    for atraso in (0.008, 0.017):  # várias mãos batendo quase juntas
        i = int(atraso * SR)
        s[i:] += 0.7 * ruido(0.18, [900, 3500], 22)[:len(s) - i]
    return s


def gerar(caminho, compassos=None):
    n = len(compassos) if compassos else 8
    dur = n * COMPASSO + 2.0
    tec, baixo, perc = (np.zeros(int(dur * SR)) for _ in range(3))
    final = n - 1
    for c in range(n):
        t0 = c * COMPASSO
        acorde = PROGRESSAO[c % 4] if c < final else "Am"
        raiz = NOTA[RAIZ[acorde]]
        if c == final:  # acorde final com bumbo forte, deixando soar
            for nota in ("A4", "C5", "E5"):
                soma(tec, tom_teclado(NOTA[nota], 1.6), t0, 0.5)
            soma(baixo, tom_baixo(raiz, 1.4), t0)
            soma(perc, bumbo_paredao(), t0, 1.0)
            continue
        for b, nota, d in RIFF:
            if b == 3:
                nota = FIM_RIFF[acorde]
            soma(tec, tom_teclado(NOTA[nota], d * BATIDA), t0 + b * BATIDA, 0.9 if c >= 1 else 0.6)
        for b in (0, 0.75, 1.5, 2, 2.75, 3.5):  # baixo sincopado do piseiro
            soma(baixo, tom_baixo(raiz * (2 if b in (0.75, 2.75) else 1), 0.45 * BATIDA), t0 + b * BATIDA)
        for b in range(4):
            soma(perc, bumbo_paredao(), t0 + b * BATIDA, 1.0)
        if c >= 1:
            for b in (1, 3):
                soma(perc, palma(), t0 + b * BATIDA, 0.55)
        for k in range(8):
            soma(perc, ruido(0.05, 7000, 80), t0 + k * BATIDA / 2, 0.06 if k % 2 == 0 else 0.12)

    # o bumbo "abaixa" o teclado e o baixo um pouquinho (efeito de paredão)
    bomba = np.ones(len(perc))
    for c in range(n):
        for b in range(4):
            i = int((c * COMPASSO + b * BATIDA) * SR)
            j = min(len(bomba), i + int(0.18 * SR))
            bomba[i:j] = np.minimum(bomba[i:j], 0.55 + 0.45 * np.linspace(0, 1, j - i))
    sos = butter(2, 9000, btype="lowpass", fs=SR, output="sos")
    tec = sosfilt(sos, tec)
    esq = 0.55 * tec * bomba + 0.7 * baixo * bomba + perc
    dir_ = 0.45 * tec * bomba + 0.7 * baixo * bomba + perc
    ir_t = np.arange(int(0.6 * SR)) / SR
    ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 8)
    ir /= np.abs(ir).sum() / 8
    est = np.stack([ch + 0.08 * fftconvolve(ch, ir)[:len(ch)] for ch in (esq, dir_)], axis=1)
    est /= np.abs(est).max() / 0.89
    wavfile.write(caminho, SR, (est * 32767).astype(np.int16))
    return n * COMPASSO


if __name__ == "__main__":
    print(f"{gerar(sys.argv[1]):.2f}s de música")
