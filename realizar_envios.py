import socketio
import requests
import time

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

cliente = ClienteCoordinador()

headers_ = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/123.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://tiendaschasqui.ar",
    "vendure-token": "csd",
    "Connection": "keep-alive",
}

cont_peticiones = 0
while (True):
    print("Pidiendo registros envio...")
    cliente.sio.emit('get_data_to_send')
    recive = cliente.sio.receive()

    data = recive[1]["data"]

    print("Envio recibido...")
    for info in data:
        if (not "data" in info):
            continue

        #print(info["data"])
        print('Realizando peticion...')
        req_ = requests.post(info['url'], headers=headers_, json=info["data"])
        response = req_.json()
        print(response)
        cont_peticiones = cont_peticiones + 1
        print("Peticiones realizadas: ", cont_peticiones)
        print("")

