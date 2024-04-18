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

BRANCH_ID = 136
BASE_URL  = "https://www.bringeri.com.ar"
CP        = "7000"
fecha     = datetime.datetime.now().strftime("%Y%m%d")

driver = get_driver()

driver.get(BASE_URL)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
time.sleep(6)
modal = driver.find_elements("class name", "vtex-modal__modal")
inputs_modal = modal[0].find_elements("tag name", "input")
inputs_modal[0].send_keys( CP )
hacer_clic_por_texto(driver, 'Guardar')

time.sleep(15)

diccio_nombres = {}
def procesar_resultados(res_consulta, categoria):
    soup = BeautifulSoup(res_consulta, 'html.parser')
    cant = 0
    data_ = soup.find(class_="flex flex-column min-vh-100 w-100")
    if(data_ == None):
        return 0
    
    data_ = data_.find("script")
    if(data_ == None):
        return 0
    
    try:
        data_ = data_.text
        data_ = json.loads(data_)
    except:
        return 0
    
    data_ = data_["itemListElement"]
    
    for element in data_:
        try:
            item = element["item"]
        except:
            continue

        if (len(item["offers"]["offers"]) != 1):
            continue
        
        if (item["name"] in diccio_nombres):
            print("producto repetido")
            continue

        diccio_nombres[ item["name"] ] = True

        cant = cant + 1
        producto = {
                    "vendor_id": 58,
                    "name": categoria + " - " + item["name"],
                    "price": float(item["offers"]["offers"][0]["price"]),
                    "url": item["@id"],
                    "is_ext": "",
                    "branch_id": BRANCH_ID,
                    "category": CATEGORIAS[categoria]["category"],
                    "key": CONFIG["BACK_KEY"]
                }
        
        print(producto)
        cliente.sio.emit('registrar_precio', producto)
        prod_log = producto
        prod_log["all_data"] = element
        
        print("")

    return cant

for categoria in CATEGORIAS:
    if (categoria == CATEGORIA_INICIO or CATEGORIAS[categoria]["category"] == CATEGORIA_INICIO_ID):
        print(categoria, CATEGORIA_INICIO, CATEGORIA_INICIO_ID)
        PROCESAR = True
        continue    

    if (PROCESAR == True):
        url = CATEGORIAS[categoria]['url']
        print(categoria, url)
        page = 1
        while True:
            url_page = BASE_URL + url + "?page=" + str(page)
            driver.get(url_page)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
            
            res_consulta = driver.page_source
            if (procesar_resultados(res_consulta, categoria) == 0):
                break

            page = page + 1
    else:
        print("ignorando categoria: ", categoria)
        continue
