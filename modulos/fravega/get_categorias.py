import requests
import datetime
import json

BASE_URL = "https://www.fravega.com"
URL = "https://www.fravega.com/_next/data/jcF0ciy0GlOCE4NotZalk/es-AR/l/tv-y-video/tv.json?marcas=philips&categorias=tv-y-video%2Ftv&categorySlug=tv-y-video&categorySlug=tv"

response = requests.get(URL)
respuesta = response.json()

menus_keys = respuesta['pageProps']['__APOLLO_STATE__']['ROOT_QUERY']['categoryMenu({\"postalCode\":\"\"})']['sections'][0]
menus_keys = menus_keys['items'][0]['sections'][0]['items']

arbol_categorias = {}

for categoria in menus_keys:
    nombre_categoria = categoria['label'].strip()

    for sub_categoria in categoria['sections']:
        nombre_sub_categoria = sub_categoria['label'].strip()
        
        for sub_sub_categoria in sub_categoria['items']:
            nombre_sub_sub_categoria = sub_sub_categoria['label'].strip()
            enlace_sub_sub_categoria = BASE_URL + sub_sub_categoria['href']
            
            arbol_categorias[nombre_sub_sub_categoria] = { "sub_items":[], "texto": nombre_sub_sub_categoria, "category":"", "url": enlace_sub_sub_categoria }
            print(arbol_categorias[nombre_sub_sub_categoria])

with open('categorias.json', 'w') as file:
    json.dump(arbol_categorias, file)
    print('categorias.json actualizado!')