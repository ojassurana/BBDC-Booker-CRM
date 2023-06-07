from pymongo import MongoClient
import time
from datetime import datetime

uri = "mongodb+srv://cluster0.mqlx5ut.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
mongo = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='ojas.pem')
users = mongo['Users']
clients = users['clients']
total_credits = sum([client['credits'] for client in clients.find()])
total_credits_used = sum([client['credits_used'] for client in clients.find()])

print("Time:_____________________________")
print("Date and time right now: ", datetime.now())
print("Unix time now: ", time.time())
print()
print("Credits:__________________________")
print("Total credits: ", total_credits)
print("Total credits used: ", total_credits_used)
print()




# import csv

# csv_file = 'payments.csv' # Format should be id,Created (UTC),Amount,Fee,Customer ID.
# fee_total = 0
# amount_total = 0

# with open(csv_file, 'r') as file:
#     reader = csv.DictReader(file)
#     for row in reader:
#         fee = float(row['Fee'])
#         fee_total += fee
#         amount_total += float(row['Amount'])

# # print('Total Number of transactions: ', reader.line_num - 1)
# print(f"The total value of all the fees is: ${fee_total:.2f}")
# # print(f"The total of credits is: {amount_total/9:.2f}")