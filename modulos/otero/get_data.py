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
import argparse

import socketio
sio = socketio.SimpleClient()
sio.connect('http://localhost:7777')

sio.emit('cliente_conectado')
if (not sio.receive()[1]["status"]):
    print("Rechazado")
    exit()

BRANCH_ID = 93
URL_BASE = "https://www.otero.com.ar"

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

fecha = datetime.datetime.now().strftime("%Y%m%d")

parser = argparse.ArgumentParser()

parser.add_argument("--categoria_inicio", type=str, help="Categoria desde la cual se procesan resultados")
args = parser.parse_args()
categoria_inicio = args.categoria_inicio


def procesar_resultados(res_consulta, categoria):
    soup = BeautifulSoup(res_consulta, 'html.parser')

    product_html = soup.find_all(class_="PRODUCT_BOX")
    for product in product_html:
        name = product.find("h3").text
        try:
            enlace = product.find(class_="box_data")
            enlace = enlace.find("a")
            enlace = URL_BASE + enlace.get("href")
            price = product.find(class_="precio-final")
            if (price == None):
                print("No se pudo procesar el precio")
                continue
            else:
                price = price.text
        except:
            print("No se pudo procesar el precio")
            continue

        try:
            precio = float(str(price).replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").strip())
        except:
            print("No se pudo procesar el precio", price)
            continue
        
        producto = {
                    "vendor_id": 58,
                    "name": categoria + ' - ' +name,
                    "price": precio,
                    "is_ext": "",
                    "url": enlace,
                    "branch_id": BRANCH_ID,
                    "category": categorias[categoria]["category"],
                    "key": config["BACK_KEY"]
                }
        print(producto)
        sio.emit('registrar_precio', producto)
        #enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=producto)
        #print(enviar_back.json())

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

procesar = True
print(categoria_inicio)

if (categoria_inicio != None):
    procesar = False

for categoria in categorias:
    print("Procesado categoria: ",categoria)

    if (categoria == categoria_inicio):
        print(categoria, categoria_inicio)
        procesar = True
        continue
    
    if (procesar == True):
        url = URL_BASE+categorias[categoria]['url']
        print("haciendo petición a: ", url)
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
        res_consulta = driver.page_source
        
        scroll_hasta_el_final(driver)

        soup2 = BeautifulSoup(res_consulta, 'html.parser')
        paginacion = soup2.find(class_="pagination_wrapper")

        if (paginacion == None):
            print("No hay paginacion")
            procesar_resultados(res_consulta, categoria)
            continue
        paginas = paginacion.find_all("a")
        if len(paginas) == 0:
            print("No hay paginacion")
            procesar_resultados(res_consulta, categoria)
            continue

        for pagina in paginas:
            print(pagina.get("href"))
            driver.get(url+pagina.get("href"))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
            res_consulta = driver.page_source
            
            scroll_hasta_el_final(driver)
            procesar_resultados(res_consulta, categoria)
        

    else:
        print("ignorando categoria: ", categoria)
        continue