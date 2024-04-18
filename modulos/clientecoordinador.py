import socketio
import argparse
import json

parser = argparse.ArgumentParser()

parser.add_argument("--categoria_inicio", type=str, help="Categoria desde la cual se procesan resultados")
parser.add_argument("--categoria_inicio_id", type=str, help="ID categoria desde la cual se procesan resultados")
parser.add_argument("--ruta_categorias", type=str, help="Ruta de archivo de configuracion de categorias")
parser.add_argument("--ruta_config", type=str, help="Ruta de archivo de configuracion general")
args = parser.parse_args()
CATEGORIA_INICIO    = args.categoria_inicio
CATEGORIA_INICIO_ID = args.categoria_inicio_id
RUTA_CATEGORIAS     = args.ruta_categorias
RUTA_CONFIG         = args.ruta_config

try:
    with open( RUTA_CATEGORIAS ) as archivo_json:
        CATEGORIAS = json.load(archivo_json)
except:
    print("Archivo de categorias no encontrado")

with open( RUTA_CONFIG , "r") as archivo:
    CONFIG = json.load(archivo)

PROCESAR = True
print(CATEGORIA_INICIO, CATEGORIA_INICIO_ID)

if (CATEGORIA_INICIO != None or CATEGORIA_INICIO_ID != None):
    PROCESAR = False

class ClienteCoordinador:
    def __init__(self):
        self.sio = socketio.SimpleClient()
        self.conectar()

    def conectar(self):
        self.sio.connect('http://localhost:7777')

        self.sio.emit('cliente_conectado')
        if (not self.sio.receive()[1]["status"]):
            print("Rechazado")
            exit()