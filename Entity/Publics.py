# import inspect
# import json
# from json import JSONEncoder
from typing import List
from datetime import datetime
from Utilities.utils import datetimeToStr,dateToStringLocal, encontrarFormatoFecha,strToEpoch,epochToDate,epochToDateStr
import datetime
from pytz import timezone

class relation(object):
    hoja: str
    name : str
    objeto : str
    type:str

#Clase de canal por Sh
class channel_by_stakeholder(object):
    id : int
    name : str
    account : str
    account_id : int
    channel_name : str
    channel_id : int 
    client_id : int
    search_id : str
    tipo : str
    alias: str
    
    #Agrega sh general
    def addGeneral(self,data,client, type_social):
        if type_social == 'twitter':
            self.id =  1
            self.name = data.nombre
            self.account = data.tw
            self.account_id = data.account_id
            self.channel_name = ""
            self.channel_id = client.channel
            self.client_id = int(client.client_id)
            self.search_id = ""
            self.tipo = "gen"
            self.alias = ""
        if type_social == 'facebook':      
            self.id =  1
            self.name = data.nombre #
            self.account = data.fb
            self.account_id = ''
            self.channel_name = ""
            self.channel_id = client.channel
            self.client_id = int(client.client_id)
            self.search_id = ""
            self.tipo = "gen"
            self.alias = ""

    
    #Agrega Sh
    def addSh(self,data,client, type_social):
        if type_social == 'twitter':
            self.id =  1
            self.name = data.nombre
            self.account = data.tw
            self.account_id = data.account_id
            self.channel_name = ""
            self.channel_id = client.channel
            self.client_id = int(data.client_id)
            self.search_id = ""
            self.tipo = data.tipo
            self.alias = data.alias
        if type_social == 'facebook':
            self.id =  1
            self.name = data.nombre
            self.account = data.fb
            self.account_id = data.account_id
            self.channel_name = ""
            self.channel_id = client.channel
            self.client_id = int(data.client_id)
            self.search_id = ""
            self.tipo = data.tipo
            self.alias = data.alias

#Acalse de stakeholder
class stakeholder(object):
    id: int 
    stakeholder_id  : str
    name : str
    account : str
    account_id : str
    channel_name : str
    channel_id : str
    client_id : int
    search_id : str
#clase de stakeholder por cuenta de id
class stakeholderAccount_id(object):
    account_id : str

 #Clase de puerto de clienet   
class clientPort(object):
    client_id : int
    port : int
    active : bool
    name : str
    number: int
    pais_id : int
    bk_full : bool
    bk_send : bool

    #
    def set_data(self,data):
        self.pais_id = int(data.pais_id)
        self.client_id = int(data.client_id)
        self.port = int(data.port)
        stado =  False
        if data.active == "1" or data.active == True:
            stado =  True
        else:
            stado =  False
        self.active = stado
        self.name = data.cola_name
        self.number = int(data.numero)
        self.bk_send = data.bk_send
        self.bk_full = data.bk_full


class NicknameSH(object):
    alias: str
    client_id : int
    sh_id : str
    viewpoint : str
    is_internal : bool

    def addAlias(self,data):
        self.alias = data.alias
        self.client_id = int(data.client_id)
        self.sh_id = ""
        self.viewpoint = ""
        self.is_internal = False
        if data.tipo == "Primario":
            self.is_internal = True
        if data.tipo == "Secundario":
            self.is_internal = False

#Clase de palabras de interes
class InteresMonibot(object):
    Type : str
    client_id : int
    evaluation : str
    search_id : str
    title : str
    word : str

    #Agrega palabra de interes
    def addInteres(self,data,int_un):
        self.Type = "Interes"
        self.client_id = int(data.client_id)
        self.evaluation = data.tipo
        self.search_id ="all"
        self.title = data.nombre
        self.word = int_un
#Clase de palabras de excepcion
class ExceptionsMonibot(object):
    client_id: int
    word: str

    #Agrega palabra excepcion
    def addExceptions(self, data, int_un):
        self.client_id = int(data.client_id)
        self.word = int_un

#Clase de Rss
class RssMonibot(object):
    title: str
    link: str
    summary: str
    published: str
    authors: str

    #Agregar Rss
    def addRss(self, data):
        self.title = data.Title
        self.link = data.Url
        self.summary = data.Summary
        self.published = data.Published
        self.authors = data.Authors

#Calse oracion
class Prayer(object):
    prayer: str
    subject: List[str]
    attitude: str        

class Prayer(object):
    prayer : str
    subject : List[str]
    attitude: str

#Clase de publication
class PublicationMonibot(object):
    provider_item_id : str
    search_id : str
    client_id: int
    name: str
    screen_name: str
    created_at: int
    engine: str
    sts_text: str
    sts_text_format: str
    attitude: str
    source_url : str
    prayers : List[Prayer]
    process_attitude : str
    send_notification : bool
    rule : str
    package_name = str

    def __init__(self):
        self.send_notification = False
        self.prayers =  None
        self.process_attitude = None
        self.attitude = None
        self.rule = None
        self.sts_text_format =  None
        self.package_name = None

    def setTwitter(self,data,client_id,type):
        if type == 'twitter':
            self.client_id = client_id 
            self.created_at = strToEpoch(data['created_at'], '%a %b %d %H:%M:%S %z %Y')
            self.engine = "Twitter"
            self.name = data['user']['name']
            self.provider_item_id = str(data['id_str']),
            self.screen_name =  data['user']['screen_name'], 
            self.search_id = "hydra2066",
            self.source_url = "https://twitter.com/"+data['user']['screen_name']+"/status/"+data['id_str'],
            self.sts_text = data['text']
        if type == 'rss':
            self.client_id = client_id 
            self.created_at = encontrarFormatoFecha(data['published'],'epoch')
            self.engine = "RSS"
            self.name = data['author']
            self.provider_item_id = str(11111111111),
            self.screen_name =  data['account'], 
            self.search_id = "hydra2066",
            self.source_url = data['url'],
            self.sts_text = data['text']
        if type == 'facebook':
            self.client_id = client_id 
            self.created_at = data['Created time']        
            self.engine = "Facebook"
            self.name = data['account']
            self.provider_item_id = str(data['id_str'])
            self.screen_name =  'Posts'
            self.search_id = "hydra2066"
            self.sts_text = str(data['Message'])
            self.source_url = data['Post link'],

            


#Clase de tipo de palabras
class TypesWords(object):
    def __init__(self,informative, positive, negative):
        self.informative = informative
        self.positive = positive
        self.negative = negative
        
# class SHAttitude(object):
    
#     attitude :str
#     client_id : int
#     screen_name : str
#     stakeholder_id : str
#     twitter_account : str

# class ListSH(object):
#     list_sh : List[SHAttitude]

# class ListSH(object):
#     list_sh : List[SHAttitude]

#Clase telegram
class MonibotTelegram(object):
    id : int
    client_id : int 
    name_chat : str 
    id_channel : str 
    status : bool 
    id_group : str

#Clase busqueda
class search_result(object):
    id : int
    provider_item_id : str
    country_id : int   
    langugage : int 
    provider_id : str 
    search_id : str
    name : str
    created_at : datetime
    profile_image_url : str
    screen_name : str
    engine : str
    source_url : str
    geo_id : str
    geo_name : str
    geo_code : str
    geo_country : str  
    geo_city : str 
    geo_latitude : str 
    geo_longitude : str
    friends_count : int 
    followers_count :  int
    created_at_default_time_zone : str
    created_at_local : datetime
    created_at_local_utime : int
    created_at_time_zone : str
    mood_flag : str
    favorite_url : str
    reply_url : str
    follow_url : str
    stakeholder_id : str 
    geo_Statue : str
    sts_text : str
    attitude : str

    #metodo de json a tweeter
    def JsonToTwetter(self,tw,stakeholders,UTC):
        self.provider_item_id = tw['id']
        self.country_id = 0
        self.langugage = 0;
        self.provider_id = ""
        self.name = tw['user']['screen_name']
        self.profile_image_url = "https://avatars.io/twitter/" + tw['user']['screen_name']
        self.source_url = "https://twitter.com/" + tw['user']['screen_name'] + "/status/" + str(tw['id'])
        self.screen_name = tw['user']['screen_name']
        self.engine = "stream"
        self.search_id = stakeholders.search_id
        if "extended_tweet" in tw:
            objTweet = tw["extended_tweet"]
        else:
            objTweet = None
        if objTweet != None:
            textAllTweet = objTweet["full_text"]
            if (objTweet != None):
                if (textAllTweet != None):
                    textTweet = textAllTweet
                else:
                    textTweet = tw["text"];
            else:
                textTweet = tw["text"];
        else:
            textTweet = tw["text"];
        self.sts_text = textTweet;
        self.friends_count = tw['user']["friends_count"];
        self.followers_count = tw['user']["followers_count"];
        format = "%Y-%m-%d %H:%M:%S" 
        #2020-01-29 14:14:58.000
        dateTw = epochToDate(strToEpoch(tw['created_at'],"%a %b %d %H:%M:%S %z %Y"))
        self.created_at = datetimeToStr(dateTw,format)
        self.created_at_local = datetimeToStr(dateToStringLocal(dateTw,-UTC),format) 

#Clase construir mensaje
class MessageBuild(object):
    mensaje :  str
    appName :  str
    autor :  str
    currentConverted :  str
    groupName :  str
    clientName :  str
    textoFinal :  str
    attitudeResponse :  str
    intereses :  str
    sourceUrl :  str
    typeAlert :  str 
    intention :  str

    def __init__(self,mensaje, appName, autor,currentConverted,groupName,clientName,textoFinal,attitudeResponse,intereses,sourceUrl):
        self.mensaje = mensaje
        self.appName = appName
        self.autor = autor
        self.currentConverted = currentConverted
        self.groupName = groupName
        self.clientName = clientName
        self.textoFinal = textoFinal
        self.attitudeResponse = attitudeResponse
        self.intereses = intereses
        self.sourceUrl = sourceUrl
        self.typeAlert = None
        self.intention = None



# classes de driver sobre nueva estructura de drive 
class client(object):
    pais_id : int
    active : bool
    client_id: int 
    cola_name :str
    general_sh: bool
    name_proyect: str
    port: int
    channel : str
    numero: int

    #agrega cliente
    def addClient(self,data):
        self.pais_id = int(data['pais_id'])
        self.active = int(data['active'])
        self.client_id= int(data['client_id'])
        self.cola_name = data['cola_name']
        self.general_sh= int(data['general_sh'])
        self.name_proyect= data['name_proyect']
        self.port = int(data['port'])
        self.channel = data['channel']
        self.numero = int(data['numero'])

#clase Sh
class stakeholder(object):

    client_id : int
    interes : str
    nombre : str
    cargo : str
    tw : str
    account_id : str
    fb : str
    tipo : str
    alias : str
    rss : str

#clase Sh general
class stakeholder_general(object):
    nombre : str
    tw : str
    foto : str
    fb : str
    fb_link : str
    ins : str
    tik : str
    medio : str
    account_id : str
    rss : str

#case intereses del cliente
class interes_client(object):
    client_id : int
    nombre : str
    interes : str
    tipo : str

#clase excepciones del cliente
class exceptions_client(object):
    client_id: int
    exceptions: str    

#clase de rss
# class Rss(object):
    # title: str
    # link: str
    # summary: str
    # published: str
    # authors: str

class Rss(object):
    title : str
    url : str
    summary : str
    published : str
    author : str
    account : str
    text : str
    beautiful : str
    linkRss : str
    id_str : str
class Query(object):
    server_id:int
    client_id: int
    querys:str
        
#Clase interes compues de interes
class interes_compuesto_client(object):
    Type : str
    client_id : int
    evaluation : str
    search_id : str
    title : str
    word : str
    numInteres:str
    idInteres:int
    # interes2 : str
    # interes_dos_Descripcion :str
    # interes_dos_evaluacion:str


    #Agrega palabra de interes
    def addInteres(self,data ):
        self.Type = "Interes"
        self.client_id = int(data[0])
        self.evaluation = data[1]
        self.search_id ="all"
        self.title = data[2]
        self.word = data[3]
        self.numInteres = data[4]
        self.idInteres = data[5]



# #Clase interes compues de interes
# class interes_compuesto_client(object):
#     client_id : int
#     nombre : str
#     interes1 : str
#     interes_uno_descripcion :str
#     interes_uno_evaluacion:str
#     interes2 : str
#     interes_dos_Descripcion :str
#     interes_dos_evaluacion:str


#     #Agrega palabra de interes
#     def addInteres(self,dataCliente , interes1 , interes2):
#         self.client_id = dataCliente[0]["client_id"]
#         self.nombre = dataCliente[0]["name_proyect"]

#         self.interes1 = interes1[0]['nombre']
#         self.interes_uno_descripcion = interes1[0]['interes']
#         self.interes_uno_evaluacion = interes1[0]['tipo']

#         self.interes2 =  interes2[0]['nombre']
#         self.interes_dos_descripcion = interes2[0]['interes']
#         self.interes_dos_evaluacion = interes2[0]['tipo']