import socketio
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--categoria_inicio", type=str, help="Categoria desde la cual se procesan resultados")
args = parser.parse_args()
categoria_inicio = args.categoria_inicio

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