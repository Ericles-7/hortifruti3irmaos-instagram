"""Story de produto (1080x1920): foto em destaque com o texto no estilo dos reels.

Uso: python3 reels/story_produto.py <nome>
Gera reels/story-<nome>.jpg a partir de STORIES abaixo.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from editar_reel import (AMARELO, BRANCO, H, INSTAGRAM, VERDE, VERDE_CLARO, VERDE_ESCURO, W, colar_centro,
                         fonte, fundo_gradiente, logo_inteiro, texto_destaque)

PASTA = Path(__file__).parent

# nome: (foto em reels/fotos, etiqueta, título, subtítulo)
STORIES = {
    "melancia": ("fotos/melancia-3.jpg", "CORTADA NA HORA", "Melancia docinha!", "vermelhinha e suculenta"),
}


def foto_em_cartao(caminho, largura):
    foto = Image.open(PASTA / caminho).convert("RGB")
    altura = round(largura * foto.height / foto.width)
    foto = foto.resize((largura, altura), Image.LANCZOS)
    borda = 14
    cartao = Image.new("RGBA", (largura + 2 * borda + 60, altura + 2 * borda + 60), (0, 0, 0, 0))
    base = Image.new("RGBA", cartao.size, (0, 0, 0, 0))
    ImageDraw.Draw(base).rounded_rectangle((30, 30, cartao.width - 30, cartao.height - 30), radius=44,
                                           fill=BRANCO + (255,))
    cartao.alpha_composite(Image.eval(base.filter(ImageFilter.GaussianBlur(18)), lambda v: v // 2))
    cartao.alpha_composite(base)
    mascara = Image.new("L", foto.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, foto.width, foto.height), radius=34, fill=255)
    cartao.paste(foto, (30 + borda, 30 + borda), mascara)
    return cartao


def pilula(d, cy, txt, f, fundo, cor):
    l, t, r, b = d.textbbox((0, 0), txt, font=f)
    w, h = r - l + 96, b - t + 52
    x, y = (W - w) / 2, cy - h / 2
    d.rounded_rectangle((x, y, x + w, y + h), radius=h / 2, fill=fundo)
    d.text((x + 48 - l, y + 26 - t), txt, font=f, fill=cor)


def gerar(nome):
    foto, etiqueta, titulo, subtitulo = STORIES[nome]
    img = fundo_gradiente((40, 120, 40), VERDE_ESCURO)
    d = ImageDraw.Draw(img)

    logo = logo_inteiro()
    logo = logo.resize((420, round(logo.height * 420 / logo.width)), Image.LANCZOS)
    x = (W - logo.width) // 2
    d.rounded_rectangle((x - 24, 96, x + logo.width + 24, 120 + logo.height + 12), radius=36, fill=VERDE)
    img.alpha_composite(logo, (x, 110))

    pilula(d, 390, etiqueta, fonte(42), VERDE_CLARO, VERDE_ESCURO)
    colar_centro(img, foto_em_cartao(foto, 940), W / 2, 860)
    colar_centro(img, texto_destaque(titulo, 96), W / 2, 1340)
    fs = fonte(52, "ExtraBold")
    d.text(((W - d.textlength(subtitulo, font=fs)) / 2, 1430), subtitulo, font=fs, fill=BRANCO)

    pilula(d, 1640, "Peça pelo Zap  (83) 99937-8165", fonte(50), AMARELO, VERDE_ESCURO)
    fp = fonte(34, "Bold")
    d.text(((W - d.textlength(INSTAGRAM, font=fp)) / 2, 1760), INSTAGRAM, font=fp, fill=(255, 255, 255, 200))

    saida = PASTA / f"story-{nome}.jpg"
    img.convert("RGB").save(saida, quality=92)
    print(saida)


if __name__ == "__main__":
    gerar(sys.argv[1])
