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

BRANCH_ID = 104

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

fecha = datetime.datetime.now().strftime("%Y%m%d")

listado_productos = []

def procesar_resultados(res_consulta, categoria):
    soup = BeautifulSoup(res_consulta, 'html.parser')

    product_html = soup.find_all(class_="col-lg-4 col-md-4 col-sm-6 col-xs-vista ga-impresion producto")
    for product in product_html:
        try:
            precio = product.get("precio")
            #precio = precio.replace("/u", "").replace("/kg", "").replace("$", "").replace(",", "").replace(".", "").strip()
        except:
            print("no se pudieron obtener datos")
            continue
        try:
            producto = {
                        "vendor_id": 58,
                        "name": categoria + " - " + product.get("nombre"),
                        "price": float(precio),
                        "is_ext": "",
                        "url": "https://www.siemprefarmacias.com.ar/" + product.find_all("a")[1].get("href"),
                        "branch_id": BRANCH_ID,
                        "category": categorias[categoria]["category"]
                    }
            listado_productos.append(producto)
        except:
            print("no se pudo obtner enlace")
            continue
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
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

def hacer_clic_por_texto(driver, texto):
    try:
        elemento = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{texto}')]")))
        elemento.click()
    except:
        print("No se pudo hacer clic en el elemento")
        return False
    return True

for categoria in categorias:
    print("Procesado categoria: ",categoria)

    url = categorias[categoria]['url']
    print("haciendo petición a: ", url)
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
    
    
    scroll_hasta_el_final(driver)
    while True:
        res = hacer_clic_por_texto(driver, 'Ver más productos')
        time.sleep(3)
        scroll_hasta_el_final(driver)
        if not res:
            break

    res_consulta = driver.page_source
    procesar_resultados(res_consulta, categoria)
    

    path = 'salida/productos_cat'+fecha+'.json'
    with open(path, 'w') as file:
        json.dump(listado_productos, file)
        print(path,' actualizado')