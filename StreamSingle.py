import twarc
from Utilities.utils import cargaConfig, cargaConfig_twitter_credentials
from Utilities.log import log_file
from Utilities.mq import mqClass
from Utilities.theread  import threadingClass, callProgram
from Controller.manage_tweet import routerTwette
import json
import sys
from Entity.StdOutListener import StdOutListenerClass
from Controller.FilesController import  getListChannelByStakeholderAll, getListPortsByClientAll

log = log_file("C:\Log\Stream\StreamRouter.log")     
configuration = cargaConfig(log)
log.log_File=configuration['log']
sys.setrecursionlimit(10000) # 10000 is an example, try with different values

def main():
    try:
        callProgram
        log.info("iniciar",True,True)
        log.warning("#################################################",True);
        log.warning("#########-INICIANDO PYTHON STREAM SINGLE-##########",True);
        log.warning("#################################################",True);
        configCredential = cargaConfig_twitter_credentials(log)
        print(configCredential)
        CONSUMER_KEY = configCredential['CONSUMER_KEY'] #Config.twitter_credentials.CONSUMER_KEY
        CONSUMER_SECRET = configCredential['CONSUMER_SECRET'] #Config.twitter_credentials.CONSUMER_SECRET
        ACCESS_TOKEN = configCredential['ACCESS_TOKEN'] #Config.twitter_credentials.ACCESS_TOKEN
        ACCESS_TOKEN_SECRET = configCredential['ACCESS_TOKEN_SECRET'] #Config.twitter_credentials.ACCESS_TOKEN_SECRET
        tw = twarc.Twarc(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        tweet_id = configuration['tw_id']
        tweet = tw.get('https://api.twitter.com/1.1/statuses/show/%s.json' % tweet_id)
        tweet_json = tweet.json()
        tweet_json['text'] =tweet_json['full_text'] 
        tweet_str  = json.dumps(tweet_json, indent=2)
        listener = StdOutListenerClass(log,configuration)
        listener.on_data(tweet_str)
    except Exception as e:
        print(str(e))    
            
main()