require("dotenv").config()

const fs = require("fs")
const express = require('express');
const { createServer } = require("http");
const { Server } = require("socket.io");
const BotsCtrl = require('./server_control_bots.js')

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer);

const port = process.env.PORT || 5000;

const INTERVALO_GUARDADO = 10000
const LOTE_ENVIO_CANT  = 100

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

  socket.on('get_data_to_send', () => {
    console.log('enviador pide data');
    prox_data = []
    for (let i=0; i < TIPOS_ENVIO.length; i++){
        let element = runtime.envios_server[TIPOS_ENVIO[i]].data_enviar.pop()
        if (!element?.key) continue
        let enviar = {
            key: element.key,
            lst_importa: [element]
        }

        for (let j=0; j < LOTE_ENVIO_CANT; j++){
            let element_ = runtime.envios_server[TIPOS_ENVIO[i]].data_enviar.pop()
            if (!element_?.key) break
            enviar.lst_importa.push(element_)
        }

        console.log('Seteados para enviar: ', enviar.lst_importa.length, ', faltan: ', runtime.envios_server[TIPOS_ENVIO[i]].data_enviar.length, ' ', TIPOS_ENVIO[i])
        
        prox_data.push({ 
            "data": enviar,     
            "url": runtime.envios_server[TIPOS_ENVIO[i]].url}
        )
    }
    socket.emit('data_to_send', {
        status: true, data: prox_data
    });
  })

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
