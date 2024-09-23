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
            "category_name": categoria,
            "key": CONFIG["BACK_KEY"]
        }
        cliente.sio.emit('registrar_precio', producto)
        cantidad = cantidad + 1
        print(producto)
    return cantidad


for categoria in CATEGORIAS:
    if (categoria == CATEGORIA_INICIO or CATEGORIAS[categoria]["category"] == CATEGORIA_INICIO_ID):
        print(categoria, CATEGORIA_INICIO, CATEGORIA_INICIO_ID)
        PROCESAR = True
        continue

    url = CATEGORIAS[categoria]['url']

    if (PROCESAR == True):
        procesados = procesar_elementos( url, CATEGORIAS[categoria]["category"],  categoria )
        if (procesados == 0):
            continue

        pag = 2
        while True:
            print("pagina ", pag)
            url_page = url + "page/" + str(pag)
            try:
                procesados = procesar_elementos( url_page, CATEGORIAS[categoria]["category"],  categoria  )
            except:
                break
            if procesados == 0:
                break
            pag = pag + 1

    else:
        print("ignorando categoria: ", categoria)
        continue