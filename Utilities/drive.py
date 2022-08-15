from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle
import json
from Entity.Publics import relation
from Utilities.utils import JsonToObject
from typing import List

class driverClass:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    def __init__(self, log):
        self.creds = None
        self.log = log
        if os.path.exists('Config/token.pickle'):
            with open('Config/token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                self.flow = InstalledAppFlow.from_client_secrets_file(
                    'Config/credentials.json', self.SCOPES)
                self.creds = self.flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('Config/token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('sheets', 'v4', credentials=self.creds, cache_discovery=False)
        self.relations = self.GetRelations()
    def configClinet(self,SAMPLE_SPREADSHEET_ID,SAMPLE_RANGE_NAME,SAMPLE_RANGE_TITTLE,SAMPLE_RANGE_DATA,RELATION):
        # Call the Sheets API
        try:
            sheet = self.service.spreadsheets()
            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range=SAMPLE_RANGE_NAME+"!"+SAMPLE_RANGE_TITTLE).execute()
            valuesTittle = result.get('values', [])

            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range=SAMPLE_RANGE_NAME+"!"+SAMPLE_RANGE_DATA).execute()
            valuesData = result.get('values', [])
        except Exception as e:
            print(str(e))

        data = []
        if not valuesData:
            self.log.info("No data found.")
        else:
            for row in valuesData:
                # Print columns A and E, which correspond to indices 0 and 4.
                count = 0
                dict1 = {}
                try:
                    for row_tittle in valuesTittle[0]:
                        d = {}
                        try:
                            value = row[count]
                        except IndexError as e:
                            value = ''
                        except Exception as e:
                            pass
                        value = value.replace("\u200f", "").rstrip()
                        d[self.GetTittle(row_tittle.lower(),RELATION)] = self.GetValue(row_tittle.lower(),RELATION,value)
                        dict1.update( d )
                        count += 1 
                    data.append(dict1)
                except Exception as e:
                    self.log.info("Registro falta info.")
        return data
    def SetDataUpdate(self,SAMPLE_SPREADSHEET_ID ,serverID,posicion,valueData):
        abc=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        sheet = self.service.spreadsheets()
        values = {'values':[[valueData,],]}
        celda = abc[posicion]+str(serverID+1)
        result = self.service.spreadsheets().values().update(
            spreadsheetId=SAMPLE_SPREADSHEET_ID, 
            range="Servers!"+celda,
            valueInputOption='RAW',
            body=values
        ).execute()
        return celda
    def SetData(self,SAMPLE_SPREADSHEET_ID):
        sheet = self.service.spreadsheets()
        values = {'values':[['Hello Saturn',],]}
        result = self.service.spreadsheets().values().append(
            spreadsheetId=SAMPLE_SPREADSHEET_ID, 
            range="A1",
            valueInputOption='RAW',
            body=values
        ).execute()
    def GetRelations(self):
        try:
            with open("Config/relation.json", "r") as f: 
                relati = json.loads(f.read())
            relations : List[relation] = JsonToObject(relati, List[relation])
            return relations
        except Exception as e:
            return []
        
    def GetTittle(self,name,hoja):
        for target_list in self.relations:
            if target_list.name.lower() == name.lower()  and target_list.hoja.lower() == hoja.lower():
                return target_list.objeto.lower()
    def GetValue(self,name,hoja,value):
        for target_list in self.relations:
            if target_list.name.lower() == name.lower()  and target_list.hoja.lower() == hoja.lower():
                if target_list.type == "int":
                    return int(value)
                if target_list.type == "string":
                    return value
                if target_list.type == "json":
                    return json.loads(value)
                if target_list.type == "bool":
                    if (value.lower() == "true" or value.lower() == '1'):
                        value = True
                    else:
                        value = False
                    return value
                if target_list.type == "list":
                    Client = []
                    if value != '':  
                        for client_list in value.split(" "):
                            Client.append(int(client_list))    
                    return Client
                