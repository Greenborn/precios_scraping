#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json

with open('subcategory-0.json') as archivo_json:
    categorias = json.load(archivo_json)

arbol_categorias = {}

for cat in categorias["urlset"]["url"]:
    url = cat["loc"]
    categoria = url.split("/")[-1].replace("-", " ").upper()
    arbol_categorias[categoria] = { "category":categoria, "sub_items": [], "url": url }
    print(arbol_categorias[categoria])

with open('categorias.json', 'w') as file:
    json.dump(arbol_categorias, file)
    print('categorias.json actualizado!')