#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.prestigio.com.ar"

print("haciendo petición a: ", URL)
response = requests.get(URL)
response = response.text

categorias = {}

soup = BeautifulSoup(response, 'html.parser')
scripts = soup.find_all("script")

mayor_script = ''
mayor_cant = 0
for script in scripts:
    if (len(script.text) > mayor_cant):
        mayor_cant = len(script.text)
        mayor_script = script.text

mayor_script = mayor_script.replace('__RUNTIME__ = ', '')
mayor_script = mayor_script.replace('__STATE__ = {}', '')
mayor_script = json.loads( mayor_script )
mayor_script = mayor_script["extensions"]["store.home\u002F$before_menu-context"]["content"]["menuPrimerNivel"]

for cat in mayor_script:
    if (not "menuSegundoNivel" in cat):
        categoria  = cat["__editorItemTitle"]
        enlace_cat = URL + cat["linkCategoryPrincipal"].strip()
        
        categorias[categoria] = { "category":"", "sub_items": [], "url": enlace_cat }
        print(categorias[categoria])
        print("")
    else:
        for s_cat in cat["menuSegundoNivel"]:
            if (not "menuTercerNivel" in s_cat):
                categoria  = s_cat["__editorItemTitle"]
                enlace_cat = URL + s_cat["linkSubCategoria"].strip()
                
                categorias[categoria] = { "category":"", "sub_items": [], "url": enlace_cat }
                print(categorias[categoria])
                print("")
            else:
                for ss_cat in s_cat["menuTercerNivel"]:
                    categoria  = ss_cat["__editorItemTitle"]
                    enlace_cat = URL + ss_cat["linkCategory"].strip()
                    
                    categorias[categoria] = { "category":"", "sub_items": [], "url": enlace_cat }
                    print(categorias[categoria])
                    print("")


with open('categorias.json', 'w') as file:
    json.dump(categorias, file)
    print('categorias.json actualizado!')