"""Reel "dias da semana": um produto por dia (mão pegando da banca cheia), o nome do dia no centro
em letra serifada creme, cortes de 1 batida e meia, e no fim tela escura com o emblema e o @.

Uso: python3 reels/reel_semana.py <projeto>
Gera reels/<projeto>.mp4. Cada cena é uma foto (zoom lento) ou um trecho de vídeo (arquivo, início).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import musica
from editar_reel import FPS, INSTAGRAM, PASTA, H, W, X264, cena_foto, colar_centro, ffmpeg, fonte, icone_logo

SERIFA = PASTA / "fonts" / "DMSerifDisplay.ttf"
CREME = (255, 241, 196)
DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
BATIDAS_DIA = 2
BATIDAS_FIM = 6

# projeto: 7 cenas, uma por dia. Foto em reels/ ("fotos/x.jpg") ou vídeo ("brutos/x.mp4", início em s).
PROJETOS = {
    # prévia com as fotos aprovadas; trocar pelos vídeos da mão pegando o produto quando chegarem
    "semana-previa": [
        "fotos/manga-colorida.jpg",
        "fotos/melancia-3.jpg",
        "fotos/manga-coite.jpg",
        "fotos/rapadura-gergelim.jpg",
        "fotos/melancia-2.jpg",
        ("brutos/manga.mp4", 17.0),
        "fotos/rapadura-pilha.jpg",
    ],
}


def texto_dia(dia):
    f = ImageFont.truetype(str(SERIFA), 150)
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), dia, font=f)
    img = Image.new("RGBA", (r - l + 80, b - t + 80), (0, 0, 0, 0))
    sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sombra).text((40 - l, 46 - t), dia, font=f, fill=(0, 0, 0, 150))
    img.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(img).text((40 - l, 40 - t), dia, font=f, fill=CREME)
    return img


def tela_final():
    img = Image.new("RGBA", (W, H), (12, 14, 12, 255))
    colar_centro(img, icone_logo(220), W / 2, H / 2 - 80)
    d = ImageDraw.Draw(img)
    f = fonte(44, "ExtraBold")
    d.text((W / 2, H / 2 + 90), INSTAGRAM, font=f, fill=CREME, anchor="mm")
    d.text((W / 2, H / 2 + 160), "Fresquinho todo dia da semana", font=fonte(36, "Bold"), fill=(200, 200, 190),
           anchor="mm")
    return img


def cena_video(arquivo, ini, quadros, saida):
    ffmpeg("-ss", f"{ini:.3f}", "-i", str(PASTA / arquivo), "-an", "-vf",
           f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},"
           "eq=saturation=1.25:contrast=1.07:brightness=0.03,unsharp=5:5:0.6",
           "-frames:v", str(quadros), *X264, "-crf", "15", str(saida))


def main(projeto):
    cenas = PROJETOS[projeto]
    tmp = Path(tempfile.mkdtemp())
    q_dia = round(BATIDAS_DIA * musica.BATIDA * FPS)
    q_fim = round(BATIDAS_FIM * musica.BATIDA * FPS)
    partes = []
    for i, cena in enumerate(cenas):
        parte = tmp / f"dia{i}.mp4"
        if isinstance(cena, tuple):
            cena_video(cena[0], cena[1], q_dia, parte)
        else:
            cena_foto(cena, q_dia, i, False, parte)
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

    wav = tmp / "musica.wav"
    musica.gerar(str(wav), ["C", "G", "Am", "F", "C"])
    n = 7 * q_dia + q_fim
    total = n / FPS
    textos = [texto_dia(d) for d in DIAS]
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
        dia = q // q_dia
        if dia >= 7:
            quadro = vazio
        else:
            dt = (q - dia * q_dia) / FPS
            quadro = vazio.copy()
            alfa = min(1.0, dt / 0.12)  # o nome entra rápido junto com o corte
            txt = textos[dia]
            if alfa < 1:
                txt = txt.copy()
                txt.putalpha(txt.getchannel("A").point(lambda v: int(v * alfa)))
            quadro.alpha_composite(txt, ((W - txt.width) // 2, H // 2 - txt.height // 2))
        proc.stdin.write(quadro.tobytes())
    proc.stdin.close()
    if proc.wait():
        sys.exit("falha ao compor o vídeo")
    print(f"{saida} ({total:.1f}s)")


if __name__ == "__main__":
    main(sys.argv[1])
