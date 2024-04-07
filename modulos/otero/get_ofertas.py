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

BRANCH_ID = 93
URL_BASE = "https://www.otero.com.ar"
URL = "https://www.otero.com.ar/tienda/whirlpool-special-days"

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

fecha = datetime.datetime.now().strftime("%Y%m%d")

listado_productos = []

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
        
        promocion = {
                        "orden":       0,
                        "titulo":      name,
                        "id_producto": 0,
                        "datos_extra": {},
                        "precio":      precio,
                        "branch_id":   BRANCH_ID,
                        "url":         enlace,
                        "key":         config["BACK_KEY"]
                    }
        print(promocion)
        enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar_oferta", json=promocion)
        print(enviar_back.json())
        print("")
        listado_productos.append(promocion)

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
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

    
print("haciendo petición a: ", URL)
driver.get(URL)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
res_consulta = driver.page_source

scroll_hasta_el_final(driver)

soup2 = BeautifulSoup(res_consulta, 'html.parser')
paginacion = soup2.find(class_="pagination_wrapper")

if (paginacion == None):
    print("No hay paginacion")
    procesar_resultados(res_consulta, "")
    exit()

paginas = paginacion.find_all("a")
if len(paginas) == 0:
    print("No hay paginacion")
    procesar_resultados(res_consulta, "")
    exit()

for pagina in paginas:
    print(pagina.get("href"))
    driver.get(url+pagina.get("href"))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
    res_consulta = driver.page_source
    
    scroll_hasta_el_final(driver)
    procesar_resultados(res_consulta, "")


path = 'salida/productos_ofertas_'+fecha+'.json'
with open(path, 'w') as file:
    json.dump(listado_productos, file)
    print(path,' actualizado')

print("obtenidos ", len(listado_productos), " productos")