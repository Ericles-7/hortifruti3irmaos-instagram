"""Trilha de forró pé-de-serra própria (sem direitos autorais): sanfona, zabumba, triângulo e baixo.

Mesmo andamento da musica.py (112 BPM), para os cortes dos reels caírem na batida.
Progressão C-F-G7-C com a sétima menor (Sib) da sanfona, bem nordestina.
Uso: python3 reels/musica_forro.py saida.wav  (ou importar gerar())
"""
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve

from musica import BATIDA, COMPASSO, NOTA, SR, bumbo, ruido, rng, soma, tom_baixo

PROGRESSAO = ["C", "F", "G7", "C2"]
ACORDES = {
    "C": (["C4", "E4", "G4"], "C3"),
    "F": (["C4", "F4", "A4"], "F2"),
    "G7": (["B3", "D4", "F4"], "G2"),
    "C2": (["C4", "E4", "A#4"], "C3"),
}
# Frase da sanfona: (batida no compasso, nota, duração em batidas)
MELODIA = {
    "C": [(0, "G4", 0.5), (0.5, "C5", 0.25), (0.75, "E5", 0.75), (1.5, "G5", 0.5), (2, "E5", 0.5),
          (2.5, "D5", 0.5), (3, "C5", 1)],
    "F": [(0, "A4", 0.5), (0.5, "C5", 0.25), (0.75, "F5", 0.75), (1.5, "A5", 0.5), (2, "G5", 0.5),
          (2.5, "F5", 0.5), (3, "E5", 1)],
    "G7": [(0, "B4", 0.5), (0.5, "D5", 0.25), (0.75, "F5", 0.75), (1.5, "G5", 0.5), (2, "F5", 0.5),
           (2.5, "D5", 0.5), (3, "B4", 1)],
    "C2": [(0, "C5", 0.5), (0.5, "E5", 0.25), (0.75, "G5", 0.75), (1.5, "A#5", 0.5), (2, "A5", 0.5),
           (2.5, "G5", 0.5), (3, "E5", 1)],
}
# Baião: zabumba grave no 1 e no "a" do 1; bacalhau (aro) nos contratempos
ZABUMBA = [0, 0.75, 2, 2.75]
BACALHAU = [1, 1.5, 3, 3.5]


def tom_sanfona(f, dur):
    """Duas palhetas levemente desafinadas (o 'musette') com fole: ataque macio e vibrato lento."""
    t = np.arange(int(dur * SR)) / SR
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t)
    s = 0
    for desvio in (1.0, 1.0035):
        fase = 2 * np.pi * f * desvio * np.cumsum(vib) / SR
        s = s + sum((0.7 ** k) * np.sin(k * fase) for k in range(1, 7))
    env = np.minimum(1, t / 0.025) * np.minimum(1, (dur - t) / 0.04)
    return 0.5 * s * env


def triangulo(aberto):
    t = np.arange(int((0.35 if aberto else 0.06) * SR)) / SR
    s = sum(np.sin(2 * np.pi * f * t) for f in (4200, 6100, 8300))
    return s * np.exp(-t * (9 if aberto else 60))


def gerar(caminho, compassos=None):
    n = len(compassos) if compassos else 9
    barras = [PROGRESSAO[i % 4] for i in range(n - 1)] + ["C"]
    dur = n * COMPASSO + 2.0
    sanf, baixo, perc = (np.zeros(int(dur * SR)) for _ in range(3))
    final = n - 1
    for c, nome in enumerate(barras):
        t0 = c * COMPASSO
        notas, raiz = ACORDES[nome]
        if c == final:  # acorde final da sanfona com zabumba, deixando soar
            for nota in notas + ["C5"]:
                soma(sanf, tom_sanfona(NOTA[nota], 1.8), t0, 0.45)
            soma(baixo, tom_baixo(NOTA[raiz], 2.0), t0)
            soma(perc, bumbo(), t0, 1.0)
            soma(perc, triangulo(True), t0, 0.25)
            continue
        for b, nota, d in MELODIA[nome]:
            soma(sanf, tom_sanfona(NOTA[nota], d * BATIDA * 0.95), t0 + b * BATIDA)
        for b in (0.5, 1.5, 2.5, 3.5):  # mão esquerda da sanfona no contratempo
            for nota in notas:
                soma(sanf, tom_sanfona(NOTA[nota] / 2, 0.22 * BATIDA), t0 + b * BATIDA, 0.18)
        soma(baixo, tom_baixo(NOTA[raiz], 0.75 * BATIDA), t0)
        soma(baixo, tom_baixo(NOTA[raiz] * 1.5, 1.25 * BATIDA), t0 + 0.75 * BATIDA, 0.7)
        soma(baixo, tom_baixo(NOTA[raiz], 2 * BATIDA), t0 + 2 * BATIDA, 0.85)
        for b in ZABUMBA:
            soma(perc, bumbo(), t0 + b * BATIDA, 1.0 if b in (0, 2) else 0.7)
        for b in BACALHAU:
            soma(perc, ruido(0.05, [1800, 5000], 60), t0 + b * BATIDA, 0.3)
        for k in range(16):  # triângulo: aberto no contratempo, abafado no resto
            soma(perc, triangulo(k % 4 == 2), t0 + k * BATIDA / 4, 0.12 if k % 4 == 2 else 0.06)

    esq = 0.55 * sanf + 0.6 * baixo + perc
    dir_ = 0.45 * sanf + 0.6 * baixo + perc
    ir_t = np.arange(int(0.9 * SR)) / SR
    ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 6)
    ir /= np.abs(ir).sum() / 8
    est = np.stack([c + 0.1 * fftconvolve(c, ir)[:len(c)] for c in (esq, dir_)], axis=1)
    est /= np.abs(est).max() / 0.89
    wavfile.write(caminho, SR, (est * 32767).astype(np.int16))
    return n * COMPASSO


if __name__ == "__main__":
    print(f"{gerar(sys.argv[1]):.2f}s de música")
