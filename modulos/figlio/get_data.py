#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json

BRANCH = 97
fecha = datetime.datetime.now().strftime("%Y%m%d")

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

url = 'https://pedidos.masdelivery.com/panel/lib/front-api.php'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json; charset=utf-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://pedidos.masdelivery.com',
    'Connection': 'keep-alive',
    'Referer': 'https://pedidos.masdelivery.com/figlio-premium',
    #'Cookie': 'PHPSESSID=u14enjieehctpo4dr8lu9ma2o9',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-GPC': '1',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'
}

data = '[{"action":"GetLocationMenu","data":{"location_id":3250,"timezone":"America/Argentina/Buenos_Aires","default_delivery_time_id":2,"markup":1}},{"action":"GetDiscount","data":{"location_id":3250,"order_date":null,"delivery_method":null,"timezone":"America/Argentina/Buenos_Aires","bin":null}}]'

response = requests.post(url, headers=headers, data=data)

respuesta = response.json()
respuesta = respuesta['GetLocationMenu']["currentMenu"]['dishes']

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

listado_productos = []
for prod in respuesta:

    categoria = categorias[prod['category_name']]["category"]
    producto = {
                    "vendor_id": 58,
                    "name": "HELADOS - " + prod['category_name'] + ' - ' + prod['name'],
                    "price": prod["price"],
                    "is_ext": prod["id"],
                    "branch_id": BRANCH,
                    "category": categoria,
                    "url": "https://pedidos.masdelivery.com/figlio-premium",
                    "key": config["BACK_KEY"]
                }
    enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=producto)
    print(enviar_back.json())
    listado_productos.append(producto)
    print(producto)

path = 'salida/productos_cat'+fecha+'.json'
with open(path, 'w') as file:
    json.dump(listado_productos, file)
    print(path,' actualizado')