import json
import time
from http.client import IncompleteRead as http_incompleteRead
from urllib3.exceptions import ProtocolError
from Utilities.utils import cargaConfig
from Utilities.log import log_file
from Entity.SuperMetricsQuery import SuperMetricsQueryClass
from Utilities.mq import mqClass
from datetime import datetime, timedelta
from pytz import timezone


log = log_file("C:\Log\Stream\StreamSuperMetrics.log")   



###############################################################################################
#############################      Facebook Public Data           #############################
###############################################################################################

# Resive Dict de las paginas a analizar, donde la key es la pagina, en la informacion es el 
# numero de posts a extraer y la Frecuencia
# Ejemplo:
# [eltiempo, reforma, etc]

def extractorFacebookAllClients(configuration,listClientsSheet,rangeOfTime,postLimit):
    try:
        channel_by_stakeholders_F = listClientsSheet
        clients = [item for item in channel_by_stakeholders_F if item.account !='' and item.client_id !='' and item.channel_id != '' and 'https' not in item.account]
        listClientsExist,listClientsById, ClientsnotFound = getValidClientsFacebook(clients)
        if listClientsExist != 'limit':
            posts = facebookPostListByPage(listClientsExist,listClientsById,postLimit,rangeOfTime)
            if type(posts) == list:
                print('Posts Recolectados para agregar a la cola: '+str(len(posts)))
                addFacebookPostsToQueue(posts)
            elif posts == 'limit':
                log.warning(' Licence Limit stop extractorFacebookAll ' ,True)
                changeSupermetricsUser()
            elif posts == 'NotFound':
                pass
        else:
            log.warning(' Licence Limit stop extractorFacebookAll ' ,True)


    except  Exception as e:
        log.error(str(e),True,True)

def changeSupermetricsUser():
    pass
def extractorFacebook(configuration,listClientsSheet,rangeOfTime,postLimit):
    if configuration != None:
        try:
            log.warning("Iniciando recolección de posts de los clientes",True)
            channel_by_stakeholders_F = listClientsSheet
            clients = [item for item in channel_by_stakeholders_F if item.account !='' and item.client_id !='' and item.channel_id != '' and 'https' not in item.account]
            log.warning("Comienza Extractor Facebook Clientes :"+ str(len(clients)),True)
           # posts = facebookPostListByPage(clients,[],postLimit,rangeOfTime)
            for client in clients:
                auxclient = [client.account.replace('@','')]
                posts = facebookPostListByPage(auxclient,[],postLimit,rangeOfTime)
                if type(posts) == list:
                    addFacebookPostsToQueue(posts)
                elif posts == 'limit':
                    log.warning(' Licence Limit stop extractorFacebookAll ' ,True)
                    changeSupermetricsUser()
                elif posts == 'NotFound':
                    pass
                 
        except  Exception as e:
            log.error(str(e),True,True)

def getValidClientsFacebook(clients):
    try:
        validUsers = []
        validUsersbyId = dict()
        notUserFound = []
        for client in clients:
            auxclient = [client.account.replace('@','')]
            dataUser = getUserDetailsFacebook(auxclient)
            if dataUser != 'NotFound' and dataUser != 'limit' :
                validUsers.append( dataUser['Username'])
                validUsersbyId[dataUser['Page ID']] = dataUser['Username']
            elif dataUser == 'NotFound':
                notUserFound.append(auxclient)
            elif dataUser == 'limit':
                return 'limit','limit','limit'
        return validUsers, validUsersbyId, notUserFound
    except  Exception as e:
        log.error(str(e),True,True)



def listOfFacebookUsersExist(clients):
    try:
        log.warning("Comienza Clear Cliente P :"+ str(len(clients)),True)
        rangeOfTime = 'last_3_days_inc'
        listNotFound = []
        dictbyClientId = dict()
        listClientsExist = []
        for client in clients:
            auxclient = [client.account.replace('@','')]
            posts = facebookPostListByPage(auxclient,[],1,rangeOfTime)
            if type(posts) == str:
                listNotFound.append(posts)
            else:
                exist = [x for x in listClientsExist if x == [auxclient]]
                if posts == None or posts == []:
                    userDetails = getUserDetailsFacebook(auxclient)
                    dictbyClientId[userDetails['Page ID']] = auxclient
                    listClientsExist.append(auxclient)

                elif posts != None and posts != []:
                    dataUser = json.loads(posts[0])['data']['From user ID']
                    if exist != [] and exist != None:
                        dictbyClientId[dataUser] = auxclient
                    else:
                        listClientsExist.append(auxclient)
                        dictbyClientId[dataUser] = auxclient
        return listClientsExist,dictbyClientId, listNotFound                      
    except Exception as e:
        log.error(str(e),True,True)

def getUserDetailsFacebook(username):
    try:
        configuration = cargaConfig(log)
        supermetrics = SuperMetricsQueryClass()
        supermetrics.ds_id = 'FBPD'
        supermetrics.ds_accounts = username
        supermetrics.ds_user = configuration['user_supermetrics'] 
        supermetrics.data_range_type = 'yesterday'
        supermetrics.fields = ['username','page_id','fan_count','followers_count','talking_about_count','checkins']   
        supermetrics.max_rows = 1
        supermetrics.settings = {'report_type':'Page'}
        supermetrics.api_key = configuration['api_key_supermetrics']
        supermetrics.log = log
        supermetrics.url = configuration['url_supermetrics']
        userDetails,listUsername = supermetrics.startQuery()     
        if userDetails != 'NotFound' and userDetails != 'limit' :
            userdata = userDetails['data']
            headers = userdata[0]
            userdata.pop(0)
            dictUserData = dict(zip(headers,userdata[0])) 
            return dictUserData
        elif userDetails == 'limit':
            # pruebamonitbot@gmail.com api_kuLIK9ro14sxzPcA4ThJH2kBPIBp18I2MkxscWDShObzRQIdkNSTqZRegG19slOEq53Y3dABE2C3uj9xAf1dOpvpAMrTulUuNMSf
            return 'limit'
        elif userDetails == 'NotFound':
            return 'NotFound'

    except  Exception as e:
        log.error(str(e),True,True)
   


def facebookPostListByPage(page,dictClientsById, n_posts, range):
    try:  
        configuration = cargaConfig(log)
        supermetrics = SuperMetricsQueryClass()
        supermetrics.ds_id = 'FBPD'
        supermetrics.ds_accounts = page
        supermetrics.ds_user = configuration['user_supermetrics'] 
        supermetrics.data_range_type = range
        supermetrics.fields = ["post_id","created_time","message","from_name"]
        supermetrics.max_rows = n_posts
        supermetrics.settings = {"report_type":"PagePosts"}
        supermetrics.api_key = configuration['api_key_supermetrics']
        supermetrics.log = log
        supermetrics.url = configuration['url_supermetrics']
        if type(dictClientsById) == dict and len(page) > 2 :
            posts = supermetrics.startMultiQuery(dictClientsById)          
            if posts != 'NotFound' and posts != 'limit' :
                listPostFormat = []
                posts = posts['data']
                headers = posts[0]
                posts.pop(0)            
                for post in posts:
                    dictPost = dict(zip(headers,post))                    
                    auxsplit = dictPost['Post ID'].split('_')
                    dictPost['Post link'] = 'https://www.facebook.com/'+str(auxsplit[0])+'/posts/'+str(auxsplit[1])
                    postformat =  json.dumps({"type":"facebook","data":dictPost, "account":str(dictClientsById[auxsplit[1]])}) 
                    listPostFormat.append(postformat)
                return listPostFormat
            elif posts == 'limit':
                return 'limit'
            elif posts  == 'NotFound':
                return  'NotFound'
            
        else:
            posts, username = supermetrics.startQuery()
            if posts != 'NotFound' and posts != 'limit' :
                listPostFormat = []
                posts = posts['data']
                headers = posts[0]
                posts.pop(0)
                horaac = None
                sortedArray = sorted(
                    posts,
                    key=lambda x: datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S'), reverse=False
                )

                if posts != None and username != 0:            
                    for post in sortedArray:
                        dictPost = dict(zip(headers,post))                    
                        auxsplit = dictPost['Post ID'].split('_')
                        datetime_object = datetime.strptime(dictPost['Created time'], '%Y-%m-%d %H:%M:%S')
                        datetime_object = datetime_object.replace(tzinfo=timezone('Europe/Helsinki'))
                        dictPost['Created time'] = datetime_object.astimezone(timezone('America/Bogota'))- timedelta(hours=1)- timedelta(minutes=20)  
                        dictPost['Created time'] = str(dictPost['Created time']).replace('-05:00','')     
                        dictPost['Post link'] = 'https://www.facebook.com/'+str(auxsplit[0])+'/posts/'+str(auxsplit[1])
                        dictPost['id_str'] = dictPost['Post ID']
                        dictPost['account'] = str(username[0])
                        postformat =  json.dumps({"type":"facebook","data":dictPost, "account":str(username[0])}) 
                        listPostFormat.append(postformat)

                    return listPostFormat
            elif posts == 'limit':
                return 'limit'
            elif posts  == 'NotFound':
                return  'NotFound'
    except Exception as e:
        log.error(str(e),True,True)

def addFacebookPostsToQueue(posts):
    try:
        configuration = cargaConfig(log)
        mq1 = mqClass(log)
        for post in posts:
            jsonFormat = json.loads(post)
            #jsonFormat['data'] = json.dumps(jsonFormat['data'])
            mq1.add(json.dumps(jsonFormat),str(configuration['cache_port']))
    except Exception as e:
        log.error(str(e),True,True)


