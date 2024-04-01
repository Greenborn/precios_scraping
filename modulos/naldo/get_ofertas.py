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

URL = "https://www.naldo.com.ar/250?O=OrderByReleaseDateDESC&map=productClusterIds&page=1"

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

fecha = datetime.datetime.now().strftime("%Y%m%d")

listado_productos = []
descuentos_no_procesados = []

def procesar_resultados(res_consulta, categoria):
    soup = BeautifulSoup(res_consulta, 'html.parser')
    data_json = soup.find("script", {"type": "application/ld+json"})
    
    if (data_json == None):
        print("no se encontraron resultados")
        return 0
    
    data_json = json.loads(data_json.text)['itemListElement']

    for prd_data in data_json:
        _data = prd_data['item']

        if (len(_data["offers"]["offers"]) != 1):
            descuentos_no_procesados.append(prd_data)
            with open('tipos_descuentos.json', 'w') as file:
                json.dump(descuentos_no_procesados, file)
            continue

        precio = _data["offers"]["offers"][0]["price"]

        promocion = {
                    "orden":       0,
                    "titulo":      _data["name"],
                    "id_producto": 0,
                    #"datos_extra": { "promo_cnt": promo_cnt },
                    "datos_extra": { },
                    "precio":      float(precio),
                    "branch_id":   BRANCH_ID,
                    "url":         _data["@id"],
                    "key":         config["BACK_KEY"]
                }

        enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar_oferta", json=promocion)
        print(enviar_back.json())
        print(promocion)
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


print("haciendo petición a: ", URL)

try:
    driver.get(URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
    res_consulta = driver.page_source
except:
    print("error atajado")
    exit()

scroll_hasta_el_final(driver)
try:
    procesar_resultados(res_consulta, "")
except:
    print("error procesando")
    exit()

path = 'salida/productos_ofertas_'+fecha+'.json'
with open(path, 'w') as file:
    json.dump(listado_productos, file)
    print(path,' actualizado')