import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.greenboutique.com.ar/"

print("haciendo petición a: ", URL)
response = requests.get(URL)
response = response.text


soup = BeautifulSoup(response, 'html.parser')
cat_menu = soup.find(class_="js-desktop-nav-col")
arbol_categorias = {}

categorias = cat_menu.find_all('li', recursive=False)
for cat in categorias:
    sub_cats = cat.find_all('li', recursive=False)
    for sub_cat in sub_cats:
        name  = sub_cat.find("a").text.strip()
        link = sub_cat.find("a").get("href")
        print(name, link)

    
    
