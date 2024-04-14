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

BRANCH_ID = 18
BASE_URL  = "https://www.vea.com.ar"
USER      = "ratertico@proton.me"
fecha     = datetime.datetime.now().strftime("%Y%m%d")

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
        
        if (item["name"] in diccio_nombres):
            print("producto repetido")
            continue

        diccio_nombres[ item["name"] ] = True

        cant = cant + 1
        producto = {
                    "vendor_id": 58,
                    "name": categoria + " - " + item["name"],
                    "price": float(item["offers"]["highPrice"]),
                    "url": item["@id"],
                    "is_ext": "",
                    "branch_id": BRANCH_ID,
                    "category": CATEGORIAS[categoria]["category"],
                    "key": CONFIG["BACK_KEY"]
                }
        cliente.sio.emit('registrar_precio', producto)
        print(producto)

        prod_log = producto
        prod_log["all_data"] = element
        
        print("")

    return cant

procesar = True
print(CATEGORIA_INICIO)

if (CATEGORIA_INICIO != None):
    procesar = False

for categoria in CATEGORIAS:
    url = CATEGORIAS[categoria]['url']
    path = 'salida/productos_cat'+fecha+'.json'
    print(categoria, url)

    if (categoria == CATEGORIA_INICIO):
        print(categoria, CATEGORIA_INICIO)
        procesar = True
        continue

    if (procesar == True):
        page = 1
        while True:
            url_page = url + "?page=" + str(page)
            driver.get(url_page)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
            time.sleep(2)
            res_consulta = driver.page_source
            if (procesar_resultados(res_consulta, categoria) == 0):
                break

            page = page + 1
    else:
        print("ignorando categoria: ", categoria)
        continue
