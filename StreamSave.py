import pika
import json
import argparse
from Utilities.utils import cargaConfig, JsonToObject, cifradoCesar
from Utilities.log import log_file
from Utilities.mq import mqClass 
from Utilities.timeScan import timeClass
from Controller.FilesController import getListChannelByStakeholderAll_facebook, GetPortByCliet_id, getListChannelByStakeholderAll, getListPortsByClientAll, getListChannelByStakeholderForNameAndClientid, loadChannelByStakeholder, getAliasSH, getInterestMonibotWords
from Controller.manage_tweet import SaveTweetByAccount, characterizeTwetter, rssToTwitter
from Entity.Publics import channel_by_stakeholder, clientPort
from typing import List
from Utilities.theread import threadingClass
from Utilities.FIFO import pila

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="Nombre de MQ")
parser.add_argument("-c", "--client", help="Nombre de cliente")
args = parser.parse_args()
listport = []
def main():
    mq = mqClass(log)
    try:
        mq.consume(args.name.rstrip().lstrip(),callback)
        mq.reconect(log)
        main()
    except Exception as e:
        log.error("StreamRouter => %s  " % (e),True,True)
        main()

#Guarda en la base de datos
def callback(ch, method, properties, body):
    try:
        if configuration['memcached']:
            pi = pila(log);   
        else:
            pi = None
        t =  timeClass(log ,"callback")
        jsonData = json.loads(body)
        post_data = jsonData['data']
        if jsonData['type'] == 'twitter':
            name = post_data['user']['screen_name']
            id_data =  post_data['id_str']
            hora_data = post_data['created_at']
            chanel = channel_by_stakeholders
        if jsonData['type'] == 'rss':
            name = post_data['account']
            post_data['id_str'] = cifradoCesar(post_data['url'],7)
            id_data =  post_data['id_str']
            hora_data = post_data['published']
            chanel = channel_by_stakeholders
        if jsonData['type'] == 'facebook':
            name = post_data['account']
            id_data =  post_data['id_str']
            hora_data = post_data['Created time']
            post_data['Post link'] = post_data['Post link']
            chanel = channel_by_stakeholders_F
        if configuration['listIdTw'].find(id_data) < 0 :
            channel_by_stakeholder = getListChannelByStakeholderForNameAndClientid(name,int(args.client),chanel)
            if configuration['save_bd']:
                ChannelByStakeholder = SaveTweetByAccount(log,post_data,jsonData,int(args.client),channel_by_stakeholder,configuration)
            else:
                ChannelByStakeholder = {"data" :channel_by_stakeholder, "status":True}
                log.info("SaveTweetByAccount => Stakeholder ==> Desactivado guardado de base de datos channel_by_stakeholder => "+name,True,True)  
            if ChannelByStakeholder['status']:
                    for target_list in ChannelByStakeholder['data']:
                        if configuration['threading']:
                            p1 =  threadingClass(log)
                            arg = (log,configuration,post_data,jsonData,int(args.client),pi,target_list,)
                            p1.selectFunction("saveTwetterBd",id_data,arg)
                            p1.start()
                        else:
                            sendTel = characterizeTwetter(log,configuration,post_data,pi,target_list, jsonData['type'])
                            if sendTel[0]:
                                configuration['listIdTw'] += id_data+' '
                                break
            log.warning("StreamSave =>TW :"+id_data,True,True,t.end())
            try:
                colaTweet = {}
                envioMensajeBk = False
                if len(listport) > 0:
                    if configuration['bk_active']:
                        if configuration['valida_sh']: 
                            if len(ChannelByStakeholder['data']) > 0 and listport[0].bk_full:
                                envioMensajeBk = True
                            elif len(ChannelByStakeholder['data']) > 0 and sendTel[0] and listport[0].bk_send:
                                envioMensajeBk = True
                        else:
                            if listport[0].bk_full:
                                envioMensajeBk = True
                            elif sendTel[0] and listport[0].bk_send:
                                envioMensajeBk = True
                        if envioMensajeBk:
                            colaTweet.update(data=post_data.copy())
                            colaTweet.update(type=jsonData['type'])
                            colaTweet.update(client_id=channel_by_stakeholder[0].client_id)
                            colaTweet.update(modulo='StreamSave')
                            colaTweet.update(valida_sh=configuration['valida_sh'])
                            colaTweet.update(bk_full=listport[0].bk_full)
                            colaTweet.update(bk_send=listport[0].bk_send)
                            colaTweet = json.dumps(colaTweet)
                            if not mq1.add(colaTweet, configuration['bk_telegram']):
                                mq2 = mqClass(log)
                                mq2.declare(configuration['bk_telegram'])
                                mq2.add(colaTweet, configuration['bk_telegram'])
            except Exception as et:
                log.error("callback => Exception => StreamSave => IError al guardar el mq %s => %s : %s " % (jsonData['type'],et, "General"),True,True)
        else:
            log.warning("StreamSave => callback "+jsonData['type']+" existente :"+id_data,True,True,t.end())
    except Exception as e:
        log.error("StreamRouter => %s  " % (e),True,True)
        


if args.name and args.client:
    log = log_file("C:\Log\Stream\StreamSave"+args.name.rstrip().lstrip().capitalize()+".log")
    
    configuration = cargaConfig(log)
    configuration['listIdTw'] = ''
    mq1 = mqClass(log)
    mq1.declare(configuration['bk_telegram'])
    log.log_File=configuration['log']
    log.warning("################################################",True);
    log.warning("#-INICIANDO PYTHON STREAM SAVE client "+str(args.client)+"-#####",True);
    log.warning("################################################",True);
    log.warning("",True,True);
    log.warning("Log_File: "+str(configuration['log']),True);
    log.printer("Abriendo canal",True)
    listport = GetPortByCliet_id(log,getListPortsByClientAll(),int(args.client))
    # channel_by_stakeholders : List[channel_by_stakeholder] = JsonToObject(loadChannelByStakeholder(), List[channel_by_stakeholder])
    channel_by_stakeholders = getListChannelByStakeholderAll()
    channel_by_stakeholders_F = getListChannelByStakeholderAll_facebook()

    main()
    