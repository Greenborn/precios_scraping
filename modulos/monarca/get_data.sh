#!/bin/bash
python get_data.py --ini 1 --fin 1000 &
pid1 = $!

python get_data.py --ini 1001 --fin 2000 &
pid2 = $!

python get_data.py --ini 2001 --fin 3000 &
pid3 = $!

python get_data.py --ini 3001 --fin 4000 &
pid4 = $!

python get_data.py --ini 4001 --fin 5000 &
pid5 = $!

python get_data.py --ini 5001 --fin 6000 &
pid6 = $!

python get_data.py --ini 6001 --fin 7000 &
pid7 = $!

python get_data.py --ini 7001 --fin 8000 &
pid8 = $!

python get_data.py --ini 8001 --fin 9000 &
pid9 = $!

python get_data.py --ini 9001 --fin 10000 &
pid10 = $!

python get_data.py --ini 10001 --fin 11000 &
pid11 = $!

# Esperar a que los subprocesos terminen
wait $pid1
wait $pid2
wait $pid3
wait $pid4
wait $pid5
wait $pid6
wait $pid7
wait $pid8
wait $pid9
wait $pid10
wait $pid11

# Continuar con el script principal
echo "Todos los subprocesos han terminado."

python generar_lista_productos.py
