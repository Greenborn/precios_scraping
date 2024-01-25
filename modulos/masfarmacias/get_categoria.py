import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.masfarmacias.com/"

response = requests.get(URL)
response = response.text

soup = BeautifulSoup(response, 'html.parser')
categorias = soup.find_all(class_='hfe-sub-menu-item')

arbol_categorias = {}
for cat in categorias:
    categoria  = cat.text
    enlace_cat = cat.get("href")
    print("Categoria: ", categoria)

    arbol_categorias[categoria] = { "category":"", "sub_items": [], "url": enlace_cat}

with open('categorias.json', 'w') as file:
    json.dump(arbol_categorias, file)
    print('categorias.json actualizado!')