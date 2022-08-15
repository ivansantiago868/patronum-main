# from Utilities.Tokenizer import tokenizerNltk
from tweepy.streaming import StreamListener
from Utilities.FIFO import pila
from Utilities.mq import mqClass
from Controller.FilesController import  getListChannelByStakeholderAll,getListPortsByClientAll
import time
import json
from Utilities.theread  import threadingClass, multiprocessingClass
from Utilities.utils import isDefine
from Utilities.utils import JsonToObject, ObjectToJson
from Utilities.timeScan import timeClass


class StdOutListenerClass(StreamListener):
    def __init__(self,log,configuration):
        self.conteo = 1
        self.log = log
        self.type = 'twitter'
        self.configuration = configuration
        if self.configuration['memcached']:
            self.pi = pila(self.log);
            self.memoriStatus = self.pi.setIni();
            self.mq = None
        else:
            self.pi = None
            self.mq = mqClass(self.log);
            self.mq.declare(str(self.configuration['cache_port']))
            self.mq.declare(str(self.configuration['cache_port_bk']))
            self.memoriStatus = True
        self.channel = getListChannelByStakeholderAll()
        self.ports = getListPortsByClientAll()
    def on_error(self, status):
        if status == 420:
            self.log.error("FECHA:"+time.strftime("%c")+": "+" ERROR=> CLASS=>StdOutListener,Error=>http.client Incomplete Read error: "+ str(status))
            return False
        if status == 406:
            self.log.error("FECHA:"+time.strftime("%c")+": "+" ERROR=> CLASS=>StdOutListener,Error=>http.client Incomplete Read error: "+ str(status))
            return False
        self.log.error("FECHA:"+time.strftime("%c")+": "+" ERROR=> CLASS=>StdOutListener: "+ str(status))
        return True
    def on_data(self, data):
        t = timeClass(self.log,"name")
        self.log.info("ingreso a on=>data ",True,True)
        try:
            if self.type == 'twitter':
                tweet = {"type":"twitter","data":json.loads(data)}
            elif self.type == 'twitterQuery':
                # tokenizerNltk(json.loads(data))
                tweet = {"type":"query","data":json.loads(data)}
            else:
                tweet = {"type":"twitter","data":json.loads(data)}
            data = json.dumps(tweet) 
            if isDefine(tweet['data'],'screen_name'):
                if tweet['data']['text'].find("RT") == -1:
                    if self.configuration['memcached']:
                        self.pi.add(data)
                    else:
                        if not self.mq.add(data,str(self.configuration['cache_port'])):
                            self.mq = mqClass(self.log);
                            self.mq.add(data,str(self.configuration['cache_port']))
                    self.log.warning("on_data contador =>"+str(self.conteo)+", tw=>"+tweet['data']['id_str'],True,True,t.end())
            self.conteo += 1 
        except Exception as e:
            self.log.error("IError al guardar el Tweet -> on_data => %s : %s " % (e, tweet['data']['id_str']),True,True)
        return True


    


