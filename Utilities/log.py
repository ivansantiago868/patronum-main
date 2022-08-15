from ast import Try
from Controller.manage_tweet import getSendMessage
import logging
import time
from logging.handlers import RotatingFileHandler
from Utilities.utils import cargaConfig, dateUtc
import sys, os

class log_file:
    def __init__(self, ruta):
        try:
            logging.basicConfig(filename=ruta, level=logging.INFO)
            self.fecha = "Fecha: "
            self.msn = " ,Msn: "
            self.log_File = True
            self.config = cargaConfig(self)
            self.utc = 0
            self.top = ''
            self.time = ''
            self.utc = self.config['utc_log']
            
        except Exception as e:
            logging.error(e); 
        
    def setTime(self,time):
        self.time = " ,Time: %.10f seconds." % time
    def setLog_file(self,log_File):
        self.log_File = log_File
    def info(self,msn,display = False,dateStatus =  False):
        try:
            if(dateStatus):
                msn = self.fecha+ dateUtc(self.utc).strftime("%c")+self.top+self.msn+msn+self.time
                self.time = ''
            if self.log_File:
                if display:
                    print(msn);
                    logging.info(msn); 
                else:
                    logging.info(msn); 
            else:
                if display:
                    print(msn);
        except Exception as e:
            logging.error(e); 
    def error(self,msn,modul = "",display = False,dateStatus =  False,SendMsn = True):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        try:
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        except Exception as e:
            fname = ""
            print(e)
        # print(exc_type, fname, exc_tb.tb_lineno)
        anexo = f" programa : {fname}, line: {exc_tb.tb_lineno}"
        if(dateStatus):
            if(modul != ""):
                msn = self.fecha+ dateUtc(self.utc).strftime("%c")+self.top+ " ,Module: "+modul+self.msn+msn+self.time+anexo
                self.time = ''
            else: 
                msn = self.fecha+ dateUtc(self.utc).strftime("%c")+self.top+self.msn+msn+self.time+anexo
                self.time = ''
        
        if display:
            print(msn);
            logging.error(msn); 
        else:
            logging.error(msn); 
        body = { 
            "fromPhone":self.config['bot_id'],
            "text":msn,
            "toPhone":self.config['log_canaltelegram'],
            "channel":"telegram",
            "messageBodyType":"chat"
        }
        if (SendMsn):
            getSendMessage(self,body,self.config)

    def warning(self,msn,display = False,dateStatus =  False,time = False):
        if(dateStatus):
            if time:
                self.time = " ,Time: %.10f seconds." % time
                msn = self.fecha+ dateUtc(self.utc).strftime("%c")+self.top+self.msn+msn+self.time
            else:
                msn = self.fecha+ dateUtc(self.utc).strftime("%c")+self.top+self.msn+msn+self.time
            self.time = ''
        if display:
            print(msn);
            logging.info(msn); 
        else:
            logging.info(msn); 
            
    def printer(self,msn,dateStatus =  False):
        if(dateStatus):
            msn = self.fecha+ dateUtc(self.utc).strftime("%c")+self.top+self.msn+msn+self.time
            self.time = ''
        print(msn);

    def addlogger(self,type, message):
        logFile = 'C://Log//Stream//stream.log'
        my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=20 * 1024 * 1024, backupCount=30, encoding=None, delay=0)

        #while True:
        if type == 'info':
            my_handler.setLevel(logging.INFO)
            app_log = logging.getLogger('root')
            app_log.setLevel(logging.INFO)
            app_log.addHandler(my_handler)
            app_log.info("INFO=>:" + message)

        if type == 'error':
            my_handler.setLevel(logging.error)
            app_log = logging.getLogger('root')
            app_log.setLevel(logging.error)
            app_log.addHandler(my_handler)
            app_log.error("ERROR=>: " + message)

        if type == 'warning':
            my_handler.setLevel(logging.warning())
            app_log = logging.getLogger('root')
            app_log.setLevel(logging.warning)
            app_log.addHandler(my_handler)
            app_log.warning("WARNING=>: "+message)


