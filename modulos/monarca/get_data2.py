#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
import datetime

URL_CATEGORIAS = "http://api.monarcadigital.com.ar/categories/struct?version=87ddd4f1-8d9b-4cbf-a677-07db09562e7c"

with open('data/matchs_categorias.json') as archivo_json:
    matchs = json.load(archivo_json)

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

fecha = datetime.datetime.now().strftime("%Y%m%d")
path = 'salida/productos_cat'+fecha+'.json'

productos = []
productos_no_publicados = []
VENDOR = 58
BRANCH = 1

for categoria in matchs:
    url_consulta_cat = "http://api.monarcadigital.com.ar/categories/"+categoria+"/products" 
    print("Consultando URL: ", url_consulta_cat )

    response = requests.get(url_consulta_cat)

    if not response.json():
        print('Se obtuvo respuesta vacía')
        continue

    response = response.json()
    for registro in response:
        
        if registro['status'] != "Publicado":
            print("No publicado")
            continue

        presentacion = ""
        if registro['presentation'] != None:
            presentacion = ' - ' + registro['presentation'].strip()
        producto = { 
            "name": registro['description'].strip() + ' - ' + registro['brand'].strip() + ' - ' + presentacion,
            "price": registro['price'],
            "vendor_id": VENDOR,
            "branch_id": BRANCH,
            "reg": registro,
            "category": matchs[str(registro['category']['id'])],
            "key": config["BACK_KEY"]
        }
        print(producto)
        enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=producto)
        print(enviar_back.json())
        productos.append(producto)

    with open(path, 'w') as file:
        json.dump(productos, file)

print("Productos a agregar: ", len(productos))
print("Productos no publicados: ", len(productos_no_publicados))
