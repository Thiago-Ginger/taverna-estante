# Estante da Magic Tavern

Mapas e aventuras de licença aberta, prontos para importar na [Magic Tavern](https://github.com/Thiago-Ginger/taverna) com um clique (aba Cenas → 📚 Estante).

Só entra aqui o que pode ser redistribuído. Cada item traz a licença e o crédito, e a importação cria na campanha uma entrada no diário com a atribuição.

## Fontes

| Fonte | O que entra | Licença | Crédito |
|---|---|---|---|
| [Dyson Logos](https://dysonlogos.blog/maps/commercial-maps/) | Mapas marcados com a licença comercial gratuita do autor (só a imagem, não o texto dos posts) | Licença comercial gratuita do Dyson Logos | "Cartography by Dyson Logos" (obrigatório) |
| [Watabou](https://watabou.itch.io/) (em breve) | Mapas gerados pelos geradores de masmorra, vila e cidade | Uso livre, inclusive comercial, nas palavras do autor | Apreciado, não obrigatório |
| [One Page Dungeon Contest](https://www.dungeoncontest.com/) (em breve) | Masmorras de uma página | CC BY-SA (3.0 ou 4.0, conforme o ano) | Autor de cada entrada; adaptações seguem CC BY-SA |

## Como está organizado

- `catalog.json`: a lista que a Magic Tavern lê (título, descrição, etiquetas, autor, licença, crédito, miniatura e endereço do pacote).
- `packages/<id>.json`: o pacote de cada item. É uma aventura da Magic Tavern (cenas, diário...) em que as imagens aparecem como `asset:<arquivo>`, mais a lista `assets` com o endereço de cada arquivo nas Releases.
- `thumbs/`: as miniaturas.
- As imagens grandes ficam nas [Releases](https://github.com/Thiago-Ginger/taverna-estante/releases) (`dyson-1`, ...).
- `tools/`: os scripts que montam os pacotes.

## Adicionar mapas do Dyson Logos

1. Confira que o mapa está na [lista de mapas comerciais](https://dysonlogos.blog/maps/commercial-maps/).
2. Baixe a versão com grid em JPG (a de 300 dpi, com casas de 75 px) para uma pasta, com o nome `<slug>.jpg`, e acrescente o mapa em `MAPS`, em `tools/build_dyson.py`.
3. Rode `python tools/build_dyson.py <pasta>`: ele mede o grid, gera a miniatura, o pacote e a entrada do catálogo.
4. Suba a imagem na Release: `gh release upload dyson-1 <pasta>/<slug>.jpg`.

## Licença deste repositório

Os scripts e o catálogo são MIT. Cada mapa ou aventura segue a licença da sua fonte, indicada no catálogo e no pacote.
