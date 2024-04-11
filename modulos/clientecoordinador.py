import socketio

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