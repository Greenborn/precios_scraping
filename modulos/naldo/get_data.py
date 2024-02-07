#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BRANCH_ID = 91

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

fecha = datetime.datetime.now().strftime("%Y%m%d")

listado_productos = []

def procesar_resultados(res_consulta, categoria):
    soup = BeautifulSoup(res_consulta, 'html.parser')
    products_html = soup.find_all(class_="vtex-search-result-3-x-galleryItem")
    
    for product_html in products_html:
        marca = product_html.find(class_="vtex-product-summary-2-x-productBrandName").text
        descr = product_html.find(class_="vtex-product-summary-2-x-productBrand").text
        price = product_html.find(class_="vtex-flex-layout-0-x-flexColChild--product-price-container-2").text

        try:
            precio = float(str(price).replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").strip())
        except:
            print("no se pudo convertir el precio")

        producto = {
                    "vendor_id": 58,
                    "name": categoria + ' - ' + marca + " - " + descr,
                    "price": precio,
                    "is_ext": "",
                    "branch_id": BRANCH_ID,
                    "category": categorias[categoria]["category"]
                }
        listado_productos.append(producto)
        print(producto)
        print("")

def scroll_hasta_el_final(driver):
    last_scroll_position = 0
    while True:
        # Mover el scroll hasta el final de la página actual
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        time.sleep(2)
        current_scroll_position = driver.execute_script("return window.pageYOffset")

        # Si no hay más contenido para mostrar (es decir, no se ha desplazado más), salir del bucle
        if current_scroll_position == last_scroll_position:
            break

        last_scroll_position = current_scroll_position

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

for categoria in categorias:
    print("Procesado categoria: ",categoria)

    url = categorias[categoria]['url']
    print("haciendo petición a: ", url)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
        res_consulta = driver.page_source
    except:
        print("error atajado")
        continue

    scroll_hasta_el_final(driver)
    try:
        procesar_resultados(res_consulta, categoria)
    except:
        print("error procesando")
        continue

    path = 'salida/productos_cat'+fecha+'.json'
    with open(path, 'w') as file:
        json.dump(listado_productos, file)
        print(path,' actualizado')