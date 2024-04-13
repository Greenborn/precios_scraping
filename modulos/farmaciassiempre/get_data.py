#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import datetime
import time
import sys

sys.path.insert(1, "./modulos")
from clientecoordinador import *
cliente = ClienteCoordinador()
from selenium_utils import *

BRANCH_ID = 104

fecha = datetime.datetime.now().strftime("%Y%m%d")

ofertas_ = []

def procesar_resultados(res_consulta, categoria):
    soup = BeautifulSoup(res_consulta, 'html.parser')

    product_html = soup.find_all(class_="col-lg-4 col-md-4 col-sm-6 col-xs-vista ga-impresion producto")
    for product in product_html:
        try:
            precio = product.get("precio")
            #precio = precio.replace("/u", "").replace("/kg", "").replace("$", "").replace(",", "").replace(".", "").strip()
        except:
            print("no se pudieron obtener datos")
            continue

        if (product.find(class_="valor-anterior") != None):
            print("Oferta detectada!")
            ofertas_.append(product)
            continue

        try:
            producto = {
                        "vendor_id": 58,
                        "name": categoria + " - " + product.get("nombre"),
                        "price": float(precio),
                        "is_ext": "",
                        "url": "https://www.siemprefarmacias.com.ar/" + product.find_all("a")[1].get("href"),
                        "branch_id": BRANCH_ID,
                        "category": CATEGORIAS[categoria]["category"],
                        "key": CONFIG["BACK_KEY"]
                    }
            sio.emit('registrar_precio', producto)
        except:
            print("no se pudo obtner enlace")
            continue
        print(producto)

driver = get_driver()

def hacer_clic_por_texto(driver, texto):
    try:
        elemento = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{texto}')]")))
        elemento.click()
    except:
        print("No se pudo hacer clic en el elemento")
        return False
    return True

for categoria in CATEGORIAS:
    print("Procesado categoria: ",categoria)

    url = CATEGORIAS[categoria]['url']
    print("haciendo petición a: ", url)
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
    
    
    scroll_hasta_el_final(driver)
    while True:
        res = hacer_clic_por_texto(driver, 'Ver más productos')
        time.sleep(3)
        scroll_hasta_el_final(driver)
        if not res:
            break

    res_consulta = driver.page_source
    procesar_resultados(res_consulta, categoria)
    
print("ofertas ", len(ofertas_))