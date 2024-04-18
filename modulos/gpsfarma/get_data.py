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

BRANCH_ID = 149

fecha = datetime.datetime.now().strftime("%Y%m%d")

diccio_nam = {}

def procesar_elementos( url, cat_id, categoria ):
    cantidad = 0
    pagina   = 1
    
    diccio_cat_nam = {}

    while (True):
        response = requests.get(url+'?p='+str(pagina)+'&product_list_limit=36', cookies={ "region_id":"702", "city_id":"290"})
        print(url+'?p='+str(pagina))
        response = response.text
        soup = BeautifulSoup(response, 'html.parser')
        
        articulos = soup.find_all(class_="product-item-info")
        for art in articulos:
            
            if (art.find(class_="product-item-link") == None):
                continue
            enlace = art.find(class_="product-item-link")
            nombre = categoria + ' - ' + enlace.text.replace("\n", "").strip()

            if (enlace.text in diccio_nam):
                return cantidad
            diccio_nam[enlace.text] = True

            if (enlace.text in diccio_cat_nam):
                return cantidad
            diccio_cat_nam[enlace.text] = True

            #Verificamos si se trata de una oferta
            cont_oferta = art.find(class_="product-image-wrapper")
            if (cont_oferta == None):
                print("No hay contenedor de imagen")
                continue
            cont_oferta = cont_oferta.find(class_="top_left category")

            if (cont_oferta != None):
                texto_oferta = cont_oferta.find("img").get("alt")
                print(texto_oferta)
                try:
                    precio = float(art.find(class_="special-price").find(class_="price").text.replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").replace(",", ".").strip())
                except:
                    print("no se pudo obtener precio")
                    precio = float(art.find(class_="price-final_price").find(class_="price").text.replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").replace(",", ".").strip())

                promocion = {
                    "orden":       0,
                    "titulo":      texto_oferta + ' - ' + nombre,
                    "id_producto": 0,
                    #"datos_extra": { "promo_cnt": promo_cnt },
                    "datos_extra": {},
                    "precio":      precio,
                    "branch_id":   BRANCH_ID,
                    "url":         enlace.get("href"),
                    "key":         CONFIG["BACK_KEY"]
                }
                print(promocion)
                cliente.sio.emit('registrar_oferta', promocion)
            else:
                print("no es oferta")

                try:
                    precio = float(art.find(class_="price-final_price").find(class_="price").text.replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").replace(",", ".").strip())

                    producto = {
                        "vendor_id": 58,
                        "name": nombre,
                        "url": enlace.get("href"),
                        "price": precio,
                        "is_ext": "",
                        "branch_id": BRANCH_ID,
                        "category": cat_id,
                        "key": CONFIG["BACK_KEY"]
                    }
                except:
                    print("no se pudo obtener precio")
                    continue
                cantidad = cantidad + 1
                cliente.sio.emit('registrar_precio', producto)
                print(producto)

            print("")
            

        pagina = pagina + 1
    
    return cantidad

procesar = True
print(CATEGORIA_INICIO, CATEGORIA_INICIO_ID)

if (CATEGORIA_INICIO != None or CATEGORIA_INICIO_ID != None):
    procesar = False

total = 0
for categoria in CATEGORIAS:
    if (categoria == CATEGORIA_INICIO or CATEGORIAS[categoria]["category"] == CATEGORIA_INICIO_ID):
        print(categoria, CATEGORIA_INICIO, CATEGORIA_INICIO_ID)
        PROCESAR = True
        continue
    
    if (PROCESAR == True):
        url = CATEGORIAS[categoria]['url']
        total = total + procesar_elementos( url, CATEGORIAS[categoria]["category"],  categoria )
    else:
        print("ignorando categoria: ", categoria)
        continue

print(total)