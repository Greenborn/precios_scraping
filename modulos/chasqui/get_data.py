#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime
import argparse
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import socketio
sio = socketio.SimpleClient()
sio.connect('http://localhost:7777')

sio.emit('cliente_conectado')
if (not sio.receive()[1]["status"]):
    print("Rechazado")
    exit()

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

BRANCH_ID = 138
BASE_URL = "https://tiendaschasqui.ar/csd/catalogo"

fecha = datetime.datetime.now().strftime("%Y%m%d")

parser = argparse.ArgumentParser()

parser.add_argument("--categoria_inicio", type=str, help="Categoria desde la cual se procesan resultados")
args = parser.parse_args()
categoria_inicio = args.categoria_inicio

def get_cookies_header( cookies ):
    return '; '.join([f'{key}={value}' for key, value in cookies.items()]) 

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
        return True
    except:
        print("No se pudo hacer clic en el elemento")
        return False

diccio_items = {}

procesar = True
print(categoria_inicio)

if (categoria_inicio != None):
    procesar = False

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

diccio_prods_name = {}

for categoria in categorias:
    url = categorias[categoria]['url']

    if (categoria == categoria_inicio):
        print(categoria, categoria_inicio)
        procesar = True
        continue

    if (procesar == True):
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))

        res_consulta = driver.page_source
        time.sleep(3)
        auth_token = driver.execute_script("return sessionStorage.getItem('authToken')")
        
        headers_ = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/123.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://tiendaschasqui.ar",
            "vendure-token": "csd",
            "authorization": "Bearer " + auth_token,
            "Connection": "keep-alive",
            "Referer": url
        }

        url_api = "https://tiendaschasqui.ar/shop-api"
        cat_slug = url.split("/")
        cat_slug = cat_slug[len(cat_slug)-1]
        response_cat_d = requests.post(url_api, headers=headers_, json=
            {
                "operationName":"GetCollection",
                "variables":{"slug":cat_slug},
                "query":"query GetCollection($id: ID, $slug: String) {\n  collection(id: $id, slug: $slug) {\n    id\n    name\n    slug\n    description\n    featuredAsset {\n      ...Asset\n      __typename\n    }\n    breadcrumbs {\n      id\n      slug\n      name\n      __typename\n    }\n    children {\n      id\n      slug\n      featuredAsset {\n        ...Asset\n        __typename\n      }\n      name\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment Asset on Asset {\n  id\n  width\n  height\n  name\n  preview\n  focalPoint {\n    x\n    y\n    __typename\n  }\n  __typename\n}\n"
            })
        
        response_cat_d = response_cat_d.json()
        id_colection = response_cat_d['data']['collection']['id']
        
        response = requests.post(url_api, headers=headers_, json = 
            {
                "operationName":"SearchProducts",
                "variables":{
                    "input":{
                        "term":"","groupByProduct":True,
                        "collectionId":id_colection,
                        "facetValueFilters":[],
                        "take":1200,"skip":0,"sort":{"price":"ASC"}
                    }
                },
                "query":"query SearchProducts($input: SearchInput!) {\n  search(input: $input) {\n    items {\n      productVariantId\n      productId\n      slug\n      productName\n      description\n      facetValueIds\n      inStock\n      priceWithTax {\n        ... on PriceRange {\n          min\n          max\n          __typename\n        }\n        __typename\n      }\n      productAsset {\n        id\n        preview\n        focalPoint {\n          x\n          y\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    totalItems\n    facetValues {\n      count\n      facetValue {\n        id\n        name\n        code\n        facet {\n          id\n          name\n          code\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
            })
        data_items = response.json()
        data_items = data_items["data"]["search"]["items"]
        
        for prod in data_items:
            try:
                headers_["Referer"] = "https://tiendaschasqui.ar/csd/producto/"+prod["slug"]
                response_prod = requests.post(url_api, headers=headers_, json = 
                    {
                        "operationName":"GetProductDetail",
                        "variables":{"slug":prod["slug"]},
                        "query":"query GetProductDetail($slug: String!) {\n  product(slug: $slug) {\n    id\n    name\n    description\n    slug\n    variants {\n      id\n      name\n      options {\n        code\n        name\n        __typename\n      }\n      price\n      priceWithTax\n      sku\n      stockLevel\n      __typename\n    }\n    featuredAsset {\n      ...Asset\n      __typename\n    }\n    assets {\n      ...Asset\n      __typename\n    }\n    collections {\n      id\n      slug\n      breadcrumbs {\n        id\n        name\n        slug\n        __typename\n      }\n      __typename\n    }\n    facetValues {\n      name\n      code\n      __typename\n    }\n    customFields {\n      productor {\n        id\n        name\n        localidad\n        provincia\n        descriptionOffered\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment Asset on Asset {\n  id\n  width\n  height\n  name\n  preview\n  focalPoint {\n    x\n    y\n    __typename\n  }\n  __typename\n}\n"
                    })
                data_response_prod = response_prod.json()
                data_prod = data_response_prod["data"]["product"]

                if (data_prod["name"] in diccio_prods_name):
                    print("producto repetido")
                    continue
                diccio_prods_name[data_prod["name"]] = 1
                
                producto = {
                        "vendor_id": 58,
                        "name": categoria + " - " + data_prod["name"],
                        "price": float(prod["priceWithTax"]["max"])/100,
                        "url": "https://tiendaschasqui.ar/csd/producto/"+data_prod["slug"],
                        "is_ext": "",
                        "nota": "Productor: " + data_prod["customFields"]["productor"]["name"], 
                        "branch_id": BRANCH_ID,
                        "category": categorias[categoria]["category"],
                        "key": config["BACK_KEY"]
                    }
                print(producto)
                sio.emit('registrar_precio', producto)
                #enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=producto)
                #print(enviar_back.json())
                print("")
            except:
                continue

        print("")
    else:
        print("ignorando categoria: ", categoria)
        continue

