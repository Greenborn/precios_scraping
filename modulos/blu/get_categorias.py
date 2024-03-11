#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.puntoblu.com.ar/"

print("haciendo petición a: ", URL)
response = requests.get(URL)
response = response.text

categorias = {}

soup = BeautifulSoup(response, 'html.parser')

categorias = {}

menu = soup.find(class_="ub-mega-menu")
conte = menu.find_all("li")

for cat in conte:
    enlace = cat.find("a")

    if enlace == None:
        print("No se encontro enlace")
        continue

    if cat.find("ul") != None:
        print("Tiene sub categorias")
        continue
    
    categorias[enlace.text.strip()] = { "category":"", "sub_items": [], "url": enlace.get("href") }
    print(categorias[enlace.text.strip()])
    print("")

with open('categorias.json', 'w') as file:
    json.dump(categorias, file)
    print('categorias.json actualizado!')