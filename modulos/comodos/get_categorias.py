#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup

URL = "https://www.comodos.com.ar"

print("haciendo petición a: ", URL)
response = requests.get(URL)
response = response.text

categorias = {}

soup = BeautifulSoup(response, 'html.parser')

cats = soup.find_all(class_="menu-item")
for cat in cats:
    categoria  = cat.find("a").text.strip()
    enlace_cat = cat.find("a").get("href")
    
    categorias[categoria] = { "category":"", "sub_items": [], "url": enlace_cat }
    print(categorias[categoria])
    print("")

with open('categorias.json', 'w') as file:
    json.dump(categorias, file)
    print('categorias.json actualizado!')