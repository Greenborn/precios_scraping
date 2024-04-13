#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json
from bs4 import BeautifulSoup
import sys

sys.path.insert(1, "./modulos")
from clientecoordinador import *
cliente = ClienteCoordinador()

BRANCH = 98
fecha = datetime.datetime.now().strftime("%Y%m%d")

for categoria in CATEGORIAS:
    print("Procesado categoria: ", categoria)
    url = CATEGORIAS[categoria]["url"]

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
                "category": CATEGORIAS[categoria]["category"],
                "key": CONFIG["BACK_KEY"]
            }
        except:
            print("producto", product_html, "no procesado")
            continue
        cliente.sio.emit('registrar_precio', producto)
        
        print(producto)
        print("")
