
from Utilities.mq import mqClass
import json
from Utilities.utils import JsonToObject,ObjectToJson, cifradoCesar
from Entity.Publics import RssMonibot, Rss
import feedparser
import requests
from bs4 import BeautifulSoup
from typing import List


class controlRss:
    def __init__(self,log,Rss_Configuration,past_Rss,configuration):
        self.Post_List = []
        self.newLine = chr(10)
        self.past_Rss = {}
        self.past_Rss= past_Rss
        self.log = log
        self.Rss_Configuration=Rss_Configuration
        self.List_Rss = {}
        self.configuration = configuration

    def mainRss(self):
        self.log.warning("Entra -> mainRss de manage_rss",True,True)
        if len(self.Rss_Configuration) > 0:
            for rssConfig in self.Rss_Configuration:
                self.listRss(rssConfig)
                self.ValidarListRss(rssConfig)  
                self.past_Rss[rssConfig['url']] = self.ValidateRss(self.List_Rss[rssConfig['url']], self.past_Rss[rssConfig['url']],log=self.log,configuration=self.configuration)
        self.log.warning("Salida -> mainRss de manage_rss",True,True)
            
    def ValidarListRss(self,rssConfig):
        for post in self.Post_List:
            self.List_Rss[post.linkRss].append(post)
                
    def listRss(self,rssConfig):
        self.log.warning("Entra -> listRss de url :"+rssConfig['url'],True,True)
        rss = feedparser.parse(rssConfig['url'])
        self.List_Rss[rssConfig['url']] = []
        if len(rss.entries) > 0:
            for post in rss.entries:
                r = Rss()
                r.title = post.title
                r.url = post.link
                try:
                    r.summary = post.summary
                except Exception as e:
                    self.log.warning(msn="Rss "+str(e)+" ",display=False,dateStatus= True,time= True)
                    r.summary = ''
                r.published = post.published
                r.author = rssConfig['sh_name']
                r.account = rssConfig['sh']
                try:
                    page = requests.get(post.link)
                    soup = BeautifulSoup(page.content.decode("utf-8").replace(self.newLine , ''), 'html.parser')
                    r.beautiful = soup.text
                except Exception as e:
                    r.beautiful = ''
                try:
                    try:
                        content = post.content
                        textContent = ''
                        if len(content) > 0:
                            for contInt in content:
                                if contInt.value != '':
                                    textContent = contInt.value
                                    break
                        soup = BeautifulSoup(textContent, 'html.parser')
                        r.text = soup.text
                    except Exception as econten:
                        r.text = post.summary
                except requests.exceptions.ConnectionError as e:
                    self.log.warning("url:"+post.link +",error:  " +str(e),display=False,dateStatus=True,time=True)
                    r.text = post.summary
                except Exception as e:
                    self.log.error("RSS:"+rssConfig['url']+"->url:"+post.link +",error:  " +str(e),modul="do_something",display=True,dateStatus=True)
                r.linkRss = rssConfig['url']
                r.id_str = cifradoCesar(rssConfig['url'],7)
                self.Post_List.append(r)
        else:
            self.log.warning("url:"+ rssConfig['url'] +",error: sin datos ",display=True,dateStatus=True,time=True)
        self.log.warning("Salida -> listRss de url :"+rssConfig['url'],True,True)
    #Validara si los RSS de un timepo determinado han cambiado con respecto al recien obtenido       
    def ValidateRss(self,listRss,past_Rss,log,configuration):
        try:
            if not past_Rss:
                    RssToJson(listRss)
                    sendDataToCola(listRss,self.log,self.configuration)
                    return listRss

            else:
                new_list = []
                for new_data in listRss :
                    buscarMensaje = True
                    for old_data in past_Rss:
                        if old_data.summary == new_data.summary and old_data.title == new_data.title:
                            buscarMensaje = False
                    if buscarMensaje:
                        new_list.append(new_data)
                        past_Rss.append(old_data)
                if new_list:
                    sendDataToCola(new_list,self.log,self.configuration)
                
                #new_list = past_Rss
                RssToJson(new_list)
                return new_list
        except Exception as e:
            log.error("Error en "+str(e),modul="ValidateRss",display=True,dateStatus=True)

            
#Función para convertir los RSS obtenidos al formato json
def RssToJson(listRss):
    alisJson = ObjectToJson(listRss)
    todos_los_json = []
    try:
        with open("FileProcess/msnRSS.json") as f:
            for linea in f:
                for item in json.loads(linea):
                    alisJson.append(item)
    except Exception as e:
        pass
    with open('FileProcess/msnRSS.json', 'w+') as json_file:
        json.dump(alisJson, json_file)

#Función que mandara los RSS a la cola de mq
def sendDataToCola(dataRss,log,configuration):
    mq = mqClass(log)
    mq.declare(str(configuration['cache_port']))
    for data in dataRss:
        data = {"type": "rss", "data":json.loads(json.dumps(ObjectToJson(data)))}
        data = json.dumps(data)
        if not mq.add(data,str(configuration['cache_port'])):
            mq = mqClass(log);
            mq.add(data,str(configuration['cache_port']))