#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.pintureriasambito.com"

print("haciendo petición a: ", URL)
response = requests.get(URL)
response = response.text

categorias = {}

soup = BeautifulSoup(response, 'html.parser')
cat_menu = soup.find(class_="navigation")

cats = cat_menu.find_all("li")
for cat in cats:
    categoria  = cat.find("a").text.strip()
    enlace_cat = cat.find("a").get("href")
    
    categorias[categoria] = { "category":"", "sub_items": [], "url": enlace_cat }
    print(categorias[categoria])
    print("")

with open('categorias.json', 'w') as file:
    json.dump(categorias, file)
    print('categorias.json actualizado!')