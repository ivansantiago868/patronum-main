
import psutil
import os 
from Controller.FilesController import getListPortsByClientAll, GetPortByCliet_id
from Utilities.theread  import threadingClass
from Utilities.FIFO import pila
from Utilities.utils import cargaConfig

class memcacheClass:
    def __init__(self, log):
        self.log = log

    def createMemcached(self,clients):
        configuration = cargaConfig(self.log)
        port = configuration['cache_port']
        p1 =  threadingClass(self.log)
        arg = (self.log,port,)
        p1.selectFunction("openMemcached","openMemcached "+str(port),arg)
        p1.start()
        list_ports = getListPortsByClientAll()
        for client in clients:
            listport = GetPortByCliet_id(self.log,list_ports,client)
            if len(listport):
                port = listport[0].port
                client_id = listport[0].client_id
                p1 =  threadingClass(self.log)
                arg = (self.log,port,)
                p1.selectFunction("openMemcached","client "+str(client_id)+",openMemcached "+str(port),arg)
                p1.start()
                pi = pila(self.log);
                pi.clientAdd(port)
                pi.setIni()
    def coustomMemdcached(self,port):
        p1 =  threadingClass(self.log)
        arg = (self.log,port,)
        p1.selectFunction("openMemcached","openMemcached "+str(port),arg)
        p1.start()
    def deletPip(self):
        for p in psutil.process_iter():
            if p.name() == 'memcached.exe':
                print(p, p.name(), p.pid)
                p.terminate()
                self.log.info("KIIL process",True);