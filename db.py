from pymongo import MongoClient
import os
from dotenv import dotenv_values

config = dotenv_values(os.getcwd() + "/.env")

# connect to Mongodb

client = MongoClient(config["MONGODB_CONNECTION_URI"])
db = client[config["DB_NAME"]]
collection = db[config["COLLECTION_NAME"]]

print("Connected to Mongodb")