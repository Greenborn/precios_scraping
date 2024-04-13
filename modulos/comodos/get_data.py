#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import time
from bs4 import BeautifulSoup
import datetime
import sys 

sys.path.insert(1, "../")
from clientecoordinador import *
cliente = ClienteCoordinador()
from selenium_utils import *


BRANCH_ID = 151

fecha = datetime.datetime.now().strftime("%Y%m%d")

diccio_nam = {}

driver = get_driver()

def procesar_elementos( url, cat_id, categoria ):
    cantidad = 0
    diccio_cat_nam = {}
    
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
    time.sleep(1)

    scroll_hasta_el_final(driver)

    response = driver.page_source

    soup = BeautifulSoup(response, 'html.parser')
    articulos = soup.find_all(class_="type-product")
    for art in articulos:
        script = art.find("script").text.split("] = ")[1].split(";")[0]
        script = json.loads(script)
        
        enlace = art.find("a")

        try:
            producto = {
                "vendor_id": 58,
                "name": categoria + ' - ' + script['name'] + ' - ' + art.find(class_="sfida-descrp-price").text,
                "url": enlace.get("href"),
                "price": float(script['price']),
                "is_ext": "",
                "branch_id": BRANCH_ID,
                "category": cat_id,
                "key": CONFIG["BACK_KEY"]
            }
        except:
            continue
        cantidad = cantidad + 1
        cliente.sio.emit('registrar_precio', producto)
        print(producto)
        print("")
    
    return cantidad

procesar = True
print(CATEGORIA_INICIO)

if (CATEGORIA_INICIO != None):
    procesar = False

total = 0
for categoria in CATEGORIAS:
    url = CATEGORIAS[categoria]['url']

    if (categoria == CATEGORIA_INICIO):
        print(categoria, CATEGORIA_INICIO)
        procesar = True
        continue

    if (procesar == True):
        total = total + procesar_elementos( url, CATEGORIAS[categoria]["category"],  categoria )
    else:
        print("ignorando categoria: ", categoria)
        continue

print(total)