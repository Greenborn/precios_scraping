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

BRANCH_ID = 135

fecha = datetime.datetime.now().strftime("%Y%m%d")
BASE_URL = "https://www.pchome.com.ar/app/"

listado_productos = []

for categoria in categorias:
    print("Procesado categoria Nivel 0: ",categoria)

    for sub_categoria in categorias[categoria]['sub_items']:
        texto_sub_cat = sub_categoria['texto']
        print("----> Procesando sub categoría: ",texto_sub_cat)

        url = sub_categoria["url"]
        print("haciendo petición a: ", url)
        response = requests.get(url, 
                                headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0'},
                                cookies={"suite-company-id":"48"})

        response = response.text
        soup = BeautifulSoup(response, 'html.parser')

        product_html = soup.find_all(class_="tt-product")
        print("Cant Productos: ", len(product_html))

        for product in product_html:
            html_data = BeautifulSoup(str(product.contents), 'html.parser')
            producto = {
                "vendor_id": 58,
                "name": html_data.find(class_="tt-title").text,
                "price": float(html_data.find(class_="tt-price").text.replace("/u", "").replace("/kg", "").replace("$", "").replace(",", "").strip()),
                "is_ext": "",
                "branch_id": BRANCH_ID,
                "category": sub_categoria["category"],
                "url": BASE_URL + html_data.find(class_="tt-title").find("a").get("href"),
                "key": config["BACK_KEY"]
            }
            enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=producto)
            print(enviar_back.json())
            listado_productos.append(producto)
            print(producto)
        path = 'salida/productos_cat'+fecha+'.json'
        with open(path, 'w') as file:
            json.dump(listado_productos, file)
            print('estado.json actualizado')

    print("")

print("Se obtuvieron ", len(listado_productos), " productos")

