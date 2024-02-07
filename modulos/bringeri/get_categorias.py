#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.bringeri.com.ar"

print("haciendo petición a: ", URL)
response = requests.get(URL)
response = response.text

soup = BeautifulSoup(response, 'html.parser')
cats_menu = soup.find_all(class_="vtex-menu-2-x-menuItem")
arbol_categorias = {}

for cat in cats_menu:
    
    link_cnt = cat.find(class_="vtex-menu-2-x-styledLinkContainer")
    print(link_cnt.find("a").get("href"))
    print("")