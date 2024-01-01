import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.sumaelectrohogar.com.ar"

print("haciendo petición a: ", URL)
response = requests.get(URL)
response = response.text


soup = BeautifulSoup(response, 'html.parser')
cat_menu = soup.find(class_="pt_vegamenu_cate")
arbol_categorias = {}

categorias = cat_menu.find_all(class_='pt_menu')
for cat in categorias:
    sub_cats = cat.find_all(class_='itemMenu level4')

    for sub_cat in sub_cats:
        enlaces = sub_cat.find_all('a')
        for enlace in enlaces:
            name_cat = enlace.text.strip()
            arbol_categorias[name_cat] = { "category":"", "sub_items": [], "url": enlace.get("href") }
            print(arbol_categorias[name_cat])
            print("")

with open('categorias.json', 'w') as file:
    json.dump(arbol_categorias, file)
    print('categorias.json actualizado!')