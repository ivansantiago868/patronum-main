from Utilities.utils import cargaConfig
from Utilities.log import log_file
import os, shutil
from Controller.FilesController import getAliasSH, getInterestMonibotWords, getFileChannelByStakeholder,getFileConfigByClient, getListModelo_InteresCompuesto 
from Controller.DriveControler import  setFileListClient,setFileListShGeneral, setFileListShClient,setFileListInteresClient,createFilesProgram, setFileListExceptionsClient,setFileListQuerysClient, setFileListInteresCompuesto
from Utilities.theread import callProgram


#Función que borra los archivos de los clientes, Sh, palabras de interes y palabras Excepciones 
def deletefile(log):
    folder = 'FileProcess/'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            # elif os.path.isdir(file_path):
            #     shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

#Cargará las configuraciones que esten en alrchivo config.ini
log = log_file("C:\Log\Stream\StreamFile.log")     
configuration = cargaConfig(log)
log.log_File=configuration['log']
# callProgram(log,configuration['pathfile']+'StreamLogs.exe')
# deletefile(log)
callProgram(log,configuration['pathfile']+'StreamConfig.exe')
if configuration['sheet_active']:

    #Funciones para administrar la hoja de los clientes, Sh, palabras de inters, palabras excepción
    setFileListClient(log,configuration)
    setFileListShGeneral(log,configuration)
    setFileListShClient(log,configuration)
    setFileListInteresClient(log,configuration)
    setFileListExceptionsClient(log, configuration)
    setFileListQuerysClient(log, configuration)
    setFileListInteresCompuesto(log , configuration)

#Función que creara los archivos para los Clientes, Sh, Palabras de Interes y Palabras Excepción
    createFilesProgram(log,configuration)
else:
    getAliasSH(log)
    getInterestMonibotWords(log)
    getFileChannelByStakeholder(log)
    getFileConfigByClient(log)
    getListModelo_InteresCompuesto()