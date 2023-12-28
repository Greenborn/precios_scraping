import csv
import json

categorias = {}
arbol_categorias = {}

with open('resultados.csv', 'r') as archivo_csv:
    lector_csv = csv.reader(archivo_csv)

    for registro in lector_csv:
        json_field = json.loads(registro[2])
        
        if len(json_field) == 1:
            json_field = json_field[0]
            if ("category" in json_field):
                categorias[json_field["category"]['id']] = json_field["category"]
    
    arbol_categorias = categorias.copy()
    for categoria in categorias:
        cat = categorias[categoria]
        cat['id_sistema'] = ''
        padre = cat['parentId']

        if padre != None:
            if not padre in arbol_categorias:
                arbol_categorias[padre] = {}

            if not 'sub_categorias' in arbol_categorias[padre]:
                arbol_categorias[padre]['sub_categorias'] = []

            arbol_categorias[padre]['sub_categorias'].append(cat)
            print(arbol_categorias[padre])

    for categoria in categorias:
        padre = categorias[categoria]['parentId']
        if padre != None:
            del arbol_categorias[categoria]
    
    for categoria in arbol_categorias:
        print(arbol_categorias[categoria])
        print("")

    with open("data/arbol_categorias.json", 'w') as file:
        json.dump(arbol_categorias, file)

    print("Cantidad de categorías: ", len(categorias))
    print("Cantidad de categorías raiz: ", len(arbol_categorias))