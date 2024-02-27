#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.bringeri.com.ar/climatizacion/calefaccion/calefaccion-a-lena?__pickRuntime=appsEtag,blocks,blocksTree,components,contentMap,extensions,messages,page,pages,query,queryData,route,runtimeMeta,settings&__device=desktop"

print("haciendo petición a: ", URL)
response = requests.get(URL)
response = response.json()

categorias = {}

response = response["extensions"]

cant = 0
for pos_cat in response:
    if "store.search#subcategory/$before_header.full/header-layout.desktop/sticky-layout#main-header-desktop/flex-layout.row#category-menu-desktop/flex-layout.col#category-menu-desktop-container/flex-layout.row#category-menu-desktop-content/flex-layout.col#category-menu-desktop-col-1/flex-layout.row#category-menu-desktop-col-1-content/flex-layout.col#trigger-category-menu/overlay-trigger#category-drawer-menu/overlay-layout#category-drawer-menu/disclosure-layout-group#category-drawer-menu/" in pos_cat:
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

