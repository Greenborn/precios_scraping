#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import socketio 

fecha = datetime.now().strftime("%Y%m%d")
path = 'salida/productos_cat'+fecha+'.json'
URL = "https://www.diarco.com.ar/ofertas/"
UR_OFERTA = "https://www.diarco.com.ar/ofertas/?e-filter-9a897e7-sucursal=tandil&tipo-sucursal=mayorista#"
BRANCH_ID = 129
listado_productos = []

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

contador = 1

ultima = 150
cont_descuento = 0
cont_promo = 0

sio = socketio.SimpleClient()
sio.connect('http://localhost:7777')

sio.emit('cliente_conectado')
if (not sio.receive()[1]["status"]):
    print("Rechazado")
    exit()

while True:
    if (contador > ultima):
        break

    url_ = URL + str(contador) + "/?e-filter-9a897e7-sucursal=tandil"
    print("Consultando URL: ", url_)

    response = requests.get(url_)
    response = response.text
    soup = BeautifulSoup(response, 'html.parser')

    product_html = soup.find_all(class_="product-type-simple")
    if (len(product_html) == 0):
        break
    for product in product_html:
        class_list = product['class']
        
        _titulo    = product.find("h1")
        _s_titulo  = product.find("h2")
        url_oferta = url_

        _price     = _s_titulo.find(class_="price-container").text
        _decimal_1 = _s_titulo.find(class_="custom-decimal").text.strip()
        _decimal_2 = _s_titulo.find(class_="custom-decimal-final").text.strip()

        _descript2 = product.find_all("h2",class_="elementor-heading-title elementor-size-default")
        if (_descript2 != None):
            if (len(_descript2) > 1):
                _descript2 = _descript2[1].text.strip()
            else:
                _descript2 = ""
        else:
            _descript2 = ""

        _descript1 = product.find(class_="short-description-tag")
        if (_descript1 != None):
            _descript1 = _descript1.text.strip()
        else:
            _descript1 = ""
        
        price_cnt = _price.replace("$","").replace("%","").replace(_decimal_2,"",1)

        if (_decimal_2 == "FINAL"):
            price_cnt = price_cnt.replace(_decimal_1,"",1)

        titulo_oferta = _titulo.text
        if (_descript1 != ""):
            titulo_oferta = titulo_oferta + " - " + _descript1
        if (_descript2 != ""):
            titulo_oferta = titulo_oferta + " - " + _descript2
        
        # en promociones 3x2 por ej
        promo_cnt = ''
        if (_decimal_2 == "" and _decimal_1 == ""):
            promo_cnt = price_cnt
            titulo_oferta = price_cnt + " - " + titulo_oferta
        elif (_decimal_1 == "%"):
            promo_cnt     = price_cnt + _decimal_1 + " " + _decimal_2
            titulo_oferta = price_cnt + _decimal_1 + " " + _decimal_2 + " " + titulo_oferta

        promocion = {
            "orden":       0,
            "titulo":      titulo_oferta,
            "id_producto": 0,
            "datos_extra": { "promo_cnt": promo_cnt },
            "precio":      -1,
            "branch_id":   BRANCH_ID,
            "url":         url_oferta,
            "key": config["BACK_KEY"]
        }

        if (_decimal_2 == "FINAL"):
            promocion["precio"] = float(price_cnt)

        #print( ';', _decimal_1, ';', _decimal_2, ';')
        cont_promo = cont_promo + 1
        print(promocion)
        sio.emit('registrar_oferta', promocion)
        #enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar_oferta", json=promocion)
        #print(enviar_back.json())
        print("")

    contador = contador + 1

with open(path, 'w') as file:
    json.dump(listado_productos, file)
    print('estado.json actualizado')

print("Promo", cont_promo)