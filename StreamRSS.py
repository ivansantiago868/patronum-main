
import argparse
import json

from Utilities.utils import cargaConfig
from Utilities.log import log_file
from Controller.manage_rss import  controlRss
from datetime import datetime, date
import sched, time
from datetime import datetime
import scrapy


#Cargará las configuraciones que esten en alrchivo config.ini
log = log_file("C:\Log\Stream\StreamRss.log")     
configuration = cargaConfig(log)
log.log_File=configuration['log']


parser = argparse.ArgumentParser()
parser.add_argument("-t", "--time", help="tiempo de ciclo de lanzamiento")
args = parser.parse_args()
time_trends = (60*int(args.time))
# time_trends = 5
Rss_Configuration = []


past_Rss = {}
for Rss_data in configuration['List_Rss']:
    past_Rss[Rss_data['url']] = []
Config_Rss = configuration['List_Rss']
for Rss_data in Config_Rss:
    Rss_Configuration.append(Rss_data)
rss = controlRss(log,Rss_Configuration,past_Rss,configuration)
def main():
    log.info("iniciar",True,True)
    log.warning("#################################################",True);
    log.warning("#########-INICIANDO PYTHON STREAM RSS -##########",True);
    log.warning("#################################################",True);
    dt_string = datetime.today().strftime("%M")
    countMinutos = ((int(dt_string) // (time_trends/60))+1 ) * (time_trends/60)
    sleep = ((((countMinutos- int(dt_string))-1)*60))-(int(datetime.today().strftime("%S")))+60
    if sleep < 0:
        sleep = 0
    log.warning("~~~~~~~~~Termina Espera sleep ajuste a hora fija: "+str(sleep/60)+", tiempo:"+datetime.today().strftime("%H:%M:%S")+"~~~~~~~",True,True)
    time.sleep(sleep)
    s = sched.scheduler(time.time, time.sleep)
    def do_something(sc): 
        try:
            now = datetime.now()
            log.warning("Ejecutando... Date:"+str(now.date())+",Hora:"+str(now.time()),True,True)
            rss.mainRss()
            now = datetime.now()
            log.warning("Termina... Date:"+str(now.date())+",Hora:"+str(now.time()),True,True)
            log.warning("~~~~~~~~~Termina Espera sleep: "+str(time_trends/60)+", tiempo:"+datetime.today().strftime("%H:%M:%S")+"~~~~~~~",True,True)
            s.enter(time_trends, 1, do_something, (sc,))
            s.run()
        except Exception as e:
            log.error("Error en "+str(e),modul="do_something",display=True,dateStatus=True)
            main()
    s.enter(time_trends, 1, do_something, (s,))
    s.run()
    
main()



