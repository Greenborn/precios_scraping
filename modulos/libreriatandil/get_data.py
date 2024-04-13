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

parser = argparse.ArgumentParser()

parser.add_argument("--categoria_inicio", type=str, help="Categoria desde la cual se procesan resultados")
args = parser.parse_args()
categoria_inicio = args.categoria_inicio

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
                "key": CONFIG["BACK_KEY"]
            }
        except:
            continue
        cantidad = cantidad + 1
        
        cliente.sio.emit('registrar_precio', producto)
        print(producto)
    return cantidad

procesar = True
print(categoria_inicio)

if (categoria_inicio != None):
    procesar = False

for categoria in CATEGORIAS:
    url = CATEGORIAS[categoria]['url']

    if (categoria == categoria_inicio):
        print(categoria, categoria_inicio)
        procesar = True
        continue

    if (procesar == True):
        procesar_elementos( url, CATEGORIAS[categoria]["category"],  categoria )
    else:
        print("ignorando categoria: ", categoria)
        continue