import json
from bs4 import BeautifulSoup
import datetime
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BRANCH_ID = 92

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

fecha = datetime.datetime.now().strftime("%Y%m%d")

listado_productos = []

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

for categoria in categorias:
    print("Procesado categoria: ",categoria)

    url = categorias[categoria]['url']
    print("haciendo petición a: ", url)
    
    try:
        driver.get(url+"#/show-all")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
        time.sleep(3)
        res_consulta = driver.page_source
    except:
        print("error atajado")
        continue

    response = res_consulta

    soup = BeautifulSoup(response, 'html.parser')

    productos = soup.find_all(class_="product-container item")
    for prod in productos:
        name = prod.find(class_="product-name").text
        price = prod.find(class_="price").text
        try:
            precio = float(str(price).replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").strip())
        except:
            print("No se pudo procesar el precio", price)
            continue
        producto = {
                    "vendor_id": 58,
                    "name": categoria + ' - ' +name,
                    "price": precio,
                    "is_ext": "",
                    "branch_id": BRANCH_ID,
                    "category": categorias[categoria]["category"]
                }
        print(producto)
        listado_productos.append(producto)
    
    path = 'salida/productos_cat'+fecha+'.json'
    with open(path, 'w') as file:
        json.dump(listado_productos, file)
        print(path,' actualizado')
    
