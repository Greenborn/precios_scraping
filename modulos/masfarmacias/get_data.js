const axios = require("axios")
const fs    = require('fs')
const util  = require('util')

const readFileAsync = util.promisify(fs.readFile)

const BRANCH_ID = 127
const HOY = new Date()
const fecha = String(HOY.getFullYear()) + String(Number(HOY.getMonth() + 1)).toLocaleString(undefined, {
    minimumIntegerDigits: 2,
    minimumFractionDigits: 0
  }) + String(Number(HOY.getDate()).toLocaleString(undefined, {
    minimumIntegerDigits: 2,
    minimumFractionDigits: 0
  }))
const path = 'salida/productos_cat'+fecha+'.json'


async function procesar_categoria( nombre_cat, categoria, t_offset ){
    
    setTimeout( () => {
        console.log( nombre_cat, categoria.url, t_offset )
        axios.get( categoria.url )
            .then(function (response) {
                console.log(response)
                return true
            })
            .catch(function (error) {
                console.log(error)
                return false
            });
    }, t_offset)
    
}

setTimeout(
async() => {
    const data = await readFileAsync("./categorias.json", 'utf8')
    const categorias = JSON.parse(data)

    if (categorias){
        let proms_arr = []
        const keys = Object.keys(categorias)
        t_offset = 100
        for (let i=0; i < keys.length; i++)
            proms_arr.push( procesar_categoria( keys[i], categorias[keys[i]], t_offset*i ) )
        await Promise.all(proms_arr)
    }
}, 100)