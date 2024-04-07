#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime
import argparse

import socketio

sio = socketio.SimpleClient()
sio.connect('http://localhost:7777')

sio.emit('cliente_conectado')
if (not sio.receive()[1]["status"]):
    print("Rechazado")
    exit()


parser = argparse.ArgumentParser()

parser.add_argument("--categoria_inicio", type=str, help="Categoria desde la cual se procesan resultados")
args = parser.parse_args()
categoria_inicio = args.categoria_inicio

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

BRANCH_ID = 127

fecha = datetime.datetime.now().strftime("%Y%m%d")

diccio_nam = {}

def procesar_elementos( url, cat_id, categoria ):
    cantidad = 0
    print(url)

    response = requests.get(url)
    response = response.text
    soup = BeautifulSoup(response, 'html.parser')

    articulos = soup.find_all("article")
    
    for art in articulos:
        nombre = categoria + ' - ' + art.find_all("a")[2].text
        if (nombre in diccio_nam):
            continue
        diccio_nam[nombre] = True

        try:
            precio = art.find_all("bdi")
            if len(precio) == 2:
                precio = precio[1].text.replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").replace(",", ".").strip()
            elif len(precio) == 1:
                precio = precio[0].text.replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").replace(",", ".").strip()
            else:
                print("No se puede determinar precio")
                continue
        except:
            print("Error al obtener precio")
            continue

        producto = {
            "vendor_id": 58,
            "name": nombre,
            "url": art.find_all("a")[2].get("href"),
            "price": float(precio),
            "is_ext": "",
            "branch_id": BRANCH_ID,
            "category": cat_id,
            "key": config["BACK_KEY"]
        }
        #enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=producto)
        #print(enviar_back.json())
        sio.emit('registrar_precio', producto)
        cantidad = cantidad + 1
        print(producto)
    return cantidad

procesar = True
print(categoria_inicio)

if (categoria_inicio != None):
    procesar = False

for categoria in categorias:
    if (categoria == categoria_inicio):
        print(categoria, categoria_inicio)
        procesar = True
        continue

    url = categorias[categoria]['url']

    if (procesar == True):
        procesados = procesar_elementos( url, categorias[categoria]["category"],  categoria )
        if (procesados == 0):
            continue

        pag = 2
        while True:
            print("pagina ", pag)
            url_page = url + "page/" + str(pag)
            try:
                procesados = procesar_elementos( url_page, categorias[categoria]["category"],  categoria  )
            except:
                break
            if procesados == 0:
                break
            pag = pag + 1

    else:
        print("ignorando categoria: ", categoria)
        continue