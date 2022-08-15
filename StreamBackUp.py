from Utilities.theread import saveJsonMQ, threadingClass
from Utilities.utils import cargaConfig, cifradoCesar
from Utilities.log import log_file
from Utilities.mq import mqClass
from Utilities.utils import JsonToObject,ObjectToJson
from Controller.Tr_BD import Tr_BD
import pyodbc
import json

#Cargará las configuraciones que esten en alrchivo config.ini
log = log_file("C:\Log\Stream\StreamBackUp.log") 
configuration = cargaConfig(log)
configuration['listIdTw'] = ''
#Función para consumir la cola cache_port_bk que este en el config.ini
def main():
    try:   
        mq = mqClass(log)
        mq.consume(str(configuration["bk_telegram"]), callback)
        mq.reconect(log)
        main()
    except Exception as e:
        log.error("StreamBackUp main => %s  " % (e),True,True)


#Mandara a la base de datos la informacion obtenida por el consume
def callback(ch, method, properties, bodyJson):
    try:
        if configuration['threading']:
            p1 =  threadingClass(log)
            arg = (log,configuration,bodyJson,Tr_Bd,)
            p1.selectFunction("saveJsonMQ",'StreamBk',arg)
            p1.start()
        else:
            saveJsonMQ(log,configuration,bodyJson,Tr_Bd)
    except Exception as e:
        log.error("callback main => %s  " % (e),True,True)


try:
    Tr_Bd = Tr_BD(log,'catrina')
    main()
except Exception as e:
    log.error("StreamBackUp Ini => %s  " % (e),True,True)
