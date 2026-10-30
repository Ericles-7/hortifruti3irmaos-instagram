"""Reel "nossas frutas": uma fruta por corte (2 batidas), o nome no centro em letra serifada creme,
forró de fundo, e no fim tela escura com o emblema, o @ e o Zap.

Uso: python3 reels/reel_frutas.py <projeto>
Gera reels/<projeto>.mp4. Cena: (nome, "brutos/x.mp4", início em s) ou (nome, "fotos/x.jpg", None).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

import musica
import musica_forro
from editar_reel import FPS, INSTAGRAM, PASTA, H, W, X264, cena_foto, colar_centro, ffmpeg, fonte, icone_logo
from reel_semana import CREME, cena_video, texto_dia

BATIDAS_CENA = 2
BATIDAS_FIM = 6
ZAP = "(83) 99937-8165"

PROJETOS = {
    "frutas-teste": [
        ("Melancia", "arquivo/2026-10/brutos/melancia-cortada.mp4", 2.5),
        ("Mamão", "arquivo/2026-10/brutos/mamao-1.mp4", 1.0),
        ("Tangerina", "arquivo/2026-10/brutos/laranja.mp4", 0.5),
        ("Uva", "arquivo/2026-10/brutos/uva-ameixa.mp4", 1.0),
        ("Ameixa", "arquivo/2026-10/brutos/uva-ameixa.mp4", 12.0),
        ("Kiwi", "arquivo/2026-10/brutos/kiwi.mp4", 1.0),
        ("Manga", "arquivo/2026-10/brutos/manga.mp4", 17.0),
    ],
}


def tela_final():
    img = Image.new("RGBA", (W, H), (12, 14, 12, 255))
    colar_centro(img, icone_logo(220), W / 2, H / 2 - 120)
    d = ImageDraw.Draw(img)
    d.text((W / 2, H / 2 + 50), "Hortifruti 3 Irmãos", font=fonte(56, "ExtraBold"), fill=CREME, anchor="mm")
    d.text((W / 2, H / 2 + 125), INSTAGRAM, font=fonte(38, "Bold"), fill=(200, 200, 190), anchor="mm")
    d.text((W / 2, H / 2 + 200), f"Peça pelo Zap {ZAP}", font=fonte(38, "Bold"), fill=(200, 200, 190),
           anchor="mm")
    return img


def main(projeto):
    cenas = PROJETOS[projeto]
    tmp = Path(tempfile.mkdtemp())
    q_cena = round(BATIDAS_CENA * musica.BATIDA * FPS)
    q_fim = round(BATIDAS_FIM * musica.BATIDA * FPS)
    partes = []
    for i, (_, arquivo, ini) in enumerate(cenas):
        parte = tmp / f"c{i}.mp4"
        if ini is None:
            cena_foto(arquivo, q_cena, i, False, parte)
        else:
            cena_video(arquivo, ini, q_cena, parte)
        partes.append(parte)
    final = tmp / "final.png"
    tela_final().convert("RGB").save(final)
    parte = tmp / "fim.mp4"
    ffmpeg("-loop", "1", "-i", str(final), "-vf", f"fps={FPS},fade=t=in:st=0:d=0.3",
           "-frames:v", str(q_fim), *X264, "-crf", "15", str(parte))
    partes.append(parte)
    lista = tmp / "lista.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in partes))
    corpo = tmp / "corpo.mp4"
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(corpo))

    n = len(cenas) * q_cena + q_fim
    total = n / FPS
    wav = tmp / "musica.wav"
    musica_forro.gerar(str(wav), [None] * (round(total / musica.COMPASSO) + 1))
    textos = [texto_dia(nome) for nome, _, _ in cenas]
    saida = PASTA / f"{projeto}.mp4"
    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-i", str(corpo),
         "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav),
         "-filter_complex",
         f"[0:v][1:v]overlay=0:0[v];[2:a]atrim=0:{total:.3f},afade=t=out:st={total - 1:.3f}:d=1,"
         "loudnorm=I=-14:TP=-1.5[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", *X264, "-crf", "20", "-profile:v", "high",
         "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", str(saida)],
        stdin=subprocess.PIPE)
    vazio = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for q in range(n):
        c = q // q_cena
        if c >= len(cenas):
            quadro = vazio
        else:
            alfa = min(1.0, (q - c * q_cena) / FPS / 0.12)  # o nome entra rápido junto com o corte
            txt = textos[c]
            if alfa < 1:
                txt = txt.copy()
                txt.putalpha(txt.getchannel("A").point(lambda v: int(v * alfa)))
            quadro = vazio.copy()
            quadro.alpha_composite(txt, ((W - txt.width) // 2, H // 2 - txt.height // 2))
        proc.stdin.write(quadro.tobytes())
    proc.stdin.close()
    if proc.wait():
        sys.exit("falha ao compor o vídeo")
    print(f"{saida} ({total:.1f}s)")


if __name__ == "__main__":
    main(sys.argv[1])
