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

BRANCH_ID = 91

URL = "https://www.naldo.com.ar/250?O=OrderByReleaseDateDESC&map=productClusterIds&page=1"


fecha = datetime.datetime.now().strftime("%Y%m%d")

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
                    "key":         CONFIG["BACK_KEY"]
                }
        cliente.sio.emit('registrar_oferta', promocion)
        print(promocion)
        print("")

driver = get_driver()

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
