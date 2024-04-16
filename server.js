require("dotenv").config()

const fs = require("fs")
const express = require('express');
const { createServer } = require("http");
const { Server } = require("socket.io");
const axios = require('axios');
const BotsCtrl = require('./server_control_bots.js')

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer);

const port = process.env.PORT || 5000;

const INTERVALO_ENVIO = 100
const REINTENTO_ERR_MOD = 5 
const RAFAGAS_ENVIO = 1
const INTERVALO_GUARDADO = 10000
const ENVIOS_HABILITADOS = true

app.use(express.static(__dirname + '/latency_public'));

let envios_server = {
    'registrar_precio': {
        "data_enviar":[],
        "data_enviada": [],
        "data_error": [],
        "data_error_status": [],
        "url": process.env.URL_BACK  + "/publico/productos/importar"
    },
    'registrar_oferta': {
        "data_enviar":[],
        "data_enviada": [],
        "data_error": [],
        "data_error_status": [],
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

let ciclo_numero = 0

async function procesar_envios() {
    ciclo_numero ++
    let envio_pendiente = envios_server['registrar_precio'].data_enviar.length > 0 
                            || envios_server['registrar_oferta'].data_enviar.length > 0

    if (ciclo_numero % REINTENTO_ERR_MOD == 0 || !envio_pendiente) {
        let tipos_envios = Object.keys(envios_server)
        for (let i = 0; i < tipos_envios.length; i++) {
            let envio_info  = envios_server[tipos_envios[i]]
            let lista_envio = null
            if (ciclo_numero % 2 == 0)
                lista_envio = envio_info.data_error
            else 
                lista_envio = envio_info.data_error_status
            let url_envio   = envio_info.url
            let cantidad    = lista_envio.length
            if (cantidad > 0) {
                let elemento = lista_envio.pop()
                console.log( tipos_envios[i],' Por enviar ', cantidad, ' enviadas ', envio_info.data_enviada.length, ' errores ', envio_info.data_error.length)
                
                if (tipos_envios[i] === 'registrar_precio' && elemento?.name == undefined){
                    envios_server['registrar_oferta'].data_enviar.push(elemento)
                    console.log('recatalogando')
                    return
                } else if (tipos_envios[i] === 'registrar_oferta' && elemento?.titulo == undefined){
                    envios_server['registrar_precio'].data_enviar.push(elemento)
                    console.log('recatalogando')
                    return
                } 
                
                if (ENVIOS_HABILITADOS) {
                    axios.post(url_envio, elemento)
                        .then(function (response) {
                        console.log(response.data)
                            //Si se obtine codigo 200, se envia a la lista de enviadas
                            if (response.data.stat)
                                envio_info.data_enviada.push( elemento )
                            else {
                                envio_info.data_error_status = [elemento].concat(envio_info.data_error_status)
                            }
                        })
                        .catch(function (error) {
                            //Caso contrario se reporta y se enviua a la lista de errores
                        //console.log("Error al realizar petición", cantidad );
                            envio_info.data_error.push( elemento )
                        })
                } else {
                    console.log("envio deshabilitado")
                    envio_info.data_enviada.push( elemento )
                }
            }
        }
        return
    }
    

    let tipos_envios = Object.keys(envios_server)
    for (let i = 0; i < tipos_envios.length; i++) {
        for (let j = 0; j < RAFAGAS_ENVIO; j++) {
            let envio_info  = envios_server[tipos_envios[i]]
            let lista_envio = envio_info.data_enviar
            let url_envio   = envio_info.url
            let cantidad = lista_envio.length
            if (cantidad > 0) {
                let elemento = lista_envio.pop()
                console.log( 
                    tipos_envios[i],
                    ' Por enviar ', cantidad, 
                    ' enviadas ', envio_info.data_enviada.length, 
                    ' errores ', envio_info.data_error.length,  
                    ' errores status ', envio_info.data_error_status.length)
                
                if (tipos_envios[i] === 'registrar_precio' && elemento?.name == undefined){
                    envios_server['registrar_oferta'].data_enviar.push(elemento)
                    console.log('recatalogando')
                    return
                } else if (tipos_envios[i] === 'registrar_oferta' && elemento?.titulo == undefined){
                    envios_server['registrar_precio'].data_enviar.push(elemento)
                    console.log('recatalogando')
                    return
                } 

                if (ENVIOS_HABILITADOS){
                    axios.post(url_envio, elemento)
                        .then(function (response) {
                        console.log(response.data)
                            //Si se obtine codigo 200, se envia a la lista de enviadas
                            if (response.data.stat)
                                envio_info.data_enviada.push( elemento )
                            else {
                                envio_info.data_error_status = [elemento].concat(envio_info.data_error_status)
                            }
                        })
                        .catch(function (error) {
                            //Caso contrario se reporta y se enviua a la lista de errores
                        //console.log("Error al realizar petición", cantidad );
                            envio_info.data_error.push( elemento )
                        })
                } else {
                    console.log("envio deshabilitado")
                    envio_info.data_enviada.push( elemento )
                }
            }
        }
    }
    return
}

setInterval(async () => {
    await procesar_envios()
}, INTERVALO_ENVIO)

let chequeo_runtime_pendiente = true

setInterval(async () => {
    if (chequeo_runtime_pendiente){
        chequeo_runtime_pendiente = false
        let HOY = new Date()
        let fecha = String(HOY.getFullYear())+String(HOY.getMonth())+String(HOY.getDate())
        
        if (fs.existsSync("./resultados/runtime"+fecha+".json")) {
            try {
                console.log("Se encontro archivo runtime, procesando")
                fs.readFile("./resultados/runtime"+fecha+".json", function(err, data) {
                    // Converting to JSON
                    const data_runtime = JSON.parse(data);
                    
                    envios_server['registrar_precio'].data_enviar  = envios_server['registrar_precio'].data_enviar.concat(data_runtime['registrar_precio'].data_enviar)
                    envios_server['registrar_precio'].data_enviada = envios_server['registrar_precio'].data_enviada.concat(data_runtime['registrar_precio'].data_enviada)
                    envios_server['registrar_precio'].data_error   = envios_server['registrar_precio'].data_error.concat(data_runtime['registrar_precio'].data_error)
                    envios_server['registrar_precio'].data_error_status   = envios_server['registrar_precio'].data_error_status.concat(data_runtime['registrar_precio'].data_error_status)

                    envios_server['registrar_oferta'].data_enviar  = envios_server['registrar_oferta'].data_enviar.concat(data_runtime['registrar_oferta'].data_enviar)
                    envios_server['registrar_oferta'].data_enviada = envios_server['registrar_oferta'].data_enviada.concat(data_runtime['registrar_oferta'].data_enviada)
                    envios_server['registrar_oferta'].data_error   = envios_server['registrar_oferta'].data_error.concat(data_runtime['registrar_oferta'].data_error)
                    envios_server['registrar_oferta'].data_error_status   = envios_server['registrar_oferta'].data_error_status.concat(data_runtime['registrar_oferta'].data_error_status)
                });
            } catch (error) {
                console.log(error)
                chequeo_runtime_pendiente = true
            }
        } else {
            console.log("no hay archivo runtime encontrado")
        }
        
    } else {
        let HOY = new Date()
        let fecha = String(HOY.getFullYear())+String(HOY.getMonth())+String(HOY.getDate())
        try {
            fs.writeFile("./resultados/runtime"+fecha+".json", JSON.stringify(envios_server), err => {
                console.log("Done writing"); // Success
            })
        } catch (error) {
            console.log("error al guardar archivo")
        }
        
    }
    return
}, INTERVALO_GUARDADO)

httpServer.listen(port, () => console.log(`server listening on port ${port}`));