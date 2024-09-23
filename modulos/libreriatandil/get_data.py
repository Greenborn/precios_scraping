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

BRANCH_ID = 130
BASE_URL = "https://www.libreriatandil.com.ar/"

fecha = datetime.datetime.now().strftime("%Y%m%d")

diccio_nam = {}

def procesar_elementos( url, cat_id, categoria ):
    cantidad = 0
    url = BASE_URL + url 
    print(url)

    response = requests.get(url)
    response = response.text
    soup = BeautifulSoup(response, 'html.parser')

    articulos = soup.find_all(class_="product")
    
    for art in articulos:
        
        if (art.find("h4") == None):
            continue
        nombre = categoria + ' - ' + art.find("h4").text
        if (nombre in diccio_nam):
            continue
        diccio_nam[nombre] = True
        try:
            producto = {
                "vendor_id": 58,
                "name": nombre,
                "url": BASE_URL + art.find("a").get("href").replace("../", ""),
                "price": float(art.find(class_="prize").text.replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").replace(",", ".").strip()),
                "is_ext": "",
                "branch_id": BRANCH_ID,
                "category": cat_id,
                "category_name": categoria,
                "key": CONFIG["BACK_KEY"]
            }
        except:
            continue
        cantidad = cantidad + 1
        
        cliente.sio.emit('registrar_precio', producto)
        print(producto)
    return cantidad

for categoria in CATEGORIAS:
    if (categoria == CATEGORIA_INICIO or CATEGORIAS[categoria]["category"] == CATEGORIA_INICIO_ID):
        print(categoria, CATEGORIA_INICIO, CATEGORIA_INICIO_ID)
        PROCESAR = True
        continue
    
    if (PROCESAR == True):
        url = CATEGORIAS[categoria]['url']
        procesar_elementos( url, CATEGORIAS[categoria]["category"],  categoria )
    else:
        print("ignorando categoria: ", categoria)
        continue