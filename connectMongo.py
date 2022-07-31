from pymongo import MongoClient

#dotenv import and load
from dotenv import load_dotenv
import os
load_dotenv()

#connect mongodb
def connect_mongodb():
    MONGO_URI = os.getenv("MONGO_URI")
    try:
        client = MongoClient(MONGO_URI)
        db = client["flask-web"]
        return db
    except:
        print("ERROR: cannot connect to db")