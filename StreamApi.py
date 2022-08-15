from flask import Flask , request , Response
from flask_cors import CORS
from Entity.Publics import client
from Utilities.drive  import driverClass
from Utilities.log import log_file
from Utilities.utils import JsonToObject, cargaConfig, cargaConfig_twitter_credentials, cargaConfigIni 
import json
import twarc
from Entity.StdOutListener import StdOutListenerClass
import Controller.SuperMetricsController as superMetrics
from Controller.manage_tweet import routerTwette , EnvioManual
from Controller.FilesController import getListChannelByStakeholderAll_facebook,  getListChannelByStakeholderAll, getListPortsByClientAll
from Utilities.mq import mqClass 
from Controller.Tr_BD import Tr_BD
from Controller.DriveControler import getFileListClient


app = Flask(__name__)
# app.config['DEBUG'] = True
# app.config.update(
#     DEBUG=True,
#     SECRET_KEY='...'
# )


cors = CORS(app, resources={r"/Api/*": {"origins": "*"}})
log = log_file("C:\Log\Stream\StreamApi.log")
configuration = cargaConfig(log )
listCliente = getFileListClient(log , configuration)
configurationInicio = cargaConfigIni(log)
mq1 = mqClass(log)
mq1.declare(configuration['bk_telegram'])


@app.route('/')
def main():
    return "Hola Mundo Inicia el servidor"

@app.route('/Api/Mensajes' , methods=["POST"])
def getMensajes():
    if request.method == "POST":
        log.info("Peticion recibida" , True,  True)
        try:
            reporte = []
            reporte.append(request.values['cliente'])
            reporte.append(request.values['tipo'])
            reporte.append(request.values['url']) 
            reporte.append(request.values['autor'])
            reporte.append(request.values['estado'])
            reporte.append(request.values['mensaje'])
            log.info("Data : %s" % (reporte) , True,  True)
            if reporte[1].lower() == "twitter":
                configCredential = cargaConfig_twitter_credentials(log)
                print(configCredential)
                consumer_key = configCredential['CONSUMER_KEY'] #Config.twitter_credentials.CONSUMER_KEY
                consumer_secret = configCredential['CONSUMER_SECRET'] #Config.twitter_credentials.CONSUMER_SECRET
                access_token = configCredential['ACCESS_TOKEN'] #Config.twitter_credentials.ACCESS_TOKEN
                access_token_secret = configCredential['ACCESS_TOKEN_SECRET'] #Config.twitter_credentials.ACCESS_TOKEN_SECRET
                log.info("twitter " , True,  True)
                tw = twarc.Twarc(consumer_key, consumer_secret, access_token, access_token_secret)
                tweet_id = reporte[2]
                tweet_id = tweet_id.split('/')
                tweet_id = tweet_id[-1]
                tweet = tw.get('https://api.twitter.com/1.1/statuses/show/%s.json' % tweet_id)
                tweet_json = tweet.json()
                tweet_json['text'] =tweet_json['full_text'] 
                tweet_str  = json.dumps(tweet_json, indent=2)
                tweet = {"type":"twitter","data":json.loads(tweet_str)}
            elif reporte[1].lower() == 'facebook':
                log.info("facebook" ,True,  True)
                tweet = {"type":reporte[1].lower(),"data":{"account":reporte[1], "id_str":"" , "Created time":""}}
            else:
                log.info("rss" ,True,  True)
                tweet = {"type":"rss","data":{"account":"", "id_str":"" , "Created time":"" , "author":reporte[3] , "title":"" , "url": reporte[2] , "sumary":"","summary":"" ,  "published":"" }}
            clients = listCliente
            resp = EnvioManual(log , configuration , tweet  , mq1, clients  ,reporte)

            log.info("respuesta %s" % (resp["Mensaje"]) ,True,  True)
            if resp['status'] == 200: 
                return { "Mensaje":resp['Mensaje'] , "status" : 200}
            else: 
                return { "Mensaje":resp['Mensaje'] , "status" :400}
            #Envia  al cola 
            # mq1.add(json.dumps(send_Data),listport[0].name
            #routerTwettereporte[1]reporte[1]
        except Exception as e:
            log.error(" %s %s" % (str(e)),True,True)
            return { "Mensaje":str(e) , "status" :400}
    #Este nos servira para traer mensajes
@app.route('/Api/listar' , methods=["POST"])
def listmessages():
    try:
        bd = Tr_BD(log , "catrina")
        tweets_records = bd.getTweets()
        return { "Mensaje":tweets_records, "status" :200}
    except Exception as e:
        return { "Mensaje":str(e) , "status" :400}
        

@app.route('/Api/getClient' , methods=["POST"])
def getClient():
    try:
        client = listCliente
        name_proyect , idCliente = [] , []
        for cliente in client:
            name_proyect.append(cliente['name_proyect'])
            idCliente.append(cliente['client_id'])
        return { "name":name_proyect , "idCliente":idCliente}
    except Exception as e:  
        return { "Mensaje":str(e) , "status" :400}


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5000)
#host='0.0.0.0'