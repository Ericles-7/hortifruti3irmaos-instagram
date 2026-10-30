"""Reel educativo "Como escolher fruta boa": uma dica por fruta, no formato que mais gera salvamentos.

Gancho com a pergunta e "salva esse vídeo"; depois cada fruta com o selo "Dica n", o nome em laranja
com contorno branco e a dica numa legenda branca (estilo legenda de vídeo viral); fecha com a
chamada "ou deixa que a gente escolhe pra você" e a assinatura animada (logo, @ e Zap).
Trilha de piseiro (musica_piseiro.py), com os cortes na batida.

Uso: python3 reels/reel_dicas.py <projeto>
Gera reels/<projeto>.mp4 e reels/<projeto>-capa.jpg.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

import musica_piseiro as trilha
from editar_reel import (FPS, PASTA, VERDE, H, W, X264, Camadas, colar_centro, duracao, ffmpeg, fonte, pulo,
                         texto_destaque)
from reel_viral import cena_video

BATIDA = trilha.BATIDA
BATIDAS_GANCHO = 6
BATIDAS_DICA = 6
BATIDAS_CHAMADA = 6
SEG_FIM = 3.4  # assinatura (logo e depois o contato)

PROJETOS = {
    "como-escolher": dict(
        gancho=("brutos/melancia-cortada.mp4", 0.0,
                "Como escolher\nfruta boa", "e não errar mais!", "salva esse vídeo"),
        dicas=[
            ("brutos/melancia-cortada.mp4", 1.5, "Melancia", "Dê uns tapinhas: som oco é sinal de madura."),
            ("brutos/mamao-1.mp4", 1.0, "Mamão", "Casca amarelando e firme ao apertar."),
            ("brutos/laranja.mp4", 0.5, "Tangerina", "Pegue a mais pesada: é a mais suculenta."),
            ("brutos/kiwi.mp4", 1.0, "Kiwi", "Apertou e cedeu um pouquinho? Tá no ponto."),
            ("brutos/uva-ameixa.mp4", 1.0, "Uva", "Bagos firmes e bem presos no cacho."),
        ],
        chamada=("brutos/uva-ameixa.mp4", 12.0, "Ou deixa que a gente\nescolhe pra você!",
                 "Manda sua lista no Zap"),
    ),
}


def legenda(txt, tamanho=54, largura=880):
    """Legenda branca com texto escuro, quebrada em linhas, como as legendas de vídeo viral."""
    f = fonte(tamanho, "Black")
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    linhas, atual = [], ""
    for p in txt.split():
        teste = f"{atual} {p}".strip()
        if d.textlength(teste, font=f) <= largura or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = p
    linhas.append(atual)
    alt = tamanho + 18
    w = int(max(d.textlength(l, font=f) for l in linhas)) + 70
    h = alt * len(linhas) + 40
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=28, fill=(255, 255, 255, 245))
    for i, l in enumerate(linhas):
        d.text((w / 2, 20 + alt * i + alt / 2), l, font=f, fill=(20, 24, 20), anchor="mm")
    return img


def selo(txt):
    f = fonte(50)
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), txt, font=f)
    w, h = r - l + 60, b - t + 34
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=VERDE + (240,))
    d.text((30 - l, 17 - t), txt, font=f, fill=(255, 255, 255))
    return img


class CamadasDicas:
    def __init__(self, proj):
        self.q_gancho = round(BATIDAS_GANCHO * BATIDA * FPS)
        self.q_dica = round(BATIDAS_DICA * BATIDA * FPS)
        self.q_chamada = round(BATIDAS_CHAMADA * BATIDA * FPS)
        dicas = proj["dicas"]
        self.q_corpo = self.q_gancho + len(dicas) * self.q_dica + self.q_chamada
        self.n = self.q_corpo + round(SEG_FIM * FPS)
        _, _, titulo, sub, salva = proj["gancho"]
        self.base = Camadas(titulo, [(0, 1, None)])  # só para a marca d'água e a assinatura final
        self.titulo = texto_destaque(titulo, 110)
        self.sub = legenda(sub, 58)
        self.salva = selo(salva)
        self.selos = [selo(f"Dica {i + 1}") for i in range(len(dicas))]
        self.nomes = [texto_destaque(d[2], 140) for d in dicas]
        self.dicas = [legenda(d[3]) for d in dicas]
        _, _, cham, zap = proj["chamada"]
        self.chamada = texto_destaque(cham, 88)
        self.zap = legenda(zap, 56)
        self.escurece = Image.new("RGBA", (W, H), (0, 0, 0, 100))

    def quadro(self, q):
        if q >= self.q_corpo:
            return self.base.quadro(self.base.inicio_fim + (q - self.q_corpo) / FPS)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if q < self.q_gancho:
            dt = q / FPS
            img.alpha_composite(self.escurece)
            colar_centro(img, self.titulo, W / 2, H * 0.40, pulo(dt))
            colar_centro(img, self.sub, W / 2, H * 0.40 + 210, pulo(dt - 0.35))
            colar_centro(img, self.salva, W / 2, H * 0.40 + 340, pulo(dt - 0.9))
            return img
        img.alpha_composite(self.base.marca, (W - self.base.marca.width - 36, 150))
        k = q - self.q_gancho
        if k < len(self.dicas) * self.q_dica:
            i, r = divmod(k, self.q_dica)
            dt = r / FPS
            if r < 3:  # flash branco no corte
                img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(150 * (1 - r / 3)))))
            colar_centro(img, self.selos[i], W / 2, H * 0.17, pulo(dt))
            colar_centro(img, self.nomes[i], W / 2, H * 0.60, pulo(dt - 0.03))
            colar_centro(img, self.dicas[i], W / 2, H * 0.60 + 190, pulo(dt - 0.3))
            return img
        dt = (k - len(self.dicas) * self.q_dica) / FPS
        img.alpha_composite(self.escurece)
        colar_centro(img, self.chamada, W / 2, H * 0.45, pulo(dt))
        colar_centro(img, self.zap, W / 2, H * 0.45 + 190, pulo(dt - 0.25))
        return img


def main(projeto):
    proj = PROJETOS[projeto]
    camadas = CamadasDicas(proj)
    tmp = Path(tempfile.mkdtemp())
    cenas = [(proj["gancho"][0], proj["gancho"][1], camadas.q_gancho)]
    cenas += [(d[0], d[1], camadas.q_dica) for d in proj["dicas"]]
    cenas.append((proj["chamada"][0], proj["chamada"][1], camadas.q_chamada))
    partes = []
    for i, (arquivo, ini, quadros) in enumerate(cenas):
        parte = tmp / f"c{i}.mp4"
        cena_video(arquivo, ini, quadros, parte)
        partes.append(parte)
    lista = tmp / "lista.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in partes))
    corpo = tmp / "corpo.mp4"
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(corpo))

    total = camadas.n / FPS
    wav = tmp / "musica.wav"
    trilha.gerar(str(wav), [None] * (int(total / trilha.COMPASSO) + 1))
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

    quadro = tmp / "quadro.jpg"  # capa: o gancho completo na tela
    ffmpeg("-ss", "2.0", "-i", str(saida), "-frames:v", "1", "-q:v", "2", str(quadro))
    Image.open(quadro).save(capa, quality=92)
    print(f"{saida} ({duracao(str(saida)):.1f}s) e {capa}")


if __name__ == "__main__":
    main(sys.argv[1])
