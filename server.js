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

const INTERVALO_ARMA_ENVIO = 100
const INTERVALO_ENVIO = 10000
const REINTENTO_ERR_MOD = 5 
const RAFAGAS_ENVIO = 1
const INTERVALO_GUARDADO = 10000
const ENVIOS_HABILITADOS = true
const CANT_ELEMENTOS_IMP = 20 //cantidad de elementos maxima por peticion de importacion

app.use(express.static(__dirname + '/latency_public'));

const TIPOS_ENVIO = [
    'registrar_precio', 'registrar_oferta'
]

let runtime = {
    "envios_server": {
        'registrar_precio': {
            "data_enviar":[],
            "data_enviada": [],
            "data_error": [],
            "data_error_status": [],
            "data_preparada": [{ registros:[], lista: false }],
            "url": process.env.URL_BACK  + "/publico/productos/importar"
        },
        'registrar_oferta': {
            "data_enviar":[],
            "data_enviada": [],
            "data_error": [],
            "data_error_status": [],
            "data_preparada": [{ registros:[], lista: false }],
            "url": process.env.URL_BACK  + "/publico/productos/importar_oferta"
        }
    },
    "estado_bot": {}
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
    const endpoint = 'registrar_precio'
    console.log(endpoint)
    if (runtime.estado_bot[data.branch_id] == undefined){
        runtime.estado_bot[data.branch_id] = {}
    }
    //Se registra última categoria procesada
    runtime.estado_bot[data.branch_id]["category"] = data?.category
    runtime.envios_server[endpoint].data_enviar.push(data)
  });

  socket.on('registrar_oferta', ( data ) => {
    const endpoint = 'registrar_oferta'
    console.log(endpoint)
    runtime.envios_server[endpoint].data_enviar.push(data)
  });

  socket.on('disconnect', () => {
    console.log(`disconnect ${socket.id}`);
  });
});

let ciclo_numero = 0

function hay_envio_pendiente(){
    return runtime.envios_server['registrar_precio'].data_enviar.length > 0 
            || runtime.envios_server['registrar_oferta'].data_enviar.length > 0
}

async function preparar_envios() {
    ciclo_numero ++

    if (ciclo_numero % REINTENTO_ERR_MOD == 0 || !hay_envio_pendiente()) {
        for (let i = 0; i < TIPOS_ENVIO.length; i++) {
            let envio_info  = runtime.envios_server[TIPOS_ENVIO[i]]
            let lista_envio = null
            if (ciclo_numero % 2 == 0)
                lista_envio = envio_info.data_error
            else 
                lista_envio = envio_info.data_error_status
            
            let cantidad    = lista_envio.length
            if (cantidad > 0) {
                let elemento = lista_envio.pop()
                console.log( TIPOS_ENVIO[i],' Por enviar ', cantidad, ' enviadas ', envio_info.data_enviada.length, ' errores ', envio_info.data_error.length)
                
                if (TIPOS_ENVIO[i] === 'registrar_precio' && elemento?.name == undefined){
                    runtime.envios_server['registrar_oferta'].data_preparada.push(elemento)
                    console.log('recatalogando')
                    return
                } else if (TIPOS_ENVIO[i] === 'registrar_oferta' && elemento?.titulo == undefined){
                    runtime.envios_server['registrar_precio'].data_preparada.push(elemento)
                    console.log('recatalogando')
                    return
                } 
                
                if (ENVIOS_HABILITADOS) {
                    envio_info.data_preparada.registros.push(elemento)
                    if (envio_info.data_preparada.registros.length >= CANT_ELEMENTOS_IMP) {
                        envio_info.data_preparada.lista = true
                    }
                    
                } else {
                    console.log("envio deshabilitado")
                    envio_info.data_enviada.push( elemento )
                }
            }
        }
        return
    }
    
    for (let i = 0; i < TIPOS_ENVIO.length; i++) {
        for (let j = 0; j < RAFAGAS_ENVIO; j++) {
            let envio_info  = runtime.envios_server[TIPOS_ENVIO[i]]
            let lista_envio = envio_info.data_enviar

            let cantidad = lista_envio.length
            if (cantidad > 0) {
                let elemento = lista_envio.pop()
                console.log( 
                    TIPOS_ENVIO[i],
                    ' Items Por enviar ', cantidad, 
                    ' enviadas ', envio_info.data_enviada.length, 
                    ' errores ', envio_info.data_error.length,  
                    ' errores status ', envio_info.data_error_status.length)
                
                if (TIPOS_ENVIO[i] === 'registrar_precio' && elemento?.name == undefined){
                    runtime.envios_server['registrar_oferta'].data_enviar.push(elemento)
                    console.log('recatalogando')
                    return
                } else if (TIPOS_ENVIO[i] === 'registrar_oferta' && elemento?.titulo == undefined){
                    runtime.envios_server['registrar_precio'].data_enviar.push(elemento)
                    console.log('recatalogando')
                    return
                } 

                if (ENVIOS_HABILITADOS){
                    let regs_preparados = envio_info.data_preparada
                    let ultimo = regs_preparados[regs_preparados.length - 1]
                    ultimo.registros.push(elemento)
                    if (ultimo.registros.length >= CANT_ELEMENTOS_IMP) {
                        ultimo.lista = true
                        regs_preparados.push({ registros: [], lista: false })
                    }
                } else {
                    console.log("envio deshabilitado")
                    envio_info.data_enviada.push( elemento )
                }
            }
        }
    }
    return
}

async function procesar_envios(){
    for (let i = 0; i < TIPOS_ENVIO.length; i++) {
        const envio_info  = runtime.envios_server[TIPOS_ENVIO[i]]
        if (envio_info.data_preparada.length == 0) continue
        
        
        const url_envio   = envio_info.url
        let encontrado = false
        for (let j = 0; j < envio_info.data_preparada.length; j++) {
            let pack_envio = envio_info.data_preparada[j]
            if (!pack_envio.lista) continue
            if (pack_envio.lista) {
                encontrado = pack_envio
            }
        }

        if (encontrado !== false){
            const ENVIO = { key: encontrado.registros[0].key, lst_importa: encontrado.registros }
            axios.post(url_envio, ENVIO)
                .then(function (response) {
                    console.log(response.data)
                    //Si se obtine codigo 200, se envia a la lista de enviadas
                    if (response.data.stat){
                        envio_info.data_enviada.push( ENVIO )
                        runtime.envios_server[TIPOS_ENVIO[i]].data_preparada.splice(j, 1)
                    } else {
                        envio_info.data_error_status = [encontrado].concat(envio_info.data_error_status)
                    }
                })
                .catch(function (error) {
                    //Caso contrario se reporta y se enviua a la lista de errores
                //console.log("Error al realizar petición", cantidad );
                    envio_info.data_error.push( encontrado )
                })
        }
    }
    return
}

setInterval(async () => {
    await preparar_envios()
}, INTERVALO_ARMA_ENVIO)

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
                    // En runtime se concatena el estado actual al almacenado en el archivo
                    const data_runtime = JSON.parse(data);
                    
                    for (let i=0; i < TIPOS_ENVIO.length; i++){
                        let t_envio       = TIPOS_ENVIO[i]
                        let runtime_envio = runtime.envios_server[t_envio]
                        let file_envios   = data_runtime.envios_server[t_envio]

                        runtime_envio.data_enviar       = runtime_envio.data_enviar.concat(file_envios.data_enviar)
                        runtime_envio.data_enviada      = runtime_envio.data_enviada.concat(file_envios.data_enviada)
                        runtime_envio.data_error        = runtime_envio.data_error.concat(file_envios.data_error)
                        runtime_envio.data_error_status = runtime_envio.data_error_status.concat(file_envios.data_error_status)
                    }
                    runtime.estado_bot = data_runtime.estado_bot

                    BotsCtrl.comenzar_ejecucion( runtime.estado_bot )
                });
            } catch (error) {
                console.log(error)
                chequeo_runtime_pendiente = true
            }
        } else {
            console.log("no hay archivo runtime encontrado")
            BotsCtrl.comenzar_ejecucion( runtime.estado_bot )
        }
        
    } else {
        let HOY = new Date()
        let fecha = String(HOY.getFullYear())+String(HOY.getMonth())+String(HOY.getDate())
        try {
            fs.writeFile("./resultados/runtime"+fecha+".json", JSON.stringify(runtime), err => {
                console.log("Done writing"); // Success
            })
        } catch (error) {
            console.log("error al guardar archivo")
        }
        
    }
    return
}, INTERVALO_GUARDADO)

httpServer.listen(port, () => console.log(`server listening on port ${port}`));
