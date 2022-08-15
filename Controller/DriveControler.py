from Utilities.drive  import driverClass
import json
from Utilities.timeScan import timeClass
from Entity.Publics import client,clientPort, relation, stakeholder_general, stakeholder, channel_by_stakeholder, NicknameSH, interes_client, InteresMonibot, ExceptionsMonibot, exceptions_client, Query ,interes_compuesto_client
from Utilities.utils import JsonToObject,ObjectToJson, OrdenarjsonPorKey, UnicoJson
from typing import List
import numpy as np

file_name_class = ' DriverController.py'
"""
Funciones para carga de archivos desde Google Drive 
"""
def UpdateCelda(log , SAMPLE_SPREADSHEET_ID ,serverID,posicion,valueData):
    t = timeClass(log,'UpdateCelda')
    log.info( 'inicio de UpdateCelda' + file_name_class+'',True,True)
    dr = driverClass(log)
    try:
        celda=dr.SetDataUpdate(SAMPLE_SPREADSHEET_ID,serverID,posicion,valueData)
        log.info( f'se actualizo el sheet en la celda {str(celda)}',True,True)
    except Exception as e :
        log.error( 'Problemas al actualizar sheet de verdadero a falso :'+str(e),True,True)

def setFileListClientSheet(log,SHEET_ID,SHEET_INI,SHEET_TITTLE,SHEET_DATA,RELATION):
    t = timeClass(log,'setFileListClientSheet ')
    log.info( 'inicio de setFileListClientSheet ' + file_name_class+' hoja: ' + SHEET_INI,True,True)
    try:
        dr = driverClass(log)
        rela = [] 
        for item in RELATION:
            obj = {}
            obj['objeto'] = item['objeto']
            obj['name'] = item['name']
            obj['hoja'] = SHEET_INI
            obj['type'] = item['type']
            rela.append(obj)
        relations : List[relation] = JsonToObject(rela, List[relation])
        dr.relations = relations
        data = dr.configClinet(SHEET_ID,SHEET_INI,SHEET_TITTLE,SHEET_DATA,SHEET_INI)
        # clientPorts : List[clientPort] = JsonToObject(data, List[clientPort])
        with open('FileProcess/driver_'+SHEET_INI+'.json', 'w') as json_file:
            json.dump(data, json_file)
        log.warning( 'Archivo de setFileListClientSheet creado correctamente!!!!' + file_name_class+' hoja: ' + SHEET_INI,True,True,t.end())
        return data
    except Exception as e :
        log.error( 'Problemas al guardar el setFileListClientSheet '+file_name_class+' hoja: ' + SHEET_INI,True,True)

def mappingConfig(log,configurationInicio):
    try:
        count = 0
        while count < len(configurationInicio['Hojas']):
            configurationInicio['Hojas'][count]['dataset']= setFileListClientSheet(log,configurationInicio['SHEET_ID'],configurationInicio['Hojas'][count]['NAME'],configurationInicio['Hojas'][count]['TITLE'],configurationInicio['Hojas'][count]['DATA'],configurationInicio['Hojas'][count]['RELATION'])
            count += 1 
        Config = []
        for lista_clinetes in configurationInicio['Hojas']:
            if lista_clinetes['NAME'] == 'Config':
                for listaConfig in lista_clinetes['dataset']:
                    if listaConfig['name'] == configurationInicio['AMBIENTE']:
                        Config = listaConfig
                        Config['HojasConfig'] = []
                        Config['BDConfig'] = []
            if lista_clinetes['NAME'] == 'Hojas':                    
                for listaConfig in lista_clinetes['dataset']:
                    if listaConfig['config_id'] == Config['hojas']:
                        Config['HojasConfig'].append(listaConfig)
            if lista_clinetes['NAME'] == 'Pass':                    
                for listaConfig in lista_clinetes['dataset']:
                    if listaConfig['id_bd'] == Config['bd']:
                        Config['BDConfig'].append(listaConfig)
        for HojasConfig_list in Config['HojasConfig']:
            if HojasConfig_list['name'] == "Servers" or HojasConfig_list['name'] == "Trends" or HojasConfig_list['name'] == "RSS" :
                # relation = json.loads(HojasConfig_list['relation'])
                infoServer = setFileListClientSheet(log,Config['sheet'],HojasConfig_list['name'],HojasConfig_list['tittle'],HojasConfig_list['data'],HojasConfig_list['relation'])
                Config[HojasConfig_list['name']] = []
                for infoServer_id in infoServer:
                    if int(infoServer_id['server_id']) ==configurationInicio['server_id']:
                        Config[HojasConfig_list['name']].append(infoServer_id)
        return Config
    except Exception as e:
        log.error(str(e),"main",True,True)



"""
Funciones para administrar la hoja de los Query
"""
def setFileListQuerysClient(log, configuration):
    t = timeClass(log, 'setFileListQuerys')
    log.info('inicio de setFileListQuerys' +file_name_class+'', True, True)
    try:
        dr = driverClass(log)
        data = dr.configClinet(configuration['SHEET_ID'],configuration['SHEET_QUERY_INI'],configuration['SHEET_QUERY_TITTLE'],configuration['SHEET_QUERY_DATA'],configuration['SHEET_QUERY_INI'])
        # clientPorts : List[clientPort] = JsonToObject(data, List[clientPort])
        with open('FileProcess/driver_querys_client.json', 'w', encoding='utf8') as json_file:
            json.dump(data, json_file)
        log.warning('Archivo de setFileListQuerys creado correctamente!!!!' + file_name_class+' ', True, True, t.end())
    except Exception as e:
        log.error('Problemas al guardar el setFileListQuerys' +file_name_class+' ', True, True)
def getFileListQuerysClient(log, configuration):
    t = timeClass(log, 'getFileListQuerysClient')
    log.info('inicio de getFileListQuerysClient' +file_name_class+'', True, True)
    try:
        clients_json = []
        clients = []
        with open("FileProcess/driver_querys_client.json", "r", encoding='utf8') as f:
            clients_json = json.loads(f.read())

        return clients_json
        log.warning('Archivo de getFileListQuerysClient creado correctamente!!!!' +
                    file_name_class+' ', True, True, t.end())
    except Exception as e:
        log.error('Problemas al obtener el getFileListQuerysClient' +file_name_class+' ', True, True)
"""
Funciones para administrar la hoja de los clientes
"""

def setFileListClient(log,configuration):
    t = timeClass(log,'setFileListClient')
    log.info( 'inicio de setFileListClient' + file_name_class+'',True,True)
    try:
        dr = driverClass(log)
        data = dr.configClinet(configuration['SHEET_ID'],configuration['SHEET_CLIENT_INI'],configuration['SHEET_CLIENT_TITTLE'],configuration['SHEET_CLIENT_DATA'],configuration['SHEET_CLIENT_INI'])
        # clientPorts : List[clientPort] = JsonToObject(data, List[clientPort])
        with open('FileProcess/driver_port_by_client.json', 'w', encoding='utf8') as json_file:
            json.dump(data, json_file)
        log.warning( 'Archivo de setFileListClient creado correctamente!!!!' + file_name_class+' ',True,True,t.end())
    except Exception as e :
        log.error( 'Problemas al guardar el setFileListClient'+file_name_class+' ',True,True)

def getFileListClient(log,configuration):
    t = timeClass(log,'getFileListClient')
    log.info( 'inicio de getFileListClient' + file_name_class+'',True,True)
    try:
        clients_json = []
        clients = []
        with open("FileProcess/driver_port_by_client.json", "r", encoding='utf8') as f:
            clients_json = json.loads(f.read())
        
        return clients_json
        log.warning( 'Archivo de getFileListClient creado correctamente!!!!' + file_name_class+' ',True,True,t.end())
    except Exception as e :
        log.error( 'Problemas al obtener el getFileListClient'+file_name_class+' ',True,True)
        
def getListPortsByClientId(log,configuration,id):
    client_channels = []
    dict_a = getFileListClient(log,configuration)
    # ports_by_client : List[client] = JsonToObject(json.loads(dict_a), List[client])
    for client_channel in dict_a:
        if int(client_channel['client_id']) == id:
            cl = client()
            cl.addClient(client_channel)
            client_channels.append(cl)
    return client_channels
"""
Funciones para administrar la hoja de los sh generales
"""

def setFileListShGeneral(log,configuration):
    t = timeClass(log,'setFileListShGeneral')
    log.info( 'inicio de setFileListShGeneral' + file_name_class+'',True,True)
    try:
        dr = driverClass(log)
        data = dr.configClinet(configuration['SHEET_ID'],configuration['SHEET_SH_GENERAL_INI'],configuration['SHEET_SH_GENERAL_TITTLE'],configuration['SHEET_SH_GENERAL_DATA'],configuration['SHEET_SH_GENERAL_INI'])
        # clientPorts : List[clientPort] = JsonToObject(data, List[clientPort])
        with open('FileProcess/driver_list_sh_general.json', 'w' , encoding='utf8') as json_file:
            json.dump(data, json_file)
        log.warning( 'Archivo de setFileListShGeneral creado correctamente!!!!' + file_name_class+' ',True,True,t.end())
    except Exception as e :
        log.error( 'Problemas al guardar el setFileListShGeneral'+file_name_class+' ',True,True)

def getFileListShGeneral(log,configuration):
    t = timeClass(log,'getFileListShGeneral')
    log.info( 'inicio de getFileListShGeneral' + file_name_class+'',True,True)
    try:
        clients_json = []
        clients = []
        with open("FileProcess/driver_list_sh_general.json", "r", encoding='utf8') as f:
            clients_json = json.loads(f.read())
        
        return clients_json
        log.warning( 'Archivo de getFileListShGeneral creado correctamente!!!!' + file_name_class+' ',True,True,t.end())
    except Exception as e :
        log.error( 'Problemas al obtener el getFileListShGeneral'+file_name_class+' ',True,True)
"""
Funciones para administrar la hoja de los sh por cliente 
"""

def setFileListShClient(log,configuration):
    t = timeClass(log,'setFileListShClient')
    log.info( 'inicio de setFileListShClient' + file_name_class+'',True,True)
    try:
        dr = driverClass(log)
        data = dr.configClinet(configuration['SHEET_ID'],configuration['SHEET_SH_INI'],configuration['SHEET_SH_TITTLE'],configuration['SHEET_SH_DATA'],configuration['SHEET_SH_INI'])
        # clientPorts : List[clientPort] = JsonToObject(data, List[clientPort])
        with open('FileProcess/driver_sh_client.json', 'w', encoding='utf8') as json_file:
            json.dump(data, json_file)
        log.warning( 'Archivo de setFileListShClient creado correctamente!!!!' + file_name_class+' ',True,True,t.end())
    except Exception as e :
        log.error( 'Problemas al guardar el setFileListShClient'+file_name_class+' ',True,True)

def getFileListShClient(log,configuration):
    t = timeClass(log,'getFileListShClient')
    log.info( 'inicio de getFileListShClient' + file_name_class+'',True,True)
    try:
        clients_json = []
        clients = []
        with open("FileProcess/driver_sh_client.json", "r", encoding='utf8') as f:
            clients_json = json.loads(f.read())
        
        return clients_json
        log.warning( 'Archivo de getFileListShClient creado correctamente!!!!' + file_name_class+' ',True,True,t.end())
    except Exception as e :
        log.error( 'Problemas al obtener el getFileListShClient'+file_name_class+' ',True,True)
"""
Funciones para administrar la hoja de los clientes
"""

def setFileListInteresClient(log,configuration):
    t = timeClass(log,'setFileListInteresClient')
    log.info( 'inicio de setFileListInteresClient' + file_name_class+'',True,True)
    try:
        dr = driverClass(log)
        data = dr.configClinet(configuration['SHEET_ID'],configuration['SHEET_INTERES_INI'],configuration['SHEET_INTERES_TITTLE'],configuration['SHEET_INTERES_DATA'],configuration['SHEET_INTERES_INI'])
        # clientPorts : List[clientPort] = JsonToObject(data, List[clientPort])
        with open('FileProcess/driver_interes_client.json', 'w', encoding='utf8') as json_file:
            json.dump(data, json_file)
        log.warning( 'Archivo de setFileListInteresClient creado correctamente!!!!' + file_name_class+' ',True,True,t.end())
    except Exception as e :
        log.error( 'Problemas al guardar el setFileListInteresClient'+file_name_class+' ',True,True)

def getFileListInteresClient(log,configuration):
    t = timeClass(log,'getFileListInteresClient')
    log.info( 'inicio de getFileListInteresClient' + file_name_class+'',True,True)
    try:
        clients_json = []
        clients = []
        with open("FileProcess/driver_interes_client.json", "r", encoding='utf8') as f:
            clients_json = json.loads(f.read())
        
        return clients_json
        log.warning( 'Archivo de getFileListInteresClient creado correctamente!!!!' + file_name_class+' ',True,True,t.end())
    except Exception as e :
        log.error( 'Problemas al obtener el getFileListInteresClient'+file_name_class+' ',True,True)

def setFileListExceptionsClient(log, configuration):
    t = timeClass(log, 'setFileListExceptionsClien')
    log.info('inicio de setFileListExceptionsClien' +file_name_class+'', True, True)
    try:
        dr = driverClass(log)
        data = dr.configClinet(
            configuration['SHEET_ID'], configuration['SHEET_EXCEPTIONS_INI'],
            configuration['SHEET_EXCEPTIONS_TITTLE'], configuration['SHEET_EXCEPTIONS_DATA'], configuration['SHEET_EXCEPTIONS_INI'])
        # clientPorts : List[clientPort] = JsonToObject(data, List[clientPort])
        with open('FileProcess/driver_exceptions_client.json', 'w', encoding='utf8') as json_file:
            json.dump(data, json_file)
        log.warning('Archivo de setFileListExceptionsClient creado correctamente!!!!' +
                    file_name_class+' ', True, True, t.end())
    except Exception as e:
        log.error('Problemas al guardar el setFileListExceptionsClient' +file_name_class+' ', True, True)

def getFileListExceptionsClient(log, configuration):
    t = timeClass(log, 'setFileListExceptionsClient')
    log.info('inicio de setFileListExceptionsClient' +file_name_class+'', True, True)
    try:
        clients_json = []
        clients = []
        with open("FileProcess/driver_exceptions_client.json", "r", encoding='utf8') as f:
            clients_json = json.loads(f.read())

        return clients_json
        log.warning('Archivo de getFileListExceptionsClient creado correctamente!!!!' +
                    file_name_class+' ', True, True, t.end())
    except Exception as e:
        log.error('Problemas al obtener el getFileListExceptionsClient' +file_name_class+' ', True, True)

def setFileListInteresCompuesto(log,configuration):
    t = timeClass(log,'setFileListInteresCompuesto')
    log.info( 'inicio de setFileListInteresCompuesto' + file_name_class+'',True,True)
    try:
        dr = driverClass(log)
        data = dr.configClinet(configuration['SHEET_ID'] , configuration['SHEET_INTERES_COMPUESTO_INI'],configuration['SHEET_INTERES_COMPUESTO_TITTLE'],configuration['SHEET_INTERES_COMPUESTO_DATA'] ,configuration['SHEET_INTERES_COMPUESTO_INI'])
        # clientPorts : List[clientPort] = JsonToObject(data, List[clientPort])
        with open('FileProcess/driver_interes_compuesto.json', 'w', encoding='utf8') as json_file:
            json.dump(data, json_file)
        log.warning( 'Archivo de setFileListInteresCompuesto creado correctamente!!!!' + file_name_class+' ',True,True,t.end())
    except Exception as e :
        log.error( 'Problemas al guardar el setFileListInteresCompuesto'+file_name_class+' ',True,True)

def getFileListExceptionsInteresCompuesto(log, configuration):
    t = timeClass(log, 'getFileListExceptionsInteresCompuesto')
    log.info('inicio de getFileListExceptionsInteresCompuesto' +file_name_class+'', True, True)
    try:
        clients_json = []
        clients = []
        with open("FileProcess/driver_interes_compuesto.json", "r", encoding='utf8') as f:
            clients_json = json.loads(f.read())

        return clients_json
        log.warning('Archivo de getFileListExceptionsClient creado correctamente!!!!' +
                    file_name_class+' ', True, True, t.end())
    except Exception as e:
        log.error('Problemas al obtener el getFileListExceptionsInteresCompuesto' +file_name_class+' ', True, True)

"""
**************************************************************************************************************
"""
def getQueryForClient(log, configuration):
    a = []
    finalData = []
    t = timeClass(log, 'getQueryForClient')
    log.info('inicio de getQueryForClient' +file_name_class+'', True, True)
    query_json = getFileListQuerysClient(log,configuration)
    query_temp: List[Query] = JsonToObject(query_json, List[Query])
    querys : client = []
    for query_ini in query_temp: 
        try:
            if int(query_ini.client_id) in  configuration['clients'] and int(query_ini.server_id) ==  configuration['server_id'] :
                a = query_ini.querys.split(', ')
                for data in a:
                    finalData.append(data)
        except Exception as e:
           log.info('getShForClient no existe cliente client :' +str(query_ini.client_id), True, True)
        

    accountIDS = ""
    for item in np.unique(finalData).tolist():
        if item != "":
            if accountIDS == "":
                accountIDS = item
            else:
                accountIDS = accountIDS +", " + item
    return accountIDS
#Funciones para administrar la hojas de los Sh por cliente
def getShForClient(log,configuration):
    t = timeClass(log, 'getShForClient')
    log.info('inicio de getShForClient' +file_name_class+'', True, True)
    clients_json = getFileListClient(log,configuration)
    clients_temp: List[client] = JsonToObject(clients_json, List[client])
    clients : client = []
    for client_ini in clients_temp: 
        try:
            if int(client_ini.client_id) in  configuration['clients']:
            # if configuration['clients'].index(int(client_ini.client_id)) >= 0 :
                if (client_ini.active == '1' or client_ini.active == True):
                    clients.append(client_ini)
        except Exception as e:
            log.info('getShForClient no existe cliente client :' +str(client_ini.client_id), True, True)
    a = []
    for clie in clients:
        data = idshForClient(log,clie,configuration)
        a.extend(data)
    accountIDS = ""
    for item in np.unique(a).tolist():
        if item != "":
            if accountIDS == "":
                accountIDS = item
            else:
                accountIDS = accountIDS +", " + item
    return accountIDS
"""
Funciones para administrar la hojas de los clientes
"""
def idshForClient(log,client,configuration):
    data_gn = []
    if bool(client.general_sh):
        data_gn = getFileListShGeneral(log,configuration)
    data_shs = getFileListShClient(log,configuration)
    list_data_sh = []
    for data_sh in data_gn:
        if data_sh['pais_id'] == client.pais_id:
            list_data_sh.append(data_sh['account_id'])
    for data_sh in data_shs:
        if int(client.client_id) == int(data_sh['client_id']):
            list_data_sh.append(data_sh['account_id'])
    return np.unique(list_data_sh).tolist()
    
"""
**************************************************************************************************************
"""

#Función para crear todos los archivos de Clientes, Sh, Palabras de Interes y Palabras Excepción
def createFilesProgram(log,configuration):
    createFileInterestMonibotWords(log,configuration)
    createFileExceptionsMonibotWords(log, configuration)
    createFileAlias(log,configuration)
    createFileChannel_by_stakeholder(log,configuration)
    createFileChannel_by_stakeholder(log,configuration,'facebook')
    createFilePort_by_client(log,configuration)
    createFileInteresCompuesto(log,configuration)

#Funcion que crear el archivo de intereses Compuestos
def createFileInteresCompuesto(log,configuration):
    Interes = []

    #Obtenermos el interes compuesto
    data_interes_compuesto = getFileListExceptionsInteresCompuesto(log , configuration)
    #Obtenemos la data de lo clientes
    clients_json = getFileListClient(log , configuration)
    #Obtenemos la data de los intereses
    Interes_Cliente = getFileListInteresClient(log , configuration)
    cont = 0
    data_interes_compuesto_temp : List[interes_compuesto_client] = JsonToObject(data_interes_compuesto, List[interes_compuesto_client]) 
    for data_int in data_interes_compuesto_temp:
        interes_uno = []
        interes_dos = []
        for item in Interes_Cliente:
            if(item['client_id'] == data_int.cliente_id):
                if (data_int.interes1 == item['nombre']):
                    interes_uno.append(item)
                elif (data_int.interes2 == item['nombre']):
                    interes_dos.append(item)    
                else:
                    print("No hay interes")

        for i in interes_uno:
            wordInteres = i['interes'].split(',')
            for wordUni in wordInteres:
                ns = interes_compuesto_client()
                data= [i['client_id'] , i['tipo'] , i['nombre'] , wordUni , "Interes1" , cont ]
                ns.addInteres(data)
                Interes.append(ns)
        if (data_int.interes2 == "" and interes_uno != []):
            ns = interes_compuesto_client()
            data= [ interes_uno[0]["client_id"] , "Informativo" , "None" , "None" , "Interes2" , cont ]
            ns.addInteres(data)
            Interes.append(ns)
        else:
            for i in interes_dos:
                wordInteres = i['interes'].split(',')
                for wordUni in wordInteres:
                    ns = interes_compuesto_client()
                    data= [i['client_id'] , i['tipo'] , i['nombre'] , wordUni , "Interes2" , cont ]
                    ns.addInteres(data)
                    Interes.append(ns)
        cont += 1
    alisJson  = ObjectToJson(Interes)
    dict = {"Code": "true", "Message": "OK", "word": alisJson}
    with open('FileProcess/Modelo_InteresCompuestosWords.json', 'w') as json_file:
        json.dump(dict, json_file)
        
#Funcion que crear el archvio de intereses
def createFileInterestMonibotWords(log,configuration):
    Interes = []
    data_interes = getFileListInteresClient(log,configuration)
    data_interes_temp: List[interes_client] = JsonToObject(data_interes, List[interes_client])
    for data_int in data_interes_temp:
        dataInteresuni = data_int.interes.split(",")
        for int_un in dataInteresuni:
            ns = InteresMonibot()
            ns.addInteres(data_int,int_un)
            Interes.append(ns)
    # alisJson  = json.loads(ObjectToJson(Interes))
    alisJson  = ObjectToJson(Interes)
    dict = {"Code": "true", "Message": "OK", "words": alisJson}  
    with open('FileProcess/Modelo_interestMonibotWords.json', 'w') as json_file:   
        json.dump(dict, json_file)
#Funcion que crear el archvio de aliasSH
def createFileAlias(log,configuration):
    alias = []
    data_shs = getFileListShClient(log,configuration)
    data_shs_temp: List[stakeholder] = JsonToObject(data_shs, List[stakeholder])
    for data_sh in data_shs_temp:
        try:
            if configuration['clients'].index(int(data_sh.client_id)) >= 0 :
                ns = NicknameSH()
                if data_sh.tw != '' and data_sh.tw != 'N/A':
                    if data_sh.tw.find("@") >= 0:
                        data_sh.alias = data_sh.tw+","+data_sh.tw.strip('@')+","+data_sh.alias
                    else:
                        data_sh.alias = "@"+data_sh.tw+","+data_sh.tw+","+data_sh.alias
                
                ns.addAlias(data_sh)
                alias.append(ns)
        except Exception as e:
            log.info('createFileAlias no existe cliente client :' +str(data_sh.tw), True, True)
    alisJson  = ObjectToJson(alias)
    dict = {"Code": "true", "Message": "OK", "alias": alisJson}
        
    with open('FileProcess/Modelo_aliasSH.json', 'w') as json_file:   
        json.dump(dict, json_file)
#Funcion que crear el archvio de Channel_by_stakeholder
def createFileChannel_by_stakeholder(log,configuration, type_social = 'twitter'):
    sh = []
    ## Trae los clientes en forma de objeto 
    clients_json = getFileListClient(log,configuration)
    clients_temp: List[client] = JsonToObject(clients_json, List[client])
  
    ##  trae stackeholders Comunes en forma de objeto 
    data_gn = getFileListShGeneral(log,configuration)
    data_gn_temp: List[stakeholder_general] = JsonToObject(data_gn, List[stakeholder_general])
    
    ## trae Stackeholders en forma de objeto 
    data_shs = getFileListShClient(log,configuration)
    data_shs_temp: List[stakeholder] = JsonToObject(data_shs, List[stakeholder])


    for client_ini in clients_temp:
        if (client_ini.general_sh == '1' or client_ini.general_sh == True) and (client_ini.active == '1' or client_ini.active == True):
            for sh_general in data_gn_temp:
                if sh_general.pais_id  == client_ini.pais_id:
                    sh_class = channel_by_stakeholder()  
                    sh_class.addGeneral(sh_general,client_ini, type_social)
                    if type_social == 'facebook':
                       if sh_class.account != '':  
                            pass
                            #sh.append(sh_class)
                    else:
                        sh.append(sh_class)

    for sh_tem in data_shs_temp:
        sh_class = channel_by_stakeholder()
        for client_ini in clients_temp:
            if int(client_ini.client_id) == int(sh_tem.client_id) and (client_ini.active == "1" or client_ini.active == True):                
                if sh_tem.tipo.upper() == 'Total'.upper():
                    pass
                    # print(f"sh total {sh_tem.tw} client {sh_tem.client_id}")
                sh_class.addSh(sh_tem,client_ini, type_social)
                if type_social == 'facebook'  and sh_tem.fb != '':
                    if sh_class.account != '':
                        sh.append(sh_class)
                else:
                    sh.append(sh_class)
                break
    alisJson = ObjectToJson(sh)
    dict = {"Code": "true", "Message": "OK", "sh": alisJson}

    if type_social == 'twitter':    
        with open('FileProcess/Modelo_Channel_by_stakeholder.json', 'w') as json_file:   
            json.dump(dict, json_file)  
    if type_social == 'facebook':
        with open('FileProcess/Modelo_Channel_by_stakeholder_facebook.json', 'w') as json_file:   
            json.dump(dict, json_file)

#Funcion que crear el archvio de port_by_client 
def createFilePort_by_client(log,configuration):
    clients = []
    clients_json = getFileListClient(log,configuration)
    clients_temp: List[client] = JsonToObject(clients_json, List[client])
    for client_ini in clients_temp:
        try:
            if configuration['clients'].index(int(client_ini.client_id)) >= 0 :
                cp = clientPort()
                cp.set_data(client_ini)
                clients.append(cp)
        except Exception as e:
            pass
    for client_ini in clients_temp:
        try:
            if configuration['clients_director'].index(int(client_ini.client_id)) >= 0 :
                cp = clientPort()
                cp.set_data(client_ini)
                clients.append(cp)
        except Exception as e:
            pass
    # np.unique(a).tolist()
    # Usage
    # If you want most recent name to win, just sort by timestamp first
    clienteOrdenado = OrdenarjsonPorKey(ObjectToJson(clients),'name')

    # Remove everything with a duplicate value for key 'client_id'
    alisJson = UnicoJson(clienteOrdenado, 'client_id')

    # alisJson = ObjectToJson(clients)
    dict = {"Code": "true", "Message": "OK", "port": alisJson}

    with open('FileProcess/Modelo_port_by_client.json', 'w') as json_file:   
        json.dump(dict, json_file)         
#Funcion que crear el archvio de exceptionsMonibotWords 
def createFileExceptionsMonibotWords(log, configuration):
    Exceptions = []
    data_exceptions = getFileListExceptionsClient(log, configuration)
    data_exceptions_temp: List[exceptions_client] = JsonToObject(
        data_exceptions, List[exceptions_client])

    for data_int in data_exceptions_temp:
        dataExceptionsuni = data_int.exceptions.split(",")
        for int_un in dataExceptionsuni:
            ns = ExceptionsMonibot()
            ns.addExceptions(data_int, int_un)
            Exceptions.append(ns)
    alisJson = ObjectToJson(Exceptions)
    dict = {"Code": "true", "Message": "OK", "words": alisJson}

    with open('FileProcess/Modelo_exceptionsMonibotWords.json', 'w') as json_file:
        json.dump(dict, json_file)        

