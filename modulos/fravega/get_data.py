import requests
from bs4 import BeautifulSoup
import datetime
import json

BRANCH_ID = 96
BASE_URL = "https://www.fravega.com/"
fecha = datetime.datetime.now().strftime("%Y%m%d")

with open('categorias.json') as archivo_json:
    categorias = json.load(archivo_json)

todos_productos = []

def procesar_resultados(response, categoria):
    soup = BeautifulSoup(response, 'html.parser')
    contenedor = soup.find('ul', attrs={'data-test-id': 'results-list'})
    resultados = contenedor.find_all('li')
    for resultado in resultados:
        print("Procesando resultado: ")

        precio = resultado.find('div', attrs={'data-test-id': 'product-price'}).text
        precio = precio.replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").strip()

        nombre = resultado.find('div', attrs={'data-test-id': 'product-title'}).text
        producto = {
                    "vendor_id": 58,
                    "name": categoria + ' - ' + nombre,
                    "price": precio,
                    "is_ext": "",
                    "branch_id": BRANCH_ID,
                    "all_data": data_,
                    "category": categorias[categoria]["category"]
                }
        todos_productos.append(producto)
        print(producto)
        print("")

for categoria in categorias:
    print("Procesado categoria: ",categoria)
    cat_data = categorias[categoria]

    URL = cat_data['url'].replace("https://www.fravega.coml","https://www.fravega.com/l")
    response = requests.get(URL)
    response = response.text

    soup = BeautifulSoup(response, 'html.parser')

    paginador = soup.find_all('li', attrs={'data-type': 'page'})
    
    if paginador == None:
        procesar_resultados(response, categoria)

    for pagina in paginador:
        url_pag = BASE_URL + pagina.find("a").get("href")
        print(url_pag)

        response = requests.get(URL)
        response = response.text
        procesar_resultados(response, categoria)

    print("")