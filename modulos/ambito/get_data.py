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

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

BRANCH_ID = 145

fecha = datetime.datetime.now().strftime("%Y%m%d")

listado_productos = []

diccio_nam = {}

parser = argparse.ArgumentParser()

parser.add_argument("--categoria_inicio", type=str, help="Categoria desde la cual se procesan resultados")
args = parser.parse_args()
categoria_inicio = args.categoria_inicio

def procesar_elementos( url, cat_id, categoria ):
    cantidad = 0
    pagina   = 1
    

    diccio_cat_nam = {}

    while (True):
        response = requests.get(url+'?p='+str(pagina)+'&product_list_limit=64')
        print(url+'?p='+str(pagina)+'&product_list_limit=64')
        response = response.text
        soup = BeautifulSoup(response, 'html.parser')
        
        articulos = soup.find_all(class_="product-item-info")
        for art in articulos:
            
            if (art.find(class_="product-item-link") == None):
                continue
            enlace = art.find(class_="product-item-link")
            nombre = categoria + ' - ' + enlace.text.replace("\n", "")

            if (enlace.text in diccio_nam):
                return cantidad
            diccio_nam[enlace.text] = True

            if (enlace.text in diccio_cat_nam):
                return cantidad
            diccio_cat_nam[enlace.text] = True

            try:
                producto = {
                    "vendor_id": 58,
                    "name": nombre,
                    "url": enlace.get("href"),
                    "price": float(art.find(class_="price").text.replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").replace(",", ".").strip()),
                    "is_ext": "",
                    "branch_id": BRANCH_ID,
                    "category": cat_id,
                    "key": config["BACK_KEY"]
                }
            except:
                continue
            cantidad = cantidad + 1
            #enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=producto)
            sio.emit('registrar_precio', producto)
            print("")
            listado_productos.append(producto)
            print(producto)

        pagina = pagina + 1
    
    return cantidad

procesar = True
print(categoria_inicio)

if (categoria_inicio != None):
    procesar = False

total = 0
for categoria in categorias:
    url = categorias[categoria]['url']

    if (categoria == categoria_inicio):
        print(categoria, categoria_inicio)
        procesar = True
        continue

    if (procesar == True):
        total = total + procesar_elementos( url, categorias[categoria]["category"],  categoria )
    else:
        print("ignorando categoria: ", categoria)
        continue
    
    path = 'salida/productos_cat'+fecha+'.json'
    with open(path, 'w') as file:
        json.dump(listado_productos, file)
        print('estado.json actualizado')

print(total)