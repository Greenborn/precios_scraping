#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

BRANCH_ID = 82

fecha = datetime.datetime.now().strftime("%Y%m%d")
BASE_URL = "https://golopolis.com.ar/app/"

listado_productos = []



url = "https://golopolis.com.ar/app/?action=products&promotionId=-1"
print("haciendo petición a: ", url)
response = requests.get(url, 
                        headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0'},
                        cookies={"suite-company-id":"21"})

response = response.text
soup = BeautifulSoup(response, 'html.parser')

product_html = soup.find_all(class_="product-item")
print("Cant Productos: ", len(product_html))

for product in product_html:
    html_data = BeautifulSoup(str(product.contents), 'html.parser')

    precio = html_data.find(class_="tt-price").text.replace("/u", "").replace("/kg", "").replace("$", "").replace(",", "").strip()

    notas = ""
    if (html_data.find(class_="tt-label-our-fatured") != None):
        notas = html_data.find(class_="tt-label-our-fatured").text

    promocion = {
                    "orden":       0,
                    "titulo":      html_data.find(class_="tt-title").text,
                    "id_producto": 0,
                    #"datos_extra": { "promo_cnt": promo_cnt },
                    "datos_extra": { "notas": notas },
                    "precio":      float(precio),
                    "branch_id":   BRANCH_ID,
                    "url":         BASE_URL + html_data.find(class_="tt-title").find("a").get("href"),
                    "key":         config["BACK_KEY"]
                }

    enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar_oferta", json=promocion)
    print(enviar_back.json())
    listado_productos.append(promocion)
    print(promocion)

path = 'salida/ofertas'+fecha+'.json'
with open(path, 'w') as file:
    json.dump(listado_productos, file)
    print('estado.json actualizado')

    print("")

print("Se obtuvieron ", len(listado_productos), " productos")

