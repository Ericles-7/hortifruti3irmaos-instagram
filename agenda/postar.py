"""Apoio à publicação automática da fila (agenda/fila.json).

  python3 agenda/postar.py pendentes             # postagens pendentes cujo horário chegou há no máximo 90 min (JSON)
  python3 agenda/postar.py marcar <id> publicado <media_id>
  python3 agenda/postar.py marcar <id> erro "<mensagem>"
  python3 agenda/postar.py restantes             # dias de feed ainda programados
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

FILA = Path(__file__).with_name("fila.json")
ATRASO_MAXIMO = timedelta(minutes=90)  # depois disso o post perde a hora (ex.: "bom dia" à noite) e não sai


def carregar():
    return json.loads(FILA.read_text())


def agora(fila):
    return datetime.now(ZoneInfo(fila["fuso"]))


def pendentes():
    fila = carregar()
    fuso = ZoneInfo(fila["fuso"])
    agora_ = agora(fila)
    saida = []
    for p in fila["postagens"]:
        quando = datetime.fromisoformat(f"{p['data']}T{p['hora']}").replace(tzinfo=fuso)
        if p["status"] == "pendente" and quando <= agora_ <= quando + ATRASO_MAXIMO:
            if "video" in p:
                item = {**p, "video_url": fila["base_video"].format(commit=p["commit"]) + p["video"]}
                if "capa" in p:
                    item["cover_url"] = fila["base_url"] + p["capa"]
                saida.append(item)
            else:
                saida.append({**p, "urls": [fila["base_url"] + i for i in p["imagens"]]})
    print(json.dumps(saida, ensure_ascii=False, indent=2))


def marcar(id_, status, extra=""):
    fila = carregar()
    for p in fila["postagens"]:
        if p["id"] == id_:
            p["status"] = status
            if status == "publicado":
                p["media_id"] = extra
            elif extra:
                p["erro"] = extra
            break
    else:
        sys.exit(f"id não encontrado: {id_}")
    FILA.write_text(json.dumps(fila, ensure_ascii=False, indent=2) + "\n")


def restantes():
    fila = carregar()
    hoje = agora(fila).strftime("%Y-%m-%d")
    dias = sorted({p["data"] for p in fila["postagens"]
                   if p["tipo"] == "carrossel" and p["data"] >= hoje})
    print(f"{len(dias)} carrosséis programados; último em {dias[-1] if dias else '—'}")


if __name__ == "__main__":
    cmd, *args = sys.argv[1:] or ["pendentes"]
    {"pendentes": pendentes, "marcar": marcar, "restantes": restantes}[cmd](*args)
