from utils import *
import pandas as pd
import json
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
from pprint import pprint
import os

# Load environment variables
load_dotenv(os.getenv('MDB_PASSWORD'))

# Connect to MongoDB
MDB_USERNAME = os.getenv('MDB_USERNAME')
MDB_PASSWORD = os.getenv('MDB_PASSWORD')

MDB_URI = f'mongodb+srv://{MDB_USERNAME}:{MDB_PASSWORD}@goco-scraping.bwqwr.mongodb.net/goco?retryWrites=true&w=majority'

client = MongoClient(MDB_URI)

sport_names = ["baseball", "mens-basketball", "cross-country", "fencing", "football", "mens-golf", "heavyweight-rowing","lightweight-rowing", "mens-soccer", "mens-squash", "mens-swimming-and-diving", "track-and-field", "wrestling", "mens-tennis", "womens-basketball", "arch", "field-hockey", "womens-golf", "lacrosse", "womens-rowing", "womens-soccer", "softball", "womens-squash", "womens-swimming-and-diving", "womens-swimming-and-diving", "track-and-field", "womens-volleyball"]

for sport in sport_names:
    db = client[sport]

    collection = db["team_stats"]

    data = get_team_stats(sport)

    collection.insert_one(data)

    collection = db["roster"]

    data = get_roster_data(sport)
    
    collection.insert_many(data)
    
    collection = db["schedule"]

    data = get_schedule_data(sport)

    collection.insert_many(data)
