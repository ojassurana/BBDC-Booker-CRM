from pymongo import MongoClient
import time
from datetime import datetime
import requests

uri = "mongodb+srv://cluster0.mqlx5ut.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
mongo = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='ojas.pem')
users = mongo['Users']
clients = users['clients']
lst_ids = [client["_id"] for client in clients.find()]
message = '''
🚨REMINDER TO TOPUP ACCOUNT

BBDC's top-up system will be down from 10pm (10 June) to 10am (11 June), to ensure that we are able to continue getting slots for you, please top-up your account sufficiently !
'''
lst_ids = [495589406]
for id in lst_ids:
    print(id)
    requests.get("https://api.telegram.org/bot5641356025:AAFhotXRyhkUXWcFBXhSN78gs0Hk9AjPpNY/sendMessage?chat_id="+str(id)+"&text="+message)