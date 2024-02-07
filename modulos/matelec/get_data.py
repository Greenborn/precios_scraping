#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import datetime

URL_BASE = "https://www.matelec.com.ar"
BRANCH_ID = 87

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

fecha = datetime.datetime.now().strftime("%Y%m%d")

listado_productos = []

for categoria in categorias:
    print("Procesado categoria Nivel 0: ",categoria)

    for sub_categoria in categorias[categoria]['sub_items']:
        texto_sub_cat = sub_categoria['texto'].strip()
        print("----> Procesando sub categoría: ",texto_sub_cat)

        