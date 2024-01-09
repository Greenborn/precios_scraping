import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.greenboutique.com.ar/"

print("haciendo petición a: ", URL)
response = requests.get(URL)
response = response.text


soup = BeautifulSoup(response, 'html.parser')
cat_menu = soup.find(class_="js-desktop-nav-col")
arbol_categorias = {}

menuenlaces = cat_menu.find_all('li', recursive=False)
arbol_categorias = {}
for menuitem in menuenlaces:

    categorias = menuitem.find_all('li')
    for cat in categorias:
        link = cat.find("a").get("href")
        nombre_cat = cat.text.strip()
        if "\n" in nombre_cat:
            print("Hay saltos de linea en ", nombre_cat)
            continue
        arbol_categorias[nombre_cat] = { "category":"", "sub_items": [], "url": link }
        print(nombre_cat)
        print("")

with open('categorias.json', 'w') as file:
    json.dump(arbol_categorias, file)
    print('categorias.json actualizado!')