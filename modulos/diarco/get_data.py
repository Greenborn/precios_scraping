#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime

fecha = datetime.now().strftime("%Y%m%d")
path = 'salida/productos_cat'+fecha+'.json'
URL = "https://www.diarco.com.ar/ofertas/?wlfilter=1&orderby=popularity&sucursal=Tandil&padre=182&hijo=183&nieto=205&woolentor_sucursal=Tandil&product-page="
BRANCH_ID = 129
listado_productos = []

with open("../config.json", "r") as archivo:
    config = json.load(archivo)

contador = 1

ultima = 150
cont_descuento = 0
cont_promo = 0

while True:
    if (contador > ultima):
        break

    url_ = URL + str(contador)
    print("Consultando URL: ", url_)

    response = requests.get(url_)
    response = response.text
    soup = BeautifulSoup(response, 'html.parser')

    product_html = soup.find_all(class_="product-type-simple")
    if (len(product_html) == 0):
        break
    for product in product_html:
        class_list = product['class']
        
        if "product_tag-club" in class_list or "tag-estandar-naranja" in class_list or  "product_tag-oferta" in class_list or "product_tag-6x5" in class_list or "product_tag-promo" in class_list or "product_tag-super-descuento" in class_list or "product_tag-cuotas" in class_list:
            cont_promo = cont_promo + 1
            print("Promo encontrada! se omite")
            continue

        html_data = BeautifulSoup(str(product.contents), 'html.parser')
        
        nombre = html_data.find(class_="woocommerce-loop-product__title").text + " - " + html_data.find(class_="product-brand-title").text + " - "  + html_data.find(class_="woocommerce-product-details__short-description").text
        
        try:
            text = html_data.find(class_='woocommerce-Price-amount').text
            print(text)
            if "%" in text or  "Cuotas" in nombre or  "En la Segunda Unidad" in nombre or  "EN TODAS LAS" in nombre or "EN TODOS LOS" in nombre  or "EN TODA LA" in nombre:
                print("Descuento encontrado! se omite") 
                cont_descuento = cont_descuento + 1
                continue
            if "X" in text:
                print("Descuento encontrado! se omite")
                cont_descuento = cont_descuento + 1
                continue
            text = text.replace("C/IVA", "").replace(",", "").replace("$", "")
            precio = float(text)/100
        except:
            continue

        producto = {
            "vendor_id": 58,
            "name": nombre,
            "price": precio,
            "is_ext": "",
            "es_oferta": True,
            "fecha_limite": "",
            "page": contador,
            "branch_id": BRANCH_ID,
            "category": 155,
            "key": config["BACK_KEY"]
        }

        enviar_back = requests.post(config["URL_BACK"] + "/publico/productos/importar", json=producto)
        print(enviar_back.json())

        listado_productos.append(producto)
        print(producto)

    contador = contador + 1

with open(path, 'w') as file:
    json.dump(listado_productos, file)
    print('estado.json actualizado')

print("Promo", cont_promo)
print("Descuento", cont_descuento)
print("Total", len(listado_productos))