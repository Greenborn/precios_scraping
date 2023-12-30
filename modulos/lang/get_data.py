import json
import requests
from bs4 import BeautifulSoup
import datetime
import re

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

BRANCH_ID = 86

fecha = datetime.datetime.now().strftime("%Y%m%d")

listado_productos = []

for categoria in categorias:
    print("Procesado categoria Nivel 0: ",categoria)

    for sub_categoria in categorias[categoria]['sub_items']:
        texto_sub_cat = sub_categoria['texto']
        print("----> Procesando sub categoría: ",texto_sub_cat)

        page = 1
        while True:
            url = sub_categoria["url"] + "?&page=" + str(page)
            print("haciendo petición a: ", url)
            response = requests.get(url, 
                                    headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0'})

            response = response.text

            soup = BeautifulSoup(response, 'html.parser')

            product_html = soup.find_all(class_="card-ecommerce")
            print("Cant Productos: ", len(product_html))

            if (len(product_html) == 0):
                print("Se terminaron las paginas")
                break

            for product in product_html:
                html_data = BeautifulSoup(str(product.contents), 'html.parser')
                precio = re.findall(r'\d+', html_data.find(class_="pecio_final").text)
                
                if len(precio) == 0:
                    print("Precio invalido")
                    continue

                precio = ''.join(precio)
                
                producto = {
                    "vendor_id": 58,
                    "name": html_data.find(class_="card-title").text,
                    "price": float(precio.replace("/u", "").replace("/kg", "").replace("$", "").replace(",", "").strip()),
                    "is_ext": "",
                    "branch_id": BRANCH_ID,
                    "category": sub_categoria["category"]
                }
                listado_productos.append(producto)
                print(producto)
            
            page = page +1

path = 'salida/productos_cat'+fecha+'.json'
with open(path, 'w') as file:
    json.dump(listado_productos, file)
    print(path,' actualizado')


