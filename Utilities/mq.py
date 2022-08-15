import pika
import time
from Utilities.utils import cargaConfig

class mqClass:
    def __init__(self, log):
        self.reconect(log)
        
    def reconect(self,log):
        configuration = cargaConfig(log)
        self.configuration = configuration
        self.log = log
        try:
            if configuration['mqauth']:
                self.propertis = pika.BasicProperties(
                                    delivery_mode = 2, # make message persistent
                                    expiration = "36000000",
                                )
                credentials = pika.PlainCredentials(configuration['mquser'], configuration['mqpass'])
                parameters = pika.ConnectionParameters(host=configuration['mqip'],port=configuration['mqport'],credentials=credentials,socket_timeout=10)
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
            else: 
                self.propertis = pika.BasicProperties(
                                    delivery_mode = 2, # make message persistent
                                    expiration = "36000000",
                                )
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=configuration['mqip']))
                self.channel = self.connection.channel()
        except Exception as e:
            self.log.error("__init__ => %s  " % (e),"mqClass",True,True)
    def declare(self,name):
        try:
            self.channel.queue_declare(queue=name, durable=True)
        except Exception as e:
            tipoError = type(e)
            self.log.error("declare => %s , mq => %s , except => %s" % (e,name,tipoError),"mqClass",True,True)
    def consume(self,name,callback):
        try:
            self.channel.basic_consume(queue=name, on_message_callback=callback, auto_ack=True)
            print(' [*] Esperando mensaje. Para salir CTRL+C')
            self.channel.start_consuming()
        except pika.exceptions.StreamLostError as e:
            tipoError = type(e)
            self.log.error("consume => %s , mq => %s , except => %s" % (e,name,tipoError),"mqClass",True,True,False)
            return True
        except Exception as e:
            tipoError = type(e)
            self.log.error("consume => %s , mq => %s , except => %s" % (e,name,tipoError),"mqClass",True,True)
            return False
        

    def add(self,data,name):
        try:
            self.channel.basic_publish(exchange='', routing_key=name, body=data)
            return True
        except pika.exceptions.StreamLostError as e:
            tipoError = type(e)
            self.log.error("add => %s , mq => %s , except => %s" % (e,name,tipoError),"mqClass",True,True,False)
            return False
        except pika.exceptions.ChannelWrongStateError as e:
            tipoError = type(e)
            self.log.error("add => %s , mq => %s , except => %s" % (e,name,tipoError),"mqClass",True,True,False)
            time.sleep(5)
            return False
        except Exception as e:
            tipoError = type(e)
            self.log.error("add => %s , mq => %s , except => %s" % (e,name,tipoError),"mqClass",True,True)
            return True
        
    def close(self):
        self.connection.close()

