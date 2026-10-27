"""Edita o vídeo bruto da banca no reel "Tour pela banca" (1080x1920, com a marca do hortifruti).

Uso: python3 reels/editar_reel.py <video_bruto.mp4>
Gera reels/tour-banca.mp4 e reels/tour-banca-capa.jpg.

Edição: estabiliza, corrige a cor, tira os trechos tremidos e borrados, corta no ritmo da
música (112 BPM), dá um zoom suave em cada cena, anima os textos e põe a trilha de musica.py.
"""
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
VERDE = (28, 94, 32)
VERDE_CLARO = (200, 240, 160)
AMARELO = (255, 222, 120)
BRANCO = (255, 255, 255)
BATIDA = musica.BATIDA

# Cenas aproveitadas do vídeo bruto: (início em s, duração em batidas, legenda)
# Somam 36 batidas (9 compassos); o cartão final ocupa mais 8.
CENAS = [
    (0.0, 5, None),  # laranjas, com o gancho por cima
    (4.9, 4, "Maracujá e batata"),
    (7.1, 4, "Cebola roxa e branca"),
    (9.95, 3, "Tomate no ponto"),
    (12.1, 3, "Abacaxi e melão"),
    (14.8, 3, "Abacaxi e melão"),
    (18.3, 5, "Fruta escolhida a dedo"),
    (23.2, 9, "Tudo fresquinho pra você"),
]
BATIDAS_FIM = 8
QUADRO_CAPA = 12.7  # abacaxi, o trecho mais nítido


def fonte(tamanho, peso="Black"):
    f = ImageFont.truetype(str(FONTE), tamanho)
    f.set_variation_by_name(peso)
    return f


def texto_centro(d, y, txt, f, cor, sombra=True):
    x = (W - d.textlength(txt, font=f)) / 2
    if sombra:
        d.text((x + 4, y + 5), txt, font=f, fill=(0, 0, 0, 110))
    d.text((x, y), txt, font=f, fill=cor)


def pilula(d, y, txt, f, fundo, cor, pad_x=44, pad_y=22):
    l, t, r, b = d.textbbox((0, 0), txt, font=f)
    w, h = r - l + 2 * pad_x, b - t + 2 * pad_y
    x = (W - w) / 2
    d.rounded_rectangle((x, y, x + w, y + h), radius=h / 2, fill=fundo)
    d.text((x + pad_x - l, y + pad_y - t), txt, font=f, fill=cor)
    return y + h


def logo_card(img, y, largura):
    logo = Image.open(LOGO).convert("RGBA")
    logo = logo.resize((largura, round(logo.height * largura / logo.width)), Image.LANCZOS)
    x = (W - logo.width) // 2
    card = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle(
        (x - 26, y - 14, x + logo.width + 26, y + logo.height + 14), radius=40, fill=VERDE + (255,))
    sombra = card.filter(ImageFilter.GaussianBlur(18))
    img.alpha_composite(Image.eval(sombra, lambda v: v // 2))
    img.alpha_composite(card)
    img.alpha_composite(logo, (x, y))
    return y + logo.height + 14


def camada(caminho, desenhar):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    desenhar(img, ImageDraw.Draw(img))
    img.save(caminho)


def camada_topo(img, d):
    logo_card(img, 70, 380)


def camada_gancho(img, d):
    pilula(d, 330, "TOUR PELA BANCA", fonte(46), VERDE_CLARO, VERDE)
    texto_centro(d, 430, "Vem ver o que", fonte(110), BRANCO)
    texto_centro(d, 550, "tem hoje!", fonte(110), AMARELO)


def camada_legenda(txt):
    return lambda img, d: pilula(d, 1540, txt, fonte(66), VERDE + (238,), BRANCO, pad_x=56, pad_y=28)


def cartao_final(caminho):
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(28 + 50 * t), int(94 + 80 * t), int(32 + 30 * t), 255))
    y = logo_card(img, 360, 620)
    texto_centro(d, y + 120, "Feira fresquinha", fonte(96), BRANCO)
    texto_centro(d, y + 230, "todo dia!", fonte(96), AMARELO)
    y = pilula(d, y + 420, "Chama no Zap  (83) 99937-8165", fonte(50), BRANCO, VERDE, pad_x=56, pad_y=30)
    texto_centro(d, y + 70, "Rua Francisco Euclides Fernandes, 1200", fonte(44, "ExtraBold"), VERDE_CLARO, sombra=False)
    texto_centro(d, y + 130, "Uiraúna - PB", fonte(44, "ExtraBold"), VERDE_CLARO, sombra=False)
    texto_centro(d, 1700, "Siga @hortifruti3irmaos_uirauna", fonte(40, "Bold"), BRANCO, sombra=False)
    img.convert("RGB").save(caminho, quality=95)


def capa(quadro, caminho):
    img = Image.open(quadro).convert("RGBA").resize((W, H))
    escuro = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    de = ImageDraw.Draw(escuro)
    for y in range(H):  # escurece o meio para o título aparecer bem
        a = int(150 * max(0, 1 - abs(y - 960) / 700))
        de.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    img.alpha_composite(escuro)
    logo_card(img, 380, 440)
    d = ImageDraw.Draw(img)
    texto_centro(d, 760, "Tour pela", fonte(130), BRANCO)
    texto_centro(d, 900, "banca", fonte(150), AMARELO)
    pilula(d, 1120, "Vem ver o que tem hoje!", fonte(54), VERDE_CLARO, VERDE)
    img.convert("RGB").save(caminho, quality=92)


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def duracao(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", video], capture_output=True, text=True, check=True)
    return float(out.stdout)


X264 = ["-c:v", "libx264", "-preset", "slow", "-pix_fmt", "yuv420p", "-r", str(FPS)]


def zoom(quadros, entrando):
    """Zoom suave de 7% ao longo da cena (para dentro ou para fora), sem tremer."""
    z = f"1+0.07*on/{quadros}" if entrando else f"1.07-0.07*on/{quadros}"
    return (f"scale={2 * W}:{2 * H}:flags=lanczos,"
            f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}")


def anima(k, ini, fim, deslize=36):
    """Filtro para a entrada k: aparece com fade e sobe um pouco; some com fade."""
    filtro = (f"[{k}:v]format=rgba,fade=t=in:st={ini:.3f}:d=0.22:alpha=1,"
              f"fade=t=out:st={fim - 0.18:.3f}:d=0.18:alpha=1[o{k}];")
    y = f"if(lt(t,{ini + 0.3:.3f}),{deslize}*(1-(t-{ini:.3f})/0.3),0)"
    return filtro, f"overlay=x=0:y='{y}':enable='between(t,{ini:.3f},{fim:.3f})'"


def main(bruto):
    tmp = Path(tempfile.mkdtemp())

    # 1) estabiliza e corrige a cor do vídeo inteiro, já em 1080x1920
    trf = tmp / "estab.trf"
    ffmpeg("-i", bruto, "-vf", f"vidstabdetect=shakiness=8:accuracy=15:result={trf}", "-f", "null", "-")
    base = tmp / "base.mp4"
    ffmpeg("-i", bruto, "-an", "-vf",
           f"vidstabtransform=input={trf}:smoothing=30:zoom=5:optzoom=0,"
           f"scale={W}:{H}:flags=lanczos,"
           "eq=saturation=1.25:contrast=1.08:brightness=0.015:gamma=0.98,"
           "vibrance=intensity=0.12,colortemperature=temperature=5600:mix=0.6,"
           "unsharp=5:5:0.55,vignette=PI/6",
           *X264, "-crf", "15", str(base))

    # 2) recorta cada cena no tamanho exato em batidas, com zoom alternado
    partes = []
    for i, (ini, batidas, _) in enumerate(CENAS):
        quadros = round(batidas * BATIDA * FPS)
        parte = tmp / f"cena{i}.mp4"
        ffmpeg("-i", str(base), "-ss", f"{ini:.3f}", "-vf", zoom(quadros, i % 2 == 0),
               "-frames:v", str(quadros), *X264, "-crf", "16", str(parte))
        partes.append(parte)
    cartao_final(tmp / "final.jpg")
    quadros_fim = round(BATIDAS_FIM * BATIDA * FPS)
    parte = tmp / "cena_final.mp4"
    ffmpeg("-loop", "1", "-i", str(tmp / "final.jpg"),
           "-vf", f"zoompan=z='1+0.04*on/{quadros_fim}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                  f":d=1:s={W}x{H}:fps={FPS},fade=t=in:st=0:d=0.25:color=white",
           "-frames:v", str(quadros_fim), *X264, "-crf", "16", str(parte))
    partes.append(parte)
    lista = tmp / "lista.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in partes))
    corpo = tmp / "corpo.mp4"
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(corpo))

    # 3) textos animados por cima + trilha
    total = duracao(str(corpo))
    inicio_fim = sum(b for _, b, _ in CENAS) * BATIDA
    musica_wav = tmp / "musica.wav"
    musica.gerar(str(musica_wav))

    camada(tmp / "topo.png", camada_topo)
    camada(tmp / "gancho.png", camada_gancho)
    textos = [(tmp / "topo.png", 0.0, inicio_fim, 0), (tmp / "gancho.png", 0.15, 5 * BATIDA - 0.05, 36)]
    t = 0.0
    for ini, batidas, legenda in CENAS:  # cenas seguidas com a mesma legenda viram um texto só
        fim = t + batidas * BATIDA
        if legenda:
            if textos[-1][0].stem == legenda:
                textos[-1] = (textos[-1][0], textos[-1][1], fim - 0.05, 36)
            else:
                png = tmp / f"{legenda}.png"
                camada(png, camada_legenda(legenda))
                textos.append((png, t + 0.1, fim - 0.05, 36))
        t = fim

    entradas = ["-i", str(corpo)]
    filtro, ult = "", "0:v"
    for k, (png, ini, fim, deslize) in enumerate(textos, start=1):
        entradas += ["-loop", "1", "-t", f"{total:.3f}", "-i", str(png)]
        prep, sobre = anima(k, ini, fim, deslize)
        filtro += f"{prep}[{ult}][o{k}]{sobre}[v{k}];"
        ult = f"v{k}"
    entradas += ["-i", str(musica_wav)]
    filtro += (f"[{len(textos) + 1}:a]atrim=0:{total:.3f},afade=t=out:st={total - 1.2:.3f}:d=1.2,"
               "loudnorm=I=-14:TP=-1.5[a]")
    ffmpeg(*entradas, "-filter_complex", filtro, "-map", f"[{ult}]", "-map", "[a]",
           *X264, "-crf", "21", "-profile:v", "high",
           "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", "-t", f"{total:.3f}",
           str(SAIDA))

    # 4) capa
    quadro = tmp / "quadro.jpg"
    ffmpeg("-ss", str(QUADRO_CAPA), "-i", str(base), "-frames:v", "1", str(quadro))
    capa(quadro, CAPA)
    print(f"{SAIDA} ({duracao(str(SAIDA)):.1f}s) e {CAPA}")


if __name__ == "__main__":
    main(sys.argv[1])
