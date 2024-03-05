#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

BRANCH_ID = 137
BASE_URL  = "https://sampietroweb.com.ar"

fecha = datetime.datetime.now().strftime("%Y%m%d")

listado_productos = []

diccio_nam = {}

for categoria in categorias:
    id = categorias[categoria]['id']
    url = "https://sampietroweb.com.ar/Item/Search/?page=1&id="+str(id)+"&recsPerPage=2400&order=id&sort=False&itemtype=Category%2C%20Content%2C%20Product&term=&getFilterData=True&filters=&fields=Name"
    response = requests.get(url)

    response = response.text
    soup = BeautifulSoup(response, 'html.parser')

    articulos = soup.find_all("article")

    for articulo in articulos:
        enlace_cnt = articulo.find(class_="box_image")
        enlace     = enlace_cnt.find("a")

        nombre_cnt = articulo.find(class_="box_data")
        nombre     = nombre_cnt.find("h3").text.strip()

        if (nombre in diccio_nam):
            print("producto repetido", nombre)
            continue

        diccio_nam[nombre] = 1

        precio = articulo.find(class_="price_wrapper")
        if (precio is None):
            print("No se encuentra precio")
            continue
        
        precio = precio.find(class_="precio-final")
        if (precio is None):
            print("No se encuentra precio, no disponible?")
            continue

        precio = precio.text.replace(".", "").replace(",", ".").strip()

        producto = {
            "vendor_id": 58,
            "name": categoria + " - " + nombre,
            "url": BASE_URL + enlace.get("href"),
            "price": float(precio),
            "is_ext": "",
            "branch_id": BRANCH_ID,
            "category": categorias[categoria]["category"],
            "key": config["BACK_KEY"]
        }

        enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=producto)
        print(enviar_back.json())
        listado_productos.append(producto)

        print(producto)
        print("")

    path = 'salida/productos_cat'+fecha+'.json'
    with open(path, 'w') as file:
        json.dump(listado_productos, file)
        print(path,' actualizado')

