
const {PythonShell} =require('python-shell');
const fs = require("fs")

let procesos = []

async function ejecutar_bot( item ){
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
    const data_habilitados = JSON.parse(data);
    
    let proms = []
    for (let i=0; i < data_habilitados.length; i++){
        let item = data_habilitados[i]

        proms.push( ejecutar_bot( item ) )
    }

    Promise.all( proms ).then( () => {
        console.log("procesos terminados")
    })
});
