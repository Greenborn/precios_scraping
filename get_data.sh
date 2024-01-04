cd modulos/rappi
sh get_data_nocat.sh &
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
python get_data.py  &
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
python get_data.py &
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
python get_data.py &
pid10 = $!

cd ..
cd figlio
python get_data.py &
pid11 = $!

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

cd ..
cd ..
python genera_salida_conjunta.py

cd resultados
rm -f ../../OpenPriceStadisticsBack/scripts/tmp/*.json
cp *.json ../../OpenPriceStadisticsBack/scripts/tmp/
cd ../../OpenPriceStadisticsBack/scripts
python importar_productos.py