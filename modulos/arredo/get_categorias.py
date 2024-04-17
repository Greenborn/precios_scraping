#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.arredo.com.ar/ropa-de-cama/cubrecamas?__pickRuntime=appsEtag%2Cblocks%2CblocksTree%2Ccomponents%2CcontentMap%2Cextensions%2Cmessages%2Cpage%2Cpages%2Cquery%2CqueryData%2Croute%2CruntimeMeta%2Csettings&__device=desktop"

print("haciendo petición a: ", URL)
response = requests.get(URL)
response = response.json()

categorias = {}

response = json.loads(response["queryData"][1]["data"])["facets"]["facets"]

for categoria in response:
    print(categoria)
    print("")

with open('categorias.json', 'w') as file:
    json.dump(categorias, file)
    print('categorias.json actualizado!')