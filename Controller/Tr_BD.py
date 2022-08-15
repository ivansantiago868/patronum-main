import json
import psycopg2
import uuid
from Utilities.utils import cargaConfig
from datetime import date
from Utilities.utils import encontrarFormatoFecha, dateToStringLocal, dateUtc, epochToDateStr, datetimeToStr

#Clase de la base de datos
class Tr_BD(object):
    name:str
    server: str
    database: str
    username: str
    password: str
    port : str
    
    def __init__(self, log,nameBd):
        try:
            self.log = log
            self.name = nameBd
            configuration = cargaConfig(log)
            self.server = configuration[nameBd+"_url"]
            self.database = configuration[nameBd+"_bd"]
            self.username = configuration[nameBd+"_user"]
            self.password = configuration[nameBd+"_pass"]
            self.port = str(configuration[nameBd+"_port"])
            self.conectar()
        except Exception as e:
            self.log.error("Error=>Tr_BD en Tweet => %s __init__" % (e),True,True)

    def conectar(self):
        try:
            self.log.info(msn="conectado a "+self.name,display=True,dateStatus=False)
            self.connect = psycopg2.connect("host="+ self.server +" port="+ self.port +" dbname="+ self.database +" user=" + self.username \
            +" password="+ self.password)
            
            # Create a cursor object
            self.cursor = self.connect.cursor()
        except Exception as e:
            self.log.error("Error=>Tr_BD en Tweet => %s conectar" % (e),True,True)
        
    #Método para guardar en la base de datos, dependiendo d esi es tweet o rss
    def setTweetandRss(self, body,bodyJson):
        try:
            today = date.today()
                #Aqui vamos a consultar los datos
            if body['type'] == "twitter":
                created_at = body["data"]["created_at"]
                created_at_utc = epochToDateStr(encontrarFormatoFecha(body["data"]["created_at"],'epoch'),'%a %b %d %H:%M:%S %Y')
                id_tweet = body["data"]["id"]
                text = body["data"]["text"]
                id_str = body["data"]["user"]["id"]
                user_screen_name = body["data"]["user"]["screen_name"]
                user_profile_image = body["data"]["user"]["profile_image_url"]
                tweet_url =  "https://twitter.com/LeonidasEsteban/status/"+str(body["data"]["id"])
                hashtags = []
                tweet_container_url = []
                user_mention_id = []
                user_mention_sc = []
                valida_sh = body['valida_sh']
                bk_full = body['bk_full']
                bk_send = body['bk_send']
                day = today.day
                month = today.month
                year = today.year
                client_id = body['client_id']
                modulo = body['modulo']

                if "user_mentions" in body["data"]["entities"]:
                    for usr_mentions in body["data"]["entities"]["user_mentions"]:
                        user_mention_id.append(usr_mentions["id_str"])
                        user_mention_sc.append(usr_mentions["screen_name"])

                if len(body["data"]["entities"]["hashtags"]) > 0:
                    for items in body["data"]["entities"]["hashtags"]:
                        hashtags.append("#" + items["text"])
                
                if len(body["data"]["entities"]["urls"]) > 0:
                        tweet_container_url.append(body["data"]["entities"]["urls"][0]["expanded_url"])

                if "extended_tweet" in body["data"]:
                    text = body["data"]["extended_tweet"]["full_text"].replace("'", '')
                
                if body["data"]["retweeted"] == False and body["data"]["in_reply_to_status_id_str"] == None:
                        retweeted = False
                        Tweet = True
                        replay = False
                elif body["data"]["retweeted"] == False and body["data"]["in_reply_to_status_id_str"] != None:
                    retweeted = False
                    Tweet = False
                    replay = True
                else:
                    retweeted = True
                    Tweet = False
                    replay = False
                jsonData = json.dumps(body).replace("'", '"')
                giud_id = str(uuid.uuid4())
                text = text.replace("'", '')
                columnas = "giud_id, user_id, screen_name, profile_image, tweet_id, created_at, tweet_text, retweet, tweet, hashtags, tweet_container_url, user_mention_id, user_mention_sc, reply, json, dia, mes, año, client_id, modulo, valida_sh, bk_full, bk_send, tweet_url, created_at_utc"
                query = f"INSERT INTO tweets ({columnas}) VALUES('{giud_id}','{id_str}', '{user_screen_name}', '{user_profile_image}', '{id_tweet}', '{created_at}', '{text}', '{retweeted}', '{Tweet}', '{json.dumps(hashtags)}', '{json.dumps(tweet_container_url)}', '{json.dumps(user_mention_id)}', '{json.dumps(user_mention_sc)}', {replay},'{jsonData}', '{day}', '{month}', '{year}', '{client_id}', '{modulo}', {valida_sh}, {bk_full}, {bk_send}, '{tweet_url}', '{created_at_utc}');"
                self.cursor.execute(query)
                self.connect.commit()
            elif  body['type'] == "rss":
                authors = body["data"]["author"].replace("'", "")
                Title = body["data"]["title"].replace("'", "")
                Url = body["data"]["url"] 
                Summary =  body["data"]["summary"] .replace("'", "")
                Published_date =  body["data"]["published"]
                day = today.day
                month = today.month
                year = today.year
                client_id = body['client_id']
                modulo = body['modulo']
                id_str = body["data"]["id_str"]
                giud_id = str(uuid.uuid4())
                columnas = "giud_id, id_str, autor, published_date, title, url, text_summary, dia, mes, año, client_id, modulo"
                query = f"INSERT INTO rss({columnas}) VALUES('{giud_id}','{id_str}','{authors}', '{Published_date}','{Title}','{Url}','{Summary}', '{day}', '{year}', '{month}', '{client_id}', '{modulo}')"
                self.cursor.execute(query)
                self.connect.commit()
            elif  body['type'] == "facebook":
                giud_id = str(uuid.uuid4())
                id_str = body["data"]["id_str"]
            self.log.info(msn=body['type']+":insert a "+giud_id+" str_id="+str(id_str)+'-'+str(body['client_id']),display=True,dateStatus=False)
            return True
        except Exception as e:
            self.log.error("Error=>setTweetandRss en %s => %s query => %s" % (body['type'],e,query),True,True)
            self.conectar()
            return False
    
    def getTweets(self):
        query = "SELECT * FROM tweets "
        self.cursor.execute(query)
        self.connect.commit()
        tweets_records = self.cursor.fetchall()
        self.numtweets = len(tweets_records)
        return tweets_records

    def end(self):
        del self.connect
        del self.cursor


