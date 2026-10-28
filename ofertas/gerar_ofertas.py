"""Encarte de ofertas em carrossel (1080x1350): capa "Ofertaço" + lâminas com 6 produtos cada.

Uso: python3 ofertas/gerar_ofertas.py [ofertas.json]
Lê os produtos (nome, unidade, preço, foto em ofertas/fotos) e grava ofertas/saida/oferta-<n>.jpg.
"""
import json
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

PASTA = Path(__file__).parent
RAIZ = PASTA.parent
FONTE = RAIZ / "reels" / "fonts" / "Nunito.ttf"
LOGO = RAIZ / "reels" / "logo.png"

W, H = 1080, 1350
VERDE = (28, 94, 32)
VERDE_VIVO = (52, 150, 48)
LARANJA = (243, 112, 33)
AMARELO = (255, 205, 60)
BRANCO = (255, 255, 255)
PAPEL = (241, 241, 237)
CARTAO = (216, 216, 211)
ENDERECO = "Rua Francisco Euclides Fernandes, 1200 · Uiraúna - PB"
ZAP = "Peça pelo Zap (83) 99937-8165"


def fonte(tamanho, peso="Black"):
    f = ImageFont.truetype(str(FONTE), tamanho)
    f.set_variation_by_name(peso)
    return f


def textura(cor, intensidade=10, semente=7):
    """Fundo com granulado leve, como papel (lâminas) ou tecido (capa)."""
    rnd = random.Random(semente)
    pequeno = Image.new("L", (W // 3, H // 3))
    pequeno.putdata([128 + rnd.randint(-intensidade, intensidade) for _ in range(pequeno.width * pequeno.height)])
    ruido = pequeno.resize((W, H), Image.BICUBIC)
    base = Image.new("RGB", (W, H), cor)
    claro = Image.new("RGB", (W, H), tuple(min(255, c + 25) for c in cor))
    escuro = Image.new("RGB", (W, H), tuple(max(0, c - 25) for c in cor))
    base = Image.composite(claro, base, ruido.point(lambda v: max(0, v - 128) * 4))
    base = Image.composite(escuro, base, ruido.point(lambda v: max(0, 128 - v) * 4))
    return base.convert("RGBA")


def cartao_logo(largura, fundo=VERDE):
    logo = Image.open(LOGO).convert("RGBA")
    logo = logo.resize((largura, round(logo.height * largura / logo.width)), Image.LANCZOS)
    pad = largura // 18
    img = Image.new("RGBA", (logo.width + 2 * pad, logo.height + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle((0, 0, img.width, img.height), radius=pad * 2, fill=fundo + (255,))
    img.alpha_composite(logo, (pad, pad))
    return img


def sombra(img, raio=16, deslocamento=(0, 10), forca=90):
    s = Image.new("RGBA", (img.width + 4 * raio, img.height + 4 * raio), (0, 0, 0, 0))
    s.paste((0, 0, 0, forca), (2 * raio + deslocamento[0], 2 * raio + deslocamento[1]), img.getchannel("A"))
    return s.filter(ImageFilter.GaussianBlur(raio)), 2 * raio


def colar(base, img, x, y, com_sombra=True):
    if com_sombra:
        s, m = sombra(img)
        base.alpha_composite(s, (round(x - m), round(y - m)))
    base.alpha_composite(img, (round(x), round(y)))


def pilula(txt, f, fundo, cor, pad=(34, 16)):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), txt, font=f)
    img = Image.new("RGBA", (r - l + 2 * pad[0], b - t + 2 * pad[1]), (0, 0, 0, 0))
    di = ImageDraw.Draw(img)
    di.rounded_rectangle((0, 0, img.width - 1, img.height - 1), radius=img.height // 2.6, fill=fundo + (255,))
    di.text((pad[0] - l, pad[1] - t), txt, font=f, fill=cor)
    return img


def texto_centro(d, cy, txt, f, cor):
    l, t, r, b = d.textbbox((0, 0), txt, font=f)
    d.text(((W - (r - l)) / 2 - l, cy - (b - t) / 2 - t), txt, font=f, fill=cor)


def faixa_inclinada(linhas, angulo=4):
    """As duas pílulas do "Ofertaço" (verde e laranja), levemente inclinadas."""
    a = pilula(linhas[0], fonte(60), VERDE, BRANCO, (40, 18))
    b = pilula(linhas[1], fonte(60), LARANJA, BRANCO, (40, 18))
    img = Image.new("RGBA", (max(a.width, b.width + 70) + 40, a.height + b.height + 20), (0, 0, 0, 0))
    img.alpha_composite(a, (0, 0))
    img.alpha_composite(b, (70, a.height - 6))
    return img.rotate(angulo, resample=Image.BICUBIC, expand=True)


def capa(dados):
    img = textura(VERDE_VIVO, 14, 3)
    d = ImageDraw.Draw(img)
    # cantos laranja
    d.polygon([(W - 260, 0), (W, 0), (W, 170)], fill=LARANJA)
    d.polygon([(0, H - 200), (0, H), (300, H)], fill=LARANJA)
    d.polygon([(0, 0), (150, 0), (0, 110)], fill=AMARELO)

    faixa = faixa_inclinada(dados["faixa"])
    colar(img, faixa, (W - faixa.width) / 2, 120)

    logo = cartao_logo(760)
    colar(img, logo, (W - logo.width) / 2, 390)

    caixa = pilula("ofertas", fonte(190), LARANJA, BRANCO, (60, 6))
    caixa = caixa.rotate(-2, resample=Image.BICUBIC, expand=True)
    colar(img, caixa, (W - caixa.width) / 2, 720)

    texto_centro(d, 1090, f"Ofertas válidas {dados['validade']}", fonte(62, "ExtraBold"), BRANCO)
    texto_centro(d, 1160, "ou enquanto durar o estoque.", fonte(46, "SemiBold"), BRANCO)
    return img.convert("RGB")


def foto_recortada(nome, largura, altura):
    foto = Image.open(PASTA / "fotos" / nome).convert("RGB")
    foto = ImageOps.fit(foto, (largura, altura), Image.LANCZOS, centering=(0.5, 0.5))
    mascara = Image.new("L", foto.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, largura - 1, altura - 1), radius=26, fill=255)
    out = Image.new("RGBA", foto.size, (0, 0, 0, 0))
    out.paste(foto, (0, 0), mascara)
    return out


def caber(txt, peso, tamanho, largura_max):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    while tamanho > 16 and d.textlength(txt, font=fonte(tamanho, peso)) > largura_max:
        tamanho -= 2
    return fonte(tamanho, peso)


def cartao_produto(p, cw, ch):
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, cw - 1, ch - 1), radius=38, fill=CARTAO + (255,))
    foto = foto_recortada(p["foto"], cw - 36, 190)
    img.alpha_composite(foto, (18, 18))

    nome = p["nome"].upper()
    fn = caber(nome, "Black", 30, cw - 44)
    if fn.size < 25 and " " in nome:  # nome comprido: duas linhas
        meio = nome.rfind(" ", 0, len(nome) // 2 + 4)
        for i, linha in enumerate((nome[:meio], nome[meio + 1:])):
            d.text((24, 210 + i * 26), linha, font=caber(linha, "Black", 24, cw - 44), fill=VERDE)
    else:
        d.text((24, 222), nome, font=fn, fill=VERDE)

    # unidade (etiqueta) + "POR R$" à esquerda, preço grande à direita
    fu = fonte(22, "Black")
    l, t, r, b = d.textbbox((0, 0), p["unidade"], font=fu)
    d.rounded_rectangle((24, 272, 24 + r - l + 14, 272 + b - t + 10), radius=6, fill=LARANJA)
    d.text((31 - l, 277 - t), p["unidade"], font=fu, fill=BRANCO)
    fp = fonte(22, "Black")
    d.text((24, 306), "POR", font=fp, fill=LARANJA)
    d.text((24, 330), "R$", font=fp, fill=LARANJA)
    fpreco = caber(p["preco"], "Black", 96, cw - 100)
    l, t, r, b = d.textbbox((0, 0), p["preco"], font=fpreco)
    d.text((86 - l, 352 - b), p["preco"], font=fpreco, fill=LARANJA)
    return img


def lamina(dados, produtos, indice):
    img = textura(PAPEL, 6, 11 + indice)
    d = ImageDraw.Draw(img)

    logo = cartao_logo(330)
    tag = pilula("ofertas", fonte(76), LARANJA, BRANCO, (30, 4))
    total = logo.width + 18 + tag.width
    x0 = (W - total) / 2
    colar(img, logo, x0, 50)
    colar(img, tag, x0 + logo.width + 18, 50 + (logo.height - tag.height) / 2 + 6)
    texto_centro(d, 235, "Ofertas válidas enquanto durar o estoque.", fonte(36, "ExtraBold"), VERDE)

    cw, ch, gap, mx, y0 = 304, 372, 24, 60, 280
    for k, p in enumerate(produtos):
        col, lin = k % 3, k // 3
        cartao = cartao_produto(p, cw, ch)
        colar(img, cartao, mx + col * (cw + gap), y0 + lin * (ch + gap))

    # rodapé: validade + selo, e faixa laranja com endereço e Zap
    d.text((60, 1095), f"Válido de {dados['validade']}", font=fonte(32, "ExtraBold"), fill=VERDE)
    selo = faixa_inclinada(dados["faixa"], 5)
    selo = selo.resize((260, round(selo.height * 260 / selo.width)), Image.LANCZOS)

    d.rectangle((0, H - 190, W, H), fill=LARANJA)
    d.rectangle((0, H - 190, W, H - 182), fill=VERDE)
    texto_centro(d, H - 128, ZAP, fonte(44, "Black"), BRANCO)
    texto_centro(d, H - 62, ENDERECO, fonte(32, "Bold"), BRANCO)
    colar(img, selo, W - selo.width - 40, H - 190 - selo.height * 0.62)
    return img.convert("RGB")


def main(arquivo=PASTA / "ofertas.json"):
    dados = json.loads(Path(arquivo).read_text())
    saida = PASTA / "saida"
    saida.mkdir(exist_ok=True)
    for f in saida.glob("oferta-*.jpg"):
        f.unlink()
    laminas = [capa(dados)]
    prods = dados["produtos"]
    for i in range(0, len(prods), 6):
        laminas.append(lamina(dados, prods[i:i + 6], i // 6))
    for n, img in enumerate(laminas, 1):
        img.save(saida / f"oferta-{n}.jpg", quality=92)
    print(f"{len(laminas)} lâminas em {saida}")


if __name__ == "__main__":
    main(*sys.argv[1:2])
