#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime
import time
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

BRANCH_ID = 56

parser = argparse.ArgumentParser()

parser.add_argument("--categoria_inicio", type=str, help="Categoria desde la cual se procesan resultados")
args = parser.parse_args()
categoria_inicio = args.categoria_inicio

fecha = datetime.datetime.now().strftime("%Y%m%d")
listado_productos = []

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#options.add_argument('--headless')

driver = webdriver.Chrome(options=options)

def scroll_hasta_el_final(driver):
    last_scroll_position = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        time.sleep(2)
        current_scroll_position = driver.execute_script("return window.pageYOffset")

        if current_scroll_position == last_scroll_position:
            break

        last_scroll_position = current_scroll_position

listado_productos = []
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
                        "category": categorias[categoria]["category"],
                        "key": config["BACK_KEY"]
                    }
        except:
            print("No se pudo procesar el elemento")
            continue
        
        print(producto)
        enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=producto)
        print(enviar_back.json())

        prod_log = producto
        prod_log["all_data"] = element
        listado_productos.append(prod_log)
        
        print("")

def hacer_clic_por_texto(driver, texto):
    try:
        elemento = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{texto}')]")))
        elemento.click()
    except:
        print("No se pudo hacer clic en el elemento")
    
driver.get("https://www.simplicity.com.ar/")
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
driver.execute_script("localStorage.setItem('regionId', 'U1cjc2ltcGxpY2l0eWFyc3VjMzM2');")
modal_state = '{"userId":null,"userAddresses":null,"userSelectedAddress":null,"sellerSelected":true,"selectedSeller":{"address":"9 de Julio 626","city":"Tandil","cost":false,"geo":"-59.1355249,-37.3255822","id":"b68e5807-da0f-11ed-83ab-0e85e0979699","name":"Simplicity Tandil [9 de Julio 626]","province":"Buenos Aires","pupId":"20336","type":"simplicity","whitelabel":"simplicityarsuc336","value":"Simplicity Tandil [9 de Julio 626]","label":"Simplicity Tandil [9 de Julio 626]"},"selectedPickupPoint":{"friendlyName":"Simplicity Tandil [9 de Julio 626]","address":{"addressType":"pickup","receiverName":null,"addressId":"20336","isDisposable":true,"postalCode":"7000","city":"Tandil","state":"Buenos Aires","country":"ARG","street":"9 de Julio","number":"626","neighborhood":null,"complement":null,"reference":null,"geoCoordinates":[-59.13552,-37.32558]},"additionalInfo":null,"id":"simplicityarsuc336_20336","businessHours":[{"DayOfWeek":1,"OpeningTime":"09:00:00","ClosingTime":"20:00:00"},{"DayOfWeek":2,"OpeningTime":"09:00:00","ClosingTime":"20:00:00"},{"DayOfWeek":3,"OpeningTime":"09:00:00","ClosingTime":"20:00:00"},{"DayOfWeek":4,"OpeningTime":"09:00:00","ClosingTime":"20:00:00"},{"DayOfWeek":5,"OpeningTime":"09:00:00","ClosingTime":"20:00:00"},{"DayOfWeek":6,"OpeningTime":"09:00:00","ClosingTime":"20:00:00"}],"idOrderForm":"Simplicity Tandil [9 de Julio 626]","pupId":"20336","whitelabel":"simplicityarsuc336"},"shippingType":"pickup","shippingExtraType":"2","hasExpress":false,"hasError":false,"hasBeenMerged":true,"shouldLoadAddress":false,"hasReloaded":true}'
driver.execute_script("localStorage.setItem('modalState', '"+modal_state+"');")

time.sleep(2)

procesar = True
print(categoria_inicio)

if (categoria_inicio != None):
    procesar = False

for categoria in categorias:
    path = 'salida/productos_cat'+fecha+'.json'
    url = categorias[categoria]['url']

    if (categoria == categoria_inicio):
        print(categoria, categoria_inicio)
        procesar = True
        continue

    if (procesar == True):
        print("haciendo petición a: ", url, procesar)
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
        
        scroll_hasta_el_final(driver)
        res_consulta = driver.page_source
        procesar_resultados(res_consulta, categoria)

        
    else:
        print("ignorando categoria: ", categoria)
        continue

    with open(path, 'w') as file:
        json.dump(listado_productos, file)
        print(path,' actualizado')

