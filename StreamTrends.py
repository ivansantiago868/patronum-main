from pickle import TRUE
from Utilities.log import log_file
from Utilities.utils import cargaConfig, cargaConfig_twitter_credentials
from time import sleep
import sched, time
import argparse
from datetime import datetime, date
from twarc import Twarc
import json
from Controller.manage_tweet import getSendMessage
from tqdm import tqdm
from inspect import currentframe, getframeinfo
import sys, os
frameinfo = getframeinfo(currentframe())
#! Libreria para usar barras de progreso -> from tqdm import tqdm


#Cargará las configuraciones que esten en alrchivo config.ini
log = log_file("C:\Log\Stream\StreamTrends.log")
configuration = cargaConfig(log)
log.log_File=configuration['log']


def main():
    try:
        timeTrendsList = []
        trendsList = []
        trendsIndex = []
        
        t = datetime.utcnow()
        if extractConfigTrends(configuration, trendsList):                          #! 1.- Se extraera todos los trends que esten en el archivo config.ini
            actualTimeMinut = int(datetime.today().strftime("%M"))

            if actualTimeMinut == 0:
                actualTimeMinut = 60  

            getTrendsTimes(trendsList, timeTrendsList, actualTimeMinut)             #! 2.- Obtiene todos los tiempos de la lista de trends y calcula el timepo que tiene para el sleep
            if len(timeTrendsList) > 0:                                
                schedule = sched.scheduler(time.time, time.sleep)                                      
                schedule.enter(sleepTime(min(timeTrendsList)), 1, loopTrends, (schedule, timeTrendsList, trendsList, trendsIndex)) #! 3.- Hara un sleep con el tiempo mas pequeño en la lista y ejecutara la funcion loopTrends
                schedule.run()
            else:
                now = datetime.now()
                log.warning("Conteo de tiempos en hoja de sheet no encontrado ... Date:"+str(now.date())+",Hora:"+str(now.time()),True,True)
    except Exception as e:
        log.error("Error en "+str(e),modul="main",display=True,dateStatus=True)
        main()
                
            
    
def loopTrends(schedule, timeTrendsList, trendsList, trendsIndex):
    
    try:
        now = datetime.now()
        log.warning("Ejecutando... Date:"+str(now.date())+",Hora:"+str(now.time()),True,True)

        actualTimeMinut = int(datetime.today().strftime("%M"))
        log.warning("validateTime... Date:"+str(now.date())+",Hora:"+str(now.time()),True,True)
        validateTime(trendsList, trendsIndex, actualTimeMinut)              #! 3.- Validara que trends debera ejecutarse dependiendo del tiempo actual o al mas cercano
        log.warning("trendsExtraccion... Date:"+str(now.date())+",Hora:"+str(now.time()),True,True)
        trendsExtraccion(trendsList, trendsIndex)                           #! 5.- Extra los trends
        log.warning("validationChanges... Date:"+str(now.date())+",Hora:"+str(now.time()),True,True)
        validationChanges(trendsList, trendsIndex)                          #! 6.- Validara los cambios que hayan pasado                         
        del timeTrendsList[:]
        del trendsIndex[:]
        
        now = datetime.now()

        log.warning("Termina... Date:"+str(now.date())+",Hora:"+str(now.time()),True,True)
        log.warning("~~~~~~~~~Termina Espera sleep: "+str(timeTrendsList)+", tiempo:"+datetime.today().strftime("%H:%M:%S")+"~~~~~~~",True,True)
        
        getTrendsTimes(trendsList, timeTrendsList, actualTimeMinut, False)  #! 7.- Obtiene todos los tiempos de la lista de trends y calcula el timepo que tiene para el sleep
        schedule.enter(sleepTime(min(timeTrendsList)), 1, loopTrends, (schedule, timeTrendsList, trendsList, trendsIndex)) #! 8.- Hara un sleep con el tiempo mas pequeño en la lista y ejecutara la funcion loopTrends
        schedule.run()

    except Exception as e:
        log.error("Error en "+str(e),modul="loopTrends",display=True,dateStatus=True,e=e)
        main()


#! Extrea la configuracion de los trends de cada pais que este en el archivi config.ini
def extractConfigTrends(configuration, listTrends):

    if len(configuration["List_Pais"]) > 0:

        for pais in configuration["List_Pais"]:
            pais.update(actualTrends = [])
            pais.update(pastTrends = [])
            pais.update(sendType = -1)
            listTrends.append(pais)
        return True

    else:
        log.warning("No hay paises en config.ini",True,True)
        return False



#! Obtiene todos los tiempos de la lista de trends y calcula el timepo que tiene para el sleep
def getTrendsTimes(listTrends, listTimeTrends, actualTimeMinut, run = True):

    if actualTimeMinut == 0 or actualTimeMinut == 60:
        actualTimeMinut = 1

    for time in listTrends:
        if time['status_full']:
            for i in range(actualTimeMinut, 61):
                if i % time["timedelaystatus"] == 0 and run:
                    if actualTimeMinut == 1:
                        listTimeTrends.append(1+(i - actualTimeMinut))
                        #run  = False
                        break
                    listTimeTrends.append(i - actualTimeMinut)
                    run = False
                    break
                run = True
        else:
            for i in range(actualTimeMinut, 61):
                if i % time["timetrends"] == 0:
                    listTimeTrends.append(i - actualTimeMinut)
                    break
    print(listTimeTrends)




#! Hace el sleep con el numeor mas pequeño que hay en la lista timeTrendslist
def sleepTime(timeToSleep):
    time = datetime.utcnow()
    now = datetime.now()
    timeToSleep = (timeToSleep*60) - (time.second + time.microsecond/1000000.0)
    log.warning(f"Espere {str(timeToSleep / 60)} minutos, Inicio: {str(now)}",True,True)
    return timeToSleep
    
    


#! Calcula el tiempo para hacer un sleep hasta el siguientr minuto (solo si es necesario)
def delay(pastTimeMinut):

    time = datetime.utcnow()
    actualTimeMinut = int(datetime.today().strftime("%M"))

    if  pastTimeMinut == actualTimeMinut:
        delayTime = 60 - (time.second + time.microsecond / 1000000.0)
        log.warning(f"~~~~~~~~~~~~~~~~~~ESPERE DELAY: {delayTime / 60} SEGUNDOS~~~~~~~~~~~~~~",True,True)
        # for _ in tqdm(list(range(int(delayTime)))):
        #     pass
        sleep(delayTime)
        log.warning(f"~~~~~~~~~~~~~~~~~~ACABO LA ESPERA DE DELAY~~~~~~~~~~~~~~",True,True)
    else:
        delayTime = (pastTimeMinut * 60) - (time.second + time.microsecond/1000000.0)
        log.warning(f"~~~~~~~~~~~~~~~~~~ESPERE DELAY: {delayTime / 60} SEGUNDOS~~~~~~~~~~~~~~",True,True)
        # for _ in tqdm(list(range(int(delayTime)))):
        #     pass
        sleep(delayTime)
        log.warning(f"~~~~~~~~~~~~~~~~~~ACABO LA ESPERA DE DELAY~~~~~~~~~~~~~~",True,True)


    #? Se puede implementar una barrra de progreso con el tiempo que debe esperar con la libreria de tqdm
    #     time = datetime.utcnow()
    #     actualTimeMinut = int(datetime.today().strftime("%M"))
    #     delayTime = 60 - (time.second + time.microsecond / 1000000.0)
    #     print(f"~~~~~~~~~~~~~~~~~~ESPERE DELAY: {delayTime} SEGUNDOS~~~~~~~~~~~~~~")
    #     for _ in tqdm(list(range(int(delayTime)))):
    #         sleep(1)  # doing some expensive work...
    #         elapsed_time = delayTime - int(actualTimeMinut)
    #         if elapsed_time > delayTime:
    #             raise TimeoutError("long_running_function took too long!")
    
    # tqdm.write("Done task")




#! Valida que el tiempo en la configuracion y en el actual sean iguales
def validateTime(trendsList, trendsIndex, actualTimeinut):
    now = datetime.now()
    try:
        index = 0
        time = False
        for trends in trendsList:
            if trends['sendtop'] and actualTimeinut % trends['timeminutoalert'] == 0:
                if trends['status_full']:
                    if actualTimeinut % trends['timedelaystatus'] == 0:
                        trends['sendType'] = 0
                        time = True

                elif actualTimeinut % trends['timetrends'] == 0:
                    trends['sendType'] = 0
                    time = True
            else:
                if trends['status_full'] and actualTimeinut % trends['timedelaystatus'] == 0 and actualTimeinut % trends['timetrends'] != 0:
                    trends['sendType'] = 1
                    time = True
                
                else:
                    if actualTimeinut % trends['timetrends'] == 0:
                        trends['sendType'] = 2 
                        time = True
                    else:
                        log.warning("~~~~~~~~~No es el momento de lanzar " + trends['name']+ " ~~~~~~~"+",Hora:"+str(now.time()),True,True)
            
            if time:
                log.warning("~~~~~~~~~Si es el momento de lanzar " + trends['name']+ " ~~~~~~~"+",Hora:"+str(now.time()),True,True)
                trendsIndex.append(index)
                time = False
            index += 1
    except Exception as e:
        log.error(f"error {e} {str(now.time())}",'validateTime',True,True)





#! Función para obtener los Trends de la lista de paises en trendsList
def trendsExtraccion(trendsList, indexNums):

    tweets_dict = {}
    Trending_Topics = []

    #Credenciales de Twitter
    configCredential = cargaConfig_twitter_credentials(log)
    print(configCredential)
    consumer_key = configCredential['CONSUMER_KEY'] #Config.twitter_credentials.CONSUMER_KEY
    consumer_secret = configCredential['CONSUMER_SECRET'] #Config.twitter_credentials.CONSUMER_SECRET
    access_token = configCredential['ACCESS_TOKEN'] #Config.twitter_credentials.ACCESS_TOKEN
    access_token_secret = configCredential['ACCESS_TOKEN_SECRET'] #Config.twitter_credentials.ACCESS_TOKEN_SECRET
    t = Twarc(consumer_key, consumer_secret, access_token, access_token_secret)

    # 1.- Recorre la lista de numeros que son los index de los trends que seran descargadas
    # 2.- Extrae el numero de trends que este en la configuracion de cada pais
    for nums in indexNums:
        for tweet in t.trends_place(str(trendsList[nums].get('id'))):
            tweet.update(Pais = trendsList[nums].get('name'))
            if trendsList[nums]["sendType"] >= 0:
                if trendsList[nums]["sendType"] == 0:
                    del trendsList[nums]["pastTrends"][:]
                    numsTrends = trendsList[nums]["trends_number_alert"]

                elif trendsList[nums]["sendType"] == 1 or trendsList[nums]['sendType'] == 2:
                    numsTrends = trendsList[nums]["trends_number"] 
                    if len(trendsList[nums]["actualTrends"]) > numsTrends:
                        del trendsList[nums]["actualTrends"][numsTrends: ]
                    trendsList[nums]["pastTrends"] = trendsList[nums]["actualTrends"].copy()

                del tweet["trends"][numsTrends:]
                del trendsList[nums]["actualTrends"][:]

                for trendsNames in tweet['trends']:
                    trendsList[nums]["actualTrends"].append(trendsNames['name'])



#! Valida los cambios y envia los trends a su respectivo canal de telegram
def validationChanges(listTrends, indexList):
    
    message = ''
    message_changes = False
    if configuration['custom_canaltelegram'] != '':
        msnPrueba = 'PRUEBA **'
    else:
        msnPrueba = ''
    for nums in indexList:
        if listTrends[nums]['sendType'] == 0 or listTrends[nums]['sendType'] == 2:
            if listTrends[nums]['sendType'] == 0:
                trendsNumber = str(listTrends[nums]['trends_number_alert'])
            else:
                trendsNumber = str(listTrends[nums]['trends_number'])
            message = msnPrueba+"Compartimos las "+ trendsNumber +" principales tendencias para " + listTrends[nums]['name'].strip().capitalize() + ":\n\n"
        else:
            message = msnPrueba+"Compartimos los cambios en tendencias para " + listTrends[nums]['name'].strip().capitalize() + ":\n\n"


        if not listTrends[nums]['pastTrends']:
            for trends in listTrends[nums]['actualTrends']:
                message += f"{trends} #{int(listTrends[nums]['actualTrends'].index(trends)) + 1}\n"
    
        else:
            for presentTrends in listTrends[nums]['actualTrends']:

                if presentTrends in listTrends[nums]['pastTrends']:

                    if listTrends[nums]['sendType'] == 2:

                        if listTrends[nums]['pastTrends'].index(presentTrends) == listTrends[nums]['actualTrends'].index(presentTrends):
                            message += f"{presentTrends} \U000027A1 (se mantiene) #{int(listTrends[nums]['actualTrends'].index(presentTrends)) + 1}\n"
                            
                        elif listTrends[nums]['pastTrends'].index(presentTrends) > listTrends[nums]['actualTrends'].index(presentTrends):
                            message += f"{presentTrends} \U0001F53D (baja) #{int(listTrends[nums]['actualTrends'].index(presentTrends)) + 1}\n"

                        elif listTrends[nums]['pastTrends'].index(presentTrends) < listTrends[nums]['actualTrends'].index(presentTrends):
                            message += f"{presentTrends} \U0001F53C (sube) #{int(listTrends[nums]['actualTrends'].index(presentTrends)) + 1}\n"
                else:
                    message += f"{presentTrends} \U0001F4A5 (nuevo en el Top {listTrends[nums]['trends_number']} ) #{int(listTrends[nums]['actualTrends'].index(presentTrends)) + 1}\n"
                    if not message_changes:
                        for pastTrends in listTrends[nums]['pastTrends']:
                            if pastTrends not in listTrends[nums]['actualTrends']:
                                message += f"{pastTrends} \U0001F4C9 (sale del Top {listTrends[nums]['trends_number']})\n"
                                message_changes = True




        if listTrends[nums]['sendType'] == 0 or listTrends[nums]['sendType'] == 2:
            if configuration['custom_canaltelegram'] == '':
                sendTelegram(listTrends[nums]['channel'].strip(), message)
                if configuration['copy_canaltelegram']:
                    sendTelegram(configuration['custom_canaltelegram'].strip(), message)
            else:
                sendTelegram(configuration['custom_canaltelegram'].strip(), message)
        else:
            if message !=  msnPrueba+"Compartimos los cambios en tendencias para " + listTrends[nums]['name'].strip().capitalize() + ":\n\n":
                if configuration['custom_canaltelegram'] == '':
                    sendTelegram(listTrends[nums]['channel'].strip(), message)
                    if configuration['copy_canaltelegram']:
                        sendTelegram(configuration['custom_canaltelegram'].strip(), message)
                else:
                    sendTelegram(configuration['custom_canaltelegram'].strip(), message)
        
        print(message)

            



#! Manda al canal de telegram las alertas
def sendTelegram(canalTelegram,mensaje):
    bot_id =  configuration['bot_id']
    body = {
        "fromPhone":bot_id,
        "text":mensaje,
        "toPhone":canalTelegram,
        "channel":"telegram",
        "messageBodyType":"chat"
    }
    getSendMessage(log,body,configuration)




#! Escribe en los archivos Json los Trends de cada país
def Trendings_Json(trendsList, trendsIndex):


    now = datetime.now()
    current_time = "Curren Time " + now.strftime("%H:%M:%S")

    for nums in trendsIndex:
        with open("FileProcess/Trends/Treds"+trendsList[nums]['name'].strip().capitalize()+".json", 'a', encoding='utf-8') as f:
            json.dump(current_time, f, ensure_ascii=False, indent=4)
            json.dump(trendsList[nums]['trends']['name'], f,
                    ensure_ascii=False, indent=4)


main()
