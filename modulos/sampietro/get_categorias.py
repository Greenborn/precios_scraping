import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://sampietroweb.com.ar"

response = requests.get(BASE_URL)
response = response.text

# Crear el objeto BeautifulSoup para analizar el HTML
soup = BeautifulSoup(response, 'html.parser')

elements = soup.find_all(class_="dropdown-submenu")

_categorias = {}

for submenus in elements:
    sub_items = submenus.find_all("a")
    
    for enlace in sub_items:
        categoria = enlace.text.strip()
        url       = enlace.get("href")
        id        = enlace.get("id")
        if id == None:
            continue
        id = id.split("drop")
        if len(id) < 2:
            continue
        _categorias[categoria] = { "texto": categoria, "id": id[1], "category":"", "url": BASE_URL + url }
        print(_categorias[categoria])
        print("")

with open('categorias.json', 'w') as file:
    json.dump(_categorias, file)
    print('categorias.json actualizado!')