import json
import time
from tweepy import OAuthHandler, Stream
from twarc import Twarc
from http.client import IncompleteRead as http_incompleteRead
from urllib3.exceptions import ProtocolError

from Utilities.utils import cargaConfig, cargaConfig_twitter_credentials
from Utilities.log import log_file
from Utilities.MemCached import memcacheClass
from Controller.FilesController import  getFileConfigByClient, getFileIdTwtterByClient
from Controller.manage_tweet import getStakeholders
from Utilities.theread import callProgram
from Entity.StdOutListener import StdOutListenerClass
from Controller.DriveControler import  getShForClient, getQueryForClient

#Cargará las configuraciones que esten en alrchivo config.ini
log = log_file("C:\Log\Stream\StreamMain.log")   
configuration = cargaConfig(log)
log.log_File=configuration['log']

#Función para limpiar del servidor o pc
def memChachedClear():
    me = memcacheClass(log)
    log.warning("##########################################",True);
    log.warning("#########- Inicia LimpiarCache   -########",True);
    log.warning("##########################################",True);
    me.deletPip();
    if configuration['memcached']:
        me.coustomMemdcached(configuration['cache_port'])
        log.warning("##########################################",True);
        log.warning("#########-    Fin LimpiarCache   -########",True);
        log.warning("##########################################",True);
        log.warning("",True);
        log.warning("",True);

def main():
    if configuration != None:
        #cargar class Log para muestra de logs 
        #Inicio de Extractor
        log.warning("###############################################",True);
        log.warning("#########-INICIANDO PYTHON STREAM MAIN-########",True);
        log.warning("###############################################",True);
        log.warning("",True,True);
        log.warning("Log_File: "+str(configuration['log']),True);
        log.printer("Abriendo canal",True)
        #cargando config de variables 
        accounts = configuration['accounts_ids']
        clients = configuration['clients']
 
        log.printer("URL Base=> "+ configuration['url_base'])
        try:
            log.info("#obtener elementos para la extracción (stakeholders, ids)")
            log.printer("Listado de id's de clientes a consultar")
            log.printer(','.join(map(str, clients)))
            if configuration['sheet_active']:
                if configuration['stream_type'].upper().strip() == 'SH':
                    stakeholders = getShForClient(log,configuration)
                    log.warning("Cuentas SH que vamos a revisar: " + stakeholders,True,True)
                elif configuration['stream_type'].upper().strip() == 'SEARCH':
                    stakeholders = getQueryForClient(log,configuration)
                    log.warning("Cuentas Query que vamos a revisar: " + stakeholders,True,True)
                    
                else:
                    stakeholders = getShForClient(log,configuration)
            else:
                # stakeholders = getStakeholders(clients,log)
                stakeholders = getFileIdTwtterByClient(log,clients)
                if accounts != '' :
                    stakeholders += accounts
            # stakeholders = '140996203'
            if stakeholders != '':
                listSh = stakeholders.split(', ') 
            else:
                listSh = []
            
            status = True
        except  Exception as e:
            status = False
            log.error("Error al obtener los stakeholders:"+str(e),"getStakeholders",True,True)

        if status and len(listSh) > 0:
            log.info("Ingreso existen cuentas SH extractTweet",True,True)
            extractTweet(stakeholders)
        else:
            if len(listSh) == 0:
                log.error("Error al sin SH los stakeholders-status :false No hay SH",True,True)
            else:
                log.error("Error al obtener los stakeholders-status :false ",True,True)
                main()

#Funcion para extrar los tweets de los Sh de los clientes, en ella hanra dos opciones Twarc y Tweepy
def extractTweet(stakeholders):
    try:
        # stakeholders = '140996203'
        listener = StdOutListenerClass(log,configuration)
        if listener.memoriStatus:
            error_delay = configuration['sleep_error']
            try:  
                if(configuration['stream']):
                    log.warning("Ingreso Stream",True)
                    #apertura de Escucha stream y creacion token Twitter
                    configCredential = cargaConfig_twitter_credentials(log)
                    print(configCredential)
                    CONSUMER_KEY = configCredential['CONSUMER_KEY'] #Config.twitter_credentials.CONSUMER_KEY
                    CONSUMER_SECRET = configCredential['CONSUMER_SECRET'] #Config.twitter_credentials.CONSUMER_SECRET
                    ACCESS_TOKEN = configCredential['ACCESS_TOKEN'] #Config.twitter_credentials.ACCESS_TOKEN
                    ACCESS_TOKEN_SECRET = configCredential['ACCESS_TOKEN_SECRET'] #Config.twitter_credentials.ACCESS_TOKEN_SECRET
                    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
                    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
                    stream = Stream(auth, listener)
                    if configuration['stream_type'].upper().strip() == 'SH':
                        stream.filter(follow=[stakeholders], stall_warnings=True)
                    elif configuration['stream_type'].upper().strip() == 'SEARCH':
                        listener.type = 'twitterQuery'
                        stream.filter(track=[stakeholders], stall_warnings=True)
                    else:
                        stream.filter(follow=[stakeholders], stall_warnings=True)
                else:
                    log.warning("Ingreso Twarc",True)
                    configCredential = cargaConfig_twitter_credentials(log)
                    print(configCredential)
                    CONSUMER_KEY = configCredential['CONSUMER_KEY'] #Config.twitter_credentials.CONSUMER_KEY
                    CONSUMER_SECRET = configCredential['CONSUMER_SECRET'] #Config.twitter_credentials.CONSUMER_SECRET
                    ACCESS_TOKEN = configCredential['ACCESS_TOKEN'] #Config.twitter_credentials.ACCESS_TOKEN
                    ACCESS_TOKEN_SECRET = configCredential['ACCESS_TOKEN_SECRET'] #Config.twitter_credentials.ACCESS_TOKEN_SECRET
                    twarc = Twarc(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
                    if configuration['stream_type'].upper().strip() == 'SH':
                        for tweet in twarc.filter(follow=[stakeholders]):
                            listener.on_data(json.dumps(tweet))
                    elif configuration['stream_type'].upper().strip() == 'SEARCH':
                        listener.type = 'twitterQuery'
                        for tweet in twarc.filter(track=[stakeholders]):
                            listener.on_data(json.dumps(tweet))
                    else:
                        for tweet in twarc.filter(follow=[stakeholders]):
                            listener.on_data(json.dumps(tweet))
            except (http_incompleteRead, ProtocolError) as e:
                log.error("http_incompleteRead or ProtocolError:"+str(e),"extractTweet",True,True)
                log.warning("Restarting stream filter en "+str(error_delay)+" segundos... ~~~",True,True)
                time.sleep(error_delay)
                main()
            except RateLimitExceeded as e:
                log.error("RateLimitExceeded por el cliente:"+str(e),"extractTweet",True,True)
                log.error("Segundos de pausa indicados en excepcion: {}".format(e.sleep_seconds),"extractTweet",True,True)
                main()
            except Exception as e:
                log.error("ERROR CON EL CANAL "+str(e),"extractTweet",True,True)
                main()
    except  Exception as e:
        log.error("Error al extractTweet:"+str(e),"extractTweet",True,True)
        main()

class RateLimitExceeded(Exception):
    def set_sleep_seconds(self, seconds):
        self.sleep_seconds = seconds


memChachedClear()

#Ejecuta los arhcivo .exe
callProgram(log,configuration['pathfile']+'StreamFile.exe')
main()