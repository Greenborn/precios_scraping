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

with open('locales.json', 'r') as file:
    locales = json.load(file)

with open(ruta_matchs_config, "r") as archivo:
    matchs = json.load(archivo)

parser = argparse.ArgumentParser()

parser.add_argument("--comercio", type=str, help="Comercio")
parser.add_argument("--categoria", type=int, help="Categoria")

args = parser.parse_args()

comercio = args.comercio
categoria = args.categoria
VENDOR = 58

def scroll_hasta_el_final(driver):
    last_scroll_position = 0
    # Hacer scroll hasta el final de la página
    while True:
        # Mover el scroll hasta el final de la página actual
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        current_scroll_position = driver.execute_script("return window.pageYOffset")
        # Si no hay más contenido para mostrar (es decir, no se ha desplazado más), salir del bucle
        if current_scroll_position == last_scroll_position:
            break
        # Actualizar la última posición del scroll
        last_scroll_position = current_scroll_position

def obtener_contenido_por_clase(html, clase):
    soup = BeautifulSoup(html, 'html.parser')
    elementos = soup.find_all(class_=clase)
    if elementos:
        return [str(elemento) for elemento in elementos]
    else:
        return None
    
def obtener_enlaces_con_info(html):
    enlaces = []
    soup = BeautifulSoup(html, 'html.parser')
    elementos_enlace = soup.find_all('a')
    for enlace in elementos_enlace:
        url = enlace['href']
        nombre = enlace.text
        enlaces.append({
            "url": url,
            "nombre": nombre
        })
    return enlaces

def hacer_clic_por_texto(driver, texto):
    try:
        elemento = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{texto}')]")))
        elemento.click()
    except:
        print("No se pudo hacer clic en el elemento")

def obtener_contenido_por_dataqa(html, dataqa):
    soup = BeautifulSoup(html, 'html.parser')
    elemento = soup.find(attrs={'data-qa': dataqa})
    if elemento:
        return str(elemento)
    else:
        return None
    
def obtener_elementos_sub_cat(html):
    elementos = []
    if (html == None):
        return []
    soup = BeautifulSoup(html, 'html.parser')
    elementos_con_data_qa = soup.find_all(attrs={"data-qa": lambda value: value and "product-item" in value})
    for elemento in elementos_con_data_qa:
        html_interno = str(elemento.contents)
        valor_data_qa = elemento.get("data-qa")
        titulo = elemento.find(attrs={"data-qa": "product-name"}).text if elemento.find(attrs={"data-qa": "product-name"}) else None
        descripcion = elemento.find(attrs={"data-qa": "product-description"}).text if elemento.find(attrs={"data-qa": "product-description"}) else None
        precio = elemento.find(attrs={"data-qa": "product-price"}).text if elemento.find(attrs={"data-qa": "product-price"}) else None
        
        elementos.append({
            #"html_interno": html_interno,
            "data_qa": valor_data_qa,
            "titulo": titulo,
            "descripcion": descripcion,
            "precio": precio
        })
    return elementos

url_categoria = BASE_URL + locales[comercio]["enlaces_categorias"][categoria]["url"]
print("Consultando URL:", url_categoria)

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

driver.get(url_categoria)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
scroll_hasta_el_final(driver)

contenido_sub = driver.page_source
see_all = obtener_contenido_por_clase(contenido_sub,"wrapper-see-all")

path = 'salida/productos_cat'+fecha+'.json'

todos_los_productos = []

for sub_cat in see_all:
    enlaces_cat = obtener_enlaces_con_info( sub_cat )
    
    for enlace_sub_cat in enlaces_cat:
        sub_cat_url = BASE_URL + enlace_sub_cat['url']
        print("-> sub categoria: "+ sub_cat_url)

        try:
            driver.delete_all_cookies()
            driver.execute_script("window.localStorage.clear()")
            driver.execute_script("window.sessionStorage.clear()")

            driver.get(sub_cat_url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))

            hacer_clic_por_texto(driver, 'Ver más')
            time.sleep(3)
        except:
            print("error!")
            continue

        contenido_sub_cat = driver.page_source
                                    
        wrapper_sub_cat = obtener_contenido_por_dataqa(contenido_sub_cat, 'wrapper-component')
        productos = obtener_elementos_sub_cat(wrapper_sub_cat)

        
        for producto in productos:
            nuevo_prod = {}
            nuevo_prod['vendor_id'] = VENDOR
            nuevo_prod['name'] = producto['titulo'] +' - '+ producto['descripcion']
            nuevo_prod['name'] = nuevo_prod['name'].strip()
            nuevo_prod['price'] = float(producto['precio'].replace("/u", "").replace("/kg", "").replace("$", "").replace(".", "").replace(",", ".").strip())
            nuevo_prod['is_ext'] = producto['data_qa']

            solo_cat = url_categoria.split("/")[-1]
            solo_sub_cat = sub_cat_url.split("/")[-1]
            print(nuevo_prod)
            print(solo_cat, ' ',solo_sub_cat)
            if not solo_cat in matchs['categorias'] or not solo_sub_cat in matchs['categorias'][solo_cat]:
                print('Se omite producto no hay categoria')
                print(solo_cat, ' ',solo_sub_cat)
                with open("categorias_faltantes.csv", "a", newline="") as archivo_csv:
                    writer = csv.writer(archivo_csv)
                    writer.writerow([solo_cat, solo_sub_cat])
                continue
            
            solo_comercio = comercio.split("/")[-1]
            nuevo_prod['branch_id'] = matchs["comercios"][solo_comercio]
            
            if (solo_cat in matchs["categorias"]):
                nuevo_prod['category'] = matchs["categorias"][solo_cat][solo_sub_cat]
            else:
                nuevo_prod['category'] = -1
            
            print(nuevo_prod)
            todos_los_productos.append(nuevo_prod)

        try:
            with open(path, 'r') as file:
                todos_los_productos = todos_los_productos + json.load(file)
        except:
            print("No se pudo cargar archivo dump de productos catalogados")

        with open(path, 'w') as file:
            json.dump(todos_los_productos, file)
            todos_los_productos = []