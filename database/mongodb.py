import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_db():
    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri)
    db = client.get_database("disck_tallk")
    return db

db = get_db()
