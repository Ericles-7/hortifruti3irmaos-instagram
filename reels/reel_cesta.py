"""Reel "pega a cesta e vem": a mão pega a cestinha na entrada, depois cortes bem rápidos (meia batida)
de bancas cheias vistas de cima, voltando à cesta de vez em quando, e no fim a fachada da loja, que
escurece com o emblema e o @ por cima. Sem texto, só música.

Uso: python3 reels/reel_cesta.py <projeto>
Gera reels/<projeto>.mp4. Cena: ("brutos/x.mp4", início em s, batidas) ou ("fotos/x.jpg", None, batidas).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

import musica
from editar_reel import FPS, INSTAGRAM, PASTA, H, W, X264, cena_foto, colar_centro, ffmpeg, fonte, icone_logo
from reel_semana import CREME, cena_video

BATIDAS_FIM = 6  # fachada escurecendo com o emblema e o @

# Preencher com os vídeos da mãe: a cesta, as bancas (meia batida cada) e a fachada (última cena).
PROJETOS = {
    "cesta-modelo": [
        ("brutos/manga.mp4", 0.0, 2),       # (trocar) mão pegando a cestinha
        ("fotos/manga-colorida.jpg", None, 0.5),
        ("fotos/melancia-3.jpg", None, 0.5),
        ("fotos/manga-coite.jpg", None, 0.5),
        ("fotos/rapadura-gergelim.jpg", None, 0.5),
        ("brutos/manga.mp4", 11.0, 1),     # (trocar) volta à cesta
        ("fotos/melancia-2.jpg", None, 0.5),
        ("fotos/rapadura-pilha.jpg", None, 0.5),
        ("fotos/manga-coite.jpg", None, 0.5),
        ("fotos/manga-colorida.jpg", None, 0.5),
        ("fotos/melancia-1.jpg", None, 2),  # (trocar) fachada da loja
    ],
    # vídeos da mãe de 29/10 (sem a cesta e a fachada ainda): bancas cheias, cortes de 1 batida
    "chegou-29-10": [
        ("brutos/melancia-cortada.mp4", 2.5, 3),
        ("brutos/laranja.mp4", 0.5, 1),
        ("brutos/cebola.mp4", 0.0, 1),
        ("brutos/alho.mp4", 3.0, 1),
        ("brutos/melancia-pilha.mp4", 1.0, 1),
        ("brutos/melancia-cortada.mp4", 7.0, 1),
        ("brutos/laranja.mp4", 3.0, 1),
        ("brutos/cebola.mp4", 6.0, 1),
        ("brutos/alho.mp4", 7.0, 1),
        ("brutos/melancia-pilha.mp4", 12.0, 2),
    ],
}


def camada_fim(alfa):
    img = Image.new("RGBA", (W, H), (0, 0, 0, int(170 * alfa)))
    if alfa > 0.5:
        k = (alfa - 0.5) * 2
        ic = icone_logo(180)
        ic.putalpha(ic.getchannel("A").point(lambda v: int(v * k)))
        colar_centro(img, ic, W / 2, H / 2 - 40)
        d = ImageDraw.Draw(img)
        d.text((W / 2, H / 2 + 100), INSTAGRAM, font=fonte(42, "ExtraBold"), fill=CREME + (int(255 * k),),
               anchor="mm")
    return img


def main(projeto):
    cenas = PROJETOS[projeto]
    tmp = Path(tempfile.mkdtemp())
    partes, quadros_cenas = [], []
    for i, (arquivo, ini, batidas) in enumerate(cenas):
        q = max(1, round(batidas * musica.BATIDA * FPS))
        if i == len(cenas) - 1:
            q += round(BATIDAS_FIM * musica.BATIDA * FPS)  # a fachada continua por baixo do final
        parte = tmp / f"c{i}.mp4"
        if ini is None:
            cena_foto(arquivo, q, i, False, parte)
        else:
            cena_video(arquivo, ini, q, parte)
        partes.append(parte)
        quadros_cenas.append(q)
    lista = tmp / "lista.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in partes))
    corpo = tmp / "corpo.mp4"
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(corpo))

    n = sum(quadros_cenas)
    total = n / FPS
    inicio_fim = n - round(BATIDAS_FIM * musica.BATIDA * FPS)
    wav = tmp / "musica.wav"
    musica.gerar(str(wav), ["C", "G", "Am", "F", "C", "G", "Am", "F", "C"][:max(3, round(total / musica.COMPASSO) + 1)])
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
    vazio = Image.new("RGBA", (W, H), (0, 0, 0, 0)).tobytes()
    for q in range(n):
        if q < inicio_fim:
            proc.stdin.write(vazio)
        else:
            proc.stdin.write(camada_fim(min(1.0, (q - inicio_fim) / (FPS * 0.8))).tobytes())
    proc.stdin.close()
    if proc.wait():
        sys.exit("falha ao compor o vídeo")
    print(f"{saida} ({total:.1f}s)")


if __name__ == "__main__":
    main(sys.argv[1])
