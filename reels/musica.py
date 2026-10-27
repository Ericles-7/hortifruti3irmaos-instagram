"""Trilha de fundo própria (sem direitos autorais): ukulele, baixo, marimba e percussão leve.

112 BPM, em Dó maior. A progressão C-G-Am-F termina em G-C no cartão final.
Uso: python3 reels/musica.py saida.wav  (ou importar gerar())
"""
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

SR = 44100
BPM = 112
BATIDA = 60 / BPM
COMPASSO = 4 * BATIDA

# Acordes (voicing do ukulele) e baixo, em Hz
NOTA = {n: 440 * 2 ** ((i - 9) / 12) for i, n in enumerate(
    ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4"])}
NOTA.update({n[:-1] + "5": f * 2 for n, f in list(NOTA.items())})
NOTA.update({n[:-1] + "3": f / 2 for n, f in list(NOTA.items()) if n.endswith("4")})
NOTA.update({n[:-1] + "2": f / 4 for n, f in list(NOTA.items()) if n.endswith("4")})
ACORDES = {
    "C": (["C4", "E4", "G4", "C5"], "C3"),
    "G": (["G3", "B3", "D4", "G4"], "G2"),
    "Am": (["A3", "C4", "E4", "A4"], "A2"),
    "F": (["F3", "A3", "C4", "F4"], "F2"),
}
# Melodia da marimba: (batida no compasso, nota) para cada acorde
MELODIA = {
    "C": [(0, "E5"), (1, "G5"), (2, "A5"), (3, "G5")],
    "G": [(0, "D5"), (2, "B4"), (3, "D5")],
    "Am": [(0, "C5"), (1, "E5"), (2, "A5"), (3, "G5")],
    "F": [(0, "F5"), (1, "E5"), (2, "C5")],
}
# Ritmo do strum: (batida, direção, força)
STRUM = [(0, 1, 1.0), (1, 1, 0.7), (1.5, -1, 0.5), (2.5, -1, 0.5), (3, 1, 0.75), (3.5, -1, 0.5)]

rng = np.random.default_rng(3)


def tom_pluck(f, dur=1.6):
    t = np.arange(int(dur * SR)) / SR
    s = sum((1 / k ** 1.3) * np.sin(2 * np.pi * k * f * t) * np.exp(-t * (2.5 + 1.8 * k)) for k in range(1, 9))
    return s * np.minimum(1, t / 0.003)


def tom_marimba(f, dur=0.9):
    t = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 5) + 0.25 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 22)
    return s * np.minimum(1, t / 0.002)


def tom_baixo(f, dur):
    t = np.arange(int(dur * SR)) / SR
    s = np.tanh(1.5 * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)))
    return s * np.exp(-t * 2.2) * np.minimum(1, t / 0.005)


def bumbo():
    t = np.arange(int(0.3 * SR)) / SR
    fase = 2 * np.pi * np.cumsum(50 + 90 * np.exp(-t * 30)) / SR
    return np.sin(fase) * np.exp(-t * 12)


def ruido(dur, faixa, decai):
    t = np.arange(int(dur * SR)) / SR
    sos = butter(4, faixa, btype="bandpass" if isinstance(faixa, list) else "highpass", fs=SR, output="sos")
    return sosfilt(sos, rng.standard_normal(len(t))) * np.exp(-t * decai)


def soma(trilha, som, t, ganho=1.0):
    i = int(t * SR)
    if i >= len(trilha):
        return
    n = min(len(som), len(trilha) - i)
    trilha[i:i + n] += ganho * som[:n]


def gerar(caminho, compassos=None):
    if compassos is None:
        compassos = ["C", "G", "Am", "F"] * 2 + ["C", "G", "C"]
    dur = len(compassos) * COMPASSO + 2.0
    uke, baixo, mar, perc = (np.zeros(int(dur * SR)) for _ in range(4))
    final = len(compassos) - 1
    for c, nome in enumerate(compassos):
        t0 = c * COMPASSO
        notas, raiz = ACORDES[nome]
        if c == final:  # acorde final: um strum só, deixando soar
            for j, n in enumerate(notas):
                soma(uke, tom_pluck(NOTA[n], 2.0), t0 + j * 0.018, 0.9)
            soma(baixo, tom_baixo(NOTA[raiz], 2.0), t0)
            soma(mar, tom_marimba(NOTA["C5"], 1.6), t0, 0.9)
            soma(mar, tom_marimba(NOTA["G5"], 1.6), t0 + 0.02, 0.5)
            soma(perc, bumbo(), t0, 0.8)
            continue
        for b, direcao, forca in STRUM:
            ordem = notas if direcao > 0 else notas[::-1]
            for j, n in enumerate(ordem):
                soma(uke, tom_pluck(NOTA[n]), t0 + b * BATIDA + j * 0.012, forca * (1 - 0.08 * j))
        soma(baixo, tom_baixo(NOTA[raiz], 2 * BATIDA), t0)
        soma(baixo, tom_baixo(NOTA[raiz] * (1.5 if nome != "F" else 1), 2 * BATIDA), t0 + 2 * BATIDA, 0.8)
        if c >= 2:  # marimba entra no 3º compasso
            for b, n in MELODIA[nome]:
                soma(mar, tom_marimba(NOTA[n]), t0 + b * BATIDA)
        if c >= 1:  # percussão entra no 2º compasso
            for b in (0, 2):
                soma(perc, bumbo(), t0 + b * BATIDA, 0.9)
            for b in (1, 3):
                soma(perc, ruido(0.15, [900, 4000], 28), t0 + b * BATIDA, 0.35)
        for k in range(8):
            soma(perc, ruido(0.06, 6000, 70), t0 + k * BATIDA / 2, 0.05 if k % 2 == 0 else 0.08)

    # mixagem em estéreo (ukulele à esquerda, marimba à direita) + um pouco de reverb
    esq = 0.55 * uke + 0.55 * baixo + 0.25 * mar + perc
    dir_ = 0.40 * uke + 0.55 * baixo + 0.40 * mar + perc
    ir_t = np.arange(int(1.1 * SR)) / SR
    ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 5)
    ir /= np.abs(ir).sum() / 8
    est = []
    for canal in (esq, dir_):
        molhado = fftconvolve(canal, ir)[:len(canal)]
        est.append(canal + 0.12 * molhado)
    est = np.stack(est, axis=1)
    est /= np.abs(est).max() / 0.89
    wavfile.write(caminho, SR, (est * 32767).astype(np.int16))
    return len(compassos) * COMPASSO


if __name__ == "__main__":
    print(f"{gerar(sys.argv[1]):.2f}s de música")
