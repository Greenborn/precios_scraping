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
from selenium_utils import *

BRANCH_ID = 148
BASE_URL = "https://www.prestigio.com.ar"

driver = get_driver()

fecha = datetime.datetime.now().strftime("%Y%m%d")
diccio_nam = {}

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
                        "key": CONFIG["BACK_KEY"]
                    }
                print(producto)
                cliente.sio.emit('registrar_precio', producto)
                print("")
            except:
                print("error al procesar")
                continue

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