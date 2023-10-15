import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import dotenv
from dotenv import load_dotenv
from bson.objectid import ObjectId


load_dotenv()

# Get env variables
MONGO_URI = os.getenv('MONGO_URI') 
# Create a new client and connect to the server
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client[os.getenv("MONGO_DBNAME")]
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


#test database
doc = {
    "name":"lemon",
    "email":"lemon@gmail.com",
    "password":"123456",

}

db.users.insert_one(doc)
doc1= db.users.find_one({"name": "lemon"})
print(doc1["email"])




