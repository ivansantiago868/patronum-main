import json
import pyodbc
from typing import List
from Entity.Publics import channel_by_stakeholder, MonibotTelegram, stakeholder, clientPort,stakeholderAccount_id, search_result
from Utilities.utils import JsonToObject, cargaConfig ,ObjectToJson,formatStr#, getSamesItem, ObjectToJson


#Clase de suntzu
class SuntzuBd(object):
    server : str 
    database: str 
    username : str  
    password : str 
    conn = None
    log = None

    def __init__(self,log):
        try:
            self.log = log
            configuration = cargaConfig(log)
            self.server = 'tcp:'+configuration["suntzu_url"]
            self.username = configuration["suntzu_user"] 
            self.password = configuration["suntzu_pass"] 
            self.database = configuration["suntzu_bd"] 
            self.conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+self.server+';DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password)
            self.cursor = self.conn.cursor()
            self.status = True
        except Exception as e:
            self.status = False
            self.log.error("Error=>SuntzuBd en getListMonibotTelegram => %s" % (e),True,True)
    #Método para obtener los puertos de los cliente 
    def getPortByClints(self):
        json1 = json.loads('[{"port":11012,"client_id":12,"active":true,"name":"client12"},{"port":11013,"client_id":13,"active":true,"name":"client13"},{"port":11015,"client_id":15,"active":true,"name":"client15"},{"port":11020,"client_id":20,"active":true,"name":"client20"},{"port":11071,"client_id":71,"active":true,"name":"client71"},{"port":11125,"client_id":125,"active":true,"name":"client125"},{"port":11134,"client_id":134,"active":true,"name":"client134"},{"port":11136,"client_id":136,"active":true,"name":"client136"},{"port":11137,"client_id":137,"active":true,"name":"client137"},{"port":11138,"client_id":138,"active":true,"name":"client138"},{"port":11140,"client_id":140,"active":true,"name":"client140"},{"port":11176,"client_id":176,"active":true,"name":"client176"},{"port":11178,"client_id":178,"active":true,"name":"client178"},{"port":11181,"client_id":181,"active":true,"name":"client181"},{"port":11185,"client_id":185,"active":true,"name":"client185"},{"port":11186,"client_id":186,"active":true,"name":"client186"},{"port":11187,"client_id":187,"active":true,"name":"client187"}]')
        clientPorts : List[clientPort] = JsonToObject(json1, List[clientPort])
        return clientPorts
    #Método para obtener los Sh por clientes guardados en  Suntzu
    def getStakeholderByClient(self,clients):
        try:
            channel_by_stakeholders : List[channel_by_stakeholder]
            selectActive = ''
            clientList  = ",".join([str(_) for _ in clients])
            for target_list in clients:
                selectActive += "(select fact_stakeholder.stakeholder_id collate SQL_Latin1_General_CP1_CI_AS FROM fact_stakeholder INNER JOIN stakeholder ON stakeholder.id = fact_stakeholder.stakeholder_id collate SQL_Latin1_General_CP1_CI_AS WHERE fact_stakeholder.client_id = "+str(target_list)+"  and fact_stakeholder.active = 1 and stakeholder.is_internal = 1) union "

            # query = "select * from ( select id,stakeholder_id,name,account,account_id,channel_name,channel_id,client_id,search_id from ( select min(id) id1 from monibot_stakeholders group by account) as a  inner join monibot_stakeholders ms on ms.id = a.id1) f WHERE client_id IN ("+clientList+") AND client_id IS NOT NULL AND stakeholder_id IS NOT NULL and not stakeholder_id in ("+selectActive[0:-6]+")"
            query = "select DISTINCT account_id from monibot_stakeholders"
            self.cursor.execute(query)
            rows  =  self.cursor.fetchall()
            data = []
            if len(rows) > 0:
                num_fields = len(self.cursor.description)
                field_names = [i[0] for i in self.cursor.description]
                for row in rows:
                    objectRow = {}
                    cont = 0
                    while cont < num_fields:
                        objectRow[field_names[cont]] = row[cont]
                        cont += 1
                    data.append(objectRow) 
            stakeholders : List[stakeholderAccount_id] = JsonToObject(data, List[stakeholderAccount_id])
            return stakeholders
        except Exception as e:
            self.log.error("Error=>SuntzuBd en getStakeholderByClient => %s" % (e),True,True)
    #Método para obtener los canales por SH guardados en  Suntzu
    def getChannel_by_stakeholder(self):
        try:
            channel_by_stakeholders : List[channel_by_stakeholder]
            # query = "select min(id) id,min(name) name,min(account) account,account_id,min(channel_name) channel_name,min(channel_id) channel_id,client_id ,min(search_id) search_id  from channel_by_stakeholder group by client_id,account_id"
            query = " select min(id) id,min(name) name,min(account) account,account_id,min(channel_name) channel_name,min(channel_id) channel_id,client_id,min(search_id) search_id from ( select * from channel_by_stakeholder union  select id,name,account,account_id,channel_name,channel_id,client_id,search_id from monibot_stakeholders ) as d group by client_id,account_id"
            self.cursor.execute(query)
            rows  =  self.cursor.fetchall()
            data = []
            if len(rows) > 0:
                num_fields = len(self.cursor.description)
                field_names = [i[0] for i in self.cursor.description]
                for row in rows:
                    objectRow = {}
                    cont = 0
                    while cont < num_fields:
                        objectRow[field_names[cont]] = row[cont]
                        cont += 1
                    data.append(objectRow) 
            channel_by_stakeholders : List[channel_by_stakeholder] = JsonToObject(data, List[channel_by_stakeholder])
            return channel_by_stakeholders
        except Exception as e:
            self.log.error("Error=>SuntzuBd en getChannel_by_stakeholder => %s" % (e),True,True)

    #Método para guardar los tweets en Suntzu
    def setSaveTwitter(self,twitter):
        try:
            nameList = []
            valueList = []
            json_data = ObjectToJson(twitter)
            for key in json_data:
                value = json_data[key]
                nameList.append(key)
                if type(value) == str:
                    valueList.append("'"+formatStr(value)+"'") 
                else:
                    if type(value) == int:
                        valueList.append(str(value)) 
                    else:
                        valueList.append(str(value))   
            nameStr =  ",".join(nameList)
            valuStr =  ",".join(valueList)
            self.cursor.execute('INSERT INTO dbo.search_result ('+ nameStr +') VALUES ('+valuStr+')') 
            #self.cursor.execute("insert into products(id, name) values (?, ?)", 'pyodbc', 'awesome library')
            self.conn.commit()
        except Exception as e:
            self.log.error("Error=>SuntzuBd en setSaveTwitter => %s" % (e),True,True)
    def __del__(self):
        self.log.info("LOG=>SuntzuBd en __del__ => ",True,True)
        #self.conn.close()
        #del self.cursor
    def end(self):
        self.conn.close()
        del self.cursor
    
    #Método para obtener los telegrams del cliente
    def getListMonibotTelegram(self,client_id):
        try:
            MonibotTelegramList : List[MonibotTelegram]
            self.cursor.execute('SELECT [id_group],[client_id],[name_chat],[id_channel],[status],[id] FROM [dbo].[monibot_telegram] where client_id =  '+str(client_id))
            rows  =  self.cursor.fetchall()
            data = []
            if len(rows) > 0:
                num_fields = len(self.cursor.description)
                field_names = [i[0] for i in self.cursor.description]
                for row in rows:
                    objectRow = {}
                    cont = 0
                    while cont < num_fields:
                        objectRow[field_names[cont]] = row[cont]
                        cont += 1
                    data.append(objectRow) 
            MonibotTelegrams : List[MonibotTelegram] = JsonToObject(data, List[MonibotTelegram])
            return MonibotTelegrams
        except Exception as e:
            self.log.error("Error=>SuntzuBd en getListMonibotTelegram => %s" % (e),True,True)

    def getIDTweet(self):
        try:
            self.cursor.execute("SELECT [provider_item_id] FROM [Suntzu].[dbo].[search_result] WHERE  CAST(created_at AS DATE)= CONVERT (DATE, SYSDATETIME()) AND [likes_count] IS NULL AND [retweets_count] IS NULL")
            rows = self.cursor.fetchall()
            data = []
            if len(rows) > 0:
                num_fields = len(self.cursor.description)
                field_names = [i[0] for i in self.cursor.description]
                for row in rows:
                    objectRow = {}
                    cont = 0
                    while cont < num_fields:
                        objectRow[field_names[cont]] = row[cont]
                        cont += 1
                    data.append(objectRow) 
            search_results : List[search_result] = JsonToObject(data, List[search_result])
            return search_results
        except Exception as e:
            self.log.error("Error=>SuntzuBd en getIDTweet => %s" % (e),True,True)



    def setTweetsCounter(self, id_tweet, rt_counter, likes_counter):
        try:            
            self.cursor.execute(f"UPDATE [Suntzu].[dbo].[search_result] SET [Likes_counter] = {str(likes_counter)}, [retweets_counter] = {str(rt_counter)} WHERE [provider_item_id] ={str(id_tweet)}")
            self.conn.commit()

        except Exception as e:
            self.log.error("Error=>SuntzuBd en setTweetsCounter => %s" % (e),True,True)





    # def saveAlerts(self, tweet):

    #     columns = 'provider_item_id, provider_id, search_id, name, created_at, profile_image_url, screen_name, engine, created_at_default_time, created_at_local, created_at_ultime, created_at_time_zone, sts_text, position, attitude, enviroment'
        

    #     for items in tweet["user"]["name_screen"]:
    #         namescreen = items

    #         for items in tweet["user"]["profile_image_url"]:
    #             profile_image_url = items

    #             for items in tweet["text"]:
    #                 text = items

    #                 query = f"INSERT INTO search_resultAlert ({columns}) VALUES (\'1229948254789554176\', \'Twitter\', \'hydra2066\', \'{name}\', GETDATE(), \'{profile_image_url}\', \'{names}\',
    #                 \'Twitter\', \'UTC\', GETDATE(), \'0\', \'Mexico/General\', {text}, \'0\', \'125\', \'Informativo\', \'DEV\'"

    #                 self.cursor.execute(query)





    # def getChannel_by_stakeholderForName(self,sh):
    #     #sh = 'Christi88924980'
    #     try:
    #         channel_by_stakeholders : List[channel_by_stakeholder]
    #         self.cursor.execute("select * from channel_by_stakeholder where UPPER(account) = UPPER('"+sh+"') or UPPER(account) = UPPER('@"+sh+"') ")
    #         rows  =  self.cursor.fetchall()
    #         data = []
    #         if len(rows) > 0:
    #             num_fields = len(self.cursor.description)
    #             field_names = [i[0] for i in self.cursor.description]
    #             for row in rows:
    #                 objectRow = {}
    #                 cont = 0
    #                 while cont < num_fields:
    #                     objectRow[field_names[cont]] = row[cont]
    #                     cont += 1
    #                 data.append(objectRow) 
    #         channel_by_stakeholders : List[channel_by_stakeholder] = JsonToObject(data, List[channel_by_stakeholder])
    #         return channel_by_stakeholders
    #     except Exception as e:
    #         self.log.error("Error=>SuntzuBd en getChannel_by_stakeholder => %s" % (e),True,True)