require("dotenv").config()
const express   = require('express');
let app         = express();
const expressWs = require('express-ws')(app);
const uuid      = require("uuid")

expressWs.getWss().on('connection', function(ws) {
    ws['id_conexion'] = uuid.v4()
  });
  
  app.ws('/', function(ws, req) {  
    ws.on('message', function(msg) {
  
      let msgJson = null
  
      try {
        msgJson = JSON.parse( msg )
        console.log(msgJson)
  
        if (msgJson.hasOwnProperty('accion')){
          
          switch(msgJson.accion){  
            case 'registro_promo':
              
            break;
          }
          
        }
      } catch( error ){
        console.log('error', error)
      }
      
    });
  
  });
  
  app.listen(process.env.PUERTO);
  console.log('puerto', process.env.PUERTO)