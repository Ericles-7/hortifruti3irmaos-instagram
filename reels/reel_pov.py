"""Reel "POV: você chegou cedo na Segunda da Fruta" (Roteiro 2 do PLANEJAMENTO.md).

Gancho em formato POV; depois cortes rápidos na batida pelas frutas que chegaram, com o nome pequeno
no canto; a frase de urgência ("fruta que chegou hoje é fruta que acaba hoje"); a chamada pro Zap e a
assinatura animada. Trilha de piseiro.

Uso: python3 reels/reel_pov.py <projeto>
Gera reels/<projeto>.mp4 e reels/<projeto>-capa.jpg.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

import musica_piseiro as trilha
from editar_reel import FPS, PASTA, H, W, X264, Camadas, colar_centro, duracao, ffmpeg, pulo, texto_destaque
from reel_dicas import legenda, selo
from reel_viral import cena_video

BATIDA = trilha.BATIDA
SEG_FIM = 3.4

# projeto: blocos (vídeo, início, batidas, tipo, texto). tipo: "gancho", "corte" (nome no canto),
# "frase" (texto grande no meio) ou "chamada" (texto grande + legenda do Zap).
PROJETOS = {
    "pov-segunda-fruta": [
        ("arquivo/2026-10/brutos/melancia-cortada.mp4", 0.0, 6, "gancho",
         "você chegou cedo na Segunda da Fruta do Hortifruti 3 Irmãos"),
        ("arquivo/2026-10/brutos/melancia-cortada.mp4", 1.6, 2, "corte", "Melancia"),
        ("arquivo/2026-10/brutos/mamao-1.mp4", 1.0, 2, "corte", "Mamão"),
        ("arquivo/2026-10/brutos/laranja.mp4", 0.5, 2, "corte", "Tangerina"),
        ("arquivo/2026-10/brutos/uva-ameixa.mp4", 1.0, 2, "corte", "Uva sem semente"),
        ("arquivo/2026-10/brutos/uva-ameixa.mp4", 12.0, 2, "corte", "Ameixa"),
        ("arquivo/2026-10/brutos/kiwi.mp4", 1.0, 2, "corte", "Kiwi"),
        ("arquivo/2026-10/brutos/manga.mp4", 0.0, 2, "corte", "Manga coité"),
        ("arquivo/2026-10/brutos/tangerina-caixa.mp4", 0.5, 2, "corte", "Tangerina na caixa"),
        ("arquivo/2026-10/brutos/ameixa.mp4", 2.75, 6, "frase", "Fruta que chegou hoje\né fruta que acaba hoje!"),
        ("arquivo/2026-10/brutos/uva-ameixa.mp4", 4.0, 6, "chamada", "Passa aqui ou\npede pelo Zap!|A gente separa as mais bonitas"),
    ],
}


def caber(img, largura=W - 60):
    if img.width <= largura:
        return img
    return img.resize((largura, round(img.height * largura / img.width)), Image.LANCZOS)


class CamadasPov:
    def __init__(self, blocos):
        self.blocos = []
        q = 0
        for arq, ini, batidas, tipo, txt in blocos:
            n = round(batidas * BATIDA * FPS)
            if tipo == "gancho":
                arte = (selo("POV:"), legenda(txt, 62, 860))
            elif tipo == "corte":
                arte = (selo(txt),)
            elif tipo == "frase":
                arte = (caber(texto_destaque(txt, 96)),)
            else:
                grande, peq = txt.split("|")
                arte = (caber(texto_destaque(grande, 96)), legenda(peq, 54))
            self.blocos.append((q, n, tipo, arte))
            q += n
        self.q_corpo = q
        self.n = q + round(SEG_FIM * FPS)
        self.base = Camadas("", [(0, 1, None)])  # marca d'água e assinatura final
        self.escurece = Image.new("RGBA", (W, H), (0, 0, 0, 100))

    def quadro(self, q):
        if q >= self.q_corpo:
            return self.base.quadro(self.base.inicio_fim + (q - self.q_corpo) / FPS)
        ini, n, tipo, arte = next(b for b in self.blocos if b[0] <= q < b[0] + b[1])
        r = q - ini
        dt = r / FPS
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if tipo == "gancho":
            img.alpha_composite(self.escurece)
            colar_centro(img, arte[0], W / 2, H * 0.36, pulo(dt))
            colar_centro(img, arte[1], W / 2, H * 0.36 + 230, pulo(dt - 0.25))
            return img
        img.alpha_composite(self.base.marca, (W - self.base.marca.width - 36, 150))
        if r < 3:  # flash branco no corte
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(130 * (1 - r / 3)))))
        if tipo == "corte":
            colar_centro(img, arte[0], 60 + arte[0].width / 2, H * 0.80, pulo(dt))
        elif tipo == "frase":
            img.alpha_composite(self.escurece)
            colar_centro(img, arte[0], W / 2, H * 0.47, pulo(dt))
        else:
            img.alpha_composite(self.escurece)
            colar_centro(img, arte[0], W / 2, H * 0.43, pulo(dt))
            colar_centro(img, arte[1], W / 2, H * 0.43 + 210, pulo(dt - 0.25))
        return img


def main(projeto):
    blocos = PROJETOS[projeto]
    camadas = CamadasPov(blocos)
    tmp = Path(tempfile.mkdtemp())
    partes = []
    for i, ((arq, ini, *_), (_, n, _, _)) in enumerate(zip(blocos, camadas.blocos)):
        parte = tmp / f"c{i}.mp4"
        cena_video(arq, ini, n, parte)
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

    quadro = tmp / "quadro.jpg"  # capa: o gancho completo na tela
    ffmpeg("-ss", "1.5", "-i", str(saida), "-frames:v", "1", "-q:v", "2", str(quadro))
    Image.open(quadro).save(capa, quality=92)
    print(f"{saida} ({duracao(str(saida)):.1f}s) e {capa}")


if __name__ == "__main__":
    main(sys.argv[1])
