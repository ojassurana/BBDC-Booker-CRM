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


today = datetime.today().strftime('%d-%m-%y')
date = datetime.strptime(today, '%d-%m-%y').strftime('%Y-%m-%d')
date = datetime.strptime(date, '%Y-%m-%d').date()
print(today)
print(date)