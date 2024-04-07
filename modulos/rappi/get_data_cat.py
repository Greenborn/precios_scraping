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
import csv
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

with open('locales.json', 'r') as file:
    locales = json.load(file)

with open(ruta_matchs_config, "r") as archivo:
    matchs = json.load(archivo)

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

parser = argparse.ArgumentParser()

parser.add_argument("--comercio", type=str, help="Comercio")
parser.add_argument("--categoria", type=int, help="Categoria")
parser.add_argument("--headless", type=str, help="Headless")

args = parser.parse_args()

comercio = args.comercio
headless = args.headless
categoria = args.categoria
VENDOR = 58

def scroll_hasta_el_final(driver):
    last_scroll_position = 0
    # Hacer scroll hasta el final de la página
    while True:
        # Mover el scroll hasta el final de la página actual
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        current_scroll_position = driver.execute_script("return window.pageYOffset")
        # Si no hay más contenido para mostrar (es decir, no se ha desplazado más), salir del bucle
        if current_scroll_position == last_scroll_position:
            break
        # Actualizar la última posición del scroll
        last_scroll_position = current_scroll_position

def obtener_contenido_por_clase(html, clase):
    soup = BeautifulSoup(html, 'html.parser')
    elementos = soup.find_all(class_=clase)
    if elementos:
        return [str(elemento) for elemento in elementos]
    else:
        return None
    
def obtener_enlaces_con_info(html):
    enlaces = []
    soup = BeautifulSoup(html, 'html.parser')
    elementos_enlace = soup.find_all('a')
    for enlace in elementos_enlace:
        url = enlace['href']
        nombre = enlace.text
        enlaces.append({
            "url": url,
            "nombre": nombre
        })
    return enlaces

def hacer_clic_por_texto(driver, texto):
    try:
        elemento = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{texto}')]")))
        elemento.click()
    except:
        print("No se pudo hacer clic en el elemento")

def obtener_elementos_sub_cat(html):
    elementos = []
    if (html == None):
        return []
    soup = BeautifulSoup(html, 'html.parser')
    elementos_con_data_qa = soup.find_all(attrs={"data-qa": lambda value: value and "product-item" in value})
    for elemento in elementos_con_data_qa:
        html_interno = str(elemento.contents)
        valor_data_qa = elemento.get("data-qa")
        titulo = elemento.find(attrs={"data-qa": "product-name"}).text if elemento.find(attrs={"data-qa": "product-name"}) else None
        descripcion = elemento.find(attrs={"data-qa": "product-description"}).text if elemento.find(attrs={"data-qa": "product-description"}) else None
        precio = elemento.find(attrs={"data-qa": "product-price"}).text if elemento.find(attrs={"data-qa": "product-price"}) else None
        
        elementos.append({
            #"html_interno": html_interno,
            "data_qa": valor_data_qa,
            "titulo": titulo,
            "descripcion": descripcion,
            "precio": precio
        })
    return elementos

url_categoria = BASE_URL + locales[comercio]["enlaces_categorias"][categoria]["url"]
print("Consultando URL:", url_categoria)

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
if (headless == 'true'):
    options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

driver.get(url_categoria)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
scroll_hasta_el_final(driver)

contenido_sub = driver.page_source
see_all = obtener_contenido_por_clase(contenido_sub,"wrapper-see-all")

path = 'salida/productos_cat'+fecha+'.json'

todos_los_productos = []
todos_los_descuentos = []
discounts_types = {}

for sub_cat in see_all:
    enlaces_cat = obtener_enlaces_con_info( sub_cat )
    
    for enlace_sub_cat in enlaces_cat:
        sub_cat_url = BASE_URL + enlace_sub_cat['url']
        print("-> sub categoria: "+ sub_cat_url)

        try:
            driver.delete_all_cookies()
            driver.execute_script("window.localStorage.clear()")
            driver.execute_script("window.sessionStorage.clear()")

            driver.get(sub_cat_url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))

            hacer_clic_por_texto(driver, 'Ver más')
            time.sleep(3)
        except:
            print("error!")
            continue

        contenido_sub_cat = driver.page_source

        soup = BeautifulSoup(contenido_sub_cat, 'html.parser')
        try:
            json_data = json.loads(soup.find("script", {"id": "__NEXT_DATA__"}).text)
        except:
            print("No se encontraron datos")
            exit()

        prods_data = json_data["props"]["pageProps"]["fallback"]
        for key in prods_data:
            prods_data = prods_data[key]
            break
        prods_data = prods_data["aisle_detail_response"]["data"]["components"]

        for comp_prod in prods_data:
            for prod in comp_prod["resource"]["products"]:
                #print(prod)
                nombre_categoria = prod["category_name"]
                solo_comercio = comercio.split("/")[-1]

                if prod["have_discount"]:
                    print("Es promocion")
                    if (prod["discount_type"] == "percentage"):
                        texto_descuento = ""
                        if (prod["discounts"]["pay_products"] == "1"):
                            texto_descuento = prod["discounts"]["earnings"]
                        elif (prod["discounts"]["pay_products"] == "2"):
                            texto_descuento = prod["discounts"]["earnings"] + " llevando 2 unidades "
                        else:
                            discounts_types[prod['id']] = prod["discounts"]
                            print("promocion descuento no contemplada")
                            discounts_types[prod["discount_type"]] = True
                            with open('tipos_descuentos.json', 'w') as file:
                                json.dump(discounts_types, file)
                            continue
                        promocion = {
                            "orden":       0,
                            "titulo":      texto_descuento + ' - ' + prod["name"] + " - " + prod["description"],
                            "id_producto": 0,
                            "datos_extra": { "promo_cnt": texto_descuento, "_data": prod["discounts"]  },
                            "datos_extra": {},
                            "precio":      float(prod["price"]),
                            "url":         sub_cat_url,
                            "key":         config["BACK_KEY"]
                        }
                        promocion['branch_id'] = matchs["comercios"][solo_comercio]
                        print(promocion)
                        sio.emit('registrar_oferta', promocion)
                        #enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar_oferta", json=promocion)
                        todos_los_descuentos.append(promocion)
                        #print(enviar_back.json())
                    else:
                        discounts_types[prod["discount_type"]] = True
                        with open('tipos_descuentos.json', 'w') as file:
                            json.dump(discounts_types, file)
                else:
                    nuevo_prod = {
                            "vendor_id": 58,
                            "name": prod["name"] + " - " + prod["description"],
                            "price": float(prod["price"]),
                            "url": sub_cat_url,
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
                    #enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=nuevo_prod)
                    #print(enviar_back.json())
                    sio.emit('registrar_precio', nuevo_prod)
                    todos_los_productos.append(nuevo_prod)
                    print("")

