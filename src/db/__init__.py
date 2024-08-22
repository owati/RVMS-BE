from pymongo import MongoClient

def db():
    return MongoClient()['rvms-test']