#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.carrefour.com.ar/almacen/aceites-y-vinagres/aceites-comunes?__pickRuntime=appsEtag%2Cblocks%2CblocksTree%2Ccomponents%2CcontentMap%2Cextensions%2Cmessages%2Cpage%2Cpages%2Cquery%2CqueryData%2Croute%2CruntimeMeta%2Csettings&__device=desktop"

print("haciendo petición a: ", URL)
response = requests.get(URL)
response = response.json()

categorias = {}

response = response["extensions"]

cant = 0
for pos_cat in response:
    if "store.search#subcategory/$before_header.full/header-layout.desktop/header-row#3-d-mainHeader/drawer#menu-desktop/flex-layout.row#main-menu-desktop/vtex.menu@2.x:menu#category-menu/content-visibility" in pos_cat:
        elemento = response[pos_cat]
        if (elemento["component"] == "vtex.menu@2.35.1/MenuItem"):
            if not "href" in elemento["content"]["itemProps"]:
                continue

            if elemento["content"]["itemProps"]["href"] == "":
                continue 

            cant = cant + 1
            categorias[elemento["content"]["itemProps"]["text"]] = { "category":"", "sub_items": [], "url": elemento["content"]["itemProps"]["href"] }
            print(categorias[elemento["content"]["itemProps"]["text"]], cant)
            print("")

with open('categorias.json', 'w') as file:
    json.dump(categorias, file)
    print('categorias.json actualizado!')