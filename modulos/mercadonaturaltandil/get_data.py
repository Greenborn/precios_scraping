#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime
import time
import sys

sys.path.insert(1, "./modulos")
from clientecoordinador import *
cliente = ClienteCoordinador()
from selenium_utils import *

BRANCH_ID = 94

fecha = datetime.datetime.now().strftime("%Y%m%d")

def procesar_resultados(res_consulta, categoria):
    soup = BeautifulSoup(res_consulta, 'html.parser')

    product_html = soup.find_all(class_="js-item-product")
    for product in product_html:
        try:
            precio = product.find(class_="js-price-display").text
            precio = precio.replace("/u", "").replace("/kg", "").replace("$", "").replace(",", "").replace(".", "").strip()
            precio = float(precio)/100
        except:
            print("no se pudieron obtener datos")
            continue

        producto = {
                    "vendor_id": 58,
                    "name": categoria + " - " + product.find(class_="js-item-name").text,
                    "price": precio,
                    "is_ext": "",
                    "url": product.find(class_="item-link").get("href"),
                    "branch_id": BRANCH_ID,
                    "category_name": categoria,
                    "category": CATEGORIAS[categoria]["category"],
                    "key": CONFIG["BACK_KEY"]
                }
        
        cliente.sio.emit('registrar_precio', producto)
        print(producto)

driver = get_driver()

for categoria in CATEGORIAS:
    if (categoria == CATEGORIA_INICIO or CATEGORIAS[categoria]["category"] == CATEGORIA_INICIO_ID):
        print(categoria, CATEGORIA_INICIO, CATEGORIA_INICIO_ID)
        PROCESAR = True
        continue

    if (PROCESAR == True):
        print("Procesado categoria: ",categoria)

        url = CATEGORIAS[categoria]['url']
        print("haciendo petición a: ", url)
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
        res_consulta = driver.page_source
        
        scroll_hasta_el_final(driver)
        procesar_resultados(res_consulta, categoria)
    else:
        print("ignorando categoria: ", categoria)
        continue
