#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
from bs4 import BeautifulSoup
import time
import requests
import argparse
import socketio

sio = socketio.SimpleClient()
sio.connect('http://localhost:7777')

sio.emit('cliente_conectado')
if (not sio.receive()[1]["status"]):
    print("Rechazado")
    exit()

fecha = datetime.datetime.now().strftime("%Y%m%d")
BASE_URL = "https://www.rappi.com.ar"
ruta_matchs_config = "matchs_categoria_comercio.json"
path = 'salida/productos_cat'+fecha+'.json'

with open('locales_no_cat.json', 'r') as file:
    locales = json.load(file)

with open(ruta_matchs_config, "r") as archivo:
    matchs = json.load(archivo)

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

parser = argparse.ArgumentParser()

parser.add_argument("--comercio", type=int, help="Comercio")
parser.add_argument("--headless", type=str, help="Headless")

args = parser.parse_args()

headless = args.headless
comercio = args.comercio
VENDOR = 58


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

def obtener_contenido_por_id(html, id_):
    soup = BeautifulSoup(html, 'html.parser')
    elemento = soup.find(id=id_)
    if elemento:
        return str(elemento)
    else:
        return None
    
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
if (headless == 'true'):
    options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

url = locales[comercio]["url"]
print("Consultando URL:", url)

driver.get(url)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
time.sleep(3)  
scroll_hasta_el_final(driver)

contenido = driver.page_source
contenido = obtener_contenido_por_id(contenido, 'restaurantLayoutContainer')

todos_los_productos = []

ofertas_keys = {  }

if contenido != None:
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        json_data = json.loads(soup.find("script", {"id": "__NEXT_DATA__"}).text)
    except:
        print("No se encontraron datos")
        exit()

    prods_data = json_data["props"]["pageProps"]["fallback"]
    for key in prods_data:
        prods_data = prods_data[key]
        break
    prods_data = prods_data["corridors"]

    for pasillo in prods_data:
        nombre_categoria = pasillo["name"]
        for prod in pasillo["products"]:
            
            solo_comercio = url.split("/")[-1]

            if prod["discountInPercent"] != 0:
                print("Es promocion")
                
                promocion = {
                    "orden":       0,
                    "titulo":      prod["discountText"] + ' - ' + prod["name"] + " - " + prod["description"],
                    "id_producto": 0,
                    #"datos_extra": { "promo_cnt": promo_cnt },
                    "datos_extra": {},
                    "precio":      float(prod["price"]),
                    "url":         url+"?productDetail="+str(prod['id']),
                    "key":         config["BACK_KEY"]
                }
                promocion['branch_id'] = matchs["comercios"][solo_comercio]
                print(promocion)
                sio.emit('registrar_oferta', promocion)
                #enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar_oferta", json=promocion)
                #print(enviar_back.json())
            else:
                nuevo_prod = {
                        "vendor_id": 58,
                        "name": prod["name"] + " - " + prod["description"],
                        "price": float(prod["price"]),
                        "url": url+"?productDetail="+str(prod['id']),
                        "key": config["BACK_KEY"]
                    }
                nuevo_prod['branch_id'] = matchs["comercios"][solo_comercio]
                try:
                    nuevo_prod['category'] = matchs["categorias"][nombre_categoria]
                except:
                    with open("categorias.json", 'r') as file:
                        categorias = json.load(file)
                        if nombre_categoria in categorias:
                            nuevo_prod['category'] = categorias[nombre_categoria]["category"]
                        else:
                            nuevo_prod['category'] = matchs["categorias"]["no catalogado"]
                print(nuevo_prod)
                sio.emit('registrar_precio', nuevo_prod)
                #enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=nuevo_prod)
                #print(enviar_back.json())
            print("")

    try:
        with open(path, 'r') as file:
            todos_los_productos = todos_los_productos + json.load(file)
    except:
        print("No se pudo cargar archivo dump de productos catalogados")

    with open(path, 'w') as file:
        json.dump(todos_los_productos, file)
        todos_los_productos = []