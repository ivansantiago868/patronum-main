from datetime import datetime, date
import json
import time
from Controller.DriveControler import mappingConfig, setFileListClientSheet , UpdateCelda
from Utilities.theread import callProgram
from Utilities.log import log_file
from Utilities.utils import cargaConfig, cargaConfigIni
import psutil
import os
import sched, time
import subprocess

log = log_file("C:\Log\Stream\StreamJob.log")

configurationInicio = cargaConfigIni(log)
configuration = cargaConfig(log)

def main():
    log.warning("##########################################",True);
    log.warning("#########-   Inicia StreamJob    -########",True);
    log.warning("##########################################",True);
    Config =  mappingConfig(log,configurationInicio)
    dt_string = datetime.today().strftime("%M")
    hora_string = datetime.today().strftime("%H:%M")
    timeSleep = configuration['time_reboot']
    s = sched.scheduler(time.time, time.sleep)
    def do_something(sc):
        try:            
            timeSleep = configuration['time_reboot']
            hora_string = datetime.today().strftime("%H:%M")
            log.warning("######################################################",True);
            log.warning(f"#########-   Inicia StreamJob {str(hora_string)} -########",True);
            log.warning("######################################################",True);
            log.warning("Entra por la funcion, time : "+str(hora_string),True,True)
            horaCerra = ""
            for list_config in Config['HojasConfig']:
                if list_config['name'] == 'Servers':
                    log.warning("#########-Obtener la informacion de la hora de Servers-########",True);
                    relations = json.dumps(list_config['relation'])
                    data = setFileListClientSheet(log,configuration['SHEET_ID'],configuration['SHEET_SERVER_INI'],configuration['SHEET_SERVER_TITTLE'],configuration['SHEET_SERVER_DATA'],json.loads(relations))
                    for item in data:
                        if int(item['server_id']) == configuration['server_id']:
                            horaCerra = item['time_reload']
                            timeSleep = item['time_reboot']
                            if item['time_reload'] == hora_string or item['reboot'] == True:
                                log.warning("Empezamos a cerrar aplicaciones aplicaciones :"+str(hora_string),True ,True)
                                apps = item['reboot_json']
                                relanzarApp(log,apps)
                                campos = []
                                for key in item:
                                    campos.append(key)
                                posicion = campos.index("reboot")
                                if item['reboot']:
                                    UpdateCelda(log,configuration['SHEET_ID'],configuration['server_id'],posicion,False)
                            else:
                                log.warning(f"valor de reboot  {item['reboot']} no se cierran las aplicaciones",True,True)
                                log.warning("Empezamos a cerrar aplicaciones aplicaciones automaticamente a las : "+str(horaCerra),True ,True)
                            break
            log.warning(f"Espere por favor {timeSleep} segundos..............................",True,True)
            s.enter(timeSleep, 1, do_something, (sc,))
        except Exception as e:
            log.error("Error en "+str(e),modul="StreamJob",display=True,dateStatus=True)
            s.enter(timeSleep, 1, do_something, (sc,))
    log.warning("Lanzamiento por time_reload, Hora: "+hora_string,True,True)
    s.enter(0.1, 1, do_something, (s,))
    s.run()

def main1():
    try:
        Config =  mappingConfig(log,configurationInicio)
        dt_string = datetime.today().strftime("%M")
        hora_string = datetime.today().strftime("%H:%M")
        countMinutos = ((int(dt_string) // (configuration['time_reboot']/60))+1 ) * (configuration['time_reboot']/60)
        while(True):  # Bucle infinito
            cargaHoraSub = True
            typoSend = True
            log.info("~~~~~~~~~Esperando minuto :"+str(countMinutos)+"~~~~~~~")
            while(cargaHoraSub):
                now = datetime.today()
                dt_string = now.strftime("%M")
                if countMinutos == int(dt_string) or datetime.today().strftime("%H:%M") == configuration['time_reload']:
                    cargaHoraSub = False
                    if datetime.today().strftime("%H:%M") == configuration['time_reload']:
                        typoSend = True
                    else:
                        typoSend = False
                    log.warning("~~~~~~~Acaboron los "+str(configuration['time_reboot']/60)+" min~~~~~~~~",True,True)
            if typoSend:
                log.warning("Lanzamiento por time_reload, Hora: "+datetime.today().strftime("%H:%M"),True,True)
                cargaHoraSub = True
            else:
                log.warning("Entra por Reboot, minuto: "+str(countMinutos),True,True)
                for list_config in Config['HojasConfig']:
                    if list_config['name'] == 'Servers':
                        relations = json.dumps(list_config['relation'])
                        data = setFileListClientSheet(log,configuration['SHEET_ID'],configuration['SHEET_SERVER_INI'],configuration['SHEET_SERVER_TITTLE'],configuration['SHEET_SERVER_DATA'],json.loads(relations))
                        for item in data:
                            if int(item['server_id']) == configuration['server_id']:
                                if item['reboot'] == True:
                                    apps = [{'name':'StreamMain.exe','time' : 60},{'name':'StreamRouter.exe','time' : 60},{'name':'StreamDirector.exe','time' : 60}]
                                    relanzarApp(log,apps)
                                break
                cargaHoraSub = True
            now = datetime.today()
            dt_string = now.strftime("%M")
            countMinutos = int(dt_string)+(configuration['time_reboot']/60)
            if countMinutos >= 60:
                countMinutos = (configuration['time_reboot']/60)
                
    except Exception as e:
        log.error(str(e),"main",True,True)

def relanzarApp(log,apps):
    log.warning("Relanzar Apps: ",True,True)
    for list_app in apps:
        if is_running(log,list_app['name']):
            is_running(log,list_app['name'],True)
            log.warning("##########################################",True);
            log.warning(f"Esperamos {list_app['time']} segundos para continuar",True,True)
            log.warning("##########################################",True);
            time.sleep(list_app['time']) 
    log.warning("Termina Relanzar Apps",True,True)


def is_running(log,scriptName,kill= False,sleepClose = 20):
    if not kill:
        for q in psutil.process_iter():
            if q.name().startswith(scriptName):
                return True
        log.warning(f"No se encontro la aplicacion  {scriptName} ejecutada",True,True)
        return False
    else:
        for q in psutil.process_iter():
            if q.name().startswith(scriptName):
                if kill:
                    children = q.children(recursive=True)
                    if children != []:
                        for child in children:
                            try:
                                p = psutil.Process(child.pid)
                                p.kill()
                                log.warning("Cierra subproceso "+str(child),True,True)
                            except psutil.NoSuchProcess as e:
                                children = q.children(recursive=True)
                                log.warning("##########################################",True);
                                log.warning("*Warning "+str(e),True,True)
                                continue
                            except Exception as e:
                                log.error("Error en is_running "+str(e),True,True);
                    else :
                        try:
                            q.kill()
                            log.warning("Cierra programa "+scriptName,True,True)
                        except psutil.NoSuchProcess as e:
                            log.warning("##########################################",True);
                            log.warning("*Warning "+str(e),True,True)
                            continue
                        except Exception as e:
                            log.error("Error en is_running "+str(e),True,True);
        

callProgram(log,configuration['pathfile']+'StreamConfig.exe')
main()