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

import argparse

BRANCH_ID = 91

parser = argparse.ArgumentParser()

parser.add_argument("--categoria_inicio", type=str, help="Categoria desde la cual se procesan resultados")
args = parser.parse_args()
categoria_inicio = args.categoria_inicio

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

fecha = datetime.datetime.now().strftime("%Y%m%d")

listado_productos = []
descuentos_no_procesados = []
producto_ya_listado = {}

def procesar_resultados(res_consulta, categoria):
    soup = BeautifulSoup(res_consulta, 'html.parser')

    data_json = soup.find("script", {"type": "application/ld+json"})
    all_json_data = soup.find_all("script", {"type": "application/ld+json"})
    #print(len(all_json_data))
    for json_d in all_json_data:
        #print(len(json_d.text), json_d.text)
        if (len(json_d.text) > 512):
            data_json = json_d
            break

    if (data_json == None):
        print("no se encontraron resultados")
        return 0
    
    data_json = json.loads(data_json.text)['itemListElement']

    for prd_data in data_json:
        _data = prd_data['item']

        if (not "offers" in _data):
            print("No se puede procesar")
            continue

        if (len(_data["offers"]["offers"]) != 1):
            descuentos_no_procesados.append(prd_data)
            with open('tipos_descuentos.json', 'w') as file:
                json.dump(descuentos_no_procesados, file)
            continue
        
        if (_data["name"] in producto_ya_listado):
            print("producto repetido")
            continue
        producto_ya_listado[_data["name"]] = 1

        precio = _data["offers"]["offers"][0]["price"]

        producto = {
                    "vendor_id": 58,
                    "name": categoria + ' - ' + _data["brand"]["name"] + " - " + _data["name"],
                    "price": precio,
                    "is_ext": "",
                    "branch_id": BRANCH_ID,
                    "category": categorias[categoria]["category"],
                    "key": config["BACK_KEY"]
                }
        sio.emit('registrar_precio', producto)
        #enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=producto)
        #print(enviar_back.json())
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
#options.add_argument('--headless')
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
        #try:
        time.sleep(2)
        procesar_resultados(res_consulta, categoria)
        """except Exception as e:
            print(e)
            print("error procesando")
            continue"""

    else:
        print("ignorando categoria: ", categoria)
        continue
