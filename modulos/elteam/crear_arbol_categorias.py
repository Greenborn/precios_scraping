import json
import requests
from bs4 import BeautifulSoup
import datetime

URL_BASE = "https://eltheamcomputacion.mitiendanube.com/"

fecha = datetime.datetime.now().strftime("%Y%m%d")

response = requests.get(URL_BASE + "/shop")
response = response.text

soup = BeautifulSoup(response, 'html.parser')
cat_menu = soup.find(class_="desktop-list-subitems list-subitems nav-list-accordion")
arbol_categorias = {}

categorias = cat_menu.find_all('li')
for cat in categorias:
    categoria  = cat.find("a").text.strip()
    enlace_cat = cat.find("a").get("href")
    
    arbol_categorias[categoria] = { "category":"", "sub_items": [], "url": enlace_cat }

with open('categorias.json', 'w') as file:
    json.dump(arbol_categorias, file)
    print('categorias.json actualizado!')