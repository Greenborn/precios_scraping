import requests
import datetime
import json

BRANCH_ID = 83
fecha = datetime.datetime.now().strftime("%Y%m%d")

categorias = [
    {
        "name": "hogar-y-decoracion",
        "category": 1151,
        "url": "https://api.emetelas.com.ar/api/v1/products?page=1&size=12000&sortBy=name&category=hogar-y-decoracion"
    },
    {
        "name": "manualidades-y-disfraces",
        "category": 1190,
        "url": "https://api.emetelas.com.ar/api/v1/products?page=1&size=12000&sortBy=name&category=manualidades-y-disfraces"
    },
    {
        "name": "indumentaria-y-confeccion",
        "category": 1189,
        "url": "https://api.emetelas.com.ar/api/v1/products?page=1&size=12000&sortBy=name&category=indumentaria-y-confeccion"
    },
    {
        "name": "para-el-bebe",
        "category": 1194,
        "url": "https://api.emetelas.com.ar/api/v1/products?page=1&size=12000&sortBy=name&category=para-el-bebe"
    }
]

listado_productos = []

for categoria in categorias:
    url = categoria["url"]
    categoria = categoria["category"]
    response = requests.get(url)

    if response.json():
        respuesta = response.json()
        respuesta = respuesta["data"]

        for prod in respuesta:
            if prod["status"] == "available":
                producto = {
                    "vendor_id": 58,
                    "name": prod["name"],
                    "price": prod["price"],
                    "is_ext": prod["id"],
                    "branch_id": BRANCH_ID,
                    "category": categoria,
                    "url": "https://emetelas.com.ar/"+prod["slug"]
                }
                listado_productos.append(producto)
                print(producto)

path = 'salida/productos_cat'+fecha+'.json'
with open(path, 'w') as file:
    json.dump(listado_productos, file)
    print('estado.json actualizado')