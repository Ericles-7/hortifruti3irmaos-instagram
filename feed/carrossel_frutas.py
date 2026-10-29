"""Carrossel "Não sei qual fruta comprar... O Hortifruti 3 Irmãos te ajuda!" (1080x1350).

Capa com a pergunta + uma lâmina por fruta (foto real, logo no topo, nome grande e o benefício
numa caixa verde) + lâmina final com o Zap.
Uso: python3 feed/carrossel_frutas.py   -> feed/saida/frutas-<n>.jpg
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageOps

from post_foto import BRANCO, ESCURO, H, LOGO, RAIZ, W, emblema, fonte, texto_quebrado

PASTA = Path(__file__).parent
FOTOS = RAIZ / "reels" / "fotos"
VERDE = (28, 94, 32)
VERDE_VIVO = (46, 160, 60)
LARANJA = (255, 106, 0)

CAPA = ("manga-colorida.jpg", "“Não sei qual\nfruta comprar...”", "O Hortifruti 3 Irmãos te ajuda!")
# (foto, nome, benefício)
FRUTAS = [
    ("manga-colorida.jpg", "MANGA",
     "Fonte de vitaminas A e C e de fibras, que ajudam no bom funcionamento do intestino."),
    ("melancia-3.jpg", "MELANCIA",
     "Tem muita água: ótima pra hidratar nos dias quentes. Ainda traz vitaminas A e C."),
    ("manga-coite.jpg", "MANGA COITÉ",
     "Verdinha e firme, perfeita pra suco, salada e aquele lanche com sal."),
]
FINAL = ("melancia-1.jpg", "Escolheu a sua?", "Passe na loja ou peça pelo Zap\n(83) 99937-8165")


def fundo(foto, escurecer=60):
    img = Image.open(FOTOS / foto).convert("RGB")
    img = ImageOps.fit(img, (W, H), Image.LANCZOS)
    img = ImageEnhance.Color(img).enhance(1.15).convert("RGBA")
    img.alpha_composite(Image.new("RGBA", (W, H), ESCURO + (escurecer,)))
    return img


def logo_topo(img):
    logo = Image.open(LOGO).convert("RGBA")
    logo = logo.resize((380, round(logo.height * 380 / logo.width)), Image.LANCZOS)
    pad = 18
    card = Image.new("RGBA", (logo.width + 2 * pad, logo.height + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=40,
                                           fill=VERDE + (255,))
    card.alpha_composite(logo, (pad, pad))
    img.alpha_composite(card, ((W - card.width) // 2, 70))


def texto_contorno(d, xy, txt, f, cor, borda=6, contorno=BRANCO, **kw):
    d.text(xy, txt, font=f, fill=cor, stroke_width=borda, stroke_fill=contorno, **kw)


def caixa(d, x, y, linhas, f, cor_fundo, largura_max):
    """Caixa arredondada atrás de cada linha, como marca-texto."""
    for linha in linhas:
        l, t, r, b = d.textbbox((0, 0), linha, font=f)
        d.rounded_rectangle((x - 18, y - 10, x + r - l + 18, y + b - t + 16), radius=16, fill=cor_fundo)
        y += b - t + 22
    return y


def escrever_caixa(d, x, y, txt, f, largura):
    linhas = texto_quebrado(d, txt, f, largura)
    yy = caixa(d, x, y, linhas, f, VERDE_VIVO, largura)
    for linha in linhas:
        l, t, r, b = d.textbbox((0, 0), linha, font=f)
        d.text((x - l, y - t), linha, font=f, fill=BRANCO)
        y += b - t + 22
    return yy


def capa():
    foto, pergunta, resposta = CAPA
    img = fundo(foto, 110)
    logo_topo(img)
    d = ImageDraw.Draw(img)
    f = fonte(92, "ExtraBold")
    d.multiline_text((W / 2, 640), pergunta, font=f, fill=BRANCO, anchor="mm", align="center", spacing=10)
    fr = fonte(54, "ExtraBold")
    l, t, r, b = d.textbbox((0, 0), resposta, font=fr)
    w, h = r - l + 50, b - t + 34
    x, y = (W - w) / 2, 900
    d.rectangle((x, y, x + w, y + h), fill=LARANJA)
    d.text((x + 25 - l, y + 17 - t), resposta, font=fr, fill=BRANCO)
    img.alpha_composite(emblema(110), ((W - 110) // 2, H - 170))
    return img.convert("RGB")


def lamina(foto, nome, beneficio):
    img = fundo(foto, 40)
    logo_topo(img)
    d = ImageDraw.Draw(img)
    x = 90
    fn = fonte(104 if len(nome) < 10 else 88, "Black")
    texto_contorno(d, (x, 330), nome, fn, LARANJA, borda=7)
    escrever_caixa(d, x + 12, 470, beneficio, fonte(42, "SemiBold"), W - 2 * x - 40)
    img.alpha_composite(emblema(110), (W - 160, H - 170))
    return img.convert("RGB")


def final():
    foto, titulo, texto = FINAL
    img = fundo(foto, 120)
    logo_topo(img)
    d = ImageDraw.Draw(img)
    texto_contorno(d, (W / 2, 620), titulo, fonte(96, "Black"), LARANJA, borda=7, anchor="mm")
    d.multiline_text((W / 2, 800), texto, font=fonte(52, "Bold"), fill=BRANCO, anchor="mm", align="center",
                     spacing=14)
    fb = fonte(40, "Bold")
    end = "Rua Francisco Euclides Fernandes, 1200 · Uiraúna"
    d.text((W / 2, 960), end, font=fb, fill=BRANCO, anchor="mm")
    img.alpha_composite(emblema(120), ((W - 120) // 2, H - 190))
    return img.convert("RGB")


def main():
    saida = PASTA / "saida"
    saida.mkdir(exist_ok=True)
    laminas = [capa()] + [lamina(*f) for f in FRUTAS] + [final()]
    for n, img in enumerate(laminas, 1):
        img.save(saida / f"frutas-{n}.jpg", quality=93)
    print(f"{len(laminas)} lâminas em {saida}")


if __name__ == "__main__":
    main()
