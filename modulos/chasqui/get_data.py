#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime
import argparse
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

BRANCH_ID = 138
BASE_URL = "https://tiendaschasqui.ar/csd/catalogo"

fecha = datetime.datetime.now().strftime("%Y%m%d")

parser = argparse.ArgumentParser()

parser.add_argument("--categoria_inicio", type=str, help="Categoria desde la cual se procesan resultados")
args = parser.parse_args()
categoria_inicio = args.categoria_inicio


listado_productos = []
def get_cookies_header( cookies ):
    return '; '.join([f'{key}={value}' for key, value in cookies.items()]) 

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

def hacer_clic_por_texto(driver, texto):
    try:
        elemento = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{texto}')]")))
        elemento.click()
        return True
    except:
        print("No se pudo hacer clic en el elemento")
        return False

diccio_items = {}

procesar = True
print(categoria_inicio)

if (categoria_inicio != None):
    procesar = False

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

for categoria in categorias:
    url = categorias[categoria]['url']

    if (categoria == categoria_inicio):
        print(categoria, categoria_inicio)
        procesar = True
        continue

    if (procesar == True):
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))

        res_mas = True
        while res_mas:
            scroll_hasta_el_final(driver)
            res_mas = hacer_clic_por_texto(driver, 'Cargar más productos')

        res_consulta = driver.page_source
        soup = BeautifulSoup(res_consulta, 'html.parser')
        data_ = soup.find_all(class_="product-card")
        
        for prod in data_:
            try:
                name = prod.find(class_="product-details")
                name = name.find(class_="product-details__name").text.strip()

                price = prod.find(class_="product-details__price").text.replace(" ","").replace("$","").replace(".","").replace(",",".")

                producto = {
                        "vendor_id": 58,
                        "name": categoria + " - " + name,
                        "price": float(price),
                        "url": "https://tiendaschasqui.ar/csd/",
                        "is_ext": "",
                        "branch_id": BRANCH_ID,
                        "category": categorias[categoria]["category"],
                        "key": config["BACK_KEY"]
                    }
                print(producto)
                enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=producto)
                print(enviar_back.json())
                print("")
            except:
                continue

        print("")
    else:
        print("ignorando categoria: ", categoria)
        continue
    
    path = 'salida/productos_cat'+fecha+'.json'
    with open(path, 'w') as file:
        json.dump(listado_productos, file)
        print(path,' actualizado')