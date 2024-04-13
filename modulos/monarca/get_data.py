#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import datetime
import json
import requests
import argparse
import socketio

URL_CATEGORIAS = "http://api.monarcadigital.com.ar/categories/struct?version=87ddd4f1-8d9b-4cbf-a677-07db09562e7c"

with open('data/matchs_categorias.json') as archivo_json:
    matchs = json.load(archivo_json)

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

fecha = datetime.datetime.now().strftime("%Y%m%d")
path = 'salida/productos_cat'+fecha+'.json'

productos = []
productos_no_publicados = []
VENDOR = 58
BRANCH = 1
URL_MONARCA_APP = "https://monarcadigital.com.ar/app/"

parser = argparse.ArgumentParser()

parser.add_argument("--categoria_inicio", type=str, help="Categoria desde la cual se procesan resultados")
args = parser.parse_args()
categoria_inicio = args.categoria_inicio

procesar = True
print(categoria_inicio)

if (categoria_inicio != None):
    procesar = False

ofertas_no_procesadas = []
tipos_ofertas = { 
    "PERCENTAGE_OFF": True,
    "NXM": True,
    "PERCENTAGE_N_OFF": True,
    "PXQ": True
}

todos_los_descuentos = []

def convertir_fecha(fecha_str):
    fecha_datetime = datetime.datetime.strptime(fecha_str, "%d/%m/%Y %H:%M:%S")
    return fecha_datetime.strftime("%Y-%m-%d %H:%M:%S")

with socketio.SimpleClient() as sio:
    sio.connect('http://localhost:7777')

    sio.emit('cliente_conectado')
    if (not sio.receive()[1]["status"]):
        print("Rechazado")
        exit()

    for categoria in matchs:
        url_consulta_cat = "http://api.monarcadigital.com.ar/categories/"+categoria+"/products" 
        print("Consultando URL: ", url_consulta_cat )

        if (categoria == categoria_inicio):
            print(categoria, categoria_inicio)
            procesar = True
            continue
        
        if (procesar == True):
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
                categoria_asignada    = matchs[str(registro['category']['id'])]

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
                                            "branch_id":   BRANCH,
                                            "url":         URL_MONARCA_APP,
                                            "key":         config["BACK_KEY"]
                                        }
                            print(promocion)
                            
                            sio.emit('registrar_oferta', promocion)
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
                        "branch_id": BRANCH,
                        "barcode": registro['barcode'],
                        #"reg": registro,
                        "url": URL_MONARCA_APP,
                        "category": categoria_asignada,
                        "key": config["BACK_KEY"]
                    }
                    print(producto)
                    sio.emit('registrar_precio', producto)
                    print("")
                    productos.append(producto)

            with open(path, 'w') as file:
                json.dump(productos, file)
        else:
            print("ignorando categoria: ", categoria)
            continue

    print("Productos a agregar: ", len(productos))
    print("promociones", len(todos_los_descuentos))
    print("Productos no publicados: ", len(productos_no_publicados))
