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

BRANCH_ID = 88
URL_OFERTAS = "https://eltheamcomputacion.mitiendanube.com/outlet/"
    
fecha = datetime.datetime.now().strftime("%Y%m%d")

def procesar_resultados(res_consulta):
    soup = BeautifulSoup(res_consulta, 'html.parser')

    product_html = soup.find_all(class_="js-item-product")
    for product in product_html:
        data_ = product.find(attrs={"data-component": "structured-data.item"}).text

        try:
            data_ = json.loads( str(data_) )
        except:
            print("json no procesado")
            continue
        
        if "availability" in data_["offers"]:
            if (data_["offers"]["availability"] == "http://schema.org/OutOfStock"):
                print("Sin Stock")
                continue

        promocion = {
            "orden":       0,
            "titulo":      data_["name"] + " - " + data_["description"],
            "id_producto": 0,
            #"datos_extra": { "promo_cnt": promo_cnt },
            "datos_extra": {},
            "precio":      float(data_["offers"]["price"]),
            "branch_id":   BRANCH_ID,
            "url":         data_["offers"]["url"],
            "key":         CONFIG["BACK_KEY"]
        }

        cliente.sio.emit('registrar_oferta', promocion)
        print(promocion)
        print("")


driver = get_driver()

url = URL_OFERTAS
print("haciendo petición a: ", url)
driver.get(url)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
res_consulta = driver.page_source

scroll_hasta_el_final(driver)
procesar_resultados(res_consulta)

