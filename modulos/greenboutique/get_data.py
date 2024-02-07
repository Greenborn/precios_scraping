#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json
from bs4 import BeautifulSoup
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BRANCH_ID = 95
fecha = datetime.datetime.now().strftime("%Y%m%d")

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

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

todos_resultados = []
def procesar_productos( products_html ):
    for product_html in products_html:
        
        enlace = product_html.find("a", class_="js-item-name")
        if (enlace == None):
            print("No se encontro el enlace")
            print(product_html)
            continue
        
        precio = product_html.find("span", class_="js-price-display").text
        try:
            precio = float(precio.replace("$", "").replace(".", "").split(",")[0])
        except:
            print(precio," Precio invalido ")
            continue

        producto = {
                    "vendor_id": 58,
                    "name": categoria + ' - ' + enlace.get("title").strip(),
                    "price": precio,
                    "is_ext": "",
                    "url": enlace.get("href"),
                    "branch_id": BRANCH_ID,
                    "category": categorias[categoria]["category"],
                    "key": config["BACK_KEY"]
                }
        enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=producto)
        print(enviar_back.json())
        print(producto)
        todos_resultados.append(producto)

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless')

driver = webdriver.Chrome(options=options)

for categoria in categorias:
    print("Procesado categoria: ", categoria)
    url = categorias[categoria]["url"]

    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
    res_consulta = driver.page_source

    scroll_hasta_el_final(driver)

    soup = BeautifulSoup(res_consulta, 'html.parser')
    products_html = soup.find_all(class_="js-product-container")
    procesar_productos( products_html )

path = 'salida/productos_cat'+fecha+'.json'
with open(path, 'w') as file:
    json.dump(todos_resultados, file)
    print(path,' actualizado')
