import json
import mysql.connector

conexion = mysql.connector.connect(
    host="localhost",
    user="precios",
    password="precios",
    database="precios"
)

cursor = conexion.cursor()

ID_INICIAL = 227

arbol_categorias = {}
dicc_categorias = {}

dicc_categorias_exp = {}
matchs_categorias = {}

def procesar_sub_categorias(sub_categorias):

    for sub_categoria in sub_categorias:
        id = sub_categoria['id_interno']
        root_cat = None
        if (sub_categoria['parentId'] in dicc_categorias):
            root_cat = dicc_categorias[sub_categoria['parentId']]['id_interno']
        name = sub_categoria['description']
        print(id, root_cat, name)
        sub_categoria["insertada"] = True

        try:
            cursor.execute("INSERT INTO category (id, root_category_id, name) VALUES (%s, %s, %s)", (id, root_cat, name))
        except Exception as e:
            
            try:
                sub_categoria['description'] = sub_categoria['description'] + "_" + str(sub_categoria['id'])
                cursor.execute("INSERT INTO category (id, root_category_id, name) VALUES (%s, %s, %s)", (id, root_cat, sub_categoria['description']))
            except Exception as e:
                sub_categoria["insertada"] = False
                print(e)
                print("No se insertara categoria")

        dicc_categorias_exp[id] = sub_categoria     
        matchs_categorias[sub_categoria['id']] = id
        procesar_sub_categorias(sub_categoria['sub_categorias'])

with open('categories.json') as archivo_json:
    datos = json.load(archivo_json)

id_inc = ID_INICIAL
for registro in datos:
    registro["sub_categorias"] = []
    registro["insertada"] = None
    registro["id_interno"] = id_inc
    id_inc = id_inc + 1
    dicc_categorias[registro['id']] = registro

for registro in datos:
    if registro['parentId'] != None:
        dicc_categorias[registro['parentId']]["sub_categorias"].append(registro)

for registro in datos:
    if registro['parentId'] == None:
        arbol_categorias[registro['id']] = registro

for nodo in arbol_categorias:
    node_data = arbol_categorias[nodo]
    print(node_data['id_interno'], None, node_data['description'])
    node_data["insertada"] = True
    try:
        cursor.execute("INSERT INTO category (id, root_category_id, name) VALUES (%s, %s, %s)", (node_data['id_interno'], None, node_data['description']))
    except Exception as e:
        try:
            node_data['description'] = node_data['description'] + "_" + str(node_data['id'])
            cursor.execute("INSERT INTO category (id, root_category_id, name) VALUES (%s, %s, %s)", (node_data['id_interno'], None, node_data['description']))
        except Exception as e:
            print(e)
            node_data["insertada"] = False
            print("No se insertara categoria")
    
    dicc_categorias_exp[node_data['id_interno']] = node_data
    matchs_categorias[node_data['id']] = node_data['id_interno']
    procesar_sub_categorias(node_data['sub_categorias'])

conexion.commit()

with open("data/arbol_categorias_2.json", 'w') as file:
    json.dump(arbol_categorias, file)

with open("data/diccionario_categorias.json", 'w') as file:
    json.dump(dicc_categorias_exp, file)

with open("data/matchs_categorias.json", 'w') as file:
    json.dump(matchs_categorias, file)
