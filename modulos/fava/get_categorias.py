import requests
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://fava.com.ar/"
URL_CAT = "https://fava.com.ar/swmegamenu/index/showpopup?category_id="

print("haciendo petición a: ", URL)
response = requests.get(URL)
response = response.text


soup = BeautifulSoup(response, 'html.parser')

arbol_categorias = {}

conte = soup.find_all(attrs={"data-id": lambda value: value })
for cnt in conte:
    
    peticion_cat = requests.post(URL_CAT+cnt.get("data-id"), headers={
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://fava.com.ar",
        "Referer": "https://fava.com.ar/tecnologia",
        "Cookie": "rontend=8b6da57b8648dcb124080f95cc18a2c2; frontend_cid=k9eHbNFSY2c9jPRR; logglytrackingsession=f1443dc3-b946-47b0-af5a-fa3b9e7d81f3; wpnViewcount=9; TPIDC=8o0zkvly-ynp5fqwdi-5xj32uk9rige7tn-msgpo7i2u6axr5-06rve-3tbh; _gcl_au=1.1.162431421.1706467043; cwdcc=false; external_no_cache=1; cus=false; __zlcmid=1K2mSKXNBX5CCts; wpnLastDenial=1706467243914; cwdscc=true; _wpn_cotpc=1; sdtpc=1; _wpnmvecc=9; _wpnriecc=9; _wpnlvecc=9; _wpnhecc=9",
    })
    response_cat = peticion_cat.json()
    
    soup2 = BeautifulSoup(response_cat["popup_content"], 'html.parser')
    enlaces = soup2.find_all("a")

    for enlace in enlaces:
        name_cat = enlace.text.strip()
        arbol_categorias[name_cat] = { "category":"", "sub_items": [], "url": enlace.get("href") }
        print(arbol_categorias[name_cat])
        print("")

with open('categorias.json', 'w') as file:
    json.dump(arbol_categorias, file)
    print('categorias.json actualizado!')
