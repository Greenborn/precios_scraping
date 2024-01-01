import json
import requests
from bs4 import BeautifulSoup
import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.naldo.com.ar"

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

print("ingresando a URL: ", URL)
driver.get(URL)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))

res_consulta = driver.page_source

soup = BeautifulSoup(res_consulta, 'html.parser')
cat_menu = soup.find(class_="naldoar-drawer-menu-0-x-sidebarContent")
arbol_categorias = {}

category_menu = soup.find_all("li")
for category in category_menu:
    category_name = category.find("a").text
    link = category.find("a").get("href")
    arbol_categorias[category_name] = { "category": "", "sub_items": [], "url": URL + link }
    print(arbol_categorias[category_name])
    print("")

with open('categorias.json', 'w') as file:
    json.dump(arbol_categorias, file)
    print('categorias.json actualizado!')
