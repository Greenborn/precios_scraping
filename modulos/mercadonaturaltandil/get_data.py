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

import socketio
sio = socketio.SimpleClient()
sio.connect('http://localhost:7777')

sio.emit('cliente_conectado')
if (not sio.receive()[1]["status"]):
    print("Rechazado")
    exit()
BRANCH_ID = 94

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

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
                    "category": categorias[categoria]["category"],
                    "key": config["BACK_KEY"]
                }
        #enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=producto)
        #print(enviar_back.json())
        sio.emit('registrar_precio', producto)
        print(producto)

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
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

for categoria in categorias:
    print("Procesado categoria: ",categoria)

    url = categorias[categoria]['url']
    print("haciendo petición a: ", url)
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
    res_consulta = driver.page_source
    
    scroll_hasta_el_final(driver)
    procesar_resultados(res_consulta, categoria)
