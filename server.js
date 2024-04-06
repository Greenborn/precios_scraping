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

    axios.post(process.env.URL_BACK  + "/publico/productos/importar" , data)
        .then(function (response) {
            console.log(response.data);
            socket.emit('registrar_precio', response.data);
        })
        .catch(function (error) {
            let error_r = errores_envios['fallo_conexion']['registrar_precio']
            error_r.push({ "data": data, "error": error });
            console.log("Error al realizar petición, errores hasta el momento: ", error_r.length );
        })
  });

  socket.on('registrar_oferta', ( data ) => {
    console.log('registrar_oferta')

    axios.post(process.env.URL_BACK  + "/publico/productos/importar_oferta" , data)
        .then(function (response) {
            console.log(response.data);
            socket.emit('registrar_oferta', response.data);
        })
        .catch(function (error) {
            let error_r = errores_envios['fallo_conexion']['registrar_oferta']
            error_r.push({ "data": data, "error": error });
            console.log("Error al realizar petición, errores hasta el momento: ", error_r.length );
        })
  });

  socket.on('disconnect', () => {
    console.log(`disconnect ${socket.id}`);
  });
});

httpServer.listen(port, () => console.log(`server listening on port ${port}`));