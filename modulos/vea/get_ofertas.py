#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
from bs4 import BeautifulSoup
import datetime

import time
import sys

sys.path.insert(1, "../")
from clientecoordinador import *
cliente = ClienteCoordinador()
from selenium_utils import *


with open("../config.json", "r") as archivo:
    config = json.load(archivo)

BRANCH_ID = 18
BASE_URL  = "https://www.vea.com.ar"
USER      = "ratertico@proton.me"
fecha     = datetime.datetime.now().strftime("%Y%m%d")
URL_OFERTAS = "https://www.vea.com.ar/36637?map=productClusterIds"

driver = get_driver()

driver.get(BASE_URL)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))

time.sleep(3)

hacer_clic_por_texto(driver, 'Seleccioná tu Sucursal')
time.sleep(2)

inputs = driver.find_elements("tag name", "input")
inputs[1].send_keys( USER )
time.sleep(2)

modal = driver.find_elements("class name", "veaargentina-delivery-modal-1-x-container")
btn_modal = modal[0].find_elements("tag name", "button")
btn_modal[0].click()
time.sleep(6)

hacer_clic_por_texto(driver, 'Retiro en tienda')
time.sleep(6)
modal = driver.find_elements("class name", "veaargentina-delivery-modal-1-x-container")
inputs_modal = modal[0].find_elements("tag name", "select")

inputs_modal[0].send_keys("BUENOS AIRES")
time.sleep(1)
inputs_modal[1].send_keys("Vea Tandil")
time.sleep(1)

btn_modal = modal[0].find_elements("tag name", "button")
btn_modal[4].click()
time.sleep(15)

listado_productos = []

diccio_nombres = {}
def procesar_resultados(res_consulta, categoria):
    soup = BeautifulSoup(res_consulta, 'html.parser')
    cant = 0
    data_ = soup.find(class_="flex flex-column min-vh-100 w-100")
    if(data_ == None):
        print("no se encuentra contenedo resultados", data_)
        return 0
    
    data_ = data_.find("script")
    if(data_ == None):
        print("No se encuentra script")
        return 0
    
    try:
        data_ = data_.text
        data_ = json.loads(data_)
    except:
        print("No se pudo hacer json.loads")
        return 0
    
    data_ = data_["itemListElement"]
    
    for element in data_:
        try:
            item = element["item"]
        except:
            print("no se encuentra items en json")
            continue

        if (len(item["offers"]["offers"]) != 1):
            print("len offers: ", len(item["offers"]["offers"]))
            continue
        
        if (item["@id"] in diccio_nombres):
            print("producto repetido")
            continue

        diccio_nombres[ item["@id"] ] = True

        cant = cant + 1
        producto = {
                    "vendor_id": 58,
                    "name": item["name"],
                    "price": float(item["offers"]["offers"][0]["price"]),
                    "url": item["@id"],
                    "is_ext": "",
                    "branch_id": BRANCH_ID,
                    "key": config["BACK_KEY"]
                }
        
        print(item)
        print("")
        texto_descuento = ""
        promocion = {
                        "orden":       0,
                        "titulo":      texto_descuento + ' - ' + item["name"],
                        "id_producto": 0,
                        "datos_extra": { },
                        "precio":      float(item["offers"]["offers"][0]["price"]),
                        "branch_id":   BRANCH_ID,
                        "url":         item["@id"],
                        "key":         config["BACK_KEY"]
                    }
        print(promocion)

        prod_log = producto
        prod_log["all_data"] = element
        listado_productos.append(prod_log)
        
        print("")

    return cant




path = 'salida/productos_oferta_'+fecha+'.json'
    
page = 1
url = URL_OFERTAS
while True:
    url_page = url + "&page=" + str(page)
    print(url_page)
    driver.get(url_page)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
    time.sleep(2)
    res_consulta = driver.page_source
    if (procesar_resultados(res_consulta, "") == 0):
        break

    page = page + 1
    

with open(path, 'w') as file:
    json.dump(listado_productos, file)
    print(path,' actualizado')

print(len(listado_productos))