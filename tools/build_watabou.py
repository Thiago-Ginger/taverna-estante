"""Gera os pacotes da estante com masmorras do One Page Dungeon, de Watabou.

Uso: python -I tools/build_watabou.py <pasta com <seed>.json e <seed>.png>

Como exportar cada masmorra (https://watabou.github.io/one-page-dungeon/?seed=<seed>), no menu do
botão direito:
- View: desligue "Rotate-to-fit" (a masmorra fica alinhada ao grid);
- Layers: desligue "Title & story"; Notes: "Off" (as notas viram marcadores na cena);
- Export as > JSON e Export as > PNG... com 70 px por casa.

Do JSON saem as paredes (o contorno das salas e corredores, com as rotundas em círculo), as
portas (comuns, trancadas, grades e secretas), as notas das salas como marcadores só do mestre e
o diário com a história. Os textos foram traduzidos para o português.

Licença: nas palavras do autor, as imagens criadas pelo gerador podem ser usadas como quiser,
inclusive em aventuras comerciais (https://watabou.itch.io/one-page-dungeon). Crédito apreciado.
"""
import json
import math
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "Thiago-Ginger/taverna-estante"
RELEASE = "watabou-1"
RAW = f"https://raw.githubusercontent.com/{REPO}/main"
LICENSE_URL = "https://watabou.itch.io/one-page-dungeon"
ATTRIBUTION = "Masmorra gerada com o One Page Dungeon, de Watabou"
C = 70  # px por casa no PNG exportado
PAPER = (237, 224, 206)  # cor do papel do gerador, para o fundo transparente

# Tipos de porta do JSON, conferidos no desenho: 0 passagem, 2 arco, 3/8/9 escadas (sem parede).
DOORS = {
    1: {"door": "door", "ds": "closed", "doorSound": "wood"},
    5: {"door": "door", "ds": "locked", "doorSound": "metal"},  # porta reforçada
    7: {"door": "door", "ds": "locked", "doorSound": "metal"},  # porta reforçada
    4: {"door": "door", "ds": "locked", "doorSound": "metal", "see": True},  # grade
    6: {"door": "secret", "ds": "closed", "doorSound": "stone"},
}

MAPS = [
    {
        "seed": 307326832,
        "title": "O Baluarte Superior do Titã das Sombras",
        "story": "O Titã das Sombras se foi há muito tempo, mas o povo ainda evita chegar perto do baluarte. Hoje ele está infestado de leões, que não ligam para o passado do lugar. Dizem que o baluarte guarda tesouros de artefatos mágicos e livros antigos.",
        "notes": {
            "1": "Um baú guarda um anel de ouro.",
            "2": "Algum ouro escondido numa fresta da parede.",
            "3": "Um cesto médio com uma chave dentro.",
            "4": "Uma porta dupla redonda, com fechadura, na parede norte da câmara pequena.",
        },
        "tags": ["fortaleza", "feras"],
    },
    {
        "seed": 1001,
        "title": "O Solar Secreto do Sacerdote Vermelho",
        "story": "Por um milênio o solar do Sacerdote Vermelho ficou abandonado. Há pouco tempo um dragão morto-vivo fez dele seu covil. Dizem que o solar é rico em ouro.",
        "notes": {
            "1": "Uma porta grande, com fechadura, a oeste.",
            "2": "Um painel na parede esconde uma chave em forma de peixe.",
            "3": "Um caçador anão empalhado, segurando uma capa estranha que vibra de leve.",
            "4": "Um caixote quebrado com algum ouro, rações e um cajado.",
            "5": "Uma artífice misteriosa, de cabelo desgrenhado, descansando no chão.",
        },
        "tags": ["solar", "morto-vivo", "dragão"],
    },
    {
        "seed": 1002,
        "title": "O Sepulcro do Messias de Gelo",
        "story": "Desde a morte do Messias de Gelo o sepulcro mudou de mãos muitas vezes. Hoje está tomado por águias, indiferentes ao passado do lugar.",
        "notes": {
            "1": "Um poço sem fundo: responde a uma pergunta se alguém jogar uma moeda nele.",
            "2": "Uma enorme porta de pedra, com duas fechaduras, na parede sul da câmara pequena.",
            "3": "Uma chave em forma de coroa no meio de um pentagrama desenhado no chão.",
            "4": "Uma caixa média com uma chave em forma de coroa.",
            "5": "Uma glaive entre os escombros no chão.",
            "6": "O corpo petrificado de um ogro, com algum ouro e um escudo por perto.",
        },
        "tags": ["tumba", "feras"],
    },
    {
        "seed": 1003,
        "title": "O Salão Submerso do Ceifador Dourado",
        "story": "O salão do Ceifador Dourado fica numa ilha solitária e está parcialmente alagado. Hoje está tomado por leões. Dizem que a lendária pedra Karketrondeh está escondida aqui.",
        "notes": {
            "1": "Algum ouro num armário médio.",
            "2": "Uma porta em forma de boca, a leste.",
        },
        "tags": ["ilha", "água", "feras"],
    },
    {
        "seed": 1004,
        "title": "Os Salões do Ceifador Sombrio",
        "story": "Desde a morte do Ceifador Sombrio os salões mudaram de mãos muitas vezes. Hoje estão tomados por serpentes.",
        "notes": {
            "1": "Uma pintura, totalmente destruída por gnolls vândalos.",
            "2": "Uma grande porta de madeira na parede leste da câmara.",
            "3": "Uma pedra do medo sobre um pedestal.",
            "4": "Um trono de ferro: quem se senta nele faz surgir um espelho estranho, que solta fumaça.",
            "5": "Uma entrada dos fundos dos salões. Um cesto reforçado com gemas.",
        },
        "tags": ["salões", "serpentes"],
    },
    {
        "seed": 1005,
        "title": "A Fortaleza da Dama Aranha",
        "story": "A Dama Aranha se foi há muito tempo, mas o povo ainda evita chegar perto da fortaleza. Hoje ela está infestada de formigas. Na fortaleza cresce uma espécie rara de frutinhas.",
        "notes": {
            "1": "Um baú guarda uma katana.",
            "2": "O corpo meio devorado de um bardo, com uma chave de cobre por perto.",
            "3": "Um cachecol estranho, que brilha de leve, num caixote podre.",
            "4": "Uma porta dupla redonda, revestida de ferro, com duas fechaduras, na parede leste da sala pequena.",
            "5": "Uma pilha de escombros esconde algum ouro e uma capa.",
            "6": "Uma chave de cobre flutuando no meio da sala pequena.",
        },
        "tags": ["fortaleza", "insetos"],
    },
    {
        "seed": 1006,
        "title": "O Refúgio do Deserto da Bruxa Demoníaca",
        "story": "O refúgio da Bruxa Demoníaca fica numa ilha remota. Há pouco tempo uma temível fera mutante fez dele sua casa.",
        "notes": {
            "1": "Uma porta surrada, a leste.",
            "2": "Um cofre surrado com algum ouro e um escudo.",
            "3": "Uma caixa guarda gemas.",
            "4": "Uma entrada dos fundos do refúgio.",
            "5": "O cadáver de um halfling, com velas por perto.",
            "6": "Um objeto sinistro, que sangra, trancado num cofre.",
        },
        "tags": ["ilha", "deserto", "monstro"],
    },
    {
        "seed": 1007,
        "title": "O Covil do Cavaleiro Lich",
        "story": "O covil do Cavaleiro Lich fica no fundo da floresta escura, protegido pelos bichos perigosos da região e pelo clima hostil. Hoje é controlado por um bando de cultistas, e parte dele está alagada. Correm boatos de que o covil guarda tesouros de livros antigos.",
        "notes": {
            "1": "Uma entrada dos fundos do covil.",
            "2": "Fogo num braseiro: quem toca nele cai no sono.",
            "3": "Um cajado profano trancado num cofre mágico.",
            "4": "Um mosaico de flechas no teto.",
            "5": "Uma chave de prata no meio de um círculo de runas no chão.",
            "6": "Um cultista morrendo; entre suas coisas, um pente misterioso coberto de hieróglifos.",
            "7": "Uma porta revestida de ferro, chamuscada, com fechadura, na parede norte.",
        },
        "tags": ["covil", "morto-vivo", "cultistas", "água", "floresta"],
    },
    {
        "seed": 1008,
        "title": "A Cidadela de Riellas-Don",
        "story": "A cidadela de Riellas-Don fica numa ilha distante. Hoje está tomada por javalis, indiferentes ao passado do lugar.",
        "notes": {
            "1": "Uma porta maciça, a oeste.",
            "2": "Um anão morrendo; entre suas coisas, um medalhão estranho que vibra.",
            "3": "Um machado estranho, coberto de símbolos, flutuando no meio da câmara pequena.",
        },
        "tags": ["fortaleza", "ilha", "feras"],
    },
    {
        "seed": 1009,
        "title": "A Pirâmide Eterna de Nemeia",
        "story": "A pirâmide de Nemeia fica numa curva do profundo rio Rhun-Mos. Hoje está tomada por morcegos. Na pirâmide cresce uma espécie muito valiosa de cogumelos.",
        "notes": {
            "1": "Um portão enorme na parede norte.",
            "2": "Um sacerdote cego, tremendo de medo.",
            "3": "Um cachecol num baú médio.",
            "4": "O corpo esfolado de um hobgoblin, com um pé de cabra e uma glaive por perto.",
        },
        "tags": ["pirâmide", "templo", "feras"],
    },
]


def cells_of(d):
    return {
        (r["x"] + i, r["y"] + j) for r in d["rects"] for i in range(r["w"]) for j in range(r["h"])
    }


def align(d, im):
    """Casa (x0, y0) do JSON que cai no canto do PNG (a margem muda de mapa para mapa)."""
    cells = cells_of(d)
    mx = min(c[0] for c in cells)
    my = min(c[1] for c in cells)
    best = None
    for x0 in range(mx - 3, mx + 1):
        for y0 in range(my - 3, my + 1):
            ok = 0
            for x, y in cells:
                px, py = int((x - x0 + 0.3) * C), int((y - y0 + 0.3) * C)
                if 0 <= px < im.width and 0 <= py < im.height:
                    p = im.getpixel((px, py))
                    ok += p[3] > 200 and sum(p[:3]) / 3 > 150
            score = ok / len(cells)
            if best is None or score > best[0]:
                best = (score, x0, y0)
    if best[0] < 0.9:
        raise SystemExit(f"PNG não bate com o JSON ({best[0]:.0%})")
    return best


def wall(c, **kw):
    w = {
        "c": [round(v, 1) for v in c],
        "move": "normal",
        "sight": "normal",
        "light": "normal",
        "sound": "normal",
        "dir": "both",
        "door": "none",
        "ds": "closed",
    }
    w.update(kw)
    return w


def merge(edges):
    """Junta arestas de 1 casa na mesma linha em segmentos longos."""
    out = []
    for horizontal in (True, False):
        lines = {}
        for e in edges:
            (ax, ay), (bx, by) = e
            if (ay == by) != horizontal:
                continue
            key, a, b = (ay, min(ax, bx), max(ax, bx)) if horizontal else (ax, min(ay, by), max(ay, by))
            lines.setdefault(key, []).append((a, b))
        for key, segs in lines.items():
            segs.sort()
            start, end = segs[0]
            for a, b in segs[1:] + [(None, None)]:
                if a == end:
                    end = b
                    continue
                out.append((start, key, end, key) if horizontal else (key, start, key, end))
                start, end = a, b
    return out


def walls_for(d, x0, y0):
    cells = cells_of(d)
    rotundas = [r for r in d["rects"] if r.get("rotunda")]

    def in_rotunda(cell):
        return any(r["x"] <= cell[0] < r["x"] + r["w"] and r["y"] <= cell[1] < r["y"] + r["h"] for r in rotundas)

    edges = []
    openings = []  # pontos do contorno das rotundas por onde se entra
    for x, y in cells:
        for dx, dy, edge in (
            (0, -1, ((x, y), (x + 1, y))),
            (0, 1, ((x, y + 1), (x + 1, y + 1))),
            (-1, 0, ((x, y), (x, y + 1))),
            (1, 0, ((x + 1, y), (x + 1, y + 1))),
        ):
            n = (x + dx, y + dy)
            inside = in_rotunda((x, y))
            if inside and n in cells and not in_rotunda(n):
                openings.append(((edge[0][0] + edge[1][0]) / 2, (edge[0][1] + edge[1][1]) / 2))
            if n in cells:
                continue
            if inside:
                continue  # a rotunda ganha um círculo no lugar do quadrado
            edges.append(edge)
    segs = merge(edges)
    px = lambda x: (x - x0) * C  # noqa: E731
    py = lambda y: (y - y0) * C  # noqa: E731
    out = [wall((px(a), py(b), px(c), py(e))) for a, b, c, e in segs]
    for r in rotundas:
        cx, cy, rad = r["x"] + r["w"] / 2, r["y"] + r["h"] / 2, r["w"] / 2
        n = 8 * r["w"]
        for i in range(n):
            a1, a2 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            p1 = (cx + rad * math.cos(a1), cy + rad * math.sin(a1))
            p2 = (cx + rad * math.cos(a2), cy + rad * math.sin(a2))
            mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
            if any(math.hypot(mid[0] - ox, mid[1] - oy) < 0.5 for ox, oy in openings):
                continue
            out.append(wall((px(p1[0]), py(p1[1]), px(p2[0]), py(p2[1]))))
    doors = 0
    for q in d["doors"]:
        kind = DOORS.get(q["type"])
        if not kind:
            continue
        x, y = q["x"], q["y"]
        if q["dir"]["y"] != 0:
            c = (px(x), py(y + 0.5), px(x + 1), py(y + 0.5))
        else:
            c = (px(x + 0.5), py(y), px(x + 0.5), py(y + 1))
        extra = {k: v for k, v in kind.items() if k != "see"}
        if kind.get("see"):
            extra.update(sight="none", light="none", sound="none")
        out.append(wall(c, **extra))
        doors += 1
    return out, doors


def para(text):
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}


def package(m, d, size, x0, y0, walls):
    asset = f"watabou-{m['seed']}.jpg"
    source = f"https://watabou.github.io/one-page-dungeon/?seed={m['seed']}"
    notes = sorted(d["notes"], key=lambda n: int(n["ref"]))
    rooms = {"type": "doc", "content": [para(m["story"])] + [para(f"{n['ref']}. {m['notes'][n['ref']]}") for n in notes]}
    credits = {
        "type": "doc",
        "content": [
            para(f"{ATTRIBUTION} (semente {m['seed']}, título original: {d['title']}). Mapa: {source}"),
            para(
                "Nas palavras do autor, as imagens do gerador podem ser usadas como quiser, inclusive em "
                f"aventuras comerciais: {LICENSE_URL}. Textos traduzidos para o português."
            ),
            para(
                "Escala sugerida: 1 quadrado = 5 pés. Paredes e portas já vêm no mapa; as notas das "
                "salas aparecem como marcadores só para o mestre."
            ),
        ],
    }
    page = lambda pid, title, doc: {  # noqa: E731
        "id": pid, "title": title, "kind": "text", "doc": doc, "imageUrl": None, "caption": "",
    }
    adventure = {
        "name": m["title"],
        "description": m["story"],
        "homebrew": [],
        "docs": [
            {
                "ref": "masmorra",
                "doc": {
                    "kind": "journal",
                    "data": {
                        "title": m["title"],
                        "pages": [page("p1", "A masmorra", rooms), page("p2", "Créditos", credits)],
                    },
                },
            },
            {
                "ref": "cena",
                "doc": {
                    "kind": "scene",
                    "data": {
                        "scene": {
                            "name": m["title"][:60],
                            "imageUrl": f"asset:{asset}",
                            "width": size[0],
                            "height": size[1],
                            "grid": {"size": C, "offsetX": 0, "offsetY": 0, "visible": False, "distance": 5, "units": "ft"},
                            "journalId": "masmorra",
                            "backgroundColor": "#EDE0CE",
                            "globalLight": True,
                            "darkness": 0,
                        },
                        "tokens": [],
                        "templates": [],
                        "drawings": [],
                        "notes": [
                            {
                                "x": round((n["pos"]["x"] - x0) * C, 1),
                                "y": round((n["pos"]["y"] - y0) * C, 1),
                                "title": f"{n['ref']}. {m['notes'][n['ref']]}"[:80],
                                "text": m["notes"][n["ref"]],
                                "color": "#8B2E1F",
                                "gmOnly": True,
                                "journalId": "masmorra",
                            }
                            for n in notes
                        ],
                        "walls": walls,
                        "lights": [],
                    },
                },
            },
        ],
    }
    return {
        "format": 1,
        "adventure": adventure,
        "assets": {asset: f"https://github.com/{REPO}/releases/download/{RELEASE}/{asset}"},
    }


def main():
    src, out_img = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]
    items = []
    for m in MAPS:
        base = os.path.join(src, str(m["seed"]))
        with open(base + ".json", encoding="utf-8") as f:
            d = json.load(f)
        if set(m["notes"]) != {n["ref"] for n in d["notes"]}:
            raise SystemExit(f"{m['seed']}: notas traduzidas não batem com o JSON")
        im = Image.open(base + ".png").convert("RGBA")
        score, x0, y0 = align(d, im)
        walls, doors = walls_for(d, x0, y0)
        flat = Image.new("RGB", im.size, PAPER)
        flat.paste(im, mask=im.split()[3])
        flat.save(os.path.join(out_img, f"watabou-{m['seed']}.jpg"), quality=88)
        thumb = flat.copy()
        thumb.thumbnail((480, 480))
        thumb.save(os.path.join(ROOT, "thumbs", f"watabou-{m['seed']}.jpg"), quality=78)
        pkg = package(m, d, im.size, x0, y0, walls)
        with open(os.path.join(ROOT, "packages", f"watabou-{m['seed']}.json"), "w", encoding="utf-8") as f:
            json.dump(pkg, f, ensure_ascii=False, indent=1)
        items.append(
            {
                "id": f"watabou-{m['seed']}",
                "kind": "adventure",
                "title": m["title"],
                "originalTitle": d["title"],
                "description": m["story"],
                "tags": ["masmorra"] + m["tags"],
                "author": "Watabou",
                "source": f"https://watabou.github.io/one-page-dungeon/?seed={m['seed']}",
                "license": "Uso livre, inclusive comercial (nas palavras do autor)",
                "licenseUrl": LICENSE_URL,
                "attribution": ATTRIBUTION,
                "thumb": f"{RAW}/thumbs/watabou-{m['seed']}.jpg",
                "package": f"{RAW}/packages/watabou-{m['seed']}.json",
                "grid": {"size": C, "squares": [im.width // C, im.height // C]},
            }
        )
        print(f"{m['seed']}: {im.width}x{im.height}, alinhamento {score:.0%}, {len(walls)} paredes ({doors} portas), {len(d['notes'])} notas")
    catalog_path = os.path.join(ROOT, "catalog.json")
    with open(catalog_path, encoding="utf-8") as f:
        catalog = json.load(f)
    others = [i for i in catalog["items"] if not i["id"].startswith("watabou-")]
    catalog["items"] = others + items
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=1)
    print(f"catálogo: {len(catalog['items'])} itens")


if __name__ == "__main__":
    main()
