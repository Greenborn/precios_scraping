cd modulos/masfarmacias
python3 get_data.py 

cd ..
cd rappi
sh get_data.sh

cd ..
cd monarca
sh get_data.sh

cd ..
cd golopolis
python3 get_data.py

cd ..
cd emetelas
python3 get_data.py

cd ..
cd lang
python3 get_data.py 

cd ..
cd elteam
python3 get_data.py

cd ..
cd kulture
python3 get_data.py 

cd ..
cd naldo
python3 get_data.py

cd ..
cd sumahogar
python3 get_data.py

cd ..
cd otero
python3 get_data.py

cd ..
cd mercadonaturaltandil
python3 get_data.py

cd ..
cd figlio
python3 get_data.py 

cd ..
cd promofiesta
python3 get_data.py 

cd ..
cd greenboutique
python3 get_data.py

cd ..
cd libreriatandil
python3 get_data.py

cd ..
cd amarillagas
python3 get_data.py

cd ..
cd farmaciassiempre
python3 get_data.py

cd ..
cd diarco
python3 get_data.py

cd ..
cd fava
python3 get_data.py

cd ..
cd ..
python3 genera_salida_conjunta.py

cd resultados
rm -f ../../precios_back/scripts/tmp/*.json
cp *.json ../../precios_back/scripts/tmp/
cd ../../precios_back/scripts
node importar_productos.js