import requests
import csv
from datetime import datetime
import argparse

url_base = "http://api.monarcadigital.com.ar/products/id-list?id={}"

parser = argparse.ArgumentParser()

parser.add_argument("--ini", type=int, help="Valor numérico de inicio")
parser.add_argument("--fin", type=int, help="Valor numérico de fin")

args = parser.parse_args()

valor_inicial = args.ini
valor_final = args.fin

fecha = datetime.now().strftime("%Y%m%d")
path = 'salida/productos_cat'+fecha+'.csv'

print("Iniciando en:", valor_inicial)
print("Finalizando en:", valor_final)
numero = valor_inicial

MAX_VACIO = 100
cantidad_vacio = MAX_VACIO

while cantidad_vacio > 0 and numero < valor_final:
    # Construir la URL con el número actual
    url = url_base.format(numero)
    print('Consultando URL: ', url)
    # Realizar la petición GET
    response = requests.get(url)
    print('Respuesta obtenida: ',response)
    print('')
    # Verificar si se obtuvo un resultado vacío
    if not response.json():
        cantidad_vacio = cantidad_vacio - 1
        print('Se obtuvo respuesta vacía')
    else:
        cantidad_vacio = MAX_VACIO

    # Obtener la fecha actual
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Guardar la respuesta en el archivo resultados.csv
    with open(path, "a", newline="") as archivo_csv:
        writer = csv.writer(archivo_csv)
        writer.writerow([fecha_actual, numero, response.text])

    # Incrementar el número
    numero += 1