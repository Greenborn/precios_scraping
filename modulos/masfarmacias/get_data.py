import json
import requests
from bs4 import BeautifulSoup
import datetime

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

BRANCH_ID = 127

fecha = datetime.datetime.now().strftime("%Y%m%d")

listado_productos = []

diccio_nam = {}

def procesar_elementos( url, cat_id, categoria ):
    cantidad = 0
    print(url)

    response = requests.get(url)
    response = response.text
    soup = BeautifulSoup(response, 'html.parser')

    articulos = soup.find_all("article")
    
    for art in articulos:
        nombre = categoria + ' - ' + art.find_all("a")[2].text
        if (nombre in diccio_nam):
            continue
        diccio_nam[nombre] = True
        producto = {
            "vendor_id": 58,
            "name": nombre,
            "url": art.find_all("a")[2].get("href"),
            "price": float(art.find("bdi").text.replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").replace(",", ".").strip()),
            "is_ext": "",
            "branch_id": BRANCH_ID,
            "category": cat_id
        }
        cantidad = cantidad + 1
        listado_productos.append(producto)
        print(producto)
    return cantidad

for categoria in categorias:
    url = categorias[categoria]['url']

    procesados = procesar_elementos( url, categorias[categoria]["category"],  categoria )
    if (procesados == 0):
        continue

    pag = 2
    while True:
        print("pagina ", pag)
        url_page = url + "page/" + str(pag)
        try:
            procesados = procesar_elementos( url_page, categorias[categoria]["category"],  categoria  )
        except:
            break
        if procesados == 0:
            break
        pag = pag + 1

    path = 'salida/productos_cat'+fecha+'.json'
    with open(path, 'w') as file:
        json.dump(listado_productos, file)
        print('estado.json actualizado')