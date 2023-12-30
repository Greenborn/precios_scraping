import json
import requests
from bs4 import BeautifulSoup
import datetime

URL_BASE = "https://www.matelec.com.ar"

fecha = datetime.datetime.now().strftime("%Y%m%d")

response = requests.get(URL_BASE + "/shop")
response = response.text

soup = BeautifulSoup(response, 'html.parser')
cat_menu = soup.find(class_="o_wsale_filmstip_container")
arbol_categorias = {}

categorias = cat_menu.find_all('li')
for cat in categorias:
    categoria  = cat.find("span").text
    enlace_cat = cat.get("data-link-href")
    
    url_cat = URL_BASE + enlace_cat
    arbol_categorias[categoria] = { "category":"", "sub_items": [], "url": url_cat }

    print("ingresando a categoria: ", url_cat)
    response = requests.get(url_cat)
    response = response.text

    soup = BeautifulSoup(response, 'html.parser')
    sub_cat_menu = soup.find(class_="o_wsale_filmstip")

    if sub_cat_menu is None:
        print("No hay sub categorías")
        continue
    
    sub_categorias = sub_cat_menu.find_all('li')
    for sub_cat in sub_categorias:
        sub_categoria  = sub_cat.find("span").text
        enlace_sub_cat = sub_cat.get("data-link-href")
        enlace = { "texto": sub_cat.text, "category":"", "url": URL_BASE + enlace_sub_cat }
        arbol_categorias[categoria]["sub_items"].append(enlace)
        print(sub_categoria)

with open('categorias.json', 'w') as file:
    json.dump(arbol_categorias, file)
    print('categorias.json actualizado!')