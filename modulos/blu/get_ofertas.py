#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime
import socketio

sio = socketio.SimpleClient()
sio.connect('http://localhost:7777')

sio.emit('cliente_conectado')
if (not sio.receive()[1]["status"]):
    print("Rechazado")
    exit()

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

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

            nombre = enlace.text.strip()
            if (enlace.text.strip() in diccio_nam):
                print("producto repetido")
                continue

            diccio_nam[nombre] = True

            try:
                precio = art.find(class_="price").text.strip().replace(".","").replace(",",".").replace("$","").replace(" ","")
                
                promocion = {
                    "orden":       0,
                    "titulo":      nombre,
                    "id_producto": 0,
                    #"datos_extra": { "promo_cnt": promo_cnt },
                    "datos_extra": {},
                    "precio":      float(precio),
                    "branch_id":   BRANCH_ID,
                    "url":         enlace.get("href"),
                    "key":         config["BACK_KEY"]
                }
            except:
                print("error al formatear producto")
                if (can_obtenidos < 2):
                    return cantidad
                continue

            #enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar_oferta", json=promocion)
            #print(enviar_back.json())
            sio.emit('registrar_oferta', promocion)
            print(promocion)
            print("")
            cantidad = cantidad + 1

        pagina = pagina + 1

procesar_elementos( "https://www.puntoblu.com.ar/blu-sale", "",  "" )
    