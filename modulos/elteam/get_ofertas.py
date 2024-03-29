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

BRANCH_ID = 88
URL_OFERTAS = "https://eltheamcomputacion.mitiendanube.com/outlet/"

with open("../config.json", "r") as archivo:
    config = json.load(archivo)
    
fecha = datetime.datetime.now().strftime("%Y%m%d")

listado_productos = []

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
            "key":         config["BACK_KEY"]
        }

        enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar_oferta", json=promocion)
        print(enviar_back.json())
        listado_productos.append(promocion)
        print(promocion)
        print("")

def scroll_hasta_el_final(driver):
    last_scroll_position = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        time.sleep(2)
        current_scroll_position = driver.execute_script("return window.pageYOffset")

        if current_scroll_position == last_scroll_position:
            break

        last_scroll_position = current_scroll_position

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

url = URL_OFERTAS
print("haciendo petición a: ", url)
driver.get(url)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
res_consulta = driver.page_source

scroll_hasta_el_final(driver)
procesar_resultados(res_consulta)


path = 'salida/productos_ofertas_'+fecha+'.json'
with open(path, 'w') as file:
    json.dump(listado_productos, file)
    print(path,' actualizado')

print("obtenidos ", len(listado_productos))