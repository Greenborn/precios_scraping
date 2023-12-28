import json

with open('locales.json', 'r') as file:
    locales = json.load(file)

with open('tiene_catalogo.json', 'r') as file:
    tiene_catalogo = json.load(file)

nuevo_locales = []

for elemento in locales:
    nuevo = {
        'url': elemento['url'],
        'tiene_catalogo': tiene_catalogo[elemento['url']+"/catalogo"]
    }
    nuevo_locales.append(nuevo)

with open('locales.json', 'w') as file:
    json.dump(nuevo_locales, file)