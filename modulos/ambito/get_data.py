#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import datetime
import sys

sys.path.insert(1, "./modulos")
from clientecoordinador import *
cliente = ClienteCoordinador()

BRANCH_ID = 145

fecha = datetime.datetime.now().strftime("%Y%m%d")

diccio_nam = {}

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
                    "key": CONFIG["BACK_KEY"]
                }
            except:
                continue
            cantidad = cantidad + 1
            
            cliente.sio.emit('registrar_precio', producto)
            print("")
            print(producto)

        pagina = pagina + 1
    
    return cantidad

procesar = True
print(CATEGORIA_INICIO)

if (CATEGORIA_INICIO != None):
    procesar = False

total = 0
for categoria in CATEGORIAS:
    url = CATEGORIAS[categoria]['url']

    if (categoria == CATEGORIA_INICIO):
        print(categoria, CATEGORIA_INICIO)
        procesar = True
        continue

    if (procesar == True):
        total = total + procesar_elementos( url, CATEGORIAS[categoria]["category"],  categoria )
    else:
        print("ignorando categoria: ", categoria)
        continue

print(total)