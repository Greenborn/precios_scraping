#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime
import re
import sys

sys.path.insert(1, "./modulos")
from clientecoordinador import *
cliente = ClienteCoordinador()

BRANCH_ID = 86

fecha = datetime.datetime.now().strftime("%Y%m%d")

listado_productos = []

diccio_prod = {}

page = 1
ciclar = True 
while ciclar:
    url = "https://www.langtecnologia.com.ar/promociones/vuelta-al-cole/" + "?&page=" + str(page)
    print("haciendo petición a: ", url)
    response = requests.get(url, 
                            headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0'})

    response = response.text

    soup = BeautifulSoup(response, 'html.parser')

    product_html = soup.find_all(class_="card-ecommerce")
    print("Cant Productos: ", len(product_html))

    if (len(product_html) == 0):
        print("Se terminaron las paginas")
        break

    for product in product_html:
        html_data = BeautifulSoup(str(product.contents), 'html.parser')
        precio = re.findall(r'\d+', html_data.find(class_="pecio_final").text)
        
        if len(precio) == 0:
            print("Precio invalido")
            continue

        precio = ''.join(precio)
        
        try:
            precio = precio.replace("/u", "").replace("/kg", "").replace("$", "").replace(",", "").strip()
            titulo = html_data.find(class_="card-title").text.strip()
            if titulo in diccio_prod:
                ciclar = False
                break
            diccio_prod[titulo] = True

            promocion = {
                    "orden":       0,
                    "titulo":      titulo,
                    "id_producto": 0,
                    #"datos_extra": { "promo_cnt": promo_cnt },
                    "datos_extra": {},
                    "precio":      float(precio),
                    "branch_id":   BRANCH_ID,
                    "url":         html_data.find(class_="card-title").find("a").get("href"),
                    "key":         CONFIG["BACK_KEY"]
                }
        except:
            print("error")
            continue

        cliente.sio.emit('registrar_oferta', promocion)
        listado_productos.append(promocion)
        print(promocion)
        print("")
    page = page +1

print(len(listado_productos))



