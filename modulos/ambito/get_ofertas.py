#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

BRANCH_ID = 145

fecha = datetime.datetime.now().strftime("%Y%m%d")

listado_productos = []

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
                precio = float(art.find(class_="price").text.replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").replace(",", ".").strip())
                
                promo_cnt = art.find(class_="cataloglabel-top-right").find("span").text

                promocion = {
                    "orden":       0,
                    "titulo":      promo_cnt + ' -' + nombre,
                    "id_producto": 0,
                    #"datos_extra": { "promo_cnt": promo_cnt },
                    "datos_extra": {},
                    "precio":      precio,
                    "branch_id":   BRANCH_ID,
                    "url":         enlace.get("href"),
                    "key":         config["BACK_KEY"]
                }
            except:
                continue
            cantidad = cantidad + 1
            enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar_oferta", json=promocion)
            print(enviar_back.json())
            listado_productos.append(promocion)
            print(promocion)

        pagina = pagina + 1
    
    return cantidad


total = procesar_elementos( "https://www.pintureriasambito.com/descuentos-y-ofertas", "",  "" )

path = 'salida/promociones'+fecha+'.json'
with open(path, 'w') as file:
    json.dump(listado_productos, file)
    print('estado.json actualizado')

print(total)