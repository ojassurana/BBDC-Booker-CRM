from fastapi import FastAPI, Request, Header, Response
import os
import requests
from fastapi.middleware.cors import CORSMiddleware
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime, timedelta
from fastapi.responses import HTMLResponse
from typing import Dict, List
import time
import telegram
from telegram import constants
import stripe
from pymongo import MongoClient
import random
import string
import traceback
import json
global mongo
global users
global clients
global msg1


# API Keys: ___________________________________________________________________________________________________________
TOKEN = os.environ["TOKEN"]
stripe.api_key = os.environ["stripe_api_key"]
webhook_secret = os.environ["webhook_secret"]
mongodb_key = "ojas.pem"
heroku_url = "https:/bbdc-booker-crm.herokuapp.com"
app_script_url = os.environ["app_script_url"]
admin_id = int(os.environ['admin_id'])
price_of_each_credit = 10
# Client: ____________________________________________________________________________________________________________  
bot = telegram.Bot(TOKEN)
app = FastAPI()
uri = os.environ['mongo_url']
mongo = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='ojas.pem')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Text: ______________________________________________________________________________________________________________
msg1 = '''<u><b>What this bot does:</b></u>
We are a team of individuals who will assist in booking your BBDC practical lessons slots based on your given schedule.

✅ <b>Supported</b>: Class 3/3A Practical lessons
❌ <b>Not supported</b>: FTT/BTT/TPDS/DS

<u><b>Pricing:</b></u>
1 credit will be deducted for every practical slot booked.
See /credits command for more information.

<u><b>How to use:</b></u>
1. Use /setlogin command to update your BBDC username and password.
2. Add bot credits with /credits command.
3. Use the /choose_session command to select the practical sessions you are available for.
4. Use the /start_checking command to start checking for new slots. We will automatically do it for you and inform you if you got a slot. Use the /stop_checking command to stop checking for new slots.
5. The bot will notify you once a slot is found and booked for you.

<u><b>Note:</b></u>
Use /contact for any queries or issues.
In case there are any issues, we will contact you immediately on WhatsApp.
⚠️ <b>Remember to keep your BBDC Balance TOPPED UP or we will be unable to book slots for you</b>
'''
msg3 = '''
<b><u>Your bot credits:</u></b>
Available Credits: {credits}
Credits used: {credits_used}

<b><u>Pricing:</u></b>
You can buy bot credits for $10/credit.\nWhenever you purchase a slot successfully, one credit will be deducted from your account.\nIf you resell any of the slots you've purchased, you won't get a refund for the credits used.

<b><u>How to top-up credits?</u></b>
1. Visit the link below, determine the amount of credits you wish to purchase and proceed to pay with PayNow.
2. After payments, credits are immedately added to your account.

<b><u>Link:</u></b>
https://buy.stripe.com/{product_payment_code}?client_reference_id={random_id}

🆘 Need help? Use the /contact command to get support.
'''
# Functions: _________________________________________________________________________________________________________
users = mongo['Users']
clients = users['clients']
admin = users['admin']

def retract_booking_validator(input_str):
    input_list = input_str.split(" ")
    if len(input_list) != 3:
        return False
    command, user_id, booking_id = input_list[0], input_list[1], input_list[2]
    if command != "/retract_booking":
        return False
    if len(user_id) != 4:
        return False
    if len(booking_id) != 4:
        return False
    return [user_id, booking_id]


def view_booking_history_validator(input_str):
    input_list = input_str.split(" ")
    if len(input_list) != 2:
        return False
    command, user_id = input_list
    if command != "/view_booking_history":
        return False
    if len(user_id) != 4:
        return False
    return user_id


def send_appscript_request(data):
    try:
        bro = requests.get(app_script_url, params=data)
    except:
        traceback.print_exc()


async def slot_checker(session_choice, slot, date):
    session_timings = {
    1: '0730',
    2: '0920',
    3: '1130',
    4: '1320',
    5: '1520',
    6: '1710',
    7: '1920',
    8: '2110'
    }
    today = datetime.today().strftime('%d-%m-%y')
    date = datetime.strptime(date, '%d-%m-%y').strftime('%Y-%m-%d')
    if date not in session_choice:
        return False 
    if int(slot) not in session_choice[date]:
        return False
    session_timing = datetime.strptime(session_timings[int(slot)], '%H%M')
    timing_before = (session_timing - timedelta(hours=2, minutes=30)).time()
    today = datetime.today().date()
    current_time = datetime.now().time() 
    date = datetime.strptime(date, '%Y-%m-%d').date()
    if date == today and current_time > timing_before:
        return False

    return True


def get_info_validator(input_str):
    input_list = input_str.strip().split()
    if len(input_list) != 2:
        return False
    command, user_id = input_list
    if command != "/get_info":
        return False
    if len(user_id) != 4:
        return False
    return user_id



async def update_state_admin(chat_id, major, minor):
    admin.update_one({"_id": chat_id}, {"$set": {"state.major": major, "state.minor": minor}})


def book_slot_validator(input_str):
    input_list = input_str.strip().split(" ")
    if len(input_list) != 4:
        return False
    command, user_id, slot, date = input_list
    if command != "/book_slot":
        return
    if len(user_id) != 4:
        return False
    if slot.isdigit() == False:
        return False
    if int(slot)>8 or int(slot)<1:
        return False
    try:
        datetime.strptime(date, '%d-%m-%y')
    except:
        return False
    return [user_id, slot, date]
     



def top_up_validator(input_str):
    input_list = input_str.strip().split()
    if len(input_list) != 2:
        return False
    command, user_id = input_list
    if command != "/top_up":
        return False
    if len(user_id) != 4:
        return False
    return user_id


def wrong_login_validator(input_str):
    input_list = input_str.strip().split()
    if len(input_list) != 2:
        return False
    command, user_id = input_list
    if command != "/wrong_login":
        return False
    if len(user_id) != 4:
        return False
    return user_id



def user_group_validator(input_str):
    input_list = input_str.split(" ")
    if len(input_list) != 3:
        return False
    user_id, group_id = input_list[1], input_list[2]
    if len(user_id) != 4:
        return False
    if len(group_id) != 5:
        return False
    if group_id[0] != "G":
        return False
    if group_id[1] not in ["6", "8", "9"]:
        return False
    if not group_id[2:].isdigit():
        return False
    return [user_id, group_id]



def user_test_validator(input_str):
    input_list = input_str.split(" ")
    if len(input_list) != 3:
        return False
    user_id, test = input_list[1], input_list[2]
    if test.lower() == "none":
        return [user_id, "None"]
    if len(user_id) != 4:
        return False
    try:
        datetime.strptime(test, '%d-%m-%y')
    except:
        return False
    return [user_id, test]



def session_is_empty(session_choices):
    if session_choices == {} or session_choices == None or session_choices == []: 
        return True
    for date, sessions in session_choices.items():
        if date >= datetime.now().strftime("%Y-%m-%d"):
            return False
    return True


def generate_table_history(booking_history):
    output = ""
    for document in booking_history:
        date = document["date"]
        session = document["slot"]
        booking_id = document["booking_id"]
        output += f"<b>Date: </b>{date}\n<b>Session Number:</b>{session}\n<b>Booking ID: </b> {booking_id}\n-------\n"
    return output



def generate_table(data_dict):
    # Create the header row
    header = "<b>Date:</b>             |<b>Sessions:</b>"

    # Create the separator row
    separator = "-" * len(header)

    # Combine the header and separator rows
    table = f"{header}\n{separator}"

    # Iterate over the data dictionary and add each row to the table
    for date, session_data in data_dict.items():
        # Convert the session data to a comma-separated string
        session_str = ", ".join(str(s) for s in session_data)

        # Add the row to the table
        table += f"\n{date}\t\t| {session_str}"

    return table



async def top_up(amount, client_reference_id, stripe_id, time):
    credits = amount/price_of_each_credit
    to_add = {"amount": amount, "stripe_id": stripe_id, "time": time, "credits": credits}
    clients.update_one({"random_id": client_reference_id}, {"$push": {"topup_history":  to_add}})
    clients.update_one({"random_id": client_reference_id}, {"$inc": {"credits": credits}})
    message = "<b>Top-up notification</b>:\n\n<b>Top-up credits:</b> " + str(int(credits)) + " credits have been added to your account\n<b>Amount paid:</b> $"+str(amount)+"\n\nThank you for your purchase! You made use /credits to check your total amount of credits."
    telegram_id = clients.find_one({"random_id": client_reference_id})["_id"]
    await send_text(telegram_id, message)
    await send_text(telegram_id, "Next steps:\n1. Please make use of /choose_session to choose which driving sessions you are free for.\n2. Use /start_checking to start checking for available driving sessions.")


async def update_session_choices(user_id, sessions):
    clients.update_one({"random_id": user_id}, {"$set": {"session_choices": sessions}})
    


async def send_text(chat_id, message_text):
    await bot.send_message(chat_id, message_text, parse_mode=telegram.constants.ParseMode.HTML, disable_web_page_preview=True)



async def update_state_client(chat_id, major, minor):
    clients.update_one({"_id": chat_id}, {"$set": {"state.major": major, "state.minor": minor}})


async def update_state_admin(chat_id, major, minor):
    admin.update_one({"_id": chat_id}, {"$set": {"state.major": major, "state.minor": minor}})


async def update_info_payload(chat_id, key, pair):
    clients.update_one({"_id": chat_id}, {"$set": {str("info_payload."+key): pair}})


async def info_payload_reset(chat_id):
    clients.update_one({"_id": chat_id}, {"$set": {"info_payload": {}}})


async def info_payload_reset_admin(chat_id):
    admin.update_one({"_id": chat_id}, {"$set": {"info_payload": {}}})


async def update_client_info_from_payload(chat_id, info_payload):
    for key in info_payload:
        clients.update_one({"_id": chat_id}, {"$set": {str(key): info_payload[key]}})


async def send_options_buttons(chat_id, text, options):
    buttons = []
    for option in options:
        buttons.append(InlineKeyboardButton(text=option, callback_data=option))
    keyboard = [buttons]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)





async def setlogin_handler(chat_id, client_status, update):
    if client_status['state']['minor'] == 1 and update.message and update.message.text:
        text = update.message.text
        await update_info_payload(chat_id, "username", text)
        await send_text(client_status['_id'], "The system has received your username, if any changes are needed, please use /re_enter commmand")
        await send_text(client_status['_id'], "Please enter your BBDC <b>password</b>:")
        await update_state_client(client_status['_id'], 1, 2)
    elif client_status['state']['minor'] == 2 and update.message and update.message.text:
        text = update.message.text
        await update_info_payload(chat_id, "password", text)
        await send_text(client_status['_id'], "The system has received your password, if any changes are needed, please use /re_enter commmand.")
        await send_options_buttons(client_status['_id'], "Are you booking Class 3A or Class 3 practical slot?\nClick on the button below 👇🏼",["Class 3A", "Class 3"])
        await update_state_client(client_status['_id'], 1, 3)
    elif client_status['state']['minor'] == 3 and update.callback_query and update.callback_query.data:
        text = update.callback_query.data
        if text == "Class 3A":
            await update_info_payload(chat_id, "type", "3A")
        elif text == "Class 3":
            await update_info_payload(chat_id, "type", "3")
        else:
            await send_text(chat_id, "Please select an option instead!")
            return False
        await update_state_client(client_status['_id'], 1, 4)
        reply_keyboard = [[KeyboardButton("Share Phone Number 📞", request_contact=True)]]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await send_text(client_status['_id'], "The system has received your license type, if any changes are needed, please use /re_enter commmand.")
        await bot.send_message(chat_id, text="Click the button below to share your 📞 contact details\nThis is so that we can contact you if there are any issues.", reply_markup=markup)
    elif client_status['state']['minor'] == 4 and update.message.contact != None:
        await update_state_client(client_status['_id'], 0, 0)
        await update_info_payload(chat_id, "phone", update.message.contact.phone_number)
        info_payload = clients.find_one({'_id': chat_id})['info_payload']
        await update_client_info_from_payload(chat_id, info_payload)
        await info_payload_reset(chat_id)
        await bot.send_message(chat_id=update.message.chat_id, text="Your BBDC username and password has been updated! If any changes are needed, please use the /setlogin command.", reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=update.message.chat_id, text="You may now use the /credits command to top-up your credits so that we can book slots for you.")
        if client_status["group"] == "": # Yet to set the group
            await send_text(admin_id, "A new user has been added to the database.\n<b>Database ID is:</b> " + client_status['random_id'])
        send_appscript_request({'method': "setLogin", 'username': info_payload['username'], 'password': info_payload['password'], 'type': info_payload["type"], 'phone': update.message.contact.phone_number, "id": client_status['random_id']})
    else:
        await send_text(chat_id, "Please enter a valid input")


@app.post("/telegram")
async def echo(request: Request):
    try:
        update_data = await request.json()
        update = telegram.Update.de_json(update_data, bot)
        if update.message:
            chat_id = update.message.chat_id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat_id
        else:
            await send_text(chat_id, "Your message type isn't supported.")
            return {"status": "ok"}
        if clients.find_one({'_id': chat_id}):
            client_status = clients.find_one({'_id': chat_id})
            if client_status['state']['major'] == 0:
                if update.message:
                    if "/start" == update.message.text :
                        await send_text(chat_id, msg1)
                    elif "/setlogin" == update.message.text:
                        await send_text(chat_id, "Please enter your BBDC <b>username</b>:")
                        await update_state_client(chat_id, 1, 1)
                    elif "/cancel" == update.message.text:
                        await send_text(chat_id, "Your current procedure has been cancelled.")
                        await update_state_client(chat_id, 0, 0)
                        await info_payload_reset(chat_id)
                        return {"status": "ok"}
                    elif "/credits" == update.message.text:
                        if client_status['username'] == "":
                            await send_text(chat_id, "Please set your login details first using the /setlogin command")
                        else:
                            credits = client_status['credits']
                            credits_used = client_status['credits_used']
                            random_id = client_status['random_id']
                            product_payment_code = "fZe9Dv49I1ICdFu5kk"
                            await send_text(chat_id, msg3.format(credits=credits, credits_used=credits_used, random_id=random_id, product_payment_code=product_payment_code))
                    elif "/choose_session" == update.message.text:
                        # checks if client has credits
                        if client_status['credits'] < 1:
                            await send_text(chat_id, "⚠️ You do not have enough credits to book a session. Please top up your credits using the /credits command first") 
                            return {"status": "ok"}
                        else:
                            await send_text(chat_id, "Click on the following link to let us know your availible timings:\n  <a href='https://bbdcbot.s3.ap-southeast-1.amazonaws.com/index.html?id="+client_status['random_id']+"'>Click Here</a>")
                            return {"status": "ok"}
                    elif "/start_checking" == update.message.text:
                        if client_status["checking"] == True:
                            await send_text(chat_id, "You are already in the queue for checking. Please wait for the next available slot.")
                            return {"status": "ok"}
                        else:
                            if client_status['credits'] < 1:
                                await send_text(chat_id, "⚠️ You do not have enough credits to book a session. Please top up your credits using the /credits command first") 
                                return {"status": "ok"}
                            else:
                                if session_is_empty(client_status['session_choices']):
                                    await send_text(chat_id, "You have not selected any session. Please use the /choose_session command to select a session first.")
                                    return {"status": "ok"}
                                else:
                                    await send_text(chat_id, "We have started looking for sessions for you. If you wish to make any changes, use the /choose_session commmand. The following are the sessions you have selected to choose from:")
                                    await send_text(chat_id, generate_table(client_status['session_choices']))
                                    await bot.send_photo(chat_id=chat_id, photo="https://bbdcbot.s3.ap-southeast-1.amazonaws.com/Timings.png", caption="Please note the timings of each session.")
                                    clients.update_one({'_id': chat_id}, {'$set': {'checking': True}})
                                    return {"status": "ok"}
                    elif "/stop_checking" == update.message.text:
                        if client_status['checking'] == False:
                            await send_text(chat_id, "You are not in the queue for checking. Please use the /start_checking command to start checking for sessions.")
                            return {"status": "ok"}
                        else:
                            await send_text(chat_id, "We have stopped looking for sessions for you. Please use /start_checking again to book sessions.")
                            clients.update_one({'_id': chat_id}, {'$set': {'checking': False}})
                            return {"status": "ok"}
                    elif "/contact" == update.message.text:
                        help_msg = "Please contact @ojasx for customer support/suggestions."
                        await send_text(chat_id, help_msg)
                    elif "/booking_history" == update.message.text:
                        if client_status['booking_history'] == [] or client_status['booking_history'] == None:
                            await send_text(chat_id, "You have not booked any sessions yet.")
                            return {"status": "ok"}
                        else:
                            await send_text(chat_id, "Here is your booking history:")
                            await send_text(chat_id, generate_table_history(client_status['booking_history']))
                            return {"status": "ok"}
                    else: 
                        await send_text(chat_id, "I am not sure what you mean 😅. Please use the availible command in the menu section to interact with me. Or /contact support for help.")

                else:
                    await send_text(chat_id, "Please enter a valid input.")
            elif client_status['state']['major'] == 1:
                if update.message and update.message.text == "/re_enter":
                    await bot.send_message(chat_id=chat_id, text="Please re-enter", reply_markup=ReplyKeyboardRemove())
                    return {"status": "ok"}
                if update.message and update.message.text == "/cancel":
                    await send_text(chat_id, "Your current procedure has been cancelled.")
                    await update_state_client(chat_id, 0, 0)
                    await info_payload_reset(chat_id)
                    return {"status": "ok"}
                await setlogin_handler(chat_id, client_status, update)
        elif chat_id == admin_id:
            client_status = admin.find_one({'_id': chat_id})
            if client_status['state']['major'] == 0:
                if update.message:
                    if "/user_group" in update.message.text:
                        data = user_group_validator(update.message.text)
                        if data == False:
                            await send_text(chat_id, "Please enter in the correct format /user_group [user_id] [group_id]. Make sure the format for user and group is correct.")
                            return {"status": "ok"}
                        else:
                            user_id, group_id = data[0], data[1]
                            user_status = clients.find_one({'random_id': user_id})
                            if user_status == None:
                                await send_text(chat_id, "User does not exist.")
                                return {"status": "ok"}
                            else:
                                clients.update_one({'random_id': user_id}, {'$set': {'group': group_id}})
                                await send_text(chat_id, "User group "+user_id+"has been updated to "+group_id+".")
                                send_appscript_request({"id": user_id, "group": group_id, "method": "userGroup"})
                                return {"status": "ok"}
                    elif "/cancel" == update.message.text:
                        await send_text(chat_id, "Your current procedure has been cancelled.")
                        await update_state_admin(chat_id, 0, 0)
                        await info_payload_reset_admin(chat_id)
                        return {"status": "ok"}
                    elif "/wrong_login" in update.message.text:
                        data = wrong_login_validator(update.message.text)
                        if data == False:
                            await send_text(chat_id, "Please enter in the correct format /wrong_login [user_id]")
                            return {"status": "ok"}
                        else:
                            user_id = data
                            user_status = clients.find_one({'random_id': user_id})
                            if user_status == None:
                                await send_text(chat_id, "User does not exist.")
                                return {"status": "ok"}
                            else:
                                await send_text(user_status["_id"], "⚠️ Our team has detected that you have entered the wrong login details. Please use /setlogin to update your login details. ⚠️")
                                await send_text(chat_id, "User "+user_id+" has been notified.")
                                return {"status": "ok"} 
                    elif "/top_up" in update.message.text:
                        data = top_up_validator(update.message.text)
                        if data == False:
                            await send_text(chat_id, "Please enter in the correct format /top_up [user_id]")
                            return {"status": "ok"}
                        else:
                            user_id = data
                            user_status = clients.find_one({'random_id': user_id})
                            if user_status == None:
                                await send_text(chat_id, "User does not exist.")
                                return {"status": "ok"}
                            else:
                                await send_text(user_status["_id"], "Our workers have detected that you have insufficient funds in your BBDC account. Please top it up!")
                                await send_text(chat_id, "User "+user_id+" has been notified.")
                                return {"status": "ok"}
                    elif "/get_info" in update.message.text:
                        data = get_info_validator(update.message.text)
                        if data == False:
                            await send_text(chat_id, "Please enter in the correct format /get_info [user_id]")
                            return {"status": "ok"}
                        else:
                            user_id = data
                            user_status = clients.find_one({'random_id': user_id})
                            if user_status == None:
                                await send_text(chat_id, "User does not exist.")
                                return {"status": "ok"}
                            else:
                                text = ""
                                client_status = clients.find_one({'random_id': user_id})
                                text = f"<b>User ID:</b> {client_status['random_id']}\n"
                                text += f"<b>Group:</b> {client_status['group']}\n"
                                text += f"<b>Test date:</b> {client_status['test']}\n"
                                text += f"<b>BBDC Username:</b> {client_status['username']}\n"
                                text += f"<b>BBDC Password:</b> {client_status['password']}\n"
                                text += f"<b>Credits:</b> {client_status['credits']}\n"
                                text += f"<b>Phone number:</b> {client_status['phone']}\n"
                                text += f"<b>Type:</b> {'Automatic' if client_status['type'] else 'Manual'}\n"
                                text += f"<b>Checking:</b> {'Yes' if client_status['checking'] else 'No'}\n"
                                await send_text(chat_id, text)
                                table = generate_table(client_status['session_choices'])
                                await send_text(chat_id, table)
                                return {"status": "ok"}
                    elif "/user_test" in update.message.text:
                        data = user_test_validator(update.message.text)
                        if data == False:
                            await send_text(chat_id, "Please enter in the correct format /user_test [user_id] [test_date]. Make sure the format for user and group is correct.")
                            return {"status": "ok"}
                        else:
                            user_id, test = data[0], data[1]
                            user_status = clients.find_one({'random_id': user_id})
                            if user_status == None:
                                await send_text(chat_id, "User does not exist.")
                                return {"status": "ok"}
                            else:
                                clients.update_one({'random_id': user_id}, {'$set': {'test': test}})
                                await send_text(chat_id, "User test "+user_id+" has been updated to "+test+".")
                                send_appscript_request({"method": "userTest", "id": user_id, "test": test})
                                return {"status": "ok"}
                    elif "/book_slot" in update.message.text:
                        data = book_slot_validator(update.message.text)
                        if data == False:
                            await send_text(chat_id, "Please enter in the correct format /book_slot [user_id] [slot_number 1 to 8] [DD-MM-YY].\nMake sure the format for user and group is correct.")
                            return {"status": "ok"}
                        else:
                            user_id, slot, date = data[0], data[1], data[2]
                            user_status = clients.find_one({'random_id': user_id})
                            if user_status == None:
                                await send_text(chat_id, "User does not exist.")
                                return {"status": "ok"}
                            else:
                                # Check if the user is on checking
                                if user_status['checking'] == False:
                                    await send_text(chat_id, "User is not on checking.")
                                    return {"status": "ok"}
                                # Check if the slot is one of the selected slot by the user and the timing of the slot is atleast 2.5 hours away
                                session_choice = user_status['session_choices']
                                if await slot_checker(session_choice, slot, date) == False:
                                    await send_text(chat_id, "Slot is not one of the selected slot by the user or the timing of the slot is not atleast 2.5 hours away.")
                                    return {"status": "ok"}
                                slot = int(slot)
                                first_char = random.choice(string.ascii_uppercase)
                                second_char = str(random.randint(0, 9))
                                third_char = random.choice(string.ascii_uppercase)
                                fourth_char = str(random.randint(0, 9))
                                booking_id = f"{first_char}{second_char}{third_char}{fourth_char}"
                                message_confirmation = ""
                                message_confirmation += f"Booking ID: {booking_id}\n"
                                message_confirmation += f"User ID: {user_id}\n"
                                message_confirmation += f"Slot: {slot}\n"
                                message_confirmation += f"Date: {date}\n"
                                session_choices = user_status['session_choices']
                                date = datetime.strptime(date, '%d-%m-%y').strftime('%Y-%m-%d')
                                session_choices[date].remove(slot)
                                if session_choices[date] == []:
                                    session_choices.pop(date)
                                clients.update_one({'random_id': user_id}, {'$set': {'session_choices': session_choices}})
                                clients.update_one({'random_id': user_id}, {'$inc': {'credits': -1}})
                                clients.update_one({'random_id': user_id}, {'$inc': {'credits_used': 1}})
                                booking = {"booking_id": booking_id, "user_id": user_id, "slot": slot, "date": date, "time": time.time()}
                                # Add the booking to booking_history document of the user_id and also to the booking_history document
                                clients.update_one({'random_id': user_id}, {'$push': {'booking_history': booking}})
                                session_timings = {
                                    1: '0730',
                                    2: '0920',
                                    3: '1130',
                                    4: '1320',
                                    5: '1520',
                                    6: '1710',
                                    7: '1920',
                                    8: '2110'
                                }
                                user_message_confirmation = "<u><b>Booking Confirmation:</b></u>\n\n"
                                user_message_confirmation += f"<b>Booking ID:</b> {booking_id}\n"
                                date1 = datetime.strptime(date, "%Y-%m-%d").strftime("%d %B %Y")
                                user_message_confirmation += f"<b>Date:</b> {date1}\n"
                                time_string = session_timings[slot]
                                start_time = datetime.strptime(time_string, "%H%M")
                                end_time = start_time + timedelta(minutes=100)
                                formatted_range = start_time.strftime("%-I:%M%p") + " to " + end_time.strftime("%-I:%M%p")
                                user_message_confirmation += f"<b>Timing:</b> {formatted_range}\n"
                                user_message_confirmation += "\n1 credit has been deducted from your account. Kindly report to BBDC for your lessons during the above timing.\n"
                                clients.update_one({'random_id': user_id}, {'$set': {'checking': False}})
                                if clients.find_one({'random_id': user_id})['credits'] == 0:
                                    user_message_confirmation += "You have no more credits left. Kindly please add more credits using the /credits command"
                                await send_text(chat_id, message_confirmation)
                                await send_text(user_status["_id"], user_message_confirmation)
                                await send_text(user_status["_id"], "⚠️ Please use /start_checking command AGAIN to start checking for new slots. ⚠️")
                                return {"status": "ok"}    
                    elif "/view_booking_history" in update.message.text:
                        data = view_booking_history_validator(update.message.text)    
                        if data == False:
                            await send_text(chat_id, "Please enter in the correct format /view_booking_history [user_id]")
                            return {"status": "ok"}
                        else:
                            user_id = data
                            user_status = clients.find_one({'random_id': user_id})
                            if user_status == None:
                                await send_text(chat_id, "User does not exist.")
                                return {"status": "ok"}
                            else:
                                booking_history = user_status['booking_history']
                                message = ""
                                message += f"User ID: {user_id}\n\n"
                                session_timings = {
                                    1: '0730',
                                    2: '0920',
                                    3: '1130',
                                    4: '1320',
                                    5: '1520',
                                    6: '1710',
                                    7: '1920',
                                    8: '2110'
                                }
                                for booking in booking_history:
                                    booking_id = booking['booking_id']
                                    slot = booking['slot']
                                    date = booking['date']
                                    date1 = datetime.strptime(date, "%Y-%m-%d").strftime("%d %B %Y")
                                    time_string = session_timings[slot]
                                    start_time = datetime.strptime(time_string, "%H%M")
                                    end_time = start_time + timedelta(minutes=100)
                                    formatted_range = start_time.strftime("%-I:%M%p") + " to " + end_time.strftime("%-I:%M%p")
                                    message += f"Booking ID: {booking_id}\n"
                                    message += f"Date: {date1}\n"
                                    message += f"Slot: {slot}\n"
                                    message += f"Timing: {formatted_range}\n\n------------------------\n"
                                await send_text(chat_id, message)
                                return {"status": "ok"}
                    elif "/retract_booking" in update.message.text: 
                        data = retract_booking_validator(update.message.text)
                        if data == False:
                            await send_text(chat_id, "Please enter in the correct format /retract_booking [user_id] [booking_id]")   
                            return {"status": "ok"}
                        else:
                            user_id, booking_id = data[0], data[1]
                            user_status = clients.find_one({'random_id': user_id})
                            if user_status == None:
                                await send_text(chat_id, "User does not exist.")
                                return {"status": "ok"}
                            else:
                                booking_history = user_status['booking_history']
                                booking_exists = False
                                for booking in booking_history:
                                    if booking['booking_id'] == booking_id:
                                        booking_exists = True
                                        booking_history.remove(booking)
                                        break
                                if booking_exists == False:
                                    await send_text(chat_id, "Booking ID does not exist.")
                                    return {"status": "ok"}
                                else:
                                    clients.update_one({'random_id': user_id}, {'$set': {'credits': user_status['credits'] + 1}})
                                    clients.update_one({'random_id': user_id}, {'$set': {'credits_used': user_status['credits_used'] - 1}})
                                    clients.update_one({'random_id': user_id}, {'$set': {'booking_history': booking_history}})
                                    await send_text(user_status["_id"], "Due to some error on our part, your booking has been retracted. 1 credit has been refunded to your account. \n Booking ID retracted: " + booking_id)
                                    await send_text(chat_id, "User infomed. Booking ID retracted: " + booking_id)
                                    return {"status": "ok"}
                                    
        else: # Create a new user in clients
            first_char = str(random.randint(0, 9))
            second_char = random.choice(string.ascii_uppercase)
            third_char = str(random.randint(0, 9))
            fourth_char = random.choice(string.ascii_uppercase)
            random_id = f"{first_char}{second_char}{third_char}{fourth_char}"
            while clients.count_documents({"random_id": random_id}) > 0:
                first_char = str(random.randint(0, 9))
                second_char = random.choice(string.ascii_uppercase)
                third_char = str(random.randint(0, 9))
                fourth_char = random.choice(string.ascii_uppercase)
                random_id = f"{first_char}{second_char}{third_char}{fourth_char}"
            new_user = {
                "_id": int(chat_id),  # Telegram ID (INT)
                "random_id": random_id,  # Random User ID (STR)
                "group": "",  # The person’s group ID(STR)
                "test": None,  # The person’s test date (Date)
                "username": "",  # BBDC Username of the individual (STR)
                "password": "",  # BBDC Password of the individual (STR)
                "credits": 0, # The amount of credits the user has (INT)
                "phone": "",  # The person’s phone number (STR)
                "topup_history": [],  # A document containing the top up history of the fellow users (Documents)
                "credits_used": 0,  # The total number of credits the user has used (FLOAT)
                "session_choices": {},  # A document containing all the session choices they have (Documents)
                "booking_history": [],  # A document containing all the bookings we have done for them (Documents)
                "state": {"major": 0, "minor": 0},  # State of each user in the document flow (Document)
                "info_payload": {},  # Contain all the information relevant to the current procedure (Document)
                "checking": False,  # Checking if a person is checking for new time slots (Boolean)
                "type": True  # True is Automatic, False is Manual (BOOLEAN)
            }
            clients.insert_one(new_user)
            await send_text(chat_id, msg1)
        return {"status": "ok"}
    except Exception as e:
        print(e)
        print("Exception occurred on line:", e.__traceback__.tb_lineno)
        traceback.print_exc()
        return {"status": "ok"}
    

@app.post("/stripe")
async def webhook_received(request: Request, stripe_signature: str = Header(None)):
    data = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload=data,
            sig_header=stripe_signature,
            secret=webhook_secret
        )
        event_data = event['data']
    except Exception as e:
        print(e)
        return {"error": str(e)}
    amount = event_data['object']['amount_total']/100
    client_reference_id = event_data['object']['client_reference_id']
    stripe_id = event_data['object']['id']
    time = event_data["object"]["created"]
    # check if stripe_id is already in the database
    if clients.find_one({"random_id": client_reference_id, "topup_history": {"$elemMatch": {"stripe_id": stripe_id}}}) != None:
        return {"status": "success"}
    else:
        await top_up(amount, client_reference_id, stripe_id, time)
    return {"status": "success"}


@app.post("/form")
async def form(request: Request):
    data = await request.form()
    form_data = json.dumps(dict(data))
    form_data = json.loads(form_data)
    user_id = form_data['id']
    sessions = {}
    for key in form_data:
        # Check if the key represents a session
        if key.startswith('20'):
            # Extract the date and session number from the key
            date, session = key.split('+')
            session_num = int(session.split('_')[1])
            
            # Add the session number to the appropriate list in the sessions dictionary
            if date in sessions:
                sessions[date].append(session_num)
            else:
                sessions[date] = [session_num]
    await update_session_choices(user_id, sessions)
    table = generate_table(sessions)
    telegram_id = clients.find_one({'random_id': user_id})['_id']
    await send_text(telegram_id, "Your sessions have been successful updated! If you wish to update the slots you are free for, use /choose_session again to update you availible timings if you want. Here's a summary of your currently selected sessions:\n"+table)
    await send_text(telegram_id, "⚠️ Please use /start_checking command next and bot will inform you when a session has been reserved for you by our team. ⚠️")
    clients.update_one({'random_id': user_id}, {'$set': {'checking': False}})
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Thanks!</title>
    </head>
    <body>
        <h1>Thanks for informing us your free timings!</h1>
        <p>You may now proceed back to the bot: <a href="https://t.me/bbdcslotbooking_bot">Telegram Bot</a> or you may close this tab.</p>
        <p>We will notify you once we have booked a slot for you :)</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)



@app.get("/obtain_session/{id}")
async def obtain_session(id: str):
    client = clients.find_one({'random_id': id})
    if client:
        return client['session_choices']
    else:
        return {"status": "error", "message": "Invalid ID"}



@app.get("/daily_updater")
def get_data():
    documents = clients.find({'type': "3", "checking": True})
    result = {}
    current_date = datetime.now().date()
    for document in documents:
        if document['type'] == "3":
            session_choices = document['session_choices']
            for date, numbers in session_choices.items():
                # Convert the date string to a datetime object
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                # Ignore dates from the previous day or before
                if date_obj < current_date:
                    continue
                # Format the date as "DD-MM-YY"
                formatted_date = date_obj.strftime('%d-%m-%y')
                # Add the numbers to the corresponding date in the result dictionary
                result.setdefault(formatted_date, {})
                for number in range(1, 9):  # Include numbers 1 to 8 by default
                    result[formatted_date].setdefault(number, [])
                for number in numbers:
                    result[formatted_date].setdefault(number, []).append(document['random_id'])
                # Add missing dates as empty dictionaries
                date_delta = date_obj - current_date
                for i in range(1, date_delta.days):
                    missing_date = (current_date + timedelta(days=i)).strftime('%d-%m-%y')
                    result.setdefault(missing_date, {})
                    for number in range(1, 9):  # Include numbers 1 to 8 by default
                        result[missing_date].setdefault(number, [])
    sorted_result = {date: result[date] for date in sorted(result)}
    documents = clients.find({'type': "3A", "checking": True})
    result = {}
    current_date = datetime.now().date()
    for document in documents:
        if document['type'] == "3A":
            session_choices = document['session_choices']
            for date, numbers in session_choices.items():
                # Convert the date string to a datetime object
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                # Ignore dates from the previous day or before
                if date_obj < current_date:
                    continue
                # Format the date as "DD-MM-YY"
                formatted_date = date_obj.strftime('%d-%m-%y')
                # Add the numbers to the corresponding date in the result dictionary
                result.setdefault(formatted_date, {})
                for number in range(1, 9):  # Include numbers 1 to 8 by default
                    result[formatted_date].setdefault(number, [])
                for number in numbers:
                    result[formatted_date].setdefault(number, []).append(document['random_id'])
                # Add missing dates as empty dictionaries
                date_delta = date_obj - current_date
                for i in range(1, date_delta.days):
                    missing_date = (current_date + timedelta(days=i)).strftime('%d-%m-%y')
                    result.setdefault(missing_date, {})
                    for number in range(1, 9):  # Include numbers 1 to 8 by default
                        result[missing_date].setdefault(number, [])
    sorted_result_a = {date: result[date] for date in sorted(result)}
    return {"3": sorted_result, "3A": sorted_result_a}
