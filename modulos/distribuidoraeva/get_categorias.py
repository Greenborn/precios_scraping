#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.distribuidoraeva.com.ar"

print("haciendo petición a: ", URL)
response = requests.get(URL, headers={
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0"
})
response = response.text

categorias = {}

soup = BeautifulSoup(response, 'html.parser')

mayores_scripts = soup.find_all("script")
mayor = mayores_scripts[0].text
for script in mayores_scripts:
    if len(mayor) < len(script.text):
        mayor = script.text

mayor = mayor.split("categorias_flatten = ")[1].split(";")[0]
mayor = json.loads(mayor)
print(mayor)

for cat in mayor:
    categoria  = cat["c_nombre"]
    enlace_cat = URL + cat["c_link_full"]
    
    categorias[categoria] = { "category":"", "id_ext": cat["idCategorias"], "sub_items": [], "url": enlace_cat }
    print(categorias[categoria])
    print("")

with open('categorias.json', 'w') as file:
    json.dump(categorias, file)
    print('categorias.json actualizado!')