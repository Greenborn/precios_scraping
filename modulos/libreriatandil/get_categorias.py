import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.libreriatandil.com.ar/"

response = requests.get(URL)
response = response.text

soup = BeautifulSoup(response, 'html.parser')
menu = soup.find(class_='meninmenu')

menu_items = menu.find_all('li')

arbol_categorias = {}
for cat in menu_items:
    if (cat.find('ul') == None):
        categoria  = cat.text.strip()
        enlace_cat = cat.find("a").get("href")
        print("Categoria: ", categoria)

        arbol_categorias[categoria] = { "category":"", "sub_items": [], "url": enlace_cat}

with open('categorias.json', 'w') as file:
    json.dump(arbol_categorias, file)
    print('categorias.json actualizado!')