"""Edita o vídeo bruto da banca no reel "Tour pela banca" (1080x1920).

Uso: python3 reels/editar_reel.py <video_bruto.mp4>
Gera reels/tour-banca.mp4 e reels/tour-banca-capa.jpg.

Modelo de edição (referência: reels de hortifruti com produto em destaque a cada ~2 s):
gancho em plano aberto com toque na tela e texto que "pula"; depois uma cena por produto, em
corte seco no ritmo da música, com o nome do produto em laranja com contorno branco aparecendo
com efeito de pulo; no fim, assinatura animada com o logo, o @ do Instagram e o Zap.
"""
import math
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import musica

PASTA = Path(__file__).parent
FONTE = PASTA / "fonts" / "Nunito.ttf"
LOGO = PASTA / "logo.png"
SAIDA = PASTA / "tour-banca.mp4"
CAPA = PASTA / "tour-banca-capa.jpg"

W, H, FPS = 1080, 1920, 30
LARANJA = (255, 106, 0)
VERDE = (28, 94, 32)
VERDE_ESCURO = (14, 52, 18)
VERDE_CLARO = (200, 240, 160)
AMARELO = (255, 222, 120)
BRANCO = (255, 255, 255)
BATIDA = musica.BATIDA
INSTAGRAM = "@hortifruti3irmaos_uirauna"

GANCHO = "Aqui no Hortifruti 3 Irmãos\nvocê encontra..."
# Cenas do vídeo bruto: (início em s, duração em batidas, texto). A 1ª é o gancho.
# Somam 36 batidas (9 compassos); a assinatura final ocupa mais 8.
CENAS = [
    (26.0, 4, None),  # plano aberto do corredor
    (0.0, 4, "laranja..."),
    (4.9, 4, "maracujá e batata..."),
    (7.1, 4, "cebola..."),
    (9.95, 3, "tomate..."),
    (12.4, 3, "abacaxi..."),
    (14.8, 3, "melão..."),
    (18.3, 3, "abacate..."),
    (20.0, 3, "tangerina..."),
    (22.0, 5, "e muito mais!"),
]
BATIDAS_FIM = 8
APROXIMA = 1.12  # leve aproximação para o produto encher a tela


def fonte(tamanho, peso="Black"):
    f = ImageFont.truetype(str(FONTE), tamanho)
    f.set_variation_by_name(peso)
    return f


def texto_destaque(txt, tamanho=84):
    """Texto laranja com contorno branco e sombra suave, recortado no tamanho certo."""
    f = fonte(tamanho)
    borda = max(5, tamanho // 13)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = (round(v) for v in tmp.multiline_textbbox((0, 0), txt, font=f, align="center", spacing=6,
                                                           stroke_width=borda))
    pad = 24
    img = Image.new("RGBA", (r - l + 2 * pad, b - t + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pos = (pad - l, pad - t)
    sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sombra).multiline_text((pos[0] + 3, pos[1] + 6), txt, font=f, fill=(0, 0, 0, 120), align="center",
                                          spacing=6, stroke_width=borda, stroke_fill=(0, 0, 0, 120))
    img.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(6)))
    d.multiline_text(pos, txt, font=f, fill=LARANJA, align="center", spacing=6, stroke_width=borda, stroke_fill=BRANCO)
    return img


def logo_inteiro():
    return Image.open(LOGO).convert("RGBA")


def icone_logo(tamanho):
    """Só o círculo do carrinho, para usar como ícone acima do texto do gancho."""
    logo = logo_inteiro()
    lado = logo.height
    ic = logo.crop((0, 0, lado, lado))
    mascara = Image.new("L", (lado, lado), 0)
    ImageDraw.Draw(mascara).ellipse((14, 14, lado - 14, lado - 14), fill=255)
    redondo = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    redondo.paste(ic, (0, 0), mascara)
    return redondo.resize((tamanho, tamanho), Image.LANCZOS)


def pulo(t, dur=0.28):
    """Escala do efeito de "pulo": cresce passando um pouco do tamanho e assenta (easeOutBack)."""
    if t <= 0:
        return 0.0
    if t >= dur:
        return 1.0
    x = t / dur
    c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def colar_centro(base, img, cx, cy, escala=1.0, alfa=1.0):
    if escala <= 0.01 or alfa <= 0:
        return
    if escala != 1.0:
        img = img.resize((max(1, round(img.width * escala)), max(1, round(img.height * escala))), Image.BILINEAR)
    if alfa < 1:
        img = img.copy()
        img.putalpha(img.getchannel("A").point(lambda v: int(v * alfa)))
    base.alpha_composite(img, (round(cx - img.width / 2), round(cy - img.height / 2)))


def icone_instagram(lado, cor):
    img = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    e = max(3, lado // 12)
    d.rounded_rectangle((e, e, lado - e, lado - e), radius=lado // 4, outline=cor, width=e)
    r = lado // 4.2
    d.ellipse((lado / 2 - r, lado / 2 - r, lado / 2 + r, lado / 2 + r), outline=cor, width=e)
    p = lado * 0.73
    d.ellipse((p - e, lado * 0.27 - e, p + e, lado * 0.27 + e), fill=cor)
    return img


def fundo_gradiente(topo, baixo):
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(topo, baixo)) + (255,))
    return img


class Camadas:
    """Desenha, quadro a quadro, tudo o que vai por cima do vídeo (textos e assinatura final)."""

    def __init__(self):
        self.inicios = []
        t = 0.0
        for _, batidas, _ in CENAS:
            self.inicios.append(t)
            t += batidas * BATIDA
        self.inicio_fim = t
        self.total = t + BATIDAS_FIM * BATIDA
        self.gancho = texto_destaque(GANCHO, 80)
        self.icone = icone_logo(110)
        self.textos = [texto_destaque(txt) if txt else None for _, _, txt in CENAS]
        self.marca = self._marca_dagua()
        self.fundo_claro = fundo_gradiente((70, 160, 50), (40, 120, 36))
        self.fundo_escuro = fundo_gradiente((24, 70, 26), VERDE_ESCURO)
        logo = logo_inteiro()
        self.logo = logo.resize((640, round(logo.height * 640 / logo.width)), Image.LANCZOS)
        self.cartao_logo = self._cartao(self.logo)
        self.contato = self._contato()

    def _marca_dagua(self):
        f = fonte(30, "Bold")
        d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        w = int(d.textlength(INSTAGRAM, font=f)) + 70
        img = Image.new("RGBA", (w, 48), (0, 0, 0, 0))
        img.alpha_composite(icone_instagram(36, (255, 255, 255, 190)), (0, 6))
        ImageDraw.Draw(img).text((50, 4), INSTAGRAM, font=f, fill=(255, 255, 255, 190))
        return img

    def _cartao(self, logo):
        pad = 34
        img = Image.new("RGBA", (logo.width + 2 * pad + 60, logo.height + 2 * pad + 60), (0, 0, 0, 0))
        cartao = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(cartao).rounded_rectangle((30, 30, img.width - 30, img.height - 30), radius=48,
                                                 fill=VERDE + (255,))
        img.alpha_composite(Image.eval(cartao.filter(ImageFilter.GaussianBlur(16)), lambda v: v // 2))
        img.alpha_composite(cartao)
        img.alpha_composite(logo, (30 + pad, 30 + pad))
        return img

    def _contato(self):
        img = Image.new("RGBA", (W, 520), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        f = fonte(54)
        ig = icone_instagram(64, BRANCO)
        w = 64 + 22 + d.textlength(INSTAGRAM, font=f)
        x = (W - w) / 2
        img.alpha_composite(ig, (round(x), 8))
        d.text((x + 86, 0), INSTAGRAM, font=f, fill=BRANCO)
        txt = "Chama no Zap  (83) 99937-8165"
        fz = fonte(50)
        l, t, r, b = d.textbbox((0, 0), txt, font=fz)
        pw, ph = r - l + 112, b - t + 60
        px = (W - pw) / 2
        d.rounded_rectangle((px, 130, px + pw, 130 + ph), radius=ph / 2, fill=AMARELO)
        d.text((px + 56 - l, 130 + 30 - t), txt, font=fz, fill=VERDE_ESCURO)
        fe = fonte(42, "ExtraBold")
        for i, linha in enumerate(["Rua Francisco Euclides Fernandes, 1200", "Uiraúna - PB"]):
            d.text(((W - d.textlength(linha, font=fe)) / 2, 300 + i * 58), linha, font=fe, fill=VERDE_CLARO)
        return img

    def quadro(self, t):
        if t >= self.inicio_fim:
            return self._assinatura(t - self.inicio_fim)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        img.alpha_composite(self.marca, (W - self.marca.width - 36, 150))
        cena = max(i for i, ini in enumerate(self.inicios) if ini <= t)
        dt = t - self.inicios[cena]
        if cena == 0:
            self._gancho(img, dt)
        elif self.textos[cena] is not None:
            colar_centro(img, self.textos[cena], W / 2, H * 0.74, pulo(dt - 0.04))
        return img

    def _gancho(self, img, dt):
        toque = 0.55  # o "dedo" toca a tela e o texto pula
        d = ImageDraw.Draw(img)
        cx, cy = W * 0.56, H * 0.53
        if dt < toque + 0.35:
            # bolinha de toque chegando e o anel se abrindo no toque
            chega = min(1, dt / toque)
            x = cx + (1 - chega) ** 2 * 260
            y = cy + (1 - chega) ** 2 * 360
            r = 34 if dt < toque else 34 * (1 - min(1, (dt - toque) / 0.2) * 0.4)
            a = 230 if dt < toque + 0.15 else int(230 * max(0, 1 - (dt - toque - 0.15) / 0.2))
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, a), outline=(0, 0, 0, a // 3), width=3)
            if dt >= toque:
                k = (dt - toque) / 0.35
                ra = 34 + 90 * k
                d.ellipse((cx - ra, cy - ra, cx + ra, cy + ra), outline=(255, 255, 255, int(220 * (1 - k))), width=6)
        e = pulo(dt - toque)
        colar_centro(img, self.icone, W / 2, H * 0.40, e)
        colar_centro(img, self.gancho, W / 2, H * 0.40 + 175, e)

    def _assinatura(self, dt):
        troca = 1.7  # fundo claro com o logo -> fundo escuro com o contato
        if dt < troca:
            img = self.fundo_claro.copy()
            e = pulo(dt, 0.35)
            if dt < 0.3:  # leve "glitch" na entrada do logo
                for desloc, cor in ((-14, (255, 60, 60, 110)), (14, (60, 200, 255, 110))):
                    fantasma = Image.new("RGBA", self.cartao_logo.size, cor)
                    fantasma.putalpha(self.cartao_logo.getchannel("A").point(lambda v: v * 110 // 255))
                    colar_centro(img, fantasma, W / 2 + desloc * (1 - dt / 0.3), H * 0.45, e)
            colar_centro(img, self.cartao_logo, W / 2, H * 0.45, e)
            return img
        k = min(1, (dt - troca) / 0.35)
        img = Image.blend(self.fundo_claro, self.fundo_escuro, k)
        sobe = 1 - (1 - k) ** 3
        colar_centro(img, self.cartao_logo, W / 2, H * 0.45 - sobe * 330, 1 - 0.18 * sobe)
        e = max(0.0, min(1.0, (dt - troca - 0.15) / 0.35))
        colar_centro(img, self.contato, W / 2, H * 0.62 + (1 - e) * 60, 1.0, e)
        return img


def ffmpeg(*args, **kw):
    return subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True, **kw)


def duracao(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", video], capture_output=True, text=True, check=True)
    return float(out.stdout)


X264 = ["-c:v", "libx264", "-preset", "slow", "-pix_fmt", "yuv420p", "-r", str(FPS)]


def main(bruto):
    tmp = Path(tempfile.mkdtemp())

    # 1) estabiliza, corrige a cor (claro, saturado e limpo) e leva para 1080x1920
    trf = tmp / "estab.trf"
    ffmpeg("-i", bruto, "-vf", f"vidstabdetect=shakiness=8:accuracy=15:result={trf}", "-f", "null", "-")
    base = tmp / "base.mp4"
    ffmpeg("-i", bruto, "-an", "-vf",
           f"vidstabtransform=input={trf}:smoothing=30:zoom=5:optzoom=0,"
           f"scale={round(W * APROXIMA / 2) * 2}:{round(H * APROXIMA / 2) * 2}:flags=lanczos,crop={W}:{H},"
           "eq=saturation=1.28:contrast=1.07:brightness=0.035:gamma=0.97,"
           "vibrance=intensity=0.15,unsharp=5:5:0.6",
           *X264, "-crf", "15", str(base))

    # 2) cenas em corte seco, no tamanho exato em batidas; a assinatura entra depois por cima
    camadas = Camadas()
    partes = []
    for i, (ini, batidas, _) in enumerate(CENAS):
        quadros = round(batidas * BATIDA * FPS)
        parte = tmp / f"cena{i}.mp4"
        ffmpeg("-ss", f"{ini:.3f}", "-i", str(base), "-frames:v", str(quadros), *X264, "-crf", "15", str(parte))
        partes.append(parte)
    lista = tmp / "lista.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in partes))
    corpo = tmp / "corpo.mp4"
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(corpo))

    # 3) composição: vídeo + camadas desenhadas quadro a quadro + trilha
    musica_wav = tmp / "musica.wav"
    musica.gerar(str(musica_wav))
    n = round(camadas.total * FPS)
    total = n / FPS
    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-i", str(corpo),
         "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-i", str(musica_wav),
         "-filter_complex",
         f"[0:v]tpad=stop_mode=clone:stop_duration=10,setsar=1[v0];"
         f"[v0][1:v]overlay=0:0:eof_action=pass[v];"
         f"[2:a]atrim=0:{total:.3f},afade=t=out:st={total - 1.0:.3f}:d=1.0,loudnorm=I=-14:TP=-1.5[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}",
         *X264, "-crf", "20", "-profile:v", "high",
         "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", str(SAIDA)],
        stdin=subprocess.PIPE)
    for q in range(n):
        proc.stdin.write(camadas.quadro(q / FPS).tobytes())
    proc.stdin.close()
    if proc.wait():
        sys.exit("falha ao compor o vídeo")

    # 4) capa: o plano aberto com o gancho já na tela
    quadro = tmp / "quadro.jpg"
    ffmpeg("-ss", "1.2", "-i", str(SAIDA), "-frames:v", "1", "-q:v", "2", str(quadro))
    Image.open(quadro).save(CAPA, quality=92)
    print(f"{SAIDA} ({duracao(str(SAIDA)):.1f}s) e {CAPA}")


if __name__ == "__main__":
    main(sys.argv[1])
