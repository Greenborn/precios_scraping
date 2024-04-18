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

BRANCH_ID = 56

fecha = datetime.datetime.now().strftime("%Y%m%d")

driver = get_driver()

def procesar_resultados(res_consulta, categoria):
    soup = BeautifulSoup(res_consulta, 'html.parser')

    data_ = soup.find(class_="flex flex-column min-vh-100 w-100")
    if(data_ == None):
        return
    
    try:
        data_ = data_.find("script").text
        if(data_ == None):
            return
    except:
        print("No se puede obtener json")
        return
    
    try:
        data_ = json.loads(data_)
    except:
        return
    
    data_ = data_["itemListElement"]

    for element in data_:
        try:
            item = element["item"]
        except:
            continue

        if (len(item["offers"]["offers"]) != 1):
            continue
        
        producto = {}
        try:
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
        except:
            print("No se pudo procesar el elemento")
            continue
        
        print(producto)
        cliente.sio.emit('registrar_precio', producto)

        prod_log = producto
        prod_log["all_data"] = element
        
        print("")

    
driver.get("https://www.simplicity.com.ar/")
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
driver.execute_script("localStorage.setItem('regionId', 'U1cjc2ltcGxpY2l0eWFyc3VjMzM2');")
modal_state = '{"userId":null,"userAddresses":null,"userSelectedAddress":null,"sellerSelected":true,"selectedSeller":{"address":"9 de Julio 626","city":"Tandil","cost":false,"geo":"-59.1355249,-37.3255822","id":"b68e5807-da0f-11ed-83ab-0e85e0979699","name":"Simplicity Tandil [9 de Julio 626]","province":"Buenos Aires","pupId":"20336","type":"simplicity","whitelabel":"simplicityarsuc336","value":"Simplicity Tandil [9 de Julio 626]","label":"Simplicity Tandil [9 de Julio 626]"},"selectedPickupPoint":{"friendlyName":"Simplicity Tandil [9 de Julio 626]","address":{"addressType":"pickup","receiverName":null,"addressId":"20336","isDisposable":true,"postalCode":"7000","city":"Tandil","state":"Buenos Aires","country":"ARG","street":"9 de Julio","number":"626","neighborhood":null,"complement":null,"reference":null,"geoCoordinates":[-59.13552,-37.32558]},"additionalInfo":null,"id":"simplicityarsuc336_20336","businessHours":[{"DayOfWeek":1,"OpeningTime":"09:00:00","ClosingTime":"20:00:00"},{"DayOfWeek":2,"OpeningTime":"09:00:00","ClosingTime":"20:00:00"},{"DayOfWeek":3,"OpeningTime":"09:00:00","ClosingTime":"20:00:00"},{"DayOfWeek":4,"OpeningTime":"09:00:00","ClosingTime":"20:00:00"},{"DayOfWeek":5,"OpeningTime":"09:00:00","ClosingTime":"20:00:00"},{"DayOfWeek":6,"OpeningTime":"09:00:00","ClosingTime":"20:00:00"}],"idOrderForm":"Simplicity Tandil [9 de Julio 626]","pupId":"20336","whitelabel":"simplicityarsuc336"},"shippingType":"pickup","shippingExtraType":"2","hasExpress":false,"hasError":false,"hasBeenMerged":true,"shouldLoadAddress":false,"hasReloaded":true}'
driver.execute_script("localStorage.setItem('modalState', '"+modal_state+"');")

time.sleep(2)

for categoria in CATEGORIAS:
    if (categoria == CATEGORIA_INICIO or CATEGORIAS[categoria]["category"] == CATEGORIA_INICIO_ID):
        print(categoria, CATEGORIA_INICIO, CATEGORIA_INICIO_ID)
        PROCESAR = True
        continue

    if (PROCESAR == True):
        url = CATEGORIAS[categoria]['url']

        print("haciendo petición a: ", url)
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
        
        scroll_hasta_el_final(driver)
        res_consulta = driver.page_source
        procesar_resultados(res_consulta, categoria)

    else:
        print("ignorando categoria: ", categoria)
        continue

