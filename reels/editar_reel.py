"""Edita o vídeo bruto da banca no reel "Tour pela banca" (1080x1920, com a marca do hortifruti).

Uso: python3 reels/editar_reel.py <video_bruto.mp4> [voz_piper.onnx]
Gera reels/tour-banca.mp4 e reels/tour-banca-capa.jpg. Com a voz (Piper TTS), grava a narração
do roteiro (reels/tour-banca-roteiro.md) por cima do som ambiente.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

PASTA = Path(__file__).parent
FONTE = PASTA / "fonts" / "Nunito.ttf"
LOGO = PASTA / "logo.png"
SAIDA = PASTA / "tour-banca.mp4"
CAPA = PASTA / "tour-banca-capa.jpg"

W, H = 1080, 1920
VERDE = (28, 94, 32)
VERDE_CLARO = (200, 240, 160)
AMARELO = (255, 222, 120)
BRANCO = (255, 255, 255)
FIM = 3.5  # segundos do cartão final

# (início, fim, legenda) sobre o vídeo bruto
LEGENDAS = [
    (0.0, 4.5, "Laranja fresquinha"),
    (4.5, 7.0, "Maracujá e batata"),
    (7.0, 10.0, "Cebola roxa e branca"),
    (10.0, 12.0, "Tomate no ponto"),
    (12.0, 17.5, "Abacaxi e melão"),
    (17.5, 22.5, "Fruta escolhida a dedo"),
    (22.5, 99.0, "Tudo fresquinho pra você"),
]

# (início no reel final, fala) — o mesmo texto de reels/tour-banca-roteiro.md
NARRACAO = [
    (0.3, "Ei, vem ver o que tem hoje no Hortifruti Três Irmãos!"),
    (3.7, "Laranja docinha, maracujá e batata selecionada."),
    (8.3, "Cebola roxa e branca, e tomate no ponto pro seu almoço."),
    (13.5, "Abacaxi e melão cheirosos, do jeitinho que você gosta."),
    (17.8, "Tudo escolhido a dedo, com preço baixo de verdade."),
    (21.4, "Faz sua feira aqui com a gente, ou manda sua lista no Zap, que a gente separa e leva até você!"),
    (28.5, "Hortifruti Três Irmãos: feira fresquinha todo dia!"),
]


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


def camada_topo(caminho):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    logo_card(img, 70, 380)
    img.save(caminho)


def camada_gancho(caminho):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pilula(d, 300, "TOUR PELA BANCA", fonte(44), VERDE_CLARO, VERDE)
    texto_centro(d, 400, "Vem ver o que", fonte(104), BRANCO)
    texto_centro(d, 515, "tem hoje!", fonte(104), AMARELO)
    img.save(caminho)


def camada_legenda(caminho, txt):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pilula(ImageDraw.Draw(img), 1560, txt, fonte(64), VERDE + (235,), BRANCO, pad_x=54, pad_y=26)
    img.save(caminho)


def fundo_verde():
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(28 + 50 * t), int(94 + 80 * t), int(32 + 30 * t), 255))
    return img


def cartao_final(caminho):
    img = fundo_verde()
    y = logo_card(img, 360, 620)
    d = ImageDraw.Draw(img)
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


def narrar(voz, tmp, video):
    """Sintetiza cada fala e mistura por cima do som ambiente (que fica baixinho)."""
    entradas, filtro = ["-i", str(video)], ""
    for i, (ini, fala) in enumerate(NARRACAO):
        wav = tmp / f"fala{i}.wav"
        subprocess.run([sys.executable, "-m", "piper", "-m", voz, "-f", str(wav), "--length-scale", "0.92"],
                       input=fala, text=True, check=True, capture_output=True)
        entradas += ["-i", str(wav)]
        ms = int(ini * 1000)
        filtro += f"[{i + 1}:a]aresample=44100,adelay={ms}|{ms},volume=1.8[f{i}];"
    falas = "".join(f"[f{i}]" for i in range(len(NARRACAO)))
    filtro += (f"{falas}amix=inputs={len(NARRACAO)}:normalize=0[voz];"
               "[0:a]volume=0.3[amb];[amb][voz]amix=inputs=2:duration=first:normalize=0,"
               "loudnorm=I=-14:TP=-1.5[a]")
    ffmpeg(*entradas, "-filter_complex", filtro, "-map", "0:v", "-map", "[a]",
           "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", str(SAIDA))


def main(bruto, voz=None):
    tmp = Path(tempfile.mkdtemp())
    dur = duracao(bruto)

    # 1) estabiliza, corrige a cor e leva para 1080x1920
    trf = tmp / "estab.trf"
    ffmpeg("-i", bruto, "-vf", f"vidstabdetect=shakiness=6:result={trf}", "-f", "null", "-")
    base = tmp / "base.mp4"
    ffmpeg("-i", bruto, "-vf",
           f"vidstabtransform=input={trf}:smoothing=20:zoom=4,"
           f"scale={W}:{H}:flags=lanczos,eq=saturation=1.22:contrast=1.06:brightness=0.02,"
           "unsharp=5:5:0.6,fps=30,format=yuv420p",
           "-af", "highpass=f=80,volume=2.0", "-c:v", "libx264", "-crf", "18", "-preset", "slow",
           "-c:a", "aac", "-b:a", "128k", "-ar", "44100", str(base))

    # 2) camadas de texto
    camada_topo(tmp / "topo.png")
    camada_gancho(tmp / "gancho.png")
    for i, (_, _, txt) in enumerate(LEGENDAS):
        camada_legenda(tmp / f"leg{i}.png", txt)
    cartao_final(tmp / "final.jpg")

    entradas = ["-i", str(base), "-i", str(tmp / "topo.png"), "-i", str(tmp / "gancho.png")]
    filtro = "[0:v][1:v]overlay=0:0[v0];[v0][2:v]overlay=0:0:enable='between(t,0,3.2)'[v1];"
    ult = "v1"
    for i, (ini, fim, _) in enumerate(LEGENDAS):
        entradas += ["-i", str(tmp / f"leg{i}.png")]
        ini = max(ini, 3.2)  # legendas entram depois do gancho
        if ini >= fim:
            continue
        filtro += f"[{ult}][{i + 3}:v]overlay=0:0:enable='between(t,{ini},{min(fim, dur)})'[l{i}];"
        ult = f"l{i}"

    # 3) cartão final com transição, áudio sai em fade
    n = len(LEGENDAS) + 3
    entradas += ["-loop", "1", "-t", str(FIM), "-i", str(tmp / "final.jpg"),
                 "-f", "lavfi", "-t", str(FIM), "-i", "anullsrc=r=44100:cl=stereo"]
    xf = round(dur - 0.6, 2)
    filtro += (f"[{n}:v]fps=30,format=yuv420p,setsar=1,settb=1/30[fim];"
               f"[{ult}]fps=30,setsar=1,settb=1/30[corpo];"
               f"[corpo][fim]xfade=transition=fade:duration=0.6:offset={xf}[v];"
               f"[0:a]afade=t=out:st={dur - 1.5}:d=1.5[a0];"
               f"[a0][{n + 1}:a]acrossfade=d=0.6[a]")
    ffmpeg(*entradas, "-filter_complex", filtro, "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-crf", "23", "-preset", "slow", "-profile:v", "high",
           "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
           "-movflags", "+faststart", str(tmp / "sem_voz.mp4"))
    if voz:
        narrar(voz, tmp, tmp / "sem_voz.mp4")
    else:
        (tmp / "sem_voz.mp4").replace(SAIDA)

    # 4) capa a partir de um quadro colorido (melões)
    quadro = tmp / "quadro.jpg"
    ffmpeg("-ss", "14.5", "-i", str(base), "-frames:v", "1", str(quadro))
    capa(quadro, CAPA)
    print(f"{SAIDA} ({duracao(str(SAIDA)):.1f}s) e {CAPA}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
