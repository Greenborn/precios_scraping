
cd modulos/masfarmacias
python get_data.py &
pid16 = $!

cd ..
cd rappi
sh get_data.sh &
pid0 = $!

cd ..
cd monarca
sh get_data.sh &
pid1 = $!

cd ..
cd golopolis
python get_data.py &
pid2 = $!

cd ..
cd emetelas
python get_data.py &
pid3 = $!

cd ..
cd lang
python get_data.py &
pid4 = $!

cd ..
cd elteam
python get_data.py &
pid5 = $!

cd ..
cd kulture
python get_data.py  &
pid6 = $!

cd ..
cd naldo
python get_data.py &
pid7 = $!

cd ..
cd sumahogar
python get_data.py &
pid8 = $!

cd ..
cd otero
python get_data.py  &
pid9 = $!

cd ..
cd mercadonaturaltandil
python get_data.py  &
pid10 = $!

cd ..
cd figlio
python get_data.py  &
pid11 = $!

cd ..
cd promofiesta
python get_data.py  &
pid12 = $!

cd ..
cd greenboutique
python get_data.py  &
pid13 = $!

cd ..
cd libreriatandil
python get_data.py  &
pid18 = $!

cd ..
cd amarillagas
python get_data.py &
pid14 = $!

cd ..
cd farmaciassiempre
python get_data.py &
pid15 = $!



cd ..
cd diarco
python get_data.py &
pid17 = $!

cd ..
cd fava
python get_data.py &
pid19 = $!

cd ..
cd naturaldietetica
python get_data.py &
pid20 = $!

wait $pid0
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
wait $pid12
wait $pid13
wait $pid18
wait $pid14
wait $pid15
wait $pid17
wait $pid16
wait $pid19
wait $pid20

cd ..
cd ..
python genera_salida_conjunta.py

cd resultados
rm -f ../../precios_back/scripts/tmp/*.json
cp *.json ../../precios_back/scripts/tmp/
cd ../../precios_back/scripts
node importar_productos.js