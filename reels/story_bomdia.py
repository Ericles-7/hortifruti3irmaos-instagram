"""Stories de bom dia (1080x1920) em formatos diferentes, com fotos reais da loja:
capa de jornal, previsão do tempo, polaroids, nota de compra e tipografia gigante.

Uso: python3 reels/story_bomdia.py [nome ...]   (sem nome, gera todos)
Grava stories/fotos/<nome>.jpg. As fotos vêm de reels/fotos (mídias de 30/10).
"""
import math
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from editar_reel import AMARELO, BRANCO, INSTAGRAM, LARANJA, VERDE, VERDE_ESCURO, W, H, fonte, icone_logo

RAIZ = Path(__file__).parent.parent
FOTOS = RAIZ / "reels" / "fotos"
SAIDA = RAIZ / "stories" / "fotos"
SERIFA = RAIZ / "reels" / "fonts" / "DMSerifDisplay.ttf"
MONTSERRAT = RAIZ / "reels" / "fonts" / "Montserrat.ttf"
PAPEL = (250, 246, 236)
TINTA = (28, 30, 26)
ZAP = "(83) 99937-8165"


def serifa(t):
    return ImageFont.truetype(str(SERIFA), t)


def mont(t, peso="ExtraBold"):
    f = ImageFont.truetype(str(MONTSERRAT), t)
    f.set_variation_by_name(peso)
    return f


def foto(nome, w, h, centro=(0.5, 0.5)):
    img = Image.open(FOTOS / nome).convert("RGB")
    img = ImageOps.fit(img, (w, h), Image.LANCZOS, centering=centro)
    img = ImageEnhance.Color(img).enhance(1.18)
    return ImageEnhance.Contrast(img).enhance(1.05)


def rodape(img, cor=TINTA, y=1795):
    d = ImageDraw.Draw(img)
    d.text((W / 2, y), f"Peça pelo Zap {ZAP}", font=mont(40), fill=cor, anchor="mm")
    d.text((W / 2, y + 58), INSTAGRAM, font=mont(30, "SemiBold"), fill=cor, anchor="mm")


def sombra(base, caixa, raio=0, desfoque=22, alfa=110, desloc=(0, 14)):
    camada = Image.new("RGBA", base.size, (0, 0, 0, 0))
    x0, y0, x1, y1 = caixa
    ImageDraw.Draw(camada).rounded_rectangle((x0 + desloc[0], y0 + desloc[1], x1 + desloc[0], y1 + desloc[1]),
                                             radius=raio, fill=(0, 0, 0, alfa))
    base.alpha_composite(camada.filter(ImageFilter.GaussianBlur(desfoque)))


def jornal():
    """Capa de jornal: 'O Bom Dia', manchete e foto, com a data e o dia da semana."""
    img = Image.new("RGBA", (W, H), PAPEL + (255,))
    d = ImageDraw.Draw(img)
    d.text((W / 2, 150), "O Bom Dia", font=serifa(150), fill=TINTA, anchor="mm")
    d.line((70, 250, W - 70, 250), fill=TINTA, width=4)
    d.text((70, 280), "UIRAÚNA · EDIÇÃO DE HOJE", font=mont(30, "Bold"), fill=TINTA)
    d.text((W - 70, 280), "HORTIFRUTI 3 IRMÃOS", font=mont(30, "Bold"), fill=TINTA, anchor="ra")
    d.line((70, 330, W - 70, 330), fill=TINTA, width=2)
    d.multiline_text((70, 380), "Chegou fruta\nfresquinha na\nbanca!", font=serifa(120), fill=TINTA, spacing=4)
    f = foto("uva-verde.jpg", W - 140, 640)
    img.paste(f, (70, 820))
    d.text((70, 1478), "Uva verde graúda, maçã vermelhinha, melão e mamão no ponto.", font=mont(30, "Medium"),
           fill=(80, 80, 72))
    d.line((70, 1540, W - 70, 1540), fill=TINTA, width=2)
    d.text((70, 1575), "Leia mais na loja ou peça a sua", font=serifa(56), fill=TINTA)
    d.text((70, 1645), "edição pelo Zap.", font=serifa(56), fill=VERDE)
    img.alpha_composite(icone_logo(150), (W - 220, 1560))
    rodape(img)
    return img


def previsao():
    """Previsão do tempo: '100% de chance de fruta fresca'."""
    topo, baixo = (255, 196, 92), (255, 128, 64)
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(topo, baixo)) + (255,))
    # sol
    cx, cy, r = W / 2, 430, 150
    for k in range(12):
        a = k * math.pi / 6
        d.line((cx + math.cos(a) * (r + 30), cy + math.sin(a) * (r + 30), cx + math.cos(a) * (r + 95),
                cy + math.sin(a) * (r + 95)), fill=(255, 241, 170), width=18)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 236, 140))
    d.text((W / 2, 150), "BOM DIA, UIRAÚNA!", font=mont(54), fill=BRANCO, anchor="mm")
    d.text((W / 2, 720), "Previsão de hoje", font=mont(48, "SemiBold"), fill=BRANCO, anchor="mm")
    d.text((W / 2, 860), "100%", font=mont(230, "Black"), fill=BRANCO, anchor="mm")
    d.text((W / 2, 1010), "de chance de fruta fresca", font=mont(56), fill=BRANCO, anchor="mm")
    # cartão com 3 "dias" = 3 frutas
    cartao = (70, 1100, W - 70, 1640)
    sombra(img, cartao, 40)
    d.rounded_rectangle(cartao, radius=40, fill=(255, 255, 255, 235))
    itens = [("maca-2.jpg", "Maçã", "crocante"), ("uva-roxa-mao-quadro.jpg", "Uva", "docinha"),
             ("melao-quadro.jpg", "Melão", "geladinho")]
    lado = 260
    for i, (arq, nome, clima) in enumerate(itens):
        x = 100 + i * 300
        f = foto(arq, lado, lado)
        mascara = Image.new("L", (lado, lado), 0)
        ImageDraw.Draw(mascara).ellipse((0, 0, lado, lado), fill=255)
        img.paste(f, (x, 1140), mascara)
        d.text((x + lado / 2, 1450), nome, font=mont(46), fill=TINTA, anchor="mm")
        d.text((x + lado / 2, 1510), clima, font=mont(34, "SemiBold"), fill=LARANJA, anchor="mm")
    d.text((W / 2, 1590), "Hortifruti 3 Irmãos", font=mont(30, "Bold"), fill=VERDE, anchor="mm")
    rodape(img, BRANCO)
    return img


def polaroids():
    """Três polaroids tortinhas presas na parede verde, com legenda escrita à mão."""
    img = Image.new("RGBA", (W, H), (34, 92, 52, 255))
    d = ImageDraw.Draw(img)
    for y in range(0, H, 6):  # textura de parede
        d.line((0, y, W, y), fill=(38, 98, 56, 255), width=2)
    d.text((W / 2, 170), "Bom dia!", font=serifa(170), fill=(255, 241, 196), anchor="mm")
    d.text((W / 2, 300), "As fotos de hoje aqui na loja", font=mont(40, "SemiBold"), fill=BRANCO, anchor="mm")
    fotos = [("maca-1.jpg", "maçã", -6, (60, 400)), ("uva-verde.jpg", "uva verde", 5, (550, 460)),
             ("pimentao.jpg", "pimentão", -3, (290, 1075))]
    for arq, legenda, ang, (x, y) in fotos:
        lado = 390
        quadro = Image.new("RGBA", (lado + 60, lado + 170), (255, 255, 255, 255))
        quadro.paste(foto(arq, lado, lado), (30, 30))
        ImageDraw.Draw(quadro).text(((lado + 60) / 2, lado + 100), legenda, font=serifa(64), fill=TINTA,
                                    anchor="mm")
        quadro = quadro.rotate(ang, expand=True, resample=Image.BICUBIC)
        camada = Image.new("RGBA", img.size, (0, 0, 0, 0))
        camada.alpha_composite(quadro, (x, y))
        sombra_q = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sombra_q.paste((0, 0, 0, 120), (x + 10, y + 20), quadro.getchannel("A"))
        img.alpha_composite(sombra_q.filter(ImageFilter.GaussianBlur(18)))
        img.alpha_composite(camada)
        # durex
        fita = Image.new("RGBA", (170, 54), (255, 250, 220, 170)).rotate(ang + 3, expand=True)
        img.alpha_composite(fita, (x + quadro.width // 2 - 85, y - 18))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, 1690, W - 70, 1890), radius=36, fill=AMARELO + (255,))
    d.text((W / 2, 1755), f"Peça pelo Zap {ZAP}", font=mont(44), fill=VERDE_ESCURO, anchor="mm")
    d.text((W / 2, 1825), INSTAGRAM, font=mont(30, "SemiBold"), fill=VERDE_ESCURO, anchor="mm")
    return img


def nota():
    """Nota de compra: 'Pedido do bom dia', com o total 'muita saúde'."""
    img = Image.new("RGBA", (W, H), (236, 242, 230, 255))
    img.paste(foto("mamao-2-quadro.jpg", W, H).filter(ImageFilter.GaussianBlur(14)), (0, 0))
    img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 70)))
    x0, x1, y0, y1 = 150, W - 150, 170, 1650
    sombra(img, (x0, y0, x1, y1), 0, 26, 140)
    papel = Image.new("RGBA", (x1 - x0, y1 - y0), (255, 254, 248, 255))
    dp = ImageDraw.Draw(papel)
    # serrilhado embaixo
    for x in range(0, papel.width, 40):
        dp.polygon([(x, papel.height), (x + 20, papel.height - 22), (x + 40, papel.height)], fill=(0, 0, 0, 0))
    img.alpha_composite(papel, (x0, y0))
    d = ImageDraw.Draw(img)
    cx = W / 2
    img.alpha_composite(icone_logo(130), (int(cx - 65), y0 + 40))
    d.text((cx, y0 + 230), "HORTIFRUTI 3 IRMÃOS", font=mont(40, "Black"), fill=TINTA, anchor="mm")
    d.text((cx, y0 + 285), "Uiraúna - PB", font=mont(30, "Medium"), fill=(110, 110, 100), anchor="mm")
    d.text((cx, y0 + 380), "PEDIDO DO BOM DIA", font=mont(48), fill=VERDE, anchor="mm")
    tracejado = lambda y: [d.line((x, y, x + 18, y), fill=(160, 160, 150), width=3) for x in range(x0 + 50, x1 - 50, 30)]
    tracejado(y0 + 440)
    itens = [("1x", "Café com mamão"), ("1x", "Maçã na lancheira"), ("1x", "Uva pra sobremesa"),
             ("1x", "Melão geladinho"), ("1x", "Sorriso no rosto")]
    fi = mont(44, "SemiBold")
    for i, (q, item) in enumerate(itens):
        y = y0 + 520 + i * 95
        d.text((x0 + 60, y), q, font=fi, fill=TINTA)
        d.text((x0 + 150, y), item, font=fi, fill=TINTA)
        d.text((x1 - 60, y), "ok", font=fi, fill=VERDE, anchor="ra")
    tracejado(y0 + 1010)
    d.text((x0 + 60, y0 + 1060), "TOTAL", font=mont(56, "Black"), fill=TINTA)
    d.text((x1 - 60, y0 + 1060), "muita saúde", font=mont(56, "Black"), fill=LARANJA, anchor="ra")
    tracejado(y0 + 1160)
    d.text((cx, y0 + 1230), "Bom dia e volte sempre!", font=serifa(70), fill=TINTA, anchor="mm")
    d.text((cx, y0 + 1320), "Seu pedido também chega pelo Zap", font=mont(34, "Medium"), fill=(110, 110, 100),
           anchor="mm")
    rodape(img, BRANCO)
    return img


def gigante():
    """Tipografia gigante: 'BOM DIA' vazado mostrando a foto por dentro das letras."""
    fundo = foto("repolho-2-quadro.jpg", W, H)
    img = Image.new("RGBA", (W, H), (250, 246, 236, 255))
    mascara = Image.new("L", (W, H), 0)
    dm = ImageDraw.Draw(mascara)
    f = mont(330, "Black")
    dm.text((W / 2, 520), "BOM", font=f, fill=255, anchor="mm")
    dm.text((W / 2, 860), "DIA", font=f, fill=255, anchor="mm")
    img.paste(fundo, (0, 0), mascara)
    d = ImageDraw.Draw(img)
    d.text((W / 2, 200), "HORTIFRUTI 3 IRMÃOS", font=mont(44, "Black"), fill=VERDE, anchor="mm")
    d.text((W / 2, 1110), "a feira mais fresquinha", font=serifa(84), fill=TINTA, anchor="mm")
    d.text((W / 2, 1210), "de Uiraúna já começou", font=serifa(84), fill=TINTA, anchor="mm")
    faixa = foto("maca-2.jpg", W, 360, (0.5, 0.4))
    img.paste(faixa, (0, 1330))
    d.rounded_rectangle((90, 1440, W - 90, 1580), radius=70, fill=LARANJA + (255,))
    d.text((W / 2, 1510), "Passa aqui ou chama no Zap", font=mont(48), fill=BRANCO, anchor="mm")
    rodape(img)
    return img


STORIES = {
    "bom-dia-jornal": jornal,
    "bom-dia-previsao": previsao,
    "bom-dia-polaroid": polaroids,
    "bom-dia-nota": nota,
    "bom-dia-gigante": gigante,
}

if __name__ == "__main__":
    SAIDA.mkdir(parents=True, exist_ok=True)
    for nome in sys.argv[1:] or STORIES:
        STORIES[nome]().convert("RGB").save(SAIDA / f"{nome}.jpg", quality=92)
        print(SAIDA / f"{nome}.jpg")
