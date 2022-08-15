from Utilities.utils import cargaConfig
from Utilities.log import log_file
from Utilities.theread  import threadingClass
from Controller.FilesController import  getListPortsByClientAll
from subprocess import call

#Cargará las configuraciones que esten en alrchivo config.ini
log = log_file("C:\Log\Stream\StreamDirector.log")     
configuration = cargaConfig(log)
log.log_File=configuration['log']
clients_drive = getListPortsByClientAll()

#Ejecutara los arhivos runStreamRss.exe, runStreamTrend.exe con la lista de argumentos que esten en el archivo config.ini
def main():
    path = configuration['pathfile']
    comand = path+'\StreamConfig.exe'
    log.warning(comand,True,True)
    call(comand)
    comand = path+'\StreamFile.exe'
    log.warning(comand,True,True)
    call(comand)
    clients = configuration['clients_director']
    clints_data = []
    log.warning("trends "+str(configuration['trends_active']),True,True)
    if configuration['trends_active']:
        p1 = threadingClass(log)
        arg = (log,"run Trends",path,)
        p1.selectFunction("runStreamTrend","run Trends", arg)
        p1.start()
        # comand = path+'\StreamTrends.exe'
        log.warning(comand, True, True)
        # call(comand)
    log.warning("rss "+str(configuration['rss_active']),True,True)
    if configuration['rss_active']:
        List_Rss = configuration['List_Rss']
        for rss in List_Rss:
            p1 = threadingClass(log)
            time=rss['timerss']/60
            arg = (log, rss['url'],path,int(time),)
            p1.selectFunction("runStreamRss","run Rss", arg)
            p1.start()
            break
    log.warning("save "+str(configuration['streamsave_active']),True,True)
    if configuration['streamsave_active']:
        for client in clients:
            estado = True
            for client_drive in clients_drive:
                if client_drive.client_id == client:
                    if client_drive.active:
                        clints_data.append({'client':client,'number':client_drive.number})
                        estado = False
                        log.warning("add client "+str(client_drive.client_id),True,True)
                        break
            # if estado:
            #     if client_drive.active:
            #         clints_data.append({'client':client,'number':1})

                
        for client_run in clints_data:
            for i in range(client_run['number']):
                # if client_run != 13 and client_run != 125:
                    p1 =  threadingClass(log)
                    arg = (log,"client"+str(client_run['client']),client_run['client'],path,)
                    p1.selectFunction("runStreamSave","run client"+str(client_run['client']),arg)
                    p1.start() 

    
main()