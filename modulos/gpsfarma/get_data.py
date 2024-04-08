#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime
import argparse
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

BRANCH_ID = 149

fecha = datetime.datetime.now().strftime("%Y%m%d")

diccio_nam = {}

parser = argparse.ArgumentParser()

parser.add_argument("--categoria_inicio", type=str, help="Categoria desde la cual se procesan resultados")
args = parser.parse_args()
categoria_inicio = args.categoria_inicio

def procesar_elementos( url, cat_id, categoria ):
    cantidad = 0
    pagina   = 1
    

    diccio_cat_nam = {}

    while (True):
        response = requests.get(url+'?p='+str(pagina)+'&product_list_limit=36')
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

                promocion = {
                    "orden":       0,
                    "titulo":      texto_oferta + ' - ' + nombre,
                    "id_producto": 0,
                    #"datos_extra": { "promo_cnt": promo_cnt },
                    "datos_extra": {},
                    "precio":      float(art.find(class_="price").text.replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").replace(",", ".").strip()),
                    "branch_id":   BRANCH_ID,
                    "url":         enlace.get("href"),
                    "key":         config["BACK_KEY"]
                }
                print(promocion)
                sio.emit('registrar_oferta', promocion)
            else:
                print("no es oferta")

                try:
                    producto = {
                        "vendor_id": 58,
                        "name": nombre,
                        "url": enlace.get("href"),
                        "price": float(art.find(class_="price").text.replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").replace(",", ".").strip()),
                        "is_ext": "",
                        "branch_id": BRANCH_ID,
                        "category": cat_id,
                        "key": config["BACK_KEY"]
                    }
                except:
                    continue
                cantidad = cantidad + 1
                sio.emit('registrar_precio', producto)
                print(producto)

            print("")
            

        pagina = pagina + 1
    
    return cantidad

procesar = True
print(categoria_inicio)

if (categoria_inicio != None):
    procesar = False

total = 0
for categoria in categorias:
    url = categorias[categoria]['url']

    if (categoria == categoria_inicio):
        print(categoria, categoria_inicio)
        procesar = True
        continue

    if (procesar == True):
        total = total + procesar_elementos( url, categorias[categoria]["category"],  categoria )
    else:
        print("ignorando categoria: ", categoria)
        continue

print(total)