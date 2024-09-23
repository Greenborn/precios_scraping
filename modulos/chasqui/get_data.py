#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime
import time
import sys

sys.path.insert(1, "./modulos")
from clientecoordinador import *
cliente = ClienteCoordinador()
from selenium_utils import *

BRANCH_ID = 138
BASE_URL = "https://tiendaschasqui.ar/csd/catalogo"

fecha = datetime.datetime.now().strftime("%Y%m%d")

def get_cookies_header( cookies ):
    return '; '.join([f'{key}={value}' for key, value in cookies.items()]) 

diccio_items = {}

driver = get_driver()

diccio_prods_name = {}

while True:
    try:
        for categoria in CATEGORIAS:
            if (categoria == CATEGORIA_INICIO or CATEGORIAS[categoria]["category"] == CATEGORIA_INICIO_ID):
                print(categoria, CATEGORIA_INICIO, CATEGORIA_INICIO_ID)
                PROCESAR = True
                continue

            if (PROCESAR == True):
                url = CATEGORIAS[categoria]['url']
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
                                "category": CATEGORIAS[categoria]["category"],
                                "category_name": categoria,
                                "key": CONFIG["BACK_KEY"]
                            }
                        print(producto)
                        cliente.sio.emit('registrar_precio', producto)
                        print("")
                    except:
                        continue

                print("")
            else:
                print("ignorando categoria: ", categoria)
                continue
    except Exception as e:
        print("Error al realizar consulta, reintentando")
        print(e)
        continue
    break