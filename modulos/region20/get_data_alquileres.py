#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime
import hashlib
import re

import time
import random

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://www.region20.com.ar"
URL      = BASE_URL + "/propiedades/departamento-alquiler.htm?action=listar_subcategorias_inmuebles&subcategoria=5&localidades_seleccionadas=134&precio_seleccionado_menor=&precio_seleccionado_mayor=&usuarios_seleccionados=&tipo_seleccionado=&tiendas_seleccionadas=&marcas_seleccionadas=&modelos_seleccionados=&anios_seleccionados=&combustible_seleccionado=&0km_seleccionado=&financiacion_seleccionada=&credito_seleccionado=&forma_pago_seleccionadas=&ambientes_seleccionadas=&dormitorios_seleccionadas=&banios_seleccionados=&aestrenar_seleccionado=&moneda=&txt_buscar=&fecha_seleccionada="
FECHA    = datetime.datetime.now().strftime("%Y%m%d")

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

print("haciendo petición a: ", URL)
driver.get(URL)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
response = driver.page_source


with open("../config.json", "r") as archivo:
    config = json.load(archivo)

soup = BeautifulSoup(response, 'html.parser')

articulos = soup.find_all(class_="aviso-galeria")

listado = []
for articulo in articulos:
    enlace = BASE_URL + articulo.find(class_="titulo-listado").find("a").get("href")

    time.sleep( random.randint(2, 3) )
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear()")
    driver.execute_script("window.sessionStorage.clear()")
    driver.get(enlace)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
    rta_post = driver.page_source

    post_soup = BeautifulSoup(rta_post, 'html.parser')
    #print(rta_post)
    locador = post_soup.find(class_="userName").text.strip()
    titulo  = post_soup.find(class_="highlightTitle").text.strip()

    try:
        precio  = post_soup.find(class_="precio").text

        moneda = "AR$"
        if ( "U$S" in precio ):
            moneda = "U$S"

        precio = precio.replace("$", "").replace(" ", "").replace("U", "").replace("S", "").replace(".", "").replace(",", ".").strip()
        precio = float(precio)
    except:
        print("no se pudo obtener el precio")
        continue

    especificaciones =  post_soup.find_all(class_="especificacion")

    obj_especificaciones = {}
    suma_especificaciones = ""
    for especificacion in especificaciones:
        key_especificacion = especificacion.find("span").text.strip().lower()
        key_especificacion = key_especificacion.replace("ü", "").replace("ñ", "n").replace("á", "a").replace("é", "e").replace("í", "i")
        key_especificacion = key_especificacion.replace("ó", "o").replace("ú", "u").replace(" ", "_").replace(".", "").replace(",", "__")
        obj_especificaciones[ key_especificacion ] = especificacion.find("p").text
        suma_especificaciones = suma_especificaciones + obj_especificaciones[ key_especificacion ]  + "|"

    if (precio < 10000 and moneda != "U$S"):
        print("precio invalido?", precio, moneda)
        continue

    datos_alquiler = {
        "titulo": titulo,
        "locador": locador,
        "url": enlace,
        "precio": precio,
        "moneda": moneda,
        "especificaciones": obj_especificaciones,
        "key": config["BACK_KEY"],
    }
    suma_campos = re.sub(r'[^a-zA-Z0-9]', '', titulo + locador + suma_especificaciones) 
    hash_ = hashlib.md5( str( suma_campos ).encode() ).hexdigest()
    datos_alquiler["hash"] = hash_
    print(suma_campos, hash_)
    listado.append( datos_alquiler )
    print( datos_alquiler )
    enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar_alquiler", json=datos_alquiler)
    print(enviar_back.json())
    print("")

path = 'salida/alquileres_'+FECHA+'.json'
with open(path, 'w') as file:
    json.dump(listado, file)
    print(path,' actualizado')


