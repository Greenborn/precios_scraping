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
        nombre = art.find_all("a")[2].text
        if (nombre in diccio_nam):
            continue
        diccio_nam[nombre] = True
        
        promo_cnt = art.find(class_="descuento-img").get("src").replace("https://www.masfarmacias.com/wp-content/themes/hello-theme-child-master/images/descuentos/","")
        promo_cnt = promo_cnt.replace(".png","")

        if len(promo_cnt) > 10:
            print("Descuento invalido")
            print("\n \n")
            continue

        if "segunda" in promo_cnt:
            promo_cnt = promo_cnt.replace("segunda", "") + '% en 2da Unidad'
        elif "x" in promo_cnt:
            promo_cnt = promo_cnt
        else:
            promo_cnt = promo_cnt + '%'

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
        promocion = {
                    "orden":       0,
                    "titulo":      promo_cnt + ' - ' + nombre,
                    "id_producto": 0,
                    "datos_extra": { "promo_cnt": promo_cnt },
                    "datos_extra": {  },
                    "precio":      float(precio),
                    "branch_id":   BRANCH_ID,
                    "url":         art.find_all("a")[2].get("href"),
                    "key":         CONFIG["BACK_KEY"]
                }
        
        cliente.sio.emit('registrar_oferta', promocion)

        cantidad = cantidad + 1
        print(promocion)
        print("")
    return cantidad

        
pag = 1
while True:
    print("pagina ", pag)
    url_page = "https://www.masfarmacias.com/ofertas/"+str(pag)+"/?rule_id=1365,1366,1367,1368,1369,1370,1371,1372,1373,1374,1375,1376,1377"
    try:
        procesados = procesar_elementos( url_page, "",  ""  )
    except:
        break
    if procesados == 0:
        break
    pag = pag + 1

    