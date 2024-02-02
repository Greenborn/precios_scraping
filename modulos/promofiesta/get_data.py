import requests
import datetime
import json
from bs4 import BeautifulSoup

BRANCH = 98
fecha = datetime.datetime.now().strftime("%Y%m%d")

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

listado_productos = []

for categoria in categorias:
    print("Procesado categoria: ", categoria)
    url = categorias[categoria]["url"]

    response = requests.get(url)
    response = response.text

    soup = BeautifulSoup(response, 'html.parser')
    products_html = soup.find_all(class_="col-9 col-sm-6 col-md-4 col-xl-3 mb-4 mx-auto")

    for product_html in products_html:
        try:
            producto = {
                "vendor_id": 58,
                "name": (categoria + " - " + product_html.find(class_="mb-0 text-primary fs").text.strip().replace("\n","")).strip(),
                "price": float(product_html.find(class_="precio-color text-bold text-danger fs").text.replace("/u", "").replace("/kg", "").replace("$", "").replace(",", "").strip()),
                "is_ext": "",
                "url": url,
                "branch_id": BRANCH,
                "category": categorias[categoria]["category"]
            }
        except:
            print("producto", product_html, "no procesado")
            continue
        listado_productos.append(producto)
        print(producto)
        print("")

path = 'salida/productos_cat'+fecha+'.json'
with open(path, 'w') as file:
    json.dump(listado_productos, file)
    print('estado.json actualizado')