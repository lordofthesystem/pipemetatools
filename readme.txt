#Ambiente web

#Instalar
conda create -n web python=3.11
conda activate web
pip install fastapi uvicorn pandas
pip install polars

#Rodar
conda activate web
uvicorn main:app --reload --host 0.0.0.0 --port 8010
http://10.20.34.31:8010/


