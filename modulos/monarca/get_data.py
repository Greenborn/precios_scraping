#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime
import sys
#sys.path.insert(1, "../")
sys.path.insert(1, "./modulos")
from clientecoordinador import *
cliente = ClienteCoordinador()

BRANCH_ID = 1
VENDOR = 58

fecha = datetime.datetime.now().strftime("%Y%m%d")
URL_MONARCA_APP = "https://monarcadigital.com.ar/app/"

ofertas_no_procesadas = []
tipos_ofertas = { 
    "PERCENTAGE_OFF": True,
    "NXM": True,
    "PERCENTAGE_N_OFF": True,
    "PXQ": True
}

todos_los_descuentos = []
productos = []

def convertir_fecha(fecha_str):
    fecha_datetime = datetime.datetime.strptime(fecha_str, "%d/%m/%Y %H:%M:%S")
    return fecha_datetime.strftime("%Y-%m-%d %H:%M:%S")

for categoria in CATEGORIAS:
    if (categoria == CATEGORIA_INICIO or CATEGORIAS[categoria]["category"] == CATEGORIA_INICIO_ID):
        print(categoria, CATEGORIA_INICIO, CATEGORIA_INICIO_ID)
        PROCESAR = True
        continue

    if (PROCESAR == True):
        categoria_asignada = CATEGORIAS[categoria]["id_ext"]
        url_consulta_cat = "http://api.monarcadigital.com.ar/categories/"+str(categoria_asignada)+"/products" 
        print("Consultando URL: ", url_consulta_cat, categoria )

        response = requests.get(url_consulta_cat)
        if not response.json():
            print('Se obtuvo respuesta vacía')
            continue

        response = response.json()

        for registro in response:
            if registro['status'] != "Publicado":
                print("No publicado")
                continue

            presentacion = ""
            if registro['presentation'] != None:
                presentacion = ' - ' + registro['presentation'].strip()

            nomobre_completo_prod = registro['description'].strip() + ' - ' + registro['brand'].strip() + ' - ' + presentacion
            oferta_data           = registro['promotions']
            
            if (len(oferta_data) == 1):
                print(oferta_data, len(oferta_data))
                print("")
                oferta_ = oferta_data[0]
                if (oferta_["type"] in tipos_ofertas):
                    try:
                        texto_descuento = oferta_["content"]
                        promocion = {
                                        "orden":       0,
                                        "titulo":      texto_descuento + ' - ' + nomobre_completo_prod,
                                        "id_producto": 0,
                                        "datos_extra": { "promo_cnt": texto_descuento, 
                                                        "_data": oferta_, 
                                                        "hasta": convertir_fecha(oferta_["dateTo"]),
                                                        "desde": convertir_fecha(oferta_["fromDate"]),
                                                        },
                                        "precio":      float(registro["price"]),
                                        "branch_id":   BRANCH_ID,
                                        "url":         URL_MONARCA_APP,
                                        "key":         CONFIG["BACK_KEY"]
                                    }
                        print(promocion)
                        
                        #cliente.sio.emit('registrar_oferta', promocion)
                        todos_los_descuentos.append(promocion)
                        print("")
                    except:
                        print("no se pudo procesar oferta")
                        ofertas_no_procesadas.append(oferta_)
                        print(oferta_)
                        with open('ofertas_no_procesadas.json', 'w') as file:
                            json.dump(ofertas_no_procesadas, file)
                        continue
                else:
                    ofertas_no_procesadas.append(registro)
                    print("no se procesa oferta")
                    with open('ofertas_no_procesadas.json', 'w') as file:
                        json.dump(ofertas_no_procesadas, file)
                    
            elif (len(oferta_data) > 1):
                ofertas_no_procesadas.append(registro)
                print("hay mas de una oferta")
                with open('ofertas_no_procesadas.json', 'w') as file:
                    json.dump(ofertas_no_procesadas, file)
            elif (len(oferta_data) == 0):
                producto = { 
                    "name": nomobre_completo_prod,
                    "price": float(registro['price']),
                    "vendor_id": VENDOR,
                    "branch_id": BRANCH_ID,
                    "barcode": registro['barcode'],
                    #"reg": registro,
                    "url": URL_MONARCA_APP,
                    "category": CATEGORIAS[categoria]["category"],
                    "key": CONFIG["BACK_KEY"]
                }
                print(producto)
                #cliente.sio.emit('registrar_precio', producto)
                print("")
                productos.append(producto)

    else:
        print("ignorando categoria: ", categoria)
        continue

print("Productos a agregar: ", len(productos))
print("promociones", len(todos_los_descuentos))