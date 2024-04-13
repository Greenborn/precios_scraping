#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
from datetime import datetime
import sys

sys.path.insert(1, "./modulos")
from clientecoordinador import *
cliente = ClienteCoordinador()

fecha_actual = datetime.now()
fecha = datetime.now().strftime("%Y%m%d")
URL = "https://pedidos.amarillagas.com/api/get_products_for_category"


BRANCH_ID = 99
CATEGORY_ID = 1971

headers_ = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
    "Referer": "https://pedidos.amarillagas.com/",
    "base_version": "1.0.0",
    "device_type": "WEB",
    "Content-Type": "application/json",
    "Origin": "https://pedidos.amarillagas.com",
    "Connection": "keep-alive",
    "Cookie": "G_ENABLED_IDPS=google; __stripe_mid=aa49bb68-6ae4-4dc2-8030-d0ddaa6ae76f0a9835; __stripe_sid=efbc3886-1e95-4864-8717-491b34e8ed7e912f9d",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-GPC": "1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "TE": "trailers"
}

cookies_ = {
}

data_ = {
    "page_no": 1,
    "offset": 1,
    "limit": 25,
    "marketplace_reference_id": "b4b21574374cad104a422e6b81bcfef3",
    "marketplace_user_id": 283199,
    "user_id": 301176,
    "date_time": fecha_actual.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
    "domain_name": "pedidos.amarillagas.com",
    "dual_user_key": "0",
    "language": "es"
}

response = requests.post(URL,   json=data_,
                                headers=headers_,
                                cookies=cookies_)

response = response.json()
if (response == None):
    exit(0)

response = response["data"]
for product in response:
    producto = {
        "vendor_id": 58,
        "name": "Garrafas" + ' - ' + product["name"] + " - " + product["description"],
        "price": product["price"],
        "is_ext": "",
        "enlace": "",
        "branch_id": BRANCH_ID,
        "category": CATEGORY_ID,
        "key": CONFIG["BACK_KEY"]
    }
    print(producto)
    
    cliente.sio.emit('registrar_precio', producto)
    print("")
