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
phone_number = [client["phone"] for client in clients.find()]
message = '''
⭐️ <b>Enjoying our service?</b> ⭐️

The <b>creator of this Bot</b> 🧠 is presenting a <b>free ChatGPT webinar</b> 👨🏼‍🏫

Made for both Students 👨🏼‍🎓 and Professionals 📈

Boost Your productivity and Success Now: whether it's at work 🧑🏽‍💻 or at school 🏫

📅 Date: July 8th
⏰ Time: 11:00 AM to 12:30 PM

Secure your spot now at: www.teachx.me/chatgpt
  
<b>Can't make it or have other queries</b>? Use /contact command
'''

message = '''
🚨 Kindly be reminded to choose as <b>many slots as possible</b> when you click on the link after pressing /choose_session

😀 This is the maximise our probability of booking a slot for you.
'''

# lst_ids = [495589406]
for id in lst_ids:
    print(id)
    requests.get("https://api.telegram.org/bot5641356025:AAFhotXRyhkUXWcFBXhSN78gs0Hk9AjPpNY/sendMessage?parse_mode=HTML&chat_id="+str(id)+"&text="+message)

# remove '' from the list phone_number
# phone_number = [x for x in phone_number if x != '']
# print(len(phone_number))
# print(phone_number)
