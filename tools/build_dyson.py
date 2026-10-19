"""Gera os pacotes da estante com mapas do Dyson Logos.

Uso: python -I tools/build_dyson.py <pasta com as imagens .jpg baixadas>

Para cada mapa: confere o grid desenhado (tamanho da casa e deslocamento), gera a miniatura em
thumbs/, o pacote em packages/ e a entrada do catálogo. As imagens grandes vão na Release
`dyson-1` (gh release upload), com o mesmo nome de arquivo.

Licença dos mapas: licença comercial gratuita do Dyson Logos, só para os mapas marcados assim
em https://dysonlogos.blog/maps/commercial-maps/ ; o crédito "Cartography by Dyson Logos" é
obrigatório. O texto dos posts não está incluído (não faz parte da licença).
"""
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "Thiago-Ginger/taverna-estante"
RELEASE = "dyson-1"
RAW = f"https://raw.githubusercontent.com/{REPO}/main"
LICENSE_URL = "https://dysonlogos.blog/maps/commercial-maps/"
ATTRIBUTION = "Cartography by Dyson Logos"

MAPS = [
    {
        "slug": "the-flying-swine",
        "title": "The Flying Swine",
        "titlePt": "O Porco Voador",
        "post": "https://dysonlogos.blog/2026/02/06/the-flying-swine-a-fine-drinking-establishment/",
        "description": "Taverna com salão de mesas, balcão, cozinha, quartos e varanda.",
        "tags": ["taverna", "cidade"],
    },
    {
        "slug": "the-pilgrims-mug",
        "title": "The Pilgrim's Mug",
        "titlePt": "A Caneca do Peregrino",
        "post": "https://dysonlogos.blog/2026/04/08/the-pilgrims-mug/",
        "description": "Estalagem de beira de estrada em três pisos, lado a lado, com estábulo.",
        "tags": ["taverna", "estrada", "vários andares"],
    },
    {
        "slug": "sparrows-tower",
        "title": "Sparrow's Tower",
        "titlePt": "A Torre do Pardal",
        "post": "https://dysonlogos.blog/2026/02/11/sparrows-tower/",
        "description": "Ruína de torre com andares e porões ligados por escadas, lado a lado.",
        "tags": ["ruína", "torre", "vários andares"],
    },
    {
        "slug": "the-hollow-spire",
        "title": "The Hollow Spire",
        "titlePt": "O Pináculo Oco",
        "post": "https://dysonlogos.blog/2025/10/08/the-hollow-spire/",
        "description": "Torre de quatro andares com duas masmorras abaixo, cada nível no mesmo mapa.",
        "tags": ["torre", "masmorra", "vários andares"],
    },
    {
        "slug": "fallen-temple-of-sekhmet",
        "title": "Fallen Temple of Sekhmet",
        "titlePt": "O Templo Caído de Sekhmet",
        "post": "https://dysonlogos.blog/2025/12/12/fallen-temple-of-sekhmet/",
        "description": "Templo em ruínas com colunatas, salões e partes desmoronadas.",
        "tags": ["ruína", "templo"],
    },
    {
        "slug": "valgrenas-vault",
        "title": "Valgrena's Vault",
        "titlePt": "O Cofre de Valgrena",
        "post": "https://dysonlogos.blog/2026/01/09/valgrenas-vault/",
        "description": "Cripta simétrica em dois níveis, com salões de pilares e câmaras laterais.",
        "tags": ["masmorra", "cripta"],
    },
    {
        "slug": "tomb-beneath-the-mound",
        "title": "Tomb Beneath the Mound",
        "titlePt": "A Tumba sob o Monte",
        "post": "https://dysonlogos.blog/2026/06/10/tomb-beneath-the-mound/",
        "description": "Túmulo escavado sob um monte: galerias, câmara funerária e um segundo nível.",
        "tags": ["masmorra", "tumba"],
    },
    {
        "slug": "hollowshore-cairn",
        "title": "Hollowshore Cairn",
        "titlePt": "O Túmulo da Margem Oca",
        "post": "https://dysonlogos.blog/2026/06/17/hollowshore-cairn/",
        "description": "Túmulo de pedra numa ilha, com câmaras de pilares e celas, cercado de água.",
        "tags": ["masmorra", "tumba", "ilha"],
    },
    {
        "slug": "still-grotto",
        "title": "The Caves of Still Grotto",
        "titlePt": "As Cavernas da Gruta Parada",
        "post": "https://dysonlogos.blog/2026/04/10/the-caves-of-still-grotto/",
        "description": "Caverna marinha com um lago interno e passagens estreitas.",
        "tags": ["caverna", "costa"],
    },
    {
        "slug": "tideworn-grotto",
        "title": "Tideworn Grotto",
        "titlePt": "A Gruta das Marés",
        "post": "https://dysonlogos.blog/2025/09/10/tideworn-grotto/",
        "description": "Grutas na costa gastas pelo mar, em terraços, com um redemoinho.",
        "tags": ["caverna", "costa"],
    },
]


def grid(path):
    """Tamanho da casa e deslocamento do grid desenhado (pelo perfil das linhas finas)."""
    a = 255.0 - np.asarray(Image.open(path).convert("L"), dtype=np.float64)
    out = []
    for profile in (a.mean(axis=0), a.mean(axis=1)):
        trend = np.convolve(profile, np.ones(15) / 15, mode="same")
        fine = np.clip(profile - trend, 0, None)
        best = (0.0, 0, 0)
        for period in range(30, 121):
            for offset in range(period):
                score = fine[offset::period].mean() - fine.mean()
                if score > best[0]:
                    best = (score, period, offset)
        _, period, offset = best
        # Um pixel antes do período é o mesmo grid começando em 0.
        out.append((period, 0 if offset in (0, period - 1) else offset))
    (px, ox), (py, oy) = out
    if px != py:
        raise SystemExit(f"{path}: grid diferente nos eixos ({px} x {py})")
    return px, ox, oy


def para(text):
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}


def package(m, size, width, height, ox, oy):
    asset = f"{m['slug']}.jpg"
    credits = {
        "type": "doc",
        "content": [
            para(f"{m['titlePt']} ({m['title']}). {m['description']}"),
            para(
                f"{ATTRIBUTION}. Mapa original: {m['post']}. Licença comercial gratuita do autor "
                f"(crédito obrigatório): {LICENSE_URL}"
            ),
            para(
                "Escala sugerida: 1 quadrado = 5 pés (dá para mudar nas opções da cena). O mapa "
                "não traz paredes: use a ferramenta de paredes se quiser bloquear passagem e visão."
            ),
        ],
    }
    adventure = {
        "name": m["titlePt"],
        "description": m["description"],
        "homebrew": [],
        "docs": [
            {
                "ref": "creditos",
                "doc": {
                    "kind": "journal",
                    "data": {
                        "title": f"{m['titlePt']}: créditos",
                        "pages": [
                            {
                                "id": "p1",
                                "title": "Créditos",
                                "kind": "text",
                                "doc": credits,
                                "imageUrl": None,
                                "caption": "",
                            }
                        ],
                    },
                },
            },
            {
                "ref": "cena",
                "doc": {
                    "kind": "scene",
                    "data": {
                        "scene": {
                            "name": m["titlePt"][:60],
                            "imageUrl": f"asset:{asset}",
                            "width": width,
                            "height": height,
                            "grid": {
                                "size": size,
                                "offsetX": ox,
                                "offsetY": oy,
                                "visible": False,
                                "distance": 5,
                                "units": "ft",
                            },
                            "journalId": "creditos",
                            "globalLight": True,
                            "darkness": 0,
                        },
                        "tokens": [],
                        "templates": [],
                        "drawings": [],
                        "notes": [],
                        "walls": [],
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
    src = sys.argv[1]
    items = []
    for m in MAPS:
        path = os.path.join(src, f"{m['slug']}.jpg")
        img = Image.open(path)
        width, height = img.size
        size, ox, oy = grid(path)
        thumb = img.convert("RGB")
        thumb.thumbnail((480, 480))
        thumb.save(os.path.join(ROOT, "thumbs", f"dyson-{m['slug']}.jpg"), quality=78)
        pkg = package(m, size, width, height, ox, oy)
        with open(os.path.join(ROOT, "packages", f"dyson-{m['slug']}.json"), "w", encoding="utf-8") as f:
            json.dump(pkg, f, ensure_ascii=False, indent=1)
        items.append(
            {
                "id": f"dyson-{m['slug']}",
                "kind": "map",
                "title": m["titlePt"],
                "originalTitle": m["title"],
                "description": m["description"],
                "tags": m["tags"],
                "author": "Dyson Logos",
                "source": m["post"],
                "license": "Licença comercial gratuita do Dyson Logos (crédito obrigatório)",
                "licenseUrl": LICENSE_URL,
                "attribution": ATTRIBUTION,
                "thumb": f"{RAW}/thumbs/dyson-{m['slug']}.jpg",
                "package": f"{RAW}/packages/dyson-{m['slug']}.json",
                "grid": {"size": size, "squares": [width // size, height // size]},
            }
        )
        print(f"{m['slug']}: {width}x{height}, casa {size}px, deslocamento ({ox},{oy})")
    catalog_path = os.path.join(ROOT, "catalog.json")
    catalog = {"format": 1, "items": []}
    if os.path.exists(catalog_path):
        with open(catalog_path, encoding="utf-8") as f:
            catalog = json.load(f)
    others = [i for i in catalog["items"] if not i["id"].startswith("dyson-")]
    catalog["items"] = others + items
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=1)
    print(f"catálogo: {len(catalog['items'])} itens")


if __name__ == "__main__":
    main()
