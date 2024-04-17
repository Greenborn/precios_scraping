#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.bulonfer.com/ofertas"

print("haciendo petición a: ", URL)
response = requests.get(URL)
response = response.text

categorias = {}

soup = BeautifulSoup(response, 'html.parser')
json_cnt = soup.find_all(class_="vtex-flex-layout-0-x-flexColChild--contenidoDerecho")[1]
json_scr = json_cnt.find("script").text
data_ = json.loads(json_scr)
print(data_)


with open('categorias.json', 'w') as file:
    json.dump(categorias, file)
    print('categorias.json actualizado!')