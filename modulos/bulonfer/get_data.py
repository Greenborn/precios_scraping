#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.bulonfer.com/ofertas"

print("haciendo petición a: ", URL)
response = requests.get(URL)
response = response.text

categorias = {}

response = response["extensions"]["store.search#category/$after_footer/footer-layout.desktop/footer-oculto"]["content"]["opciones"]


cant = 0
for elemento in response:
    
    if (elemento["correspondeA"] == "CATEGORIA" or elemento["correspondeA"] == "SUBCATEGORIA"):
        print("")

        if not "URL" in elemento:
            continue

        if elemento["URL"] == "":
            continue 

        cant = cant + 1
        categorias[elemento["anchorText"]] = { "category":"", "sub_items": [], "url": elemento["URL"] }
        print(categorias[elemento["anchorText"]], cant)
        print("")

        

with open('categorias.json', 'w') as file:
    json.dump(categorias, file)
    print('categorias.json actualizado!')