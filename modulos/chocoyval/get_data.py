#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import datetime
import sys
import json
#sys.path.insert(1, "../")
sys.path.insert(1, "./modulos")
from clientecoordinador import *
cliente = ClienteCoordinador()

BRANCH_ID = 152

fecha = datetime.datetime.now().strftime("%Y%m%d")

diccio_nam = {}

def procesar_elementos( url, cat_id, categoria ):
    cantidad = 0
    pagina   = 1
    
    diccio_cat_nam = {}

    while (True):
        response = requests.get(url+'page/'+str(pagina)+'/')
        print(url+'page/'+str(pagina)+'/')
        response = response.text
        soup = BeautifulSoup(response, 'html.parser')

        listado = soup.find(class_="js-product-table")
        if (listado == None):
            return cantidad
        articulos = listado.find_all(class_="js-item-product")
        
        for art in articulos:
            try:
                data_ = json.loads(art.find("script").text)
            except:
                print("no se encontro json")
                continue

            e_url = data_['mainEntityOfPage']["@id"]
            nombre = categoria + ' - ' + data_['name']
            precio = float(data_['offers']['price'])          

            if nombre in diccio_nam:
                print("producto repetido")
                return cantidad
            diccio_nam[nombre] = True

            if (precio == 0):
                continue

            producto = {
                "vendor_id": 58,
                "name": nombre,
                "url": e_url,
                "price": precio,
                "is_ext": "",
                "branch_id": BRANCH_ID,
                "category": cat_id,
                "key": CONFIG["BACK_KEY"]
            }
            cantidad = cantidad + 1
            print(producto)
            print("")
            cliente.sio.emit('registrar_precio', producto)

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