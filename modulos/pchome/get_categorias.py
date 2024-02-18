import json
from bs4 import BeautifulSoup

BASE_URL = "https://www.pchome.com.ar/app/"

# Abrir el archivo HTML
with open('menu.html', 'r') as file:
    html_content = file.read()

# Crear el objeto BeautifulSoup para analizar el HTML
soup = BeautifulSoup(html_content, 'html.parser')

elements = soup.find_all(class_="dropdown tt-megamenu-col-01 tt-submenu")

arbol_categorias = {}

# Imprimir los elementos li de primer nivel
for element in elements:
    sub_items = element.find(class_="tt-megamenu-submenu")
    categoria = element.find("a").text
    
    arbol_categorias[categoria] = { "category":"", "sub_items": []}

    for sub_item in sub_items:
        link = sub_item.find("a")
        if link != -1:
            enlace = { "texto": link.text, "category":"", "url": BASE_URL + link.get("href") }
            arbol_categorias[categoria]["sub_items"].append(enlace)

with open('categorias.json', 'w') as file:
    json.dump(arbol_categorias, file)
    print('categorias.json actualizado!')
