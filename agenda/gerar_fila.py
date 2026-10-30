"""Gera agenda/fila.json: as postagens programadas (feed e stories) dia a dia.

Uso: python3 agenda/gerar_fila.py
Rodar de novo reescreve a fila, mas mantém o status das postagens já publicadas.
"""
import json
from datetime import date, timedelta
from pathlib import Path

FILA = Path(__file__).with_name("fila.json")
# As artes ficam no repositório público hortifruti3irmaos-midia (o Instagram baixa de lá).
BASE_URL = "https://raw.githubusercontent.com/Ericles-7/hortifruti3irmaos-midia/main/"

# Vídeos vão pelo jsDelivr (serve como video/mp4, o raw do GitHub não), fixados no commit
# do repositório de mídia que trouxe o vídeo.
BASE_VIDEO = "https://cdn.jsdelivr.net/gh/Ericles-7/hortifruti3irmaos-midia@{commit}/"

INICIO = date(2026, 10, 27)
FIM = date(2026, 11, 25)

HORA_STORY = ["06:53", "11:53", "16:53"]
HORA_FEED = "17:53"
# A partir de 29/10 tudo sai de manhã, quando a loja tem mais movimento (pedido do dono).
MANHA_DESDE = date(2026, 10, 29)
HORA_STORY_MANHA = ["06:53", "08:53", "10:53"]
HORA_FEED_MANHA = "05:57"  # "6h": 3 min antes da hora cheia, quando o agendador costuma atrasar


def horarios(dia):
    if dia >= MANHA_DESDE:
        return HORA_STORY_MANHA, HORA_FEED_MANHA
    return HORA_STORY, HORA_FEED

RODAPE = "📲 (83) 99937-8165 · 📍 Rua Francisco Euclides Fernandes, 1200 — Uiraúna"
TAGS = "#Uiraúna #Hortifruti3Irmãos #FeiraFresca"

# Carrosséis do feed, na ordem de publicação.
FEED = {
    date(2026, 10, 28): ("01-delivery",
        "Feira fresquinha sem sair de casa? Tem sim! 🛒🍎\n"
        "Manda sua lista no Zap, a gente escolhe tudo a dedo e leva até você — ou deixa separado pra você retirar no hortifruti. Arrasta pro lado e veja como é fácil 👉\n"
        "Pague no Pix, cartão ou na entrega.\n"
        f"{RODAPE}\n"
        "Salva e manda pra quem vive dizendo que não tem tempo de ir à feira 😉\n"
        f"#Delivery {TAGS}"),
    date(2026, 10, 29): ("q01-quinta-chegou-foto",  # versão com foto (feed/post_foto.py)
        "QUINTOU! 🥬🥕 Chegou verdura nova no Hortifruti 3 Irmãos!\n"
        "Toda quinta a banca renova: folhas, legumes e reposição de frutas pra você escolher com calma. Arrasta pro lado 👉\n"
        "Quanto mais cedo, mais escolha! Passe aqui ou peça pelo Zap que a gente separa as mais bonitas.\n"
        f"{RODAPE}\n"
        f"#QuintaDaVerdura {TAGS}"),
    date(2026, 10, 31): ("v01-qualidade",
        "Qualidade que você vê de longe 👀🍅\n"
        "Cada caixa é aberta e conferida assim que chega. O que não está bonito não vai pra banca — simples assim. Arrasta e veja o caminho da fruta até você 👉\n"
        "Se não serve pra nossa mesa, não vai pra sua!\n"
        f"{RODAPE}\n"
        f"#Compromisso3Irmãos {TAGS}"),
    # A partir de 02/11: rodízio semanal do PLANEJAMENTO.md (pedido do dono em 30/10).
    # (nome, legenda[, nº de imagens[, status]]); "aguardando" segura até o dono aprovar a prévia.
    date(2026, 11, 5): ("r3-5-jeitos-verduras",
        "Comprou verdura e não sabe o que fazer? 🥦🥕 Separamos 5 ideias rápidas!\n"
        "Couve-flor gratinada, brócolis no alho, vinagrete caprichado, cenoura na salada e pimenta-de-cheiro "
        "no feijão. Arrasta pro lado 👉\n"
        "Tudo isso tem fresquinho aqui no Hortifruti 3 Irmãos: passe aqui ou peça pelo Zap que a gente separa.\n"
        f"{RODAPE}\n"
        "Salva pra fazer no almoço de hoje 😋 Qual você vai testar primeiro?\n"
        f"#ReceitaFácil #Verduras {TAGS}", 7),
    date(2026, 11, 12): ("q03-quinta-chegou",
        "QUINTOU! 🥬🍇 Chegou mercadoria nova no Hortifruti 3 Irmãos!\n"
        "Repolho verde e roxo, pimentão, uva roxa, uva verde, maçã e melão fresquinhos pra sua semana. Arrasta pro lado 👉\n"
        "Passe aqui ou peça pelo Zap que a gente separa as mais bonitas.\n"
        f"{RODAPE}\n"
        "O que não pode faltar na sua feira? Comenta aqui 👇\n"
        f"#QuintaDaVerdura {TAGS}", 8, "aguardando"),
    date(2026, 11, 13): ("r5-sobremesa",
        "Sextou! Já pensou na sobremesa do fim de semana? 🍇🍉\n"
        "Salada de frutas, uva congelada, arroz doce com uva-passa, vitamina de mamão e amendoim torradinho: "
        "5 ideias com o que tem fresquinho aqui no Hortifruti 3 Irmãos. Arrasta pro lado 👉\n"
        "Separa pelo Zap e passa pra pegar! Sábado estamos abertos das 4h às 15h.\n"
        f"{RODAPE}\n"
        "Qual vai ser a sobremesa aí na sua casa? Comenta aqui 👇\n"
        f"#Sextou #Sobremesa {TAGS}", 7, "aguardando"),
}

# Reels e stories em vídeo: {data: [dict(hora, video, commit, ...)]}. Reel leva também capa e legenda.
# O "Tour pela banca" (reels/) foi só um teste e não é publicado.
# "status": "aguardando" segura o post até o dono aprovar (aí vira "pendente" no fila.json).
# Manga coité: aprovada pelo dono em 27/10.
MANGA = "01014f7f1d544ee17e37d548a38b3fd3b92aa9bb"  # commit do hortifruti3irmaos-midia com o vídeo
REELS = {
    date(2026, 10, 28): [dict(
        hora="06:53", video="reels/manga-coite.mp4", capa="reels/manga-coite-capa.jpg", commit=MANGA,
        legenda="CHEGOU MANGA COITÉ! 🥭💚\n"
        "Caixa cheia de manga verdinha e fresquinha aqui no Hortifruti 3 Irmãos. Pra suco, pra sobremesa "
        "ou pra comer na hora: é manga que não acaba!\n"
        "Garanta a sua: passe aqui ou peça pelo Zap que a gente separa as mais bonitas pra você.\n"
        f"{RODAPE}\n"
        "Marca aqui quem ama manga 👇\n"
        f"#MangaCoité #Manga {TAGS}",
    )],
}
# "Como escolher fruta boa": aprovado pelo dono na noite de 29/10, publicado na sexta 30/10 às 6h.
COMO_ESCOLHER = "577ee8b6450dfcc270f102172059a4e18d0b76b4"
REELS[date(2026, 10, 30)] = [dict(
    hora="05:57", video="reels/como-escolher.mp4", capa="reels/como-escolher-capa.jpg", commit=COMO_ESCOLHER,
    legenda="Como escolher fruta boa e não errar mais! 🍉🥭\n"
    "Salva esse vídeo pra lembrar na hora da feira 👇\n"
    "1️⃣ Melancia: dê uns tapinhas, som oco é sinal de madura\n"
    "2️⃣ Mamão: casca amarelando e firme ao apertar\n"
    "3️⃣ Tangerina: pegue a mais pesada, é a mais suculenta\n"
    "4️⃣ Kiwi: apertou e cedeu um pouquinho? Tá no ponto\n"
    "5️⃣ Uva: bagos firmes e bem presos no cacho\n"
    "Ou deixa que a gente escolhe pra você aqui no Hortifruti 3 Irmãos: manda sua lista no Zap!\n"
    f"{RODAPE}\n"
    "Qual dessas dicas você não sabia? Comenta aqui 👇\n"
    f"#ComoEscolher #DicaDaFeira {TAGS}",
)]
# Semana A (02/11): Roteiro 2 na segunda e Roteiro 5 na sexta. Commit do repositório de mídia em MIDIA_02_11.
MIDIA_02_11 = "8b8f227edf360c6bea918493d6da923625761dd0"
REELS[date(2026, 11, 2)] = [dict(
    hora="05:57", video="reels/pov-segunda-fruta.mp4", capa="reels/pov-segunda-fruta-capa.jpg",
    commit=MIDIA_02_11,
    legenda="POV: você chegou cedo na Segunda da Fruta 🍉🥭\n"
    "Toda segunda chega fruta nova aqui no Hortifruti 3 Irmãos: melancia, mamão, tangerina, uva sem semente, "
    "ameixa, kiwi e manga coité fresquinhos.\n"
    "Fruta que chegou hoje é fruta que acaba hoje! Passe aqui ou peça pelo Zap que a gente separa as mais bonitas.\n"
    f"{RODAPE}\n"
    "Qual dessas vai pra sua casa hoje? Comenta aqui 👇\n"
    f"#SegundaDaFruta {TAGS}",
)]
REELS[date(2026, 11, 6)] = [dict(
    hora="05:57", video="reels/lista-fim-de-semana.mp4", capa="reels/lista-fim-de-semana-capa.jpg",
    commit=MIDIA_02_11,
    legenda="Sextou! Já fez a lista do fim de semana? 📝✅\n"
    "Mamão pro café, uva pra sobremesa, alface e cheiro-verde, pimenta-de-cheiro, pimentão pro vinagrete, "
    "melancia pra gelar e doce caseiro: tem tudo aqui no Hortifruti 3 Irmãos.\n"
    "Separa pelo Zap hoje e passa pra pegar! Sábado estamos abertos das 4h às 15h.\n"
    f"{RODAPE}\n"
    "O que não pode faltar na sua lista? Comenta aqui 👇\n"
    f"#Sextou #FimDeSemana {TAGS}",
)]
# Semana B: Roteiro 4 na segunda 09/11 (mídias de 30/10).
MIDIA_09_11 = "5c3781d93c9853cb7c9c371a49c496c0190c3279"
REELS[date(2026, 11, 9)] = [dict(
    hora="05:57", video="reels/como-guardar.mp4", capa="reels/como-guardar-capa.jpg",
    commit=MIDIA_09_11, status="aguardando",
    legenda="Sua fruta estraga rápido? Guarda assim que dura mais! 🍎🥬\n"
    "Salva esse vídeo 👇\n"
    "1️⃣ Repolho: inteiro e sem lavar, num saco na geladeira\n"
    "2️⃣ Maçã: na geladeira, longe das outras frutas\n"
    "3️⃣ Uva: na geladeira e sem lavar; lave só na hora de comer\n"
    "4️⃣ Mamão: fora da geladeira até amadurecer, depois na geladeira\n"
    "5️⃣ Tangerina: em lugar fresco e arejado\n"
    "E quando acabar, a gente leva mais: peça pelo Zap aqui no Hortifruti 3 Irmãos!\n"
    f"{RODAPE}\n"
    "Qual dessas você não sabia? Comenta aqui 👇\n"
    f"#ComoGuardar #DicaDaFeira {TAGS}",
)]
STORIES_VIDEO = {
    date(2026, 10, 28): [dict(hora="06:53", video="reels/manga-coite.mp4", commit=MANGA)],
}

BOM_DIA = ["bom-dia-1", "bom-dia-2", "bom-dia-3"]
DICAS = ["dica-tomate", "dica-banana", "dica-folhas", "dica-manga", "dica-cebola",
         "dica-limao", "dica-abacate", "almoco", "zap-3", "dica-cenoura", "dica-morango",
         "dica-alho", "dica-melancia", "dica-cheiro-verde"]
ZAP = ["zap-1", "zap-2", "zap-4"]  # zap-3 ("faltou fruta pro almoço?") vai com as dicas, ao meio-dia


# A partir de 29/10 os stories usam fotos reais (stories/fotos, gerados por reels/story_produto.py)
# em vez das ilustrações (stories/banco); só entram dicas de produtos que têm foto.
FOTOS_DESDE = date(2026, 10, 29)
DICAS_FOTO = ["dica-manga", "dica-rapadura", "dica-melancia", "zap-3"]


def story_imagem(nome, dia):
    """Versão com foto quando existe (a partir de 28/10, quando o dono pediu); senão a ilustrada."""
    foto = f"stories/fotos/{nome}.jpg"
    if dia >= date(2026, 10, 28) and (Path(__file__).parent.parent / foto).exists():
        return foto
    return f"stories/banco/{nome}.jpg"


# Rodízio semanal (PLANEJAMENTO.md): semana A tem a Segunda da Fruta, semana B a Quinta da Verdura.
RODIZIO_DESDE = date(2026, 11, 2)  # segunda de uma semana A


def semana_a(dia):
    return (dia - RODIZIO_DESDE).days // 7 % 2 == 0


def stories_do_dia(n, dia):
    """Os 3 stories do dia: bom dia, dica e chamada (zap / fim de semana / endereço / família)."""
    zap = ZAP[n % len(ZAP)]
    if dia >= date(2026, 10, 30) and dia.weekday() == 4:  # sexta e sábado do rodízio já nesta semana
        return ["sextou", "sexta-produto", "sexta-zap"]
    if dia >= date(2026, 10, 30) and dia.weekday() == 5:
        return ["sabado-feira", "sabado-doces", zap]
    if dia >= RODIZIO_DESDE:
        if dia.weekday() == 0 and semana_a(dia):
            return ["fruta-chegou", "fruta-video", "fruta-zap"]
        if dia.weekday() == 3 and not semana_a(dia):
            return ["quinta-chegou", "verdura-destaque", zap]
        if dia.weekday() == 4:
            return ["sextou", "sexta-produto", "sexta-zap"]
        if dia.weekday() == 5:
            return ["sabado-feira", "sabado-doces", zap]
    # sábado: endereço (ilustrado) só até ter a foto da fachada
    sabado = "endereco" if dia < FOTOS_DESDE else ZAP[n % len(ZAP)]
    tarde = {4: "fim-de-semana", 5: sabado, 6: f"familia-{n // 7 % 2 + 1}"}.get(
        dia.weekday(), ZAP[n % len(ZAP)])
    dicas = DICAS_FOTO if dia >= FOTOS_DESDE else DICAS
    return [BOM_DIA[n % len(BOM_DIA)], dicas[n % len(dicas)], tarde]


def gerar():
    antigos = {}
    if FILA.exists():
        antigos = {p["id"]: p for p in json.loads(FILA.read_text())["postagens"]}

    postagens = []
    dia, n = INICIO, 0
    while dia <= FIM:
        horas_story, hora_feed = horarios(dia)
        for hora, nome in zip(horas_story, stories_do_dia(n, dia)):
            postagens.append({
                "id": f"{dia}-{hora}-story-{nome}",
                "data": str(dia), "hora": hora, "tipo": "story",
                "imagens": [story_imagem(nome, dia)],
            })
        if dia in FEED:
            nome, legenda, *extra = FEED[dia]
            postagens.append({
                "id": f"{dia}-{hora_feed}-carrossel-{nome}",
                "data": str(dia), "hora": hora_feed, "tipo": "carrossel",
                "imagens": [f"{nome}-{i}.jpg" for i in range(1, (extra[0] if extra else 3) + 1)],
                "legenda": legenda,
                **({"status": extra[1]} if len(extra) > 1 else {}),
            })
        for tipo, extras in (("reel", REELS), ("story", STORIES_VIDEO)):
            for r in extras.get(dia, []):
                postagens.append({
                    "id": f"{dia}-{r['hora']}-{tipo}-{Path(r['video']).stem}",
                    "data": str(dia), "tipo": tipo, **r,
                })
        dia += timedelta(days=1)
        n += 1

    for p in postagens:
        antigo = antigos.get(p["id"], {})
        p["status"] = antigo.get("status", p.get("status", "pendente"))
        if "media_id" in antigo:
            p["media_id"] = antigo["media_id"]

    FILA.write_text(json.dumps({
        "fuso": "America/Fortaleza",
        "base_url": BASE_URL,
        "base_video": BASE_VIDEO,
        "postagens": postagens,
    }, ensure_ascii=False, indent=2) + "\n")
    print(f"{len(postagens)} postagens de {INICIO} a {FIM}")


if __name__ == "__main__":
    gerar()
