
import json
import requests
from bs4 import BeautifulSoup
import datetime

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

BRANCH_ID = 133
BASE_URL = "https://fava.com.ar"

fecha = datetime.datetime.now().strftime("%Y%m%d")

listado_productos = []

diccio_nam = {}

headers_ = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://fava.com.ar",
    "Referer": ""
}

def get_cookies_header( cookies ):
    return '; '.join([f'{key}={value}' for key, value in cookies.items()]) 

diccio_items = {}

def procesar_elementos( url, cat_id, categoria, cookies_ ):
    cantidad = 0

    pagina = 1
    headers_["Referer"] = url + "?"
    headers_["Cookie"] = get_cookies_header( cookies_ )
    
    cantidad_paginas = 999

    while pagina <= cantidad_paginas:
        url_ = url + "?___SID=U&ajaxcatalog=true&p=" + str(pagina)
        print("Probando: ",url_)

        response = requests.post(url_, cookies=cookies_, headers=headers_)
        response = response.json()
        response = response["productlist"]

        soup = BeautifulSoup(response, 'html.parser')
        items = soup.find_all(class_="item")

        if len(items) == 0:
            return cantidad
        
        paginador = soup.find(class_="pages")
        if (paginador == None):
            cantidad_paginas = 1
        else:
            cantidad_paginas = int(paginador.find_all("li")[-2].text.strip())
            
        print("cantidad de paginas: ", cantidad_paginas)
        for item in items:
            enlace = item.find("a")
            name = enlace.get("title").strip()

            precio = -1
            try:
                precio = item.find(class_="price").text.strip()
                precio = float(precio.replace("/u", "").replace("/kg", "").replace("$", "").replace(",", ".").replace(".", ""))
            except:
                print("No se pudo procesar el precio")
                continue

            if name in diccio_items:
                print("Producto repetido: ", name)
            else:
                diccio_items[name] = 1

                producto = {
                            "vendor_id": 58,
                            "name": categoria + ' - ' +name,
                            "price": precio,
                            "is_ext": "",
                            "url": enlace.get("href"),
                            "branch_id": BRANCH_ID,
                            "category": cat_id
                        }
                print(producto)
                cantidad = cantidad + 1
                listado_productos.append(producto)

        pagina = pagina + 1

response = requests.get(BASE_URL)
cookies = response.cookies

for categoria in categorias:
    url = categorias[categoria]['url']

    procesar_elementos( url, categorias[categoria]["category"],  categoria, cookies )
    
    path = 'salida/productos_cat'+fecha+'.json'
    with open(path, 'w') as file:
        json.dump(listado_productos, file)
        print(path,' actualizado')