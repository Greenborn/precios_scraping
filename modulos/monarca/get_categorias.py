#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests

URL_CATEGORIAS = "http://api.monarcadigital.com.ar/categories/struct?version=87ddd4f1-8d9b-4cbf-a677-07db09562e7c"

respuesta = requests.get(URL_CATEGORIAS)
respuesta = json.loads(respuesta.text)
categorias = respuesta["categories"]

lista_categorias = {}

for categoria in categorias:
    if (categoria["flagEnabled"]):
        print(categoria)
        lista_categorias[categoria["description"]] = { "category": "", "sub_items": [], "url": "", "id_ext": categoria["id"] }
        print("")

with open('categorias.json', 'w') as file:
    json.dump(lista_categorias, file)
    print('categorias.json actualizado!')

print(len(lista_categorias))