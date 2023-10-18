import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import dotenv
from dotenv import load_dotenv
from bson.objectid import ObjectId


# load credentials and configuration options from .env file
load_dotenv()




# Create a new client and connect to the server
client = MongoClient(os.getenv('MONGO_URI') , serverSelectionTimeoutMS=5000)
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    db = client[os.getenv("MONGO_DBNAME")]
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


#test database
"""
doc = {
    "name":"lemon",
    "email":"lemon@gmail.com",
    "password":"123456",

}

db.users.insert_one(doc)
doc1= db.users.find_one({"name": "lemon"})
print(doc1["email"])
"""





