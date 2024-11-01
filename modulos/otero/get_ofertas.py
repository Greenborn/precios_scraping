#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
from bs4 import BeautifulSoup
import datetime
import sys

sys.path.insert(1, "./modulos")
from clientecoordinador import *
cliente = ClienteCoordinador()
from selenium_utils import *

BRANCH_ID = 93
URL_BASE = "https://www.otero.com.ar"
URL = "https://www.otero.com.ar/tienda/ofertas-destacadas"

fecha = datetime.datetime.now().strftime("%Y%m%d")

def procesar_resultados(res_consulta, categoria):
    soup = BeautifulSoup(res_consulta, 'html.parser')

    product_html = soup.find_all(class_="PRODUCT_BOX")
    for product in product_html:
        name = product.find("h3").text
        try:
            enlace = product.find(class_="box_data")
            enlace = enlace.find("a")
            enlace = URL_BASE + enlace.get("href")
            price = product.find(class_="precio-final")
            if (price == None):
                print("No se pudo procesar el precio")
                continue
            else:
                price = price.text
        except:
            print("No se pudo procesar el precio")
            continue

        try:
            precio = float(str(price).replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").strip())
        except:
            print("No se pudo procesar el precio", price)
            continue
        
        promocion = {
                        "orden":       0,
                        "titulo":      name,
                        "id_producto": 0,
                        "datos_extra": {},
                        "precio":      precio,
                        "branch_id":   BRANCH_ID,
                        "url":         enlace,
                        "key":         CONFIG["BACK_KEY"]
                    }
        print(promocion)
        cliente.sio.emit('registrar_oferta', promocion)
        print("")

driver = get_driver()
    
print("haciendo petición a: ", URL)
driver.get(URL)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
res_consulta = driver.page_source

scroll_hasta_el_final(driver)

soup2 = BeautifulSoup(res_consulta, 'html.parser')
paginacion = soup2.find(class_="pagination_wrapper")

if (paginacion == None):
    print("No hay paginacion")
    procesar_resultados(res_consulta, "")
    exit()

paginas = paginacion.find_all("a")
if len(paginas) == 0:
    print("No hay paginacion")
    procesar_resultados(res_consulta, "")
    exit()

for pagina in paginas:
    print(pagina.get("href"))
    driver.get(URL+pagina.get("href"))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
    res_consulta = driver.page_source
    
    scroll_hasta_el_final(driver)
    procesar_resultados(res_consulta, "")


