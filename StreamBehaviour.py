from twarc import Twarc
from Utilities.log import log_file
from Utilities.utils import cargaConfig
import json
import codecs
from Controller.SuntzuController import SuntzuBd
from Controller.FilesController import getTweetsID

# This creates an instance of Twarc.
t = Twarc()
log = log_file("C:\Log\Stream\StreamTW.log")     
configuration = cargaConfig(log)
log.log_File=configuration['log']

SuntzuBd = SuntzuBd(log)

def main():
    tweetss = getTweetsID(log)
    for id_tweests in tweetss:
        print(f"Extrallendo numero de likes y rt del tweet {id_tweests.provider_item_id}")
        try:
            tweet = list(t.hydrate([id_tweests.provider_item_id]))[0] #ahi se pondra el id del tweet
            retweets_count = tweet["retweet_count"]
            likes_count = tweet["favorite_count"]
            SuntzuBd.setTweetsCounter(id_tweests.provider_item_id, retweets_count, likes_count)
        except:
            print("ERROR: -> Tweet borrado o Cuneta suspendida")
    
main()