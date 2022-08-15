![Texto alternativo opcional si no se carga la imagen](https://www.metricser.com/wp-content/uploads/2019/09/HOR-blanco-600x200.png) 

## Python 3.6.8 no superior
# Gotet Twitter Stream 

> se aconseja usar VisualCode ya que se tiene los launcher establecidos 

#  Pasos a seguir para compilar 

1. Install pip virtualenv
``` 
pip install virtualenv
``` 
2. creat virtual env
``` 
virtualenv env
``` 
3. seleccionar env
``` 
# Linux
source env/bin/activate

# windows
.\env\Scripts\activate  

``` 
4. instalar paquetes relacionados
``` 
pip install -r requirements.txt
``` 
#  Archivos de ambiente 
Para cada ambiente se tiene un archivo de Sheet Google como configuracion inicial y esta ubucado en este archivo  

https://docs.google.com/spreadsheets/d/1QybmFeM3iF0kgvWRwnG1f4SsKgK_C8CWnAORM8890MI/edit#gid=1916605349



#  Archivos de Configuraciones 

Para cada uno de los Ambientes se tiene un archivo de configuracion por Ambiente el cual se detalla abajo 

| Ambiente | SHEET ID |
| :---: | :---: |
| Produccion | 1ITI8clviwefq2mgQIyk5Mqemc1KLJn8AeBVt9WX6ODk |
| QA | 1GuROs_3KzBpIn3pbwVlbWYcdK4XX3YFJi7bxV5xSaWc |
| DESARROLLO | 19KKM1_6Y-her3lQKnZ7vPV1wZkLuSB_vdKxMnAHLDkc |
| PreProducion | 1TOTaXih1ZTXErdJQaPCtJ5CREmdMNBXoKrudvu3_d8o |



#  Pasos para construir .exe

1. Construir el ejecutable
``` 
pyinstaller .\StreamMain.spec
``` 

Nota: Debe tener cuidado en no ejecutar el comando en el archivo Stream*.py debido a que pierde la configuracion de trasfomacion del .exe original 

## Gracias