#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime


import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

BRANCH_ID = 18
BASE_URL  = "https://www.vea.com.ar"
USER      = "ratertico@proton.me"
fecha     = datetime.datetime.now().strftime("%Y%m%d")

def hacer_clic_por_texto(driver, texto):
    try:
        elemento = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{texto}')]")))
        elemento.click()
    except:
        print("No se pudo hacer clic en el elemento")

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

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

def procesar_resultados(res_consulta, categoria):
    soup = BeautifulSoup(res_consulta, 'html.parser')
    cant = 0
    data_ = soup.find(class_="flex flex-column min-vh-100 w-100")
    if(data_ == None):
        return 0
    
    data_ = data_.find("script").text
    if(data_ == None):
        return 0
    
    try:
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
        
        cant = cant + 1
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
        
        print(producto)
        enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=producto)
        print(enviar_back.json())

        prod_log = producto
        prod_log["all_data"] = element
        listado_productos.append(prod_log)
        
        print("")

    return cant

for categoria in categorias:
    url = categorias[categoria]['url']
    print(categoria, url)

    page = 1
    while True:
        url_page = url + "?page=" + str(page)
        driver.get(url_page)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
        
        res_consulta = driver.page_source
        if (procesar_resultados(res_consulta, categoria) == 0):
            break

        page = page + 1
    print("")