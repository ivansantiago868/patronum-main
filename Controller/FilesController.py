import json
from Utilities.utils import JsonToObject, ObjectToJson, ObjectToStr, cargaConfig
from typing import List
from Entity.Publics import channel_by_stakeholder ,NicknameSH, TypesWords, clientPort#, ListSH
from Controller.SuntzuController import SuntzuBd
from Utilities.http_service import POSTAliasSh
import re
from time import time
from Utilities.timeScan import timeClass
# from Utilities.log import log_file

file_name_class = 'FileController.py'

"""
@Response
    <channel_by_stakeholder:channel_by_stakeholder> Regresa un objete en el cual contiene una lista de channel by stakeholder
@Response
"""
def getListChannelByStakeholderAll():
    dict_a = loadChannelByStakeholder()['sh']
    channel_by_stakeholders : List[channel_by_stakeholder] = JsonToObject(dict_a, List[channel_by_stakeholder])
    return channel_by_stakeholders
"""
Funcion para leer el archivo de ChannelByStakeholder para monibot  
"""
def loadChannelByStakeholder():
    attitudeWords = []
    with open("FileProcess/Modelo_Channel_by_stakeholder.json", "r") as f:
        attitudeWords = json.loads(f.read())
    return attitudeWords

def getListChannelByStakeholderAll_facebook():
    dict_a = loadChannelByStakeholder_facebook()['sh']
    channel_by_stakeholders : List[channel_by_stakeholder] = JsonToObject(dict_a, List[channel_by_stakeholder])
    return channel_by_stakeholders

def loadChannelByStakeholder_facebook():
    attitudeWords = []
    with open("FileProcess/Modelo_Channel_by_stakeholder_facebook.json", "r") as f:
        attitudeWords = json.loads(f.read())
    return attitudeWords

def getListPortsByClientAll():
    dict_a = loadPortByClients()['port']
    ports_by_client : List[clientPort] = JsonToObject(dict_a, List[clientPort])
    return ports_by_client
"""
Funcion para leer el archivo de ChannelByStakeholder para monibot  
"""
def loadPortByClients():
    attitudeWords = []
    with open("FileProcess/Modelo_port_by_client.json", "r") as f:
        attitudeWords = json.loads(f.read())
    return attitudeWords

def getFileConfigByClient(log):
    t = timeClass(log,'getFileConfigByClient')
    log.info( 'inicio de getFileConfigByClient' + file_name_class+'',True,True)
    suntzubd = SuntzuBd(log)
    if suntzubd.status:
        port_by_clints = suntzubd.getPortByClints()
        if len(port_by_clints) > 0:
            result = ObjectToStr(port_by_clints)
            with open('FileProcess/Modelo_port_by_client.json', 'w') as json_file:
                json.dump(result, json_file)
            log.warning( 'Archivo de getFileConfigByClient creado correctamente!!!!' + file_name_class+' ',True,True,t.end())
            return True
        else:
            log.error( 'Problemas al obtener el getFileConfigByClient'+file_name_class+' ',True,True)
            return False
    else:
        return False
def GetPortByCliet_id(log,data,client_id):
    find_sh = list(filter(lambda x: x['client_id'] == client_id, ObjectToJson(data)))
    clientPorts : List[clientPort] = JsonToObject(find_sh, List[clientPort])
    return clientPorts

def getFileIdTwtterByClient(log,clients):
    log.info( 'inicio de getFileIdTwtterByClient' + file_name_class+'',True,True)
    suntzubd = SuntzuBd(log)
    if suntzubd.status:
        sh = suntzubd.getStakeholderByClient(clients)
        accountIDS = ""
        for item in sh:
            if accountIDS == "":
                accountIDS = item.account_id
            else:
                accountIDS = accountIDS +", " + item.account_id
        return accountIDS

def getFileChannelByStakeholder(log):
    t = timeClass(log,'getFileChannelByStakeholder')
    log.info( 'inicio de getFileChannelByStakeholder' + file_name_class+'',True,True)
    suntzubd = SuntzuBd(log)
    if suntzubd.status:
        channel_by_stakeholders = suntzubd.getChannel_by_stakeholder()
        if len(channel_by_stakeholders) > 0:
            result = ObjectToStr(channel_by_stakeholders)
            with open('FileProcess/Modelo_Channel_by_stakeholder.json', 'w') as json_file:
                json.dump(result, json_file)
            log.warning( 'Archivo de getFileChannelByStakeholder creado correctamente!!!!' + file_name_class+'getFileChannelByStakeholder',True,True,t.end())
            return True
        else:
            log.error( 'Problemas al obtener el getFileChannelByStakeholder'+file_name_class+'getFileChannelByStakeholder',True,True)
            return False
    else:
        return False

def getTweetsID(log):
    suntzuBd = SuntzuBd(log)
    if suntzuBd.status:
        tweets = suntzuBd.getIDTweet()
        return tweets
"""
Funcion para generar el archivo de alias por sh de todos los cliente
"""
def getAliasSH(log):
    t = timeClass(log,'getAliasSH')
    configuration = {}
    configuration = cargaConfig(log)
    url_base = configuration['url_base']
    #response_reactions = POSTAliasSh(log,url_base + '/attitude/Search/Result/Alias/Get', '{}')
    response_reactions = POSTAliasSh(log,url_base + '/cognitive/attitude/Search/Result/Alias/Get', '{}')

    if response_reactions.status_code == 200:
        result = response_reactions.json()
        with open('FileProcess/Modelo_aliasSH.json', 'w') as json_file:
            json.dump(result, json_file)

        log.warning( 'Archivo de alias creado correctamente!!!!'+ file_name_class+ 'getAliasSH',True,True,t.end())
        #logger('info', result['alias'], file_name_class, 'getAliasSH')
        return True
    else:
        log.error( 'Problemas al obtener los alias de los SH'+ file_name_class+ 'getAliasSH',True,True)
        return False
"""
Funcion para crear el archivo con los tags  de todos los cliente, este archivo solo lo ocupa monibot
"""
def getInterestMonibotWords(log):
    t = timeClass(log,'getInterestMonibotWords')
    configuration = {}
    configuration = cargaConfig(log)
    url_base = configuration['url_base']
    response_reactions = POSTAliasSh(log,url_base + '/cognitive/attitude/Monibot/Interest/Get', '{}')

    if response_reactions.status_code == 200:
        result = response_reactions.json()
        with open('FileProcess/Modelo_interestMonibotWords.json', 'w') as json_file:
            json.dump(result, json_file)

        log.warning( 'Archivo de palabras creado correctamente!!!!' + file_name_class+'getInterestMonibotWords',True,True,t.end())
        return True
    else:
        log.error( 'Problemas al obtener el attitude de las palabras'+file_name_class+'getInterestMonibotWords',True,True)
        return False

def getNickanmeObjectByClientId(clientId: int = None, sheet : bool =  False):
    if sheet:
        data = loadNicknamesSH()['alias']
    else:
        data = loadNicknamesSH()['alias']
    if clientId == None:
        find_sh = list(data)
    else:
        find_sh = list(filter(lambda x: int(x['client_id']) == int(clientId), data))
    nicknames: List[NicknameSH] = JsonToObject(find_sh, List[NicknameSH])
    return nicknames

"""
Funcion para leer el archivo que contiene los alias de cada SH de todos los clientes
"""
def loadNicknamesSH():
    nicknames = []
    with open("FileProcess/Modelo_aliasSH.json", "r") as f:
        nicknames = json.loads(f.read())
    return nicknames

def getNickanmeObjectByClientIdAndInternal(clientId: int =  None, isInternal: bool = True):
    data = loadNicknamesSH()['alias']
    if clientId == None:
        find_sh = list(filter(lambda x: bool(x['is_internal'] == bool(isInternal)), data))
    else:
        find_sh = list(filter(lambda x: int(x['client_id']) == int(clientId) and bool(x['is_internal'] == bool(isInternal)), data))
    nicknames: List[NicknameSH] = JsonToObject(find_sh, List[NicknameSH])

    return nicknames
"""
@Response
    <channel_by_stakeholder:channel_by_stakeholder> Regresa un objete en el cual contiene una lista de channel by stakeholder por nombre de user name 
@Response
"""
def getListChannelByStakeholderForName(name:str,client_id:int):
    dict_a = loadChannelByStakeholder()['sh']
    channel_by_stakeholders : List[channel_by_stakeholder] = JsonToObject(dict_a, List[channel_by_stakeholder])
    filter_channel_by_stakeholders = []
    for cbs in channel_by_stakeholders:
        if (cbs.account.upper() == name.upper() or cbs.account.upper() == "@"+name.upper()) and cbs.client_id == client_id:
            filter_channel_by_stakeholders.append(cbs)
    return filter_channel_by_stakeholders
"""
Funcion para fltras por cliente ChannelByStakeholder
"""
def getListChannelByStakeholderForNameAndClientid(name:str,client_id:int,channel_by_stakeholders : List[channel_by_stakeholder]):
    filter_channel_by_stakeholders = []
    total = False
    for cbs in channel_by_stakeholders:    
        if (cbs.account.upper() == name.upper() or cbs.account.upper() == "@"+name.upper()) and cbs.client_id == client_id:
            if cbs.tipo.upper() == 'TOTAL'.upper():
                total = True
                listIni = []
                listIni.append(cbs)
                filter_channel_by_stakeholders = listIni + filter_channel_by_stakeholders
            else:  
                filter_channel_by_stakeholders.append(cbs)
    
    return filter_channel_by_stakeholders
"""
Funcion para leer el archivo de intereses para monibot  
"""
def loadInterestMonibotWords():
    attitudeWords = []
    with open("FileProcess/Modelo_interestMonibotWords.json", "r") as f:
        attitudeWords = json.loads(f.read())
    return attitudeWords

def loadExceptionsMoniBotWords():
    exceptionsWords = []
    with open("FileProcess/Modelo_exceptionsMonibotWords.json", "r") as f:
        exceptionsWords = json.loads(f.read())
    return exceptionsWords
"""
@Response
    <types_words:TypesWords>    Regresa un objete en el cual contiene una lista de palabras positivas, negativas y positivas
@Response
"""
def getListWordsInterestMonibot(client_id:int,search_id:str):

    #Derechos y libertades===#LibertadDePrensa
    #Derechos y libertades===Libertad de Prensa
    #Derechos y libertades===acceso a la justicia
    #Derechos y libertades===democracia en México

    #Familia === Patria potestad
    #Familia === juicio de divorcio
    #Familia === violencia familiar
    #Familia === violencia intrafamiliar
    #Familia === pensión alimenticia
    #Familia === adopción homoparental

    
    dict_a = loadInterestMonibotWords()["words"]
    info = list(map(lambda x: str(x['title']).strip().lower()+'==='+str(x['word']).strip().lower(),
                    filter(lambda x: x['evaluation'] == "Informativo"
                                     and (x['client_id'] == client_id or x['client_id'] == 0) and str(x['word']).strip().lower() != "", dict_a)))
    neg = list(map(lambda x: str(x['title']).strip().lower()+'==='+str(x['word']).strip().lower(),
                   filter(lambda x: x['evaluation'] == "Negativo"
                                    and (x['client_id'] == client_id or x['client_id'] == 0) and str(x['word']).strip().lower() != "", dict_a)))
    pos = list(map(lambda x: str(x['title']).strip().lower()+'==='+str(x['word']).strip().lower(),
                   filter(lambda x: x['evaluation'] == "Positivo"
                                    and (x['client_id'] == client_id or x['client_id'] == 0)  and str(x['word']).strip().lower() != "", dict_a)))
    types_words = TypesWords(info,pos,neg)
    return types_words

#Funcion para leer el archivo de exepcions para monibot  
def getListWordExceptionsMonibot(client_id:int, search:str):
    dict_exceptions = loadExceptionsMoniBotWords()["words"]
    exceptions = list(map(lambda x: str(x['word']).strip().lower()+'==='+str(x['word']).strip().lower(),
                    filter(lambda x: x['client_id'] == client_id or (x['client_id'] == 0) and str(x['word']).strip().lower() != "", dict_exceptions)))
    return exceptions
#Función Regresa un objete en el cual contiene una lista de palabras excepción
def getWordsFromTextMonibot(sts:str,words:List[str]):
    try:
        start_time = time()
        listDelimitados = [',','.',';',':']
        # print("words: "+str(len(words)))
        # words_existe = [word for word in words if word.lower() in str(sts).lower()]
        #listText = sts.replace('.', '').replace(',', '').split(' ')
        #words_existe = getSamesItem(listText, words)
        #words_existe = [w for w in words if " " + w.lower() + " " in " " + sts.lower() + " "]
        # for xy in words:
        #     print("xy: "+xy)
            #list(filter(None, re.split("[===]+", xy.lower())))
        words_existe = [w for w in words if " "+list(filter(None, re.split("[===]+", w.lower())))[1]+" " in " "+sts.lower()+" "]

        for item in listDelimitados:
           words_existeAlter = [w for w in words if " "+list(filter(None, re.split("[===]+", w.lower())))[1]+item in " "+sts.lower()+item]
           words_existe.extend(words_existeAlter)
        # print("words_existe: "+str(len(words_existe)));
        elapsed_time = time() - start_time
        # print("words_existe time: %.10f seconds." % elapsed_time)
        return words_existe
    except Exception as e:
        # print("getWordsFromTextMonibot")
        words_existe = []
        return words_existe

# def getSHByClient(client_id):
#     print("..................")
#     dict_a = loadAttitudeSH()['SH']
#     find_sh = {'list_sh':list(filter(lambda x:  x['client_id'] == client_id , dict_a))}

#     shs: ListSH = JsonToObject(find_sh, ListSH)
#     return shs

# """
# Funcion para leer el archivo de attitude de cada uno de los sh que hay de todos los clientes esto se ocupa en la attitudeV2
# """
# def loadAttitudeSH():
#     attitudeSH = []
#     with open("FileProcess/attitudeSH.json", "r") as f:
#         attitudeSH = json.loads(f.read())
#     return attitudeSH


def getListModelo_InteresCompuesto():
    InteresCompuesto_Modelos = []
    with open("FileProcess/Modelo_InteresCompuestosWords.json", "r") as f:
        InteresCompuesto_Modelos = json.loads(f.read())
    return InteresCompuesto_Modelos


"""
@Response
    <types_words:TypesWords>    Regresa un objete en el cual contiene una lista de palabras positivas, negativas y positivas
@Response
"""
def getListWordsInterestCompuestoMonibot(client_id:int,search_id:str):
    dict_a = getListModelo_InteresCompuesto()["word"]
    info = list(map(lambda x: str(x['title']).strip().lower()+'==='+str(x['word']).strip().lower()+'==='+str(x['idInteres']).strip().lower()+'==='+str(x['numInteres']).strip().lower(),
                    filter(lambda x: x['evaluation'] == "Informativo"
                                    and (x['client_id'] == client_id or x['client_id'] == 0) and str(x['word']).strip().lower() != "", dict_a)))
    neg = list(map(lambda x: str(x['title']).strip().lower()+'==='+str(x['word']).strip().lower(),
                   filter(lambda x: x['evaluation'] == "Negativo"
                                    and (x['client_id'] == client_id or x['client_id'] == 0) , dict_a)))
    pos = list(map(lambda x: str(x['title']).strip().lower()+'==='+str(x['word']).strip().lower(),
                   filter(lambda x: x['evaluation'] == "Positivo"
                                    and (x['client_id'] == client_id or x['client_id'] == 0) , dict_a)))
    types_words = TypesWords(info,pos,neg)
    return types_words


def getWordsFromTextMonibotInteresCompuesto(sts:str,words:List[str]):
    try:    
        # sts ="estes es un mensaje presidente de Lala este es el segundo interes @SigmaAlimentos "
        start_time = time()
        listDelimitados = [',','.',';',':']
        word_exist_interes_uno , word_exist_interes_dos = [] , []
        for item in listDelimitados:
            word_exist_interes_uno  = findWordCompuesto(sts , words , item , [True] )
            if len(word_exist_interes_uno)  > 0 : break

        if len(word_exist_interes_uno) > 0 :
            # print("###########################################")
            # print("Encontramos el primer interes")
            for item in listDelimitados:
                word_exist_interes_dos  = findWordCompuesto(sts , words , item , [False ,word_exist_interes_uno[2]])
                if len(word_exist_interes_dos)  > 0 : break
            if len(word_exist_interes_dos)  > 0:
                elapsed_time = time() - start_time
                # print("###########################################")
                # print("Encontramos los dos intereses")
                return word_exist_interes_uno , word_exist_interes_dos
            else:
                # print("###########################################")
                # print("No se encontro el segundo interes")
                elapsed_time = time() - start_time
                word_exist_interes_uno , word_exist_interes_dos = [] , []
                return word_exist_interes_uno , word_exist_interes_dos
        else:
            # print("###########################################")
            # print("No se encontro el primer interes")
            elapsed_time = time() - start_time
            return word_exist_interes_uno , word_exist_interes_dos
    except Exception as e:
        word_exist_interes_uno , word_exist_interes_dos  = [] ,  [] 
        # print("getWordsFromTextMonibot")
        words_existe = []
        return word_exist_interes_uno , word_exist_interes_dos

def findWordCompuesto(sts , words:List[str] , item , findCondition):
    for wordInteres in words:
        data =  list(filter(None, re.split("[===]+", wordInteres.lower())))
        if findCondition[0] :
            if (" "+data[1]+item in " "+sts.lower()+item  or " "+data[1] in " "+sts.lower() ) and data[3] == "interes1":
                return data
        else:
            if (data[3] == "interes2" and data[2] == findCondition[1] and data[0] == "none"):
                #  (" "+data[1]+item in " "+sts.lower()+item  or " "+data[1] in " "+sts.lower()) and data[3] == "interes2" and data[2] == findCondition[1]:
                return [False]    
            elif(" "+data[1]+item in " "+sts.lower()+item  or " "+data[1] in " "+sts.lower()) and data[3] == "interes2" and data[2] == findCondition[1]:
                return  data
    return []


    