import threading
from multiprocessing import Process
from Utilities.log import log_file
import time
from subprocess import call
from Controller.manage_tweet import GetShFromMessage,SendTelegram#,SaveTweetByAccount,
from Controller.FilesController import  GetPortByCliet_id, getListPortsByClientAll
from Utilities.utils import cargaConfig, cifradoCesar
import json
from Utilities.utils import JsonToObject, ObjectToJson
from Utilities.FIFO import pila
from Controller.manage_tweet import SaveTweetByAccount,characterizeTwetter
from Utilities.timeScan import timeClass
from Utilities.utils import isDefine
# from Utilities.MemCached import memcacheClass

class threadingClass:
    def __init__(self, log):
        self.log = log
        self.t = threading.Thread(name='ThreadingIni',target=funIni,args=(self.log,))

    #funciones de constructor hilos
    def selectFunction(self,function,name1,arg):
        if function == "time":
            self.t = threading.Thread(target=timerLoop, name= name1,args=arg)
        if function == "display":
            self.t = threading.Thread(target=logDisplay, name= name1,args=arg)
        if function == "saveTwetterCache":
            self.t = threading.Thread(target=saveTwetterCache, name= name1,args=arg)
        # if function == "saveTwetterBd":
        #     self.t = threading.Thread(target=saveTwetterBd, name= name1,args=arg)
        if function == "openMemcached":
            self.t = threading.Thread(target=openMemcached, name= name1,args=arg)
        if function == "main":
            self.t = threading.Thread(target=saveStreamMain, name= name1,args=arg)
        if function == "mqDirecto":
            self.t = threading.Thread(target=mqDirecto, name= name1,args=arg)
        if function == "runStreamSave":
            self.t = threading.Thread(target=runStreamSave, name= name1,args=arg)
        if function == "runStreamTrend":
            self.t = threading.Thread(target=runStreamTrends, name= name1,args=arg)
        if function == "runStreamRss":
            self.t = threading.Thread(target=runStreamRss, name= name1, args=arg)
        if function == "saveJsonMQ":
            self.t = threading.Thread(target=saveJsonMQ, name= name1, args=arg)

    def start(self):
        self.t.start()
    def end(self):
        self.t.terminate()

class multiprocessingClass:
    def __init__(self, log):
        self.log = log
        self.t = Process(target=funIni,args=(self.log,))
    #funciones de constructor hilos
    def selectFunction(self,function,name1,arg):
        if function == "time":
            self.t = Process(target=timerLoop,args=arg)
        if function == "display":
            self.t = Process(target=logDisplay,args=arg)
        if function == "saveTwetterCache":
            self.t = Process(target=saveTwetterCache,args=arg)
        # if function == "saveTwetterBd":
        #     self.t = Process(target=saveTwetterBd,args=arg)
        if function == "openMemcached":
            self.t = Process(target=openMemcached,args=arg)
        if function == "main":
            self.t = Process(target=saveStreamMain,args=arg)
        if function == "mqDirecto":
            self.t = Process(target=mqDirecto,args=arg)
    def start(self):
        self.t.start()
    def end(self):
        self.t.terminate()

#funciones de ekjecicion hilo
def runStreamTrends(log,name,path):
    log.info("Name Threading : "+threading.current_thread().getName()+' threadingClass => Start => runStreamSave '+name,True,True)
    comand = path+'\StreamTrends.exe '
    log.warning(comand,True,True)
    call(comand)

def saveJsonMQ(log,configuration,bodyJson,Tr_Bd):
    body = json.loads(bodyJson)
    bodyData = body['data']
    if body['type'] == 'twitter':
        id_data =  bodyData['id']
    if body['type'] == 'rss':
        id_data = cifradoCesar(bodyData['url'],7)
        bodyData['id_str'] = id_data
    if body['type'] == 'facebook':
        id_data =  bodyData['id_str']
        
    if configuration['listIdTw'].find(str(id_data)+'-'+str(body['client_id'])) < 0 :
        status = Tr_Bd.setTweetandRss(body,bodyJson)
        if status:
            configuration['listIdTw'] += str(id_data)+'-'+str(body['client_id'])+' '
    else:
        log.info(msn=body['type']+":existente a "+str(id_data)+'-'+str(body['client_id']),display=True,dateStatus=False)
def runStreamRss(log, url, path,time):
    log.info("Name Rss : " +threading.current_thread().getName()+' rssClass => Start => runStreamSave '+ url, True, True )
    comand = path+'\StreamRss.exe -t ' + str(time)
    log.warning(comand, True, True)
    call(comand)

#funciones de ekjecicion hilo
def runStreamSave(log,name,cliente,path):
    log.info("Name Threading : "+threading.current_thread().getName()+' threadingClass => Start => runStreamSave '+name,True,True)
    comand = path+'\StreamSave.exe -n '+name+' -c '+str(cliente)
    log.warning(comand,True,True)
    call(comand)

def callProgram(log,command):
    log.warning(command,True,True)
    call(command)
def mqDirecto(log,data,mq,name):
    status_mq = mq.add(data,name)

def openMemcached(log,port):
    log.info("Name Threading : "+threading.current_thread().getName()+' threadingClass => Start => openMemcached '+str(port),True,True)
    comand = 'c:\memcached\memcached.exe -m 512 -p '+str(port)+' -t 8 -v'
    log.warning(comand,True,True)
    call(comand)
    
def saveTwetterCache(log,data,tweet,conteo,pi,mq,list_port,configuration,channel):
    t =  timeClass(log ,threading.current_thread().getName())
    log.info("Name Threading : "+threading.current_thread().getName()+' threadingClass => Start => saveTwetterCache ',True,True)
    try:
        
        if isDefine(tweet,'screen_name'):
            name = tweet['user']['screen_name']
            channel_by_stakeholders = []
            for cbs in channel:
                if cbs.account.upper() == name.upper() or cbs.account.upper() == "@"+name.upper():
                        channel_by_stakeholders.append(cbs)
                
            if len(channel_by_stakeholders) > 0:
                log.info("Existe channel_by_stakeholders tw=>"+tweet['id_str'],True,True)
                if tweet['text'].find("RT") == -1:
                    clients = configuration['clients']
                    for channel_by_stakeholder in channel_by_stakeholders:
                        find_sh = list(filter(lambda x: x == channel_by_stakeholder.client_id, ObjectToJson(clients)))
                        if len(find_sh) > 0:
                            listport = GetPortByCliet_id(log,list_port,channel_by_stakeholder.client_id)
                            try:
                                log.info(data,True,True)
                                if configuration['memcached']:
                                    pi.clientAdd(listport[0].port)
                                    pi.add(data)
                                    log.top = " ,Client=>"+str(channel_by_stakeholder.client_id)+ ", PORT=>"+str(listport[0].port)
                                    log.setTime(t.end())
                                    log.warning("#"+str(conteo)+"=>id_tweet original=>: " +tweet['id_str'] + ", Hora_TW=>: "+ tweet['created_at'],True,True)
                                else:
                                    # status_mq = mq.add(data,listport[0].name)
                                    log.top = " ,Client=>"+str(channel_by_stakeholder.client_id)+ ", MQ=>"+str(listport[0].name)
                                    log.setTime(t.end())
                                    log.warning("#"+str(conteo)+"=>id_tweet original=>: " +tweet['id_str'] + ", Hora_TW=>: "+ tweet['created_at'],True,True)
                            except Exception as f:
                                log.error("Name Threading : "+threading.current_thread().getName()+' threadingClass => Exception => saveTwetterCache => '+"IError al guardar el Tweet => %s : %s " % (e, tweet['id_str']),True,True)
                        else:
                            log.info("threadingClass => saveTwetterCache no se tiene cliente en lista ",True,True)
                else:
                    log.info("id_tweet RT: " + tweet['id_str'],True,True)
            else:
                log.info("Stakeholder ==> El SH no se encuentra en la tabla channel_by_stakeholder => "+tweet['user']['screen_name']+",tw=>"+tweet['id_str'],True,True)
        else:
            if isDefine(tweet,'delete'):
                log.info("id_tweet DL: " + tweet['delete']['status']['id_str'],True,True)
    except Exception as e:
        log.error("saveTwetterCachet => %s : %s " % (e, tweet['id_str']),True,True)
    log.info("Name Threading : "+threading.current_thread().getName()+' threadingClass => End => saveTwetterCache ',True,True)

def funIni(log):
    log.info("Name Threading : "+threading.current_thread().getName()+ " Constructor threading",True,True)

def logDisplay(log,type,msn):
    log.info("Name Threading : "+threading.current_thread().getName()+" threadingClass => Start => logDisplay",True,True)
    if type == "warning":
        log.info(msn,True,True)
    if type == "info":
        log.info(msn,True,True)
    if type == "error":
        log.error(msn,True,True)
    log.info("Name Threading : "+threading.current_thread().getName()+" threadingClass => End   => logDisplay",True,True)

def timerLoop(log,timeloop : int):
    log.info("Name Threading : "+threading.current_thread().getName()+' threadingClass => Start => timerLoop X '+str(timeloop),True,True)
    time.sleep(timeloop)
    log.info("Name Threading : "+threading.current_thread().getName()+' threadingClass => End   => timerLoop X '+str(timeloop),True,True)

def saveStreamMain(log,client):
    log.top = " ,Client=>"+str(client)
    configuration = cargaConfig(log)
    log.warning("###############################################",True);
    log.warning("#########-INICIANDO PYTHON STREAM SAVE-########",True);
    log.warning("###############################################",True);
    log.warning("",True,True);
    log.warning("Log_File: "+str(configuration['log']),True);
    log.printer("Abriendo canal",True)
    list_ports = getListPortsByClientAll()
    listport = GetPortByCliet_id(log,list_ports,client)
    pi = pila(log);    
    pi.clientAdd(listport[0].port)
    try:
        status =  True
        conteo = 1
        log.printer("status=>"+str(status),True)
        while status:
            # time.sleep(configuration['sleep_error'])
            pilaResponce = pi.setIni()
            # if pilaResponce == -1:
            #     me = memcacheClass(log)
            #     me.coustomMemdcached(pi.port)
            pi.printGuia()
            while pi.cima < pi.cola:
                try:
                    log.info("PILA => get data Cima: "+str(pi.cima),True,True)
                    data =pi.get('stream'+str(pi.cima))
                    if data != None:
                        tweet = json.loads(data)
                        data = json.dumps(tweet)
                        if tweet['text'].find("RT") == -1:
                            log.info("saveStreamMain=>#"+str(conteo)+"=>id_tweet original=>: " +tweet['id_str'] + ", Hora_TW=>: "+ tweet['created_at'],True,True);
                            log.info("saveStreamMain=>"+data)
                            ChannelByStakeholder = SaveTweetByAccount(log,data,tweet,client)
                            if configuration['threading']:
                                p1 =  threadingClass(log)
                                # arg = (log,data,tweet,configuration['client_id'],pi,conteo,ChannelByStakeholder,)
                                # p1.selectFunction("saveTwetterBd",tweet['id_str'],arg)
                                # p1.start()
                            else:
                                characterizeTwetter(log,configuration,data,tweet,client,pi,ChannelByStakeholder)
                        else:
                            log.info("saveStreamMain=>#"+str(conteo)+"=>id_tweet RT: " + tweet['id_str'],True,True);
                    else:
                        log.error("saveStreamMain=>Cache no existe data cima:"+str(pi.cima),True,True);
                    
                    conteo += 1
                except Exception as e:
                    try:
                        if tweet['delete']:
                            log.info("saveStreamMain=>No de guardar el Tweet esta eliminado => " + tweet['delete']['status']['id_str'],True,True)
                    except Exception as f:
                        log.error("saveStreamMain=>IError al guardar el Tweet => %s : %s " % (e, tweet['id_str']),True,True)
                pi.cima = pi.cima +1 
            pi.set("cima",pi.cima)
        log.warning("###############################################",True);
        log.warning("#########-FINALIZAR PYTHON STREAM SAVE-########",True);
        log.warning("###############################################",True);   
        log.warning("                                               ",True);   
        time.sleep(configuration['sleep_error'])
        saveStreamMain(log,client); 
    except Exception as e:
        log.error("CACHESAVE=>FileController => %s  " % (e),True,True)