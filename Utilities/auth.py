
from tweepy import OAuthHandler
import tweepy
from Utilities.log import log_file

from Utilities.utils import cargaConfig, cargaConfig_twitter_credentials

log = log_file("C:\Log\Stream\Auth.log")
configuration = cargaConfig(log)
log.log_File=configuration['log']

#Loggear aplicación de twitter
def logAuth():
    configCredential = cargaConfig_twitter_credentials(log)
    print(configCredential)
    CONSUMER_KEY = configCredential['CONSUMER_KEY'] #Config.twitter_credentials.CONSUMER_KEY
    CONSUMER_SECRET = configCredential['CONSUMER_SECRET'] #Config.twitter_credentials.CONSUMER_SECRET
    ACCESS_TOKEN = configCredential['ACCESS_TOKEN'] #Config.twitter_credentials.ACCESS_TOKEN
    ACCESS_TOKEN_SECRET = configCredential['ACCESS_TOKEN_SECRET'] #Config.twitter_credentials.ACCESS_TOKEN_SECRET
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)
    return api