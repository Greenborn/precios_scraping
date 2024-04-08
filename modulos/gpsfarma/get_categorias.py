#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://gpsfarma.com"

print("haciendo petición a: ", URL)
response = requests.get(URL)
response = response.text

categorias = {}

soup = BeautifulSoup(response, 'html.parser')
menu = soup.find(class_="navigation")
cats = menu.find_all("li", class_="level2")

print(len(cats))
for cat in cats:
    enlace_url = cat.find("a").get("href")
    enlace_txt = cat.find("a").text.strip()

    print(enlace_url, enlace_txt)
    categorias[enlace_txt] = { "category":"", "sub_items": [], "url": enlace_url }
    print("")


with open('categorias.json', 'w') as file:
    json.dump(categorias, file)
    print('categorias.json actualizado!')