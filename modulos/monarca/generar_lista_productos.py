import csv
import json
from datetime import datetime

productos = []

VENDOR = 58
BRANCH = 1

productos_no_publicados = []

fecha = datetime.now().strftime("%Y%m%d")
path = 'salida/productos_cat'+fecha+'.csv'
path_json = 'salida/productos_cat'+fecha+'.json'

with open('data/matchs_categorias.json') as archivo_json:
    matchs = json.load(archivo_json)

with open(path, 'r') as archivo_csv:
    lector_csv = csv.reader(archivo_csv)

    for registro in lector_csv:
        json_field = json.loads(registro[2])

        if (len(json_field) == 1):
            registro = json_field[0]
            if registro['status'] != "Publicado":
                productos_no_publicados.append(registro)
            else:
                presentacion = ""
                if registro['presentation'] != None:
                    presentacion = ' - ' + registro['presentation'].strip()
                producto = { 
                    "name": registro['description'].strip() + presentacion,
                    "price": registro['price'],
                    "vendor_id": VENDOR,
                    "branch_id": BRANCH,
                    "category": matchs[str(registro['category']['id'])]
                }
                print(producto)
                productos.append(producto)

    with open(path_json, 'w') as file:
        json.dump(productos, file)

    print("Productos a agregar: ", len(productos))
    print("Productos no publicados: ", len(productos_no_publicados))