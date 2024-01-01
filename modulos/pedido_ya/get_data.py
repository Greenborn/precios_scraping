import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
from bs4 import BeautifulSoup
import time
import csv
import argparse


fecha = datetime.datetime.now().strftime("%Y%m%d")
path = 'salida/productos_cat'+fecha+'.json'

with open('locales.json', 'r') as file:
    locales = json.load(file)

parser = argparse.ArgumentParser()

parser.add_argument("--comercio", type=int, help="Comercio")

args = parser.parse_args()

comercio = args.comercio

local_data = locales[comercio]
print("Local conf: ", local_data)

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


options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'")

driver = webdriver.Chrome(options=options)

url = local_data["url"]
print("Consultando URL:", url)

driver.get(url)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
            
scroll_hasta_el_final(driver)

contenido = driver.page_source
soup = BeautifulSoup(contenido, 'html.parser')
secciones = soup.find_all(id="section__products")

for seccion in secciones:
    print(seccion)
    print("")
