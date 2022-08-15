import json

from psycopg2 import connect
from Utilities.http_service import sendSH, POSTAT #,  POST,  ,saveSHaccount,sendSHaccount 
from Utilities.utils import BuscarDatoEnListaObjt, cargaConfig ,cargaConfigApi,  ObjectToJson, cifradoCesar, desCifradoCesar, encontrarFormatoFecha, epochToDateStr, get_random_string,strToDatetime, epochToDate,dateToStringLocal,datetimeToStr, strToEpoch,minimiUrl#, UnionListWithoutRepetition, getSamesItem, removeItemSameFromList, , 
from Controller.SuntzuController import SuntzuBd
from Controller.FilesController import getListChannelByStakeholderForName, getNickanmeObjectByClientId,getNickanmeObjectByClientIdAndInternal,getListWordsInterestMonibot, getWordsFromTextMonibot, GetPortByCliet_id, getListWordExceptionsMonibot , getListWordsInterestCompuestoMonibot , getWordsFromTextMonibotInteresCompuesto
from Entity.Publics import search_result,PublicationMonibot, MonibotTelegram, MessageBuild#, , channel_by_stakeholder, 
from Controller.ShController import trainEntNicknamesSHByClientId, trainEntNicknamesPrinSHByClientId
from Controller.DriveControler import getListPortsByClientId
from typing import List
# from Utilities.log import log_file
from Utilities.mq import mqClass
import re
from Utilities.timeScan import timeClass
from collections import defaultdict
import itertools
from datetime import datetime
from Controller.Tr_BD import Tr_BD
from datetime import datetime , timezone
from datetime import timedelta
from dateutil.parser import parse




#Funcion para obtener los Sh de la base de datos Suntzu
def getStakeholders (clients,log):
    log.info("abriendo config.ini",True,True)
    configuration = cargaConfig(log)
    url_base = configuration['url_base']
    accountIDS = ""
    response_getSH = sendSH(log,url_base + 'Grial/GetStakeholdersPerClient', clients)
    if response_getSH.status_code == 200:
        #logging.info("Respuesta del servicio de guardado: ==>" + response_getSH.status_code)
        sh = response_getSH.json()
        accountIDS = ""
        for item in sh['stakeholders']:
            if accountIDS == "":
                accountIDS = item['account_id']
            else:
                accountIDS = accountIDS +", " + item['account_id']
    else:
        log.error("Error con el servicio para obtener stakeholders")

    return accountIDS
def EnvioManual(log,configuration,body,mq1,clients  , reporte=[] , hour_utc_subtract = 0):
    try:
        data = body
        post_data =  data['data']
        if data['type'] == 'twitter':
            name = post_data['user']['screen_name']
            id_data =  post_data['id_str']
            hora_data = post_data['created_at']
        client_id = []
        exists = False
        for i in clients:
            if i['client_id'] == int(reporte[0]):
                exists = True
                client_id.append(i)
                break
        if exists:
            URL = reporte[2]
            urlShort = ''
            if configuration['url_minimi']:
                urlShort = "URL:  " + minimiUrl(URL,configuration)
            else:
                urlShort = "URL:  " + URL
            if data["type"] == "twitter":
                date = epochToDateStr(encontrarFormatoFecha(post_data['created_at'],'epoch'),'%a %b %d %H:%M:%S %Y')
                date = parse(post_data['created_at'])
                # date = date.replace(tzinfo=timezone.utc)
                #air_time = date.replace(tzinfo=timezone.utc)
                # current_time = datetime.now()
                # current_time = current_time.astimezone()

                now = date + timedelta(hours=hour_utc_subtract)
                date = now.strftime('%a %b %d %H:%M:%S %Y')

                # air_time = air_time.strftime('%a %b %d %H:%M:%S %Y')
                data["data"]["published"]= date
            else:
                date = datetime.today()
                # date = datetime.today().strftime('%a %b %d %H:%M:%S %Y')
                now = date + timedelta(hours=-5)
                # date = datetime.today().strftime('%a %b %d %H:%M:%S %Y')
                date = now.strftime('%a %b %d %H:%M:%S %Y')
                data["data"]["published"]= date


            #Tenemos que cambiar esto channel_id
            
            bot_id =  configuration['bot_id']
            Fuente = "Fuente.: "+reporte[1]
            autor = "Autor: " +reporte[3]
            Fecha = "Fecha: "+ date
            mensaje = "Mensaje: "+reporte[5]
            #channel_by_stakeholder.client_id
            #mq2.declare(configuration['bk_telegram'])
            #mq1.add(json.dumps(send_Data),listport[0].name)

            #client_id[0]['channel']
            #configuration['custom_canaltelegram']
            toPhone = client_id[0]['channel']
            #toPhone =configuration['custom_canaltelegram']
            toPhone ='-1001429915200'

            body = {
                "fromPhone":bot_id,
                "text":"{} \n{} \n{} \n{} \n{}  ".format(Fuente,autor,urlShort, Fecha,mensaje),
                "toPhone":toPhone,
                "channel":"telegram",
                "messageBodyType":"chat" 
            }
            log.info("Se genera el body" ,True,  True)
            log.info(("Enviando mensaje") ,True,  True)
            respuesta = getSendMessage(log,body,configuration)
            log.info((respuesta) ,True,  True)
            log.info(("Mensaje enviado") ,True,  True)
            ##client_id[0]['channel']
            #configuration['bk_telegram']
            #client_id[0]['cola_name']
            #cola_name_mq = configuration['bk_telegram']
            cola_name_mq = client_id[0]['cola_name']
            log.info(("Enviando al mq %s " % (cola_name_mq)) ,True,  True)
            if not mq1.add(json.dumps(body), cola_name_mq):
                log.info(("Reconectando al mq") ,True,  True)
                #Mandamos a la cola 
                mq1.reconect(log)
                mq1.add(json.dumps(body), cola_name_mq)

            dicc_2 = {"client_id": reporte[0] , "modulo":"StreamApi" , "bk_full" : client_id[0]['bk_full'] , "bk_send" : client_id[0]['bk_send'] , "valida_sh":False}
            data.update(dicc_2)
            log.info(("Enviando a la db catrina") ,True,  True)
            bd = Tr_BD(log , "catrina")
            bd.setTweetandRss(data , configuration)
            return {"Mensaje":"Se envio el mensaje correctamente" , "status":200}
        else:
            return {"Mensaje":"El cliente no existe en el sheet" , "status":400}
    except Exception as e :
        log.error(" %s %s " % (data['type'],str(e)),True,True)
        return {"Mensaje":str(e), "status":400}

def routerTwette(log,configuration,body,channel,ports,mq1,clients , validacion = True , reporte=[]):
    existe = False
    if validacion:
        data = json.loads(body)
    else:
        data = body    
    sh_total = False
    try:
        t =  timeClass(log ,"callback")
        post_data =  data['data']
        if data['type'] == 'twitter':
            name = post_data['user']['screen_name']
            id_data =  post_data['id_str']
            hora_data = post_data['created_at']
        if data['type'] == 'rss':
            name = post_data['account']
            id_data =  post_data['account']+" "+post_data['url']
            hora_data = post_data['published']
        if data['type'] == 'facebook':
            name = post_data['account']
            id_data =  post_data['id_str']
            hora_data = post_data['Created time']
        channel_by_stakeholders = []
        for cbs in channel:
            if cbs.account.upper() == name.upper() or cbs.account.upper() == "@"+name.upper():
                if cbs.tipo.upper() == 'Total'.upper():
                    channel_by_stakeholders_tempo = []
                    channel_by_stakeholders_tempo.append(cbs)
                    channel_by_stakeholders = channel_by_stakeholders_tempo + channel_by_stakeholders
                else:
                    channel_by_stakeholders.append(cbs)
        if len(channel_by_stakeholders) > 0:
            if data['type'] == 'twitter':
                send_msn = post_data['id_str']
            else:
                send_msn = name
            log.info("Existe channel_by_stakeholders "+data['type']+"=>"+send_msn,True,True)
            client_id = []
            sh_send_by_client = []
            for cbl in channel_by_stakeholders:
                if cbl.client_id in client_id:
                    indx = True
                else:
                    client_id.append(cbl.client_id)
                    sh_send_by_client.append(cbl)
            for channel_by_stakeholder in sh_send_by_client:
                client_exist = []
                for cbs in clients:
                    if channel_by_stakeholder.client_id == cbs:
                        client_exist.append(cbs)
                if len(client_exist) > 0:
                    listport = GetPortByCliet_id(log,ports,channel_by_stakeholder.client_id)
                    if channel_by_stakeholder.tipo.upper() == 'Total'.upper():
                        sh_total = True
                    if len(listport) > 0:
                        if data['type'] == 'facebook':
                            send_Data = {"type":data['type'],"data":post_data,'sh_total':sh_total,"account": name}
                        else:
                            send_Data = {"type":data['type'],"data":post_data,'sh_total':sh_total}
                        try:
                            #True
                            if validacion:
                                if configuration['memcached']:
                                    # pi.clientAdd(listport[0].port)
                                    # pi.add(body) 
                                    log.warning("memcached no activo callback=>router"+data['type']+" original=>: " +id_data + ", Hora_"+data['type']+"=>: "+ hora_data,True,True,t.end())
                                else: 
                                    if not mq1.add(json.dumps(send_Data),listport[0].name):
                                        mq1.reconect(log)
                                        mq1.add(json.dumps(send_Data),listport[0].name)
                                    log.top = " ,Client=>"+str(channel_by_stakeholder.client_id)+ ", PORT=>"+str(listport[0].port)
                                    log.warning("callback=>router"+data['type']+" original=>: " +id_data + ", Hora_"+data['type']+"=>: "+ hora_data,True,True,t.end())
                            #False 
                            else:
                                if int(reporte[0]) == channel_by_stakeholder.client_id:
                                    existe= True
                                    try:
                                        if not mq1.add(json.dumps(send_Data),configuration['bk_telegram']):
                                            #Mandamos a la cola 
                                            mq1.reconect(log)
                                            mq1.add(json.dumps(send_Data), configuration['bk_telegram'])
                                        #Tenemos que cambiar esto channel_id
                                        bot_id =  configuration['bot_id']
                                        Fuente = "Fuente: "+reporte[1]
                                        autor = "Autor: "+channel_by_stakeholder.account
                                        URL = reporte[2]
                                        urlShort = ''
                                        if configuration['url_minimi']:
                                            urlShort = "URL:  " + minimiUrl(URL,configuration)
                                        else:
                                            urlShort = "URL:  " + URL
                                        date = epochToDateStr(encontrarFormatoFecha(send_Data['data']['created_at'],'epoch'),'%a %b %d %H:%M:%S %Y')
                                        #date = datetime.strptime(send_Data['data']['created_at'], '%a %b %d %H:%M:%S %z %Y')
                                        #date = "{}-{}-{}  {}:{}:{}".format(date.day , date.month ,date.year , date.hour , date.minute , date.second )
                                        Fecha = "Fecha: "+date
                                        mensaje = "Mensaje: "+reporte[5]
                                        #channel_by_stakeholder.client_id
                                        body = {
                                            "fromPhone":bot_id,
                                            "text":"{} \n{} \n{} \n{} \n{}  ".format(Fuente,autor,urlShort, Fecha,mensaje),
                                            "toPhone":configuration['custom_canaltelegram'],
                                            "channel":"telegram",
                                            "messageBodyType":"chat"
                                        }
                                        getSendMessage(log,body,configuration)
                                        dicc_2 = {"client_id": channel_by_stakeholder.client_id , "modulo":"StreamApi" , "bk_full" : listport[0].bk_full , "bk_send" : listport[0].bk_send , "valida_sh":False}
                                        send_Data.update(dicc_2)
                                        #mq2.declare(configuration['bk_telegram'])
                                        #mq1.add(json.dumps(send_Data),listport[0].name)
                                        bd = Tr_BD(log , "catrina")
                                        bd.setTweetandRss(send_Data , configuration)
                                        log.top = " ,Client=>"+str(channel_by_stakeholder.client_id)+ ", PORT=>"+str(listport[0].port)
                                        log.warning("callback=>router"+data['type']+" original=>: " +id_data + ", Hora_"+data['type']+"=>: "+ hora_data,True,True,t.end())
                                        return True
                                    except Exception as e :
                                        print(str(e))
                                        log.error("callback => Exception => save"+data['type']+"Cache => IError al guardar el %s => %s : %s " % (data['type'],e, id_data),True,True)
                                        return False
                                    # Se envia el cliente por el telegram directamente
                        except Exception as f:
                            log.error("callback => Exception => save"+data['type']+"Cache => IError al guardar el %s => %s : %s " % (data['type'],f, id_data),True,True)
        else:
            log.top = ""
            log.info("No Existe channel_by_stakeholders "+data['type']+"=>"+id_data+" cuenta "+name,True,True)
        if validacion == False:
            if existe == False:
                return False
        return True
    except Exception as et:
        log.error("callback => Exception => router"+data['type']+" => IError al guardar el %s => %s : %s " % (data['type'],et, "General"),True,True)
        return False

   
    

## Convert rss to twitter format 
def rssToTwitter(rss):
    tweet = {}
    tweet['id_str'] = cifradoCesar(rss['url'],7)
    # rep  = desCifradoCesar(tweet['id_str'],7)
    try:
        tweet['created_at'] = epochToDateStr(strToEpoch(rss['published'], '%a, %d %b %Y %H:%M:%S %z'),'%a %b %d %H:%M:%S +0000 %Y')
    except Exception as e:
        try:
            tweet['created_at'] = epochToDateStr(strToEpoch(rss['published'], '%Y-%m-%dT%H:%M:%SZ'),'%a %b %d %H:%M:%S +0000 %Y')
        except Exception as ef:
            tweet['created_at'] = ''
    return tweet
##caracterisar Tweet
def characterizeTwetter(log,configuration,tweet,pi,target_list,type):
    t =  timeClass(log ,"characterizeTwetter")

    try:
        if configuration['listIdTw'].find(tweet['id_str']) < 0 :
            publications = GetShFromMessage(log,tweet,int(target_list.client_id),configuration,type)
            for publication in publications:
                #publication.send_notification =  True
                publication.package_name = 'com.twitter.android'
                if target_list.tipo.upper() == 'TOTAL'.upper():
                    publication.send_notification = True
                if publication.send_notification and  publication.process_attitude == 'V2':

                    if configuration['send_telegram']:
                        # SaveTwitter(tweet)
                        rest,errorSend = SendTelegram(log,tweet,publication,type)
                    if(rest and errorSend):
                        if configuration['memcached']:
                            pi.delete('stream'+str(pi.cima))
                    log.warning("characterizeTwetter=>id_tweet : " + tweet['id_str']+" Send, errorSend: "+str(errorSend) ,True,True,t.end());
                    return rest,errorSend
                else:
                    log.warning("characterizeTwetter=>id_tweet : " + tweet['id_str']+" TW send_notification False ",True,True,t.end());
            return False,True
        else:
            return False,True
    except Exception as e:
        log.error("characterizeTwetter => Exception => IError al guardar el Tweet => %s : %s " % (e, tweet['id_str']),True,True)
        return False,False
#Guardar tweet
def SaveTweetByAccount(log,item,tweet,client_id,channel_by_stakeholders,configuration):
    t = timeClass(log,"SaveTweetByAccount")
    try:
        log.info("SaveTweetByAccount => Envíando tweet al BD: " + str(tweet))
        suntzubd = SuntzuBd(log)
        if suntzubd.status:
        # if True:
            if tweet['user'] != None:
                if len(channel_by_stakeholders) > 0:
                    for stakeholders in channel_by_stakeholders:
                        sr = search_result()
                        sr.JsonToTwetter(tweet,stakeholders,configuration['UTC_DB'])
                        suntzubd.setSaveTwitter(sr)
                        log.info("SaveTweetByAccount => Stakeholder "+tweet['user']['screen_name']+"==> CLient "+str(stakeholders.client_id))
                    dataBusqueda = {"data" :channel_by_stakeholders, "status":True}
                else:
                    log.info("SaveTweetByAccount => Stakeholder ==> El SH no se encuentra en la tabla channel_by_stakeholder => "+tweet['user']['screen_name'],True,True)
                    suntzubd.end() 
                    dataBusqueda = {"data" :None, "status":False}
            else:
                log.info("SaveTweetByAccount => Stakeholder ==> TW no tiene USER => ",True,True)
                suntzubd.end() 
                dataBusqueda = {"data" :None, "status":False}
        else:
            dataBusqueda = {"data" :None, "status":False}
        log.setTime(t.end())
        log.info("SaveTweetByAccount => SAVE => ",True,True)
        return dataBusqueda
    except Exception as e:
        log.error("CACHESAVE=>SaveTweetByAccount => %s  " % (e),True,True)
        dataBusqueda = {"data" :None, "status":False}
        return dataBusqueda

def GetShFromMessage(log,data,client_id,configuration,type):
    log.info("Ingreso a Caracterizacion de tw",True,True)
    #tweet = json.loads(data)
 
    publication =  PublicationMonibot()
    publication.process_attitude = 'V2'
    publication.setTwitter(data,client_id,type)
    publication.sts_text_format = publication.sts_text
    return processAttitude(log, publication,configuration)

   

def processAttitude(log ,request : PublicationMonibot,configuration):
    file_name = "NlpController.py"
    try:
        return mainEvaluation(log,request,request.client_id, request.search_id[0],configuration)
    except Exception as e:
        log.error("Caracterizacion => processAttitude=>"+str(e))
        return False

def mainEvaluation(log,process : PublicationMonibot,client_id:int, search_id:str,configuration):
    try:
            t = timeClass(log,"mainEvaluation")
            process_list = []
            # textoTotal = tweet['user']['screen_name'] +" "+tweet['user']['name'] +" "+ tweet['text']
            process.prayers = {"prayer":"","staff":"","staff_prin":""}
            
            f = timeClass(log,"mainEvaluation GetPrayers")
            log.info("Ingreso a Caracterizacion de tw=> GetPrayers",True,True)
            process = GetPrayers(log,process,client_id,configuration)
            log.info("Salida a Caracterizacion de tw=> GetPrayers",True,True)
            # log.warning("mainEvaluation GetPrayers => cliente_is=>"+str(client_id)+",tw_id "+process.provider_item_id[0],True,True,f.end())

            f = timeClass(log,"mainEvaluation GetPrayers")
            log.info("Ingreso a Caracterizacion de tw=> GetMainEvaluationPublication",True,True)
            process = GetMainEvaluationPublication(log,process,client_id,search_id,configuration)
            log.info("Salida a Caracterizacion de tw=> GetMainEvaluationPublication",True,True)
            # log.warning("mainEvaluation GetMainEvaluationPublication => cliente_is=>"+str(client_id)+",tw_id "+process.provider_item_id[0],True,True,f.end())

            f = timeClass(log,"mainEvaluation GetPrayers")
            log.info("Ingreso a Caracterizacion de tw=> GetMainEvaluationClient",True,True)
            process = GetMainEvaluationClient(log,process,client_id,search_id,configuration)
            log.info("Salida a Caracterizacion de tw=> GetMainEvaluationClient",True,True)
            # log.warning("mainEvaluation GetMainEvaluationClient => cliente_is=>"+str(client_id)+",tw_id "+process.provider_item_id[0],True,True,f.end())

            f = timeClass(log,"mainEvaluation GetPrayers")
            log.info("Ingreso a Caracterizacion de tw=> GetMainEvaluationPrayers",True,True)
            process = GetMainEvaluationPrayers(log,process,client_id,search_id,configuration)
            log.info("Salida a Caracterizacion de tw=> GetMainEvaluationPrayers",True,True)
            # log.warning("mainEvaluation GetMainEvaluationPrayers => cliente_is=>"+str(client_id)+",tw_id "+process.provider_item_id[0],True,True,f.end())
            
            f = timeClass(log, "mainEvaluation GetPrayes")
            log.info("Ingreso a Caracterizacion de tw=> GetMainEvaluationExceptions", True, True)
            process = GetMainEvaluationExceptions(log, process, client_id, search_id, configuration)
            log.info("Salida a Caracterizacion de tw=> GetMainEvaluationExceptions")

            process_list.append(process)
            # log.warning("mainEvaluation cliente_is=>"+str(client_id)+", tw_id "+process.provider_item_id[0],True,True,t.end())
            return process_list
    except Exception as e:
        log.error("CACHESAVE=>IError mainEvaluation => %s " % (e),True,True)
    
def GetPrayers(log , publications : PublicationMonibot, client_id : int,configuration):
    try:
        nicknameList = getNickanmeObjectByClientId(client_id,configuration['sheet_active'])
        patterns = trainEntNicknamesSHByClientId(nicknameList)
        textoTotal = textoValidate(publications)
        sh =[]
        for nickname in nicknameList:
            nickSplitList = nickname.alias.split(',')
            for nickSplit in nickSplitList:
                if textoTotal.find(nickSplit.rstrip().lstrip()) > 0 and nickSplit.rstrip().lstrip() != ''  and nickSplit.rstrip().lstrip() != '.' and nickSplit.rstrip().lstrip() != 'P':
                    # sh +=  " " + nickSplit.rstrip().lstrip() + ","
                    sh.append(nickSplit.rstrip().lstrip())
                    publications.send_notification = True
        if publications.send_notification:
            publications.prayers = {"prayer":sh,"staff":"","staff_prin":""}
        return publications
    except Exception as e:
        log.error("CACHESAVE=>IError mainEvaluation => %s " % (e),True,True)
        return False
def GetMainEvaluationClient(log, publications : PublicationMonibot,client_id:int,serach_id:str,configuration):
    try:
        nicknameList = getNickanmeObjectByClientId(client_id)
        nicknameInternals = getNickanmeObjectByClientIdAndInternal(client_id,True)
        patterns = trainEntNicknamesPrinSHByClientId(nicknameInternals)
        textoTotal = textoValidate(publications)
        sh =[]
        for nickname in patterns:
            screen_name= "@"+publications.screen_name[0]
            if screen_name.find(nickname['label']) >= 0 and nickname['label'] != '':
                sh.append(nickname['label'])
                publications.send_notification = True
        if publications.send_notification:
            publications.prayers['staff_prin'] = sh
        return publications
    except Exception as e:
        log.error("CACHESAVE=>IError mainEvaluation => %s " % (e),True,True)
        return False
def GetMainEvaluationPublication(log, publications : PublicationMonibot,client_id:int,serach_id:str,configuration):
    try:
        nicknameList = getNickanmeObjectByClientId(client_id)
        nicknameInternals = getNickanmeObjectByClientIdAndInternal(client_id,True)
        patterns = trainEntNicknamesSHByClientId(nicknameInternals)
        textoTotal = textoValidate(publications)
        sh =[]
        for nickname in patterns:

            if textoTotal.find(nickname['pattern']) >= 0 and nickname['pattern'] != '':
                sh.append(nickname['pattern'])
                publications.send_notification = True
        if publications.send_notification:
            publications.prayers['staff'] = sh
        return publications
    except Exception as e:
        log.error("CACHESAVE=>IError mainEvaluation => %s " % (e),True,True)
        return False
def GetMainEvaluationPrayers(log, publications : PublicationMonibot,client_id:int,serach_id:str,configuration):
    try:
        publications.send_notification = False
        publications.rule = ""
        #types_words = getListWordsInterestMonibot(client_id,publications.search_id[0])
        types_words = getListWordsInterestCompuestoMonibot(client_id,publications.search_id[0])
        tags_interest = {'negative': '', 'positive': '', 'informative': ''}
        try:
            # print(client_id)
            words_type_attitude = getWordsFromTextMonibotInteresCompuesto(publications.sts_text, types_words.negative)

            # words_type_attitude = getWordsFromTextMonibot(publications.sts_text, types_words.negative)
            if words_type_attitude[0] != [] and words_type_attitude[1] !=[]:
                # print("negative")
                tags_interest['negative'] += ", "+str(words_type_attitude[0])
                publications.send_notification = True
            else:
                words_type_attitude = getWordsFromTextMonibotInteresCompuesto(publications.sts_text, types_words.positive)
                # words_type_attitude = getWordsFromTextMonibot(publications.sts_text, types_words.positive)
                if words_type_attitude[0] != [] and words_type_attitude[1] !=[]:
                    # print("positivos")
                    tags_interest['positive'] += ", "+str(words_type_attitude[0])
                    publications.send_notification = True
                else:

                    words_type_attitude_complete = getWordsFromTextMonibotInteresCompuesto(publications.sts_text, types_words.informative)
                    # words_type_attitude = [(list(filter(None, re.split("[===]+", w)))[0]) for w in words_type_attitude_complete]
                    if words_type_attitude_complete[0] != [] and words_type_attitude_complete[1] !=[]:
                        if(words_type_attitude_complete[1][0] == False):
                            # print("informativo")
                            tags_interest['informative'] += ", "+str(words_type_attitude_complete[0][0])
                            publications.send_notification = True
                        else:
                            # print("informativo")
                            tags_interest['informative'] += ", "+str(words_type_attitude_complete[0][0] +"  y  "+ words_type_attitude_complete[1][0])
                            publications.send_notification = True
                    else:
                        print("Ninguno")
        except Exception as e:
            log.error("CACHESAVE=>IError GetMainEvaluationPrayers ,WordsFromTextMonibot=> %s " % (e),True,True)   
        rule = {"user":[],"staff":[],"client":[],"interes":[]}
        try:       
            user = []
            if publications.prayers != None:
                for player in publications.prayers['prayer']:
                    if player.find("@") >= 0:
                        if publications.sts_text.find(player.rstrip().lstrip()+" ") >= 0:
                            user.append(player.rstrip().lstrip())
                            # publications.send_notification = True
                    else:
                        if player.find("#") >= 0:
                            if publications.sts_text.find(player.rstrip().lstrip()+" ") >= 0:
                                user.append(player.rstrip().lstrip())
                                # publications.send_notification = True
                        else:
                            if publications.sts_text.find(" "+player.rstrip().lstrip()+" ") >= 0:
                                user.append(player.rstrip().lstrip())
                                # publications.send_notification = True
            rule["user"] = user
        except Exception as e:
            log.error("CACHESAVE=>IError GetMainEvaluationPrayers , prayer => %s " % (e),True,True)  
        try:  
            staff = []
            if publications.prayers != None:
                for player in publications.prayers['staff']:
                    if player.find("@") >= 0:
                        if publications.sts_text.find(player.rstrip().lstrip()) >= 0:
                            staff.append(player.rstrip().lstrip())
                            publications.send_notification = True
                    else:
                        if player.find("#") >= 0:
                            if publications.sts_text.find(player.rstrip().lstrip()) >= 0:
                                staff.append(player.rstrip().lstrip())
                                publications.send_notification = True
                        else:
                            if publications.sts_text.find(player.rstrip().lstrip()) >= 0:
                                staff.append(player.rstrip().lstrip())
                                publications.send_notification = True
            rule["staff"] = staff
        except Exception as e:
            log.error("CACHESAVE=>IError GetMainEvaluationPrayers , staff=> %s " % (e),True,True)  
        try:  
            staff = []
            if publications.prayers != None:
                for player in publications.prayers['staff_prin']:
                    staff.append(player.rstrip().lstrip())
                    publications.send_notification = True
            rule["prin"] = staff
        except Exception as e:
            log.error("CACHESAVE=>IError GetMainEvaluationPrayers , staff_prin=> %s " % (e),True,True)  
        try:  
            interes = []
            if tags_interest["negative"] != '':
                interes.append(tags_interest["negative"])
                publications.send_notification = True
            elif tags_interest['positive'] != '':
                interes.append(tags_interest['positive'])
                publications.send_notification = True
            elif tags_interest['informative'] != '':
                interes.append(tags_interest['informative'])
                publications.send_notification = True
        
            else:
                print("sin tags_interest")
            rule["interes"] = interes
        except Exception as e:
            log.error("CACHESAVE=>IError GetMainEvaluationPrayers , tags_interest => %s " % (e),True,True)  
        publications.rule = rule
        return publications
    except Exception as e:
        log.error("CACHESAVE=>IError GetMainEvaluationPrayers => %s " % (e),True,True)
        publications.send_notification = False
        return publications

def GetMainEvaluationExceptions(log, publications : PublicationMonibot,client_id:int,serach_id:str,configuration):
    try:
        exceptions = []
        exceptions = getListWordExceptionsMonibot(client_id,publications.search_id[0])
        tags_interest = {'Exception': ''}
        words_type_attitude = getWordsFromTextMonibot(publications.sts_text,  exceptions)
        if len(words_type_attitude) > 0:
            tags_interest['Exception'] += ", "+str(words_type_attitude[0])
            publications.send_notification = False
            return publications
        else:
            return publications    
    except Exception as e:
        log.error("CACHESAVE=>IError GetMainEvaluationPrayers ,WordsFromTextMonibot=> %s " % (e),True,True)   
        publications.send_notification = False
        return publications      


def textoValidate(publications : PublicationMonibot):
    textoTotal = publications.sts_text #str(publications.screen_name) +" "+publications.name +" "+ 
    return textoTotal
def msmFacebook(log,data, publication):
    pass

def SendTelegramFacebook(log,data,posts,publication : PublicationMonibot ,type):
    try:
        configuration = cargaConfig(log)
        if type == 'facebook':
            if ( filtrarPaquete(publication.package_name) and publication.sts_text != "" and publication.sts_text != None):
                #validar duplcidos Utilidades.convertToSha1
                clientId = publication.client_id
                if(publication.process_attitude == 'V2'):
                    attitude = publication.attitude
                    if configuration['sheet_active']:
                        canalesTelegram = getListPortsByClientId(log,configuration,int(publication.client_id))
                    else:
                        canalesTelegram = buscarTelegramCanal(log,int(publication.client_id))
                    if len(canalesTelegram) >0 :
                        configuration = cargaConfig(log)
                        if configuration['sheet_active']:
                            canalTelegram = canalesTelegram[0].channel
                        else:
                            canalTelegram = canalesTelegram[0].id_channel
                        if configuration['custom_canaltelegram'] != '':
                            # canalTelegram = '-1001429915200'
                            canalTelegram = configuration['custom_canaltelegram']
                        #messageF = 'Fuente: Facebook \n Autor: '+ str(data['account']) + ' \n ' 
                        num = 1
                        bot_id =  configuration['bot_id']

                        for post in posts:
                            messageF = 'Fuente: Facebook \n Autor: '+ str(data['account']) +('\n' 
                            + 'Link: ' +str(post['permalink_url'])+ '\n'
                            + 'Fecha: '+str(post['Created time'])+'\n'
                            + 'Tipo Contenido: ' + str(post['Content type']) + '\n'
                            + 'Mensaje: ' + str(post['Message']) + '\n'+'\n'
                            + 'Reacciones: ' + str(post['Reactions']) + ' Comentarios: ' + str(post['Comments']) + ' Likes: ' + str(post['Likes']) + ' Post Shares: ' + str(post['Post shares']) + '\n'
                            + 'Love: ' + str(post['Reactions: Love'])  + ' Haha: ' + str(post['Reactions: Haha']) + ' Wow: ' + str(post['Reactions: Wow']) + ' Sad: ' + str(post['Reactions: Sad']) + ' Thankful: ' + str(post['Reactions: Thankful']) + ' Angry: ' + str(post['Reactions: Angry']) + ' Pride: ' + str(post['Reactions: Pride']) + '\n'
                            ) + '\n'
                            num = num + 1
                            body = { 
                            "fromPhone":bot_id,
                            "text": messageF,#publication.sts_text,
                            "toPhone":canalTelegram,
                            "channel":"telegram",
                            "messageBodyType":"chat"
                            }
                            getSendMessage(log,body,configuration)
 
                        tt = 'Sin Fecha'
                        #msb = MessageBuild()
                       # mensaje = construirMensajeFacebook(log,msb,canalesTelegram[0])
                        
                        if configuration['copy_canaltelegram'] :
                            if configuration['sheet_active']:
                                body['text'] += "Canal:  " + canalesTelegram.name_proyect+ "\n"
                            else:
                                body['text'] += "Canal:  " + canalesTelegram.name_chat+ "\n"
                            body['toPhone'] = '-1001429915200'
                            getSendMessage(log,body,configuration)
                    return True
                else:
                    return False
            else:
                return False
    except Exception as e:
        log.error("StreamRouter metodo: SendTelegram => %s  " % (e),True,True)
        return False
        
def SendTelegram(log,data,publication : PublicationMonibot ,type):
    try:
        configuration = cargaConfig(log)
        autor : str
        autor = publication.name 
        textoFinal = publication.sts_text_format
        # filtrarPaquete(publication.package_name) and
        if ( publication.sts_text != "" and publication.sts_text != None):
            #validar duplcidos Utilidades.convertToSha1
            clientId = publication.client_id
            if(publication.process_attitude == 'V2'):
                attitude = publication.attitude
                if configuration['sheet_active']:
                    canalesTelegram = getListPortsByClientId(log,configuration,int(publication.client_id))
                else:
                    canalesTelegram = buscarTelegramCanal(log,int(publication.client_id))
                if len(canalesTelegram) >0 :
                    configuration = cargaConfig(log)
                    if configuration['sheet_active']:
                        canalTelegram = canalesTelegram[0].channel
                    else:
                        canalTelegram = canalesTelegram[0].id_channel
                    if configuration['custom_canaltelegram'] != '':
                        # canalTelegram = '-1001429915200'
                        canalTelegram = configuration['custom_canaltelegram']
                    
                    bot_id =  configuration['bot_id']
                    # campo diferente con el de facebook
                    if type == 'twitter':
                        fechaStr = epochToDateStr(publication.created_at,'%a %b %d %H:%M:%S   %Y')                            
                    elif type == 'facebook':
                        fechaStr = publication.created_at
                    else:
                        fechaStr = epochToDateStr(publication.created_at,'%a %b %d %H:%M:%S   %Y')
                    datetime_object = encontrarFormatoFecha(fechaStr)
                    if datetime_object != None:
                        tt = datetimeToStr(dateToStringLocal(datetime_object,configuration['utc_tel']),"%Y-%m-%d %H:%M:%S")
                    else:
                        tt = 'Sin Fecha'
                    if publication.engine == 'RSS':
                        publication.engine = 'Google'
                    msb = MessageBuild(publication.sts_text,publication.engine,publication.name,tt,'No disponible','No disponible',publication.sts_text_format,publication.attitude,'No disponible',publication.source_url)
                    mensaje = construirMensaje(log,msb,publication.rule,canalesTelegram[0])
                    body = { 
                        "fromPhone":bot_id,
                        "text":mensaje,
                        "toPhone":canalTelegram,
                        "channel":"telegram",
                        "messageBodyType":"chat"
                    }
                    getSendMessage(log,body,configuration)
                    if configuration['copy_canaltelegram'] :
                        if configuration['sheet_active']:
                            body['text'] += "Canal:  " + canalesTelegram.name_proyect+ "\n"
                        else:
                            body['text'] += "Canal:  " + canalesTelegram.name_chat+ "\n"
                        body['toPhone'] = '-1001429915200'
                        getSendMessage(log,body,configuration)
                return True,True
            else:
                return False,True
        else:
            return False,True
    except Exception as e:
        log.error("StreamRouter metodo: SendTelegram => %s  " % (e),True,True)
        return False,False

def filtrarPaquete(paquete : str):
        if (paquete == 'com.twitter.android' or paquete == 'com.google.android.youtube' or paquete == 'com.whatsapp' or  paquete == 'com.facebook' or paquete == 'com.facebook.katana'):
            return True
        else:
            return False

#Envíar tweet a servicio monibot
def buscarTelegramCanal(log,client_id : int):
    suntzubd = SuntzuBd(log)
    if suntzubd.status:
        telegramGroup : List[MonibotTelegram]
        try:
            telegramGroup = []
            telegramGroup =  suntzubd.getListMonibotTelegram(client_id)
            #cargar lista de mensajes 
            if (telegramGroup == None or len(telegramGroup) == 0):
                #LOG.info('No existe grupo de telegram para el cliente: '+ id )
                print("No existe grupo de telegram para el cliente:")
        except Exception as e:
            #LOG.info("No se encontró grupo, se envía al general");
            print("No grupos telegram por cliente ")
        suntzubd.end()
        return telegramGroup
    else:
        return False
def construirMensajeFacebook(log,messageBuild,canalesTelegram):
    configuration = cargaConfig(log)
    urlPost = messageBuild.sourceUrl[0]
    return str

def construirMensaje(log,messageBuild,regla,canalesTelegram):
    configuration = cargaConfig(log)
    urlPost = messageBuild.sourceUrl[0]
    str = ''
    if(messageBuild.sourceUrl == None):
        urlPost = obtenerLink(messageBuild.mensaje);

    if(messageBuild.attitudeResponse==None):
        messageBuild.attitudeResponse = 'No disponible'
    str = "Fuente:  " + messageBuild.appName + "\n"
    str += "Autor: " + messageBuild.autor + "\n"
    if configuration['url_minimi']:
        str += "URL:  " + minimiUrl(urlPost,configuration) + "\n"
    else:
        str += "URL:  " + urlPost + "\n"
    
    if(messageBuild.typeAlert == None or messageBuild.typeAlert == ""):
        #str += "Actitud: " + messageBuild.AttitudeResponse + "\n"
        print("no hay regla")
    else:
        #str += "Intención: "+messageBuild.getIntention + "\n"
        print("no hay regla")
        
    str += "Fecha:  " + messageBuild.currentConverted + "\n"
    #str += "Hora:  " + messageBuild.getCurrentConverted().split(" ")[1] + "\n"
    # if(regla.startsWith("Interés:")):
    #    str += regla + "\n"
    # str.append("Regla:  " + regla + "\n");
    user = ', '.join(regla['user'])
    staff = ', '.join(regla['staff'])
    interes = ', '.join(regla['interes'])
    client = ', '.join(regla['prin'])
    if configuration['log'] and configuration['custom_canaltelegram'] != '':
        str += "Regla: user{ " +user+'}, staff {'+staff+' }, client {'+client+' }, interes {'+interes+"}\n"
        if messageBuild.appName == 'Google':
            str += "Rss::  " + messageBuild.textoFinal[0:255]+ "\n"
    else:
        if interes != '':
            interStr= '#'
            inter = interes.replace(","," ").split()
            for palabra in inter:
                interStr += palabra.capitalize()+" "
            str += "Interés:"+interStr+"\n"
    if messageBuild.appName == 'Google':
        pass
        # str += "Mensaje:  " + messageBuild.textoFinal[0:255]+ "\n"
    else:
        str += "Mensaje:  " + messageBuild.textoFinal+ "\n"
    if configuration['log'] and configuration['custom_canaltelegram'] != '':
        if configuration['sheet_active']:
            str += "Canal:  " + canalesTelegram.name_proyect+ "\n"
        else:
            str += "Canal:  " + canalesTelegram.name_chat+ "\n"
    #str += "Cliente_id: "+ str(canalesTelegram.client_id)
        
    return str

def getSendMessage(log,body,configuration):
    print("abriendo getSendMessage")
    # configuration = cargaConfig(log)
    url_base = configuration['api_bus']
    print(url_base)
    print(body)
    response_getSH = POSTAT(log,url_base, body)
    print(response_getSH)

    if response_getSH.status_code == 200:
        #logging.info("Respuesta del servicio de guardado: ==>" + response_getSH.status_code)
        sh = response_getSH.json()
        if sh['success']:
            return True
        else:
            return False
    else:
        log.error("Error con el envio de mensaje por Bus ")

def obtenerLink(mensaje):
    if (mensaje.find("https://t.co/") >= 0):
        i = mensaje.find("https://t.co/")
        return mensaje[i:]
    else:
        return 'No disponible'


def SaveTwitterBD(tweet):
    TweetSaves = {"name_screen":"", "id":"","profile_image":"", "text":""}

    for items in tweet["user"]["name_screen"]:
        TweetSaves["name_screen"] = items

    for items in tweet["user"]["id"]:
        TweetSaves["id"] = items   

        for items in tweet["user"]["profile_image_url"]:
            TweetSaves["profile_image"] = items

        for items in tweet["text"]:
            TweetSaves["text"] = items    

    with open("FileProcess/tt.json", 'a', encoding='utf-8') as f:
            json.dump(TweetSaves, f, ensure_ascii=False, indent=4)




# def send(item):
#     print(item)




# def getStakeholdersMonibot(log):
#     with open("config.ini", "r") as f:
#         configuration = json.loads(f.read())
#     url_base = configuration['url_base']
#     response_getSH = sendSHaccount(log,url_base + 'Twitter/GetUserAccount', configuration['client_id'])
#     if response_getSH.status_code == 200:
#         log.error("Número de tuits a mostrar")
#         stakeholderList = response_getSH.json()
#     else:
#         log.error("Número de tuits a mostrar")

#     return stakeholderList

# def saveStakeholdersMonibot(sh_id, client_id, account, account_id,log):
#     with open("config.ini", "r") as f:
#         configuration = json.loads(f.read())
#     url_base = configuration['url_base']
#     response_getSH = saveSHaccount(log,url_base + 'Twitter/SaveStakeholderAccount', sh_id, client_id, account, account_id)
#     if response_getSH.status_code == 200:
#         log.info("Stakeholder editado correctamente")
#     else:
#         log.error("Número de tuits a mostrar")

# def getTrends():
#     print("Id's de paises a consultar")
#     api = logAuth()
#     trends = api.trends_place(116545)
#     return trends

# def getGeo():
#     print("Id's de paises a consultar")
#     api = logAuth()
#     locations = api.trends_available()
#     return locations

# def getUser(log):
#     print("Obteniendo la información por usuario")
#     api = logAuth()
#     #logging.error("Prueba log ERROR=>CLASS: MANAGE_TWEET => FUNCTION: getUser")
#     accountID = ""
#     try:
#         users = getStakeholdersMonibot()
#         if users != None:
#             for stakeholder in users['ListStakeholders']:
#                 try:
#                     useritem = api.get_user(stakeholder['account'])
#                     accountID = useritem.id_str
#                 except Exception as e:
#                     accountID = ""

#                 saveStakeholdersMonibot(stakeholder['stakeholder_id'], stakeholder['client_id'], stakeholder['account'], accountID)
#                 log.info("Stakeholder agregado a bd")
#                 sleep(0.3)
#                 #stakeholder['account_id'] = useritem.id
#     except Exception as e:
#         solicitud = {'status_code': 500}
#         log.error("Exception: "+str(e))

#     useritem = api.get_user('@SCJN')
#     return useritem 