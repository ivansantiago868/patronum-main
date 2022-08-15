import requests
# import json

# # Definimos la URL
# url = "http://localhost:8087/API/V1/Grial/ReactionPublication/get"

# Definimos la cabecera y el diccionario con los datos
cabecera1 = {'Content-type': 'application/json'}
#Extrae de la base de datos los AliasSh
def POSTAliasSh(logging,url, request):
    logging.info("Iniciando metodo POST http_service.py POST"+"URL: "+str(url)+"  Request:  "+str(request),True, True)
    solicitud = None
    try:
        solicitud = requests.post(url, headers=cabecera1, data=request)
    except ConnectionRefusedError as e:
        solicitud = {'status_code' : 404}
        logging.error( "ConnectionRefusedError: " + str(e), 'http_service.py', 'POST')
    except OSError as e:
        solicitud = {'status_code': 408}
        logging.error( "OSError: " + str(e), 'http_service.py', 'POST')
    except Exception as e:
        solicitud = {'status_code': 500}
        logging.error( "Exception: "+str(e), 'http_service.py', 'POST')
    except:
        solicitud = {'status_code': 500}
        raise
    return solicitud

#Extrae de la base de datos los Sh
def sendSH(logging,url, request):
    solicitud = None
    try:
        solicitud = requests.post(url, json={'clients': request})
    except ConnectionRefusedError as e:
        solicitud = {'status_code' : 404}
        logging.error("ConnectionRefusedError: " + str(e))
    except OSError as e:
        solicitud = {'status_code': 408}
        logging.error("OSError: " + str(e))
    except Exception as e:
        solicitud = {'status_code': 500}
        logging.error("Exception: "+str(e))
    except:
        solicitud = {'status_code': 500}
        raise

    return solicitud

#Extrae de la base de datos los post
def POSTAT(logging,url, request):
    solicitud = None
    try:
        solicitud = requests.post(url, json=request)
    except ConnectionRefusedError as e:
        solicitud = {'status_code' : 404}
        logging.error("ConnectionRefusedError: " + str(e))
    except OSError as e:
        solicitud = {'status_code': 408}
        logging.error("OSError: " + str(e))
    except Exception as e:
        solicitud = {'status_code': 500}
        logging.error("Exception: "+str(e))
    except:
        solicitud = {'status_code': 500}
        raise

    return solicitud

# def POST(logging,url, request):
#     solicitud = None
#     try:
#         solicitud = requests.post(url, json={'tweet': request})
#     except ConnectionRefusedError as e:
#         solicitud = {'status_code' : 404}
#         logging.error("ConnectionRefusedError: " + str(e))
#     except OSError as e:
#         solicitud = {'status_code': 408}
#         logging.error("OSError: " + str(e))
#     except Exception as e:
#         solicitud = {'status_code': 500}
#         logging.error("Exception: "+str(e))
#     except:
#         solicitud = {'status_code': 500}
#         raise

#     return solicitud





# def sendSHaccount(logging,url, request):
#     logging.info("Iniciando metodo POST ")
#     logging.info("URL: "+str(url))
#     logging.info("Request:  " +str(requests))
#     solicitud = None
#     try:
#         solicitud = requests.post(url, json={'client_id': request})
#     except ConnectionRefusedError as e:
#         solicitud = {'status_code' : 404}
#         logging.error("ConnectionRefusedError: " + str(e))
#     except OSError as e:
#         solicitud = {'status_code': 408}
#         logging.error("OSError: " + str(e))
#     except Exception as e:
#         solicitud = {'status_code': 500}
#         logging.error("Exception: "+str(e))
#     except:
#         solicitud = {'status_code': 500}
#         raise

#     return solicitud

# def saveSHaccount(logging,url, sh_id, client_id, account, account_id):
#     logging.info("Iniciando metodo POST ")
#     logging.info("URL: "+str(url))
#     logging.info("Request:  " +str(requests))
#     solicitud = None
#     try:
#         solicitud = requests.post(url, json={'stakeholder_id': sh_id, 'client_id': client_id, 'account': account, 'account_id':account_id})
#     except ConnectionRefusedError as e:
#         solicitud = {'status_code' : 404}
#         logging.error("ConnectionRefusedError: " + str(e))
#     except OSError as e:
#         solicitud = {'status_code': 408}
#         logging.error("OSError: " + str(e))
#     except Exception as e:
#         solicitud = {'status_code': 500}
#         logging.error("Exception: "+str(e))
#     except:
#         solicitud = {'status_code': 500}
#         raise

#     return solicitud

# #response = POST(url,datos)
# #if response.status_code == 200:
#     #print("Message: "+str(response.__dict__))
#     #print("Message: " + str(response.text))

#     #text = str(response.text)
#     #listR = response.json()
#     #print("Json: "+listR['Message'])
#     #ids = filter(lambda x: x['provider_id'] != "",listR['reactions'])
#     #print("OK.............."+list(ids))
