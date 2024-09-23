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
        
        producto = {
                    "vendor_id": 58,
                    "name": categoria + ' - ' +name,
                    "price": precio,
                    "is_ext": "",
                    "url": enlace,
                    "branch_id": BRANCH_ID,
                    "category_name": categoria,
                    "category": CATEGORIAS[categoria]["category"],
                    "key": CONFIG["BACK_KEY"]
                }
        print(producto)
        cliente.sio.emit('registrar_precio', producto)

driver = get_driver()

for categoria in CATEGORIAS:
    if (categoria == CATEGORIA_INICIO or CATEGORIAS[categoria]["category"] == CATEGORIA_INICIO_ID):
        print(categoria, CATEGORIA_INICIO, CATEGORIA_INICIO_ID)
        PROCESAR = True
        continue
    
    if (PROCESAR == True):
        print("Procesado categoria: ",categoria)
        url = URL_BASE+CATEGORIAS[categoria]['url']
        print("haciendo petición a: ", url)
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
        res_consulta = driver.page_source
        
        scroll_hasta_el_final(driver)

        soup2 = BeautifulSoup(res_consulta, 'html.parser')
        paginacion = soup2.find(class_="pagination_wrapper")

        if (paginacion == None):
            print("No hay paginacion")
            procesar_resultados(res_consulta, categoria)
            continue
        paginas = paginacion.find_all("a")
        if len(paginas) == 0:
            print("No hay paginacion")
            procesar_resultados(res_consulta, categoria)
            continue

        for pagina in paginas:
            print(pagina.get("href"))
            driver.get(url+pagina.get("href"))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
            res_consulta = driver.page_source
            
            scroll_hasta_el_final(driver)
            procesar_resultados(res_consulta, categoria)
        

    else:
        print("ignorando categoria: ", categoria)
        continue