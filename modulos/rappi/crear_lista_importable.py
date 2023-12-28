
import json

REESCRIBIR_MATCHS = False
PROCESA_CATALOGADO = True
PROCESA_NO_CATALOGADO = True

VENDOR = 58

# Ruta al archivo JSON
ruta_catalogado = "salida/productos_cat20231227.json"
ruta_no_catalogado = "salida/productos_no_cat20231227.json"
ruta_matchs_config = "matchs_categoria_comercio.json"
ruta_salida = "salida/productos.json"

# Leer el archivo JSON
if PROCESA_CATALOGADO:
    with open(ruta_catalogado, "r") as archivo:
        data_c = json.load(archivo)
if PROCESA_NO_CATALOGADO:
    with open(ruta_no_catalogado, "r") as archivo:
        data_nc = json.load(archivo)
with open(ruta_matchs_config, "r") as archivo:
    matchs = json.load(archivo)

todos_los_productos = []
todas_categorias = {}
todos_negocios = {}

#Productos Catalogados
if PROCESA_CATALOGADO:
    for comercio in data_c:
        solo_comercio = comercio.split("/")[-1]
        if (not solo_comercio in todos_negocios):
            todos_negocios[solo_comercio] = ""

        for cat_comercio in data_c[comercio]:
            
            solo_cat = cat_comercio.split("/")[-1]
            if (not solo_cat in todas_categorias):
                todas_categorias[solo_cat] = {}
            for sub_cat in data_c[comercio][cat_comercio]:
                solo_sub_cat = sub_cat.split("/")[-1]
                if (not solo_sub_cat in todas_categorias[solo_cat]):
                    todas_categorias[solo_cat][solo_sub_cat] = ""
                
                productos = data_c[comercio][cat_comercio][sub_cat]
                for producto in productos:
                    nuevo_prod = {}
                    nuevo_prod['vendor_id'] = VENDOR
                    nuevo_prod['name'] = producto['titulo'] +' - '+ producto['descripcion']
                    nuevo_prod['name'] = nuevo_prod['name'].strip()
                    nuevo_prod['price'] = float(producto['precio'].replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").replace(",", ".").strip())
                    nuevo_prod['is_ext'] = producto['data_qa']
                    if not solo_cat in matchs['categorias'] or not solo_sub_cat in matchs['categorias'][solo_cat]:
                        print('Se omite producto no hay categoria')
                        print(solo_cat, ' ',solo_sub_cat)
                        continue

                    if (solo_comercio in matchs["comercios"]):
                        nuevo_prod['branch_id'] = matchs["comercios"][solo_comercio]
                    else:
                        nuevo_prod['branch_id'] = -1
                    if (solo_cat in matchs["categorias"]):
                        nuevo_prod['category'] = matchs["categorias"][solo_cat][solo_sub_cat]
                    else:
                        nuevo_prod['category'] = -1
                    
                    todos_los_productos.append( nuevo_prod)

if PROCESA_NO_CATALOGADO:
#Productos no catalogados
    for comercio in data_nc:
        comercio_ = data_nc[comercio]
        solo_comercio = comercio.split("/")[-1]
        if (not solo_comercio in todos_negocios):
            todos_negocios[solo_comercio] = ""

        for prod in comercio_:
            if prod['titulo'] != None:
                nuevo_prod = {}
                nuevo_prod['vendor_id'] = VENDOR
                nuevo_prod['name'] = prod['titulo'].strip() +' - '+ prod['descripcion'].strip()
                nuevo_prod['name'] = nuevo_prod['name'].strip()
                try:
                    nuevo_prod['price'] = float(prod['precio'].replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").replace(",", ".").strip())
                except:
                    print("error al querer formatear precio", prod['precio'])
                    continue
                nuevo_prod['is_ext'] = prod['data_qa']
                if (solo_comercio in matchs["comercios"]):
                    nuevo_prod['branch_id'] = matchs["comercios"][solo_comercio]
                else:
                    nuevo_prod['branch_id'] = -1
                nuevo_prod['category'] = matchs["categorias"]["no catalogado"]
                todos_los_productos.append(nuevo_prod)

matchs["comercios"] = todos_negocios
matchs["categorias"] = todas_categorias

if (REESCRIBIR_MATCHS):
    with open(ruta_matchs_config, "w") as archivo:
        json.dump(matchs, archivo)
        print("Se reescribieron los matchs")

with open(ruta_salida, "w") as archivo:
    json.dump(todos_los_productos, archivo)
    print("Se genero productos.json")
