from Utilities.utils import cargaConfig
from Utilities.log import log_file
from datetime import datetime, date
import sched, time
from datetime import datetime
from os import listdir
from os.path import isfile, join
import os


log = log_file("C:\Log\Stream\StreamFile.log")     
configuration = cargaConfig(log)

def main():

    Kill_Proccess()



def Kill_Proccess():

    pathfiles = configuration["pathfile"]
    listprocess = [f for f in listdir(pathfiles) if isfile(join(pathfiles, f))]

    for process in listprocess:
        if process != 'StreamFile.exe' and process != 'StreamLogs.exe':
            os.system(f"taskkill/f /im {process}")
            print(f"Proceso {process} terminado")
        
    CleanLogs()

def CleanLogs():
 
    pathFiles = "C:\\Log\\Stream"
    logfiles = [f for f in listdir(pathFiles) if isfile(join(pathFiles, f))]

    for log in logfiles:
        f = open(pathFiles + "\\" + log, 'r+')
        f.truncate(0)
        print(f"Archivo Log: {log} limpio")


main()





    






    