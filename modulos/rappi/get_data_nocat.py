import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
from bs4 import BeautifulSoup
import time
import csv
import argparse

fecha = datetime.datetime.now().strftime("%Y%m%d")
BASE_URL = "https://www.rappi.com.ar"
ruta_matchs_config = "matchs_categoria_comercio.json"
path = 'salida/productos_cat'+fecha+'.json'

with open('locales_no_cat.json', 'r') as file:
    locales = json.load(file)

with open(ruta_matchs_config, "r") as archivo:
    matchs = json.load(archivo)

parser = argparse.ArgumentParser()

parser.add_argument("--comercio", type=int, help="Comercio")

args = parser.parse_args()

comercio = args.comercio
VENDOR = 58


def scroll_hasta_el_final(driver):
    last_scroll_position = 0
    while True:
        # Mover el scroll hasta el final de la página actual
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        time.sleep(2)
        current_scroll_position = driver.execute_script("return window.pageYOffset")

        # Si no hay más contenido para mostrar (es decir, no se ha desplazado más), salir del bucle
        if current_scroll_position == last_scroll_position:
            break

        last_scroll_position = current_scroll_position

def obtener_contenido_por_id(html, id_):
    soup = BeautifulSoup(html, 'html.parser')
    elemento = soup.find(id=id_)
    if elemento:
        return str(elemento)
    else:
        return None
    
def obtener_elementos_con_data_qa(html):
    elementos = []
    soup = BeautifulSoup(html, 'html.parser')
    elementos_con_data_qa = soup.find_all(attrs={"data-qa": True})
    for elemento in elementos_con_data_qa:
        html_interno = str(elemento.contents)
        valor_data_qa = elemento.get("data-qa")
        texto_h4 = elemento.find("h4").text if elemento.find("h4") else None
        contenido_p = elemento.find("p").text if elemento.find("p") else None
        texto_chakra_skeleton = elemento.find(class_="chakra-skeleton").text if elemento.find(class_="chakra-skeleton") else None
        elementos.append({
            #"html_interno": html_interno,
            "data_qa": valor_data_qa,
            "titulo": texto_h4,
            "descripcion": contenido_p,
            "precio": texto_chakra_skeleton
        })
    return elementos


options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

url = locales[comercio]["url"]
print("Consultando URL:", url)

driver.get(url)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
            
scroll_hasta_el_final(driver)

contenido = driver.page_source
contenido = obtener_contenido_por_id(contenido, 'restaurantLayoutContainer')

todos_los_productos = []

if contenido != None:
    productos = obtener_elementos_con_data_qa(contenido)
    for producto in productos:
        
        if producto['titulo'] != None:
            nuevo_prod = {}
            nuevo_prod['vendor_id'] = VENDOR
            nuevo_prod['name'] = producto['titulo'] +' - '+ producto['descripcion']
            nuevo_prod['name'] = nuevo_prod['name'].strip()
            try:
                nuevo_prod['price'] = float(producto['precio'].replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").replace(",", ".").strip())
            except:
                print(producto['precio'], "no se puede procesar")
                continue
            nuevo_prod['is_ext'] = producto['data_qa']

            solo_comercio = url.split("/")[-1]
            nuevo_prod['branch_id'] = matchs["comercios"][solo_comercio]
            nuevo_prod['category'] = matchs["categorias"]["no catalogado"]
            todos_los_productos.append(nuevo_prod)
            print(nuevo_prod)

    try:
        with open(path, 'r') as file:
            todos_los_productos = todos_los_productos + json.load(file)
    except:
        print("No se pudo cargar archivo dump de productos catalogados")

    with open(path, 'w') as file:
        json.dump(todos_los_productos, file)
        todos_los_productos = []