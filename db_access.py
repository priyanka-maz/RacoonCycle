from pymongo import MongoClient

client = MongoClient('localhost', 27017)

def storePost(dict):
    racoon_db = client.racoon_db
    post_collection = racoon_db.post
    post_collection.insert_one(dict)
    for i in post_collection.find():
        print(i)

