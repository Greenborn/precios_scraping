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

BRANCH_ID = 91

fecha = datetime.datetime.now().strftime("%Y%m%d")

listado_productos = []
descuentos_no_procesados = []
producto_ya_listado = {}

def procesar_resultados(res_consulta, categoria):
    soup = BeautifulSoup(res_consulta, 'html.parser')

    data_json = soup.find("script", {"type": "application/ld+json"})
    all_json_data = soup.find_all("script", {"type": "application/ld+json"})
    #print(len(all_json_data))
    for json_d in all_json_data:
        #print(len(json_d.text), json_d.text)
        if (len(json_d.text) > 512):
            data_json = json_d
            break

    if (data_json == None):
        print("no se encontraron resultados")
        return 0
    
    data_json = json.loads(data_json.text)['itemListElement']

    for prd_data in data_json:
        _data = prd_data['item']

        if (not "offers" in _data):
            print("No se puede procesar")
            continue

        if (len(_data["offers"]["offers"]) != 1):
            descuentos_no_procesados.append(prd_data)
            with open('tipos_descuentos.json', 'w') as file:
                json.dump(descuentos_no_procesados, file)
            continue
        
        if (_data["name"] in producto_ya_listado):
            print("producto repetido")
            continue
        producto_ya_listado[_data["name"]] = 1

        precio = _data["offers"]["offers"][0]["price"]

        producto = {
                    "vendor_id": 58,
                    "name": categoria + ' - ' + _data["brand"]["name"] + " - " + _data["name"],
                    "price": precio,
                    "is_ext": "",
                    "branch_id": BRANCH_ID,
                    "category_name": categoria,
                    "category": CATEGORIAS[categoria]["category"],
                    "key": CONFIG["BACK_KEY"]
                }
        
        cliente.sio.emit('registrar_precio', producto)
        print(producto)
        print("")        

driver = get_driver()

for categoria in CATEGORIAS:
    if (categoria == CATEGORIA_INICIO or CATEGORIAS[categoria]["category"] == CATEGORIA_INICIO_ID):
        print(categoria, CATEGORIA_INICIO, CATEGORIA_INICIO_ID)
        PROCESAR = True
        continue

    if (PROCESAR == True):
        print("Procesado categoria: ",categoria)
        url = CATEGORIAS[categoria]['url']
        print("haciendo petición a: ", url)

        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
            res_consulta = driver.page_source
        except:
            print("error atajado")
            continue

        scroll_hasta_el_final(driver)
        #try:
        time.sleep(2)
        procesar_resultados(res_consulta, categoria)

    else:
        print("ignorando categoria: ", categoria)
        continue
