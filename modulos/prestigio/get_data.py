#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

BRANCH_ID = 148
BASE_URL = "https://www.prestigio.com.ar"

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

fecha = datetime.datetime.now().strftime("%Y%m%d")


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
        print(url+'?page='+str(pagina))
        try:
            driver.get(url+'?page='+str(pagina))
        except:
            return cantidad
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
        response = driver.page_source
        soup = BeautifulSoup(response, 'html.parser')
        
        articulos = soup.find_all(class_="vtex-product-summary-2-x-container--default-shelf")
        if (len(articulos) == 0):
            print("no se encontraron mas productos")
            return cantidad
        
        for art in articulos:
            try:
                sub_name = art.find(class_="vtex-product-summary-2-x-productBrandName").text + art.find(class_="vtex-product-summary-2-x-productBrand--default-shelf-name").text
                nombre_prod = categoria + ' - ' + art.find(class_="vtex-product-summary-2-x-productBrandName").text
                nombre_prod = nombre_prod + " " + art.find(class_="vtex-product-summary-2-x-productBrand--default-shelf-name").text
                enlace = art.find("a")
                precio = art.find(class_="vtex-product-price-1-x-sellingPriceValue").text
                precio = float(precio.replace("$", "").replace(".", "").replace(",", ".").strip())

                if (sub_name in diccio_cat_nam):
                    print("Producto repetido")
                    return cantidad
                diccio_cat_nam[sub_name] = True

                producto = {
                        "vendor_id": 58,
                        "name": nombre_prod,
                        "url": BASE_URL + enlace.get("href"),
                        "price": precio,
                        "is_ext": "",
                        "branch_id": BRANCH_ID,
                        "category": cat_id,
                        "key": config["BACK_KEY"]
                    }
                print(producto)
                sio.emit('registrar_precio', producto)
                print("")
            except:
                print("error al procesar")
                continue

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

print(total)