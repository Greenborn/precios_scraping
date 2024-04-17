#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json
from bs4 import BeautifulSoup

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BRANCH = 12
fecha = datetime.datetime.now().strftime("%Y%m%d")
BASE_URL = "https://www.carrefour.com.ar/"
USER = "ratertico@proton.me"
PASS = "Boteado67624"

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

def scroll_hasta_el_final(driver):
    last_scroll_position = 0
    while True:
        # Mover el scroll hasta el final de la página actual
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        time.sleep(2)
        current_scroll_position = driver.execute_script("return window.pageYOffset")

        # Si no hay más contenido para mostrar (es decir, no se ha desplazado más), salir del bucle
        if current_scroll_position == last_scroll_position:
            break

        last_scroll_position = current_scroll_position

def hacer_clic_por_texto(driver, texto):
    try:
        elemento = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{texto}')]")))
        elemento.click()
    except:
        print("No se pudo hacer clic en el elemento")

driver.get(BASE_URL)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))

time.sleep(3)

hacer_clic_por_texto(driver, 'SELECCIONÁ TIENDA')
time.sleep(3)

hacer_clic_por_texto(driver, 'Ingresar con mail y contraseña')
time.sleep(3)

inputs = driver.find_elements("tag name", "input")

inputs[1].send_keys( USER )
inputs[2].send_keys( PASS )
time.sleep(2)

hacer_clic_por_texto(driver, 'Entrar')
time.sleep(2)
hacer_clic_por_texto(driver, 'Aceptar Todo')
time.sleep(2)

hacer_clic_por_texto(driver, 'SELECCIONÁ TIENDA')
time.sleep(2)

hacer_clic_por_texto(driver, 'Retiro o Drive')
time.sleep(1)
hacer_clic_por_texto(driver, 'Continuar')
time.sleep(3)
hacer_clic_por_texto(driver, 'Supermercado')

time.sleep(100)
exit()

for categoria in categorias:
    url =  BASE_URL +categorias[categoria]['url']

    page = 1
    while True:
        url = url + "&page=" + str(page)
        url = url.replace("//", "/")

        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
        res_consulta = driver.page_source

        scroll_hasta_el_final(driver)

        time.sleep(5)        

        soup = BeautifulSoup(res_consulta, 'html.parser')

        products = soup.find_all("article")
        
        for product in products:
            print(product)
            print("")

        if (len(products) == 0):
            break
        page = page + 1

