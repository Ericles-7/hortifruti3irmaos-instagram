"""Reel "Lista do fim de semana" (Roteiro 5 do PLANEJAMENTO.md), para as sextas.

Gancho "Sextou!"; depois um produto por vez no fundo enquanto uma lista de papel vai sendo marcada
(✔) item por item; fecha com a chamada pro Zap, o horário de sábado e a assinatura animada.
Trilha de piseiro.

Uso: python3 reels/reel_lista.py <projeto>
Gera reels/<projeto>.mp4 e reels/<projeto>-capa.jpg.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

import musica_piseiro as trilha
from editar_reel import (FPS, LARANJA, PASTA, VERDE, H, W, X264, Camadas, colar_centro, duracao, ffmpeg, fonte,
                         pulo, texto_destaque)
from reel_dicas import legenda
from reel_pov import caber
from reel_viral import cena_video

BATIDA = trilha.BATIDA
BATIDAS_GANCHO = 6
BATIDAS_ITEM = 4
BATIDAS_CHAMADA = 6
SEG_FIM = 3.4

PROJETOS = {
    "lista-fim-de-semana": dict(
        gancho=("brutos/uva-ameixa.mp4", 4.0, "Sextou!", "Já fez a lista do fim de semana?"),
        titulo="Lista do fim de semana",
        itens=[
            ("brutos/mamao-1.mp4", 1.0, "Mamão pro café"),
            ("brutos/uva-ameixa.mp4", 1.0, "Uva pra sobremesa"),
            ("brutos/verduras.mp4", 0.5, "Alface e cheiro-verde"),
            ("brutos/pimenta-de-cheiro.mp4", 0.75, "Pimenta-de-cheiro"),
            ("brutos/pimentao.mp4", 3.0, "Pimentão pro vinagrete"),
            ("brutos/melancia-cortada.mp4", 1.5, "Melancia pra gelar"),
            ("brutos/doces-2.mp4", 0.0, "Doce caseiro"),
        ],
        chamada=("brutos/ameixa.mp4", 2.75, "Separa pelo Zap hoje\ne passa pra pegar!",
                 "Sábado aberto das 4h às 15h"),
    ),
}

LINHA = 74


class Lista:
    """O papel da lista: título e os itens, cada um com a caixinha que recebe o ✔."""

    def __init__(self, titulo, itens):
        self.f = fonte(46, "ExtraBold")
        self.ft = fonte(52)
        self.itens = itens
        self.w = 860
        self.h = 130 + LINHA * len(itens) + 30

    def desenhar(self, feitos, k_ultimo):
        """feitos: quantos itens já aparecem; o último entra com o ✔ animado (k_ultimo de 0 a 1)."""
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, self.w - 1, self.h - 1), radius=34, fill=(255, 252, 240, 245))
        d.text((self.w / 2, 70), "Lista do fim de semana", font=self.ft, fill=VERDE, anchor="mm")
        d.line((50, 118, self.w - 50, 118), fill=(220, 210, 180), width=3)
        for i, txt in enumerate(self.itens[:feitos]):
            y = 130 + LINHA * i + LINHA / 2
            k = k_ultimo if i == feitos - 1 else 1.0
            d.rounded_rectangle((50, y - 22, 94, y + 22), radius=8, outline=(120, 120, 110), width=4)
            if k > 0:  # o ✔ é desenhado aos poucos: primeiro a perninha curta, depois a longa
                a, b, c = (56, y), (70, y + 16), (102, y - 26)
                k1 = min(1, k * 2)
                d.line((a, (a[0] + (b[0] - a[0]) * k1, a[1] + (b[1] - a[1]) * k1)), fill=LARANJA, width=9)
                if k > 0.5:
                    k2 = (k - 0.5) * 2
                    d.line((b, (b[0] + (c[0] - b[0]) * k2, b[1] + (c[1] - b[1]) * k2)), fill=LARANJA, width=9)
            d.text((124, y), txt, font=self.f, fill=(30, 34, 30), anchor="lm")
        return img


class CamadasLista:
    def __init__(self, proj):
        self.q_gancho = round(BATIDAS_GANCHO * BATIDA * FPS)
        self.q_item = round(BATIDAS_ITEM * BATIDA * FPS)
        self.q_chamada = round(BATIDAS_CHAMADA * BATIDA * FPS)
        self.itens = [i[2] for i in proj["itens"]]
        self.q_corpo = self.q_gancho + len(self.itens) * self.q_item + self.q_chamada
        self.n = self.q_corpo + round(SEG_FIM * FPS)
        _, _, grande, peq = proj["gancho"]
        self.sextou = texto_destaque(grande, 150)
        self.pergunta = legenda(peq, 58)
        self.lista = Lista(proj["titulo"], self.itens)
        _, _, cham, sab = proj["chamada"]
        self.chamada = caber(texto_destaque(cham, 92))
        self.sabado = legenda(sab, 54)
        self.base = Camadas("", [(0, 1, None)])
        self.escurece = Image.new("RGBA", (W, H), (0, 0, 0, 100))

    def quadro(self, q):
        if q >= self.q_corpo:
            return self.base.quadro(self.base.inicio_fim + (q - self.q_corpo) / FPS)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if q < self.q_gancho:
            dt = q / FPS
            img.alpha_composite(self.escurece)
            colar_centro(img, self.sextou, W / 2, H * 0.40, pulo(dt))
            colar_centro(img, self.pergunta, W / 2, H * 0.40 + 190, pulo(dt - 0.3))
            return img
        img.alpha_composite(self.base.marca, (W - self.base.marca.width - 36, 150))
        k = q - self.q_gancho
        if k < len(self.itens) * self.q_item:
            i, r = divmod(k, self.q_item)
            if r < 3:  # flash branco no corte
                img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(120 * (1 - r / 3)))))
            marca = max(0.0, min(1.0, (r / FPS - 0.25) / 0.35))  # o ✔ entra logo depois do corte
            papel = self.lista.desenhar(i + 1, marca)
            colar_centro(img, papel, W / 2, 250 + papel.height / 2, pulo(k / FPS) if i == 0 else 1.0)
            return img
        dt = (k - len(self.itens) * self.q_item) / FPS
        img.alpha_composite(self.escurece)
        colar_centro(img, self.chamada, W / 2, H * 0.43, pulo(dt))
        colar_centro(img, self.sabado, W / 2, H * 0.43 + 200, pulo(dt - 0.25))
        return img


def main(projeto):
    proj = PROJETOS[projeto]
    camadas = CamadasLista(proj)
    tmp = Path(tempfile.mkdtemp())
    cenas = [(proj["gancho"][0], proj["gancho"][1], camadas.q_gancho)]
    cenas += [(a, i, camadas.q_item) for a, i, _ in proj["itens"]]
    cenas.append((proj["chamada"][0], proj["chamada"][1], camadas.q_chamada))
    partes = []
    for n, (arq, ini, quadros) in enumerate(cenas):
        parte = tmp / f"c{n}.mp4"
        cena_video(arq, ini, quadros, parte)
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
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", *X264, "-crf", "23", "-profile:v", "high",
         "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", str(saida)],
        stdin=subprocess.PIPE)
    for q in range(camadas.n):
        proc.stdin.write(camadas.quadro(q).tobytes())
    proc.stdin.close()
    if proc.wait():
        sys.exit("falha ao compor o vídeo")

    quadro = tmp / "quadro.jpg"  # capa: o "Sextou!" na tela
    ffmpeg("-ss", "1.5", "-i", str(saida), "-frames:v", "1", "-q:v", "2", str(quadro))
    Image.open(quadro).save(capa, quality=92)
    print(f"{saida} ({duracao(str(saida)):.1f}s) e {capa}")


if __name__ == "__main__":
    main(sys.argv[1])
