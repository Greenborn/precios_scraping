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

BASE_URL = "https://tiendaschasqui.ar/csd/catalogo"

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

driver.get(BASE_URL)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))

res_consulta = driver.page_source

soup = BeautifulSoup(res_consulta, 'html.parser')
menu_ = soup.find(class_="productListLayout-nav")
menu_items = menu_.find_all("li")

def hacer_clic_por_texto(driver, texto):
    try:
        elemento = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{texto}')]")))
        elemento.click()
    except:
        print("No se pudo hacer clic en el elemento")

categorias = {}

for item in menu_items:
    print(item.text)
    categoria = item.text
    hacer_clic_por_texto(driver, categoria)

    categorias[categoria] = { "category":"", "sub_items": [], "url": driver.current_url }
    time.sleep(1)
    print("")

with open('categorias.json', 'w') as file:
    json.dump(categorias, file)
    print('categorias.json actualizado!')