"""Stories com foto (1080x1920): foto real em destaque, etiqueta, título no estilo dos reels e o Zap.

Uso: python3 reels/story_produto.py [nome ...]   (sem nome, gera todos)
Grava stories/fotos/<nome>.jpg. As fotos vêm de reels/fotos.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

from editar_reel import (AMARELO, BRANCO, INSTAGRAM, VERDE, VERDE_CLARO, VERDE_ESCURO, W, colar_centro, fonte,
                         fundo_gradiente, logo_inteiro, texto_destaque)

RAIZ = Path(__file__).parent.parent
SAIDA = RAIZ / "stories" / "fotos"
R = "reels/fotos/"

# nome: (foto, etiqueta, título (\n quebra a linha), texto)
STORIES = {
    # Só fotos aprovadas pelo dono (melancia, mangas e rapadura); o resto entra quando ele fotografar.
    # bom dia
    "bom-dia-1": (R + "manga-coite.jpg", "BOM DIA, UIRAÚNA!", "Mercadoria\nfresquinha",
                  "Já estamos separando os pedidos. Manda a sua lista no Zap!"),
    "bom-dia-2": (R + "melancia-2.jpg", "BOM DIA!", "Feira boa\ncomeça cedo",
                  "Frutas, verduras e legumes escolhidos a dedo pra você."),
    "bom-dia-3": (R + "manga-colorida.jpg", "BOM DIA!", "Hoje tem\ncoisa boa",
                  "Vem conferir na loja ou peça sem sair de casa."),
    # dicas
    "dica-manga": (R + "manga-colorida.jpg", "DICA RÁPIDA", "Manga\ndoce e no ponto",
                   "Amadureça fora da geladeira e depois guarde nela."),
    "dica-melancia": (R + "melancia-1.jpg", "DICA RÁPIDA", "Melancia\ncortada",
                      "Cubra bem e guarde na geladeira; consuma em poucos dias."),
    "dica-rapadura": (R + "rapadura-gergelim.jpg", "DICA RÁPIDA", "Rapadura\nsempre boa",
                      "Guarde em pote fechado, longe da umidade, que ela não mela."),
    # meio-dia e tarde
    "zap-1": (R + "rapadura-pilha.jpg", "PEÇA PELO ZAP", "Fez a lista?\nA gente separa!",
              "Mande sua lista e receba em casa ou retire na loja."),
    "zap-2": (R + "melancia-2.jpg", "SEM FILA", "Sua feira\nsem sair de casa",
              "É só chamar no WhatsApp que a gente leva até você."),
    "zap-3": (R + "manga-colorida.jpg", "ESQUECEU ALGO?", "Faltou fruta\npro almoço?",
              "Chama no Zap que a gente resolve rapidinho."),
    "zap-4": (R + "manga-coite.jpg", "ENTREGA EM CASA", "A gente leva\naté você",
              "Frutas, verduras e legumes na sua porta, em Uiraúna."),
    "fim-de-semana": (R + "rapadura-garrafas.jpg", "FIM DE SEMANA", "Já fez a feira\ndo fim de semana?",
                      "Garanta frutas e verduras fresquinhas pro seu sábado."),
    "familia-1": (R + "rapadura-pilha.jpg", "NEGÓCIO DE FAMÍLIA", "Escolhido\ncom carinho",
                  "Cada item passa pelas mãos da nossa família."),
    "familia-2": (R + "melancia-3.jpg", "OBRIGADO!", "Valeu pela\npreferência",
                  "Cada pedido de vocês faz a nossa família crescer."),
    # produtos
    "melancia": (R + "melancia-3.jpg", "CORTADA NA HORA", "Melancia docinha!", "vermelhinha e suculenta"),
}


def foto_em_cartao(caminho, largura, altura):
    foto = ImageOps.fit(Image.open(RAIZ / caminho).convert("RGB"), (largura, altura), Image.LANCZOS)
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


def quebrar(d, txt, f, largura):
    linhas, atual = [], ""
    for palavra in txt.split():
        teste = f"{atual} {palavra}".strip()
        if d.textlength(teste, font=f) <= largura or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    return linhas + [atual]


def gerar(nome):
    foto, etiqueta, titulo, texto = STORIES[nome]
    img = fundo_gradiente((40, 120, 40), VERDE_ESCURO)
    d = ImageDraw.Draw(img)

    logo = logo_inteiro()
    logo = logo.resize((400, round(logo.height * 400 / logo.width)), Image.LANCZOS)
    x = (W - logo.width) // 2
    d.rounded_rectangle((x - 24, 80, x + logo.width + 24, 104 + logo.height + 12), radius=36, fill=VERDE)
    img.alpha_composite(logo, (x, 94))

    pilula(d, 360, etiqueta, fonte(42), VERDE_CLARO, VERDE_ESCURO)
    colar_centro(img, foto_em_cartao(foto, 940, 700), W / 2, 800)

    tit = texto_destaque(titulo, 88)
    if tit.width > W - 40:
        tit = tit.resize((W - 40, round(tit.height * (W - 40) / tit.width)), Image.LANCZOS)
    colar_centro(img, tit, W / 2, 1290)
    fs = fonte(46, "ExtraBold")
    linhas = quebrar(d, texto, fs, W - 140)
    y = 1290 + tit.height / 2 + 10
    for linha in linhas:
        d.text(((W - d.textlength(linha, font=fs)) / 2, y), linha, font=fs, fill=BRANCO)
        y += 60

    pilula(d, 1700, "Peça pelo Zap  (83) 99937-8165", fonte(50), AMARELO, VERDE_ESCURO)
    fp = fonte(34, "Bold")
    d.text(((W - d.textlength(INSTAGRAM, font=fp)) / 2, 1800), INSTAGRAM, font=fp, fill=(255, 255, 255, 200))

    SAIDA.mkdir(parents=True, exist_ok=True)
    saida = SAIDA / f"{nome}.jpg"
    img.convert("RGB").save(saida, quality=92)
    return saida


if __name__ == "__main__":
    for nome in sys.argv[1:] or STORIES:
        print(gerar(nome))
