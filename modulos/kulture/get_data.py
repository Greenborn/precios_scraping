#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
from bs4 import BeautifulSoup
import datetime
import sys

sys.path.insert(1, "./modulos")
from clientecoordinador import *
cliente = ClienteCoordinador()
from selenium_utils import *

BRANCH_ID = 90

fecha = datetime.datetime.now().strftime("%Y%m%d")

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
        
        if (str(data_["offers"]["price"]) == "0"):
            print("Sin Precio")
            continue

        producto = {
                    "vendor_id": 58,
                    "name": data_["name"] + " - " + data_["description"],
                    "price": float(data_["offers"]["price"]),
                    "url": data_["offers"]["url"],
                    "is_ext": "",
                    "branch_id": BRANCH_ID,
                    "all_data": data_,
                    "category": CATEGORIAS[categoria]["category"],
                    "category_name": categoria,
                    "key": CONFIG["BACK_KEY"]
                }
        cliente.sio.emit('registrar_precio', producto)
        print(producto)

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
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
        res_consulta = driver.page_source
        
        scroll_hasta_el_final(driver)
        procesar_resultados(res_consulta)
    else:
        print("ignorando categoria: ", categoria)
        continue
    
