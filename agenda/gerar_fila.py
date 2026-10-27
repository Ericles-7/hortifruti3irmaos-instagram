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

INICIO = date(2026, 10, 28)
FIM = date(2026, 11, 25)

HORA_STORY = ["06:53", "11:53", "16:53"]
HORA_FEED = "17:53"

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
    date(2026, 10, 29): ("q01-quinta-chegou",
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
    date(2026, 11, 2): ("s01-segunda-chegou",
        "SEGUNDOU! 🍍🍊 Chegou fruta nova!\n"
        "Toda segunda a fruteira renova: frutas da estação, opções pro lanche e pro suco — tudo escolhido a dedo. Arrasta pro lado 👉\n"
        "Comece a semana com a fruteira cheia: passe no hortifruti ou peça pelo Zap.\n"
        f"{RODAPE}\n"
        "Qual fruta não pode faltar na sua casa? Comenta aqui 👇\n"
        f"#SegundaDaFruta {TAGS}"),
    date(2026, 11, 4): ("02-familia",
        "Uma família cuidando da sua mesa 💚\n"
        "Aqui cada fruta, verdura e legume é escolhido com o mesmo carinho que a gente tem com a nossa própria casa. Frescor todo dia, escolha a dedo e atendimento de família. Arrasta pro lado 👉\n"
        f"{RODAPE}\n"
        "Segue a gente pra receber ofertas e dicas toda semana!\n"
        f"#NegócioDeFamília {TAGS}"),
    date(2026, 11, 5): ("q02-quinta-salada",
        "Salada hoje é lei! 🥗\n"
        "Base verde, muita cor e aquela crocância que faz falta: arrasta e monte a salada perfeita em 3 passos 👉\n"
        "Tudo pra sua salada tá aqui — é só mandar a lista no Zap.\n"
        f"{RODAPE}\n"
        "Salva pra fazer no almoço!\n"
        f"#QuintaDaVerdura {TAGS}"),
    date(2026, 11, 7): ("v02-preco-baixo",
        "Preço baixo DE VERDADE 💸🍉\n"
        "Promoção toda semana, ofertas do dia no Zap e feira completa num lugar só, sem rodar a cidade. Arrasta e veja como sua feira rende mais 👉\n"
        "Sacola cheia, bolso feliz!\n"
        f"{RODAPE}\n"
        f"#PreçoBaixo #Compromisso3Irmãos {TAGS}"),
    date(2026, 11, 9): ("s02-segunda-no-ponto",
        "Abacaxi, melancia e manga no ponto 🍍🍉🥭\n"
        "É Segunda da Fruta! Arrasta e nunca mais erre na escolha 👉\n"
        "Fruta no ponto é aqui: escolha com a gente ou peça pelo Zap.\n"
        f"{RODAPE}\n"
        "Salva e manda pra quem vai à feira!\n"
        f"#SegundaDaFruta {TAGS}"),
    date(2026, 11, 11): ("03-site",
        "Sua feira no celular 📱🛒\n"
        "Escolha os produtos, monte o pedido e pague no Pix, cartão ou na entrega. Retire no hortifruti ou receba em casa, aqui em Uiraúna. Arrasta pro passo a passo 👉\n"
        "O link está na bio do perfil!\n"
        f"{RODAPE}\n"
        f"#FeiraOnline {TAGS}"),
    date(2026, 11, 12): ("q03-quinta-conservar",
        "Verdura nova dura mais assim 🥬\n"
        "É Quinta da Verdura! Arrasta e veja 3 truques de quem é da feira pra couve, cheiro-verde, rúcula e alface ficarem verdinhos por mais tempo 👉\n"
        f"{RODAPE}\n"
        "Salva e manda pra quem vive jogando folha fora!\n"
        f"#QuintaDaVerdura {TAGS}"),
    date(2026, 11, 14): ("v03-compromisso",
        "Aqui você não é só mais um cliente 🤝\n"
        "A gente te chama pelo nome, separa seu pedido do Zap como se fosse pra nossa casa e leva até a sua porta em Uiraúna. Arrasta e veja nosso compromisso 👉\n"
        "Palavra de irmão é palavra dada!\n"
        f"{RODAPE}\n"
        f"#Compromisso3Irmãos {TAGS}"),
    date(2026, 11, 16): ("04-dica-mamao",
        "Você sabe escolher o mamão no ponto? 🧡\n"
        "É Segunda da Fruta e a dica de hoje é do mamão: como escolher e como guardar. Arrasta e aprenda em 3 passos 👉\n"
        f"{RODAPE}\n"
        "Salva esta dica e manda pra quem vai à feira!\n"
        f"#SegundaDaFruta #DicaDaFeira {TAGS}"),
    date(2026, 11, 18): ("05-endereco",
        "Venha nos visitar! 📍\n"
        "No hortifruti, pelo WhatsApp ou pelo site: do jeito que for melhor pra você. Arrasta pro lado 👉\n"
        f"{RODAPE}\n"
        "Marca aqui quem precisa conhecer o Hortifruti 3 Irmãos!\n"
        f"{TAGS}"),
    date(2026, 11, 19): ("q04-quinta-couve",
        "3 jeitos de amar a couve 💚\n"
        "Refogada, na farofa ou no suco verde: arrasta e escolha o seu preferido 👉\n"
        "Couve fresquinha chegou hoje! Chama no Zap e peça a sua.\n"
        f"{RODAPE}\n"
        "Qual é o seu? Comenta aí 👇\n"
        f"#QuintaDaVerdura {TAGS}"),
    date(2026, 11, 21): ("08-vem-pra-feira",
        "3 irmãos, 3 compromissos com você 🍎🍅🥑\n"
        "Qualidade a dedo, preço baixo de verdade e cliente tratado como família. Arrasta e conheça cada um 👉\n"
        "Vem conferir a diferença! Marca quem merece uma feira assim.\n"
        f"{RODAPE}\n"
        f"#Compromisso3Irmãos {TAGS}"),
    date(2026, 11, 23): ("07-dica-banana",
        "Banana passando do ponto rápido demais? 🍌\n"
        "É Segunda da Fruta! Arrasta e aprenda em 3 passos a guardar, amadurecer e aproveitar a banana até o fim 👉\n"
        "Banana boa é aqui: dúzia ou unidade, do jeito que você quiser.\n"
        f"{RODAPE}\n"
        "Salva e manda pra quem vai à feira!\n"
        f"#SegundaDaFruta #DicaDaFeira {TAGS}"),
    date(2026, 11, 25): ("06-dica-folhas",
        "Sua alface murcha rápido na geladeira? 🥬\n"
        "Arrasta e aprenda em 3 passos a manter as folhas verdinhas por mais tempo 👉\n"
        "Folhas fresquinhas toda semana: peça pelo Zap que a gente escolhe pra você.\n"
        f"{RODAPE}\n"
        "Salva e manda pra quem vai à feira!\n"
        f"#DicaDaFeira {TAGS}"),
}

# Reels e stories em vídeo: {data: [dict(hora, video, commit, ...)]}. Reel leva também capa e legenda.
# O "Tour pela banca" (reels/) foi só um teste e não é publicado.
REELS = {}
STORIES_VIDEO = {}

BOM_DIA = ["bom-dia-1", "bom-dia-2", "bom-dia-3"]
DICAS = ["dica-tomate", "dica-banana", "dica-folhas", "dica-manga", "dica-cebola",
         "dica-limao", "dica-abacate", "almoco", "zap-3", "dica-cenoura", "dica-morango",
         "dica-alho", "dica-melancia", "dica-cheiro-verde"]
ZAP = ["zap-1", "zap-2", "zap-4"]  # zap-3 ("faltou fruta pro almoço?") vai com as dicas, ao meio-dia


def stories_do_dia(n, dia):
    """Os 3 stories do dia: bom dia, dica e chamada (zap / fim de semana / endereço / família)."""
    tarde = {4: "fim-de-semana", 5: "endereco", 6: f"familia-{n // 7 % 2 + 1}"}.get(
        dia.weekday(), ZAP[n % len(ZAP)])
    return [BOM_DIA[n % len(BOM_DIA)], DICAS[n % len(DICAS)], tarde]


def gerar():
    antigos = {}
    if FILA.exists():
        antigos = {p["id"]: p for p in json.loads(FILA.read_text())["postagens"]}

    postagens = []
    dia, n = INICIO, 0
    while dia <= FIM:
        for hora, nome in zip(HORA_STORY, stories_do_dia(n, dia)):
            postagens.append({
                "id": f"{dia}-{hora}-story-{nome}",
                "data": str(dia), "hora": hora, "tipo": "story",
                "imagens": [f"stories/banco/{nome}.jpg"],
            })
        if dia in FEED:
            nome, legenda = FEED[dia]
            postagens.append({
                "id": f"{dia}-{HORA_FEED}-carrossel-{nome}",
                "data": str(dia), "hora": HORA_FEED, "tipo": "carrossel",
                "imagens": [f"{nome}-{i}.jpg" for i in (1, 2, 3)],
                "legenda": legenda,
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
        p["status"] = antigo.get("status", "pendente")
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
