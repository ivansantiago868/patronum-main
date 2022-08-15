from typing import List
from Entity.Publics import relation
from Utilities.drive import driverClass
import json
import os
from Controller.DriveControler import mappingConfig
from Utilities.log import log_file
from Utilities.utils import JsonToObject, cargaConfig, cargaConfigIni

log = log_file("C:\Log\Stream\StreamConfig.log")

configurationInicio = cargaConfigIni(log)
config = cargaConfig(log)

def createConfig(Config):
    try:
        RelacionJson = []
        ConfigSaveIni = {}
        
        for item in Config['Servers'][0]:
            value = Config['Servers'][0][item]
            # try:
            #     value = int(Config['Servers'][0][item])
            # except Exception as e:
            #     if Config['Servers'][0][item].lower() == "true" or Config['Servers'][0][item].lower() == "false":
            #         if (Config['Servers'][0][item].lower() == "true"):
            #             value = True
            #         else:
            #             value = False
            #     else:
            #         if ' ' in value:
            #             Client = []
            #             for client_list in value.split(" "):
            #                 Client.append(int(client_list))    
            #             value =  Client
            ConfigSaveIni[item] =  value
        ConfigSaveIni['SHEET_ID'] = Config['sheet']
        for item in Config['HojasConfig']:
            ConfigSaveIni['SHEET_'+item['name_config']+"_INI"] =  item['name']
            ConfigSaveIni['SHEET_'+item['name_config']+"_TITTLE"] =  item['tittle']
            ConfigSaveIni['SHEET_'+item['name_config']+"_DATA"] =  item['data']
            for relation_list in item['relation']:
                relation_list['hoja'] = item['name']
                RelacionJson.append(relation_list)
            relations : List[relation] = JsonToObject(RelacionJson, List[relation])
            if item['name'] == 'Clientes':
                try:
                    dr = driverClass(log)
                    dr.relations = relations
                    dataClientActivate = dr.configClinet(ConfigSaveIni['SHEET_ID'],ConfigSaveIni['SHEET_'+item['name_config']+"_INI"],ConfigSaveIni['SHEET_'+item['name_config']+"_TITTLE"],ConfigSaveIni['SHEET_'+item['name_config']+"_DATA"],item['name'])
                    # clientPorts : List[clientPort] = JsonToObject(data, List[clientPort])
                except Exception as e :
                    log.error( 'Problemas al cargar clinetes activos',True,True)
        clientsList = []
        for item in ConfigSaveIni['clients']:
            for item2 in dataClientActivate:
                if item == item2['client_id'] and item2['active']:     
                    clientsList.append(item)
        ConfigSaveIni['clients'] = clientsList
        clients_directorList = []
        for item in ConfigSaveIni['clients_director']:
            for item2 in dataClientActivate:
                if item == item2['client_id'] and item2['active']:     
                    clients_directorList.append(item)
        ConfigSaveIni['clients_director'] = clients_directorList
        for item in Config['BDConfig']:
            ConfigSaveIni[item['name']+"_url"] =  item['ip']
            ConfigSaveIni[item['name']+"_user"] =  item['user']
            ConfigSaveIni[item['name']+"_pass"] =  item['pass']
            ConfigSaveIni[item['name']+"_bd"] =  item['bd']
            ConfigSaveIni[item['name']+"_port"] =  item['port']
        ConfigSaveIni['List_Pais'] = []
        for item in Config['Trends']:
            # {"name":"Mexico","id":23424900,"channel":"-1001474316286","timeTrends":300,"trends_number":10,"sendTop":true,"timeMinutoAlert":0,"trends_number_alert":50}
            tren = item
            ConfigSaveIni['List_Pais'].append(tren)
        ConfigSaveIni['List_Rss'] = [] 
        for item in Config['RSS']:
            tren = item
            ConfigSaveIni['List_Rss'].append(tren)
        folder = 'Config/'
        file_path = os.path.join(folder, 'config.ini')
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        with open('Config/config.ini', 'w+') as json_file:
            json.dump(ConfigSaveIni, json_file)
        file_path = os.path.join(folder, 'relation.json')
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        with open('Config/relation.json', 'w+') as json_file:
            json.dump(RelacionJson, json_file)
        print(ConfigSaveIni)
    except Exception as e:
        log.error(str(e),"main",True,True)

    
def main():
    try:
        Config =  mappingConfig(log,configurationInicio)
                
        createConfig(Config)
    except Exception as e:
        log.error(str(e),"main",True,True)

main()