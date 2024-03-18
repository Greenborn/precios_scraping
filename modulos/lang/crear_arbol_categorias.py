import json
from bs4 import BeautifulSoup

# Abrir el archivo HTML
with open('menu.html', 'r') as file:
    html_content = file.read()

# Crear el objeto BeautifulSoup para analizar el HTML
soup = BeautifulSoup(html_content, 'html.parser')

elements = soup.find_all(class_="dropdown-submenu")

arbol_categorias = {}

# Imprimir los elementos li de primer nivel
for element in elements:
    categoria  = element.find("a").text
    enlace_cat = element.find("a").get("href")
    print("Categoria: ", categoria)

    arbol_categorias[categoria] = { "category":"", "sub_items": []}
    
    ul_element = element.find('ul', class_='dropdown-menu')
    enlaces = ul_element.find_all('a')
    for sub_cat in enlaces:
        enlace = { "texto": sub_cat.text.replace("\n","").strip(), "category":"", "url": sub_cat.get("href") }
        arbol_categorias[categoria]["sub_items"].append(enlace)
        print(enlace)
    print("")
    
with open('categorias.json', 'w') as file:
    json.dump(arbol_categorias, file)
    print('categorias.json actualizado!')