import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
from bs4 import BeautifulSoup
import time

# Cargar el archivo locales.json en memoria
with open('locales.json', 'r') as file:
    locales = json.load(file)

#Cargar el archivo estado.json
with open('estado.json', 'r') as file:
    estado = json.load(file)

    if (estado["ultimo_sitio"] == None):
        estado["ultimo_sitio"] = {}
        estado["ultimo_sitio"]["url"] = ""

fecha = datetime.datetime.now().strftime("%Y%m%d")
BASE_URL = "https://www.rappi.com.ar"

def scroll_hasta_el_final(driver):
    window_height = driver.execute_script("return window.innerHeight")
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

def transformar_url(url):
    url = url.replace(BASE_URL+"/", "")
    url = url.replace("/", "__")
    url = url.replace(".", "_")
    url = url + "__"
    return url

# Función para guardar el contenido en un archivo con el nombre de la URL concatenado con la fecha
def guardar_contenido(url, contenido):
    nombre_archivo = f"{transformar_url(url)}_{fecha}.html"

    with open("data/"+nombre_archivo, 'w') as file:
        file.write(contenido)
    print(f"Contenido guardado en el archivo {nombre_archivo}")

def obtener_contenido_por_dataqa(html, dataqa):
    soup = BeautifulSoup(html, 'html.parser')
    elemento = soup.find(attrs={'data-qa': dataqa})
    if elemento:
        return str(elemento)
    else:
        return None

def obtener_contenido_por_id(html, id_):
    soup = BeautifulSoup(html, 'html.parser')
    elemento = soup.find(id=id_)
    if elemento:
        return str(elemento)
    else:
        return None
    
def obtener_contenido_por_clase(html, clase):
    soup = BeautifulSoup(html, 'html.parser')
    elementos = soup.find_all(class_=clase)
    if elementos:
        return [str(elemento) for elemento in elementos]
    else:
        return None

tiene_catalogo = {}

def actualizar_config_locales():
    with open('locales.json', 'w') as file:
        json.dump(locales, file)
        print('Locales.json actualizado')

def actualizar_estado():
    with open('estado.json', 'w') as file:
        json.dump(estado, file)
        print('estado.json actualizado')

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

def hacer_clic_por_texto(driver, texto):
    try:
        elemento = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{texto}')]")))
        elemento.click()
    except:
        print("No se pudo hacer clic en el elemento")

def obtener_elementos_sub_sub_cat(html):
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

# Función para abrir cada URL y guardar el contenido
def abrir_urls():
    paso_sub_categoria = False
    url_local_encontrada = False
    url_categoria_encontrada = False

    productos_no_cat = {}
    productos_cat = {}

    try:
        with open('salida/productos_cat'+fecha+'.json', 'r') as file:
            productos_cat = json.load(file)
    except:
        print("No se pudo cargar archivo dump de productos catalogados")
    
    try:
        with open('salida/productos_no_cat'+fecha+'.json', 'r') as file:
            productos_no_cat = json.load(file)
    except:
        print("No se pudo cargar archivo dump de productos no catalogados")
    
    options = webdriver.ChromeOptions()

    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(BASE_URL)
        
        for elemento in locales:
            if (estado['ultimo_sitio'] == ""):
                estado['ultimo_sitio'] = elemento['url']
            if (elemento['url'] != estado['ultimo_sitio'] and not url_local_encontrada):
                continue
            else:
                if elemento['url'] == estado['ultimo_sitio']:
                    url_local_encontrada = True
            estado['ultimo_sitio'] = elemento['url']
            actualizar_estado()            

            if elemento['tiene_catalogo']:
                url = elemento['url'] + "/catalogo"
                
                try:
                    driver.get(url)
                except:
                    print("Error atajado 160")
                    continue
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))

                scroll_hasta_el_final(driver)

                contenido = driver.page_source
                contenido = obtener_contenido_por_dataqa(contenido, 'wrapper-component')

                if contenido == None:
                    tiene_catalogo[url] = False
                else:
                    guardar_contenido(url, contenido)
                    tiene_catalogo[url] = True
                    elemento['enlaces_categorias'] = obtener_enlaces_con_info(contenido)
                    actualizar_config_locales()

                    for enlace in elemento['enlaces_categorias']:
                        if (estado['ultima_categoria'] == ""):
                            estado['ultima_categoria'] = enlace['url']
                        if (enlace['url'] != estado['ultima_categoria'] and not url_categoria_encontrada):
                            continue
                        else:
                            if enlace['url'] == estado['ultima_categoria']:
                                url_categoria_encontrada = True
                        estado['ultima_categoria'] = enlace['url']
                        actualizar_estado()                    

                        print(enlace)
                        sub_url = BASE_URL + enlace['url']
                        print("-> ingresando a sub categoria:"+ sub_url)
                        try:
                            driver.get(sub_url)
                        except:
                            print("Error atajado 184")
                            continue
                        
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))

                        if not elemento['url'] in productos_cat:
                            productos_cat[elemento['url']] = {}
                        
                        if not sub_url in productos_cat[elemento['url']]:
                            productos_cat[elemento['url']][sub_url] = {}

                        contenido_sub = driver.page_source
                        see_all = obtener_contenido_por_clase(contenido_sub,"wrapper-see-all")
                        for sub_cat in see_all:
                            enlaces_cat = obtener_enlaces_con_info( sub_cat )
                            
                            for enlace_sub_sub in enlaces_cat:
                                if (estado['ultima_sub_categoria'] == ""):
                                    estado['ultima_sub_categoria'] = enlace_sub_sub['url']
                                if (enlace_sub_sub['url'] != estado['ultima_sub_categoria'] and not url_categoria_encontrada):
                                    continue
                                else:
                                    if enlace_sub_sub['url'] == estado['ultima_sub_categoria']:
                                        url_categoria_encontrada = True
                                estado['ultima_sub_categoria'] = enlace_sub_sub['url']
                                actualizar_estado()

                                productos_cat[elemento['url']][sub_url][enlace_sub_sub['url']] = []

                                sub_sub_url = BASE_URL + enlace_sub_sub['url']
                                print("-----> sub sub categoria: "+ sub_sub_url)
                                try:
                                    driver.delete_all_cookies()
                                    driver.execute_script("window.localStorage.clear()")
                                    driver.execute_script("window.sessionStorage.clear()")

                                    driver.get(sub_sub_url)

                                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))

                                    hacer_clic_por_texto(driver, 'Ver más')
                                    time.sleep(3)

                                    contenido_sub_sub = driver.page_source
                                    
                                    wrapper_sub_sub= obtener_contenido_por_dataqa(contenido_sub_sub, 'wrapper-component')
                                    productos_cat[elemento['url']][sub_url][enlace_sub_sub['url']] = obtener_elementos_sub_sub_cat(wrapper_sub_sub)

                                    with open('salida/productos_cat'+fecha+'.json', 'w') as file:
                                        json.dump(productos_cat, file)
                                        print('productos_cat'+fecha+'.json actualizado!')
                                except:
                                    print("Error atajado 202")
                                    continue

                with open('tiene_catalogo.json', 'w') as file:
                    json.dump(tiene_catalogo, file)
            else:
                url = elemento['url']
                try:
                    driver.delete_all_cookies()
                    driver.execute_script("window.localStorage.clear()")
                    driver.execute_script("window.sessionStorage.clear()")
                    driver.get(url)
                except:
                    print("Error atajado 224")
                    continue
                
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
            
                scroll_hasta_el_final(driver)

                contenido = driver.page_source
                contenido = obtener_contenido_por_id(contenido, 'restaurantLayoutContainer')

                if contenido != None:
                    guardar_contenido(url, contenido)
                    tiene_catalogo[url] = True
                    productos_no_cat[url] = obtener_elementos_con_data_qa(contenido)
                    with open('salida/productos_no_cat'+fecha+'.json', 'w') as file:
                        json.dump(productos_no_cat, file)
                        print('productos_no_cat'+fecha+'.json actualizado!')

    finally:
        driver.quit()

# Llamar a la función para abrir las URLs
abrir_urls()