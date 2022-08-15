from typing import List, Dict
import inspect
import datetime
import json
import random
import string
import requests
import urllib
# import os
# import datetime

# Abecedario a utilizar en el cifrado
abc = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"+"ABCDEFGHIJKLMNÑOPQRSTUVWXYZ".lower()+":/"

#Carga la configuracion del archivo config.ini
def cargaConfig(log):
    configuration = None
    try:
        with open("./Config/config.ini", "r", encoding="utf-8") as f:
            configuration = json.loads(f.read())
    except  Exception as e:
        log.error("Error al obtener los config.ini:"+str(e),True,True)
    return configuration

def cargaConfigApi(log):
    configuration = None
    try:
        with open("./Config/configApi.json", "r", encoding="utf-8") as f:
            configuration = json.loads(f.read())
    except  Exception as e:
        log.error("Error al obtener los config.ini:"+str(e),True,True)
    return configuration

#Carga la configuracion del archivo ParametrosInicio.ini
def cargaConfigIni(log):
    configuration = None
    try:
        with open("./Config/ParametrosInicio.ini", "r", encoding="utf-8") as f:
            configuration = json.loads(f.read())
    except  Exception as e:
        log.error("Error al obtener los config.ini:"+str(e),True,True)
    return configuration

def cargaConfig_twitter_credentials(log):
    configuration = None
    try:
        with open("./Config/twitter_credentials.ini", "r", encoding="utf-8") as f:
            configuration = json.loads(f.read())
    except  Exception as e:
        log.error("Error al obtener los twitter_credentials.ini:"+str(e),True,True)
    return configuration

def BuscarDatoEnListaObjt(lista,campo,buscar):
    contar = 0
    for item in ObjectToJson(lista):
        if item[campo].upper() == buscar.upper():
            return {'conteo': contar, 'data':ObjectToJson(item)}
        contar += 1 
    return {'conteo': contar, 'data': None}
#Busca si la cuenta existe o no
def isDefine(obj,name):
    try:
        if name == 'screen_name':
            campo = obj['user']['screen_name']
        if name == 'delete':
            campo = obj['delete']
        return True
    except Exception as e :
        return False
#Convierte de Json a objeto
def JsonToObject(data, cls):
    annotations: dict = cls.__annotations__ if hasattr(cls, '__annotations__') else None
    if issubclass(cls, List):
        list_type = cls.__args__[0]
        instance: list = list()
        for value in data:
            instance.append(JsonToObject(value, list_type))
        return instance
    elif issubclass(cls, Dict):
            key_type = cls.__args__[0]
            val_type = cls.__args__[1]
            instance: dict = dict()
            for key, value in data.items():
                instance.update(JsonToObject(key, key_type), JsonToObject(value, val_type))
            return instance
    else:
        instance : cls = cls()
        for name, value in data.items():
            field_type = annotations.get(name)
            if inspect.isclass(field_type) and isinstance(value, (dict, tuple, list, set, frozenset)):
                setattr(instance, name, JsonToObject(value, field_type))
            else:
                setattr(instance, name, value)
        return instance

def ObjectToStr(obj):
    #result = json.dumps(obj, cls=ObjectEncoder, indent=4, sort_keys=True)
    result = json.dumps(obj, cls=ObjectEncoder)
    return result
def StrToJson(str):
    return json.loads(str)
#Objeto a Json
def ObjectToJson(obj):
    #result = json.dumps(obj, cls=ObjectEncoder, indent=4, sort_keys=True)
    result = StrToJson(ObjectToStr(obj))
    return result
class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_json"):
            return self.default(obj.to_json())
        elif hasattr(obj, "__dict__"):
            d = dict(
                (key, value)
                for key, value in inspect.getmembers(obj)
                if not key.startswith("__")
                and not inspect.isabstract(value)
                and not inspect.isbuiltin(value)
                and not inspect.isfunction(value)
                and not inspect.isgenerator(value)
                and not inspect.isgeneratorfunction(value)
                and not inspect.ismethod(value)
                and not inspect.ismethoddescriptor(value)
                and not inspect.isroutine(value)
            )
            return self.default(d)
        return obj

#Fecha a string
def dateToStringLocal(hoy,diferencia):
    fecha = hoy - datetime.timedelta(hours=diferencia)
    return fecha

#Fecha de
def datetimeToStr(hoy,format):
    return hoy.strftime(format)

#formatea el string
def formatStr(string):
    return string.replace("'", " ")

#String a epch
def strToEpoch(data,format):
    datetime_object = datetime.datetime.strptime(data, format)
    milliseconds = int(round(datetime_object.timestamp() * 1000))
    return milliseconds

#String a fecha
def strToDatetime(str,format):
    datetime_object = datetime.datetime.strptime(str, format)
    return datetime_object

#Epoch a fecha
def epochToDate(epoch):
    return datetime.datetime.fromtimestamp(epoch/1000)

#Epoch a fecha string
def epochToDateStr(epoch,format):
    return datetime.datetime.fromtimestamp(epoch/1000).strftime(format)

#Fehca a Utc
def dateUtc(utc):
    return dateToStringLocal(datetime.datetime.now(),utc)

def encontrarFormatoFecha(fechaStr : str,tipoRetorno = 'date'):
    epochDate = None
    
    arrayFormats = ['%a %b %d %H:%M:%S %z %Y','%a %b %d %H:%M:%S   %Y','%a, %d %b %Y %H:%M:%S GMT','%a, %d %b %Y %H:%M:%S %z','%Y-%m-%dT%H:%M:%SZ','%Y-%m-%d %H:%M:%S']
    for item in arrayFormats:
        if epochDate == None:  
            try:
                epochDate = strToEpoch(fechaStr, item)
            except Exception as e:
                pass 
    if tipoRetorno == 'epoch':
        return epochDate
    if tipoRetorno == 'date':
        return epochToDate(epochDate)


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
    # print("Random string of length", length, "is:", result_str)

def cifradoCesar(texto:string,n:int):
    # Variable para guardar mensaje cifrado
    cifrado = ""
    for l in texto:
        # Si la letra está en el abecedario se reemplaza
        if l in abc:
            pos_letra = abc.index(l)
            # Sumamos para movernos a la derecha del abc
            nueva_pos = (pos_letra + n) % len(abc)
            cifrado+= abc[nueva_pos]
        else:
            # Si no está en el abecedario sólo añadelo
            cifrado+= l

    # print("Mensaje cifrado:", cifrado)
    return cifrado

def desCifradoCesar(texto:string,n:int):
    # Iteramos por posibles valores de desplazamiento
    for i in range(28):
        # Guardar posible mensaje
        descifrado = ""
        for l in texto:
            # Si la letra está en el abecedario reemplazamos
            if l in abc:
                pos_letra = abc.index(l)
                # Restamos para movernos a la izquierda
                nueva_pos = (pos_letra - i) % len(abc)
                descifrado += abc[nueva_pos]
            else:
                descifrado+= l
        msj = (f"ROT-{i}:", descifrado)
        # print(msj)
        if i == n:
            return descifrado
        

        
def OrdenarjsonPorKey(list,key):
    return sorted(list, key=lambda k: k[key], reverse=True)

def UnicoJson(seq, key):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x[key] not in seen and not seen_add(x[key])]
        


def minimiUrl(url_full,configuration):
    key = configuration['url_key_minimi']
    url = urllib.parse.quote(url_full)
    url = url_full
    name  = 'xcpect.us'
    userDomain = '1'
    r = requests.get('http://cutt.ly/api/api.php?key={}&short={}&userDomain={}'.format(key, url,userDomain))
    # KCr = requests.get('http://cutt.ly/api/api.php?key={}&short={}&name={}&userDomain={}'.format(key, url, name, userDomain))
    if r.status_code == 200:
        jsonData =  StrToJson(r.text)
        try:
            if jsonData['url']['status'] == 7:
                return jsonData['url']['shortLink']
            else:
                return url
        except Exception as e:
            print("minimiUrl   = "+str(jsonData))
            return url
    else:
        return url
    print(r.text)