import os
from pymongo import MongoClient

def db():
    return MongoClient(os.getenv('MONGO_URL'))['rvms-test']