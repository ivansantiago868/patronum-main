from Utilities.mq import mqClass 
from Utilities.utils import cargaConfig, cifradoCesar
from Utilities.log import log_file
from Utilities.MemCached import memcacheClass
from Utilities.timeScan import timeClass
from Controller.FilesController import getListChannelByStakeholderAll_facebook , getListChannelByStakeholderAll, getListPortsByClientAll, GetPortByCliet_id
from Controller.manage_tweet import routerTwette
from Utilities.theread import callProgram
import json
import ast

#Cargará las configuraciones que esten en alrchivo config.ini
log = log_file("C:\Log\Stream\StreamRouter.log")     
configuration = cargaConfig(log)
log.log_File=configuration['log']
ports = getListPortsByClientAll()
channel = getListChannelByStakeholderAll()
channel_facebook = getListChannelByStakeholderAll_facebook()
configuration['listIdTw'] = ''
conteo =  1

mq1 = mqClass(log)
#Función para limpiar la cola de la lista de clientes que esten en la configuración
def memChachedClear():
    clients = configuration['clients']
    if configuration['memcached']:
        me = memcacheClass(log)
        log.warning("##########################################",True);
        log.warning("#########- Inicia LimpiarCache   -########",True);
        log.warning("##########################################",True);
        me.deletPip();
        me.createMemcached(clients)
        log.warning("##########################################",True);
        log.warning("#########-    Fin LimpiarCache   -########",True);
        log.warning("##########################################",True);
        log.warning("",True);
        log.warning("",True);
    else:
        log.warning("##########################################",True);
        log.warning("#########- Inicia Declara MQ     -########",True);
        log.warning("##########################################",True);
        for client in clients:
            mq1.declare("client"+str(client))
        log.warning("##########################################",True);
        log.warning("#########-    Fin Declara MQ     -########",True);
        log.warning("##########################################",True);
        log.warning("",True);
        log.warning("",True);
def main():
    log.warning("###############################################",True);
    log.warning("#########-INICIANDO PYTHON STREAM ROUTER-########",True);
    log.warning("###############################################",True);
    log.warning("",True,True);
    log.warning("Log_File: "+str(configuration['log']),True);
    log.printer("Abriendo Rabbit MQ",True)
    mq = mqClass(log)
    # mq.declare(str(configuration['cache_port']))
    try:
        mq.consume(str(configuration['cache_port']),callback)
        mq1.reconect(log)
        ## mq consume cola con type facebook
        main()
    except Exception as e:
        log.error("StreamRouter => %s  " % (e),True,True)
        main()

#Función para recibir la informacion del consume y después redirigirlo a la cola del cliente 
def callback(ch,method, properties, body):
    try:
        clients = configuration['clients']
        dict_body = json.loads(body)
        if dict_body['type'] == 'facebook':
            channel_dt = channel_facebook
        elif dict_body['type'] == 'rss':
            channel_dt = channel
            dict_body['data']['id_str'] = cifradoCesar(dict_body['data']['url'],7)
        else:
            channel_dt = channel
        if configuration['listIdTw'].find(dict_body['data']['id_str']) < 0 :
            if not routerTwette(log,configuration,body,channel_dt,ports,mq1,clients):
                mq1.reconect(log)
                routerTwette(log,configuration,body,channel,ports,mq1,clients)
            else:
                configuration['listIdTw'] += dict_body['data']['id_str']+' '
        else:
            log.warning(f"ya existe este {dict_body['type']} = {dict_body['data']['id_str']}",True);
    except Exception as e:
        log.error("StreamRouter callback => %s  " % (e),True,True)

memChachedClear()
#Ejecuta los arhcivo .exe
callProgram(log,configuration['pathfile']+'StreamFile.exe')
configuration = cargaConfig(log)
configuration['listIdTw'] = ''
main()