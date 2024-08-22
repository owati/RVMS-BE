import os
from pymongo import MongoClient

def db():
    return MongoClient(os.getenv('MONG0_URL'))['rvms-test']