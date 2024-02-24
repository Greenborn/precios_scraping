#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.vea.com.ar/almacen/aceites-y-vinagres?__pickRuntime=appsEtag%2Cblocks%2CblocksTree%2Ccomponents%2CcontentMap%2Cextensions%2Cmessages%2Cpage%2Cpages%2Cquery%2CqueryData%2Croute%2CruntimeMeta%2Csettings&__device=desktop"

print("haciendo petición a: ", URL)
response = requests.get(URL)
response = response.json()

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