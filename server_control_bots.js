
const {PythonShell} =require('python-shell');
const fs = require("fs")
const os = require('os-utils')

const EJECUCION_TICK = 2000
const USO_PROC_RUN   = 0.75

let habilitados  = []
let ejecutados   = []
let por_ejecutar = []

async function ejecutar_bot( item ){
    console.log('Ejecutando: ', item)

    let options = {
        mode: 'text',
        pythonOptions: ['-u'], // get print results in real-time
        args: [
            '--ruta_categorias', __dirname+'/modulos/'+item+'/categorias.json',
            '--ruta_config', __dirname+'/modulos/config.json'
        ]
    }

    PythonShell.run(__dirname+'/modulos/'+item+'/get_data.py', options, function (err, result){
        if (err) {
            console.log(err)
        }
        console.log('result: ', result.toString())
        res.send(result.toString())
    })
}

fs.readFile("./modulos/habilitados.json", function(err, data) {
    // Converting to JSON
    habilitados  = JSON.parse(data);
    por_ejecutar = [...habilitados]
});


setInterval( async ()=> {
    os.cpuUsage(async function(v){
        console.log( 'CPU Usage (%): ' + v )

        if (v < USO_PROC_RUN && por_ejecutar.length > 0){
            let a_ejecutar = por_ejecutar.pop()
            ejecutados.push(a_ejecutar)

            await ejecutar_bot( a_ejecutar )
        }
    })
}, EJECUCION_TICK )