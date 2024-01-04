import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.otero.com.ar/"

print("haciendo petición a: ", URL)
response = requests.get(URL)
response = response.text


soup = BeautifulSoup(response, 'html.parser')

arbol_categorias = {}

conte = soup.find_all("ul",class_='dropdown-menu menu-2')

for cnt in conte:
    conte_2 = cnt.find_all("ul",class_='menu-3')

    for conte in conte_2:
        categorias = conte.find_all("li")
        for cat in categorias:
            
            enlaces = cat.find_all('a')
            for enlace in enlaces:
                name_cat = enlace.text.strip()
                arbol_categorias[name_cat] = { "category":"", "sub_items": [], "url": enlace.get("href") }
                print(arbol_categorias[name_cat])
                print("")

with open('categorias.json', 'w') as file:
    json.dump(arbol_categorias, file)
    print('categorias.json actualizado!')

