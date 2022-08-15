import json
import time
from Utilities.utils import cargaConfig
from Utilities.log import log_file
import Controller.SuperMetricsController as superMetrics
from Controller.FilesController import getListChannelByStakeholderAll_facebook
from time import time
import sched, time
import argparse
from Utilities.theread import callProgram
from datetime import datetime

log = log_file("C:\Log\Stream\StreamSuperMetrics.log")
configuration = cargaConfig(log)
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--time", help="tiempo de ciclo de lanzamiento")
args = parser.parse_args()
if args.time is None:
    args.time = configuration['time_reboot']
time_trends = (60*int(args.time))

def main():
    log.info("iniciar",True,True)
    log.warning("#################################################",True);
    log.warning("#########-INICIANDO PYTHON STREAM SUPERMETRICS -##########",True);
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
            
            channel_by_stakeholders_F = getListChannelByStakeholderAll_facebook()
            #superMetrics.extractorFacebookAllClients(configuration,channel_by_stakeholders_F,'last_6_days',1000)
            
            superMetrics.extractorFacebook(configuration,channel_by_stakeholders_F,'last_2_days_inc',1000)

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


#Ejecuta los arhcivo .exe
callProgram(log,configuration['pathfile']+'StreamFile.exe')
configuration = cargaConfig(log)
main()

#main()
# loop = asyncio.get_event_loop()

# loop.run_until_complete(main())
