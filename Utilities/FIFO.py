from pymemcache.client import base
from Utilities.utils import cargaConfig
# from Utilities.MemCached import memcacheClass

class pila:
    def __init__(self,log):
        try:
            self.log = log;
            self.log.info("PILA => __init__ => Entrada",True,True)
            configuration = cargaConfig(log)
            self.url = configuration['cache_url']
            self.port = configuration['cache_port']
            self.client = base.Client((configuration['cache_url'], configuration['cache_port']))
            # self.printGuia();
            self.log.info("PILA => __init__ => Salida",True,True)
            
        except Exception as e:
            self.log.error("PILA => __init__ =>  %s  " % (e),True,True)
    def clientAdd(self,port):
        self.port = port
        self.client = base.Client((self.url, port))
    def setIni(self):
        self.log.info("PILA => setIni => Entrada",True,True)
        stCola = True
        while stCola:
            try:
                cima = self.client.get("cima")
                cola = self.client.get("cola")
                self.log.info("PILA => setIni => cima=>"+str(cima)+",cola=>"+str(cola),True,True)
                if cima != None and cola != None:
                    self.cima = int(cima)
                    self.cola = int(cola)
                else:   
                    if cima == None and cola == None:
                        cima = self.cima = 1
                        cola = self.cola = 1
                        self.client.add("cima",self.cima)
                        self.client.add("cola",self.cola)  
                    else:
                        self.log.error("PILA => setIni => cima=>"+str(cima)+",cola=>"+str(cola),True,True)
                self.log.info("PILA => setIni => Salida",True,True)
                stCola = False
                
            except ConnectionRefusedError as b:
                # me = memcacheClass(log)
                self.log.error("PILA => setIni => %s memcache No Iniciado " % (b),True,True)
                stCola = False
                # me.coustomMemdcached(self.port)
                return -1
            except (OSError,KeyError,AttributeError) as os:
                stCola = False
            except Exception as e:
                self.log.error("PILA => setIni Exception => %s  => Type %s" % (e,type(e)),True,True)
            
        return True

    def printGuia(self):
        try:
            self.log.info("PILA => printGuia => Entrada",True,True)
            if self.client.get("cima") != None:
                self.log.info("PILA => printGuia => Cima:"+str(self.client.get("cima"))+",Cola:"+str(self.client.get("cola")),False,True)
            self.log.info("PILA => printGuia => Salida",True,True)
        except Exception as e:
            self.log.error("PILA => => printGuia =>%s  " % (e),True,True)
        
    def add(self,value):
        try:
            self.log.info("PILA => add => Entrada",True,True)
            cacheIni = self.setIni()
            if cacheIni:
                self.log.info("PILA => add => setIni",True,True)
                coltemp = self.cola 
                self.client.set("cola",self.cola +1)
                name = "stream"+str(coltemp)
                self.client.add(name,value)
                self.log.warning("PILA => add data Cola: "+str(coltemp),False,True);
                # self.log.info("Value: "+str(self.client.get(name)),False,True);
                self.log.info("PILA => add => Salida",True,True)
            else:
                self.log.error("PILA => add => Error carga de setIni ",True,True)
        except Exception as e:
            self.log.error("PILA => add =>%s  " % (e),True,True)
    def separate(self,value):
        setIni();
    def set(self,key,value):
        try:
            self.log.info("PILA => set => Entrada",True,True)
            self.client.set(key,value)
            self.log.info("PILA => set =>Key :"+str(self.client.get(key)),False,True)
            self.log.info("PILA => set => Salida",True,True)
        except Exception as e:
            self.log.error("PILA => => set =>%s  " % (e),True,True)
    def get(self,key):
        return self.client.get(key)
    def touch(self,key,expire = 0):
        return self.client.touch(key,expire)
    def delete(self,key):
        self.log.warning("PILA => delete =>Key :"+str(key),False,True)
        return self.client.delete(key)
    def flush_all(self):
        self.client.flush_all() 