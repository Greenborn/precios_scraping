
const {PythonShell} =require('python-shell');
const fs = require("fs")
const os = require('os-utils')

const EJECUCION_TICK = 2000
const USO_PROC_RUN   = 0.8

let habilitados  = []
let ejecutados   = []
let por_ejecutar = []

async function ejecutar_bot( item, estado_bot ){
    return new Promise(async (resolve, reject) => {
        try{
            console.log('Ejecutando: ', item, estado_bot)
            let parametros = [
                '--ruta_categorias', __dirname+'/modulos/'+item["d"]+'/categorias.json',
                '--ruta_config', __dirname+'/modulos/config.json'
            ]

            if (estado_bot !== undefined){
                parametros.push( '--categoria_inicio_id' )
                parametros.push( estado_bot["category"] )
            }

            let options = {
                mode: 'text',
                pythonOptions: ['-u'], // get print results in real-time
                args: parametros
            }

            await PythonShell.run(__dirname+'/modulos/'+item["d"]+'/'+item["e"]+'.py', options, function (err, result){
                if (err) {
                    console.log(err)
                    por_ejecutar = [item].concat(por_ejecutar)
                    resolve(false)
                }
                console.log('result: ', result.toString())
                resolve(true)
            })
        } catch(e) {
            console.log('error en ejecucion de bot, se agrega a listado para nueva ejecucion',e)
            por_ejecutar = [item].concat(por_ejecutar)
            resolve(false)
        }
    })
}

fs.readFile("./modulos/habilitados.json", function(err, data) {
    // Converting to JSON
    habilitados  = JSON.parse(data);
    por_ejecutar = [...habilitados]
});

exports.comenzar_ejecucion = ( estados_bots ) => {
    console.log(estados_bots)
    setInterval( async ()=> {
        os.cpuUsage(async function(v){
            console.log( 'CPU Usage (%): ' + v )
    
            if (v < USO_PROC_RUN && por_ejecutar.length > 0){
                let a_ejecutar = por_ejecutar.pop()
                ejecutados.push(a_ejecutar)
    
                await ejecutar_bot( a_ejecutar, estados_bots[a_ejecutar["branch_id"]] )
            }
        })
    }, EJECUCION_TICK )
}