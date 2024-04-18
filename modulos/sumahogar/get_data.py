#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
from bs4 import BeautifulSoup
import datetime
import time
import sys

sys.path.insert(1, "./modulos")
from clientecoordinador import *
cliente = ClienteCoordinador()
from selenium_utils import *

BRANCH_ID = 92

fecha = datetime.datetime.now().strftime("%Y%m%d")

driver = get_driver()

for categoria in CATEGORIAS:
    if (categoria == CATEGORIA_INICIO or CATEGORIAS[categoria]["category"] == CATEGORIA_INICIO_ID):
        print(categoria, CATEGORIA_INICIO, CATEGORIA_INICIO_ID)
        PROCESAR = True
        continue
    
    if (PROCESAR == True):
        print("Procesado categoria: ",categoria)

        url = CATEGORIAS[categoria]['url']
        print("haciendo petición a: ", url)
        
        try:
            driver.get(url+"#/show-all")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
            time.sleep(3)
            res_consulta = driver.page_source
        except:
            print("error atajado")
            continue

        response = res_consulta

        soup = BeautifulSoup(response, 'html.parser')

        productos = soup.find_all(class_="product-container item")
        for prod in productos:
            name = prod.find(class_="product-name").text
            price = prod.find(class_="price").text
            try:
                precio = float(str(price).replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").strip())
            except:
                print("No se pudo procesar el precio", price)
                continue
            producto = {
                        "vendor_id": 58,
                        "name": categoria + ' - ' +name,
                        "price": precio,
                        "is_ext": "",
                        "url": prod.find(class_="product-name").get("href"),
                        "branch_id": BRANCH_ID,
                        "category": CATEGORIAS[categoria]["category"],
                        "key": CONFIG["BACK_KEY"]
                    }
            print(producto)
            cliente.sio.emit('registrar_precio', producto)
    else:
        print("ignorando categoria: ", categoria)
        continue
   
