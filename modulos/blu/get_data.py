#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime
import sys

sys.path.insert(1, "./modulos")
from clientecoordinador import *
cliente = ClienteCoordinador()

BRANCH_ID = 139
BASE_URL = "https://www.puntoblu.com.ar/"

fecha = datetime.datetime.now().strftime("%Y%m%d")

diccio_nam = {}

def procesar_elementos( url, cat_id, categoria ):
    cantidad = 0
    pagina = 1

    while True:
        url_ = url + "?p=" + str(pagina)
        print(url_)

        response = requests.get(url_)
        response = response.text
        soup = BeautifulSoup(response, 'html.parser')

        articulos = soup.find_all(class_="product-item")
        can_obtenidos = len(articulos)
        if (can_obtenidos == 0):
            return cantidad
        print("cantidad ", can_obtenidos)

        for art in articulos:
            enlace = art.find(class_="product-item-link") 

            nombre = categoria + ' - ' + enlace.text.strip()
            if (enlace.text.strip() in diccio_nam):
                print("producto repetido")
                continue

            diccio_nam[nombre] = True

            try:
                precio = art.find(class_="price").text.strip().replace(".","").replace(",",".").replace("$","").replace(" ","")
                producto = {
                    "vendor_id": 58,
                    "name": nombre,
                    "url": enlace.get("href"),
                    "price": float(precio),
                    "is_ext": "",
                    "branch_id": BRANCH_ID,
                    "category": cat_id,
                    "key": CONFIG["BACK_KEY"]
                }
            except:
                print("error al formatear producto")
                if (can_obtenidos < 2):
                    return cantidad
                continue

            cliente.sio.emit('registrar_precio', producto)
            print(producto)
            print("")
            cantidad = cantidad + 1

        pagina = pagina + 1

procesar = True
print(CATEGORIA_INICIO)

if (CATEGORIA_INICIO != None):
    procesar = False

for categoria in CATEGORIAS:
    url = CATEGORIAS[categoria]['url']

    if (categoria == CATEGORIA_INICIO):
        print(categoria, CATEGORIA_INICIO)
        procesar = True
        continue

    if (procesar == True):
        procesar_elementos( url, CATEGORIAS[categoria]["category"],  categoria )
    else:
        print("ignorando categoria: ", categoria)
        continue
    