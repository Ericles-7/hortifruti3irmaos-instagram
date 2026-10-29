"""Posts do feed com foto real de fundo (1080x1350), no estilo "Frescor que você vê":
foto escurecida, título branco + verde, faixa laranja, texto, botão branco e o emblema do hortifruti.

Uso: python3 feed/post_foto.py <post>
Grava feed/saida/<post>-<n>.jpg a partir de POSTS abaixo.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

PASTA = Path(__file__).parent
RAIZ = PASTA.parent
MONTSERRAT = RAIZ / "reels" / "fonts" / "Montserrat.ttf"
LOGO = RAIZ / "reels" / "logo.png"

W, H = 1080, 1350
BRANCO = (255, 255, 255)
VERDE = (92, 222, 104)
LARANJA = (247, 168, 72)
ESCURO = (22, 26, 20)

# post: lâminas (foto, título branco, título verde, faixa laranja, texto, botão)
POSTS = {
    "q01-quinta-chegou-foto": [
        ("fotos/corredor.jpg", "Quintou!", "Chegou verdura", "nova no Hortifruti 3 Irmãos.",
         "Folhas, legumes e frutas renovados toda quinta pra deixar a sua mesa mais fresquinha.",
         "Arrasta pro lado →"),
        ("fotos/tomate.jpg", "Toda quinta", "a banca renova", "Quanto mais cedo, mais escolha.",
         "Tomate, cebola, folhas e legumes escolhidos a dedo, um por um, pra você.",
         "Passe na loja e aproveite! ↓"),
        ("fotos/cebola.jpg", "Peça pelo", "Zap", "(83) 99937-8165",
         "A gente separa as mais bonitas e leva até você.\nRua Francisco Euclides Fernandes, 1200 · Uiraúna",
         "Chama no Zap! ↓"),
    ],
    # fotos tiradas dos vídeos da mãe de 29/10 (bancas cheias)
    "q02-quinta-chegou": [
        ("fotos/q-cheiro-verde.jpg", "Quintou!", "Chegou mercadoria", "nova no Hortifruti 3 Irmãos.",
         "Verdura, fruta e tempero fresquinhos, prontos pra sua mesa.",
         "Arrasta pro lado →"),
        ("fotos/q-verduras.jpg", "Cheiro-verde", "e alface", "Molhos fresquinhos.",
         "Coentro e cebolinha no saquinho, do jeito que a sua cozinha pede.",
         "Arrasta pro lado →"),
        ("fotos/q-mamao.jpg", "Mamão", "no ponto", "Maduro e de vez.",
         "Pra comer hoje ou deixar amadurecer em casa.",
         "Arrasta pro lado →"),
        ("fotos/q-melancia-cortada.jpg", "Melancia", "vermelhinha", "Docinha e suculenta.",
         "Muita água pra hidratar nos dias quentes.",
         "Arrasta pro lado →"),
        ("fotos/q-tangerina.jpg", "Tangerina", "docinha", "Fresquinha da semana.",
         "Boa pro suco, pra sobremesa e pro lanche da criançada.",
         "Arrasta pro lado →"),
        ("fotos/q-cebola.jpg", "Cebola", "e cebola roxa", "Banca abastecida pra semana.",
         "Aquele tempero de todo dia, que não pode faltar na cozinha.",
         "Arrasta pro lado →"),
        ("fotos/q-alho.jpg", "Alho", "premium", "Graúdo e cheiroso.",
         "Caixa nova chegando pra deixar a sua comida mais gostosa.",
         "Arrasta pro lado →", 9),
        ("fotos/q-melancia-pilha.jpg", "Peça pelo", "Zap", "(83) 99937-8165",
         "A gente separa as mais bonitas e leva até você.\nRua Francisco Euclides Fernandes, 1200 · Uiraúna",
         "Chama no Zap! ↓"),
    ],
}


def fonte(tamanho, peso="ExtraBold"):
    f = ImageFont.truetype(str(MONTSERRAT), tamanho)
    f.set_variation_by_name(peso)
    return f


def fundo(foto, desfoque=0):
    img = Image.open(PASTA / foto).convert("RGB")
    img = ImageOps.fit(img, (W, H), Image.LANCZOS, centering=(0.6, 0.5))
    if desfoque:  # para fotos com letreiro que briga com o título
        img = img.filter(ImageFilter.GaussianBlur(desfoque))
    img = ImageEnhance.Color(img).enhance(1.25)
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=60))
    img = img.convert("RGBA")
    # escurece da esquerda para a direita (o texto fica à esquerda) e um pouco embaixo
    sombra = Image.new("L", (W, H))
    d = ImageDraw.Draw(sombra)
    for x in range(W):
        d.line([(x, 0), (x, H)], fill=int(215 * max(0.0, 1 - x / (W * 0.85)) + 40))
    escuro = Image.new("RGBA", (W, H), ESCURO + (255,))
    escuro.putalpha(sombra)
    img.alpha_composite(escuro)
    return img


def emblema(diametro):
    """O círculo do carrinho, tirado do logo."""
    logo = Image.open(LOGO).convert("RGBA")
    lado = logo.height
    ic = logo.crop((0, 0, lado, lado))
    mascara = Image.new("L", (lado, lado), 0)
    ImageDraw.Draw(mascara).ellipse((14, 14, lado - 14, lado - 14), fill=255)
    out = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    out.paste(ic, (0, 0), mascara)
    return out.resize((diametro, diametro), Image.LANCZOS)


def texto_quebrado(d, txt, f, largura):
    linhas = []
    for paragrafo in txt.split("\n"):
        atual = ""
        for p in paragrafo.split():
            teste = f"{atual} {p}".strip()
            if d.textlength(teste, font=f) <= largura or not atual:
                atual = teste
            else:
                linhas.append(atual)
                atual = p
        linhas.append(atual)
    return linhas


def caber(d, txt, peso, tamanho, largura):
    while d.textlength(txt, font=fonte(tamanho, peso)) > largura and tamanho > 30:
        tamanho -= 4
    return fonte(tamanho, peso)


def lamina(foto, branco, verde, faixa, texto, botao, desfoque=0):
    img = fundo(foto, desfoque)
    d = ImageDraw.Draw(img)
    x, larg = 70, 760

    f1 = caber(d, branco, "ExtraBold", 132, larg)
    f2 = caber(d, verde, "Black", 132, larg + 60)
    y = 300
    d.text((x, y), branco, font=f1, fill=BRANCO)
    y += f1.size * 1.12
    d.text((x, y), verde, font=f2, fill=VERDE)
    y += f2.size * 1.32

    ff = caber(d, faixa, "SemiBold", 48, larg)
    l, t, r, b = d.textbbox((0, 0), faixa, font=ff)
    d.rectangle((x - 6, y, x + r - l + 36, y + b - t + 30), fill=LARANJA)
    d.text((x + 15 - l, y + 15 - t), faixa, font=ff, fill=ESCURO)
    y += b - t + 30 + 70

    fc = fonte(40, "Medium")
    for linha in texto_quebrado(d, texto, fc, larg - 60):
        d.text((x, y), linha, font=fc, fill=BRANCO)
        y += 48
    y += 50

    fb = fonte(36, "SemiBold")
    l, t, r, b = d.textbbox((0, 0), botao, font=fb)
    d.rounded_rectangle((x, y, x + r - l + 52, y + b - t + 40), radius=12, fill=BRANCO + (240,))
    d.text((x + 26 - l, y + 20 - t), botao, font=fb, fill=ESCURO)

    img.alpha_composite(emblema(130), (x, H - 210))
    return img.convert("RGB")


def main(post):
    saida = PASTA / "saida"
    saida.mkdir(exist_ok=True)
    for n, partes in enumerate(POSTS[post], 1):
        caminho = saida / f"{post}-{n}.jpg"
        lamina(*partes).save(caminho, quality=93)
        print(caminho)


if __name__ == "__main__":
    main(sys.argv[1])
