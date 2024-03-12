#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime
import argparse

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

BRANCH_ID = 130
BASE_URL = "https://www.libreriatandil.com.ar/"

fecha = datetime.datetime.now().strftime("%Y%m%d")

listado_productos = []

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
                "key": config["BACK_KEY"]
            }
        except:
            continue
        cantidad = cantidad + 1
        enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=producto)
        print(enviar_back.json())
        listado_productos.append(producto)
        print(producto)
    return cantidad

procesar = True
print(categoria_inicio)

if (categoria_inicio != None):
    procesar = False

for categoria in categorias:
    url = categorias[categoria]['url']

    if (categoria == categoria_inicio):
        print(categoria, categoria_inicio)
        procesar = True
        continue

    if (procesar == True):
        procesar_elementos( url, categorias[categoria]["category"],  categoria )
    else:
        print("ignorando categoria: ", categoria)
        continue
    
    path = 'salida/productos_cat'+fecha+'.json'
    with open(path, 'w') as file:
        json.dump(listado_productos, file)
        print('estado.json actualizado')