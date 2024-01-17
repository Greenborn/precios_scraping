from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from bs4 import BeautifulSoup

URL = "https://www.siemprefarmacias.com.ar"

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

driver.get(URL)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
res_consulta = driver.page_source


soup = BeautifulSoup(res_consulta, 'html.parser')
menu = soup.find(class_="navbar-collapse collapse menu-color2")

arbol_categorias = {}
enlaces = menu.find_all("li")
for enlace in enlaces:
    link = enlace.find("a")
    if link == None:
        continue
    enlace_cat = URL+"/"+link.get("href")
    arbol_categorias[link.text.strip()] = { "category":"", "sub_items": [], "url": enlace_cat }
    print(arbol_categorias[link.text.strip()])
    print("")

with open('categorias.json', 'w') as file:
    json.dump(arbol_categorias, file)
    print('categorias.json actualizado!')