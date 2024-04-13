#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime
import sys

sys.path.insert(1, "./modulos")
from clientecoordinador import *
cliente = ClienteCoordinador()

BRANCH_ID = 150

fecha = datetime.datetime.now().strftime("%Y%m%d")

diccio_nam = {}

def procesar_elementos( url, cat_id, categoria, id_ext ):
    cantidad = 0
    pagina   = 1
    

    diccio_cat_nam = {}

    while (True):
        #https://www.distribuidoraeva.com.ar/v4/product/category?filter_page=2&filter_order=4&filter_categories%5B%5D=953189&filter_categories%5B%5D=826510
        url_pag = "https://www.distribuidoraeva.com.ar/v4/product/category?filter_page="
        url_pag = url_pag + str(pagina) + "&filter_order=4&filter_categories[]=" + str(id_ext)
        response = requests.get(url_pag, headers={
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
            "content-type": "application/json",
            "set_cookie":"EMPRETIENDA_SESSION=eyJpdiI6Inp1RDlXS0FVdU93eHA2WUNaa2p0TWc9PSIsInZhbHVlIjoicFF5bWp2Z3FKaU1hWEZKQkFDKzJFNTVDNUZJNlRLaWR5bXhuVnF3ekxwbGhSbnFDemVDWHJLTGg0YWtycEN2MlR6elN4SzQrNUhvNlVoVmhHT0M2aDA2Z2swa3FrT2ZkVzBhd28xekpObTIzNkxFUUdkaWFCUmc3V1I2RGlUTDYiLCJtYWMiOiJiOTIyZDM0ZDg1NzA1NjQ0YWZiNGUxMTJmZDUwNDQyNTc5YTVlZWM5MjM5ZWY3OGE0YmVkZGViN2UyZjA1YjAwIn0%3D; expires=Wed, 17-Apr-2024 07:46:34 GMT; Max-Age=604800; path=/; secure; httponly; samesite=lax"
        }, 
        cookies={
           "EMPRETIENDA_SESSION":"eyJpdiI6IlVWRlBLMlUxTCtzNTRmV1wvOUhsaktnPT0iLCJ2YWx1ZSI6IjMxdVc3akg3dDVDUG10WTdLMytXK0liVDB6eDFsMWtqZVFVaGQ0czd5RHoxb0dyQ0pMeWFNWU5GclFRcTdwWWVcL3Q4cjI0VWgwbk9tUXVIZFh1ZE9uczRnUHVRdHhaRSs1d2JMV3VUc2hhY1ZPWXNOWU93ak5qUmdXRFFET09NKyIsIm1hYyI6ImFhNDM4ZGQ0ZjJiNjEyN2U1MzU1NjdmZjY1OGM4YTg3NzllMTU2ODllNjExZTM0NDA4YjA3MThiOThiZWJhMzMifQ=="
        })
        print(url_pag)
        response = response.text
        response = json.loads(response)
        
        if (len(response["data"]) == 0):
            return cantidad
        
        items = response["data"]
        for item in items:
            #print(item)
            if ( item["p_precio_oferta"] != 0 ):
                print("oferta")
            else:
                producto = {
                    "vendor_id": 58,
                    "name": categoria + " - " + item["p_nombre"],
                    "price": float(item["p_precio"]),
                    "is_ext": "",
                    "branch_id": BRANCH_ID,
                    "category": cat_id,
                    "url": url + "/" + item["p_link"],
                    "key": CONFIG["BACK_KEY"]
                }
                cliente.sio.emit('registrar_precio', producto)
                print(producto)
                print("")

        pagina = pagina + 1
    
    return cantidad

procesar = True
print(CATEGORIA_INICIO)

if (CATEGORIA_INICIO != None):
    procesar = False

total = 0
for categoria in CATEGORIAS:
    url = CATEGORIAS[categoria]['url']

    if (categoria == CATEGORIA_INICIO):
        print(categoria, CATEGORIA_INICIO)
        procesar = True
        continue

    if (procesar == True):
        total = total + procesar_elementos( url, CATEGORIAS[categoria]["category"],  categoria, CATEGORIAS[categoria]['id_ext'] )
    else:
        print("ignorando categoria: ", categoria)
        continue

print(total)