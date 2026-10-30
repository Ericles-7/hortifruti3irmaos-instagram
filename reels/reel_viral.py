"""Reel em formato viral de lista ("7 frutas que chegaram..."), com vários vídeos da banca.

Gancho em texto grande no 1º segundo; depois um produto por corte, cada um entrando com zoom
"soco" e um flash branco, contador "1/7" no canto, o nome do produto pulando em laranja com
contorno branco e uma etiqueta amarela com o motivo para comprar. No fim, a assinatura animada
(logo, @ e Zap) do editar_reel.

Uso: python3 reels/reel_viral.py <projeto>
Gera reels/<projeto>.mp4 e reels/<projeto>-capa.jpg.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

import musica
from editar_reel import (AMARELO, BATIDA, BATIDAS_FIM, COR, FPS, PASTA, VERDE, VERDE_ESCURO, H, W, X264, Camadas,
                         cena_foto, colar_centro, duracao, ffmpeg, fonte, pulo, texto_destaque)

# projeto: gancho (vídeo, início, batidas, texto) e produtos (vídeo ou foto, início, nome, etiqueta).
# Gancho + produtos somam compassos inteiros (4 batidas), para a música fechar certinho.
BATIDAS_PRODUTO = 3
PROJETOS = {
    "frutas-viral": dict(
        gancho=("arquivo/2026-10/brutos/melancia-cortada.mp4", 0.0, 3, "7 frutas fresquinhas\nque chegaram no\nHortifruti 3 Irmãos!"),
        produtos=[
            ("arquivo/2026-10/brutos/melancia-cortada.mp4", 1.6, "Melancia", "vermelhinha e docinha"),
            ("arquivo/2026-10/brutos/mamao-1.mp4", 1.0, "Mamão", "maduro e de vez"),
            ("arquivo/2026-10/brutos/laranja.mp4", 0.5, "Tangerina", "pro suco e pro lanche"),
            ("arquivo/2026-10/brutos/uva-ameixa.mp4", 1.0, "Uva", "sem semente"),
            ("arquivo/2026-10/brutos/uva-ameixa.mp4", 12.0, "Ameixa", "suculenta"),
            ("arquivo/2026-10/brutos/kiwi.mp4", 1.0, "Kiwi", "cheio de vitamina C"),
            ("arquivo/2026-10/brutos/manga.mp4", 0.0, "Manga coité", "verdinha e firme"),
        ],
        compassos=["C", "G", "Am", "F", "C", "G", "Am", "F", "C"],
    ),
}


def cena_video(arquivo, ini, quadros, saida):
    """Trecho do vídeo enchendo a tela, com zoom "soco" na entrada e a cor da banca realçada."""
    z = "1.08*(1+0.16*max(0,1-on/6))"
    ffmpeg("-ss", f"{ini:.3f}", "-i", str(PASTA / arquivo), "-an", "-vf",
           f"scale={2 * W}:{2 * H}:force_original_aspect_ratio=increase:flags=lanczos,crop={2 * W}:{2 * H},"
           f"zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps={FPS},{COR}",
           "-frames:v", str(quadros), *X264, "-crf", "15", str(saida))


def etiqueta(txt):
    f = fonte(52, "ExtraBold")
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), txt, font=f)
    w, h = r - l + 80, b - t + 44
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=AMARELO + (255,))
    d.text((40 - l, 22 - t), txt, font=f, fill=VERDE_ESCURO)
    return img


def contador(i, n):
    txt = f"{i}/{n}"
    f = fonte(56)
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), txt, font=f)
    w, h = r - l + 56, b - t + 36
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=22, fill=VERDE + (235,))
    d.text((28 - l, 18 - t), txt, font=f, fill=(255, 255, 255))
    return img


class CamadasViral:
    def __init__(self, proj):
        _, _, b_gancho, txt_gancho = proj["gancho"]
        self.produtos = proj["produtos"]
        self.q_gancho = round(b_gancho * BATIDA * FPS)
        self.q_prod = round(BATIDAS_PRODUTO * BATIDA * FPS)
        self.q_corpo = self.q_gancho + len(self.produtos) * self.q_prod
        # a assinatura do editar_reel (logo, @ e Zap) fecha o vídeo
        self.base = Camadas(txt_gancho, [(0, b_gancho + len(self.produtos) * BATIDAS_PRODUTO, None)])
        self.gancho = texto_destaque(txt_gancho, 88)
        n = len(self.produtos)
        self.nomes = [texto_destaque(p[2], 150) for p in self.produtos]
        self.etiquetas = [etiqueta(p[3]) for p in self.produtos]
        self.contadores = [contador(i + 1, n) for i in range(n)]
        self.escurece = Image.new("RGBA", (W, H), (0, 0, 0, 90))
        self.n = self.q_corpo + round(BATIDAS_FIM * BATIDA * FPS)

    def quadro(self, q):
        if q >= self.q_corpo:
            return self.base.quadro(self.base.inicio_fim + (q - self.q_corpo) / FPS)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        img.alpha_composite(self.base.marca, (W - self.base.marca.width - 36, 150))
        if q < self.q_gancho:
            dt = q / FPS
            img.alpha_composite(self.escurece)  # o gancho precisa ler bem em cima de qualquer fundo
            colar_centro(img, self.base.icone, W / 2, H * 0.36, pulo(dt))
            colar_centro(img, self.gancho, W / 2, H * 0.36 + 230, pulo(dt - 0.08))
            return img
        i = (q - self.q_gancho) // self.q_prod
        k = (q - self.q_gancho) % self.q_prod
        dt = k / FPS
        if k < 3:  # flash branco no corte
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(150 * (1 - k / 3)))))
        img.alpha_composite(self.contadores[i], (40, 150))
        colar_centro(img, self.nomes[i], W / 2, H * 0.66, pulo(dt - 0.03))
        colar_centro(img, self.etiquetas[i], W / 2, H * 0.66 + 150, pulo(dt - 0.22))
        return img


def main(projeto):
    proj = PROJETOS[projeto]
    camadas = CamadasViral(proj)
    tmp = Path(tempfile.mkdtemp())
    arq, ini, _, _ = proj["gancho"]
    cenas = [(arq, ini, camadas.q_gancho)] + [(p[0], p[1], camadas.q_prod) for p in proj["produtos"]]
    partes = []
    for i, (arquivo, inicio, quadros) in enumerate(cenas):
        parte = tmp / f"c{i}.mp4"
        if inicio is None:
            cena_foto(arquivo, quadros, i, True, parte)
        else:
            cena_video(arquivo, inicio, quadros, parte)
        partes.append(parte)
    lista = tmp / "lista.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in partes))
    corpo = tmp / "corpo.mp4"
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(corpo))

    wav = tmp / "musica.wav"
    musica.gerar(str(wav), proj.get("compassos"))
    total = camadas.n / FPS
    saida, capa = PASTA / f"{projeto}.mp4", PASTA / f"{projeto}-capa.jpg"
    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-i", str(corpo),
         "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav),
         "-filter_complex",
         f"[0:v]tpad=stop_mode=clone:stop_duration=10,setsar=1[v0];"
         f"[v0][1:v]overlay=0:0:eof_action=pass[v];"
         f"[2:a]atrim=0:{total:.3f},afade=t=out:st={total - 1:.3f}:d=1,loudnorm=I=-14:TP=-1.5[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", *X264, "-crf", "20", "-profile:v", "high",
         "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", str(saida)],
        stdin=subprocess.PIPE)
    for q in range(camadas.n):
        proc.stdin.write(camadas.quadro(q).tobytes())
    proc.stdin.close()
    if proc.wait():
        sys.exit("falha ao compor o vídeo")

    quadro = tmp / "quadro.jpg"  # capa: o gancho já na tela
    ffmpeg("-ss", "1.0", "-i", str(saida), "-frames:v", "1", "-q:v", "2", str(quadro))
    Image.open(quadro).save(capa, quality=92)
    print(f"{saida} ({duracao(str(saida)):.1f}s) e {capa}")


if __name__ == "__main__":
    main(sys.argv[1])
