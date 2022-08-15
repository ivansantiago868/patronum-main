from __future__ import print_function
from subprocess import Popen, PIPE, CalledProcessError
from csv import writer
import csv
import time
import twarc

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pprint import pprint
from googleapiclient import discovery
from Utilities.utils import cargaConfig
from Utilities.log import log_file
from Utilities.drive  import driverClass


log = log_file("C:\Log\Stream\StreamFile.log")     
configuration = cargaConfig(log)
log.log_File=configuration['log']

def main():
    dr = driverClass(log)
    id_position = 0
    user_position = 0
    datos_csv = []
    User_names = []
    data_extract = []
    # Es el nombre del archivo a checar

    file_name = '\\Users\\Santiago\\Downloads\\(QA) Stakeholder Manager - Stakeholders.csv'

    # El archivo que se creara con los nuevos resultados
    my_file = '\\Users\\Santiago\\Downloads\\(QA) Stakeholder Manager - Stakeholders-.csv'


    data_extract = extract_data_docs()
    id_position = position_id(id_position, data_extract)
    user_position = position_username(user_position, data_extract)
    User_names = get_usernames(
        User_names, datos_csv, data_extract, id_position, user_position)
    get_userId(User_names, datos_csv, id_position, user_position)
    data_update(datos_csv)

# Obtiene la posición de la columna donde se guardan los Ids


def position_id(id_position, data_extract):

    for keywords in data_extract[0]:

        if " Id" in keywords:
            id_position += 1
            continue
        elif "Id Cliente" in keywords:
            id_position += 1
            continue
        elif "Id" in keywords:
            return id_position
        id_position += 1


# Obtiene la posición de los Urls o los namescreen
def position_username(user_position, data_extract):

    num = 0
    while user_position is not None:
        for keywords in data_extract[num]:
            if 'https://mobile.twitter.com/' in keywords:
                print(keywords)
                return user_position
            elif 'https://twitter.com/' in keywords:
                print(keywords)
                return user_position
            elif '@' in keywords:
                print(keywords)
                return user_position

            user_position += 1
        user_position = 0
        num += 1

# Obtiene los namescreen  de los usuarios y los guarda en una lista


def get_usernames(User_names, datos_csv, data_extract, id_position, user_position):
    user = ''
    keyword = '/status/'
    results = []

    for row in data_extract:
        datos_csv.append(row)
        if len(row) >= user_position + 1 and len(row) < id_position:
            results.append(row[user_position])
        else:
            continue

    for row in results:

        if not row:
            row = "N/A"
            User_names.append(row)

        elif 'https://twitter.com/' in row:
            # Quita todo lo que no sea el userscreen
            row = row.replace('https://twitter.com/', "")
            last_char = row.index(keyword) + len(keyword)
            row = row[:last_char - 8]
            User_names.append(row)

        elif 'https://mobile.twitter.com/' in row:
            row = row.replace('https://mobile.twitter.com/', "")
            last_char = row.index(keyword) + len(keyword)
            user = row[:last_char - 8]
            User_names.append(row)

        elif '@' in row:
            row = row.replace('@', "")

            if "\u200f" in row:
                row = row.replace("\u200f", "")
                user = row
                User_names.append(user)
            else:
                user = row
                User_names.append(user)

    return User_names

# Obtine los UserId de los usuarios guardados en la lista User_names


def get_userId(User_names, datos_csv, id_position, user_position):

    keyword = ", \"id_str\":"
    User = ''

    for row in User_names:
        User = row
        twitter = 'https://twitter.com/' + User + "/status/"
        mobile = "https://mobile.twitter.com/" + User + "/status/"
        User_search = "@" + User
        if "N/A" in User:
            id_user = " "
            info = "NameScreen: " + User + " id: " + id_user
            print(info)

        else:

            # Guarda todo lo que se imprima en la terminal, resultante del comando
            capture = Popen(f"twarc users {User} ", stdout=PIPE)
            for line in capture.stdout:
                id_user = line.decode("utf-8").replace("{\"id\": ", "")

                if keyword in id_user:
                    last_char = id_user.index(keyword) + len(keyword)
                    id_user = str(id_user[:last_char - 11])
                    info = "NameScreen: " + User + " id: " + id_user
                    print(info)

                for row in datos_csv:

                    # Busca el userscreen el csv y checa si ya esta escrito id o no
                    if len(row) == user_position + 1 and len(row) < id_position + 1 and User_search in row[user_position]:
                        if len(row) == user_position + 1 or len(row) < id_position + 1:
                            while (len(row) != id_position + 1):
                                row.insert(user_position + 1, '')
                            row[id_position] = id_user
                            break

                        elif len(row) == id_position + 1:
                            row[id_position] = id_user
                            break

                    elif len(row) == user_position + 1 and len(row) < id_position + 1 and twitter in row[user_position]:
                        if len(row) == user_position + 1 or len(row) < id_position + 1:
                            while (len(row) != id_position + 1):
                                row.insert(user_position + 1, '')
                            row[id_position] = id_user
                            break

                        elif len(row) == id_position + 1:
                            row[id_position] = id_user
                            break

                    elif len(row) == user_position + 1 and len(row) < id_position + 1 and mobile in row[user_position]:
                        if len(row) == user_position + 1 or len(row) < id_position + 1:
                            while (len(row) != id_position + 1):
                                row.insert(user_position + 1, '')
                            row[id_position] = id_user
                            break

                        elif len(row) == id_position + 1:
                            row[id_position] = id_user
                            break

            if not id_user:
                id_user = ""
                info = "NameScreen: " + User + " id: " + id_user
                print(info)

                for row in datos_csv:

                    # Busca el userscreen el csv y checa si ya esta escrito id o no
                    if len(row) == user_position + 1 and len(row) < id_position + 1 and User_search in row[user_position]:
                        if len(row) == user_position + 1 or len(row) < id_position + 1:
                            while (len(row) != id_position + 1):
                                row.insert(user_position + 1, '')
                            row[id_position] = id_user
                            break

                        elif len(row) == id_position + 1:
                            row[id_position] = id_user
                            break

                    elif len(row) == user_position + 1 and len(row) < id_position + 1 and twitter in row[user_position]:
                        if len(row) == user_position + 1 or len(row) < id_position + 1:
                            while (len(row) != id_position + 1):
                                row.insert(user_position + 1, '')
                            row[id_position] = id_user
                            break

                        elif len(row) == id_position + 1:
                            row[id_position] = id_user
                            break

                    elif len(row) == user_position + 1 and len(row) < id_position + 1 and mobile in row[user_position]:
                        if len(row) == user_position + 1 or len(row) < id_position + 1:
                            while (len(row) != id_position + 1):
                                row.insert(user_position + 1, '')
                            row[id_position] = id_user
                            break

                        elif len(row) == id_position + 1:
                            row[id_position] = id_user
                            break

            id_user = ""


def data_update(datos_csv):  # Hace update de la informacion de la hoja
    with open('token.pickle', 'rb') as token:
        cred = pickle.load(token)

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    service = discovery.build('sheets', 'v4', credentials=cred)
    spreadsheet_id = '11gTiPjWTnAG3Wp6aFbsRpawIDbe7v1Pwjt80t2ohqco'
    range_ = "A1"
    value_input_option = 'RAW'
    values_ = datos_csv

    value_range_body = {
        "majorDimension": "ROWS",
        "range": range_,
        "values": values_
    }

    request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id,
                                                     range=range_, valueInputOption=value_input_option, body=value_range_body)
    response = request.execute()

# Extrae la informacion de la hoja de google


def extract_data_docs():

    # Son los permisos que estas pidiendo
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    SAMPLE_SPREADSHEET_ID = '11gTiPjWTnAG3Wp6aFbsRpawIDbe7v1Pwjt80t2ohqco'

    # Nombre de la hoja
    SAMPLE_RANGE_NAME = 'Monibot no enviados - PJ'

    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'C:\\Users\\Santiago\\Documents\\Gotet.Twitter.Stream\\Config\\credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    rows = result.get('values', [])
    return rows


main()
