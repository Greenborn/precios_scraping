#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json
from bs4 import BeautifulSoup

import socketio
sio = socketio.SimpleClient()
sio.connect('http://localhost:7777')

sio.emit('cliente_conectado')
if (not sio.receive()[1]["status"]):
    print("Rechazado")
    exit()

BRANCH = 98
fecha = datetime.datetime.now().strftime("%Y%m%d")

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

with open("../config.json", "r") as archivo:
    config = json.load(archivo)


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
                "category": categorias[categoria]["category"],
                "key": config["BACK_KEY"]
            }
        except:
            print("producto", product_html, "no procesado")
            continue
        sio.emit('registrar_precio', producto)
        
        print(producto)
        print("")
