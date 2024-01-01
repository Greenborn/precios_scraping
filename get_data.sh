
cd modulos/rappi

sh get_data.sh
sh get_data_1.sh
sh get_data_2.sh
sh get_data_nocat.sh

cd ..
cd monarca
sh get_data.sh 

cd ..
cd golopolis
python get_data.py

cd ..
cd emetelas
python get_data.py

cd ..
cd lang
python get_data.py

cd ..
cd elteam
python get_data.py

cd ..
cd kulture
python get_data.py

cd ..
cd ..
python genera_salida_conjunta.py

cd resultados
rm -f ../../OpenPriceStadisticsBack/scripts/tmp/*.json
cp *.json ../../OpenPriceStadisticsBack/scripts/tmp/
cd ../../OpenPriceStadisticsBack/scripts
python importar_productos.py