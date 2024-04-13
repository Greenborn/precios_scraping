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

BRANCH_ID = 134

fecha = datetime.datetime.now().strftime("%Y%m%d")

def procesar_resultados(res_consulta):
    soup = BeautifulSoup(res_consulta, 'html.parser')

    product_html = soup.find_all(class_="js-item-product")
    for product in product_html:
        data_ = product.find("script").text

        try:
            data_ = json.loads( str(data_) )
        except:
            print("json no procesado")
            continue
        
        if "availability" in data_["offers"]:
            if (data_["offers"]["availability"] == "http://schema.org/OutOfStock"):
                print("Sin Stock")
                continue

        producto = {
                    "vendor_id": 58,
                    "name": data_["name"] + " - " + data_["description"],
                    "price": float(data_["offers"]["price"]),
                    "is_ext": "",
                    "branch_id": BRANCH_ID,
                    "url": data_["offers"]["url"],
                    #"all_data": data_,
                    "category": CATEGORIAS[categoria]["category"],
                    "key": CONFIG["BACK_KEY"]
                }
        cliente.sio.emit('registrar_precio', producto)
        print(producto)


driver = get_driver()

for categoria in CATEGORIAS:
    print("Procesado categoria: ",categoria)

    url = CATEGORIAS[categoria]['url']
    print("haciendo petición a: ", url)
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
    res_consulta = driver.page_source
    
    scroll_hasta_el_final(driver)
    procesar_resultados(res_consulta)
    
