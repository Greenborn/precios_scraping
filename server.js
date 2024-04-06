require("dotenv").config()

const express = require('express');
const { createServer } = require("http");
const { Server } = require("socket.io");
const axios = require('axios');

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer);

const port = process.env.PORT || 5000;

app.use(express.static(__dirname + '/latency_public'));

let errores_envios = {
    'fallo_conexion': {
        'registrar_precio': [],
        'registrar_oferta': []
    }
}

let envios_server = {
    'registrar_precio': {
        "data_enviar":[],
        "data_enviada": [],
        "data_error": [],
        "url": process.env.URL_BACK  + "/publico/productos/importar"
    },
    'registrar_oferta': {
        "data_enviar":[],
        "data_enviada": [],
        "data_error": [],
        "url": process.env.URL_BACK  + "/publico/productos/importar_oferta"
    }
}

io.on('connection', socket => {
  console.log(`connect ${socket.id}`);

  socket.on('cliente_conectado', () => {
    console.log('Msg conectado');
    socket.emit('conexion_aceptada', {
        status: true
    });
  });

  socket.on('registrar_precio', ( data ) => {
    console.log('registrar_precio')
    envios_server['registrar_precio'].data_enviar.push(data)
  });

  socket.on('registrar_oferta', ( data ) => {
    console.log('registrar_oferta')
    envios_server['registrar_oferta'].data_enviar.push(data)
  });

  socket.on('disconnect', () => {
    console.log(`disconnect ${socket.id}`);
  });
});

const INTERVALO_ENVIO = 100
const RAFAGAS_ENVIO = 1

async function procesar_envios() {
    let tipos_envios = Object.keys(envios_server)
    for (let i = 0; i < tipos_envios.length; i++) {
        for (let j = 0; j < RAFAGAS_ENVIO; j++) {
            let envio_info  = envios_server[tipos_envios[i]]
            let lista_envio = envio_info.data_enviar
            let url_envio   = envio_info.url
            let cantidad = lista_envio.length
            if (cantidad > 0) {
                let elemento = lista_envio.pop()
                console.log( tipos_envios[i],' Por enviar ', cantidad, ' enviadas ', envio_info.data_enviada.length, ' errores ', envio_info.data_error.length)
                axios.post(url_envio, elemento)
                    .then(function (response) {
                    //console.log(response.data)
                        //Si se obtine codigo 200, se envia a la lista de enviadas
                        envio_info.data_enviada.push( elemento )
                    })
                    .catch(function (error) {
                        //Caso contrario se reporta y se enviua a la lista de errores
                    //console.log("Error al realizar petición", cantidad );
                        envio_info.data_error.push( elemento )
                    })
            }
        }
    }
    return
}

setInterval(async () => {
    await procesar_envios()
}, INTERVALO_ENVIO)

httpServer.listen(port, () => console.log(`server listening on port ${port}`));