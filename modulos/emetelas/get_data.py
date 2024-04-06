#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json
import socketio

BRANCH_ID = 83
fecha = datetime.datetime.now().strftime("%Y%m%d")

with open("../config.json", "r") as archivo:
    config = json.load(archivo)
    
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


with socketio.SimpleClient() as sio:
    sio.connect('http://localhost:7777')

    sio.emit('cliente_conectado')
    if (not sio.receive()[1]["status"]):
        print("Rechazado")
        exit()

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
                        "url": "https://emetelas.com.ar/"+prod["slug"],
                        "key": config["BACK_KEY"]
                    }
                    sio.emit('registrar_precio', producto)
                    listado_productos.append(producto)
                    print(producto)
                    print("")

    path = 'salida/productos_cat'+fecha+'.json'
    with open(path, 'w') as file:
        json.dump(listado_productos, file)
        print('estado.json actualizado')

    print("obtenidos ", len(listado_productos))