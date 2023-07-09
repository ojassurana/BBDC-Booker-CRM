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
# get a list of phone numbers from the database
# phone_number = [client["phone"] for client in clients.find()]
# print(phone_number)
message = "⚠️ <b>REMINDER</b> ⚠️\nReminder to use /start_checking so that we can start looking for new slots for you if you haven't already done so."
lst_ids = [495589406]
for id in lst_ids:
    print(id)
    requests.get("https://api.telegram.org/bot5641356025:AAFhotXRyhkUXWcFBXhSN78gs0Hk9AjPpNY/sendMessage?parse_mode=HTML&chat_id="+str(id)+"&text="+message)
       