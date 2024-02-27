#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import datetime
import json
fecha = datetime.datetime.now().strftime("%Y%m%d")

with open('modulos/habilitados.json', 'r') as file:
    habilitados = json.load(file)

todos_productos = []

for habilitado in habilitados:
    path = 'modulos/'+habilitado+'/salida/productos_cat'+fecha+'.json'
    print("Abriendo archivo: ", path)

    with open(path, 'r') as file:
        productos_cat = json.load(file)
        todos_productos = todos_productos + productos_cat
    
with open("resultados/productos"+fecha+".json", 'w') as file:
    json.dump(todos_productos, file)
    print("Se genero resultados/productos"+fecha+".json", len(todos_productos))